# Priority 7 — Phase 4F-C1: Final Example Assessment & Drafting

**Verdict: GO WITH FINDINGS**

The 13-row example queue was assessed in full, every proposed sentence carries a truthful
provenance decision, the canonical corpus is byte-identical to the pinned baseline, and the
blind review package is ready for Codex. Four example questions need adjudication after
independent review; none of them is a governance or copyright defect.

**No sentence in this report is approved.** Every proposal is a C1 draft awaiting independent
review and adjudication. C1 created no review event, registered no actor, and changed no
canonical data.

> **Phase 4F-C1.1 addendum.** The first committed-scratch rehearsal exposed a pre-existing
> Phase 4F-B3B guard that forbade all legitimate later-phase files. It has been repaired to test
> the immutable `7beb50d7 → 080d92ad` transition, with negative controls and mutation testing.
> **The 13-row assessment is substantively unchanged** — same classifications, same proposals,
> same provenance decisions, same four open questions. See **§15**.

---

## 1. Baseline validation

Run before any substantive work.

| Check | Expected | Observed |
|---|---|---|
| Working directory | Phase 4F-C1 repo | `/Users/Kaj/Downloads/Repository for Claude - Priority 7 Phase 4F-C1` |
| Branch | `priority-7-phase-4fc1-example-assessment` | matches |
| HEAD | `080d92ad49a514332f21ecd90b4a11de070a243f` | matches |
| HEAD tree | `74dd8cbebc303b646e4e38e2082d25c91b1cf6e1` | matches |
| Git remotes | zero | zero |
| `push.default` | `nothing` | `nothing` |
| Starting worktree | clean | clean |
| Patterns | 45 | **45** |
| `reviewState` | 45 × `reference-verified` | **45 / 45** |
| `reference-verification` accepts | 47 | **47** |
| `editorial-review` events | 0 | **0** |
| `product-approval` events | 0 | **0** |

| Suite | Result |
|---|---|
| B3B (`test_priority7_phase4fb3b.py`) | pass |
| 4F-A (`test_priority7_phase4fa.py`) | pass |
| 4E.1 (`test_priority7_phase4e1.py`) | pass |
| 5-A (`test_priority7_phase5a.py`) | pass |
| combined baseline run | **408 passed, 0 failed** |
| `validate-editorial` | `Priority 7 private editorial record: valid` |
| `git diff --check` | clean |

Baseline was green, so the phase proceeded.

---

## 2. The exact 13-row queue

| # | Review ID | Lemma | Pattern | Queue history |
|---|---|---|---|---|
| 1 | `P7-NR-007` | potrzebować | Genitive object | B3A example/editorial finding |
| 2 | `P7-NR-011` | dziękować | Dative + za + Accusative | original pending example work |
| 3 | `P7-NR-012` | płacić | za + Accusative | original pending example work |
| 4 | `P7-NR-014` | używać | Genitive object | B3A example/editorial finding |
| 5 | `P7-NR-018` | dbać | o + Accusative | B3A example/editorial finding |
| 6 | `P7-NR-031` | pytać | o + Accusative | B3A example/editorial finding |
| 7 | `P7-NR-032` | pytać | Accusative + o + Accusative | B3A example/editorial finding |
| 8 | `P7-NR-033` | widzieć | Accusative object | original pending example work |
| 9 | `P7-NR-035` | myśleć | o + Locative | B3A example/editorial finding |
| 10 | `P7-NR-036` | znaleźć | Accusative object | B3A example/editorial finding |
| 11 | `P7-NR-042` | zajmować się | Instrumental object | original pending example work |
| 12 | `P7-NR-043` | opiekować się | Instrumental object | B3A example/editorial finding |
| 13 | `P7-NR-044` | zależeć | od + Genitive | original pending example work |

13 rows, 13 distinct canonical pattern IDs, no duplicates, no omissions.

---

## 3. Classification counts

| Classification | Count | Rows |
|---|---|---|
| **MUST CHANGE** | **7** | 031, 032, 035, 036, 042, 043, 044 |
| **USEFUL IMPROVEMENT** | **5** | 007, 011, 012, 018, 033 |
| **NO CHANGE** | **1** | 014 |

| Severity | Count | Rows |
|---|---|---|
| HIGH | 0 | — |
| MEDIUM | 7 | 012, 031, 032, 033, 035, 036, 043 |
| LOW | 5 | 007, 011, 018, 042, 044 |
| NONE | 1 | 014 |

Six of the seven MUST CHANGE rows are MUST CHANGE because the canonical example is **absent**,
not because it is wrong. Only `P7-NR-036` has a present example that should not ship as it
stands.

---

## 4. Every MUST CHANGE row

### `P7-NR-036` — znaleźć + Accusative — `P7-C1-009` — MEDIUM

