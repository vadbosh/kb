#!/usr/bin/env python3
"""Tests for the kb CLI. Standard library only, like the tool itself.

    python3 tests/test_kb.py            all of it, a few seconds
    python3 tests/test_kb.py -v         one line per test
    python3 tests/test_kb.py Guards     one group

What is covered, and why these and not others: every case below is either a
guard the tool exists to enforce, or a bug that actually shipped once. The
regressions have their version in the docstring — `kb add --dir <fresh>` ended
in a traceback (4.0.1), `streams` read another directory's transcript (3.1.0),
Codex support was a claim no one had run (2.6.0). Each was found by a human
hitting it.

Not covered, deliberately: whether a note is *useful*. That was tried, measured
on nineteen real notes, and abandoned — see kb/02-guards-beat-prose.md.

Every run is confined to a temporary directory with its own HOME and its own
KB_REGISTRY, so the machine's real notes and registry are never touched. PATH is
cut to /usr/bin:/bin, which keeps gitleaks and trufflehog out of the run: the
secret tests are about the built-in patterns, and an external scanner would make
the result depend on what happens to be installed.
"""
import importlib.machinery
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KB = REPO / "skills" / "kb" / "scripts" / "kb"


def load_kb_module():
    """Import the CLI as a module. It has no .py suffix, hence the loader."""
    loader = importlib.machinery.SourceFileLoader("kb_cli", str(KB))
    spec = importlib.util.spec_from_loader("kb_cli", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


kb_cli = load_kb_module()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="kbtest-"))
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.proj = self.tmp / "proj"
        self.proj.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def kb(self, *argv, cwd=None, expect=None, env=None):
        environ = {
            "HOME": str(self.home),
            "KB_REGISTRY": str(self.tmp / "registry.txt"),
            "KB_LANG": "en",
            "PATH": "/usr/bin:/bin",
            "LC_ALL": "C.UTF-8",
            "PYTHONIOENCODING": "utf-8",
        }
        environ.update(env or {})
        res = subprocess.run(
            [sys.executable, str(KB), *argv],
            cwd=str(cwd or self.proj), env=environ,
            capture_output=True, text=True, timeout=120)
        if expect is not None:
            self.assertEqual(
                res.returncode, expect,
                f"\n$ kb {' '.join(argv)}\nexit {res.returncode}, "
                f"expected {expect}\n--- stdout ---\n{res.stdout}"
                f"\n--- stderr ---\n{res.stderr}")
        return res

    # helpers ---------------------------------------------------------------

    def make_kb(self, cwd=None):
        self.kb("init", cwd=cwd, expect=0)
        return (cwd or self.proj) / "kb"

    def write_note(self, root, name, kind="reference", title=None,
                   updated=None, body="text", supersedes=None):
        # Derived from the filename, because two notes promising the reader the
        # same thing is now a finding of its own.
        title = title or name.removesuffix(".md")
        fm = ["---", f"title: {title}", f"kind: {kind}",
              f"updated: {updated or date.today().isoformat()}"]
        if supersedes:
            fm.append(f"supersedes: {supersedes}")
        fm += ["---", "", f"# {title}", "", body, ""]
        path = root / name
        path.write_text("\n".join(fm), encoding="utf-8")
        return path

    def fill_overview(self, root):
        """Answer the placeholder so `check` has nothing to say about it."""
        text = (root / "00-overview.md").read_text(encoding="utf-8")
        text = text.replace(
            "<!-- one paragraph: what the work is, where it ends, "
            "what does NOT go here -->",
            "The logging pipeline. Cluster work does not go here.")
        (root / "00-overview.md").write_text(text, encoding="utf-8")


# ── the guards: why the rules live in the binary ────────────────────────────

class Guards(Base):
    """Confinement. Prose asking for this was evaded four times, each by a
    different wording of the same judgement; the binary is not persuadable."""

    def test_write_outside_cwd_refused(self):
        other = self.tmp / "other"
        other.mkdir()
        res = self.kb("add", "x", "--kind", "state", "--dir", str(other / "kb"))
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("outside", res.stderr)
        self.assertFalse((other / "kb").exists(), "refused but wrote anyway")

    def test_read_outside_cwd_refused(self):
        """Reading is confined too: a tool that reaches anywhere gets used to."""
        other = self.tmp / "other"
        other.mkdir()
        self.make_kb(cwd=other)
        res = self.kb("check", "--dir", str(other / "kb"))
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("outside", res.stderr)

    def test_allow_outside_env_lifts_it(self):
        """The escape exists for cron, and says so in the environment."""
        other = self.tmp / "other"
        other.mkdir()
        self.make_kb(cwd=other)
        self.kb("status", "--dir", str(other / "kb"),
                env={"KB_ALLOW_OUTSIDE": "1"}, expect=0)

    def test_filesystem_root_authorises_nothing(self):
        """Standing at / would otherwise put every path 'under' the cwd."""
        res = self.kb("init", cwd="/")
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("authorises nothing", res.stderr)

    def test_home_directory_refused(self):
        """Real incident: notes about a project landed in $HOME."""
        res = self.kb("init", cwd=self.proj,
                      env={"HOME": str(self.tmp)})
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("home directory", res.stderr)

    def test_directory_on_path_refused(self):
        """Real incident: a kb created among sixty executables in ~/.local/bin."""
        res = self.kb("init", cwd=self.proj,
                      env={"PATH": f"/usr/bin:/bin:{self.proj}"})
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("PATH", res.stderr)

    def test_system_directory_refused(self):
        res = self.kb("init", cwd="/tmp")
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("system directory", res.stderr)
        self.assertFalse(Path("/tmp/kb").exists())


# ── creating notes ──────────────────────────────────────────────────────────

class Add(Base):
    def test_empty_directory_gets_scaffolded(self):
        res = self.kb("add", "pipeline", "--kind", "reference", expect=0)
        self.assertIn("created", res.stdout)
        self.assertTrue((self.proj / "kb" / "00-overview.md").is_file())
        self.assertTrue((self.proj / "kb" / "01-pipeline.md").is_file())

    def test_fresh_dir_argument_gets_scaffolded(self):
        """4.0.1: --dir at a directory with no notes ended in a traceback."""
        target = self.proj / "sub" / "kb"
        res = self.kb("add", "x", "--kind", "reference", "--dir", str(target),
                      expect=0)
        self.assertNotIn("Traceback", res.stderr)
        self.assertTrue((target / "00-overview.md").is_file())
        self.assertTrue((target / "01-x.md").is_file())

    def test_numbers_increment_and_gaps_are_never_reused(self):
        root = self.make_kb()
        self.kb("add", "one", expect=0)
        self.kb("add", "two", expect=0)
        (root / "01-one.md").unlink()
        self.kb("add", "three", expect=0)
        self.assertTrue((root / "03-three.md").is_file(),
                        "a freed number was reused; references to it survive")

    def test_whitespace_in_slug_refused(self):
        self.make_kb()
        res = self.kb("add", "two words")
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("whitespace", res.stderr)

    def test_state_gets_todays_date_in_its_name(self):
        root = self.make_kb()
        self.kb("add", "snapshot", "--kind", "state", expect=0)
        today = date.today().isoformat()
        self.assertTrue((root / f"01-snapshot-{today}.md").is_file())

    def test_unknown_kind_refused(self):
        self.make_kb()
        res = self.kb("add", "x", "--kind", "notakind")
        self.assertNotEqual(res.returncode, 0)

    def test_front_matter_and_title_written(self):
        root = self.make_kb()
        self.kb("add", "x", "--kind", "decision", "--title", "why: the choice",
                expect=0)
        text = (root / "01-x.md").read_text(encoding="utf-8")
        self.assertIn("kind: decision", text)
        self.assertIn("title: why: the choice", text)

    def test_headings_match_the_kind(self):
        """4.4.0: `kind` said when a note expires, never what belongs in it."""
        root = self.make_kb()
        self.kb("add", "d", "--kind", "decision", expect=0)
        self.kb("add", "r", "--kind", "reference", expect=0)
        decision = (root / "01-d.md").read_text(encoding="utf-8")
        reference = (root / "02-r.md").read_text(encoding="utf-8")
        self.assertIn("## When to revisit", decision)
        self.assertIn("## What was rejected and why", decision)
        self.assertIn("## Where it lives", reference)
        self.assertNotIn("When to revisit", reference)
        self.assertIn("kb:fill", decision)

    def test_a_title_already_taken_is_refused(self):
        """The index column answers "what do I need?" — twice identically it
        answers nothing. Three snapshots in one day looked exactly like that."""
        self.make_kb()
        self.kb("add", "a", "--title", "what is done and what is open", expect=0)
        res = self.kb("add", "b", "--title", "what is done and what is open")
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("already promises the reader", res.stderr)
        self.assertFalse((self.proj / "kb" / "02-b.md").exists(),
                         "refused but created the file anyway")

    def test_a_different_title_is_fine(self):
        self.make_kb()
        self.kb("add", "a", "--title", "morning: before the tests", expect=0)
        self.kb("add", "b", "--title", "evening: after the release", expect=0)

    def test_both_languages_carry_the_same_headings(self):
        for lang in ("ru", "en"):
            shape = kb_cli.STRINGS[lang]["shape"]
            self.assertEqual(set(shape), set(kb_cli.KINDS),
                             f"{lang}: a kind with no headings gets none written")
            for kind, heads in shape.items():
                self.assertTrue(heads, f"{lang}/{kind}: empty skeleton")


