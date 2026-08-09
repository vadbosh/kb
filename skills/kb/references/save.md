# Writing to the notes

Triggered by "kbsave", "запиши в kb", "задокументируй это", or the end of a task
worth remembering. `SKILL.md` has the tool contract; everything else is here.

Nothing durable — no findings, no decisions, no traps → say
`Nothing durable for kb.` Do NOT create empty notes.

**"Already saved earlier in this session" is not that case until you have looked.**
A note written an hour ago may have been moved, renamed or deleted since, and the
conversation will not know. Check the file is still there before skipping on those
grounds — and if it is gone, this save is not a repeat, it is the only copy.

## The five kinds

Does a newer file **replace** this one, or is it **edited in place**?

| kind | holds | ages by |
|---|---|---|
| `state` | a snapshot on a date: what is done, what is open | superseded by a later date |
| `plan` | what is planned, in what order | superseded when executed |
| `decision` | a choice and **why**; alternatives rejected | never — `--supersedes` only |
| `reference` | how something works; durable | edited in place |
| `recipe` | traps and ready-to-run checks | edited in place |

`state` needs a date in its filename; `kb add state --kind state` adds today's.
Which one is current is **computed**, and earlier ones are marked rather than
deleted — each still describes its own date truthfully.

A `decision` is never rewritten. Reversing one means a new `decision` that
supersedes it: the reasoning behind the old choice is usually what someone needs
six months later. `supersedes:` covers deletion too — name the deleted file
there and `check` reads a later mention of it as history, not a broken link.

That field is what marks both index rows: `decision ⤺ 01` on the replacing note,
`⤺ (reversed by 03)` on the replaced one. Leave it out and the two read as
equals, which is how someone acts on a reversed decision.

## Rules for everything below

- **Run only the commands a step names.** Nothing extra, however informative it
  might be. `kb list` prints every notes directory on the machine; called during
  a save it buries the two or three the question is about under everything else.
  Whether a stream has a kb is `ls -d <dir>/kb`, per stream, and nothing wider.
- **Write in the language the notes are written in**, not this file's. Titles and
  bodies land in a document a human reads.
- **No credentials.** Reference the mechanism (a secret in the cluster, an env
  var), never the value.
- **Nothing that lives elsewhere** — reference it by path or URL. A copy goes
  stale silently, a link does not. Documentation next to code included: it is
  edited together with the code.

## Step 1 — which work streams did this session touch?

A stream is a body of work with its own directory. A long session often has
several, and every other kb command answers for one directory — so reaching for
`kb status` first silently decides the session had one subject.

**Do not enumerate from memory.** Recall returns whatever is most recent and
reads as complete either way; after a compaction it provably is not, and nothing
from the inside tells the two apart. Ask the transcript:

```
kb streams                directories mentioned, commonest first
kb streams --sessions 3   when the work spans more than the current one
```

It extracts **paths**, not prose — a tenth of the cost, and the question is
which directories anyway. No transcript found → it says so, and the list is
yours to give, with the fact that it came from memory said out loud.

Work with no directory — a web console, a mailbox rule, a remote host — leaves
nothing to extract. The tail of pathless messages is a hint, not a second list.

Better than any of this: **save at the boundary**, one stream at a time, while
the context is whole. Then there is never more than one.

- **One stream with a kb already** → write it. Do not turn a routine save into a
  questionnaire.
- **Several** → list and ask. Enumerating is your job; choosing is not.
- **No kb yet** → create it **where the session is running**, and say so in the
  report. `./kb` is the answer; the directory was chosen when the session was
  started there.

Do not deliberate about this. The subject of the work does not decide where its
notes live — the working directory does, and reasoning past that is how notes
end up somewhere nobody will look. `kb` will not create one outside cwd anyway.

The one case that needs a question: **cwd itself is refused** — `$HOME`, a
directory on `PATH`, a system root. Then there is genuinely nowhere, and the
human picks. Name what you would use and wait.

Use the harness's own multiple-choice prompt where there is one (`AskUserQuestion`
with `multiSelect` in Claude Code), otherwise a numbered list. **One line per
stream** — what came out of it, and whether its kb exists:

```
1. ~/src/api      auth rewritten, two bugs fixed   → kb/ exists
2. ~/src/deploy   rollout script + smoke test      → kb/ (new)
3. workstation    editor and shell config          → no home yet
```

Do not argue the case for each — a paragraph per stream turns a two-second
choice into a wall of text. Save the reasoning for whichever they pick.

