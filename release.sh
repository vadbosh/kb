#!/usr/bin/env bash
# release.sh — keep the version, the changelog and the tags saying the same thing.
#
#   ./release.sh check     verify they agree; exit 3 if they do not
#   ./release.sh tag       create the missing tag for the current version
#
# Three places record a release and each drifts on its own: `version:` inside
# SKILL.md is what ships, CHANGELOG.md is what a reader looks at, a git tag is
# what `git checkout` needs. A release where the three disagree is worse than an
# untagged one -- the disagreement is silent, and each source looks authoritative.
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
SKILL="$SRC/skills/kb/SKILL.md"
LOG="$SRC/CHANGELOG.md"
COPIES=0

# Machine-specific paths belong to the machine, not to a public repository.
# KB_MIRRORS is a colon-separated list of directories that hold a COPY of the
# skill and are not written by install.sh -- a config canon that redistributes
# it, a second checkout, a container mount. Set it in .release.local, which is
# not tracked.
[ -f "$SRC/.release.local" ] && . "$SRC/.release.local"

version() {
	grep -m1 '^version:' "$SKILL" | sed 's/version: *"//; s/"//'
}

# Everywhere on this machine that holds an installed copy: the three assistant
# directories install.sh writes to, plus whatever KB_MIRRORS names.
installed_dirs() {
	local d
	for d in "$HOME/.claude/skills/kb" \
	         "$HOME/.config/opencode/skills/kb" \
	         "$HOME/.codex/skills/kb"; do
		[ -f "$d/SKILL.md" ] && printf '%s\n' "$d"
	done
	# printf WITH the newline: `read` drops a final line that has none, which
	# is every single-entry KB_MIRRORS -- the common case, silently ignored.
	printf '%s\n' "${KB_MIRRORS:-}" | tr ':' '\n' | while read -r d; do
		[ -n "$d" ] && [ -f "$d/SKILL.md" ] && printf '%s\n' "$d"
	done
}

# A copy that is behind is a copy that will be read. The assistant directories
# are refreshed by install.sh at release time; a mirror is refreshed by whatever
# owns it, which is exactly why it gets forgotten -- twice in one evening here,
# and each time the stale copy was found a day later by someone reading it.
copies() {
	local v="$1" d behind=0 n=0 iv same
	while read -r d; do
		[ -n "$d" ] || continue
		n=$((n + 1))
		iv="$(grep -m1 '^version:' "$d/SKILL.md" | sed 's/version: *"//; s/"//')"
		same=1
		for f in SKILL.md references/save.md references/restore.md scripts/kb; do
			cmp -s "$SRC/skills/kb/$f" "$d/$f" || same=0
		done
		if [ "$iv" = "$v" ] && [ "$same" -eq 1 ]; then
			continue
		fi
		[ "$behind" -eq 0 ] && echo "  installed copies behind the source:"
		behind=$((behind + 1))
		echo "    ${d/#$HOME/\~}  version $iv$([ "$same" -eq 0 ] && echo ", content differs")"
	done <<-EOF
	$(installed_dirs)
	EOF
	if [ "$behind" -gt 0 ]; then
		echo "                    ./install.sh refreshes the assistant directories;"
		echo "                    a mirror is refreshed by whatever owns it"
		return 1
	fi
	# "0, all at 4.8.0" reads as a check that passed. Nothing was checked --
	# a fresh clone on a machine with no assistant installed is the normal
	# case, and saying so is the difference between a fact and a formality.
	if [ "$n" -eq 0 ]; then
		echo "  installed copies:  none on this machine — nothing to compare"
		return 0
	fi
	COPIES=$n
	echo "  installed copies:  $n, all at $v"
}

