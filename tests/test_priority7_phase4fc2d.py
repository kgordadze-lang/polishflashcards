"""Final independent closure checks for Priority 7 Phase 4F-C2D.

This suite treats the delivered canonical corpus as read-only.  It independently
pins the C2C two-row override, reconstructs C2, checks the complete eleven-row
implementation against the immutable baseline, exercises every historical
normalizer with unauthorized mutations, and keeps the C2B NO-GO historical.
"""

from __future__ import annotations

import collections
import copy
import csv
import hashlib
import importlib
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import priority7_tooling as T
from priority7_tooling import validate_editorial

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
from tests import test_priority7_phase4fb3b as B3B
from tests import test_priority7_phase4fc2 as C2
from tests import test_priority7_phase4fc2b as C2B
from tests import test_priority7_phase4fc2c as C2C


ROOT = Path(__file__).resolve().parents[1]
CORPUS_FILE = ROOT / "editorial" / "verb-pattern-candidates.json"
CONTEXT_FILE = ROOT / "editorial" / "priority-7-authoring-context.json"
C1C_MATRIX = ROOT / "reports" / "phase-4fc1c" / "adjudication-matrix.csv"
C2C_MATRIX = (ROOT / "reports" /
              "priority-7-phase-4fc2c-provenance-adjudication.csv")
C2D_SUMMARY = ROOT / "reports" / "priority-7-phase-4fc2d-summary.md"

BASELINE_COMMIT = "080d92ad49a514332f21ecd90b4a11de070a243f"
BASELINE_TREE = "74dd8cbebc303b646e4e38e2082d25c91b1cf6e1"
B3B_BASELINE = "7beb50d7b3463d7745352f1608f1e30019529fdf"

GENERATION_ACTOR = "priority7-example-generation"
REFERENCE_ACTOR = "priority7-reference-analysis"

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

# Independent expected values: these are not derived from the implementation
# matrix or from C2/C2C constants, so a joint matrix/implementation edit cannot
# make the closure check agree with itself.
FINAL_ELEVEN = {
    "P7-NR-011": ("Dziękuję siostrze za kolację.",
                  "I thank my sister for dinner."),
    "P7-NR-012": ("Płacę za kawę i gazetę.",
                  "I am paying for a coffee and a newspaper."),
    "P7-NR-018": ("Codziennie dbam o kondycję.",
                  "I look after my fitness every day."),
    "P7-NR-031": ("Zawsze pytam o cenę.",
                  "I always ask about the price."),
    "P7-NR-032": ("Pytam koleżankę o nową restaurację.",
                  "I am asking my friend about the new restaurant."),
    "P7-NR-033": ("Czy widzisz tę czerwoną torbę?",
                  "Do you see that red bag?"),
    "P7-NR-035": ("Ciągle myślę o egzaminie.",
                  "I keep thinking about the exam."),
    "P7-NR-036": ("W końcu znalazłam nową pracę.",
                  "I finally found a new job."),
    "P7-NR-042": ("Kiedy siostra jest w pracy, zajmuję się jej córką.",
                  "When my sister is at work, I look after her daughter."),
    "P7-NR-043": ("Dziś opiekuję się młodszą siostrą.",
                  "Today I'm looking after my younger sister."),
    "P7-NR-044": ("Nasze plany zależą od pogody.",
                  "Our plans depend on the weather."),
}

REPLACEMENTS = {
    "P7-NR-011", "P7-NR-012", "P7-NR-018", "P7-NR-033", "P7-NR-036"
}
CREATES = {
    "P7-NR-031", "P7-NR-032", "P7-NR-035",
    "P7-NR-042", "P7-NR-043", "P7-NR-044",
}

