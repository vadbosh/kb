# kb

**A knowledge base in plain Markdown whose index cannot rot, where every fact is
typed by how it goes out of date.**

Point it at anything you would otherwise keep as a growing pile of `.md` files —
a migration, an incident, a research thread, a renovation, a legal case. Nothing
about it is specific to code.

[Русская версия](README.RU.md) · Full manual: [English](docs/kb.en.md) · [Русский](docs/kb.ru.md)

**Just want to start?** → [Install](#install), then [Usage](#usage). Three steps.

---

## The idea

Almost everyone eventually writes a wiki for their own work: one file listing the
others, topic files around it. It works for about three weeks.

Then files get added, renamed, split. The list is updated by hand — until it
isn't. The "current status" heading keeps a date nobody touched. Links point at
files that moved. The usual archaeological evidence is a stack of
`00-overview.md.bak.*` beside the real directory, one per attempt to keep the
thing honest.

Three mechanisms below work against that. The first two remove the source of the
divergence automatically. The third fixes nothing — it shows you where the
divergence has already happened.

### 1. The index is generated, not maintained

Every note carries three lines of front matter:

```yaml
---
title: what the reader will find here
kind: reference
updated: 2026-09-01
---
```

The index contains a **managed block**. Everything between the markers is rebuilt
from those lines; everything outside them is yours and is never touched.

```markdown
## Where to start reading

<!-- kb:begin -->
Current snapshot: `21-state-2026-08-07.md` (2026-08-07).

| what you need | file | kind | updated |
|---|---|---|---|
| how the pipeline works | `02-pipeline.md` | reference | 2026-08-05 |
| traps and check commands | `23-traps.md` | recipe | 2026-08-07 |
<!-- kb:end -->
```

You never write that table. It cannot disagree with the files, because it is
derived from them.

### 2. Knowledge is typed by how it expires

In an ordinary wiki every page is equal: nothing on the page tells you whether it
describes how things are or how they were. Yet they expire differently — two
files from the same directory:

- `02-pipeline.md`, "how the log pipeline works". True for months. When the
  pipeline changes the file is edited in place; the previous text is of no use to
  anyone.
- `15-state-2026-08-05.md`, "what is done and what is open as of 5 August". True
  for exactly that date. A week later it is **not wrong** — it is a historical
  fact. Rewriting it destroys evidence; a newer snapshot appears next to it while
  this one stays.

The first is maintained, the second is frozen and superseded. Put both in one
undifferentiated list and the reader cannot tell which is which — and starts
doubting both. kb makes you say which it is, in the `kind` field.

| kind | holds | how it ages |
|---|---|---|
| `state` | a snapshot on a date | **superseded** by a later one |
| `plan` | what is planned, in what order | superseded once executed |
| `decision` | a choice and *why*; rejected alternatives | **never expires** — a historical fact |
| `reference` | how something works | edited in place |
| `recipe` | traps and ready-to-run checks | edited in place |

What the tool then gets for free:

- **Which snapshot is current is computed**, not declared — the `state` with the
  latest date in its filename. Earlier ones are marked, never deleted: each still
  describes its own date truthfully.
- **A `decision` is never rewritten.** Reversing one means writing a new decision
  that supersedes it, so the reasoning behind the old choice stays readable —
  usually the thing you actually needed six months later.

### 3. Rot is reported through two separate channels

```
kb check     mechanical: index vs files, dead links, missing front matter, size
kb verify    advisory:   paths that no longer exist, notes nobody revisited
```

Deliberately **not merged**. `check` is binary — exit 3 means go fix it. `verify`
is probabilistic — exit 3 means go look. Merging them would drown an exact signal
in guesses.

Neither claims to know whether a statement about the world is still true. A
recipe can hold the command that would prove it; running that command against
production on a schedule is not a note-taking tool's job.

---

## Install

Requires **Python 3.10+** and nothing else. No pip, no packages, no sudo.

```bash
git clone https://github.com/vadbosh/kb && cd kb

./install.sh              # Linux / macOS
./install.sh --dry-run    # print what would happen, change nothing
./install.sh --with-path  # also put kb on PATH, for running it by hand
```

```powershell
.\install.ps1             # Windows
.\install.ps1 -DryRun
.\install.ps1 -WithPath

# if execution policy blocks the file:
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

Both check Python before touching anything and stop with a coloured, actionable
message if it is missing or not on PATH — a common outcome on Windows when
"Add python.exe to PATH" was left unticked during setup.

Everything lands in one directory per assistant:

```
<skills-dir>/kb/SKILL.md
<skills-dir>/kb/references/*.md
<skills-dir>/kb/scripts/kb        + kb.cmd launcher on Windows
```

Nothing depends on `PATH` or on `~/.local/bin` existing — that directory is not a
thing on Windows, which is also why the Windows installer writes a `.cmd`
launcher (Windows does not act on a shebang line).

Only assistant directories that already exist are written to; `--skills-dir
<path>` / `-SkillsDir <path>` overrides the detection. Manual install is just
`cp -r skills/kb <skills-dir>/` — the skill is self-contained.

Re-running an installer is a genuine no-op for unchanged files and backs up
whatever it replaces as `<file>.bak.<timestamp>`.

---

## Usage

What you MUST do, in order:

1. **Install** — `./install.sh` (Linux/macOS) or `.\install.ps1` (Windows). See
   [Install](#install).
2. **`cd` into your project** and start your assistant there.
3. **Type `/kb save`.** This is the step that creates `kb/` and writes the first
   note. Before it, the project has no `kb/` — launching the assistant does not
   create one, and that is normal.

After that, two commands are the whole workflow:

```
/kb restore    first thing when you sit down — loads the notes, says what changed
/kb save       any time something is worth keeping
```

That is all. You never run `kb` in a shell; the assistant does it for you.

Saying `kbrestore` or `kbsave` as plain words in a message works identically —
use whichever you find easier to remember.

<details>
<summary>What those two actually run</summary>

| Command | Underneath |
|---|---|
| `/kb restore` | `kb status` + `kb check` + `kb verify`, then the index and the current snapshot, then only the files the task needs |
| `/kb save` | `kb status` → decides append-or-new → `kb add` → writes the body → `kb sync` → `kb check` |

</details>

### Adopting notes you already have

If a directory already holds a hand-written index and numbered files:

```bash
kb adopt              # preview: what moves, which titles it harvests
kb adopt --apply
```

It moves the notes into `kb/`, adds front matter, inserts the managed markers and
builds the table. Titles are **harvested from your existing table**, not invented
from each `# H1` — the phrasing a human wrote for a reader answers "what do I
need", a document title does not, and losing it would defeat the point. Every
touched file is backed up first.

---

## What it deliberately does not do

- **No auto-splitting of long files.** Size is reported, never enforced. A long
  coherent reference is a good file; where to cut is a question of meaning.
  `kb outline` prints a section map so the decision costs a dozen lines to read
  instead of fifteen hundred.
- **No database, no server, no lock-in.** The notes are ordinary Markdown in your
  own repository. Delete the tool and they stay readable; only the table stops
  updating itself.
- **No opinion about your prose.** Only the managed block is generated.

---

## Two layers

| Layer | Owns | Lives in |
|---|---|---|
| CLI `kb` | everything **mechanical** — numbering, the table, drift detection, which snapshot is current | `<skill-dir>/scripts/kb` |
| Skill `kb` | everything needing **judgement** — new file or existing one, which `kind`, when a file has grown two questions | your assistant's skills directory |

The split is the design. Neither side does the other's job: the CLI never guesses
what a note means, the assistant never hand-edits the table.

The skill has two halves, each loaded only when needed:

```
kb/SKILL.md               routing + the rules both halves share
kb/references/save.md     writing: append or new file, which kind, titles
kb/references/restore.md  reading: orient, be selective, brief
kb/scripts/kb             the CLI — one copy, no PATH dependency
```

Written for assistants that read `SKILL.md` — Claude Code, Opencode, Codex. The
CLI also works on its own if you prefer driving it by hand.

---

## Commands

| Command | What |
|---|---|
| `kb status` | where the kb is, file count, current snapshot, largest files |
| `kb check` | mechanical drift; exit 3 = go fix it |
| `kb verify` | suspicions: vanished paths, notes past their re-check age |
| `kb sync` | rebuild the index table from front matter |
| `kb add <slug> --kind <k> --title "…"` | next numbered note + front matter + rebuild |
| `kb outline [file]` | section map with weights — where the seams for a split are |
| `kb list [--scan DIR] [--prune]` | every kb known on this machine |
| `kb adopt [--apply] [--in-place]` | migrate a hand-made notes directory |
| `--dir X` | operate on X instead of `./kb` |

---

## Configuration

| Variable | Default | Controls |
|---|---|---|
| `KB_LANG` | `ru` | language of text written **into** notes — table header, the "current snapshot" line, the index skeleton. Diagnostics are always English. |
| `KB_REGISTRY` | `$HOME/.local/state/kb/registry.txt` | where the list of known kb directories lives |
| `KB_DOC_DIR` | `$HOME/.kb-docs` | install target for the manual |
| `KB_BIN_DIR` | `$HOME/.local/bin` · `%LOCALAPPDATA%\kb\bin` | install target for the optional PATH copy |

A team writing notes in English sets `KB_LANG=en` once. Existing notes are
unaffected — the setting only applies to text generated from then on. Adding a
language means adding one key to the `STRINGS` dict in the CLI.

No path anywhere is hardcoded to a particular machine.

---

## Design notes

Worth knowing before extending it:

- **Numbering gaps are never reused.** A number that once pointed at a file may
  still be cited from a commit message or another note.
- **Row order is by number**, so editing one file does not reshuffle the table and
  diffs stay small.
- **`verify` only checks paths inside backticks whose root exists.** Measured on a
  real 19-file kb: without both constraints you get 271 flags of which about 2 are
  real — URL paths, API versions, fragments of longer paths. With them: 6 flags,
  2 real. A report with the first ratio teaches you to ignore it within days. The
  cost is that a path inside a fenced block is not checked.
- **Size thresholds are 400 and 1200 lines.** The familiar "keep it under 200
  lines" rule is about instruction files that load into context on every turn.
  These are read on demand, one at a time, so it does not transfer.
- **Front matter is parsed without a YAML dependency** — flat `key: value` pairs
  between `---` fences, splitting on the first colon so titles may contain them.

---

## Uninstall

```bash
rm -rf <skills-dir>/kb
rm -f  ~/.local/bin/kb        # only if --with-path was used
rm -rf ~/.local/state/kb      # the registry
rm -rf ~/.kb-docs
```

Your notes are untouched — they were never inside the tool.

---

## License

MIT.
