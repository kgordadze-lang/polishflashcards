# Priority 7 — Phase 2C Review-Package Preparation Summary

**Phase:** `priority-7-phase-2c`
**Purpose:** convert the approved Phase 2B research corpus and native-review queue into a
package a native Polish reviewer can evaluate without reading JSON, code or Git history.
**Not** a linguistic-authoring phase. No review was conducted and no review state advanced.

---

## 1. Safety baseline

Verified before any file was written:

| Check | Expected | Observed |
|---|---|---|
| Working directory | `/Users/Kaj/Downloads/Repository for Claude - Priority 7 Phase 2C` | matches |
| Branch | `priority-7-phase-2c-review-package` | matches |
| HEAD | `543191cf4bf86aa0330d59aadffb441b780c5080` | matches |
| Tree | `e12cd989e2b470c9c487d9a5b8d5556032d922c2` | matches |
| Git remotes | zero | zero |
| `push.default` | `nothing` | `nothing` |
| Starting working tree | clean | clean |
| `_review/` | exists, ignored via `.git/info/exclude` | exists, `_review/` present in `.git/info/exclude` |

SHA-256 baselines were recorded for every protected source file before packaging began and
re-checked at the end (§11).

## 2. Authoritative inputs

Read read-only. No web browsing, no new linguistic research, no correction of the corpus.

- `editorial/verb-pattern-candidates.json` — authoritative corpus (30 lemmas, 34 meanings,
  45 patterns, all `reviewState: research`)
- `editorial/priority-7-authoring-context.json` — confirms `reviewerRegistry` and
  `authorRegistry` are empty
- `reports/priority-7-phase-2b-native-review-queue.md` — 22 targeted questions (NRQ-01 …
  NRQ-22) and 22 draft sentences (B-01 … B-22)
- `reports/priority-7-phase-2b-pilot-coverage.md`
- `reports/priority-7-phase-2b-source-evidence-audit.md` — evidence classification §2
- `reports/priority-7-phase-2b-summary.md`
- Phase 1 specifications, in particular `priority-7-pattern-data-specification.md` §5–6 for
  the case-question convention, plus the Phase 2A tooling contract, for terminology
  consistency.

Every Phase 2B count used as a target was first reconciled against the source files. All
reconciled exactly; nothing was forced to a target.

## 3. Package methodology

1. The corpus was flattened in its deterministic on-disk order — lemma order, then meaning
   order, then pattern order — producing exactly 45 patterns. That order is the sheet order
   and the manifest order.
2. Each pattern was rendered into reviewer-readable form:
   - `pattern_display` renders the construction so it is understandable at a glance
     (`szukać + Genitive`, `pomagać komuś w + Locative`, `zależeć komuś na + Locative`).
     The final slot is shown as `preposition + Case`; earlier participant slots use a Polish
     placeholder pronoun. The structured complement data was **not** replaced — it is
     rendered in full alongside, in `complement_structure`, with role and requiredness.
   - `case_question` uses the Phase 1 convention: base questions per case, with the
     preposition prefixed for prepositional complements (`na kogo? na co?`, `o kim? o czym?`).
     Infinitive and clause complements are marked as not applicable rather than given an
     invented question.
   - `meaning_en` carries the English glosses plus the meaning's scope statement, because
     meaning boundaries are one of the things the reviewer is asked to judge.
   - `learner_explanation_en`, `relation_type`, `recognition_cefr`, `production_cefr` and
     `teaching_status` are copied verbatim from the corpus. Absent production CEFR (the
     recognition-only patterns) is shown as `—`.
3. Reviewer-facing instructions and all review questions were written in plain Polish. The
   English learner gloss and explanation stay visible, because the product teaches Polish to
   English-speaking learners and those strings are themselves under review.
4. Technical metadata appears only where it helps trace a decision: `pattern_id`,
   `evidence_class`, `question_ids`. Stable-ID mechanics, review fingerprints, frozen
   baselines and runtime projection are absent from the reviewer-facing material.
5. Review-only row IDs `P7-NR-001` … `P7-NR-045` were minted for the sheet. They are not
   Priority 7 canonical IDs and were not written into the editorial corpus (verified, §10).

## 4. Package file locations

Reviewer-facing files, under the locally ignored `_review/`:

| File | Bytes |
|---|---:|
| `_review/priority-7-native-review-guide.md` | 12 512 |
| `_review/priority-7-native-review-sheet.csv` | 58 091 |
| `_review/priority-7-native-review-manifest.json` | — |

Trackable preparation report (this file):

- `reports/priority-7-phase-2c-summary.md`

No reviewer-response data was created in `editorial/`. No duplicate or alternate versions of
any package file were created.

## 5. 45-row coverage

The CSV is UTF-8 with standard CSV quoting and has exactly **45 data rows**, one per pattern.

- Every editorial pattern ID appears exactly once; no unknown ID appears.
- Row order is byte-for-byte the corpus order.
- `P7-NR-001` … `P7-NR-045` are complete, unique and in sequence.

Column order, exactly as specified:

```
review_row_id, pattern_id, lemma, meaning_en, pattern_display, relation_type,
complement_structure, case_question, learner_explanation_en, recognition_cefr,
production_cefr, teaching_status, evidence_class, special_attention, example_kind,
example_pl, example_en, question_ids, questions_pl, structure_verdict,
naturalness_verdict, example_verdict, cefr_verdict, teaching_status_verdict,
replacement_example_pl, reviewer_notes_pl
```

## 6. Example split — 23 reuse / 22 draft

Every one of the 45 rows carries exactly one example candidate.

| `example_kind` | Rows | Source |
|---|---:|---|
| `repository-reuse` | 23 | the pattern's canonical example in the corpus, copied byte-for-byte |
| `draft-original-not-canonical` | 22 | the corresponding draft B-01 … B-22 from the Phase 2B native-review queue |

The 23 + 22 mapping resolved exactly onto the 45 patterns with no residue: the 22 patterns
with no canonical example are precisely the 22 patterns for which the queue holds a draft.
No missing draft was invented.

The drafts remain **outside** canonical editorial data. The guide states explicitly that
approving a draft in this sheet does not make it canonical — that still requires a named
example-authoring authority, which does not exist (Phase 2B §11.1).

Row-to-draft mapping is recorded in the manifest under `reviewRowToDraftExampleId`.

## 7. Targeted questions

All **22** unique question IDs (`NRQ-01` … `NRQ-22`) are represented in the sheet. None was
dropped or merged.

- Questions were rewritten into plain Polish for reviewer clarity; the substantive issue of
  each was preserved, including its specific sub-questions.
- A question mapped to more than one pattern appears on every pattern it concerns
  (for example `NRQ-12` on both `słuchać` meanings and both `zajmować się` meanings).
- `NRQ-15` (all 24 error notes are predicted, not documented) is instantiated per pattern
  with that pattern's own predicted wrong form and proposed guidance, so it reaches all 23
  patterns that carry an error note.
- 38 rows carry at least one question; 7 rows carry none.
- The manifest proves representation via `questionIdToReviewRows` and
  `questionIdsRepresented`.

## 8. Evidence-class distribution

Copied from the approved Phase 2B source-evidence audit §2. No linguistic evidence was
recalculated and no source URL appears in the sheet — the class alone signals where extra
scrutiny is required.

| Class | Rows | Patterns |
|---|---:|---|
| A | 40 | frame corresponds to a listed contemporary schema |
| B | 3 | `pomagać` + Dat, `dziękować` + `za` + Acc, `pytać` + `o` + Acc |
| C | 1 | `prosić` + Acc person + `o` + Acc thing |
| D | 1 | `podobać się` Nom stimulus + Dat experiencer |

`special_attention = yes` was set for every B/C/D pattern, every pattern carrying a targeted
question, and every pattern Phase 2B identified as high-risk — the Phase 2B queue places all
22 questions in its "highest-risk structural questions" section, so those two sets coincide.
Result: **38 rows `yes`, 7 rows `no`**. Every B/C/D pattern also carries at least one
question, so the two criteria overlap rather than conflict.

## 9. Blank reviewer decision fields

These seven columns are blank in all 45 rows, verified mechanically:

`structure_verdict`, `naturalness_verdict`, `example_verdict`, `cefr_verdict`,
`teaching_status_verdict`, `replacement_example_pl`, `reviewer_notes_pl`

Nothing was pre-answered. The allowed values are defined only in the guide.

## 10. Review verdict vocabulary

Defined in `_review/priority-7-native-review-guide.md`, which is written primarily in
natural Polish.

| Decision | Allowed values |
|---|---|
| Structure | `OK`, `ZMIEŃ`, `ODRZUĆ`, `NIEPEWNE` |
| Naturalness | `NATURALNE`, `MOŻLIWE_ALE_NIETYPOWE`, `NIENATURALNE`, `NIEPEWNE` |
| Example | `OK`, `POPRAW`, `ODRZUĆ`, `BRAK_PRZYKŁADU` |
| CEFR | `OK`, `ZA_NISKO`, `ZA_WYSOKO`, `NIEPEWNE` |
| Teaching status | `PRODUKCJA`, `TYLKO_ROZUMIENIE`, `ODROCZYĆ`, `NIEPEWNE` |

The guide explains that `PRODUKCJA` means learners should actively practise producing the
form, `TYLKO_ROZUMIENIE` that recognition is useful without requiring active production, and
`ODROCZYĆ` that the pattern should not enter this pilot yet. It asks for a free-text comment
in `reviewer_notes_pl` whenever the choice is anything other than the positive/default
verdict.

The guide also directs attention to meaning boundaries, case and preposition government,
required versus optional participants, lexical `się`, contemporary usage, register, whether
the English learner explanation misleads, whether the example unmistakably demonstrates the
intended pattern, whether a pattern is too advanced for its proposed CEFR, and whether
production practice would be frustrating or ambiguous. It states plainly that this is a
selective A1–B1 learner pilot, not an exhaustive Polish dictionary.