# What ships is read by people who have this skill and nothing else of ours.
# Three kinds of local detail have reached those files -- a path into this
# checkout, a tool that lives only in this repository, a version from this
# changelog -- and each was found by a reader, never by the release. The test
# is not a word list: it asks whether the thing named exists HERE and is not
# part of what gets installed.
shipped_leaks() {
	local f found=0 tok base
	for f in "$SRC"/skills/kb/SKILL.md "$SRC"/skills/kb/references/*.md; do
		# A path into this checkout. Invented examples do not resolve here,
		# which is exactly what makes them safe to print.
		while read -r tok; do
			[ -n "$tok" ] || continue
			echo "    ${f#"$SRC"/}: $tok — a path into this checkout"
			found=1
		done < <(grep -oE "$SRC[A-Za-z0-9._/-]*" "$f" || true)

		# A file of ours that is NOT installed: the reader cannot run it.
		# Written with the suffix or the slash it always carries -- a bare
		# `tests` matched the English word in ordinary prose, and a pattern
		# anchored on a word boundary missed `./release.sh`, which is how the
		# leak was actually written.
		while read -r tok; do
			[ -n "$tok" ] || continue
			echo "    ${f#"$SRC"/}: $tok — exists here, never installed"
			found=1
		done < <(grep -oE '(\./)?(release\.sh|install\.sh|install\.ps1|CHANGELOG\.md|tests/)' "$f" | sort -u || true)

		# A version out of our changelog. The `version:` field is the one
		# legitimate mention: it is what ships, not an illustration.
		while read -r tok; do
			[ -n "$tok" ] || continue
			grep -q "^## ${tok}\( \|$\)" "$LOG" || continue
			echo "    ${f#"$SRC"/}: $tok — a version from our changelog"
			found=1
		done < <(grep -v '^version:' "$f" | grep -oE '\b[0-9]+\.[0-9]+\.[0-9]+\b' || true)
	done
	return $found
}

check() {
	local v problems=0
	v="$(version)"
	[ -n "$v" ] || { echo "no version: field in $SKILL" >&2; return 3; }
	echo "  SKILL.md version: $v"

	if grep -q "^## $v\( \|$\)" "$LOG"; then
		echo "  CHANGELOG.md:     has a section for $v"
	else
		echo "  CHANGELOG.md:     NO section for $v — add one before tagging"
		problems=1
	fi

	if git -C "$SRC" rev-parse "v$v" >/dev/null 2>&1; then
		echo "  tag v$v:          exists"
	else
		echo "  tag v$v:          missing — ./release.sh tag creates it"
		problems=1
	fi

	# A tag for a version nobody records reads as a release that was withdrawn.
	local orphan
	orphan="$(git -C "$SRC" tag | while read -r tg; do
		t="${tg#v}"
		grep -q "^## $t\( \|$\)" "$LOG" || echo "v$t"
	done)"
	if [ -n "$orphan" ]; then
		echo "  tags with no changelog entry:"
		echo "$orphan" | sed 's/^/    /'
		problems=1
	fi

	# The three records can agree perfectly while the tag sits behind HEAD.
	# "agreed" then reads as "released", and the work since is invisible --
	# five commits of release machinery once sat unreleased under that word.
	local ahead
	ahead="$(git -C "$SRC" rev-list --count "v$v..HEAD" 2>/dev/null || echo 0)"
	if [ "$ahead" -gt 0 ]; then
		echo "  HEAD:             $ahead commit(s) after v$v — unreleased"
		echo "                    bump version:, add a section, then ./release.sh tag"
	else
		echo "  HEAD:             at v$v"
	fi

	local leaks
	leaks="$(shipped_leaks)" || {
		echo "  what ships mentions what only exists here:"
		echo "$leaks"
		problems=1
	}
	[ -n "$leaks" ] || echo "  shipped files:    nothing local named in them"

	copies "$v" || problems=1

	[ "$problems" -eq 0 ] || return 3
	if [ "$ahead" -gt 0 ]; then
		echo "  the three records agree; the tag is behind HEAD"
		return 0
	fi
	if [ "${COPIES:-0}" -gt 0 ]; then
		echo "  agreed and released, and all $COPIES copies here match"
	else
		echo "  agreed and released"
	fi
}

tag() {
	local v
	v="$(version)"
	if ! git -C "$SRC" diff --quiet || ! git -C "$SRC" diff --cached --quiet; then
		echo "working tree is dirty — commit first, the tag names a commit" >&2
		return 1
	fi
	grep -q "^## $v\( \|$\)" "$LOG" || {
		echo "CHANGELOG.md has no section for $v — write it first" >&2
		return 1
	}
	if git -C "$SRC" rev-parse "v$v" >/dev/null 2>&1; then
		echo "  v$v already tagged"
		return 0
	fi
	# The changelog section goes into the tag, so `git show v4.1.0` answers
	# "what changed" without leaving git. Copied rather than written again:
	# a tag is immutable once pushed, and a second wording would be the one
	# nobody could correct.
	local notes
	notes="$(awk -v v="## $v" '
		$0 == v || index($0, v " ") == 1 { on = 1; next }
		on && /^## / { exit }
		on { print }' "$LOG")"
	printf '%s\n%s\n' "$(git -C "$SRC" log -1 --format=%s)" "$notes" \
		| git -C "$SRC" tag -a "v$v" -F -
	echo "  tagged v$v at $(git -C "$SRC" rev-parse --short HEAD)"
	echo "  push it: git push --tags origin"
}

case "${1:-check}" in
	check) check ;;
	tag)   tag ;;
	*)     echo "usage: $0 {check|tag}" >&2; exit 2 ;;
esac
