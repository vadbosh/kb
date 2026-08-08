# Writing to the notes

Triggered by "kbsave", "запиши в kb", "задокументируй это", or the end of a task
worth remembering. Read `SKILL.md` first — the tool contract, the five kinds and
the shared rules live there.

## Skip-if-trivial guard

No findings, no decisions, no traps, nothing that outlives the conversation →
say `Nothing durable for kb.` Do NOT create empty notes.

## Step 1 — append or new file

Run `kb status` first to see what already exists.

**Append to an existing file** when the fact is one more instance of what that
file already covers — another trap for a `recipe`, another component in a
`reference`. Then: edit the file, bump `updated:` in its front matter, `kb sync`.

**A new file** when any of these holds:

- it answers a different question than every existing file — which is literally
  what the index column asks: *what do I need?*
- it is a `state` or a `decision`; those are points in time, never appended to
- putting it in the obvious host would make that file cover two `kind`s at once

**Splitting an existing file** — never by size alone. `kb check` flags big files,
but the flag is an invitation to look, not a verdict: a long coherent reference
is a good file. The real criterion is whether the sections belong to different
kinds.

Judging costs almost nothing — do NOT read the file to decide:

```
kb outline <file>     sections with weights; no argument = every file over 400 lines
```

Read the heading map. Split only where one part describes **how things are**
(`reference`) and another **what to do** (`plan`), or a `recipe` has grown inside
a `state`. Cut on that seam and keep each part whole. If every section answers
the same question, leave the file alone however long it is — say so and move on.

## Step 2 — write the title

`--title` becomes the index row, and that column answers **"what do I need?"** —
not "what is this document called". Write from the reader's side:

```
good   what is done and what is still open right now
good   traps and ready-to-run verification commands
bad    State as of 2026-08-05      (repeats the filename)
bad    Fluent-bit                  (a noun, answers nothing)
```

## Step 3 — write the body

`kb add` creates the file with front matter and an `# H1`; you fill the body.
Lead with the concrete subject. Written text, not a transcript — the durable model of
how something works, not the tape of what was typed.

Reversing an earlier decision → `kb add … --kind decision --supersedes <file>`.
Do not rewrite the old one.

## Step 4 — finish with `kb check`, always

Exit 3 means something needs attention. Act on it in the same turn rather than
leaving it for the user to notice:

| What `check` reported | What to do |
|---|---|
| stale index table | `kb sync` |
| links a missing file | fix the link or restore the file |
| no front matter / unknown kind | add the front matter |
| **file over the size threshold** | `kb outline` → judge by kind-mixing → propose a seam OR say "no seam, leaving it" |
| `*.bak.*` left over | verify against the originals, then propose deleting |

**Exit 4 is different: a credential was found in a note.** Do not quietly edit
the file. If the notes are under version control the value is already in
history, and a silent fix hides that from the person who has to rotate it. Say
what was found and where, then let the human decide. Note also what the check
covered — the report says whether an external scanner was available, and a short
generic password in a sentence is caught by nothing.

Never stay silent about size and never defer it — it is the one signal that
otherwise accumulates for years. But never split silently either: propose the
seam, the decision is the human's.

## After a session that moved or renamed anything, run `kb verify`

`check` proves the notes are internally consistent. It says nothing about whether
they are still **true**. The restore half runs `verify` at session start, so the
routine pass is covered — run it here only when THIS session moved, renamed or
deleted something the notes may point at.

```
kb verify     vanished paths, notes past their re-check age; exit 3 = look
```

It reports **suspicions**, not errors. A flagged path may live inside a container
or on another host. Two rules learned the hard way:

- **Confirm the replacement exists before rewriting a path.** A breadcrumb left
  by a human (`MOVED.md` and friends) can itself be wrong. Check the new path
  first, in a step separate from the edit.
- **`verify` only sees paths in backticks.** That filter is what keeps the report
  readable, but it means a stale path inside a fenced block slips through — grep
  for the old string too when fixing one.

## Never

- **Keep a diary.** A `state` file is a snapshot, not "what we did on Tuesday".
- Everything in the shared rules section of `SKILL.md`.

## Report

Counts and paths, not content:

```
kb: +1 decision (04-why-x-target.md), edited 03-traps-and-recipes.md, index synced.
```
