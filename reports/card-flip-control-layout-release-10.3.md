# Card flip control layout release 10.3 preparation

## Repository and approved baseline

- Working repository: `/Users/Kaj/Downloads/Repository for Codex - Flip Control Layout Release 10.3`
- Branch: `release/card-flip-layout-10.3`
- Starting HEAD and approved implementation commit: `839c37e2d82eb9dc3deb51e1368a256dd8a7fc6d`
- Starting tree and approved implementation tree: `d1878f65a6af606f2c3d1ac5dd33f714e4d8da1e`
- Starting worktree was clean; `git remote -v` was empty; `push.default=nothing`.
- The approved control row, face structure, button count, interactions, keyboard behavior, and accessibility wiring were not substantively changed. The only `index.html` change is `APP_VERSION`.

## Release markers and generated output

- Release date: **2026-10-03**.
- `APP_VERSION`: `9.19` → `10.3` in `index.html`.
- Service worker shell `CACHE`: `popolsku-v75` → `popolsku-v76`.
- `AUDIO_CACHE`: remains `popolsku-audio`.
- `SCHEMA_VERSION`: remains `2`; `CONTENT_MIGRATION_REVISION`: remains `2`.
- Official builder command: `PYTHONDONTWRITEBYTECODE=1 python3 build_pages.py` (equivalent to the requested `python3 build_pages.py` without bytecode side effects).
- The builder changed **31 versioned learner pages**: 23 grammar topic pages, 6 vocabulary topic pages, the guide hub, and the listening guide. Each generated-page byte delta is solely `v9.19` → `v10.3`. The builder owns 33 HTML outputs in total; the grammar and vocabulary redirect stubs were unchanged. No current builder-owned page retains `v9.19` or `popolsku-v75`.
- `sitemap.xml`: 32 URLs before and after, all unique, no URL/order changes. All 32 `<lastmod>` values advanced from `2026-09-22` to `2026-10-03`: 31 changed generated pages plus the manually dated root application shell.
- A second builder run changed **0** files; `build_pages.py --check` passed. Generated output is deterministic.

## Validation

- Focused `tests/current/test_card_flip_layout.py`: **3/3 passed**. Its assertions still cover the normal-flow row, one native labeled button per scene, control before rotating faces, flip and Prev/Next wiring, the reported Nominative sentence, and current release markers.
- Maintained current regression runner: **10/10 JavaScript suites and 116/116 Python tests passed**, covering navigation, responsive/mobile layout, accessibility/focus, card and audio behavior, grammar and front/back states.
- Selected legacy assertions: grammar interaction **616/616**; activities **146/146**; audio failure inline feedback **38/38**; Phase 1A accessibility **82/82**; Phase 1B keyboard/focus **214/214**; Phase 2A core activity accessibility **127/127**. Total **1,223/1,223** passed. No historical allowlist was broadened.
- `validate_content.py`: passed; 10 levels, 97 topics, 1,215 cards, 353 drills; forward baseline unchanged.
- `verify_audio.py`: passed; **3,621 required, 3,621 manifest entries, 3,621 MP3 files, 0 missing, 0 orphaned**.
- `verb_patterns_runtime_validator.py`: passed; **98 lemmas, 129 meanings, 269 patterns, 269 examples, 269 pronunciation-enabled examples**.
- `validate_current_release.py`: passed; release and storage markers valid.
- `build_pages.py --check`: passed; no generated drift.
- `git diff --check`: passed.
- The known pre-existing `ResourceWarning` for `audio-manifest.json` was **not observed** in these builder runs. It was not changed or repaired.
- Some passing `osascript` legacy suites emitted macOS `com.apple.hiservices-xpcservice` connection warnings; all selected assertions passed.

## Release diff and protected state

Exactly **36 paths** are in this release-preparation commit: 2 canonical marker files, 31 generated learner pages, 1 sitemap, 1 focused current test, and this report. Exact paths:

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
- `index.html`
- `reports/card-flip-control-layout-release-10.3.md`
- `sitemap.xml`
- `sw.js`
- `tests/current/test_card_flip_layout.py`
- `vocabulary/everyday-polish-slang/index.html`
- `vocabulary/polish-corporate-slang/index.html`
- `vocabulary/polish-exclamations/index.html`
- `vocabulary/polish-idioms/index.html`
- `vocabulary/polish-party-slang/index.html`
- `vocabulary/polish-proverbs/index.html`

The 12 named protected files are byte-identical to the approved implementation commit: `audio-manifest.json`, `content/verb-patterns.json`, `data-a1.js`, `data-a2.js`, `data-b1.js`, `data-grammar.js`, `data-podcasts.js`, `data-scenarios.js`, `data-verbs.js`, `pp-verb-patterns.js`, `pp_audio_rule.py`, and `pp-usage.js`. The `audio/` Git tree is unchanged (`7a2ab13e6b7e537f0f64c768db8ee6b36cb5396a`). No learning content, mappings, eligibility, privacy/install copy, analytics, offline audio architecture, or schema/migration behavior changed. The service worker runtime change is only its shell `CACHE` marker.

## Release boundary

This report is included in the single release-preparation commit, so its own final commit/tree hashes cannot be embedded in it without changing those hashes. The final commit and tree identifiers are recorded in the completion report. The worktree is to finish clean, with zero remotes. Nothing was pushed or deployed. The production repository was never accessed. This candidate requires independent release review before production integration.
