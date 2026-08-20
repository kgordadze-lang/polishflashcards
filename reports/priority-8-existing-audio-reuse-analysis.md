# Priority 8 Phase 0 — exact reuse for the 45 released examples

[priority-8-audio-reuse.csv](priority-8-audio-reuse.csv) contains the required one-row-per-example evidence: IDs, exact/normalized text, class, manifest key, provenance context, MP3 path and existence/non-empty/hash checks, collision/duplicate status and TTS-risk notes.

## Exact totals

| Classification | Count |
|---|---:|
| `exact-existing-reuse` | 20 |
| `normalization-equivalent-reuse` | 0 |
| `new-audio-required` | 25 |
| `ineligible-or-editorial-decision` | 0 |
| **Total** | **45** |

Immediately reusable clips: **20**. Net-new clips if all 45 approved examples receive pronunciation playback: **25**. Editorial-decision items: **0**. Distinct normalized utterances: **45**. Duplicate utterances: **0**.

Every reuse claim was checked through the production normalization implementation, resolved by the actual manifest key, and verified to point to a present non-empty MP3. All 20 exact reuses are also the 20 approved `repository-reuse` examples. All 25 new clips are editorial-generated examples that never entered the existing `data-*.js` audio rule.

## Equivalence, duplicates and collisions

All example strings are already normalization-stable: normalized text equals exact authored text. Therefore there are no normalization-equivalent-only reuses. The 45 normalized strings are unique, and none collides with a different manifest text at its 12-hex key. The global manifest also has no normalized duplicate or key/hash mismatch.

A future generator must still fail closed if an occupied 12-hex key carries different Polish text. “No current collision” is not permission to overwrite on a future collision.

## Eligibility judgment

All 45 are complete, approved Polish sentences with English translations. None contains an unfinished marker, placeholder, abbreviation, numeral or proper name that demands a pre-generation editorial decision. Recognition-only examples remain suitable for learner-initiated pronunciation because playback is receptive, not a production activity. This conclusion does not enable their flags; the governance and human audio-QA gates still apply.

## TTS QA priorities

The CSV marks heuristic risk only; it is not an audio-quality verdict. Human QA should pay closer attention to longer/multi-clause prosody and words such as `zaświadczenia`, `podwyżkę` and `Szczerze`. Questions require natural interrogative intonation. Every new clip still needs exact-text, pronunciation, stress, pacing, truncation and file-integrity review in the approved voice.

No audio was generated in Phase 0.