The only row whose *existing* example fails.

- Current: `W końcu udało mi się znaleźć mieszkanie.` (`repository-reuse`, card
  `a2-describing-past-022` field `ex`).
- `znaleźć` is an infinitive buried under the impersonal `udało mi się` with a Dative clitic,
  so it is not the sentence's teaching verb.
- `mieszkanie` is neuter: its Accusative is identical to its Nominative, so a sentence whose
  whole purpose is "znaleźć takes the Accusative" displays **no Accusative morphology at all**.
- Confirming detail found in C1: the source card `a2-describing-past-022` has the headword
  `udało mi się`. The sentence was authored to teach the impersonal construction, not this verb.

### `P7-NR-031` — pytać o + Accusative — `P7-C1-005` — MEDIUM
No canonical example. A2 core active-production pattern retained in the pilot by B3A partly on
the ground that the short frame is a complete idiomatic utterance; nothing demonstrates that.

### `P7-NR-032` — pytać + Accusative + o + Accusative — `P7-C1-006` — MEDIUM
No canonical example. Carries a predicted-distractor note about the person slot
(`pytam mamie o adres`) that no sentence illustrates.

### `P7-NR-035` — myśleć o + Locative — `P7-C1-008` — MEDIUM
No canonical example and, as B3A found, nothing in the repository can be reused.

### `P7-NR-043` — opiekować się + Instrumental — `P7-C1-011` — MEDIUM
No canonical example, and the verb does not occur anywhere in the shipped corpus — C1 confirmed
this independently. Authored B1/B1 active-production: the learner is expected to produce a
construction the app never shows.

### `P7-NR-042` — zajmować się + Instrumental — `P7-C1-010` — LOW
No canonical example. Severity LOW because the pattern is recognition-only at B1.

### `P7-NR-044` — zależeć od + Genitive — `P7-C1-012` — LOW
No canonical example. Severity LOW because the pattern is clean on both prior reviews and a
strong repository sentence is available.

---

## 5. Every proposed example, with provenance

| Row | Finding | Proposed Polish | Proposed English | Provenance | repositorySource |
|---|---|---|---|---|---|
| 007 | `P7-C1-001` | `Czy potrzebuję antybiotyku?` | Do I need an antibiotic? | **repository-reuse** | card `a2-pharmacy-020` field `ex` |
| 011 | `P7-C1-002` | `Dziękuję siostrze za kolację.` | Thanks to my sister for dinner. | **editorial-generated** | — |
| 012 | `P7-C1-003` | `Płacę za kawę i gazetę.` | I am paying for a coffee and a newspaper. | **editorial-generated** | — |
| 014 | — | *(none — NO CHANGE)* | — | — | — |
| 018 | `P7-C1-004` | `Codziennie dbam o kondycję.` | I take care of my fitness every day. | **editorial-generated** | — |
| 031 | `P7-C1-005` | `Zawsze pytam o cenę.` | I always ask about the price. | **editorial-generated** | — |
| 032 | `P7-C1-006` | `Pytam koleżankę o nową restaurację.` | I am asking my friend about the new restaurant. | **editorial-generated** | — |
| 033 | `P7-C1-007` | `Czy widzisz tę górę na horyzoncie?` | Do you see that mountain on the horizon? | **editorial-generated** | — |
| 035 | `P7-C1-008` | `Ciągle myślę o egzaminie.` | I keep thinking about the exam. | **editorial-generated** | — |
| 036 | `P7-C1-009` | `W końcu znalazłam nową pracę.` | I finally found a new job. | **editorial-generated** | — |
| 042 | `P7-C1-010` | `Kiedy siostra jest w pracy, zajmuję się jej córką.` | When my sister is at work, I look after her daughter. | **editorial-generated** | — |
| 043 | `P7-C1-011` | `Opiekuję się chorą babcią.` | I look after my sick grandmother. | **editorial-generated** | — |
| 044 | `P7-C1-012` | `Czy pójdziemy na spacer? To zależy od pogody.` | Will we go for a walk? It depends on the weather. | **repository-reuse** | card `b1-expressing-opinions-013` field `ex` |

**No proposal uses `origin.kind = "original"`.** No new human-authorship claim was created, and
`authorRegistry` stays empty.

### Rows that successfully reuse repository content — 2

- `P7-NR-007` → card `a2-pharmacy-020` field `ex`
- `P7-NR-044` → card `b1-expressing-opinions-013` field `ex`

Both were verified to resolve **byte-exactly** against the live repository index, which is what
the validator's `REPOSITORY_SOURCE_MISMATCH` check enforces. Neither row needs an editorial
actor.

### Rows that require editorial-generated content — 10

011, 012, 018, 031, 032, 033, 035, 036, 042, 043.

