# Priority 7 — Phase 4F-A Summary

## Real corpus reference verification

**Verdict: GO.**

All 45 real patterns were audited against freshly re-opened authoritative sources and all 45 are now
`reference-verified` under `solo-maintainer-reference-backed`, recorded by a registered nonhuman
reference-analysis actor. 41 rest on **exact-frame** support and 4 on **subframe** support. Nothing
was advanced past tier 1 and no human assurance is claimed anywhere.

This document records the phase as it actually happened, including the pass that got it wrong.

---

## 1. History of this phase

The result was reached in two passes. The first was too strict; the second corrected the standard,
not the data.

| | |
|---|---|
| **Pass 1 (initial)** | Re-inspected all 34 cited WSJP PAN locators and required a printed `Składnia` schema whose slot set matched the authored pattern. Result: **41 verified, 4 unresolved, 0 correction needed**. The four rows left at `research` were `pomagać` + Dative, `dziękować` za + Accusative, `prosić` KOGO + o CO and `pytać` o + Accusative |
| **Independent review** | Found that exact-`Składnia` matching was **too strict** for this corpus, and that the first pass had made one outright false claim and one unnecessary evidence addition |
| **Pass 2 (this document)** | Adopted the locked learner-subframe standard, read the `Definicja` / `Połączenia` / `Cytaty` sections of the four entries, verified all four on authoritative usage, reverted the unnecessary addition, and fixed a CRLF defect in the matrix. Result: **45 verified, 0 unresolved, 0 correction needed** |

Three defects from pass 1 are corrected here and named explicitly:

1. **A false claim about `prosić`.** Pass 1 reported that WSJP "never combines" the accusative person
   with the `o` request. That was true of the `Składnia` schema inventory and **false of the entry**:
   this sense's `Cytaty` contain contemporary usage realising both in a single clause. The claim is
   retracted, the evidence note now records the usage support, and a regression test forbids any
   artefact from reintroducing it.
2. **An unnecessary `podobać się` evidence addition.** Pass 1 added a second WSJP record for sense 2
   (`odpowiadać komuś`) and asserted that sense 2 "is the reading the record's learner treatment
   actually uses". That was wrong. Sense 1's own `Połączenia` list `film, książka, muzyka` among the
   subjects, and its definition reads "wyglądem **lub innymi cechami** … daną rzecz". Sense 1 already
   covers the learner treatment. The sense-2 record has been **removed** and the wording corrected.
3. **CRLF line endings in the audit matrix.** `csv.DictWriter` defaults to `\r\n`; the matrix was
   written with 46 CRLF terminators. It is now pure LF, and a test asserts the file contains no `\r`.
4. **A baseline-comparison test that went vacuous once committed.** Found by the committed-scratch
   gate during pass 2, not by review. Phase 4F-A's own baseline assertions resolved the baseline as
   `git show HEAD:…`; in the scratch rehearsal `HEAD` *is* the candidate, so the file was compared
   against itself and the note-rewrite count collapsed from 7 to 0. The baseline is now pinned by
   SHA (`681ff69`), so those assertions mean the same thing before and after commit, and the
   shipping-file guard now inspects both the working tree and the committed diff.

This summary is **not** rewritten as though the first pass had been 45/45.

---

## 2. The verification standard

The locked pattern-data specification settles what a pattern is:

> "A pattern is a complete, meaning-specific learner construction with one relationship
> classification and an ordered set of complement slots."

and what the corpus is:

> "The corpus is selective teaching content, not an exhaustive dictionary."

A learner pattern therefore does **not** have to reproduce every complement of one complete WSJP
`Składnia` row. It may isolate a governed complement when authoritative evidence establishes that
complement and contemporary usage licenses the construction. Verification accepts two support kinds
and no others:

| Support kind | Standard | Count |
|---|---|---|
| **EXACT-FRAME** | a printed `Składnia` schema directly realises the authored construction | **41** |
| **SUBFRAME** | the entry's own `Definicja`, `Połączenia` or `Cytaty` realise the taught complement — with or without the other participants the formal `Składnia` row lists | **4** |

Subframe support is **authoritative-usage** support. It **never licenses inferring a frame from model
intuition**, and it never licenses arbitrary slot deletion: participant structure, case and
preposition government, and the omissibility being taught, each still require evidence from the entry
itself. Every subframe row's evidence note names the section that supplies the support and states
what `Składnia` does and does not show, so no record can pass usage support off as a printed schema.

---

## 3. What was actually inspected

The recorded evidence metadata was treated as a claim to check, not as a source.

| Step | What was done |
|---|---|
| Entry/sense pages | All **34** distinct `wsjp.pl` locators cited across the 45 patterns were re-fetched on 2026-08-14 |
| Parent entries | All **30** parent entry pages were fetched to enumerate each entry's numbered sense inventory |
| Składnia | Each table was parsed **mechanically** — row by row, subject column / verb / complement column — so no model paraphrase sits between the printed schema and the audit decision |
| Definicja / Połączenia / Cytaty | Read for the four subframe rows and for `podobać się`, to establish usage support and sense coverage |
| Repository locators | All 45 `data-*.js` locators re-resolved through `validate_content.load_source_corpus`; all resolve, and their corpus-wide claims were re-tested |
| Mędak locators | **Not re-inspected** — the demo PDF is unavailable to this phase, so no Mędak record was re-dated and none is pinned by any acceptance |

Every locator resolved to a live page whose title cue matches the sense named. The four sense-less
locators (`dziękować`, `dbać`, `rozmawiać`, `opiekować się`) are single-sense entries, so they are
unambiguous as written. Ten "numbered separately" scope claims were each checked against the real
sense list and all ten were exact — including `mieć`'s "nineteen numbered senses".

---

## 4. The four subframe rows

| Row | Pattern | What `Składnia` shows | What licenses the learner pattern |
|---|---|---|---|
| 2 | `pomagać` + Dative | `KOMU + w CZYM \| przy CZYM`; `BEZOKOLICZNIK + (KOMU)`; `KOMU + CZYM` — no `KOMU`-only schema | `Połączenia` realises the **bare Dative recipient as its own collocation class** of persons and groups helped, listed separately from the `w`/`przy` groups; the sense definition names the participant as *komuś* |
| 10 | `dziękować` za + Accusative | all four schemas carry `KOMU` | the **sense definition itself** realises *wdzięczność za coś* with no recipient, and `Połączenia` lists a separate **za-CO collocation class** of things thanked for |
| 16 | `prosić` KOGO + o CO | `o CO` and a bare `CO` object as **separate** schemas | this sense's **`Cytaty`** contain contemporary usage realising the accusative person and the `o` + Accusative request **together in one clause**; `Połączenia` independently attests human accusative objects |
| 31 | `pytać` o + Accusative | `KOGO + o KOGO/CO`; `KOGO + ZDANIE PYTAJNOZALEŻNE`; `MOWA WPROST` | `Połączenia` realises the `o` phrase **with no expressed addressee**, and `Cytaty` show the addressee omitted |

**Row 31 is the thinnest of the four and is recorded as such.** Its support is a single `Połączenia`
collocation realising the `o` phrase without an addressee, not a whole collocation class as with rows
2 and 10, nor direct combined usage as with row 16. The evidence note says so in those words. It is
genuine authoritative usage and it clears the standard, but a human reviewing this corpus should know
it is the least redundantly evidenced acceptance in the set.

No correction event was written for any of the four. They had no standing acceptance to correct —
their earlier classification was a decision not to write one, not a recorded error in the data.

---

## 5. Row 37, `podobać się`

