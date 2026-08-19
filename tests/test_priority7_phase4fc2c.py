"""Priority 7 Phase 4F-C2C — provenance collision repair.

Phase 4F-C2B returned NO-GO on one contained finding: two editorial-generated
sentences collided exactly with pre-existing language-learning material.  This
phase replaces those two sentences and nothing else.

What the suite proves:

1.  **The override is two rows wide.**  Exactly ``P7-NR-033`` and
    ``P7-NR-043``; its prior wording is the C1C wording it supersedes; its
    final wording is what the corpus holds; and the six historical
    normalizers, the C2 suite and this suite all declare the same map.
2.  **Everything else is the arriving C2 candidate.**  Undoing the override
    reproduces the arriving C2 corpus at its pinned SHA-256, so the two
    ``pl``/``en`` pairs are provably the only canonical change.  The nine
    other generated examples, the eighteen reuse examples and the authoring
    context are byte-identical.
3.  **Identity survived the wording change.**  Both durable keys and both
    deterministic IDs are the C2 ones and still recompute; 29 examples; no
    second example; no ``original`` origin; no new actor.
4.  **Governance is untouched.**  45 ``reference-verified`` derived by the
    tooling, 47 acceptances, no editorial-review or product-approval event,
    tier-1 digests unchanged, and higher-scope digest *values* moving on
    exactly the two rows while the changed *set* stays C2's eleven.
5.  **History was preserved.**  The C1/C1B/C1C artifacts, the C2 report and
    the C2B NO-GO are byte-identical to what arrived.
6.  **The boundary still has teeth.**  Exact C2C normalizes to the historical
    checkpoint; a third row's wording, an identity mutation, a provenance
    mutation, a role escalation and a meaning/evidence mutation all still
    survive normalization and are still rejected by the validator.

Every mutation below is applied to an in-memory copy.  Nothing here writes to
the corpus, the context, the tooling or any shipping file.
"""

from __future__ import annotations

import collections
import copy
import csv
import hashlib
import importlib
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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
from priority7_tooling import validate_editorial  # noqa: E402
from tests import test_priority7_phase4fc2 as C2  # noqa: E402
from tests import test_priority7_phase4fc2b as C2B  # noqa: E402

CORPUS = ROOT / "editorial" / "verb-pattern-candidates.json"
CONTEXT_FILE = ROOT / "editorial" / "priority-7-authoring-context.json"
C1C_MATRIX = ROOT / "reports" / "phase-4fc1c" / "adjudication-matrix.csv"
C2_SUMMARY = ROOT / "reports" / "priority-7-phase-4fc2-summary.md"
C2B_SUMMARY = ROOT / "reports" / "priority-7-phase-4fc2b-summary.md"
C2C_SUMMARY = ROOT / "reports" / "priority-7-phase-4fc2c-summary.md"
C2C_MATRIX = (ROOT / "reports" /
              "priority-7-phase-4fc2c-provenance-adjudication.csv")

BASELINE_COMMIT = "080d92ad49a514332f21ecd90b4a11de070a243f"
BASELINE_TREE = "74dd8cbebc303b646e4e38e2082d25c91b1cf6e1"

#: The arriving Phase 4F-C2 candidate, which C2B reviewed and this phase
#: repairs.  C2 was never committed, so there is no tree to read it from: the
#: check is that undoing exactly the two-row override reproduces these bytes.
C2_CANDIDATE_CORPUS_SHA256 = (
    "cec93c71f772bef7a6f458400e70e225ba873238e9f313ffce7eb35c3e606701")
#: The authoring context is not touched by this phase at all.
C2_CANDIDATE_CONTEXT_SHA256 = (
    "bee8eb95ed78775e50a7fc57da2381d67c43087b00c836e6e6cb0c81925df718")

#: Historical artifacts this phase must not edit, pinned as they arrived.
PRESERVED_ARTIFACTS = {
    "reports/phase-4fc1/blind-review-input.csv":
        "0af6c076be5c569074ed861e2c8e65fdd0bd048c3fa538f01ebbec60fac45771",
    "reports/phase-4fc1/example-matrix.csv":
        "2422eed842c558f8cd6671123563b88b02e5464c0d06f63ed57fce817a410f4f",
    "reports/phase-4fc1/summary.md":
        "45ad110a3e2bcbd9c4c8f8881824b219ccbe0e0c293bcd364ee1877021599d7f",
    "reports/phase-4fc1b/example-review-matrix.csv":
        "0f43a13f300e94d5edb50018bcdab5de7c145a75040c8ba70b1a4064bc1ad50e",
    "reports/phase-4fc1b/summary.md":
        "645a4252eb911f802ead3f8ce3d3afe265970d7c49befbc83da6c83e659cdb9f",
    "reports/phase-4fc1c/adjudication-matrix.csv":
        "0c5c7f83b240b2d02ed1dc3a04a5522ca9e8227a74e175cb0fc17404aab69044",
    "reports/phase-4fc1c/summary.md":
        "21fe7541a784768dbeaf45f226af27835778a6830120b36f27e3b9b097405d64",
    "reports/priority-7-phase-4fc2-summary.md":
        "e12768828935c67d138ae77717bef0e68de10fe2c02047e8bbc2e5e332ed38d9",
    "reports/priority-7-phase-4fc2b-summary.md":
        "09995264798fe6402355ee16390ace9e7e6f3808b0a980489bfd1e7b3f778329",
}

