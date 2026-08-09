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

## Step 1 — one command

```
kb brief
```

That is the read. It prints the verdict of `check` and `verify`, the index in
full, the current `state` in full, the plans as their own group, and every other
note as one line saying what it answers. Deterministic — the same files give the
same bytes — and it costs what reading the index and the snapshot costs anyway,
which is what any orientation does first.

Four steps used to stand here: three commands whose answers had to be held
together, then a choice of which files to open. Each was a chance to skip one,
and the one skipped was `verify` — the only one that knows whether these notes
still describe the work.

What its verdict lines mean:

- **check: clean** → the notes agree with each other. Not that they are true.
- **check: disagree** → the detail follows; `kb sync` fixes a stale index. Never
  trust a stale table silently.
- **check: A CREDENTIAL** → report the file and line, edit nothing.
- **verify: suspicions** → the detail follows. A flagged path may live in a
  container or on another host; files newer than the snapshot mean the work
  moved on and the snapshot may be behind. Surface these under Discrepancies,
  fix nothing unasked, and never rewrite a path without confirming the
  replacement exists.

No `kb/` under cwd → `kb brief` says so. Run `kb list` before concluding there
are no notes; the project's kb may be registered elsewhere. Still nothing → say
so plainly, do not invent notes.

## Step 2 — open only what the task needs

`brief` listed every other note with the question it answers. Open the ones this
task needs and no others — that column exists so you do not read everything. A
row marked `⚠ ~Nk tokens` is expensive; open it only if the task needs it.

## Step 3 — resuming an old session

On `--resume` the conversation comes back, but the files may have moved on:
another session wrote, the human edited, or compaction dropped the details.
Compare what `kb brief` reports **now** against what the conversation shows:

- **same current `state`, `check` clean** → the context is still valid, re-read
  nothing, say so.
- **a newer `state` appeared** → read it; the situation changed since this
  conversation last looked.
- **`check` reports drift** → the notes were edited without a sync; read the
  changed files rather than trusting the table.

State this comparison explicitly. That is the whole value of running this on
resume rather than assuming the context is fresh.

## Step 4 — say what it means

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

## The two halves belong to different parties

`kb brief` shows the notes; it is already in front of the reader and does not
need repeating. What it cannot do is say what any of it means for the work in
front of you — that is the only part this half exists for.

So neither half alone is the answer. Retelling the output wastes the reader's
attention on something they can see; saying "the output above is verbatim" and
stopping leaves them with the same files they had and no orientation. Show
nothing twice, and answer the four questions in Step 4.

## Never

- **Retell what `brief` printed** — the reader has it. Say what follows from it.
- **Read every file "just in case"** — the index column tells you which one.
- **Treat an older `state` as current** — `kb status` already computed which one
  is current; use its answer.
- **Write anything.** Creating or editing notes is the save half.
- **Auto-execute** what the notes describe. Briefing only.

## End with

A one-line reminder, in the user's language, that `/kb save` at the end of the
work records what was learned.
