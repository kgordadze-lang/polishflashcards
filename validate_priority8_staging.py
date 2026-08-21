#!/usr/bin/env python3
"""Read-only validator for the private Priority 8 Phase 4B staging artifact."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent
STAGING_PATH = ROOT / "editorial/priority-8-phase4-staging.json"
FREEZE_CSV = ROOT / "reports/priority-8-phase-3b-final-lemma-freeze.csv"
HANDOFF_PATH = ROOT / "reports/priority-8-phase-3b-phase4-handoff.md"
POLICY_PATH = ROOT / "reports/priority-8-phase-4a2-2-policy-freeze.md"
CONTRACT_PATH = ROOT / "reports/priority-8-phase-4a2-2-staging-contract.md"

EXPECTED_HEAD = "2e90510f2a91bca2297781208bce3c94648e4427"
EXPECTED_TREE = "f86d876fce59f4042fa3bf9a306720914ed79b9d"
EXPECTED_STATUSES = ["draft", "independently-reviewed", "human-approved"]
METADATA_IDENTITIES = {"zaczynać", "przeczytać"}
EXPECTED_METADATA_PARTNERS = {
    "zacząć": {"canonicalLemma": "zaczynać", "aspect": "imperfective"},
    "czytać": {"canonicalLemma": "przeczytać", "aspect": "perfective"},
}
PRODUCTION_ID_FIELDS = {
    "lemmaid", "meaningid", "patternid", "exampleid", "exerciseid"
}
CANDIDATE_KEY_FIELDS = {
    "candidateMeaningKey", "candidatePatternKey", "candidateExampleKey"
}
PRODUCTION_ID_RE = re.compile(r"vp-[lmpex]-")
KEY_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

GLOBAL_CONSTRAINT_TEXTS = [
    "Preserve generalized-role versus concrete-realization discipline. "
    "`DOKĄD`, `SKĄD`, and `GDZIE` are not new architecture types or proof "
    "of exclusive preposition government.",
    "Build exact sense-specific schemas only.",
    "Keep alternative schemas alternative; never reconstruct an unsupported "
    "maximal frame.",
    "Preserve lexical `się` and `sobie` as part of the verified identity.",
    "Preserve required lexical `udział` in `brać udział w + Locative` and "
    "`wziąć udział w + Locative`.",
    "Keep aspect partners independently evidenced.",
    "Never transfer syntax through an aspect metadata relationship.",
    "Keep ordinary Genitive under negation grammar-owned rather than creating "
    "a lemma-specific lexical pattern.",
    "Preserve exact clause distinctions: `że`, `żeby`, "
    "interrogative-dependent, and direct speech.",
    "Keep related identities separate, including `radzić / radzić sobie`, "
    "`uczyć / uczyć się`, and reflexive/non-reflexive entries.",
    "Do not restore any rejected Phase 2 hypothesis during authoring.",
    "Allocate no stable ID until the exact Phase 4 editorial record is "
    "approved under the later ID policy.",
]


class FrozenInputError(RuntimeError):
    """Raised when the binding source reports no longer form the frozen intake."""


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_identity(path: Path) -> dict[str, str]:
    return {"path": _relative(path), "sha256": _sha256(path)}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _expected_sources() -> dict[str, dict[str, str]]:
    return {
        "phase3BFreezeCsv": _source_identity(FREEZE_CSV),
        "phase3BHandoff": _source_identity(HANDOFF_PATH),
        "phase4A2PolicyFreeze": _source_identity(POLICY_PATH),
        "phase4A2StagingContract": _source_identity(CONTRACT_PATH),
    }


def _expected_global_constraints() -> list[dict[str, Any]]:
    source_path = _relative(HANDOFF_PATH)
    return [
        {
            "constraintOrder": order,
            "text": text,
            "source": {
                "path": source_path,
                "section": "Global Phase 4 constraints",
                "item": order,
            },
        }
        for order, text in enumerate(GLOBAL_CONSTRAINT_TEXTS, 1)
    ]


def _phase3_rows() -> dict[int, tuple[str, dict[str, str]]]:
    records: dict[int, tuple[str, dict[str, str]]] = {}
    paths = sorted(ROOT.glob(
        "reports/priority-8-phase-3-batch-*-verification.csv"
    ))
    if len(paths) != 7:
        raise FrozenInputError(
            f"expected seven Phase 3 verification CSVs, found {len(paths)}"
        )
    for path in paths:
        for row in _read_csv(path):
            order = int(row["verification_order"])
            if order in records:
                raise FrozenInputError(
                    f"duplicate Phase 3 verification order {order}"
                )
            records[order] = (_relative(path), row)
    if sorted(records) != list(range(1, 71)):
        raise FrozenInputError("Phase 3 verification records are not orders 1-70")
    return records


def _expected_lemmas() -> list[dict[str, Any]]:
    freeze_rows = _read_csv(FREEZE_CSV)
    if len(freeze_rows) != 70:
        raise FrozenInputError(
            f"expected 70 frozen researched identities, found {len(freeze_rows)}"
        )
    metadata_rows = [
        row for row in freeze_rows if row["full_pattern_in_phase4"] == "no"
    ]
    if [(int(row["verification_order"]), row["lemma"])
            for row in metadata_rows] != [(17, "zaczynać"), (37, "przeczytać")]:
        raise FrozenInputError("metadata-only frozen identities changed")

    phase3 = _phase3_rows()
    expected: list[dict[str, Any]] = []
    for frozen in freeze_rows:
        if frozen["full_pattern_in_phase4"] != "yes":
            continue
        order = int(frozen["verification_order"])
        verification_csv, evidence = phase3[order]
        if evidence["lemma"] != frozen["lemma"]:
            raise FrozenInputError(
                f"freeze/evidence lemma mismatch at order {order}"
            )
        aspect = evidence["aspect"]
        if aspect not in {"imperfective", "perfective"}:
            raise FrozenInputError(
                f"invalid frozen aspect {aspect!r} at order {order}"
            )
        record: dict[str, Any] = {
            "verificationOrder": order,
            "canonicalLemma": frozen["lemma"],
            "aspect": aspect,
            "phase3Disposition": frozen["phase3_disposition"],
            "phase3Evidence": {
                "verificationCsv": verification_csv,
                "verificationOrder": order,
                "primarySourceKey": evidence["primary_source_key"],
                "primarySourceLocator": evidence["primary_source_locator"],
            },
            "bindingConstraints": [],
        }
        if frozen["phase3_representation_fit"] == "compatible with narrowing":
            if frozen["phase3_disposition"] == "KEEP WITH NARROWING":
                section = "Sixteen KEEP WITH NARROWING constraints"
            else:
                section = "Additional KEEP VERIFIED representation constraints"
            record["bindingConstraints"] = [{
                "text": frozen["authoring_constraint"],
                "source": {
                    "path": _relative(HANDOFF_PATH),
                    "section": section,
                    "verificationOrder": order,
                },
            }]
        expected.append(record)

    constrained = [item for item in expected if item["bindingConstraints"]]
    if len(expected) != 68 or len(constrained) != 21:
        raise FrozenInputError(
            "frozen intake must contain 68 full records and 21 constraints"
        )
    return expected


def _walk(value: Any, path: str = "$") -> Iterable[tuple[str, Any, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            yield key, child, child_path
            yield from _walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")


def _exact_keys(
    value: Any,
    expected: set[str],
    path: str,
    issues: list[str],
) -> bool:
    if not isinstance(value, dict):
        issues.append(f"{path} must be an object")
        return False
    actual = set(value)
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    if missing:
        issues.append(f"{path} missing fields: {', '.join(missing)}")
    if unexpected:
        issues.append(f"{path} has unexpected fields: {', '.join(unexpected)}")
    return not missing and not unexpected


def _check_recursive_prohibitions(data: Any, issues: list[str]) -> None:
    for key, value, path in _walk(data):
        if key.lower() in PRODUCTION_ID_FIELDS:
            issues.append(f"{path}: production-ID field name is prohibited")
        if isinstance(value, str) and PRODUCTION_ID_RE.search(value):
            issues.append(f"{path}: production vp-* ID prefix is prohibited")
        if key in CANDIDATE_KEY_FIELDS:
            if not isinstance(value, str) or not KEY_RE.fullmatch(value):
                issues.append(
                    f"{path}: candidate key must use lowercase kebab-case"
                )
            issues.append(f"{path}: candidate keys are prohibited in Phase 4B0")


def validate_data(data: Any) -> list[str]:
    """Return deterministic validation issues; an empty list means valid."""
    issues: list[str] = []
    top_fields = {
        "stagingSchemaVersion", "stagingRevision", "priority", "phase",
        "phaseStep", "frozenFullPatternCount", "sources",
        "startingIntegrationBaseline", "allowedReviewStatuses",
        "globalConstraints", "lemmas",
    }
    if not _exact_keys(data, top_fields, "$", issues):
        if not isinstance(data, dict):
            return issues

    expected_envelope = {
        "stagingSchemaVersion": 1,
        "stagingRevision": 1,
        "priority": 8,
        "phase": "4B",
        "phaseStep": "4B0",
        "frozenFullPatternCount": 68,
    }
    for key, expected in expected_envelope.items():
        if data.get(key) != expected:
            issues.append(f"$.{key} must equal {expected!r}")

    if data.get("sources") != _expected_sources():
        issues.append("$.sources does not match the frozen source identities")
    baseline = {"head": EXPECTED_HEAD, "tree": EXPECTED_TREE}
    if data.get("startingIntegrationBaseline") != baseline:
        issues.append("$.startingIntegrationBaseline does not match Phase 4B0")
    if data.get("allowedReviewStatuses") != EXPECTED_STATUSES:
        issues.append("$.allowedReviewStatuses does not match private vocabulary")
    if data.get("globalConstraints") != _expected_global_constraints():
        issues.append("$.globalConstraints does not match all 12 frozen constraints")

    lemmas = data.get("lemmas")
    if not isinstance(lemmas, list):
        issues.append("$.lemmas must be an array")
        _check_recursive_prohibitions(data, issues)
        return issues

    expected_records = _expected_lemmas()
    expected_sequence = [
        (record["verificationOrder"], record["canonicalLemma"])
        for record in expected_records
    ]
    actual_sequence = [
        (record.get("verificationOrder"), record.get("canonicalLemma"))
        if isinstance(record, dict) else (None, None)
        for record in lemmas
    ]
    if len(lemmas) != 68:
        issues.append(f"$.lemmas must contain exactly 68 records; found {len(lemmas)}")
    if actual_sequence != expected_sequence:
        issues.append("$.lemmas verification order/membership sequence is not frozen 68")

    actual_names = [
        record.get("canonicalLemma")
        for record in lemmas if isinstance(record, dict)
    ]
    duplicate_names = sorted({name for name in actual_names
                              if actual_names.count(name) > 1}, key=str)
    if duplicate_names:
        issues.append(
            "$.lemmas has duplicate canonicalLemma values: "
            + ", ".join(map(str, duplicate_names))
        )
    forbidden_full = sorted(METADATA_IDENTITIES.intersection(actual_names))
    if forbidden_full:
        issues.append(
            "metadata-only identities cannot be full-pattern records: "
            + ", ".join(forbidden_full)
        )

    expected_by_lemma = {
        record["canonicalLemma"]: record for record in expected_records
    }
    metadata_occurrences: list[tuple[Any, Any]] = []
    for index, record in enumerate(lemmas):
        path = f"$.lemmas[{index}]"
        if not isinstance(record, dict):
            issues.append(f"{path} must be an object")
            continue
        lemma = record.get("canonicalLemma")
        allowed_fields = {
            "verificationOrder", "canonicalLemma", "aspect",
            "phase3Disposition", "phase3Evidence", "bindingConstraints",
            "stagingReviewStatus", "candidateContent",
        }
        if lemma in EXPECTED_METADATA_PARTNERS:
            allowed_fields.add("metadataAspectPartner")
        if lemma in {"brać", "wziąć"}:
            allowed_fields.add("requiredLexicalItems")
        _exact_keys(record, allowed_fields, path, issues)

        expected = expected_by_lemma.get(lemma)
        if expected is not None:
            for field in (
                "verificationOrder", "canonicalLemma", "aspect",
                "phase3Disposition", "phase3Evidence", "bindingConstraints",
            ):
                if record.get(field) != expected[field]:
                    issues.append(
                        f"{path}.{field} does not match frozen Phase 3 source"
                    )
        if record.get("aspect") not in {"imperfective", "perfective"}:
            issues.append(f"{path}.aspect must be imperfective or perfective")

        status = record.get("stagingReviewStatus")
        if status not in EXPECTED_STATUSES:
            issues.append(f"{path}.stagingReviewStatus is not allowed")
        if status != "draft":
            issues.append(f"{path}.stagingReviewStatus must be draft in Phase 4B0")

        candidate = record.get("candidateContent")
        candidate_path = f"{path}.candidateContent"
        if _exact_keys(candidate, {"meanings", "patterns", "examples"},
                       candidate_path, issues):
            for collection in ("meanings", "patterns", "examples"):
                if candidate[collection] != []:
                    issues.append(
                        f"{candidate_path}.{collection} must be empty in Phase 4B0"
                    )

        if "metadataAspectPartner" in record:
            metadata_occurrences.append((lemma, record["metadataAspectPartner"]))
        expected_lexical = ["udział"] if lemma in {"brać", "wziąć"} else None
        if expected_lexical is not None:
            if record.get("requiredLexicalItems") != expected_lexical:
                issues.append(
                    f"{path}.requiredLexicalItems must equal ['udział']"
                )
        elif "requiredLexicalItems" in record:
            issues.append(
                f"{path}.requiredLexicalItems is allowed only on brać and wziąć"
            )

    expected_occurrences = list(EXPECTED_METADATA_PARTNERS.items())
    if metadata_occurrences != expected_occurrences:
        issues.append(
            "metadataAspectPartner occurrences must be exactly "
            "zacząć->zaczynać and czytać->przeczytać"
        )
    recursive_metadata_count = sum(
        1 for key, _, _ in _walk(data) if key == "metadataAspectPartner"
    )
    if recursive_metadata_count != 2:
        issues.append(
            "staging must contain exactly two metadataAspectPartner fields; "
            f"found {recursive_metadata_count}"
        )

    _check_recursive_prohibitions(data, issues)
    return issues


def load_staging(path: Path = STAGING_PATH) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_file(path: Path = STAGING_PATH) -> list[str]:
    return validate_data(load_staging(path))


def main() -> int:
    try:
        issues = validate_file()
    except (OSError, json.JSONDecodeError, FrozenInputError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    if issues:
        print(f"FAIL: {len(issues)} staging validation issue(s)", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1
    print(
        "PASS: Priority 8 Phase 4B0 staging is read-only valid "
        "(68 draft lemmas, 21 constrained records, 12 global constraints)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
