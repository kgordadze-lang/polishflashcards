"""Priority 7 Phase 4F-C2 — implementing the adjudicated canonical examples.

Phase 4F-C1 assessed the 13-row example queue, Phase 4F-C1B reviewed it blind,
and Phase 4F-C1C adjudicated the two into one locked result per row.  This
phase implements that result and nothing else.

**The effective specification is C1C's adjudication plus the Phase 4F-C2C
two-row provenance override.**  C2C found that the C1C wording of exactly
P7-NR-033 and P7-NR-043 collided verbatim with pre-existing language-teaching
material and replaced those two sentences before release.  C1C's artifacts are
historical and were not rewritten, so the supersession is declared here in
``PHASE_4FC2C_WORDING_OVERRIDE``: a closed two-row literal that moves ``pl``
and ``en`` only.  Every other row, and every non-wording field of these two,
is still compared against the C1C matrix byte for byte.

What the suite proves:

1.  **The plan.**  The locked matrix still carries exactly 13 rows over the 13
    queue patterns with the adjudicated disposition split, read from the
    matrix rather than restated here.
2.  **The anchor.**  Every ``current*`` column of that matrix reproduces the
    *immutable baseline commit* byte for byte.  Everything below compares the
    implementation against the matrix, so without this the matrix and the
    corpus could be edited together and agree with each other about a corpus
    nobody adjudicated.
3.  **The implementation.**  Two rows keep their baseline example object byte
    for byte; five carry the adjudicated wording under an unchanged durable
    key and ID; six gained exactly one new example.  Four of the eleven final
    sentences are additionally checked against the Phase 4C summary as
    committed at the baseline, which records the text AB accepted.
4.  **Provenance.**  One nonhuman example-generation actor, ``human: false``,
    holding that role and nothing else; every generated example naming it; no
    ``original`` origin anywhere; an empty ``authorRegistry``; and both
    surviving repository-reuse sources still resolving byte-exactly.
5.  **Identity.**  29 example IDs, every one recomputing from its owning
    pattern and durable key through ``allocate_example_id``, no duplicate, no
    retired ID and no ID reused.
6.  **Governance.**  Examples sit above tier 1, so all 45 patterns are still
    ``reference-verified`` by the tooling's own derivation, the 47 reference
    acceptances are untouched, and nothing advanced to tier 2 or tier 3.
7.  **Boundary.**  Measured against the pinned baseline commit, the only
    canonical change is the example work plus the provenance and actor
    metadata it requires.

Every mutation below is applied to an in-memory copy.  Nothing here writes to
the corpus, the context, the tooling or any shipping file.
"""

from __future__ import annotations

import collections
import copy
import csv
import json
import subprocess
import sys
import unittest
from datetime import date
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
import priority7_phase4fh3_normalizer as H3  # noqa: E402

from priority7_tooling import (  # noqa: E402
    SOLO_MAINTAINER_MODE,
    ValidationContext,
    validate_editorial,
    validate_runtime,
)

CORPUS = ROOT / "editorial" / "verb-pattern-candidates.json"
CONTEXT_FILE = ROOT / "editorial" / "priority-7-authoring-context.json"
C1C_MATRIX = ROOT / "reports" / "phase-4fc1c" / "adjudication-matrix.csv"
C1C_SUMMARY = ROOT / "reports" / "phase-4fc1c" / "summary.md"
C2_SUMMARY = ROOT / "reports" / "priority-7-phase-4fc2-summary.md"
C2C_SUMMARY = ROOT / "reports" / "priority-7-phase-4fc2c-summary.md"

#: The commit Phase 4F-B3B produced.  Phase 4F-C1, 4F-C1B, 4F-C1C and this
#: phase all take it as their immutable baseline.  Pinned by SHA and never
#: resolved as ``HEAD``: once the C2 candidate is itself committed, ``HEAD``
#: contains it and a HEAD-anchored guard compares the corpus with itself.
BASELINE_COMMIT = "080d92ad49a514332f21ecd90b4a11de070a243f"
BASELINE_TREE = "74dd8cbebc303b646e4e38e2082d25c91b1cf6e1"

#: The Phase 4C summary as committed at the baseline.  It records the five
#: sentences AB accepted as presented, so four of the eleven final sentences
#: can be checked against a source that is neither the C1C matrix nor the
#: corpus this phase wrote.
PHASE_4C_SUMMARY_PATH = "reports/priority-7-phase-4c-summary.md"

QUEUE = (
    "P7-NR-007", "P7-NR-011", "P7-NR-012", "P7-NR-014", "P7-NR-018",
    "P7-NR-031", "P7-NR-032", "P7-NR-033", "P7-NR-035", "P7-NR-036",
    "P7-NR-042", "P7-NR-043", "P7-NR-044",
)

EXPECTED_DISPOSITIONS = {"KEEP CURRENT": 2, "REPLACE": 5, "CREATE": 6,
                         "ADD": 0, "NO IMPLEMENTATION YET": 0}

PATTERN_COUNT = 45
REFERENCE_VERIFIED_COUNT = 45
REFERENCE_ACCEPT_COUNT = 47
BASELINE_EXAMPLE_COUNT = 23
EXAMPLE_COUNT = 29
REPOSITORY_REUSE_COUNT = 18
EDITORIAL_GENERATED_COUNT = 11

GENERATION_ACTOR = "priority7-example-generation"
REFERENCE_ACTOR = "priority7-reference-analysis"
ADOPTED_AT = "2026-08-16"

#: The example sense Phase 4F-C1C rejected on P7-NR-033, and the longer
#: Phase 4C candidate it also declined.  Neither may come back.
WIDZIEC_PATTERN = (
    "vp-p-widziec-perceive-visually-accusative-object-80b697e51432")
REJECTED_WIDZIEC = "Widziałam wczoraj twoją siostrę."
REJECTED_WIDZIEC_LONG = "Czy widzisz tę górę na horyzoncie?"
#: The two-sentence repository-reuse candidate C1C rejected on P7-NR-044.
REJECTED_ZALEZEC = "Czy pójdziemy na spacer? To zależy od pogody."

#: The effective implementation specification is *C1C's adjudication plus the
#: Phase 4F-C2C two-row provenance override*, and nothing else.  C2C found
#: that the C1C wording of exactly these two rows collided verbatim with
#: pre-existing language-teaching material and replaced the sentences before
#: release.  C1C's own artifacts are historical and were not rewritten, so
#: the supersession lives here, as a closed literal keyed by review ID.
#:
#: Only ``pl`` and ``en`` move.  The durable key, the deterministic ID,
#: ``audioEligible``, ``origin.kind``, ``generatorRef`` and ``adoptedAt`` are
#: exactly the C2 ones, and every other C1C row is still compared against the
#: matrix byte for byte.
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
OVERRIDDEN_ROWS = frozenset(PHASE_4FC2C_WORDING_OVERRIDE)


def effective_final(row):
    """The wording the corpus must hold for ``row``: C1C, then C2C.

    Refuses to fire unless the matrix still carries the exact C1C wording the
    override was written against, so an edit to the historical adjudication
    artifact cannot be absorbed silently.
    """
    override = PHASE_4FC2C_WORDING_OVERRIDE.get(row["reviewId"])
    if override is None:
        return row["finalPolish"], row["finalEnglish"]
    if (row["finalPolish"], row["finalEnglish"]) != (
            override["priorPl"], override["priorEn"]):
        raise AssertionError(
            "the Phase 4F-C2C override no longer supersedes the C1C wording "
            f"it was written against: {row['reviewId']}")
    return override["finalPl"], override["finalEn"]

