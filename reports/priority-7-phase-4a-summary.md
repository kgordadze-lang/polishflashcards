# Priority 7 — Phase 4A Reviewer-Ready Linguistic Closure Package

**Phase:** `priority-7-phase-4a-reviewer-closure`
**Purpose:** turn the existing research corpus, the two provisional AI review tracks and the
Phase 2C.2 source adjudication into a compact package a Polish native speaker / teacher can
work through without reconstructing Priority 7's history or reading 45 dense research records.
**Not** an adjudication phase. **Not** a canonical-data-edit phase. No review was conducted, no
review state advanced, no linguistic conclusion was created.

---

## 1. Safety baseline

Verified before anything was written:

| Check | Expected | Observed |
|---|---|---|
| Working directory | `/Users/Kaj/Downloads/Repository for Claude - Priority 7 Phase 4A` | matches |
| Branch | `priority-7-phase-4a-reviewer-closure` | matches |
| HEAD | `f339efb1d5a2cb4f27cfcc1458e118beefb43b87` | matches |
| Tree | `bedd14b99a642f6af16cef73a0a9170cfbb49395` | matches |
| Git remotes | zero | zero |
| `push.default` | `nothing` | `nothing` |
| Starting working tree | clean | clean |

HEAD and tree were re-verified at the end of the phase and are unchanged. No commit, no push,
no remote, no branch operation of any kind.

## 2. Authoritative material used

Read read-only from this repository:

- `editorial/verb-pattern-candidates.json` — the corpus (30 lemmas, 34 meanings, 45 patterns,
  all `reviewState: research`)
- `editorial/priority-7-authoring-context.json` — confirms `reviewerRegistry` and
  `authorRegistry` are empty, and records the source-use boundaries
- `reports/priority-7-phase-2b-native-review-queue.md` — NRQ-01 … NRQ-22, drafts B-01 … B-22,
  the Part C level/status inventory and the Part D list of deliberate omissions
- `reports/priority-7-phase-2b-source-evidence-audit.md` — evidence classes A/B/C/D, the
  Mędak/WSJP use boundaries, the correction and source-precision passes, evidence gaps
- `reports/priority-7-phase-2b-summary.md`, `reports/priority-7-phase-2b-pilot-coverage.md`
- `reports/priority-7-phase-2c-summary.md` — review-row minting rule, packaging conventions,
  reviewer-verdict vocabulary
- `reports/priority-7-phase-2c2-summary.md` — the two-track AI comparison and every preserved
  source adjudication
- `reports/priority-7-pattern-data-specification.md` — `relationType` and `required` semantics
- `reports/priority-7-provenance-and-review-specification.md` — review kinds and gates
  (`external-verification`, `native-linguistic`, `product-approval`); a native-linguistic
  reviewer cannot be an AI identity
- `reports/priority-7-phase-3a-*` and `reports/priority-7-phase-3e-summary.md` — confirmation
  that the release boundary and the "nothing is enabled" state are unchanged

### No new outside research

No web browsing, no WSJP lookup, no Google, no dictionary consultation, no corpus search, no new
linguistic conclusion. Everything linguistic in the package is a condensed paraphrase of a
conclusion already recorded in the tracked material above, and every statement the tracked
material does not support is marked as unavailable in the package itself.

## 3. Review-row mapping and its provenance

The package is keyed on the Phase 2C review row IDs `P7-NR-001` … `P7-NR-045`.

Those IDs were minted in Phase 2C into `_review/priority-7-native-review-manifest.json`, which
lived in a locally ignored directory. **That directory is not part of this repository and is
absent from this working copy**, so the stored mapping could not simply be read back.

The mapping was therefore recomputed from the rule the tracked Phase 2C summary states in §3:
the corpus is flattened in its deterministic on-disk order (lemma, then meaning, then pattern),
and rows are numbered sequentially. The recomputed mapping was then cross-checked three ways:

1. row-by-row against the Part C pattern inventory in the Phase 2B native-review queue, which
   lists all 45 patterns in the same order — exact match;
