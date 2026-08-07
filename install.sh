#!/usr/bin/env bash
# Install the kb toolkit: CLI, skills, docs.
#
# Idempotent — safe to re-run after an update. Nothing outside the user's home
# is touched, no sudo, no package manager. Existing files are backed up before
# being replaced, so a bad update is one `mv` away from being undone.
#
#   ./install.sh              install CLI + skills into every IDE found + docs
#   ./install.sh --dry-run    print what would happen, change nothing
#   ./install.sh --bin-only   just the CLI
#
# The CLI itself has no hardcoded paths: it stores its registry under
# $HOME/.local/state/kb (override with KB_REGISTRY) and reads KB_LANG for the
# language of the text it writes into notes.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${KB_BIN_DIR:-$HOME/.local/bin}"
DOC_DIR="${KB_DOC_DIR:-$HOME/.claude/docs}"
STAMP="$(date +%Y%m%d-%H%M%S)"

DRY_RUN=0
BIN_ONLY=0
for arg in "$@"; do
    case "$arg" in
        --dry-run)  DRY_RUN=1 ;;
        --bin-only) BIN_ONLY=1 ;;
        -h|--help)  sed -n '2,14p' "${BASH_SOURCE[0]}" | sed 's/^# \?//'; exit 0 ;;
        *) echo "unknown option: $arg" >&2; exit 2 ;;
    esac
done

say() { printf '%s\n' "$*"; }

# Copy with a timestamped backup of whatever was there. Returns without acting
# when the content is already identical, so re-running is genuinely a no-op.
install_file() {
    local src="$1" dst="$2"
    if [ -f "$dst" ] && cmp -s "$src" "$dst"; then
        say "  = $dst"
        return 0
    fi
    if [ "$DRY_RUN" -eq 1 ]; then
        say "  would install $dst"
        return 0
    fi
    mkdir -p "$(dirname "$dst")"
    if [ -f "$dst" ]; then
        cp -p "$dst" "$dst.bak.$STAMP"
        say "  ~ $dst  (backup: $dst.bak.$STAMP)"
    else
        say "  + $dst"
    fi
    cp "$src" "$dst"
}

# ── CLI ─────────────────────────────────────────────────────────────────────
say "── CLI ──"
install_file "$SRC/bin/kb" "$BIN_DIR/kb"
[ "$DRY_RUN" -eq 0 ] && chmod +x "$BIN_DIR/kb"

case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *) say "  ! $BIN_DIR is not on PATH — add it:"
       say "      echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc" ;;
esac

if [ "$BIN_ONLY" -eq 1 ]; then
    say "done (--bin-only)"
    exit 0
fi

# ── skills ──────────────────────────────────────────────────────────────────
# One directory per assistant. Only those already present are written to —
# installing into an IDE the user does not have would litter their home.
say "── skills ──"
found_ide=0
for ide_dir in "$HOME/.claude/skills" \
               "$HOME/.config/opencode/skills" \
               "$HOME/.codex/skills"; do
    parent="$(dirname "$ide_dir")"
    [ -d "$parent" ] || continue
    found_ide=1
    say "  ${ide_dir/#$HOME/\~}"
    for skill in kbsave kbrestore; do
        install_file "$SRC/skills/$skill/SKILL.md" "$ide_dir/$skill/SKILL.md"
    done
done

if [ "$found_ide" -eq 0 ]; then
    say "  ! no assistant config directory found"
    say "    (~/.claude, ~/.config/opencode, ~/.codex)"
    say "    copy skills/ into your assistant's skills directory by hand"
fi

# ── docs ────────────────────────────────────────────────────────────────────
say "── docs ──"
install_file "$SRC/docs/kb.ru.md" "$DOC_DIR/kb.ru.md"
install_file "$SRC/docs/kb.en.md" "$DOC_DIR/kb.en.md"

# ── verify ──────────────────────────────────────────────────────────────────
say "── verify ──"
if [ "$DRY_RUN" -eq 1 ]; then
    say "  (dry run, nothing installed)"
elif "$BIN_DIR/kb" --help >/dev/null 2>&1; then
    say "  $("$BIN_DIR/kb" --help 2>&1 | head -1)"
    say "  ok — try: cd <project> && kb list"
else
    say "  ! $BIN_DIR/kb did not run. Python 3.10+ required:"
    say "    $(python3 --version 2>&1 || echo 'python3 not found')"
    exit 1
fi
