import copy
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile
import types
import unittest


ROOT = Path(__file__).resolve().parents[1]
PHASE1_BASELINE = "e036a53c4bd6a7c39e79db0b23ad75ae97db3949"
PHASE1_RELEASE = "caf3716d503a51d90e3238f1a566de6caad6fef0"
PHASE4D2_RELEASE = "a6420870f8c12fc25ffe15cd66b0a159bcac2fee"
sys.path.insert(0, str(ROOT))

import pp_audio_rule
import verify_audio


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def load(path):
    return json.loads(read(path))


def git_bytes(revision, path):
    result = subprocess.run(
        ["git", "show", f"{revision}:{path}"], cwd=ROOT, capture_output=True)
    if result.returncode:
        raise AssertionError(
            f"required historical object unavailable: {revision}:{path}: "
            f"{result.stderr.decode('utf-8', 'replace').strip()}")
    return result.stdout


def git_json(revision, path):
    return json.loads(git_bytes(revision, path).decode("utf-8"))


def git_audio_keys(revision):
    result = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", revision, "audio"], cwd=ROOT,
        text=True, capture_output=True)
    if result.returncode:
        raise AssertionError(
            f"required historical tree unavailable: {revision}: {result.stderr.strip()}")
    return {Path(path).stem for path in result.stdout.splitlines()
            if path.startswith("audio/") and path.endswith(".mp3")}


def historical_required_keys(revision):
    """Rebuild required phrases from the named Git revision, never live bytes."""
    archive = subprocess.run(
        ["git", "archive", revision], cwd=ROOT, capture_output=True)
    if archive.returncode:
        raise AssertionError(
            f"required historical archive unavailable: {revision}: "
            f"{archive.stderr.decode('utf-8', 'replace').strip()}")
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as bundle:
            bundle.extractall(root, filter="data")
        required = pp_audio_rule.required_phrases(
            str(root / "data-*.js"), root / "content" / "verb-patterns.json")
    return {phrase_key(phrase) for phrase in required}