# ── the generated index ─────────────────────────────────────────────────────

    def test_add_takes_the_body_at_creation(self):
        root = self.make_kb()
        body = self.tmp / "body.md"
        body.write_text("First paragraph.\n\n## A section\n\nText.\n",
                        encoding="utf-8")
        self.kb("add", "note", "--kind", "recipe", "--title", "a trap",
                "--body-file", str(body), expect=0)
        # Without this the note is created empty and overwritten whole: two
        # round trips, and in a long session a round trip costs the whole
        # context again -- measured at ~105k against 16 calls for one save.
        text = (root / "01-note.md").read_text(encoding="utf-8")
        self.assertIn("First paragraph.", text)
        self.assertIn("## A section", text)
        self.assertNotIn("kb:fill", text)
        self.assertEqual(text.count("# a trap"), 1)

    def test_a_body_repeating_the_heading_does_not_double_it(self):
        root = self.make_kb()
        body = self.tmp / "body.md"
        body.write_text("# a trap\n\nText.\n", encoding="utf-8")
        self.kb("add", "note", "--kind", "recipe", "--title", "a trap",
                "--body-file", str(body), expect=0)
        # Two `# ` lines for one index row is what a reader sees otherwise.
        self.assertEqual(
            (root / "01-note.md").read_text(encoding="utf-8").count("# a trap"), 1)

    def test_without_the_flag_the_skeleton_is_still_written(self):
        root = self.make_kb()
        self.kb("add", "note", "--kind", "recipe", "--title", "a trap", expect=0)
        self.assertIn("kb:fill",
                      (root / "01-note.md").read_text(encoding="utf-8"))


    def test_a_relative_dir_still_names_the_project(self):
        # `Path(".kb").parent` is `Path(".")`, whose name is the empty string —
        # so the overview came out titled `# `, carrying nothing. `--dir .kb` is
        # the ordinary way to type it, which is how this shipped.
        self.kb("add", "note", "--kind", "recipe", "--title", "t",
                "--dir", ".kb", expect=0)
        first = (self.proj / ".kb" / "00-overview.md").read_text(
            encoding="utf-8").splitlines()[0]
        self.assertIn(self.proj.name, first)

    def test_one_h1_per_note_whatever_the_body_says(self):
        root = self.make_kb()
        body = self.tmp / "body.md"
        body.write_text("# its own heading\n\nText.\n", encoding="utf-8")
        res = self.kb("add", "note", "--kind", "recipe", "--title", "a trap",
                      "--body-file", str(body), expect=0)
        text = (root / "01-note.md").read_text(encoding="utf-8")
        self.assertEqual(len([l for l in text.splitlines()
                              if l.startswith("# ")]), 1)
        self.assertIn("# a trap", text)
        # Dropping it silently would lose the only thing it said.
        self.assertIn("its own heading", res.stderr)


class Index(Base):
    def test_table_is_regenerated_from_front_matter(self):
        root = self.make_kb()
        self.write_note(root, "01-a.md", kind="recipe", title="traps worth knowing")
        self.kb("sync", expect=0)
        text = (root / "00-overview.md").read_text(encoding="utf-8")
        self.assertIn("traps worth knowing", text)
        self.assertIn("`01-a.md`", text)
        self.assertIn("recipe", text)

    def test_prose_outside_the_markers_is_never_touched(self):
        root = self.make_kb()
        overview = root / "00-overview.md"
        text = overview.read_text(encoding="utf-8")
        overview.write_text(text + "\n## Hand-written\n\nDo not rewrite this.\n",
                            encoding="utf-8")
        self.write_note(root, "01-a.md")
        self.kb("sync", expect=0)
        after = overview.read_text(encoding="utf-8")
        self.assertIn("Do not rewrite this.", after)
        self.assertIn("## Hand-written", after)

    def test_current_snapshot_is_computed_and_earlier_ones_marked(self):
        root = self.make_kb()
        self.write_note(root, "01-state-2026-01-01.md", kind="state")
        self.write_note(root, "02-state-2026-06-01.md", kind="state")
        self.kb("sync", expect=0)
        text = (root / "00-overview.md").read_text(encoding="utf-8")
        self.assertIn("Current snapshot: `02-state-2026-06-01.md`", text)
        self.assertIn("earlier snapshot", text)

    def test_name_date_beats_updated_for_which_snapshot_is_current(self):
        """`updated` moves on a typo fix; the snapshot itself does not."""
        root = self.make_kb()
        self.write_note(root, "01-state-2026-01-01.md", kind="state",
                        updated="2026-12-31")
        self.write_note(root, "02-state-2026-06-01.md", kind="state",
                        updated="2026-06-01")
        notes = kb_cli.load_notes(root)
        self.assertEqual(kb_cli.current_state(notes).name,
                         "02-state-2026-06-01.md")

    def test_supersedes_marks_both_rows(self):
        root = self.make_kb()
        self.write_note(root, "01-old.md", kind="decision", title="old choice")
        self.write_note(root, "02-new.md", kind="decision", title="new choice",
                        supersedes="01-old.md")
        self.kb("sync", expect=0)
        text = (root / "00-overview.md").read_text(encoding="utf-8")
        self.assertIn("reversed by 02", text)
        self.assertIn("⤺ 01", text)

    def test_sync_is_idempotent(self):
        root = self.make_kb()
        self.write_note(root, "01-a.md")
        self.kb("sync", expect=0)
        res = self.kb("sync", expect=0)
        self.assertIn("already current", res.stdout)


# ── check: what it catches and what it must not ─────────────────────────────

class Check(Base):
    def clean_kb(self):
        root = self.make_kb()
        self.fill_overview(root)
        self.write_note(root, "01-a.md", kind="reference")
        self.write_note(root, f"02-state-{date.today().isoformat()}.md",
                        kind="state")
        self.kb("sync", expect=0)
        return root

    def test_clean_kb_exits_zero(self):
        self.clean_kb()
        res = self.kb("check", expect=0)
        self.assertIn("clean:", res.stdout)

    def test_stale_index_is_drift_and_sync_fixes_it(self):
        root = self.clean_kb()
        self.write_note(root, "03-late.md")
        res = self.kb("check", expect=3)
        self.assertIn("stale", res.stdout)
        self.kb("sync", expect=0)
        self.kb("check", expect=0)

    def test_missing_link_target_reported(self):
        root = self.clean_kb()
        overview = root / "00-overview.md"
        overview.write_text(
            overview.read_text(encoding="utf-8") + "\nSee `09-gone.md`.\n",
            encoding="utf-8")
        res = self.kb("check", expect=3)
        self.assertIn("09-gone.md", res.stdout)

    def test_link_between_notes_is_checked_too(self):
        root = self.clean_kb()
        note = root / "01-a.md"
        note.write_text(note.read_text(encoding="utf-8") + "\nSee `08-gone.md`.\n",
                        encoding="utf-8")
        res = self.kb("check", expect=3)
        self.assertIn("01-a.md links a missing file: 08-gone.md", res.stdout)

    def test_a_note_may_point_at_the_overview(self):
        """The overview is not a note, which once made a link to it "missing".

        load_notes() skips 00-overview.md on purpose -- it has no kind and
        belongs in no generated table -- and the same set was being used as
        "files that exist". So the one file check separately insists must be
        present was the one a note could not cite.
        """
        root = self.clean_kb()
        note = root / "01-a.md"
        note.write_text(note.read_text(encoding="utf-8") + "\nSee `00-overview.md`.\n",
                        encoding="utf-8")
        self.kb("sync", expect=0)
        self.kb("check", expect=0)

    def test_the_overview_may_point_at_itself(self):
        root = self.clean_kb()
        overview = root / "00-overview.md"
        overview.write_text(
            overview.read_text(encoding="utf-8") + "\nThis file is `00-overview.md`.\n",
            encoding="utf-8")
        self.kb("check", expect=0)

    def test_a_superseded_name_is_history_not_a_broken_link(self):
        root = self.clean_kb()
        self.write_note(root, "03-new.md", kind="decision",
                        supersedes="03-deleted.md",
                        body="Replaces `03-deleted.md`, which is gone.")
        self.kb("sync", expect=0)
        self.kb("check", expect=0)

    def test_unanswered_heading_reported(self):
        """4.4.0: deleting a heading is a decision, leaving it blank is not."""
        root = self.clean_kb()
        self.kb("add", "d", "--kind", "decision", expect=0)
        res = self.kb("check", expect=3)
        self.assertIn("still empty", res.stdout)

    def test_overview_placeholder_reported(self):
        root = self.make_kb()
        self.write_note(root, "01-a.md")
        self.kb("sync", expect=0)
        res = self.kb("check", expect=3)
        self.assertIn("placeholder", res.stdout)

    def test_notes_without_a_state_reported(self):
        """`restore` says 'the situation now' and needs somewhere to read it."""
        root = self.make_kb()
        self.fill_overview(root)
        for i in (1, 2, 3):
            self.write_note(root, f"0{i}-a{i}.md", kind="reference")
        self.kb("sync", expect=0)
        res = self.kb("check", expect=3)
        self.assertIn("no `state`", res.stdout)

    def test_updated_that_is_not_a_date_reported(self):
        root = self.clean_kb()
        note = root / "01-a.md"
        note.write_text(note.read_text(encoding="utf-8")
                        .replace(f"updated: {date.today().isoformat()}",
                                 "updated: yesterday"), encoding="utf-8")
        res = self.kb("check", expect=3)
        self.assertIn("not a date", res.stdout)

    def test_note_without_front_matter_reported(self):
        root = self.clean_kb()
        (root / "03-bare.md").write_text("# bare\n\ntext\n", encoding="utf-8")
        res = self.kb("sync", expect=0)
        res = self.kb("check", expect=3)
        self.assertIn("no front matter", res.stdout)

    def test_file_outside_the_naming_scheme_reported(self):
        root = self.clean_kb()
        (root / "notes.md").write_text("# loose\n", encoding="utf-8")
        res = self.kb("check", expect=3)
        self.assertIn("not in the NN-slug.md scheme", res.stdout)

    def test_duplicate_titles_reported(self):
        """`add` refuses them now; these are the ones written earlier or
        edited by hand afterwards."""
        root = self.clean_kb()
        self.write_note(root, "03-b.md", title="the same promise")
        self.write_note(root, "04-c.md", title="the same promise")
        self.kb("sync", expect=0)
        res = self.kb("check", expect=3)
        self.assertIn("promise the reader 'the same promise'", res.stdout)
        self.assertIn("03-b.md", res.stdout)
        self.assertIn("04-c.md", res.stdout)

    def test_whitespace_in_a_filename_reported(self):
        root = self.clean_kb()
        self.write_note(root, "03-two words.md")
        res = self.kb("check", expect=3)
        self.assertIn("whitespace in the filename", res.stdout)


