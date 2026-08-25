#!/usr/bin/env python3
"""Generate and verify the private Priority 8 Phase 4C1 stable-ID map.

The generator consumes only the frozen candidate hierarchy, verifies that the
live staging hierarchy is identical, and delegates every stable-ID allocation
to the locked Priority 7 allocator.  It never writes canonical/runtime data.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

import priority7_tooling as tooling


ROOT = Path(__file__).resolve().parent
STAGING_PATH = ROOT / "editorial" / "priority-8-phase4-staging.json"
FREEZE_PATH = ROOT / "editorial" / "priority-8-phase4-candidate-key-freeze.json"
MAP_PATH = ROOT / "editorial" / "priority-8-phase4c-stable-id-map.json"
RUNTIME_PATH = ROOT / "content" / "verb-patterns.json"

FROZEN_DIGEST = "0d636b3c81c15f51e36558ef5d9c18e35b189b5f5a143003c283b4732f33be27"
MAP_SCHEMA_VERSION = 1
ALLOCATION_REVISION = 1
ARTIFACT_STATUS = "priority-8-phase-4c-id-map-nonproduction"
EXPECTED_NEW_COUNTS = {
    "lemma": 68,
    "meaning": 95,
    "pattern": 224,
    "example": 224,
}
EXPECTED_RELEASED_COUNTS = {
    "lemma": 30,
    "meaning": 34,
    "pattern": 45,
    "example": 45,
}
ROW_KEYS = {
    "kind", "canonicalLemma", "meaningKey", "patternKey", "exampleKey",
    "id", "seedVersion", "status",
}
TOMBSTONE_KEYS = {
    "id", "kind", "formerParentId", "retirementRevision", "reason",
    "replacementIds",
}


class Phase4C1Error(ValueError):
    """A fail-closed Phase 4C1 allocation or validation failure."""


def read_json(path: Path) -> Any:
    def no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise Phase4C1Error(f"duplicate JSON key {key!r} in {path}")
            result[key] = value
        return result

    with path.open(encoding="utf-8") as handle:
        return json.load(handle, object_pairs_hook=no_duplicates)


def serialized(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def canonical_freeze_bytes(projection: Any) -> bytes:
    return json.dumps(
        projection, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def freeze_digest(projection: Any) -> str:
    return hashlib.sha256(canonical_freeze_bytes(projection)).hexdigest()


def projection_from_staging(staging: Mapping[str, Any]) -> list[dict[str, Any]]:
    lemmas = staging.get("lemmas")
    if not isinstance(lemmas, list):
        raise Phase4C1Error("staging lemmas must be an array")
    ordered = sorted(lemmas, key=lambda row: row.get("verificationOrder", -1))
    owners = [(row.get("verificationOrder"), row.get("canonicalLemma")) for row in ordered]
    if len(owners) != len(set(owners)):
        raise Phase4C1Error("duplicate staging lemma/order owner")

    projection: list[dict[str, Any]] = []
    for lemma in ordered:
        content = lemma.get("candidateContent")
        if not isinstance(content, Mapping):
            raise Phase4C1Error("staging lemma lacks candidateContent")
        meanings = content.get("meanings")
        patterns = content.get("patterns")
        examples = content.get("examples")
        if not all(isinstance(value, list) for value in (meanings, patterns, examples)):
            raise Phase4C1Error("candidateContent hierarchy collections must be arrays")

        meaning_keys = [row.get("candidateMeaningKey") for row in meanings]
        if len(meaning_keys) != len(set(meaning_keys)):
            raise Phase4C1Error("duplicate meaning owner")
        patterns_by_meaning = {key: [] for key in meaning_keys}
        pattern_owners: list[tuple[Any, Any]] = []
        for pattern in patterns:
            owner = (pattern.get("meaningKeyRef"), pattern.get("candidatePatternKey"))
            if owner[0] not in patterns_by_meaning:
                raise Phase4C1Error("orphan pattern meaning reference")
            if owner in pattern_owners:
                raise Phase4C1Error("duplicate pattern owner")
            pattern_owners.append(owner)
            patterns_by_meaning[owner[0]].append(pattern)

        examples_by_owner: dict[tuple[Any, Any], Mapping[str, Any]] = {}
        for example in examples:
            owner = (example.get("meaningKeyRef"), example.get("patternKeyRef"))
            if owner in examples_by_owner:
                raise Phase4C1Error("duplicate example owner")
            examples_by_owner[owner] = example
        if set(pattern_owners) != set(examples_by_owner) or len(
                pattern_owners) != len(examples_by_owner):
            raise Phase4C1Error("pattern/example ownership mismatch")

        projected_meanings = []
        for meaning_key in meaning_keys:
            projected_patterns = []
            for pattern in patterns_by_meaning[meaning_key]:
                pattern_key = pattern["candidatePatternKey"]
                example = examples_by_owner[(meaning_key, pattern_key)]
                projected_patterns.append({
                    "candidatePatternKey": pattern_key,
                    "example": {"candidateExampleKey": example["candidateExampleKey"]},
                })
            projected_meanings.append({
                "candidateMeaningKey": meaning_key,
                "patterns": projected_patterns,
            })
        projection.append({
            "verificationOrder": lemma["verificationOrder"],
            "canonicalLemma": lemma["canonicalLemma"],
            "meanings": projected_meanings,
        })
    return projection


def projection_from_manifest(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    expected_top = {
        "freezeSchemaVersion", "priority", "phase", "status", "sourceStaging",
        "counts", "candidateKeyFreezeDigest", "lemmas",
    }
    if set(manifest) != expected_top:
        raise Phase4C1Error("unexpected candidate-freeze manifest shape")
    if (manifest.get("freezeSchemaVersion") != 1 or manifest.get("priority") != 8 or
            manifest.get("phase") != "4B" or manifest.get("status") != "frozen"):
        raise Phase4C1Error("candidate-freeze governance envelope mismatch")
    lemmas = manifest.get("lemmas")
    if not isinstance(lemmas, list):
        raise Phase4C1Error("candidate-freeze lemmas must be an array")
    for lemma in lemmas:
        if not isinstance(lemma, Mapping) or set(lemma) != {
                "verificationOrder", "canonicalLemma", "meanings"}:
            raise Phase4C1Error("unexpected candidate-freeze lemma shape")
        for meaning in lemma["meanings"]:
            if not isinstance(meaning, Mapping) or set(meaning) != {
                    "candidateMeaningKey", "patterns"}:
                raise Phase4C1Error("unexpected candidate-freeze meaning shape")
            for pattern in meaning["patterns"]:
                if not isinstance(pattern, Mapping) or set(pattern) != {
                        "candidatePatternKey", "example"}:
                    raise Phase4C1Error("unexpected candidate-freeze pattern shape")
                if not isinstance(pattern["example"], Mapping) or set(
                        pattern["example"]) != {"candidateExampleKey"}:
                    raise Phase4C1Error("unexpected candidate-freeze example shape")
    return copy.deepcopy(lemmas)


def verify_freeze_gate(
        manifest: Mapping[str, Any], staging: Mapping[str, Any]
) -> list[dict[str, Any]]:
    manifest_projection = projection_from_manifest(manifest)
    live_projection = projection_from_staging(staging)
    if manifest_projection != live_projection:
        raise Phase4C1Error("manifest/live candidate hierarchy mismatch")
    manifest_digest = freeze_digest(manifest_projection)
    live_digest = freeze_digest(live_projection)
    if (manifest.get("candidateKeyFreezeDigest") != FROZEN_DIGEST or
            manifest_digest != FROZEN_DIGEST or live_digest != FROZEN_DIGEST):
        raise Phase4C1Error("candidate-key freeze digest mismatch")
    counts = {
        "lemmas": len(manifest_projection),
        "meanings": sum(len(row["meanings"]) for row in manifest_projection),
        "patterns": sum(
            len(meaning["patterns"])
            for row in manifest_projection for meaning in row["meanings"]),
    }
    counts["examples"] = counts["patterns"]
    counts["totalCandidateKeys"] = (
        counts["meanings"] + counts["patterns"] + counts["examples"])
    if counts != {
            "lemmas": 68, "meanings": 95, "patterns": 224,
            "examples": 224, "totalCandidateKeys": 543}:
        raise Phase4C1Error(f"candidate hierarchy counts mismatch: {counts}")
    if manifest.get("counts") != counts:
        raise Phase4C1Error("candidate-freeze recorded counts mismatch")
    return manifest_projection


def identity_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        row.get("canonicalLemma"), row.get("meaningKey"),
        row.get("patternKey"), row.get("exampleKey"),
    )


def allocate_projection(projection: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Allocate only by calling the locked Priority 7 stable-ID functions."""
    rows: list[dict[str, Any]] = []
    for lemma in projection:
        canonical = lemma["canonicalLemma"]
        if tooling.normalize_canonical_lemma(canonical) != canonical:
            raise Phase4C1Error(f"noncanonical frozen lemma identity: {canonical!r}")
        lemma_id = tooling.allocate_lemma_id(canonical)
        rows.append(_row("lemma", canonical, None, None, None, lemma_id))
        for meaning in lemma["meanings"]:
            meaning_key = meaning["candidateMeaningKey"]
            meaning_id = tooling.allocate_meaning_id(lemma_id, canonical, meaning_key)
            rows.append(_row("meaning", canonical, meaning_key, None, None, meaning_id))
            for pattern in meaning["patterns"]:
                pattern_key = pattern["candidatePatternKey"]
                pattern_id = tooling.allocate_pattern_id(
                    meaning_id, canonical, meaning_key, pattern_key)
                rows.append(_row(
                    "pattern", canonical, meaning_key, pattern_key, None, pattern_id))
                example_key = pattern["example"]["candidateExampleKey"]
                example_id = tooling.allocate_example_id(pattern_id, example_key)
                rows.append(_row(
                    "example", canonical, meaning_key, pattern_key, example_key,
                    example_id))
    return sorted(rows, key=lambda row: row["id"])


