# Priority 8 Phase 4E2 — Human audio QA disposition

## Executive decision

**HUMAN LISTENING QA: WAIVED FOR RELEASE / DEFERRED TO IN-APP ACCEPTANCE**

The product owner reports that the initial listening sample/batch was reviewed
and all sampled clips passed with no issues reported. The product owner
explicitly waives exhaustive clip-by-clip listening of the remaining generated
clips before release. This records a product acceptance decision, not a claim
that every pronunciation is perfect.

## Technical audio status

- Phase 4E1 generation was independently technically verified: 219 new clips,
  all decoding successfully with positive duration; 3,402 historical clips are
  byte-identical; five reused clips are unchanged.
- Current reconciliation: 3,621 required phrases, 3,621 manifest entries, and
  3,621 MP3 files; 269/269 Verb Patterns coverage; zero missing, orphan,
  empty, duplicate, or colliding entries.
- Voice: `pl-PL-MarekNeural`.
- `verify_audio.py`: PASS.

## Truthfulness boundary and QA artifact

The CSV remains unchanged. It contains 219 rows with `technicalStatus=PASS`,
`humanQaStatus=PENDING`, and empty notes. Unreviewed clips are not represented
as human PASS, and no claim of 219/219 human review or universal pronunciation
approval is made. The detailed technical inventory remains at
`editorial/priority-8-phase4e1-audio-qa.csv`.

## Release-risk acceptance

Release may proceed on the basis of deterministic generation, successful
technical decoding, complete required-audio resolution, immutable historical
audio, collision/orphan/missing-file checks, and available fallback behavior.
The product owner accepts the residual pronunciation-quality risk. Individual
audio or pronunciation defects discovered during real use may be corrected in
follow-up releases.

## Invariance and verification

No audio, manifest, production content, UI, migration, activity, governance,
or test files were changed. APP_VERSION remains `8.13`; the shell cache remains
`popolsku-v68`; AUDIO_CACHE remains `popolsku-audio`; production content SHA-256
remains `66a02804b8ea1bb2b8a4ec7260855018db0e32f7a0623b78dc8b62fd58801ff1`.

Required gates are green: Phase 1 17/17, Phase 1 playback 25/25, Phase 1B
1/1, governed Phase 4 483/483, Phase 4C4C1 5/5, Phase 4C4C 78/78, Phase 4D1
5/5, Phase 4E1 5/5, migration 121/121, audio fallback 585/585, staging, and
`verify_audio.py`.

## Next gate

**READY FOR FULL PRIORITY 8 APPLICATION ACCEPTANCE TESTING.** The next work is
real-app acceptance across the 98-lemma Verb Patterns surface, navigation and
search, rendering, generated MP3 playback, fallback, cache/offline behavior,
responsive devices, and existing learning-surface regressions. It is not an
exhaustive listening pass.

## Commit endpoint

- HEAD: `2146dc960b0beadeb39d7f0ea3d7094b46afe70f`
- Parent: `d3c6a9083fd1e90129c5689b776db55a7a139669`
- Subject: `Priority 8 Phase 4E1A close audio completeness transition`
- This disposition adds one report path only; no audio or QA-row status changes.
