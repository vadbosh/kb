# kb — work notes with an index that does not rot

A `kb/` directory per work stream: one `00-overview.md` acting as a map, plus
numbered topic files around it. Readable by a human, cheap for an assistant to
navigate, and the index is **generated** rather than maintained by hand.

Full manual: [`docs/kb.en.md`](docs/kb.en.md) · по-русски: [`docs/kb.ru.md`](docs/kb.ru.md)

## The problem

Notes about an investigation pile up in a project root. Someone writes an index
by hand. Then files get added, renamed, split — and the index quietly starts
lying. The usual archaeological evidence is a stack of `00-overview.md.bak.*`
next to a real directory, one per attempt to keep the thing honest.

Three failure modes, all of them mechanical:

- the index drifts from the files
- links point at files that were deleted or moved
- "the current snapshot is the newest one" lives only as prose nobody checks

## Install

Requires **Python 3.10+** and nothing else — no pip, no sudo, no packages.

```bash
git clone <this-repo> && cd kb
./install.sh              # CLI + skills into every assistant found + docs
./install.sh --dry-run    # print what would happen, change nothing
./install.sh --bin-only   # just the CLI
```

The installer is idempotent: re-running after an update replaces only what
actually changed, and backs up anything it overwrites as `<file>.bak.<stamp>`.

It writes into three places, all under `$HOME`:

```
~/.local/bin/kb                    the CLI
~/.claude/skills/kb{save,restore}/ skills — only for assistants already present
~/.config/opencode/skills/…        (same)
~/.codex/skills/…                  (same)
~/.claude/docs/kb.{ru,en}.md       the manual
```

## Portability

**No path is hardcoded to the author's machine.** The CLI resolves everything
from `$HOME` or environment variables:

| Variable | Default | What it controls |
|---|---|---|
| `KB_REGISTRY` | `$HOME/.local/state/kb/registry.txt` | where the list of known kb directories lives |
| `KB_LANG` | `ru` | language of the text written **into** notes (table header, "current snapshot" line, the index skeleton). Diagnostics are always English. |
| `KB_BIN_DIR` | `$HOME/.local/bin` | install target for the CLI |
| `KB_DOC_DIR` | `$HOME/.claude/docs` | install target for the manual |

A team that writes notes in English installs with:

```bash
echo 'export KB_LANG=en' >> ~/.bashrc
```

Existing notes are unaffected — the setting only applies to text generated from
then on.

## Two words to remember

```
kbrestore    at the start of work — loads the notes, tells you what changed
kbsave       when there is something worth keeping
```

Everything mechanical hangs off those two. You never call `kb sync` yourself.

| You type | What runs underneath |
|---|---|
| `kbrestore` | `kb status` + `kb check` + `kb verify`, then reads the index and the current snapshot |
| `kbsave` | `kb status` → decides append-or-new → `kb add` → writes → `kb sync` → `kb check` |

Both work as slash commands too: `/kbsave`, `/kbrestore`.

## What is in the box

```
bin/kb                     the CLI — pure stdlib, ~800 lines, no dependencies
skills/kbsave/SKILL.md     judgement: what to write, where, which kind
skills/kbrestore/SKILL.md  judgement: what to read, what changed since last time
docs/kb.en.md              full manual, English
docs/kb.ru.md              full manual, Russian
install.sh                 idempotent installer
```

The split is deliberate: **the CLI owns everything mechanical** (numbering, the
index table, drift detection, which snapshot is current), **the assistant owns
judgement** (is this a new file or an existing one, which `kind`, when a file
has grown two questions and wants splitting). Neither does the other's job.

## Commands

| Command | What |
|---|---|
| `kb status` | where the kb is, file count, current snapshot, largest files |
| `kb check` | mechanical drift; exit 3 = go fix it |
| `kb verify` | suspicions: vanished paths, notes past their re-check age; exit 3 = go look |
| `kb sync` | rebuild the index table from front matter |
| `kb add <slug> --kind <k> --title "…"` | next numbered file + front matter + rebuild |
| `kb list [--scan DIR] [--prune]` | every known kb on this machine |
| `kb outline [file]` | section map with weights — where the seams for a split are |
| `kb adopt [--apply]` | migrate an existing hand-made notes directory |

## Adopting notes you already have

If a directory already holds `00-overview.md` and numbered files written by
hand:

```bash
cd <that-project>
kb adopt              # preview: what moves, which titles it harvests
kb adopt --apply
```

`adopt` moves the notes into `kb/`, adds front matter, inserts the managed
markers, and rebuilds the table. Titles are **harvested from your existing
index table**, not invented from the H1 — the phrasing a human wrote for a
reader is better than a document title, and losing it would defeat the point.
Every touched file is backed up first.

## Design notes worth knowing before you extend it

- **The managed block.** The index table lives between `<!-- kb:begin -->` and
  `<!-- kb:end -->` and is regenerated from front matter. Prose outside the
  markers is never touched by the tool. That is the whole trick: the human keeps
  writing, the table stops rotting.
- **Size is advisory, never enforced.** Files are read on demand, one at a time,
  so the 200-line rule for always-loaded instruction files does not transfer. A
  long coherent reference is a good file. The real split criterion is mixed
  `kind`s — because `kind` is exactly "which question does this answer".
- **`check` and `verify` are separate on purpose.** `check` is binary and
  mechanical; `verify` is probabilistic. Merging them would drown an exact
  signal in guesses.
- **`verify` only looks at paths inside backticks whose root exists.** Measured
  on a real 19-file kb: without those two constraints you get 271 flags of which
  ~2 are real. With them: 6 flags, 2 real. A report with the first ratio teaches
  you to ignore it within days.
- **Gaps in numbering are never reused.** A number that once pointed at a file
  may still be cited from a commit message or another note.

## Uninstall

```bash
rm -f ~/.local/bin/kb
rm -rf ~/.claude/skills/kbsave ~/.claude/skills/kbrestore
rm -rf ~/.config/opencode/skills/kbsave ~/.config/opencode/skills/kbrestore
rm -rf ~/.codex/skills/kbsave ~/.codex/skills/kbrestore
rm -rf ~/.local/state/kb          # the registry; notes themselves are untouched
```

Your notes are plain markdown in your own repositories. Removing the tool leaves
them fully readable — the index table simply stops updating itself.
