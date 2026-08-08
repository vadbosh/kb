# Writing to the notes

Triggered by "kbsave", "запиши в kb", "задокументируй это", or the end of a task
worth remembering. Read `SKILL.md` first — the tool contract, the five kinds and
the shared rules live there.

Nothing durable — no findings, no decisions, no traps → say
`Nothing durable for kb.` Do NOT create empty notes.

## Step 1 — which work streams did this session touch?

A stream is a body of work with its own directory or repository. A long session
often has several, and every kb command answers for one directory only — so
reaching for `kb status` first silently decides the session had one subject.

**Do not enumerate them from memory.** Recall returns whatever is most recent
and reads as complete either way, and after the conversation has been compacted
it is provably not — you cannot tell "nothing else happened" from "I no longer
have it". Ask the transcript instead:

```
kb streams              directories this session mentioned, commonest first
kb streams --sessions 3 when the work spans more than the current one
```

It reads the harness's own transcript and extracts **paths**, not prose — a
tenth of the cost, and the question is which directories anyway. When it finds
no transcript it says so; then the list is yours to give, and the fact that it
came from memory is worth saying out loud.

Work with no directory at all — a web console, a mailbox rule, a remote host —
leaves nothing to extract. `kb streams` shows a tail of messages that mention no
path, but that is a hint, not a second list.

Best avoided altogether by **saving at the boundary** — one stream finished,
one save, while the context is still whole. Then there is never more than one.

- **One stream** → write it. Do not turn a routine save into a questionnaire.
- **Several** → list them and ask which to write. Enumerating is your job;
  choosing is not.

Use the harness's own multiple-choice prompt where there is one (`AskUserQuestion`
with `multiSelect` in Claude Code); otherwise print a numbered list and wait.
**One line per stream** — what came out of it, and whether its kb exists:

```
1. ~/src/api      auth rewritten, two bugs fixed   → kb/ exists
2. ~/src/deploy   rollout script + smoke test      → kb/ (new)
3. workstation    editor and shell config          → no home yet
```

Do not argue the case for each one — a paragraph per stream turns a two-second
choice into a wall of text. Save the reasoning for whichever they pick.

A stream may be skipped; it may not vanish unmentioned. **"It is in the git
history" is the excuse to distrust most** — a log says what changed, not *what do
I need*. If the reasoning behind a design is worth finding later it belongs in a
`decision`, with the commit named as a pointer.

## Step 2 — append or new file

Run `kb status` to see what exists.

**Append** when the fact is one more instance of what a file already covers —
another trap in a `recipe`, another component in a `reference`. Edit the file,
bump `updated:`, `kb sync`.

**New file** when any of these holds:

- it answers a different question than every existing file — literally what the
  index column asks: *what do I need?*
- it is a `state` or a `decision`; those are points in time, never appended to
- putting it in the obvious host would make that file cover two `kind`s at once

**Splitting** — never by size alone. A long coherent `reference` is a good file.
The real criterion is mixed kinds. Judge from the heading map, do not read the
file:

```
kb outline <file>     sections with weights; no argument = every file over 400 lines
```

Split only where one part describes **how things are** and another **what to
do**, or a `recipe` has grown inside a `state`. If every section answers the same
question, leave it alone however long — say so and move on.

## Step 3 — write the title

`--title` becomes the index row, and that column answers **"what do I need?"**,
not "what is this document called":

```
good   what is done and what is still open right now
good   traps and ready-to-run verification commands
bad    State as of 2026-08-05      (repeats the filename)
bad    Fluent-bit                  (a noun, answers nothing)
```

## Step 4 — write the body

`kb add` creates the file with front matter and an `# H1`; you fill the body.
Lead with the concrete subject. Written text, not a transcript.

**Run a command before writing a claim about the system** — now, not from
memory of a run earlier in the session. `check` and `verify` cannot help here:
they prove the notes agree with each other, never that a sentence about the
world is true. A false note is worse than no note, being read with the same
confidence as the rest. Two things to watch:

- a `grep` matching inside a comment reads as "the code uses it" — re-run against
  executable lines only
- an assertion that happens to be true is still unverified; next time it is not

Cannot be checked from here — a live cluster, another host, a stopped service?
**Say so in the note.** "Probably X, not verifiable from this machine" is
durable; a confident X is a trap.

**A `decision` needs one step more: search for an existing answer first.**
Another tool or project may have solved the same problem already. A decision
justified by "this is impossible" is worth exactly as much as the search behind
it.

Reversing an earlier decision → `kb add … --kind decision --supersedes <file>`.
Do not rewrite the old one. **Deleting a note a newer one replaces** → same
mechanism: put the deleted name in the replacing note's `supersedes:` and say in
prose what went and why. `check` then reads a later mention of it as history
rather than a broken link.

## Step 5 — finish with `kb check`, always

Exit 3 means something needs attention — act in the same turn:

| What `check` reported | What to do |
|---|---|
| stale index table | `kb sync` |
| links a missing file | fix the link or restore the file |
| no front matter / unknown kind | add the front matter |
| **file over the size threshold** | `kb outline` → judge by kind-mixing → propose a seam OR say "no seam, leaving it" |
| `*.bak.*` left over | verify against the originals, then propose deleting |

Never stay silent about size and never defer it; never split silently either —
propose the seam, the decision is the human's.

**Exit 4 is different: a credential was found.** Do not quietly edit the file. If
the notes are versioned the value is already in history, and a silent fix hides
that from whoever has to rotate it. Say what was found and where, and note what
the scan covered — a short generic password in a sentence is caught by nothing.

Never write a sample credential into a note to test the scan. A correctly
formatted key is a real finding to every tool that touches the repository
afterwards, fake or not.

## Run `kb verify` if this session moved or renamed anything

`check` proves internal consistency and says nothing about whether the notes are
still **true**. The restore half runs `verify` at session start, so the routine
pass is covered.

```
kb verify     vanished paths, notes past their re-check age; exit 3 = look
```

It reports **suspicions**: a flagged path may live in a container or on another
host. Two rules learned the hard way:

- **Confirm the replacement exists before rewriting a path.** A breadcrumb left
  by a human can itself be wrong. Check first, in a step separate from the edit.
- **`verify` only sees paths in backticks** — a stale path inside a fenced block
  slips through, so grep for the old string too when fixing one.

## Never

- **Keep a diary.** A `state` file is a snapshot, not "what we did on Tuesday".
- **Let a stream vanish.** Skipping is a decision; announce it.
- Everything in the shared rules section of `SKILL.md`.

## Report

Counts and paths, not content — one line per stream, including skipped ones.
Without them the reader cannot tell whether a subject was considered and
rejected, or never noticed:

```
kb: ~/src/api      +1 decision (04-why-x.md), edited 03-traps.md, synced
kb: ~/src/deploy   nothing written — no kb yet, your call
kb: workstation    skipped, nothing durable
```
