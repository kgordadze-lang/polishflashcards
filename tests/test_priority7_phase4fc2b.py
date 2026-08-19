"""Independent closure guards for Priority 7 Phase 4F-C2B.

These tests do not re-adjudicate the locked sentences.  They prove that the
reviewed C2 candidate is exactly the locked implementation and, critically,
that the repaired historical normalizers remove only the exact approved C2
example and actor objects.  Unauthorized mutations must survive normalization
so the older committed-state comparisons can still reject them.

This review returned NO-GO on an external-source collision in P7-NR-043 and
P7-NR-033.  Phase 4F-C2C answered it by replacing exactly those two sentences.
Nothing below is re-stated as though C2 had been approved: the suite reaches
the approved-object comparison through C2C's closed two-row wording override,
and it now also proves that the override is two rows wide and no wider.
"""

from __future__ import annotations

import copy
import importlib
import json
import subprocess
import unittest
from pathlib import Path

from priority7_tooling import validate_editorial
from tests import test_priority7_phase4fc2 as C2


ROOT = Path(__file__).resolve().parents[1]
BASELINE_COMMIT = "080d92ad49a514332f21ecd90b4a11de070a243f"
BASELINE_TREE = "74dd8cbebc303b646e4e38e2082d25c91b1cf6e1"

HISTORICAL_MODULES = (
    "tests.test_priority7_phase4c",
    "tests.test_priority7_phase4e",
    "tests.test_priority7_phase4e1",
    "tests.test_priority7_phase4fa",
    "tests.test_priority7_phase4fb3b",
    "tests.test_priority7_phase5a",
)

ORIGINAL_CANDIDATE_FOOTPRINT = {
    "editorial/priority-7-authoring-context.json",
    "editorial/verb-pattern-candidates.json",
    "reports/phase-4fc1/blind-review-input.csv",
    "reports/phase-4fc1/example-matrix.csv",
    "reports/phase-4fc1/summary.md",
    "reports/phase-4fc1b/example-review-matrix.csv",
    "reports/phase-4fc1b/summary.md",
    "reports/phase-4fc1c/adjudication-matrix.csv",
    "reports/phase-4fc1c/summary.md",
    "reports/priority-7-phase-4fc2-summary.md",
    "tests/test_priority7_phase3d1.py",
    "tests/test_priority7_phase3fa.py",
    "tests/test_priority7_phase4c.py",
    "tests/test_priority7_phase4e.py",
    "tests/test_priority7_phase4e1.py",
    "tests/test_priority7_phase4fa.py",
    "tests/test_priority7_phase4fb3b.py",
    "tests/test_priority7_phase4fc1c.py",
    "tests/test_priority7_phase4fc2.py",
    "tests/test_priority7_phase5a.py",
}

C2B_ARTIFACTS = {
    "reports/priority-7-phase-4fc2b-summary.md",
    "tests/test_priority7_phase4fc2b.py",
}


def git(*arguments):
    return subprocess.run(
        ["git", *arguments], cwd=ROOT, capture_output=True, text=True,
        check=True)


def git_json(path):
    return json.loads(git("show", f"{BASELINE_COMMIT}:{path}").stdout)


def pattern(corpus, pattern_id):
    return C2.patterns_by_id(corpus)[pattern_id][2]


