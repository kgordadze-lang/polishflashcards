"""Priority 7 Phase 4F-E1 — final editorial-review governance advancement.

This phase performed no content review.  The substantive final editorial
review was completed by Phases 4F-D1, 4F-D2, 4F-D3 and 4F-D3.1; Phase 4F-E1
records the governance events that make it visible to the tooling.  This suite
treats the delivered candidate as read-only and proves, against the immutable
baseline ``5aef7e4a447b57f862dabf098b575a431f5f8484``:

1.  **Exactly 45 acceptances, and nothing more.**  One qualifying
    ``editorial-review`` acceptance per pattern, 45 rows at
    ``editorial-reviewed``, every event digest recomputing against the pattern
    it sits on, and no second acceptance anywhere.
2.  **The identities are truthful and independent.**  Two nonhuman actors,
    each ``human: false``, each holding only the ``editorial-review`` role;
    the editorial actor distinct from the reference actor, from the
    example-generation actor and from its own corroborator; no human invented
    anywhere; ``authorRegistry`` still empty; AB unchanged and eventless.
3.  **Nothing above tier 2 happened.**  No product approval, no ``approved``
    row, no freeze, no release authorisation, no runtime projection, no
    ``patternDataRevision`` increment.
4.  **History is intact.**  All 47 reference acceptances stand byte-identical,
    including the two superseded ``mówić`` events, and no reference event was
    created, altered or removed.
5.  **Content did not move.**  Every learner-facing and provenance field is
    baseline-identical; the three D3.1 corrections stand exactly as
    adjudicated; ``P7-NR-011`` is untouched; tooling and every shipping file
    are byte-identical.
6.  **The boundary has teeth.**  A missing event, a duplicate acceptance, a
    stale digest, a wrong role, an actor that is also the reference or
    example-generation actor, a self-corroborating actor, an invented human,
    an unauthorised wording change, a mutated example origin, a mutated
    reference event, a premature product approval and a premature ``approved``
    state are each rejected — by the validator, by the derived state, or by
    surviving the Phase 4F-E1 normaliser and still breaking the guard.

Every mutation below is applied to an in-memory copy.  Nothing here writes to
the corpus, the context, the tooling or any shipping file.

Run:  python3 -m unittest tests.test_priority7_phase4fe1
"""

from __future__ import annotations

import collections
import copy
import csv
import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import os.path as _e1_os_path
import sys as _e1_sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in _e1_sys.path:
    _e1_sys.path.insert(0, str(ROOT))
_E1_DIR = _e1_os_path.dirname(_e1_os_path.abspath(__file__))
if _E1_DIR not in _e1_sys.path:
    _e1_sys.path.insert(0, _E1_DIR)

import priority7_tooling as T  # noqa: E402
from priority7_tooling import ValidationContext, validate_editorial  # noqa: E402

import priority7_phase4fe1_normalizer as E1  # noqa: E402

CORPUS_PATH = "editorial/verb-pattern-candidates.json"
CONTEXT_PATH = "editorial/priority-7-authoring-context.json"
MATRIX_PATH = "reports/priority-7-phase-4fe1-editorial-review-matrix.csv"
SUMMARY_PATH = "reports/priority-7-phase-4fe1-summary.md"

#: Phase 4F-E1 arrived on top of this commit.
BASELINE_COMMIT = "5aef7e4a447b57f862dabf098b575a431f5f8484"
BASELINE_TREE = "2dc8d799d5dd22056139abee629a8f98907932ac"

#: Independent expected values, written from the phase brief rather than read
#: out of the corpus, so a joint edit to corpus and artifact cannot make this
#: suite agree with itself.
EDITORIAL_ACTOR = "priority7-editorial-review"
CORROBORATING_ACTOR = "priority7-editorial-corroboration"
REFERENCE_ACTOR = "priority7-reference-analysis"
GENERATION_ACTOR = "priority7-example-generation"
HUMAN_REVIEWER = "native-reviewer-001"

PATTERN_COUNT = 45
EXAMPLE_COUNT = 29
REFERENCE_ACCEPT_COUNT = 47
EDITORIAL_ACCEPT_COUNT = 45
REVIEWED_AT = "2026-08-17"

TIER_ONE = "external-verification"
TIER_TWO = "native-linguistic"

#: The exact post-D3.1 wording the three corrected rows must still carry, and
#: the pre-D3.1 wording that must be gone.  Written out here rather than read
#: from the D3 artifact.
D31_FINAL_WORDING = {
    "vp-p-dbac-take-care-of-o-accusative-target-d3e3eb63129c": {
        "examples[0].en": ("I look after my fitness every day.",
                           "I work on my fitness every day."),
    },
    "vp-p-lubic-enjoy-thing-or-activity-infinitive-activity-be3742b7ce45": {
        "examples[0].en": ("I like reading before sleep.",
                           "I like reading before bed."),
    },
    "vp-p-podobac-sie-appeal-to-nominative-stimulus-dative-experiencer"
    "-ef199e675ee9": {
        "learnerExplanationEn": (
            "The thing liked is the subject and the person is Dative: "
            "ten film podoba mi się.",
            "The thing liked is the subject and the person is Dative: "
            "ten film mi się podoba."),
        "errorNotes[0].guidanceEn": (
            "The thing liked is the subject and the person is Dative: "
            "ten film podoba mi się.",
            "The thing liked is the subject and the person is Dative: "
            "ten film mi się podoba."),
    },
}

#: The row whose D2 blocker was overturned: byte-identical to the baseline.
OVERTURNED_PATTERN = (
    "vp-p-dziekowac-thank-dative-recipient-za-accusative-057197dd300f")

#: Files Phase 4F-E1 was forbidden to touch.  Compared at the phase-owned
#: revision, so a later phase editing one of them cannot fail this claim.
UNCHANGED_FILES = (
    "priority7_tooling.py",
    "data-a1.js",
    "data-a2.js",
    "data-b1.js",
    "data-grammar.js",
    "data-verbs.js",
    "data-scenarios.js",
    "data-podcasts.js",
    "pp-verb-patterns.js",
    "pp-answer.js",
    "pp-distractor.js",
    "pp-migrate.js",
    "pp-usage.js",
    "index.html",
    "sw.js",
    "build_pages.py",
    "validate_content.py",
    "verify_audio.py",
    "manifest.json",
    "sitemap.xml",
    "audio-manifest.json",
    "reports/priority-7-phase-4fd1-final-editorial-matrix.csv",
    "reports/priority-7-phase-4fd1-summary.md",
    "reports/priority-7-phase-4fd2-blind-final-editorial-matrix.csv",
    "reports/priority-7-phase-4fd2-summary.md",
    "reports/priority-7-phase-4fd3-adjudication.csv",
    "reports/priority-7-phase-4fd31-summary.md",
)

#: The two documents this phase was allowed to change.
E1_EDITED_FILES = {CORPUS_PATH, CONTEXT_PATH}

#: The phase's own new artifacts.
E1_ARTIFACTS = {
    MATRIX_PATH,
    SUMMARY_PATH,
    "tests/test_priority7_phase4fe1.py",
    "tests/priority7_phase4fe1_normalizer.py",
}

#: The historical suites repaired to revert this phase's approved governance
#: work.  A path manifest; the repair itself is proved by running them.
E1_HISTORICAL_TEST_REPAIRS = {
    f"tests/test_priority7_phase{name}.py"
    for name in ("3b", "3c", "3d1", "3fa", "4c", "4e", "4e1", "4fa", "4fb3b",
                 "4fc2", "4fc2c", "4fc2d", "4fd31", "5a")
}

#: Immutable Phase 4F-E1 transition.  Later phases may add arbitrary paths;
#: they sit outside the baseline -> first-descendant boundary and therefore
#: cannot widen this set.
E1_CANDIDATE_PATHS = E1_EDITED_FILES | E1_ARTIFACTS | E1_HISTORICAL_TEST_REPAIRS


