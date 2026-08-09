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

## 4.14.2

- `save` requires the "what would they run" block to hold read-only commands
  only. An assistant told to brief and not to act read one and ran it — harmless
  there, because those commands only read. Somewhere else the same block would
  hold a `terraform apply`. The rule is not "write no commands": the block is
  what makes a note usable. Destructive steps are described in prose, never
  written as a line someone can lift and run.

## 4.14.1

- The drift rule added in 4.12.0 fired on every active day: notes written, a
  release shipped ten minutes later, and the next session opened with a
  suspicion nobody could act on — the false-positive ratio this project refuses
  to ship, found by a reader who said as much. It now compares the newest work
  against the newest *note* rather than the snapshot, and only past an hour. The
  claim narrows to what is worth saying: work went on and produced no note.

## 4.14.0

- `restore` begins with `kb brief` and nothing else. It used to open with three
  commands whose answers had to be held together, then a choice of which files
  to read — four chances to skip one, and the one skipped was `verify`, the only
  one that knows whether the notes still describe the work. `brief` does all of
  it deterministically and costs what reading the index and the snapshot costs
  anyway.
- The two halves are named as belonging to different parties: the tool shows the
  notes, the reader already has them, and the assistant's only job is saying
  what follows. Both failures seen this week come from doing one half — a
  retelling with an error in it, or a sentence confirming the output was
  verbatim and nothing more.

## 4.13.0

- `brief` runs `check` and `verify` itself and prints their verdict above the
  notes. Three commands to answer one question is three chances to skip the
  third, and the third is the one that knows whether the notes still describe
  the work — a stale kb must not read like a current one because nobody typed
  the last command.

## 4.12.0

- `verify` reports files in the work stream that are newer than the current
  snapshot. Every other check compares notes with notes — index against front
  matter, links against files, snapshots against each other — so a kb stays
  spotless while describing a state the work left seven releases ago. That is
  the most common drift there is and the only one nothing could see. Found by a
  reader who went and read the log, which nothing had asked him to do.
- Modification times, not git: four of six real work streams here are not
  repositories, and "cannot check" reads as "fine". Measured on the three that
  have a snapshot — one flagged, and it was the real one; the other two, where
  the work stopped before the snapshot was written, stayed quiet. Times are not
  history, a checkout moves them, so this is a suspicion and never a `check`.

## 4.11.3

- The line at the top of `brief` asks for both halves. "Report what it said"
  produced a paraphrase with an error in it — four releases rendered as five
  numbers. "Do not summarise it" produced the opposite failure: the output sat
  in a collapsed block and the assistant answered with one sentence saying the
  output above was verbatim, having read nothing. The display and the
  understanding are done by different parties, so both have to be asked for:
  the notes are shown by the tool, and what they mean for the work now is said
  after them.

## 4.11.2

- `brief` opens by telling whoever relays it not to summarise. `SKILL.md`
  already said a named command is run and reported, and an assistant summarised
  the output anyway — rendering four releases as "four releases (4.7.1, 4.7.2,
  4.8.0, 4.8.1, 4.9.0)", five numbers under the word four, which is the class of
  error the verbatim output exists to prevent. A rule in a file that may not be
  loaded is weaker than a line in the output that certainly is.

## 4.11.1

- `brief` lists the `plan` notes first and says the steps are in them. A
  snapshot answers where things stand; work that is sequenced but not yet done
  lives in a plan, and in a kb of twenty notes a plan listed among the
  references is a plan nobody opens. Tried on a real one: the two plans, one of
  them the working plan for the whole migration, sat eleventh and fourteenth in
  an undifferentiated list.
- They are named, not printed: one of those files is nineteen thousand tokens,
  several times the whole briefing.

## 4.11.0

- `kb brief` — the overview and the current snapshot printed verbatim, plus why
  that snapshot is the current one and a list of every other note by the question
  it answers. No model in the loop: the same files produce the same bytes.
  `restore` is a briefing — selective by design, phrased by whoever writes it —
  which is the wrong shape for "show me what the notes say", the question asked
  when work resumes after days away.
