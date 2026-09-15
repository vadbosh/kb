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

## 4.30.0

- **The notes are found from anywhere inside the project.** Discovery looked in
  cwd and nowhere else, so every command run from a subdirectory reported that
  the project had no notes at all — and work happens in a subdirectory far more
  often than in a project root. Noticed when a session standing in `.git` found
  nothing and worked around it by writing "run kb from the project root" into
  the entry point, which is a note about a defect rather than a fix for one.

  `./kb`, then `./.kb`, then the same two in every directory above. The walk is
  bounded, because walking to the filesystem root would adopt a stranger's
  notes: the repository root ends it when there is one, and without a repository
  it stops before `$HOME`, where a kb is refused anyway. A save from a
  subdirectory joins the stream around it instead of starting a second kb down
  there.

  The confinement check called that ancestor "outside cwd" and refused it — the
  one place it was wrong, since nothing was reached across to. It accepts a
  stream cwd is standing inside; a sibling is still refused.

- **The tool stops answering questions it cannot ask.** The refusal on an
  occupied directory opened with "Put the notes in ./.kb instead" — an
  imperative — and it was carried out twice without anybody being asked, against
  a skill rule that says to ask. The git question printed as `note:` and was
  likewise treated as settled. Both now state the situation, list the options
  without preferring one, and say the choice belongs to the person.

  Prose lost to tool output four times in one day. That is recorded in
  `kb/04-llm-failure-modes.md` with the mechanism: the command's words arrive at
  the moment of deciding, the skill's rule was read ten turns earlier.

## 4.29.1

- **A relative `--dir` left the project nameless.** `Path(".kb").parent` is
  `Path(".")` and its name is the empty string, so an overview scaffolded that
  way came out titled `# ` — carrying nothing, in the first line of the first
  file anyone opens. `--dir .kb` is the ordinary way to type the second name
  4.28.0 had just introduced, so the two shipped together and the second broke
  the first. The root is resolved before anything is derived from its parent.

- **A note could carry two `# ` headings.** `--body-file` dropped a body's own
  heading only when it matched the title exactly; any other wording stayed and
  the note had two, with the index showing one. kb writes the title heading
  itself, so the body's is dropped whatever it says — and said out loud, because
  dropping it silently would lose the only thing it carried.

  Both found by a human reading the two files a save produces, on the release
  that introduced them.

## 4.29.0

- **`kb add --body-file <path|->` writes the note in one call.** The body had
  nowhere to go, so every save created the file empty and then overwrote it
  whole: two tool calls where one does. Measured on a real save — sixteen calls
  against a context of about 105 000 tokens, so a round trip costs the entire
  conversation again, while the longest section of `references/save.md` is worth
  roughly 800 tokens. Shortening prose is not where the cost is, and the measured
  numbers are in `kb/16-cost-is-round-trips.md` so the idea stops coming back.

  It also closes a trap that had to be warned about in prose: a file a command
  has just created exists, has never been read, and looks new — and a `Write`
  over it is refused *after* the whole body has been sent.

  With a body the section skeleton is skipped; the headings are the writer's. A
  body that repeats the `# title` heading does not get a second one.

## 4.28.0

- **kb no longer writes into a directory it did not make.** `kb` is an ordinary
  directory name and a project may already have one — source, a mount, a
  placeholder. The old test was "is there an overview here", the answer for such
  a directory is no, and the scaffold went in beside whatever was there.
  Measured on a directory holding two source files, which afterwards held two
  source files and an index. Nothing was overwritten, and that is not the point:
  the directory belonged to somebody and the tool took it without asking.

  Empty counts as taken. A directory somebody made is a placeholder for what
  they are about to put in it, and "it was empty" is not consent.

  The refusal names the alternatives and writes nothing. There is no silent
  fallback to another name either — choosing one is a decision about somebody
  else's directory, and making it quietly is the failure the guard exists to
  stop.

- **A second name, `.kb`, is searched.** A name nobody searches for is not an
  alternative: every later command would need `--dir` and nothing remembers it
  between sessions. Discovery is `./kb`, then `./.kb`, then the flat layout.

  The predicate deciding nested-from-flat was written out ten times as
  `root.name == "kb"`. One copy left unchanged would compute the project as the
  notes directory itself and send the entry point, the exclude rule and the
  work-ahead scan inside it. It is one function now, asked by all ten.

  `kb local` already derived its pattern from the real path, so it excludes
  whichever name is in use, with `AGENTS.md` and `CLAUDE.md` beside it.

## 4.27.0

