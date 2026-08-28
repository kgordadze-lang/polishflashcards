"""Priority 8 Phase 4C4C approved release-governance freeze tests."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import priority7_tooling as tooling  # noqa: E402
import priority8_phase4c4c_release_freeze as release  # noqa: E402

PHASE4C4C_COMMIT = "3d60bc61a85066007a659be4837aafc16131f0e4"
PHASE4C4C_REPORT = "reports/priority-8-phase-4c4c-release-freeze.md"
PHASE4C4C_BRANCH = "priority-8-phase-4c-architecture"


def sha256_file(relative):
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def git_bytes(relative, commit=PHASE4C4C_COMMIT):
    run = subprocess.run(
        ["git", "show", f"{commit}:{relative}"], cwd=ROOT,
        capture_output=True)
    if run.returncode != 0:
        raise AssertionError(
            f"historical object unavailable: {commit}:{relative}: "
            f"{run.stderr.decode('utf-8', errors='replace')}")
    return run.stdout


def git_json(relative, commit=PHASE4C4C_COMMIT):
    return json.loads(git_bytes(relative, commit).decode("utf-8"))


def historical_sha256(relative, commit=PHASE4C4C_COMMIT):
    return hashlib.sha256(git_bytes(relative, commit)).hexdigest()


def historical_phase4c4c_branch(report_bytes=None):
    """Read the exact Phase 4C4C workflow context from immutable history."""
    if report_bytes is None:
        report_bytes = git_bytes(PHASE4C4C_REPORT)
    text = report_bytes.decode("utf-8")
    marker = f"The work began on `{PHASE4C4C_BRANCH}` at"
    if text.count(marker) != 1:
        raise AssertionError(
            "historical Phase 4C4C branch evidence mismatch: "
            f"expected exactly one {marker!r}")
    return PHASE4C4C_BRANCH


@contextmanager
def historical_phase4c4c_production():
    """Run Phase 4C4C's gate against production at its owned endpoint."""
    original_read_json = release.read_json
    original_file_digest = release.file_digest

    def historical_read_json(relative):
        if relative in release.PRODUCTION_SHA256:
            return git_json(relative)
        return original_read_json(relative)

    def historical_file_digest(relative):
        if relative in release.PRODUCTION_SHA256:
            return historical_sha256(relative)
        return original_file_digest(relative)

    with mock.patch.object(
            release, "read_json", side_effect=historical_read_json), \
            mock.patch.object(
                release, "file_digest", side_effect=historical_file_digest):
        yield


def pattern_rows(document):
    return list(release.iter_patterns(document))


