import copy
import glob
import hashlib
import difflib
import json
import re
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

import build_pages

from priority7_tooling import (
    RepositoryIndex,
    ValidationContext,
    ValidationFailure,
    allocate_example_id,
    allocate_exercise_id,
    allocate_lemma_id,
    allocate_meaning_id,
    allocate_pattern_id,
    canonicalize_rfc8785,
    evidence_digest,
    freeze_editorial,
    lemma_slug,
    normalize_canonical_lemma,
    pattern_readable_stem,
    project_nonrelease_fixture,
    project_runtime_nonrelease,
    repository_index_from_root,
    review_scope_digest,
    validate_editorial,
    validate_frozen_release,
    validate_runtime,
    validate_specification_fixture,
    verified_runtime_from_frozen,
)


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
FICTIONAL_LEMMA = "fikcjonować"
FICTIONAL_MEANING_KEY = "test-content"
FICTIONAL_PATTERN_KEY = "direct-target"
FIXTURE_CARD_ID = "p7-fixture-card-001"
FIXTURE_CARD_2_ID = "p7-fixture-card-002"
FIXTURE_DRILL_ID = "p7-fixture-drill-001"
FIXTURE_REUSED_SENTENCE = (
    "ZNACZNIK-NIEPRODUKCYJNY: fikcyjny operator oznacza obiekt testowy."
)

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


def injected_sources():
    """Existing-corpus shape, held only in memory and unmistakably nonproduction."""
    return [{
        "source": "p7-fixture-memory",
        "sourceIssues": [],
        "levels": [{
            "id": "p7-fixture-level",
            "level": "NONPRODUCTION FIXTURE",
            "blurb": "Priority 7 fictional tooling fixture.",
            "topics": [{
                "id": "p7-fixture-topic",
                "name": "NONPRODUCTION FIXTURE",
                "cards": [
                    {
                        "id": FIXTURE_CARD_ID,
                        "pl": "ZNACZNIK-NIEPRODUKCYJNY: fikcjonuję obiekt.",
                        "en": "NONPRODUCTION-FIXTURE: I fiction-test an object.",
                        "ex": FIXTURE_REUSED_SENTENCE,
                        "exEn": "NONPRODUCTION-FIXTURE: a fictional operator marks a test object.",
                    },
                    {
                        "id": FIXTURE_CARD_2_ID,
                        "pl": "ZNACZNIK-NIEPRODUKCYJNY: drugi obiekt.",
                        "en": "NONPRODUCTION-FIXTURE: second object.",
                        "ex": "ZNACZNIK-NIEPRODUKCYJNY: fikcjonuję obiekt B.",
                        "exEn": "NONPRODUCTION-FIXTURE: I fiction-test object B.",
                    },
                ],
                "drills": [{
                    "id": FIXTURE_DRILL_ID,
                    "type": "choose",
                    "prompt": "ZNACZNIK-NIEPRODUKCYJNY: ___ obiekt testowy.",
                    "answer": "fikcjonuję",
                    "full": "ZNACZNIK-NIEPRODUKCYJNY: fikcjonuję obiekt testowy.",
                }],
            }],
        }],
    }]


def validation_context(repository_index=None):
    if repository_index is None:
        repository_index = RepositoryIndex.from_sources(injected_sources())
    return ValidationContext(
        source_registry={
            "fixture-reference": {"sourceKind": "contemporary-reference"},
            "fixture-corroboration": {"sourceKind": "contemporary-corpus"},
            "phase1-specification-fixture": {"sourceKind": "repository"},
        },
        reviewer_registry={
            "fixture-external-human": {
                "human": True,
                "roles": ["external-verification"],
            },
            "fixture-native-human": {
                "human": True,
                "roles": ["native-linguistic"],
            },
            "fixture-product-human": {
                "human": True,
                "roles": ["product-approval", "correction", "reopen"],
            },
        },
        author_registry={"fixture-human-author": {"human": True}},
        repository_index=repository_index,
        today=date(2026, 8, 9),
    )


def parts(document, lemma_index=0, meaning_index=0, pattern_index=0):
    lemma = document["lemmas"][lemma_index]
    meaning = lemma["meanings"][meaning_index]
    pattern = meaning["patterns"][pattern_index]
    return lemma, meaning, pattern


def acceptance_events(lemma, meaning, pattern, reviewed_at="2026-08-08"):
    external = review_scope_digest(
        "external-verification", lemma, meaning, pattern)
    native = review_scope_digest("native-linguistic", lemma, meaning, pattern)
    product = review_scope_digest("product-approval", lemma, meaning, pattern)
    return [
        {
            "kind": "external-verification",
            "decision": "accept",
            "scopeVersion": 1,
            "scopeDigest": external,
            "supportingEvidenceDigests": sorted(
                [evidence_digest(pattern["evidence"][0])]),
            "reviewerRef": "fixture-external-human",
            "reviewedAt": reviewed_at,
        },
        {
            "kind": "native-linguistic",
            "decision": "accept",
            "scopeVersion": 1,
            "scopeDigest": native,
            "reviewerRef": "fixture-native-human",
            "reviewedAt": reviewed_at,
        },
        {
            "kind": "product-approval",
            "decision": "accept",
            "scopeVersion": 1,
            "scopeDigest": product,
            "reviewerRef": "fixture-product-human",
            "reviewedAt": reviewed_at,
        },
    ]