- **`kb local` covers the file that points at the notes, not just the notes.**
  The notes and their pointer are one decision, and excluding only the notes
  left an `AGENTS.md` the next `git add -A` would commit — promising a clone a
  directory it will never get. The tool then reported that state as a finding,
  which is the worst arrangement of all: it created the mismatch and complained
  about it. Found on a real repository the first time the git branch was
  exercised, by a human who had answered the question correctly.

  Only files kb wrote are touched: an `AGENTS.md` without the markers belongs to
  somebody, and a `CLAUDE.md` holding anything but the import does too. Both are
  left alone and said so.

## 4.26.1

- **The mismatch finding said "committed" about a file that was untracked, in a
  repository with no commits at all.** What the check actually asks is whether
  the pointer is *excluded*, and it is not the same question: a file nobody has
  ever committed is still the file the next `git add -A` will take. Reported on
  a real repository the day the branch was first exercised — the reader was sent
  to undo a commit that did not exist. Both directions now say what git would
  say: not excluded, or tracked.

## 4.26.0

- **The language belongs to the kb, not to the machine.** `KB_LANG` was one
  variable for every directory on the host, so two streams in two languages
  could not coexist and a kb cloned onto a differently configured machine
  changed language under its owner. It is recorded in the `kb:begin` marker of
  the overview at scaffold time and read back by every command after that; a kb
  made before this picks up the mark on its next `kb sync`. `KB_LANG` now
  decides for a kb that has none.

- **Pointing the variable at an existing kb is reported, not obeyed.** Only part
  of the file is the tool's to write: the marker, the table header, the snapshot
  line and the generated block flip on the next sync, while every `title:`, the
  prose outside the markers and the filled sections of the entry point are
  written by hand and stay as they were. Flipping the setting alone leaves an
  English header over Russian titles. `check` prints the three things that have
  to be translated first and the order to do it in — at the moment somebody
  exports the variable, which is where that answer is acted on, rather than in a
  manual they are not reading at the time.

  There is no language migration command, and the finding says so.

## 4.25.0

- **The page that says how to fill the entry point was unreachable at the one
  moment it is needed.** 4.23.0 moved those instructions out of `save.md` and
  gated them on a `⚠`, which is right for every condition except the one 4.22.0
  had just added: a fresh `route` creates three empty slots and prints nothing,
  because nothing is wrong. So the save that must fill them is the save that
  cannot see the rules for filling them.

  Measured, not reasoned: the same stream was saved twice after the rules
  shipped, by a human following the procedure exactly, and both times the entry
  point came out with a command copied from a note and a line duplicating the
  generated block — the two things those rules forbid. The second run reported
  it plainly: no `⚠` was printed, so the page was never opened.

  Creating the slots is a condition now, reported by `route_findings()` like
  every other, which means `route` announces it in the turn that writes the
  file and `sync` and `verify` keep announcing it until the slots are answered.
  `verify` had carried its own copy of this check; it is gone — one
  implementation, three callers, the lesson of 4.19.3 applied to the check that
  had escaped it.

## 4.24.2

- **A filled slot could repeat what the generated block says a few lines below
  it.** Nothing forbade it, so the first entry point filled under 4.22.0 named
  `kb brief` twice in the same file — once by hand at the top, once inside the
  block — in a file loaded at the start of every session. The two copies drift
  the moment the block is regenerated. Read the block before filling the slots;
  everything it carries is already said.

## 4.24.1

- **Two tests now stand where discipline kept failing.** Examples lifted out of
  a live session reached the shipped skill four times in two days, each time
  written by whoever had just written the rule against it. `Shipped` asks two
  questions of every file that installs: does any path named here exist on this
  machine, and is any home-directory path one that is not kb's own.

  The first catches the mechanism — a leak happens by copying what is in front
  of the writer, and such a path resolves while an invented one does not. It has
  a hole, found by the leak that prompted the test: a docstring pointed into a
  home-directory tree that had been moved away the day before, so the path
  resolved to nothing and read as an invented example. The second test covers
  that hole by shape rather than by existence.

  Both were exercised against planted leaks of each kind before being believed.

- The docstring in question no longer names anybody's directory.

## 4.24.0

- **The tool is for any subject, and it had stopped saying so.** kb wrote into
  every project's `AGENTS.md` that "tests are the recorded expectation, the code
  is the actual implementation" — a sentence with no meaning for a kb of
  recipes, a case file, a renovation or a diet. The generated block now names
  only kb's own kinds: a `decision` is the intent, an active `plan` is a change
  not finished, a `state` is how things stood on its own date, and how they
  stand now is answered by a check rather than a note. Both languages.

  The commands slot said "how to bring it up and how to check it"; bringing a
  thing up is deployment. It asks what checks that the work is in good shape.

