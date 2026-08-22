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
BATCH_1 = tuple(lemma for _, lemma in validator.AUTHORING_BATCHES[0])
BATCH_1_DIGEST_FIELDS = (
    "verificationOrder",
    "canonicalLemma",
    "aspect",
    "phase3Disposition",
    "phase3Evidence",
    "bindingConstraints",
    "candidateContent",
)
BATCH_1_APPROVED_DIGEST = (
    "3849e0082e59e0984e7082c35e5b492eb3a228706aab2a7323575a5a9f9e619e"
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
        {field: item[field] for field in BATCH_1_DIGEST_FIELDS}
        for item in records
    ]
    canonical = json.dumps(
        projection,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


class Priority8Phase4B1Batch01Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(STAGING_PATH.read_text(encoding="utf-8"))
        cls.batch_records = [record(cls.data, lemma) for lemma in BATCH_1]

    def test_live_staging_validates(self):
        self.assertEqual([], validator.validate_data(self.data))

    def test_frozen_corpus_and_exact_batch_membership(self):
        self.assertEqual(68, self.data["frozenFullPatternCount"])
        self.assertEqual(
            validator.AUTHORING_BATCHES[0],
            tuple(
                (item["verificationOrder"], item["canonicalLemma"])
                for item in self.batch_records
            ),
        )

    def test_exact_approved_batch_content_digest(self):
        self.assertEqual(BATCH_1_APPROVED_DIGEST,
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
        self.assertEqual(25, sum(
            len(item["candidateContent"]["patterns"])
            for item in self.batch_records))
        self.assertEqual(25, sum(
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
        self.assertEqual(1, len(reuse))
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


if __name__ == "__main__":
    unittest.main()
