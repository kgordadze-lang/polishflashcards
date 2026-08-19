"""Independent closure checks for Priority 7 Phase 4F-D2.

The suite validates the D2 review artifacts against the immutable corpus D2
actually received.  It keeps that historical claim separate from the accepted
D3.1 successor and remains stable when later phase artifacts are committed.
"""

from __future__ import annotations

import collections
import csv
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path

import priority7_tooling as T
from tests import test_priority7_phase4fc2 as C2


ROOT = Path(__file__).resolve().parents[1]
BASELINE_COMMIT = "3d613def18e9edf8bcabd331d40b5b90df30a9da"
BASELINE_TREE = "3d1a9600041f83a9a2374b0fef5a069bc77a4d63"
AUDIT_BASELINE_COMMIT = "ea60d346dac2de519f487c16165e1f523dd00350"
CORPUS = ROOT / "editorial" / "verb-pattern-candidates.json"
CONTEXT = ROOT / "editorial" / "priority-7-authoring-context.json"
TOOLING = ROOT / "priority7_tooling.py"
BLIND_INPUT = ROOT / "reports" / "priority-7-phase-4fd1-blind-final-review-input.csv"
MATRIX = ROOT / "reports" / "priority-7-phase-4fd2-blind-final-editorial-matrix.csv"
SUMMARY = ROOT / "reports" / "priority-7-phase-4fd2-summary.md"

CORPUS_SHA256 = "6a174face8dffdcf26f0c2e073bf183287f9d67c09ac28d661ce61c3b257c257"
CURRENT_CORPUS_SHA256 = "924d1bf185f13ad885a4b1ddc57651c1d8bb1f2b5258f2dc379be6ea97e7a9a3"
CONTEXT_SHA256 = "bee8eb95ed78775e50a7fc57da2381d67c43087b00c836e6e6cb0c81925df718"
TOOLING_SHA256 = "bbb8b31d9bd25ed601fec8c97e2313d2d808bfd68c55b48eb4b5de970fdfb7c2"
BLIND_SHA256 = "069ceee9e55bc3f1fffa152014dec024de826b8001caa0beabcffbdff114c916"

D2_ARTIFACTS = {
    "reports/priority-7-phase-4fd2-blind-final-editorial-matrix.csv",
    "reports/priority-7-phase-4fd2-summary.md",
    "tests/test_priority7_phase4fd2.py",
}

AUDIT_HISTORY_ARTIFACTS = D2_ARTIFACTS | {
    "reports/priority-7-phase-4fd1-blind-final-review-input.csv",
    "reports/priority-7-phase-4fd1-final-editorial-matrix.csv",
    "reports/priority-7-phase-4fd1-summary.md",
    "tests/test_priority7_phase4fd1.py",
}

VERDICTS = {"ACCEPT", "ACCEPT WITH NOTE", "CHANGES NEEDED", "DEFER"}
SEVERITIES = {"NONE", "LOW", "MEDIUM", "HIGH"}
EXPECTED_BLOCKERS = {
    "P7-NR-011": ("P7-D2-001", "I thank my sister for dinner.",
                  "I say thank you to my sister for dinner."),
    "P7-NR-018": ("P7-D2-002", "I look after my fitness every day.",
                  "I work on my fitness every day."),
    "P7-NR-028": ("P7-D2-003", "I like reading before sleep.",
                  "I like reading before bed."),
    "P7-NR-037": ("P7-D2-004", "ten film podoba mi się",
                  "ten film mi się podoba"),
}

REQUIRED_MATRIX_FIELDS = {
    "reviewId", "lemmaId", "lemma", "meaningId", "patternId",
    "relationType", "teachingStatus", "cefrRecognition", "cefrProduction",
    "exampleId", "exampleOrigin", "d2Verdict", "severity",
    "editorialAcceptanceRecommended", "meaningFit", "patternCorrectness",
    "complementCorrectness", "learnerExplanationAssessment",
    "errorNotesAssessment", "exampleAssessment", "englishAssessment",
    "cefrAssessment", "statusAssessment", "siblingPatternAssessment",
    "provenanceAssessment", "findingId", "findingSummary",
    "requiredCanonicalChange", "nonblockingNote", "blockingField",
    "currentValue", "blockingRationale", "recommendedCorrection",
    "affectsTier1ReferenceScope", "freshReferenceVerificationRequired",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=check)


