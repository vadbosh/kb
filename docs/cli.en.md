# kb — the command line on its own

**kb is an ordinary command-line program. No assistant, no IDE, no editor
plugin, no configuration file, no daemon, no network.** The rest of the
documentation shows it driven by an assistant through `/kb save`, because that
is the convenient path. This page is the other one: you, a terminal, and a
directory.

It runs **in any directory, including an empty one**. Nothing has to be prepared
first — the notes directory comes into existence on the first note you write.

```bash
mkdir /tmp/incident && cd /tmp/incident
kb add timeline --kind state --title "what happened, minute by minute"
```

That is the whole setup. There was no project, no repository, no config.

Requires **Python 3.10+** and nothing else.

---

## What gets written, and what the index is built from

The first question once no assistant is involved: what does kb actually put in
there?

**Exactly what you typed on the command line, and not a byte more.** `kb add`
creates a seven-line file: three front-matter fields and an `# ` heading
repeating `--title`. The body is empty:

```console
$ kb add pipeline --kind reference --title "how the log pipeline works"
$ cat kb/01-pipeline.md
---
title: how the log pipeline works
kind: reference
updated: 2026-08-08
---

# how the log pipeline works
```

`title` comes from `--title`, `kind` from `--kind`, `updated` is today. kb
invents nothing else — no prose, no summary, no tags. The content is written by
a human in an editor, or by an assistant when there is one. The tool keeps the
books; it does not write them.

**The index is built from the front matter of every `NN-*.md` — those three
fields and nothing else.** The body is never read, however much of it there is:

```console
$ echo 'a great deal of text in the body' >> kb/01-pipeline.md
$ kb sync
index already current (4 files)          ← the table did not move

$ sed -i 's/^title: .*/title: a different title/' kb/01-pipeline.md
$ kb sync
index rewritten: 4 files                 ← now it did
```

That is where the promise comes from: the index cannot disagree with the files,
because it is derived from them — specifically from the part of them that exists
for exactly this purpose.

**If a file has no front matter at all** — written by hand before kb was in the
picture, say — it does not drop out of the index. kb fills the gap by guessing:
the title from the first `# `, the kind as `reference`. And it says plainly that
it guessed:

```console
$ kb check
2 problem(s):
  - index table is stale — run `kb sync`
  - 05-handmade.md: no front matter (kind/title guessed)
```

The guess works, but only until you correct it: write the fields out and the
file stops being a special case. `kb adopt` does exactly that across a whole
directory — and first renames anything not already in the `NN-slug.md` shape,
since a hand-made directory rarely is. It previews before it writes, and the
backup it takes of each file is verified and removed once the write is confirmed.

---

## Getting to the binary

The CLI ships inside the skill directory, so it works whether or not anything
else is installed:

```
<skills-dir>/kb/scripts/kb        Linux / macOS
<skills-dir>\kb\scripts\kb.cmd    Windows
```

For daily terminal use, put it on `PATH` once:

```bash
./install.sh --with-path          # during install
# or by hand:
ln -s ~/.claude/skills/kb/scripts/kb ~/.local/bin/kb
```

Everything below is written as `kb`; the full path works identically.

---

## From an empty directory to a working knowledge base

Every block below is real output, not an illustration.

**An empty directory has no notes, and kb says so rather than inventing any:**

```console
$ ls -a
$ kb status
kb: no 00-overview.md in ./kb or . — run `kb init` first, or pass --dir
$ echo $?
1
```

**The first note creates everything it needs:**

```console
$ kb add pipeline --kind reference --title "how the log pipeline works"
created /tmp/clidemo/kb/00-overview.md
created /tmp/clidemo/kb/01-pipeline.md
index rewritten: 1 files
```

Two files: the index, and the note. `kb init` exists for scaffolding the index
alone, but it is optional — `kb add` does it when the directory is empty.

**The note is a plain Markdown file with three front-matter fields:**

```console
$ cat kb/01-pipeline.md
---
title: how the log pipeline works
kind: reference
updated: 2026-08-08
---

# how the log pipeline works
```

Write the body with any editor you like. kb never touches it.

```bash
$EDITOR kb/01-pipeline.md
```

**Add the other kinds as the work produces them:**

```console
$ kb add traps --kind recipe --title "traps and the commands that check them"
created /tmp/clidemo/kb/02-traps.md
index rewritten: 2 files

$ kb add state --kind state --title "what is done, what is open"
created /tmp/clidemo/kb/03-state-2026-08-08.md
index rewritten: 3 files
```

A `state` gets today's date into its filename by itself — that is how kb later
computes which snapshot is current.

**See what you have:**

```console
$ kb status
kb root: /tmp/clidemo/kb   files: 3
current state: 03-state-2026-08-08.md (2026-08-08)
  state      1
  reference  1
  recipe     1
```

