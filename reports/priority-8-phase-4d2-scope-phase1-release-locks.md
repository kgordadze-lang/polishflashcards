# Priority 8 Phase 4D2 — scope Phase-1 release locks

## Starting endpoint and corrected invocation

This correction started on `priority-8-phase-4c-architecture` at
`6a03609840de6710f04c8eab8f297a4d114b7d60`, tree
`9e81d9b59d3e10387ed56ac14a1f4666456fe53a`, parent
`00362a66e2e3984f73f9eeebf70ecef4b1e3ecb7`, subject `Priority 8 Phase 4D1
unify Verb Patterns audio icon`. The worktree was clean; there were no remotes,
`push.default` was `nothing`, and the fail-closed pre-push hook was executable.

Python tests are invoked as repository-root modules. Direct execution of
`tests/test_priority8_phase1b.py` incorrectly places `tests/` before the root
and cannot import `pp_audio_rule`; `python3 -m unittest
tests.test_priority8_phase1b` is the authoritative invocation.

## Original results and classification

| Suite | Original result | Classification |
| --- | --- | --- |
| Phase1 Python | 17 total; 11 fail, 6 pass | ten `HISTORICAL_PHASE_SNAPSHOT`; `test_manifest_and_files_reconcile_exactly` is `MIXED_HISTORICAL_AND_CURRENT` |
| Phase1 playback | 25 assertions; 6 fail, 19 pass | A2, A4, B2 emoji, E1, and F1 are historical/superseded; B2 innerHTML is rewritten as `CURRENT_GLOBAL_INVARIANT` |
| Phase1B | 1/1 pass as module | current static-QA artifact check; unchanged |

The historical owner endpoints are the full local Git objects
`e036a53c4bd6a7c39e79db0b23ad75ae97db3949` (Phase-1 baseline) and
`caf3716d503a51d90e3238f1a566de6caad6fef0` (Phase-1 final release). All
historical reads use `git show` or `git ls-tree` with explicit failure on a
missing object; they use no network, checkout, or worktree mutation.

## Corrections

`tests/test_priority8_phase1.py` now reads Phase-1 baseline/final editorial,
runtime, manifest, reports, worker, index, migration, and audio objects from
those endpoints. It retains exact Phase-1 values: revision 2, 45 examples, 154
stable IDs, four recognition-only patterns, format version 1, the 20/25 split,
3,402 manifest entries, APP_VERSION 8.12, and cache v67. In-memory mutations
of revision, example count, stable IDs, recognition-only count, format version,
APP_VERSION, cache, and release-worker bytes are shown to fail their matching
historical conditions.

The mixed manifest test has two independent sections. The historical section
proves Phase-1 example coverage and exact manifest/disk equality at the final
Phase-1 tree. The live section checks current content-address validity,
normalized uniqueness, collisions, manifest-to-file mapping, non-empty files,
and no current manifest/disk orphan. It intentionally requires the current
manifest key set to be a proper subset of the 3,621 current required keys,
rather than pretending all future clips exist. Current negative controls detect
missing and zero-byte referenced files, orphan files, normalized duplicates,
hash collisions, and an occupied different-hash generator slot.

`tests/test_priority8_phase1_playback.js` obtains the same final Phase-1
objects through local `NSTask` Git reads. It preserves 45 examples, four
recognition-only patterns, cache v67, APP_VERSION 8.12, and the old emoji button
only as snapshots. The current B2 guard now permits exactly
`audio.innerHTML = G_AUDIO`, requires `G_AUDIO` to be static SVG text, keeps
the Polish example in the `pEl`/text path and `data-say` in
`encodeURIComponent(pattern.example.pl)`, and rejects an in-memory mutation to
`audio.innerHTML = pattern.example.pl`.

## Current and projected audio state

The current checkout contains 3,402 manifest entries and 3,402 non-empty MP3s.
Of the 224 examples introduced after Phase 1, five reuse an existing content
hash and 219 are missing. There are zero current hash collisions. No audio was
generated and `audio-manifest.json` was not changed.

The no-write rehearsal derives 219 distinct missing hashes. Therefore a correct
future audio tranche has 3,402 + 219 = 3,621 manifest entries, five reused new
examples, zero missing eligible examples, zero orphans, and zero collisions.
This is a projection only; no current test asserts 3,621 or full current
coverage.

## Verification and handoff

After the correction, Phase1 Python passes 17/17, the documented JXA playback
suite passes 25/25, and Phase1B passes 1/1. Staging validation passes; the
Phase 4C4C1 parity suite passes 5/5. Phase-4C4C, Phase-4D1, migration, and
audio-fallback gates are rerun after the local commit so their clean-worktree
sentinels evaluate at the committed endpoint.

Production content remains SHA-256
`66a02804b8ea1bb2b8a4ec7260855018db0e32f7a0623b78dc8b62fd58801ff1`.
No production, UI, audio, activity, migration, governance, deployment, push,
or integration change is part of this correction. Audio generation remains
blocked pending independent Phase 4D2 verification.
