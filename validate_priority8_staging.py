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
PHASE_STEP_REVISIONS = {
    "4B0": 1,
    "4B1": 2,
    "4B2": 3,
    "4B3": 4,
    "4B4": 5,
    "4B5": 6,
    "4B6": 7,
    "4B7": 8,
}
AUTHORING_BATCHES = (
    (
        (1, "pracować"), (2, "iść"), (3, "chodzić"), (4, "jechać"),
        (5, "jeździć"), (6, "dojść"), (7, "dojechać"), (8, "wracać"),
        (9, "wrócić"), (10, "przyjść"),
    ),
    (
        (11, "przyjechać"), (12, "wyjść"), (13, "wyjechać"),
        (14, "przynosić"), (15, "odpowiadać"), (16, "zamawiać"),
        (18, "zacząć"), (19, "kończyć"), (20, "pamiętać"),
        (21, "zapominać"),
    ),
    (
        (22, "próbować"), (23, "pozwalać"), (24, "unikać"),
        (25, "wymagać"), (26, "należeć"), (27, "kłócić się"),
        (28, "pokazywać"), (29, "radzić sobie"), (30, "kupować"),
        (31, "kupić"),
    ),
    (
        (32, "dawać"), (33, "dać"), (34, "brać"), (35, "wziąć"),
        (36, "czytać"), (38, "pisać"), (39, "napisać"),
        (40, "spotykać się"), (41, "spotkać się"),
    ),
    (
        (42, "oglądać"), (43, "obejrzeć"), (44, "skończyć"),
        (45, "chcieć"), (46, "robić"), (47, "rozumieć"),
        (48, "mieszkać"), (49, "umówić się"), (50, "dzwonić"),
        (51, "powiedzieć"),
    ),
    (
        (52, "gotować"), (53, "rezerwować"), (54, "cieszyć się"),
        (55, "martwić się"), (56, "zgadzać się"), (57, "zapraszać"),
        (58, "polecać"), (59, "radzić"), (60, "pasować"), (61, "móc"),
    ),
    (
        (62, "musieć"), (63, "wiedzieć"), (64, "jeść"), (65, "pić"),
        (66, "kochać"), (67, "przepraszać"), (68, "życzyć"),
        (69, "korzystać"), (70, "uczyć"),
    ),
)
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
RELATION_TYPES = {
    "lexical-frame", "constructional-frame", "means-method",
    "subject-experiencer",
}
COMPLEMENT_TYPES = {"case", "preposition-case", "infinitive", "clause"}
DIRECT_CASE_IDS = {
    "nominative", "genitive", "dative", "accusative", "instrumental",
}
PREPOSITION_CASE_IDS = {
    "genitive", "dative", "accusative", "instrumental", "locative",
}
ROLES = {
    "subject", "object", "recipient", "experiencer", "predicate",
    "content", "topic", "interlocutor", "means", "target",
}
CLAUSE_KINDS = {"ze", "czy", "zeby", "interrogative", "direct-speech"}
CEFR_LEVELS = ("A1", "A2", "B1", "above-b1")
TEACHING_STATUSES = {"active-production", "recognition-only", "deferred"}
USAGE_PRIORITIES = {"core", "common", "limited"}
REGISTERS = {"neutral", "formal", "informal"}
PREPOSITION_RE = re.compile(r"^[a-ząćęłńóśźż]+$")
CANDIDATE_GOVERNANCE_FIELDS = {
    "reviewState", "reviewEvents", "reviewerRef", "reviewedAt", "actorRef",
    "corroboratingActorRefs", "authorRef", "authoredAt", "generatorRef",
    "adoptedAt", "releaseMode", "releaseAuthorization", "sourceRegistry",
    "reviewerRegistry", "authorRegistry", "editorialActorRegistry", "origin",
}
CANDIDATE_MEANING_FIELDS = {
    "candidateMeaningKey", "glossesEn", "internalScope",
}
CANDIDATE_PATTERN_FIELDS = {
    "candidatePatternKey", "meaningKeyRef", "relationType", "complements",
    "cefr", "teachingStatus", "usage", "learnerExplanationEn",
}
CANDIDATE_EXAMPLE_FIELDS = {
    "candidateExampleKey", "meaningKeyRef", "patternKeyRef", "pl", "en",
    "candidateOrigin",
}
CANDIDATE_ORIGIN_KINDS = {"editorial-generated", "repository-reuse"}
REPOSITORY_SOURCE_FIELDS = {
    "card": {"pl", "ex"},
    "drill": {"prompt", "answer"},
}

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