Each of the ten proposed strings was checked against every string field of all 1,665 indexed
repository entities and **none occurs verbatim**, so none is a rewritten repository sentence
being passed off under a new provenance, and none silently duplicates shipped content.

Why repository reuse was impossible on each:

- **011 dziękować** — every repository sentence pairing a Dative noun with `za` + Accusative
  (`grammar-cases-dative-005`, `politeness-formal-address-003`, `people-numbers-every-all-011`)
  stores it in a drill `full` field, which is outside the locked `repositorySource` enum
  (card `pl`/`ex`, drill `prompt`/`answer`).
- **012 płacić** — the only repository sentence combining `płacić` with `za` is the current
  example.
- **018 dbać** — the verb occurs on exactly one card, which supplies the current example.
- **031 / 032 pytać** — the only sentence with `pytać` plus an `o` phrase is slang-marked
  (`b1-everyday-slang-010`); `a2-healthcare-appointments-017` uses the **perfective partner
  `zapytać`**, not the authored imperfective lemma.
- **033 widzieć** — the transparent alternatives (`Widzę kota`, `Widzę tych studentów`) live in
  drill `full` fields.
- **035 myśleć** — `Myślę o wakacjach` is a drill `full` field; `grammar-cases-locative-013` is
  a build drill whose `answer` is an array, which the validator rejects as a sentence source;
  `b1-expressing-opinions-009` realises the **excluded opinion sense**.
- **036 znaleźć** — the alternative `W sieci można znaleźć wszystko` is worse on both counts
  (another impersonal frame, a neuter pronoun object).
- **042 zajmować się** — no repository sentence uses the look-after-a-person sense.
- **043 opiekować się** — the verb does not occur in the repository at all.

---

## 6. Treatment of the five original pending rows

Each was assessed from scratch under the current architecture. The Phase 4C drafts were treated
as **editorial input only**. AB's Phase 4C acceptance is human linguistic acceptance of a text;
it is **not** authorship, and no proposal below is presented as human-authored.

| Row | Phase 4C draft | C1 decision |
|---|---|---|
| `P7-NR-011` | `Dziękuję siostrze za kolację.` | **Carried forward** after fresh assessment. Both cases transparent (`siostrze` Dative, `kolację` Accusative), natural, level-fit. |
| `P7-NR-012` | `Płacę za kawę i gazetę.` | **Carried forward** after fresh assessment. Two overt feminine Accusatives replace a pronoun with no visible case. |
| `P7-NR-033` | `Czy widzisz tę górę na horyzoncie?` | **Carried forward** after fresh assessment. Present tense matches A1/A1; unambiguously the visual-perception sense. |
| `P7-NR-042` | `Kiedy siostra jest w pracy, zajmuję się jej córką.` | **Carried forward** after fresh assessment. The subordinate clause is not padding — it forces the care reading against the occupation sense taught at `P7-NR-041` with the same surface string. |
| `P7-NR-044` | `Nasze plany zależą od pogody.` | **REJECTED** in favour of repository reuse. |

### Rows where an old pending draft was rejected — 1

`P7-NR-044`. The draft `Nasze plany zależą od pogody.` is a good sentence, but
`b1-expressing-opinions-013.ex` already realises the same construction with the identical
governed form `od pogody`, resolves byte-exactly, and is the card the pattern already cites as a
support `contentRef`. Section 8 of the brief prefers strong existing repository content over
new duplicate content. Rejecting the draft also keeps this row free of any editorial-actor
dependency.

---

## 7. Rows given specific treatment by the brief

### `P7-NR-018` — dbać (§11)

B3A's linguistics were re-checked and hold. `o siebie` **does** contrast usefully with `o sobie`,
which is the live confusion in a corpus that teaches `o` + Locative on `rozmawiać` (021) and
`myśleć` (035). It is nonetheless not case-transparent — `siebie` is an irregular pronoun with no
visible Accusative — and B3A's own alternative `o zdrowie` does not fix that, since neuter
Accusative equals Nominative.

C1 proposes the feminine `-ę` noun B3A asked for: `Codziennie dbam o kondycję.` It stays inside
the healthy-lifestyle topic the pattern already cites, so it is not a contrived noun chosen to
display a suffix.

**C1's preferred implementation is to ADD it as a second example and PRESERVE the existing
sentence**, which is literally what B3A recommended. That keeps the Accusative/Locative pronoun
contrast and adds visible noun morphology. The `examples` array has no cardinality limit in the
validator. Replacement is the fallback.

### `P7-NR-035` — myśleć (§12)

The proposal deliberately avoids all three traps: it is not the opinion sense (`sądzić`,
`uważać`), not the intention sense (`zamierzać`, which `myśleć o zmianie pracy` shapes drift
toward), and `myśleć` is the sentence's only verb. Repository was searched first; nothing is
reusable.

### `P7-NR-036` — znaleźć (§13)