class CandidateReconstructionTests(unittest.TestCase):

    def test_the_baseline_is_the_independently_supplied_object(self):
        self.assertEqual(
            BASELINE_TREE,
            git("rev-parse", f"{BASELINE_COMMIT}^{{tree}}").stdout.strip())

    def test_the_arriving_candidate_was_exactly_twenty_files(self):
        self.assertEqual(20, len(ORIGINAL_CANDIDATE_FOOTPRINT))
        self.assertEqual(
            {
                "editorial/priority-7-authoring-context.json",
                "editorial/verb-pattern-candidates.json",
            },
            {path for path in ORIGINAL_CANDIDATE_FOOTPRINT
             if path.startswith("editorial/")})
        carried_reports = {
            path for path in ORIGINAL_CANDIDATE_FOOTPRINT
            if path.startswith("reports/phase-4fc1")}
        self.assertEqual(7, len(carried_reports))
        self.assertEqual(
            8, len(carried_reports | {"tests/test_priority7_phase4fc1c.py"}))
        self.assertEqual(
            8, len({path for path in ORIGINAL_CANDIDATE_FOOTPRINT
                    if path.startswith("tests/test_priority7_phase") and
                    path not in {
                        "tests/test_priority7_phase4fc1c.py",
                        "tests/test_priority7_phase4fc2.py",
                    }}))

    def test_c2b_owns_exactly_its_two_nonshipping_artifacts(self):
        """The historical claim is about C2B's files, not the live tree.

        Later phases may add arbitrary files without changing which artifacts
        C2B itself produced.  Canonical and protected-field boundaries are
        enforced independently by the reconstruction and mutation tests below.
        """
        self.assertEqual(
            {"reports/priority-7-phase-4fc2b-summary.md",
             "tests/test_priority7_phase4fc2b.py"}, C2B_ARTIFACTS)
        for relative in C2B_ARTIFACTS:
            with self.subTest(relative=relative):
                self.assertTrue((ROOT / relative).is_file())
                self.assertTrue(relative.startswith(("reports/", "tests/")))

    def test_the_immutable_baseline_remains_in_repository_history(self):
        result = git("merge-base", "--is-ancestor", BASELINE_COMMIT, "HEAD")
        self.assertEqual(0, result.returncode)


class ExactNormalizerTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.current = C2.load_corpus()
        cls.baseline = git_json("editorial/verb-pattern-candidates.json")
        cls.context = C2.load_context_document()
        cls.baseline_context = git_json(
            "editorial/priority-7-authoring-context.json")
        cls.modules = [importlib.import_module(name)
                       for name in HISTORICAL_MODULES]

    def assert_mutation_survives(self, mutated, label):
        for module in self.modules:
            with self.subTest(module=module.__name__, mutation=label):
                normalized = module.without_phase_4fc2_examples(mutated)
                self.assertNotEqual(self.baseline, normalized)

    def test_exact_legitimate_c2_examples_normalize_to_the_checkpoint(self):
        for module in self.modules:
            with self.subTest(module=module.__name__):
                self.assertEqual(
                    self.baseline,
                    module.without_phase_4fc2_examples(self.current))

    def test_created_example_identity_and_provenance_mutations_survive(self):
        pattern_id = C2.rows_by_id()["P7-NR-031"]["patternId"]
        mutations = {
            "id": lambda example: example.__setitem__(
                "id", example["id"][:-1] + "0"),
            "key": lambda example: example.__setitem__(
                "key", "unauthorized-durable-key"),
            "audio": lambda example: example.__setitem__(
                "audioEligible", True),
            "generator": lambda example: example["origin"].__setitem__(
                "generatorRef", C2.REFERENCE_ACTOR),
            "date": lambda example: example["origin"].__setitem__(
                "adoptedAt", "2026-08-15"),
            "extra-origin-field": lambda example: example["origin"].__setitem__(
                "authorRef", "native-reviewer-001"),
        }
        for label, mutate in mutations.items():
            candidate = copy.deepcopy(self.current)
            mutate(pattern(candidate, pattern_id)["examples"][0])
            self.assert_mutation_survives(candidate, label)

    def test_a_third_rows_wording_mutation_is_still_rejected(self):
        """The Phase 4F-C2C override is two rows, not a wording gate.

        C2C moved the wording of P7-NR-033 and P7-NR-043 only.  Every other
        implemented row must still be compared against the C1C matrix, so an
        unauthorized sentence anywhere else survives normalization and the
        older committed-state comparisons still see it.
        """
        for review_id in ("P7-NR-031", "P7-NR-011", "P7-NR-036",
                          "P7-NR-042"):
            candidate = copy.deepcopy(self.current)
            pattern_id = C2.rows_by_id()[review_id]["patternId"]
            pattern(candidate, pattern_id)["examples"][0]["pl"] = (
                "Nieautoryzowana zmiana zdania.")
            self.assert_mutation_survives(candidate, f"wording-{review_id}")

    def test_an_unapproved_wording_on_an_overridden_row_survives(self):
        """The override accepts its own two sentences, not any sentence."""
        for review_id in ("P7-NR-033", "P7-NR-043"):
            candidate = copy.deepcopy(self.current)
            pattern_id = C2.rows_by_id()[review_id]["patternId"]
            example = pattern(candidate, pattern_id)["examples"][0]
            example["pl"] = "Nieautoryzowana zmiana zdania."
            self.assert_mutation_survives(candidate, f"wording-{review_id}")

            candidate = copy.deepcopy(self.current)
            example = pattern(candidate, pattern_id)["examples"][0]
            example["en"] = "An unauthorized replacement."
            self.assert_mutation_survives(candidate, f"gloss-{review_id}")

    def test_replacement_identity_mutation_survives(self):
        pattern_id = C2.rows_by_id()["P7-NR-012"]["patternId"]
        candidate = copy.deepcopy(self.current)
        pattern(candidate, pattern_id)["examples"][0]["key"] = (
            "unauthorized-replacement-key")
        self.assert_mutation_survives(candidate, "replacement-key")

    def test_a_second_or_out_of_queue_example_survives(self):
        candidate = copy.deepcopy(self.current)
        pattern_id = C2.rows_by_id()["P7-NR-031"]["patternId"]
        examples = pattern(candidate, pattern_id)["examples"]
        extra = copy.deepcopy(examples[0])
        extra["key"] = "unauthorized-second-example"
        extra["id"] = "vp-e-unauthorized-second-example-000000000000"
        examples.append(extra)
        self.assert_mutation_survives(candidate, "second-example")

        candidate = copy.deepcopy(self.current)
        for _, _, current_pattern in C2.iter_patterns(candidate):
            if (current_pattern["id"] not in
                    {row["patternId"] for row in C2.read_matrix()}):
                current_pattern.setdefault("examples", []).append({
                    "id": "vp-e-unauthorized-outside-queue-000000000000",
                    "key": "unauthorized-outside-queue",
                    "pl": "To jest niedozwolony przykład.",
                    "en": "This is an unauthorized example.",
                    "audioEligible": False,
                    "origin": {
                        "kind": "editorial-generated",
                        "generatorRef": C2.GENERATION_ACTOR,
                        "adoptedAt": C2.ADOPTED_AT,
                    },
                })
                break
        self.assert_mutation_survives(candidate, "outside-queue-example")

    def test_protected_nonexample_mutations_survive(self):
        mutations = {}

        candidate = copy.deepcopy(self.current)
        candidate["lemmas"][0]["meanings"][0]["glossesEn"][0] += " changed"
        mutations["meaning"] = candidate

        candidate = copy.deepcopy(self.current)
        next(C2.iter_patterns(candidate))[2]["complements"][0]["case"] = (
            "dative")
        mutations["complement"] = candidate

        candidate = copy.deepcopy(self.current)
        next(C2.iter_patterns(candidate))[2]["evidence"][0]["locator"] += (
            "#unauthorized")
        mutations["evidence"] = candidate

        candidate = copy.deepcopy(self.current)
        next(C2.iter_patterns(candidate))[2]["reviewEvents"][0]["decision"] = (
            "reject")
        mutations["reference-event"] = candidate

        candidate = copy.deepcopy(self.current)
        for example in C2.all_examples(candidate):
            if example["origin"]["kind"] == "repository-reuse":
                example["pl"] = "Nieautoryzowana zmiana zdania."
                break
        mutations["outside-c1c-wording"] = candidate

        for label, candidate in mutations.items():
            self.assert_mutation_survives(candidate, label)

    def test_exact_actor_is_removed_but_any_actor_mutation_survives(self):
        for module in self.modules:
            with self.subTest(module=module.__name__, mutation="exact"):
                normalized = module.without_phase_4fc2_actor(self.context)
                self.assertEqual(
                    self.baseline_context["editorialActorRegistry"],
                    normalized["editorialActorRegistry"])

        actor_mutations = {
            "role-escalation": lambda record: record["roles"].append(
                "editorial-review"),
            "human-escalation": lambda record: record.__setitem__(
                "human", True),
            "kind": lambda record: record.__setitem__(
                "kind", "editorial-review-workflow"),
            "phase": lambda record: record.__setitem__(
                "namedInPhase", "Priority 7 Phase 4F-C2B"),
            "note": lambda record: record.__setitem__(
                "note", record["note"] + " Mutated."),
            "extra-field": lambda record: record.__setitem__(
                "reviewerRef", "native-reviewer-001"),
        }
        for label, mutate in actor_mutations.items():
            candidate = copy.deepcopy(self.context)
            mutate(candidate["editorialActorRegistry"][C2.GENERATION_ACTOR])
            for module in self.modules:
                with self.subTest(module=module.__name__, mutation=label):
                    normalized = module.without_phase_4fc2_actor(candidate)
                    self.assertIn(
                        C2.GENERATION_ACTOR,
                        normalized["editorialActorRegistry"])

    def test_an_extra_actor_survives(self):
        candidate = copy.deepcopy(self.context)
        candidate["editorialActorRegistry"]["unauthorized-extra-actor"] = {
            "human": False,
            "kind": "example-generation-workflow",
            "roles": ["example-generation"],
            "namedInPhase": "unauthorized",
            "note": "unauthorized",
        }
        for module in self.modules:
            with self.subTest(module=module.__name__):
                normalized = module.without_phase_4fc2_actor(candidate)
                self.assertIn(
                    "unauthorized-extra-actor",
                    normalized["editorialActorRegistry"])


