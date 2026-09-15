# The entry point at the project root

Loaded on demand. `kb sync` — and therefore every save — prints a `⚠` line per
condition and names this file beside them; `kb route` does the same when it
writes. No `⚠`, no reason to be here: on a save where the entry point is fine
this page is worth nothing, and `route` runs about once per project.

The conditions are conditions, not events. Each stays wrong until somebody fixes
it, and fixing them is yours.

## Fill the `kb:fill` slots, in the same turn

`route` leaves three: what the work is, the commands that check it, what proves
it done. **Write them from the session you just had, then say what you wrote.**
Handing the file back with the slots empty is the one outcome nobody wants: the
human asked for a save and got homework, and the next session reads a heading
with no answer under it, which is worse than no heading.

The material is already in front of you — the note you just wrote, the overview
you just filled, the commands you actually ran. That is derivation, not
invention:

| Slot | Where the answer comes from |
|---|---|
| what this work is, and its boundaries | the overview paragraph — one sentence of it |
| the commands | what checks **this work** — whatever answers "is it in good shape": `kb check` always, plus whatever this stream is checked by |
| what proves it done | the shape of a good result from those commands — `OK`, empty output, no drift |

**The commands slot holds what checks the work, not what the work is about.**
The pull is strongest where the stream's subject *is* commands — a kb of
recipes, queries or procedures. Copying one of those up into the entry point
puts a second copy of it in a file loaded every session, and a copy goes stale
while the original does not. That is the rule
that governs a note; it governs here too. Name the note instead.

The question that separates them: **after running it, do I know whether the
work is in good shape?** `kb check` answers that, and so does whatever this
stream is verified by. A command the notes are *about* answers something else
entirely, however central it is to the subject.

**Write the entry point in the language the notes are written in.** The
generated block already follows `KB_LANG`; matching it by hand keeps one reader
from meeting two languages in one stream. An English file next to Russian notes
is marginally cheaper per session and worse to live with — and it is not even
uniformly English, since the note titles inside the generated block come from
the front matter as they were written.

**Ask only for what the session genuinely does not contain**, and ask for that
one thing rather than for the file: a stream where nothing was run and the note
names no command has no honest answer to the commands slot, and guessing one
puts a command into a file an agent will execute. Leave that slot's comment in
place, say which slot and why, and fill the rest.

Never write a command that changes anything. The same rule as a note's check
block, and for the same reason: an agent told to brief and not to act read one
and ran it.

`verify` keeps reporting empty sections until they are answered, so a slot left
behind is not quietly forgotten — it is a finding every session from now on.

## Act on what the entry point reports, do not just relay it

| Reported | What to do |
|---|---|
| **over 200 lines of context** | move what is not routing out, leave one line pointing at it, re-run `kb sync`. **Choose the destination by when it loads** — the table below. Say in the report what moved and where |
| **a subdirectory over the budget** | the chain is named in the finding. Shorten the root file first — it is charged again in every chain, so one edit fixes several. Then the subdirectory's own `CLAUDE.md`, by the same table |
| `CLAUDE.md` missing, or without the import | write the one line `@AGENTS.md`. A missing `CLAUDE.md` you may create outright: Claude Code reads it and not `AGENTS.md`, so without it the entry point reaches nobody |
| `AGENTS.md` has no markers | do not add them silently — the file belongs to somebody. Say where they go and ask |
| pointer committed while the notes are not | name the two ways out — commit the notes, or exclude the pointer as well — and ask which. Both are real answers |

**Moving prose is an edit, so it is reported, never silent.** The rule this tool
holds is that nobody shortens a human's text without saying so — not that the
text may never be touched. A section moved into a note with a pointer left behind
loses nothing and costs nothing per session; the same section left in place is
paid for on every request of every session.

What may never move: the check commands and the definition of done. Those are the
reason the file exists, and an agent that has to open a note to find them will
not.

## Where the moved text goes, by when it loads

The budget is about *when* a file reaches the context window, not about where it
sits on disk. Moving text into another file that also loads at launch saves
nothing — it only makes the entry point look shorter.

| What the text is | Where it goes | When it loads |
|---|---|---|
| routing: what this work is, the check commands, the definition of done | stays in `AGENTS.md` | every session — that is what it is for |
| a convention tied to one kind of file ("when touching a `<ext>` file…") | `.claude/rules/<topic>.md` with `paths:` frontmatter | only when a matching file is read |
| a repeatable procedure shared across projects | a skill | when the model judges it relevant |
| something true of this stream only | a note in `kb/`, named from `AGENTS.md` | when someone opens it |
| anything reached by `@path` | **nowhere** — an import is expanded at launch, so the lines are paid for wherever they are written | every session |

That last row is the one that surprises: `@`-imports look like references and
behave like paste. `kb` counts them, up to four hops, because a budget that
ignored them stayed silent on the files that overran it worst — 35 lines
reported where 635 were loaded.

The budget is per launch directory. A session started in a subdirectory loads
that directory's `CLAUDE.md` on top of every ancestor's, so the root file is
charged again in every chain — which is why shortening it is the first move.
