# Priority 7 — Audio Impact Analysis

**Phase:** 0 analysis only. No phrases were generated, no manifest changed and no MP3 was touched.

## 1. Verified current baseline

`python3 verify_audio.py` passes with exact forward/reverse parity: 3,377 required phrases, 3,377 manifest entries, 3,377 non-orphan MP3 files.

| Content source | Occurrences | Distinct required phrases |
|---|---:|---:|
| A1 | 668 | 647 |
| A2 | 1,019 | 997 |
| B1 | 620 | 615 |
| Grammar | 781 | 627 |
| Podcasts | 95 | 95 |
| Scenarios | 296 | 289 |
| Verbs | 259 | 215 |
| **Total distinct** | — | **3,377** |

The manifest voice is `pl-PL-MarekNeural`; its recorded generation timestamp is `2026-08-01T08:27:27.519443Z`.

## 2. Current phrase identity

[`pp_audio_rule.py`](../pp_audio_rule.py) is the phrase source of truth. It parses every `data-*.js` file as `PP_LEVELS.push(...)` content and recursively collects eligible utterance fields. A non-template dictionary with a string `pl` can be treated as main audio; selected nested `ex`, `full` and `npc` strings are also collected.

Runtime manifest lookup normalizes HTML/whitespace but does not case-fold or apply general Unicode normalization ([`index.html:3040`](../index.html#L3040)). Python and JavaScript normalization must stay in parity. A phrase that differs in case, punctuation, Unicode composition or wording may require a distinct clip even if a human considers it equivalent.

Generation hashes the normalized phrase with SHA-256 and uses the first 12 hexadecimal characters in the filename. It preserves nonempty existing files, rewrites the manifest, reports orphans and does not delete them automatically. Verification checks required→manifest→file and file→manifest coverage.

## 3. What Priority 7 should speak

| Content type | Audio? | Reason |
|---|---|---|
| Approved complete Polish example | yes, if used in listening/reference playback | natural prosody and reusable learner value |
| Approved feedback sentence | maybe | only when it is a complete natural utterance |
| Existing identical sentence | reuse | exact normalized manifest match |
| Lemma label | usually no | isolated dictionary-like audio adds little beyond existing card audio |
| Pattern notation | no | `szukać + genitive` is not a natural utterance |
| Case/preposition label | no | visual teaching metadata, not pronunciation content |
| Diagnostic question | generally no | avoid synthesizing abstract grammar prompts |
| Research candidate/unapproved example | no | fail closed until linguistic approval |

Audio eligibility must be explicit and separate from general activity eligibility. Generic `pl` keys must not cause every pattern label to enter synthesis.

## 4. Reuse and net-new growth

Existing cards, grammar and scenarios already supply many natural sentences. A future inventory step should compare each approved authored example against the manifest using the exact shared normalization rule before generation.

The likely pilot growth driver is one or more independently authored examples per approved meaning/pattern—not the 30 lemma labels. A rough planning range is **30–90 distinct new utterances** if the pilot uses one to three non-reused sentences per verb. This is an estimate, not an inventory. The exact delta must be produced after content/native review and before synthesis.

Potential reuse is highest for patterns already present in case lessons/scenarios (`potrzebować`, `pomagać`, `używać`, `płacić`, `szukać`, `interesować się`). Reuse still requires exact phrase identity and editorial approval; an existing sentence is not automatically the best Priority 7 example.

## 5. Cache capacity and retention

The service worker uses:

- shell cache `popolsku-v65`;
- versionless audio cache `popolsku-audio`;
- maximum target 4,200 entries;
- trimming toward 4,000 entries;
- batches of 64 with one retry.

At 3,377 current clips, nominal headroom is 823 files before the maximum and 623 before crossing the trim target. A 30–90 clip pilot fits numerically, but storage pressure and per-device eviction remain relevant. Audio remains lazy/cache-first, not shell-precached.

Do not rename `popolsku-audio`: its content-hash identity lets existing clips survive releases. A shell cache bump is a separate deployment concern when loader/manifest/SW assets change.

## 6. Safeguards for later phases

1. Add an explicit approved-example collector for the pattern schema.
2. Reject labels, questions, notation and unapproved records in the audio inventory.
3. Verify Python/JavaScript normalization parity, including NFC edge cases.
4. Report exact reuse, new and retired/orphan counts before synthesis.
5. Generate incrementally; never delete orphans as a side effect of ordinary generation.
6. Verify manifest/file forward and reverse coverage, nonempty files and hash identity.
7. Update pinned test counts deliberately.
8. Perform native listening QA for pronunciation, segmentation, stress/prosody and example naturalness.
9. Test Range requests, offline playback, cache retention and storage-pressure behavior.

## 7. Phase recommendation

Do not include audio in specification/tooling Phase 1 or validator Phase 2. After a small data pilot has passed linguistic review, run a read-only audio inventory and approve its exact delta. Generate audio only in a separately reviewable phase with manifest, MP3, service-worker and retention tests updated atomically.
