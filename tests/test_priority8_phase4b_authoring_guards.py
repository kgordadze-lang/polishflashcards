"""Live semantic authoring guards for Priority 8 Phase 4B staging.

Unlike historical batch digests and the moving progress gate, these rules are
declarative structural invariants applied to whatever Phase 4B batch is live.
"""

from __future__ import annotations

import copy
import json
import re
import unittest
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STAGING_PATH = ROOT / "editorial/priority-8-phase4-staging.json"
RULES_PATH = ROOT / "tests/fixtures/priority8_phase4b_authoring_rules.json"
RULE_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
COMPLEMENT_FIELDS = {
    "type", "case", "preposition", "clauseKind", "required", "role",
}


class GuardConfigurationError(ValueError):
    """Raised when the declarative rule registry is malformed."""


COMMON_FIELDS = {"ruleId", "kind", "lemma", "verificationOrder"}
RULE_FIELDS = {
    "forbid-complement-cooccurrence": COMMON_FIELDS | {"signatures"},
    "forbid-complement-match": COMMON_FIELDS | {"signature"},
    "require-exact-pattern-shapes": COMMON_FIELDS
    | {"exactMeaningSet", "meaningShapes"},
    "require-lexical-identity": COMMON_FIELDS | {"lexicalItems"},
    "require-empty-candidate-content": {
        "ruleId", "kind", "lemma", "target", "ownerLemma",
    },
    "allow-only-preposition-case-signatures": COMMON_FIELDS
    | {"allowedSignatures"},
    "require-lexical-material-in-pattern": COMMON_FIELDS
    | {"meaningKey", "patternSelector", "material", "fields"},
}


def _configuration_problem(rule_id: str, message: str) -> None:
    raise GuardConfigurationError(f"rule {rule_id!r}: {message}")


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_signature(rule_id: str, value: Any, path: str) -> None:
    if not isinstance(value, dict) or not value:
        _configuration_problem(rule_id, f"{path} must be a non-empty object")
    unknown = set(value) - COMPLEMENT_FIELDS
    if unknown:
        _configuration_problem(
            rule_id, f"{path} has unknown fields: {', '.join(sorted(unknown))}"
        )
    if not _nonempty_string(value.get("type")):
        _configuration_problem(rule_id, f"{path}.type must be a non-empty string")
    if "required" in value and not isinstance(value["required"], bool):
        _configuration_problem(rule_id, f"{path}.required must be Boolean")


def _validate_signature_list(
    rule_id: str, value: Any, path: str, minimum: int = 1
) -> None:
    if not isinstance(value, list) or len(value) < minimum:
        _configuration_problem(
            rule_id, f"{path} must contain at least {minimum} signature(s)"
        )
    for index, signature in enumerate(value):
        _validate_signature(rule_id, signature, f"{path}[{index}]")