A stream may be skipped; it may not vanish unmentioned. **"It is in the git
history" is the excuse to distrust most** — a log says what changed, not *what
do I need*. Reasoning worth finding later belongs in a `decision`, with the
commit named as a pointer.

## Step 2 — append or new file

`kb status` first, to see what exists.

**Append** when the fact is one more instance of what a file already covers —
another trap in a `recipe`, another component in a `reference`. Edit it, bump
`updated:`, `kb sync`.

**New file** when any of these holds:

- it answers a different question than every existing file — literally what the
  index column asks: *what do I need?*
- it is a `state` or a `decision`; those are points in time, never appended to
- the obvious host would end up covering two `kind`s at once

**Splitting** — never by size alone; a long coherent `reference` is a good file.
The criterion is mixed kinds. Judge from the heading map, do not read the file:

```
kb outline <file>     sections with weights; no argument = every file over 400 lines
```

Cut only where one part describes **how things are** and another **what to do**,
or a `recipe` has grown inside a `state`. Every section answering the same
question → leave it, however long, and say so.

## Step 3 — write the title

`--title` becomes the index row, and that column answers **"what do I need?"**,
not "what is this called":

```
good   what is done and what is still open right now
good   traps and ready-to-run verification commands
bad    State as of 2026-08-05      (repeats the filename)
bad    Fluent-bit                  (a noun, answers nothing)
```

## Step 4 — write the body

`kb add` creates the file with front matter and an `# H1`; you fill the body.
Lead with the concrete subject. Written text, not a transcript.

**Run a command before writing a claim about the system** — now, not from memory
of a run earlier in the session. `check` and `verify` cannot help: they prove the
notes agree with each other, never that a sentence about the world is true, and a
false note is read with the same confidence as the rest. Two to watch:

- a `grep` matching inside a comment reads as "the code uses it" — re-run against
  executable lines only
- an assertion that happens to be true is still unverified; next time it is not

Not checkable from here — a live cluster, another host, a stopped service? **Say
so in the note.** "Probably X, not verifiable from this machine" is durable; a
confident X is a trap.

**A `decision` needs one step more: search for an existing answer first.**
Another tool or project may have solved it already. A decision justified by "this
is impossible" is worth exactly what the search behind it was worth.

## Step 5 — finish with `kb check`, always

Exit 3 means act in the same turn:

| What `check` reported | What to do |
|---|---|
| stale index table | `kb sync` |
| links a missing file | fix the link or restore the file |
| no front matter / unknown kind | add the front matter |
| `updated` is not a date | correct it — a non-date can win the current-snapshot contest |
| whitespace in a filename | rename with hyphens; links to it cannot be verified |
| `*.bak.*` left over | check them against the originals, then propose deleting |
| **file over the size threshold** | `kb outline` → judge by kind-mixing → propose a seam OR say "no seam, leaving it" |

Never stay silent about size and never defer it; never split silently either —
propose the seam, the decision is the human's.

**Exit 4 is different: a credential was found.** Do not quietly edit the file. If
the notes are versioned the value is already in history, and a silent fix hides
that from whoever has to rotate it. Say what was found and where, and what the
scan covered — a short generic password in a sentence is caught by nothing.
Never write a sample credential into a note to test the scan: a correctly
formatted key is a real finding to every tool that later touches the repository,
fake or not.

## Run `kb verify` if this session moved or renamed anything

`check` proves internal consistency, not truth. The restore half runs `verify` at
session start, so the routine pass is covered.

```
kb verify     vanished paths, notes past their re-check age; exit 3 = look
```

It reports **suspicions** — a flagged path may live in a container or on another
host. Two rules learned the hard way:

- **Confirm the replacement exists before rewriting a path.** A breadcrumb left
  by a human can itself be wrong. Check first, in a step separate from the edit.
- **`verify` only sees paths in backticks** — one inside a fenced block slips
  through, so grep for the old string too when fixing one.

## Never

- **Keep a diary.** A `state` is a snapshot, not "what we did on Tuesday".
- **Let a stream vanish.** Skipping is a decision; announce it.

## Report

Counts and paths, not content — one line per stream, **including skipped ones**.
Without those the reader cannot tell whether a subject was considered and
rejected, or never noticed:

```
kb: ~/src/api      +1 decision (04-why-x.md), edited 03-traps.md, synced
kb: ~/src/deploy   nothing written — no kb yet, your call
kb: workstation    skipped, nothing durable
```
