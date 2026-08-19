"""Closure checks for Priority 7 Phase 4F-D1.

Phase 4F-D1 is an assessment-only phase.  It reviews the integrated 45-pattern
corpus for final editorial acceptance and writes three report artifacts plus
this suite.  It writes nothing canonical.

This suite therefore proves two different things.  First, that the D1 review
artifacts are internally complete and consistent: 45 rows, the exact reviewed
pattern set, a valid verdict/severity enum, YES/NO consistency, unique finding
IDs, and a blind Codex package that cannot leak the D1 verdict.  Second, that
the reviewed corpus, authoring context and tooling at the immutable historical
baseline had no review event or approval, and that D1 owned no canonical,
shipping or runtime artifact.

Historical comparisons read Git objects at the pinned D1 baseline, never the
live working tree.  The footprint check resolves this audit-history candidate
as the first descendant of its D3.1 baseline and then selects D1's explicit
phase-owned artifacts, so later Priority 7 phases do not falsify D1 history.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CORPUS_FILE = ROOT / "editorial" / "verb-pattern-candidates.json"
CONTEXT_FILE = ROOT / "editorial" / "priority-7-authoring-context.json"
TOOLING_FILE = ROOT / "priority7_tooling.py"

MATRIX_FILE = ROOT / "reports" / "priority-7-phase-4fd1-final-editorial-matrix.csv"
BLIND_FILE = ROOT / "reports" / "priority-7-phase-4fd1-blind-final-review-input.csv"
SUMMARY_FILE = ROOT / "reports" / "priority-7-phase-4fd1-summary.md"

BASELINE_COMMIT = "3d613def18e9edf8bcabd331d40b5b90df30a9da"
BASELINE_TREE = "3d1a9600041f83a9a2374b0fef5a069bc77a4d63"
AUDIT_BASELINE_COMMIT = "ea60d346dac2de519f487c16165e1f523dd00350"
CURRENT_CANONICAL_SHA256 = "924d1bf185f13ad885a4b1ddc57651c1d8bb1f2b5258f2dc379be6ea97e7a9a3"

CANONICAL_SHA256 = "6a174face8dffdcf26f0c2e073bf183287f9d67c09ac28d661ce61c3b257c257"
CONTEXT_SHA256 = "bee8eb95ed78775e50a7fc57da2381d67c43087b00c836e6e6cb0c81925df718"
TOOLING_SHA256 = "bbb8b31d9bd25ed601fec8c97e2313d2d808bfd68c55b48eb4b5de970fdfb7c2"

D1_ARTIFACTS = {
    "reports/priority-7-phase-4fd1-final-editorial-matrix.csv",
    "reports/priority-7-phase-4fd1-blind-final-review-input.csv",
    "reports/priority-7-phase-4fd1-summary.md",
    "tests/test_priority7_phase4fd1.py",
}

AUDIT_HISTORY_ARTIFACTS = D1_ARTIFACTS | {
    "reports/priority-7-phase-4fd2-blind-final-editorial-matrix.csv",
    "reports/priority-7-phase-4fd2-summary.md",
    "tests/test_priority7_phase4fd2.py",
}

VERDICTS = {"ACCEPT", "ACCEPT WITH NOTE", "CHANGES NEEDED", "DEFER"}
SEVERITIES = {"NONE", "LOW", "MEDIUM", "HIGH"}
BLOCKING_VERDICTS = {"CHANGES NEEDED", "DEFER"}

# Section 21: the blind package must not carry these as columns or as obvious
# serialized field names inside its cells.
FORBIDDEN_BLIND_TOKENS = (
    "verdict", "severity", "acceptancerecommended", "findingid",
    "findingsummary", "requiredcanonicalchange", "nonblockingnote",
    "recommendation",
)

# Verdict vocabulary that would let Codex infer the D1 answer from prose.
FORBIDDEN_BLIND_PHRASES = (
    "accept with note", "changes needed", "defer", "accept as is",
    "nonblocking", "non-blocking", "blocking", "p7-d1-",
)

RUNTIME_PREFIXES = (
    "audio/", "fonts/", "grammar/", "guide/", "vocabulary/", "data-",
    "pp-", "index.html", "sw.js", "manifest.json", "sitemap.xml",
    "audio-manifest.json", "build_pages.py", "validate_content.py",
    "verify_audio.py", "generate_audio.py", "pp_audio_rule.py",
    "priority7_tooling.py", "editorial/",
)


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True, check=True)


def git_blob(relative, revision=BASELINE_COMMIT):
    """Bytes for a path at an immutable revision, never the working tree."""
    return subprocess.run(
        ["git", "show", f"{revision}:{relative}"], cwd=ROOT,
        capture_output=True, check=True).stdout


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def candidate_revision():
    """The committed audit-history transition, or None while uncommitted.

    Resolved from the accepted D3.1 baseline so later phases cannot change it.
    """
    head = git("rev-parse", "HEAD").stdout.strip()
    if head == AUDIT_BASELINE_COMMIT:
        return None
    revisions = git("rev-list", "--reverse", "--ancestry-path",
                    f"{AUDIT_BASELINE_COMMIT}..HEAD").stdout.split()
    if not revisions:
        raise AssertionError("audit baseline is not an ancestor of HEAD")
    return revisions[0]


def audit_candidate_footprint():
    """Exact audit-history transition, independent of later commits."""
    revision = candidate_revision()
    if revision is None:
        return {line[3:] for line in
                git("status", "--porcelain", "-uall").stdout.splitlines()}
    return set(git("diff", "--name-only", AUDIT_BASELINE_COMMIT, revision)
               .stdout.split())


def candidate_footprint():
    """D1's explicit phase-owned part of the audit-history transition."""
    return audit_candidate_footprint() & D1_ARTIFACTS