# ---------------------------------------------------------------------------
# phase-owned reads: the candidate, never arbitrary future HEAD
# ---------------------------------------------------------------------------

def git(*arguments):
    return subprocess.run(["git", "-C", str(ROOT), *arguments],
                          capture_output=True, text=True, check=False)


def candidate_revision():
    """Return the committed Phase 4F-E1 revision, or None while uncommitted.

    Phase 4F-E1 is integrated as the first descendant of the immutable
    baseline.  Once later commits exist, that first descendant remains the
    phase-owned candidate; arbitrary live HEAD additions never become part of
    Phase 4F-E1, and a later product-approval phase can add files, add events
    and move review state without any claim below changing.
    """
    head = git("rev-parse", "HEAD")
    if head.returncode != 0:
        raise AssertionError(head.stderr)
    if head.stdout.strip() == BASELINE_COMMIT:
        return None
    revisions = git("rev-list", "--reverse", "--ancestry-path",
                    f"{BASELINE_COMMIT}..HEAD")
    if revisions.returncode != 0:
        raise AssertionError(revisions.stderr)
    descendants = revisions.stdout.split()
    if not descendants:
        raise AssertionError("baseline is not an ancestor of HEAD")
    return descendants[0]


def candidate_blob(path):
    """Read ``path`` from the phase-owned candidate.

    Before integration that is the working tree; after integration it is the
    baseline's first descendant, so later work is deliberately irrelevant.
    """
    revision = candidate_revision()
    if revision is None:
        return (ROOT / path).read_text(encoding="utf-8")
    result = git("show", f"{revision}:{path}")
    if result.returncode != 0:
        raise AssertionError(f"candidate blob missing: {path}")
    return result.stdout


def candidate_footprint():
    """Exactly the phase-owned Phase 4F-E1 transition paths."""
    revision = candidate_revision()
    if revision is None:
        touched = set(git("diff", "--name-only", BASELINE_COMMIT).
                      stdout.splitlines())
        touched |= set(git("ls-files", "--others", "--exclude-standard").
                       stdout.splitlines())
        return touched
    result = git("diff", "--name-only", BASELINE_COMMIT, revision)
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return set(result.stdout.splitlines())


def baseline_blob(path):
    result = git("show", f"{BASELINE_COMMIT}:{path}")
    if result.returncode != 0:
        raise AssertionError(f"baseline blob missing: {path}")
    return result.stdout


def candidate_corpus():
    return json.loads(candidate_blob(CORPUS_PATH))


def candidate_context():
    return json.loads(candidate_blob(CONTEXT_PATH))


def baseline_corpus():
    return json.loads(baseline_blob(CORPUS_PATH))


def baseline_context():
    return json.loads(baseline_blob(CONTEXT_PATH))


