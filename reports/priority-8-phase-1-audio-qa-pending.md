# Priority 8 Phase 1A — audio QA pending

Human listening QA is pending for exactly 25 net-new `pl-PL-MarekNeural` clips. No row is passed, approved, native-reviewed, or linguistically reviewed.

The machine-readable review queue is [priority-8-phase-1-audio-qa-pending.csv](priority-8-phase-1-audio-qa-pending.csv). It contains one row per clip with the example ID, lemma, pattern ID, exact Polish utterance, deterministic hash key, MP3 path, Phase 0 TTS-risk classification, special intonation/prosody issue, and `human_qa_status=pending`.

## Review procedure

For every row, the human owner should compare the clip against the exact Polish column and check pronunciation, lexical stress, clause/question intonation, pacing, truncation, artifacts, voice consistency, and whether the whole sentence is present. Pay additional attention to the rows marked moderate and to comma/clause prosody or question intonation.

The generated files awaiting human review are:

- [0b4d3fbd75d7](../audio/0b4d3fbd75d7.mp3), [14a59bbdc91a](../audio/14a59bbdc91a.mp3), [34d6718a97b5](../audio/34d6718a97b5.mp3), [3a1345633c7b](../audio/3a1345633c7b.mp3), [3d709270cdd6](../audio/3d709270cdd6.mp3)
- [49075a113c25](../audio/49075a113c25.mp3), [52221b23692c](../audio/52221b23692c.mp3), [67814b59e796](../audio/67814b59e796.mp3), [6ebd3768b640](../audio/6ebd3768b640.mp3), [779329e1891f](../audio/779329e1891f.mp3)
- [7e089f4410d7](../audio/7e089f4410d7.mp3), [9cd5878d87e5](../audio/9cd5878d87e5.mp3), [a47da763550c](../audio/a47da763550c.mp3), [b2b4d7e44eec](../audio/b2b4d7e44eec.mp3), [b304455b54fa](../audio/b304455b54fa.mp3)
- [b3d0274579f7](../audio/b3d0274579f7.mp3), [ba8ffae67384](../audio/ba8ffae67384.mp3), [bf30f876fb3d](../audio/bf30f876fb3d.mp3), [c9fd4250f49a](../audio/c9fd4250f49a.mp3), [cd4741e333d3](../audio/cd4741e333d3.mp3)
- [d883cb2fb59a](../audio/d883cb2fb59a.mp3), [deafd1c92fce](../audio/deafd1c92fce.mp3), [ef2b6a3eedbf](../audio/ef2b6a3eedbf.mp3), [f06e4a2bd9c3](../audio/f06e4a2bd9c3.mp3), [fb790bca5329](../audio/fb790bca5329.mp3)

Do not change any CSV status until the human has actually listened. Human QA must happen before integration or deployment.
