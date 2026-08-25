import hashlib
import json
import re
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

import sys

sys.path.insert(0, str(ROOT))

import priority7_tooling as tooling  # noqa: E402
import validate_priority8_staging as validator  # noqa: E402


STAGING_PATH = ROOT / "editorial/priority-8-phase4-staging.json"
BATCH_2 = tuple(lemma for _, lemma in validator.AUTHORING_BATCHES[1])
BATCH_2_DIGEST_FIELDS = (
    "verificationOrder",
    "canonicalLemma",
    "aspect",
    "phase3Disposition",
    "phase3Evidence",
    "bindingConstraints",
    "candidateContent",
    "metadataAspectPartner",
)
BATCH_2_APPROVED_DIGEST = (
    "87c07469634cc039e68e2f52a5f306a05ca7753e1e4d328d58542c4b549e2f82"
)
ALLOWED_REVIEW_STATUSES = {
    "draft", "independently-reviewed", "human-approved",
}
PRODUCTION_ID_KEY_NAMES = validator.PRODUCTION_ID_FIELDS
ORDER_NUMBER_RE = re.compile(r"(?:^|-)0*[1-9][0-9]*(?:-|$)")


def record(data, lemma):
    return next(item for item in data["lemmas"]
                if item["canonicalLemma"] == lemma)


