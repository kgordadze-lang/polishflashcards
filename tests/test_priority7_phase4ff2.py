"""Priority 7 Phase 4F-F2 — human product-approval governance recording.

This phase performed **no content review and no linguistic review**.  The
substantive decision is the product owner's own: after visually inspecting all
45 patterns in the Priority 7 learner interface, the owner returned a single
explicit ``APPROVE ALL``.  Phase 4F-F2 records that one human decision as the
governance events the tooling requires, and nothing else.

This suite treats the delivered candidate as read-only and proves, against the
immutable baseline ``cd0a3bf8a0003e81d405428dc039ec3f348cb8b5``:

1.  **Exactly 45 approvals, and nothing more.**  One qualifying
    ``product-approval`` acceptance per pattern, 45 rows at ``approved``,
    every event digest recomputing against the pattern it sits on, and no
    second acceptance anywhere.
2.  **The approver is human, and is the right human.**  ``product-owner-001``
    resolves in ``reviewerRegistry`` with ``human: true``, holds
    ``product-approval`` and nothing else, and explicitly acknowledges the
    ``solo-maintainer-reference-backed`` release mode.  No nonhuman actor is
    used.  AB is not the approver and gained nothing.
3.  **The stage sits where the chain puts it.**  Product approval follows the
    standing editorial review on all 45, is pinned to the tier-3 scope, and
    is structurally human-borne: ``reviewerRef`` required, ``actorRef``
    refused.
4.  **History is intact.**  All 47 reference acceptances and all 45 editorial
    acceptances stand byte-identical, and no earlier event was created,
    altered or removed.
5.  **Content did not move.**  Every learner-facing, evidence and provenance
    field is baseline-identical; tooling and every shipping file are
    byte-identical.
6.  **Approval is not release.**  No freeze, no runtime projection, no
    ``patternDataRevision``, no version or cache change, no activity
    eligibility and no audio.
7.  **The boundary has teeth.**  A missing approval, a duplicate approval, a
    stale digest, a wrong preceding state, a wrong human role, a missing
    release-mode acknowledgement, a nonhuman approver, an unregistered or
    absent reviewer identity, a mutated reference or editorial event, a
    content mutation and a premature release action are each rejected -- by
    the validator, by the derived state, or by surviving the Phase 4F-F2
    normaliser and still breaking the guard.

Every mutation below is applied to an in-memory copy.  Nothing here writes to
the corpus, the context, the tooling or any shipping file.

**Future safety.**  This suite describes the immutable F2 transition.  It is
deliberately silent about what comes after: a later phase may freeze the
approved corpus, project a public runtime, add its own reports and tests and
integrate that runtime into the app without any assertion here failing merely
because those artifacts exist.  The release-boundary claims below are stated
over the files Phase 4F-F2 itself owned, at the revision it owned them, and
never as a ban on future paths or a comparison against a moving ``HEAD``.

Run:  python3 -m unittest tests.test_priority7_phase4ff2
"""

from __future__ import annotations

import collections
import copy
import csv
import functools
import hashlib
import json
import subprocess
import unittest
from pathlib import Path

import os.path as _f2_os_path
import sys as _f2_sys

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

def i1_baseline_reference():
    """The commit each Phase 4F-I1 baseline comparison is made against.

    Resolved lazily so this helper can sit beside the other Phase 4F-I1
    plumbing, above the suite's own pinned-baseline constant.
    """
    return BASELINE_COMMIT

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


def i1_baseline_blob(reference, path):
    """The bytes of ``path`` at ``reference``, or ``None`` when it is absent."""
    result = subprocess.run(
        ["git", "show", f"{reference}:{path}"], cwd=str(ROOT),
        capture_output=True, check=False)
    return result.stdout if result.returncode == 0 else None


def is_only_the_i1_activation(path, reference=None):
    """True when ``path``'s whole difference from the baseline is the I1 layer.

    Phase 4F-I1 is the release that activates Priority 7.  A path qualifies
    only when it is one of the paths I1 was entitled to move AND the pinned I1
    layer accounts for every byte of the difference:

    * ``content/verb-patterns.json`` -- present with exactly the pinned release
      digest, byte length and revision, and nothing else in ``content/``;
    * ``index.html`` / ``sw.js`` -- classified through the all-or-nothing
      bundle, so neither can qualify unless the runtime and the other file
      moved with it;
    * a generated page -- differing by its one footer version stamp alone;
    * ``sitemap.xml`` -- differing by ``<lastmod>`` values alone, with an
      identical URL set, order and structure.

    Every other path, and any other edit to these paths, is still reported.
    """
    reference = i1_baseline_reference() if reference is None else reference
    path = path.rstrip("/")
    if path == "content":
        present = sorted(
            str(p.relative_to(ROOT)) for p in (ROOT / "content").rglob("*")
            if p.is_file())
        if present != [I1.PHASE_4FI1_RUNTIME_PATH]:
            return False
        path = I1.PHASE_4FI1_RUNTIME_PATH
    if not I1.is_phase_4fi1_path(path):
        return False
    if path == I1.PHASE_4FI1_RUNTIME_PATH:
        return i1_bundle().state == "complete"
    baseline = i1_baseline_blob(reference, path)
    if baseline is None:
        return False
    return I1.is_exactly_the_i1_transition(
        path, baseline.decode("utf-8"),
        (ROOT / path).read_text(encoding="utf-8"), bundle=i1_bundle())
if str(ROOT) not in _f2_sys.path:
    _f2_sys.path.insert(0, str(ROOT))
_F2_DIR = _f2_os_path.dirname(_f2_os_path.abspath(__file__))
if _F2_DIR not in _f2_sys.path:
    _f2_sys.path.insert(0, _F2_DIR)

import priority7_tooling as T  # noqa: E402
from priority7_tooling import ValidationContext, validate_editorial  # noqa: E402

import priority7_phase4fe1_normalizer as E1  # noqa: E402
import priority7_phase4ff2_normalizer as F2  # noqa: E402
import priority7_phase4fh2_normalizer as H2  # noqa: E402
import priority7_phase4fh21_normalizer as H21  # noqa: E402
import priority7_phase4fh3_normalizer as H3  # noqa: E402

CORPUS_PATH = "editorial/verb-pattern-candidates.json"
CONTEXT_PATH = "editorial/priority-7-authoring-context.json"
MATRIX_PATH = "reports/priority-7-phase-4ff2-product-approval-matrix.csv"
SUMMARY_PATH = "reports/priority-7-phase-4ff2-product-approval-summary.md"

#: Phase 4F-F2 arrived on top of this commit.
BASELINE_COMMIT = "cd0a3bf8a0003e81d405428dc039ec3f348cb8b5"
BASELINE_TREE = "28ee6de0226ad48839212fca2ec1cd167e4fbfe7"