def git_blob(relative: str, revision: str = BASELINE_COMMIT) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{revision}:{relative}"], cwd=ROOT,
        capture_output=True, check=True)
    return result.stdout


def candidate_revision() -> str | None:
    """Return the audit-history transition, ignoring later commits."""
    head = git("rev-parse", "HEAD").stdout.strip()
    if head == AUDIT_BASELINE_COMMIT:
        return None
    ancestor = git("merge-base", "--is-ancestor", AUDIT_BASELINE_COMMIT, "HEAD",
                   check=False)
    if ancestor.returncode != 0:
        raise AssertionError("the audit baseline is not an ancestor of HEAD")
    revisions = git(
        "rev-list", "--reverse", "--ancestry-path",
        f"{AUDIT_BASELINE_COMMIT}..HEAD").stdout.split()
    if not revisions:
        raise AssertionError("HEAD differs from the baseline without a descendant")
    return revisions[0]


def audit_candidate_footprint() -> set[str]:
    revision = candidate_revision()
    if revision is None:
        return {line[3:] for line in
                git("status", "--porcelain", "-uall").stdout.splitlines()}
    return set(git(
        "diff", "--name-only", AUDIT_BASELINE_COMMIT, revision).stdout.split())


def candidate_footprint() -> set[str]:
    """D2's explicit phase-owned part of the audit-history transition."""
    return audit_candidate_footprint() & D2_ARTIFACTS


class D2ArtifactCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.corpus_bytes = git_blob("editorial/verb-pattern-candidates.json")
        cls.context_bytes = git_blob(
            "editorial/priority-7-authoring-context.json")
        cls.corpus = json.loads(cls.corpus_bytes)
        cls.context = json.loads(cls.context_bytes)
        cls.matrix = read_csv(MATRIX)
        cls.blind = read_csv(BLIND_INPUT)
        cls.summary = SUMMARY.read_text(encoding="utf-8")
        cls.patterns = {
            pattern["id"]: (lemma, meaning, pattern)
            for lemma, meaning, pattern in C2.iter_patterns(cls.corpus)
        }


class BlindnessAndBaselineTests(D2ArtifactCase):

    def test_baseline_commit_tree_and_repository_boundary_are_exact(self):
        self.assertEqual(BASELINE_COMMIT,
                         git("rev-parse", f"{BASELINE_COMMIT}^{{commit}}").stdout.strip())
        self.assertEqual(BASELINE_TREE,
                         git("rev-parse", f"{BASELINE_COMMIT}^{{tree}}").stdout.strip())
        self.assertEqual([], git("remote").stdout.split())

    def test_the_d1_input_supplied_to_d2_is_verdict_free(self):
        forbidden_fields = {
            "d1Verdict", "severity", "editorialAcceptanceRecommended",
            "findingId", "findingSummary", "requiredCanonicalChange",
            "nonblockingNote", "recommendation",
        }
        self.assertTrue(forbidden_fields.isdisjoint(self.blind[0]))
        payload = "\n".join(
            value for row in self.blind for value in row.values()).lower()
        for phrase in ("accept with note", "changes needed", "p7-d1-"):
            self.assertNotIn(phrase, payload)
        self.assertIn("No D1 final editorial", self.summary)

    def test_blind_input_digest_is_exact_and_recorded(self):
        self.assertEqual(BLIND_SHA256, digest(BLIND_INPUT))
        self.assertIn(BLIND_SHA256, self.summary)
        self.assertIn("No D1 final editorial", self.summary)

    def test_historical_canonical_files_and_tooling_match_pinned_digests(self):
        checks = (
            ("editorial/verb-pattern-candidates.json", CORPUS_SHA256),
            ("editorial/priority-7-authoring-context.json", CONTEXT_SHA256),
            ("priority7_tooling.py", TOOLING_SHA256),
        )
        for relative, expected_digest in checks:
            with self.subTest(path=relative):
                self.assertEqual(
                    expected_digest, hashlib.sha256(git_blob(relative)).hexdigest())

    def test_current_successor_is_not_mistaken_for_the_reviewed_corpus(self):
        historical = git_blob("editorial/verb-pattern-candidates.json")
        current = git_blob("editorial/verb-pattern-candidates.json",
                           AUDIT_BASELINE_COMMIT)
        self.assertNotEqual(historical, current)
        self.assertEqual(CURRENT_CORPUS_SHA256,
                         hashlib.sha256(current).hexdigest())

    def test_candidate_commit_changes_only_d2_artifacts(self):
        self.assertEqual(D2_ARTIFACTS, candidate_footprint())

    def test_audit_history_transition_has_exactly_seven_artifacts(self):
        self.assertEqual(AUDIT_HISTORY_ARTIFACTS,
                         audit_candidate_footprint())


