# Priority 8 Phase 4C4A — editorial packaging bridge and governance preparation

This phase makes the independently verified Phase 4C3 records legible to the
repository's own governance machinery. It authors no semantics, grants no
product approval, freezes nothing and projects nothing to production.

## 1. Human adjudication

Phase 4C4 stopped at the human-authority gate. The three decisions returned as:

| Decision | Outcome | What this phase did with it |
|---|---|---|
| **HD-4C4-01** | **NOT YET APPROVED** | No product-approval event exists. No pattern is `approved`. No `releaseAuthorization`. No freeze. |
| **HD-4C4-02** | **APPROVED** | The deterministic packaging bridge appended the 68 records to the editorial corpus. Phase 4C3 semantics were not reopened. |
| **HD-4C4-03** | **APPROVED** | Four nonhuman Priority 8 actors registered, each tied to committed workflow evidence. No AI work is described as human review. |

## 2. Starting endpoint

| Check | Observed |
|---|---|
| Branch | `priority-8-phase-4c-architecture` |
| HEAD | `816176f591909d505549e2818d6b8d6d75c67f25` |
| Tree | `cfa888243677ff5c2510672f67d1a00d719240e7` |
| Worktree / remotes / `push.default` / pre-push | clean / 0 / `nothing` / executable fail-closed |
| Canonical candidates SHA-256 | `c54e611d…5bfa7e9` |
| Stable-ID map SHA-256 | `20fc8a56…b6487a9d` |
| Candidate freeze digest | `0d636b3c…2f33be27` |
| Staging validator | PASS |
| Fifteen governed suites | **392 passed** |

## 3. Packaging correction

Phase 4C0 §15.2/§18.1/§25 require the 68 to be **added** to
`editorial/verb-pattern-candidates.json`. Phase 4C3 instead wrote a
runtime-shaped private artifact and left that corpus at 30 lemmas, so
`freeze_editorial` had nothing to operate on. Phase 4C4A closes that gap.

`priority8_phase4c4a_editorial_bridge.py` is verify-only by default, writes only
under `--write`, performs two independent builds and requires byte-identical
output. It is idempotent: the baseline is always the corpus with any previously
packaged Priority 8 lemma removed, so re-running rebuilds rather than appending a
second copy. Three consecutive `--write` runs produce identical bytes for all
four outputs.

The measured effect on `validate_editorial`:

| Document | Issues |
|---|---:|
| Released 30 + the 68, before packaging | **3,292** |
| Released 30 + the 68, after packaging | **0** |

## 4. Semantic immutability

Nothing semantic moved. Verified field-by-field against the Phase 4C3 artifact:

| Invariant | Result |
|---|---|
| Lemmas / meanings / patterns / examples | 68 / 95 / 224 / 224 |
| Stable IDs | 611, all unique, equal to the private map |
| `relationType`, `complements`, `cefr`, `teachingStatus`, `usage`, `learnerExplanationEn`, `activityEligibility` | 0 drift rows |
| `requiredLexicalItems` | 2 patterns, unchanged |
| Example `id` / `pl` / `en` | byte-identical |
| Teaching split | 222 active-production / 2 recognition-only |
| `source` complements / preserved family targets | 7 / 6 |
| Direct-speech patterns | 11 |
| Deferral ledger | 10, unchanged |
| Metadata-only identities | `zaczynać`, `przeczytać` absent; zero partner arrays |
| Editorial universe | **98 lemmas** (30 released + 68 new) |

The released 30 lemma records are byte-identical to `HEAD`.

## 5. Editorial-shape reconstruction

Three dimensions Phase 4C3 kept outside its canonical core were recovered
one-to-one from committed artifacts, never invented:

| Field | Source | Result |
|---|---|---|
| `key` (543) | frozen candidate identity layer | exact set equality with the freeze manifest |
| `internalScope` (95) | retained `governance.meaningScopes` | exact equality |
| `origin` (224) | retained `governance.exampleOrigins` | 220 editorial-generated + 4 repository-reuse |

The 4 repository-reuse origins keep their exact `repositorySource` card
references, which re-resolve through the repository index. The 220
editorial-generated origins gain `generatorRef` and `adoptedAt`, both required
by the schema.

## 6. Evidence construction

Each of the 224 patterns carries exactly one evidence record. Phase 3 verified
each lemma against one exact WSJP PAN sense, so the support is **sense-level and
shared across a lemma's patterns**. It is recorded at that granularity rather
than inflated into per-pattern source work nobody performed.