PRESERVED_REPORTS = {
    "reports/phase-4fc1/summary.md":
        "45ad110a3e2bcbd9c4c8f8881824b219ccbe0e0c293bcd364ee1877021599d7f",
    "reports/phase-4fc1b/summary.md":
        "645a4252eb911f802ead3f8ce3d3afe265970d7c49befbc83da6c83e659cdb9f",
    "reports/phase-4fc1c/summary.md":
        "21fe7541a784768dbeaf45f226af27835778a6830120b36f27e3b9b097405d64",
    "reports/priority-7-phase-4fc2-summary.md":
        "e12768828935c67d138ae77717bef0e68de10fe2c02047e8bbc2e5e332ed38d9",
    "reports/priority-7-phase-4fc2b-summary.md":
        "09995264798fe6402355ee16390ace9e7e6f3808b0a980489bfd1e7b3f778329",
    "reports/priority-7-phase-4fc2c-summary.md":
        "c9ce3d76e4ac7ee6ad00e100d30fbdc8a0c16a1e33c919a94013377bd2f12ab2",
    "reports/priority-7-phase-4fc2c-provenance-adjudication.csv":
        "ea5aa2638c272542a05b17a395e471c1c0a6046ebbcace8e6a73d191c83f160d",
}

C2D_ARTIFACTS = {
    "reports/priority-7-phase-4fc2d-summary.md",
    "tests/test_priority7_phase4fc2d.py",
}

#: Phase 4F-E1 repaired the historical suites to revert its own approved
#: governance work, and they now import its normaliser; Phase 4F-F2, Phase
#: 4F-H2, Phase 4F-H2.1, Phase 4F-H3 and Phase 4F-I1 each did the same for
#: theirs -- H3's being the UI wording layer in ``index.html`` rather than a
#: corpus layer, and I1's being the atomic release bundle across the runtime
#: document, ``index.html`` and ``sw.js``.  None of them is part of the C2D
#: transition -- the footprint assertion below still pins exactly 27 paths --
#: but the reconstructed clone has to carry them for the copied suites to
#: import at all.  In that clone the shipping files sit at the C2D baseline,
#: so the I1 layer is uniformly ``absent`` there and normalises nothing.
REPAIRED_SUITE_DEPENDENCIES = {
    "tests/priority7_phase4fe1_normalizer.py",
    "tests/priority7_phase4ff2_normalizer.py",
    "tests/priority7_phase4fh2_normalizer.py",
    "tests/priority7_phase4fh21_normalizer.py",
    "tests/priority7_phase4fh3_normalizer.py",
    "tests/priority7_phase4fi1_normalizer.py",
}


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True, check=True)


def candidate_revision():
    """Return the committed C2D transition, or None while it is uncommitted.

    Once later commits exist, the candidate is still the first descendant of
    the immutable baseline.  This keeps the exact integration boundary stable
    without treating every later file in the live repository as part of C2D.
    """
    head = git("rev-parse", "HEAD").stdout.strip()
    if head == BASELINE_COMMIT:
        return None
    revisions = git(
        "rev-list", "--reverse", "--ancestry-path",
        f"{BASELINE_COMMIT}..HEAD").stdout.split()
    if not revisions:
        raise AssertionError("baseline is not an ancestor of HEAD")
    return revisions[0]


def candidate_footprint():
    """Exact C2D candidate paths, independent of later committed files."""
    revision = candidate_revision()
    if revision is None:
        return C2.touched_since_baseline()
    return set(git("diff", "--name-only", BASELINE_COMMIT, revision).
               stdout.split())


def load(path):
    """Read a JSON artifact, reverting later approved work newest-first.

    Only the corpus carries D3.1 corrections; the normaliser is a no-op
    on every other artifact, and refuses to fire on any wording it was
    not written against.

    Phase 4F-E1 is reverted BEFORE Phase 4F-D3.1, because its acceptances
    are bound to the post-D3.1 tier-2 digests.  Reverting the wording first
    would move those digests and leave the acceptances unrecognised.
    """
    document = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(document, dict) and "lemmas" in document:
        document = C2.without_phase_4fd31_corrections(
            E1.without_phase_4fe1_editorial_review(
                F2.without_phase_4ff2_product_approval(
                    H2.without_phase_4fh2_content_completion(
                        H21.without_phase_4fh21_product_reapproval(document)))))
    return document


def baseline_json(relative):
    return json.loads(git("show", f"{BASELINE_COMMIT}:{relative}").stdout)


def rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def c1c_by_id():
    return {row["reviewId"]: row for row in rows(C1C_MATRIX)}


def pattern(document, review_id):
    pattern_id = c1c_by_id()[review_id]["patternId"]
    return C2.patterns_by_id(document)[pattern_id][2]


def example(document, review_id):
    examples = C2.examples_of(pattern(document, review_id))
    if len(examples) != 1:
        raise AssertionError(f"{review_id}: expected one example")
    return examples[0]