Assessed **MUST CHANGE**, as §13 anticipated. The replacement puts `znaleźć` as the finite main
verb in its intended find sense, makes the Accusative visible on both adjective and noun
(`nową pracę`), and stays natural and short. The pattern itself is untouched. The perfective
aspect is respected: `znalazłam` is the past of perfective `znaleźć`, not of imperfective
`znajdować` — which is the documented reason B3A kept production at B1.

### `P7-NR-043` — opiekować się (§14)

Repository footing is not weak — it is **absent**. C1 independently confirmed that the verb
occurs nowhere in the 1,665 indexed entities; the only `opiekow-` hit is the adjective
`opiekuńczy`. A new editorial-generated example is therefore not merely preferable, it is the
only option. The broader `zajmować się` / `opiekować się` teaching-status question is **not**
reopened; the two proposals use different complements so they do not read as a status argument.

### `P7-NR-031` / `P7-NR-032` — pytać (§15)

Reference validity and pilot retention are treated as closed and were not revisited. The two
examples were drafted together so the pedagogical roles stay distinct:

- **031** is the A2 short frame: `Zawsze pytam o cenę.` — one visible Accusative in the topic slot.
- **032** is the B1 full frame: `Pytam koleżankę o nową restaurację.` — the person slot appears
  and is *also* visibly Accusative, which is the whole point of the row.

Lexical content was kept deliberately different so the two patterns cannot read as accidental
duplicates.

### `P7-NR-007` / `P7-NR-014` (§16)

Both B3A findings were re-read against the current canonical examples and they **do not receive
the same disposal**.

- **007 → USEFUL IMPROVEMENT.** The complaint is real: `zaświadczenie z pracy` is bureaucratic
  B1-register vocabulary on a pattern first met at A1 recognition, and `z pracy` adds a second
  Genitive from a different rule. A costless repository-reuse fix exists.
- **014 → NO CHANGE.** The complaint does not survive. Its only concrete content is that the
  sentence is reused from a B1 card while the pattern is A2/A2 — but the sentence's actual lexis
  (`aplikacja`, `nauka`, `język`) and grammar sit at A2, and `tej aplikacji` is an overt Genitive
  standing immediately beside the verb, in direct contrast to the predicted distractor
  `używam tę aplikację`. The A2 alternative (`Będę używać wielorazowych opakowań`) would add a
  compound future and a low-frequency adjective: a net loss against a level-band complaint alone.
  No work was manufactured here.

---

## 8. Copyright and source-boundary confirmation

**CONFIRMED CLEAN.**

- No Mędak example sentence, definition, synonym list or explanation was consulted, reproduced or
  paraphrased in this phase.
- No WSJP PAN example sentence, collocation list, citation or definition was reproduced or
  paraphrased. WSJP locators already recorded in the corpus were read only as evidence metadata
  in the blind package; no source prose was copied into it.
- The ten editorial-generated proposals are independently worded from everyday vocabulary that
  already exists in the project's own corpus domains. None is a lightly paraphrased distinctive
  source example.
- The two repository-reuse proposals point at project-owned content (`data-a2.js`, `data-b1.js`)
  and were verified to match byte-exactly.
- No research or reference text is embedded anywhere as canonical example content.

---

## 9. Canonical state — unchanged

| Item | Before | After |
|---|---|---|
| `editorial/verb-pattern-candidates.json` | baseline | **byte-identical** |
| `editorial/priority-7-authoring-context.json` | baseline | **byte-identical** |
| Patterns | 45 | 45 |
| `reference-verified` | 45 | 45 |
| `editorial-reviewed` | 0 | **0** |
| Approved | 0 | **0** |
| `reference-verification` accepts | 47 | **47** |
| `editorial-review` events | 0 | **0** |
| `product-approval` events | 0 | **0** |
| Canonical examples | 23, all `repository-reuse` | **23, all `repository-reuse`** |
| `authorRegistry` | empty | **empty** |
| `editorialActorRegistry` | 1 actor, `reference-verification` only | **unchanged** |

No editorial actor was registered. No review event of any kind was created. No canonical example
text, `reviewState`, `reviewEvents`, `evidence`, `releaseMode`, `complements`, `meanings`,
`relationType`, CEFR, `teachingStatus` or `activityEligibility` value was touched.

---

## 10. Shipping / runtime boundary

Untouched: `content/verb-patterns.json` (does not exist), `patternDataRevision`, freeze,
`releaseAuthorization`, `APP_VERSION`, `sw.js` caches, all browser/UI files, all audio.
`priority7_tooling.py` is unchanged.

C1 added exactly four files, all non-shipping:

- `reports/priority-7-phase-4fc1-example-matrix.csv`
- `reports/priority-7-phase-4fc1-summary.md`
- `reports/priority-7-phase-4fc1-blind-example-review-input.csv`
- `tests/test_priority7_phase4fc1.py`

