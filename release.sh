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

version() {
	grep -m1 '^version:' "$SKILL" | sed 's/version: *"//; s/"//'
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

	[ "$problems" -eq 0 ] || return 3
	echo "  agreed"
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
