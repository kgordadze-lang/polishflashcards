"""Priority 7 Phase 4E solo-maintainer governance amendment.

Phase 4E answers one question: can this project authorise a release without
either blocking forever on human roles it does not have, or lying about the
review it actually performed?

Everything exercised here is synthetic.  No lemma, sentence, reviewer, actor,
source or approval in this suite is real, and the suite deliberately re-proves
at the end that the real 45-pattern corpus advanced by exactly nothing.

The properties under test are:

* a nonhuman actor can never be rendered as human or native review;
* the solo-maintainer chain accepts genuine reference-backed editorial
  evidence and refuses missing, stale, unsourced or unresolved-blocking
  evidence;
* owner product approval is mandatory and mode-aware;
* an editorially generated sentence is recorded as generated, never authored;
* the fully human-reviewed chain remains available and unweakened;
* the release states its own governance mode in a form derived from the
  retained history, so no later tool can mistake one mode for the other.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import subprocess
import unittest
from datetime import date
from pathlib import Path

import priority7_tooling as T
from priority7_tooling import (
    DEFAULT_RELEASE_MODE,
    HUMAN_REVIEWED_MODE,
    RELEASE_MODES,
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
EDITORIAL_ACTOR = "test-actor-editorial-001"
CORROBORATING_ACTOR = "test-actor-editorial-002"
# Phase 4E.1: reference verification is performed by its own nonhuman
# source-analysis workflow actor, never by a human reference reviewer.
REFERENCE_ACTOR = "test-actor-reference-analysis-001"
NATIVE_REVIEWER = "test-reviewer-native-001"
EXTERNAL_REVIEWER = "test-reviewer-external-001"
PRODUCT_REVIEWER = "test-reviewer-product-001"

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


def parts_of(document, lemma_index=0, meaning_index=0, pattern_index=0):
    lemma = document["lemmas"][lemma_index]
    meaning = lemma["meanings"][meaning_index]
    return lemma, meaning, meaning["patterns"][pattern_index]


def declared_mode_of(pattern):
    return pattern.get("releaseMode", DEFAULT_RELEASE_MODE)


def contemporary_pins(pattern):
    return sorted({
        evidence_digest(record) for record in pattern["evidence"]
        if record["sourceKind"] in {
            "contemporary-reference", "contemporary-corpus"}
    })


def reference_verification(lemma, meaning, pattern, reviewed_at=REVIEWED_AT):
    return {
        "kind": "reference-verification",
        "decision": "accept",
        "scopeVersion": 1,
        "scopeDigest": review_scope_digest(
            "reference-verification", lemma, meaning, pattern),
        "supportingEvidenceDigests": contemporary_pins(pattern),
        "actorRef": REFERENCE_ACTOR,
        "reviewedAt": reviewed_at,
    }


def editorial_review(lemma, meaning, pattern, reviewed_at=REVIEWED_AT,
                     findings=None):
    event = {
        "kind": "editorial-review",
        "decision": "accept",
        "scopeVersion": 1,
        "scopeDigest": review_scope_digest(
            "editorial-review", lemma, meaning, pattern),
        "actorRef": EDITORIAL_ACTOR,
        "corroboratingActorRefs": [CORROBORATING_ACTOR],
        "reviewedAt": reviewed_at,
    }
    if findings is not None:
        event["findings"] = findings
    return event


def owner_approval(lemma, meaning, pattern, reviewed_at=REVIEWED_AT):
    return {
        "kind": "product-approval",
        "decision": "accept",
        "scopeVersion": 1,
        "scopeDigest": review_scope_digest(
            "product-approval", lemma, meaning, pattern),
        "reviewerRef": OWNER,
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


def approved_patterns(document):
    for lemma in document["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                if pattern.get("reviewState") == "approved":
                    yield lemma, meaning, pattern


def solo_document():
    """The synthetic release, re-governed under the solo-maintainer mode.

    Every human-authored example becomes a truthfully labelled editorially
    generated one, because that is what the real workflow now produces.
    """
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
    """The same release under the pre-existing fully human-reviewed chain."""
    document = payload()["editorial"]
    for lemma, meaning, pattern in approved_patterns(document):
        pattern["reviewEvents"] = human_chain(lemma, meaning, pattern)
    return document


class Phase4ETestCase(unittest.TestCase):
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

    def solo_frozen(self, document=None, revision=1):
        return freeze_editorial(document or solo_document(), revision, context())

    def first_solo(self, document):
        """The one approved pattern that carries examples and error notes."""
        for lemma, meaning, pattern in approved_patterns(document):
            if pattern.get("examples"):
                return lemma, meaning, pattern
        raise AssertionError("fixture must expose an approved pattern")


# --------------------------------------------------------------------------
# §10/§19  a nonhuman actor can never be rendered as human or native review
# --------------------------------------------------------------------------

class NonhumanActorCannotMasqueradeAsHuman(Phase4ETestCase):

    def test_an_editorial_review_cannot_name_a_reviewer(self):
        """The schema itself refuses the confusion, not a downstream check."""
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        event = pattern["reviewEvents"][1]
        event.pop("actorRef")
        event["reviewerRef"] = NATIVE_REVIEWER
        codes = self.codes(document)
        self.assertIn("SCHEMA_REQUIRED", codes)
        self.assertIn("SCHEMA_UNKNOWN_FIELD", codes)

    def test_a_human_stage_cannot_name_an_editorial_actor(self):
        """Product approval is the solo chain's human stage, and stays one.

        Phase 4E.1 moved reference verification onto a nonhuman actor, so the
        stage this property is asserted against is the owner's approval -- the
        one stage that must never become machine-performed.
        """
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        event = pattern["reviewEvents"][2]
        event.pop("reviewerRef")
        event["actorRef"] = EDITORIAL_ACTOR
        codes = self.codes(document)
        self.assertIn("SCHEMA_REQUIRED", codes)
        self.assertIn("SCHEMA_UNKNOWN_FIELD", codes)

    def test_an_editorial_actor_reference_cannot_resolve_to_a_human(self):
        document = solo_document()
        actors = copy.deepcopy(payload()["syntheticIdentities"]
                               ["editorialActorRegistry"])
        actors[EDITORIAL_ACTOR]["human"] = True
        self.assertRefused(
            "EDITORIAL_ACTOR_NOT_NONHUMAN", document,
            context(editorial_actor_registry=actors))

    def test_an_actor_record_must_state_human_false_explicitly(self):
        """Omitting the field is not the same as declaring nonhumanity."""
        document = solo_document()
        actors = copy.deepcopy(payload()["syntheticIdentities"]
                               ["editorialActorRegistry"])
        actors[EDITORIAL_ACTOR].pop("human")
        self.assertRefused(
            "EDITORIAL_ACTOR_NOT_NONHUMAN", document,
            context(editorial_actor_registry=actors))

    def test_a_model_placed_in_the_reviewer_registry_is_still_refused(self):
        """The direct attempt: register the model as a native reviewer."""
        document = human_document()
        reviewers = copy.deepcopy(payload()["syntheticIdentities"]
                                  ["reviewerRegistry"])
        reviewers["test-model-pretending-001"] = {
            "human": False, "roles": ["native-linguistic"]}
        _, _, pattern = self.first_solo(document)
        pattern["reviewEvents"][1]["reviewerRef"] = "test-model-pretending-001"
        self.assertRefused(
            "REVIEWER_NOT_HUMAN", document, context(reviewer_registry=reviewers))

    def test_an_editorial_actor_key_does_not_resolve_as_a_reviewer(self):
        document = human_document()
        _, _, pattern = self.first_solo(document)
        pattern["reviewEvents"][1]["reviewerRef"] = EDITORIAL_ACTOR
        self.assertRefused("REVIEWER_REGISTRY_DANGLING", document)

    def test_one_identity_key_cannot_be_both_reviewer_and_actor(self):
        reviewers = copy.deepcopy(payload()["syntheticIdentities"]
                                  ["reviewerRegistry"])
        reviewers[EDITORIAL_ACTOR] = {
            "human": True, "roles": ["native-linguistic"]}
        self.assertRefused(
            "REGISTRY_KEY_COLLISION", solo_document(),
            context(reviewer_registry=reviewers))

    def test_an_editorial_actor_needs_the_editorial_review_role(self):
        document = solo_document()
        actors = copy.deepcopy(payload()["syntheticIdentities"]
                               ["editorialActorRegistry"])
        actors[EDITORIAL_ACTOR]["roles"] = ["example-generation"]
        self.assertRefused(
            "EDITORIAL_ACTOR_ROLE", document,
            context(editorial_actor_registry=actors))

    def test_the_release_never_describes_editorial_review_as_native(self):
        """The decisive end-to-end property, asserted on the frozen release."""
        frozen = self.solo_frozen()
        self.assertEqual(
            {"releaseModes": [SOLO_MAINTAINER_MODE],
             "humanVerifiedPatternIds": [],
             "humanNativeReviewedPatternIds": []},
            frozen["releaseAuthorization"])
        released = set()
        for row in frozen["policy"]:
            if row["kind"] == "pattern" and row["reviewState"] == "approved":
                released.add(row["id"])
                self.assertEqual(SOLO_MAINTAINER_MODE, row["releaseMode"])
        self.assertTrue(released)
        for row in frozen["reviewHistory"]:
            if row["id"] not in released:
                continue
            with self.subTest(id=row["id"]):
                kinds = {event["kind"] for event in row["reviewEvents"]}
                self.assertEqual(set(T.SOLO_STAGE_KINDS), kinds)
                self.assertNotIn("native-linguistic", kinds)
                self.assertNotIn("external-verification", kinds)
                for event in row["reviewEvents"]:
                    if event["kind"] == "editorial-review":
                        self.assertIn("actorRef", event)
                        self.assertNotIn("reviewerRef", event)


# --------------------------------------------------------------------------
# §12/§19  the solo-maintainer chain accepts a genuine reference-backed release
# --------------------------------------------------------------------------

class SoloMaintainerReleasePath(Phase4ETestCase):

    def test_a_complete_reference_backed_release_validates_and_freezes(self):
        document = solo_document()
        self.assertClean(document)
        frozen = self.solo_frozen(document)
        self.assertEqual([], validate_frozen_release(frozen))
        runtime = verified_runtime_from_frozen(frozen)
        self.assertEqual([], validate_runtime(runtime))
        self.assertTrue(runtime["lemmas"])

    def test_the_solo_chain_reaches_approved_through_its_own_state_names(self):
        """Each rung of the ladder is reachable and is named for what it is.

        Learner activities and audio require approval, so every unapproved rung
        must also surrender them.  Both fields sit inside the editorial-review
        scope, so the chain is stamped against that reduced content rather than
        bolted onto a chain that reviewed something else -- which is exactly
        the invalidation this governance is for.
        """
        for count, expected in (
                (0, "research"), (1, "reference-verified"),
                (2, "editorial-reviewed"), (3, "approved")):
            with self.subTest(events=count):
                trial = solo_document()
                lemma, meaning, candidate = self.first_solo(trial)
                if expected != "approved":
                    candidate["activityEligibility"] = []
                    for example in candidate["examples"]:
                        example["audioEligible"] = False
                candidate["reviewEvents"] = solo_chain(
                    lemma, meaning, candidate)[:count]
                candidate["reviewState"] = expected
                self.assertClean(trial)

    def test_a_wrong_state_label_is_refused_at_every_step(self):
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["reviewEvents"] = pattern["reviewEvents"][:2]
        pattern["activityEligibility"] = []
        for claimed in ("approved", "native-reviewed", "externally-verified",
                        "research"):
            with self.subTest(claimed=claimed):
                trial = copy.deepcopy(document)
                _, _, candidate = self.first_solo(trial)
                candidate["reviewState"] = claimed
                self.assertRefused("REVIEW_STATE_MISMATCH", trial)

    def test_the_owner_multi_role_needs_an_explicit_registry_allowance(self):
        """One person verifying and approving is allowed, but never silently.

        Phase 4E.1 moved reference verification onto a nonhuman actor, so the
        solo owner now performs exactly one review stage and this allowance no
        longer has anything to govern there.  The multi-stage case it exists
        for is a human-mode one: the same person acting as external verifier
        and then as product approver.  The gate is asserted where it now
        actually bites, rather than quietly ceasing to be tested.
        """
        def multi_stage_human_release():
            document = human_document()
            for _, _, pattern in approved_patterns(document):
                pattern["reviewEvents"][0]["reviewerRef"] = OWNER
                pattern["reviewEvents"][2]["reviewerRef"] = OWNER
            return document

        def owner_registry(*, allowed):
            reviewers = copy.deepcopy(payload()["syntheticIdentities"]
                                      ["reviewerRegistry"])
            record = dict(
                reviewers[OWNER],
                roles=["external-verification", "product-approval",
                       "correction", "reopen"])
            if not allowed:
                record.pop("ownerAllowsMultipleRoles")
            reviewers[OWNER] = record
            return context(reviewer_registry=reviewers)

        self.assertClean(
            multi_stage_human_release(), owner_registry(allowed=True))
        self.assertRefused(
            "REVIEWER_MULTI_ROLE_NOT_AUTHORIZED",
            multi_stage_human_release(), owner_registry(allowed=False))

    def test_each_stage_still_requires_its_own_role(self):
        """Every solo stage checks its performer against its own registry.

        The tiers now resolve through different registries -- the nonhuman
        actor registry for reference verification and editorial review, the
        human reviewer registry for product approval -- so the property is
        asserted once per stage against whichever registry governs it.
        """
        actor_stages = (
            (0, REFERENCE_ACTOR, "reference-verification"),
            (1, EDITORIAL_ACTOR, "editorial-review"),
        )
        for index, actor, role in actor_stages:
            with self.subTest(stage=role):
                actors = copy.deepcopy(payload()["syntheticIdentities"]
                                       ["editorialActorRegistry"])
                actors[actor]["roles"] = [
                    item for item in actors[actor]["roles"] if item != role]
                self.assertRefused(
                    "EDITORIAL_ACTOR_ROLE", solo_document(),
                    context(editorial_actor_registry=actors))

        reviewers = copy.deepcopy(payload()["syntheticIdentities"]
                                  ["reviewerRegistry"])
        reviewers[OWNER]["roles"] = [
            item for item in reviewers[OWNER]["roles"]
            if item != "product-approval"]
        self.assertRefused(
            "REVIEWER_ROLE", solo_document(),
            context(reviewer_registry=reviewers))

    def test_the_locked_stage_order_still_applies_to_the_solo_chain(self):
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["reviewEvents"] = pattern["reviewEvents"][1:]
        self.assertRefused("REVIEW_STAGE_ORDER", document)


# --------------------------------------------------------------------------
# §9/§13/§19  missing, unsourced and stale evidence all fail closed
# --------------------------------------------------------------------------

class EvidenceGates(Phase4ETestCase):

    def test_reference_verification_without_pinned_evidence_is_refused(self):
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["reviewEvents"][0].pop("supportingEvidenceDigests")
        self.assertRefused("REVIEW_EVIDENCE_REQUIRED", document)

    def test_reference_verification_needs_contemporary_evidence(self):
        document = solo_document()
        lemma, meaning, pattern = self.first_solo(document)
        pattern["evidence"].append({
            "sourceId": "test-source-headword-001",
            "sourceKind": "medak-research",
            "locator": "fixture://phase5a/synthetic/headword",
            "factType": "lemma",
            "checkedAt": REVIEWED_AT,
        })
        sources = copy.deepcopy(payload()["syntheticIdentities"]
                                ["sourceRegistry"])
        sources["test-source-headword-001"] = {"sourceKind": "medak-research"}
        pattern["reviewEvents"] = solo_chain(lemma, meaning, pattern)
        pattern["reviewEvents"][0]["supportingEvidenceDigests"] = [
            evidence_digest(pattern["evidence"][-1])]
        codes = self.codes(document, context(source_registry=sources))
        self.assertIn("REVIEW_CONTEMPORARY_EVIDENCE_REQUIRED", codes)
        self.assertIn("REVIEW_STATE_MISMATCH", codes)

    def test_reference_verification_needs_pattern_or_meaning_evidence(self):
        """Headword presence and a bare contrast note verify no pattern."""
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

    def test_a_pin_that_no_longer_resolves_invalidates_the_release(self):
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["evidence"][0]["note"] = "TEST-ONLY edited after acceptance."
        self.assertRefused("REVIEW_STATE_MISMATCH", document)

    def test_a_removed_evidence_record_invalidates_the_release(self):
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["errorNotes"] = []
        del pattern["evidence"][0]
        self.assertRefused("REVIEW_STATE_MISMATCH", document)

    def test_appending_corroborating_evidence_stays_noninvalidating(self):
        """Strengthening the case must not punish the maintainer."""
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["evidence"].append({
            "sourceId": "test-source-corpus-001",
            "sourceKind": "contemporary-corpus",
            "locator": "fixture://phase5a/synthetic/extra-corroboration",
            "factType": "usage-register",
            "checkedAt": REVIEWED_AT,
        })
        self.assertClean(document)


# --------------------------------------------------------------------------
# §2B/§12/§19  independent editorial review and unresolved blocking findings
# --------------------------------------------------------------------------

class EditorialReviewGates(Phase4ETestCase):

    def test_an_unresolved_blocking_finding_cannot_be_accepted(self):
        document = solo_document()
        lemma, meaning, pattern = self.first_solo(document)
        pattern["reviewEvents"][1] = editorial_review(
            lemma, meaning, pattern,
            findings=[{
                "severity": "high",
                "summary": "TEST-ONLY invented blocking wording objection.",
                "resolved": False,
            }])
        self.assertRefused("EDITORIAL_UNRESOLVED_BLOCKING_FINDING", document)

    def test_a_resolved_blocking_finding_is_accepted_with_its_resolution(self):
        document = solo_document()
        lemma, meaning, pattern = self.first_solo(document)
        pattern["reviewEvents"][1] = editorial_review(
            lemma, meaning, pattern,
            findings=[{
                "severity": "high",
                "summary": "TEST-ONLY invented blocking wording objection.",
                "resolved": True,
                "resolutionNote": "TEST-ONLY invented resolution record.",
            }])
        self.assertClean(document)

    def test_a_resolution_note_is_mandatory_and_cannot_be_faked_away(self):
        document = solo_document()
        lemma, meaning, pattern = self.first_solo(document)
        pattern["reviewEvents"][1] = editorial_review(
            lemma, meaning, pattern,
            findings=[{
                "severity": "high",
                "summary": "TEST-ONLY invented blocking wording objection.",
                "resolved": True,
            }])
        self.assertRefused("SCHEMA_REQUIRED", document)

    def test_an_unresolved_finding_cannot_carry_a_resolution_note(self):
        document = solo_document()
        lemma, meaning, pattern = self.first_solo(document)
        pattern["reviewEvents"][1] = editorial_review(
            lemma, meaning, pattern,
            findings=[{
                "severity": "low",
                "summary": "TEST-ONLY invented minor note.",
                "resolved": False,
                "resolutionNote": "TEST-ONLY contradictory note.",
            }])
        self.assertRefused("EDITORIAL_FINDING_RESOLUTION_FORBIDDEN", document)

    def test_a_single_model_opinion_is_never_release_authoritative(self):
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["reviewEvents"][1].pop("corroboratingActorRefs")
        self.assertRefused("EDITORIAL_CORROBORATION_REQUIRED", document)

    def test_a_model_cannot_corroborate_itself(self):
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["reviewEvents"][1]["corroboratingActorRefs"] = [EDITORIAL_ACTOR]
        self.assertRefused("EDITORIAL_CORROBORATION_SELF", document)

    def test_a_corroborating_actor_must_itself_be_a_registered_nonhuman(self):
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["reviewEvents"][1]["corroboratingActorRefs"] = [
            "test-unregistered-actor"]
        self.assertRefused("EDITORIAL_ACTOR_REGISTRY_DANGLING", document)

    def test_an_editorial_review_requesting_changes_blocks_the_release(self):
        document = solo_document()
        lemma, meaning, pattern = self.first_solo(document)
        pattern["reviewEvents"] = [
            reference_verification(lemma, meaning, pattern),
            {
                "kind": "editorial-review",
                "decision": "changes-requested",
                "actorRef": EDITORIAL_ACTOR,
                "reviewedAt": REVIEWED_AT,
                "note": "TEST-ONLY invented objection.",
                "findings": [{
                    "severity": "high",
                    "summary": "TEST-ONLY invented blocking objection.",
                    "resolved": False,
                }],
            },
            owner_approval(lemma, meaning, pattern, LATER),
        ]
        codes = self.codes(document)
        self.assertIn("REVIEW_STAGE_ORDER", codes)
        self.assertIn("REVIEW_STATE_MISMATCH", codes)


# --------------------------------------------------------------------------
# §5/§13/§19  owner product approval is mandatory and mode-aware
# --------------------------------------------------------------------------

class OwnerApprovalGates(Phase4ETestCase):

    def test_a_release_without_owner_approval_is_not_approved(self):
        """Claiming approval is refused; conceding it costs the learner surface."""
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        del pattern["reviewEvents"][2]
        self.assertRefused("REVIEW_STATE_MISMATCH", document)

        pattern["reviewState"] = "editorial-reviewed"
        codes = self.codes(document)
        self.assertIn("UNAPPROVED_ACTIVITY", codes)
        self.assertIn("AUDIO_NOT_AUTHORIZED", codes)
        self.assertNotIn("REVIEW_STATE_MISMATCH", codes)

    def test_an_unapproved_pattern_cannot_be_projected_or_frozen(self):
        document = solo_document()
        for _, _, pattern in approved_patterns(document):
            del pattern["reviewEvents"][2]
        with self.assertRaises(ValidationFailure):
            freeze_editorial(document, 1, context())

    def test_owner_approval_requires_acknowledging_the_release_mode(self):
        """Approving under a weaker chain is a decision, not a default."""
        reviewers = copy.deepcopy(payload()["syntheticIdentities"]
                                  ["reviewerRegistry"])
        reviewers[OWNER].pop("acknowledgedReleaseModes")
        self.assertRefused(
            "OWNER_RELEASE_MODE_NOT_ACKNOWLEDGED", solo_document(),
            context(reviewer_registry=reviewers))

    def test_acknowledging_only_the_other_mode_does_not_transfer(self):
        reviewers = copy.deepcopy(payload()["syntheticIdentities"]
                                  ["reviewerRegistry"])
        reviewers[OWNER]["acknowledgedReleaseModes"] = [HUMAN_REVIEWED_MODE]
        self.assertRefused(
            "OWNER_RELEASE_MODE_NOT_ACKNOWLEDGED", solo_document(),
            context(reviewer_registry=reviewers))


# --------------------------------------------------------------------------
# §6/§19  truthful generated provenance, and no fabricated human authorship
# --------------------------------------------------------------------------

class ExampleProvenance(Phase4ETestCase):

    def test_an_editorially_generated_example_is_valid_and_labelled(self):
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        self.assertEqual(
            "editorial-generated", pattern["examples"][0]["origin"]["kind"])
        self.assertClean(document)

    def test_generated_provenance_requires_a_generator_and_a_date(self):
        for missing in ("generatorRef", "adoptedAt"):
            with self.subTest(missing=missing):
                document = solo_document()
                _, _, pattern = self.first_solo(document)
                pattern["examples"][0]["origin"].pop(missing)
                self.assertRefused("SCHEMA_REQUIRED", document)

    def test_a_generated_example_cannot_also_claim_a_human_author(self):
        for field, value in (("authorRef", "test-author-original-001"),
                             ("authoredAt", REVIEWED_AT)):
            with self.subTest(field=field):
                document = solo_document()
                _, _, pattern = self.first_solo(document)
                pattern["examples"][0]["origin"][field] = value
                self.assertRefused("ORIGIN_EDITORIAL_FIELD_FORBIDDEN", document)

    def test_a_generated_example_cannot_claim_repository_reuse(self):
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["examples"][0]["origin"]["repositorySource"] = {
            "kind": "card", "id": "p7-phase5a-synthetic-card-001", "field": "ex"}
        self.assertRefused("ORIGIN_EDITORIAL_FIELD_FORBIDDEN", document)

    def test_the_generator_must_be_a_registered_nonhuman_actor(self):
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["examples"][0]["origin"]["generatorRef"] = "test-unregistered"
        self.assertRefused("EDITORIAL_ACTOR_REGISTRY_DANGLING", document)

    def test_a_human_cannot_be_recorded_as_the_generator(self):
        document = solo_document()
        actors = copy.deepcopy(payload()["syntheticIdentities"]
                               ["editorialActorRegistry"])
        actors[EDITORIAL_ACTOR]["human"] = True
        self.assertRefused(
            "EDITORIAL_ACTOR_NOT_NONHUMAN", document,
            context(editorial_actor_registry=actors))

    def test_the_generator_needs_the_example_generation_role(self):
        document = solo_document()
        actors = copy.deepcopy(payload()["syntheticIdentities"]
                               ["editorialActorRegistry"])
        actors[EDITORIAL_ACTOR]["roles"] = ["editorial-review"]
        self.assertRefused(
            "EDITORIAL_ACTOR_ROLE", document,
            context(editorial_actor_registry=actors))

    def test_false_human_authorship_is_still_rejected(self):
        """Phase 4E adds a truthful option; it removes no existing guard."""
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["examples"][0]["origin"] = {
            "kind": "original",
            "authorRef": EDITORIAL_ACTOR,
            "authoredAt": REVIEWED_AT,
        }
        self.assertRefused("AUTHOR_REGISTRY_DANGLING", document)

    def test_a_nonhuman_author_record_is_still_rejected(self):
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["examples"][0]["origin"] = {
            "kind": "original",
            "authorRef": "test-author-model-001",
            "authoredAt": REVIEWED_AT,
        }
        self.assertRefused(
            "AUTHOR_NOT_HUMAN", document,
            context(author_registry={"test-author-model-001": {"human": False}}))

    def test_generated_provenance_never_reaches_the_public_runtime(self):
        runtime = verified_runtime_from_frozen(self.solo_frozen())
        blob = json.dumps(runtime)
        for token in ("editorial-generated", "generatorRef", "adoptedAt",
                      EDITORIAL_ACTOR):
            with self.subTest(token=token):
                self.assertNotIn(token, blob)

        def keys(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    yield key
                    yield from keys(child)
            elif isinstance(value, list):
                for child in value:
                    yield from keys(child)

        self.assertNotIn("origin", set(keys(runtime)))

    def test_changing_a_released_origin_still_requires_a_correction(self):
        """Re-reviewing the change is not the same as authorising it."""
        baseline = self.solo_frozen()
        document = solo_document()
        lemma, meaning, pattern = self.first_solo(document)
        pattern["examples"][0]["origin"]["adoptedAt"] = LATER
        pattern["reviewEvents"].extend(
            solo_chain(lemma, meaning, pattern, LATER))
        with self.assertRaises(ValidationFailure) as caught:
            freeze_editorial(document, 1, context(), previous=baseline)
        self.assertIn(
            "FROZEN_ORIGIN_CORRECTION_REQUIRED",
            [issue.code for issue in caught.exception.issues])


# --------------------------------------------------------------------------
# §3/§4/§11/§19  the two modes never borrow each other's evidence or names
# --------------------------------------------------------------------------

class ModeDiscipline(Phase4ETestCase):

    def test_an_unknown_release_mode_fails_closed(self):
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["releaseMode"] = "owner-says-it-is-fine"
        codes = self.codes(document)
        self.assertIn("SCHEMA_ENUM", codes)
        self.assertIn("REVIEW_STATE_MISMATCH", codes)

    def test_an_absent_mode_means_the_strictest_chain(self):
        """Absence is never the permissive reading."""
        self.assertEqual(HUMAN_REVIEWED_MODE, DEFAULT_RELEASE_MODE)
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern.pop("releaseMode")
        self.assertRefused("REVIEW_STATE_MISMATCH", document)

    def test_editorial_review_cannot_advance_a_human_reviewed_pattern(self):
        """AI review is recordable everywhere and authoritative only in its mode."""
        document = human_document()
        lemma, meaning, pattern = self.first_solo(document)
        pattern["reviewEvents"][1] = editorial_review(lemma, meaning, pattern)
        codes = self.codes(document)
        self.assertIn("REVIEW_STAGE_ORDER", codes)
        self.assertIn("REVIEW_STATE_MISMATCH", codes)

    def test_native_review_alone_cannot_advance_a_solo_pattern(self):
        document = solo_document()
        lemma, meaning, pattern = self.first_solo(document)
        pattern["reviewEvents"][1] = {
            "kind": "native-linguistic",
            "decision": "accept",
            "scopeVersion": 1,
            "scopeDigest": review_scope_digest(
                "native-linguistic", lemma, meaning, pattern),
            "reviewerRef": NATIVE_REVIEWER,
            "reviewedAt": REVIEWED_AT,
        }
        codes = self.codes(document)
        self.assertIn("REVIEW_STAGE_ORDER", codes)
        self.assertIn("REVIEW_STATE_MISMATCH", codes)

    def test_the_two_chains_share_scope_tiers_without_sharing_authority(self):
        """Identical digests are deliberate; identical authority is not.

        A reference verification covers exactly the fields an external
        verification covers, so their digests match.  Relabelling one as the
        other still establishes nothing, because currency is keyed on the
        event kind the declared mode actually requires.
        """
        document = solo_document()
        lemma, meaning, pattern = self.first_solo(document)
        self.assertEqual(
            review_scope_digest("external-verification", lemma, meaning, pattern),
            review_scope_digest("reference-verification", lemma, meaning, pattern))
        self.assertEqual(
            review_scope_digest("native-linguistic", lemma, meaning, pattern),
            review_scope_digest("editorial-review", lemma, meaning, pattern))
        pattern["reviewEvents"][0]["kind"] = "external-verification"
        pattern["reviewEvents"][0]["reviewerRef"] = EXTERNAL_REVIEWER
        self.assertRefused("REVIEW_STATE_MISMATCH", document)

    def test_switching_mode_after_approval_invalidates_the_approval(self):
        for start, switched in ((solo_document(), HUMAN_REVIEWED_MODE),
                                (human_document(), SOLO_MAINTAINER_MODE)):
            with self.subTest(switched=switched):
                document = copy.deepcopy(start)
                for _, _, pattern in approved_patterns(document):
                    pattern["releaseMode"] = switched
                self.assertRefused("REVIEW_STATE_MISMATCH", document)


# --------------------------------------------------------------------------
# §3/§19  genuine human native review remains representable and strengthening
# --------------------------------------------------------------------------

class HumanReviewRemainsRepresentable(Phase4ETestCase):

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

    def test_a_solo_release_may_carry_genuine_human_native_review(self):
        document = self.solo_with_native_review()
        self.assertClean(document)
        frozen = freeze_editorial(document, 1, context())
        authorization = frozen["releaseAuthorization"]
        self.assertEqual([SOLO_MAINTAINER_MODE], authorization["releaseModes"])
        self.assertTrue(
            authorization["humanNativeReviewedPatternIds"],
            "genuine human native review must be reported, not discarded")

    def test_human_native_coverage_is_reported_per_pattern_not_blanket(self):
        """A reviewer who saw one pattern has not covered its neighbours."""
        document = self.solo_with_native_review()
        reviewed_id = None
        for _, _, pattern in approved_patterns(document):
            if reviewed_id is None:
                reviewed_id = pattern["id"]
                continue
            pattern["reviewEvents"] = [
                event for event in pattern["reviewEvents"]
                if event["kind"] != "native-linguistic"]
        frozen = freeze_editorial(document, 1, context())
        self.assertEqual(
            [reviewed_id],
            frozen["releaseAuthorization"]["humanNativeReviewedPatternIds"])

    def test_stale_human_native_review_stops_being_reported(self):
        """Coverage is a live digest claim, not a permanent badge.

        The pattern is rewritten and then re-verified, re-reviewed and
        re-approved through its own chain, so it is legitimately releasable
        again.  What the human native reviewer actually saw is now a different
        text, so the release must stop reporting them as covering it.
        """
        document = self.solo_with_native_review()
        stale_id = None
        for lemma, meaning, pattern in approved_patterns(document):
            if not pattern.get("examples"):
                continue
            stale_id = pattern["id"]
            pattern["learnerExplanationEn"] = (
                "TEST-ONLY invented explanation rewritten after native review.")
            for event in pattern["reviewEvents"]:
                if event["kind"] == "native-linguistic":
                    continue  # deliberately left pointing at the old text
                event["scopeDigest"] = review_scope_digest(
                    event["kind"], lemma, meaning, pattern)
        self.assertIsNotNone(stale_id)
        self.assertClean(document)

        frozen = freeze_editorial(document, 1, context())
        reported = frozen["releaseAuthorization"]["humanNativeReviewedPatternIds"]
        self.assertNotIn(stale_id, reported)

    def test_a_human_native_rejection_blocks_a_solo_release(self):
        """Human review is optional as a gate and never optional as a veto."""
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

        pattern["reviewState"] = "rejected"
        codes = self.codes(document)
        self.assertIn("UNAPPROVED_ACTIVITY", codes)
        self.assertIn("AUDIO_NOT_AUTHORIZED", codes)
        self.assertNotIn("REVIEW_STATE_MISMATCH", codes)

    def test_a_human_native_change_request_invalidates_editorial_acceptance(self):
        """A native objection drops the pattern back to its verified tier."""
        document = solo_document()
        _, _, pattern = self.first_solo(document)
        pattern["reviewEvents"].append({
            "kind": "native-linguistic",
            "decision": "changes-requested",
            "reviewerRef": NATIVE_REVIEWER,
            "reviewedAt": LATER,
            "note": "TEST-ONLY invented native wording objection.",
        })
        self.assertRefused("REVIEW_STATE_MISMATCH", document)

        pattern["reviewState"] = "reference-verified"
        pattern["activityEligibility"] = []
        for example in pattern["examples"]:
            example["audioEligible"] = False
        self.assertClean(document)


# --------------------------------------------------------------------------
# §15/§19  the fully human-reviewed release mode is unweakened
# --------------------------------------------------------------------------

class HumanReviewedModeStillWorks(Phase4ETestCase):

    def test_the_human_chain_still_validates_freezes_and_projects(self):
        document = human_document()
        self.assertClean(document)
        frozen = freeze_editorial(document, 1, context())
        self.assertEqual([], validate_frozen_release(frozen))
        approved_ids = sorted(
            pattern["id"] for _, _, pattern in approved_patterns(document))
        self.assertEqual(
            {"releaseModes": [HUMAN_REVIEWED_MODE],
             "humanVerifiedPatternIds": approved_ids,
             "humanNativeReviewedPatternIds": approved_ids},
            frozen["releaseAuthorization"])
        self.assertEqual([], validate_runtime(
            verified_runtime_from_frozen(frozen)))

    def test_the_human_chain_still_requires_a_human_at_every_stage(self):
        for index, reference in enumerate(
                (EXTERNAL_REVIEWER, NATIVE_REVIEWER, PRODUCT_REVIEWER)):
            with self.subTest(stage=index):
                reviewers = copy.deepcopy(payload()["syntheticIdentities"]
                                          ["reviewerRegistry"])
                reviewers[reference] = dict(reviewers[reference], human=False)
                self.assertRefused(
                    "REVIEWER_NOT_HUMAN", human_document(),
                    context(reviewer_registry=reviewers))

    def test_the_human_chain_needs_no_owner_mode_acknowledgement(self):
        """Phase 4E imposes its new attestation only on its own weaker mode."""
        reviewers = payload()["syntheticIdentities"]["reviewerRegistry"]
        self.assertNotIn("acknowledgedReleaseModes", reviewers[PRODUCT_REVIEWER])
        self.assertClean(human_document())


# --------------------------------------------------------------------------
# §7/§19  the English side is an editorial translation
# --------------------------------------------------------------------------

class EnglishTranslationScope(Phase4ETestCase):

    def edited_en(self, document):
        _, _, pattern = self.first_solo(document)
        pattern["examples"][0]["en"] = (
            "TEST-ONLY retranslated invented sentence, still not Polish.")
        return pattern

    def test_an_en_only_edit_stays_schema_valid(self):
        document = solo_document()
        self.edited_en(document)
        codes = self.codes(document)
        self.assertEqual(
            {"REVIEW_STATE_MISMATCH"}, codes,
            "an English retranslation is a review-currency question only")

    def test_an_en_only_edit_leaves_reference_verification_intact(self):
        document = solo_document()
        lemma, meaning, pattern = self.first_solo(document)
        before = review_scope_digest(
            "reference-verification", lemma, meaning, pattern)
        self.edited_en(document)
        self.assertEqual(
            before,
            review_scope_digest(
                "reference-verification", lemma, meaning, pattern),
            "authorship and structural verification concern example.pl")

    def test_an_en_only_edit_invalidates_editorial_and_product_scope(self):
        document = solo_document()
        lemma, meaning, pattern = self.first_solo(document)
        before = {
            stage: review_scope_digest(stage, lemma, meaning, pattern)
            for stage in ("editorial-review", "product-approval")}
        self.edited_en(document)
        for stage, digest in before.items():
            with self.subTest(stage=stage):
                self.assertNotEqual(
                    digest,
                    review_scope_digest(stage, lemma, meaning, pattern))

    def test_an_en_only_edit_drops_a_solo_release_to_reference_verified(self):
        document = solo_document()
        self.demote(self.edited_en(document), "reference-verified")
        self.assertClean(document)

    def test_an_en_only_edit_drops_a_human_release_to_externally_verified(self):
        document = human_document()
        self.demote(self.edited_en(document), "externally-verified")
        self.assertClean(document)

    def demote(self, pattern, state):
        pattern["reviewState"] = state
        pattern["activityEligibility"] = []
        for example in pattern["examples"]:
            example["audioEligible"] = False


# --------------------------------------------------------------------------
# §11/§12/§19  the frozen release states its own governance, and cannot lie
# --------------------------------------------------------------------------

class FrozenReleaseAuthorization(Phase4ETestCase):

    def test_the_release_authorization_record_is_derived_not_asserted(self):
        frozen = self.solo_frozen()
        forged_id = "vp-p-zorbulate-test-object-direct-object-ed5c9d6bd0b1"
        for mutation in (
                {"releaseModes": [HUMAN_REVIEWED_MODE],
                 "humanVerifiedPatternIds": [],
                 "humanNativeReviewedPatternIds": []},
                {"releaseModes": [SOLO_MAINTAINER_MODE],
                 "humanVerifiedPatternIds": [],
                 "humanNativeReviewedPatternIds": [forged_id]},
                {"releaseModes": [SOLO_MAINTAINER_MODE],
                 "humanVerifiedPatternIds": [forged_id],
                 "humanNativeReviewedPatternIds": []},
                {"releaseModes": [HUMAN_REVIEWED_MODE, SOLO_MAINTAINER_MODE],
                 "humanVerifiedPatternIds": [],
                 "humanNativeReviewedPatternIds": []}):
            with self.subTest(mutation=mutation["releaseModes"]):
                tampered = copy.deepcopy(frozen)
                tampered["releaseAuthorization"] = mutation
                self.assertIn(
                    "FROZEN_RELEASE_AUTHORIZATION_PARITY",
                    [issue.code for issue in validate_frozen_release(tampered)])

    def test_a_frozen_release_must_carry_its_authorization_record(self):
        frozen = self.solo_frozen()
        del frozen["releaseAuthorization"]
        self.assertIn(
            "SCHEMA_REQUIRED",
            [issue.code for issue in validate_frozen_release(frozen)])

    def test_every_frozen_pattern_policy_declares_its_mode(self):
        frozen = self.solo_frozen()
        for index, row in enumerate(frozen["policy"]):
            if row["kind"] != "pattern":
                continue
            with self.subTest(id=row["id"]):
                self.assertIn(row["releaseMode"], RELEASE_MODES)
            tampered = copy.deepcopy(frozen)
            del tampered["policy"][index]["releaseMode"]
            self.assertIn(
                "SCHEMA_REQUIRED",
                [issue.code for issue in validate_frozen_release(tampered)])

    def test_a_frozen_mode_swap_is_refused_in_either_dimension(self):
        """Relabelling a released pattern cannot rewrite what reviewed it.

        Changing one dimension is caught by parity; changing both is caught by
        the state derivation, because the human chain's events are simply not
        in the history.  There is no third place to change.
        """
        control = self.solo_frozen()
        approved = {
            row["id"] for row in control["policy"]
            if row["kind"] == "pattern" and row["reviewState"] == "approved"}
        self.assertTrue(approved)

        policy_only = copy.deepcopy(control)
        for row in policy_only["policy"]:
            if row["id"] in approved:
                row["releaseMode"] = HUMAN_REVIEWED_MODE
        self.assertIn(
            "FROZEN_RELEASE_MODE_PARITY",
            [issue.code for issue in validate_frozen_release(policy_only)])

        both = copy.deepcopy(control)
        for collection in ("policy", "reviewHistory"):
            for row in both[collection]:
                if row["id"] in approved:
                    row["releaseMode"] = HUMAN_REVIEWED_MODE
        self.assertIn(
            "FROZEN_REVIEW_STATE_MISMATCH",
            [issue.code for issue in validate_frozen_release(both)])

    def test_a_retired_pattern_keeps_its_own_governance_mode(self):
        """A tombstoned pattern has no policy row; its history still knows."""
        document = solo_document()
        lemma, meaning, _ = parts_of(document)
        retired = meaning["patterns"].pop()
        baseline = self.solo_frozen()
        advanced = freeze_editorial(
            document, 2, context(), previous=baseline,
            tombstones=[{
                "id": retired["id"],
                "kind": "pattern",
                "formerParentId": meaning["id"],
                "retirementRevision": 2,
                "reason": "TEST-ONLY invented synthetic retirement.",
                "replacementIds": [],
            }])
        self.assertEqual([], validate_frozen_release(advanced))
        history = {row["id"]: row for row in advanced["reviewHistory"]}
        self.assertIn(retired["id"], history)
        self.assertEqual(
            declared_mode_of(retired), history[retired["id"]]["releaseMode"])
        self.assertNotIn(
            retired["id"], {row["id"] for row in advanced["policy"]})

    def test_a_frozen_unknown_mode_is_refused(self):
        frozen = self.solo_frozen()
        for index, row in enumerate(frozen["policy"]):
            if row["kind"] == "pattern":
                frozen["policy"][index]["releaseMode"] = "unaudited"
        self.assertIn(
            "SCHEMA_ENUM",
            [issue.code for issue in validate_frozen_release(frozen)])

    def test_frozen_editorial_events_cannot_gain_a_blocking_finding(self):
        """The frozen archive is validated, not merely stored."""
        frozen = self.solo_frozen()
        patched = False
        for row in frozen["reviewHistory"]:
            for event in row["reviewEvents"]:
                if event["kind"] == "editorial-review":
                    event["findings"] = [{
                        "severity": "high",
                        "summary": "TEST-ONLY invented blocking objection.",
                        "resolved": False,
                    }]
                    patched = True
        self.assertTrue(patched, "fixture must contain an editorial review")
        self.assertIn(
            "EDITORIAL_UNRESOLVED_BLOCKING_FINDING",
            [issue.code for issue in validate_frozen_release(frozen)])

    def test_frozen_review_history_still_refuses_a_nonhuman_reviewer_field(self):
        frozen = self.solo_frozen()
        for row in frozen["reviewHistory"]:
            for event in row["reviewEvents"]:
                if event["kind"] == "editorial-review":
                    event.pop("actorRef")
                    event["reviewerRef"] = NATIVE_REVIEWER
        codes = [issue.code for issue in validate_frozen_release(frozen)]
        self.assertIn("SCHEMA_REQUIRED", codes)
        self.assertIn("SCHEMA_UNKNOWN_FIELD", codes)


# --------------------------------------------------------------------------
# §12/§15  freeze, revision and stable-ID protections are unchanged
# --------------------------------------------------------------------------

class ReleaseSafeguardsUnchanged(Phase4ETestCase):

    def test_released_wording_still_requires_an_owner_correction(self):
        baseline = self.solo_frozen()
        document = solo_document()
        lemma, meaning, pattern = self.first_solo(document)
        pattern["learnerExplanationEn"] = "TEST-ONLY silently rewritten copy."
        pattern["reviewEvents"].extend(
            solo_chain(lemma, meaning, pattern, LATER))
        with self.assertRaises(ValidationFailure) as caught:
            freeze_editorial(document, 2, context(), previous=baseline)
        self.assertIn(
            "FROZEN_WORDING_CORRECTION_REQUIRED",
            [issue.code for issue in caught.exception.issues])

    def test_a_stable_id_survives_a_wording_change_under_the_solo_mode(self):
        """§8: keys and IDs are stable even when the sentence changes."""
        baseline = self.solo_frozen()
        released = {
            row["id"] for row in baseline["identity"] if row["kind"] == "example"}
        document = solo_document()
        lemma, meaning, pattern = self.first_solo(document)
        pattern["examples"][0]["pl"] = "TEST-ONLY replacement invented sentence."
        pattern["examples"][0]["en"] = "TEST-ONLY replacement invented gloss."
        pattern["reviewEvents"].append({
            "kind": "correction",
            "decision": "accept",
            "reviewerRef": OWNER,
            "reviewedAt": LATER,
            "note": "TEST-ONLY invented owner correction of released wording.",
        })
        pattern["reviewEvents"].extend(
            solo_chain(lemma, meaning, pattern, LATER))
        advanced = freeze_editorial(document, 2, context(), previous=baseline)
        self.assertEqual(
            released,
            {row["id"] for row in advanced["identity"] if row["kind"] == "example"},
            "stable example IDs must not be reallocated by new wording")
        self.assertEqual(2, advanced["patternDataRevision"])

    def test_the_revision_contract_still_binds_the_solo_mode(self):
        baseline = self.solo_frozen()
        for revision in (1, 3):
            with self.subTest(revision=revision):
                document = solo_document()
                lemma, meaning, pattern = self.first_solo(document)
                pattern["examples"][0]["pl"] = "TEST-ONLY other invented text."
                pattern["reviewEvents"].append({
                    "kind": "correction",
                    "decision": "accept",
                    "reviewerRef": OWNER,
                    "reviewedAt": LATER,
                    "note": "TEST-ONLY invented owner correction.",
                })
                pattern["reviewEvents"].extend(
                    solo_chain(lemma, meaning, pattern, LATER))
                with self.assertRaises(ValidationFailure) as caught:
                    freeze_editorial(
                        document, revision, context(), previous=baseline)
                self.assertIn(
                    "FROZEN_REVISION_TRANSITION",
                    [issue.code for issue in caught.exception.issues])

    def test_a_solo_release_still_refuses_to_ship_private_governance(self):
        runtime = verified_runtime_from_frozen(self.solo_frozen())
        blob = json.dumps(runtime)
        for token in sorted(T.GOVERNANCE_PRIVATE_KEYS):
            with self.subTest(token=token):
                self.assertNotIn(token, blob)
        for token in ("reviewEvents", "reviewState", "evidence",
                      "reference-verification", "editorial-review",
                      SOLO_MAINTAINER_MODE, OWNER):
            with self.subTest(token=token):
                self.assertNotIn(token, blob)


# --------------------------------------------------------------------------
# Repair 1  duplicate stage acceptances cannot reach an authoritative release
# --------------------------------------------------------------------------

class DuplicateStageAcceptance(Phase4ETestCase):
    """Codex's first NO-GO: a stage accepted twice used to be absorbed.

    The original replay reset tier 1 on a second acceptance instead of
    rejecting it, so `[external, external, native, product]` validated, froze,
    passed frozen validation and produced authoritative runtime. Tiers 2 and 3
    were incidentally protected -- a repeated acceptance there failed the
    preceding-state check -- but tier 1 has no predecessor, so nothing caught
    it.

    The rule now enforced: an on-chain acceptance is refused when that tier
    already stands over the identical scope, with no intervening correction,
    reopen, change request, completed round, or scope change.
    """

    def duplicated(self, document, tier, chain_builder):
        """Insert a second copy of one tier's acceptance into every chain."""
        for lemma, meaning, pattern in approved_patterns(document):
            chain = chain_builder(lemma, meaning, pattern)
            events = list(chain)
            events.insert(tier + 1, copy.deepcopy(chain[tier]))
            pattern["reviewEvents"] = events
        return document

    def assertNeverReachesRelease(self, document):
        """The whole real release path must refuse this history, not just one check."""
        issues = validate_editorial(document, context())
        self.assertTrue(issues, "editorial validation must refuse the duplicate")
        self.assertIn("REVIEW_DUPLICATE_STAGE_ACCEPTANCE",
                      {issue.code for issue in issues})
        with self.assertRaises(ValidationFailure) as caught:
            freeze_editorial(document, 1, context())
        self.assertIn("REVIEW_DUPLICATE_STAGE_ACCEPTANCE",
                      {issue.code for issue in caught.exception.issues})

    def test_every_stage_of_both_chains_refuses_a_duplicate_acceptance(self):
        matrix = (
            (HUMAN_REVIEWED_MODE, human_document, human_chain,
             ("external-verification", "native-linguistic", "product-approval")),
            (SOLO_MAINTAINER_MODE, solo_document, solo_chain,
             ("reference-verification", "editorial-review", "product-approval")),
        )
        for mode, build_document, build_chain, stages in matrix:
            for tier, stage in enumerate(stages):
                with self.subTest(mode=mode, stage=stage):
                    self.assertNeverReachesRelease(
                        self.duplicated(build_document(), tier, build_chain))

    def test_a_tampered_frozen_release_cannot_carry_a_duplicate(self):
        """Freeze refuses these, so the frozen envelope is probed directly."""
        control = self.solo_frozen()
        self.assertEqual([], validate_frozen_release(control))
        for stage in ("reference-verification", "editorial-review",
                      "product-approval"):
            with self.subTest(stage=stage):
                tampered = copy.deepcopy(control)
                for row in tampered["reviewHistory"]:
                    events = row["reviewEvents"]
                    for index, event in enumerate(events):
                        if event["kind"] == stage:
                            events.insert(index + 1, copy.deepcopy(event))
                            break
                codes = {issue.code
                         for issue in validate_frozen_release(tampered)}
                self.assertIn("REVIEW_DUPLICATE_STAGE_ACCEPTANCE", codes)
                with self.assertRaises(ValidationFailure):
                    verified_runtime_from_frozen(tampered)

    def test_a_duplicate_never_produces_authoritative_runtime(self):
        """The property that actually matters, stated end-to-end."""
        for build_document, build_chain in ((human_document, human_chain),
                                            (solo_document, solo_chain)):
            for tier in range(3):
                with self.subTest(chain=build_chain.__name__, tier=tier):
                    document = self.duplicated(
                        build_document(), tier, build_chain)
                    with self.assertRaises(ValidationFailure):
                        verified_runtime_from_frozen(
                            freeze_editorial(document, 1, context()))

    def test_a_scope_change_legitimately_permits_re_review(self):
        """The guard must not block real re-review after real invalidation."""
        for build_document, build_chain in ((human_document, human_chain),
                                            (solo_document, solo_chain)):
            with self.subTest(chain=build_chain.__name__):
                document = build_document()
                for lemma, meaning, pattern in approved_patterns(document):
                    pattern["learnerExplanationEn"] += (
                        " TEST-ONLY edit invalidating the existing review.")
                    pattern["reviewEvents"] = pattern["reviewEvents"] + (
                        build_chain(lemma, meaning, pattern, LATER))
                self.assertClean(document)
                frozen = freeze_editorial(document, 1, context())
                self.assertEqual([], validate_frozen_release(frozen))
                self.assertEqual([], validate_runtime(
                    verified_runtime_from_frozen(frozen)))

    def test_an_owner_correction_legitimately_permits_re_review(self):
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

    def test_a_change_request_legitimately_permits_re_acceptance(self):
        document = solo_document()
        for lemma, meaning, pattern in approved_patterns(document):
            chain = solo_chain(lemma, meaning, pattern)
            pattern["reviewEvents"] = [
                chain[0],
                {
                    "kind": "reference-verification",
                    "decision": "changes-requested",
                    "actorRef": REFERENCE_ACTOR,
                    "reviewedAt": REVIEWED_AT,
                    "note": "TEST-ONLY invented request for changes.",
                },
            ] + solo_chain(lemma, meaning, pattern, LATER)
        self.assertClean(document)

    def test_a_completed_round_may_be_followed_by_a_fresh_round(self):
        """Repeating a stage within a round is refused; a new round is not."""
        document = solo_document()
        for lemma, meaning, pattern in approved_patterns(document):
            pattern["reviewEvents"] = pattern["reviewEvents"] + solo_chain(
                lemma, meaning, pattern, LATER)
        self.assertClean(document)

        # ...but the closing approval itself still cannot simply be repeated.
        repeated = solo_document()
        for lemma, meaning, pattern in approved_patterns(repeated):
            pattern["reviewEvents"] = pattern["reviewEvents"] + [
                owner_approval(lemma, meaning, pattern, LATER)]
        self.assertRefused("REVIEW_DUPLICATE_STAGE_ACCEPTANCE", repeated)


