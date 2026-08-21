import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import validate_priority8_staging as validator  # noqa: E402


STAGING_PATH = ROOT / "editorial/priority-8-phase4-staging.json"


def record(data, lemma):
    return next(item for item in data["lemmas"]
                if item["canonicalLemma"] == lemma)


def candidate_meaning(key="core"):
    return {
        "candidateMeaningKey": key,
        "glossesEn": ["test meaning"],
        "internalScope": "Fixture-only semantic scope.",
    }


def candidate_pattern(key="case-target", meaning_ref="core"):
    return {
        "candidatePatternKey": key,
        "meaningKeyRef": meaning_ref,
        "relationType": "lexical-frame",
        "complements": [{
            "type": "case",
            "case": "genitive",
            "required": True,
            "role": "target",
        }],
        "cefr": {"recognition": "A1", "production": "A1"},
        "teachingStatus": "active-production",
        "usage": {"priority": "core", "register": "neutral"},
        "learnerExplanationEn": "Fixture-only learner explanation.",
    }


def candidate_example(
    key="first-context",
    meaning_ref="core",
    pattern_ref="case-target",
    candidate_origin=None,
):
    if candidate_origin is None:
        candidate_origin = {"kind": "editorial-generated"}
    return {
        "candidateExampleKey": key,
        "meaningKeyRef": meaning_ref,
        "patternKeyRef": pattern_ref,
        "pl": "Zdanie wyłącznie testowe.",
        "en": "Fixture-only sentence.",
        "candidateOrigin": candidate_origin,
    }


def repository_origin(source_kind, field, source_id="repository-content-001"):
    return {
        "kind": "repository-reuse",
        "repositorySource": {
            "kind": source_kind,
            "id": source_id,
            "field": field,
        },
    }


