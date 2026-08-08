# Loading the notes into the session

Triggered by "kbrestore", "прочитай kb", "что в заметках", or the start of work
in a project that has a `kb/`. Read `SKILL.md` first — the tool contract, the
five kinds and the shared rules live there.

Reading the files themselves is the Read tool, not the CLI.

## Step 1 — orient before reading

```
kb status && kb check && kb verify
```

All three, always. This is the one moment in the workflow where they are cheap
and where their answers matter. `verify` in particular has no other natural home:
it must not run on every save (noise), and leaving it to "run it when it feels
right" means it never runs at all.

`kb status` names the current `state` file — the answer to "what is the situation
now". Every older `state` describes its own date and is not cancelled.

`kb check` exit 3 means the index disagrees with the files. Report it and say
`kb sync` fixes it. Do not silently trust a stale index.

`kb verify` exit 3 is different: suspicions, not errors. A flagged path may live
inside a container or on another host. Surface what it found under Discrepancies
in the briefing; fix nothing unasked, and never rewrite a path without first
confirming the replacement exists.

No `kb/` under cwd → run `kb list` before concluding there are no notes; the
project's kb may be registered elsewhere. Still nothing → say so plainly, do not
invent notes.

## Step 2 — read the index, then be selective

Read `kb/00-overview.md` in full. It is small and it is the map: the prose says
what the work stream is and what is deliberately NOT in it, and the generated
table has one row per file with the question that file answers.

Then read:

- the **current `state`** file — always, that is the situation now
- **only the files the task needs**, chosen by the index's "what do I need" column

Do not read every file. That column exists precisely so you don't have to. A file
marked `⚠ ~Nk tokens` in the index is expensive — open it only if the task
actually needs it.

## Step 3 — resuming an old session

On `--resume` / `--continue` the conversation comes back, but the files may have
moved on: another session wrote to them, the human edited them, or compaction
dropped the details.

Compare what `kb status` reports **now** against what the restored conversation
shows:

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

## Never

- **Dump the files raw** — synthesize. The user can open them.
- **Read every file "just in case"** — the index column tells you which one.
- **Treat an older `state` as current** — `kb status` already computed which one
  is current; use its answer.
- **Write anything.** Creating or editing notes is the save half.
- **Auto-execute** what the notes describe. Briefing only.

## End with

A one-line reminder, in the user's language, that saying `kbsave` at the end of
the work records what was learned.
