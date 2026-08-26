#!/usr/bin/env python3
"""Priority 7 Phase 2A fictional schema, review, ID, and projection tooling.

This module is deliberately independent from the Po polsku browser runtime and
from ``validate_content.py``.  It accepts only the locked Phase 1 editorial and
runtime shapes, and it never writes a production asset.  The command-line
interface is read-only except for an explicitly requested projected output.
"""

from __future__ import annotations

import argparse
import copy
import dataclasses
import datetime as _datetime
import hashlib
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


FORMAT_VERSION = 2
SCOPE_VERSION = 1
EDITORIAL_ARTIFACT_STATUS = "priority-7-editorial-nonproduction"
SPECIFICATION_ARTIFACT_STATUS = "specification-example-not-production"
FROZEN_ARTIFACT_STATUS = "priority-7-frozen-fixture-nonproduction"
NONRELEASE_PROJECTION_STATUS = (
    "priority-7-runtime-projection-nonrelease-fixture")

KEY_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SAFE_ID_RE = re.compile(r"^[a-z0-9-]+$")
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
ID_RES = {
    "lemma": re.compile(r"^vp-l-[a-z0-9]+(?:-[a-z0-9]+)*-[0-9a-f]{12}$"),
    "meaning": re.compile(r"^vp-m-[a-z0-9]+(?:-[a-z0-9]+)*-[0-9a-f]{12}$"),
    "pattern": re.compile(r"^vp-p-[a-z0-9]+(?:-[a-z0-9]+)*-[0-9a-f]{12}$"),
    "example": re.compile(r"^vp-e-[a-z0-9]+(?:-[a-z0-9]+)*-[0-9a-f]{12}$"),
    "exercise": re.compile(r"^vp-x-[a-z0-9]+(?:-[a-z0-9]+)*-[0-9a-f]{12}$"),
}

RELATION_TYPES = {
    "lexical-frame", "constructional-frame", "means-method",
    "subject-experiencer",
}
COMPLEMENT_TYPES = {"case", "preposition-case", "infinitive", "clause"}
CASE_IDS = {
    "nominative", "genitive", "dative", "accusative", "instrumental",
    "locative", "vocative",
}
DIRECT_CASE_IDS = {
    "nominative", "genitive", "dative", "accusative", "instrumental",
}
PREPOSITION_CASE_IDS = {
    "genitive", "dative", "accusative", "instrumental", "locative",
}
ROLES = {
    "subject", "object", "recipient", "experiencer", "predicate",
    "content", "topic", "interlocutor", "means", "target", "source",
}
CLAUSE_KINDS = {"ze", "czy", "zeby", "interrogative", "direct-speech"}
ASPECTS = {"imperfective", "perfective", "biaspectual", "unresolved"}
CEFR_LEVELS = ("A1", "A2", "B1", "above-b1")
TEACHING_STATUSES = {"active-production", "recognition-only", "deferred"}
USAGE_PRIORITIES = {"core", "common", "limited"}
REGISTERS = {"neutral", "formal", "informal"}
ACTIVITY_KEYS = {
    "reference", "search", "grammar-choose", "grammar-build", "type-it",
    "listening", "mixed-quiz", "case-mix", "conversation",
}
REVIEW_STATES = {
    "research", "externally-verified", "native-reviewed", "approved",
    "deferred", "rejected", "reference-verified", "editorial-reviewed",
}
REVIEW_KINDS = {
    "external-verification", "native-linguistic", "product-approval",
    "reopen", "correction", "reference-verification", "editorial-review",
}
# The three locked *scope tiers*.  These names are also the human-reviewed
# release chain, which is why the tuple is unchanged: a stage's scope digest is
# a property of what it covers (structure, learner wording, integration), not of
# who or what performed it.
STAGE_KINDS = (
    "external-verification", "native-linguistic", "product-approval",
)
# The Phase 4E solo-maintainer chain covers the same three tiers with truthful
# names for the actors that actually perform them: the maintainer checking a
# claim against documented references, independent nonhuman editorial review,
# and the project owner's product decision.
SOLO_STAGE_KINDS = (
    "reference-verification", "editorial-review", "product-approval",
)
RELEASE_STAGE_KINDS = frozenset(STAGE_KINDS) | frozenset(SOLO_STAGE_KINDS)
STAGE_SCOPE_TIER = {
    "external-verification": "external-verification",
    "reference-verification": "external-verification",
    "native-linguistic": "native-linguistic",
    "editorial-review": "native-linguistic",
    "product-approval": "product-approval",
}
STAGE_TIER_INDEX = {tier: index for index, tier in enumerate(STAGE_KINDS)}
STAGE_STATE = {
    "external-verification": "externally-verified",
    "reference-verification": "reference-verified",
    "native-linguistic": "native-reviewed",
    "editorial-review": "editorial-reviewed",
    "product-approval": "approved",
}
HUMAN_REVIEWED_MODE = "human-reviewed"
SOLO_MAINTAINER_MODE = "solo-maintainer-reference-backed"
# A pattern that declares no mode is governed by the stricter, fully human
# chain.  Absence is never permissive, and an unrecognised value fails closed.
DEFAULT_RELEASE_MODE = HUMAN_REVIEWED_MODE
RELEASE_MODES = {
    HUMAN_REVIEWED_MODE: STAGE_KINDS,
    SOLO_MAINTAINER_MODE: SOLO_STAGE_KINDS,
}
# Phase 4E.1.  Whether a stage is performed by a person or by the project's own
# nonhuman workflow is a property of the governing mode, not of the stage name.
#
# ``editorial-review`` is actor-borne in both modes: it has no place in the
# human chain at all, and where it appears alongside one it is supplementary
# nonhuman commentary that can block but never advance.
#
# ``reference-verification`` is the solo chain's tier-1 stage and is likewise
# actor-borne, because no second human reference reviewer exists.  Phase 4E
# shipped it requiring a human ``reviewerRef``, which would have forced the
# project to name the owner -- or someone else -- as a human reference verifier
# they are not.  It now resolves through the nonhuman actor registry instead.
MODE_NONHUMAN_STAGE_KINDS = {
    HUMAN_REVIEWED_MODE: frozenset({"editorial-review"}),
    SOLO_MAINTAINER_MODE: frozenset(
        {"editorial-review", "reference-verification"}),
}
# Stage kinds a mode refuses outright rather than merely declining to advance
# on.  Under the human chain, tier 1 is an identified human external verifier;
# a reference-verification event there would be ambiguous about who actually
# verified the claim, which is precisely the confusion Phase 4E.1 removes.
MODE_FORBIDDEN_STAGE_KINDS = {
    HUMAN_REVIEWED_MODE: frozenset({"reference-verification"}),
    SOLO_MAINTAINER_MODE: frozenset(),
}
REVIEWED_STATES = {
    "externally-verified", "reference-verified", "native-reviewed",
    "editorial-reviewed", "approved",
}
TIER1_KINDS = frozenset({"external-verification", "reference-verification"})
CONTEMPORARY_SOURCE_KINDS = {"contemporary-reference", "contemporary-corpus"}
# A reference verification must rest on a source-backed statement about the
# pattern or the meaning itself, not on headword presence alone.
REFERENCE_PATTERN_FACT_TYPES = {"complement-frame", "meaning"}
# The complete role vocabulary a nonhuman actor may hold.  Roles name what the
# workflow does, never which vendor or model ran it, so a release stays
# reproducible without a commercial product name being load-bearing.
EDITORIAL_ACTOR_ROLES = {
    "editorial-review", "example-generation", "reference-verification",
}
FINDING_SEVERITIES = {"low", "medium", "high"}
BLOCKING_FINDING_SEVERITIES = {"high"}
ORIGIN_KINDS = {"original", "repository-reuse", "editorial-generated"}
REVIEW_DECISIONS = {"accept", "changes-requested", "defer", "reject"}
SOURCE_KINDS = {
    "repository", "medak-research", "contemporary-reference",
    "contemporary-corpus",
}
FACT_TYPES = {
    "lemma", "meaning", "complement-frame", "usage-register", "contrast",
    "cefr",
}
CONTENT_KINDS = {"card", "topic", "drill", "scenario"}
CONTENT_PURPOSES = {"support", "practice", "context", "contrast"}
ERROR_KINDS = {"documented-common-error", "predicted-distractor"}
PREPOSITION_RE = re.compile(r"^[a-ząćęłńóśźż]+$")
REQUIRED_LEXICAL_ITEM_RE = PREPOSITION_RE

# The private keys the shipping JavaScript loader mirrors exactly in its own
# rejection list.  This set is a locked cross-language contract and must not
# drift; Phase 4E therefore leaves it alone and layers its own vocabulary below.
PRIVATE_RUNTIME_KEYS = {
    "artifactStatus", "specificationNotice", "internalScope", "key",
    "evidence", "sourceId", "sourceKind", "locator", "factType",
    "checkedAt", "reviewState", "reviewEvents", "reviewerRef", "reviewedAt",
    "scopeVersion", "scopeDigest", "supportingEvidenceDigests", "origin",
    "authorRef", "authoredAt", "repositorySource", "evidenceRefs",
    "sourceRegistry", "reviewerRegistry", "authorRegistry", "editorialNotes",
}
# Phase 4E governance vocabulary.  Every one of these lives only in the private
# editorial record or the frozen release envelope.  The closed runtime schema
# gives them nowhere to appear, so the shipping loader needs no extension and
# this Python-side sweep is defence in depth.
GOVERNANCE_PRIVATE_KEYS = {
    "releaseMode", "releaseAuthorization", "actorRef",
    "corroboratingActorRefs", "findings", "generatorRef", "adoptedAt",
    "editorialActorRegistry",
}
FORBIDDEN_RUNTIME_KEYS = PRIVATE_RUNTIME_KEYS | GOVERNANCE_PRIVATE_KEYS


@dataclass(frozen=True)
class Issue:
    """One deterministic validation finding."""

    code: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.code} {self.path}: {self.message}"


class ValidationFailure(ValueError):
    """Raised when a fail-closed operation receives invalid input."""

    def __init__(self, issues: Sequence[Issue]):
        self.issues = list(issues)
        super().__init__("\n".join(str(issue) for issue in self.issues))


@dataclass(frozen=True)
class RepositoryEntity:
    kind: str
    entity_id: str
    record: Mapping[str, Any]
    path: str


@dataclass
class RepositoryIndex:
    """Fail-closed index over stable cards, drills, topics, and scenarios."""

    entities: dict[str, RepositoryEntity] = field(default_factory=dict)
    issues: list[Issue] = field(default_factory=list)

    @classmethod
    def from_sources(cls, sources: Any) -> "RepositoryIndex":
        result = cls()
        if not isinstance(sources, list):
            result.issues.append(Issue(
                "REPOSITORY_SOURCES_TYPE", "$repository",
                "Repository sources must be a list."))
            return result

        def add(kind: str, record: Any, path: str) -> None:
            if not isinstance(record, dict):
                result.issues.append(Issue(
                    "REPOSITORY_ENTITY_TYPE", path,
                    f"Repository {kind} must be an object."))
                return
            entity_id = record.get("id")
            if not isinstance(entity_id, str) or not SAFE_ID_RE.fullmatch(entity_id):
                result.issues.append(Issue(
                    "REPOSITORY_ID", path,
                    f"Repository {kind} requires a lowercase safe stable ID."))
                return
            if entity_id in result.entities:
                prior = result.entities[entity_id]
                result.issues.append(Issue(
                    "REPOSITORY_DUPLICATE_ID", path,
                    f"ID {entity_id!r} already belongs to {prior.kind} at {prior.path}."))
                return
            result.entities[entity_id] = RepositoryEntity(
                kind, entity_id, record, path)

        for source_index, source in enumerate(sources):
            source_path = f"$repository[{source_index}]"
            if not isinstance(source, dict):
                result.issues.append(Issue(
                    "REPOSITORY_SOURCE_TYPE", source_path,
                    "Repository source must be an object."))
                continue
            source_issues = source.get("sourceIssues", [])
            if not isinstance(source_issues, list):
                result.issues.append(Issue(
                    "REPOSITORY_SOURCE_ISSUES_TYPE", source_path,
                    "Repository sourceIssues must be an array when present."))
            else:
                for source_issue in source_issues:
                    result.issues.append(Issue(
                        "REPOSITORY_SOURCE_INVALID", source_path,
                        f"Upstream source issue: {source_issue}"))
            levels = source.get("levels")
            if not isinstance(levels, list):
                result.issues.append(Issue(
                    "REPOSITORY_LEVELS_TYPE", source_path,
                    "Repository source levels must be a list."))
                continue
            for level_index, level in enumerate(levels):
                if not isinstance(level, dict):
                    result.issues.append(Issue(
                        "REPOSITORY_LEVEL_TYPE",
                        f"{source_path}.levels[{level_index}]",
                        "Repository level must be an object."))
                    continue
                topics = level.get("topics", [])
                if not isinstance(topics, list):
                    result.issues.append(Issue(
                        "REPOSITORY_TOPICS_TYPE",
                        f"{source_path}.levels[{level_index}].topics",
                        "Repository topics must be a list."))
                    continue
                for topic_index, topic in enumerate(topics):
                    topic_path = (
                        f"{source_path}.levels[{level_index}].topics[{topic_index}]")
                    if not isinstance(topic, dict):
                        result.issues.append(Issue(
                            "REPOSITORY_TOPIC_TYPE", topic_path,
                            "Repository topic must be an object."))
                        continue
                    topic_kind = (
                        "scenario" if "scenes" in topic or topic.get("kind") == "convo"
                        else "topic")
                    add(topic_kind, topic, topic_path)
                    for collection, kind in (("cards", "card"), ("drills", "drill")):
                        records = topic.get(collection, [])
                        if not isinstance(records, list):
                            result.issues.append(Issue(
                                "REPOSITORY_COLLECTION_TYPE",
                                f"{topic_path}.{collection}",
                                f"Repository {collection} must be a list."))
                            continue
                        for record_index, record in enumerate(records):
                            add(kind, record, f"{topic_path}.{collection}[{record_index}]")
        return result

    def get(self, entity_id: Any) -> RepositoryEntity | None:
        if not isinstance(entity_id, str):
            return None
        return self.entities.get(entity_id)


@dataclass(frozen=True)
class ValidationContext:
    """Private registries are explicit inputs, never fields in the editorial file."""

    source_registry: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    reviewer_registry: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    author_registry: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    repository_index: RepositoryIndex | None = None
    today: _datetime.date = field(default_factory=_datetime.date.today)
    allocation_registry: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    # Nonhuman editorial actors live in their own registry so that no model can
    # ever be resolved through a field that means "identified human reviewer",
    # and no human can be laundered into a machine-generated provenance record.
    editorial_actor_registry: Mapping[str, Mapping[str, Any]] = field(
        default_factory=dict)
    pronunciation_playback_authorized: bool = False

    def __post_init__(self) -> None:
        if isinstance(self.today, str):
            try:
                parsed = _datetime.date.fromisoformat(self.today)
            except ValueError:
                return
            object.__setattr__(self, "today", parsed)


def _sha12(seed: str) -> str:
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]


def normalize_canonical_lemma(value: str) -> str:
    """Apply the exact Phase 1 canonical-lemma normalization."""
    if not isinstance(value, str):
        raise TypeError("canonical lemma must be a string")
    normalized = unicodedata.normalize("NFC", value)
    normalized = re.sub(r"\s+", " ", normalized.strip()).lower()
    return normalized


_POLISH_TRANSLITERATION = str.maketrans({
    "ą": "a", "ć": "c", "ę": "e", "ł": "l", "ń": "n",
    "ó": "o", "ś": "s", "ź": "z", "ż": "z",
})


def lemma_slug(canonical_lemma: str) -> str:
    normalized = normalize_canonical_lemma(canonical_lemma)
    slug = normalized.translate(_POLISH_TRANSLITERATION)
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    if len(slug) > 32:
        slug = slug[:32].rstrip("-")
    if not slug:
        raise ValueError("canonical lemma produces an empty ASCII slug")
    return slug


def _require_key(value: str, label: str) -> str:
    if not isinstance(value, str) or not KEY_RE.fullmatch(value):
        raise ValueError(f"{label} must be lowercase ASCII kebab-case")
    return value


def allocate_lemma_id(canonical_lemma: str) -> str:
    normalized = normalize_canonical_lemma(canonical_lemma)
    slug = lemma_slug(normalized)
    seed = f"v1|lemma|{normalized}"
    return f"vp-l-{slug}-{_sha12(seed)}"


def allocate_meaning_id(
        lemma_id: str, canonical_lemma: str, meaning_key: str) -> str:
    _require_key(meaning_key, "meaning key")
    if not ID_RES["lemma"].fullmatch(lemma_id):
        raise ValueError("owning lemma ID is malformed")
    seed = f"v1|meaning|{lemma_id}|{meaning_key}"
    return f"vp-m-{lemma_slug(canonical_lemma)}-{meaning_key}-{_sha12(seed)}"


def allocate_pattern_id(
        meaning_id: str, canonical_lemma: str, meaning_key: str,
        pattern_key: str) -> str:
    _require_key(meaning_key, "meaning key")
    _require_key(pattern_key, "pattern key")
    if not ID_RES["meaning"].fullmatch(meaning_id):
        raise ValueError("owning meaning ID is malformed")
    seed = f"v1|pattern|{meaning_id}|{pattern_key}"
    readable = f"{lemma_slug(canonical_lemma)}-{meaning_key}-{pattern_key}"
    return f"vp-p-{readable}-{_sha12(seed)}"


def pattern_readable_stem(pattern_id: str) -> str:
    if not isinstance(pattern_id, str):
        raise ValueError("owning pattern ID is malformed")
    match = re.fullmatch(
        r"vp-p-(?P<stem>[a-z0-9]+(?:-[a-z0-9]+)*)-(?P<digest>[0-9a-f]{12})",
        pattern_id)
    if match is None or not match.group("stem"):
        raise ValueError("owning pattern ID is malformed")
    return match.group("stem")


def allocate_example_id(pattern_id: str, example_key: str) -> str:
    _require_key(example_key, "example key")
    stem = pattern_readable_stem(pattern_id)
    seed = f"v1|example|{pattern_id}|{example_key}"
    return f"vp-e-{stem}-{example_key}-{_sha12(seed)}"


def allocate_exercise_id(
        pattern_id: str, activity_type: str, item_key: str) -> str:
    _require_key(activity_type, "activity type")
    _require_key(item_key, "item key")
    stem = pattern_readable_stem(pattern_id)
    seed = f"v1|exercise|{pattern_id}|{activity_type}|{item_key}"
    return f"vp-x-{stem}-{activity_type}-{item_key}-{_sha12(seed)}"


def _reject_surrogates(value: str) -> None:
    if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
        raise ValueError("RFC 8785 input must not contain lone surrogate code points")


def _utf16_sort_key(value: str) -> bytes:
    _reject_surrogates(value)
    return value.encode("utf-16be")


def canonicalize_rfc8785(value: Any) -> bytes:
    """RFC 8785 serialization for the deliberately limited Phase 1 domain.

    The reviewed schemas permit null, booleans, Unicode strings, arrays, objects,
    and small integers.  Floating-point numbers are forbidden.  Object property
    names are sorted by UTF-16 code units as required by JCS.  This limited-domain
    implementation therefore avoids the ECMAScript-number conversion problem
    without silently substituting ordinary ``sort_keys=True`` JSON.
    """

    def encode(item: Any) -> str:
        if item is None:
            return "null"
        if item is True:
            return "true"
        if item is False:
            return "false"
        if type(item) is int:
            if abs(item) > 9_007_199_254_740_991:
                raise ValueError("integer is outside the RFC 8785 safe domain")
            return str(item)
        if isinstance(item, float):
            raise TypeError("floating-point values are forbidden in Priority 7 digests")
        if isinstance(item, str):
            _reject_surrogates(item)
            if unicodedata.normalize("NFC", item) != item:
                raise ValueError("reviewed strings must already be Unicode NFC")
            return json.dumps(item, ensure_ascii=False, separators=(",", ":"))
        if isinstance(item, list):
            return "[" + ",".join(encode(child) for child in item) + "]"
        if isinstance(item, dict):
            for key in item:
                if not isinstance(key, str):
                    raise TypeError("RFC 8785 object property names must be strings")
                _reject_surrogates(key)
                if unicodedata.normalize("NFC", key) != key:
                    raise ValueError("reviewed property names must already be Unicode NFC")
            parts = []
            for key in sorted(item, key=_utf16_sort_key):
                parts.append(encode(key) + ":" + encode(item[key]))
            return "{" + ",".join(parts) + "}"
        raise TypeError(f"unsupported RFC 8785 value type: {type(item).__name__}")

    return encode(value).encode("utf-8")


def _full_digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonicalize_rfc8785(value)).hexdigest()


def evidence_digest(evidence_record: Mapping[str, Any]) -> str:
    return _full_digest(dict(evidence_record))


def _sorted_strings(value: Any) -> list[str]:
    return sorted(list(value or []))


def _project_complement(complement: Mapping[str, Any]) -> dict[str, Any]:
    projected = {
        "type": complement["type"],
        "required": complement["required"],
        "role": complement["role"],
        "questionOverridePl": copy.deepcopy(complement.get("questionOverridePl")),
    }
    for conditional in ("case", "preposition", "clauseKind"):
        if conditional in complement:
            projected[conditional] = complement[conditional]
    return projected


def _project_cefr(cefr: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "recognition": cefr["recognition"],
        "production": cefr.get("production"),
    }


def _project_usage(usage: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "priority": usage["priority"],
        "register": usage["register"],
        "note": usage.get("note"),
    }


