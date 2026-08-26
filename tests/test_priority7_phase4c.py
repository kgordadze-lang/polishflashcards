"""Priority 7 Phase 4C — applying human review to canonical editorial data.

Phase 4C is the first phase permitted to modify canonical Priority 7 editorial
data.  What it was actually permitted to apply is narrow, and these tests pin
both halves of that: the one legitimate change, and every transition that the
locked governance contract refuses.

The human review itself is real.  Reviewer ``native-reviewer-001`` (initials
``AB``, a native Polish speaker) accepted all 45 Phase 4A rows as presented on
2026-08-13 with zero corrections, flags, rejections, unresolved items and
comments.  Phase 4B validated that evidence into an external ledger whose
SHA-256 is pinned below.

Two governance dependencies block the consequences that a green native review
would otherwise unlock, and both are proven mechanically here rather than
asserted:

1.  ``reviewState`` cannot advance to ``native-reviewed``.  The state machine in
    ``priority7_tooling._review_history_state`` refuses a ``native-linguistic``
    acceptance that is not preceded by an ``external-verification`` acceptance.
    No human external verifier exists; Phase 2B source work was AI-performed and
    the specification states that AI agreement is never a review event.  A
    ``native-linguistic`` event therefore cannot even be appended, let alone
    advance the state.

2.  The five accepted replacement sentences cannot enter the corpus.  They are
    not repository text, so ``repository-reuse`` provenance breaks; and
    ``origin.kind = "original"`` requires an ``authorRef`` resolving to a
    registered human author.  Acceptance is not authorship, so no such author
    exists and none was invented.

The tests below therefore pin the truthful lower state and the outstanding
blockers, exactly as Phase 4C's brief requires when a stage cannot legitimately
be reached.
"""

import collections
import copy
import csv
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent


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
    root = pathlib.Path(root)
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
    return (pathlib.Path(root) / path).read_text(encoding="utf-8")
sys.path.insert(0, str(ROOT))

import priority7_tooling as T  # noqa: E402

# Phase 4F-E1 normalisation.  Imported by path, with no dependency on any
# other import in this module, so it resolves identically under
# `python3 -m unittest`, a direct script run, and the importlib loading
# the later closure suites use.
import os.path as _e1_os_path
import sys as _e1_sys

_E1_DIR = _e1_os_path.dirname(_e1_os_path.abspath(__file__))
if _E1_DIR not in _e1_sys.path:
    _e1_sys.path.insert(0, _E1_DIR)

import priority7_phase4fe1_normalizer as E1  # noqa: E402
import priority7_phase4ff2_normalizer as F2  # noqa: E402
import priority7_phase4fh2_normalizer as H2  # noqa: E402
import priority7_phase4fh21_normalizer as H21  # noqa: E402

CORPUS = ROOT / "editorial" / "verb-pattern-candidates.json"
CONTEXT_FILE = ROOT / "editorial" / "priority-7-authoring-context.json"
PHASE_4B_REPORT = ROOT / "reports" / "priority-7-phase-4b-summary.md"
PUBLIC_RUNTIME = ROOT / "content" / "verb-patterns.json"

REVIEWER_ID = "native-reviewer-001"
REVIEW_DATE = "2026-08-13"

# SHA-256 of the external Phase 4B validated ledger, which is deliberately held
# outside Git in /Users/Kaj/Downloads/Priority_7_Phase_4B_Human_Attestation.
VALIDATED_LEDGER_SHA256 = (
    "7196ef6a6bc41042ebb1b2c3f4d365c66a8e680a89052ff62437301ffe9fb209")

# The corpus digest recorded by Phase 4B.  Phase 4C applied no canonical corpus
# change, so this must still hold.
CORPUS_SHA256_AT_PHASE_4B = (
    "b6fb8139ed99368a2a1527db6dd79d32f06df3e2e069cf59ae559a798176435f")

# The exact sentences the reviewer accepted as presented.  They are recorded
# here as human-accepted-but-pending, NOT as canonical corpus content.
ACCEPTED_REPLACEMENTS = {
    "P7-NR-011": "Dziękuję siostrze za kolację.",
    "P7-NR-012": "Płacę za kawę i gazetę.",
    "P7-NR-033": "Czy widzisz tę górę na horyzoncie?",
    "P7-NR-042": "Kiedy siostra jest w pracy, zajmuję się jej córką.",
    "P7-NR-044": "Nasze plany zależą od pogody.",
}

MAPPING_ROW_RE = re.compile(
    r"^\| (P7-NR-\d{3}) \| (\w+) \| ([a-z-]+) \| `([^`]+)` \| `([^`]+)` \| "
    r"`([^`]+)` \| (.+?) \| (.+?) \|$", re.M)

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


def load_corpus():
    return json.loads(CORPUS.read_text(encoding="utf-8"))


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


def load_context_document():
    return json.loads(CONTEXT_FILE.read_text(encoding="utf-8"))


def build_context(reviewers=None, authors=None, actors=None):
    raw = load_context_document()
    return T.ValidationContext(
        source_registry=raw["sourceRegistry"],
        reviewer_registry=(raw["reviewerRegistry"] if reviewers is None
                           else reviewers),
        author_registry=raw["authorRegistry"] if authors is None else authors,
        allocation_registry=raw["allocationRegistry"],
        repository_index=T.repository_index_from_root(ROOT),
        # Phase 4F-A registered the nonhuman reference-analysis actor, so the
        # real context this suite validates against now has a fifth registry.
        # AB's limits are unaffected: the actor registry cannot name a human.
        editorial_actor_registry=(raw.get("editorialActorRegistry", {})
                                  if actors is None else actors),
    )