class Phase4C4CReleaseFreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with historical_phase4c4c_production():
            cls.corpus, cls.context_document, cls.frozen, cls.changed = release.build()
        cls.summary = release.metrics(cls.corpus, cls.frozen)
        cls.review_set, cls.new_lemma_ids = release.review_sets(cls.corpus)
        cls.rows = [(lemma, meaning, pattern)
                    for lemma, meaning, pattern in pattern_rows(cls.corpus)
                    if pattern["id"] in cls.review_set]
        cls.by_id = {pattern["id"]: (lemma, meaning, pattern)
                     for lemma, meaning, pattern in cls.rows}
        cls.start_corpus = json.loads(subprocess.check_output(
            ["git", "show", f"{release.STARTING_HEAD}:{release.CORPUS_PATH}"],
            cwd=ROOT))
        cls.start_by_id = {
            pattern["id"]: pattern
            for lemma, meaning, pattern in pattern_rows(cls.start_corpus)
            if pattern["id"] in cls.review_set}
        cls.candidates = release.read_json(release.CANDIDATES_PATH)
        cls.stable_map = release.read_json(release.STABLE_MAP_PATH)
        cls.context = release.validation_context(cls.context_document)

    def rejected_editorial(self, corpus, *codes):
        observed = {issue.code for issue in tooling.validate_editorial(
            corpus, self.context)}
        self.assertTrue(set(codes) & observed, (codes, sorted(observed)))

    def rejected_frozen(self, frozen, *codes):
        observed = {issue.code for issue in tooling.validate_frozen_release(frozen)}
        self.assertTrue(set(codes) & observed, (codes, sorted(observed)))

    def changed_pattern(self, index=0):
        corpus = copy.deepcopy(self.corpus)
        rows = [(l, m, p) for l, m, p in pattern_rows(corpus)
                if p["id"] in self.review_set]
        return corpus, rows[index]

    # Exact review set and append-only five-event transition.
    def test_01_review_set_is_exactly_224(self):
        self.assertEqual(224, len(self.review_set))

    def test_02_manifest_preview_editorial_and_stable_map_sets_are_equal(self):
        observed, _ = release.review_sets(self.corpus)
        self.assertEqual(self.review_set, observed)

    def test_03_first_two_events_are_preserved_exactly(self):
        for _lemma, _meaning, pattern in self.rows:
            self.assertEqual(
                self.start_by_id[pattern["id"]]["reviewEvents"],
                pattern["reviewEvents"][:2])

    def test_04_every_history_has_exactly_five_events(self):
        self.assertTrue(all(len(pattern["reviewEvents"]) == 5
                            for _lemma, _meaning, pattern in self.rows))

    def test_05_final_event_sequence_is_exact(self):
        expected = ["reference-verification", "editorial-review",
                    "editorial-review", "editorial-review", "product-approval"]
        self.assertTrue(all([event["kind"] for event in pattern["reviewEvents"]]
                            == expected for _l, _m, pattern in self.rows))

    def test_06_event_3_is_changes_requested(self):
        self.assertTrue(all(pattern["reviewEvents"][2]["decision"] ==
                            "changes-requested" for _l, _m, pattern in self.rows))

    def test_07_event_3_is_nonhuman_actor_borne(self):
        self.assertTrue(all(
            event.get("actorRef") == "priority8-editorial-review" and
            "reviewerRef" not in event
            for _l, _m, pattern in self.rows
            for event in [pattern["reviewEvents"][2]]))

    def test_08_event_3_note_is_narrow_and_truthful(self):
        self.assertTrue(all(pattern["reviewEvents"][2]["note"] ==
                            release.EVENT3_NOTE for _l, _m, pattern in self.rows))

    # Audio transition, event 4 currency, and human approval.
    def test_09_exactly_224_examples_transitioned_false_to_true(self):
        self.assertEqual(224, sum(
            self.start_by_id[pattern["id"]]["examples"][0]["audioEligible"] is False
            and pattern["examples"][0]["audioEligible"] is True
            for _l, _m, pattern in self.rows))

    def test_10_no_other_example_field_changed(self):
        for _l, _m, pattern in self.rows:
            old = self.start_by_id[pattern["id"]]["examples"][0]
            new = pattern["examples"][0]
            self.assertEqual({k: v for k, v in old.items() if k != "audioEligible"},
                             {k: v for k, v in new.items() if k != "audioEligible"})

    def test_11_event_4_is_fresh_editorial_accept(self):
        self.assertTrue(all(
            (pattern["reviewEvents"][3]["kind"],
             pattern["reviewEvents"][3]["decision"]) ==
            ("editorial-review", "accept") for _l, _m, pattern in self.rows))

    def test_12_event_4_scope_digest_is_current(self):
        for lemma, meaning, pattern in self.rows:
            self.assertEqual(
                tooling.review_scope_digest(
                    "editorial-review", lemma, meaning, pattern),
                pattern["reviewEvents"][3]["scopeDigest"])

    def test_13_event_4_has_valid_corroboration(self):
        self.assertTrue(all(pattern["reviewEvents"][3][
            "corroboratingActorRefs"] == ["priority8-editorial-corroboration"]
            for _l, _m, pattern in self.rows))

    def test_14_event_4_actors_are_independent(self):
        self.assertTrue(all(
            pattern["reviewEvents"][3]["actorRef"] not in
            pattern["reviewEvents"][3]["corroboratingActorRefs"]
            for _l, _m, pattern in self.rows))

    def test_15_pre_product_prefix_derives_editorial_reviewed(self):
        for lemma, meaning, pattern in self.rows:
            candidate = copy.deepcopy(pattern)
            candidate["reviewEvents"] = candidate["reviewEvents"][:4]
            self.assertEqual("editorial-reviewed",
                             release.current_state(candidate, lemma, meaning).state)

    def test_16_exactly_224_product_approvals_exist(self):
        self.assertEqual(224, self.summary["productApprovals"])

    def test_17_product_approvals_use_exact_human_reviewer(self):
        self.assertTrue(all(pattern["reviewEvents"][4].get("reviewerRef") ==
                            "product-owner-001" for _l, _m, pattern in self.rows))

    def test_18_product_approvals_have_no_actor_ref(self):
        self.assertTrue(all("actorRef" not in pattern["reviewEvents"][4]
                            for _l, _m, pattern in self.rows))

    def test_19_approval_date_is_grounded(self):
        self.assertEqual({"2026-08-26"}, {
            pattern["reviewEvents"][4]["reviewedAt"]
            for _l, _m, pattern in self.rows})

    def test_20_product_approval_scope_is_current(self):
        for lemma, meaning, pattern in self.rows:
            self.assertEqual(
                tooling.review_scope_digest(
                    "product-approval", lemma, meaning, pattern),
                pattern["reviewEvents"][4]["scopeDigest"])

    def test_21_all_224_states_are_derived_approved(self):
        self.assertEqual(224, self.summary["approved"])
        for lemma, meaning, pattern in self.rows:
            self.assertEqual("approved",
                             release.current_state(pattern, lemma, meaning).state)

    def test_22_editorial_validator_has_zero_issues(self):
        self.assertEqual([], tooling.validate_editorial(self.corpus, self.context))

    # Semantic and activity boundaries.
    def test_23_all_activity_eligibility_arrays_remain_empty(self):
        self.assertEqual(224, self.summary["activityEligibilityEmpty"])

    def test_24_no_listening_type_it_or_mixed_authority_exists(self):
        forbidden = {"listening", "type-it", "mixed-quiz"}
        self.assertFalse(any(forbidden & set(pattern["activityEligibility"])
                             for _l, _m, pattern in self.rows))

    def test_25_semantic_drift_is_zero_except_audio_and_governance(self):
        for _l, _m, pattern in self.rows:
            expected = copy.deepcopy(self.start_by_id[pattern["id"]])
            expected["examples"][0]["audioEligible"] = True
            for field in set(expected) - {"reviewEvents", "reviewState"}:
                self.assertEqual(expected.get(field), pattern.get(field),
                                 (pattern["id"], field))

    def test_26_exactly_seven_source_complements_remain(self):
        self.assertEqual(7, sum(
            complement["role"] == "source" for _l, _m, pattern in self.rows
            for complement in pattern["complements"]))

    def test_27_six_genuine_family_targets_remain(self):
        families = {"wracać", "wrócić", "wyjść", "kupować", "kupić"}
        self.assertEqual(6, sum(
            complement["role"] == "target"
            for lemma, _m, pattern in self.rows
            if lemma["canonicalLemma"] in families
            for complement in pattern["complements"]))

    def test_28_exactly_eleven_direct_speech_patterns_remain(self):
        self.assertEqual(11, sum(any(
            complement.get("clauseKind") == "direct-speech"
            for complement in pattern["complements"])
            for _l, _m, pattern in self.rows))

    def test_29_exactly_two_patterns_carry_required_lexical_items(self):
        lexical = [pattern for _l, _m, pattern in self.rows
                   if "requiredLexicalItems" in pattern]
        self.assertEqual(2, len(lexical))
        self.assertTrue(all(pattern["requiredLexicalItems"] == ["udział"]
                            for pattern in lexical))

    def test_30_udzial_survives_frozen_structure(self):
        structures = [row for row in self.frozen["structure"]
                      if row.get("requiredLexicalItems") == ["udział"]]
        self.assertEqual(2, len(structures))

    def test_31_udzial_survives_independent_runtime_reconstruction(self):
        reconstructed = tooling._derive_runtime_from_frozen(
            3,
            {row["id"]: row for row in self.frozen["identity"]},
            {row["id"]: row for row in self.frozen["structure"]},
            {row["id"]: row for row in self.frozen["wording"]},
            {row["id"]: row for row in self.frozen["policy"]})
        lexical = [pattern for lemma in reconstructed["lemmas"]
                   for meaning in lemma["meanings"]
                   for pattern in meaning["patterns"]
                   if pattern.get("requiredLexicalItems") == ["udział"]]
        self.assertEqual(2, len(lexical))

    # Freeze, allocations, release admission, and truthful authority.
    def test_32_candidate_freeze_is_unchanged(self):
        self.assertEqual(release.IMMUTABLE_SHA256[release.KEY_FREEZE_PATH],
                         sha256_file(release.KEY_FREEZE_PATH))

    def test_33_stable_map_is_unchanged(self):
        self.assertEqual(release.IMMUTABLE_SHA256[release.STABLE_MAP_PATH],
                         sha256_file(release.STABLE_MAP_PATH))

    def test_34_new_priority8_allocations_equal_611(self):
        self.assertEqual(611, self.summary["newPriority8Allocations"])

    def test_35_released_allocations_equal_154(self):
        self.assertEqual(154, self.summary["releasedAllocations"])

    def test_36_total_allocation_universe_equals_765(self):
        self.assertEqual(765, self.summary["totalAllocations"])

    def test_37_allocation_ids_have_no_collisions(self):
        ids = [row["id"] for row in self.frozen["allocations"]]
        self.assertEqual(765, len(set(ids)))

    def test_38_no_vp_x_allocation_exists(self):
        self.assertFalse(any(row["id"].startswith("vp-x-")
                             for row in self.frozen["allocations"]))

    def test_39_zero_tombstones_exist(self):
        self.assertEqual(0, self.summary["tombstones"])

    def test_40_metadata_only_identities_are_excluded(self):
        metadata = self.candidates["governance"]["metadataOnlyAspectRelations"]
        self.assertEqual({"zaczynać", "przeczytać"},
                         {row["metadataAspectPartner"]["canonicalLemma"]
                          for row in metadata})
        allocated = {row.get("canonicalLemmaAtAllocation")
                     for row in self.frozen["allocations"]}
        self.assertTrue({"zaczynać", "przeczytać"}.isdisjoint(allocated))

    def test_41_exactly_ten_deferrals_remain(self):
        self.assertEqual(10, len(self.candidates["deferralLedger"]))

    def test_42_frozen_identity_is_valid(self):
        self.assertEqual([], tooling.validate_frozen_release(self.frozen))
        self.assertEqual(765, len(self.frozen["identity"]))

    def test_43_frozen_structure_is_valid(self):
        self.assertEqual(765, len(self.frozen["structure"]))

    def test_44_frozen_wording_is_valid(self):
        self.assertEqual(765, len(self.frozen["wording"]))

    def test_45_frozen_policy_is_valid(self):
        self.assertEqual(765, len(self.frozen["policy"]))

    def test_46_frozen_runtime_parity_is_exact(self):
        self.assertEqual(
            self.frozen["runtimeProjection"],
            tooling.verified_runtime_from_frozen(self.frozen))

    def test_47_frozen_digests_are_deterministic(self):
        with historical_phase4c4c_production():
            again = release.freeze(self.corpus, {
                **self.context_document, "allocationRegistry": {}})
        self.assertEqual(release.canonical_bytes(self.frozen),
                         release.canonical_bytes(again))

    def test_48_release_authorization_is_derived(self):
        self.assertEqual({
            "releaseModes": ["solo-maintainer-reference-backed"],
            "humanVerifiedPatternIds": [],
            "humanNativeReviewedPatternIds": [],
        }, self.frozen["releaseAuthorization"])

    def test_49_exactly_224_priority8_patterns_are_admitted(self):
        self.assertEqual(224, self.summary["admittedPriority8Patterns"])

    def test_50_authority_chain_is_truthful(self):
        for _l, _m, pattern in self.rows:
            self.assertIn("actorRef", pattern["reviewEvents"][0])
            self.assertIn("actorRef", pattern["reviewEvents"][1])
            self.assertIn("reviewerRef", pattern["reviewEvents"][4])

    def test_51_no_human_editorial_or_audio_qa_claim_exists(self):
        notes = " ".join(event.get("note", "") for _l, _m, pattern in self.rows
                         for event in pattern["reviewEvents"][2:])
        self.assertIn("No human language review", notes)
        self.assertIn("audio QA", notes)

    # Immutable receipt/private/production/runtime isolation and hygiene.
    def test_52_immutable_review_receipt_is_unchanged(self):
        self.assertEqual(release.IMMUTABLE_SHA256[release.MANIFEST_PATH],
                         sha256_file(release.MANIFEST_PATH))

    def test_53_all_private_inputs_are_unchanged(self):
        for relative, expected in release.IMMUTABLE_SHA256.items():
            self.assertEqual(expected, sha256_file(relative), relative)

    def test_54_all_production_inputs_are_unchanged(self):
        for relative, expected in release.PRODUCTION_SHA256.items():
            historical = git_bytes(relative)
            self.assertEqual(expected, historical_sha256(relative), relative)
            with self.assertRaises(AssertionError):
                self.assertEqual(
                    expected,
                    hashlib.sha256(historical + b"\n# historical-tamper").hexdigest())
        index = git_bytes("index.html").decode("utf-8")
        service_worker = git_bytes("sw.js").decode("utf-8")
        self.assertIn('APP_VERSION = "8.12"', index)
        self.assertIn('CACHE = "popolsku-v67"', service_worker)
        with self.assertRaises(AssertionError):
            self.assertIn(
                'APP_VERSION = "8.12"',
                index.replace('APP_VERSION = "8.12"', 'APP_VERSION = "8.13"'))
        with self.assertRaises(AssertionError):
            self.assertIn(
                'CACHE = "popolsku-v67"',
                service_worker.replace(
                    'CACHE = "popolsku-v67"', 'CACHE = "popolsku-v68"'))

    def test_55_production_remains_30_34_45_45_revision_2(self):
        runtime = git_json(release.RUNTIME_PATH)
        meanings = [meaning for lemma in runtime["lemmas"]
                    for meaning in lemma["meanings"]]
        patterns = [pattern for meaning in meanings for pattern in meaning["patterns"]]
        examples = [example for pattern in patterns
                    for example in pattern.get("examples", [])]
        self.assertEqual((30, 34, 45, 45, 2, 2),
                         (len(runtime["lemmas"]), len(meanings), len(patterns),
                          len(examples), runtime["formatVersion"],
                          runtime["patternDataRevision"]))
        mutated = copy.deepcopy(runtime)
        mutated["lemmas"].pop()
        mutated["patternDataRevision"] = 3
        mutated_meanings = [meaning for lemma in mutated["lemmas"]
                            for meaning in lemma["meanings"]]
        mutated_patterns = [pattern for meaning in mutated_meanings
                            for pattern in meaning["patterns"]]
        mutated_examples = [example for pattern in mutated_patterns
                            for example in pattern.get("examples", [])]
        with self.assertRaises(AssertionError):
            self.assertEqual(
                (30, 34, 45, 45, 2, 2),
                (len(mutated["lemmas"]), len(mutated_meanings),
                 len(mutated_patterns), len(mutated_examples),
                 mutated["formatVersion"], mutated["patternDataRevision"]))

    def test_56_nonrelease_projection_does_not_mutate_production(self):
        self.assertEqual(release.PRODUCTION_SHA256[release.RUNTIME_PATH],
                         historical_sha256(release.RUNTIME_PATH))

    def test_57_verify_only_mode_writes_nothing(self):
        before = {path: sha256_file(path) for path in (
            release.CORPUS_PATH, release.CONTEXT_PATH, release.MANIFEST_PATH)}
        current_git = release.git

        def historical_git(*args):
            if args == ("branch", "--show-current"):
                return historical_phase4c4c_branch()
            return current_git(*args)

        with historical_phase4c4c_production(), \
                mock.patch.object(release, "git", side_effect=historical_git):
            self.assertEqual(0, release.main([]))
        after = {path: sha256_file(path) for path in before}
        self.assertEqual(before, after)

    def test_58_historical_branch_context_is_immutable_not_current(self):
        report_bytes = git_bytes(PHASE4C4C_REPORT)
        self.assertEqual(PHASE4C4C_BRANCH, historical_phase4c4c_branch())

        mutated = report_bytes.replace(
            f"`{PHASE4C4C_BRANCH}`".encode(), b"`main`", 1)
        self.assertNotEqual(report_bytes, mutated)
        with self.assertRaisesRegex(
                AssertionError, "historical Phase 4C4C branch evidence mismatch"):
            historical_phase4c4c_branch(mutated)

        with mock.patch.object(release, "git", return_value="main") as current_git:
            self.assertEqual(PHASE4C4C_BRANCH, historical_phase4c4c_branch())
        current_git.assert_not_called()

    def test_59_context_registry_is_exactly_the_frozen_universe(self):
        self.assertEqual(
            {row["id"] for row in self.frozen["allocations"]},
            set(self.context_document["allocationRegistry"]))

    # Adversarial fail-closed tests.
    def test_60_rejects_missing_event_3_and_direct_old_acceptance_to_product(self):
        corpus, (_l, _m, pattern) = self.changed_pattern()
        del pattern["reviewEvents"][2]
        with self.assertRaises(release.GateFailure):
            release.verify_approved_corpus(corpus)

    def test_61_rejects_missing_event_4(self):
        corpus, (_l, _m, pattern) = self.changed_pattern()
        del pattern["reviewEvents"][3]
        with self.assertRaises(release.GateFailure):
            release.verify_approved_corpus(corpus)

    def test_62_rejects_audio_true_with_stale_editorial_acceptance(self):
        corpus, (_l, _m, pattern) = self.changed_pattern()
        pattern["reviewEvents"] = pattern["reviewEvents"][:2]
        pattern["reviewState"] = "editorial-reviewed"
        self.rejected_editorial(corpus, "REVIEW_SCOPE_STALE", "AUDIO_NOT_AUTHORIZED")

    def test_63_rejects_wrong_event_4_scope_digest(self):
        corpus, (_l, _m, pattern) = self.changed_pattern()
        pattern["reviewEvents"][3]["scopeDigest"] = "sha256:" + "0" * 64
        self.rejected_editorial(
            corpus, "REVIEW_SCOPE_STALE", "REVIEW_STATE_MISMATCH")

    def test_64_rejects_event_4_self_corroboration(self):
        corpus, (_l, _m, pattern) = self.changed_pattern()
        pattern["reviewEvents"][3]["corroboratingActorRefs"] = [
            pattern["reviewEvents"][3]["actorRef"]]
        self.rejected_editorial(corpus, "EDITORIAL_CORROBORATION_SELF")

    def test_65_rejects_nonhuman_or_wrong_product_approver(self):
        corpus, (_l, _m, pattern) = self.changed_pattern()
        event = pattern["reviewEvents"][4]
        event["reviewerRef"] = "priority8-editorial-review"
        self.rejected_editorial(
            corpus, "REVIEWER_REGISTRY_DANGLING", "REVIEWER_NOT_HUMAN")

    def test_66_rejects_missing_reviewer_ref(self):
        corpus, (_l, _m, pattern) = self.changed_pattern()
        del pattern["reviewEvents"][4]["reviewerRef"]
        self.rejected_editorial(corpus, "SCHEMA_REQUIRED")

    def test_67_rejects_approval_over_pre_audio_scope(self):
        corpus, (lemma, meaning, pattern) = self.changed_pattern()
        old = copy.deepcopy(pattern)
        old["examples"][0]["audioEligible"] = False
        pattern["reviewEvents"][4]["scopeDigest"] = tooling.review_scope_digest(
            "product-approval", lemma, meaning, old)
        self.rejected_editorial(
            corpus, "REVIEW_SCOPE_STALE", "REVIEW_STATE_MISMATCH")

    def test_68_rejects_one_missing_or_extra_product_approval(self):
        corpus, (_l, _m, pattern) = self.changed_pattern()
        pattern["reviewEvents"].pop()
        with self.assertRaises(release.GateFailure):
            release.verify_approved_corpus(corpus)
        corpus, (_l, _m, pattern) = self.changed_pattern()
        pattern["reviewEvents"].append(copy.deepcopy(pattern["reviewEvents"][-1]))
        with self.assertRaises(release.GateFailure):
            release.verify_approved_corpus(corpus)

    def test_69_rejects_only_223_audio_examples_enabled(self):
        corpus, (_l, _m, pattern) = self.changed_pattern()
        pattern["examples"][0]["audioEligible"] = False
        with self.assertRaises(release.GateFailure):
            release.verify_approved_corpus(corpus)

    def test_70_rejects_activity_or_listening_eligibility(self):
        for value in (["reference"], ["listening"], ["type-it"], ["mixed-quiz"]):
            corpus, (_l, _m, pattern) = self.changed_pattern()
            pattern["activityEligibility"] = value
            with self.subTest(value=value), self.assertRaises(release.GateFailure):
                release.verify_approved_corpus(corpus)

    def test_71_rejects_source_target_and_purchase_price_regressions(self):
        source_rows = [(i, p) for i, (_l, _m, p) in enumerate(self.rows)
                       if any(c["role"] == "source" for c in p["complements"])]
        corpus, (_l, _m, pattern) = self.changed_pattern(source_rows[0][0])
        next(c for c in pattern["complements"] if c["role"] == "source")[
            "role"] = "target"
        with self.assertRaises(release.GateFailure):
            release.verify_approved_corpus(corpus)

    def test_72_rejects_direct_speech_downgrade(self):
        index = next(i for i, (_l, _m, p) in enumerate(self.rows)
                     if any(c.get("clauseKind") == "direct-speech"
                            for c in p["complements"]))
        corpus, (_l, _m, pattern) = self.changed_pattern(index)
        next(c for c in pattern["complements"]
             if c.get("clauseKind") == "direct-speech")["clauseKind"] = "ze"
        with self.assertRaises(release.GateFailure):
            release.verify_approved_corpus(corpus)

    def test_73_rejects_required_lexical_items_removal_reorder_or_tamper(self):
        index = next(i for i, (_l, _m, p) in enumerate(self.rows)
                     if "requiredLexicalItems" in p)
        for replacement in (None, ["inny"], ["udział", "drugi"]):
            corpus, (_l, _m, pattern) = self.changed_pattern(index)
            if replacement is None:
                del pattern["requiredLexicalItems"]
            else:
                pattern["requiredLexicalItems"] = replacement
            with self.subTest(replacement=replacement), self.assertRaises(
                    release.GateFailure):
                release.verify_approved_corpus(corpus)

    def test_74_rejects_stable_id_replacement_or_candidate_key_rename(self):
        corpus, (_l, _m, pattern) = self.changed_pattern()
        pattern["id"] = pattern["id"][:-12] + "000000000000"
        self.rejected_editorial(
            corpus, "ID_ALLOCATION_MISMATCH", "ID_GLOBAL_DUPLICATE",
            "ID_RECOMPUTATION", "ALLOCATION_PARENT")
        corpus, (_l, _m, pattern) = self.changed_pattern()
        pattern["key"] += "-renamed"
        self.rejected_editorial(
            corpus, "ID_ALLOCATION_MISMATCH", "ID_RECOMPUTATION",
            "ALLOCATION_KEY")

    def test_75_rejects_metadata_only_allocation(self):
        context = copy.deepcopy(self.context_document)
        sample = copy.deepcopy(next(iter(context["allocationRegistry"].values())))
        sample["id"] = "vp-l-zaczynac-000000000000"
        sample["seed"] = "v1|lemma|zaczynać"
        sample["canonicalLemmaAtAllocation"] = "zaczynać"
        context["allocationRegistry"][sample["id"]] = sample
        issues = tooling.validate_editorial(
            self.corpus, release.validation_context(context))
        self.assertTrue(issues)

    def test_76_rejects_new_tombstone_or_allocation_collision(self):
        tombstone = copy.deepcopy(self.frozen)
        tombstone["tombstones"].append({"id": "not-an-id"})
        self.rejected_frozen(tombstone, "SCHEMA_REQUIRED", "FROZEN_ORDER")
        collision = copy.deepcopy(self.frozen)
        collision["allocations"].append(copy.deepcopy(collision["allocations"][0]))
        self.rejected_frozen(collision, "FROZEN_ALLOCATION_DUPLICATE")

    def test_77_rejects_false_human_editorial_authority(self):
        corpus, (_l, _m, pattern) = self.changed_pattern()
        event = pattern["reviewEvents"][3]
        del event["actorRef"]
        event["reviewerRef"] = "product-owner-001"
        self.rejected_editorial(corpus, "SCHEMA_REQUIRED", "SCHEMA_UNKNOWN_FIELD")

    def test_78_rejects_incomplete_release_admission(self):
        frozen = copy.deepcopy(self.frozen)
        row = next(row for row in frozen["policy"]
                   if row["id"] in self.review_set)
        row["reviewState"] = "editorial-reviewed"
        self.rejected_frozen(
            frozen, "FROZEN_SCOPE_PARITY", "FROZEN_RUNTIME_PARITY",
            "FROZEN_RELEASE_AUTHORIZATION_PARITY",
            "FROZEN_REVIEW_STATE_MISMATCH", "AUDIO_NOT_AUTHORIZED")


if __name__ == "__main__":
    unittest.main()