class CoverageAndMatrixTests(D2ArtifactCase):

    def test_matrix_has_all_required_columns(self):
        self.assertTrue(self.matrix)
        self.assertTrue(REQUIRED_MATRIX_FIELDS <= set(self.matrix[0]))

    def test_exactly_45_rows_and_unique_review_and_pattern_ids(self):
        self.assertEqual(45, len(self.blind))
        self.assertEqual(45, len(self.matrix))
        self.assertEqual(45, len({row["reviewId"] for row in self.matrix}))
        self.assertEqual(45, len({row["patternId"] for row in self.matrix}))

    def test_blind_and_matrix_pattern_sets_equal_the_canonical_set(self):
        canonical = set(self.patterns)
        self.assertEqual(45, len(canonical))
        self.assertEqual(canonical, {row["patternId"] for row in self.blind})
        self.assertEqual(canonical, {row["patternId"] for row in self.matrix})

    def test_matrix_identity_and_governance_columns_match_blind_input(self):
        blind = {row["reviewId"]: row for row in self.blind}
        fields = (
            "lemmaId", "lemma", "meaningId", "patternId", "relationType",
            "teachingStatus", "cefrRecognition", "cefrProduction",
            "exampleId", "exampleOrigin",
        )
        for row in self.matrix:
            with self.subTest(review_id=row["reviewId"]):
                self.assertEqual(
                    {field: blind[row["reviewId"]][field] for field in fields},
                    {field: row[field] for field in fields})

    def test_every_integrated_assessment_is_present(self):
        fields = (
            "meaningFit", "patternCorrectness", "complementCorrectness",
            "learnerExplanationAssessment", "errorNotesAssessment",
            "exampleAssessment", "englishAssessment", "cefrAssessment",
            "statusAssessment", "siblingPatternAssessment",
            "provenanceAssessment",
        )
        for row in self.matrix:
            with self.subTest(review_id=row["reviewId"]):
                self.assertTrue(all(row[field].strip() for field in fields))