def digests(document, stage):
    return {
        current["id"]: T.review_scope_digest(stage, lemma, meaning, current)
        for lemma, meaning, current in C2.iter_patterns(document)
    }


class ClosureCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Phase 4F-E1 recorded the 45 tier-2 acceptances after this phase
        # closed.  Every claim here is about the C2D candidate, so that
        # approved governance work is reverted; ``cls.live`` keeps the
        # unmodified documents for the checks that must hold regardless.
        cls.live = json.loads(CORPUS_FILE.read_text(encoding="utf-8"))
        cls.live_context = json.loads(
            CONTEXT_FILE.read_text(encoding="utf-8"))
        cls.current = load(CORPUS_FILE)
        cls.context = E1.without_phase_4fe1_actors(
            F2.without_phase_4ff2_reviewer(
                H2.without_phase_4fh2_context(
                    H21.without_phase_4fh21_context(load(CONTEXT_FILE)))))
        cls.baseline = baseline_json("editorial/verb-pattern-candidates.json")
        cls.baseline_context = baseline_json(
            "editorial/priority-7-authoring-context.json")
        cls.c2 = C2C.c2_candidate()
        cls.matrix = c1c_by_id()


class OverrideClosureTests(ClosureCase):

    def test_the_adjudication_artifact_is_exactly_two_closed_rows(self):
        adjudication = rows(C2C_MATRIX)
        self.assertEqual(["P7-NR-033", "P7-NR-043"],
                         [row["reviewId"] for row in adjudication])
        self.assertEqual(2, len(adjudication))
        for row in adjudication:
            expected = OVERRIDE[row["reviewId"]]
            self.assertEqual(expected["priorPl"], row["priorPolish"])
            self.assertEqual(expected["priorEn"], row["priorEnglish"])
            self.assertEqual(expected["finalPl"], row["finalPolish"])
            self.assertEqual(expected["finalEn"], row["finalEnglish"])
            self.assertEqual("editorial-generated", row["finalOrigin"])

    def test_all_eight_override_declarations_are_exact(self):
        declarations = [C2.PHASE_4FC2C_WORDING_OVERRIDE, C2C.OVERRIDE]
        declarations.extend(importlib.import_module(name).
                            PHASE_4FC2C_WORDING_OVERRIDE
                            for name in C2B.HISTORICAL_MODULES)
        self.assertEqual(8, len(declarations))
        for declaration in declarations:
            self.assertEqual(OVERRIDE, declaration)

    def test_relative_to_c2_only_four_text_values_changed(self):
        before = {item["id"]: item for item in C2.all_examples(self.c2)}
        changed = set()
        for item in C2.all_examples(self.current):
            prior = before[item["id"]]
            for field in sorted(set(item) | set(prior)):
                if item.get(field) != prior.get(field):
                    changed.add((item["id"], field))
        expected = {(example(self.current, review_id)["id"], field)
                    for review_id in OVERRIDE for field in ("pl", "en")}
        self.assertEqual(expected, changed)

    def test_authoring_context_is_byte_identical_to_c2(self):
        # Removing exactly the two blocks Phase 4F-E1 inserted -- its actor
        # records and its notice paragraph -- must reproduce the C2 candidate
        # byte for byte.  Any edit to either leaves the digest wrong.
        digest = hashlib.sha256(
            E1.without_phase_4fe1_context_text(
                F2.without_phase_4ff2_context_text(
                    H2.without_phase_4fh2_context_text(
                        H21.without_phase_4fh21_context_text(
                            CONTEXT_FILE.read_text(encoding="utf-8"))))
            ).encode("utf-8")
        ).hexdigest()
        self.assertEqual(C2C.C2_CANDIDATE_CONTEXT_SHA256, digest)

    def test_superseded_canonical_strings_are_gone_but_history_keeps_them(self):
        canonical = CORPUS_FILE.read_text(encoding="utf-8")
        history = "\n".join((ROOT / path).read_text(encoding="utf-8")
                            for path in PRESERVED_REPORTS)
        for values in OVERRIDE.values():
            self.assertNotIn(values["priorPl"], canonical)
            self.assertIn(values["priorPl"], history)