Named as needing closer attention, because their evidence mapping is qualified: `pomagać`,
`dziękować`, `pytać`, `prosić`, `podobać się`. Named as deliberately outside the current
pattern corpus, open for comment but not for addition in this phase: `czekać, aż …` and
`mówić po polsku`.

## 11. Manifest and hashes

`_review/priority-7-native-review-manifest.json` is a mechanical verification artifact, not
reviewer-facing prose. It records the phase, the source integration commit and tree, the
headline counts, the ordered list of all 45 pattern IDs, the ordered
`review_row_id → pattern_id` mapping, the row-to-draft mapping, the
`question_id → review rows` mapping, all 22 represented question IDs, and the file hashes.
It contains no reviewer identity and no reviewer response.

| File | SHA-256 |
|---|---|
| `priority-7-native-review-sheet.csv` | `1db52bcaccfc495ef7b070ab29a9d1abc6ae2f37eb68e14f14c1661385fd3a73` |
| `priority-7-native-review-guide.md` | `950ae89ec35c33375a348143f4617cc7e702b0a8aa1dc285bbc41595c36ba950` |
| `priority-7-native-review-manifest.json` | `b9c95c0a9063a43cbcbf042c450708ef771b5127e54ff39e52e7eddb04d3d37f` |

Source corpus hash recorded in the manifest for traceability:
`b6fb8139ed99368a2a1527db6dd79d32f06df3e2e069cf59ae559a798176435f`.

## 12. Mechanical validation

A one-off validation script was run from the session scratchpad; no production tooling was
created or modified. 38 checks, all passing:

- CSV has exactly 45 data rows, with the exact specified columns in the exact order.
- Every editorial pattern ID appears exactly once; no unknown ID; corpus order preserved.
- `P7-NR-001` … `P7-NR-045` complete, unique and in sequence.
- Exactly 23 `repository-reuse` and exactly 22 `draft-original-not-canonical`; every row has
  a non-empty example; reuse examples are byte-identical to the corpus; draft rows occur
  only where the corpus has no example.
- Exactly 22 unique targeted question IDs represented; every row with `question_ids` has
  question text; no unresolved templating placeholders.
- Evidence classes 40 / 3 / 1 / 1; `special_attention` follows the stated rule.
- All seven reviewer-response columns blank in all 45 rows.
- CEFR, teaching status, relation type and learner explanation copied unchanged.
- All 45 corpus patterns still `reviewState: research`; no `reviewEvents`; no
  `activityEligibility`; `reviewerRegistry` and `authorRegistry` still empty.
- No review-state or identity vocabulary in the reviewer-facing files (the only occurrences
  are inside the manifest's own explanatory notice, which states what is absent).
- No `P7-NR-` ID written into the editorial corpus.
- CSV and guide hashes match the manifest; manifest counts, ordering and row map match the
  sheet.
- `_review/` absent from `git status`; zero remotes; HEAD unchanged.
- Every protected source file byte-identical to its recorded baseline.

## 13. Ignore status of `_review/`

`_review/` is listed in `.git/info/exclude` and is therefore ignored locally. Confirmed
absent from `git status --short --untracked-files=all`. Its contents are not tracked, not
staged and not committed.

## 14. Explicit end-of-phase confirmations

- **No editorial corpus data changed.** `editorial/verb-pattern-candidates.json` and
  `editorial/priority-7-authoring-context.json` are byte-identical to their baseline hashes.
- **No review state changed.** All 45 patterns remain `research`. No `reviewState` was
  written, no review event of any kind was created, and no acceptance was calculated as
  though review had occurred.
- **No reviewer identity and no author identity was created.** `reviewerRegistry` and
  `authorRegistry` remain empty objects.
- **No draft example was promoted to a canonical example.** The 22 drafts exist only in the
  review sheet, marked `draft-original-not-canonical`.
- **No CEFR, teaching status, activity eligibility, evidence, ID, meaning or pattern was
  altered.**
- **No app/runtime file changed.** `content/verb-patterns.json` was not created; no audio
  was generated; nothing was frozen.
- **`priority7_tooling.py`, `tests/test_priority7_phase2a.py` and every Phase 1/2B report
  are byte-identical to baseline.** The only new tracked file is this summary.

## 15. Inconsistencies found and reported, not corrected

None. Every Phase 2B count used by this phase reconciled exactly against the source files:
30 lemmas, 34 meanings, 45 patterns, 23 canonical examples, 22 patterns without one, 22
drafts, 22 targeted questions, 24 predicted error notes across 23 patterns, evidence classes
40 / 3 / 1 / 1. No corpus wording was cleaned up and no linguistic issue was fixed during
packaging.

## 16. Final Git scope

```
?? reports/priority-7-phase-2c-summary.md
```

Zero remotes. No commit. No push. No branch operation of any kind.

## 17. Next step (not authorised by this phase)

Deliver `_review/priority-7-native-review-guide.md` and
`_review/priority-7-native-review-sheet.csv` to a native Polish reviewer, keeping
`_review/priority-7-native-review-manifest.json` for verification of what was sent. The
completed sheet returns as reviewer input; converting it into review events still requires a
named native-linguistic reviewer authority, which does not yet exist.
