#!/usr/bin/env bash
# Install the kb toolkit — Linux / macOS.  Windows: use install.ps1
#
# The CLI is installed INSIDE the skill (skills/kb/scripts/kb), so nothing
# depends on PATH or on ~/.local/bin existing. A copy on PATH is offered
# separately and only for running kb by hand.
#
#   ./install.sh                 install the skill into every assistant found + docs
#   ./install.sh --dry-run       print what would happen, change nothing
#   ./install.sh --with-path     also place a copy on PATH for manual use
#   ./install.sh --skills-dir D  install into D instead of auto-detecting
#
# Idempotent: re-running replaces only what changed and backs up what it
# overwrites as <file>.bak.<timestamp>. Nothing outside $HOME is touched.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOC_DIR="${KB_DOC_DIR:-$HOME/.kb-docs}"
PATH_DIR="${KB_BIN_DIR:-$HOME/.local/bin}"
STAMP="$(date +%Y%m%d-%H%M%S)"

DRY_RUN=0
WITH_PATH=0
SKILLS_DIR=""
while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run)    DRY_RUN=1 ;;
        --with-path)  WITH_PATH=1 ;;
        --skills-dir) SKILLS_DIR="${2:-}"; shift ;;
        -h|--help)    sed -n '2,15p' "${BASH_SOURCE[0]}" | sed 's/^# \?//'; exit 0 ;;
        *) echo "unknown option: $1" >&2; exit 2 ;;
    esac
    shift
done

# Colour only when stdout is a terminal — piping into a log must stay clean.
if [ -t 1 ]; then
    C_OK=$'\033[32m'; C_WARN=$'\033[33m'; C_BAD=$'\033[31m'; C_OFF=$'\033[0m'
else
    C_OK=''; C_WARN=''; C_BAD=''; C_OFF=''
fi

say()  { printf '%s\n' "$*"; }
ok()   { printf '%s%s%s\n' "$C_OK"   "$*" "$C_OFF"; }
warn() { printf '%s%s%s\n' "$C_WARN" "$*" "$C_OFF"; }
bad()  { printf '%s%s%s\n' "$C_BAD"  "$*" "$C_OFF"; }
tilde() { printf '%s' "${1/#$HOME/\~}"; }

# Copy with a timestamped backup. Returns early when the content already
# matches, so a re-run is a genuine no-op instead of a pile of identical .bak.
install_file() {
    local src="$1" dst="$2" mode="${3:-644}"
    if [ -f "$dst" ] && cmp -s "$src" "$dst"; then
        say "    = $(tilde "$dst")"
        return 0
    fi
    if [ "$DRY_RUN" -eq 1 ]; then
        say "    would write $(tilde "$dst")"
        return 0
    fi
    mkdir -p "$(dirname "$dst")"
    if [ -f "$dst" ]; then
        cp -p "$dst" "$dst.bak.$STAMP"
        say "    ~ $(tilde "$dst")  (backup .bak.$STAMP)"
    else
        say "    + $(tilde "$dst")"
    fi
    cp "$src" "$dst"
    chmod "$mode" "$dst"
}

# Assistants keep skills in their own directory. Only those already present are
# written to — creating a config tree for an assistant the user does not have
# would just litter their home.
detect_skill_dirs() {
    if [ -n "$SKILLS_DIR" ]; then
        printf '%s\n' "$SKILLS_DIR"
        return
    fi
    local d
    for d in "$HOME/.claude/skills" \
             "$HOME/.config/opencode/skills" \
             "$HOME/.codex/skills"; do
        [ -d "$(dirname "$d")" ] && printf '%s\n' "$d"
    done
}

