# kb — the manual

A Markdown knowledge base per work stream: an index `00-overview.md` plus
numbered files `NN-slug.md`. Two properties carry the whole design:

- **the index table is generated** from each file's front matter, so it cannot
  drift from the files it describes
- **every note is typed by how it expires** — `state` and `plan` are superseded
  by newer ones, `reference` and `recipe` are edited in place, a `decision`
  never expires because it records why a choice was made

Why that matters, and what the tool refuses to do, is in
[README.md](../README.md). This file is the working manual: how to drive it day
to day and what each mechanism actually guarantees.

| Layer | Owns | Lives in |
|---|---|---|
| Skill `kb` | judgement — what to write, where, what to read | your assistant's skills directory |
| CLI `kb` | mechanics — numbering, the table, drift detection | `<skill-dir>/scripts/kb` |

The skill loads one half on demand: `references/save.md` to write,
`references/restore.md` to read. There is one command, `/kb`, and the half is
chosen by the argument: `/kb save` and `/kb restore`.

A third file, `references/entry-point.md`, loads on a narrower condition: a
command printed a `⚠` about `AGENTS.md` and named the file beside it. What to do
about those findings is a page of instructions worth nothing on the saves where
the entry point is fine, which is most of them.

Normal work never touches the shell — the skill calls the CLI itself. The one
routine exception is `kb adopt`, once per directory you are migrating.

Install, configuration and uninstall: [README.md](../README.md#install).
Using it from a terminal without an assistant: [cli.en.md](cli.en.md).

---

## Work cycle — what to type and when

### Session 1, new project

Nothing to prepare in advance — and nothing appears by itself either.
**Launching the assistant does not create `kb/`.** The directory comes into
existence the first time you type `/kb save`. Until then the project has none.

**Notes are found from anywhere inside the project.** `./kb`, then `./.kb`,
then the same two in every directory above, stopping at the repository root — or
before `$HOME` when there is no repository. Work happens in a subdirectory more
often than in a project root, and a save from one joins the stream around it
rather than starting a second kb down there.

**Unless the project already has a `kb/` of its own.** It is an ordinary
directory name — source, a mount, a placeholder — so kb refuses to scaffold into
one it did not make, empty or not, and hands the choice back:

```
kb: /path/to/project/kb exists, holds 4 file(s), and has no 00-overview.md — it is
not a notes directory, and kb does not write into one it did not make.
  This is a decision for the person, not for kb. The options:
    ./.kb            a name kb also searches, so nothing needs --dir afterwards
    this directory   KB_ALLOW_EXISTING=1, if it is for the notes after all
    somewhere else   --dir <path>, and every later command needs it too
  Ask which, then re-run. kb has no preference between them.
```

Empty counts as taken: a directory somebody made is a placeholder for what they
are about to put in it. `./.kb` is the second name kb searches, so choosing it
costs nothing afterwards — no `--dir` on later commands, nothing to remember.
The entry point still goes to the **project root**, not inside the notes.

```
$ cd /path/to/project
$ claude
```

You work as usual; kb takes no part in it:

```
> figure out why fluent-bit is not reaching the database
```

Something worth keeping has turned up:

```
> /kb save
```

From here the skill does the rest itself: checks `kb status` (empty, so it
creates `kb/`), picks the `kind`, phrases the `title`, writes the file, rebuilds
the index. Then it reports in counts:

```
kb: created /path/to/project/kb, +1 reference (01-fluentbit-pipeline.md). Index rebuilt.
```

`/kb save` with nothing after it means "decide yourself what from this session is
worth keeping". Name the subject if you would rather be explicit:
`/kb save about the fluent-bit pipeline`.

Next task, next result, save again:

```
> why does terraform init fail with text file busy
...
> /kb save
```

That one is a known trap, so `kind: recipe`. No such file exists yet, so a new
one appears:

```
kb: +1 recipe (02-traps-and-recipes.md). Index rebuilt.
```

A third trap of the same sort would be **appended to that same**
`02-traps-and-recipes.md` rather than breeding files. That is what the
append-or-new decision looks like in practice.

Leaving the assistant: `/exit`.

### Session 2, resuming

```
$ claude --resume <ID>
```

You need the previous snapshot:

```
> /kb restore
```

The skill runs `kb status` + `kb check` + `kb verify`, reads the index and the
current `state`, and compares that against what the conversation already holds.
One of three answers:

| What it finds | What it says |
|---|---|
| same snapshot, `check` clean | "context still valid, nothing to re-read" — spends no tokens |
| a newer `state` appeared | reads it: "the situation changed, here is how" |
| `check` reports drift (exit 3) | "notes were edited without a `kb sync`" — reads the changed files, not the table |

Then a briefing: state, what is open, which files this task needs.

If you resumed straight away and nothing on disk moved, `/kb restore` can be
skipped — it is all in the conversation already. It earns its keep when **time
has passed** or **another session was writing**.

Task done, save:

```
> /kb save
```

Files exist by now, so more often it will **append**. This is usually the point
where a snapshot belongs:

```
> /kb save state snapshot
```

→ `03-state-2026-08-07.md`; the index marks it current by itself and tags the
previous one `⏳ (earlier snapshot)`.

### Cheat sheet

| Moment | Type |
|---|---|
| record what was learned | `/kb save` |
| record specifically about X | `/kb save about X` |
| capture a dated snapshot | `/kb save state snapshot` |
| resumed a session, need context | `/kb restore` |
| what is in the notes at all | `/kb restore` |

The command is `/kb`, with the half chosen by the first word: `/kb save` and
`/kb restore`. There is no `/kbsave` or `/kbrestore` — the skill is named `kb`.
Saying "kbsave" or "kbrestore" inside a sentence usually works too, since both
are listed in the skill's description, but that is recognition rather than a
command.

You never need the shell — the skill calls `kb` itself. One exception:
`kb adopt`, once, to migrate an older directory.

---

## Writing

```
/kb save
/kb save about the terraform init problem
```

The skill handles all of it:

1. `kb status` — what is already there
2. decides: **append** to an existing file, or **start a new one**
   - append — when this is one more instance of what that file already covers
   - new — when it answers a different question, or it is a `state` or a
     `decision` (points in time, never appended to)
   - split an existing one — when it is over ~400 lines **and** its sections are
     about different things
3. picks the `kind`, writes a `title` from the reader's side ("what do I need",
   not "what is this document called")
