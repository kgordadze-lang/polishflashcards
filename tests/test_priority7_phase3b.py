"""Priority 7 Phase 3B - synthetic non-release fixture and runtime boundary.

Three things are asserted here, and they are deliberately kept apart:

  1. the committed fixture at ``tests/fixtures/priority7/runtime-fixture.json``
     is exactly what the existing ``project-fixture`` non-release CLI emits for
     the synthetic editorial document defined below - so it cannot be
     hand-edited into something else;
  2. that fixture is wrapped, and the wrapper says ``releaseAuthorized: false``;
  3. nothing about it leaks into a public surface, and no real Priority 7
     runtime artefact exists.

The synthetic editorial document is invented from end to end.  Its lemmas are
not Polish words, its glosses are not teaching material, and its "approved"
review events approve nothing about Polish - they exist only because the
projector admits approved patterns and nothing else, which is the guard that
keeps the real research corpus out of every runtime shape (Phase 3A runtime
contract 4.2).  Nothing in this file may be read as a linguistic claim, and no
record in ``editorial/verb-pattern-candidates.json`` is touched, promoted or
projected by it.

Run:  python3 -m unittest tests.test_priority7_phase3b
"""

import json
import re
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import build_pages

from priority7_tooling import (
    NONRELEASE_PROJECTION_STATUS,
    ValidationContext,
    allocate_example_id,
    allocate_lemma_id,
    allocate_meaning_id,
    allocate_pattern_id,
    evidence_digest,
    project_nonrelease_fixture,
    review_scope_digest,
    validate_editorial,
    validate_runtime,
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

import priority7_phase4fe1_normalizer as E1
import priority7_phase4ff2_normalizer as F2
import priority7_phase4fh2_normalizer as H2
import priority7_phase4fh21_normalizer as H21

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
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "priority7"
FIXTURE_PATH = FIXTURE_DIR / "runtime-fixture.json"
EDITORIAL_CORPUS = ROOT / "editorial" / "verb-pattern-candidates.json"


def priority7_corpus(document):
    """Exact released Priority 7 identity slice, independent of ordering."""
    released = json.loads(
        (ROOT / "content" / "verb-patterns.json").read_text(encoding="utf-8"))
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

# One marker string every synthetic record carries, so a stray copy of this data
# announces itself wherever it is found.
MARK = "SYNTHETIC-NONRELEASE"
# Deliberately hostile text.  Runtime strings are data; the renderer must place
# them with textContent and never as markup.  The JXA suite proves the DOM side;
# this file only proves the strings survive the pipeline unchanged.
HOSTILE = (
    '<img src=x onerror="window.__vpPwned=1">'
    "</span><script>window.__vpPwned=1</script>"
)
LONG_TAIL = (
    " This sentence is deliberately long so the narrow-phone layout has to wrap "
    "a real paragraph of learner-facing text between tokens rather than clipping "
    "it, scrolling it sideways or breaking it inside a word."
)

REVIEWED_AT = "2026-08-08"
CHECKED_AT = "2026-08-08"

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


def synthetic_context_document():
    """The private registries the CLI needs, as its --context JSON."""
    return {
        "sourceRegistry": {
            "synthetic-fixture-reference": {"sourceKind": "contemporary-reference"},
        },
        "reviewerRegistry": {
            "synthetic-fixture-external": {
                "human": True,
                "roles": ["external-verification"],
            },
            "synthetic-fixture-native": {
                "human": True,
                "roles": ["native-linguistic"],
            },
            "synthetic-fixture-product": {
                "human": True,
                "roles": ["product-approval"],
            },
        },
        "authorRegistry": {"synthetic-fixture-author": {"human": True}},
    }


def _evidence(locator):
    return [{
        "sourceId": "synthetic-fixture-reference",
        "sourceKind": "contemporary-reference",
        "locator": f"fixture://{MARK}/{locator}",
        "factType": "complement-frame",
        "checkedAt": CHECKED_AT,
        "note": f"{MARK}: invented record for UI shape tests; not evidence about Polish.",
    }]


def _example(pattern_id, key, pl, en):
    return {
        "id": allocate_example_id(pattern_id, key),
        "key": key,
        "pl": pl,
        "en": en,
        "origin": {
            "kind": "original",
            "authorRef": "synthetic-fixture-author",
            "authoredAt": REVIEWED_AT,
        },
        "audioEligible": False,
    }


def _acceptance_events(lemma, meaning, pattern):
    """The three stage acceptances the projector requires, over invented data."""
    return [
        {
            "kind": "external-verification",
            "decision": "accept",
            "scopeVersion": 1,
            "scopeDigest": review_scope_digest(
                "external-verification", lemma, meaning, pattern),
            "supportingEvidenceDigests": [
                evidence_digest(pattern["evidence"][0])],
            "reviewerRef": "synthetic-fixture-external",
            "reviewedAt": REVIEWED_AT,
        },
        {
            "kind": "native-linguistic",
            "decision": "accept",
            "scopeVersion": 1,
            "scopeDigest": review_scope_digest(
                "native-linguistic", lemma, meaning, pattern),
            "reviewerRef": "synthetic-fixture-native",
            "reviewedAt": REVIEWED_AT,
        },
        {
            "kind": "product-approval",
            "decision": "accept",
            "scopeVersion": 1,
            "scopeDigest": review_scope_digest(
                "product-approval", lemma, meaning, pattern),
            "reviewerRef": "synthetic-fixture-product",
            "reviewedAt": REVIEWED_AT,
        },
    ]


def _lemma(canonical, aspect, meanings, display=None):
    lemma_id = allocate_lemma_id(canonical)
    record = {
        "id": lemma_id,
        "canonicalLemma": canonical,
        "reflexive": canonical.endswith(" się"),
        "aspect": aspect,
        "meanings": [],
    }
    if display is not None:
        record["displayLemma"] = display
    for meaning_key, glosses, scope, patterns in meanings:
        meaning_id = allocate_meaning_id(lemma_id, canonical, meaning_key)
        meaning = {
            "id": meaning_id,
            "key": meaning_key,
            "glossesEn": glosses,
            "internalScope": scope,
            "patterns": [],
        }
        for spec in patterns:
            pattern_id = allocate_pattern_id(
                meaning_id, canonical, meaning_key, spec["key"])
            pattern = {
                "id": pattern_id,
                "key": spec["key"],
                "relationType": spec["relationType"],
                "complements": spec["complements"],
                "cefr": spec["cefr"],
                "teachingStatus": spec["teachingStatus"],
                "usage": spec["usage"],
                "learnerExplanationEn": spec["learnerExplanationEn"],
                "activityEligibility": spec.get("activityEligibility", []),
                "evidence": _evidence(spec["key"]),
                "reviewState": "approved",
                "reviewEvents": [],
            }
            if spec.get("example"):
                key, pl, en = spec["example"]
                pattern["examples"] = [_example(pattern_id, key, pl, en)]
            if spec.get("errorNotes"):
                pattern["errorNotes"] = spec["errorNotes"]
            if spec.get("contentRefs"):
                pattern["contentRefs"] = spec["contentRefs"]
            meaning["patterns"].append(pattern)
        record["meanings"].append(meaning)
    return record


def synthetic_editorial_document():
    """Six invented lemmas covering every shape the Phase 3B UI must render.

    Deliberately covered: one lemma / one meaning / one pattern; a lemma with
    two meanings; a meaning with three patterns; two case complements in one
    frame; preposition + case; lexical ``się``; an infinitive complement; a
    clause complement; recognition level differing from production; a
    recognition-only pattern; an example present; an example absent; very long
    learner-facing strings; and hostile text that must never become markup.
    """
    document = {
        "artifactStatus": "priority-7-editorial-nonproduction",
        "formatVersion": 1,
        "lemmas": [
            # 1. the simplest possible shape: one meaning, one pattern, one case.
            _lemma("fikcjonować", "imperfective", [(
                "test-object",
                [f"{MARK}: act on an invented object"],
                f"{MARK}: invented sense; exercises one direct case slot.",
                [{
                    "key": "direct-object",
                    "relationType": "lexical-frame",
                    "complements": [{
                        "type": "case", "case": "accusative",
                        "required": True, "role": "object",
                    }],
                    "cefr": {"recognition": "A1", "production": "A1"},
                    "teachingStatus": "active-production",
                    "usage": {"priority": "core", "register": "neutral"},
                    "learnerExplanationEn": (
                        f"{MARK}: with this invented sense the verb takes a "
                        "direct object."
                    ),
                    "activityEligibility": [
                        "reference", "search", "grammar-choose"],
                    "example": (
                        "first-context",
                        f"{MARK}: fikcjonuję obiekt testowy.",
                        f"{MARK}: I act on the invented test object.",
                    ),
                    "errorNotes": [{
                        "kind": "predicted-distractor",
                        "incorrectForm": f"{MARK}-ZLA-FORMA",
                        "guidanceEn": (
                            f"{MARK}: invented guidance string, never learner copy."
                        ),
                    }],
                }],
            )]),
            # 2. one meaning, three patterns: means-method, preposition+case,
            #    and a two-complement frame spanning two different cases.
            _lemma("metodować", "imperfective", [(
                "method-action",
                [f"{MARK}: carry out an invented method"],
                f"{MARK}: invented sense; exercises sibling patterns.",
                [
                    {
                        "key": "instrumental-means",
                        "relationType": "means-method",
                        "complements": [{
                            "type": "case", "case": "instrumental",
                            "required": False, "role": "means",
                        }],
                        "cefr": {"recognition": "A2", "production": "A2"},
                        "teachingStatus": "active-production",
                        "usage": {"priority": "common", "register": "neutral"},
                        "learnerExplanationEn": (
                            f"{MARK}: this invented frame names how the action "
                            "is carried out."
                        ),
                        "activityEligibility": [],
                    },
                    {
                        "key": "topic-locative",
                        "relationType": "lexical-frame",
                        "complements": [{
                            "type": "preposition-case", "preposition": "o",
                            "case": "locative", "required": True,
                            "role": "topic",
                        }],
                        "cefr": {"recognition": "A2", "production": "B1"},
                        "teachingStatus": "active-production",
                        "usage": {"priority": "common", "register": "neutral"},
                        "learnerExplanationEn": (
                            f"{MARK}: this invented frame names what the action "
                            "is about, and it carries hostile text on purpose: "
                            + HOSTILE + LONG_TAIL
                        ),
                        "activityEligibility": [],
                        "example": (
                            "long-context",
                            f"{MARK}: metoduję o obiekcie testowym, "
                            "o wymyślonym obiekcie testowym i o jeszcze jednym "
                            "wymyślonym obiekcie testowym.",
                            f"{MARK}: a deliberately long invented translation "
                            "that has to wrap on a narrow phone, and it also "
                            "carries hostile text: " + HOSTILE,
                        ),
                    },
                    {
                        "key": "recipient-and-area",
                        "relationType": "lexical-frame",
                        "complements": [
                            {
                                "type": "case", "case": "dative",
                                "required": True, "role": "recipient",
                            },
                            {
                                "type": "preposition-case", "preposition": "w",
                                "case": "locative", "required": True,
                                "role": "content",
                            },
                        ],
                        "cefr": {"recognition": "B1", "production": "B1"},
                        "teachingStatus": "active-production",
                        "usage": {"priority": "common", "register": "neutral"},
                        "learnerExplanationEn": (
                            f"{MARK}: this invented frame has two slots, and "
                            "both belong to it."
                        ),
                        "activityEligibility": [],
                    },
                ],
            )]),
            # 3. lexical `się`, two meanings, one of them recognition-only.
            _lemma("zetafikcjonować się", "imperfective", [
                (
                    "object-sense",
                    [f"{MARK}: relate to an invented object"],
                    f"{MARK}: invented first sense of a reflexive entry.",
                    [{
                        "key": "genitive-object",
                        "relationType": "lexical-frame",
                        "complements": [{
                            "type": "case", "case": "genitive",
                            "required": True, "role": "object",
                        }],
                        "cefr": {"recognition": "A2", "production": "A2"},
                        "teachingStatus": "active-production",
                        "usage": {"priority": "core", "register": "neutral"},
                        "learnerExplanationEn": (
                            f"{MARK}: the first invented sense takes one slot."
                        ),
                        "activityEligibility": ["reference", "search"],
                        "example": (
                            "first-context",
                            f"{MARK}: zetafikcjonuję się obiektu testowego.",
                            f"{MARK}: I relate to the invented test object.",
                        ),
                    }],
                ),
                (
                    "target-sense",
                    [f"{MARK}: aim at an invented object"],
                    f"{MARK}: invented second sense with different government.",
                    [{
                        "key": "target-accusative",
                        "relationType": "lexical-frame",
                        "complements": [{
                            "type": "preposition-case", "preposition": "o",
                            "case": "accusative", "required": True,
                            "role": "target",
                        }],
                        "cefr": {"recognition": "B1"},
                        "teachingStatus": "recognition-only",
                        "usage": {"priority": "common", "register": "neutral"},
                        "learnerExplanationEn": (
                            f"{MARK}: the second invented sense behaves "
                            "differently from the first."
                        ),
                        "activityEligibility": ["reference", "search"],
                    }],
                ),
            ]),
            # 4. the two complements that have no case at all.
            _lemma("bezokolicznikować", "imperfective", [(
                "clause-action",
                [f"{MARK}: report an invented action"],
                f"{MARK}: invented sense; exercises non-case complements.",
                [
                    {
                        "key": "infinitive-content",
                        "relationType": "lexical-frame",
                        "complements": [{
                            "type": "infinitive", "required": True,
                            "role": "content",
                        }],
                        "cefr": {"recognition": "A1", "production": "A2"},
                        "teachingStatus": "active-production",
                        "usage": {"priority": "core", "register": "neutral"},
                        "learnerExplanationEn": (
                            f"{MARK}: this invented frame is followed by "
                            "another verb, not by a case."
                        ),
                        "activityEligibility": [],
                    },
                    {
                        "key": "recipient-clause",
                        "relationType": "lexical-frame",
                        "complements": [
                            {
                                "type": "case", "case": "dative",
                                "required": True, "role": "recipient",
                            },
                            {
                                "type": "clause", "clauseKind": "ze",
                                "required": True, "role": "content",
                            },
                        ],
                        "cefr": {"recognition": "B1", "production": "B1"},
                        "teachingStatus": "active-production",
                        "usage": {"priority": "common", "register": "neutral"},
                        "learnerExplanationEn": (
                            f"{MARK}: this invented frame mixes one case slot "
                            "with a clause."
                        ),
                        "activityEligibility": [],
                        "example": (
                            "clause-context",
                            f"{MARK}: bezokolicznikuję obiektowi, że to test.",
                            f"{MARK}: I report to the invented object that "
                            "this is a test.",
                        ),
                    },
                ],
            )]),
            # 5. a Nominative subject beside a Dative experiencer.
            _lemma("podobnikować się", "imperfective", [(
                "experiencer-sense",
                [f"{MARK}: appeal to an invented person"],
                f"{MARK}: invented sense; exercises subject-experiencer.",
                [{
                    "key": "subject-and-experiencer",
                    "relationType": "subject-experiencer",
                    "complements": [
                        {
                            "type": "case", "case": "nominative",
                            "required": True, "role": "subject",
                        },
                        {
                            "type": "case", "case": "dative",
                            "required": True, "role": "experiencer",
                        },
                    ],
                    "cefr": {"recognition": "A2"},
                    "teachingStatus": "recognition-only",
                    "usage": {"priority": "common", "register": "neutral"},
                    "learnerExplanationEn": (
                        f"{MARK}: in this invented frame the roles are the "
                        "other way round from English."
                    ),
                    "activityEligibility": ["reference"],
                }],
            )]),
            # 6. a display lemma that is long on purpose, and a predicate slot.
            _lemma(
                "konstrukcjować", "imperfective",
                [(
                    "role-sense",
                    [f"{MARK}: hold an invented role"],
                    f"{MARK}: invented sense; exercises a predicate slot.",
                    [{
                        "key": "predicate-instrumental",
                        "relationType": "constructional-frame",
                        "complements": [{
                            "type": "case", "case": "instrumental",
                            "required": True, "role": "predicate",
                        }],
                        "cefr": {"recognition": "A1", "production": "A1"},
                        "teachingStatus": "active-production",
                        "usage": {"priority": "core", "register": "neutral"},
                        "learnerExplanationEn": (
                            f"{MARK}: this invented frame names a role rather "
                            "than an object." + LONG_TAIL
                        ),
                        "activityEligibility": ["reference", "search"],
                    }],
                )],
                display=(
                    "konstrukcjować (" + MARK.lower()
                    + " display form, deliberately long)"
                ),
            ),
        ],
    }
    for lemma in document["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                pattern["reviewEvents"] = _acceptance_events(
                    lemma, meaning, pattern)
    return document


def _cli_context():
    return ValidationContext(
        source_registry=synthetic_context_document()["sourceRegistry"],
        reviewer_registry=synthetic_context_document()["reviewerRegistry"],
        author_registry=synthetic_context_document()["authorRegistry"],
    )


def regenerate_fixture_bytes():
    """Run the existing non-release CLI exactly as the fixture was produced."""
    document = synthetic_editorial_document()
    with tempfile.TemporaryDirectory(prefix="priority7-phase3b-") as work:
        editorial_path = Path(work) / "synthetic-editorial.json"
        context_path = Path(work) / "synthetic-context.json"
        editorial_path.write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        context_path.write_text(
            json.dumps(synthetic_context_document(), ensure_ascii=False,
                       indent=2) + "\n",
            encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable, "priority7_tooling.py", "project-fixture",
                str(editorial_path), "--test-pattern-data-revision", "1",
                "--context", str(context_path),
            ],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
    return result


class SyntheticFixtureTests(unittest.TestCase):
    """The fixture is generated, wrapped, and only ever a test input."""

    @classmethod
    def setUpClass(cls):
        cls.raw = FIXTURE_PATH.read_text(encoding="utf-8")
        cls.fixture = json.loads(cls.raw)

    def test_synthetic_editorial_document_validates_with_zero_issues(self):
        issues = validate_editorial(
            synthetic_editorial_document(), _cli_context())
        self.assertEqual([], [str(issue) for issue in issues])

    def test_committed_fixture_is_exactly_what_project_fixture_emits(self):
        result = regenerate_fixture_bytes()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(
            self.raw, result.stdout,
            "The committed fixture must be byte-identical to a fresh "
            "project-fixture run over the synthetic editorial document, so it "
            "cannot be hand-edited into a different document.")

    def test_fixture_is_wrapped_and_explicitly_not_release_authorized(self):
        self.assertEqual(
            ["artifactStatus", "releaseAuthorized", "runtimeProjection"],
            list(self.fixture))
        self.assertEqual(
            NONRELEASE_PROJECTION_STATUS, self.fixture["artifactStatus"])
        self.assertIs(False, self.fixture["releaseAuthorized"])
        self.assertEqual(
            "priority-7-runtime-projection-nonrelease-fixture",
            self.fixture["artifactStatus"],
            "The wrapper string is the visible guard; the shipping loader "
            "refuses any document carrying it.")

    def test_projection_inside_the_wrapper_is_a_valid_runtime_shape(self):
        projection = self.fixture["runtimeProjection"]
        self.assertEqual(
            ["formatVersion", "patternDataRevision", "lemmas"],
            list(projection))
        self.assertEqual(1, projection["formatVersion"])
        self.assertEqual(1, projection["patternDataRevision"])
        self.assertEqual(
            [], [str(issue) for issue in
                 validate_runtime(projection, ValidationContext())])

    def test_projection_is_not_a_release_and_says_so_nowhere_else(self):
        """validate_runtime passing is not release authorization."""
        projection = self.fixture["runtimeProjection"]
        self.assertNotIn("artifactStatus", projection)
        self.assertNotIn("releaseAuthorized", projection)
        # The projector is the non-release path: it cannot be reached with a
        # release revision claim, and its output is wrapped again here.
        rewrapped = project_nonrelease_fixture(
            synthetic_editorial_document(), 1, _cli_context())
        self.assertIs(False, rewrapped["releaseAuthorized"])
        self.assertEqual(projection, rewrapped["runtimeProjection"])

    def test_fixture_covers_every_shape_the_phase_3b_ui_must_render(self):
        lemmas = self.fixture["runtimeProjection"]["lemmas"]
        patterns = [
            pattern for lemma in lemmas for meaning in lemma["meanings"]
            for pattern in meaning["patterns"]
        ]
        complement_types = {
            complement["type"] for pattern in patterns
            for complement in pattern["complements"]
        }
        cases = {
            complement.get("case") for pattern in patterns
            for complement in pattern["complements"]
            if complement.get("case")
        }
        self.assertEqual(6, len(lemmas))
        self.assertEqual(10, len(patterns))
        self.assertEqual(
            {"case", "preposition-case", "infinitive", "clause"},
            complement_types)
        self.assertEqual(
            {"nominative", "genitive", "dative", "accusative", "instrumental",
             "locative"},
            cases,
            "Six cases occur; Vocative cannot occur, because the validator "
            "forbids it as a complement.")
        self.assertTrue(any(len(lemma["meanings"]) > 1 for lemma in lemmas))
        self.assertTrue(any(
            len(meaning["patterns"]) > 1 for lemma in lemmas
            for meaning in lemma["meanings"]))
        self.assertTrue(any(
            len(pattern["complements"]) > 1 for pattern in patterns))
        self.assertTrue(any(lemma["reflexive"] for lemma in lemmas))
        self.assertTrue(any(
            pattern["teachingStatus"] == "recognition-only"
            for pattern in patterns))
        self.assertTrue(any(
            pattern["cefr"].get("production") != pattern["cefr"]["recognition"]
            for pattern in patterns))
        self.assertTrue(any("examples" in pattern for pattern in patterns))
        self.assertTrue(any("examples" not in pattern for pattern in patterns))
        self.assertTrue(any(
            len(pattern["learnerExplanationEn"]) > 200 for pattern in patterns))
        self.assertTrue(any(
            HOSTILE in pattern["learnerExplanationEn"] for pattern in patterns),
            "The hostile string must survive the pipeline as data so the UI "
            "test can prove it is never parsed as markup.")

    def test_fixture_holds_no_private_editorial_field_at_any_depth(self):
        from priority7_tooling import PRIVATE_RUNTIME_KEYS

        def keys(value):
            if isinstance(value, dict):
                for key, nested in value.items():
                    yield key
                    yield from keys(nested)
            elif isinstance(value, list):
                for item in value:
                    yield from keys(item)

        found = set(keys(self.fixture["runtimeProjection"]))
        self.assertEqual(set(), found & PRIVATE_RUNTIME_KEYS)
        # The wrapper itself is exempt by design: artifactStatus is the guard.
        self.assertIn("artifactStatus", self.fixture)

    def test_fixture_contains_no_real_editorial_lemma_or_gloss(self):
        corpus = json.loads(EDITORIAL_CORPUS.read_text(encoding="utf-8"))
        historical = priority7_corpus(corpus)
        real_lemmas = set()
        real_glosses = set()
        for lemma in corpus["lemmas"]:
            real_lemmas.add(lemma["canonicalLemma"])
            for meaning in lemma["meanings"]:
                real_glosses.update(meaning["glossesEn"])
        self.assertEqual(45, sum(
            len(meaning["patterns"]) for lemma in historical["lemmas"]
            for meaning in lemma["meanings"]))
        haystack = self.raw
        for lemma in sorted(real_lemmas):
            with self.subTest(lemma=lemma):
                self.assertNotIn(lemma, haystack)
        # Glosses are compared as whole strings, plus as substrings once they
        # are long enough to be distinctive: a real corpus gloss of "have" says
        # nothing about leakage, while "talk / have a conversation" would.
        fixture_glosses = {
            gloss
            for lemma in self.fixture["runtimeProjection"]["lemmas"]
            for meaning in lemma["meanings"]
            for gloss in meaning["glossesEn"]
        }
        self.assertEqual(set(), fixture_glosses & real_glosses)
        for gloss in sorted(real_glosses):
            if len(gloss) < 12:
                continue
            with self.subTest(gloss=gloss):
                self.assertNotIn(gloss, haystack)
        for lemma in self.fixture["runtimeProjection"]["lemmas"]:
            self.assertNotIn(lemma["canonicalLemma"], real_lemmas)
            for meaning in lemma["meanings"]:
                self.assertIn(MARK, " ".join(meaning["glossesEn"]))

    def test_real_editorial_corpus_exposes_no_learner_activity_or_audio(self):
        """Phase 4F-A raised review states; it exposed nothing to a learner.

        Reference verification is tier 1 of three.  Activity eligibility and
        audio both require ``approved``, which needs an editorial review and a
        human product approval that do not exist, so both must still be zero.

        Phase 4F-E1 later added tier 2.  Its approved governance work is
        reverted before the historical state claim is made, so that claim
        still means exactly what it meant when it was written.  The learner
        exposure counts are deliberately taken from the LIVE corpus instead:
        editorial review must not have exposed anything either, and asserting
        that against the normalised copy would not prove it.
        """
        live = json.loads(EDITORIAL_CORPUS.read_text(encoding="utf-8"))
        corpus = E1.without_phase_4fe1_editorial_review(
            F2.without_phase_4ff2_product_approval(
                H2.without_phase_4fh2_content_completion(
                    H21.without_phase_4fh21_product_reapproval(live))))
        corpus = priority7_corpus(corpus)
        states, kinds, eligibility, audio = [], [], 0, 0
        for lemma in corpus["lemmas"]:
            for meaning in lemma["meanings"]:
                for pattern in meaning["patterns"]:
                    states.append(pattern["reviewState"])
                    kinds.extend(event["kind"]
                                 for event in pattern["reviewEvents"])
        for lemma in live["lemmas"]:
            for meaning in lemma["meanings"]:
                for pattern in meaning["patterns"]:
                    eligibility += len(pattern["activityEligibility"])
                    audio += sum(
                        1 for example in pattern.get("examples", [])
                        if example["audioEligible"])
        self.assertEqual(45, len(states))
        self.assertEqual({"reference-verified"}, set(states))
        self.assertEqual({"reference-verification"}, set(kinds))
        self.assertEqual(0, eligibility)
        self.assertEqual(0, audio)


class FixtureIsolationTests(unittest.TestCase):
    """The fixture is a test input and may never become a public artefact."""

    def test_fixture_lives_only_under_the_approved_test_path(self):
        self.assertTrue(FIXTURE_PATH.is_file())
        present = sorted(
            str(path.relative_to(FIXTURE_DIR))
            for path in FIXTURE_DIR.rglob("*") if path.is_file())
        # NARROWED by Priority 7 Phase 3D-1, not relaxed.  That phase adds the
        # synthetic grammar-choose mechanics records as a second wrapped,
        # explicitly non-release file in this same test-only directory, and the
        # invariant stays "exactly these, and nothing else".  Its own wrapper is
        # asserted by tests/test_priority7_phase3d1.py and by
        # DeploymentIsolationTests; the runtime fixture below is untouched, so
        # the byte-for-byte regeneration test still holds it down exactly.
        # NARROWED again by Priority 7 Phase 5-A, not relaxed.  That phase adds
        # the synthetic private editorial fixture it freezes and the test-only
        # JXA harness that drives the shipping loader over the resulting
        # projection.  Neither is a runtime document and neither is reachable
        # from any public surface; the invariant stays "exactly these, and
        # nothing else".
        self.assertEqual(
            ["exercise-fixture.json", "phase5a-loader-harness.js",
             "release-runtime-fixture.json", "runtime-fixture.json",
             "synthetic-release-editorial.json"], present,
            "tests/fixtures/priority7 holds exactly the two wrapped "
            "non-release fixtures, the bare synthetic Phase 3F-A public-shape "
            "rehearsal fixture, and the Phase 5-A synthetic editorial fixture "
            "and loader harness, and nothing else.")
        for forbidden in ("content", "grammar", "vocabulary", "guide"):
            for name in ("runtime-fixture.json", "exercise-fixture.json"):
                self.assertFalse((ROOT / forbidden / name).exists())

    def test_no_public_priority7_runtime_artifact_exists(self):
        # Superseded by Phase 4F-I1, which materialised the official runtime.
        # The claim that survives is the one this phase was actually making:
        # no runtime document exists here other than exactly the I1 release
        # artifact, whose bytes the normaliser pins by digest.
        self.assertEqual("complete", i1_bundle().state)

    def test_fixture_content_cannot_enter_a_public_surface(self):
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        worker = (ROOT / "sw.js").read_text(encoding="utf-8")
        loader = (ROOT / "pp-verb-patterns.js").read_text(encoding="utf-8")
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        outputs, _, _ = build_pages.build_outputs(str(ROOT))
        public_text = "\n".join(
            [index, worker, loader, sitemap, *outputs.values()])
        for marker in (
            "tests/fixtures", "runtime-fixture.json", MARK, HOSTILE,
            NONRELEASE_PROJECTION_STATUS, "runtimeProjection",
            "releaseAuthorized", "editorial/",
        ):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, public_text)
        # Nor may any synthetic lemma appear in a shipped file.
        for lemma in json.loads(
                FIXTURE_PATH.read_text(encoding="utf-8")
        )["runtimeProjection"]["lemmas"]:
            with self.subTest(lemma=lemma["canonicalLemma"]):
                self.assertNotIn(lemma["canonicalLemma"], public_text)
        self.assertEqual(32, len(ET.fromstring(sitemap)))

    def test_shipping_code_cannot_unwrap_the_fixture_envelope(self):
        """The unwrap step exists in test code only (contract 4.5a)."""
        loader = (ROOT / "pp-verb-patterns.js").read_text(encoding="utf-8")
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        for source, name in ((loader, "pp-verb-patterns.js"),
                             (index, "index.html")):
            with self.subTest(source=name):
                self.assertNotIn("runtimeProjection", source)
                self.assertNotIn("releaseAuthorized", source)
        self.assertNotIn(
            "__acceptForTest", index,
            "The test-only injection entry point must never be referenced "
            "from the shipping application.")
    def test_loader_mirrors_the_private_key_rejection_list_exactly(self):
        """The rejection list is complete, and it is a rejection list only."""
        from priority7_tooling import PRIVATE_RUNTIME_KEYS

        loader = (ROOT / "pp-verb-patterns.js").read_text(encoding="utf-8")
        block = re.search(
            r"var PRIVATE_KEYS = \[(.*?)\];", loader, re.S).group(1)
        listed = set(re.findall(r'"([^"]+)"', block))
        self.assertEqual(
            PRIVATE_RUNTIME_KEYS, listed,
            "A private key the browser does not know about is a private key "
            "the browser cannot refuse.")
        # Naming a key in order to refuse it is not reading it.  No private
        # field may be read, in any access form, anywhere in the loader.  The
        # bare name `key` is excluded from this sweep only because the loader's
        # own view objects carry an opaque integer `key`; its rejection is
        # covered by the list assertion above and by the JXA suite, which feeds
        # a document carrying an immutable authoring key and asserts refusal.
        for key in sorted(PRIVATE_RUNTIME_KEYS - {"key"}):
            for access in (f".{key}", f'["{key}"]', f"['{key}']"):
                with self.subTest(access=access):
                    self.assertNotIn(access, loader)

    def test_loader_makes_no_release_or_review_claim(self):
        loader = (ROOT / "pp-verb-patterns.js").read_text(encoding="utf-8")
        for forbidden in (
            "releaseAuthorized", "runtimeProjection", "approved", "verified",
            "nativeReview", "native-review", "isRelease", "released",
        ):
            with self.subTest(token=forbidden):
                self.assertNotIn(forbidden, loader)

    def test_loader_owns_no_global_network_storage_or_dom_api(self):
        loader = (ROOT / "pp-verb-patterns.js").read_text(encoding="utf-8")
        for forbidden in (
            "fetch(", "XMLHttpRequest", "localStorage", "sessionStorage",
            "indexedDB", "innerHTML", "eval(", "document.getElementById",
            "document.createElement", "document.querySelector",
            "textContent", "window.", "location", "navigator",
        ):
            with self.subTest(token=forbidden):
                self.assertNotIn(forbidden, loader)
        self.assertEqual(
            1, loader.count('request(url, { cache: "no-store" })'),
            "Phase 3F-A may call only the explicitly injected request "
            "dependency; it must not acquire a global fetch path.")

    def test_the_surface_exists_without_any_runtime_request(self):
        """The entry is ordinary information architecture, not fetch-gated.

        Phase 3B ships the Grammar -> Verb Patterns entry unconditionally so the
        no-data state is a real, reachable, testable state.  Nothing about
        creating or opening it may reach the network: the future public runtime
        file, its fetch, its service-worker entries and its cache bump are one
        atomic release concern, and none of them is present here.
        """
        index = pre_i1("index.html")
        self.assertIn(
            'LEVELS.push({ level:"Verb Patterns", group:"grammar",', index)
        self.assertNotIn("if(PP_VERB_PATTERNS && PP_VERB_PATTERNS.available){", index)
        self.assertEqual(1, index.count('level:"Verb Patterns"'))
        # The two pre-existing fetches are the audio manifest and the freshness
        # HEAD; this phase adds none, and names no runtime path to fetch.
        self.assertEqual(2, index.count("fetch("))
        self.assertNotIn("content/", index)
        self.assertNotIn("verb-patterns.json", index)
        for token in ("XMLHttpRequest", "EventSource", "importScripts"):
            with self.subTest(token=token):
                self.assertNotIn(token, index)

    def test_ordinary_startup_reads_no_fixture_and_no_editorial_file(self):
        """Startup can reach neither the fixture nor the private workspace.

        Path and data references only.  Two comments in the shell explain that
        editorial *terms* never reach the screen, and the loader must NAME the
        private keys in order to refuse them - neither is a way to open a file.
        """
        index = pre_i1("index.html")
        loader = (ROOT / "pp-verb-patterns.js").read_text(encoding="utf-8")
        for source, name in ((index, "index.html"), (loader, "pp-verb-patterns.js")):
            for token in ('"tests/', "'tests/", "runtime-fixture",
                          "editorial/", "fixtures"):
                with self.subTest(source=name, token=token):
                    self.assertNotIn(token, source)
        # The injection entry point is defined in the loader and referenced by
        # the test harness; the shipping shell must not know it exists.
        self.assertNotIn("__acceptForTest", index)
        # Nothing in the verb-pattern surface parses a document of its own: the
        # only parse in the shell is the pre-existing progress store.
        patterns_block = index[
            index.index("const P = { li:0, ti:0, topicRef:null"):
            index.index("/* ---------------- grammar (teach -> drill) ---------------- */")
        ]
        for token in ("JSON.parse", "JSON.stringify", "fetch(", "await"):
            with self.subTest(token=token):
                self.assertNotIn(token, patterns_block)
                self.assertNotIn(token, loader)

    def test_version_and_cache_markers_are_untouched_by_this_phase(self):
        index = pre_i1("index.html")
        worker = pre_i1("sw.js")
        migrate = (ROOT / "pp-migrate.js").read_text(encoding="utf-8")
        self.assertEqual(
            "8.10", re.search(r'APP_VERSION\s*=\s*"([^"]+)"', index).group(1))
        self.assertEqual(
            "popolsku-v65",
            re.search(r'CACHE\s*=\s*"([^"]+)"', worker).group(1))
        self.assertEqual(
            "popolsku-audio",
            re.search(r'AUDIO_CACHE\s*=\s*"([^"]+)"', worker).group(1))
        self.assertEqual(
            "2", re.search(r"SCHEMA_VERSION\s*[:=]\s*(\d+)", migrate).group(1))
        self.assertEqual(
            "2",
            re.search(r"CONTENT_MIGRATION_REVISION\s*[:=]\s*(\d+)",
                      migrate).group(1))
        self.assertNotIn("patternDataRevision", index)
        self.assertNotIn("patternDataRevision", worker)
        self.assertNotIn("verb-patterns.json", worker)


if __name__ == "__main__":
    unittest.main()
