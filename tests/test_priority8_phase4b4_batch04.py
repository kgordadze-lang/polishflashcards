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
MATRIX_PATH = ROOT / "reports/priority-8-phase-4b4-schema-matrix.md"
RULES_PATH = ROOT / "tests/fixtures/priority8_phase4b_authoring_rules.json"
MATRIX_APPROVED_SHA256 = (
    "6e63c9d2628d9237e7b5851c29e55975734440878dac7491873f9368291f3781"
)
BATCH_4 = tuple(lemma for _, lemma in validator.AUTHORING_BATCHES[3])
BATCH_4_DIGEST_FIELDS = (
    "verificationOrder",
    "canonicalLemma",
    "aspect",
    "phase3Disposition",
    "phase3Evidence",
    "bindingConstraints",
    "candidateContent",
    "metadataAspectPartner",
    "requiredLexicalItems",
)
BATCH_4_APPROVED_DIGEST = (
    "7f8fd8840d7aadeffbd23a5047cf8ce200b07c84c41520835a11f575c698b4f2"
)
ALLOWED_REVIEW_STATUSES = {
    "draft", "independently-reviewed", "human-approved",
}
PRODUCTION_ID_KEY_NAMES = validator.PRODUCTION_ID_FIELDS
ORDER_NUMBER_RE = re.compile(r"(?:^|-)0*[1-9][0-9]*(?:-|$)")
EXPECTED_BATCH_4_RULE_IDS = (
    "p8-4b-dawac-exact-pattern-shapes",
    "p8-4b-dac-exact-pattern-shapes",
    "p8-4b-brac-exact-pattern-shapes",
    "p8-4b-brac-participation-explanation-material",
    "p8-4b-wziac-exact-pattern-shapes",
    "p8-4b-wziac-participation-explanation-material",
    "p8-4b-czytac-exact-pattern-shapes",
    "p8-4b-czytac-authorized-o-locative-topic-signatures",
    "p8-4b-pisac-exact-pattern-shapes",
    "p8-4b-napisac-exact-pattern-shapes",
    "p8-4b-spotykac-sie-lexical-identity",
    "p8-4b-spotykac-sie-exact-pattern-shapes",
    "p8-4b-spotkac-sie-lexical-identity",
    "p8-4b-spotkac-sie-exact-pattern-shapes",
)


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
        {field: item[field] for field in BATCH_4_DIGEST_FIELDS if field in item}
        for item in records
    ]
    canonical = json.dumps(
        projection,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


class Priority8Phase4B4Batch04Tests(unittest.TestCase):
    """Historical regression test for approved Batch 4 authoring.

    Follows the Batch 1/2/3 future-safe architecture: this test pins the
    approved Batch 4 content digest and does not assert phaseStep,
    stagingRevision, or corpus-wide draft/future-empty boundaries, so later
    Batch 5-7 authoring cannot invalidate it. Those moving assertions belong
    to tests/test_priority8_phase4b_progress.py.
    """

    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(STAGING_PATH.read_text(encoding="utf-8"))
        cls.batch_records = [record(cls.data, lemma) for lemma in BATCH_4]

    def test_live_staging_validates(self):
        self.assertEqual([], validator.validate_data(self.data))

    def test_frozen_corpus_and_exact_batch_membership(self):
        self.assertEqual(68, self.data["frozenFullPatternCount"])
        self.assertEqual(
            validator.AUTHORING_BATCHES[3],
            tuple(
                (item["verificationOrder"], item["canonicalLemma"])
                for item in self.batch_records
            ),
        )
        self.assertEqual(
            (32, 33, 34, 35, 36, 38, 39, 40, 41),
            tuple(item["verificationOrder"] for item in self.batch_records),
        )
        self.assertEqual(
            ("dawać", "dać", "brać", "wziąć", "czytać", "pisać", "napisać",
             "spotykać się", "spotkać się"),
            tuple(item["canonicalLemma"] for item in self.batch_records),
        )

    def test_order_37_przeczytac_remains_metadata_only(self):
        names = {item["canonicalLemma"] for item in self.data["lemmas"]}
        self.assertNotIn("przeczytać", names)
        czytac = record(self.data, "czytać")
        partner = czytac["metadataAspectPartner"]
        self.assertEqual("przeczytać", partner["canonicalLemma"])
        self.assertNotIn("candidateContent", partner)

    def test_frozen_schema_matrix_is_unchanged(self):
        self.assertEqual(
            MATRIX_APPROVED_SHA256,
            hashlib.sha256(MATRIX_PATH.read_bytes()).hexdigest(),
        )

    def test_exact_approved_batch_content_digest(self):
        self.assertEqual(BATCH_4_APPROVED_DIGEST,
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
        self.assertEqual(13, sum(
            len(item["candidateContent"]["meanings"])
            for item in self.batch_records))
        self.assertEqual(41, sum(
            len(item["candidateContent"]["patterns"])
            for item in self.batch_records))
        self.assertEqual(41, sum(
            len(item["candidateContent"]["examples"])
            for item in self.batch_records))

    def test_per_lemma_meaning_and_pattern_counts_match_the_frozen_matrix(self):
        expected = {
            "dawać": (1, 1),
            "dać": (1, 1),
            "brać": (2, 3),
            "wziąć": (2, 3),
            "czytać": (1, 5),
            "pisać": (2, 13),
            "napisać": (2, 13),
            "spotykać się": (1, 1),
            "spotkać się": (1, 1),
        }
        for item in self.batch_records:
            content = item["candidateContent"]
            expected_meanings, expected_patterns = expected[item["canonicalLemma"]]
            self.assertEqual(
                expected_meanings, len(content["meanings"]), item["canonicalLemma"])
            self.assertEqual(
                expected_patterns, len(content["patterns"]), item["canonicalLemma"])

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

    def test_candidate_keys_match_the_frozen_matrix_proposals(self):
        # The matrix's meaningKeyProposal/schemaKeyProposal values are frozen
        # authoring inputs and must be used verbatim as candidateMeaningKey/
        # candidatePatternKey, never renamed or decorated with batch/order
        # numbers or source wording.
        expected_meaning_keys = {
            "dawać": {"transfer-to-recipient"},
            "dać": {"completed-transfer-to-recipient"},
            "brać": {"literal-taking", "fixed-participation"},
            "wziąć": {"bounded-literal-taking", "fixed-participation"},
            "czytać": {"reading-written-content"},
            "pisać": {"text-creation", "written-correspondence"},
            "napisać": {"completed-text-creation",
                        "completed-written-correspondence"},
            "spotykać się": {"recurring-social-meeting"},
            "spotkać się": {"completed-social-meeting"},
        }
        expected_pattern_keys = {
            "dawać": {"accusative-thing-dative-recipient"},
            "dać": {"accusative-thing-dative-recipient"},
            "brać": {
                "accusative-entity-optional-instrumental-means",
                "accusative-entity-za-accusative-gripped-part",
                "w-locative-participation-target",
            },
            "wziąć": {
                "accusative-entity-optional-instrumental-means",
                "accusative-entity-za-accusative-gripped-part",
                "w-locative-participation-target",
            },
            "czytać": {
                "accusative-content-optional-listener", "o-locative-topic",
                "ze-content-clause", "interrogative-content-clause",
                "direct-speech-content",
            },
            "spotykać się": {"z-instrumental-meeting-partner"},
            "spotkać się": {"z-instrumental-meeting-partner"},
        }
        correspondence_pattern_keys = {
            f"{mode}-{name}"
            for mode in ("dative", "do-genitive")
            for name in ("topic", "ze-clause", "zeby-clause",
                          "interrogative-clause", "direct-speech",
                          "accusative-content")
        }
        expected_pattern_keys["pisać"] = {"accusative-created-text"} | correspondence_pattern_keys
        expected_pattern_keys["napisać"] = {"accusative-created-text"} | correspondence_pattern_keys

        for item in self.batch_records:
            lemma = item["canonicalLemma"]
            content = item["candidateContent"]
            self.assertEqual(
                expected_meaning_keys[lemma],
                {m["candidateMeaningKey"] for m in content["meanings"]},
                lemma,
            )
            self.assertEqual(
                expected_pattern_keys[lemma],
                {p["candidatePatternKey"] for p in content["patterns"]},
                lemma,
            )
            for key in {m["candidateMeaningKey"] for m in content["meanings"]} | {
                p["candidatePatternKey"] for p in content["patterns"]
            }:
                self.assertNotRegex(key, r"batch|order|verification")

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
        self.assertEqual(0, len(reuse))
        index = tooling.repository_index_from_root(ROOT)
        self.assertEqual([], index.issues)
        for lemma, example, source in reuse:
            entity = index.get(source["id"])
            self.assertIsNotNone(entity, lemma)
            self.assertEqual(source["kind"], entity.kind, lemma)
            self.assertIn(source["field"], entity.record, lemma)
            self.assertEqual(example["pl"], entity.record[source["field"]], lemma)

    def test_polish_examples_are_unique_and_generated_examples_are_not_quiet_reuse(self):
        # Polish sentences must be pedagogically distinct (no gratuitous
        # duplication), but English translations are NOT required to be
        # globally unique: two distinct Polish recipient-mode alternatives
        # (Dative vs do + Genitive) can and do share the same natural
        # English rendering, and naturalness always outranks an artificial
        # uniqueness constraint on the translation.
        examples = [
            example for item in self.batch_records
            for example in item["candidateContent"]["examples"]
        ]
        self.assertEqual(41, len(examples))
        polish = [example["pl"] for example in examples]
        self.assertEqual(len(polish), len(set(polish)))
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

    def test_applicable_binding_constraints_unchanged(self):
        expected = {
            item["canonicalLemma"]: item["bindingConstraints"]
            for item in validator._expected_lemmas()
            if item["canonicalLemma"] in BATCH_4
        }
        self.assertEqual(
            expected,
            {item["canonicalLemma"]: item["bindingConstraints"]
             for item in self.batch_records},
        )

    def test_required_lexical_items_preserved_for_brac_and_wziac(self):
        brac = record(self.data, "brać")
        wziac = record(self.data, "wziąć")
        self.assertEqual(["udział"], brac["requiredLexicalItems"])
        self.assertEqual(["udział"], wziac["requiredLexicalItems"])
        for lemma_record in (brac, wziac):
            participation = next(
                m for m in lemma_record["candidateContent"]["meanings"]
                if m["candidateMeaningKey"] == "fixed-participation"
            )
            pattern = next(
                p for p in lemma_record["candidateContent"]["patterns"]
                if p["meaningKeyRef"] == "fixed-participation"
            )
            example = next(
                e for e in lemma_record["candidateContent"]["examples"]
                if e["meaningKeyRef"] == "fixed-participation"
            )
            self.assertIn("udział", participation["internalScope"])
            self.assertIn("udział", pattern["learnerExplanationEn"])
            self.assertIn("udział", example["pl"])
            self.assertEqual(
                [{"type": "preposition-case", "preposition": "w",
                  "case": "locative", "required": True, "role": "target"}],
                pattern["complements"],
            )
            self.assertFalse(any(
                p["candidatePatternKey"] not in (
                    "accusative-entity-optional-instrumental-means",
                    "accusative-entity-za-accusative-gripped-part",
                    "w-locative-participation-target",
                )
                for p in lemma_record["candidateContent"]["patterns"]
            ))

    def test_brac_and_wziac_optional_instrumental_never_stands_alone(self):
        for lemma in ("brać", "wziąć"):
            item = record(self.data, lemma)
            literal_patterns = [
                p for p in item["candidateContent"]["patterns"]
                if p["candidatePatternKey"]
                == "accusative-entity-optional-instrumental-means"
            ]
            self.assertEqual(1, len(literal_patterns), lemma)
            complements = literal_patterns[0]["complements"]
            self.assertEqual(2, len(complements), lemma)
            means = [c for c in complements if c["role"] == "means"]
            self.assertEqual(1, len(means), lemma)
            self.assertFalse(means[0]["required"], lemma)
            self.assertFalse(any(
                p["complements"] == [
                    {"type": "case", "case": "instrumental",
                     "required": True, "role": "means"}
                ]
                for p in item["candidateContent"]["patterns"]
            ), lemma)

    def test_czytac_has_no_concretized_gdzie_location_pattern(self):
        czytac = record(self.data, "czytać")
        for pattern in czytac["candidateContent"]["patterns"]:
            for c in pattern["complements"]:
                if c["type"] == "preposition-case":
                    self.assertEqual("o", c["preposition"])
                    self.assertEqual("locative", c["case"])
                    self.assertEqual("topic", c["role"])

    def test_czytac_authorizes_both_o_locative_topic_signatures(self):
        czytac = record(self.data, "czytać")
        topic_signatures = [
            (c["required"])
            for pattern in czytac["candidateContent"]["patterns"]
            for c in pattern["complements"]
            if c["type"] == "preposition-case" and c["preposition"] == "o"
            and c["case"] == "locative" and c["role"] == "topic"
        ]
        self.assertIn(True, topic_signatures)
        self.assertIn(False, topic_signatures)
        required_topic_patterns = [
            pattern for pattern in czytac["candidateContent"]["patterns"]
            for c in pattern["complements"]
            if c["type"] == "preposition-case" and c["preposition"] == "o"
            and c["case"] == "locative" and c["role"] == "topic"
            and c["required"] is True
        ]
        self.assertEqual(1, len(required_topic_patterns))
        self.assertEqual(
            "o-locative-topic", required_topic_patterns[0]["candidatePatternKey"])

    def test_pisac_recipient_modes_never_co_occur_and_all_recipients_optional(self):
        pisac = record(self.data, "pisać")
        correspondence = [
            p for p in pisac["candidateContent"]["patterns"]
            if p["meaningKeyRef"] == "written-correspondence"
        ]
        self.assertEqual(12, len(correspondence))
        for pattern in correspondence:
            recipient_types = {
                (c["type"], c.get("preposition"))
                for c in pattern["complements"]
                if c["role"] == "recipient"
            }
            self.assertEqual(1, len(recipient_types), pattern["candidatePatternKey"])
            recipient = next(c for c in pattern["complements"] if c["role"] == "recipient")
            self.assertFalse(recipient["required"], pattern["candidatePatternKey"])

    def test_napisac_required_dative_asymmetry_matches_the_frozen_matrix(self):
        napisac = record(self.data, "napisać")
        correspondence = {
            p["candidatePatternKey"]: p
            for p in napisac["candidateContent"]["patterns"]
            if p["meaningKeyRef"] == "completed-written-correspondence"
        }
        self.assertEqual(12, len(correspondence))
        required_dative_keys = {
            "dative-ze-clause", "dative-zeby-clause",
            "dative-interrogative-clause",
        }
        optional_dative_keys = {
            "dative-topic", "dative-direct-speech", "dative-accusative-content",
        }
        for key in required_dative_keys:
            dative = next(
                c for c in correspondence[key]["complements"]
                if c["type"] == "case" and c["case"] == "dative"
            )
            self.assertTrue(dative["required"], key)
        for key in optional_dative_keys:
            dative = next(
                c for c in correspondence[key]["complements"]
                if c["type"] == "case" and c["case"] == "dative"
            )
            self.assertFalse(dative["required"], key)
        for key, pattern in correspondence.items():
            if key.startswith("do-genitive"):
                do_complement = next(
                    c for c in pattern["complements"]
                    if c["type"] == "preposition-case" and c["preposition"] == "do"
                )
                self.assertFalse(do_complement["required"], key)

    def test_napisac_is_not_normalized_to_pisac(self):
        pisac = record(self.data, "pisać")
        napisac = record(self.data, "napisać")
        pisac_by_key = {
            p["candidatePatternKey"]: p
            for p in pisac["candidateContent"]["patterns"]
            if p["meaningKeyRef"] == "written-correspondence"
        }
        napisac_by_key = {
            p["candidatePatternKey"]: p
            for p in napisac["candidateContent"]["patterns"]
            if p["meaningKeyRef"] == "completed-written-correspondence"
        }
        differing = {
            key for key in pisac_by_key
            if pisac_by_key[key]["complements"] != napisac_by_key[key]["complements"]
        }
        self.assertEqual(
            {"dative-ze-clause", "dative-zeby-clause",
             "dative-interrogative-clause"},
            differing,
        )

    def test_spotykac_sie_and_spotkac_sie_preserve_lexical_sie(self):
        spotykac = record(self.data, "spotykać się")
        spotkac = record(self.data, "spotkać się")
        self.assertEqual("spotykać się", spotykac["canonicalLemma"])
        self.assertEqual("spotkać się", spotkac["canonicalLemma"])
        names = {item["canonicalLemma"] for item in self.data["lemmas"]}
        self.assertNotIn("spotykać", names)
        self.assertNotIn("spotkać", names)
        for item in (spotykac, spotkac):
            for pattern in item["candidateContent"]["patterns"]:
                self.assertEqual(
                    [{"type": "preposition-case", "preposition": "z",
                      "case": "instrumental", "required": True,
                      "role": "interlocutor"}],
                    pattern["complements"],
                )

    def test_batch_4_live_guard_rules_are_present(self):
        registry = json.loads(RULES_PATH.read_text(encoding="utf-8"))
        rule_ids = {rule["ruleId"] for rule in registry["rules"]}
        for expected_id in EXPECTED_BATCH_4_RULE_IDS:
            self.assertIn(expected_id, rule_ids)
        self.assertEqual(14, len(EXPECTED_BATCH_4_RULE_IDS))


if __name__ == "__main__":
    unittest.main()