#: Fields no row is entitled to move.  Section 13 of the brief.
FROZEN_PATTERN_FIELDS = (
    "key", "relationType", "complements", "cefr", "teachingStatus", "usage",
    "learnerExplanationEn", "activityEligibility", "evidence", "releaseMode",
    "reviewState", "reviewEvents", "contentRefs", "errorNotes",
)

SHIPPING_SENTINELS = (
    "index.html", "manifest.json", "sw.js", "priority7_tooling.py",
    "pp-verb-patterns.js", "build_pages.py", "validate_content.py",
    "data-a1.js", "data-a2.js", "data-b1.js", "data-grammar.js",
    "data-verbs.js", "audio-manifest.json",
)

#: The *current* C2 boundary, as prefixes.  Deliberately not a closed set of
#: file paths: a closed set is exactly the historical-footprint bug Phase
#: 4F-C1.1 had to repair, and it would forbid every file a later phase adds.
#: What C2 must not touch is stated positively instead -- shipping sentinels,
#: runtime payloads, and every canonical field outside the example work.
C2_FOOTPRINT_PREFIXES = ("editorial/", "reports/", "tests/")

#: Non-vacuity for the boundary guards: C2's own two artifacts.
C2_ARTIFACTS = (
    "reports/priority-7-phase-4fc2-summary.md",
    "tests/test_priority7_phase4fc2.py",
)

_REPOSITORY_INDEX = None


def repository_index():
    global _REPOSITORY_INDEX
    if _REPOSITORY_INDEX is None:
        _REPOSITORY_INDEX = T.repository_index_from_root(ROOT)
    return _REPOSITORY_INDEX


def git(*arguments):
    return subprocess.run(["git", *arguments], cwd=ROOT,
                          capture_output=True, text=True)


def git_blob(path):
    """Read a path as of the pinned baseline commit, never as of HEAD."""
    result = git("show", f"{BASELINE_COMMIT}:{path}")
    if result.returncode != 0:
        raise AssertionError(f"baseline blob missing: {path}")
    return result.stdout


def is_only_the_h3_ui_wording(path):
    """True for ``index.html`` when its only change is the Phase 4F-H3 layer.

    Phase 4F-H3 is the UI wording phase, and the first phase since ``f339efb``
    entitled to change a shipping file at all.  A path qualifies only when
    removing H3's six pinned strings reproduces this phase's baseline bytes
    exactly, so any other shell edit -- a version or cache bump, a loader
    activation, a change to the recognition-only guards -- any other path, and
    any partly applied layer are still reported exactly as before.
    """
    if not H3.is_phase_4fh3_path(path):
        return False
    baseline = git("show", f"{BASELINE_COMMIT}:{path}")
    if baseline.returncode != 0:
        return False
    # LAYERED by Priority 7 Phase 4F-I1, the same way the corpus claims are
    # layered through E1/F2/H2/H2.1: the shell now carries the I1 release layer
    # on top of the H3 wording layer, so the H3 classification is made over the
    # shell with the I1 layer removed.  Both layers are all-or-nothing and
    # neither hides anything the other could not, so an edit outside the two
    # pinned sets is still reported here exactly as before.
    return H3.is_exactly_the_h3_ui_wording(path, baseline.stdout, pre_i1(path))


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


def load_corpus():
    """The corpus as Phase 4F-C2 left it: later approved work reverted.

    Phase 4F-D3.1 corrected three editorial-tier strings on already
    reference-verified rows.  This suite's claims are about what C2
    delivered, so that approved work is reverted here rather than
    weakening any assertion below.

    Phase 4F-E1 later recorded the 45 tier-2 acceptances; that approved
    governance work is reverted first, on the same terms.
    """
    return without_phase_4fd31_corrections(
        E1.without_phase_4fe1_editorial_review(
            F2.without_phase_4ff2_product_approval(
                H2.without_phase_4fh2_content_completion(
                    H21.without_phase_4fh21_product_reapproval(live_corpus())))))


def live_corpus():
    """The corpus exactly as it stands, with no normalisation at all."""
    return json.loads(CORPUS.read_text(encoding="utf-8"))


def live_context_document():
    return json.loads(CONTEXT_FILE.read_text(encoding="utf-8"))


def load_context_document():
    return E1.without_phase_4fe1_actors(
        F2.without_phase_4ff2_reviewer(
            H2.without_phase_4fh2_context(
                H21.without_phase_4fh21_context(live_context_document()))))


def baseline_corpus():
    return json.loads(git_blob("editorial/verb-pattern-candidates.json"))


def build_context(document=None, *, today=None):
    document = document or load_context_document()
    return ValidationContext(
        source_registry=document["sourceRegistry"],
        reviewer_registry=document["reviewerRegistry"],
        author_registry=document["authorRegistry"],
        allocation_registry=document["allocationRegistry"],
        editorial_actor_registry=document["editorialActorRegistry"],
        repository_index=repository_index(),
        today=date.fromisoformat(today or ADOPTED_AT),
    )


def read_matrix():
    with C1C_MATRIX.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def rows_by_id():
    return {row["reviewId"]: row for row in read_matrix()}