class Secrets(Base):
    """Exit 4 is its own code: a stale table and a private key in a note are
    not the same news, and anything automating this must tell them apart.

    The sample below is assembled at runtime rather than written out. A
    correctly formatted key in this file would be a real finding to every
    scanner that later touches the repository — fake or not."""

    def test_credential_gets_its_own_exit_code(self):
        root = self.make_kb()
        self.fill_overview(root)
        token = "xox" + "b-" + "2" * 12 + "-" + "a" * 10
        self.write_note(root, "01-a.md", body=f"token is {token} here")
        self.kb("sync", expect=0)
        res = self.kb("check", expect=4)
        self.assertIn("SECRETS", res.stdout)
        self.assertIn("01-a.md", res.stdout)

    def test_ordinary_technical_prose_is_not_a_finding(self):
        """The ratio is the product: a report that cries wolf gets ignored."""
        root = self.make_kb()
        self.fill_overview(root)
        self.write_note(root, "01-a.md", kind="reference", body=(
            "Log path `/var/log/fluent-bit/tail.db`, pod "
            "`fluent-bit-7d9c6f8b4-x2kqp`, commit 4de62bc39f1.\n"
            "The credential lives in the cluster as `kube-system/logging-creds` "
            "and is mounted as an env var; the value is not written down here.\n"
            "Checksum e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934c.\n"))
        self.write_note(root, f"02-state-{date.today().isoformat()}.md",
                        kind="state", body="Nothing open.")
        self.kb("sync", expect=0)
        self.kb("check", expect=0)

    def test_patterns_fire_on_shape_not_on_the_word(self):
        self.assertTrue(kb_cli.scan_line("password = " + '"' + "s" * 12 + '"'))
        self.assertFalse(kb_cli.scan_line("the password is stored in Vault"))
        self.assertFalse(kb_cli.scan_line("see `/etc/kubernetes/admin.conf`"))


# ── the rest of the commands ────────────────────────────────────────────────

class Commands(Base):
    def test_status_names_the_current_snapshot(self):
        root = self.make_kb()
        self.write_note(root, "01-state-2026-01-01.md", kind="state")
        self.write_note(root, "02-b.md", kind="recipe")
        self.kb("sync", expect=0)
        res = self.kb("status", expect=0)
        self.assertIn("current state: 01-state-2026-01-01.md", res.stdout)
        self.assertIn("recipe", res.stdout)

    def test_verify_flags_a_path_that_vanished(self):
        root = self.make_kb()
        self.write_note(root, "01-a.md",
                        body="Config at `/usr/share/kb-test-not-here/conf.yml`.")
        self.kb("sync", expect=0)
        res = self.kb("verify", expect=3)
        self.assertIn("/usr/share/kb-test-not-here/conf.yml", res.stdout)

    def test_verify_sees_the_work_moving_past_the_snapshot(self):
        """The one drift every other check is blind to: notes consistent with
        each other and seven releases behind the thing they describe."""
        import os, time
        root = self.make_kb()
        self.write_note(root, "01-state-2026-06-01.md", kind="state")
        self.kb("sync", expect=0)

        # Work minutes after a note is the normal shape of an active day and
        # must stay quiet; the first version of this rule fired on it every time.
        (self.proj / "app.py").write_text("changed right after the note\n")
        res = self.kb("verify", expect=0)
        self.assertIn("nothing suspicious", res.stdout)

        # Hours of work with nothing written down is the case worth reporting.
        later = time.time() + 3 * 3600
        os.utime(self.proj / "app.py", (later, later))
        res = self.kb("verify", expect=3)
        self.assertIn("work went on for 3h", res.stdout)
        self.assertIn("app.py", res.stdout)

    def test_verify_ignores_the_notes_themselves(self):
        """Writing a note is not the work moving on."""
        root = self.make_kb()
        self.write_note(root, "01-state-2026-06-01.md", kind="state")
        self.kb("sync", expect=0)
        self.write_note(root, "02-a.md", kind="reference", title="written later")
        self.kb("sync", expect=0)
        res = self.kb("verify", expect=0)
        self.assertNotIn("work went on for", res.stdout)

    def test_verify_is_quiet_when_paths_resolve(self):
        root = self.make_kb()
        self.write_note(root, "01-a.md", body="Python lives at `/usr/bin/python3`.")
        self.kb("sync", expect=0)
        res = self.kb("verify", expect=0)
        self.assertIn("nothing suspicious", res.stdout)

    def test_verify_reports_a_stale_reference(self):
        root = self.make_kb()
        old = (date.today() - timedelta(days=400)).isoformat()
        self.write_note(root, "01-a.md", kind="reference", updated=old)
        self.kb("sync", expect=0)
        res = self.kb("verify", expect=3)
        self.assertIn("not revisited", res.stdout)

    def test_brief_prints_the_overview_and_the_snapshot_verbatim(self):
        root = self.make_kb()
        self.fill_overview(root)
        self.write_note(root, "01-a.md", kind="reference", title="how it works",
                        body="a line only this file has")
        self.write_note(root, "02-state-2026-06-01.md", kind="state",
                        title="where things stand", body="the situation now")
        self.kb("sync", expect=0)
        res = self.kb("brief", expect=0)
        self.assertIn("The logging pipeline", res.stdout)     # overview prose
        self.assertIn("the situation now", res.stdout)        # snapshot body
        self.assertIn("01-a.md", res.stdout)                  # listed, not printed
        self.assertNotIn("a line only this file has", res.stdout)

    def test_brief_tells_the_relayer_not_to_summarise(self):
        """The skill file says it; an assistant summarised anyway, turning four
        releases into a list of five. The output is read for certain."""
        root = self.make_kb()
        self.fill_overview(root)
        self.write_note(root, "01-state-2026-06-01.md", kind="state")
        self.kb("sync", expect=0)
        head = "\n".join(self.kb("brief", expect=0).stdout.split("\n")[:3])
        self.assertIn("Do not retell", head)
        self.assertIn("what the work is", head)
        self.assertIn("would open", head)

    def test_brief_is_byte_identical_between_runs(self):
        """The point of the command: no model, no phrasing, no variation."""
        root = self.make_kb()
        self.fill_overview(root)
        self.write_note(root, "01-state-2026-06-01.md", kind="state")
        self.kb("sync", expect=0)
        first = self.kb("brief", expect=0).stdout
        second = self.kb("brief", expect=0).stdout
        self.assertEqual(first, second)

    def test_brief_says_why_this_snapshot_is_current(self):
        """Three snapshots on one date show the same date three times; the tie
        is broken by a number, which reads as arbitrary unless it is said."""
        root = self.make_kb()
        self.fill_overview(root)
        self.write_note(root, "01-state-2026-06-01.md", kind="state", title="one")
        self.write_note(root, "02-state-2026-06-01.md", kind="state", title="two")
        self.kb("sync", expect=0)
        res = self.kb("brief", expect=0)
        self.assertIn("02-state-2026-06-01.md", res.stdout)
        self.assertIn("highest number wins", res.stdout)

    def test_brief_separates_the_plans(self):
        """A snapshot says where things stand; the sequenced work not yet done
        lives in a `plan`, and among twenty references nobody opens it."""
        root = self.make_kb()
        self.fill_overview(root)
        self.write_note(root, "01-how.md", kind="reference", title="how it works")
        self.write_note(root, "02-next.md", kind="plan", title="the migration steps")
        self.write_note(root, "03-state-2026-06-01.md", kind="state", title="now")
        self.kb("sync", expect=0)
        out = self.kb("brief", expect=0).stdout
        self.assertIn("planned work", out)
        # Every filename also appears in the index table printed above, so the
        # order is only meaningful inside the trailer.
        tail = out[out.index("planned work"):]
        self.assertLess(tail.index("planned work"), tail.index("the rest"))
        self.assertLess(tail.index("02-next.md"), tail.index("01-how.md"))

    def test_brief_on_a_kb_with_no_snapshot_says_so(self):
        root = self.make_kb()
        self.fill_overview(root)
        self.write_note(root, "01-a.md", kind="reference")
        self.kb("sync", expect=0)
        res = self.kb("brief", expect=0)
        self.assertIn("no state note", res.stdout)

    def test_outline_maps_the_sections(self):
        root = self.make_kb()
        self.write_note(root, "01-a.md",
                        body="## First\n\ntext\n\n## Second\n\nmore\n")
        self.kb("sync", expect=0)
        res = self.kb("outline", "01-a.md", expect=0)
        self.assertIn("First", res.stdout)
        self.assertIn("Second", res.stdout)

    def test_list_shows_a_registered_kb(self):
        self.make_kb()
        res = self.kb("list", expect=0)
        self.assertIn(str(self.proj / "kb"), res.stdout)

    def test_reading_a_directory_that_is_not_a_kb_says_so(self):
        res = self.kb("check")
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("kb init", res.stderr)

    def test_hook_dry_run_writes_nothing(self):
        self.make_kb()
        (self.proj / ".git" / "hooks").mkdir(parents=True)
        self.kb("hook", "--dry-run", expect=0)
        self.assertFalse((self.proj / ".git" / "hooks" / "pre-commit").exists())

    def test_hook_install_blocks_on_exit_four(self):
        self.make_kb()
        (self.proj / ".git" / "hooks").mkdir(parents=True)
        self.kb("hook", "--install", expect=0)
        hook = self.proj / ".git" / "hooks" / "pre-commit"
        self.assertTrue(hook.is_file())
        self.assertIn("-eq 4", hook.read_text(encoding="utf-8"))


