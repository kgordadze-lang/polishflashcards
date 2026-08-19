# Priority 7 — Phase 4F-B3A Summary

## Adjudication of the two independent editorial reviews

**Final verdict: GO.**

Phase 4F-B1 (primary) and Phase 4F-B2 (blind corroboration) each assessed the same 45 canonical
patterns. Both matrices reconstruct cleanly and are mechanically complete. The two reviews agree
exactly on 13 rows, differ compatibly on 22, and disagree substantively on 10.

All 45 rows now carry exactly one B3A disposition: **21 ACCEPT AS IS**, **19 ACCEPT WITH
NONBLOCKING NOTE**, **5 CHANGE BEFORE EDITORIAL ACCEPTANCE**, **0 DEFER FROM PILOT**. Every change
row carries a field-level instruction B3B can implement without asking a further question. Nothing
canonical was modified here.

Real state is unchanged: **45 reference-verified**, **0 editorial-reviewed**, **0 approved**, 45
reference-verification events, **no editorial-review** event, **no product-approval** event.

---

## 1. Baseline

Verified before any file was written.

| Check | Expected | Observed |
|---|---|---|
| HEAD | `7beb50d7b3463d7745352f1608f1e30019529fdf` | matches |
| Tree | `ad6095037214360836b1bd9a5bb06326e0b809d7` | matches |
| Remotes | zero | zero |
| `push.default` | `nothing` | `nothing` |
| Lemmas / meanings / patterns | 30 / 34 / 45 | 30 / 34 / 45 |
| `reference-verified` / `editorial-reviewed` / `approved` | 45 / 0 / 0 | 45 / 0 / 0 |
| `reference-verification` / `editorial-review` / `product-approval` events | 45 / 0 / 0 | 45 / 0 / 0 |

The blind-review input B2 worked from digests to
`8b1124b9a256863db736cf892bfeb00ed0a700c46d8c889c95a54b9f18246b3c`, which is exactly the digest B2's
own summary records for it, and its header row carries no verdict, severity, finding or rationale
column. The blindness boundary is therefore re-checked here rather than taken on trust.

---

## 2. Reconstruction

| Check | B1 | B2 |
|---|---|---|
| Rows | 45 | 45 |
| Distinct review IDs | 45 | 45 |
| Duplicates | none | none |
| Omissions | none | none |
| Pattern IDs resolving to the corpus | 45/45 | 45/45 |
| Descriptor fields disagreeing between the reviews | — | **0** |

Both reviews read the same data: lemma, meaning ID, pattern ID, pattern, relation type, both CEFR
bands, teaching status and support class are identical across all 45 rows in both matrices.

---

## 3. Agreement classification

Classification is derived from the two source matrices by one published rule, not asserted:
identical verdict **and** identical severity is exact agreement; two accept-family verdicts that
differ in any way is a compatible difference; anything pairing an accept-family verdict with
`CHANGES NEEDED` or `DEFER` is a substantive disagreement.

| Class | Count | IDs |
|---|---:|---|
| **EXACT AGREEMENT** | **13** | 004, 006, 008, 010, 015, 017, 019, 025, 026, 034 (all `ACCEPT`/`NONE`); 029, 030, 037 (all `CHANGES NEEDED`/`MEDIUM`) |
| **COMPATIBLE DIFFERENCE** | **22** | 001, 002, 003, 007, 009, 011, 012, 014, 016, 018, 020, 022, 023, 024, 027, 028, 032, 033, 038, 041, 044, 045 |
| **SUBSTANTIVE DISAGREEMENT** | **10** | **005, 013, 021, 031, 035, 036, 039, 040, 042, 043** |

Twenty of the 22 compatible differences are B1 `ACCEPT WITH NOTE`/LOW against B2 clean `ACCEPT`.
The other two are `P7-NR-018` (B2's only note, against B1's clean accept) and `P7-NR-032`, where
both verdicts are accept-family but B1 raised severity to MEDIUM for a reason external to the row.