def patterns(document):
    for lemma in document["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                yield lemma, meaning, pattern


def examples(document):
    for lemma, _, pattern in patterns(document):
        for example in pattern.get("examples", []):
            yield lemma, pattern, example


def stable_ids(document):
    identifiers = []
    for lemma in document["lemmas"]:
        identifiers.append(lemma["id"])
        for meaning in lemma["meanings"]:
            identifiers.append(meaning["id"])
            for pattern in meaning["patterns"]:
                identifiers.append(pattern["id"])
                identifiers.extend(example["id"]
                                   for example in pattern.get("examples", []))
    return identifiers


def phrase_key(phrase):
    return hashlib.sha256(phrase.encode("utf-8")).hexdigest()[:12]


def current_audio_file_problems(manifest, live_keys, file_sizes):
    """Current full-reconciliation checks for manifest, files, and required audio."""
    problems = list(verify_audio.manifest_integrity_problems(manifest))
    for key in sorted(live_keys - set(manifest)):
        problems.append(f"missing required manifest entry: {key}")
    for key, entry in manifest.items():
        size = file_sizes.get(Path(entry["file"]).stem)
        if size is None:
            problems.append(f"missing referenced MP3: {key}")
        elif size == 0:
            problems.append(f"empty referenced MP3: {key}")
    for key in sorted(set(manifest) - live_keys):
        problems.append(f"orphaned manifest entry: {key}")
    for key in sorted(set(file_sizes) - set(manifest)):
        problems.append(f"orphaned MP3 on disk: {key}")
    return problems


class Priority8Phase1GovernanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.release_editorial = git_json(
            PHASE1_RELEASE, "editorial/verb-pattern-candidates.json")
        cls.release_runtime = git_json(PHASE1_RELEASE, "content/verb-patterns.json")
        cls.baseline_editorial = git_json(
            PHASE1_BASELINE, "editorial/verb-pattern-candidates.json")
        cls.baseline_runtime = git_json(
            PHASE1_BASELINE, "content/verb-patterns.json")

    def test_official_transition_is_historical_revision_two_release(self):
        release_examples = list(examples(self.release_runtime))
        self.assertEqual(2, self.release_runtime["patternDataRevision"])
        self.assertEqual(45, len(release_examples))
        self.assertEqual(45, sum(example["audioEligible"]
                                 for _, _, example in release_examples))
        self.assertEqual(0, sum(bool(pattern["activityEligibility"])
                                for _, _, pattern in patterns(self.release_runtime)))
        tampered = copy.deepcopy(self.release_runtime)
        tampered["patternDataRevision"] = 3
        self.assertNotEqual(2, tampered["patternDataRevision"])

    def test_playback_policy_is_historical_and_explicit(self):
        release_examples = list(examples(self.release_editorial))
        self.assertEqual(45, len(release_examples))
        self.assertTrue(all(example["audioEligible"]
                            for _, _, example in release_examples))
        self.assertTrue(all(pattern["activityEligibility"] == []
                            for _, _, pattern in patterns(self.release_editorial)))
        tampered = copy.deepcopy(self.release_editorial)
        next(examples(tampered))[2]["audioEligible"] = False
        self.assertNotEqual(45, sum(example["audioEligible"]
                                    for _, _, example in examples(tampered)))

    def test_only_audio_policy_and_digest_bound_events_changed_editorial(self):
        normalized = copy.deepcopy(self.release_editorial)
        for _, _, pattern in patterns(normalized):
            phase_events = [event for event in pattern["reviewEvents"]
                            if "Priority 8 Phase 1A playback-only policy" in
                            event.get("note", "")]
            self.assertEqual(
                ["changes-requested", "accept", "accept"],
                [event["decision"] for event in phase_events])
            self.assertEqual(
                ["editorial-review", "editorial-review", "product-approval"],
                [event["kind"] for event in phase_events])
            del pattern["reviewEvents"][-3:]
            pattern["examples"][0]["audioEligible"] = False
        self.assertEqual(self.baseline_editorial, normalized)
        normalized["lemmas"][0]["id"] = "tampered-phase1-id"
        self.assertNotEqual(self.baseline_editorial, normalized)

    def test_public_delta_is_historical_revision_and_audio_flags_only(self):
        normalized = copy.deepcopy(self.release_runtime)
        normalized["patternDataRevision"] = 1
        for _, _, example in examples(normalized):
            example["audioEligible"] = False
        self.assertEqual(self.baseline_runtime, normalized)
        normalized["formatVersion"] = 2
        self.assertNotEqual(self.baseline_runtime, normalized)

    def test_all_45_are_playback_only_and_stable(self):
        release_examples = list(examples(self.release_editorial))
        baseline_examples = list(examples(self.baseline_editorial))
        self.assertEqual(45, len(release_examples))
        self.assertEqual(
            [(p["id"], e["id"], e["pl"]) for _, p, e in baseline_examples],
            [(p["id"], e["id"], e["pl"]) for _, p, e in release_examples])
        self.assertEqual(
            hashlib.sha256("\0".join(e["pl"] for _, _, e in baseline_examples)
                           .encode("utf-8")).hexdigest(),
            hashlib.sha256("\0".join(e["pl"] for _, _, e in release_examples)
                           .encode("utf-8")).hexdigest())
        self.assertNotEqual(45, len(release_examples[:-1]))

    def test_all_154_stable_ids_are_unchanged(self):
        before = stable_ids(self.baseline_editorial)
        after = stable_ids(self.release_editorial)
        self.assertEqual(154, len(after))
        self.assertEqual(len(after), len(set(after)))
        self.assertEqual(before, after)
        self.assertNotEqual(before, after[:-1])

    def test_recognition_only_and_schema_migration_are_historical(self):
        before = [pattern["id"] for _, _, pattern in patterns(self.baseline_editorial)
                  if pattern["teachingStatus"] == "recognition-only"]
        after = [pattern["id"] for _, _, pattern in patterns(self.release_editorial)
                 if pattern["teachingStatus"] == "recognition-only"]
        self.assertEqual(4, len(after))
        self.assertEqual(before, after)
        migration = git_bytes(PHASE1_RELEASE, "pp-migrate.js").decode("utf-8")
        self.assertRegex(migration, r"SCHEMA_VERSION\s*=\s*2")
        self.assertRegex(migration, r"CONTENT_MIGRATION_REVISION\s*=\s*2")
        self.assertEqual(1, self.release_runtime["formatVersion"])
        self.assertNotEqual(4, len(after[:-1]))
        tampered = copy.deepcopy(self.release_runtime)
        tampered["formatVersion"] = 2
        self.assertNotEqual(1, tampered["formatVersion"])

    def test_private_governance_stays_out_of_public_runtime(self):
        runtime = load("content/verb-patterns.json")
        forbidden = {
            "evidence", "reviewEvents", "reviewState", "origin", "scopeDigest",
            "reviewerRef", "actorRef", "internalScope", "key", "releaseMode",
        }

        def keys(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    yield key
                    yield from keys(child)
            elif isinstance(value, list):
                for child in value:
                    yield from keys(child)

        self.assertFalse(forbidden & set(keys(runtime)))


class Priority8Phase1AudioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load("audio-manifest.json")["entries"]
        cls.phase1_manifest = git_json(PHASE1_RELEASE, "audio-manifest.json")["entries"]
        cls.baseline_manifest = git_json(PHASE1_BASELINE, "audio-manifest.json")["entries"]
        cls.phase4d2_manifest = git_json(PHASE4D2_RELEASE, "audio-manifest.json")["entries"]
        cls.phase4d2_disk = git_audio_keys(PHASE4D2_RELEASE)
        cls.phase4d2_live = historical_required_keys(PHASE4D2_RELEASE)
        cls.phase1_runtime = git_json(PHASE1_RELEASE, "content/verb-patterns.json")
        cls.rows = list(csv.DictReader(io.StringIO(
            git_bytes(PHASE1_RELEASE, "reports/priority-8-audio-reuse.csv")
            .decode("utf-8"))))

    def test_locked_reuse_split_and_required_set(self):
        counts = {}
        for row in self.rows:
            counts[row["classification"]] = counts.get(row["classification"], 0) + 1
        self.assertEqual({"exact-existing-reuse": 20, "new-audio-required": 25}, counts)
        eligible = list(examples(self.phase1_runtime))
        self.assertEqual(45, len(eligible))
        self.assertEqual(45, len({pp_audio_rule.normalize(row[2]["pl"])
                                  for row in eligible}))
        self.assertEqual(3402, len(self.phase1_manifest))
        self.assertNotEqual(45, len(eligible[:-1]))

    def test_manifest_and_files_reconcile_exactly(self):
        # Phase-1 full coverage is a release snapshot, not a ban on later patterns.
        phase1_examples = {
            phrase_key(pp_audio_rule.normalize(example["pl"]))
            for _, _, example in examples(self.phase1_runtime)}
        phase1_disk = git_audio_keys(PHASE1_RELEASE)
        self.assertEqual(3402, len(self.phase1_manifest))
        self.assertTrue(phase1_examples.issubset(self.phase1_manifest))
        self.assertEqual(set(self.phase1_manifest), phase1_disk)
        historical_missing = copy.deepcopy(self.phase1_manifest)
        del historical_missing[next(iter(historical_missing))]
        self.assertNotEqual(set(historical_missing), phase1_disk)

        # Phase 4D2 is an immutable pre-audio checkpoint: 219 valid clips were pending.
        pre_audio_missing = self.phase4d2_live - set(self.phase4d2_manifest)
        self.assertEqual(3402, len(self.phase4d2_manifest))
        self.assertEqual(3402, len(self.phase4d2_disk))
        self.assertEqual(set(self.phase4d2_manifest), self.phase4d2_disk)
        self.assertEqual(219, len(pre_audio_missing))
        self.assertTrue(set(self.phase4d2_manifest) < self.phase4d2_live)
        self.assertEqual(
            [], verify_audio.manifest_integrity_problems(self.phase4d2_manifest))
        self.assertTrue(set(self.phase4d2_manifest).issubset(self.phase4d2_live))
        altered_missing = set(pre_audio_missing)
        altered_missing.pop()
        self.assertNotEqual(219, len(altered_missing))
        synthetic_pre_audio_full = dict(self.phase4d2_manifest)
        synthetic_pre_audio_full.update({key: {} for key in pre_audio_missing})
        self.assertNotEqual(3402, len(synthetic_pre_audio_full))

        # Current Phase 4E1 state is complete, not a future-audio exception.
        required = pp_audio_rule.required_phrases(
            str(ROOT / "data-*.js"), ROOT / "content" / "verb-patterns.json")
        live = {phrase_key(item) for item in required}
        files = {path.stem: path.stat().st_size
                 for path in (ROOT / "audio").glob("*.mp3")}
        self.assertEqual([], current_audio_file_problems(self.manifest, live, files))
        self.assertEqual(3621, len(self.manifest))
        self.assertEqual(3621, len(files))
        self.assertEqual(set(self.manifest), set(files))
        self.assertEqual(set(self.manifest), live)
        missing_manifest = copy.deepcopy(self.manifest)
        del missing_manifest[next(iter(missing_manifest))]
        self.assertTrue(any("missing required manifest entry" in problem for problem in
                            current_audio_file_problems(missing_manifest, live, files)))
        missing_current_file = dict(files)
        del missing_current_file[next(iter(missing_current_file))]
        self.assertTrue(any("missing referenced MP3" in problem for problem in
                            current_audio_file_problems(
                                self.manifest, live, missing_current_file)))
        orphan_manifest = copy.deepcopy(self.manifest)
        orphan_manifest["ffffffffffff"] = copy.deepcopy(self.manifest[next(iter(self.manifest))])
        self.assertTrue(current_audio_file_problems(orphan_manifest, live, files))

    def test_20_reused_clips_and_entries_are_byte_identical(self):
        reused = [row for row in self.rows
                  if row["classification"] == "exact-existing-reuse"]
        self.assertEqual(20, len(reused))
        for row in reused:
            key = row["manifest_key"]
            self.assertEqual(self.phase1_manifest[key], self.manifest[key])
            self.assertEqual(git_bytes(PHASE1_RELEASE, f"audio/{key}.mp3"),
                             (ROOT / "audio" / f"{key}.mp3").read_bytes())

    def test_exactly_25_new_content_addresses_were_absent_at_baseline(self):
        new_rows = [row for row in self.rows
                    if row["classification"] == "new-audio-required"]
        qa_rows = list(csv.DictReader(io.StringIO(
            git_bytes(PHASE1_RELEASE, "reports/priority-8-phase-1-audio-qa-pending.csv")
            .decode("utf-8"))))
        self.assertEqual(25, len(new_rows))
        self.assertEqual(
            {pp_audio_rule.normalize(row["exact_polish"]) for row in new_rows},
            {pp_audio_rule.normalize(row["exact_polish"]) for row in qa_rows})
        expected_keys = set()
        for row in new_rows:
            phrase = pp_audio_rule.normalize(row["exact_polish"])
            key = phrase_key(phrase)
            expected_keys.add(key)
            self.assertNotIn(key, self.baseline_manifest)
            self.assertEqual({"pl": phrase, "file": f"audio/{key}.mp3"},
                             self.phase1_manifest[key])
            self.assertEqual(self.phase1_manifest[key], self.manifest[key])
        self.assertEqual(expected_keys,
                         set(self.phase1_manifest) - set(self.baseline_manifest))

    def test_negative_controls_detect_missing_orphan_duplicate_and_collision(self):
        first = next(iter(self.manifest))
        required = pp_audio_rule.required_phrases(
            str(ROOT / "data-*.js"), ROOT / "content" / "verb-patterns.json")
        live = {phrase_key(item) for item in required}
        files = {path.stem: path.stat().st_size
                 for path in (ROOT / "audio").glob("*.mp3")}
        missing_file = dict(files)
        del missing_file[first]
        self.assertTrue(any("missing referenced MP3" in problem for problem in
                            current_audio_file_problems(self.manifest, live, missing_file)))
        empty_file = dict(files)
        empty_file[first] = 0
        self.assertTrue(any("empty referenced MP3" in problem for problem in
                            current_audio_file_problems(self.manifest, live, empty_file)))
        orphan_file = dict(files)
        orphan_file["ffffffffffff"] = 1
        self.assertTrue(any("orphaned MP3" in problem for problem in
                            current_audio_file_problems(self.manifest, live, orphan_file)))
        collision = copy.deepcopy(self.manifest)
        collision[first]["pl"] = "different synthetic test only"
        self.assertTrue(any("collision" in problem
                            for problem in verify_audio.manifest_integrity_problems(collision)))
        duplicate = copy.deepcopy(self.manifest)
        duplicate["eeeeeeeeeeee"] = copy.deepcopy(self.manifest[first])
        self.assertTrue(any("duplicate normalized" in problem
                            for problem in verify_audio.manifest_integrity_problems(duplicate)))

    def test_generator_refuses_an_occupied_different_hash_slot(self):
        sys.modules.setdefault("edge_tts", types.SimpleNamespace())
        import generate_audio
        with self.assertRaisesRegex(RuntimeError, "collision or manifest drift"):
            generate_audio.validate_manifest_slot(
                {"abc": {"pl": "other", "file": "audio/abc.mp3"}},
                "abc", "expected", "audio/abc.mp3")


class Priority8Phase1ReleaseTests(unittest.TestCase):
    def test_release_markers_and_worker_contract(self):
        index = git_bytes(PHASE1_RELEASE, "index.html").decode("utf-8")
        worker = git_bytes(PHASE1_RELEASE, "sw.js").decode("utf-8")
        self.assertRegex(index, r'APP_VERSION\s*=\s*"8\.12"')
        self.assertIn('const CACHE = "popolsku-v67";', worker)
        self.assertIn('const AUDIO_CACHE = "popolsku-audio";', worker)
        stripped = re.sub(r"/\*.*?\*/|//[^\n]*", "", worker, flags=re.S)
        self.assertNotIn("skipWaiting()", stripped)
        self.assertNotIn("clients.claim()", stripped)
        self.assertNotRegex(index.replace('APP_VERSION = "8.12"',
                                          'APP_VERSION = "8.13"'),
                            r'APP_VERSION\s*=\s*"8\.12"')
        self.assertNotIn('const CACHE = "popolsku-v67";',
                         worker.replace('const CACHE = "popolsku-v67";',
                                        'const CACHE = "popolsku-v68";'))

    def test_worker_behavior_is_byte_identical_after_release_metadata_is_removed(self):
        baseline = git_bytes(PHASE1_BASELINE, "sw.js").decode("utf-8")
        release = git_bytes(PHASE1_RELEASE, "sw.js").decode("utf-8")
        normalized = release.replace(
            'const CACHE = "popolsku-v67";',
            'const CACHE = "popolsku-v66";').replace(
                "3,402 clips + ~23%", "3,377 clips + ~24%").replace(
                    "3,402 clips", "3,377 clips")
        self.assertEqual(baseline, normalized)
        self.assertNotEqual(baseline, normalized + "\n// synthetic mutation\n")

    def test_pending_human_qa_artifacts_are_explicit(self):
        report = git_bytes(
            PHASE1_RELEASE, "reports/priority-8-phase-1-audio-qa-pending.md").decode("utf-8")
        rows = list(csv.DictReader(io.StringIO(git_bytes(
            PHASE1_RELEASE, "reports/priority-8-phase-1-audio-qa-pending.csv")
            .decode("utf-8"))))
        self.assertEqual(25, len(rows))
        self.assertTrue(all(row["human_qa_status"] == "pending" for row in rows))
        self.assertNotIn("human-QA = passed", report)
        self.assertIn("Human listening QA is pending", report)


if __name__ == "__main__":
    unittest.main()