def _project_error_notes(pattern: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Bind error claims to complete evidence digests, never array positions."""
    evidence = pattern["evidence"]
    if not isinstance(evidence, list):
        raise TypeError("pattern evidence must be an array")
    projected: list[dict[str, Any]] = []
    for note in pattern.get("errorNotes", []):
        projected_note = {
            "kind": note["kind"],
            "incorrectForm": note["incorrectForm"],
            "guidanceEn": note["guidanceEn"],
            "evidenceDigests": None,
        }
        if "evidenceRefs" in note:
            refs = note["evidenceRefs"]
            if not isinstance(refs, list) or any(
                    type(index) is not int or index < 0 or index >= len(evidence)
                    for index in refs):
                raise ValueError("error-note evidence index does not resolve")
            projected_note["evidenceDigests"] = [
                evidence_digest(evidence[index]) for index in refs]
        projected.append(projected_note)
    return projected


def review_scope(
        stage: str, lemma: Mapping[str, Any], meaning: Mapping[str, Any],
        pattern: Mapping[str, Any]) -> dict[str, Any]:
    """Construct the locked cumulative scope projection for one pattern.

    Phase 1 gives a field projection rather than a literal JSON example.  The
    direct representation used here keeps ancestor facts in ``lemma`` and
    ``meaning`` objects and accumulates pattern-owned facts in ``pattern``.

    ``stage`` accepts any release stage kind.  Phase 4E's solo-maintainer
    stages project the same three locked scope tiers as their human-reviewed
    counterparts, so ``scopeVersion`` stays 1 and no historical digest is
    reinterpreted: a reference verification covers exactly the fields an
    external verification covered, and an editorial review covers exactly the
    fields a native review covered.
    """
    if stage not in STAGE_SCOPE_TIER:
        raise ValueError(f"unknown review stage: {stage}")
    stage = STAGE_SCOPE_TIER[stage]
    result: dict[str, Any] = {
        "scopeVersion": SCOPE_VERSION,
        "lemma": {
            "id": lemma["id"],
            "canonicalLemma": lemma["canonicalLemma"],
            "displayLemma": lemma.get("displayLemma"),
            "reflexive": lemma["reflexive"],
            "aspect": lemma["aspect"],
            "aspectPartnerIds": _sorted_strings(lemma.get("aspectPartnerIds")),
        },
        "meaning": {
            "id": meaning["id"],
            "key": meaning["key"],
            "glossesEn": copy.deepcopy(meaning["glossesEn"]),
            "internalScope": meaning["internalScope"],
        },
        "pattern": {"id": pattern["id"], "key": pattern["key"]},
    }
    result["pattern"].update({
        "relationType": pattern["relationType"],
        "complements": [
            _project_complement(item) for item in pattern["complements"]],
        "aspectEquivalentPatternIds": _sorted_strings(
            pattern.get("aspectEquivalentPatternIds")),
        "usage": _project_usage(pattern["usage"]),
    })
    if "requiredLexicalItems" in pattern:
        result["pattern"]["requiredLexicalItems"] = copy.deepcopy(
            pattern["requiredLexicalItems"])
    if stage in ("native-linguistic", "product-approval"):
        result["pattern"].update({
            "cefr": _project_cefr(pattern["cefr"]),
            "teachingStatus": pattern["teachingStatus"],
            "learnerExplanationEn": pattern["learnerExplanationEn"],
            "examples": copy.deepcopy(pattern.get("examples")),
            "errorNotes": _project_error_notes(pattern),
            "activityEligibility": _sorted_strings(
                pattern.get("activityEligibility")),
        })
    if stage == "product-approval":
        result["pattern"]["contentRefs"] = sorted(
            copy.deepcopy(pattern.get("contentRefs", [])),
            key=lambda ref: (ref["kind"], ref["id"], ref["purpose"]))
    return result


def review_scope_digest(
        stage: str, lemma: Mapping[str, Any], meaning: Mapping[str, Any],
        pattern: Mapping[str, Any]) -> str:
    return _full_digest(review_scope(stage, lemma, meaning, pattern))


def _add(issues: list[Issue], code: str, path: str, message: str) -> None:
    issues.append(Issue(code, path, message))


def _validate_context(context: Any, issues: list[Issue]) -> bool:
    """Validate external/private dependencies once before any resolution."""
    if not isinstance(context, ValidationContext):
        _add(issues, "CONTEXT_TYPE", "$context",
             "Validation context must be a ValidationContext object.")
        return False
    valid = True
    for field_name in (
            "source_registry", "reviewer_registry", "author_registry",
            "allocation_registry", "editorial_actor_registry"):
        if not isinstance(getattr(context, field_name), Mapping):
            _add(issues, "CONTEXT_REGISTRY_TYPE", f"$context.{field_name}",
                 "Private registry must be an object mapping stable IDs to records.")
            valid = False
    if valid:
        # One identity key may never mean "human reviewer" in one registry and
        # "model" or "author" in another; that ambiguity is exactly how a
        # nonhuman actor would end up rendered as human review.
        for first, second in (
                ("reviewer_registry", "editorial_actor_registry"),
                ("author_registry", "editorial_actor_registry"),
                ("reviewer_registry", "author_registry")):
            shared = sorted(
                set(getattr(context, first)) & set(getattr(context, second)))
            if shared:
                _add(issues, "REGISTRY_KEY_COLLISION", f"$context.{second}",
                     f"Identity keys {shared!r} are claimed by both "
                     f"{first} and {second}.")
                valid = False
    if context.repository_index is not None and not isinstance(
            context.repository_index, RepositoryIndex):
        _add(issues, "CONTEXT_REPOSITORY_INDEX_TYPE", "$context.repository_index",
             "repository_index must be a RepositoryIndex or null.")
        valid = False
    if type(context.today) is not _datetime.date:
        _add(issues, "CONTEXT_DATE", "$context.today",
             "today must be a real date or ISO YYYY-MM-DD string.")
        valid = False
    if type(context.pronunciation_playback_authorized) is not bool:
        _add(issues, "CONTEXT_PLAYBACK_POLICY",
             "$context.pronunciation_playback_authorized",
             "pronunciation_playback_authorized must be a Boolean.")
        valid = False
    return valid


def _closed_object(
        value: Any, path: str, required: set[str], allowed: set[str],
        issues: list[Issue]) -> bool:
    if not isinstance(value, dict):
        _add(issues, "SCHEMA_OBJECT", path, "Value must be an object.")
        return False
    for key in sorted(required - set(value), key=str):
        _add(issues, "SCHEMA_REQUIRED", f"{path}.{key}", "Required field is missing.")
    for key in sorted(set(value) - allowed, key=str):
        _add(issues, "SCHEMA_UNKNOWN_FIELD", f"{path}.{key}", "Unknown field is forbidden.")
    return True


def _nonempty_string(
        value: Any, path: str, issues: list[Issue], minimum: int = 1,
        maximum: int | None = None) -> bool:
    if not isinstance(value, str) or len(value) < minimum:
        _add(issues, "SCHEMA_STRING", path, f"Value must be a string of length >= {minimum}.")
        return False
    if maximum is not None and len(value) > maximum:
        _add(issues, "SCHEMA_STRING_LENGTH", path, f"String exceeds {maximum} characters.")
        return False
    if unicodedata.normalize("NFC", value) != value:
        _add(issues, "STRING_NOT_NFC", path, "Reviewed strings must already be Unicode NFC.")
        return False
    try:
        _reject_surrogates(value)
    except ValueError as exc:
        _add(issues, "STRING_SURROGATE", path, str(exc))
        return False
    return True


def _is_member(value: Any, allowed: Iterable[Any]) -> bool:
    try:
        return value in allowed
    except (TypeError, ValueError):
        return False


def _enum(value: Any, allowed: set[str] | Sequence[str], path: str,
          issues: list[Issue]) -> bool:
    if not _is_member(value, allowed):
        _add(issues, "SCHEMA_ENUM", path, f"Value {value!r} is not in the closed enum.")
        return False
    return True


def _key(value: Any, path: str, issues: list[Issue]) -> bool:
    if not isinstance(value, str) or not KEY_RE.fullmatch(value):
        _add(issues, "KEY_INVALID", path, "Value must be lowercase ASCII kebab-case.")
        return False
    return True


def _id_syntax(value: Any, kind: str, path: str, issues: list[Issue]) -> bool:
    if not isinstance(value, str) or not ID_RES[kind].fullmatch(value):
        _add(issues, "ID_SYNTAX", path, f"Value is not a valid Priority 7 {kind} ID.")
        return False
    return True


def _boolean(value: Any, path: str, issues: list[Issue]) -> bool:
    if type(value) is not bool:
        _add(issues, "SCHEMA_BOOLEAN", path, "Value must be Boolean.")
        return False
    return True


def _date(value: Any, path: str, issues: list[Issue], today: _datetime.date) -> bool:
    if (not isinstance(value, str) or
            re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value) is None):
        _add(issues, "DATE_INVALID", path, "Date must use ISO YYYY-MM-DD.")
        return False
    try:
        parsed = _datetime.date.fromisoformat(value)
    except ValueError:
        _add(issues, "DATE_INVALID", path, "Date must be a real ISO YYYY-MM-DD date.")
        return False
    if parsed > today:
        _add(issues, "DATE_IN_FUTURE", path, "Date must not be in the future.")
        return False
    return True


def _string_list(
        value: Any, path: str, issues: list[Issue], *, min_items: int = 0,
        max_items: int | None = None, unique: bool = False,
        allowed: set[str] | None = None) -> bool:
    if not isinstance(value, list):
        _add(issues, "SCHEMA_ARRAY", path, "Value must be an array.")
        return False
    valid = True
    if len(value) < min_items:
        _add(issues, "SCHEMA_ARRAY_LENGTH", path, f"Array requires at least {min_items} item(s).")
        valid = False
    if max_items is not None and len(value) > max_items:
        _add(issues, "SCHEMA_ARRAY_LENGTH", path, f"Array permits at most {max_items} item(s).")
        valid = False
    for index, item in enumerate(value):
        if not _nonempty_string(item, f"{path}[{index}]", issues):
            valid = False
        elif allowed is not None and not _is_member(item, allowed):
            _add(issues, "SCHEMA_ENUM", f"{path}[{index}]", "Unknown array enum value.")
            valid = False
    if unique and all(isinstance(item, str) for item in value) and len(set(value)) != len(value):
        _add(issues, "SCHEMA_ARRAY_UNIQUE", path, "Array values must be unique.")
        valid = False
    return valid


def _validate_required_lexical_items(
        value: Any, path: str, issues: list[Issue]) -> None:
    """Validate ordered fixed words that belong to a pattern's structure."""
    if not _string_list(
            value, path, issues, min_items=1, max_items=4, unique=True):
        return
    for index, item in enumerate(value):
        if not REQUIRED_LEXICAL_ITEM_RE.fullmatch(item):
            _add(
                issues, "REQUIRED_LEXICAL_ITEM_INVALID", f"{path}[{index}]",
                "Required lexical items must be exact lowercase NFC Polish words.")


def _validate_repository_source(
        value: Any, path: str, issues: list[Issue]) -> None:
    required = {"kind", "id", "field"}
    if not _closed_object(value, path, required, required, issues):
        return
    kind = value.get("kind")
    _enum(kind, {"card", "drill"}, f"{path}.kind", issues)
    entity_id = value.get("id")
    if not isinstance(entity_id, str) or not SAFE_ID_RE.fullmatch(entity_id):
        _add(issues, "REPOSITORY_SOURCE_ID", f"{path}.id", "Source ID must be lowercase-safe.")
    field_value = value.get("field")
    allowed_fields = {"pl", "ex"} if kind == "card" else {"prompt", "answer"}
    if not _is_member(field_value, allowed_fields):
        _add(issues, "REPOSITORY_SOURCE_FIELD", f"{path}.field",
             f"Field is not allowed for source kind {kind!r}.")


def _resolve_repository_reuse(
        example: Mapping[str, Any], path: str, context: ValidationContext,
        issues: list[Issue]) -> None:
    source = example.get("origin", {}).get("repositorySource")
    if not isinstance(source, dict):
        return
    index = context.repository_index
    if index is None:
        _add(issues, "REPOSITORY_INDEX_REQUIRED", path,
             "Repository reuse requires a repository index.")
        return
    if index.issues:
        _add(issues, "REPOSITORY_INDEX_INVALID", path,
             "Repository index contains source or duplicate-ID errors.")
        return
    source_id = source.get("id")
    source_kind = source.get("kind")
    source_field = source.get("field")
    allowed_fields = {"pl", "ex"} if source_kind == "card" else {
        "prompt", "answer"}
    if (not isinstance(source_id, str) or
            not SAFE_ID_RE.fullmatch(source_id) or
            not _is_member(source_kind, {"card", "drill"}) or
            not isinstance(source_field, str) or
            not _is_member(source_field, allowed_fields)):
        return
    entity = index.get(source_id)
    if entity is None:
        _add(issues, "REPOSITORY_SOURCE_DANGLING", path,
             f"Repository source ID {source.get('id')!r} does not resolve.")
        return
    if entity.kind != source.get("kind"):
        _add(issues, "REPOSITORY_SOURCE_KIND", path,
             f"Repository source resolves as {entity.kind}, not {source.get('kind')}.")
        return
    if source_field not in entity.record:
        _add(issues, "REPOSITORY_SOURCE_FIELD_MISSING", path,
             f"Repository source has no {source_field!r} field.")
        return
    source_value = entity.record[source_field]
    if not isinstance(source_value, str):
        _add(issues, "REPOSITORY_SOURCE_NOT_STRING", path,
             "The exact referenced repository field is not a sentence string.")
        return
    if example.get("pl") != source_value:
        _add(issues, "REPOSITORY_SOURCE_MISMATCH", path,
             "Example text is not exactly equal to the referenced repository field.")


@dataclass(frozen=True)
class _EntityInfo:
    kind: str
    entity_id: str
    parent_id: str | None
    key: str | None
    path: str
    record: Mapping[str, Any]
    lemma: Mapping[str, Any]
    meaning: Mapping[str, Any] | None
    pattern: Mapping[str, Any] | None


def _validate_evidence(
        value: Any, path: str, context: ValidationContext,
        issues: list[Issue], *, resolve_registry: bool) -> None:
    required = {"sourceId", "sourceKind", "locator", "factType", "checkedAt"}
    allowed = required | {"note"}
    if not _closed_object(value, path, required, allowed, issues):
        return
    source_id = value.get("sourceId")
    _key(source_id, f"{path}.sourceId", issues)
    source_kind = value.get("sourceKind")
    _enum(source_kind, SOURCE_KINDS, f"{path}.sourceKind", issues)
    _nonempty_string(value.get("locator"), f"{path}.locator", issues, 3)
    _enum(value.get("factType"), FACT_TYPES, f"{path}.factType", issues)
    _date(value.get("checkedAt"), f"{path}.checkedAt", issues, context.today)
    if "note" in value:
        _nonempty_string(value["note"], f"{path}.note", issues, 1, 240)
    if resolve_registry and isinstance(source_id, str):
        registry = context.source_registry.get(source_id)
        if not isinstance(registry, Mapping):
            _add(issues, "SOURCE_REGISTRY_DANGLING", f"{path}.sourceId",
                 "Evidence sourceId does not resolve in the private source registry.")
        elif registry.get("sourceKind") != source_kind:
            _add(issues, "SOURCE_REGISTRY_KIND", f"{path}.sourceKind",
                 "Evidence sourceKind disagrees with the private source registry.")
        if (source_kind == "medak-research" and
                value.get("factType") != "lemma" and
                (not isinstance(registry, Mapping) or
                 registry.get("detailedEntryReviewed") is not True)):
            _add(issues, "MEDAK_DETAIL_NOT_ESTABLISHED", f"{path}.factType",
                 "Non-lemma Mędak evidence requires a registry record proving "
                 "that the detailed entry was reviewed.")


def _validate_editorial_actor(
        actor_ref: Any, path: str, role: str, context: ValidationContext,
        issues: list[Issue]) -> None:
    """Resolve a nonhuman editorial actor and refuse any human identity."""
    if not isinstance(actor_ref, str):
        return
    actor = context.editorial_actor_registry.get(actor_ref)
    if not isinstance(actor, Mapping):
        _add(issues, "EDITORIAL_ACTOR_REGISTRY_DANGLING", path,
             "Editorial actor reference does not resolve in the private "
             "nonhuman editorial actor registry.")
        return
    if actor.get("human") is not False:
        _add(issues, "EDITORIAL_ACTOR_NOT_NONHUMAN", path,
             "An editorial actor record must state human: false.  A human "
             "identity belongs in the reviewer or author registry.")
    roles = actor.get("roles", [])
    if not isinstance(roles, list) or role not in roles:
        _add(issues, "EDITORIAL_ACTOR_ROLE", path,
             f"Editorial actor lacks the required {role!r} role.")
    if isinstance(roles, list) and any(
            not isinstance(item, str) or item not in EDITORIAL_ACTOR_ROLES
            for item in roles):
        # A nonhuman actor may hold only the workflow roles this architecture
        # defines.  An unrecognised role -- above all one borrowed from the
        # human vocabulary, such as 'native-linguistic' -- is how a model would
        # start describing itself as something it cannot be.
        _add(issues, "EDITORIAL_ACTOR_ROLE_UNKNOWN", path,
             "A nonhuman editorial actor may hold only the workflow roles "
             f"{sorted(EDITORIAL_ACTOR_ROLES)!r}.")


def _validate_review_finding(
        value: Any, path: str, decision: Any, issues: list[Issue]) -> None:
    required = {"severity", "summary", "resolved"}
    if not _closed_object(
            value, path, required, required | {"resolutionNote"}, issues):
        return
    severity = value.get("severity")
    _enum(severity, FINDING_SEVERITIES, f"{path}.severity", issues)
    _nonempty_string(value.get("summary"), f"{path}.summary", issues, 3, 240)
    resolved = value.get("resolved")
    _boolean(resolved, f"{path}.resolved", issues)
    if resolved is True:
        if "resolutionNote" not in value:
            _add(issues, "SCHEMA_REQUIRED", f"{path}.resolutionNote",
                 "A resolved editorial finding must record how it was resolved.")
        else:
            _nonempty_string(
                value["resolutionNote"], f"{path}.resolutionNote", issues, 3, 240)
    elif "resolutionNote" in value:
        _add(issues, "EDITORIAL_FINDING_RESOLUTION_FORBIDDEN",
             f"{path}.resolutionNote",
             "An unresolved editorial finding must not carry a resolution note.")
    if (decision == "accept" and
            _is_member(severity, BLOCKING_FINDING_SEVERITIES) and
            resolved is not True):
        _add(issues, "EDITORIAL_UNRESOLVED_BLOCKING_FINDING", path,
             "An editorial acceptance cannot carry an unresolved blocking "
             "linguistic finding.")


def _validate_review_event(
        value: Any, path: str, context: ValidationContext,
        issues: list[Issue], *, resolve_registry: bool,
        release_mode: str | None = None) -> None:
    kind = value.get("kind") if isinstance(value, dict) else None
    # Phase 4E.1.  The applicable release mode is resolved *before* the schema
    # is closed, because which of actorRef and reviewerRef this event may carry
    # is a consequence of the mode, not of the stage name on its own.  An
    # absent, malformed or unknown mode resolves to the strictest chain here
    # and is separately reported by the closed-enum check that carried it.
    mode = normalized_release_mode(release_mode)
    # An editorial review is performed by a model, never by a person, and under
    # the solo chain so is reference verification: both carry an actorRef and
    # are structurally incapable of naming a human reviewer.
    nonhuman_stage = _is_member(kind, nonhuman_stage_kinds(mode))
    editorial_stage = kind == "editorial-review"
    required = {"kind", "decision", "reviewedAt"} | (
        {"actorRef"} if nonhuman_stage else {"reviewerRef"})
    allowed = required | {
        "scopeVersion", "scopeDigest", "supportingEvidenceDigests", "note"}
    if editorial_stage:
        allowed |= {"corroboratingActorRefs", "findings"}
    if not _closed_object(value, path, required, allowed, issues):
        return
    decision = value.get("decision")
    _enum(kind, REVIEW_KINDS, f"{path}.kind", issues)
    _enum(decision, REVIEW_DECISIONS, f"{path}.decision", issues)
    if _is_member(kind, forbidden_stage_kinds(mode)):
        # Not merely non-advancing: refused.  Recording a reference
        # verification against a human-reviewed pattern would leave the
        # history ambiguous about whether a person verified the claim.
        _add(issues, "REVIEW_STAGE_NOT_IN_MODE", f"{path}.kind",
             f"{kind!r} is not a review stage under the {mode!r} release "
             "mode, which verifies through an identified human external "
             "verifier.")
    reviewer_ref = None
    actor_ref = None
    if nonhuman_stage:
        actor_ref = value.get("actorRef")
        _key(actor_ref, f"{path}.actorRef", issues)
    else:
        reviewer_ref = value.get("reviewerRef")
        _key(reviewer_ref, f"{path}.reviewerRef", issues)
    _date(value.get("reviewedAt"), f"{path}.reviewedAt", issues, context.today)
    if "note" in value:
        _nonempty_string(value["note"], f"{path}.note", issues, 1, 240)

    for index, finding in enumerate(
            value.get("findings", []) if isinstance(
                value.get("findings"), list) else []):
        _validate_review_finding(
            finding, f"{path}.findings[{index}]", decision, issues)
    if "findings" in value and (
            not isinstance(value["findings"], list) or not value["findings"]):
        _add(issues, "EDITORIAL_FINDINGS_TYPE", f"{path}.findings",
             "Editorial findings must be a non-empty array when present.")

    corroborating = value.get("corroboratingActorRefs")
    # Corroboration is the editorial tier's own independence mechanism and
    # stays there.  A reference verification's substantive support is the cited
    # source evidence, checked below, not a second opinion about the sources.
    if editorial_stage and decision == "accept":
        if not isinstance(corroborating, list) or not corroborating:
            _add(issues, "EDITORIAL_CORROBORATION_REQUIRED",
                 f"{path}.corroboratingActorRefs",
                 "An editorial acceptance requires at least one independent "
                 "corroborating editorial actor; one model's opinion is never "
                 "release-authoritative on its own.")
        else:
            for index, reference in enumerate(corroborating):
                _key(reference, f"{path}.corroboratingActorRefs[{index}]", issues)
            if (all(isinstance(item, str) for item in corroborating) and
                    (corroborating != sorted(corroborating) or
                     len(set(corroborating)) != len(corroborating))):
                _add(issues, "EDITORIAL_CORROBORATION_ORDER",
                     f"{path}.corroboratingActorRefs",
                     "Corroborating editorial actors must be sorted and unique.")
            if isinstance(actor_ref, str) and actor_ref in corroborating:
                _add(issues, "EDITORIAL_CORROBORATION_SELF",
                     f"{path}.corroboratingActorRefs",
                     "An editorial actor cannot corroborate itself.")
    elif "corroboratingActorRefs" in value:
        _add(issues, "EDITORIAL_CORROBORATION_FORBIDDEN",
             f"{path}.corroboratingActorRefs",
             "Corroborating actors are recorded only on an editorial acceptance.")

    stage_accept = kind in RELEASE_STAGE_KINDS and decision == "accept"
    accepted_external = _is_member(kind, TIER1_KINDS) and decision == "accept"
    if stage_accept:
        if (type(value.get("scopeVersion")) is not int or
                value.get("scopeVersion") != SCOPE_VERSION):
            _add(issues, "REVIEW_SCOPE_VERSION", f"{path}.scopeVersion",
                 "Accepted stage requires scopeVersion 1.")
        if not isinstance(value.get("scopeDigest"), str) or not DIGEST_RE.fullmatch(
                value.get("scopeDigest", "")):
            _add(issues, "REVIEW_SCOPE_DIGEST", f"{path}.scopeDigest",
                 "Accepted stage requires a full lowercase SHA-256 digest.")
    else:
        for forbidden in ("scopeVersion", "scopeDigest"):
            if forbidden in value:
                _add(issues, "REVIEW_SCOPE_FORBIDDEN", f"{path}.{forbidden}",
                     "Scope fields are allowed only on accepted review stages.")

    if accepted_external:
        pins = value.get("supportingEvidenceDigests")
        if not isinstance(pins, list) or not pins:
            _add(issues, "REVIEW_EVIDENCE_REQUIRED",
                 f"{path}.supportingEvidenceDigests",
                 "Accepted external verification requires pinned evidence digests.")
        else:
            for index, digest in enumerate(pins):
                if not isinstance(digest, str) or not DIGEST_RE.fullmatch(digest):
                    _add(issues, "REVIEW_EVIDENCE_DIGEST",
                         f"{path}.supportingEvidenceDigests[{index}]",
                         "Evidence pin must be a full lowercase SHA-256 digest.")
            if (all(isinstance(pin, str) for pin in pins) and
                    (pins != sorted(pins) or len(set(pins)) != len(pins))):
                _add(issues, "REVIEW_EVIDENCE_ORDER",
                     f"{path}.supportingEvidenceDigests",
                     "Evidence pins must be sorted and unique.")
    elif "supportingEvidenceDigests" in value:
        _add(issues, "REVIEW_EVIDENCE_FORBIDDEN",
             f"{path}.supportingEvidenceDigests",
             "Evidence pins are allowed only on accepted external verification.")

    if decision != "accept" and "note" not in value:
        _add(issues, "REVIEW_NOTE_REQUIRED", f"{path}.note",
             "A non-accept review decision requires a note.")
    if _is_member(kind, {"reopen", "correction"}):
        if decision != "accept":
            _add(issues, "REVIEW_AUDIT_DECISION", f"{path}.decision",
                 "Reopen and correction audit events use decision 'accept'.")
        if "note" not in value:
            _add(issues, "REVIEW_NOTE_REQUIRED", f"{path}.note",
                 "Reopen and correction events require a note.")

    if resolve_registry and nonhuman_stage and isinstance(kind, str):
        # The required role is the stage itself: an actor registered only for
        # editorial review cannot perform reference verification, and neither
        # can one registered only to generate examples.
        _validate_editorial_actor(
            actor_ref, f"{path}.actorRef", kind, context, issues)
        for index, reference in enumerate(
                corroborating if isinstance(corroborating, list) else []):
            _validate_editorial_actor(
                reference, f"{path}.corroboratingActorRefs[{index}]",
                "editorial-review", context, issues)
    if resolve_registry and isinstance(reviewer_ref, str):
        reviewer = context.reviewer_registry.get(reviewer_ref)
        if not isinstance(reviewer, Mapping):
            _add(issues, "REVIEWER_REGISTRY_DANGLING", f"{path}.reviewerRef",
                 "Reviewer reference does not resolve in the private registry.")
        else:
            if reviewer.get("human") is not True:
                _add(issues, "REVIEWER_NOT_HUMAN", f"{path}.reviewerRef",
                     "Only an identified human can create a review event.")
            if (release_mode == SOLO_MAINTAINER_MODE and
                    kind == "product-approval" and decision == "accept"):
                # Solo-maintainer product approval is only meaningful if the
                # owner has recorded that they know which assurance they are
                # accepting.  The stricter human-reviewed chain predates this
                # and needs no new attestation.
                acknowledged = reviewer.get("acknowledgedReleaseModes")
                if (not isinstance(acknowledged, list) or
                        release_mode not in acknowledged):
                    _add(issues, "OWNER_RELEASE_MODE_NOT_ACKNOWLEDGED",
                         f"{path}.reviewerRef",
                         "Product approval under the solo-maintainer mode "
                         "requires the approver's registry record to "
                         "acknowledge that release mode explicitly.")
            roles = reviewer.get("roles", [])
            if kind in RELEASE_STAGE_KINDS and (
                    not isinstance(roles, list) or kind not in roles):
                _add(issues, "REVIEWER_ROLE", f"{path}.reviewerRef",
                     f"Reviewer lacks the required {kind!r} role.")
            elif kind == "correction" and (
                    not isinstance(roles, list) or not (
                        {"correction", "product-approval"} & set(
                            role for role in roles if isinstance(role, str)))):
                _add(issues, "REVIEWER_ROLE", f"{path}.reviewerRef",
                     "Correction events require correction or product authority.")
            elif kind == "reopen" and (
                    not isinstance(roles, list) or not (
                        {"reopen", "product-approval"} & set(
                            role for role in roles if isinstance(role, str)))):
                _add(issues, "REVIEWER_ROLE", f"{path}.reviewerRef",
                     "Reopen events require reopen or product authority.")


def _validate_origin(
        value: Any, path: str, context: ValidationContext,
        issues: list[Issue], *, fixture_mode: bool,
        resolve_registry: bool) -> None:
    allowed = {
        "kind", "authorRef", "authoredAt", "repositorySource", "generatorRef",
        "adoptedAt"}
    if not _closed_object(value, path, {"kind"}, allowed, issues):
        return
    kind = value.get("kind")
    origin_kinds = set(ORIGIN_KINDS)
    if fixture_mode:
        origin_kinds.add("specification-fixture")
    _enum(kind, origin_kinds, f"{path}.kind", issues)
    if _is_member(kind, {"original", "specification-fixture"}):
        for required in ("authorRef", "authoredAt"):
            if required not in value:
                _add(issues, "SCHEMA_REQUIRED", f"{path}.{required}",
                     "Original example origin requires this field.")
        author_ref = value.get("authorRef")
        _key(author_ref, f"{path}.authorRef", issues)
        _date(value.get("authoredAt"), f"{path}.authoredAt", issues, context.today)
        for forbidden in ("repositorySource", "generatorRef", "adoptedAt"):
            if forbidden in value:
                _add(issues, "ORIGIN_REPOSITORY_FORBIDDEN", f"{path}.{forbidden}",
                     "Original examples must not carry repository-reuse or "
                     "editorial-generation fields.")
        if resolve_registry and kind == "original" and isinstance(author_ref, str):
            author = context.author_registry.get(author_ref)
            if not isinstance(author, Mapping):
                _add(issues, "AUTHOR_REGISTRY_DANGLING", f"{path}.authorRef",
                     "Original-example author does not resolve in the private registry.")
            elif author.get("human") is not True:
                _add(issues, "AUTHOR_NOT_HUMAN", f"{path}.authorRef",
                     "Original learner examples require an identified human author.")
    elif kind == "editorial-generated":
        # Not repository reuse and not human authorship: a sentence drafted
        # through the project's own editorial workflow by a nonhuman actor.
        # It is never described as authored by a person.
        for required in ("generatorRef", "adoptedAt"):
            if required not in value:
                _add(issues, "SCHEMA_REQUIRED", f"{path}.{required}",
                     "Editorial-generated origin requires this field.")
        generator_ref = value.get("generatorRef")
        _key(generator_ref, f"{path}.generatorRef", issues)
        _date(value.get("adoptedAt"), f"{path}.adoptedAt", issues, context.today)
        for forbidden in ("authorRef", "authoredAt", "repositorySource"):
            if forbidden in value:
                _add(issues, "ORIGIN_EDITORIAL_FIELD_FORBIDDEN",
                     f"{path}.{forbidden}",
                     "An editorial-generated example must not claim a human "
                     "author or a repository source.")
        if resolve_registry:
            _validate_editorial_actor(
                generator_ref, f"{path}.generatorRef", "example-generation",
                context, issues)
    elif kind == "repository-reuse":
        if "repositorySource" not in value:
            _add(issues, "ORIGIN_REPOSITORY_REQUIRED", f"{path}.repositorySource",
                 "Repository reuse requires an exact repositorySource.")
        else:
            _validate_repository_source(value["repositorySource"],
                                        f"{path}.repositorySource", issues)
        for forbidden in ("authorRef", "authoredAt", "generatorRef", "adoptedAt"):
            if forbidden in value:
                _add(issues, "ORIGIN_AUTHOR_FORBIDDEN", f"{path}.{forbidden}",
                     "Repository reuse must not carry original-author or "
                     "editorial-generation fields.")


def _validate_example(
        value: Any, path: str, context: ValidationContext,
        issues: list[Issue], *, fixture_mode: bool,
        resolve_registry: bool) -> None:
    required = {"id", "key", "pl", "en", "origin", "audioEligible"}
    if not _closed_object(value, path, required, required, issues):
        return
    _id_syntax(value.get("id"), "example", f"{path}.id", issues)
    _key(value.get("key"), f"{path}.key", issues)
    _nonempty_string(value.get("pl"), f"{path}.pl", issues, 3)
    _nonempty_string(value.get("en"), f"{path}.en", issues, 3)
    _validate_origin(value.get("origin"), f"{path}.origin", context, issues,
                     fixture_mode=fixture_mode, resolve_registry=resolve_registry)
    _boolean(value.get("audioEligible"), f"{path}.audioEligible", issues)
    if isinstance(value.get("origin"), dict) and (
            value["origin"].get("kind") == "repository-reuse"):
        _resolve_repository_reuse(value, path, context, issues)


def _validate_content_ref(
        value: Any, path: str, context: ValidationContext,
        issues: list[Issue], *, resolve_repository: bool) -> None:
    required = {"kind", "id", "purpose"}
    if not _closed_object(value, path, required, required, issues):
        return
    kind = value.get("kind")
    _enum(kind, CONTENT_KINDS, f"{path}.kind", issues)
    entity_id = value.get("id")
    if not isinstance(entity_id, str) or not SAFE_ID_RE.fullmatch(entity_id):
        _add(issues, "CONTENT_REF_ID", f"{path}.id", "Content reference ID is invalid.")
    _enum(value.get("purpose"), CONTENT_PURPOSES, f"{path}.purpose", issues)
    if resolve_repository and isinstance(entity_id, str):
        index = context.repository_index
        if index is None:
            _add(issues, "REPOSITORY_INDEX_REQUIRED", path,
                 "Content reference resolution requires a repository index.")
        elif index.issues:
            _add(issues, "REPOSITORY_INDEX_INVALID", path,
                 "Repository index contains source or duplicate-ID errors.")
        else:
            entity = index.get(entity_id)
            if entity is None:
                _add(issues, "CONTENT_REF_DANGLING", f"{path}.id",
                     "Content reference does not resolve.")
            elif entity.kind != kind:
                _add(issues, "CONTENT_REF_KIND", f"{path}.kind",
                     f"Content reference resolves as {entity.kind}, not {kind}.")


def _validate_complement(
        value: Any, path: str, relation_type: Any,
        issues: list[Issue]) -> None:
    base_required = {"type", "required", "role"}
    base_allowed = base_required | {
        "case", "preposition", "clauseKind", "questionOverridePl"}
    if not _closed_object(value, path, base_required, base_allowed, issues):
        return
    complement_type = value.get("type")
    _enum(complement_type, COMPLEMENT_TYPES, f"{path}.type", issues)
    _boolean(value.get("required"), f"{path}.required", issues)
    role = value.get("role")
    _enum(role, ROLES, f"{path}.role", issues)
    if "questionOverridePl" in value:
        _string_list(value["questionOverridePl"], f"{path}.questionOverridePl",
                     issues, min_items=1, unique=True)

    required_by_type: set[str]
    forbidden_by_type: set[str]
    if complement_type == "case":
        required_by_type = {"case"}
        forbidden_by_type = {"preposition", "clauseKind"}
        case_id = value.get("case")
        _enum(case_id, DIRECT_CASE_IDS, f"{path}.case", issues)
        if _is_member(case_id, {"locative", "vocative"}):
            _add(issues, "DIRECT_CASE_FORBIDDEN", f"{path}.case",
                 "Direct Locative and Vocative complements are forbidden.")
        if case_id == "nominative":
            if not _is_member(
                    relation_type, {"constructional-frame", "subject-experiencer"}):
                _add(issues, "NOMINATIVE_RELATION", path,
                     "Direct Nominative requires constructional or subject-experiencer relation.")
            if not _is_member(role, {"subject", "predicate"}):
                _add(issues, "NOMINATIVE_ROLE", f"{path}.role",
                     "Direct Nominative role must be subject or predicate.")
    elif complement_type == "preposition-case":
        required_by_type = {"preposition", "case"}
        forbidden_by_type = {"clauseKind"}
        preposition = value.get("preposition")
        if not isinstance(preposition, str) or not PREPOSITION_RE.fullmatch(preposition):
            _add(issues, "PREPOSITION_INVALID", f"{path}.preposition",
                 "Preposition must be one exact lowercase NFC Polish word.")
        _enum(value.get("case"), PREPOSITION_CASE_IDS, f"{path}.case", issues)
    elif complement_type == "infinitive":
        required_by_type = set()
        forbidden_by_type = {"case", "preposition", "clauseKind"}
    elif complement_type == "clause":
        required_by_type = {"clauseKind"}
        forbidden_by_type = {"case", "preposition"}
        _enum(value.get("clauseKind"), CLAUSE_KINDS, f"{path}.clauseKind", issues)
    else:
        return
    for required in required_by_type:
        if required not in value:
            _add(issues, "COMPLEMENT_FIELD_REQUIRED", f"{path}.{required}",
                 "Complement type requires this field.")
    for forbidden in forbidden_by_type:
        if forbidden in value:
            _add(issues, "COMPLEMENT_FIELD_FORBIDDEN", f"{path}.{forbidden}",
                 "Complement type forbids this field.")


def _validate_cefr(
        value: Any, path: str, teaching_status: Any,
        issues: list[Issue]) -> None:
    allowed = {"recognition", "production"}
    if not _closed_object(value, path, {"recognition"}, allowed, issues):
        return
    recognition = value.get("recognition")
    production = value.get("production")
    _enum(recognition, set(CEFR_LEVELS), f"{path}.recognition", issues)
    if "production" in value:
        _enum(production, set(CEFR_LEVELS), f"{path}.production", issues)
        if recognition in CEFR_LEVELS and production in CEFR_LEVELS and (
                CEFR_LEVELS.index(production) < CEFR_LEVELS.index(recognition)):
            _add(issues, "CEFR_ORDER", path,
                 "Production CEFR must not precede recognition CEFR.")
    if teaching_status == "active-production":
        if not _is_member(production, {"A1", "A2", "B1"}):
            _add(issues, "ACTIVE_PRODUCTION_CEFR", path,
                 "Active production requires an A1-B1 production CEFR.")
    elif _is_member(
            teaching_status, {"recognition-only", "deferred"}) and "production" in value:
        _add(issues, "NONPRODUCTION_CEFR", f"{path}.production",
             f"{teaching_status} must omit production CEFR.")


def _validate_usage(
        value: Any, path: str, teaching_status: Any,
        issues: list[Issue]) -> None:
    required = {"priority", "register"}
    allowed = required | {"note"}
    if not _closed_object(value, path, required, allowed, issues):
        return
    priority = value.get("priority")
    _enum(priority, USAGE_PRIORITIES, f"{path}.priority", issues)
    _enum(value.get("register"), REGISTERS, f"{path}.register", issues)
    if "note" in value:
        _nonempty_string(value["note"], f"{path}.note", issues, 1, 240)
    if priority == "limited":
        if "note" not in value:
            _add(issues, "LIMITED_NOTE_REQUIRED", f"{path}.note",
                 "Limited usage requires a learner-facing note.")
        if teaching_status == "active-production":
            _add(issues, "LIMITED_ACTIVE_PRODUCTION", path,
                 "Limited usage cannot be active-production in the A1-B1 corpus.")


def _validate_error_note(
        value: Any, path: str, evidence_count: int,
        issues: list[Issue], *, runtime: bool) -> None:
    required = {"kind", "incorrectForm", "guidanceEn"}
    allowed = set(required) if runtime else required | {"evidenceRefs"}
    if not _closed_object(value, path, required, allowed, issues):
        return
    kind = value.get("kind")
    _enum(kind, ERROR_KINDS, f"{path}.kind", issues)
    _nonempty_string(value.get("incorrectForm"), f"{path}.incorrectForm", issues)
    _nonempty_string(value.get("guidanceEn"), f"{path}.guidanceEn", issues, 3)
    if runtime:
        return
    refs = value.get("evidenceRefs")
    if kind == "documented-common-error" and not isinstance(refs, list):
        _add(issues, "ERROR_EVIDENCE_REQUIRED", f"{path}.evidenceRefs",
             "Documented common errors require evidence references.")
    if "evidenceRefs" in value:
        if not isinstance(refs, list) or not refs:
            _add(issues, "ERROR_EVIDENCE_ARRAY", f"{path}.evidenceRefs",
                 "Evidence references must be a non-empty array.")
        else:
            if all(type(reference) is int for reference in refs) and len(set(refs)) != len(refs):
                _add(issues, "ERROR_EVIDENCE_UNIQUE", f"{path}.evidenceRefs",
                     "Evidence references must be unique.")
            for index, reference in enumerate(refs):
                if type(reference) is not int or not 0 <= reference < evidence_count:
                    _add(issues, "ERROR_EVIDENCE_DANGLING",
                         f"{path}.evidenceRefs[{index}]",
                         "Evidence index does not resolve in this pattern.")


def _validate_relation_roles(
        relation_type: Any, complements: Any, path: str,
        issues: list[Issue]) -> None:
    if not isinstance(complements, list):
        return
    roles = [item.get("role") for item in complements if isinstance(item, dict)]
    if relation_type == "means-method":
        if "means" not in roles:
            _add(issues, "MEANS_ROLE_REQUIRED", path,
                 "means-method requires a complement with role 'means'.")
    if relation_type == "subject-experiencer":
        if "subject" not in roles or "experiencer" not in roles:
            _add(issues, "EXPERIENCER_ROLES_REQUIRED", path,
                 "subject-experiencer requires subject and experiencer roles.")


def declared_release_mode(record: Mapping[str, Any] | Any) -> str:
    """Return the declared release mode, defaulting to the strictest chain.

    Every value is normalised here, including malformed ones: a container, a
    number, a Boolean or an unknown string all resolve to the strictest chain
    rather than raising.  The malformed value itself is reported as a schema
    issue by the closed-enum check at each entry point, so nothing is silently
    accepted -- but no caller has to defend against an unhashable value, and no
    tooling entry point can be crashed by one.
    """
    if not isinstance(record, Mapping):
        return DEFAULT_RELEASE_MODE
    mode = record.get("releaseMode", DEFAULT_RELEASE_MODE)
    # Membership is tested only after the value is known to be a string: an
    # unhashable list or dict would otherwise raise inside the dict lookup.
    if not isinstance(mode, str) or mode not in RELEASE_MODES:
        return DEFAULT_RELEASE_MODE
    return mode


def release_mode_chain(release_mode: Any) -> tuple[str, ...]:
    """Return the stage chain for a mode, fail-closed on any malformed value."""
    if not isinstance(release_mode, str):
        return RELEASE_MODES[DEFAULT_RELEASE_MODE]
    return RELEASE_MODES.get(release_mode, RELEASE_MODES[DEFAULT_RELEASE_MODE])


def normalized_release_mode(release_mode: Any) -> str:
    """Normalise any mode value, including a missing one, to a known mode.

    A malformed or unknown value resolves to the strictest chain here exactly
    as it does in :func:`declared_release_mode`; the value itself is still
    reported by the closed-enum check at whichever entry point carried it.
    """
    if isinstance(release_mode, str) and release_mode in RELEASE_MODES:
        return release_mode
    return DEFAULT_RELEASE_MODE


def nonhuman_stage_kinds(release_mode: Any) -> frozenset[str]:
    """Return the stage kinds a mode records against a nonhuman actor."""
    return MODE_NONHUMAN_STAGE_KINDS[normalized_release_mode(release_mode)]


def forbidden_stage_kinds(release_mode: Any) -> frozenset[str]:
    """Return the stage kinds a mode refuses to carry at all."""
    return MODE_FORBIDDEN_STAGE_KINDS[normalized_release_mode(release_mode)]


@dataclass(frozen=True)
class ReviewCurrency:
    """The release-authoritative reading of one pattern's review history."""

    state: str
    verification_pins: frozenset[str]
    human_native_review_current: bool
    # Phase 4E.1.  Whether an identified *human* external verification still
    # stands over this pattern's tier-1 scope.  A nonhuman reference
    # verification never sets it, so a release can name its genuine human
    # verification coverage without implying any where none exists.
    human_verification_current: bool = False


def _derive_review_currency(
        events: Any, release_mode: str, scope_digests: Mapping[str, Any],
        current_evidence_digests: set[str],
        evidence_by_digest: Mapping[str, Mapping[str, Any]], *,
        diagnostics: list[tuple[str, str]] | None = None) -> ReviewCurrency:
    """Replay an append-only history into the state its digests still support.

    One derivation serves both the editorial record and the frozen release
    envelope so the two can never disagree about what a history proves.

    The three locked scope tiers are replayed in order.  Only the declared
    mode's own chain kind can establish currency at a tier; a stage event from
    the other chain -- a genuine human native review of a solo-maintainer
    pattern, say -- is preserved and may still *block*, but never substitutes
    for the required stage.  That asymmetry is the whole point: human review
    strengthens a release when it exists and is never fabricated when it does
    not.
    """
    chain = release_mode_chain(release_mode)
    current = [False, False, False]
    verification_pins: set[str] = set()
    human_native_current = False
    human_verification_current = False
    terminal: str | None = None
    if not isinstance(events, list):
        events = []
    for event in events:
        if not isinstance(event, dict):
            continue
        kind = event.get("kind")
        decision = event.get("decision")
        if kind == "correction":
            continue
        if kind == "reopen":
            current = [False, False, False]
            verification_pins.clear()
            human_native_current = False
            human_verification_current = False
            terminal = None
            continue
        if kind not in RELEASE_STAGE_KINDS:
            continue
        index = STAGE_TIER_INDEX[STAGE_SCOPE_TIER[kind]]
        if decision == "defer":
            terminal = "deferred"
            continue
        if decision == "reject":
            terminal = "rejected"
            continue
        if decision == "changes-requested":
            # An unresolved request for changes invalidates its own tier and
            # everything built on top of it, whichever chain raised it.
            terminal = None
            for tier in range(index, len(current)):
                current[tier] = False
            if index == 0:
                verification_pins.clear()
                human_verification_current = False
            if index <= 1:
                human_native_current = False
            continue
        if decision != "accept":
            continue
        on_chain = chain[index] == kind
        digest_current = bool(
            type(event.get("scopeVersion")) is int and
            event.get("scopeVersion") == SCOPE_VERSION and
            event.get("scopeDigest") == scope_digests.get(
                STAGE_SCOPE_TIER[kind]))
        if index == 0:
            pins = event.get("supportingEvidenceDigests")
            pins_resolve = bool(
                isinstance(pins, list) and pins and
                all(isinstance(pin, str) and pin in current_evidence_digests
                    for pin in pins))
            contemporary = bool(pins_resolve and any(
                evidence_by_digest.get(pin, {}).get("sourceKind") in
                CONTEMPORARY_SOURCE_KINDS for pin in pins))
            if diagnostics is not None and pins_resolve and not contemporary:
                diagnostics.append((
                    "REVIEW_CONTEMPORARY_EVIDENCE_REQUIRED",
                    "Current verification acceptance must pin contemporary "
                    "reference or corpus evidence."))
            source_backed = True
            if kind == "reference-verification":
                source_backed = bool(pins_resolve and any(
                    evidence_by_digest.get(pin, {}).get("factType") in
                    REFERENCE_PATTERN_FACT_TYPES for pin in pins))
                if diagnostics is not None and pins_resolve and not source_backed:
                    diagnostics.append((
                        "REFERENCE_PATTERN_EVIDENCE_REQUIRED",
                        "A reference verification must pin source evidence "
                        "about the pattern or the meaning itself, not "
                        "headword presence alone."))
            accepted = bool(
                digest_current and pins_resolve and contemporary and source_backed)
            if kind == "external-verification":
                # Recorded whether or not this chain requires it, exactly as
                # human native review is at tier 2, so a solo release that did
                # attract a genuine human external verification can say so.  A
                # nonhuman reference verification never sets it, and a later
                # on-chain acceptance of the *other* tier-1 kind does not clear
                # it: both statements stand over the same scope, and only an
                # explicit change request or reopen retires this one.
                human_verification_current = accepted
            if not on_chain:
                continue
            terminal = None
            current = [accepted, False, False]
            verification_pins = set(pins) if accepted else set()
            human_native_current = False
            continue
        if index == 1:
            accepted = bool(current[0] and digest_current)
            if kind == "native-linguistic":
                # Recorded whether or not this chain requires it, so a release
                # can report genuine human native coverage without depending
                # on it.  Requiring current[0] keeps the flag conservative: it
                # never claims more coverage than the chain itself proves.
                human_native_current = accepted
            if not on_chain:
                continue
            terminal = None
            current[1] = accepted
            current[2] = False
            continue
        if not on_chain:
            continue
        terminal = None
        current[2] = bool(current[1] and digest_current)

    if terminal is not None:
        return ReviewCurrency(
            terminal, frozenset(), human_native_current,
            human_verification_current)
    if current[2]:
        state = STAGE_STATE[chain[2]]
    elif current[1]:
        state = STAGE_STATE[chain[1]]
    elif current[0]:
        state = STAGE_STATE[chain[0]]
    else:
        state = "research"
    return ReviewCurrency(
        state, frozenset(verification_pins), human_native_current,
        human_verification_current)


def _replay_actor_independence(
        events: Sequence[Any], event_path: str, issues: list[Issue]) -> None:
    """Refuse one nonhuman identity performing both nonhuman tiers.

    The solo chain's assurance is corroboration between two independent
    workflows: one that checks the claim against authoritative references, and
    a separate one that reviews the resulting learner-facing treatment.  One
    identity doing both is a single opinion recorded twice, so the rule is the
    strict one -- the reference actor may not reappear as the editorial actor
    or among its corroborators anywhere in the pattern's history.
    """
    reference_actors: set[str] = set()
    editorial_actors: set[str] = set()
    for event in events:
        if not isinstance(event, dict) or event.get("decision") != "accept":
            continue
        kind = event.get("kind")
        actor_ref = event.get("actorRef")
        if kind == "reference-verification":
            if isinstance(actor_ref, str):
                reference_actors.add(actor_ref)
        elif kind == "editorial-review":
            if isinstance(actor_ref, str):
                editorial_actors.add(actor_ref)
            corroborating = event.get("corroboratingActorRefs")
            for reference in corroborating if isinstance(
                    corroborating, list) else []:
                if isinstance(reference, str):
                    editorial_actors.add(reference)
    shared = sorted(reference_actors & editorial_actors)
    if shared:
        _add(issues, "REVIEW_ACTOR_INDEPENDENCE", event_path,
             f"Nonhuman actors {shared!r} perform both reference verification "
             "and editorial review for this pattern; the two tiers exist to "
             "corroborate each other and require distinct actor identities.")


def _replay_review_order(
        events: Sequence[Any], release_mode: str, path: str,
        event_path: str, issues: list[Issue], *,
        context: ValidationContext | None) -> None:
    """Check append-only ordering and locked stage order for one history.

    ``context`` is supplied only where the private registries are resolvable;
    the frozen envelope deliberately cannot reach them.
    """
    chain = release_mode_chain(release_mode)
    history_state = "research"
    deferred_reopen_pending = False
    previous_date: str | None = None
    # Per tier: the digest of the last on-chain acceptance that is still
    # standing, or None once an explicit governance event has reset that tier.
    # A second acceptance of a tier whose standing acceptance already covers
    # the identical scope is a duplicate: nothing that tier reviews can have
    # changed, so the second event proves nothing the first did not.
    standing_digest: list[Any] = [None, None, None]

    def reset_tiers(lowest: int) -> None:
        for tier_index in range(lowest, len(standing_digest)):
            standing_digest[tier_index] = None

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            continue
        current_path = f"{event_path}[{index}]"
        reviewed_at = event.get("reviewedAt")
        if (isinstance(reviewed_at, str) and previous_date is not None and
                reviewed_at < previous_date):
            _add(issues, "REVIEW_EVENT_ORDER", f"{current_path}.reviewedAt",
                 "Append-only review event dates must be nondecreasing.")
        if isinstance(reviewed_at, str):
            previous_date = reviewed_at
        kind = event.get("kind")
        decision = event.get("decision")
        if kind == "correction":
            # An owner-authorized correction is the architecture's existing
            # licence to change released material, so it legitimately reopens
            # every tier to re-review.
            reset_tiers(0)
            continue
        if kind == "reopen":
            reset_tiers(0)
            if not _is_member(history_state, {"deferred", "rejected"}):
                _add(issues, "REVIEW_REOPEN_ORDER", current_path,
                     "Reopen is valid only after deferred or rejected state.")
            if history_state == "deferred":
                deferred_reopen_pending = True
            if history_state == "rejected" and context is not None:
                reviewer_ref = event.get("reviewerRef")
                reviewer = context.reviewer_registry.get(
                    reviewer_ref, {}) if isinstance(reviewer_ref, str) else {}
                roles = reviewer.get("roles", []) if isinstance(
                    reviewer, Mapping) else []
                if not isinstance(reviewer, Mapping) or not isinstance(
                        roles, list) or "product-approval" not in roles:
                    _add(issues, "REVIEW_REJECTED_REOPEN_AUTHORITY", current_path,
                         "A rejected treatment requires an owner-authorized reopen.")
            history_state = "research"
            continue
        if kind not in RELEASE_STAGE_KINDS:
            continue
        tier = STAGE_TIER_INDEX[STAGE_SCOPE_TIER[kind]]
        if _is_member(history_state, {"deferred", "rejected"}):
            _add(issues, "REVIEW_REOPEN_REQUIRED", current_path,
                 "A deferred or rejected treatment requires an explicit reopen "
                 "before another stage event.")
            continue
        if decision == "defer":
            history_state = "deferred"
            reset_tiers(0)
            continue
        if decision == "reject":
            history_state = "rejected"
            reset_tiers(0)
            continue
        if decision == "changes-requested":
            history_state = (
                "research" if tier == 0 else STAGE_STATE[chain[tier - 1]])
            reset_tiers(tier)
            continue
        if decision != "accept":
            continue
        if chain[tier] != kind:
            # Supplementary evidence from the other chain: recorded, never
            # chain-advancing, and never renamed into the declared chain.
            continue
        accepted_digest = event.get("scopeDigest")
        if (standing_digest[tier] is not None and
                accepted_digest == standing_digest[tier]):
            # Re-accepting a tier that already stands over the identical scope
            # is not evidence.  Legitimate re-review is always preceded by
            # something that changed: a correction, a reopen, a request for
            # changes, or an edit that moves the scope digest.
            _add(issues, "REVIEW_DUPLICATE_STAGE_ACCEPTANCE", current_path,
                 f"{kind!r} is already accepted for this exact scope with no "
                 "intervening correction, reopen, change request or scope "
                 "change; a repeated acceptance establishes nothing.")
            continue
        standing_digest[tier] = accepted_digest
        # A fresh acceptance at this tier reopens everything built on it.
        reset_tiers(tier + 1)
        if tier == len(standing_digest) - 1:
            # Owner approval closes the review round.  A later round may
            # legitimately re-verify and re-review the same material from the
            # top; what stays forbidden is repeating a stage *within* a round,
            # which is what the checks above reject.  The product tier itself
            # is deliberately left standing, so a repeated approval is still
            # caught until a new verification reopens it.
            reset_tiers(0)
            standing_digest[tier] = accepted_digest
        if tier == 0:
            history_state = STAGE_STATE[kind]
            deferred_reopen_pending = False
        elif history_state != STAGE_STATE[chain[tier - 1]]:
            _add(issues, "REVIEW_STAGE_ORDER", current_path,
                 f"{kind!r} acceptance requires a preceding "
                 f"{chain[tier - 1]!r} acceptance.")
        else:
            history_state = STAGE_STATE[kind]

    if deferred_reopen_pending:
        _add(issues, "REVIEW_DEFERRED_REOPEN_EXTERNAL_REQUIRED", path,
             "Reopening a deferred treatment requires a new verification "
             "acceptance before the history can advance.")

    _replay_actor_independence(events, event_path, issues)


def _review_history_state(
        lemma: Mapping[str, Any], meaning: Mapping[str, Any],
        pattern: Mapping[str, Any], path: str, context: ValidationContext,
        issues: list[Issue]) -> None:
    events = pattern.get("reviewEvents")
    if not isinstance(events, list):
        return
    release_mode = declared_release_mode(pattern)

    _replay_review_order(
        events, release_mode, path, f"{path}.reviewEvents", issues,
        context=context)

    stage_roles_by_reviewer: dict[str, set[str]] = {}
    for event in events:
        if not isinstance(event, dict) or event.get("decision") != "accept":
            continue
        kind = event.get("kind")
        reviewer_ref = event.get("reviewerRef")
        if kind in RELEASE_STAGE_KINDS and isinstance(reviewer_ref, str):
            stage_roles_by_reviewer.setdefault(reviewer_ref, set()).add(kind)
    for reviewer_ref, roles_used in stage_roles_by_reviewer.items():
        if len(roles_used) < 2:
            continue
        reviewer = context.reviewer_registry.get(reviewer_ref)
        if not isinstance(reviewer, Mapping) or (
                reviewer.get("ownerAllowsMultipleRoles") is not True):
            _add(issues, "REVIEWER_MULTI_ROLE_NOT_AUTHORIZED", path,
                 f"Reviewer {reviewer_ref!r} performs multiple review stages "
                 "without an explicit owner allowance in the private registry.")

    try:
        current_scope_digests = {
            stage: review_scope_digest(stage, lemma, meaning, pattern)
            for stage in STAGE_KINDS
        }
        current_evidence_sequence: list[str | None] = []
        current_evidence_records: dict[str, Mapping[str, Any]] = {}
        for record in pattern.get("evidence", []):
            if not isinstance(record, dict):
                current_evidence_sequence.append(None)
                continue
            digest = evidence_digest(record)
            current_evidence_sequence.append(digest)
            current_evidence_records[digest] = record
        current_evidence_digests = set(current_evidence_records)
    except (KeyError, TypeError, ValueError):
        return

    diagnostics: list[tuple[str, str]] = []
    currency = _derive_review_currency(
        events, release_mode, current_scope_digests, current_evidence_digests,
        current_evidence_records, diagnostics=diagnostics)
    for code, message in diagnostics:
        _add(issues, code, path, message)
    expected_state = currency.state
    current_external_pins = currency.verification_pins
    if expected_state in REVIEWED_STATES:
        reviewed_error_notes = pattern.get("errorNotes", [])
        if not isinstance(reviewed_error_notes, list):
            reviewed_error_notes = []
        for note_index, note in enumerate(reviewed_error_notes):
            refs = note.get("evidenceRefs", []) if isinstance(note, dict) else []
            if not isinstance(refs, list):
                continue
            for ref_index, reference in enumerate(refs):
                if (type(reference) is int and
                        0 <= reference < len(current_evidence_sequence)):
                    referenced_digest = current_evidence_sequence[reference]
                    if referenced_digest not in current_external_pins:
                        _add(issues, "ERROR_EVIDENCE_NOT_EXTERNALLY_PINNED",
                             f"{path}.errorNotes[{note_index}].evidenceRefs["
                             f"{ref_index}]",
                             "Evidence used by a currently reviewed error claim "
                             "must be pinned by the current external acceptance.")
    if pattern.get("reviewState") != expected_state:
        _add(issues, "REVIEW_STATE_MISMATCH", f"{path}.reviewState",
             f"Current event history and digests require {expected_state!r}, "
             f"not {pattern.get('reviewState')!r}.")


def _validate_pattern(
        value: Any, path: str, lemma: Mapping[str, Any],
        meaning: Mapping[str, Any], context: ValidationContext,
        issues: list[Issue], entities: list[_EntityInfo], *,
        fixture_mode: bool, resolve_registries: bool) -> None:
    required = {
        "id", "key", "relationType", "complements", "cefr",
        "teachingStatus", "usage", "learnerExplanationEn",
        "activityEligibility", "evidence", "reviewState", "reviewEvents",
    }
    allowed = required | {
        "aspectEquivalentPatternIds", "examples", "contentRefs", "errorNotes",
        "releaseMode", "requiredLexicalItems"}
    if not _closed_object(value, path, required, allowed, issues):
        return
    # Absent means the strictest chain, so no existing record silently becomes
    # eligible for a weaker one.  An unrecognised value fails closed here and
    # again below, where an unknown mode can establish no stage at all.
    if "releaseMode" in value:
        _enum(value.get("releaseMode"), RELEASE_MODES, f"{path}.releaseMode",
              issues)
    release_mode = declared_release_mode(value)
    pattern_id = value.get("id")
    pattern_key = value.get("key")
    id_ok = _id_syntax(pattern_id, "pattern", f"{path}.id", issues)
    key_ok = _key(pattern_key, f"{path}.key", issues)
    if id_ok and key_ok and pattern_id not in context.allocation_registry:
        try:
            expected = allocate_pattern_id(
                meaning["id"], lemma["canonicalLemma"], meaning["key"], pattern_key)
            if pattern_id != expected:
                _add(issues, "ID_RECOMPUTATION", f"{path}.id",
                     f"Pattern ID must recompute exactly as {expected!r}.")
        except (KeyError, TypeError, ValueError):
            pass
    if isinstance(pattern_id, str):
        entities.append(_EntityInfo(
            "pattern", pattern_id, meaning.get("id"),
            pattern_key if isinstance(pattern_key, str) else None,
            path, value, lemma, meaning, value))

    relation_type = value.get("relationType")
    _enum(relation_type, RELATION_TYPES, f"{path}.relationType", issues)
    complements = value.get("complements")
    if not isinstance(complements, list) or not complements:
        _add(issues, "COMPLEMENTS_REQUIRED", f"{path}.complements",
             "Pattern requires a non-empty ordered complement array.")
    else:
        for index, complement in enumerate(complements):
            _validate_complement(
                complement, f"{path}.complements[{index}]", relation_type, issues)
        _validate_relation_roles(relation_type, complements,
                                 f"{path}.complements", issues)

    teaching_status = value.get("teachingStatus")
    _enum(teaching_status, TEACHING_STATUSES, f"{path}.teachingStatus", issues)
    _validate_cefr(value.get("cefr"), f"{path}.cefr", teaching_status, issues)
    _validate_usage(value.get("usage"), f"{path}.usage", teaching_status, issues)
    _nonempty_string(value.get("learnerExplanationEn"),
                     f"{path}.learnerExplanationEn", issues, 3)
    if "requiredLexicalItems" in value:
        _validate_required_lexical_items(
            value["requiredLexicalItems"], f"{path}.requiredLexicalItems", issues)

    eligibility = value.get("activityEligibility")
    eligibility_ok = _string_list(
        eligibility, f"{path}.activityEligibility", issues, unique=True,
        allowed=ACTIVITY_KEYS)
    if isinstance(eligibility, list):
        eligibility_values = {
            item for item in eligibility if isinstance(item, str)}
        if teaching_status == "recognition-only" and (
                {"grammar-build", "type-it"} & eligibility_values):
            _add(issues, "RECOGNITION_PRODUCTION_ACTIVITY",
                 f"{path}.activityEligibility",
                 "recognition-only forbids grammar-build and type-it.")
        if teaching_status == "deferred" and eligibility:
            _add(issues, "DEFERRED_ACTIVITY", f"{path}.activityEligibility",
                 "Deferred teaching status cannot expose learner activities.")
        if eligibility and value.get("reviewState") != "approved":
            _add(issues, "UNAPPROVED_ACTIVITY", f"{path}.activityEligibility",
                 "Learner activity eligibility requires approved review state.")

    evidence = value.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        _add(issues, "EVIDENCE_REQUIRED", f"{path}.evidence",
             "Every editorial pattern candidate requires evidence.")
        evidence_count = 0
    else:
        evidence_count = len(evidence)
        seen_evidence_digests: set[str] = set()
        for index, record in enumerate(evidence):
            _validate_evidence(
                record, f"{path}.evidence[{index}]", context, issues,
                resolve_registry=resolve_registries)
            if isinstance(record, dict):
                try:
                    digest = evidence_digest(record)
                except (TypeError, ValueError, UnicodeError):
                    continue
                if digest in seen_evidence_digests:
                    _add(issues, "EVIDENCE_DUPLICATE_DIGEST",
                         f"{path}.evidence[{index}]",
                         "Evidence records must have unique complete-record digests "
                         "so removal of a pinned record is detectable.")
                seen_evidence_digests.add(digest)

    review_state = value.get("reviewState")
    _enum(review_state, REVIEW_STATES, f"{path}.reviewState", issues)
    events = value.get("reviewEvents")
    if not isinstance(events, list):
        _add(issues, "SCHEMA_ARRAY", f"{path}.reviewEvents",
             "reviewEvents must be an array.")
    else:
        for index, event in enumerate(events):
            _validate_review_event(
                event, f"{path}.reviewEvents[{index}]", context, issues,
                resolve_registry=resolve_registries,
                release_mode=release_mode)

    examples = value.get("examples", [])
    if "examples" in value and not isinstance(examples, list):
        _add(issues, "SCHEMA_ARRAY", f"{path}.examples", "examples must be an array.")
        examples = []
    example_keys: set[str] = set()
    for index, example in enumerate(examples):
        example_path = f"{path}.examples[{index}]"
        _validate_example(
            example, example_path, context, issues, fixture_mode=fixture_mode,
            resolve_registry=resolve_registries)
        if not isinstance(example, dict):
            continue
        example_id = example.get("id")
        example_key = example.get("key")
        if isinstance(example_key, str):
            if example_key in example_keys:
                _add(issues, "SIBLING_KEY_DUPLICATE", f"{example_path}.key",
                     "Example key is duplicated within its pattern.")
            example_keys.add(example_key)
        if isinstance(example_id, str) and isinstance(pattern_id, str):
            if (example_id not in context.allocation_registry and
                    isinstance(example_key, str) and
                    KEY_RE.fullmatch(example_key)):
                try:
                    expected = allocate_example_id(pattern_id, example_key)
                    if example_id != expected:
                        _add(issues, "ID_RECOMPUTATION", f"{example_path}.id",
                             f"Example ID must recompute exactly as {expected!r}.")
                except ValueError:
                    pass
            entities.append(_EntityInfo(
                "example", example_id, pattern_id,
                example_key if isinstance(example_key, str) else None,
                example_path, example, lemma, meaning, value))
        if example.get("audioEligible") is True and not (
                review_state == "approved" and (
                    (isinstance(eligibility, list) and
                     "listening" in eligibility) or
                    context.pronunciation_playback_authorized)):
            _add(issues, "AUDIO_NOT_AUTHORIZED", f"{example_path}.audioEligible",
                 "Audio requires an approved owning pattern and either the "
                 "explicit pronunciation-playback policy or Listening eligibility.")

    if eligibility_ok and isinstance(eligibility, list) and (
            {item for item in eligibility if isinstance(item, str)} &
            {"listening", "grammar-choose", "grammar-build", "type-it"}) and not examples:
        _add(issues, "ACTIVITY_EXAMPLE_REQUIRED", f"{path}.examples",
             "Listening and active grammar use require a reviewed sentence example.")

    aspect_equivalents = value.get("aspectEquivalentPatternIds", [])
    if "aspectEquivalentPatternIds" in value:
        _string_list(aspect_equivalents, f"{path}.aspectEquivalentPatternIds",
                     issues, unique=True)
        if isinstance(aspect_equivalents, list):
            for index, target in enumerate(aspect_equivalents):
                _id_syntax(target, "pattern",
                           f"{path}.aspectEquivalentPatternIds[{index}]", issues)

    content_refs = value.get("contentRefs", [])
    if "contentRefs" in value and not isinstance(content_refs, list):
        _add(issues, "SCHEMA_ARRAY", f"{path}.contentRefs",
             "contentRefs must be an array.")
    elif isinstance(content_refs, list):
        ref_keys: set[tuple[Any, Any, Any]] = set()
        for index, reference in enumerate(content_refs):
            reference_path = f"{path}.contentRefs[{index}]"
            _validate_content_ref(
                reference, reference_path, context, issues,
                resolve_repository=resolve_registries)
            if isinstance(reference, dict):
                identity = (
                    reference.get("kind"), reference.get("id"),
                    reference.get("purpose"))
                if all(isinstance(item, str) for item in identity) and identity in ref_keys:
                    _add(issues, "CONTENT_REF_DUPLICATE", reference_path,
                         "Content references must be unique.")
                if all(isinstance(item, str) for item in identity):
                    ref_keys.add(identity)

    error_notes = value.get("errorNotes", [])
    if "errorNotes" in value and not isinstance(error_notes, list):
        _add(issues, "SCHEMA_ARRAY", f"{path}.errorNotes",
             "errorNotes must be an array.")
    elif isinstance(error_notes, list):
        for index, note in enumerate(error_notes):
            _validate_error_note(
                note, f"{path}.errorNotes[{index}]", evidence_count,
                issues, runtime=False)

    if review_state == "approved" and lemma.get("aspect") == "unresolved":
        _add(issues, "APPROVED_ASPECT_UNRESOLVED", f"{path}.reviewState",
             "Approved patterns require a resolved lemma aspect.")
    if isinstance(events, list):
        _review_history_state(lemma, meaning, value, path, context, issues)


def _validate_hierarchy(
        lemmas: Any, context: ValidationContext, issues: list[Issue], *,
        fixture_mode: bool, require_nonempty: bool,
        resolve_registries: bool) -> list[_EntityInfo]:
    entities: list[_EntityInfo] = []
    if not isinstance(lemmas, list):
        _add(issues, "SCHEMA_ARRAY", "$.lemmas", "lemmas must be an array.")
        return entities
    if require_nonempty and not lemmas:
        _add(issues, "LEMMAS_REQUIRED", "$.lemmas",
             "This contract requires at least one lemma.")
    canonical_identities: dict[str, str] = {}
    for lemma_index, lemma in enumerate(lemmas):
        lemma_path = f"$.lemmas[{lemma_index}]"
        required = {"id", "canonicalLemma", "reflexive", "aspect", "meanings"}
        allowed = required | {"displayLemma", "aspectPartnerIds"}
        if not _closed_object(lemma, lemma_path, required, allowed, issues):
            continue
        lemma_id = lemma.get("id")
        canonical = lemma.get("canonicalLemma")
        id_ok = _id_syntax(lemma_id, "lemma", f"{lemma_path}.id", issues)
        canonical_ok = _nonempty_string(
            canonical, f"{lemma_path}.canonicalLemma", issues, 2)
        if canonical_ok:
            normalized = normalize_canonical_lemma(canonical)
            if canonical != normalized:
                _add(issues, "CANONICAL_LEMMA_NORMALIZATION",
                     f"{lemma_path}.canonicalLemma",
                     "Canonical lemma must be NFC, trimmed, single-spaced, and lowercase.")
            prior_id = canonical_identities.get(normalized)
            if prior_id is not None and prior_id != lemma_id:
                _add(issues, "LEMMA_IDENTITY_COLLAPSE", f"{lemma_path}.canonicalLemma",
                     "Two lemma entities cannot share one normalized canonical identity.")
            canonical_identities[normalized] = lemma_id
        if id_ok and canonical_ok and lemma_id not in context.allocation_registry:
            try:
                expected = allocate_lemma_id(canonical)
                if lemma_id != expected:
                    _add(issues, "ID_RECOMPUTATION", f"{lemma_path}.id",
                         f"Lemma ID must recompute exactly as {expected!r}.")
            except (TypeError, ValueError):
                pass
        reflexive = lemma.get("reflexive")
        _boolean(reflexive, f"{lemma_path}.reflexive", issues)
        if canonical_ok and type(reflexive) is bool:
            lexical_reflexive = normalize_canonical_lemma(canonical).endswith(" się")
            if reflexive != lexical_reflexive:
                _add(issues, "REFLEXIVE_ASSERTION", f"{lemma_path}.reflexive",
                     "reflexive must agree with lexical final 'się' in canonicalLemma.")
        aspect = lemma.get("aspect")
        _enum(aspect, ASPECTS, f"{lemma_path}.aspect", issues)
        if "displayLemma" in lemma:
            _nonempty_string(lemma["displayLemma"], f"{lemma_path}.displayLemma", issues, 2)
        partners = lemma.get("aspectPartnerIds", [])
        if "aspectPartnerIds" in lemma:
            _string_list(partners, f"{lemma_path}.aspectPartnerIds", issues, unique=True)
            if isinstance(partners, list):
                for index, target in enumerate(partners):
                    _id_syntax(target, "lemma",
                               f"{lemma_path}.aspectPartnerIds[{index}]", issues)
                if aspect == "unresolved" and partners:
                    _add(issues, "UNRESOLVED_ASPECT_LINK", f"{lemma_path}.aspectPartnerIds",
                         "Unresolved aspect cannot publish partner links.")
        if isinstance(lemma_id, str):
            entities.append(_EntityInfo(
                "lemma", lemma_id, None, None, lemma_path,
                lemma, lemma, None, None))

        meanings = lemma.get("meanings")
        if not isinstance(meanings, list) or not meanings:
            _add(issues, "MEANINGS_REQUIRED", f"{lemma_path}.meanings",
                 "Every lemma entity requires at least one meaning.")
            continue
        meaning_keys: set[str] = set()
        for meaning_index, meaning in enumerate(meanings):
            meaning_path = f"{lemma_path}.meanings[{meaning_index}]"
            required_meaning = {"id", "key", "glossesEn", "internalScope", "patterns"}
            if not _closed_object(
                    meaning, meaning_path, required_meaning, required_meaning, issues):
                continue
            meaning_id = meaning.get("id")
            meaning_key = meaning.get("key")
            meaning_id_ok = _id_syntax(
                meaning_id, "meaning", f"{meaning_path}.id", issues)
            meaning_key_ok = _key(meaning_key, f"{meaning_path}.key", issues)
            if isinstance(meaning_key, str):
                if meaning_key in meaning_keys:
                    _add(issues, "SIBLING_KEY_DUPLICATE", f"{meaning_path}.key",
                         "Meaning key is duplicated within its lemma.")
                meaning_keys.add(meaning_key)
            if (meaning_id_ok and meaning_key_ok and canonical_ok and
                    meaning_id not in context.allocation_registry):
                try:
                    expected = allocate_meaning_id(lemma_id, canonical, meaning_key)
                    if meaning_id != expected:
                        _add(issues, "ID_RECOMPUTATION", f"{meaning_path}.id",
                             f"Meaning ID must recompute exactly as {expected!r}.")
                except (TypeError, ValueError):
                    pass
            glosses = meaning.get("glossesEn")
            _string_list(glosses, f"{meaning_path}.glossesEn", issues,
                         min_items=1, max_items=3, unique=True)
            _nonempty_string(meaning.get("internalScope"),
                             f"{meaning_path}.internalScope", issues, 3)
            if isinstance(meaning_id, str):
                entities.append(_EntityInfo(
                    "meaning", meaning_id, lemma_id, meaning_key,
                    meaning_path, meaning, lemma, meaning, None))

            patterns = meaning.get("patterns")
            if not isinstance(patterns, list) or not patterns:
                _add(issues, "PATTERNS_REQUIRED", f"{meaning_path}.patterns",
                     "Every meaning entity requires at least one pattern.")
                continue
            pattern_keys: set[str] = set()
            for pattern_index, pattern in enumerate(patterns):
                pattern_path = f"{meaning_path}.patterns[{pattern_index}]"
                if isinstance(pattern, dict) and isinstance(pattern.get("key"), str):
                    if pattern["key"] in pattern_keys:
                        _add(issues, "SIBLING_KEY_DUPLICATE", f"{pattern_path}.key",
                             "Pattern key is duplicated within its meaning.")
                    pattern_keys.add(pattern["key"])
                _validate_pattern(
                    pattern, pattern_path, lemma, meaning, context, issues,
                    entities, fixture_mode=fixture_mode,
                    resolve_registries=resolve_registries)

    by_id: dict[str, _EntityInfo] = {}
    for entity in entities:
        if entity.entity_id in by_id:
            _add(issues, "ID_GLOBAL_DUPLICATE", f"{entity.path}.id",
                 f"ID is already used at {by_id[entity.entity_id].path}.")
        else:
            by_id[entity.entity_id] = entity
        allocation = context.allocation_registry.get(entity.entity_id)
        if isinstance(allocation, Mapping):
            if allocation.get("kind") != entity.kind:
                _add(issues, "ALLOCATION_KIND", f"{entity.path}.id",
                     "Released ID kind disagrees with its allocation record.")
            if allocation.get("parentId") != entity.parent_id:
                _add(issues, "ALLOCATION_PARENT", f"{entity.path}.id",
                     "Released ID moved away from its allocated parent.")
            if allocation.get("key") != entity.key:
                _add(issues, "ALLOCATION_KEY", f"{entity.path}.id",
                     "Released immutable key disagrees with its allocation record.")
            if entity.kind in {"meaning", "pattern"}:
                lemma_allocation = context.allocation_registry.get(
                    entity.lemma.get("id"))
                allowed_canonical_inputs = [entity.lemma.get("canonicalLemma")]
                if isinstance(lemma_allocation, Mapping):
                    allowed_canonical_inputs.append(
                        lemma_allocation.get("canonicalLemmaAtAllocation"))
                if not _is_member(
                        allocation.get("canonicalLemmaAtAllocation"),
                        allowed_canonical_inputs):
                    _add(issues, "ALLOCATION_CANONICAL_LINEAGE", f"{entity.path}.id",
                         "Released child allocation canonical input must match the "
                         "lemma's original or current reviewed canonical form.")
            if entity.kind == "pattern" and entity.meaning is not None and (
                    allocation.get("meaningKeyAtAllocation") !=
                    entity.meaning.get("key")):
                _add(issues, "ALLOCATION_MEANING_KEY_LINEAGE", f"{entity.path}.id",
                     "Released pattern allocation meaning-key input must match its "
                     "immutable owning meaning key.")

    lemma_entities = {
        item.entity_id: item for item in entities if item.kind == "lemma"}
    pattern_entities = {
        item.entity_id: item for item in entities if item.kind == "pattern"}
    reviewed_states = REVIEWED_STATES
    reviewed_lemma_ids = {
        item.lemma.get("id") for item in pattern_entities.values()
        if isinstance(item.lemma.get("id"), str) and
        _is_member(item.record.get("reviewState"), reviewed_states)}
    for lemma_id, entity in lemma_entities.items():
        partners = entity.record.get("aspectPartnerIds", [])
        if not isinstance(partners, list):
            continue
        for target_id in partners:
            if not isinstance(target_id, str):
                continue
            if target_id == lemma_id:
                _add(issues, "ASPECT_LINK_SELF", entity.path,
                     "Aspect partner link cannot point to itself.")
                continue
            target = lemma_entities.get(target_id)
            if target is None:
                _add(issues, "ASPECT_LINK_DANGLING", entity.path,
                     f"Aspect partner {target_id!r} does not resolve.")
            else:
                if (lemma_id not in reviewed_lemma_ids or
                        target_id not in reviewed_lemma_ids):
                    _add(issues, "ASPECT_LINK_UNREVIEWED", entity.path,
                         "Reciprocal lemma aspect links require a current "
                         "external-or-later review on both linked sides.")
                target_partners = target.record.get("aspectPartnerIds", [])
                if not isinstance(target_partners, list) or lemma_id not in target_partners:
                    _add(issues, "ASPECT_LINK_NONRECIPROCAL", entity.path,
                         f"Aspect partner {target_id!r} does not link back.")
    for pattern_id, entity in pattern_entities.items():
        equivalents = entity.record.get("aspectEquivalentPatternIds", [])
        if not isinstance(equivalents, list):
            continue
        for target_id in equivalents:
            if not isinstance(target_id, str):
                continue
            if target_id == pattern_id:
                _add(issues, "ASPECT_PATTERN_SELF", entity.path,
                     "Aspect-equivalent pattern cannot point to itself.")
                continue
            target = pattern_entities.get(target_id)
            if target is None:
                _add(issues, "ASPECT_PATTERN_DANGLING", entity.path,
                     f"Aspect-equivalent pattern {target_id!r} does not resolve.")
                continue
            if (not _is_member(
                    entity.record.get("reviewState"), reviewed_states) or
                    not _is_member(
                        target.record.get("reviewState"), reviewed_states)):
                _add(issues, "ASPECT_PATTERN_UNREVIEWED", entity.path,
                     "Aspect-equivalent pattern links require both explicit "
                     "pattern records to be externally reviewed or later.")
            target_equivalents = target.record.get("aspectEquivalentPatternIds", [])
            if not isinstance(target_equivalents, list) or (
                    pattern_id not in target_equivalents):
                _add(issues, "ASPECT_PATTERN_NONRECIPROCAL", entity.path,
                     f"Aspect-equivalent pattern {target_id!r} does not link back.")
            owner_id = entity.lemma.get("id")
            target_owner_id = target.lemma.get("id")
            owner_partners = entity.lemma.get("aspectPartnerIds", [])
            target_owner_partners = target.lemma.get("aspectPartnerIds", [])
            if (not isinstance(owner_partners, list) or
                    not isinstance(target_owner_partners, list) or
                    target_owner_id not in owner_partners or
                    owner_id not in target_owner_partners):
                _add(issues, "ASPECT_PATTERN_OWNER_LINK", entity.path,
                     "Equivalent patterns require reciprocal owning-lemma aspect links.")
    return entities


def validate_specification_fixture(
        document: Any, context: ValidationContext | None = None) -> list[Issue]:
    """Validate the distinct Phase 1 report-only fictional fixture contract."""
    if context is None:
        context = ValidationContext()
    issues: list[Issue] = []
    if not _validate_context(context, issues):
        return issues
    required = {
        "artifactStatus", "specificationNotice", "formatVersion",
        "patternDataRevision", "lemmas"}
    if not _closed_object(document, "$", required, required, issues):
        return issues
    if document.get("artifactStatus") != SPECIFICATION_ARTIFACT_STATUS:
        _add(issues, "SPECIFICATION_ARTIFACT_STATUS", "$.artifactStatus",
             "This is not the report-only specification fixture.")
    _nonempty_string(document.get("specificationNotice"),
                     "$.specificationNotice", issues, 20)
    if (type(document.get("formatVersion")) is not int or
            document.get("formatVersion") != FORMAT_VERSION):
        _add(issues, "FORMAT_VERSION", "$.formatVersion",
             f"formatVersion must be {FORMAT_VERSION}.")
    revision = document.get("patternDataRevision")
    if type(revision) is not int or revision < 1:
        _add(issues, "PATTERN_REVISION", "$.patternDataRevision",
             "Fixture revision must be a positive integer.")
    fixture_context = dataclasses.replace(context, allocation_registry={})
    _validate_hierarchy(
        document.get("lemmas"), fixture_context, issues, fixture_mode=True,
        require_nonempty=True, resolve_registries=False)
    return issues


def _expected_allocation_id(allocation: Mapping[str, Any]) -> str:
    """Reproduce a complete originally allocated ID from its retained seed."""
    kind = allocation["kind"]
    parent_id = allocation["parentId"]
    key = allocation["key"]
    seed = allocation["seed"]
    readable = allocation["readableStem"]
    canonical_at_allocation = allocation["canonicalLemmaAtAllocation"]
    meaning_key_at_allocation = allocation["meaningKeyAtAllocation"]
    if not isinstance(readable, str) or not KEY_RE.fullmatch(readable):
        raise ValueError("allocation readable stem is malformed")
    digest = _sha12(seed)
    if kind == "lemma":
        prefix = "v1|lemma|"
        if not seed.startswith(prefix):
            raise ValueError("lemma seed has the wrong family")
        original_canonical = seed[len(prefix):]
        if (not original_canonical or
                normalize_canonical_lemma(original_canonical) != original_canonical):
            raise ValueError("lemma seed does not retain a normalized canonical lemma")
        if canonical_at_allocation != original_canonical or (
                meaning_key_at_allocation is not None):
            raise ValueError("lemma allocation-time identity inputs are inconsistent")
        expected = allocate_lemma_id(original_canonical)
        expected_readable = expected[len("vp-l-"):-13]
        if readable != expected_readable:
            raise ValueError("lemma readable stem disagrees with its original canonical lemma")
        return expected
    expected_seed = f"v1|{kind}|{parent_id}|{key}"
    if seed != expected_seed:
        raise ValueError("seed disagrees with immutable parent/key fields")
    parent_kind = {
        "meaning": "lemma", "pattern": "meaning", "example": "pattern"}[kind]
    if not isinstance(parent_id, str) or not ID_RES[parent_kind].fullmatch(parent_id):
        raise ValueError("owning allocation ID is malformed")
    if not isinstance(key, str) or not KEY_RE.fullmatch(key):
        raise ValueError("allocation key is malformed")
    if kind == "example":
        if canonical_at_allocation is not None or meaning_key_at_allocation is not None:
            raise ValueError("example allocation must derive only from its stable pattern")
        expected_readable = f"{pattern_readable_stem(parent_id)}-{key}"
        if readable != expected_readable:
            raise ValueError("example readable stem disagrees with its stable pattern/key")
    else:
        if (not isinstance(canonical_at_allocation, str) or
                normalize_canonical_lemma(canonical_at_allocation) !=
                canonical_at_allocation):
            raise ValueError("child allocation lacks its normalized canonical input")
        if kind == "meaning":
            if meaning_key_at_allocation != key:
                raise ValueError("meaning allocation key input is inconsistent")
            expected_readable = f"{lemma_slug(canonical_at_allocation)}-{key}"
        else:
            if (not isinstance(meaning_key_at_allocation, str) or
                    not KEY_RE.fullmatch(meaning_key_at_allocation)):
                raise ValueError("pattern allocation lacks its meaning-key input")
            expected_readable = (
                f"{lemma_slug(canonical_at_allocation)}-"
                f"{meaning_key_at_allocation}-{key}")
        if readable != expected_readable:
            raise ValueError("child readable stem disagrees with allocation-time inputs")
    child_family = "m" if kind == "meaning" else "p"
    if kind == "example":
        child_family = "e"
    return f"vp-{child_family}-{readable}-{digest}"


def _validate_context_allocations(
        allocations: Mapping[str, Mapping[str, Any]],
        issues: list[Issue]) -> None:

    records_by_id = {
        allocation.get("id"): allocation
        for allocation in allocations.values()
        if isinstance(allocation, Mapping) and isinstance(allocation.get("id"), str)
    }
    for registry_id, allocation in allocations.items():
        path = f"$allocationRegistry[{registry_id!r}]"
        required = {
            "id", "kind", "parentId", "key", "seed", "readableStem",
            "canonicalLemmaAtAllocation", "meaningKeyAtAllocation"}
        if not _closed_object(allocation, path, required, required, issues):
            continue
        entity_id = allocation.get("id")
        kind = allocation.get("kind")
        if registry_id != entity_id:
            _add(issues, "ALLOCATION_REGISTRY_KEY", path,
                 "Allocation registry key must equal its stored ID.")
        if not _is_member(kind, {"lemma", "meaning", "pattern", "example"}):
            _add(issues, "ALLOCATION_KIND", f"{path}.kind",
                 "Allocation has an unknown entity kind.")
            continue
        _id_syntax(entity_id, kind, f"{path}.id", issues)
        parent_id = allocation.get("parentId")
        key = allocation.get("key")
        if kind == "lemma":
            if parent_id is not None or key is not None:
                _add(issues, "ALLOCATION_OWNERSHIP", path,
                     "Lemma allocation has no parent or key.")
        else:
            parent_kind = {
                "meaning": "lemma", "pattern": "meaning", "example": "pattern"}[kind]
            _id_syntax(parent_id, parent_kind, f"{path}.parentId", issues)
            _key(key, f"{path}.key", issues)
        seed = allocation.get("seed")
        _key(allocation.get("readableStem"), f"{path}.readableStem", issues)
        canonical_at_allocation = allocation.get("canonicalLemmaAtAllocation")
        if canonical_at_allocation is not None:
            _nonempty_string(
                canonical_at_allocation, f"{path}.canonicalLemmaAtAllocation", issues)
        meaning_key_at_allocation = allocation.get("meaningKeyAtAllocation")
        if meaning_key_at_allocation is not None:
            _key(meaning_key_at_allocation, f"{path}.meaningKeyAtAllocation", issues)
        if not _nonempty_string(seed, f"{path}.seed", issues):
            _add(issues, "ALLOCATION_SEED", f"{path}.seed",
                 "Allocation must retain its original seed.")
            continue
        try:
            expected_id = _expected_allocation_id(allocation)
        except (KeyError, TypeError, ValueError, UnicodeError) as exc:
            _add(issues, "ALLOCATION_SEED", f"{path}.seed",
                 f"Allocation seed cannot reproduce its ID: {exc}.")
        else:
            if entity_id != expected_id:
                _add(issues, "ALLOCATION_ID_RECOMPUTATION", f"{path}.id",
                     f"Allocation must reproduce its complete original ID "
                     f"{expected_id!r}, including the readable stem.")
        if _is_member(kind, {"meaning", "pattern", "example"}) and isinstance(
                parent_id, str):
            parent = records_by_id.get(parent_id)
            expected_parent_kind = {
                "meaning": "lemma", "pattern": "meaning", "example": "pattern"}[kind]
            if not isinstance(parent, Mapping):
                _add(issues, "ALLOCATION_PARENT_DANGLING", f"{path}.parentId",
                     "Released child allocation must retain its parent allocation.")
            elif parent.get("kind") != expected_parent_kind:
                _add(issues, "ALLOCATION_PARENT_KIND", f"{path}.parentId",
                     "Released child allocation points to the wrong parent family.")


def validate_editorial(
        document: Any, context: ValidationContext | None = None) -> list[Issue]:
    """Validate the complete private editorial record and all global invariants."""
    if context is None:
        context = ValidationContext()
    issues: list[Issue] = []
    if not _validate_context(context, issues):
        return issues
    required = {"artifactStatus", "formatVersion", "lemmas"}
    if not _closed_object(document, "$", required, required, issues):
        return issues
    if document.get("artifactStatus") != EDITORIAL_ARTIFACT_STATUS:
        _add(issues, "EDITORIAL_ARTIFACT_STATUS", "$.artifactStatus",
             "Editorial artifactStatus is missing or incorrect.")
    if (type(document.get("formatVersion")) is not int or
            document.get("formatVersion") != FORMAT_VERSION):
        _add(issues, "FORMAT_VERSION", "$.formatVersion",
             f"formatVersion must be {FORMAT_VERSION}.")
    if not isinstance(context.allocation_registry, Mapping):
        _add(issues, "ALLOCATION_REGISTRY_TYPE", "$allocationRegistry",
             "Allocation registry must be an object mapping IDs to records.")
    else:
        _validate_context_allocations(context.allocation_registry, issues)
    _validate_hierarchy(
        document.get("lemmas"), context, issues, fixture_mode=False,
        require_nonempty=False, resolve_registries=True)
    return issues


def _validate_runtime_example(value: Any, path: str, issues: list[Issue]) -> None:
    required = {"id", "pl", "en", "audioEligible"}
    if not _closed_object(value, path, required, required, issues):
        return
    _id_syntax(value.get("id"), "example", f"{path}.id", issues)
    _nonempty_string(value.get("pl"), f"{path}.pl", issues, 3)
    _nonempty_string(value.get("en"), f"{path}.en", issues, 3)
    _boolean(value.get("audioEligible"), f"{path}.audioEligible", issues)


def _recursive_private_key_check(
        value: Any, path: str, issues: list[Issue]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN_RUNTIME_KEYS:
                _add(issues, "RUNTIME_PRIVATE_FIELD", f"{path}.{key}",
                     "Private/editorial field is forbidden in runtime data.")
            _recursive_private_key_check(child, f"{path}.{key}", issues)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _recursive_private_key_check(child, f"{path}[{index}]", issues)


def validate_runtime(
        document: Any, context: ValidationContext | None = None) -> list[Issue]:
    """Validate the distinct closed public runtime projection contract."""
    if context is None:
        context = ValidationContext()
    issues: list[Issue] = []
    if not _validate_context(context, issues):
        return issues
    required = {"formatVersion", "patternDataRevision", "lemmas"}
    if not _closed_object(document, "$", required, required, issues):
        return issues
    if context.allocation_registry:
        _validate_context_allocations(context.allocation_registry, issues)
    _recursive_private_key_check(document, "$", issues)
    if (type(document.get("formatVersion")) is not int or
            document.get("formatVersion") != FORMAT_VERSION):
        _add(issues, "FORMAT_VERSION", "$.formatVersion",
             f"formatVersion must be {FORMAT_VERSION}.")
    revision = document.get("patternDataRevision")
    if type(revision) is not int or revision < 1:
        _add(issues, "PATTERN_REVISION", "$.patternDataRevision",
             "Runtime patternDataRevision must be a positive integer.")
    lemmas = document.get("lemmas")
    if not isinstance(lemmas, list) or not lemmas:
        _add(issues, "RUNTIME_LEMMAS_REQUIRED", "$.lemmas",
             "Runtime projection requires at least one admitted lemma.")
        return issues

    ids: dict[str, str] = {}
    lemma_map: dict[str, Mapping[str, Any]] = {}
    pattern_map: dict[str, tuple[Mapping[str, Any], Mapping[str, Any]]] = {}

    def remember(entity_id: Any, path: str) -> None:
        if not isinstance(entity_id, str):
            return
        if entity_id in ids:
            _add(issues, "ID_GLOBAL_DUPLICATE", path,
                 f"Runtime ID is already used at {ids[entity_id]}.")
        else:
            ids[entity_id] = path

    def verify_allocation(
            entity_id: Any, kind: str, parent_id: Any, path: str) -> None:
        if not context.allocation_registry or not isinstance(entity_id, str):
            return
        allocation = context.allocation_registry.get(entity_id)
        if not isinstance(allocation, Mapping):
            _add(issues, "RUNTIME_ALLOCATION_DANGLING", path,
                 "Runtime entity must resolve in the supplied frozen allocation "
                 "registry.")
            return
        if allocation.get("kind") != kind:
            _add(issues, "RUNTIME_ALLOCATION_KIND", path,
                 "Runtime entity kind disagrees with its frozen allocation.")
        if allocation.get("parentId") != parent_id:
            _add(issues, "RUNTIME_ALLOCATION_PARENT", path,
                 "Runtime nesting disagrees with frozen allocation ownership.")

    for lemma_index, lemma in enumerate(lemmas):
        lemma_path = f"$.lemmas[{lemma_index}]"
        required_lemma = {
            "id", "canonicalLemma", "reflexive", "aspect", "meanings"}
        allowed_lemma = required_lemma | {"displayLemma", "aspectPartnerIds"}
        if not _closed_object(
                lemma, lemma_path, required_lemma, allowed_lemma, issues):
            continue
        lemma_id = lemma.get("id")
        _id_syntax(lemma_id, "lemma", f"{lemma_path}.id", issues)
        remember(lemma_id, f"{lemma_path}.id")
        verify_allocation(lemma_id, "lemma", None, f"{lemma_path}.id")
        if isinstance(lemma_id, str):
            lemma_map[lemma_id] = lemma
        canonical = lemma.get("canonicalLemma")
        canonical_ok = _nonempty_string(
            canonical, f"{lemma_path}.canonicalLemma", issues, 2)
        if canonical_ok and canonical != normalize_canonical_lemma(canonical):
            _add(issues, "CANONICAL_LEMMA_NORMALIZATION",
                 f"{lemma_path}.canonicalLemma",
                 "Runtime canonical lemma must remain normalized.")
        reflexive = lemma.get("reflexive")
        _boolean(reflexive, f"{lemma_path}.reflexive", issues)
        if canonical_ok and type(reflexive) is bool and reflexive != (
                normalize_canonical_lemma(canonical).endswith(" się")):
            _add(issues, "REFLEXIVE_ASSERTION", f"{lemma_path}.reflexive",
                 "Runtime reflexive assertion disagrees with canonicalLemma.")
        aspect = lemma.get("aspect")
        _enum(aspect, ASPECTS - {"unresolved"}, f"{lemma_path}.aspect", issues)
        if "displayLemma" in lemma:
            _nonempty_string(lemma["displayLemma"],
                             f"{lemma_path}.displayLemma", issues, 2)
        if "aspectPartnerIds" in lemma:
            partners = lemma["aspectPartnerIds"]
            _string_list(partners, f"{lemma_path}.aspectPartnerIds", issues,
                         unique=True)
            if isinstance(partners, list):
                for index, target in enumerate(partners):
                    _id_syntax(target, "lemma",
                               f"{lemma_path}.aspectPartnerIds[{index}]", issues)
        meanings = lemma.get("meanings")
        if not isinstance(meanings, list) or not meanings:
            _add(issues, "RUNTIME_MEANINGS_REQUIRED", f"{lemma_path}.meanings",
                 "Projected lemma requires a non-empty meanings array.")
            continue
        for meaning_index, meaning in enumerate(meanings):
            meaning_path = f"{lemma_path}.meanings[{meaning_index}]"
            required_meaning = {"id", "glossesEn", "patterns"}
            if not _closed_object(
                    meaning, meaning_path, required_meaning, required_meaning, issues):
                continue
            meaning_id = meaning.get("id")
            _id_syntax(meaning_id, "meaning", f"{meaning_path}.id", issues)
            remember(meaning_id, f"{meaning_path}.id")
            verify_allocation(
                meaning_id, "meaning", lemma_id, f"{meaning_path}.id")
            _string_list(meaning.get("glossesEn"), f"{meaning_path}.glossesEn",
                         issues, min_items=1, max_items=3, unique=True)
            patterns = meaning.get("patterns")
            if not isinstance(patterns, list) or not patterns:
                _add(issues, "RUNTIME_PATTERNS_REQUIRED", f"{meaning_path}.patterns",
                     "Projected meaning requires a non-empty patterns array.")
                continue
            for pattern_index, pattern in enumerate(patterns):
                pattern_path = f"{meaning_path}.patterns[{pattern_index}]"
                required_pattern = {
                    "id", "relationType", "complements", "cefr",
                    "teachingStatus", "usage", "learnerExplanationEn",
                    "activityEligibility"}
                allowed_pattern = required_pattern | {
                    "aspectEquivalentPatternIds", "examples", "contentRefs",
                    "errorNotes", "requiredLexicalItems"}
                if not _closed_object(
                        pattern, pattern_path, required_pattern, allowed_pattern,
                        issues):
                    continue
                pattern_id = pattern.get("id")
                _id_syntax(pattern_id, "pattern", f"{pattern_path}.id", issues)
                remember(pattern_id, f"{pattern_path}.id")
                verify_allocation(
                    pattern_id, "pattern", meaning_id, f"{pattern_path}.id")
                if isinstance(pattern_id, str):
                    pattern_map[pattern_id] = (lemma, pattern)
                relation_type = pattern.get("relationType")
                _enum(relation_type, RELATION_TYPES,
                      f"{pattern_path}.relationType", issues)
                complements = pattern.get("complements")
                if not isinstance(complements, list) or not complements:
                    _add(issues, "COMPLEMENTS_REQUIRED",
                         f"{pattern_path}.complements",
                         "Runtime pattern requires complements.")
                else:
                    for index, complement in enumerate(complements):
                        _validate_complement(
                            complement, f"{pattern_path}.complements[{index}]",
                            relation_type, issues)
                    _validate_relation_roles(
                        relation_type, complements,
                        f"{pattern_path}.complements", issues)
                teaching_status = pattern.get("teachingStatus")
                _enum(teaching_status, {"active-production", "recognition-only"},
                      f"{pattern_path}.teachingStatus", issues)
                _validate_cefr(pattern.get("cefr"), f"{pattern_path}.cefr",
                               teaching_status, issues)
                _validate_usage(pattern.get("usage"), f"{pattern_path}.usage",
                                teaching_status, issues)
                _nonempty_string(pattern.get("learnerExplanationEn"),
                                 f"{pattern_path}.learnerExplanationEn", issues, 3)
                if "requiredLexicalItems" in pattern:
                    _validate_required_lexical_items(
                        pattern["requiredLexicalItems"],
                        f"{pattern_path}.requiredLexicalItems", issues)
                eligibility = pattern.get("activityEligibility")
                _string_list(eligibility, f"{pattern_path}.activityEligibility",
                             issues, unique=True, allowed=ACTIVITY_KEYS)
                if teaching_status == "recognition-only" and isinstance(
                        eligibility, list) and (
                        {"grammar-build", "type-it"} & {
                            item for item in eligibility if isinstance(item, str)}):
                    _add(issues, "RECOGNITION_PRODUCTION_ACTIVITY",
                         f"{pattern_path}.activityEligibility",
                         "recognition-only forbids grammar-build and type-it.")
                examples = pattern.get("examples", [])
                if "examples" in pattern and not isinstance(examples, list):
                    _add(issues, "SCHEMA_ARRAY", f"{pattern_path}.examples",
                         "Runtime examples must be an array.")
                    examples = []
                for example_index, example in enumerate(examples):
                    example_path = f"{pattern_path}.examples[{example_index}]"
                    _validate_runtime_example(example, example_path, issues)
                    if isinstance(example, dict):
                        example_id = example.get("id")
                        remember(example_id, f"{example_path}.id")
                        verify_allocation(
                            example_id, "example", pattern_id,
                            f"{example_path}.id")
                        if isinstance(example_id, str) and isinstance(pattern_id, str):
                            try:
                                stem = pattern_readable_stem(pattern_id)
                                if not example_id.startswith(f"vp-e-{stem}-"):
                                    _add(issues, "RUNTIME_EXAMPLE_OWNERSHIP",
                                         f"{example_path}.id",
                                         "Example readable stem does not match its pattern.")
                            except ValueError:
                                pass
                        if example.get("audioEligible") is True and not (
                                isinstance(eligibility, list) and
                                "listening" in eligibility or
                                type(revision) is int and revision >= 2):
                            _add(issues, "AUDIO_NOT_AUTHORIZED",
                                 f"{example_path}.audioEligible",
                                 "Runtime revision 1 audio requires Listening; "
                                 "independent pronunciation starts at revision 2.")
                if isinstance(eligibility, list) and (
                        {item for item in eligibility if isinstance(item, str)} & {
                            "listening", "grammar-choose", "grammar-build", "type-it"}) and not examples:
                    _add(issues, "ACTIVITY_EXAMPLE_REQUIRED",
                         f"{pattern_path}.examples",
                         "Listening and active grammar use require an example.")
                equivalents = pattern.get("aspectEquivalentPatternIds", [])
                if "aspectEquivalentPatternIds" in pattern:
                    _string_list(equivalents,
                                 f"{pattern_path}.aspectEquivalentPatternIds",
                                 issues, unique=True)
                    if isinstance(equivalents, list):
                        for index, target in enumerate(equivalents):
                            _id_syntax(target, "pattern",
                                       f"{pattern_path}.aspectEquivalentPatternIds[{index}]",
                                       issues)
                refs = pattern.get("contentRefs", [])
                if "contentRefs" in pattern and not isinstance(refs, list):
                    _add(issues, "SCHEMA_ARRAY", f"{pattern_path}.contentRefs",
                         "Runtime contentRefs must be an array.")
                elif isinstance(refs, list):
                    seen_refs: set[tuple[Any, Any, Any]] = set()
                    for ref_index, reference in enumerate(refs):
                        ref_path = f"{pattern_path}.contentRefs[{ref_index}]"
                        _validate_content_ref(
                            reference, ref_path, context, issues,
                            resolve_repository=context.repository_index is not None)
                        if isinstance(reference, dict):
                            identity = (
                                reference.get("kind"), reference.get("id"),
                                reference.get("purpose"))
                            if (all(isinstance(item, str) for item in identity) and
                                    identity in seen_refs):
                                _add(issues, "CONTENT_REF_DUPLICATE", ref_path,
                                     "Runtime content references must be unique.")
                            if all(isinstance(item, str) for item in identity):
                                seen_refs.add(identity)
                error_notes = pattern.get("errorNotes", [])
                if "errorNotes" in pattern and not isinstance(error_notes, list):
                    _add(issues, "SCHEMA_ARRAY", f"{pattern_path}.errorNotes",
                         "Runtime errorNotes must be an array.")
                elif isinstance(error_notes, list):
                    for note_index, note in enumerate(error_notes):
                        _validate_error_note(
                            note, f"{pattern_path}.errorNotes[{note_index}]", 0,
                            issues, runtime=True)

    for lemma_id, lemma in lemma_map.items():
        partner_ids = lemma.get("aspectPartnerIds", [])
        if not isinstance(partner_ids, list):
            continue
        for target_id in partner_ids:
            if not isinstance(target_id, str):
                continue
            if target_id == lemma_id:
                _add(issues, "ASPECT_LINK_SELF", "$.lemmas",
                     "Runtime aspect partner link cannot point to itself.")
                continue
            target = lemma_map.get(target_id)
            if target is None:
                _add(issues, "ASPECT_LINK_DANGLING", "$.lemmas",
                     f"Runtime aspect partner {target_id!r} does not resolve.")
            else:
                target_partners = target.get("aspectPartnerIds", [])
                if not isinstance(target_partners, list) or lemma_id not in target_partners:
                    _add(issues, "ASPECT_LINK_NONRECIPROCAL", "$.lemmas",
                         f"Runtime aspect partner {target_id!r} does not link back.")
    for pattern_id, (owner, pattern) in pattern_map.items():
        equivalent_ids = pattern.get("aspectEquivalentPatternIds", [])
        if not isinstance(equivalent_ids, list):
            continue
        for target_id in equivalent_ids:
            if not isinstance(target_id, str):
                continue
            if target_id == pattern_id:
                _add(issues, "ASPECT_PATTERN_SELF", "$.lemmas",
                     "Runtime aspect-equivalent link cannot point to itself.")
                continue
            target_pair = pattern_map.get(target_id)
            if target_pair is None:
                _add(issues, "ASPECT_PATTERN_DANGLING", "$.lemmas",
                     f"Runtime aspect-equivalent pattern {target_id!r} does not resolve.")
                continue
            target_owner, target = target_pair
            target_equivalents = target.get("aspectEquivalentPatternIds", [])
            if not isinstance(target_equivalents, list) or (
                    pattern_id not in target_equivalents):
                _add(issues, "ASPECT_PATTERN_NONRECIPROCAL", "$.lemmas",
                     f"Runtime aspect-equivalent pattern {target_id!r} does not link back.")
            owner_partners = owner.get("aspectPartnerIds", [])
            if (not isinstance(owner_partners, list) or
                    target_owner.get("id") not in owner_partners):
                _add(issues, "ASPECT_PATTERN_OWNER_LINK", "$.lemmas",
                     "Runtime equivalent patterns require linked owning lemmas.")
    return issues


def _runtime_complement(complement: Mapping[str, Any]) -> dict[str, Any]:
    return copy.deepcopy(dict(complement))


def _runtime_pattern(
        pattern: Mapping[str, Any], admitted_pattern_ids: set[str]) -> dict[str, Any]:
    runtime: dict[str, Any] = {
        "id": pattern["id"],
        "relationType": pattern["relationType"],
        "complements": [_runtime_complement(item) for item in pattern["complements"]],
        "cefr": copy.deepcopy(pattern["cefr"]),
        "teachingStatus": pattern["teachingStatus"],
        "usage": copy.deepcopy(pattern["usage"]),
        "learnerExplanationEn": pattern["learnerExplanationEn"],
        "activityEligibility": sorted(pattern["activityEligibility"]),
    }
    if "requiredLexicalItems" in pattern:
        runtime["requiredLexicalItems"] = copy.deepcopy(
            pattern["requiredLexicalItems"])
    equivalents = sorted(
        target for target in pattern.get("aspectEquivalentPatternIds", [])
        if target in admitted_pattern_ids)
    if equivalents:
        runtime["aspectEquivalentPatternIds"] = equivalents
    if pattern.get("examples"):
        runtime["examples"] = [{
            "id": example["id"],
            "pl": example["pl"],
            "en": example["en"],
            "audioEligible": example["audioEligible"],
        } for example in pattern["examples"]]
    if pattern.get("contentRefs"):
        runtime["contentRefs"] = sorted(
            copy.deepcopy(pattern["contentRefs"]),
            key=lambda ref: (ref["kind"], ref["id"], ref["purpose"]))
    if pattern.get("errorNotes"):
        runtime["errorNotes"] = [{
            "kind": note["kind"],
            "incorrectForm": note["incorrectForm"],
            "guidanceEn": note["guidanceEn"],
        } for note in pattern["errorNotes"]]
    return runtime


def project_runtime_nonrelease(
        document: Any, pattern_data_revision: int,
        context: ValidationContext | None = None) -> dict[str, Any]:
    """Construct a validated runtime-shaped value without release authority.

    This pure projection is for tests and for ``freeze_editorial`` while it
    validates a complete transition.  Even with an allocation registry, its
    result does not prove active membership, tombstone history, or a valid
    release revision.  The only release-authoritative source is the
    ``runtimeProjection`` returned by ``freeze_editorial`` (or subsequently
    accepted by ``verified_runtime_from_frozen``).
    """
    if context is None:
        context = ValidationContext()
    issues = validate_editorial(document, context)
    if issues:
        raise ValidationFailure(issues)
    if type(pattern_data_revision) is not int or pattern_data_revision < 1:
        raise ValidationFailure([Issue(
            "PATTERN_REVISION", "$.patternDataRevision",
            "Runtime patternDataRevision must be a positive integer.")])

    admitted_pattern_ids = {
        pattern["id"]
        for lemma in document["lemmas"]
        for meaning in lemma["meanings"]
        for pattern in meaning["patterns"]
        if pattern["reviewState"] == "approved" and
        pattern["teachingStatus"] in {"active-production", "recognition-only"}
    }
    admitted_lemma_ids = {
        lemma["id"]
        for lemma in document["lemmas"]
        if any(
            pattern["id"] in admitted_pattern_ids
            for meaning in lemma["meanings"] for pattern in meaning["patterns"])
    }
    projected_lemmas: list[dict[str, Any]] = []
    for lemma in sorted(document["lemmas"], key=lambda item: item["id"]):
        projected_meanings: list[dict[str, Any]] = []
        for meaning in sorted(lemma["meanings"], key=lambda item: item["id"]):
            projected_patterns = [
                _runtime_pattern(pattern, admitted_pattern_ids)
                for pattern in sorted(meaning["patterns"], key=lambda item: item["id"])
                if pattern["id"] in admitted_pattern_ids
            ]
            if projected_patterns:
                projected_meanings.append({
                    "id": meaning["id"],
                    "glossesEn": copy.deepcopy(meaning["glossesEn"]),
                    "patterns": projected_patterns,
                })
        if not projected_meanings:
            continue
        runtime_lemma: dict[str, Any] = {
            "id": lemma["id"],
            "canonicalLemma": lemma["canonicalLemma"],
            "reflexive": lemma["reflexive"],
            "aspect": lemma["aspect"],
            "meanings": projected_meanings,
        }
        if "displayLemma" in lemma:
            runtime_lemma["displayLemma"] = lemma["displayLemma"]
        partners = sorted(
            target for target in lemma.get("aspectPartnerIds", [])
            if target in admitted_lemma_ids)
        if partners:
            runtime_lemma["aspectPartnerIds"] = partners
        projected_lemmas.append(runtime_lemma)
    runtime_document = {
        "formatVersion": FORMAT_VERSION,
        "patternDataRevision": pattern_data_revision,
        "lemmas": projected_lemmas,
    }
    if not projected_lemmas:
        raise ValidationFailure([Issue(
            "PROJECTION_EMPTY", "$.lemmas",
            "No current approved active/recognition pattern can be projected.")])
    # Editorial validation above already checked every released allocation and
    # live-recomputed every newly authored ID.  A transition context is therefore
    # intentionally a partial registry until ``freeze_editorial`` appends the new
    # allocations; do not misinterpret that partial set as a complete runtime
    # release registry here.
    runtime_issues = validate_runtime(
        runtime_document, dataclasses.replace(context, allocation_registry={}))
    if runtime_issues:
        raise ValidationFailure(runtime_issues)
    return runtime_document


def project_nonrelease_fixture(
        document: Any, test_pattern_data_revision: int,
        context: ValidationContext | None = None) -> dict[str, Any]:
    """Wrap a pure projection so CLI output cannot be mistaken for a release."""
    return {
        "artifactStatus": NONRELEASE_PROJECTION_STATUS,
        "releaseAuthorized": False,
        "runtimeProjection": project_runtime_nonrelease(
            document, test_pattern_data_revision, context),
    }


def _allocation_for_entity(entity: _EntityInfo) -> dict[str, Any]:
    if entity.kind == "lemma":
        seed = f"v1|lemma|{normalize_canonical_lemma(entity.record['canonicalLemma'])}"
    elif entity.kind == "meaning":
        seed = f"v1|meaning|{entity.parent_id}|{entity.key}"
    elif entity.kind == "pattern":
        seed = f"v1|pattern|{entity.parent_id}|{entity.key}"
    elif entity.kind == "example":
        seed = f"v1|example|{entity.parent_id}|{entity.key}"
    else:
        raise ValueError(f"unsupported frozen entity kind: {entity.kind}")
    family = {
        "lemma": "l", "meaning": "m", "pattern": "p", "example": "e"}[
            entity.kind]
    prefix = f"vp-{family}-"
    readable_stem = entity.entity_id[len(prefix):-13]
    return {
        "id": entity.entity_id,
        "kind": entity.kind,
        "parentId": entity.parent_id,
        "key": entity.key,
        "seed": seed,
        "readableStem": readable_stem,
        "canonicalLemmaAtAllocation": (
            entity.record["canonicalLemma"] if entity.kind == "lemma" else
            entity.lemma["canonicalLemma"] if entity.kind in {"meaning", "pattern"}
            else None),
        "meaningKeyAtAllocation": (
            entity.key if entity.kind == "meaning" else
            entity.meaning["key"] if entity.kind == "pattern" and
            entity.meaning is not None else None),
    }


def _identity_for_entity(entity: _EntityInfo) -> dict[str, Any]:
    result = {
        "id": entity.entity_id,
        "kind": entity.kind,
        "parentId": entity.parent_id,
        "key": entity.key,
    }
    if entity.kind == "pattern":
        result["relationType"] = entity.record["relationType"]
    return result


def _structural_complements(pattern: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {key: copy.deepcopy(value) for key, value in complement.items()
         if key != "questionOverridePl"}
        for complement in pattern["complements"]
    ]


def _structure_for_entity(entity: _EntityInfo) -> dict[str, Any]:
    result: dict[str, Any] = {"id": entity.entity_id, "kind": entity.kind}
    if entity.kind == "lemma":
        result.update({
            "canonicalLemma": entity.record["canonicalLemma"],
            "reflexive": entity.record["reflexive"],
            "aspect": entity.record["aspect"],
            "aspectPartnerIds": sorted(entity.record.get("aspectPartnerIds", [])),
        })
    elif entity.kind == "meaning":
        result["parentLemmaId"] = entity.parent_id
    elif entity.kind == "pattern":
        result.update({
            "parentMeaningId": entity.parent_id,
            "relationType": entity.record["relationType"],
            "complements": _structural_complements(entity.record),
            "aspectEquivalentPatternIds": sorted(
                entity.record.get("aspectEquivalentPatternIds", [])),
            "contentRefs": sorted(
                copy.deepcopy(entity.record.get("contentRefs", [])),
                key=lambda ref: (ref["kind"], ref["id"], ref["purpose"])),
            "exampleIds": [
                example["id"] for example in entity.record.get("examples", [])],
            "examplesPresent": "examples" in entity.record,
        })
        if "requiredLexicalItems" in entity.record:
            result["requiredLexicalItems"] = copy.deepcopy(
                entity.record["requiredLexicalItems"])
    elif entity.kind == "example":
        result["parentPatternId"] = entity.parent_id
    return result


def _wording_for_entity(entity: _EntityInfo) -> dict[str, Any]:
    result: dict[str, Any] = {"id": entity.entity_id, "kind": entity.kind}
    if entity.kind == "lemma":
        result["displayLemma"] = entity.record.get("displayLemma")
    elif entity.kind == "meaning":
        result["glossesEn"] = copy.deepcopy(entity.record["glossesEn"])
        result["internalScope"] = entity.record["internalScope"]
    elif entity.kind == "pattern":
        result.update({
            "learnerExplanationEn": entity.record["learnerExplanationEn"],
            "usageNote": entity.record["usage"].get("note"),
            "questionOverrides": [
                copy.deepcopy(item.get("questionOverridePl"))
                for item in entity.record["complements"]],
            "errorNotes": copy.deepcopy(entity.record.get("errorNotes", [])),
        })
    elif entity.kind == "example":
        result.update({"pl": entity.record["pl"], "en": entity.record["en"]})
    return result


def _policy_for_entity(entity: _EntityInfo) -> dict[str, Any]:
    result: dict[str, Any] = {"id": entity.entity_id, "kind": entity.kind}
    if entity.kind == "pattern":
        result.update({
            "cefr": copy.deepcopy(entity.record["cefr"]),
            "teachingStatus": entity.record["teachingStatus"],
            "usage": {
                "priority": entity.record["usage"]["priority"],
                "register": entity.record["usage"]["register"],
            },
            "activityEligibility": sorted(entity.record["activityEligibility"]),
            "reviewState": entity.record["reviewState"],
            "releaseMode": declared_release_mode(entity.record),
            "scopeVersion": SCOPE_VERSION,
            "currentScopeDigests": {
                stage: review_scope_digest(
                    stage, entity.lemma, entity.meaning, entity.record)
                for stage in STAGE_KINDS
            },
        })
    elif entity.kind == "example":
        result["audioEligible"] = entity.record["audioEligible"]
    return result


FROZEN_ENTITY_KINDS = {"lemma", "meaning", "pattern", "example"}


def _validate_frozen_identity_row(
        row: Any, path: str, issues: list[Issue]) -> bool:
    if not isinstance(row, dict):
        _add(issues, "FROZEN_IDENTITY_OBJECT", path,
             "Frozen identity entry must be an object.")
        return False
    kind = row.get("kind")
    if not _is_member(kind, FROZEN_ENTITY_KINDS):
        _add(issues, "FROZEN_KIND", f"{path}.kind",
             "Frozen identity has an unknown entity kind.")
        _closed_object(row, path, {"id", "kind", "parentId", "key"},
                       {"id", "kind", "parentId", "key"}, issues)
        return False
    required = {"id", "kind", "parentId", "key"}
    if kind == "pattern":
        required.add("relationType")
    if not _closed_object(row, path, required, required, issues):
        return False
    entity_id = row.get("id")
    _id_syntax(entity_id, kind, f"{path}.id", issues)
    parent_id = row.get("parentId")
    key = row.get("key")
    if kind == "lemma":
        if parent_id is not None or key is not None:
            _add(issues, "FROZEN_IDENTITY_OWNERSHIP", path,
                 "Lemma identity must have null parentId and key.")
    else:
        parent_kind = {
            "meaning": "lemma", "pattern": "meaning", "example": "pattern"}[kind]
        _id_syntax(parent_id, parent_kind, f"{path}.parentId", issues)
        _key(key, f"{path}.key", issues)
    if kind == "pattern":
        _enum(row.get("relationType"), RELATION_TYPES,
              f"{path}.relationType", issues)
    return isinstance(entity_id, str)


def _validate_frozen_structure_row(
        row: Any, path: str, issues: list[Issue]) -> bool:
    if not isinstance(row, dict):
        _add(issues, "FROZEN_SNAPSHOT_OBJECT", path,
             "Frozen structure entry must be an object.")
        return False
    kind = row.get("kind")
    schemas = {
        "lemma": {"id", "kind", "canonicalLemma", "reflexive", "aspect",
                  "aspectPartnerIds"},
        "meaning": {"id", "kind", "parentLemmaId"},
        "pattern": {"id", "kind", "parentMeaningId", "relationType",
                    "complements", "aspectEquivalentPatternIds", "contentRefs",
                    "exampleIds", "examplesPresent"},
        "example": {"id", "kind", "parentPatternId"},
    }
    required = schemas.get(kind) if isinstance(kind, str) else None
    if required is None:
        _add(issues, "FROZEN_KIND", f"{path}.kind",
             "Frozen structure has an unknown entity kind.")
        return False
    allowed = set(required)
    if kind == "pattern":
        allowed.add("requiredLexicalItems")
    if not _closed_object(row, path, required, allowed, issues):
        return False
    _id_syntax(row.get("id"), kind, f"{path}.id", issues)
    if kind == "lemma":
        canonical = row.get("canonicalLemma")
        canonical_ok = _nonempty_string(canonical, f"{path}.canonicalLemma", issues, 2)
        if canonical_ok and canonical != normalize_canonical_lemma(canonical):
            _add(issues, "CANONICAL_LEMMA_NORMALIZATION", f"{path}.canonicalLemma",
                 "Frozen canonical lemma must remain normalized.")
        # Type-check only: a historical wrong redundant Boolean is deliberately
        # accepted so the correction workflow can repair it in place.
        _boolean(row.get("reflexive"), f"{path}.reflexive", issues)
        _enum(row.get("aspect"), ASPECTS, f"{path}.aspect", issues)
        partners = row.get("aspectPartnerIds")
        _string_list(partners, f"{path}.aspectPartnerIds", issues, unique=True)
        if isinstance(partners, list):
            if all(isinstance(item, str) for item in partners) and partners != sorted(partners):
                _add(issues, "FROZEN_SET_ORDER", f"{path}.aspectPartnerIds",
                     "Frozen set-like links must be lexicographically sorted.")
            for index, target in enumerate(partners):
                _id_syntax(target, "lemma", f"{path}.aspectPartnerIds[{index}]", issues)
    elif kind == "meaning":
        _id_syntax(row.get("parentLemmaId"), "lemma", f"{path}.parentLemmaId", issues)
    elif kind == "pattern":
        _id_syntax(row.get("parentMeaningId"), "meaning",
                   f"{path}.parentMeaningId", issues)
        relation_type = row.get("relationType")
        _enum(relation_type, RELATION_TYPES, f"{path}.relationType", issues)
        if "requiredLexicalItems" in row:
            _validate_required_lexical_items(
                row["requiredLexicalItems"],
                f"{path}.requiredLexicalItems", issues)
        complements = row.get("complements")
        if not isinstance(complements, list) or not complements:
            _add(issues, "COMPLEMENTS_REQUIRED", f"{path}.complements",
                 "Frozen pattern structure requires complements.")
        else:
            for index, complement in enumerate(complements):
                _validate_complement(
                    complement, f"{path}.complements[{index}]", relation_type, issues)
                if isinstance(complement, dict) and "questionOverridePl" in complement:
                    _add(issues, "FROZEN_STRUCTURE_WORDING_FIELD",
                         f"{path}.complements[{index}].questionOverridePl",
                         "Question override copy belongs only in the frozen wording "
                         "dimension.")
            _validate_relation_roles(relation_type, complements,
                                     f"{path}.complements", issues)
        equivalents = row.get("aspectEquivalentPatternIds")
        _string_list(equivalents, f"{path}.aspectEquivalentPatternIds",
                     issues, unique=True)
        if isinstance(equivalents, list):
            if (all(isinstance(item, str) for item in equivalents) and
                    equivalents != sorted(equivalents)):
                _add(issues, "FROZEN_SET_ORDER",
                     f"{path}.aspectEquivalentPatternIds",
                     "Frozen set-like links must be lexicographically sorted.")
            for index, target in enumerate(equivalents):
                _id_syntax(target, "pattern",
                           f"{path}.aspectEquivalentPatternIds[{index}]", issues)
        refs = row.get("contentRefs")
        if not isinstance(refs, list):
            _add(issues, "SCHEMA_ARRAY", f"{path}.contentRefs",
                 "Frozen contentRefs must be an array.")
        else:
            seen_refs: set[tuple[str, str, str]] = set()
            sortable_refs: list[tuple[str, str, str]] = []
            for index, reference in enumerate(refs):
                reference_path = f"{path}.contentRefs[{index}]"
                _validate_content_ref(
                    reference, reference_path, ValidationContext(), issues,
                    resolve_repository=False)
                if isinstance(reference, dict):
                    identity = (reference.get("kind"), reference.get("id"),
                                reference.get("purpose"))
                    if all(isinstance(item, str) for item in identity):
                        if identity in seen_refs:
                            _add(issues, "CONTENT_REF_DUPLICATE", reference_path,
                                 "Frozen content references must be unique.")
                        seen_refs.add(identity)
                        sortable_refs.append(identity)
            if len(sortable_refs) == len(refs) and sortable_refs != sorted(sortable_refs):
                _add(issues, "FROZEN_SET_ORDER", f"{path}.contentRefs",
                     "Frozen content references must use deterministic tuple order.")
        example_ids = row.get("exampleIds")
        _string_list(example_ids, f"{path}.exampleIds", issues, unique=True)
        if isinstance(example_ids, list):
            for index, example_id in enumerate(example_ids):
                _id_syntax(example_id, "example",
                           f"{path}.exampleIds[{index}]", issues)
        _boolean(row.get("examplesPresent"), f"{path}.examplesPresent", issues)
    else:
        _id_syntax(row.get("parentPatternId"), "pattern",
                   f"{path}.parentPatternId", issues)
    return isinstance(row.get("id"), str)


def _validate_frozen_error_note(
        value: Any, path: str, issues: list[Issue]) -> None:
    required = {"kind", "incorrectForm", "guidanceEn"}
    allowed = required | {"evidenceRefs"}
    if not _closed_object(value, path, required, allowed, issues):
        return
    kind = value.get("kind")
    _enum(kind, ERROR_KINDS, f"{path}.kind", issues)
    _nonempty_string(value.get("incorrectForm"), f"{path}.incorrectForm", issues)
    _nonempty_string(value.get("guidanceEn"), f"{path}.guidanceEn", issues, 3)
    refs = value.get("evidenceRefs")
    if kind == "documented-common-error" and not isinstance(refs, list):
        _add(issues, "ERROR_EVIDENCE_REQUIRED", f"{path}.evidenceRefs",
             "Documented frozen error notes retain evidence references.")
    if "evidenceRefs" in value:
        if not isinstance(refs, list) or not refs:
            _add(issues, "ERROR_EVIDENCE_ARRAY", f"{path}.evidenceRefs",
                 "Frozen evidence references must be a non-empty array.")
        elif not all(type(reference) is int and reference >= 0 for reference in refs):
            _add(issues, "ERROR_EVIDENCE_INDEX", f"{path}.evidenceRefs",
                 "Frozen evidence references must be non-negative integer indexes.")
        elif len(set(refs)) != len(refs):
            _add(issues, "ERROR_EVIDENCE_UNIQUE", f"{path}.evidenceRefs",
                 "Frozen evidence references must be unique.")


def _validate_frozen_wording_row(
        row: Any, path: str, issues: list[Issue]) -> bool:
    if not isinstance(row, dict):
        _add(issues, "FROZEN_SNAPSHOT_OBJECT", path,
             "Frozen wording entry must be an object.")
        return False
    kind = row.get("kind")
    schemas = {
        "lemma": {"id", "kind", "displayLemma"},
        "meaning": {"id", "kind", "glossesEn", "internalScope"},
        "pattern": {"id", "kind", "learnerExplanationEn", "usageNote",
                    "questionOverrides", "errorNotes"},
        "example": {"id", "kind", "pl", "en"},
    }
    required = schemas.get(kind) if isinstance(kind, str) else None
    if required is None:
        _add(issues, "FROZEN_KIND", f"{path}.kind",
             "Frozen wording has an unknown entity kind.")
        return False
    if not _closed_object(row, path, required, required, issues):
        return False
    _id_syntax(row.get("id"), kind, f"{path}.id", issues)
    if kind == "lemma":
        display = row.get("displayLemma")
        if display is not None:
            _nonempty_string(display, f"{path}.displayLemma", issues, 2)
    elif kind == "meaning":
        _string_list(row.get("glossesEn"), f"{path}.glossesEn", issues,
                     min_items=1, max_items=3, unique=True)
        _nonempty_string(row.get("internalScope"), f"{path}.internalScope", issues, 3)
    elif kind == "pattern":
        _nonempty_string(row.get("learnerExplanationEn"),
                         f"{path}.learnerExplanationEn", issues, 3)
        usage_note = row.get("usageNote")
        if usage_note is not None:
            _nonempty_string(usage_note, f"{path}.usageNote", issues, 1, 240)
        overrides = row.get("questionOverrides")
        if not isinstance(overrides, list):
            _add(issues, "SCHEMA_ARRAY", f"{path}.questionOverrides",
                 "Frozen questionOverrides must be an array.")
        else:
            for index, override in enumerate(overrides):
                if override is not None:
                    _string_list(override, f"{path}.questionOverrides[{index}]",
                                 issues, min_items=1)
        notes = row.get("errorNotes")
        if not isinstance(notes, list):
            _add(issues, "SCHEMA_ARRAY", f"{path}.errorNotes",
                 "Frozen errorNotes must be an array.")
        else:
            for index, note in enumerate(notes):
                _validate_frozen_error_note(note, f"{path}.errorNotes[{index}]", issues)
    else:
        _nonempty_string(row.get("pl"), f"{path}.pl", issues, 3)
        _nonempty_string(row.get("en"), f"{path}.en", issues, 3)
    return isinstance(row.get("id"), str)


def _validate_frozen_policy_row(
        row: Any, path: str, issues: list[Issue]) -> bool:
    if not isinstance(row, dict):
        _add(issues, "FROZEN_SNAPSHOT_OBJECT", path,
             "Frozen policy entry must be an object.")
        return False
    kind = row.get("kind")
    schemas = {
        "lemma": {"id", "kind"},
        "meaning": {"id", "kind"},
        "pattern": {"id", "kind", "cefr", "teachingStatus", "usage",
                    "activityEligibility", "reviewState", "releaseMode",
                    "scopeVersion", "currentScopeDigests"},
        "example": {"id", "kind", "audioEligible"},
    }
    required = schemas.get(kind) if isinstance(kind, str) else None
    if required is None:
        _add(issues, "FROZEN_KIND", f"{path}.kind",
             "Frozen policy has an unknown entity kind.")
        return False
    if not _closed_object(row, path, required, required, issues):
        return False
    _id_syntax(row.get("id"), kind, f"{path}.id", issues)
    if kind == "pattern":
        teaching_status = row.get("teachingStatus")
        _enum(teaching_status, TEACHING_STATUSES, f"{path}.teachingStatus", issues)
        _validate_cefr(row.get("cefr"), f"{path}.cefr", teaching_status, issues)
        usage = row.get("usage")
        if _closed_object(usage, f"{path}.usage", {"priority", "register"},
                          {"priority", "register"}, issues):
            priority = usage.get("priority")
            _enum(priority, USAGE_PRIORITIES, f"{path}.usage.priority", issues)
            _enum(usage.get("register"), REGISTERS,
                  f"{path}.usage.register", issues)
            if priority == "limited" and teaching_status == "active-production":
                _add(issues, "LIMITED_ACTIVE_PRODUCTION", f"{path}.usage",
                     "Limited usage cannot be active-production.")
        eligibility = row.get("activityEligibility")
        _string_list(eligibility,
                     f"{path}.activityEligibility", issues,
                     unique=True, allowed=ACTIVITY_KEYS)
        if (isinstance(eligibility, list) and
                all(isinstance(item, str) for item in eligibility) and
                eligibility != sorted(eligibility)):
            _add(issues, "FROZEN_SET_ORDER", f"{path}.activityEligibility",
                 "Frozen activity eligibility must be lexicographically sorted.")
        eligibility_values = {
            item for item in eligibility if isinstance(item, str)
        } if isinstance(eligibility, list) else set()
        if teaching_status == "recognition-only" and (
                {"grammar-build", "type-it"} & eligibility_values):
            _add(issues, "RECOGNITION_PRODUCTION_ACTIVITY",
                 f"{path}.activityEligibility",
                 "Frozen recognition-only policy forbids productive activities.")
        if teaching_status == "deferred" and eligibility_values:
            _add(issues, "DEFERRED_ACTIVITY", f"{path}.activityEligibility",
                 "Frozen deferred policy cannot expose learner activities.")
        review_state = row.get("reviewState")
        _enum(review_state, REVIEW_STATES, f"{path}.reviewState", issues)
        # A frozen release states its own governance mode explicitly, so no
        # later tool has to infer whether the chain behind it was human.
        _enum(row.get("releaseMode"), RELEASE_MODES, f"{path}.releaseMode",
              issues)
        if eligibility_values and review_state != "approved":
            _add(issues, "UNAPPROVED_ACTIVITY", f"{path}.activityEligibility",
                 "Frozen learner activities require approved review state.")
        if (type(row.get("scopeVersion")) is not int or
                row.get("scopeVersion") != SCOPE_VERSION):
            _add(issues, "FROZEN_SCOPE_VERSION", f"{path}.scopeVersion",
                 "Frozen policy scopeVersion must be 1.")
        digests = row.get("currentScopeDigests")
        required_digests = set(STAGE_KINDS)
        if _closed_object(digests, f"{path}.currentScopeDigests",
                          required_digests, required_digests, issues):
            for stage in STAGE_KINDS:
                digest = digests.get(stage)
                if not isinstance(digest, str) or not DIGEST_RE.fullmatch(digest):
                    _add(issues, "FROZEN_SCOPE_DIGEST",
                         f"{path}.currentScopeDigests.{stage}",
                         "Frozen current scope digest must be full SHA-256.")
    elif kind == "example":
        _boolean(row.get("audioEligible"), f"{path}.audioEligible", issues)
    return isinstance(row.get("id"), str)


def _validate_frozen_review_history_row(
        row: Any, path: str, issues: list[Issue]) -> bool:
    required = {
        "id", "releaseMode", "evidenceArchive", "currentEvidenceDigests",
        "exampleOrigins", "reviewEvents"}
    if not _closed_object(row, path, required, required, issues):
        return False
    pattern_id = row.get("id")
    _id_syntax(pattern_id, "pattern", f"{path}.id", issues)
    # The history states the governance its own events ran under.  A retired
    # pattern keeps no policy row, so this is the durable home for the mode.
    _enum(row.get("releaseMode"), RELEASE_MODES, f"{path}.releaseMode", issues)
    release_mode = declared_release_mode(row)
    example_origins = row.get("exampleOrigins")
    if not isinstance(example_origins, list):
        _add(issues, "SCHEMA_ARRAY", f"{path}.exampleOrigins",
             "Frozen current example origins must be an ordered array.")
    else:
        origin_ids: list[str] = []
        for index, origin_row in enumerate(example_origins):
            origin_path = f"{path}.exampleOrigins[{index}]"
            required_origin = {"id", "origin"}
            if not _closed_object(
                    origin_row, origin_path, required_origin, required_origin, issues):
                continue
            origin_id = origin_row.get("id")
            _id_syntax(origin_id, "example", f"{origin_path}.id", issues)
            if isinstance(origin_id, str):
                origin_ids.append(origin_id)
            _validate_origin(
                origin_row.get("origin"), f"{origin_path}.origin",
                ValidationContext(), issues, fixture_mode=False,
                resolve_registry=False)
        if len(origin_ids) != len(set(origin_ids)):
            _add(issues, "FROZEN_EXAMPLE_ORIGIN_DUPLICATE",
                 f"{path}.exampleOrigins",
                 "Frozen example origins must name each current example once.")
    evidence_archive = row.get("evidenceArchive")
    archived_digests: set[str] = set()
    archive_order: list[str] = []
    context = ValidationContext()
    if not isinstance(evidence_archive, list):
        _add(issues, "SCHEMA_ARRAY", f"{path}.evidenceArchive",
             "Frozen evidence archive must be an array.")
    else:
        for index, evidence in enumerate(evidence_archive):
            evidence_path = f"{path}.evidenceArchive[{index}]"
            _validate_evidence(
                evidence, evidence_path, context, issues, resolve_registry=False)
            if not isinstance(evidence, dict):
                continue
            try:
                digest = evidence_digest(evidence)
            except (TypeError, ValueError, UnicodeError):
                continue
            if digest in archived_digests:
                _add(issues, "FROZEN_EVIDENCE_DUPLICATE", evidence_path,
                     "Frozen evidence archive digests must be unique.")
            archived_digests.add(digest)
            archive_order.append(digest)
        if archive_order != sorted(archive_order):
            _add(issues, "FROZEN_EVIDENCE_ORDER", f"{path}.evidenceArchive",
                 "Frozen evidence archive must use deterministic digest order.")
    events = row.get("reviewEvents")
    current_evidence_digests = row.get("currentEvidenceDigests")
    _string_list(current_evidence_digests, f"{path}.currentEvidenceDigests",
                 issues, unique=True)
    if isinstance(current_evidence_digests, list):
        for index, digest in enumerate(current_evidence_digests):
            if not isinstance(digest, str) or not DIGEST_RE.fullmatch(digest):
                _add(issues, "FROZEN_EVIDENCE_DIGEST",
                     f"{path}.currentEvidenceDigests[{index}]",
                     "Current evidence fingerprint must be a full SHA-256 digest.")
            elif digest not in archived_digests:
                _add(issues, "FROZEN_EVIDENCE_CURRENT_DANGLING",
                     f"{path}.currentEvidenceDigests[{index}]",
                     "Current evidence fingerprint must resolve in the archive.")
    if not isinstance(events, list):
        _add(issues, "SCHEMA_ARRAY", f"{path}.reviewEvents",
             "Frozen review history must be an array.")
        return isinstance(pattern_id, str)
    for index, event in enumerate(events):
        event_path = f"{path}.reviewEvents[{index}]"
        # The frozen row carries the governance its own events ran under, so
        # the released history is held to exactly the actor contract the
        # editorial record was held to.  Without this, a frozen envelope could
        # carry a reference verification naming a human reviewer that the
        # editorial validator would have refused outright.
        _validate_review_event(
            event, event_path, context, issues, resolve_registry=False,
            release_mode=release_mode)
        if not isinstance(event, dict):
            continue
        pins = event.get("supportingEvidenceDigests")
        if isinstance(pins, list):
            for pin_index, pin in enumerate(pins):
                if isinstance(pin, str) and pin not in archived_digests:
                    _add(issues, "FROZEN_EVIDENCE_PIN_DANGLING",
                         f"{event_path}.supportingEvidenceDigests[{pin_index}]",
                         "Historical evidence pin must resolve in the private archive.")
    _replay_review_order(
        events, release_mode, path, f"{path}.reviewEvents", issues,
        context=None)
    return isinstance(pattern_id, str)


def _derive_runtime_from_frozen(
        revision: int, identity_by_id: Mapping[str, Mapping[str, Any]],
        structure_by_id: Mapping[str, Mapping[str, Any]],
        wording_by_id: Mapping[str, Mapping[str, Any]],
        policy_by_id: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    """Rebuild the exact public projection from the four frozen dimensions."""
    admitted_pattern_ids = {
        entity_id for entity_id, policy in policy_by_id.items()
        if policy.get("kind") == "pattern" and
        policy.get("reviewState") == "approved" and
        policy.get("teachingStatus") in {"active-production", "recognition-only"}
    }
    admitted_lemma_ids: set[str] = set()
    for pattern_id in admitted_pattern_ids:
        pattern_identity = identity_by_id[pattern_id]
        meaning_identity = identity_by_id[pattern_identity["parentId"]]
        admitted_lemma_ids.add(meaning_identity["parentId"])

    meanings_by_lemma: dict[str, list[str]] = {}
    patterns_by_meaning: dict[str, list[str]] = {}
    for entity_id, identity in identity_by_id.items():
        if identity.get("kind") == "meaning":
            meanings_by_lemma.setdefault(identity["parentId"], []).append(entity_id)
        elif identity.get("kind") == "pattern":
            patterns_by_meaning.setdefault(identity["parentId"], []).append(entity_id)

    runtime_lemmas: list[dict[str, Any]] = []
    for lemma_id in sorted(admitted_lemma_ids):
        lemma_structure = structure_by_id[lemma_id]
        lemma_wording = wording_by_id[lemma_id]
        runtime_meanings: list[dict[str, Any]] = []
        for meaning_id in sorted(meanings_by_lemma.get(lemma_id, [])):
            runtime_patterns: list[dict[str, Any]] = []
            for pattern_id in sorted(patterns_by_meaning.get(meaning_id, [])):
                if pattern_id not in admitted_pattern_ids:
                    continue
                structure = structure_by_id[pattern_id]
                wording = wording_by_id[pattern_id]
                policy = policy_by_id[pattern_id]
                usage = copy.deepcopy(policy["usage"])
                if wording.get("usageNote") is not None:
                    usage["note"] = wording["usageNote"]
                runtime_pattern: dict[str, Any] = {
                    "id": pattern_id,
                    "relationType": structure["relationType"],
                    "complements": [],
                    "cefr": copy.deepcopy(policy["cefr"]),
                    "teachingStatus": policy["teachingStatus"],
                    "usage": usage,
                    "learnerExplanationEn": wording["learnerExplanationEn"],
                    "activityEligibility": sorted(policy["activityEligibility"]),
                }
                if "requiredLexicalItems" in structure:
                    runtime_pattern["requiredLexicalItems"] = copy.deepcopy(
                        structure["requiredLexicalItems"])
                for complement, override in zip(
                        structure["complements"], wording["questionOverrides"]):
                    runtime_complement = copy.deepcopy(complement)
                    if override is not None:
                        runtime_complement["questionOverridePl"] = copy.deepcopy(override)
                    runtime_pattern["complements"].append(runtime_complement)
                equivalents = sorted(
                    target for target in structure["aspectEquivalentPatternIds"]
                    if target in admitted_pattern_ids)
                if equivalents:
                    runtime_pattern["aspectEquivalentPatternIds"] = equivalents
                examples = []
                for example_id in structure["exampleIds"]:
                    example_wording = wording_by_id[example_id]
                    example_policy = policy_by_id[example_id]
                    examples.append({
                        "id": example_id,
                        "pl": example_wording["pl"],
                        "en": example_wording["en"],
                        "audioEligible": example_policy["audioEligible"],
                    })
                if examples:
                    runtime_pattern["examples"] = examples
                content_refs = sorted(
                    copy.deepcopy(structure["contentRefs"]),
                    key=lambda ref: (ref["kind"], ref["id"], ref["purpose"]))
                if content_refs:
                    runtime_pattern["contentRefs"] = content_refs
                error_notes = [{
                    "kind": note["kind"],
                    "incorrectForm": note["incorrectForm"],
                    "guidanceEn": note["guidanceEn"],
                } for note in wording["errorNotes"]]
                if error_notes:
                    runtime_pattern["errorNotes"] = error_notes
                runtime_patterns.append(runtime_pattern)
            if runtime_patterns:
                meaning_wording = wording_by_id[meaning_id]
                runtime_meanings.append({
                    "id": meaning_id,
                    "glossesEn": copy.deepcopy(meaning_wording["glossesEn"]),
                    "patterns": runtime_patterns,
                })
        runtime_lemma: dict[str, Any] = {
            "id": lemma_id,
            "canonicalLemma": lemma_structure["canonicalLemma"],
            "reflexive": lemma_structure["reflexive"],
            "aspect": lemma_structure["aspect"],
            "meanings": runtime_meanings,
        }
        if lemma_wording.get("displayLemma") is not None:
            runtime_lemma["displayLemma"] = lemma_wording["displayLemma"]
        partners = sorted(
            target for target in lemma_structure["aspectPartnerIds"]
            if target in admitted_lemma_ids)
        if partners:
            runtime_lemma["aspectPartnerIds"] = partners
        runtime_lemmas.append(runtime_lemma)
    return {
        "formatVersion": FORMAT_VERSION,
        "patternDataRevision": revision,
        "lemmas": runtime_lemmas,
    }


def _frozen_expected_review_state(
        policy: Mapping[str, Any],
        history: Mapping[str, Any]) -> ReviewCurrency:
    """Recompute a released pattern's state from the frozen audit dimensions.

    The frozen envelope cannot reach the private registries, so this reads the
    retained digests and evidence archive only.  It shares one derivation with
    the editorial validator, so a frozen release can never claim a state the
    editorial record would refuse.
    """
    scope_digests = policy.get("currentScopeDigests", {})
    if not isinstance(scope_digests, Mapping):
        scope_digests = {}
    current_evidence_rows = history.get("currentEvidenceDigests", [])
    if not isinstance(current_evidence_rows, list):
        current_evidence_rows = []
    current_evidence = set(
        digest for digest in current_evidence_rows
        if isinstance(digest, str))
    evidence_by_digest: dict[str, Mapping[str, Any]] = {}
    evidence_archive = history.get("evidenceArchive", [])
    if not isinstance(evidence_archive, list):
        evidence_archive = []
    for record in evidence_archive:
        if not isinstance(record, dict):
            continue
        try:
            evidence_by_digest[evidence_digest(record)] = record
        except (TypeError, ValueError, UnicodeError):
            continue
    return _derive_review_currency(
        history.get("reviewEvents", []), declared_release_mode(history),
        scope_digests, current_evidence, evidence_by_digest)


def _admitted_frozen_pattern_ids(
        policy_by_id: Mapping[str, Mapping[str, Any]]) -> list[str]:
    """The exact pattern set the public runtime projection admits."""
    return sorted(
        entity_id for entity_id, policy in policy_by_id.items()
        if policy.get("kind") == "pattern" and
        policy.get("reviewState") == "approved" and
        policy.get("teachingStatus") in {"active-production", "recognition-only"})


def _derive_release_authorization(
        policy_by_id: Mapping[str, Mapping[str, Any]],
        review_history_by_id: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    """State, on the release itself, which governance produced it.

    Every field is derived, never asserted, so a release cannot describe itself
    as more human-reviewed than its own retained history proves.

    The two human-coverage lists are stated per pattern rather than per release
    because a mixed release is otherwise ambiguous about which patterns a
    person actually saw.  Under the solo-maintainer mode both are ordinarily
    empty, and that emptiness is the honest statement: reference verification
    and editorial review were performed by nonhuman workflows against
    authoritative sources, and no human external verification or native review
    is being claimed.
    """
    admitted = _admitted_frozen_pattern_ids(policy_by_id)
    modes: set[str] = set()
    human_native: list[str] = []
    human_verified: list[str] = []
    for entity_id in admitted:
        history = review_history_by_id.get(entity_id)
        if not isinstance(history, Mapping):
            continue
        # Normalised, never raw: a malformed stored mode is reported by the
        # row's closed-enum check and must not be copied into a derived record.
        modes.add(declared_release_mode(history))
        currency = _frozen_expected_review_state(
            policy_by_id[entity_id], history)
        if currency.human_native_review_current:
            human_native.append(entity_id)
        if currency.human_verification_current:
            human_verified.append(entity_id)
    return {
        "releaseModes": sorted(modes),
        "humanVerifiedPatternIds": sorted(human_verified),
        "humanNativeReviewedPatternIds": sorted(human_native),
    }


def _frozen_scope_digests_for_pattern(
        pattern_id: str, identity_by_id: Mapping[str, Mapping[str, Any]],
        structure_by_id: Mapping[str, Mapping[str, Any]],
        wording_by_id: Mapping[str, Mapping[str, Any]],
        policy_by_id: Mapping[str, Mapping[str, Any]],
        history: Mapping[str, Any]) -> dict[str, str]:
    pattern_identity = identity_by_id[pattern_id]
    meaning_id = pattern_identity["parentId"]
    meaning_identity = identity_by_id[meaning_id]
    lemma_id = meaning_identity["parentId"]
    lemma_identity = identity_by_id[lemma_id]
    lemma_structure = structure_by_id[lemma_id]
    lemma_wording = wording_by_id[lemma_id]
    meaning_wording = wording_by_id[meaning_id]
    pattern_structure = structure_by_id[pattern_id]
    pattern_wording = wording_by_id[pattern_id]
    pattern_policy = policy_by_id[pattern_id]

    archive_by_digest = {
        evidence_digest(record): record
        for record in history["evidenceArchive"]
    }
    evidence = [
        copy.deepcopy(archive_by_digest[digest])
        for digest in history["currentEvidenceDigests"]
    ]

    lemma: dict[str, Any] = {
        "id": lemma_id,
        "canonicalLemma": lemma_structure["canonicalLemma"],
        "displayLemma": lemma_wording["displayLemma"],
        "reflexive": lemma_structure["reflexive"],
        "aspect": lemma_structure["aspect"],
        "aspectPartnerIds": copy.deepcopy(lemma_structure["aspectPartnerIds"]),
    }
    meaning = {
        "id": meaning_id,
        "key": meaning_identity["key"],
        "glossesEn": copy.deepcopy(meaning_wording["glossesEn"]),
        "internalScope": meaning_wording["internalScope"],
    }
    complements: list[dict[str, Any]] = []
    for complement, override in zip(
            pattern_structure["complements"],
            pattern_wording["questionOverrides"]):
        complete = copy.deepcopy(complement)
        if override is not None:
            complete["questionOverridePl"] = copy.deepcopy(override)
        complements.append(complete)
    usage = copy.deepcopy(pattern_policy["usage"])
    if pattern_wording["usageNote"] is not None:
        usage["note"] = pattern_wording["usageNote"]
    origin_by_id = {
        row["id"]: row["origin"] for row in history["exampleOrigins"]}
    examples: list[dict[str, Any]] = []
    for example_id in pattern_structure["exampleIds"]:
        example_identity = identity_by_id[example_id]
        example_wording = wording_by_id[example_id]
        example_policy = policy_by_id[example_id]
        examples.append({
            "id": example_id,
            "key": example_identity["key"],
            "pl": example_wording["pl"],
            "en": example_wording["en"],
            "origin": copy.deepcopy(origin_by_id[example_id]),
            "audioEligible": example_policy["audioEligible"],
        })
    pattern: dict[str, Any] = {
        "id": pattern_id,
        "key": pattern_identity["key"],
        "relationType": pattern_structure["relationType"],
        "complements": complements,
        "aspectEquivalentPatternIds": copy.deepcopy(
            pattern_structure["aspectEquivalentPatternIds"]),
        "cefr": copy.deepcopy(pattern_policy["cefr"]),
        "teachingStatus": pattern_policy["teachingStatus"],
        "usage": usage,
        "learnerExplanationEn": pattern_wording["learnerExplanationEn"],
        "activityEligibility": copy.deepcopy(pattern_policy["activityEligibility"]),
        "evidence": evidence,
        "errorNotes": copy.deepcopy(pattern_wording["errorNotes"]),
        "contentRefs": copy.deepcopy(pattern_structure["contentRefs"]),
    }
    if "requiredLexicalItems" in pattern_structure:
        pattern["requiredLexicalItems"] = copy.deepcopy(
            pattern_structure["requiredLexicalItems"])
    if pattern_structure["examplesPresent"]:
        pattern["examples"] = examples
    return {
        stage: review_scope_digest(stage, lemma, meaning, pattern)
        for stage in STAGE_KINDS
    }


def _validate_frozen_document(value: Any) -> list[Issue]:
    issues: list[Issue] = []
    required = {
        "artifactStatus", "formatVersion", "patternDataRevision", "allocations",
        "identity", "structure", "wording", "policy", "tombstones",
        "runtimeProjection", "reviewHistory", "releaseAuthorization"}
    if not _closed_object(value, "$frozen", required, required, issues):
        return issues
    if value.get("artifactStatus") != FROZEN_ARTIFACT_STATUS:
        _add(issues, "FROZEN_ARTIFACT_STATUS", "$frozen.artifactStatus",
             "Frozen fixture artifactStatus is incorrect.")
    if (type(value.get("formatVersion")) is not int or
            value.get("formatVersion") != FORMAT_VERSION):
        _add(issues, "FROZEN_FORMAT_VERSION", "$frozen.formatVersion",
             f"Frozen formatVersion must be {FORMAT_VERSION}.")
    revision = value.get("patternDataRevision")
    if type(revision) is not int or revision < 1:
        _add(issues, "FROZEN_REVISION", "$frozen.patternDataRevision",
             "Frozen runtime revision must be a positive integer.")
    revision_limit = revision if type(revision) is int and revision >= 1 else 0
    for collection in (
            "allocations", "identity", "structure", "wording", "policy",
            "tombstones", "reviewHistory"):
        if not isinstance(value.get(collection), list):
            _add(issues, "FROZEN_ARRAY", f"$frozen.{collection}",
                 "Frozen collection must be an array.")
    runtime_projection = value.get("runtimeProjection")
    runtime_issues = validate_runtime(runtime_projection)
    for issue in runtime_issues:
        suffix = issue.path[1:] if issue.path.startswith("$") else f".{issue.path}"
        _add(issues, f"FROZEN_RUNTIME_{issue.code}",
             f"$frozen.runtimeProjection{suffix}", issue.message)
    if isinstance(runtime_projection, dict) and runtime_projection.get(
            "patternDataRevision") != revision:
        _add(issues, "FROZEN_RUNTIME_REVISION",
             "$frozen.runtimeProjection.patternDataRevision",
             "Frozen runtime projection revision must equal patternDataRevision.")
    if issues:
        return issues
    allocation_ids: set[str] = set()
    allocations_by_id: dict[str, Mapping[str, Any]] = {}
    for index, allocation in enumerate(value["allocations"]):
        path = f"$frozen.allocations[{index}]"
        required_allocation = {
            "id", "kind", "parentId", "key", "seed", "readableStem",
            "canonicalLemmaAtAllocation", "meaningKeyAtAllocation"}
        if not _closed_object(
                allocation, path, required_allocation, required_allocation, issues):
            continue
        entity_id = allocation.get("id")
        kind = allocation.get("kind")
        if not _is_member(kind, {"lemma", "meaning", "pattern", "example"}):
            _add(issues, "FROZEN_KIND", f"{path}.kind", "Unknown frozen entity kind.")
        else:
            _id_syntax(entity_id, kind, f"{path}.id", issues)
        if not isinstance(entity_id, str):
            _add(issues, "FROZEN_ALLOCATION_ID", f"{path}.id",
                 "Allocation ID must be a string.")
            continue
        if entity_id in allocation_ids:
            _add(issues, "FROZEN_ALLOCATION_DUPLICATE", f"{path}.id",
                 "Allocated IDs are append-only and unique.")
        allocation_ids.add(entity_id)
        allocations_by_id[entity_id] = allocation
        parent_id = allocation.get("parentId")
        key = allocation.get("key")
        if kind == "lemma":
            if parent_id is not None or key is not None:
                _add(issues, "FROZEN_ALLOCATION_OWNERSHIP", path,
                     "Lemma allocation has no parent or key.")
        elif _is_member(kind, {"meaning", "pattern", "example"}):
            parent_kind = {
                "meaning": "lemma", "pattern": "meaning", "example": "pattern"}[kind]
            _id_syntax(parent_id, parent_kind, f"{path}.parentId", issues)
            _key(key, f"{path}.key", issues)
        seed = allocation.get("seed")
        _key(allocation.get("readableStem"), f"{path}.readableStem", issues)
        canonical_at_allocation = allocation.get("canonicalLemmaAtAllocation")
        if canonical_at_allocation is not None:
            _nonempty_string(
                canonical_at_allocation, f"{path}.canonicalLemmaAtAllocation", issues)
        meaning_key_at_allocation = allocation.get("meaningKeyAtAllocation")
        if meaning_key_at_allocation is not None:
            _key(meaning_key_at_allocation, f"{path}.meaningKeyAtAllocation", issues)
        if not _nonempty_string(seed, f"{path}.seed", issues) or not (
                isinstance(seed, str) and seed.startswith("v1|")):
            _add(issues, "FROZEN_SEED", f"{path}.seed",
                 "Allocation must retain its original versioned seed.")
        else:
            try:
                expected_id = _expected_allocation_id(allocation)
            except (KeyError, TypeError, ValueError, UnicodeError) as exc:
                _add(issues, "FROZEN_SEED", f"{path}.seed",
                     f"Allocation seed cannot reproduce its ID: {exc}.")
            else:
                if entity_id != expected_id:
                    _add(issues, "FROZEN_ID_RECOMPUTATION", f"{path}.id",
                         f"Allocation must reproduce its complete original ID "
                         f"{expected_id!r}, including the readable stem.")

    for entity_id, allocation in allocations_by_id.items():
        kind = allocation.get("kind")
        if not _is_member(kind, {"meaning", "pattern", "example"}):
            continue
        parent_id = allocation.get("parentId")
        parent = allocations_by_id.get(parent_id) if isinstance(parent_id, str) else None
        expected_parent_kind = {
            "meaning": "lemma", "pattern": "meaning", "example": "pattern"}[kind]
        if not isinstance(parent, Mapping):
            _add(issues, "FROZEN_ALLOCATION_PARENT_DANGLING",
                 f"$frozen.allocations[{entity_id!r}].parentId",
                 "Released child allocation must retain its parent allocation.")
        elif parent.get("kind") != expected_parent_kind:
            _add(issues, "FROZEN_ALLOCATION_PARENT_KIND",
                 f"$frozen.allocations[{entity_id!r}].parentId",
                 "Released child allocation points to the wrong parent family.")

    identity_ids: list[str] = []
    identity_by_id: dict[str, Mapping[str, Any]] = {}
    for index, row in enumerate(value["identity"]):
        path = f"$frozen.identity[{index}]"
        if not _validate_frozen_identity_row(row, path, issues):
            continue
        entity_id = row.get("id")
        kind = row.get("kind")
        identity_ids.append(entity_id)
        identity_by_id[entity_id] = row
        allocation = allocations_by_id.get(entity_id)
        if allocation is None:
            _add(issues, "FROZEN_IDENTITY_UNALLOCATED", f"{path}.id",
                 "Active frozen identity lacks an allocation record.")
        else:
            for field_name in ("kind", "parentId", "key"):
                if row.get(field_name) != allocation.get(field_name):
                    _add(issues, "FROZEN_IDENTITY_ALLOCATION", f"{path}.{field_name}",
                         "Frozen identity disagrees with its allocation record.")

    for entity_id, identity in identity_by_id.items():
        kind = identity.get("kind")
        if kind == "lemma":
            continue
        parent_id = identity.get("parentId")
        parent = identity_by_id.get(parent_id) if isinstance(parent_id, str) else None
        expected_parent_kind = {
            "meaning": "lemma", "pattern": "meaning", "example": "pattern"}.get(kind)
        if not isinstance(parent, Mapping):
            _add(issues, "FROZEN_IDENTITY_PARENT_DANGLING",
                 f"$frozen.identity[{entity_id!r}].parentId",
                 "Active frozen child identity must resolve its active parent.")
        elif parent.get("kind") != expected_parent_kind:
            _add(issues, "FROZEN_IDENTITY_PARENT_KIND",
                 f"$frozen.identity[{entity_id!r}].parentId",
                 "Active frozen child identity points to the wrong parent family.")

    tombstone_ids: list[str] = []
    for index, row in enumerate(value["tombstones"]):
        path = f"$frozen.tombstones[{index}]"
        required_tombstone = {
            "id", "kind", "formerParentId", "retirementRevision", "reason",
            "replacementIds"}
        if not _closed_object(
                row, path, required_tombstone, required_tombstone, issues):
            continue
        entity_id = row.get("id")
        kind = row.get("kind")
        if not isinstance(entity_id, str):
            _add(issues, "TOMBSTONE_ID", f"{path}.id",
                 "Tombstone ID must be a string.")
            continue
        tombstone_ids.append(entity_id)
        if _is_member(kind, {"lemma", "meaning", "pattern", "example"}):
            _id_syntax(entity_id, kind, f"{path}.id", issues)
        else:
            _add(issues, "TOMBSTONE_KIND", f"{path}.kind", "Unknown tombstone kind.")
        allocation = allocations_by_id.get(entity_id)
        if allocation is None:
            _add(issues, "TOMBSTONE_UNALLOCATED", f"{path}.id",
                 "Tombstone must retain an allocation record.")
        else:
            if allocation.get("kind") != kind:
                _add(issues, "TOMBSTONE_KIND", f"{path}.kind",
                     "Tombstone kind disagrees with allocation.")
            if allocation.get("parentId") != row.get("formerParentId"):
                _add(issues, "TOMBSTONE_PARENT", f"{path}.formerParentId",
                     "Tombstone former parent disagrees with allocation.")
        retired_revision = row.get("retirementRevision")
        if type(retired_revision) is not int or not 1 <= retired_revision <= revision_limit:
            _add(issues, "TOMBSTONE_REVISION", f"{path}.retirementRevision",
                 "Tombstone revision must be within the frozen revision range.")
        _nonempty_string(row.get("reason"), f"{path}.reason", issues, 3, 240)
        replacements = row.get("replacementIds")
        if not isinstance(replacements, list) or not all(
                isinstance(item, str) for item in replacements):
            _add(issues, "TOMBSTONE_REPLACEMENTS", f"{path}.replacementIds",
                 "replacementIds must be an array of strings.")
        elif len(set(replacements)) != len(replacements):
            _add(issues, "TOMBSTONE_REPLACEMENTS_UNIQUE",
                 f"{path}.replacementIds", "Replacement IDs must be unique.")

    snapshot_maps: dict[str, dict[str, Mapping[str, Any]]] = {}
    snapshot_validators = {
        "structure": _validate_frozen_structure_row,
        "wording": _validate_frozen_wording_row,
        "policy": _validate_frozen_policy_row,
    }
    for collection in ("structure", "wording", "policy"):
        collection_ids: list[str] = []
        collection_map: dict[str, Mapping[str, Any]] = {}
        for index, row in enumerate(value[collection]):
            path = f"$frozen.{collection}[{index}]"
            if not snapshot_validators[collection](row, path, issues):
                continue
            entity_id = row.get("id")
            kind = row.get("kind")
            collection_ids.append(entity_id)
            collection_map[entity_id] = row
            identity = identity_by_id.get(entity_id)
            if identity is None or identity.get("kind") != kind:
                _add(issues, "FROZEN_SNAPSHOT_COVERAGE", path,
                     "Snapshot entry does not match an active identity.")
        if len(collection_ids) != len(set(collection_ids)) or set(collection_ids) != set(identity_ids):
            _add(issues, "FROZEN_SNAPSHOT_COVERAGE", f"$frozen.{collection}",
                 "Every snapshot dimension must cover each active identity exactly once.")
        snapshot_maps[collection] = collection_map

    structure_by_id = snapshot_maps["structure"]
    wording_by_id = snapshot_maps["wording"]
    policy_by_id = snapshot_maps["policy"]
    for entity_id, structure_row in structure_by_id.items():
        identity = identity_by_id.get(entity_id)
        if not isinstance(identity, Mapping):
            continue
        kind = structure_row.get("kind")
        parent_field = {
            "meaning": "parentLemmaId", "pattern": "parentMeaningId",
            "example": "parentPatternId"}.get(kind)
        if parent_field is not None and structure_row.get(parent_field) != identity.get(
                "parentId"):
            _add(issues, "FROZEN_STRUCTURE_OWNERSHIP",
                 f"$frozen.structure[{entity_id!r}].{parent_field}",
                 "Frozen structural ownership disagrees with identity ownership.")
        if kind == "pattern" and structure_row.get("relationType") != identity.get(
                "relationType"):
            _add(issues, "FROZEN_STRUCTURE_RELATION",
                 f"$frozen.structure[{entity_id!r}].relationType",
                 "Frozen structural relationType disagrees with identity.")
        if kind == "pattern":
            wording_row = wording_by_id.get(entity_id)
            complements = structure_row.get("complements")
            overrides = wording_row.get("questionOverrides") if isinstance(
                wording_row, Mapping) else None
            if isinstance(complements, list) and isinstance(overrides, list) and (
                    len(complements) != len(overrides)):
                _add(issues, "FROZEN_QUESTION_OVERRIDE_PARITY",
                     f"$frozen.wording[{entity_id!r}].questionOverrides",
                     "Frozen question overrides must align positionally with complements.")
            example_ids = structure_row.get("exampleIds")
            owned_example_ids = {
                child_id for child_id, child in identity_by_id.items()
                if child.get("kind") == "example" and
                child.get("parentId") == entity_id}
            if isinstance(example_ids, list) and set(
                    item for item in example_ids if isinstance(item, str)) != (
                    owned_example_ids):
                _add(issues, "FROZEN_EXAMPLE_ORDER_COVERAGE",
                     f"$frozen.structure[{entity_id!r}].exampleIds",
                     "Ordered exampleIds must cover every example owned by the pattern.")
            if (structure_row.get("examplesPresent") is False and
                    isinstance(example_ids, list) and example_ids):
                _add(issues, "FROZEN_EXAMPLE_PRESENCE",
                     f"$frozen.structure[{entity_id!r}].examplesPresent",
                     "A pattern cannot omit examples while retaining example IDs.")

    lemma_structures = {
        entity_id: row for entity_id, row in structure_by_id.items()
        if row.get("kind") == "lemma"}
    pattern_structures = {
        entity_id: row for entity_id, row in structure_by_id.items()
        if row.get("kind") == "pattern"}
    frozen_reviewed_states = REVIEWED_STATES
    frozen_reviewed_pattern_ids = {
        entity_id for entity_id, policy_row in policy_by_id.items()
        if policy_row.get("kind") == "pattern" and
        _is_member(policy_row.get("reviewState"), frozen_reviewed_states)}
    frozen_reviewed_lemma_ids: set[str] = set()
    for reviewed_pattern_id in frozen_reviewed_pattern_ids:
        pattern_identity = identity_by_id.get(reviewed_pattern_id)
        parent_meaning_id = pattern_identity.get("parentId") if isinstance(
            pattern_identity, Mapping) else None
        meaning_identity = identity_by_id.get(
            parent_meaning_id) if isinstance(parent_meaning_id, str) else None
        lemma_id = meaning_identity.get("parentId") if isinstance(
            meaning_identity, Mapping) else None
        if isinstance(lemma_id, str):
            frozen_reviewed_lemma_ids.add(lemma_id)
    for lemma_id, row in lemma_structures.items():
        partners = row.get("aspectPartnerIds")
        if not isinstance(partners, list):
            continue
        for target_id in partners:
            if not isinstance(target_id, str):
                continue
            if target_id == lemma_id:
                _add(issues, "ASPECT_LINK_SELF", f"$frozen.structure[{lemma_id!r}]",
                     "Frozen aspect partner cannot point to itself.")
                continue
            target = lemma_structures.get(target_id)
            if target is None:
                _add(issues, "ASPECT_LINK_DANGLING",
                     f"$frozen.structure[{lemma_id!r}]",
                     "Frozen aspect partner does not resolve to an active lemma.")
            else:
                if (lemma_id not in frozen_reviewed_lemma_ids or
                        target_id not in frozen_reviewed_lemma_ids):
                    _add(issues, "ASPECT_LINK_UNREVIEWED",
                         f"$frozen.structure[{lemma_id!r}]",
                         "Frozen reciprocal lemma aspect links require current "
                         "external-or-later review on both sides.")
                target_partners = target.get("aspectPartnerIds", [])
                if not isinstance(target_partners, list) or lemma_id not in target_partners:
                    _add(issues, "ASPECT_LINK_NONRECIPROCAL",
                         f"$frozen.structure[{lemma_id!r}]",
                         "Frozen aspect partner link is not reciprocal.")
    for pattern_id, row in pattern_structures.items():
        equivalents = row.get("aspectEquivalentPatternIds")
        if not isinstance(equivalents, list):
            continue
        for target_id in equivalents:
            if not isinstance(target_id, str):
                continue
            if target_id == pattern_id:
                _add(issues, "ASPECT_PATTERN_SELF",
                     f"$frozen.structure[{pattern_id!r}]",
                     "Frozen aspect-equivalent pattern cannot point to itself.")
                continue
            target = pattern_structures.get(target_id)
            if target is None:
                _add(issues, "ASPECT_PATTERN_DANGLING",
                     f"$frozen.structure[{pattern_id!r}]",
                     "Frozen aspect-equivalent pattern does not resolve.")
            else:
                if (pattern_id not in frozen_reviewed_pattern_ids or
                        target_id not in frozen_reviewed_pattern_ids):
                    _add(issues, "ASPECT_PATTERN_UNREVIEWED",
                         f"$frozen.structure[{pattern_id!r}]",
                         "Frozen aspect-equivalent links require both pattern "
                         "records to be externally reviewed or later.")
                target_equivalents = target.get("aspectEquivalentPatternIds", [])
                if not isinstance(target_equivalents, list) or (
                        pattern_id not in target_equivalents):
                    _add(issues, "ASPECT_PATTERN_NONRECIPROCAL",
                         f"$frozen.structure[{pattern_id!r}]",
                         "Frozen aspect-equivalent pattern link is not reciprocal.")

    for entity_id, policy_row in policy_by_id.items():
        if policy_row.get("kind") == "pattern":
            wording_row = wording_by_id.get(entity_id)
            usage = policy_row.get("usage")
            if (isinstance(usage, Mapping) and usage.get("priority") == "limited" and
                    isinstance(wording_row, Mapping) and
                    wording_row.get("usageNote") is None):
                _add(issues, "LIMITED_NOTE_REQUIRED",
                     f"$frozen.wording[{entity_id!r}].usageNote",
                     "Frozen limited usage must retain its learner-facing note.")
            if policy_row.get("reviewState") == "approved":
                pattern_identity = identity_by_id.get(entity_id)
                meaning_identity = identity_by_id.get(
                    pattern_identity.get("parentId")) if isinstance(
                        pattern_identity, Mapping) and isinstance(
                            pattern_identity.get("parentId"), str) else None
                lemma_structure = structure_by_id.get(
                    meaning_identity.get("parentId")) if isinstance(
                        meaning_identity, Mapping) and isinstance(
                            meaning_identity.get("parentId"), str) else None
                if isinstance(lemma_structure, Mapping) and lemma_structure.get(
                        "aspect") == "unresolved":
                    _add(issues, "APPROVED_ASPECT_UNRESOLVED",
                         f"$frozen.policy[{entity_id!r}].reviewState",
                         "Frozen approved patterns require resolved lemma aspect.")
        elif policy_row.get("kind") == "example" and policy_row.get(
                "audioEligible") is True:
            identity = identity_by_id.get(entity_id)
            parent_id = identity.get("parentId") if isinstance(identity, Mapping) else None
            parent_policy = policy_by_id.get(parent_id) if isinstance(
                parent_id, str) else None
            if (not isinstance(parent_policy, Mapping) or
                    parent_policy.get("reviewState") != "approved" or (
                        "listening" not in parent_policy.get(
                            "activityEligibility", []) and not (
                                type(revision) is int and revision >= 2))):
                _add(issues, "AUDIO_NOT_AUTHORIZED",
                     f"$frozen.policy[{entity_id!r}].audioEligible",
                     "Frozen revision 1 audio requires approved Listening; "
                     "revision 2 may authorize pronunciation independently.")

    review_history_ids: list[str] = []
    review_history_by_id: dict[str, Mapping[str, Any]] = {}
    for index, row in enumerate(value["reviewHistory"]):
        path = f"$frozen.reviewHistory[{index}]"
        if not _validate_frozen_review_history_row(row, path, issues):
            continue
        pattern_id = row.get("id")
        row_policy = policy_by_id.get(pattern_id)
        if (isinstance(row_policy, Mapping) and
                row_policy.get("releaseMode") != row.get("releaseMode")):
            _add(issues, "FROZEN_RELEASE_MODE_PARITY", f"{path}.releaseMode",
                 "An active pattern's released governance mode must be the "
                 "same in its policy row and its review history.")
        review_history_ids.append(pattern_id)
        review_history_by_id[pattern_id] = row
        allocation = allocations_by_id.get(pattern_id)
        if not isinstance(allocation, Mapping) or allocation.get("kind") != "pattern":
            _add(issues, "FROZEN_REVIEW_HISTORY_ID", f"{path}.id",
                 "Frozen review history must belong to an allocated pattern.")
    expected_review_history_ids = {
        entity_id for entity_id, allocation in allocations_by_id.items()
        if allocation.get("kind") == "pattern"}
    if (len(review_history_ids) != len(set(review_history_ids)) or
            set(review_history_ids) != expected_review_history_ids):
        _add(issues, "FROZEN_REVIEW_HISTORY_COVERAGE", "$frozen.reviewHistory",
             "Review history must cover every active or retired pattern exactly once.")
    for pattern_id, wording_row in wording_by_id.items():
        if wording_row.get("kind") != "pattern":
            continue
        history_row = review_history_by_id.get(pattern_id)
        policy_row = policy_by_id.get(pattern_id)
        current_external_pins: set[str] = set()
        expected_state: str | None = None
        if isinstance(history_row, Mapping) and isinstance(policy_row, Mapping):
            structure_row = structure_by_id.get(pattern_id)
            example_origins = history_row.get("exampleOrigins")
            if isinstance(structure_row, Mapping) and isinstance(
                    structure_row.get("exampleIds"), list) and isinstance(
                        example_origins, list):
                origin_ids = [
                    row.get("id") for row in example_origins
                    if isinstance(row, Mapping)]
                if origin_ids != structure_row["exampleIds"]:
                    _add(issues, "FROZEN_EXAMPLE_ORIGIN_COVERAGE",
                         f"$frozen.reviewHistory[{pattern_id!r}].exampleOrigins",
                         "Frozen example origins must exactly follow the current "
                         "ordered example IDs.")
            try:
                recomputed_scope_digests = _frozen_scope_digests_for_pattern(
                    pattern_id, identity_by_id, structure_by_id,
                    wording_by_id, policy_by_id, history_row)
            except (KeyError, TypeError, ValueError, UnicodeError):
                _add(issues, "FROZEN_SCOPE_RECOMPUTATION",
                     f"$frozen.policy[{pattern_id!r}].currentScopeDigests",
                     "Frozen current scope digests cannot be reconstructed from "
                     "the closed audit dimensions.")
            else:
                if policy_row.get("currentScopeDigests") != recomputed_scope_digests:
                    _add(issues, "FROZEN_SCOPE_PARITY",
                         f"$frozen.policy[{pattern_id!r}].currentScopeDigests",
                         "Frozen scope digests must exactly match the canonical "
                         "projection reconstructed from the closed audit dimensions.")
            currency = _frozen_expected_review_state(policy_row, history_row)
            expected_state = currency.state
            current_external_pins = set(currency.verification_pins)
            if policy_row.get("reviewState") != expected_state:
                _add(issues, "FROZEN_REVIEW_STATE_MISMATCH",
                     f"$frozen.policy[{pattern_id!r}].reviewState",
                     f"Frozen event history and retained current digests require "
                     f"{expected_state!r}.")
        current_evidence = history_row.get("currentEvidenceDigests", []) if isinstance(
            history_row, Mapping) else []
        evidence_count = len(current_evidence) if isinstance(current_evidence, list) else 0
        notes = wording_row.get("errorNotes", [])
        if not isinstance(notes, list):
            continue
        for note_index, note in enumerate(notes):
            refs = note.get("evidenceRefs", []) if isinstance(note, dict) else []
            if not isinstance(refs, list):
                continue
            for ref_index, reference in enumerate(refs):
                if type(reference) is int and reference >= evidence_count:
                    _add(issues, "ERROR_EVIDENCE_DANGLING",
                         f"$frozen.wording[{pattern_id!r}].errorNotes["
                         f"{note_index}].evidenceRefs[{ref_index}]",
                         "Frozen error-note evidence index does not resolve in "
                         "the retained current evidence order.")
                elif (type(reference) is int and reference >= 0 and
                      _is_member(expected_state, REVIEWED_STATES) and
                      isinstance(current_evidence, list) and
                      reference < len(current_evidence) and
                      current_evidence[reference] not in current_external_pins):
                    _add(issues, "ERROR_EVIDENCE_NOT_EXTERNALLY_PINNED",
                         f"$frozen.wording[{pattern_id!r}].errorNotes["
                         f"{note_index}].evidenceRefs[{ref_index}]",
                         "Frozen evidence used by a currently reviewed error claim "
                         "must be pinned by the current external acceptance.")

    if len(set(identity_ids)) != len(identity_ids):
        _add(issues, "FROZEN_ACTIVE_DUPLICATE", "$frozen.identity",
             "Active identity snapshot IDs must be unique.")
    if len(set(tombstone_ids)) != len(tombstone_ids):
        _add(issues, "TOMBSTONE_DUPLICATE", "$frozen.tombstones",
             "Tombstone IDs must be unique.")
    if set(identity_ids) & set(tombstone_ids):
        _add(issues, "TOMBSTONE_RESURRECTION", "$frozen",
             "An ID cannot be active and tombstoned simultaneously.")
    if set(identity_ids) | set(tombstone_ids) != allocation_ids:
        _add(issues, "FROZEN_ALLOCATION_COVERAGE", "$frozen.allocations",
             "Every allocation must be either active or tombstoned, and vice versa.")
    for index, row in enumerate(value["tombstones"]):
        if not isinstance(row, dict) or not isinstance(row.get("replacementIds"), list):
            continue
        for replacement_index, replacement in enumerate(row["replacementIds"]):
            target = allocations_by_id.get(replacement) if isinstance(
                replacement, str) else None
            replacement_path = (
                f"$frozen.tombstones[{index}].replacementIds[{replacement_index}]")
            if target is None:
                _add(issues, "TOMBSTONE_REPLACEMENT_DANGLING", replacement_path,
                     "Frozen replacement must resolve to a retained allocation.")
            elif target.get("kind") != row.get("kind"):
                _add(issues, "TOMBSTONE_REPLACEMENT_KIND", replacement_path,
                     "Frozen replacement must have the same entity kind.")
    for rows_path, rows in (
            ("$frozen.allocations", value["allocations"]),
            ("$frozen.identity", value["identity"]),
            ("$frozen.structure", value["structure"]),
            ("$frozen.wording", value["wording"]),
            ("$frozen.policy", value["policy"]),
            ("$frozen.tombstones", value["tombstones"]),
            ("$frozen.reviewHistory", value["reviewHistory"])):
        ids_in_order = [row.get("id") for row in rows if isinstance(row, dict)]
        if ids_in_order != sorted(ids_in_order, key=lambda item: str(item)):
            _add(issues, "FROZEN_ORDER", rows_path,
                 "Frozen records must use deterministic ID order.")
    authorization = value["releaseAuthorization"]
    required_authorization = {
        "releaseModes", "humanVerifiedPatternIds",
        "humanNativeReviewedPatternIds"}
    if _closed_object(authorization, "$frozen.releaseAuthorization",
                      required_authorization, required_authorization, issues):
        _string_list(authorization.get("releaseModes"),
                     "$frozen.releaseAuthorization.releaseModes", issues,
                     min_items=1, unique=True, allowed=set(RELEASE_MODES))
        for coverage_field in (
                "humanVerifiedPatternIds", "humanNativeReviewedPatternIds"):
            _string_list(
                authorization.get(coverage_field),
                f"$frozen.releaseAuthorization.{coverage_field}",
                issues, unique=True)

    if not issues:
        expected_runtime = _derive_runtime_from_frozen(
            revision, identity_by_id, structure_by_id, wording_by_id, policy_by_id)
        if value["runtimeProjection"] != expected_runtime:
            _add(issues, "FROZEN_RUNTIME_PARITY", "$frozen.runtimeProjection",
                 "Runtime projection must be exactly derivable from the four "
                 "closed frozen dimensions.")
        expected_authorization = _derive_release_authorization(
            policy_by_id, review_history_by_id)
        if authorization != expected_authorization:
            _add(issues, "FROZEN_RELEASE_AUTHORIZATION_PARITY",
                 "$frozen.releaseAuthorization",
                 "The release authorization record must be exactly derivable "
                 "from the admitted patterns' declared modes and retained "
                 "review history.")
    return issues


def validate_frozen_release(value: Any) -> list[Issue]:
    """Validate the complete frozen release envelope, not runtime shape alone."""
    return _validate_frozen_document(value)


def verified_runtime_from_frozen(value: Any) -> dict[str, Any]:
    """Return runtime bytes only after the complete frozen envelope validates."""
    issues = validate_frozen_release(value)
    if issues:
        raise ValidationFailure(issues)
    return copy.deepcopy(value["runtimeProjection"])


def _validate_tombstone(
        tombstone: Any, path: str, revision: int,
        previous_identity: Mapping[str, Mapping[str, Any]],
        current_entities: Mapping[str, _EntityInfo],
        all_allocation_ids: set[str],
        issues: list[Issue]) -> None:
    required = {
        "id", "kind", "formerParentId", "retirementRevision", "reason",
        "replacementIds"}
    if not _closed_object(tombstone, path, required, required, issues):
        return
    entity_id = tombstone.get("id")
    kind = tombstone.get("kind")
    if not _is_member(kind, {"lemma", "meaning", "pattern", "example"}):
        _add(issues, "TOMBSTONE_KIND", f"{path}.kind", "Unknown tombstone kind.")
    elif not _id_syntax(entity_id, kind, f"{path}.id", issues):
        pass
    if tombstone.get("retirementRevision") != revision:
        _add(issues, "TOMBSTONE_REVISION", f"{path}.retirementRevision",
             "New tombstone retirementRevision must equal the transition revision.")
    _nonempty_string(tombstone.get("reason"), f"{path}.reason", issues, 3, 240)
    replacements = tombstone.get("replacementIds")
    if not isinstance(replacements, list):
        _add(issues, "TOMBSTONE_REPLACEMENTS", f"{path}.replacementIds",
             "replacementIds must be an array, empty when there is no replacement.")
        replacements = []
    elif not all(isinstance(item, str) for item in replacements):
        _add(issues, "TOMBSTONE_REPLACEMENTS", f"{path}.replacementIds",
             "Replacement IDs must all be strings.")
        replacements = []
    elif len(set(replacements)) != len(replacements):
        _add(issues, "TOMBSTONE_REPLACEMENTS_UNIQUE", f"{path}.replacementIds",
             "Replacement IDs must be unique.")
    for index, replacement in enumerate(replacements):
        replacement_path = f"{path}.replacementIds[{index}]"
        if replacement == entity_id:
            _add(issues, "TOMBSTONE_REPLACEMENT_SELF", replacement_path,
                 "A tombstone cannot replace itself.")
        if replacement not in current_entities:
            _add(issues, "TOMBSTONE_REPLACEMENT_DANGLING", replacement_path,
                 "Replacement ID must resolve to a current active entity.")
        elif current_entities[replacement].kind != kind:
            _add(issues, "TOMBSTONE_REPLACEMENT_KIND", replacement_path,
                 "Replacement entity must have the same kind as the tombstone.")
        if replacement not in all_allocation_ids:
            _add(issues, "TOMBSTONE_REPLACEMENT_UNALLOCATED", replacement_path,
                 "Replacement ID must have an allocation record.")
    prior = previous_identity.get(entity_id)
    if prior is None:
        _add(issues, "TOMBSTONE_UNKNOWN_ID", f"{path}.id",
             "Only a previously active allocated ID can be newly tombstoned.")
    else:
        if prior.get("kind") != kind:
            _add(issues, "TOMBSTONE_KIND", f"{path}.kind",
                 "Tombstone kind disagrees with the former entity.")
        if prior.get("parentId") != tombstone.get("formerParentId"):
            _add(issues, "TOMBSTONE_PARENT", f"{path}.formerParentId",
                 "Tombstone formerParentId disagrees with frozen ownership.")


def _entity_has_new_correction(
        entity: _EntityInfo, entities: Sequence[_EntityInfo],
        context: ValidationContext,
        new_events_by_pattern: Mapping[str, Sequence[Mapping[str, Any]]]) -> bool:
    if entity.kind == "lemma":
        pattern_ids = {
            item.entity_id for item in entities
            if item.kind == "pattern" and
            item.lemma.get("id") == entity.entity_id}
    elif entity.kind == "meaning":
        pattern_ids = {
            item.entity_id for item in entities
            if item.kind == "pattern" and item.parent_id == entity.entity_id}
    elif entity.kind == "pattern":
        pattern_ids = {entity.entity_id}
    elif entity.kind == "example":
        pattern_ids = {entity.parent_id} if isinstance(entity.parent_id, str) else set()
    else:
        pattern_ids = set()

    def authorized(event: Any) -> bool:
        if not isinstance(event, dict) or event.get("kind") != "correction" or (
                event.get("decision") != "accept") or not bool(event.get("note")):
            return False
        reviewer_ref = event.get("reviewerRef")
        reviewer = context.reviewer_registry.get(reviewer_ref) if isinstance(
            reviewer_ref, str) else None
        roles = reviewer.get("roles") if isinstance(reviewer, Mapping) else None
        return isinstance(roles, list) and "product-approval" in roles

    return bool(pattern_ids) and all(any(
        authorized(event) for event in new_events_by_pattern.get(pattern_id, ()))
        for pattern_id in pattern_ids)


def freeze_editorial(
        document: Any, pattern_data_revision: int,
        context: ValidationContext | None = None, *,
        previous: Mapping[str, Any] | None = None,
        tombstones: Iterable[Mapping[str, Any]] = (),
        legacy_reflexive_correction_ids: Iterable[str] = ()) -> dict[str, Any]:
    """Create or advance an independent fictional frozen Priority 7 baseline.

    Previous allocation records and tombstones are append-only.  Released IDs
    validate against those records instead of being rehashed from corrected
    wording.  The returned object is a test/private audit artifact, never a
    runtime corpus.
    """
    if context is None:
        context = ValidationContext()
    issues: list[Issue] = []
    if type(pattern_data_revision) is not int or pattern_data_revision < 1:
        raise ValidationFailure([Issue(
            "FROZEN_REVISION", "$frozen.patternDataRevision",
            "Frozen runtime revision must be a positive integer.")])
    if previous is None and pattern_data_revision != 1:
        _add(issues, "FROZEN_INITIAL_REVISION", "$frozen.patternDataRevision",
             "The first fictional released runtime snapshot starts at revision 1.")
    try:
        tombstone_rows_input = list(tombstones)
    except TypeError:
        raise ValidationFailure([Issue(
            "TOMBSTONE_COLLECTION", "$newTombstones",
            "New tombstones must be an iterable of closed tombstone objects.")])
    try:
        legacy_ids_list = list(legacy_reflexive_correction_ids)
    except TypeError:
        raise ValidationFailure([Issue(
            "FROZEN_LEGACY_REFLEXIVE_IDS", "$legacyReflexiveCorrectionIds",
            "Legacy reflexive correction IDs must be an iterable of lemma IDs.")])
    if (any(not isinstance(item, str) for item in legacy_ids_list) or
            len(set(legacy_ids_list)) != len(legacy_ids_list)):
        raise ValidationFailure([Issue(
            "FROZEN_LEGACY_REFLEXIVE_IDS", "$legacyReflexiveCorrectionIds",
            "Legacy reflexive correction IDs must be unique strings.")])
    legacy_reflexive_ids = set(legacy_ids_list)
    if previous is None and legacy_reflexive_ids:
        raise ValidationFailure([Issue(
            "FROZEN_LEGACY_REFLEXIVE_SCOPE", "$legacyReflexiveCorrectionIds",
            "Legacy Boolean repair is valid only for an explicit prior baseline.")])

    previous_allocations: dict[str, Mapping[str, Any]] = {}
    previous_identity: dict[str, Mapping[str, Any]] = {}
    previous_structure: dict[str, Mapping[str, Any]] = {}
    previous_wording: dict[str, Mapping[str, Any]] = {}
    previous_tombstones: dict[str, Mapping[str, Any]] = {}
    previous_review_history: dict[str, Mapping[str, Any]] = {}
    if previous is not None:
        prior_issues = _validate_frozen_document(previous)
        if prior_issues:
            if not legacy_reflexive_ids:
                raise ValidationFailure(prior_issues)
            sanitized_previous = copy.deepcopy(previous)
            legacy_issues: list[Issue] = []
            runtime_lemmas = {
                lemma.get("id"): lemma
                for lemma in sanitized_previous.get(
                    "runtimeProjection", {}).get("lemmas", [])
                if isinstance(lemma, dict) and isinstance(lemma.get("id"), str)}
            structure_lemmas = {
                row.get("id"): row
                for row in sanitized_previous.get("structure", [])
                if isinstance(row, dict) and row.get("kind") == "lemma" and
                isinstance(row.get("id"), str)}
            for lemma_id in legacy_reflexive_ids:
                structure_row = structure_lemmas.get(lemma_id)
                runtime_row = runtime_lemmas.get(lemma_id)
                if not isinstance(structure_row, dict) or not isinstance(
                        runtime_row, dict):
                    _add(legacy_issues, "FROZEN_LEGACY_REFLEXIVE_SCOPE",
                         "$legacyReflexiveCorrectionIds",
                         f"Legacy lemma {lemma_id!r} must exist in frozen structure "
                         "and the valid runtime projection.")
                    continue
                canonical = structure_row.get("canonicalLemma")
                expected_reflexive = (
                    normalize_canonical_lemma(canonical).endswith(" się")
                    if isinstance(canonical, str) else None)
                if (type(structure_row.get("reflexive")) is not bool or
                        structure_row.get("reflexive") == expected_reflexive or
                        runtime_row.get("canonicalLemma") != canonical or
                        runtime_row.get("reflexive") != expected_reflexive):
                    _add(legacy_issues, "FROZEN_LEGACY_REFLEXIVE_SCOPE",
                         "$legacyReflexiveCorrectionIds",
                         f"Legacy lemma {lemma_id!r} is not exactly one redundant "
                         "Boolean mismatch against an otherwise valid runtime lemma.")
                    continue
                structure_row["reflexive"] = expected_reflexive
            if legacy_issues:
                raise ValidationFailure(legacy_issues)
            sanitized_issues = _validate_frozen_document(sanitized_previous)
            if sanitized_issues:
                raise ValidationFailure(prior_issues)
        elif legacy_reflexive_ids:
            raise ValidationFailure([Issue(
                "FROZEN_LEGACY_REFLEXIVE_SCOPE", "$legacyReflexiveCorrectionIds",
                "The prior baseline is already valid; no legacy Boolean exception "
                "is permitted.")])
        previous_allocations = {
            row["id"]: row for row in previous["allocations"]}
        previous_identity = {row["id"]: row for row in previous["identity"]}
        previous_structure = {row["id"]: row for row in previous["structure"]}
        previous_wording = {row["id"]: row for row in previous["wording"]}
        previous_tombstones = {row["id"]: row for row in previous["tombstones"]}
        previous_review_history = {
            row["id"]: row for row in previous["reviewHistory"]}

    validation_context = dataclasses.replace(
        context, allocation_registry=previous_allocations)
    editorial_issues = validate_editorial(document, validation_context)
    if editorial_issues:
        raise ValidationFailure(editorial_issues)
    collector_issues: list[Issue] = []
    entities = _validate_hierarchy(
        document["lemmas"], validation_context, collector_issues,
        fixture_mode=False, require_nonempty=False, resolve_registries=True)
    if collector_issues:
        raise ValidationFailure(collector_issues)
    runtime_projection = project_runtime_nonrelease(
        document, pattern_data_revision, validation_context)
    current_by_id = {entity.entity_id: entity for entity in entities}
    current_ids = set(current_by_id)

    review_history = {
        pattern_id: copy.deepcopy(dict(row))
        for pattern_id, row in previous_review_history.items()}
    new_events_by_pattern: dict[str, list[Mapping[str, Any]]] = {}
    for entity in entities:
        if entity.kind != "pattern":
            continue
        current_events = copy.deepcopy(entity.record.get("reviewEvents", []))
        prior_row = previous_review_history.get(entity.entity_id)
        prior_events = prior_row.get("reviewEvents", []) if isinstance(
            prior_row, Mapping) else []
        history_is_prefix = (
            isinstance(prior_events, list) and
            len(current_events) >= len(prior_events) and
            current_events[:len(prior_events)] == prior_events)
        if not history_is_prefix:
            _add(issues, "FROZEN_REVIEW_HISTORY_NOT_APPEND_ONLY", entity.path,
                 "Released pattern review history must retain the prior event "
                 "array as an exact prefix.")
            new_events_by_pattern[entity.entity_id] = []
        else:
            new_events_by_pattern[entity.entity_id] = current_events[len(prior_events):]
        archived_by_digest: dict[str, Mapping[str, Any]] = {}
        prior_current_evidence = prior_row.get(
            "currentEvidenceDigests", []) if isinstance(prior_row, Mapping) else []
        if isinstance(prior_row, Mapping):
            for evidence in prior_row.get("evidenceArchive", []):
                if isinstance(evidence, dict):
                    try:
                        archived_by_digest[evidence_digest(evidence)] = copy.deepcopy(evidence)
                    except (TypeError, ValueError, UnicodeError):
                        pass
        for evidence in entity.record.get("evidence", []):
            if isinstance(evidence, dict):
                archived_by_digest[evidence_digest(evidence)] = copy.deepcopy(evidence)
        current_evidence_digests = [
            evidence_digest(evidence) for evidence in entity.record.get("evidence", [])]
        evidence_is_prefix = (
            isinstance(prior_current_evidence, list) and
            len(current_evidence_digests) >= len(prior_current_evidence) and
            current_evidence_digests[:len(prior_current_evidence)] ==
            prior_current_evidence)
        if not evidence_is_prefix:
            _add(issues, "FROZEN_EVIDENCE_NOT_APPEND_ONLY", entity.path,
                 "Released evidence order is append-only so numeric error-note "
                 "references cannot silently retarget.")
        review_history[entity.entity_id] = {
            "id": entity.entity_id,
            "releaseMode": declared_release_mode(entity.record),
            "evidenceArchive": [
                archived_by_digest[digest] for digest in sorted(archived_by_digest)],
            "currentEvidenceDigests": current_evidence_digests,
            "exampleOrigins": [{
                "id": example["id"],
                "origin": copy.deepcopy(example["origin"]),
            } for example in entity.record.get("examples", [])],
            "reviewEvents": current_events,
        }
        prior_origins_by_id = {
            row.get("id"): row.get("origin")
            for row in prior_row.get("exampleOrigins", [])
            if isinstance(row, Mapping) and isinstance(row.get("id"), str)
        } if isinstance(prior_row, Mapping) and isinstance(
            prior_row.get("exampleOrigins"), list) else {}
        current_origins_by_id = {
            row["id"]: row["origin"]
            for row in review_history[entity.entity_id]["exampleOrigins"]}
        retained_origin_changed = any(
            example_id in current_origins_by_id and
            current_origins_by_id[example_id] != prior_origin
            for example_id, prior_origin in prior_origins_by_id.items())
        if (retained_origin_changed and not _entity_has_new_correction(
                entity, entities, context, new_events_by_pattern)):
            _add(issues, "FROZEN_ORIGIN_CORRECTION_REQUIRED", entity.path,
                 "Changing a retained example's released origin requires a fresh "
                 "owner-authorized correction event.")

    for lemma_id in legacy_reflexive_ids:
        entity = current_by_id.get(lemma_id)
        prior_structure = previous_structure.get(lemma_id)
        prior_identity = previous_identity.get(lemma_id)
        if (not isinstance(entity, _EntityInfo) or entity.kind != "lemma" or
                not isinstance(prior_structure, Mapping) or
                not isinstance(prior_identity, Mapping)):
            _add(issues, "FROZEN_LEGACY_REFLEXIVE_SCOPE",
                 "$legacyReflexiveCorrectionIds",
                 f"Legacy lemma {lemma_id!r} must retain its active lemma identity.")
            continue
        current_structure = _structure_for_entity(entity)
        canonical = current_structure.get("canonicalLemma")
        expected_reflexive = (
            normalize_canonical_lemma(canonical).endswith(" się")
            if isinstance(canonical, str) else None)
        if (canonical != prior_structure.get("canonicalLemma") or
                current_structure.get("reflexive") != expected_reflexive or
                _identity_for_entity(entity) != prior_identity or
                not _entity_has_new_correction(
                    entity, entities, context, new_events_by_pattern)):
            _add(issues, "FROZEN_LEGACY_REFLEXIVE_SCOPE",
                 "$legacyReflexiveCorrectionIds",
                 "Legacy redundant-Boolean repair requires unchanged canonical "
                 "bytes/identity/ownership, the canonical Boolean value, and a fresh "
                 "owner-authorized correction event on every affected pattern.")

    allocations = {key: copy.deepcopy(dict(value))
                   for key, value in previous_allocations.items()}
    for entity in entities:
        if entity.entity_id not in allocations:
            allocation = _allocation_for_entity(entity)
            if _sha12(allocation["seed"]) != entity.entity_id.rsplit("-", 1)[-1]:
                _add(issues, "FROZEN_NEW_ID_HASH", f"{entity.path}.id",
                     "New allocation ID does not match its original seed.")
            allocations[entity.entity_id] = allocation

    proposed_tombstones = {
        key: copy.deepcopy(dict(value))
        for key, value in previous_tombstones.items()}
    for index, tombstone in enumerate(tombstone_rows_input):
        if not isinstance(tombstone, Mapping):
            _add(issues, "TOMBSTONE_OBJECT", f"$newTombstones[{index}]",
                 "New tombstone must be an object.")
            continue
        entity_id = tombstone.get("id")
        if not isinstance(entity_id, str):
            _add(issues, "TOMBSTONE_ID", f"$newTombstones[{index}].id",
                 "New tombstone ID must be a string.")
            continue
        if entity_id in proposed_tombstones:
            _add(issues, "TOMBSTONE_IMMUTABLE", f"$newTombstones[{index}].id",
                 "Existing tombstones are immutable and cannot be re-added or edited.")
            continue
        proposed_tombstones[entity_id] = copy.deepcopy(dict(tombstone))

    all_allocation_ids = set(allocations)
    for tombstone_id, tombstone in proposed_tombstones.items():
        if tombstone_id in previous_tombstones:
            if tombstone != previous_tombstones[tombstone_id]:
                _add(issues, "TOMBSTONE_IMMUTABLE", "$frozen.tombstones",
                     "A prior tombstone changed or disappeared.")
            continue
        _validate_tombstone(
            tombstone, "$newTombstones", pattern_data_revision,
            previous_identity, current_by_id, all_allocation_ids, issues)

    for entity_id, prior_identity in previous_identity.items():
        if entity_id not in current_ids and entity_id not in proposed_tombstones:
            _add(issues, "FROZEN_REMOVAL_WITHOUT_TOMBSTONE", "$frozen.identity",
                 f"Released ID {entity_id!r} disappeared without a tombstone.")
    for entity_id in current_ids:
        if entity_id in proposed_tombstones:
            _add(issues, "TOMBSTONE_RESURRECTION", current_by_id[entity_id].path,
                 "A tombstoned ID cannot become active again.")

    for entity_id, entity in current_by_id.items():
        prior_identity = previous_identity.get(entity_id)
        if prior_identity is not None:
            current_identity = _identity_for_entity(entity)
            for immutable in ("kind", "parentId", "key"):
                if prior_identity.get(immutable) != current_identity.get(immutable):
                    _add(issues, "FROZEN_IDENTITY_DRIFT", entity.path,
                         f"Released {immutable} changed in place.")
            if entity.kind == "pattern" and prior_identity.get(
                    "relationType") != current_identity.get("relationType"):
                _add(issues, "FROZEN_RELATION_REPLACEMENT_REQUIRED", entity.path,
                     "Released relationType change requires a new ID and tombstone.")
        prior_structure = previous_structure.get(entity_id)
        if prior_structure is None:
            continue
        current_structure = _structure_for_entity(entity)
        if entity.kind == "pattern":
            if prior_structure.get("relationType") != current_structure.get("relationType"):
                _add(issues, "FROZEN_RELATION_REPLACEMENT_REQUIRED", entity.path,
                     "Released relationType change requires replacement.")
            if prior_structure.get("complements") != current_structure.get("complements"):
                _add(issues, "FROZEN_COMPLEMENT_REPLACEMENT_REQUIRED", entity.path,
                     "Released complement identity change requires replacement.")
        elif entity.kind == "lemma":
            prior_canonical = prior_structure.get("canonicalLemma")
            current_canonical = current_structure.get("canonicalLemma")
            if isinstance(prior_canonical, str) and isinstance(current_canonical, str):
                prior_reflexive_identity = normalize_canonical_lemma(
                    prior_canonical).endswith(" się")
                current_reflexive_identity = normalize_canonical_lemma(
                    current_canonical).endswith(" się")
                if prior_reflexive_identity != current_reflexive_identity:
                    _add(issues, "FROZEN_LEXICAL_SIE_REPLACEMENT_REQUIRED", entity.path,
                         "Adding or removing lexical 'się' requires replacement.")
                elif (prior_canonical != current_canonical or
                      prior_structure.get("reflexive") != current_structure.get("reflexive")) and not (
                        _entity_has_new_correction(
                            entity, entities, context, new_events_by_pattern)):
                    _add(issues, "FROZEN_CORRECTION_REQUIRED", entity.path,
                         "Same-identity lemma/reflexive correction requires correction events.")
        prior_wording = previous_wording.get(entity_id)
        if (prior_wording is not None and
                prior_wording != _wording_for_entity(entity) and
                not _entity_has_new_correction(
                    entity, entities, context, new_events_by_pattern)):
            _add(issues, "FROZEN_WORDING_CORRECTION_REQUIRED", entity.path,
                 "Released wording changes require a new owner-authorized "
                 "correction audit event on every affected pattern.")

    identity = sorted(
        (_identity_for_entity(entity) for entity in entities), key=lambda row: row["id"])
    structure = sorted(
        (_structure_for_entity(entity) for entity in entities), key=lambda row: row["id"])
    wording = sorted(
        (_wording_for_entity(entity) for entity in entities), key=lambda row: row["id"])
    policy = sorted(
        (_policy_for_entity(entity) for entity in entities), key=lambda row: row["id"])
    tombstone_rows = sorted(
        proposed_tombstones.values(), key=lambda row: str(row.get("id", "")))
    review_history_rows = sorted(
        review_history.values(), key=lambda row: row["id"])

    if previous is not None:
        previous_revision = previous["patternDataRevision"]
        previous_runtime_payload = copy.deepcopy(previous["runtimeProjection"])
        current_runtime_payload = copy.deepcopy(runtime_projection)
        previous_runtime_payload.pop("patternDataRevision", None)
        current_runtime_payload.pop("patternDataRevision", None)
        runtime_change = current_runtime_payload != previous_runtime_payload
        expected_revision = previous_revision + 1 if runtime_change else previous_revision
        if pattern_data_revision != expected_revision:
            _add(issues, "FROZEN_REVISION_TRANSITION", "$frozen.patternDataRevision",
                 f"The public runtime projection requires revision "
                 f"{expected_revision}, not {pattern_data_revision}.")

    if issues:
        raise ValidationFailure(issues)
    result = {
        "artifactStatus": FROZEN_ARTIFACT_STATUS,
        "formatVersion": FORMAT_VERSION,
        "patternDataRevision": pattern_data_revision,
        "allocations": sorted(allocations.values(), key=lambda row: row["id"]),
        "identity": identity,
        "structure": structure,
        "wording": wording,
        "policy": policy,
        "tombstones": tombstone_rows,
        "runtimeProjection": runtime_projection,
        "reviewHistory": review_history_rows,
        "releaseAuthorization": _derive_release_authorization(
            {row["id"]: row for row in policy},
            {row["id"]: row for row in review_history_rows}),
    }
    frozen_issues = _validate_frozen_document(result)
    if frozen_issues:
        raise ValidationFailure(frozen_issues)
    return result


def repository_index_from_root(root: str | Path) -> RepositoryIndex:
    """Load repository data through its strict source-corpus adapter."""
    from validate_content import load_source_corpus  # local, read-only adapter

    root_path = Path(root)
    sources = load_source_corpus(str(root_path / "data-*.js"))
    return RepositoryIndex.from_sources(sources)


def _load_json(path: str | Path) -> Any:
    def reject_duplicate_keys(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON object key: {key!r}")
            result[key] = value
        return result

    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle, object_pairs_hook=reject_duplicate_keys)


def _load_context(path: str | None, repository_root: str | None) -> ValidationContext:
    raw: Mapping[str, Any] = _load_json(path) if path else {}
    if not isinstance(raw, Mapping):
        raise ValueError("context JSON must be an object")
    index = repository_index_from_root(repository_root) if repository_root else None
    allocation_registry = raw.get("allocationRegistry", {})
    if isinstance(allocation_registry, list):
        indexed_allocations: dict[str, Any] = {}
        for index, row in enumerate(allocation_registry):
            if not isinstance(row, Mapping) or not isinstance(row.get("id"), str):
                raise ValueError(
                    f"allocationRegistry[{index}] must be an object with a string ID")
            entity_id = row["id"]
            if entity_id in indexed_allocations:
                raise ValueError(
                    f"duplicate allocationRegistry ID: {entity_id!r}")
            indexed_allocations[entity_id] = row
        allocation_registry = indexed_allocations
    if not isinstance(allocation_registry, Mapping):
        raise ValueError("allocationRegistry must be an object or allocation array")
    return ValidationContext(
        source_registry=raw.get("sourceRegistry", {}),
        reviewer_registry=raw.get("reviewerRegistry", {}),
        author_registry=raw.get("authorRegistry", {}),
        repository_index=index,
        allocation_registry=allocation_registry,
        editorial_actor_registry=raw.get("editorialActorRegistry", {}),
        pronunciation_playback_authorized=raw.get(
            "pronunciationPlaybackAuthorized", False),
    )


def _print_issues(issues: Sequence[Issue]) -> None:
    for issue in issues:
        print(str(issue), file=sys.stderr)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Priority 7 Phase 2A fictional/private tooling")
    subparsers = parser.add_subparsers(dest="command", required=True)

    specification_parser = subparsers.add_parser("validate-specification")
    specification_parser.add_argument("input")

    editorial_parser = subparsers.add_parser("validate-editorial")
    editorial_parser.add_argument("input")
    editorial_parser.add_argument("--context")
    editorial_parser.add_argument("--repository-root")

    runtime_parser = subparsers.add_parser("validate-runtime")
    runtime_parser.add_argument("input")
    runtime_parser.add_argument("--context")
    runtime_parser.add_argument("--repository-root")

    project_parser = subparsers.add_parser(
        "project-fixture",
        help="emit an explicitly nonrelease runtime-shaped test fixture")
    project_parser.add_argument("input")
    project_parser.add_argument(
        "--test-pattern-data-revision", required=True, type=int)
    project_parser.add_argument("--context")
    project_parser.add_argument("--repository-root")
    project_parser.add_argument(
        "--output", help="Omit to write the nonrelease wrapper to stdout.")

    arguments = parser.parse_args(argv)
    try:
        document = _load_json(arguments.input)
        if arguments.command == "validate-specification":
            issues = validate_specification_fixture(document)
            if issues:
                _print_issues(issues)
                return 1
            print("Priority 7 specification fixture: valid")
            return 0
        if arguments.command == "validate-runtime":
            context = _load_context(arguments.context, arguments.repository_root)
            issues = validate_runtime(document, context)
            if issues:
                _print_issues(issues)
                return 1
            print("Priority 7 runtime projection: valid")
            return 0
        context = _load_context(arguments.context, arguments.repository_root)
        if arguments.command == "validate-editorial":
            issues = validate_editorial(document, context)
            if issues:
                _print_issues(issues)
                return 1
            print("Priority 7 private editorial record: valid")
            return 0
        projected = project_nonrelease_fixture(
            document, arguments.test_pattern_data_revision, context)
        serialized = json.dumps(
            projected, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
        if arguments.output:
            Path(arguments.output).write_text(serialized, encoding="utf-8")
        else:
            sys.stdout.write(serialized)
        return 0
    except (OSError, json.JSONDecodeError, ValueError, ValidationFailure) as exc:
        if isinstance(exc, ValidationFailure):
            _print_issues(exc.issues)
        else:
            print(f"priority7 tooling error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