The computed substantive set matches the brief's expected high-priority list on 10 of its 15
entries. The other five — 018, 029, 030, 032, 037 — are rows where the reviewers agreed on the
verdict; they are adjudicated individually below regardless, and two of them (029, 030) are
consensus change rows.

**Treatment divergence inside agreement.** Two rows carry the same verdict from both reviewers but
different proposed remedies, and are flagged separately in the matrix: `P7-NR-030` (B2 proposes an
additional label change B1 does not) and `P7-NR-037` (the reviewers propose different CEFR bands).
Agreement that a problem exists did not guarantee agreement on the solution, exactly as the brief
anticipated.

---

## 4. Three facts neither review checked

Three adjudications turn on properties of the locked runtime and schema that neither reviewer
verified. They are pinned by test so that a later change to any of them reopens the decision resting
on it.

1. **`usage.note` has no render path.** `pp-verb-patterns.js` accepts it in `closedKeys` and
   type-checks it, and no renderer reads it. No pattern in the corpus uses it. B1 proposed it as the
   vehicle for two clarifications (rows 013, 016); it would have added canonical text no learner
   can ever see.
2. **The `że` diacritic is not missing.** `CLAUSE_TOKENS` already maps the locked ASCII
   `clauseKind` value `"ze"` to the rendered token `"że …"`. B2's proposed label fix for row 030
   addresses a review-artifact label, not the learner surface.
3. **`required` is inert.** All 54 complements in the corpus are `required: true`, and no renderer
   filters or branches on the flag — every complement renders unconditionally. Flipping it to
   `false` is therefore correct as a record of the evidence but, on its own, invisible to learners.
   This is why the `mówić` correction below is two-part rather than one-part.

A fourth, smaller point: `contentRef.kind` is a closed enum of `card`/`topic`/`drill`/`scenario`, so
B1's proposed pattern-to-pattern contrast link on rows 042/043 is not expressible at all.

---

## 5. Final dispositions

| Disposition | Count |
|---|---:|
| ACCEPT AS IS | **21** |
| ACCEPT WITH NONBLOCKING NOTE | **19** |
| CHANGE BEFORE EDITORIAL ACCEPTANCE | **5** |
| DEFER FROM PILOT | **0** |

| Severity | Count |
|---|---:|
| NONE | **21** |
| LOW | **16** |
| MEDIUM | **8** |
| HIGH | **0** |

| Primary change category | Count |
|---|---:|
| NONE | 21 |
| EXAMPLE | 8 |
| MODEL_LIMITATION | 4 |
| LABEL_OR_NOTE | 3 |
| TEACHING_STATUS | 3 |
| CEFR | 2 |
| MEANING | 2 |
| OPTIONALITY | 2 |

B1's single HIGH severity does not survive adjudication (see `P7-NR-031`). The corpus carries no
HIGH-severity row into B3B.

**Owning phase for the 24 non-clean rows:** 5 to Phase 4F-B3B (canonical implementation), 8 to Phase
4F-C (example work), 5 to a post-pilot model/vocabulary review, and 6 recorded in this register only
so a settled question is not re-litigated.

---

## 6. The change plan

Five rows require a canonical change before editorial acceptance. Each instruction is field-level.
None is implemented here.

### `P7-NR-005` — `słuchać` + Genitive (obey) · LABEL_OR_NOTE · MEDIUM

In `vp-p-sluchac-obey-genitive-object-674adae2dec3`, change `learnerExplanationEn` from

> In the obey sense słuchać still takes the Genitive: **nie słucha rodziców.**

to

> In the obey sense słuchać still takes the Genitive: **dziecko słucha mamy.**

Change no other field. `teachingStatus` stays `recognition-only`; `cefr` stays `{recognition: B1}`.
Directive to 4F-C: the canonical example must also be affirmative and case-transparent.

*Why:* the current illustration is negated, and the Polish genitive of negation independently forces
the Genitive on any object — so the sentence is equally consistent with an Accusative-governing verb
and cannot demonstrate the claim it makes. B1's own remedy (make it affirmative) is insufficient:
`rodziców` is syncretic, since masculine-personal Accusative plural equals Genitive plural. The
replacement must be affirmative **and** case-transparent, which `mamy` (≠ `mamę`) is.

