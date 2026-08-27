\
"""Focused regression coverage for Priority 8 Phase 4E1 audio generation."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import unittest
from pathlib import Path

from pp_audio_rule import normalize, verb_pattern_audio_examples
from verify_audio import manifest_integrity_problems, phrase_hash


ROOT = Path(__file__).resolve().parent.parent
BASELINE = "a6420870f8c12fc25ffe15cd66b0a159bcac2fee"
REUSED_TEXTS = (
    "Idę do sklepu.",
    "Kupiłem jej kwiaty.",
    "Kupiłem prezenty dla całej rodziny.",
    "Wyszedłem z domu.",
    "Wyjście z nałogu wymaga silnej woli.",
)


def git_bytes(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{BASELINE}:{path}"], cwd=ROOT)


def git_text(path: str) -> str:
    return git_bytes(path).decode("utf-8")


class Priority8Phase4E1AudioGenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "audio-manifest.json").read_text(encoding="utf-8"))
        cls.entries = cls.manifest["entries"]
        cls.baseline_entries = json.loads(git_text("audio-manifest.json"))["entries"]
        cls.examples = verb_pattern_audio_examples()
        cls.example_by_hash = {
            phrase_hash(normalize(example["pl"])): example for example in cls.examples
        }
        cls.audio_files = {path.stem: path for path in (ROOT / "audio").glob("*.mp3")}

    def test_counts_coverage_and_manifest_disk_bijection(self):
        self.assertEqual(269, len(self.examples))
        self.assertEqual(269, len(self.example_by_hash))
        self.assertEqual(3621, len(self.entries))
        self.assertEqual(3621, len(self.audio_files))
        self.assertEqual(set(self.entries), set(self.audio_files))
        for key, example in self.example_by_hash.items():
            self.assertIn(key, self.entries, example["pl"])
            self.assertGreater(self.audio_files[key].stat().st_size, 0, example["pl"])

    def test_exact_baseline_preservation_and_new_p8_set(self):
        self.assertEqual(3402, len(self.baseline_entries))
        self.assertTrue(self.baseline_entries.items() <= self.entries.items())
        new_keys = set(self.entries) - set(self.baseline_entries)
        expected_new_keys = set(self.example_by_hash) - set(self.baseline_entries)
        self.assertEqual(219, len(new_keys))
        self.assertEqual(expected_new_keys, new_keys)
        baseline_audio = {}
        for line in subprocess.check_output(
            ["git", "ls-tree", "-r", "--format=%(objectname) %(path)", BASELINE, "audio"],
            cwd=ROOT, text=True,
        ).splitlines():
            blob, path = line.split(" ", 1)
            baseline_audio[path] = blob
        self.assertEqual(3402, len(baseline_audio))
        actual_blobs = subprocess.check_output(
            ["git", "hash-object", "--stdin-paths"], cwd=ROOT, text=True,
            input="".join(f"{path}\n" for path in sorted(baseline_audio)),
        ).splitlines()
        self.assertEqual(
            [baseline_audio[path] for path in sorted(baseline_audio)], actual_blobs
        )

    def test_reuses_are_original_and_new_files_are_valid(self):
        for text in REUSED_TEXTS:
            key = phrase_hash(normalize(text))
            path = self.entries[key]["file"]
            self.assertEqual(git_bytes(path), (ROOT / path).read_bytes(), text)
        new_keys = set(self.entries) - set(self.baseline_entries)
        self.assertEqual(219, len(new_keys))
        self.assertTrue(all(self.audio_files[key].stat().st_size > 0 for key in new_keys))
        for key in new_keys:
            entry = self.entries[key]
            self.assertEqual(key, phrase_hash(normalize(entry["pl"])))
            self.assertEqual(f"audio/{key}.mp3", entry["file"])

    def test_integrity_and_release_locks(self):
        self.assertEqual([], manifest_integrity_problems(self.entries))
        self.assertEqual(
            "66a02804b8ea1bb2b8a4ec7260855018db0e32f7a0623b78dc8b62fd58801ff1",
            hashlib.sha256((ROOT / "content/verb-patterns.json").read_bytes()).hexdigest(),
        )
        self.assertEqual(0, subprocess.call(
            ["git", "diff", "--quiet", BASELINE, "--", "content/verb-patterns.json"], cwd=ROOT))
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        worker = (ROOT / "sw.js").read_text(encoding="utf-8")
        generator = (ROOT / "generate_audio.py").read_text(encoding="utf-8")
        self.assertIn('const APP_VERSION = "8.13";', index)
        self.assertIn('const CACHE = "popolsku-v68";', worker)
        self.assertIn('const AUDIO_CACHE = "popolsku-audio";', worker)
        self.assertIn('const AUDIO_CACHE_MAX_ENTRIES = 4200;', worker)
        self.assertIn("def validate_manifest_slot", generator)
        self.assertIn("content-hash collision or manifest drift", generator)

    def test_human_qa_queue_is_complete_and_pending(self):
        with (ROOT / "editorial/priority-8-phase4e1-audio-qa.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(219, len(rows))
        self.assertEqual(list(range(1, 220)), [int(row["qaOrder"]) for row in rows])
        self.assertEqual({"PENDING"}, {row["humanQaStatus"] for row in rows})
        self.assertEqual({"PASS"}, {row["technicalStatus"] for row in rows})
        self.assertTrue(all(not row["humanQaNote"] for row in rows))
        self.assertEqual(
            set(self.entries) - set(self.baseline_entries), {row["hash"] for row in rows}
        )
        report = (ROOT / "reports/priority-8-phase-4e1-audio-generation.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("HUMAN LISTENING QA IS PENDING", report)
        self.assertNotIn("HUMAN LISTENING QA IS COMPLETE", report)


if __name__ == "__main__":
    unittest.main()