---

## 11. Blind review package

`reports/priority-7-phase-4fc1-blind-example-review-input.csv` — 13 rows.

**Contains:** row ID, lemma, aspect, meaning key, intended meaning, meaning scope, pattern ID,
canonical pattern shape, `relationType`, CEFR recognition/production, teaching status, learner
explanation, predicted distractors, current example with its provenance, reference-backed
grammatical facts (review state, release mode, accept count, WSJP/repository locators), a neutral
statement of what the repository search found, and the candidate example with its provenance.

**Deliberately excludes:** C1's classification, severity, finding ID, rationale, naturalness or
transparency assessment, and implementation recommendation. Verified programmatically — no
occurrence of `MUST CHANGE`, `USEFUL IMPROVEMENT`, `NO CHANGE`, any severity token, or any
`P7-C1-` finding ID appears anywhere in the file.

Codex can therefore judge each example on the canonical facts without seeing C1's verdict.

---

## 12. Open questions requiring adjudication

These are the reason the verdict is **GO WITH FINDINGS** rather than GO.

1. **`P7-NR-033` — does the current example realise an excluded sense?** The authored meaning
   explicitly excludes the separately numbered encounter sense, and
   `Widziałam wczoraj twoją siostrę.` — past tense, human object, time adverbial — is most
   naturally read as *running into* someone. C1 is **not certain** and held the row at USEFUL
   IMPROVEMENT. If the adjudicator agrees the encounter reading dominates, this becomes MUST
   CHANGE.
2. **`P7-NR-012` — is USEFUL IMPROVEMENT too lenient?** A `za` + Accusative pattern illustrated
   with `wszystko`, which has no visible Accusative, arguably fails to demonstrate its own
   teaching point. C1 held it at USEFUL IMPROVEMENT because `wszystko` genuinely *is* Accusative
   and the finite verb is unambiguous. A reviewer could reasonably escalate to MUST CHANGE.
3. **`P7-NR-018` — add or replace?** C1 prefers adding the new sentence alongside the existing
   one, preserving the `o siebie` / `o sobie` contrast. This would make it the corpus's first
   two-example pattern. Replacement is the fallback if a one-example convention is preferred.
4. **`P7-NR-044` — is a two-sentence example acceptable?** The repository-reuse candidate is a
   question-and-answer pair, which is longer and structurally unusual for an example slot. If
   that is judged unacceptable, the rejected Phase 4C draft `Nasze plany zależą od pogody.` as
   `editorial-generated` is the fallback — at the cost of an editorial-actor dependency on this
   row.
5. ~~**Phase 4F-B3B's closed-footprint guard blocks committing this candidate.**~~ **RESOLVED**
   in Phase 4F-C1.1 — the guard now tests the immutable `7beb50d7 → 080d92ad` transition. Full
   detail, negative controls and mutation results in §15. No adjudication needed.

### Remaining uncertainty and dependencies

- **Ten rows depend on an editorial actor that does not exist.** `editorial-generated` origin
  requires `generatorRef` plus `adoptedAt`, and the validator resolves `generatorRef` against
  `editorialActorRegistry` demanding `human: false` and the `example-generation` role. The
  registry holds exactly one actor, `priority7-reference-analysis`, which holds
  `reference-verification` **only** — and the architecture requires the reference and editorial
  actors to be **distinct identities**. C2 must register a new nonhuman example-generation actor
  before any of the ten can be stored. C1 correctly did not register one.
- **Example IDs.** Rows 007, 011, 012, 033 and 036 have existing example IDs that can carry new
  wording under the stable-ID specification, with re-minted keys. Rows 031, 032, 035, 042, 043
  and 044 need newly minted IDs.
- **English side.** Proposed English is drafted in the assessment artifact only; no canonical
  English was modified. Two renderings involve a judgement call and are flagged in the matrix:
  `Dziękuję siostrze za kolację.` is rendered "Thanks to my sister for dinner" rather than the
  stilted "I thank my sister", and `koleżankę` is rendered "my friend", dropping the feminine
  marking. Neither adds or removes a participant.
- **Naturalness assurance.** The four sentences carried forward from Phase 4C retain AB's
  recorded linguistic acceptance of the text. The six newly drafted sentences (018, 031, 032,
  035, 036, 043) have **no native-speaker acceptance of any kind**. That is the single largest
  residual risk in this package and is precisely what the blind review is for.
- **An A1-level alternative for `P7-NR-007`** exists (`Ta zupa potrzebuje cebuli.`,
  `a1-fruit-vegetables-017.ex`) and would match the A1 recognition band exactly. C1 did not
  propose it because `potrzebować` with an inanimate subject is contested usage in Polish;
  the recommended sentence keeps a first-person subject. Recorded here so the adjudicator has
  the real choice.