### `P7-NR-029` — `mówić` + Dative + Accusative · OPTIONALITY · MEDIUM

In `vp-p-mowic-tell-content-dative-recipient-accusative-content-2f2b1add1960`:

- **(a)** change `complements[0].required` (the Dative recipient) from `true` to `false`, leaving
  `complements[1]` (Accusative content) `required: true`;
- **(b)** change `learnerExplanationEn` from *"Two roles: the person told is Dative, the thing told
  is Accusative."* to *"The thing told is Accusative and the person told is Dative; the person can be
  left out: mówię prawdę."*

Do not add a new pattern. Do not change `cefr`, `teachingStatus`, `relationType` or evidence. B3B
must recompute the pattern's `reviewEvent` `scopeDigest`, since complements are in scope.

### `P7-NR-030` — `mówić` + Dative + `że`-clause · OPTIONALITY · MEDIUM

In `vp-p-mowic-tell-content-dative-recipient-ze-clause-a01ddc4a4736`:

- **(a)** change `complements[0].required` from `true` to `false`, leaving the clause complement
  `required: true`;
- **(b)** change `learnerExplanationEn` from *"The same meaning with clause content: the person stays
  Dative and że introduces what is said."* to *"The same meaning with clause content: że introduces
  what is said, and the person, if named, is Dative: mówię, że to prawda."*

Do **not** change `clauseKind`. B3B must recompute the `scopeDigest`.

### `P7-NR-037` — `podobać się` + Nominative + Dative · TEACHING_STATUS · MEDIUM

In `vp-p-podobac-sie-appeal-to-nominative-stimulus-dative-experiencer-ef199e675ee9`:

- **(a)** change `teachingStatus` from `recognition-only` to `active-production`;
- **(b)** add `cefr.production = "A2"` (the schema requires a production band once teaching status is
  active-production; recognition stays `A2`).

Change no complement, no role, no `relationType` and no `learnerExplanationEn`. Do not alter
`ROLE_PHRASES`. Directive to 4F-C: author a contrastive canonical example pairing this frame with
`lubić`.

### `P7-NR-040` — `wierzyć` + `w` + Accusative · TEACHING_STATUS · MEDIUM

In `vp-p-wierzyc-have-trust-w-accusative-target-6561408ea8d1`:

- **(a)** change `teachingStatus` from `recognition-only` to `active-production`;
- **(b)** add `cefr.production = "B1"` (the schema forces production `B1` when recognition is `B1`).

Do **not** split the meaning, do not create a new meaning ID, and leave `internalScope` and its
religious / ideological / self-confidence exclusions verbatim.

---

## 7. Defer plan

**No row is deferred from the pilot.** B1's single `DEFER` (`P7-NR-031`) is overturned on the merits
in §8 rather than carried forward, and no other row approaches the threshold. `DEFER` was not used
to avoid a difficult choice: the two hardest calls in this phase — `pytać` and `wierzyć` — are both
answered decisively.

---

## 8. Specific adjudications

### `P7-NR-005` — `słuchać` obey · B1-only finding · **real issue B2 missed**

B1 is right and B2 did not look at the illustration; B2 assessed only the sense split, which is
sound and is left untouched. See §6 for the correction and why B1's own remedy needed strengthening.
This is a change rather than example debt because `learnerExplanationEn` is canonical text that
Phase 4F-C does not own.

### `P7-NR-013` — `płacić` + Instrumental · B1-only finding · **nonblocking editorial preference**

B2's verdict is better supported; B1's *observation* is kept. `ROLE_PHRASES.means` does render as
"how it is done", which reads as manner where the Instrumental is strictly the payment instrument.
But B1's remedy fails on inspection — `usage.note` has no render path (§4.1) — and the phrasebook is
global and locked by design, which B1 itself refuses to repoint for one row. The learner-facing
surface is meanwhile not ambiguous: `learnerExplanationEn` already says "To say how you pay" with
*kartą/gotówką*, and the error note already targets `*płacę z kartą`. **No canonical change.** Kept
as locked-phrasebook debt alongside F-15. Active-production A1 retained.

