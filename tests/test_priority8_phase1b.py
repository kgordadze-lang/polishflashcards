import csv
import hashlib
from collections import Counter
from datetime import datetime
from pathlib import Path
import unittest

import pp_audio_rule


ROOT = Path(__file__).resolve().parents[1]
COMPLETED = ROOT / "reports/priority-8-phase-1b-human-audio-qa.csv"
PENDING = ROOT / "reports/priority-8-phase-1-audio-qa-pending.csv"
MATCH_FIELDS = (
    "example_id",
    "lemma",
    "pattern_id",
    "exact_polish",
    "manifest_key",
    "mp3_path",
    "tts_risk",
    "special_issue",
)


def rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class Priority8Phase1BHumanAudioQATests(unittest.TestCase):
    def test_completed_record_is_25_pass_and_matches_pending_queue(self):
        completed = rows(COMPLETED)
        pending = {row["example_id"]: row for row in rows(PENDING)}

        self.assertEqual(25, len(completed))
        self.assertEqual(25, len({row["example_id"] for row in completed}))
        self.assertEqual(Counter({"PASS": 25}), Counter(
            row["human_qa_status"] for row in completed))
        self.assertEqual(set(pending), {
            row["example_id"] for row in completed})

        for row in completed:
            self.assertTrue(row["reviewed_at"])
            datetime.fromisoformat(row["reviewed_at"])
            self.assertEqual(
                tuple(pending[row["example_id"]][field]
                      for field in MATCH_FIELDS),
                tuple(row[field] for field in MATCH_FIELDS),
            )
            normalized = pp_audio_rule.normalize(row["exact_polish"])
            key = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]
            self.assertEqual(key, row["manifest_key"])
            self.assertEqual(f"audio/{key}.mp3", row["mp3_path"])
            clip = ROOT / row["mp3_path"]
            self.assertTrue(clip.is_file())
            self.assertGreater(clip.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
