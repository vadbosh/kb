# Writing to the notes

Triggered by "kbsave", "запиши в kb", "задокументируй это", or the end of a task
worth remembering. Read `SKILL.md` first — the tool contract, the five kinds and
the shared rules live there.

## Skip-if-trivial guard

No findings, no decisions, no traps, nothing that outlives the conversation →
say `Nothing durable for kb.` Do NOT create empty notes.

## Step 1 — how many work streams did this session touch?

**Do this before anything else, and never skip it.** A long session usually
touches several: a tool being built, a bundle being fixed, a machine being
configured. Each is its own work stream with its own directory, and therefore its
own kb. `kb status` answers for ONE directory — reaching for it first quietly
decides that the session had one subject.

1. List the work streams this session actually touched. A stream is a body of
   work with its own directory or repository — not a topic, not a task.
2. Resolve a kb for each: `./kb` in its directory, or `kb list` if it already has
   one elsewhere.

**One stream → just write it.** Do not turn a routine save into a questionnaire.

**Several streams → ask which ones to write.** Enumerating is your job; choosing
is not.

Use the harness's own multiple-choice prompt if it has one — in Claude Code that
is `AskUserQuestion` with `multiSelect`. Where there is none (opencode, Codex),
print a numbered list and wait. Either way the shape is the same: **one line per
stream**, carrying only what a person needs to choose — what came out of it, and
whether a kb for it exists.

```
1. /AI_P/Qdrant   bundle now has a drift check      → kb/ exists
2. /home/kb       6 defects, docs reworked          → kb/ (new)
3. AI tooling     trigger rule, dead command gone   → no home yet
4. gh-traffic     collector + cron                  → in MEMORY.md
```

**Do not argue the case for each stream.** A paragraph per stream turns a
two-second choice into a wall of text; save the reasoning for whichever stream
they pick, or for a question they ask. Then write the chosen ones, steps 2–5 per
stream.

**Never decide this alone, and never let a stream vanish unmentioned.** Writing
one kb and staying quiet about the other three reads as "everything is saved".

"It is in the git history" is the reason that deserves the most suspicion — both
when you offer it and when you accept it. A log records what changed and why it
changed; it does not answer *what do I need*, which is the question the index
column asks. Thirty commits are not a knowledge base. If the reasoning behind a
design is worth finding later, it belongs in a `decision`, with the commit named
as a pointer.

## Step 2 — append or new file

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

## Step 3 — write the title

`--title` becomes the index row, and that column answers **"what do I need?"** —
not "what is this document called". Write from the reader's side:

```
good   what is done and what is still open right now
good   traps and ready-to-run verification commands
bad    State as of 2026-08-05      (repeats the filename)
bad    Fluent-bit                  (a noun, answers nothing)
```

## Step 4 — write the body

`kb add` creates the file with front matter and an `# H1`; you fill the body.
Lead with the concrete subject. Written text, not a transcript — the durable model of
how something works, not the tape of what was typed.

**Every claim about the system gets a command before it gets written.** Not a
recollection of one run earlier in the session — a command, now. `check` and
`verify` cannot help here: they prove the notes are consistent with each other,
never that a sentence about the world is true. A note asserting something false
is worse than no note, because it is read with the same confidence as the rest.

Two failures worth recognising, both real:

- *An assertion nobody checked, which happened to be true.* "It was not in cron
  either" — written without opening cron. Correct by luck. Next time it is not.
- *A grep that matched a comment.* `grep output collect.sh` finds the word in
  `# ships to $output` and reads as "the code uses it". Re-run against the
  executable lines: `grep -v '^\s*#' <file> | grep <term>`.

If a claim cannot be checked from here — a fact about a live cluster, another
host, a service that is not running — **say that in the note**. "Probably X,
could not verify from this machine" is durable. A confident X is a trap.

**A `decision` needs one more step: look for an existing answer first.** This
machine has other tools, other installers, other projects; one of them may have
solved the same problem already. Search before you reason. A decision justified
by "this is impossible" is only as good as the search behind it — and the search
is usually the part that was skipped.

Reversing an earlier decision → `kb add … --kind decision --supersedes <file>`.
Do not rewrite the old one.

**Deleting a note that a newer one replaces → record it the same way.** Put the
deleted name in the replacing note's `supersedes:`, then say in the prose what
went and why. `check` treats a name declared superseded as history rather than a
broken link, so the record survives without turning into a warning every run.

## Step 5 — finish with `kb check`, always

Exit 3 means something needs attention. Act on it in the same turn rather than
leaving it for the user to notice:

| What `check` reported | What to do |
|---|---|
| stale index table | `kb sync` |
| links a missing file | fix the link or restore the file |
| no front matter / unknown kind | add the front matter |
| **file over the size threshold** | `kb outline` → judge by kind-mixing → propose a seam OR say "no seam, leaving it" |
| `*.bak.*` left over | verify against the originals, then propose deleting |

Never write a sample credential into a note to see whether the scan catches it.
A correctly formatted key is a real finding to every tool that touches the
repository afterwards, including GitHub's own scanning — fake or not.

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
- **Let a work stream vanish.** Writing one kb and saying nothing about the other
  three reads as "everything is saved". Skipping is a decision; announce it.
- Everything in the shared rules section of `SKILL.md`.

## Report

Counts and paths, not content — **one line per work stream, including the ones
skipped.** The skipped lines are the point: without them the reader cannot tell
whether a subject was considered and rejected, or never noticed at all.

```
kb: /AI_P/Qdrant/kb  — created, +1 reference, +1 decision, index synced
kb: /home/kb         — nothing written: the design decisions from today are in
                       33 commits and nowhere findable; needs a kb, your call
kb: gh-traffic       — skipped, already in MEMORY.md
```
