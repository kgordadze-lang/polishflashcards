"""Focused tests for the maintained public Verb Patterns validator."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from verb_patterns_runtime_validator import validate_runtime


ROOT = Path(__file__).resolve().parents[2]
RUNTIME = json.loads(
    (ROOT / "content/verb-patterns.json").read_text(encoding="utf-8"))


def codes(document):
    return {issue.code for issue in validate_runtime(document)}


class CurrentVerbPatternsRuntimeValidatorTests(unittest.TestCase):
    def test_canonical_runtime_is_valid(self):
        self.assertEqual([], validate_runtime(RUNTIME))

    def test_wrong_format_version_fails(self):
        document = copy.deepcopy(RUNTIME)
        document["formatVersion"] += 1
        self.assertIn("FORMAT_VERSION", codes(document))

    def test_private_editorial_field_fails_at_any_depth(self):
        document = copy.deepcopy(RUNTIME)
        document["lemmas"][0]["reviewState"] = "approved"
        self.assertIn("RUNTIME_PRIVATE_FIELD", codes(document))

    def test_duplicate_global_id_fails(self):
        document = copy.deepcopy(RUNTIME)
        document["lemmas"][0]["meanings"][0]["id"] = document["lemmas"][0]["id"]
        self.assertIn("ID_GLOBAL_DUPLICATE", codes(document))

    def test_dangling_aspect_partner_fails(self):
        document = copy.deepcopy(RUNTIME)
        document["lemmas"][0]["aspectPartnerIds"] = [
            "vp-l-not-a-real-lemma-000000000000"]
        self.assertIn("ASPECT_LINK_DANGLING", codes(document))

    def test_audio_rule_no_longer_imports_historical_tooling(self):
        source = (ROOT / "pp_audio_rule.py").read_text(encoding="utf-8")
        self.assertNotIn("priority7_tooling", source)
        self.assertIn(
            "from verb_patterns_runtime_validator import validate_runtime", source)


if __name__ == "__main__":
    unittest.main()