class FinalExampleTests(ClosureCase):

    def test_the_final_eleven_are_exact_and_editorial_generated(self):
        self.assertEqual(11, len(FINAL_ELEVEN))
        for review_id, (polish, english) in FINAL_ELEVEN.items():
            item = example(self.current, review_id)
            self.assertEqual((polish, english), (item["pl"], item["en"]))
            self.assertEqual(
                {"kind": "editorial-generated",
                 "generatorRef": GENERATION_ACTOR,
                 "adoptedAt": "2026-08-16"}, item["origin"])
            self.assertNotIn("repositorySource", item["origin"])

    def test_the_five_replacements_and_six_creates_have_correct_identity(self):
        baseline_examples = {item["id"]: item
                             for item in C2.all_examples(self.baseline)}
        for review_id in REPLACEMENTS:
            item = example(self.current, review_id)
            self.assertIn(item["id"], baseline_examples)
        for review_id in CREATES:
            item = example(self.current, review_id)
            self.assertNotIn(item["id"], baseline_examples)
        self.assertEqual(5, len(REPLACEMENTS))
        self.assertEqual(6, len(CREATES))

    def test_every_identity_recomputes_and_none_is_duplicated(self):
        ids, sibling_keys = [], []
        for _, _, current in C2.iter_patterns(self.current):
            for item in C2.examples_of(current):
                ids.append(item["id"])
                sibling_keys.append((current["id"], item["key"]))
                self.assertEqual(
                    T.allocate_example_id(current["id"], item["key"]),
                    item["id"])
        self.assertEqual(29, len(ids))
        self.assertEqual(29, len(set(ids)))
        self.assertEqual(29, len(set(sibling_keys)))
        self.assertEqual(0, sum(len(current.get("retiredExampleIds", []))
                                for _, _, current in
                                C2.iter_patterns(self.current)))

    def test_two_keep_rows_are_baseline_byte_identical(self):
        keep = [row for row in self.matrix.values()
                if row["implementationDisposition"] == "KEEP CURRENT"]
        self.assertEqual(2, len(keep))
        for row in keep:
            self.assertEqual(example(self.baseline, row["reviewId"]),
                             example(self.current, row["reviewId"]))

    def test_special_case_transparency_and_distinctness_survive(self):
        self.assertEqual("Czy widzisz tę czerwoną torbę?",
                         example(self.current, "P7-NR-033")["pl"])
        self.assertRegex(example(self.current, "P7-NR-033")["pl"],
                         r"\btę czerwoną torbę\b")
        self.assertEqual("Dziś opiekuję się młodszą siostrą.",
                         example(self.current, "P7-NR-043")["pl"])
        self.assertRegex(example(self.current, "P7-NR-043")["pl"],
                         r"\bmłodszą siostrą\b")
        self.assertEqual("Zawsze pytam o cenę.",
                         example(self.current, "P7-NR-031")["pl"])
        self.assertEqual("Pytam koleżankę o nową restaurację.",
                         example(self.current, "P7-NR-032")["pl"])
        self.assertNotIn("koleżankę",
                         example(self.current, "P7-NR-031")["pl"])

    def test_c2_case_corrections_and_single_sentence_row_survive(self):
        expected_forms = {
            "P7-NR-012": ("za kawę", "gazetę"),
            "P7-NR-018": ("o kondycję",),
            "P7-NR-036": ("nową pracę",),
        }
        for review_id, forms in expected_forms.items():
            polish = example(self.current, review_id)["pl"]
            for form in forms:
                self.assertIn(form, polish)
        polish = example(self.current, "P7-NR-044")["pl"]
        self.assertEqual("Nasze plany zależą od pogody.", polish)
        self.assertEqual(1, sum(polish.count(mark) for mark in ".?!"))