- **The skill prose carried the same bias, and worse, it carried examples
  lifted from whatever stream produced the rule.** A `tcpdump` line and a
  component directory from a live repository had been written into a tool that
  installs into three assistants and runs on every project — an example from
  one domain steers every save in every other. Removed, together with the
  product names and the software-shaped illustrations that had accumulated
  around them: a test runner, a linter, a release, "about to change the code",
  "documentation next to code", two example streams named after source
  directories.

  This class has a history in this repository: real paths leaking into examples
  was recorded three times in two days, in the documentation. This time it
  reached the shipped skill, and the author of the rule was the one who broke
  it.

## 4.23.1

- **The commands slot in the entry point is for what checks the work, not what
  the work is about.** A stream of `tcpdump` recipes had its own `tcpdump` line
  copied up into `AGENTS.md`, where it became a second copy of a command the
  note already carried, in a file loaded every session. A copy goes stale and
  the original does not — the rule that governs a note governs here too, and
  4.22.0 gave the slot no way to tell the two apart. The test that separates
  them: after running it, do I know whether the work is in good shape?

- **The entry point is written in the language of the notes.** `KB_LANG` already
  decides the generated block; the sections the assistant fills now match it, so
  one stream never asks its reader to switch languages. English beside Russian
  notes is marginally cheaper per session and worse to live with — and not even
  uniformly English, since the titles inside the generated block come from the
  front matter as written.

## 4.23.0

- **The entry-point instructions load on demand, and the tool says when.** They
  had grown to 1104 words inside `references/save.md` — a quarter of the file —
  and were paid on every save, including the ones where nothing is wrong with
  the entry point, which is most of them: `route` runs about once per project
  and the block keeps itself current after that. Measured across releases, that
  block is where a save went from 3722 words to 5138, a 38% rise since 4.15.4.

  They now live in `references/entry-point.md`, and the condition for loading it
  travels with the finding rather than sitting in prose: every command that
  prints a `⚠` about `AGENTS.md` prints the filename beside it. Prose asking the
  reader to notice a condition is the thing that gets skipped — an output line
  arrives whether or not anyone was looking for it. A save with a clean entry
  point now loads 4352 words instead of 5138, and a save with a finding loads
  what it did before.

- `release.sh` compared four files per installed copy, by name, and a fifth
  reference file would not have been compared at all — a copy could differ in it
  and still be reported as a match. It asks the source what it ships now. Same
  defect as the prose that enumerates tool output, in a shell script.

## 4.22.1

- `SKILL.md` carried the rule both halves share — "everything outside the
  markers was written by a human, do not rewrite it" — and 4.22.0 had just told
  the save half to write in exactly that region. A `kb:fill` comment is kb's own
  placeholder, not anybody's text, and the rule now says so. Left as it was, the
  page a half reads first contradicted the page it reads second, which is how an
  instruction gets ignored.

## 4.22.0

- **The save half fills the `kb:fill` slots instead of handing them back.**
  `route` leaves three — what the work is, the commands that check it, what
  proves it done — and the instruction said they were the human's. So a save on
  a fresh stream ended by asking the human to go and write them, which is the
  one outcome nobody wants: they asked for a save and got homework, and the
  next session reads a heading with no answer under it.

  The material was already there and unused. The overview paragraph answers the
  first slot, the commands the session actually ran answer the second, and the
  shape of a good result from those commands answers the third. That is
  derivation from what was just written, not invention.

  The guard that produced the old wording stays, narrowed to where it belongs:
  a stream where nothing was run and the note names no command has no honest
  answer for the commands slot. Ask for that one slot, say why, fill the rest —
  and never write a command that changes anything, for the same reason a note's
  check block holds only read-only commands.

## 4.21.1

- The restore half enumerated the entry-point findings and 4.21.0 added one to
  the list, so the subdirectory chain was reported by the tool and absent from
  the instructions that say what to do about it. Prose that enumerates tool
  output is exactly what goes stale — the same defect 4.16.1 fixed, one release
  later.

## 4.21.0

- **The context budget is per launch directory, not per file.** It measured the
  pair at the project root, which is the only place a session never actually
  starts in a layered repository. The host loads `CLAUDE.md` from the launch
  directory and every directory above it, so a component's own instruction file
  is charged **on top of** its ancestors — a sum belonging to no single file, and
  therefore to no check. Found by a human reading the tree: a component at 124
  lines under a root at 100 overran the 200-line budget while neither file broke
  it alone.

  `route_chains()` walks the project, prunes what the work-ahead check already
  prunes (ignored directories, nested streams, `SCAN_SKIP`), and reports the
  worst three chains. The root finding stays first: the root file is in every
  chain, so shortening it shortens all of them.

  Run against three real cluster repositories it named one overrun the same
  manual pass had missed — 215 lines, because the chain pulls an `@AGENTS.md`
  the eye does not add up.