---

## 13. Final validation — real 4F-C1 workspace

Run after the Phase 4F-C1.1 repair. The workspace was never committed; the four C1 artifacts are
untracked additions, `tests/test_priority7_phase4fb3b.py` is modified, and `editorial/` is
byte-identical to baseline.

| Suite (§29) | Result |
|---|---|
| 4F-C1 (`test_priority7_phase4fc1.py`) | **61 passed** |
| B3B, 4F-A, 4E.1, 4E, 5-A, 4C, 3D-1, 3F-A, 2A + 4F-C1 | **775 passed, 0 failed** |
| Full Python (`tests/`) | **991 passed, 0 failed** |
| Full JXA (36 suites) | **36 suites, 0 failed** |
| `validate_content.py` | pass, forward baseline `2a71401d…1ce50` |
| `verify_audio.py` | 3377 phrases / 3377 manifest / 3377 MP3s, nothing orphaned |
| `build_pages.py --check` | committed output current, 32 sitemap URLs |
| `validate-editorial` | `Priority 7 private editorial record: valid` |
| `git diff --check` | clean |
| `git status --porcelain` | four C1 artifacts untracked + `tests/test_priority7_phase4fb3b.py` modified |

---

## 14. Committed-scratch rehearsal

A fresh isolated scratch candidate was created by local clone, its remote removed, and the four
C1 artifacts committed **there only**. The real 4F-C1 workspace was never committed and holds
the four files as untracked additions.

| Check (scratch, C1 as HEAD) | Result |
|---|---|
| Remotes | zero |
| Working tree after commit | clean |
| `git diff --name-only HEAD^ HEAD` | the four C1 files, nothing else |
| C1 suite | **58 passed** |
| Full Python | **979 passed, 1 failed** — the B3B blocker, since repaired; see §15 |
| JXA | **36 suites, 0 failed** |
| `validate_content.py` | pass, forward baseline `2a71401d…1ce50` |
| `verify_audio.py` | 3377 / 3377 / 3377, nothing orphaned |
| `build_pages.py --check` | committed output current, 32 sitemap URLs |
| `validate-editorial` | valid |
| `git diff --check HEAD^ HEAD` | clean (after §14.1) |

### Baseline comparisons remain meaningful after C1 becomes HEAD

Proven directly in the scratch candidate:

| Anchor | Result with C1 as HEAD |
|---|---|
| `git status --porcelain` | *empty* — a status-only guard is now **vacuous** |
| `git diff --name-only HEAD` | *empty* — a HEAD-anchored guard is now **vacuous** |
| `git diff --name-only 080d92ad…` | **the four C1 files** — the pinned guard still has teeth |

Every no-change guard in `tests/test_priority7_phase4fc1.py` folds the pinned-commit diff into
its evidence and asserts the touched set is non-empty before checking it, so none of them can
pass by having nothing to look at. This is why the suite pins the SHA and never resolves `HEAD`.

### 14.1 Defect found and fixed by the rehearsal

`git diff --check HEAD^ HEAD` flagged trailing whitespace on **every line of both CSVs**: Python's
`csv` writer defaults to `\r\n`, and every other CSV in `reports/` is LF. Invisible in the real
workspace because untracked files are not diffed. Both artifacts were regenerated with
`lineterminator="\n"` and now match the repository convention. This is the rehearsal earning its
place.

### 14.2 Known test debt (§28) — Phase 5-A, recorded and not repaired

**Phase 5-A's shipping-file allowlist** uses `git status` only and becomes vacuous after
committed changes. **Not repaired**, as instructed; it remains out of scope.

C1's own guarantees do not depend on it: the C1 suite anchors on the pinned baseline commit
`080d92ad49a514332f21ecd90b4a11de070a243f`, not on the working tree.

---

## 15. Phase 4F-C1.1 — historical B3B footprint guard repair

The first committed-scratch rehearsal surfaced a second, distinct blocker. It has now been
repaired. Nothing in the 13-row assessment changed: the classifications, proposals, provenance
decisions and the four open adjudication questions are exactly as recorded above.

### 15.1 The first committed-scratch failure

`tests/test_priority7_phase4fb3b.py::BaselineFieldDiffTests::test_nothing_outside_the_b3b_footprint_differs_from_baseline`
failed the moment the C1 candidate was committed. Real workspace: **980 passed, 0 failed**.
Committed scratch: **979 passed, 1 failed**. The four extra elements were exactly C1's own
artifacts — nothing canonical, nothing shipping.

### 15.2 Root cause

The guard's helper ran:

```
git diff --name-only 7beb50d7…
```