---

## The one rule when editing by hand

The index table is **generated**. Edit the front matter, then run `kb sync` —
never the table itself.

```console
$ sed -i 's/^title: .*/title: how logs get from the pod to the collector/' kb/01-pipeline.md
$ kb check
1 problem(s):
  - index table is stale — run `kb sync`

secrets: none found — checked with built-in patterns + trufflehog
$ echo $?
3

$ kb sync
index rewritten: 3 files

$ kb check
clean: 3 files, index current
```

That window between editing a file and running `kb sync` is the only moment the
index can be wrong, and `check` is what closes it. Anything outside the
`kb:begin` / `kb:end` markers is yours; kb never rewrites it.

The regenerated table:

```markdown
<!-- kb:begin -->
Current snapshot: `03-state-2026-08-08.md` (2026-08-08).

| what you need                              | file                      | kind      | updated    |
|--------------------------------------------|---------------------------|-----------|------------|
| how logs get from the pod to the collector | `01-pipeline.md`          | reference | 2026-08-08 |
| traps and the commands that check them     | `02-traps.md`             | recipe    | 2026-08-08 |
| what is done, what is open                 | `03-state-2026-08-08.md`  | state     | 2026-08-08 |
<!-- kb:end -->
```

---

## Which directories a session touched

`kb streams` answers a question none of the other commands do: over this
session, which places did the work actually happen in? It reads the harness's
own transcript — Claude Code and Codex keep JSONL files, Opencode a sqlite
store — and pulls out the **directories** mentioned, not the prose.

```console
$ kb streams
  read: claude ×1

   21  ~/src/api
   13  ~/src/deploy
   11  /srv/gateway

  mentioning no path (93) — work with no directory does not appear above at all:
    • have a look at the journal, there may be mysql errors
```

Paths rather than messages on purpose: the question is which directories, and it
costs about a tenth as much to answer that way.

```bash
kb streams                  # the current session
kb streams --sessions 3     # when the work spans several
kb streams --top 20         # more directories
```

Why it exists: after a long session, and especially after the conversation has
been compacted, remembering what was touched returns whatever is most recent and
reads as complete either way. This does not remember; it reads.

Two things it cannot do. Work with **no directory** — a web console, a mailbox
rule, a host you only reached over ssh — leaves nothing to extract; the tail of
pathless messages is a hint, not a second list. And if the harness keeps no
transcript it says so, and the list is yours to give.

---

## Working from somewhere else

`--dir` points at the notes from any working directory, which is what makes kb
usable from a script or a cron job:

```console
$ cd /
$ kb --dir /tmp/clidemo/kb status
kb root: /tmp/clidemo/kb   files: 3
current state: 03-state-2026-08-08.md (2026-08-08)
```

Every kb this machine has seen is remembered, so you do not have to:

```console
$ kb list
  /srv/logging/kb                          3 files, snapshot 2026-08-05
  /srv/gateway/kb                          19 files, snapshot 2026-08-07, ⚠ 1 heavy
  /tmp/clidemo/kb                          3 files, snapshot 2026-08-08
```

```bash
kb list --scan ~/projects   # adopt kbs created before the registry existed
kb list --prune             # forget entries whose directory is gone
```

---

## Command reference

| Command | What it does |
|---|---|
| `kb add <slug> --kind <k> --title "..."` | new note + front matter + reindex; creates `kb/` if absent |
| `kb status` | where the kb is, how many files, which snapshot is current, the largest files |
| `kb check` | mechanical drift and credentials |
| `kb verify` | advisory: vanished paths, notes nobody has revisited |
| `kb sync` | rebuild the index table from front matter |
| `kb outline [file]` | section map with weights; no argument means every file over 400 lines |
| `kb list [--scan DIR] [--prune]` | every kb known on this machine |
| `kb streams [--sessions N]` | directories this session touched, read from the transcript |
| `kb init [--title ...]` | the index skeleton alone |
| `kb adopt [--apply] [--in-place]` | retrofit hand-written notes: numbers unnumbered `.md`, adds front matter, builds the index |
| `kb hook` | install a git pre-commit that refuses a commit holding a credential |

Flags: `--dir <path>` anywhere, `--supersedes <file>` on `add`, `--no-sync` on
`add` to skip the reindex.

### Exit codes

| Code | Meaning | In a script |
|---|---|---|
| 0 | clean | continue |
| 1 | usage error, or no kb where you pointed | fix the invocation |
| 2 | bad arguments | fix the invocation |
| 3 | drift found (`check`) or something suspicious (`verify`) | look, then act |
| 4 | **a credential was found in a note** | stop; do not commit |

Exit 3 from `check` and from `verify` mean different things on purpose. `check`
is mechanical: 3 means there is a defect to fix. `verify` is heuristic: 3 means
something is worth a human glance, and may be perfectly fine.