def iter_patterns(corpus):
    for lemma in corpus["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                yield lemma, meaning, pattern


def patterns_by_id(corpus):
    return {pattern["id"]: (lemma, meaning, pattern)
            for lemma, meaning, pattern in iter_patterns(corpus)}


def editorial_events(pattern):
    return [event for event in pattern["reviewEvents"]
            if event["kind"] == "editorial-review"]


def reference_events(pattern):
    return [event for event in pattern["reviewEvents"]
            if event["kind"] == "reference-verification"]


def build_context(document=None, *, corpus_root=True):
    document = document or candidate_context()
    return ValidationContext(
        source_registry=document["sourceRegistry"],
        reviewer_registry=document["reviewerRegistry"],
        author_registry=document["authorRegistry"],
        allocation_registry=document["allocationRegistry"],
        editorial_actor_registry=document["editorialActorRegistry"],
        repository_index=T.repository_index_from_root(ROOT)
        if corpus_root else None)


def resolve(container, path):
    """Resolve a dotted/indexed field path such as ``examples[0].en``."""
    value = container
    for part in path.split("."):
        if part.endswith("]"):
            name, index = part[:-1].split("[")
            value = value[name][int(index)]
        else:
            value = value[part]
    return value


def assign(container, path, new_value):
    parts = path.split(".")
    value = container
    for part in parts[:-1]:
        if part.endswith("]"):
            name, index = part[:-1].split("[")
            value = value[name][int(index)]
        else:
            value = value[part]
    last = parts[-1]
    if last.endswith("]"):
        name, index = last[:-1].split("[")
        value[name][int(index)] = new_value
    else:
        value[last] = new_value


class E1Case(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.corpus = candidate_corpus()
        cls.context = candidate_context()
        cls.baseline = baseline_corpus()
        cls.baseline_context_document = baseline_context()
        cls.current = patterns_by_id(cls.corpus)
        cls.before = patterns_by_id(cls.baseline)


# ---------------------------------------------------------------------------
# §1  the baseline this suite argues from
# ---------------------------------------------------------------------------

class BaselineIntegrityTests(E1Case):

    def test_the_pinned_baseline_commit_and_tree_agree(self):
        tree = git("rev-parse", f"{BASELINE_COMMIT}^{{tree}}").stdout.strip()
        self.assertEqual(BASELINE_TREE, tree)

    def test_the_repository_has_no_remote(self):
        self.assertEqual("", git("remote").stdout.strip())

    def test_the_baseline_stood_entirely_at_reference_verified(self):
        states = collections.Counter(
            pattern["reviewState"] for _, _, pattern in
            iter_patterns(self.baseline))
        self.assertEqual({"reference-verified": PATTERN_COUNT}, dict(states))
        self.assertEqual(
            [], [event for _, _, pattern in iter_patterns(self.baseline)
                 for event in pattern["reviewEvents"]
                 if event["kind"] != "reference-verification"])


# ---------------------------------------------------------------------------
# §2  exactly 45 qualifying acceptances
# ---------------------------------------------------------------------------

class AcceptanceTests(E1Case):

    def test_there_are_exactly_forty_five_patterns(self):
        self.assertEqual(PATTERN_COUNT, len(self.current))

    def test_every_pattern_is_editorial_reviewed(self):
        states = collections.Counter(
            pattern["reviewState"] for _, _, pattern in
            iter_patterns(self.corpus))
        self.assertEqual({"editorial-reviewed": PATTERN_COUNT}, dict(states))

    def test_exactly_forty_five_new_editorial_acceptances_exist(self):
        events = [event for _, _, pattern in iter_patterns(self.corpus)
                  for event in editorial_events(pattern)]
        self.assertEqual(EDITORIAL_ACCEPT_COUNT, len(events))
        self.assertEqual({"accept"}, {event["decision"] for event in events})

    def test_each_pattern_carries_exactly_one_editorial_acceptance(self):
        for pattern_id, (_, _, pattern) in self.current.items():
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(1, len(editorial_events(pattern)))

    def test_the_editorial_event_is_always_the_last_event(self):
        """Append-only: tier 2 sits after the tier-1 acceptance it rests on."""
        for pattern_id, (_, _, pattern) in self.current.items():
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual("editorial-review",
                                 pattern["reviewEvents"][-1]["kind"])
                self.assertEqual("reference-verification",
                                 pattern["reviewEvents"][-2]["kind"])

    def test_every_event_digest_recomputes_against_its_pattern(self):
        for pattern_id, (lemma, meaning, pattern) in self.current.items():
            with self.subTest(pattern_id=pattern_id):
                event = editorial_events(pattern)[0]
                self.assertEqual(
                    T.review_scope_digest(
                        "editorial-review", lemma, meaning, pattern),
                    event["scopeDigest"])
                self.assertEqual(T.SCOPE_VERSION, event["scopeVersion"])

    def test_the_editorial_digest_is_the_tier_two_scope(self):
        """Not tier 1, and not tier 3: the locked native-linguistic tier."""
        for pattern_id, (lemma, meaning, pattern) in self.current.items():
            with self.subTest(pattern_id=pattern_id):
                event = editorial_events(pattern)[0]
                self.assertEqual(
                    T.review_scope_digest(
                        TIER_TWO, lemma, meaning, pattern),
                    event["scopeDigest"])
                self.assertNotEqual(
                    T.review_scope_digest(
                        TIER_ONE, lemma, meaning, pattern),
                    event["scopeDigest"])

    def test_no_d1_or_d2_era_digest_was_reused_on_the_corrected_rows(self):
        """The three D3.1 rows bind to their post-correction tier-2 scope."""
        for pattern_id in D31_FINAL_WORDING:
            with self.subTest(pattern_id=pattern_id):
                lemma, meaning, pattern = self.current[pattern_id]
                base_lemma, base_meaning, base_pattern = self.before[pattern_id]
                self.assertEqual(
                    T.review_scope_digest(
                        TIER_TWO, lemma, meaning, pattern),
                    editorial_events(pattern)[0]["scopeDigest"])
                # The pre-D3.1 tier-2 digest is a different value, so reusing
                # a D1/D2 baseline digest would have been detectable.
                self.assertEqual(
                    T.review_scope_digest(
                        TIER_TWO, base_lemma, base_meaning, base_pattern),
                    editorial_events(pattern)[0]["scopeDigest"],
                    "the D3.1 corrections were already in the baseline")

    def test_every_acceptance_carries_the_phase_date(self):
        for pattern_id, (_, _, pattern) in self.current.items():
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(
                    REVIEWED_AT, editorial_events(pattern)[0]["reviewedAt"])

    def test_no_acceptance_pins_evidence_digests(self):
        """Evidence pinning belongs to tier 1 and is refused here."""
        for pattern_id, (_, _, pattern) in self.current.items():
            with self.subTest(pattern_id=pattern_id):
                self.assertNotIn("supportingEvidenceDigests",
                                 editorial_events(pattern)[0])

    def test_no_acceptance_names_a_human_reviewer(self):
        for pattern_id, (_, _, pattern) in self.current.items():
            with self.subTest(pattern_id=pattern_id):
                self.assertNotIn("reviewerRef", editorial_events(pattern)[0])

    def test_recorded_blocking_findings_are_all_resolved(self):
        with_findings = {
            pattern_id for pattern_id, (_, _, pattern) in self.current.items()
            if "findings" in editorial_events(pattern)[0]}
        self.assertEqual(
            set(D31_FINAL_WORDING) | {OVERTURNED_PATTERN}, with_findings)
        for pattern_id in with_findings:
            _, _, pattern = self.current[pattern_id]
            for finding in editorial_events(pattern)[0]["findings"]:
                with self.subTest(pattern_id=pattern_id):
                    self.assertEqual("high", finding["severity"])
                    self.assertIs(True, finding["resolved"])
                    self.assertTrue(finding["resolutionNote"].strip())

    def test_the_tooling_derives_the_state_rather_than_trusting_it(self):
        """The state is replayed from the history, not read off the record."""
        for pattern_id, (lemma, meaning, pattern) in self.current.items():
            with self.subTest(pattern_id=pattern_id):
                scope = {stage: T.review_scope_digest(
                    stage, lemma, meaning, pattern) for stage in T.STAGE_KINDS}
                records = {T.evidence_digest(item): item
                           for item in pattern["evidence"]}
                currency = T._derive_review_currency(
                    pattern["reviewEvents"], pattern["releaseMode"],
                    scope, set(records), records)
                self.assertEqual("editorial-reviewed", currency.state)
                # Neither human flag may be raised by a nonhuman chain.
                self.assertIs(False, currency.human_native_review_current)
                self.assertIs(False, currency.human_verification_current)

    def test_the_candidate_validates_under_the_real_validator(self):
        self.assertEqual([], validate_editorial(self.corpus, build_context()))

    def test_the_cli_validator_accepts_the_candidate(self):
        """The documented invocation, run against the phase-owned candidate.

        The candidate is materialised into a temporary directory rather than
        read from the working tree, so a later phase editing these documents
        cannot make this historical claim fail.
        """
        with tempfile.TemporaryDirectory(prefix="priority7-4fe1-") as tmp:
            corpus = Path(tmp) / "corpus.json"
            context = Path(tmp) / "context.json"
            corpus.write_text(candidate_blob(CORPUS_PATH), encoding="utf-8")
            context.write_text(candidate_blob(CONTEXT_PATH), encoding="utf-8")
            result = subprocess.run(
                ["python3", "priority7_tooling.py", "validate-editorial",
                 "--context", str(context), "--repository-root", str(ROOT),
                 str(corpus)],
                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("valid", result.stdout)


# ---------------------------------------------------------------------------
# §3  identity, role and independence
# ---------------------------------------------------------------------------

class ActorIdentityTests(E1Case):

    def setUp(self):
        self.actors = self.context["editorialActorRegistry"]

    def test_exactly_two_new_actors_were_registered(self):
        self.assertEqual(
            {EDITORIAL_ACTOR, CORROBORATING_ACTOR},
            set(self.actors) -
            set(self.baseline_context_document["editorialActorRegistry"]))

    def test_both_new_actors_are_nonhuman(self):
        for actor_id in (EDITORIAL_ACTOR, CORROBORATING_ACTOR):
            with self.subTest(actor=actor_id):
                self.assertIs(False, self.actors[actor_id]["human"])

    def test_both_new_actors_hold_only_the_editorial_review_role(self):
        for actor_id in (EDITORIAL_ACTOR, CORROBORATING_ACTOR):
            with self.subTest(actor=actor_id):
                self.assertEqual(["editorial-review"],
                                 self.actors[actor_id]["roles"])
                for role in self.actors[actor_id]["roles"]:
                    self.assertIn(role, T.EDITORIAL_ACTOR_ROLES)

    def test_the_editorial_actor_is_not_the_reference_actor(self):
        self.assertNotEqual(EDITORIAL_ACTOR, REFERENCE_ACTOR)
        self.assertNotIn("reference-verification",
                         self.actors[EDITORIAL_ACTOR]["roles"])
        for pattern_id, (_, _, pattern) in self.current.items():
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(
                    {REFERENCE_ACTOR},
                    {event["actorRef"] for event in reference_events(pattern)})
                self.assertEqual(
                    EDITORIAL_ACTOR,
                    editorial_events(pattern)[0]["actorRef"])

    def test_the_editorial_actor_is_not_the_example_generation_actor(self):
        self.assertNotEqual(EDITORIAL_ACTOR, GENERATION_ACTOR)
        self.assertEqual(["example-generation"],
                         self.actors[GENERATION_ACTOR]["roles"])
        self.assertNotIn("editorial-review",
                         self.actors[GENERATION_ACTOR]["roles"])

    def test_every_acceptance_names_one_distinct_corroborator(self):
        for pattern_id, (_, _, pattern) in self.current.items():
            with self.subTest(pattern_id=pattern_id):
                event = editorial_events(pattern)[0]
                corroborating = event["corroboratingActorRefs"]
                self.assertEqual([CORROBORATING_ACTOR], corroborating)
                self.assertNotIn(event["actorRef"], corroborating)
                self.assertEqual(sorted(set(corroborating)), corroborating)
                for reference in corroborating:
                    self.assertIn("editorial-review",
                                  self.actors[reference]["roles"])
                    self.assertIs(False, self.actors[reference]["human"])

    def test_the_corroborator_is_neither_reference_nor_generation_actor(self):
        self.assertNotIn(CORROBORATING_ACTOR, {REFERENCE_ACTOR,
                                               GENERATION_ACTOR})

    def test_the_reference_actor_record_is_untouched(self):
        self.assertEqual(
            self.baseline_context_document["editorialActorRegistry"],
            {key: value for key, value in self.actors.items()
             if key not in {EDITORIAL_ACTOR, CORROBORATING_ACTOR}})

    def test_no_human_identity_was_invented(self):
        self.assertEqual({}, self.context["authorRegistry"])
        self.assertEqual({}, self.context["allocationRegistry"])
        self.assertEqual({HUMAN_REVIEWER},
                         set(self.context["reviewerRegistry"]))
        self.assertEqual(
            self.baseline_context_document["reviewerRegistry"],
            self.context["reviewerRegistry"])
        for actor_id, record in self.actors.items():
            with self.subTest(actor=actor_id):
                self.assertIs(False, record["human"])
        self.assertEqual(
            set(), set(self.actors) & set(self.context["reviewerRegistry"]))

    def test_ab_gained_no_event_and_no_new_authority(self):
        record = self.context["reviewerRegistry"][HUMAN_REVIEWER]
        self.assertEqual(["native-linguistic"], record["roles"])
        self.assertNotIn("ownerAllowsMultipleRoles", record)
        self.assertNotIn("acknowledgedReleaseModes", record)
        blob = candidate_blob(CORPUS_PATH)
        for token in (HUMAN_REVIEWER, "native-linguistic", "reviewerRef"):
            with self.subTest(token=token):
                self.assertNotIn(token, blob)

    def test_the_replayed_independence_rule_is_satisfied(self):
        for pattern_id, (_, _, pattern) in self.current.items():
            with self.subTest(pattern_id=pattern_id):
                issues = []
                T._replay_actor_independence(
                    pattern["reviewEvents"], "$events", issues)
                self.assertEqual([], issues)


# ---------------------------------------------------------------------------
# §4  nothing above tier 2 happened
# ---------------------------------------------------------------------------

class NoReleaseActionTests(E1Case):

    def test_no_product_approval_event_exists(self):
        self.assertEqual(
            [], [event for _, _, pattern in iter_patterns(self.corpus)
                 for event in pattern["reviewEvents"]
                 if event["kind"] == "product-approval"])

    def test_no_pattern_is_approved(self):
        self.assertNotIn("approved",
                         {pattern["reviewState"] for _, _, pattern
                          in iter_patterns(self.corpus)})

    def test_no_product_or_correction_authority_was_named(self):
        reviewers = self.context["reviewerRegistry"]
        for role in ("product-approval", "external-verification",
                     "reference-verification", "correction", "reopen"):
            with self.subTest(role=role):
                self.assertEqual(
                    [], [key for key, record in reviewers.items()
                         if role in record.get("roles", [])])

    def test_no_stage_outside_the_solo_chain_was_recorded(self):
        kinds = {event["kind"] for _, _, pattern in iter_patterns(self.corpus)
                 for event in pattern["reviewEvents"]}
        self.assertEqual({"reference-verification", "editorial-review"}, kinds)

    def test_the_release_mode_is_unchanged_on_every_row(self):
        self.assertEqual(
            {T.SOLO_MAINTAINER_MODE},
            {pattern["releaseMode"] for _, _, pattern
             in iter_patterns(self.corpus)})

    def test_no_freeze_release_or_runtime_projection_happened(self):
        # Read from the phase-owned candidate, not the live tree: what this
        # asserts is that PHASE 4F-E1 froze and projected nothing, which a
        # later release phase creating these paths cannot falsify.
        revision = candidate_revision()
        if revision is None:
            listing = git("ls-files", "--", "content").stdout.splitlines()
            listing += [path for path in
                        git("ls-files", "--others", "--exclude-standard",
                            "--", "content").stdout.splitlines()]
        else:
            listing = git("ls-tree", "-r", "--name-only", revision,
                          "--", "content").stdout.splitlines()
        self.assertEqual([], listing)
        blob = candidate_blob(CORPUS_PATH)
        for token in ("releaseAuthorization", "frozen", "releaseAuthorized",
                      "patternDataRevision", "runtimeProjection"):
            with self.subTest(token=token):
                self.assertNotIn(token, blob)
        self.assertEqual({"artifactStatus", "formatVersion", "lemmas"},
                         set(self.corpus))
        self.assertEqual(self.baseline["artifactStatus"],
                         self.corpus["artifactStatus"])
        self.assertEqual(self.baseline["formatVersion"],
                         self.corpus["formatVersion"])

    def test_no_row_became_activity_eligible_or_audio_eligible(self):
        self.assertEqual(
            0, sum(len(pattern["activityEligibility"]) for _, _, pattern
                   in iter_patterns(self.corpus)))
        self.assertEqual(
            0, sum(1 for _, _, pattern in iter_patterns(self.corpus)
                   for example in pattern.get("examples", [])
                   if example["audioEligible"]))


# ---------------------------------------------------------------------------
# §5  the reference tier is intact
# ---------------------------------------------------------------------------

class ReferenceHistoryTests(E1Case):

    def test_all_forty_seven_reference_acceptances_remain(self):
        events = [event for _, _, pattern in iter_patterns(self.corpus)
                  for event in reference_events(pattern)]
        self.assertEqual(REFERENCE_ACCEPT_COUNT, len(events))
        self.assertEqual({"accept"}, {event["decision"] for event in events})

    def test_every_reference_event_is_byte_identical_to_the_baseline(self):
        for pattern_id, (_, _, pattern) in self.current.items():
            with self.subTest(pattern_id=pattern_id):
                _, _, before = self.before[pattern_id]
                self.assertEqual(before["reviewEvents"],
                                 reference_events(pattern))

    def test_the_two_superseded_mowic_events_remain_historical(self):
        """Stale by digest, preserved in history, still not the active basis."""
        stale = []
        for pattern_id, (lemma, meaning, pattern) in self.current.items():
            current_digest = T.review_scope_digest(
                TIER_ONE, lemma, meaning, pattern)
            for index, event in enumerate(reference_events(pattern)):
                if event["scopeDigest"] != current_digest:
                    stale.append((pattern_id, index))
        self.assertEqual(2, len(stale))
        for pattern_id, index in stale:
            with self.subTest(pattern_id=pattern_id):
                self.assertIn("mowic", pattern_id)
                events = reference_events(self.current[pattern_id][2])
                # A later, current-digest acceptance stands after it.
                self.assertLess(index, len(events) - 1)
                lemma, meaning, pattern = self.current[pattern_id]
                self.assertEqual(
                    T.review_scope_digest(TIER_ONE, lemma, meaning, pattern),
                    events[-1]["scopeDigest"])

    def test_no_tier_one_digest_moved(self):
        for pattern_id, (lemma, meaning, pattern) in self.current.items():
            base_lemma, base_meaning, base_pattern = self.before[pattern_id]
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(
                    T.review_scope_digest(
                        TIER_ONE, base_lemma, base_meaning, base_pattern),
                    T.review_scope_digest(
                        TIER_ONE, lemma, meaning, pattern))

    def test_no_fresh_reference_verification_event_was_created(self):
        before = sum(len(pattern["reviewEvents"]) for _, _, pattern
                     in iter_patterns(self.baseline))
        after = sum(len(reference_events(pattern)) for _, _, pattern
                    in iter_patterns(self.corpus))
        self.assertEqual(before, after)


# ---------------------------------------------------------------------------
# §6  content did not move
# ---------------------------------------------------------------------------

class ContentImmutabilityTests(E1Case):

    def test_only_review_state_and_review_events_differ_anywhere(self):
        governance = {"reviewState", "reviewEvents"}
        for pattern_id, (lemma, meaning, pattern) in self.current.items():
            base_lemma, base_meaning, base_pattern = self.before[pattern_id]
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(
                    {k: v for k, v in base_pattern.items()
                     if k not in governance},
                    {k: v for k, v in pattern.items() if k not in governance})
                self.assertEqual(
                    {k: v for k, v in base_lemma.items() if k != "meanings"},
                    {k: v for k, v in lemma.items() if k != "meanings"})
                self.assertEqual(
                    {k: v for k, v in base_meaning.items()
                     if k != "patterns"},
                    {k: v for k, v in meaning.items() if k != "patterns"})

    def test_the_document_shape_is_unchanged(self):
        self.assertEqual(len(self.baseline["lemmas"]),
                         len(self.corpus["lemmas"]))
        self.assertEqual(
            [pattern["id"] for _, _, pattern in iter_patterns(self.baseline)],
            [pattern["id"] for _, _, pattern in iter_patterns(self.corpus)])

    def test_the_twenty_nine_examples_are_byte_identical(self):
        before = [example for _, _, pattern in iter_patterns(self.baseline)
                  for example in pattern.get("examples", [])]
        after = [example for _, _, pattern in iter_patterns(self.corpus)
                 for example in pattern.get("examples", [])]
        self.assertEqual(EXAMPLE_COUNT, len(after))
        self.assertEqual(before, after)

    def test_example_provenance_is_untouched(self):
        origins = [example["origin"] for _, _, pattern
                   in iter_patterns(self.corpus)
                   for example in pattern.get("examples", [])]
        self.assertEqual(
            [example["origin"] for _, _, pattern in iter_patterns(self.baseline)
             for example in pattern.get("examples", [])],
            origins)
        self.assertEqual({"repository-reuse", "editorial-generated"},
                         {origin["kind"] for origin in origins})
        for origin in origins:
            if origin["kind"] == "editorial-generated":
                self.assertEqual(GENERATION_ACTOR, origin["generatorRef"])
            self.assertNotIn("authorRef", origin)

    def test_the_three_d31_corrections_stand_exactly(self):
        for pattern_id, fields in D31_FINAL_WORDING.items():
            _, _, pattern = self.current[pattern_id]
            for path, (prior, final) in fields.items():
                with self.subTest(pattern_id=pattern_id, field=path):
                    self.assertEqual(final, resolve(pattern, path))
                    self.assertNotEqual(prior, resolve(pattern, path))

    def test_the_overturned_row_is_byte_identical_outside_governance(self):
        governance = {"reviewState", "reviewEvents"}
        _, _, pattern = self.current[OVERTURNED_PATTERN]
        _, _, before = self.before[OVERTURNED_PATTERN]
        self.assertEqual(
            {k: v for k, v in before.items() if k not in governance},
            {k: v for k, v in pattern.items() if k not in governance})
        self.assertEqual("I thank my sister for dinner.",
                         pattern["examples"][0]["en"])

    def test_the_superseded_wording_never_reappeared(self):
        blob = candidate_blob(CORPUS_PATH)
        for fields in D31_FINAL_WORDING.values():
            for prior, final in fields.values():
                with self.subTest(prior=prior):
                    self.assertNotIn(prior, blob)
                    self.assertIn(final, blob)


# ---------------------------------------------------------------------------
# §7  the surface outside the two governed documents
# ---------------------------------------------------------------------------

class UntouchedSurfaceTests(E1Case):

    def test_the_tooling_is_byte_identical(self):
        """No tooling change was needed, so none was made."""
        self.assertEqual(baseline_blob("priority7_tooling.py"),
                         candidate_blob("priority7_tooling.py"))

    def test_every_forbidden_file_is_baseline_identical(self):
        for relative in UNCHANGED_FILES:
            with self.subTest(path=relative):
                self.assertEqual(baseline_blob(relative),
                                 candidate_blob(relative))

    def test_the_phase_owned_transition_is_exactly_its_declared_paths(self):
        self.assertEqual(E1_CANDIDATE_PATHS, candidate_footprint())
        self.assertEqual(20, len(E1_CANDIDATE_PATHS))
        self.assertEqual(set(), E1_CANDIDATE_PATHS & set(UNCHANGED_FILES))

    def test_the_committed_candidate_is_the_baselines_direct_child(self):
        revision = candidate_revision()
        if revision is None:
            self.assertEqual(
                BASELINE_COMMIT, git("rev-parse", "HEAD").stdout.strip())
            self.assertNotEqual(set(), candidate_footprint())
        else:
            parent = git("rev-parse", f"{revision}^")
            self.assertEqual(0, parent.returncode, parent.stderr)
            self.assertEqual(BASELINE_COMMIT, parent.stdout.strip())

    def test_the_context_changed_only_in_permitted_registry_fields(self):
        base = self.baseline_context_document
        for key in base:
            if key in {"contextNotice", "editorialActorRegistry"}:
                continue
            with self.subTest(key=key):
                self.assertEqual(base[key], self.context[key])
        self.assertEqual(set(base), set(self.context))
        # The notice is appended to, never rewritten.
        self.assertTrue(
            self.context["contextNotice"].startswith(base["contextNotice"]))

    def test_removing_the_two_inserted_blocks_restores_the_context_bytes(self):
        self.assertEqual(
            baseline_blob(CONTEXT_PATH),
            E1.without_phase_4fe1_context_text(candidate_blob(CONTEXT_PATH)))

    def test_removing_the_forty_five_events_restores_the_corpus_bytes(self):
        self.assertEqual(
            baseline_blob(CORPUS_PATH),
            E1.without_phase_4fe1_corpus_text(candidate_blob(CORPUS_PATH)))

    def test_no_file_carries_a_crlf_or_trailing_whitespace_defect(self):
        """CRLF or trailing blanks here would trip `git diff --check`."""
        for relative in sorted(E1_CANDIDATE_PATHS):
            with self.subTest(path=relative):
                text = candidate_blob(relative)
                self.assertNotIn("\r", text)
                for number, line in enumerate(text.splitlines(), start=1):
                    self.assertEqual(line.rstrip(), line,
                                     f"{relative}:{number}")


# ---------------------------------------------------------------------------
# §8  negative controls — the boundary has teeth
# ---------------------------------------------------------------------------

class NegativeControlTests(E1Case):
    """Each mutation must be refused, or must survive normalisation.

    Two rejection mechanisms are exercised.  ``assert_invalid`` proves the
    validator refuses the shape outright.  ``assert_survives_normalisation``
    proves that a mutation dressed up as this phase's approved work is not
    absorbed by the Phase 4F-E1 normaliser, so every historical guard still
    sees it and still fails.
    """

    def assert_invalid(self, corpus, label, *, context=None):
        issues = validate_editorial(corpus, context or build_context())
        self.assertNotEqual([], issues, f"{label} was accepted")
        return {issue.code for issue in issues}

    def assert_survives_normalisation(self, corpus, label):
        normalised = E1.without_phase_4fe1_editorial_review(corpus)
        self.assertNotEqual(
            self.baseline, normalised,
            f"the normaliser absorbed an unauthorized change: {label}")
        return normalised

    def a_pattern(self, corpus, pattern_id=None):
        pattern_id = pattern_id or next(iter(self.current))
        return patterns_by_id(corpus)[pattern_id][2]

    # -- missing / duplicated events ---------------------------------------

    def test_a_missing_editorial_event_cannot_hold_editorial_reviewed(self):
        corpus = copy.deepcopy(self.corpus)
        pattern = self.a_pattern(corpus)
        pattern["reviewEvents"] = [event for event in pattern["reviewEvents"]
                                   if event["kind"] != "editorial-review"]
        self.assertIn("REVIEW_STATE_MISMATCH",
                      self.assert_invalid(corpus, "missing editorial event"))

    def test_a_duplicate_editorial_acceptance_is_rejected(self):
        corpus = copy.deepcopy(self.corpus)
        pattern = self.a_pattern(corpus)
        pattern["reviewEvents"].append(
            copy.deepcopy(pattern["reviewEvents"][-1]))
        self.assertIn("REVIEW_DUPLICATE_STAGE_ACCEPTANCE",
                      self.assert_invalid(corpus, "duplicate acceptance"))
        self.assert_survives_normalisation(corpus, "duplicate acceptance")

    # -- digests ------------------------------------------------------------

    def test_a_stale_editorial_digest_cannot_reach_editorial_reviewed(self):
        corpus = copy.deepcopy(self.corpus)
        pattern = self.a_pattern(corpus)
        pattern["reviewEvents"][-1]["scopeDigest"] = "sha256:" + "0" * 64
        self.assertIn("REVIEW_STATE_MISMATCH",
                      self.assert_invalid(corpus, "stale digest"))
        self.assert_survives_normalisation(corpus, "stale digest")

    def test_a_tier_one_digest_on_the_editorial_event_is_stale(self):
        corpus = copy.deepcopy(self.corpus)
        pattern_id = next(iter(self.current))
        lemma, meaning, pattern = patterns_by_id(corpus)[pattern_id]
        pattern["reviewEvents"][-1]["scopeDigest"] = T.review_scope_digest(
            TIER_ONE, lemma, meaning, pattern)
        self.assertIn("REVIEW_STATE_MISMATCH",
                      self.assert_invalid(corpus, "tier-1 digest at tier 2"))

    def test_an_editorial_digest_goes_stale_when_learner_wording_changes(self):
        """The binding is real: editing the reviewed text invalidates it."""
        corpus = copy.deepcopy(self.corpus)
        pattern = self.a_pattern(corpus)
        pattern["learnerExplanationEn"] += " Unauthorized addition."
        self.assertIn("REVIEW_STATE_MISMATCH",
                      self.assert_invalid(corpus, "wording change"))
        self.assert_survives_normalisation(corpus, "wording change")

    def test_a_recomputed_digest_cannot_disguise_mutated_wording_as_e1(self):
        """E2 control A: static E1 facts defeat a self-consistent forgery."""
        corpus = copy.deepcopy(self.corpus)
        pattern_id = next(iter(self.current))
        lemma, meaning, pattern = patterns_by_id(corpus)[pattern_id]
        pattern["learnerExplanationEn"] += " Unauthorized repinned addition."
        malicious_digest = T.review_scope_digest(
            "editorial-review", lemma, meaning, pattern)
        editorial_events(pattern)[0]["scopeDigest"] = malicious_digest

        normalised = self.assert_survives_normalisation(
            corpus, "wording mutation plus freshly repinned digest")
        _, _, after = patterns_by_id(normalised)[pattern_id]
        self.assertEqual("editorial-reviewed", after["reviewState"])
        self.assertEqual(1, len(editorial_events(after)))
        self.assertEqual(malicious_digest,
                         editorial_events(after)[0]["scopeDigest"])
        self.assertNotEqual(
            E1.E1_EXPECTED_SCOPE_DIGESTS[pattern_id], malicious_digest)

    def test_an_e1_shaped_event_on_a_forty_sixth_identity_is_never_stripped(self):
        """E2 control B: the literal allowlist has no wildcard or 46th row."""
        corpus = copy.deepcopy(self.corpus)
        lemma = corpus["lemmas"][0]
        meaning = lemma["meanings"][0]
        synthetic = copy.deepcopy(meaning["patterns"][0])
        synthetic["id"] = "vp-p-synthetic-future-pattern-000000000000"
        synthetic["key"] = "synthetic-future-pattern"
        synthetic["reviewEvents"] = [
            event for event in synthetic["reviewEvents"]
            if event["kind"] != "editorial-review"]
        shaped_event = copy.deepcopy(
            editorial_events(meaning["patterns"][0])[0])
        shaped_event["scopeDigest"] = T.review_scope_digest(
            "editorial-review", lemma, meaning, synthetic)
        synthetic["reviewEvents"].append(shaped_event)
        synthetic["reviewState"] = "editorial-reviewed"
        meaning["patterns"].append(synthetic)

        normalised = self.assert_survives_normalisation(
            corpus, "E1-shaped acceptance on a non-E1 identity")
        after = normalised["lemmas"][0]["meanings"][0]["patterns"][-1]
        self.assertEqual(synthetic, after)
        self.assertEqual(1, len(editorial_events(after)))
        self.assertNotIn(synthetic["id"], E1.E1_EXPECTED_PATTERN_IDS)
        self.assertNotEqual([], validate_editorial(corpus, build_context()))

    # -- actor identity and role -------------------------------------------

    def test_an_actor_without_the_editorial_review_role_is_rejected(self):
        document = copy.deepcopy(self.context)
        document["editorialActorRegistry"][EDITORIAL_ACTOR]["roles"] = [
            "example-generation"]
        self.assertIn(
            "EDITORIAL_ACTOR_ROLE",
            self.assert_invalid(self.corpus, "wrong actor role",
                                context=build_context(document)))

    def test_an_actor_holding_an_unknown_role_is_rejected(self):
        document = copy.deepcopy(self.context)
        document["editorialActorRegistry"][EDITORIAL_ACTOR]["roles"] = [
            "editorial-review", "native-linguistic"]
        self.assertIn(
            "EDITORIAL_ACTOR_ROLE_UNKNOWN",
            self.assert_invalid(self.corpus, "borrowed human role",
                                context=build_context(document)))

    def test_the_reference_actor_may_not_perform_the_editorial_review(self):
        corpus = copy.deepcopy(self.corpus)
        for _, _, pattern in iter_patterns(corpus):
            pattern["reviewEvents"][-1]["actorRef"] = REFERENCE_ACTOR
        document = copy.deepcopy(self.context)
        document["editorialActorRegistry"][REFERENCE_ACTOR]["roles"] = [
            "reference-verification", "editorial-review"]
        codes = self.assert_invalid(
            corpus, "reference actor as editorial actor",
            context=build_context(document))
        self.assertIn("REVIEW_ACTOR_INDEPENDENCE", codes)
        self.assert_survives_normalisation(
            corpus, "reference actor as editorial actor")

    def test_the_example_generation_actor_may_not_editorially_review(self):
        corpus = copy.deepcopy(self.corpus)
        for _, _, pattern in iter_patterns(corpus):
            pattern["reviewEvents"][-1]["actorRef"] = GENERATION_ACTOR
        codes = self.assert_invalid(
            corpus, "example generator as editorial actor")
        self.assertIn("EDITORIAL_ACTOR_ROLE", codes)
        self.assert_survives_normalisation(
            corpus, "example generator as editorial actor")

    def test_an_unregistered_actor_is_rejected(self):
        corpus = copy.deepcopy(self.corpus)
        self.a_pattern(corpus)["reviewEvents"][-1]["actorRef"] = (
            "priority7-unregistered-actor")
        self.assertIn("EDITORIAL_ACTOR_REGISTRY_DANGLING",
                      self.assert_invalid(corpus, "unregistered actor"))

    # -- corroboration ------------------------------------------------------

    def test_an_acceptance_without_a_corroborator_is_rejected(self):
        corpus = copy.deepcopy(self.corpus)
        del self.a_pattern(corpus)["reviewEvents"][-1][
            "corroboratingActorRefs"]
        self.assertIn("EDITORIAL_CORROBORATION_REQUIRED",
                      self.assert_invalid(corpus, "no corroborator"))
        self.assert_survives_normalisation(corpus, "no corroborator")

    def test_an_empty_corroborator_list_is_rejected(self):
        corpus = copy.deepcopy(self.corpus)
        self.a_pattern(corpus)["reviewEvents"][-1][
            "corroboratingActorRefs"] = []
        self.assertIn("EDITORIAL_CORROBORATION_REQUIRED",
                      self.assert_invalid(corpus, "empty corroborator list"))

    def test_an_actor_corroborating_itself_is_rejected(self):
        corpus = copy.deepcopy(self.corpus)
        self.a_pattern(corpus)["reviewEvents"][-1][
            "corroboratingActorRefs"] = [EDITORIAL_ACTOR]
        self.assertIn("EDITORIAL_CORROBORATION_SELF",
                      self.assert_invalid(corpus, "self-corroboration"))
        self.assert_survives_normalisation(corpus, "self-corroboration")

    def test_the_reference_actor_may_not_corroborate(self):
        corpus = copy.deepcopy(self.corpus)
        for _, _, pattern in iter_patterns(corpus):
            pattern["reviewEvents"][-1]["corroboratingActorRefs"] = [
                REFERENCE_ACTOR]
        codes = self.assert_invalid(corpus, "reference actor corroborating")
        self.assertIn("REVIEW_ACTOR_INDEPENDENCE", codes)
        self.assertIn("EDITORIAL_ACTOR_ROLE", codes)

    def test_the_example_generation_actor_may_not_corroborate(self):
        corpus = copy.deepcopy(self.corpus)
        self.a_pattern(corpus)["reviewEvents"][-1][
            "corroboratingActorRefs"] = [GENERATION_ACTOR]
        self.assertIn("EDITORIAL_ACTOR_ROLE",
                      self.assert_invalid(corpus, "generator corroborating"))

    # -- human identities ---------------------------------------------------

    def test_an_invented_human_editorial_actor_is_rejected(self):
        document = copy.deepcopy(self.context)
        document["editorialActorRegistry"][EDITORIAL_ACTOR]["human"] = True
        self.assertIn(
            "EDITORIAL_ACTOR_NOT_NONHUMAN",
            self.assert_invalid(self.corpus, "human editorial actor",
                                context=build_context(document)))

    def test_naming_a_human_reviewer_on_the_editorial_event_is_rejected(self):
        corpus = copy.deepcopy(self.corpus)
        event = self.a_pattern(corpus)["reviewEvents"][-1]
        event["reviewerRef"] = HUMAN_REVIEWER
        self.assertIn("SCHEMA_UNKNOWN_FIELD",
                      self.assert_invalid(corpus, "human reviewerRef"))
        self.assert_survives_normalisation(corpus, "human reviewerRef")

    def test_an_identity_key_may_not_be_both_actor_and_reviewer(self):
        document = copy.deepcopy(self.context)
        document["reviewerRegistry"][EDITORIAL_ACTOR] = {
            "human": True, "roles": ["native-linguistic"]}
        self.assertIn(
            "REGISTRY_KEY_COLLISION",
            self.assert_invalid(self.corpus, "actor/reviewer key collision",
                                context=build_context(document)))

    # -- content, provenance and reference events ---------------------------

    def test_an_unauthorized_canonical_wording_change_survives(self):
        corpus = copy.deepcopy(self.corpus)
        self.a_pattern(
            corpus, OVERTURNED_PATTERN)["examples"][0]["en"] = (
                "I say thank you to my sister for dinner.")
        self.assert_survives_normalisation(corpus, "fourth wording change")

    def test_an_example_provenance_mutation_survives(self):
        corpus = copy.deepcopy(self.corpus)
        for _, _, pattern in iter_patterns(corpus):
            for example in pattern.get("examples", []):
                if example["origin"]["kind"] == "editorial-generated":
                    example["origin"]["generatorRef"] = EDITORIAL_ACTOR
                    break
            else:
                continue
            break
        self.assert_survives_normalisation(corpus, "provenance mutation")
        self.assertNotEqual([], validate_editorial(corpus, build_context()))

    def test_a_reference_event_mutation_survives_and_is_rejected(self):
        """Editing the tier-1 acceptance collapses everything built on it."""
        corpus = copy.deepcopy(self.corpus)
        pattern = self.a_pattern(corpus)
        reference_events(pattern)[-1]["scopeDigest"] = "sha256:" + "1" * 64
        self.assert_survives_normalisation(corpus, "reference digest mutation")
        self.assertIn("REVIEW_STATE_MISMATCH",
                      self.assert_invalid(corpus, "reference digest mutation"))

    def test_a_reference_event_reordering_is_rejected(self):
        corpus = copy.deepcopy(self.corpus)
        pattern = self.a_pattern(corpus)
        reference_events(pattern)[0]["reviewedAt"] = "2026-08-18"
        self.assert_survives_normalisation(corpus, "reference date mutation")
        self.assertIn("REVIEW_EVENT_ORDER",
                      self.assert_invalid(corpus, "reference date mutation"))

    def test_an_altered_resolved_finding_is_not_normalised(self):
        corpus = copy.deepcopy(self.corpus)
        pattern_id = next(iter(E1.E1_SPECIAL_ROWS))
        pattern = self.a_pattern(corpus, pattern_id)
        editorial_events(pattern)[0]["findings"][0]["resolutionNote"] += (
            " Unauthorized alteration.")
        normalised = self.assert_survives_normalisation(
            corpus, "altered resolved finding")
        _, _, after = patterns_by_id(normalised)[pattern_id]
        self.assertEqual("editorial-reviewed", after["reviewState"])
        self.assertEqual(1, len(editorial_events(after)))

    def test_deleting_a_reference_event_breaks_the_chain(self):
        corpus = copy.deepcopy(self.corpus)
        pattern = self.a_pattern(corpus)
        pattern["reviewEvents"] = [event for event in pattern["reviewEvents"]
                                   if event["kind"] != "reference-verification"]
        codes = self.assert_invalid(corpus, "deleted reference event")
        self.assertIn("REVIEW_STAGE_ORDER", codes)

    # -- premature release actions ------------------------------------------

    def test_a_premature_product_approval_is_rejected(self):
        corpus = copy.deepcopy(self.corpus)
        lemma, meaning, pattern = patterns_by_id(
            corpus)[next(iter(self.current))]
        pattern["reviewEvents"].append({
            "kind": "product-approval",
            "decision": "accept",
            "scopeVersion": T.SCOPE_VERSION,
            "scopeDigest": T.review_scope_digest(
                "product-approval", lemma, meaning, pattern),
            "reviewerRef": HUMAN_REVIEWER,
            "reviewedAt": REVIEWED_AT,
        })
        pattern["reviewState"] = "approved"
        codes = self.assert_invalid(corpus, "premature product approval")
        self.assertIn("REVIEWER_ROLE", codes)
        self.assert_survives_normalisation(corpus, "premature product approval")

    def test_a_premature_approved_state_without_an_event_is_rejected(self):
        corpus = copy.deepcopy(self.corpus)
        pattern_id = next(iter(self.current))
        self.a_pattern(corpus, pattern_id)["reviewState"] = "approved"
        self.assertIn("REVIEW_STATE_MISMATCH",
                      self.assert_invalid(corpus, "premature approved state"))
        normalised = self.assert_survives_normalisation(
            corpus, "premature approved state")
        _, _, after = patterns_by_id(normalised)[pattern_id]
        self.assertEqual("approved", after["reviewState"])
        self.assertEqual(1, len(editorial_events(after)))

    def test_activity_eligibility_still_requires_approved(self):
        corpus = copy.deepcopy(self.corpus)
        self.a_pattern(corpus)["activityEligibility"] = ["reference"]
        self.assertNotEqual(
            [], validate_editorial(corpus, build_context()),
            "eligibility on an editorial-reviewed row was accepted")

    def test_a_runtime_projection_of_this_corpus_still_emits_nothing(self):
        """No row is approved, so the release projector has nothing to emit."""
        with self.assertRaises(Exception):
            T.freeze_editorial(self.corpus, build_context())


# ---------------------------------------------------------------------------
# §9  the reported artifacts say exactly this
# ---------------------------------------------------------------------------

class ArtifactTests(E1Case):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rows = list(csv.DictReader(
            candidate_blob(MATRIX_PATH).splitlines()))

    def test_the_matrix_has_one_row_per_pattern(self):
        self.assertEqual(PATTERN_COUNT, len(self.rows))
        self.assertEqual(PATTERN_COUNT,
                         len({row["patternId"] for row in self.rows}))
        self.assertEqual(PATTERN_COUNT,
                         len({row["reviewId"] for row in self.rows}))
        self.assertEqual(set(self.current),
                         {row["patternId"] for row in self.rows})

    def test_the_matrix_carries_the_required_columns(self):
        required = {"reviewId", "patternId", "priorReviewState",
                    "finalReviewState", "editorialScopeDigest",
                    "editorialActorRef", "corroboratorRef", "decision",
                    "sourceReviewBasis", "productApprovalCreated"}
        self.assertLessEqual(required, set(self.rows[0]))

    def test_every_matrix_row_states_the_truth(self):
        for row in self.rows:
            with self.subTest(review_id=row["reviewId"]):
                _, _, pattern = self.current[row["patternId"]]
                event = editorial_events(pattern)[0]
                self.assertEqual("reference-verified", row["priorReviewState"])
                self.assertEqual("editorial-reviewed", row["finalReviewState"])
                self.assertEqual(event["scopeDigest"],
                                 row["editorialScopeDigest"])
                self.assertEqual(EDITORIAL_ACTOR, row["editorialActorRef"])
                self.assertEqual(CORROBORATING_ACTOR, row["corroboratorRef"])
                self.assertEqual("ACCEPT", row["decision"])
                self.assertEqual("no", row["productApprovalCreated"])
                self.assertTrue(row["sourceReviewBasis"].strip())

    def test_all_forty_five_decisions_are_accept(self):
        self.assertEqual({"ACCEPT"}, {row["decision"] for row in self.rows})

    def test_the_matrix_claims_no_human_review(self):
        blob = candidate_blob(MATRIX_PATH)
        for token in ("native speaker", "native-reviewer", "AB",
                      "human review", "professional linguist"):
            with self.subTest(token=token):
                self.assertNotIn(token, blob)
        self.assertEqual({"false"},
                         {row["editorialActorHuman"] for row in self.rows} |
                         {row["corroboratorHuman"] for row in self.rows})

    def test_the_summary_states_the_counts_and_the_disclaimers(self):
        text = candidate_blob(SUMMARY_PATH)
        for claim in ("45", "47", "29", BASELINE_COMMIT, BASELINE_TREE,
                      EDITORIAL_ACTOR, CORROBORATING_ACTOR,
                      "solo-maintainer-reference-backed"):
            with self.subTest(claim=claim):
                self.assertIn(claim, text)
        lowered = " ".join(text.lower().replace("*", "").split())
        for disclaimer in ("it does not mean native-speaker review",
                           "no product approval",
                           "the tooling was not changed"):
            with self.subTest(disclaimer=disclaimer):
                self.assertIn(disclaimer, lowered)

    def test_the_historical_review_artifacts_were_not_rewritten(self):
        for relative in ("reports/priority-7-phase-4fd1-final-editorial-matrix.csv",
                         "reports/priority-7-phase-4fd2-blind-final-editorial-matrix.csv",
                         "reports/priority-7-phase-4fd3-adjudication.csv"):
            with self.subTest(path=relative):
                self.assertEqual(baseline_blob(relative),
                                 candidate_blob(relative))


# ---------------------------------------------------------------------------
# §10  the normaliser itself is exact
# ---------------------------------------------------------------------------

class NormaliserTests(E1Case):

    def test_the_static_allowlist_and_digest_map_pin_exactly_the_candidate(self):
        self.assertEqual(PATTERN_COUNT, len(E1.E1_EXPECTED_PATTERN_IDS))
        self.assertEqual(E1.E1_EXPECTED_PATTERN_IDS,
                         frozenset(E1.E1_EXPECTED_SCOPE_DIGESTS))
        self.assertEqual(frozenset(self.current), E1.E1_EXPECTED_PATTERN_IDS)
        for pattern_id, (_, _, pattern) in self.current.items():
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(
                    editorial_events(pattern)[0]["scopeDigest"],
                    E1.E1_EXPECTED_SCOPE_DIGESTS[pattern_id])

    def test_the_normaliser_reproduces_the_baseline_corpus_exactly(self):
        self.assertEqual(
            self.baseline,
            E1.without_phase_4fe1_editorial_review(self.corpus))

    def test_the_normaliser_reproduces_the_baseline_context_exactly(self):
        self.assertEqual(
            self.baseline_context_document,
            E1.without_phase_4fe1_actors(self.context))

    def test_the_normaliser_is_idempotent_on_the_baseline(self):
        self.assertEqual(
            self.baseline,
            E1.without_phase_4fe1_editorial_review(self.baseline))
        self.assertEqual(
            self.baseline_context_document,
            E1.without_phase_4fe1_actors(self.baseline_context_document))

    def test_an_edited_actor_record_survives_the_context_normaliser(self):
        document = copy.deepcopy(self.context)
        document["editorialActorRegistry"][EDITORIAL_ACTOR]["roles"].append(
            "reference-verification")
        self.assertIn(
            EDITORIAL_ACTOR,
            E1.without_phase_4fe1_actors(document)["editorialActorRegistry"])

    def test_an_edited_notice_survives_the_context_normaliser(self):
        document = copy.deepcopy(self.context)
        document["contextNotice"] += " An unauthorized further sentence."
        self.assertNotEqual(
            self.baseline_context_document["contextNotice"],
            E1.without_phase_4fe1_actors(document)["contextNotice"])

    def test_the_text_normaliser_refuses_a_non_canonical_corpus_form(self):
        with self.assertRaises(AssertionError):
            E1.without_phase_4fe1_corpus_text(
                json.dumps(self.corpus, indent=4, ensure_ascii=False) + "\n")

    def test_every_repaired_historical_suite_still_passes(self):
        """The repairs are proved by running them, not by asserting a list.

        They run against a materialised checkout of the phase-owned
        candidate, never against the live tree.  A later phase may add files,
        add events and move review state; whether it also keeps these suites
        current is that phase's own closure obligation, and cannot make this
        historical claim about Phase 4F-E1 fail.
        """
        suites = sorted(
            "tests." + Path(relative).stem
            for relative in E1_HISTORICAL_TEST_REPAIRS)
        revision = candidate_revision()
        with tempfile.TemporaryDirectory(prefix="priority7-4fe1-tree-") as tmp:
            if revision is None:
                # Uncommitted: the working tree is the candidate.
                tree = ROOT
            else:
                # A real clone, not an export: several of these suites read
                # their own git history.  The local clone is hardlinked and
                # its remote is removed, so it is cheap and self-contained.
                tree = Path(tmp) / "candidate"
                clone = subprocess.run(
                    ["git", "clone", "-q", "--no-checkout", str(ROOT),
                     str(tree)], capture_output=True, text=True, check=False)
                self.assertEqual(0, clone.returncode, clone.stderr)
                for arguments in (["remote", "remove", "origin"],
                                  ["checkout", "-q", "--detach", revision]):
                    step = subprocess.run(
                        ["git", "-C", str(tree), *arguments],
                        capture_output=True, text=True, check=False)
                    self.assertEqual(0, step.returncode, step.stderr)
            environment = dict(os.environ)
            environment["PYTHONPATH"] = (
                f"{tree}{_e1_os_path.pathsep}{tree / 'tests'}")
            result = subprocess.run(
                ["python3", "-m", "unittest", "-q", *suites],
                cwd=tree, capture_output=True, text=True, env=environment)
            self.assertEqual(0, result.returncode,
                             (result.stdout + result.stderr)[-4000:])


if __name__ == "__main__":
    unittest.main()