- **`CLAUDE.local.md` counts.** Loaded straight after `CLAUDE.md` in the same
  directory, uncommitted, and until now absent from every number kb printed. A
  personal file is still context, and the one measured here carried 15 lines of
  it into every session started in that component.

- **`verify` scans the entry point for dead paths, and `~/…` is a path.** Two
  pointers to a directory moved that morning survived a sweep of the notes and
  the code, because they sat in a `CLAUDE.md` — which git ignores in those
  repositories, so no commit hook saw them either. Both were found by a human
  reading the file.

  `~/…` was excluded from `checkable_paths()` as shell syntax rather than a
  path, which exempted the one shape people write for a file in their home
  directory. Expanded before the root test now, so the first two components are
  still what decides.

## 4.20.0

- **The context budget follows `@`-imports now, up to four hops.** It counted the
  two files at the project root and nothing else, so a `CLAUDE.md` of two lines
  importing 633 more reported 35 and stayed quiet. An import is expanded into
  context at launch — the lines are paid for wherever they are written — which
  makes the un-followed case exactly the one that overruns worst. Measured on a
  real repository: three EKS clusters were loading 481, 471 and 381 lines each
  against a 200-line budget, and kb had nothing to say about any of them.

  Four hops because that is where Claude Code stops expanding; counting further
  would report lines that never arrive. A file reached twice is counted once —
  `CLAUDE.md` imports `AGENTS.md` in the layout `route` writes, so the seed
  matters.

- **`references/save.md` gains the table that says where moved text goes.** The
  instruction was "move what is not routing into a note", which is right for one
  of the four cases and wrong for the rest. The destination is chosen by *when*
  the file loads: a convention tied to a file type belongs in a rule with `paths:`
  frontmatter, a procedure shared across projects belongs in a skill, and
  anything reached by `@path` belongs nowhere — moving text there saves nothing
  and only makes the entry point look shorter.

## 4.19.5

- **The reverse mismatch is reported by `route` alone, not by `sync` and
  `verify`.** Its first use on a real repository landed on a state that was
  deliberate: notes committed next to the code on purpose, and every AI artifact
  excluded by a policy written long before kb existed. A finding that repeats
  every session against an intended state is furniture, and this file has the
  note explaining why that is the expensive kind of noise.

  The two directions are not equally bad, which is what the split now says. A
  committed pointer to excluded notes ships a promise nothing can keep, and that
  one still surfaces everywhere. Notes committed without their pointer ships the
  notes and omits the signpost — the reader has everything; it also follows from
  a choice `add` already put to the human.

  Stated in the code because it is a real cost: `route` runs about once per
  project, so this may go unseen. That is the trade.

## 4.19.4

- **A refusal on `AGENTS.md` no longer cancels the `CLAUDE.md` step.** `route`
  died when it found an `AGENTS.md` it had not written, and dying skipped
  everything after — so a project with a hand-written `AGENTS.md` and no
  `CLAUDE.md` came away with nothing at all, which is the worst of the three
  possible outcomes: Claude Code reads `CLAUDE.md` and not `AGENTS.md`, so it saw
  neither the notes nor the instructions already sitting there.

  The refusal is still a refusal — the file is not touched and the exit code is
  1 — but the import is written, because it links an instruction file that
  already exists to the assistant that cannot otherwise see it, whether or not
  that file carries a kb block.

## 4.19.3

- **The mismatch between the notes and their pointer was only checked in one
  direction.** 4.16.2 reported a pointer committed while its notes are excluded;
  the opposite arrangement — notes committed, pointer ignored — went unreported,
  and that is the one a real repository had. Its `.gitignore` excludes every AI
  artifact by policy (`CLAUDE.md`, `AGENTS.md`, `.claude/`, `.cursor/`,
  `GEMINI.md`) and simply had not heard of `kb/`, so a first save there would
  have shipped the notes to everyone while the file pointing at them stayed
  local. Both directions are reported now.

- `kb route` carried its own copy of the git check and its own copy of the
  budget check, separate from the ones `sync` and `verify` ask for. That is how
  the missing direction shipped: adding a condition to `route_findings()` left
  `route` itself blind to it. One implementation, three callers.