def _nonempty_string(
    value: Any,
    path: str,
    issues: list[str],
    *,
    minimum: int = 1,
) -> bool:
    if (not isinstance(value, str) or value != value.strip()
            or len(value) < minimum):
        issues.append(f"{path} must be a non-empty trimmed string")
        return False
    return True


def _enum(
    value: Any,
    allowed: set[str] | tuple[str, ...],
    path: str,
    issues: list[str],
) -> bool:
    if not isinstance(value, str) or value not in allowed:
        issues.append(
            f"{path} must be one of: {', '.join(sorted(allowed))}"
        )
        return False
    return True


def _candidate_key(value: Any, path: str, issues: list[str]) -> bool:
    if not isinstance(value, str) or not KEY_RE.fullmatch(value):
        issues.append(f"{path}: candidate key must use lowercase kebab-case")
        return False
    return True


def _string_list(
    value: Any,
    path: str,
    issues: list[str],
    *,
    minimum: int = 1,
    maximum: int | None = None,
) -> bool:
    if not isinstance(value, list):
        issues.append(f"{path} must be an array")
        return False
    if len(value) < minimum or (maximum is not None and len(value) > maximum):
        range_text = f"{minimum}"
        if maximum is not None:
            range_text += f"-{maximum}"
        issues.append(f"{path} must contain {range_text} item(s)")
        return False
    valid = True
    seen: set[str] = set()
    for index, item in enumerate(value):
        if not _nonempty_string(item, f"{path}[{index}]", issues):
            valid = False
        elif item in seen:
            issues.append(f"{path}[{index}] duplicates a sibling string")
            valid = False
        else:
            seen.add(item)
    return valid


def _check_recursive_prohibitions(
    data: Any,
    issues: list[str],
    *,
    allow_candidate_keys: bool = False,
) -> None:
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
            if not allow_candidate_keys:
                issues.append(
                    f"{path}: candidate keys are prohibited in Phase 4B0"
                )


def _check_candidate_prohibitions(
    candidate: Any,
    path: str,
    issues: list[str],
) -> None:
    for key, _, child_path in _walk(candidate, path):
        if key.lower() in PRODUCTION_ID_FIELDS:
            issues.append(
                f"{child_path}: production-ID field name is prohibited "
                "from candidate content"
            )
        if key in CANDIDATE_GOVERNANCE_FIELDS:
            issues.append(
                f"{child_path}: governance/reviewer identity field is "
                "prohibited from candidate content"
            )


