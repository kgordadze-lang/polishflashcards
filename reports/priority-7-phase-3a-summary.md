# Priority 7 — Phase 3A Summary

**Phase:** 3A — Learner Experience and Runtime Integration **Architecture and UX design only**.
No learner-facing functionality was implemented, and nothing is approved for release.

**Revision:** Phase 3A architecture correction pass applied. The architecture was provisionally
accepted subject to amendments, all of which are incorporated into the five reports. See §8 for the
amendment record.

## 1. Baseline

Verified before any work, all matching the expected values:

| Check | Verified value |
|---|---|
| Branch | `priority-7-phase-3a-ux-architecture` |
| HEAD | `2b152f4d6079762f875bf1f3a2b3c2699970e4c2` |
| Tree | `f6e9b3ae49bd7e0f35bc2ba6f7bfd092ed017fc3` |
| Git remotes | **none** |
| `push.default` | `nothing` |
| Starting worktree | clean |

## 2. Audit performed

The shipping application was inspected directly before any recommendation was formed. Covered:
`index.html` (all 5,615 lines — markup, both `<style>` blocks, the inline script), `pp-usage.js`,
`pp-answer.js`, `pp-distractor.js`, `pp-migrate.js`, all seven `data-*.js` files, `sw.js`,
`build_pages.py`, `validate_content.py`, the generated `grammar/`, `vocabulary/` and `guide/`
output, and the assertions of the JXA and Python test suites — in particular
`test_grammar_interaction.js`, `test_typeit_*`, `test_mixed_*`, `test_listening_*`,
`test_phase1a_accessibility.js`, `test_phase1b_keyboard_focus.js`,
`test_phase2a_core_activity_accessibility.js`, `test_phase2c_navigation.js`,
`test_phase3b_mobile_layout.js`, `test_phase3_closeout.js`,
`test_phase4b1_service_worker_cache.js` and `test_priority7_phase2a.py`.

The authoritative Priority 7 material was read as locked input: the Phase 0 audit reports, the
Phase 1 specification set, the Phase 2A tooling summary, the Phase 2B authoring/source/queue/coverage
summaries, `reports/priority-7-phase-2c-summary.md`, `reports/priority-7-phase-2c2-summary.md`,
`priority7_tooling.py`, `tests/test_priority7_phase2a.py`, and both `editorial/*.json` files
(read-only).

Two facts were verified mechanically rather than assumed:

- `validate_editorial(corpus, committed_context)` returns **0 issues**;
- `project_runtime_nonrelease(corpus, 1, context)` raises
  `PROJECTION_EMPTY $.lemmas: No current approved active/recognition pattern can be projected.`

The corpus is structurally sound and simultaneously unprojectable. Structural validity and release
authorization are orthogonal, and this corpus is the proof.

## 3. Primary UX recommendation

**A hybrid, with a dedicated Verb Patterns surface as the home of the content, reached through the
existing Grammar category; case lessons and vocabulary cards act as doorways, never as second
copies.**

**`Verb Patterns → lemma → meaning → pattern` is the one canonical ownership hierarchy.** The A–Z
verb index is the default and canonical entry point; **case is a filter/view over that one index**,
addressable as deep-linked state, and never an owner or a container.

- **Tier 1** — a `Verb patterns` level with `group:"grammar"`, synthesized at runtime exactly as
  `Type it` and `Listening` already are, contributing **one** topic (the verb index) and opening onto
  a read-first `#patterns` screen with an in-screen case-filter chip row.
- **Tier 2** — one outbound deep link per case topic into the case-filtered index state, one
  back-link per pattern to its case lesson.
- **Tier 3** — one optional pointer line on the vocabulary card back, resolved through a **narrowly
  eligible** reverse index (`kind:"card"` + `purpose:"support"` only), gated on both reference count
  and lemma-level meaning ambiguity.

Lemma-first handles what case-grouping could not: multi-case lemmas (`rozmawiać`, `płacić`,
`zależeć`) stay in one entry; multi-complement patterns appear whole with the matched chip
emphasised; and infinitive and clause complements — which have no case at all — have a home rather
than vanishing, plus an explicit `No case (verb / clause)` filter option.

Rejected: patterns inside the seven case topics (shreds multi-case lemmas, duplicates existing
Grammar content, wrong primary key); **case-grouped sets as containers inside the new surface** —
the superseded first draft — for the same reasons, plus no home for infinitive/clause complements;
cards as the primary host (`CARD_FIELDS` is closed, coverage is partial, cards are not meanings, the
back face is full); a fourth top-level tab (`.cat-seg` is a pinned three-tab row); generated static
pages (out of pilot scope, and a public claim about `research` content); reusing `gRenderTeach` (it
is `innerHTML` over authored markup).