def walk(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def batch_digest(records):
    projection = [
        {field: item[field] for field in BATCH_2_DIGEST_FIELDS if field in item}
        for item in records
    ]
    canonical = json.dumps(
        projection,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


class Priority8Phase4B2Batch02Tests(unittest.TestCase):
    """Historical regression test for approved Batch 2 authoring.

    Follows the Batch 1 future-safe architecture described in
    reports/priority-8-phase-4b-test-lifecycle.md: this test pins the
    approved Batch 2 content digest and does not assert phaseStep,
    stagingRevision, or corpus-wide draft/future-empty boundaries, so later
    Batch 3-7 authoring cannot invalidate it. Those moving assertions belong
    to tests/test_priority8_phase4b_progress.py.
    """

    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(STAGING_PATH.read_text(encoding="utf-8"))
        cls.batch_records = [record(cls.data, lemma) for lemma in BATCH_2]

    def test_live_staging_validates(self):
        self.assertEqual([], validator.validate_data(self.data))

    def test_frozen_corpus_and_exact_batch_membership(self):
        self.assertEqual(68, self.data["frozenFullPatternCount"])
        self.assertEqual(
            validator.AUTHORING_BATCHES[1],
            tuple(
                (item["verificationOrder"], item["canonicalLemma"])
                for item in self.batch_records
            ),
        )
        self.assertEqual(
            (11, 12, 13, 14, 15, 16, 18, 19, 20, 21),
            tuple(item["verificationOrder"] for item in self.batch_records),
        )
        self.assertNotIn(
            17, [item["verificationOrder"] for item in self.batch_records])

    def test_exact_approved_batch_content_digest(self):
        self.assertEqual(BATCH_2_APPROVED_DIGEST,
                         batch_digest(self.batch_records))

    def test_batch_review_statuses_use_allowed_lifecycle_values(self):
        self.assertTrue(all(
            item["stagingReviewStatus"] in ALLOWED_REVIEW_STATUSES
            for item in self.batch_records
        ))

    def test_authored_counts_and_every_meaning_has_a_pattern(self):
        for item in self.batch_records:
            content = item["candidateContent"]
            self.assertGreaterEqual(len(content["meanings"]), 1)
            self.assertGreaterEqual(len(content["patterns"]), 1)
            meaning_keys = {
                meaning["candidateMeaningKey"]
                for meaning in content["meanings"]
            }
            pattern_meanings = {
                pattern["meaningKeyRef"] for pattern in content["patterns"]
            }
            self.assertTrue(meaning_keys <= pattern_meanings)
        self.assertEqual(12, sum(
            len(item["candidateContent"]["meanings"])
            for item in self.batch_records))
        self.assertEqual(28, sum(
            len(item["candidateContent"]["patterns"])
            for item in self.batch_records))
        self.assertEqual(28, sum(
            len(item["candidateContent"]["examples"])
            for item in self.batch_records))

    def test_ownership_scopes_and_one_example_per_pattern(self):
        for item in self.batch_records:
            lemma = item["canonicalLemma"]
            content = item["candidateContent"]
            meaning_keys = [
                meaning["candidateMeaningKey"] for meaning in content["meanings"]
            ]
            self.assertEqual(len(meaning_keys), len(set(meaning_keys)), lemma)
            pattern_owners = [
                (pattern["meaningKeyRef"], pattern["candidatePatternKey"])
                for pattern in content["patterns"]
            ]
            self.assertEqual(len(pattern_owners), len(set(pattern_owners)), lemma)
            self.assertTrue(all(owner[0] in meaning_keys for owner in pattern_owners))
            example_owners = [
                (example["meaningKeyRef"], example["patternKeyRef"])
                for example in content["examples"]
            ]
            self.assertEqual(Counter(pattern_owners), Counter(example_owners), lemma)
            example_keys = [
                (example["meaningKeyRef"], example["patternKeyRef"],
                 example["candidateExampleKey"])
                for example in content["examples"]
            ]
            self.assertEqual(len(example_keys), len(set(example_keys)), lemma)
            self.assertTrue(all(
                owner in pattern_owners for owner in example_owners), lemma)
            self.assertTrue(all(
                not ORDER_NUMBER_RE.search(key)
                for _, _, key in example_keys), lemma)

    def test_candidate_origins_are_truthful_and_resolve_when_reused(self):
        examples = [
            (item["canonicalLemma"], example)
            for item in self.batch_records
            for example in item["candidateContent"]["examples"]
        ]
        reuse = []
        for lemma, example in examples:
            origin = example["candidateOrigin"]
            if origin["kind"] == "editorial-generated":
                self.assertEqual({"kind"}, set(origin), lemma)
            else:
                self.assertEqual("repository-reuse", origin["kind"], lemma)
                self.assertEqual({"kind", "repositorySource"}, set(origin), lemma)
                reuse.append((lemma, example, origin["repositorySource"]))
        # Batch 2's repository search found no eligible exact-pattern match
        # (see reports/priority-8-phase-4b2-batch-02-authoring.md); every
        # candidate is editorial-generated.
        self.assertEqual(0, len(reuse))
        index = tooling.repository_index_from_root(ROOT)
        self.assertEqual([], index.issues)
        for lemma, example, source in reuse:
            entity = index.get(source["id"])
            self.assertIsNotNone(entity, lemma)
            self.assertEqual(source["kind"], entity.kind, lemma)
            self.assertIn(source["field"], entity.record, lemma)
            self.assertEqual(example["pl"], entity.record[source["field"]], lemma)

    def test_examples_are_unique_and_generated_examples_are_not_quiet_reuse(self):
        examples = [
            example for item in self.batch_records
            for example in item["candidateContent"]["examples"]
        ]
        polish = [example["pl"] for example in examples]
        english = [example["en"] for example in examples]
        self.assertEqual(len(polish), len(set(polish)))
        self.assertEqual(len(english), len(set(english)))
        index = tooling.repository_index_from_root(ROOT)
        self.assertEqual([], index.issues)
        source_fields = {"card": {"pl", "ex"}, "drill": {"prompt", "answer"}}
        for example in examples:
            if example["candidateOrigin"]["kind"] != "editorial-generated":
                continue
            matches = [
                (entity.entity_id, field)
                for entity in index.entities.values()
                for field in source_fields.get(entity.kind, set())
                if entity.record.get(field) == example["pl"]
            ]
            self.assertEqual([], matches, example["pl"])

    def test_no_production_ids_or_id_fields_exist(self):
        for item in self.batch_records:
            for key, value in walk(item):
                self.assertNotIn(key.lower(), PRODUCTION_ID_KEY_NAMES)
                if isinstance(value, str):
                    self.assertIsNone(
                        validator.PRODUCTION_ID_RE.search(value), value)

    def test_metadata_only_relationship_integrity(self):
        zaczac = record(self.data, "zacząć")
        self.assertEqual(
            validator.EXPECTED_METADATA_PARTNERS["zacząć"],
            zaczac["metadataAspectPartner"],
        )
        names = {item["canonicalLemma"] for item in self.data["lemmas"]}
        self.assertNotIn("zaczynać", names)

    def test_zapominac_interrogative_reconciliation_is_pinned(self):
        zapominac = record(self.data, "zapominać")
        pattern = next(
            item for item in zapominac["candidateContent"]["patterns"]
            if item["candidatePatternKey"]
            == "interrogative-forgotten-content"
        )
        self.assertEqual("recall-failure", pattern["meaningKeyRef"])
        self.assertEqual(
            [{"type": "clause", "clauseKind": "interrogative",
              "required": True, "role": "content"}],
            pattern["complements"],
        )
        self.assertEqual(
            {"recognition": "A2", "production": "A2"}, pattern["cefr"])
        self.assertEqual("active-production", pattern["teachingStatus"])
        examples = zapominac["candidateContent"]["examples"]
        self.assertEqual(
            1,
            sum(example["patternKeyRef"]
                == "interrogative-forgotten-content"
                for example in examples),
        )
        self.assertFalse(any(
            item["candidatePatternKey"] == "czy-dependent-clause"
            for item in zapominac["candidateContent"]["patterns"]
        ))

    def test_applicable_binding_constraints_unchanged(self):
        expected = {
            item["canonicalLemma"]: item["bindingConstraints"]
            for item in validator._expected_lemmas()
            if item["canonicalLemma"] in BATCH_2
        }
        self.assertEqual(
            expected,
            {item["canonicalLemma"]: item["bindingConstraints"]
             for item in self.batch_records},
        )


if __name__ == "__main__":
    unittest.main()
