#!/usr/bin/env python3
"""Build/check the Priority 8 Phase 1A governance and runtime transition.

The revision-1 frozen baseline is reconstructed from the authorized starting
commit, then the current private editorial source is projected through the
existing freeze_editorial -> verified_runtime_from_frozen release path.  This
script never reads a preview, fixture, or hand-built public runtime.
"""

import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

import priority7_tooling as tooling


ROOT = Path(__file__).resolve().parent
STARTING_HEAD = "e036a53c4bd6a7c39e79db0b23ad75ae97db3949"
EDITORIAL_PATH = ROOT / "editorial" / "verb-pattern-candidates.json"
CONTEXT_PATH = ROOT / "editorial" / "priority-7-authoring-context.json"
RUNTIME_PATH = ROOT / "content" / "verb-patterns.json"
REVIEW_DATE = "2026-08-20"
PHASE_MARKER = "Priority 8 Phase 1A playback-only policy"
CONTEXT_NOTICE = (
    " Priority 8 Phase 1A supersedes only the prior statements that audio was "
    "deferred and disabled. On 2026-08-20 the product owner authorized "
    "playback-only pronunciation for the same 45 approved examples. The "
    "existing nonhuman editorial workflow re-reviewed the eligibility-only "
    "scope, and digest-bound product acceptances record that narrow decision. "
    "All activityEligibility arrays remain empty. This does not authorize "
    "Listening or claim human listening, native-speaker, linguistic, or audio-"
    "quality approval. The 25 synthesized clips remain pending human listening "
    "QA; this local candidate is not authorized for integration or deployment.")


