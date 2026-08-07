---
name: kbsave
description: Handle phrases "kbsave", "/kbsave", "запиши в kb", "запиши в заметки", "save to kb", "оформи в kb", "задокументируй это" by writing durable knowledge from the current session into the project's kb/ work-notes directory via the `kb` CLI. Use whenever the user wants findings, decisions, traps or a state snapshot persisted as readable notes rather than left in the conversation.
version: "1.0.0"
---

# kbsave

Write what was learned into `kb/` — the project's work-notes directory with a
generated index. Counterpart of `kbrestore`.

## Tool

`kb` CLI at `~/.local/bin/kb`. Pure stdlib, no dependencies.

```bash
kb status                                     # where the kb is, what is in it
kb add <slug> --kind <kind> --title "<...>"   # new note + front matter + reindex
kb sync                                       # rebuild the index table
kb check                                      # drift; exit 3 if any
```

Resolve the directory from cwd (`./kb`). If cwd is not the project, pass
`--dir <path>`. If no `kb/` exists yet, `kb add` creates it — no `init` needed.

## Skip-if-trivial guard

No findings, no decisions, no traps, nothing that outlives the conversation →
say `Nothing durable for kb.` Do NOT create empty notes.

## Step 1 — decide: append or new file

Run `kb status` first to see what already exists.

**Append to an existing file** when the fact is one more instance of what that
file already covers — another trap for a `recipe` file, another component in a
`reference`. Then: edit the file, bump `updated:` in its front matter, `kb sync`.

**New file** when any of these holds:

- it answers a different question than every existing file (that is literally
  what the index column asks: *what do I need?*)
- it is a `state` or a `decision` — those are points in time, never appended to
- putting it in the obvious host would make that file cover two `kind`s at once

**Split an existing file** — never by size alone. `kb check` flags big files, but
the flag is an invitation to look, not a verdict: a long coherent reference is a
good file. The real criterion is whether the sections belong to different
**kinds**, because `kind` is exactly "which question does this answer".

Judging costs almost nothing — do NOT read the file to decide:

```bash
kb outline <file>     # sections with weights; no arg = every file over 400 lines
```

Read the heading map. Split only where one part describes **how things are**
(`reference`) and another **what to do** (`plan`), or a `recipe` has grown inside
a `state`. Cut on that seam, keep each part whole. If every section answers the
same question, leave the file alone however long it is — say so and move on.

## Step 2 — pick the kind

| kind | holds | replaced by a newer one? |
|---|---|---|
| `state` | snapshot on a date: what is done, what is open | yes, by a later date |
| `plan` | what is planned, in what order | yes, when executed |
| `decision` | a choice and **why**; alternatives rejected | no — `--supersedes` |
| `reference` | how something works; durable | no — edited in place |
| `recipe` | traps and ready-to-run verification commands | no — edited in place |

`state` gets today's date in the filename automatically.
Reversing an earlier decision → `--supersedes <file>`, do not rewrite the old one.

## Step 3 — write the title

`--title` becomes the index row, and that column answers **"what do I need?"** —
not "what is this document called". Write from the reader's side:

```
good   what is done and what is still open right now
good   traps and ready-to-run verification commands
bad    State as of 2026-08-05      (repeats the filename)
bad    Fluent-bit                  (a noun, answers nothing)
```

Write the title in **the language the notes are written in**, not the language of
this skill — it goes straight into a document a human reads.

## Step 4 — write the body, then sync

`kb add` creates the file with front matter and an H1; fill the body yourself.
Lead with the concrete subject. Prose, not a transcript — the durable model of
how something works, not the tape of what was typed.

Finish with `kb check` — **always, every time**. Exit 3 means something needs
attention; act on it in the same turn rather than leaving it for the user to
notice:

| What `check` reported | What to do |
|---|---|
| stale index table | `kb sync` |
| links a missing file | fix the link or restore the file |
| no front matter / unknown kind | add the front matter |
| **file over the size threshold** | `kb outline` → judge by kind-mixing → propose a seam OR say "no seam, leaving it" |
| `*.bak.*` left over | verify against the originals, then propose deleting |

Never stay silent about size and never defer it — it is the one signal that
otherwise accumulates for years. But never split silently either: propose the
seam, the decision is the human's.

### After a session that moved or renamed anything, run `kb verify`

`check` proves the notes are internally consistent. It says nothing about
whether they are still **true**. `kbrestore` runs `verify` at session start, so
the routine pass is covered — run it here only when THIS session moved, renamed
or deleted something the notes may point at:

```bash
kb verify     # vanished paths, notes past their re-check age; exit 3 = look
```

It reports **suspicions**, not errors. A flagged path may live inside a
container or on another host — verify before editing. Two rules learned the hard
way:

- **Confirm the replacement exists before rewriting a path.** A breadcrumb left
  by a human (`MOVED.md` and friends) can itself be wrong. `ls` the new path
  first, in a separate step from the edit.
- **`verify` only sees paths in backticks.** That filter is what keeps the
  report readable, but it means a stale path inside a code block slips through —
  grep for the old string too when fixing one.

## Never

- **Edit inside `<!-- kb:begin -->` / `<!-- kb:end -->`** — that table is
  generated; `kb sync` overwrites it. Change front matter instead.
- **Rewrite prose outside the markers** without being asked — it is the human's.
- **Write credentials.** Reference the mechanism (a secret in the cluster, an
  env var), never the value.
- **Copy documentation that lives next to the code** — it is edited together
  with the code. Name its path instead.
- **Keep a diary.** A `state` file is a snapshot, not "what we did on Tuesday".
- **Duplicate something that lives elsewhere** — reference it by path or URL.
  A copy goes stale silently; a link does not.

## Report

Counts and paths, not content:

```
kb: +1 decision (04-why-x-target.md), edited 03-traps-and-recipes.md, index synced.
```