| Field | Value |
|---|---|
| `sourceId` | `wsjp-pan` (224/224) |
| `sourceKind` | `contemporary-reference` |
| `locator` | register URL + Phase 3 sense locator + the Phase 3 source key |
| `factType` | `complement-frame` ×223, `meaning` ×1 |
| `checkedAt` | `2026-08-20` ×123, `2026-08-21` ×101 |

## 7. `sourceId` mapping

Phase 3 keys such as `WSJP-BRAC-01` are **sense locators, not source
identities**. All 68 distinct keys resolve through the committed
`reports/priority-8-phase-3-source-register.md` to the single registered source
`wsjp-pan`. No source ID is synthesised from a title, filename or key; a test
asserts no `sourceId` ever matches `^WSJP-`. Every `sourceId` resolves in
`sourceRegistry` and its `sourceKind` agrees with the registry.

## 8. `checkedAt` grounding

Every `checkedAt` is the **Accessed** date recorded in the committed Phase 3
source register for that pattern's own primary source. Each record's locator
embeds its Phase 3 source key, so a test re-derives the expected date from the
register and requires exact equality — the grounding is mechanically re-checked,
not asserted in prose.

No current date, commit time, file mtime or execution time is used anywhere. The
only two dates present are `2026-08-20` and `2026-08-21`, and a test asserts
today's date is not among them.

`adoptedAt` on the 220 generated origins is `2026-08-25`, the date written into
the Phase 4B batch reports as the "Final reconciliation correction note", at
which the live example wording reached the state Phase 4C3 promoted verbatim.

## 9. Pattern-evidence granularity and `odpowiadać`

`odpowiadać/answering-by-speech/direct-speech` is the one row Phase 4C3 marked
`policy-authorized-direct-speech`. Its frozen Phase 3 binding constraint names
only the `na`-question and `że`-content schemas; direct speech is a Phase 3B
global-constraint policy addition adjudicated at Phase 4C0 §9.5.

Its evidence record therefore uses `factType: meaning` — sense-level support
only — with a note stating the policy basis. It does **not** claim
`complement-frame` support, because that would cite a Składnia row that does not
license the frame. It is the only one of the 11 direct-speech patterns recorded
this way, and tests assert both halves of that.

`meaning` is a member of `REFERENCE_PATTERN_FACT_TYPES`, so the tier-1
acceptance stands honestly on sense-level support.

## 10. Nonhuman actor registration

Four actors added, each `human: false`, each holding exactly one role, each
`namedInPhase: "Priority 8 Phase 4C4A"`:

| Actor | Role | Committed workflow evidence |
|---|---|---|
| `priority8-reference-analysis` | `reference-verification` | Phase 3 source verification; seven batch CSVs + the source register |
| `priority8-editorial-review` | `editorial-review` | Phase 4B authoring + final semantic reconciliation |
| `priority8-editorial-corroboration` | `editorial-review` | Phase 4B mechanical reconciliation audit + seven batch risk reviews |
| `priority8-example-generation` | `example-generation` | Phase 4B example authoring |

The reference actor is distinct from both editorial actors, satisfying
`REVIEW_ACTOR_INDEPENDENCE` structurally. All four Priority 7 actors are
byte-identical. `reviewerRegistry` and `authorRegistry` are unchanged; no human
identity was added and `authorRegistry` stays empty. The context notice is
appended, never rewritten, and re-running the bridge does not append it twice.

## 11. Review-event chain and derived state

Each pattern carries exactly two events, in order:

1. `reference-verification` / `accept` — `actorRef: priority8-reference-analysis`,
   `reviewedAt` = that pattern's own source access date, pinning its evidence digest.
2. `editorial-review` / `accept` — `actorRef: priority8-editorial-review`,
   `corroboratingActorRefs: [priority8-editorial-corroboration]`,
   `reviewedAt: 2026-08-25`.

Dates are nondecreasing. Every `scopeDigest` is recomputed from the finished
record, so the scope each event claims is the scope that exists. `releaseMode` is
`solo-maintainer-reference-backed` on all 224.

**Derived state: `editorial-reviewed` on all 224.** `reviewState` is not
hardcoded — the bridge computes it through `_derive_review_currency`, and a test
re-derives it independently and requires equality.

## 12. Product approval — absent

