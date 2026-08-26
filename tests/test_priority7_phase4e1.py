"""Priority 7 Phase 4E.1 nonhuman reference verification.

Phase 4E introduced the solo-maintainer release mode but shipped a mismatch:
``editorial-review`` accepted a nonhuman ``actorRef`` while
``reference-verification`` still demanded a human ``reviewerRef``.  Nothing had
yet been written under it, but the only way to use the mode as shipped would
have been to name a person -- realistically the project owner -- as a human
reference verifier they are not.

Phase 4E.1 removes that requirement.  The properties under test are:

* the actor contract is chosen from the governing release mode, not from the
  stage name alone: a solo reference verification carries an actorRef and
  cannot carry a reviewerRef, and the human chain refuses the stage outright;
* the actor records only that the workflow ran -- every Phase 4E evidence
  condition still decides whether the claim is verified;
* the reference and editorial tiers require independent nonhuman identities,
  because two names for one opinion corroborate nothing;
* release validity never depends on a commercial model or vendor name;
* product approval remains human, mandatory and mode-acknowledged;
* the fully human-reviewed chain is unchanged and unweakened;
* the frozen release keeps nonhuman verification distinguishable from human
  verification, and describes its own assurance without overstating it.

Everything exercised here is synthetic.  No lemma, sentence, reviewer, actor,
source or approval in this suite is real, and the suite re-proves at the end
that the real 45-pattern corpus advanced by exactly nothing.
"""

from __future__ import annotations

import collections
import copy
import csv
import hashlib
import json
import inspect
import subprocess
import tempfile
import unittest
from datetime import date
from pathlib import Path

import priority7_tooling as T
from priority7_tooling import (
    DEFAULT_RELEASE_MODE,
    EDITORIAL_ACTOR_ROLES,
    HUMAN_REVIEWED_MODE,
    SOLO_MAINTAINER_MODE,
    RepositoryIndex,
    ValidationContext,
    ValidationFailure,
    evidence_digest,
    freeze_editorial,
    review_scope_digest,
    validate_editorial,
    validate_frozen_release,
    validate_runtime,
    verified_runtime_from_frozen,
)

# Phase 4F-E1 normalisation.  Imported by path, with no dependency on any
# other import in this module, so it resolves identically under
# `python3 -m unittest`, a direct script run, and the importlib loading
# the later closure suites use.
import os.path as _e1_os_path
import sys as _e1_sys

_E1_DIR = _e1_os_path.dirname(_e1_os_path.abspath(__file__))
if _E1_DIR not in _e1_sys.path:
    _e1_sys.path.insert(0, _E1_DIR)

import priority7_phase4fe1_normalizer as E1
import priority7_phase4ff2_normalizer as F2
import priority7_phase4fh2_normalizer as H2
import priority7_phase4fh21_normalizer as H21


ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# Phase 4F-I1 normalisation, shared by every historical Priority 7 suite.
#
# Phase 4F-I1 activated the Priority 7 release as one atomic bundle: the
# official runtime document appeared at content/verb-patterns.json, index.html
# gained the single production loader call and APP_VERSION 8.10 -> 8.11, sw.js
# advanced popolsku-v65 -> v66 and learned the runtime's required-precache
# entry and its network-first classification, and the generator-owned pages
# were regenerated because their footer stamps APP_VERSION.
#
# The claims restated through this helper were true statements about the tiers
# that had run when this phase closed.  I1 legitimately supersedes them, so
# they are now made over the bundle with the I1 layer removed -- the same
# phase-aware repair the E1/F2/H2/H2.1/H3 layers already use.  The normaliser
# is all-or-nothing: it refuses any tree in which the runtime, the shell and
# the worker did not move together, or in which the runtime bytes are not the
# pinned I1 release, and it hides nothing beyond its own pinned strings.
#
# Imported by path, with no dependency on any other import in this module.
# ---------------------------------------------------------------------------
import os.path as _i1_os_path
import sys as _i1_sys

_I1_DIR = _i1_os_path.dirname(_i1_os_path.abspath(__file__))
if _I1_DIR not in _i1_sys.path:
    _i1_sys.path.insert(0, _I1_DIR)

import priority7_phase4fi1_normalizer as I1


def i1_bundle(root=ROOT):
    """The validated Phase 4F-I1 transition for this tree, or its absence."""
    root = Path(root)
    runtime = root / I1.PHASE_4FI1_RUNTIME_PATH
    return I1.bundle(
        index_text=(root / "index.html").read_text(encoding="utf-8"),
        worker_text=(root / "sw.js").read_text(encoding="utf-8"),
        runtime_bytes=runtime.read_bytes() if runtime.is_file() else None)


def pre_i1(path, root=ROOT):
    """``path`` as it stood before Phase 4F-I1 activated the release."""
    return i1_bundle(root).without_activation(path)


def i1_shipping_text(path, root=ROOT):
    """``path``'s text with the Phase 4F-I1 release layer removed.

    Ordinary text for every path I1 did not edit, so a loop over shipping
    sentinels can use it unconditionally.  It composes with the older layer
    helpers: the shell carries the I1 layer on top of the H3 wording layer, so
    a caller strips I1 here and H3 afterwards, exactly as the corpus claims
    strip H2.1 then H2 then F2 then E1.
    """
    if path in I1.PHASE_4FI1_SHIPPING_PATHS:
        return pre_i1(path, root)
    return (Path(root) / path).read_text(encoding="utf-8")
FIXTURE = ROOT / "tests" / "fixtures" / "priority7" / "synthetic-release-editorial.json"
CORPUS = ROOT / "editorial" / "verb-pattern-candidates.json"
CONTEXT_FILE = ROOT / "editorial" / "priority-7-authoring-context.json"
PUBLIC_RUNTIME = ROOT / "content" / "verb-patterns.json"

PRIORITY7_ACTOR_IDS = frozenset({
    "priority7-reference-analysis", "priority7-editorial-review",
    "priority7-editorial-corroboration", "priority7-example-generation",
})


def priority7_corpus(document):
    """Exact released Priority 7 identity slice, independent of ordering."""
    released = json.loads(PUBLIC_RUNTIME.read_text(encoding="utf-8"))
    expected_lemmas = {lemma["id"] for lemma in released["lemmas"]}
    expected_meanings = {
        meaning["id"] for lemma in released["lemmas"]
        for meaning in lemma["meanings"]}
    expected_patterns = {
        pattern["id"] for lemma in released["lemmas"]
        for meaning in lemma["meanings"] for pattern in meaning["patterns"]}
    lemmas = [lemma for lemma in document["lemmas"]
              if lemma.get("id") in expected_lemmas]
    meanings = [meaning for lemma in lemmas for meaning in lemma["meanings"]]
    patterns = [pattern for meaning in meanings for pattern in meaning["patterns"]]
    observed = ([lemma["id"] for lemma in lemmas],
                [meaning["id"] for meaning in meanings],
                [pattern["id"] for pattern in patterns])
    expected = (expected_lemmas, expected_meanings, expected_patterns)
    if any(len(ids) != len(wanted) or set(ids) != wanted
           for ids, wanted in zip(observed, expected)):
        raise AssertionError("historical Priority 7 identity set changed")
    return {**document, "lemmas": lemmas}


def priority7_actors(registry):
    return {key: value for key, value in registry.items()
            if key in PRIORITY7_ACTOR_IDS}

REVIEWED_AT = "2026-08-08"
LATER = "2026-08-09"

OWNER = "test-reviewer-owner-001"
REFERENCE_ACTOR = "test-actor-reference-analysis-001"
EDITORIAL_ACTOR = "test-actor-editorial-001"
CORROBORATING_ACTOR = "test-actor-editorial-002"
NATIVE_REVIEWER = "test-reviewer-native-001"
EXTERNAL_REVIEWER = "test-reviewer-external-001"
PRODUCT_REVIEWER = "test-reviewer-product-001"

# Every mode value the schema does not recognise, including absence.  Each one
# must resolve to the strictest chain rather than to a permissive reading.
MALFORMED_MODES = (
    None, True, 1, 1.5, [], {}, [SOLO_MAINTAINER_MODE],
    {"mode": SOLO_MAINTAINER_MODE}, "", "solo", "trust-me",
)

def i1_is_generated_output(path):
    """True for the generator-owned outputs Phase 4F-I1 regenerated.

    I1 advances APP_VERSION, which the page generator stamps into every
    generated footer, so ``build_pages.py`` rewrites the 31 pages and the
    sitemap.  They are regenerated, never hand-edited, and each is admitted
    only by its own pinned delta -- one footer version stamp per page, and
    ``<lastmod>`` values alone in the sitemap.
    """
    return (path in I1.PHASE_4FI1_GENERATED_PAGES
            or path == I1.PHASE_4FI1_SITEMAP_PATH)


def payload():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def context(**overrides):
    data = payload()
    identities = data["syntheticIdentities"]
    keywords = {
        "source_registry": identities["sourceRegistry"],
        "reviewer_registry": identities["reviewerRegistry"],
        "author_registry": identities["authorRegistry"],
        "editorial_actor_registry": identities["editorialActorRegistry"],
        "repository_index": RepositoryIndex.from_sources(
            data["syntheticRepositorySources"]),
        "today": date.fromisoformat(data["reviewContextDate"]),
    }
    keywords.update(overrides)
    return ValidationContext(**keywords)


def actor_registry():
    return copy.deepcopy(payload()["syntheticIdentities"]["editorialActorRegistry"])


def reviewer_registry():
    return copy.deepcopy(payload()["syntheticIdentities"]["reviewerRegistry"])