def refresh_acceptance(document, audit_events=()):
    for lemma in document["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                if pattern.get("reviewState") == "approved":
                    pattern["reviewEvents"] = acceptance_events(
                        lemma, meaning, pattern)
                    pattern["reviewEvents"].extend(copy.deepcopy(audit_events))
    return document


def append_stage_acceptances(document, reviewed_at="2026-08-09"):
    for lemma in document["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                if pattern.get("reviewState") == "approved":
                    pattern["reviewEvents"].extend(
                        acceptance_events(
                            lemma, meaning, pattern, reviewed_at=reviewed_at))
    return document


def append_correction_and_acceptances(document, note):
    for lemma in document["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                if pattern.get("reviewState") != "approved":
                    continue
                pattern["reviewEvents"].append({
                    "kind": "correction",
                    "decision": "accept",
                    "reviewerRef": "fixture-product-human",
                    "reviewedAt": "2026-08-09",
                    "note": note,
                })
                pattern["reviewEvents"].extend(acceptance_events(
                    lemma, meaning, pattern, reviewed_at="2026-08-09"))
    return document


def fictional_editorial():
    lemma_id = allocate_lemma_id(FICTIONAL_LEMMA)
    meaning_id = allocate_meaning_id(
        lemma_id, FICTIONAL_LEMMA, FICTIONAL_MEANING_KEY)
    pattern_id = allocate_pattern_id(
        meaning_id,
        FICTIONAL_LEMMA,
        FICTIONAL_MEANING_KEY,
        FICTIONAL_PATTERN_KEY,
    )
    document = {
        "artifactStatus": "priority-7-editorial-nonproduction",
        "formatVersion": 1,
        "lemmas": [{
            "id": lemma_id,
            "canonicalLemma": FICTIONAL_LEMMA,
            "displayLemma": "FIKCJONOWAĆ — NONPRODUCTION FIXTURE",
            "reflexive": False,
            "aspect": "biaspectual",
            "meanings": [{
                "id": meaning_id,
                "key": FICTIONAL_MEANING_KEY,
                "glossesEn": ["perform an explicitly fictional test action"],
                "internalScope": (
                    "NONPRODUCTION FIXTURE: invented tooling sense; no linguistic claim."
                ),
                "patterns": [{
                    "id": pattern_id,
                    "key": FICTIONAL_PATTERN_KEY,
                    "relationType": "lexical-frame",
                    "complements": [{
                        "type": "case",
                        "case": "accusative",
                        "required": True,
                        "role": "object",
                    }],
                    "cefr": {"recognition": "A1", "production": "A1"},
                    "teachingStatus": "active-production",
                    "usage": {"priority": "core", "register": "neutral"},
                    "learnerExplanationEn": (
                        "NONPRODUCTION FIXTURE: demonstrates one direct case slot."
                    ),
                    "activityEligibility": [
                        "reference",
                        "search",
                        "grammar-choose",
                        "grammar-build",
                        "type-it",
                        "listening",
                    ],
                    "evidence": [{
                        "sourceId": "fixture-reference",
                        "sourceKind": "contemporary-reference",
                        "locator": "fixture://nonproduction/direct-target",
                        "factType": "complement-frame",
                        "checkedAt": "2026-08-08",
                        "note": "Invented evidence record for deterministic tooling tests only.",
                    }],
                    "reviewState": "approved",
                    "reviewEvents": [],
                    "examples": [
                        {
                            "id": allocate_example_id(pattern_id, "original-context"),
                            "key": "original-context",
                            "pl": (
                                "ZNACZNIK-NIEPRODUKCYJNY: fikcjonuję obiekt A."
                            ),
                            "en": (
                                "NONPRODUCTION-FIXTURE: I fiction-test object A."
                            ),
                            "origin": {
                                "kind": "original",
                                "authorRef": "fixture-human-author",
                                "authoredAt": "2026-08-08",
                            },
                            "audioEligible": True,
                        },
                        {
                            "id": allocate_example_id(pattern_id, "repository-context"),
                            "key": "repository-context",
                            "pl": FIXTURE_REUSED_SENTENCE,
                            "en": (
                                "NONPRODUCTION-FIXTURE: a fictional operator marks a test object."
                            ),
                            "origin": {
                                "kind": "repository-reuse",
                                "repositorySource": {
                                    "kind": "card",
                                    "id": FIXTURE_CARD_ID,
                                    "field": "ex",
                                },
                            },
                            "audioEligible": False,
                        },
                    ],
                    "contentRefs": [{
                        "kind": "card",
                        "id": FIXTURE_CARD_ID,
                        "purpose": "support",
                    }],
                    "errorNotes": [{
                        "kind": "predicted-distractor",
                        "incorrectForm": "ZNACZNIK-NIEPRODUKCYJNY-BŁĄD",
                        "guidanceEn": (
                            "NONPRODUCTION FIXTURE: choose the marked fictional form."
                        ),
                    }],
                }],
            }],
        }],
    }
    return refresh_acceptance(document)


def add_deferred_pattern(document, key="deferred-frame"):
    lemma, meaning, _ = parts(document)
    pattern_id = allocate_pattern_id(
        meaning["id"], lemma["canonicalLemma"], meaning["key"], key)
    meaning["patterns"].append({
        "id": pattern_id,
        "key": key,
        "relationType": "lexical-frame",
        "complements": [{
            "type": "preposition-case",
            "preposition": "za",
            "case": "accusative",
            "required": True,
            "role": "target",
        }],
        "cefr": {"recognition": "above-b1"},
        "teachingStatus": "deferred",
        "usage": {
            "priority": "limited",
            "register": "neutral",
            "note": "NONPRODUCTION FIXTURE: deliberately deferred.",
        },
        "learnerExplanationEn": (
            "NONPRODUCTION FIXTURE: hidden alternate fictional frame."
        ),
        "activityEligibility": [],
        "evidence": [{
            "sourceId": "fixture-reference",
            "sourceKind": "contemporary-reference",
            "locator": "fixture://nonproduction/deferred-frame",
            "factType": "complement-frame",
            "checkedAt": "2026-08-08",
        }],
        "reviewState": "research",
        "reviewEvents": [],
    })
    return pattern_id


def add_approved_pattern(document, key="approved-alternate-frame"):
    """Add a second fictional approved pattern with freshly allocated IDs."""
    lemma, meaning, template = parts(document)
    pattern = copy.deepcopy(template)
    pattern_id = allocate_pattern_id(
        meaning["id"], lemma["canonicalLemma"], meaning["key"], key)
    pattern["id"] = pattern_id
    pattern["key"] = key
    for example in pattern.get("examples", []):
        example["id"] = allocate_example_id(pattern_id, example["key"])
    meaning["patterns"].append(pattern)
    refresh_acceptance(document)
    return pattern_id


def fictional_corroboration(locator_suffix="corroboration"):
    return {
        "sourceId": "fixture-corroboration",
        "sourceKind": "contemporary-corpus",
        "locator": f"fixture://nonproduction/{locator_suffix}",
        "factType": "contrast",
        "checkedAt": "2026-08-08",
        "note": "Independent fictional corroboration for safety tests.",
    }


def add_terminal_pattern(document, key, decision):
    pattern_id = add_deferred_pattern(document, key)
    pattern = parts(document)[1]["patterns"][-1]
    pattern["reviewState"] = "deferred" if decision == "defer" else "rejected"
    pattern["reviewEvents"] = [{
        "kind": "external-verification",
        "decision": decision,
        "reviewerRef": "fixture-external-human",
        "reviewedAt": "2026-08-08",
        "note": f"NONPRODUCTION FIXTURE {decision} terminal decision.",
    }]
    return pattern_id


def add_fictional_aspect_partner(document):
    first_lemma, _, _ = parts(document)
    canonical = "partnerofikcjonować"
    lemma_id = allocate_lemma_id(canonical)
    meaning_key = "partner-test-content"
    meaning_id = allocate_meaning_id(lemma_id, canonical, meaning_key)
    pattern_key = "partner-direct-target"
    pattern_id = allocate_pattern_id(
        meaning_id, canonical, meaning_key, pattern_key)
    partner_pattern = {
        "id": pattern_id,
        "key": pattern_key,
        "relationType": "lexical-frame",
        "complements": [{
            "type": "case",
            "case": "accusative",
            "required": True,
            "role": "object",
        }],
        "cefr": {"recognition": "A1", "production": "A1"},
        "teachingStatus": "active-production",
        "usage": {"priority": "core", "register": "neutral"},
        "learnerExplanationEn": (
            "NONPRODUCTION FIXTURE: fictional aspect-partner frame."
        ),
        "activityEligibility": [],
        "evidence": [{
            "sourceId": "fixture-reference",
            "sourceKind": "contemporary-reference",
            "locator": "fixture://nonproduction/aspect-partner",
            "factType": "complement-frame",
            "checkedAt": "2026-08-08",
        }],
        "reviewState": "research",
        "reviewEvents": [],
    }
    partner_meaning = {
        "id": meaning_id,
        "key": meaning_key,
        "glossesEn": ["perform a fictional partner test action"],
        "internalScope": "NONPRODUCTION FIXTURE aspect partner scope.",
        "patterns": [partner_pattern],
    }
    partner_lemma = {
        "id": lemma_id,
        "canonicalLemma": canonical,
        "displayLemma": "PARTNEROFIKCJONOWAĆ — NONPRODUCTION FIXTURE",
        "reflexive": False,
        "aspect": "perfective",
        "aspectPartnerIds": [first_lemma["id"]],
        "meanings": [partner_meaning],
    }
    first_lemma["aspect"] = "imperfective"
    first_lemma["aspectPartnerIds"] = [lemma_id]
    document["lemmas"].append(partner_lemma)
    refresh_acceptance(document)
    return partner_lemma, partner_meaning, partner_pattern


def specification_fixture():
    lemma_id = allocate_lemma_id(FICTIONAL_LEMMA)
    meaning_id = allocate_meaning_id(
        lemma_id, FICTIONAL_LEMMA, FICTIONAL_MEANING_KEY)
    pattern_id = allocate_pattern_id(
        meaning_id,
        FICTIONAL_LEMMA,
        FICTIONAL_MEANING_KEY,
        FICTIONAL_PATTERN_KEY,
    )
    return {
        "artifactStatus": "specification-example-not-production",
        "specificationNotice": (
            "Fictional Phase 1 fixture only; not learner-facing content."
        ),
        "formatVersion": 1,
        "patternDataRevision": 1,
        "lemmas": [{
            "id": lemma_id,
            "canonicalLemma": FICTIONAL_LEMMA,
            "reflexive": False,
            "aspect": "unresolved",
            "meanings": [{
                "id": meaning_id,
                "key": FICTIONAL_MEANING_KEY,
                "glossesEn": ["perform a fictional test action"],
                "internalScope": "Invented specification-only sense.",
                "patterns": [{
                    "id": pattern_id,
                    "key": FICTIONAL_PATTERN_KEY,
                    "relationType": "lexical-frame",
                    "complements": [{
                        "type": "case",
                        "case": "accusative",
                        "required": True,
                        "role": "object",
                    }],
                    "cefr": {"recognition": "A1"},
                    "teachingStatus": "deferred",
                    "usage": {
                        "priority": "limited",
                        "register": "neutral",
                        "note": "Fictional specification fixture only.",
                    },
                    "learnerExplanationEn": (
                        "Fictional wording demonstrates one direct case slot."
                    ),
                    "activityEligibility": [],
                    "evidence": [{
                        "sourceId": "phase1-specification-fixture",
                        "sourceKind": "repository",
                        "locator": "fixture://phase1/example",
                        "factType": "complement-frame",
                        "checkedAt": "2026-08-08",
                    }],
                    "reviewState": "research",
                    "reviewEvents": [],
                    "examples": [{
                        "id": allocate_example_id(pattern_id, "first-context"),
                        "key": "first-context",
                        "pl": "ZNACZNIK-NIEPRODUKCYJNY: fikcjonuję obiekt.",
                        "en": "NONPRODUCTION-FIXTURE: I fiction-test an object.",
                        "origin": {
                            "kind": "specification-fixture",
                            "authorRef": "fixture-spec-author",
                            "authoredAt": "2026-08-08",
                        },
                        "audioEligible": False,
                    }],
                }],
            }],
        }],
    }


class Phase2ATestCase(unittest.TestCase):
    def assertIssues(self, issues, message=None):
        self.assertTrue(issues, message or "expected validation to fail closed")
        self.assertTrue(
            all(isinstance(issue.code, str) and issue.code for issue in issues),
            issues,
        )

    def assertHasCode(self, issues, code):
        self.assertIn(code, {issue.code for issue in issues}, issues)

    def assertEditorialValid(self, document):
        self.assertEqual([], validate_editorial(document, validation_context()))


class StableIdTests(Phase2ATestCase):
    def test_normalization_transliteration_punctuation_and_lexical_sie(self):
        self.assertEqual(
            "ąćęłńóśźż się",
            normalize_canonical_lemma("  ĄĆĘŁŃÓŚŹŻ\tSIĘ  "),
        )
        self.assertEqual("acelnoszz-sie", lemma_slug("ąćęłńóśźż się"))
        self.assertEqual(
            "fikcjonowac-sie",
            lemma_slug("  FIKCJONOWAĆ!!!   SIĘ "),
        )

    def test_slug_truncation_is_exact_and_drops_a_trailing_hyphen(self):
        long_word = "a" * 40
        self.assertEqual("a" * 32, lemma_slug(long_word))
        ending_at_hyphen = "a" * 31 + " ą"
        self.assertEqual("a" * 31, lemma_slug(ending_at_hyphen))

    def test_same_readable_slug_keeps_distinct_full_identity(self):
        self.assertEqual(lemma_slug("źabać"), lemma_slug("żabać"))
        self.assertNotEqual(allocate_lemma_id("źabać"), allocate_lemma_id("żabać"))
        a = "a" * 32 + "x"
        b = "a" * 32 + "y"
        self.assertEqual(lemma_slug(a), lemma_slug(b))
        self.assertNotEqual(allocate_lemma_id(a), allocate_lemma_id(b))

    def test_empty_slug_is_rejected(self):
        for value in ("---", " !!! ", ""):
            with self.subTest(value=value), self.assertRaises(ValueError):
                lemma_slug(value)

    def test_all_id_families_reproduce_locked_fictional_examples(self):
        lemma_id = allocate_lemma_id("fikcjonować")
        self.assertEqual("vp-l-fikcjonowac-a104036141da", lemma_id)
        meaning_id = allocate_meaning_id(
            lemma_id, "fikcjonować", "test-content")
        self.assertEqual(
            "vp-m-fikcjonowac-test-content-8125d25987aa", meaning_id)
        pattern_id = allocate_pattern_id(
            meaning_id, "fikcjonować", "test-content", "direct-target")
        self.assertEqual(
            "vp-p-fikcjonowac-test-content-direct-target-fe6705e214bf",
            pattern_id,
        )
        self.assertEqual(
            "fikcjonowac-test-content-direct-target",
            pattern_readable_stem(pattern_id),
        )
        self.assertEqual(
            "vp-e-fikcjonowac-test-content-direct-target-first-context-718f9ecca50f",
            allocate_example_id(pattern_id, "first-context"),
        )
        self.assertEqual(
            "vp-x-fikcjonowac-test-content-direct-target-grammar-choose-first-context-ccadf037a929",
            allocate_exercise_id(pattern_id, "grammar-choose", "first-context"),
        )
        self.assertEqual(
            "vp-x-fikcjonowac-test-content-direct-target-grammar-choose-second-context-60e1fb776c5f",
            allocate_exercise_id(pattern_id, "grammar-choose", "second-context"),
        )

    def test_every_phase1_fictional_schema_entity_id_recomputes(self):
        fixtures = (
            (
                "fikcjonować",
                "vp-l-fikcjonowac-a104036141da",
                "test-content",
                "vp-m-fikcjonowac-test-content-8125d25987aa",
                (
                    ("direct-target", "vp-p-fikcjonowac-test-content-direct-target-fe6705e214bf"),
                    ("infinitive-content", "vp-p-fikcjonowac-test-content-infinitive-content-94ebc1d64764"),
                    ("ze-content", "vp-p-fikcjonowac-test-content-ze-content-51c05e2bd5a4"),
                ),
            ),
            (
                "metodować",
                "vp-l-metodowac-31466acb0b90",
                "method-action",
                "vp-m-metodowac-method-action-3af23eb4a46f",
                (
                    ("instrumental-method", "vp-p-metodowac-method-action-instrumental-method-76890bd225e1"),
                    ("za-target", "vp-p-metodowac-method-action-za-target-86f4f3594f38"),
                ),
            ),
            (
                "podobnisić się",
                "vp-l-podobnisic-sie-b94c54f6bbbc",
                "appeal-fiction",
                "vp-m-podobnisic-sie-appeal-fiction-11c4ed0d94d6",
                (("subject-experiencer", "vp-p-podobnisic-sie-appeal-fiction-subject-experiencer-ab4d9407ce34"),),
            ),
            (
                "rolować",
                "vp-l-rolowac-bf32e11727eb",
                "role-fiction",
                "vp-m-rolowac-role-fiction-3bc527fe0052",
                (("predicate-role", "vp-p-rolowac-role-fiction-predicate-role-8761fb770fbd"),),
            ),
        )
        for canonical, lemma_id, meaning_key, meaning_id, patterns in fixtures:
            with self.subTest(canonical=canonical):
                self.assertEqual(lemma_id, allocate_lemma_id(canonical))
                self.assertEqual(
                    meaning_id,
                    allocate_meaning_id(lemma_id, canonical, meaning_key),
                )
                for pattern_key, pattern_id in patterns:
                    self.assertEqual(
                        pattern_id,
                        allocate_pattern_id(
                            meaning_id, canonical, meaning_key, pattern_key),
                    )

    def test_malformed_owning_pattern_ids_and_keys_fail_closed(self):
        malformed = (
            "vp-p-missingdigest",
            "vp-l-wrong-family-0123456789ab",
            "vp-p-empty--0123456789ab",
            "vp-p-upper-ABCDEF012345",
        )
        for pattern_id in malformed:
            with self.subTest(pattern_id=pattern_id), self.assertRaises(ValueError):
                pattern_readable_stem(pattern_id)
        good = allocate_pattern_id(
            allocate_meaning_id(
                allocate_lemma_id(FICTIONAL_LEMMA),
                FICTIONAL_LEMMA,
                FICTIONAL_MEANING_KEY,
            ),
            FICTIONAL_LEMMA,
            FICTIONAL_MEANING_KEY,
            FICTIONAL_PATTERN_KEY,
        )
        for bad_key in ("", "Upper", "two words", "-leading", "trailing-"):
            with self.subTest(key=bad_key), self.assertRaises(ValueError):
                allocate_example_id(good, bad_key)


class CanonicalDigestTests(Phase2ATestCase):
    def test_rfc8785_canonicalization_is_utf8_sorted_and_compact(self):
        self.assertEqual(
            '{"a":"ąć","b":1,"nested":{"x":true}}'.encode("utf-8"),
            canonicalize_rfc8785({
                "nested": {"x": True},
                "b": 1,
                "a": "ąć",
            }),
        )
        self.assertEqual(
            b'{"control":"line\\nquote\\\""}',
            canonicalize_rfc8785({"control": "line\nquote\""}),
        )
        # RFC 8785 sorts object names by UTF-16 code units, not code points.
        self.assertEqual(
            '{"😀":1,"":2}'.encode("utf-8"),
            canonicalize_rfc8785({"\ue000": 2, "😀": 1}),
        )

    def test_floats_and_non_json_values_are_explicitly_rejected(self):
        for value in ({"n": 1.5}, {"value": object()}, {1: "not-a-string-key"}):
            with self.subTest(value=repr(value)), self.assertRaises(TypeError):
                canonicalize_rfc8785(value)
        for value in ({"n": 9_007_199_254_740_992}, {"text": "e\u0301"}):
            with self.subTest(value=repr(value)), self.assertRaises(ValueError):
                canonicalize_rfc8785(value)

    def test_evidence_digest_hashes_the_complete_record_including_note(self):
        evidence = parts(fictional_editorial())[2]["evidence"][0]
        expected = "sha256:" + hashlib.sha256(
            canonicalize_rfc8785(evidence)).hexdigest()
        self.assertEqual(expected, evidence_digest(evidence))
        changed = copy.deepcopy(evidence)
        changed["note"] += " Changed."
        self.assertNotEqual(evidence_digest(evidence), evidence_digest(changed))

    def test_review_scope_sorting_and_stage_boundaries(self):
        base = fictional_editorial()
        lemma, meaning, pattern = parts(base)
        pattern["contentRefs"].append({
            "kind": "card",
            "id": FIXTURE_CARD_2_ID,
            "purpose": "context",
        })
        digests = {
            stage: review_scope_digest(stage, lemma, meaning, pattern)
            for stage in (
                "external-verification",
                "native-linguistic",
                "product-approval",
            )
        }
        self.assertEqual({
            "external-verification": (
                "sha256:a0742fa0765953449d8a78e42a3b0affe18fc37eefbe89f09aef07caff50d063"
            ),
            "native-linguistic": (
                "sha256:341b493380310dcbcfa4e6670afb81ff0b6b9292483a8451ebe4fd39bfce44a3"
            ),
            "product-approval": (
                "sha256:618fb462183b00086ba094c30eb23e7b6dc12ecd6dde8691a9053ba6b2b1c788"
            ),
        }, digests)

        reordered = copy.deepcopy(base)
        r_lemma, r_meaning, r_pattern = parts(reordered)
        r_pattern["activityEligibility"].reverse()
        r_pattern["contentRefs"].reverse()
        self.assertEqual(
            digests["native-linguistic"],
            review_scope_digest(
                "native-linguistic", r_lemma, r_meaning, r_pattern),
        )
        self.assertEqual(
            digests["product-approval"],
            review_scope_digest(
                "product-approval", r_lemma, r_meaning, r_pattern),
        )

        linguistic = copy.deepcopy(base)
        l_lemma, l_meaning, l_pattern = parts(linguistic)
        l_pattern["complements"][0]["required"] = False
        for stage, old in digests.items():
            self.assertNotEqual(
                old,
                review_scope_digest(stage, l_lemma, l_meaning, l_pattern),
                stage,
            )

        learner_copy = copy.deepcopy(base)
        c_lemma, c_meaning, c_pattern = parts(learner_copy)
        c_pattern["learnerExplanationEn"] += " Revised."
        self.assertEqual(
            digests["external-verification"],
            review_scope_digest(
                "external-verification", c_lemma, c_meaning, c_pattern),
        )
        self.assertNotEqual(
            digests["native-linguistic"],
            review_scope_digest(
                "native-linguistic", c_lemma, c_meaning, c_pattern),
        )

        integration = copy.deepcopy(base)
        i_lemma, i_meaning, i_pattern = parts(integration)
        i_pattern["contentRefs"][0]["purpose"] = "context"
        self.assertEqual(
            digests["native-linguistic"],
            review_scope_digest(
                "native-linguistic", i_lemma, i_meaning, i_pattern),
        )
        self.assertNotEqual(
            digests["product-approval"],
            review_scope_digest(
                "product-approval", i_lemma, i_meaning, i_pattern),
        )

        audit = copy.deepcopy(base)
        a_lemma, a_meaning, a_pattern = parts(audit)
        a_pattern["evidence"].append({
            "sourceId": "fixture-corroboration",
            "sourceKind": "contemporary-corpus",
            "locator": "fixture://nonproduction/corroboration",
            "factType": "usage-register",
            "checkedAt": "2026-08-08",
        })
        for stage, old in digests.items():
            self.assertEqual(
                old,
                review_scope_digest(stage, a_lemma, a_meaning, a_pattern),
                stage,
            )

        audit_event = copy.deepcopy(base)
        e_lemma, e_meaning, e_pattern = parts(audit_event)
        e_pattern["reviewEvents"].append({
            "kind": "correction",
            "decision": "accept",
            "reviewerRef": "fixture-product-human",
            "reviewedAt": "2026-08-09",
            "note": "NONPRODUCTION FIXTURE append-only audit event.",
        })
        for stage, old in digests.items():
            self.assertEqual(
                old,
                review_scope_digest(stage, e_lemma, e_meaning, e_pattern),
                stage,
            )


class ContractAndEditorialValidationTests(Phase2ATestCase):
    def test_committed_specification_report_is_a_valid_phase1_fixture(self):
        report = json.loads(
            (ROOT / "reports/priority-7-pattern-schema.example.json").read_text(
                encoding="utf-8"))
        self.assertEqual([], validate_specification_fixture(report))

    def test_specification_fixture_cannot_bypass_id_recomputation_via_registry(self):
        fixture = specification_fixture()
        forged_id = "vp-l-forged-fixture-0123456789ab"
        fixture["lemmas"][0]["id"] = forged_id
        base_context = validation_context()
        context = ValidationContext(
            source_registry=base_context.source_registry,
            reviewer_registry=base_context.reviewer_registry,
            author_registry=base_context.author_registry,
            repository_index=base_context.repository_index,
            today=base_context.today,
            allocation_registry={forged_id: {}},
        )

        self.assertHasCode(
            validate_specification_fixture(fixture, context),
            "ID_RECOMPUTATION",
        )

    def test_three_envelopes_are_distinct(self):
        spec = specification_fixture()
        editorial = fictional_editorial()
        self.assertEqual([], validate_specification_fixture(spec))
        self.assertEditorialValid(editorial)
        self.assertIssues(validate_editorial(spec, validation_context()))
        self.assertIssues(validate_specification_fixture(editorial))

        with_revision = copy.deepcopy(editorial)
        with_revision["patternDataRevision"] = 1
        self.assertIssues(validate_editorial(with_revision, validation_context()))

    def test_valid_full_editorial_record_covers_reuse_and_approval(self):
        document = fictional_editorial()
        self.assertEditorialValid(document)
        _, _, pattern = parts(document)
        self.assertEqual(2, len(pattern["examples"]))
        self.assertEqual(
            [
                "external-verification",
                "native-linguistic",
                "product-approval",
            ],
            [event["kind"] for event in pattern["reviewEvents"]],
        )

    def test_closed_schema_enums_hierarchy_and_same_record_rules(self):
        cases = []

        def case(label, mutate):
            candidate = fictional_editorial()
            mutate(candidate)
            cases.append((label, candidate))

        case("unknown top-level field", lambda d: d.__setitem__("privateExtra", True))
        case(
            "unknown relation type",
            lambda d: parts(d)[2].__setitem__("relationType", "invented-frame"),
        )
        case(
            "union complement type",
            lambda d: parts(d)[2]["complements"][0].__setitem__(
                "type", "case-or-clause"),
        )
        case(
            "direct locative",
            lambda d: parts(d)[2]["complements"][0].__setitem__(
                "case", "locative"),
        )
        case(
            "direct nominative lexical frame",
            lambda d: parts(d)[2]["complements"][0].__setitem__(
                "case", "nominative"),
        )

        def invalid_nominative_role(d):
            pattern = parts(d)[2]
            pattern["relationType"] = "constructional-frame"
            pattern["complements"][0].update(
                {"case": "nominative", "role": "object"})
        case("invalid direct nominative role", invalid_nominative_role)

        def means_without_means(d):
            pattern = parts(d)[2]
            pattern["relationType"] = "means-method"
            pattern["complements"][0].update(
                {"case": "instrumental", "role": "object"})
        case("means-method role restriction", means_without_means)

        def experiencer_without_subject(d):
            pattern = parts(d)[2]
            pattern["relationType"] = "subject-experiencer"
            pattern["complements"] = [{
                "type": "case",
                "case": "dative",
                "required": True,
                "role": "experiencer",
            }]
        case("subject-experiencer role restriction", experiencer_without_subject)

        def recognition_with_production(d):
            pattern = parts(d)[2]
            pattern["teachingStatus"] = "recognition-only"
        case("recognition-only has production CEFR", recognition_with_production)

        def recognition_build(d):
            pattern = parts(d)[2]
            pattern["teachingStatus"] = "recognition-only"
            pattern["cefr"].pop("production")
        case("recognition-only has productive eligibility", recognition_build)

        def active_without_production(d):
            parts(d)[2]["cefr"].pop("production")
        case("active production lacks production CEFR", active_without_production)

        def limited_active(d):
            parts(d)[2]["usage"] = {
                "priority": "limited",
                "register": "neutral",
                "note": "NONPRODUCTION FIXTURE: restricted.",
            }
        case("limited active-production", limited_active)

        def deferred_visible(d):
            pattern = parts(d)[2]
            pattern["teachingStatus"] = "deferred"
            pattern["cefr"].pop("production")
        case("deferred learner eligibility", deferred_visible)

        def audio_without_listening(d):
            pattern = parts(d)[2]
            pattern["activityEligibility"] = ["reference"]
        case("audio needs listening not reference", audio_without_listening)

        for label, candidate in cases:
            with self.subTest(rule=label):
                self.assertIssues(
                    validate_editorial(candidate, validation_context()), label)

    def test_complement_discriminators_and_private_registries_fail_closed(self):
        mutations = {
            "COMPLEMENT_FIELD_REQUIRED": lambda d: parts(d)[2].__setitem__(
                "complements", [{
                    "type": "preposition-case",
                    "case": "accusative",
                    "required": True,
                    "role": "target",
                }]),
            "COMPLEMENT_FIELD_FORBIDDEN": lambda d: parts(d)[2].__setitem__(
                "complements", [{
                    "type": "infinitive",
                    "case": "accusative",
                    "required": True,
                    "role": "content",
                }]),
            "PREPOSITION_INVALID": lambda d: parts(d)[2].__setitem__(
                "complements", [{
                    "type": "preposition-case",
                    "preposition": "za czym",
                    "case": "instrumental",
                    "required": True,
                    "role": "target",
                }]),
            "SCHEMA_ARRAY_LENGTH": lambda d: parts(d)[2]["complements"][0].__setitem__(
                "questionOverridePl", []),
            "DATE_IN_FUTURE": lambda d: parts(d)[2]["evidence"][0].__setitem__(
                "checkedAt", "2026-08-10"),
            "SOURCE_REGISTRY_KIND": lambda d: parts(d)[2]["evidence"][0].__setitem__(
                "sourceKind", "contemporary-corpus"),
        }
        for code, mutate in mutations.items():
            with self.subTest(code=code):
                candidate = fictional_editorial()
                mutate(candidate)
                self.assertHasCode(
                    validate_editorial(candidate, validation_context()), code)

        candidate = fictional_editorial()
        context = validation_context()
        context.reviewer_registry["fixture-external-human"]["human"] = False
        self.assertHasCode(
            validate_editorial(candidate, context), "REVIEWER_NOT_HUMAN")

        candidate = fictional_editorial()
        context = validation_context()
        context.author_registry.clear()
        self.assertHasCode(
            validate_editorial(candidate, context), "AUTHOR_REGISTRY_DANGLING")

    def test_aspect_links_must_resolve_and_cannot_point_to_self(self):
        dangling = fictional_editorial()
        parts(dangling)[0]["aspectPartnerIds"] = [
            allocate_lemma_id("kontrafikcjonować")]
        self.assertHasCode(
            validate_editorial(dangling, validation_context()),
            "ASPECT_LINK_DANGLING",
        )

        self_link = fictional_editorial()
        lemma = parts(self_link)[0]
        lemma["aspectPartnerIds"] = [lemma["id"]]
        self.assertHasCode(
            validate_editorial(self_link, validation_context()),
            "ASPECT_LINK_SELF",
        )

    def test_aspect_partner_lemmas_require_reviewed_patterns_on_both_sides(self):
        document = fictional_editorial()
        partner_lemma, partner_meaning, partner_pattern = (
            add_fictional_aspect_partner(document))
        self.assertHasCode(
            validate_editorial(document, validation_context()),
            "ASPECT_LINK_UNREVIEWED",
        )

        partner_pattern["reviewEvents"] = [acceptance_events(
            partner_lemma, partner_meaning, partner_pattern)[0]]
        partner_pattern["reviewState"] = "externally-verified"
        self.assertEditorialValid(document)

    def test_aspect_equivalent_patterns_require_both_endpoints_reviewed(self):
        document = fictional_editorial()
        partner_lemma, partner_meaning, reviewed_partner = (
            add_fictional_aspect_partner(document))
        reviewed_partner["reviewEvents"] = [acceptance_events(
            partner_lemma, partner_meaning, reviewed_partner)[0]]
        reviewed_partner["reviewState"] = "externally-verified"

        unreviewed = copy.deepcopy(reviewed_partner)
        unreviewed_key = "unreviewed-equivalent"
        unreviewed_id = allocate_pattern_id(
            partner_meaning["id"],
            partner_lemma["canonicalLemma"],
            partner_meaning["key"],
            unreviewed_key,
        )
        unreviewed.update({
            "id": unreviewed_id,
            "key": unreviewed_key,
            "reviewState": "research",
            "reviewEvents": [],
            "aspectEquivalentPatternIds": [parts(document)[2]["id"]],
        })
        partner_meaning["patterns"].append(unreviewed)
        parts(document)[2]["aspectEquivalentPatternIds"] = [unreviewed_id]
        refresh_acceptance(document)
        self.assertHasCode(
            validate_editorial(document, validation_context()),
            "ASPECT_PATTERN_UNREVIEWED",
        )

        unreviewed["reviewEvents"] = [acceptance_events(
            partner_lemma, partner_meaning, unreviewed)[0]]
        unreviewed["reviewState"] = "externally-verified"
        self.assertEditorialValid(document)

    def test_malformed_nested_values_and_contexts_return_issues(self):
        mutations = (
            lambda p: p[2].__setitem__("relationType", []),
            lambda p: p[2].__setitem__("complements", [[]]),
            lambda p: p[2].__setitem__("activityEligibility", [[]]),
            lambda p: p[2].__setitem__("evidence", [[]]),
            lambda p: p[2].__setitem__("reviewEvents", [[]]),
            lambda p: p[2].__setitem__("examples", [[]]),
            lambda p: p[2].__setitem__("contentRefs", [[]]),
            lambda p: p[2].__setitem__("errorNotes", [[]]),
        )
        for index, mutate in enumerate(mutations):
            with self.subTest(nested_case=index):
                candidate = fictional_editorial()
                mutate(parts(candidate))
                self.assertIssues(
                    validate_editorial(candidate, validation_context()))

        malformed_contexts = (
            {},
            ValidationContext(source_registry=[]),
            ValidationContext(reviewer_registry=[]),
            ValidationContext(author_registry=[]),
            ValidationContext(allocation_registry=[]),
            ValidationContext(repository_index="NONPRODUCTION INVALID INDEX"),
            ValidationContext(today=[]),
        )
        for context in malformed_contexts:
            with self.subTest(context=repr(context)):
                self.assertIssues(validate_editorial(fictional_editorial(), context))
                self.assertIssues(validate_specification_fixture(
                    specification_fixture(), context))
                self.assertIssues(validate_runtime({
                    "formatVersion": 1,
                    "patternDataRevision": 999,
                    "lemmas": [],
                }, context))

        malformed_registry_records = (
            ValidationContext(source_registry={"fixture-reference": []}),
            ValidationContext(reviewer_registry={
                "fixture-external-human": []}),
            ValidationContext(author_registry={"fixture-human-author": []}),
            ValidationContext(allocation_registry={"malformed-fixture": []}),
        )
        for context in malformed_registry_records:
            with self.subTest(registry_record=repr(context)):
                self.assertIssues(
                    validate_editorial(fictional_editorial(), context))

        runtime = project_runtime_nonrelease(
            fictional_editorial(), 999, validation_context())
        runtime["lemmas"][0]["meanings"][0]["patterns"][0][
            "activityEligibility"] = [[]]
        self.assertIssues(validate_runtime(runtime))

    def test_version_and_scope_constants_require_exact_integers(self):
        for malformed in (True, 1.0):
            with self.subTest(field="editorial.formatVersion", value=malformed):
                editorial = fictional_editorial()
                editorial["formatVersion"] = malformed
                self.assertHasCode(
                    validate_editorial(editorial, validation_context()),
                    "FORMAT_VERSION",
                )

            with self.subTest(field="specification.formatVersion", value=malformed):
                specification = specification_fixture()
                specification["formatVersion"] = malformed
                self.assertHasCode(
                    validate_specification_fixture(specification),
                    "FORMAT_VERSION",
                )

            with self.subTest(field="specification.revision", value=malformed):
                specification = specification_fixture()
                specification["patternDataRevision"] = malformed
                self.assertHasCode(
                    validate_specification_fixture(specification),
                    "PATTERN_REVISION",
                )

            runtime = project_runtime_nonrelease(
                fictional_editorial(), 1, validation_context())
            with self.subTest(field="runtime.formatVersion", value=malformed):
                malformed_runtime = copy.deepcopy(runtime)
                malformed_runtime["formatVersion"] = malformed
                self.assertHasCode(
                    validate_runtime(malformed_runtime), "FORMAT_VERSION")
            with self.subTest(field="runtime.revision", value=malformed):
                malformed_runtime = copy.deepcopy(runtime)
                malformed_runtime["patternDataRevision"] = malformed
                self.assertHasCode(
                    validate_runtime(malformed_runtime), "PATTERN_REVISION")

            with self.subTest(field="review.scopeVersion", value=malformed):
                editorial = fictional_editorial()
                parts(editorial)[2]["reviewEvents"][0]["scopeVersion"] = malformed
                self.assertHasCode(
                    validate_editorial(editorial, validation_context()),
                    "REVIEW_SCOPE_VERSION",
                )

            baseline = freeze_editorial(
                fictional_editorial(), 1, validation_context())
            with self.subTest(field="frozen.formatVersion", value=malformed):
                malformed_frozen = copy.deepcopy(baseline)
                malformed_frozen["formatVersion"] = malformed
                with self.assertRaises(ValidationFailure) as caught:
                    freeze_editorial(
                        fictional_editorial(),
                        1,
                        validation_context(),
                        previous=malformed_frozen,
                    )
                self.assertHasCode(
                    caught.exception.issues, "FROZEN_FORMAT_VERSION")
            with self.subTest(field="frozen.scopeVersion", value=malformed):
                malformed_frozen = copy.deepcopy(baseline)
                pattern_policy = next(
                    row for row in malformed_frozen["policy"]
                    if row["kind"] == "pattern")
                pattern_policy["scopeVersion"] = malformed
                with self.assertRaises(ValidationFailure) as caught:
                    freeze_editorial(
                        fictional_editorial(),
                        1,
                        validation_context(),
                        previous=malformed_frozen,
                    )
                self.assertHasCode(
                    caught.exception.issues, "FROZEN_SCOPE_VERSION")

            with self.subTest(field="freeze.revision", value=malformed):
                with self.assertRaises(ValidationFailure) as caught:
                    freeze_editorial(
                        fictional_editorial(), malformed, validation_context())
                self.assertHasCode(caught.exception.issues, "FROZEN_REVISION")

    def test_dates_require_the_exact_yyyy_mm_dd_spelling(self):
        mutations = (
            (
                "evidence.checkedAt",
                lambda pattern, value: pattern["evidence"][0].__setitem__(
                    "checkedAt", value),
            ),
            (
                "review.reviewedAt",
                lambda pattern, value: pattern["reviewEvents"][0].__setitem__(
                    "reviewedAt", value),
            ),
            (
                "origin.authoredAt",
                lambda pattern, value: pattern["examples"][0]["origin"].__setitem__(
                    "authoredAt", value),
            ),
        )
        for malformed in ("20260808", "2026-W32-6", "2026-8-8"):
            for field, mutate in mutations:
                with self.subTest(field=field, value=malformed):
                    document = fictional_editorial()
                    mutate(parts(document)[2], malformed)
                    self.assertHasCode(
                        validate_editorial(document, validation_context()),
                        "DATE_INVALID",
                    )

    def test_review_event_fail_closed_rules(self):
        cases = []

        def changed(label, mutate):
            candidate = fictional_editorial()
            mutate(parts(candidate)[2]["reviewEvents"])
            cases.append((label, candidate))

        changed(
            "accepted external requires supporting evidence",
            lambda events: events[0].pop("supportingEvidenceDigests"),
        )
        changed(
            "accepted native forbids supporting evidence",
            lambda events: events[1].__setitem__(
                "supportingEvidenceDigests", events[0]["supportingEvidenceDigests"]),
        )
        changed(
            "accepted product forbids supporting evidence",
            lambda events: events[2].__setitem__(
                "supportingEvidenceDigests", events[0]["supportingEvidenceDigests"]),
        )
        changed(
            "nonaccept needs note",
            lambda events: events.append({
                "kind": "native-linguistic",
                "decision": "changes-requested",
                "reviewerRef": "fixture-native-human",
                "reviewedAt": "2026-08-08",
            }),
        )
        changed(
            "nonaccept forbids scope",
            lambda events: events.append({
                "kind": "native-linguistic",
                "decision": "reject",
                "scopeVersion": 1,
                "scopeDigest": events[1]["scopeDigest"],
                "reviewerRef": "fixture-native-human",
                "reviewedAt": "2026-08-08",
                "note": "NONPRODUCTION FIXTURE rejection.",
            }),
        )
        changed(
            "correction needs note and forbids scope",
            lambda events: events.append({
                "kind": "correction",
                "decision": "accept",
                "scopeVersion": 1,
                "scopeDigest": events[2]["scopeDigest"],
                "reviewerRef": "fixture-product-human",
                "reviewedAt": "2026-08-08",
            }),
        )
        changed("approved needs every stage", lambda events: events.pop(1))
        for label, candidate in cases:
            with self.subTest(rule=label):
                self.assertIssues(
                    validate_editorial(candidate, validation_context()), label)

    def test_later_nonaccept_decisions_control_the_current_review_state(self):
        expected_states = {
            "changes-requested": "native-reviewed",
            "defer": "deferred",
            "reject": "rejected",
        }
        for decision, expected_state in expected_states.items():
            with self.subTest(decision=decision):
                candidate = fictional_editorial()
                pattern = parts(candidate)[2]
                pattern["activityEligibility"] = []
                for example in pattern["examples"]:
                    example["audioEligible"] = False
                refresh_acceptance(candidate)
                pattern["reviewEvents"].append({
                    "kind": "product-approval",
                    "decision": decision,
                    "reviewerRef": "fixture-product-human",
                    "reviewedAt": "2026-08-09",
                    "note": f"NONPRODUCTION FIXTURE {decision} decision.",
                })
                pattern["reviewState"] = expected_state
                self.assertEditorialValid(candidate)

        reopened = fictional_editorial()
        pattern = parts(reopened)[2]
        pattern["activityEligibility"] = []
        for example in pattern["examples"]:
            example["audioEligible"] = False
        pattern["reviewEvents"] = [{
            "kind": "external-verification",
            "decision": "reject",
            "reviewerRef": "fixture-external-human",
            "reviewedAt": "2026-08-08",
            "note": "NONPRODUCTION FIXTURE rejected treatment.",
        }, {
            "kind": "reopen",
            "decision": "accept",
            "reviewerRef": "fixture-product-human",
            "reviewedAt": "2026-08-09",
            "note": "NONPRODUCTION FIXTURE owner-authorized reopen.",
        }]
        pattern["reviewState"] = "research"
        self.assertEditorialValid(reopened)

    def test_reflexivity_aspect_and_ownership_fail_closed(self):
        mismatch = fictional_editorial()
        parts(mismatch)[0]["reflexive"] = True
        self.assertIssues(validate_editorial(mismatch, validation_context()))

        lexical_sie = fictional_editorial()
        lemma = parts(lexical_sie)[0]
        lemma["canonicalLemma"] = "fikcjonować się"
        self.assertIssues(validate_editorial(lexical_sie, validation_context()))
        self.assertNotEqual(
            allocate_lemma_id("fikcjonować"),
            allocate_lemma_id("fikcjonować się"),
        )

        duplicate = fictional_editorial()
        duplicate["lemmas"].append(copy.deepcopy(duplicate["lemmas"][0]))
        self.assertIssues(validate_editorial(duplicate, validation_context()))

        wrong_owner = fictional_editorial()
        lemma, meaning, pattern = parts(wrong_owner)
        foreign_pattern_id = allocate_pattern_id(
            meaning["id"],
            lemma["canonicalLemma"],
            meaning["key"],
            "foreign-owner",
        )
        example = pattern["examples"][0]
        example["id"] = allocate_example_id(
            foreign_pattern_id, example["key"])
        refresh_acceptance(wrong_owner)
        self.assertHasCode(
            validate_editorial(wrong_owner, validation_context()),
            "ID_RECOMPUTATION",
        )

    def test_example_origins_and_repository_reuse_are_exact(self):
        valid = fictional_editorial()
        self.assertEditorialValid(valid)

        allowed_targets = (
            ("card", FIXTURE_CARD_ID, "pl",
             "ZNACZNIK-NIEPRODUKCYJNY: fikcjonuję obiekt."),
            ("card", FIXTURE_CARD_ID, "ex", FIXTURE_REUSED_SENTENCE),
            ("drill", FIXTURE_DRILL_ID, "prompt",
             "ZNACZNIK-NIEPRODUKCYJNY: ___ obiekt testowy."),
            ("drill", FIXTURE_DRILL_ID, "answer", "fikcjonuję"),
        )
        for kind, entity_id, field, exact_text in allowed_targets:
            with self.subTest(valid_source=f"{kind}.{field}"):
                candidate = fictional_editorial()
                example = parts(candidate)[2]["examples"][1]
                example["pl"] = exact_text
                example["origin"]["repositorySource"] = {
                    "kind": kind,
                    "id": entity_id,
                    "field": field,
                }
                refresh_acceptance(candidate)
                self.assertEditorialValid(candidate)

        cases = []

        def mutate_reuse(label, mutate):
            candidate = fictional_editorial()
            example = parts(candidate)[2]["examples"][1]
            mutate(example)
            refresh_acceptance(candidate)
            cases.append((label, candidate))

        mutate_reuse(
            "nonexistent source id",
            lambda ex: ex["origin"]["repositorySource"].__setitem__(
                "id", "p7-fixture-missing"),
        )
        mutate_reuse(
            "wrong source kind",
            lambda ex: ex["origin"]["repositorySource"].__setitem__(
                "kind", "drill"),
        )
        mutate_reuse(
            "forbidden card field",
            lambda ex: ex["origin"]["repositorySource"].__setitem__(
                "field", "prompt"),
        )
        mutate_reuse(
            "exact equality forbids whitespace normalization",
            lambda ex: ex.__setitem__("pl", ex["pl"] + " "),
        )

        original_with_source = fictional_editorial()
        original = parts(original_with_source)[2]["examples"][0]
        original["origin"]["repositorySource"] = {
            "kind": "card",
            "id": FIXTURE_CARD_ID,
            "field": "ex",
        }
        refresh_acceptance(original_with_source)
        cases.append(("original forbids repository source", original_with_source))

        dictionary_origin = fictional_editorial()
        parts(dictionary_origin)[2]["examples"][0]["origin"]["kind"] = (
            "source-derived")
        refresh_acceptance(dictionary_origin)
        cases.append(("source-derived origins are forbidden", dictionary_origin))

        for label, candidate in cases:
            with self.subTest(rule=label):
                self.assertIssues(
                    validate_editorial(candidate, validation_context()), label)

    def test_repository_index_rejects_duplicate_stable_ids(self):
        sources = injected_sources()
        duplicate = copy.deepcopy(sources[0]["levels"][0]["topics"][0]["cards"][0])
        sources[0]["levels"][0]["topics"][0]["cards"].append(duplicate)
        index = RepositoryIndex.from_sources(sources)
        self.assertIn("REPOSITORY_DUPLICATE_ID", {issue.code for issue in index.issues})

    def test_repository_reuse_and_content_refs_report_exact_resolution_codes(self):
        dangling_reuse = fictional_editorial()
        parts(dangling_reuse)[2]["examples"][1]["origin"][
            "repositorySource"]["id"] = "p7-fixture-missing"
        refresh_acceptance(dangling_reuse)
        self.assertHasCode(
            validate_editorial(dangling_reuse, validation_context()),
            "REPOSITORY_SOURCE_DANGLING",
        )

        wrong_reuse_kind = fictional_editorial()
        wrong_source = parts(wrong_reuse_kind)[2]["examples"][1]["origin"][
            "repositorySource"]
        wrong_source["kind"] = "drill"
        wrong_source["field"] = "answer"
        refresh_acceptance(wrong_reuse_kind)
        self.assertHasCode(
            validate_editorial(wrong_reuse_kind, validation_context()),
            "REPOSITORY_SOURCE_KIND",
        )

        dangling_ref = fictional_editorial()
        parts(dangling_ref)[2]["contentRefs"][0]["id"] = "p7-fixture-missing"
        refresh_acceptance(dangling_ref)
        self.assertHasCode(
            validate_editorial(dangling_ref, validation_context()),
            "CONTENT_REF_DANGLING",
        )

        wrong_ref_kind = fictional_editorial()
        parts(wrong_ref_kind)[2]["contentRefs"][0]["kind"] = "drill"
        refresh_acceptance(wrong_ref_kind)
        self.assertHasCode(
            validate_editorial(wrong_ref_kind, validation_context()),
            "CONTENT_REF_KIND",
        )

    def test_repository_index_rejects_nonarray_source_issues(self):
        for malformed in (
                None,
                "NONPRODUCTION-FIXTURE-UPSTREAM-ERROR",
                {"code": "NONPRODUCTION-FIXTURE-UPSTREAM-ERROR"},
                7):
            with self.subTest(source_issues=repr(malformed)):
                sources = injected_sources()
                sources[0]["sourceIssues"] = malformed
                index = RepositoryIndex.from_sources(sources)
                self.assertHasCode(
                    index.issues, "REPOSITORY_SOURCE_ISSUES_TYPE")

    def test_repository_adapter_uses_the_strict_duplicate_key_loader(self):
        source = """PP_LEVELS.push({
          id: 'p7-fixture-level-original',
          id: 'p7-fixture-level-duplicate',
          level: 'NONPRODUCTION FIXTURE',
          topics: []
        });
        """
        with tempfile.TemporaryDirectory(prefix="priority7-fixture-") as temp_dir:
            Path(temp_dir, "data-fixture.js").write_text(
                source, encoding="utf-8")
            index = repository_index_from_root(temp_dir)
        self.assertHasCode(index.issues, "REPOSITORY_SOURCE_INVALID")
        self.assertTrue(any(
            "SOURCE_DUPLICATE_OBJECT_KEY" in issue.message
            for issue in index.issues
        ), index.issues)

    def test_actual_repository_adapter_resolves_exact_values_fail_closed(self):
        index = repository_index_from_root(ROOT)
        self.assertEqual([], index.issues)
        allowed_fields = {
            "card": ("pl", "ex"),
            "drill": ("prompt", "answer"),
        }
        entities = sorted(index.entities.values(), key=lambda item: item.entity_id)
        exact_entity = next(
            entity
            for entity in entities
            if entity.kind == "card"
            and isinstance(entity.record.get("ex"), str)
            and len(entity.record["ex"]) >= 3
        )
        exact_field = "ex"

        exact = fictional_editorial()
        pattern = parts(exact)[2]
        example = pattern["examples"][1]
        example["pl"] = exact_entity.record[exact_field]
        example["origin"]["repositorySource"] = {
            "kind": exact_entity.kind,
            "id": exact_entity.entity_id,
            "field": exact_field,
        }
        pattern["contentRefs"] = [{
            "kind": exact_entity.kind,
            "id": exact_entity.entity_id,
            "purpose": "support",
        }]
        refresh_acceptance(exact)
        context = validation_context(index)
        self.assertEqual([], validate_editorial(exact, context))

        whitespace_mismatch = copy.deepcopy(exact)
        parts(whitespace_mismatch)[2]["examples"][1]["pl"] += " "
        refresh_acceptance(whitespace_mismatch)
        self.assertHasCode(
            validate_editorial(whitespace_mismatch, context),
            "REPOSITORY_SOURCE_MISMATCH",
        )

        missing_entity, missing_field = next(
            (entity, field)
            for entity in entities
            if entity.kind in allowed_fields
            for field in allowed_fields[entity.kind]
            if field not in entity.record
        )
        missing = copy.deepcopy(exact)
        pattern = parts(missing)[2]
        pattern["examples"][1]["origin"]["repositorySource"] = {
            "kind": missing_entity.kind,
            "id": missing_entity.entity_id,
            "field": missing_field,
        }
        pattern["contentRefs"] = [{
            "kind": missing_entity.kind,
            "id": missing_entity.entity_id,
            "purpose": "support",
        }]
        refresh_acceptance(missing)
        self.assertHasCode(
            validate_editorial(missing, context),
            "REPOSITORY_SOURCE_FIELD_MISSING",
        )

        nonstring_entity, nonstring_field = next(
            (entity, field)
            for entity in entities
            if entity.kind == "drill"
            for field in allowed_fields[entity.kind]
            if field in entity.record and not isinstance(entity.record[field], str)
        )
        nonstring = copy.deepcopy(exact)
        pattern = parts(nonstring)[2]
        pattern["examples"][1]["origin"]["repositorySource"] = {
            "kind": nonstring_entity.kind,
            "id": nonstring_entity.entity_id,
            "field": nonstring_field,
        }
        pattern["contentRefs"] = [{
            "kind": nonstring_entity.kind,
            "id": nonstring_entity.entity_id,
            "purpose": "support",
        }]
        refresh_acceptance(nonstring)
        self.assertHasCode(
            validate_editorial(nonstring, context),
            "REPOSITORY_SOURCE_NOT_STRING",
        )


class ReviewInvalidationTests(Phase2ATestCase):
    def test_current_approval_is_valid_and_covered_mutations_are_stale(self):
        base = fictional_editorial()
        self.assertEditorialValid(base)
        mutations = {
            "canonical lemma": lambda p: p[0].__setitem__(
                "canonicalLemma", "kontrafikcjonować"),
            "display lemma": lambda p: p[0].__setitem__(
                "displayLemma", p[0]["displayLemma"] + " ZMIANA"),
            "reflexivity": lambda p: p[0].__setitem__("reflexive", True),
            "aspect": lambda p: p[0].__setitem__("aspect", "imperfective"),
            "meaning gloss": lambda p: p[1]["glossesEn"].append(
                "a changed fictional gloss"),
            "meaning scope": lambda p: p[1].__setitem__(
                "internalScope", p[1]["internalScope"] + " Changed."),
            "relation type": lambda p: p[2].__setitem__(
                "relationType", "constructional-frame"),
            "complement": lambda p: p[2]["complements"][0].__setitem__(
                "required", False),
            "CEFR": lambda p: p[2]["cefr"].__setitem__("production", "A2"),
            "teaching status": lambda p: p[2].__setitem__(
                "teachingStatus", "recognition-only"),
            "explanation": lambda p: p[2].__setitem__(
                "learnerExplanationEn", p[2]["learnerExplanationEn"] + " Changed."),
            "example text": lambda p: p[2]["examples"][0].__setitem__(
                "pl", p[2]["examples"][0]["pl"] + " ZMIANA."),
            "example origin": lambda p: p[2]["examples"][0]["origin"].__setitem__(
                "authoredAt", "2026-08-07"),
            "activity eligibility": lambda p: p[2]["activityEligibility"].remove(
                "search"),
            "audio eligibility": lambda p: p[2]["examples"][0].__setitem__(
                "audioEligible", False),
            "content reference": lambda p: p[2]["contentRefs"][0].__setitem__(
                "purpose", "context"),
            "error guidance": lambda p: p[2]["errorNotes"][0].__setitem__(
                "guidanceEn", p[2]["errorNotes"][0]["guidanceEn"] + " Changed."),
        }
        for label, mutate in mutations.items():
            with self.subTest(field=label):
                candidate = copy.deepcopy(base)
                mutate(parts(candidate))
                self.assertIssues(
                    validate_editorial(candidate, validation_context()), label)

    def test_pinned_evidence_edit_or_removal_invalidates_external_acceptance(self):
        edited = fictional_editorial()
        lemma, meaning, pattern = parts(edited)
        pattern["errorNotes"] = [{
            "kind": "documented-common-error",
            "incorrectForm": "ZNACZNIK-NIEPRODUKCYJNY-BŁĄD-EDYCJI",
            "guidanceEn": "NONPRODUCTION FIXTURE: documented error guidance.",
            "evidenceRefs": [0],
        }]
        refresh_acceptance(edited)
        before = {
            stage: review_scope_digest(stage, lemma, meaning, pattern)
            for stage in (
                "external-verification", "native-linguistic", "product-approval")
        }
        pattern["evidence"][0]["note"] += " Edited."
        self.assertEqual(
            before["external-verification"],
            review_scope_digest("external-verification", lemma, meaning, pattern),
        )
        for stage in ("native-linguistic", "product-approval"):
            self.assertNotEqual(
                before[stage], review_scope_digest(stage, lemma, meaning, pattern))
        self.assertIssues(validate_editorial(edited, validation_context()))

        removed = fictional_editorial()
        parts(removed)[2]["evidence"][0] = {
            "sourceId": "fixture-corroboration",
            "sourceKind": "contemporary-corpus",
            "locator": "fixture://nonproduction/replacement-evidence",
            "factType": "complement-frame",
            "checkedAt": "2026-08-08",
        }
        self.assertIssues(validate_editorial(removed, validation_context()))

    def test_error_evidence_index_cannot_retarget_to_unpinned_evidence(self):
        document = fictional_editorial()
        pattern = parts(document)[2]
        pattern["errorNotes"] = [{
            "kind": "documented-common-error",
            "incorrectForm": "ZNACZNIK-NIEPRODUKCYJNY-BŁĄD-UDOKUMENTOWANY",
            "guidanceEn": (
                "NONPRODUCTION FIXTURE: documented fictional error guidance."
            ),
            "evidenceRefs": [0],
        }]
        refresh_acceptance(document)
        self.assertEditorialValid(document)

        pattern["evidence"].insert(0, {
            "sourceId": "fixture-corroboration",
            "sourceKind": "contemporary-corpus",
            "locator": "fixture://nonproduction/unpinned-index-insertion",
            "factType": "contrast",
            "checkedAt": "2026-08-08",
        })
        self.assertHasCode(
            validate_editorial(document, validation_context()),
            "ERROR_EVIDENCE_NOT_EXTERNALLY_PINNED",
        )

    def test_two_pinned_evidence_records_cannot_silently_retarget_error_claim(self):
        document = fictional_editorial()
        lemma, meaning, pattern = parts(document)
        pattern["evidence"].append(fictional_corroboration("second-pinned-record"))
        pattern["errorNotes"] = [{
            "kind": "documented-common-error",
            "incorrectForm": "ZNACZNIK-NIEPRODUKCYJNY-BŁĄD-DWA-PINY",
            "guidanceEn": "NONPRODUCTION FIXTURE: bind the first evidence record.",
            "evidenceRefs": [0],
        }]
        refresh_acceptance(document)
        pattern["reviewEvents"][0]["supportingEvidenceDigests"] = sorted(
            evidence_digest(record) for record in pattern["evidence"])
        self.assertEditorialValid(document)
        before = {
            stage: review_scope_digest(stage, lemma, meaning, pattern)
            for stage in (
                "external-verification", "native-linguistic", "product-approval")
        }

        pattern["evidence"].reverse()
        self.assertEqual(
            before["external-verification"],
            review_scope_digest("external-verification", lemma, meaning, pattern),
        )
        for stage in ("native-linguistic", "product-approval"):
            self.assertNotEqual(
                before[stage], review_scope_digest(stage, lemma, meaning, pattern))
        self.assertHasCode(
            validate_editorial(document, validation_context()),
            "REVIEW_STATE_MISMATCH",
        )
        with self.assertRaises(ValidationFailure):
            project_runtime_nonrelease(document, 1, validation_context())

    def test_evidence_position_change_preserves_scope_when_digest_target_is_same(self):
        document = fictional_editorial()
        lemma, meaning, pattern = parts(document)
        pattern["errorNotes"] = [{
            "kind": "documented-common-error",
            "incorrectForm": "ZNACZNIK-NIEPRODUKCYJNY-BŁĄD-STAŁY-CEL",
            "guidanceEn": "NONPRODUCTION FIXTURE: preserve the evidence target.",
            "evidenceRefs": [0],
        }]
        refresh_acceptance(document)
        before = {
            stage: review_scope_digest(stage, lemma, meaning, pattern)
            for stage in ("native-linguistic", "product-approval")
        }

        pattern["evidence"].insert(
            0, fictional_corroboration("inserted-before-same-target"))
        pattern["errorNotes"][0]["evidenceRefs"] = [1]
        for stage in ("native-linguistic", "product-approval"):
            self.assertEqual(
                before[stage], review_scope_digest(stage, lemma, meaning, pattern))
        self.assertEditorialValid(document)

    def test_unpinned_corroboration_does_not_invalidate_current_approval(self):
        candidate = fictional_editorial()
        lemma, meaning, pattern = parts(candidate)
        pattern["errorNotes"] = [{
            "kind": "documented-common-error",
            "incorrectForm": "ZNACZNIK-NIEPRODUKCYJNY-BŁĄD-DOPISANIA",
            "guidanceEn": "NONPRODUCTION FIXTURE: reviewed error claim.",
            "evidenceRefs": [0],
        }]
        refresh_acceptance(candidate)
        stages = (
            "external-verification", "native-linguistic", "product-approval")
        before = {
            stage: review_scope_digest(stage, lemma, meaning, pattern)
            for stage in stages
        }
        corroboration = fictional_corroboration("corroborating-record")
        corroboration["factType"] = "usage-register"
        pattern["evidence"].append(corroboration)
        for stage in stages:
            self.assertEqual(
                before[stage], review_scope_digest(stage, lemma, meaning, pattern))
        self.assertEditorialValid(candidate)

    def test_duplicate_evidence_digests_are_rejected_and_every_pin_survives(self):
        duplicate = fictional_editorial()
        pattern = parts(duplicate)[2]
        pattern["evidence"].append(copy.deepcopy(pattern["evidence"][0]))
        refresh_acceptance(duplicate)
        self.assertHasCode(
            validate_editorial(duplicate, validation_context()),
            "EVIDENCE_DUPLICATE_DIGEST",
        )

        pinned = fictional_editorial()
        pattern = parts(pinned)[2]
        pattern["evidence"].append({
            "sourceId": "fixture-corroboration",
            "sourceKind": "contemporary-corpus",
            "locator": "fixture://nonproduction/second-pinned-record",
            "factType": "usage-register",
            "checkedAt": "2026-08-08",
        })
        refresh_acceptance(pinned)
        pattern["reviewEvents"][0]["supportingEvidenceDigests"] = sorted(
            evidence_digest(record) for record in pattern["evidence"])
        self.assertEditorialValid(pinned)

        removed = copy.deepcopy(pinned)
        parts(removed)[2]["evidence"].pop()
        self.assertHasCode(
            validate_editorial(removed, validation_context()),
            "REVIEW_STATE_MISMATCH",
        )

    def test_external_acceptance_pins_only_contemporary_evidence(self):
        corpus = fictional_editorial()
        parts(corpus)[2]["evidence"] = [{
            "sourceId": "fixture-corroboration",
            "sourceKind": "contemporary-corpus",
            "locator": "fixture://nonproduction/corpus-acceptance",
            "factType": "complement-frame",
            "checkedAt": "2026-08-08",
        }]
        refresh_acceptance(corpus)
        self.assertEditorialValid(corpus)

        repository = fictional_editorial()
        parts(repository)[2]["evidence"] = [{
            "sourceId": "phase1-specification-fixture",
            "sourceKind": "repository",
            "locator": "fixture://nonproduction/repository-evidence",
            "factType": "complement-frame",
            "checkedAt": "2026-08-08",
        }]
        refresh_acceptance(repository)
        self.assertHasCode(
            validate_editorial(repository, validation_context()),
            "REVIEW_CONTEMPORARY_EVIDENCE_REQUIRED",
        )

        medak = fictional_editorial()
        parts(medak)[2]["evidence"] = [{
            "sourceId": "fixture-medak-research",
            "sourceKind": "medak-research",
            "locator": "fixture://nonproduction/research-evidence",
            "factType": "complement-frame",
            "checkedAt": "2026-08-08",
        }]
        refresh_acceptance(medak)
        context = validation_context()
        context.source_registry["fixture-medak-research"] = {
            "sourceKind": "medak-research"}
        self.assertHasCode(
            validate_editorial(medak, context),
            "REVIEW_CONTEMPORARY_EVIDENCE_REQUIRED",
        )

    def test_one_reviewer_needs_owner_permission_to_accept_multiple_stages(self):
        candidate = fictional_editorial()
        reviewer_ref = "fixture-multiple-stage-human"
        for event in parts(candidate)[2]["reviewEvents"]:
            event["reviewerRef"] = reviewer_ref

        context = validation_context()
        context.reviewer_registry[reviewer_ref] = {
            "human": True,
            "roles": [
                "external-verification",
                "native-linguistic",
                "product-approval",
            ],
        }
        self.assertHasCode(
            validate_editorial(candidate, context),
            "REVIEWER_MULTI_ROLE_NOT_AUTHORIZED",
        )

        context.reviewer_registry[reviewer_ref][
            "ownerAllowsMultipleRoles"] = True
        self.assertEqual([], validate_editorial(candidate, context))


class FrozenEditorialTests(Phase2ATestCase):
    def test_freeze_is_deterministic_and_sibling_reordering_is_harmless(self):
        document = fictional_editorial()
        add_deferred_pattern(document)
        baseline = freeze_editorial(document, 1, validation_context())
        reordered = copy.deepcopy(document)
        parts(reordered)[1]["patterns"].reverse()
        self.assertEqual(
            baseline,
            freeze_editorial(reordered, 1, validation_context()),
        )

    def test_frozen_structural_drift_and_parent_move_are_rejected(self):
        document = fictional_editorial()
        second_id = add_deferred_pattern(document)
        baseline = freeze_editorial(document, 1, validation_context())

        drifted = copy.deepcopy(document)
        parts(drifted)[1]["patterns"][1]["complements"][0]["required"] = False
        with self.assertRaises(ValidationFailure):
            freeze_editorial(
                drifted, 1, validation_context(), previous=baseline)

        moved = copy.deepcopy(document)
        lemma, first_meaning, _ = parts(moved)
        second_meaning_key = "alternate-fiction"
        second_meaning_id = allocate_meaning_id(
            lemma["id"], lemma["canonicalLemma"], second_meaning_key)
        moved_pattern = first_meaning["patterns"].pop(1)
        lemma["meanings"].append({
            "id": second_meaning_id,
            "key": second_meaning_key,
            "glossesEn": ["alternate nonproduction fiction"],
            "internalScope": "NONPRODUCTION FIXTURE alternate ownership.",
            "patterns": [moved_pattern],
        })
        self.assertEqual(second_id, moved_pattern["id"])
        with self.assertRaises(ValidationFailure):
            freeze_editorial(
                moved, 1, validation_context(), previous=baseline)

    def test_frozen_allocation_validates_the_complete_readable_id(self):
        document = fictional_editorial()
        forged = freeze_editorial(document, 1, validation_context())
        allocation = next(
            row for row in forged["allocations"] if row["kind"] == "example")
        self.assertEqual({
            "id", "kind", "parentId", "key", "seed", "readableStem",
            "canonicalLemmaAtAllocation", "meaningKeyAtAllocation",
        }, set(allocation))
        original_id = allocation["id"]
        forged_id = f"vp-e-forged-readable-{original_id.rsplit('-', 1)[-1]}"
        allocation["readableStem"] = "forged-readable"
        for collection in (
                "allocations", "identity", "structure", "wording", "policy"):
            for row in forged[collection]:
                if row["id"] == original_id:
                    row["id"] = forged_id
            forged[collection].sort(key=lambda row: row["id"])

        with self.assertRaises(ValidationFailure) as caught:
            freeze_editorial(
                document, 2, validation_context(), previous=forged)
        self.assertHasCode(caught.exception.issues, "FROZEN_SEED")

    def test_frozen_snapshot_rows_are_closed_and_required_per_kind(self):
        document = fictional_editorial()
        baseline = freeze_editorial(document, 1, validation_context())
        required_fields = (
            ("identity", "lemma", "id"),
            ("identity", "meaning", "parentId"),
            ("identity", "pattern", "relationType"),
            ("identity", "example", "key"),
            ("structure", "lemma", "canonicalLemma"),
            ("structure", "meaning", "parentLemmaId"),
            ("structure", "pattern", "complements"),
            ("structure", "example", "parentPatternId"),
            ("wording", "lemma", "displayLemma"),
            ("wording", "meaning", "internalScope"),
            ("wording", "pattern", "learnerExplanationEn"),
            ("wording", "example", "pl"),
            ("policy", "lemma", "id"),
            ("policy", "meaning", "id"),
            ("policy", "pattern", "currentScopeDigests"),
            ("policy", "example", "audioEligible"),
            ("reviewHistory", None, "currentEvidenceDigests"),
        )
        for collection, kind, required_field in required_fields:
            with self.subTest(collection=collection, kind=kind):
                malformed = copy.deepcopy(baseline)
                row = (
                    malformed[collection][0]
                    if kind is None else
                    next(
                        item for item in malformed[collection]
                        if item["kind"] == kind)
                )
                row.pop(required_field)
                with self.assertRaises(ValidationFailure) as caught:
                    freeze_editorial(
                        document, 2, validation_context(), previous=malformed)
                self.assertHasCode(caught.exception.issues, "SCHEMA_REQUIRED")

        for collection in (
                "identity", "structure", "wording", "policy", "reviewHistory"):
            with self.subTest(closed_collection=collection):
                unknown = copy.deepcopy(baseline)
                unknown[collection][0]["fixtureUnknown"] = True
                with self.assertRaises(ValidationFailure) as caught:
                    freeze_editorial(
                        document, 2, validation_context(), previous=unknown)
                self.assertHasCode(
                    caught.exception.issues, "SCHEMA_UNKNOWN_FIELD")

    def test_malformed_frozen_policy_and_history_containers_fail_closed(self):
        document = fictional_editorial()
        pattern_id = parts(document)[2]["id"]
        baseline = freeze_editorial(document, 1, validation_context())
        cases = (
            ("policy", "currentScopeDigests", (None, 7, [], {})),
            ("reviewHistory", "evidenceArchive", (None, 7, {}, [[]])),
            ("reviewHistory", "currentEvidenceDigests", (None, 7, {}, [{}])),
            ("reviewHistory", "reviewEvents", (None, 7, {}, [[]])),
        )
        for collection, field, malformed_values in cases:
            for malformed_value in malformed_values:
                with self.subTest(
                        collection=collection,
                        field=field,
                        malformed=repr(malformed_value)):
                    malformed = copy.deepcopy(baseline)
                    row = next(
                        item for item in malformed[collection]
                        if item["id"] == pattern_id)
                    row[field] = copy.deepcopy(malformed_value)
                    with self.assertRaises(ValidationFailure) as caught:
                        freeze_editorial(
                            document,
                            1,
                            validation_context(),
                            previous=malformed,
                        )
                    self.assertIssues(caught.exception.issues)

    def test_private_only_change_keeps_revision_but_runtime_change_increments(self):
        document = fictional_editorial()
        baseline = freeze_editorial(document, 1, validation_context())

        private_change = copy.deepcopy(document)
        parts(private_change)[1]["internalScope"] += (
            " NONPRODUCTION private clarification.")
        append_correction_and_acceptances(
            private_change,
            "NONPRODUCTION FIXTURE private-scope correction.",
        )
        private_frozen = freeze_editorial(
            private_change, 1, validation_context(), previous=baseline)
        self.assertEqual(1, private_frozen["patternDataRevision"])

        runtime_change = copy.deepcopy(document)
        parts(runtime_change)[2]["learnerExplanationEn"] += (
            " NONPRODUCTION visible clarification.")
        append_correction_and_acceptances(
            runtime_change,
            "NONPRODUCTION FIXTURE visible wording correction.",
        )
        with self.assertRaises(ValidationFailure) as caught:
            freeze_editorial(
                runtime_change, 1, validation_context(), previous=baseline)
        self.assertHasCode(
            caught.exception.issues, "FROZEN_REVISION_TRANSITION")
        advanced = freeze_editorial(
            runtime_change, 2, validation_context(), previous=baseline)
        self.assertEqual(2, advanced["patternDataRevision"])

    def test_transition_requires_a_fresh_correction_not_only_fresh_approvals(self):
        document = fictional_editorial()
        baseline = freeze_editorial(document, 1, validation_context())
        changed = copy.deepcopy(document)
        parts(changed)[2]["learnerExplanationEn"] += (
            " NONPRODUCTION visible correction without an audit event.")
        append_stage_acceptances(changed)
        self.assertEditorialValid(changed)

        with self.assertRaises(ValidationFailure) as caught:
            freeze_editorial(
                changed, 2, validation_context(), previous=baseline)
        self.assertHasCode(
            caught.exception.issues, "FROZEN_WORDING_CORRECTION_REQUIRED")

    def test_new_example_is_an_addition_but_retained_origin_change_is_correction(self):
        document = fictional_editorial()
        baseline = freeze_editorial(document, 1, validation_context())

        with_addition = copy.deepcopy(document)
        pattern = parts(with_addition)[2]
        added_id = allocate_example_id(pattern["id"], "added-context")
        pattern["examples"].append({
            "id": added_id,
            "key": "added-context",
            "pl": "ZNACZNIK-NIEPRODUKCYJNY: dodany kontekst fikcyjny.",
            "en": "NONPRODUCTION-FIXTURE: an added fictional context.",
            "origin": {
                "kind": "original",
                "authorRef": "fixture-human-author",
                "authoredAt": "2026-08-09",
            },
            "audioEligible": False,
        })
        append_stage_acceptances(with_addition)
        added = freeze_editorial(
            with_addition, 2, validation_context(), previous=baseline)
        self.assertIn(added_id, {
            row["id"] for row in added["allocations"]})
        self.assertIn(
            added_id,
            [example["id"] for example in
             added["runtimeProjection"]["lemmas"][0]["meanings"][0][
                 "patterns"][0]["examples"]],
        )

        changed_origin = copy.deepcopy(document)
        parts(changed_origin)[2]["examples"][0]["origin"]["authoredAt"] = (
            "2026-08-07")
        append_stage_acceptances(changed_origin)
        with self.assertRaises(ValidationFailure) as caught:
            freeze_editorial(
                changed_origin, 1, validation_context(), previous=baseline)
        self.assertHasCode(
            caught.exception.issues, "FROZEN_ORIGIN_CORRECTION_REQUIRED")

        corrected_origin = copy.deepcopy(document)
        parts(corrected_origin)[2]["examples"][0]["origin"]["authoredAt"] = (
            "2026-08-07")
        append_correction_and_acceptances(
            corrected_origin,
            "NONPRODUCTION FIXTURE retained-origin correction.",
        )
        repaired = freeze_editorial(
            corrected_origin, 1, validation_context(), previous=baseline)
        self.assertEqual(1, repaired["patternDataRevision"])

    def test_historical_correction_cannot_authorize_a_later_wording_change(self):
        document = fictional_editorial()
        append_correction_and_acceptances(
            document,
            "NONPRODUCTION FIXTURE historical correction before release.",
        )
        baseline = freeze_editorial(document, 1, validation_context())
        changed = copy.deepcopy(document)
        parts(changed)[2]["learnerExplanationEn"] += (
            " NONPRODUCTION later visible correction.")
        append_stage_acceptances(changed)
        self.assertEditorialValid(changed)

        with self.assertRaises(ValidationFailure) as caught:
            freeze_editorial(
                changed, 2, validation_context(), previous=baseline)
        self.assertHasCode(
            caught.exception.issues, "FROZEN_WORDING_CORRECTION_REQUIRED")

    def test_frozen_runtime_projection_must_match_closed_dimensions(self):
        document = fictional_editorial()
        forged = freeze_editorial(document, 1, validation_context())
        forged["runtimeProjection"]["lemmas"][0]["meanings"][0][
            "patterns"][0]["learnerExplanationEn"] += (
                " NONPRODUCTION forged runtime-only wording.")

        with self.assertRaises(ValidationFailure) as caught:
            freeze_editorial(
                document, 1, validation_context(), previous=forged)
        self.assertHasCode(caught.exception.issues, "FROZEN_RUNTIME_PARITY")

    def test_frozen_policy_and_history_cannot_forge_research_as_approved(self):
        document = fictional_editorial()
        research_id = add_deferred_pattern(document, "research-elevation")
        approved_id = parts(document)[2]["id"]
        forged = freeze_editorial(document, 1, validation_context())
        policy_by_id = {row["id"]: row for row in forged["policy"]}
        history_by_id = {
            row["id"]: row for row in forged["reviewHistory"]}

        research_policy = policy_by_id[research_id]
        approved_policy = policy_by_id[approved_id]
        research_policy["reviewState"] = "approved"
        research_policy["currentScopeDigests"] = copy.deepcopy(
            approved_policy["currentScopeDigests"])
        for field in (
                "evidenceArchive", "currentEvidenceDigests", "reviewEvents"):
            history_by_id[research_id][field] = copy.deepcopy(
                history_by_id[approved_id][field])

        with self.assertRaises(ValidationFailure) as caught:
            freeze_editorial(
                document, 1, validation_context(), previous=forged)
        self.assertHasCode(caught.exception.issues, "FROZEN_SCOPE_PARITY")

    def test_frozen_example_origins_exactly_follow_structure_example_ids(self):
        document = fictional_editorial()
        pattern_id = parts(document)[2]["id"]
        baseline = freeze_editorial(document, 1, validation_context())
        structure = next(
            row for row in baseline["structure"] if row["id"] == pattern_id)
        history = next(
            row for row in baseline["reviewHistory"] if row["id"] == pattern_id)
        self.assertEqual(
            structure["exampleIds"],
            [row["id"] for row in history["exampleOrigins"]],
        )

        for label, mutate in (
                ("missing", lambda rows: rows.pop()),
                ("reordered", lambda rows: rows.reverse())):
            with self.subTest(label=label):
                forged = copy.deepcopy(baseline)
                forged_history = next(
                    row for row in forged["reviewHistory"]
                    if row["id"] == pattern_id)
                mutate(forged_history["exampleOrigins"])
                with self.assertRaises(ValidationFailure) as caught:
                    freeze_editorial(
                        document, 1, validation_context(), previous=forged)
                self.assertHasCode(
                    caught.exception.issues,
                    "FROZEN_EXAMPLE_ORIGIN_COVERAGE",
                )

    def test_frozen_review_history_rejects_invalid_stage_and_reopen_paths(self):
        document = fictional_editorial()
        approved_id = parts(document)[2]["id"]
        approved = freeze_editorial(document, 1, validation_context())

        stage_order = copy.deepcopy(approved)
        stage_history = next(
            row for row in stage_order["reviewHistory"]
            if row["id"] == approved_id)
        stage_history["reviewEvents"][:2] = reversed(
            stage_history["reviewEvents"][:2])
        with self.assertRaises(ValidationFailure) as caught:
            freeze_editorial(
                document, 1, validation_context(), previous=stage_order)
        self.assertHasCode(caught.exception.issues, "REVIEW_STAGE_ORDER")

        spurious_reopen = copy.deepcopy(approved)
        next(
            row for row in spurious_reopen["reviewHistory"]
            if row["id"] == approved_id
        )["reviewEvents"].append({
            "kind": "reopen",
            "decision": "accept",
            "reviewerRef": "fixture-product-human",
            "reviewedAt": "2026-08-09",
            "note": "NONPRODUCTION FIXTURE spurious reopen.",
        })
        with self.assertRaises(ValidationFailure) as caught:
            freeze_editorial(
                document, 1, validation_context(), previous=spurious_reopen)
        self.assertHasCode(caught.exception.issues, "REVIEW_REOPEN_ORDER")

        deferred_document = fictional_editorial()
        deferred_id = add_terminal_pattern(
            deferred_document, "deferred-reopen-path", "defer")
        deferred = freeze_editorial(
            deferred_document, 1, validation_context())
        lemma, meaning, _ = parts(deferred_document)
        deferred_pattern = next(
            pattern for pattern in meaning["patterns"]
            if pattern["id"] == deferred_id)

        missing_reopen = copy.deepcopy(deferred)
        next(
            row for row in missing_reopen["reviewHistory"]
            if row["id"] == deferred_id
        )["reviewEvents"].append(
            acceptance_events(
                lemma,
                meaning,
                deferred_pattern,
                reviewed_at="2026-08-09",
            )[0])
        with self.assertRaises(ValidationFailure) as caught:
            freeze_editorial(
                deferred_document,
                1,
                validation_context(),
                previous=missing_reopen,
            )
        self.assertHasCode(caught.exception.issues, "REVIEW_REOPEN_REQUIRED")

        incomplete_reopen = copy.deepcopy(deferred)
        next(
            row for row in incomplete_reopen["reviewHistory"]
            if row["id"] == deferred_id
        )["reviewEvents"].append({
            "kind": "reopen",
            "decision": "accept",
            "reviewerRef": "fixture-product-human",
            "reviewedAt": "2026-08-09",
            "note": "NONPRODUCTION FIXTURE incomplete deferred reopen.",
        })
        with self.assertRaises(ValidationFailure) as caught:
            freeze_editorial(
                deferred_document,
                1,
                validation_context(),
                previous=incomplete_reopen,
            )
        self.assertHasCode(
            caught.exception.issues,
            "REVIEW_DEFERRED_REOPEN_EXTERNAL_REQUIRED",
        )

    def test_released_review_history_is_an_exact_append_only_prefix(self):
        document = fictional_editorial()
        baseline = freeze_editorial(document, 1, validation_context())

        rewritten = copy.deepcopy(document)
        parts(rewritten)[2]["reviewEvents"][0]["note"] = (
            "NONPRODUCTION FIXTURE forged historical annotation.")
        self.assertEditorialValid(rewritten)
        with self.assertRaises(ValidationFailure) as caught:
            freeze_editorial(
                rewritten, 1, validation_context(), previous=baseline)
        self.assertHasCode(
            caught.exception.issues,
            "FROZEN_REVIEW_HISTORY_NOT_APPEND_ONLY",
        )

        removed = copy.deepcopy(document)
        lemma, meaning, pattern = parts(removed)
        pattern["reviewEvents"].pop()
        pattern["reviewEvents"].append(
            acceptance_events(
                lemma, meaning, pattern, reviewed_at="2026-08-09")[-1])
        self.assertEditorialValid(removed)
        with self.assertRaises(ValidationFailure) as caught:
            freeze_editorial(
                removed, 1, validation_context(), previous=baseline)
        self.assertHasCode(
            caught.exception.issues,
            "FROZEN_REVIEW_HISTORY_NOT_APPEND_ONLY",
        )

    def test_deleted_id_requires_tombstone_and_cannot_resurrect(self):
        document = fictional_editorial()
        retired_id = add_deferred_pattern(document, "retired-fiction")
        _, meaning, _ = parts(document)
        former_parent = meaning["id"]
        baseline = freeze_editorial(document, 1, validation_context())
        without_retired = copy.deepcopy(document)
        parts(without_retired)[1]["patterns"] = [
            pattern for pattern in parts(without_retired)[1]["patterns"]
            if pattern["id"] != retired_id
        ]

        with self.assertRaises(ValidationFailure):
            freeze_editorial(
                without_retired, 1, validation_context(), previous=baseline)

        tombstone = {
            "id": retired_id,
            "kind": "pattern",
            "formerParentId": former_parent,
            "retirementRevision": 1,
            "reason": "NONPRODUCTION FIXTURE retirement test.",
            "replacementIds": [],
        }
        retired = freeze_editorial(
            without_retired,
            1,
            validation_context(),
            previous=baseline,
            tombstones=(tombstone,),
        )
        self.assertIn(tombstone, retired["tombstones"])

        carried = freeze_editorial(
            without_retired, 1, validation_context(), previous=retired)
        self.assertIn(tombstone, carried["tombstones"])

        with self.assertRaises(ValidationFailure) as caught:
            freeze_editorial(
                document,
                1,
                validation_context(),
                previous=retired,
            )
        self.assertHasCode(caught.exception.issues, "TOMBSTONE_RESURRECTION")

    def test_allocation_only_projection_cannot_bypass_complete_tombstone_release(self):
        document = fictional_editorial()
        retired_id = parts(document)[2]["id"]
        survivor_id = add_approved_pattern(document, "approved-survivor")
        former_parent = parts(document)[1]["id"]
        baseline = freeze_editorial(document, 1, validation_context())

        without_retired = copy.deepcopy(document)
        parts(without_retired)[1]["patterns"] = [
            pattern for pattern in parts(without_retired)[1]["patterns"]
            if pattern["id"] != retired_id
        ]
        tombstone = {
            "id": retired_id,
            "kind": "pattern",
            "formerParentId": former_parent,
            "retirementRevision": 2,
            "reason": "NONPRODUCTION FIXTURE release-boundary retirement.",
            "replacementIds": [],
        }
        retired_example_ids = [
            row["id"] for row in baseline["identity"]
            if row["kind"] == "example" and row["parentId"] == retired_id
        ]
        transition_tombstones = [tombstone, *(
            {
                "id": example_id,
                "kind": "example",
                "formerParentId": retired_id,
                "retirementRevision": 2,
                "reason": "NONPRODUCTION FIXTURE retired pattern child.",
                "replacementIds": [],
            }
            for example_id in retired_example_ids
        )]
        retired = freeze_editorial(
            without_retired,
            2,
            validation_context(),
            previous=baseline,
            tombstones=transition_tombstones,
        )
        base_context = validation_context()
        allocation_context = ValidationContext(
            source_registry=base_context.source_registry,
            reviewer_registry=base_context.reviewer_registry,
            author_registry=base_context.author_registry,
            repository_index=base_context.repository_index,
            today=base_context.today,
            allocation_registry={
                row["id"]: row for row in retired["allocations"]},
        )

        # Allocation membership alone still sees the retired ID.  That is useful
        # shape checking, but intentionally has no release authority.
        standalone = project_runtime_nonrelease(
            document, 2, allocation_context)
        self.assertEqual([], validate_runtime(standalone, allocation_context))
        standalone_ids = {
            pattern["id"]
            for lemma in standalone["lemmas"]
            for meaning in lemma["meanings"]
            for pattern in meaning["patterns"]
        }
        self.assertEqual({retired_id, survivor_id}, standalone_ids)

        released = verified_runtime_from_frozen(retired)
        self.assertEqual(retired["runtimeProjection"], released)
        released_ids = {
            pattern["id"]
            for lemma in released["lemmas"]
            for meaning in lemma["meanings"]
            for pattern in meaning["patterns"]
        }
        self.assertEqual({survivor_id}, released_ids)

        forged = copy.deepcopy(retired)
        forged["runtimeProjection"] = standalone
        self.assertHasCode(
            validate_frozen_release(forged), "FROZEN_RUNTIME_PARITY")
        with self.assertRaises(ValidationFailure):
            verified_runtime_from_frozen(forged)
        with self.assertRaises(ValidationFailure) as caught:
            freeze_editorial(
                document, 3, validation_context(), previous=retired)
        self.assertHasCode(caught.exception.issues, "TOMBSTONE_RESURRECTION")

    def test_tombstone_replacement_must_resolve_to_a_new_active_allocation(self):
        document = fictional_editorial()
        retired_id = add_deferred_pattern(document, "superseded-fiction")
        baseline = freeze_editorial(document, 1, validation_context())

        replacement = copy.deepcopy(document)
        _, meaning, _ = parts(replacement)
        meaning["patterns"] = [
            pattern for pattern in meaning["patterns"]
            if pattern["id"] != retired_id
        ]
        replacement_id = add_deferred_pattern(replacement, "replacement-fiction")
        tombstone = {
            "id": retired_id,
            "kind": "pattern",
            "formerParentId": meaning["id"],
            "retirementRevision": 1,
            "reason": "NONPRODUCTION FIXTURE superseded structure.",
            "replacementIds": [replacement_id],
        }
        advanced = freeze_editorial(
            replacement,
            1,
            validation_context(),
            previous=baseline,
            tombstones=(tombstone,),
        )
        self.assertIn(tombstone, advanced["tombstones"])
        self.assertIn(
            replacement_id, {row["id"] for row in advanced["allocations"]})

        dangling = copy.deepcopy(tombstone)
        dangling["replacementIds"] = [allocate_lemma_id("widmofikcjonować")]
        with self.assertRaises(ValidationFailure) as caught:
            freeze_editorial(
                replacement,
                1,
                validation_context(),
                previous=baseline,
                tombstones=(dangling,),
            )
        self.assertHasCode(
            caught.exception.issues, "TOMBSTONE_REPLACEMENT_DANGLING")

    def test_tombstone_replacement_chain_retains_every_allocation(self):
        document = fictional_editorial()
        first_id = add_deferred_pattern(document, "chain-first")
        baseline = freeze_editorial(document, 1, validation_context())

        second_document = copy.deepcopy(document)
        _, meaning, _ = parts(second_document)
        meaning["patterns"] = [
            pattern for pattern in meaning["patterns"]
            if pattern["id"] != first_id
        ]
        second_id = add_deferred_pattern(second_document, "chain-second")
        first_tombstone = {
            "id": first_id,
            "kind": "pattern",
            "formerParentId": meaning["id"],
            "retirementRevision": 1,
            "reason": "NONPRODUCTION FIXTURE first chain replacement.",
            "replacementIds": [second_id],
        }
        second_frozen = freeze_editorial(
            second_document,
            1,
            validation_context(),
            previous=baseline,
            tombstones=(first_tombstone,),
        )

        third_document = copy.deepcopy(second_document)
        _, third_meaning, _ = parts(third_document)
        third_meaning["patterns"] = [
            pattern for pattern in third_meaning["patterns"]
            if pattern["id"] != second_id
        ]
        third_id = add_deferred_pattern(third_document, "chain-third")
        second_tombstone = {
            "id": second_id,
            "kind": "pattern",
            "formerParentId": third_meaning["id"],
            "retirementRevision": 1,
            "reason": "NONPRODUCTION FIXTURE second chain replacement.",
            "replacementIds": [third_id],
        }
        third_frozen = freeze_editorial(
            third_document,
            1,
            validation_context(),
            previous=second_frozen,
            tombstones=(second_tombstone,),
        )

        tombstones = {row["id"]: row for row in third_frozen["tombstones"]}
        self.assertEqual([second_id], tombstones[first_id]["replacementIds"])
        self.assertEqual([third_id], tombstones[second_id]["replacementIds"])
        self.assertTrue(
            {first_id, second_id, third_id}.issubset(
                {row["id"] for row in third_frozen["allocations"]}))

    def test_malformed_tombstone_ids_raise_validation_failure(self):
        document = fictional_editorial()
        retired_id = add_deferred_pattern(document, "malformed-retirement")
        baseline = freeze_editorial(document, 1, validation_context())
        without_retired = copy.deepcopy(document)
        _, meaning, _ = parts(without_retired)
        meaning["patterns"] = [
            pattern for pattern in meaning["patterns"]
            if pattern["id"] != retired_id
        ]
        template = {
            "id": retired_id,
            "kind": "pattern",
            "formerParentId": meaning["id"],
            "retirementRevision": 1,
            "reason": "NONPRODUCTION FIXTURE malformed tombstone test.",
            "replacementIds": [],
        }
        for malformed_id in (None, [], {}, "vp-p-malformed"):
            with self.subTest(malformed_id=repr(malformed_id)):
                tombstone = copy.deepcopy(template)
                tombstone["id"] = malformed_id
                with self.assertRaises(ValidationFailure):
                    freeze_editorial(
                        without_retired,
                        1,
                        validation_context(),
                        previous=baseline,
                        tombstones=(tombstone,),
                    )

    def test_reviewed_wording_correction_preserves_allocated_id(self):
        document = fictional_editorial()
        baseline = freeze_editorial(document, 1, validation_context())
        corrected = copy.deepcopy(document)
        _, _, pattern = parts(corrected)
        original_id = pattern["id"]
        pattern["learnerExplanationEn"] += " Approved fictional correction."
        append_correction_and_acceptances(
            corrected, "NONPRODUCTION FIXTURE wording correction.")
        updated = freeze_editorial(
            corrected, 2, validation_context(), previous=baseline)
        self.assertEqual(original_id, parts(corrected)[2]["id"])
        self.assertIn(original_id, {row["id"] for row in updated["allocations"]})

    def test_same_identity_lemma_and_redundant_boolean_corrections_keep_id(self):
        document = fictional_editorial()
        baseline = freeze_editorial(document, 1, validation_context())
        lemma_id = parts(document)[0]["id"]

        corrected_spelling = copy.deepcopy(document)
        lemma = parts(corrected_spelling)[0]
        lemma["canonicalLemma"] = "fikcjonowac"
        append_correction_and_acceptances(
            corrected_spelling,
            "NONPRODUCTION FIXTURE same-identity spelling correction.",
        )
        corrected = freeze_editorial(
            corrected_spelling, 2, validation_context(), previous=baseline)
        self.assertIn(lemma_id, {row["id"] for row in corrected["allocations"]})

        legacy_boolean = copy.deepcopy(baseline)
        next(
            row for row in legacy_boolean["structure"]
            if row["id"] == lemma_id
        )["reflexive"] = True
        corrected_boolean = copy.deepcopy(document)
        append_correction_and_acceptances(
            corrected_boolean,
            "NONPRODUCTION FIXTURE redundant Boolean correction.",
        )
        repaired = freeze_editorial(
            corrected_boolean,
            1,
            validation_context(),
            previous=legacy_boolean,
            legacy_reflexive_correction_ids=(lemma_id,),
        )
        self.assertIn(lemma_id, {row["id"] for row in repaired["allocations"]})

    def test_post_release_lexical_sie_change_requires_replacement(self):
        document = fictional_editorial()
        baseline = freeze_editorial(document, 1, validation_context())
        changed = copy.deepcopy(document)
        lemma, _, _ = parts(changed)
        lemma["canonicalLemma"] = FICTIONAL_LEMMA + " się"
        lemma["reflexive"] = True
        append_correction_and_acceptances(
            changed,
            "NONPRODUCTION FIXTURE lexical identity change attempt.",
        )
        with self.assertRaises(ValidationFailure):
            freeze_editorial(
                changed, 2, validation_context(), previous=baseline)


def recursively_collect_keys(value, out=None):
    out = set() if out is None else out
    if isinstance(value, dict):
        out.update(value)
        for child in value.values():
            recursively_collect_keys(child, out)
    elif isinstance(value, list):
        for child in value:
            recursively_collect_keys(child, out)
    return out


class ProjectionAndRuntimeTests(Phase2ATestCase):
    PRIVATE_KEYS = {
        "artifactStatus",
        "specificationNotice",
        "key",
        "internalScope",
        "evidence",
        "sourceId",
        "sourceKind",
        "locator",
        "factType",
        "checkedAt",
        "reviewState",
        "reviewEvents",
        "reviewerRef",
        "reviewedAt",
        "scopeVersion",
        "scopeDigest",
        "supportingEvidenceDigests",
        "origin",
        "authorRef",
        "authoredAt",
        "repositorySource",
        "evidenceRefs",
        "sourceRegistry",
        "reviewerRegistry",
        "authorRegistry",
        "editorialNotes",
    }

    def project(self, document, revision=999):
        return project_runtime_nonrelease(
            document, revision, validation_context())

    def test_projector_admits_only_current_approved_teaching_patterns(self):
        document = fictional_editorial()
        research_id = add_deferred_pattern(document)
        deferred_id = add_terminal_pattern(document, "deferred-decision", "defer")
        rejected_id = add_terminal_pattern(document, "rejected-decision", "reject")
        self.assertEditorialValid(document)
        runtime = self.project(document)
        self.assertEqual([], validate_runtime(runtime))
        runtime_patterns = runtime["lemmas"][0]["meanings"][0]["patterns"]
        self.assertEqual([parts(document)[2]["id"]], [p["id"] for p in runtime_patterns])
        serialized = json.dumps(runtime, ensure_ascii=False)
        for excluded_id in (research_id, deferred_id, rejected_id):
            self.assertNotIn(excluded_id, serialized)

    def test_projection_contains_only_the_runtime_field_contract(self):
        runtime = self.project(fictional_editorial())
        self.assertEqual({"formatVersion", "patternDataRevision", "lemmas"}, set(runtime))
        self.assertEqual(set(), self.PRIVATE_KEYS & recursively_collect_keys(runtime))
        lemma = runtime["lemmas"][0]
        meaning = lemma["meanings"][0]
        pattern = meaning["patterns"][0]
        example = pattern["examples"][0]
        self.assertEqual(
            {"id", "canonicalLemma", "displayLemma", "reflexive", "aspect", "meanings"},
            set(lemma),
        )
        self.assertEqual({"id", "glossesEn", "patterns"}, set(meaning))
        self.assertEqual({"id", "pl", "en", "audioEligible"}, set(example))

    def test_standalone_projection_surface_is_explicitly_nonrelease(self):
        wrapper = project_nonrelease_fixture(
            fictional_editorial(), 999, validation_context())
        self.assertEqual({
            "artifactStatus", "releaseAuthorized", "runtimeProjection"},
            set(wrapper),
        )
        self.assertEqual(
            "priority-7-runtime-projection-nonrelease-fixture",
            wrapper["artifactStatus"],
        )
        self.assertIs(wrapper["releaseAuthorized"], False)
        self.assertEqual([], validate_runtime(wrapper["runtimeProjection"]))
        self.assertIssues(validate_runtime(wrapper))

        cli_document = fictional_editorial()
        cli_pattern = parts(cli_document)[2]
        cli_pattern["examples"] = [cli_pattern["examples"][0]]
        cli_pattern["contentRefs"] = []
        refresh_acceptance(cli_document)
        base_context = validation_context()
        context_payload = {
            "sourceRegistry": base_context.source_registry,
            "reviewerRegistry": base_context.reviewer_registry,
            "authorRegistry": base_context.author_registry,
        }
        with tempfile.TemporaryDirectory(
                prefix="priority7-nonrelease-cli-") as temp_dir:
            document_path = Path(temp_dir, "editorial.json")
            context_path = Path(temp_dir, "context.json")
            document_path.write_text(
                json.dumps(cli_document, ensure_ascii=False), encoding="utf-8")
            context_path.write_text(
                json.dumps(context_payload, ensure_ascii=False), encoding="utf-8")
            cli_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "priority7_tooling.py"),
                    "project-fixture",
                    str(document_path),
                    "--test-pattern-data-revision",
                    "999",
                    "--context",
                    str(context_path),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(0, cli_result.returncode, cli_result.stderr)
        cli_wrapper = json.loads(cli_result.stdout)
        self.assertEqual(
            "priority-7-runtime-projection-nonrelease-fixture",
            cli_wrapper["artifactStatus"],
        )
        self.assertIs(cli_wrapper["releaseAuthorized"], False)

        help_result = subprocess.run(
            [sys.executable, str(ROOT / "priority7_tooling.py"), "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, help_result.returncode, help_result.stderr)
        self.assertIn("project-fixture", help_result.stdout)
        old_command = subprocess.run(
            [sys.executable, str(ROOT / "priority7_tooling.py"), "project"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(2, old_command.returncode)
        self.assertIn("invalid choice", old_command.stderr)

    def test_stale_approval_fails_before_projection(self):
        stale = fictional_editorial()
        parts(stale)[2]["learnerExplanationEn"] += " Stale edit."
        with self.assertRaises(ValidationFailure):
            self.project(stale)

    def test_runtime_schema_rejects_every_private_editorial_field(self):
        runtime = self.project(fictional_editorial())
        for key in sorted(self.PRIVATE_KEYS):
            with self.subTest(private_key=key):
                candidate = copy.deepcopy(runtime)
                insertion = candidate["lemmas"][0]["meanings"][0]["patterns"][0]
                insertion[key] = "NONPRODUCTION PRIVATE FIXTURE"
                self.assertHasCode(
                    validate_runtime(candidate), "RUNTIME_PRIVATE_FIELD")

    def test_runtime_revision_status_and_aspect_fail_closed(self):
        runtime = self.project(fictional_editorial())
        cases = []
        zero = copy.deepcopy(runtime)
        zero["patternDataRevision"] = 0
        cases.append(zero)
        unresolved = copy.deepcopy(runtime)
        unresolved["lemmas"][0]["aspect"] = "unresolved"
        cases.append(unresolved)
        deferred = copy.deepcopy(runtime)
        deferred["lemmas"][0]["meanings"][0]["patterns"][0][
            "teachingStatus"] = "deferred"
        cases.append(deferred)
        for candidate in cases:
            self.assertIssues(validate_runtime(candidate))

    def test_runtime_can_verify_ids_against_a_frozen_allocation_registry(self):
        document = fictional_editorial()
        frozen = freeze_editorial(document, 1, validation_context())
        runtime = frozen["runtimeProjection"]
        base_context = validation_context()
        context = ValidationContext(
            source_registry=base_context.source_registry,
            reviewer_registry=base_context.reviewer_registry,
            author_registry=base_context.author_registry,
            repository_index=base_context.repository_index,
            today=base_context.today,
            allocation_registry={
                row["id"]: row for row in frozen["allocations"]},
        )
        self.assertEqual([], validate_runtime(runtime, context))

        lemma = runtime["lemmas"][0]
        meaning = lemma["meanings"][0]
        pattern = meaning["patterns"][0]
        cases = (
            (
                "lemma",
                lambda value: value["lemmas"][0].__setitem__(
                    "id", allocate_lemma_id("runtimefikcjonować")),
                {"RUNTIME_ALLOCATION_DANGLING", "RUNTIME_ALLOCATION_PARENT"},
            ),
            (
                "meaning",
                lambda value: value["lemmas"][0]["meanings"][0].__setitem__(
                    "id",
                    allocate_meaning_id(
                        lemma["id"], lemma["canonicalLemma"], "runtime-forged"),
                ),
                {"RUNTIME_ALLOCATION_DANGLING", "RUNTIME_ALLOCATION_PARENT"},
            ),
            (
                "example",
                lambda value: value["lemmas"][0]["meanings"][0]["patterns"][0][
                    "examples"][0].__setitem__(
                        "id", allocate_example_id(pattern["id"], "runtime-forged")),
                {"RUNTIME_ALLOCATION_DANGLING"},
            ),
        )
        for label, mutate, expected_codes in cases:
            with self.subTest(entity=label):
                malformed = copy.deepcopy(runtime)
                mutate(malformed)
                codes = {
                    issue.code for issue in validate_runtime(malformed, context)}
                self.assertTrue(expected_codes.issubset(codes), codes)

    def test_validate_runtime_cli_resolves_content_refs_with_repository_root(self):
        runtime = self.project(fictional_editorial())
        runtime["lemmas"][0]["meanings"][0]["patterns"][0][
            "contentRefs"] = [{
                "kind": "card",
                "id": "priority7-nonproduction-missing-ref",
                "purpose": "support",
            }]
        with tempfile.TemporaryDirectory(
                prefix="priority7-runtime-cli-") as temp_dir:
            runtime_path = Path(temp_dir, "runtime.json")
            runtime_path.write_text(
                json.dumps(runtime, ensure_ascii=False), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "priority7_tooling.py"),
                    "validate-runtime",
                    str(runtime_path),
                    "--repository-root",
                    str(ROOT),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("CONTENT_REF_DANGLING", result.stderr)


class DeploymentIsolationTests(Phase2ATestCase):
    PRIVATE_PATH_MARKERS = (
        "tests/fixtures/priority7",
        "editorial/verb-pattern-candidates.json",
        "editorial/priority-7-authoring-context.json",
        "content/verb-patterns.json",
    )
    # Any browser-facing reference under this prefix fails closed, so a future
    # private file renamed inside the workspace cannot leak by escaping the
    # explicit marker list above.
    PRIVATE_PATH_PREFIXES = ("editorial/",)
    # Phase 2B authorises exactly these private files inside the isolated local
    # Priority 7 authoring workspace.  Existing locally is NOT the same as being
    # authorised for public production transfer: publication is denied by the
    # remaining tests in this class, which inspect the actual public surface.
    ALLOWED_PRIVATE_EDITORIAL_FILES = frozenset({
        "verb-pattern-candidates.json",
        "priority-7-authoring-context.json",
    })
    # Phase 3B authorises exactly one file under the fixture marker path: the
    # wrapped, explicitly non-release synthetic runtime fixture.  The invariant
    # moves from "absent" to "present and only this", and every other assertion
    # in this class still denies publication of it.
    # STRENGTHENED again by Priority 7 Phase 3D-1: the synthetic grammar-choose
    # mechanics records live in the same test-only directory, in their own
    # wrapped, explicitly non-release file.  The invariant is unchanged in kind -
    # exactly these files, each carrying its own non-release markers in its own
    # bytes, and every publication assertion in this class still applies to both.
    # NARROWED again by Phase 3F-A: one additional BARE public-shape rehearsal
    # fixture is allowed. Unlike the two wrapped prototype fixtures it carries
    # no private/non-release envelope at all; its isolation and unmistakably
    # synthetic content are asserted by test_priority7_phase3fa.py. It remains
    # test-only and is not a deployable runtime merely because its shape matches.
    # EXTENDED by Priority 7 Phase 5-A, not relaxed.  That phase adds one
    # synthetic PRIVATE editorial fixture and one test-only JXA loader harness
    # to the same test-only directory; the invariant stays "exactly these, and
    # nothing else".  The editorial fixture is deliberately absent from
    # FIXTURE_NONRELEASE_MARKERS below: it is not a wrapped runtime projection
    # and therefore carries no `releaseAuthorized` field to assert.  Its own
    # nonproduction marker is asserted separately.
    ALLOWED_FIXTURE_FILES = frozenset({
        "runtime-fixture.json",
        "exercise-fixture.json",
        "release-runtime-fixture.json",
        "synthetic-release-editorial.json",
        "phase5a-loader-harness.js",
    })
    FIXTURE_NONRELEASE_MARKERS = {
        "runtime-fixture.json": "priority-7-runtime-projection-nonrelease-fixture",
        "exercise-fixture.json": "priority-7-exercise-fixture-synthetic-nonrelease",
    }
    PHASE5A_EDITORIAL_FIXTURE = "synthetic-release-editorial.json"
    PHASE5A_EDITORIAL_MARKER = (
        "priority-7-phase-5a-synthetic-editorial-nonproduction")

    def test_private_editorial_workspace_is_local_only_and_never_published(self):
        """Phase 2B may hold private editorial data locally; nothing may ship.

        This replaces the Phase 2A-era assertion that ``editorial/`` must not
        exist at all.  Phase 2B explicitly authorises the private candidate
        corpus and its authoring context inside the isolated local workflow, so
        the invariant moves from "absent" to "exactly the approved private set,
        and no public runtime artefact".
        """
        editorial_root = ROOT / "editorial"
        if editorial_root.exists():
            self.assertTrue(editorial_root.is_dir())
            present = {
                str(path.relative_to(editorial_root))
                for path in editorial_root.rglob("*") if path.is_file()
            }
            self.assertEqual(
                self.ALLOWED_PRIVATE_EDITORIAL_FILES, present,
                "The private editorial workspace must contain exactly the "
                "authorised Phase 2B files; an unexpected file must fail closed "
                "rather than appear silently.",
            )

        # SUPERSEDED by Priority 7 Phase 4F-I1, which released it.  Up to 3B
        # no public runtime corpus could be produced at all; what survives is
        # that the only one that may exist is exactly the I1 release artifact,
        # pinned by digest, byte length and revision.
        self.assertEqual("complete", i1_bundle().state)
        for marker in self.PRIVATE_PATH_MARKERS:
            if marker.startswith("editorial/"):
                continue
            if marker == "tests/fixtures/priority7":
                continue          # strengthened below rather than skipped
            if marker == I1.PHASE_4FI1_RUNTIME_PATH:
                # STRENGTHENED by Priority 7 Phase 4F-I1, not relaxed.  Before
                # the release this path had to be absent; it now exists, so the
                # assertion becomes the narrower one that it holds exactly the
                # pinned release bytes and moved together with the shell and
                # the worker.  Any other file at this path fails closed.
                self.assertEqual("complete", i1_bundle().state)
                continue
            with self.subTest(marker=marker):
                self.assertFalse((ROOT / marker).exists())

        # STRENGTHENED by Priority 7 Phase 3B, not weakened.  Before this phase
        # the fixture path was asserted absent; it now exists, so the assertion
        # becomes three narrower ones: it holds exactly the one authorised
        # wrapped fixture, that fixture says in its own bytes that it is not
        # release-authorised, and it stays out of every public surface (the
        # marker sweep in the next test, which is unchanged).
        fixture_root = ROOT / "tests" / "fixtures" / "priority7"
        self.assertTrue(fixture_root.is_dir())
        self.assertEqual(
            self.ALLOWED_FIXTURE_FILES,
            {
                str(path.relative_to(fixture_root))
                for path in fixture_root.rglob("*") if path.is_file()
            },
            "The fixture path holds exactly the enumerated synthetic fixtures; "
            "any other file there must fail closed rather than appear silently.",
        )
        for name, marker in self.FIXTURE_NONRELEASE_MARKERS.items():
            with self.subTest(fixture=name):
                fixture = json.loads(
                    (fixture_root / name).read_text(encoding="utf-8"))
                self.assertEqual(marker, fixture["artifactStatus"])
                self.assertIs(False, fixture["releaseAuthorized"])

        # The Phase 5-A private editorial fixture carries its own nonproduction
        # marker, and its inner editorial document keeps the ordinary editorial
        # envelope so the real tooling validates it unchanged.
        phase5a = json.loads(
            (fixture_root / self.PHASE5A_EDITORIAL_FIXTURE).read_text(
                encoding="utf-8"))
        self.assertEqual(
            self.PHASE5A_EDITORIAL_MARKER, phase5a["artifactStatus"])
        self.assertEqual(
            "priority-7-editorial-nonproduction",
            phase5a["editorial"]["artifactStatus"])
        self.assertNotIn("releaseAuthorized", phase5a)

    def test_fixture_cannot_enter_data_or_audio_discovery_globs(self):
        self.assertEqual(
            [
                "data-a1.js",
                "data-a2.js",
                "data-b1.js",
                "data-grammar.js",
                "data-podcasts.js",
                "data-scenarios.js",
                "data-verbs.js",
            ],
            sorted(Path(path).name for path in glob.glob(str(ROOT / "data-*.js"))),
        )
        self.assertFalse(any(
            marker.endswith(".js") or Path(marker).name.startswith("data-")
            for marker in self.PRIVATE_PATH_MARKERS
        ))

    def test_app_service_worker_sitemap_and_generated_outputs_exclude_private_paths(self):
        # SUPERSEDED IN ONE MARKER by Priority 7 Phase 4F-I1, and in no other.
        # ``content/verb-patterns.json`` was a private marker here because no
        # release existed: naming it in a public surface could only have been a
        # leak.  I1 makes it the official public runtime path, so the sweep is
        # made over the shell and worker with the I1 layer removed, where it
        # still says exactly what it said.  A SECOND reference, a different
        # runtime URL or a preview/fixture URL survives normalisation and is
        # still reported, and the live count is pinned separately below.
        index = pre_i1("index.html")
        worker = pre_i1("sw.js")
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        outputs, _, _ = build_pages.build_outputs(str(ROOT))
        public_text = "\n".join([index, worker, sitemap, *outputs.values()])
        for marker in self.PRIVATE_PATH_MARKERS:
            with self.subTest(marker=marker):
                self.assertNotIn(marker, public_text)

        # LIVE, and unconditional: the official runtime path appears exactly
        # where the I1 bundle puts it and nowhere else.  Once in the shell (the
        # single production URL constant), twice in the worker (the required
        # precache entry and its canonical path constant), and never in a
        # generated page or the sitemap.
        live_index = (ROOT / "index.html").read_text(encoding="utf-8")
        live_worker = (ROOT / "sw.js").read_text(encoding="utf-8")
        runtime_marker = I1.PHASE_4FI1_RUNTIME_PATH
        self.assertEqual(1, live_index.count(runtime_marker))
        self.assertEqual(2, live_worker.count(runtime_marker))
        self.assertNotIn(runtime_marker, sitemap)
        for name, text in outputs.items():
            with self.subTest(output=name):
                self.assertNotIn(runtime_marker, text)
        for prefix in self.PRIVATE_PATH_PREFIXES:
            with self.subTest(prefix=prefix):
                self.assertNotIn(
                    prefix, public_text,
                    "No browser-facing loader, service-worker precache entry, "
                    "sitemap URL or generated page may reference the private "
                    "editorial workspace under any filename.")

        # AMENDED by Priority 7 Phase 3B: eleven entries become twelve, because
        # the phase adds the verb-pattern consumer.  The assertion is narrowed,
        # not relaxed - it is still an exact, ordered list of named files, so a
        # thirteenth entry, a reordering or a path outside this list still fails.
        # The file added here is isolated: Phase 3F-A gives it one dormant,
        # injected transport primitive, but index.html still has no call site or
        # runtime URL, so there is no browser-reachable Priority 7 data path.
        scripts = re.findall(r'<script src="([^"]+)"', index)
        self.assertEqual([
            "data-a1.js",
            "data-a2.js",
            "data-b1.js",
            "data-grammar.js",
            "data-verbs.js",
            "data-scenarios.js",
            "data-podcasts.js",
            "pp-usage.js",
            "pp-answer.js",
            "pp-distractor.js",
            "pp-migrate.js",
            "pp-verb-patterns.js",
        ], scripts)
        self.assertEqual(32, len(ET.fromstring(sitemap)))

    def test_generator_outputs_remain_current_and_owned_directories_contain_no_fixture(self):
        outputs, _, _ = build_pages.build_outputs(str(ROOT))
        self.assertEqual([], build_pages.drift_report(outputs, str(ROOT)))
        for path in outputs:
            self.assertFalse(path.startswith("tests/"), path)
        for directory in build_pages.GENERATED_DIRS:
            for marker in self.PRIVATE_PATH_MARKERS:
                self.assertFalse((ROOT / directory / marker).exists())

    PRODUCTION_BASELINE = "f6bdc73a86f8b114582d52d0380e7289b8f2fe5d"
    # AMENDED by Priority 7 Phase 3B.  index.html is deliberately edited by that
    # phase - it adds the read-first Verb Patterns screen and closes the
    # routeTopic fallthrough - so it moves out of the byte-identical set and into
    # its own, narrower assertion below.  Every other protected path stays exactly
    # as it was: byte-identical to the production baseline.  Nothing was dropped
    # from the protected surface, and no path was removed from scrutiny.
    PROTECTED_UNCHANGED = (
        "sw.js", "pp-migrate.js", "manifest.json", "robots.txt",
        "sitemap.xml", "build_pages.py", "validate_content.py", "generate_audio.py",
        "verify_audio.py", "pp_audio_rule.py", "data-a1.js", "data-a2.js",
        "data-b1.js", "data-grammar.js", "data-verbs.js", "data-scenarios.js",
        "data-podcasts.js", "audio-manifest.json", "grammar", "vocabulary",
        "guide", "audio", "fonts", "favicon.svg", "apple-touch-icon.png",
        "icon-192.png", "icon-512.png", "icon-maskable-512.png", "og-image.png",
    )
    # The complete set of lines Phase 3B was allowed to REMOVE from the shipping
    # shell, each one part of the routing remediation.  A removal outside this
    # list fails, which is what keeps the assertion meaningful without a new
    # baseline commit: additive work is separately constrained below, and every
    # pinned contract in the JXA suites still holds the rest of the file down.
    ALLOWED_INDEX_REMOVALS_3B = (
        '  else startTopic(li, ti);                              /* vocab + podcast */',
        '  if(t.mature){',
        '    return;',
        '  routeTopic(li, ti, t);',
        '  if(p) routeTopic(p.li, p.ti, p.t);',
    )
    # NARROWED by Priority 7 Phase 3D-1, not relaxed.  That phase adds two narrow
    # extension points to the existing Grammar choose engine - one for a drill
    # whose text arrives as DATA rather than as authored markup, one for options
    # that carry an explicit identity beside their label - plus the guard that
    # keeps Back and `Review the lesson` off a practice set that has no lesson.
    # Every line it removes is enumerated here.  The authored markup path is
    # RETAINED, byte for byte, inside the new else branch: the innerHTML line
    # below reappears one indent level deeper and is asserted present, unchanged,
    # by tests/test_priority7_choose_ui.js, and the 612 assertions in
    # tests/test_grammar_interaction.js re-prove the authored behaviour whole.
    ALLOWED_INDEX_REMOVALS_3D1 = (
        '  const p=c.prompt.replace("___",\'<span class="blank"></span>\');',
        '  const dt = c._case ? "Choose the right form \\u00b7 <b>"+c._case+"</b>"'
        ' : "Choose the right form";',
        '  card.innerHTML=\'<div class="d-type" id="gInstruction">\'+dt+\'</div>'
        '<h2 class="q-prompt" id="gQuestion" lang="pl" tabindex="-1">\'+p+\'</h2>'
        '<div class="q-en" id="gQuestionMeaning">\'+c.promptEn+\'</div>'
        '<div class="opts" role="group" aria-labelledby="gInstruction gQuestion">'
        '</div><div class="fb-box" id="gFbBox"></div>\';',
        '  const box=card.querySelector(".opts");',
        '    btn.setAttribute("lang","pl");',
        '    btn.setAttribute("data-val",o);',
        '    btn.textContent=o;',
        '      const val=btn.getAttribute("data-val");',
        '        btn.setAttribute("aria-label",val+", correct");',
        '        gAnnounceCorrect(c.answer);',
        # The four retry lines below moved one indent deeper into the `else`
        # branch of the opt-in reveal, and are otherwise unchanged: an authored
        # drill still marks the chosen option, disables only that one, announces
        # the retry verdict and moves focus to the next available option.
        '        btn.setAttribute("aria-label",val+", incorrect. Try again");',
        '        btn.disabled=true;',
        '        gAnnounceWrong(val);',
        '        gFocusNextOption(box,btn);',
        '$("gBack").addEventListener("click", ()=>{'
        ' if($("gPractice").style.display!=="none"){ gRenderTeach();'
        ' gPhaseView("learn"); } else show("home"); });',
    )
    # NARROWED again by the Phase 3D-1 independent-review correction, and for the
    # same reason: each line below is REPLACED in place, not dropped.
    #  * the two announcer lines move behind an `Array.isArray` branch, so a
    #    plain authored answer still becomes exactly one lang="pl" element and a
    #    mixed structural label is segmented instead of wrongly wrapped in one;
    #  * `G` gains one in-memory array and `gStartPractice` resets it, so the
    #    completion summary can tell a retry that was cleared from one that was
    #    not - `G.results` records first-try only and cannot answer that;
    #  * the four completion lines move into `gDoneMessage`, which returns the
    #    IDENTICAL sentence for every authored round (every retry there ends on
    #    the right answer, because nothing else advances the drill).
    ALLOWED_INDEX_REMOVALS_3D1_REVIEW = (
        'const G = { topic:null, li:0, tpi:0, ti:0, di:0, results:[],'
        ' attempted:false, state:"ask", build:{pool:[],row:[]} };',
        '  G.queue=G.topic.mixOf ? G.topic.drills.slice() :'
        ' gShuffle(G.topic.drills); G.di=0; G.results=[];'
        ' gPhaseView("practice"); gRenderDrill();',
        # once in gAnnounceWrong, once in gAnnounceCorrect
        '  answer.setAttribute("lang","pl");',
        '  answer.setAttribute("lang","pl");',
        '  answer.textContent=label;',
        '  answer.textContent=pl;',
        '  const retried=G.queue.length-total;',
        '  $("gDoneMsg").textContent = score===total',
        '    ? "Every answer right on the first try. This is clicking."',
        '    : "Nice work through the set - "+retried+" drill"+(retried===1?"":"s")'
        '+" came back for a second pass and you cleared "'
        '+(retried===1?"it":"them")+".";',
    )
    # Priority 7 Phase 3E replaces exactly these six pre-existing activity CSS
    # declarations. The replacement declarations preserve every prior property
    # and add only max-width / overflow-wrap so a hostile unbroken runtime token
    # cannot create horizontal page overflow. No content, behaviour, breakpoint,
    # hidden-overflow workaround or release marker is involved.
    ALLOWED_INDEX_REMOVALS_3E = (
        '  .q-prompt{margin:0;font-size:22px;font-weight:800;line-height:1.35;'
        'letter-spacing:-.4px;color:var(--forest)}',
        '  .q-en{font-size:14px;color:var(--muted);font-weight:500;margin-top:8px}',
        '  .opt{border:1.5px solid var(--border);background:#fff;color:var(--forest);'
        'border-radius:14px;padding:14px 16px;font-size:16px;font-weight:700;'
        'cursor:pointer;text-align:center;transition:.14s;font-family:inherit}',
        '  .fb-good .p{font-size:15.5px;font-weight:700;color:var(--forest);line-height:1.35}',
        '  .fb-good .e{font-size:12.5px;color:var(--muted);margin-top:2px}',
        '  .fb-explain{font-size:13px;color:var(--sage-hover);font-weight:600;'
        'margin-top:9px;line-height:1.45}',
    )
    ALLOWED_INDEX_REMOVALS = (ALLOWED_INDEX_REMOVALS_3B +
                              ALLOWED_INDEX_REMOVALS_3D1 +
                              ALLOWED_INDEX_REMOVALS_3D1_REVIEW +
                              ALLOWED_INDEX_REMOVALS_3E)

    def _diff(self, *paths):
        return subprocess.run(
            ["git", "diff", "--exit-code", self.PRODUCTION_BASELINE, "--", *paths],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )

    # AMENDED by Priority 7 Phase 4F-I1, exactly as Phase 3B amended it for
    # index.html.  I1 is a release, so ``sw.js``, ``sitemap.xml`` and the three
    # generated-page trees legitimately move.  They are not dropped from
    # scrutiny: they move into the narrower classification below, which admits
    # only the pinned I1 transition and reports every other byte.
    I1_RELEASE_PATHS = ("sw.js", "sitemap.xml", "grammar", "vocabulary", "guide")

    def test_protected_application_surface_matches_untouched_production_baseline(self):
        untouched = [path for path in self.PROTECTED_UNCHANGED
                     if path not in self.I1_RELEASE_PATHS]
        self.assertEqual(
            len(self.PROTECTED_UNCHANGED) - len(self.I1_RELEASE_PATHS),
            len(untouched))
        result = self._diff(*untouched)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_the_release_paths_moved_by_exactly_the_i1_transition(self):
        """Every path I1 was entitled to move, and nothing beyond the layer.

        ``sw.js`` is classified through the all-or-nothing bundle, so it can
        only pass while the runtime and the shell moved with it.  Each
        generated page may differ by its footer version stamp alone, and the
        sitemap by ``<lastmod>`` values alone -- an added, removed or reordered
        URL, or any other byte, still fails.
        """
        bundle = i1_bundle()
        changed = subprocess.run(
            ["git", "diff", "--name-only", self.PRODUCTION_BASELINE, "--",
             *self.I1_RELEASE_PATHS],
            cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual("", changed.stderr)
        moved = sorted(line for line in changed.stdout.splitlines() if line)
        self.assertTrue(moved, "the release guard must have evidence")
        for relative in moved:
            with self.subTest(path=relative):
                self.assertTrue(I1.is_phase_4fi1_path(relative), relative)
                baseline = subprocess.run(
                    ["git", "show", f"{self.PRODUCTION_BASELINE}:{relative}"],
                    cwd=ROOT, capture_output=True, text=True, check=False)
                self.assertEqual(0, baseline.returncode, relative)
                self.assertTrue(
                    I1.is_exactly_the_i1_transition(
                        relative, baseline.stdout,
                        (ROOT / relative).read_text(encoding="utf-8"),
                        bundle=bundle),
                    relative)

    def test_app_shell_changes_are_confined_to_the_reviewed_phase_3b_edit(self):
        """index.html changed on purpose; this states exactly how far.

        The original assertion diffed the shell against a fixed commit and
        required emptiness.  Phase 3B edits the shell, and Phase 3B does not
        commit, so there is no newer reviewed commit for the baseline to move to.
        The safety intent is preserved by narrowing instead: every line removed
        from the shell must be one of the five routing lines this phase was
        authorised to replace, and nothing added to it may reference a private
        path, the fixture, the non-release wrapper or a runtime corpus.
        """
        # RESTATED over the pre-I1 shell by Priority 7 Phase 4F-I1.  I1 is the
        # release that adds the loader activation and the version bump, both of
        # which this Phase 3B claim forbids.  Removing the pinned I1 layer puts
        # the shell back where this assertion was written, and every byte I1
        # did not pin is still compared.
        baseline = subprocess.run(
            ["git", "show", f"{self.PRODUCTION_BASELINE}:index.html"],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(0, baseline.returncode, baseline.stderr)
        diff_lines = list(difflib.unified_diff(
            baseline.stdout.splitlines(),
            pre_i1("index.html").splitlines(),
            lineterm="", n=0,
        ))
        removed = [
            line[1:] for line in diff_lines
            if line.startswith("-") and not line.startswith("---")
        ]
        added = [
            line[1:] for line in diff_lines
            if line.startswith("+") and not line.startswith("+++")
        ]
        self.assertEqual(
            sorted(self.ALLOWED_INDEX_REMOVALS), sorted(removed),
            "Phase 3B removes exactly the routing lines it replaces; any other "
            "deletion from the shipping shell is unreviewed.",
        )
        self.assertTrue(added, "The phase is expected to add the new surface.")
        forbidden = (
            "editorial/", "tests/fixtures", "runtime-fixture", "runtimeProjection",
            "releaseAuthorized", "artifactStatus", "content/verb-patterns.json",
            "__acceptForTest",
        )
        for line in added:
            for token in forbidden:
                with self.subTest(token=token):
                    self.assertNotIn(token, line)
        # The added surface must not have moved any version or cache marker.
        self.assertFalse([line for line in added if "APP_VERSION" in line])


if __name__ == "__main__":
    unittest.main()
