#!/usr/bin/env python3
"""Persist and verify the Priority 8 Phase 4C4C release-governance freeze.

Default operation is verify-only.  ``--write`` persists only the approved
editorial corpus and the allocation registry in the private authoring context.
The frozen release document is deliberately reconstructed in memory: Phase
4C4C grants release authority but does not project or publish production data.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable

import priority7_tooling as tooling
import priority8_phase1_transition as phase1
import priority8_phase4c4a_editorial_bridge as bridge


ROOT = Path(__file__).resolve().parent
STARTING_HEAD = "292a963c5f6f67b08392edb97b395ce05cb74297"
STARTING_TREE = "36d4711ef441486c8eaa7250414a1259df32bff4"
STARTING_PARENT = "e4dba274be989093b25a9367aea9ab6a9c29cbdb"
STARTING_SUBJECT = "Priority 8 Phase 4C4C2 scope historical tooling locks"
APPROVAL_DATE = "2026-08-26"
OWNER = "product-owner-001"
PHASE_MARKER = "Priority 8 Phase 4C4C"

CORPUS_PATH = "editorial/verb-pattern-candidates.json"
CONTEXT_PATH = "editorial/priority-7-authoring-context.json"
MANIFEST_PATH = "editorial/priority-8-phase4c4a-review-manifest.json"
PREVIEW_PATH = "editorial/priority-8-phase4c4a-review-preview.json"
CANDIDATES_PATH = "editorial/priority-8-phase4c-canonical-candidates.json"
STABLE_MAP_PATH = "editorial/priority-8-phase4c-stable-id-map.json"
KEY_FREEZE_PATH = "editorial/priority-8-phase4-candidate-key-freeze.json"
STAGING_PATH = "editorial/priority-8-phase4-staging.json"
RUNTIME_PATH = "content/verb-patterns.json"

IMMUTABLE_SHA256 = {
    CANDIDATES_PATH:
        "c54e611da32ad61c4c020545594ec1f33c0bcea6937f31c9e7a31d29bc5fa7e9",
    STABLE_MAP_PATH:
        "20fc8a566cb34825306f9198f4977fb0dacef3c33696cad45ff7ecbab6487a9d",
    MANIFEST_PATH:
        "f9776493385c06aa8eef212f6168072d931bc82c72cf086d872c977090127eee",
    PREVIEW_PATH:
        "31ab0139fbf5fa5e9d8dc309897a0d410152be5e65ca9f14fb2d6efb2cb895ae",
    KEY_FREEZE_PATH:
        "b74bff54122ffb25c5ce8215e5bf28f8aa8823eabc2528cae8b1066a7eb1ab8b",
    STAGING_PATH:
        "6ba1bcab43feeee5bfb99a5ac67eace8befa12c3df67f44bfb94191bf1a80adc",
}

PRODUCTION_SHA256 = {
    RUNTIME_PATH:
        "c5e934a80e33b261a58a5dc7087e4c82e3ec9b9c684863465241173790c6a961",
    "pp-verb-patterns.js":
        "5f1552d29d2173e17fd50f8775fbc4b7eed1efbf0427b1f374489bbb3cbf7aa6",
    "priority7_tooling.py":
        "c08b607ef4b6b13d89a774d86d25d54b341a65310aa49adbf7b174df61cca85c",
    "validate_priority8_staging.py":
        "cf63ba385fb2d2e96558f1e4142c9fad16f49fd9f69251e6b70ab8f386cd302e",
    "index.html":
        "2257d3c9916a4cbf2420ffbf63b25e51dfd01e87e0eb153cb37386b0af1f6eab",
    "sw.js":
        "5f5e3d41762f14fca51f5d5984071c09ec6349c8ea2f87b36c16b8238a6a6b3e",
    "audio-manifest.json":
        "791dc09355b90f1457beb46f140a3997fc073ad46a85237a2aedecf6038707b2",
}

EVENT3_NOTE = (
    PHASE_MARKER + " audio eligibility scope transition; no learner-facing "
    "semantic change.")
EVENT4_NOTE = (
    PHASE_MARKER + " refreshed nonhuman editorial review over the "
    "audio-enabled scope; no learner-facing semantic change, human editorial "
    "review, listening approval, or audio QA.")
EVENT5_NOTE = (
    PHASE_MARKER + ": the product owner approved all 224 reviewed patterns "
    "for product release, including pronunciation playback eligibility. No "
    "human language review, audio QA, activity approval, or production projection.")
CONTEXT_NOTICE = (
    " Priority 8 Phase 4C4C records the product owner's 2026-08-26 decision "
    "to approve all 224 Priority 8 patterns for product release. The 224 "
    "audioEligible flags moved from false to true for pronunciation playback "
    "only; all activityEligibility arrays remain empty and this authorizes no "
    "Listening. Each append-only history now contains the existing nonhuman "
    "reference verification and editorial acceptance, a nonhuman editorial "
    "changes-requested event for the audio scope transition, a fresh "
    "independently corroborated nonhuman editorial acceptance over that "
    "audio-enabled scope, and one human product approval by product-owner-001. "
    "The owner decision records approval of the reviewed set for product "
    "release; it does not claim row-by-row inspection, human reference "
    "verification, human editorial or linguistic review, listening QA, audio "
    "quality approval, activity approval, production projection, deployment, "
    "or integration. Existing freeze_editorial machinery derived 765 "
    "allocation records (154 released and 611 Priority 8), zero tombstones, "
    "and release authorization; no frozen runtime or production artifact was "
    "persisted in this phase.")


class GateFailure(RuntimeError):
    """A deterministic fail-closed Phase 4C4C gate failure."""


def read_json(relative: str) -> Any:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":")).encode("utf-8")


def pretty_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def git(*args: str) -> str:
    run = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True)
    if run.returncode:
        raise GateFailure(run.stderr.strip() or f"git {' '.join(args)} failed")
    return run.stdout.strip()


def iter_patterns(document: dict) -> Iterable[tuple[dict, dict, dict]]:
    for lemma in document["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                yield lemma, meaning, pattern


def validation_context(context_document: dict) -> tooling.ValidationContext:
    allocation_registry = context_document["allocationRegistry"]
    if isinstance(allocation_registry, list):
        allocation_registry = {row["id"]: row for row in allocation_registry}
    return tooling.ValidationContext(
        source_registry=context_document["sourceRegistry"],
        reviewer_registry=context_document["reviewerRegistry"],
        author_registry=context_document["authorRegistry"],
        allocation_registry=allocation_registry,
        editorial_actor_registry=context_document["editorialActorRegistry"],
        repository_index=tooling.repository_index_from_root(str(ROOT)),
        pronunciation_playback_authorized=context_document[
            "pronunciationPlaybackAuthorized"],
    )


def immutable_gate() -> None:
    for relative, expected in {**IMMUTABLE_SHA256, **PRODUCTION_SHA256}.items():
        observed = file_digest(relative)
        if observed != expected:
            raise GateFailure(
                f"immutable SHA-256 mismatch for {relative}: {observed} != {expected}")


def safety_gate(*, writing: bool) -> None:
    if git("branch", "--show-current") != "priority-8-phase-4c-architecture":
        raise GateFailure("wrong branch")
    if git("config", "--get", "push.default") != "nothing":
        raise GateFailure("push.default is not nothing")
    if git("remote"):
        raise GateFailure("repository has remotes")
    if not (ROOT / ".git/hooks/pre-push").is_file() or not (
            ROOT / ".git/hooks/pre-push").stat().st_mode & 0o111:
        raise GateFailure("pre-push hook is not executable")
    head = git("rev-parse", "HEAD")
    if writing and head != STARTING_HEAD:
        raise GateFailure(f"--write requires starting HEAD {STARTING_HEAD}; got {head}")
    if head == STARTING_HEAD:
        if git("rev-parse", "HEAD^{tree}") != STARTING_TREE:
            raise GateFailure("starting tree mismatch")
        if git("rev-parse", "HEAD^") != STARTING_PARENT:
            raise GateFailure("starting parent mismatch")
        if git("log", "-1", "--format=%s") != STARTING_SUBJECT:
            raise GateFailure("starting subject mismatch")


def review_sets(corpus: dict) -> tuple[set[str], set[str]]:
    manifest = read_json(MANIFEST_PATH)
    preview = read_json(PREVIEW_PATH)
    candidates = read_json(CANDIDATES_PATH)
    stable_map = read_json(STABLE_MAP_PATH)
    new_lemma_ids = {
        lemma["id"] for lemma in candidates["canonicalCandidates"]["lemmas"]}
    sets = [
        {row["patternId"] for row in manifest["rows"]},
        {pattern["id"] for lemma in preview["lemmas"]
         for meaning in lemma["meanings"] for pattern in meaning["patterns"]},
        {pattern["id"] for lemma, _meaning, pattern in iter_patterns(corpus)
         if lemma["id"] in new_lemma_ids},
        {row["id"] for row in stable_map["allocations"]
         if row["kind"] == "pattern"},
    ]
    if len(sets[0]) != 224 or any(value != sets[0] for value in sets[1:]):
        raise GateFailure("manifest/preview/editorial/stable-map review sets differ")
    return sets[0], new_lemma_ids


def current_state(
        pattern: dict, lemma: dict, meaning: dict) -> tooling.ReviewCurrency:
    evidence_by_digest = {
        tooling.evidence_digest(row): row for row in pattern["evidence"]}
    return tooling._derive_review_currency(
        pattern["reviewEvents"], pattern["releaseMode"],
        {stage: tooling.review_scope_digest(stage, lemma, meaning, pattern)
         for stage in tooling.STAGE_KINDS},
        set(evidence_by_digest), evidence_by_digest)


def phase_events(pattern: dict) -> list[dict]:
    return [event for event in pattern["reviewEvents"]
            if PHASE_MARKER in event.get("note", "")]


def approve_corpus(source: dict) -> tuple[dict, bool]:
    """Build the five-event live state without touching the input value."""
    result = copy.deepcopy(source)
    review_set, new_lemma_ids = review_sets(result)
    rows = [(lemma, meaning, pattern)
            for lemma, meaning, pattern in iter_patterns(result)
            if pattern["id"] in review_set]
    if len(rows) != 224:
        raise GateFailure("editorial review set does not resolve exactly 224 patterns")

    completed = [phase_events(pattern) for _lemma, _meaning, pattern in rows]
    if any(completed):
        if not all(len(events) == 3 for events in completed):
            raise GateFailure("partial or duplicate Phase 4C4C event set")
        verify_approved_corpus(result, review_set, new_lemma_ids)
        return result, False

    for _lemma, _meaning, pattern in rows:
        if (pattern["reviewState"] != "editorial-reviewed" or
                len(pattern["reviewEvents"]) != 2 or
                pattern["activityEligibility"] != [] or
                len(pattern["examples"]) != 1 or
                pattern["examples"][0]["audioEligible"] is not False):
            raise GateFailure(f"invalid pre-approval state for {pattern['id']}")
        pattern["examples"][0]["audioEligible"] = True

    for lemma, meaning, pattern in rows:
        pattern["reviewEvents"].append({
            "kind": "editorial-review",
            "decision": "changes-requested",
            "actorRef": bridge.EDITORIAL_ACTOR,
            "reviewedAt": APPROVAL_DATE,
            "note": EVENT3_NOTE,
        })
        pattern["reviewEvents"].append({
            "kind": "editorial-review",
            "decision": "accept",
            "scopeVersion": tooling.SCOPE_VERSION,
            "scopeDigest": tooling.review_scope_digest(
                "editorial-review", lemma, meaning, pattern),
            "actorRef": bridge.EDITORIAL_ACTOR,
            "corroboratingActorRefs": [bridge.CORROBORATION_ACTOR],
            "reviewedAt": APPROVAL_DATE,
            "note": EVENT4_NOTE,
        })
        if current_state(pattern, lemma, meaning).state != "editorial-reviewed":
            raise GateFailure(f"fresh editorial acceptance is not current: {pattern['id']}")
        pattern["reviewEvents"].append({
            "kind": "product-approval",
            "decision": "accept",
            "scopeVersion": tooling.SCOPE_VERSION,
            "scopeDigest": tooling.review_scope_digest(
                "product-approval", lemma, meaning, pattern),
            "reviewerRef": OWNER,
            "reviewedAt": APPROVAL_DATE,
            "note": EVENT5_NOTE,
        })
        pattern["reviewState"] = current_state(pattern, lemma, meaning).state

    verify_approved_corpus(result, review_set, new_lemma_ids)
    return result, True


def verify_approved_corpus(
        corpus: dict, review_set: set[str] | None = None,
        new_lemma_ids: set[str] | None = None) -> None:
    if review_set is None or new_lemma_ids is None:
        review_set, new_lemma_ids = review_sets(corpus)
    source = json.loads(
        subprocess.check_output(
            ["git", "show", f"{STARTING_HEAD}:{CORPUS_PATH}"], cwd=ROOT))
    source_by_id = {
        pattern["id"]: pattern for lemma, _meaning, pattern in iter_patterns(source)
        if lemma["id"] in new_lemma_ids}
    rows = [(lemma, meaning, pattern)
            for lemma, meaning, pattern in iter_patterns(corpus)
            if pattern["id"] in review_set]
    if len(rows) != 224:
        raise GateFailure("approved corpus does not contain exactly 224 review rows")
    for lemma, meaning, pattern in rows:
        events = pattern["reviewEvents"]
        old = source_by_id[pattern["id"]]
        if events[:2] != old["reviewEvents"] or len(events) != 5:
            raise GateFailure(f"review history prefix/count mismatch: {pattern['id']}")
        if [event["kind"] for event in events[2:]] != [
                "editorial-review", "editorial-review", "product-approval"]:
            raise GateFailure(f"review history kind mismatch: {pattern['id']}")
        if [event["decision"] for event in events[2:]] != [
                "changes-requested", "accept", "accept"]:
            raise GateFailure(f"review history decision mismatch: {pattern['id']}")
        if (events[2].get("actorRef") != bridge.EDITORIAL_ACTOR or
                "reviewerRef" in events[2]):
            raise GateFailure(f"event 3 authority mismatch: {pattern['id']}")
        if (events[3].get("actorRef") != bridge.EDITORIAL_ACTOR or
                events[3].get("corroboratingActorRefs") != [
                    bridge.CORROBORATION_ACTOR] or
                events[3]["scopeDigest"] != tooling.review_scope_digest(
                    "editorial-review", lemma, meaning, pattern)):
            raise GateFailure(f"event 4 currentness/corroboration mismatch: {pattern['id']}")
        if (events[4].get("reviewerRef") != OWNER or "actorRef" in events[4] or
                events[4]["reviewedAt"] != APPROVAL_DATE or
                events[4]["scopeDigest"] != tooling.review_scope_digest(
                    "product-approval", lemma, meaning, pattern)):
            raise GateFailure(f"event 5 authority/currentness mismatch: {pattern['id']}")
        if (pattern["reviewState"] != "approved" or
                current_state(pattern, lemma, meaning).state != "approved"):
            raise GateFailure(f"review state is not derived approved: {pattern['id']}")
        if pattern["activityEligibility"] != []:
            raise GateFailure(f"activity eligibility changed: {pattern['id']}")
        if len(pattern["examples"]) != 1 or not pattern["examples"][0]["audioEligible"]:
            raise GateFailure(f"audio eligibility is not enabled: {pattern['id']}")

        expected = copy.deepcopy(old)
        expected["examples"][0]["audioEligible"] = True
        for field in set(expected) - {"reviewEvents", "reviewState"}:
            if pattern.get(field) != expected.get(field):
                raise GateFailure(f"unauthorized semantic drift {pattern['id']} {field}")


def released_baseline(context: tooling.ValidationContext) -> dict:
    baseline, _ = phase1.baseline_json(CORPUS_PATH)
    baseline["formatVersion"] = tooling.FORMAT_VERSION
    audio_enabled, _ = phase1.authorize_playback(baseline)
    revision1 = tooling.freeze_editorial(baseline, 1, context)
    revision2 = tooling.freeze_editorial(
        audio_enabled, 2, context, previous=revision1)
    if tooling.verified_runtime_from_frozen(revision2) != read_json(RUNTIME_PATH):
        raise GateFailure("released frozen baseline does not reconstruct production")
    if len(revision2["allocations"]) != 154:
        raise GateFailure("released baseline does not contain 154 allocations")
    return revision2


def freeze(corpus: dict, context_document: dict) -> dict:
    context = validation_context(context_document)
    issues = tooling.validate_editorial(corpus, context)
    if issues:
        raise tooling.ValidationFailure(issues)
    previous = released_baseline(context)
    frozen = tooling.freeze_editorial(corpus, 3, context, previous=previous)
    issues = tooling.validate_frozen_release(frozen)
    if issues:
        raise tooling.ValidationFailure(issues)
    reconstructed = tooling._derive_runtime_from_frozen(
        frozen["patternDataRevision"],
        {row["id"]: row for row in frozen["identity"]},
        {row["id"]: row for row in frozen["structure"]},
        {row["id"]: row for row in frozen["wording"]},
        {row["id"]: row for row in frozen["policy"]})
    if reconstructed != frozen["runtimeProjection"]:
        raise GateFailure("frozen runtime reconstruction parity failed")
    return frozen


def updated_context(source: dict, frozen: dict) -> dict:
    result = copy.deepcopy(source)
    result["allocationRegistry"] = {
        row["id"]: copy.deepcopy(row) for row in frozen["allocations"]}
    marker = " Priority 8 Phase 4C4C records"
    notice = result["contextNotice"]
    if marker in notice:
        notice = notice[:notice.index(marker)]
    result["contextNotice"] = notice + CONTEXT_NOTICE
    return result


def metrics(corpus: dict, frozen: dict) -> dict:
    review_set, new_lemma_ids = review_sets(corpus)
    stable_ids = {row["id"] for row in read_json(STABLE_MAP_PATH)["allocations"]}
    new_allocations = [row for row in frozen["allocations"]
                       if row["id"] in stable_ids]
    released_allocations = [row for row in frozen["allocations"]
                            if row["id"] not in stable_ids]
    admitted = {
        pattern["id"] for lemma in frozen["runtimeProjection"]["lemmas"]
        for meaning in lemma["meanings"] for pattern in meaning["patterns"]}
    rows = [(lemma, meaning, pattern)
            for lemma, meaning, pattern in iter_patterns(corpus)
            if lemma["id"] in new_lemma_ids]
    result = {
        "reviewSet": len(review_set),
        "approved": sum(pattern["reviewState"] == "approved"
                        for _lemma, _meaning, pattern in rows),
        "audioEligible": sum(example["audioEligible"] is True
                             for _lemma, _meaning, pattern in rows
                             for example in pattern["examples"]),
        "activityEligibilityEmpty": sum(pattern["activityEligibility"] == []
                                        for _lemma, _meaning, pattern in rows),
        "fiveEventHistories": sum(len(pattern["reviewEvents"]) == 5
                                  for _lemma, _meaning, pattern in rows),
        "productApprovals": sum(
            event["kind"] == "product-approval"
            for _lemma, _meaning, pattern in rows
            for event in pattern["reviewEvents"]),
        "releasedAllocations": len(released_allocations),
        "newPriority8Allocations": len(new_allocations),
        "totalAllocations": len(frozen["allocations"]),
        "tombstones": len(frozen["tombstones"]),
        "admittedPriority8Patterns": len(admitted & review_set),
        "frozenDigest": digest(frozen),
        "frozenDimensionDigests": {
            key: digest(frozen[key])
            for key in ("identity", "structure", "wording", "policy")},
        "releaseAuthorization": frozen["releaseAuthorization"],
    }
    expected = {
        "reviewSet": 224, "approved": 224, "audioEligible": 224,
        "activityEligibilityEmpty": 224, "fiveEventHistories": 224,
        "productApprovals": 224, "releasedAllocations": 154,
        "newPriority8Allocations": 611, "totalAllocations": 765,
        "tombstones": 0, "admittedPriority8Patterns": 224,
    }
    for key, value in expected.items():
        if result[key] != value:
            raise GateFailure(f"metric {key}={result[key]} != {value}")
    return result


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    temporary.replace(path)


def build() -> tuple[dict, dict, dict, bool]:
    immutable_gate()
    source_corpus = read_json(CORPUS_PATH)
    source_context = read_json(CONTEXT_PATH)
    approved, changed = approve_corpus(source_corpus)
    # Use a pre-freeze registry while deriving the append-only allocation set.
    freeze_context = copy.deepcopy(source_context)
    freeze_context["allocationRegistry"] = {}
    frozen = freeze(approved, freeze_context)
    context = updated_context(source_context, frozen)
    # Real post-persistence validation uses the complete registry representation.
    issues = tooling.validate_editorial(approved, validation_context(context))
    if issues:
        raise tooling.ValidationFailure(issues)
    if set(context["allocationRegistry"]) != {
            row["id"] for row in frozen["allocations"]}:
        raise GateFailure("persisted allocation registry identity universe differs")
    return approved, context, frozen, changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    try:
        safety_gate(writing=args.write)
        corpus, context, frozen, changed = build()
        summary = metrics(corpus, frozen)
        proposed = [
            CORPUS_PATH, CONTEXT_PATH,
            "priority8_phase4c4c_release_freeze.py",
            "tests/test_priority8_phase4c2_schema_extensions.py",
            "tests/test_priority8_phase4c4a_governance_preparation.py",
            "tests/test_priority8_phase4c4c_release_freeze.py",
            "reports/priority-8-phase-4c4c-release-freeze.md",
        ]
        print("proposedPaths=" + json.dumps(proposed))
        print(json.dumps(summary, indent=2, sort_keys=True))
        corpus_data = pretty_bytes(corpus)
        context_data = pretty_bytes(context)
        if args.write:
            if not changed:
                raise GateFailure("--write requested but governance is already persisted")
            # Every gate above completed before the first repository data write.
            atomic_write(ROOT / CORPUS_PATH, corpus_data)
            atomic_write(ROOT / CONTEXT_PATH, context_data)
            print("WROTE approved editorial corpus and private allocation registry")
        else:
            if ((ROOT / CORPUS_PATH).read_bytes() != corpus_data or
                    (ROOT / CONTEXT_PATH).read_bytes() != context_data):
                print("VERIFY-ONLY: rehearsed transition differs from disk; no bytes written")
            else:
                print("VERIFY-ONLY: persisted state is current; no bytes written")
        return 0
    except (GateFailure, tooling.ValidationFailure, KeyError, ValueError) as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
