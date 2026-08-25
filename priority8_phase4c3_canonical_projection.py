#!/usr/bin/env python3
"""Project and verify the private Priority 8 Phase 4C3 canonical candidates.

The persisted artifact is private, nonproduction and pre-release.  This tool
never writes the released runtime corpus, never invokes release authorization,
and delegates all stable-ID work to the locked Phase 4C1 implementation.
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
import priority8_phase4c1_stable_ids as phase4c1


ROOT = Path(__file__).resolve().parent
STAGING_PATH = phase4c1.STAGING_PATH
FREEZE_PATH = phase4c1.FREEZE_PATH
MAP_PATH = phase4c1.MAP_PATH
RUNTIME_PATH = phase4c1.RUNTIME_PATH
ARTIFACT_PATH = (
    ROOT / "editorial" / "priority-8-phase4c-canonical-candidates.json")
CONTEXT_PATH = ROOT / "editorial" / "priority-7-authoring-context.json"

SCHEMA_VERSION = 1
ARTIFACT_STATUS = (
    "priority-8-phase-4c3-canonical-candidates-private-nonproduction")
MAP_SHA256 = "20fc8a566cb34825306f9198f4977fb0dacef3c33696cad45ff7ecbab6487a9d"
FROZEN_FILE_SHA256 = {
    STAGING_PATH: "6ba1bcab43feeee5bfb99a5ac67eace8befa12c3df67f44bfb94191bf1a80adc",
    FREEZE_PATH: "b74bff54122ffb25c5ce8215e5bf28f8aa8823eabc2528cae8b1066a7eb1ab8b",
    MAP_PATH: MAP_SHA256,
    RUNTIME_PATH: "c5e934a80e33b261a58a5dc7087e4c82e3ec9b9c684863465241173790c6a961",
}

EXPECTED_NEW_COUNTS = {
    "lemma": 68, "meaning": 95, "pattern": 224, "example": 224}
EXPECTED_COMBINED_COUNTS = {
    "lemmas": 98, "meanings": 129, "patterns": 269, "examples": 269,
    "stableIds": 765,
}
METADATA_ONLY = {"zaczynać", "przeczytać"}
LEXICAL_IDENTITIES = {
    "radzić", "radzić sobie", "uczyć", "życzyć",
    "kłócić się", "spotykać się", "spotkać się", "umówić się",
    "cieszyć się", "martwić się", "zgadzać się",
}

# Frozen identity plus the exact source/provider complement realization.
SOURCE_COMPLEMENTS = {
    ("wracać", "return-to-earlier-place", "z-genitive-return-source", "z", "genitive"),
    ("wrócić", "completed-return-to-earlier-place", "z-genitive-return-source", "z", "genitive"),
    ("wyjść", "literal-exit-from-place", "z-genitive-source", "z", "genitive"),
    ("wyjechać", "transport-departure", "z-genitive-source", "z", "genitive"),
    ("kupować", "process-purchase", "seller-price-schema", "od", "genitive"),
    ("kupić", "completed-purchase", "seller-price-schema", "od", "genitive"),
    ("zamawiać", "commissioning-ordering", "u-genitive-provider", "u", "genitive"),
}
PERSON_SOURCE_LEMMAS = {"kupować", "kupić", "zamawiać"}
SOURCE_FAMILY_LEMMAS = {row[0] for row in SOURCE_COMPLEMENTS}

DIRECT_SPEECH_PATTERNS = {
    ("odpowiadać", "answering-by-speech", "direct-speech"),
    ("czytać", "reading-written-content", "direct-speech-content"),
    ("pisać", "written-correspondence", "dative-direct-speech"),
    ("pisać", "written-correspondence", "do-genitive-direct-speech"),
    ("napisać", "completed-written-correspondence", "dative-direct-speech"),
    ("napisać", "completed-written-correspondence", "do-genitive-direct-speech"),
    ("powiedzieć", "spoken-communication", "direct-speech-content"),
    ("zgadzać się", "consent", "direct-speech-consent"),
    ("zgadzać się", "opinion-agreement", "direct-speech-agreement"),
    ("polecać", "directive-instruction", "dative-direct-speech-instruction"),
    ("radzić", "giving-advice", "dative-direct-speech-advice"),
}
PARTICIPATION_PATTERNS = {
    ("brać", "fixed-participation", "w-locative-participation-target"),
    ("wziąć", "fixed-participation", "w-locative-participation-target"),
}
CORRECTED_INTERROGATIVES = {
    ("zapominać", "recall-failure", "interrogative-forgotten-content"),
    ("kłócić się", "interpersonal-quarrelling", "interrogative-disputed-content"),
}

DEFERRALS = (
    ("pracować", "workplace GDZIE", "generalized role",
     "No concrete realization exists in frozen evidence; internalScope retains the boundary."),
    ("przynosić", "optional generalized source/goal", "generalized role",
     "No supported concrete realization may be inferred."),
    ("pokazywać", "optional GDZIE", "generalized role",
     "No concrete realization exists in frozen evidence."),
    ("czytać", "generalized GDZIE", "generalized role",
     "No concrete realization exists in frozen evidence."),
    ("zapraszać", "separate KOGO + GDZIE schema", "generalized role",
     "Only separately evidenced na/do constructions are canonical."),
    ("wiedzieć", "SKĄD source of knowledge", "generalized role",
     "Frozen evidence licenses no arbitrary od/z realization."),
    ("uczyć", "school-sense GDZIE", "generalized role",
     "No concrete realization exists in frozen evidence."),
    ("umówić się", "appointment KIEDY", "non-structural adjunct boundary",
     "Time is sentence grammar, not a canonical complement, and is never merged with venue."),
    ("corpus-wide", "KTÓRĘDY", "generalized role",
     "No authored concrete realization exists anywhere in the frozen corpus."),
    ("umówić się", "co do + Genitive", "compound preposition",
     "Capability and content admission are both refused in current Phase 4C."),
)


class Phase4C3Error(ValueError):
    """A fail-closed Phase 4C3 projection or validation failure."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def serialized(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def _source_key(
        lemma: str, meaning_key: str, pattern_key: str,
        complement: Mapping[str, Any]) -> tuple[str, str, str, Any, Any]:
    return (
        lemma, meaning_key, pattern_key,
        complement.get("preposition"), complement.get("case"))


