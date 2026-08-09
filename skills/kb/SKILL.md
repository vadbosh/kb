---
name: kb
description: Read and write a project's kb/ work-notes — a Markdown knowledge base whose index is generated rather than maintained by hand. Handles phrases "kbsave", "kbrestore", "/kb", "запиши в kb", "запиши в заметки", "прочитай kb", "прочитай заметки", "восстанови контекст из kb", "save to kb", "read kb", "что в заметках", "задокументируй это", "оформи в kb". Use at the start of work to load the notes and see what changed, and at the end to persist findings, decisions, traps or a dated snapshot instead of leaving them in the conversation.
version: "4.6.0"
---

# kb

A Markdown knowledge base per work stream: one `00-overview.md` acting as a map,
plus numbered topic files. The index table is **generated** from each file's
front matter, so it cannot drift from the files it describes.

## Which branch do you need

| The user wants | Read |
|---|---|
| to load the notes, orient, see what changed — "kbrestore", "прочитай kb", start of a session | `references/restore.md` |
| to write down what was learned — "kbsave", "запиши в kb", end of a task | `references/save.md` |
| **one named command** — `/kb check`, `/kb status`, `/kb list`, `/kb verify`, `/kb outline`, `/kb sync`, `/kb streams` | neither; see below |

Read only the one that applies. Everything each half needs beyond this page is
in that file — the kinds, the writing rules, the briefing format.

**Saving has one rule that holds even if that file never loads: never conclude
there is nothing to save without looking on disk first.** "Nothing new",
"nothing changed since last time", "already saved above" are the same judgement
made from memory, and memory does not know that a note was deleted an hour ago.
A stream with no `kb/` and a session that did work has nothing written down
anywhere — that is the opposite of nothing to save. Looking means `ls` in that
stream's own directory, not a search of the filesystem: a note outside its
`kb/` is not its record.

**A named command is a request for that command, not for a session ritual.** Run
it, report what it said, stop. Do not load a reference file, do not read the
notes, do not save anything. Two exceptions, because the exit code demands an
answer:

- **exit 4 from `check`** — a credential is in a note. Report the file and line;
  do not edit it silently. `references/save.md` says why.
- **exit 3 from `check`** — act on what it lists in the same turn: `kb sync` for a
  stale index, fix or restore a missing link target, add front matter. A size
  finding is an invitation to run `kb outline` and judge, not an order to split.

With no directory named, run it for the current project; `kb list` covers every
known one.

## Tool

The CLI ships **inside this skill** — nothing depends on `PATH` or on
`~/.local/bin`, which does not exist on Windows. Your base directory is given at
the top of this skill; the binary sits in `scripts/` next to this file:

```
"<skill-dir>/scripts/kb" <command>         Linux / macOS
"<skill-dir>\scripts\kb.cmd" <command>     Windows
```

Written as `kb <command>` from here on for readability. If `kb` is also on PATH
(the installer offers that for manual use) either form works.

Requires Python 3.10+ and nothing else.

```
kb status                                     where the kb is, what is in it
kb check                                      drift (exit 3), credentials (exit 4)
kb verify                                     advisory: dead paths, stale notes
kb sync                                       rebuild the index table
kb add <slug> --kind <kind> --title "<...>"   new note + front matter + reindex
kb outline [file]                             section map — where the seams are
kb list                                       every kb known on this machine
kb streams                                    directories this session touched
```

Resolve the notes directory from cwd (`./kb`). Not the project dir →
`--dir <path>`. No `kb/` yet → `kb add` creates it, no `init` needed.

**One kb covers one work stream, and a session often touches several.** Every
other command answers for a single directory, so running one and stopping
silently decides the session had one subject. `kb streams` answers the other
question — which directories came up — by reading the transcript rather than
trusting recall.

## The one rule both halves share

**Never edit between `<!-- kb:begin -->` and `<!-- kb:end -->`.** That table is
generated; the next `kb sync` overwrites it. Change front matter instead.
Everything outside the markers was written by a human — do not rewrite it unless
asked.
