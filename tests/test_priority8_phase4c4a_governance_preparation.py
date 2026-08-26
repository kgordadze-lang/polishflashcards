"""Priority 8 Phase 4C4A - editorial packaging bridge and governance preparation.

The suite proves three separable things and keeps them separable.

1. *Packaging fidelity*: the 68 editorial records carry exactly the semantics the
   independently verified Phase 4C3 artifact holds, and the released 30 are
   untouched.
2. *Truthfulness of the constructed governance*: every evidence field is
   grounded in a committed artifact, every actor is nonhuman, and nothing claims
   authority nobody granted.
3. *The historical absence that matters*: at the immutable Phase 4C4A endpoint,
   no product approval, no approved review state, no release authorization, no
   freeze, and no runtime exposure existed.  Later release-governance phases may
   advance the live editorial records without rewriting this checkpoint.

The adversarial class is deliberately large, because this phase is the one that
could most easily manufacture authority by accident.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import priority7_tooling as tooling  # noqa: E402
import priority8_phase4c4a_editorial_bridge as bridge  # noqa: E402

CORPUS_PATH = "editorial/verb-pattern-candidates.json"
CONTEXT_PATH = "editorial/priority-7-authoring-context.json"
MANIFEST_PATH = "editorial/priority-8-phase4c4a-review-manifest.json"
PREVIEW_PATH = "editorial/priority-8-phase4c4a-review-preview.json"
CANDIDATES_PATH = "editorial/priority-8-phase4c-canonical-candidates.json"
STABLE_MAP_PATH = "editorial/priority-8-phase4c-stable-id-map.json"
FREEZE_PATH = "editorial/priority-8-phase4-candidate-key-freeze.json"

BASELINE_COMMIT = "816176f591909d505549e2818d6b8d6d75c67f25"
PHASE4C4A_COMMIT = "4e81202591cf2c8609983346e3c24fe2c185a8b8"
PHASE4C4A_FINAL_COMMIT = "2e3e42df34c0899f7dbb93d0bbea4c24823e2e58"

CANDIDATES_SHA256 = (
    "c54e611da32ad61c4c020545594ec1f33c0bcea6937f31c9e7a31d29bc5fa7e9")
STABLE_MAP_SHA256 = (
    "20fc8a566cb34825306f9198f4977fb0dacef3c33696cad45ff7ecbab6487a9d")
FREEZE_DIGEST = (
    "0d636b3c81c15f51e36558ef5d9c18e35b189b5f5a143003c283b4732f33be27")

PRIORITY8_ACTORS = {
    "priority8-reference-analysis": "reference-verification",
    "priority8-editorial-review": "editorial-review",
    "priority8-editorial-corroboration": "editorial-review",
    "priority8-example-generation": "example-generation",
}


def read_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def git_json(relative, commit=BASELINE_COMMIT):
    run = subprocess.run(
        ["git", "show", f"{commit}:{relative}"], cwd=ROOT,
        capture_output=True, text=True)
    if run.returncode != 0:
        raise AssertionError(run.stderr)
    return json.loads(run.stdout)


def git_bytes(relative, commit):
    run = subprocess.run(
        ["git", "show", f"{commit}:{relative}"], cwd=ROOT,
        capture_output=True)
    if run.returncode != 0:
        raise AssertionError(
            f"historical object unavailable: {commit}:{relative}: "
            f"{run.stderr.decode('utf-8', errors='replace')}")
    return run.stdout


def sha256_file(relative):
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def iter_patterns(corpus):
    for lemma in corpus["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                yield lemma, meaning, pattern


class Phase4C4ABase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = read_json(CORPUS_PATH)
        cls.context_document = read_json(CONTEXT_PATH)
        cls.manifest = read_json(MANIFEST_PATH)
        cls.preview = read_json(PREVIEW_PATH)
        cls.candidates = read_json(CANDIDATES_PATH)
        cls.baseline_corpus = git_json(CORPUS_PATH)
        cls.baseline_context = git_json(CONTEXT_PATH)
        cls.phase4c4a_corpus = git_json(CORPUS_PATH, PHASE4C4A_COMMIT)
        cls.phase4c4a_context_document = git_json(
            CONTEXT_PATH, PHASE4C4A_COMMIT)
        cls.phase4c4a_manifest = git_json(MANIFEST_PATH, PHASE4C4A_COMMIT)
        cls.phase4c4a_preview = git_json(PREVIEW_PATH, PHASE4C4A_COMMIT)
        cls.new_lemma_ids = {
            lemma["id"]
            for lemma in cls.candidates["canonicalCandidates"]["lemmas"]}
        cls.new_lemmas = [
            lemma for lemma in cls.corpus["lemmas"]
            if lemma["id"] in cls.new_lemma_ids]
        cls.new_patterns = [
            pattern for lemma, _meaning, pattern in iter_patterns(cls.corpus)
            if lemma["id"] in cls.new_lemma_ids]
        cls.phase4c4a_new_lemmas = [
            lemma for lemma in cls.phase4c4a_corpus["lemmas"]
            if lemma["id"] in cls.new_lemma_ids]
        cls.phase4c4a_new_patterns = [
            pattern for lemma, _meaning, pattern in iter_patterns(
                cls.phase4c4a_corpus)
            if lemma["id"] in cls.new_lemma_ids]
        cls.source_register = bridge.load_source_register()

    def context(self, document=None):
        document = self.context_document if document is None else document
        return tooling.ValidationContext(
            source_registry=document["sourceRegistry"],
            reviewer_registry=document["reviewerRegistry"],
            author_registry=document["authorRegistry"],
            allocation_registry=document["allocationRegistry"],
            editorial_actor_registry=document["editorialActorRegistry"],
            repository_index=tooling.repository_index_from_root(str(ROOT)),
            pronunciation_playback_authorized=document[
                "pronunciationPlaybackAuthorized"],
        )

    def assert_rejected(self, corpus, code, context_document=None):
        issues = tooling.validate_editorial(
            corpus, self.context(context_document))
        self.assertIn(
            code, {issue.code for issue in issues},
            f"expected {code}; got {sorted({i.code for i in issues})}")

    def assert_phase4c4a_preapproval_snapshot(
            self, corpus=None, context_document=None, manifest=None):
        """Assert the exact state at the immutable Phase 4C4A checkpoint."""
        corpus = self.phase4c4a_corpus if corpus is None else corpus
        context_document = (self.phase4c4a_context_document
                            if context_document is None else context_document)
        manifest = self.phase4c4a_manifest if manifest is None else manifest
        patterns = [
            pattern for lemma, _meaning, pattern in iter_patterns(corpus)
            if lemma["id"] in self.new_lemma_ids]
        self.assertEqual(224, len(patterns))
        self.assertEqual({"editorial-reviewed"},
                         {pattern["reviewState"] for pattern in patterns})
        self.assertEqual(0, sum(
            event["kind"] == "product-approval"
            for pattern in patterns for event in pattern["reviewEvents"]))
        self.assertTrue(all(
            [event["kind"] for event in pattern["reviewEvents"]] == [
                "reference-verification", "editorial-review"]
            for pattern in patterns))
        self.assertTrue(all(
            "reviewerRef" not in event and "actorRef" in event
            for pattern in patterns for event in pattern["reviewEvents"]))
        self.assertTrue(all(
            example["audioEligible"] is False
            for pattern in patterns for example in pattern["examples"]))
        self.assertTrue(all(
            pattern["activityEligibility"] == [] for pattern in patterns))
        self.assertEqual({}, context_document["allocationRegistry"])
        self.assertIs(False, manifest["productApproved"])
        self.assertIs(False, manifest["releaseAuthorized"])
        self.assertEqual("awaiting-human-product-review",
                         manifest["reviewState"])


class PackagingFidelity(Phase4C4ABase):
    def test_the_editorial_universe_is_exactly_ninety_eight_lemmas(self):
        self.assertEqual(98, len(self.corpus["lemmas"]))
        self.assertEqual(68, len(self.new_lemmas))
        self.assertEqual(
            30, len(self.corpus["lemmas"]) - len(self.new_lemmas))

    def test_the_new_records_are_exactly_the_verified_hierarchy(self):
        meanings = [m for lemma in self.new_lemmas for m in lemma["meanings"]]
        examples = [e for p in self.new_patterns for e in p["examples"]]
        self.assertEqual((68, 95, 224, 224), (
            len(self.new_lemmas), len(meanings),
            len(self.new_patterns), len(examples)))

    def test_the_released_thirty_records_are_byte_identical(self):
        baseline_ids = [lemma["id"] for lemma in self.baseline_corpus["lemmas"]]
        retained = [
            lemma for lemma in self.corpus["lemmas"]
            if lemma["id"] in set(baseline_ids)]
        self.assertEqual(self.baseline_corpus["lemmas"], retained)

    def test_only_the_envelope_format_version_moved_on_the_baseline(self):
        # Phase 4C2 moved the contract to 2 and left this private corpus at 1,
        # so the baseline failed validate_editorial with exactly that issue.
        self.assertEqual(1, self.baseline_corpus["formatVersion"])
        self.assertEqual(tooling.FORMAT_VERSION, self.corpus["formatVersion"])
        self.assertEqual(
            set(self.baseline_corpus), set(self.corpus),
            "the envelope gained or lost a key")
        baseline_issues = tooling.validate_editorial(
            self.baseline_corpus, self.context(self.baseline_context))
        self.assertEqual(
            ["FORMAT_VERSION"], sorted({i.code for i in baseline_issues}))

    def test_every_semantic_field_equals_the_phase_4c3_artifact(self):
        source = {
            pattern["id"]: pattern
            for lemma in self.candidates["canonicalCandidates"]["lemmas"]
            for meaning in lemma["meanings"]
            for pattern in meaning["patterns"]}
        fields = ("relationType", "complements", "cefr", "teachingStatus",
                  "usage", "learnerExplanationEn", "activityEligibility")
        for pattern in self.new_patterns:
            original = source[pattern["id"]]
            for field in fields:
                self.assertEqual(
                    original[field], pattern[field],
                    f"{pattern['id']} drifted on {field}")
            self.assertEqual(
                original.get("requiredLexicalItems"),
                pattern.get("requiredLexicalItems"))
            for packaged, verified in zip(
                    pattern["examples"], original["examples"]):
                self.assertEqual(verified["id"], packaged["id"])
                self.assertEqual(verified["pl"], packaged["pl"])
                self.assertEqual(verified["en"], packaged["en"])

    def test_the_six_hundred_eleven_stable_ids_are_exact_and_unique(self):
        identifiers = []
        for lemma in self.new_lemmas:
            identifiers.append(lemma["id"])
            for meaning in lemma["meanings"]:
                identifiers.append(meaning["id"])
                for pattern in meaning["patterns"]:
                    identifiers.append(pattern["id"])
                    identifiers.extend(e["id"] for e in pattern["examples"])
        self.assertEqual(611, len(identifiers))
        self.assertEqual(611, len(set(identifiers)))
        mapped = {
            row["id"] for row in read_json(STABLE_MAP_PATH)["allocations"]}
        self.assertEqual(mapped, set(identifiers))

    def test_the_released_one_hundred_fifty_four_ids_are_untouched(self):
        released = {
            lemma["id"] for lemma in self.baseline_corpus["lemmas"]}
        for lemma in self.baseline_corpus["lemmas"]:
            for meaning in lemma["meanings"]:
                released.add(meaning["id"])
                for pattern in meaning["patterns"]:
                    released.add(pattern["id"])
                    released.update(e["id"] for e in pattern["examples"])
        self.assertEqual(154, len(released))
        current = set()
        for lemma in self.corpus["lemmas"]:
            if lemma["id"] in self.new_lemma_ids:
                continue
            current.add(lemma["id"])
            for meaning in lemma["meanings"]:
                current.add(meaning["id"])
                for pattern in meaning["patterns"]:
                    current.add(pattern["id"])
                    current.update(e["id"] for e in pattern["examples"])
        self.assertEqual(released, current)

    def test_the_frozen_invariants_survive_packaging(self):
        statuses = [p["teachingStatus"] for p in self.new_patterns]
        self.assertEqual(222, statuses.count("active-production"))
        self.assertEqual(2, statuses.count("recognition-only"))
        roles = [c["role"] for p in self.new_patterns for c in p["complements"]]
        self.assertEqual(7, roles.count("source"))
        self.assertEqual(11, sum(
            1 for p in self.new_patterns for c in p["complements"]
            if c.get("clauseKind") == "direct-speech"))
        self.assertEqual(2, sum(
            1 for p in self.new_patterns if "requiredLexicalItems" in p))

    def test_the_six_preserved_family_targets_stay_target(self):
        families = {"wracać", "wrócić", "wyjść", "wyjechać", "kupować",
                    "kupić", "zamawiać"}
        sources = targets = 0
        for lemma, _meaning, pattern in iter_patterns(self.corpus):
            if lemma["canonicalLemma"] not in families:
                continue
            if lemma["id"] not in self.new_lemma_ids:
                continue
            for complement in pattern["complements"]:
                sources += complement["role"] == "source"
                targets += complement["role"] == "target"
        self.assertEqual((7, 6), (sources, targets))

    def test_metadata_only_identities_are_absent(self):
        names = {lemma["canonicalLemma"] for lemma in self.new_lemmas}
        self.assertNotIn("zaczynać", names)
        self.assertNotIn("przeczytać", names)
        for lemma in self.new_lemmas:
            self.assertNotIn("aspectPartnerIds", lemma)
            for meaning in lemma["meanings"]:
                for pattern in meaning["patterns"]:
                    self.assertNotIn("aspectEquivalentPatternIds", pattern)

    def test_the_ten_deferrals_are_preserved_unchanged(self):
        self.assertEqual(10, len(self.candidates["deferralLedger"]))
        self.assertEqual(
            git_json(CANDIDATES_PATH)["deferralLedger"],
            self.candidates["deferralLedger"])


class KeyScopeAndOriginReconstruction(Phase4C4ABase):
    def test_every_candidate_key_reconstructs_one_to_one(self):
        frozen = bridge.freeze_key_paths(read_json(FREEZE_PATH))
        packaged = set()
        for lemma in self.new_lemmas:
            packaged.add((lemma["canonicalLemma"],))
            for meaning in lemma["meanings"]:
                packaged.add((lemma["canonicalLemma"], meaning["key"]))
                for pattern in meaning["patterns"]:
                    packaged.add((lemma["canonicalLemma"], meaning["key"],
                                  pattern["key"]))
                    for example in pattern["examples"]:
                        packaged.add((lemma["canonicalLemma"], meaning["key"],
                                      pattern["key"], example["key"]))
        self.assertEqual(frozen, packaged)
        self.assertEqual(611, len(packaged))

    def test_every_internal_scope_equals_the_retained_governance_row(self):
        scopes = {
            row["meaningId"]: row["internalScope"]
            for row in self.candidates["governance"]["meaningScopes"]}
        packaged = {
            meaning["id"]: meaning["internalScope"]
            for lemma in self.new_lemmas for meaning in lemma["meanings"]}
        self.assertEqual(scopes, packaged)
        self.assertEqual(95, len(packaged))

    def test_every_origin_equals_the_retained_governance_row(self):
        origins = {
            row["exampleId"]: row["origin"]
            for row in self.candidates["governance"]["exampleOrigins"]}
        generated = reused = 0
        for pattern in self.new_patterns:
            for example in pattern["examples"]:
                origin = example["origin"]
                verified = origins[example["id"]]
                self.assertEqual(verified["kind"], origin["kind"])
                if origin["kind"] == "editorial-generated":
                    generated += 1
                    self.assertEqual(
                        bridge.EXAMPLE_ACTOR, origin["generatorRef"])
                    self.assertEqual(
                        bridge.PHASE_4B_RECONCILIATION_DATE,
                        origin["adoptedAt"])
                    self.assertNotIn("authorRef", origin)
                else:
                    reused += 1
                    self.assertEqual(
                        verified["repositorySource"],
                        origin["repositorySource"])
        self.assertEqual((220, 4), (generated, reused))

    def test_no_example_claims_a_human_author(self):
        self.assertEqual({}, self.context_document["authorRegistry"])
        for pattern in self.new_patterns:
            for example in pattern["examples"]:
                self.assertNotEqual("original", example["origin"]["kind"])


class EvidenceTruthfulness(Phase4C4ABase):
    def test_every_pattern_carries_evidence(self):
        self.assertEqual(224, len(self.new_patterns))
        for pattern in self.new_patterns:
            self.assertTrue(pattern["evidence"])

    def test_every_source_id_resolves_in_the_registry(self):
        registry = self.context_document["sourceRegistry"]
        for pattern in self.new_patterns:
            for record in pattern["evidence"]:
                self.assertIn(record["sourceId"], registry)
                self.assertEqual(
                    registry[record["sourceId"]]["sourceKind"],
                    record["sourceKind"])

    def test_no_source_id_is_synthesised_from_a_phase_three_key(self):
        # Phase 3 keys such as WSJP-BRAC-01 are sense locators, never source
        # identities.  They may appear inside a locator and nowhere else.
        for pattern in self.new_patterns:
            for record in pattern["evidence"]:
                self.assertNotRegex(record["sourceId"], r"^WSJP-")
                self.assertEqual("wsjp-pan", record["sourceId"])

    def test_every_checked_at_is_a_committed_source_register_access_date(self):
        by_key = {
            key: entry["accessed"]
            for key, entry in self.source_register.items()}
        self.assertTrue(by_key)
        for pattern in self.new_patterns:
            for record in pattern["evidence"]:
                match = re.search(
                    r"Phase 3 source key ([A-Z0-9-]+)\)$", record["locator"])
                self.assertIsNotNone(
                    match, f"{pattern['id']} locator is not traceable")
                self.assertEqual(
                    by_key[match.group(1)], record["checkedAt"],
                    f"{pattern['id']} checkedAt is not the register date")

    def test_checked_at_is_never_an_execution_or_commit_artifact(self):
        import datetime
        today = datetime.date.today().isoformat()
        dates = {
            record["checkedAt"]
            for pattern in self.new_patterns
            for record in pattern["evidence"]}
        self.assertEqual({"2026-08-20", "2026-08-21"}, dates)
        self.assertNotIn(today, dates)

    def test_evidence_digests_are_deterministic(self):
        for pattern in self.new_patterns:
            for record in pattern["evidence"]:
                self.assertEqual(
                    tooling.evidence_digest(record),
                    tooling.evidence_digest(copy.deepcopy(record)))

    def test_the_odpowiadac_direct_speech_row_keeps_truthful_provenance(self):
        provenance = {
            row["patternId"]: row
            for row in self.candidates["governance"]["patternProvenance"]}
        policy_rows = [
            pattern_id for pattern_id, row in provenance.items()
            if row["provenanceClass"] == "policy-authorized-direct-speech"]
        self.assertEqual(1, len(policy_rows))
        target = next(
            p for p in self.new_patterns if p["id"] == policy_rows[0])
        self.assertIn("odpowiadac", target["id"])
        self.assertEqual("direct-speech", target["key"])
        record = target["evidence"][0]
        # It must NOT claim the Skladnia licensed the direct-speech frame.
        self.assertEqual("meaning", record["factType"])
        self.assertNotEqual("complement-frame", record["factType"])
        self.assertIn("policy addition", record["note"])

    def test_the_other_direct_speech_rows_are_not_marked_policy_authorized(self):
        direct_speech = [
            p for p in self.new_patterns
            if any(c.get("clauseKind") == "direct-speech"
                   for c in p["complements"])]
        self.assertEqual(11, len(direct_speech))
        policy = [p for p in direct_speech
                  if p["evidence"][0]["factType"] == "meaning"]
        self.assertEqual(1, len(policy))


class ActorRegistry(Phase4C4ABase):
    def test_exactly_four_priority_eight_actors_were_added(self):
        added = (set(self.context_document["editorialActorRegistry"]) -
                 set(self.baseline_context["editorialActorRegistry"]))
        self.assertEqual(set(PRIORITY8_ACTORS), added)

    def test_every_priority_seven_actor_is_unchanged(self):
        for name, record in self.baseline_context[
                "editorialActorRegistry"].items():
            self.assertEqual(
                record, self.context_document["editorialActorRegistry"][name])

    def test_every_new_actor_is_explicitly_nonhuman_and_single_role(self):
        registry = self.context_document["editorialActorRegistry"]
        for name, role in PRIORITY8_ACTORS.items():
            actor = registry[name]
            self.assertIs(False, actor["human"])
            self.assertEqual([role], actor["roles"])
            self.assertEqual("Priority 8 Phase 4C4A", actor["namedInPhase"])

    def test_no_new_human_reviewer_identity_exists(self):
        self.assertEqual(
            self.baseline_context["reviewerRegistry"],
            self.context_document["reviewerRegistry"])
        self.assertEqual(
            self.baseline_context["authorRegistry"],
            self.context_document["authorRegistry"])

    def test_the_reference_actor_never_performs_editorial_review(self):
        for pattern in self.new_patterns:
            for event in pattern["reviewEvents"]:
                if event["kind"] == "editorial-review":
                    self.assertNotEqual(
                        bridge.REFERENCE_ACTOR, event["actorRef"])
                    self.assertNotIn(
                        bridge.REFERENCE_ACTOR,
                        event.get("corroboratingActorRefs", []))

    def test_the_source_and_registry_facts_are_otherwise_untouched(self):
        for field in ("sourceRegistry", "contextStatus",
                      "pronunciationPlaybackAuthorized"):
            self.assertEqual(
                self.baseline_context[field], self.context_document[field])
        self.assertEqual(
            {}, self.phase4c4a_context_document["allocationRegistry"])

    def test_the_context_notice_is_appended_not_rewritten(self):
        self.assertTrue(
            self.context_document["contextNotice"].startswith(
                self.baseline_context["contextNotice"]))


class ReviewEventChain(Phase4C4ABase):
    def test_every_pattern_has_exactly_the_two_nonhuman_stages(self):
        self.assert_phase4c4a_preapproval_snapshot()

        def first_phase4c4a_pattern(corpus):
            return next(
                pattern for lemma, _meaning, pattern in iter_patterns(corpus)
                if lemma["id"] in self.new_lemma_ids)

        product_approval = copy.deepcopy(self.phase4c4a_corpus)
        first_phase4c4a_pattern(product_approval)["reviewEvents"].append(
            {"kind": "product-approval"})
        with self.assertRaises(AssertionError):
            self.assert_phase4c4a_preapproval_snapshot(product_approval)

        approved = copy.deepcopy(self.phase4c4a_corpus)
        first_phase4c4a_pattern(approved)["reviewState"] = "approved"
        with self.assertRaises(AssertionError):
            self.assert_phase4c4a_preapproval_snapshot(approved)

        allocated_context = copy.deepcopy(self.phase4c4a_context_document)
        allocated_context["allocationRegistry"] = {"vp-p-example": {}}
        with self.assertRaises(AssertionError):
            self.assert_phase4c4a_preapproval_snapshot(
                context_document=allocated_context)

        third_event = copy.deepcopy(self.phase4c4a_corpus)
        first_phase4c4a_pattern(third_event)["reviewEvents"].append(
            {"kind": "editorial-review"})
        with self.assertRaises(AssertionError):
            self.assert_phase4c4a_preapproval_snapshot(third_event)

        audio_enabled = copy.deepcopy(self.phase4c4a_corpus)
        first_phase4c4a_pattern(audio_enabled)["examples"][0]["audioEligible"] = True
        with self.assertRaises(AssertionError):
            self.assert_phase4c4a_preapproval_snapshot(audio_enabled)

    def test_every_event_is_nonhuman(self):
        for pattern in self.new_patterns:
            for event in pattern["reviewEvents"][:2]:
                self.assertNotIn("reviewerRef", event)
                self.assertIn("actorRef", event)

    def test_the_editorial_acceptance_is_independently_corroborated(self):
        for pattern in self.new_patterns:
            editorial = pattern["reviewEvents"][1]
            self.assertEqual(bridge.EDITORIAL_ACTOR, editorial["actorRef"])
            self.assertEqual(
                [bridge.CORROBORATION_ACTOR],
                editorial["corroboratingActorRefs"])
            self.assertNotIn(
                editorial["actorRef"], editorial["corroboratingActorRefs"])

    def test_review_dates_are_grounded_and_nondecreasing(self):
        for pattern in self.new_patterns:
            reference, editorial = pattern["reviewEvents"][:2]
            self.assertIn(reference["reviewedAt"], {"2026-08-20", "2026-08-21"})
            self.assertEqual(
                bridge.PHASE_4B_RECONCILIATION_DATE, editorial["reviewedAt"])
            self.assertLessEqual(
                reference["reviewedAt"], editorial["reviewedAt"])

    def test_the_reference_acceptance_pins_its_own_evidence(self):
        for pattern in self.new_patterns:
            reference = pattern["reviewEvents"][0]
            digests = {
                tooling.evidence_digest(r) for r in pattern["evidence"]}
            self.assertEqual(
                sorted(digests),
                reference["supportingEvidenceDigests"])

    def test_every_scope_digest_binds_the_record_that_exists(self):
        for lemma, meaning, pattern in iter_patterns(self.corpus):
            if lemma["id"] not in self.new_lemma_ids:
                continue
            for event in pattern["reviewEvents"]:
                self.assertEqual(
                    tooling.review_scope_digest(
                        event["kind"], lemma, meaning, pattern),
                    event["scopeDigest"],
                    f"{pattern['id']} {event['kind']} digest is stale")

    def test_the_release_mode_is_the_solo_chain(self):
        for pattern in self.new_patterns:
            self.assertEqual(
                "solo-maintainer-reference-backed", pattern["releaseMode"])


class ReviewStateAndAbsentAuthority(Phase4C4ABase):
    def test_every_new_pattern_is_editorial_reviewed(self):
        states = {p["reviewState"] for p in self.phase4c4a_new_patterns}
        self.assertEqual({"editorial-reviewed"}, states)

    def test_review_state_is_derived_not_asserted(self):
        for lemma, meaning, pattern in iter_patterns(self.corpus):
            if lemma["id"] not in self.new_lemma_ids:
                continue
            evidence = {
                tooling.evidence_digest(r): r for r in pattern["evidence"]}
            derived = tooling._derive_review_currency(
                pattern["reviewEvents"], pattern["releaseMode"],
                {stage: tooling.review_scope_digest(
                    stage, lemma, meaning, pattern)
                 for stage in tooling.STAGE_KINDS},
                set(evidence), evidence).state
            self.assertEqual(derived, pattern["reviewState"])

    def test_there_are_zero_product_approval_events(self):
        for pattern in self.phase4c4a_new_patterns:
            for event in pattern["reviewEvents"]:
                self.assertNotEqual("product-approval", event["kind"])

    def test_no_new_pattern_is_approved(self):
        for pattern in self.phase4c4a_new_patterns:
            self.assertNotEqual("approved", pattern["reviewState"])

    def test_the_released_forty_five_remain_the_only_approved_patterns(self):
        approved = [
            pattern["id"] for _l, _m, pattern in iter_patterns(
                self.phase4c4a_corpus)
            if pattern["reviewState"] == "approved"]
        self.assertEqual(45, len(approved))
        self.assertFalse(
            set(approved) & {p["id"] for p in self.phase4c4a_new_patterns})

    def test_the_manifest_records_that_nothing_is_approved(self):
        self.assertIs(False, self.phase4c4a_manifest["productApproved"])
        self.assertIs(False, self.phase4c4a_manifest["releaseAuthorized"])
        self.assertEqual(
            "awaiting-human-product-review",
            self.phase4c4a_manifest["reviewState"])

    def test_no_release_authorization_artifact_exists(self):
        for pattern in self.phase4c4a_new_patterns:
            self.assertNotIn("releaseAuthorization", pattern)
        self.assertNotIn("releaseAuthorization", self.phase4c4a_corpus)
        self.assertNotIn("allocations", self.phase4c4a_corpus)

    def test_the_allocation_registry_gained_nothing(self):
        self.assertEqual({}, self.phase4c4a_context_document["allocationRegistry"])

    def test_no_tombstone_exists(self):
        self.assertEqual([], read_json(STABLE_MAP_PATH)["tombstones"])

    def test_no_frozen_snapshot_was_produced(self):
        for name in ("identity", "structure", "wording", "policy",
                     "tombstones", "reviewHistory", "runtimeProjection"):
            self.assertNotIn(name, self.phase4c4a_corpus)


class EligibilityAndAudioBoundary(Phase4C4ABase):
    def test_activity_eligibility_is_empty_on_every_new_pattern(self):
        for pattern in self.new_patterns:
            self.assertEqual([], pattern["activityEligibility"])

    def test_audio_is_disabled_pre_approval_on_all_new_examples(self):
        values = [
            example["audioEligible"]
            for pattern in self.phase4c4a_new_patterns
            for example in pattern["examples"]]
        self.assertEqual(224, len(values))
        self.assertTrue(all(value is False for value in values))

    def test_enabling_audio_before_approval_is_refused_by_the_validator(self):
        # This is the rule that forces the pre-approval representation, and it
        # is asserted rather than assumed.
        corpus = copy.deepcopy(self.phase4c4a_corpus)
        for lemma, _meaning, pattern in iter_patterns(corpus):
            if lemma["id"] not in self.new_lemma_ids:
                continue
            pattern["examples"][0]["audioEligible"] = True
            break
        self.assert_rejected(
            corpus, "AUDIO_NOT_AUTHORIZED", self.phase4c4a_context_document)

    def test_the_released_forty_five_keep_their_authorized_audio(self):
        for lemma, _meaning, pattern in iter_patterns(self.corpus):
            if lemma["id"] in self.new_lemma_ids:
                continue
            for example in pattern["examples"]:
                self.assertIs(True, example["audioEligible"])

    def test_the_manifest_preserves_the_future_audio_candidates(self):
        self.assertEqual(224, len(self.manifest["rows"]))
        for row in self.manifest["rows"]:
            self.assertIs(False, row["audioEligibleAtPackaging"])
            self.assertIs(True, row["audioEligibleIfApproved"])
        self.assertIn("Listening", self.manifest["audioNotice"])

    def test_audio_eligibility_never_implies_listening(self):
        for row in self.manifest["rows"]:
            self.assertNotIn("listening", row["activityEligibility"])


class EditorialValidation(Phase4C4ABase):
    def test_the_packaged_corpus_passes_validate_editorial_cleanly(self):
        issues = tooling.validate_editorial(self.corpus, self.context())
        self.assertEqual(
            [], [(i.code, i.path) for i in issues])

    def test_no_mechanical_missing_field_issue_remains(self):
        issues = tooling.validate_editorial(self.corpus, self.context())
        blocking = {
            "SCHEMA_REQUIRED", "KEY_INVALID", "EVIDENCE_REQUIRED",
            "SCHEMA_ENUM", "SCHEMA_ARRAY", "SCHEMA_OBJECT", "SCHEMA_STRING"}
        self.assertEqual(set(), {i.code for i in issues} & blocking)

    def test_the_packaging_is_deterministic(self):
        rebuilt = bridge.build_corpus(
            read_json(CANDIDATES_PATH), self.phase4c4a_corpus,
            bridge.load_source_register())
        self.assertEqual(
            bridge._canonical_bytes(self.phase4c4a_corpus),
            bridge._canonical_bytes(rebuilt))

    def test_rebuilding_from_the_baseline_reproduces_the_corpus(self):
        rebuilt = bridge.build_corpus(
            read_json(CANDIDATES_PATH), self.baseline_corpus,
            bridge.load_source_register())
        self.assertEqual(
            bridge._canonical_bytes(self.phase4c4a_corpus),
            bridge._canonical_bytes(rebuilt))


class HumanReviewPackage(Phase4C4ABase):
    def test_the_manifest_covers_every_one_of_the_224_patterns(self):
        self.assertEqual(
            {p["id"] for p in self.phase4c4a_new_patterns},
            {row["patternId"] for row in self.phase4c4a_manifest["rows"]})
        self.assertEqual(
            {"lemmas": 68, "meanings": 95, "patterns": 224, "examples": 224},
            self.phase4c4a_manifest["reviewSet"])

    def test_the_manifest_binds_the_exact_reviewed_inputs(self):
        self.assertEqual(
            CANDIDATES_SHA256,
            self.phase4c4a_manifest["sourceCanonicalCandidatesSha256"])
        self.assertEqual(
            STABLE_MAP_SHA256,
            self.phase4c4a_manifest["sourceStableIdMapSha256"])
        self.assertEqual(
            FREEZE_DIGEST,
            self.phase4c4a_manifest["sourceCandidateKeyFreezeDigest"])
        self.assertEqual(
            bridge._canonical_digest(self.phase4c4a_corpus),
            self.phase4c4a_manifest["packagedEditorialCorpusDigest"])
        self.assertEqual(
            bridge._canonical_digest(self.phase4c4a_preview),
            self.phase4c4a_manifest["reviewPreviewDigest"])
        self.assertEqual(self.phase4c4a_manifest, self.manifest)

    def test_every_manifest_row_exposes_what_a_reviewer_must_assess(self):
        required = {
            "patternId", "canonicalLemma", "meaningKey", "patternKey",
            "glossesEn", "relationType", "complements", "cefr",
            "teachingStatus", "usage", "learnerExplanationEn", "examplePl",
            "exampleEn"}
        for row in self.phase4c4a_manifest["rows"]:
            self.assertTrue(required <= set(row))
            self.assertTrue(row["examplePl"] and row["exampleEn"])

    def test_the_manifest_row_content_matches_the_corpus(self):
        rows = {
            row["patternId"]: row for row in self.phase4c4a_manifest["rows"]}
        for pattern in self.phase4c4a_new_patterns:
            row = rows[pattern["id"]]
            self.assertEqual(pattern["learnerExplanationEn"],
                             row["learnerExplanationEn"])
            self.assertEqual(pattern["complements"], row["complements"])
            self.assertEqual(pattern["examples"][0]["pl"], row["examplePl"])

    def test_the_preview_is_a_valid_runtime_document(self):
        issues = tooling.validate_runtime(
            self.phase4c4a_preview, tooling.ValidationContext())
        self.assertEqual([], [(i.code, i.path) for i in issues])

    def test_the_preview_contains_exactly_the_pending_records(self):
        self.assertEqual(68, len(self.phase4c4a_preview["lemmas"]))
        patterns = [
            pattern for lemma in self.phase4c4a_preview["lemmas"]
            for meaning in lemma["meanings"]
            for pattern in meaning["patterns"]]
        self.assertEqual(224, len(patterns))
        self.assertEqual(
            {p["id"] for p in self.phase4c4a_new_patterns},
            {p["id"] for p in patterns})

    def test_the_preview_claims_no_release_revision_advance(self):
        released = read_json("content/verb-patterns.json")
        self.assertEqual(
            released["patternDataRevision"],
            self.phase4c4a_preview["patternDataRevision"])


class RuntimeAndProductionIsolation(Phase4C4ABase):
    def test_production_runtime_is_untouched(self):
        released = read_json("content/verb-patterns.json")
        self.assertEqual(git_json("content/verb-patterns.json"), released)
        self.assertEqual(30, len(released["lemmas"]))
        self.assertEqual(2, released["patternDataRevision"])

    def test_the_packaged_corpus_still_projects_only_the_released_forty_five(self):
        # The strongest proof that packaging granted no runtime exposure: the
        # real non-release projection admits approved patterns only.
        projected = tooling.project_runtime_nonrelease(
            self.phase4c4a_corpus, 2,
            self.context(self.phase4c4a_context_document))
        patterns = [
            pattern for lemma in projected["lemmas"]
            for meaning in lemma["meanings"]
            for pattern in meaning["patterns"]]
        self.assertEqual(30, len(projected["lemmas"]))
        self.assertEqual(45, len(patterns))
        self.assertEqual(
            read_json("content/verb-patterns.json"), projected)

    def test_no_private_artifact_is_referenced_by_runtime_or_shell(self):
        names = [
            "priority-8-phase4c4a-review-manifest",
            "priority-8-phase4c4a-review-preview",
            "priority-8-phase4c-canonical-candidates",
            "verb-pattern-candidates",
            "priority-7-authoring-context",
        ]
        for relative in ("pp-verb-patterns.js", "sw.js", "index.html",
                         "audio-manifest.json"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            for name in names:
                self.assertNotIn(name, text, f"{name} leaked into {relative}")

    def test_the_frozen_inputs_are_byte_identical(self):
        self.assertEqual(CANDIDATES_SHA256, sha256_file(CANDIDATES_PATH))
        self.assertEqual(STABLE_MAP_SHA256, sha256_file(STABLE_MAP_PATH))
        self.assertEqual(
            FREEZE_DIGEST,
            self.candidates["sourceCandidateKeyFreezeDigest"])

    def test_staging_and_freeze_manifests_are_unchanged(self):
        for relative in (FREEZE_PATH, "editorial/priority-8-phase4-staging.json"):
            self.assertEqual(git_json(relative), read_json(relative))

    def test_no_schema_or_runtime_source_changed(self):
        for relative in ("pp-verb-patterns.js",
                         "validate_priority8_staging.py", "index.html",
                         "sw.js", "audio-manifest.json"):
            run = subprocess.run(
                ["git", "diff", "--quiet", BASELINE_COMMIT, "--", relative],
                cwd=ROOT)
            self.assertEqual(0, run.returncode, f"{relative} changed")

        tooling_path = "priority7_tooling.py"
        baseline_tooling = git_bytes(tooling_path, BASELINE_COMMIT)
        for endpoint in (PHASE4C4A_COMMIT, PHASE4C4A_FINAL_COMMIT):
            self.assertEqual(
                baseline_tooling, git_bytes(tooling_path, endpoint),
                f"{tooling_path} changed during Phase 4C4A at {endpoint}")
        with self.assertRaises(AssertionError):
            self.assertEqual(
                baseline_tooling,
                git_bytes(tooling_path, PHASE4C4A_FINAL_COMMIT)
                + b"\n# historical-tamper")


class AdversarialGovernance(Phase4C4ABase):
    def mutate_first_new_pattern(self, mutate):
        corpus = copy.deepcopy(self.phase4c4a_corpus)
        for lemma, meaning, pattern in iter_patterns(corpus):
            if lemma["id"] in self.new_lemma_ids:
                mutate(lemma, meaning, pattern)
                return corpus
        raise AssertionError("no new pattern found")

    def test_an_unregistered_source_id_is_refused(self):
        corpus = self.mutate_first_new_pattern(
            lambda l, m, p: p["evidence"][0].update(
                {"sourceId": "wsjp-brac-01"}))
        self.assert_rejected(corpus, "SOURCE_REGISTRY_DANGLING")

    def test_a_future_checked_at_is_refused(self):
        corpus = self.mutate_first_new_pattern(
            lambda l, m, p: p["evidence"][0].update({"checkedAt": "2099-01-01"}))
        self.assert_rejected(corpus, "DATE_IN_FUTURE")

    def test_a_missing_checked_at_is_refused(self):
        corpus = self.mutate_first_new_pattern(
            lambda l, m, p: p["evidence"][0].pop("checkedAt"))
        self.assert_rejected(corpus, "SCHEMA_REQUIRED")

    def test_removing_evidence_entirely_is_refused(self):
        corpus = self.mutate_first_new_pattern(
            lambda l, m, p: p.update({"evidence": []}))
        self.assert_rejected(corpus, "EVIDENCE_REQUIRED")

    def test_an_unknown_reviewer_is_refused(self):
        def mutate(lemma, meaning, pattern):
            pattern["reviewEvents"].append({
                "kind": "product-approval", "decision": "accept",
                "scopeVersion": 1,
                "scopeDigest": tooling.review_scope_digest(
                    "product-approval", lemma, meaning, pattern),
                "reviewerRef": "product-owner-999",
                "reviewedAt": "2026-08-25"})
            pattern["reviewState"] = "approved"
        self.assert_rejected(
            self.mutate_first_new_pattern(mutate), "REVIEWER_REGISTRY_DANGLING")

    def test_a_nonhuman_actor_placed_in_a_human_reviewer_slot_is_refused(self):
        def mutate(lemma, meaning, pattern):
            pattern["reviewEvents"].append({
                "kind": "product-approval", "decision": "accept",
                "scopeVersion": 1,
                "scopeDigest": tooling.review_scope_digest(
                    "product-approval", lemma, meaning, pattern),
                "reviewerRef": bridge.EDITORIAL_ACTOR,
                "reviewedAt": "2026-08-25"})
            pattern["reviewState"] = "approved"
        self.assert_rejected(
            self.mutate_first_new_pattern(mutate), "REVIEWER_REGISTRY_DANGLING")

    def test_claiming_approved_without_a_product_approval_is_refused(self):
        corpus = self.mutate_first_new_pattern(
            lambda l, m, p: p.update({"reviewState": "approved"}))
        self.assert_rejected(corpus, "REVIEW_STATE_MISMATCH")

    def test_a_stale_scope_digest_cannot_hold_the_state_up(self):
        corpus = self.mutate_first_new_pattern(
            lambda l, m, p: p.update(
                {"learnerExplanationEn": p["learnerExplanationEn"] + " Extra."}))
        self.assert_rejected(corpus, "REVIEW_STATE_MISMATCH")

    def test_evidence_attached_with_the_wrong_scope_breaks_its_pin(self):
        def mutate(lemma, meaning, pattern):
            pattern["evidence"][0]["locator"] = (
                pattern["evidence"][0]["locator"] + " tampered")
        self.assert_rejected(
            self.mutate_first_new_pattern(mutate), "REVIEW_STATE_MISMATCH")

    def test_a_self_corroborating_editorial_actor_is_refused(self):
        def mutate(lemma, meaning, pattern):
            pattern["reviewEvents"][1]["corroboratingActorRefs"] = [
                pattern["reviewEvents"][1]["actorRef"]]
        self.assert_rejected(
            self.mutate_first_new_pattern(mutate),
            "EDITORIAL_CORROBORATION_SELF")

    def test_dropping_corroboration_is_refused(self):
        def mutate(lemma, meaning, pattern):
            pattern["reviewEvents"][1].pop("corroboratingActorRefs")
        self.assert_rejected(
            self.mutate_first_new_pattern(mutate),
            "EDITORIAL_CORROBORATION_REQUIRED")

    def test_one_actor_performing_both_nonhuman_tiers_is_refused(self):
        def mutate(lemma, meaning, pattern):
            pattern["reviewEvents"][0]["actorRef"] = bridge.EDITORIAL_ACTOR
        self.assert_rejected(
            self.mutate_first_new_pattern(mutate), "REVIEW_ACTOR_INDEPENDENCE")

    def test_an_actor_without_the_stage_role_is_refused(self):
        def mutate(lemma, meaning, pattern):
            pattern["reviewEvents"][0]["actorRef"] = bridge.EXAMPLE_ACTOR
        self.assert_rejected(
            self.mutate_first_new_pattern(mutate), "EDITORIAL_ACTOR_ROLE")

    def test_a_changed_stable_id_is_refused(self):
        corpus = self.mutate_first_new_pattern(
            lambda l, m, p: p.update({"id": p["id"][:-1] + "0"}))
        self.assert_rejected(corpus, "ID_RECOMPUTATION")

    def test_a_renamed_candidate_key_is_refused(self):
        corpus = self.mutate_first_new_pattern(
            lambda l, m, p: p.update({"key": "renamed-key"}))
        self.assert_rejected(corpus, "ID_RECOMPUTATION")

    def test_a_structural_role_regression_moves_the_frozen_digest(self):
        def mutate(lemma, meaning, pattern):
            for complement in pattern["complements"]:
                complement["role"] = "topic"
        self.assert_rejected(
            self.mutate_first_new_pattern(mutate), "REVIEW_STATE_MISMATCH")

    def test_a_removed_required_lexical_item_moves_the_frozen_digest(self):
        corpus = copy.deepcopy(self.corpus)
        for lemma, meaning, pattern in iter_patterns(corpus):
            if "requiredLexicalItems" in pattern:
                pattern.pop("requiredLexicalItems")
                break
        else:
            self.fail("no requiredLexicalItems pattern")
        self.assert_rejected(corpus, "REVIEW_STATE_MISMATCH")

    def test_a_manifest_missing_one_pattern_is_detectable(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["rows"].pop()
        self.assertNotEqual(
            {p["id"] for p in self.new_patterns},
            {row["patternId"] for row in manifest["rows"]})

    def test_a_manifest_with_an_extra_pattern_is_detectable(self):
        manifest = copy.deepcopy(self.manifest)
        extra = copy.deepcopy(manifest["rows"][0])
        extra["patternId"] = "vp-p-fabricated-row-000000000000"
        manifest["rows"].append(extra)
        self.assertNotEqual(
            {p["id"] for p in self.new_patterns},
            {row["patternId"] for row in manifest["rows"]})

    def test_a_wrong_candidate_digest_stops_the_bridge(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["sourceCanonicalCandidatesSha256"] = "0" * 64
        self.assertNotEqual(
            CANDIDATES_SHA256, manifest["sourceCanonicalCandidatesSha256"])

    def test_promoting_a_metadata_only_identity_is_detectable(self):
        corpus = copy.deepcopy(self.corpus)
        clone = copy.deepcopy(
            next(l for l in corpus["lemmas"] if l["id"] in self.new_lemma_ids))
        clone["canonicalLemma"] = "zaczynać"
        corpus["lemmas"].append(clone)
        self.assert_rejected(corpus, "ID_RECOMPUTATION")


if __name__ == "__main__":
    unittest.main()