4. `kb add --body-file -` — front matter and body in one write → `kb sync` → `kb check`
5. reports in counts: `+1 decision (04-why-x-target.md), edited 03-traps.md`

Nothing worth keeping → it says `Nothing durable for kb.` and creates no empty
files.

### The six kinds

| kind | holds | superseded |
|---|---|---|
| `charter` | why the stream exists, its boundaries, what is deliberately not done | no — edited in place, one per kb |
| `state` | snapshot on a date: what is done, what is open | yes, by a later date |
| `plan` | what is planned, in what order | yes, when executed |
| `decision` | a choice and **why** | no — only `--supersedes` |
| `reference` | how something works | no — edited in place |
| `recipe` | traps and verification commands | no — edited in place |

A `state` gets today's date into its filename automatically.

---

## Resuming an old session

```
/kb restore
```

`claude -r` brings the conversation back, but the files may have moved on
meanwhile: you edited them, another session edited them, or details dropped out
when the context was compacted. The result is an agent remembering one state of
the notes while the disk holds another.

`/kb restore` is exactly that reconciliation:

1. `kb status` — which snapshot is current **now**
2. `kb check` — the index has not drifted from the files
3. `kb verify` — nothing vanished, no note left unvisited too long
4. reads the index, reads the current snapshot
5. **compares that against the conversation** and says so plainly:
   - same snapshot, `check` clean → context still valid, nothing to re-read
   - a newer `state` appeared → reads it, the situation has changed
   - `check` reported drift → the notes were edited without a `sync`, so it reads
     the changed files

Then the briefing: state, what is open, which files this task needs, what drift
turned up. Not one file retold after another — a digest. The rest is opened as
needed, going by the "what you need" column in the index.

None of this fires by itself at session start; you ask for it. A `SessionStart`
hook is deliberately not wanted here — the reconciliation is worth doing when you
sit down to work, not on every launch of the assistant.

---

## How the index updates

