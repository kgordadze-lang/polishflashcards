"""Priority 7 Phase 4F-C1C -- independent example review adjudication.

Phase 4F-C1 assessed the 13-row example queue and drafted proposals.  Phase
4F-C1B reviewed the same queue blind, from a package that deliberately
withheld C1's classifications, severities and recommendations.  This phase
reconciles the two and fixes one adjudicated result per row.

The suite proves four separate things:

1.  **Reconstruction.**  Both source matrices really do carry the same 13
    review IDs over the same 13 canonical pattern IDs, with no duplicate and
    no omission, and their current-example facts agree with the corpus.
2.  **Reproduction.**  Every ``c1*`` and ``c1b*`` column in the adjudication
    matrix is the source review's own value, not a retyping of it.
3.  **Completeness.**  Every row carries exactly one disposition, every
    REPLACE / ADD / CREATE row carries a complete final example spec, every
    repository-reuse final source resolves byte-exactly, and no final origin
    is ``original``.
4.  **Boundary.**  Nothing canonical, shipping or runtime moved, measured
    against the *pinned* baseline commit rather than ``HEAD``.

C1C is adjudication only.  Nothing in this file writes to the corpus, the
context, the tooling or any shipping file.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

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
sys.path.insert(0, str(ROOT))
_C1C_DIR = str(Path(__file__).resolve().parent)
if _C1C_DIR not in sys.path:
    sys.path.insert(0, _C1C_DIR)

import priority7_phase4fh3_normalizer as H3  # noqa: E402
import priority7_tooling as T  # noqa: E402

CORPUS = ROOT / "editorial" / "verb-pattern-candidates.json"
CONTEXT_FILE = ROOT / "editorial" / "priority-7-authoring-context.json"

C1_MATRIX = ROOT / "reports" / "phase-4fc1" / "example-matrix.csv"
C1_SUMMARY = ROOT / "reports" / "phase-4fc1" / "summary.md"
C1_BLIND_INPUT = ROOT / "reports" / "phase-4fc1" / "blind-review-input.csv"
C1B_MATRIX = ROOT / "reports" / "phase-4fc1b" / "example-review-matrix.csv"
C1B_SUMMARY = ROOT / "reports" / "phase-4fc1b" / "summary.md"

C1C_MATRIX = ROOT / "reports" / "phase-4fc1c" / "adjudication-matrix.csv"
C1C_SUMMARY = ROOT / "reports" / "phase-4fc1c" / "summary.md"

#: The three files Phase 4F-C1C added, as this workspace carries them.  The
#: adjudication artifacts were handed over under ``reports/phase-4fc1c/``
#: alongside the copied C1 and C1B directories rather than under the flat
#: ``reports/priority-7-phase-4fc1c-*`` names the C1C summary records.
C1C_ARTIFACTS = (
    "reports/phase-4fc1c/adjudication-matrix.csv",
    "reports/phase-4fc1c/summary.md",
    "tests/test_priority7_phase4fc1c.py",
)

#: The commit Phase 4F-B3B produced, which Phase 4F-C1, 4F-C1B and this phase
#: all take as their immutable baseline.  Pinned by SHA and never resolved as
#: ``HEAD``.  C1C changes nothing canonical, so a HEAD-anchored comparison
#: would be vacuous in the uncommitted workspace and *self-comparing* once the
#: C1C candidate is committed in a scratch rehearsal.  Every guard below reads
#: this SHA.
BASELINE_COMMIT = "080d92ad49a514332f21ecd90b4a11de070a243f"
BASELINE_TREE = "74dd8cbebc303b646e4e38e2082d25c91b1cf6e1"

#: Externally recorded in the phase brief: the blind package C1B actually
#: reviewed.  Anchoring on a hash supplied from outside the repository is what
#: makes the blindness claim checkable rather than self-asserted.
BLIND_INPUT_SHA256 = (
    "0af6c076be5c569074ed861e2c8e65fdd0bd048c3fa538f01ebbec60fac45771")

#: The other four copied review artifacts, hashed on arrival in this
#: workspace.  They are inputs, not outputs: C1C must not edit them.
SOURCE_ARTIFACT_SHA256 = {
    "reports/phase-4fc1/example-matrix.csv":
        "2422eed842c558f8cd6671123563b88b02e5464c0d06f63ed57fce817a410f4f",
    "reports/phase-4fc1/summary.md":
        "45ad110a3e2bcbd9c4c8f8881824b219ccbe0e0c293bcd364ee1877021599d7f",
    "reports/phase-4fc1b/example-review-matrix.csv":
        "0f43a13f300e94d5edb50018bcdab5de7c145a75040c8ba70b1a4064bc1ad50e",
    "reports/phase-4fc1b/summary.md":
        "645a4252eb911f802ead3f8ce3d3afe265970d7c49befbc83da6c83e659cdb9f",
}

QUEUE = (
    "P7-NR-007", "P7-NR-011", "P7-NR-012", "P7-NR-014", "P7-NR-018",
    "P7-NR-031", "P7-NR-032", "P7-NR-033", "P7-NR-035", "P7-NR-036",
    "P7-NR-042", "P7-NR-043", "P7-NR-044",
)

PATTERN_COUNT = 45
REFERENCE_VERIFIED_COUNT = 45
REFERENCE_ACCEPT_COUNT = 47
CANONICAL_EXAMPLE_COUNT = 23

CLASSIFICATIONS = {"MUST CHANGE", "USEFUL IMPROVEMENT", "NO CHANGE"}
SEVERITIES = {"HIGH", "MEDIUM", "LOW", "NONE"}
COMPARISONS = {
    "EXACT AGREEMENT", "COMPATIBLE DIFFERENCE", "SUBSTANTIVE DISAGREEMENT"}
DISPOSITIONS = {
    "KEEP CURRENT", "REPLACE", "ADD", "CREATE", "NO IMPLEMENTATION YET"}
PRIORITIES = {
    "REQUIRED FOR EDITORIAL ACCEPTANCE", "OPTIONAL POLISH", "NOT APPLICABLE"}
#: Section 5 of the brief.  ``original`` is deliberately absent: newly
#: generated material must never carry a human-authorship claim.
FINAL_ORIGINS = {"repository-reuse", "editorial-generated"}
NEEDS_SPEC = {"REPLACE", "ADD", "CREATE"}

EXPECTED_COMPARISONS = {
    "EXACT AGREEMENT": 5,
    "COMPATIBLE DIFFERENCE": 5,
    "SUBSTANTIVE DISAGREEMENT": 3,
}
EXPECTED_CLASSIFICATIONS = {
    "MUST CHANGE": 10, "USEFUL IMPROVEMENT": 1, "NO CHANGE": 2}
EXPECTED_DISPOSITIONS = {
    "KEEP CURRENT": 2, "REPLACE": 5, "ADD": 0, "CREATE": 6,
    "NO IMPLEMENTATION YET": 0}
EXPECTED_PRIORITIES = {
    "REQUIRED FOR EDITORIAL ACCEPTANCE": 10, "OPTIONAL POLISH": 1,
    "NOT APPLICABLE": 2}

#: The two rows whose current canonical example survives adjudication, with
#: the repository source it must keep resolving through.
KEEP_CURRENT_SOURCES = {
    "P7-NR-007": ("card", "a2-official-matters-019", "ex"),
    "P7-NR-014": ("card", "b1-media-technology-001", "ex"),
}

#: Shipping and runtime sentinels.  C1C is a reports-and-tests phase; if any
#: of these moved, the phase overstepped.
SHIPPING_SENTINELS = (
    "index.html", "manifest.json", "sw.js", "priority7_tooling.py",
    "pp-verb-patterns.js", "build_pages.py", "validate_content.py",
    "data-a1.js", "data-a2.js", "data-b1.js", "data-grammar.js",
    "data-verbs.js", "audio-manifest.json",
)

#: Everything C1C is allowed to touch, as prefixes.  Deliberately a prefix
#: allowlist and not a closed set -- that is the Phase 4F-C1.1 lesson applied
#: forward: a phase cannot enumerate what its successors may add.
C1C_FOOTPRINT_PREFIXES = ("reports/", "tests/")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_REPOSITORY_INDEX = None


def repository_index():
    global _REPOSITORY_INDEX
    if _REPOSITORY_INDEX is None:
        _REPOSITORY_INDEX = T.repository_index_from_root(ROOT)
    return _REPOSITORY_INDEX


def git(*arguments, cwd=ROOT):
    return subprocess.run(["git", *arguments], cwd=cwd,
                          capture_output=True, text=True)


def git_blob(path):
    """Read a path as of the pinned baseline commit, never as of HEAD."""
    result = git("show", f"{BASELINE_COMMIT}:{path}")
    if result.returncode != 0:
        raise AssertionError(f"baseline blob missing: {path}")
    return result.stdout


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_matrix(path):
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def indexed(rows):
    return {row["reviewId"]: row for row in rows}


def load_corpus():
    """The corpus Phase 4F-C1C adjudicated, read at the pinned baseline.

    C1C wrote nothing canonical, so at the time this suite was written the
    working tree and the baseline were the same document and reading either
    meant the same thing.  Phase 4F-C2 then implemented the specification C1C
    locked, and a live read would silently restate C1C's findings against a
    corpus C1C never saw.  Reading the immutable baseline keeps every claim
    below about the document that was actually adjudicated, before and after
    any successor phase.  The *current* corpus boundary is owned by the Phase
    4F-C2 suite, which measures it against this same commit.
    """
    return json.loads(git_blob("editorial/verb-pattern-candidates.json"))


def patterns_by_id(corpus):
    result = {}
    for lemma in corpus["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                result[pattern["id"]] = (lemma, meaning, pattern)
    return result


def all_patterns(corpus):
    return [pattern for _, _, pattern in patterns_by_id(corpus).values()]


def touched_since_baseline():
    """Paths this workspace changed relative to the pinned baseline commit.

    Folds the pinned-commit diff together with ``git status`` so the answer is
    the same whether the C1C candidate is sitting untracked in the real
    workspace or committed in a scratch rehearsal.  ``git diff`` cannot see
    untracked files; ``git status`` goes empty once they are committed.  Every
    guard that consumes this asserts it is non-empty first, so none of them can
    pass by having nothing to look at.
    """
    diff = git("diff", "--name-only", BASELINE_COMMIT)
    if diff.returncode != 0:
        raise AssertionError(diff.stderr)
    touched = {line for line in diff.stdout.split("\n") if line}
    status = git("status", "--porcelain", "-uall")
    if status.returncode != 0:
        raise AssertionError(status.stderr)
    for line in status.stdout.split("\n"):
        if line.strip():
            touched.add(line[3:].strip().strip('"'))
    return touched


# ---------------------------------------------------------------------------
# 1.  Reconstruction of the two source reviews
# ---------------------------------------------------------------------------

class SourceReviewReconstructionTests(unittest.TestCase):

    def setUp(self):
        self.c1 = read_matrix(C1_MATRIX)
        self.c1b = read_matrix(C1B_MATRIX)

    def test_c1_matrix_has_exactly_thirteen_rows(self):
        self.assertEqual(13, len(self.c1))

    def test_c1b_matrix_has_exactly_thirteen_rows(self):
        self.assertEqual(13, len(self.c1b))

    def test_both_matrices_carry_the_expected_review_queue(self):
        self.assertEqual(list(QUEUE), [row["reviewId"] for row in self.c1])
        self.assertEqual(list(QUEUE), [row["reviewId"] for row in self.c1b])

    def test_neither_matrix_duplicates_or_omits_a_review_id(self):
        for label, rows in (("C1", self.c1), ("C1B", self.c1b)):
            observed = [row["reviewId"] for row in rows]
            self.assertEqual(len(observed), len(set(observed)), label)
            self.assertEqual(set(QUEUE), set(observed), label)

    def test_both_matrices_name_the_same_canonical_pattern_ids(self):
        c1 = {row["reviewId"]: row["patternId"] for row in self.c1}
        c1b = {row["reviewId"]: row["patternId"] for row in self.c1b}
        self.assertEqual(c1, c1b)
        self.assertEqual(13, len(set(c1.values())))

    def test_both_matrices_name_the_same_meaning_ids(self):
        c1 = {row["reviewId"]: row["meaningId"] for row in self.c1}
        c1b = {row["reviewId"]: row["meaningId"] for row in self.c1b}
        self.assertEqual(c1, c1b)

    def test_every_named_pattern_resolves_in_the_corpus(self):
        index = patterns_by_id(load_corpus())
        for row in self.c1:
            self.assertIn(row["patternId"], index, row["reviewId"])

    def test_descriptors_agree_with_each_other(self):
        c1, c1b = indexed(self.c1), indexed(self.c1b)
        for review_id in QUEUE:
            for field in ("lemma", "meaningId", "patternId", "currentPolish",
                          "currentEnglish", "currentOrigin"):
                self.assertEqual(c1[review_id][field], c1b[review_id][field],
                                 f"{review_id}.{field}")

    def test_current_example_facts_agree_with_the_corpus(self):
        index = patterns_by_id(load_corpus())
        for row in self.c1:
            lemma, meaning, pattern = index[row["patternId"]]
            self.assertEqual(row["lemma"], lemma["canonicalLemma"],
                             row["reviewId"])
            self.assertEqual(row["meaningId"], meaning["id"], row["reviewId"])
            examples = pattern.get("examples", [])
            if row["currentExampleStatus"] == "PRESENT":
                self.assertEqual(1, len(examples), row["reviewId"])
                example = examples[0]
                self.assertEqual(row["currentPolish"], example["pl"],
                                 row["reviewId"])
                self.assertEqual(row["currentEnglish"], example["en"],
                                 row["reviewId"])
                self.assertEqual(row["currentOrigin"],
                                 example["origin"]["kind"], row["reviewId"])
            else:
                self.assertEqual("ABSENT", row["currentExampleStatus"],
                                 row["reviewId"])
                self.assertEqual([], examples, row["reviewId"])
                self.assertEqual("", row["currentPolish"], row["reviewId"])

    def test_the_blind_input_is_the_package_recorded_in_the_brief(self):
        self.assertEqual(BLIND_INPUT_SHA256, sha256(C1_BLIND_INPUT))

    def test_the_blind_input_covers_the_same_queue(self):
        rows = read_matrix(C1_BLIND_INPUT)
        self.assertEqual(13, len(rows))
        self.assertEqual(list(QUEUE), [row["rowId"] for row in rows])

    def test_the_blind_input_withheld_the_primary_verdicts(self):
        """The blindness claim, checked rather than taken on trust."""
        text = C1_BLIND_INPUT.read_text(encoding="utf-8")
        for token in ("MUST CHANGE", "USEFUL IMPROVEMENT", "NO CHANGE",
                      "MEDIUM", "HIGH", "P7-C1-"):
            self.assertNotIn(token, text, token)


# ---------------------------------------------------------------------------
# 2.  The copied review artifacts are inputs, and stay byte-identical
# ---------------------------------------------------------------------------

class SourceArtifactImmutabilityTests(unittest.TestCase):

    def test_every_copied_source_artifact_is_byte_identical(self):
        for relative, digest in SOURCE_ARTIFACT_SHA256.items():
            self.assertEqual(digest, sha256(ROOT / relative), relative)

    def test_the_hash_guard_would_notice_a_changed_byte(self):
        """Negative control: the digests are not trivially satisfiable."""
        for relative, digest in SOURCE_ARTIFACT_SHA256.items():
            mutated = (ROOT / relative).read_bytes() + b"\n"
            self.assertNotEqual(digest, hashlib.sha256(mutated).hexdigest(),
                                relative)

    def test_the_source_artifacts_are_untracked_inputs(self):
        """They arrived with the phase; the baseline commit does not hold them."""
        for relative in (*SOURCE_ARTIFACT_SHA256,
                         "reports/phase-4fc1/blind-review-input.csv"):
            self.assertNotEqual(
                0, git("cat-file", "-e", f"{BASELINE_COMMIT}:{relative}")
                .returncode, relative)


# ---------------------------------------------------------------------------
# 3.  The adjudication matrix reproduces both reviews exactly
# ---------------------------------------------------------------------------

class AdjudicationReproductionTests(unittest.TestCase):

    def setUp(self):
        self.rows = read_matrix(C1C_MATRIX)
        self.by_id = indexed(self.rows)
        self.c1 = indexed(read_matrix(C1_MATRIX))
        self.c1b = indexed(read_matrix(C1B_MATRIX))

    def test_adjudication_has_exactly_thirteen_rows(self):
        self.assertEqual(13, len(self.rows))
        self.assertEqual(list(QUEUE), [row["reviewId"] for row in self.rows])

    def test_required_columns_are_present(self):
        required = {
            "reviewId", "lemma", "meaningId", "patternId",
            "c1Classification", "c1Severity", "c1Proposal",
            "c1bClassification", "c1bSeverity", "c1bProposalDecision",
            "c1bAlternative", "comparisonClass",
            "finalClassification", "finalSeverity",
            "implementationDisposition", "implementationPriority",
            "finalPolish", "finalEnglish", "finalOrigin",
            "finalRepositorySource",
            "caseTransparency", "senseFit", "naturalness", "cefrFit",
            "provenanceResult", "adjudicationRationale",
        }
        self.assertLessEqual(required, set(self.rows[0]))

    def test_identity_columns_come_from_the_source_reviews(self):
        for review_id in QUEUE:
            row, c1 = self.by_id[review_id], self.c1[review_id]
            for field in ("lemma", "meaningId", "patternId"):
                self.assertEqual(c1[field], row[field], f"{review_id}.{field}")

    def test_c1_columns_reproduce_the_c1_matrix(self):
        for review_id in QUEUE:
            row, c1 = self.by_id[review_id], self.c1[review_id]
            self.assertEqual(c1["classification"], row["c1Classification"],
                             review_id)
            self.assertEqual(c1["findingSeverity"], row["c1Severity"],
                             review_id)
            if c1["proposedPolish"]:
                self.assertIn(c1["proposedPolish"], row["c1Proposal"],
                              review_id)
                self.assertIn(c1["proposedEnglish"], row["c1Proposal"],
                              review_id)
                self.assertIn(c1["proposedOrigin"], row["c1Proposal"],
                              review_id)
                if c1["proposedRepositorySource"]:
                    self.assertIn(c1["proposedRepositorySource"],
                                  row["c1Proposal"], review_id)
            else:
                self.assertEqual("NONE", row["c1Proposal"], review_id)

    def test_c1b_columns_reproduce_the_c1b_matrix(self):
        for review_id in QUEUE:
            row, c1b = self.by_id[review_id], self.c1b[review_id]
            self.assertEqual(c1b["currentClassification"],
                             row["c1bClassification"], review_id)
            self.assertEqual(c1b["severity"], row["c1bSeverity"], review_id)
            self.assertEqual(c1b["proposalDecision"],
                             row["c1bProposalDecision"], review_id)
            if c1b["alternativePolish"]:
                self.assertIn(c1b["alternativePolish"], row["c1bAlternative"],
                              review_id)
                self.assertIn(c1b["alternativeEnglish"], row["c1bAlternative"],
                              review_id)
            else:
                self.assertEqual("NONE", row["c1bAlternative"], review_id)

    def test_reproduced_values_are_drawn_from_the_source_vocabularies(self):
        for review_id in QUEUE:
            row = self.by_id[review_id]
            self.assertIn(row["c1Classification"], CLASSIFICATIONS, review_id)
            self.assertIn(row["c1Severity"], SEVERITIES, review_id)
            self.assertIn(row["c1bClassification"], CLASSIFICATIONS, review_id)
            self.assertIn(row["c1bSeverity"], SEVERITIES, review_id)

    def test_source_review_counts_are_the_ones_the_summaries_report(self):
        c1 = [row["classification"] for row in self.c1.values()]
        self.assertEqual(7, c1.count("MUST CHANGE"))
        self.assertEqual(5, c1.count("USEFUL IMPROVEMENT"))
        self.assertEqual(1, c1.count("NO CHANGE"))
        c1b = [row["currentClassification"] for row in self.c1b.values()]
        self.assertEqual(7, c1b.count("MUST CHANGE"))
        self.assertEqual(4, c1b.count("USEFUL IMPROVEMENT"))
        self.assertEqual(2, c1b.count("NO CHANGE"))
        severities = [row["severity"] for row in self.c1b.values()]
        self.assertEqual(1, severities.count("HIGH"))
        self.assertEqual("P7-NR-033",
                         next(rid for rid, row in self.c1b.items()
                              if row["severity"] == "HIGH"))

    def test_comparison_class_is_one_of_the_three(self):
        for review_id in QUEUE:
            self.assertIn(self.by_id[review_id]["comparisonClass"],
                          COMPARISONS, review_id)

    def test_rows_the_reviews_agreed_on_are_not_called_disagreements(self):
        """An EXACT AGREEMENT row must really agree on class and severity."""
        for review_id in QUEUE:
            row = self.by_id[review_id]
            if row["comparisonClass"] != "EXACT AGREEMENT":
                continue
            self.assertEqual(row["c1Classification"], row["c1bClassification"],
                             review_id)
            self.assertEqual(row["c1Severity"], row["c1bSeverity"], review_id)

    def test_comparison_counts(self):
        observed = {name: 0 for name in COMPARISONS}
        for row in self.rows:
            observed[row["comparisonClass"]] += 1
        self.assertEqual(EXPECTED_COMPARISONS, observed)


# ---------------------------------------------------------------------------
# 4.  The adjudicated result is complete and internally consistent
# ---------------------------------------------------------------------------

class AdjudicationCompletenessTests(unittest.TestCase):

    def setUp(self):
        self.rows = read_matrix(C1C_MATRIX)
        self.by_id = indexed(self.rows)

    def test_every_row_carries_exactly_one_disposition(self):
        for row in self.rows:
            disposition = row["implementationDisposition"]
            self.assertIn(disposition, DISPOSITIONS, row["reviewId"])
            self.assertEqual(1, sum(disposition == name
                                    for name in DISPOSITIONS),
                             row["reviewId"])

    def test_every_row_carries_a_final_classification_and_severity(self):
        for row in self.rows:
            self.assertIn(row["finalClassification"], CLASSIFICATIONS,
                          row["reviewId"])
            self.assertIn(row["finalSeverity"], SEVERITIES, row["reviewId"])

    def test_every_row_carries_an_implementation_priority(self):
        for row in self.rows:
            self.assertIn(row["implementationPriority"], PRIORITIES,
                          row["reviewId"])

    def test_no_change_rows_keep_the_current_example(self):
        for row in self.rows:
            if row["finalClassification"] == "NO CHANGE":
                self.assertEqual("KEEP CURRENT",
                                 row["implementationDisposition"],
                                 row["reviewId"])
                self.assertEqual("NONE", row["finalSeverity"], row["reviewId"])
                self.assertEqual("NOT APPLICABLE",
                                 row["implementationPriority"], row["reviewId"])

    def test_keep_current_rows_restate_the_current_example(self):
        for row in self.rows:
            if row["implementationDisposition"] != "KEEP CURRENT":
                continue
            self.assertEqual(row["currentPolish"], row["finalPolish"],
                             row["reviewId"])
            self.assertEqual(row["currentEnglish"], row["finalEnglish"],
                             row["reviewId"])
            self.assertEqual(row["currentOrigin"], row["finalOrigin"],
                             row["reviewId"])

    def test_no_row_is_left_open(self):
        """Section 4: NO IMPLEMENTATION YET must not be used as an escape."""
        for row in self.rows:
            self.assertNotEqual("NO IMPLEMENTATION YET",
                                row["implementationDisposition"],
                                row["reviewId"])

    def test_disposition_and_priority_counts(self):
        dispositions = {name: 0 for name in DISPOSITIONS}
        priorities = {name: 0 for name in PRIORITIES}
        classifications = {name: 0 for name in CLASSIFICATIONS}
        for row in self.rows:
            dispositions[row["implementationDisposition"]] += 1
            priorities[row["implementationPriority"]] += 1
            classifications[row["finalClassification"]] += 1
        self.assertEqual(EXPECTED_DISPOSITIONS, dispositions)
        self.assertEqual(EXPECTED_PRIORITIES, priorities)
        self.assertEqual(EXPECTED_CLASSIFICATIONS, classifications)

    def test_every_changed_row_has_a_complete_final_example_spec(self):
        for row in self.rows:
            if row["implementationDisposition"] not in NEEDS_SPEC:
                continue
            review_id = row["reviewId"]
            self.assertTrue(row["finalPolish"].strip(), review_id)
            self.assertTrue(row["finalEnglish"].strip(), review_id)
            self.assertIn(row["finalOrigin"], FINAL_ORIGINS, review_id)
            for field in ("caseTransparency", "senseFit", "naturalness",
                          "cefrFit", "provenanceResult",
                          "adjudicationRationale"):
                self.assertTrue(row[field].strip(), f"{review_id}.{field}")

    def test_every_final_polish_sentence_is_a_real_sentence(self):
        for row in self.rows:
            polish = row["finalPolish"]
            self.assertGreaterEqual(len(polish), 3, row["reviewId"])
            self.assertTrue(polish[-1] in ".?!", row["reviewId"])

    def test_a_changed_row_never_restates_the_current_example(self):
        for row in self.rows:
            if row["implementationDisposition"] != "REPLACE":
                continue
            self.assertNotEqual(row["currentPolish"], row["finalPolish"],
                                row["reviewId"])

    def test_create_rows_are_exactly_the_patterns_with_no_example(self):
        index = patterns_by_id(load_corpus())
        for row in self.rows:
            has_example = bool(index[row["patternId"]][2].get("examples"))
            if row["implementationDisposition"] == "CREATE":
                self.assertFalse(has_example, row["reviewId"])
            else:
                self.assertTrue(has_example, row["reviewId"])

    def test_no_two_rows_propose_the_same_sentence(self):
        finals = [row["finalPolish"] for row in self.rows]
        self.assertEqual(len(finals), len(set(finals)))

    def test_the_two_pytac_rows_do_not_collapse_into_one_pattern(self):
        """Section 13: 031 and 032 must stay pedagogically distinct.

        The verb and the preposition are shared *by design* -- both patterns
        are pytać + o + Accusative, and that is the point of the pair.  What
        must not be shared is the lexical content, so that the short frame and
        the full frame cannot read as accidental duplicates of each other.
        """
        shared_by_design = {"pytam", "o"}

        def content(sentence):
            words = sentence.lower().rstrip(".?!").split()
            return set(words) - shared_by_design

        short = self.by_id["P7-NR-031"]["finalPolish"]
        full = self.by_id["P7-NR-032"]["finalPolish"]
        self.assertNotEqual(short, full)
        self.assertTrue(content(short) and content(full))
        self.assertEqual(set(), content(short) & content(full))
        # The full frame really does add a second Accusative participant.
        self.assertGreater(len(content(full)), len(content(short)))


# ---------------------------------------------------------------------------
# 5.  Provenance of every final example
# ---------------------------------------------------------------------------

class FinalProvenanceTests(unittest.TestCase):

    def setUp(self):
        self.rows = read_matrix(C1C_MATRIX)
        self.by_id = indexed(self.rows)

    def test_no_final_origin_claims_original_authorship(self):
        for row in self.rows:
            self.assertNotEqual("original", row["finalOrigin"],
                                row["reviewId"])
            self.assertIn(row["finalOrigin"], FINAL_ORIGINS, row["reviewId"])

    def test_generated_finals_use_editorial_generated_with_no_source(self):
        generated = [row for row in self.rows
                     if row["finalOrigin"] == "editorial-generated"]
        self.assertEqual(11, len(generated))
        for row in generated:
            self.assertEqual("", row["finalRepositorySource"].strip(),
                             row["reviewId"])

    def test_every_repository_reuse_final_source_resolves_byte_exactly(self):
        index = repository_index()
        self.assertEqual([], index.issues)
        reuse = [row for row in self.rows
                 if row["finalOrigin"] == "repository-reuse"]
        self.assertTrue(reuse, "the resolution guard must have subjects")
        for row in reuse:
            review_id = row["reviewId"]
            match = re.fullmatch(r"(card|drill):([a-z0-9-]+)\.(pl|ex|prompt|answer)",
                                 row["finalRepositorySource"])
            self.assertIsNotNone(match, review_id)
            kind, entity_id, field = match.groups()
            entity = index.get(entity_id)
            self.assertIsNotNone(entity, f"{review_id}: {entity_id}")
            self.assertEqual(kind, entity.kind, review_id)
            self.assertIn(field, entity.record, review_id)
            self.assertEqual(row["finalPolish"], entity.record[field],
                             review_id)

    def test_the_declared_keep_current_sources_are_the_corpus_ones(self):
        index = patterns_by_id(load_corpus())
        for review_id, (kind, entity_id, field) in KEEP_CURRENT_SOURCES.items():
            row = self.by_id[review_id]
            self.assertEqual(f"{kind}:{entity_id}.{field}",
                             row["finalRepositorySource"], review_id)
            example = index[row["patternId"]][2]["examples"][0]
            source = example["origin"]["repositorySource"]
            self.assertEqual({"kind": kind, "id": entity_id, "field": field},
                             source, review_id)

    def test_the_resolution_guard_rejects_a_wrong_source(self):
        """Negative control: byte-exactness is not trivially satisfied."""
        index = repository_index()
        entity = index.get("a2-official-matters-019")
        self.assertNotEqual("Czy potrzebuję antybiotyku?", entity.record["ex"])
        self.assertIsNone(index.get("a2-official-matters-999"))

    def test_no_generated_final_exists_verbatim_in_the_repository(self):
        index = repository_index()
        strings = []
        for entity in index.entities.values():
            stack = [entity.record]
            while stack:
                item = stack.pop()
                if isinstance(item, str):
                    strings.append(item)
                elif isinstance(item, list):
                    stack.extend(item)
                elif isinstance(item, dict):
                    stack.extend(item.values())
        self.assertGreater(len(strings), 20000)
        for row in self.rows:
            if row["finalOrigin"] != "editorial-generated":
                continue
            polish = row["finalPolish"]
            for value in strings:
                self.assertNotIn(polish, value,
                                 f"{row['reviewId']} occurs in the repository")

    def test_no_generated_final_exists_verbatim_in_the_canonical_corpus(self):
        # Against the corpus C1C generated them for: none of the eleven
        # duplicated shipped canonical content at the time it was adjudicated.
        text = git_blob("editorial/verb-pattern-candidates.json")
        for row in self.rows:
            if row["finalOrigin"] != "editorial-generated":
                continue
            self.assertNotIn(json.dumps(row["finalPolish"], ensure_ascii=False)[1:-1],
                             text, row["reviewId"])

    def test_the_editorial_generated_rows_still_need_an_actor_c1c_did_not_add(self):
        """Truthfulness of the recorded governance prerequisite.

        Stated over the baseline C1C closed against: the eleven generated
        rows really did require an example-generation actor that did not yet
        exist, and C1C correctly registered none.  Registering it is Phase
        4F-C2's step, so a live read would deny the prerequisite it records.
        """
        context = json.loads(
            git_blob("editorial/priority-7-authoring-context.json"))
        registry = context["editorialActorRegistry"]
        self.assertEqual(["priority7-reference-analysis"], list(registry))
        self.assertEqual(["reference-verification"],
                         registry["priority7-reference-analysis"]["roles"])
        self.assertEqual({}, context["authorRegistry"])


# ---------------------------------------------------------------------------
# 6.  ADD is unavailable, which is why no row uses it
# ---------------------------------------------------------------------------

class SingleExampleArchitectureTests(unittest.TestCase):
    """Section 9 turns on a product fact, so the fact is pinned here.

    If the runtime ever starts rendering more than the first example, this
    suite should fail and the ADD disposition should be reconsidered.
    """

    def test_the_view_model_projects_only_the_first_example(self):
        source = (ROOT / "pp-verb-patterns.js").read_text(encoding="utf-8")
        self.assertIn("pattern.examples[0].pl", source)
        self.assertIn("pattern.examples[0].en", source)

    def test_the_page_renders_a_single_example_object(self):
        source = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("pattern.example.pl", source)
        self.assertIn("pattern.example.en", source)

    def test_every_canonical_pattern_holds_at_most_one_example(self):
        for pattern in all_patterns(load_corpus()):
            self.assertLessEqual(len(pattern.get("examples", [])), 1,
                                 pattern["id"])

    def test_no_row_was_dispositioned_add(self):
        for row in read_matrix(C1C_MATRIX):
            self.assertNotEqual("ADD", row["implementationDisposition"],
                                row["reviewId"])


# ---------------------------------------------------------------------------
# 7.  Canonical, shipping and runtime boundary, against the pinned baseline
# ---------------------------------------------------------------------------

class CanonicalBoundaryTests(unittest.TestCase):

    def test_the_pinned_baseline_is_the_commit_and_tree_it_claims(self):
        self.assertEqual(
            BASELINE_TREE,
            git("rev-parse", f"{BASELINE_COMMIT}^{{tree}}").stdout.strip())

    def test_the_pinned_baseline_is_the_commit_c1c_adjudicated(self):
        """The anchor every claim above rests on, checked directly."""
        self.assertEqual(
            BASELINE_TREE,
            git("rev-parse", f"{BASELINE_COMMIT}^{{tree}}").stdout.strip())
        self.assertEqual(PATTERN_COUNT, len(all_patterns(load_corpus())))

    def test_the_adjudication_baseline_registered_no_example_author(self):
        """What C1C adjudicated against: no author, one tier-1 actor only."""
        document = json.loads(
            git_blob("editorial/priority-7-authoring-context.json"))
        self.assertEqual({}, document["authorRegistry"])
        self.assertEqual({"priority7-reference-analysis"},
                         set(document["editorialActorRegistry"]))
        self.assertEqual(
            ["reference-verification"],
            document["editorialActorRegistry"]
            ["priority7-reference-analysis"]["roles"])

    def test_pattern_count_is_unchanged(self):
        self.assertEqual(PATTERN_COUNT, len(all_patterns(load_corpus())))

    def test_every_pattern_is_still_reference_verified(self):
        states = [pattern["reviewState"] for pattern in all_patterns(load_corpus())]
        self.assertEqual(REFERENCE_VERIFIED_COUNT,
                         states.count("reference-verified"))
        self.assertEqual(PATTERN_COUNT, len(states))

    def test_reference_verification_accept_count_is_unchanged(self):
        accepts = 0
        for pattern in all_patterns(load_corpus()):
            for event in pattern.get("reviewEvents", []):
                if (event["kind"] == "reference-verification" and
                        event["decision"] == "accept"):
                    accepts += 1
        self.assertEqual(REFERENCE_ACCEPT_COUNT, accepts)

    def test_no_editorial_review_or_product_approval_event_exists(self):
        for pattern in all_patterns(load_corpus()):
            for event in pattern.get("reviewEvents", []):
                self.assertNotIn(event["kind"],
                                 {"editorial-review", "product-approval"},
                                 pattern["id"])

    def test_the_adjudication_baseline_holds_the_23_examples_reviewed(self):
        """C1C adjudicated 23 canonical examples and wrote none of its own."""
        baseline = patterns_by_id(
            json.loads(git_blob("editorial/verb-pattern-candidates.json")))
        self.assertEqual(PATTERN_COUNT, len(baseline))
        total = sum(len(pattern.get("examples", []))
                    for _, _, pattern in baseline.values())
        self.assertEqual(CANONICAL_EXAMPLE_COUNT, total)

    def test_every_adjudicated_example_was_repository_reuse(self):
        for pattern in all_patterns(load_corpus()):
            for example in pattern.get("examples", []):
                self.assertEqual("repository-reuse",
                                 example["origin"]["kind"], example["id"])

    def test_no_shipping_or_runtime_file_moved(self):
        """Compared with the Phase 4F-I1 and 4F-H3 layers removed.

        Two phases have been entitled to change a shipping file since this
        baseline: H3, the UI wording phase, and I1, the atomic release.  Both
        layers are pinned and all-or-nothing, so removing them must reproduce
        these bytes exactly and every other shell or worker edit still fails
        here.  I1 is stripped first because it sits on top of H3.
        """
        for relative in SHIPPING_SENTINELS:
            text = i1_shipping_text(relative)
            if H3.is_phase_4fh3_path(relative):
                text = H3.without_phase_4fh3_ui_wording(text)
            self.assertEqual(git_blob(relative), text, relative)

    def test_no_runtime_pattern_payload_was_created(self):
        # Superseded by Priority 7 Phase 4F-I1, the release that materialised
        # the official runtime.  The only document that may occupy that path
        # is exactly the I1 release artifact, pinned by digest and revision,
        # and it may only exist alongside the matching shell and worker.
        self.assertEqual("complete", i1_bundle().state)

    def test_the_c1c_footprint_is_reports_and_tests_only(self):
        """C1C's own three files, and nothing canonical or shipping among them.

        Scoped to the artifacts C1C added rather than to everything the
        workspace has touched since the baseline.  A successor phase entitled
        to write canonical data -- Phase 4F-C2 is exactly that -- must not be
        forbidden by a closed guard belonging to a phase that closed before
        it; the current boundary is owned by the successor's own suite.  That
        is the Phase 4F-C1.1 lesson applied one level further.
        """
        touched = touched_since_baseline()
        self.assertTrue(touched, "the footprint guard must have evidence")
        for path in C1C_ARTIFACTS:
            with self.subTest(path=path):
                self.assertTrue(path.startswith(C1C_FOOTPRINT_PREFIXES), path)
                self.assertFalse(path.startswith("editorial/"), path)
                for sentinel in SHIPPING_SENTINELS:
                    self.assertNotEqual(sentinel, path)

    def test_the_c1c_artifacts_are_in_the_footprint(self):
        """Non-vacuity: the guards above are looking at something real."""
        touched = touched_since_baseline()
        for relative in C1C_ARTIFACTS:
            self.assertIn(relative, touched, relative)


# ---------------------------------------------------------------------------
# 8.  The Phase 4F-C1.1 historical guard is preserved, not widened
# ---------------------------------------------------------------------------

class HistoricalB3BGuardTests(unittest.TestCase):
    """Section 26.  Asserted from outside the edited module."""

    def setUp(self):
        import test_priority7_phase4fb3b as B3B
        self.module = B3B

    def test_the_b3b_guard_still_tests_the_immutable_transition(self):
        self.assertEqual("7beb50d7b3463d7745352f1608f1e30019529fdf",
                         self.module.BASELINE_COMMIT)
        self.assertEqual(BASELINE_COMMIT, self.module.B3B_CHECKPOINT)

    def test_the_checkpoint_is_the_child_of_the_b3b_baseline(self):
        parents = git("rev-list", "--parents", "-n", "1",
                      BASELINE_COMMIT).stdout.split()
        self.assertEqual([BASELINE_COMMIT, self.module.BASELINE_COMMIT],
                         parents)

    def test_the_b3b_footprint_was_not_widened_for_c1c(self):
        footprint = self.module.B3B_FOOTPRINT
        self.assertEqual(11, len(footprint))
        for relative in C1C_ARTIFACTS + (
                "reports/phase-4fc1/example-matrix.csv",
                "reports/phase-4fc1b/example-review-matrix.csv"):
            self.assertNotIn(relative, footprint, relative)

    def test_the_historical_transition_still_resolves_to_the_footprint(self):
        self.assertEqual(
            self.module.B3B_FOOTPRINT,
            self.module.transition_footprint(
                ROOT, self.module.BASELINE_COMMIT, self.module.B3B_CHECKPOINT))

    def test_later_phase_files_do_not_enter_the_historical_answer(self):
        """C1C's own files exist now and must leave B3B's history unmoved."""
        observed = self.module.transition_footprint(
            ROOT, self.module.BASELINE_COMMIT, self.module.B3B_CHECKPOINT)
        for path in observed:
            self.assertNotIn("4fc1c", path)


# ---------------------------------------------------------------------------
# 9.  The summary agrees with the matrix
# ---------------------------------------------------------------------------

class SummaryConsistencyTests(unittest.TestCase):

    def setUp(self):
        self.rows = read_matrix(C1C_MATRIX)
        self.text = C1C_SUMMARY.read_text(encoding="utf-8")

    def test_the_summary_states_the_go_verdict(self):
        self.assertIn("**Verdict: GO**", self.text)

    def test_every_final_sentence_appears_in_the_summary(self):
        for row in self.rows:
            self.assertIn(row["finalPolish"], self.text, row["reviewId"])
            self.assertIn(row["finalEnglish"], self.text, row["reviewId"])

    def test_the_summary_adjudicates_the_four_named_rows(self):
        for token in ("P7-NR-012", "P7-NR-018", "P7-NR-033", "P7-NR-044"):
            self.assertIn(token, self.text, token)

    def test_the_summary_pins_the_baseline_commit(self):
        self.assertIn(BASELINE_COMMIT, self.text)

    def test_the_summary_records_no_open_owner_decision(self):
        self.assertIn("**None.**", self.text)
        for row in self.rows:
            self.assertNotEqual("NO IMPLEMENTATION YET",
                                row["implementationDisposition"])


if __name__ == "__main__":
    unittest.main()