- Zero `product-approval` events on the 224.
- Zero patterns in state `approved`.
- Zero `reviewerRef` fields on any new event; every stage is nonhuman.
- The released 45 remain the only approved patterns in the corpus.

## 13. Release authorization — absent

No `releaseAuthorization`, no `allocations`, no identity/structure/wording/policy
snapshot, no `reviewHistory`, no `runtimeProjection`. `freeze_editorial` was not
invoked. `allocationRegistry` remains `{}`. `tombstones` remains `[]`.

## 14. Audio authorization boundary

`AUDIO_NOT_AUTHORIZED` gates `audioEligible: true` on an **approved** owning
pattern. The repository's own precedent is exact: the released 45 carried
`audioEligible: false` until Priority 8 Phase 1A flipped them under explicit
owner authorization (commit `9f8968e`).

Phase 4C4A therefore packages all 224 new examples `audioEligible: false`, and a
test proves the validator refuses `true` here. The Phase 4C3 promotion policy is
preserved, not discarded: every review-manifest row records
`audioEligibleAtPackaging: false` alongside `audioEligibleIfApproved: true`, so
the 224 future pronunciation candidates remain explicit. The released 45 keep
their authorized `true`. This authorizes no Listening.

## 15. Activity eligibility

`activityEligibility: []` on all 224. No activity authority was created or implied.

## 16. Editorial validation

`validate_editorial` on the packaged 98-lemma corpus: **0 issues**.

Zero remaining mechanical missing-field issues for `key`, `internalScope`,
`origin`, `evidence`, `reviewState` or `reviewEvents`.

One envelope change was required and is classified as
**EXPECTED — pre-existing defect corrected under the §18 envelope exception**:
the corpus `formatVersion` moved 1 → 2. Phase 4C2 moved the contract and the
public runtime to 2 but left this private corpus at 1, so it has failed
`validate_editorial` with exactly one `FORMAT_VERSION` issue since that phase. A
test pins the baseline's single-issue state so the correction is auditable. No
record of the released 30 changed.

## 17. Human-review package

| Artifact | Purpose |
|---|---|
| `editorial/priority-8-phase4c4a-review-manifest.json` | binds the exact reviewed set: 224 rows, Phase 4C3 SHA, stable-map SHA, freeze digest, packaged-corpus digest, preview digest |
| `editorial/priority-8-phase4c4a-review-preview.json` | private runtime-shaped preview of the pending 68 lemmas; passes `validate_runtime` with 0 issues |
| `--review-sheet PATH` | regenerates a self-contained offline HTML sheet driven by the real shipping `pp-verb-patterns.js` |

The review surface is the existing one, not a new UI: the sheet inlines the
shipping loader and renders every row through it. Verified through the
repository's own JXA harness — the loader accepts the preview and reports 68
lemmas / 224 patterns, with the three architecture-approved renderings live:

- `brać udział + w czym?` and `wziąć udział + w czym?` (HD-4C-02);
- 11 direct-speech chips rendering `„…”`;
- 7 source rows reading **"where it comes from"**, with `od kogo?` / `u kogo?`
  on the three person-origin rows (HD-4C-01).

Zero patterns render any activity eligibility and zero examples render an audio
control. The sheet is deliberately generated on demand rather than committed:
`editorial/` and `reports/` contain no HTML today, and a private page inside the
deployable tree could be served by the static host.

The manifest records `productApproved: false`, `releaseAuthorized: false`,
`reviewState: awaiting-human-product-review`.

## 18. Frozen-input immutability

Byte-identical at the endpoint: the Phase 4C3 canonical candidates
(`c54e611d…`), the stable-ID map (`20fc8a56…`), the candidate-key freeze
manifest, and Phase 4B staging.

Untouched: `content/verb-patterns.json` (30/34/45/45, `formatVersion 2`,
`patternDataRevision 2`), `pp-verb-patterns.js`, `priority7_tooling.py`,
`validate_priority8_staging.py`, `index.html`, `sw.js`, `audio/`,
`audio-manifest.json`, migration tooling and activities.

The strongest runtime-isolation proof: `project_runtime_nonrelease` over the
packaged corpus still yields **exactly the released 45 patterns across 30
lemmas**, byte-equal to `content/verb-patterns.json`, because the projection
admits approved patterns only. Packaging granted no runtime exposure.

## 19. Tests

| Gate | Result |
|---|---|
| `python3 validate_priority8_staging.py` | PASS |
| Fifteen existing governed suites | 392 passed |
| Dedicated Phase 4C4A suite | **91 passed** |
| Combined sixteen suites | **483 passed** |

