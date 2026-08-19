"""Priority 7 Phase 4F-H2.1 — product re-approval after H2 content completion.

Phase 4F-H2 completed the learner-facing content and then deliberately stopped
one tier short of release: it left the 44 rows it changed at
``editorial-reviewed`` with their Phase 4F-F2 approvals honestly stale, so the
product owner could look at the corrected material before anything derived
``approved``.  On 2026-08-18 the owner reviewed the H2 learner-facing preview
and returned "H2 approved".

This phase records that decision and nothing else.  It appends **exactly one**
``product-approval`` acceptance to each of the 44 changed patterns, bound to
that pattern's freshly recomputed *current* tier-3 scope digest, and moves
those rows to ``approved``.  It writes no learner content, registers no
identity, and gives the one pattern H2 never touched **no** second approval.

Proved below, against the immutable baseline
``98cd258016564a381856d7b86cccf9e6402b458d``:

1.  **The H2 baseline was what H2 said it was.**  Recomputed from the baseline
    commit, not taken on trust: 45 patterns, 45 examples, 44
    ``editorial-reviewed`` and 1 ``approved``, 42 corrections, 44 editorial
    change requests, 44 fresh editorial acceptances, **0** product approvals
    after H2; tier 1 current on 45, tier 2 current on 45, tier 3 current on
    exactly the one untouched row and stale on exactly the other 44.
2.  **The authority is the existing owner.**  ``product-owner-001``, already
    in the registry, still holding ``product-approval`` and nothing else.  No
    reviewer was added, no role was widened, and no correction or reopen
    authority was created.
3.  **Exactly 44 approvals, each over its own current scope.**  One per changed
    pattern, ``decision=accept``, ``reviewerRef`` (never ``actorRef``),
    ``reviewedAt=2026-08-18``, ``scopeVersion=1``, and a ``scopeDigest`` that
    equals the freshly computed tier-3 digest and equals no stale H2 or F2
    digest.
4.  **The untouched row was left alone.**  ``vp-p-zajmowac-sie-look-after-
    person-instrumental-object-6f93facbd939`` still carries exactly one
    product approval, still Phase 4F-F2's, still current.
5.  **The final state is 45/45 approved**, on 89 product-approval acceptances
    (45 historical + 44 fresh), with the 47 reference acceptances, 89
    editorial acceptances, 44 editorial change requests and 42 corrections
    byte-identical and ``reopen`` still 0.
6.  **No content moved.**  The corpus is byte-identical to the H2 baseline
    apart from ``reviewEvents`` and ``reviewState``; tier-1, tier-2 **and**
    tier-3 scope digests moved on 0 of 45.
7.  **Nothing shipped and nothing was enabled.**  Every shipping file
    byte-identical, ``APP_VERSION`` and the shell cache unchanged,
    ``content/verb-patterns.json`` absent, ``activityEligibility`` empty on
    all 45 and no example audio-eligible.
8.  **The boundary has teeth.**  A missing approval, an approval on the
    untouched row, a duplicate, a wrong reviewer, an ``actorRef`` in place of
    a ``reviewerRef``, a wrong date, a stale digest, an approval ahead of
    editorial currency, a post-approval content edit, an extra reference,
    correction or reopen event, an audio or activity change and a runtime
    materialisation are each rejected -- by the validator, by the derived
    state, or by surviving the H2.1 normaliser and still breaking a
    historical guard.

Every mutation below is applied to an in-memory copy.  Nothing here writes to
the corpus, the context, the tooling or any shipping file.

Run:  python3 -m unittest tests.test_priority7_phase4fh21
"""

from __future__ import annotations

import collections
import copy
import csv
import json
import subprocess
import unittest
from pathlib import Path

import os.path as _h21_os_path
import sys as _h21_sys

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
if str(ROOT) not in _h21_sys.path:
    _h21_sys.path.insert(0, str(ROOT))
_H21_DIR = _h21_os_path.dirname(_h21_os_path.abspath(__file__))
if _H21_DIR not in _h21_sys.path:
    _h21_sys.path.insert(0, _H21_DIR)

import priority7_tooling as T  # noqa: E402
from priority7_tooling import ValidationContext, validate_editorial  # noqa: E402

import priority7_phase4fh2_normalizer as H2  # noqa: E402
import priority7_phase4fh21_normalizer as H21  # noqa: E402
import priority7_phase4fh3_normalizer as H3  # noqa: E402

CORPUS_PATH = "editorial/verb-pattern-candidates.json"
CONTEXT_PATH = "editorial/priority-7-authoring-context.json"
MATRIX_PATH = "reports/priority-7-phase-4fh21-product-approval-matrix.csv"
SUMMARY_PATH = "reports/priority-7-phase-4fh21-product-reapproval-summary.md"
NORMALISER_PATH = "tests/priority7_phase4fh21_normalizer.py"
PUBLIC_RUNTIME_PATH = "content/verb-patterns.json"

#: Phase 4F-H2.1 arrived on top of this commit and states every immutability
#: claim against it, never against a moving ``HEAD``.
BASELINE_COMMIT = "98cd258016564a381856d7b86cccf9e6402b458d"
BASELINE_TREE = "1523e7e70edb5f7bcfecc8ec64e0841a47390e43"

H21_DATE = "2026-08-18"
OWNER = "product-owner-001"
NATIVE_REVIEWER = "native-reviewer-001"
EDITORIAL_ACTOR = "priority7-editorial-review"
CORROBORATOR = "priority7-editorial-corroboration"
REFERENCE_ACTOR = "priority7-reference-analysis"
GENERATOR = "priority7-example-generation"

PATTERN_COUNT = 45
CHANGED_COUNT = 44
EXAMPLE_COUNT = 45
REPOSITORY_REUSE_TOTAL = 20
EDITORIAL_GENERATED_TOTAL = 25
REFERENCE_ACCEPTANCES = 47
EDITORIAL_ACCEPTANCES = 89
EDITORIAL_CHANGE_REQUESTS = 44
CORRECTIONS = 42
HISTORICAL_APPROVALS = 45
FINAL_APPROVALS = HISTORICAL_APPROVALS + CHANGED_COUNT

UNTOUCHED = H21.H21_UNTOUCHED_PATTERN_ID

PROTECTED_SHIPPING_FILES = (
    "index.html", "sw.js", "manifest.json", "pp-verb-patterns.js",
    "pp-usage.js", "pp-answer.js", "pp-distractor.js", "pp-migrate.js",
    "sitemap.xml", "audio-manifest.json", "data-a1.js", "data-a2.js",
    "data-b1.js", "data-grammar.js", "data-podcasts.js", "data-scenarios.js",
    "data-verbs.js", "validate_content.py", "build_pages.py", "verify_audio.py",
    "pp_audio_rule.py", "priority7_tooling.py", "generate_audio.py",
    "robots.txt", "CNAME",
)