# --------------------------------------------------------------------------
# Repair 2  a malformed releaseMode is a validation issue, never a crash
# --------------------------------------------------------------------------

MALFORMED_RELEASE_MODES = (
    ("null", None),
    ("boolean", True),
    ("integer", 1),
    ("float", 1.5),
    ("array", []),
    ("populated array", ["human-reviewed"]),
    ("object", {}),
    ("populated object", {"mode": "human-reviewed"}),
    ("empty string", ""),
    ("unknown string", "unknown-mode"),
)


class MalformedReleaseMode(Phase4ETestCase):
    """Codex's second NO-GO: container-valued releaseMode raised TypeError.

    ``declared_release_mode`` tested membership against a dict before proving
    the value was a string, so ``releaseMode: []`` and ``releaseMode: {}``
    crashed the validator with an unhashable-type error instead of returning a
    deterministic issue. Every other malformed scalar already validated
    correctly, which is exactly what made the gap easy to miss.
    """

    def test_the_normaliser_never_raises_and_never_coerces(self):
        for label, value in MALFORMED_RELEASE_MODES:
            with self.subTest(value=label):
                self.assertEqual(
                    DEFAULT_RELEASE_MODE,
                    T.declared_release_mode({"releaseMode": value}),
                    "a malformed mode must fall back to the strictest chain")
        self.assertEqual(
            DEFAULT_RELEASE_MODE, T.declared_release_mode({}),
            "an absent mode still defaults to the strictest chain")
        for mode in RELEASE_MODES:
            with self.subTest(mode=mode):
                self.assertEqual(
                    mode, T.declared_release_mode({"releaseMode": mode}))

    def test_the_chain_lookup_never_raises_on_a_malformed_mode(self):
        for label, value in MALFORMED_RELEASE_MODES:
            with self.subTest(value=label):
                self.assertEqual(
                    RELEASE_MODES[DEFAULT_RELEASE_MODE],
                    T.release_mode_chain(value))

    def test_editorial_validation_reports_an_issue_without_raising(self):
        for label, value in MALFORMED_RELEASE_MODES:
            with self.subTest(value=label):
                document = solo_document()
                for _, _, pattern in approved_patterns(document):
                    pattern["releaseMode"] = value
                issues = validate_editorial(document, context())
                self.assertTrue(issues, f"{label} must be refused")
                self.assertIn("SCHEMA_ENUM", {issue.code for issue in issues})

    def test_freeze_refuses_and_no_runtime_is_produced(self):
        for label, value in MALFORMED_RELEASE_MODES:
            with self.subTest(value=label):
                document = solo_document()
                for _, _, pattern in approved_patterns(document):
                    pattern["releaseMode"] = value
                with self.assertRaises(ValidationFailure) as caught:
                    freeze_editorial(document, 1, context())
                self.assertIn(
                    "SCHEMA_ENUM",
                    {issue.code for issue in caught.exception.issues})

    def test_a_malformed_mode_in_a_frozen_policy_row_is_refused(self):
        control = self.solo_frozen()
        for label, value in MALFORMED_RELEASE_MODES:
            with self.subTest(value=label):
                tampered = copy.deepcopy(control)
                for row in tampered["policy"]:
                    if row["kind"] == "pattern":
                        row["releaseMode"] = value
                codes = {issue.code
                         for issue in validate_frozen_release(tampered)}
                self.assertIn("SCHEMA_ENUM", codes)
                with self.assertRaises(ValidationFailure):
                    verified_runtime_from_frozen(tampered)

    def test_a_malformed_mode_in_a_frozen_history_row_is_refused(self):
        control = self.solo_frozen()
        for label, value in MALFORMED_RELEASE_MODES:
            with self.subTest(value=label):
                tampered = copy.deepcopy(control)
                for row in tampered["reviewHistory"]:
                    row["releaseMode"] = value
                codes = {issue.code
                         for issue in validate_frozen_release(tampered)}
                self.assertIn("SCHEMA_ENUM", codes)
                with self.assertRaises(ValidationFailure):
                    verified_runtime_from_frozen(tampered)

    def test_a_malformed_mode_never_leaks_into_the_derived_authorization(self):
        """A derived record normalises; it never echoes a malformed value.

        The stored value is still reported as a schema issue -- the enum error
        quotes it, which is the point of the diagnostic. What must never happen
        is a *derived* governance record repeating it, because that record is
        what a later tool reads to learn how the release was reviewed.
        """
        control = self.solo_frozen()
        policy = {row["id"]: row for row in control["policy"]}
        for label, value in MALFORMED_RELEASE_MODES:
            with self.subTest(value=label):
                history = {
                    row["id"]: dict(row, releaseMode=copy.deepcopy(value))
                    for row in control["reviewHistory"]}
                derived = T._derive_release_authorization(policy, history)
                self.assertTrue(
                    set(derived["releaseModes"]) <= set(RELEASE_MODES),
                    f"derived modes leaked a malformed value: {derived}")
                self.assertEqual([DEFAULT_RELEASE_MODE], derived["releaseModes"])
        self.assertEqual(
            [SOLO_MAINTAINER_MODE],
            control["releaseAuthorization"]["releaseModes"])

    def test_the_real_corpus_survives_every_public_entry_point(self):
        """No public entry point may crash on a malformed mode."""
        corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
        for label, value in MALFORMED_RELEASE_MODES:
            with self.subTest(value=label):
                document = copy.deepcopy(corpus)
                document["lemmas"][0]["meanings"][0]["patterns"][0][
                    "releaseMode"] = value
                issues = validate_editorial(document, ValidationContext())
                self.assertIn("SCHEMA_ENUM", {issue.code for issue in issues})


