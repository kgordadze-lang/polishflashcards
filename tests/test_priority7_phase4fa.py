"""Priority 7 Phase 4F-A real-corpus reference verification.

Phase 4E built the solo-maintainer chain and Phase 4E.1 corrected its actor
model, both on synthetic data only.  Phase 4F-A is the first phase to run that
machinery over the real 45-pattern corpus.

**Two kinds of support, one standard.**  The locked specification defines a
pattern as "a complete, meaning-specific learner construction" and states that
"the corpus is selective teaching content, not an exhaustive dictionary".  A
learner pattern may therefore isolate a governed complement that a dictionary's
formal ``Składnia`` row shows alongside further participants.  Verification
accepts two support kinds and no others:

``EXACT-FRAME``
    a printed ``Składnia`` schema directly realises the authored construction.

``SUBFRAME``
    the entry's own ``Definicja``, ``Połączenia`` or ``Cytaty`` realise the
    taught complement, with or without the other participants, even though no
    single ``Składnia`` row matches the authored slot set.

Subframe support is authoritative-usage support.  It is never model intuition,
and it never licenses arbitrary slot deletion: participant structure, case and
preposition government still require evidence from the entry itself.

The properties under test:

* the outcome is the audited one -- 45 verified, 41 on exact-frame support and
  4 on subframe support, and zero rows advanced past tier 1;
* each row's ``reference-verified`` state is **derived** by the tooling from its
  events, scope digests and evidence, not asserted by the corpus;
* every acceptance is borne by the registered nonhuman actor, never a person;
* the four subframe rows carry evidence that names the section supporting them,
  and does not claim a Składnia row that does not exist;
* Phase 4F-A wrote governance and re-inspected evidence, and changed no
  linguistic content, no learner-facing treatment, no example and no shipping
  file -- and did not touch the governance tooling it ran under;
* the published audit matrix agrees with the corpus row by row.

Every mutation below is applied to an in-memory copy.  Nothing here writes to
the corpus, the context, the tooling or any shipping file.
"""

from __future__ import annotations

import collections
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
from priority7_tooling import (  # noqa: E402
    HUMAN_REVIEWED_MODE,
    SOLO_MAINTAINER_MODE,
    ValidationContext,
    evidence_digest,
    review_scope_digest,
    validate_editorial,
)

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

CORPUS = ROOT / "editorial" / "verb-pattern-candidates.json"
CONTEXT_FILE = ROOT / "editorial" / "priority-7-authoring-context.json"
PUBLIC_RUNTIME = ROOT / "content" / "verb-patterns.json"
MATRIX = ROOT / "reports" / "priority-7-phase-4fa-reference-matrix.csv"
SUMMARY = ROOT / "reports" / "priority-7-phase-4fa-summary.md"
SPEC = ROOT / "reports" / "priority-7-pattern-data-specification.md"

#: The day the reference workflow ran and every WSJP locator was re-opened.
INSPECTED_ON = "2026-08-14"
#: The day the Phase 2B evidence set was compiled.  Sources this phase could not
#: re-open -- the Mędak demo PDF and the repository corpus -- keep it.
COMPILED_ON = "2026-08-09"
REFERENCE_ACTOR = "priority7-reference-analysis"

EXACT_FRAME = "EXACT-FRAME"
SUBFRAME = "SUBFRAME"

#: The four rows accepted on subframe support, and the section of the entry that
#: supplies it.  The token must appear in the row's own WSJP evidence note, so
#: this mapping cannot be satisfied by a note that merely says "verified".
SUBFRAME_SUPPORT = {
    # bare Dative recipient is its own Polaczenia collocation class
    "vp-p-pomagac-assist-dative-recipient-9f0a375c5e81": "Polaczenia",
    # the sense definition itself realises 'za cos' with no recipient
    "vp-p-dziekowac-thank-za-accusative-reason-fd31baa1b1ad": "definition",
    # the sense's citations realise the Accusative person and the o request together
    "vp-p-prosic-request-accusative-person-o-accusative-thing-b7a8d9ce1a99": "Cytaty",
    # Polaczenia realises the o phrase with the addressee omitted
    "vp-p-pytac-ask-for-information-o-accusative-topic-c89674d989d8": "Polaczenia",
}

STAGE_KINDS_NOT_RUN = (
    "editorial-review", "product-approval", "external-verification",
    "native-linguistic", "correction", "reopen",
)

#: The subset of the above that no later phase has run either.  Phase 4F-E1
#: performed ``editorial-review`` and Phase 4F-F2 the human
#: ``product-approval``; everything else here is still absent from the live
#: corpus and is swept there directly.  A stage leaves this tuple only when an
#: authorised phase actually performs it, never to make a suite pass.
STAGE_KINDS_NEVER_RUN = tuple(
    kind for kind in STAGE_KINDS_NOT_RUN
    if kind not in {"editorial-review", "product-approval"})

#: Evidence accounting, recomputed from the repaired corpus.  Phase 4F-A added
#: and deleted nothing: it re-dated what it re-opened and rewrote notes.
EVIDENCE_TOTAL = 122
WSJP_RECORDS = 46
WSJP_DISTINCT_ENTRY_SENSE_URLS = 34
NOTE_REWRITES = 8

_REPOSITORY_INDEX = None

PRIORITY7_ACTOR_IDS = frozenset({
    "priority7-reference-analysis", "priority7-editorial-review",
    "priority7-editorial-corroboration", "priority7-example-generation",
})


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


def priority7_actors(registry):
    return {key: value for key, value in registry.items()
            if key in PRIORITY7_ACTOR_IDS}


def repository_index():
    """Build the repository index once; it is read-only and identical per run."""
    global _REPOSITORY_INDEX
    if _REPOSITORY_INDEX is None:
        _REPOSITORY_INDEX = T.repository_index_from_root(ROOT)
    return _REPOSITORY_INDEX


def live_corpus():
    """The corpus exactly as it stands, with no normalisation at all."""
    return json.loads(CORPUS.read_text(encoding="utf-8"))


def live_context_document():
    return json.loads(CONTEXT_FILE.read_text(encoding="utf-8"))


def load_corpus():
    # Phase 4F-E1 recorded the tier-2 editorial acceptances this suite was
    # written to prove absent.  That approved governance work is reverted
    # here so every Phase 4F-A claim below still means what it meant when it
    # was written; an event that differs anywhere survives and still fails.
    return E1.without_phase_4fe1_editorial_review(
        F2.without_phase_4ff2_product_approval(
            H2.without_phase_4fh2_content_completion(
                H21.without_phase_4fh21_product_reapproval(live_corpus()))))


