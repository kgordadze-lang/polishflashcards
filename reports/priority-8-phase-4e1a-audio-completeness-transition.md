# Priority 8 Phase 4E1A — audio completeness transition

## Executive result

Phase 4E1 created valid, complete pronunciation audio but initially left the
Phase 4D2 pre-audio inequality as a live assertion. This transition moves that
inequality into a Git-backed historical proof and makes full reconciliation the
current contract. No audio was regenerated, replaced, or otherwise modified.

## Starting endpoint and audio validity

- Starting commit: `d3c6a9083fd1e90129c5689b776db55a7a139669` (`Priority 8
  Phase 4E1 generate Verb Patterns audio`).
- Starting state: 3,621 manifest entries and 3,621 non-empty MP3 files; manifest
  and disk keys matched exactly.
- `verify_audio.py`: PASS. All 3,621 required phrases were covered, with no
  missing/orphan/empty files, normalized duplicates, or hash collisions.
- `tests/test_priority8_phase4e1_audio_generation.py`: 5/5 PASS.
- Verb Patterns: 269 eligible examples, 269 covered.

## The corrected three-state contract

| State | Source | Required assertion |
|---|---|---|
| Phase 1 final | `caf3716d503a51d90e3238f1a566de6caad6fef0` | Its 3,402-entry release snapshot is complete for the Phase-1 authorized scope. |
| Phase 4D2 pre-audio | `a6420870f8c12fc25ffe15cd66b0a159bcac2fee` | 3,402 manifest entries and MP3s; 219 current required phrases were deliberately pending; manifest was a strict subset of its 3,621 required keys. |
| Current post-4E1 | current repository state | 3,621 manifest entries and MP3s; manifest keys, disk keys, and live required keys are exactly equal. |

The Phase 4D2 input is reconstructed from `git archive` in a temporary test
directory. Its historical corpus is never derived from current repository bytes.
At that endpoint the test proves 3,402/3,402 manifest/disk parity, valid manifest
integrity, no shipped orphans, a strict subset of required keys, and exactly 219
missing keys.

## Test-contract correction and negative controls

`tests/test_priority8_phase1.py` now preserves the original Phase-1 release
snapshot assertions, proves the Phase-4D2 pending-audio state historically, and
requires exact current completeness.

- Historical negative controls detect a changed missing count and reject a
  synthetic historical manifest expanded to the required universe.
- Current negative controls detect a missing required manifest entry, a missing
  referenced MP3, and an injected orphan manifest entry.
- Existing live checks remain for malformed/hash-collision entries, normalized
  duplicates, zero-byte referenced files, and orphan files. Generator collision
  protection remains covered by the existing test and neither generator nor
  verifier was changed.

## Immutability and release locks

Before and after this change, the deterministic inventory digest over every
`relative path`, `size`, and MP3 SHA-256 was
`f118df64fdd3b1001b67eb48e97852a24c2623a4d606b8a867bf31bcf54d000f`.
There are zero added, deleted, renamed, or modified MP3s, and
`audio-manifest.json` is byte-identical.

The following remain unchanged: `content/verb-patterns.json` SHA-256
`66a02804b8ea1bb2b8a4ec7260855018db0e32f7a0623b78dc8b62fd58801ff1`,
`index.html`, the `G_AUDIO` implementation, `sw.js`, APP_VERSION `8.13`, shell
cache `popolsku-v68`, `AUDIO_CACHE` `popolsku-audio`, migration, governance, and
activity eligibility.

## Verification results

| Check | Result |
|---|---|
| Phase 1 contract | 17/17 PASS |
| Phase 1 playback | 25/25 PASS |
| Phase 1B | 1/1 PASS |
| Governed Phase 4 discovery | PASS |
| Phase 4C4C1 / 4C4C / 4D1 / 4E1 | 5/5, 78/78, 5/5, 5/5 PASS |
| Migration / audio fallback | 121/121, 585/585 PASS |
| Staging / `verify_audio.py` | PASS |

## Human-QA boundary and handoff

`editorial/priority-8-phase4e1-audio-qa.csv` still contains 219 rows with
`technicalStatus=PASS`, `humanQaStatus=PENDING`, and empty notes. No human review
status was changed.

**HUMAN LISTENING QA IS STILL PENDING.** The current Phase 4E1 audio and its
4E1A completeness contract are ready for independent verification before that
human listening checkpoint.
