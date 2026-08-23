# Priority 8 Phase 4B4 — Batch 04 authoring

## Correction addendum (product-quality review)

Independent review of the original authoring (commit
`823ee376c258bb8e4d4183c3e577d60291ab14dd`) approved the full 41/41 matrix
implementation and all structural/guard work, but required two product-quality
corrections, applied in a separate follow-up commit without touching the
matrix, the guard registry, the progress test, or any complement/key:

1. **Teaching status of the 12 `do` + Genitive correspondence patterns.**
   The original blanket `recognition-only` classification is corrected below
   (§"CEFR / teaching-status decisions"). It is contradicted by existing
   product content, which already drills active production of `do` +
   Genitive correspondence (`data-verbs.js` drill `verbs-future-tense-005`,
   type `"build"`, target "Napiszę do ciebie wieczorem."). Each `do` +
   Genitive pattern's `cefr` and `teachingStatus` were mirrored exactly from
   its Dative-mode sibling in the same content family, mechanically, per
   lemma. Result: **41 active-production, 0 recognition-only** (up from
   29/12) — derived by direct inspection of the sibling records, not forced.
2. **Ten example/translation corrections** (§"Example provenance" and the
   per-lemma table below), covering four ambiguous interrogative-clause
   translations, two Dative `że`-clause translations using a marked "write
   my friend that…" construction, two Dative direct-speech translations with
   the same "write my friend:" awkwardness, and the `brać`/`wziąć`
   optional-Instrumental examples (one contrived, one carrying a
   slash-alternative English translation). Complements, candidate keys, and
   meaning/pattern/example cardinality are byte-identical to the original
   commit for all 41 patterns — verified programmatically.

English-string uniqueness across Batch 4 is **no longer presented as a
product-quality goal**: four distinct English translations are each shared
by a sibling pair (Dative vs. `do`+Genitive), so 8 of the 41 example records
participate in English duplication. This is intentional — natural
translation quality outranks an artificial uniqueness constraint. All 41
Polish sentences remain pairwise unique. The Batch 4 content digest changed
accordingly; see below.

## Scope and starting endpoint

This is an **implementation** task against an already-reviewed and frozen
linguistic schema matrix. No Phase 3 evidence was reinterpreted, no new
linguistic research was performed, and the schema matrix itself was not
redesigned.

Starting endpoint (verified before any edit):

- branch `priority-8-phase-4b-editorial-authoring`
- HEAD `7d4ed2a11d7217c6d38fc1b975c89900c825cadd`
- tree `aa42acebf560e2a209f4191491bfa99c6b03502f`
- clean working tree, zero remotes, `push.default=nothing`, executable
  blocking pre-push hook
- staging SHA-256 before authoring:
  `bf0870600768586d7faba6244a5799ae5e91e61373c214eca56f9099ec6c53b1`

Binding authoring plan: `reports/priority-8-phase-4b4-schema-matrix.md`,
recorded SHA-256 before editing and reverified unchanged after authoring:
`6e63c9d2628d9237e7b5851c29e55975734440878dac7491873f9368291f3781`.

## Matrix 13/41 reconciliation

The frozen matrix declares, and this authoring implements exactly:

- 9 full-pattern lemmas: `dawać`, `dać`, `brać`, `wziąć`, `czytać`, `pisać`,
  `napisać`, `spotykać się`, `spotkać się` (order 37 `przeczytać` remains
  metadata-only, no `candidateContent`).
- 13 meanings: `dawać` 1, `dać` 1, `brać` 2, `wziąć` 2, `czytać` 1, `pisać` 2,
  `napisać` 2, `spotykać się` 1, `spotkać się` 1.
- 41 schema alternatives: `dawać` 1, `dać` 1, `brać` 3, `wziąć` 3, `czytać` 5,
  `pisać` 13 (1 creation + 12 correspondence), `napisać` 13 (1 creation + 12
  correspondence), `spotykać się` 1, `spotkać się` 1. 1+1+3+3+5+13+13+1+1 = 41.
- 41 examples, one primary example per pattern.
- 0 HOLD rows.

## Per-lemma meaning/pattern/example counts

| Lemma | Meanings | Patterns | Examples | active-production | recognition-only |
|---|---:|---:|---:|---:|---:|
| `dawać` | 1 | 1 | 1 | 1 | 0 |
| `dać` | 1 | 1 | 1 | 1 | 0 |
| `brać` | 2 | 3 | 3 | 3 | 0 |
| `wziąć` | 2 | 3 | 3 | 3 | 0 |
| `czytać` | 1 | 5 | 5 | 5 | 0 |
| `pisać` | 2 | 13 | 13 | 13 | 0 |
| `napisać` | 2 | 13 | 13 | 13 | 0 |
| `spotykać się` | 1 | 1 | 1 | 1 | 0 |
| `spotkać się` | 1 | 1 | 1 | 1 | 0 |
| **Total** | **13** | **41** | **41** | **41** | **0** |