def _staging_indexes(staging: Mapping[str, Any]) -> tuple[dict[str, Any], dict[tuple[str, str, str], Any], dict[tuple[str, str, str], Any]]:
    lemmas: dict[str, Any] = {}
    patterns: dict[tuple[str, str, str], Any] = {}
    examples: dict[tuple[str, str, str], Any] = {}
    for lemma in staging["lemmas"]:
        canonical = lemma["canonicalLemma"]
        lemmas[canonical] = lemma
        content = lemma["candidateContent"]
        for pattern in content["patterns"]:
            key = (canonical, pattern["meaningKeyRef"], pattern["candidatePatternKey"])
            patterns[key] = pattern
        for example in content["examples"]:
            key = (canonical, example["meaningKeyRef"], example["patternKeyRef"])
            examples[key] = example
    return lemmas, patterns, examples


def _allocation_index(stable_map: Mapping[str, Any]) -> dict[tuple[Any, ...], Mapping[str, Any]]:
    return {phase4c1.identity_key(row): row for row in stable_map["allocations"]}


def _allocation(
        index: Mapping[tuple[Any, ...], Mapping[str, Any]], canonical: str,
        meaning_key: str | None = None, pattern_key: str | None = None,
        example_key: str | None = None) -> Mapping[str, Any]:
    row = index.get((canonical, meaning_key, pattern_key, example_key))
    if row is None:
        raise Phase4C3Error(
            f"stable-ID map has no allocation for {(canonical, meaning_key, pattern_key, example_key)!r}")
    return row


