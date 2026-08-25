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
MATRIX_PATH = ROOT / "reports/priority-8-phase-4b6-schema-matrix.md"
RULES_PATH = ROOT / "tests/fixtures/priority8_phase4b_authoring_rules.json"
MATRIX_APPROVED_SHA256 = (
    "72ab74094d67e4a6c944eaa5b421c2a8b7509ae4bd3b59e102a448fee364fe8c"
)
BATCH_6 = tuple(lemma for _, lemma in validator.AUTHORING_BATCHES[5])
BATCH_6_DIGEST_FIELDS = (
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
BATCH_6_APPROVED_DIGEST = (
    "cff207b6e728fb203ba05a9ba94915432957be76101b3bd6a0f65137cdda98d5"
)
ALLOWED_REVIEW_STATUSES = {
    "draft", "independently-reviewed", "human-approved",
}
PRODUCTION_ID_KEY_NAMES = validator.PRODUCTION_ID_FIELDS
ORDER_NUMBER_RE = re.compile(r"(?:^|-)0*[1-9][0-9]*(?:-|$)")
EXPECTED_BATCH_6_RULE_IDS = (
    "p8-4b-gotowac-exact-pattern-shapes",
    "p8-4b-rezerwowac-exact-pattern-shapes",
    "p8-4b-rezerwowac-authorized-preposition-cases",
    "p8-4b-cieszyc-sie-lexical-identity",
    "p8-4b-cieszyc-sie-exact-pattern-shapes",
    "p8-4b-cieszyc-sie-authorized-preposition-cases",
    "p8-4b-martwic-sie-lexical-identity",
    "p8-4b-martwic-sie-exact-pattern-shapes",
    "p8-4b-martwic-sie-authorized-preposition-cases",
    "p8-4b-zgadzac-sie-lexical-identity",
    "p8-4b-zgadzac-sie-exact-pattern-shapes",
    "p8-4b-zgadzac-sie-authorized-preposition-cases",
    "p8-4b-zapraszac-exact-pattern-shapes",
    "p8-4b-zapraszac-authorized-preposition-cases",
    "p8-4b-polecac-exact-pattern-shapes",
    "p8-4b-radzic-exact-pattern-shapes",
    "p8-4b-radzic-no-z-instrumental-coping",
    "p8-4b-pasowac-exact-pattern-shapes",
    "p8-4b-pasowac-authorized-preposition-cases",
    "p8-4b-moc-exact-pattern-shapes",
    "p8-4b-moc-no-question-clause",
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
        {field: item[field] for field in BATCH_6_DIGEST_FIELDS if field in item}
        for item in records
    ]
    canonical = json.dumps(
        projection,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


class Priority8Phase4B6Batch06Tests(unittest.TestCase):
    """Historical regression test for approved Batch 6 authoring.

    Follows the Batch 1-5 future-safe architecture: this test pins the
    approved Batch 6 content digest and does not assert phaseStep,
    stagingRevision, or corpus-wide draft/future-empty boundaries, so later
    Batch 7 authoring cannot invalidate it. Those moving assertions belong to
    tests/test_priority8_phase4b_progress.py.
    """

    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(STAGING_PATH.read_text(encoding="utf-8"))
        cls.batch_records = [record(cls.data, lemma) for lemma in BATCH_6]

    def test_live_staging_validates(self):
        self.assertEqual([], validator.validate_data(self.data))

    def test_frozen_corpus_and_exact_batch_membership(self):
        self.assertEqual(68, self.data["frozenFullPatternCount"])
        self.assertEqual(
            validator.AUTHORING_BATCHES[5],
            tuple(
                (item["verificationOrder"], item["canonicalLemma"])
                for item in self.batch_records
            ),
        )
        self.assertEqual(
            (52, 53, 54, 55, 56, 57, 58, 59, 60, 61),
            tuple(item["verificationOrder"] for item in self.batch_records),
        )
        self.assertEqual(
            ("gotować", "rezerwować", "cieszyć się", "martwić się",
             "zgadzać się", "zapraszać", "polecać", "radzić", "pasować",
             "móc"),
            tuple(item["canonicalLemma"] for item in self.batch_records),
        )
        self.assertNotIn("powiedzieć",
                          {item["canonicalLemma"] for item in self.batch_records})
        self.assertNotIn("musieć",
                          {item["canonicalLemma"] for item in self.batch_records})

    def test_frozen_schema_matrix_is_unchanged(self):
        self.assertEqual(
            MATRIX_APPROVED_SHA256,
            hashlib.sha256(MATRIX_PATH.read_bytes()).hexdigest(),
        )

    def test_exact_approved_batch_content_digest(self):
        self.assertEqual(BATCH_6_APPROVED_DIGEST,
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
        self.assertEqual(16, sum(
            len(item["candidateContent"]["meanings"])
            for item in self.batch_records))
        self.assertEqual(37, sum(
            len(item["candidateContent"]["patterns"])
            for item in self.batch_records))
        self.assertEqual(37, sum(
            len(item["candidateContent"]["examples"])
            for item in self.batch_records))

    def test_per_lemma_meaning_and_pattern_counts_match_the_frozen_matrix(self):
        expected = {
            "gotować": (1, 1),
            "rezerwować": (1, 2),
            "cieszyć się": (1, 4),
            "martwić się": (1, 4),
            "zgadzać się": (2, 7),
            "zapraszać": (1, 2),
            "polecać": (2, 5),
            "radzić": (1, 5),
            "pasować": (4, 5),
            "móc": (2, 2),
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
            "gotować": {"meal-preparation"},
            "rezerwować": {"booking-reservation"},
            "cieszyć się": {"experiencing-joy"},
            "martwić się": {"worry-concern"},
            "zgadzać się": {"consent", "opinion-agreement"},
            "zapraszać": {"invitation"},
            "polecać": {"directive-instruction", "recommendation"},
            "radzić": {"giving-advice"},
            "pasować": {"appearance-harmony", "physical-fit",
                        "typical-appropriateness", "expectation-suitability"},
            "móc": {"ability-possibility", "permission"},
        }
        expected_pattern_keys = {
            "gotować": {"accusative-dish-dative-beneficiary"},
            "rezerwować": {"accusative-item-dative-beneficiary",
                           "accusative-item-dla-genitive-beneficiary"},
            "cieszyć się": {"z-genitive-realized-cause",
                            "na-accusative-anticipated-occasion",
                            "instrumental-nominal-cause",
                            "ze-propositional-cause"},
            "martwić się": {"instrumental-worry-cause",
                            "o-accusative-concern-object",
                            "ze-worry-proposition",
                            "interrogative-worry-content"},
            "zgadzać się": {"na-accusative-consented-proposal",
                            "zeby-consented-event",
                            "infinitive-consented-action",
                            "direct-speech-consent",
                            "z-instrumental-agreement-partner",
                            "ze-agreed-proposition",
                            "direct-speech-agreement"},
            "zapraszać": {"accusative-invitee-na-accusative-event",
                          "accusative-invitee-do-genitive-destination"},
            "polecać": {"dative-infinitive-instruction",
                        "dative-zeby-instruction",
                        "dative-direct-speech-instruction",
                        "dative-accusative-action-noun",
                        "dative-accusative-recommended-item"},
            "radzić": {"dative-accusative-advice-item",
                       "dative-zeby-advice",
                       "dative-interrogative-advice",
                       "dative-direct-speech-advice",
                       "dative-infinitive-advice"},
            "pasować": {"do-genitive-harmony-target",
                        "do-genitive-fit-target",
                        "na-accusative-fitted-object",
                        "dative-evaluator-do-genitive-reference",
                        "dative-expectation-holder"},
            "móc": {"infinitive-possible-action", "infinitive-permitted-action"},
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
                # hyphen/end-bounded so legitimate English words such as
                # "expectation-holder" are not mistaken for a meta-identifier
                self.assertNotRegex(
                    key, r"(?:^|-)(?:batch|order|verification|hold)(?:-|$)")

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
        self.assertEqual(37, len(examples))
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
            if item["canonicalLemma"] in BATCH_6
        }
        self.assertEqual(
            expected,
            {item["canonicalLemma"]: item["bindingConstraints"]
             for item in self.batch_records},
        )
        # None of the ten Batch 6 records is a KEEP WITH NARROWING record.
        self.assertTrue(all(
            item["bindingConstraints"] == [] for item in self.batch_records))

    def test_gotowac_meal_preparation_is_genuinely_all_optional(self):
        gotowac = record(self.data, "gotować")
        patterns = gotowac["candidateContent"]["patterns"]
        self.assertEqual(1, len(patterns))
        complements = patterns[0]["complements"]
        self.assertEqual(2, len(complements))
        self.assertTrue(all(not c["required"] for c in complements))
        self.assertFalse(any(
            c["type"] == "preposition-case" and c.get("preposition") == "dla"
            for c in complements))

    def test_rezerwowac_beneficiary_alternatives_never_combine(self):
        rezerwowac = record(self.data, "rezerwować")
        patterns = rezerwowac["candidateContent"]["patterns"]
        self.assertEqual(2, len(patterns))
        for pattern in patterns:
            acc = [c for c in pattern["complements"] if c["type"] == "case"
                   and c["case"] == "accusative"]
            self.assertEqual(1, len(acc))
            self.assertTrue(acc[0]["required"])
            self.assertEqual(2, len(pattern["complements"]))
        dative_row = next(
            p for p in patterns
            if p["candidatePatternKey"] == "accusative-item-dative-beneficiary")
        dla_row = next(
            p for p in patterns
            if p["candidatePatternKey"] == "accusative-item-dla-genitive-beneficiary")
        self.assertFalse(next(
            c for c in dative_row["complements"] if c["type"] == "case"
            and c["role"] == "recipient")["required"])
        self.assertFalse(next(
            c for c in dla_row["complements"]
            if c.get("preposition") == "dla")["required"])
        # no maximal row combining both beneficiary modes
        self.assertFalse(any(
            len(p["complements"]) > 2 for p in patterns))

    def test_cieszyc_sie_preserves_lexical_sie_and_frozen_z_genitive_role(self):
        cieszyc = record(self.data, "cieszyć się")
        self.assertEqual("cieszyć się", cieszyc["canonicalLemma"])
        names = {item["canonicalLemma"] for item in self.data["lemmas"]}
        self.assertNotIn("cieszyć", names)
        z_pattern = next(
            p for p in cieszyc["candidateContent"]["patterns"]
            if p["candidatePatternKey"] == "z-genitive-realized-cause")
        self.assertEqual(
            [{"type": "preposition-case", "preposition": "z",
              "case": "genitive", "required": True, "role": "topic"}],
            z_pattern["complements"],
        )
        self.assertEqual(4, len(cieszyc["candidateContent"]["patterns"]))

    def test_martwic_sie_preserves_lexical_sie_and_no_bac_sie_transfer(self):
        martwic = record(self.data, "martwić się")
        self.assertEqual("martwić się", martwic["canonicalLemma"])
        names = {item["canonicalLemma"] for item in self.data["lemmas"]}
        self.assertNotIn("martwić", names)
        for pattern in martwic["candidateContent"]["patterns"]:
            for complement in pattern["complements"]:
                self.assertFalse(
                    complement.get("preposition") == "z"
                    and complement.get("case") == "genitive")
        self.assertEqual(4, len(martwic["candidateContent"]["patterns"]))

    def test_zgadzac_sie_two_meanings_and_agreement_direct_speech_has_no_partner(self):
        zgadzac = record(self.data, "zgadzać się")
        self.assertEqual("zgadzać się", zgadzac["canonicalLemma"])
        names = {item["canonicalLemma"] for item in self.data["lemmas"]}
        self.assertNotIn("zgadzać", names)
        content = zgadzac["candidateContent"]
        self.assertEqual(2, len(content["meanings"]))
        consent = [p for p in content["patterns"] if p["meaningKeyRef"] == "consent"]
        agreement = [p for p in content["patterns"]
                     if p["meaningKeyRef"] == "opinion-agreement"]
        self.assertEqual(4, len(consent))
        self.assertEqual(3, len(agreement))
        agreement_direct_speech = next(
            p for p in agreement
            if p["candidatePatternKey"] == "direct-speech-agreement")
        self.assertEqual(1, len(agreement_direct_speech["complements"]))
        self.assertEqual(
            "direct-speech",
            agreement_direct_speech["complements"][0]["clauseKind"])
        consent_direct_speech = next(
            p for p in consent
            if p["candidatePatternKey"] == "direct-speech-consent")
        self.assertEqual(1, len(consent_direct_speech["complements"]))
        # no z+Instrumental appears in any consent-owned pattern
        self.assertFalse(any(
            c.get("preposition") == "z" and c.get("case") == "instrumental"
            for p in consent for c in p["complements"]))
        # no na/infinitive/zeby appears in any agreement-owned pattern
        agreement_types = {
            (c["type"], c.get("preposition"), c.get("clauseKind"))
            for p in agreement for c in p["complements"]
        }
        self.assertFalse(any(t[1] == "na" for t in agreement_types))
        self.assertFalse(any(t[0] == "infinitive" for t in agreement_types))
        self.assertFalse(any(t[2] == "zeby" for t in agreement_types))

    def test_zapraszac_only_exact_na_do_no_gdzie_concretization(self):
        zapraszac = record(self.data, "zapraszać")
        patterns = zapraszac["candidateContent"]["patterns"]
        self.assertEqual(2, len(patterns))
        prepositions = {
            c.get("preposition")
            for p in patterns for c in p["complements"]
            if c["type"] == "preposition-case"
        }
        self.assertEqual({"na", "do"}, prepositions)

    def test_polecac_instruction_and_recommendation_meaning_split(self):
        polecac = record(self.data, "polecać")
        content = polecac["candidateContent"]
        self.assertEqual(2, len(content["meanings"]))
        instruction = [p for p in content["patterns"]
                       if p["meaningKeyRef"] == "directive-instruction"]
        recommendation = [p for p in content["patterns"]
                          if p["meaningKeyRef"] == "recommendation"]
        self.assertEqual(4, len(instruction))
        self.assertEqual(1, len(recommendation))
        # no infinitive or clause content in recommendation
        self.assertFalse(any(
            c["type"] in {"infinitive", "clause"}
            for p in recommendation for c in p["complements"]))
        a4 = next(p for p in instruction
                  if p["candidatePatternKey"] == "dative-accusative-action-noun")
        b1 = recommendation[0]
        self.assertEqual("dative-accusative-recommended-item",
                          b1["candidatePatternKey"])
        # A4 and B1 are structurally identical but meaning-owned distinctly
        a4_shape = sorted(json.dumps(c, sort_keys=True) for c in a4["complements"])
        b1_shape = sorted(json.dumps(c, sort_keys=True) for c in b1["complements"])
        self.assertEqual(a4_shape, b1_shape)
        self.assertNotEqual(a4["meaningKeyRef"], b1["meaningKeyRef"])
        meanings = {m["candidateMeaningKey"]: m for m in content["meanings"]}
        self.assertNotEqual(
            meanings["directive-instruction"]["internalScope"],
            meanings["recommendation"]["internalScope"])

    def test_radzic_dative_requiredness_asymmetry_and_no_sobie_or_z_instrumental(self):
        radzic = record(self.data, "radzić")
        self.assertEqual("radzić", radzic["canonicalLemma"])
        self.assertNotIn("requiredLexicalItems", radzic)
        patterns = radzic["candidateContent"]["patterns"]
        self.assertEqual(5, len(patterns))
        infinitive_row = next(
            p for p in patterns
            if p["candidatePatternKey"] == "dative-infinitive-advice")
        dative_in_infinitive = next(
            c for c in infinitive_row["complements"] if c["type"] == "case")
        self.assertFalse(dative_in_infinitive["required"])
        for p in patterns:
            if p["candidatePatternKey"] == "dative-infinitive-advice":
                continue
            dative = next(c for c in p["complements"] if c["type"] == "case"
                          and c["role"] == "recipient")
            self.assertTrue(dative["required"], p["candidatePatternKey"])
        # no z + Instrumental coping construction anywhere
        self.assertFalse(any(
            c.get("preposition") == "z" and c.get("case") == "instrumental"
            for p in patterns for c in p["complements"]))

    def test_pasowac_four_meanings_five_rows_three_all_optional(self):
        pasowac = record(self.data, "pasować")
        content = pasowac["candidateContent"]
        self.assertEqual(4, len(content["meanings"]))
        self.assertEqual(5, len(content["patterns"]))
        all_optional = [
            p for p in content["patterns"]
            if p["complements"] and not any(c["required"] for c in p["complements"])
        ]
        self.assertEqual(3, len(all_optional))
        self.assertEqual(
            {"do-genitive-fit-target", "na-accusative-fitted-object",
             "dative-expectation-holder"},
            {p["candidatePatternKey"] for p in all_optional},
        )
        sense5 = next(
            p for p in content["patterns"]
            if p["candidatePatternKey"] == "dative-expectation-holder")
        self.assertEqual("lexical-frame", sense5["relationType"])
        self.assertEqual(
            [{"type": "case", "case": "dative", "required": False,
              "role": "experiencer"}],
            sense5["complements"],
        )

    def test_moc_two_meanings_two_infinitive_rows_no_question_complement(self):
        moc = record(self.data, "móc")
        content = moc["candidateContent"]
        self.assertEqual(2, len(content["meanings"]))
        self.assertEqual(2, len(content["patterns"]))
        for pattern in content["patterns"]:
            self.assertEqual(
                [{"type": "infinitive", "required": True, "role": "content"}],
                pattern["complements"],
            )
        clause_kinds = {
            c.get("clauseKind")
            for p in content["patterns"] for c in p["complements"]
            if c["type"] == "clause"
        }
        self.assertEqual(set(), clause_kinds)

    def test_batch_6_live_guard_rules_are_present(self):
        registry = json.loads(RULES_PATH.read_text(encoding="utf-8"))
        rule_ids = {rule["ruleId"] for rule in registry["rules"]}
        for expected_id in EXPECTED_BATCH_6_RULE_IDS:
            self.assertIn(expected_id, rule_ids)
        self.assertEqual(21, len(EXPECTED_BATCH_6_RULE_IDS))
        self.assertEqual(2, registry["registryVersion"])
        # Batch 6 pins its own 21 rules, not the registry total: later batches
        # legitimately add rules, so a fixed total would be a moving-state
        # assertion of exactly the kind this historical lock avoids.
        self.assertGreaterEqual(len(registry["rules"]), 57)


if __name__ == "__main__":
    unittest.main()