#: Every pattern-owned field H2.1 must not have touched.  ``reviewEvents`` and
#: ``reviewState`` are deliberately absent: they are the whole transition.
FROZEN_PATTERN_FIELDS = (
    "id", "key", "relationType", "complements", "cefr", "teachingStatus",
    "usage", "learnerExplanationEn", "activityEligibility", "evidence",
    "releaseMode", "examples", "contentRefs", "errorNotes",
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def git(*arguments):
    return subprocess.run(["git", *arguments], cwd=ROOT, capture_output=True,
                          text=True, check=False)


def git_blob(relative, revision=BASELINE_COMMIT):
    result = git("show", f"{revision}:{relative}")
    if result.returncode != 0:
        raise AssertionError(f"missing at {revision}: {relative}")
    return result.stdout


def read(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


def is_only_the_h3_ui_wording(path):
    """True for ``index.html`` when its only change is the Phase 4F-H3 layer.

    Phase 4F-H3 is the UI wording phase this suite already named as a later
    phase's work, and the first phase since ``f339efb`` entitled to change a
    shipping file at all.  A path qualifies only when removing H3's six
    pinned strings reproduces this phase's baseline bytes exactly, so any
    other shell edit -- a version or cache bump, a loader activation, a change
    to the recognition-only guards -- any other path, and any partly applied
    layer are still reported exactly as before.
    """
    if not H3.is_phase_4fh3_path(path):
        return False
    baseline = git("show", f"{BASELINE_COMMIT}:{path}")
    if baseline.returncode != 0:
        return False
    # LAYERED by Priority 7 Phase 4F-I1: the shell now carries the I1 release
    # layer on top of the H3 wording layer, so the H3 classification is made
    # over the shell with the I1 layer removed.  Both layers are pinned and
    # all-or-nothing, so an edit outside either pinned set is still reported.
    return H3.is_exactly_the_h3_ui_wording(path, baseline.stdout, pre_i1(path))


def live_corpus():
    """The corpus exactly as it stands on disk, with no normalisation."""
    return json.loads(read(CORPUS_PATH))


def live_context_document():
    """The context exactly as it stands on disk, with no normalisation."""
    return json.loads(read(CONTEXT_PATH))


def baseline_corpus():
    return json.loads(git_blob(CORPUS_PATH))


def baseline_context_document():
    return json.loads(git_blob(CONTEXT_PATH))


def repository_index():
    return T.repository_index_from_root(str(ROOT))


def build_context(document=None, *, resolve_repository=True):
    document = live_context_document() if document is None else document
    return ValidationContext(
        source_registry=document["sourceRegistry"],
        reviewer_registry=document["reviewerRegistry"],
        author_registry=document["authorRegistry"],
        allocation_registry=document["allocationRegistry"],
        repository_index=repository_index() if resolve_repository else None,
        editorial_actor_registry=document.get("editorialActorRegistry", {}),
        today=H21_DATE,
    )


def iter_patterns(corpus):
    for lemma in corpus["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                yield lemma, meaning, pattern


def rows_by_id(corpus):
    return {pattern["id"]: (lemma, meaning, pattern)
            for lemma, meaning, pattern in iter_patterns(corpus)}


def stage_digests(lemma, meaning, pattern):
    return {
        "tier1": T.review_scope_digest(
            "external-verification", lemma, meaning, pattern),
        "tier2": T.review_scope_digest(
            "native-linguistic", lemma, meaning, pattern),
        "tier3": T.review_scope_digest(
            "product-approval", lemma, meaning, pattern),
    }


def events_of(corpus, kind=None, decision=None):
    return [event for _l, _m, pattern in iter_patterns(corpus)
            for event in pattern["reviewEvents"]
            if (kind is None or event["kind"] == kind)
            and (decision is None or event["decision"] == decision)]


def approvals_of(pattern):
    return [event for event in pattern["reviewEvents"]
            if event["kind"] == "product-approval"]


def derived_state(lemma, meaning, pattern):
    """The state the live history and live digests actually support."""
    return T._derive_review_currency(
        pattern["reviewEvents"],
        T.declared_release_mode(pattern),
        {stage: T.review_scope_digest(stage, lemma, meaning, pattern)
         for stage in T.STAGE_KINDS},
        {T.evidence_digest(record) for record in pattern.get("evidence", [])},
        {T.evidence_digest(record): record
         for record in pattern.get("evidence", [])},
    ).state


def codes(issues):
    return sorted({issue.code for issue in issues})


class Phase4FH21TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = live_corpus()
        cls.context_document = live_context_document()
        cls.baseline = baseline_corpus()
        cls.baseline_context = baseline_context_document()
        cls.rows = rows_by_id(cls.corpus)
        cls.baseline_rows = rows_by_id(cls.baseline)

    def mutated(self):
        return copy.deepcopy(type(self).corpus)

    def mutated_context(self):
        return copy.deepcopy(type(self).context_document)

    def a_changed_pattern(self, corpus):
        return rows_by_id(corpus)[sorted(H21.H21_EXPECTED_PATTERN_IDS)[0]][2]


# ---------------------------------------------------------------------------
# 1.  The H2 baseline, recomputed rather than taken on trust
# ---------------------------------------------------------------------------

class BaselineConfirmation(Phase4FH21TestCase):

    def test_the_baseline_is_the_declared_commit_and_tree(self):
        self.assertEqual(
            BASELINE_TREE,
            git("rev-parse", f"{BASELINE_COMMIT}^{{tree}}").stdout.strip())

    def test_the_baseline_holds_forty_five_patterns_and_forty_five_examples(self):
        self.assertEqual(PATTERN_COUNT, len(self.baseline_rows))
        self.assertEqual(
            EXAMPLE_COUNT,
            sum(len(pattern["examples"])
                for _l, _m, pattern in iter_patterns(self.baseline)))

    def test_the_baseline_state_is_forty_four_editorial_and_one_approved(self):
        states = collections.Counter(
            pattern["reviewState"]
            for _l, _m, pattern in iter_patterns(self.baseline))
        self.assertEqual({"editorial-reviewed": CHANGED_COUNT, "approved": 1},
                         dict(states))

    def test_the_one_baseline_approved_row_is_the_untouched_pattern(self):
        approved = [pattern["id"]
                    for _l, _m, pattern in iter_patterns(self.baseline)
                    if pattern["reviewState"] == "approved"]
        self.assertEqual([UNTOUCHED], approved)

    def test_the_baseline_fresh_h2_event_counts(self):
        fresh = collections.Counter(
            (event["kind"], event["decision"])
            for _l, _m, pattern in iter_patterns(self.baseline)
            for event in pattern["reviewEvents"]
            if event["reviewedAt"] == H21_DATE)
        self.assertEqual(CORRECTIONS, fresh[("correction", "accept")])
        self.assertEqual(EDITORIAL_CHANGE_REQUESTS,
                         fresh[("editorial-review", "changes-requested")])
        self.assertEqual(CHANGED_COUNT, fresh[("editorial-review", "accept")])
        self.assertEqual(0, fresh[("product-approval", "accept")])

    def test_the_baseline_historical_ledger_matches_the_h2_report(self):
        counts = collections.Counter(
            (event["kind"], event["decision"])
            for _l, _m, pattern in iter_patterns(self.baseline)
            for event in pattern["reviewEvents"])
        self.assertEqual(REFERENCE_ACCEPTANCES,
                         counts[("reference-verification", "accept")])
        self.assertEqual(EDITORIAL_ACCEPTANCES,
                         counts[("editorial-review", "accept")])
        self.assertEqual(EDITORIAL_CHANGE_REQUESTS,
                         counts[("editorial-review", "changes-requested")])
        self.assertEqual(CORRECTIONS, counts[("correction", "accept")])
        self.assertEqual(HISTORICAL_APPROVALS,
                         counts[("product-approval", "accept")])
        self.assertEqual(
            0, sum(1 for _l, _m, pattern in iter_patterns(self.baseline)
                   for event in pattern["reviewEvents"]
                   if event["kind"] == "reopen"))

    def test_the_baseline_tier_one_and_tier_two_are_current_on_all_forty_five(self):
        for pattern_id, (lemma, meaning, pattern) in self.baseline_rows.items():
            digests = stage_digests(lemma, meaning, pattern)
            with self.subTest(pattern_id=pattern_id):
                reference = [event for event in pattern["reviewEvents"]
                             if event["kind"] == "reference-verification"][-1]
                editorial = [event for event in pattern["reviewEvents"]
                             if event["kind"] == "editorial-review"
                             and event["decision"] == "accept"][-1]
                self.assertEqual(digests["tier1"], reference["scopeDigest"])
                self.assertEqual(digests["tier2"], editorial["scopeDigest"])

    def test_the_baseline_tier_three_is_stale_on_exactly_the_forty_four(self):
        stale = set()
        for pattern_id, (lemma, meaning, pattern) in self.baseline_rows.items():
            approval = approvals_of(pattern)[-1]
            if approval["scopeDigest"] != stage_digests(
                    lemma, meaning, pattern)["tier3"]:
                stale.add(pattern_id)
        self.assertEqual(set(H21.H21_EXPECTED_PATTERN_IDS), stale)
        self.assertNotIn(UNTOUCHED, stale)

    def test_the_untouched_baseline_row_keeps_all_three_current_digests(self):
        lemma, meaning, pattern = self.baseline_rows[UNTOUCHED]
        digests = stage_digests(lemma, meaning, pattern)
        kinds = {"reference-verification": "tier1",
                 "editorial-review": "tier2",
                 "product-approval": "tier3"}
        for kind, tier in kinds.items():
            accepted = [event for event in pattern["reviewEvents"]
                        if event["kind"] == kind
                        and event["decision"] == "accept"][-1]
            with self.subTest(tier=tier):
                self.assertEqual(digests[tier], accepted["scopeDigest"])

    def test_the_baseline_allowlist_is_every_pattern_but_the_untouched_one(self):
        self.assertEqual(
            set(self.baseline_rows) - {UNTOUCHED},
            set(H21.H21_EXPECTED_PATTERN_IDS))
        self.assertEqual(CHANGED_COUNT, len(H21.H21_EXPECTED_PATTERN_IDS))


# ---------------------------------------------------------------------------
# 2.  The authority is the existing human product owner
# ---------------------------------------------------------------------------

class ProductOwnerAuthority(Phase4FH21TestCase):

    def test_the_reviewer_registry_is_byte_identical_to_the_baseline(self):
        self.assertEqual(self.baseline_context["reviewerRegistry"],
                         self.context_document["reviewerRegistry"])

    def test_the_owner_holds_product_approval_and_nothing_else(self):
        record = self.context_document["reviewerRegistry"][OWNER]
        self.assertIs(True, record["human"])
        self.assertEqual(["product-approval"], record["roles"])
        self.assertNotIn("ownerAllowsMultipleRoles", record)
        self.assertIn("solo-maintainer-reference-backed",
                      record["acknowledgedReleaseModes"])

    def test_no_reviewer_holds_correction_or_reopen_authority_of_its_own(self):
        for reviewer_id, record in (
                self.context_document["reviewerRegistry"].items()):
            with self.subTest(reviewer=reviewer_id):
                self.assertEqual(
                    set(), {"correction", "reopen", "external-verification"}
                    & set(record["roles"]))

    def test_no_reviewer_or_actor_identity_was_added_or_removed(self):
        for registry in ("reviewerRegistry", "editorialActorRegistry",
                         "authorRegistry", "sourceRegistry",
                         "allocationRegistry"):
            with self.subTest(registry=registry):
                self.assertEqual(self.baseline_context[registry],
                                 self.context_document[registry])

    def test_the_author_registry_is_still_empty(self):
        self.assertEqual({}, self.context_document["authorRegistry"])

    def test_every_new_approval_names_the_owner_and_never_an_actor(self):
        for pattern_id in H21.H21_EXPECTED_PATTERN_IDS:
            event = self.rows[pattern_id][2]["reviewEvents"][-1]
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(OWNER, event["reviewerRef"])
                self.assertNotIn("actorRef", event)
                self.assertNotIn("corroboratingActorRefs", event)

    def test_the_native_reviewer_is_named_by_no_new_event(self):
        self.assertNotIn(
            NATIVE_REVIEWER,
            json.dumps([pattern["reviewEvents"][-1]
                        for pattern_id in H21.H21_EXPECTED_PATTERN_IDS
                        for pattern in [self.rows[pattern_id][2]]],
                       ensure_ascii=False))


# ---------------------------------------------------------------------------
# 3.  Exactly 44 approvals, each over its own current tier-3 scope
# ---------------------------------------------------------------------------

class TheFortyFourApprovals(Phase4FH21TestCase):

    def test_exactly_forty_four_approvals_were_appended(self):
        appended = []
        for pattern_id, (_l, _m, pattern) in self.rows.items():
            before = self.baseline_rows[pattern_id][2]["reviewEvents"]
            after = pattern["reviewEvents"]
            self.assertEqual(before, after[:len(before)], pattern_id)
            appended.extend((pattern_id, event) for event in after[len(before):])
        self.assertEqual(CHANGED_COUNT, len(appended))
        self.assertEqual(set(H21.H21_EXPECTED_PATTERN_IDS),
                         {pattern_id for pattern_id, _ in appended})

    def test_each_changed_row_gained_exactly_one_trailing_approval(self):
        for pattern_id in H21.H21_EXPECTED_PATTERN_IDS:
            pattern = self.rows[pattern_id][2]
            before = self.baseline_rows[pattern_id][2]["reviewEvents"]
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(len(before) + 1, len(pattern["reviewEvents"]))
                self.assertEqual("product-approval",
                                 pattern["reviewEvents"][-1]["kind"])

    def test_every_new_approval_uses_the_existing_event_schema_exactly(self):
        for pattern_id in H21.H21_EXPECTED_PATTERN_IDS:
            event = self.rows[pattern_id][2]["reviewEvents"][-1]
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(
                    {"kind", "decision", "scopeVersion", "scopeDigest",
                     "reviewerRef", "reviewedAt", "note"}, set(event))
                self.assertEqual("product-approval", event["kind"])
                self.assertEqual("accept", event["decision"])
                self.assertEqual(1, event["scopeVersion"])
                self.assertEqual(H21_DATE, event["reviewedAt"])

    def test_every_new_approval_pins_the_freshly_computed_tier_three_digest(self):
        for pattern_id in H21.H21_EXPECTED_PATTERN_IDS:
            lemma, meaning, pattern = self.rows[pattern_id]
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(
                    stage_digests(lemma, meaning, pattern)["tier3"],
                    pattern["reviewEvents"][-1]["scopeDigest"])

    def test_no_new_approval_reuses_a_stale_h2_or_f2_digest(self):
        for pattern_id in H21.H21_EXPECTED_PATTERN_IDS:
            pattern = self.rows[pattern_id][2]
            fresh = pattern["reviewEvents"][-1]["scopeDigest"]
            historical = {event["scopeDigest"]
                          for event in pattern["reviewEvents"][:-1]
                          if "scopeDigest" in event}
            with self.subTest(pattern_id=pattern_id):
                self.assertNotIn(fresh, historical)

    def test_every_new_approval_carries_the_same_truthful_note(self):
        notes = {self.rows[pattern_id][2]["reviewEvents"][-1]["note"]
                 for pattern_id in H21.H21_EXPECTED_PATTERN_IDS}
        self.assertEqual({H21.H21_NOTE}, notes)
        self.assertLessEqual(len(H21.H21_NOTE), 240)
        lowered = H21.H21_NOTE.lower()
        for claim in ("product owner visually reviewed",
                      "corrected h2 learner content", "completed examples",
                      "translated polish illustrations", "2026-08-18",
                      "not a new linguistic, reference or native-speaker "
                      "review", "audio deferred", "ui wording separate"):
            with self.subTest(claim=claim):
                self.assertIn(claim, lowered)
        for forbidden in ("authored", "wrote ", "native speaker confirmed",
                          "professional", "verified the polish"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, lowered)

    def test_the_appended_events_match_the_normalisers_static_pins(self):
        for pattern_id in H21.H21_EXPECTED_PATTERN_IDS:
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(H21.approved_h21_event(pattern_id),
                                 self.rows[pattern_id][2]["reviewEvents"][-1])

    def test_the_appended_approvals_are_the_only_new_events_anywhere(self):
        added = collections.Counter()
        for pattern_id, (_l, _m, pattern) in self.rows.items():
            before = self.baseline_rows[pattern_id][2]["reviewEvents"]
            for event in pattern["reviewEvents"][len(before):]:
                added[(event["kind"], event["decision"])] += 1
        self.assertEqual({("product-approval", "accept"): CHANGED_COUNT},
                         dict(added))


# ---------------------------------------------------------------------------
# 4.  The untouched pattern was left alone
# ---------------------------------------------------------------------------

class TheUntouchedPattern(Phase4FH21TestCase):

    def test_the_untouched_row_is_byte_identical_to_the_baseline(self):
        self.assertEqual(self.baseline_rows[UNTOUCHED][2],
                         self.rows[UNTOUCHED][2])

    def test_the_untouched_row_carries_exactly_one_product_approval(self):
        approvals = approvals_of(self.rows[UNTOUCHED][2])
        self.assertEqual(1, len(approvals))
        self.assertEqual("2026-08-17", approvals[0]["reviewedAt"])

    def test_the_untouched_rows_existing_approval_still_covers_its_scope(self):
        lemma, meaning, pattern = self.rows[UNTOUCHED]
        self.assertEqual(stage_digests(lemma, meaning, pattern)["tier3"],
                         approvals_of(pattern)[0]["scopeDigest"])

    def test_the_untouched_row_is_outside_the_h21_allowlist(self):
        self.assertNotIn(UNTOUCHED, H21.H21_EXPECTED_PATTERN_IDS)
        with self.assertRaises(KeyError):
            H21.approved_h21_event(UNTOUCHED)


# ---------------------------------------------------------------------------
# 5.  The final governance state
# ---------------------------------------------------------------------------

class FinalGovernanceState(Phase4FH21TestCase):

    def test_all_forty_five_patterns_are_approved(self):
        states = collections.Counter(
            pattern["reviewState"]
            for _l, _m, pattern in iter_patterns(self.corpus))
        self.assertEqual({"approved": PATTERN_COUNT}, dict(states))

    def test_all_forty_five_derive_approved_from_their_own_history(self):
        for pattern_id, (lemma, meaning, pattern) in self.rows.items():
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual("approved",
                                 derived_state(lemma, meaning, pattern))

    def test_the_product_approval_ledger_is_forty_five_plus_forty_four(self):
        approvals = events_of(self.corpus, "product-approval", "accept")
        self.assertEqual(FINAL_APPROVALS, len(approvals))
        by_date = collections.Counter(event["reviewedAt"] for event in approvals)
        self.assertEqual(HISTORICAL_APPROVALS, by_date["2026-08-17"])
        self.assertEqual(CHANGED_COUNT, by_date[H21_DATE])

    def test_the_reference_verification_ledger_did_not_change(self):
        self.assertEqual(
            REFERENCE_ACCEPTANCES,
            len(events_of(self.corpus, "reference-verification", "accept")))
        for pattern_id, (_l, _m, pattern) in self.rows.items():
            before = [event for event in
                      self.baseline_rows[pattern_id][2]["reviewEvents"]
                      if event["kind"] == "reference-verification"]
            after = [event for event in pattern["reviewEvents"]
                     if event["kind"] == "reference-verification"]
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(before, after)

    def test_the_editorial_review_events_did_not_change(self):
        self.assertEqual(EDITORIAL_ACCEPTANCES,
                         len(events_of(self.corpus, "editorial-review",
                                       "accept")))
        self.assertEqual(EDITORIAL_CHANGE_REQUESTS,
                         len(events_of(self.corpus, "editorial-review",
                                       "changes-requested")))
        for pattern_id, (_l, _m, pattern) in self.rows.items():
            before = [event for event in
                      self.baseline_rows[pattern_id][2]["reviewEvents"]
                      if event["kind"] == "editorial-review"]
            after = [event for event in pattern["reviewEvents"]
                     if event["kind"] == "editorial-review"]
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(before, after)

    def test_the_correction_events_did_not_change(self):
        self.assertEqual(CORRECTIONS,
                         len(events_of(self.corpus, "correction")))
        for pattern_id, (_l, _m, pattern) in self.rows.items():
            before = [event for event in
                      self.baseline_rows[pattern_id][2]["reviewEvents"]
                      if event["kind"] == "correction"]
            after = [event for event in pattern["reviewEvents"]
                     if event["kind"] == "correction"]
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(before, after)

    def test_there_is_still_no_reopen_event_anywhere(self):
        self.assertEqual([], events_of(self.corpus, "reopen"))

    def test_the_historical_product_approvals_are_preserved_byte_for_byte(self):
        for pattern_id, (_l, _m, pattern) in self.rows.items():
            before = approvals_of(self.baseline_rows[pattern_id][2])
            after = approvals_of(pattern)
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(before, after[:len(before)])

    def test_the_release_mode_is_unchanged_on_all_forty_five(self):
        modes = {pattern["releaseMode"]
                 for _l, _m, pattern in iter_patterns(self.corpus)}
        self.assertEqual({"solo-maintainer-reference-backed"}, modes)

    def test_the_live_record_validates_against_the_real_context(self):
        self.assertEqual([], validate_editorial(self.corpus, build_context()))

    def test_a_freeze_now_admits_all_forty_five_patterns(self):
        frozen = T.freeze_editorial(self.mutated(), 1, build_context())
        admitted = [pattern["id"]
                    for lemma in frozen["runtimeProjection"]["lemmas"]
                    for meaning in lemma["meanings"]
                    for pattern in meaning["patterns"]]
        self.assertEqual(PATTERN_COUNT, len(admitted))
        self.assertEqual(set(self.rows), set(admitted))


# ---------------------------------------------------------------------------
# 6.  Digest currency
# ---------------------------------------------------------------------------

class DigestCurrency(Phase4FH21TestCase):

    def test_no_scope_digest_moved_at_any_tier(self):
        moved = {"tier1": [], "tier2": [], "tier3": []}
        for pattern_id, (lemma, meaning, pattern) in self.rows.items():
            before = stage_digests(*self.baseline_rows[pattern_id])
            after = stage_digests(lemma, meaning, pattern)
            for tier in moved:
                if before[tier] != after[tier]:
                    moved[tier].append(pattern_id)
        self.assertEqual({"tier1": [], "tier2": [], "tier3": []}, moved)

    def test_every_tier_one_acceptance_is_current(self):
        for pattern_id, (lemma, meaning, pattern) in self.rows.items():
            accepted = [event for event in pattern["reviewEvents"]
                        if event["kind"] == "reference-verification"][-1]
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(stage_digests(lemma, meaning, pattern)["tier1"],
                                 accepted["scopeDigest"])

    def test_every_tier_two_acceptance_is_current(self):
        for pattern_id, (lemma, meaning, pattern) in self.rows.items():
            accepted = [event for event in pattern["reviewEvents"]
                        if event["kind"] == "editorial-review"
                        and event["decision"] == "accept"][-1]
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(stage_digests(lemma, meaning, pattern)["tier2"],
                                 accepted["scopeDigest"])

    def test_every_tier_three_scope_is_now_accepted_and_current(self):
        for pattern_id, (lemma, meaning, pattern) in self.rows.items():
            accepted = approvals_of(pattern)[-1]
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(stage_digests(lemma, meaning, pattern)["tier3"],
                                 accepted["scopeDigest"])

    def test_the_forty_four_stale_approvals_are_still_recorded_as_stale(self):
        """Superseded, never rewritten: the staleness stays in the history."""
        for pattern_id in H21.H21_EXPECTED_PATTERN_IDS:
            lemma, meaning, pattern = self.rows[pattern_id]
            stale = approvals_of(pattern)[0]
            with self.subTest(pattern_id=pattern_id):
                self.assertNotEqual(
                    stage_digests(lemma, meaning, pattern)["tier3"],
                    stale["scopeDigest"])


# ---------------------------------------------------------------------------
# 7.  Canonical content did not move
# ---------------------------------------------------------------------------

class ContentImmutability(Phase4FH21TestCase):

    def test_the_corpus_differs_only_in_review_events_and_review_state(self):
        before, after = copy.deepcopy(self.baseline), copy.deepcopy(self.corpus)
        for document in (before, after):
            for _l, _m, pattern in iter_patterns(document):
                pattern.pop("reviewEvents")
                pattern.pop("reviewState")
        self.assertEqual(before, after)

    def test_every_frozen_pattern_field_is_byte_identical(self):
        for pattern_id, (_l, _m, pattern) in self.rows.items():
            baseline = self.baseline_rows[pattern_id][2]
            self.assertEqual(set(baseline), set(pattern))
            for field in FROZEN_PATTERN_FIELDS:
                with self.subTest(pattern_id=pattern_id, field=field):
                    self.assertEqual(baseline.get(field), pattern.get(field))

    def test_the_pattern_identities_are_unchanged(self):
        self.assertEqual([pattern["id"] for _l, _m, pattern
                          in iter_patterns(self.baseline)],
                         [pattern["id"] for _l, _m, pattern
                          in iter_patterns(self.corpus)])

    def test_the_example_corpus_is_unchanged_and_honestly_sourced(self):
        examples = [example for _l, _m, pattern in iter_patterns(self.corpus)
                    for example in pattern["examples"]]
        self.assertEqual(EXAMPLE_COUNT, len(examples))
        origins = collections.Counter(
            example["origin"]["kind"] for example in examples)
        self.assertEqual({"repository-reuse": REPOSITORY_REUSE_TOTAL,
                          "editorial-generated": EDITORIAL_GENERATED_TOTAL},
                         dict(origins))
        self.assertEqual(
            [], [example for example in examples
                 if example["origin"]["kind"] == "original"])

    def test_every_example_id_and_text_is_baseline_identical(self):
        for pattern_id, (_l, _m, pattern) in self.rows.items():
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(self.baseline_rows[pattern_id][2]["examples"],
                                 pattern["examples"])

    def test_the_lemma_and_meaning_scaffolding_is_unchanged(self):
        def scaffolding(document):
            return [(lemma["id"], meaning["id"], meaning["key"],
                     lemma["canonicalLemma"], lemma["aspect"])
                    for lemma, meaning, _p in iter_patterns(document)]
        self.assertEqual(scaffolding(self.baseline), scaffolding(self.corpus))

    def test_the_corpus_envelope_is_unchanged(self):
        for key in ("artifactStatus", "formatVersion"):
            with self.subTest(key=key):
                self.assertEqual(self.baseline[key], self.corpus[key])


# ---------------------------------------------------------------------------
# 8.  Audio, activity, UI and shipping invariants
# ---------------------------------------------------------------------------

class ReleaseAndActivityBoundary(Phase4FH21TestCase):

    def test_activity_eligibility_is_empty_on_all_forty_five(self):
        self.assertEqual(
            0, sum(len(pattern["activityEligibility"])
                   for _l, _m, pattern in iter_patterns(self.corpus)))

    def test_no_example_is_audio_eligible(self):
        self.assertEqual(
            0, sum(1 for _l, _m, pattern in iter_patterns(self.corpus)
                   for example in pattern["examples"]
                   if example["audioEligible"] is True))

    def test_every_shipping_file_is_byte_identical_to_the_baseline(self):
        """Compared with the Phase 4F-I1 and 4F-H3 layers removed.

        Two phases have been entitled to change a shipping file since this
        baseline: H3, the UI wording phase, and I1, the atomic release.  Both
        layers are pinned and all-or-nothing, so removing them must reproduce
        these bytes exactly and every other shell or worker edit still fails
        here.  I1 is stripped first because it sits on top of H3, and the
        generator-owned outputs it regenerated are admitted only by their own
        pinned delta.
        """
        for name in PROTECTED_SHIPPING_FILES:
            with self.subTest(path=name):
                if i1_is_generated_output(name):
                    self.assertTrue(I1.is_exactly_the_i1_transition(
                        name, git_blob(name), read(name),
                        bundle=i1_bundle()), name)
                    continue
                text = i1_shipping_text(name)
                if H3.is_phase_4fh3_path(name):
                    text = H3.without_phase_4fh3_ui_wording(text)
                self.assertEqual(git_blob(name), text)

    def test_the_app_version_and_shell_cache_did_not_advance(self):
        # Superseded by Phase 4F-I1, which advanced both as one release step;
        # restated over the shell and worker with the pinned I1 layer removed.
        self.assertIn('const APP_VERSION = "8.10";', pre_i1("index.html"))
        self.assertIn('const CACHE = "popolsku-v65";', pre_i1("sw.js"))
        self.assertIn("PP_MIGRATE.CONTENT_MIGRATION_REVISION = 2;",
                      read("pp-migrate.js"))

    def test_the_ui_wording_is_still_the_pre_h3_wording(self):
        """UI capitalisation and the badge label are H3, not this phase.

        Stated over the shell with the Phase 4F-H3 layer removed, so it keeps
        meaning something once H3 has landed: strip H3 and what is left must
        still be exactly the pre-H3 wording this phase shipped beside.  The
        title claim is pinned at its five title/label sites rather than by a
        bare substring, which a code comment could satisfy on its own.
        """
        index = H3.without_phase_4fh3_ui_wording(read("index.html"))
        self.assertIn("Understand this one", index)
        self.assertNotIn("Understand for now", index)
        self.assertIn('<h1 id="pTitle">Verb patterns</h1>', index)
        self.assertEqual(1, index.count('level:"Verb patterns"'))
        self.assertEqual(1, index.count('name:"Verb patterns"'))
        # Four of the five sites are JS string literals; the fifth is the
        # static <h1>, pinned above.
        self.assertEqual(4, index.count('"Verb patterns"'))

    def test_the_public_runtime_artifact_does_not_exist(self):
        # Superseded by Priority 7 Phase 4F-I1, the release that materialised
        # the official runtime.  The only document that may occupy that path
        # is exactly the I1 release artifact, pinned by digest and revision,
        # and it may only exist alongside the matching shell and worker.
        self.assertEqual("complete", i1_bundle().state)

    def test_no_audio_file_or_manifest_entry_moved(self):
        self.assertEqual(git_blob("audio-manifest.json"),
                         read("audio-manifest.json"))
        changed = git("diff", "--name-only", BASELINE_COMMIT, "--", "audio")
        self.assertEqual("", changed.stdout.strip())

    def test_no_generated_page_or_sitemap_moved(self):
        """Restated over the Phase 4F-I1 release.

        I1 advances APP_VERSION, which the generator stamps into every footer,
        so it legitimately regenerates the 31 pages and the sitemap.  What this
        phase still claims is that it moved none of them itself: every path
        that did move is admitted only by its own pinned I1 delta.
        """
        bundle = i1_bundle()
        for area in ("grammar", "guide", "vocabulary", "sitemap.xml"):
            with self.subTest(path=area):
                changed = git("diff", "--name-only", BASELINE_COMMIT, "--", area)
                for relative in sorted(
                        line for line in changed.stdout.splitlines() if line):
                    with self.subTest(page=relative):
                        self.assertTrue(
                            i1_is_generated_output(relative), relative)
                        self.assertTrue(I1.is_exactly_the_i1_transition(
                            relative, git_blob(relative), read(relative),
                            bundle=bundle), relative)


# ---------------------------------------------------------------------------
# 9.  The governance record
# ---------------------------------------------------------------------------

class ContextRecord(Phase4FH21TestCase):

    def test_the_context_changed_only_by_an_appended_notice_paragraph(self):
        for key in self.baseline_context:
            if key == "contextNotice":
                continue
            with self.subTest(key=key):
                self.assertEqual(self.baseline_context[key],
                                 self.context_document[key])
        self.assertEqual(set(self.baseline_context),
                         set(self.context_document))

    def test_the_historical_notice_text_is_untouched(self):
        base = self.baseline_context["contextNotice"]
        live = self.context_document["contextNotice"]
        self.assertTrue(live.startswith(base))
        self.assertEqual(base + H21.H21_CONTEXT_NOTICE_SUFFIX, live)

    def test_the_appended_notice_is_truthful_about_what_h21_did(self):
        suffix = H21.H21_CONTEXT_NOTICE_SUFFIX
        for claim in (
                "Phase 4F-H2.1 is governance only",
                "exactly one product-approval acceptance to each of the 44 "
                "patterns H2 changed",
                "All 45 patterns are now approved",
                "product-owner-001",
                "freshly recomputed CURRENT tier-3 scope digest",
                "no stale H2 or F2 digest was reused",
                "it deliberately received no second approval",
                "No learner content changed",
                "reopen events remain 0",
                UNTOUCHED):
            with self.subTest(claim=claim):
                self.assertIn(claim, suffix)

    def test_the_notice_disclaims_language_review_and_shipping(self):
        suffix = H21.H21_CONTEXT_NOTICE_SUFFIX
        for disclaimer in (
                "it is not a new linguistic, reference or native-speaker "
                "review",
                "the Polish was not authored or externally verified by the "
                "owner",
                "is never a language judgement",
                "audio remains deferred and no audio was enabled",
                "nothing was frozen, released or projected to runtime"):
            with self.subTest(disclaimer=disclaimer):
                self.assertIn(disclaimer, suffix)


# ---------------------------------------------------------------------------
# 10.  File footprint
# ---------------------------------------------------------------------------

class FileFootprint(Phase4FH21TestCase):

    def footprint(self):
        status = git("status", "--porcelain")
        self.assertEqual(0, status.returncode, status.stderr)
        changed = {line[3:].strip().strip('"')
                   for line in status.stdout.splitlines() if line.strip()}
        committed = git("diff", "--name-only", BASELINE_COMMIT, "HEAD")
        if committed.returncode == 0:
            changed |= {line.strip() for line in committed.stdout.splitlines()
                        if line.strip()}
        return {path for path in changed if path}

    def test_this_phase_touched_only_editorial_tests_and_reports(self):
        unexpected = sorted(
            path for path in self.footprint()
            if not path.startswith(("tests/", "reports/", "editorial/"))
            and not is_only_the_h3_ui_wording(path)
            and not is_only_the_i1_activation(path))
        self.assertEqual([], unexpected, f"unexpected footprint: {unexpected}")

    def test_only_the_two_editorial_files_moved(self):
        editorial = sorted(path for path in self.footprint()
                           if path.startswith("editorial/"))
        self.assertEqual([CONTEXT_PATH, CORPUS_PATH], editorial)

    def test_the_phase_owned_artifacts_exist(self):
        for relative in (SUMMARY_PATH, MATRIX_PATH, NORMALISER_PATH,
                         "tests/test_priority7_phase4fh21.py"):
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).exists())


# ---------------------------------------------------------------------------
# 11.  Negative controls
# ---------------------------------------------------------------------------

class NegativeControls(Phase4FH21TestCase):

    def normalised(self, corpus):
        return H21.without_phase_4fh21_product_reapproval(corpus)

    # -- a missing approval ------------------------------------------------

    def test_a_missing_h21_approval_is_refused_by_the_normaliser(self):
        corpus = self.mutated()
        pattern = self.a_changed_pattern(corpus)
        pattern["reviewEvents"].pop()
        pattern["reviewState"] = "editorial-reviewed"
        self.assertEqual("partial", H21.phase_4fh21_layer_state(corpus))
        with self.assertRaises(AssertionError):
            self.normalised(corpus)

    def test_a_missing_approval_left_claiming_approved_is_refused(self):
        corpus = self.mutated()
        pattern = self.a_changed_pattern(corpus)
        pattern["reviewEvents"].pop()
        self.assertIn("REVIEW_STATE_MISMATCH",
                      codes(validate_editorial(corpus, build_context())))

    # -- an approval on the untouched pattern ------------------------------

    def test_an_approval_on_the_untouched_pattern_is_visible_and_refused(self):
        corpus = self.mutated()
        lemma, meaning, pattern = rows_by_id(corpus)[UNTOUCHED]
        pattern["reviewEvents"].append({
            "kind": "product-approval", "decision": "accept",
            "scopeVersion": 1,
            "scopeDigest": stage_digests(lemma, meaning, pattern)["tier3"],
            "reviewerRef": OWNER, "reviewedAt": H21_DATE,
            "note": H21.H21_NOTE})
        self.assertIn("REVIEW_DUPLICATE_STAGE_ACCEPTANCE",
                      codes(validate_editorial(corpus, build_context())))
        survivor = rows_by_id(self.normalised(corpus))[UNTOUCHED][2]
        self.assertEqual(2, len(approvals_of(survivor)))

    # -- a duplicate approval on a changed pattern -------------------------

    def test_a_duplicated_new_approval_is_not_absorbed(self):
        corpus = self.mutated()
        pattern = self.a_changed_pattern(corpus)
        pattern["reviewEvents"].append(copy.deepcopy(pattern["reviewEvents"][-1]))
        self.assertIn("REVIEW_DUPLICATE_STAGE_ACCEPTANCE",
                      codes(validate_editorial(corpus, build_context())))
        self.assertEqual("partial", H21.phase_4fh21_layer_state(corpus))
        with self.assertRaises(AssertionError):
            self.normalised(corpus)

    # -- a wrong or nonhuman reviewer --------------------------------------

    def test_a_wrong_reviewer_ref_is_rejected_and_survives_normalisation(self):
        corpus = self.mutated()
        pattern = self.a_changed_pattern(corpus)
        pattern["reviewEvents"][-1]["reviewerRef"] = NATIVE_REVIEWER
        self.assertIn("REVIEWER_ROLE",
                      codes(validate_editorial(corpus, build_context())))
        with self.assertRaises(AssertionError):
            self.normalised(corpus)

    def test_an_unregistered_reviewer_ref_is_rejected(self):
        corpus = self.mutated()
        pattern = self.a_changed_pattern(corpus)
        pattern["reviewEvents"][-1]["reviewerRef"] = "product-owner-002"
        self.assertIn("REVIEWER_REGISTRY_DANGLING",
                      codes(validate_editorial(corpus, build_context())))

    def test_an_actor_ref_in_place_of_a_reviewer_ref_is_rejected(self):
        corpus = self.mutated()
        pattern = self.a_changed_pattern(corpus)
        event = pattern["reviewEvents"][-1]
        del event["reviewerRef"]
        event["actorRef"] = EDITORIAL_ACTOR
        found = codes(validate_editorial(corpus, build_context()))
        self.assertIn("SCHEMA_REQUIRED", found)
        self.assertIn("SCHEMA_UNKNOWN_FIELD", found)
        with self.assertRaises(AssertionError):
            self.normalised(corpus)

    # -- a wrong date -------------------------------------------------------

    def test_a_future_reviewed_at_is_rejected(self):
        corpus = self.mutated()
        pattern = self.a_changed_pattern(corpus)
        pattern["reviewEvents"][-1]["reviewedAt"] = "2026-08-19"
        self.assertIn("DATE_IN_FUTURE",
                      codes(validate_editorial(corpus, build_context())))

    def test_a_backdated_reviewed_at_breaks_the_append_only_order(self):
        corpus = self.mutated()
        pattern = self.a_changed_pattern(corpus)
        pattern["reviewEvents"][-1]["reviewedAt"] = "2026-08-16"
        self.assertIn("REVIEW_EVENT_ORDER",
                      codes(validate_editorial(corpus, build_context())))

    def test_a_wrong_date_survives_normalisation(self):
        corpus = self.mutated()
        pattern = self.a_changed_pattern(corpus)
        pattern["reviewEvents"][-1]["reviewedAt"] = "2026-08-17"
        with self.assertRaises(AssertionError):
            self.normalised(corpus)

    # -- a stale or wrong digest -------------------------------------------

    def test_a_stale_tier_three_digest_is_rejected(self):
        corpus = self.mutated()
        pattern = self.a_changed_pattern(corpus)
        pattern["reviewEvents"][-1]["scopeDigest"] = approvals_of(pattern)[0][
            "scopeDigest"]
        self.assertIn("REVIEW_STATE_MISMATCH",
                      codes(validate_editorial(corpus, build_context())))

    def test_a_repinned_digest_survives_normalisation(self):
        corpus = self.mutated()
        pattern = self.a_changed_pattern(corpus)
        pattern["reviewEvents"][-1]["scopeDigest"] = "sha256:" + "0" * 64
        with self.assertRaises(AssertionError):
            self.normalised(corpus)

    def test_a_changed_note_survives_normalisation(self):
        corpus = self.mutated()
        pattern = self.a_changed_pattern(corpus)
        pattern["reviewEvents"][-1]["note"] = "Approved, no caveats at all."
        with self.assertRaises(AssertionError):
            self.normalised(corpus)

    # -- approval ahead of editorial currency ------------------------------

    def test_an_approval_before_editorial_currency_derives_nothing(self):
        """Strip the fresh tier-2 acceptance: the approval stops advancing."""
        corpus = self.mutated()
        lemma, meaning, pattern = rows_by_id(corpus)[
            sorted(H21.H21_EXPECTED_PATTERN_IDS)[0]]
        events = pattern["reviewEvents"]
        index = max(position for position, event in enumerate(events)
                    if event["kind"] == "editorial-review"
                    and event["decision"] == "accept")
        events.pop(index)
        self.assertEqual("reference-verified",
                         derived_state(lemma, meaning, pattern))
        self.assertIn("REVIEW_STATE_MISMATCH",
                      codes(validate_editorial(corpus, build_context())))

    def test_an_approval_after_an_unresolved_change_request_derives_nothing(self):
        corpus = self.mutated()
        lemma, meaning, pattern = rows_by_id(corpus)[
            sorted(H21.H21_EXPECTED_PATTERN_IDS)[0]]
        pattern["reviewEvents"].insert(len(pattern["reviewEvents"]) - 1, {
            "kind": "editorial-review", "decision": "changes-requested",
            "actorRef": EDITORIAL_ACTOR, "reviewedAt": H21_DATE,
            "note": "Second thoughts about the corrected wording."})
        self.assertEqual("reference-verified",
                         derived_state(lemma, meaning, pattern))

    # -- content edited after the approval digest was computed -------------

    def test_a_changed_example_after_approval_is_rejected(self):
        corpus = self.mutated()
        pattern = self.a_changed_pattern(corpus)
        pattern["examples"][0]["textPl"] = "Zupełnie inne zdanie."
        self.assertIn("REVIEW_STATE_MISMATCH",
                      codes(validate_editorial(corpus, build_context())))

    def test_a_changed_learner_explanation_after_approval_is_rejected(self):
        corpus = self.mutated()
        pattern = self.a_changed_pattern(corpus)
        pattern["learnerExplanationEn"] += " Extra sentence."
        self.assertIn("REVIEW_STATE_MISMATCH",
                      codes(validate_editorial(corpus, build_context())))

    def test_a_content_edit_survives_normalisation_into_the_h2_layer(self):
        """H2.1 comes off cleanly; H2 then refuses the mutated row."""
        corpus = self.mutated()
        pattern = self.a_changed_pattern(corpus)
        pattern["learnerExplanationEn"] += " Extra sentence."
        normalised = H2.without_phase_4fh2_content_completion(
            self.normalised(corpus))
        survivor = rows_by_id(normalised)[pattern["id"]][2]
        self.assertIn("Extra sentence.", survivor["learnerExplanationEn"])
        self.assertNotEqual(
            self.baseline_rows[pattern["id"]][2]["learnerExplanationEn"],
            survivor["learnerExplanationEn"])

    # -- extra events -------------------------------------------------------

    def test_an_extra_reference_verification_is_refused(self):
        corpus = self.mutated()
        lemma, meaning, pattern = rows_by_id(corpus)[
            sorted(H21.H21_EXPECTED_PATTERN_IDS)[0]]
        pattern["reviewEvents"].append({
            "kind": "reference-verification", "decision": "accept",
            "scopeVersion": 1,
            "scopeDigest": stage_digests(lemma, meaning, pattern)["tier1"],
            "supportingEvidenceDigests": sorted(
                {T.evidence_digest(record) for record in pattern["evidence"]}),
            "actorRef": REFERENCE_ACTOR, "reviewedAt": H21_DATE,
            "note": "An unauthorised extra tier-1 pass."})
        self.assertNotEqual([], validate_editorial(corpus, build_context()))
        with self.assertRaises(AssertionError):
            self.normalised(corpus)

    def test_an_extra_correction_is_refused(self):
        corpus = self.mutated()
        pattern = self.a_changed_pattern(corpus)
        pattern["reviewEvents"].append({
            "kind": "correction", "decision": "accept", "reviewerRef": OWNER,
            "reviewedAt": H21_DATE, "note": "An unauthorised extra correction."})
        # A trailing correction is inert for the derived state by design -- it
        # licenses future change rather than retracting the approval -- so the
        # guard that catches it is the layer, not the validator.
        self.assertEqual("partial", H21.phase_4fh21_layer_state(corpus))
        with self.assertRaises(AssertionError):
            self.normalised(corpus)

    def test_a_reopen_event_is_refused(self):
        corpus = self.mutated()
        pattern = self.a_changed_pattern(corpus)
        pattern["reviewEvents"].append({
            "kind": "reopen", "decision": "accept", "reviewerRef": OWNER,
            "reviewedAt": H21_DATE, "note": "An unauthorised reopen."})
        found = codes(validate_editorial(corpus, build_context()))
        self.assertIn("REVIEW_REOPEN_ORDER", found)
        with self.assertRaises(AssertionError):
            self.normalised(corpus)

    def test_a_future_product_approval_is_refused(self):
        corpus = self.mutated()
        lemma, meaning, pattern = rows_by_id(corpus)[
            sorted(H21.H21_EXPECTED_PATTERN_IDS)[0]]
        pattern["reviewEvents"].append({
            "kind": "product-approval", "decision": "accept",
            "scopeVersion": 1,
            "scopeDigest": stage_digests(lemma, meaning, pattern)["tier3"],
            "reviewerRef": OWNER, "reviewedAt": H21_DATE,
            "note": "A later phase approving the same scope again."})
        self.assertIn("REVIEW_DUPLICATE_STAGE_ACCEPTANCE",
                      codes(validate_editorial(corpus, build_context())))
        with self.assertRaises(AssertionError):
            self.normalised(corpus)

    # -- audio, activity and shipping --------------------------------------

    def test_enabling_audio_on_an_example_is_refused(self):
        corpus = self.mutated()
        pattern = self.a_changed_pattern(corpus)
        pattern["examples"][0]["audioEligible"] = True
        self.assertIn("AUDIO_NOT_AUTHORIZED",
                      codes(validate_editorial(corpus, build_context())))

    def test_enabling_an_activity_is_refused(self):
        corpus = self.mutated()
        pattern = self.a_changed_pattern(corpus)
        pattern["activityEligibility"] = ["choose-form"]
        self.assertNotEqual([], validate_editorial(corpus, build_context()))

    def test_a_runtime_materialisation_would_be_outside_the_footprint(self):
        # It was outside H2.1's footprint, and it is inside I1's.  What
        # survives is that the runtime present here is exactly the pinned I1
        # release artifact and that H2.1 itself committed nothing to that path.
        self.assertEqual("complete", i1_bundle().state)
        # It was outside H2.1's footprint: the path is absent from H2.1's own
        # baseline commit, so whatever tracks it now entered afterwards -- and
        # the bundle check above proves what entered is exactly the pinned I1
        # release, moving together with the shell and the worker.
        at_baseline = subprocess.run(
            ["git", "cat-file", "-e", f"{BASELINE_COMMIT}:{PUBLIC_RUNTIME_PATH}"],
            cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertNotEqual(0, at_baseline.returncode)
        tracked = git("ls-files", PUBLIC_RUNTIME_PATH).stdout.strip()
        self.assertIn(tracked, ("", PUBLIC_RUNTIME_PATH))


# ---------------------------------------------------------------------------
# 12.  The normaliser contract
# ---------------------------------------------------------------------------

class NormaliserContract(Phase4FH21TestCase):

    def test_the_normaliser_reproduces_the_baseline_corpus_byte_for_byte(self):
        self.assertEqual(
            git_blob(CORPUS_PATH),
            H21.without_phase_4fh21_corpus_text(read(CORPUS_PATH)))

    def test_the_normaliser_reproduces_the_baseline_context_byte_for_byte(self):
        self.assertEqual(
            git_blob(CONTEXT_PATH),
            H21.without_phase_4fh21_context_text(read(CONTEXT_PATH)))

    def test_the_document_normaliser_reproduces_the_baseline_documents(self):
        self.assertEqual(
            self.baseline,
            H21.without_phase_4fh21_product_reapproval(self.corpus))
        self.assertEqual(
            self.baseline_context,
            H21.without_phase_4fh21_context(self.context_document))

    def test_the_normaliser_is_idempotent_on_an_already_reverted_corpus(self):
        once = H21.without_phase_4fh21_product_reapproval(self.corpus)
        self.assertEqual(
            once, H21.without_phase_4fh21_product_reapproval(once))

    def test_the_layer_state_is_complete_live_and_absent_at_the_baseline(self):
        self.assertEqual("complete", H21.phase_4fh21_layer_state(self.corpus))
        self.assertEqual("absent", H21.phase_4fh21_layer_state(self.baseline))

    def test_the_text_normaliser_refuses_a_noncanonical_corpus_form(self):
        with self.assertRaises(AssertionError):
            H21.without_phase_4fh21_corpus_text(
                json.dumps(self.corpus, ensure_ascii=False))

    def test_the_normaliser_refuses_an_identity_outside_the_transition(self):
        with self.assertRaises(KeyError):
            H21.approved_h21_event("vp-p-not-a-real-pattern-000000000000")

    def test_the_pinned_transition_is_forty_four_rows_and_forty_four_events(self):
        self.assertEqual(CHANGED_COUNT, len(H21.H21_EXPECTED_PATTERN_IDS))
        self.assertEqual(CHANGED_COUNT, len(H21.H21_EXPECTED_SCOPE_DIGESTS))
        self.assertEqual(set(H21.H21_EXPECTED_PATTERN_IDS),
                         set(H21.H21_EXPECTED_SCOPE_DIGESTS))
        self.assertEqual(CHANGED_COUNT,
                         len(set(H21.H21_EXPECTED_SCOPE_DIGESTS.values())))

    def test_the_normaliser_never_reads_a_live_row_to_decide_the_revert(self):
        """It imports only copy and json, opens nothing, computes no digest."""
        source = read(NORMALISER_PATH)
        self.assertEqual(
            ["copy", "json"],
            sorted(line.split()[1] for line in source.splitlines()
                   if line.startswith("import ")))
        body = source.split('"""', 2)[2]
        for forbidden in ("open(", "Path(", "subprocess.", "read_text",
                          "review_scope_digest", "priority7_tooling",
                          "hashlib", "sha256("):
            with self.subTest(token=forbidden):
                self.assertNotIn(forbidden, body)

    def test_the_h2_layer_still_comes_off_underneath_this_one(self):
        self.assertEqual(
            json.loads(git_blob(CORPUS_PATH, "4141872721d097e53c40f05e83b3ea730c38eff0")),
            H2.without_phase_4fh2_content_completion(
                H21.without_phase_4fh21_product_reapproval(self.corpus)))


# ---------------------------------------------------------------------------
# 13.  Reports
# ---------------------------------------------------------------------------

class Reports(Phase4FH21TestCase):

    def test_the_matrix_lists_exactly_the_forty_four_approvals(self):
        with (ROOT / MATRIX_PATH).open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(CHANGED_COUNT, len(rows))
        self.assertEqual(set(H21.H21_EXPECTED_PATTERN_IDS),
                         {row["patternId"] for row in rows})
        for row in rows:
            with self.subTest(pattern_id=row["patternId"]):
                lemma, meaning, pattern = self.rows[row["patternId"]]
                self.assertEqual(row["priorState"], "editorial-reviewed")
                self.assertEqual(row["finalState"], pattern["reviewState"])
                self.assertEqual(row["reviewerRef"], OWNER)
                self.assertEqual(row["reviewedAt"], H21_DATE)
                self.assertEqual(
                    row["tier3ScopeDigest"],
                    stage_digests(lemma, meaning, pattern)["tier3"])
                self.assertEqual(
                    row["supersededDigest"], approvals_of(pattern)[0][
                        "scopeDigest"])
                self.assertNotEqual(row["supersededDigest"],
                                    row["tier3ScopeDigest"])

    def test_the_matrix_never_lists_the_untouched_pattern(self):
        self.assertNotIn(UNTOUCHED, read(MATRIX_PATH))

    def test_the_summary_states_the_transition_and_the_verdict(self):
        text = read(SUMMARY_PATH)
        for claim in (BASELINE_COMMIT, BASELINE_TREE, "44", "45", OWNER,
                      "2026-08-18", UNTOUCHED, "**Verdict: GO**"):
            with self.subTest(claim=claim):
                self.assertIn(claim, text)

    def test_the_summary_does_not_claim_language_review_or_shipping(self):
        lowered = read(SUMMARY_PATH).lower()
        for forbidden in ("native-speaker review was performed",
                          "professional linguistic review was performed",
                          "audio was enabled", "released to production"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, lowered)


if __name__ == "__main__":
    unittest.main()