#: The two rows, and nothing else.  Held here as the phase's own copy so the
#: consistency test compares independent declarations rather than one shared
#: constant re-imported under three names.
OVERRIDE = {
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

#: The six historical suites C2B repaired and this phase re-pointed.
HISTORICAL_MODULES = C2B.HISTORICAL_MODULES

C2C_ARTIFACTS = {
    "reports/priority-7-phase-4fc2c-provenance-adjudication.csv",
    "reports/priority-7-phase-4fc2c-summary.md",
    "tests/test_priority7_phase4fc2c.py",
}

C2C_MATRIX_FIELDS = [
    "reviewId", "priorPolish", "priorEnglish", "collisionClass",
    "collisionSource", "adjudication", "finalPolish", "finalEnglish",
    "finalOrigin", "identityHandling", "rationale",
]

GENERATION_ACTOR = "priority7-example-generation"
REFERENCE_ACTOR = "priority7-reference-analysis"
ADOPTED_AT = "2026-08-16"

PATTERN_COUNT = 45
EXAMPLE_COUNT = 29
REPOSITORY_REUSE_COUNT = 18
EDITORIAL_GENERATED_COUNT = 11
REFERENCE_VERIFIED_COUNT = 45
REFERENCE_ACCEPT_COUNT = 47
C2_IMPLEMENTED_ROW_COUNT = 11

TIER_ONE_STAGES = ("reference-verification", "external-verification")
HIGHER_SCOPE_STAGES = ("editorial-review", "native-linguistic",
                       "product-approval")


def git(*arguments):
    return subprocess.run(["git", *arguments], cwd=ROOT, capture_output=True,
                          text=True)


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_path(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


#: Phase 4F-D3.1 applied three approved editorial-tier wording corrections
#: after this phase closed.  This suite reconstructs and pins the arriving C2
#: candidate by text, so that later approved work is reverted by text here,
#: under the same discipline the C2C override itself uses: each substitution
#: declares how many matches it requires and fails loudly on any other count.
#: The map is C2's closed literal; nothing else may be reverted.
def without_phase_4fd31_text(text):
    """Return ``text`` with exactly the three D3.1 corrections reverted."""
    for row in sorted(C2.PHASE_4FD31_EDITORIAL_CORRECTION.values(),
                      key=lambda item: item["patternId"]):
        for field, expected in (("exampleEn", 1),
                                ("learnerExplanationEn", 1),
                                ("guidanceEn", 1)):
            if field not in row:
                continue
            prior, final = row[field]
            if field == "exampleEn":
                needle, replacement = '"en": "%s"' % final, '"en": "%s"' % prior
            else:
                needle, replacement = '"%s": "%s"' % (field, final), \
                    '"%s": "%s"' % (field, prior)
            count = text.count(needle)
            if count != expected:
                raise AssertionError(
                    "expected exactly %d Phase 4F-D3.1 %s match for %s, "
                    "found %d" % (expected, field, row["patternId"], count))
            text = text.replace(needle, replacement)
    return text


def corpus_text():
    """The corpus text as Phase 4F-C2C left it, with later work reverted.

    Phase 4F-D3.1's three wording corrections are reverted by text.  Phase
    4F-E1's 45 tier-2 acceptances are reverted first, through the phase-owned
    text normaliser, which asserts the file's canonical stored form rather
    than assuming it.
    """
    return without_phase_4fd31_text(
        E1.without_phase_4fe1_corpus_text(
            F2.without_phase_4ff2_corpus_text(
                H2.without_phase_4fh2_corpus_text(
                    H21.without_phase_4fh21_corpus_text(
                        CORPUS.read_text(encoding="utf-8"))))))


def c2_candidate_text():
    """The arriving C2 corpus text, reconstructed by undoing the override.

    Substitutes on the ``"pl"``/``"en"`` pair together so a coincidental
    sentence elsewhere in the file cannot be rewritten, and requires exactly
    one match per row.
    """
    text = corpus_text()
    for review_id, row in sorted(OVERRIDE.items()):
        found = re.compile(
            r'("pl": )"%s"(,\n\s*"en": )"%s"'
            % (re.escape(row["finalPl"]), re.escape(row["finalEn"])))
        text, count = found.subn(
            lambda match, row=row: '%s"%s"%s"%s"' % (
                match.group(1), row["priorPl"], match.group(2),
                row["priorEn"]),
            text)
        if count != 1:
            raise AssertionError(
                f"expected exactly one C2C pair for {review_id}, found {count}")
    return text


def corpus():
    return json.loads(corpus_text())


def c2_candidate():
    return json.loads(c2_candidate_text())


def context_text():
    """The context text as Phase 4F-C2C left it, with E1's registry gone."""
    return E1.without_phase_4fe1_context_text(
        F2.without_phase_4ff2_context_text(
            H2.without_phase_4fh2_context_text(
                H21.without_phase_4fh21_context_text(
                    CONTEXT_FILE.read_text(encoding="utf-8")))))


def context_document():
    return json.loads(context_text())


def baseline_corpus():
    result = git("show", f"{BASELINE_COMMIT}:editorial/"
                         "verb-pattern-candidates.json")
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


def c1c_rows():
    with C1C_MATRIX.open(newline="", encoding="utf-8") as handle:
        return {row["reviewId"]: row for row in csv.DictReader(handle)}


def c2c_rows():
    with C2C_MATRIX.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def patterns_by_id(document):
    return C2.patterns_by_id(document)


def example_of(document, review_id):
    pattern_id = c1c_rows()[review_id]["patternId"]
    examples = patterns_by_id(document)[pattern_id][2].get("examples") or []
    return examples[0] if len(examples) == 1 else None


class Phase4FC2CTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.corpus = corpus()
        cls.c2 = c2_candidate()
        cls.baseline = baseline_corpus()
        cls.document = context_document()
        cls.c1c = c1c_rows()
        cls.current = patterns_by_id(cls.corpus)
        cls.prior = patterns_by_id(cls.c2)
        cls.before = patterns_by_id(cls.baseline)


# ---------------------------------------------------------------------------
# 1.  The override is exactly two rows
# ---------------------------------------------------------------------------

class OverrideShapeTests(Phase4FC2CTestCase):

    def test_the_override_names_exactly_the_two_collided_rows(self):
        self.assertEqual({"P7-NR-033", "P7-NR-043"}, set(OVERRIDE))

    def test_both_rows_are_real_c1c_implementation_rows(self):
        for review_id in OVERRIDE:
            with self.subTest(review_id=review_id):
                row = self.c1c[review_id]
                self.assertIn(row["implementationDisposition"],
                              {"REPLACE", "CREATE"})
                self.assertEqual("editorial-generated", row["finalOrigin"])
                self.assertEqual("", row["finalRepositorySource"])
                self.assertIn(row["patternId"], self.current)

    def test_the_prior_wording_is_the_c1c_wording_it_supersedes(self):
        for review_id, row in OVERRIDE.items():
            with self.subTest(review_id=review_id):
                self.assertEqual(self.c1c[review_id]["finalPolish"],
                                 row["priorPl"])
                self.assertEqual(self.c1c[review_id]["finalEnglish"],
                                 row["priorEn"])

    def test_the_prior_wording_is_what_the_c2_candidate_actually_held(self):
        for review_id, row in OVERRIDE.items():
            with self.subTest(review_id=review_id):
                example = example_of(self.c2, review_id)
                self.assertIsNotNone(example)
                self.assertEqual(row["priorPl"], example["pl"])
                self.assertEqual(row["priorEn"], example["en"])

    def test_the_final_wording_actually_replaces_something(self):
        for review_id, row in OVERRIDE.items():
            with self.subTest(review_id=review_id):
                self.assertNotEqual(row["priorPl"], row["finalPl"])
                self.assertNotEqual(row["priorEn"], row["finalEn"])

    def test_no_other_c1c_row_is_overridden(self):
        for review_id, row in self.c1c.items():
            if review_id in OVERRIDE:
                continue
            with self.subTest(review_id=review_id):
                if row["implementationDisposition"] == "KEEP CURRENT":
                    continue
                example = example_of(self.corpus, review_id)
                self.assertEqual(row["finalPolish"], example["pl"])
                self.assertEqual(row["finalEnglish"], example["en"])

    def test_every_declaration_of_the_override_agrees(self):
        """Three independent copies exist; they must be the same map."""
        declarations = {"tests.test_priority7_phase4fc2c": OVERRIDE,
                        "tests.test_priority7_phase4fc2":
                            C2.PHASE_4FC2C_WORDING_OVERRIDE}
        for name in HISTORICAL_MODULES:
            declarations[name] = importlib.import_module(
                name).PHASE_4FC2C_WORDING_OVERRIDE
        self.assertEqual(8, len(declarations))
        for name, declared in declarations.items():
            with self.subTest(module=name):
                self.assertEqual(OVERRIDE, declared)

    def test_the_override_refuses_a_matrix_that_no_longer_matches(self):
        """It supersedes a known wording, not whatever the matrix says."""
        row = dict(self.c1c["P7-NR-033"])
        row["finalPolish"] = "Zmieniona macierz."
        with self.assertRaises(AssertionError):
            C2.effective_final(row)
        for name in HISTORICAL_MODULES:
            module = importlib.import_module(name)
            with self.subTest(module=name):
                with self.assertRaises(AssertionError):
                    module.phase_4fc2c_final_wording(row)


# ---------------------------------------------------------------------------
# 2.  Everything else is the arriving C2 candidate
# ---------------------------------------------------------------------------

class C2ReconstructionTests(Phase4FC2CTestCase):

    def test_undoing_the_override_reproduces_the_arriving_c2_corpus(self):
        self.assertEqual(C2_CANDIDATE_CORPUS_SHA256,
                         sha256_text(c2_candidate_text()))

    def test_the_corpus_actually_moved(self):
        self.assertNotEqual(C2_CANDIDATE_CORPUS_SHA256,
                            sha256_text(corpus_text()))

    def test_the_authoring_context_is_byte_identical_to_the_c2_candidate(self):
        # Phase 4F-E1 appended two actor records and one notice paragraph.
        # Removing exactly those two blocks must reproduce the C2 candidate
        # byte for byte; any edit to either leaves the hash wrong.
        self.assertEqual(
            C2_CANDIDATE_CONTEXT_SHA256,
            hashlib.sha256(context_text().encode("utf-8")).hexdigest())

    def test_exactly_four_canonical_values_moved(self):
        expected = set()
        for review_id in OVERRIDE:
            example = example_of(self.c2, review_id)
            for field in ("pl", "en"):
                expected.add((example["id"], field))
        self.assertEqual(4, len(expected))
        self.assertEqual(expected, set(self.changed_example_fields()))

    def changed_example_fields(self):
        prior = {example["id"]: example
                 for example in C2.all_examples(self.c2)}
        for example in C2.all_examples(self.corpus):
            before = prior[example["id"]]
            for field in sorted(set(before) | set(example)):
                if before.get(field) != example.get(field):
                    yield example["id"], field

    def test_the_nine_other_generated_examples_are_byte_identical(self):
        overridden = {example_of(self.c2, review_id)["id"]
                      for review_id in OVERRIDE}
        prior = {example["id"]: example
                 for example in C2.all_examples(self.c2)}
        generated = [example for example in C2.all_examples(self.corpus)
                     if example["origin"]["kind"] == "editorial-generated"]
        self.assertEqual(EDITORIAL_GENERATED_COUNT, len(generated))
        untouched = [example for example in generated
                     if example["id"] not in overridden]
        self.assertEqual(9, len(untouched))
        for example in untouched:
            with self.subTest(example_id=example["id"]):
                self.assertEqual(prior[example["id"]], example)

    def test_every_reuse_example_is_byte_identical_to_the_baseline(self):
        baseline = {example["id"]: example
                    for example in C2.all_examples(self.baseline)}
        reuse = [example for example in C2.all_examples(self.corpus)
                 if example["origin"]["kind"] == "repository-reuse"]
        self.assertEqual(REPOSITORY_REUSE_COUNT, len(reuse))
        for example in reuse:
            with self.subTest(example_id=example["id"]):
                self.assertEqual(baseline[example["id"]], example)

    def test_no_pattern_field_outside_the_examples_moved(self):
        self.assertEqual(set(self.prior), set(self.current))
        for pattern_id, (lemma, meaning, pattern) in self.current.items():
            prior_lemma, prior_meaning, prior_pattern = self.prior[pattern_id]
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(
                    {key: value for key, value in prior_pattern.items()
                     if key != "examples"},
                    {key: value for key, value in pattern.items()
                     if key != "examples"})
                self.assertEqual(prior_meaning["id"], meaning["id"])
                self.assertEqual(prior_meaning["glossesEn"],
                                 meaning["glossesEn"])
                self.assertEqual(prior_meaning["internalScope"],
                                 meaning["internalScope"])
                self.assertEqual(prior_lemma["canonicalLemma"],
                                 lemma["canonicalLemma"])

    def test_the_corpus_still_holds_forty_five_patterns(self):
        self.assertEqual(PATTERN_COUNT, len(self.current))
        self.assertEqual(PATTERN_COUNT, len(self.prior))


# ---------------------------------------------------------------------------
# 3.  The canonical implementation of the two rows
# ---------------------------------------------------------------------------

class CanonicalImplementationTests(Phase4FC2CTestCase):

    def test_the_corpus_holds_exactly_the_locked_replacements(self):
        for review_id, row in OVERRIDE.items():
            with self.subTest(review_id=review_id):
                example = example_of(self.corpus, review_id)
                self.assertIsNotNone(example, "exactly one example")
                self.assertEqual(row["finalPl"], example["pl"])
                self.assertEqual(row["finalEn"], example["en"])

    def test_the_collided_sentences_are_gone_from_the_corpus(self):
        blob = corpus_text()
        for review_id, row in OVERRIDE.items():
            with self.subTest(review_id=review_id):
                self.assertNotIn(row["priorPl"], blob)
                self.assertNotIn(row["priorEn"], blob)

    def test_both_rows_are_still_editorial_generated(self):
        for review_id in OVERRIDE:
            with self.subTest(review_id=review_id):
                origin = example_of(self.corpus, review_id)["origin"]
                self.assertEqual(
                    {"kind": "editorial-generated",
                     "generatorRef": GENERATION_ACTOR,
                     "adoptedAt": ADOPTED_AT},
                    origin)

    def test_the_generation_actor_is_unchanged_and_still_alone(self):
        actors = self.document["editorialActorRegistry"]
        self.assertEqual({GENERATION_ACTOR, REFERENCE_ACTOR}, set(actors))
        self.assertIs(False, actors[GENERATION_ACTOR]["human"])
        self.assertEqual(["example-generation"],
                         actors[GENERATION_ACTOR]["roles"])
        self.assertEqual("Priority 7 Phase 4F-C2",
                         actors[GENERATION_ACTOR]["namedInPhase"])
        self.assertEqual({}, self.document["authorRegistry"])

    def test_no_new_actor_was_named_for_this_phase(self):
        blob = CONTEXT_FILE.read_text(encoding="utf-8")
        self.assertNotIn("4F-C2C", blob)
        self.assertNotIn("4fc2c", blob)

    def test_identity_is_exactly_the_c2_identity(self):
        for review_id in OVERRIDE:
            with self.subTest(review_id=review_id):
                before = example_of(self.c2, review_id)
                after = example_of(self.corpus, review_id)
                self.assertEqual(before["id"], after["id"])
                self.assertEqual(before["key"], after["key"])
                self.assertEqual(before["audioEligible"],
                                 after["audioEligible"])
                self.assertIs(False, after["audioEligible"])

    def test_both_ids_still_recompute_from_pattern_and_durable_key(self):
        for review_id in OVERRIDE:
            with self.subTest(review_id=review_id):
                pattern_id = self.c1c[review_id]["patternId"]
                example = example_of(self.corpus, review_id)
                self.assertEqual(
                    T.allocate_example_id(pattern_id, example["key"]),
                    example["id"])

    def test_every_id_in_the_corpus_recomputes_and_is_unique(self):
        ids, pairs = [], []
        for _, _, pattern in C2.iter_patterns(self.corpus):
            for example in C2.examples_of(pattern):
                with self.subTest(example_id=example["id"]):
                    self.assertEqual(
                        T.allocate_example_id(pattern["id"], example["key"]),
                        example["id"])
                ids.append(example["id"])
                pairs.append((pattern["id"], example["key"]))
        self.assertEqual(EXAMPLE_COUNT, len(ids))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(pairs), len(set(pairs)))

    def test_no_id_was_retired_reused_or_tombstoned(self):
        before = {example["id"] for example in C2.all_examples(self.c2)}
        after = {example["id"] for example in C2.all_examples(self.corpus)}
        self.assertEqual(before, after)
        self.assertNotIn("tombstone", corpus_text())
        self.assertEqual([], self.document["allocationRegistry"].get(
            "retired", []))

    def test_the_corpus_holds_twenty_nine_examples_and_no_second_one(self):
        self.assertEqual(EXAMPLE_COUNT, len(C2.all_examples(self.corpus)))
        for _, _, pattern in C2.iter_patterns(self.corpus):
            with self.subTest(pattern_id=pattern["id"]):
                self.assertLessEqual(len(C2.examples_of(pattern)), 1)

    def test_no_example_was_created_or_removed(self):
        self.assertEqual(len(C2.all_examples(self.c2)),
                         len(C2.all_examples(self.corpus)))
        self.assertEqual(EXAMPLE_COUNT, len(C2.all_examples(self.c2)))

    def test_the_origin_split_is_unchanged(self):
        counts = collections.Counter(
            example["origin"]["kind"]
            for example in C2.all_examples(self.corpus))
        self.assertEqual({"repository-reuse": REPOSITORY_REUSE_COUNT,
                          "editorial-generated": EDITORIAL_GENERATED_COUNT},
                         dict(counts))

    def test_no_original_origin_was_introduced(self):
        self.assertNotIn('"original"', corpus_text())
        self.assertNotIn("authorRef", corpus_text())
        self.assertNotIn("authoredAt", corpus_text())

    def test_the_replacements_are_single_sentences(self):
        for review_id, row in OVERRIDE.items():
            with self.subTest(review_id=review_id):
                polish = row["finalPl"]
                self.assertEqual(1, sum(polish.count(mark)
                                        for mark in (".", "?", "!")))
                self.assertIn(polish[-1], ".?!")

    def test_the_replacements_still_realise_the_governed_case(self):
        """Surface evidence that each row still teaches its complement."""
        widziec = example_of(self.corpus, "P7-NR-033")
        for form in ("tę", "czerwoną", "torbę"):
            with self.subTest(form=form):
                self.assertIn(form, widziec["pl"])
        opiekowac = example_of(self.corpus, "P7-NR-043")
        for form in ("opiekuję się", "młodszą", "siostrą"):
            with self.subTest(form=form):
                self.assertIn(form, opiekowac["pl"])
        for preposition in (" o ", " za ", " od "):
            with self.subTest(preposition=preposition):
                self.assertNotIn(preposition, opiekowac["pl"])

    def test_the_two_rows_keep_their_adjudicated_complement(self):
        for review_id, case in (("P7-NR-033", "accusative"),
                                ("P7-NR-043", "instrumental")):
            with self.subTest(review_id=review_id):
                pattern = self.current[self.c1c[review_id]["patternId"]][2]
                self.assertEqual([{"type": "case", "case": case,
                                   "required": True, "role": "object"}],
                                 pattern["complements"])


# ---------------------------------------------------------------------------
# 4.  Governance
# ---------------------------------------------------------------------------

class GovernanceTests(Phase4FC2CTestCase):

    def currency(self, document):
        table = {}
        for lemma, meaning, pattern in C2.iter_patterns(document):
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

    def digests(self, document, stage):
        return {pattern["id"]: T.review_scope_digest(stage, lemma, meaning,
                                                     pattern)
                for lemma, meaning, pattern in C2.iter_patterns(document)}

    def test_all_forty_five_patterns_are_still_reference_verified(self):
        states = collections.Counter(
            pattern["reviewState"]
            for _, _, pattern in C2.iter_patterns(self.corpus))
        self.assertEqual({"reference-verified": REFERENCE_VERIFIED_COUNT},
                         dict(states))

    def test_the_tooling_derives_that_state_rather_than_trusting_it(self):
        derived = collections.Counter(
            currency.state for currency in self.currency(self.corpus).values())
        self.assertEqual({"reference-verified": REFERENCE_VERIFIED_COUNT},
                         dict(derived))

    def test_the_derived_currency_is_identical_to_the_c2_candidate(self):
        after, before = self.currency(self.corpus), self.currency(self.c2)
        self.assertEqual(set(before), set(after))
        for pattern_id in before:
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(before[pattern_id], after[pattern_id])

    def test_the_forty_seven_acceptances_are_untouched(self):
        for pattern_id, (_, _, pattern) in self.current.items():
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(self.prior[pattern_id][2]["reviewEvents"],
                                 pattern["reviewEvents"])
        accepts = sum(1 for _, _, pattern in C2.iter_patterns(self.corpus)
                      for event in pattern["reviewEvents"]
                      if event["kind"] == "reference-verification"
                      and event["decision"] == "accept")
        self.assertEqual(REFERENCE_ACCEPT_COUNT, accepts)

    def test_no_review_event_of_any_other_kind_exists(self):
        kinds = collections.Counter(
            event["kind"] for _, _, pattern in C2.iter_patterns(self.corpus)
            for event in pattern["reviewEvents"])
        self.assertEqual({"reference-verification": REFERENCE_ACCEPT_COUNT},
                         dict(kinds))

    def test_no_editorial_review_or_product_approval_was_created(self):
        blob = corpus_text()
        for token in ("editorial-review", "product-approval",
                      "external-verification", "native-linguistic",
                      "correction", "reopen", "editorial-reviewed",
                      "approved"):
            with self.subTest(token=token):
                self.assertNotIn(f'"{token}"', blob)

    def test_tier_one_scope_digests_are_unchanged(self):
        for stage in TIER_ONE_STAGES:
            with self.subTest(stage=stage):
                self.assertEqual(self.digests(self.c2, stage),
                                 self.digests(self.corpus, stage))
                self.assertEqual(self.digests(self.baseline, stage),
                                 self.digests(self.corpus, stage))

    def test_higher_scope_values_moved_on_exactly_the_two_rows(self):
        expected = {self.c1c[review_id]["patternId"] for review_id in OVERRIDE}
        self.assertEqual(2, len(expected))
        for stage in HIGHER_SCOPE_STAGES:
            before, after = self.digests(self.c2, stage), self.digests(
                self.corpus, stage)
            with self.subTest(stage=stage):
                self.assertEqual(
                    expected,
                    {pattern_id for pattern_id in after
                     if before[pattern_id] != after[pattern_id]})

    def test_the_changed_row_set_against_the_baseline_is_still_c2s_eleven(self):
        expected = {row["patternId"] for row in self.c1c.values()
                    if row["implementationDisposition"] in {"REPLACE",
                                                            "CREATE"}}
        self.assertEqual(C2_IMPLEMENTED_ROW_COUNT, len(expected))
        for stage in HIGHER_SCOPE_STAGES:
            baseline, after = self.digests(self.baseline, stage), self.digests(
                self.corpus, stage)
            with self.subTest(stage=stage):
                self.assertEqual(
                    expected,
                    {pattern_id for pattern_id in after
                     if baseline[pattern_id] != after[pattern_id]})

    def test_no_recorded_event_digest_was_made_stale_or_healed(self):
        def superseded(document):
            return [(pattern["id"], index)
                    for lemma, meaning, pattern in C2.iter_patterns(document)
                    for index, event in enumerate(pattern["reviewEvents"])
                    if T.review_scope_digest(event["kind"], lemma, meaning,
                                             pattern) != event["scopeDigest"]]
        self.assertEqual(superseded(self.c2), superseded(self.corpus))

    def test_the_editorial_document_still_validates(self):
        issues = validate_editorial(self.corpus, C2.build_context())
        self.assertEqual([], [issue.code for issue in issues])


# ---------------------------------------------------------------------------
# 5.  Historical artifacts
# ---------------------------------------------------------------------------

class HistoricalArtifactTests(unittest.TestCase):

    def test_every_preserved_artifact_is_byte_identical(self):
        for path, digest in PRESERVED_ARTIFACTS.items():
            with self.subTest(path=path):
                self.assertEqual(digest, sha256_path(path))

    def test_the_c1c_matrix_still_holds_the_superseded_wording(self):
        rows = c1c_rows()
        self.assertEqual(13, len(rows))
        for review_id, row in OVERRIDE.items():
            with self.subTest(review_id=review_id):
                self.assertEqual(row["priorPl"], rows[review_id]["finalPolish"])
                self.assertEqual(row["priorEn"],
                                 rows[review_id]["finalEnglish"])

    def test_the_c2_report_was_not_retro_edited(self):
        text = C2_SUMMARY.read_text(encoding="utf-8")
        self.assertIn("**Verdict: GO**", text)
        for row in OVERRIDE.values():
            with self.subTest(sentence=row["priorPl"]):
                self.assertIn(row["priorPl"], text)
                self.assertNotIn(row["finalPl"], text)

    def test_the_c2b_no_go_is_preserved_as_delivered(self):
        text = C2B_SUMMARY.read_text(encoding="utf-8")
        self.assertIn("**Verdict: NO-GO**", text)
        for review_id in OVERRIDE:
            with self.subTest(review_id=review_id):
                self.assertIn(review_id, text)
        for row in OVERRIDE.values():
            with self.subTest(sentence=row["finalPl"]):
                self.assertNotIn(row["finalPl"], text)


# ---------------------------------------------------------------------------
# 6.  Source and reference boundary
# ---------------------------------------------------------------------------

class SourceBoundaryTests(Phase4FC2CTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.index = C2.repository_index()

    def repository_haystack(self):
        def strings(value):
            if isinstance(value, str):
                yield value
            elif isinstance(value, dict):
                for item in value.values():
                    yield from strings(item)
            elif isinstance(value, list):
                for item in value:
                    yield from strings(item)
        return chr(10).join(
            text for entity in self.index.entities.values()
            for text in strings(entity.record))

    def test_neither_replacement_reuses_repository_or_baseline_text(self):
        haystack = self.repository_haystack()
        baseline_blob = json.dumps(self.baseline, ensure_ascii=False)
        for review_id, row in OVERRIDE.items():
            for field in ("finalPl", "finalEn"):
                with self.subTest(review_id=review_id, field=field):
                    self.assertNotIn(row[field], haystack)
                    self.assertNotIn(row[field], baseline_blob)

    def test_no_generated_sentence_anywhere_duplicates_shipped_content(self):
        haystack = self.repository_haystack()
        for example in C2.all_examples(self.corpus):
            if example["origin"]["kind"] != "editorial-generated":
                continue
            for field in ("pl", "en"):
                with self.subTest(example_id=example["id"], field=field):
                    self.assertNotIn(example[field], haystack)

    def test_neither_replacement_appears_in_any_shipped_data_file(self):
        for name in ("data-a1.js", "data-a2.js", "data-b1.js",
                     "data-grammar.js", "data-verbs.js", "data-scenarios.js",
                     "data-podcasts.js", "index.html"):
            text = (ROOT / name).read_text(encoding="utf-8")
            for review_id, row in OVERRIDE.items():
                with self.subTest(path=name, review_id=review_id):
                    self.assertNotIn(row["finalPl"], text)
                    self.assertNotIn(row["finalEn"], text)

    def test_no_generated_example_claims_a_repository_source(self):
        for example in C2.all_examples(self.corpus):
            if example["origin"]["kind"] != "editorial-generated":
                continue
            with self.subTest(example_id=example["id"]):
                self.assertNotIn("repositorySource", example["origin"])

    def test_every_reuse_source_still_resolves_byte_exactly(self):
        reuse = [example for example in C2.all_examples(self.corpus)
                 if example["origin"]["kind"] == "repository-reuse"]
        self.assertEqual(REPOSITORY_REUSE_COUNT, len(reuse))
        for example in reuse:
            with self.subTest(example_id=example["id"]):
                source = example["origin"]["repositorySource"]
                entity = self.index.get(source["id"])
                self.assertIsNotNone(entity, source["id"])
                self.assertEqual(source["kind"], entity.kind)
                self.assertEqual(example["pl"],
                                 entity.record[source["field"]])

    def test_no_reference_source_text_was_quoted_into_an_example(self):
        for token in ("wsjp.pl/haslo", "Skladnia", "Składnia", "Medak",
                      "Mędak", "Gramatyka dla praktyka"):
            for example in C2.all_examples(self.corpus):
                with self.subTest(token=token, example_id=example["id"]):
                    self.assertNotIn(token, example["pl"])
                    self.assertNotIn(token, example["en"])


# ---------------------------------------------------------------------------
# 7.  The historical normalizers still have teeth
# ---------------------------------------------------------------------------

class NormalizerControlTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.corpus = corpus()
        cls.baseline = baseline_corpus()
        cls.context = context_document()
        cls.modules = [importlib.import_module(name)
                       for name in HISTORICAL_MODULES]
        cls.rows = c1c_rows()

    def pattern(self, document, review_id):
        return patterns_by_id(document)[self.rows[review_id]["patternId"]][2]

    def assert_survives(self, mutated, label):
        for module in self.modules:
            with self.subTest(module=module.__name__, mutation=label):
                self.assertNotEqual(
                    self.baseline, module.without_phase_4fc2_examples(mutated))

    def test_the_exact_c2c_candidate_normalizes_to_the_checkpoint(self):
        for module in self.modules:
            with self.subTest(module=module.__name__):
                self.assertEqual(
                    self.baseline,
                    module.without_phase_4fc2_examples(self.corpus))

    def test_a_third_rows_wording_mutation_is_still_rejected(self):
        """The C2C override is two rows wide, not a wording gate."""
        for review_id in ("P7-NR-031", "P7-NR-011", "P7-NR-018",
                          "P7-NR-042"):
            self.assertNotIn(review_id, OVERRIDE)
            candidate = copy.deepcopy(self.corpus)
            self.pattern(candidate, review_id)["examples"][0]["pl"] = (
                "Nieautoryzowana zmiana zdania.")
            self.assert_survives(candidate, f"wording-{review_id}")

    def test_an_unapproved_wording_on_an_overridden_row_is_rejected(self):
        for review_id in OVERRIDE:
            candidate = copy.deepcopy(self.corpus)
            self.pattern(candidate, review_id)["examples"][0]["pl"] = (
                "Nieautoryzowana zmiana zdania.")
            self.assert_survives(candidate, f"wording-{review_id}")

            candidate = copy.deepcopy(self.corpus)
            self.pattern(candidate, review_id)["examples"][0]["en"] = (
                "An unauthorized replacement.")
            self.assert_survives(candidate, f"gloss-{review_id}")

    def test_reverting_to_the_collided_sentence_is_rejected(self):
        for review_id, row in OVERRIDE.items():
            candidate = copy.deepcopy(self.corpus)
            example = self.pattern(candidate, review_id)["examples"][0]
            example["pl"], example["en"] = row["priorPl"], row["priorEn"]
            self.assert_survives(candidate, f"collided-{review_id}")

    def test_identity_mutations_on_the_overridden_rows_survive(self):
        mutations = {
            "id": lambda example: example.__setitem__(
                "id", example["id"][:-1] + "0"),
            "key": lambda example: example.__setitem__(
                "key", "unauthorized-durable-key"),
            "audio": lambda example: example.__setitem__(
                "audioEligible", True),
        }
        for review_id in OVERRIDE:
            for label, mutate in mutations.items():
                candidate = copy.deepcopy(self.corpus)
                mutate(self.pattern(candidate, review_id)["examples"][0])
                self.assert_survives(candidate, f"{label}-{review_id}")

    def test_provenance_mutations_survive(self):
        mutations = {
            "generator": lambda origin: origin.__setitem__(
                "generatorRef", REFERENCE_ACTOR),
            "kind": lambda origin: origin.__setitem__(
                "kind", "repository-reuse"),
            "date": lambda origin: origin.__setitem__(
                "adoptedAt", "2026-08-15"),
            "extra": lambda origin: origin.__setitem__(
                "authorRef", "native-reviewer-001"),
        }
        for review_id in OVERRIDE:
            for label, mutate in mutations.items():
                candidate = copy.deepcopy(self.corpus)
                mutate(self.pattern(
                    candidate, review_id)["examples"][0]["origin"])
                self.assert_survives(candidate, f"{label}-{review_id}")

    def test_a_second_example_on_an_overridden_row_survives(self):
        for review_id in OVERRIDE:
            candidate = copy.deepcopy(self.corpus)
            examples = self.pattern(candidate, review_id)["examples"]
            extra = copy.deepcopy(examples[0])
            extra["key"] = "unauthorized-second-example"
            extra["id"] = "vp-e-unauthorized-second-example-000000000000"
            examples.append(extra)
            self.assert_survives(candidate, f"second-{review_id}")

    def test_actor_role_escalation_survives(self):
        candidate = copy.deepcopy(self.context)
        candidate["editorialActorRegistry"][GENERATION_ACTOR]["roles"].append(
            "editorial-review")
        for module in self.modules:
            with self.subTest(module=module.__name__):
                self.assertIn(
                    GENERATION_ACTOR,
                    module.without_phase_4fc2_actor(
                        candidate)["editorialActorRegistry"])

    def test_the_exact_actor_is_still_removed(self):
        expected = baseline_context()["editorialActorRegistry"]
        for module in self.modules:
            with self.subTest(module=module.__name__):
                self.assertEqual(
                    expected,
                    module.without_phase_4fc2_actor(
                        self.context)["editorialActorRegistry"])


def baseline_context():
    result = git("show", f"{BASELINE_COMMIT}:editorial/"
                         "priority-7-authoring-context.json")
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


class ValidatorControlTests(unittest.TestCase):

    def setUp(self):
        self.corpus = corpus()
        self.context = C2.build_context()

    def codes(self, candidate):
        return {issue.code
                for issue in validate_editorial(candidate, self.context)}

    def test_the_exact_c2c_candidate_is_valid(self):
        self.assertEqual(set(), self.codes(self.corpus))

    def test_a_reuse_wording_mutation_is_rejected(self):
        candidate = copy.deepcopy(self.corpus)
        for example in C2.all_examples(candidate):
            if example["origin"]["kind"] == "repository-reuse":
                example["pl"] = "Nieautoryzowana zmiana zdania."
                break
        self.assertIn("REPOSITORY_SOURCE_MISMATCH", self.codes(candidate))

    def test_meaning_complement_and_evidence_mutations_are_rejected(self):
        for label, mutate in (
            ("meaning", lambda document:
             document["lemmas"][0]["meanings"][0]["glossesEn"].__setitem__(
                 0, "unauthorized meaning")),
            ("complement", lambda document:
             next(C2.iter_patterns(document))[2]["complements"][0].__setitem__(
                 "case", "dative")),
            ("evidence", lambda document:
             next(C2.iter_patterns(document))[2]["evidence"][0].__setitem__(
                 "locator", "unauthorized locator")),
        ):
            candidate = copy.deepcopy(self.corpus)
            mutate(candidate)
            with self.subTest(mutation=label):
                self.assertIn("REVIEW_STATE_MISMATCH", self.codes(candidate))

    def test_a_review_event_mutation_is_rejected(self):
        candidate = copy.deepcopy(self.corpus)
        next(C2.iter_patterns(candidate))[2]["reviewEvents"][0]["decision"] = (
            "reject")
        codes = self.codes(candidate)
        self.assertIn("REVIEW_STATE_MISMATCH", codes)
        self.assertIn("REVIEW_SCOPE_FORBIDDEN", codes)


# ---------------------------------------------------------------------------
# 8.  The C2C artifacts
# ---------------------------------------------------------------------------

class ArtifactTests(unittest.TestCase):

    def setUp(self):
        self.summary = C2C_SUMMARY.read_text(encoding="utf-8")
        self.rows = c2c_rows()

    def test_the_matrix_has_exactly_the_two_rows_and_the_named_columns(self):
        self.assertEqual(2, len(self.rows))
        self.assertEqual(["P7-NR-033", "P7-NR-043"],
                         sorted(row["reviewId"] for row in self.rows))
        for row in self.rows:
            with self.subTest(review_id=row["reviewId"]):
                self.assertEqual(C2C_MATRIX_FIELDS, list(row))

    def test_the_matrix_agrees_with_the_implemented_override(self):
        for row in self.rows:
            expected = OVERRIDE[row["reviewId"]]
            with self.subTest(review_id=row["reviewId"]):
                self.assertEqual(expected["priorPl"], row["priorPolish"])
                self.assertEqual(expected["priorEn"], row["priorEnglish"])
                self.assertEqual(expected["finalPl"], row["finalPolish"])
                self.assertEqual(expected["finalEn"], row["finalEnglish"])
                self.assertEqual("editorial-generated", row["finalOrigin"])

    def test_every_matrix_cell_is_populated(self):
        for row in self.rows:
            for field in C2C_MATRIX_FIELDS:
                with self.subTest(review_id=row["reviewId"], field=field):
                    self.assertTrue(row[field].strip())

    def test_the_matrix_records_the_collision_and_the_identity_treatment(self):
        for row in self.rows:
            with self.subTest(review_id=row["reviewId"]):
                self.assertIn("COLLISION", row["collisionClass"].upper())
                self.assertIn("IDENTITY PRESERVED", row["identityHandling"])
                example_key = example_of(corpus(), row["reviewId"])["key"]
                self.assertIn(example_key, row["identityHandling"])

    def test_the_summary_states_the_verdict_and_pins_the_baseline(self):
        self.assertIn("**Verdict: GO**", self.summary)
        self.assertIn(BASELINE_COMMIT, self.summary)

    def test_the_summary_carries_both_prior_and_both_final_sentences(self):
        for review_id, row in OVERRIDE.items():
            for field in ("priorPl", "priorEn", "finalPl", "finalEn"):
                with self.subTest(review_id=review_id, field=field):
                    self.assertIn(row[field], self.summary)

    def flowed(self):
        """The summary as running prose: no markdown emphasis, no line wraps."""
        return re.sub(r"\s+", " ",
                      self.summary.lower().replace("*", "").replace("`", ""))

    def test_the_summary_records_the_process_based_interpretation(self):
        for phrase in ("describes process and provenance",
                       "best-effort",
                       "global uniqueness cannot reasonably be proved",
                       "does not assert",
                       "supersedes only the wording fields"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.flowed())

    def test_the_summary_does_not_accuse_anyone_of_copying(self):
        lowered = self.summary.lower()
        for phrase in ("plagiar", "copied from", "was copied"):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, lowered)

    def test_the_summary_records_the_counts_it_claims(self):
        for token in (str(EXAMPLE_COUNT), str(REFERENCE_ACCEPT_COUNT),
                      str(REFERENCE_VERIFIED_COUNT), GENERATION_ACTOR):
            with self.subTest(token=token):
                self.assertIn(token, self.summary)


# ---------------------------------------------------------------------------
# 9.  Workspace shape
# ---------------------------------------------------------------------------

class WorkspaceTests(unittest.TestCase):

    def test_the_baseline_is_the_commit_it_claims_to_be(self):
        self.assertEqual(
            BASELINE_TREE,
            git("rev-parse", f"{BASELINE_COMMIT}^{{tree}}").stdout.strip())

    def test_c2c_owns_exactly_its_three_nonshipping_artifacts(self):
        """Inspect only the artifacts belonging to this historical phase."""
        self.assertEqual(
            {"reports/priority-7-phase-4fc2c-provenance-adjudication.csv",
             "reports/priority-7-phase-4fc2c-summary.md",
             "tests/test_priority7_phase4fc2c.py"}, C2C_ARTIFACTS)
        for relative in C2C_ARTIFACTS:
            with self.subTest(relative=relative):
                self.assertTrue((ROOT / relative).is_file())
                self.assertTrue(relative.startswith(("reports/", "tests/")))

    def test_the_immutable_baseline_remains_in_repository_history(self):
        result = git("merge-base", "--is-ancestor", BASELINE_COMMIT, "HEAD")
        self.assertEqual(0, result.returncode)


if __name__ == "__main__":
    unittest.main()