def approved_patterns(document):
    for lemma in document["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                if pattern.get("reviewState") == "approved":
                    yield lemma, meaning, pattern


def contemporary_pins(pattern):
    return sorted({
        evidence_digest(record) for record in pattern["evidence"]
        if record["sourceKind"] in {
            "contemporary-reference", "contemporary-corpus"}
    })


def reference_verification(lemma, meaning, pattern, reviewed_at=REVIEWED_AT,
                           actor=REFERENCE_ACTOR):
    """The amended tier-1 event: a nonhuman workflow, source-backed."""
    return {
        "kind": "reference-verification",
        "decision": "accept",
        "scopeVersion": 1,
        "scopeDigest": review_scope_digest(
            "reference-verification", lemma, meaning, pattern),
        "supportingEvidenceDigests": contemporary_pins(pattern),
        "actorRef": actor,
        "reviewedAt": reviewed_at,
    }


def editorial_review(lemma, meaning, pattern, reviewed_at=REVIEWED_AT,
                     actor=EDITORIAL_ACTOR, corroborating=(CORROBORATING_ACTOR,)):
    return {
        "kind": "editorial-review",
        "decision": "accept",
        "scopeVersion": 1,
        "scopeDigest": review_scope_digest(
            "editorial-review", lemma, meaning, pattern),
        "actorRef": actor,
        "corroboratingActorRefs": sorted(corroborating),
        "reviewedAt": reviewed_at,
    }


def owner_approval(lemma, meaning, pattern, reviewed_at=REVIEWED_AT,
                   reviewer=OWNER):
    return {
        "kind": "product-approval",
        "decision": "accept",
        "scopeVersion": 1,
        "scopeDigest": review_scope_digest(
            "product-approval", lemma, meaning, pattern),
        "reviewerRef": reviewer,
        "reviewedAt": reviewed_at,
    }


def solo_chain(lemma, meaning, pattern, reviewed_at=REVIEWED_AT):
    return [
        reference_verification(lemma, meaning, pattern, reviewed_at),
        editorial_review(lemma, meaning, pattern, reviewed_at),
        owner_approval(lemma, meaning, pattern, reviewed_at),
    ]


def human_chain(lemma, meaning, pattern, reviewed_at=REVIEWED_AT):
    return [
        {
            "kind": "external-verification",
            "decision": "accept",
            "scopeVersion": 1,
            "scopeDigest": review_scope_digest(
                "external-verification", lemma, meaning, pattern),
            "supportingEvidenceDigests": contemporary_pins(pattern),
            "reviewerRef": EXTERNAL_REVIEWER,
            "reviewedAt": reviewed_at,
        },
        {
            "kind": "native-linguistic",
            "decision": "accept",
            "scopeVersion": 1,
            "scopeDigest": review_scope_digest(
                "native-linguistic", lemma, meaning, pattern),
            "reviewerRef": NATIVE_REVIEWER,
            "reviewedAt": reviewed_at,
        },
        {
            "kind": "product-approval",
            "decision": "accept",
            "scopeVersion": 1,
            "scopeDigest": review_scope_digest(
                "product-approval", lemma, meaning, pattern),
            "reviewerRef": PRODUCT_REVIEWER,
            "reviewedAt": reviewed_at,
        },
    ]


def solo_document():
    """The synthetic release under the amended solo-maintainer chain."""
    document = payload()["editorial"]
    for lemma, meaning, pattern in approved_patterns(document):
        pattern["releaseMode"] = SOLO_MAINTAINER_MODE
        for example in pattern.get("examples", []):
            if example["origin"]["kind"] == "original":
                example["origin"] = {
                    "kind": "editorial-generated",
                    "generatorRef": EDITORIAL_ACTOR,
                    "adoptedAt": REVIEWED_AT,
                }
        pattern["reviewEvents"] = solo_chain(lemma, meaning, pattern)
    return document


def human_document():
    """The same release under the untouched fully human-reviewed chain."""
    document = payload()["editorial"]
    for lemma, meaning, pattern in approved_patterns(document):
        pattern["reviewEvents"] = human_chain(lemma, meaning, pattern)
    return document


class Phase4E1TestCase(unittest.TestCase):
    maxDiff = None

    def codes(self, document, validation_context=None):
        return {issue.code for issue in validate_editorial(
            document, validation_context or context())}

    def assertClean(self, document, validation_context=None):
        issues = validate_editorial(document, validation_context or context())
        self.assertEqual([], issues, f"unexpected issues: {issues}")

    def assertRefused(self, code, document, validation_context=None):
        codes = self.codes(document, validation_context)
        self.assertIn(code, codes, f"expected {code}, saw {sorted(codes)}")

    def first_solo(self, document):
        """The one approved pattern carrying examples and error notes."""
        for lemma, meaning, pattern in approved_patterns(document):
            if pattern.get("examples"):
                return lemma, meaning, pattern
        raise AssertionError("fixture must expose an approved pattern")

    def solo_frozen(self, document=None, revision=1):
        return freeze_editorial(document or solo_document(), revision, context())


# --------------------------------------------------------------------------
# §1/§2  the actor contract is chosen from the mode, not from the stage name
# --------------------------------------------------------------------------

class ModeSensitiveActorContract(Phase4E1TestCase):

    def test_a_solo_reference_verification_by_a_nonhuman_actor_is_valid(self):
        """The control: the amendment's whole point, end to end.

        Nothing about this release names a human reference verifier, and it is
        nonetheless a complete, valid, freezable solo-maintainer release.
        """
        self.assertClean(solo_document())

    def test_a_solo_reference_verification_cannot_name_a_human_reviewer(self):
        """The mismatch Phase 4E.1 exists to remove, asserted directly."""
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        event = pattern["reviewEvents"][0]
        event.pop("actorRef")
        event["reviewerRef"] = OWNER
        codes = self.codes(document)
        self.assertIn("SCHEMA_REQUIRED", codes)
        self.assertIn("SCHEMA_UNKNOWN_FIELD", codes)

    def test_a_solo_reference_verification_cannot_carry_both_references(self):
        """Carrying both is the laundering shape, so the schema closes it."""
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["reviewEvents"][0]["reviewerRef"] = OWNER
        self.assertRefused("SCHEMA_UNKNOWN_FIELD", document)

    def test_the_human_chain_refuses_a_reference_verification_outright(self):
        """Not merely non-advancing: the human chain has no such stage.

        Leaving it representable would make a human-reviewed history ambiguous
        about whether a person had verified the claim, which is exactly the
        confusion this amendment removes.
        """
        document = human_document()
        lemma, meaning, pattern = self.first_solo(document)
        pattern["reviewEvents"].insert(
            0, reference_verification(lemma, meaning, pattern))
        self.assertRefused("REVIEW_STAGE_NOT_IN_MODE", document)

    def test_the_human_chain_refuses_it_however_it_is_referenced(self):
        for label, mutate in (
                ("actorRef", lambda event: event),
                ("reviewerRef", lambda event: {
                    key: value for key, value in event.items()
                    if key != "actorRef"} | {"reviewerRef": OWNER})):
            with self.subTest(reference=label):
                document = human_document()
                lemma, meaning, pattern = self.first_solo(document)
                pattern["reviewEvents"].insert(0, mutate(
                    reference_verification(lemma, meaning, pattern)))
                self.assertRefused("REVIEW_STAGE_NOT_IN_MODE", document)

    def test_the_declared_mode_decides_the_contract_for_every_stage(self):
        """The full mode/stage contract matrix, asserted in one place."""
        expected = {
            (HUMAN_REVIEWED_MODE, "external-verification"): "reviewerRef",
            (HUMAN_REVIEWED_MODE, "native-linguistic"): "reviewerRef",
            (HUMAN_REVIEWED_MODE, "product-approval"): "reviewerRef",
            (HUMAN_REVIEWED_MODE, "editorial-review"): "actorRef",
            (SOLO_MAINTAINER_MODE, "reference-verification"): "actorRef",
            (SOLO_MAINTAINER_MODE, "editorial-review"): "actorRef",
            (SOLO_MAINTAINER_MODE, "product-approval"): "reviewerRef",
            (SOLO_MAINTAINER_MODE, "external-verification"): "reviewerRef",
            (SOLO_MAINTAINER_MODE, "native-linguistic"): "reviewerRef",
        }
        for (mode, kind), reference in expected.items():
            with self.subTest(mode=mode, kind=kind):
                nonhuman = kind in T.nonhuman_stage_kinds(mode)
                self.assertEqual(reference == "actorRef", nonhuman)
        self.assertEqual(
            frozenset({"reference-verification"}),
            T.forbidden_stage_kinds(HUMAN_REVIEWED_MODE))
        self.assertEqual(
            frozenset(), T.forbidden_stage_kinds(SOLO_MAINTAINER_MODE))

    def test_the_solo_chain_still_reaches_approved_by_its_own_state_names(self):
        """Each rung is reachable, and every rung is named for what it is.

        Learner activities and audio require approval, so an unapproved rung
        surrenders them -- and both sit inside the editorial-review scope, so
        the chain is stamped against that reduced content rather than bolted
        onto a chain that reviewed something else.
        """
        for count, expected in (
                (0, "research"), (1, "reference-verified"),
                (2, "editorial-reviewed"), (3, "approved")):
            with self.subTest(events=count):
                document = solo_document()
                lemma, meaning, pattern = self.first_solo(document)
                if expected != "approved":
                    pattern["activityEligibility"] = []
                    for example in pattern["examples"]:
                        example["audioEligible"] = False
                pattern["reviewEvents"] = solo_chain(
                    lemma, meaning, pattern)[:count]
                pattern["reviewState"] = expected
                self.assertNotIn("REVIEW_STATE_MISMATCH", self.codes(document))

    def test_the_locked_stage_order_still_binds_the_actor_borne_tiers(self):
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["reviewEvents"] = pattern["reviewEvents"][1:]
        self.assertRefused("REVIEW_STAGE_ORDER", document)


# --------------------------------------------------------------------------
# §1  the reference actor is a registered nonhuman workflow, never a person
# --------------------------------------------------------------------------

class ReferenceActorIdentity(Phase4E1TestCase):

    def test_an_unregistered_reference_actor_is_refused(self):
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["reviewEvents"][0]["actorRef"] = "test-actor-nobody"
        self.assertRefused("EDITORIAL_ACTOR_REGISTRY_DANGLING", document)

    def test_a_reference_actor_declaring_itself_human_is_refused(self):
        document = solo_document()
        actors = actor_registry()
        actors[REFERENCE_ACTOR]["human"] = True
        self.assertRefused(
            "EDITORIAL_ACTOR_NOT_NONHUMAN", document,
            context(editorial_actor_registry=actors))

    def test_a_reference_actor_must_state_human_false_explicitly(self):
        """Omitting the field is not the same as declaring nonhumanity."""
        document = solo_document()
        actors = actor_registry()
        actors[REFERENCE_ACTOR].pop("human")
        self.assertRefused(
            "EDITORIAL_ACTOR_NOT_NONHUMAN", document,
            context(editorial_actor_registry=actors))

    def test_a_reference_actor_needs_the_reference_verification_role(self):
        document = solo_document()
        actors = actor_registry()
        actors[REFERENCE_ACTOR]["roles"] = ["editorial-review"]
        self.assertRefused(
            "EDITORIAL_ACTOR_ROLE", document,
            context(editorial_actor_registry=actors))

    def test_an_editorial_only_actor_cannot_perform_reference_verification(self):
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["reviewEvents"][0]["actorRef"] = CORROBORATING_ACTOR
        self.assertRefused("EDITORIAL_ACTOR_ROLE", document)

    def test_an_actor_may_hold_only_the_defined_workflow_roles(self):
        """A borrowed human role is how a model starts describing itself as one."""
        for role in ("native-linguistic", "external-verification",
                     "product-approval", "reviewer", ""):
            with self.subTest(role=role):
                document = solo_document()
                actors = actor_registry()
                actors[REFERENCE_ACTOR]["roles"] = [
                    "reference-verification", role]
                self.assertRefused(
                    "EDITORIAL_ACTOR_ROLE_UNKNOWN", document,
                    context(editorial_actor_registry=actors))

    def test_the_defined_actor_role_vocabulary_is_exactly_these_three(self):
        self.assertEqual(
            {"reference-verification", "editorial-review", "example-generation"},
            set(EDITORIAL_ACTOR_ROLES))

    def test_a_reference_actor_cannot_be_used_as_a_human_external_verifier(self):
        document = human_document()
        _, _, pattern = self.first_solo(document)
        pattern["reviewEvents"][0]["reviewerRef"] = REFERENCE_ACTOR
        self.assertRefused("REVIEWER_REGISTRY_DANGLING", document)

    def test_a_reference_actor_cannot_be_used_as_a_native_reviewer(self):
        document = human_document()
        _, _, pattern = self.first_solo(document)
        pattern["reviewEvents"][1]["reviewerRef"] = REFERENCE_ACTOR
        self.assertRefused("REVIEWER_REGISTRY_DANGLING", document)

    def test_a_reference_actor_cannot_generate_examples_without_that_role(self):
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["examples"][0]["origin"]["generatorRef"] = REFERENCE_ACTOR
        self.assertRefused("EDITORIAL_ACTOR_ROLE", document)

    def test_one_identity_key_cannot_be_both_reviewer_and_reference_actor(self):
        reviewers = reviewer_registry()
        reviewers[REFERENCE_ACTOR] = {
            "human": True, "roles": ["external-verification"]}
        self.assertRefused(
            "REGISTRY_KEY_COLLISION", solo_document(),
            context(reviewer_registry=reviewers))

    def test_a_human_native_reviewer_cannot_be_reused_as_a_reference_actor(self):
        """The AB shape: a real human native reviewer, borrowed as a workflow.

        Registering the same identity in both places is refused outright, and
        registering the human record itself in the actor registry is refused
        for being human and for holding a role no actor may hold.
        """
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["reviewEvents"][0]["actorRef"] = NATIVE_REVIEWER
        self.assertRefused("EDITORIAL_ACTOR_REGISTRY_DANGLING", document)

        actors = actor_registry()
        actors[NATIVE_REVIEWER] = {
            "human": True, "roles": ["native-linguistic"]}
        codes = self.codes(
            document, context(editorial_actor_registry=actors))
        self.assertIn("REGISTRY_KEY_COLLISION", codes)

    def test_the_product_owner_cannot_act_as_a_reference_actor(self):
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["reviewEvents"][0]["actorRef"] = OWNER
        self.assertRefused("EDITORIAL_ACTOR_REGISTRY_DANGLING", document)

    def test_the_owner_cannot_be_relisted_as_a_nonhuman_reference_actor(self):
        """The direct attempt: declare the human owner to be a workflow."""
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["reviewEvents"][0]["actorRef"] = OWNER
        actors = actor_registry()
        actors[OWNER] = {"human": False, "roles": ["reference-verification"]}
        self.assertRefused(
            "REGISTRY_KEY_COLLISION", document,
            context(editorial_actor_registry=actors))


# --------------------------------------------------------------------------
# §3  the actor records that the workflow ran; the sources do the verifying
# --------------------------------------------------------------------------

class SourceAuthorityNotModelAuthority(Phase4E1TestCase):

    def test_a_reference_acceptance_without_pinned_evidence_is_refused(self):
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["reviewEvents"][0].pop("supportingEvidenceDigests")
        self.assertRefused("REVIEW_EVIDENCE_REQUIRED", document)

    def test_a_reference_acceptance_pinning_nothing_current_is_refused(self):
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["reviewEvents"][0]["supportingEvidenceDigests"] = [
            "sha256:" + "0" * 64]
        self.assertRefused("REVIEW_STATE_MISMATCH", document)

    def test_lemma_only_evidence_verifies_no_pattern(self):
        """Headword presence is not a statement about a complement frame."""
        document = solo_document()
        lemma, meaning, pattern = self.first_solo(document)
        pattern["evidence"] = [
            record for record in pattern["evidence"]
            if record["factType"] != "complement-frame"]
        pattern["errorNotes"] = []
        pattern["reviewEvents"] = solo_chain(lemma, meaning, pattern)
        codes = self.codes(document)
        self.assertIn("REFERENCE_PATTERN_EVIDENCE_REQUIRED", codes)
        self.assertIn("REVIEW_STATE_MISMATCH", codes)

    def test_medak_headword_only_evidence_is_refused(self):
        document = solo_document()
        lemma, meaning, pattern = self.first_solo(document)
        pattern["evidence"] = [{
            "sourceId": "test-source-headword-001",
            "sourceKind": "medak-research",
            "locator": "fixture://phase4e1/synthetic/headword",
            "factType": "lemma",
            "checkedAt": REVIEWED_AT,
        }]
        pattern["errorNotes"] = []
        pattern["reviewEvents"] = solo_chain(lemma, meaning, pattern)
        pattern["reviewEvents"][0]["supportingEvidenceDigests"] = [
            evidence_digest(pattern["evidence"][0])]
        sources = copy.deepcopy(payload()["syntheticIdentities"]["sourceRegistry"])
        sources["test-source-headword-001"] = {"sourceKind": "medak-research"}
        codes = self.codes(document, context(source_registry=sources))
        self.assertIn("REVIEW_CONTEMPORARY_EVIDENCE_REQUIRED", codes)
        self.assertIn("REVIEW_STATE_MISMATCH", codes)

    def test_stale_evidence_retires_the_reference_verification(self):
        """The actor's signature does not outlive the sources it pinned."""
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["evidence"][0]["locator"] = "fixture://phase4e1/retargeted"
        self.assertRefused("REVIEW_STATE_MISMATCH", document)

    def test_an_edit_after_verification_retires_it(self):
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["learnerExplanationEn"] = (
            "TEST-ONLY invented copy rewritten after reference verification.")
        self.assertRefused("REVIEW_STATE_MISMATCH", document)

    def test_the_actor_alone_never_makes_a_pattern_verified(self):
        """A perfectly registered actor plus no qualifying evidence is research."""
        document = solo_document()
        lemma, meaning, pattern = self.first_solo(document)
        pattern["evidence"] = [
            record for record in pattern["evidence"]
            if record["factType"] != "complement-frame"]
        pattern["errorNotes"] = []
        pattern["reviewEvents"] = solo_chain(lemma, meaning, pattern)
        pattern["reviewState"] = "research"
        pattern["activityEligibility"] = []
        for example in pattern["examples"]:
            example["audioEligible"] = False
        self.assertNotIn("REVIEW_STATE_MISMATCH", self.codes(document))

    def test_a_reference_event_cannot_borrow_the_editorial_corroboration(self):
        """Its corroboration is the cited sources, not a second opinion."""
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["reviewEvents"][0]["corroboratingActorRefs"] = [
            CORROBORATING_ACTOR]
        self.assertRefused("SCHEMA_UNKNOWN_FIELD", document)


# --------------------------------------------------------------------------
# §4  the two nonhuman tiers must be independent identities
# --------------------------------------------------------------------------

class ReferenceAndEditorialIndependence(Phase4E1TestCase):

    def test_one_actor_cannot_perform_both_nonhuman_tiers(self):
        document = solo_document()
        actors = actor_registry()
        actors[REFERENCE_ACTOR]["roles"] = [
            "editorial-review", "reference-verification"]
        for lemma, meaning, pattern in approved_patterns(document):
            pattern["reviewEvents"][1] = editorial_review(
                lemma, meaning, pattern, actor=REFERENCE_ACTOR)
        self.assertRefused(
            "REVIEW_ACTOR_INDEPENDENCE", document,
            context(editorial_actor_registry=actors))

    def test_the_reference_actor_cannot_reappear_as_a_corroborator(self):
        """Corroboration by the actor that made the claim corroborates nothing."""
        document = solo_document()
        actors = actor_registry()
        actors[REFERENCE_ACTOR]["roles"] = [
            "editorial-review", "reference-verification"]
        for lemma, meaning, pattern in approved_patterns(document):
            pattern["reviewEvents"][1] = editorial_review(
                lemma, meaning, pattern,
                corroborating=(CORROBORATING_ACTOR, REFERENCE_ACTOR))
        self.assertRefused(
            "REVIEW_ACTOR_INDEPENDENCE", document,
            context(editorial_actor_registry=actors))

    def test_independence_holds_across_rounds_not_just_within_one(self):
        """A later round may not quietly swap the two identities over."""
        document = solo_document()
        actors = actor_registry()
        actors[REFERENCE_ACTOR]["roles"] = [
            "editorial-review", "reference-verification"]
        actors[EDITORIAL_ACTOR]["roles"] = [
            "editorial-review", "example-generation", "reference-verification"]
        for lemma, meaning, pattern in approved_patterns(document):
            second = solo_chain(lemma, meaning, pattern, LATER)
            second[0]["actorRef"] = EDITORIAL_ACTOR
            second[1] = editorial_review(
                lemma, meaning, pattern, LATER, actor=REFERENCE_ACTOR)
            pattern["reviewEvents"] = pattern["reviewEvents"] + second
        self.assertRefused(
            "REVIEW_ACTOR_INDEPENDENCE", document,
            context(editorial_actor_registry=actors))

    def test_the_editorial_tier_still_requires_its_own_corroboration(self):
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["reviewEvents"][1].pop("corroboratingActorRefs")
        self.assertRefused("EDITORIAL_CORROBORATION_REQUIRED", document)

    def test_an_editorial_actor_still_cannot_corroborate_itself(self):
        document = solo_document()
        for lemma, meaning, pattern in approved_patterns(document):
            pattern["reviewEvents"][1] = editorial_review(
                lemma, meaning, pattern, corroborating=(EDITORIAL_ACTOR,))
        self.assertRefused("EDITORIAL_CORROBORATION_SELF", document)

    def test_three_distinct_identities_is_the_valid_shape(self):
        """The positive control for the independence rule."""
        document = solo_document()
        actors = set()
        for _, _, pattern in approved_patterns(document):
            actors.add(pattern["reviewEvents"][0]["actorRef"])
            actors.add(pattern["reviewEvents"][1]["actorRef"])
            actors.update(pattern["reviewEvents"][1]["corroboratingActorRefs"])
        self.assertEqual(
            {REFERENCE_ACTOR, EDITORIAL_ACTOR, CORROBORATING_ACTOR}, actors)
        self.assertClean(document)


# --------------------------------------------------------------------------
# §5  no release may depend on a commercial model or vendor name
# --------------------------------------------------------------------------

class VendorIndependence(Phase4E1TestCase):

    VENDOR_TOKENS = (
        "Claude", "Opus", "Sonnet", "Anthropic", "GPT", "OpenAI", "Codex",
        "Gemini", "Llama", "Mistral",
    )

    def test_no_vendor_or_model_name_appears_in_the_governance_tooling(self):
        source = (ROOT / "priority7_tooling.py").read_text(encoding="utf-8")
        for token in self.VENDOR_TOKENS:
            with self.subTest(token=token):
                self.assertNotIn(token, source)

    def test_stable_actor_identity_is_a_workflow_role_not_a_product(self):
        registry = payload()["syntheticIdentities"]["editorialActorRegistry"]
        for reference, record in registry.items():
            with self.subTest(actor=reference):
                blob = json.dumps(
                    {"id": reference, "roles": record["roles"]},
                    ensure_ascii=False)
                for token in self.VENDOR_TOKENS:
                    self.assertNotIn(token, blob)

    def test_private_audit_metadata_is_never_load_bearing(self):
        """Run and model notes may be kept; nothing may depend on them."""
        baseline = self.solo_frozen()
        for label, mutate in (
                ("absent", lambda record: record.pop("auditMetadata", None)),
                ("rewritten", lambda record: record.__setitem__(
                    "auditMetadata", {"runNote": "TEST-ONLY different note."})),
                ("vendor named", lambda record: record.__setitem__(
                    "auditMetadata", {"runNote": "TEST-ONLY vendor note."}))):
            with self.subTest(metadata=label):
                actors = actor_registry()
                mutate(actors[REFERENCE_ACTOR])
                validation_context = context(editorial_actor_registry=actors)
                self.assertClean(solo_document(), validation_context)
                self.assertEqual(
                    baseline,
                    freeze_editorial(solo_document(), 1, validation_context))

    def test_the_actor_kind_field_is_descriptive_not_a_gate(self):
        for kind in ("language-model", "source-analysis-workflow", "anything"):
            with self.subTest(kind=kind):
                actors = actor_registry()
                actors[REFERENCE_ACTOR]["kind"] = kind
                self.assertClean(
                    solo_document(), context(editorial_actor_registry=actors))

    def test_no_actor_metadata_reaches_the_frozen_release(self):
        blob = json.dumps(self.solo_frozen(), ensure_ascii=False)
        self.assertNotIn("auditMetadata", blob)
        self.assertNotIn("source-analysis-workflow", blob)


# --------------------------------------------------------------------------
# §6  product approval remains human, mandatory and mode-acknowledged
# --------------------------------------------------------------------------

class ProductApprovalRemainsHuman(Phase4E1TestCase):

    def test_a_release_without_owner_approval_is_not_approved(self):
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["reviewEvents"] = pattern["reviewEvents"][:2]
        self.assertRefused("REVIEW_STATE_MISMATCH", document)

    def test_product_approval_cannot_be_performed_by_an_actor(self):
        for actor in (REFERENCE_ACTOR, EDITORIAL_ACTOR):
            with self.subTest(actor=actor):
                document = solo_document()
                _, _, pattern = self.first_solo(document)
                event = pattern["reviewEvents"][2]
                event.pop("reviewerRef")
                event["actorRef"] = actor
                codes = self.codes(document)
                self.assertIn("SCHEMA_REQUIRED", codes)
                self.assertIn("SCHEMA_UNKNOWN_FIELD", codes)

    def test_a_nonhuman_product_approver_is_refused(self):
        reviewers = reviewer_registry()
        reviewers[OWNER]["human"] = False
        self.assertRefused(
            "REVIEWER_NOT_HUMAN", solo_document(),
            context(reviewer_registry=reviewers))

    def test_the_owner_must_still_acknowledge_the_solo_release_mode(self):
        reviewers = reviewer_registry()
        reviewers[OWNER].pop("acknowledgedReleaseModes")
        self.assertRefused(
            "OWNER_RELEASE_MODE_NOT_ACKNOWLEDGED", solo_document(),
            context(reviewer_registry=reviewers))

    def test_the_owner_holds_no_reference_verification_authority(self):
        """The amendment's honesty claim about the owner, asserted directly."""
        reviewers = payload()["syntheticIdentities"]["reviewerRegistry"]
        self.assertNotIn("reference-verification", reviewers[OWNER]["roles"])
        self.assertNotIn("external-verification", reviewers[OWNER]["roles"])
        self.assertNotIn("native-linguistic", reviewers[OWNER]["roles"])
        self.assertEqual(
            ["product-approval", "correction", "reopen"],
            reviewers[OWNER]["roles"])


# --------------------------------------------------------------------------
# §7  optional human native review is preserved exactly as Phase 4E left it
# --------------------------------------------------------------------------

class OptionalHumanNativeReview(Phase4E1TestCase):

    def solo_with_native_review(self):
        document = solo_document()
        for lemma, meaning, pattern in approved_patterns(document):
            pattern["reviewEvents"] = [
                reference_verification(lemma, meaning, pattern),
                editorial_review(lemma, meaning, pattern),
                {
                    "kind": "native-linguistic",
                    "decision": "accept",
                    "scopeVersion": 1,
                    "scopeDigest": review_scope_digest(
                        "native-linguistic", lemma, meaning, pattern),
                    "reviewerRef": NATIVE_REVIEWER,
                    "reviewedAt": REVIEWED_AT,
                },
                owner_approval(lemma, meaning, pattern),
            ]
        return document

    def test_genuine_native_review_still_strengthens_a_solo_release(self):
        document = self.solo_with_native_review()
        self.assertClean(document)
        authorization = freeze_editorial(
            document, 1, context())["releaseAuthorization"]
        self.assertEqual([SOLO_MAINTAINER_MODE], authorization["releaseModes"])
        self.assertTrue(authorization["humanNativeReviewedPatternIds"])
        self.assertEqual([], authorization["humanVerifiedPatternIds"])

    def test_a_native_rejection_still_vetoes_a_solo_release(self):
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["reviewEvents"].append({
            "kind": "native-linguistic",
            "decision": "reject",
            "reviewerRef": NATIVE_REVIEWER,
            "reviewedAt": LATER,
            "note": "TEST-ONLY invented native objection to the treatment.",
        })
        self.assertRefused("REVIEW_STATE_MISMATCH", document)

    def test_a_native_change_request_still_drops_the_editorial_tier(self):
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["reviewEvents"].append({
            "kind": "native-linguistic",
            "decision": "changes-requested",
            "reviewerRef": NATIVE_REVIEWER,
            "reviewedAt": LATER,
            "note": "TEST-ONLY invented native wording objection.",
        })
        pattern["reviewState"] = "reference-verified"
        pattern["activityEligibility"] = []
        for example in pattern["examples"]:
            example["audioEligible"] = False
        self.assertClean(document)


# --------------------------------------------------------------------------
# §8  the closed schema refuses every cross-field substitution
# --------------------------------------------------------------------------

class ClosedReviewEventSchema(Phase4E1TestCase):

    def substitutions(self):
        """(label, mode, builder, index) for every stage of both chains."""
        return (
            ("solo reference-verification", solo_document, 0),
            ("solo editorial-review", solo_document, 1),
            ("solo product-approval", solo_document, 2),
            ("human external-verification", human_document, 0),
            ("human native-linguistic", human_document, 1),
            ("human product-approval", human_document, 2),
        )

    def test_every_stage_refuses_the_opposite_reference_field(self):
        for label, build, index in self.substitutions():
            with self.subTest(stage=label):
                document = build()
                _, _, pattern = self.first_solo(document)
                event = pattern["reviewEvents"][index]
                if "actorRef" in event:
                    event.pop("actorRef")
                    event["reviewerRef"] = OWNER
                else:
                    event.pop("reviewerRef")
                    event["actorRef"] = EDITORIAL_ACTOR
                codes = self.codes(document)
                self.assertIn("SCHEMA_REQUIRED", codes)
                self.assertIn("SCHEMA_UNKNOWN_FIELD", codes)

    def test_no_stage_may_carry_both_reference_fields(self):
        for label, build, index in self.substitutions():
            with self.subTest(stage=label):
                document = build()
                _, _, pattern = self.first_solo(document)
                event = pattern["reviewEvents"][index]
                event["reviewerRef" if "actorRef" in event else "actorRef"] = (
                    OWNER if "actorRef" in event else EDITORIAL_ACTOR)
                self.assertRefused("SCHEMA_UNKNOWN_FIELD", document)

    def test_findings_remain_an_editorial_review_field_only(self):
        for index in (0, 2):
            with self.subTest(event=index):
                document = solo_document()
                _, _, pattern = self.first_solo(document)
                pattern["reviewEvents"][index]["findings"] = [{
                    "severity": "low",
                    "summary": "TEST-ONLY invented finding.",
                    "resolved": False}]
                self.assertRefused("SCHEMA_UNKNOWN_FIELD", document)


# --------------------------------------------------------------------------
# §9  duplicate and out-of-order acceptances at the new actor-borne tier
# --------------------------------------------------------------------------

class DuplicateAndOrderRules(Phase4E1TestCase):

    def test_a_duplicate_reference_acceptance_is_refused(self):
        document = solo_document()
        for _, _, pattern in approved_patterns(document):
            pattern["reviewEvents"].insert(
                1, copy.deepcopy(pattern["reviewEvents"][0]))
        self.assertRefused("REVIEW_DUPLICATE_STAGE_ACCEPTANCE", document)
        with self.assertRaises(ValidationFailure) as caught:
            freeze_editorial(document, 1, context())
        self.assertIn(
            "REVIEW_DUPLICATE_STAGE_ACCEPTANCE",
            {issue.code for issue in caught.exception.issues})

    def test_a_duplicate_with_a_different_actor_is_still_a_duplicate(self):
        """Re-running the workflow under a second identity proves nothing new."""
        document = solo_document()
        actors = actor_registry()
        actors["test-actor-reference-analysis-002"] = {
            "human": False,
            "roles": ["reference-verification"],
        }
        for lemma, meaning, pattern in approved_patterns(document):
            pattern["reviewEvents"].insert(1, reference_verification(
                lemma, meaning, pattern,
                actor="test-actor-reference-analysis-002"))
        self.assertRefused(
            "REVIEW_DUPLICATE_STAGE_ACCEPTANCE", document,
            context(editorial_actor_registry=actors))

    def test_an_out_of_order_editorial_review_is_refused(self):
        document = solo_document()
        for _, _, pattern in approved_patterns(document):
            events = pattern["reviewEvents"]
            pattern["reviewEvents"] = [events[1], events[0], events[2]]
        self.assertRefused("REVIEW_STAGE_ORDER", document)

    def test_a_change_request_permits_a_fresh_reference_verification(self):
        document = solo_document()
        for lemma, meaning, pattern in approved_patterns(document):
            pattern["reviewEvents"] = [
                reference_verification(lemma, meaning, pattern),
                {
                    "kind": "reference-verification",
                    "decision": "changes-requested",
                    "actorRef": REFERENCE_ACTOR,
                    "reviewedAt": REVIEWED_AT,
                    "note": "TEST-ONLY invented request for changes.",
                },
            ] + solo_chain(lemma, meaning, pattern, LATER)
        self.assertClean(document)

    def test_an_owner_correction_permits_a_fresh_round(self):
        document = solo_document()
        for lemma, meaning, pattern in approved_patterns(document):
            pattern["reviewEvents"] = pattern["reviewEvents"] + [{
                "kind": "correction",
                "decision": "accept",
                "reviewerRef": OWNER,
                "reviewedAt": LATER,
                "note": "TEST-ONLY owner correction authorising re-review.",
            }] + solo_chain(lemma, meaning, pattern, LATER)
        self.assertClean(document)
        self.assertEqual([], validate_frozen_release(
            freeze_editorial(document, 1, context())))

    def test_a_reopen_after_rejection_still_needs_owner_authority(self):
        document = solo_document()
        for lemma, meaning, pattern in approved_patterns(document):
            pattern["reviewEvents"] = [{
                "kind": "reference-verification",
                "decision": "reject",
                "actorRef": REFERENCE_ACTOR,
                "reviewedAt": REVIEWED_AT,
                "note": "TEST-ONLY invented rejection.",
            }, {
                "kind": "reopen",
                "decision": "accept",
                "reviewerRef": PRODUCT_REVIEWER,
                "reviewedAt": LATER,
                "note": "TEST-ONLY reopen by a non-owner.",
            }] + solo_chain(lemma, meaning, pattern, LATER)
        reviewers = reviewer_registry()
        reviewers[PRODUCT_REVIEWER]["roles"] = ["reopen"]
        self.assertRefused(
            "REVIEW_REJECTED_REOPEN_AUTHORITY", document,
            context(reviewer_registry=reviewers))


# --------------------------------------------------------------------------
# §10/§11  the frozen release keeps the distinction and states it truthfully
# --------------------------------------------------------------------------

class FrozenHistoryKeepsTheDistinction(Phase4E1TestCase):

    def test_the_frozen_history_retains_the_nonhuman_reference_actor(self):
        frozen = self.solo_frozen()
        self.assertEqual([], validate_frozen_release(frozen))
        seen = 0
        for row in frozen["reviewHistory"]:
            for event in row["reviewEvents"]:
                if event["kind"] != "reference-verification":
                    continue
                seen += 1
                self.assertEqual(REFERENCE_ACTOR, event["actorRef"])
                self.assertNotIn("reviewerRef", event)
        self.assertTrue(seen, "the released history must retain the tier")

    def test_a_frozen_actor_reference_cannot_be_swapped_for_a_reviewer(self):
        """The substitution that would make a workflow look like a person."""
        frozen = self.solo_frozen()
        for row in frozen["reviewHistory"]:
            for event in row["reviewEvents"]:
                if event["kind"] == "reference-verification":
                    event.pop("actorRef")
                    event["reviewerRef"] = OWNER
        codes = {issue.code for issue in validate_frozen_release(frozen)}
        self.assertIn("SCHEMA_REQUIRED", codes)
        self.assertIn("SCHEMA_UNKNOWN_FIELD", codes)

    def test_a_frozen_reference_event_cannot_become_a_human_verification(self):
        frozen = self.solo_frozen()
        for row in frozen["reviewHistory"]:
            for event in row["reviewEvents"]:
                if event["kind"] == "reference-verification":
                    event["kind"] = "external-verification"
                    event.pop("actorRef")
                    event["reviewerRef"] = EXTERNAL_REVIEWER
        self.assertIn(
            "FROZEN_REVIEW_STATE_MISMATCH",
            {issue.code for issue in validate_frozen_release(frozen)})

    def test_a_frozen_human_mode_row_cannot_gain_a_reference_event(self):
        frozen = freeze_editorial(human_document(), 1, context())
        self.assertEqual([], validate_frozen_release(frozen))
        for row in frozen["reviewHistory"]:
            if not row["reviewEvents"]:
                continue
            row["reviewEvents"].insert(0, {
                "kind": "reference-verification",
                "decision": "accept",
                "scopeVersion": 1,
                "scopeDigest": row["reviewEvents"][0]["scopeDigest"],
                "supportingEvidenceDigests": row["currentEvidenceDigests"],
                "actorRef": REFERENCE_ACTOR,
                "reviewedAt": REVIEWED_AT,
            })
        self.assertIn(
            "REVIEW_STAGE_NOT_IN_MODE",
            {issue.code for issue in validate_frozen_release(frozen)})

    def test_the_frozen_envelope_enforces_actor_independence_too(self):
        """The rule lives in the replay both readings share, so it travels."""
        control = self.solo_frozen()
        self.assertEqual([], validate_frozen_release(control))

        def as_editorial_actor(event):
            event["actorRef"] = REFERENCE_ACTOR

        def as_corroborator(event):
            event["corroboratingActorRefs"] = sorted(
                set(event["corroboratingActorRefs"]) | {REFERENCE_ACTOR})

        for label, tamper in (("performs both tiers", as_editorial_actor),
                              ("corroborates itself", as_corroborator)):
            with self.subTest(shape=label):
                frozen = copy.deepcopy(control)
                for row in frozen["reviewHistory"]:
                    for event in row["reviewEvents"]:
                        if event["kind"] == "editorial-review":
                            tamper(event)
                self.assertIn(
                    "REVIEW_ACTOR_INDEPENDENCE",
                    {issue.code for issue in validate_frozen_release(frozen)})

    def test_a_solo_release_claims_no_human_verification_or_native_review(self):
        authorization = self.solo_frozen()["releaseAuthorization"]
        self.assertEqual(
            {"releaseModes": [SOLO_MAINTAINER_MODE],
             "humanVerifiedPatternIds": [],
             "humanNativeReviewedPatternIds": []},
            authorization)

    def test_a_human_release_states_its_human_coverage_per_pattern(self):
        document = human_document()
        approved = sorted(
            pattern["id"] for _, _, pattern in approved_patterns(document))
        self.assertEqual(
            {"releaseModes": [HUMAN_REVIEWED_MODE],
             "humanVerifiedPatternIds": approved,
             "humanNativeReviewedPatternIds": approved},
            freeze_editorial(document, 1, context())["releaseAuthorization"])

    def test_human_verification_coverage_cannot_be_forged(self):
        frozen = self.solo_frozen()
        approved = sorted(
            row["id"] for row in frozen["policy"]
            if row["kind"] == "pattern" and row["reviewState"] == "approved")
        for field in ("humanVerifiedPatternIds",
                      "humanNativeReviewedPatternIds"):
            with self.subTest(field=field):
                tampered = copy.deepcopy(frozen)
                tampered["releaseAuthorization"][field] = approved
                self.assertIn(
                    "FROZEN_RELEASE_AUTHORIZATION_PARITY",
                    [issue.code for issue in validate_frozen_release(tampered)])

    def test_a_genuine_human_verification_of_a_solo_pattern_is_reported(self):
        """Truthfulness runs both ways: real human coverage is not discarded."""
        document = solo_document()
        for lemma, meaning, pattern in approved_patterns(document):
            pattern["reviewEvents"] = [
                reference_verification(lemma, meaning, pattern),
                {
                    "kind": "external-verification",
                    "decision": "accept",
                    "scopeVersion": 1,
                    "scopeDigest": review_scope_digest(
                        "external-verification", lemma, meaning, pattern),
                    "supportingEvidenceDigests": contemporary_pins(pattern),
                    "reviewerRef": EXTERNAL_REVIEWER,
                    "reviewedAt": REVIEWED_AT,
                },
                editorial_review(lemma, meaning, pattern),
                owner_approval(lemma, meaning, pattern),
            ]
        self.assertClean(document)
        authorization = freeze_editorial(
            document, 1, context())["releaseAuthorization"]
        self.assertEqual([SOLO_MAINTAINER_MODE], authorization["releaseModes"])
        self.assertTrue(authorization["humanVerifiedPatternIds"])
        self.assertEqual([], authorization["humanNativeReviewedPatternIds"])

    def test_release_authorization_is_derived_from_the_retained_history(self):
        frozen = self.solo_frozen()
        policy = {row["id"]: row for row in frozen["policy"]}
        history = {row["id"]: row for row in frozen["reviewHistory"]}
        self.assertEqual(
            frozen["releaseAuthorization"],
            T._derive_release_authorization(policy, history))


# --------------------------------------------------------------------------
# §12  both modes travel the whole real machinery, end to end
# --------------------------------------------------------------------------

class BothModesEndToEnd(Phase4E1TestCase):

    def assertReachesAuthoritativeRuntime(self, document):
        self.assertClean(document)
        frozen = freeze_editorial(document, 1, context())
        self.assertEqual([], validate_frozen_release(frozen))
        runtime = verified_runtime_from_frozen(frozen)
        self.assertEqual([], validate_runtime(runtime))
        self.assertEqual(frozen["runtimeProjection"], runtime)
        return frozen, runtime

    def test_the_human_chain_reaches_authoritative_runtime(self):
        self.assertReachesAuthoritativeRuntime(human_document())

    def test_the_solo_chain_reaches_authoritative_runtime(self):
        self.assertReachesAuthoritativeRuntime(solo_document())

    def test_both_modes_project_the_identical_public_runtime(self):
        """Governance decides what may ship, never what shipping looks like."""
        _, human_runtime = self.assertReachesAuthoritativeRuntime(
            human_document())
        _, solo_runtime = self.assertReachesAuthoritativeRuntime(
            solo_document())
        self.assertEqual(human_runtime, solo_runtime)

    def test_neither_mode_ships_any_governance_vocabulary(self):
        for label, build in (("human", human_document),
                             ("solo", solo_document)):
            with self.subTest(mode=label):
                _, runtime = self.assertReachesAuthoritativeRuntime(build())
                blob = json.dumps(runtime, ensure_ascii=False)
                for token in sorted(T.GOVERNANCE_PRIVATE_KEYS) + [
                        "reference-verification", "editorial-review",
                        SOLO_MAINTAINER_MODE, REFERENCE_ACTOR, OWNER]:
                    self.assertNotIn(token, blob)


# --------------------------------------------------------------------------
# §13  a malformed or unknown mode fails closed rather than crashing
# --------------------------------------------------------------------------

class MalformedModeFailsClosed(Phase4E1TestCase):

    def test_no_malformed_mode_crashes_the_editorial_validator(self):
        for value in MALFORMED_MODES:
            with self.subTest(value=repr(value)):
                document = solo_document()
                for _, _, pattern in approved_patterns(document):
                    pattern["releaseMode"] = copy.deepcopy(value)
                codes = self.codes(document)
                self.assertIn("SCHEMA_ENUM", codes)

    def test_a_malformed_mode_collapses_to_the_strictest_chain(self):
        """Fail-closed compounds: the defaulted chain has no reference tier.

        A pattern whose mode cannot be read is governed by the human chain,
        which refuses the reference-verification stage outright.  An unreadable
        mode therefore cannot leave a nonhuman verification standing.
        """
        for value in MALFORMED_MODES:
            with self.subTest(value=repr(value)):
                document = solo_document()
                for _, _, pattern in approved_patterns(document):
                    pattern["releaseMode"] = copy.deepcopy(value)
                codes = self.codes(document)
                self.assertIn("REVIEW_STAGE_NOT_IN_MODE", codes)

    def test_the_mode_helpers_normalise_every_malformed_value(self):
        for value in MALFORMED_MODES:
            with self.subTest(value=repr(value)):
                self.assertEqual(
                    DEFAULT_RELEASE_MODE, T.normalized_release_mode(value))
                self.assertEqual(
                    T.nonhuman_stage_kinds(DEFAULT_RELEASE_MODE),
                    T.nonhuman_stage_kinds(value))
                self.assertEqual(
                    T.forbidden_stage_kinds(DEFAULT_RELEASE_MODE),
                    T.forbidden_stage_kinds(value))

    def test_an_absent_mode_is_the_human_chain(self):
        document = solo_document()
        for _, _, pattern in approved_patterns(document):
            pattern.pop("releaseMode")
        codes = self.codes(document)
        self.assertIn("REVIEW_STAGE_NOT_IN_MODE", codes)

    def test_a_malformed_mode_in_a_frozen_history_row_is_refused(self):
        for value in MALFORMED_MODES:
            with self.subTest(value=repr(value)):
                frozen = self.solo_frozen()
                for row in frozen["reviewHistory"]:
                    row["releaseMode"] = copy.deepcopy(value)
                codes = {issue.code
                         for issue in validate_frozen_release(frozen)}
                self.assertTrue(codes, "a malformed frozen mode must be refused")
                self.assertIn("SCHEMA_ENUM", codes)


# --------------------------------------------------------------------------
# §13  one mutation per load-bearing Phase 4E.1 gate, in a single matrix
# --------------------------------------------------------------------------

class LoadBearingGateMutations(Phase4E1TestCase):

    def test_the_unmutated_control_is_clean(self):
        self.assertClean(solo_document())

    def test_each_gate_refuses_its_own_mutation(self):
        def reviewer_ref_on_reference(document, ctx):
            _, _, pattern = self.first_solo(document)
            event = pattern["reviewEvents"][0]
            event.pop("actorRef")
            event["reviewerRef"] = OWNER
            return document, ctx

        def unknown_actor(document, ctx):
            _, _, pattern = self.first_solo(document)
            pattern["reviewEvents"][0]["actorRef"] = "test-actor-nobody"
            return document, ctx

        def human_actor(document, ctx):
            actors = actor_registry()
            actors[REFERENCE_ACTOR]["human"] = True
            return document, context(editorial_actor_registry=actors)

        def missing_role(document, ctx):
            actors = actor_registry()
            actors[REFERENCE_ACTOR]["roles"] = []
            return document, context(editorial_actor_registry=actors)

        def borrowed_human_role(document, ctx):
            actors = actor_registry()
            actors[REFERENCE_ACTOR]["roles"] = [
                "reference-verification", "native-linguistic"]
            return document, context(editorial_actor_registry=actors)

        def shared_actor(document, ctx):
            actors = actor_registry()
            actors[REFERENCE_ACTOR]["roles"] = [
                "reference-verification", "editorial-review"]
            for lemma, meaning, pattern in approved_patterns(document):
                pattern["reviewEvents"][1] = editorial_review(
                    lemma, meaning, pattern, actor=REFERENCE_ACTOR)
            return document, context(editorial_actor_registry=actors)

        def actor_as_human_verifier(document, ctx):
            human = human_document()
            _, _, pattern = self.first_solo(human)
            pattern["reviewEvents"][0]["reviewerRef"] = REFERENCE_ACTOR
            return human, ctx

        def native_reviewer_as_actor(document, ctx):
            _, _, pattern = self.first_solo(document)
            pattern["reviewEvents"][0]["actorRef"] = NATIVE_REVIEWER
            return document, ctx

        def owner_as_actor(document, ctx):
            _, _, pattern = self.first_solo(document)
            pattern["reviewEvents"][0]["actorRef"] = OWNER
            return document, ctx

        def no_evidence(document, ctx):
            _, _, pattern = self.first_solo(document)
            pattern["reviewEvents"][0].pop("supportingEvidenceDigests")
            return document, ctx

        def stale_evidence(document, ctx):
            _, _, pattern = self.first_solo(document)
            pattern["evidence"][0]["locator"] = "fixture://phase4e1/retargeted"
            return document, ctx

        def duplicate_reference(document, ctx):
            _, _, pattern = self.first_solo(document)
            pattern["reviewEvents"].insert(
                1, copy.deepcopy(pattern["reviewEvents"][0]))
            return document, ctx

        def reference_in_human_mode(document, ctx):
            human = human_document()
            lemma, meaning, pattern = self.first_solo(human)
            pattern["reviewEvents"].insert(
                0, reference_verification(lemma, meaning, pattern))
            return human, ctx

        def unknown_mode(document, ctx):
            _, _, pattern = self.first_solo(document)
            pattern["releaseMode"] = "trust-me"
            return document, ctx

        def missing_approval(document, ctx):
            _, _, pattern = self.first_solo(document)
            pattern["reviewEvents"] = pattern["reviewEvents"][:2]
            return document, ctx

        mutations = (
            ("a solo reference stage cannot name a reviewer",
             reviewer_ref_on_reference, "SCHEMA_UNKNOWN_FIELD"),
            ("the reference actor must resolve", unknown_actor,
             "EDITORIAL_ACTOR_REGISTRY_DANGLING"),
            ("the reference actor must be nonhuman", human_actor,
             "EDITORIAL_ACTOR_NOT_NONHUMAN"),
            ("the reference actor needs its role", missing_role,
             "EDITORIAL_ACTOR_ROLE"),
            ("an actor cannot hold a human role", borrowed_human_role,
             "EDITORIAL_ACTOR_ROLE_UNKNOWN"),
            ("the two nonhuman tiers must be independent", shared_actor,
             "REVIEW_ACTOR_INDEPENDENCE"),
            ("an actor cannot be a human external verifier",
             actor_as_human_verifier, "REVIEWER_REGISTRY_DANGLING"),
            ("a human native reviewer cannot be an actor",
             native_reviewer_as_actor, "EDITORIAL_ACTOR_REGISTRY_DANGLING"),
            ("the product owner cannot be an actor", owner_as_actor,
             "EDITORIAL_ACTOR_REGISTRY_DANGLING"),
            ("reference acceptance needs pinned evidence", no_evidence,
             "REVIEW_EVIDENCE_REQUIRED"),
            ("stale evidence retires the verification", stale_evidence,
             "REVIEW_STATE_MISMATCH"),
            ("a reference stage cannot be accepted twice", duplicate_reference,
             "REVIEW_DUPLICATE_STAGE_ACCEPTANCE"),
            ("the human chain has no reference stage", reference_in_human_mode,
             "REVIEW_STAGE_NOT_IN_MODE"),
            ("an unknown mode fails closed", unknown_mode, "SCHEMA_ENUM"),
            ("owner approval stays mandatory", missing_approval,
             "REVIEW_STATE_MISMATCH"),
        )
        for name, mutate, expected in mutations:
            with self.subTest(gate=name):
                document, validation_context = mutate(
                    solo_document(), context())
                self.assertRefused(expected, document, validation_context)


# --------------------------------------------------------------------------
# §14/§16  the real corpus, the real context and AB advanced by nothing
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Phase 4F-B3B editorial delta
#
# Phase 4F-B3B implemented the five approved editorial corrections from the B3A
# adjudication -- rows P7-NR-005, P7-NR-029, P7-NR-030, P7-NR-037 and
# P7-NR-040.  They change learner-facing canonical fields by design, which is
# exactly what the guard below forbids *for its own phase*.  Normalising them
# away keeps that guard truthful about the phase it belongs to, instead of
# reporting a later phase's authorised work as this phase's violation.
#
# The normalisation is deliberately exact: it reverts a field only when that
# field currently holds the precise value B3B wrote.  Any other edit -- to
# these patterns, to these fields, or anywhere else in the corpus -- survives
# normalisation and still fails the guard.  The corrected values themselves are
# pinned independently by tests/test_priority7_phase4fb3b.py.
# --------------------------------------------------------------------------

#: pattern id -> field -> (value B3B wrote, value it replaced)
PHASE_4FB3B_APPROVED_EDITS = {
    "vp-p-sluchac-obey-genitive-object-674adae2dec3": {
        "learnerExplanationEn": (
            "In the obey sense słuchać still takes the Genitive: "
            "dziecko słucha mamy.",
            "In the obey sense słuchać still takes the Genitive: "
            "nie słucha rodziców."),
    },
    "vp-p-mowic-tell-content-dative-recipient-accusative-content"
    "-2f2b1add1960": {
        "learnerExplanationEn": (
            "The thing told is Accusative and the person told is Dative; the "
            "person can be left out: mówię prawdę.",
            "Two roles: the person told is Dative, the thing told is "
            "Accusative."),
        "complements": (
            [{"type": "case", "case": "dative", "required": False,
              "role": "recipient"},
             {"type": "case", "case": "accusative", "required": True,
              "role": "content"}],
            [{"type": "case", "case": "dative", "required": True,
              "role": "recipient"},
             {"type": "case", "case": "accusative", "required": True,
              "role": "content"}]),
    },
    "vp-p-mowic-tell-content-dative-recipient-ze-clause-a01ddc4a4736": {
        "learnerExplanationEn": (
            "The same meaning with clause content: że introduces what is "
            "said, and the person, if named, is Dative: mówię, że to prawda.",
            "The same meaning with clause content: the person stays Dative "
            "and że introduces what is said."),
        "complements": (
            [{"type": "case", "case": "dative", "required": False,
              "role": "recipient"},
             {"type": "clause", "clauseKind": "ze", "required": True,
              "role": "content"}],
            [{"type": "case", "case": "dative", "required": True,
              "role": "recipient"},
             {"type": "clause", "clauseKind": "ze", "required": True,
              "role": "content"}]),
    },
    "vp-p-podobac-sie-appeal-to-nominative-stimulus-dative-experiencer"
    "-ef199e675ee9": {
        "teachingStatus": ("active-production", "recognition-only"),
        "cefr": ({"recognition": "A2", "production": "A2"},
                 {"recognition": "A2"}),
    },
    "vp-p-wierzyc-have-trust-w-accusative-target-6561408ea8d1": {
        "teachingStatus": ("active-production", "recognition-only"),
        "cefr": ({"recognition": "B1", "production": "B1"},
                 {"recognition": "B1"}),
    },
}


def without_phase_4fb3b_edits(corpus):
    """Return a copy of ``corpus`` with the three B3B corrections reverted."""
    corpus = copy.deepcopy(corpus)
    for lemma in corpus["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                edits = PHASE_4FB3B_APPROVED_EDITS.get(pattern["id"], {})
                for field, (written, replaced) in edits.items():
                    if pattern.get(field) == written:
                        pattern[field] = replaced
    return corpus


# --------------------------------------------------------------------------
# Phase 4F-C2 normalisation
#
# Phase 4F-C2 implemented the canonical example specification locked by Phase
# 4F-C1C: five existing canonical examples took new wording under their
# unchanged durable keys and IDs, six patterns gained their first example, and
# one nonhuman example-generation actor was registered to carry the resulting
# `editorial-generated` provenance.  This suite's historical claims are stated
# over the corpus with that approved work reverted, exactly as Phase 4F-B3B's
# corrections already are.
#
# The revert is keyed on the complete approved example object: locked text,
# durable key, deterministic ID, audio flag and every provenance field.  Any
# mutation, second example or example on a fourteenth pattern remains visible
# and still breaks the historical guard.
# --------------------------------------------------------------------------

PHASE_4FC1C_MATRIX = ROOT / "reports" / "phase-4fc1c" / "adjudication-matrix.csv"

#: The nonhuman actor Phase 4F-C2 registered.  It holds the
#: `example-generation` role only and never appears in a review event.
PHASE_4FC2_ACTOR = "priority7-example-generation"
PHASE_4FC2_ADOPTED_AT = "2026-08-16"
PHASE_4FC2_EXAMPLE_KEYS = {
    "vp-p-dziekowac-thank-dative-recipient-za-accusative-057197dd300f":
        "thanks-for-cooperation",
    "vp-p-placic-pay-za-accusative-goods-73c6760c091d":
        "how-much-for-everything",
    "vp-p-dbac-take-care-of-o-accusative-target-d3e3eb63129c":
        "care-every-day",
    "vp-p-pytac-ask-for-information-o-accusative-topic-c89674d989d8":
        "asking-about-the-price",
    "vp-p-pytac-ask-for-information-accusative-person-o-accusative-topic-841b41ed735a":
        "asking-a-friend-about-a-restaurant",
    "vp-p-widziec-perceive-visually-accusative-object-80b697e51432":
        "saw-your-sister",
    "vp-p-myslec-think-about-o-locative-topic-edf0461e0dd2":
        "thinking-about-the-exam",
    "vp-p-znalezc-find-accusative-object-d80c52211462":
        "finally-found-a-flat",
    "vp-p-zajmowac-sie-look-after-person-instrumental-object-6f93facbd939":
        "looking-after-my-sisters-daughter",
    "vp-p-opiekowac-sie-care-for-instrumental-object-8aa6f0a91e5b":
        "caring-for-a-sick-grandmother",
    "vp-p-zalezec-depend-on-od-genitive-source-1ad29f7a1318":
        "plans-depend-on-the-weather",
}
PHASE_4FC2_ACTOR_NOTE_SHA256 = (
    "82065a16d79829e6e4526880009e84dfb0982ed4e1b4a49e7695e72ed93558d6")


#: Phase 4F-C2C superseded the wording of exactly these two Phase 4F-C1C rows
#: after an exact collision with pre-existing language-teaching material was
#: found before release.  Only ``pl`` and ``en`` move: the durable key, the
#: deterministic ID, ``audioEligible`` and the whole ``origin`` object are the
#: C2 ones.  The map is a closed literal keyed by review ID; no other row may
#: be overridden, and an unauthorized wording mutation anywhere else must
#: still survive normalization.
PHASE_4FC2C_WORDING_OVERRIDE = {
    "P7-NR-033": {
        "priorPl": "Czy widzisz tę górę?",
        "priorEn": "Do you see that mountain?",
        "finalPl": "Czy widzisz tę czerwoną torbę?",
        "finalEn": "Do you see that red bag?",
    },
    "P7-NR-043": {
        "priorPl": "Opiekuję się chorą babcią.",
        "priorEn": "I look after my sick grandmother.",
        "finalPl": "Dziś opiekuję się młodszą siostrą.",
        "finalEn": "Today I'm looking after my younger sister.",
    },
}


def phase_4fc2c_final_wording(row):
    """C1C's locked wording, with exactly the two C2C rows superseded.

    The override refuses to fire unless the matrix still carries the exact
    C1C wording it supersedes, so an edit to the historical adjudication
    artifact cannot be absorbed here silently.
    """
    override = PHASE_4FC2C_WORDING_OVERRIDE.get(row["reviewId"])
    if override is None:
        return row["finalPolish"], row["finalEnglish"]
    if (row["finalPolish"], row["finalEnglish"]) != (
            override["priorPl"], override["priorEn"]):
        raise AssertionError(
            "Phase 4F-C2C override no longer supersedes the C1C wording it "
            f"was written against: {row['reviewId']}")
    return override["finalPl"], override["finalEn"]


def phase_4fc2_rows():
    """The Phase 4F-C1C rows Phase 4F-C2 implemented, keyed by pattern ID."""
    with PHASE_4FC1C_MATRIX.open(newline="", encoding="utf-8") as handle:
        return {row["patternId"]: row for row in csv.DictReader(handle)
                if row["implementationDisposition"] in {"REPLACE", "CREATE"}}


def phase_4fc2_repository_source(locator):
    kind, rest = locator.split(":", 1)
    entity_id, field = rest.rsplit(".", 1)
    return {"kind": kind, "id": entity_id, "field": field}


# --------------------------------------------------------------------------
# Phase 4F-D3.1 normalisation
#
# The locked D3 adjudication approved exactly three editorial-tier wording
# corrections on patterns that were already reference-verified: two English
# example translations and one positive Polish model that appears in two
# learner-facing fields of a single pattern.  No Polish example text, no
# provenance, no identity and no reference evidence moved, so every tier-1
# reference digest is unchanged and only the tier-2 editorial scope of these
# three rows differs.
#
# This suite's historical claims are stated over the corpus with that approved
# work reverted, exactly as Phase 4F-B3B's corrections and Phase 4F-C2's
# examples already are.  The revert is keyed on the exact approved final
# string in the exact field of the exact pattern: an unauthorized fourth
# wording change, or any mutation of one of these three, is not recognised,
# stays visible, and still breaks the historical guard.
# --------------------------------------------------------------------------

#: Closed literal.  Review ID -> the single pattern the correction lives on and
#: the exact (prior, final) strings per field.  No other row may be normalised,
#: and no field outside these three may be normalised on these rows.
PHASE_4FD31_EDITORIAL_CORRECTION = {
    "P7-NR-018": {
        "patternId":
            "vp-p-dbac-take-care-of-o-accusative-target-d3e3eb63129c",
        "exampleEn": ("I look after my fitness every day.",
                      "I work on my fitness every day."),
    },
    "P7-NR-028": {
        "patternId": "vp-p-lubic-enjoy-thing-or-activity-infinitive-activity"
                     "-be3742b7ce45",
        "exampleEn": ("I like reading before sleep.",
                      "I like reading before bed."),
    },
    "P7-NR-037": {
        "patternId":
            "vp-p-podobac-sie-appeal-to-nominative-stimulus-dative-experiencer"
            "-ef199e675ee9",
        "learnerExplanationEn": (
            "The thing liked is the subject and the person is Dative: "
            "ten film podoba mi się.",
            "The thing liked is the subject and the person is Dative: "
            "ten film mi się podoba."),
        "guidanceEn": (
            "The thing liked is the subject and the person is Dative: "
            "ten film podoba mi się.",
            "The thing liked is the subject and the person is Dative: "
            "ten film mi się podoba."),
    },
}

PHASE_4FD31_BY_PATTERN = {
    row["patternId"]: row
    for row in PHASE_4FD31_EDITORIAL_CORRECTION.values()
}


def without_phase_4fd31_corrections(corpus):
    """Return a copy of ``corpus`` with the three D3.1 corrections reverted.

    Each field reverts only when it currently holds the exact approved final
    string, so a wording mutation anywhere -- including a fourth canonical
    edit on one of these same three patterns -- survives normalisation.
    """
    corpus = copy.deepcopy(corpus)
    for lemma in corpus["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                row = PHASE_4FD31_BY_PATTERN.get(pattern["id"])
                if row is None:
                    continue
                if "exampleEn" in row:
                    prior, final = row["exampleEn"]
                    examples = pattern.get("examples") or []
                    if len(examples) == 1 and examples[0].get("en") == final:
                        examples[0]["en"] = prior
                if "learnerExplanationEn" in row:
                    prior, final = row["learnerExplanationEn"]
                    if pattern.get("learnerExplanationEn") == final:
                        pattern["learnerExplanationEn"] = prior
                if "guidanceEn" in row:
                    prior, final = row["guidanceEn"]
                    notes = pattern.get("errorNotes") or []
                    if notes and notes[0].get("guidanceEn") == final:
                        notes[0]["guidanceEn"] = prior
    return corpus


def without_phase_4fc2_examples(corpus):
    """Return a copy of ``corpus`` with the C1C example work reverted.

    Later approved wording is absorbed first: the Phase 4F-C2C two-row
    override through :func:`phase_4fc2c_final_wording`, and the Phase
    4F-D3.1 editorial corrections through
    :func:`without_phase_4fd31_corrections`.  The result is the corpus as
    it stood before Phase 4F-C2, which is what this suite's historical
    claims are stated over.
    """
    corpus = without_phase_4fd31_corrections(corpus)
    rows = phase_4fc2_rows()
    for lemma in corpus["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                row = rows.get(pattern["id"])
                if row is None:
                    continue
                examples = pattern.get("examples") or []
                if len(examples) != 1:
                    continue
                example = examples[0]
                key = PHASE_4FC2_EXAMPLE_KEYS[pattern["id"]]
                final_pl, final_en = phase_4fc2c_final_wording(row)
                expected = {
                    "id": T.allocate_example_id(pattern["id"], key),
                    "key": key,
                    "pl": final_pl,
                    "en": final_en,
                    "audioEligible": False,
                    "origin": {
                        "kind": "editorial-generated",
                        "generatorRef": PHASE_4FC2_ACTOR,
                        "adoptedAt": PHASE_4FC2_ADOPTED_AT,
                    },
                }
                if example != expected:
                    continue
                if row["implementationDisposition"] == "CREATE":
                    # The baseline omits the key entirely on a pattern that
                    # has no example; restoring [] would not be the baseline.
                    pattern.pop("examples")
                    continue
                example["pl"] = row["currentPolish"]
                example["en"] = row["currentEnglish"]
                example["origin"] = {
                    "kind": row["currentOrigin"],
                    "repositorySource": phase_4fc2_repository_source(
                        row["currentRepositorySource"]),
                }
    return corpus


def without_phase_4fc2_actor(context_document):
    """Remove only the exact approved C2 actor, never a mutated record."""
    context_document = copy.deepcopy(context_document)
    registry = context_document.get("editorialActorRegistry", {})
    record = registry.get(PHASE_4FC2_ACTOR)
    if (isinstance(record, dict) and
            set(record) == {"human", "kind", "roles", "namedInPhase", "note"} and
            record["human"] is False and
            record["kind"] == "example-generation-workflow" and
            record["roles"] == ["example-generation"] and
            record["namedInPhase"] == "Priority 7 Phase 4F-C2" and
            hashlib.sha256(record["note"].encode("utf-8")).hexdigest() ==
            PHASE_4FC2_ACTOR_NOTE_SHA256):
        registry.pop(PHASE_4FC2_ACTOR)
    return context_document



#: The commit Phase 4F-A produced; its review history is the checkpoint.
#: Phase 4F-B3B.1 appended one fresh tier-1 acceptance to each of the two rows
#: whose optionality correction moved their reference scope, and rewrote none
#: of the original 45.  Asserting 47 as "Phase 4F-A's inventory" would rewrite
#: history; asserting 45 as the current total would deny the refresh.
PHASE_4FA_CHECKPOINT_COMMIT = "7beb50d7b3463d7745352f1608f1e30019529fdf"

#: The same commit named for its other role: the parent Phase 4F-B3B started
#: from, and therefore the immutable pre-B3B corpus any "did a later phase
#: change linguistic content?" guard must compare against.  Aliased rather than
#: re-spelled so the two names can never drift apart -- 4F-A produced this
#: commit and B3B began from it, so they are one commit seen from two sides.
PHASE_4FB3B_BASELINE_SHA = PHASE_4FA_CHECKPOINT_COMMIT

#: Fields a governance-only phase may move.  Deliberately the same four the
#: guard has always excluded; Phase 4F-B3B.2 widened nothing.
GOVERNANCE_KEYS = frozenset(
    {"releaseMode", "reviewState", "reviewEvents", "evidence"})


def corpus_projection(corpus):
    """Every lemma, meaning and pattern fact outside the governance keys."""
    return [
        {"lemma": {k: v for k, v in lemma.items() if k != "meanings"},
         "meaning": {k: v for k, v in meaning.items() if k != "patterns"},
         "pattern": {k: v for k, v in pattern.items()
                     if k not in GOVERNANCE_KEYS}}
        for lemma in corpus["lemmas"]
        for meaning in lemma["meanings"]
        for pattern in meaning["patterns"]]


def guard_holds(repository, revision, *, normalise_baseline=False,
                corpus_name="corpus.json"):
    """Run the later-change guard inside ``repository`` against ``revision``.

    The repaired guard is ``revision=<pinned baseline>`` with
    ``normalise_baseline=False``: the working corpus, with the five approved
    B3B edits reverted, must equal the immutable pre-B3B corpus.

    ``revision="HEAD", normalise_baseline=True`` reproduces the superseded
    form exactly, so the controls can show it passing where the repaired form
    fails.  Both sides had to be normalised there, because both sides carried
    the candidate's edits once the candidate was HEAD -- which is precisely
    what made it a comparison of the corpus with itself.

    Returns a bool rather than asserting so a control can require either
    outcome.
    """
    blob = subprocess.run(
        ["git", "show", f"{revision}:{corpus_name}"],
        cwd=repository, capture_output=True, text=True)
    if blob.returncode != 0:
        raise AssertionError(blob.stderr)
    baseline = json.loads(blob.stdout)
    if normalise_baseline:
        baseline = without_phase_4fb3b_edits(baseline)
    working = json.loads(
        (Path(repository) / corpus_name).read_text(encoding="utf-8"))
    return (corpus_projection(baseline)
            == corpus_projection(without_phase_4fb3b_edits(working)))

#: pattern id -> fresh tier-1 acceptances appended by Phase 4F-B3B.1.
PHASE_4FB3B1_REFRESHED = {
    "vp-p-mowic-tell-content-dative-recipient-accusative-content"
    "-2f2b1add1960": 1,
    "vp-p-mowic-tell-content-dative-recipient-ze-clause-a01ddc4a4736": 1,
}

PHASE_4FA_EVENT_COUNT = 45
CURRENT_EVENT_COUNT = (
    PHASE_4FA_EVENT_COUNT + sum(PHASE_4FB3B1_REFRESHED.values()))


def phase_4fa_review_events():
    """pattern id -> the reviewEvents Phase 4F-A actually wrote."""
    blob = subprocess.run(
        ["git", "show", PHASE_4FA_CHECKPOINT_COMMIT
         + ":editorial/verb-pattern-candidates.json"],
        cwd=ROOT, capture_output=True, text=True)
    if blob.returncode != 0:
        raise AssertionError(blob.stderr)
    return {pattern["id"]: pattern["reviewEvents"]
            for lemma in json.loads(blob.stdout)["lemmas"]
            for meaning in lemma["meanings"]
            for pattern in meaning["patterns"]}


class CommittedStateGuard(unittest.TestCase):
    """The later-change guard must stay meaningful once the candidate is HEAD.

    Every control below runs inside a throwaway repository built in a temporary
    directory.  The real repository is never written to, never committed and
    never has its HEAD moved; only the two corpora are borrowed from it.

    The point the controls establish is narrow and behavioural: with HEAD moved
    past the baseline, pinning to the baseline commit still discriminates,
    while reading ``HEAD`` no longer does.
    """

    #: A pattern none of the five approved B3B edits touches.
    UNRELATED_PATTERN = "vp-p-szukac-seek-genitive-target-71dc6eff512c"

    def isolated_repository(self):
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)

        def run(*arguments):
            return subprocess.run(
                ["git", *arguments], cwd=holder.name, capture_output=True,
                text=True, check=True)

        run("init", "-q")
        run("config", "user.email", "phase4e1@example.invalid")
        run("config", "user.name", "phase 4e1 control")
        return holder.name, run

    def commit_corpus(self, directory, run, corpus, message):
        (Path(directory) / "corpus.json").write_text(
            json.dumps(corpus, ensure_ascii=False, indent=2), encoding="utf-8")
        run("add", "-A")
        run("commit", "-q", "-m", message)
        return run("rev-parse", "HEAD").stdout.strip()

    def baseline_corpus(self):
        blob = subprocess.run(
            ["git", "show", PHASE_4FB3B_BASELINE_SHA
             + ":editorial/verb-pattern-candidates.json"],
            cwd=ROOT, capture_output=True, text=True, check=True)
        return json.loads(blob.stdout)

    def candidate_corpus(self):
        # The Phase 4F-B3B candidate this guard is about: the live corpus with
        # the later Phase 4F-C2 example work reverted.
        return without_phase_4fc2_examples(
            H2.without_phase_4fh2_content_completion(
                H21.without_phase_4fh21_product_reapproval(
                    json.loads(CORPUS.read_text(encoding="utf-8")))))

    def with_sixth_edit(self):
        """The candidate plus one unauthorised learner-facing change."""
        corpus = self.candidate_corpus()
        for lemma in corpus["lemmas"]:
            for meaning in lemma["meanings"]:
                for pattern in meaning["patterns"]:
                    if pattern["id"] == self.UNRELATED_PATTERN:
                        pattern["learnerExplanationEn"] = "unauthorised sixth"
                        return corpus
        self.fail("control pattern not found")

    def committed_history(self, *corpora):
        """Commit each corpus in turn; return (baseline sha, head sha)."""
        directory, run = self.isolated_repository()
        shas = [self.commit_corpus(directory, run, corpus, f"step {index}")
                for index, corpus in enumerate(corpora)]
        return directory, shas[0], shas[-1]

    # -- the repair works ---------------------------------------------------

    def test_the_legitimate_candidate_passes_once_it_is_head(self):
        directory, baseline, head = self.committed_history(
            self.baseline_corpus(), self.candidate_corpus())
        self.assertNotEqual(baseline, head, "HEAD must have moved")
        self.assertTrue(guard_holds(directory, baseline))

    def test_a_sixth_committed_edit_fails_against_the_pinned_baseline(self):
        directory, baseline, _ = self.committed_history(
            self.baseline_corpus(), self.candidate_corpus(),
            self.with_sixth_edit())
        self.assertFalse(guard_holds(directory, baseline))

    def test_a_wrong_value_on_an_approved_field_fails(self):
        corpus = self.candidate_corpus()
        podobac = next(key for key in PHASE_4FB3B_APPROVED_EDITS
                       if "podobac" in key)
        for lemma in corpus["lemmas"]:
            for meaning in lemma["meanings"]:
                for pattern in meaning["patterns"]:
                    if pattern["id"] == podobac:
                        pattern["cefr"]["production"] = "B1"
        directory, baseline, _ = self.committed_history(
            self.baseline_corpus(), corpus)
        self.assertFalse(guard_holds(directory, baseline))

    def test_reverting_an_approved_edit_also_fails(self):
        """Normalisation reverts the approved value, not the whole field."""
        corpus = self.candidate_corpus()
        sluchac = next(key for key in PHASE_4FB3B_APPROVED_EDITS
                       if "sluchac" in key)
        for lemma in corpus["lemmas"]:
            for meaning in lemma["meanings"]:
                for pattern in meaning["patterns"]:
                    if pattern["id"] == sluchac:
                        pattern["learnerExplanationEn"] = "something else"
        directory, baseline, _ = self.committed_history(
            self.baseline_corpus(), corpus)
        self.assertFalse(guard_holds(directory, baseline))

    # -- why the repair was needed, kept executable -------------------------

    def test_the_old_head_form_would_have_missed_the_sixth_edit(self):
        """The defect Codex found, pinned so it cannot return.

        Same repository, same unauthorised commit, same guard body -- only the
        revision differs.  Read from ``HEAD`` the comparison is the corpus
        against itself and passes; read from the pinned baseline it fails.
        """
        directory, baseline, _ = self.committed_history(
            self.baseline_corpus(), self.candidate_corpus(),
            self.with_sixth_edit())
        self.assertTrue(
            guard_holds(directory, "HEAD", normalise_baseline=True),
            "the superseded HEAD form is expected to be vacuous")
        self.assertFalse(guard_holds(directory, baseline),
                         "the pinned form must catch what HEAD misses")

    def test_the_head_form_was_sound_only_while_uncommitted(self):
        """It was not always wrong -- only wrong once the candidate is HEAD."""
        directory, baseline, _ = self.committed_history(
            self.baseline_corpus())
        # HEAD is still the pre-B3B baseline, as it was throughout B3B.
        (Path(directory) / "corpus.json").write_text(
            json.dumps(self.with_sixth_edit(), ensure_ascii=False, indent=2),
            encoding="utf-8")
        self.assertFalse(
            guard_holds(directory, "HEAD", normalise_baseline=True))
        self.assertFalse(guard_holds(directory, baseline))

    def test_the_production_guard_reads_the_pinned_baseline(self):
        """Read the guard's executable body, not the whole file.

        A file-wide search would trip over the controls above, which must
        mention ``HEAD`` to demonstrate the defect, and over the guard's own
        docstring, which explains why it no longer reads it.
        """
        source = inspect.getsource(
            RealGovernanceBoundary
            .test_the_real_corpus_changed_only_governance_and_evidence)
        body = source.split('"""')[-1]
        self.assertIn("PHASE_4FB3B_BASELINE_SHA", body)
        self.assertNotIn("HEAD", body)


class RealGovernanceBoundary(Phase4E1TestCase):

    def real_corpus(self):
        # Phase 4F-C2 implemented the locked Phase 4F-C1C example
        # specification.  Phase 4E.1's boundary claims are about the corpus
        # Phase 4E.1 governed, so that later approved work is reverted here
        # exactly as Phase 4F-B3B's corrections already are.  Phase 4F-E1's
        # tier-2 acceptances are reverted first, on the same terms.
        return without_phase_4fc2_examples(
            E1.without_phase_4fe1_editorial_review(
                F2.without_phase_4ff2_product_approval(
                    H2.without_phase_4fh2_content_completion(
                        H21.without_phase_4fh21_product_reapproval(
                            self.live_corpus())))))

    def real_context_document(self):
        return without_phase_4fc2_actor(
            E1.without_phase_4fe1_actors(
                F2.without_phase_4ff2_reviewer(
                    H2.without_phase_4fh2_context(
                        H21.without_phase_4fh21_context(
                            self.live_context_document())))))

    def live_corpus(self):
        return json.loads(CORPUS.read_text(encoding="utf-8"))

    def live_context_document(self):
        return json.loads(CONTEXT_FILE.read_text(encoding="utf-8"))

    def test_the_amended_validator_still_accepts_the_live_corpus(self):
        """The same gate, run against the corpus as it stands right now.

        The sibling test pins Phase 4F-A's own review date and therefore has
        to read the normalised corpus.  This one carries no pinned date, so
        it keeps proving that whatever later phases recorded still passes the
        Phase 4E.1 actor model unchanged.
        """
        document = self.live_context_document()
        issues = validate_editorial(self.live_corpus(), ValidationContext(
            source_registry=document["sourceRegistry"],
            reviewer_registry=document["reviewerRegistry"],
            author_registry=document["authorRegistry"],
            allocation_registry=document["allocationRegistry"],
            editorial_actor_registry=document["editorialActorRegistry"],
            repository_index=T.repository_index_from_root(ROOT)))
        self.assertEqual([], issues, f"unexpected issues: {issues}")

    def test_every_live_actor_is_nonhuman_and_holds_only_workflow_roles(self):
        """Live and unconditional: the actor model cannot drift.

        Phase 4F-E1 registered the tier-2 actors Phase 4E.1 anticipated.
        Whatever is registered, no actor may be a person, may hold a role
        outside the closed workflow vocabulary, or may share an identity key
        with a human reviewer or author.
        """
        document = self.live_context_document()
        actors = document["editorialActorRegistry"]
        self.assertEqual({}, document["authorRegistry"])
        for actor_id, record in actors.items():
            with self.subTest(actor=actor_id):
                self.assertIs(False, record["human"])
                self.assertNotEqual([], record["roles"])
                for role in record["roles"]:
                    self.assertIn(role, T.EDITORIAL_ACTOR_ROLES)
        self.assertEqual(set(), set(actors) & set(document["reviewerRegistry"]))
        self.assertEqual(set(), set(actors) & set(document["authorRegistry"]))
        # The two nonhuman tiers stay separate identities.
        reference = {actor_id for actor_id, record in actors.items()
                     if "reference-verification" in record["roles"]}
        editorial = {actor_id for actor_id, record in actors.items()
                     if "editorial-review" in record["roles"]}
        self.assertEqual(set(), reference & editorial)

    def test_the_real_corpus_changed_only_governance_and_evidence(self):
        """Phase 4F-A wrote this corpus, so the byte-identity check moved.

        What Phase 4E.1 guarded -- that the amendment touched no linguistic
        content -- is guarded here: outside ``releaseMode``, ``reviewState``,
        ``reviewEvents`` and ``evidence``, every lemma, meaning and pattern
        matches the pre-B3B baseline once the five approved B3B edits are
        normalised away.

        The baseline is pinned to the immutable commit, never read from
        ``HEAD``.  ``HEAD`` was correct only while Phase 4F-B3B was an
        uncommitted working tree; the moment the candidate is itself committed,
        ``HEAD`` contains it and this degrades into comparing the corpus with
        itself, which passes no matter what changed.  ``CommittedStateGuard``
        below proves that difference on a repository whose HEAD really has
        moved.

        Only the working side is normalised.  The baseline predates B3B, so it
        holds none of the values ``without_phase_4fb3b_edits`` reverts, and
        normalising it too could only ever mask a difference.
        """
        result = subprocess.run(
            ["git", "show", PHASE_4FB3B_BASELINE_SHA
             + ":editorial/verb-pattern-candidates.json"],
            cwd=ROOT, capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(
            corpus_projection(json.loads(result.stdout.decode("utf-8"))),
            corpus_projection(without_phase_4fb3b_edits(self.real_corpus())))

    def test_the_real_corpus_holds_exactly_the_phase_4fa_inventory(self):
        corpus = priority7_corpus(self.real_corpus())
        lemmas = corpus["lemmas"]
        meanings = [m for lemma in lemmas for m in lemma["meanings"]]
        patterns = [p for meaning in meanings for p in meaning["patterns"]]
        self.assertEqual(30, len(lemmas))
        self.assertEqual(34, len(meanings))
        self.assertEqual(45, len(patterns))
        self.assertEqual(
            {"reference-verified": 45},
            dict(collections.Counter(
                pattern["reviewState"] for pattern in patterns)))
        self.assertEqual(PHASE_4FA_EVENT_COUNT,
                         sum(len(history) for history in
                             phase_4fa_review_events().values()))
        self.assertEqual(
            CURRENT_EVENT_COUNT,
            sum(len(pattern["reviewEvents"]) for pattern in patterns))
        self.assertEqual(
            0, sum(len(pattern["activityEligibility"]) for pattern in patterns))

    def test_every_real_event_is_an_actor_borne_reference_verification(self):
        """The amendment's whole point, exercised on real data.

        No real event may name a human reviewer, claim a stage the solo chain
        does not have at tier 1, or arrive without the nonhuman actor.
        """
        corpus = priority7_corpus(self.real_corpus())
        patterns = [p for lemma in corpus["lemmas"]
                    for meaning in lemma["meanings"]
                    for p in meaning["patterns"]]
        self.assertEqual({SOLO_MAINTAINER_MODE},
                         {pattern["releaseMode"] for pattern in patterns})
        for pattern in patterns:
            for event in pattern["reviewEvents"]:
                with self.subTest(pattern_id=pattern["id"]):
                    self.assertEqual("reference-verification", event["kind"])
                    self.assertEqual("accept", event["decision"])
                    self.assertEqual("priority7-reference-analysis",
                                     event["actorRef"])
                    self.assertNotIn("reviewerRef", event)
                    self.assertNotIn("corroboratingActorRefs", event)
                    self.assertNotIn("findings", event)
        blob = json.dumps(corpus, ensure_ascii=False)
        for token in (HUMAN_REVIEWED_MODE, "editorial-review",
                      "editorial-generated", "generatorRef", "reviewerRef",
                      "external-verification", "native-linguistic",
                      "product-approval", REFERENCE_ACTOR):
            with self.subTest(token=token):
                if token == REFERENCE_ACTOR:
                    # the synthetic actor, which must never reach real data
                    self.assertTrue(token.startswith("test-"))
                self.assertNotIn(token, blob)

    def test_the_five_pending_replacement_slots_are_untouched(self):
        """Three repository-reuse originals intact, two slots still empty."""
        corpus = self.real_corpus()
        origins = [
            example["origin"]["kind"]
            for lemma in corpus["lemmas"]
            for meaning in lemma["meanings"]
            for pattern in meaning["patterns"]
            for example in (pattern.get("examples") or [])]
        self.assertEqual({"repository-reuse"}, set(origins))
        self.assertEqual(
            0, sum(1 for kind in origins if kind == "editorial-generated"))

    def test_ab_remains_a_human_native_reviewer_and_nothing_else(self):
        reviewers = self.real_context_document()["reviewerRegistry"]
        self.assertEqual({"native-reviewer-001"}, set(reviewers))
        record = reviewers["native-reviewer-001"]
        self.assertIs(True, record["human"])
        self.assertIs(True, record["nativePolishSpeaker"])
        self.assertEqual("AB", record["displayName"])
        self.assertEqual(["native-linguistic"], record["roles"])
        self.assertNotIn("ownerAllowsMultipleRoles", record)
        self.assertNotIn("acknowledgedReleaseModes", record)

    def test_the_real_reference_actor_is_nonhuman_and_singly_roled(self):
        """Phase 4E.1's actor model, as actually instantiated.

        One identity, ``human: false`` stated explicitly, holding the tier-1
        role and nothing else -- so it cannot also perform the editorial review
        it would have to be independent of, and cannot generate an example.
        """
        document = self.real_context_document()
        self.assertEqual({}, document["authorRegistry"])
        self.assertEqual({}, document["allocationRegistry"])
        actors = priority7_actors(document["editorialActorRegistry"])
        self.assertEqual({"priority7-reference-analysis"}, set(actors))
        record = actors["priority7-reference-analysis"]
        self.assertIs(False, record["human"])
        self.assertEqual(["reference-verification"], record["roles"])
        for role in record["roles"]:
            self.assertIn(role, T.EDITORIAL_ACTOR_ROLES)
        self.assertEqual(
            set(), set(document["reviewerRegistry"]) & set(actors),
            "no identity key may span the human and nonhuman registries")

    def test_the_real_actor_identity_names_a_workflow_not_a_vendor(self):
        blob = json.dumps(
            self.real_context_document()["editorialActorRegistry"],
            ensure_ascii=False).lower()
        for token in VendorIndependence.VENDOR_TOKENS:
            with self.subTest(token=token):
                self.assertNotIn(token.lower(), blob)

    def test_no_real_reviewer_holds_any_release_stage_authority_but_native(self):
        reviewers = self.real_context_document()["reviewerRegistry"]
        for role in ("external-verification", "reference-verification",
                     "product-approval", "correction", "reopen"):
            with self.subTest(role=role):
                self.assertEqual(
                    [], [reference for reference, record in reviewers.items()
                         if role in record.get("roles", [])])

    def test_no_synthetic_identity_leaked_into_the_real_context(self):
        blob = json.dumps(self.real_context_document(), ensure_ascii=False)
        for forbidden in ("test-", "synthetic", "fixture"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, blob)

    def test_the_amended_validator_accepts_the_real_corpus_as_it_stands(self):
        corpus = self.real_corpus()
        document = self.real_context_document()
        issues = validate_editorial(corpus, ValidationContext(
            source_registry=document["sourceRegistry"],
            reviewer_registry=document["reviewerRegistry"],
            author_registry=document["authorRegistry"],
            allocation_registry=document["allocationRegistry"],
            editorial_actor_registry=document["editorialActorRegistry"],
            repository_index=T.repository_index_from_root(ROOT),
            today=date(2026, 8, 14)))
        self.assertEqual([], issues, f"unexpected issues: {issues}")

    def test_no_release_artifact_or_public_runtime_exists(self):
        # Superseded by Priority 7 Phase 4F-I1, the release that materialised
        # the official runtime.  The only document that may occupy that path
        # is exactly the I1 release artifact, pinned by digest and revision,
        # and it may only exist alongside the matching shell and worker.
        self.assertEqual("complete", i1_bundle().state)


if __name__ == "__main__":
    unittest.main()
