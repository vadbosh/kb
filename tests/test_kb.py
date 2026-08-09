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

    def write_note(self, root, name, kind="reference", title="t",
                   updated=None, body="text", supersedes=None):
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

    def test_both_languages_carry_the_same_headings(self):
        for lang in ("ru", "en"):
            shape = kb_cli.STRINGS[lang]["shape"]
            self.assertEqual(set(shape), set(kb_cli.KINDS),
                             f"{lang}: a kind with no headings gets none written")
            for kind, heads in shape.items():
                self.assertTrue(heads, f"{lang}/{kind}: empty skeleton")


# ── the generated index ─────────────────────────────────────────────────────

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


if __name__ == "__main__":
    unittest.main(verbosity=2 if "-v" in sys.argv else 1)