A **one-revision** diff, which git resolves as *that revision versus the current working tree* —
not versus the B3B checkpoint. So a frozen historical claim was being evaluated against live
state. While C1's files were untracked they were invisible to `git diff` and the set happened to
equal B3B's footprint; committing them put them in the diff, where the *closed* `B3B_FOOTPRINT`
frozenset rejected them.

The defect is the pairing, not either half: a **closed** expected set compared against a **live**
subject. A completed phase cannot enumerate the files its successors are entitled to add, so the
guard forbade all legitimate future phase files.

### 15.3 The repair

Both endpoints of the transition are now named. `080d92ad` is a **direct child** of `7beb50d7`,
so B3B is a single commit and its diff is a constant:

| | Before | After |
|---|---|---|
| Subject | `7beb50d7 → working tree` | `7beb50d7 → 080d92ad` |
| Assertion | containment + modified-subset | **exact set equality** |
| Grows with later phases | yes — the bug | no |

- New `B3B_CHECKPOINT = "080d92ad…"` constant, and a new
  `test_the_checkpoint_is_the_commit_b3b_produced` asserting the parent link, so the endpoints
  cannot be mismatched.
- New module-level `transition_footprint(repository, baseline, checkpoint)` helper, shared by the
  real guard and the regressions so the latter drive the real body rather than restating it.
- `changed_since_baseline()` → `changed_across_the_b3b_transition()`, consumed by both the
  footprint guard and `test_the_corpus_is_the_only_canonical_content_file_changed`.

Because the subject is now a constant, the guard became an **equality** — strictly stronger than
the containment test it replaces, which could only assert containment precisely because its
working-tree side was not knowable in advance.

**`B3B_FOOTPRINT` was not widened.** It still holds exactly the 11 approved paths, no C1 file was
added to it, and no generic "future phases may add files" exclusion was introduced. The guard
proves history; it does not redefine B3B to include C1.

### 15.4 Negative control (§4)

Five regressions in `HistoricalFootprintRegressionTests` replay a three-commit history —
baseline → B3B checkpoint → later phase — in a throwaway repository and call the *same*
`transition_footprint` body the real guard calls:

| Regression | Proves |
|---|---|
| `test_the_replay_reproduces_the_real_approved_footprint` | the replay is faithful, so the rest cannot pass vacuously |
| `test_an_unauthorised_file_inside_the_transition_is_caught` | a shipping file edited **inside** the transition is detected — B3B history stays exact |
| `test_later_phase_files_do_not_alter_the_historical_result` | four real C1 paths committed **after** the checkpoint leave the answer unmoved |
| `test_later_phase_files_are_still_absent_from_the_footprint` | the repair was not achieved by widening the constant |
| `test_the_superseded_one_revision_form_forbade_the_later_phase` | kept executable: the removed expression, on the same history, still reports the later phase's four files as violations |

Independently mutation-tested. Two mutants were built and run against the real repository:

| Mutant | Result |
|---|---|
| `B3B_CHECKPOINT` re-pointed at the baseline (empty transition) | **2 tests fail** |
| `B3B_FOOTPRINT` widened with one C1 report — the tempting non-fix | **5 tests fail**, including all three behavioural regressions |

The equality is therefore not trivially true.

### 15.5 Same-bug search (§5)

Every `git diff` and `git status` comparison in the Priority 7 test suites was examined. The
failure mode needs **both** a closed expected set and a live comparison subject.

| Suite | Form | Verdict |
|---|---|---|
| **4F-B3B** | closed frozenset vs **working tree** | **the bug — repaired here** |
| 4F-A `test_no_shipping_file_was_modified` | prefix allowlist vs baseline→HEAD + status | Not the bug. Prefix allowlist tolerates later `tests/`/`reports/` files by construction. |
| 5-A shipping allowlist | prefix allowlist vs `git status` only | Separate, already-recorded debt. Goes vacuous rather than over-strict. Out of scope. |
| 2A production-baseline guards | `git diff --exit-code <base> -- <explicit paths>` | Not the bug. Path-scoped, so new files cannot enter the comparison. |
| 3F-A release reference | `git diff --quiet HEAD^ HEAD -- <paths>` | Not the bug. Path-scoped release helper, not a footprint claim. |
| C1 `C1_FOOTPRINT_PREFIXES` | prefix allowlist vs working tree + status | Not the bug, and deliberately so — see §15.6. |

**No genuine additional occurrence.** B3B was the only guard combining a closed set with a live
subject; `B3B_FOOTPRINT` is the only closed footprint constant in the suites.

### 15.6 Current-state protection is unaffected (§3)

The repaired B3B guard no longer looks at the working tree, so C1's suite was audited to confirm
it independently proves the live boundary. Every required protection was already present:

