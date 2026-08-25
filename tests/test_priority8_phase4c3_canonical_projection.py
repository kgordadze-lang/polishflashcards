import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import priority8_phase4c3_canonical_projection as phase4c3  # noqa: E402
from tests.test_priority8_phase4c2_schema_extensions import js_probe  # noqa: E402


PROTECTED_HASHES = {
    "editorial/priority-8-phase4-staging.json":
        "6ba1bcab43feeee5bfb99a5ac67eace8befa12c3df67f44bfb94191bf1a80adc",
    "editorial/priority-8-phase4-candidate-key-freeze.json":
        "b74bff54122ffb25c5ce8215e5bf28f8aa8823eabc2528cae8b1066a7eb1ab8b",
    "editorial/priority-8-phase4c-stable-id-map.json":
        "20fc8a566cb34825306f9198f4977fb0dacef3c33696cad45ff7ecbab6487a9d",
    "content/verb-patterns.json":
        "c5e934a80e33b261a58a5dc7087e4c82e3ec9b9c684863465241173790c6a961",
    "priority7_tooling.py":
        "9e8080f35a73680ab3d7f7f6e3f9435f83b2db56a26ebc6f48f3a4a7afa98988",
    "priority8_phase4c1_stable_ids.py":
        "7bcb64fa33269497c0b5af7a8631eaaf7dc317790395df0140e383b1be70301a",
    "pp-verb-patterns.js":
        "5f1552d29d2173e17fd50f8775fbc4b7eed1efbf0427b1f374489bbb3cbf7aa6",
    "validate_priority8_staging.py":
        "cf63ba385fb2d2e96558f1e4142c9fad16f49fd9f69251e6b70ab8f386cd302e",
    "index.html":
        "2257d3c9916a4cbf2420ffbf63b25e51dfd01e87e0eb153cb37386b0af1f6eab",
    "sw.js":
        "5f5e3d41762f14fca51f5d5984071c09ec6349c8ea2f87b36c16b8238a6a6b3e",
    "audio-manifest.json":
        "791dc09355b90f1457beb46f140a3997fc073ad46a85237a2aedecf6038707b2",
}


def sha256(relative):
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