class Priority8Phase4B1AAuthoringSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.real = json.loads(STAGING_PATH.read_text(encoding="utf-8"))

    def authored(self, phase_step="4B1"):
        data = copy.deepcopy(self.real)
        data["phaseStep"] = phase_step
        data["stagingRevision"] = validator.PHASE_STEP_REVISIONS[phase_step]
        completed = int(phase_step[-1])
        for batch in validator.AUTHORING_BATCHES[:completed]:
            for _, lemma in batch:
                content = record(data, lemma)["candidateContent"]
                content["meanings"] = [candidate_meaning()]
                content["patterns"] = [candidate_pattern()]
        return data

    def assert_invalid(self, data, expected_fragment):
        issues = validator.validate_data(data)
        self.assertTrue(issues, "mutated staging unexpectedly validated")
        self.assertTrue(
            any(expected_fragment in issue for issue in issues),
            f"missing {expected_fragment!r} in issues: {issues}",
        )

    def test_real_phase4b0_staging_still_validates(self):
        self.assertEqual([], validator.validate_data(self.real))

    def test_valid_candidate_meaning_fixture(self):
        self.assertEqual([], validator.validate_data(self.authored()))

    def test_valid_candidate_pattern_ownership(self):
        data = self.authored()
        pattern = record(data, "pracować")["candidateContent"]["patterns"][0]
        self.assertEqual("core", pattern["meaningKeyRef"])
        self.assertEqual([], validator.validate_data(data))

    def test_valid_candidate_example_ownership(self):
        data = self.authored()
        record(data, "pracować")["candidateContent"]["examples"] = [
            candidate_example()
        ]
        self.assertEqual([], validator.validate_data(data))

    def test_editorial_generated_candidate_origin_accepted(self):
        data = self.authored()
        record(data, "pracować")["candidateContent"]["examples"] = [
            candidate_example(
                candidate_origin={"kind": "editorial-generated"})
        ]
        self.assertEqual([], validator.validate_data(data))

    def _assert_repository_origin_accepted(self, source_kind, field):
        data = self.authored()
        record(data, "pracować")["candidateContent"]["examples"] = [
            candidate_example(
                candidate_origin=repository_origin(source_kind, field))
        ]
        self.assertEqual([], validator.validate_data(data))

    def test_repository_reuse_card_pl_accepted(self):
        self._assert_repository_origin_accepted("card", "pl")

    def test_repository_reuse_card_ex_accepted(self):
        self._assert_repository_origin_accepted("card", "ex")

    def test_repository_reuse_drill_prompt_accepted(self):
        self._assert_repository_origin_accepted("drill", "prompt")

    def test_repository_reuse_drill_answer_accepted(self):
        self._assert_repository_origin_accepted("drill", "answer")

    def test_missing_candidate_origin_rejected(self):
        data = self.authored()
        example = candidate_example()
        example.pop("candidateOrigin")
        record(data, "pracować")["candidateContent"]["examples"] = [example]
        self.assert_invalid(data, "missing fields: candidateOrigin")

    def test_unknown_candidate_origin_kind_rejected(self):
        data = self.authored()
        example = candidate_example(candidate_origin={"kind": "unknown"})
        record(data, "pracować")["candidateContent"]["examples"] = [example]
        self.assert_invalid(data, "candidateOrigin.kind must be one of")

    def test_editorial_generated_with_repository_source_rejected(self):
        data = self.authored()
        origin = {
            "kind": "editorial-generated",
            "repositorySource": {
                "kind": "card", "id": "card-001", "field": "pl"},
        }
        record(data, "pracować")["candidateContent"]["examples"] = [
            candidate_example(candidate_origin=origin)
        ]
        self.assert_invalid(data, "candidateOrigin has unexpected fields")

    def test_repository_reuse_without_repository_source_rejected(self):
        data = self.authored()
        example = candidate_example(
            candidate_origin={"kind": "repository-reuse"})
        record(data, "pracować")["candidateContent"]["examples"] = [example]
        self.assert_invalid(data, "missing fields: repositorySource")

    def _assert_repository_source_mutation_rejected(
        self, mutation, expected_fragment
    ):
        data = self.authored()
        origin = repository_origin("card", "pl")
        mutation(origin["repositorySource"])
        record(data, "pracować")["candidateContent"]["examples"] = [
            candidate_example(candidate_origin=origin)
        ]
        self.assert_invalid(data, expected_fragment)

    def test_repository_source_missing_kind_rejected(self):
        self._assert_repository_source_mutation_rejected(
            lambda source: source.pop("kind"), "missing fields: kind")

    def test_repository_source_missing_id_rejected(self):
        self._assert_repository_source_mutation_rejected(
            lambda source: source.pop("id"), "missing fields: id")

    def test_repository_source_missing_field_rejected(self):
        self._assert_repository_source_mutation_rejected(
            lambda source: source.pop("field"), "missing fields: field")

    def test_repository_source_extra_field_rejected(self):
        self._assert_repository_source_mutation_rejected(
            lambda source: source.update({"extra": "not-allowed"}),
            "unexpected fields: extra",
        )

    def test_card_with_prompt_field_rejected(self):
        data = self.authored()
        example = candidate_example(
            candidate_origin=repository_origin("card", "prompt"))
        record(data, "pracować")["candidateContent"]["examples"] = [example]
        self.assert_invalid(data, "must be one of: ex, pl")

    def test_drill_with_ex_field_rejected(self):
        data = self.authored()
        example = candidate_example(
            candidate_origin=repository_origin("drill", "ex"))
        record(data, "pracować")["candidateContent"]["examples"] = [example]
        self.assert_invalid(data, "must be one of: answer, prompt")

    def test_blank_repository_source_id_rejected(self):
        data = self.authored()
        example = candidate_example(
            candidate_origin=repository_origin("card", "pl", "  "))
        record(data, "pracować")["candidateContent"]["examples"] = [example]
        self.assert_invalid(data, "repositorySource.id must be a non-empty")

    def test_repository_source_production_vp_prefix_rejected(self):
        data = self.authored()
        example = candidate_example(
            candidate_origin=repository_origin("card", "pl", "vp-l-test"))
        record(data, "pracować")["candidateContent"]["examples"] = [example]
        self.assert_invalid(data, "production vp-* ID prefix is prohibited")

    def test_original_candidate_origin_rejected(self):
        data = self.authored()
        example = candidate_example(candidate_origin={"kind": "original"})
        record(data, "pracować")["candidateContent"]["examples"] = [example]
        self.assert_invalid(data, "candidateOrigin.kind must be one of")

    def test_provenance_governance_and_actor_fields_remain_rejected(self):
        for field in (
            "actorRef", "generatorRef", "reviewerRef", "authorRef",
            "adoptedAt",
        ):
            with self.subTest(field=field):
                data = self.authored()
                origin = {"kind": "editorial-generated", field: "actor-001"}
                record(data, "pracować")["candidateContent"]["examples"] = [
                    candidate_example(candidate_origin=origin)
                ]
                self.assert_invalid(
                    data, "governance/reviewer identity field")

    def test_same_candidate_meaning_key_under_two_lemmas_allowed(self):
        data = self.authored()
        self.assertEqual(
            "core",
            record(data, "pracować")["candidateContent"]["meanings"][0]
            ["candidateMeaningKey"],
        )
        self.assertEqual(
            "core",
            record(data, "iść")["candidateContent"]["meanings"][0]
            ["candidateMeaningKey"],
        )
        self.assertEqual([], validator.validate_data(data))

    def test_duplicate_candidate_meaning_key_within_lemma_rejected(self):
        data = self.authored()
        content = record(data, "pracować")["candidateContent"]
        content["meanings"].append(candidate_meaning())
        self.assert_invalid(data, "duplicate candidateMeaningKey within lemma")

    def test_same_candidate_pattern_key_under_different_meanings_allowed(self):
        data = self.authored()
        content = record(data, "pracować")["candidateContent"]
        content["meanings"].append(candidate_meaning("alternate"))
        content["patterns"].append(candidate_pattern("case-target", "alternate"))
        self.assertEqual([], validator.validate_data(data))

    def test_duplicate_candidate_pattern_key_under_same_meaning_rejected(self):
        data = self.authored()
        content = record(data, "pracować")["candidateContent"]
        content["patterns"].append(candidate_pattern())
        self.assert_invalid(
            data, "duplicate candidatePatternKey under meaningKeyRef")

    def test_same_candidate_example_key_under_different_patterns_allowed(self):
        data = self.authored()
        content = record(data, "pracować")["candidateContent"]
        content["patterns"].append(candidate_pattern("alternate-frame"))
        content["examples"] = [
            candidate_example(),
            candidate_example(pattern_ref="alternate-frame"),
        ]
        self.assertEqual([], validator.validate_data(data))

    def test_repeated_pattern_key_examples_resolve_with_meaning_reference(self):
        data = self.authored()
        content = record(data, "pracować")["candidateContent"]
        content["meanings"].append(candidate_meaning("alternate"))
        content["patterns"].append(candidate_pattern("case-target", "alternate"))
        content["examples"] = [
            candidate_example(meaning_ref="core"),
            candidate_example(meaning_ref="alternate"),
        ]
        self.assertEqual([], validator.validate_data(data))

    def test_duplicate_candidate_example_key_under_same_pattern_rejected(self):
        data = self.authored()
        content = record(data, "pracować")["candidateContent"]
        content["examples"] = [candidate_example(), candidate_example()]
        self.assert_invalid(
            data, "duplicate candidateExampleKey under patternKeyRef")

    def test_unresolved_meaning_key_reference_rejected(self):
        data = self.authored()
        record(data, "pracować")["candidateContent"]["patterns"][0][
            "meaningKeyRef"] = "other-owner"
        self.assert_invalid(data, "unresolved meaningKeyRef within lemma")

    def test_unresolved_pattern_key_reference_rejected(self):
        data = self.authored()
        record(data, "pracować")["candidateContent"]["examples"] = [
            candidate_example(pattern_ref="missing-pattern")
        ]
        self.assert_invalid(data, "unresolved patternKeyRef within lemma")

    def test_malformed_candidate_meaning_key_rejected(self):
        data = self.authored()
        record(data, "pracować")["candidateContent"]["meanings"][0][
            "candidateMeaningKey"] = "Not Kebab"
        self.assert_invalid(data, "candidate key must use lowercase kebab-case")

    def test_malformed_candidate_pattern_key_rejected(self):
        data = self.authored()
        record(data, "pracować")["candidateContent"]["patterns"][0][
            "candidatePatternKey"] = "not_kebab"
        self.assert_invalid(data, "candidate key must use lowercase kebab-case")

    def test_malformed_candidate_example_key_rejected(self):
        data = self.authored()
        example = candidate_example(key="not kebab")
        record(data, "pracować")["candidateContent"]["examples"] = [example]
        self.assert_invalid(data, "candidate key must use lowercase kebab-case")

    def _assert_vp_prefix_rejected(self, prefix):
        data = self.authored()
        record(data, "pracować")["candidateContent"]["meanings"][0][
            "internalScope"] = prefix + "test"
        self.assert_invalid(data, "production vp-* ID prefix is prohibited")

    def test_vp_l_prefix_rejected(self):
        self._assert_vp_prefix_rejected("vp-l-")

    def test_vp_m_prefix_rejected(self):
        self._assert_vp_prefix_rejected("vp-m-")

    def test_vp_p_prefix_rejected(self):
        self._assert_vp_prefix_rejected("vp-p-")

    def test_vp_e_prefix_rejected(self):
        self._assert_vp_prefix_rejected("vp-e-")

    def test_vp_x_prefix_rejected(self):
        self._assert_vp_prefix_rejected("vp-x-")

    def test_production_id_field_rejected_from_candidate_content(self):
        data = self.authored()
        record(data, "pracować")["candidateContent"]["meanings"][0][
            "meaningId"] = "not-a-production-value"
        self.assert_invalid(data, "production-ID field name is prohibited")

    def test_cross_lemma_ownership_cannot_resolve(self):
        data = self.authored()
        other = record(data, "iść")["candidateContent"]
        other["meanings"] = [candidate_meaning("other-owner")]
        other["patterns"] = [candidate_pattern(meaning_ref="other-owner")]
        local = record(data, "pracować")["candidateContent"]
        local["patterns"][0]["meaningKeyRef"] = "other-owner"
        self.assert_invalid(data, "unresolved meaningKeyRef within lemma")

    def test_direct_speech_clause_candidate_accepted_in_staging(self):
        data = self.authored()
        pattern = record(data, "pracować")["candidateContent"]["patterns"][0]
        pattern["complements"] = [{
            "type": "clause",
            "clauseKind": "direct-speech",
            "required": True,
            "role": "content",
        }]
        self.assertEqual([], validator.validate_data(data))

    def test_fifth_complement_type_rejected(self):
        data = self.authored()
        record(data, "pracować")["candidateContent"]["patterns"][0][
            "complements"][0]["type"] = "destination"
        self.assert_invalid(data, "must be one of: case, clause, infinitive")

    def _assert_generalized_role_type_rejected(self, complement_type):
        data = self.authored()
        record(data, "pracować")["candidateContent"]["patterns"][0][
            "complements"][0]["type"] = complement_type
        self.assert_invalid(data, "must be one of: case, clause, infinitive")

    def test_dokad_complement_type_rejected(self):
        self._assert_generalized_role_type_rejected("DOKĄD")

    def test_skad_complement_type_rejected(self):
        self._assert_generalized_role_type_rejected("SKĄD")

    def test_gdzie_complement_type_rejected(self):
        self._assert_generalized_role_type_rejected("GDZIE")

    def test_canonical_review_state_rejected_from_candidate_content(self):
        data = self.authored()
        record(data, "pracować")["candidateContent"]["patterns"][0][
            "reviewState"] = "research"
        self.assert_invalid(data, "governance/reviewer identity field")

    def test_reviewer_identity_rejected_from_candidate_content(self):
        data = self.authored()
        record(data, "pracować")["candidateContent"]["examples"] = [
            candidate_example()
        ]
        record(data, "pracować")["candidateContent"]["examples"][0][
            "reviewerRef"] = "reviewer-001"
        self.assert_invalid(data, "governance/reviewer identity field")

    def test_candidate_field_sets_are_exact(self):
        self.assertEqual(
            {"candidateMeaningKey", "glossesEn", "internalScope"},
            validator.CANDIDATE_MEANING_FIELDS,
        )
        self.assertEqual(
            {
                "candidatePatternKey", "meaningKeyRef", "relationType",
                "complements", "cefr", "teachingStatus", "usage",
                "learnerExplanationEn",
            },
            validator.CANDIDATE_PATTERN_FIELDS,
        )
        self.assertEqual(
            {
                "candidateExampleKey", "meaningKeyRef", "patternKeyRef",
                "pl", "en", "candidateOrigin",
            },
            validator.CANDIDATE_EXAMPLE_FIELDS,
        )

    def test_batch_1_membership_is_exact(self):
        self.assertEqual(
            [
                "pracować", "iść", "chodzić", "jechać", "jeździć",
                "dojść", "dojechać", "wracać", "wrócić", "przyjść",
            ],
            [lemma for _, lemma in validator.AUTHORING_BATCHES[0]],
        )

    def test_all_seven_batch_sizes_are_exact(self):
        self.assertEqual(
            [10, 10, 10, 9, 10, 10, 9],
            [len(batch) for batch in validator.AUTHORING_BATCHES],
        )

    def test_metadata_only_orders_occur_in_no_batch(self):
        orders = {
            order for batch in validator.AUTHORING_BATCHES
            for order, _ in batch
        }
        self.assertTrue({17, 37}.isdisjoint(orders))

    def test_each_frozen_lemma_appears_in_exactly_one_batch(self):
        flattened = [item for batch in validator.AUTHORING_BATCHES
                     for item in batch]
        expected = [(item["verificationOrder"], item["canonicalLemma"])
                    for item in self.real["lemmas"]]
        self.assertEqual(expected, flattened)
        self.assertEqual(68, len(set(flattened)))

    def test_revision_phase_step_mapping_is_exact(self):
        self.assertEqual(
            {
                "4B0": 1, "4B1": 2, "4B2": 3, "4B3": 4,
                "4B4": 5, "4B5": 6, "4B6": 7, "4B7": 8,
            },
            validator.PHASE_STEP_REVISIONS,
        )

    def test_wrong_revision_for_phase_step_rejected(self):
        data = self.authored()
        data["stagingRevision"] = 3
        self.assert_invalid(data, "stagingRevision must equal 2 for 4B1")

    def test_future_batch_authored_content_rejected(self):
        data = self.authored("4B1")
        future = record(data, "przyjechać")["candidateContent"]
        future["meanings"] = [candidate_meaning()]
        future["patterns"] = [candidate_pattern()]
        self.assert_invalid(data, "future-batch lemma must remain empty")

    def test_completed_batch_missing_content_rejected(self):
        data = self.authored("4B1")
        record(data, "pracować")["candidateContent"] = {
            "meanings": [], "patterns": [], "examples": []}
        self.assert_invalid(data, "completed-batch lemma requires")

    def test_future_batch_review_status_must_remain_draft(self):
        data = self.authored("4B1")
        record(data, "przyjechać")["stagingReviewStatus"] = (
            "independently-reviewed")
        self.assert_invalid(data, "must remain draft before its authoring batch")

    def test_examples_are_not_required_by_canonical_cardinality(self):
        data = self.authored("4B1")
        self.assertTrue(all(
            not record(data, lemma)["candidateContent"]["examples"]
            for _, lemma in validator.AUTHORING_BATCHES[0]
        ))
        self.assertEqual([], validator.validate_data(data))

    def test_every_candidate_meaning_requires_a_pattern(self):
        data = self.authored()
        content = record(data, "pracować")["candidateContent"]
        content["meanings"].append(candidate_meaning("unowned"))
        self.assert_invalid(data, "requires at least one pattern")

    def test_validation_is_deterministic(self):
        data = self.authored()
        self.assertEqual(
            validator.validate_data(data), validator.validate_data(data))

    def test_validation_does_not_mutate_fixture_input(self):
        data = self.authored()
        before = copy.deepcopy(data)
        validator.validate_data(data)
        self.assertEqual(before, data)

    def test_success_summary_reports_live_b0_and_revision(self):
        self.assertEqual(
            "PASS: Priority 8 4B0 staging revision 1 is read-only valid "
            "(68 lemmas, 21 constrained records, 12 global constraints).",
            validator.success_summary(self.real),
        )

    def test_success_summary_reports_future_b1_and_revision(self):
        data = self.authored("4B1")
        self.assertEqual([], validator.validate_data(data))
        self.assertIn(
            "Priority 8 4B1 staging revision 2",
            validator.success_summary(data),
        )


if __name__ == "__main__":
    unittest.main()