# --------------------------------------------------------------------------
# §19  every load-bearing Phase 4E gate is mutation-tested in one matrix
# --------------------------------------------------------------------------

class LoadBearingGateMutations(Phase4ETestCase):
    """One mutation per gate, so a future refactor cannot quietly drop one.

    Each entry mutates exactly one thing in an otherwise valid solo-maintainer
    release.  The control case immediately below proves the unmutated document
    really is clean, so a passing row here can never be an accident of some
    unrelated breakage.
    """

    def test_the_unmutated_control_is_clean(self):
        self.assertClean(solo_document())

    def test_each_governance_gate_refuses_its_own_mutation(self):
        def drop_actor(document, ctx):
            _, _, pattern = self.first_solo(document)
            pattern["reviewEvents"][1]["actorRef"] = "test-unregistered-actor"
            return document, ctx

        def humanise_actor(document, ctx):
            actors = copy.deepcopy(payload()["syntheticIdentities"]
                                   ["editorialActorRegistry"])
            actors[EDITORIAL_ACTOR]["human"] = True
            return document, context(editorial_actor_registry=actors)

        def strip_corroboration(document, ctx):
            _, _, pattern = self.first_solo(document)
            pattern["reviewEvents"][1].pop("corroboratingActorRefs")
            return document, ctx

        def unresolved_blocking(document, ctx):
            lemma, meaning, pattern = self.first_solo(document)
            pattern["reviewEvents"][1] = editorial_review(
                lemma, meaning, pattern, findings=[{
                    "severity": "high",
                    "summary": "TEST-ONLY invented blocking objection.",
                    "resolved": False}])
            return document, ctx

        def strip_pins(document, ctx):
            _, _, pattern = self.first_solo(document)
            pattern["reviewEvents"][0].pop("supportingEvidenceDigests")
            return document, ctx

        def stale_evidence(document, ctx):
            _, _, pattern = self.first_solo(document)
            pattern["evidence"][0]["locator"] = "fixture://phase5a/retargeted"
            return document, ctx

        def stale_scope(document, ctx):
            _, _, pattern = self.first_solo(document)
            pattern["learnerExplanationEn"] = "TEST-ONLY rewritten after review."
            return document, ctx

        def drop_owner_approval(document, ctx):
            _, _, pattern = self.first_solo(document)
            del pattern["reviewEvents"][2]
            return document, ctx

        def unacknowledged_owner(document, ctx):
            reviewers = copy.deepcopy(payload()["syntheticIdentities"]
                                      ["reviewerRegistry"])
            reviewers[OWNER].pop("acknowledgedReleaseModes")
            return document, context(reviewer_registry=reviewers)

        def unauthorised_multi_role(document, ctx):
            reviewers = copy.deepcopy(payload()["syntheticIdentities"]
                                      ["reviewerRegistry"])
            reviewers[OWNER] = dict(
                reviewers[OWNER],
                roles=["external-verification", "product-approval",
                       "correction", "reopen"])
            reviewers[OWNER].pop("ownerAllowsMultipleRoles")
            # Phase 4E.1: the multi-stage case is a human-mode one now, since
            # the solo owner performs product approval and nothing else.
            human = human_document()
            for _, _, pattern in approved_patterns(human):
                pattern["reviewEvents"][0]["reviewerRef"] = OWNER
                pattern["reviewEvents"][2]["reviewerRef"] = OWNER
            return human, context(reviewer_registry=reviewers)

        def unknown_mode(document, ctx):
            _, _, pattern = self.first_solo(document)
            pattern["releaseMode"] = "trust-me"
            return document, ctx

        def fabricated_authorship(document, ctx):
            _, _, pattern = self.first_solo(document)
            pattern["examples"][0]["origin"] = {
                "kind": "original",
                "authorRef": EDITORIAL_ACTOR,
                "authoredAt": REVIEWED_AT}
            return document, ctx

        def unregistered_generator(document, ctx):
            _, _, pattern = self.first_solo(document)
            pattern["examples"][0]["origin"]["generatorRef"] = "test-nobody"
            return document, ctx

        def colliding_identity(document, ctx):
            reviewers = copy.deepcopy(payload()["syntheticIdentities"]
                                      ["reviewerRegistry"])
            reviewers[EDITORIAL_ACTOR] = {"human": True, "roles": []}
            return document, context(reviewer_registry=reviewers)

        def duplicate_verification(document, ctx):
            _, _, pattern = self.first_solo(document)
            pattern["reviewEvents"].insert(
                1, copy.deepcopy(pattern["reviewEvents"][0]))
            return document, ctx

        def container_mode(document, ctx):
            _, _, pattern = self.first_solo(document)
            pattern["releaseMode"] = []
            return document, ctx

        mutations = (
            ("editorial actor must resolve", drop_actor,
             "EDITORIAL_ACTOR_REGISTRY_DANGLING"),
            ("editorial actor must be nonhuman", humanise_actor,
             "EDITORIAL_ACTOR_NOT_NONHUMAN"),
            ("editorial review needs corroboration", strip_corroboration,
             "EDITORIAL_CORROBORATION_REQUIRED"),
            ("blocking findings must be resolved", unresolved_blocking,
             "EDITORIAL_UNRESOLVED_BLOCKING_FINDING"),
            ("reference verification needs pinned evidence", strip_pins,
             "REVIEW_EVIDENCE_REQUIRED"),
            ("edited evidence invalidates acceptance", stale_evidence,
             "REVIEW_STATE_MISMATCH"),
            ("edited copy invalidates acceptance", stale_scope,
             "REVIEW_STATE_MISMATCH"),
            ("owner approval is mandatory", drop_owner_approval,
             "REVIEW_STATE_MISMATCH"),
            ("owner must acknowledge the mode", unacknowledged_owner,
             "OWNER_RELEASE_MODE_NOT_ACKNOWLEDGED"),
            ("multi-role needs an explicit allowance", unauthorised_multi_role,
             "REVIEWER_MULTI_ROLE_NOT_AUTHORIZED"),
            ("an unknown mode fails closed", unknown_mode, "SCHEMA_ENUM"),
            ("human authorship cannot be fabricated", fabricated_authorship,
             "AUTHOR_REGISTRY_DANGLING"),
            ("a generator must be registered", unregistered_generator,
             "EDITORIAL_ACTOR_REGISTRY_DANGLING"),
            ("identity keys cannot straddle registries", colliding_identity,
             "REGISTRY_KEY_COLLISION"),
            ("a stage cannot be accepted twice", duplicate_verification,
             "REVIEW_DUPLICATE_STAGE_ACCEPTANCE"),
            ("a container-valued mode fails closed", container_mode,
             "SCHEMA_ENUM"),
        )
        for name, mutate, expected in mutations:
            with self.subTest(gate=name):
                document, validation_context = mutate(
                    solo_document(), context())
                self.assertRefused(expected, document, validation_context)

    def test_each_frozen_gate_refuses_its_own_mutation(self):
        def swap_policy_mode(frozen):
            for row in frozen["policy"]:
                if row["kind"] == "pattern" and row["reviewState"] == "approved":
                    row["releaseMode"] = HUMAN_REVIEWED_MODE

        def swap_history_mode(frozen):
            for row in frozen["reviewHistory"]:
                row["releaseMode"] = HUMAN_REVIEWED_MODE

        def drop_history_mode(frozen):
            for row in frozen["reviewHistory"]:
                del row["releaseMode"]

        def forge_authorization(frozen):
            frozen["releaseAuthorization"]["releaseModes"] = [
                HUMAN_REVIEWED_MODE]

        def forge_native_coverage(frozen):
            approved = [row["id"] for row in frozen["policy"]
                        if row["kind"] == "pattern" and
                        row["reviewState"] == "approved"]
            frozen["releaseAuthorization"][
                "humanNativeReviewedPatternIds"] = sorted(approved)

        def relabel_editorial_event(frozen):
            for row in frozen["reviewHistory"]:
                for event in row["reviewEvents"]:
                    if event["kind"] == "editorial-review":
                        event["kind"] = "native-linguistic"
                        event.pop("actorRef")
                        event.pop("corroboratingActorRefs", None)
                        event["reviewerRef"] = NATIVE_REVIEWER

        def drop_pin(frozen):
            for row in frozen["reviewHistory"]:
                for event in row["reviewEvents"]:
                    if event["kind"] == "reference-verification":
                        event["supportingEvidenceDigests"] = [
                            "sha256:" + "0" * 64]

        mutations = (
            ("policy mode cannot drift from history", swap_policy_mode,
             "FROZEN_RELEASE_MODE_PARITY"),
            ("history mode cannot be relabelled", swap_history_mode,
             "FROZEN_RELEASE_MODE_PARITY"),
            ("history must declare a mode", drop_history_mode,
             "SCHEMA_REQUIRED"),
            ("authorization modes are derived", forge_authorization,
             "FROZEN_RELEASE_AUTHORIZATION_PARITY"),
            ("human native coverage cannot be forged", forge_native_coverage,
             "FROZEN_RELEASE_AUTHORIZATION_PARITY"),
            ("an editorial event cannot become native review",
             relabel_editorial_event, "FROZEN_REVIEW_STATE_MISMATCH"),
            ("a dangling pin invalidates the release", drop_pin,
             "FROZEN_EVIDENCE_PIN_DANGLING"),
        )
        control = self.solo_frozen()
        self.assertEqual([], validate_frozen_release(control))
        for name, mutate, expected in mutations:
            with self.subTest(gate=name):
                frozen = copy.deepcopy(control)
                mutate(frozen)
                codes = [issue.code for issue in validate_frozen_release(frozen)]
                self.assertIn(expected, codes, f"{name}: saw {sorted(set(codes))}")