def _validate_complement(
    value: Any,
    path: str,
    relation_type: Any,
    issues: list[str],
) -> None:
    required = {"type", "required", "role"}
    allowed = required | {
        "case", "preposition", "clauseKind", "questionOverridePl",
    }
    if not isinstance(value, dict):
        issues.append(f"{path} must be an object")
        return
    actual = set(value)
    missing = required - actual
    unexpected = actual - allowed
    if missing:
        issues.append(f"{path} missing fields: {', '.join(sorted(missing))}")
    if unexpected:
        issues.append(
            f"{path} has unexpected fields: {', '.join(sorted(unexpected))}"
        )

    complement_type = value.get("type")
    _enum(complement_type, COMPLEMENT_TYPES, f"{path}.type", issues)
    if type(value.get("required")) is not bool:
        issues.append(f"{path}.required must be a boolean")
    role = value.get("role")
    _enum(role, ROLES, f"{path}.role", issues)
    if "questionOverridePl" in value:
        _string_list(value["questionOverridePl"],
                     f"{path}.questionOverridePl", issues)

    required_by_type: set[str]
    forbidden_by_type: set[str]
    if complement_type == "case":
        required_by_type = {"case"}
        forbidden_by_type = {"preposition", "clauseKind"}
        case_id = value.get("case")
        _enum(case_id, DIRECT_CASE_IDS, f"{path}.case", issues)
        if case_id == "nominative":
            if relation_type not in {
                    "constructional-frame", "subject-experiencer"}:
                issues.append(
                    f"{path}: direct nominative requires a constructional "
                    "or subject-experiencer relation"
                )
            if role not in {"subject", "predicate"}:
                issues.append(
                    f"{path}.role: direct nominative role must be subject "
                    "or predicate"
                )
    elif complement_type == "preposition-case":
        required_by_type = {"preposition", "case"}
        forbidden_by_type = {"clauseKind"}
        preposition = value.get("preposition")
        if (not isinstance(preposition, str)
                or not PREPOSITION_RE.fullmatch(preposition)):
            issues.append(
                f"{path}.preposition must be one lowercase Polish word"
            )
        _enum(value.get("case"), PREPOSITION_CASE_IDS,
              f"{path}.case", issues)
    elif complement_type == "infinitive":
        required_by_type = set()
        forbidden_by_type = {"case", "preposition", "clauseKind"}
    elif complement_type == "clause":
        required_by_type = {"clauseKind"}
        forbidden_by_type = {"case", "preposition"}
        _enum(value.get("clauseKind"), CLAUSE_KINDS,
              f"{path}.clauseKind", issues)
    else:
        return
    for required_field in sorted(required_by_type):
        if required_field not in value:
            issues.append(
                f"{path}.{required_field} is required for {complement_type}"
            )
    for forbidden_field in sorted(forbidden_by_type):
        if forbidden_field in value:
            issues.append(
                f"{path}.{forbidden_field} is forbidden for {complement_type}"
            )


def _validate_cefr(
    value: Any,
    path: str,
    teaching_status: Any,
    issues: list[str],
) -> None:
    if not isinstance(value, dict):
        issues.append(f"{path} must be an object")
        return
    required = {"recognition"}
    allowed = {"recognition", "production"}
    missing = required - set(value)
    unexpected = set(value) - allowed
    if missing:
        issues.append(f"{path} missing fields: {', '.join(sorted(missing))}")
    if unexpected:
        issues.append(
            f"{path} has unexpected fields: {', '.join(sorted(unexpected))}"
        )
    recognition = value.get("recognition")
    _enum(recognition, CEFR_LEVELS, f"{path}.recognition", issues)
    production = value.get("production")
    if "production" in value:
        _enum(production, CEFR_LEVELS, f"{path}.production", issues)
        if recognition in CEFR_LEVELS and production in CEFR_LEVELS:
            if CEFR_LEVELS.index(production) < CEFR_LEVELS.index(recognition):
                issues.append(
                    f"{path}: production CEFR must not precede recognition"
                )
    if teaching_status == "active-production":
        if production not in {"A1", "A2", "B1"}:
            issues.append(
                f"{path}: active-production requires A1-B1 production CEFR"
            )
    elif teaching_status in {"recognition-only", "deferred"}:
        if "production" in value:
            issues.append(
                f"{path}.production is forbidden for {teaching_status}"
            )


def _validate_usage(
    value: Any,
    path: str,
    teaching_status: Any,
    issues: list[str],
) -> None:
    if not isinstance(value, dict):
        issues.append(f"{path} must be an object")
        return
    required = {"priority", "register"}
    allowed = required | {"note"}
    missing = required - set(value)
    unexpected = set(value) - allowed
    if missing:
        issues.append(f"{path} missing fields: {', '.join(sorted(missing))}")
    if unexpected:
        issues.append(
            f"{path} has unexpected fields: {', '.join(sorted(unexpected))}"
        )
    priority = value.get("priority")
    _enum(priority, USAGE_PRIORITIES, f"{path}.priority", issues)
    _enum(value.get("register"), REGISTERS, f"{path}.register", issues)
    if "note" in value:
        _nonempty_string(value["note"], f"{path}.note", issues)
    if priority == "limited":
        if "note" not in value:
            issues.append(f"{path}.note is required for limited usage")
        if teaching_status == "active-production":
            issues.append(
                f"{path}: limited usage cannot be active-production"
            )