The dedicated suite covers packaging fidelity, key/scope/origin reconstruction,
evidence truthfulness, actor registry, the review chain, derived state, the
absence of approval and authorization, the audio and eligibility boundaries,
editorial validation, determinism, the human-review package, runtime isolation,
and 21 adversarial rejections — unregistered `sourceId`, future or missing
`checkedAt`, removed evidence, unknown reviewer, a nonhuman actor placed in a
human `reviewerRef`, an inserted product approval, `approved` without approval, a
self-corroborating actor, dropped corroboration, one actor performing both
nonhuman tiers, a stale scope digest, tampered evidence, changed stable ID,
renamed candidate key, role regression, removed `requiredLexicalItems`,
metadata-only promotion, and manifest omission/addition.

### 19.1 Superseded Priority 7 historical locks — needs a decision

**30 Priority 7 tests that passed at `HEAD` now fail.** They are reported here
rather than edited, because Phase 4C0 §23 forbids a Phase 4C subphase editing a
historical lock and the authorized changed-path set does not include them.

Every one is the same structural class: a **whole-corpus or whole-registry global
assertion** written when the editorial corpus held only Priority 7 content —
"the corpus has exactly 30 lemmas", "exactly one actor carries a review-stage
role", "all 45 patterns are reference-verified". Examples:

- `test_priority7_phase4fi1.py::StartingCheckpointTests::test_the_approved_corpus_is_30_34_45_45_and_all_approved` → `30 != 98`
- `test_priority7_phase4fa.py::NonhumanReferenceActor::test_exactly_one_actor_is_registered_and_it_is_nonhuman` → the three Priority 8 review actors

The collision is **inherent to HD-4C4-02**: any correct implementation of the
Phase 4C0-mandated append breaks these same locks. It is not caused by how the
packaging was done.

Context for the decision: these suites are already substantially failing at
`HEAD` in this working copy (for example `test_priority7_phase4fa` 23 failed / 51
passed, `test_priority7_phase4fi1` 53 failed / 43 passed **before** this phase);
they are not the operative governed baseline, which is the fifteen Priority 8
suites at 392. This phase adds 30 failures on top of a pre-existing 519.

Two candidate resolutions, for Phase 4C4B or a dedicated subphase:

1. **Narrow each lock to Priority 7 scope**, following the Phase 4C2 precedent
   in which Phase 4C1's whole-file hash lock was replaced by one stricter about
   the invariant it actually owned. Preferred: it preserves each test's real
   intent.
2. **Give Priority 8 its own editorial corpus**, which contradicts Phase 4C0
   §5.1/§15.2 and would reopen the packaging decision.

`test_priority8_phase4c3_canonical_projection.py::test_46_no_unexpected_changed_paths_exist`
also fails while this phase's work is uncommitted; it asserts the working tree
carries no path outside Phase 4C3's own set and passes again once the tree is
clean. No edit is needed for it.

## 20. Phase 4C4B entry instructions

Phase 4C4B is the human product review and, if the owner approves, the recording
of that decision.

1. Regenerate the review sheet:
   `python3 priority8_phase4c4a_editorial_bridge.py --review-sheet <path>`
   and confirm its digest against `reviewPreviewDigest` in the manifest.
2. The owner inspects all 224 patterns and returns an explicit decision. AI
   agreement is not approval.
3. On approval, and only then:
   - append one `product-approval` event per pattern, `reviewerRef: product-owner-001`,
     `reviewedAt` = the real review date, bound to each pattern's freshly
     recomputed tier-3 scope digest — never a stale digest;
   - `product-owner-001` already acknowledges `solo-maintainer-reference-backed`,
     which `OWNER_RELEASE_MODE_NOT_ACKNOWLEDGED` requires;
   - `reviewState` becomes `approved` **by derivation**, never by assertion;
   - `audioEligible` may then move to `true` on the 224 examples, which is
     pronunciation playback only and still authorizes no Listening;
   - `activityEligibility` stays `[]`.
4. Resolve §19.1 before or alongside 4C4B.
5. Structure freeze, `allocationRegistry` persistence and `releaseAuthorization`
   remain Phase 4C4C. Runtime projection remains Phase 4C5/4D.

**EDITORIAL PACKAGE COMPLETE — NONHUMAN REVIEW TIERS GROUNDED — AWAITING HUMAN PRODUCT APPROVAL**