def validate_rule_registry(
    registry: Any, data: dict[str, Any] | None = None
) -> None:
    """Fail closed on malformed rules and, optionally, unresolved targets."""
    if not isinstance(registry, dict) or set(registry) != {
        "registryVersion", "rules"
    }:
        raise GuardConfigurationError(
            "registry must contain exactly registryVersion and rules"
        )
    if registry["registryVersion"] != 1:
        raise GuardConfigurationError("registryVersion must equal 1")
    if not isinstance(registry["rules"], list):
        raise GuardConfigurationError("rules must be an array")

    seen: set[str] = set()
    for index, rule in enumerate(registry["rules"]):
        if not isinstance(rule, dict):
            raise GuardConfigurationError(f"rules[{index}] must be an object")
        rule_id = rule.get("ruleId", f"rules[{index}]")
        if not _nonempty_string(rule.get("ruleId")) or not RULE_ID_RE.fullmatch(
            rule["ruleId"]
        ):
            _configuration_problem(str(rule_id), "ruleId must be a stable kebab-case ID")
        if rule_id in seen:
            _configuration_problem(rule_id, "duplicate ruleId")
        seen.add(rule_id)

        kind = rule.get("kind")
        if kind not in RULE_FIELDS:
            _configuration_problem(rule_id, f"unknown rule kind {kind!r}")
        if set(rule) != RULE_FIELDS[kind]:
            missing = RULE_FIELDS[kind] - set(rule)
            extra = set(rule) - RULE_FIELDS[kind]
            details = []
            if missing:
                details.append(f"missing fields: {', '.join(sorted(missing))}")
            if extra:
                details.append(f"unknown fields: {', '.join(sorted(extra))}")
            _configuration_problem(rule_id, "; ".join(details))
        if not _nonempty_string(rule["lemma"]):
            _configuration_problem(rule_id, "lemma must be a non-empty string")

        if "verificationOrder" in rule and (
            not isinstance(rule["verificationOrder"], int)
            or isinstance(rule["verificationOrder"], bool)
            or rule["verificationOrder"] < 1
        ):
            _configuration_problem(rule_id, "verificationOrder must be a positive integer")

        if kind == "forbid-complement-cooccurrence":
            _validate_signature_list(rule_id, rule["signatures"], "signatures", 2)
        elif kind == "forbid-complement-match":
            _validate_signature(rule_id, rule["signature"], "signature")
        elif kind == "require-exact-pattern-shapes":
            if not isinstance(rule["exactMeaningSet"], bool):
                _configuration_problem(rule_id, "exactMeaningSet must be Boolean")
            shapes = rule["meaningShapes"]
            if not isinstance(shapes, list) or not shapes:
                _configuration_problem(rule_id, "meaningShapes must be a non-empty array")
            meaning_keys: set[str] = set()
            for meaning_index, shape in enumerate(shapes):
                path = f"meaningShapes[{meaning_index}]"
                if not isinstance(shape, dict) or set(shape) != {
                    "meaningKey", "patterns"
                }:
                    _configuration_problem(
                        rule_id, f"{path} must contain exactly meaningKey and patterns"
                    )
                meaning_key = shape["meaningKey"]
                if not _nonempty_string(meaning_key):
                    _configuration_problem(rule_id, f"{path}.meaningKey is invalid")
                if meaning_key in meaning_keys:
                    _configuration_problem(rule_id, f"duplicate meaningKey {meaning_key!r}")
                meaning_keys.add(meaning_key)
                patterns = shape["patterns"]
                if not isinstance(patterns, list) or not patterns:
                    _configuration_problem(rule_id, f"{path}.patterns must not be empty")
                for pattern_index, pattern_shape in enumerate(patterns):
                    _validate_signature_list(
                        rule_id,
                        pattern_shape,
                        f"{path}.patterns[{pattern_index}]",
                    )
        elif kind == "require-lexical-identity":
            items = rule["lexicalItems"]
            if not isinstance(items, list) or not items or not all(
                _nonempty_string(item) for item in items
            ):
                _configuration_problem(
                    rule_id, "lexicalItems must be a non-empty string array"
                )
        elif kind == "require-empty-candidate-content":
            if rule["target"] != "metadataAspectPartner":
                _configuration_problem(
                    rule_id, "target must equal 'metadataAspectPartner'"
                )
            if not _nonempty_string(rule["ownerLemma"]):
                _configuration_problem(rule_id, "ownerLemma must be a non-empty string")
        elif kind == "allow-only-preposition-case-signatures":
            _validate_signature_list(
                rule_id, rule["allowedSignatures"], "allowedSignatures"
            )
            for signature in rule["allowedSignatures"]:
                if signature.get("type") != "preposition-case":
                    _configuration_problem(
                        rule_id, "allowedSignatures must describe preposition-case complements"
                    )
        elif kind == "require-lexical-material-in-pattern":
            if not _nonempty_string(rule["meaningKey"]):
                _configuration_problem(rule_id, "meaningKey must be a non-empty string")
            _validate_signature(
                rule_id, rule["patternSelector"], "patternSelector"
            )
            if not _nonempty_string(rule["material"]):
                _configuration_problem(rule_id, "material must be a non-empty string")
            if rule["fields"] != ["learnerExplanationEn"]:
                _configuration_problem(
                    rule_id,
                    "fields must currently equal ['learnerExplanationEn']",
                )

    if data is not None:
        issues = _target_issues(data, registry["rules"])
        if issues:
            raise GuardConfigurationError("; ".join(issues))