class BehavioralNegativeControlTests(unittest.TestCase):

    def setUp(self):
        self.corpus = C2.load_corpus()
        self.context = C2.build_context()

    def codes(self, corpus):
        return {issue.code for issue in validate_editorial(corpus, self.context)}

    def test_validator_rejects_outside_queue_wording_mutation(self):
        candidate = copy.deepcopy(self.corpus)
        for example in C2.all_examples(candidate):
            if example["origin"]["kind"] == "repository-reuse":
                example["pl"] = "Nieautoryzowana zmiana zdania."
                break
        self.assertIn("REPOSITORY_SOURCE_MISMATCH", self.codes(candidate))

    def test_validator_rejects_meaning_complement_and_evidence_mutations(self):
        for label, mutate in (
            ("meaning", lambda corpus:
             corpus["lemmas"][0]["meanings"][0]["glossesEn"].__setitem__(
                 0, "unauthorized meaning")),
            ("complement", lambda corpus:
             next(C2.iter_patterns(corpus))[2]["complements"][0].__setitem__(
                 "case", "dative")),
            ("evidence", lambda corpus:
             next(C2.iter_patterns(corpus))[2]["evidence"][0].__setitem__(
                 "locator", "unauthorized locator")),
        ):
            candidate = copy.deepcopy(self.corpus)
            mutate(candidate)
            with self.subTest(mutation=label):
                self.assertIn("REVIEW_STATE_MISMATCH", self.codes(candidate))

    def test_validator_rejects_reference_event_mutation(self):
        candidate = copy.deepcopy(self.corpus)
        next(C2.iter_patterns(candidate))[2]["reviewEvents"][0]["decision"] = (
            "reject")
        codes = self.codes(candidate)
        self.assertIn("REVIEW_STATE_MISMATCH", codes)
        self.assertIn("REVIEW_SCOPE_FORBIDDEN", codes)

    def test_shipping_mutation_is_outside_the_c2_boundary(self):
        for path in ("priority7_tooling.py", "index.html", "sw.js"):
            with self.subTest(path=path):
                self.assertFalse(path.startswith(C2.C2_FOOTPRINT_PREFIXES))


if __name__ == "__main__":
    unittest.main()
