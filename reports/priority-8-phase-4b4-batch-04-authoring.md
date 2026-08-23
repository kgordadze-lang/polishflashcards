# Priority 8 Phase 4B4 — Batch 04 authoring

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
| `pisać` | 2 | 13 | 13 | 7 | 6 |
| `napisać` | 2 | 13 | 13 | 7 | 6 |
| `spotykać się` | 1 | 1 | 1 | 1 | 0 |
| `spotkać się` | 1 | 1 | 1 | 1 | 0 |
| **Total** | **13** | **41** | **41** | **29** | **12** |

For `pisać`/`napisać`, the Dative recipient mode (Mode A, 6 alternatives each)
is `active-production`; the `do` + Genitive recipient mode (Mode B, 6
alternatives each) is `recognition-only`, reflecting that `do` + Genitive
addressing is materially less central for active learner production than the
modern default Dative recipient, while remaining fully declared and
structurally guarded either way. See the risk review for the full rationale.

## Candidate keys

Every `candidateMeaningKey` and `candidatePatternKey` is used **verbatim**
from the frozen matrix's `meaningKeyProposal` / `schemaKeyProposal` columns —
none renamed, none decorated with batch numbers, verification orders, or
source wording. No production ID was allocated anywhere.

## CEFR / teaching-status decisions

- Basic one-complement or two-required-complement constructions (`dawać`,
  `dać`, `brać`/`wziąć` literal A1/A2, participation, `spotykać się`/
  `spotkać się`, `czytać` alt 1, `pisać`/`napisać` creation and
  `dative-accusative-content`): CEFR A1/A1 or A2/A2, `active-production`,
  `core` priority.
- Clause-based alternatives (`że`, `żeby`, interrogative-dependent, direct
  speech) on `czytać` and `pisać`/`napisać` Mode A: CEFR A2/B1 or A2/A2,
  `active-production`, `common` priority.
- `pisać`/`napisać` Mode B (`do` + Genitive) alternatives: CEFR B1 recognition
  only (no `production` field), `recognition-only`, `common` priority.

## Example provenance

- 41 examples authored, all `candidateOrigin.kind = "editorial-generated"`.
- **Repository-reuse count: 0.** A targeted search was performed against
  `editorial/verb-pattern-candidates.json` and the `data-*.js` product corpora
  (via `priority7_tooling.repository_index_from_root`) for existing Polish
  sentences realizing any of the 41 target schemas (transfer, taking,
  participation, reading, correspondence, meeting vocabulary). No exact,
  schema-faithful match was found, so reuse was not forced, per the task's
  "reuse is optional" instruction.
- **Editorial-generated count: 41.**
- **Quiet-reuse scan:** every one of the 41 generated Polish sentences was
  checked against the full repository entity index (1665 entities from
  `data-*.js`) for a verbatim match in any `card.pl`/`card.ex`/`drill.prompt`/
  `drill.answer` field. Zero matches — no generated sentence already exists
  verbatim elsewhere in the repository under a different classification.
- All 41 Polish strings and all 41 English strings are pairwise unique across
  Batch 4 (verified programmatically).

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

**Batch 4 digest:**
`06fa454bb7888b5bf4cb4a904add75cb68adba591d6ead11eb916f92faefcf6c`

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