def verify_inputs(
        manifest: Mapping[str, Any], staging: Mapping[str, Any],
        stable_map: Mapping[str, Any], runtime: Mapping[str, Any]) -> dict[str, Any]:
    for path, expected in FROZEN_FILE_SHA256.items():
        if sha256(path) != expected:
            raise Phase4C3Error(f"frozen input hash mismatch: {path.relative_to(ROOT)}")
    phase4c1.verify_freeze_gate(manifest, staging)
    summary = phase4c1.validate_map(
        stable_map, manifest=manifest, staging=staging, runtime=runtime)
    if stable_map != phase4c1.build_map(manifest, staging):
        raise Phase4C3Error("stable-ID map differs from independent regeneration")
    if summary != {
            "releasedCounts": {"lemma": 30, "meaning": 34, "pattern": 45, "example": 45},
            "releasedTotal": 154,
            "newCounts": EXPECTED_NEW_COUNTS,
            "newTotal": 611, "unionTotal": 765,
            "newNewCollisions": 0, "newReleasedCollisions": 0,
            "tombstones": 0, "exerciseIds": 0}:
        raise Phase4C3Error(f"stable-ID summary mismatch: {summary}")

    _, patterns, _ = _staging_indexes(staging)
    found_sources: set[tuple[str, str, str, str, str]] = set()
    family_targets = 0
    for (lemma, meaning_key, pattern_key), pattern in patterns.items():
        for complement in pattern["complements"]:
            if lemma in SOURCE_FAMILY_LEMMAS and complement.get("role") == "target":
                family_targets += 1
            source_key = _source_key(lemma, meaning_key, pattern_key, complement)
            if source_key in SOURCE_COMPLEMENTS:
                if complement.get("role") != "target":
                    raise Phase4C3Error("frozen source complement is not temporary target")
                found_sources.add(source_key)
    if found_sources != SOURCE_COMPLEMENTS or family_targets != 13:
        raise Phase4C3Error(
            f"corrected source gate mismatch: {len(found_sources)} sources / {family_targets} targets")
    return summary