class CanonicalBoundaryTests(ClosureCase):

    def test_no_nonexample_pattern_or_meaning_field_changed(self):
        before = C2.patterns_by_id(self.baseline)
        after = C2.patterns_by_id(self.current)
        self.assertEqual(set(before), set(after))
        for pattern_id, (lemma, meaning, current) in after.items():
            old_lemma, old_meaning, old = before[pattern_id]
            self.assertEqual(
                {key: value for key, value in old_lemma.items()
                 if key != "meanings"},
                {key: value for key, value in lemma.items()
                 if key != "meanings"})
            self.assertEqual(
                {key: value for key, value in old_meaning.items()
                 if key != "patterns"},
                {key: value for key, value in meaning.items()
                 if key != "patterns"})
            self.assertEqual({k: v for k, v in old.items() if k != "examples"},
                             {k: v for k, v in current.items()
                              if k != "examples"})

    def test_baseline_to_final_changed_row_set_is_exactly_the_eleven(self):
        before = C2.patterns_by_id(self.baseline)
        after = C2.patterns_by_id(self.current)
        changed = {pattern_id for pattern_id in after
                   if before[pattern_id][2] != after[pattern_id][2]}
        expected = {self.matrix[review_id]["patternId"]
                    for review_id in FINAL_ELEVEN}
        self.assertEqual(expected, changed)

    def test_context_changed_only_for_notice_and_exact_generation_actor(self):
        changed = {key for key in self.context
                   if self.context[key] != self.baseline_context[key]}
        self.assertEqual({"contextNotice", "editorialActorRegistry"}, changed)
        actor_delta = (set(self.context["editorialActorRegistry"]) -
                       set(self.baseline_context["editorialActorRegistry"]))
        self.assertEqual({GENERATION_ACTOR}, actor_delta)
        self.assertEqual(
            self.baseline_context["editorialActorRegistry"][REFERENCE_ACTOR],
            self.context["editorialActorRegistry"][REFERENCE_ACTOR])

    def test_generation_actor_has_no_escalated_authority(self):
        actor = self.context["editorialActorRegistry"][GENERATION_ACTOR]
        self.assertIs(False, actor["human"])
        self.assertEqual("example-generation-workflow", actor["kind"])
        self.assertEqual(["example-generation"], actor["roles"])
        self.assertEqual({}, self.context["authorRegistry"])
        for forbidden in ("reference-verification", "editorial-review",
                          "product-approval"):
            self.assertNotIn(forbidden, actor["roles"])


class GovernanceTests(ClosureCase):

    def test_counts_and_validation_are_exact(self):
        states = collections.Counter(current["reviewState"]
                                     for _, _, current in
                                     C2.iter_patterns(self.current))
        events = [event for _, _, current in C2.iter_patterns(self.current)
                  for event in current["reviewEvents"]]
        self.assertEqual({"reference-verified": 45}, dict(states))
        self.assertEqual(47, len(events))
        self.assertEqual({"reference-verification"},
                         {event["kind"] for event in events})
        self.assertEqual({"accept"}, {event["decision"] for event in events})
        self.assertEqual([], validate_editorial(self.current,
                                                C2.build_context()))

    def test_tier_one_is_baseline_identical_and_higher_scope_is_exact(self):
        for stage in ("reference-verification", "external-verification"):
            self.assertEqual(digests(self.baseline, stage),
                             digests(self.current, stage))
        eleven = {self.matrix[review_id]["patternId"]
                  for review_id in FINAL_ELEVEN}
        two = {self.matrix[review_id]["patternId"] for review_id in OVERRIDE}
        for stage in ("editorial-review", "native-linguistic",
                      "product-approval"):
            base, c2, final = (digests(document, stage) for document in
                               (self.baseline, self.c2, self.current))
            self.assertEqual(eleven, {key for key in final
                                      if base[key] != final[key]})
            self.assertEqual(two, {key for key in final
                                   if c2[key] != final[key]})