**Case UX:** one chip type everywhere, reading `question(s) · Full Case Name`, with the preposition
bonded inside the chip, and a plain-English role phrase directly beneath it. No abbreviations, no
notation, no per-case colour coding. Questions are derived centrally from a seven-row table — the
corpus contains zero `questionOverridePl`, so central derivation covers it completely, and all ten
preposition+case combinations present derive to natural Polish.

**Activities:** `grammar-choose` only, and only after real approvals. Type It may eventually gain a
correction line in feedback but never a cue; Mixed Quiz is excluded because `rRecord` exists to write
card progress; Listening is excluded because pattern knowledge does not serve utterance→meaning
recognition and zero examples are audio-eligible; a new "Build the pattern" activity is assessed and
declined.

**Progress:** nothing persists. No new storage key, no schema migration, no analytics, no telemetry,
no cookies, no identifiers. The parked Priority 6 measurement decision is not reopened.

## 4. Primary runtime recommendation

Preserve the locked boundary: **private editorial record → `freeze_editorial` → authorized frozen
release → public `content/verb-patterns.json` → `pp-verb-patterns.js` → UI.**

**Two responsibilities, deliberately separated.** The **browser loader** owns shape and safety at
load time: it may accept only the expected public runtime shape, reject private editorial and
non-release envelope fields, fail safely when data is unavailable or malformed, and expose no
private provenance or review field. It **must never be described as proving that a runtime artifact
came from an authorized frozen release** — it cannot, and a hand-edited file looks identical to it.
Only the **frozen/release machinery** can establish active membership, tombstone validity,
review/release state and an authorized frozen projection; that is the authoritative release gate,
and it runs at build time on private inputs the browser never receives.

Phase 3B builds and tests against an **explicitly synthetic, invented-verb fixture** generated by the
existing `project-fixture` non-release path, committed at `tests/fixtures/priority7/` — a path the
Phase 2A deployment tests already assert absent from every public surface. Copying a subset of the
real research corpus is rejected, because it would require marking real linguistic claims `approved`
that no human has authorized.

**How the tests consume a fixture the shipping loader refuses.** The unwrap happens in a **test-only
harness path**, never in production code: the harness asserts the wrapper's `artifactStatus` and
`releaseAuthorized: false`, reads `runtimeProjection`, and feeds it to a test-only injection entry
point that reaches the same derivation code the fetch path feeds. Production code must never strip
`releaseAuthorized: false`, convert a `project-fixture` envelope into something loadable, or treat
fixture validation as release proof. One test proves the loader **rejects** the wrapped file;
another proves the injected projection renders — together showing the wrapper is load-bearing.

Preserved throughout: **test fixture ≠ validated runtime shape ≠ authorized frozen release.**

Two existing Phase 2A assertions will fail when a loader is added — the exact eleven-entry
`<script src>` list and the protected-surface `git diff`. That is the guard working. Both must be
**narrowed in the same reviewed slice**, never deleted.

## 5. Proposed implementation sequence

| Slice | Objective | Gate |
|---|---|---|
| **3B** | Non-release fixture + test harness path + passive lemma-first reference surface + **required `routeTopic` default-deny** | four gate items: presentation architecture approved; §A4a routing complete with its nine regression tests; the harness contract proven from both sides; line-by-line review of the two amended deployment assertions |
| **3C** | Cross-links: case lessons deep-link into the filtered index, patterns link back, card-back pointer under the two-gate rule | linking direction right; the deep link lands in a filtered *view*, not a container; no duplication in the case lessons |
| **3D-1** | **Synthetic activity-mechanics prototype — startable after 3B, no linguistic approval needed** | owner approval of mechanics and negative progress evidence; **no linguistic sign-off required, and none may be claimed** |
| **3D-2** | Integration of **real** Priority 7 activity items — **currently unstartable** | seven prerequisites, incl. named reviewers, one genuinely `approved` pattern with `grammar-choose`, reviewed item records, and a release |
| **3E** | Accessibility and mobile hardening on real devices | owner approval of the accessibility evidence record |
| **3F** | Release gate — a decision, not a change | complete review of every released pattern, plus closure of the Phase 2C.2 open items and the Phase 0 `nie lubię` / `chcieć` inconsistencies |

**Routing default-deny is a required 3B safety task, not a cleanup.** `routeTopic()` currently has
no default-deny branch, and Phase 3B introduces the first new topic `kind` since `typeit`/`listen` —
which is what makes the latent fallthrough reachable. Stop condition: if any unknown or malformed
`kind` can still reach an incompatible renderer, 3B does not ship.

## 6. Files created

Exactly five, all tracked reports under `reports/`:

1. `reports/priority-7-phase-3a-current-surface-audit.md`
2. `reports/priority-7-phase-3a-ux-integration-architecture.md`
3. `reports/priority-7-phase-3a-runtime-prototype-contract.md`
4. `reports/priority-7-phase-3a-implementation-plan.md`
5. `reports/priority-7-phase-3a-summary.md`

No implementation file, no runtime JSON, no mock HTML, no test change, no modification to any
existing report.

## 7. Confirmations

**Application, data and tooling unchanged.** `index.html`, `sw.js`, all seven `data-*.js` files,
`pp-usage.js`, `pp-answer.js`, `pp-distractor.js`, `pp-migrate.js`, `build_pages.py`,
`validate_content.py`, `generate_audio.py`, `verify_audio.py`, `pp_audio_rule.py`,
`priority7_tooling.py`, `audio-manifest.json`, `sitemap.xml`, `manifest.json`, `robots.txt` and the
`audio/`, `grammar/`, `vocabulary/`, `guide/` and `fonts/` trees are byte-identical to the baseline.

**Tests unchanged.** No file under `tests/` was created, modified or deleted.

**Editorial content unchanged.** `editorial/verb-pattern-candidates.json` and
`editorial/priority-7-authoring-context.json` are byte-identical to the baseline. They were read
only.

**Review state unchanged.** All **45** patterns remain `reviewState: research`. **Zero** review
events exist; `reviewEvents` remains empty on all 45. Zero reviewer identities and zero author
identities were created. All 45 `activityEligibility` arrays remain empty.

**No runtime Priority 7 data.** `content/verb-patterns.json` does not exist. No public runtime
corpus, no fixture, no mock data of any kind was created.

**Version markers unchanged.** `APP_VERSION` `8.10`; shell cache `popolsku-v65`; audio cache
`popolsku-audio`; progress `schemaVersion` `2`; `CONTENT_MIGRATION_REVISION` `2`;
`patternDataRevision` still does not exist.

**Production untouched.** No deployment, no build, no generated-page regeneration, no audio
generation. Production was out of scope and was not accessed.

**Git.** Zero remotes. `push.default=nothing`. **No commit. No push. No remote added.**

Final `git status --short --untracked-files=all` shows exactly the five new Phase 3A reports and
nothing else.

## 8. Amendment record — architecture correction pass

Four amendments were required before integration. All are incorporated; no new file was created and
no file outside the five Phase 3A reports was touched.

| # | Amendment | Where applied |
|---|---|---|
| **1** | Make the primary hierarchy genuinely lemma-first: `Verb Patterns → lemma → meaning → pattern` is the sole canonical ownership hierarchy; A–Z is the default discovery model; case is a filter / browse view / deep-linked state and never an owner. Explains multi-complement, infinitive, clause, and multi-case lemmas. Wireframes replaced. | UX architecture §1, §1.0, §1.1, §3.1, §3.1a, §3.1b, §4.1a, §5.5, §6 (J1–J4), §7.1, §7.2, §11.1, §11.4, §12, §13, §15; summary §3 |
| **2** | Tighten card backlinks: audit the locked `contentRef` relation types and admit **only** `kind:"card"` + `purpose:"support"`; add a second gate on lemma-level meaning ambiguity; `contrast` refs never imply the card teaches or instantiates the pattern. | Audit §4.3 (new `kind`×`purpose` evidence); UX architecture §8.1, §8.1a, §8.3, §8.3a, §8.4, §15; plan §A6 |
| **3** | Make `routeTopic()` default-deny a **required** Phase 3B safety task, with explicit new-kind handling, unknown-kind deny, focus behaviour, nine regression tests, and a hard stop condition; added to the 3B acceptance gate and touch map. | Audit §2.3 (defect traced); plan §A4 row, new §A4a, slice 3B scope/stop/gate; summary §5 |
| **4** | Separate runtime **shape validation** from **release authorization** explicitly, and specify the test-only injection harness by which UI tests consume a fixture the shipping loader refuses. | Runtime contract §1.1, §4.5a, §5.2, §5.4, §7.3, §9; summary §4 |
| **5** | Phase 3D wording: split synthetic activity-mechanics prototyping (possible without approved Polish) from integration of real Priority 7 items (blocked on linguistic/product gates). Neither designed nor implemented. | Plan slice 3D → 3D-1 / 3D-2, sequencing rationale; summary §5 |

No amendment changed the recommendation to build a dedicated Verb Patterns surface inside the
Grammar category, the case-chip visual grammar, the activity strategy, the no-persistence position,
or the runtime boundary itself.

## 9. What this phase does not claim

No linguistic fact in the Priority 7 corpus is approved, native-reviewed or release-ready by this
work. The 28 / 12 / 5 provisional classification from Phase 2C.2 remains engineering planning
context, not a release state. Phase 3B is not implemented and is not authorized by this report.
