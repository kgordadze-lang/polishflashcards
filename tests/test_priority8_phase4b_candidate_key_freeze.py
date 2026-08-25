import copy
import hashlib
import json
import re
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

import sys

sys.path.insert(0, str(ROOT))

import validate_priority8_staging as validator  # noqa: E402


STAGING_PATH = ROOT / "editorial/priority-8-phase4-staging.json"
MANIFEST_PATH = ROOT / "editorial/priority-8-phase4-candidate-key-freeze.json"
FROZEN_DIGEST = "0d636b3c81c15f51e36558ef5d9c18e35b189b5f5a143003c283b4732f33be27"
KEY_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FROZEN_LEMMA_ORDER = (
    (1, "pracować"),
    (2, "iść"),
    (3, "chodzić"),
    (4, "jechać"),
    (5, "jeździć"),
    (6, "dojść"),
    (7, "dojechać"),
    (8, "wracać"),
    (9, "wrócić"),
    (10, "przyjść"),
    (11, "przyjechać"),
    (12, "wyjść"),
    (13, "wyjechać"),
    (14, "przynosić"),
    (15, "odpowiadać"),
    (16, "zamawiać"),
    (18, "zacząć"),
    (19, "kończyć"),
    (20, "pamiętać"),
    (21, "zapominać"),
    (22, "próbować"),
    (23, "pozwalać"),
    (24, "unikać"),
    (25, "wymagać"),
    (26, "należeć"),
    (27, "kłócić się"),
    (28, "pokazywać"),
    (29, "radzić sobie"),
    (30, "kupować"),
    (31, "kupić"),
    (32, "dawać"),
    (33, "dać"),
    (34, "brać"),
    (35, "wziąć"),
    (36, "czytać"),
    (38, "pisać"),
    (39, "napisać"),
    (40, "spotykać się"),
    (41, "spotkać się"),
    (42, "oglądać"),
    (43, "obejrzeć"),
    (44, "skończyć"),
    (45, "chcieć"),
    (46, "robić"),
    (47, "rozumieć"),
    (48, "mieszkać"),
    (49, "umówić się"),
    (50, "dzwonić"),
    (51, "powiedzieć"),
    (52, "gotować"),
    (53, "rezerwować"),
    (54, "cieszyć się"),
    (55, "martwić się"),
    (56, "zgadzać się"),
    (57, "zapraszać"),
    (58, "polecać"),
    (59, "radzić"),
    (60, "pasować"),
    (61, "móc"),
    (62, "musieć"),
    (63, "wiedzieć"),
    (64, "jeść"),
    (65, "pić"),
    (66, "kochać"),
    (67, "przepraszać"),
    (68, "życzyć"),
    (69, "korzystać"),
    (70, "uczyć"),
)
HD2_SOURCE_ROWS = (
    ("wracać", "return-to-earlier-place", "z-genitive-return-source", "z"),
    ("wrócić", "completed-return-to-earlier-place", "z-genitive-return-source", "z"),
    ("wyjść", "literal-exit-from-place", "z-genitive-source", "z"),
    ("wyjechać", "transport-departure", "z-genitive-source", "z"),
    ("kupować", "process-purchase", "seller-price-schema", "od"),
    ("kupić", "completed-purchase", "seller-price-schema", "od"),
    ("zamawiać", "commissioning-ordering", "u-genitive-provider", "u"),
)


def record(data, lemma):
    return next(item for item in data["lemmas"]
                if item["canonicalLemma"] == lemma)