```bash
kb check || case $? in
  3) echo "drift — run kb sync or read the report" ;;
  4) echo "credential in the notes; not committing"; exit 1 ;;
esac
```

---

## Environment

| Variable | Effect |
|---|---|
| `KB_LANG` | language of the text kb writes **into** the notes: `ru` (default) or `en`. Diagnostics stay English. |
| `KB_REGISTRY` | where the list of known kbs lives; default `~/.local/state/kb/registry.txt` |

```console
$ KB_LANG=en kb add pipeline --kind reference --title "how the log pipeline works"
$ sed -n '/kb:begin/,/kb:end/p' kb/00-overview.md
<!-- kb:begin — generated by `kb sync`, do not edit by hand -->

| what you need | file | kind | updated |
|---|---|---|---|
| how the log pipeline works | `01-pipeline.md` | reference | 2026-08-08 |
```

Set it per project in a shell profile or a direnv file; it only affects text
written from that point on.

---

## Where the CLI actually earns its keep

Two situations, honestly: **a machine doing it without you**, and **no assistant
within reach**. Everything else is more comfortable through `/kb`.

### A scheduled sweep over every knowledge base

Notes about infrastructure fill up with paths — to config directories, to
scripts, to mount points. They rot silently: someone renames a directory and the
note keeps claiming the old one. Nobody opens an assistant to check that. Cron
does:

```cron
0 9 * * 1  kb list | awk '/^ *\// {print $1}' | while read -r d; do kb --dir "$d" verify; done
```

Note the `^ *` — `kb list` indents its output, and an anchor without it matches
nothing. To get mail only when something is actually wrong:

```bash
kb list | awk '/^ *\// {print $1}' | while read -r d; do
  out=$(kb --dir "$d" verify 2>&1) || { echo "── $d"; echo "$out" | grep '✗'; }
done
```

Run against two live knowledge bases, that printed (paths here and below
replaced with neutral ones — the output is real, the directories are not yours):

```
── /srv/gateway/kb
    ✗ /etc/nginx/custom-conf-parts/
    ✗ /etc/nginx/custom-lua-scripts/
```

Four paths cited by a note that no longer exist on this host. They may still
live inside a container — `verify` reports suspicion, not fact — but that is
exactly the list a human should glance at once a week.

### Refusing a commit that carries a credential

`kb check` exits 4 when it finds one, and 4 is the only code worth treating as a
hard stop. Inside a git repository:

```bash
kb hook
```

It will not overwrite a pre-commit hook it did not write; it prints the line to
add by hand instead. In CI, where the notes live in a repository:

```yaml
kb-check:
  script:
    - kb --dir docs/kb check || [ $? -ne 4 ]
```

That lets exit 3 (drift) through while failing the job on a credential. Invert
it if you want stale indexes to fail too.

### A machine where no assistant is installed

kb is one file with no dependencies, so `scp` is the whole install. Working out
at three in the morning why a database stopped answering, you can write the
`recipe` right there, on the host where you found it, instead of carrying it in
your head until morning.

### kb as an output target for other programs

Any script can write a note. That is the part people miss:

```bash
kb add apply-$(date +%s) --kind state \
   --title "what this terraform apply changed" --dir /srv/infra/kb
```

A wrapper around `terraform apply`, a post-incident script, a nightly report —
all of them can deposit into the same knowledge base an assistant later reads.
kb stops being an assistant's notebook and becomes a format other tooling can
target.

### Orientation that costs nothing

`kb status` answers in milliseconds and says which snapshot is current and which
files are heaviest. Sometimes that is all you needed, and starting a session for
it is overkill.

### Colleagues who do not use AI at all

It is Markdown plus one command. Reading a knowledge base requires installing
nothing whatsoever — which is what makes it shareable across a team where not
everyone works the same way.

### What this list deliberately does not include

Writing notes by hand, day to day. Typing `kb add --kind --title` every time you
learn something is work an assistant does better, because the interesting part
is judgement: append or start a new file, which `kind` fits, how to phrase the
title for a reader rather than for yourself. The CLI does not attempt any of
that — see the last section.

---

## What the CLI will not do for you

It does not decide **what** to write, whether a fact belongs in an existing file
or a new one, or which `kind` fits. That is judgement, and it lives in the skill
— which is the argument for driving kb through an assistant when you have one.
Without one, those decisions are yours; the guidance is in
[the manual](kb.en.md).

Nor does it edit note bodies. `kb add` creates the file and the front matter;
what goes underneath is written by a human or an assistant, in an editor.

---

Full manual: [English](kb.en.md) · [Русский](kb.ru.md) ·
[Русская версия этой страницы](cli.ru.md)