The conclusion that the stimulus-subject analysis is **structurally supported** stands, and is now
better evidenced than in pass 1. The `Składnia` table has a subject column, and the sense's second
schema places a clause in that subject position while `KOMU` stays:

```
[bez ograniczeń]                 + podobać się + KOMU
(to,) że ZDANIE | jak ZDANIE     + podobać się + KOMU
```

The subject slot is structural, not editorial — which is what the original Phase 2B note
("Skladnia names only the KOMU slot") understated. Sense 1's `Połączenia` additionally list
`film, książka, muzyka, piosenka, serial, utwór, występ` among the subjects, so sense 1 covers the
learner treatment (`nie podoba mi się ten film`) directly.

The sense-2 record added in pass 1 is therefore **removed**, and the claim that sense 2 is the reading
the learner example uses is **withdrawn**. The acceptance pins only the sense-1 record.

Row 37 is classified `EXACT-FRAME`: the `Składnia` row `[bez ograniczeń] + podobać się + KOMU`
realises the authored construction, subject column included.

---

## 6. Evidence accounting

Recomputed from the repaired corpus against baseline `HEAD` `681ff69`.

| Measure | Baseline | Final |
|---|---|---|
| Total evidence records | 122 | **122** |
| WSJP records | 46 | **46** |
| Distinct WSJP entry/sense URLs | 34 | **34** |
| Distinct WSJP locator strings | 44 | **44** |
| Mędak + repository records | 76 | 76 |
| **Additions** | — | **0** |
| **Deletions** | — | **0** |
| `checkedAt` changes | — | **46** (every WSJP record, `2026-08-09` → `2026-08-14`) |
| Note rewrites | — | **8** |
| Locator made precise | — | **1** |
| Any other field changed | — | **0** |

The pass-1 addition and its removal cancel exactly, so the final corpus holds the baseline evidence
set. The "123 records / 35 locators" figures reported mid-phase were temporary and are not carried
forward.

The eight note rewrites: `czekać` (records that the `na KOGO/CO` slot is parenthesised as omissible);
`rozmawiać` o-locative (records that `o CZYM` is the sole complement of the plural-subject schema);
`podobać się` (§5); `pomagać`, `dziękować`, `pytać` and both `prosić` records (§4). The one locator
made precise is the second `prosić` record, retitled from `- Polaczenia` to `- Polaczenia i Cytaty`
because its note now rests on both sections.

The two check dates are deliberately left distinguishable: the Mędak demo could not be re-opened, so
re-dating it would assert a check that did not happen.

---

## 7. Governance recorded

`editorialActorRegistry` holds exactly one record:

```json
"priority7-reference-analysis": {
  "human": false,
  "kind": "source-analysis-workflow",
  "roles": ["reference-verification"],
  "namedInPhase": "Priority 7 Phase 4F-A"
}
```

It holds the tier-1 role and nothing else, and names a workflow rather than a vendor or model. The
tier-2 identity was deliberately **not** registered: registering it would imply a review that has not
happened, and its absence is structurally what keeps every row at `reference-verified`.

`releaseMode: solo-maintainer-reference-backed` is on all 45 patterns — the mode declares which chain
governs a row, and had to be assigned before any event, because the default `human-reviewed` chain
refuses a `reference-verification` event outright.

Each of the 45 acceptances is a single actor-borne event pinning **WSJP records only**: no Mędak
record (headword presence proves nothing about a frame) and no repository record (existing app
content establishes what Po polsku teaches, not what Polish requires). 44 events pin one record; the
`prosić` event pins two. Every pin resolves to a current digest, is `contemporary-reference`, and
carries `complement-frame`. Each event note states the support, and exact-frame notes name the
licensing schema, so the audit survives in the data and not only in this report.

---

## 8. The full row-by-row result

Complete detail, including the extracted `Składnia` for every cited locator, is in
[`priority-7-phase-4fa-reference-matrix.csv`](priority-7-phase-4fa-reference-matrix.csv).

