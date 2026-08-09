# Loading the notes into the session

Triggered by "kbrestore", "прочитай kb", "что в заметках", or the start of work
in a project that has a `kb/`. `SKILL.md` has the tool contract.

The index shows a `kind` per row. It says how that note ages, and reading only
needs the consequence: a `state` is true for its date and the current one is
computed for you; everything else is maintained in place. The full table lives
in `references/save.md`, where the choice is actually made.

Reading the files themselves is the Read tool, not the CLI.

**Run only the commands a step names** — nothing extra, however informative. A
briefing padded with output nobody asked for costs tokens and hides the answer.

## Step 1 — orient before reading

```
kb status && kb check && kb verify
```

All three, always — this is the one moment where they are cheap and their answers
matter. `verify` has no other natural home: on every save it is noise, and left
to judgement it never runs.

`kb status` names the current `state`; older ones describe their own date and are
not cancelled. `kb check` exit 3 means the index disagrees with the files — say
`kb sync` fixes it, never trust a stale index silently. `kb verify` exit 3 is
suspicions, not errors: a flagged path may live in a container or on another
host. Surface those under Discrepancies, fix nothing unasked, and never rewrite a
path without first confirming the replacement exists.

No `kb/` under cwd → run `kb list` before concluding there are no notes; the
project's kb may be registered elsewhere. Still nothing → say so plainly, do not
invent notes.

## Step 2 — read the index, then be selective

Read `kb/00-overview.md` in full — it is small and it is the map: prose saying
what the stream is and what is deliberately NOT in it, plus one table row per
file with the question that file answers.

Then the **current `state`** (always — that is the situation now) and **only the
files the task needs**, chosen by the "what do I need" column. That column exists
so you do not read everything. A row marked `⚠ ~Nk tokens` is expensive; open it
only if the task needs it.

## Step 3 — resuming an old session

On `--resume` the conversation comes back, but the files may have moved on:
another session wrote, the human edited, or compaction dropped the details.
Compare what `kb status` reports **now** against what the conversation shows:

- **same current `state`, `check` clean** → the context is still valid, re-read
  nothing, say so.
- **a newer `state` appeared** → read it; the situation changed since this
  conversation last looked.
- **`check` reports drift** → the notes were edited without a sync; read the
  changed files rather than trusting the table.

State this comparison explicitly. That is the whole value of running this on
resume rather than assuming the context is fresh.

## Step 4 — brief

```
## kb: <path>   (<N> files, snapshot <NN-state-YYYY-MM-DD>)

## State
<2-4 lines from the current state file>

## Open
<what is unfinished, from state/plan>

## What to read for this task
- `NN-file.md` — <why this one specifically>

## Discrepancies
<only if check or verify exited 3, or the snapshot changed since last time>
```

Render the headings **in the language the user writes in** — this is shown to a
human, not to the tool.

Skip any section with nothing in it. Everything empty → say the kb is empty,
don't pad.

## When the briefing is the wrong shape

This half is selective and phrased by whoever writes it, so two runs differ in
wording and in which files were opened. That is right for "what should I read
for this task" and wrong for "show me what the notes say" — the question asked
when work resumes after days away, where a paraphrase is exactly what the reader
does not want.

`kb brief` answers that one: the overview and the current snapshot printed
verbatim, why that snapshot is the current one, and a list of everything else by
the question it answers. Same files in, same bytes out. Run it and show the
output; do not summarise what it printed.

## Never

- **Dump the files raw** — synthesize. The user can open them. Asked for the
  files themselves, run `kb brief`, which is that request answered exactly.
- **Read every file "just in case"** — the index column tells you which one.
- **Treat an older `state` as current** — `kb status` already computed which one
  is current; use its answer.
- **Write anything.** Creating or editing notes is the save half.
- **Auto-execute** what the notes describe. Briefing only.

## End with

A one-line reminder, in the user's language, that `/kb save` at the end of the
work records what was learned.