def _validate_candidate_meaning(
    value: Any,
    path: str,
    issues: list[str],
) -> str | None:
    if not _exact_keys(value, CANDIDATE_MEANING_FIELDS, path, issues):
        if not isinstance(value, dict):
            return None
    key = value.get("candidateMeaningKey")
    key_ok = _candidate_key(key, f"{path}.candidateMeaningKey", issues)
    _string_list(value.get("glossesEn"), f"{path}.glossesEn", issues,
                 minimum=1, maximum=3)
    _nonempty_string(value.get("internalScope"),
                     f"{path}.internalScope", issues, minimum=3)
    return key if key_ok else None


def _validate_candidate_pattern(
    value: Any,
    path: str,
    issues: list[str],
) -> tuple[str | None, str | None]:
    if not _exact_keys(value, CANDIDATE_PATTERN_FIELDS, path, issues):
        if not isinstance(value, dict):
            return None, None
    key = value.get("candidatePatternKey")
    key_ok = _candidate_key(key, f"{path}.candidatePatternKey", issues)
    meaning_ref = value.get("meaningKeyRef")
    ref_ok = _candidate_key(meaning_ref, f"{path}.meaningKeyRef", issues)
    relation_type = value.get("relationType")
    _enum(relation_type, RELATION_TYPES, f"{path}.relationType", issues)

    complements = value.get("complements")
    if not isinstance(complements, list) or not complements:
        issues.append(f"{path}.complements must be a non-empty array")
    else:
        roles = []
        for index, complement in enumerate(complements):
            _validate_complement(
                complement, f"{path}.complements[{index}]", relation_type,
                issues,
            )
            if isinstance(complement, dict):
                roles.append(complement.get("role"))
        if relation_type == "means-method" and "means" not in roles:
            issues.append(
                f"{path}.complements: means-method requires role 'means'"
            )
        if relation_type == "subject-experiencer" and not (
                {"subject", "experiencer"} <= set(roles)):
            issues.append(
                f"{path}.complements: subject-experiencer requires subject "
                "and experiencer roles"
            )

    teaching_status = value.get("teachingStatus")
    _enum(teaching_status, TEACHING_STATUSES,
          f"{path}.teachingStatus", issues)
    _validate_cefr(value.get("cefr"), f"{path}.cefr",
                   teaching_status, issues)
    _validate_usage(value.get("usage"), f"{path}.usage",
                    teaching_status, issues)
    _nonempty_string(value.get("learnerExplanationEn"),
                     f"{path}.learnerExplanationEn", issues, minimum=3)
    return (meaning_ref if ref_ok else None, key if key_ok else None)


def _validate_candidate_example(
    value: Any,
    path: str,
    issues: list[str],
) -> tuple[str | None, str | None, str | None]:
    if not _exact_keys(value, CANDIDATE_EXAMPLE_FIELDS, path, issues):
        if not isinstance(value, dict):
            return None, None, None
    key = value.get("candidateExampleKey")
    key_ok = _candidate_key(key, f"{path}.candidateExampleKey", issues)
    meaning_ref = value.get("meaningKeyRef")
    meaning_ok = _candidate_key(
        meaning_ref, f"{path}.meaningKeyRef", issues)
    pattern_ref = value.get("patternKeyRef")
    pattern_ok = _candidate_key(
        pattern_ref, f"{path}.patternKeyRef", issues)
    _nonempty_string(value.get("pl"), f"{path}.pl", issues, minimum=3)
    _nonempty_string(value.get("en"), f"{path}.en", issues, minimum=3)
    _validate_candidate_origin(
        value.get("candidateOrigin"), f"{path}.candidateOrigin", issues)
    return (
        meaning_ref if meaning_ok else None,
        pattern_ref if pattern_ok else None,
        key if key_ok else None,
    )