class HistoryAndGuardTests(ClosureCase):

    def test_historical_reports_are_byte_identical_and_c2b_stays_no_go(self):
        for relative, expected in PRESERVED_REPORTS.items():
            digest = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(expected, digest, relative)
        c2b = (ROOT / "reports/priority-7-phase-4fc2b-summary.md").read_text(
            encoding="utf-8")
        self.assertIn("**Verdict: NO-GO**", c2b)
        self.assertNotIn("**Verdict: GO**", c2b)

    def test_b3b_transition_and_footprint_remain_immutable(self):
        self.assertEqual(B3B_BASELINE, B3B.BASELINE_COMMIT)
        self.assertEqual(BASELINE_COMMIT, B3B.B3B_CHECKPOINT)
        self.assertEqual(11, len(B3B.B3B_FOOTPRINT))
        self.assertEqual(B3B.B3B_FOOTPRINT,
                         B3B.transition_footprint(
                             ROOT, B3B_BASELINE, BASELINE_COMMIT))

    def test_all_six_normalizers_accept_exact_candidate(self):
        for module_name in C2B.HISTORICAL_MODULES:
            module = importlib.import_module(module_name)
            self.assertEqual(self.baseline,
                             module.without_phase_4fc2_examples(self.current))
            normalized = module.without_phase_4fc2_actor(self.context)
            self.assertEqual(
                self.baseline_context["editorialActorRegistry"],
                normalized["editorialActorRegistry"])
            for key in self.baseline_context:
                if key in {"contextNotice", "editorialActorRegistry"}:
                    continue
                self.assertEqual(self.baseline_context[key], normalized[key])

    def assert_corpus_mutation_survives(self, candidate):
        for module_name in C2B.HISTORICAL_MODULES:
            module = importlib.import_module(module_name)
            self.assertNotEqual(
                self.baseline, module.without_phase_4fc2_examples(candidate),
                module_name)

    def test_required_corpus_mutation_controls_are_caught(self):
        mutations = []
        candidate = copy.deepcopy(self.current)
        example(candidate, "P7-NR-031")["pl"] = "Nieautoryzowana zmiana."
        mutations.append(candidate)
        candidate = copy.deepcopy(self.current)
        example(candidate, "P7-NR-033")["key"] = "unauthorized-key"
        mutations.append(candidate)
        candidate = copy.deepcopy(self.current)
        example(candidate, "P7-NR-043")["origin"]["generatorRef"] = (
            REFERENCE_ACTOR)
        mutations.append(candidate)
        candidate = copy.deepcopy(self.current)
        candidate["lemmas"][0]["meanings"][0]["glossesEn"][0] += " changed"
        mutations.append(candidate)
        candidate = copy.deepcopy(self.current)
        next(C2.iter_patterns(candidate))[2]["complements"][0]["case"] = (
            "dative")
        mutations.append(candidate)
        candidate = copy.deepcopy(self.current)
        next(C2.iter_patterns(candidate))[2]["evidence"][0]["locator"] += "#x"
        mutations.append(candidate)
        candidate = copy.deepcopy(self.current)
        next(C2.iter_patterns(candidate))[2]["reviewEvents"][0]["decision"] = (
            "reject")
        mutations.append(candidate)
        for candidate in mutations:
            self.assert_corpus_mutation_survives(candidate)

    def test_actor_role_escalation_survives_every_normalizer(self):
        candidate = copy.deepcopy(self.context)
        candidate["editorialActorRegistry"][GENERATION_ACTOR]["roles"].append(
            "editorial-review")
        for module_name in C2B.HISTORICAL_MODULES:
            module = importlib.import_module(module_name)
            normalized = module.without_phase_4fc2_actor(candidate)
            self.assertIn(GENERATION_ACTOR,
                          normalized["editorialActorRegistry"])


class TestAuditAndWorkspaceTests(unittest.TestCase):

    def test_c2c_is_not_a_head_self_comparison_or_global_uniqueness_claim(self):
        source = (ROOT / "tests/test_priority7_phase4fc2c.py").read_text(
            encoding="utf-8")
        self.assertNotRegex(source, r"git\(\s*[\"']show[\"']\s*,\s*[\"']HEAD")
        summary = (ROOT / "reports/priority-7-phase-4fc2c-summary.md").read_text(
            encoding="utf-8").lower()
        flowed = re.sub(r"\s+", " ", summary)
        self.assertIn("global uniqueness cannot reasonably be proved", flowed)
        self.assertIn("best-effort", flowed)
        self.assertIn("non-blocking", flowed)

    def test_c2b_and_c2c_do_not_name_their_successor(self):
        for relative in ("tests/test_priority7_phase4fc2b.py",
                         "tests/test_priority7_phase4fc2c.py"):
            source = (ROOT / relative).read_text(encoding="utf-8").lower()
            with self.subTest(relative=relative):
                for token in ("c2d", "phase-4fc2d",
                              "priority-7-phase-4fc2d",
                              "test_priority7_phase4fc2d"):
                    self.assertNotIn(token, source)

    def test_candidate_stage_transition_has_exactly_twenty_seven_paths(self):
        self.assertEqual(BASELINE_TREE,
                         git("rev-parse", f"{BASELINE_COMMIT}^{{tree}}").
                         stdout.strip())
        self.assertEqual("", git("remote").stdout)
        expected = (C2B.ORIGINAL_CANDIDATE_FOOTPRINT | C2B.C2B_ARTIFACTS |
                    C2C.C2C_ARTIFACTS | C2D_ARTIFACTS)
        self.assertEqual(expected, candidate_footprint())
        self.assertEqual(27, len(candidate_footprint()))

    def test_candidate_transition_is_baseline_child_when_committed(self):
        revision = candidate_revision()
        if revision is None:
            self.assertEqual(BASELINE_COMMIT,
                             git("rev-parse", "HEAD").stdout.strip())
            self.assertTrue(git("status", "--porcelain", "-uall").stdout)
        else:
            self.assertEqual(
                BASELINE_COMMIT,
                git("rev-parse", f"{revision}^").stdout.strip())


