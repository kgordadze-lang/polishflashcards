# Priority 8 Phase 0 — current production baseline

## Scope and starting gate

This audit ran only in `/Users/Kaj/Downloads/Repository for Codex - Priority 8 Phase 0`. The prohibited production repository and the Priority 8 integration repository were not accessed. No remote was added, no push or deployment was attempted, and no symlink was followed.

| Gate | Verified value | Result |
|---|---|---|
| Path | `/Users/Kaj/Downloads/Repository for Codex - Priority 8 Phase 0` | pass |
| Branch | `priority-8-phase-0-audit` | pass |
| Starting HEAD | `2bf4d09505866c9a47ecfa0f6634d6f05352f679` | pass |
| Starting tree | `52b988c0818eecc5b90b64f901dc65aa4a2888d2` | pass |
| Starting status | clean | pass |
| Remotes | none | pass |
| `push.default` | `nothing` | pass |
| `.git/hooks/pre-push` | regular file, mode `-rwxr-xr-x`, executable | pass |
| Repository symlinks | none found (scan excluded `.git` and did not follow links) | pass |

The gate was checked before broad repository traversal. All conditions matched, so the audit continued.

## Verified release identifiers

| Item | Source | Verified value |
|---|---|---|
| `APP_VERSION` | `index.html:1987` | `8.11` |
| Shell cache | `sw.js:26` | `popolsku-v66` |
| Audio cache | `sw.js:27` | `popolsku-audio` |
| `SCHEMA_VERSION` | `pp-migrate.js:21` | `2` |
| `CONTENT_MIGRATION_REVISION` | `pp-migrate.js:25` | `2` |
| Runtime | committed file | `content/verb-patterns.json` |
| Runtime SHA-256 | `shasum -a 256` | `d7911b2a4597147f3f0336c9b0cd154d1bec390d246fc4f33620b7bcf46460ed` |
| `formatVersion` | runtime JSON | `1` |
| `patternDataRevision` | runtime JSON | `1` |

## Recalculated Verb Patterns baseline

| Measure | Exact value |
|---|---:|
| Lemmas | 30 |
| Meanings | 34 |
| Patterns | 45 |
| Examples | 45 |
| Content references | 101 |
| Error notes | 24 |
| Active-production patterns | 41 |
| Recognition-only patterns | 4 |
| Non-empty `activityEligibility` arrays | 0 |
| `audioEligible: true` examples | 0 |
| Priority 7 pronunciation clips shipped | 0 |

All 45 private editorial pattern records are `approved`, all use `solo-maintainer-reference-backed`, and the latest current-scope event on each is `product-approval: accept`. The public runtime correctly excludes private evidence, origins and review history.

## Recalculated global audio baseline

The source-of-truth rule reported 3,377 required normalized phrases. `verify_audio.py` checked exactly 3,377 manifest entries and 3,377 MP3 files: 0 missing entries, 0 missing/empty files, 0 stale manifest entries and 0 orphaned MP3s. Every manifest key equals the first 12 hex characters of SHA-256 over the normalized Polish text; every value points to `audio/<key>.mp3`. There are no duplicate normalized manifest utterances and no zero-byte clips.

The current voice is `pl-PL-MarekNeural`; the manifest timestamp is `2026-08-01T08:27:27.519443Z`.

## Validation evidence

- `python3 validate_content.py`: pass; 10 levels, 97 topics, 1,215 cards, 353 drills, 1,675 unique IDs; frozen forward digest `2a71401d8966ccbda59ec696f2c41cc3b48801d5c6059a881183b44ea3a1ce50`.
- `python3 pp_audio_rule.py`: 3,377 phrases; 25 templates, none with complete `audioText`.
- `python3 verify_audio.py`: pass; exact audio parity, no orphans.
- Runtime SHA-256 and all JSON counts were independently recomputed rather than copied from prior prose.

No material baseline discrepancy was found.
