# Priority 8 Phase 4B5 — Batch 05 authoring

## Scope and starting endpoint

This is an **implementation** task against an already independently-reviewed
and frozen linguistic schema matrix. No Phase 3 evidence was reinterpreted,
no new linguistic research was performed, and the schema matrix itself was
not modified.

Starting endpoint (verified before any edit):

- branch `priority-8-phase-4b-editorial-authoring`
- HEAD `dc3acf75d37f1c91f7fb8bda99f0408d09c1ef71`
- tree `596a726e1f21c97d37aa2b70dae9e4db4dea4393`
- clean working tree, zero remotes, `push.default=nothing`, executable
  blocking pre-push hook
- staging SHA-256 before authoring:
  `0f26b17238ec1abe984145fd7a6c232419465a5baec1f59a3a14e23d93295f8c`
- guard registry SHA-256 before authoring:
  `3caab1419f14718ed7c82b5fea4eb5fac3326160864c88decd88ca13b6277db0`

Binding authoring plan: `reports/priority-8-phase-4b5-schema-matrix.md`
(commit `dc3acf75d37f1c91f7fb8bda99f0408d09c1ef71`, subject "Priority 8 Phase
4B5 author schema matrix"), independently reviewed and approved. SHA-256
recorded before editing and reverified unchanged after authoring:
`9f2de2eda2cb051d47ec13f4eaadc45ba617f55b5c8871588db61e8b79641ad7`.

## Matrix 15/40 reconciliation

The frozen matrix declares, and this authoring implements exactly:

- 10 full-pattern lemmas: `oglądać`, `obejrzeć`, `skończyć`, `chcieć`,
  `robić`, `rozumieć`, `mieszkać`, `umówić się`, `dzwonić`, `powiedzieć`.
- 15 meanings: `oglądać` 1, `obejrzeć` 1, `skończyć` 2, `chcieć` 2, `robić`
  2, `rozumieć` 2, `mieszkać` 1, `umówić się` 2, `dzwonić` 1, `powiedzieć` 1.
  1+1+2+2+2+2+1+2+1+1 = 15.
- 40 schema alternatives: `oglądać` 1, `obejrzeć` 1, `skończyć` 3, `chcieć`
  6, `robić` 2, `rozumieć` 4, `mieszkać` 1, `umówić się` 7 (2 appointment +
  5 agreement), `dzwonić` 4, `powiedzieć` 11.
  1+1+3+6+2+4+1+7+4+11 = 40.
- 40 examples, one primary example per pattern.
- 0 unresolved HOLD rows in the frozen matrix (both original `umówić się`
  HOLDs were adjudicated before the matrix was committed).

A programmatic pass parsed all 40 schema rows directly out of the matrix
markdown (meaning key, pattern key, and the exact required/optional
complement list per row) and diffed them against the authored
`candidateContent`: **40/40 matched exactly, 0 missing, 0 extra.**

## Per-lemma meaning/pattern/example counts

| Lemma | Meanings | Patterns | Examples | active-production | recognition-only |
|---|---:|---:|---:|---:|---:|
| `oglądać` | 1 | 1 | 1 | 1 | 0 |
| `obejrzeć` | 1 | 1 | 1 | 1 | 0 |
| `skończyć` | 2 | 3 | 3 | 3 | 0 |
| `chcieć` | 2 | 6 | 6 | 6 | 0 |
| `robić` | 2 | 2 | 2 | 2 | 0 |
| `rozumieć` | 2 | 4 | 4 | 4 | 0 |
| `mieszkać` | 1 | 1 | 1 | 1 | 0 |
| `umówić się` | 2 | 7 | 7 | 7 | 0 |
| `dzwonić` | 1 | 4 | 4 | 4 | 0 |
| `powiedzieć` | 1 | 11 | 11 | 11 | 0 |
| **Total** | **15** | **40** | **40** | **40** | **0** |

## Candidate keys

Every `candidateMeaningKey` and `candidatePatternKey` is used **verbatim**
from the frozen matrix's `meaningKeyProposal` / `schemaKeyProposal` columns —
none renamed, none decorated with batch numbers, verification orders, HOLD
history, or source wording. No production ID was allocated anywhere.

## CEFR / teaching-status decisions

Following the explicit lesson carried forward from the Phase 4B4 product-
quality correction, `teachingStatus` and `cefr` were assigned by
**content-family complexity and practical learner value**, never by surface
participant mode (e.g. never "Dative vs. `do`+Genitive" or "one preposition
vs. another" as the deciding factor):

- Basic one- or two-complement constructions with high everyday value
  (`oglądać`, `obejrzeć`, `skończyć`'s Accusative/infinitive alternatives,
  `chcieć`'s Genitive/infinitive/Accusative-request alternatives, both
  `robić` meanings, `rozumieć`'s Accusative alternatives, `mieszkać`,
  `umówić się`'s appointment alternatives and `na`/`o` agreement
  alternatives, `dzwonić`'s target realizations, `powiedzieć`'s Accusative-
  content and `o`+Locative-topic alternatives in both recipient modes): CEFR
  A1/A1 or A2/A2, `active-production`, `core`/`common` priority.
- Clause-based alternatives (`że`, `żeby`, interrogative-dependent) across
  `chcieć`, `rozumieć`, `umówić się` agreement, `dzwonić`, and both
  `powiedzieć` recipient modes: CEFR A2/B1 or A2/A2, `active-production`,
  `common` priority — matching the established clause-family CEFR
  convention already used across Batches 1–4.
- `skończyć`'s colloquial cessation sense (`z + Instrumental`) is A2/B1
  `active-production`/`common`: idiomatic and moderately marked, but a
  genuinely common, learner-useful expression, not withheld to an artificial
  recognition-only tier.

**Result: 40 active-production, 0 recognition-only.** No recognition-only
classification was needed for Batch 5; every construction was judged
practical enough for active production once assessed by its own content-
family complexity rather than by recipient mode, mirroring exactly the
corrected Batch 4 outcome (41 active-production / 0 recognition-only there
too, after the same content-family principle was applied).

`powiedzieć`'s two recipient modes (Dative, `do` + Genitive) carry
**identical** `cefr`/`teachingStatus` per content family — mirrored exactly,
not classified independently by mode, exactly as the Phase 4B4 correction
requires.

## Example provenance

- 40 examples authored, all `candidateOrigin.kind = "editorial-generated"`.
- **Repository-reuse count: 0.** A targeted search of
  `editorial/verb-pattern-candidates.json` and the `data-*.js` product
  corpora found no exact, schema-faithful match to reuse for any of the 40
  target schemas, so reuse was not forced.
- **Editorial-generated count: 40.**
- **Quiet-reuse scan, two layers, both run for every example:**
  1. *Historical-lock / index scan* — every generated Polish sentence
     checked via `priority7_tooling.repository_index_from_root` against the
     fields it actually indexes (`card.pl`, `card.ex`, `drill.prompt`,
     `drill.answer`; 1665 entities, 0 adapter issues). **0 collisions.**
     This scan does not reach nested grammar-deck example arrays.
  2. *Supplemental raw-text scan* (broader, authoring-time only, not
     enforced by any test) — verbatim grep of every `.js`,
     `editorial/*.json`, and `reports/*` file (190 files, ~8.3 MB),
     excluding the staging file and Batch 5's own reports.

  The supplemental scan **did** surface two genuine collisions on the first
  pass: "Chcę odpocząć." (verbatim in `data-verbs.js`'s modal-verb teaching
  deck) and "Chciałbym kawę." (verbatim in `data-grammar.js`'s conditional-
  mood teaching deck, in both a bolded prose line and a declension table
  row). Both occurrences live inside `teach[].examples[]`/`table[]` arrays
  with **no addressable `card` or `drill` id** — the same architectural gap
  already documented in the Phase 4B4 correction review (grammar-deck nested
  examples fall outside the `card`/`drill` record shape the locked
  `candidateOrigin.repositorySource` format requires). Since no valid
  repository-reuse citation was possible, both sentences were **rewritten**
  rather than misclassified: `chcieć`'s `infinitive-own-action` example
  became "Chcę zwiedzić Kraków." (I want to visit Krakow), and
  `polite-request-or-intention`'s `accusative-requested-object` example
  became "Chciałbym herbatę." (I would like a tea). Both replacements were
  re-scanned through both layers with zero further collisions.
- All 40 Polish strings are pairwise unique. One English-string duplicate
  exists by design, not distortion: `powiedzieć`'s Dative and `do`+Genitive
  `zeby-clause` alternatives both translate as "I told my friend to wait." —
  natural distinct-verb translations were found for the other four
  recipient-mode content families (`tell`/`say to` and `tell`/`mention to`
  pairs), but no equally natural distinct rendering exists for "tell someone
  to do X" without distorting the English, so the duplicate was accepted per
  the naturalness-first policy rather than forced apart.

## Live rules added (same commit)

Fourteen new declarative guard rules were added to
`tests/fixtures/priority8_phase4b_authoring_rules.json` (registry grew from
22 to 36 rules; no existing rule was modified):

1. `p8-4b-ogladac-exact-pattern-shapes`
2. `p8-4b-obejrzec-exact-pattern-shapes`
3. `p8-4b-skonczyc-exact-pattern-shapes`
4. `p8-4b-chciec-exact-pattern-shapes`
5. `p8-4b-robic-exact-pattern-shapes`
6. `p8-4b-rozumiec-exact-pattern-shapes`
7. `p8-4b-mieszkac-exact-pattern-shapes`
8. `p8-4b-mieszkac-authorized-preposition-cases`
9. `p8-4b-dzwonic-exact-pattern-shapes`
10. `p8-4b-dzwonic-authorized-preposition-cases`
11. `p8-4b-powiedziec-exact-pattern-shapes`
12. `p8-4b-umowic-sie-lexical-identity`
13. `p8-4b-umowic-sie-exact-pattern-shapes`
14. `p8-4b-umowic-sie-authorized-preposition-cases`

**`umówić się` guard scoping — stated explicitly per the matrix's own
instruction:** the allowlist rule (14) is **lemma-wide** — it blocks any
`preposition-case` signature outside the five legitimate ones actually used
across *both* meanings, but by itself cannot detect a structurally-
authorized signature placed under the *wrong* meaning. Meaning-specific
placement is enforced by the exact-pattern-shapes rule (13), which is
`exactMeaningSet`-scoped per meaning. The two rules are complementary, not
redundant. The guard interpreter itself was not modified — only the
declarative rule data was extended, using existing primitives.

**Twenty-three in-memory mutation proofs (A–W)** were run against copies of
the staged data before committing, covering every lemma and the explicit
cross-meaning bypass demonstration for `umówić się` (mutation M is caught by
the exact-shapes rule; the same mutation, checked against the allowlist rule
*alone*, is confirmed **not** caught — proving the allowlist is not itself
meaning-scoped, exactly as the independent matrix review required be stated
honestly). Every mutation was caught by its intended rule; no repository
file was touched by the mutation testing itself. See the risk review for
the full mutation matrix.

## Batch 5 content digest

Digest projection fields: `verificationOrder`, `canonicalLemma`, `aspect`,
`phase3Disposition`, `phase3Evidence`, `bindingConstraints`,
`candidateContent`, `metadataAspectPartner` (present on no Batch 5 lemma),
`requiredLexicalItems` (present on no Batch 5 lemma) — the same projection
and canonical-JSON serialization discipline used by the Batch 1–4 historical
locks.

**Batch 5 digest:**
`7c95810c26d99237995f138b58a9ae5ca07cd7431721cd619f1eb4f4622daf60`

B1–B4 digests independently recomputed and confirmed unchanged:
`3849e0082e59e0984e7082c35e5b492eb3a228706aab2a7323575a5a9f9e619e`,
`dd55047bbd7db3d28224d6366015c7353479206e4ffba64cf8b6397efb8d8db8`,
`8276864944181e47b573767151e98b556b52037b7920335d32fb510aeee58edb`,
`7f8fd8840d7aadeffbd23a5047cf8ce200b07c84c41520835a11f575c698b4f2`.

Pinned in `tests/test_priority8_phase4b5_batch05.py`.

## Cumulative staging state after Batch 5

- `phaseStep`: `4B5`
- `stagingRevision`: `6`
- 49 authored full-pattern lemmas (39 from Batches 1–4 + 10 from Batch 5)
- 66 meanings (51 + 15)
- 164 patterns (124 + 40)
- 164 examples (124 + 40)
- 19 future-empty full-pattern records (29 − 10)
- all 68 staging records remain `stagingReviewStatus: draft`

## Architecture-boundary facts documented, not resolved, by this authoring

- **`co do + Genitive`** (`umówić się` agreement sense): verified linguistic
  evidence, **architecture-deferred from Phase 4B** — the locked
  `preposition-case` schema accepts only a single lowercase Polish word
  (`PREPOSITION_RE`), so this genuine sixth agreement alternative receives
  zero product rows, is never encoded as `co` or `do` alone, and is never
  called rejected or unsupported. It remains a named Phase 4C backlog item
  in the frozen matrix (§19).
- **`KIEDY`** (`umówić się` appointment source schema 2): source-selected
  and required in the richer WSJP evidence, but has no documented concrete
  realization and is not a locked complement type. It is **not** represented
  as any complement, not folded into `do + Genitive`, and not given a new
  architecture type — an explicit, bounded lossy projection into the four-
  type model, also tracked in the matrix's Phase 4C backlog.

Neither fact was newly discovered here; both were already adjudicated in the
frozen matrix and are simply implemented faithfully — no schema, validator,
or `PREPOSITION_RE` change was made or proposed in this task.

## Tests

- `python3 validate_priority8_staging.py` → `PASS: Priority 8 4B5 staging
  revision 6 is read-only valid (68 lemmas, 21 constrained records, 12
  global constraints).`
- The nine scoped Phase 4B suites (`test_priority8_phase4b0_staging`,
  `test_priority8_phase4b1a_authoring_schema`, `test_priority8_phase4b1_batch01`,
  `test_priority8_phase4b2_batch02`, `test_priority8_phase4b3_batch03`,
  `test_priority8_phase4b4_batch04`, `test_priority8_phase4b5_batch05` (new),
  `test_priority8_phase4b_progress`, `test_priority8_phase4b_authoring_guards`)
  run together: **219 tests, all passing** (190 pre-existing + 29 new in the
  Batch 5 historical lock).
- `git diff --check` — clean.

No schema interpretation was performed during authoring: the approved Phase
4B5-A matrix was implemented exactly as frozen, and the matrix file itself
was not modified (SHA-256 unchanged, reverified above).