Front matter is the source of truth; the table is derived from it.

```
kb/02-pipeline.md          kb/00-overview.md
---                        <!-- kb:begin -->
title: how it works  ──┐   | what you need | file | kind | updated |
kind: reference        ├──►| how it works | `02-pipeline.md` | reference | … |
updated: 2026-08-05  ──┘   <!-- kb:end -->
---
```

`kb sync` reads the front matter of every `NN-*.md` and rewrites **only** the
text between the markers. Everything else in the index stays byte for byte.

| Action | Index |
|---|---|
| `kb add` (inside `/kb save`) | rebuilt at once |
| editing `title` / `kind` / `updated` | needs `kb sync` |
| file deleted or renamed | needs `kb sync` |

Between editing a file and running `kb sync` the index is out of date — which is
what `kb check` catches (`index table is stale`, exit 3). Inside `/kb save` both
`sync` and `check` run on their own.

**Computed automatically, never written by hand:**

- the current snapshot — the highest date among `state` files, on its own line
  above the table
- earlier snapshots are tagged `⏳ (earlier snapshot)`
- `supersedes:` in a note's front matter marks both rows: the replacing note
  reads `decision ⤺ 01` in the kind column, the replaced one
  `⤺ (reversed by 03)` in its description. The replaced file stays where it is —
  the reasoning behind the old choice is usually what someone needs six months
  later. If it was deleted instead, there is no row to mark and its name stops
  counting as a broken link
- row order — by file number, so editing one file does not reshuffle the table
- the number of a new file — the next free one; freed numbers are never reissued
  (something may still point at a number that once belonged to a file)

---

## The entry point at the project root

Everything described above starts with the `kb brief` command. Someone who does
not know the notes exist will not run it. A file at the project root, though, is
what an agent reads every time.

```
kb route
```

`kb route` writes two files into the project root. The first is `AGENTS.md`,
holding the pointer to the notes, the charter and the current snapshot. The
second is `CLAUDE.md`, holding one line: `@AGENTS.md`.

There are two files because Claude Code reads `CLAUDE.md` and does not read
`AGENTS.md`, while Codex and Opencode read `AGENTS.md`. The text itself lives
only in `AGENTS.md`; `CLAUDE.md` imports it.

`/kb save` calls `kb route` too — when it creates the `kb/` directory in a
project that has no `AGENTS.md` yet. Where `AGENTS.md` already exists, `/kb save`
only offers to run `kb route` and touches the file itself not at all.

**What is generated and what is yours.** Between the `kb:begin` and `kb:end`
markers is what kb derives from the notes; `kb route` and `kb sync` keep that
block current. Outside the markers is your text: what the work is, the check
commands, the definition of done. The CLI leaves them as `kb:fill` comments,
because a CLI cannot write prose — **`/kb save` fills them in the same turn**,
from the notes it just wrote and the commands the session actually ran, and says
what it wrote so you can correct it. It asks instead of guessing only where the
session holds no answer: a stream that ran nothing has no honest check command,
and a made-up one lands in a file an agent will execute. An
`AGENTS.md` without markers kb does not touch and refuses to write to. A
`CLAUDE.md` without the import kb does not write to either — it prints the line
for you to add by hand.

**Length.** Both files reach the context window at every session start, so their
combined length is capped at 200 lines. Everything the host expands at launch
counts towards it — an `@path` import up to four hops deep, and `CLAUDE.local.md`
alongside `CLAUDE.md`.

The cap applies per launch directory, not per file. A session started in a
subdirectory loads that directory's `CLAUDE.md` on top of every ancestor's, so
`kb route` and `kb verify` report those chains as well as the root, worst first.
kb will not shorten any of them: outside the markers the text is yours.

## Versioned, or only on this machine

Notes inside a git repository are committed by default — nobody chooses that,
`git add -A` does. The question is asked once, when the directory is created,
because after that it never arises again:

```
kb local          # .git/info/exclude — the notes stay here
                  # or commit them, and they ship with the project
```

`.git/info/exclude` and not `.gitignore`: the latter is itself committed, so it
imposes one person's choice on everyone who clones the repository.

