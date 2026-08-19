"""Priority 7 Phase 4F-B3B -- implementation of the approved B3A adjudication.

B3A adjudicated 45 native-review rows and approved five canonical corrections.
All five are implemented here.  Two of them took a detour worth recording,
because the detour is the phase's substantive finding:

``complements[].required`` is projected by ``_project_complement`` into the
*external-verification* scope tier -- the tier a ``reference-verification``
event stands over.  So the optionality corrections on P7-NR-029 and P7-NR-030
were never editorial-only: applying them retired the Phase 4F-A reference
verification on both rows and dropped them from ``reference-verified`` to
``research``.  B3B stopped rather than redigest a historical event in place.

Phase 4F-B3B.1 then re-opened the WSJP Składnia, confirmed the parenthesised
KOMU on both frames, applied the corrections, and appended one *fresh* tier-1
acceptance to each.  The original 45 acceptances were left verbatim.  The
corpus therefore carries 47 reference verifications: 45 historical and 2 that
stand over the corrected scope.

Every mutation in this file is applied to an in-memory copy.  Nothing here
writes to the corpus, the context, the tooling or any shipping file.
"""

from __future__ import annotations

import copy
import csv
import hashlib
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
    ValidationContext,
    evidence_digest,
    review_scope_digest,
    validate_editorial,
)

CORPUS = ROOT / "editorial" / "verb-pattern-candidates.json"
CONTEXT_FILE = ROOT / "editorial" / "priority-7-authoring-context.json"
MATRIX = ROOT / "reports" / "phase-4fb3a" / "adjudication-matrix.csv"
B3A_SUMMARY = ROOT / "reports" / "phase-4fb3a" / "summary.md"
B3B_SUMMARY = ROOT / "reports" / "priority-7-phase-4fb3b-summary.md"

#: The commit Phase 4F-B3B started from, and the commit Phase 4F-A produced --
#: the same commit, seen from two directions.  Pinned by SHA and never resolved
#: as ``HEAD``: the working tree is what this phase changed, so comparing the
#: tree against ``HEAD`` once B3B is committed would compare it with itself.
BASELINE_COMMIT = "7beb50d7b3463d7745352f1608f1e30019529fdf"
BASELINE_TREE = "ad6095037214360836b1bd9a5bb06326e0b809d7"

#: The commit B3B produced -- the far side of the immutable B3B transition,
#: and the commit Phase 4F-C1 in turn took as *its* baseline.
#:
#: Phase 4F-C1.1 repair.  The footprint guard below used to diff
#: ``BASELINE_COMMIT`` with no second revision, which git resolves as "that
#: revision versus the current working tree".  That reads a frozen historical
#: claim off live state: while a later phase's files are untracked they are
#: invisible to ``git diff`` and the guard passes, and the moment they are
#: committed the closed footprint rejects them.  A completed phase's history
#: does not change when a later phase begins, so the transition is now named
#: by both of its endpoints.
B3B_CHECKPOINT = "080d92ad49a514332f21ecd90b4a11de070a243f"

INSPECTED_ON = "2026-08-14"
REFERENCE_ACTOR = "priority7-reference-analysis"

PATTERN_COUNT = 45
#: Acceptances Phase 4F-A wrote, and the total standing after the B3B.1 refresh.
PHASE_4FA_EVENT_COUNT = 45
REFRESH_EVENT_COUNT = 2
CURRENT_EVENT_COUNT = PHASE_4FA_EVENT_COUNT + REFRESH_EVENT_COUNT

# ---------------------------------------------------------------------------
# The adjudicated plan, restated as data.
# ---------------------------------------------------------------------------

EXPECTED_DISPOSITIONS = {
    "ACCEPT AS IS": 21,
    "ACCEPT WITH NONBLOCKING NOTE": 19,
    "CHANGE BEFORE EDITORIAL ACCEPTANCE": 5,
}

APPROVED_CHANGE_ROWS = (
    "P7-NR-005", "P7-NR-029", "P7-NR-030", "P7-NR-037", "P7-NR-040")

SLUCHAC = "vp-p-sluchac-obey-genitive-object-674adae2dec3"
MOWIC_ACC = (
    "vp-p-mowic-tell-content-dative-recipient-accusative-content-2f2b1add1960")
MOWIC_ZE = "vp-p-mowic-tell-content-dative-recipient-ze-clause-a01ddc4a4736"
PODOBAC = (
    "vp-p-podobac-sie-appeal-to-nominative-stimulus-dative-experiencer"
    "-ef199e675ee9")
WIERZYC_W = "vp-p-wierzyc-have-trust-w-accusative-target-6561408ea8d1"

#: The five approved rows, and the only pattern-level keys each may move.
#: ``reviewEvents`` appears only where a fresh tier-1 acceptance was appended.
APPROVED_FIELDS = {
    SLUCHAC: {"learnerExplanationEn"},
    MOWIC_ACC: {"complements", "learnerExplanationEn", "reviewEvents"},
    MOWIC_ZE: {"complements", "learnerExplanationEn", "reviewEvents"},
    PODOBAC: {"teachingStatus", "cefr"},
    WIERZYC_W: {"teachingStatus", "cefr"},
}

#: Rows whose optionality correction reached tier-1 reference scope and so
#: required a fresh reference verification.
REFRESHED_ROWS = (MOWIC_ACC, MOWIC_ZE)

#: Phase 4F-C example handoff.  The first five are slots that were already
#: future work before B3B; the rest are example findings B3A routed to 4F-C.
PENDING_EXAMPLE_ROWS = (
    "P7-NR-011", "P7-NR-012", "P7-NR-033", "P7-NR-042", "P7-NR-044")
B3A_EXAMPLE_FINDINGS = (
    "P7-NR-007", "P7-NR-014", "P7-NR-018", "P7-NR-031",
    "P7-NR-032", "P7-NR-035", "P7-NR-036", "P7-NR-043")

B3A_ARTIFACT_SHA256 = {
    "adjudication-matrix.csv":
        "95f0551c5af82f2771ca341aee19acffbf102e67da5f2cec7a7610830a5e27cd",
    "summary.md":
        "3eec5862313b6de0234a6c102a74ac97df8d6540343e906798038db67e77109f",
}

#: Earlier suites whose "no later phase changes linguistic content" guard was
#: re-pinned to normalise the five approved edits away and nothing else.
NORMALISING_GUARD_MODULES = (
    "test_priority7_phase4c.py", "test_priority7_phase4e1.py",
    "test_priority7_phase4fa.py", "test_priority7_phase5a.py")

#: Earlier suites that had to learn the difference between Phase 4F-A's own
#: 45-acceptance checkpoint and the 47 standing after the targeted refresh.
CHECKPOINT_GUARD_MODULES = NORMALISING_GUARD_MODULES + (
    "test_priority7_phase4e.py", "test_priority7_phase3d1.py")

B3B_MODIFIED_FILES = tuple(sorted(
    ["editorial/verb-pattern-candidates.json"]
    + [f"tests/{name}" for name in CHECKPOINT_GUARD_MODULES]))

B3B_ADDED_FILES = (
    "reports/phase-4fb3a/adjudication-matrix.csv",
    "reports/phase-4fb3a/summary.md",
    "reports/priority-7-phase-4fb3b-summary.md",
    "tests/test_priority7_phase4fb3b.py",
)

B3B_FOOTPRINT = frozenset(B3B_MODIFIED_FILES) | frozenset(B3B_ADDED_FILES)