def iter_patterns(corpus):
    for lemma in corpus["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                yield lemma, meaning, pattern


def find_pattern(corpus, pattern_id):
    for lemma, meaning, pattern in iter_patterns(corpus):
        if pattern["id"] == pattern_id:
            return lemma, meaning, pattern
    raise KeyError(pattern_id)


EXPECTED_ROW_COUNT = 45


class DuplicateReviewIdError(ValueError):
    """The mapping source repeats a Review ID.

    Keying rows by Review ID before checking uniqueness would let a duplicated
    row silently overwrite an earlier one, and every downstream count would
    still look correct.  This is raised during parsing so no caller can reach a
    mapping that has already lost a row.
    """


def parse_mapping_rows(text):
    """Parse the mapping table into an ordered list, preserving duplicates."""
    return [
        {
            "reviewId": review_id,
            "group": group,
            "decision": decision,
            "lemmaId": lemma_id,
            "meaningId": meaning_id,
            "patternId": pattern_id,
            "exampleId": (example_cell.strip("`")
                          if example_cell.strip() != "—" else None),
            "draftRef": (draft_cell.strip("`")
                         if draft_cell.strip() != "—" else None),
        }
        for (review_id, group, decision, lemma_id, meaning_id, pattern_id,
             example_cell, draft_cell) in MAPPING_ROW_RE.findall(text)
    ]


def build_mapping(text, *, expected_row_count=None):
    """Reject duplicate Review IDs BEFORE keying the mapping by Review ID.

    Uniqueness is checked against the ordered parse, so a repeated Review ID
    fails loudly instead of overwriting the row that came before it.  The
    optional row-count guard is applied *after* the duplicate check, so a
    duplicate is always reported as a duplicate rather than as a count
    mismatch.
    """
    raw_rows = parse_mapping_rows(text)
    review_ids = [row["reviewId"] for row in raw_rows]
    duplicates = sorted({review_id for review_id in review_ids
                         if review_ids.count(review_id) > 1})
    if duplicates:
        raise DuplicateReviewIdError(
            f"duplicate Review ID(s) in the mapping source: {duplicates}")
    if expected_row_count is not None and len(raw_rows) != expected_row_count:
        raise ValueError(
            f"expected {expected_row_count} mapping rows, parsed {len(raw_rows)}")
    mapping = {row["reviewId"]: row for row in raw_rows}
    if len(mapping) != len(raw_rows):  # unreachable; belt and braces
        raise DuplicateReviewIdError("a row was silently overwritten")
    return mapping


def phase4b_mapping():
    """The 45-row mapping, read from the tracked Phase 4B report.

    Reading the tracked report rather than restating the table keeps a single
    in-repository source of truth and additionally proves that the tracked
    mapping still agrees with the real corpus.
    """
    return build_mapping(PHASE_4B_REPORT.read_text(encoding="utf-8"),
                         expected_row_count=EXPECTED_ROW_COUNT)


class LedgerCoverage(unittest.TestCase):
    """All 45 human decisions are accounted for at ID level, not by count."""

    def setUp(self):
        self.mapping = phase4b_mapping()
        self.corpus = load_corpus()

    def test_exactly_the_45_expected_review_ids_are_present(self):
        self.assertEqual(
            {f"P7-NR-{index:03d}" for index in range(1, 46)},
            set(self.mapping),
            "the mapping must cover P7-NR-001..045 with no omission or extra")
        self.assertEqual(45, len(self.mapping), "no duplicate review IDs")

    def test_group_partition_is_12_priority_5_example_28_confirmation(self):
        groups = {}
        for row in self.mapping.values():
            groups[row["group"]] = groups.get(row["group"], 0) + 1
        self.assertEqual({"priority": 12, "example": 5, "confirmation": 28},
                         groups)

    def test_each_group_carries_exactly_the_recorded_human_decision(self):
        expected = {
            "priority": "accepted-as-presented",
            "example": "replacement-accepted-as-presented",
            "confirmation": "looks-good",
        }
        for review_id, row in sorted(self.mapping.items()):
            with self.subTest(review_id=review_id):
                self.assertEqual(expected[row["group"]], row["decision"])

    def test_every_mapped_canonical_id_resolves_in_the_real_corpus(self):
        lemmas, meanings, patterns, examples = {}, {}, {}, {}
        for lemma in self.corpus["lemmas"]:
            lemmas[lemma["id"]] = lemma
            for meaning in lemma["meanings"]:
                meanings[meaning["id"]] = meaning
                for pattern in meaning["patterns"]:
                    patterns[pattern["id"]] = (lemma, meaning, pattern)
                    for example in pattern.get("examples") or []:
                        examples[example["id"]] = example

        for review_id, row in sorted(self.mapping.items()):
            with self.subTest(review_id=review_id):
                self.assertIn(row["lemmaId"], lemmas)
                self.assertIn(row["meaningId"], meanings)
                self.assertIn(row["patternId"], patterns)
                lemma, meaning, _ = patterns[row["patternId"]]
                self.assertEqual(row["lemmaId"], lemma["id"],
                                 "pattern must be owned by the mapped lemma")
                self.assertEqual(row["meaningId"], meaning["id"],
                                 "pattern must be owned by the mapped meaning")
                if row["exampleId"] is not None:
                    self.assertIn(row["exampleId"], examples)

    def test_the_45_review_ids_biject_onto_the_45_real_patterns(self):
        mapped = [row["patternId"] for row in self.mapping.values()]
        real = {
            pattern["id"] for _, _, pattern in
            iter_patterns(priority7_corpus(self.corpus))}
        self.assertEqual(45, len(set(mapped)), "no pattern mapped twice")
        self.assertEqual(real, set(mapped),
                         "every real pattern received exactly one decision")

    def test_no_review_id_leaked_into_canonical_data(self):
        self.assertNotIn("P7-NR-", CORPUS.read_text(encoding="utf-8"))


class DuplicateRowRejection(unittest.TestCase):
    """A duplicated Review ID must fail loudly, not overwrite silently.

    Review found that keying rows by Review ID before checking uniqueness let a
    duplicated row replace the row parsed before it.  Injecting a second
    ``P7-NR-001`` row still produced 45 unique keys, so every coverage test
    kept passing while one real decision had been dropped.  These tests pin the
    repair, and operate on scratch text only - the tracked report and the
    external validated ledger are never modified.
    """

    def setUp(self):
        self.real_text = PHASE_4B_REPORT.read_text(encoding="utf-8")

    def _duplicate_first_row(self):
        """Scratch copy of the report with the P7-NR-001 row repeated."""
        rows = parse_mapping_rows(self.real_text)
        self.assertEqual(EXPECTED_ROW_COUNT, len(rows))
        for line in self.real_text.splitlines():
            if line.startswith("| P7-NR-001 |"):
                return self.real_text.replace(line, line + "\n" + line, 1), line
        self.fail("could not locate the P7-NR-001 mapping row to duplicate")

    def test_the_real_45_row_mapping_still_parses_cleanly(self):
        mapping = build_mapping(self.real_text,
                                expected_row_count=EXPECTED_ROW_COUNT)
        self.assertEqual(EXPECTED_ROW_COUNT, len(mapping))
        self.assertEqual({f"P7-NR-{index:03d}" for index in range(1, 46)},
                         set(mapping))

    def test_a_duplicated_review_id_is_rejected(self):
        mutated, _ = self._duplicate_first_row()
        with self.assertRaises(DuplicateReviewIdError) as caught:
            build_mapping(mutated)
        self.assertIn("P7-NR-001", str(caught.exception))

    def test_duplicate_is_rejected_as_a_duplicate_not_as_a_count_mismatch(self):
        """The duplicate check runs before the row-count guard."""
        mutated, _ = self._duplicate_first_row()
        with self.assertRaises(DuplicateReviewIdError):
            build_mapping(mutated, expected_row_count=EXPECTED_ROW_COUNT)

    def test_the_duplicated_row_would_otherwise_have_been_swallowed(self):
        """Proves the mutation is genuinely invisible to a keyed mapping.

        Without the guard the mutated source still yields 45 unique keys, which
        is exactly why the original coverage tests failed to catch it.
        """
        mutated, _ = self._duplicate_first_row()
        raw_rows = parse_mapping_rows(mutated)
        self.assertEqual(EXPECTED_ROW_COUNT + 1, len(raw_rows))
        naive = {row["reviewId"]: row for row in raw_rows}
        self.assertEqual(EXPECTED_ROW_COUNT, len(naive),
                         "a naive keyed mapping hides the extra row")

    def test_a_short_mapping_is_rejected_by_the_row_count_guard(self):
        rows = self.real_text.splitlines()
        trimmed = "\n".join(
            line for line in rows if not line.startswith("| P7-NR-045 |"))
        with self.assertRaises(ValueError):
            build_mapping(trimmed, expected_row_count=EXPECTED_ROW_COUNT)


class ReviewerRecord(unittest.TestCase):
    """AB is a native reviewer: not an author, verifier or product approver."""

    def setUp(self):
        # Phase 4F-F2 legitimately registered the human product owner.  That
        # approved registration is reverted here so this class's claims about
        # who Phase 4C named, and about what may appear in a reviewer record,
        # still mean what they meant when written.
        self.context = F2.without_phase_4ff2_reviewer(
            H2.without_phase_4fh2_context(
                H21.without_phase_4fh21_context(load_context_document())))
        self.reviewers = self.context["reviewerRegistry"]

    def test_exactly_one_reviewer_is_named_and_it_is_the_real_human(self):
        self.assertEqual({REVIEWER_ID}, set(self.reviewers))
        record = self.reviewers[REVIEWER_ID]
        self.assertIs(True, record["human"])
        self.assertEqual("AB", record["displayName"])
        self.assertEqual("Native Polish speaker", record["background"])
        self.assertIs(True, record["nativePolishSpeaker"])

    def test_reviewer_holds_the_native_role_and_nothing_else(self):
        record = self.reviewers[REVIEWER_ID]
        self.assertEqual(["native-linguistic"], record["roles"])
        for forbidden in ("external-verification", "product-approval",
                          "correction", "reopen"):
            self.assertNotIn(forbidden, record["roles"])

    def test_reviewer_was_not_granted_multi_role_authority(self):
        self.assertNotIn("ownerAllowsMultipleRoles", self.reviewers[REVIEWER_ID])

    def test_no_credential_was_invented_beyond_the_attestation(self):
        """The attestation says only "Native Polish speaker"."""
        blob = json.dumps(self.reviewers, ensure_ascii=False)
        # "native-linguistic" is the legitimate role token; case-fold first,
        # then strip every occurrence so the credential sweep below cannot
        # trivially match the substring "linguist" inside the role name.
        prose = blob.lower().replace("native-linguistic", "")
        for invented in ("teacher", "teaching", "linguist", "professor",
                         "editor", "qualification", "certified"):
            with self.subTest(invented=invented):
                self.assertNotIn(invented, prose.lower())

    def test_no_personal_contact_or_owner_identity_was_recorded(self):
        blob = json.dumps(self.reviewers, ensure_ascii=False)
        for forbidden in ("@", "Kaj", "gordadze", "phone", "address"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, blob)

    def test_external_evidence_is_referenced_by_digest_not_embedded(self):
        record = self.reviewers[REVIEWER_ID]
        self.assertEqual(VALIDATED_LEDGER_SHA256,
                         record["attestationLedgerSha256"])
        blob = CORPUS.read_text(encoding="utf-8") + json.dumps(
            self.context, ensure_ascii=False)
        for artifact in ("review-attestation", "decision-ledger",
                         "phase4b-validated-ledger"):
            self.assertNotIn(artifact, blob)

    def test_no_author_identity_exists_anywhere(self):
        self.assertEqual({}, self.context["authorRegistry"])


class NativeReviewedIsBlocked(unittest.TestCase):
    """The state machine, not an opinion, refuses the advance to native.

    These cases are about the **human-reviewed** chain's ordering rules and
    AB's role limits, so the pattern under test is put back on that chain
    explicitly.  Phase 4F-A moved the real corpus onto
    ``solo-maintainer-reference-backed``, where a native acceptance is
    supplementary and cannot advance anything at all -- a strictly stronger
    refusal, asserted separately below.
    """

    def setUp(self):
        self.corpus = load_corpus()
        self.pattern_id = "vp-p-szukac-seek-genitive-target-71dc6eff512c"

    @staticmethod
    def _on_human_chain(pattern):
        """Restore the pre-Phase-4F-A shape of one pattern, in memory only."""
        pattern["releaseMode"] = T.HUMAN_REVIEWED_MODE
        pattern["reviewState"] = "research"
        pattern["reviewEvents"] = []
        return pattern

    def _with_native_event(self, review_state=None):
        corpus = copy.deepcopy(self.corpus)
        lemma, meaning, pattern = find_pattern(corpus, self.pattern_id)
        self._on_human_chain(pattern)
        pattern["reviewEvents"] = [{
            "kind": "native-linguistic",
            "decision": "accept",
            "scopeVersion": T.SCOPE_VERSION,
            "scopeDigest": T.review_scope_digest(
                "native-linguistic", lemma, meaning, pattern),
            "reviewerRef": REVIEWER_ID,
            "reviewedAt": REVIEW_DATE,
        }]
        if review_state is not None:
            pattern["reviewState"] = review_state
        return corpus

    def test_a_bare_native_acceptance_is_rejected_even_at_research_state(self):
        issues = T.validate_editorial(self._with_native_event(), build_context())
        self.assertIn("REVIEW_STAGE_ORDER", {issue.code for issue in issues},
                      "native acceptance requires a preceding external one")

    def test_claiming_native_reviewed_is_rejected_twice_over(self):
        issues = T.validate_editorial(
            self._with_native_event("native-reviewed"), build_context())
        codes = {issue.code for issue in issues}
        self.assertIn("REVIEW_STAGE_ORDER", codes)
        self.assertIn("REVIEW_STATE_MISMATCH", codes)

    def _ab_performs_both_stages(self, roles):
        """AB is used for external verification AND native review.

        ``roles`` is what the registry grants AB, which is what separates the
        two failure modes the validator distinguishes.
        """
        corpus = copy.deepcopy(self.corpus)
        lemma, meaning, pattern = find_pattern(corpus, self.pattern_id)
        self._on_human_chain(pattern)
        pins = sorted({T.evidence_digest(record)
                       for record in pattern["evidence"]
                       if record["sourceKind"] in {"contemporary-reference",
                                                   "contemporary-corpus"}})
        pattern["reviewEvents"] = [
            {
                "kind": "external-verification",
                "decision": "accept",
                "scopeVersion": T.SCOPE_VERSION,
                "scopeDigest": T.review_scope_digest(
                    "external-verification", lemma, meaning, pattern),
                "supportingEvidenceDigests": pins,
                "reviewerRef": REVIEWER_ID,
                "reviewedAt": REVIEW_DATE,
            },
            {
                "kind": "native-linguistic",
                "decision": "accept",
                "scopeVersion": T.SCOPE_VERSION,
                "scopeDigest": T.review_scope_digest(
                    "native-linguistic", lemma, meaning, pattern),
                "reviewerRef": REVIEWER_ID,
                "reviewedAt": REVIEW_DATE,
            },
        ]
        pattern["reviewState"] = "native-reviewed"
        reviewers = copy.deepcopy(load_context_document()["reviewerRegistry"])
        reviewers[REVIEWER_ID]["roles"] = list(roles)
        return {issue.code for issue in T.validate_editorial(
            corpus, build_context(reviewers=reviewers))}

    def test_native_only_reviewer_used_externally_fails_on_role_and_multi_role(self):
        """Case B: AB keeps the real registry's native-linguistic-only role."""
        codes = self._ab_performs_both_stages(["native-linguistic"])
        self.assertEqual(
            {"REVIEWER_ROLE", "REVIEWER_MULTI_ROLE_NOT_AUTHORIZED"}, codes,
            "AB holds no external-verification role, and spans two stages")

    def test_granting_ab_both_roles_still_fails_on_multi_role_alone(self):
        """Case A: even fabricating the extra role does not open the path.

        Granting the role removes ``REVIEWER_ROLE`` but leaves
        ``REVIEWER_MULTI_ROLE_NOT_AUTHORIZED``, because one human spanning two
        stages needs an explicit owner allowance that does not exist.  The
        distinction matters: the remaining error is the one that cannot be
        cleared by editing a registry field.
        """
        codes = self._ab_performs_both_stages(
            ["native-linguistic", "external-verification"])
        self.assertEqual({"REVIEWER_MULTI_ROLE_NOT_AUTHORIZED"}, codes)
        self.assertNotIn("REVIEWER_ROLE", codes)

    def test_an_ai_identity_can_never_stand_in_as_the_external_verifier(self):
        corpus = self._with_native_event()
        reviewers = dict(load_context_document()["reviewerRegistry"])
        reviewers["ai-adjudicator"] = {
            "human": False, "roles": ["external-verification"]}
        lemma, meaning, pattern = find_pattern(corpus, self.pattern_id)
        pins = sorted({T.evidence_digest(record)
                       for record in pattern["evidence"]
                       if record["sourceKind"] in {"contemporary-reference",
                                                   "contemporary-corpus"}})
        pattern["reviewEvents"].insert(0, {
            "kind": "external-verification",
            "decision": "accept",
            "scopeVersion": T.SCOPE_VERSION,
            "scopeDigest": T.review_scope_digest(
                "external-verification", lemma, meaning, pattern),
            "supportingEvidenceDigests": pins,
            "reviewerRef": "ai-adjudicator",
            "reviewedAt": REVIEW_DATE,
        })
        codes = {issue.code for issue in T.validate_editorial(
            corpus, build_context(reviewers=reviewers))}
        self.assertIn("REVIEWER_NOT_HUMAN", codes)


class ExampleAuthorshipIsBlocked(unittest.TestCase):
    """Native acceptance of a sentence is not authorship of that sentence."""

    def setUp(self):
        # Phase 4C's claim is about the corpus Phase 4C left behind, so the
        # later approved example work is reverted before it is stated.
        self.corpus = without_phase_4fc2_examples(load_corpus())
        self.pattern_id = (
            "vp-p-dziekowac-thank-dative-recipient-za-accusative-057197dd300f")
        self.text = ACCEPTED_REPLACEMENTS["P7-NR-011"]

    def _replaced(self, origin):
        corpus = copy.deepcopy(self.corpus)
        _, _, pattern = find_pattern(corpus, self.pattern_id)
        pattern["examples"][0]["pl"] = self.text
        pattern["examples"][0]["en"] = "I thank my sister for dinner."
        pattern["examples"][0]["origin"] = origin
        return corpus

    def test_replacement_text_breaks_repository_reuse_provenance(self):
        corpus = copy.deepcopy(self.corpus)
        _, _, pattern = find_pattern(corpus, self.pattern_id)
        pattern["examples"][0]["pl"] = self.text
        codes = {issue.code
                 for issue in T.validate_editorial(corpus, build_context())}
        self.assertIn("REPOSITORY_SOURCE_MISMATCH", codes,
                      "the accepted sentence is not the repository sentence")

    def test_original_origin_without_an_author_is_rejected(self):
        codes = {issue.code for issue in T.validate_editorial(
            self._replaced({"kind": "original"}), build_context())}
        self.assertIn("SCHEMA_REQUIRED", codes)

    def test_an_unregistered_author_is_rejected(self):
        codes = {issue.code for issue in T.validate_editorial(
            self._replaced({"kind": "original",
                            "authorRef": "unresolved-author",
                            "authoredAt": REVIEW_DATE}), build_context())}
        self.assertIn("AUTHOR_REGISTRY_DANGLING", codes)

    def test_a_nonhuman_author_is_rejected(self):
        codes = {issue.code for issue in T.validate_editorial(
            self._replaced({"kind": "original",
                            "authorRef": "ai-draft",
                            "authoredAt": REVIEW_DATE}),
            build_context(authors={"ai-draft": {"human": False}}))}
        self.assertIn("AUTHOR_NOT_HUMAN", codes)

    def test_the_reviewer_was_not_recorded_as_the_author(self):
        """AB accepted the sentences; AB did not write them."""
        self.assertEqual({}, load_context_document()["authorRegistry"])
        blob = CORPUS.read_text(encoding="utf-8")
        self.assertNotIn(REVIEWER_ID, blob)
        self.assertNotIn("authorRef", blob)

    def test_none_of_the_five_accepted_sentences_entered_the_corpus(self):
        blob = json.dumps(self.corpus, ensure_ascii=False)
        for review_id, sentence in sorted(ACCEPTED_REPLACEMENTS.items()):
            with self.subTest(review_id=review_id):
                self.assertNotIn(sentence, blob,
                                 "blocked on authorship, not on linguistics")

    def test_the_three_replaceable_slots_keep_their_original_wording(self):
        """Nothing was half-applied: the old sentences are still intact."""
        corpus = self.corpus
        expected = {
            "vp-e-dziekowac-thank-dative-recipient-za-accusative-"
            "thanks-for-cooperation-92656ebcc371":
                "Dziękuję wszystkim za owocną współpracę.",
            "vp-e-placic-pay-za-accusative-goods-"
            "how-much-for-everything-dd5e5c88cfd4":
                "Ile płacę za wszystko?",
            "vp-e-widziec-perceive-visually-accusative-object-"
            "saw-your-sister-ec51af47f224":
                "Widziałam wczoraj twoją siostrę.",
        }
        found = {example["id"]: example["pl"]
                 for _, _, pattern in iter_patterns(corpus)
                 for example in pattern.get("examples") or []}
        for example_id, sentence in sorted(expected.items()):
            with self.subTest(example_id=example_id):
                self.assertEqual(sentence, found[example_id])

    def test_the_two_empty_slots_gained_no_example(self):
        corpus = self.corpus
        for pattern_id in (
                "vp-p-zajmowac-sie-look-after-person-instrumental-object-"
                "6f93facbd939",
                "vp-p-zalezec-depend-on-od-genitive-source-1ad29f7a1318"):
            with self.subTest(pattern_id=pattern_id):
                _, _, pattern = find_pattern(corpus, pattern_id)
                self.assertIsNone(pattern.get("examples"))


class TruthfulLowerStateIsPinned(unittest.TestCase):
    """Since native-reviewed is unreachable, pin what is actually true.

    Phase 4C's answer was ``research`` everywhere.  Phase 4F-A raised 41 rows
    to ``reference-verified`` through the nonhuman solo chain, which claims no
    human external verification and no native review; the four rows the
    contemporary reference does not attest stayed at ``research``.  What this
    class guards is unchanged: the recorded state is never higher than what the
    project can actually justify, and ``native-reviewed`` is still nowhere.
    """

    def setUp(self):
        # Phase 4F-E1 later reached tier 2.  Its approved acceptances are
        # reverted here so this class's historical claims still mean what they
        # meant when written; ``self.live`` keeps the unmodified corpus for the
        # checks that must hold whatever later phases did.
        self.live = load_corpus()
        self.corpus = E1.without_phase_4fe1_editorial_review(
            F2.without_phase_4ff2_product_approval(
                H2.without_phase_4fh2_content_completion(
                    H21.without_phase_4fh21_product_reapproval(self.live))))
        self.patterns = [pattern
                         for _, _, pattern in iter_patterns(self.corpus)]
        self.live_patterns = [pattern
                              for _, _, pattern in iter_patterns(self.live)]

    def test_the_corpus_still_validates(self):
        self.assertEqual([], T.validate_editorial(self.live, build_context()))

    def test_no_row_ever_claims_human_review_or_approval(self):
        """Live and unconditional: the human *linguistic* claims stay refused.

        Phase 4C refused three states because no authority for any of them
        existed.  Phase 4F-F2 legitimately supplied one of the three: the
        product owner registered themselves and approved, so ``approved``,
        ``product-approval`` and ``reviewerRef`` are now on the record and
        are checked over the normalised corpus below.  The two that claim a
        human checked the *Polish* -- ``externally-verified`` and
        ``native-reviewed`` -- have no authority to this day and stay refused
        live, whatever any later phase records.
        """
        for pattern in self.live_patterns:
            with self.subTest(pattern_id=pattern["id"]):
                self.assertNotIn(pattern["reviewState"],
                                 {"externally-verified", "native-reviewed"})
                for event in pattern["reviewEvents"]:
                    self.assertNotIn(
                        event["kind"],
                        {"external-verification", "native-linguistic"})
        for pattern in self.patterns:
            with self.subTest(pattern_id=pattern["id"], source="normalised"):
                self.assertNotEqual("approved", pattern["reviewState"])
                for event in pattern["reviewEvents"]:
                    self.assertNotEqual("product-approval", event["kind"])
                    self.assertNotIn("reviewerRef", event)

    def test_the_45_patterns_hold_the_phase_4fa_states_and_nothing_higher(self):
        patterns = [
            pattern for _, _, pattern in
            iter_patterns(priority7_corpus(self.corpus))]
        self.assertEqual(45, len(patterns))
        states = collections.Counter(
            pattern["reviewState"] for pattern in patterns)
        self.assertEqual({"reference-verified": 45}, dict(states))
        for pattern in patterns:
            with self.subTest(pattern_id=pattern["id"]):
                self.assertNotIn(pattern["reviewState"],
                                 {"externally-verified", "native-reviewed",
                                  "editorial-reviewed", "approved"})

    def test_every_review_event_is_a_nonhuman_reference_verification(self):
        events = [event for pattern in self.patterns
                  for event in pattern["reviewEvents"]]
        self.assertEqual(PHASE_4FA_EVENT_COUNT,
                         sum(len(history) for history in
                             phase_4fa_review_events().values()))
        self.assertEqual(CURRENT_EVENT_COUNT, len(events))
        for event in events:
            with self.subTest(event=event):
                self.assertEqual("reference-verification", event["kind"])
                self.assertEqual("accept", event["decision"])
                self.assertEqual("priority7-reference-analysis",
                                 event["actorRef"])
                self.assertNotIn("reviewerRef", event)

    def test_ab_gained_no_event_and_no_new_authority(self):
        blob = CORPUS.read_text(encoding="utf-8")
        for token in ("native-linguistic", "external-verification",
                      REVIEWER_ID):
            with self.subTest(token=token):
                self.assertNotIn(token, blob)
        record = load_context_document()["reviewerRegistry"][REVIEWER_ID]
        self.assertEqual(["native-linguistic"], record["roles"])
        self.assertNotIn("ownerAllowsMultipleRoles", record)
        self.assertNotIn("acknowledgedReleaseModes", record)

    def test_no_pattern_is_approved_or_release_authorized(self):
        # Both claims are made over the normalised corpus: Phase 4F-F2
        # legitimately introduced the ``product-approval`` token and the
        # ``approved`` state.  What Phase 4C guards live -- zero eligibility,
        # zero audio, no runtime -- is asserted by its own tests below.
        for pattern in self.patterns:
            with self.subTest(pattern_id=pattern["id"]):
                self.assertNotEqual("approved", pattern["reviewState"])
        self.assertNotIn(
            "product-approval",
            F2.without_phase_4ff2_corpus_text(
                H2.without_phase_4fh2_corpus_text(
                    H21.without_phase_4fh21_corpus_text(
                        CORPUS.read_text(encoding="utf-8")))))

    def test_activity_eligibility_remains_empty_everywhere(self):
        self.assertEqual(
            0, sum(len(pattern["activityEligibility"])
                   for pattern in self.patterns))

    def test_no_example_became_audio_eligible(self):
        self.assertEqual(
            0, sum(1 for pattern in self.patterns
                   for example in pattern.get("examples") or []
                   if example["audioEligible"] is not False))

    def test_no_exercise_identity_exists(self):
        blob = CORPUS.read_text(encoding="utf-8")
        self.assertNotIn("exerciseId", blob)
        self.assertNotIn("vp-x-", blob)

    def test_learner_facing_treatment_was_preserved_not_promoted(self):
        """Blanket acceptance did not silently change teaching status."""
        self.assertEqual(
            {"active-production", "recognition-only", "deferred"},
            set(T.TEACHING_STATUSES))
        for pattern in self.patterns:
            with self.subTest(pattern_id=pattern["id"]):
                self.assertIn(pattern["teachingStatus"], T.TEACHING_STATUSES)
                self.assertEqual([], pattern["activityEligibility"])


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


class CanonicalCorpusUnchanged(unittest.TestCase):
    """No linguistic or learner-facing content has ever been changed.

    Phase 4C proved this with a whole-file digest, which held while nothing at
    all had been written.  Phase 4F-A wrote governance fields and edited the
    reference evidence it re-inspected, so the file digest necessarily moved.
    The guarantee is therefore stated where it actually lives: over everything
    except ``releaseMode``, ``reviewState``, ``reviewEvents`` and ``evidence``,
    the corpus is byte-identical to the Phase 4B baseline.
    """

    #: Digest of the lemma/meaning/pattern projection with the four governance
    #: and evidence keys removed.  Computed from the Phase 4B corpus and
    #: unchanged since; it is what "no structure, meaning, teaching status,
    #: explanation, example, content reference or error note changed" means.
    LINGUISTIC_PROJECTION_SHA256 = (
        "sha256:e5f70e0048230724da02618755f6a9a96d3e01b3cf654a397e495026d8d2dbc6")

    GOVERNANCE_AND_EVIDENCE_KEYS = frozenset(
        {"releaseMode", "reviewState", "reviewEvents", "evidence"})

    @classmethod
    def linguistic_projection(cls, corpus):
        rows = []
        for lemma in corpus["lemmas"]:
            bare_lemma = {key: value for key, value in lemma.items()
                          if key != "meanings"}
            for meaning in lemma["meanings"]:
                bare_meaning = {key: value for key, value in meaning.items()
                                if key != "patterns"}
                for pattern in meaning["patterns"]:
                    rows.append({
                        "lemma": bare_lemma,
                        "meaning": bare_meaning,
                        "pattern": {
                            key: value for key, value in pattern.items()
                            if key not in cls.GOVERNANCE_AND_EVIDENCE_KEYS},
                    })
        return rows

    @classmethod
    def normalised(cls, corpus=None):
        """The corpus as Phase 4C left it: later approved work reverted.

        Phase 4F-H2 comes off first, because it is the newest layer and it
        rewrote learner-facing prose and added examples, both of which this
        projection covers.  Its phase-owned normaliser is pinned to that
        exact transition, so an unauthorised edit dressed up as H2 work
        survives here and still moves the digest.
        """
        return without_phase_4fc2_examples(
            without_phase_4fb3b_edits(
                H2.without_phase_4fh2_content_completion(
                    H21.without_phase_4fh21_product_reapproval(
                        load_corpus() if corpus is None else corpus))))

    def test_no_linguistic_or_learner_facing_content_changed(self):
        digest = hashlib.sha256(T.canonicalize_rfc8785(
            self.linguistic_projection(self.normalised()))).hexdigest()
        self.assertEqual(self.LINGUISTIC_PROJECTION_SHA256, f"sha256:{digest}",
                         "no structure, meaning, explanation or example changed")

    def test_the_projection_really_excludes_only_those_four_keys(self):
        """A guard that the digest above cannot be satisfied vacuously."""
        corpus = load_corpus()
        _, _, pattern = find_pattern(
            corpus, "vp-p-szukac-seek-genitive-target-71dc6eff512c")
        pattern["learnerExplanationEn"] = "mutated"
        digest = hashlib.sha256(T.canonicalize_rfc8785(
            self.linguistic_projection(self.normalised(corpus)))).hexdigest()
        self.assertNotEqual(self.LINGUISTIC_PROJECTION_SHA256, f"sha256:{digest}")

    def test_the_phase_4fb3b_normalisation_reverts_only_the_approved_edits(self):
        """The normalisation cannot hide an unapproved change."""
        corpus = load_corpus()
        _, _, pattern = find_pattern(
            corpus, "vp-p-wierzyc-have-trust-w-accusative-target-6561408ea8d1")
        pattern["teachingStatus"] = "deferred"
        digest = hashlib.sha256(T.canonicalize_rfc8785(
            self.linguistic_projection(self.normalised(corpus)))).hexdigest()
        self.assertNotEqual(self.LINGUISTIC_PROJECTION_SHA256, f"sha256:{digest}")

    def test_the_phase_4fc2_normalisation_reverts_only_the_locked_examples(self):
        """A sentence Phase 4F-C1C did not lock survives the revert."""
        corpus = load_corpus()
        _, _, pattern = find_pattern(
            corpus, "vp-p-zalezec-depend-on-od-genitive-source-1ad29f7a1318")
        pattern["examples"][0]["pl"] = "Wszystko zależy od ciebie."
        digest = hashlib.sha256(T.canonicalize_rfc8785(
            self.linguistic_projection(self.normalised(corpus)))).hexdigest()
        self.assertNotEqual(self.LINGUISTIC_PROJECTION_SHA256, f"sha256:{digest}")

    def test_corpus_shape_is_unchanged(self):
        corpus = priority7_corpus(self.normalised())
        meanings = sum(len(lemma["meanings"]) for lemma in corpus["lemmas"])
        patterns = list(iter_patterns(corpus))
        examples = sum(len(pattern.get("examples") or [])
                       for _, _, pattern in patterns)
        self.assertEqual(30, len(corpus["lemmas"]))
        self.assertEqual(34, meanings)
        self.assertEqual(45, len(patterns))
        self.assertEqual(23, examples)

    def test_evidence_changed_only_where_phase_4fa_re_inspected_it(self):
        """122 Phase 2B records plus the one Phase 4F-A added, and no more.

        Every record re-dated to the Phase 4F-A inspection day is a WSJP PAN
        record, because that is the only source the phase could actually
        re-open: the Mędak demo PDF is not re-inspectable and the repository
        records establish what the app teaches, not what Polish requires.
        """
        corpus = priority7_corpus(load_corpus())
        total = 0
        re_inspected = []
        for _, _, pattern in iter_patterns(corpus):
            for record in pattern["evidence"]:
                total += 1
                self.assertRegex(T.evidence_digest(record), r"^sha256:[0-9a-f]{64}$")
                if record["checkedAt"] == "2026-08-14":
                    re_inspected.append(record)
        self.assertEqual(122, total, "the 2B evidence set, unchanged in size")
        self.assertEqual(46, len(re_inspected))
        self.assertEqual({"wsjp-pan"},
                         {record["sourceId"] for record in re_inspected})
        self.assertEqual(
            46, sum(1 for _, _, pattern in iter_patterns(corpus)
                    for record in pattern["evidence"]
                    if record["sourceId"] == "wsjp-pan"),
            "every WSJP record was re-inspected, none was left stale")

    def test_only_the_authoring_context_changed_in_the_editorial_directory(self):
        """The corpus is the canonical data; the context holds registries."""
        self.assertTrue(CORPUS.exists())
        self.assertTrue(CONTEXT_FILE.exists())
        self.assertEqual(
            {"artifactStatus", "formatVersion", "lemmas"},
            set(load_corpus()),
            "no registry or review key was bolted onto the corpus document")


class NoFreezeRuntimeOrShippingChange(unittest.TestCase):
    """Phase 4C is editorial governance only."""

    def test_no_public_runtime_projection_exists(self):
        # Superseded by Priority 7 Phase 4F-I1, the release that materialised
        # the official runtime.  The only document that may occupy that path
        # is exactly the I1 release artifact, pinned by digest and revision,
        # and it may only exist alongside the matching shell and worker.
        self.assertEqual("complete", i1_bundle().state)

    def test_no_freeze_or_release_artifact_exists(self):
        for glob in ("*frozen*.json", "*release*.json", "*tombstone*.json",
                     "*allocation*.json"):
            for found in (ROOT / "editorial").glob(glob):
                self.fail(f"unexpected freeze/release artifact: {found}")

    def test_no_real_allocation_or_pattern_data_revision_was_created(self):
        context = load_context_document()
        self.assertEqual({}, context["allocationRegistry"])
        self.assertNotIn("patternDataRevision", json.dumps(context))
        self.assertNotIn("patternDataRevision",
                         CORPUS.read_text(encoding="utf-8"))

    def test_shipping_markers_are_unchanged(self):
        # Restated over the shell and worker with the pinned Phase 4F-I1
        # release layer removed; every byte I1 did not pin is still compared.
        index = pre_i1("index.html")
        worker = pre_i1("sw.js")
        self.assertIn('APP_VERSION = "8.10"', index)
        self.assertIn("popolsku-v65", worker)
        self.assertNotIn("verb-patterns.json", worker)

    def test_the_editorial_artifact_is_still_marked_nonproduction(self):
        self.assertEqual("priority-7-editorial-nonproduction",
                         load_corpus()["artifactStatus"])
        self.assertEqual("priority-7-private-authoring-context-nonproduction",
                         load_context_document()["contextStatus"])

    def test_private_editorial_keys_never_reach_a_runtime_projection(self):
        for key in ("reviewerRegistry", "authorRegistry", "reviewEvents",
                    "reviewState", "origin", "evidence"):
            self.assertIn(key, T.PRIVATE_RUNTIME_KEYS)


class OutstandingBlockers(unittest.TestCase):
    """The two dependencies that must clear before approval and freeze."""

    def test_no_external_verification_authority_is_named(self):
        reviewers = load_context_document()["reviewerRegistry"]
        holders = [reference for reference, record in reviewers.items()
                   if "external-verification" in record.get("roles", [])]
        self.assertEqual([], holders, "blocker 1 is still open")

    def test_no_product_approval_authority_is_named(self):
        """Phase 4F-F2 later cleared this blocker; 4C itself did not.

        The claim is made over the normalised context, so it still states
        what Phase 4C established.  The registration that cleared it is the
        product owner's own, recorded by an authorised later phase.
        """
        reviewers = F2.without_phase_4ff2_reviewer(
            H2.without_phase_4fh2_context(
                H21.without_phase_4fh21_context(
                    load_context_document())))["reviewerRegistry"]
        holders = [reference for reference, record in reviewers.items()
                   if "product-approval" in record.get("roles", [])]
        self.assertEqual([], holders, "product approval stays out of 4C")

    def test_no_example_authoring_authority_is_named(self):
        self.assertEqual({}, load_context_document()["authorRegistry"],
                         "blocker 2 is still open")

    def test_the_locked_stage_order_is_still_the_one_we_reasoned_about(self):
        self.assertEqual(
            ("external-verification", "native-linguistic", "product-approval"),
            T.STAGE_KINDS)
        self.assertLess(0, T.SCOPE_VERSION)
        self.assertEqual(1, T.SCOPE_VERSION)


if __name__ == "__main__":
    unittest.main()