### `P7-NR-018` — `dbać` + `o` + Accusative · B2-only finding · **KEEP NOTE, corrected**

B2's LOW note is worth keeping but is wrong in part. `o siebie` *does* distinguish Accusative from
Locative (`o sobie`), which is the live confusion in a corpus that also teaches `o` + Locative on
`rozmawiać` and `myśleć` — so the example is less opaque than B2 states. It is nonetheless not
case-transparent for a learner drilling noun endings, since `siebie` is an irregular pronoun with no
visible Accusative morphology. B2's own alternative *dbać o zdrowie* does not fix that either:
`zdrowie` is neuter and its Accusative is identical to its Nominative. Keep the natural existing
example; 4F-C should add a feminine `-ę` noun (*dbać o kondycję*, *dbać o formę*), the only shape
that makes the Accusative visible. Useful editorial debt, not release debt.

### `P7-NR-021` — `rozmawiać` + `o` + Locative · B1-only finding · **editorial preference, overturned**

B2 is better supported. F-03 reads a lexicographic artifact as a usage restriction. WSJP separates a
plural-subject reciprocal schema from a singular-subject `z KIM` schema, but that separation
idealises the entry, not the language: *Nie rozmawiam o pracy w domu* and *Nie lubię rozmawiać o
polityce* are ordinary Polish with a singular subject and no expressed partner. The authored pattern
licenses no error, and narrowing or downgrading a core A2 frame on that basis would be a real
pedagogical loss for no correctness gain. Note kept only to record that the explanation's plural
(*rozmawiamy o pracy*) is a stylistic choice, not an encoded restriction, so F-03 does not recur.

### `P7-NR-029` / `P7-NR-030` — `mówić` · consensus change rows

Both reviewers independently found the same defect and it survives verification: the cited
`Składnia` schemas are `(KOMU) + CO` and `(KOMU) + że ZDANIE`, with the Dative parenthesised, yet
both patterns mark it `required`, so the corpus cannot express *Mówię prawdę* or *Mówię, że…*.

**Is the Dative truly optional in the attested frame?** Yes — the parenthesis in the source says so
directly, and both constructions are ordinary Polish without a recipient.

**Smallest safe correction.** Flip the flag; do not author new patterns. A new pattern would take
the pilot to 46 rows after 4F-A closed reference verification at 45, and would need its own evidence
and verification event. `required: false` instead makes the data agree with evidence *already*
verified. But — the correction neither reviewer's version would have achieved — the flag alone is
inert (§4.3), so it must be paired with the one field that reaches the learner. Hence the two-part
change in §6.

B2's additional sub-proposal on row 030, that the learner-facing label loses the Polish `ż`, is
**rejected as factually wrong** (§4.2).

### `P7-NR-031` — `pytać` + `o` + Accusative · **B1's DEFER/HIGH overturned; retained in pilot**

The brief asks for a decisive product-content recommendation on five questions. Answers:

- **Should it remain in the pilot?** **Yes**, as authored.
- **Active-production or recognition-only?** **Active-production.** Asking about price, directions
  and times is core A2 transactional production. Downgrading would recreate the exact defect both
  reviewers flagged on row 037 — half of a contrast produced, half only recognised.
- **A2 appropriate?** **Yes.**
- **Does omitting the addressee create a misleading model?** **No.** The addressee is genuinely
  omissible in ordinary use, and row 032 supplies the full frame under the same meaning.
- **Is fuller `KOGO` + `o CO` treatment preferable?** **No — not instead.** Both, staged.
- **Should it coexist with `P7-NR-032`?** **Yes**, and that is already the architecture: 031 is the
  A2 short frame, 032 the B1 full frame, mirroring `prosić` 015/016 and `pomagać` 002/003.