def iter_patterns(corpus):
    for lemma in corpus["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                yield lemma, meaning, pattern


def patterns_by_id(corpus):
    return {p["id"]: (l, m, p) for l, m, p in iter_patterns(corpus)}


def examples_of(pattern):
    return pattern.get("examples") or []


def all_examples(corpus):
    return [example for _, _, pattern in iter_patterns(corpus)
            for example in examples_of(pattern)]


def parse_source(locator):
    kind, rest = locator.split(":", 1)
    entity_id, field = rest.rsplit(".", 1)
    return {"kind": kind, "id": entity_id, "field": field}


def touched_since_baseline():
    """Paths this workspace changed relative to the pinned baseline commit.

    Folds the pinned-commit diff together with ``git status`` so the answer is
    the same whether the C2 candidate sits untracked in the real workspace or
    committed in a scratch rehearsal.  ``git diff`` cannot see untracked
    files; ``git status`` goes empty once they are committed.  ``-uall``
    expands untracked directories to their files so the answer is a set of
    paths in both modes.
    """
    diff = git("diff", "--name-only", BASELINE_COMMIT)
    if diff.returncode != 0:
        raise AssertionError(diff.stderr)
    touched = {line for line in diff.stdout.split("\n") if line}
    status = git("status", "--porcelain", "-uall")
    if status.returncode != 0:
        raise AssertionError(status.stderr)
    for line in status.stdout.split("\n"):
        if line:
            touched.add(line[3:].strip().strip('"'))
    return touched


class Phase4FC2TestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.corpus = load_corpus()
        cls.baseline = baseline_corpus()
        cls.document = load_context_document()
        cls.rows = read_matrix()
        cls.by_id = rows_by_id()
        cls.current = patterns_by_id(cls.corpus)
        cls.before = patterns_by_id(cls.baseline)

    def row_example(self, review_id):
        """The single canonical example on the row's pattern, now."""
        pattern = self.current[self.by_id[review_id]["patternId"]][2]
        examples = examples_of(pattern)
        self.assertEqual(1, len(examples), review_id)
        return examples[0]

    def baseline_examples(self, review_id):
        pattern = self.before[self.by_id[review_id]["patternId"]][2]
        return examples_of(pattern)


# ---------------------------------------------------------------------------
# 1.  The locked plan, read from the matrix
# ---------------------------------------------------------------------------

class LockedPlanTests(Phase4FC2TestCase):

    def test_the_matrix_is_the_thirteen_row_queue(self):
        self.assertEqual(13, len(self.rows))
        self.assertEqual(list(QUEUE), sorted(row["reviewId"]
                                             for row in self.rows))

    def test_the_disposition_split_is_the_adjudicated_one(self):
        counts = collections.Counter(
            row["implementationDisposition"] for row in self.rows)
        for disposition, expected in EXPECTED_DISPOSITIONS.items():
            with self.subTest(disposition=disposition):
                self.assertEqual(expected, counts.get(disposition, 0))

    def test_no_row_is_left_open(self):
        for row in self.rows:
            with self.subTest(review_id=row["reviewId"]):
                self.assertIn(row["implementationDisposition"],
                              {"KEEP CURRENT", "REPLACE", "CREATE"})

    def test_the_final_origin_split_is_two_reuse_and_eleven_generated(self):
        counts = collections.Counter(row["finalOrigin"] for row in self.rows)
        self.assertEqual({"repository-reuse": 2, "editorial-generated": 11},
                         dict(counts))

    def test_no_row_finalises_an_original_origin(self):
        for row in self.rows:
            with self.subTest(review_id=row["reviewId"]):
                self.assertNotEqual("original", row["finalOrigin"])

    def test_every_row_names_a_real_pattern(self):
        for row in self.rows:
            with self.subTest(review_id=row["reviewId"]):
                self.assertIn(row["patternId"], self.current)


# ---------------------------------------------------------------------------
# 2.  The anchor: the matrix describes the immutable baseline
# ---------------------------------------------------------------------------

class BaselineAnchorTests(Phase4FC2TestCase):
    """Everything else compares the corpus against the matrix.

    If the matrix were the only reference, an edit applied to both would agree
    with itself.  These tests tie the matrix's ``current*`` columns to the
    pinned baseline commit, which no phase can rewrite.
    """

    def test_the_pinned_baseline_is_the_commit_it_claims_to_be(self):
        self.assertEqual(
            BASELINE_TREE,
            git("rev-parse", f"{BASELINE_COMMIT}^{{tree}}").stdout.strip())

    def test_the_baseline_holds_45_patterns_and_23_reuse_examples(self):
        self.assertEqual(PATTERN_COUNT, len(self.before))
        examples = all_examples(self.baseline)
        self.assertEqual(BASELINE_EXAMPLE_COUNT, len(examples))
        self.assertEqual({"repository-reuse"},
                         {example["origin"]["kind"] for example in examples})

    def test_every_current_column_reproduces_the_baseline(self):
        for row in self.rows:
            with self.subTest(review_id=row["reviewId"]):
                examples = self.baseline_examples(row["reviewId"])
                if row["currentExampleStatus"] == "ABSENT":
                    self.assertEqual([], examples)
                    self.assertEqual("", row["currentPolish"])
                    self.assertEqual("", row["currentEnglish"])
                    self.assertEqual("", row["currentOrigin"])
                    self.assertEqual("", row["currentRepositorySource"])
                    continue
                self.assertEqual(1, len(examples))
                example = examples[0]
                self.assertEqual(row["currentPolish"], example["pl"])
                self.assertEqual(row["currentEnglish"], example["en"])
                self.assertEqual(row["currentOrigin"],
                                 example["origin"]["kind"])
                self.assertEqual(
                    parse_source(row["currentRepositorySource"]),
                    example["origin"]["repositorySource"])

    def test_the_lemma_and_meaning_columns_reproduce_the_baseline(self):
        for row in self.rows:
            with self.subTest(review_id=row["reviewId"]):
                lemma, meaning, _ = self.before[row["patternId"]]
                self.assertEqual(row["lemma"], lemma["canonicalLemma"])
                self.assertEqual(row["meaningId"], meaning["id"])

    def test_four_finals_match_the_sentences_ab_accepted_at_the_baseline(self):
        """An anchor outside both the matrix and the corpus.

        The Phase 4C summary, as committed at the baseline, records the five
        sentences AB accepted as presented.  Four of them are C1C's finals.
        """
        summary = git_blob(PHASE_4C_SUMMARY_PATH)
        for review_id in ("P7-NR-011", "P7-NR-012", "P7-NR-042", "P7-NR-044"):
            with self.subTest(review_id=review_id):
                self.assertNotIn(review_id, OVERRIDDEN_ROWS,
                                 "C2C did not touch the AB-accepted rows")
                final = self.by_id[review_id]["finalPolish"]
                self.assertIn(f"`{final}`", summary)
                self.assertEqual(final, self.row_example(review_id)["pl"])

    def test_the_widziec_row_departs_from_the_phase_4c_candidate(self):
        """P7-NR-033 is the row where C1C did not adopt AB's sentence."""
        summary = git_blob(PHASE_4C_SUMMARY_PATH)
        self.assertIn(f"`{REJECTED_WIDZIEC_LONG}`", summary)
        final = effective_final(self.by_id["P7-NR-033"])[0]
        self.assertNotEqual(REJECTED_WIDZIEC_LONG, final)
        self.assertNotIn(f"`{final}`", summary)


# ---------------------------------------------------------------------------
# 3.  KEEP CURRENT — 2 rows, byte-identical to the baseline
# ---------------------------------------------------------------------------

class KeepCurrentTests(Phase4FC2TestCase):

    def keep_rows(self):
        return [row for row in self.rows
                if row["implementationDisposition"] == "KEEP CURRENT"]

    def test_there_are_exactly_two(self):
        self.assertEqual(2, len(self.keep_rows()))

    def test_the_example_object_is_byte_identical_to_the_baseline(self):
        for row in self.keep_rows():
            with self.subTest(review_id=row["reviewId"]):
                self.assertEqual(self.baseline_examples(row["reviewId"]),
                                 examples_of(
                                     self.current[row["patternId"]][2]))

    def test_nothing_was_cleaned_up_on_a_kept_row(self):
        """No punctuation, translation, origin, source or ID was tidied."""
        for row in self.keep_rows():
            with self.subTest(review_id=row["reviewId"]):
                example = self.row_example(row["reviewId"])
                self.assertNotIn(row["reviewId"], OVERRIDDEN_ROWS,
                                 "C2C overrode no repository-reuse row")
                self.assertEqual(row["finalPolish"], example["pl"])
                self.assertEqual(row["finalEnglish"], example["en"])
                self.assertEqual(row["currentPolish"], example["pl"])
                self.assertEqual(row["currentEnglish"], example["en"])
                self.assertEqual("repository-reuse", example["origin"]["kind"])
                self.assertEqual(parse_source(row["finalRepositorySource"]),
                                 example["origin"]["repositorySource"])


# ---------------------------------------------------------------------------
# 4.  REPLACE — 5 rows, new wording under an unchanged identity
# ---------------------------------------------------------------------------

class ReplaceTests(Phase4FC2TestCase):

    def replace_rows(self):
        return [row for row in self.rows
                if row["implementationDisposition"] == "REPLACE"]

    def test_there_are_exactly_five(self):
        self.assertEqual(5, len(self.replace_rows()))

    def test_the_locked_final_wording_is_what_the_corpus_holds(self):
        for row in self.replace_rows():
            with self.subTest(review_id=row["reviewId"]):
                example = self.row_example(row["reviewId"])
                final_pl, final_en = effective_final(row)
                self.assertEqual(final_pl, example["pl"])
                self.assertEqual(final_en, example["en"])

    def test_the_baseline_wording_is_gone(self):
        for row in self.replace_rows():
            with self.subTest(review_id=row["reviewId"]):
                example = self.row_example(row["reviewId"])
                self.assertNotEqual(row["currentPolish"], example["pl"])
                self.assertNotEqual(row["currentEnglish"], example["en"])

    def test_the_durable_key_and_id_are_the_baseline_ones(self):
        """Stable-ID specification section 4: example wording keeps identity."""
        for row in self.replace_rows():
            with self.subTest(review_id=row["reviewId"]):
                before = self.baseline_examples(row["reviewId"])[0]
                after = self.row_example(row["reviewId"])
                self.assertEqual(before["key"], after["key"])
                self.assertEqual(before["id"], after["id"])
                self.assertEqual(before["audioEligible"],
                                 after["audioEligible"])

    def test_the_retained_id_still_recomputes_from_pattern_and_key(self):
        for row in self.replace_rows():
            with self.subTest(review_id=row["reviewId"]):
                example = self.row_example(row["reviewId"])
                self.assertEqual(
                    T.allocate_example_id(row["patternId"], example["key"]),
                    example["id"])

    def test_every_replacement_became_editorial_generated(self):
        for row in self.replace_rows():
            with self.subTest(review_id=row["reviewId"]):
                origin = self.row_example(row["reviewId"])["origin"]
                self.assertEqual("editorial-generated", origin["kind"])
                self.assertEqual(GENERATION_ACTOR, origin["generatorRef"])
                self.assertEqual(ADOPTED_AT, origin["adoptedAt"])
                self.assertNotIn("repositorySource", origin)
                self.assertEqual("", row["finalRepositorySource"])


# ---------------------------------------------------------------------------
# 5.  CREATE — 6 rows, a first example each
# ---------------------------------------------------------------------------

class CreateTests(Phase4FC2TestCase):

    def create_rows(self):
        return [row for row in self.rows
                if row["implementationDisposition"] == "CREATE"]

    def test_there_are_exactly_six(self):
        self.assertEqual(6, len(self.create_rows()))

    def test_each_created_row_had_no_baseline_example(self):
        for row in self.create_rows():
            with self.subTest(review_id=row["reviewId"]):
                self.assertEqual([], self.baseline_examples(row["reviewId"]))
                self.assertNotIn(
                    "examples", self.before[row["patternId"]][2],
                    "the baseline omits the key on an example-less pattern")

    def test_each_created_row_now_holds_exactly_the_locked_example(self):
        for row in self.create_rows():
            with self.subTest(review_id=row["reviewId"]):
                example = self.row_example(row["reviewId"])
                final_pl, final_en = effective_final(row)
                self.assertEqual(final_pl, example["pl"])
                self.assertEqual(final_en, example["en"])
                self.assertIs(False, example["audioEligible"])
                self.assertEqual(
                    {"kind": "editorial-generated",
                     "generatorRef": GENERATION_ACTOR,
                     "adoptedAt": ADOPTED_AT},
                    example["origin"])

    def test_each_new_id_is_deterministically_allocated(self):
        for row in self.create_rows():
            with self.subTest(review_id=row["reviewId"]):
                example = self.row_example(row["reviewId"])
                self.assertEqual(
                    T.allocate_example_id(row["patternId"], example["key"]),
                    example["id"])
                self.assertRegex(example["key"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

    def test_no_created_id_existed_at_the_baseline(self):
        baseline_ids = {example["id"]
                        for example in all_examples(self.baseline)}
        for row in self.create_rows():
            with self.subTest(review_id=row["reviewId"]):
                self.assertNotIn(self.row_example(row["reviewId"])["id"],
                                 baseline_ids)


# ---------------------------------------------------------------------------
# 6.  The four rows the brief singles out
# ---------------------------------------------------------------------------

class AdjudicatedRowTests(Phase4FC2TestCase):

    def test_widziec_keeps_the_visual_sense_and_drops_the_encounter_one(self):
        example = self.row_example("P7-NR-033")
        self.assertEqual(effective_final(self.by_id["P7-NR-033"])[0],
                         example["pl"])
        blob = CORPUS.read_text(encoding="utf-8")
        self.assertNotIn(REJECTED_WIDZIEC, blob)
        self.assertNotIn(REJECTED_WIDZIEC_LONG, blob)

    def test_widziec_shows_the_accusative_on_demonstrative_and_noun(self):
        """C2C changed the noun; the taught forms are still overt.

        ``tę`` is the standard written feminine Accusative demonstrative and
        ``czerwoną torbę`` carries the Accusative on adjective and noun, so
        the row still teaches what C1C adjudicated it to teach.
        """
        example = self.row_example("P7-NR-033")
        for form in ("tę", "czerwoną", "torbę"):
            with self.subTest(form=form):
                self.assertIn(form, example["pl"])

    def test_placic_no_longer_teaches_the_opaque_wszystko(self):
        example = self.row_example("P7-NR-012")
        self.assertNotIn("wszystko", example["pl"])
        self.assertEqual(self.by_id["P7-NR-012"]["finalPolish"], example["pl"])

    def test_dbac_replaced_its_example_and_did_not_gain_a_second(self):
        row = self.by_id["P7-NR-018"]
        self.assertEqual("REPLACE", row["implementationDisposition"])
        pattern = self.current[row["patternId"]][2]
        self.assertEqual(1, len(examples_of(pattern)))

    def test_znalezc_no_longer_hides_the_verb_under_udalo_mi_sie(self):
        example = self.row_example("P7-NR-036")
        self.assertNotIn("udało mi się", example["pl"])
        self.assertNotIn("mieszkanie", example["pl"])
        self.assertEqual(self.by_id["P7-NR-036"]["finalPolish"], example["pl"])

    def test_zalezec_is_a_single_sentence_not_the_rejected_pair(self):
        example = self.row_example("P7-NR-044")
        self.assertNotIn(REJECTED_ZALEZEC, CORPUS.read_text(encoding="utf-8"))
        self.assertEqual(1, example["pl"].count("."))
        self.assertNotIn("?", example["pl"])

    def test_no_final_example_is_more_than_one_sentence(self):
        for example in all_examples(self.corpus):
            with self.subTest(example_id=example["id"]):
                terminators = sum(example["pl"].count(mark)
                                  for mark in (".", "?", "!"))
                self.assertEqual(1, terminators)
                self.assertTrue(example["pl"][-1] in ".?!")


# ---------------------------------------------------------------------------
# 7.  ADD is unavailable, so no slot gained a second example
# ---------------------------------------------------------------------------

class SingleExampleTests(Phase4FC2TestCase):

    def test_every_queue_pattern_ends_with_exactly_one_example(self):
        for row in self.rows:
            with self.subTest(review_id=row["reviewId"]):
                self.assertEqual(
                    1, len(examples_of(self.current[row["patternId"]][2])))

    def test_no_pattern_anywhere_carries_two_examples(self):
        for _, _, pattern in iter_patterns(self.corpus):
            with self.subTest(pattern_id=pattern["id"]):
                self.assertLessEqual(len(examples_of(pattern)), 1)

    def test_the_runtime_still_renders_only_the_first_example(self):
        """The product fact the ADD refusal rests on."""
        loader = (ROOT / "pp-verb-patterns.js").read_text(encoding="utf-8")
        self.assertIn("examples[0]", loader)


# ---------------------------------------------------------------------------
# 8.  Provenance
# ---------------------------------------------------------------------------

class ProvenanceTests(Phase4FC2TestCase):

    def actors(self):
        return self.document["editorialActorRegistry"]

    def test_the_generation_actor_is_registered_exactly_once(self):
        self.assertIn(GENERATION_ACTOR, self.actors())
        self.assertEqual(
            1, sum(1 for actor_id in self.actors()
                   if actor_id == GENERATION_ACTOR))
        self.assertEqual(1, CONTEXT_FILE.read_text(encoding="utf-8").count(
            f'"{GENERATION_ACTOR}":'))

    def test_the_generation_actor_is_nonhuman(self):
        self.assertIs(False, self.actors()[GENERATION_ACTOR]["human"])

    def test_its_role_set_is_minimal_and_schema_supported(self):
        roles = self.actors()[GENERATION_ACTOR]["roles"]
        self.assertEqual(["example-generation"], roles)
        for role in roles:
            self.assertIn(role, T.EDITORIAL_ACTOR_ROLES)
        self.assertNotIn("reference-verification", roles)
        self.assertNotIn("editorial-review", roles)

    def test_it_is_distinct_from_the_reference_actor(self):
        self.assertNotEqual(GENERATION_ACTOR, REFERENCE_ACTOR)
        self.assertIn(REFERENCE_ACTOR, self.actors())
        self.assertEqual(["reference-verification"],
                         self.actors()[REFERENCE_ACTOR]["roles"])

    def test_the_reference_actor_record_is_untouched(self):
        baseline = json.loads(
            git_blob("editorial/priority-7-authoring-context.json"))
        self.assertEqual(baseline["editorialActorRegistry"][REFERENCE_ACTOR],
                         self.actors()[REFERENCE_ACTOR])

    def test_no_actor_key_is_claimed_by_a_human_registry(self):
        for registry in ("reviewerRegistry", "authorRegistry"):
            with self.subTest(registry=registry):
                self.assertEqual(
                    set(), set(self.actors()) & set(self.document[registry]))

    def test_the_author_registry_is_still_empty(self):
        self.assertEqual({}, self.document["authorRegistry"])
        self.assertEqual({}, json.loads(git_blob(
            "editorial/priority-7-authoring-context.json"))["authorRegistry"])

    def test_no_ai_author_was_invented(self):
        blob = CONTEXT_FILE.read_text(encoding="utf-8")
        self.assertNotIn('"authorRegistry": {"', blob)
        self.assertNotIn("authorRef", CORPUS.read_text(encoding="utf-8"))
        self.assertNotIn("authoredAt", CORPUS.read_text(encoding="utf-8"))

    def test_ab_is_not_recorded_as_an_author_or_a_generator(self):
        reviewer = self.document["reviewerRegistry"]["native-reviewer-001"]
        self.assertEqual(["native-linguistic"], reviewer["roles"])
        self.assertNotIn("native-reviewer-001",
                         CORPUS.read_text(encoding="utf-8"))
        self.assertEqual(
            json.loads(git_blob(
                "editorial/priority-7-authoring-context.json"))
            ["reviewerRegistry"],
            self.document["reviewerRegistry"])

    def test_every_editorial_generated_example_names_the_generator(self):
        generated = [example for example in all_examples(self.corpus)
                     if example["origin"]["kind"] == "editorial-generated"]
        self.assertEqual(EDITORIAL_GENERATED_COUNT, len(generated))
        for example in generated:
            with self.subTest(example_id=example["id"]):
                self.assertEqual(GENERATION_ACTOR,
                                 example["origin"]["generatorRef"])
                self.assertEqual(ADOPTED_AT, example["origin"]["adoptedAt"])

    def test_no_generated_example_carries_a_repository_source(self):
        for example in all_examples(self.corpus):
            if example["origin"]["kind"] != "editorial-generated":
                continue
            with self.subTest(example_id=example["id"]):
                self.assertNotIn("repositorySource", example["origin"])
                self.assertNotIn("authorRef", example["origin"])
                self.assertNotIn("authoredAt", example["origin"])

    def test_no_example_claims_an_original_origin(self):
        kinds = {example["origin"]["kind"]
                 for example in all_examples(self.corpus)}
        self.assertEqual({"repository-reuse", "editorial-generated"}, kinds)
        self.assertNotIn('"original"', CORPUS.read_text(encoding="utf-8"))

    def test_the_origin_split_is_eighteen_reuse_and_eleven_generated(self):
        counts = collections.Counter(
            example["origin"]["kind"]
            for example in all_examples(self.corpus))
        self.assertEqual({"repository-reuse": REPOSITORY_REUSE_COUNT,
                          "editorial-generated": EDITORIAL_GENERATED_COUNT},
                         dict(counts))

    def test_every_surviving_repository_source_resolves_byte_exactly(self):
        index = repository_index()
        reuse = [example for example in all_examples(self.corpus)
                 if example["origin"]["kind"] == "repository-reuse"]
        self.assertEqual(REPOSITORY_REUSE_COUNT, len(reuse))
        for example in reuse:
            with self.subTest(example_id=example["id"]):
                source = example["origin"]["repositorySource"]
                entity = index.get(source["id"])
                self.assertIsNotNone(entity, source["id"])
                self.assertEqual(source["kind"], entity.kind)
                self.assertEqual(example["pl"], entity.record[source["field"]])

    def test_no_generated_sentence_duplicates_repository_or_corpus_text(self):
        """Section 12: nothing generated is quietly reused shipped content."""
        index = repository_index()

        def strings(value):
            if isinstance(value, str):
                yield value
            elif isinstance(value, dict):
                for item in value.values():
                    yield from strings(item)
            elif isinstance(value, list):
                for item in value:
                    yield from strings(item)

        repository = [text for entity in index.entities.values()
                      for text in strings(entity.record)]
        haystack = chr(10).join(repository)
        baseline_text = chr(10).join(strings(self.baseline))
        for example in all_examples(self.corpus):
            if example["origin"]["kind"] != "editorial-generated":
                continue
            for field in ("pl", "en"):
                with self.subTest(example_id=example["id"], field=field):
                    self.assertNotIn(example[field], haystack)
                    self.assertNotIn(example[field], baseline_text)

    def test_no_reference_source_text_was_quoted_into_the_corpus(self):
        blob = CORPUS.read_text(encoding="utf-8")
        for token in ("wsjp.pl/haslo", "Skladnia", "Składnia", "Medak",
                      "Mędak"):
            with self.subTest(token=token):
                for example in all_examples(self.corpus):
                    self.assertNotIn(token, example["pl"])
                    self.assertNotIn(token, example["en"])
        self.assertIn("wsjp", blob, "evidence locators are still recorded")


# ---------------------------------------------------------------------------
# 9.  Identity and allocation
# ---------------------------------------------------------------------------

class IdentityTests(Phase4FC2TestCase):

    def test_the_corpus_holds_twenty_nine_examples(self):
        self.assertEqual(EXAMPLE_COUNT, len(all_examples(self.corpus)))
        self.assertEqual(BASELINE_EXAMPLE_COUNT + 6,
                         len(all_examples(self.corpus)))

    def test_every_example_id_recomputes_from_its_pattern_and_key(self):
        for _, _, pattern in iter_patterns(self.corpus):
            for example in examples_of(pattern):
                with self.subTest(example_id=example["id"]):
                    self.assertEqual(
                        T.allocate_example_id(pattern["id"], example["key"]),
                        example["id"])

    def test_no_example_id_or_key_is_duplicated(self):
        ids = [example["id"] for example in all_examples(self.corpus)]
        self.assertEqual(len(ids), len(set(ids)))
        pairs = [(pattern["id"], example["key"])
                 for _, _, pattern in iter_patterns(self.corpus)
                 for example in examples_of(pattern)]
        self.assertEqual(len(pairs), len(set(pairs)))

    def test_no_baseline_example_id_was_retired_or_reused(self):
        before = {example["id"] for example in all_examples(self.baseline)}
        after = {example["id"] for example in all_examples(self.corpus)}
        self.assertEqual(BASELINE_EXAMPLE_COUNT, len(before))
        self.assertTrue(before <= after, "no baseline ID was retired")
        self.assertEqual(6, len(after - before))

    def test_patterns_outside_the_queue_keep_their_example_identity(self):
        queue = {row["patternId"] for row in self.rows}
        for pattern_id, (_, _, pattern) in self.current.items():
            if pattern_id in queue:
                continue
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(examples_of(self.before[pattern_id][2]),
                                 examples_of(pattern))

    def test_no_tombstone_or_allocation_record_was_needed(self):
        """The corpus has never been frozen, so no ID has been retired."""
        self.assertEqual({}, self.document["allocationRegistry"])
        self.assertNotIn("tombstone", CORPUS.read_text(encoding="utf-8"))
        self.assertNotIn("tombstone", CONTEXT_FILE.read_text(encoding="utf-8"))

    def test_a_hand_authored_id_would_be_refused(self):
        """Non-vacuity for the deterministic-ID guard."""
        corpus = copy.deepcopy(self.corpus)
        for _, _, pattern in iter_patterns(corpus):
            if pattern["id"] == self.by_id["P7-NR-044"]["patternId"]:
                pattern["examples"][0]["id"] = (
                    "vp-e-zalezec-depend-on-od-genitive-source-invented"
                    "-000000000000")
        codes = {issue.code
                 for issue in validate_editorial(corpus, build_context())}
        self.assertIn("ID_RECOMPUTATION", codes)


# ---------------------------------------------------------------------------
# 10.  Reference verification survives
# ---------------------------------------------------------------------------

class ReviewStateTests(Phase4FC2TestCase):

    def currency(self, corpus):
        table = {}
        for lemma, meaning, pattern in iter_patterns(corpus):
            mode = T.declared_release_mode(pattern)
            digests = {stage: T.review_scope_digest(stage, lemma, meaning,
                                                    pattern)
                       for stage in T.STAGE_KINDS}
            records = {T.evidence_digest(record): record
                       for record in pattern["evidence"]}
            diagnostics: list[tuple[str, str]] = []
            table[pattern["id"]] = T._derive_review_currency(
                pattern["reviewEvents"], mode, digests, set(records), records,
                diagnostics=diagnostics)
            self.assertEqual([], diagnostics, pattern["id"])
        return table

    def test_every_pattern_is_still_reference_verified(self):
        states = collections.Counter(
            pattern["reviewState"] for _, _, pattern in
            iter_patterns(self.corpus))
        self.assertEqual({"reference-verified": REFERENCE_VERIFIED_COUNT},
                         dict(states))

    def test_the_tooling_derives_that_state_rather_than_trusting_it(self):
        derived = collections.Counter(
            currency.state for currency in self.currency(self.corpus).values())
        self.assertEqual({"reference-verified": REFERENCE_VERIFIED_COUNT},
                         dict(derived))

    def test_the_derived_currency_is_identical_to_the_baseline(self):
        after = self.currency(self.corpus)
        before = self.currency(self.baseline)
        self.assertEqual(set(before), set(after))
        for pattern_id in before:
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(before[pattern_id], after[pattern_id])

    def test_no_pattern_fell_back_to_research(self):
        states = {pattern["reviewState"]
                  for _, _, pattern in iter_patterns(self.corpus)}
        self.assertNotIn("research", states)

    def test_the_forty_seven_reference_acceptances_are_unchanged(self):
        for pattern_id, (_, _, pattern) in self.current.items():
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(self.before[pattern_id][2]["reviewEvents"],
                                 pattern["reviewEvents"])
        accepts = sum(1 for _, _, pattern in iter_patterns(self.corpus)
                      for event in pattern["reviewEvents"]
                      if event["kind"] == "reference-verification"
                      and event["decision"] == "accept")
        self.assertEqual(REFERENCE_ACCEPT_COUNT, accepts)

    def test_no_new_review_event_of_any_kind_was_created(self):
        kinds = collections.Counter(
            event["kind"] for _, _, pattern in iter_patterns(self.corpus)
            for event in pattern["reviewEvents"])
        self.assertEqual({"reference-verification": REFERENCE_ACCEPT_COUNT},
                         dict(kinds))

    def test_no_editorial_review_or_product_approval_exists(self):
        # The Phase 4F-C2 candidate is scanned as a serialised document rather
        # than as raw file text, because Phase 4F-E1 legitimately introduced
        # the tier-2 tokens and Phase 4F-F2 the tier-3 ones.  The stages that
        # have still never been run are scanned from the live file below,
        # where none of them may appear.
        blob = json.dumps(load_corpus(), ensure_ascii=False)
        for token in ("editorial-review", "product-approval",
                      "external-verification", "native-linguistic",
                      "correction", "reopen", "editorial-reviewed",
                      "approved"):
            with self.subTest(token=token):
                self.assertNotIn(f'"{token}"', blob)
        # Phase 4F-H2 legitimately recorded owner-authorized ``correction``
        # events; its pinned transition is removed before the sweep so that a
        # correction no authorised phase wrote still shows up here.
        live = H2.without_phase_4fh2_corpus_text(
            H21.without_phase_4fh21_corpus_text(
                CORPUS.read_text(encoding="utf-8")))
        for token in ("external-verification", "native-linguistic",
                      "correction", "reopen"):
            with self.subTest(token=token, source="live"):
                self.assertNotIn(f'"{token}"', live)

    def test_every_pattern_still_declares_the_solo_mode(self):
        self.assertEqual({SOLO_MAINTAINER_MODE},
                         {pattern["releaseMode"] for _, _, pattern
                          in iter_patterns(self.corpus)})

    def test_tier_one_scope_digests_are_unchanged_on_all_forty_five(self):
        for pattern_id, (lemma, meaning, pattern) in self.current.items():
            base_lemma, base_meaning, base_pattern = self.before[pattern_id]
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(
                    T.review_scope_digest("reference-verification",
                                          base_lemma, base_meaning,
                                          base_pattern),
                    T.review_scope_digest("reference-verification", lemma,
                                          meaning, pattern))

    def test_every_recorded_event_digest_still_matches_its_live_scope(self):
        """No acceptance was left describing a scope that has since moved."""
        superseded = []
        for lemma, meaning, pattern in iter_patterns(self.corpus):
            for index, event in enumerate(pattern["reviewEvents"]):
                live = T.review_scope_digest(event["kind"], lemma, meaning,
                                             pattern)
                if live != event["scopeDigest"]:
                    superseded.append((pattern["id"], index))
        baseline_superseded = []
        for lemma, meaning, pattern in iter_patterns(self.baseline):
            for index, event in enumerate(pattern["reviewEvents"]):
                live = T.review_scope_digest(event["kind"], lemma, meaning,
                                             pattern)
                if live != event["scopeDigest"]:
                    baseline_superseded.append((pattern["id"], index))
        self.assertEqual(baseline_superseded, superseded,
                         "C2 neither created nor healed a superseded digest")

    def test_tier_two_scope_digests_moved_on_exactly_the_eleven_rows(self):
        expected = {row["patternId"] for row in self.rows
                    if row["implementationDisposition"] in {"REPLACE",
                                                            "CREATE"}}
        self.assertEqual(11, len(expected))
        moved = set()
        for pattern_id, (lemma, meaning, pattern) in self.current.items():
            base_lemma, base_meaning, base_pattern = self.before[pattern_id]
            if (T.review_scope_digest("editorial-review", base_lemma,
                                      base_meaning, base_pattern) !=
                    T.review_scope_digest("editorial-review", lemma, meaning,
                                          pattern)):
                moved.add(pattern_id)
        self.assertEqual(expected, moved)

    def test_no_editorial_history_could_be_made_stale(self):
        """There is none to invalidate, which is why C2 may move tier 2."""
        self.assertEqual(
            0, sum(1 for _, _, pattern in iter_patterns(self.baseline)
                   for event in pattern["reviewEvents"]
                   if event["kind"] in {"editorial-review", "native-linguistic",
                                        "product-approval"}))


# ---------------------------------------------------------------------------
# 11.  Canonical boundary against the pinned baseline
# ---------------------------------------------------------------------------

class CanonicalBoundaryTests(Phase4FC2TestCase):

    def test_the_pattern_inventory_is_unchanged(self):
        self.assertEqual(30, len(self.corpus["lemmas"]))
        self.assertEqual(
            34, sum(len(lemma["meanings"]) for lemma in self.corpus["lemmas"]))
        self.assertEqual(PATTERN_COUNT, len(self.current))
        self.assertEqual(set(self.before), set(self.current))

    def test_the_corpus_is_identical_to_the_baseline_outside_examples(self):
        def stripped(corpus):
            corpus = copy.deepcopy(corpus)
            for _, _, pattern in iter_patterns(corpus):
                pattern.pop("examples", None)
            return corpus

        self.assertEqual(stripped(self.baseline), stripped(self.corpus))

    def test_no_frozen_pattern_field_moved_on_any_row(self):
        for pattern_id, (_, _, pattern) in self.current.items():
            base = self.before[pattern_id][2]
            for field in FROZEN_PATTERN_FIELDS:
                with self.subTest(pattern_id=pattern_id, field=field):
                    self.assertEqual(base.get(field), pattern.get(field))

    def test_no_lemma_or_meaning_field_moved(self):
        for pattern_id, (lemma, meaning, _) in self.current.items():
            base_lemma, base_meaning, _ = self.before[pattern_id]
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(
                    {k: v for k, v in base_lemma.items() if k != "meanings"},
                    {k: v for k, v in lemma.items() if k != "meanings"})
                self.assertEqual(
                    {k: v for k, v in base_meaning.items() if k != "patterns"},
                    {k: v for k, v in meaning.items() if k != "patterns"})

    def test_the_error_notes_were_not_edited_to_match_the_new_examples(self):
        """Section 24 forbids it, and two rows deliberately pay that cost."""
        for pattern_id, (_, _, pattern) in self.current.items():
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(self.before[pattern_id][2].get("errorNotes"),
                                 pattern.get("errorNotes"))

    def test_no_activity_eligibility_or_audio_was_opened(self):
        self.assertEqual(
            0, sum(len(pattern["activityEligibility"])
                   for _, _, pattern in iter_patterns(self.corpus)))
        for example in all_examples(self.corpus):
            with self.subTest(example_id=example["id"]):
                self.assertIs(False, example["audioEligible"])

    def test_the_document_envelope_is_unchanged(self):
        self.assertEqual(["artifactStatus", "formatVersion", "lemmas"],
                         sorted(self.corpus))
        self.assertEqual("priority-7-editorial-nonproduction",
                         self.corpus["artifactStatus"])
        self.assertEqual(1, self.corpus["formatVersion"])

    def test_the_private_context_changed_only_where_it_had_to(self):
        baseline = json.loads(
            git_blob("editorial/priority-7-authoring-context.json"))
        current = self.document
        self.assertEqual(set(baseline), set(current))
        for field in ("contextStatus", "sourceRegistry", "reviewerRegistry",
                      "authorRegistry", "allocationRegistry"):
            with self.subTest(field=field):
                self.assertEqual(baseline[field], current[field])
        # Exactly one new actor, and the notice that describes the registries.
        self.assertEqual({GENERATION_ACTOR},
                         set(current["editorialActorRegistry"]) -
                         set(baseline["editorialActorRegistry"]))
        self.assertNotEqual(baseline["contextNotice"],
                            current["contextNotice"])

    def test_no_shipping_or_runtime_file_moved(self):
        """Compared with the Phase 4F-I1 and 4F-H3 layers removed.

        Two phases have been entitled to change a shipping file since this
        baseline: H3, the UI wording phase, and I1, the atomic release.  Both
        layers are pinned and all-or-nothing, so removing them must reproduce
        these bytes exactly and every other shell or worker edit still fails
        here.  I1 is stripped first because it sits on top of H3.
        """
        for relative in SHIPPING_SENTINELS:
            with self.subTest(relative=relative):
                text = i1_shipping_text(relative)
                if H3.is_phase_4fh3_path(relative):
                    text = H3.without_phase_4fh3_ui_wording(text)
                self.assertEqual(git_blob(relative), text)

    def test_no_runtime_pattern_payload_was_generated(self):
        # Superseded by Priority 7 Phase 4F-I1, the release that materialised
        # the official runtime.  The only document that may occupy that path
        # is exactly the I1 release artifact, pinned by digest and revision,
        # and it may only exist alongside the matching shell and worker.
        self.assertEqual("complete", i1_bundle().state)
        blob = CORPUS.read_text(encoding="utf-8")
        for token in ("releaseAuthorization", "patternDataRevision", "freeze"):
            with self.subTest(token=token):
                self.assertNotIn(token, blob)

    def test_the_locked_review_artifacts_were_not_edited(self):
        for relative in ("reports/phase-4fc1/example-matrix.csv",
                         "reports/phase-4fc1/summary.md",
                         "reports/phase-4fc1/blind-review-input.csv",
                         "reports/phase-4fc1b/example-review-matrix.csv",
                         "reports/phase-4fc1b/summary.md",
                         "reports/phase-4fc1c/adjudication-matrix.csv",
                         "reports/phase-4fc1c/summary.md"):
            with self.subTest(relative=relative):
                self.assertTrue((ROOT / relative).exists(), relative)

    def test_the_c2_footprint_stays_inside_its_prefixes(self):
        """The *current* boundary, not a checkpoint a later phase inherits.

        A prefix allowlist rather than a closed file set: once C2 is
        integrated, a successor phase adds files of its own, and a closed set
        here would forbid all of them.  That is the Phase 4F-C1.1 lesson.
        """
        touched = touched_since_baseline()
        self.assertTrue(touched, "the footprint guard must have evidence")
        for path in sorted(touched):
            if is_only_the_h3_ui_wording(path) or is_only_the_i1_activation(path):
                continue
            with self.subTest(path=path):
                self.assertTrue(path.startswith(C2_FOOTPRINT_PREFIXES), path)

    def test_only_the_two_editorial_files_changed(self):
        touched = {path for path in touched_since_baseline()
                   if path.startswith("editorial/")}
        self.assertEqual(
            {"editorial/verb-pattern-candidates.json",
             "editorial/priority-7-authoring-context.json"}, touched)

    def test_the_c2_artifacts_are_in_the_footprint(self):
        """Non-vacuity: the guards above are looking at something real."""
        touched = touched_since_baseline()
        for relative in C2_ARTIFACTS:
            with self.subTest(relative=relative):
                self.assertIn(relative, touched)

    def test_the_boundary_logic_is_commit_independent(self):
        """It reads a pinned SHA, so it means the same once C2 is HEAD.

        Checked behaviourally rather than by string matching: the baseline
        blob this suite compares against is the pinned commit's, and that is
        not the working tree, so no guard above can be a self-comparison.
        """
        self.assertRegex(BASELINE_COMMIT, r"^[0-9a-f]{40}$")
        self.assertEqual(
            BASELINE_TREE,
            git("rev-parse", f"{BASELINE_COMMIT}^{{tree}}").stdout.strip())
        self.assertNotEqual(
            git_blob("editorial/verb-pattern-candidates.json"),
            CORPUS.read_text(encoding="utf-8"),
            "the baseline side must not be the working tree")


# ---------------------------------------------------------------------------
# 12.  The tooling accepts the result
# ---------------------------------------------------------------------------

class ToolingTests(Phase4FC2TestCase):

    def test_the_real_validator_reports_no_issue(self):
        self.assertEqual([], validate_editorial(self.corpus, build_context()))

    def test_the_runtime_projection_still_refuses_to_emit_anything(self):
        """Section 16: no runtime is generated, and the tooling agrees.

        Nothing is approved, so the projector has nothing it may publish and
        fails closed.  The new examples did not make any pattern publishable.
        """
        with self.assertRaises(T.ValidationFailure) as caught:
            T.project_nonrelease_fixture(
                copy.deepcopy(self.corpus), 1, build_context())
        self.assertEqual(["PROJECTION_EMPTY"],
                         [issue.code for issue in caught.exception.issues])

    def test_every_example_validates_in_the_runtime_shape_it_would_take(self):
        """The projector's own example validator accepts all 29 of them."""
        checked = 0
        for _, _, pattern in iter_patterns(self.corpus):
            for example in examples_of(pattern):
                issues: list[T.Issue] = []
                T._validate_runtime_example(
                    {"id": example["id"], "pl": example["pl"],
                     "en": example["en"],
                     "audioEligible": example["audioEligible"]},
                    "$.example", issues)
                with self.subTest(example_id=example["id"]):
                    self.assertEqual([], issues)
                checked += 1
        self.assertEqual(EXAMPLE_COUNT, checked)

    def test_no_private_provenance_key_would_reach_the_runtime(self):
        """``origin`` is editorial-only and is not part of the public shape."""
        issues: list[T.Issue] = []
        T._validate_runtime_example(
            {"id": "vp-e-szukac-seek-genitive-target-looking-for-cafe"
                   "-efdccf7a5ba6",
             "pl": "Szukam dobrej kawiarni.", "en": "x y z",
             "audioEligible": False,
             "origin": {"kind": "editorial-generated"}},
            "$.example", issues)
        self.assertIn("SCHEMA_UNKNOWN_FIELD",
                      {issue.code for issue in issues})

    def test_dropping_the_generation_actor_fails_the_corpus(self):
        document = copy.deepcopy(self.document)
        document["editorialActorRegistry"].pop(GENERATION_ACTOR)
        codes = {issue.code for issue in
                 validate_editorial(self.corpus, build_context(document))}
        self.assertIn("EDITORIAL_ACTOR_REGISTRY_DANGLING", codes)

    def test_a_human_generation_actor_is_refused(self):
        document = copy.deepcopy(self.document)
        document["editorialActorRegistry"][GENERATION_ACTOR]["human"] = True
        codes = {issue.code for issue in
                 validate_editorial(self.corpus, build_context(document))}
        self.assertIn("EDITORIAL_ACTOR_NOT_NONHUMAN", codes)

    def test_an_actor_without_the_generation_role_is_refused(self):
        document = copy.deepcopy(self.document)
        document["editorialActorRegistry"][GENERATION_ACTOR]["roles"] = [
            "reference-verification"]
        codes = {issue.code for issue in
                 validate_editorial(self.corpus, build_context(document))}
        self.assertIn("EDITORIAL_ACTOR_ROLE", codes)

    def test_claiming_a_repository_source_for_a_generated_example_is_refused(
            self):
        corpus = copy.deepcopy(self.corpus)
        for _, _, pattern in iter_patterns(corpus):
            for example in examples_of(pattern):
                if example["origin"]["kind"] == "editorial-generated":
                    example["origin"]["repositorySource"] = {
                        "kind": "card", "id": "a1-first-verbs-020",
                        "field": "ex"}
                    break
            else:
                continue
            break
        codes = {issue.code for issue in
                 validate_editorial(corpus, build_context())}
        self.assertIn("ORIGIN_EDITORIAL_FIELD_FORBIDDEN", codes)

    def test_an_original_origin_still_needs_a_human_author(self):
        corpus = copy.deepcopy(self.corpus)
        pattern = None
        for _, _, candidate in iter_patterns(corpus):
            if candidate["id"] == self.by_id["P7-NR-031"]["patternId"]:
                pattern = candidate
        pattern["examples"][0]["origin"] = {
            "kind": "original", "authorRef": "someone",
            "authoredAt": ADOPTED_AT}
        codes = {issue.code for issue in
                 validate_editorial(corpus, build_context())}
        self.assertIn("AUTHOR_REGISTRY_DANGLING", codes)

    def test_a_broken_repository_source_is_still_caught(self):
        corpus = copy.deepcopy(self.corpus)
        for _, _, pattern in iter_patterns(corpus):
            for example in examples_of(pattern):
                if example["origin"]["kind"] == "repository-reuse":
                    example["pl"] = "Zupełnie inne zdanie."
                    codes = {issue.code for issue in
                             validate_editorial(corpus, build_context())}
                    self.assertIn("REPOSITORY_SOURCE_MISMATCH", codes)
                    return
        self.fail("no repository-reuse example found")


# ---------------------------------------------------------------------------
# 13.  The Phase 4F-C1.1 historical guard is preserved, not widened
# ---------------------------------------------------------------------------

class HistoricalB3BGuardTests(unittest.TestCase):
    """Section 24.  Asserted from outside the guarded module."""

    def setUp(self):
        sys.path.insert(0, str(ROOT / "tests"))
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

    def test_the_b3b_footprint_was_not_widened_for_c2(self):
        footprint = self.module.B3B_FOOTPRINT
        self.assertEqual(11, len(footprint))
        for relative in C2_ARTIFACTS:
            with self.subTest(relative=relative):
                self.assertNotIn(relative, footprint)

    def test_the_historical_transition_still_resolves_to_the_footprint(self):
        self.assertEqual(
            self.module.B3B_FOOTPRINT,
            self.module.transition_footprint(
                ROOT, self.module.BASELINE_COMMIT, self.module.B3B_CHECKPOINT))

    def test_c2_files_do_not_enter_the_historical_answer(self):
        observed = self.module.transition_footprint(
            ROOT, self.module.BASELINE_COMMIT, self.module.B3B_CHECKPOINT)
        for path in observed:
            with self.subTest(path=path):
                self.assertNotIn("4fc2", path)


# ---------------------------------------------------------------------------
# 14.  The summary agrees with what was implemented
# ---------------------------------------------------------------------------

class SummaryConsistencyTests(Phase4FC2TestCase):

    def setUp(self):
        self.text = C2_SUMMARY.read_text(encoding="utf-8")

    def test_the_summary_exists_and_states_its_verdict(self):
        self.assertIn("**Verdict: GO**", self.text)

    def test_every_final_sentence_appears_in_the_summary(self):
        """The C2 report is historical and records what C2 implemented.

        For the eleven rows C2C did not touch that is still the sentence in
        the corpus.  For the two it did, the C2 report keeps the superseded
        C1C wording — it is not retro-edited, exactly as the C1 and C1B
        reports were not — and the C2C report carries the replacement.
        """
        c2c = C2C_SUMMARY.read_text(encoding="utf-8")
        for row in self.rows:
            with self.subTest(review_id=row["reviewId"]):
                self.assertIn(row["finalPolish"], self.text)
                self.assertIn(row["finalEnglish"], self.text)
                if row["reviewId"] not in OVERRIDDEN_ROWS:
                    continue
                final_pl, final_en = effective_final(row)
                self.assertNotIn(final_pl, self.text)
                self.assertIn(final_pl, c2c)
                self.assertIn(final_en, c2c)

    def test_the_summary_pins_the_baseline_commit(self):
        self.assertIn(BASELINE_COMMIT, self.text)

    def test_the_summary_records_the_actor_and_the_counts(self):
        for token in (GENERATION_ACTOR, "example-generation",
                      str(EXAMPLE_COUNT), str(REFERENCE_ACCEPT_COUNT)):
            with self.subTest(token=token):
                self.assertIn(token, self.text)

    def test_the_summary_names_every_example_id_it_implemented(self):
        for row in self.rows:
            with self.subTest(review_id=row["reviewId"]):
                self.assertIn(self.row_example(row["reviewId"])["id"],
                              self.text)


if __name__ == "__main__":
    unittest.main()