2. against every row number cited in the Phase 2C.2 summary — `013` płacić Instrumental
   (`means-method`), `027` lubić, `033` widzieć, `037` podobać się (`subject-experiencer`),
   `039`/`040` wierzyć, `016` prosić, `045` zależeć komuś na czymś, `010`/`031` class B,
   `029` mówić — all match;
3. against the class B/C/D assignments in the source-evidence audit — `002`, `010`, `031` class
   B, `016` class C, `037` class D — all match.

The mapping and its derivation note are recorded in the package manifest.

## 4. Partition — 12 / 5 / 28

The locked partition was applied exactly as specified and was not altered.

| Group | Count | Review IDs |
|---|---:|---|
| Human / teacher priority | 12 | 002, 005, 009, 016, 019, 023, 029, 036, 037, 039, 040, 045 |
| Example replacement | 5 | 011, 012, 033, 042, 044 |
| Low-risk confirmation | 28 | the remaining rows |

Mutually exclusive, union exactly 45, proved mechanically (§10), not by counting by hand.

## 5. Package contents and location

Outside the repository, at `/Users/Kaj/Downloads/Priority_7_Phase_4A_Reviewer_Package`:

| File | Bytes | SHA-256 |
|---|---:|---|
| `Priority_7_Human_Review.xlsx` | 32 146 | `69ed564026954021c5908e86c0c06023409fa058e8f7b869621d2f1920e63d7e` |
| `human-priority.csv` | 23 349 | `7b9cdb55f13de6c45af86f207094ecc1e975d5bbceb5a6e4380a28dcd9f60587` |
| `example-replacements.csv` | 5 837 | `6009a328d3a38911822cd6f246b53c1e43befd5640c489f12b14eda01bfbfb5b` |
| `low-risk-confirmation.csv` | 14 709 | `99ad48e80951d252cd3dd6bd0590ecfd07b48cfd11c40d43058c0f324839628a` |
| `README.md` | 3 072 | `de0ee6361af37c27a988ff47aee0bad4bfa51fec61323014ad253ff06511052e` |
| `manifest.json` | 25 057 | `96f2c300ab081fd6ca97be3cf72f3fba1f640542eab5cac2241ece49432f38f0` |

The workbook has five sheets: **Start Here**, **Priority Review** (12), **Example Review** (5),
**Quick Confirmation** (28), **Decision Guide**. No macros, no formulas, no external links.
`.gitignore` was not modified, and nothing from the package was placed inside the repository.

## 6. How the 12 priority questions were made answerable

Each priority row carries, in reviewer-readable prose and without any JSON: the verb, the
meaning with its scope boundary, the pattern, the participants in plain terms, the Polish case
question, the sentence currently attached and its status, the level and current teaching
treatment, the English wording the app would show, the current provisional treatment, **why the
row needs human judgement**, **what the sources already settled**, and **one specific question**.

The questions are derived from the tracked adjudication, not invented. Issue types actually
present: whether a one-slot teaching subframe is idiomatic alone (002); whether a same-case
sense split helps a learner (005); level and whether a representation overstates government
(009); the single weakest-evidenced combined frame (016); an unauthored alternant (019); a
contemporary-vs-2011 sense split plus a production-difficulty question (023); the one
explicitly unresolved question carried forward from Phase 2C.2, the productivity of
`mówić komuś coś` (029); confirming that `szukać`/`znaleźć` must not be shown as an aspect pair
(036); the only editor-analysed structural slot and its recognition-only status (037); whether
two constructions belong under one learner meaning (039) and whether the second is readable as
trust rather than belief (040); a subjectless construction's teaching presentation (045).

The **Learner-facing treatment** dropdown is exposed only on the nine rows whose tracked
question actually concerns recognition versus production or level; on 019, 036 and 039 the cell
is greyed and carries no dropdown. The Decision Guide states that this answer is advice and does
not by itself change product eligibility.

