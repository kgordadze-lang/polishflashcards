# Priority 7 Phase 4F-D1 — Final Integrated Corpus Editorial Verification

Assessment only. No canonical data was changed, no editorial-review event was
created, no product approval was begun, and nothing was frozen, projected or
released.

---

## 1. Baseline

| Item | Value |
| --- | --- |
| Branch | `priority-7-phase-4fd1-final-editorial-review` |
| HEAD | `3d613def18e9edf8bcabd331d40b5b90df30a9da` |
| Tree | `3d1a9600041f83a9a2374b0fef5a069bc77a4d63` |
| Canonical corpus SHA-256 | `6a174face8dffdcf26f0c2e073bf183287f9d67c09ac28d661ce61c3b257c257` |
| Authoring context SHA-256 | `bee8eb95ed78775e50a7fc57da2381d67c43087b00c836e6e6cb0c81925df718` |
| Remotes | none |
| `push.default` | `nothing` |

All four expected hashes matched on entry and again on exit.

### Baseline validation (before any content review)

| Gate | Result |
| --- | --- |
| C2D, C2C, C2B, C2, C1C, B3B, 4F-A, 4E.1, 4E, 5-A, 4C, 3D-1, 3F-A, 2A | **1018 passed, 0 failed** |
| Full Python (`pytest tests/`) | **1234 passed, 0 failed** |
| Full JXA (36 suites, `osascript -l JavaScript`) | **36/36 green, 0 failed** |
| `validate_content.py` | OK — 1215 cards, 353 drills, 1675 ids |
| `verify_audio.py` | OK — 3377 phrases / 3377 manifest entries / 3377 MP3s |
| `build_pages.py --check` | OK — committed output current, 32 sitemap URLs |
| `priority7_tooling.py validate-editorial` | `Priority 7 private editorial record: valid` |
| `git diff --check` | clean |

Baseline was green, so content review proceeded.