def _validate_candidate_origin(
    value: Any,
    path: str,
    issues: list[str],
) -> None:
    if not isinstance(value, dict):
        issues.append(f"{path} must be an object")
        return
    kind = value.get("kind")
    if not _enum(kind, CANDIDATE_ORIGIN_KINDS, f"{path}.kind", issues):
        return
    if kind == "editorial-generated":
        _exact_keys(value, {"kind"}, path, issues)
        return

    if not _exact_keys(value, {"kind", "repositorySource"}, path, issues):
        if "repositorySource" not in value:
            return
    source = value.get("repositorySource")
    source_path = f"{path}.repositorySource"
    if not _exact_keys(source, {"kind", "id", "field"}, source_path, issues):
        if not isinstance(source, dict):
            return
    source_kind = source.get("kind")
    if not _enum(source_kind, set(REPOSITORY_SOURCE_FIELDS),
                 f"{source_path}.kind", issues):
        return
    _nonempty_string(source.get("id"), f"{source_path}.id", issues)
    _enum(source.get("field"), REPOSITORY_SOURCE_FIELDS[source_kind],
          f"{source_path}.field", issues)


def _validate_candidate_content(
    candidate: Any,
    path: str,
    issues: list[str],
) -> tuple[int, int, int]:
    if not _exact_keys(
            candidate, {"meanings", "patterns", "examples"}, path, issues):
        if not isinstance(candidate, dict):
            return 0, 0, 0
    _check_candidate_prohibitions(candidate, path, issues)

    collections: dict[str, list[Any]] = {}
    for name in ("meanings", "patterns", "examples"):
        value = candidate.get(name)
        if not isinstance(value, list):
            issues.append(f"{path}.{name} must be an array")
            collections[name] = []
        else:
            collections[name] = value

    meaning_keys: set[str] = set()
    for index, meaning in enumerate(collections["meanings"]):
        meaning_path = f"{path}.meanings[{index}]"
        key = _validate_candidate_meaning(meaning, meaning_path, issues)
        if key is not None:
            if key in meaning_keys:
                issues.append(
                    f"{meaning_path}.candidateMeaningKey: duplicate "
                    "candidateMeaningKey within lemma"
                )
            meaning_keys.add(key)

    pattern_owners: set[tuple[str, str]] = set()
    referenced_meanings: set[str] = set()
    for index, pattern in enumerate(collections["patterns"]):
        pattern_path = f"{path}.patterns[{index}]"
        meaning_ref, key = _validate_candidate_pattern(
            pattern, pattern_path, issues)
        if meaning_ref is not None and meaning_ref not in meaning_keys:
            issues.append(
                f"{pattern_path}.meaningKeyRef: unresolved meaningKeyRef "
                "within lemma"
            )
        if meaning_ref is not None and key is not None:
            referenced_meanings.add(meaning_ref)
            owner = (meaning_ref, key)
            if owner in pattern_owners:
                issues.append(
                    f"{pattern_path}.candidatePatternKey: duplicate "
                    "candidatePatternKey under meaningKeyRef"
                )
            pattern_owners.add(owner)
    for meaning_key in sorted(meaning_keys - referenced_meanings):
        issues.append(
            f"{path}.patterns: candidate meaning {meaning_key!r} requires "
            "at least one pattern"
        )

    example_owners: set[tuple[str, str, str]] = set()
    for index, example in enumerate(collections["examples"]):
        example_path = f"{path}.examples[{index}]"
        meaning_ref, pattern_ref, key = _validate_candidate_example(
            example, example_path, issues)
        if meaning_ref is not None and meaning_ref not in meaning_keys:
            issues.append(
                f"{example_path}.meaningKeyRef: unresolved meaningKeyRef "
                "within lemma"
            )
        if meaning_ref is not None and pattern_ref is not None:
            pattern_owner = (meaning_ref, pattern_ref)
            if pattern_owner not in pattern_owners:
                issues.append(
                    f"{example_path}.patternKeyRef: unresolved patternKeyRef "
                    "within lemma"
                )
            if key is not None:
                owner = (meaning_ref, pattern_ref, key)
                if owner in example_owners:
                    issues.append(
                        f"{example_path}.candidateExampleKey: duplicate "
                        "candidateExampleKey under patternKeyRef"
                    )
                example_owners.add(owner)

    return tuple(len(collections[name]) for name in (
        "meanings", "patterns", "examples"))