The adjudicated positions are presented as provisional, never as human-approved: `płacić` +
Instrumental stays a means/method relation with contemporary support for `CZYM` and
`CZYM + za CO`; `lubić` keeps the thing/activity meaning boundary; `wierzyć` keeps both frames
under one trust meaning because the source licenses both, with the learner-facing treatment left
open; `widzieć` keeps its structure and gets an example fix; `podobać się` keeps the
subject-experiencer model with presentation left open; combined `prosić` stays research at its
weaker class-C provenance; `zależeć komuś na czymś` stays structurally supported with
presentation open.

The `means-method` / `required` wording tension on row 013 is presented to the reviewer as
internal schema/editorial debt that the team owns — explicitly **not** as resolved, and
explicitly not a question for the reviewer.

## 7. Example-review design

The five rows show the intended meaning, the pattern, the sentence currently attached and its
status, what the problem is, the proposed replacement, and why it was proposed. Reviewer fields
are replacement decision, natural contemporary Polish, fits the intended meaning/pattern,
suggested final example, and comment.

The header of the replacement column reads `PROPOSED REPLACEMENT (AI draft, not approved)`; the
manifest records each of the five as `ai-draft-noncanonical`, `humanAuthored: false`,
`inCanonicalCorpus: false`; and the Decision Guide states that "Accept replacement" is review
input only — a person applies accepted changes in a later step, and nothing is written into the
canonical corpus by this package.

Two of the five (033, 011) carry a defect that the tracked material records. For the other three
(012, 042, 044) the tracked material lists the row among the five example fixes but does not
record the defect; those rows say so in plain words and offer only the observable difference
between the current sentence and the proposal. Nothing was reconstructed. Rows 042 and 044 have
no canonical example at all — the sentence currently attached to them is an unapproved Phase 2B
draft, and the sheet says so.

## 8. Quick-confirmation design

The 28 low-risk rows show only Review ID, verb, meaning, pattern, example sentence, example
status, level/teaching, and a short note where the tracked material has something worth knowing.
There is exactly one required answer — **Review** (`Looks good` / `Flag for review` / `Unsure`) —
plus an optional comment. Notes were written for 22 of the 28 rows; the other six carry none.

## 9. Traceability

Internal identifiers are present but not foregrounded. Each sheet carries `pattern_id`,
`meaning_id`, `lemma_id` and `example_id` (plus `evidence_class` on the priority sheet) in hidden
columns at the far right; the CSVs carry the same columns unhidden. The manifest additionally
holds the full 45-row mapping of review ID → group, lemma, lemma ID, meaning ID, pattern ID,
example ID or draft ID, and evidence class. No identifier was invented: rows whose pattern has no
example in the corpus carry the Phase 2B draft identifier (`draft B-xx (not in corpus)`) rather
than a fabricated example ID.

## 10. Package validation

A one-off validation script was run from the session scratchpad. **94 checks, 94 passed, 0
failed.** No production tooling was created or modified. The checks cover:

- baseline: branch, HEAD, tree, zero remotes, `push.default`, no tracked file modified, package
  written outside the repository;
- corpus: 30 lemmas, 34 meanings, 45 patterns, 45/45 `research`, zero review events, zero
  activity eligibility, empty reviewer and author registries, no `P7-NR-` ID written into the
  corpus, none of the five AI drafts present in the corpus;
- partition: 45 unique review IDs, 12 / 5 / 28, no overlap, no omission, every row traced to a
  real pattern ID, 45 unique pattern IDs, row numbering matching every row cited in Phase 2C.2;
- workbook: opens, five expected sheets in order, expected columns per sheet, 12 / 5 / 28 data
  rows, frozen header, autofilter, hidden technical columns, dropdowns present, no formulas
  anywhere, no macros, no external links;
- reviewer state: every reviewer cell blank on all three sheets, every Start Here reviewer field
  present and blank, no cell holding any decision-vocabulary value, no AI identity anywhere in
  the three review sheets;
- CSV parity: identical headers, identical row counts, identical Review IDs in identical order,
  identical context and technical values, reviewer columns blank;