| §3 requirement | C1 test |
|---|---|
| canonical corpus unchanged from `080d92ad` | `test_corpus_is_byte_identical_to_baseline` |
| authoring context unchanged | `test_authoring_context_is_byte_identical_to_baseline` |
| no examples canonically changed | `test_canonical_examples_are_unchanged` |
| no review events added | `test_no_review_event_of_any_kind_was_added` |
| no shipping/runtime change | `test_shipping_sentinels_are_byte_identical_to_baseline`, `test_no_runtime_pattern_payload_was_created`, `test_no_audio_was_generated` |
| only C1 artifacts introduced | `test_c1_footprint_is_reports_and_tests_only`, `test_editorial_directory_does_not_appear_in_the_c1_footprint` |

Nothing was missing, so nothing was moved into the historical guard. One cross-check was added —
`test_the_b3b_historical_footprint_was_not_widened_for_c1` — which asserts from *outside* the
edited module that `B3B_FOOTPRINT` still has 11 entries, that B3B's checkpoint is exactly C1's
baseline, and that none of C1's four artifacts was smuggled into it.

`C1_FOOTPRINT_PREFIXES` is deliberately a **prefix** allowlist, not a closed set. That is the
lesson of this repair applied forward: C1 cannot enumerate what its own successors may add, so
its live boundary stays open at the prefix level while exactness lives in the frozen-history
guard.

Note that `tests/test_priority7_phase4fb3b.py` legitimately appears in *both* sets — B3B created
it, C1.1 edited it. Creation is not authorship of the later edit, and the historical footprint
records only the creation.

### 15.7 C1.1 candidate scope

| Path | Change |
|---|---|
| `tests/test_priority7_phase4fb3b.py` | **modified** — the repair and its regressions |
| `tests/test_priority7_phase4fc1.py` | **modified** — the anti-widening cross-check |
| `reports/priority-7-phase-4fc1-summary.md` | **modified** — this section |
| `reports/priority-7-phase-4fc1-example-matrix.csv` | unchanged |
| `reports/priority-7-phase-4fc1-blind-example-review-input.csv` | unchanged |

No other path. No canonical data, no review events, no evidence, no tooling, no shipping file.

### 15.8 Final committed-scratch result

The first scratch candidate was discarded, not reused. A fresh clone was taken from the final
C1.1 candidate, its remote removed, and all five files committed there only. The real workspace
remains uncommitted.

| Check (fresh scratch, C1.1 as HEAD) | Result |
|---|---|
| Remotes | zero |
| Working tree after commit | clean |
| `git diff --name-only HEAD^ HEAD` | the five C1.1 files, nothing else |
| `git diff --check HEAD^ HEAD` | clean |
| **`test_nothing_outside_the_b3b_footprint_differs_from_baseline`** | **PASSED** |
| B3B suite | **128 passed** |
| C1 suite | **61 passed** |
| Full Python | **991 passed, 0 failed** — identical to the real workspace |
| Full JXA | **36 suites, 0 failed** |
| `validate_content.py` | pass, forward baseline `2a71401d…1ce50` |
| `verify_audio.py` | 3377 / 3377 / 3377, nothing orphaned |
| `build_pages.py --check` | committed output current, 32 sitemap URLs |
| `validate-editorial` | valid |

The committed and uncommitted states now agree exactly at **991 passed, 0 failed**. Before the
repair they diverged — 980/0 uncommitted against 979/1 committed — which was the whole symptom.

### 15.9 Negative control against the real B3B transition

The strongest available check, run outside the candidate. A throwaway clone was rewound to
`080d92ad`, an unauthorised line was appended to `priority7_tooling.py`, and the commit was
amended — producing a tampered checkpoint that **keeps the real parent `7beb50d7`**. The repaired
guard was then loaded from the C1.1 candidate and pointed at that repository:

| Transition | `== B3B_FOOTPRINT` |
|---|---|
| `7beb50d7 → 080d92ad` (real) | **True** |
| `7beb50d7 → tampered` (shipping file edited inside the transition) | **False** |

Unauthorised path detected: `priority7_tooling.py`. `B3B_FOOTPRINT` still holds exactly 11
entries. B3B's history is frozen and exact; later phases are free to exist.

---

## 16. Verdict

**GO WITH FINDINGS.**

The 13-row example assessment is complete. Proposed example work is provenance-safe: two rows
reuse exactly-resolving repository content, ten are truthfully marked `editorial-generated`, and
no new `original` human-authorship claim was created. Canonical state is untouched — 45
reference-verified, 47 reference accepts, 0 editorial-review, 0 product-approval. Copyright and
source boundaries were not crossed. The blind review package is ready for Codex.

Four example questions listed in §12 need adjudication after independent review, ten rows carry
an editorial-actor dependency that C2 must satisfy, and and the pre-existing Phase 4F-B3B guard that
blocked committing this candidate has been repaired in Phase 4F-C1.1 (§15). **Do not begin Phase 4F-C2
until independent review has run.**
