"""Priority 8 Phase 4C4A - deterministic editorial packaging bridge.

Phase 4C0 section 25 expected Phase 4C3 to append the 68 promoted records into
``editorial/verb-pattern-candidates.json``.  Phase 4C3 instead persisted a
runtime-shaped private artifact and left the editorial corpus untouched, so the
existing Priority 7 governance machinery had nothing to operate on.  Human
decision HD-4C4-02 narrowly amends Phase 4C4 scope to permit this deterministic
packaging correction.

The bridge is a *packaging* transformation and nothing else.  It reads the
independently verified Phase 4C3 canonical candidate artifact plus its retained
private governance layer, and re-expresses the same records in the editorial
shape the repository's own validator requires.  Every canonical semantic field
is copied verbatim.  The only fields this module creates are the editorial
dimensions Phase 4C3 deliberately kept outside its canonical core:

``key``            recovered from the frozen candidate identity layer
``internalScope``  recovered from the retained meaning-scope governance rows
``origin``         recovered from the retained example-origin governance rows
``evidence``       constructed from the committed Phase 3 source register
``reviewEvents``   constructed from committed nonhuman Priority 8 workflows
``reviewState``    derived, never asserted

Two governance boundaries are deliberate and are not defects:

* ``audioEligible`` is packaged ``false``.  ``AUDIO_NOT_AUTHORIZED`` gates a
  ``true`` value on an approved owning pattern, and no product approval exists.
  This mirrors the repository's own precedent exactly: the released 45 examples
  carried ``false`` until Priority 8 Phase 1A flipped them under explicit owner
  authorization.  The Phase 4C3 promotion policy value is preserved as a future
  approved value in the review manifest, not silently discarded.
* No ``product-approval`` event is created and no pattern reaches ``approved``.
  Human product review has not happened yet.

The module is verify-only by default and writes only under ``--write``.  It
performs two independent builds and requires them to be byte-identical.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path

import priority7_tooling as tooling

ROOT = Path(__file__).resolve().parent

CANONICAL_CANDIDATES = "editorial/priority-8-phase4c-canonical-candidates.json"
STABLE_ID_MAP = "editorial/priority-8-phase4c-stable-id-map.json"
CANDIDATE_KEY_FREEZE = "editorial/priority-8-phase4-candidate-key-freeze.json"
EDITORIAL_CORPUS = "editorial/verb-pattern-candidates.json"
AUTHORING_CONTEXT = "editorial/priority-7-authoring-context.json"
SOURCE_REGISTER = "reports/priority-8-phase-3-source-register.md"
REVIEW_MANIFEST = "editorial/priority-8-phase4c4a-review-manifest.json"
REVIEW_PREVIEW = "editorial/priority-8-phase4c4a-review-preview.json"

CANONICAL_CANDIDATES_SHA256 = (
    "c54e611da32ad61c4c020545594ec1f33c0bcea6937f31c9e7a31d29bc5fa7e9")
STABLE_ID_MAP_SHA256 = (
    "20fc8a566cb34825306f9198f4977fb0dacef3c33696cad45ff7ecbab6487a9d")
CANDIDATE_FREEZE_DIGEST = (
    "0d636b3c81c15f51e36558ef5d9c18e35b189b5f5a143003c283b4732f33be27")

RELEASE_MODE = "solo-maintainer-reference-backed"

# The single registered contemporary reference every Phase 3 WSJP source key
# resolves to.  Phase 3 keys such as ``WSJP-BRAC-01`` are sense locators into
# this one institutional resource; they are not themselves source identities and
# are never synthesised into source IDs.
WSJP_SOURCE_ID = "wsjp-pan"
WSJP_SOURCE_KIND = "contemporary-reference"

# Nonhuman Priority 8 workflow actors.  Registered under HD-4C4-03 and tied to
# committed workflow evidence.  Each holds exactly one role, and the reference
# actor is deliberately distinct from both editorial actors so the solo chain's
# independence rule is satisfied structurally.
REFERENCE_ACTOR = "priority8-reference-analysis"
EDITORIAL_ACTOR = "priority8-editorial-review"
CORROBORATION_ACTOR = "priority8-editorial-corroboration"
EXAMPLE_ACTOR = "priority8-example-generation"

# The recorded date of the Phase 4B final reconciliation, at which the live
# learner-facing wording and every example sentence reached the state Phase 4C3
# promoted byte-identically.  It is written in the batch reports themselves
# ("Final reconciliation correction note (2026-08-25)"), not read from a commit
# timestamp or a file mtime.
PHASE_4B_RECONCILIATION_DATE = "2026-08-25"

SOURCE_REGISTER_ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|")


def _read_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def _sha256_file(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def _canonical_bytes(value) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":")).encode("utf-8")


def _canonical_digest(value) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def load_source_register() -> dict[str, dict[str, str]]:
    """Parse the committed Phase 3 cumulative source register.

    The register is the only authority for a source's real access date.  Nothing
    else in this module may supply one.
    """
    register: dict[str, dict[str, str]] = {}
    for line in (ROOT / SOURCE_REGISTER).read_text(encoding="utf-8").splitlines():
        match = SOURCE_REGISTER_ROW.match(line)
        if match is None:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 8:
            continue
        register[match.group(1)] = {
            "organization": cells[1],
            "title": cells[2],
            "url": cells[3],
            "accessed": cells[4],
            "sourceType": cells[5],
            "authorityRole": cells[6],
        }
    return register


def freeze_key_paths(freeze: dict) -> set[tuple[str, ...]]:
    """Every frozen candidate identity path, for one-to-one key verification."""
    paths: set[tuple[str, ...]] = set()
    for lemma in freeze["lemmas"]:
        canonical = lemma["canonicalLemma"]
        paths.add((canonical,))
        for meaning in lemma["meanings"]:
            meaning_key = meaning["candidateMeaningKey"]
            paths.add((canonical, meaning_key))
            for pattern in meaning["patterns"]:
                pattern_key = pattern["candidatePatternKey"]
                paths.add((canonical, meaning_key, pattern_key))
                # The freeze manifest carries exactly one example per pattern,
                # as a singular object rather than an array.
                paths.add((canonical, meaning_key, pattern_key,
                           pattern["example"]["candidateExampleKey"]))
    return paths


def _evidence_for_pattern(
        provenance: dict, register: dict[str, dict[str, str]]) -> dict:
    """One honest evidence record, at the granularity Phase 3 actually reached.

    Phase 3 verified each lemma against one exact WSJP PAN sense.  That is
    sense-level support shared by every pattern of the lemma, and it is recorded
    as such rather than inflated into per-pattern source work that nobody did.
    """
    phase3 = provenance["phase3Evidence"]
    source_key = phase3["primarySourceKey"]
    entry = register[source_key]
    policy_authorized = provenance["provenanceClass"] == "policy-authorized-direct-speech"
    record = {
        "sourceId": WSJP_SOURCE_ID,
        "sourceKind": WSJP_SOURCE_KIND,
        "locator": (
            f"{entry['url']} - {phase3['primarySourceLocator']} "
            f"(Phase 3 source key {source_key})"),
        # The odpowiadac direct-speech row is a documented Phase 3B policy
        # addition, not a transcribed Skladnia row.  Claiming complement-frame
        # support for it would cite a source row that does not license it, so it
        # records sense-level support only.
        "factType": "meaning" if policy_authorized else "complement-frame",
        "checkedAt": entry["accessed"],
    }
    if policy_authorized:
        record["note"] = (
            "Sense-level support only. Direct speech on this row is a Phase 3B "
            "global-constraint policy addition adjudicated at Phase 4C0 9.5; "
            "the cited Phase 3 evidence row records clause 'ze'.")
    return record


def _review_events(
        lemma: dict, meaning: dict, pattern: dict, evidence: dict,
        reference_date: str) -> list[dict]:
    """The nonhuman tier-1 and tier-2 chain, and deliberately nothing above it.

    Tier 3 is ``product-approval``.  It is human under both release modes and no
    such decision exists for these records, so no third event is created and the
    derived state stops at ``editorial-reviewed``.
    """
    scoped = {**pattern, "evidence": [evidence]}
    return [
        {
            "kind": "reference-verification",
            "decision": "accept",
            "scopeVersion": tooling.SCOPE_VERSION,
            "scopeDigest": tooling.review_scope_digest(
                "reference-verification", lemma, meaning, scoped),
            "supportingEvidenceDigests": [tooling.evidence_digest(evidence)],
            "actorRef": REFERENCE_ACTOR,
            "reviewedAt": reference_date,
            "note": (
                "Priority 8 Phase 3 source verification against the cited WSJP "
                "PAN sense, recorded in the Phase 3 batch verification CSV and "
                "the cumulative source register. Nonhuman workflow."),
        },
        {
            "kind": "editorial-review",
            "decision": "accept",
            "scopeVersion": tooling.SCOPE_VERSION,
            "scopeDigest": tooling.review_scope_digest(
                "editorial-review", lemma, meaning, scoped),
            "actorRef": EDITORIAL_ACTOR,
            "corroboratingActorRefs": [CORROBORATION_ACTOR],
            "reviewedAt": PHASE_4B_RECONCILIATION_DATE,
            "note": (
                "Priority 8 Phase 4B authoring and final semantic "
                "reconciliation, corroborated by the independent Phase 4B "
                "mechanical reconciliation audit. Nonhuman workflows only."),
        },
    ]


def build_editorial_records(
        candidates: dict, register: dict[str, dict[str, str]]) -> list[dict]:
    """Re-express the verified Phase 4C3 records in the editorial shape."""
    governance = candidates["governance"]
    scope_by_meaning = {
        row["meaningId"]: row["internalScope"]
        for row in governance["meaningScopes"]}
    provenance_by_pattern = {
        row["patternId"]: row for row in governance["patternProvenance"]}
    origin_by_example = {
        row["exampleId"]: row["origin"] for row in governance["exampleOrigins"]}
    key_by_meaning = {
        row["meaningId"]: row["candidateMeaningKey"]
        for row in governance["meaningScopes"]}
    key_by_pattern = {
        row["patternId"]: row["candidatePatternKey"]
        for row in governance["patternProvenance"]}
    key_by_example = {
        row["exampleId"]: row["candidateExampleKey"]
        for row in governance["exampleOrigins"]}

    records: list[dict] = []
    for source_lemma in candidates["canonicalCandidates"]["lemmas"]:
        lemma = copy.deepcopy(source_lemma)
        meanings = []
        for source_meaning in lemma["meanings"]:
            meaning = copy.deepcopy(source_meaning)
            meaning_id = meaning["id"]
            # Editorial shape: key and internalScope sit between id and the
            # canonical payload, matching the released 30 exactly.
            meaning = {
                "id": meaning_id,
                "key": key_by_meaning[meaning_id],
                "glossesEn": meaning["glossesEn"],
                "internalScope": scope_by_meaning[meaning_id],
                "patterns": meaning["patterns"],
            }
            patterns = []
            for source_pattern in meaning["patterns"]:
                pattern = copy.deepcopy(source_pattern)
                pattern_id = pattern["id"]
                provenance = provenance_by_pattern[pattern_id]
                evidence = _evidence_for_pattern(provenance, register)
                reference_date = register[
                    provenance["phase3Evidence"]["primarySourceKey"]]["accessed"]

                examples = []
                for source_example in pattern.get("examples", []):
                    example_id = source_example["id"]
                    origin = copy.deepcopy(origin_by_example[example_id])
                    if origin["kind"] == "editorial-generated":
                        origin["generatorRef"] = EXAMPLE_ACTOR
                        origin["adoptedAt"] = PHASE_4B_RECONCILIATION_DATE
                    examples.append({
                        "id": example_id,
                        "key": key_by_example[example_id],
                        "pl": source_example["pl"],
                        "en": source_example["en"],
                        "origin": origin,
                        # Pre-approval representation.  See the module docstring.
                        "audioEligible": False,
                    })

                packaged = {
                    "id": pattern_id,
                    "key": key_by_pattern[pattern_id],
                    "relationType": pattern["relationType"],
                    "complements": pattern["complements"],
                    "cefr": pattern["cefr"],
                    "teachingStatus": pattern["teachingStatus"],
                    "usage": pattern["usage"],
                    "learnerExplanationEn": pattern["learnerExplanationEn"],
                    "activityEligibility": pattern["activityEligibility"],
                }
                if "requiredLexicalItems" in pattern:
                    packaged["requiredLexicalItems"] = pattern["requiredLexicalItems"]
                packaged["examples"] = examples
                packaged["evidence"] = [evidence]
                packaged["releaseMode"] = RELEASE_MODE

                # The review events are digest-bound to the finished record, so
                # the scope they claim is the scope that actually exists.
                events = _review_events(
                    lemma, meaning, packaged, evidence, reference_date)
                packaged["reviewEvents"] = events
                packaged["reviewState"] = tooling._derive_review_currency(
                    events, RELEASE_MODE,
                    {stage: tooling.review_scope_digest(
                        stage, lemma, meaning, packaged)
                     for stage in tooling.STAGE_KINDS},
                    {tooling.evidence_digest(evidence)},
                    {tooling.evidence_digest(evidence): evidence},
                ).state
                patterns.append(packaged)
            meaning["patterns"] = patterns
            meanings.append(meaning)
        lemma["meanings"] = meanings
        records.append(lemma)
    return records


def build_corpus(candidates: dict, released: dict,
                 register: dict[str, dict[str, str]]) -> dict:
    """The merged editorial universe: released 30 unchanged, then the new 68.

    The envelope ``formatVersion`` moves 1 -> 2.  This is a pre-existing Phase
    4C2 gap rather than a Phase 4C4A change: Phase 4C2 moved the contract and
    the public runtime to 2 but left this private corpus at 1, so it has failed
    ``validate_editorial`` with a single ``FORMAT_VERSION`` issue ever since.
    The bump is document envelope metadata explicitly required by the tooling
    and it touches no record of the released 30.
    """
    new_lemma_ids = {
        lemma["id"] for lemma in candidates["canonicalCandidates"]["lemmas"]}
    # Idempotent by construction: the baseline is always the corpus with any
    # previously packaged Priority 8 lemma removed, so re-running the bridge
    # rebuilds rather than appending a second copy.
    baseline = [
        lemma for lemma in released["lemmas"]
        if lemma["id"] not in new_lemma_ids]
    corpus = copy.deepcopy(released)
    corpus["formatVersion"] = tooling.FORMAT_VERSION
    corpus["lemmas"] = copy.deepcopy(baseline) + build_editorial_records(
        candidates, register)
    return corpus


def build_review_manifest(corpus: dict, candidates: dict) -> dict:
    """Bind the exact candidate set a later product review would approve.

    Phase 4C4B must be able to prove which digest the human actually saw, so the
    manifest pins the Phase 4C3 artifact SHA, the packaged-corpus digest and
    every one of the 224 pattern identities.
    """
    new_lemma_ids = {
        lemma["id"] for lemma in candidates["canonicalCandidates"]["lemmas"]}
    rows = []
    for lemma in corpus["lemmas"]:
        if lemma["id"] not in new_lemma_ids:
            continue
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                example = pattern["examples"][0]
                rows.append({
                    "patternId": pattern["id"],
                    "canonicalLemma": lemma["canonicalLemma"],
                    "meaningKey": meaning["key"],
                    "patternKey": pattern["key"],
                    "glossesEn": meaning["glossesEn"],
                    "relationType": pattern["relationType"],
                    "complements": pattern["complements"],
                    "requiredLexicalItems": pattern.get("requiredLexicalItems", []),
                    "cefr": pattern["cefr"],
                    "teachingStatus": pattern["teachingStatus"],
                    "usage": pattern["usage"],
                    "learnerExplanationEn": pattern["learnerExplanationEn"],
                    "examplePl": example["pl"],
                    "exampleEn": example["en"],
                    "exampleId": example["id"],
                    "reviewStateAtPackaging": pattern["reviewState"],
                    "activityEligibility": pattern["activityEligibility"],
                    "audioEligibleAtPackaging": example["audioEligible"],
                    "audioEligibleIfApproved": True,
                })
    rows.sort(key=lambda row: row["patternId"])
    return {
        "reviewManifestSchemaVersion": 1,
        "artifactStatus":
            "priority-8-phase-4c4a-human-review-manifest-nonproduction",
        "productApproved": False,
        "releaseAuthorized": False,
        "reviewState": "awaiting-human-product-review",
        "sourceCandidateKeyFreezeDigest": CANDIDATE_FREEZE_DIGEST,
        "sourceCanonicalCandidatesSha256": CANONICAL_CANDIDATES_SHA256,
        "sourceStableIdMapSha256": STABLE_ID_MAP_SHA256,
        "packagedEditorialCorpusDigest": _canonical_digest(corpus),
        "reviewSet": {
            "lemmas": len(new_lemma_ids),
            "meanings": sum(
                len(lemma["meanings"]) for lemma in corpus["lemmas"]
                if lemma["id"] in new_lemma_ids),
            "patterns": len(rows),
            "examples": len(rows),
        },
        "audioNotice": (
            "audioEligible is packaged false because AUDIO_NOT_AUTHORIZED "
            "requires an approved owning pattern. All 224 examples remain "
            "future pronunciation-playback candidates and become eligible only "
            "after product approval, exactly as the released 45 did at "
            "Priority 8 Phase 1A. This authorizes no Listening."),
        "rows": rows,
    }


def build_review_preview(corpus: dict, candidates: dict) -> dict:
    """A private runtime-shaped preview of the pending 224, for human review.

    ``project_runtime_nonrelease`` deliberately admits only ``approved``
    patterns, so it cannot show the owner content that has not been approved
    yet -- that exclusion is correct, and the packaged corpus still projects
    exactly the released 45 through it.  This preview therefore mirrors the same
    projection shape over the *pending* records instead, so the owner inspects
    them through the real shipping loader rather than through a bespoke viewer.

    It is private editorial data.  It is never referenced by the runtime, the
    service worker, the page shell or the audio pipeline, and it carries no
    release authority: ``patternDataRevision`` stays at the current released 2
    and is not advanced.
    """
    new_lemma_ids = {
        lemma["id"] for lemma in candidates["canonicalCandidates"]["lemmas"]}
    lemmas = []
    for lemma in sorted(corpus["lemmas"], key=lambda item: item["id"]):
        if lemma["id"] not in new_lemma_ids:
            continue
        meanings = []
        for meaning in sorted(lemma["meanings"], key=lambda item: item["id"]):
            patterns = []
            for pattern in sorted(meaning["patterns"], key=lambda item: item["id"]):
                projected = {
                    "id": pattern["id"],
                    "relationType": pattern["relationType"],
                    "complements": copy.deepcopy(pattern["complements"]),
                    "cefr": copy.deepcopy(pattern["cefr"]),
                    "teachingStatus": pattern["teachingStatus"],
                    "usage": copy.deepcopy(pattern["usage"]),
                    "learnerExplanationEn": pattern["learnerExplanationEn"],
                    "activityEligibility": list(pattern["activityEligibility"]),
                }
                if "requiredLexicalItems" in pattern:
                    projected["requiredLexicalItems"] = list(
                        pattern["requiredLexicalItems"])
                projected["examples"] = [{
                    "id": example["id"],
                    "pl": example["pl"],
                    "en": example["en"],
                    "audioEligible": example["audioEligible"],
                } for example in pattern["examples"]]
                patterns.append(projected)
            if patterns:
                meanings.append({
                    "id": meaning["id"],
                    "glossesEn": copy.deepcopy(meaning["glossesEn"]),
                    "patterns": patterns,
                })
        runtime_lemma = {
            "id": lemma["id"],
            "canonicalLemma": lemma["canonicalLemma"],
            "reflexive": lemma["reflexive"],
            "aspect": lemma["aspect"],
            "meanings": meanings,
        }
        if "displayLemma" in lemma:
            runtime_lemma["displayLemma"] = lemma["displayLemma"]
        lemmas.append(runtime_lemma)
    return {
        "formatVersion": tooling.FORMAT_VERSION,
        "patternDataRevision": corpus.get("patternDataRevision", 2)
        if isinstance(corpus.get("patternDataRevision"), int) else 2,
        "lemmas": lemmas,
    }


REVIEW_SHEET_TEMPLATE = """<!doctype html>
<meta charset="utf-8">
<title>Priority 8 - product review sheet (PRIVATE, NOT APPROVED)</title>
<style>
 body{font:15px/1.5 system-ui,sans-serif;margin:0;padding:24px;max-width:1100px}
 .warn{background:#fff4e5;border:2px solid #d97706;padding:12px 16px;margin-bottom:20px}
 .lemma{margin:28px 0 8px;font-size:20px;font-weight:700}
 .pat{border:1px solid #ddd;border-left:4px solid #2563eb;padding:12px 14px;margin:10px 0}
 .pat.rec{border-left-color:#9333ea}
 .head{font-size:17px;font-weight:600}
 .meta{color:#555;font-size:13px;margin:4px 0}
 .chip{display:inline-block;background:#eef2ff;border-radius:10px;padding:2px 8px;margin:2px 4px 2px 0;font-size:13px}
 .ex{background:#f7f7f7;padding:8px 10px;margin-top:8px}
 .id{color:#888;font-size:11px;font-family:ui-monospace,monospace}
</style>
<div class="warn">
<b>PRIVATE PRE-APPROVAL REVIEW SHEET.</b> Priority 8 Phase 4C4A.
These __PATTERN_COUNT__ patterns are <b>not product-approved</b>, not frozen, not
release-authorized and not projected to production. Every row below is rendered by
the real shipping <code>pp-verb-patterns.js</code> loader, so it shows exactly what a
learner would see. Audio is disabled pre-approval. Bound review digest:
<code>__MANIFEST_DIGEST__</code>.
</div>
<div id="out">Rendering through the shipping loader&hellip;</div>
<script>__LOADER__</script>
<script>
var PREVIEW = __PREVIEW__;
(function () {
  var out = document.getElementById("out");
  /* The loader returns the headline as a parts array; index.html joins the
     parts with a single space, so this preview does exactly the same. */
  function headlineText(parts) {
    return parts.map(function (part, i) {
      return (i ? " " : "") + part.text;
    }).join("");
  }
  function esc(value) {
    return String(value).replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }
  PP_VERB_PATTERNS.reset();
  if (!PP_VERB_PATTERNS.__acceptForTest(PREVIEW)) {
    out.textContent = "The shipping loader REJECTED this preview.";
    return;
  }
  var html = [], n = 0;
  PP_VERB_PATTERNS.index().forEach(function (row) {
    var lem = PP_VERB_PATTERNS.lemma(row.key);
    html.push('<div class="lemma">' + esc(lem.lemma) + ' <span class="meta">(' +
              esc(lem.aspect) + ')</span></div>');
    lem.meanings.forEach(function (m) {
      html.push('<div class="meta"><b>Meaning:</b> ' + esc(m.glosses) + '</div>');
      m.patterns.forEach(function (p) {
        n += 1;
        html.push('<div class="pat' + (p.recognitionOnly ? ' rec' : '') + '">');
        html.push('<div class="head">' + esc(headlineText(p.headline)) + '</div>');
        html.push('<div class="meta">' + esc(p.badge.text || "") +
                  (p.recognitionOnly ? ' &middot; <b>recognition-only</b>' : '') +
                  ' &middot; eligibility: [' + esc(p.eligibility.join(", ")) +
                  ']</div>');
        html.push('<div>' + p.chips.map(function (c) {
          return '<span class="chip">' + esc(c.text) + ' &middot; ' +
                 esc(c.role) + ' &middot; ' + esc(c.question) + '</span>';
        }).join("") + '</div>');
        html.push('<div class="meta">' + esc(p.explanation) + '</div>');
        if (p.example) {
          html.push('<div class="ex"><b>' + esc(p.example.pl) + '</b><br>' +
                    esc(p.example.en) + '</div>');
        }
        html.push('<div class="id">' + esc(p.id || "") + '</div>');
        html.push('</div>');
      });
    });
  });
  out.innerHTML = '<div class="meta">Rendered ' + n +
    ' patterns across ' + PP_VERB_PATTERNS.index().length +
    ' lemmas.</div>' + html.join("");
})();
</script>
"""


def build_review_sheet(preview: dict, manifest: dict) -> str:
    """A self-contained offline review sheet driven by the shipping loader.

    Deliberately not committed and deliberately not HTML inside the deployable
    tree: it is regenerated on demand from the two committed private artifacts,
    so no private page can ever be served by the static host.
    """
    loader = (ROOT / "pp-verb-patterns.js").read_text(encoding="utf-8")
    return (REVIEW_SHEET_TEMPLATE
            .replace("__LOADER__", loader)
            .replace("__PREVIEW__", json.dumps(preview, ensure_ascii=False))
            .replace("__PATTERN_COUNT__", str(manifest["reviewSet"]["patterns"]))
            .replace("__MANIFEST_DIGEST__",
                     manifest["packagedEditorialCorpusDigest"]))


def build_context_document(context_document: dict) -> dict:
    """Register the minimum truthful Priority 8 nonhuman actors."""
    updated = copy.deepcopy(context_document)
    registry = updated["editorialActorRegistry"]
    registry[REFERENCE_ACTOR] = {
        "human": False,
        "kind": "source-analysis-workflow",
        "roles": ["reference-verification"],
        "namedInPhase": "Priority 8 Phase 4C4A",
        "note": (
            "Nonhuman source-analysis workflow for the Priority 8 expansion. "
            "Not a person, not a native speaker, not a linguist and not a "
            "reviewer identity. It records only that the Priority 8 Phase 3 "
            "reference-verification workflow ran against the cited WSJP PAN "
            "senses; the authoritative source named in sourceRegistry supplies "
            "the substantive support. Holds the reference-verification role "
            "only and is deliberately distinct from the Priority 8 editorial "
            "and example actors and from every Priority 7 actor."),
        "auditMetadata": {
            "runNote": (
                "Private audit trail. The substantive work is Priority 8 Phase "
                "3, which verified all 68 lemmas against exact WSJP PAN senses "
                "and recorded each access date in "
                "reports/priority-8-phase-3-source-register.md and each "
                "disposition in the seven batch verification CSVs. Nothing "
                "here is part of the stable actor identity."),
        },
    }
    registry[EDITORIAL_ACTOR] = {
        "human": False,
        "kind": "editorial-review-workflow",
        "roles": ["editorial-review"],
        "namedInPhase": "Priority 8 Phase 4C4A",
        "note": (
            "Nonhuman editorial-review workflow for the Priority 8 expansion. "
            "Not a person, not a native speaker, not a linguist and not a "
            "reviewer identity. It is the identity under which Phase 4B "
            "authored the 224 learner-facing treatments and the Phase 4B final "
            "semantic reconciliation adjudicated them. It supplies no "
            "native-speaker judgement and no professional linguistic "
            "authority, and product approval remains human, mandatory and "
            "unperformed."),
        "auditMetadata": {
            "runNote": (
                "Private audit trail. The substantive record is the Phase 4B1 "
                "to 4B7 authoring reports and "
                "reports/priority-8-phase-4b-final-semantic-reconciliation.md, "
                "whose corrections were applied on 2026-08-25."),
        },
    }
    registry[CORROBORATION_ACTOR] = {
        "human": False,
        "kind": "editorial-review-workflow",
        "roles": ["editorial-review"],
        "namedInPhase": "Priority 8 Phase 4C4A",
        "note": (
            "Nonhuman editorial-review workflow registered as the independent "
            "corroborator the solo chain requires at tier 2. It is the "
            "identity of the separate Phase 4B mechanical reconciliation audit "
            "and the per-batch risk reviews, which examined the same rows "
            "independently of the authoring pass. Holds the editorial-review "
            "role only and is deliberately distinct from "
            f"{EDITORIAL_ACTOR} and {REFERENCE_ACTOR}. Corroboration means one "
            "further independent nonhuman pass agreed; it is never human "
            "review."),
        "auditMetadata": {
            "runNote": (
                "Private audit trail. The substantive record is "
                "reports/priority-8-phase-4b-final-reconciliation-mechanical-"
                "audit.md and the seven Phase 4B batch risk reviews."),
        },
    }
    registry[EXAMPLE_ACTOR] = {
        "human": False,
        "kind": "example-generation-workflow",
        "roles": ["example-generation"],
        "namedInPhase": "Priority 8 Phase 4C4A",
        "note": (
            "Nonhuman example-generation workflow for the Priority 8 "
            "expansion. Not a person, not a native speaker, not a linguist, "
            "not a reviewer and not an author: it is the identity under which "
            "Phase 4B drafted a learner sentence, and origin.kind="
            "editorial-generated records exactly that and nothing more. Holds "
            "the example-generation role only. It carries no human-authorship "
            "claim: authorRegistry stays empty and origin.kind=original "
            "remains unavailable."),
    }
    updated["editorialActorRegistry"] = {
        key: registry[key] for key in sorted(registry)}
    marker = " Priority 8 Phase 4C4A is an editorial packaging bridge"
    # Idempotent: re-running the bridge must not append the notice twice.
    base_notice = context_document["contextNotice"]
    if marker in base_notice:
        base_notice = base_notice[:base_notice.index(marker)]
    updated["contextNotice"] = base_notice + (
        " Priority 8 Phase 4C4A is an editorial packaging bridge and it "
        "supersedes no statement above. Under human decisions HD-4C4-02 and "
        "HD-4C4-03 it appended the 68 independently verified Priority 8 "
        "expansion lemmas (95 meanings, 224 patterns, 224 examples, 611 stable "
        "IDs) to the editorial corpus in the editorial shape, and registered "
        "exactly four further NONHUMAN Priority 8 actors: "
        f"{REFERENCE_ACTOR} (reference-verification), {EDITORIAL_ACTOR} and "
        f"{CORROBORATION_ACTOR} (editorial-review, deliberately distinct from "
        f"each other and from the reference actor), and {EXAMPLE_ACTOR} "
        "(example-generation). Each of the 224 patterns carries exactly one "
        "sense-level WSJP PAN evidence record whose checkedAt is the access "
        "date recorded in reports/priority-8-phase-3-source-register.md, one "
        "reference-verification acceptance and one corroborated "
        "editorial-review acceptance, so all 224 are editorial-reviewed. No "
        "human reviewer identity was added, no human authority was claimed and "
        "no existing Priority 7 record changed. HD-4C4-01 is NOT approved: "
        "zero product-approval events exist for these 224 patterns, none is "
        "approved, releaseMode is solo-maintainer-reference-backed, "
        "activityEligibility is empty on all 224, and audioEligible is false "
        "on all 224 new examples because AUDIO_NOT_AUTHORIZED requires an "
        "approved owning pattern. Nothing was frozen, allocated into "
        "allocationRegistry, release-authorized or projected to runtime.")
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Priority 8 Phase 4C4A editorial packaging bridge.")
    parser.add_argument(
        "--write", action="store_true",
        help="persist the packaged corpus, context and review manifest")
    parser.add_argument(
        "--review-sheet", metavar="PATH",
        help="write the offline human product-review sheet to PATH")
    args = parser.parse_args()

    for relative, expected in (
            (CANONICAL_CANDIDATES, CANONICAL_CANDIDATES_SHA256),
            (STABLE_ID_MAP, STABLE_ID_MAP_SHA256)):
        observed = _sha256_file(relative)
        if observed != expected:
            print(f"STOP: {relative} SHA-256 {observed} != {expected}")
            return 1

    candidates = _read_json(CANONICAL_CANDIDATES)
    if candidates["sourceCandidateKeyFreezeDigest"] != CANDIDATE_FREEZE_DIGEST:
        print("STOP: candidate freeze digest mismatch")
        return 1

    released = _read_json(EDITORIAL_CORPUS)
    context_document = _read_json(AUTHORING_CONTEXT)
    register = load_source_register()

    corpus = build_corpus(candidates, released, register)
    again = build_corpus(_read_json(CANONICAL_CANDIDATES),
                         _read_json(EDITORIAL_CORPUS), load_source_register())
    if _canonical_bytes(corpus) != _canonical_bytes(again):
        print("STOP: packaging is not deterministic")
        return 1

    updated_context = build_context_document(context_document)
    manifest = build_review_manifest(corpus, candidates)
    preview = build_review_preview(corpus, candidates)
    manifest["reviewPreviewDigest"] = _canonical_digest(preview)

    context = tooling.ValidationContext(
        source_registry=updated_context["sourceRegistry"],
        reviewer_registry=updated_context["reviewerRegistry"],
        author_registry=updated_context["authorRegistry"],
        allocation_registry=updated_context["allocationRegistry"],
        editorial_actor_registry=updated_context["editorialActorRegistry"],
        repository_index=tooling.repository_index_from_root(str(ROOT)),
        pronunciation_playback_authorized=updated_context[
            "pronunciationPlaybackAuthorized"],
    )
    issues = tooling.validate_editorial(corpus, context)
    print(f"lemmas={len(corpus['lemmas'])} "
          f"patterns={sum(len(m['patterns']) for l in corpus['lemmas'] for m in l['meanings'])} "
          f"validate_editorial issues={len(issues)}")
    for issue in issues[:20]:
        print(f"  {issue.code} {issue.path} {issue.message}")
    if issues:
        return 1

    # The preview must be a legal runtime document under the real runtime
    # validator, which is how the shipping loader is proven able to render it.
    preview_issues = tooling.validate_runtime(preview, tooling.ValidationContext())
    print(f"review preview lemmas={len(preview['lemmas'])} "
          f"validate_runtime issues={len(preview_issues)}")
    for issue in preview_issues[:20]:
        print(f"  {issue.code} {issue.path} {issue.message}")
    if preview_issues:
        return 1

    if args.write:
        (ROOT / EDITORIAL_CORPUS).write_text(
            json.dumps(corpus, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        (ROOT / AUTHORING_CONTEXT).write_text(
            json.dumps(updated_context, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        (ROOT / REVIEW_MANIFEST).write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        (ROOT / REVIEW_PREVIEW).write_text(
            json.dumps(preview, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        print("WROTE packaged corpus, context, review manifest and preview")
    else:
        print("VERIFY-ONLY: no bytes written (use --write)")

    if args.review_sheet:
        Path(args.review_sheet).write_text(
            build_review_sheet(preview, manifest), encoding="utf-8")
        print(f"WROTE review sheet {args.review_sheet}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