| # | Lemma | Pattern | Support | Licensing statement |
|---|---|---|---|---|
| 1 | szukać | genitive-target | EXACT-FRAME | `KOGO/CZEGO + (GDZIE)` |
| 2 | pomagać | dative-recipient | **SUBFRAME** | `Polaczenia: bare Dative recipient class` |
| 3 | pomagać | dative-recipient-w-locative-area | EXACT-FRAME | `KOMU + w CZYM \| przy CZYM` |
| 4 | słuchać | genitive-target | EXACT-FRAME | `KOGO/CZEGO` |
| 5 | słuchać | genitive-object | EXACT-FRAME | `KOGO/CZEGO` |
| 6 | czekać | na-accusative-target | EXACT-FRAME | `(na KOGO/CO)` |
| 7 | potrzebować | genitive-object | EXACT-FRAME | `CZEGO` |
| 8 | uczyć się | genitive-subject-matter | EXACT-FRAME | `CZEGO + (GDZIE)` |
| 9 | uczyć się | infinitive-skill | EXACT-FRAME | `BEZOKOLICZNIK` |
| 10 | dziękować | za-accusative-reason | **SUBFRAME** | `Definicja 'wdziecznosc za cos' + Polaczenia: za-CO class` |
| 11 | dziękować | dative-recipient-za-accusative | EXACT-FRAME | `KOMU + za CO` |
| 12 | płacić | za-accusative-goods | EXACT-FRAME | `(KOMU) + (CZYM) + za CO` |
| 13 | płacić | instrumental-method | EXACT-FRAME | `CZYM + (za CO)` |
| 14 | używać | genitive-object | EXACT-FRAME | `CZEGO + (do CZEGO)` |
| 15 | prosić | o-accusative-request | EXACT-FRAME | `o CO` |
| 16 | prosić | accusative-person-o-accusative-thing | **SUBFRAME** | `Cytaty: Accusative person + o + Accusative in one clause` |
| 17 | interesować się | instrumental-topic | EXACT-FRAME | `CZYM` |
| 18 | dbać | o-accusative-target | EXACT-FRAME | `o KOGO/CO` |
| 19 | tęsknić | za-instrumental-target | EXACT-FRAME | `do KOGO/CZEGO \| za KIM/CZYM` |
| 20 | rozmawiać | z-instrumental-interlocutor | EXACT-FRAME | `z KIM + (o KIM/CZYM)` |
| 21 | rozmawiać | o-locative-topic | EXACT-FRAME | `(o CZYM)` |
| 22 | rozmawiać | z-instrumental-o-locative | EXACT-FRAME | `z KIM + (o KIM/CZYM)` |
| 23 | bać się | genitive-stimulus | EXACT-FRAME | `KOGO/CZEGO` |
| 24 | bać się | o-accusative-concern | EXACT-FRAME | `o KOGO/CO` |
| 25 | być | instrumental-predicate | EXACT-FRAME | `CZYM` |
| 26 | znać | accusative-object | EXACT-FRAME | `KOGO/CO` |
| 27 | lubić | accusative-object | EXACT-FRAME | `CO` |
| 28 | lubić | infinitive-activity | EXACT-FRAME | `BEZOKOLICZNIK` |
| 29 | mówić | dative-recipient-accusative-content | EXACT-FRAME | `(KOMU) + CO` |
| 30 | mówić | dative-recipient-ze-clause | EXACT-FRAME | `(KOMU) + że ZDANIE\|żeby ZDANIE\|ZDANIE PYTAJNOZALEŻNE` |
| 31 | pytać | o-accusative-topic | **SUBFRAME** | `Polaczenia: o phrase with no expressed addressee` |
| 32 | pytać | accusative-person-o-accusative-topic | EXACT-FRAME | `KOGO + o KOGO/CO` |
| 33 | widzieć | accusative-object | EXACT-FRAME | `KOGO/CO` |
| 34 | mieć | accusative-object | EXACT-FRAME | `CO` |
| 35 | myśleć | o-locative-topic | EXACT-FRAME | `(o CZYM \| nad CZYM)` |
| 36 | znaleźć | accusative-object | EXACT-FRAME | `KOGO/CO` |
| 37 | podobać się | nominative-stimulus-dative-experiencer | EXACT-FRAME | `KOMU` (subject column included) |
| 38 | ufać | dative-object | EXACT-FRAME | `KOMU` |
| 39 | wierzyć | dative-object | EXACT-FRAME | `KOMU/CZEMU` |
| 40 | wierzyć | w-accusative-target | EXACT-FRAME | `w KOGO/CO` |
| 41 | zajmować się | instrumental-topic | EXACT-FRAME | `CZYM` |
| 42 | zajmować się | instrumental-object | EXACT-FRAME | `KIM/CZYM` |
| 43 | opiekować się | instrumental-object | EXACT-FRAME | `KIM/CZYM` |
| 44 | zależeć | od-genitive-source | EXACT-FRAME | `od CZEGO` |
| 45 | zależeć | dative-experiencer-na-locative | EXACT-FRAME | `KOMU + na CZYM` |

