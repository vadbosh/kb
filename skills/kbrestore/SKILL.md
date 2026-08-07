---
name: kbrestore
description: Handle phrases "kbrestore", "/kbrestore", "прочитай kb", "прочитай заметки", "восстанови контекст из kb", "read kb", "что в заметках" by loading the project's kb/ work-notes into the session — index first, current state snapshot, then only the files the task needs. Use at the start of a session, when resuming an old one, or whenever the user wants orientation in a project that has a kb/ directory.
version: "1.0.0"
---

# kbrestore

Load `kb/` work-notes into the session. Counterpart of `kbsave`.

## Tool

`kb` CLI at `~/.local/bin/kb`, then the Read tool for the files themselves.

```bash
kb status    # where the kb is, how many files, WHICH SNAPSHOT IS CURRENT
kb check     # index vs files; exit 3 = drift
```

Resolve from cwd (`./kb`). Not the project dir → `--dir <path>`.

No `kb/` under cwd → check the registry before concluding there are no notes:

```bash
kb list            # every known kb: path, file count, current snapshot
```

Still nothing → say so plainly, do not invent notes.

## Step 1 — orient before reading

```bash
kb status && kb check && kb verify
```

All three, always — this is the one moment in the workflow where they are cheap
and where their answers matter. `verify` in particular has no other natural
home: it must not run on every save (noise), and leaving it to "run it when it
feels right" means it never runs at all.

`kb status` names the current `state` file. That is the answer to "what is the
situation now" — every older `state` describes its own date and is not cancelled.

`kb check` exit 3 means the index disagrees with the files. Report it, and say
`kb sync` fixes it — do not silently trust a stale index.

`kb verify` exit 3 is different: suspicions, not errors. A flagged path may live
inside a container or on another host. Surface what it found in the briefing's
Discrepancies section; do not fix anything unasked, and never rewrite a path
without first confirming the replacement exists.

## Step 2 — read the index, then be selective

Read `kb/00-overview.md` in full. It is small and it is the map: the prose says
what the work stream is and what is deliberately NOT in it, and the generated
table has one row per file with the question that file answers.

Then read:

- the **current `state`** file — always, that is the situation now
- **only the files the task needs**, chosen by the index's "what do I need"
  column

Do not read every file. That column exists precisely so you don't have to.

## Step 3 — resuming an old session (`claude -r` / `-c`)

The conversation is restored, but the files may have moved on — another session
wrote to them, the human edited them, or compaction dropped the details.

Compare what `kb status` reports **now** against what the restored conversation
shows:

- **current `state` file is the same, `check` clean** → context is still valid,
  re-read nothing, say so.
- **a newer `state` file appeared** → read it; the situation changed since this
  conversation last looked.
- **`check` reports drift** → the notes were edited without a sync; read the
  changed files rather than trusting the table.

State this comparison explicitly in the briefing — that is the whole value of
running this on resume rather than assuming the context is fresh.

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
<only if kb check exited 3, or the snapshot changed since last time>
```

Render the headings **in the language the user writes in** — this is shown to a
human, not to the tool.

Skip any section with nothing in it. Everything empty → say the kb is empty,
don't pad.

## Never

- **Dump the files raw** — synthesize. The user can open them.
- **Read all files "just in case"** — the index column tells you which one.
- **Treat an older `state` as current** — `kb status` already computed which one
  is current; use its answer.
- **Write anything here.** Creating or editing notes is `kbsave`.
- **Auto-execute** what the notes describe. Briefing only.

## End with

A one-line reminder, in the user's language, that `kbsave` at the end of the
work records what was learned.