**Corrected** (see addendum): `pisać`/`napisać`'s `do` + Genitive recipient
mode (Mode B, 6 alternatives each) is `active-production`, mirroring its
Dative sibling's `cefr`/`teachingStatus` exactly, content family by content
family — not classified by recipient mode. `teachingStatus` and `cefr` now
follow content-family complexity only: `accusative-content`/`topic` are
core/A1-A2, clause alternatives (`że`, `żeby`, interrogative, direct speech)
are common/A2-B1, identically in both recipient modes.

## Candidate keys

Every `candidateMeaningKey` and `candidatePatternKey` is used **verbatim**
from the frozen matrix's `meaningKeyProposal` / `schemaKeyProposal` columns —
none renamed, none decorated with batch numbers, verification orders, or
source wording. No production ID was allocated anywhere.

## CEFR / teaching-status decisions

- Basic one-complement or two-required-complement constructions (`dawać`,
  `dać`, `brać`/`wziąć` literal A1/A2, participation, `spotykać się`/
  `spotkać się`, `czytać` alt 1, `pisać`/`napisać` creation and both modes'
  `accusative-content`): CEFR A1/A1 or A2/A2, `active-production`, `core`
  priority.
- Clause-based alternatives (`że`, `żeby`, interrogative-dependent, direct
  speech) on `czytać` and on **both** `pisać`/`napisać` recipient modes: CEFR
  A2/B1 or A2/A2, `active-production`, `common` priority.
- **Corrected:** `pisać`/`napisać`'s `do` + Genitive mode is no longer a
  separate, uniformly `recognition-only` tier. Each `do`+Genitive pattern's
  `cefr` and `teachingStatus` were mirrored mechanically from its exact
  Dative-mode sibling (same content family), so both recipient modes now
  carry identical pedagogical treatment content-family by content-family.
  `usage` was left untouched — `priority: common`/`core` was already
  consistent with `active-production` and contained no textual claim of
  peripherality that needed removing.

## Example provenance

- 41 examples authored, all `candidateOrigin.kind = "editorial-generated"`.
- **Repository-reuse count: 0.** A targeted search was performed against
  `editorial/verb-pattern-candidates.json` and the `data-*.js` product corpora
  (via `priority7_tooling.repository_index_from_root`) for existing Polish
  sentences realizing any of the 41 target schemas (transfer, taking,
  participation, reading, correspondence, meeting vocabulary). No exact,
  schema-faithful match was found, so reuse was not forced, per the task's
  "reuse is optional" instruction.
