---
name: kb
description: Read and write a project's kb/ work-notes — a Markdown knowledge base whose index is generated rather than maintained by hand. Handles phrases "kbsave", "kbrestore", "/kb", "запиши в kb", "запиши в заметки", "прочитай kb", "прочитай заметки", "восстанови контекст из kb", "save to kb", "read kb", "что в заметках", "задокументируй это", "оформи в kb". Use at the start of work to load the notes and see what changed, and at the end to persist findings, decisions, traps or a dated snapshot instead of leaving them in the conversation.
version: "2.0.0"
---

# kb

A Markdown knowledge base per work stream: one `00-overview.md` acting as a map,
plus numbered topic files. The index table is **generated** from each file's
front matter, so it cannot drift from the files it describes.

## Which half do you need

| The user wants | Read |
|---|---|
| to load the notes, orient, see what changed — "kbrestore", "прочитай kb", start of a session | `references/restore.md` |
| to write down what was learned — "kbsave", "запиши в kb", end of a task | `references/save.md` |

Read only the one that applies. They share the rules below and nothing else.

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
kb check                                      mechanical drift; exit 3 if any
kb verify                                     advisory: dead paths, stale notes
kb sync                                       rebuild the index table
kb add <slug> --kind <kind> --title "<...>"   new note + front matter + reindex
kb outline [file]                             section map — where the seams are
kb list                                       every kb known on this machine
```

Resolve the notes directory from cwd (`./kb`). Not the project dir →
`--dir <path>`. No `kb/` yet → `kb add` creates it, no `init` needed.

## The five kinds

The distinction that earns its keep: does a newer file **replace** this one, or
is the file **edited in place**?

| kind | holds | ages by |
|---|---|---|
| `state` | a snapshot on a date: what is done, what is open | superseded by a later date |
| `plan` | what is planned, in what order | superseded when executed |
| `decision` | a choice and **why**; alternatives rejected | never expires — `--supersedes` only |
| `reference` | how something works; durable | edited in place |
| `recipe` | traps and ready-to-run checks | edited in place |

`state` needs a date in its filename; `kb add state --kind state` adds today's.
Which snapshot is current is **computed** — the tool marks the earlier ones
rather than deleting them, because they still describe their own date truthfully.

A `decision` is never rewritten. Reversing one means a new `decision` that
supersedes it; the reasoning behind the old choice is usually the thing someone
needs six months later.

## Rules for both halves

- **Never edit between `<!-- kb:begin -->` and `<!-- kb:end -->`.** That table is
  generated; the next `kb sync` overwrites it. Change front matter instead.
- **Never rewrite text outside the markers** unless asked — a human wrote that
  wording.
- **Write in the language the notes are written in**, not the language of this
  skill. Titles and bodies go straight into a document a human reads.
- **No credentials.** Reference the mechanism (a secret in the cluster, an env
  var), never the value.
- **Nothing that lives elsewhere.** Reference it by path or URL — a copy goes
  stale silently, a link does not. That includes documentation kept next to the
  code, which must be edited together with the code.