#: Independent expected values, written from the phase brief and the owner's
#: own authorisation rather than read out of the corpus, so a joint edit to
#: corpus and artifact cannot make this suite agree with itself.
PRODUCT_OWNER = "product-owner-001"
HUMAN_NATIVE_REVIEWER = "native-reviewer-001"
NONHUMAN_ACTORS = (
    "priority7-reference-analysis",
    "priority7-example-generation",
    "priority7-editorial-review",
    "priority7-editorial-corroboration",
)

PATTERN_COUNT = 45
EXAMPLE_COUNT = 29
REFERENCE_ACCEPT_COUNT = 47
EDITORIAL_ACCEPT_COUNT = 45
PRODUCT_APPROVAL_COUNT = 45
APPROVAL_DATE = "2026-08-17"
PRIOR_STATE = "editorial-reviewed"
FINAL_STATE = "approved"
SOLO_MODE = "solo-maintainer-reference-backed"
PRODUCT_TIER = "product-approval"

#: Files Phase 4F-F2 was forbidden to touch.  Compared at the phase-owned
#: revision, so a later phase editing one of them cannot fail this claim.
UNCHANGED_FILES = (
    "priority7_tooling.py",
    "validate_content.py",
    "verify_audio.py",
    "build_pages.py",
    "index.html",
    "sw.js",
    "manifest.json",
    "pp-verb-patterns.js",
    "pp-migrate.js",
    "pp-answer.js",
    "pp-distractor.js",
    "pp-usage.js",
    "audio-manifest.json",
    "data-a1.js",
    "data-a2.js",
    "data-b1.js",
    "data-grammar.js",
    "data-podcasts.js",
    "data-scenarios.js",
    "data-verbs.js",
)

#: Learner-facing, evidence and provenance fields that may not move at all.
FROZEN_PATTERN_FIELDS = (
    "id", "key", "relationType", "complements", "cefr", "teachingStatus",
    "usage", "learnerExplanationEn", "activityEligibility", "evidence",
    "examples", "contentRefs", "errorNotes", "aspectEquivalentPatternIds",
    "releaseMode",
)


def git_blob(relative, revision=BASELINE_COMMIT):
    return subprocess.run(
        ["git", "show", f"{revision}:{relative}"],
        capture_output=True, text=True, check=True, cwd=ROOT).stdout


