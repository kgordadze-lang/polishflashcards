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
MATRIX_PATH = ROOT / "reports/priority-8-phase-4b5-schema-matrix.md"
RULES_PATH = ROOT / "tests/fixtures/priority8_phase4b_authoring_rules.json"
MATRIX_APPROVED_SHA256 = (
    "9f2de2eda2cb051d47ec13f4eaadc45ba617f55b5c8871588db61e8b79641ad7"
)
BATCH_5 = tuple(lemma for _, lemma in validator.AUTHORING_BATCHES[4])
BATCH_5_DIGEST_FIELDS = (
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
BATCH_5_APPROVED_DIGEST = (
    "7c95810c26d99237995f138b58a9ae5ca07cd7431721cd619f1eb4f4622daf60"
)
ALLOWED_REVIEW_STATUSES = {
    "draft", "independently-reviewed", "human-approved",
}
PRODUCTION_ID_KEY_NAMES = validator.PRODUCTION_ID_FIELDS
ORDER_NUMBER_RE = re.compile(r"(?:^|-)0*[1-9][0-9]*(?:-|$)")
EXPECTED_BATCH_5_RULE_IDS = (
    "p8-4b-ogladac-exact-pattern-shapes",
    "p8-4b-obejrzec-exact-pattern-shapes",
    "p8-4b-skonczyc-exact-pattern-shapes",
    "p8-4b-chciec-exact-pattern-shapes",
    "p8-4b-robic-exact-pattern-shapes",
    "p8-4b-rozumiec-exact-pattern-shapes",
    "p8-4b-mieszkac-exact-pattern-shapes",
    "p8-4b-mieszkac-authorized-preposition-cases",
    "p8-4b-dzwonic-exact-pattern-shapes",
    "p8-4b-dzwonic-authorized-preposition-cases",
    "p8-4b-powiedziec-exact-pattern-shapes",
    "p8-4b-umowic-sie-lexical-identity",
    "p8-4b-umowic-sie-exact-pattern-shapes",
    "p8-4b-umowic-sie-authorized-preposition-cases",
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
        {field: item[field] for field in BATCH_5_DIGEST_FIELDS if field in item}
        for item in records
    ]
    canonical = json.dumps(
        projection,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


class Priority8Phase4B5Batch05Tests(unittest.TestCase):
    """Historical regression test for approved Batch 5 authoring.

    Follows the Batch 1-4 future-safe architecture: this test pins the
    approved Batch 5 content digest and does not assert phaseStep,
    stagingRevision, or corpus-wide draft/future-empty boundaries, so later
    Batch 6-7 authoring cannot invalidate it. Those moving assertions belong
    to tests/test_priority8_phase4b_progress.py.
    """

    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(STAGING_PATH.read_text(encoding="utf-8"))
        cls.batch_records = [record(cls.data, lemma) for lemma in BATCH_5]

    def test_live_staging_validates(self):
        self.assertEqual([], validator.validate_data(self.data))

    def test_frozen_corpus_and_exact_batch_membership(self):
        self.assertEqual(68, self.data["frozenFullPatternCount"])
        self.assertEqual(
            validator.AUTHORING_BATCHES[4],
            tuple(
                (item["verificationOrder"], item["canonicalLemma"])
                for item in self.batch_records
            ),
        )
        self.assertEqual(
            (42, 43, 44, 45, 46, 47, 48, 49, 50, 51),
            tuple(item["verificationOrder"] for item in self.batch_records),
        )
        self.assertEqual(
            ("oglądać", "obejrzeć", "skończyć", "chcieć", "robić", "rozumieć",
             "mieszkać", "umówić się", "dzwonić", "powiedzieć"),
            tuple(item["canonicalLemma"] for item in self.batch_records),
        )

    def test_frozen_schema_matrix_is_unchanged(self):
        self.assertEqual(
            MATRIX_APPROVED_SHA256,
            hashlib.sha256(MATRIX_PATH.read_bytes()).hexdigest(),
        )

    def test_exact_approved_batch_content_digest(self):
        self.assertEqual(BATCH_5_APPROVED_DIGEST,
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
        self.assertEqual(15, sum(
            len(item["candidateContent"]["meanings"])
            for item in self.batch_records))
        self.assertEqual(40, sum(
            len(item["candidateContent"]["patterns"])
            for item in self.batch_records))
        self.assertEqual(40, sum(
            len(item["candidateContent"]["examples"])
            for item in self.batch_records))

    def test_per_lemma_meaning_and_pattern_counts_match_the_frozen_matrix(self):
        expected = {
            "oglądać": (1, 1),
            "obejrzeć": (1, 1),
            "skończyć": (2, 3),
            "chcieć": (2, 6),
            "robić": (2, 2),
            "rozumieć": (2, 4),
            "mieszkać": (1, 1),
            "umówić się": (2, 7),
            "dzwonić": (1, 4),
            "powiedzieć": (1, 11),
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
        expected_meaning_keys = {
            "oglądać": {"processual-viewing"},
            "obejrzeć": {"completed-viewing"},
            "skończyć": {"activity-completion", "definitive-cessation"},
            "chcieć": {"desire", "polite-request-or-intention"},
            "robić": {"entity-creation", "activity-performance"},
            "rozumieć": {"content-comprehension", "empathic-person-understanding"},
            "mieszkać": {"long-term-residence"},
            "umówić się": {"meeting-arrangement", "mutual-agreement"},
            "dzwonić": {"telephone-contact"},
            "powiedzieć": {"spoken-communication"},
        }
        expected_pattern_keys = {
            "oglądać": {"accusative-content-optional-presentation-context"},
            "obejrzeć": {"accusative-content"},
            "skończyć": {"accusative-task", "infinitive",
                         "z-instrumental-ceased-activity"},
            "chcieć": {"genitive-desired-object", "infinitive-own-action",
                       "zeby-desired-event", "accusative-requested-object",
                       "infinitive-intended-action", "zeby-requested-event"},
            "robić": {"accusative-created-entity", "accusative-activity-noun"},
            "rozumieć": {"accusative-content", "ze-content-clause",
                         "interrogative-content-clause", "accusative-person"},
            "mieszkać": {"w-locative-residence-optional-co-resident"},
            "umówić się": {
                "z-instrumental-partner-na-accusative-event",
                "do-genitive-appointment-venue", "na-accusative-agreed-term",
                "o-accusative-agreed-subject", "ze-agreement-clause",
                "zeby-agreed-action-clause", "interrogative-agreement-clause",
            },
            "dzwonić": {"do-genitive-call-target", "na-accusative-call-target",
                        "ze-reported-content-clause",
                        "zeby-requested-content-clause"},
            "powiedzieć": {
                f"{mode}-{name}"
                for mode in ("dative", "do-genitive")
                for name in ("accusative-content", "o-locative-topic",
                              "ze-clause", "zeby-clause",
                              "interrogative-clause")
            } | {"direct-speech-content"},
        }

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
                self.assertNotRegex(key, r"batch|order|verification|hold")

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
        # globally unique: naturalness always outranks an artificial
        # uniqueness constraint on the translation (Phase 4B4 precedent).
        examples = [
            example for item in self.batch_records
            for example in item["candidateContent"]["examples"]
        ]
        self.assertEqual(40, len(examples))
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
            if item["canonicalLemma"] in BATCH_5
        }
        self.assertEqual(
            expected,
            {item["canonicalLemma"]: item["bindingConstraints"]
             for item in self.batch_records},
        )

    def test_ogladac_optional_presentation_context_never_stands_alone(self):
        ogladac = record(self.data, "oglądać")
        patterns = ogladac["candidateContent"]["patterns"]
        self.assertEqual(1, len(patterns))
        complements = patterns[0]["complements"]
        self.assertEqual(2, len(complements))
        w_loc = [c for c in complements if c.get("preposition") == "w"]
        self.assertEqual(1, len(w_loc))
        self.assertFalse(w_loc[0]["required"])
        self.assertFalse(any(
            p["complements"] == [
                {"type": "preposition-case", "preposition": "w",
                 "case": "locative", "required": True, "role": "target"}
            ]
            for p in patterns
        ))

    def test_obejrzec_has_no_w_locative_imported_from_ogladac(self):
        obejrzec = record(self.data, "obejrzeć")
        for pattern in obejrzec["candidateContent"]["patterns"]:
            for c in pattern["complements"]:
                self.assertFalse(
                    c["type"] == "preposition-case" and c.get("preposition") == "w")

    def test_skonczyc_cessation_kept_separate_from_completion(self):
        skonczyc = record(self.data, "skończyć")
        completion = [
            p for p in skonczyc["candidateContent"]["patterns"]
            if p["meaningKeyRef"] == "activity-completion"
        ]
        cessation = [
            p for p in skonczyc["candidateContent"]["patterns"]
            if p["meaningKeyRef"] == "definitive-cessation"
        ]
        self.assertEqual(2, len(completion))
        self.assertEqual(1, len(cessation))
        for p in completion:
            types = {c["type"] for c in p["complements"]}
            self.assertNotIn("preposition-case", types)
        self.assertEqual(
            [{"type": "preposition-case", "preposition": "z",
              "case": "instrumental", "required": True, "role": "topic"}],
            cessation[0]["complements"],
        )

    def test_chciec_desire_and_polite_request_use_distinct_case(self):
        chciec = record(self.data, "chcieć")
        by_key = {
            (p["meaningKeyRef"], p["candidatePatternKey"]): p
            for p in chciec["candidateContent"]["patterns"]
        }
        desire_obj = by_key[("desire", "genitive-desired-object")]
        polite_obj = by_key[("polite-request-or-intention",
                              "accusative-requested-object")]
        req_desire = next(c for c in desire_obj["complements"] if c["required"])
        req_polite = next(c for c in polite_obj["complements"] if c["required"])
        self.assertEqual("genitive", req_desire["case"])
        self.assertEqual("accusative", req_polite["case"])
        # optional od/dla remain attached only to the desire object schema
        self.assertEqual(3, len(desire_obj["complements"]))
        self.assertEqual(1, len(polite_obj["complements"]))

    def test_robic_two_meanings_share_identical_structure_by_design(self):
        robic = record(self.data, "robić")
        patterns = robic["candidateContent"]["patterns"]
        self.assertEqual(2, len(patterns))
        shapes = {p["meaningKeyRef"]: p["complements"] for p in patterns}
        self.assertEqual(
            shapes["entity-creation"], shapes["activity-performance"])
        meanings = {
            m["candidateMeaningKey"]: m for m in robic["candidateContent"]["meanings"]
        }
        self.assertNotEqual(
            meanings["entity-creation"]["internalScope"],
            meanings["activity-performance"]["internalScope"],
        )

    def test_rozumiec_no_clause_on_person_meaning(self):
        rozumiec = record(self.data, "rozumieć")
        person_patterns = [
            p for p in rozumiec["candidateContent"]["patterns"]
            if p["meaningKeyRef"] == "empathic-person-understanding"
        ]
        self.assertEqual(1, len(person_patterns))
        types = {c["type"] for c in person_patterns[0]["complements"]}
        self.assertNotIn("clause", types)

    def test_mieszkac_w_locative_and_z_instrumental_co_resident(self):
        mieszkac = record(self.data, "mieszkać")
        patterns = mieszkac["candidateContent"]["patterns"]
        self.assertEqual(1, len(patterns))
        complements = patterns[0]["complements"]
        self.assertEqual(
            [{"type": "preposition-case", "preposition": "w",
              "case": "locative", "required": True, "role": "target"},
             {"type": "preposition-case", "preposition": "z",
              "case": "instrumental", "required": False, "role": "interlocutor"}],
            complements,
        )

    def test_umowic_sie_preserves_lexical_sie(self):
        umowic = record(self.data, "umówić się")
        self.assertEqual("umówić się", umowic["canonicalLemma"])
        names = {item["canonicalLemma"] for item in self.data["lemmas"]}
        self.assertNotIn("umówić", names)

    def test_umowic_sie_appointment_a1_is_genuinely_all_optional(self):
        umowic = record(self.data, "umówić się")
        pattern = next(
            p for p in umowic["candidateContent"]["patterns"]
            if p["candidatePatternKey"] == "z-instrumental-partner-na-accusative-event"
        )
        self.assertEqual("meeting-arrangement", pattern["meaningKeyRef"])
        self.assertEqual(2, len(pattern["complements"]))
        self.assertTrue(all(not c["required"] for c in pattern["complements"]))

    def test_umowic_sie_appointment_a2_is_do_genitive_realization(self):
        umowic = record(self.data, "umówić się")
        pattern = next(
            p for p in umowic["candidateContent"]["patterns"]
            if p["candidatePatternKey"] == "do-genitive-appointment-venue"
        )
        self.assertEqual("meeting-arrangement", pattern["meaningKeyRef"])
        do_complement = next(
            c for c in pattern["complements"] if c.get("preposition") == "do")
        self.assertTrue(do_complement["required"])
        z_complement = next(
            c for c in pattern["complements"] if c.get("preposition") == "z")
        self.assertFalse(z_complement["required"])

    def test_umowic_sie_has_no_kiedy_or_co_do_product_row(self):
        umowic = record(self.data, "umówić się")
        for pattern in umowic["candidateContent"]["patterns"]:
            prepositions = {
                c.get("preposition") for c in pattern["complements"]
                if c["type"] == "preposition-case"
            }
            self.assertNotIn("co", prepositions)
        # exactly 7 patterns: no synthetic 8th row for co do + Genitive,
        # and no KIEDY complement of any type was invented anywhere
        self.assertEqual(7, len(umowic["candidateContent"]["patterns"]))

    def test_dzwonic_has_no_w_sprawie_governed_pattern(self):
        dzwonic = record(self.data, "dzwonić")
        for pattern in dzwonic["candidateContent"]["patterns"]:
            for c in pattern["complements"]:
                if c["type"] == "preposition-case":
                    self.assertNotEqual("sprawie", c.get("case"))
                    if c.get("preposition") == "w":
                        self.fail("dzwonić must not author a governed w-phrase")

    def test_powiedziec_direct_speech_is_recipientless(self):
        powiedziec = record(self.data, "powiedzieć")
        direct_speech = next(
            p for p in powiedziec["candidateContent"]["patterns"]
            if p["candidatePatternKey"] == "direct-speech-content"
        )
        self.assertEqual(1, len(direct_speech["complements"]))
        self.assertEqual("clause", direct_speech["complements"][0]["type"])
        self.assertEqual(
            "direct-speech", direct_speech["complements"][0]["clauseKind"])

    def test_powiedziec_recipient_modes_never_co_occur(self):
        powiedziec = record(self.data, "powiedzieć")
        for pattern in powiedziec["candidateContent"]["patterns"]:
            recipient_types = {
                (c["type"], c.get("preposition"))
                for c in pattern["complements"] if c["role"] == "recipient"
            }
            self.assertLessEqual(len(recipient_types), 1,
                                  pattern["candidatePatternKey"])

    def test_chciec_polite_request_examples_use_first_person_restriction(self):
        chciec = record(self.data, "chcieć")
        polite_examples = [
            e for e in chciec["candidateContent"]["examples"]
            if e["meaningKeyRef"] == "polite-request-or-intention"
        ]
        self.assertEqual(3, len(polite_examples))
        for e in polite_examples:
            self.assertTrue(
                e["pl"].startswith("Chciałbym") or e["pl"].startswith("Chciałabym"),
                e["pl"],
            )

    def test_batch_5_live_guard_rules_are_present(self):
        registry = json.loads(RULES_PATH.read_text(encoding="utf-8"))
        rule_ids = {rule["ruleId"] for rule in registry["rules"]}
        for expected_id in EXPECTED_BATCH_5_RULE_IDS:
            self.assertIn(expected_id, rule_ids)
        self.assertEqual(14, len(EXPECTED_BATCH_5_RULE_IDS))


if __name__ == "__main__":
    unittest.main()