def _record_by_order(data: dict[str, Any], order: int) -> dict[str, Any] | None:
    return next(
        (item for item in data.get("lemmas", [])
         if item.get("verificationOrder") == order),
        None,
    )


def _record_by_lemma(data: dict[str, Any], lemma: str) -> dict[str, Any] | None:
    return next(
        (item for item in data.get("lemmas", [])
         if item.get("canonicalLemma") == lemma),
        None,
    )


def _target(data: dict[str, Any], rule: dict[str, Any]) -> dict[str, Any] | None:
    if rule["kind"] == "require-empty-candidate-content":
        owner = _record_by_lemma(data, rule["ownerLemma"])
        if owner is None:
            return None
        partner = owner.get("metadataAspectPartner")
        if isinstance(partner, dict) and partner.get("canonicalLemma") == rule["lemma"]:
            return partner
        return None
    return _record_by_order(data, rule["verificationOrder"])


def _target_issues(
    data: dict[str, Any], rules: list[dict[str, Any]]
) -> list[str]:
    issues = []
    for rule in rules:
        target = _target(data, rule)
        if target is None:
            issues.append(
                f"rule {rule['ruleId']!r} targets nonexistent lemma "
                f"{rule['lemma']!r}"
            )
        elif target.get("canonicalLemma") != rule["lemma"]:
            issues.append(
                f"rule {rule['ruleId']!r} expected lemma {rule['lemma']!r} "
                f"but target is {target.get('canonicalLemma')!r}"
            )
    return issues


def _matches(complement: dict[str, Any], signature: dict[str, Any]) -> bool:
    return all(complement.get(key) == value for key, value in signature.items())


def _canonical_shape(complements: list[dict[str, Any]]) -> str:
    normalized = sorted(
        json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        for item in complements
    )
    return "[" + ",".join(normalized) + "]"


def _label(rule: dict[str, Any], pattern: dict[str, Any] | None = None) -> str:
    label = f"[{rule['ruleId']}] lemma {rule['lemma']!r}"
    if pattern is not None:
        label += (
            f", meaning {pattern.get('meaningKeyRef')!r}, "
            f"pattern {pattern.get('candidatePatternKey')!r}"
        )
    return label


def _token_present(text: str, material: str) -> bool:
    return re.search(
        rf"(?<!\w){re.escape(material)}(?!\w)", text, flags=re.IGNORECASE
    ) is not None