### Three rows worth reading before approval

- **Row 6 `czekać`** — the `na KOGO/CO` slot is parenthesised, i.e. omissible. The record marks the
  complement `required: true`, which is the model's uniform marking (all 45 patterns use it) and not
  a claim of obligatoriness; the schema's optionality is recorded in the note.
- **Row 1 `szukać`** — the example `Szukam dobrej kawiarni` arguably sits under sense 2 (`pracy`)
  rather than the cited sense 1 (`zaginionego`). Both senses give `KOGO/CZEGO`, so the frame claim is
  unaffected.
- **Row 36 `znaleźć`** — cites sense 2 (`pracę`) while `szukać` cites sense 1, though `znaleźć` also
  has a `zaginionego` sense. Both give `KOGO/CO`, so again the frame claim is unaffected; the sense
  pairing is a human editorial call.

---

## 9. What Phase 4F-A deliberately did not do

| Requirement | Verified |
|---|---|
| Zero editorial-review events | yes — 0, and no editorial actor is registered |
| Zero product-approval events | yes — 0, and no human holds the role |
| No external-verification, native-linguistic, correction or reopen event | yes — 0 of each |
| No pattern above `reference-verified` | yes — all 45 at tier 1 of three |
| Five pending replacement examples not canonicalized | yes — all 23 example origins still `repository-reuse`, zero `editorial-generated`, `authorRegistry` still `{}` |
| No freeze, no runtime, no `releaseAuthorization` | yes — `content/` absent, no frozen/release/tombstone artifact |
| No `patternDataRevision` allocated | yes — the token does not appear in the corpus |
| No shipping file touched | yes — only `editorial/`, `reports/` and `tests/` changed |
| `priority7_tooling.py` unmodified | yes — byte-identical to `HEAD`, asserted in the test suite |
| No linguistic or learner-facing content changed | yes — outside `releaseMode`, `reviewState`, `reviewEvents` and `evidence`, the corpus is identical to `HEAD`, asserted by projection equality with a non-vacuity guard |
| AB unchanged | yes — `["native-linguistic"]`, human, native, no allowances, no new event, ID absent from the corpus |
| No commit, no push, no remote | yes — zero remotes, `push.default=nothing`, pre-push hook installed |
| Phase 4F-B not begun | yes |

The tooling proved sufficient: every fact this phase needed to record was already expressible, so
`priority7_tooling.py` is unmodified and the stop-and-report condition was not triggered.

---

## 10. Validation performed

