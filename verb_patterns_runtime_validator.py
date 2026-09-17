#!/usr/bin/env python3
"""Current validator for the public Verb Patterns runtime contract.

This is the maintained runtime-only subset extracted from the historical
Priority 7 tooling. It validates the canonical public JSON without requiring
editorial records, allocation ledgers, reports, or Git history.
"""

from __future__ import annotations

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


KEY_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


SAFE_ID_RE = re.compile(r"^[a-z0-9-]+$")


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


USAGE_PRIORITIES = {"core", "common", "limited"}


REGISTERS = {"neutral", "formal", "informal"}


ACTIVITY_KEYS = {
    "reference", "search", "grammar-choose", "grammar-build", "type-it",
    "listening", "mixed-quiz", "case-mix", "conversation",
}


CONTENT_KINDS = {"card", "topic", "drill", "scenario"}


CONTENT_PURPOSES = {"support", "practice", "context", "contrast"}


ERROR_KINDS = {"documented-common-error", "predicted-distractor"}


PREPOSITION_RE = re.compile(r"^[a-ząćęłńóśźż]+$")


REQUIRED_LEXICAL_ITEM_RE = PREPOSITION_RE


PRIVATE_RUNTIME_KEYS = {
    "artifactStatus", "specificationNotice", "internalScope", "key",
    "evidence", "sourceId", "sourceKind", "locator", "factType",
    "checkedAt", "reviewState", "reviewEvents", "reviewerRef", "reviewedAt",
    "scopeVersion", "scopeDigest", "supportingEvidenceDigests", "origin",
    "authorRef", "authoredAt", "repositorySource", "evidenceRefs",
    "sourceRegistry", "reviewerRegistry", "authorRegistry", "editorialNotes",
}


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


def allocate_lemma_id(canonical_lemma: str) -> str:
    normalized = normalize_canonical_lemma(canonical_lemma)
    slug = lemma_slug(normalized)
    seed = f"v1|lemma|{normalized}"
    return f"vp-l-{slug}-{_sha12(seed)}"


def pattern_readable_stem(pattern_id: str) -> str:
    if not isinstance(pattern_id, str):
        raise ValueError("owning pattern ID is malformed")
    match = re.fullmatch(
        r"vp-p-(?P<stem>[a-z0-9]+(?:-[a-z0-9]+)*)-(?P<digest>[0-9a-f]{12})",
        pattern_id)
    if match is None or not match.group("stem"):
        raise ValueError("owning pattern ID is malformed")
    return match.group("stem")


def _reject_surrogates(value: str) -> None:
    if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
        raise ValueError("RFC 8785 input must not contain lone surrogate code points")


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


def validate_runtime_file(path: str | Path = "content/verb-patterns.json") -> tuple[dict[str, Any] | None, list[Issue]]:
    """Load and validate one canonical public runtime document."""
    source = Path(path)
    try:
        document = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [Issue("RUNTIME_LOAD", str(source), str(exc))]
    return document, validate_runtime(document)


def runtime_counts(document: Mapping[str, Any]) -> dict[str, int]:
    """Return structural counts for operator visibility, not frozen expectations."""
    lemmas = document.get("lemmas", [])
    meanings = [meaning for lemma in lemmas for meaning in lemma.get("meanings", [])]
    patterns = [pattern for meaning in meanings for pattern in meaning.get("patterns", [])]
    examples = [example for pattern in patterns for example in pattern.get("examples", [])]
    return {
        "lemmas": len(lemmas),
        "meanings": len(meanings),
        "patterns": len(patterns),
        "examples": len(examples),
        "audioEligibleExamples": sum(example.get("audioEligible") is True for example in examples),
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    path = args[0] if args else "content/verb-patterns.json"
    document, issues = validate_runtime_file(path)
    if issues:
        print(f"FAIL: {len(issues)} Verb Patterns runtime issue(s)", file=sys.stderr)
        for issue in issues:
            print(f"  - {issue}", file=sys.stderr)
        return 1
    counts = runtime_counts(document or {})
    rendered = ", ".join(f"{key}={value}" for key, value in counts.items())
    print(f"PASS: public Verb Patterns runtime is structurally valid ({rendered})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