- `status` and `brief` say why a snapshot is current instead of only naming it.
  The rule is the latest date in a filename, ties broken by note number; with
  three snapshots on one day the date column shows the same value three times
  and the answer reads as arbitrary unless the tie-break is printed with it.

## 4.10.1

- The rule about stale numbers did not cover the place they do most harm: the
  block that says what to expect from a command. "Run this, expect 62 tests"
  invalidates itself on the next test written, and it is read as current by the
  one person looking at the number and the command together. `save` now asks for
  the shape of a good result — `OK`, `clean`, an empty output — not its size.

## 4.10.0

- `release.sh check` refuses to call a release ready when a shipped file names
  something that exists only here: a path into this checkout, a script of ours
  that is never installed, a version out of this changelog. Four times a local
  detail has reached a file written for other people, and every one was found by
  a reader rather than by the release.
- Not a word list — the test is whether the thing named exists here and ships.
  Verified against the text that leaked: two findings, and the current files
  come back clean. Two rules of its own were wrong on the first run: a bare
  `tests` matched the English word in prose, and a word-boundary pattern missed
  `./release.sh`, which is how the leak was actually written.

## 4.9.2

- The rule added in 4.9.1 illustrated itself with this repository's own release
  script and a version number from its changelog. `references/save.md` ships to
  every user in three assistants; none of them has that script. The rule stands,
  the example no longer names anything that exists only here.

## 4.9.1

- `save` says a number a command can print belongs beside that command, and
  never in a title. A version, a file count, a replica count: true when typed,
  and nothing tells the reader when it stops being true. "Released 4.8.1" was
  wrong twenty minutes later — found by a reader in another harness, from a
  title the index shows to someone who opens nothing.

## 4.9.0

- `kb add` refuses a title another note already carries, and `check` reports the
  ones written before that. The title IS the index row and that column answers
  "what do I need?" — answered twice identically it answers nothing. Three
  snapshots taken in one day looked exactly like that: same title, same date in
  the name, told apart only by a number that means nothing to a reader.
- Refused at creation rather than reported later: at that moment the writer
  knows what distinguishes the two, and ten notes later nobody does. Measured
  over 43 real notes in six directories — one group flagged, and it was real.

## 4.8.1

- With no assistant installed, `check` said "installed copies: 0, all at 4.8.0"
  — a check that compared nothing, worded as one that passed. It now says
  nothing was there to compare. A fresh clone is the normal case for that.

## 4.8.0

- `release.sh check` compares every installed copy on the machine against the
  source — the three assistant directories, plus anything named in `KB_MIRRORS`.
  A copy that is behind is a copy that will be read: a config canon holding its
  own mirror of the skill sat two releases behind twice in one evening, and both
  times a reader found it a day later, not the release.
- Machine-specific paths go in `.release.local`, which is not tracked. A public
  repository has no business knowing where anyone keeps their config.

## 4.7.2

- `*.bak.*` is ignored. `install.sh` and any hand edit of a live file leave
  timestamped copies; untracked, they hide the one thing `git status` is for —
  a change nobody meant to make. An outside reader found exactly that: a stray
  `install.sh.bak.*` against a snapshot promising an empty `git status`.

## 4.7.1

- `install.sh` backs up an overwritten file only when its content is NOT in the
  source repository. A backup of something `git checkout` can produce is worth
  nothing: two days of releases left 172 of them across three assistants, every
  one byte-identical to a tagged version, burying the four files actually
  installed. A hand edit — the one thing git cannot give back — is still copied
  aside, and the message says which case it was.

## 4.7.0

- `verify` reports the topics written after the current `state`. The snapshot
  never saw them, and it is what `restore` reads as "the situation now" — a
  briefing built from a file that predates the work reads as current and is not.
  Numbers are exact where dates are not: this happens inside one day and
  `updated` counts days, so every date variant of the rule was measured and
  found nothing.
- In `verify` and never in `check`: the snapshot may well still hold, and only
  the reader can say. Measured over the three real kbs that have a `state`: 3
  flags, one of them a snapshot that claimed there were no tests while
  `07-tests.md` sat next to it.

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
