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
`references/restore.md` to read. You address them by saying `kbsave` or
`kbrestore`; the slash form is `/kb save` and `/kb restore`.

Normal work never touches the shell — the skill calls the CLI itself. The one
routine exception is `kb adopt`, once per directory you are migrating.

Install, configuration and uninstall: [README.md](../README.md#install).

---

## Work cycle

### Session 1, new project

Nothing to prepare in advance — and nothing appears by itself either.
**Launching the assistant does not create `kb/`.** The directory comes into
existence the first time you say `kbsave`, and until then the project has none.

```
$ cd /path/to/project
$ claude
> figure out why fluent-bit is not reaching the database
...
> kbsave
```

The skill does the rest: `kb status` (empty → creates `kb/`), picks the `kind`,
writes the `title`, creates the file, rebuilds the index. It reports counts:

```
kb: created /path/to/project/kb, +1 reference (01-fluentbit-pipeline.md). Index rebuilt.
```

Bare `kbsave` = "decide yourself what from this session is durable". Scope it
explicitly with `kbsave about the fluent-bit pipeline`.

A second trap later would be **appended to the same** `recipe` file rather than
spawning a new one — that is the append-or-new decision.

### Session 2, resuming

```
$ claude --resume <ID>
> kbrestore
```

The skill runs `kb status` + `kb check` + `kb verify`, reads the index and the
current snapshot, then compares that against what the restored conversation
shows:

| What it finds | What it says |
|---|---|
| same snapshot, `check` clean | "context still valid, nothing to re-read" — spends no tokens |
| a newer `state` appeared | reads it: "the situation changed, here is how" |
| `check` reports drift | "notes were edited without a sync" — reads the changed files |

Then a briefing: state / what is open / which files this task needs.

If you resumed immediately and nothing on disk moved, `kbrestore` is not needed —
it earns its keep when **time has passed** or **another session wrote**.

### Cheat sheet

| Moment | Type |
|---|---|
| record what was learned | `kbsave` |
| record specifically about X | `kbsave about X` |
| capture a dated snapshot | `kbsave state snapshot` |
| resumed a session, need context | `kbrestore` |
| what is in the notes at all | `kbrestore` |

`kbsave` and `kbrestore` are ordinary words in a prompt — the skill picks them
up. `/kb save` and `/kb restore` are the explicit slash form and do the same.

---

## Writing

```bash
kb add why-x-target --kind decision --title "why routing by X-Target, not Host"
```

The file gets front matter; you write the body.

**Number** — the next free one. Gaps are never reused: a number that once pointed
at a file must not later point at a different one.

**Kinds** — five, and the distinction that earns its keep is whether a newer file
replaces this one:

| kind | holds | superseded |
|---|---|---|
| `state` | snapshot on a date: what is done, what is open | yes, by a later date |
| `plan` | what is planned, in what order | yes, when executed |
| `decision` | a choice and why | no — only `--supersedes` |
| `reference` | how something works | no — edited in place |
| `recipe` | traps and verification commands | no — edited in place |

`state` must carry a date in its name; `kb add state --kind state` adds today's.
The index computes which snapshot is current and marks the earlier ones.

Edited a file → bump `updated:` → `kb sync`. Deleted or renamed → `kb sync`.
Before you call the work documented → `kb check` (exit 3 = drift).

---

## How the index updates

Front matter is the source of truth; the table is derived from it.

```
kb/02-pipeline.md              kb/00-overview.md
---                            <!-- kb:begin -->
title: how the pipeline works ┐ | what you need | file | kind | updated |
kind: reference               ├►| how the pipeline works | `02-pipeline.md` | reference | … |
updated: 2026-08-05           ┘ <!-- kb:end -->
---
```

`kb sync` rewrites **only** the text between the markers. Everything else in the
index is byte-for-byte untouched.

Computed automatically, never written by hand: the current snapshot (max date
among `state` files), the marker on earlier ones, row order (by number, so
editing one file does not reshuffle the table), and the next free number.

---

## File size

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
meaning. But no manual monitoring either — `kbsave` runs `kb check` at the end of
every write, and the skill must act on a size warning in the same turn.

---

## Checking against reality

`check` compares the index with the files — **internal consistency**, not
whether the notes are still true. That is a separate command:

```bash
kb verify
```

`verify` reports **suspicions**, not defects, which is why it is not part of
`check`. `check` is binary and mechanical: exit 3 means go fix it. `verify` works
by heuristic: exit 3 means go look. Merging them would drown an exact signal in
guesses.

**Paths.** A path is checked only when both conditions hold: it is written in
backticks, and its root — the first two components — exists on disk. Measured on
a real kb: without them you get 271 flags out of 296 paths, roughly two of them
real — URL paths (`/stats/prometheus`), API versions (`/v1alpha1`), fragments of
longer paths. With them: 6 flags, 2 real.
The trade-off is that a path inside a code block, without backticks, is not
checked. Deliberate — otherwise the report teaches you to ignore it.

**Age by kind.** Not "wrong", just "nobody has looked at this in a while":

| kind | threshold |
|---|---|
| `recipe` | 120 days — rots when the tooling changes |
| `reference` | 180 days |
| `decision` | **never checked** — why a choice was made stays true |
| `state`, `plan` | not checked — supersession already covers them |

**What `verify` cannot do**: tell whether a claim about a live cluster still
holds ("the NLB is called X", "there is no Gateway API CRD in AU"). That needs
the cluster itself — credentials, cost, and nobody should run `terraform` or
`kubectl` on a schedule against production. Reasoning ("why X-Target rather than
Host") is not verifiable at all.

---

## Registry

`kb list` shows every known notes directory. The registry lives at
`~/.local/state/kb/registry.txt` (override with `KB_REGISTRY`), is appended to
whenever a kb is created, and is verified on read:

```bash
kb list                    # path, file count, current snapshot, heavy files
kb list --scan /projects   # pick up kbs created before the registry, or by hand
kb list --prune            # drop entries whose index disappeared
```

---

## Commands

| Command | What |
|---|---|
| `kb status` | where the kb is, file count, current snapshot, largest files |
| `kb check` | mechanical drift; exit 3 if any |
| `kb verify` | suspicions: vanished paths, notes gone stale; exit 3 |
| `kb sync` | rebuild the index table from front matter |
| `kb add <slug> --kind <k> --title "..."` | new file + front matter + rebuild |
| `kb list [--scan DIR] [--prune]` | every known kb |
| `kb outline [file]` | section map with weights — where the seams are |
| `kb init [--title ...]` | index skeleton only |
| `kb adopt [--apply] [--in-place]` | migrate an existing hand-made directory |
| `--dir X` | operate on X instead of `./kb` |

`kb check` catches: stale table, links to deleted files, files without front
matter, `.md` outside the `NN-slug.md` scheme, leftover `.bak`, oversized files.

Notes always live in `kb/`. Next to a loose `00-overview.md`, `add` and `init`
refuse to run — that would split the notes across two places. Escape hatch:
`adopt --in-place`, only when something outside links the old paths.

---

## Language

Diagnostics are English. Text the tool writes **into** the notes (table header,
"current snapshot" line, the index skeleton) follows `KB_LANG` — default `ru`,
set `KB_LANG=en` for English. Adding a language means adding one key to the
`STRINGS` dict in the CLI.

---

## Do not

- Edit the table between `kb:begin` / `kb:end` — the next `kb sync` overwrites it.
- Rewrite prose outside the markers — it is the human's.
- Store credentials. Reference the mechanism (a secret in the cluster, an env
  var), never the value.
- Duplicate documentation that lives next to the code — it is edited together
  with the code. Name its path instead.
- Keep a diary. A `state` file is a snapshot, not "what we did on Tuesday".