- The nested-`CLAUDE.md` question was settled against Anthropic's documentation
  rather than guessed: files in subdirectories are "included when Claude reads
  files in those subdirectories", not at launch, so the budget is right to count
  only the pair at the project root. The same page puts the recommendation at
  "under 200 lines", which is where `ROUTE_BUDGET` already sat. Block-level HTML
  comments are stripped before injection, so the markers are counted and not
  paid for — two lines in a real file, left alone rather than special-cased.

## 4.19.2

- **Everything the entry point can be wrong about is now reported by every
  command that touches it.** Four conditions were known to `kb route` alone: the
  200-line context budget, a missing `CLAUDE.md`, a `CLAUDE.md` that does not
  import, and a pointer committed while its notes are excluded. `route` runs once
  per project and then effectively never again, so each was announced in a single
  turn nobody revisits — and 4.18.0 made that worse by moving the writing to
  `sync`, which reported none of them. A file could grow past the budget one save
  at a time with the tool rewriting it each time and saying nothing.

  They are conditions rather than events: a pointer committed while its notes are
  not stays wrong until somebody fixes it. `route_findings()` collects them once
  and both `sync` and `verify` ask, so a save reports them at the moment of
  writing and a restore reports them at the start of every session.

- **The skill now fixes them rather than relaying them.** `references/save.md`
  gains a table: over budget → move the prose that is not routing into a note and
  leave a pointer, naming what moved; `CLAUDE.md` missing → write the import
  outright, since without it the entry point reaches Claude Code at all; no
  markers or a committed-vs-excluded mismatch → name the options and ask, because
  both belong to somebody else. Moving a section is an edit and is reported, never
  silent. The check commands and the definition of done never move: they are why
  the file exists.

## 4.19.1

- Both manuals described `verify`'s path and age checks and said nothing about
  the third one. "Work ahead of the notes" existed only as a row in the command
  table, so what it compares and what it skips were nowhere a reader could find
  them — and 4.19.0 had just changed both. Documented in both languages.

- The Russian text was rewritten after a reader called it unreadable, and the
  English followed so the two would not diverge. Three defects ran through
  everything added this session: the subject named by hint rather than by word
  ("пока их немного, всё сходится"), a pointer at where the text sits on the
  page rather than at what was done ("ниже — три механизма"), and actions with
  no actor ("файлы добавляются", "начинается расхождение"). All three are now
  rules 9-11 in the `ru-tech-docs` skill, found on this repository's own README.

  The archaeology went with them. Half the added prose argued with a previous
  release the reader never saw — "пока обновление зависело от явного `route`",
  "раньше это исключение действовало и здесь". That belongs in this file, not
  in a manual, which is why it is here.

- Both installers were checked at the end of the run: `install.sh` passes
  syntax, ShellCheck and the custom audit with nothing to report, and
  `install.ps1` parses clean. Their flags differ by `--version`, which the
  Windows one does not have and the README does not promise it does.

## 4.19.0

Three findings from one sweep of `kb verify` across eleven real streams. Nine
were clean afterwards; the two that were not are a genuine signal and a
documented false positive, which is the noise floor this check was supposed to
have.

- **The overview was never scanned for dead paths.** `load_notes()` skips it —
  it has no `kind` and belongs in no generated table — and that exemption
  silently followed the set into the path check. So the file whose whole job is
  "where to start" and "that subject lives in the other kb" was the only one
  never asked whether those paths still exist, and a pointer to a deleted kb sat
  in the first file every reader opens, in two separate streams. Exactly the
  shape of the link check in 4.15.4: a set assembled for one purpose, reused for
  a second without asking whether its members still belong.

- **A nested kb counted as the parent's work.** A stream inside a stream had its
  notes and its entry point reported as evidence that the outer one had moved
  on. Neither is true of either. Both layouts are recognised now — a loose
  overview, and the usual `<dir>/kb/00-overview.md`; testing only for the first
  pruned the notes and left the `AGENTS.md` beside them still counting.

- **Generated output counted as work.** A backup pipeline rewrote two hundred
  files under an ignored directory on every run, so its notes could never stop
  looking stale and the finding became furniture. Directories git is told to
  ignore are now pruned — one `check-ignore --stdin` call, and only where a
  repository answers. Where there is none the behaviour is exactly what it was,
  which is the point: most streams here are not repositories, and a check that
  cannot run must not change its answer.

## 4.18.1

- The generated block left two blank lines where the pointers go when a kb has
  neither a charter nor a snapshot — which is every kb on its first day, and the
  state `route` is most often run in. The newline sat in the template rather
  than in the value, so an empty group could not collapse. Found by reading a
  filled-in entry point in another stream, not by any check: nothing here
  compares whitespace, and nothing should.

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