def serialized(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def baseline_json(path):
    data = subprocess.check_output(
        ["git", "show", f"{STARTING_HEAD}:{path}"], cwd=ROOT)
    return json.loads(data.decode("utf-8")), data


def patterns(document):
    for lemma in document["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                yield lemma, meaning, pattern


def is_phase_event(event):
    return isinstance(event, dict) and PHASE_MARKER in event.get("note", "")


def authorize_playback(document):
    result = copy.deepcopy(document)
    rows = list(patterns(result))
    phase_events = [
        event for _, _, pattern in rows
        for event in pattern.get("reviewEvents", []) if is_phase_event(event)
    ]
    if phase_events:
        if len(phase_events) != 3 * len(rows):
            raise RuntimeError("partial or duplicate Phase 1A governance events")
        for _, _, pattern in rows:
            own_events = [event for event in pattern.get("reviewEvents", [])
                          if is_phase_event(event)]
            examples = pattern.get("examples", [])
            if (len(own_events) != 3 or
                    pattern.get("reviewEvents", [])[-3:] != own_events or
                    [event.get("kind") for event in own_events] != [
                        "editorial-review", "editorial-review", "product-approval"] or
                    [event.get("decision") for event in own_events] != [
                        "changes-requested", "accept", "accept"] or
                    pattern.get("reviewState") != "approved" or
                    len(examples) != 1 or
                    examples[0].get("audioEligible") is not True or
                    pattern.get("activityEligibility") != []):
                raise RuntimeError(
                    f"invalid completed Phase 1A state for {pattern.get('id')}")
        return result, False

    for _, _, pattern in rows:
        examples = pattern.get("examples", [])
        if pattern.get("reviewState") != "approved" or len(examples) != 1:
            raise RuntimeError(
                f"{pattern.get('id')} must be approved with exactly one example")
        if examples[0].get("audioEligible") is not False:
            raise RuntimeError(
                f"{examples[0].get('id')} did not start audioEligible:false")
        if pattern.get("activityEligibility") != []:
            raise RuntimeError(
                f"{pattern.get('id')} has non-empty activityEligibility")
        examples[0]["audioEligible"] = True

    for lemma, meaning, pattern in rows:
        pattern["reviewEvents"].append({
            "kind": "editorial-review",
            "decision": "changes-requested",
            "actorRef": "priority7-editorial-review",
            "reviewedAt": REVIEW_DATE,
            "note": (
                PHASE_MARKER + ": audio eligibility changed, so prior tier-2 "
                "and product acceptances are stale. Pronunciation permission "
                "is being reviewed independently from activities."),
        })
        pattern["reviewEvents"].append({
            "kind": "editorial-review",
            "decision": "accept",
            "scopeVersion": 1,
            "scopeDigest": tooling.review_scope_digest(
                "editorial-review", lemma, meaning, pattern),
            "actorRef": "priority7-editorial-review",
            "corroboratingActorRefs": ["priority7-editorial-corroboration"],
            "reviewedAt": REVIEW_DATE,
            "note": (
                PHASE_MARKER + ": exact content and activity allowlists are "
                "unchanged. audioEligible now permits pronunciation only. "
                "Nonhuman policy review; no human listening, native-speaker, "
                "or linguistic audio approval."),
        })
        pattern["reviewEvents"].append({
            "kind": "product-approval",
            "decision": "accept",
            "scopeVersion": 1,
            "scopeDigest": tooling.review_scope_digest(
                "product-approval", lemma, meaning, pattern),
            "reviewerRef": "product-owner-001",
            "reviewedAt": REVIEW_DATE,
            "note": (
                PHASE_MARKER + ": owner authorized playback for the existing "
                "45 examples. No Listening or audio-quality approval; 25 new "
                "clips remain pending human QA and this local candidate is not "
                "deployable."),
        })
    return result, True


def atomic_write(path, data):
    with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    temporary.replace(path)


def build(write=False):
    context = tooling._load_context(str(CONTEXT_PATH), str(ROOT))
    baseline_editorial, baseline_editorial_bytes = baseline_json(
        "editorial/verb-pattern-candidates.json")
    baseline_runtime, baseline_runtime_bytes = baseline_json(
        "content/verb-patterns.json")
    baseline_context, baseline_context_bytes = baseline_json(
        "editorial/priority-7-authoring-context.json")
    previous = tooling.freeze_editorial(baseline_editorial, 1, context)
    projected_previous = tooling.verified_runtime_from_frozen(previous)
    if serialized(projected_previous).encode("utf-8") != baseline_runtime_bytes:
        raise RuntimeError("reconstructed revision-1 projection differs from baseline")

    current = read_json(EDITORIAL_PATH)
    authorized, changed = authorize_playback(current)
    issues = tooling.validate_editorial(authorized, context)
    if issues:
        raise tooling.ValidationFailure(issues)
    frozen = tooling.freeze_editorial(
        authorized, 2, context, previous=previous)
    runtime = tooling.verified_runtime_from_frozen(frozen)

    examples = [
        example for _, _, pattern in patterns(authorized)
        for example in pattern.get("examples", [])
    ]
    activity = [
        pattern["activityEligibility"] for _, _, pattern in patterns(authorized)
    ]
    if len(examples) != 45 or not all(
            example["audioEligible"] is True for example in examples):
        raise RuntimeError("Phase 1A must authorize exactly 45 examples")
    if any(activity):
        raise RuntimeError("Phase 1A must leave all activity allowlists empty")
    if runtime["patternDataRevision"] != 2:
        raise RuntimeError("Phase 1A runtime revision is not 2")

    editorial_bytes = serialized(authorized).encode("utf-8")
    runtime_bytes = serialized(runtime).encode("utf-8")
    context_document = read_json(CONTEXT_PATH)
    expected_context = copy.deepcopy(baseline_context)
    expected_context["pronunciationPlaybackAuthorized"] = True
    expected_context["contextNotice"] += CONTEXT_NOTICE
    if context_document not in (baseline_context, expected_context):
        raise RuntimeError("authoring context contains a non-Phase-1A change")
    context_changed = context_document != expected_context
    baseline_context_text = baseline_context_bytes.decode("utf-8")
    status_line = (
        '  "contextStatus": "priority-7-private-authoring-context-nonproduction",\n')
    policy_line = '  "pronunciationPlaybackAuthorized": true,\n'
    if baseline_context_text.count(status_line) != 1:
        raise RuntimeError("baseline context status is not uniquely replaceable")
    baseline_context_text = baseline_context_text.replace(
        status_line, status_line + policy_line)
    old_notice = json.dumps(
        baseline_context["contextNotice"], ensure_ascii=False)
    new_notice = json.dumps(
        expected_context["contextNotice"], ensure_ascii=False)
    if baseline_context_text.count(old_notice) != 1:
        raise RuntimeError("baseline context notice is not uniquely replaceable")
    context_bytes = baseline_context_text.replace(
        old_notice, new_notice).encode("utf-8")
    if write:
        atomic_write(EDITORIAL_PATH, editorial_bytes.decode("utf-8"))
        atomic_write(RUNTIME_PATH, runtime_bytes.decode("utf-8"))
        atomic_write(CONTEXT_PATH, context_bytes.decode("utf-8"))
    elif (EDITORIAL_PATH.read_bytes() != editorial_bytes or
          RUNTIME_PATH.read_bytes() != runtime_bytes or
          CONTEXT_PATH.read_bytes() != context_bytes):
        raise RuntimeError("committed editorial/runtime bytes are not current")

    return {
        "startingHead": STARTING_HEAD,
        "baselineEditorialSha256": sha256(baseline_editorial_bytes),
        "baselineRuntimeSha256": sha256(baseline_runtime_bytes),
        "editorialSha256": sha256(editorial_bytes),
        "runtimeSha256": sha256(runtime_bytes),
        "authoringContextSha256": sha256(context_bytes),
        "patternDataRevision": runtime["patternDataRevision"],
        "eligibleExamples": len(examples),
        "activityEligibilityNonempty": sum(bool(value) for value in activity),
        "governanceEventsAdded": 135,
        "sourceChangedByThisRun": changed or context_changed,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    print(json.dumps(build(write=args.write), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