- manifest: counts 12/5/28/45, partition match, all 45 rows mapped, corpus state `research`,
  HEAD/tree recorded, corpus hash matching the file on disk, file hashes matching the files on
  disk, no reviewer response value, all five replacements marked as unapproved AI drafts;
- README: present and covering the required points.

Generation and validation scripts live outside the repository, in the session scratchpad at
`.../263688e3-cc4a-42c2-a34c-0a09ca0c3cee/scratchpad/`: `corpus.py`, `rowtext.py`,
`build_package.py`, `validate_package.py`. They are listed here rather than deleted so Phase 4C
can regenerate or re-verify the package; nothing depends on them at runtime.

## 11. Canonical corpus and review/release state — unchanged

- `editorial/verb-pattern-candidates.json` and `editorial/priority-7-authoring-context.json` are
  untouched; `git status` shows no modification to any tracked file.
- 30 lemmas, 34 meanings, 45 patterns; **45/45 `reviewState: research`**.
- Zero review events. Zero activity eligibility. Zero reviewer identities. Zero author
  identities. Zero product approvals.
- The five AI-draft replacement sentences were **not** written into the corpus and carry no
  author attribution.
- No implementation code, test, runtime file, public data file or audio was created or modified.
  No `content/verb-patterns.json`. Nothing was frozen, enabled or released.
- AI review is kept strictly separate from native review: the package discloses that two
  independent AI tracks (GPT-5.6 Sol, Claude Opus 5) were used provisionally and that source
  adjudication followed, and states plainly that this does not replace native review. No AI
  identity appears as a reviewer, author or approver, and no native-review field, review event or
  approval field was populated anywhere.

## 12. Observations reported, not acted on

Per the phase rule, these are recorded rather than silently corrected:

1. **The Phase 2C/2C.1 working directories are absent.** `_review/` and `_ai_review/` were
   locally ignored and never tracked, so the stored review-row manifest, the two track CSVs and
   the per-row AI verdicts are unavailable in this working copy. The row mapping was recovered
   from the documented rule and cross-checked (§3); the per-row AI verdicts were not recoverable
   and were not reconstructed.
2. **Two kinds of per-row rationale are unavailable and are marked as such in the package:** the
   specific defect behind example rows 012, 042 and 044, and the specific objection that placed
   P7-NR-009 in the priority group. For 009 the package says so explicitly and derives its
   question from what the tracked records do contain for that pattern (unevidenced CEFR values,
   the lexical-`się` identity question, and the pilot's own rule against implying government the
   verb does not have).
3. **Several rows carrying tracked Phase 2B "highest-risk" questions sit in the low-risk 28** —
   006 (`czekać`: the unauthored bare Genitive, and `czekać, aż …` being unencodable), 013
   (`płacić` means/method), 025 (`być` predicative scope), 027/028 (`lubić` and the existing
   `nie lubię` card), 035 (`myśleć`, whose reuse was withdrawn). This is consistent with Phase
   2C.2, where those questions were closed by source adjudication and "low risk" explicitly does
   not mean approved, so **the partition was not changed**. Instead each of those rows carries a
   one-line note in the Quick Confirmation sheet so the reviewer can flag it in seconds.
4. **The `required` wording gap on row 013 is still open**, exactly as Phase 2C.2 left it, and is
   presented as schema/editorial debt rather than as a resolved question.
5. **"Phase 4B" and "Phase 4C" are labels from the Phase 4A instruction, not from tracked
   reports.** The tracked implementation plan has only a generic Phase 4. The package therefore
   tells the reviewer that a later step applies decisions, without naming a phase.

## 13. Repository scope

```
?? reports/priority-7-phase-4a-summary.md
```

That is the only repository change. Zero remotes. No commit. No push. No `.gitignore` change. The
reviewer package is outside Git.

## 14. Next step (not authorised by this phase)

Deliver the package directory to a Polish native speaker / teacher. The returned workbook is
reviewer input only: converting it into review events still requires a named native-linguistic
reviewer authority, which does not yet exist, and applying any accepted example still requires a
named example-authoring authority, which also does not yet exist.