Three grounds for overturning. First, two of B1's four compounding reasons are out of scope or
non-distinguishing: reference validity was settled by 4F-A and this phase may not revisit it, and
the missing example is shared with 21 other rows. Second, **B1's own editorial test acquits the
row** — the test B1 formulated is whether the short frame is a complete idiomatic utterance in its
own right, and *Pytam o cenę* is exactly that, as complete as *Dziękuję za pomoc*. Third, the
support is the same *kind* B1 called the model case for the subframe standard: 4F-A records
`pytać`'s support as `Połączenia`, the same section that supports `pomagać`'s bare Dative.

What survives is B1's real point, kept as a LOW note: the lemma has no clean repository sentence —
its only attestation realises the perfective partner `zapytać` — so 4F-C must author the example
fresh rather than reuse.

### `P7-NR-032` — `pytać` + Accusative + `o` + Accusative

B1's MEDIUM severity was explicitly conditional on row 031 deferring. Row 031 is retained, the
premise dissolves, and severity drops to LOW. The kept note is the example dependency: the only
repository sentence with this verb and an `o` phrase is marked slang and is referenced rather than
reused, so 4F-C must author fresh here too.

### `P7-NR-035` — `myśleć` + `o` + Locative · B1-only finding · **facts right, disposition wrong**

Every element of F-19 verifies: the Locative drill sentence sits in a `full` field outside the
locked repository-reuse provenance enum, and the only complete repository sentence realises the
excluded opinion sense. But this is an example defect, not a pattern defect, and §12 of the brief
governs: **PATTERN ACCEPT + EXAMPLE WORK REQUIRED**. Severity stays MEDIUM rather than LOW because,
uniquely among the example-less rows, nothing can be reused — 4F-C must author from scratch.

### `P7-NR-036` — `znaleźć` + Accusative · split decision

**On B1's F-09:** right, and understated. *W końcu udało mi się znaleźć mieszkanie* buries the
pattern in an impersonal `udać się` construction with a Dative clitic — and neither reviewer noticed
that it also fails on transparency, since `mieszkanie` is neuter and its Accusative is identical to
its Nominative. The sentence meant to show "znaleźć takes the Accusative" shows no Accusative
morphology at all. Replacement is clearly necessary, but it is example work, which 4F-C owns; the
pattern is accepted. A concrete suggestion for 4F-C: a finite, unembedded sentence with a feminine
`-ę` object — *Znalazłem dobrą pracę* — which is also the sense cue the locator cites.

**On B2-004 (CEFR):** **dropped.** B2 asked for A2 production "unless aspect or inflection
sequencing supplies a documented reason", and the record supplies exactly that — the lemma is typed
`aspect: perfective`, so it has no present tense and production requires past or perfective-future
forms plus the `znaleźć`/`znalazłem` stem alternation. A2/B1 stands.

### `P7-NR-037` — `podobać się` · consensus change row

Reference evidence and `relationType` are untouched, as instructed. The pedagogical questions:

- **Recognition-only vs active-production?** **Active-production.** Both reviewers independently
  reject recognition-only for a core everyday construction whose explicit contrast partner `lubić`
  is produced at A1.
- **A2 treatment?** **Yes — production at A2.** This is the one place the reviewers proposed
  different levels (B1: A1–A2 for the fixed frame; B2: B1 after controlled A2 recognition), and B1's
  position is better supported *by B2's own stated reason*. If the defect is that recognition-only
  "underserves the pilot", setting production at B1 leaves `podobać się` two full bands behind
  `lubić` and only half-fixes it. Production at A2 matches the pattern's own recognition band,
  respects that the clitic cluster warrants being later than `lubić`, and is schema-valid.
- **Contrast with `lubić`?** Preserved and strengthened; 4F-C should author a contrastive example.
- **Should the reversal become a key teaching pattern?** **Yes.** The Nominative stays in the
  complement list: rendering the stimulus as a slot beside the Dative is what makes the reversed
  mapping visible, and the runtime already overrides its phrasing to "the thing that appeals".

B1's second sub-proposal — retune the Dative role phrase — is **rejected**.
`ROLE_PHRASES.experiencer` is global and locked, is shared with row 045 where "the person it happens
to" is apt, and the only sanctioned override already applies to the Nominative. B1 itself forbids
repointing a global phrase for one row.

