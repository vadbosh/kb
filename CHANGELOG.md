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

## 4.18.0

- **The entry point kept itself up to date with nothing.** `kb add` rebuilt the
  index inside `kb/` and left `AGENTS.md` at the project root naming a snapshot
  that a later save had superseded, with a note count to match. Nothing reported
  it: every staleness check kb had looked inside the notes directory, and this
  file sits outside it. The one copy of those facts a fresh session reads first
  was the one copy allowed to rot.

  `kb sync` now refreshes that block, so `kb add` and therefore every save carry
  it along — the same treatment the index has always had, for the same derived
  facts. Only between the markers, and only when the markers are there: a file
  at the project root that kb did not write is still never touched, by this or
  anything else.

  Drift reaching `check` now means `sync` was not run — front matter edited by
  hand, or the block itself — and it reads as the finding it is, worded like the
  stale index table it mirrors.

- `shipped_leaks()` looked for a path into this checkout with `"$SRC[...]"`,
  which is how an array index is written, so shellcheck read it as one (SC1087,
  its only error-level finding here). It worked by accident — `SRC` is a plain
  string and the brackets stayed literal — and a construct that only works by
  accident is one refactor away from not. Braces, and an unused `base` dropped
  from the same function. The detector was re-exercised against both kinds of
  planted leak, a checkout path and a file that never installs, since a fix
  inside a check that is not re-run on broken input is not a verified fix.
  `install.sh` was validated at the same time and is clean outright.

## 4.17.0

- **`release.sh check` now runs the tool before calling a release agreed.**
  Every check it had compared a record with a record; the unit tests build a
  world per case, one command at a time. Three of the four releases on
  2026-09-13 fixed a defect that needed neither — a directory with a decision
  already taken, or a second command run after a first — and both were found by
  hand, after shipping, on a real directory.

  `smoke()` copies the live kb into `mktemp`, backdates it, makes a repository
  of it and runs the sequence a session actually uses: `route`, `verify`,
  `local`, `route`. It names the two regressions it exists to catch rather than
  reporting a generic failure. Nothing touches the real notes: a copy, a
  redirected registry, and a delete guarded on a path this function created.

  The backdating is the part that earns its keep. The first version of this gate
  **passed** with the 4.16.3 defect deliberately put back, because it copied
  notes written minutes earlier and `verify` only calls work "ahead of the
  notes" past `UNWRITTEN_HOURS`. A fixture in which the condition cannot arise
  is a green run carrying no information. The defect had originally surfaced on
  a stream whose notes were 94 hours old.

- **A `Sequence` class in the tests, one fixture carried through several
  commands.** Same reasoning, the other half of the gate: state has to survive
  from step to step, since that is the only condition under which either defect
  exists. It also pins the finding *clearing* — a pointer and its notes agreeing
  again silences the report, rather than the warning being permanent once seen.

## 4.16.3

- **`verify` counted `route`'s own output as work that had outrun the notes.**
  The two files kb writes are newer than every note by construction, so running
  `route` guaranteed the next `verify` would report them — naming the two files
  it had just created as evidence the work had moved on. Found on a stream that
  is not a git repository, which is where that check matters most: four of six
  live streams here are not repositories, and a check that cannot run reads as a
  check that passed.

  The same lesson as the overview and the link check in 4.15.4: a set assembled
  for one purpose cannot be reused for a second without asking whether the
  members still belong. The entry point is a pointer to the notes rather than
  the work, and it already has two findings of its own — empty slots and the
  context budget — so it is excluded from the one about the work.

## 4.16.2

- **A committed entry point pointing at excluded notes is now reported.** Found
  by running `kb route` on this repository, which is the only place the two
  halves meet: the notes here are deliberately kept out of git and the file
  `route` writes is not, so every clone would have received an `AGENTS.md`
  promising thirteen notes in a directory that is not there.

  Each half is defensible alone — local notes are the right call for a scratch
  stream, a shared entry point is the right call for a repository — and only the
  combination is broken. That is why nothing else would have caught it: no check
  here compares a decision about the notes with a decision about a file outside
  them. `route` now asks git about both and says which way to resolve it, commit
  the notes or exclude the pointer as well. It does not choose.

- The entry point was verified the one way that counts: generated for this
  repository, filled in, then read cold from Codex with the notes directory
  explicitly off limits. It recovered the project, its boundaries, all four check
  commands and the definition of done, including the release gate and the
  requirement to exercise a check against broken input — from `AGENTS.md` alone,
  on a model that had never loaded this skill.

## 4.16.1

- The restore half still described the previous release. 4.16.0 changed what
  `kb brief` prints and what `kb verify` finds, and only the save half was
  updated — so `references/restore.md` listed the index, the snapshot and the
  plans, with no charter among them, and gave no reading for either of the two
  new `verify` findings. The tool was right and the instructions beside it were
  a version behind, which is the arrangement most likely to be believed.

  Three edits, all of them saying what the output already contains: the charter
  is printed in full and **before** the snapshot, because a list of what is done
  means nothing to a reader who does not yet know what the work is for; the
  briefing template gains a "what this is" line, omitted rather than inferred
  when there is no charter; and the two entry-point findings — empty `kb:fill`
  slots, the 200-line budget — are marked as relay-only, since the answers
  belong to the human and the prose that overruns is theirs.

## 4.16.0

- **`charter`, a sixth kind.** A `state` says where the work stands and a `plan`
  says what comes next. Neither says what the work is *for*, where its boundaries
  are, or what is deliberately not being built — so a direction rejected months
  ago gets proposed again by whoever arrives next, and the reasoning has to be
  rebuilt from memory every time. One per kb: `add` refuses a second, because two
  charters split the answer to "what are we building" and, unlike two snapshots,
  carry no date to pick a winner by. `check` reports a pair written by hand.
  Printed by `brief` *before* the snapshot, on the grounds that a list of what is
  done and open means nothing to a reader who does not yet know what it is for.
  Re-check age 365 days — direction is meant to outlive a release, and flagging
  it sooner would train the reader to skip the whole report.

