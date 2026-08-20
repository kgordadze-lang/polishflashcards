# Priority 8 Phase 1A — audio generation

## Deterministic input

The single audio rule now validates and reads pronunciation-eligible examples only from the committed public runtime. Private editorial files, reports, previews, and test fixtures are not discoverable. The combined required set is 3,402 unique normalized utterances: the unchanged 3,377 lesson phrases plus 45 Verb Patterns examples, of which 20 resolve to existing content hashes and 25 are absent at the baseline.

The generator still uses `pl-PL-MarekNeural`, SHA-256 first-12 content addressing, exact normalization parity, incremental reuse, and `audio-manifest.json`. It now refuses an occupied hash whose Polish text or canonical path differs instead of overwriting it. Its `--allowlist-csv` gate also refuses synthesis unless the repository's complete missing-phrase set exactly equals the normalized `exact_polish` column of the supplied review CSV.

## Synthesis result

On 2026-08-20 the owner explicitly authorized sending only the 25 Polish sentences in `reports/priority-8-phase-1-audio-qa-pending.csv` to Microsoft Edge TTS with `pl-PL-MarekNeural`. The allowlisted generation command created exactly 25 clips, reported zero synthesis failures, and wrote no alternative voice or speculative variants. No report fields, repository identifiers, metadata, or other files were supplied to the TTS service.

Post-generation verification found 3,402 required normalized phrases, 3,402 manifest entries, and 3,402 non-empty MP3 files. Missing, orphan, duplicate-normalized, hash-collision, key/path mismatch, and synthesis-failure counts are all zero. All 20 reused manifest entries and MP3 byte streams remain identical to the starting Git revision. All 25 new files identify technically as MPEG ADTS layer III, 48 kbps, 24 kHz, monaural; they total approximately 456 KiB and remain local to this disposable repository.

All 25 new clips remain `human_qa_status=pending`. These structural and inventory checks are not listening approval.
