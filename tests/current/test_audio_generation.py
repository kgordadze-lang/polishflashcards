"""Maintained current audio regressions extracted from the Phase 4E1 test."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from pp_audio_rule import normalize, verb_pattern_audio_examples
from verify_audio import manifest_integrity_problems, phrase_hash


ROOT = Path(__file__).resolve().parents[2]


class CurrentAudioGenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        manifest = json.loads(
            (ROOT / "audio-manifest.json").read_text(encoding="utf-8"))
        cls.entries = manifest["entries"]
        cls.examples = verb_pattern_audio_examples(
            ROOT / "content/verb-patterns.json")
        cls.example_by_hash = {
            phrase_hash(normalize(example["pl"])): example
            for example in cls.examples
        }
        cls.audio_files = {
            path.stem: path for path in (ROOT / "audio").glob("*.mp3")}

    def test_manifest_and_disk_are_a_bijection(self):
        self.assertEqual(set(self.entries), set(self.audio_files))
        self.assertTrue(self.entries)
        self.assertTrue(all(path.stat().st_size > 0 for path in self.audio_files.values()))

    def test_every_pronunciation_example_has_one_content_addressed_clip(self):
        self.assertEqual(len(self.examples), len(self.example_by_hash))
        self.assertTrue(self.examples)
        for key, example in self.example_by_hash.items():
            with self.subTest(example=example["pl"]):
                self.assertIn(key, self.entries)
                self.assertEqual(f"audio/{key}.mp3", self.entries[key]["file"])
                self.assertGreater(self.audio_files[key].stat().st_size, 0)

    def test_manifest_content_addressing_is_valid(self):
        self.assertEqual([], manifest_integrity_problems(self.entries))
        for key, entry in self.entries.items():
            self.assertEqual(key, phrase_hash(normalize(entry["pl"])))
            self.assertEqual(f"audio/{key}.mp3", entry["file"])

    def test_generator_retains_collision_and_drift_guards(self):
        generator = (ROOT / "generate_audio.py").read_text(encoding="utf-8")
        self.assertIn("def validate_manifest_slot", generator)
        self.assertIn("content-hash collision or manifest drift", generator)

    def test_audio_cache_capacity_covers_the_current_manifest(self):
        worker = (ROOT / "sw.js").read_text(encoding="utf-8")
        match = re.search(r"AUDIO_CACHE_MAX_ENTRIES\s*=\s*(\d+)", worker)
        self.assertIsNotNone(match)
        self.assertGreaterEqual(int(match.group(1)), len(self.entries))


if __name__ == "__main__":
    unittest.main()