Nothing is stored about the answer — `kb status` asks git. A stored flag would
be a second copy of a fact git already owns, and the two part company the first
time someone edits an ignore rule.

---

## CLI reference

| Command | What |
|---|---|
| `kb status` | where the kb is, file count, current snapshot, largest files |
| `kb brief` | the overview and the current snapshot printed verbatim — same bytes every run |
| `kb check` | mechanical drift; exit 3 if any |
| `kb verify` | suspicions: vanished paths, notes gone stale, work that outran the notes; exit 3 |
| `kb sync` | rebuild the index table from front matter |
| `kb add <slug> --kind <k> --title "..."` | new file + front matter + rebuild |
| `kb list [--scan DIR] [--prune]` | every known kb: where it lives, what is inside |
| `kb streams [--sessions N]` | where this session stands, then which directories it touched — read from the transcript |
| `kb outline [file]` | section map with weights — where the seams are |
| `kb init [--title ...]` | index skeleton only |
| `kb adopt [--apply] [--in-place]` | migrate an existing hand-made directory |
| `kb hook --install` | git pre-commit that refuses a commit on exit 4 |
| `kb route` | `AGENTS.md` at the project root + a `CLAUDE.md` that imports it |
| `kb local [--dry-run]` | keep the notes out of git (`.git/info/exclude`) |
| `--dir X` | operate on X instead of `./kb` or `./.kb` |

