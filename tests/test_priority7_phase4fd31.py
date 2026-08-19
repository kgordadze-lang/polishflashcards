"""Priority 7 Phase 4F-D3.1 — targeted final editorial repair.

The locked D3 adjudication approved exactly three editorial-tier corrections
and overturned a fourth blocker.  This suite treats the delivered corpus as
read-only and proves, against the immutable baseline
``3d613def18e9edf8bcabd331d40b5b90df30a9da``:

1.  **Exactly three rows moved.**  ``P7-NR-018``, ``P7-NR-028`` and
    ``P7-NR-037`` carry the exact approved prior -> final values.
    ``P7-NR-011``, whose D2 blocker was overturned, is byte-identical to the
    baseline, and no other row or field moved anywhere in the corpus.
2.  **Each correction is exactly as narrow as it was authorised to be.**  018
    keeps its Polish, provenance, key and ID; 028 keeps its Polish,
    ``repositorySource``, key and ID; 037 changes only the positive-model
    substring, in exactly the two learner-facing fields that carried it.
3.  **028 is a repair towards its own source, not away from it.**  The
    repository source card is byte-identical to the baseline, and the
    canonical English now agrees with the English that card already carried.
4.  **The reference tier never moved.**  Tier-1 scope digests are baseline
    identical on all 45 patterns; the tier-2 editorial scope and the tier-3
    scope move on exactly the three corrected rows.  45 ``reference-verified``,
    47 reference acceptances, no editorial-review event, no product approval,
    and no fresh reference-verification event.
5.  **Nothing outside the corpus moved.**  Authoring context, tooling,
    shipping card corpus and runtime are baseline identical.
6.  **The boundary has teeth.**  A fourth unauthorized canonical wording
    change -- including one dressed as a fourth approved correction, and one
    applied to the three corrected rows themselves -- is rejected by these
    checks and survives every historical normalizer.

Every mutation below is applied to an in-memory copy or to a throwaway clone.
Nothing here writes to the corpus, the context, the tooling or any shipping
file.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import importlib
import json
import subprocess
import unittest
from pathlib import Path

import sys

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
# `python3 -m unittest`, a direct script run, and importlib loading.
import os.path as _e1_os_path  # noqa: E402
import sys as _e1_sys  # noqa: E402

_E1_DIR = _e1_os_path.dirname(_e1_os_path.abspath(__file__))
if _E1_DIR not in _e1_sys.path:
    _e1_sys.path.insert(0, _E1_DIR)

import priority7_phase4fe1_normalizer as E1  # noqa: E402
import priority7_phase4ff2_normalizer as F2  # noqa: E402
import priority7_phase4fh2_normalizer as H2  # noqa: E402
import priority7_phase4fh21_normalizer as H21  # noqa: E402
import priority7_phase4fh3_normalizer as H3  # noqa: E402
from priority7_tooling import validate_editorial  # noqa: E402
from tests import test_priority7_phase4fc2 as C2  # noqa: E402
from tests import test_priority7_phase4fc2b as C2B  # noqa: E402
from tests import test_priority7_phase4fc2c as C2C  # noqa: E402

CORPUS = ROOT / "editorial" / "verb-pattern-candidates.json"
CONTEXT_FILE = ROOT / "editorial" / "priority-7-authoring-context.json"
C1C_MATRIX = ROOT / "reports" / "phase-4fc1c" / "adjudication-matrix.csv"
D3_MATRIX = ROOT / "reports" / "priority-7-phase-4fd3-adjudication.csv"
D31_SUMMARY = ROOT / "reports" / "priority-7-phase-4fd31-summary.md"

#: Phase 4F-D3.1 arrived on top of this commit and changed nothing else.
BASELINE_COMMIT = "3d613def18e9edf8bcabd331d40b5b90df30a9da"
BASELINE_TREE = "3d1a9600041f83a9a2374b0fef5a069bc77a4d63"

REFERENCE_ACTOR = "priority7-reference-analysis"
GENERATION_ACTOR = "priority7-example-generation"

#: The scope tier a reference verification covers, and the two higher tiers.
TIER_ONE = "external-verification"
HIGHER_TIERS = ("native-linguistic", "product-approval")

#: Independent expected values.  These are written from the locked D3 decision
#: rather than read out of the corpus or the adjudication CSV, so a joint edit
#: to the corpus and the artifact cannot make this suite agree with itself.
CORRECTIONS = {
    "P7-NR-018": {
        "patternId":
            "vp-p-dbac-take-care-of-o-accusative-target-d3e3eb63129c",
        "field": "examples[0].en",
        "prior": "I look after my fitness every day.",
        "final": "I work on my fitness every day.",
    },
    "P7-NR-028": {
        "patternId": "vp-p-lubic-enjoy-thing-or-activity-infinitive-activity"
                     "-be3742b7ce45",
        "field": "examples[0].en",
        "prior": "I like reading before sleep.",
        "final": "I like reading before bed.",
    },
    "P7-NR-037": {
        "patternId":
            "vp-p-podobac-sie-appeal-to-nominative-stimulus-dative-experiencer"
            "-ef199e675ee9",
        "field": "learnerExplanationEn; errorNotes[0].guidanceEn",
        "prior": "ten film podoba mi się",
        "final": "ten film mi się podoba",
    },
}

#: The row whose D2 blocker D3 overturned.  It must not move at all.
OVERTURNED = "P7-NR-011"

#: The historical D1 and D2 verdicts, which were produced independently of this
#: workspace and are recorded on all four adjudicated rows.
D1_VERDICT = "ACCEPT WITH NOTE"
D2_VERDICT = "CHANGES NEEDED"

#: The two patterns whose recorded event digests already failed to recompute at
#: the baseline.  D3.1 discloses this inherited state and repairs none of it.
INHERITED_STALE_DIGEST_ROWS = {
    "vp-p-mowic-tell-content-dative-recipient-accusative-content-2f2b1add1960",
    "vp-p-mowic-tell-content-dative-recipient-ze-clause-a01ddc4a4736",
}

#: The repository card P7-NR-028 declares as its source.  D3 rejected D2's
#: proposal to edit it, so it must be baseline identical -- and it must
#: already carry the English the canonical example was corrected to.
SOURCE_CARD_FILE = "data-a1.js"
SOURCE_CARD_ID = "a1-free-time-003"
SOURCE_CARD_EN = "I like reading before bed."

#: Everything Phase 4F-D3.1 was forbidden to touch.
UNCHANGED_FILES = (
    "editorial/priority-7-authoring-context.json",
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
)

#: The three phase-owned report/test artifacts.
D31_ARTIFACTS = {
    "reports/priority-7-phase-4fd3-adjudication.csv",
    "reports/priority-7-phase-4fd31-summary.md",
    "tests/test_priority7_phase4fd31.py",
}

#: The nine historical suites whose checkpoint reconstruction needed the
#: exact closed D3.1 normalizer.  This is a path manifest, distinct from
#: ``NORMALIZER_MODULES`` below: C2C and C2D delegate to C2 rather than
#: duplicating its object normalizer, but their own loaders still changed.
D31_HISTORICAL_TEST_REPAIRS = {
    f"tests/test_priority7_phase{name}.py"
    for name in ("4c", "4e", "4e1", "4fa", "4fb3b", "5a",
                 "4fc2", "4fc2c", "4fc2d")
}

#: Immutable Phase 4F-D3.1 transition.  Later phases may add arbitrary paths;
#: they are outside the baseline -> first-descendant boundary and therefore
#: cannot widen this set.
D31_CANDIDATE_PATHS = (
    {"editorial/verb-pattern-candidates.json"}
    | D31_ARTIFACTS
    | D31_HISTORICAL_TEST_REPAIRS
)

#: The historical suites whose normalizers absorb the D3.1 corrections.
NORMALIZER_MODULES = C2B.HISTORICAL_MODULES


def git(*arguments):
    return subprocess.run(["git", "-C", str(ROOT), *arguments],
                          capture_output=True, text=True, check=False)


def candidate_revision():
    """Return the committed D3.1 revision, or None while it is uncommitted.

    D3.1 is integrated as the first descendant of the immutable baseline.
    Once later commits exist, that first descendant remains the phase-owned
    candidate; arbitrary live HEAD additions never become part of D3.1.
    """
    head = git("rev-parse", "HEAD")
    if head.returncode != 0:
        raise AssertionError(head.stderr)
    if head.stdout.strip() == BASELINE_COMMIT:
        return None
    revisions = git(
        "rev-list", "--reverse", "--ancestry-path",
        f"{BASELINE_COMMIT}..HEAD")
    if revisions.returncode != 0:
        raise AssertionError(revisions.stderr)
    descendants = revisions.stdout.split()
    if not descendants:
        raise AssertionError("baseline is not an ancestor of HEAD")
    return descendants[0]


def candidate_footprint():
    """Return exactly the phase-owned D3.1 transition paths.

    Before integration this reads the baseline-to-working-candidate delta,
    including untracked D3.1 artifacts.  After integration it reads only the
    baseline-to-first-descendant commit, so later committed or working-tree
    files are deliberately irrelevant.
    """
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
    """Read a path as of the pinned baseline commit, never as of HEAD."""
    result = git("show", f"{BASELINE_COMMIT}:{path}")
    if result.returncode != 0:
        raise AssertionError(f"baseline blob missing: {path}")
    return result.stdout


def baseline_corpus():
    return json.loads(baseline_blob("editorial/verb-pattern-candidates.json"))


def corpus_text():
    """The corpus text as Phase 4F-D3.1 delivered it.

    Phase 4F-E1 later appended the 45 tier-2 acceptances this suite proves
    absent.  That approved governance work is reverted here through the
    phase-owned text normaliser, which asserts the file's canonical stored
    form rather than assuming it, so every D3.1 claim below still means what
    it meant when it was written.
    """
    return E1.without_phase_4fe1_corpus_text(
        F2.without_phase_4ff2_corpus_text(
            H2.without_phase_4fh2_corpus_text(
                H21.without_phase_4fh21_corpus_text(
                    CORPUS.read_text(encoding="utf-8")))))


def context_text():
    """The context text as Phase 4F-D3.1 left it: E1's registry removed."""
    return E1.without_phase_4fe1_context_text(
        F2.without_phase_4ff2_context_text(
            H2.without_phase_4fh2_context_text(
                H21.without_phase_4fh21_context_text(
                    CONTEXT_FILE.read_text(encoding="utf-8")))))