**One invocation-mode observation, not a baseline failure.**
`tests/test_priority7_phase4fc1c.py` line 862 does a bare
`import test_priority7_phase4fb3b`, which needs `tests/` on `sys.path`. Under
`pytest` (the project's runner, whose default prepend import mode supplies it)
C1C is green at 73 passed. Under `python3 -m unittest tests.test_priority7_phase4fc1c`
from the repository root the five `HistoricalB3BGuardTests` error with
`ModuleNotFoundError`. The later C2 suite fixed the same construct by adding an
explicit `sys.path.insert` before the import; C1C did not receive that edit.
This is a historical test-harness fragility, touches nothing canonical, and D1
did not modify it.

---

## 2. Coverage

All 45 final canonical patterns were reviewed as integrated wholes — not only
recently changed rows. One matrix row per pattern, 45 rows, no duplicates.

- `reports/priority-7-phase-4fd1-final-editorial-matrix.csv` — 45 rows
- `reports/priority-7-phase-4fd1-blind-final-review-input.csv` — 45 rows
- `tests/test_priority7_phase4fd1.py`

Corpus state confirmed unchanged: 30 lemmas, 34 meanings, 45 patterns,
29 canonical examples, 45 reference-verified, 47 reference-verification
accepts, 0 editorial-review events, 0 product approvals.

---

## 3. Final counts

### Verdicts

| Verdict | Count |
| --- | --- |
| ACCEPT | 23 |
| ACCEPT WITH NOTE | 22 |
| CHANGES NEEDED | 0 |
| DEFER | 0 |

### Severity

| Severity | Count |
| --- | --- |
| NONE | 23 |
| LOW | 22 |
| MEDIUM | 0 |
| HIGH | 0 |

### Editorial acceptance

| Recommendation | Count |
| --- | --- |
| YES | 45 |
| NO | 0 |

### Blocking rows

There are **no blocking rows**. No row requires a canonical change, deferment
or substantive independent adjudication before an editorial-review event could
be created.

This result was stress-tested rather than assumed. The strongest candidates for
a MEDIUM finding were examined explicitly and each fell short:

- **P7-NR-036** — the `errorNotes` entry still names `mieszkanie`, the object of
  the example Phase 4F-C1C replaced. It is nonetheless a correct, self-contained
  illustration that neither quotes nor contradicts the current example, and its
  guidance disambiguates with the singular `znaleźć mieszkanie`. Phase 4F-C2C
  had already adjudicated exactly this errorNote/example noun decoupling as a
  non-defect on P7-NR-043.
- **P7-NR-016** — the evidence note's "awaiting human external and native
  confirmation" is imprecise now that AB accepted all 45 rows on 2026-08-13, but
  external verification genuinely does remain outstanding, and the note is an
  internal research annotation with no learner-facing render path.
- **Twelve active-production rows carry no canonical example.** This is the
  locked Phase 4F-C1C example scope (13 rows), not an authoring gap, and
  `activityEligibility` is empty on all 45 rows so nothing is generated from
  them. Phase 4F-B3B had already classified the outstanding example directives
  as nonblocking.

A genuinely clean result is reported here because the review found one, not
because 45/45 was targeted.

---

## 4. Nonblocking notes (22)

Every note below is retained for future polish or debt. None blocks editorial
acceptance.

| Finding | Row | Lemma | Note |
| --- | --- | --- | --- |
| P7-D1-001 | P7-NR-001 | szukać | WSJP locator sense cue `zaginionego` is narrower than the authored scope and the café example; Genitive government is invariant across the candidate senses. |
| P7-D1-002 | P7-NR-005 | słuchać | No canonical example; the B3B directive for an affirmative, case-transparent example is outstanding. The corrected explanation already satisfies it. |
| P7-D1-003 | P7-NR-009 | uczyć się | A2/B1 sits a band above the Genitive sibling P7-NR-008 (A1/A2) and the reused example is from an A1 card; adjudicated as justified by the governing verb. |
| P7-D1-004 | P7-NR-011 | dziękować | Durable key `thanks-for-cooperation` no longer describes the sentence; the English "I thank my sister for dinner" is literal and slightly formal. |
| P7-D1-005 | P7-NR-012 | płacić | Durable key `how-much-for-everything` no longer describes the sentence. |
| P7-D1-006 | P7-NR-013 | płacić | `required: true` on the Instrumental means slot is construction-scoped, not verb-scoped; locked `ROLE_PHRASES.means` renders as "how it is done", which reads as manner. |
| P7-D1-007 | P7-NR-016 | prosić | Evidence note partly superseded by AB's Phase 4C acceptance; locked `ROLE_PHRASES.interlocutor` misfits `prosić`; no canonical example. |
| P7-D1-008 | P7-NR-018 | dbać | English "I look after my fitness every day" is a slightly unidiomatic rendering of `dbam o kondycję`. |
| P7-D1-009 | P7-NR-021 | rozmawiać | `required: true` on a slot WSJP parenthesises `(o CZYM)`; the plural illustration is stylistic, not an encoded restriction. |
| P7-D1-010 | P7-NR-023 | bać się | Pattern key says `genitive-stimulus` while the closed `ROLES` enum forces role `target`; no `stimulus` member exists, so no canonical change is available. |
| P7-D1-011 | P7-NR-027 | lubić | Excluding the people sense means the `lubić` / `podobać się` personal contrast the corpus cross-references cannot be shown. Post-pilot coverage. |
| P7-D1-012 | P7-NR-028 | lubić | English "before sleep" diverges from the shipping card's own "before bed" for the identical sentence; the Polish still resolves byte-exactly. |
| P7-D1-013 | P7-NR-029 | mówić | B3B directive for examples showing the recipient present and omitted is outstanding; the optional-Dative correction itself is complete. |
| P7-D1-014 | P7-NR-030 | mówić | Same outstanding example directive; the clause complement and optionality wording are correct. |
| P7-D1-015 | P7-NR-031 | pytać | Subframe support rests on a single collocation rather than a class, as the canonical evidence note itself records. |
| P7-D1-016 | P7-NR-033 | widzieć | Durable key `saw-your-sister` no longer describes the sentence; explicitly adjudicated in Phase 4F-C2C. |
| P7-D1-017 | P7-NR-036 | znaleźć | errorNote names `mieszkanie`, the object of the replaced example; the distractor string is homographic with a grammatical Accusative plural. |
| P7-D1-018 | P7-NR-037 | podobać się | B3B directive for a contrastive `podobać się` / `lubić` example is outstanding; the active-production promotion is itself coherent. |
| P7-D1-019 | P7-NR-039 | wierzyć | One broad `have-trust` meaning carries both frames; retained by decision, split not re-litigated. |
| P7-D1-020 | P7-NR-040 | wierzyć | B3B directive for a contrastive `wierzę ci` / `wierzę w ciebie` example is outstanding; the promotion removes the sibling asymmetry. |
| P7-D1-021 | P7-NR-042 | zajmować się | recognition-only against 043's active-production while both English glosses read "look after"; distinction rests on `teachingStatus`. |
| P7-D1-022 | P7-NR-045 | zależeć | A subjectless impersonal construction typed `lexical-frame`, with subjectlessness carried by prose alone. Model boundary. |

---

## 5. Status of the five B3B corrections

All five corrections survive intact in the final integrated corpus and remain
coherent. None was reopened; no reference-level conflict was found.

| Row | Final state | Verdict |
| --- | --- | --- |
| **P7-NR-005** | `learnerExplanationEn` reads `dziecko słucha mamy` — affirmative and case-transparent, since Genitive `mamy` is distinct from Accusative `mamę`. `recognition-only`, `cefr.recognition B1`, no `production` key. | ACCEPT WITH NOTE (example directive outstanding) |
| **P7-NR-029** | `complements[0].required = false` (Dative recipient), `complements[1].required = true` (Accusative content). Explanation states the omission explicitly: "the person can be left out: mówię prawdę." Two reference-verification accepts. | ACCEPT WITH NOTE |
| **P7-NR-030** | `complements[0].required = false`, `że`-clause `required = true`, `clauseKind` left as the ASCII enum key `ze`. Explanation reads "the person, if named, is Dative". Two reference-verification accepts. | ACCEPT WITH NOTE |
| **P7-NR-037** | `active-production` with `cefr.production A2` against `recognition A2`. The `subject-experiencer` relation and the reversed Nominative-subject / Dative-experiencer mapping are stated in both `learnerExplanationEn` and the errorNote. Status fits the pattern. | ACCEPT WITH NOTE |
| **P7-NR-040** | `active-production` with `cefr.production B1` against `recognition B1`. Broad parent meaning kept verbatim; the promotion removes the pre-existing asymmetry with the already active-production Dative sibling P7-NR-039. Level fits the final meaning and pattern. | ACCEPT WITH NOTE |

**029 / 030 optional Dative semantics** are coherent: the optional flag, the
learner explanation and the WSJP `(KOMU)` parenthesisation agree, and the
required content complement is untouched in both rows.

---

## 6. Status of the previously discussed points

Reassessed on the final state; none is a problem, and none was relitigated
without new evidence.

| Row(s) | Point | Finding |
| --- | --- | --- |
| **P7-NR-013** | `means-method` / `required` terminology | Coherent. `required` is scoped to the taught construction, not to the verb, and the corpus applies that convention consistently (cf. 006, 021). The learner surface is unambiguous. Retained with P7-D1-006. |
| **P7-NR-031** | `pytać o` + Accusative intentionally in the pilot | Retained. The single-collocation subframe support is recorded truthfully in canonical evidence; the created example realises the addressee-less frame cleanly. P7-D1-015. |
| **P7-NR-039 / 040** | broad `wierzyć` meaning architecture | Retained. Both frames sit under one cited WSJP sense, the two explanations state the contrast, and a split would move the pilot to 35 meanings and reopen meaning-level support. P7-D1-019, P7-D1-020. |
| **P7-NR-042 / 043** | `zajmować się` / `opiekować się` teaching distinction | Retained and confirmed still distinct after the C2C repair. 042 stays `recognition-only`, 043 `active-production`, following the corpus's primary/secondary-sense principle. P7-D1-021; 043 itself is a clean ACCEPT. |
| **P7-NR-037** | `podobać się` subject-experiencer structure | Coherent. Representing the Nominative stimulus as a complement slot is how the locked model expresses the reversed mapping, and `relationType` names it. P7-D1-018 concerns only the outstanding example. |

---

## 7. Audit results

### Error-note audit

24 `errorNotes` entries across 21 patterns were reviewed against their final
patterns and examples.

- Every predicted error is a real learner mistake and every `guidanceEn` states
  the case the pattern actually teaches. No note teaches a contradictory case.
- **P7-NR-007 is clean.** The row that exposed historical example/error-note
  coupling in the C2 example work retained its example, so `zaświadczenie` /
  `zaświadczenia` still matches `Potrzebuję zaświadczenia z pracy.` exactly.
- One stale coupling survives: **P7-NR-036** names `mieszkanie`, the object of
  the example C1C replaced. It remains correct standalone and does not
  contradict the current example (P7-D1-017).
- **P7-NR-043**'s explanation and errorNote still use `babcia` while the example
  now uses `młodszą siostrą`. Phase 4F-C2C recorded this as a deliberate,
  non-defect trade for source distance, and the errorNote's Accusative/Instrumental
  minimal pair is preserved. Not re-opened.
- Other noun differences between errorNote and example (011, 013, 032, 035) are
  independent minimal pairs that were never coupled to the example.

### Learner-explanation audit

All 45 `learnerExplanationEn` fields were reviewed.

- Each names the exact case or preposition correctly, and each is concise.
- Required/optional participant wording is accurate everywhere. The two rows
  with an optional participant (029, 030) both say so in words.
- No explanation implies exhaustive valency; the deliberately selective rows
  (019 `tęsknić`, 035 `myśleć`, 040 `wierzyć`) read as selective.
- No stale wording was found after the C2/C2C example changes: the five rows
  whose wording was replaced (011, 012, 033, 036, 043) have explanations that
  are independent of the example text.

### CEFR / status audit

- `teachingStatus`: 41 `active-production`, 4 `recognition-only`. No `deferred`.
- All 4 `recognition-only` rows (005, 024, 042, 045) declare `cefr.recognition`
  only and no `cefr.production`. All 41 `active-production` rows declare both.
- No row has production below recognition.
- `usage.priority` is `core` (31) or `common` (14). No `limited` row exists, so
  the "limited forbids active-production" rule is vacuously satisfied.
- `activityEligibility` is `[]` on all 45 rows, so `grammar-build` and `type-it`
  are unreachable everywhere and the recognition-only restriction cannot be
  violated. Eligibility remains an explicit allowlist defaulting to false, and no
  durable pattern mastery exists in the pilot.
- One internal asymmetry is noted rather than changed (P7-D1-003, row 009). No
  new curriculum philosophy was imposed.

### Sibling-pattern audit

Eleven lemmas carry more than one pattern: `pomagać` (002/003), `słuchać`
(004/005), `uczyć się` (008/009), `dziękować` (010/011), `płacić` (012/013),
`prosić` (015/016), `rozmawiać` (020/021/022), `bać się` (023/024), `lubić`
(027/028), `mówić` (029/030), `pytać` (031/032), `wierzyć` (039/040),
`zajmować się` (041/042), `zależeć` (044/045).

- Every sibling set is meaningfully distinguishable, by complement structure,
  by meaning, or — for 041/042 and 042/043 — by teaching status.
- Optional participants are represented consistently: only 029/030 carry an
  optional slot, and both do so identically.
- No example collapses an intended distinction. 031's example deliberately omits
  the addressee that 032's supplies; 020/021/022 have no examples to collide;
  042 and 043 keep distinct complements, which C2C verified when repairing 043.
- No two sibling explanations contradict one another.

### Provenance audit

- 18 `repository-reuse` examples: **all 18 resolve byte-exactly** to their
  recorded `card.<field>` source in the shipping corpus, checked mechanically
  through `validate_content.load_source_corpus`.
- 11 `editorial-generated` examples: all name `priority7-example-generation` as
  `generatorRef`, all carry `adoptedAt 2026-08-16`, and none carries any extra
  attribution key. `authorRegistry` is empty and no `origin.kind = original`
  example exists, so no false human or original attribution is present.
- `editorial-generated` was treated as the process/provenance classification it
  is. **No internet-wide uniqueness audit was performed** and none is claimed;
  the C2B/C2C collision screens stand as the record on that question.
- Seven reuse rows carry an English gloss that differs from the source card's
  `exEn`. Five are contraction normalisation ("I'm" → "I am"). Two are wording
  choices, of which one is noted (P7-D1-012, row 028: "before sleep" against the
  card's more idiomatic "before bed"). The Polish, which is what the recorded
  `field: ex` provenance claims, is identical in all 18.

---

## 8. Remaining uncertainties

- **No human external verification and no product approval exist**, and D1 does
  not substitute for either. All 45 rows remain `reference-verified` under
  `solo-maintainer-reference-backed`, which never means human external
  verification, professional linguistic review or native-speaker review.
- **Five durable example keys and the IDs minted from them no longer describe
  their sentences** (011, 012, 033, 036, 043). This is the accepted opaque-identifier
  condition from C2B/C2C, but it is real maintainability debt: a future
  maintainer grepping by ID will be misled.
- **English register on a few glosses** (011, 018, 028) is serviceable but not
  the most idiomatic available. For the reuse rows this cannot be fixed without
  weighing it against exact repository resolvability.
- **Locked-model debt** (013, 016, 023, 045) is not fixable inside the current
  closed enums and should inform any post-pilot revision of `ROLES`,
  `ROLE_PHRASES` and `relationType`.
- Twelve `active-production` rows still have no canonical example.

---

## 9. Boundary confirmations

- **No canonical content changed.** `editorial/verb-pattern-candidates.json`,
  `editorial/priority-7-authoring-context.json` and `priority7_tooling.py` are
  byte-identical to `3d613def18e9edf8bcabd331d40b5b90df30a9da`, and their
  SHA-256 values match the published baseline.
- **No editorial-review event was created.** No pattern rose above
  `reference-verified`; the only actor on any review event is
  `priority7-reference-analysis`; no editorial-review actor is registered.
- **No product approval was begun.** No `approved` review state and no
  `product-approval` event exists.
- No actor was added, no ID or allocation changed, and no runtime or shipping
  content moved. The candidate footprint is exactly four paths: the three D1
  reports and this phase's test suite.
- Nothing was frozen, projected or runtime-released.

---

## 10. Blind Codex package

`reports/priority-7-phase-4fd1-blind-final-review-input.csv`

- 45 rows, the exact canonical pattern set, 32 columns.
- Carries lemma, aspect, reflexivity, meaning key, glosses and internal scope,
  pattern key, relation type, complements with required/optional, CEFR, teaching
  status, usage, activity eligibility, learner explanation, error notes, final
  Polish and English, example key/ID/provenance, evidence source identifiers and
  notes, review state, release mode, content refs, and sibling-pattern context.
- Excludes the D1 verdict, severity, acceptance recommendation, finding ID,
  finding summary, required change, nonblocking note and all persuasive
  adjudication language.

Blindness was verified programmatically, not asserted: header scan, cell scan
for serialized field names, and a scan for adjudication vocabulary
(`accept with note`, `changes needed`, `defer`, `nonblocking`, `blocking`,
`P7-D1-`) all returned zero hits, and the pattern set was proved equal to both
the matrix and the canonical corpus. These checks are pinned in
`tests/test_priority7_phase4fd1.py`.

| Artifact | SHA-256 |
| --- | --- |
| `priority-7-phase-4fd1-blind-final-review-input.csv` | `069ceee9e55bc3f1fffa152014dec024de826b8001caa0beabcffbdff114c916` |
| `priority-7-phase-4fd1-final-editorial-matrix.csv` | `3e3e5a85f3d464d79721db7da0e22b7e68bf217d7e5b3e2b16768e0e824644c7` |

---

## 11. Committed-scratch survivability

A fresh isolated scratch clone was made from the complete D1 candidate, its
remote removed, and the four D1 artifacts committed there **only**. The real D1
workspace was never committed.

| Check | Result |
| --- | --- |
| Scratch parent | `3d613def18e9edf8bcabd331d40b5b90df30a9da` (baseline child) |
| Working tree | clean |
| Remotes | zero |
| Commit contents | exactly the 3 D1 reports + `tests/test_priority7_phase4fd1.py` |
| D1 + C2D + C2C + C2B | 184 passed, 0 failed |
| Full Python | 1295 passed, 0 failed |
| Full JXA (36 suites) | 36/36 green, 0 failed |
| `validate_content.py` / `verify_audio.py` / `build_pages.py --check` / editorial | all OK |
| `git diff --check HEAD^ HEAD` | clean |
| Canonical hashes in committed scratch | unchanged |

### Future-safety proof

A harmless hypothetical later-phase report and test suite
(`priority-7-phase-4fz9-*`) were then added and committed on top in the scratch.

- The historical C2B / C2C / C2D protections stayed green (123 passed), so they
  do **not** encode "no future Priority 7 phase may ever add another file".
- **Full Python stayed green at 1296 passed** with the later phase present, so
  no historical suite anywhere in the repository regressed.
- D1's own footprint check stayed correct and still resolved to D1's four paths,
  because `candidate_revision()` resolves the candidate as the first descendant
  of the pinned baseline rather than diffing HEAD.

The hypothetical commit was then removed, the scratch restored to the D1-only
state (184 passed, `git diff --check` clean), and the scratch deleted.

**One artifact defect was caught by this stage and fixed.** The first generated
CSVs used `csv.writer`'s default CRLF terminator, which `git diff --check` reads
as trailing whitespace; the repository's other report CSVs are LF. Both files
were regenerated with `lineterminator="\n"`, the recorded SHA-256 values below
are the corrected ones, and `ArtifactHygieneTests` in the D1 suite now pins LF
endings, no trailing whitespace and a single terminal newline so this cannot
recur.

---

## 12. Final verdict

**GO**

All 45 final patterns are recommended for editorial acceptance as authored.
Twenty-two rows carry optional, nonblocking notes; no row requires a canonical
change or deferment. Canonical state is unchanged and the blind Codex package
is ready.

Editorial-review events were not created and product approval was not begun.
