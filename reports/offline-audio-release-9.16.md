# Offline Pronunciation Download — release 9.16 preparation

## Scope and repository safety

This task prepared the approved Offline Pronunciation Download feature as a release candidate. It did not redesign or refactor the approved feature, generate audio, push, deploy, or transfer files to production.

| Item | Verified value |
|---|---|
| Repository | `/Users/Kaj/Downloads/Repository for Codex - Offline Audio Release 9.16` |
| Branch | `offline-audio-release-9.16` |
| Starting `HEAD` | `7aa740117b842d1d07fbfd85030a525be9451f26` |
| Starting `HEAD^{tree}` | `eec14123dc438998ea371a7ababc17cdef86e39d` |
| Starting worktree | clean |
| Git remotes | none |
| `push.default` | `nothing` |

All eleven required Phase 0–3 reports were read before editing. The approved implementation status entering release preparation was:

- Phase 0 architecture/design: **APPROVED**;
- Phase 1 downloader/cache engine: **APPROVED**;
- Phase 2 learner-facing UI: **APPROVED**;
- Phase 3 service-worker lifecycle compatibility: **APPROVED**;
- Phase 4A physical iPhone acceptance: **PROVISIONAL PASS**, with no apparent functional issues observed.

Neither `/Users/Kaj/Documents/GitHub/polishflashcards` nor `/Users/Kaj/Documents/Polish Flashcards - Offline Audio Integration` nor any earlier disposable repository was accessed. No production site or production repository was accessed. Git remotes remained empty throughout. Nothing was pushed or deployed.

## Release markers and approved architecture

- `APP_VERSION`: `9.15` → `9.16` in `index.html`.
- Versioned shell cache: `popolsku-v70` → `popolsku-v71` in `sw.js`, exactly once.
- `AUDIO_CACHE`: remains exactly `popolsku-audio`.

The `index.html` product diff is only the `APP_VERSION` line. The `sw.js` product diff is only the numbered shell-cache line. Consequently, downloader protocol behavior, page-orchestrated concurrency 3, worker-owned validated writes, reconciliation truth, cooperative Pause/Continue, successor protection, Remove/store ordering, quota single-flight recovery, Range handling, capability negotiation, old-active/new-page handling, and natural service-worker lifecycle are unchanged.

There is still no `skipWaiting()`, `clients.claim()`, Background Sync, direct page-side Cache Storage write, durable download-completion flag, automatic forced reload, analytics, telemetry, cookie, persistent user/device identifier, remote progress reporting, third-party API, or external tracker. Capability negotiation remains local page-to-worker messaging.

## Official generated output and sitemap

After updating `APP_VERSION`, `python3 build_pages.py` updated **31 learner-facing generated pages**:

- 23 grammar topic pages;
- 6 vocabulary topic pages;
- `guide/index.html`;
- `guide/listening/index.html`.

Every one of those 31 pages changed only its generated footer projection from `v9.15` to `v9.16`. The builder-owned redirect stubs did not differ and were not rewritten. `python3 build_pages.py --check` subsequently passed and reported 23 grammar pages, 6 vocabulary pages, the guide hub, 32 sitemap URLs, and 380 pronunciation-enabled generated examples/words.

The sitemap URL set and order remain structurally unchanged at **32 unique URLs**, with no duplicates. The exact date delta is:

- 31 generated learner-page entries: `2026-09-15` → `2026-09-16`;
- root `https://popolsku.app/`: remains `2026-08-06`, because it is not generator-rendered and repository convention deliberately carries its manually owned date forward.

No historical/static URL was arbitrarily redated.

## Exact changed paths and classification

The release candidate contains **38 changed paths** relative to the starting commit.

### A. Release markers (2)

- `index.html`
- `sw.js`

### B. Official builder-owned generated learner pages (31)