class Adopt(Base):
    """Retrofitting a hand-made directory. The descriptions a human wrote are
    the thing worth keeping — an H1 answers a different question."""

    def hand_made(self):
        d = self.proj / "notes"
        d.mkdir()
        (d / "00-overview.md").write_text(
            "# notes\n\n| file | what |\n|---|---|\n"
            "| `01-pipeline.md` | how the pipeline actually works |\n",
            encoding="utf-8")
        (d / "01-pipeline.md").write_text("# Pipeline\n\ntext\n", encoding="utf-8")
        return d

    def test_preview_moves_nothing(self):
        d = self.hand_made()
        res = self.kb("adopt", "--dir", str(d), expect=0)
        self.assertIn("preview only", res.stdout)
        self.assertTrue((d / "01-pipeline.md").is_file())
        self.assertFalse((d / "kb").exists())

    def test_apply_moves_into_kb_and_keeps_the_written_description(self):
        d = self.hand_made()
        self.kb("adopt", "--dir", str(d), "--apply", expect=0)
        moved = d / "kb" / "01-pipeline.md"
        self.assertTrue(moved.is_file())
        self.assertIn("title: how the pipeline actually works",
                      moved.read_text(encoding="utf-8"))
        self.assertIn("kb:begin",
                      (d / "kb" / "00-overview.md").read_text(encoding="utf-8"))


# ── transcripts: which directories a session touched ────────────────────────

class Transcripts(Base):
    """Unit-level, because the alternative is a fixture per harness and a
    subprocess to read it. Three formats, two of them found broken only after
    someone ran them."""

    def jsonl(self, name, records):
        path = self.tmp / name
        path.write_text("\n".join(json.dumps(r) for r in records) + "\n",
                        encoding="utf-8")
        return path

    def test_claude_format(self):
        path = self.jsonl("claude.jsonl", [
            {"type": "user", "cwd": "/srv/api",
             "message": {"role": "user", "content": "work in /srv/api"}},
            {"type": "assistant", "message": {"role": "assistant",
                                              "content": "not a user turn"}},
        ])
        got = list(kb_cli._user_messages(path))
        self.assertEqual(got, ["work in /srv/api"])

    def test_codex_format(self):
        """2.6.0 claimed Codex support; the parser keyed on the envelope, and
        Codex writes `response_item` with the role inside the payload."""
        path = self.jsonl("codex.jsonl", [
            {"type": "session_meta", "payload": {"cwd": "/srv/gateway"}},
            {"type": "response_item", "payload": {
                "role": "user",
                "content": [{"type": "input_text", "text": "deploy /srv/gateway"}]}},
        ])
        got = list(kb_cli._user_messages(path))
        self.assertEqual(got, ["deploy /srv/gateway"])

    def test_transcript_cwd_from_both_shapes(self):
        claude = self.jsonl("c.jsonl", [{"type": "user", "cwd": "/srv/api",
                                         "message": {"content": "x"}}])
        codex = self.jsonl("x.jsonl", [{"type": "session_meta",
                                        "payload": {"cwd": "/srv/gateway"}}])
        self.assertEqual(kb_cli._transcript_cwd(claude), "/srv/api")
        self.assertEqual(kb_cli._transcript_cwd(codex), "/srv/gateway")

    def test_a_transcript_with_no_cwd_is_not_claimed(self):
        """3.1.0: the newest transcript on the machine won, so a session in one
        directory reported another's work."""
        orphan = self.jsonl("o.jsonl", [{"type": "user",
                                         "message": {"content": "x"}}])
        self.assertIsNone(kb_cli._transcript_cwd(orphan))

    def test_broken_lines_do_not_stop_the_read(self):
        path = self.tmp / "mixed.jsonl"
        path.write_text('not json\n'
                        + json.dumps({"type": "user",
                                      "message": {"role": "user",
                                                  "content": "kept"}}) + "\n",
                        encoding="utf-8")
        self.assertEqual(list(kb_cli._user_messages(path)), ["kept"])

    def test_no_transcript_for_this_directory_says_so(self):
        res = self.kb("streams")
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("no transcript", res.stdout)
        self.assertIn("from memory", res.stdout)


# ── parsing ─────────────────────────────────────────────────────────────────

class Parsing(Base):
    def test_a_title_may_contain_a_colon(self):
        meta, body = kb_cli.parse_front_matter(
            "---\ntitle: why: the choice\nkind: decision\n---\n\n# h\n")
        self.assertEqual(meta["title"], "why: the choice")
        self.assertEqual(meta["kind"], "decision")
        self.assertIn("# h", body)

    def test_a_hand_quoted_title_loses_the_quotes(self):
        # The block looks like YAML, so a human editing it quotes a value with
        # a colon. Without dequoting, the quotes reach the index row.
        for quoted, plain in (('"why: the choice"', "why: the choice"),
                              ("'why: the choice'", "why: the choice")):
            meta, _ = kb_cli.parse_front_matter(
                f"---\ntitle: {quoted}\nkind: decision\n---\n\n# h\n")
            self.assertEqual(meta["title"], plain)

    def test_quotes_that_are_not_surrounding_are_kept(self):
        meta, _ = kb_cli.parse_front_matter(
            '---\ntitle: the "quoted" word inside\nkind: reference\n---\n\n# h\n')
        self.assertEqual(meta["title"], 'the "quoted" word inside')

    def test_text_without_front_matter_survives_intact(self):
        meta, body = kb_cli.parse_front_matter("# just a heading\n")
        self.assertEqual(meta, {})
        self.assertEqual(body, "# just a heading\n")

    def test_links_are_found_in_backticks_and_in_markdown(self):
        found = kb_cli.linked_files("see `01-a.md` and [b](02-b.md), not 03-c.md")
        self.assertEqual(found, {"01-a.md", "02-b.md"})

    def test_replace_block_reports_absent_markers(self):
        self.assertIsNone(kb_cli.replace_block("no markers here", "x"))

    def test_checkable_paths_ignores_prose_and_fragments(self):
        text = ("`/usr/share/doc` is real, /usr/share/doc in prose is not, "
                "`/v1alpha1/status` is an API path, `/usr/.../doc` is elided")
        self.assertEqual(kb_cli.checkable_paths(text), {"/usr/share/doc"})