### `P7-NR-039` / `P7-NR-040` — `wierzyć` · the grouping question

**Option C: retain the grouping, and clarify by promoting the sibling — not option B.**

The source groups them: the cited sense *mieć zaufanie* lists both `KOMU/CZEMU` and `w KOGO/CO`
under one numbered sense, so the grouping is not imposed on the data. The contrast B2 wants to
protect is already carried where learners meet it — the two patterns state it explicitly ("To
believe a person, use the Dative" / "For confidence in a person or thing, use w + Accusative") and
`internalScope` names both readings. Splitting the meaning would file the two halves *apart*, making
the contrast less visible, not more. And the architectural cost is real: a split moves the pilot
from 34 meanings to 35, needs a new meaning ID and scope, and reopens meaning-level reference
support that 4F-A closed. This is the dictionary-taxonomy purity the brief warns against.

B2's *separate* point — that recognition-only is unnecessarily restrictive — is **upheld**, and is
actioned on row 040. Taking the two halves of one finding on their own merits is not splitting the
difference. B1's defence of the asymmetry (production would invite learners into excluded territory)
does not survive scrutiny: government is invariant across those senses, so a learner who produces
*wierzę w Boga* produces correct Polish with correct government. The exclusion bounds the corpus's
meaning inventory, not the learner's output; the risk is scope leak, not error. Against that,
*wierzę w ciebie* is high-value everyday production, and teaching only one half of an explicitly
paired contrast for production is the same defect flagged on row 037. Promoting 040 also removes the
unexplained sibling asymmetry F-16 records.

### `P7-NR-042` — `zajmować się` (look-after) · B1-only finding · **overturned**

B2 is better supported. F-08 reads the status split as an unexplained inconsistency, but it follows
a principle the corpus applies consistently: **the primary or dedicated sense is produced; the
secondary sense of a polysemous verb is recognised.** That is exactly rows 004/005 (`słuchać`
perception produced, obey recognised) and rows 023/024 (`bać się`). Here the dedicated care verb
`opiekować się` is produced and the secondary care sense of a verb whose pilot-primary sense is
occupation (041, active-production) is recognised — which also protects the learner from choosing
between two readings of the same surface string, *zajmuję się dzieckiem* against *zajmuję się
marketingiem*. **No change.** B1's specific remedy is in any case not expressible: `contentRef.kind`
is a closed enum, so a pattern cannot reference a sibling pattern. Note kept to record the principle
so the asymmetry stops reading as an oversight.

### `P7-NR-043` — `opiekować się` · B1-only finding · **real issue, but example work**

F-10 verifies and is the sharpest example finding in the corpus: this is the only pattern whose own
evidence records that no card, drill, scenario or podcast line uses the lemma anywhere, and it is
authored active-production with no canonical example. But the pattern is clean — EXACT-FRAME
`KIM/CZYM`, single-frame entry, good error note — and §12 governs: it is not downgraded for example
work 4F-C owns, and it is not singled out for a gate the other fifteen example-less
active-production rows do not face. The F-08 half is resolved at row 042. Severity MEDIUM because
the example must be authored from nothing.

---

## 9. Pattern defects versus example defects

Eight rows are marked **PATTERN ACCEPT + EXAMPLE WORK REQUIRED** — accepted linguistically, with
concrete work handed to Phase 4F-C, which owns final example work: **007, 014, 018, 031, 032, 035,
036, 043**. Three of them (035, 036, 043) carry MEDIUM severity because the work is harder than
ordinary drafting: two must be authored from nothing, and one must replace an example that is
actively working against the pattern it illustrates.

No linguistic pattern was downgraded for missing or weak example work. The corpus-level example gap
— 22 of 45 patterns without a canonical example, 16 of them active-production — remains a single
phase-level dependency on 4F-C, recorded once rather than duplicated as 18 row-level findings.

---

## 10. LOW-note triage

Nineteen notes kept, eleven dropped. Neither outcome blocks advancement.

**KEEP NOTE (19).** 001 (locator cue ≠ taught scope), 007 and 014 (example above the pattern's
band), 009 and 028 (infinitive CEFR — kept with the *resolution*, see below), 013 and 016 (locked
role phrasebook), 018 (case-transparent example), 021 (plural is stylistic, not encoded), 023 and
045 (closed-enum model limits), 027 (excluded `lubić` people sense blocks the `podobać się`
contrast), 031 and 032 (`pytać` examples must be authored fresh), 035, 036, 043 (example work), 039
(grouping decision recorded), 042 (status asymmetry is principled).

**DROP NOTE (11).** 002, 003, 011, 012, 020, 022, 024, 033, 038, 041, 044 — every one of these
carried F-01, and nothing else, or F-01 plus an already-tracked 4C replacement. F-01 is a
corpus-level dependency that B2 records identically as a dependency rather than a finding. Recording
it 18 more times as row-level release debt would add no information.

**One sub-finding dropped inside a kept row:** B2-004's CEFR half on row 036 (see §8).

**F-12 resolved rather than carried.** The `uczyć się` / `lubić` infinitive CEFR mismatch is
adjudicated, not deferred: the two placements can both be right, and B1 itself named the escape.
`lubić` + infinitive is a fixed high-frequency A1 formula with no competing frame; `uczyć się` +
infinitive expresses skill acquisition and must first be separated from `uczyć się` + Genitive (row
008), a genuine extra demand. No CEFR change on either row; the note records the justification so
the asymmetry stops reading as unreconciled.

---

## 11. Canonical boundary

Nothing in `editorial/verb-pattern-candidates.json` or
`editorial/priority-7-authoring-context.json` was modified; both are byte-identical to the pinned
baseline `7beb50d7b3463d7745352f1608f1e30019529fdf`. No editorial actor was registered — the
`editorialActorRegistry` still holds only `priority7-reference-analysis` with the
`reference-verification` role and nothing else, and B1's deliberate decision not to register a
tier-2 identity is left standing.

| | |
|---|---|
| `reference-verified` | **45** |
| `editorial-reviewed` | **0** |
| `approved` | **0** |
| `reference-verification` events | **45** |
| `editorial-review` events | **0** |
| `product-approval` events | **0** |

Every change this phase wants is in the matrix's `b3aProposedChange` column and in §6 of this
document, and nowhere else. Both source reviews are preserved unchanged and pinned by SHA-256; they
are evidence, and this phase read them only.

---

## 12. Validation

| Gate | Result |
|---|---|
| `tests/test_priority7_phase4fb3a.py` (new) | pass |
| Phase 4F-A, 4E.1, 4E, 5-A, 4C, 3F-A, 2A suites | pass |
| Full Python suite | pass |
| Full JXA suite | pass |
| `validate_content.py` | pass |
| `verify_audio.py` | pass |
| `build_pages.py --check` | pass |
| `priority7_tooling.py validate-editorial` | valid |
| `git diff --check` | clean |
| Committed-scratch survivability | pass |

Every baseline comparison in the new suite is pinned to
`7beb50d7b3463d7745352f1608f1e30019529fdf` by SHA rather than resolved as `HEAD`, so it means the
same thing before and after this candidate is committed.

---

## 13. Final verdict

**Final verdict: GO.**

Adjudication is complete. All 45 patterns carry exactly one disposition, the ten substantive
disagreements are each decided on the better-supported treatment rather than averaged, both
consensus change rows have an exact correction, and the five change rows give Phase 4F-B3B a
field-level implementation plan that needs no further decision. No question was left for the project
owner to settle before canonical implementation can proceed.

Two calls are worth the owner's attention on the way past, both stated and reasoned rather than
open: production at **A2** rather than B1 for `podobać się` (§8), the one row where the reviewers
proposed different bands; and the promotion of `wierzyć w` + Accusative to production while its
excluded senses stay excluded (§8).

Phase 4F-B3B is **not** begun here. No canonical field was changed, no editorial-review event was
created, nothing was approved, frozen or generated.