class VerdictAndFindingTests(D2ArtifactCase):

    def test_verdict_severity_and_recommendation_enums_are_valid(self):
        for row in self.matrix:
            with self.subTest(review_id=row["reviewId"]):
                self.assertIn(row["d2Verdict"], VERDICTS)
                self.assertIn(row["severity"], SEVERITIES)
                self.assertIn(row["editorialAcceptanceRecommended"], {"YES", "NO"})

    def test_yes_no_consistency_is_exact(self):
        yes = {"ACCEPT", "ACCEPT WITH NOTE"}
        for row in self.matrix:
            expected = "YES" if row["d2Verdict"] in yes else "NO"
            with self.subTest(review_id=row["reviewId"]):
                self.assertEqual(expected, row["editorialAcceptanceRecommended"])

    def test_verdict_severity_and_yes_no_counts_are_pinned(self):
        self.assertEqual(
            {"ACCEPT": 41, "CHANGES NEEDED": 4},
            dict(collections.Counter(row["d2Verdict"] for row in self.matrix)))
        self.assertEqual(
            {"NONE": 41, "MEDIUM": 4},
            dict(collections.Counter(row["severity"] for row in self.matrix)))
        self.assertEqual(
            {"YES": 41, "NO": 4},
            dict(collections.Counter(
                row["editorialAcceptanceRecommended"] for row in self.matrix)))

    def test_finding_ids_are_unique_stable_and_required_for_non_none_rows(self):
        ids = [row["findingId"] for row in self.matrix if row["findingId"]]
        self.assertEqual([f"P7-D2-{index:03d}" for index in range(1, 5)], ids)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(re.fullmatch(r"P7-D2-\d{3}", value) for value in ids))
        for row in self.matrix:
            with self.subTest(review_id=row["reviewId"]):
                self.assertEqual(row["severity"] != "NONE", bool(row["findingId"]))

    def test_each_blocker_has_exact_change_scope_and_reverification_information(self):
        by_id = {row["reviewId"]: row for row in self.matrix}
        self.assertEqual(set(EXPECTED_BLOCKERS), {
            row["reviewId"] for row in self.matrix
            if row["d2Verdict"] == "CHANGES NEEDED"})
        for review_id, (finding_id, current, correction) in EXPECTED_BLOCKERS.items():
            row = by_id[review_id]
            with self.subTest(review_id=review_id):
                self.assertEqual(finding_id, row["findingId"])
                self.assertEqual("MEDIUM", row["severity"])
                self.assertEqual("NO", row["editorialAcceptanceRecommended"])
                self.assertTrue(row["blockingField"].strip())
                self.assertIn(current, row["currentValue"])
                self.assertTrue(row["blockingRationale"].strip())
                self.assertIn(correction, row["recommendedCorrection"])
                self.assertEqual("NO", row["affectsTier1ReferenceScope"])
                self.assertEqual("NO", row["freshReferenceVerificationRequired"])
                self.assertIn(row["blockingField"], row["requiredCanonicalChange"])
                self.assertIn(current, row["requiredCanonicalChange"])
                self.assertIn(correction, row["requiredCanonicalChange"])

    def test_accept_rows_hide_no_required_change_or_note(self):
        for row in self.matrix:
            if row["d2Verdict"] == "ACCEPT":
                with self.subTest(review_id=row["reviewId"]):
                    self.assertEqual("NONE", row["severity"])
                    self.assertEqual("", row["requiredCanonicalChange"])
                    self.assertEqual("", row["nonblockingNote"])
                    self.assertEqual("", row["findingId"])

    def test_summary_records_every_blocker_and_no_nonblocking_note(self):
        for review_id, (finding_id, current, correction) in EXPECTED_BLOCKERS.items():
            with self.subTest(review_id=review_id):
                self.assertIn(review_id, self.summary)
                self.assertIn(finding_id, self.summary)
                self.assertIn(current, self.summary)
                self.assertIn(correction, self.summary)
        self.assertIn("None. D2 did not use `ACCEPT WITH NOTE`", self.summary)
        self.assertIn("**GO WITH FINDINGS**", self.summary)


class CanonicalGovernanceTests(D2ArtifactCase):

    def test_canonical_counts_are_45_reference_verified_47_accepts_29_examples(self):
        patterns = [pattern for _, _, pattern in C2.iter_patterns(self.corpus)]
        self.assertEqual(45, len(patterns))
        self.assertEqual({"reference-verified"}, {
            pattern["reviewState"] for pattern in patterns})
        accepts = [
            event for pattern in patterns for event in pattern["reviewEvents"]
            if event["kind"] == "reference-verification"
            and event["decision"] == "accept"]
        self.assertEqual(47, len(accepts))
        self.assertEqual(29, len(C2.all_examples(self.corpus)))

    def test_no_editorial_review_product_approval_or_other_event_exists(self):
        patterns = [pattern for _, _, pattern in C2.iter_patterns(self.corpus)]
        kinds = collections.Counter(
            event["kind"] for pattern in patterns
            for event in pattern["reviewEvents"])
        self.assertEqual({"reference-verification": 47}, dict(kinds))
        self.assertEqual(0, sum(
            pattern["reviewState"] == "editorial-reviewed" for pattern in patterns))
        self.assertEqual(0, sum(
            pattern["reviewState"] == "approved" for pattern in patterns))

    def test_corpus_is_nonproduction_and_no_release_or_runtime_state_changed(self):
        self.assertEqual("priority-7-editorial-nonproduction",
                         self.corpus["artifactStatus"])
        self.assertEqual(3, len(D2_ARTIFACTS))  # non-vacuity for footprint guard
        self.assertFalse(any(path.startswith((
            "editorial/", "data-", "pp-", "index.html", "sw.js",
            "manifest.json", "audio", "build_pages.py", "validate_content.py"))
            for path in candidate_footprint()))

    def test_canonical_document_still_passes_editorial_validation(self):
        issues = T.validate_editorial(
            self.corpus, C2.build_context(self.context))
        self.assertEqual([], [str(issue) for issue in issues])


if __name__ == "__main__":
    unittest.main()