- **`kb route` — an entry point at the project root.** Everything in this tool
  assumed somebody would run `kb brief`. Nobody who does not already know the
  notes exist ever does, which made a kb invisible to exactly the reader who
  needs it most: a fresh session, another assistant, a new person. What every
  agent does read is the file at the root of the repository.

  Two files, one source. Claude Code reads `CLAUDE.md` and *not* `AGENTS.md`
  (verified against Anthropic's own memory documentation, which contradicts the
  common claim that it reads both); Codex and Opencode read `AGENTS.md`. So the
  content lives in `AGENTS.md` and `CLAUDE.md` holds one line, `@AGENTS.md` —
  the pattern Anthropic documents for this case. Detecting which assistant is
  running and writing only its file was considered and dropped: it breaks on the
  move that makes the feature worth having, which is starting in one tool and
  continuing in another. A symlink was dropped for needing Administrator or
  Developer Mode on Windows, where this ships an installer.

  Only what kb can derive goes between the markers. Check commands and the
  definition of done sit outside them, because kb does not know them and a
  placeholder inside the block would be erased on the next run. An existing
  `AGENTS.md` with no markers is refused rather than rewritten; an existing
  `CLAUDE.md` is never edited, only told what line to add. Those placeholders
  are now a `verify` finding too: `route` names them in the turn that wrote the
  file and nobody sees that message again, so an entry point promising an agent
  a way to check its work and holding a comment instead would rot in silence.

  `/kb save` runs it unasked in the one case where nothing can be damaged — the
  kb was created this turn and the project root has no `AGENTS.md`. Elsewhere it
  is offered, because that file belongs to somebody. The condition is announced
  by `kb add` in its own output rather than asked for in the skill's prose: four
  rewrites of an instruction in this repository produced four different failures,
  and a line in output the caller already reads does not have that problem.

- **A context budget on that entry point, advisory both ways.** Note thresholds
  are generous on purpose: a note is read when someone opens it, so length costs
  nothing until then. This file is the opposite — expanded into the context
  window at every session start and paid for on every request — so the 200-line
  rule for always-loaded instruction files applies to it, measured as the sum of
  both files, since the import brings one in alongside the other. `route` and
  `verify` report the overrun. Neither trims: what overruns is prose a human
  wrote, and silently shortening it is the edit this tool refuses everywhere
  else. Counted with `splitlines()` rather than the note counter's
  `count("\n") + 1`, which overstates a newline-terminated file by one — nobody
  notices that at a 400-line advisory and everybody would at 200.

- **`kb local`, and the question that precedes it.** Notes created inside a git
  repository are committed by default, and nobody chooses that — `git add -A`
  does. Scaffolding a kb now says so once, at the only moment the question can
  arise, and `kb local` writes `.git/info/exclude`. Not `.gitignore`: that file
  is itself committed, so it imposes one person's choice on everyone who clones.
  Nothing is stored about the answer — `kb status` asks git, because a stored
  flag is a second copy of a fact git already owns and the two part company at
  the first edit of an ignore rule. Refused once the notes are tracked, where an
  exclude rule would report success and change nothing.

## 4.15.4

- A note could not cite the overview. `load_notes()` skips `00-overview.md` on
  purpose — it has no kind and belongs in no generated table — and the same set
  was doing double duty as "files that exist" for the link check. So a note
  writing `` `00-overview.md` `` was told it links a missing file, and the file
  in question is the one `check` separately insists must be present and filled
  in. Found while writing a state note that pointed a reader at the map.

  The fix is one term: the overview joins `known`. Nothing else moves — the
  generated table still comes from notes alone, and a name listed in
  `supersedes:` is still history rather than a broken link. Two cases added: a
  note citing the overview, and the overview citing itself, both of which fail
  on the previous version.

## 4.15.3

- A title written the way strict YAML requires kept its quotes. The block is not
  YAML and never was — `---` fences and a split on the first colon — but it
  looks like one, so a value containing `": "` gets quoted by whoever edits it by
  hand, and the pair travelled verbatim into the index row. That row is what a
  reader sees before opening any file, and nothing in `check` reads the first
  character of a title, so the table was the only place it showed. Found while
  writing a `recipe` whose title had a colon in it. One pair of surrounding
  quotes is now dropped at parse time; quotes anywhere else in the line are left
  alone, and `kb add` still writes the value unquoted.

## 4.15.2

- Two facts in the documentation had gone stale over a day of releases, in all
  six files at once. The installer no longer copies aside every file it
  replaces — only content the repository does not already hold — and `verify`
  has a third finding, work that outran the notes. Both now say so, in both
  languages.

## 4.15.1

- Removing the note-numbering rule left `current_state` computed in `verify` and
  never used — the kind of leftover that has the next reader looking for the
  purpose of a line that has none. Gone, and the one case the drift check cannot
  answer is now named where it is skipped: a flat layout, where the notes and
  the work are the same files.

## 4.15.0

- The rule from 4.7.0 — notes numbered above the current snapshot — is gone. It
  fired on all three real kbs that have a snapshot, because an ordinary save
  writes a note and is not required to write a new `state`: the flag lit after
  every save. One true finding in its life, a snapshot claiming there were no
  tests with `07-tests.md` beside it, against a permanent glow.
- What remains says the same thing more directly: work went on and no note was
  written. It looks at the work rather than at the numbering of notes, and it
  measured quiet on the kbs where the notes are current.

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