| Gate | Result |
|---|---|
| Phase 4F-A | **69 passed** |
| Phase 4E.1 | 90 passed |
| Phase 4E | 104 passed |
| Phase 5-A | 112 passed |
| Phase 4C | 55 passed |
| Phase 3F-A | 17 passed |
| Phase 2A | 77 passed |
| Phase 3B / 3C / 3D-1 | 19 / 22 / 44 passed |
| **Full Python** | **784 passed, 0 failed** |
| **Full JXA** | **36 suites, 0 failed** |
| `validate_content.py` | OK — forward baseline sha256 `2a71401d…3a1ce50` unchanged |
| `verify_audio.py` | OK — 3377 phrases, nothing orphaned |
| `build_pages.py --check` | OK — committed output current |
| Editorial validation of the real corpus (CLI) | valid |
| `git diff --check` | clean, working tree and `HEAD^..HEAD` in scratch |
| Committed-scratch survivability | Python + 36 JXA + content + audio + pages + editorial, all pass committed |

Prior-phase boundary assertions across Phases 3B, 3C, 3D-1, 3F-A, 4C, 4E, 4E.1 and 5-A were
retargeted in pass 1 and preserved here; pass 2 changed only the expected counts (41/4 → 45/0,
evidence 123 → 122), leaving the projection-identity assertions and the actor-registry negative
control untouched.

Those inherited suites still resolve their baseline as `git show HEAD:…`, which goes vacuous once a
candidate is committed — a pre-existing pattern in this repository, acknowledged in Phase 5-A's own
docstring and not introduced here. It costs no coverage: the Phase 4F-A suite carries
commit-independent versions of the same three assertions (linguistic projection, tooling unmodified,
no shipping file changed), pinned to `681ff69`.

### Adversarial results

Each probe mutates an in-memory copy of the **real** corpus or context.

| Probe | Result |
|---|---|
| each of the 45 rows downgraded to `research`, one at a time | ✕ `REVIEW_STATE_MISMATCH` (45/45) |
| any subframe row's acceptance removed | ✕ `REVIEW_STATE_MISMATCH` |
| actor registry emptied | ✕ `EDITORIAL_ACTOR_REGISTRY_DANGLING` |
| actor record `human: true` / omitting `human` | ✕ `EDITORIAL_ACTOR_NOT_NONHUMAN` |
| actor given `native-linguistic` | ✕ `EDITORIAL_ACTOR_ROLE_UNKNOWN` |
| actor given only `editorial-review` | ✕ `EDITORIAL_ACTOR_ROLE` |
| actor ID also registered as a reviewer | ✕ `REGISTRY_KEY_COLLISION` |
| AB used as the reference actor | ✕ `EDITORIAL_ACTOR_REGISTRY_DANGLING` |
| pinned evidence edited after acceptance (all four subframe rows + a control) | ✕ `REVIEW_STATE_MISMATCH` |
| pins removed | ✕ `REVIEW_EVIDENCE_REQUIRED` |
| repinned to the Mędak headword record alone | ✕ `REVIEW_CONTEMPORARY_EVIDENCE_REQUIRED` + `REFERENCE_PATTERN_EVIDENCE_REQUIRED` + `REVIEW_STATE_MISMATCH` |
| verified frame edited (`genitive` → `accusative`) | ✕ `REVIEW_STATE_MISMATCH` |
| `releaseMode` deleted / relabelled `human-reviewed` | ✕ `REVIEW_STAGE_NOT_IN_MODE` |
| acceptance relabelled as human `external-verification` | ✕ `REVIEWER_REGISTRY_DANGLING` + `REVIEW_STATE_MISMATCH` |
| acceptance duplicated | ✕ `REVIEW_DUPLICATE_STAGE_ACCEPTANCE` |
| editorial review stacked by the reference actor | ✕ `EDITORIAL_CORROBORATION_SELF` + `REVIEW_ACTOR_INDEPENDENCE` |
| an exact-frame row whose named schema is absent from the extracted table | refused before writing, by the audit script |
| reintroducing the retracted `prosić` claim in any artefact | ✕ regression test |
| reintroducing the `podobać się` sense-2 record | ✕ regression test |

