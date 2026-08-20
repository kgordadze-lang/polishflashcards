import copy
import csv
import dataclasses
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import types
import unittest


ROOT = Path(__file__).resolve().parents[1]
START = "e036a53c4bd6a7c39e79db0b23ad75ae97db3949"
sys.path.insert(0, str(ROOT))

import pp_audio_rule
import priority7_tooling
import verify_audio


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def load(path):
    return json.loads(read(path))


def git_bytes(path):
    return subprocess.check_output(
        ["git", "show", f"{START}:{path}"], cwd=ROOT)


def git_json(path):
    return json.loads(git_bytes(path).decode("utf-8"))


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


class Priority8Phase1GovernanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.editorial = load("editorial/verb-pattern-candidates.json")
        cls.runtime = load("content/verb-patterns.json")
        cls.baseline_editorial = git_json("editorial/verb-pattern-candidates.json")
        cls.baseline_runtime = git_json("content/verb-patterns.json")
        cls.context = priority7_tooling._load_context(
            str(ROOT / "editorial/priority-7-authoring-context.json"), str(ROOT))

    def test_official_transition_is_current_and_revision_two(self):
        result = subprocess.run(
            [sys.executable, "priority8_phase1_transition.py"], cwd=ROOT,
            text=True, capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr)
        evidence = json.loads(result.stdout)
        self.assertEqual(2, evidence["patternDataRevision"])
        self.assertEqual(45, evidence["eligibleExamples"])
        self.assertEqual(0, evidence["activityEligibilityNonempty"])
        self.assertFalse(evidence["sourceChangedByThisRun"])
        self.assertEqual([], priority7_tooling.validate_editorial(
            self.editorial, self.context))
        self.assertEqual([], priority7_tooling.validate_runtime(self.runtime))

    def test_playback_policy_is_explicit_and_revision_gated(self):
        self.assertTrue(self.context.pronunciation_playback_authorized)
        locked_context = dataclasses.replace(
            self.context, pronunciation_playback_authorized=False)
        editorial_issues = priority7_tooling.validate_editorial(
            self.editorial, locked_context)
        self.assertEqual(45, sum(
            issue.code == "AUDIO_NOT_AUTHORIZED" for issue in editorial_issues))
        revision_one = copy.deepcopy(self.runtime)
        revision_one["patternDataRevision"] = 1
        runtime_issues = priority7_tooling.validate_runtime(revision_one)
        self.assertEqual(45, sum(
            issue.code == "AUDIO_NOT_AUTHORIZED" for issue in runtime_issues))

    def test_only_audio_policy_and_digest_bound_events_changed_editorial(self):
        current = copy.deepcopy(self.editorial)
        for _, _, pattern in patterns(current):
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
        self.assertEqual(self.baseline_editorial, current)

    def test_public_delta_is_revision_and_audio_flags_only(self):
        current = copy.deepcopy(self.runtime)
        current["patternDataRevision"] = 1
        for _, _, example in examples(current):
            example["audioEligible"] = False
        self.assertEqual(self.baseline_runtime, current)

    def test_all_45_are_playback_only_and_stable(self):
        current_examples = list(examples(self.editorial))
        baseline_examples = list(examples(self.baseline_editorial))
        self.assertEqual(45, len(current_examples))
        self.assertTrue(all(row[2]["audioEligible"] for row in current_examples))
        self.assertTrue(all(pattern["activityEligibility"] == []
                            for _, _, pattern in patterns(self.editorial)))
        self.assertEqual(
            [(p["id"], e["id"], e["pl"]) for _, p, e in baseline_examples],
            [(p["id"], e["id"], e["pl"]) for _, p, e in current_examples])
        self.assertEqual(
            hashlib.sha256("\0".join(e["pl"] for _, _, e in baseline_examples)
                           .encode("utf-8")).hexdigest(),
            hashlib.sha256("\0".join(e["pl"] for _, _, e in current_examples)
                           .encode("utf-8")).hexdigest())

    def test_all_154_stable_ids_are_unchanged(self):
        before = stable_ids(self.baseline_editorial)
        after = stable_ids(self.editorial)
        self.assertEqual(154, len(after))
        self.assertEqual(len(after), len(set(after)))
        self.assertEqual(before, after)

    def test_recognition_only_and_schema_migration_are_unchanged(self):
        before = [pattern["id"] for _, _, pattern in patterns(
            self.baseline_editorial) if pattern["teachingStatus"] == "recognition-only"]
        after = [pattern["id"] for _, _, pattern in patterns(
            self.editorial) if pattern["teachingStatus"] == "recognition-only"]
        self.assertEqual(4, len(after))
        self.assertEqual(before, after)
        migration = read("pp-migrate.js")
        self.assertRegex(migration, r"SCHEMA_VERSION\s*=\s*2")
        self.assertRegex(migration, r"CONTENT_MIGRATION_REVISION\s*=\s*2")
        self.assertEqual(1, self.runtime["formatVersion"])

    def test_private_governance_stays_out_of_public_runtime(self):
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

        self.assertFalse(forbidden & set(keys(self.runtime)))