def _row(
        kind: str, canonical: str, meaning_key: str | None,
        pattern_key: str | None, example_key: str | None, entity_id: str
) -> dict[str, Any]:
    return {
        "kind": kind,
        "canonicalLemma": canonical,
        "meaningKey": meaning_key,
        "patternKey": pattern_key,
        "exampleKey": example_key,
        "id": entity_id,
        "seedVersion": 1,
        "status": "active",
    }


def build_map(
        manifest: Mapping[str, Any] | None = None,
        staging: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if manifest is None:
        manifest = read_json(FREEZE_PATH)
    if staging is None:
        staging = read_json(STAGING_PATH)
    projection = verify_freeze_gate(manifest, staging)
    return {
        "stableIdMapSchemaVersion": MAP_SCHEMA_VERSION,
        "artifactStatus": ARTIFACT_STATUS,
        "sourceCandidateKeyFreezeDigest": FROZEN_DIGEST,
        "allocationRevision": ALLOCATION_REVISION,
        "allocations": allocate_projection(projection),
        "tombstones": [],
    }


def released_identity_rows(runtime: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for lemma in runtime.get("lemmas", []):
        canonical = lemma["canonicalLemma"]
        lemma_id = lemma["id"]
        if tooling.allocate_lemma_id(canonical) != lemma_id:
            raise Phase4C1Error(f"released lemma ID does not reproduce: {lemma_id}")
        lemma_stem = lemma_id[len("vp-l-"):-13]
        rows.append(_row("lemma", canonical, None, None, None, lemma_id))
        for meaning in lemma["meanings"]:
            meaning_id = meaning["id"]
            meaning_readable = meaning_id[len("vp-m-"):-13]
            prefix = f"{lemma_stem}-"
            if not meaning_readable.startswith(prefix):
                raise Phase4C1Error("released meaning readable stem disagrees with lemma")
            meaning_key = meaning_readable[len(prefix):]
            if tooling.allocate_meaning_id(lemma_id, canonical, meaning_key) != meaning_id:
                raise Phase4C1Error(f"released meaning ID does not reproduce: {meaning_id}")
            rows.append(_row("meaning", canonical, meaning_key, None, None, meaning_id))
            pattern_prefix = f"{meaning_readable}-"
            for pattern in meaning["patterns"]:
                pattern_id = pattern["id"]
                pattern_readable = tooling.pattern_readable_stem(pattern_id)
                if not pattern_readable.startswith(pattern_prefix):
                    raise Phase4C1Error("released pattern readable stem disagrees with meaning")
                pattern_key = pattern_readable[len(pattern_prefix):]
                expected_pattern = tooling.allocate_pattern_id(
                    meaning_id, canonical, meaning_key, pattern_key)
                if expected_pattern != pattern_id:
                    raise Phase4C1Error(f"released pattern ID does not reproduce: {pattern_id}")
                rows.append(_row(
                    "pattern", canonical, meaning_key, pattern_key, None, pattern_id))
                example_prefix = f"{pattern_readable}-"
                for example in pattern.get("examples", []):
                    example_id = example["id"]
                    example_readable = example_id[len("vp-e-"):-13]
                    if not example_readable.startswith(example_prefix):
                        raise Phase4C1Error(
                            "released example readable stem disagrees with pattern")
                    example_key = example_readable[len(example_prefix):]
                    if tooling.allocate_example_id(pattern_id, example_key) != example_id:
                        raise Phase4C1Error(
                            f"released example ID does not reproduce: {example_id}")
                    rows.append(_row(
                        "example", canonical, meaning_key, pattern_key, example_key,
                        example_id))
    counts = Counter(row["kind"] for row in rows)
    if dict(counts) != EXPECTED_RELEASED_COUNTS:
        raise Phase4C1Error(f"released identity counts mismatch: {dict(counts)}")
    if len({row["id"] for row in rows}) != 154:
        raise Phase4C1Error("released IDs are not globally unique")
    return rows


def parent_id_for_row(
        row: Mapping[str, Any], by_identity: Mapping[tuple[Any, ...], Mapping[str, Any]]
) -> str | None:
    canonical, meaning_key, pattern_key, example_key = identity_key(row)
    if row["kind"] == "lemma":
        return None
    if row["kind"] == "meaning":
        parent_key = (canonical, None, None, None)
    elif row["kind"] == "pattern":
        parent_key = (canonical, meaning_key, None, None)
    elif row["kind"] == "example":
        parent_key = (canonical, meaning_key, pattern_key, None)
    else:
        raise Phase4C1Error(f"unknown allocation kind: {row['kind']!r}")
    parent = by_identity.get(parent_key)
    if parent is None:
        raise Phase4C1Error(f"orphan {row['kind']} allocation: {identity_key(row)!r}")
    return str(parent["id"])


def seed_for_row(
        row: Mapping[str, Any], by_identity: Mapping[tuple[Any, ...], Mapping[str, Any]]
) -> str:
    parent_id = parent_id_for_row(row, by_identity)
    if row["kind"] == "lemma":
        return f"v1|lemma|{tooling.normalize_canonical_lemma(row['canonicalLemma'])}"
    key_name = {
        "meaning": "meaningKey", "pattern": "patternKey", "example": "exampleKey"
    }[row["kind"]]
    return f"v1|{row['kind']}|{parent_id}|{row[key_name]}"


def expected_id_for_row(
        row: Mapping[str, Any], by_identity: Mapping[tuple[Any, ...], Mapping[str, Any]]
) -> str:
    canonical = row["canonicalLemma"]
    parent_id = parent_id_for_row(row, by_identity)
    if row["kind"] == "lemma":
        return tooling.allocate_lemma_id(canonical)
    if row["kind"] == "meaning":
        return tooling.allocate_meaning_id(parent_id, canonical, row["meaningKey"])
    if row["kind"] == "pattern":
        return tooling.allocate_pattern_id(
            parent_id, canonical, row["meaningKey"], row["patternKey"])
    return tooling.allocate_example_id(parent_id, row["exampleKey"])


def validate_map(
        value: Mapping[str, Any],
        manifest: Mapping[str, Any] | None = None,
        staging: Mapping[str, Any] | None = None,
        runtime: Mapping[str, Any] | None = None,
        require_current_projection: bool = True,
) -> dict[str, Any]:
    expected_top = {
        "stableIdMapSchemaVersion", "artifactStatus",
        "sourceCandidateKeyFreezeDigest", "allocationRevision", "allocations",
        "tombstones",
    }
    if not isinstance(value, Mapping) or set(value) != expected_top:
        raise Phase4C1Error("unexpected stable-ID map top-level shape")
    if value.get("stableIdMapSchemaVersion") != MAP_SCHEMA_VERSION:
        raise Phase4C1Error("stable-ID map schema version mismatch")
    if value.get("artifactStatus") != ARTIFACT_STATUS:
        raise Phase4C1Error("stable-ID map artifact status mismatch")
    if value.get("sourceCandidateKeyFreezeDigest") != FROZEN_DIGEST:
        raise Phase4C1Error("stable-ID map source freeze digest mismatch")
    revision = value.get("allocationRevision")
    if type(revision) is not int or revision < 1:
        raise Phase4C1Error("allocationRevision must be a positive integer")
    allocations = value.get("allocations")
    tombstones = value.get("tombstones")
    if not isinstance(allocations, list) or not isinstance(tombstones, list):
        raise Phase4C1Error("allocations and tombstones must be arrays")
    if any(not isinstance(row, Mapping) or set(row) != ROW_KEYS for row in allocations):
        raise Phase4C1Error("unexpected allocation row shape")
    if any(not isinstance(row, Mapping) or set(row) != TOMBSTONE_KEYS
           for row in tombstones):
        raise Phase4C1Error("unexpected tombstone row shape")
    if allocations != sorted(allocations, key=lambda row: row["id"]):
        raise Phase4C1Error("allocation rows must be sorted by ID")
    if tombstones != sorted(tombstones, key=lambda row: row["id"]):
        raise Phase4C1Error("tombstone rows must be sorted by ID")

    identity_keys = [identity_key(row) for row in allocations]
    ids = [row["id"] for row in allocations]
    if len(identity_keys) != len(set(identity_keys)):
        raise Phase4C1Error("one candidate identity cannot receive two IDs")
    if len(ids) != len(set(ids)):
        raise Phase4C1Error("one stable ID cannot belong to two identities")
    by_identity = dict(zip(identity_keys, allocations))
    by_id = dict(zip(ids, allocations))
    seeds: list[str] = []
    for row in allocations:
        if row["kind"] not in EXPECTED_NEW_COUNTS:
            raise Phase4C1Error("unknown allocation namespace")
        if row["seedVersion"] != 1:
            raise Phase4C1Error("only locked seedVersion 1 is permitted")
        if row["status"] not in {"active", "tombstoned"}:
            raise Phase4C1Error("unknown allocation lifecycle status")
        expected_nulls = {
            "lemma": (None, None, None),
            "meaning": (row["meaningKey"], None, None),
            "pattern": (row["meaningKey"], row["patternKey"], None),
            "example": (row["meaningKey"], row["patternKey"], row["exampleKey"]),
        }[row["kind"]]
        if (row["meaningKey"], row["patternKey"], row["exampleKey"]) != expected_nulls:
            raise Phase4C1Error("allocation key levels disagree with kind")
        expected_id = expected_id_for_row(row, by_identity)
        if row["id"] != expected_id:
            raise Phase4C1Error(f"allocation ID does not reproduce: {row['id']}")
        if not tooling.ID_RES[row["kind"]].fullmatch(row["id"]):
            raise Phase4C1Error(f"allocation ID has a namespace mismatch: {row['id']}")
        seeds.append(seed_for_row(row, by_identity))
    if len(seeds) != len(set(seeds)):
        raise Phase4C1Error("duplicate stable-ID seed")

    tombstone_by_id: dict[str, Mapping[str, Any]] = {}
    for tombstone in tombstones:
        entity_id = tombstone["id"]
        if entity_id in tombstone_by_id:
            raise Phase4C1Error("duplicate tombstone ID")
        tombstone_by_id[entity_id] = tombstone
        allocation = by_id.get(entity_id)
        if allocation is None:
            raise Phase4C1Error("tombstone has no retained allocation")
        if allocation["status"] != "tombstoned":
            raise Phase4C1Error("active allocation cannot also be tombstoned")
        if tombstone["kind"] != allocation["kind"]:
            raise Phase4C1Error("tombstone kind disagrees with retained allocation")
        if tombstone["formerParentId"] != parent_id_for_row(allocation, by_identity):
            raise Phase4C1Error("tombstone former parent disagrees with allocation")
        retirement = tombstone["retirementRevision"]
        if type(retirement) is not int or retirement < 1 or retirement > revision:
            raise Phase4C1Error("tombstone retirement revision is invalid")
        if not isinstance(tombstone["reason"], str) or not tombstone["reason"].strip():
            raise Phase4C1Error("tombstone reason must be nonempty")
        replacements = tombstone["replacementIds"]
        if (not isinstance(replacements, list) or
                len(replacements) != len(set(replacements)) or entity_id in replacements):
            raise Phase4C1Error("tombstone replacements are invalid")
        for replacement_id in replacements:
            replacement = by_id.get(replacement_id)
            if (replacement is None or replacement["status"] != "active" or
                    replacement["kind"] != allocation["kind"]):
                raise Phase4C1Error("tombstone replacement must be active and same-kind")
    for allocation in allocations:
        is_tombstoned = allocation["status"] == "tombstoned"
        if is_tombstoned != (allocation["id"] in tombstone_by_id):
            raise Phase4C1Error("allocation lifecycle and tombstone registry disagree")

    if manifest is None:
        manifest = read_json(FREEZE_PATH)
    if staging is None:
        staging = read_json(STAGING_PATH)
    projection = verify_freeze_gate(manifest, staging)
    if require_current_projection:
        expected = allocate_projection(projection)
        if allocations != expected or tombstones:
            raise Phase4C1Error("persisted map differs from regenerated allocation")

    if runtime is None:
        runtime = read_json(RUNTIME_PATH)
    released = released_identity_rows(runtime)
    released_by_identity = {identity_key(row): row for row in released}
    for row in allocations:
        released_row = released_by_identity.get(identity_key(row))
        if released_row is not None and released_row["id"] != row["id"]:
            raise Phase4C1Error(
                "private map disagrees with authoritative released canonical ID")
    existing_ids = {row["id"] for row in released}
    new_ids = set(ids)
    if existing_ids & new_ids:
        raise Phase4C1Error("new allocation collides with a released stable ID")
    counts = Counter(row["kind"] for row in allocations)
    if dict(counts) != EXPECTED_NEW_COUNTS:
        raise Phase4C1Error(f"new allocation counts mismatch: {dict(counts)}")
    if len(new_ids) != 611 or len(existing_ids | new_ids) != 765:
        raise Phase4C1Error("stable-ID union count mismatch")
    if any(row["canonicalLemma"] in {"zaczynać", "przeczytać"}
           for row in allocations):
        raise Phase4C1Error("metadata-only identity received a stable ID")
    if any(entity_id.startswith("vp-x-") for entity_id in ids):
        raise Phase4C1Error("exercise IDs are forbidden in Phase 4C1")
    return {
        "releasedCounts": dict(Counter(row["kind"] for row in released)),
        "releasedTotal": len(existing_ids),
        "newCounts": dict(counts),
        "newTotal": len(new_ids),
        "unionTotal": len(existing_ids | new_ids),
        "newNewCollisions": len(ids) - len(new_ids),
        "newReleasedCollisions": len(existing_ids & new_ids),
        "tombstones": len(tombstones),
        "exerciseIds": sum(entity_id.startswith("vp-x-") for entity_id in ids),
    }


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", text=True)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def run(write: bool = False) -> dict[str, Any]:
    generated = build_map()
    # Two independent complete allocations must serialize byte-for-byte.
    independently_generated = build_map()
    if serialized(generated) != serialized(independently_generated):
        raise Phase4C1Error("independent allocation runs are not byte-identical")
    summary = validate_map(generated)
    if write:
        atomic_write(MAP_PATH, serialized(generated))
    if not MAP_PATH.exists():
        raise Phase4C1Error("private stable-ID map is not persisted")
    persisted_text = MAP_PATH.read_text(encoding="utf-8")
    if persisted_text != serialized(generated):
        raise Phase4C1Error("persisted map is not byte-identical to regeneration")
    persisted = read_json(MAP_PATH)
    if validate_map(persisted) != summary:
        raise Phase4C1Error("persisted map validation differs from regeneration")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write", action="store_true",
        help="atomically write the deterministic private mapping artifact")
    args = parser.parse_args()
    print(json.dumps(run(write=args.write), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