def _check_batch_plan(
    expected_sequence: list[tuple[int, str]],
    issues: list[str],
) -> None:
    sizes = [len(batch) for batch in AUTHORING_BATCHES]
    if sizes != [10, 10, 10, 9, 10, 10, 9]:
        issues.append("frozen authoring batch sizes changed")
    flattened = [item for batch in AUTHORING_BATCHES for item in batch]
    if flattened != expected_sequence:
        issues.append(
            "frozen authoring batches do not cover the ordered 68 exactly once"
        )
    if any(order in {17, 37} for order, _ in flattened):
        issues.append("metadata-only orders 17 and 37 cannot enter a batch")


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
        "priority": 8,
        "phase": "4B",
        "frozenFullPatternCount": 68,
    }
    for key, expected in expected_envelope.items():
        if data.get(key) != expected:
            issues.append(f"$.{key} must equal {expected!r}")
    phase_step = data.get("phaseStep")
    expected_revision = PHASE_STEP_REVISIONS.get(phase_step)
    if expected_revision is None:
        issues.append(
            "$.phaseStep must be one of: "
            + ", ".join(PHASE_STEP_REVISIONS)
        )
        completed_batch_count = 0
    else:
        completed_batch_count = int(phase_step[-1])
        if data.get("stagingRevision") != expected_revision:
            issues.append(
                f"$.stagingRevision must equal {expected_revision!r} for "
                f"{phase_step}"
            )

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
    _check_batch_plan(expected_sequence, issues)

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
        if phase_step == "4B0" and status != "draft":
            issues.append(f"{path}.stagingReviewStatus must be draft in Phase 4B0")

        candidate = record.get("candidateContent")
        candidate_path = f"{path}.candidateContent"
        candidate_counts = _validate_candidate_content(
            candidate, candidate_path, issues)
        batch_number = next(
            (batch_index for batch_index, batch in enumerate(
                AUTHORING_BATCHES, 1) if (record.get("verificationOrder"), lemma)
             in batch),
            None,
        )
        if phase_step == "4B0":
            for collection, count in zip(
                    ("meanings", "patterns", "examples"), candidate_counts):
                if count:
                    issues.append(
                        f"{candidate_path}.{collection} must be empty in Phase 4B0"
                    )
        elif batch_number is not None and batch_number <= completed_batch_count:
            if candidate_counts[0] == 0 or candidate_counts[1] == 0:
                issues.append(
                    f"{candidate_path}: completed-batch lemma requires "
                    "candidate meanings and patterns"
                )
        else:
            if any(candidate_counts):
                issues.append(
                    f"{candidate_path}: future-batch lemma must remain empty"
                )
            if status != "draft":
                issues.append(
                    f"{path}.stagingReviewStatus must remain draft before "
                    "its authoring batch"
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

    _check_recursive_prohibitions(
        data, issues, allow_candidate_keys=phase_step != "4B0")
    return issues


def load_staging(path: Path = STAGING_PATH) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_file(path: Path = STAGING_PATH) -> list[str]:
    return validate_data(load_staging(path))


def success_summary(data: dict[str, Any]) -> str:
    """Return the truthful deterministic success label for validated staging."""
    return (
        f"PASS: Priority 8 {data['phaseStep']} staging revision "
        f"{data['stagingRevision']} is read-only valid "
        "(68 lemmas, 21 constrained records, 12 global constraints)."
    )


def main() -> int:
    try:
        data = load_staging()
        issues = validate_data(data)
    except (OSError, json.JSONDecodeError, FrozenInputError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    if issues:
        print(f"FAIL: {len(issues)} staging validation issue(s)", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1
    print(success_summary(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