# v1 shipped two skills, kbsave and kbrestore, each with its own copy of the CLI.
# v2 merges them into one `kb` skill. Leaving the old pair in place would give
# three skills competing for the same trigger phrases, so they are removed — but
# only after confirming the directory is ours and holds nothing hand-written.
remove_legacy() {
    local dir="$1" name stray
    for name in kbsave kbrestore; do
        [ -d "$dir/$name" ] || continue
        if ! grep -q "^name: $name\$" "$dir/$name/SKILL.md" 2>/dev/null; then
            warn "    ? $(tilde "$dir/$name") is not ours — left untouched"
            continue
        fi
        stray="$(find "$dir/$name" -type f \
                  ! -name SKILL.md ! -path '*/scripts/kb' ! -name '*.bak.*' \
                  -print -quit 2>/dev/null)"
        if [ -n "$stray" ]; then
            warn "    ? $(tilde "$dir/$name") has extra files — left untouched"
            continue
        fi
        if [ "$DRY_RUN" -eq 1 ]; then
            say "    would remove $(tilde "$dir/$name")  (replaced by kb/)"
        else
            rm -rf -- "${dir:?}/${name:?}"
            warn "    - $(tilde "$dir/$name")  (v1 layout, replaced by kb/)"
        fi
    done
}

# 3.10+ is the floor: the CLI uses `X | None` annotations and the match-free but
# 3.10-only union syntax. Report the version found rather than a bare failure.
find_python() {
    local py
    for py in python3 python; do
        if command -v "$py" >/dev/null 2>&1 &&
           "$py" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' \
                 >/dev/null 2>&1; then
            printf '%s' "$py"
            return 0
        fi
    done
    return 1
}

# ── prerequisites ───────────────────────────────────────────────────────────
if ! PY="$(find_python)"; then
    bad "Python 3.10 or newer is required."
    say "  python3: $(python3 --version 2>&1 || echo 'not found')"
    say "  python:  $(python --version  2>&1 || echo 'not found')"
    warn "  Debian/Ubuntu: sudo apt install python3"
    warn "  macOS:         brew install python@3.12"
    exit 1
fi
ok "python: $PY — $("$PY" --version 2>&1)"

# ── skills (each carries its own copy of the CLI) ───────────────────────────
say "── skill ──"
found=0
while IFS= read -r dir; do
    [ -n "$dir" ] || continue
    found=1
    say "  $(tilde "$dir")"
    # One skill directory, one copy of the CLI inside it.
    install_file "$SRC/skills/kb/SKILL.md" "$dir/kb/SKILL.md"
    for ref in "$SRC"/skills/kb/references/*.md; do
        install_file "$ref" "$dir/kb/references/$(basename "$ref")"
    done
    install_file "$SRC/skills/kb/scripts/kb" "$dir/kb/scripts/kb" 755
    remove_legacy "$dir"
done < <(detect_skill_dirs)

if [ "$found" -eq 0 ]; then
    bad "  No assistant directory found."
    warn "    Looked for ~/.claude, ~/.config/opencode, ~/.codex"
    warn "    Pass --skills-dir <path> to install anyway."
    exit 1
fi

# ── docs ────────────────────────────────────────────────────────────────────
say "── docs ──"
install_file "$SRC/docs/kb.en.md" "$DOC_DIR/kb.en.md"
install_file "$SRC/docs/kb.ru.md" "$DOC_DIR/kb.ru.md"

# ── optional: a copy on PATH, for running kb by hand ────────────────────────
if [ "$WITH_PATH" -eq 1 ]; then
    say "── PATH copy ──"
    install_file "$SRC/skills/kb/scripts/kb" "$PATH_DIR/kb" 755
    case ":$PATH:" in
        *":$PATH_DIR:"*) ;;
        *) warn "    $(tilde "$PATH_DIR") is not on PATH. Add it:"
           say "        echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc" ;;
    esac
fi

# ── verify ──────────────────────────────────────────────────────────────────
say "── verify ──"
if [ "$DRY_RUN" -eq 1 ]; then
    warn "  dry run — nothing was installed"
    exit 0
fi
# No pipe to `head`: it would close the pipe early, the writer would take
# SIGPIPE, and pipefail would turn that into a failed install at the last step.
all_dirs="$(detect_skill_dirs)"
probe="${all_dirs%%$'\n'*}/kb/scripts/kb"
if "$probe" --help >/dev/null 2>&1; then
    ok "  ok — $(tilde "$probe")"
    say ""
    say "  In your assistant: say 'kbrestore' to load a project's notes,"
    say "  'kbsave' to write down what you learned."
    say "  By hand: \"$probe\" list"
else
    bad "  Installed, but $(tilde "$probe") did not run."
    exit 1
fi