`kb check` exits 3 on drift and **4 when a credential is found in a note**. What
the scan covers and what it cannot is in
[README](../README.md#credentials).

`kb check` catches: a stale table, links to deleted files, an `updated` that is
not a date, whitespace in a filename, files without front
matter, `.md` outside the `NN-slug.md` scheme, leftover `.bak`, **files past the
size threshold**.

### File size

The "no more than 200 lines" rule is about instruction files (`CLAUDE.md`,
`rules/*.md`, `SKILL.md`) that load into context **every turn**. kb files are
read selectively, one at a time, so the threshold is different and looser:

| Threshold | Meaning |
|---|---|
| 400 lines | worth checking whether the sections answer different questions |
| 1200 lines | one `Read` is expensive; the file is marked `⚠ ~Nk tokens` in the index |

**Size alone is never a reason to split.** A long coherent `reference` is a good
file. The real criterion is mixed `kind`s in one file, because `kind` is exactly
"which question does this answer". Judge with `kb outline` — a dozen headings
instead of reading fifteen hundred lines.

There is no auto-splitting and there will not be: where to cut is a question of
meaning. But no manual watching either — `/kb save` runs `kb check` at the end of
every write, and the skill must act on a size warning in the same turn.

### Checking against reality

`check` compares the index with the files — **internal consistency**, not whether
the notes are still true. That is a separate command:

```bash
kb verify
```

`verify` reports **suspicions**, not defects, which is why it is kept out of
`check`. `check` is binary and mechanical: exit 3 means go fix it. `verify` works
by heuristic: exit 3 means go look. Merging them would drown an exact signal in
guesses.

**Paths.** A path is checked only when both conditions hold: it is written in
backticks (`` `like this` ``), and its root — the first two components — exists
on disk. Measured on a real kb: without them you get 271 flags out of 296 paths,
roughly two of them real — URL paths (`/stats/prometheus`), API versions
(`/v1alpha1`), fragments of longer paths. With them: 6 flags, 2 real. The other
side of the bargain is that a path inside a code block, without backticks, goes
unchecked. Deliberate — at the opposite ratio the report soon stops being read.

A `~/…` path counts as absolute and is expanded before the test. It was left out
at first as shell syntax rather than a path, which quietly exempted the one shape
people write for a file in their home directory.

Paths are looked for in the notes, in the overview, and in the entry point —
`AGENTS.md`, `CLAUDE.md` and whatever they import. The entry point is the file an
agent reads before touching the project, and in a repository that excludes AI
artifacts from git no commit hook sees it either.

**Work ahead of the notes.** kb takes the newest file in the work directory and
compares it against the newest file in `kb/`. A gap of more than an hour means
something was done and not written down.

Git is not used here — more than half of all work streams are not repositories.

Not counted as work:

| Skipped | Why |
|---|---|
| the `kb/` directory itself | a record of the work, not the work |
| `AGENTS.md` and `CLAUDE.md` at the root | kb writes them |
| a nested kb — `<dir>/kb/00-overview.md` or a loose overview | that is the neighbouring stream |
| directories in `.gitignore` | build output |

**Age by kind.** Not "wrong", just "nobody has looked at this in a while":

| kind | threshold |
|---|---|
| `recipe` | 120 days — goes stale as the tooling moves |
| `reference` | 180 days |
| `charter` | 365 days — direction is meant to outlive a release; flagging it sooner would train you to skip the whole report |
| `decision` | **never checked** — why a choice was made stays true |
| `state`, `plan` | not checked — supersession already covers them |

**What `verify` cannot do**: confirm a claim about a live system ("the NLB is
called X", "there is no Gateway API CRD in AU"). That needs the system itself —
credentials, cost, and nobody is going to run `terraform` or `kubectl` against
production on a schedule. Reasoning ("why X-Target rather than Host") is not
verifiable at all.

### Registry

`kb list` shows every known notes directory. The registry lives at
`~/.local/state/kb/registry.txt` (override with `KB_REGISTRY`). It fills itself
as kbs are created, and on read every path is checked for whether it still
exists:

```bash
kb list                    # every kb: path, file count, current snapshot, heavy files
kb list --scan /projects   # pick up kbs created before the registry, or by hand
kb list --prune            # drop entries whose index disappeared
```

Notes always live in `kb/`. If `00-overview.md` sits loose in the directory root,
`add` and `init` refuse to run — otherwise one directory ends up holding two sets
of notes. Escape hatch: `adopt --in-place`, only when something outside links the
old paths.

A flat layout is therefore never started by accident. A stream directory always
exists before the notes do, and kb does not scaffold into a directory it did not
make, so the two ways in are `adopt --in-place` on notes that are already there,
and `KB_ALLOW_EXISTING=1` on a directory that is meant to hold them. Both are
read and written like any other kb afterwards.

---

## Do not

- Edit the table between `kb:begin` / `kb:end` — the next `kb sync` overwrites it.
- Rewrite text outside the markers without being asked — a human wrote that
  wording.
- Store credentials. Reference the mechanism (a secret in the cluster, an env
  var), never the value.
- Duplicate documentation that lives next to the code — it is edited together
  with the code. Name its path instead.
- Keep a diary. A `state` file is a snapshot, not "what we did on Tuesday".

---

## Language

Tool diagnostics (`check` / `list` / `outline` / `status`) are English. Text the
tool writes **into** the notes — the table header, the "current snapshot" line,
the index skeleton, the generated block of `AGENTS.md` — follows the language of
the kb itself. A new language is one key in the `STRINGS` dict inside the CLI
and nothing else.

**The language belongs to the kb, not to the machine.** It is recorded in the
`kb:begin` marker of the overview when the directory is scaffolded, and read
back by every command after that. Two streams in two languages therefore sit on
one machine without interfering, and a kb cloned onto a machine set up
differently keeps its own. `KB_LANG` decides for a kb that has no language
recorded yet — a new one, or one made before this was so, which picks up the
mark on its next `kb sync`.

### Switching a kb from one language to another

Pointing `KB_LANG` at an existing kb does not switch it, and `kb check` reports
the attempt rather than acting on it. The reason is that only part of the file
is the tool's to write:

| What | Changes on `kb sync` |
|---|---|
| the marker, the table header, the "current snapshot" line, the block in `AGENTS.md` | yes |
| the `title:` of every note | no — written by hand |
| the prose outside the markers in `00-overview.md` | no |
| the sections of the entry point somebody filled | no |
| the body of every note | no |

Flipping the setting alone therefore produces an English header over Russian
titles. The order that works:

```
1. translate the `title:` of every note, the prose outside the markers, and the
   filled sections of AGENTS.md
2. KB_LANG=<new> kb sync        the generated parts follow, and the mark is rewritten
3. kb check                     the index agrees with the front matter again
```

Step 1 is the whole job and no command does it; kb has no language migration.

Skill trigger phrases are bilingual — both "запиши в kb" and "save to kb" work.
The bodies of the skills are English, since an LLM is what reads them.