def canonical_patterns():
    document = json.loads(git_blob("editorial/verb-pattern-candidates.json"))
    out = []
    for lemma in document["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                out.append((lemma, meaning, pattern))
    return out


# ---------------------------------------------------------------------------
# 1.  The D1 matrix covers exactly the 45 canonical patterns
# ---------------------------------------------------------------------------

class MatrixCoverageTests(unittest.TestCase):

    def setUp(self):
        self.rows = rows(MATRIX_FILE)
        self.patterns = canonical_patterns()

    def test_the_matrix_has_exactly_forty_five_rows(self):
        self.assertEqual(45, len(self.rows))

    def test_the_matrix_covers_the_exact_canonical_pattern_id_set(self):
        self.assertEqual({p["id"] for _, _, p in self.patterns},
                         {r["patternId"] for r in self.rows})

    def test_no_pattern_is_reviewed_twice(self):
        ids = [r["patternId"] for r in self.rows]
        self.assertEqual(len(ids), len(set(ids)))

    def test_review_ids_are_unique_and_well_formed(self):
        review_ids = [r["reviewId"] for r in self.rows]
        self.assertEqual(45, len(set(review_ids)))
        for review_id in review_ids:
            self.assertRegex(review_id, r"^P7-NR-\d{3}$")

    def test_matrix_lemma_meaning_and_relation_match_canonical_data(self):
        by_pattern = {p["id"]: (l, m, p) for l, m, p in self.patterns}
        for row in self.rows:
            lemma, meaning, pattern = by_pattern[row["patternId"]]
            with self.subTest(row=row["reviewId"]):
                self.assertEqual(lemma["id"], row["lemmaId"])
                self.assertEqual(lemma["canonicalLemma"], row["lemma"])
                self.assertEqual(meaning["id"], row["meaningId"])
                self.assertEqual(pattern["relationType"], row["relationType"])
                self.assertEqual(pattern["teachingStatus"],
                                 row["teachingStatus"])
                self.assertEqual(pattern["cefr"].get("recognition", ""),
                                 row["cefrRecognition"])
                self.assertEqual(pattern["cefr"].get("production", ""),
                                 row["cefrProduction"])

    def test_matrix_example_columns_match_canonical_examples(self):
        by_pattern = {p["id"]: p for _, _, p in self.patterns}
        for row in self.rows:
            examples = by_pattern[row["patternId"]].get("examples") or []
            with self.subTest(row=row["reviewId"]):
                if examples:
                    self.assertEqual(examples[0]["id"], row["exampleId"])
                    self.assertTrue(row["exampleOrigin"])
                else:
                    self.assertEqual("", row["exampleId"])
                    self.assertEqual("", row["exampleOrigin"])

    def test_every_required_assessment_column_is_present_and_filled(self):
        required = (
            "meaningFit", "patternCorrectness", "complementCorrectness",
            "learnerExplanationAssessment", "errorNotesAssessment",
            "exampleAssessment", "englishAssessment", "cefrAssessment",
            "statusAssessment", "siblingPatternAssessment",
            "provenanceAssessment",
        )
        for row in self.rows:
            for column in required:
                with self.subTest(row=row["reviewId"], column=column):
                    self.assertIn(column, row)
                    self.assertTrue(row[column].strip())


# ---------------------------------------------------------------------------
# 2.  Verdict, severity and acceptance are a coherent closed system
# ---------------------------------------------------------------------------

class VerdictIntegrityTests(unittest.TestCase):

    def setUp(self):
        self.rows = rows(MATRIX_FILE)

    def test_every_verdict_is_in_the_enum(self):
        for row in self.rows:
            with self.subTest(row=row["reviewId"]):
                self.assertIn(row["d1Verdict"], VERDICTS)

    def test_every_severity_is_in_the_enum(self):
        for row in self.rows:
            with self.subTest(row=row["reviewId"]):
                self.assertIn(row["severity"], SEVERITIES)

    def test_acceptance_recommendation_follows_the_verdict(self):
        for row in self.rows:
            expected = "NO" if row["d1Verdict"] in BLOCKING_VERDICTS else "YES"
            with self.subTest(row=row["reviewId"]):
                self.assertIn(row["editorialAcceptanceRecommended"],
                              {"YES", "NO"})
                self.assertEqual(expected,
                                 row["editorialAcceptanceRecommended"])

    def test_accept_rows_carry_no_finding_and_no_severity(self):
        for row in self.rows:
            if row["d1Verdict"] != "ACCEPT":
                continue
            with self.subTest(row=row["reviewId"]):
                self.assertEqual("NONE", row["severity"])
                self.assertEqual("", row["findingId"])
                self.assertEqual("", row["findingSummary"])
                self.assertEqual("", row["nonblockingNote"])

    def test_non_none_rows_have_unique_stable_finding_ids(self):
        finding_ids = [r["findingId"] for r in self.rows
                       if r["severity"] != "NONE"]
        self.assertTrue(finding_ids)
        self.assertEqual(len(finding_ids), len(set(finding_ids)))
        for finding_id in finding_ids:
            self.assertRegex(finding_id, r"^P7-D1-\d{3}$")

    def test_every_non_none_row_states_a_finding(self):
        for row in self.rows:
            if row["severity"] == "NONE":
                continue
            with self.subTest(row=row["reviewId"]):
                self.assertTrue(row["findingId"].strip())
                self.assertTrue(row["findingSummary"].strip())

    def test_blocking_rows_carry_a_required_canonical_change(self):
        """CHANGES NEEDED / DEFER must state the change, and be MEDIUM or HIGH."""
        for row in self.rows:
            if row["d1Verdict"] not in BLOCKING_VERDICTS:
                continue
            with self.subTest(row=row["reviewId"]):
                self.assertTrue(row["requiredCanonicalChange"].strip())
                self.assertIn(row["severity"], {"MEDIUM", "HIGH"})

    def test_accepted_rows_hide_no_required_canonical_change(self):
        for row in self.rows:
            if row["d1Verdict"] in BLOCKING_VERDICTS:
                continue
            with self.subTest(row=row["reviewId"]):
                self.assertEqual("", row["requiredCanonicalChange"].strip())

    def test_accept_with_note_rows_justify_why_the_note_is_nonblocking(self):
        for row in self.rows:
            if row["d1Verdict"] != "ACCEPT WITH NOTE":
                continue
            with self.subTest(row=row["reviewId"]):
                self.assertTrue(row["nonblockingNote"].strip())
                self.assertIn("Nonblocking because:", row["nonblockingNote"])

    def test_severity_and_verdict_do_not_contradict(self):
        for row in self.rows:
            with self.subTest(row=row["reviewId"]):
                if row["severity"] == "NONE":
                    self.assertEqual("ACCEPT", row["d1Verdict"])
                if row["d1Verdict"] == "ACCEPT WITH NOTE":
                    self.assertIn(row["severity"], {"LOW", "MEDIUM"})


# ---------------------------------------------------------------------------
# 3.  The blind Codex package is complete and cannot leak the verdict
# ---------------------------------------------------------------------------

class BlindPackageTests(unittest.TestCase):

    def setUp(self):
        self.blind = rows(BLIND_FILE)
        self.matrix = rows(MATRIX_FILE)

    def test_blind_input_covers_the_same_exact_forty_five_patterns(self):
        self.assertEqual(45, len(self.blind))
        self.assertEqual({r["patternId"] for r in self.matrix},
                         {r["patternId"] for r in self.blind})
        self.assertEqual({p["id"] for _, _, p in canonical_patterns()},
                         {r["patternId"] for r in self.blind})

    def test_blind_input_has_no_duplicate_rows(self):
        ids = [r["patternId"] for r in self.blind]
        self.assertEqual(len(ids), len(set(ids)))

    def test_blind_headers_contain_no_verdict_bearing_field(self):
        headers = list(self.blind[0].keys())
        for header in headers:
            normalised = header.lower().replace("_", "").replace("-", "")
            for token in FORBIDDEN_BLIND_TOKENS:
                with self.subTest(header=header, token=token):
                    self.assertNotIn(token, normalised)

    def test_blind_cells_contain_no_serialized_verdict_field_name(self):
        for row in self.blind:
            for column, value in row.items():
                normalised = (value or "").lower().replace("_", "")
                normalised = normalised.replace("-", "").replace(" ", "")
                for token in FORBIDDEN_BLIND_TOKENS:
                    with self.subTest(row=row["reviewId"], column=column,
                                      token=token):
                        self.assertNotIn(token, normalised)

    def test_blind_cells_contain_no_adjudication_vocabulary(self):
        for row in self.blind:
            for column, value in row.items():
                lowered = (value or "").lower()
                for phrase in FORBIDDEN_BLIND_PHRASES:
                    with self.subTest(row=row["reviewId"], column=column,
                                      phrase=phrase):
                        self.assertNotIn(phrase, lowered)

    def test_blind_input_carries_enough_canonical_context_to_assess(self):
        needed = ("lemma", "meaningKey", "meaningGlossesEn", "relationType",
                  "complements", "cefrRecognition", "teachingStatus",
                  "learnerExplanationEn", "errorNotes", "examplePl",
                  "exampleEn", "exampleOrigin", "evidenceSources",
                  "siblingPatterns")
        for column in needed:
            self.assertIn(column, self.blind[0])
        for row in self.blind:
            with self.subTest(row=row["reviewId"]):
                self.assertTrue(row["lemma"].strip())
                self.assertTrue(row["complements"].strip())
                self.assertTrue(row["learnerExplanationEn"].strip())
                self.assertTrue(row["evidenceSources"].strip())

    def test_blind_example_fields_match_canonical_examples(self):
        by_pattern = {p["id"]: p for _, _, p in canonical_patterns()}
        for row in self.blind:
            examples = by_pattern[row["patternId"]].get("examples") or []
            with self.subTest(row=row["reviewId"]):
                if examples:
                    self.assertEqual(examples[0]["pl"], row["examplePl"])
                    self.assertEqual(examples[0]["en"], row["exampleEn"])
                else:
                    self.assertEqual("", row["examplePl"])
                    self.assertEqual("", row["exampleEn"])

    def test_blind_package_is_not_merely_the_matrix_with_columns_dropped(self):
        """It must add canonical context the matrix does not carry."""
        extra = set(self.blind[0]) - set(self.matrix[0])
        for column in ("learnerExplanationEn", "errorNotes", "examplePl",
                       "evidenceSources", "siblingPatterns"):
            self.assertIn(column, extra)


class ArtifactHygieneTests(unittest.TestCase):
    """The D1 reports must satisfy `git diff --check` on their own terms."""

    ARTIFACTS = (MATRIX_FILE, BLIND_FILE, SUMMARY_FILE)

    def test_artifacts_use_lf_line_endings(self):
        """csv.writer defaults to CRLF, which git reads as trailing whitespace."""
        for path in self.ARTIFACTS:
            with self.subTest(path=path.name):
                self.assertNotIn(b"\r", path.read_bytes())

    def test_artifacts_have_no_trailing_whitespace(self):
        for path in self.ARTIFACTS:
            for number, line in enumerate(
                    path.read_text(encoding="utf-8").splitlines(), start=1):
                with self.subTest(path=path.name, line=number):
                    self.assertEqual(line.rstrip(), line)

    def test_artifacts_end_with_exactly_one_newline(self):
        for path in self.ARTIFACTS:
            data = path.read_bytes()
            with self.subTest(path=path.name):
                self.assertTrue(data.endswith(b"\n"))
                self.assertFalse(data.endswith(b"\n\n"))


# ---------------------------------------------------------------------------
# 4.  D1 changed nothing canonical
# ---------------------------------------------------------------------------

class CanonicalImmutabilityTests(unittest.TestCase):

    def test_reviewed_corpus_matches_the_published_historical_sha256(self):
        historical = git_blob("editorial/verb-pattern-candidates.json")
        self.assertEqual(CANONICAL_SHA256, sha256(historical))

    def test_reviewed_authoring_context_matches_the_historical_sha256(self):
        historical = git_blob("editorial/priority-7-authoring-context.json")
        self.assertEqual(CONTEXT_SHA256, sha256(historical))

    def test_reviewed_tooling_is_read_from_the_historical_boundary(self):
        historical = git_blob("priority7_tooling.py")
        self.assertEqual(TOOLING_SHA256, sha256(historical))

    def test_current_successor_is_not_mistaken_for_the_reviewed_corpus(self):
        historical = git_blob("editorial/verb-pattern-candidates.json")
        current = git_blob("editorial/verb-pattern-candidates.json",
                           AUDIT_BASELINE_COMMIT)
        self.assertNotEqual(historical, current)
        self.assertEqual(CURRENT_CANONICAL_SHA256, sha256(current))

    def test_baseline_tree_is_the_expected_tree(self):
        self.assertEqual(
            BASELINE_TREE,
            git("rev-parse", f"{BASELINE_COMMIT}^{{tree}}").stdout.strip())

    def test_this_suite_never_uses_head_as_the_historical_side(self):
        source = Path(__file__).read_text(encoding="utf-8")
        self.assertNotRegex(source, r"git_blob\(\s*f?[\"']HEAD")
        self.assertNotRegex(source, r"[\"']show[\"']\s*,\s*f?[\"']HEAD")


# ---------------------------------------------------------------------------
# 5.  The corpus is still the reviewed pilot: no event, no approval
# ---------------------------------------------------------------------------

class CorpusStateTests(unittest.TestCase):

    def setUp(self):
        self.patterns = canonical_patterns()
        self.document = json.loads(
            git_blob("editorial/verb-pattern-candidates.json"))

    def test_the_corpus_still_holds_thirty_lemmas_and_forty_five_patterns(self):
        self.assertEqual(30, len(self.document["lemmas"]))
        self.assertEqual(
            34, sum(len(l["meanings"]) for l in self.document["lemmas"]))
        self.assertEqual(45, len(self.patterns))

    def test_all_forty_five_patterns_are_reference_verified(self):
        states = [p.get("reviewState") for _, _, p in self.patterns]
        self.assertEqual({"reference-verified"}, set(states))
        self.assertEqual(45, len(states))

    def test_there_are_exactly_forty_seven_reference_verification_accepts(self):
        accepts = [event
                   for _, _, pattern in self.patterns
                   for event in pattern.get("reviewEvents", [])
                   if event["kind"] == "reference-verification"
                   and event["decision"] == "accept"]
        self.assertEqual(47, len(accepts))

    def test_there_are_exactly_twenty_nine_canonical_examples(self):
        examples = [e for _, _, p in self.patterns
                    for e in (p.get("examples") or [])]
        self.assertEqual(29, len(examples))

    def test_no_editorial_review_event_exists(self):
        for _, _, pattern in self.patterns:
            for event in pattern.get("reviewEvents", []):
                with self.subTest(pattern=pattern["id"]):
                    self.assertNotEqual("editorial-review", event["kind"])

    def test_no_product_approval_exists(self):
        for _, _, pattern in self.patterns:
            with self.subTest(pattern=pattern["id"]):
                self.assertNotEqual("approved", pattern.get("reviewState"))
                for event in pattern.get("reviewEvents", []):
                    self.assertNotEqual("product-approval", event["kind"])

    def test_only_the_reference_analysis_actor_has_acted_on_review_events(self):
        actors = {event.get("actorRef")
                  for _, _, pattern in self.patterns
                  for event in pattern.get("reviewEvents", [])}
        self.assertEqual({"priority7-reference-analysis"}, actors)

    def test_no_editorial_review_actor_was_registered(self):
        context = json.loads(
            git_blob("editorial/priority-7-authoring-context.json"))
        registry = context["editorialActorRegistry"]
        for name, actor in registry.items():
            with self.subTest(actor=name):
                self.assertNotIn("editorial-review", actor["roles"])
        self.assertEqual({}, context["authorRegistry"])

    def test_example_provenance_is_nonhuman_and_truthful(self):
        kinds = []
        for _, _, pattern in self.patterns:
            for example in pattern.get("examples") or []:
                origin = example["origin"]
                kinds.append(origin["kind"])
                with self.subTest(example=example["id"]):
                    self.assertIn(origin["kind"],
                                  {"repository-reuse", "editorial-generated"})
                    self.assertNotEqual("original", origin["kind"])
                    if origin["kind"] == "editorial-generated":
                        self.assertEqual("priority7-example-generation",
                                         origin["generatorRef"])
        self.assertEqual(18, kinds.count("repository-reuse"))
        self.assertEqual(11, kinds.count("editorial-generated"))

    def test_activity_eligibility_is_empty_everywhere(self):
        for _, _, pattern in self.patterns:
            with self.subTest(pattern=pattern["id"]):
                self.assertEqual([], pattern.get("activityEligibility"))

    def test_recognition_only_rows_declare_no_production_level(self):
        for _, _, pattern in self.patterns:
            if pattern["teachingStatus"] == "active-production":
                continue
            with self.subTest(pattern=pattern["id"]):
                self.assertNotIn("production", pattern["cefr"])


# ---------------------------------------------------------------------------
# 6.  Current-phase footprint, without a future-hostile historical claim
# ---------------------------------------------------------------------------

class CandidateFootprintTests(unittest.TestCase):
    """Section 25.  This checks THIS candidate only.

    It deliberately does not assert that no later Priority 7 phase may add a
    file: the candidate is resolved as the first descendant of the baseline, so
    later commits leave this answer unchanged.
    """

    def test_the_repository_has_no_remote(self):
        self.assertEqual("", git("remote").stdout)

    def test_the_candidate_introduces_only_its_own_artifacts(self):
        self.assertEqual(D1_ARTIFACTS, candidate_footprint())

    def test_the_audit_history_transition_has_exactly_seven_artifacts(self):
        self.assertEqual(AUDIT_HISTORY_ARTIFACTS,
                         audit_candidate_footprint())

    def test_the_candidate_is_a_child_of_the_baseline_when_committed(self):
        revision = candidate_revision()
        if revision is None:
            self.assertEqual(AUDIT_BASELINE_COMMIT,
                             git("rev-parse", "HEAD").stdout.strip())
        else:
            self.assertEqual(
                AUDIT_BASELINE_COMMIT,
                git("rev-parse", f"{revision}^").stdout.strip())

    def test_no_shipping_or_runtime_path_was_touched(self):
        for path in candidate_footprint():
            with self.subTest(path=path):
                self.assertFalse(
                    path.startswith(RUNTIME_PREFIXES),
                    f"D1 must not touch shipping/runtime path {path}")

    def test_the_candidate_touches_no_canonical_editorial_file(self):
        footprint = candidate_footprint()
        self.assertNotIn("editorial/verb-pattern-candidates.json", footprint)
        self.assertNotIn("editorial/priority-7-authoring-context.json",
                         footprint)
        self.assertNotIn("priority7_tooling.py", footprint)

    def test_the_candidate_adds_no_other_test_suite(self):
        suites = {p for p in candidate_footprint()
                  if p.startswith("tests/") and p.endswith(".py")}
        self.assertEqual({"tests/test_priority7_phase4fd1.py"}, suites)


# ---------------------------------------------------------------------------
# 7.  The summary reports the review honestly
# ---------------------------------------------------------------------------

class SummaryTests(unittest.TestCase):

    def setUp(self):
        self.text = SUMMARY_FILE.read_text(encoding="utf-8")
        self.flowed = re.sub(r"\s+", " ", self.text)
        self.rows = rows(MATRIX_FILE)

    def test_the_summary_pins_the_baseline_commit_tree_and_hashes(self):
        for token in (BASELINE_COMMIT, BASELINE_TREE, CANONICAL_SHA256,
                      CONTEXT_SHA256):
            self.assertIn(token, self.text)

    def test_the_summary_reports_the_actual_verdict_counts(self):
        counts = {}
        for row in self.rows:
            counts[row["d1Verdict"]] = counts.get(row["d1Verdict"], 0) + 1
        for verdict, count in counts.items():
            self.assertIn(f"{verdict} | {count}", self.text)

    def test_the_summary_states_every_blocking_row(self):
        blocking = [r["reviewId"] for r in self.rows
                    if r["d1Verdict"] in BLOCKING_VERDICTS]
        for review_id in blocking:
            self.assertIn(review_id, self.text)
        if not blocking:
            self.assertIn("no blocking rows", self.flowed.lower())

    def test_the_summary_names_every_row_carrying_a_note(self):
        for row in self.rows:
            if row["d1Verdict"] != "ACCEPT WITH NOTE":
                continue
            with self.subTest(row=row["reviewId"]):
                self.assertIn(row["reviewId"], self.text)
                self.assertIn(row["findingId"], self.text)

    def test_the_summary_reports_the_five_b3b_corrections(self):
        for review_id in ("P7-NR-005", "P7-NR-029", "P7-NR-030",
                          "P7-NR-037", "P7-NR-040"):
            self.assertIn(review_id, self.text)

    def test_the_summary_reports_the_previously_discussed_points(self):
        for review_id in ("P7-NR-013", "P7-NR-031", "P7-NR-039",
                          "P7-NR-042", "P7-NR-043"):
            self.assertIn(review_id, self.text)

    def test_the_summary_confirms_the_boundaries_d1_did_not_cross(self):
        lowered = self.flowed.lower()
        self.assertIn("no canonical content changed", lowered)
        self.assertIn("no editorial-review event", lowered)

    def test_the_summary_carries_the_blind_package_sha256(self):
        digest = sha256(BLIND_FILE.read_bytes())
        self.assertIn(digest, self.text)

    def test_the_summary_does_not_claim_global_textual_uniqueness(self):
        lowered = self.flowed.lower()
        self.assertNotIn("globally unique", lowered)
        self.assertNotIn("internet-wide", lowered.replace("no internet-wide", ""))


if __name__ == "__main__":
    unittest.main()