def load_context_document():
    return E1.without_phase_4fe1_actors(
        F2.without_phase_4ff2_reviewer(
            H2.without_phase_4fh2_context(
                H21.without_phase_4fh21_context(live_context_document()))))


def build_context(document=None, *, actors=None, reviewers=None):
    document = document or load_context_document()
    return ValidationContext(
        source_registry=document["sourceRegistry"],
        reviewer_registry=(document["reviewerRegistry"] if reviewers is None
                           else reviewers),
        author_registry=document["authorRegistry"],
        allocation_registry=document["allocationRegistry"],
        editorial_actor_registry=(document["editorialActorRegistry"]
                                  if actors is None else actors),
        repository_index=repository_index(),
        # Pinned to the inspection day so the suite neither drifts with the
        # clock nor silently accepts a future-dated record.
        today=date.fromisoformat(INSPECTED_ON),
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


def wsjp_records(pattern):
    return [record for record in pattern["evidence"]
            if record["sourceId"] == "wsjp-pan"]


def codes(issues):
    return {issue.code for issue in issues}


def git(*arguments):
    return subprocess.run(["git", *arguments], cwd=ROOT,
                          capture_output=True, text=True)


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


#: The commit Phase 4F-A started from.  Pinned by SHA rather than resolved as
#: ``HEAD`` so every baseline comparison below means the same thing before and
#: after this candidate is committed: once committed, ``HEAD`` *is* the phase's
#: own work, and a baseline test written against it silently compares the file
#: to itself.  The committed-scratch gate caught exactly that.
BASELINE_COMMIT = "681ff69a191ccc6d61f73eccb21248703e1ac9d5"


def baseline_corpus():
    result = git("show", f"{BASELINE_COMMIT}:editorial/verb-pattern-candidates.json")
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


GOVERNANCE_KEYS = frozenset(
    {"releaseMode", "reviewState", "reviewEvents", "evidence"})


def linguistic_projection(corpus):
    """Everything Phase 4F-A was not entitled to touch."""
    return [
        {"lemma": {k: v for k, v in lemma.items() if k != "meanings"},
         "meaning": {k: v for k, v in meaning.items() if k != "patterns"},
         "pattern": {k: v for k, v in pattern.items()
                     if k not in GOVERNANCE_KEYS}}
        for lemma, meaning, pattern in iter_patterns(corpus)]


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



# --------------------------------------------------------------------------
# Phase 4F-B3B.1 tier-1 reference refresh
#
# Phase 4F-B3B corrected the recipient Dative on the two `mówić` rows from
# required to optional.  ``complements[].required`` sits inside the tier-1
# reference scope, so that correction retired those two Phase 4F-A
# acceptances.  Phase 4F-B3B.1 re-opened the WSJP Składnia, confirmed the
# parenthesised KOMU on both frames, and appended one fresh reference
# verification to each.  It rewrote none of the original 45.
#
# Two distinct facts follow, and the tests below keep them apart:
#   * what Phase 4F-A created -- 45 acceptances, read back from the commit
#     that phase produced rather than restated as a bare number;
#   * what stands now -- 47, the original 45 preserved as a prefix plus the
#     two refreshes.
# Asserting 47 as "Phase 4F-A's inventory" would rewrite history; asserting 45
# as the current total would deny the refresh.  Both are wrong, so neither is
# written below.
# --------------------------------------------------------------------------

#: The commit Phase 4F-A produced; its review history is the checkpoint.
PHASE_4FA_CHECKPOINT_COMMIT = "7beb50d7b3463d7745352f1608f1e30019529fdf"

#: pattern id -> fresh tier-1 acceptances appended by Phase 4F-B3B.1.
PHASE_4FB3B1_REFRESHED = {
    "vp-p-mowic-tell-content-dative-recipient-accusative-content"
    "-2f2b1add1960": 1,
    "vp-p-mowic-tell-content-dative-recipient-ze-clause-a01ddc4a4736": 1,
}

#: Acceptances Phase 4F-A itself wrote, and the total standing after refresh.
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


class Phase4FATestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.corpus = load_corpus()
        cls.document = load_context_document()
        cls.patterns = [pattern for _, _, pattern in iter_patterns(cls.corpus)]

    def mutated(self):
        return copy.deepcopy(self.corpus)


# --------------------------------------------------------------------------
# §1  the locked architecture the subframe adjudication rests on
# --------------------------------------------------------------------------

class LearnerSubframeArchitecture(Phase4FATestCase):
    """The adjudication is read from the locked specification, not assumed."""

    def test_the_specification_defines_a_pattern_as_a_learner_construction(self):
        spec = SPEC.read_text(encoding="utf-8")
        self.assertIn(
            "A pattern is a complete, meaning-specific learner construction",
            spec)

    def test_the_specification_says_the_corpus_is_selective_not_exhaustive(self):
        spec = " ".join(SPEC.read_text(encoding="utf-8").split())
        self.assertIn(
            "The corpus is selective teaching content, not an exhaustive "
            "dictionary.", spec)

    def test_the_summary_states_both_support_kinds_and_their_limit(self):
        summary = " ".join(
            SUMMARY.read_text(encoding="utf-8").replace("*", "").split())
        for phrase in ("EXACT-FRAME", "SUBFRAME",
                       "never licenses inferring a frame from model intuition"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, summary)


# --------------------------------------------------------------------------
# §2  the audited outcome, stated exactly
# --------------------------------------------------------------------------

class AuditedOutcome(Phase4FATestCase):

    def test_the_corpus_validates_as_written(self):
        # Stated over the Phase 4F-C2 example work reverted, because this
        # suite deliberately pins ``today`` to the Phase 4F-A inspection day
        # and a later phase's honest ``adoptedAt`` is in that pinned future.
        self.assertEqual([], validate_editorial(
            without_phase_4fc2_examples(self.corpus), build_context()))

    def test_the_inventory_is_unchanged_and_every_row_is_verified(self):
        corpus = priority7_corpus(self.corpus)
        patterns = [pattern for _, _, pattern in iter_patterns(corpus)]
        self.assertEqual(30, len(corpus["lemmas"]))
        self.assertEqual(
            34, sum(len(lemma["meanings"]) for lemma in corpus["lemmas"]))
        self.assertEqual(45, len(patterns))
        self.assertEqual(
            {"reference-verified": 45},
            dict(collections.Counter(
                pattern["reviewState"] for pattern in patterns)))

    def test_no_pattern_remains_at_research(self):
        self.assertEqual(
            [], [pattern["id"] for pattern in self.patterns
                 if pattern["reviewState"] == "research"])

    def test_every_intended_pattern_declares_the_solo_maintainer_mode(self):
        self.assertEqual(
            {SOLO_MAINTAINER_MODE},
            {pattern["releaseMode"] for pattern in self.patterns})

    def test_phase_4fa_wrote_exactly_forty_five_reference_acceptances(self):
        """The checkpoint, read from the commit Phase 4F-A produced."""
        checkpoint = phase_4fa_review_events()
        events = [event for history in checkpoint.values()
                  for event in history]
        self.assertEqual(PHASE_4FA_EVENT_COUNT, len(events))
        self.assertEqual({("reference-verification", "accept")},
                         {(event["kind"], event["decision"])
                          for event in events})
        self.assertEqual(
            {1}, {len(history) for history in checkpoint.values()},
            "exactly one acceptance per pattern, per review round")

    def test_the_phase_4fa_acceptances_survive_verbatim(self):
        """Phase 4F-B3B.1 appended; it rewrote, redigested and deleted nothing."""
        checkpoint = phase_4fa_review_events()
        for pattern in self.patterns:
            original = checkpoint[pattern["id"]]
            self.assertEqual(original,
                             pattern["reviewEvents"][:len(original)],
                             pattern["id"])

    def test_only_the_two_refreshed_rows_gained_an_acceptance(self):
        checkpoint = phase_4fa_review_events()
        appended = {
            pattern["id"]: len(pattern["reviewEvents"]) - len(
                checkpoint[pattern["id"]])
            for pattern in self.patterns}
        self.assertEqual(PHASE_4FB3B1_REFRESHED,
                         {pid: n for pid, n in appended.items() if n})
        self.assertEqual(
            CURRENT_EVENT_COUNT,
            sum(len(pattern["reviewEvents"]) for pattern in self.patterns))

    def test_every_current_event_is_still_a_reference_acceptance(self):
        events = [event for pattern in self.patterns
                  for event in pattern["reviewEvents"]]
        self.assertEqual(CURRENT_EVENT_COUNT, len(events))
        self.assertEqual({("reference-verification", "accept")},
                         {(event["kind"], event["decision"])
                          for event in events})

    def test_no_later_or_human_stage_was_run(self):
        kinds = {event["kind"] for pattern in self.patterns
                 for event in pattern["reviewEvents"]}
        # The text sweep runs over the normalised corpus, because Phase 4F-E1
        # legitimately introduced the ``editorial-review`` token and Phase
        # 4F-F2 the ``product-approval`` one.  The stages that have still
        # never been run anywhere are swept from the live text below, where
        # they must not appear whatever a later phase recorded.
        blob = json.dumps(
            E1.without_phase_4fe1_editorial_review(
                F2.without_phase_4ff2_product_approval(
                    H2.without_phase_4fh2_content_completion(
                        H21.without_phase_4fh21_product_reapproval(live_corpus())))),
            ensure_ascii=False)
        # Phase 4F-H2 legitimately recorded owner-authorized ``correction``
        # events, so the live sweep runs over the text with that pinned
        # transition removed.  A correction this phase did not author is not
        # recognised by the H2 normaliser, survives here, and still fails.
        live_blob = H2.without_phase_4fh2_corpus_text(
            H21.without_phase_4fh21_corpus_text(
                CORPUS.read_text(encoding="utf-8")))
        for kind in STAGE_KINDS_NOT_RUN:
            with self.subTest(kind=kind):
                self.assertNotIn(kind, kinds)
                self.assertNotIn(kind, blob)
        for kind in STAGE_KINDS_NEVER_RUN:
            with self.subTest(kind=kind, source="live"):
                self.assertNotIn(kind, live_blob)

    def test_no_row_stands_above_reference_verified(self):
        for _, _, pattern in iter_patterns(priority7_corpus(self.corpus)):
            with self.subTest(pattern_id=pattern["id"]):
                self.assertNotIn(
                    pattern["reviewState"],
                    {"externally-verified", "native-reviewed",
                     "editorial-reviewed", "approved", "deferred", "rejected"})

    def test_reference_verified_is_not_a_human_assurance_claim(self):
        summary = " ".join(
            SUMMARY.read_text(encoding="utf-8").lower().replace("*", "").split())
        for disclaimer in ("not human external verification",
                           "not native-speaker review",
                           "no person checked these 45 rows"):
            with self.subTest(disclaimer=disclaimer):
                self.assertIn(disclaimer, summary)


# --------------------------------------------------------------------------
# §3  the state is derived by the tooling, not decorated onto the corpus
# --------------------------------------------------------------------------

class StateIsDerivedNotAsserted(Phase4FATestCase):
    """Each row's state is re-derived, one row at a time.

    Asserting the corpus says ``reference-verified`` proves nothing on its own.
    These cases prove the tooling *requires* that value: downgrade a row and the
    validator objects, so the state is a consequence of the recorded events,
    scope digests and evidence rather than a label.
    """

    def test_downgrading_any_single_row_is_refused(self):
        context = build_context()
        for pattern_id in [pattern["id"] for pattern in self.patterns]:
            with self.subTest(pattern_id=pattern_id):
                corpus = self.mutated()
                _, _, pattern = find_pattern(corpus, pattern_id)
                pattern["reviewState"] = "research"
                self.assertIn("REVIEW_STATE_MISMATCH",
                              codes(validate_editorial(corpus, context)))

    def test_removing_any_single_acceptance_drops_that_row(self):
        context = build_context()
        for pattern_id in sorted(SUBFRAME_SUPPORT):
            with self.subTest(pattern_id=pattern_id):
                corpus = self.mutated()
                _, _, pattern = find_pattern(corpus, pattern_id)
                pattern["reviewEvents"] = []
                self.assertIn("REVIEW_STATE_MISMATCH",
                              codes(validate_editorial(corpus, context)))

    def test_every_standing_scope_digest_recomputes(self):
        """The acceptance that *stands* always covers the current content.

        Where Phase 4F-B3B.1 appended a refresh, the superseded original keeps
        its historical digest -- that is what preserving history means, and the
        superseded set is pinned to exactly the two refreshed rows so a stale
        digest cannot appear anywhere else unnoticed.
        """
        superseded = {}
        for lemma, meaning, pattern in iter_patterns(
                priority7_corpus(self.corpus)):
            with self.subTest(pattern_id=pattern["id"]):
                events = pattern["reviewEvents"]
                for event in events:
                    self.assertEqual(1, event["scopeVersion"])
                current = review_scope_digest(
                    "reference-verification", lemma, meaning, pattern)
                self.assertEqual(current, events[-1]["scopeDigest"])
                stale = [event for event in events[:-1]
                         if event["scopeDigest"] != current]
                if stale:
                    superseded[pattern["id"]] = len(stale)
        self.assertEqual(PHASE_4FB3B1_REFRESHED, superseded)

    def test_editing_a_verified_frame_retires_its_acceptance(self):
        corpus = self.mutated()
        _, _, pattern = find_pattern(
            corpus, "vp-p-szukac-seek-genitive-target-71dc6eff512c")
        pattern["complements"][0]["case"] = "accusative"
        self.assertIn("REVIEW_STATE_MISMATCH",
                      codes(validate_editorial(corpus, build_context())))


# --------------------------------------------------------------------------
# §4  the four subframe rows are evidenced, and say what evidences them
# --------------------------------------------------------------------------

class SubframeSupportIsEvidenced(Phase4FATestCase):

    def test_all_four_are_verified_and_carry_one_acceptance(self):
        for pattern_id in sorted(SUBFRAME_SUPPORT):
            with self.subTest(pattern_id=pattern_id):
                _, _, pattern = find_pattern(self.corpus, pattern_id)
                self.assertEqual("reference-verified", pattern["reviewState"])
                self.assertEqual(1, len(pattern["reviewEvents"]))
                self.assertEqual("reference-verification",
                                 pattern["reviewEvents"][0]["kind"])

    def test_each_pins_current_qualifying_contemporary_evidence(self):
        for pattern_id in sorted(SUBFRAME_SUPPORT):
            with self.subTest(pattern_id=pattern_id):
                _, _, pattern = find_pattern(self.corpus, pattern_id)
                current = {evidence_digest(record): record
                           for record in pattern["evidence"]}
                pins = pattern["reviewEvents"][0]["supportingEvidenceDigests"]
                self.assertTrue(pins)
                for pin in pins:
                    record = current.get(pin)
                    self.assertIsNotNone(record, "pin must resolve")
                    self.assertEqual("contemporary-reference",
                                     record["sourceKind"])
                    self.assertIn(record["factType"],
                                  T.REFERENCE_PATTERN_FACT_TYPES)
                    self.assertEqual(INSPECTED_ON, record["checkedAt"])

    def test_each_note_names_the_section_that_supplies_the_support(self):
        """A subframe row must say where the usage support comes from."""
        for pattern_id, token in sorted(SUBFRAME_SUPPORT.items()):
            with self.subTest(pattern_id=pattern_id):
                _, _, pattern = find_pattern(self.corpus, pattern_id)
                notes = " ".join(record["note"]
                                 for record in wsjp_records(pattern))
                self.assertIn(token, notes)
                self.assertIn("Skladnia", notes,
                              "the note must also state what Skladnia shows")

    def test_no_subframe_note_claims_a_matching_skladnia_row(self):
        """Honesty about the formal schema is the point of the distinction."""
        for pattern_id in sorted(SUBFRAME_SUPPORT):
            with self.subTest(pattern_id=pattern_id):
                _, _, pattern = find_pattern(self.corpus, pattern_id)
                notes = " ".join(record["note"]
                                 for record in wsjp_records(pattern)).lower()
                self.assertTrue(
                    any(marker in notes for marker in
                        ("lists no", "pairs", "encodes no", "separately")),
                    "the note must record that Skladnia does not match")

    def test_no_event_note_passes_usage_support_off_as_a_schema(self):
        """The distinction has to survive in the data, not just the report.

        A subframe acceptance may not describe itself as licensed by a printed
        schema, and every acceptance must state the day the entry was re-opened.
        """
        for _, _, pattern in iter_patterns(priority7_corpus(self.corpus)):
            note = pattern["reviewEvents"][0]["note"]
            with self.subTest(pattern_id=pattern["id"]):
                self.assertIn(INSPECTED_ON, note)
                if pattern["id"] in SUBFRAME_SUPPORT:
                    self.assertNotIn("licensed by", note)
                    self.assertTrue(
                        any(section in note for section in
                            ("Polaczenia", "Cytaty", "definition")),
                        "a subframe acceptance must name its usage support")

    def test_prosic_does_not_claim_the_combined_frame_is_unattested(self):
        """Regression: the first Phase 4F-A pass got this wrong.

        It reported that WSJP "never combines" the accusative person with the o
        request.  That was true of the Skladnia schema inventory and false of
        the entry, whose citations realise both in one clause.  No artefact may
        reintroduce the stronger claim.
        """
        pattern_id = ("vp-p-prosic-request-accusative-person-"
                      "o-accusative-thing-b7a8d9ce1a99")
        _, _, pattern = find_pattern(self.corpus, pattern_id)
        notes = " ".join(record["note"] for record in wsjp_records(pattern))
        self.assertIn("Cytaty", notes)
        self.assertIn("together", notes)
        forbidden = (
            "does not attest a personal object combined",
            "never combines",
            "no sense combines",
            "not attested in any sense",
        )
        # The claim may not be *asserted* anywhere the corpus speaks for itself.
        haystacks = {
            "evidence notes": notes,
            "matrix": MATRIX.read_text(encoding="utf-8"),
        }
        for label, text in haystacks.items():
            flat = " ".join(text.split())
            for claim in forbidden:
                with self.subTest(artefact=label, claim=claim):
                    self.assertNotIn(claim, flat)
        # The summary may quote it, but only while retracting it: a bare
        # reappearance without the retraction is what this guards against.
        summary = " ".join(SUMMARY.read_text(encoding="utf-8").split())
        for claim in forbidden:
            if claim not in summary:
                continue
            with self.subTest(quoted=claim):
                self.assertIn("The claim is retracted", summary)
                self.assertIn("false of the entry", summary)

    def test_podobac_sie_rests_on_sense_one_alone(self):
        """The discarded sense-2 addition must not come back.

        Sense 1's own Polaczenia list films, books and music as subjects, so it
        already covers the learner treatment; the sense-2 record added in the
        first pass claimed a reading the treatment does not need.
        """
        pattern_id = ("vp-p-podobac-sie-appeal-to-nominative-stimulus-"
                      "dative-experiencer-ef199e675ee9")
        _, _, pattern = find_pattern(self.corpus, pattern_id)
        records = wsjp_records(pattern)
        self.assertEqual(1, len(records))
        self.assertIn("4701782", records[0]["locator"])
        self.assertNotIn("4701783", records[0]["locator"])
        self.assertNotIn("4701783", CORPUS.read_text(encoding="utf-8"))
        self.assertNotIn("odpowiadac komus", MATRIX.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# §5  the actor is nonhuman, singly roled, and load-bearing
# --------------------------------------------------------------------------

class NonhumanReferenceActor(Phase4FATestCase):

    def actors(self):
        return copy.deepcopy(self.document["editorialActorRegistry"])

    def test_exactly_one_actor_is_registered_and_it_is_nonhuman(self):
        # Stated as the tier boundary Phase 4F-A actually established rather
        # than as a closed registry key set: exactly one actor carries a
        # review-stage role, it is the nonhuman reference actor, and no actor
        # carries the tier-2 editorial role.  A later phase registering a
        # non-review actor -- Phase 4F-C2's example generator -- leaves that
        # boundary exactly where Phase 4F-A left it.
        actors = priority7_actors(self.document["editorialActorRegistry"])
        self.assertIn(REFERENCE_ACTOR, actors)
        review_roles = {"reference-verification", "editorial-review"}
        with_review_role = {
            actor_id for actor_id, record in actors.items()
            if review_roles & set(record.get("roles") or [])}
        self.assertEqual({REFERENCE_ACTOR}, with_review_role)
        record = actors[REFERENCE_ACTOR]
        self.assertIs(False, record["human"])
        self.assertEqual(["reference-verification"], record["roles"])
        for actor_id, other in actors.items():
            with self.subTest(actor_id=actor_id):
                self.assertIs(False, other["human"])
                for role in other["roles"]:
                    self.assertIn(role, T.EDITORIAL_ACTOR_ROLES)

    def test_the_actor_is_not_an_editorial_reviewer_or_example_generator(self):
        roles = self.document["editorialActorRegistry"][REFERENCE_ACTOR]["roles"]
        self.assertNotIn("editorial-review", roles)
        self.assertNotIn("example-generation", roles)

    def test_the_actor_key_is_claimed_by_no_human_registry(self):
        for registry in ("reviewerRegistry", "authorRegistry"):
            with self.subTest(registry=registry):
                self.assertNotIn(REFERENCE_ACTOR, self.document[registry])

    def test_every_acceptance_names_the_actor_and_never_a_person(self):
        for pattern in self.patterns:
            for event in pattern["reviewEvents"]:
                with self.subTest(pattern_id=pattern["id"]):
                    self.assertEqual(REFERENCE_ACTOR, event["actorRef"])
                    self.assertNotIn("reviewerRef", event)

    def test_an_unregistered_actor_fails_the_whole_corpus(self):
        self.assertIn("EDITORIAL_ACTOR_REGISTRY_DANGLING",
                      codes(validate_editorial(
                          self.corpus, build_context(actors={}))))

    def test_a_human_actor_record_is_refused(self):
        actors = self.actors()
        actors[REFERENCE_ACTOR]["human"] = True
        self.assertIn("EDITORIAL_ACTOR_NOT_NONHUMAN",
                      codes(validate_editorial(
                          self.corpus, build_context(actors=actors))))

    def test_an_actor_record_omitting_human_is_refused(self):
        actors = self.actors()
        del actors[REFERENCE_ACTOR]["human"]
        self.assertIn("EDITORIAL_ACTOR_NOT_NONHUMAN",
                      codes(validate_editorial(
                          self.corpus, build_context(actors=actors))))

    def test_borrowing_a_human_role_is_refused(self):
        actors = self.actors()
        actors[REFERENCE_ACTOR]["roles"] = [
            "reference-verification", "native-linguistic"]
        self.assertIn("EDITORIAL_ACTOR_ROLE_UNKNOWN",
                      codes(validate_editorial(
                          self.corpus, build_context(actors=actors))))

    def test_an_actor_without_the_reference_role_cannot_verify(self):
        actors = self.actors()
        actors[REFERENCE_ACTOR]["roles"] = ["editorial-review"]
        self.assertIn("EDITORIAL_ACTOR_ROLE",
                      codes(validate_editorial(
                          self.corpus, build_context(actors=actors))))

    def test_the_actor_key_may_not_also_be_a_reviewer(self):
        reviewers = copy.deepcopy(self.document["reviewerRegistry"])
        reviewers[REFERENCE_ACTOR] = {
            "human": True, "roles": ["native-linguistic"]}
        self.assertIn("REGISTRY_KEY_COLLISION",
                      codes(validate_editorial(
                          self.corpus, build_context(reviewers=reviewers))))

    def test_ab_cannot_be_used_as_the_reference_actor(self):
        corpus = self.mutated()
        _, _, pattern = find_pattern(
            corpus, "vp-p-szukac-seek-genitive-target-71dc6eff512c")
        pattern["reviewEvents"][0]["actorRef"] = "native-reviewer-001"
        self.assertIn("EDITORIAL_ACTOR_REGISTRY_DANGLING",
                      codes(validate_editorial(corpus, build_context())))

    def test_no_vendor_or_model_name_is_load_bearing(self):
        blob = json.dumps(self.document["editorialActorRegistry"],
                          ensure_ascii=False).lower()
        for token in ("claude", "opus", "sonnet", "anthropic", "gpt", "openai",
                      "codex", "gemini", "llama", "mistral"):
            with self.subTest(token=token):
                self.assertNotIn(token, blob)


# --------------------------------------------------------------------------
# §6  the acceptances rest on the freshly inspected reference evidence
# --------------------------------------------------------------------------

class EvidenceIsLoadBearing(Phase4FATestCase):

    def test_every_pin_resolves_to_a_current_contemporary_frame_record(self):
        for lemma, meaning, pattern in iter_patterns(self.corpus):
            current = {evidence_digest(record): record
                       for record in pattern["evidence"]}
            for event in pattern["reviewEvents"]:
                pins = event["supportingEvidenceDigests"]
                with self.subTest(pattern_id=pattern["id"]):
                    self.assertTrue(pins)
                    self.assertEqual(sorted(set(pins)), pins)
                    for pin in pins:
                        record = current.get(pin)
                        self.assertIsNotNone(record, "pin must resolve")
                        self.assertEqual("wsjp-pan", record["sourceId"])
                        self.assertEqual("contemporary-reference",
                                         record["sourceKind"])
                        self.assertIn(record["factType"],
                                      T.REFERENCE_PATTERN_FACT_TYPES)

    def test_no_acceptance_leans_on_medak_or_on_the_repository(self):
        """Headword presence and existing app content verify nothing."""
        for lemma, meaning, pattern in iter_patterns(self.corpus):
            by_digest = {evidence_digest(record): record
                         for record in pattern["evidence"]}
            for event in pattern["reviewEvents"]:
                for pin in event["supportingEvidenceDigests"]:
                    with self.subTest(pattern_id=pattern["id"]):
                        self.assertNotIn(
                            by_digest[pin]["sourceKind"],
                            {"medak-research", "repository"})

    def test_editing_a_pinned_record_retires_the_acceptance(self):
        for pattern_id in sorted(SUBFRAME_SUPPORT) + [
                "vp-p-szukac-seek-genitive-target-71dc6eff512c"]:
            with self.subTest(pattern_id=pattern_id):
                corpus = self.mutated()
                _, _, pattern = find_pattern(corpus, pattern_id)
                pinned = pattern["reviewEvents"][0][
                    "supportingEvidenceDigests"][0]
                for record in pattern["evidence"]:
                    if evidence_digest(record) == pinned:
                        record["note"] = "silently rewritten after acceptance"
                        break
                else:
                    self.fail("pinned record not found")
                self.assertIn("REVIEW_STATE_MISMATCH",
                              codes(validate_editorial(corpus, build_context())))

    def test_removing_the_pins_refuses_the_acceptance(self):
        corpus = self.mutated()
        _, _, pattern = find_pattern(
            corpus, "vp-p-szukac-seek-genitive-target-71dc6eff512c")
        del pattern["reviewEvents"][0]["supportingEvidenceDigests"]
        self.assertIn("REVIEW_EVIDENCE_REQUIRED",
                      codes(validate_editorial(corpus, build_context())))

    def test_repinning_to_headword_evidence_alone_is_refused(self):
        corpus = self.mutated()
        _, _, pattern = find_pattern(
            corpus, "vp-p-szukac-seek-genitive-target-71dc6eff512c")
        headword = [record for record in pattern["evidence"]
                    if record["sourceKind"] == "medak-research"]
        self.assertEqual(1, len(headword))
        pattern["reviewEvents"][0]["supportingEvidenceDigests"] = [
            evidence_digest(headword[0])]
        found = codes(validate_editorial(corpus, build_context()))
        self.assertIn("REVIEW_CONTEMPORARY_EVIDENCE_REQUIRED", found)
        self.assertIn("REFERENCE_PATTERN_EVIDENCE_REQUIRED", found)
        self.assertIn("REVIEW_STATE_MISMATCH", found)

    def test_the_evidence_accounting_matches_the_repaired_corpus(self):
        records = [record for _, _, pattern in iter_patterns(
                       priority7_corpus(self.corpus))
                   for record in pattern["evidence"]]
        wsjp = [record for record in records
                if record["sourceId"] == "wsjp-pan"]
        self.assertEqual(EVIDENCE_TOTAL, len(records))
        self.assertEqual(WSJP_RECORDS, len(wsjp))
        self.assertEqual(
            WSJP_DISTINCT_ENTRY_SENSE_URLS,
            len({record["locator"].split(" ")[0] for record in wsjp}))

    def test_phase_4fa_added_and_deleted_no_evidence_record(self):
        def keys(corpus):
            return {(pattern["id"], record["sourceId"])
                    for _, _, pattern in iter_patterns(corpus)
                    for record in pattern["evidence"]}

        baseline = baseline_corpus()
        self.assertEqual(
            EVIDENCE_TOTAL,
            sum(len(pattern["evidence"])
                for _, _, pattern in iter_patterns(baseline)))
        self.assertEqual(keys(baseline), keys(self.corpus))

    def test_only_wsjp_records_carry_the_inspection_date(self):
        by_date = collections.defaultdict(set)
        for _, _, pattern in iter_patterns(priority7_corpus(self.corpus)):
            for record in pattern["evidence"]:
                by_date[record["checkedAt"]].add(record["sourceId"])
        self.assertEqual({"wsjp-pan"}, by_date[INSPECTED_ON])
        self.assertNotIn("wsjp-pan", by_date[COMPILED_ON])
        self.assertEqual({INSPECTED_ON, COMPILED_ON}, set(by_date))

    def test_every_wsjp_record_was_re_inspected_none_left_stale(self):
        wsjp = [record for _, _, pattern in iter_patterns(
                    priority7_corpus(self.corpus))
                for record in wsjp_records(pattern)]
        self.assertEqual(WSJP_RECORDS, len(wsjp))
        self.assertEqual({INSPECTED_ON},
                         {record["checkedAt"] for record in wsjp})

    def test_the_note_rewrites_are_exactly_the_recorded_ones(self):
        baseline = {(pattern["id"], record["sourceId"], record["locator"]):
                    record.get("note")
                    for _, _, pattern in iter_patterns(baseline_corpus())
                    for record in pattern["evidence"]}
        current = {(pattern["id"], record["sourceId"], record["locator"]):
                   record.get("note")
                   for _, _, pattern in iter_patterns(self.corpus)
                   for record in pattern["evidence"]}
        rewritten = [key for key in baseline.keys() & current.keys()
                     if baseline[key] != current[key]]
        # One locator string was also made precise, so it appears as a
        # baseline-only and a current-only key rather than a rewrite.
        self.assertEqual(NOTE_REWRITES - 1, len(rewritten))
        self.assertEqual(1, len(set(baseline) - set(current)))
        self.assertEqual(1, len(set(current) - set(baseline)))

    def test_every_repository_locator_still_resolves(self):
        index = repository_index()
        for _, _, pattern in iter_patterns(self.corpus):
            for record in pattern["evidence"]:
                if record["sourceId"] != "repository":
                    continue
                entity_id = record["locator"].split("#", 1)[1]
                with self.subTest(locator=record["locator"]):
                    self.assertIsNotNone(index.get(entity_id))


# --------------------------------------------------------------------------
# §7  the mode is load-bearing too
# --------------------------------------------------------------------------

class ModeIsLoadBearing(Phase4FATestCase):

    def test_dropping_the_release_mode_refuses_the_stage_outright(self):
        corpus = self.mutated()
        _, _, pattern = find_pattern(
            corpus, "vp-p-szukac-seek-genitive-target-71dc6eff512c")
        del pattern["releaseMode"]
        found = codes(validate_editorial(corpus, build_context()))
        self.assertIn("REVIEW_STAGE_NOT_IN_MODE", found)
        self.assertIn("REVIEW_STATE_MISMATCH", found)

    def test_relabelling_the_row_human_reviewed_refuses_the_stage(self):
        corpus = self.mutated()
        _, _, pattern = find_pattern(
            corpus, "vp-p-szukac-seek-genitive-target-71dc6eff512c")
        pattern["releaseMode"] = HUMAN_REVIEWED_MODE
        self.assertIn("REVIEW_STAGE_NOT_IN_MODE",
                      codes(validate_editorial(corpus, build_context())))

    def test_relabelling_an_acceptance_as_human_verification_fails(self):
        corpus = self.mutated()
        _, _, pattern = find_pattern(
            corpus, "vp-p-szukac-seek-genitive-target-71dc6eff512c")
        event = pattern["reviewEvents"][0]
        event["kind"] = "external-verification"
        event["reviewerRef"] = event.pop("actorRef")
        found = codes(validate_editorial(corpus, build_context()))
        self.assertIn("REVIEWER_REGISTRY_DANGLING", found)
        self.assertIn("REVIEW_STATE_MISMATCH", found)

    def test_a_second_identical_acceptance_establishes_nothing(self):
        corpus = self.mutated()
        _, _, pattern = find_pattern(
            corpus, "vp-p-szukac-seek-genitive-target-71dc6eff512c")
        pattern["reviewEvents"].append(
            copy.deepcopy(pattern["reviewEvents"][0]))
        self.assertIn("REVIEW_DUPLICATE_STAGE_ACCEPTANCE",
                      codes(validate_editorial(corpus, build_context())))

    def test_an_editorial_review_cannot_be_stacked_by_the_reference_actor(self):
        corpus = self.mutated()
        lemma, meaning, pattern = find_pattern(
            corpus, "vp-p-szukac-seek-genitive-target-71dc6eff512c")
        pattern["reviewEvents"].append({
            "kind": "editorial-review",
            "decision": "accept",
            "scopeVersion": 1,
            "scopeDigest": review_scope_digest(
                "editorial-review", lemma, meaning, pattern),
            "actorRef": REFERENCE_ACTOR,
            "corroboratingActorRefs": [REFERENCE_ACTOR],
            "reviewedAt": INSPECTED_ON,
        })
        found = codes(validate_editorial(corpus, build_context()))
        self.assertIn("EDITORIAL_CORROBORATION_SELF", found)
        self.assertIn("REVIEW_ACTOR_INDEPENDENCE", found)


# --------------------------------------------------------------------------
# §8  the published matrix agrees with the corpus, row by row
# --------------------------------------------------------------------------

class MatrixAgreesWithTheCorpus(Phase4FATestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with MATRIX.open(encoding="utf-8", newline="") as handle:
            cls.rows = list(csv.DictReader(handle))

    def test_the_matrix_is_lf_terminated(self):
        raw = MATRIX.read_bytes()
        self.assertNotIn(b"\r", raw, "the matrix must use Unix line endings")

    def test_the_matrix_covers_every_pattern_exactly_once(self):
        self.assertEqual(45, len(self.rows))
        self.assertEqual(
                         {pattern["id"] for _, _, pattern in iter_patterns(
                             priority7_corpus(self.corpus))},
                         {row["patternId"] for row in self.rows})

    def test_the_matrix_counts_are_the_reported_counts(self):
        counts = collections.Counter(row["classification"] for row in self.rows)
        self.assertEqual(45, counts["VERIFIED"])
        self.assertEqual(0, counts["UNRESOLVED"])
        self.assertEqual(0, counts["CORRECTION NEEDED"])
        supports = collections.Counter(row["supportKind"] for row in self.rows)
        self.assertEqual({EXACT_FRAME: 41, SUBFRAME: 4}, dict(supports))

    def test_every_row_matches_the_corpus_and_states_one_support_kind(self):
        by_id = {pattern["id"]: pattern for pattern in self.patterns}
        for row in self.rows:
            with self.subTest(pattern_id=row["patternId"]):
                pattern = by_id[row["patternId"]]
                self.assertEqual("VERIFIED", row["classification"])
                self.assertEqual("accept", row["referenceEvent"])
                self.assertEqual(pattern["reviewState"], row["endState"])
                self.assertEqual(pattern["releaseMode"], row["releaseMode"])
                self.assertIn(row["supportKind"], {EXACT_FRAME, SUBFRAME})
                self.assertTrue(row["licensingSchema"])

    def test_exact_frame_rows_name_a_schema_that_is_actually_printed(self):
        for row in self.rows:
            if row["supportKind"] != EXACT_FRAME:
                continue
            with self.subTest(pattern_id=row["patternId"]):
                self.assertIn(row["licensingSchema"], row["observedSkladnia"])

    def test_subframe_rows_are_exactly_the_four_and_claim_no_schema(self):
        subframe = {row["patternId"] for row in self.rows
                    if row["supportKind"] == SUBFRAME}
        self.assertEqual(set(SUBFRAME_SUPPORT), subframe)
        for row in self.rows:
            if row["supportKind"] != SUBFRAME:
                continue
            with self.subTest(pattern_id=row["patternId"]):
                self.assertNotIn(row["licensingSchema"], row["observedSkladnia"],
                                 "a subframe row must not pass itself off as a "
                                 "printed Skladnia schema")
                self.assertTrue(
                    any(section in row["licensingSchema"] for section in
                        ("Polaczenia", "Cytaty", "Definicja")),
                    "a subframe row must name its supporting section")

    def test_every_row_cites_the_locator_it_was_verified_against(self):
        by_id = {pattern["id"]: pattern for pattern in self.patterns}
        for row in self.rows:
            with self.subTest(pattern_id=row["patternId"]):
                recorded = {record["locator"]
                            for record in wsjp_records(by_id[row["patternId"]])}
                self.assertEqual(recorded,
                                 set(row["wsjpLocators"].split(" ; ")))


# --------------------------------------------------------------------------
# §9  what Phase 4F-A did not do
# --------------------------------------------------------------------------

class PhaseBoundary(Phase4FATestCase):

    def test_the_governance_tooling_was_not_modified(self):
        """§14: if the tooling had been insufficient, the phase would stop."""
        baseline = git("show", f"{BASELINE_COMMIT}:priority7_tooling.py")
        self.assertEqual(0, baseline.returncode, baseline.stderr)
        self.assertEqual(
            baseline.stdout,
            (ROOT / "priority7_tooling.py").read_text(encoding="utf-8"))

    def normalised(self, corpus=None):
        """The corpus as Phase 4F-A left it: later approved work reverted."""
        return without_phase_4fc2_examples(
            without_phase_4fb3b_edits(self.corpus if corpus is None else corpus))

    def test_no_linguistic_or_learner_facing_content_changed(self):
        self.assertEqual(
            linguistic_projection(baseline_corpus()),
            linguistic_projection(self.normalised()))

    def test_the_projection_guard_is_not_vacuous(self):
        corpus = self.mutated()
        _, _, pattern = find_pattern(
            corpus, "vp-p-szukac-seek-genitive-target-71dc6eff512c")
        pattern["learnerExplanationEn"] = "mutated"
        self.assertNotEqual(
            linguistic_projection(baseline_corpus()),
            linguistic_projection(self.normalised(corpus)))

    def test_the_phase_4fb3b_normalisation_reverts_only_the_approved_edits(self):
        """The normalisation cannot hide an unapproved change."""
        corpus = self.mutated()
        _, _, pattern = find_pattern(
            corpus, "vp-p-sluchac-obey-genitive-object-674adae2dec3")
        pattern["learnerExplanationEn"] = "something else entirely"
        self.assertNotEqual(
            linguistic_projection(baseline_corpus()),
            linguistic_projection(self.normalised(corpus)))

    def test_the_phase_4fc2_normalisation_reverts_only_the_locked_examples(self):
        """A sentence Phase 4F-C1C did not lock survives the revert."""
        corpus = self.mutated()
        _, _, pattern = find_pattern(
            corpus, "vp-p-widziec-perceive-visually-accusative-object"
                    "-80b697e51432")
        pattern["examples"][0]["pl"] = "Czy widzisz to jezioro?"
        self.assertNotEqual(
            linguistic_projection(baseline_corpus()),
            linguistic_projection(self.normalised(corpus)))

    def test_the_five_pending_replacement_slots_were_not_canonicalized(self):
        normalised = self.normalised()
        origins = [example["origin"]["kind"]
                   for _, _, pattern in iter_patterns(normalised)
                   for example in (pattern.get("examples") or [])]
        self.assertEqual(23, len(origins))
        self.assertEqual({"repository-reuse"}, set(origins))
        self.assertEqual({}, self.document["authorRegistry"])
        self.assertNotIn("editorial-generated",
                         json.dumps(normalised, ensure_ascii=False))

    def test_nothing_became_learner_visible(self):
        self.assertEqual(
            0, sum(len(pattern["activityEligibility"])
                   for pattern in self.patterns))
        self.assertEqual(
            0, sum(1 for _, _, pattern in iter_patterns(self.corpus)
                   for example in (pattern.get("examples") or [])
                   if example["audioEligible"] is True))

    def test_ab_is_unchanged_and_gained_no_event(self):
        record = self.document["reviewerRegistry"]["native-reviewer-001"]
        self.assertIs(True, record["human"])
        self.assertIs(True, record["nativePolishSpeaker"])
        self.assertEqual(["native-linguistic"], record["roles"])
        self.assertNotIn("ownerAllowsMultipleRoles", record)
        self.assertNotIn("acknowledgedReleaseModes", record)
        self.assertNotIn("native-reviewer-001",
                         CORPUS.read_text(encoding="utf-8"))

    def test_no_freeze_runtime_or_revision_was_produced(self):
        # Superseded by Priority 7 Phase 4F-I1, the release phase.  What
        # survives is that the only runtime that may exist is exactly the
        # pinned I1 release artifact, alongside its matching shell and worker.
        self.assertEqual("complete", i1_bundle().state)
        for glob in ("*frozen*.json", "*release*.json", "*tombstone*.json"):
            for found in (ROOT / "editorial").glob(glob):
                self.fail(f"unexpected release artifact: {found}")
        blob = CORPUS.read_text(encoding="utf-8")
        self.assertNotIn("patternDataRevision", blob)
        self.assertNotIn("releaseAuthorization", blob)

    def test_the_corpus_document_gained_no_registry_key(self):
        self.assertEqual({"artifactStatus", "formatVersion", "lemmas"},
                         set(self.corpus))

    def test_no_shipping_file_was_modified(self):
        """Works uncommitted and committed: the diff is against the baseline.

        ``git status`` alone goes empty the moment the candidate is committed,
        which would make this guard vacuous in the committed-scratch rehearsal.
        """
        status = git("status", "--porcelain")
        self.assertEqual(0, status.returncode, status.stderr)
        committed = git("diff", "--name-only", BASELINE_COMMIT, "HEAD")
        self.assertEqual(0, committed.returncode, committed.stderr)
        changed = [line[3:].strip().strip('"')
                   for line in status.stdout.splitlines() if line.strip()]
        changed += [line.strip() for line in committed.stdout.splitlines()
                    if line.strip()]
        allowed_prefixes = ("tests/", "reports/")
        allowed_paths = {
            "editorial/verb-pattern-candidates.json",
            "editorial/priority-7-authoring-context.json",
        }
        unexpected = [path for path in changed
                      if not path.startswith(allowed_prefixes)
                      and path not in allowed_paths
                      and not is_only_the_h3_ui_wording(path)
                      and not is_only_the_i1_activation(path)]
        self.assertEqual([], unexpected,
                         f"no shipping file may be modified: {unexpected}")

    def test_the_repository_still_has_no_remote(self):
        remotes = git("remote")
        self.assertEqual(0, remotes.returncode, remotes.stderr)
        self.assertEqual("", remotes.stdout.strip())

    def test_the_phase_reports_exist(self):
        self.assertTrue(SUMMARY.is_file())
        self.assertTrue(MATRIX.is_file())

    def test_the_summary_records_the_two_pass_history_honestly(self):
        """§14: the first pass's 41/4 result must not be written out of history."""
        summary = " ".join(
            SUMMARY.read_text(encoding="utf-8").replace("*", "").split())
        for phrase in ("41 verified", "4 unresolved", "too strict",
                       "sense-2", "CRLF"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, summary)


if __name__ == "__main__":
    unittest.main()
