"""Moving live-progress gate; Batch 2-7 update its phase and batch boundary.

Batch 7 is the final authoring batch: all seven batches are complete, every
frozen full-pattern lemma now carries candidateContent, and the future-empty
set is empty. That does not mean Phase 4B is approved - the final 68-lemma
reconciliation still follows independent Batch 7 review.
"""

import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

import sys

sys.path.insert(0, str(ROOT))

import validate_priority8_staging as validator  # noqa: E402


STAGING_PATH = ROOT / "editorial/priority-8-phase4-staging.json"
RULES_PATH = ROOT / "tests/fixtures/priority8_phase4b_authoring_rules.json"
EMPTY_CONTENT = {"meanings": [], "patterns": [], "examples": []}
RECONCILIATION_RULE_IDS = {
    "p8-4b-zapominac-exact-pattern-shapes",
    "p8-4b-klocic-sie-exact-pattern-shapes",
}
CURRENT_AUTHORED = tuple(
    item for batch in validator.AUTHORING_BATCHES[:7] for item in batch
)
CURRENT_FUTURE = tuple(
    item for batch in validator.AUTHORING_BATCHES[7:] for item in batch
)


def walk(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


class Priority8Phase4BProgressTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(STAGING_PATH.read_text(encoding="utf-8"))
        cls.by_order = {
            item["verificationOrder"]: item for item in cls.data["lemmas"]
        }

    def test_live_staging_validates(self):
        self.assertEqual([], validator.validate_data(self.data))

    def test_current_envelope_and_full_pattern_count(self):
        self.assertEqual(1, self.data["stagingSchemaVersion"])
        self.assertEqual(8, self.data["stagingRevision"])
        self.assertEqual("4B7", self.data["phaseStep"])
        self.assertEqual(68, self.data["frozenFullPatternCount"])
        self.assertEqual(68, len(self.data["lemmas"]))

    def test_exact_current_authored_and_future_empty_boundaries(self):
        authored = tuple(
            (item["verificationOrder"], item["canonicalLemma"])
            for item in self.data["lemmas"]
            if item["candidateContent"] != EMPTY_CONTENT
        )
        self.assertEqual(CURRENT_AUTHORED, authored)
        self.assertEqual(68, len(CURRENT_AUTHORED))
        self.assertEqual(0, len(CURRENT_FUTURE))
        self.assertEqual(70, CURRENT_AUTHORED[-1][0])
        self.assertEqual(7, len(validator.AUTHORING_BATCHES))
        for order, lemma in CURRENT_FUTURE:
            with self.subTest(order=order, lemma=lemma):
                item = self.by_order[order]
                self.assertEqual(lemma, item["canonicalLemma"])
                self.assertEqual(EMPTY_CONTENT, item["candidateContent"])

    def test_all_current_review_statuses_are_draft(self):
        self.assertEqual(
            Counter({"draft": 68}),
            Counter(item["stagingReviewStatus"] for item in self.data["lemmas"]),
        )

    def test_current_authored_totals(self):
        authored_records = [
            self.by_order[order] for order, _ in CURRENT_AUTHORED
        ]
        totals = tuple(
            sum(len(item["candidateContent"][collection])
                for item in authored_records)
            for collection in ("meanings", "patterns", "examples")
        )
        self.assertEqual((95, 224, 224), totals)

    def test_current_teaching_status_split_and_recognition_only_control(self):
        patterns = [
            (item["canonicalLemma"], pattern)
            for item in self.data["lemmas"]
            for pattern in item["candidateContent"]["patterns"]
        ]
        self.assertEqual(
            Counter({"active-production": 222, "recognition-only": 2}),
            Counter(pattern["teachingStatus"] for _, pattern in patterns),
        )
        recognition_only = {
            (lemma, pattern["meaningKeyRef"], pattern["candidatePatternKey"])
            for lemma, pattern in patterns
            if pattern["teachingStatus"] == "recognition-only"
        }
        self.assertEqual(
            {
                ("pozwalać", "inanimate-enabling", "zeby-enabling"),
                ("wymagać", "situation-requires-content", "zeby-clause"),
            },
            recognition_only,
        )

    def test_current_reconciliation_guard_ids_are_present(self):
        registry = json.loads(RULES_PATH.read_text(encoding="utf-8"))
        rule_ids = {rule["ruleId"] for rule in registry["rules"]}
        self.assertTrue(RECONCILIATION_RULE_IDS <= rule_ids)
        self.assertEqual(2, registry["registryVersion"])
        self.assertGreaterEqual(len(registry["rules"]), 74)

    def test_no_production_or_canonical_runtime_ids(self):
        for key, value in walk(self.data):
            self.assertNotIn(key.lower(), validator.PRODUCTION_ID_FIELDS)
            if isinstance(value, str):
                self.assertIsNone(validator.PRODUCTION_ID_RE.search(value), value)

    def test_exact_metadata_only_aspect_relationships(self):
        partners = {
            item["canonicalLemma"]: item["metadataAspectPartner"]
            for item in self.data["lemmas"]
            if "metadataAspectPartner" in item
        }
        self.assertEqual(validator.EXPECTED_METADATA_PARTNERS, partners)
        names = {item["canonicalLemma"] for item in self.data["lemmas"]}
        self.assertTrue(validator.METADATA_IDENTITIES.isdisjoint(names))

    def test_all_binding_and_global_constraints_remain_present(self):
        expected_bindings = {
            item["canonicalLemma"]: item["bindingConstraints"]
            for item in validator._expected_lemmas()
        }
        self.assertEqual(
            21,
            sum(bool(value) for value in expected_bindings.values()),
        )
        self.assertEqual(
            expected_bindings,
            {item["canonicalLemma"]: item["bindingConstraints"]
             for item in self.data["lemmas"]},
        )
        self.assertEqual(
            validator._expected_global_constraints(),
            self.data["globalConstraints"],
        )


if __name__ == "__main__":
    unittest.main()