class Priority8Phase4C3CanonicalProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.staging = phase4c3.phase4c1.read_json(phase4c3.STAGING_PATH)
        cls.manifest = phase4c3.phase4c1.read_json(phase4c3.FREEZE_PATH)
        cls.stable_map = phase4c3.phase4c1.read_json(phase4c3.MAP_PATH)
        cls.runtime = phase4c3.phase4c1.read_json(phase4c3.RUNTIME_PATH)
        cls.persisted = phase4c3.phase4c1.read_json(phase4c3.ARTIFACT_PATH)
        cls.generated = phase4c3.build_artifact()
        cls.summary = phase4c3.validate_artifact(cls.persisted)
        cls.trace_by_id = {
            row["stableId"]: row for row in cls.persisted["identityLedger"]["rows"]}
        cls.patterns = {}
        cls.lemmas = {}
        for lemma in cls.persisted["canonicalCandidates"]["lemmas"]:
            cls.lemmas[lemma["canonicalLemma"]] = lemma
            for meaning in lemma["meanings"]:
                for pattern in meaning["patterns"]:
                    trace = cls.trace_by_id[pattern["id"]]
                    identity = (
                        trace["canonicalLemma"], trace["candidateMeaningKey"],
                        trace["candidatePatternKey"])
                    cls.patterns[identity] = pattern

    def assert_rejected(self, artifact):
        with self.assertRaises(phase4c3.Phase4C3Error):
            phase4c3.validate_artifact(artifact)

    def mutation(self):
        return copy.deepcopy(self.persisted)

    def mutated_pattern(self, artifact, identity):
        trace_by_id = {
            row["stableId"]: row for row in artifact["identityLedger"]["rows"]}
        for lemma in artifact["canonicalCandidates"]["lemmas"]:
            for meaning in lemma["meanings"]:
                for pattern in meaning["patterns"]:
                    trace = trace_by_id[pattern["id"]]
                    if (trace["canonicalLemma"], trace["candidateMeaningKey"],
                            trace["candidatePatternKey"]) == identity:
                        return pattern
        raise AssertionError(identity)

    def test_01_frozen_candidate_digest_and_hierarchy_are_exact(self):
        projection = phase4c3.phase4c1.verify_freeze_gate(
            self.manifest, self.staging)
        self.assertEqual(phase4c3.phase4c1.FROZEN_DIGEST,
                         phase4c3.phase4c1.freeze_digest(projection))
        self.assertEqual((68, 95, 224, 224), (
            len(projection),
            sum(len(row["meanings"]) for row in projection),
            sum(len(meaning["patterns"]) for row in projection
                for meaning in row["meanings"]),
            sum(len(meaning["patterns"]) for row in projection
                for meaning in row["meanings"])))

    def test_02_stable_map_hash_counts_and_zero_vpx_are_exact(self):
        self.assertEqual(phase4c3.MAP_SHA256, sha256(
            "editorial/priority-8-phase4c-stable-id-map.json"))
        summary = phase4c3.phase4c1.validate_map(self.stable_map)
        self.assertEqual(611, summary["newTotal"])
        self.assertEqual(0, summary["exerciseIds"])

    def test_03_staging_freeze_and_map_hierarchy_are_equal(self):
        self.assertEqual(
            phase4c3.phase4c1.projection_from_manifest(self.manifest),
            phase4c3.phase4c1.projection_from_staging(self.staging))
        self.assertEqual(self.stable_map, phase4c3.phase4c1.build_map())

    def test_04_exact_private_candidate_counts(self):
        self.assertEqual((68, 95, 224, 224, 611), (
            self.summary["lemmas"], self.summary["meanings"],
            self.summary["patterns"], self.summary["examples"],
            self.summary["stableIds"]))

    def test_05_all_611_projected_ids_match_the_private_map(self):
        projected = set(self.trace_by_id)
        mapped = {row["id"] for row in self.stable_map["allocations"]}
        self.assertEqual(mapped, projected)
        self.assertEqual(611, len(projected))

    def test_06_exact_seven_source_conversions(self):
        found = set()
        for identity, pattern in self.patterns.items():
            for complement in pattern["complements"]:
                source_key = phase4c3._source_key(*identity, complement)
                if complement["role"] == "source":
                    found.add(source_key)
        self.assertEqual(phase4c3.SOURCE_COMPLEMENTS, found)

    def test_07_six_other_family_targets_remain_target(self):
        preserved = []
        for identity, pattern in self.patterns.items():
            if identity[0] not in phase4c3.SOURCE_FAMILY_LEMMAS:
                continue
            preserved.extend(
                (identity, item) for item in pattern["complements"]
                if item["role"] == "target")
        self.assertEqual(6, len(preserved))

    def test_08_purchase_price_targets_remain_target(self):
        for lemma, meaning in (("kupować", "process-purchase"),
                               ("kupić", "completed-purchase")):
            pattern = self.patterns[(lemma, meaning, "seller-price-schema")]
            price = next(item for item in pattern["complements"]
                         if item.get("preposition") == "za")
            seller = next(item for item in pattern["complements"]
                          if item.get("preposition") == "od")
            self.assertEqual("target", price["role"])
            self.assertEqual("source", seller["role"])

    def test_09_destination_and_goal_targets_remain_target(self):
        identities = {
            ("wracać", "return-to-earlier-place", "do-genitive-return-goal"),
            ("wrócić", "completed-return-to-earlier-place", "do-genitive-return-goal"),
            ("wyjść", "literal-exit-from-place", "do-genitive-destination"),
            ("wyjść", "literal-exit-from-place", "na-accusative-destination"),
        }
        for identity in identities:
            self.assertEqual(
                {"target"}, {row["role"] for row in self.patterns[identity]["complements"]})

    def test_10_person_sources_use_only_approved_question_overrides(self):
        overrides = []
        for identity, pattern in self.patterns.items():
            for complement in pattern["complements"]:
                if "questionOverridePl" in complement:
                    overrides.append((identity, complement))
        self.assertEqual(3, len(overrides))
        self.assertEqual({"kupować", "kupić", "zamawiać"},
                         {identity[0] for identity, _ in overrides})
        self.assertTrue(all(row["questionOverridePl"] == ["kogo?"]
                            for _, row in overrides))

    def test_11_direct_speech_count_and_identities_are_exact(self):
        found = set()
        for identity, pattern in self.patterns.items():
            if any(row.get("clauseKind") == "direct-speech"
                   for row in pattern["complements"]):
                found.add(identity)
        self.assertEqual(phase4c3.DIRECT_SPEECH_PATTERNS, found)
        self.assertEqual(11, len(found))

    def test_12_corrected_interrogatives_remain_interrogative(self):
        for identity in phase4c3.CORRECTED_INTERROGATIVES:
            kinds = {row.get("clauseKind") for row in self.patterns[identity]["complements"]}
            self.assertIn("interrogative", kinds)
            self.assertNotIn("czy", kinds)

    def test_13_old_czy_dependent_identity_is_absent(self):
        self.assertFalse(any(
            row["candidatePatternKey"] == "czy-dependent-clause"
            for row in self.persisted["identityLedger"]["rows"]))

    def test_14_czy_moge_is_sentence_packaging_over_infinitive(self):
        pattern = self.patterns[("móc", "permission", "infinitive-permitted-action")]
        self.assertEqual(["infinitive"], [row["type"] for row in pattern["complements"]])
        self.assertTrue(pattern["examples"][0]["pl"].startswith("Czy mogę"))

    def test_15_required_lexical_items_are_exact(self):
        carrying = {identity for identity, pattern in self.patterns.items()
                    if "requiredLexicalItems" in pattern}
        self.assertEqual(phase4c3.PARTICIPATION_PATTERNS, carrying)
        for identity in carrying:
            pattern = self.patterns[identity]
            self.assertEqual(["udział"], pattern["requiredLexicalItems"])
            self.assertFalse(any(row.get("case") == "accusative"
                                 for row in pattern["complements"]))

    def test_16_generic_runtime_headlines_include_udzial(self):
        for lemma_name in ("brać", "wziąć"):
            identity = (lemma_name, "fixed-participation",
                        "w-locative-participation-target")
            lemma = copy.deepcopy(self.lemmas[lemma_name])
            target = copy.deepcopy(self.patterns[identity])
            meaning_id = next(
                meaning["id"] for meaning in self.lemmas[lemma_name]["meanings"]
                if any(row["id"] == target["id"] for row in meaning["patterns"]))
            lemma["meanings"] = [{
                "id": meaning_id,
                "glossesEn": ["participate"], "patterns": [target]}]
            document = {"formatVersion": 2, "patternDataRevision": 2, "lemmas": [lemma]}
            probe = js_probe(document)
            self.assertTrue(probe["accepted"])
            self.assertEqual(
                [lemma_name, "udział", "+", "w czym?"],
                [token["text"] for token in probe["headline"]])

    def test_17_metadata_only_identities_are_not_promoted(self):
        self.assertTrue(phase4c3.METADATA_ONLY.isdisjoint(self.lemmas))
        relations = self.persisted["governance"]["metadataOnlyAspectRelations"]
        self.assertEqual({"zaczynać", "przeczytać"},
                         {row["metadataAspectPartner"]["canonicalLemma"] for row in relations})
        self.assertTrue(all(row["canonicalIdentityAllocated"] is False for row in relations))

    def test_18_lexical_sie_and_sobie_boundaries_are_distinct(self):
        self.assertNotEqual(self.lemmas["radzić"]["id"], self.lemmas["radzić sobie"]["id"])
        self.assertIn("uczyć", self.lemmas)
        self.assertNotIn("uczyć się", self.lemmas)
        for name in ("kłócić się", "spotykać się", "spotkać się",
                     "umówić się", "cieszyć się", "martwić się", "zgadzać się"):
            self.assertTrue(self.lemmas[name]["canonicalLemma"].endswith(" się"))
            self.assertTrue(self.lemmas[name]["reflexive"])

    def test_19_aspect_links_and_syntax_inheritance_are_absent(self):
        self.assertFalse(any("aspectPartnerIds" in lemma for lemma in self.lemmas.values()))
        self.assertFalse(any("aspectEquivalentPatternIds" in pattern
                             for pattern in self.patterns.values()))
        for kind in ("ze", "zeby", "interrogative"):
            pisać = self.patterns[("pisać", "written-correspondence", f"dative-{kind}-clause")]
            napisać = self.patterns[("napisać", "completed-written-correspondence", f"dative-{kind}-clause")]
            self.assertFalse(next(row for row in pisać["complements"]
                                  if row.get("case") == "dative")["required"])
            self.assertTrue(next(row for row in napisać["complements"]
                                 if row.get("case") == "dative")["required"])

    def test_20_deferral_ledger_is_exact_and_complete(self):
        ledger = self.persisted["deferralLedger"]
        self.assertEqual(10, len(ledger))
        self.assertEqual(set(phase4c3.DEFERRALS), {
            (row["lemma"], row["fact"], row["whyNoCanonicalPattern"], row["reason"])
            for row in ledger})
        self.assertTrue(all(row["architectureDecision"] == "DEFERRED" for row in ledger))

    def test_21_umowic_sie_kiedy_and_co_do_create_no_patterns(self):
        keys = {identity[2] for identity in self.patterns if identity[0] == "umówić się"}
        self.assertFalse(any("kiedy" in key or "co-do" in key for key in keys))
        facts = {row["fact"] for row in self.persisted["deferralLedger"]
                 if row["lemma"] == "umówić się"}
        self.assertEqual({"appointment KIEDY", "co do + Genitive"}, facts)

    def test_22_pasowac_has_no_synthetic_subject(self):
        pattern = self.patterns[("pasować", "expectation-suitability",
                                 "dative-expectation-holder")]
        self.assertEqual("lexical-frame", pattern["relationType"])
        self.assertNotIn("subject", {row["role"] for row in pattern["complements"]})

    def test_23_kochac_register_is_preserved(self):
        patterns = [pattern for identity, pattern in self.patterns.items()
                    if identity[0] == "kochać"]
        self.assertTrue(patterns)
        self.assertEqual({"neutral"}, {row["usage"]["register"] for row in patterns})

    def test_24_status_activity_and_audio_eligibility_are_exact(self):
        statuses = [pattern["teachingStatus"] for pattern in self.patterns.values()]
        self.assertEqual(222, statuses.count("active-production"))
        self.assertEqual(2, statuses.count("recognition-only"))
        self.assertTrue(all(pattern["activityEligibility"] == []
                            for pattern in self.patterns.values()))
        self.assertTrue(all(pattern["examples"][0]["audioEligible"] is True
                            for pattern in self.patterns.values()))

    def test_25_provenance_and_repository_reuse_are_truthful(self):
        provenance = self.persisted["governance"]["patternProvenance"]
        self.assertEqual(224, len(provenance))
        policy = [row for row in provenance
                  if row["provenanceClass"] == "policy-authorized-direct-speech"]
        self.assertEqual(1, len(policy))
        self.assertEqual(("odpowiadać", "direct-speech"),
                         (policy[0]["canonicalLemma"], policy[0]["candidatePatternKey"]))
        origins = self.persisted["governance"]["exampleOrigins"]
        kinds = [row["origin"]["kind"] for row in origins]
        self.assertEqual(220, kinds.count("editorial-generated"))
        self.assertEqual(4, kinds.count("repository-reuse"))
        context = phase4c3.tooling._load_context(str(phase4c3.CONTEXT_PATH), str(ROOT))
        for row in origins:
            source = row["origin"].get("repositorySource")
            if source:
                record = context.repository_index.get(source["id"]).record
                pattern = self.patterns[(
                    row["canonicalLemma"], row["candidateMeaningKey"],
                    row["candidatePatternKey"])]
                self.assertEqual(record[source["field"]], pattern["examples"][0]["pl"])

    def test_26_candidate_key_id_entity_traceability_is_bijective(self):
        rows = self.persisted["identityLedger"]["rows"]
        self.assertEqual(611, len(rows))
        self.assertEqual(611, len({row["stableId"] for row in rows}))
        self.assertEqual({"PROMOTED"}, {row["outcome"] for row in rows})
        self.assertEqual(543, sum(row["kind"] != "lemma" for row in rows))

    def test_27_loss_audit_promoted_611_missing_zero(self):
        ledger = self.persisted["identityLedger"]
        self.assertEqual((611, 0, 0), (
            ledger["promoted"], ledger["missing"], ledger["duplicatePromotions"]))

    def test_28_combined_accounting_is_exact(self):
        ledger = self.persisted["combinedCorpusLedger"]
        self.assertEqual({"lemmas": 98, "meanings": 129, "patterns": 269,
                          "examples": 269, "stableIds": 765},
                         ledger["combinedFuture"])

    def test_29_all_154_released_ids_reproduce_unchanged(self):
        rows = phase4c3.phase4c1.released_identity_rows(self.runtime)
        self.assertEqual(154, len(rows))
        self.assertEqual(154, len({row["id"] for row in rows}))

    def test_30_all_protected_inputs_and_production_paths_are_unchanged(self):
        for relative, expected in PROTECTED_HASHES.items():
            self.assertEqual(expected, sha256(relative), relative)

    def test_31_regeneration_is_byte_identical_and_default_is_verify_only(self):
        self.assertEqual(self.generated, self.persisted)
        before = phase4c3.ARTIFACT_PATH.read_bytes()
        summary = phase4c3.run(write=False)
        self.assertEqual(self.summary, summary)
        self.assertEqual(before, phase4c3.ARTIFACT_PATH.read_bytes())

    def test_32_private_artifact_has_zero_runtime_references(self):
        private_name = phase4c3.ARTIFACT_PATH.name
        for relative in ("content/verb-patterns.json", "pp-verb-patterns.js",
                         "sw.js", "index.html", "audio-manifest.json"):
            self.assertNotIn(private_name, (ROOT / relative).read_text(encoding="utf-8"))

    def test_33_private_core_passes_the_real_production_validator(self):
        wrapper = {
            "formatVersion": 2, "patternDataRevision": 2,
            "lemmas": copy.deepcopy(self.persisted["canonicalCandidates"]["lemmas"]),
        }
        self.assertEqual([], phase4c3.tooling.validate_runtime(wrapper))

    def test_34_unknown_canonical_field_is_rejected(self):
        changed = self.mutation()
        changed["canonicalCandidates"]["lemmas"][0]["unknown"] = True
        self.assert_rejected(changed)

    def test_35_source_left_as_target_is_rejected(self):
        changed = self.mutation()
        pattern = self.mutated_pattern(
            changed, ("wracać", "return-to-earlier-place", "z-genitive-return-source"))
        pattern["complements"][0]["role"] = "target"
        self.assert_rejected(changed)

    def test_36_non_source_target_converted_to_source_is_rejected(self):
        changed = self.mutation()
        pattern = self.mutated_pattern(
            changed, ("wyjść", "literal-exit-from-place", "do-genitive-destination"))
        pattern["complements"][0]["role"] = "source"
        self.assert_rejected(changed)

    def test_37_blanket_target_to_source_mutation_is_rejected(self):
        changed = self.mutation()
        for lemma in changed["canonicalCandidates"]["lemmas"]:
            if lemma["canonicalLemma"] not in phase4c3.SOURCE_FAMILY_LEMMAS:
                continue
            for meaning in lemma["meanings"]:
                for pattern in meaning["patterns"]:
                    for complement in pattern["complements"]:
                        if complement["role"] == "target":
                            complement["role"] = "source"
        self.assert_rejected(changed)

    def test_38_direct_speech_downgrade_is_rejected(self):
        changed = self.mutation()
        pattern = self.mutated_pattern(changed, next(iter(phase4c3.DIRECT_SPEECH_PATTERNS)))
        next(row for row in pattern["complements"]
             if row.get("clauseKind") == "direct-speech")["clauseKind"] = "ze"
        self.assert_rejected(changed)

    def test_39_interrogative_changed_to_czy_is_rejected(self):
        changed = self.mutation()
        pattern = self.mutated_pattern(changed, next(iter(phase4c3.CORRECTED_INTERROGATIVES)))
        next(row for row in pattern["complements"]
             if row.get("clauseKind") == "interrogative")["clauseKind"] = "czy"
        self.assert_rejected(changed)

    def test_40_required_udzial_omission_and_wrong_addition_are_rejected(self):
        changed = self.mutation()
        pattern = self.mutated_pattern(changed, next(iter(phase4c3.PARTICIPATION_PATTERNS)))
        del pattern["requiredLexicalItems"]
        self.assert_rejected(changed)
        changed = self.mutation()
        wrong = self.mutated_pattern(
            changed, ("brać", "literal-taking", "accusative-entity-optional-instrumental-means"))
        wrong["requiredLexicalItems"] = ["udział"]
        self.assert_rejected(changed)

    def test_41_metadata_only_lemma_promotion_is_rejected(self):
        changed = self.mutation()
        fake = copy.deepcopy(changed["canonicalCandidates"]["lemmas"][0])
        fake["canonicalLemma"] = "zaczynać"
        changed["canonicalCandidates"]["lemmas"].append(fake)
        self.assert_rejected(changed)

    def test_42_aspect_syntax_inheritance_is_rejected(self):
        changed = self.mutation()
        pattern = self.mutated_pattern(
            changed, ("pisać", "written-correspondence", "dative-ze-clause"))
        next(row for row in pattern["complements"]
             if row.get("case") == "dative")["required"] = True
        self.assert_rejected(changed)

    def test_43_frozen_key_omission_duplication_and_reparenting_are_rejected(self):
        changed = self.mutation()
        changed["identityLedger"]["rows"].pop()
        self.assert_rejected(changed)
        changed = self.mutation()
        changed["identityLedger"]["rows"].append(
            copy.deepcopy(changed["identityLedger"]["rows"][0]))
        self.assert_rejected(changed)
        changed = self.mutation()
        lemma = changed["canonicalCandidates"]["lemmas"][0]
        pattern = lemma["meanings"][0]["patterns"].pop()
        lemma["meanings"][-1]["patterns"].append(pattern)
        self.assert_rejected(changed)

    def test_44_mapped_id_change_is_rejected(self):
        changed = self.mutation()
        changed["canonicalCandidates"]["lemmas"][0]["id"] = self.lemmas["pracować"]["id"]
        self.assert_rejected(changed)

    def test_45_unregistered_deferral_is_rejected(self):
        changed = self.mutation()
        changed["deferralLedger"].append(copy.deepcopy(changed["deferralLedger"][0]))
        self.assert_rejected(changed)

    def test_46_no_unexpected_changed_paths_exist(self):
        output = subprocess.check_output(
            ["git", "status", "--short"], cwd=ROOT, text=True)
        paths = {line[3:] for line in output.splitlines() if line}
        self.assertTrue(paths.issubset({
            "editorial/priority-8-phase4c-canonical-candidates.json",
            "priority8_phase4c3_canonical_projection.py",
            "tests/test_priority8_phase4c3_canonical_projection.py",
            "reports/priority-8-phase-4c3-canonical-projection.md",
        }), paths)


if __name__ == "__main__":
    unittest.main()