def guard_issues(
    data: dict[str, Any], registry: dict[str, Any]
) -> list[str]:
    """Return every semantic rule violation; malformed registries raise."""
    validate_rule_registry(registry)
    issues = []
    for rule in registry["rules"]:
        item = _target(data, rule)
        if item is None:
            issues.append(
                f"[{rule['ruleId']}] lemma {rule['lemma']!r}: target does not exist"
            )
            continue
        if item.get("canonicalLemma") != rule["lemma"]:
            issues.append(
                f"[{rule['ruleId']}] lemma {rule['lemma']!r}: canonical identity "
                f"must equal {rule['lemma']!r}, found "
                f"{item.get('canonicalLemma')!r}"
            )
            continue

        kind = rule["kind"]
        content = item.get("candidateContent", {})
        patterns = content.get("patterns", [])

        if kind == "forbid-complement-cooccurrence":
            for pattern in patterns:
                complements = pattern.get("complements", [])
                if all(
                    any(_matches(complement, signature)
                        for complement in complements)
                    for signature in rule["signatures"]
                ):
                    issues.append(
                        f"{_label(rule, pattern)}: prohibited complement "
                        f"co-occurrence matched all signatures {rule['signatures']!r}"
                    )
        elif kind == "forbid-complement-match":
            for pattern in patterns:
                for complement in pattern.get("complements", []):
                    if _matches(complement, rule["signature"]):
                        issues.append(
                            f"{_label(rule, pattern)}: prohibited complement "
                            f"matched {rule['signature']!r}"
                        )
        elif kind == "require-exact-pattern-shapes":
            expected_meanings = {
                shape["meaningKey"] for shape in rule["meaningShapes"]
            }
            actual_meanings = {
                meaning.get("candidateMeaningKey")
                for meaning in content.get("meanings", [])
            }
            if rule["exactMeaningSet"] and actual_meanings != expected_meanings:
                issues.append(
                    f"{_label(rule)}: exact meaning set must be "
                    f"{sorted(expected_meanings)!r}, found {sorted(actual_meanings)!r}"
                )
            for meaning_shape in rule["meaningShapes"]:
                meaning_key = meaning_shape["meaningKey"]
                expected = Counter(
                    _canonical_shape(shape)
                    for shape in meaning_shape["patterns"]
                )
                actual_patterns = [
                    pattern for pattern in patterns
                    if pattern.get("meaningKeyRef") == meaning_key
                ]
                actual = Counter(
                    _canonical_shape(pattern.get("complements", []))
                    for pattern in actual_patterns
                )
                if actual != expected:
                    issues.append(
                        f"{_label(rule)}, meaning {meaning_key!r}: required exact "
                        f"pattern shapes {dict(expected)!r}, found {dict(actual)!r}"
                    )
        elif kind == "require-lexical-identity":
            missing = [
                material for material in rule["lexicalItems"]
                if not _token_present(item["canonicalLemma"], material)
            ]
            if missing:
                issues.append(
                    f"{_label(rule)}: canonical identity lacks required lexical "
                    f"material {missing!r}"
                )
        elif kind == "require-empty-candidate-content":
            if "candidateContent" in item:
                issues.append(
                    f"{_label(rule)}: metadata-only identity must not have "
                    "candidateContent"
                )
        elif kind == "allow-only-preposition-case-signatures":
            allowed = rule["allowedSignatures"]
            for pattern in patterns:
                for complement in pattern.get("complements", []):
                    if complement.get("type") != "preposition-case":
                        continue
                    if not any(complement == signature for signature in allowed):
                        issues.append(
                            f"{_label(rule, pattern)}: unauthorized concretized "
                            f"preposition-case signature {complement!r}; allowed "
                            f"signatures are {allowed!r}"
                        )
        elif kind == "require-lexical-material-in-pattern":
            selected = [
                pattern for pattern in patterns
                if pattern.get("meaningKeyRef") == rule["meaningKey"]
                and any(
                    _matches(complement, rule["patternSelector"])
                    for complement in pattern.get("complements", [])
                )
            ]
            if not selected:
                issues.append(
                    f"{_label(rule)}, meaning {rule['meaningKey']!r}: no pattern "
                    f"matches selector {rule['patternSelector']!r}"
                )
            for pattern in selected:
                for field in rule["fields"]:
                    value = pattern.get(field, "")
                    if not isinstance(value, str) or not _token_present(
                        value, rule["material"]
                    ):
                        issues.append(
                            f"{_label(rule, pattern)}: field {field!r} lacks "
                            f"required lexical material {rule['material']!r}"
                        )
    return issues


def _record(data: dict[str, Any], lemma: str) -> dict[str, Any]:
    return next(
        item for item in data["lemmas"] if item["canonicalLemma"] == lemma
    )


def _pattern(
    data: dict[str, Any], lemma: str, meaning: str, pattern_key: str
) -> dict[str, Any]:
    return next(
        pattern
        for pattern in _record(data, lemma)["candidateContent"]["patterns"]
        if pattern["meaningKeyRef"] == meaning
        and pattern["candidatePatternKey"] == pattern_key
    )