def _canonical_bytes(projection):
    return json.dumps(
        projection,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def freeze_digest(projection):
    return hashlib.sha256(_canonical_bytes(projection)).hexdigest()


def projection_from_staging(data):
    result = []
    lemma_rows = sorted(data["lemmas"], key=lambda item: item["verificationOrder"])
    lemma_owners = [
        (item["verificationOrder"], item["canonicalLemma"])
        for item in lemma_rows
    ]
    if len(lemma_owners) != len(set(lemma_owners)):
        raise ValueError("duplicate lemma/order owner")

    for lemma in lemma_rows:
        content = lemma["candidateContent"]
        meaning_keys = [item["candidateMeaningKey"] for item in content["meanings"]]
        if len(meaning_keys) != len(set(meaning_keys)):
            raise ValueError("duplicate meaning owner")

        patterns_by_meaning = {key: [] for key in meaning_keys}
        pattern_owners = []
        for pattern in content["patterns"]:
            meaning_key = pattern["meaningKeyRef"]
            if meaning_key not in patterns_by_meaning:
                raise ValueError("orphan pattern meaning reference")
            owner = (meaning_key, pattern["candidatePatternKey"])
            pattern_owners.append(owner)
            patterns_by_meaning[meaning_key].append(pattern)
        if len(pattern_owners) != len(set(pattern_owners)):
            raise ValueError("duplicate pattern owner")

        examples_by_owner = {}
        for example in content["examples"]:
            owner = (example["meaningKeyRef"], example["patternKeyRef"])
            if owner in examples_by_owner:
                raise ValueError("duplicate example owner")
            examples_by_owner[owner] = example
        if Counter(pattern_owners) != Counter(examples_by_owner.keys()):
            raise ValueError("pattern/example ownership mismatch")

        projected_meanings = []
        for meaning_key in meaning_keys:
            projected_patterns = []
            for pattern in patterns_by_meaning[meaning_key]:
                pattern_key = pattern["candidatePatternKey"]
                example = examples_by_owner[(meaning_key, pattern_key)]
                projected_patterns.append({
                    "candidatePatternKey": pattern_key,
                    "example": {
                        "candidateExampleKey": example["candidateExampleKey"],
                    },
                })
            projected_meanings.append({
                "candidateMeaningKey": meaning_key,
                "patterns": projected_patterns,
            })
        result.append({
            "verificationOrder": lemma["verificationOrder"],
            "canonicalLemma": lemma["canonicalLemma"],
            "meanings": projected_meanings,
        })
    return result


def projection_from_manifest(manifest):
    if set(manifest) != {
        "freezeSchemaVersion", "priority", "phase", "status",
        "sourceStaging", "counts", "candidateKeyFreezeDigest", "lemmas",
    }:
        raise ValueError("unexpected manifest top-level shape")
    for lemma in manifest["lemmas"]:
        if set(lemma) != {"verificationOrder", "canonicalLemma", "meanings"}:
            raise ValueError("unexpected manifest lemma shape")
        for meaning in lemma["meanings"]:
            if set(meaning) != {"candidateMeaningKey", "patterns"}:
                raise ValueError("unexpected manifest meaning shape")
            for pattern in meaning["patterns"]:
                if set(pattern) != {"candidatePatternKey", "example"}:
                    raise ValueError("unexpected manifest pattern shape")
                if set(pattern["example"]) != {"candidateExampleKey"}:
                    raise ValueError("unexpected manifest example shape")
    return copy.deepcopy(manifest["lemmas"])


def all_projected_keys(projection):
    keys = []
    for lemma in projection:
        for meaning in lemma["meanings"]:
            keys.append(meaning["candidateMeaningKey"])
            for pattern in meaning["patterns"]:
                keys.append(pattern["candidatePatternKey"])
                keys.append(pattern["example"]["candidateExampleKey"])
    return keys


def walk(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


class Priority8Phase4BCandidateKeyFreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.staging_text = STAGING_PATH.read_text(encoding="utf-8")
        cls.manifest_text = MANIFEST_PATH.read_text(encoding="utf-8")
        cls.data = json.loads(cls.staging_text)
        cls.manifest = json.loads(cls.manifest_text)
        cls.live_projection = projection_from_staging(cls.data)
        cls.manifest_projection = projection_from_manifest(cls.manifest)

    def assert_freeze_detects(self, mutated_staging):
        try:
            projection = projection_from_staging(mutated_staging)
        except ValueError:
            return
        self.assertNotEqual(FROZEN_DIGEST, freeze_digest(projection))

    def test_exact_frozen_lemma_order(self):
        self.assertEqual(
            FROZEN_LEMMA_ORDER,
            tuple((item["verificationOrder"], item["canonicalLemma"])
                  for item in self.live_projection),
        )

    def test_exact_key_counts(self):
        meanings = sum(len(item["meanings"]) for item in self.live_projection)
        patterns = sum(
            len(meaning["patterns"])
            for item in self.live_projection for meaning in item["meanings"]
        )
        examples = patterns
        self.assertEqual((68, 95, 224, 224, 543),
                         (len(self.live_projection), meanings, patterns,
                          examples, meanings + patterns + examples))

    def test_live_and_manifest_hierarchies_are_exactly_equal(self):
        self.assertEqual(self.live_projection, self.manifest_projection)

    def test_freeze_digest_matches_live_and_manifest(self):
        self.assertEqual(FROZEN_DIGEST, freeze_digest(self.live_projection))
        self.assertEqual(FROZEN_DIGEST, freeze_digest(self.manifest_projection))
        self.assertEqual(FROZEN_DIGEST,
                         self.manifest["candidateKeyFreezeDigest"])

    def test_manifest_governance_envelope(self):
        self.assertEqual(1, self.manifest["freezeSchemaVersion"])
        self.assertEqual(8, self.manifest["priority"])
        self.assertEqual("4B", self.manifest["phase"])
        self.assertEqual("frozen", self.manifest["status"])
        self.assertEqual(
            {"phaseStep": self.data["phaseStep"],
             "stagingRevision": self.data["stagingRevision"]},
            self.manifest["sourceStaging"],
        )
        self.assertEqual(
            {"lemmas": 68, "meanings": 95, "patterns": 224,
             "examples": 224, "totalCandidateKeys": 543},
            self.manifest["counts"],
        )

    def test_manifest_serialization_is_deterministic(self):
        self.assertEqual(
            json.dumps(self.manifest, ensure_ascii=False, indent=2) + "\n",
            self.manifest_text,
        )

    def test_key_format_and_nonsemantic_dependency_hygiene(self):
        for key in all_projected_keys(self.live_projection):
            self.assertRegex(key, KEY_RE)
            tokens = key.split("-")
            self.assertFalse(any(token.isdigit() for token in tokens), key)
            self.assertFalse(
                {"p8", "phase4b", "batch", "order", "wsjp", "medak",
                 "evidence"} & set(tokens),
                key,
            )
            self.assertNotIn("vp-", key)

    def test_ownership_reference_integrity_and_one_example_per_pattern(self):
        self.assertEqual(self.live_projection, projection_from_staging(self.data))
        for lemma in self.live_projection:
            for meaning in lemma["meanings"]:
                for pattern in meaning["patterns"]:
                    self.assertEqual({"candidateExampleKey"},
                                     set(pattern["example"]))

    def test_old_czy_key_absent_and_new_interrogative_keys_exact(self):
        keys = all_projected_keys(self.live_projection)
        self.assertNotIn("czy-dependent-clause", keys)
        expected = {
            ("zapominać", "interrogative-forgotten-content"),
            ("kłócić się", "interrogative-disputed-content"),
        }
        actual = {
            (lemma["canonicalLemma"], pattern["candidatePatternKey"])
            for lemma in self.live_projection
            for meaning in lemma["meanings"]
            for pattern in meaning["patterns"]
            if pattern["candidatePatternKey"] in {
                "interrogative-forgotten-content",
                "interrogative-disputed-content",
            }
        }
        self.assertEqual(expected, actual)

    def test_hd2_source_semantic_keys_and_coarse_roles_are_preserved(self):
        for lemma, meaning_key, pattern_key, preposition in HD2_SOURCE_ROWS:
            item = record(self.data, lemma)
            pattern = next(
                candidate for candidate in item["candidateContent"]["patterns"]
                if candidate["meaningKeyRef"] == meaning_key
                and candidate["candidatePatternKey"] == pattern_key
            )
            complement = next(
                candidate for candidate in pattern["complements"]
                if candidate.get("preposition") == preposition
            )
            self.assertEqual("target", complement["role"])

    def test_no_stable_production_ids_in_staging_or_manifest(self):
        for document in (self.data, self.manifest):
            for key, value in walk(document):
                self.assertNotIn(key, validator.PRODUCTION_ID_FIELDS)
                if isinstance(value, str):
                    self.assertFalse(value.startswith("vp-"), value)

    def test_manifest_contains_identity_only(self):
        forbidden = {
            "learnerExplanationEn", "pl", "en", "glossesEn", "cefr",
            "teachingStatus", "priority", "register", "candidateOrigin",
            "stagingReviewStatus", "relationType", "complements",
        }
        nested_keys = {key for key, _ in walk(self.manifest["lemmas"])}
        self.assertTrue(forbidden.isdisjoint(nested_keys))

    def test_mutation_rename_meaning_key_is_caught(self):
        data = copy.deepcopy(self.data)
        item = record(data, "próbować")
        old = item["candidateContent"]["meanings"][0]["candidateMeaningKey"]
        new = old + "-renamed"
        item["candidateContent"]["meanings"][0]["candidateMeaningKey"] = new
        for collection in ("patterns", "examples"):
            for value in item["candidateContent"][collection]:
                if value["meaningKeyRef"] == old:
                    value["meaningKeyRef"] = new
        self.assert_freeze_detects(data)

    def test_mutation_rename_pattern_key_is_caught(self):
        data = copy.deepcopy(self.data)
        item = record(data, "pracować")
        pattern = item["candidateContent"]["patterns"][0]
        old = pattern["candidatePatternKey"]
        pattern["candidatePatternKey"] = old + "-renamed"
        item["candidateContent"]["examples"][0]["patternKeyRef"] = old + "-renamed"
        self.assert_freeze_detects(data)

    def test_mutation_rename_example_key_is_caught(self):
        data = copy.deepcopy(self.data)
        record(data, "pracować")["candidateContent"]["examples"][0][
            "candidateExampleKey"
        ] = "renamed-primary"
        self.assert_freeze_detects(data)

    def test_mutation_move_pattern_to_different_meaning_is_caught(self):
        data = copy.deepcopy(self.data)
        item = record(data, "próbować")
        pattern = item["candidateContent"]["patterns"][0]
        old_meaning = pattern["meaningKeyRef"]
        new_meaning = item["candidateContent"]["meanings"][1]["candidateMeaningKey"]
        pattern["meaningKeyRef"] = new_meaning
        example = next(value for value in item["candidateContent"]["examples"]
                       if value["meaningKeyRef"] == old_meaning
                       and value["patternKeyRef"] == pattern["candidatePatternKey"])
        example["meaningKeyRef"] = new_meaning
        self.assert_freeze_detects(data)

    def test_mutation_reassign_example_to_another_pattern_is_caught(self):
        data = copy.deepcopy(self.data)
        item = record(data, "iść")
        example = item["candidateContent"]["examples"][0]
        example["patternKeyRef"] = item["candidateContent"]["patterns"][1][
            "candidatePatternKey"
        ]
        self.assert_freeze_detects(data)

    def test_mutation_swap_two_pattern_keys_is_caught(self):
        data = copy.deepcopy(self.data)
        patterns = record(data, "iść")["candidateContent"]["patterns"]
        patterns[0]["candidatePatternKey"], patterns[1]["candidatePatternKey"] = (
            patterns[1]["candidatePatternKey"], patterns[0]["candidatePatternKey"]
        )
        self.assert_freeze_detects(data)

    def test_mutation_restore_old_czy_key_is_caught(self):
        data = copy.deepcopy(self.data)
        item = record(data, "zapominać")
        pattern = next(value for value in item["candidateContent"]["patterns"]
                       if value["candidatePatternKey"] ==
                       "interrogative-forgotten-content")
        pattern["candidatePatternKey"] = "czy-dependent-clause"
        example = next(value for value in item["candidateContent"]["examples"]
                       if value["patternKeyRef"] ==
                       "interrogative-forgotten-content")
        example["patternKeyRef"] = "czy-dependent-clause"
        self.assert_freeze_detects(data)

    def test_mutation_source_key_to_target_key_is_caught(self):
        data = copy.deepcopy(self.data)
        item = record(data, "wracać")
        pattern = next(value for value in item["candidateContent"]["patterns"]
                       if value["candidatePatternKey"] ==
                       "z-genitive-return-source")
        pattern["candidatePatternKey"] = "z-genitive-return-target"
        example = next(value for value in item["candidateContent"]["examples"]
                       if value["patternKeyRef"] == "z-genitive-return-source")
        example["patternKeyRef"] = "z-genitive-return-target"
        self.assert_freeze_detects(data)

    def test_mutation_remove_one_key_is_caught(self):
        data = copy.deepcopy(self.data)
        item = record(data, "pracować")
        item["candidateContent"]["patterns"].clear()
        item["candidateContent"]["examples"].clear()
        self.assert_freeze_detects(data)

    def test_mutation_add_one_key_is_caught(self):
        data = copy.deepcopy(self.data)
        item = record(data, "pracować")
        pattern = copy.deepcopy(item["candidateContent"]["patterns"][0])
        example = copy.deepcopy(item["candidateContent"]["examples"][0])
        pattern["candidatePatternKey"] = "added-freeze-mutation"
        example["patternKeyRef"] = "added-freeze-mutation"
        item["candidateContent"]["patterns"].append(pattern)
        item["candidateContent"]["examples"].append(example)
        self.assert_freeze_detects(data)

    def test_prose_only_mutation_does_not_change_digest(self):
        data = copy.deepcopy(self.data)
        pattern = record(data, "pracować")["candidateContent"]["patterns"][0]
        pattern["learnerExplanationEn"] += " Editorial wording may change."
        self.assertEqual(FROZEN_DIGEST,
                         freeze_digest(projection_from_staging(data)))


if __name__ == "__main__":
    unittest.main()