---

## 11. Files changed

| File | Change |
|---|---|
| `editorial/verb-pattern-candidates.json` | `releaseMode` on all 45; 45 reference-verification acceptances; 46 evidence re-dates, 8 note rewrites, 1 locator made precise; net zero additions or deletions |
| `editorial/priority-7-authoring-context.json` | `editorialActorRegistry` created with one nonhuman actor; `contextNotice` and the WSJP source-registry note updated; actor audit metadata records both passes |
| `reports/priority-7-phase-4fa-summary.md` | this document |
| `reports/priority-7-phase-4fa-reference-matrix.csv` | **new** — 45-row audit matrix with `supportKind`, LF line endings |
| `tests/test_priority7_phase4fa.py` | **new** — 69 tests |
| `tests/test_priority7_phase3b.py`, `3c`, `3d1`, `3fa`, `4c`, `4e`, `4e1`, `5a` | boundary assertions retargeted in pass 1; pass 2 changed only the expected counts (41/4 → 45/0, evidence 123 → 122), leaving the projection-identity assertions and the actor-registry negative control untouched |

Not touched: `priority7_tooling.py`, all shipping and browser files, the runtime, generated pages, the
provenance specification.

---

## 12. Limitations — read this before approving anything

`reference-verified` here means: **a nonhuman source-analysis workflow re-opened the cited WSJP PAN
entry on 2026-08-14 and found either a printed `Składnia` schema realising the authored frame, or
authoritative usage in the entry's own `Definicja` / `Połączenia` / `Cytaty` realising the taught
complement.** It is **not human external verification**, not professional linguistic review, and
**not native-speaker review**. No person checked these 45 rows in this phase.

Specific limits:

- The audit compares **complement realisation**. It does not verify pedagogical framing, CEFR levels,
  register, learner explanations or error notes — none is in the tier-1 scope, and all remain
  unreviewed.
- Subframe support establishes that the taught complement is realised in authoritative usage. It does
  **not** establish that the isolated construction is the best thing to teach, or that the omitted
  participants are pedagogically safe to omit. Those are exactly the judgements the editorial and
  product stages exist for.
- Row 31 `pytać` rests on a single collocation rather than a class (§4).
- Sense selection was checked against each entry's sense list, but where two numbered senses give the
  same frame (rows 1, 36) the choice between them is a human editorial judgement this phase did not
  make.
- The Mędak evidence could not be re-opened and carries no weight in any acceptance. The repository
  evidence was re-resolved but establishes what the app teaches, not what Polish requires, and
  carries no weight either.

---

## 13. What the next phase must do

Phase 4F-B was **not** started. Before anything can pass `reference-verified`:

1. Register a **distinct** nonhuman editorial actor plus at least one independent corroborator — the
   solo chain needs three distinct nonhuman identities and currently has one.
2. Register the project owner with `product-approval` and an `acknowledgedReleaseModes` entry naming
   `solo-maintainer-reference-backed`, having read §12.
3. Put the four subframe rows in front of a human. They are reference-verified, not pedagogically
   settled: the question of whether to teach the one-slot subframe or the fuller attested frame is an
   editorial decision, and AB is the obvious person to ask.
4. Decide the sense-selection questions flagged on rows 1 and 36.

---

## 14. Verdict

**GO.**

All 45 patterns are reference-verified and each is defensible from material this phase actually read
and recorded: 41 from a printed schema, 4 from authoritative usage under the locked learner-subframe
architecture. The false `prosić` claim is retracted and regression-guarded, the unnecessary
`podobać się` addition is removed, the evidence accounting is recomputed from the repaired corpus,
and the matrix defect is fixed. No human assurance is claimed anywhere, and every release boundary —
no editorial review, no product approval, no freeze, no runtime, no shipping change — holds.
