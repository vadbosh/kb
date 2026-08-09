# kb

**A knowledge base in plain Markdown whose index cannot rot, where every fact is
typed by how it goes out of date.**

Point it at anything you would otherwise keep as a growing pile of `.md` files —
a migration, an incident, a research thread, a renovation, a legal case. Nothing
about it is specific to code.

[Русская версия](README.RU.md) · Full manual: [English](docs/kb.en.md) · [Русский](docs/kb.ru.md) · [Changelog](CHANGELOG.md)
Using it from a terminal, without an assistant: [CLI guide](docs/cli.en.md) · [по-русски](docs/cli.ru.md)

**Just want to start?** → [Install](#install), then [Usage](#usage). Three steps.

---

## The idea

Almost everyone ends up keeping a wiki for their own work: one file listing the
rest, topic files around it. While there are few files, it holds together.

Then files get added, renamed, split. Each of those changes means editing the
list by hand, and sooner or later nobody does. That is where the divergence
starts: the "current status" section keeps a date no one refreshed, links lead to
files that moved long ago, and a stack of `00-overview.md.bak.*` builds up beside
the directory — one copy per attempt to put the index back in order.

Three mechanisms below work against that. The first two remove the source of the
divergence automatically. The third fixes nothing — it shows you where the
divergence has already happened.

### 1. The index is generated, not maintained

Every note opens with three front-matter fields. This is the top of
`kb/02-pipeline.md`:

```yaml
---
title: how the pipeline works
kind: reference
updated: 2026-08-05
---
# the note itself follows
```

The index is `kb/00-overview.md`. The first `/kb save` creates it: headings, a
rules section, a paragraph about what the work is. From then on that text is
ordinary text — the assistant extends it as the work goes, or you edit it by hand.

Inside the index sits a region between two markers. That region, and only that
region, kb rebuilds from the front matter of every note:

```markdown
## Where to start reading          <- your text, kb never touches it

<!-- kb:begin -->                  <- everything down to kb:end is generated
Current snapshot: `21-state-2026-08-07.md` (2026-08-07).

| what you need            | file             | kind      | updated    |
|--------------------------|------------------|-----------|------------|
| how the pipeline works   | `02-pipeline.md` | reference | 2026-08-05 |
| traps and check commands | `23-traps.md`    | recipe    | 2026-08-07 |
<!-- kb:end -->

Prose again: what the work is, what does NOT go here, where else to look.
```

Nobody edits the snapshot line or the table — not you, not the assistant. Both are
assembled from the files on every `kb sync`, and an edit inside the markers is
lost. Such a table cannot disagree with the files: it came from them. Anything
outside the markers kb never touches.

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

### 3. Two independent checks watch for staleness

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

A command name on its own works too — `/kb check`, `/kb status`, `/kb list`. The
assistant runs that one command and reports what it said, without loading the
notes or writing anything.

There is no `/kbsave` or `/kbrestore` — the skill is named `kb`, so the command
is `/kb` and the half is chosen by the first word. Saying "kbsave" or "kbrestore"
inside a sentence usually works as well, since both are listed in the skill's
description, but that is recognition rather than a command.

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
- **No opinion about your writing.** Only the managed block is generated.

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
| `kb streams [--sessions N]` | which directories this session touched, read from the transcript |
| `kb adopt [--apply] [--in-place]` | migrate a hand-made notes directory |
| `kb hook --install` | git pre-commit that refuses a commit on exit 4 |
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

## Credentials

`kb check` scans the notes for credentials on every run — which means on every
`/kb save`, since the skill calls it there. Two layers, and the report always
says which of them ran:

```
secrets: none found — checked with built-in patterns + trufflehog 3.95.3
secrets: none found — checked with built-in patterns only
         install gitleaks or trufflehog for the full ruleset
```

**Layer 1, always** — fifteen patterns, no install, works everywhere. Twelve
match a shape with an unmistakable prefix or header: AWS access keys, GitHub,
Slack, Google, Stripe, OpenAI-family and Atlassian tokens, PEM private keys,
JWTs, passwords inside connection URLs, `IDENTIFIED BY '…'` in SQL.

Three more require **the variable name and the value shape together**, because
the secret itself has no prefix — an AWS secret access key is forty characters of
base64 and nothing else. `aws_secret_access_key = <40 base64>` has no innocent
reading; a bare forty-character token has many. Each of these was measured
against both live note directories before being added: zero matches, so they do
not collide with ordinary text.

**Layer 2, when present** — `gitleaks`, `trufflehog` or `detect-secrets`,
whichever is found on PATH first, run over the same directory. Roughly 150 rules
instead of ten. Missing is not an error; it narrows coverage, and the report
says so.

A finding exits **4**, distinct from 3 for ordinary drift, so a hook or a
pipeline can tell "the table is stale" from "there is a key in a note".

### What it does not catch

An entropy pass was written for this and then removed. On two real note
directories it produced four findings, all four false: a file path, a config
value, a Kubernetes pod name, another path. Identifiers and paths are long and
look random; no threshold separated them from a token. A report at that ratio
stops being read within days.

So **a short generic password sitting in a sentence is caught by nothing here** —
not by the built-in patterns, not by gitleaks, not by trufflehog. The author of
gitleaks says as much about `MyServiceToken="secret123"`. This lowers the risk;
it does not replace not writing credentials down.

### Testing the scan

A credential with a correct format is indistinguishable from a live one, both to
this scan and to everyone else's. **Do not commit sample credentials as test
fixtures**, even fake ones: GitHub's own secret scanning will flag them, and so
will the scanners of everyone who clones the repository. Generate them inside the
test from a template instead, so no valid-looking value is ever stored in a file.

The same applies to the notes themselves. A fake key pasted into a note "to see
what happens" is a real finding as far as every tool is concerned.

### Blocking a commit

```bash
kb hook --install     # git pre-commit; refuses a commit on exit 4
```

Only meaningful when the notes are inside a git repository. Plenty are not — in
that case the control that applies is `kb check` at the end of every save, which
runs regardless.
---

## Design notes

Worth knowing before extending it:

- **Numbering gaps are never reused.** A number that once pointed at a file may
  still be cited from a commit message or another note.
- **Row order is by number**, so editing one file does not reshuffle the table and
  diffs stay small.
- **`verify` checks a path only when both conditions hold**: it is written in
  backticks, and its root exists on disk. Measured on a real 19-file kb: without
  them you get 271 flags of which about two are real — URL paths, API versions,
  fragments of longer paths. With them: 6 flags, 2 real. At the first ratio the
  report stops being read within days. The cost is that a path inside a fenced
  block is not checked.
- **Size thresholds are 400 and 1200 lines.** The familiar "keep it under 200
  lines" rule is about instruction files, which load into context on every turn.
  kb files are read on demand and one at a time, so that rule does not apply to
  them.
- **Front matter is parsed without a YAML dependency** — flat `key: value` pairs
  between `---` fences, split on the first colon so that a title may contain a
  colon of its own.

---

## Tests

```bash
python3 tests/test_kb.py          # a few seconds, standard library only
python3 tests/test_kb.py -v       # one line per test
python3 tests/test_kb.py Guards   # one group
```

Each run gets a temporary directory with its own `HOME` and its own
`KB_REGISTRY`, so real notes and the real registry are never touched.

What is covered is either a guard the tool exists to enforce — writing outside
the current directory, into `$HOME`, into a directory on `PATH` — or a bug that
shipped once, with its version named in the test. What is deliberately **not**
covered is whether a note is *useful*: that was attempted, measured against
nineteen real notes, and abandoned, because no mechanical signal separated the
adequate ones from the inadequate.

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
