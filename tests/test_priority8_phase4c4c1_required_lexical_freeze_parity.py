"""Regression tests for frozen runtime requiredLexicalItems parity."""

from __future__ import annotations

import copy
import unittest

import priority7_tooling as tooling
from tests.test_priority7_phase2a import (
    fictional_editorial,
    parts,
    refresh_acceptance,
    validation_context,
)


def freeze_fixture(required_lexical_items=None):
    """Freeze one valid synthetic pattern with an optional structural field."""
    document = fictional_editorial()
    document["formatVersion"] = 2
    pattern = parts(document)[2]
    if required_lexical_items is not None:
        pattern["requiredLexicalItems"] = required_lexical_items
    refresh_acceptance(document)
    context = validation_context()
    frozen = tooling.freeze_editorial(document, 1, context)
    identity = {row["id"]: row for row in frozen["identity"]}
    structure = {row["id"]: row for row in frozen["structure"]}
    wording = {row["id"]: row for row in frozen["wording"]}
    policy = {row["id"]: row for row in frozen["policy"]}
    reconstructed = tooling._derive_runtime_from_frozen(
        1, identity, structure, wording, policy)
    return document, frozen, reconstructed


def runtime_pattern(runtime):
    return runtime["lemmas"][0]["meanings"][0]["patterns"][0]


def frozen_pattern_structure(frozen):
    return next(row for row in frozen["structure"] if row["kind"] == "pattern")


def reconstruct(frozen):
    return tooling._derive_runtime_from_frozen(
        frozen["patternDataRevision"],
        {row["id"]: row for row in frozen["identity"]},
        {row["id"]: row for row in frozen["structure"]},
        {row["id"]: row for row in frozen["wording"]},
        {row["id"]: row for row in frozen["policy"]},
    )


class RequiredLexicalItemsFrozenParityTests(unittest.TestCase):
    def test_single_and_multiple_ordered_items_round_trip_through_freeze(self):
        for items in (["udział"], ["jeden", "dwa"]):
            with self.subTest(items=items):
                document, frozen, reconstructed = freeze_fixture(items)
                normal = tooling.project_runtime_nonrelease(
                    document, 1, validation_context())
                self.assertEqual(normal, frozen["runtimeProjection"])
                self.assertEqual(normal, reconstructed)
                self.assertEqual(items, runtime_pattern(reconstructed)[
                    "requiredLexicalItems"])

    def test_absence_remains_absent(self):
        document, frozen, reconstructed = freeze_fixture()
        normal = tooling.project_runtime_nonrelease(
            document, 1, validation_context())
        self.assertEqual(normal, frozen["runtimeProjection"])
        self.assertEqual(normal, reconstructed)
        self.assertNotIn("requiredLexicalItems", runtime_pattern(reconstructed))

    def test_frozen_structural_tampering_remains_fail_closed(self):
        _document, frozen, _reconstructed = freeze_fixture(["udział"])
        for replacement in (["inny"], [], ["udział", "drugi"]):
            with self.subTest(replacement=replacement):
                tampered = copy.deepcopy(frozen)
                frozen_pattern_structure(tampered)["requiredLexicalItems"] = replacement
                codes = {issue.code for issue in tooling.validate_frozen_release(tampered)}
                self.assertIn("FROZEN_SCOPE_PARITY", codes)
                self.assertNotEqual(tampered["runtimeProjection"], reconstruct(tampered))

        removed = copy.deepcopy(frozen)
        del frozen_pattern_structure(removed)["requiredLexicalItems"]
        self.assertIn(
            "FROZEN_SCOPE_PARITY",
            {issue.code for issue in tooling.validate_frozen_release(removed)},
        )
        self.assertNotEqual(removed["runtimeProjection"], reconstruct(removed))

    def test_runtime_only_tampering_and_unknown_structure_field_are_rejected(self):
        _document, frozen, reconstructed = freeze_fixture(["udział"])
        dropped = copy.deepcopy(reconstructed)
        del runtime_pattern(dropped)["requiredLexicalItems"]
        self.assertNotEqual(frozen["runtimeProjection"], dropped)

        extra_runtime = copy.deepcopy(frozen)
        runtime_pattern(extra_runtime["runtimeProjection"])[
            "requiredLexicalItems"] = ["udział", "drugi"]
        self.assertIn(
            "FROZEN_RUNTIME_PARITY",
            {issue.code for issue in tooling.validate_frozen_release(extra_runtime)},
        )

        unknown_structure = copy.deepcopy(frozen)
        frozen_pattern_structure(unknown_structure)["unknownStructuralField"] = True
        self.assertIn(
            "SCHEMA_UNKNOWN_FIELD",
            {issue.code for issue in tooling.validate_frozen_release(unknown_structure)},
        )

    def test_reordered_frozen_items_are_not_normalized_away(self):
        _document, frozen, _reconstructed = freeze_fixture(["jeden", "dwa"])
        reordered = copy.deepcopy(frozen)
        frozen_pattern_structure(reordered)["requiredLexicalItems"] = [
            "dwa", "jeden"]
        self.assertIn(
            "FROZEN_SCOPE_PARITY",
            {issue.code for issue in tooling.validate_frozen_release(reordered)},
        )
        self.assertNotEqual(reordered["runtimeProjection"], reconstruct(reordered))


if __name__ == "__main__":
    unittest.main()