- **Editorial-generated count: 41** (unchanged after the correction).
- **Quiet-reuse scan (historical-lock / index method):** every generated
  Polish sentence — including the 10 corrected in this pass — was checked
  against `priority7_tooling.repository_index_from_root`'s entity index
  (1665 entities sourced from `data-*.js`: 1215 `card`, 353 `drill`, 89
  `topic`, 8 `scenario`) for a verbatim match in the fields the historical
  lock actually reads, `card.pl`/`card.ex`/`drill.prompt`/`drill.answer`.
  Zero matches. This method does **not** reach nested grammar-deck example
  arrays (e.g. `data-verbs.js`'s `examples[].pl`), which are outside `card`/
  `drill` record shape.
- **Supplemental raw-text scan (broader, authoring-time only, not part of the
  automated historical lock):** all 10 corrected Polish sentences were also
  grepped verbatim against the full text of every `.js` file, every
  `editorial/*.json` file, and every `reports/*` file in the repository
  (187 files, ~8.2 MB), excluding the staging file and Batch 4's own reports.
  Zero matches. This scan is broader than the index method (it reaches the
  grammar-deck text) but is a one-time authoring-time check, not a
  test-suite-enforced guarantee.
- All 41 Polish strings are pairwise unique across Batch 4. English
  translations are **not** required to be unique: four distinct English
  translations are each shared by a Dative/`do`+Genitive sibling pair (the
  interrogative-clause and direct-speech alternatives, for both `pisać` and
  `napisać`), so 8 of the 41 example records participate in English
  duplication. This is intentional — natural translation quality takes
  priority over global English string uniqueness — see the correction
  addendum.

## Live rules added (same commit)

Fourteen new declarative guard rules were added to
`tests/fixtures/priority8_phase4b_authoring_rules.json` (registry grew from 8
to 22 rules; no existing rule was modified):

1. `p8-4b-dawac-exact-pattern-shapes`
2. `p8-4b-dac-exact-pattern-shapes`
3. `p8-4b-brac-exact-pattern-shapes`
4. `p8-4b-brac-participation-explanation-material`
5. `p8-4b-wziac-exact-pattern-shapes`
6. `p8-4b-wziac-participation-explanation-material`
7. `p8-4b-czytac-exact-pattern-shapes`
8. `p8-4b-czytac-authorized-o-locative-topic-signatures`
9. `p8-4b-pisac-exact-pattern-shapes`
10. `p8-4b-napisac-exact-pattern-shapes`
11. `p8-4b-spotykac-sie-lexical-identity`
12. `p8-4b-spotykac-sie-exact-pattern-shapes`
13. `p8-4b-spotkac-sie-lexical-identity`
14. `p8-4b-spotkac-sie-exact-pattern-shapes`

Rule 8 allowlists **both** authorized `o+locative` topic signatures
(`required=true` for `czytać`'s row 2 dedicated topic alternative,
`required=false` for rows 3–4's optional topic participant), per the
corrected Phase 4B4-A guard plan. The guard interpreter and its test file
(`tests/test_priority8_phase4b_authoring_guards.py`) were not modified — only
the declarative rule data was extended, using existing primitives.

Twelve in-memory mutation proofs (A–L, covering `dawać`, `brać` twice,
`wziąć`, `czytać` (unauthorized-pattern rejection plus both authorized
signatures passing), `pisać` twice, `napisać` twice, and both meeting-verb
lexical-identity checks) were run against copies of the data before
committing; every mutation was caught by its intended rule, and no
repository file was touched by the mutation testing itself. See the risk
review for the full mutation matrix.

## Batch 4 content digest

Digest projection fields: `verificationOrder`, `canonicalLemma`, `aspect`,
`phase3Disposition`, `phase3Evidence`, `bindingConstraints`,
`candidateContent`, `metadataAspectPartner` (present only for `czytać`),
`requiredLexicalItems` (present only for `brać`/`wziąć`) — the same
projection and canonical-JSON serialization discipline used by the Batch
1/2/3 historical locks.

**Batch 4 digest (corrected):**
`7f8fd8840d7aadeffbd23a5047cf8ce200b07c84c41520835a11f575c698b4f2`

(Original, pre-correction digest:
`06fa454bb7888b5bf4cb4a904add75cb68adba591d6ead11eb916f92faefcf6c` — superseded
because `cefr`, `teachingStatus`, and 10 examples' `pl`/`en`/
`learnerExplanationEn` changed. B1/B2/B3 digests are unaffected and remain
`3849e0082e59e0984e7082c35e5b492eb3a228706aab2a7323575a5a9f9e619e`,
`dd55047bbd7db3d28224d6366015c7353479206e4ffba64cf8b6397efb8d8db8`, and
`8276864944181e47b573767151e98b556b52037b7920335d32fb510aeee58edb`
respectively.)

Pinned in `tests/test_priority8_phase4b4_batch04.py`.

## Cumulative staging state after Batch 4

- `phaseStep`: `4B4`
- `stagingRevision`: `5`
- 39 authored full-pattern lemmas (30 from Batches 1–3 + 9 from Batch 4)
- 51 meanings (38 + 13)
- 124 patterns (83 + 41)
- 124 examples (83 + 41)
- 29 future-empty full-pattern records (38 − 9)
- all 68 staging records remain `stagingReviewStatus: draft`

## Tests

- `python3 validate_priority8_staging.py` → `PASS: Priority 8 4B4 staging
  revision 5 is read-only valid (68 lemmas, 21 constrained records, 12 global
  constraints).`
- The eight scoped Phase 4B suites (`test_priority8_phase4b0_staging`,
  `test_priority8_phase4b1a_authoring_schema`, `test_priority8_phase4b1_batch01`,
  `test_priority8_phase4b2_batch02`, `test_priority8_phase4b3_batch03`,
  `test_priority8_phase4b4_batch04` (new), `test_priority8_phase4b_progress`,
  `test_priority8_phase4b_authoring_guards`) run together: **190 tests, all
  passing** (167 pre-existing + 23 new in the Batch 4 historical lock).
- `git diff --check` — clean.

No schema interpretation was performed during authoring: the approved Phase
4B4-A matrix was implemented exactly as frozen, and the matrix file itself
was not modified (SHA-256 unchanged, reverified above).