def _project_complements(
        canonical: str, meaning_key: str, pattern_key: str,
        complements: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    projected: list[dict[str, Any]] = []
    converted = 0
    for raw in complements:
        complement = copy.deepcopy(dict(raw))
        if _source_key(canonical, meaning_key, pattern_key, complement) in SOURCE_COMPLEMENTS:
            if complement.get("role") != "target":
                raise Phase4C3Error("source conversion input must be temporary target")
            complement["role"] = "source"
            if canonical in PERSON_SOURCE_LEMMAS:
                complement["questionOverridePl"] = ["kogo?"]
            converted += 1
        projected.append(complement)
    expected = sum(
        1 for item in SOURCE_COMPLEMENTS
        if item[:3] == (canonical, meaning_key, pattern_key))
    if converted != expected:
        raise Phase4C3Error(
            f"source conversion count mismatch for {(canonical, meaning_key, pattern_key)!r}")
    return projected


def _deferral_ledger() -> list[dict[str, Any]]:
    rows = []
    for lemma, fact, classification, reason in DEFERRALS:
        rows.append({
            "lemma": lemma,
            "fact": fact,
            "reason": reason,
            "architectureDecision": "DEFERRED",
            "whyNoCanonicalPattern": classification,
            "candidateKeyImpact": "none; this fact is not a frozen keyed identity",
            "stableIdImpact": "none; no canonical identity is allocated",
        })
    return rows


def build_artifact(
        manifest: Mapping[str, Any] | None = None,
        staging: Mapping[str, Any] | None = None,
        stable_map: Mapping[str, Any] | None = None,
        runtime: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if manifest is None:
        manifest = phase4c1.read_json(FREEZE_PATH)
    if staging is None:
        staging = phase4c1.read_json(STAGING_PATH)
    if stable_map is None:
        stable_map = phase4c1.read_json(MAP_PATH)
    if runtime is None:
        runtime = phase4c1.read_json(RUNTIME_PATH)
    verify_inputs(manifest, staging, stable_map, runtime)

    staging_lemmas, staging_patterns, staging_examples = _staging_indexes(staging)
    allocations = _allocation_index(stable_map)
    canonical_lemmas: list[dict[str, Any]] = []
    meaning_scopes: list[dict[str, Any]] = []
    pattern_provenance: list[dict[str, Any]] = []
    example_origins: list[dict[str, Any]] = []

    for frozen_lemma in manifest["lemmas"]:
        canonical = frozen_lemma["canonicalLemma"]
        staged_lemma = staging_lemmas[canonical]
        lemma_id = _allocation(allocations, canonical)["id"]
        meanings: list[dict[str, Any]] = []
        staged_meanings = {
            row["candidateMeaningKey"]: row
            for row in staged_lemma["candidateContent"]["meanings"]}
        for frozen_meaning in frozen_lemma["meanings"]:
            meaning_key = frozen_meaning["candidateMeaningKey"]
            staged_meaning = staged_meanings[meaning_key]
            meaning_id = _allocation(allocations, canonical, meaning_key)["id"]
            meaning_scopes.append({
                "meaningId": meaning_id,
                "canonicalLemma": canonical,
                "candidateMeaningKey": meaning_key,
                "internalScope": staged_meaning["internalScope"],
            })
            patterns: list[dict[str, Any]] = []
            for frozen_pattern in frozen_meaning["patterns"]:
                pattern_key = frozen_pattern["candidatePatternKey"]
                identity = (canonical, meaning_key, pattern_key)
                staged_pattern = staging_patterns[identity]
                staged_example = staging_examples[identity]
                pattern_id = _allocation(
                    allocations, canonical, meaning_key, pattern_key)["id"]
                example_key = frozen_pattern["example"]["candidateExampleKey"]
                example_id = _allocation(
                    allocations, canonical, meaning_key, pattern_key, example_key)["id"]
                pattern = {
                    "id": pattern_id,
                    "relationType": staged_pattern["relationType"],
                    "complements": _project_complements(
                        canonical, meaning_key, pattern_key,
                        staged_pattern["complements"]),
                    "cefr": copy.deepcopy(staged_pattern["cefr"]),
                    "teachingStatus": staged_pattern["teachingStatus"],
                    "usage": copy.deepcopy(staged_pattern["usage"]),
                    "learnerExplanationEn": staged_pattern["learnerExplanationEn"],
                    "activityEligibility": [],
                    "examples": [{
                        "id": example_id,
                        "pl": staged_example["pl"],
                        "en": staged_example["en"],
                        "audioEligible": True,
                    }],
                }
                if identity in PARTICIPATION_PATTERNS:
                    if staged_lemma.get("requiredLexicalItems") != ["udział"]:
                        raise Phase4C3Error("participation lexical metadata mismatch")
                    pattern["requiredLexicalItems"] = ["udział"]
                patterns.append(pattern)
                provenance_class = (
                    "policy-authorized-direct-speech"
                    if identity == ("odpowiadać", "answering-by-speech", "direct-speech")
                    else "frozen-phase3-evidence")
                pattern_provenance.append({
                    "patternId": pattern_id,
                    "canonicalLemma": canonical,
                    "candidateMeaningKey": meaning_key,
                    "candidatePatternKey": pattern_key,
                    "provenanceClass": provenance_class,
                    "phase3Disposition": staged_lemma["phase3Disposition"],
                    "phase3Evidence": copy.deepcopy(staged_lemma["phase3Evidence"]),
                    "bindingConstraints": copy.deepcopy(staged_lemma["bindingConstraints"]),
                })
                example_origins.append({
                    "exampleId": example_id,
                    "canonicalLemma": canonical,
                    "candidateMeaningKey": meaning_key,
                    "candidatePatternKey": pattern_key,
                    "candidateExampleKey": example_key,
                    "origin": copy.deepcopy(staged_example["candidateOrigin"]),
                })
            meanings.append({
                "id": meaning_id,
                "glossesEn": copy.deepcopy(staged_meaning["glossesEn"]),
                "patterns": sorted(patterns, key=lambda row: row["id"]),
            })
        canonical_lemmas.append({
            "id": lemma_id,
            "canonicalLemma": canonical,
            "reflexive": tooling.normalize_canonical_lemma(canonical).endswith(" się"),
            "aspect": staged_lemma["aspect"],
            "meanings": sorted(meanings, key=lambda row: row["id"]),
        })

    identity_rows = [{
        "kind": row["kind"],
        "canonicalLemma": row["canonicalLemma"],
        "candidateMeaningKey": row["meaningKey"],
        "candidatePatternKey": row["patternKey"],
        "candidateExampleKey": row["exampleKey"],
        "stableId": row["id"],
        "outcome": "PROMOTED",
    } for row in stable_map["allocations"]]
    metadata_relations = [{
        "canonicalLemma": row["canonicalLemma"],
        "metadataAspectPartner": copy.deepcopy(row["metadataAspectPartner"]),
        "canonicalIdentityAllocated": False,
    } for row in staging["lemmas"] if "metadataAspectPartner" in row]

    return {
        "canonicalCandidateSchemaVersion": SCHEMA_VERSION,
        "artifactStatus": ARTIFACT_STATUS,
        "releaseAuthorized": False,
        "sourceCandidateKeyFreezeDigest": phase4c1.FROZEN_DIGEST,
        "sourceStableIdMapSha256": MAP_SHA256,
        "canonicalContract": {
            "formatVersion": tooling.FORMAT_VERSION,
            "patternDataRevision": runtime["patternDataRevision"],
        },
        "canonicalCandidates": {
            "lemmas": sorted(canonical_lemmas, key=lambda row: row["id"]),
        },
        "governance": {
            "metadataOnlyAspectRelations": sorted(
                metadata_relations, key=lambda row: row["canonicalLemma"]),
            "meaningScopes": sorted(meaning_scopes, key=lambda row: row["meaningId"]),
            "patternProvenance": sorted(
                pattern_provenance, key=lambda row: row["patternId"]),
            "exampleOrigins": sorted(example_origins, key=lambda row: row["exampleId"]),
        },
        "identityLedger": {
            "promoted": 611,
            "missing": 0,
            "duplicatePromotions": 0,
            "rows": identity_rows,
        },
        "deferralLedger": _deferral_ledger(),
        "combinedCorpusLedger": {
            "released": {
                "lemmas": 30, "meanings": 34, "patterns": 45,
                "examples": 45, "stableIds": 154,
            },
            "promotedPrivate": {
                "lemmas": 68, "meanings": 95, "patterns": 224,
                "examples": 224, "stableIds": 611,
            },
            "combinedFuture": EXPECTED_COMBINED_COUNTS,
        },
    }


def _walk_candidates(artifact: Mapping[str, Any]):
    for lemma in artifact["canonicalCandidates"]["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                yield lemma, meaning, pattern


def validate_artifact(
        artifact: Mapping[str, Any], *, compare_to_sources: bool = True) -> dict[str, Any]:
    required_top = {
        "canonicalCandidateSchemaVersion", "artifactStatus", "releaseAuthorized",
        "sourceCandidateKeyFreezeDigest", "sourceStableIdMapSha256",
        "canonicalContract", "canonicalCandidates", "governance",
        "identityLedger", "deferralLedger", "combinedCorpusLedger",
    }
    if not isinstance(artifact, Mapping) or set(artifact) != required_top:
        raise Phase4C3Error("unexpected private artifact top-level shape")
    if (artifact["canonicalCandidateSchemaVersion"] != SCHEMA_VERSION or
            artifact["artifactStatus"] != ARTIFACT_STATUS or
            artifact["releaseAuthorized"] is not False or
            artifact["sourceCandidateKeyFreezeDigest"] != phase4c1.FROZEN_DIGEST or
            artifact["sourceStableIdMapSha256"] != MAP_SHA256):
        raise Phase4C3Error("private artifact governance envelope mismatch")
    if set(artifact["canonicalCandidates"]) != {"lemmas"}:
        raise Phase4C3Error("unexpected canonicalCandidates shape")
    contract = artifact["canonicalContract"]
    if contract != {"formatVersion": 2, "patternDataRevision": 2}:
        raise Phase4C3Error("canonical contract mismatch")

    runtime_wrapper = {
        "formatVersion": contract["formatVersion"],
        "patternDataRevision": contract["patternDataRevision"],
        "lemmas": copy.deepcopy(artifact["canonicalCandidates"]["lemmas"]),
    }
    runtime_issues = tooling.validate_runtime(runtime_wrapper)
    if runtime_issues:
        raise Phase4C3Error(
            "production canonical validator rejected private candidates: " +
            "; ".join(f"{issue.code}@{issue.path}" for issue in runtime_issues[:8]))

    counts = Counter()
    ids: list[str] = []
    teaching = Counter()
    source_count = 0
    family_target_count = 0
    direct_speech: set[tuple[str, str, str]] = set()
    lexical_patterns: set[tuple[str, str, str]] = set()
    interrogatives: set[tuple[str, str, str]] = set()
    for lemma in artifact["canonicalCandidates"]["lemmas"]:
        counts["lemma"] += 1
        ids.append(lemma["id"])
        for meaning in lemma["meanings"]:
            counts["meaning"] += 1
            ids.append(meaning["id"])
            for pattern in meaning["patterns"]:
                counts["pattern"] += 1
                ids.append(pattern["id"])
                teaching[pattern["teachingStatus"]] += 1
                identity = None
                trace = next((row for row in artifact["identityLedger"]["rows"]
                              if row["stableId"] == pattern["id"]), None)
                if trace:
                    identity = (
                        trace["canonicalLemma"], trace["candidateMeaningKey"],
                        trace["candidatePatternKey"])
                if "requiredLexicalItems" in pattern and identity:
                    lexical_patterns.add(identity)
                for complement in pattern["complements"]:
                    if complement.get("role") == "source":
                        source_count += 1
                    if lemma["canonicalLemma"] in SOURCE_FAMILY_LEMMAS and complement.get("role") == "target":
                        family_target_count += 1
                    if complement.get("clauseKind") == "direct-speech" and identity:
                        direct_speech.add(identity)
                    if complement.get("clauseKind") == "interrogative" and identity in CORRECTED_INTERROGATIVES:
                        interrogatives.add(identity)
                examples = pattern.get("examples", [])
                counts["example"] += len(examples)
                ids.extend(example["id"] for example in examples)
                if len(examples) != 1 or examples[0]["audioEligible"] is not True:
                    raise Phase4C3Error("every promoted pattern requires one audio-eligible example")
                if pattern["activityEligibility"] != []:
                    raise Phase4C3Error("activity eligibility must remain empty")

    if dict(counts) != EXPECTED_NEW_COUNTS:
        raise Phase4C3Error(f"canonical candidate counts mismatch: {dict(counts)}")
    if len(ids) != 611 or len(set(ids)) != 611:
        raise Phase4C3Error("canonical stable IDs are missing or duplicated")
    if teaching != {"active-production": 222, "recognition-only": 2}:
        raise Phase4C3Error(f"teaching-status split mismatch: {dict(teaching)}")
    if source_count != 7 or family_target_count != 6:
        raise Phase4C3Error(
            f"source/target accounting mismatch: {source_count}/{family_target_count}")
    if direct_speech != DIRECT_SPEECH_PATTERNS:
        raise Phase4C3Error("direct-speech identity set mismatch")
    if lexical_patterns != PARTICIPATION_PATTERNS:
        raise Phase4C3Error("requiredLexicalItems identity set mismatch")
    if interrogatives != CORRECTED_INTERROGATIVES:
        raise Phase4C3Error("corrected interrogative identity mismatch")

    lemma_names = {
        row["canonicalLemma"] for row in artifact["canonicalCandidates"]["lemmas"]}
    if not METADATA_ONLY.isdisjoint(lemma_names):
        raise Phase4C3Error("metadata-only identity was promoted")
    if not LEXICAL_IDENTITIES.issubset(lemma_names):
        raise Phase4C3Error("lexical się/sobie identity is missing")
    if any("aspectPartnerIds" in lemma for lemma in artifact["canonicalCandidates"]["lemmas"]):
        raise Phase4C3Error("aspectPartnerIds are forbidden")
    if any("aspectEquivalentPatternIds" in pattern
           for _, _, pattern in _walk_candidates(artifact)):
        raise Phase4C3Error("aspectEquivalentPatternIds are forbidden")

    ledger = artifact["identityLedger"]
    if (set(ledger) != {"promoted", "missing", "duplicatePromotions", "rows"} or
            (ledger["promoted"], ledger["missing"], ledger["duplicatePromotions"]) != (611, 0, 0) or
            len(ledger["rows"]) != 611 or
            {row["outcome"] for row in ledger["rows"]} != {"PROMOTED"} or
            len({row["stableId"] for row in ledger["rows"]}) != 611):
        raise Phase4C3Error("identity loss ledger mismatch")
    if len(artifact["deferralLedger"]) != 10:
        raise Phase4C3Error("deferral ledger must contain exactly 10 registered facts")
    if artifact["combinedCorpusLedger"]["combinedFuture"] != EXPECTED_COMBINED_COUNTS:
        raise Phase4C3Error("combined future corpus ledger mismatch")

    if compare_to_sources:
        expected = build_artifact()
        if artifact != expected:
            raise Phase4C3Error("persisted artifact differs from deterministic source projection")
    return {
        "lemmas": counts["lemma"], "meanings": counts["meaning"],
        "patterns": counts["pattern"], "examples": counts["example"],
        "stableIds": len(ids), "activeProduction": teaching["active-production"],
        "recognitionOnly": teaching["recognition-only"],
        "sourceComplements": source_count,
        "preservedFamilyTargets": family_target_count,
        "directSpeech": len(direct_speech),
        "requiredLexicalItemsPatterns": len(lexical_patterns),
        "promoted": ledger["promoted"], "missing": ledger["missing"],
        "deferrals": len(artifact["deferralLedger"]),
        "combinedStableIds": artifact["combinedCorpusLedger"]["combinedFuture"]["stableIds"],
    }


def atomic_write(path: Path, text: str) -> None:
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
    generated = build_artifact()
    if serialized(generated) != serialized(build_artifact()):
        raise Phase4C3Error("independent projection runs are not byte-identical")
    generated_summary = validate_artifact(generated, compare_to_sources=False)
    if write:
        atomic_write(ARTIFACT_PATH, serialized(generated))
    if not ARTIFACT_PATH.exists():
        raise Phase4C3Error("private canonical candidate artifact is not persisted")
    persisted_text = ARTIFACT_PATH.read_text(encoding="utf-8")
    if persisted_text != serialized(generated):
        raise Phase4C3Error("persisted artifact is not byte-identical to regeneration")
    persisted = phase4c1.read_json(ARTIFACT_PATH)
    if validate_artifact(persisted) != generated_summary:
        raise Phase4C3Error("persisted and regenerated validations differ")
    return generated_summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write", action="store_true",
        help="atomically write the deterministic private candidate artifact")
    args = parser.parse_args()
    print(json.dumps(run(write=args.write), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