SHIPPING_PATHS = (
    "priority7_tooling.py", "pp-verb-patterns.js", "pp-usage.js",
    "pp-answer.js", "pp-distractor.js", "pp-migrate.js", "sw.js",
    "index.html", "manifest.json", "data-verbs.js", "data-a1.js",
    "data-a2.js", "data-b1.js", "data-grammar.js",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


def transition_footprint(repository, baseline, checkpoint):
    """Paths that differ across a committed transition, endpoint to endpoint.

    Two revisions, never one.  ``git diff <rev>`` compares ``<rev>`` with the
    *working tree*; passing both endpoints is what makes the answer a property
    of history rather than of the moment the suite happens to run.

    Takes the repository as an argument so the regression below can drive this
    exact body against a replayed history instead of restating its logic.
    """
    result = subprocess.run(
        ["git", "diff", "--name-only", baseline, checkpoint],
        cwd=repository, capture_output=True, text=True)
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return frozenset(line for line in result.stdout.split("\n") if line)




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



def corpus_text():
    """The Phase 4F-B3B candidate corpus, serialized for token scans."""
    return json.dumps(load_corpus(), ensure_ascii=False)


def load_corpus():
    """The corpus Phase 4F-B3B produced.

    Phase 4F-C2 implemented the example specification locked by Phase
    4F-C1C.  Every claim in this suite is about the B3B candidate, so that
    later approved work is reverted here.  The revert is keyed on the
    adjudicated final text, so an example edit C1C did not lock still reaches
    every guard below.

    Phase 4F-E1 later recorded the tier-2 acceptances this suite proves
    absent.  That approved governance work is reverted first, on the same
    terms: only the exact approved event objects are recognised.
    """
    return without_phase_4fc2_examples(
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
    """The private context as Phase 4F-B3B left it."""
    return without_phase_4fc2_actor(
        E1.without_phase_4fe1_actors(
            F2.without_phase_4ff2_reviewer(
                H2.without_phase_4fh2_context(
                    H21.without_phase_4fh21_context(live_context_document())))))


def load_baseline_corpus():
    return json.loads(git_blob("editorial/verb-pattern-candidates.json"))


def build_context():
    document = load_context_document()
    return ValidationContext(
        source_registry=document["sourceRegistry"],
        reviewer_registry=document["reviewerRegistry"],
        author_registry=document["authorRegistry"],
        allocation_registry=document["allocationRegistry"],
        editorial_actor_registry=document["editorialActorRegistry"],
        repository_index=repository_index(),
        today=date.fromisoformat(INSPECTED_ON),
    )


def iter_patterns(corpus):
    for lemma in corpus["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                yield lemma, meaning, pattern


def patterns_by_id(corpus):
    return {p["id"]: p for _, _, p in iter_patterns(corpus)}


def triples_by_id(corpus):
    return {p["id"]: (l, m, p) for l, m, p in iter_patterns(corpus)}


def adjudication_rows():
    with MATRIX.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def row_pattern_ids():
    return {row["reviewId"]: row["patternId"] for row in adjudication_rows()}


def changed_fields(before, after):
    return {key for key in set(before) | set(after)
            if before.get(key) != after.get(key)}


def dative_complement(pattern):
    matched = [c for c in pattern["complements"]
               if c.get("case") == "dative" and c["role"] == "recipient"]
    assert len(matched) == 1, pattern["id"]
    return matched[0]


# ---------------------------------------------------------------------------
# 1.  The B3A plan the implementation claims to follow
# ---------------------------------------------------------------------------

class AdjudicationPlanTests(unittest.TestCase):

    def test_matrix_has_forty_five_rows_with_unique_ids(self):
        rows = adjudication_rows()
        self.assertEqual(PATTERN_COUNT, len(rows))
        self.assertEqual(PATTERN_COUNT, len({r["reviewId"] for r in rows}))

    def test_disposition_counts_match_the_approved_plan(self):
        counts = {}
        for row in adjudication_rows():
            counts[row["b3aDisposition"]] = (
                counts.get(row["b3aDisposition"], 0) + 1)
        self.assertEqual(EXPECTED_DISPOSITIONS, counts)

    def test_no_row_is_deferred(self):
        self.assertEqual([], [r["reviewId"] for r in adjudication_rows()
                              if "DEFER" in r["b3aDisposition"]])

    def test_change_rows_are_exactly_the_five_named_rows(self):
        change = tuple(sorted(
            r["reviewId"] for r in adjudication_rows()
            if r["b3aDisposition"] == "CHANGE BEFORE EDITORIAL ACCEPTANCE"))
        self.assertEqual(APPROVED_CHANGE_ROWS, change)

    def test_change_rows_resolve_to_the_five_named_patterns(self):
        mapping = row_pattern_ids()
        self.assertEqual(set(APPROVED_FIELDS),
                         {mapping[row] for row in APPROVED_CHANGE_ROWS})

    def test_every_matrix_row_names_a_pattern_that_exists(self):
        index = patterns_by_id(load_corpus())
        for review_id, pattern_id in row_pattern_ids().items():
            self.assertIn(pattern_id, index, review_id)


# ---------------------------------------------------------------------------
# 2.  Exact field-level diff against the pinned baseline
# ---------------------------------------------------------------------------

class BaselineFieldDiffTests(unittest.TestCase):

    def setUp(self):
        self.baseline = load_baseline_corpus()
        self.current = load_corpus()
        self.before = patterns_by_id(self.baseline)
        self.after = patterns_by_id(self.current)

    def test_baseline_commit_and_tree_are_the_pinned_ones(self):
        self.assertEqual(
            BASELINE_TREE,
            git("rev-parse", f"{BASELINE_COMMIT}^{{tree}}").stdout.strip())

    def test_baseline_differs_from_the_working_tree(self):
        """Guard against a vacuous self-comparison."""
        self.assertNotEqual(
            json.loads(git_blob("editorial/verb-pattern-candidates.json")),
            load_corpus())

    def test_pattern_count_is_unchanged(self):
        self.assertEqual(PATTERN_COUNT, len(self.before))
        self.assertEqual(PATTERN_COUNT, len(self.after))

    def test_exactly_the_five_approved_rows_differ(self):
        differing = {pid for pid in self.before
                     if self.before[pid] != self.after[pid]}
        self.assertEqual(set(APPROVED_FIELDS), differing)

    def test_only_approved_fields_moved_on_each_changed_row(self):
        for pattern_id, allowed in APPROVED_FIELDS.items():
            moved = changed_fields(self.before[pattern_id],
                                   self.after[pattern_id])
            self.assertEqual(allowed, moved, pattern_id)

    def test_pattern_ids_are_unchanged(self):
        self.assertEqual(sorted(self.before), sorted(self.after))

    def test_meaning_and_lemma_ids_are_unchanged(self):
        def ids(corpus):
            return sorted((l["id"], m["id"], p["id"])
                          for l, m, p in iter_patterns(corpus))
        self.assertEqual(ids(self.baseline), ids(self.current))

    def test_meanings_are_unchanged_including_internal_scope(self):
        def meanings(corpus):
            return sorted((m["id"], m["key"], tuple(m["glossesEn"]),
                           m["internalScope"])
                          for l in corpus["lemmas"] for m in l["meanings"])
        self.assertEqual(meanings(self.baseline), meanings(self.current))

    def test_pattern_keys_are_unchanged(self):
        for pattern_id, before in self.before.items():
            self.assertEqual(before["key"], self.after[pattern_id]["key"])

    def test_evidence_is_unchanged_everywhere(self):
        for pattern_id, before in self.before.items():
            self.assertEqual(before["evidence"],
                             self.after[pattern_id]["evidence"], pattern_id)

    def test_examples_are_unchanged_everywhere(self):
        for pattern_id, before in self.before.items():
            self.assertEqual(before.get("examples"),
                             self.after[pattern_id].get("examples"), pattern_id)

    def test_content_refs_are_unchanged_everywhere(self):
        for pattern_id, before in self.before.items():
            self.assertEqual(before.get("contentRefs"),
                             self.after[pattern_id].get("contentRefs"),
                             pattern_id)

    def test_error_notes_are_unchanged_everywhere(self):
        for pattern_id, before in self.before.items():
            self.assertEqual(before.get("errorNotes"),
                             self.after[pattern_id].get("errorNotes"),
                             pattern_id)

    def test_activity_eligibility_is_unchanged_everywhere(self):
        for pattern_id, before in self.before.items():
            self.assertEqual(before.get("activityEligibility"),
                             self.after[pattern_id].get("activityEligibility"),
                             pattern_id)

    def test_release_mode_is_unchanged_everywhere(self):
        for pattern_id, before in self.before.items():
            self.assertEqual(before.get("releaseMode"),
                             self.after[pattern_id].get("releaseMode"),
                             pattern_id)

    def test_relation_type_and_usage_are_unchanged_everywhere(self):
        for pattern_id, before in self.before.items():
            self.assertEqual(before["relationType"],
                             self.after[pattern_id]["relationType"], pattern_id)
            self.assertEqual(before["usage"],
                             self.after[pattern_id]["usage"], pattern_id)

    def test_complements_moved_only_on_the_two_refreshed_rows(self):
        moved = {pid for pid, before in self.before.items()
                 if before["complements"] != self.after[pid]["complements"]}
        self.assertEqual(set(REFRESHED_ROWS), moved)

    def test_review_state_is_unchanged_everywhere(self):
        for pattern_id, before in self.before.items():
            self.assertEqual(before["reviewState"],
                             self.after[pattern_id]["reviewState"], pattern_id)

    def test_review_events_moved_only_on_the_two_refreshed_rows(self):
        moved = {pid for pid, before in self.before.items()
                 if before["reviewEvents"] != self.after[pid]["reviewEvents"]}
        self.assertEqual(set(REFRESHED_ROWS), moved)

    def test_corpus_envelope_is_unchanged(self):
        for key in ("artifactStatus", "formatVersion"):
            self.assertEqual(self.baseline[key], self.current[key])

    def changed_across_the_b3b_transition(self):
        """The B3B transition, both endpoints named.

        Phase 4F-C1.1: this used to be a one-revision diff against the working
        tree, so it answered "what differs from the B3B baseline *now*" -- a
        question whose answer legitimately grows every time a later phase adds
        a file.  B3B's footprint is history and cannot grow, so both endpoints
        are named and the working tree is not consulted.
        """
        return transition_footprint(ROOT, BASELINE_COMMIT, B3B_CHECKPOINT)

    def test_the_checkpoint_is_the_commit_b3b_produced(self):
        """The transition is one commit, so the endpoints cannot be mismatched."""
        parents = git("rev-list", "--parents", "-n", "1",
                      B3B_CHECKPOINT).stdout.split()
        self.assertEqual([B3B_CHECKPOINT, BASELINE_COMMIT], parents)

    def test_nothing_outside_the_b3b_footprint_differs_from_baseline(self):
        """Exact, in both directions, because history is fixed and known.

        The superseded form could only assert containment plus the modified
        subset, because the working-tree side of its comparison was not
        knowable in advance.  Naming both endpoints makes the answer a
        constant, so the guard is now an equality -- strictly stronger, and
        indifferent to anything a later phase commits on top.
        """
        self.assertEqual(B3B_FOOTPRINT, self.changed_across_the_b3b_transition())

    def test_the_corpus_is_the_only_canonical_content_file_changed(self):
        for path in sorted(self.changed_across_the_b3b_transition()):
            if path.startswith(("tests/", "reports/")):
                continue
            self.assertEqual("editorial/verb-pattern-candidates.json", path)

    def test_the_added_files_exist_on_disk_in_either_state(self):
        for name in B3B_ADDED_FILES:
            self.assertTrue((ROOT / name).is_file(), name)


# ---------------------------------------------------------------------------
# 3.  The five corrections, field by field
# ---------------------------------------------------------------------------

class ImplementedCorrectionTests(unittest.TestCase):

    def setUp(self):
        self.before = patterns_by_id(load_baseline_corpus())
        self.after = patterns_by_id(load_corpus())

    # -- P7-NR-005 ---------------------------------------------------------

    def test_sluchac_illustration_is_affirmative(self):
        text = self.after[SLUCHAC]["learnerExplanationEn"]
        self.assertEqual(
            "In the obey sense słuchać still takes the Genitive: "
            "dziecko słucha mamy.", text)
        self.assertNotIn("nie ", text)

    def test_sluchac_illustration_is_case_transparent(self):
        """'mamy' is Genitive and distinct from Accusative 'mamę'."""
        text = self.after[SLUCHAC]["learnerExplanationEn"]
        self.assertIn("słucha mamy", text)
        self.assertNotIn("rodziców", text)

    def test_sluchac_keeps_every_other_field(self):
        before, after = self.before[SLUCHAC], self.after[SLUCHAC]
        self.assertEqual("recognition-only", after["teachingStatus"])
        self.assertEqual({"recognition": "B1"}, after["cefr"])
        self.assertEqual(before["relationType"], after["relationType"])
        self.assertEqual(before["complements"], after["complements"])
        self.assertEqual(before["evidence"], after["evidence"])
        self.assertEqual(before["reviewEvents"], after["reviewEvents"])

    # -- P7-NR-029 ---------------------------------------------------------

    def test_mowic_accusative_recipient_is_optional(self):
        self.assertIs(False, dative_complement(self.after[MOWIC_ACC])["required"])

    def test_mowic_accusative_content_stays_required(self):
        content = [c for c in self.after[MOWIC_ACC]["complements"]
                   if c["role"] == "content"]
        self.assertEqual(1, len(content))
        self.assertEqual("accusative", content[0]["case"])
        self.assertIs(True, content[0]["required"])

    def test_mowic_accusative_explanation_states_the_optionality(self):
        text = self.after[MOWIC_ACC]["learnerExplanationEn"]
        self.assertEqual(
            "The thing told is Accusative and the person told is Dative; "
            "the person can be left out: mówię prawdę.", text)
        self.assertIn("Accusative", text)
        self.assertIn("Dative", text)
        self.assertIn("mówię prawdę", text)

    def test_mowic_accusative_keeps_its_other_fields(self):
        before, after = self.before[MOWIC_ACC], self.after[MOWIC_ACC]
        self.assertEqual(before["cefr"], after["cefr"])
        self.assertEqual(before["teachingStatus"], after["teachingStatus"])
        self.assertEqual(before["relationType"], after["relationType"])
        self.assertEqual(before["evidence"], after["evidence"])

    # -- P7-NR-030 ---------------------------------------------------------

    def test_mowic_clause_recipient_is_optional(self):
        self.assertIs(False, dative_complement(self.after[MOWIC_ZE])["required"])

    def test_mowic_clause_complement_stays_required(self):
        clause = [c for c in self.after[MOWIC_ZE]["complements"]
                  if c["type"] == "clause"]
        self.assertEqual(1, len(clause))
        self.assertIs(True, clause[0]["required"])

    def test_mowic_clause_explanation_states_the_optionality(self):
        text = self.after[MOWIC_ZE]["learnerExplanationEn"]
        self.assertEqual(
            "The same meaning with clause content: że introduces what is "
            "said, and the person, if named, is Dative: mówię, że to prawda.",
            text)
        self.assertIn("mówię, że to prawda", text)

    def test_clause_kind_is_untouched_and_renders_with_its_diacritic(self):
        """B2's diacritic complaint was rejected; the enum key stays ASCII."""
        clause = [c for c in self.after[MOWIC_ZE]["complements"]
                  if c["type"] == "clause"]
        self.assertEqual("ze", clause[0]["clauseKind"])
        self.assertEqual(
            self.before[MOWIC_ZE]["complements"][1]["clauseKind"],
            clause[0]["clauseKind"])
        source = (ROOT / "pp-verb-patterns.js").read_text(encoding="utf-8")
        self.assertIn('ze: "że …"', source)

    def test_no_replacement_pattern_was_invented_for_either_mowic_row(self):
        self.assertEqual(PATTERN_COUNT, len(self.after))
        self.assertEqual(
            len([p for p in self.before if "mowic" in p]),
            len([p for p in self.after if "mowic" in p]))

    # -- P7-NR-037 ---------------------------------------------------------

    def test_podobac_sie_is_promoted_to_active_production(self):
        after = self.after[PODOBAC]
        self.assertEqual("active-production", after["teachingStatus"])
        self.assertEqual({"recognition": "A2", "production": "A2"},
                         after["cefr"])

    def test_podobac_sie_keeps_meaning_shape_and_roles(self):
        before, after = self.before[PODOBAC], self.after[PODOBAC]
        self.assertEqual("subject-experiencer", after["relationType"])
        self.assertEqual(before["complements"], after["complements"])
        self.assertEqual(before["learnerExplanationEn"],
                         after["learnerExplanationEn"])
        self.assertEqual(before["evidence"], after["evidence"])
        self.assertEqual(before["reviewEvents"], after["reviewEvents"])

    # -- P7-NR-040 ---------------------------------------------------------

    def test_wierzyc_w_is_promoted_to_active_production(self):
        after = self.after[WIERZYC_W]
        self.assertEqual("active-production", after["teachingStatus"])
        self.assertEqual({"recognition": "B1", "production": "B1"},
                         after["cefr"])

    def test_wierzyc_dative_sibling_is_untouched(self):
        """The sibling was already active-production; that asymmetry is what
        promoting w + Accusative removes.  It must not be re-tuned in response.
        """
        sibling = "vp-p-wierzyc-have-trust-dative-object-f38bb3e72123"
        self.assertEqual(self.before[sibling], self.after[sibling])
        self.assertEqual("active-production",
                         self.after[sibling]["teachingStatus"])
        self.assertEqual({"recognition": "A2", "production": "B1"},
                         self.after[sibling]["cefr"])

    # -- teaching-status accounting ----------------------------------------

    def test_exactly_two_patterns_gained_active_production(self):
        promoted = {pid for pid in self.before
                    if self.before[pid]["teachingStatus"] != "active-production"
                    and self.after[pid]["teachingStatus"] == "active-production"}
        self.assertEqual({PODOBAC, WIERZYC_W}, promoted)

    def test_no_pattern_was_demoted(self):
        demoted = {pid for pid in self.before
                   if self.before[pid]["teachingStatus"] == "active-production"
                   and self.after[pid]["teachingStatus"] != "active-production"}
        self.assertEqual(set(), demoted)

    def test_promotion_did_not_enable_any_exercise(self):
        """teachingStatus is not an activity-eligibility derivation."""
        for pattern_id in (PODOBAC, WIERZYC_W):
            self.assertEqual([], self.after[pattern_id]["activityEligibility"])
        self.assertEqual({()}, {tuple(p.get("activityEligibility") or [])
                                for p in self.after.values()})


# ---------------------------------------------------------------------------
# 4.  Scope boundaries, proved through the tooling rather than asserted
# ---------------------------------------------------------------------------

class ScopeBoundaryTests(unittest.TestCase):

    def setUp(self):
        self.baseline = triples_by_id(load_baseline_corpus())
        self.current = triples_by_id(load_corpus())

    def digest(self, source, pattern_id, stage):
        return review_scope_digest(stage, *source[pattern_id])

    def test_tier_one_moved_on_exactly_the_two_refreshed_rows(self):
        moved = {pid for pid in self.baseline
                 if self.digest(self.baseline, pid, "reference-verification")
                 != self.digest(self.current, pid, "reference-verification")}
        self.assertEqual(set(REFRESHED_ROWS), moved)

    def test_tier_two_moved_on_exactly_the_five_approved_rows(self):
        moved = {pid for pid in self.baseline
                 if self.digest(self.baseline, pid, "editorial-review")
                 != self.digest(self.current, pid, "editorial-review")}
        self.assertEqual(set(APPROVED_FIELDS), moved)

    def test_the_three_editorial_only_rows_left_tier_one_alone(self):
        for pattern_id in (SLUCHAC, PODOBAC, WIERZYC_W):
            self.assertEqual(
                self.digest(self.baseline, pattern_id, "reference-verification"),
                self.digest(self.current, pattern_id, "reference-verification"),
                pattern_id)

    def test_tooling_places_learner_explanation_outside_reference_scope(self):
        lemma, meaning, pattern = self.current[SLUCHAC]
        scope = T.review_scope("reference-verification", lemma, meaning, pattern)
        self.assertNotIn("learnerExplanationEn", scope["pattern"])
        self.assertIn("learnerExplanationEn", T.review_scope(
            "editorial-review", lemma, meaning, pattern)["pattern"])

    def test_tooling_places_teaching_status_and_cefr_outside_reference_scope(
            self):
        lemma, meaning, pattern = self.current[PODOBAC]
        scope = T.review_scope("reference-verification", lemma, meaning, pattern)
        self.assertNotIn("teachingStatus", scope["pattern"])
        self.assertNotIn("cefr", scope["pattern"])

    def test_tooling_places_required_inside_reference_scope(self):
        """The finding that forced the targeted tier-1 refresh."""
        lemma, meaning, pattern = self.current[MOWIC_ACC]
        scope = T.review_scope("reference-verification", lemma, meaning, pattern)
        self.assertIn("required", scope["pattern"]["complements"][0])
        self.assertIn("required",
                      T._project_complement(pattern["complements"][0]))

    def test_reverting_the_optionality_would_move_tier_one_back(self):
        """Non-vacuity: the digest tracks ``required`` specifically."""
        corpus = load_corpus()
        index = patterns_by_id(corpus)
        triples = triples_by_id(corpus)
        for pattern_id in REFRESHED_ROWS:
            dative_complement(index[pattern_id])["required"] = True
            self.assertEqual(
                self.digest(self.baseline, pattern_id,
                            "reference-verification"),
                review_scope_digest("reference-verification",
                                    *triples[pattern_id]),
                pattern_id)


# ---------------------------------------------------------------------------
# 5.  The targeted tier-1 refresh: history preserved, fresh acceptance added
# ---------------------------------------------------------------------------

class ReferenceRefreshTests(unittest.TestCase):

    def setUp(self):
        self.baseline = patterns_by_id(load_baseline_corpus())
        self.corpus = load_corpus()
        self.after = patterns_by_id(self.corpus)

    def test_phase_4fa_wrote_forty_five_acceptances(self):
        events = [event for pattern in self.baseline.values()
                  for event in pattern["reviewEvents"]]
        self.assertEqual(PHASE_4FA_EVENT_COUNT, len(events))
        self.assertEqual({1}, {len(pattern["reviewEvents"])
                               for pattern in self.baseline.values()})

    def test_every_original_acceptance_survives_verbatim(self):
        """No redigesting, no re-dating, no deletion, no note rewriting."""
        for pattern_id, before in self.baseline.items():
            original = before["reviewEvents"]
            self.assertEqual(original,
                             self.after[pattern_id]["reviewEvents"][:1],
                             pattern_id)

    def test_exactly_two_refresh_acceptances_were_appended(self):
        appended = {pid: pattern["reviewEvents"][1:]
                    for pid, pattern in self.after.items()
                    if len(pattern["reviewEvents"]) > 1}
        self.assertEqual(set(REFRESHED_ROWS), set(appended))
        for pattern_id, events in appended.items():
            self.assertEqual(1, len(events), pattern_id)

    def test_the_total_is_forty_seven_not_forty_five(self):
        self.assertEqual(
            CURRENT_EVENT_COUNT,
            sum(len(p["reviewEvents"]) for p in self.after.values()))

    def test_every_event_is_a_nonhuman_reference_acceptance(self):
        for _, _, pattern in iter_patterns(self.corpus):
            for event in pattern["reviewEvents"]:
                self.assertEqual("reference-verification", event["kind"])
                self.assertEqual("accept", event["decision"])
                self.assertEqual(REFERENCE_ACTOR, event["actorRef"])
                self.assertNotIn("reviewerRef", event)

    def test_the_refresh_events_stand_over_the_corrected_scope(self):
        for lemma, meaning, pattern in iter_patterns(self.corpus):
            if pattern["id"] not in REFRESHED_ROWS:
                continue
            refresh = pattern["reviewEvents"][1]
            self.assertEqual(1, refresh["scopeVersion"])
            self.assertEqual(
                review_scope_digest(
                    "reference-verification", lemma, meaning, pattern),
                refresh["scopeDigest"], pattern["id"])

    def test_the_superseded_originals_keep_their_historical_digest(self):
        for lemma, meaning, pattern in iter_patterns(self.corpus):
            if pattern["id"] not in REFRESHED_ROWS:
                continue
            original = pattern["reviewEvents"][0]
            self.assertNotEqual(
                review_scope_digest(
                    "reference-verification", lemma, meaning, pattern),
                original["scopeDigest"], pattern["id"])
            self.assertEqual(
                self.baseline[pattern["id"]]["reviewEvents"][0]["scopeDigest"],
                original["scopeDigest"])

    def test_the_refresh_events_pin_current_contemporary_source_evidence(self):
        for _, _, pattern in iter_patterns(self.corpus):
            if pattern["id"] not in REFRESHED_ROWS:
                continue
            refresh = pattern["reviewEvents"][1]
            by_digest = {evidence_digest(record): record
                         for record in pattern["evidence"]}
            pins = refresh["supportingEvidenceDigests"]
            self.assertTrue(pins)
            self.assertEqual(sorted(set(pins)), pins)
            for pin in pins:
                self.assertIn(pin, by_digest, pattern["id"])
            self.assertTrue(any(
                by_digest[pin]["sourceKind"] in T.CONTEMPORARY_SOURCE_KINDS
                for pin in pins))
            self.assertTrue(any(
                by_digest[pin]["factType"] in T.REFERENCE_PATTERN_FACT_TYPES
                for pin in pins))
            self.assertTrue(any(
                by_digest[pin]["sourceId"] == "wsjp-pan" for pin in pins))

    def test_the_refresh_notes_identify_the_optional_recipient_support(self):
        for _, _, pattern in iter_patterns(self.corpus):
            if pattern["id"] not in REFRESHED_ROWS:
                continue
            note = pattern["reviewEvents"][1]["note"]
            self.assertLessEqual(len(note), 240)
            self.assertIn("(KOMU)", note)
            self.assertIn("4F-B3B.1", note)
            self.assertIn("optional", note)

    def test_the_refresh_did_not_touch_the_evidence_records(self):
        for pattern_id, before in self.baseline.items():
            self.assertEqual(before["evidence"],
                             self.after[pattern_id]["evidence"], pattern_id)

    def test_the_original_note_is_not_reused_for_the_refresh(self):
        for pattern_id in REFRESHED_ROWS:
            events = self.after[pattern_id]["reviewEvents"]
            self.assertNotEqual(events[0]["note"], events[1]["note"])

    def test_review_event_dates_are_nondecreasing(self):
        for _, _, pattern in iter_patterns(self.corpus):
            dates = [event["reviewedAt"] for event in pattern["reviewEvents"]]
            self.assertEqual(sorted(dates), dates, pattern["id"])

    def test_no_actor_was_registered_for_the_refresh(self):
        # Every registry, byte for byte.  ``contextNotice`` is excluded: it is
        # the maintainer-facing prose describing what the context currently
        # holds, and Phase 4F-C2 legitimately extended it when it registered
        # its example-generation actor.  No identity lives there.
        baseline = json.loads(
            git_blob("editorial/priority-7-authoring-context.json"))
        current = load_context_document()
        self.assertEqual(set(baseline), set(current))
        for field in sorted(set(baseline) - {"contextNotice"}):
            with self.subTest(field=field):
                self.assertEqual(baseline[field], current[field])

    def test_the_duplicate_stage_guard_was_not_weakened(self):
        """Re-accepting the identical scope is still refused."""
        corpus = copy.deepcopy(self.corpus)
        index = patterns_by_id(corpus)
        events = index[MOWIC_ACC]["reviewEvents"]
        events.append(copy.deepcopy(events[-1]))
        codes = {issue.code for issue in validate_editorial(
            corpus, build_context())}
        self.assertIn("REVIEW_DUPLICATE_STAGE_ACCEPTANCE", codes)


# ---------------------------------------------------------------------------
# 6.  The temporary invalidation the refresh repaired
# ---------------------------------------------------------------------------

class TemporaryInvalidationTests(unittest.TestCase):
    """The correction alone, without a fresh acceptance, is not viable.

    This is the finding Phase 4F-B3B stopped on, kept executable so the reason
    the refresh exists cannot quietly evaporate.
    """

    def corpus_without_refresh_events(self):
        corpus = load_corpus()
        for _, _, pattern in iter_patterns(corpus):
            if pattern["id"] in REFRESHED_ROWS:
                del pattern["reviewEvents"][1:]
        return corpus

    def test_without_the_refresh_the_two_rows_lose_verification(self):
        issues = validate_editorial(
            self.corpus_without_refresh_events(), build_context())
        self.assertEqual({"REVIEW_STATE_MISMATCH"},
                         {issue.code for issue in issues})
        self.assertEqual(2, len(issues))
        for issue in issues:
            self.assertIn("'research'", issue.message)

    def test_without_the_refresh_exactly_forty_three_stay_current(self):
        corpus = self.corpus_without_refresh_events()
        stale = [pattern["id"] for lemma, meaning, pattern
                 in iter_patterns(corpus)
                 if pattern["reviewEvents"][-1]["scopeDigest"]
                 != review_scope_digest(
                     "reference-verification", lemma, meaning, pattern)]
        self.assertEqual(sorted(REFRESHED_ROWS), sorted(stale))
        self.assertEqual(43, PATTERN_COUNT - len(stale))

    def test_the_learner_explanation_half_alone_never_broke_tier_one(self):
        """Only the ``required`` flip reaches reference scope."""
        corpus = self.corpus_without_refresh_events()
        index = patterns_by_id(corpus)
        for pattern_id in REFRESHED_ROWS:
            dative_complement(index[pattern_id])["required"] = True
        self.assertEqual([], validate_editorial(corpus, build_context()))


# ---------------------------------------------------------------------------
# 7.  The required flag is truthful data, not renderer input
# ---------------------------------------------------------------------------

class RequiredFlagRendererTests(unittest.TestCase):
    """The renderer does not yet consume ``required``.

    That is why flipping the flag is invisible to a learner today, and why the
    adjudication paired it with the learner explanation.  It was never a reason
    to leave the canonical value untruthful -- only the reason the correction
    could not be made without the tier-1 re-verification the flag's scope
    demands, which Phase 4F-B3B.1 performed.
    """

    def setUp(self):
        self.source = (ROOT / "pp-verb-patterns.js").read_text(encoding="utf-8")

    def test_renderer_type_checks_the_required_flag(self):
        self.assertIn('typeof value.required !== "boolean"', self.source)

    def test_renderer_never_branches_on_a_complement_required_flag(self):
        for probe in ("complement.required", ".required ?", "if (value.required",
                      "!complement.required", "required === false",
                      "required === true"):
            self.assertNotIn(probe, self.source, probe)

    def test_required_is_a_closed_schema_key(self):
        self.assertIn('closedKeys(value, ["type", "required", "role"]',
                      self.source)

    def test_exactly_two_complements_are_now_optional(self):
        flags = [(pattern["id"], complement["required"])
                 for _, _, pattern in iter_patterns(load_corpus())
                 for complement in pattern["complements"]]
        self.assertEqual(54, len(flags))
        optional = sorted({pid for pid, required in flags if not required})
        self.assertEqual(sorted(REFRESHED_ROWS), optional)
        self.assertEqual(52, sum(1 for _, required in flags if required))

    def test_the_baseline_had_no_optional_complement_at_all(self):
        flags = [complement["required"]
                 for _, _, pattern in iter_patterns(load_baseline_corpus())
                 for complement in pattern["complements"]]
        self.assertEqual(54, len(flags))
        self.assertTrue(all(flags))


# ---------------------------------------------------------------------------
# 8.  Reference tier stands, and nothing advanced past it
# ---------------------------------------------------------------------------

class ReferenceTierTests(unittest.TestCase):

    def setUp(self):
        self.corpus = load_corpus()

    def test_the_real_validator_reports_no_issue(self):
        self.assertEqual([], validate_editorial(self.corpus, build_context()))

    def test_all_forty_five_patterns_are_reference_verified(self):
        states = [p["reviewState"] for _, _, p in iter_patterns(self.corpus)]
        self.assertEqual(PATTERN_COUNT, len(states))
        self.assertEqual({"reference-verified"}, set(states))

    def test_every_standing_acceptance_covers_the_current_content(self):
        for lemma, meaning, pattern in iter_patterns(self.corpus):
            self.assertEqual(
                review_scope_digest(
                    "reference-verification", lemma, meaning, pattern),
                pattern["reviewEvents"][-1]["scopeDigest"], pattern["id"])

    def test_the_reference_actor_is_unchanged(self):
        actors = {event["actorRef"]
                  for _, _, p in iter_patterns(self.corpus)
                  for event in p["reviewEvents"]}
        self.assertEqual({REFERENCE_ACTOR}, actors)

    def test_release_mode_is_solo_maintainer_everywhere(self):
        modes = {p["releaseMode"] for _, _, p in iter_patterns(self.corpus)}
        self.assertEqual({T.SOLO_MAINTAINER_MODE}, modes)


class NoEditorialAdvancementTests(unittest.TestCase):

    def setUp(self):
        self.corpus = load_corpus()

    def test_every_event_is_a_reference_verification(self):
        kinds = [event["kind"] for _, _, p in iter_patterns(self.corpus)
                 for event in p["reviewEvents"]]
        self.assertEqual(CURRENT_EVENT_COUNT, len(kinds))
        self.assertEqual({"reference-verification"}, set(kinds))

    def test_no_editorial_review_event_exists(self):
        self.assertEqual(0, sum(
            1 for _, _, p in iter_patterns(self.corpus)
            for e in p["reviewEvents"] if e["kind"] == "editorial-review"))

    def test_no_product_approval_event_exists(self):
        self.assertEqual(0, sum(
            1 for _, _, p in iter_patterns(self.corpus)
            for e in p["reviewEvents"] if e["kind"] == "product-approval"))

    def test_no_other_governance_event_kind_was_used(self):
        blob = corpus_text()
        for kind in ("editorial-review", "product-approval",
                     "external-verification", "native-linguistic",
                     "correction", "reopen"):
            self.assertNotIn(f'"{kind}"', blob, kind)

    def test_no_pattern_is_editorial_reviewed_or_approved(self):
        states = {p["reviewState"] for _, _, p in iter_patterns(self.corpus)}
        self.assertNotIn("editorial-reviewed", states)
        self.assertNotIn("approved", states)

    def test_no_editorial_actor_was_registered_for_review(self):
        document = load_context_document()
        baseline = json.loads(
            git_blob("editorial/priority-7-authoring-context.json"))
        self.assertEqual(baseline["editorialActorRegistry"],
                         document["editorialActorRegistry"])
        for actor_id, actor in document["editorialActorRegistry"].items():
            self.assertNotIn("editorial-review", actor.get("roles") or [],
                             actor_id)

    def test_the_reference_actor_holds_the_reference_role(self):
        document = load_context_document()
        actor = document["editorialActorRegistry"][REFERENCE_ACTOR]
        self.assertIn("reference-verification", actor["roles"])
        self.assertIs(False, actor["human"])

    def test_author_registry_is_still_empty(self):
        document = load_context_document()
        self.assertEqual({}, document["authorRegistry"])

    def test_no_release_authorization_or_freeze_artifact_was_created(self):
        self.assertEqual(["artifactStatus", "formatVersion", "lemmas"],
                         sorted(load_corpus().keys()))
        blob = corpus_text()
        for token in ("releaseAuthorization", "patternDataRevision",
                      "freeze", "runtime"):
            self.assertNotIn(token, blob, token)


# ---------------------------------------------------------------------------
# 9.  Example work stays future work
# ---------------------------------------------------------------------------

class ExampleHandoffTests(unittest.TestCase):

    def setUp(self):
        self.mapping = row_pattern_ids()
        self.before = patterns_by_id(load_baseline_corpus())
        self.after = patterns_by_id(load_corpus())

    def test_no_example_changed_anywhere(self):
        for pattern_id, before in self.before.items():
            self.assertEqual(before.get("examples"),
                             self.after[pattern_id].get("examples"), pattern_id)

    def test_the_five_pending_rows_keep_their_future_work_status(self):
        for review_id in PENDING_EXAMPLE_ROWS:
            pattern = self.after[self.mapping[review_id]]
            for example in pattern.get("examples") or []:
                self.assertEqual("repository-reuse", example["origin"]["kind"],
                                 review_id)

    def test_two_pending_rows_are_still_empty_slots(self):
        empty = [r for r in PENDING_EXAMPLE_ROWS
                 if self.after[self.mapping[r]].get("examples") is None]
        self.assertEqual(["P7-NR-042", "P7-NR-044"], empty)

    def test_no_example_is_editorial_generated_yet(self):
        kinds = {example["origin"]["kind"]
                 for _, _, p in iter_patterns(load_corpus())
                 for example in (p.get("examples") or [])}
        self.assertEqual({"repository-reuse"}, kinds)

    def test_example_total_is_unchanged(self):
        total = sum(len(p.get("examples") or [])
                    for _, _, p in iter_patterns(load_corpus()))
        self.assertEqual(23, total)

    def test_b3a_example_findings_are_routed_to_phase_4fc(self):
        rows = {row["reviewId"]: row for row in adjudication_rows()}
        for review_id in B3A_EXAMPLE_FINDINGS:
            self.assertEqual("4F-C", rows[review_id]["ownerPhase"], review_id)
            self.assertEqual("EXAMPLE", rows[review_id]["b3aPrimaryCategory"],
                             review_id)

    def test_the_handoff_list_is_complete_in_the_b3b_report(self):
        text = B3B_SUMMARY.read_text(encoding="utf-8")
        for review_id in PENDING_EXAMPLE_ROWS + B3A_EXAMPLE_FINDINGS:
            self.assertIn(review_id, text)

    def test_the_report_records_every_phase_4fc_owned_row(self):
        text = B3B_SUMMARY.read_text(encoding="utf-8")
        for row in adjudication_rows():
            if row["ownerPhase"] == "4F-C":
                self.assertIn(row["reviewId"], text)

    def test_the_b3a_severity_classification_is_preserved_in_the_report(self):
        """Blocking and nonblocking example work stay distinguishable."""
        text = B3B_SUMMARY.read_text(encoding="utf-8")
        rows = {row["reviewId"]: row for row in adjudication_rows()}
        for review_id in B3A_EXAMPLE_FINDINGS:
            severity = rows[review_id]["b3aSeverity"]
            self.assertIn(severity, {"LOW", "MEDIUM", "HIGH"}, review_id)
            self.assertIn(severity, text)


# ---------------------------------------------------------------------------
# 10.  Shipping boundary, artifact history and the re-pinned guards
# ---------------------------------------------------------------------------

class ShippingBoundaryTests(unittest.TestCase):

    def test_tooling_is_byte_identical_to_baseline(self):
        self.assertEqual(git_blob("priority7_tooling.py"),
                         (ROOT / "priority7_tooling.py").read_text(
                             encoding="utf-8"))

    def test_every_shipping_path_is_byte_identical_to_baseline(self):
        """Compared with the Phase 4F-I1 and 4F-H3 layers removed.

        Two phases have been entitled to change a shipping file since this
        baseline: H3, the UI wording phase, and I1, the atomic release.  Both
        layers are pinned and all-or-nothing, so removing them must reproduce
        these bytes exactly and every other shell or worker edit still fails
        here.  I1 is stripped first because it sits on top of H3.
        """
        for name in SHIPPING_PATHS:
            path = ROOT / name
            if not path.exists():
                continue
            text = i1_shipping_text(name)
            if H3.is_phase_4fh3_path(name):
                text = H3.without_phase_4fh3_ui_wording(text)
            self.assertEqual(git_blob(name), text, name)

    def test_no_runtime_pattern_bundle_was_created(self):
        # Superseded by Priority 7 Phase 4F-I1, the release that materialised
        # the official runtime.  The only document that may occupy that path
        # is exactly the I1 release artifact, pinned by digest and revision,
        # and it may only exist alongside the matching shell and worker.
        self.assertEqual("complete", i1_bundle().state)

    def test_only_editorial_reports_and_tests_were_touched(self):
        """Asserted against the baseline, not against ``git status``.

        ``git status`` goes empty the moment the candidate is committed, which
        would make this guard vacuous in the committed-scratch rehearsal.
        """
        status = git("status", "--porcelain")
        diff = git("diff", "--name-only", BASELINE_COMMIT)
        touched = {line[3:].strip().strip('"')
                   for line in status.stdout.split("\n") if line.strip()}
        touched |= {line for line in diff.stdout.split("\n") if line}
        self.assertTrue(touched, "guard would be vacuous")
        for path in sorted(touched):
            if is_only_the_h3_ui_wording(path) or is_only_the_i1_activation(path):
                continue
            self.assertTrue(
                path.startswith(("editorial/", "reports/", "tests/")), path)


class RePinnedGuardTests(unittest.TestCase):
    """The earlier suites' guards were re-pinned, never relaxed."""

    def test_each_normalising_guard_covers_all_five_approved_rows(self):
        for module_name in NORMALISING_GUARD_MODULES:
            source = (ROOT / "tests" / module_name).read_text(encoding="utf-8")
            self.assertIn("PHASE_4FB3B_APPROVED_EDITS", source, module_name)
            # The revert is conditional on the field holding B3B's exact value.
            self.assertIn("if pattern.get(field) == written:", source,
                          module_name)
            for pattern_id in APPROVED_FIELDS:
                stem = pattern_id.rsplit("-", 1)[0]
                self.assertIn(stem, source, f"{module_name}:{pattern_id}")

    def test_no_guard_widened_its_generic_exclusion_set(self):
        """The four governance keys are the only blanket exclusions."""
        expected = '{"releaseMode", "reviewState", "reviewEvents", "evidence"}'
        for module_name in NORMALISING_GUARD_MODULES:
            source = (ROOT / "tests" / module_name).read_text(encoding="utf-8")
            self.assertIn(expected, source, module_name)
            for widened in ('"teachingStatus"', '"learnerExplanationEn"',
                            '"complements"', '"cefr"'):
                self.assertNotIn(f"{widened},\n" + " " * 8 + '"releaseMode"',
                                 source, module_name)

    def test_each_checkpoint_guard_separates_forty_five_from_forty_seven(self):
        for module_name in CHECKPOINT_GUARD_MODULES:
            source = (ROOT / "tests" / module_name).read_text(encoding="utf-8")
            self.assertIn("PHASE_4FA_EVENT_COUNT", source, module_name)
            self.assertIn("CURRENT_EVENT_COUNT", source, module_name)
            self.assertIn("phase_4fa_review_events", source, module_name)
            # The checkpoint is read from the commit, not restated as 47.
            self.assertIn(BASELINE_COMMIT, source, module_name)

    def test_no_guard_claims_phase_4fa_created_forty_seven_events(self):
        for module_name in CHECKPOINT_GUARD_MODULES:
            source = (ROOT / "tests" / module_name).read_text(encoding="utf-8")
            self.assertNotIn("PHASE_4FA_EVENT_COUNT = 47", source, module_name)
            self.assertIn("PHASE_4FA_EVENT_COUNT = 45", source, module_name)


class CommittedStateGuardRegressionTests(unittest.TestCase):
    """Phase 4F-B3B.2: the later-change guards survive their own commit.

    Two retargeted guards reconstructed the pre-B3B corpus by reading
    ``HEAD``.  That was sound only while the B3B candidate was an uncommitted
    working tree.  Once the candidate is committed, ``HEAD`` contains it, both
    sides of the comparison carry the same edits, and the guard passes whatever
    changed -- an unauthorised sixth edit included.

    This regression drives each suite's own guard body against one isolated
    committed repository, rather than matching source strings, so it fails if
    either suite regresses to a HEAD-relative baseline.
    """

    GUARDED_MODULES = ("test_priority7_phase4e1", "test_priority7_phase5a")
    UNRELATED_PATTERN = "vp-p-szukac-seek-genitive-target-71dc6eff512c"

    @staticmethod
    def load(module_name):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            module_name, ROOT / "tests" / f"{module_name}.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def isolated_repository(self):
        import tempfile
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)

        def run(*arguments):
            return subprocess.run(
                ["git", *arguments], cwd=holder.name, capture_output=True,
                text=True, check=True)

        run("init", "-q")
        run("config", "user.email", "b3b2@example.invalid")
        run("config", "user.name", "b3b2 regression")
        return holder.name, run

    def commit_corpus(self, directory, run, corpus, message):
        (Path(directory) / "corpus.json").write_text(
            json.dumps(corpus, ensure_ascii=False, indent=2), encoding="utf-8")
        run("add", "-A")
        run("commit", "-q", "-m", message)
        return run("rev-parse", "HEAD").stdout.strip()

    def with_sixth_edit(self):
        corpus = load_corpus()
        for _, _, pattern in iter_patterns(corpus):
            if pattern["id"] == self.UNRELATED_PATTERN:
                pattern["learnerExplanationEn"] = "unauthorised sixth"
                return corpus
        self.fail("control pattern not found")

    def build(self, *corpora):
        directory, run = self.isolated_repository()
        shas = [self.commit_corpus(directory, run, corpus, f"step {index}")
                for index, corpus in enumerate(corpora)]
        return directory, shas[0]

    def test_both_suites_pin_the_immutable_b3b_baseline(self):
        for module_name in self.GUARDED_MODULES:
            module = self.load(module_name)
            self.assertEqual(BASELINE_COMMIT, module.PHASE_4FB3B_BASELINE_SHA,
                             module_name)

    def test_both_guards_accept_the_legitimate_committed_candidate(self):
        directory, baseline = self.build(load_baseline_corpus(), load_corpus())
        for module_name in self.GUARDED_MODULES:
            module = self.load(module_name)
            self.assertTrue(module.guard_holds(directory, baseline),
                            module_name)

    def test_both_guards_reject_a_sixth_committed_edit(self):
        directory, baseline = self.build(
            load_baseline_corpus(), load_corpus(), self.with_sixth_edit())
        for module_name in self.GUARDED_MODULES:
            module = self.load(module_name)
            self.assertFalse(module.guard_holds(directory, baseline),
                             module_name)

    def test_the_superseded_head_form_would_have_accepted_it(self):
        """Kept executable so the reason for the repair cannot evaporate."""
        directory, baseline = self.build(
            load_baseline_corpus(), load_corpus(), self.with_sixth_edit())
        for module_name in self.GUARDED_MODULES:
            module = self.load(module_name)
            self.assertTrue(
                module.guard_holds(directory, "HEAD", normalise_baseline=True),
                f"{module_name}: HEAD form should be vacuous")
            self.assertFalse(module.guard_holds(directory, baseline),
                             f"{module_name}: pinned form must catch it")

    def test_both_guards_reject_a_wrong_value_on_an_approved_field(self):
        corpus = load_corpus()
        for _, _, pattern in iter_patterns(corpus):
            if pattern["id"] == PODOBAC:
                pattern["cefr"]["production"] = "B1"
        directory, baseline = self.build(load_baseline_corpus(), corpus)
        for module_name in self.GUARDED_MODULES:
            module = self.load(module_name)
            self.assertFalse(module.guard_holds(directory, baseline),
                             module_name)

    def test_neither_suite_widened_its_governance_exclusions(self):
        for module_name in self.GUARDED_MODULES:
            module = self.load(module_name)
            self.assertEqual(
                frozenset({"releaseMode", "reviewState", "reviewEvents",
                           "evidence"}),
                module.GOVERNANCE_KEYS, module_name)


class HistoricalFootprintRegressionTests(unittest.TestCase):
    """Phase 4F-C1.1: the repaired footprint guard, driven over a real history.

    The repair must satisfy two claims that pull in opposite directions:

    * B3B's transition stays **frozen and exact** -- an unauthorised file
      slipped *inside* the transition is still caught;
    * later phases are **allowed to exist** -- files committed *after* the
      checkpoint cannot change the answer.

    Both are proved by replaying a three-commit history in a throwaway
    repository and calling :func:`transition_footprint` -- the same body the
    real guard calls -- rather than by asserting that a constant equals a
    hardcoded list, which would prove nothing about the comparison itself.
    """

    #: Stands in for anything outside the approved footprint.  A shipping file
    #: is the worst case: B3B was forbidden to touch it at all.
    UNAUTHORISED = "priority7_tooling.py"

    #: Real C1 paths, so the "later phases may exist" claim is the actual one.
    LATER_PHASE_FILES = (
        "reports/priority-7-phase-4fc1-example-matrix.csv",
        "reports/priority-7-phase-4fc1-summary.md",
        "reports/priority-7-phase-4fc1-blind-example-review-input.csv",
        "tests/test_priority7_phase4fc1.py",
    )

    def replay_history(self, *, tamper_inside_transition=False):
        """baseline -> B3B checkpoint -> a later phase, in a scratch repo.

        Returns the two endpoints plus the later-phase head, so a test can ask
        the historical question while HEAD sits well beyond the checkpoint.
        """
        import tempfile
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        directory = Path(holder.name)

        def run(*arguments):
            return subprocess.run(["git", *arguments], cwd=directory,
                                  capture_output=True, text=True, check=True)

        def write(relative, text):
            target = directory / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")

        run("init", "-q")
        run("config", "user.email", "c11@example.invalid")
        run("config", "user.name", "c1.1 regression")

        for name in B3B_MODIFIED_FILES:
            write(name, "before the transition\n")
        write(self.UNAUTHORISED, "shipping file, untouched by B3B\n")
        run("add", "-A")
        run("commit", "-q", "-m", "pre-B3B baseline")
        baseline = run("rev-parse", "HEAD").stdout.strip()

        for name in B3B_MODIFIED_FILES:
            write(name, "after the transition\n")
        for name in B3B_ADDED_FILES:
            write(name, "added by B3B\n")
        if tamper_inside_transition:
            write(self.UNAUTHORISED, "EDITED INSIDE THE B3B TRANSITION\n")
        run("add", "-A")
        run("commit", "-q", "-m", "B3B checkpoint")
        checkpoint = run("rev-parse", "HEAD").stdout.strip()

        for name in self.LATER_PHASE_FILES:
            write(name, "committed by a later phase\n")
        run("add", "-A")
        run("commit", "-q", "-m", "later phase candidate")
        later = run("rev-parse", "HEAD").stdout.strip()

        return directory, baseline, checkpoint, later

    def test_the_replay_reproduces_the_real_approved_footprint(self):
        """Without this the two claims below could both pass vacuously."""
        directory, baseline, checkpoint, _ = self.replay_history()
        self.assertEqual(B3B_FOOTPRINT,
                         transition_footprint(directory, baseline, checkpoint))

    def test_an_unauthorised_file_inside_the_transition_is_caught(self):
        directory, baseline, checkpoint, _ = self.replay_history(
            tamper_inside_transition=True)
        observed = transition_footprint(directory, baseline, checkpoint)
        self.assertNotEqual(B3B_FOOTPRINT, observed)
        self.assertEqual({self.UNAUTHORISED}, set(observed) - B3B_FOOTPRINT)

    def test_later_phase_files_do_not_alter_the_historical_result(self):
        directory, baseline, checkpoint, later = self.replay_history()
        self.assertNotEqual(checkpoint, later)
        # HEAD is four files beyond the checkpoint; the answer is unmoved.
        self.assertEqual(B3B_FOOTPRINT,
                         transition_footprint(directory, baseline, checkpoint))
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=directory,
                              capture_output=True, text=True, check=True)
        self.assertEqual(later, head.stdout.strip())

    def test_later_phase_files_are_still_absent_from_the_footprint(self):
        """The repair must not have been achieved by widening the constant."""
        for name in self.LATER_PHASE_FILES:
            self.assertNotIn(name, B3B_FOOTPRINT, name)
        self.assertEqual(11, len(B3B_FOOTPRINT))

    def test_the_superseded_one_revision_form_forbade_the_later_phase(self):
        """Kept executable so the reason for the repair cannot evaporate.

        ``git diff --name-only <baseline>`` with no second revision is the
        exact expression this phase removed.  Here it is, run against the same
        replayed history, reporting the later phase's four files as violations
        of a footprint frozen two commits earlier.
        """
        directory, baseline, checkpoint, _ = self.replay_history()
        superseded = frozenset(
            line for line in subprocess.run(
                ["git", "diff", "--name-only", baseline], cwd=directory,
                capture_output=True, text=True, check=True
            ).stdout.split("\n") if line)

        self.assertNotEqual(B3B_FOOTPRINT, superseded)
        self.assertEqual(set(self.LATER_PHASE_FILES),
                         set(superseded) - B3B_FOOTPRINT)
        # And the repaired form, on the same repository, is unaffected.
        self.assertEqual(B3B_FOOTPRINT,
                         transition_footprint(directory, baseline, checkpoint))

    def test_the_historical_guard_names_both_endpoints(self):
        """Inspected on the two bodies concerned, not by scanning the file.

        A whole-file scan would both match its own assertion text and flag
        ``test_only_editorial_reports_and_tests_were_touched``, which is a
        *current-state* guard and is supposed to consult the working tree.
        """
        import inspect
        guard = inspect.getsource(
            BaselineFieldDiffTests.changed_across_the_b3b_transition)
        self.assertIn("BASELINE_COMMIT", guard)
        self.assertIn("B3B_CHECKPOINT", guard)

        helper = inspect.getsource(transition_footprint)
        self.assertIn('"--name-only", baseline, checkpoint', helper)

    def test_the_historical_guard_agrees_with_the_shared_helper(self):
        self.assertEqual(
            transition_footprint(ROOT, BASELINE_COMMIT, B3B_CHECKPOINT),
            BaselineFieldDiffTests.changed_across_the_b3b_transition(
                BaselineFieldDiffTests("test_corpus_envelope_is_unchanged")))


class B3AArtifactTests(unittest.TestCase):

    def test_copied_artifacts_are_byte_identical(self):
        for name, expected in B3A_ARTIFACT_SHA256.items():
            blob = (MATRIX.parent / name).read_bytes()
            self.assertEqual(expected, hashlib.sha256(blob).hexdigest(), name)

    def test_both_artifacts_are_present(self):
        self.assertTrue(MATRIX.is_file())
        self.assertTrue(B3A_SUMMARY.is_file())

    def test_the_b3b_report_exists_and_names_its_baseline(self):
        text = B3B_SUMMARY.read_text(encoding="utf-8")
        self.assertIn(BASELINE_COMMIT, text)
        self.assertIn(BASELINE_TREE, text)

    def test_the_report_names_every_approved_row(self):
        text = B3B_SUMMARY.read_text(encoding="utf-8")
        for review_id in APPROVED_CHANGE_ROWS:
            self.assertIn(review_id, text)

    def test_the_report_preserves_the_intermediate_finding(self):
        """§14: the blocker and its resolution both stay on the record.

        Tokens are chosen to survive the report's line wrapping, so this test
        checks that the finding is documented rather than that a sentence was
        phrased a particular way.
        """
        text = B3B_SUMMARY.read_text(encoding="utf-8")
        for token in ("GO WITH CHANGES REQUIRED", "REVIEW_STATE_MISMATCH",
                      "research", "external-verification", "4F-B3B.1",
                      "43", "47"):
            self.assertIn(token, text, token)

    def test_the_report_states_the_final_verdict(self):
        text = B3B_SUMMARY.read_text(encoding="utf-8")
        self.assertIn("**GO**", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