- `grammar/biernik-accusative/index.html`
- `grammar/celownik-dative/index.html`
- `grammar/dopelniacz-genitive/index.html`
- `grammar/jesli-i-gdyby-conditions/index.html`
- `grammar/kazdy-i-wszyscy-every-vs-all/index.html`
- `grammar/korespondencja-formal-writing/index.html`
- `grammar/ktory-relative-clauses/index.html`
- `grammar/liczebniki-numbers-meet-cases/index.html`
- `grammar/mianownik-nominative/index.html`
- `grammar/miejscownik-locative/index.html`
- `grammar/narodowosci-nationalities/index.html`
- `grammar/narzednik-instrumental/index.html`
- `grammar/pan-i-pani-formal-address/index.html`
- `grammar/panowie-panie-panstwo-plural-formal-address/index.html`
- `grammar/przeczenie-negation/index.html`
- `grammar/przymiotniki-adjectives-traits/index.html`
- `grammar/stopniowanie-comparison/index.html`
- `grammar/tryb-przypuszczajacy-conditional/index.html`
- `grammar/wolacz-vocative/index.html`
- `grammar/zaimki-pronouns-determiners/index.html`
- `grammar/zawody-professions/index.html`
- `grammar/zdrobnienia-diminutives/index.html`
- `grammar/zeby-so-that-want-to/index.html`
- `guide/index.html`
- `guide/listening/index.html`
- `vocabulary/everyday-polish-slang/index.html`
- `vocabulary/polish-corporate-slang/index.html`
- `vocabulary/polish-exclamations/index.html`
- `vocabulary/polish-idioms/index.html`
- `vocabulary/polish-party-slang/index.html`
- `vocabulary/polish-proverbs/index.html`

### C. Builder-owned sitemap output (1)

- `sitemap.xml`

### D. Narrow maintained current-release assertions (3)

- `tests/test_offline_audio_phase1_engine.js`
- `tests/test_offline_audio_phase2_ui.js`
- `tests/test_offline_audio_phase3_integration.js`

Only their live `9.15`/`v70` candidate expectations and current shell-cache fixture names changed to `9.16`/`v71`; no assertion was removed or weakened.

### E. Release evidence (1)

- `reports/offline-audio-release-9.16.md`

No other product, runtime, content, audio, manifest, or test path changed.

## Maintained test results

### Required Offline-audio suites

| Suite | Result |
|---|---:|
| Phase 1 engine | **89 passed, 0 failed** |
| Phase 2 UI | **104 passed, 0 failed** |
| Phase 3 integration | **50 passed, 0 failed**; it also internally reran Phase 1 at 89/0 |

### Established maintained protected regressions

The established Phase 3 protected matrix passed **3,630 assertions, 0 failed**:

| Area | Result |
|---|---:|
| audio fallback | 585/0 |
| inline audio failure/Retry and Audio Status Layout | 38/0 |
| Priority 8 playback | 25/0 |
| accessibility foundation | 82/0 |
| keyboard/focus | 214/0 |
| core activity accessibility | 127/0 |
| Listening accessibility | 229/0 |
| Listening variety | 193/0 |
| Mixed Quiz audio | 260/0 |
| Mixed Quiz accessibility | 411/0 |
| Mixed Quiz distractors | 195/0 |
| Mixed Quiz round legibility | 346/0 |
| Conversations | 101/0 |
| Podcasts | 100/0 |
| Grammar | 616/0 |
| shared overlays/dialogs | 108/0 |

Additional current suites passed **1,826 assertions, 0 failed**:

- Type It eligibility 120/0, feedback 846/0, hints 186/0, and prompts 343/0;
- activity behavior 146/0;
- round scoring 168/0;
- current Priority 8 Phase 1 Python suite 17/0.

The maintained protected and supplemental regression total is therefore **5,456 passed, 0 failed**, excluding the three required Offline-audio suite totals to avoid double-counting their separately reported evidence.

## Historical frozen exceptions

Historical provenance suites were run without mass replacement or weakening:

- navigation: **393 passed, 2 failed** — frozen app `8.11` and shell `v66` locks;
- focus/scroll: **315 passed, 1 failed** — frozen app `8.11` lock;
- mobile layout: **168 passed, 1 failed** — frozen app `8.11` lock;
- offline navigation/installability: **185 passed, 3 failed** — frozen app `8.11` and shell `v66` locks;
- Range/storage resilience: **554 passed, 9 failed** — frozen app `8.11`, shell `v66`, 3,377-clip inventory, and pre-Phase-1 source-shape/diagnostic/write-call counts; maintained replacement coverage is green in Phase 1/3;
- generated-page unit provenance: **98 passed, 2 failed** — frozen app `8.11` and pre-Offline-audio direct-route source shape; the official current `build_pages.py --check` passes and all 31 current generated pages project `9.16`;
- Phase 3 historical closeout: **505 passed, 5 failed** — frozen app `8.11`/shell `v66` plus pre-Phase-2 route and narrow-layout selector allowlists;
- Verb Patterns search: **11 behavioral tests passed, 1 failed** — frozen app `8.13` scope lock;
- speaker-icon UI: **4 behavioral tests passed, 1 failed** — frozen app `8.13`/shell `v68` input-scope lock;
- historical service-worker cache suite still aborts at its frozen `v66` invalid-read seed and old protocol prohibition;
- historical Priority 7 patterns UI still aborts at its removed `p7-fixture-card-001` support fixture.

These are historical release/source snapshots, not current regressions. Their maintained behavioral replacements passed. No historical value was edited to manufacture green output.

## Validators and canonical invariants

| Command | Result |
|---|---|
| `python3 validate_content.py` | passed — 10 levels, 97 topics, 1,215 cards, 353 drills; forward baseline intact |
| `python3 verify_audio.py` | passed — 3,621 required, 3,621 manifest entries, 3,621 MP3s, 0 missing, 0 orphaned |
| `python3 validate_priority8_staging.py` | passed — read-only revision 8 valid |
| `python3 build_pages.py --check` | passed — generated output current; 32 sitemap URLs |
| `git diff --check` | passed in the final candidate audit |

Exact audio state:

- 3,621 required pronunciations;
- 3,621 manifest entries;
- 3,621 MP3 files;
- 0 missing;
- 0 orphaned;
- 54,378,576 payload bytes;
- 51.859451 MiB.

Exact Verb Patterns state:

- 98 lemmas;
- 129 meanings;
- 269 patterns;
- 269 examples;
- 269 pronunciation-enabled examples.

No learning dataset, pronunciation eligibility, Listening eligibility, or stable ID changed.

## Protected-file and MP3 identity

The final diff against the starting commit is empty for every protected path below. Their Git blob IDs remain:

| Path | Git blob |
|---|---|
| `audio-manifest.json` | `665696228f10ba239ea9e39d21d4e0e0ec782b94` |
| `content/verb-patterns.json` | `7e7269e714fe2535734a772a20ee707aa46644ed` |
| `pp-verb-patterns.js` | `22dba6bb2eef5f2b11f8cbdc738b50a855fcd6db` |
| `pp_audio_rule.py` | `38b97d80553e7ea05fc5e6d78e274e489d79b595` |
| `pp-usage.js` | `c27602d7fb4197f10648f90f46fc1c3886827841` |
| `manifest.json` | `a2a687c85e262189d4ef87c45b45f3c82c16b6e8` |

The complete `audio/` Git tree remains `7a2ab13e6b7e537f0f64c768db8ee6b36cb5396a`. This proves every tracked MP3 name and byte is identical to the starting commit. The manifest SHA-256 remains `09f038097c118c6c55c00f15185a5e4207d02f103480675ad0b3a499ab3ad0a7`.

## Privacy, install, about, lifecycle, and physical-device status

Privacy and Install copy remain byte-identical to the approved Phase 2/3 state. The Privacy date remains **15 September 2026** because no substantive Privacy wording changed. About copy is unchanged; generated guide pages changed only their version projection.

The service worker retains its natural lifecycle: no forced activation, no client claim, capability negotiation intact, truthful old-active/new-page compatibility, controller-change invalidation, and no automatic forced reload. The versionless audio cache is preserved across the release.

Physical iPhone acceptance is accurately recorded as **PROVISIONAL PASS**. Real-device testing found no apparent functional issues. This is not an exhaustive 3,621-item, VoiceOver, or every-scenario acceptance claim. Definitive physical-device acceptance is explicitly deferred to the deployed live release's post-deployment smoke test.

## Finalization record

The release is finalized as one focused commit titled `Prepare Offline Audio release 9.16`. The exact commit and tree object IDs are reported immediately after commit creation in the final completion report; embedding the report's own final tree hash inside this tracked file would change that tree recursively.

The committed worktree is required to be clean, with zero remotes, `push.default=nothing`, nothing pushed or deployed, and production never accessed. Independent review is required before any production transfer.