# ── one direction per stream ────────────────────────────────────────────────

class Charter(Base):
    def test_a_second_charter_is_refused(self):
        self.make_kb()
        self.kb("add", "why", "--kind", "charter", "--title", "why we build it",
                expect=0)
        res = self.kb("add", "why2", "--kind", "charter", "--title", "other way",
                      expect=1)
        self.assertIn("already the charter", res.stderr)

    def test_two_hand_written_charters_are_a_finding(self):
        root = self.make_kb()
        self.fill_overview(root)
        self.write_note(root, "01-a.md", kind="charter", title="one direction")
        self.write_note(root, "02-b.md", kind="charter", title="another")
        self.kb("sync", expect=0)
        res = self.kb("check", expect=3)
        self.assertIn("2 charters", res.stdout)

    def test_brief_prints_the_charter_before_the_snapshot(self):
        root = self.make_kb()
        self.fill_overview(root)
        self.write_note(root, "01-now-2026-01-02.md", kind="state",
                        title="where it stands")
        self.write_note(root, "02-why.md", kind="charter", title="why it exists")
        self.kb("sync", expect=0)
        out = self.kb("brief", expect=0).stdout
        # A list of what is done means nothing before the reader knows what the
        # work is for, so the order is the point, not the presence.
        self.assertLess(out.index("02-why.md ─"), out.index("01-now-2026-01-02.md ─"))


# ── the entry point at the project root ─────────────────────────────────────

