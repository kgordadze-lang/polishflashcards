import copy
import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

import sys

sys.path.insert(0, str(ROOT))

import priority8_phase4c1_stable_ids as phase4c1  # noqa: E402


FROZEN_FILE_SHA256 = {
    "editorial/priority-8-phase4-candidate-key-freeze.json":
        "b74bff54122ffb25c5ce8215e5bf28f8aa8823eabc2528cae8b1066a7eb1ab8b",
    "editorial/priority-8-phase4-staging.json":
        "6ba1bcab43feeee5bfb99a5ac67eace8befa12c3df67f44bfb94191bf1a80adc",
    "content/verb-patterns.json":
        "889b44aa7f87f25325364188a9283a36b22aa6d5d491fc347bb7be73072ba14d",
    "priority7_tooling.py":
        "4fda51f3ba53c60d524a067037b106414921db71663feddbd5ac0143b7f7d8e3",
    "priority8_phase1_transition.py":
        "ebf3d05381d11ab1c0ffa3b6a8329e9486320ef3c69cf2b90642d53910de64ef",
}
METADATA_ONLY = {"zaczynać", "przeczytać"}
SOURCE_ROWS = {
    ("wracać", "return-to-earlier-place", "z-genitive-return-source"),
    ("wrócić", "completed-return-to-earlier-place", "z-genitive-return-source"),
    ("wyjść", "literal-exit-from-place", "z-genitive-source"),
    ("wyjechać", "transport-departure", "z-genitive-source"),
    ("kupować", "process-purchase", "seller-price-schema"),
    ("kupić", "completed-purchase", "seller-price-schema"),
    ("zamawiać", "commissioning-ordering", "u-genitive-provider"),
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_staging_lemma(staging, canonical):
    return next(row for row in staging["lemmas"]
                if row["canonicalLemma"] == canonical)


def find_manifest_lemma(manifest, canonical):
    return next(row for row in manifest["lemmas"]
                if row["canonicalLemma"] == canonical)


class Priority8Phase4C1StableIdTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = phase4c1.read_json(phase4c1.FREEZE_PATH)
        cls.staging = phase4c1.read_json(phase4c1.STAGING_PATH)
        cls.runtime = phase4c1.read_json(phase4c1.RUNTIME_PATH)
        cls.persisted = phase4c1.read_json(phase4c1.MAP_PATH)
        cls.projection = phase4c1.verify_freeze_gate(cls.manifest, cls.staging)
        cls.generated = phase4c1.build_map(cls.manifest, cls.staging)
        cls.allocations = cls.generated["allocations"]
        cls.released = phase4c1.released_identity_rows(cls.runtime)

    def assert_phase4c1_error(self, function, *args, **kwargs):
        with self.assertRaises(phase4c1.Phase4C1Error):
            function(*args, **kwargs)

    def test_01_candidate_freeze_digest_is_exact(self):
        self.assertEqual(phase4c1.FROZEN_DIGEST,
                         phase4c1.freeze_digest(self.projection))
        self.assertEqual(phase4c1.FROZEN_DIGEST,
                         self.manifest["candidateKeyFreezeDigest"])

    def test_02_manifest_and_live_candidate_hierarchies_are_exact(self):
        self.assertEqual(
            phase4c1.projection_from_manifest(self.manifest),
            phase4c1.projection_from_staging(self.staging),
        )

    def test_03_frozen_sources_allocator_and_canonical_bytes_are_unchanged(self):
        for relative, expected in FROZEN_FILE_SHA256.items():
            self.assertEqual(expected, sha256(ROOT / relative), relative)

    def test_04_all_154_released_ids_reproduce_exactly(self):
        counts = Counter(row["kind"] for row in self.released)
        self.assertEqual(
            {"lemma": 30, "meaning": 34, "pattern": 45, "example": 45},
            dict(counts),
        )
        self.assertEqual(154, len(self.released))
        self.assertEqual(154, len({row["id"] for row in self.released}))

    def test_05_exactly_611_new_identities_are_allocated(self):
        counts = Counter(row["kind"] for row in self.allocations)
        self.assertEqual(
            {"lemma": 68, "meaning": 95, "pattern": 224, "example": 224},
            dict(counts),
        )
        self.assertEqual(611, len(self.allocations))

    def test_06_namespace_counts_and_syntax_are_exact(self):
        expected_prefix = {
            "lemma": "vp-l-", "meaning": "vp-m-",
            "pattern": "vp-p-", "example": "vp-e-",
        }
        for row in self.allocations:
            self.assertTrue(row["id"].startswith(expected_prefix[row["kind"]]))
            self.assertRegex(row["id"], phase4c1.tooling.ID_RES[row["kind"]])

    def test_07_released_and_new_union_is_765_with_zero_collisions(self):
        released_ids = {row["id"] for row in self.released}
        new_ids = {row["id"] for row in self.allocations}
        self.assertEqual(611, len(new_ids))
        self.assertFalse(released_ids & new_ids)
        self.assertEqual(765, len(released_ids | new_ids))

    def test_08_allocation_is_byte_identical_across_independent_runs(self):
        run_one = phase4c1.serialized(phase4c1.build_map())
        run_two = phase4c1.serialized(phase4c1.build_map())
        self.assertEqual(run_one, run_two)

    def test_09_persisted_map_equals_independent_regeneration(self):
        self.assertEqual(self.generated, self.persisted)
        self.assertEqual(
            phase4c1.serialized(self.generated),
            phase4c1.MAP_PATH.read_text(encoding="utf-8"),
        )
        summary = phase4c1.validate_map(self.persisted)
        self.assertEqual((154, 611, 765), (
            summary["releasedTotal"], summary["newTotal"], summary["unionTotal"]))

    def test_10_parent_ownership_is_present_and_recomputes_every_id(self):
        by_identity = {
            phase4c1.identity_key(row): row for row in self.allocations
        }
        for row in self.allocations:
            parent_id = phase4c1.parent_id_for_row(row, by_identity)
            if row["kind"] == "lemma":
                self.assertIsNone(parent_id)
            else:
                self.assertIn(parent_id, {item["id"] for item in self.allocations})
            self.assertEqual(
                row["id"], phase4c1.expected_id_for_row(row, by_identity))

    def test_11_metadata_only_identities_receive_zero_ids(self):
        allocated_lemmas = {row["canonicalLemma"] for row in self.allocations}
        self.assertTrue(METADATA_ONLY.isdisjoint(allocated_lemmas))
        staging_text = phase4c1.STAGING_PATH.read_text(encoding="utf-8")
        self.assertTrue(all(name in staging_text for name in METADATA_ONLY))

    def test_12_no_exercise_namespace_is_allocated(self):
        self.assertFalse(any(row["id"].startswith("vp-x-")
                             for row in self.allocations))
        self.assertNotIn("exercise", {row["kind"] for row in self.allocations})

    def test_13_temporary_target_role_does_not_contaminate_source_identity(self):
        changed = copy.deepcopy(self.staging)
        changed_count = 0
        for lemma_key, meaning_key, pattern_key in SOURCE_ROWS:
            lemma = find_staging_lemma(changed, lemma_key)
            pattern = next(
                row for row in lemma["candidateContent"]["patterns"]
                if row["meaningKeyRef"] == meaning_key and
                row["candidatePatternKey"] == pattern_key)
            for complement in pattern["complements"]:
                if complement["role"] == "target":
                    complement["role"] = "source"
                    changed_count += 1
        self.assertGreaterEqual(changed_count, 7)
        self.assertEqual(self.generated, phase4c1.build_map(self.manifest, changed))

    def test_14_candidate_wording_mutation_does_not_change_ids(self):
        changed = copy.deepcopy(self.staging)
        content = changed["lemmas"][0]["candidateContent"]
        content["meanings"][0]["glossesEn"][0] = "mutated nonidentity wording"
        content["patterns"][0]["learnerExplanationEn"] = "mutated explanation"
        content["examples"][0]["pl"] = "Mutated learner-facing example."
        content["examples"][0]["en"] = "Mutated learner-facing example."
        self.assertEqual(self.generated, phase4c1.build_map(self.manifest, changed))

    def test_15_candidate_key_rename_changes_id_and_is_rejected_by_freeze_gate(self):
        manifest = copy.deepcopy(self.manifest)
        staging = copy.deepcopy(self.staging)
        old_key = manifest["lemmas"][0]["meanings"][0]["candidateMeaningKey"]
        new_key = old_key + "-renamed"
        manifest["lemmas"][0]["meanings"][0]["candidateMeaningKey"] = new_key
        content = staging["lemmas"][0]["candidateContent"]
        content["meanings"][0]["candidateMeaningKey"] = new_key
        for row in content["patterns"] + content["examples"]:
            if row["meaningKeyRef"] == old_key:
                row["meaningKeyRef"] = new_key
        old_ids = {phase4c1.identity_key(row): row["id"] for row in self.allocations}
        mutated_projection = phase4c1.projection_from_staging(staging)
        mutated_rows = phase4c1.allocate_projection(mutated_projection)
        changed_id = next(row["id"] for row in mutated_rows
                          if row["kind"] == "meaning" and row["meaningKey"] == new_key)
        old_id = next(entity_id for key, entity_id in old_ids.items()
                      if key[0] == "pracować" and key[1] == old_key and key[2] is None)
        self.assertNotEqual(old_id, changed_id)
        self.assert_phase4c1_error(phase4c1.build_map, manifest, staging)

    def test_16_reparenting_changes_identity_and_is_rejected(self):
        manifest = copy.deepcopy(self.manifest)
        staging = copy.deepcopy(self.staging)
        lemma = next(row for row in manifest["lemmas"] if len(row["meanings"]) >= 2)
        canonical = lemma["canonicalLemma"]
        source = lemma["meanings"][0]
        target = lemma["meanings"][1]
        moved = source["patterns"].pop(0)
        target["patterns"].append(moved)
        staging_lemma = find_staging_lemma(staging, canonical)
        pattern_key = moved["candidatePatternKey"]
        source_key = source["candidateMeaningKey"]
        target_key = target["candidateMeaningKey"]
        pattern = next(row for row in staging_lemma["candidateContent"]["patterns"]
                       if row["meaningKeyRef"] == source_key and
                       row["candidatePatternKey"] == pattern_key)
        pattern["meaningKeyRef"] = target_key
        example = next(row for row in staging_lemma["candidateContent"]["examples"]
                       if row["meaningKeyRef"] == source_key and
                       row["patternKeyRef"] == pattern_key)
        example["meaningKeyRef"] = target_key
        original = next(row["id"] for row in self.allocations
                        if row["canonicalLemma"] == canonical and
                        row["meaningKey"] == source_key and
                        row["patternKey"] == pattern_key and
                        row["kind"] == "pattern")
        changed = next(row["id"] for row in phase4c1.allocate_projection(
            phase4c1.projection_from_manifest(manifest))
                       if row["canonicalLemma"] == canonical and
                       row["meaningKey"] == target_key and
                       row["patternKey"] == pattern_key and
                       row["kind"] == "pattern")
        self.assertNotEqual(original, changed)
        self.assert_phase4c1_error(phase4c1.build_map, manifest, staging)

    def test_17_released_id_mutation_is_detected(self):
        runtime = copy.deepcopy(self.runtime)
        entity_id = runtime["lemmas"][0]["id"]
        runtime["lemmas"][0]["id"] = entity_id[:-1] + (
            "0" if entity_id[-1] != "0" else "1")
        self.assert_phase4c1_error(phase4c1.released_identity_rows, runtime)

    def test_18_map_can_represent_a_tombstone_without_recycling(self):
        value = copy.deepcopy(self.generated)
        row = next(item for item in value["allocations"] if item["kind"] == "pattern")
        row["status"] = "tombstoned"
        by_identity = {phase4c1.identity_key(item): item for item in value["allocations"]}
        value["tombstones"] = [{
            "id": row["id"],
            "kind": row["kind"],
            "formerParentId": phase4c1.parent_id_for_row(row, by_identity),
            "retirementRevision": 1,
            "reason": "Mutation proof of permanent retirement handling.",
            "replacementIds": [],
        }]
        summary = phase4c1.validate_map(
            value, self.manifest, self.staging, self.runtime,
            require_current_projection=False)
        self.assertEqual(1, summary["tombstones"])

    def test_19_active_and_tombstoned_reuse_is_rejected(self):
        value = copy.deepcopy(self.generated)
        row = next(item for item in value["allocations"] if item["kind"] == "pattern")
        by_identity = {phase4c1.identity_key(item): item for item in value["allocations"]}
        value["tombstones"] = [{
            "id": row["id"],
            "kind": row["kind"],
            "formerParentId": phase4c1.parent_id_for_row(row, by_identity),
            "retirementRevision": 1,
            "reason": "Invalid resurrection mutation.",
            "replacementIds": [],
        }]
        self.assert_phase4c1_error(
            phase4c1.validate_map, value, self.manifest, self.staging, self.runtime,
            False)

    def test_20_one_candidate_identity_cannot_receive_two_ids(self):
        value = copy.deepcopy(self.generated)
        duplicate = copy.deepcopy(value["allocations"][0])
        duplicate["id"] = value["allocations"][1]["id"]
        value["allocations"].append(duplicate)
        value["allocations"].sort(key=lambda row: row["id"])
        self.assert_phase4c1_error(
            phase4c1.validate_map, value, self.manifest, self.staging, self.runtime,
            False)

    def test_21_one_id_cannot_belong_to_two_candidate_identities(self):
        value = copy.deepcopy(self.generated)
        duplicate = copy.deepcopy(next(
            row for row in value["allocations"] if row["kind"] == "lemma"))
        duplicate["canonicalLemma"] = "fikcyjna-tożsamość"
        value["allocations"].append(duplicate)
        value["allocations"].sort(key=lambda row: row["id"])
        self.assert_phase4c1_error(
            phase4c1.validate_map, value, self.manifest, self.staging, self.runtime,
            False)

    def test_22_all_543_frozen_keys_and_68_lemmas_map_exactly_once(self):
        lemma_rows = [row for row in self.allocations if row["kind"] == "lemma"]
        keyed_rows = [row for row in self.allocations if row["kind"] != "lemma"]
        self.assertEqual(68, len(lemma_rows))
        self.assertEqual(543, len(keyed_rows))
        self.assertEqual(611, len({phase4c1.identity_key(row)
                                  for row in self.allocations}))

    def test_23_map_governance_schema_and_lifecycle_are_exact(self):
        self.assertEqual(1, self.persisted["stableIdMapSchemaVersion"])
        self.assertEqual(phase4c1.ARTIFACT_STATUS,
                         self.persisted["artifactStatus"])
        self.assertEqual(phase4c1.FROZEN_DIGEST,
                         self.persisted["sourceCandidateKeyFreezeDigest"])
        self.assertEqual(1, self.persisted["allocationRevision"])
        self.assertEqual([], self.persisted["tombstones"])
        self.assertEqual({"active"}, {row["status"] for row in self.allocations})
        self.assertEqual({1}, {row["seedVersion"] for row in self.allocations})

    def test_24_seed_projection_is_unique_and_parent_bound(self):
        by_identity = {phase4c1.identity_key(row): row for row in self.allocations}
        seeds = [phase4c1.seed_for_row(row, by_identity) for row in self.allocations]
        self.assertEqual(611, len(set(seeds)))
        self.assertTrue(all(seed.startswith("v1|") for seed in seeds))

    def test_25_private_map_is_not_a_runtime_source_or_precache_asset(self):
        needle = "priority-8-phase4c-stable-id-map.json"
        runtime_paths = [ROOT / "pp-verb-patterns.js", ROOT / "sw.js", ROOT / "index.html"]
        runtime_paths.extend((ROOT / "content").rglob("*"))
        for path in runtime_paths:
            if path.is_file():
                self.assertNotIn(needle, path.read_text(encoding="utf-8", errors="ignore"),
                                 str(path))

    def test_26_wrapper_reuses_locked_allocator_without_a_second_id_hash(self):
        source = (ROOT / "priority8_phase4c1_stable_ids.py").read_text(encoding="utf-8")
        for function in (
                "tooling.allocate_lemma_id", "tooling.allocate_meaning_id",
                "tooling.allocate_pattern_id", "tooling.allocate_example_id"):
            self.assertIn(function, source)
        self.assertNotIn("def _sha12", source)

    def test_27_complete_check_mode_succeeds_without_writing(self):
        self.assertEqual(phase4c1.validate_map(self.persisted), phase4c1.run())


if __name__ == "__main__":
    unittest.main()
