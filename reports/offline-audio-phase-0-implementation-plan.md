# Offline Pronunciation Download — phased implementation plan

## Phase 0 — audit and design (this commit)

Deliver only the eight required reports. Independently verify repository state, 3,621/3,621/3,621 inventory, 54,378,576 bytes / 51.859451 MiB, manifest schema/uniqueness/order, cache/Range/retention/quota path, UI placement/states, storage constraints, tests, risks, and implementation decomposition.

Exit gate:

- reports-only diff and exact required filenames;
- no changes to product, tests, content, manifest, audio, generated pages, sitemap, versions, shell cache, or `AUDIO_CACHE`;
- reports committed as `Audit offline pronunciation download architecture`;
- clean worktree, zero remotes, nothing pushed/deployed, production never accessed;
- stop for independent review.

## Phase 1 — shared downloader/cache engine and deterministic tests

Implement behind no learner-visible entry point initially if practical.

1. Refactor existing audio cache write into one promise-returning validated store primitive while retaining ordinary `cacheWrite()` behavior exactly.
2. Add strict local service-worker message commands for reconcile, store-one, and remove.
3. Require same-origin/scoped/exact canonical hashed MP3 keys and full status-200 `audio/mpeg` responses.
4. Keep Range structurally outside all writes.
5. Make store acknowledgements distinguish already present, stored, bad response, network failure, and final storage failure.
6. Serialize or otherwise bound quota-recovery critical sections so concurrent failures cannot each evict 64 entries uncontrolled.
7. Reset entry estimate on Remove.
8. Build a page-side engine module/block with deduped manifest set, generation token, missing queue, concurrency exactly 3, cooperative pause, bounded failure policy, and no required persistence metadata.
9. Add deterministic cases 1–16 and 18 from the test plan plus capability/storage variations.

Protected behavior:

- ordinary lazy playback for learners who never download;
- current audio status layout/failure/Retry/stale-owner behavior;
- cache-first MP3 and named validated reads;
- Range synthesis/pass-through/no-write;
- FIFO 4,200/4,000 and one 64-entry retry;
- shell update lifecycle with no forced activation;
- `AUDIO_CACHE = "popolsku-audio"`.

Exit gate: exact behavioral tests pass; existing behavioral suites pass; any historical release-count locks are deliberately updated/scoped with review; `verify_audio.py` remains 3,621/3,621/3,621; no UI or content change.

## Phase 2 — Offline audio screen, progress, resume, update, and remove

1. Add an Offline audio in-app screen and one menu item near Install.
2. Implement all required states: unsupported, checking, not downloaded, partial, downloading, pausing/paused/interrupted, complete, update available, network/bad-response/storage failure, removing, removal complete/failure.
3. Render exact cache-derived count and current manifest total; show “About 52 MB”.
4. Add native Download/Pause/Continue/Update/Remove controls and accessible confirmation.
5. Use native progress semantics and milestone-throttled live announcements.
6. Request persistence opportunistically on explicit intent; use estimate only as advisory.
7. Pause on navigation away; never promise background continuation.
8. Align Privacy and Install/About copy factually with optional full download and eviction caveat. This is copy consistency only, with no analytics/privacy model expansion.
9. Add deterministic UI/accessibility case 17 and state-transition/race coverage.

Exit gate: keyboard and screen-reader semantics verified in harness; no focus stealing; reduced motion and large-text layout protected; no prompt in learning flows; ordinary users see no behavioral change unless they choose Offline audio.

## Phase 3 — integration and offline regression

1. Run full audio/cache/Range/fallback/navigation/accessibility suites.
2. Verify download then offline playback across flashcards, grammar, conversations, Type It feedback, Listening, mixed rounds, Verb Patterns, global search results, and committed generated pages.
3. Verify partial download and cold-offline behavior preserves speech synthesis and visible Retry.
4. Decide separately whether to add the specific “This pronunciation isn't downloaded for offline use.” status; do not conflate it with downloader completion.
5. Verify stale replies, activity navigation, manifest refresh, worker update/waiting state, Remove races, and lazy rewarming.
6. Reconfirm 98 lemmas, 129 meanings, 269 patterns/examples/pronunciations and canonical phrase identity.
7. Reconfirm no audio generation, content/manifest regeneration, telemetry, tracking, cookies, identifiers, reporting endpoints, or backup payload change.

Exit gate: all deterministic and repository gates pass; clean candidate suitable for physical-device testing.

## Phase 4 — physical iPhone acceptance

Execute the full real-device matrix in the iOS/storage and test-plan reports on Safari and an installed Home Screen app.

Required evidence:

- device/OS/browser/build and environment;
- active manifest total and final reconciled cache total;
- start, pause, navigation, background/foreground, force-quit/restart, network-loss/resume, quota/low-storage where possible, completion, flight-mode sampling, Range scrubbing, VoiceOver, reduced motion/large text/orientation, Remove, and lazy rewarm outcomes;
- explicit record that background completion and permanence are not claimed.

If concurrency 3 is unstable, test 2 and lower the constant without changing state semantics. Do not increase above 3 merely for speed without new evidence.

Exit gate: every critical scenario passes or has an explicit product-owner risk decision; exact Complete state demonstrated from reconciliation, not UI counter.

## Phase 5 — release preparation

1. Review final learner copy and size against freshly measured repository bytes/count.
2. Recalculate retention headroom; block/revisit policy before active manifest reaches 4,000.
3. Advance learner-visible `APP_VERSION` and numbered shell cache only under existing release policy; never rename `popolsku-audio`.
4. Regenerate only generator-owned outputs required by the approved product release, then run their checks.
5. Run full test/content/audio/build suite and review diff allowlist.
6. Confirm Privacy remains accurate and no tracking/storage identifier was introduced.
7. Produce rollback notes: UI/worker protocol can roll back while versionless content-hashed audio remains reusable; rollback must not clear the audio cache.
8. Independent review before any deployment. Push/deploy is outside this Phase 0 authorization.

## File/scope expectations for later phases

Likely Phase 1/2 files are `sw.js`, `index.html`, and new focused tests; whether a small external helper is preferable should be decided during implementation based on the repository’s current single-file architecture and shell precache policy. Any new shell asset must join required precache and version staging coherently.

Do not modify `audio-manifest.json`, `audio/`, learning content, Verb Patterns runtime, or canonical identity for this feature. Do not create a second manifest/cache/library, ZIP, IndexedDB MP3 copy, playback stack, analytics, telemetry, cookies, identifiers, or reporting endpoint.

## Review checkpoints

- After Phase 0: approve architecture and product semantics.
- After Phase 1: review worker trust boundary, shared write behavior, quota serialization, and deterministic evidence before UI.
- After Phase 2: review copy, accessibility, Remove meaning, and no-background/no-permanence honesty.
- After Phase 3: review regression evidence and content invariants.
- After Phase 4: product-owner acceptance on physical iPhone evidence.
- Before Phase 5 deployment: independent release review and separate authorization.