# --------------------------------------------------------------------------
# §14/§16/§22  the real corpus and the real authoring context advanced by nothing
# --------------------------------------------------------------------------

#: The commit Phase 4F-A produced; its review history is the checkpoint.
#: Phase 4F-B3B.1 appended one fresh tier-1 acceptance to each of the two rows
#: whose optionality correction moved their reference scope, and rewrote none
#: of the original 45.  Asserting 47 as "Phase 4F-A's inventory" would rewrite
#: history; asserting 45 as the current total would deny the refresh.
PHASE_4FA_CHECKPOINT_COMMIT = "7beb50d7b3463d7745352f1608f1e30019529fdf"

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



class RealGovernanceBoundary(Phase4ETestCase):

    def real_corpus(self):
        # Phase 4F-C2 implemented the locked Phase 4F-C1C example
        # specification.  Phase 4E's boundary claims are about the corpus
        # Phase 4E governed, so that later approved work is reverted here.
        # Phase 4F-E1's tier-2 acceptances are reverted first, for the same
        # reason and on the same terms: only the exact approved objects.
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

    def test_the_solo_chain_never_borrows_human_chain_authority(self):
        """Live and unconditional: the human chain's stages stay unrun.

        Phase 4F-E1 legitimately performed tier 2 and Phase 4F-F2 tier 3, so
        ``editorial-review``, ``product-approval``, ``reviewerRef`` and
        ``approved`` now appear in the corpus.  Both were on-chain stages of
        the declared solo mode, which is exactly what Phase 4E built.  What
        Phase 4E forbids whatever any later phase records is the *other*
        chain: no ``external-verification``, no ``native-linguistic``, no
        ``human-reviewed`` mode, and no reviewer holding an authority the
        solo chain never grants.  That is asserted here against the
        unmodified files; the tier-3 claim as Phase 4E made it is asserted
        over the normalised corpus, where it still holds.
        """
        live = self.live_corpus()
        corpus = priority7_corpus(live)
        patterns = [pattern for lemma in corpus["lemmas"]
                    for meaning in lemma["meanings"]
                    for pattern in meaning["patterns"]]
        self.assertEqual(45, len(patterns))
        self.assertEqual({SOLO_MAINTAINER_MODE},
                         {pattern["releaseMode"] for pattern in patterns})
        self.assertNotIn(
            "approved",
            {pattern["reviewState"]
             for lemma in self.real_corpus()["lemmas"]
             for meaning in lemma["meanings"]
             for pattern in meaning["patterns"]})
        blob = json.dumps(live, ensure_ascii=False)
        for token in ("external-verification", "native-linguistic",
                      HUMAN_REVIEWED_MODE):
            with self.subTest(token=token):
                self.assertNotIn(token, blob)
        reviewers = self.live_context_document()["reviewerRegistry"]
        for role in ("external-verification", "reference-verification",
                     "correction", "reopen"):
            with self.subTest(role=role):
                self.assertEqual(
                    [], [reference for reference, record in reviewers.items()
                         if role in record.get("roles", [])])
        # Tier 3 is human-borne by construction: where it has been performed,
        # it names a person and never a nonhuman actor.
        actors = self.live_context_document()["editorialActorRegistry"]
        for lemma in corpus["lemmas"]:
            for meaning in lemma["meanings"]:
                for pattern in meaning["patterns"]:
                    for event in pattern["reviewEvents"]:
                        if event["kind"] != "product-approval":
                            continue
                        with self.subTest(pattern_id=pattern["id"]):
                            self.assertNotIn("actorRef", event)
                            self.assertNotIn(event["reviewerRef"], actors)
                            self.assertIs(
                                True,
                                reviewers[event["reviewerRef"]]["human"])

    def test_the_real_patterns_stand_at_tier_one_of_the_solo_chain(self):
        """Phase 4E built this chain; Phase 4F-A ran its first stage only."""
        corpus = priority7_corpus(self.real_corpus())
        patterns = [pattern for lemma in corpus["lemmas"]
                    for meaning in lemma["meanings"]
                    for pattern in meaning["patterns"]]
        self.assertEqual(45, len(patterns))
        self.assertEqual({"reference-verified"},
                         {pattern["reviewState"] for pattern in patterns})
        self.assertEqual(PHASE_4FA_EVENT_COUNT,
                         sum(len(history) for history in
                             phase_4fa_review_events().values()))
        self.assertEqual(
            CURRENT_EVENT_COUNT,
            sum(len(pattern["reviewEvents"]) for pattern in patterns))
        self.assertEqual(
            0, sum(len(pattern["activityEligibility"]) for pattern in patterns))

    def test_the_real_corpus_declares_the_solo_mode_and_no_later_stage(self):
        """The mode is now a real decision; the later stages are not."""
        corpus = self.real_corpus()
        patterns = [pattern for lemma in corpus["lemmas"]
                    for meaning in lemma["meanings"]
                    for pattern in meaning["patterns"]]
        self.assertEqual({SOLO_MAINTAINER_MODE},
                         {pattern["releaseMode"] for pattern in patterns})
        blob = json.dumps(corpus, ensure_ascii=False)
        for token in ("editorial-generated", "editorial-review",
                      "product-approval", "generatorRef", "reviewerRef",
                      "corroboratingActorRefs", "findings",
                      HUMAN_REVIEWED_MODE):
            with self.subTest(token=token):
                self.assertNotIn(token, blob)

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

    def test_only_the_reference_actor_was_named_and_no_author(self):
        """Phase 4F-A named the tier-1 workflow and stopped there.

        The tier-2 editorial actor is deliberately absent: registering it would
        be claiming a review the project has not performed, and its absence is
        what keeps every row at or below ``reference-verified``.
        """
        document = self.real_context_document()
        self.assertEqual({}, document["authorRegistry"])
        self.assertEqual({}, document["allocationRegistry"])
        actors = priority7_actors(document["editorialActorRegistry"])
        self.assertEqual({"priority7-reference-analysis"}, set(actors))
        record = actors["priority7-reference-analysis"]
        self.assertIs(False, record["human"])
        self.assertEqual(["reference-verification"], record["roles"])
        self.assertNotIn("editorial-review", record["roles"])
        self.assertNotIn("example-generation", record["roles"])

    def test_no_real_reference_or_product_authority_exists_yet(self):
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

    def test_the_real_corpus_still_fails_closed_against_the_new_gates(self):
        """The amended validator accepts the real corpus exactly as it stands."""
        corpus = self.real_corpus()
        document = self.real_context_document()
        issues = validate_editorial(corpus, ValidationContext(
            source_registry=document["sourceRegistry"],
            reviewer_registry=document["reviewerRegistry"],
            editorial_actor_registry=document["editorialActorRegistry"],
            repository_index=T.repository_index_from_root(ROOT),
            today=date(2026, 8, 14)))
        self.assertEqual([], issues, f"unexpected issues: {issues}")

    def test_dropping_the_reference_actor_registry_fails_the_real_corpus(self):
        """The acceptances genuinely depend on the registered nonhuman actor."""
        document = self.real_context_document()
        issues = validate_editorial(self.real_corpus(), ValidationContext(
            source_registry=document["sourceRegistry"],
            reviewer_registry=document["reviewerRegistry"],
            repository_index=T.repository_index_from_root(ROOT),
            today=date(2026, 8, 14)))
        self.assertIn("EDITORIAL_ACTOR_REGISTRY_DANGLING",
                      {issue.code for issue in issues})

    def test_the_five_example_slots_are_untouched(self):
        """§16: the amended model enables the next phase; it runs none of it."""
        corpus = self.real_corpus()
        examples = {
            example["id"]: example
            for lemma in corpus["lemmas"]
            for meaning in lemma["meanings"]
            for pattern in meaning["patterns"]
            for example in pattern.get("examples") or []}
        for example_id, expected in (
                ("vp-e-dziekowac-thank-dative-recipient-za-accusative-"
                 "thanks-for-cooperation-92656ebcc371",
                 "Dziękuję wszystkim za owocną współpracę."),
                ("vp-e-placic-pay-za-accusative-goods-"
                 "how-much-for-everything-dd5e5c88cfd4",
                 "Ile płacę za wszystko?"),
                ("vp-e-widziec-perceive-visually-accusative-object-"
                 "saw-your-sister-ec51af47f224",
                 "Widziałam wczoraj twoją siostrę.")):
            with self.subTest(example_id=example_id):
                self.assertEqual(expected, examples[example_id]["pl"])
                self.assertEqual(
                    "repository-reuse", examples[example_id]["origin"]["kind"])
        for pattern_id in (
                "vp-p-zajmowac-sie-look-after-person-instrumental-object-"
                "6f93facbd939",
                "vp-p-zalezec-depend-on-od-genitive-source-1ad29f7a1318"):
            with self.subTest(pattern_id=pattern_id):
                found = [pattern
                         for lemma in corpus["lemmas"]
                         for meaning in lemma["meanings"]
                         for pattern in meaning["patterns"]
                         if pattern["id"] == pattern_id]
                self.assertEqual(1, len(found))
                self.assertIsNone(found[0].get("examples"))

    def test_no_release_freeze_or_runtime_artifact_was_created(self):
        # Superseded by Priority 7 Phase 4F-I1, the release that materialised
        # the official runtime.  The only document that may occupy that path
        # is exactly the I1 release artifact, pinned by digest and revision,
        # and it may only exist alongside the matching shell and worker.
        self.assertEqual("complete", i1_bundle().state)
        for glob in ("*frozen*.json", "*release*.json", "*tombstone*.json"):
            for found in (ROOT / "editorial").glob(glob):
                self.fail(f"unexpected release artifact: {found}")

    def test_the_shipping_surface_is_unchanged(self):
        # Restated over the pre-Phase-4F-I1 shell and worker.
        index = pre_i1("index.html")
        worker = pre_i1("sw.js")
        self.assertIn('APP_VERSION = "8.10"', index)
        self.assertIn("popolsku-v65", worker)
        self.assertNotIn("verb-patterns.json", worker)
        loader = (ROOT / "pp-verb-patterns.js").read_text(encoding="utf-8")
        for token in ("releaseMode", "releaseAuthorization", "actorRef",
                      SOLO_MAINTAINER_MODE):
            with self.subTest(token=token):
                self.assertNotIn(token, loader)


if __name__ == "__main__":
    unittest.main()