class Priority8Phase1AudioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = load("content/verb-patterns.json")
        cls.manifest_doc = load("audio-manifest.json")
        cls.manifest = cls.manifest_doc["entries"]
        cls.baseline_manifest = git_json("audio-manifest.json")["entries"]
        cls.rows = list(csv.DictReader(io.StringIO(
            read("reports/priority-8-audio-reuse.csv"))))

    def test_locked_reuse_split_and_required_set(self):
        counts = {}
        for row in self.rows:
            counts[row["classification"]] = counts.get(row["classification"], 0) + 1
        self.assertEqual({"exact-existing-reuse": 20, "new-audio-required": 25}, counts)
        eligible = pp_audio_rule.verb_pattern_audio_examples(
            ROOT / "content" / "verb-patterns.json")
        self.assertEqual(45, len(eligible))
        self.assertEqual(45, len({pp_audio_rule.normalize(row["pl"]) for row in eligible}))
        required = pp_audio_rule.required_phrases(
            str(ROOT / "data-*.js"), ROOT / "content" / "verb-patterns.json")
        self.assertEqual(3402, len(required))
        self.assertEqual(len(required), len(set(required)))

    def test_manifest_and_files_reconcile_exactly(self):
        required = pp_audio_rule.required_phrases(
            str(ROOT / "data-*.js"), ROOT / "content" / "verb-patterns.json")
        live = {hashlib.sha256(item.encode("utf-8")).hexdigest()[:12]
                for item in required}
        disk = {path.stem for path in (ROOT / "audio").glob("*.mp3")}
        self.assertEqual(3402, len(self.manifest))
        self.assertEqual(live, set(self.manifest))
        self.assertEqual(live, disk)
        self.assertEqual([], verify_audio.manifest_integrity_problems(self.manifest))
        self.assertTrue(all((ROOT / entry["file"]).stat().st_size > 0
                            for entry in self.manifest.values()))

    def test_20_reused_clips_and_entries_are_byte_identical(self):
        reused = [row for row in self.rows
                  if row["classification"] == "exact-existing-reuse"]
        self.assertEqual(20, len(reused))
        for row in reused:
            key = row["manifest_key"]
            self.assertEqual(self.baseline_manifest[key], self.manifest[key])
            self.assertEqual(git_bytes(f"audio/{key}.mp3"),
                             (ROOT / "audio" / f"{key}.mp3").read_bytes())

    def test_exactly_25_new_content_addresses_were_absent_at_baseline(self):
        new_rows = [row for row in self.rows
                    if row["classification"] == "new-audio-required"]
        qa_rows = list(csv.DictReader(io.StringIO(
            read("reports/priority-8-phase-1-audio-qa-pending.csv"))))
        self.assertEqual(25, len(new_rows))
        self.assertEqual(
            {pp_audio_rule.normalize(row["exact_polish"]) for row in new_rows},
            {pp_audio_rule.normalize(row["exact_polish"]) for row in qa_rows})
        expected_keys = set()
        for row in new_rows:
            phrase = pp_audio_rule.normalize(row["exact_polish"])
            key = hashlib.sha256(phrase.encode("utf-8")).hexdigest()[:12]
            expected_keys.add(key)
            self.assertNotIn(key, self.baseline_manifest)
            self.assertEqual({"pl": phrase, "file": f"audio/{key}.mp3"},
                             self.manifest[key])
        self.assertEqual(expected_keys,
                         set(self.manifest) - set(self.baseline_manifest))

    def test_negative_controls_detect_missing_orphan_duplicate_and_collision(self):
        manifest = copy.deepcopy(self.manifest)
        first = next(iter(manifest))
        missing = copy.deepcopy(manifest)
        del missing[first]
        self.assertNotEqual(set(manifest), set(missing))
        orphan = copy.deepcopy(manifest)
        orphan["ffffffffffff"] = {
            "pl": "synthetic test only", "file": "audio/ffffffffffff.mp3"}
        self.assertTrue(verify_audio.manifest_integrity_problems(orphan))
        collision = copy.deepcopy(manifest)
        collision[first]["pl"] = "different synthetic test only"
        self.assertTrue(any("collision" in problem
                            for problem in verify_audio.manifest_integrity_problems(collision)))
        duplicate = copy.deepcopy(manifest)
        duplicate["eeeeeeeeeeee"] = copy.deepcopy(manifest[first])
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
        index = read("index.html")
        worker = read("sw.js")
        self.assertRegex(index, r'APP_VERSION\s*=\s*"8\.12"')
        self.assertIn('const CACHE = "popolsku-v67";', worker)
        self.assertIn('const AUDIO_CACHE = "popolsku-audio";', worker)
        self.assertNotIn("skipWaiting()", re.sub(r"/\*.*?\*/|//[^\n]*", "", worker,
                                                 flags=re.S))
        self.assertNotIn("clients.claim()", re.sub(r"/\*.*?\*/|//[^\n]*", "", worker,
                                                   flags=re.S))

    def test_worker_behavior_is_byte_identical_after_release_metadata_is_removed(self):
        baseline = git_bytes("sw.js").decode("utf-8")
        current = read("sw.js")
        normalized = current.replace(
            'const CACHE = "popolsku-v67";',
            'const CACHE = "popolsku-v66";').replace(
                "3,402 clips + ~23%", "3,377 clips + ~24%").replace(
                    "3,402 clips", "3,377 clips")
        self.assertEqual(baseline, normalized)

    def test_pending_human_qa_artifacts_are_explicit(self):
        report = read("reports/priority-8-phase-1-audio-qa-pending.md")
        rows = list(csv.DictReader(io.StringIO(
            read("reports/priority-8-phase-1-audio-qa-pending.csv"))))
        self.assertEqual(25, len(rows))
        self.assertTrue(all(row["human_qa_status"] == "pending" for row in rows))
        self.assertNotIn("human-QA = passed", report)
        self.assertIn("Human listening QA is pending", report)


if __name__ == "__main__":
    unittest.main()