def live_corpus():
    """The corpus as Phase 4F-D3.1 delivered it, later work reverted."""
    return json.loads(corpus_text())


def unnormalised_corpus_text():
    """The corpus file exactly as it stands right now."""
    return CORPUS.read_text(encoding="utf-8")


def iter_patterns(corpus):
    for lemma in corpus["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                yield lemma, meaning, pattern


def patterns_by_id(corpus):
    return {pattern["id"]: (lemma, meaning, pattern)
            for lemma, meaning, pattern in iter_patterns(corpus)}


def examples_of(pattern):
    return pattern.get("examples") or []


def pattern_id_for(review_id):
    with C1C_MATRIX.open(newline="", encoding="utf-8") as handle:
        rows = {row["reviewId"]: row for row in csv.DictReader(handle)}
    return rows[review_id]["patternId"]


def digests(corpus, stage):
    return {pattern["id"]: T.review_scope_digest(stage, lemma, meaning, pattern)
            for lemma, meaning, pattern in iter_patterns(corpus)}


def d3_rows():
    with D3_MATRIX.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class D31Case(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.current = live_corpus()
        cls.baseline = baseline_corpus()
        cls.current_by_id = patterns_by_id(cls.current)
        cls.baseline_by_id = patterns_by_id(cls.baseline)
        cls.corrected_pattern_ids = {row["patternId"]
                                     for row in CORRECTIONS.values()}

    def pattern(self, corpus_by_id, review_id):
        return corpus_by_id[pattern_id_for(review_id)][2]


class BaselineIntegrityTests(D31Case):
    """The baseline this suite argues from is the one D3.1 started at."""

    def test_the_pinned_baseline_commit_and_tree_agree(self):
        tree = git("rev-parse", f"{BASELINE_COMMIT}^{{tree}}").stdout.strip()
        self.assertEqual(BASELINE_TREE, tree)

    def test_the_baseline_corpus_still_holds_all_three_prior_values(self):
        for review_id, row in CORRECTIONS.items():
            with self.subTest(review_id=review_id):
                pattern = self.baseline_by_id[row["patternId"]][2]
                blob = json.dumps(pattern, ensure_ascii=False)
                self.assertIn(row["prior"], blob)
                self.assertNotIn(row["final"], blob)


class CanonicalChangeTests(D31Case):
    """Exactly the three approved corrections, and nothing else."""

    def test_exactly_three_patterns_differ_from_the_baseline(self):
        changed = {pattern_id
                   for pattern_id, (_, _, pattern) in self.current_by_id.items()
                   if pattern != self.baseline_by_id[pattern_id][2]}
        self.assertEqual(self.corrected_pattern_ids, changed)

    def test_the_overturned_row_is_byte_identical(self):
        pattern_id = pattern_id_for(OVERTURNED)
        self.assertNotIn(pattern_id, self.corrected_pattern_ids)
        self.assertEqual(self.baseline_by_id[pattern_id][2],
                         self.current_by_id[pattern_id][2])

    def test_the_two_example_corrections_are_the_exact_approved_values(self):
        for review_id in ("P7-NR-018", "P7-NR-028"):
            with self.subTest(review_id=review_id):
                row = CORRECTIONS[review_id]
                before = examples_of(
                    self.baseline_by_id[row["patternId"]][2])
                after = examples_of(self.current_by_id[row["patternId"]][2])
                self.assertEqual(1, len(before))
                self.assertEqual(1, len(after))
                self.assertEqual(row["prior"], before[0]["en"])
                self.assertEqual(row["final"], after[0]["en"])

    def test_only_the_english_moved_on_the_two_example_rows(self):
        for review_id in ("P7-NR-018", "P7-NR-028"):
            with self.subTest(review_id=review_id):
                row = CORRECTIONS[review_id]
                before = examples_of(
                    self.baseline_by_id[row["patternId"]][2])[0]
                after = examples_of(self.current_by_id[row["patternId"]][2])[0]
                moved = {field for field in set(before) | set(after)
                         if before.get(field) != after.get(field)}
                self.assertEqual({"en"}, moved)

    def test_018_keeps_its_polish_key_id_and_generated_provenance(self):
        example = examples_of(
            self.current_by_id[CORRECTIONS["P7-NR-018"]["patternId"]][2])[0]
        self.assertEqual("Codziennie dbam o kondycję.", example["pl"])
        self.assertEqual("care-every-day", example["key"])
        self.assertEqual(
            "vp-e-dbac-take-care-of-o-accusative-target-care-every-day"
            "-171833c3174d", example["id"])
        self.assertEqual(
            {"kind": "editorial-generated",
             "generatorRef": GENERATION_ACTOR,
             "adoptedAt": "2026-08-16"}, example["origin"])

    def test_028_keeps_its_polish_key_id_and_repository_source(self):
        example = examples_of(
            self.current_by_id[CORRECTIONS["P7-NR-028"]["patternId"]][2])[0]
        self.assertEqual("Lubię czytać przed snem.", example["pl"])
        self.assertEqual("reading-before-sleep", example["key"])
        self.assertEqual(
            "vp-e-lubic-enjoy-thing-or-activity-infinitive-activity"
            "-reading-before-sleep-d573db6f04d1", example["id"])
        self.assertEqual(
            {"kind": "repository-reuse",
             "repositorySource": {"kind": "card", "id": SOURCE_CARD_ID,
                                  "field": "ex"}}, example["origin"])

    def test_037_moved_only_the_positive_model_in_exactly_two_fields(self):
        row = CORRECTIONS["P7-NR-037"]
        before = self.baseline_by_id[row["patternId"]][2]
        after = self.current_by_id[row["patternId"]][2]
        moved = {field for field in set(before) | set(after)
                 if before.get(field) != after.get(field)}
        self.assertEqual({"learnerExplanationEn", "errorNotes"}, moved)
        # The English is not otherwise rewritten: substituting the model back
        # reproduces the baseline string exactly.
        self.assertEqual(
            before["learnerExplanationEn"],
            after["learnerExplanationEn"].replace(row["final"], row["prior"]))
        self.assertEqual(1, len(after["errorNotes"]))
        self.assertEqual(
            before["errorNotes"][0]["guidanceEn"],
            after["errorNotes"][0]["guidanceEn"].replace(
                row["final"], row["prior"]))
        # Everything else on the error note is untouched.
        for field in ("kind", "incorrectForm"):
            self.assertEqual(before["errorNotes"][0][field],
                             after["errorNotes"][0][field])

    def test_037_leaves_the_frozen_linguistic_fields_alone(self):
        row = CORRECTIONS["P7-NR-037"]
        before = self.baseline_by_id[row["patternId"]][2]
        after = self.current_by_id[row["patternId"]][2]
        for field in ("id", "key", "relationType", "complements", "cefr",
                      "teachingStatus", "usage", "activityEligibility",
                      "evidence", "reviewState", "reviewEvents",
                      "releaseMode", "contentRefs"):
            with self.subTest(field=field):
                self.assertEqual(before.get(field), after.get(field))
        before_meaning = self.baseline_by_id[row["patternId"]][1]
        after_meaning = self.current_by_id[row["patternId"]][1]
        self.assertEqual(
            {key: value for key, value in before_meaning.items()
             if key != "patterns"},
            {key: value for key, value in after_meaning.items()
             if key != "patterns"})

    def test_the_old_wording_is_gone_from_the_canonical_corpus(self):
        blob = corpus_text()
        for row in CORRECTIONS.values():
            with self.subTest(prior=row["prior"]):
                self.assertNotIn(row["prior"], blob)
                self.assertIn(row["final"], blob)

    def test_the_positive_model_appears_exactly_twice_and_only_corrected(self):
        blob = corpus_text()
        self.assertEqual(2, blob.count(CORRECTIONS["P7-NR-037"]["final"]))
        self.assertEqual(0, blob.count(CORRECTIONS["P7-NR-037"]["prior"]))


class SourceCardTests(D31Case):
    """028 was corrected towards its own source, and the source stands."""

    def test_the_source_card_file_is_baseline_identical(self):
        self.assertEqual(baseline_blob(SOURCE_CARD_FILE),
                         (ROOT / SOURCE_CARD_FILE).read_text(encoding="utf-8"))

    def test_the_source_card_already_carried_the_corrected_english(self):
        for text, label in ((baseline_blob(SOURCE_CARD_FILE), "baseline"),
                            ((ROOT / SOURCE_CARD_FILE).read_text(
                                encoding="utf-8"), "current")):
            with self.subTest(revision=label):
                line = next(item for item in text.splitlines()
                            if f'id:"{SOURCE_CARD_ID}"' in item)
                self.assertIn(f'exEn:"{SOURCE_CARD_EN}"', line)
                self.assertIn('ex:"Lubię czytać przed snem."', line)

    def test_canonical_english_now_agrees_with_the_source_card(self):
        example = examples_of(
            self.current_by_id[CORRECTIONS["P7-NR-028"]["patternId"]][2])[0]
        source = example["origin"]["repositorySource"]
        self.assertEqual({"kind": "card", "id": SOURCE_CARD_ID, "field": "ex"},
                         source)
        line = next(item for item
                    in (ROOT / SOURCE_CARD_FILE).read_text(
                        encoding="utf-8").splitlines()
                    if f'id:"{source["id"]}"' in item)
        self.assertIn(f'exEn:"{example["en"]}"', line)
        self.assertIn(f'ex:"{example["pl"]}"', line)

    def test_the_baseline_canonical_english_disagreed_with_the_card(self):
        """The defect D3 upheld was real, so this repair is not vacuous."""
        example = examples_of(
            self.baseline_by_id[CORRECTIONS["P7-NR-028"]["patternId"]][2])[0]
        line = next(item for item in baseline_blob(
            SOURCE_CARD_FILE).splitlines() if f'id:"{SOURCE_CARD_ID}"' in item)
        self.assertNotIn(f'exEn:"{example["en"]}"', line)


class ScopeDigestTests(D31Case):
    """Tier-1 never moved; the editorial tier moved on exactly three rows."""

    def test_tier_one_digests_are_baseline_identical_on_all_45(self):
        before = digests(self.baseline, TIER_ONE)
        after = digests(self.current, TIER_ONE)
        self.assertEqual(45, len(before))
        self.assertEqual(before, after)

    def test_higher_scope_moved_on_exactly_the_three_corrected_rows(self):
        for stage in HIGHER_TIERS:
            with self.subTest(stage=stage):
                before = digests(self.baseline, stage)
                after = digests(self.current, stage)
                moved = {pattern_id for pattern_id in before
                         if before[pattern_id] != after[pattern_id]}
                self.assertEqual(self.corrected_pattern_ids, moved)

    def test_the_solo_chain_stages_project_the_same_tiers(self):
        """reference-verification is tier-1; editorial-review is tier-2."""
        for lemma, meaning, pattern in iter_patterns(self.current):
            self.assertEqual(
                T.review_scope_digest(TIER_ONE, lemma, meaning, pattern),
                T.review_scope_digest("reference-verification", lemma,
                                      meaning, pattern))
            self.assertEqual(
                T.review_scope_digest("native-linguistic", lemma, meaning,
                                      pattern),
                T.review_scope_digest("editorial-review", lemma, meaning,
                                      pattern))
            break

    @staticmethod
    def rows_whose_event_digest_no_longer_recomputes(corpus):
        stale = set()
        for lemma, meaning, pattern in iter_patterns(corpus):
            for event in pattern.get("reviewEvents") or []:
                if T.review_scope_digest(event["kind"], lemma, meaning,
                                         pattern) != event["scopeDigest"]:
                    stale.add(pattern["id"])
        return stale

    def test_no_event_was_re_stamped_and_none_newly_went_stale(self):
        """D3.1 neither refreshed a recorded digest nor invalidated one.

        Two mowic rows already carried digests that predate Phase 4F-B3B's
        tier-1 corrections and were deliberately not re-stamped.  That set is
        inherited, not created here: what matters is that it is identical
        before and after, so no reference verification lost its cover.
        """
        before = self.rows_whose_event_digest_no_longer_recomputes(
            self.baseline)
        after = self.rows_whose_event_digest_no_longer_recomputes(self.current)
        self.assertEqual(before, after)
        # The inherited set is exactly the two disclosed mowic rows.
        self.assertEqual(INHERITED_STALE_DIGEST_ROWS, before)
        # And no corrected row joined it: tier-1 did not move on any of them.
        self.assertEqual(set(), after & self.corrected_pattern_ids)


class GovernanceTests(D31Case):
    """Editorial-tier corrections advance no stage and create no event."""

    def test_all_45_are_reference_verified_with_47_acceptances(self):
        states, events, accepts = [], [], 0
        for _, _, pattern in iter_patterns(self.current):
            states.append(pattern["reviewState"])
            for event in pattern.get("reviewEvents") or []:
                events.append(event["kind"])
                if event["decision"] == "accept":
                    accepts += 1
        self.assertEqual(45, len(states))
        self.assertEqual({"reference-verified"}, set(states))
        self.assertEqual(47, len(events))
        self.assertEqual({"reference-verification"}, set(events))
        self.assertEqual(47, accepts)

    def test_there_is_no_editorial_review_and_no_product_approval(self):
        for _, _, pattern in iter_patterns(self.current):
            for event in pattern.get("reviewEvents") or []:
                self.assertNotIn(
                    event["kind"], {"editorial-review", "product-approval",
                                    "native-linguistic"})
        blob = corpus_text()
        self.assertNotIn("editorial-review", blob)
        self.assertNotIn("product-approval", blob)
        self.assertNotIn("editorial-reviewed", blob)
        self.assertNotIn('"approved"', blob)

    def test_no_fresh_reference_verification_event_was_created(self):
        before = [event for _, _, pattern in iter_patterns(self.baseline)
                  for event in pattern.get("reviewEvents") or []]
        after = [event for _, _, pattern in iter_patterns(self.current)
                 for event in pattern.get("reviewEvents") or []]
        self.assertEqual(before, after)
        self.assertEqual({"2026-08-14"}, {event["reviewedAt"]
                                          for event in after})
        self.assertEqual({REFERENCE_ACTOR},
                         {event["actorRef"] for event in after})

    def test_the_corpus_still_validates_and_derives_the_same_states(self):
        context = C2.build_context()
        self.assertEqual([], validate_editorial(self.current, context))

    def test_counts_and_identity_are_unchanged(self):
        self.assertEqual(45, len(self.current_by_id))
        self.assertEqual(len(self.baseline_by_id), len(self.current_by_id))
        self.assertEqual(set(self.baseline_by_id), set(self.current_by_id))
        examples = [item for _, _, pattern in iter_patterns(self.current)
                    for item in examples_of(pattern)]
        self.assertEqual(29, len(examples))
        self.assertEqual(29, len({item["id"] for item in examples}))
        for _, _, pattern in iter_patterns(self.current):
            for item in examples_of(pattern):
                self.assertEqual(
                    T.allocate_example_id(pattern["id"], item["key"]),
                    item["id"])
        self.assertEqual(
            [item["id"] for item in
             [example for _, _, p in iter_patterns(self.baseline)
              for example in examples_of(p)]],
            [item["id"] for item in examples])


class UntouchedSurfaceTests(D31Case):
    """Authoring context, tooling, shipping corpus and runtime stand."""

    #: Phase 4F-E1 registered its actors in the authoring context.  The file
    #: is still baseline-identical once exactly the two blocks E1 inserted are
    #: removed, which is what "D3.1 did not touch it" means going forward.
    E1_NORMALISED_FILES = {"editorial/priority-7-authoring-context.json"}

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
                if relative in self.E1_NORMALISED_FILES:
                    text = E1.without_phase_4fe1_context_text(
                        F2.without_phase_4ff2_context_text(
                            H2.without_phase_4fh2_context_text(
                                H21.without_phase_4fh21_context_text(text))))
                self.assertEqual(baseline_blob(relative), text)

    def test_the_phase_owned_transition_is_exactly_thirteen_paths(self):
        self.assertEqual(13, len(D31_CANDIDATE_PATHS))
        self.assertEqual(D31_CANDIDATE_PATHS, candidate_footprint())

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


class AdjudicationArtifactTests(D31Case):
    """The D3 artifact records the locked decision, including the overturn."""

    def test_the_artifact_has_exactly_the_four_rows(self):
        rows = d3_rows()
        self.assertEqual(4, len(rows))
        self.assertEqual(["P7-NR-011", "P7-NR-018", "P7-NR-028", "P7-NR-037"],
                         [row["reviewId"] for row in rows])

    def test_every_required_column_is_present(self):
        with D3_MATRIX.open(newline="", encoding="utf-8") as handle:
            header = next(csv.reader(handle))
        self.assertEqual(
            ["reviewId", "d1Verdict", "d2Verdict", "d3Decision",
             "canonicalChangeRequired", "field", "priorValue", "finalValue",
             "tier1Affected", "freshReferenceVerificationRequired",
             "rationale"], header)

    def test_the_overturned_row_records_no_canonical_edit(self):
        row = next(item for item in d3_rows()
                   if item["reviewId"] == OVERTURNED)
        self.assertIn("OVERTURNED", row["d3Decision"])
        self.assertEqual(D2_VERDICT, row["d2Verdict"])
        self.assertEqual("no", row["canonicalChangeRequired"])
        self.assertEqual("", row["field"])
        self.assertEqual(row["priorValue"], row["finalValue"])

    def test_the_historical_d1_and_d2_verdicts_are_recorded_on_every_row(self):
        """The independently produced verdicts, not a placeholder."""
        for row in d3_rows():
            with self.subTest(review_id=row["reviewId"]):
                self.assertEqual(D1_VERDICT, row["d1Verdict"])
                self.assertEqual(D2_VERDICT, row["d2Verdict"])

    def test_no_placeholder_survives_anywhere_in_the_artifact(self):
        self.assertNotIn("not-recorded",
                         D3_MATRIX.read_text(encoding="utf-8"))

    def test_the_report_artifacts_are_lf_only_and_whitespace_clean(self):
        """CRLF here would trip `git diff --check` once committed."""
        for path in (D3_MATRIX, D31_SUMMARY):
            with self.subTest(path=path.name):
                raw = path.read_bytes()
                self.assertNotIn(b"\r", raw)
                for number, line in enumerate(
                        raw.decode("utf-8").splitlines(), start=1):
                    self.assertEqual(line.rstrip(), line,
                                     f"{path.name}:{number} trailing space")

    def test_the_three_upheld_rows_match_the_corpus_exactly(self):
        rows = {item["reviewId"]: item for item in d3_rows()}
        for review_id, expected in CORRECTIONS.items():
            with self.subTest(review_id=review_id):
                row = rows[review_id]
                self.assertIn("UPHELD", row["d3Decision"])
                self.assertEqual("yes", row["canonicalChangeRequired"])
                self.assertEqual(expected["field"], row["field"])
                self.assertEqual(expected["prior"], row["priorValue"])
                self.assertEqual(expected["final"], row["finalValue"])
                self.assertEqual("no", row["tier1Affected"])
                self.assertEqual(
                    "no", row["freshReferenceVerificationRequired"])

    def test_028_records_that_the_source_card_edit_was_rejected(self):
        row = next(item for item in d3_rows()
                   if item["reviewId"] == "P7-NR-028")
        self.assertIn("REJECTED", row["d3Decision"])
        self.assertIn(SOURCE_CARD_ID, row["rationale"])

    def test_the_summary_records_the_scope_and_the_verdict(self):
        text = D31_SUMMARY.read_text(encoding="utf-8")
        for needle in ("P7-NR-011", "P7-NR-018", "P7-NR-028", "P7-NR-037",
                       BASELINE_COMMIT, "GO"):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)

    def test_the_summary_states_the_tier_one_result_unambiguously(self):
        text = D31_SUMMARY.read_text(encoding="utf-8")
        self.assertIn(
            "tier-1 changed on 0 of 45; tier-1 is unchanged on all\n"
            "45 patterns", text)

    def test_the_summary_discloses_the_inherited_stale_digest_pair(self):
        """Disclosed, scoped as inherited, and explicitly not repaired."""
        text = D31_SUMMARY.read_text(encoding="utf-8")
        for pattern_id in INHERITED_STALE_DIGEST_ROWS:
            with self.subTest(pattern_id=pattern_id):
                self.assertIn(pattern_id, text)
        for claim in (
                "D3.1 introduced no new stale historical scope digest",
                "identical before and after",
                "reference-verification state remains valid",
                "does not repair or rewrite historical review events"):
            with self.subTest(claim=claim):
                self.assertIn(claim, text)
        # The superseded, incorrect blanket claim must be gone.
        self.assertNotIn("so no\nevent went stale", text)


class NegativeControlTests(D31Case):
    """A fourth unauthorized canonical wording change must be rejected."""

    def corrupted(self, mutate):
        corpus = copy.deepcopy(self.current)
        mutate(patterns_by_id(corpus))
        return corpus

    def detectors(self, corpus):
        """Every independent signal this suite would reject a corpus on."""
        changed = {pattern_id for pattern_id, (_, _, pattern)
                   in patterns_by_id(corpus).items()
                   if pattern != self.baseline_by_id[pattern_id][2]}
        higher = {pattern_id for pattern_id, digest
                  in digests(corpus, "native-linguistic").items()
                  if digest != digests(self.baseline,
                                       "native-linguistic")[pattern_id]}
        return {
            "changed row set": changed == self.corrected_pattern_ids,
            "tier-2 row set": higher == self.corrected_pattern_ids,
            "tier-1 unchanged":
                digests(corpus, TIER_ONE) == digests(self.baseline, TIER_ONE),
            # The exact-value control: only the three approved corrections
            # normalise away, so anything else leaves a residue.
            "normalises to baseline":
                C2.without_phase_4fd31_corrections(corpus) == self.baseline,
        }

    def assert_accepted(self, corpus):
        self.assertEqual({}, {name: passed
                              for name, passed in self.detectors(corpus).items()
                              if not passed})

    def assert_rejected(self, corpus, label):
        """At least one detector must fire on an unauthorized corpus."""
        failed = [name for name, passed in self.detectors(corpus).items()
                  if not passed]
        self.assertNotEqual([], failed,
                            f"unauthorized change went undetected: {label}")

    def test_the_delivered_corpus_passes_every_detector(self):
        """The controls below are not vacuous: the real corpus is accepted."""
        self.assert_accepted(self.current)

    def test_a_fourth_rows_wording_change_is_caught(self):
        def mutate(by_id):
            pattern = by_id[pattern_id_for(OVERTURNED)][2]
            examples_of(pattern)[0]["en"] = "I am thanking my sister."
        self.assert_rejected(self.corrupted(mutate), "fourth row wording")

    def test_a_fourth_rows_learner_explanation_change_is_caught(self):
        def mutate(by_id):
            pattern = by_id[
                "vp-p-szukac-seek-genitive-target-71dc6eff512c"][2]
            pattern["learnerExplanationEn"] = "mutated explanation"
        self.assert_rejected(self.corrupted(mutate), "fourth row explanation")

    def test_a_further_edit_to_a_corrected_row_is_caught(self):
        def mutate(by_id):
            pattern = by_id[CORRECTIONS["P7-NR-018"]["patternId"]][2]
            examples_of(pattern)[0]["pl"] = "Dbam o kondycję."
        self.assert_rejected(self.corrupted(mutate), "extra edit on 018")

    def test_a_tier_one_change_is_caught(self):
        def mutate(by_id):
            pattern = by_id[CORRECTIONS["P7-NR-037"]["patternId"]][2]
            pattern["complements"][0]["required"] = False
        self.assert_rejected(self.corrupted(mutate), "tier-one complement")

    def test_reverting_a_correction_is_caught(self):
        def mutate(by_id):
            row = CORRECTIONS["P7-NR-028"]
            examples_of(by_id[row["patternId"]][2])[0]["en"] = row["prior"]
        self.assert_rejected(self.corrupted(mutate), "reverted 028")

    def test_an_unauthorized_edit_survives_every_historical_normalizer(self):
        """The normalizers absorb only the three approved corrections."""
        baseline_checkpoint = None
        for name in NORMALIZER_MODULES:
            module = importlib.import_module(name)
            with self.subTest(module=name):
                exact = module.without_phase_4fd31_corrections(self.current)
                if baseline_checkpoint is None:
                    baseline_checkpoint = exact
                self.assertEqual(baseline_checkpoint, exact)
                for review_id, row in CORRECTIONS.items():
                    blob = json.dumps(exact, ensure_ascii=False)
                    self.assertIn(row["prior"], blob)
                for label, mutate in self.unauthorized_mutations().items():
                    corpus = copy.deepcopy(self.current)
                    mutate(patterns_by_id(corpus))
                    self.assertNotEqual(
                        baseline_checkpoint,
                        module.without_phase_4fd31_corrections(corpus),
                        f"{name} absorbed an unauthorized change: {label}")

    def test_the_c2c_text_normalizer_accepts_only_the_exact_delivered_text(self):
        """It reverts the real text, and refuses any other match count."""
        text = corpus_text()
        reverted = C2C.without_phase_4fd31_text(text)
        for row in CORRECTIONS.values():
            self.assertIn(row["prior"], reverted)
        self.assertEqual(self.baseline, json.loads(reverted))

        line = next(item for item in text.splitlines()
                    if '"learnerExplanationEn"' in item
                    and CORRECTIONS["P7-NR-037"]["final"] in item)
        # A second copy of the corrected field makes the count 2, not 1.
        duplicated = text.replace(line, line + "\n" + line, 1)
        self.assertNotEqual(text, duplicated)
        with self.assertRaises(AssertionError):
            C2C.without_phase_4fd31_text(duplicated)

        # And a corpus that never had the correction at all is refused too.
        with self.assertRaises(AssertionError):
            C2C.without_phase_4fd31_text(reverted)

    @staticmethod
    def unauthorized_mutations():
        def fourth_row(by_id):
            examples_of(by_id[pattern_id_for(OVERTURNED)][2])[0]["en"] = "x"

        def extra_field(by_id):
            by_id[CORRECTIONS["P7-NR-018"]["patternId"]][2][
                "learnerExplanationEn"] = "mutated"

        def polish(by_id):
            examples_of(by_id[CORRECTIONS["P7-NR-028"]["patternId"]][2])[0][
                "pl"] = "Lubię czytać wieczorem."

        def provenance(by_id):
            examples_of(by_id[CORRECTIONS["P7-NR-028"]["patternId"]][2])[0][
                "origin"] = {"kind": "editorial-generated",
                             "generatorRef": GENERATION_ACTOR,
                             "adoptedAt": "2026-08-16"}

        def guidance(by_id):
            by_id[CORRECTIONS["P7-NR-037"]["patternId"]][2]["errorNotes"][0][
                "incorrectForm"] = "mutated"

        return {"fourth row": fourth_row, "extra field": extra_field,
                "polish": polish, "provenance": provenance,
                "guidance": guidance}


class HistoricalSuiteTests(D31Case):
    """Older phases keep their own answers about their own content."""

    def test_the_normalizer_is_declared_identically_everywhere(self):
        declarations = [importlib.import_module(name).
                        PHASE_4FD31_EDITORIAL_CORRECTION
                        for name in NORMALIZER_MODULES]
        declarations.append(C2.PHASE_4FD31_EDITORIAL_CORRECTION)
        self.assertEqual(7, len(declarations))
        for declaration in declarations:
            self.assertEqual(declarations[0], declaration)
            self.assertEqual({"P7-NR-018", "P7-NR-028", "P7-NR-037"},
                             set(declaration))

    def test_the_declared_map_matches_this_suites_expectations(self):
        declared = C2.PHASE_4FD31_EDITORIAL_CORRECTION
        for review_id, row in CORRECTIONS.items():
            with self.subTest(review_id=review_id):
                entry = declared[review_id]
                self.assertEqual(row["patternId"], entry["patternId"])
                pairs = [value for key, value in entry.items()
                         if key != "patternId"]
                for prior, final in pairs:
                    self.assertIn(row["prior"], prior)
                    self.assertIn(row["final"], final)

    def test_normalising_reproduces_the_baseline_corpus_exactly(self):
        """The three corrections are provably the whole canonical delta."""
        self.assertEqual(
            self.baseline,
            C2.without_phase_4fd31_corrections(self.current))


if __name__ == "__main__":
    unittest.main()
