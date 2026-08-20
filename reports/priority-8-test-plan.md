# Priority 8 Phase 0 — deterministic future test plan

## Phase 1 pronunciation tests

### Eligibility and build set

- Approved `audioEligible:true` example enters the one production required-phrase set without adding `listening`.
- `audioEligible:false`, missing example, unapproved record, private/editorial file and unknown runtime field fail closed.
- Existing 3,377 phrases remain unchanged except for exact eligible additions.
- Pin 45 eligible current examples, 20 exact reuse, 0 normalization-equivalent, 25 new, 0 editorial-decision, 45 distinct.
- Verify key = SHA-256 first 12, manifest text/file parity, non-empty file, missing/orphan detection and collision refusal.
- A duplicate normalized eligible utterance is reported once for generation but retains an explicit many-example relationship; a true differing-text hash collision blocks.

### UI/player

- Control renders only when derived `audioEligible` is true; runtime derivation retains the Boolean.
- Contextual accessible name includes the exact Polish sentence; `lang="pl"` remains on text.
- Native button keyboard activation, 44px target, wrapping at 320px/200% text, focus preservation and reduced-motion behavior.
- Loading disables only eligible controls; settled ready/unavailable state enables the correct route.
- Replay starts one new attempt.
- Two/many visible controls never overlap audio.
- Rapid A→B switching pauses/cancels A; late A end/error/promise rejection cannot clear or speak over B.
- Failed MP3 launches one fallback; dual failure signals never duplicate speech; failed final route exposes one live-region retry.
- Retry returns focus to owner; leaving screen clears stale playback/status.

### Worker/offline

- Full MP3 cache miss fetch/write; valid warm Range → exact 206; malformed/multiple/If-Range passthrough; unsatisfiable → 416.
- Partial body never cached; invalid MIME/body entry evicted.
- New manifest/runtime remain network-first with offline cached fallback.
- Warm clip plays offline; unwarmed clip reaches fallback/failure without hanging.
- Retention ceiling/trim/protected key and one-shot quota recovery remain exact.
- Old-runtime/new-manifest and new-runtime/old-manifest combinations degrade safely.

## Expansion tests

- Stable syntax/family/global uniqueness for every `vp-l/m/p/e`; no ID from tombstones is reused.
- Parent ownership and immutable keys; released relation-type change requires replacement/tombstone.
- Reciprocal aspect lemma links and reciprocal aspect-equivalent pattern links; no inherited pattern sets.
- Lexical-`się` lemma identity remains distinct from non-reflexive lemma.
- Meaning boundaries, complement type, role, requiredness, case/preposition/clause-kind enums and relation-role validity.
- Pattern CEFR/status rules; recognition-only bars production activities; deferred has no activity.
- At least one reviewed example where required; exact origin/provenance; repository source text parity.
- Private editorial/evidence/reviewer/origin fields never leak into runtime.
- Frozen release projection is byte-deterministic and exactly matches committed runtime.
- Corpus totals and coverage matrix are recomputed, not copied from prose.

## Activity tests

Listening, grammar-build, case practice and Type It each need separate item-shape, eligibility, answer-closure, distractor, feedback, sampler and persistence tests. Do not test “audio flag implies Listening”, because the intended invariant is the opposite.

## Gates

Run targeted tests during authoring, then the full 1,999-Python/36-JXA baseline (or its legitimately increased successor), content validation, audio verification and a committed-scratch/frozen-transition check before each release. Historical phase-provenance tests remain unchanged.