class Priority8Phase4BAuthoringGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.live = json.loads(STAGING_PATH.read_text(encoding="utf-8"))
        cls.registry = json.loads(RULES_PATH.read_text(encoding="utf-8"))

    def assert_caught(self, data: dict[str, Any], rule_id: str) -> None:
        issues = guard_issues(data, self.registry)
        self.assertTrue(issues, "mutation unexpectedly passed all guards")
        self.assertTrue(
            any(f"[{rule_id}]" in issue for issue in issues),
            f"expected {rule_id!r}; issues were {issues!r}",
        )

    def test_registry_is_valid_and_all_live_targets_exist(self):
        validate_rule_registry(self.registry, self.live)

    def test_current_live_staging_passes_all_authoring_guards(self):
        self.assertEqual([], guard_issues(self.live, self.registry))

    def test_pozwalac_arbitrary_key_cannot_bypass_dative_infinitive_guard(self):
        data = copy.deepcopy(self.live)
        content = _record(data, "pozwalać")["candidateContent"]
        injected = copy.deepcopy(content["patterns"][0])
        injected["candidatePatternKey"] = "arbitrary-future-bypass-key"
        injected["complements"] = [
            {"type": "case", "case": "dative", "required": False,
             "role": "recipient"},
            {"type": "infinitive", "required": True, "role": "content"},
        ]
        content["patterns"].append(injected)
        self.assert_caught(data, "p8-4b-pozwalac-no-dative-infinitive")

    def test_unikac_arbitrary_key_infinitive_is_caught(self):
        data = copy.deepcopy(self.live)
        pattern = copy.deepcopy(
            _record(data, "unikać")["candidateContent"]["patterns"][0]
        )
        pattern["candidatePatternKey"] = "arbitrary-new-construction"
        pattern["complements"] = [
            {"type": "infinitive", "required": True, "role": "content"}
        ]
        _record(data, "unikać")["candidateContent"]["patterns"].append(pattern)
        self.assert_caught(data, "p8-4b-unikac-no-infinitive")

    def test_wymagac_standalone_od_pattern_is_caught(self):
        data = copy.deepcopy(self.live)
        pattern = copy.deepcopy(
            _record(data, "wymagać")["candidateContent"]["patterns"][0]
        )
        pattern["candidatePatternKey"] = "arbitrary-standalone-source"
        pattern["complements"] = [{
            "type": "preposition-case", "preposition": "od",
            "case": "genitive", "required": True, "role": "target",
        }]
        _record(data, "wymagać")["candidateContent"]["patterns"].append(pattern)
        self.assert_caught(data, "p8-4b-wymagac-exact-alternative-shapes")

    def test_wymagac_optional_od_requiredness_change_is_caught(self):
        data = copy.deepcopy(self.live)
        pattern = _pattern(
            data, "wymagać", "person-requires-behavior",
            "genitive-required-content",
        )
        od_complement = next(
            complement for complement in pattern["complements"]
            if complement["type"] == "preposition-case"
        )
        od_complement["required"] = True
        self.assert_caught(data, "p8-4b-wymagac-exact-alternative-shapes")

    def test_klocic_sie_canonical_identity_change_is_caught(self):
        data = copy.deepcopy(self.live)
        _record(data, "kłócić się")["canonicalLemma"] = "kłócić"
        self.assert_caught(data, "p8-4b-klocic-sie-lexical-identity")

    def test_radzic_sobie_canonical_identity_change_is_caught(self):
        data = copy.deepcopy(self.live)
        _record(data, "radzić sobie")["canonicalLemma"] = "radzić"
        self.assert_caught(data, "p8-4b-radzic-sobie-lexical-identity")

    def test_zaczynac_candidate_content_is_caught(self):
        data = copy.deepcopy(self.live)
        partner = _record(data, "zacząć")["metadataAspectPartner"]
        partner["candidateContent"] = {
            "meanings": [{"candidateMeaningKey": "unauthorized"}],
            "patterns": [],
            "examples": [],
        }
        self.assert_caught(data, "p8-4b-zaczynac-metadata-only")

    def test_przeczytac_candidate_content_is_caught(self):
        data = copy.deepcopy(self.live)
        partner = _record(data, "czytać")["metadataAspectPartner"]
        partner["candidateContent"] = {
            "meanings": [{"candidateMeaningKey": "unauthorized"}],
            "patterns": [],
            "examples": [],
        }
        self.assert_caught(data, "p8-4b-przeczytac-metadata-only")

    def test_pokazywac_unauthorized_w_accusative_is_caught(self):
        data = copy.deepcopy(self.live)
        pattern = copy.deepcopy(
            _record(data, "pokazywać")["candidateContent"]["patterns"][0]
        )
        pattern["candidatePatternKey"] = "arbitrary-gdzie-realization"
        pattern["complements"] = [{
            "type": "preposition-case", "preposition": "w",
            "case": "accusative", "required": True, "role": "target",
        }]
        _record(data, "pokazywać")["candidateContent"]["patterns"].append(pattern)
        self.assert_caught(
            data, "p8-4b-pokazywac-authorized-preposition-cases"
        )

    def test_pokazywac_current_na_accusative_pointing_is_allowed(self):
        pattern = _pattern(
            self.live, "pokazywać", "directing-attention-to-content",
            "na-accusative-pointing",
        )
        self.assertEqual(
            [{
                "type": "preposition-case", "preposition": "na",
                "case": "accusative", "required": True, "role": "target",
            }],
            pattern["complements"],
        )
        self.assertEqual([], guard_issues(self.live, self.registry))

    def test_unknown_rule_kind_fails_closed(self):
        registry = copy.deepcopy(self.registry)
        registry["rules"][0]["kind"] = "execute-arbitrary-python"
        with self.assertRaisesRegex(
            GuardConfigurationError, "unknown rule kind.*execute-arbitrary-python"
        ):
            validate_rule_registry(registry)

    def test_malformed_rule_fails_closed(self):
        registry = copy.deepcopy(self.registry)
        registry["rules"][0].pop("signatures")
        with self.assertRaisesRegex(
            GuardConfigurationError, "missing fields: signatures"
        ):
            validate_rule_registry(registry)

    def test_duplicate_rule_ids_fail_closed(self):
        registry = copy.deepcopy(self.registry)
        registry["rules"].append(copy.deepcopy(registry["rules"][0]))
        with self.assertRaisesRegex(GuardConfigurationError, "duplicate ruleId"):
            validate_rule_registry(registry)

    def test_nonexistent_target_lemma_is_rejected(self):
        registry = copy.deepcopy(self.registry)
        registry["rules"][0]["lemma"] = "nieistniejący"
        registry["rules"][0]["verificationOrder"] = 999
        with self.assertRaisesRegex(
            GuardConfigurationError, "targets nonexistent lemma 'nieistniejący'"
        ):
            validate_rule_registry(registry, self.live)

    def _synthetic_lexical_material(self, explanation: str) -> tuple[
        dict[str, Any], dict[str, Any]
    ]:
        data = {"lemmas": [{
            "verificationOrder": 999,
            "canonicalLemma": "synthetic-participation",
            "candidateContent": {
                "meanings": [{"candidateMeaningKey": "participation"}],
                "patterns": [{
                    "candidatePatternKey": "deliberately-uninformative-key",
                    "meaningKeyRef": "participation",
                    "complements": [{
                        "type": "preposition-case", "preposition": "w",
                        "case": "locative", "required": True, "role": "topic",
                    }],
                    "learnerExplanationEn": explanation,
                }],
                "examples": [],
            },
        }]}
        registry = {"registryVersion": 1, "rules": [{
            "ruleId": "synthetic-required-lexical-material",
            "kind": "require-lexical-material-in-pattern",
            "lemma": "synthetic-participation",
            "verificationOrder": 999,
            "meaningKey": "participation",
            "patternSelector": {
                "type": "preposition-case", "preposition": "w",
                "case": "locative",
            },
            "material": "udział",
            "fields": ["learnerExplanationEn"],
        }]}
        return data, registry

    def test_required_lexical_material_primitive_passes_when_present(self):
        data, registry = self._synthetic_lexical_material(
            "Keep udział in the fixed participation construction."
        )
        self.assertEqual([], guard_issues(data, registry))

    def test_required_lexical_material_primitive_fails_when_absent(self):
        data, registry = self._synthetic_lexical_material(
            "A stripped generic location construction."
        )
        issues = guard_issues(data, registry)
        self.assertEqual(1, len(issues))
        self.assertIn("required lexical material 'udział'", issues[0])


if __name__ == "__main__":
    unittest.main()
