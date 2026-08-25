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
MATRIX_PATH = ROOT / "reports/priority-8-phase-4b7-schema-matrix.md"
RULES_PATH = ROOT / "tests/fixtures/priority8_phase4b_authoring_rules.json"
MATRIX_APPROVED_SHA256 = (
    "8b152b204485001f921d54c1b8941f9e2c2173fbc910cd52c57b9e240240212a"
)
BATCH_7 = tuple(lemma for _, lemma in validator.AUTHORING_BATCHES[6])
BATCH_7_DIGEST_FIELDS = (
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
BATCH_7_APPROVED_DIGEST = (
    "a2d34c616d416f6a36f2346a2c4190522f1102087b3745ab0605be29c5430d9e"
)
ALLOWED_REVIEW_STATUSES = {
    "draft", "independently-reviewed", "human-approved",
}
PRODUCTION_ID_KEY_NAMES = validator.PRODUCTION_ID_FIELDS
ORDER_NUMBER_RE = re.compile(r"(?:^|-)0*[1-9][0-9]*(?:-|$)")
EXPECTED_BATCH_7_RULE_IDS = (
    "p8-4b-musiec-exact-pattern-shapes",
    "p8-4b-wiedziec-exact-pattern-shapes",
    "p8-4b-wiedziec-authorized-preposition-cases",
    "p8-4b-jesc-exact-pattern-shapes",
    "p8-4b-jesc-no-lexical-genitive",
    "p8-4b-pic-exact-pattern-shapes",
    "p8-4b-pic-no-lexical-genitive",
    "p8-4b-kochac-exact-pattern-shapes",
    "p8-4b-przepraszac-exact-pattern-shapes",
    "p8-4b-przepraszac-authorized-preposition-cases",
    "p8-4b-zyczyc-exact-pattern-shapes",
    "p8-4b-korzystac-exact-pattern-shapes",
    "p8-4b-korzystac-authorized-preposition-cases",
    "p8-4b-uczyc-exact-pattern-shapes",
    "p8-4b-uczyc-authorized-preposition-cases",
)


def record(data, lemma):
    return next(item for item in data["lemmas"]
                if item["canonicalLemma"] == lemma)


def pattern(item, key):
    return next(p for p in item["candidateContent"]["patterns"]
                if p["candidatePatternKey"] == key)


def walk(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def shape(complements):
    return sorted(
        json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        for item in complements
    )


def batch_digest(records):
    projection = [
        {field: item[field] for field in BATCH_7_DIGEST_FIELDS if field in item}
        for item in records
    ]
    canonical = json.dumps(
        projection,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


class Priority8Phase4B7Batch07Tests(unittest.TestCase):
    """Historical regression test for approved Batch 7 authoring.

    Follows the Batch 1-6 future-safe architecture: this test pins the
    approved Batch 7 content digest and does NOT assert phaseStep,
    stagingRevision, corpus-wide draft boundaries, the future-empty count, or
    the registry total. Batch 7 is the last authoring batch, so the
    future-empty set is currently zero -- but this lock must stay valid
    through the later 68-lemma reconciliation and any review-status
    progression, so it never depends on those moving values.
    """

    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(STAGING_PATH.read_text(encoding="utf-8"))
        cls.batch_records = [record(cls.data, lemma) for lemma in BATCH_7]

    def test_live_staging_validates(self):
        self.assertEqual([], validator.validate_data(self.data))

    def test_frozen_corpus_and_exact_batch_membership(self):
        self.assertEqual(68, self.data["frozenFullPatternCount"])
        self.assertEqual(
            validator.AUTHORING_BATCHES[6],
            tuple(
                (item["verificationOrder"], item["canonicalLemma"])
                for item in self.batch_records
            ),
        )
        self.assertEqual(
            (62, 63, 64, 65, 66, 67, 68, 69, 70),
            tuple(item["verificationOrder"] for item in self.batch_records),
        )
        self.assertEqual(
            ("musieć", "wiedzieć", "jeść", "pić", "kochać", "przepraszać",
             "życzyć", "korzystać", "uczyć"),
            tuple(item["canonicalLemma"] for item in self.batch_records),
        )
        names = {item["canonicalLemma"] for item in self.batch_records}
        # móc belongs to Batch 6; the reflexive/sobie identities are separate
        # lemmas that receive no Phase 4B full-pattern record at all.
        self.assertNotIn("móc", names)
        self.assertNotIn("uczyć się", names)
        self.assertNotIn("życzyć sobie", names)
        corpus = {item["canonicalLemma"] for item in self.data["lemmas"]}
        self.assertNotIn("uczyć się", corpus)
        self.assertNotIn("życzyć sobie", corpus)

    def test_frozen_schema_matrix_is_unchanged(self):
        self.assertEqual(
            MATRIX_APPROVED_SHA256,
            hashlib.sha256(MATRIX_PATH.read_bytes()).hexdigest(),
        )

    def test_exact_approved_batch_content_digest(self):
        self.assertEqual(BATCH_7_APPROVED_DIGEST,
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
        self.assertEqual(23, sum(
            len(item["candidateContent"]["patterns"])
            for item in self.batch_records))
        self.assertEqual(23, sum(
            len(item["candidateContent"]["examples"])
            for item in self.batch_records))

    def test_per_lemma_meaning_and_pattern_counts_match_the_frozen_matrix(self):
        expected = {
            "musieć": (1, 1),
            "wiedzieć": (1, 4),
            "jeść": (1, 1),
            "pić": (1, 1),
            "kochać": (3, 4),
            "przepraszać": (1, 2),
            "życzyć": (1, 2),
            "korzystać": (2, 2),
            "uczyć": (2, 6),
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
            "musieć": {"necessity-obligation"},
            "wiedzieć": {"factual-knowledge"},
            "jeść": {"food-consumption"},
            "pić": {"liquid-consumption"},
            "kochać": {"person-love", "idea-or-place-attachment",
                       "strong-liking"},
            "przepraszać": {"apology"},
            "życzyć": {"good-wishes"},
            "korzystać": {"resource-use", "benefit-from-advantage"},
            "uczyć": {"teaching-instruction", "school-subject-teaching"},
        }
        expected_pattern_keys = {
            "musieć": {"infinitive-required-action"},
            "wiedzieć": {"accusative-known-content",
                         "o-locative-known-topic",
                         "ze-known-proposition",
                         "interrogative-queried-content"},
            "jeść": {"accusative-food-instrumental-implement"},
            "pić": {"accusative-drink-object"},
            "kochać": {"accusative-loved-person",
                       "accusative-cherished-idea-or-place",
                       "accusative-strongly-liked-thing",
                       "infinitive-strongly-liked-activity"},
            "przepraszać": {"accusative-person-za-accusative-offence",
                            "accusative-person-ze-explanation"},
            "życzyć": {"dative-recipient-genitive-wished-thing",
                       "dative-recipient-zeby-wished-event"},
            "korzystać": {"z-genitive-used-resource",
                          "z-genitive-source-of-benefit"},
            "uczyć": {"accusative-learner-genitive-taught-content",
                      "accusative-learner-infinitive-taught-skill",
                      "accusative-learner-ze-taught-proposition",
                      "accusative-learner-interrogative-taught-content",
                      "accusative-person-o-locative-taught-topic",
                      "accusative-learner-genitive-school-subject"},
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
                self.assertNotRegex(
                    key, r"(?:^|-)(?:batch|order|verification|hold|sense)(?:-|$)")

    def test_every_pattern_uses_the_frozen_lexical_frame_relation(self):
        for item in self.batch_records:
            for candidate in item["candidateContent"]["patterns"]:
                self.assertEqual("lexical-frame", candidate["relationType"],
                                 item["canonicalLemma"])

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
        # Polish sentences must be pedagogically distinct, but English
        # translations are NOT required to be globally unique: naturalness
        # outranks an artificial uniqueness constraint (Phase 4B4 precedent).
        examples = [
            example for item in self.batch_records
            for example in item["candidateContent"]["examples"]
        ]
        self.assertEqual(23, len(examples))
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

    def test_every_required_complement_type_is_visible_in_its_example(self):
        # Structural sanity: each example belongs to its pattern and each
        # pattern has exactly one example (ownership is checked above); this
        # additionally pins that no Batch 7 pattern was left exampleless.
        for item in self.batch_records:
            content = item["candidateContent"]
            for candidate in content["patterns"]:
                owned = [
                    example for example in content["examples"]
                    if example["patternKeyRef"] == candidate["candidatePatternKey"]
                    and example["meaningKeyRef"] == candidate["meaningKeyRef"]
                ]
                self.assertEqual(1, len(owned), candidate["candidatePatternKey"])
                self.assertTrue(owned[0]["pl"].strip())
                self.assertTrue(owned[0]["en"].strip())

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
            if item["canonicalLemma"] in BATCH_7
        }
        self.assertEqual(
            expected,
            {item["canonicalLemma"]: item["bindingConstraints"]
             for item in self.batch_records},
        )
        # All nine Batch 7 records are KEEP VERIFIED with fit `compatible`.
        self.assertTrue(all(
            item["bindingConstraints"] == [] for item in self.batch_records))

    # ------------------------------------------------------------------
    # Targeted frozen-matrix invariants
    # ------------------------------------------------------------------

    def test_musiec_has_exactly_one_infinitive_pattern(self):
        musiec = record(self.data, "musieć")
        content = musiec["candidateContent"]
        self.assertEqual(1, len(content["meanings"]))
        self.assertEqual(1, len(content["patterns"]))
        self.assertEqual(
            [{"type": "infinitive", "required": True, "role": "content"}],
            content["patterns"][0]["complements"],
        )

    def test_wiedziec_four_alternatives_no_skad_no_czy(self):
        wiedziec = record(self.data, "wiedzieć")
        content = wiedziec["candidateContent"]
        self.assertEqual(1, len(content["meanings"]))
        self.assertEqual(4, len(content["patterns"]))
        for candidate in content["patterns"]:
            self.assertEqual(1, len(candidate["complements"]))
            self.assertTrue(candidate["complements"][0]["required"])
        prepositions = {
            (c.get("preposition"), c.get("case"))
            for p in content["patterns"] for c in p["complements"]
            if c["type"] == "preposition-case"
        }
        # exactly the one authorized preposition-case signature; no od/z SKĄD
        self.assertEqual({("o", "locative")}, prepositions)
        clause_kinds = {
            c["clauseKind"] for p in content["patterns"]
            for c in p["complements"] if c["type"] == "clause"
        }
        self.assertEqual({"ze", "interrogative"}, clause_kinds)
        self.assertNotIn("czy", clause_kinds)

    def test_jesc_is_all_optional_with_means_role_and_no_genitive(self):
        jesc = record(self.data, "jeść")
        content = jesc["candidateContent"]
        self.assertEqual(1, len(content["meanings"]))
        self.assertEqual(1, len(content["patterns"]))
        complements = content["patterns"][0]["complements"]
        self.assertEqual(2, len(complements))
        self.assertTrue(all(not c["required"] for c in complements))
        self.assertEqual(
            shape([
                {"type": "case", "case": "accusative", "required": False,
                 "role": "object"},
                {"type": "case", "case": "instrumental", "required": False,
                 "role": "means"},
            ]),
            shape(complements),
        )
        self.assertFalse(any(
            c.get("case") == "genitive"
            for p in content["patterns"] for c in p["complements"]))

    def test_pic_requires_accusative_and_has_no_genitive(self):
        pic = record(self.data, "pić")
        content = pic["candidateContent"]
        self.assertEqual(1, len(content["patterns"]))
        self.assertEqual(
            [{"type": "case", "case": "accusative", "required": True,
              "role": "object"}],
            content["patterns"][0]["complements"],
        )
        self.assertFalse(any(
            c.get("case") == "genitive"
            for p in content["patterns"] for c in p["complements"]))

    def test_kochac_three_meanings_infinitive_only_in_strong_liking(self):
        kochac = record(self.data, "kochać")
        content = kochac["candidateContent"]
        self.assertEqual(3, len(content["meanings"]))
        self.assertEqual(4, len(content["patterns"]))
        infinitive_owners = {
            p["meaningKeyRef"] for p in content["patterns"]
            if any(c["type"] == "infinitive" for c in p["complements"])
        }
        self.assertEqual({"strong-liking"}, infinitive_owners)
        accusative_rows = [
            p for p in content["patterns"]
            if shape(p["complements"]) == shape([
                {"type": "case", "case": "accusative", "required": True,
                 "role": "object"}])
        ]
        self.assertEqual(3, len(accusative_rows))
        # the three identical shapes are owned by three distinct meanings
        self.assertEqual(
            {"person-love", "idea-or-place-attachment", "strong-liking"},
            {p["meaningKeyRef"] for p in accusative_rows},
        )
        # the semantic split lives in the editorial fields, so they must differ
        scopes = [m["internalScope"] for m in content["meanings"]]
        self.assertEqual(len(scopes), len(set(scopes)))
        glosses = [tuple(m["glossesEn"]) for m in content["meanings"]]
        self.assertEqual(len(glosses), len(set(glosses)))
        explanations = [p["learnerExplanationEn"] for p in content["patterns"]]
        self.assertEqual(len(explanations), len(set(explanations)))

    def test_przepraszac_interlocutor_role_and_requiredness_asymmetry(self):
        przepraszac = record(self.data, "przepraszać")
        content = przepraszac["candidateContent"]
        self.assertEqual(1, len(content["meanings"]))
        self.assertEqual(2, len(content["patterns"]))
        za_row = pattern(przepraszac, "accusative-person-za-accusative-offence")
        ze_row = pattern(przepraszac, "accusative-person-ze-explanation")
        za_person = next(c for c in za_row["complements"] if c["type"] == "case")
        ze_person = next(c for c in ze_row["complements"] if c["type"] == "case")
        self.assertEqual("interlocutor", za_person["role"])
        self.assertEqual("interlocutor", ze_person["role"])
        self.assertTrue(za_person["required"])
        self.assertFalse(ze_person["required"])
        # no maximal row combining za + że
        for candidate in content["patterns"]:
            self.assertEqual(2, len(candidate["complements"]))
        self.assertFalse(any(
            any(c.get("preposition") == "za" for c in p["complements"])
            and any(c["type"] == "clause" for c in p["complements"])
            for p in content["patterns"]))

    def test_zyczyc_alternatives_required_dative_and_no_sobie_drift(self):
        zyczyc = record(self.data, "życzyć")
        self.assertEqual("życzyć", zyczyc["canonicalLemma"])
        self.assertNotIn("requiredLexicalItems", zyczyc)
        content = zyczyc["candidateContent"]
        self.assertEqual(1, len(content["meanings"]))
        self.assertEqual(2, len(content["patterns"]))
        for candidate in content["patterns"]:
            dative = next(c for c in candidate["complements"]
                          if c["type"] == "case" and c["case"] == "dative")
            self.assertTrue(dative["required"])
            self.assertEqual("recipient", dative["role"])
            self.assertEqual(2, len(candidate["complements"]))
        # Genitive and żeby are alternatives, never cumulative
        for candidate in content["patterns"]:
            has_genitive = any(c.get("case") == "genitive"
                               for c in candidate["complements"])
            has_clause = any(c["type"] == "clause"
                             for c in candidate["complements"])
            # exactly one of the two content shapes per row, never both
            self.assertNotEqual(has_genitive, has_clause)
        self.assertFalse(any(
            c["type"] == "infinitive"
            for p in content["patterns"] for c in p["complements"]))
        # no example may shift the lexical identity to `życzyć sobie`
        for example in content["examples"]:
            self.assertNotIn("sobie", example["pl"].lower())

    def test_korzystac_two_meanings_identical_rows_distinct_semantics(self):
        korzystac = record(self.data, "korzystać")
        content = korzystac["candidateContent"]
        self.assertEqual(2, len(content["meanings"]))
        self.assertEqual(2, len(content["patterns"]))
        shapes = [shape(p["complements"]) for p in content["patterns"]]
        self.assertEqual(shapes[0], shapes[1])
        self.assertEqual(
            shape([{"type": "preposition-case", "preposition": "z",
                    "case": "genitive", "required": True, "role": "object"}]),
            shapes[0],
        )
        self.assertEqual(
            {"resource-use", "benefit-from-advantage"},
            {p["meaningKeyRef"] for p in content["patterns"]},
        )
        scopes = [m["internalScope"] for m in content["meanings"]]
        self.assertEqual(len(scopes), len(set(scopes)))
        glosses = [tuple(m["glossesEn"]) for m in content["meanings"]]
        self.assertEqual(len(glosses), len(set(glosses)))
        explanations = [p["learnerExplanationEn"] for p in content["patterns"]]
        self.assertEqual(len(explanations), len(set(explanations)))

    def test_uczyc_six_alternatives_no_maximal_frame_no_gdzie_no_reflexive(self):
        uczyc = record(self.data, "uczyć")
        self.assertEqual("uczyć", uczyc["canonicalLemma"])
        self.assertNotIn("requiredLexicalItems", uczyc)
        content = uczyc["candidateContent"]
        self.assertEqual(2, len(content["meanings"]))
        self.assertEqual(6, len(content["patterns"]))
        teaching = [p for p in content["patterns"]
                    if p["meaningKeyRef"] == "teaching-instruction"]
        school = [p for p in content["patterns"]
                  if p["meaningKeyRef"] == "school-subject-teaching"]
        self.assertEqual(5, len(teaching))
        self.assertEqual(1, len(school))
        # strict alternatives: every row has exactly two complements
        for candidate in content["patterns"]:
            self.assertEqual(2, len(candidate["complements"]),
                             candidate["candidatePatternKey"])
        # sense 1 complements are all required
        for candidate in teaching:
            self.assertTrue(all(c["required"] for c in candidate["complements"]),
                            candidate["candidatePatternKey"])
        # sense 2 learner optional, subject Genitive required
        school_row = school[0]
        learner = next(c for c in school_row["complements"]
                       if c.get("case") == "accusative")
        subject = next(c for c in school_row["complements"]
                       if c.get("case") == "genitive")
        self.assertFalse(learner["required"])
        self.assertTrue(subject["required"])
        # no concrete place government derived from GDZIE
        prepositions = {
            (c.get("preposition"), c.get("case"))
            for p in content["patterns"] for c in p["complements"]
            if c["type"] == "preposition-case"
        }
        self.assertEqual({("o", "locative")}, prepositions)
        # no bare uczyć się shape (every row carries the Accusative learner)
        for candidate in content["patterns"]:
            self.assertTrue(any(c.get("case") == "accusative"
                                for c in candidate["complements"]),
                            candidate["candidatePatternKey"])
        # non-reflexive identity in every example
        for example in content["examples"]:
            tokens = re.findall(r"[^\W\d_]+", example["pl"], flags=re.UNICODE)
            self.assertNotIn("się", [t.lower() for t in tokens])

    def test_batch_7_clause_inventory_is_exact(self):
        clause_rows = [
            (item["canonicalLemma"], c["clauseKind"])
            for item in self.batch_records
            for p in item["candidateContent"]["patterns"]
            for c in p["complements"]
            if c["type"] == "clause"
        ]
        self.assertEqual(6, len(clause_rows))
        self.assertEqual(
            Counter({"ze": 3, "interrogative": 2, "zeby": 1}),
            Counter(kind for _, kind in clause_rows),
        )
        self.assertEqual(
            {("wiedzieć", "ze"), ("wiedzieć", "interrogative"),
             ("przepraszać", "ze"), ("życzyć", "zeby"),
             ("uczyć", "ze"), ("uczyć", "interrogative")},
            set(clause_rows),
        )
        # no direct speech and no czy clauseKind anywhere in Batch 7
        self.assertNotIn("direct-speech", {kind for _, kind in clause_rows})
        self.assertNotIn("czy", {kind for _, kind in clause_rows})

    def test_batch_7_has_exactly_one_all_optional_pattern(self):
        all_optional = [
            (item["canonicalLemma"], p["candidatePatternKey"])
            for item in self.batch_records
            for p in item["candidateContent"]["patterns"]
            if p["complements"] and not any(c["required"] for c in p["complements"])
        ]
        self.assertEqual(
            [("jeść", "accusative-food-instrumental-implement")], all_optional)
        self.assertFalse(any(
            not p["complements"]
            for item in self.batch_records
            for p in item["candidateContent"]["patterns"]))

    def test_batch_7_live_guard_rules_are_present(self):
        registry = json.loads(RULES_PATH.read_text(encoding="utf-8"))
        rule_ids = {rule["ruleId"] for rule in registry["rules"]}
        for expected_id in EXPECTED_BATCH_7_RULE_IDS:
            self.assertIn(expected_id, rule_ids)
        self.assertEqual(15, len(EXPECTED_BATCH_7_RULE_IDS))
        self.assertEqual(2, registry["registryVersion"])
        # presence, never a registry total: later phases may add rules
        self.assertGreaterEqual(len(registry["rules"]), 72)


if __name__ == "__main__":
    unittest.main()
