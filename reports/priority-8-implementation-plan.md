# Priority 8 — phased implementation recommendation

## Scale assumptions

| Measure | Current | Low additions / final | Central additions / final | High additions / final |
|---|---:|---:|---:|---:|
| Lemmas | 30 | 68 / 98 | 70 / 100 | 72 / 102 |
| Meanings | 34 | 80 / 114 | 95 / 129 | 120 / 154 |
| Patterns | 45 | 95 / 140 | 120 / 165 | 155 / 200 |
| Examples | 45 | 95 / 140 | 120 / 165 | 155 / 200 |
| ContentRefs | 101 | 180 / 281 | 260 / 361 | 380 / 481 |
| Error notes | 24 | 55 / 79 | 90 / 114 | 130 / 154 |
| Active-production | 41 | 80 / 121 | 100 / 141 | 125 / 166 |
| Recognition-only | 4 | 15 / 19 | 20 / 24 | 30 / 34 |

Assumptions: approximately one example per pattern; selective 1.1–1.7 meanings and 1.35–2.2 patterns per added lemma depending on scenario; active + recognition equals pattern total. These are planning bounds, not commitments.

## Recommended phases and gates

### Phase 0 — audit and plan

Reports only. Exit gate: independent review of this commit; no learner/runtime/editorial/audio changes. This report is the output.

### Phase 1 — existing-45 pronunciation, staged internally

1A policy/tooling: human owner approves pronunciation separate from Listening; update specs/validators/tests.
1B projection/UI: set eligible exact examples through private governance; carry flag through the existing runtime view and add the shared control.
1C media: freeze text, reuse 20, generate 25, human audio QA, manifest verification and product approval.

Exit gate: revision 2 official projection; 45 controls, exact 20/25/0/0 split, full accessibility/offline/Range tests, all activity allowlists still empty. Rollback: complete revision-1 runtime/UI plus removal of only new manifest references; shared clips preserved.

### Phase 2 — provisional shortlist and coverage/balance lock

Owner reviews the 101 pool and locks a **provisional** approximately-70 shortlist, reserve strategy, motion/aspect budget and target coverage/domain balance. This is not the final lemma freeze: every proposed construction remains a hypothesis, and architecture-fit holds remain reserve. No stable pattern/example IDs or learner wording are authored.

Exit gate: human-approved provisional shortlist and auditable balance rationale. Rollback: revise the provisional list without touching production.

### Phase 3 — research and contemporary reference verification

Verify meanings, frames, register, aspect/reflexive relations, locked-model fit and complement-versus-adjunct status. Use repository evidence plus WSJP PAN/other reputable sources; recommend replacements for unsupported rows while the shortlist remains provisional. Repository relevance is not valency evidence.

Exit gate: supported/uncertain/insufficient disposition and current-digest `reference-verification` evidence for every advancing hypothesis. Rollback: defer or propose a reserve replacement.

### Phase 3B — final human lemma freeze

The human product owner reviews the Phase 3 evidence, replaces unsupported candidates through learner-value/coverage/evidence criteria, resolves aspect-pair opportunity cost and freezes the final lemma identities. A replacement is never selected merely by the next numeric score.

Exit gate: final human-approved lemma set, reserves, domain/coverage balance and architecture fit. Only this gate authorizes Phase 4 construction work. Rollback: reopen the shortlist before any stable pattern/example allocation.

### Phase 4 — editorial construction

Only after Phase 3B, author selective meanings/patterns, CEFR/status, explanations, original or exact-provenance examples, content refs and error notes. Allocate stable IDs only from final frozen identity seeds. No public runtime.

Exit gate: closed private schema, stable-ID/tombstone checks, repository-source parity, no B2/C1 drift.

### Phase 5 — editorial review and human product approval

Independent editorial pass, corrections/re-review as needed, then human product approval. AI agreement is not approval.

Exit gate: every shipping pattern current-digest approved; no deferred/rejected records in projection; corpus totals/balance reviewed. Rollback: return changed records to latest valid stage.

### Phase 6 — runtime expansion

Run the official frozen transition and deterministic projection to revision 3. Expand from 30 toward 100 lemmas; preserve revision-2 audio behavior. No hand-built runtime.

Exit gate: runtime/privacy/ID/revision parity, UI/mobile/accessibility, full regression. Rollback: complete revision 2; released IDs remain reserved/tombstoned.

### Phase 7 — expanded-corpus pronunciation

After exact learner text approval, compute reuse, generate only net-new clips, human QA, update flags/manifest through governance. Planning central case: about 55 reuses and 65 new clips for 120 added examples.

Exit gate: exact manifest/file parity, duplicates/collisions adjudicated, cache capacity and offline behavior verified. Rollback: runtime/manifest eligibility release, not shared old files.

### Phase 8 — optional activities

Evaluate Listening, grammar-build/choose and targeted case practice separately. Each needs explicit allowlist/items and product approval. Do not automatically enable Type It or infer activity from audio.

Exit gate per activity: deterministic prompts/answers/distractors/feedback, recognition/production policy, sampler balance, no unintended persistence.

### Phase 9 — final cumulative verification

Recalculate all counts from Git/tree evidence; run complete Python/JXA/content/audio/runtime/frozen tests; visual, keyboard, screen-reader, offline, Range and storage checks; validate generated pages/sitemap/privacy remain correctly scoped.

### Phase 10 — controlled production release

Separate authorized deployment process. Verify exact release commit/tree, staged cache/version changes, deployment inventory and rollback package. No `skipWaiting()`/`clients.claim()` without separate evidence-backed approval.

## Approval gates

Human owner approval is required for the pronunciation semantic change, current-45 eligibility treatment, shortlist, final editorial corpus, each runtime revision and every activity family. Audio QA is a separate human gate after synthesis. Security boundary/remotes/push protection are rechecked at every repository transition.

## Unresolved product decisions

1. Formally approve the new `audioEligible` pronunciation semantics.
2. Confirm all 45 examples, including recognition-only patterns, receive playback (recommended).
3. Approve or amend the provisional ranked 70, aspect/motion budget and Phase 3B replacement rules.
4. Confirm the central scale target (~129 meanings/~165 patterns/examples) is acceptable.
5. Decide which complex frames are recognition-only versus deferred.
6. Decide whether expanded audio ships with revision 3 or a tightly scoped successor revision.
7. Decide if/when Listening is worth a separate Phase 8 release.
8. Confirm long-term private storage/operational ownership of editorial/frozen governance artifacts.

No later phase is authorized by this plan.
