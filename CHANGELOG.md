# Changelog

Versions are the `version:` field in `skills/kb/SKILL.md`, and each is tagged at
the commit that introduced it. Breaking means a command that used to work now
refuses.

Releasing, in one commit: bump `version:`, add the section here, commit, then
`./release.sh tag` and `git push --tags origin`. The tag carries this file's
section for that version, so `git tag -n99 v4.1.0` answers "what changed"
without leaving git.

A tag is not edited afterwards: `git tag -f` recreates it, and for one already
pushed that means a force-push while anyone who fetched keeps the old. Anything
that needs correcting later belongs here, where it can be.

`./release.sh check` verifies the three agree — the field that ships, the section
a reader looks at, and the tag `git checkout` needs. They drift independently,
and a release where they disagree is worse than an untagged one: each source
looks authoritative, and nothing says which is right.

## 4.6.1

- Two sections in `save.md` were numbered as steps they were not: "Step 2 —
  append or new file" and "Step 3 — write the title" both explain how to carry
  out step 3. They are now "Inside step 3 — …". A pointer that misroutes is the
  defect this project exists to prevent; it had one of its own.

## 4.6.0

- `save` gets a fifth step: grep the subject of what changed across the whole kb
  before `check`. A note is written true and goes false when the world moves, and
  nothing in the tool can see that — `check` compares notes with each other,
  never a sentence with the world. The case: tests were added, a note about them
  written, the `state` updated, and a third note kept saying "there are no tests"
  — in the file the index recommends for "I am about to change the code".
- Automating the judgement was measured and refused: an absence-phrase check
  fired 20 times over 34 real notes, effectively none of them stale prose.

## 4.5.0

- `tests/test_kb.py` — 59 tests, standard library only, each run in a temporary
  directory with its own `HOME` and `KB_REGISTRY`. They cover the guards and the
  bugs that shipped once; each regression names its version. Whether a note is
  *useful* stays unchecked, deliberately.
- `--dir` is accepted after the subcommand as well as before it. `kb check --dir
  X` used to exit 2 with `unrecognized arguments` — including the order the
  tool's own error message recommends, `kb init --dir <path>`. Found by the
  tests on their first run.

## 4.4.0

- `kb add` writes headings for the kind: a `decision` gets "what was rejected"
  and "when to revisit", a `reference` gets "where it lives" and "what breaks
  silently". `kind` said when a note expires and never what belongs in it, so
  bodies filled with reasoning and skipped location.
- `check` reports a heading left unanswered. Deleting one is a decision;
  leaving it blank is not.

## 4.3.0

- `save` ends by asking whether someone could *work* from the notes or only
  understand them, and requires anything missing to be named rather than quietly
  left out. Twice an outside reader found the same shape of gap: plenty of
  *why*, nothing about *where*.

## 4.2.0

- `check` reports two things `restore` reads and nothing made `save` write: an
  overview still holding its placeholder, and a kb of three or more notes with
  no `state`. The halves disagreed in silence — a briefing said "the situation
  now" with nothing to take it from.

## 4.1.0

- `release.sh check` compares HEAD against the tag. The three records could
  agree while the tag sat behind, and "agreed" read as "released" — five commits
  of release machinery once sat unreleased under that word.
- Tags carry their changelog section, so `git tag -n99` answers what changed.

## 4.0.2

- A save that finds its earlier note missing writes it again and says so, rather
  than producing a theory about what removed it.

## 4.0.1

- `kb add --dir <fresh directory>` scaffolded nothing and ended in a traceback.
  A `--dir` with no notes in it now behaves like an empty working directory.

## 4.0.0 — breaking

- **kb does not touch a directory you are not standing in.** Every command
  taking `--dir` refuses a path outside the current one, reading included.
  `KB_ALLOW_OUTSIDE=1` restores the sweep for cron jobs that need it.

## 3.2.0

- `save` leads with a five-step procedure; the prose behind it is demoted to
  reasons, read when a step is ambiguous.

## 3.1.1

- The check for an existing note is two `ls` in the stream's own directory.
  Not a filesystem search.

## 3.1.0

- `kb streams` reads only sessions bound to the current directory. It used to
  take the newest transcript on the machine, which meant reporting another
  project's work.
- Default rose to five sessions per source.

## 3.0.1

- The rule against concluding "nothing to save" from memory is stated in
  `SKILL.md` as well, since harnesses differ on whether they load a skill's
  reference files.

## 3.0.0 — breaking

- Writing is confined to the working directory: `add`, `sync`, `adopt`, `hook`
  refuse a `--dir` outside it.

## 2.9.0

- `$HOME`, any directory on `PATH` and the system roots are refused as places to
  scaffold notes.
- Restored: with no kb anywhere, creating one is not decided silently.

## 2.8.0

- The five kinds and the writing rules move from `SKILL.md` into
  `references/save.md`. `/kb check` costs 30% less, `/kb restore` 19%.

## 2.7.0

- `adopt` verifies each backup against the file it guards, then removes it.
  `--keep-backups` restores the old behaviour.

## 2.6.0

- `kb streams` — which directories a session touched, read from the harness's
  own transcript rather than from recall. Handles Claude Code, Codex and
  Opencode without external helpers.

## 2.5.0

- The work-stream list comes from the transcript, not from memory of the
  session.

## 2.4.0

- A claim about the system gets a command before it gets written; a `decision`
  gets a search for an existing answer first.

## 2.3.0

- One session often touches several work streams. `save` enumerates them and
  asks which to write, instead of assuming the directory it happens to be in.

## 2.2.0

- `supersedes:` marks both index rows — `decision ⤺ 01` on the replacing note,
  `⤺ (reversed by 03)` on the replaced one.

## 2.1.0

- `check` follows links between notes, not only from the overview.
- `supersedes:` earns a job: a name declared superseded is history, not a broken
  link.
- `adopt` registers the directory it retrofits; `list --prune` stops printing a
  hint that repeats the command being run.

## 2.0.0

- The two skills merge into one directory and the CLI ships inside it — nothing
  depends on `PATH` or on `~/.local/bin`, which does not exist on Windows.