class HistoricalFutureArtifactRegressionTests(unittest.TestCase):
    """Later committed files must not change C2B/C2C's historical answer."""

    HISTORICAL_SUITES = (
        "tests.test_priority7_phase4fc2b",
        "tests.test_priority7_phase4fc2c",
    )

    def run_historical_suites(self, repository):
        result = subprocess.run(
            ["python3", "-m", "unittest", "-q", *self.HISTORICAL_SUITES],
            cwd=repository, capture_output=True, text=True)
        self.assertEqual(0, result.returncode,
                         result.stdout + result.stderr)

    def commit(self, repository, message):
        subprocess.run(["git", "add", "-A"], cwd=repository, check=True,
                       capture_output=True, text=True)
        subprocess.run(
            ["git", "-c", "user.name=C2D historical regression",
             "-c", "user.email=c2d-regression@example.invalid",
             "commit", "-q", "-m", message], cwd=repository, check=True,
            capture_output=True, text=True)

    def test_committed_later_report_and_test_both_pass_historical_suites(self):
        expected = (C2B.ORIGINAL_CANDIDATE_FOOTPRINT | C2B.C2B_ARTIFACTS |
                    C2C.C2C_ARTIFACTS | C2D_ARTIFACTS |
                    REPAIRED_SUITE_DEPENDENCIES)
        with tempfile.TemporaryDirectory(prefix="priority7-c2d-future-") as tmp:
            repository = Path(tmp) / "repository"
            subprocess.run(
                ["git", "clone", "-q", "--no-hardlinks", str(ROOT),
                 str(repository)], check=True, capture_output=True, text=True)
            subprocess.run(["git", "remote", "remove", "origin"],
                           cwd=repository, check=True, capture_output=True,
                           text=True)
            subprocess.run(["git", "checkout", "-q", "--detach",
                            BASELINE_COMMIT], cwd=repository, check=True,
                           capture_output=True, text=True)
            for relative in expected:
                source, destination = ROOT / relative, repository / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
            self.commit(repository, "complete C2D candidate")
            self.run_historical_suites(repository)

            later_report = (repository / "reports" /
                            "hypothetical-later-priority7-phase.md")
            later_report.write_text("Harmless later report.\n",
                                    encoding="utf-8")
            self.commit(repository, "hypothetical later report")
            self.run_historical_suites(repository)

            later_test = (repository / "tests" /
                          "test_priority7_hypothetical_later_phase.py")
            later_test.write_text(
                "import unittest\n\n"
                "class LaterPhaseTest(unittest.TestCase):\n"
                "    def test_harmless(self):\n"
                "        self.assertTrue(True)\n",
                encoding="utf-8")
            self.commit(repository, "hypothetical later test")
            self.run_historical_suites(repository)


class SummaryTests(unittest.TestCase):

    def test_summary_records_the_contained_repairs_and_verdict(self):
        text = C2D_SUMMARY.read_text(encoding="utf-8")
        self.assertIn("**Original C2D verdict: GO WITH CHANGES REQUIRED**",
                      text)
        self.assertIn("**Final verdict: GO**", text)
        for path in ("tests/test_priority7_phase4fc2b.py",
                     "tests/test_priority7_phase4fc2c.py"):
            self.assertIn(path, text)
        self.assertIn("36", text)
        self.assertIn("C2D", text)


if __name__ == "__main__":
    unittest.main()