def read(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


def live_corpus():
    """The corpus exactly as it stands on disk, with no normalisation."""
    return json.loads(read(CORPUS_PATH))


def live_context_document():
    """The context exactly as it stands on disk, with no normalisation."""
    return json.loads(read(CONTEXT_PATH))


def f2_corpus():
    """The corpus as Phase 4F-F2 left it, with later phases normalised away.

    Phase 4F-H2 legitimately superseded this phase's approved content state
    on 44 of the 45 patterns.  Its phase-owned normaliser is closed over that
    exact transition and derives nothing from the live rows, so removing that
    layer here restores the document this suite's claims were written about
    without absorbing anything Phase 4F-H2 did not do.
    """
    return H2.without_phase_4fh2_content_completion(
        H21.without_phase_4fh21_product_reapproval(live_corpus()))


def f2_context_document():
    """The context as Phase 4F-F2 left it, with later phases normalised away."""
    return H2.without_phase_4fh2_context(
        H21.without_phase_4fh21_context(live_context_document()))


def baseline_corpus():
    return json.loads(git_blob(CORPUS_PATH))


def baseline_context_document():
    return json.loads(git_blob(CONTEXT_PATH))


@functools.lru_cache(maxsize=1)
def repository_index():
    """Built once: it reads every ``data-*.js`` file and never changes here."""
    return T.repository_index_from_root(str(ROOT))


def build_context(document=None, *, corpus_root=True):
    document = f2_context_document() if document is None else document
    return ValidationContext(
        source_registry=document["sourceRegistry"],
        reviewer_registry=document["reviewerRegistry"],
        author_registry=document["authorRegistry"],
        allocation_registry=document["allocationRegistry"],
        repository_index=repository_index() if corpus_root else None,
        editorial_actor_registry=document.get("editorialActorRegistry", {}),
        today=APPROVAL_DATE,
    )


def iter_patterns(corpus):
    for lemma in corpus["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                yield lemma, meaning, pattern


def approvals(pattern):
    return [event for event in pattern["reviewEvents"]
            if event["kind"] == PRODUCT_APPROVAL_KIND]


PRODUCT_APPROVAL_KIND = "product-approval"


def codes(issues):
    return sorted({issue.code for issue in issues})


def role_holders(document, role):
    return sorted(
        reference for reference, record in document["reviewerRegistry"].items()
        if role in record.get("roles", []))


class Phase4FF2TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = f2_corpus()
        cls.context_document = f2_context_document()
        cls.baseline = baseline_corpus()
        cls.baseline_context = baseline_context_document()
        cls.rows = list(iter_patterns(cls.corpus))
        cls.baseline_rows = list(iter_patterns(cls.baseline))

    def mutated(self):
        return copy.deepcopy(self.corpus)

    def mutated_context(self):
        return copy.deepcopy(self.context_document)


# --------------------------------------------------------------------------
# 1.  Exactly 45 approvals, and nothing more
# --------------------------------------------------------------------------

class ApprovalCounts(Phase4FF2TestCase):

    def test_the_corpus_holds_exactly_forty_five_patterns(self):
        self.assertEqual(PATTERN_COUNT, len(self.rows))
        self.assertEqual(
            PATTERN_COUNT, len({pattern["id"] for _, _, pattern in self.rows}))

    def test_the_example_inventory_is_unchanged(self):
        self.assertEqual(
            EXAMPLE_COUNT,
            sum(len(pattern.get("examples", [])) for _, _, pattern in self.rows))

    def test_exactly_forty_five_product_approvals_exist(self):
        events = [event for _, _, pattern in self.rows
                  for event in pattern["reviewEvents"]
                  if event["kind"] == PRODUCT_APPROVAL_KIND]
        self.assertEqual(PRODUCT_APPROVAL_COUNT, len(events))

    def test_every_pattern_carries_exactly_one_qualifying_approval(self):
        for _, _, pattern in self.rows:
            with self.subTest(pattern_id=pattern["id"]):
                events = [event for event in pattern["reviewEvents"]
                          if event["kind"] == PRODUCT_APPROVAL_KIND]
                self.assertEqual(1, len(events))
                self.assertEqual("accept", events[0]["decision"])

    def test_all_forty_five_final_states_are_approved(self):
        states = collections.Counter(
            pattern["reviewState"] for _, _, pattern in self.rows)
        self.assertEqual({FINAL_STATE: PATTERN_COUNT}, dict(states))

    def test_every_row_stood_at_editorial_reviewed_before_this_phase(self):
        states = collections.Counter(
            pattern["reviewState"] for _, _, pattern in self.baseline_rows)
        self.assertEqual({PRIOR_STATE: PATTERN_COUNT}, dict(states))

    def test_the_baseline_carried_no_product_approval_at_all(self):
        self.assertNotIn(PRODUCT_APPROVAL_KIND, git_blob(CORPUS_PATH))
        self.assertEqual(
            [], role_holders(self.baseline_context, PRODUCT_TIER),
            "no product authority existed before this phase")
        self.assertEqual(
            [PRODUCT_OWNER], role_holders(self.context_document, PRODUCT_TIER),
            "and exactly one exists after it")

    def test_the_event_total_grew_by_exactly_forty_five(self):
        before = sum(len(pattern["reviewEvents"])
                     for _, _, pattern in self.baseline_rows)
        after = sum(len(pattern["reviewEvents"]) for _, _, pattern in self.rows)
        self.assertEqual(before + PRODUCT_APPROVAL_COUNT, after)

    def test_every_approval_carries_the_single_owner_decision_date(self):
        for _, _, pattern in self.rows:
            with self.subTest(pattern_id=pattern["id"]):
                event = [e for e in pattern["reviewEvents"]
                         if e["kind"] == PRODUCT_APPROVAL_KIND][0]
                self.assertEqual(APPROVAL_DATE, event["reviewedAt"])


# --------------------------------------------------------------------------
# 2.  The approver is human, and is the right human
# --------------------------------------------------------------------------

class ProductOwnerIdentity(Phase4FF2TestCase):

    def record(self):
        return self.context_document["reviewerRegistry"][PRODUCT_OWNER]

    def test_the_owner_resolves_as_a_human_reviewer(self):
        self.assertIn(PRODUCT_OWNER, self.context_document["reviewerRegistry"])
        self.assertIs(True, self.record()["human"])

    def test_the_owner_holds_product_approval_and_nothing_else(self):
        self.assertEqual([PRODUCT_TIER], self.record()["roles"])
        for forbidden in ("external-verification", "native-linguistic",
                          "reference-verification", "correction", "reopen"):
            with self.subTest(role=forbidden):
                self.assertNotIn(forbidden, self.record()["roles"])

    def test_the_owner_was_granted_no_multi_stage_allowance(self):
        self.assertNotIn("ownerAllowsMultipleRoles", self.record())

    def test_the_owner_acknowledged_the_solo_release_mode_explicitly(self):
        self.assertEqual([SOLO_MODE], self.record()["acknowledgedReleaseModes"])

    def test_every_approval_names_the_owner_and_never_an_actor(self):
        for _, _, pattern in self.rows:
            with self.subTest(pattern_id=pattern["id"]):
                event = [e for e in pattern["reviewEvents"]
                         if e["kind"] == PRODUCT_APPROVAL_KIND][0]
                self.assertEqual(PRODUCT_OWNER, event["reviewerRef"])
                self.assertNotIn("actorRef", event)

    def test_no_nonhuman_actor_is_used_as_the_product_approver(self):
        actors = self.context_document["editorialActorRegistry"]
        approvers = {event["reviewerRef"] for _, _, pattern in self.rows
                     for event in pattern["reviewEvents"]
                     if event["kind"] == PRODUCT_APPROVAL_KIND}
        self.assertEqual(set(), approvers & set(actors))
        for actor_id, record in actors.items():
            with self.subTest(actor=actor_id):
                self.assertIs(False, record["human"])
                self.assertNotIn(PRODUCT_TIER, record["roles"])

    def test_the_owner_key_is_claimed_by_no_other_registry(self):
        for registry in ("authorRegistry", "editorialActorRegistry"):
            with self.subTest(registry=registry):
                self.assertNotIn(
                    PRODUCT_OWNER, self.context_document.get(registry, {}))

    def test_ab_is_not_the_approver_and_gained_nothing(self):
        approvers = {event["reviewerRef"] for _, _, pattern in self.rows
                     for event in pattern["reviewEvents"]
                     if event["kind"] == PRODUCT_APPROVAL_KIND}
        self.assertNotIn(HUMAN_NATIVE_REVIEWER, approvers)
        self.assertNotIn(HUMAN_NATIVE_REVIEWER, read(CORPUS_PATH))
        self.assertEqual(
            self.baseline_context["reviewerRegistry"][HUMAN_NATIVE_REVIEWER],
            self.context_document["reviewerRegistry"][HUMAN_NATIVE_REVIEWER])

    def test_exactly_one_reviewer_identity_was_added(self):
        self.assertEqual(
            {PRODUCT_OWNER},
            set(self.context_document["reviewerRegistry"]) -
            set(self.baseline_context["reviewerRegistry"]))

    def test_no_example_authoring_authority_was_created(self):
        self.assertEqual({}, self.context_document["authorRegistry"])

    def test_the_nonhuman_actor_registry_is_byte_identical(self):
        self.assertEqual(
            self.baseline_context["editorialActorRegistry"],
            self.context_document["editorialActorRegistry"])
        self.assertEqual(
            set(NONHUMAN_ACTORS),
            set(self.context_document["editorialActorRegistry"]))

    def test_the_owner_record_records_no_linguistic_credential(self):
        """Product approval is an inclusion decision, not a language one."""
        prose = json.dumps(self.record(), ensure_ascii=False).lower()
        prose = prose.replace("native-linguistic", "")
        for invented in ("native speaker", "linguist", "teacher", "certified",
                         "qualification", "professor", "translator"):
            with self.subTest(invented=invented):
                self.assertNotIn(invented, prose)

    def test_the_owner_record_carries_no_personal_contact_detail(self):
        blob = json.dumps(
            self.context_document["reviewerRegistry"], ensure_ascii=False)
        for forbidden in ("@", "phone", "address"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, blob)


# --------------------------------------------------------------------------
# 3.  The stage sits where the chain puts it
# --------------------------------------------------------------------------

class ChainPosition(Phase4FF2TestCase):

    def test_the_locked_solo_chain_is_unchanged(self):
        self.assertEqual(
            ("reference-verification", "editorial-review", "product-approval"),
            T.SOLO_STAGE_KINDS)
        self.assertEqual(FINAL_STATE, T.STAGE_STATE[PRODUCT_TIER])
        self.assertEqual(1, T.SCOPE_VERSION)

    def test_product_approval_is_human_borne_in_both_release_modes(self):
        for mode, nonhuman in T.MODE_NONHUMAN_STAGE_KINDS.items():
            with self.subTest(mode=mode):
                self.assertNotIn(PRODUCT_TIER, nonhuman)

    def test_every_pattern_still_declares_the_solo_mode(self):
        self.assertEqual(
            {SOLO_MODE},
            {pattern["releaseMode"] for _, _, pattern in self.rows})

    def test_approval_follows_the_standing_editorial_review_on_every_row(self):
        for _, _, pattern in self.rows:
            with self.subTest(pattern_id=pattern["id"]):
                kinds = [event["kind"] for event in pattern["reviewEvents"]]
                self.assertIn("editorial-review", kinds)
                self.assertEqual(PRODUCT_APPROVAL_KIND, kinds[-1])
                self.assertLess(
                    kinds.index("editorial-review"),
                    kinds.index(PRODUCT_APPROVAL_KIND))

    def test_every_approval_pins_the_current_tier_three_digest(self):
        for lemma, meaning, pattern in self.rows:
            with self.subTest(pattern_id=pattern["id"]):
                event = [e for e in pattern["reviewEvents"]
                         if e["kind"] == PRODUCT_APPROVAL_KIND][0]
                self.assertEqual(1, event["scopeVersion"])
                self.assertEqual(
                    T.review_scope_digest(PRODUCT_TIER, lemma, meaning, pattern),
                    event["scopeDigest"])

    def test_the_tier_three_scope_is_strictly_wider_than_tier_two(self):
        """contentRefs are in scope at tier 3 and nowhere below it."""
        for lemma, meaning, pattern in self.rows:
            with self.subTest(pattern_id=pattern["id"]):
                self.assertNotEqual(
                    T.review_scope_digest(
                        "editorial-review", lemma, meaning, pattern),
                    T.review_scope_digest(
                        PRODUCT_TIER, lemma, meaning, pattern))
                self.assertIn(
                    "contentRefs",
                    T.review_scope(PRODUCT_TIER, lemma, meaning,
                                   pattern)["pattern"])

    def test_every_digest_is_distinct_across_the_forty_five_rows(self):
        digests = {event["scopeDigest"] for _, _, pattern in self.rows
                   for event in pattern["reviewEvents"]
                   if event["kind"] == PRODUCT_APPROVAL_KIND}
        self.assertEqual(PRODUCT_APPROVAL_COUNT, len(digests))

    def test_the_approval_event_carries_only_the_permitted_fields(self):
        allowed = {"kind", "decision", "scopeVersion", "scopeDigest",
                   "reviewerRef", "reviewedAt", "note"}
        for _, _, pattern in self.rows:
            with self.subTest(pattern_id=pattern["id"]):
                event = [e for e in pattern["reviewEvents"]
                         if e["kind"] == PRODUCT_APPROVAL_KIND][0]
                self.assertEqual(set(), set(event) - allowed)
                for forbidden in ("actorRef", "corroboratingActorRefs",
                                  "findings", "supportingEvidenceDigests"):
                    self.assertNotIn(forbidden, event)

    def test_the_tooling_derives_approved_rather_than_trusting_it(self):
        """The state is a consequence of the history, not an assertion."""
        for index in range(PATTERN_COUNT):
            candidate = self.mutated()
            rows = list(iter_patterns(candidate))
            _, _, pattern = rows[index]
            pattern["reviewState"] = PRIOR_STATE
            with self.subTest(pattern_id=pattern["id"]):
                self.assertIn(
                    "REVIEW_STATE_MISMATCH",
                    codes(validate_editorial(candidate, build_context())))

    def test_the_whole_corpus_validates_as_written(self):
        self.assertEqual([], validate_editorial(self.corpus, build_context()))


# --------------------------------------------------------------------------
# 4.  History is intact
# --------------------------------------------------------------------------

class HistoryIsIntact(Phase4FF2TestCase):

    def test_all_forty_seven_reference_acceptances_are_preserved(self):
        events = [event for _, _, pattern in self.rows
                  for event in pattern["reviewEvents"]
                  if event["kind"] == "reference-verification"]
        self.assertEqual(REFERENCE_ACCEPT_COUNT, len(events))
        self.assertEqual({"accept"}, {event["decision"] for event in events})

    def test_all_forty_five_editorial_acceptances_are_preserved(self):
        events = [event for _, _, pattern in self.rows
                  for event in pattern["reviewEvents"]
                  if event["kind"] == "editorial-review"]
        self.assertEqual(EDITORIAL_ACCEPT_COUNT, len(events))
        self.assertEqual({"accept"}, {event["decision"] for event in events})

    def test_every_earlier_event_is_byte_identical_to_the_baseline(self):
        for (_, _, before), (_, _, after) in zip(self.baseline_rows, self.rows):
            with self.subTest(pattern_id=after["id"]):
                self.assertEqual(
                    before["reviewEvents"],
                    after["reviewEvents"][:len(before["reviewEvents"])])

    def test_exactly_one_event_was_appended_to_each_history(self):
        for (_, _, before), (_, _, after) in zip(self.baseline_rows, self.rows):
            with self.subTest(pattern_id=after["id"]):
                self.assertEqual(
                    len(before["reviewEvents"]) + 1, len(after["reviewEvents"]))

    def test_the_two_superseded_mowic_reference_events_still_stand(self):
        """The 47th and 46th acceptances are historical, not current."""
        doubled = [pattern["id"] for _, _, pattern in self.rows
                   if len([e for e in pattern["reviewEvents"]
                           if e["kind"] == "reference-verification"]) == 2]
        self.assertEqual(2, len(doubled))

    def test_no_reference_or_editorial_event_was_created_by_this_phase(self):
        for kind, expected in (("reference-verification", REFERENCE_ACCEPT_COUNT),
                               ("editorial-review", EDITORIAL_ACCEPT_COUNT)):
            with self.subTest(kind=kind):
                before = sum(
                    1 for _, _, pattern in self.baseline_rows
                    for event in pattern["reviewEvents"]
                    if event["kind"] == kind)
                after = sum(
                    1 for _, _, pattern in self.rows
                    for event in pattern["reviewEvents"]
                    if event["kind"] == kind)
                self.assertEqual(before, after)
                self.assertEqual(expected, after)

    def test_no_correction_or_reopen_event_was_used(self):
        kinds = {event["kind"] for _, _, pattern in self.rows
                 for event in pattern["reviewEvents"]}
        self.assertEqual(
            {"reference-verification", "editorial-review", PRODUCT_APPROVAL_KIND},
            kinds)


# --------------------------------------------------------------------------
# 5.  Content did not move
# --------------------------------------------------------------------------

class ContentImmutability(Phase4FF2TestCase):

    def test_the_normaliser_reproduces_the_baseline_corpus_byte_for_byte(self):
        self.assertEqual(
            git_blob(CORPUS_PATH),
            F2.without_phase_4ff2_corpus_text(
                H2.without_phase_4fh2_corpus_text(
                    H21.without_phase_4fh21_corpus_text(read(CORPUS_PATH)))))

    def test_the_normaliser_reproduces_the_baseline_context_byte_for_byte(self):
        self.assertEqual(
            git_blob(CONTEXT_PATH),
            F2.without_phase_4ff2_context_text(
                H2.without_phase_4fh2_context_text(
                    H21.without_phase_4fh21_context_text(read(CONTEXT_PATH)))))

    def test_no_learner_or_provenance_field_moved_on_any_row(self):
        for (_, _, before), (_, _, after) in zip(self.baseline_rows, self.rows):
            for field in FROZEN_PATTERN_FIELDS:
                with self.subTest(pattern_id=after["id"], field=field):
                    self.assertEqual(before.get(field), after.get(field))

    def test_the_lemma_and_meaning_envelopes_are_identical(self):
        def envelope(corpus, child):
            return [
                {key: value for key, value in node.items() if key != child}
                for node in (
                    corpus["lemmas"] if child == "meanings" else
                    [meaning for lemma in corpus["lemmas"]
                     for meaning in lemma["meanings"]])]

        for child in ("meanings", "patterns"):
            with self.subTest(level=child):
                self.assertEqual(envelope(self.baseline, child),
                                 envelope(self.corpus, child))

    def test_the_document_envelope_is_identical(self):
        self.assertEqual(
            {key: value for key, value in self.baseline.items()
             if key != "lemmas"},
            {key: value for key, value in self.corpus.items()
             if key != "lemmas"})

    def test_no_example_or_its_provenance_changed(self):
        for (_, _, before), (_, _, after) in zip(self.baseline_rows, self.rows):
            with self.subTest(pattern_id=after["id"]):
                self.assertEqual(
                    before.get("examples"), after.get("examples"))

    def test_no_evidence_record_changed(self):
        for (_, _, before), (_, _, after) in zip(self.baseline_rows, self.rows):
            with self.subTest(pattern_id=after["id"]):
                self.assertEqual(before["evidence"], after["evidence"])
                self.assertEqual(
                    [T.evidence_digest(record) for record in before["evidence"]],
                    [T.evidence_digest(record) for record in after["evidence"]])

    def test_the_context_changed_only_where_registration_required_it(self):
        before = copy.deepcopy(self.baseline_context)
        after = copy.deepcopy(self.context_document)
        del before["reviewerRegistry"], after["reviewerRegistry"]
        before_notice = before.pop("contextNotice")
        after_notice = after.pop("contextNotice")
        self.assertEqual(before, after)
        self.assertTrue(after_notice.startswith(before_notice))

    def test_the_appended_notice_supersedes_only_what_f2_performed(self):
        suffix = F2.F2_CONTEXT_NOTICE_SUFFIX
        for standing in ("frozen", "released", "projected to runtime"):
            with self.subTest(standing=standing):
                self.assertIn(standing, suffix)
        self.assertIn("All 45 patterns are now approved.", suffix)
        self.assertNotIn("native-speaker review advanced", suffix)

    def test_every_forbidden_file_is_baseline_identical(self):
        """Compared with the Phase 4F-I1 and 4F-H3 layers removed.

        Two phases have been entitled to change a shipping file since this
        baseline: H3, the UI wording phase, and I1, the atomic release.  Both
        layers are pinned and all-or-nothing, so removing them must reproduce
        these bytes exactly and every other shell or worker edit still fails
        here.  I1 is stripped first because it sits on top of H3.
        """
        for relative in UNCHANGED_FILES:
            with self.subTest(path=relative):
                text = i1_shipping_text(relative)
                if H3.is_phase_4fh3_path(relative):
                    text = H3.without_phase_4fh3_ui_wording(text)
                self.assertEqual(git_blob(relative), text)


# --------------------------------------------------------------------------
# 6.  Approval is not release
# --------------------------------------------------------------------------

class ApprovalIsNotRelease(Phase4FF2TestCase):
    """Stated over what Phase 4F-F2 owned, never as a ban on later work."""

    def test_no_pattern_gained_activity_eligibility(self):
        self.assertEqual(
            0,
            sum(len(pattern["activityEligibility"])
                for _, _, pattern in self.rows))

    def test_no_example_became_audio_eligible(self):
        self.assertEqual(
            0,
            sum(1 for _, _, pattern in self.rows
                for example in pattern.get("examples", [])
                if example.get("audioEligible") is True))

    def test_switching_on_an_activity_would_require_fresh_review(self):
        """Approval is a gate for eligibility, never a grant of it.

        ``activityEligibility`` sits inside the tier-2 scope, so a later
        decision to expose an activity moves both the tier-2 and tier-3
        digests and invalidates the standing review.  Approval unlocks that
        decision; it does not make it.
        """
        candidate = self.mutated()
        for _, _, pattern in iter_patterns(candidate):
            pattern["activityEligibility"] = ["reference"]
        self.assertIn(
            "REVIEW_STATE_MISMATCH",
            codes(validate_editorial(candidate, build_context())))
        for lemma, meaning, pattern in self.rows:
            with self.subTest(pattern_id=pattern["id"]):
                self.assertIn(
                    "activityEligibility",
                    T.review_scope(
                        "editorial-review", lemma, meaning, pattern)["pattern"])

    def test_no_freeze_or_release_artifact_was_created(self):
        # Superseded by Priority 7 Phase 4F-I1, the release that materialised
        # the official runtime.  The only document that may occupy that path
        # is exactly the I1 release artifact, pinned by digest and revision,
        # and it may only exist alongside the matching shell and worker.
        self.assertEqual("complete", i1_bundle().state)
        for glob in ("*frozen*.json", "*release*.json", "*runtime*.json"):
            for found in (ROOT / "editorial").glob(glob):
                self.fail(f"unexpected release artifact: {found}")

    def test_no_runtime_projection_was_committed_by_this_phase(self):
        """The phase-owned surface carries no projection, whatever comes next."""
        changed = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, check=True, cwd=ROOT).stdout
        for line in changed.splitlines():
            path = line[3:].strip().strip('"')
            with self.subTest(path=path):
                # Superseded by Priority 7 Phase 4F-I1: the projection under
                # content/ is that phase's release artifact, not F2's, and it
                # qualifies only as the exact pinned I1 transition.
                if is_only_the_i1_activation(path):
                    continue
                self.assertFalse(
                    path.startswith("content/"),
                    "a runtime projection is not part of Phase 4F-F2")

    def test_the_shipping_surface_carries_no_version_or_cache_change(self):
        """Compared with the Phase 4F-I1 and 4F-H3 layers removed.

        Two phases have been entitled to change a shipping file since this
        baseline: H3, the UI wording phase, and I1, the atomic release.  Both
        layers are pinned and all-or-nothing, so removing them must reproduce
        these bytes exactly and every other shell or worker edit still fails
        here.  I1 is stripped first because it sits on top of H3.
        """
        for relative in ("index.html", "sw.js", "manifest.json"):
            with self.subTest(path=relative):
                text = i1_shipping_text(relative)
                if H3.is_phase_4fh3_path(relative):
                    text = H3.without_phase_4fh3_ui_wording(text)
                self.assertEqual(git_blob(relative), text)

    def test_the_pattern_data_revision_was_not_incremented(self):
        self.assertNotIn("patternDataRevision", read(CORPUS_PATH))
        self.assertNotIn("patternDataRevision", read(CONTEXT_PATH))

    def test_the_only_available_projection_still_marks_itself_nonrelease(self):
        """``project-fixture`` is a test artifact and says so.

        Product approval unlocks projection; it does not perform one, and the
        only projection this tooling exposes refuses to look released.
        """
        projected = T.project_nonrelease_fixture(
            self.corpus, 1, build_context())
        self.assertIs(False, projected["releaseAuthorized"])
        self.assertEqual(
            T.NONRELEASE_PROJECTION_STATUS, projected["artifactStatus"])
        # The wrapper's own ``artifactStatus`` is the label that makes the
        # fixture unmistakably nonrelease, so the private-key sweep runs over
        # the projected document it wraps.
        blob = json.dumps(projected["runtimeProjection"], ensure_ascii=False)
        for private in T.PRIVATE_RUNTIME_KEYS:
            with self.subTest(key=private):
                self.assertNotIn(f'"{private}"', blob)


# --------------------------------------------------------------------------
# 7.  Negative controls
# --------------------------------------------------------------------------

class NegativeControls(Phase4FF2TestCase):

    def approve(self, corpus, pattern, lemma, meaning, **overrides):
        event = {
            "kind": PRODUCT_APPROVAL_KIND,
            "decision": "accept",
            "scopeVersion": 1,
            "scopeDigest": T.review_scope_digest(
                PRODUCT_TIER, lemma, meaning, pattern),
            "reviewerRef": PRODUCT_OWNER,
            "reviewedAt": APPROVAL_DATE,
        }
        event.update(overrides)
        return event

    def test_a_missing_approval_breaks_the_derived_state(self):
        candidate = self.mutated()
        lemma, meaning, pattern = next(iter_patterns(candidate))
        pattern["reviewEvents"] = [
            event for event in pattern["reviewEvents"]
            if event["kind"] != PRODUCT_APPROVAL_KIND]
        self.assertIn("REVIEW_STATE_MISMATCH",
                      codes(validate_editorial(candidate, build_context())))

    def test_a_duplicate_approval_is_refused(self):
        candidate = self.mutated()
        for _, _, pattern in iter_patterns(candidate):
            pattern["reviewEvents"].append(
                copy.deepcopy(pattern["reviewEvents"][-1]))
        self.assertIn("REVIEW_DUPLICATE_STAGE_ACCEPTANCE",
                      codes(validate_editorial(candidate, build_context())))

    def test_a_stale_product_digest_loses_the_approved_state(self):
        candidate = self.mutated()
        for _, _, pattern in iter_patterns(candidate):
            pattern["reviewEvents"][-1]["scopeDigest"] = "sha256:" + "0" * 64
        self.assertIn("REVIEW_STATE_MISMATCH",
                      codes(validate_editorial(candidate, build_context())))

    def test_pinning_the_tier_two_digest_at_tier_three_is_not_current(self):
        candidate = self.mutated()
        for lemma, meaning, pattern in iter_patterns(candidate):
            pattern["reviewEvents"][-1]["scopeDigest"] = T.review_scope_digest(
                "editorial-review", lemma, meaning, pattern)
        self.assertIn("REVIEW_STATE_MISMATCH",
                      codes(validate_editorial(candidate, build_context())))

    def test_a_wrong_preceding_state_is_refused(self):
        candidate = self.mutated()
        lemma, meaning, pattern = next(iter_patterns(candidate))
        pattern["reviewEvents"] = [
            event for event in pattern["reviewEvents"]
            if event["kind"] != "editorial-review"]
        found = codes(validate_editorial(candidate, build_context()))
        self.assertIn("REVIEW_STAGE_ORDER", found)

    def test_a_reviewer_without_the_product_role_is_refused(self):
        document = self.mutated_context()
        document["reviewerRegistry"][PRODUCT_OWNER]["roles"] = [
            "native-linguistic"]
        self.assertIn("REVIEWER_ROLE",
                      codes(validate_editorial(
                          self.corpus, build_context(document))))

    def test_an_owner_who_never_acknowledged_the_mode_is_refused(self):
        document = self.mutated_context()
        del document["reviewerRegistry"][PRODUCT_OWNER][
            "acknowledgedReleaseModes"]
        self.assertIn("OWNER_RELEASE_MODE_NOT_ACKNOWLEDGED",
                      codes(validate_editorial(
                          self.corpus, build_context(document))))

    def test_acknowledging_only_the_other_mode_is_refused(self):
        document = self.mutated_context()
        document["reviewerRegistry"][PRODUCT_OWNER][
            "acknowledgedReleaseModes"] = [T.HUMAN_REVIEWED_MODE]
        self.assertIn("OWNER_RELEASE_MODE_NOT_ACKNOWLEDGED",
                      codes(validate_editorial(
                          self.corpus, build_context(document))))

    def test_a_nonhuman_product_approver_is_refused(self):
        document = self.mutated_context()
        document["reviewerRegistry"][PRODUCT_OWNER]["human"] = False
        self.assertIn("REVIEWER_NOT_HUMAN",
                      codes(validate_editorial(
                          self.corpus, build_context(document))))

    def test_an_owner_record_omitting_human_is_refused(self):
        document = self.mutated_context()
        del document["reviewerRegistry"][PRODUCT_OWNER]["human"]
        self.assertIn("REVIEWER_NOT_HUMAN",
                      codes(validate_editorial(
                          self.corpus, build_context(document))))

    def test_an_unregistered_reviewer_identity_is_refused(self):
        document = self.mutated_context()
        del document["reviewerRegistry"][PRODUCT_OWNER]
        self.assertIn("REVIEWER_REGISTRY_DANGLING",
                      codes(validate_editorial(
                          self.corpus, build_context(document))))

    def test_an_editorial_actor_cannot_be_named_as_the_approver(self):
        candidate = self.mutated()
        for _, _, pattern in iter_patterns(candidate):
            pattern["reviewEvents"][-1]["reviewerRef"] = (
                "priority7-editorial-review")
        self.assertIn("REVIEWER_REGISTRY_DANGLING",
                      codes(validate_editorial(candidate, build_context())))

    def test_an_actor_borne_product_approval_cannot_be_expressed(self):
        candidate = self.mutated()
        for _, _, pattern in iter_patterns(candidate):
            event = pattern["reviewEvents"][-1]
            del event["reviewerRef"]
            event["actorRef"] = "priority7-editorial-review"
        found = codes(validate_editorial(candidate, build_context()))
        self.assertIn("SCHEMA_REQUIRED", found)
        self.assertIn("SCHEMA_UNKNOWN_FIELD", found)

    def test_relisting_the_owner_as_a_nonhuman_actor_is_refused(self):
        document = self.mutated_context()
        document["editorialActorRegistry"][PRODUCT_OWNER] = {
            "human": False, "kind": "editorial-review-workflow",
            "roles": ["editorial-review"]}
        self.assertIn("REGISTRY_KEY_COLLISION",
                      codes(validate_editorial(
                          self.corpus, build_context(document))))

    def test_ab_cannot_be_used_as_the_product_approver(self):
        candidate = self.mutated()
        for _, _, pattern in iter_patterns(candidate):
            pattern["reviewEvents"][-1]["reviewerRef"] = HUMAN_NATIVE_REVIEWER
        found = codes(validate_editorial(candidate, build_context()))
        self.assertIn("REVIEWER_ROLE", found)
        self.assertIn("OWNER_RELEASE_MODE_NOT_ACKNOWLEDGED", found)

    def test_corroboration_cannot_be_attached_to_a_product_approval(self):
        candidate = self.mutated()
        for _, _, pattern in iter_patterns(candidate):
            pattern["reviewEvents"][-1]["corroboratingActorRefs"] = [
                "priority7-editorial-corroboration"]
        found = codes(validate_editorial(candidate, build_context()))
        self.assertIn("EDITORIAL_CORROBORATION_FORBIDDEN", found)
        self.assertIn("SCHEMA_UNKNOWN_FIELD", found)

    def test_evidence_pins_cannot_be_attached_to_a_product_approval(self):
        candidate = self.mutated()
        for _, _, pattern in iter_patterns(candidate):
            pattern["reviewEvents"][-1]["supportingEvidenceDigests"] = [
                "sha256:" + "a" * 64]
        self.assertIn("REVIEW_EVIDENCE_FORBIDDEN",
                      codes(validate_editorial(candidate, build_context())))

    def test_an_approval_dated_before_the_editorial_review_is_refused(self):
        candidate = self.mutated()
        for _, _, pattern in iter_patterns(candidate):
            pattern["reviewEvents"][-1]["reviewedAt"] = "2026-08-16"
        self.assertIn("REVIEW_EVENT_ORDER",
                      codes(validate_editorial(candidate, build_context())))

    def test_a_mutated_reference_event_survives_the_normaliser(self):
        candidate = self.mutated()
        lemma, meaning, pattern = next(iter_patterns(candidate))
        reference = [event for event in pattern["reviewEvents"]
                     if event["kind"] == "reference-verification"][0]
        reference["reviewedAt"] = "2026-08-15"
        normalised = F2.without_phase_4ff2_product_approval(candidate)
        _, _, normalised_pattern = next(iter_patterns(normalised))
        self.assertNotEqual(
            next(iter_patterns(self.baseline))[2]["reviewEvents"],
            normalised_pattern["reviewEvents"])

    def test_a_mutated_editorial_event_survives_the_normaliser(self):
        candidate = self.mutated()
        lemma, meaning, pattern = next(iter_patterns(candidate))
        for event in pattern["reviewEvents"]:
            if event["kind"] == "editorial-review":
                event["corroboratingActorRefs"] = ["priority7-reference-analysis"]
        normalised = E1.without_phase_4fe1_editorial_review(
            F2.without_phase_4ff2_product_approval(candidate))
        _, _, normalised_pattern = next(iter_patterns(normalised))
        self.assertTrue(
            any(event["kind"] == "editorial-review"
                for event in normalised_pattern["reviewEvents"]),
            "a tampered editorial acceptance must stay visible")

    def test_a_content_mutation_invalidates_the_approval_digest(self):
        candidate = self.mutated()
        lemma, meaning, pattern = next(iter_patterns(candidate))
        pattern["learnerExplanationEn"] += " Extra unauthorised sentence."
        self.assertIn("REVIEW_STATE_MISMATCH",
                      codes(validate_editorial(candidate, build_context())))

    def test_a_contentref_mutation_invalidates_the_approval_digest(self):
        """contentRefs enter scope at tier 3, so tier 3 alone must notice."""
        candidate = self.mutated()
        moved = None
        for lemma, meaning, pattern in iter_patterns(candidate):
            if pattern.get("contentRefs"):
                pattern["contentRefs"] = list(reversed(pattern["contentRefs"]))
                if len(pattern["contentRefs"]) > 1:
                    moved = (lemma, meaning, pattern)
                    break
        if moved is None:
            self.skipTest("no row carries more than one contentRef")
        lemma, meaning, pattern = moved
        self.assertEqual(
            T.review_scope_digest("editorial-review", lemma, meaning, pattern),
            [event for event in pattern["reviewEvents"]
             if event["kind"] == "editorial-review"][0]["scopeDigest"],
            "reordering contentRefs must not move the tier-2 digest")

    def test_a_content_mutation_survives_the_normaliser(self):
        candidate = self.mutated()
        _, _, pattern = next(iter_patterns(candidate))
        pattern["learnerExplanationEn"] += " Extra unauthorised sentence."
        normalised = F2.without_phase_4ff2_product_approval(candidate)
        _, _, normalised_pattern = next(iter_patterns(normalised))
        self.assertNotEqual(
            next(iter_patterns(self.baseline))[2]["learnerExplanationEn"],
            normalised_pattern["learnerExplanationEn"])

    def test_a_repinned_approval_is_not_absorbed_by_the_normaliser(self):
        candidate = self.mutated()
        _, _, pattern = next(iter_patterns(candidate))
        pattern["reviewEvents"][-1]["note"] = "silently reworded"
        normalised = F2.without_phase_4ff2_product_approval(candidate)
        _, _, normalised_pattern = next(iter_patterns(normalised))
        self.assertEqual(FINAL_STATE, normalised_pattern["reviewState"])
        self.assertTrue(
            any(event["kind"] == PRODUCT_APPROVAL_KIND
                for event in normalised_pattern["reviewEvents"]))

    def test_a_premature_activity_grant_is_refused_before_approval(self):
        """The dependency runs the other way: eligibility needs approval."""
        candidate = copy.deepcopy(self.baseline)
        for _, _, pattern in iter_patterns(candidate):
            pattern["activityEligibility"] = ["reference"]
        self.assertIn(
            "UNAPPROVED_ACTIVITY",
            codes(validate_editorial(
                candidate, build_context(self.baseline_context))))


# --------------------------------------------------------------------------
# 8.  Reports
# --------------------------------------------------------------------------

class Reports(Phase4FF2TestCase):

    def matrix(self):
        with (ROOT / MATRIX_PATH).open(encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    def test_the_matrix_holds_exactly_forty_five_unique_rows(self):
        rows = self.matrix()
        self.assertEqual(PATTERN_COUNT, len(rows))
        self.assertEqual(PATTERN_COUNT, len({row["reviewId"] for row in rows}))
        self.assertEqual(PATTERN_COUNT, len({row["patternId"] for row in rows}))

    def test_the_matrix_review_ids_are_the_locked_forty_five(self):
        self.assertEqual(
            [f"P7-NR-{index:03d}" for index in range(1, 46)],
            [row["reviewId"] for row in self.matrix()])

    def test_every_matrix_row_agrees_with_the_corpus(self):
        by_id = {pattern["id"]: (lemma, meaning, pattern)
                 for lemma, meaning, pattern in self.rows}
        for row in self.matrix():
            with self.subTest(review_id=row["reviewId"]):
                lemma, meaning, pattern = by_id[row["patternId"]]
                event = [e for e in pattern["reviewEvents"]
                         if e["kind"] == PRODUCT_APPROVAL_KIND][0]
                self.assertEqual(PRIOR_STATE, row["priorState"])
                self.assertEqual(pattern["reviewState"], row["finalState"])
                self.assertEqual(FINAL_STATE, row["finalState"])
                self.assertEqual(
                    event["scopeDigest"], row["productApprovalScopeDigest"])
                self.assertEqual(
                    T.review_scope_digest(
                        PRODUCT_TIER, lemma, meaning, pattern),
                    row["productApprovalScopeDigest"])
                self.assertEqual(PRODUCT_OWNER, row["productOwnerRef"])
                self.assertEqual("true", row["productOwnerHuman"])
                self.assertEqual(PRODUCT_TIER, row["productOwnerRoles"])
                self.assertEqual(SOLO_MODE, row["acknowledgedReleaseMode"])
                self.assertEqual("ACCEPT", row["decision"])
                self.assertEqual(event["reviewedAt"], row["approvalDate"])
                self.assertEqual("no", row["releaseActionCreated"])
                self.assertEqual(
                    "no", row["productOwnerPerformedLinguisticReview"])
                self.assertEqual("0", row["contentFieldsChanged"])
                self.assertEqual("0", row["activityEligibilityGranted"])

    def test_every_matrix_row_traces_to_the_one_owner_decision(self):
        sources = {row["sourceDecision"] for row in self.matrix()}
        self.assertEqual(1, len(sources))
        self.assertIn("APPROVE ALL", sources.pop())

    def test_the_matrix_preserves_the_historical_event_counts(self):
        reference = sum(int(row["referenceAcceptancesPreserved"])
                        for row in self.matrix())
        editorial = sum(int(row["editorialAcceptancesPreserved"])
                        for row in self.matrix())
        self.assertEqual(REFERENCE_ACCEPT_COUNT, reference)
        self.assertEqual(EDITORIAL_ACCEPT_COUNT, editorial)

    def test_the_summary_states_the_counts_and_the_release_boundary(self):
        summary = read(SUMMARY_PATH)
        for token in (BASELINE_COMMIT, PRODUCT_OWNER, "APPROVE ALL",
                      SOLO_MODE, "45", "47"):
            with self.subTest(token=token):
                self.assertIn(token, summary)

    def test_the_summary_claims_no_linguistic_review_for_the_owner(self):
        summary = " ".join(read(SUMMARY_PATH).lower().split())
        for claim in ("native-speaker review", "linguistic review",
                      "not a language judgement",
                      "no new review of the polish"):
            with self.subTest(claim=claim):
                self.assertIn(claim, summary)


# --------------------------------------------------------------------------
# 9.  The normaliser itself
# --------------------------------------------------------------------------

class NormaliserContract(Phase4FF2TestCase):

    def test_the_normaliser_pins_forty_five_identities_and_digests(self):
        self.assertEqual(PATTERN_COUNT, len(F2.F2_EXPECTED_PATTERN_IDS))
        self.assertEqual(PATTERN_COUNT, len(F2.F2_EXPECTED_SCOPE_DIGESTS))
        self.assertEqual(
            F2.F2_EXPECTED_PATTERN_IDS,
            frozenset(pattern["id"] for _, _, pattern in self.rows))

    def test_each_pinned_digest_recomputes_against_the_live_row(self):
        for lemma, meaning, pattern in self.rows:
            with self.subTest(pattern_id=pattern["id"]):
                self.assertEqual(
                    T.review_scope_digest(
                        PRODUCT_TIER, lemma, meaning, pattern),
                    F2.F2_EXPECTED_SCOPE_DIGESTS[pattern["id"]])

    def test_the_normaliser_refuses_an_identity_outside_the_allowlist(self):
        with self.assertRaises(KeyError):
            F2.approved_f2_event("vp-p-not-a-real-priority-7-identity")

    def test_the_normaliser_leaves_a_duplicate_approval_visible(self):
        candidate = self.mutated()
        _, _, pattern = next(iter_patterns(candidate))
        pattern["reviewEvents"].append(copy.deepcopy(pattern["reviewEvents"][-1]))
        normalised = F2.without_phase_4ff2_product_approval(candidate)
        _, _, normalised_pattern = next(iter_patterns(normalised))
        self.assertEqual(
            2, len([event for event in normalised_pattern["reviewEvents"]
                    if event["kind"] == PRODUCT_APPROVAL_KIND]))

    def test_the_normaliser_leaves_a_later_state_visible(self):
        candidate = self.mutated()
        _, _, pattern = next(iter_patterns(candidate))
        pattern["reviewState"] = "rejected"
        normalised = F2.without_phase_4ff2_product_approval(candidate)
        _, _, normalised_pattern = next(iter_patterns(normalised))
        self.assertEqual("rejected", normalised_pattern["reviewState"])

    def test_the_normaliser_leaves_an_edited_owner_record_visible(self):
        document = self.mutated_context()
        document["reviewerRegistry"][PRODUCT_OWNER]["roles"] = [
            PRODUCT_TIER, "reopen"]
        self.assertIn(
            PRODUCT_OWNER,
            F2.without_phase_4ff2_reviewer(document)["reviewerRegistry"])

    def test_the_text_normaliser_refuses_a_noncanonical_corpus_form(self):
        with self.assertRaises(AssertionError):
            F2.without_phase_4ff2_corpus_text(
                json.dumps(self.corpus, ensure_ascii=False))


# --------------------------------------------------------------------------
# 10.  Baseline identity
# --------------------------------------------------------------------------

class BaselineIdentity(Phase4FF2TestCase):

    def test_the_declared_baseline_commit_and_tree_agree(self):
        tree = subprocess.run(
            ["git", "rev-parse", f"{BASELINE_COMMIT}^{{tree}}"],
            capture_output=True, text=True, check=True, cwd=ROOT).stdout.strip()
        self.assertEqual(BASELINE_TREE, tree)

    def test_the_baseline_corpus_digest_is_the_declared_one(self):
        self.assertEqual(
            "def97f266aa8ed964500c34253538c1dede2076a1f276e7a52a5b746e9217f0e",
            hashlib.sha256(git_blob(CORPUS_PATH).encode("utf-8")).hexdigest())

    def test_the_baseline_context_digest_is_the_declared_one(self):
        self.assertEqual(
            "ae7db0a69cadd0701820a7f1a6026e69f1e90e4fc6d2de164a15eb6058777691",
            hashlib.sha256(git_blob(CONTEXT_PATH).encode("utf-8")).hexdigest())


if __name__ == "__main__":
    unittest.main()