class Route(Base):
    def test_it_writes_both_files_with_the_content_in_only_one(self):
        self.make_kb()
        self.kb("route", expect=0)
        agents = (self.proj / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("kb brief", agents)
        # Claude Code reads CLAUDE.md and not AGENTS.md, so both must exist --
        # but a second copy of the text is what goes stale, hence the import.
        self.assertEqual((self.proj / "CLAUDE.md").read_text(encoding="utf-8"),
                         "@AGENTS.md\n")

    def test_it_names_the_charter_and_the_current_snapshot(self):
        root = self.make_kb()
        self.write_note(root, "01-why.md", kind="charter", title="why")
        self.write_note(root, "02-now-2026-01-02.md", kind="state", title="now")
        self.kb("route", expect=0)
        agents = (self.proj / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("kb/01-why.md", agents)
        self.assertIn("kb/02-now-2026-01-02.md", agents)

    def test_prose_outside_the_markers_survives_a_rewrite(self):
        self.make_kb()
        (self.proj / "AGENTS.md").write_text(
            "# mine\n\nmy rule\n\n<!-- kb:begin -->\n<!-- kb:end -->\n\nafter\n",
            encoding="utf-8")
        self.kb("route", expect=0)
        text = (self.proj / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("my rule", text)
        self.assertIn("after", text)
        self.assertIn("kb brief", text)

    def test_a_foreign_file_without_markers_is_refused(self):
        self.make_kb()
        (self.proj / "AGENTS.md").write_text("# hand written\n", encoding="utf-8")
        res = self.kb("route", expect=1)
        self.assertIn("no managed block", res.stdout)
        self.assertEqual((self.proj / "AGENTS.md").read_text(encoding="utf-8"),
                         "# hand written\n")

    def test_a_refused_agents_file_still_gets_its_claude_import(self):
        self.make_kb()
        mine = self.proj / "AGENTS.md"
        mine.write_text("# hand written\n\nmy rules\n", encoding="utf-8")
        res = self.kb("route", expect=1)
        # Dying on the refusal skipped the CLAUDE.md step too, so a project with
        # a hand-written AGENTS.md and no CLAUDE.md got nothing — and Claude
        # Code reads only the second one.
        self.assertEqual(mine.read_text(encoding="utf-8"),
                         "# hand written\n\nmy rules\n")
        self.assertEqual((self.proj / "CLAUDE.md").read_text(encoding="utf-8"),
                         "@AGENTS.md\n")
        self.assertIn("no managed block", res.stdout)

    def test_an_existing_claude_file_is_advised_not_edited(self):
        self.make_kb()
        (self.proj / "CLAUDE.md").write_text("# mine\n", encoding="utf-8")
        res = self.kb("route", expect=0)
        self.assertIn("@AGENTS.md", res.stdout)
        self.assertEqual((self.proj / "CLAUDE.md").read_text(encoding="utf-8"),
                         "# mine\n")

    def test_an_oversized_entry_point_is_reported_by_route_and_verify(self):
        self.make_kb()
        self.kb("route", expect=0)
        agents = self.proj / "AGENTS.md"
        agents.write_text(agents.read_text(encoding="utf-8")
                          + "\n".join(f"line {i}" for i in range(250)) + "\n",
                          encoding="utf-8")
        # Not a note: this is expanded into context at every session start, so
        # length is a running cost and the 200-line rule applies to it.
        self.assertIn("lines of context every session", self.kb("route", expect=0).stdout)
        self.assertIn("lines of context every session", self.kb("verify", expect=3).stdout)

    def test_scaffolding_says_the_project_root_has_no_pointer(self):
        # The condition for the automatic `route` arrives in the output of the
        # command the caller already ran, not in prose it has to remember.
        res = self.kb("add", "a", "--kind", "reference", "--title", "a", expect=0)
        self.assertIn("kb route", res.stderr)

    def test_that_note_is_absent_when_an_entry_point_exists(self):
        (self.proj / "AGENTS.md").write_text("# mine\n", encoding="utf-8")
        res = self.kb("add", "a", "--kind", "reference", "--title", "a", expect=0)
        self.assertNotIn("kb route", res.stderr)

    def test_verify_reports_entry_point_slots_left_empty(self):
        self.make_kb()
        self.kb("route", expect=0)
        # `route` says this once, in the turn that wrote the file, and nobody
        # sees that message again.
        res = self.kb("verify", expect=3)
        self.assertIn("nobody has answered", res.stdout)
        agents = self.proj / "AGENTS.md"
        text = agents.read_text(encoding="utf-8")
        while "<!-- kb:fill" in text:
            start = text.index("<!-- kb:fill")
            text = text[:start] + "answered" + text[text.index("-->", start) + 3:]
        agents.write_text(text, encoding="utf-8")
        self.assertNotIn("nobody has answered", self.kb("verify").stdout)

    def test_route_does_not_make_verify_report_its_own_output_as_work(self):
        root = self.make_kb()
        self.fill_overview(root)
        self.write_note(root, "01-now-2026-01-02.md", kind="state", title="now")
        self.kb("sync", expect=0)
        self.kb("route", expect=0)
        # The two files kb just wrote are newer than every note by construction,
        # so counting them would make `route` guarantee this finding.
        out = self.kb("verify").stdout
        self.assertNotIn("AGENTS.md", out.split("the entry point")[0])
        self.assertNotIn("work went on", out)

    def test_the_budget_follows_imports(self):
        self.make_kb()
        self.kb("route", expect=0)
        big = self.proj / "conventions.md"
        big.write_text("\n".join(f"line {i}" for i in range(250)) + "\n",
                       encoding="utf-8")
        claude = self.proj / "CLAUDE.md"
        claude.write_text(claude.read_text(encoding="utf-8")
                          + f"@{big}\n", encoding="utf-8")
        # An import is expanded into context at launch, so counting only the two
        # files at the project root reported 35 lines where 635 were loaded —
        # silent on exactly the files that overrun the budget worst.
        res = self.kb("route", expect=0)
        self.assertIn("conventions.md 250", res.stdout)
        self.assertIn("budget 200", res.stdout)

    def test_the_budget_covers_a_session_started_in_a_subdirectory(self):
        self.make_kb()
        self.kb("route", expect=0)
        # Neither file breaks the budget alone. The host loads both when the
        # session starts in the component directory, and that sum was nobody's.
        comp = self.proj / "component"
        comp.mkdir()
        (comp / "CLAUDE.md").write_text(
            "\n".join(f"line {i}" for i in range(150)) + "\n", encoding="utf-8")
        root_claude = self.proj / "CLAUDE.md"
        root_claude.write_text(root_claude.read_text(encoding="utf-8")
                               + "\n".join(f"pad {i}" for i in range(80)) + "\n",
                               encoding="utf-8")
        out = self.kb("route", expect=0).stdout
        self.assertIn("component/", out)
        self.assertIn("component/CLAUDE.md 150", out)
        self.assertIn("budget 200", out)

    def test_route_reports_the_slots_it_just_created(self):
        self.make_kb()
        # The instructions for filling them load on demand, gated on a finding.
        # With no finding here the page was unreachable at the one moment it is
        # needed, and two rules written into it were broken twice in a row by a
        # human following the procedure correctly.
        out = self.kb("route", expect=0).stdout
        self.assertIn("nobody has answered", out)
        self.assertIn("references/entry-point.md", out)

    def test_a_finding_names_the_file_that_says_what_to_do(self):
        self.make_kb()
        self.kb("route", expect=0)
        big = self.proj / "CLAUDE.md"
        big.write_text("\n".join(f"line {i}" for i in range(250)) + "\n",
                       encoding="utf-8")
        # The page of instructions is worth nothing on a save where the entry
        # point is fine, so it loads on demand -- and the condition for loading
        # it travels with the finding instead of sitting in prose nobody reads.
        out = self.kb("route", expect=0).stdout
        self.assertIn("budget 200", out)
        self.assertIn("references/entry-point.md", out)

    def test_a_clean_entry_point_names_no_file(self):
        self.make_kb()
        self.kb("route", expect=0)
        self.assertNotIn("references/entry-point.md",
                         self.kb("sync", expect=0).stdout)

    def test_a_subdirectory_under_the_budget_is_not_reported(self):
        self.make_kb()
        self.kb("route", expect=0)
        comp = self.proj / "2.CORE"
        comp.mkdir()
        (comp / "CLAUDE.md").write_text("small\n", encoding="utf-8")
        self.assertEqual(kb_cli.route_chains(self.proj), [])
        self.assertNotIn("2.CORE", self.kb("route", expect=0).stdout)

    def test_the_personal_file_is_part_of_the_bill(self):
        self.make_kb()
        self.kb("route", expect=0)
        before = kb_cli.route_weight(self.proj)[0]
        # Loaded straight after CLAUDE.md in the same directory, uncommitted and
        # therefore invisible to anything that reads the repository instead.
        (self.proj / "CLAUDE.local.md").write_text(
            "\n".join(f"mine {i}" for i in range(40)) + "\n", encoding="utf-8")
        total, parts = kb_cli.route_weight(self.proj)
        self.assertEqual(total, before + 40)
        self.assertIn("CLAUDE.local.md 40", parts)

    def test_a_file_imported_twice_is_counted_once(self):
        self.make_kb()
        self.kb("route", expect=0)
        # `CLAUDE.md` imports `AGENTS.md` in the layout `route` writes, so
        # AGENTS.md is both a root and an import.
        total, parts = kb_cli.route_weight(self.proj)
        self.assertEqual(len([p for p in parts if p.startswith("AGENTS.md")]), 1)
        self.assertEqual(total, sum(int(p.rsplit(" ", 1)[1]) for p in parts))

    def test_the_reported_size_is_the_one_wc_would_print(self):
        self.make_kb()
        self.kb("route", expect=0)
        expected = sum(len((self.proj / n).read_text(encoding="utf-8").splitlines())
                       for n in ("AGENTS.md", "CLAUDE.md"))
        self.assertEqual(kb_cli.route_weight(self.proj)[0], expected)

    def test_a_committed_pointer_to_excluded_notes_is_reported(self):
        subprocess.run(["git", "init", "-q", "."], cwd=str(self.proj),
                       capture_output=True,
                       env={"HOME": str(self.home), "PATH": "/usr/bin:/bin"},
                       timeout=60)
        self.make_kb()
        self.kb("local", expect=0)
        # Each half is defensible alone -- local notes, a shared entry point.
        # Only the combination ships a promise the clone cannot keep.
        res = self.kb("route", expect=0)
        self.assertIn("is not excluded while", res.stdout)
        # And it says what git would say. The word was "committed", in a
        # repository that had no commits at all: a finding that overstates the
        # state sends the reader to fix a situation that does not exist.
        self.assertNotIn("is committed", res.stdout)

    def test_the_reverse_mismatch_is_reported_too(self):
        env = {"HOME": str(self.home), "PATH": "/usr/bin:/bin"}
        def git(*a):
            subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", *a],
                           cwd=str(self.proj), capture_output=True, env=env,
                           timeout=60)
        git("init", "-q", ".")
        (self.proj / ".gitignore").write_text("AGENTS.md\nCLAUDE.md\n",
                                              encoding="utf-8")
        self.make_kb()
        self.kb("route", expect=0)
        git("add", "-A")
        git("commit", "-qm", "notes")
        # The other half of the pair: notes ship, the pointer does not. Found on
        # a repository whose policy ignores every AI artifact and had not yet
        # named the notes.
        res = self.kb("route", expect=0)
        self.assertIn("nothing there points at them", res.stdout)
        # …and only there. The notes still reach a clone, the choice was already
        # made when `add` asked, and a repository that excludes every AI
        # artifact by policy answers it the same way every time — repeated each
        # session it would be furniture.
        self.assertNotIn("nothing there points at them", self.kb("verify").stdout)
        self.assertNotIn("nothing there points at them",
                         self.kb("add", "two", "--kind", "recipe",
                                 "--title", "a trap", expect=0).stdout)

    def test_no_such_report_when_both_are_excluded(self):
        subprocess.run(["git", "init", "-q", "."], cwd=str(self.proj),
                       capture_output=True,
                       env={"HOME": str(self.home), "PATH": "/usr/bin:/bin"},
                       timeout=60)
        self.make_kb()
        self.kb("local", expect=0)
        exclude = self.proj / ".git" / "info" / "exclude"
        exclude.write_text(exclude.read_text(encoding="utf-8")
                           + "/AGENTS.md\n/CLAUDE.md\n", encoding="utf-8")
        self.assertNotIn("is not excluded while", self.kb("route", expect=0).stdout)

    def test_running_it_twice_changes_nothing(self):
        self.make_kb()
        self.kb("route", expect=0)
        first = (self.proj / "AGENTS.md").read_text(encoding="utf-8")
        res = self.kb("route", expect=0)
        self.assertIn("already current", res.stdout)
        self.assertEqual((self.proj / "AGENTS.md").read_text(encoding="utf-8"),
                         first)


# ── versioned, local, or nobody has chosen ──────────────────────────────────

class GitState(Base):
    def git(self, *argv, cwd=None):
        return subprocess.run(
            ["git", "-c", "user.email=t@t", "-c", "user.name=t", *argv],
            cwd=str(cwd or self.proj), capture_output=True, text=True,
            env={"HOME": str(self.home), "PATH": "/usr/bin:/bin"}, timeout=60)

    def test_a_new_kb_in_a_repo_says_the_choice_is_open(self):
        self.git("init", "-q", ".")
        res = self.kb("add", "a", "--kind", "reference", "--title", "a", expect=0)
        self.assertIn("not ignored", res.stderr)
        self.assertIn("neither tracked nor ignored", self.kb("status").stdout)

    def test_local_excludes_the_notes_and_is_idempotent(self):
        self.git("init", "-q", ".")
        self.make_kb()
        self.kb("local", expect=0)
        exclude = (self.proj / ".git" / "info" / "exclude").read_text(encoding="utf-8")
        self.assertIn("/kb/", exclude.splitlines())
        self.assertIn("git: excluded", self.kb("status").stdout)
        res = self.kb("local", expect=0)
        self.assertIn("already ignored", res.stdout)

    def test_local_refuses_once_the_notes_are_tracked(self):
        self.git("init", "-q", ".")
        self.make_kb()
        self.git("add", "-A")
        self.git("commit", "-qm", "notes")
        res = self.kb("local", expect=1)
        # An exclude rule does not apply to a tracked file, so writing one would
        # print success and change nothing.
        self.assertIn("already tracked", res.stderr)
        self.assertIn("git: tracked", self.kb("status").stdout)

    def test_outside_a_repository_there_is_no_question(self):
        self.make_kb()
        self.assertNotIn("git:", self.kb("status").stdout)
        res = self.kb("local", expect=1)
        self.assertIn("not inside a git repository", res.stderr)


# ── one fixture, commands in the order a session uses them ──────────────────

class Sequence(Base):
    """Every other case here builds a world for one command and asks it one
    question. Three of the four releases on 2026-09-13 fixed a defect that
    needed neither: a directory with a decision already taken, or a second
    command run after a first. Both were found by hand, after shipping.

    So this class runs the sequence instead: add, route, verify, local, route.
    State carries from step to step, which is the only condition under which
    those two defects exist at all.
    """

    def git(self, *argv):
        return subprocess.run(
            ["git", "-c", "user.email=t@t", "-c", "user.name=t", *argv],
            cwd=str(self.proj), capture_output=True, text=True,
            env={"HOME": str(self.home), "PATH": "/usr/bin:/bin"}, timeout=60)

    def aged_kb(self, hours=48):
        """A kb whose notes are not from this minute.

        `verify` only calls work "ahead of the notes" past UNWRITTEN_HOURS, so
        a fixture written a moment ago cannot produce that finding at all — the
        first version of the release-time probe passed with the defect put
        back, for exactly this reason.
        """
        root = self.make_kb()
        self.fill_overview(root)
        self.write_note(root, "01-now-2026-01-02.md", kind="state", title="now")
        self.write_note(root, "02-why.md", kind="charter", title="why")
        self.kb("sync", expect=0)
        old = time.time() - hours * 3600
        for f in root.glob("*.md"):
            os.utime(f, (old, old))
        return root

    def test_a_nested_stream_is_not_the_parents_work(self):
        root = self.aged_kb()
        del root
        nested = self.proj / "sub"
        nested.mkdir(parents=True)
        # Not `mkdir(nested / "kb")`: kb refuses to scaffold into a directory
        # somebody else made, and creating it here made the setup a test of
        # that refusal instead of the thing it is named after.
        self.kb("init", cwd=nested, expect=0)
        (nested / "AGENTS.md").write_text("pointer\n", encoding="utf-8")
        # A kb inside a kb is another subject, not evidence the parent moved on.
        # Its notes and its entry point were both counted before.
        out = self.kb("verify").stdout
        self.assertNotIn("work went on", out)

    def test_generated_output_git_is_told_to_ignore_is_not_work(self):
        subprocess.run(["git", "init", "-q", "."], cwd=str(self.proj),
                       capture_output=True,
                       env={"HOME": str(self.home), "PATH": "/usr/bin:/bin"},
                       timeout=60)
        ignore = self.proj / ".gitignore"
        ignore.write_text("out/\n", encoding="utf-8")
        self.aged_kb()
        # `.gitignore` is tracked content and would otherwise be the newest
        # thing here, which is a true finding about the wrong subject.
        old = time.time() - 48 * 3600
        os.utime(ignore, (old, old))
        out_dir = self.proj / "out"
        out_dir.mkdir()
        for i in range(3):
            (out_dir / f"artifact{i}.bin").write_text("x", encoding="utf-8")
        # A pipeline that rewrites its own output on every run would otherwise
        # keep its notes permanently "behind the work".
        self.assertNotIn("work went on", self.kb("verify").stdout)
        # A tracked file of the same age still counts — the point is what the
        # project calls its content, not the timestamp.
        (self.proj / "real.sh").write_text("x", encoding="utf-8")
        self.assertIn("work went on", self.kb("verify").stdout)

    def test_a_dead_path_in_the_overview_is_reported(self):
        root = self.make_kb()
        self.fill_overview(root)
        self.write_note(root, "01-a.md", kind="reference", title="a")
        gone = self.tmp / "vanished" / "kb"
        text = (root / "00-overview.md").read_text(encoding="utf-8")
        (root / "00-overview.md").write_text(
            text + f"\nBoundary: that subject lives in `{gone}`.\n",
            encoding="utf-8")
        # load_notes() skips the overview, and that exemption used to follow the
        # set into the path check — leaving the file with the most cross-stream
        # pointers as the only one never checked.
        res = self.kb("verify", expect=3)
        self.assertIn(str(gone), res.stdout)
        self.assertIn("00-overview.md", res.stdout)

    def test_a_dead_path_in_the_entry_point_is_reported(self):
        root = self.aged_kb()
        self.kb("route", expect=0)
        gone = self.tmp / "moved-away" / "runbook.md"
        agents = self.proj / "AGENTS.md"
        agents.write_text(agents.read_text(encoding="utf-8")
                          + f"\nFull runbook: `{gone}`.\n", encoding="utf-8")
        # An agent reads this file before touching anything, and git ignores it
        # in the repositories that found this — so no commit hook sees it either.
        res = self.kb("verify", expect=3)
        self.assertIn(str(gone), res.stdout)
        self.assertIn("AGENTS.md", res.stdout.split("the entry point")[0])
        self.assertTrue(root.is_dir())

    def test_a_home_relative_path_is_checked(self):
        root = self.aged_kb()
        self.write_note(root, "02-b.md", kind="reference", title="b",
                        body="Runbook: `~/.claude/conventions/gone.md`.")
        # `~/…` was excluded as shell syntax, which let through the one shape
        # people write for a file in their home directory.
        res = self.kb("verify", expect=3)
        self.assertIn("~/.claude/conventions/gone.md", res.stdout)

    def test_sync_reports_the_budget_it_just_refreshed_past(self):
        self.aged_kb()
        self.kb("route", expect=0)
        agents = self.proj / "AGENTS.md"
        agents.write_text(agents.read_text(encoding="utf-8")
                          + "\n".join(f"line {i}" for i in range(250)) + "\n",
                          encoding="utf-8")
        # `sync` is the only command that touches this file after the first
        # `route`, so reporting the overrun only in `route` reports it once, in
        # a turn nobody revisits.
        res = self.kb("add", "later", "--kind", "recipe", "--title", "a trap",
                      expect=0)
        self.assertIn("entry point refreshed", res.stdout)
        self.assertIn("budget 200", res.stdout)

    def test_a_hand_edited_entry_point_is_a_check_finding(self):
        self.aged_kb()
        self.kb("route", expect=0)
        agents = self.proj / "AGENTS.md"
        # `sync` keeps it current now, so drift means sync never ran: front
        # matter edited by hand, or the block itself.
        agents.write_text(
            agents.read_text(encoding="utf-8").replace("2 of them", "99 of them"),
            encoding="utf-8")
        res = self.kb("check", expect=3)
        self.assertIn("entry point at the project root", res.stdout)
        self.kb("sync", expect=0)
        self.assertIn("2 of them", agents.read_text(encoding="utf-8"))

    def test_a_foreign_file_at_the_project_root_is_never_touched(self):
        self.aged_kb()
        mine = self.proj / "AGENTS.md"
        mine.write_text("# mine, no markers\n", encoding="utf-8")
        # No markers means kb did not write it, so sync has nothing to refresh
        # and check has nothing to compare — silence, not a finding.
        self.kb("add", "later", "--kind", "recipe", "--title", "a trap", expect=0)
        self.assertEqual(mine.read_text(encoding="utf-8"), "# mine, no markers\n")
        self.assertNotIn("entry point", self.kb("check").stdout)

    def test_route_then_verify_then_local_then_route(self):
        self.git("init", "-q", ".")
        self.aged_kb()

        self.kb("route", expect=0)
        after_route = self.kb("verify").stdout
        # Step 1 → 2: the files route just wrote are newer than every note by
        # construction, so without the exclusion this fires every time.
        self.assertNotIn("work went on", after_route)

        out = self.kb("local", expect=0).stdout
        # Step 3 → 4: the notes and the file pointing at them are one decision.
        # Excluding only the notes left a pointer the next `git add -A` takes,
        # and the tool then reported the state it had just created itself.
        self.assertIn("/AGENTS.md", out)
        self.assertIn("/CLAUDE.md", out)
        exclude = (self.proj / ".git" / "info" / "exclude").read_text(
            encoding="utf-8")
        for pattern in ("/kb/", "/AGENTS.md", "/CLAUDE.md"):
            self.assertIn(pattern, exclude)
        self.assertNotIn("is not excluded while", self.kb("route", expect=0).stdout)

    def test_local_leaves_a_file_it_did_not_write_alone(self):
        self.git("init", "-q", ".")
        self.aged_kb()
        mine = self.proj / "AGENTS.md"
        mine.write_text("# mine, no markers\n", encoding="utf-8")
        self.kb("local", expect=0)
        exclude = (self.proj / ".git" / "info" / "exclude").read_text(
            encoding="utf-8")
        # Somebody else's file, so the decision about it is somebody else's.
        self.assertIn("/kb/", exclude)
        self.assertNotIn("/AGENTS.md", exclude)

    def test_a_second_save_carries_the_entry_point_with_it(self):
        self.aged_kb()
        self.kb("route", expect=0)
        agents = self.proj / "AGENTS.md"
        before = agents.read_text(encoding="utf-8")
        self.assertIn("2 of them", before)

        self.kb("add", "later", "--kind", "state", "--title", "newer", expect=0)
        after = agents.read_text(encoding="utf-8")
        # The entry point carries the same derived facts as the index. Left to
        # an explicit `route` it named a superseded snapshot for as long as
        # nobody ran one -- and it is the copy a fresh session reads first.
        self.assertIn("3 of them", after)
        self.assertNotIn(before.split("<!-- kb:begin")[1], after)
        # Prose outside the markers is still nobody's business but the human's.
        self.assertEqual(before.split("<!-- kb:begin")[0],
                         after.split("<!-- kb:begin")[0])
        # And the snapshot it names is the new one, not the one it was written
        # with — the whole point of refreshing rather than reporting.
        self.assertNotIn("01-now-2026-01-02.md", after)


# ── nothing of this machine ships in a universal tool ───────────────────────

class Shipped(unittest.TestCase):
    """The skill installs into every assistant and runs on every subject.

    An example lifted from whatever stream produced a rule steers every save in
    every other one -- a directory from a live repository and a command from one
    domain both reached the shipped files before this test existed. The leak
    happens by copying something that is in front of the writer at the time, so
    what catches it is asking whether the path is real here.
    """

    SHIPPED = sorted((REPO / "skills" / "kb").rglob("*"))
    # The tool's own layout. Fixed, so naming it cannot rot: anything else
    # under a home dotdir is somebody's directory rather than kb's.
    OWN = ("/skills/kb", "/.local/bin", "/.local/state/kb", "/.kb-docs",
           "/.local/share/opencode",
           # System locations: an interpreter, a shell, a directory used to
           # illustrate a check. Present on every machine, so naming one is not
           # a copy of anything local.
           "/usr/", "/bin/")
    PATH_RE = __import__("re").compile(r"(~|\$HOME)?(/[A-Za-z0-9_.<>*-]+){2,}")

    def paths_in(self, text):
        for m in self.PATH_RE.finditer(text):
            raw = m.group(0)
            if any(o in raw for o in self.OWN):
                continue
            yield raw

    def test_no_path_of_this_machine_is_named(self):
        found = []
        for f in self.SHIPPED:
            if not f.is_file():
                continue
            for raw in self.paths_in(f.read_text(encoding="utf-8",
                                                 errors="replace")):
                p = Path(raw.replace("$HOME", "~")).expanduser()
                if p.exists():
                    found.append(f"{f.relative_to(REPO)}: {raw}")
        self.assertEqual(found, [], "\n".join(
            ["a path that exists on this machine is named in a shipped file:"]
            + found))

    def test_no_home_directory_of_somebody_else(self):
        """`~/.claude/conventions/...` shipped once and this is what catches it.

        The existence test above cannot: that directory had been moved away by
        the time anyone looked, so the pointer to it resolved to nothing and
        read as an invented example.
        """
        allowed = {"skills", "opencode", "kb", "bin", "state", "share"}
        found = []
        for f in self.SHIPPED:
            if not f.is_file():
                continue
            for raw in self.paths_in(f.read_text(encoding="utf-8",
                                                 errors="replace")):
                if not raw.startswith(("~/.", "$HOME/.")):
                    continue
                parts = raw.split("/")
                if len(parts) > 2 and parts[2] not in allowed:
                    found.append(f"{f.relative_to(REPO)}: {raw}")
        self.assertEqual(found, [], "\n".join(
            ["a home-directory path that is not kb's own is named:"] + found))


# ── the language belongs to the kb, not to the machine ──────────────────────

class Language(Base):
    def test_a_kb_records_the_language_it_was_made_in(self):
        root = self.make_kb()          # the harness runs with KB_LANG=en
        self.assertIn("kb:begin lang=en",
                      (root / "00-overview.md").read_text(encoding="utf-8"))

    def test_it_keeps_that_language_when_the_machine_says_otherwise(self):
        root = self.make_kb()
        self.write_note(root, "01-a.md", title="how it works")
        # Two streams in two languages on one machine, and a kb cloned onto a
        # machine set up differently: both need the kb to answer, not the env.
        self.kb("sync", env={"KB_LANG": "ru"}, expect=0)
        text = (root / "00-overview.md").read_text(encoding="utf-8")
        self.assertIn("| what you need |", text)
        self.assertNotIn("| что нужно |", text)

    def test_a_kb_from_before_the_mark_gains_it_on_the_next_sync(self):
        root = self.make_kb()
        f = root / "00-overview.md"
        f.write_text(f.read_text(encoding="utf-8").replace("kb:begin lang=en",
                                                           "kb:begin"),
                     encoding="utf-8")
        self.write_note(root, "01-a.md", title="how it works")
        self.kb("sync", expect=0)
        self.assertIn("kb:begin lang=en", f.read_text(encoding="utf-8"))

    def test_asking_for_another_language_reports_what_switching_costs(self):
        root = self.make_kb()
        self.fill_overview(root)
        self.write_note(root, "01-a.md", title="how it works")
        self.kb("sync", expect=0)
        # A setting cannot translate a title or the prose outside the markers.
        # Left silent, the file ends up half in each language.
        res = self.kb("check", env={"KB_LANG": "ru"}, expect=3)
        self.assertIn("these notes are en", res.stdout)
        self.assertIn("title:", res.stdout)
        self.assertEqual(self.kb("check").returncode, 0)


# ── the notes directory is not automatically ours ───────────────────────────

class NotesDir(Base):
    """`kb` is an ordinary directory name and a project may already have one.

    Measured on a directory holding two source files: the scaffold went in
    beside them and kb treated the directory as its own from then on. Nothing
    was overwritten, which is not the point -- the directory belonged to
    somebody and the tool took it without asking.
    """

    def test_it_refuses_a_directory_somebody_else_made(self):
        (self.proj / "kb").mkdir()
        (self.proj / "kb" / "main.go").write_text("package kb\n", encoding="utf-8")
        res = self.kb("add", "note", "--kind", "reference", "--title", "t")
        self.assertEqual(res.returncode, 1)
        self.assertIn("does not write into one it did not make", res.stderr)
        self.assertFalse((self.proj / "kb" / "00-overview.md").exists())

    def test_empty_is_taken_too(self):
        # An empty directory somebody made is a placeholder for the thing they
        # are about to put in it. "It was empty" is not consent.
        (self.proj / "kb").mkdir()
        res = self.kb("add", "note", "--kind", "reference", "--title", "t")
        self.assertEqual(res.returncode, 1)
        self.assertIn("is empty", res.stderr)

    def test_the_human_can_say_it_is_for_the_notes(self):
        (self.proj / "kb").mkdir()
        self.kb("add", "note", "--kind", "reference", "--title", "t",
                env={"KB_ALLOW_EXISTING": "1"}, expect=0)
        self.assertTrue((self.proj / "kb" / "00-overview.md").is_file())

    def test_markdown_inside_names_adopt(self):
        (self.proj / "kb").mkdir()
        (self.proj / "kb" / "notes.md").write_text("# mine\n", encoding="utf-8")
        self.assertIn("kb adopt", self.kb(
            "add", "n", "--kind", "reference", "--title", "t").stderr)

    def test_dir_does_not_bypass_it(self):
        # `--dir src` with a typo is the same situation as somebody else's kb/.
        (self.proj / "src").mkdir()
        (self.proj / "src" / "main.go").write_text("x\n", encoding="utf-8")
        res = self.kb("add", "n", "--kind", "reference", "--title", "t",
                      "--dir", "src")
        self.assertEqual(res.returncode, 1)
        self.assertFalse((self.proj / "src" / "00-overview.md").exists())

    def test_the_second_name_is_found_without_dir(self):
        (self.proj / "kb").mkdir()
        (self.proj / "kb" / "main.go").write_text("x\n", encoding="utf-8")
        self.kb("add", "note", "--kind", "reference", "--title", "t",
                "--dir", ".kb", expect=0)
        # A name nobody searches for is not an alternative: every later command
        # would need --dir, and nothing remembers it between sessions.
        self.assertIn("/.kb", self.kb("status", expect=0).stdout)

    def test_the_entry_point_still_goes_to_the_project_root(self):
        (self.proj / "kb").mkdir()
        self.kb("add", "note", "--kind", "reference", "--title", "t",
                "--dir", ".kb", expect=0)
        self.kb("route", expect=0)
        # The predicate that decides nested-or-flat was written out ten times
        # before the second name existed. One copy left unchanged would compute
        # the project as the notes directory and write the pointer inside it.
        self.assertTrue((self.proj / "AGENTS.md").is_file())
        self.assertFalse((self.proj / ".kb" / "AGENTS.md").exists())

    def test_local_excludes_the_name_actually_used(self):
        subprocess.run(["git", "init", "-q", "."], cwd=str(self.proj),
                       capture_output=True,
                       env={"HOME": str(self.home), "PATH": "/usr/bin:/bin"},
                       timeout=60)
        (self.proj / "kb").mkdir()
        self.kb("add", "note", "--kind", "reference", "--title", "t",
                "--dir", ".kb", expect=0)
        self.kb("local", expect=0)
        exclude = (self.proj / ".git" / "info" / "exclude").read_text(
            encoding="utf-8")
        self.assertIn("/.kb/", exclude)
        self.assertNotIn("/kb/", exclude.replace("/.kb/", ""))


if __name__ == "__main__":
    unittest.main(verbosity=2 if "-v" in sys.argv else 1)
