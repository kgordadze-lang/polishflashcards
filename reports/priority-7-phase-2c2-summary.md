# Priority 7 — Phase 2C.2 Summary

**Provisional adjudication and cleanup. Not a native review, not an approval.**

## Purpose

Phase 2C.1 produced two independent blind AI reviews of the same 45-row Priority 7 native-review
sheet: Track A (GPT-5.6 Sol) and Track B (Claude Opus). Phase 2C.2 was permitted to compare the two
tracks and to use the supplied source-adjudication material, in order to consolidate the provisional
review into a stable low-risk research set, a sharply reduced human/teacher queue, a small set of
editorial example fixes, and a documented set of source-backed decisions.

This phase is documentation, triage and draft cleanup only.

## Baseline

- Branch `priority-7-phase-2c2-adjudication`
- Commit `9bfa6eba7e714ba98b00277b30f6453b851e8790`
- Tree `5ca86815e6996a3cbf7231e2a35d7267eccf9050`
- Zero remotes, `push.default=nothing`, clean tracked working tree at start
- `_review/` and `_ai_review/` ignored via `.git/info/exclude`

## Inputs

Phase 2C package (`_review/`): review guide, 45-row review sheet, review manifest.
Phase 2C.1 materials (`_ai_review/inputs/`): both track CSVs, the Track B summary, the cross-model
triage workbook, the 12-row human-priority list, the 5-row editorial-fix list, and the source
adjudication CSV and notes. No web access was used; the WSJP findings were taken as supplied.

## Two-model comparison

- 45 / 45 rows reconciled across the review sheet, both tracks and the triage workbook — identical
  ID sets, identical order.
- **29 / 45** rows: full agreement on all five verdict dimensions.
- **16 / 45** rows: at least one disagreement (20 dimension-level disagreements in total —
  example 7, CEFR 5, structure 5, teaching 2, naturalness 1).
- Neither track rejected any pattern: no `ODRZUĆ`, no `NIENATURALNE`, no `ODROCZYĆ` anywhere.
- Track A skews confident and objects mainly to CEFR calibration; Track B skews cautious and objects
  mainly to how patterns and examples are demonstrated to a learner.

## Result: 28 / 12 / 5

| Bucket | Count |
|---|---:|
| Low-risk provisional (research-only, no intervention recommended now) | 28 |
| Human / teacher priority (focused native or teacher judgement needed) | 12 |
| Editorial fix (example/presentation defect only) | 5 |

Mutually exclusive; union is exactly the original 45.

Human priority: 002, 005, 009, 016, 019, 023, 029, 036, 037, 039, 040, 045.
Editorial fix: 011, 012, 033, 042, 044.

The 28 low-risk rows are **not** approved, **not** native-confirmed and **not** release-ready.

## Source adjudications preserved

All supplied WSJP-backed conclusions were preserved unchanged: keep the `means-method` pattern for
*płacić* + Instrumental (013); keep the *lubić* meaning boundary (027); force no canonical sense
split for *wierzyć* (039/040); keep the Accusative visual-perception structure for *widzieć* while
fixing its example (033); keep the subject-experiencer analysis for *podobać się* (037); keep class C
caution for *prosić kogoś o coś*, unupgraded (016); keep the frame for *zależeć komuś na czymś* (045).
Class B caution is retained on 010 and 031.

One conflict was flagged rather than rewritten: on 013 the adjudication resolves Track B's objection
by narrowing what `required` means inside a `means-method` pattern, while the reviewer guide invites
reviewers to judge exactly that field. The decision stands; the wording gap is recorded for a later
phase. Minor coverage gaps between the two supplied adjudication files are also recorded.

Details, including the pedagogical/grammatical split and the one unresolved linguistic question
(029, productivity of *mówić komuś coś*), are in the private adjudication report.

## Drafts

Five AI replacement examples were drafted for the editorial-fix rows, each marked
`ai-draft-noncanonical`. They are proposals only: no `authorRef`, not written into the editorial
corpus, not represented as accepted examples.

## State

- All 45 editorial pattern records remain `reviewState: research`.
- Zero review events created; `reviewEvents` remains empty on all 45 patterns.
- Zero reviewer identities, zero author identities created.
- Zero runtime or public data created; no `content/verb-patterns.json`; no activities enabled; no
  audio enabled.
- Source editorial corpus unchanged (`editorial/verb-pattern-candidates.json`,
  `editorial/priority-7-authoring-context.json` byte-identical to baseline).
- `priority7_tooling.py`, tests, and all application files untouched.
- `_review/` and `_ai_review/` remain ignored and absent from Git status.
- Exactly one tracked change: this report.
- No commit, no push, zero remotes.

## Outputs

Private (ignored): `_ai_review/priority-7-phase-2c2-adjudication.md`,
`priority-7-phase-2c2-human-priority.csv`, `priority-7-phase-2c2-editorial-fix-drafts.csv`,
`priority-7-phase-2c2-low-risk-provisional.csv`, `priority-7-phase-2c2-validation.json`.

Tracked: `reports/priority-7-phase-2c2-summary.md` (this file).
