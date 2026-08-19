# Priority 7 — Phase 4F-C1C: Independent Example Review Adjudication

**Verdict: GO**

All 13 example decisions are adjudicated, each carries an exact C2 implementation plan with a
truthful provenance decision, and no owner decision remains open.

This phase is **adjudication only**. No canonical example, review event, actor, evidence record,
CEFR value, teaching status or ID was created or changed. `editorial/verb-pattern-candidates.json`
and `editorial/priority-7-authoring-context.json` are byte-identical to baseline
`080d92ad49a514332f21ecd90b4a11de070a243f`. **C2 has not begun.**

---

## 1. Reconstruction of both reviews

| Check | Expected | Observed |
|---|---|---|
| Working directory | Phase 4F-C1C repo | matches |
| Branch | `priority-7-phase-4fc1c-example-adjudication` | matches |
| HEAD | `080d92ad49a514332f21ecd90b4a11de070a243f` | matches |
| HEAD tree | `74dd8cbebc303b646e4e38e2082d25c91b1cf6e1` | matches |
| Git remotes | zero | zero |
| `push.default` | `nothing` | `nothing` |
| Blind-input SHA-256 | `0af6c076be5c…c45771` | **matches exactly** |
| C1 matrix rows | 13 | **13** |
| C1B matrix rows | 13 | **13** |
| Review ID sets | identical | **identical** |
| Canonical pattern IDs | 13 distinct, identical across both | **13 distinct, identical** |
| Duplicates / omissions | none | **none** |

All 13 canonical pattern IDs resolve in the corpus, and both reviews' descriptors agree with the
live canonical facts. Every `currentPolish`, `currentEnglish`, `currentOrigin`,
`currentRepositorySource` and example-presence claim was checked field-by-field against
`editorial/verb-pattern-candidates.json`: **the two reviews agree with each other and with the
corpus on every current-example fact.** Seven patterns hold one example each; six hold none.

Reconstruction completed before any adjudication.

---

## 2. Cross-review comparison

| Class | Count | Rows |
|---|---:|---|
| **EXACT AGREEMENT** | **5** | 014, 031, 032, 035, 043 |
| **COMPATIBLE DIFFERENCE** | **5** | 011, 012, 036, 042, 044 |
| **SUBSTANTIVE DISAGREEMENT** | **3** | 007, 018, 033 |

The three substantive disagreements:

- **007** — C1 recommends a canonical edit (`USEFUL IMPROVEMENT`, replace with a repository
  sentence); C1B recommends none (`NO CHANGE`, `REJECT PROPOSAL`). A canonical edit is actually
  recommended on one side and refused on the other, so this is substantive, not compatible.
- **018** — same classification, same severity and the same Polish on both sides, but different
  canonical outcomes: C1's *preferred* implementation is **ADD** (keep `o siebie`, add the new
  sentence), C1B assumes replacement. The two produce different corpora.
- **033** — `USEFUL IMPROVEMENT` / `MEDIUM` against `MUST CHANGE` / `HIGH`, and different remedy
  text. This is the row carrying C1B's only HIGH finding.

The five compatible differences are severity-band or English-wording differences that do not
change the canonical outcome, plus 036, where the classifications differ but both reviews
recommend the identical replacement sentence.

---

## 3. Final classification and severity

| Classification | Count | Rows |
|---|---:|---|
| **MUST CHANGE** | **10** | 012, 018, 031, 032, 033, 035, 036, 042, 043, 044 |
| **USEFUL IMPROVEMENT** | **1** | 011 |
| **NO CHANGE** | **2** | 007, 014 |

| Severity | Count | Rows |
|---|---:|---|
| HIGH | **0** | — |
| MEDIUM | **10** | 012, 018, 031, 032, 033, 035, 036, 042, 043, 044 |
| LOW | **1** | 011 |
| NONE | **2** | 007, 014 |

These describe the adjudicated current-example problem, not reviewer history.

### The criterion behind the escalations

Three present examples were escalated relative to one or both reviews on a single stated test:
**is the taught case visible anywhere a learner can see it?** Section 24 forbids editing
`learnerExplanationEn` or `errorNotes`, so the example is the only lever. Checking all 13 patterns,
exactly three fail the test on every surface at once:

| Row | Example | `learnerExplanationEn` | `errorNotes` | Verdict |
|---|---|---|---|---|
| **012** płacić | `za wszystko` — Acc = Nom | `płacę za bilet` — Acc = Nom | *empty* | case never visible |
| **018** dbać | `o siebie` — no morphology | `dbam o zdrowie` — Acc = Nom | *empty* | case never visible |
| **036** znaleźć | `mieszkanie` — Acc = Nom | *(contrast with szukać)* | `znaleźć mieszkanie` — Acc = Nom | case never visible |

The other ten patterns show the taught case on at least one surface, which is why 007, 011 and 014
are not escalated: 007's example carries a visible Genitive, 011's errorNote carries a visible
Dative (`mamie`) beside a visible Accusative in the example, and 014's example carries a visible
Genitive that its errorNote corrects directly.

---

## 4. Final disposition

| Disposition | Count | Rows |
|---|---:|---|
| **KEEP CURRENT** | **2** | 007, 014 |
| **REPLACE** | **5** | 011, 012, 018, 033, 036 |
| **ADD** | **0** | — |
| **CREATE** | **6** | 031, 032, 035, 042, 043, 044 |
| **NO IMPLEMENTATION YET** | **0** | — |

| Implementation priority | Count | Rows |
|---|---:|---|
| **REQUIRED FOR EDITORIAL ACCEPTANCE** | **10** | 012, 018, 031, 032, 033, 035, 036, 042, 043, 044 |
| **OPTIONAL POLISH** | **1** | 011 |
| **NOT APPLICABLE** (no change) | **2** | 007, 014 |

Exactly one row is optional, so optional polishing blocks nothing.

### ADD is not available in this product

**No row is dispositioned ADD, and the reason is architectural rather than editorial.** The
validator has no cardinality limit on `examples` — but the product renders exactly one:

- `pp-verb-patterns.js:1170` projects `pattern.examples[0]` into a **singular** view-model
  `example` object;
- `index.html:4190–4195` renders that one object as one `vp-example-pl` / `vp-example-en` pair;
- `tests/test_priority7_patterns_ui.js:376` takes `pattern.examples[0]` likewise;
- all **23** existing canonical examples sit one per pattern — there is no precedent either.

A second array element would be silently dropped and never reach a learner. Under section 9 that
settles it: only one canonical example is supported, so the stronger single example is chosen
rather than an unsupported addition mechanism. Neither review checked the runtime projection;
both reasoned from the validator alone and concluded multiple examples were supported.

---

## 5. Every final canonical example

| Row | Lemma | Final Polish | Final English | Origin | repositorySource |
|---|---|---|---|---|---|
| 007 | potrzebować | `Potrzebuję zaświadczenia z pracy.` | I need a certificate from work. | **repository-reuse** *(unchanged)* | card `a2-official-matters-019` field `ex` |
| 011 | dziękować | `Dziękuję siostrze za kolację.` | I thank my sister for dinner. | **editorial-generated** | — |
| 012 | płacić | `Płacę za kawę i gazetę.` | I am paying for a coffee and a newspaper. | **editorial-generated** | — |
| 014 | używać | `Używam tej aplikacji do nauki języków.` | I use this app for learning languages. | **repository-reuse** *(unchanged)* | card `b1-media-technology-001` field `ex` |
| 018 | dbać | `Codziennie dbam o kondycję.` | I look after my fitness every day. | **editorial-generated** | — |
| 031 | pytać | `Zawsze pytam o cenę.` | I always ask about the price. | **editorial-generated** | — |
| 032 | pytać | `Pytam koleżankę o nową restaurację.` | I am asking my friend about the new restaurant. | **editorial-generated** | — |
| 033 | widzieć | `Czy widzisz tę górę?` | Do you see that mountain? | **editorial-generated** | — |
| 035 | myśleć | `Ciągle myślę o egzaminie.` | I keep thinking about the exam. | **editorial-generated** | — |
| 036 | znaleźć | `W końcu znalazłam nową pracę.` | I finally found a new job. | **editorial-generated** | — |
| 042 | zajmować się | `Kiedy siostra jest w pracy, zajmuję się jej córką.` | When my sister is at work, I look after her daughter. | **editorial-generated** | — |
| 043 | opiekować się | `Opiekuję się chorą babcią.` | I look after my sick grandmother. | **editorial-generated** | — |
| 044 | zależeć | `Nasze plany zależą od pogody.` | Our plans depend on the weather. | **editorial-generated** | — |

**No final origin is `original`.** No human-authorship claim is created and `authorRegistry` stays
empty.

### Repository-reuse sources — 2, both re-resolved

Both are the current canonical examples on the two KEEP CURRENT rows, verified again in this phase
rather than taken from either review's claim:

| Row | Source | `pl` byte-exact | Card `exEn` matches canonical `en` |
|---|---|---|---|
| 007 | card `a2-official-matters-019` field `ex` | ✅ | ✅ |
| 014 | card `b1-media-technology-001` field `ex` | ✅ | ✅ |

Both reviews' *proposed* reuse sources were also re-resolved independently and both do resolve
byte-exactly — `card:a2-pharmacy-020.ex` for 007 and `card:b1-expressing-opinions-013.ex` for 044 —
so neither review made a false provenance claim. Both proposals were nevertheless rejected on
editorial grounds, set out in §7 and §10 below.

### Editorial-generated examples — 11

011, 012, 018, 031, 032, 033, 035, 036, 042, 043, 044.

Every one was checked against **all 27,498 strings in the 1,665 indexed repository entities** and
**all 2,532 strings in the canonical corpus**, verbatim and as a substring. **None occurs.** No
sentence is a rewritten or trimmed repository string being passed off under a new provenance, and
none silently duplicates shipped content. None is copied or paraphrased from WSJP PAN or Mędak: no
source example sentence, definition, collocation list or citation was consulted or reproduced in
this phase. Each carries `origin.kind = "editorial-generated"` with an absent `repositorySource`,
as the schema requires.

---

## 6. Rows where the C1 proposal changed after C1B — 5

| Row | C1 proposal | Final | What changed |
|---|---|---|---|
| **007** | replace with `Czy potrzebuję antybiotyku?` (repository-reuse) | **KEEP CURRENT** | Proposal dropped entirely. |
| **011** | *Thanks to my sister for dinner.* | *I thank my sister for dinner.* | English only; Polish unchanged. |
| **018** | **ADD** `Codziennie dbam o kondycję.` / *I take care of my fitness every day.* | **REPLACE**, *I look after my fitness every day.* | Disposition and English; Polish unchanged. |
| **033** | `Czy widzisz tę górę na horyzoncie?` | `Czy widzisz tę górę?` | Polish and English shortened. |
| **044** | `Czy pójdziemy na spacer? To zależy od pogody.` (repository-reuse) | `Nasze plany zależą od pogody.` (editorial-generated) | Text and origin both changed. |

Eight rows carry C1's proposal unchanged: 012, 014, 031, 032, 035, 036, 042, 043.

C1B's recommendation was not followed on three rows: **011** and **018**, where C1B's revised
English was rejected, and **044**, where C1B accepted the two-sentence repository reuse.

---

## 7. The four rows the brief singles out

### `P7-NR-012` — płacić — is `wszystko` too opaque? (§8)

**Yes, and the row is escalated to MUST CHANGE / REQUIRED — beyond both reviews.**

`wszystko` is unambiguously a grammatically valid Accusative here, and it even discriminates
against the live `za` + Instrumental competitor, since that would be `za wszystkim`. It is
nonetheless a poor example *for teaching the case*, which is the distinction section 8 asks for:
its Accusative is identical to its Nominative, so no learner can extract an ending from it.

What makes it REQUIRED rather than polish is that **nothing else in the pattern shows the ending
either**: `learnerExplanationEn` illustrates with `płacę za bilet` — masculine inanimate, Accusative
again identical to Nominative — and `errorNotes` is empty. Section 24 forbids touching either. A
learner told "za + Accusative" and shown only citation forms will produce *Płacę za kawa*. That is a
concrete predicted error caused by the canonical example.

`Płacę za kawę i gazetę.` shows two overt feminine Accusatives coordinated under one preposition,
in A1 vocabulary, in the shopping situation the pattern's own contentRef cites. Repository reuse is
impossible: of the 15 repository sentences using płacić, only `a1-numbers-prices-015.ex` combines
the verb with `za`, and that is the current example; the rest use the Instrumental means-of-payment
frame, which is a different pattern.

### `P7-NR-018` — dbać — replace, add or keep? (§9)

**REPLACE.** ADD was C1's preferred outcome and is not implementable — see §4. The product renders
`examples[0]` only, so a second example would be invisible to learners while still carrying full
provenance and review obligations.

With only one example supported, the stronger single example wins. The current `Warto dbać o siebie
każdego dnia.` is natural, on-meaning, and its `o siebie` does contrast usefully with the `o sobie`
of `rozmawiać` (021) and `myśleć` (035) — which is why severity is MEDIUM and not higher. But the
verb is an infinitive under impersonal `warto`, `siebie` is an irregular pronoun identical in
Accusative and Genitive, and `każdego dnia` adds an adverbial Genitive. On a **B1
active-production** pattern the learner is expected to produce, and with the explanation
(`dbam o zdrowie`, neuter) and an empty errorNote list both failing to show the ending, the example
must carry it. `Codziennie dbam o kondycję.` does, in a standard collocation inside the
healthy-lifestyle topic the pattern already cites.

The English is a third synthesis. C1's *I take care of my fitness* is not idiomatic — C1B was right
about that. C1B's *I make an effort to stay fit every day* deletes the object and turns a
prepositional-object frame into an infinitival purpose clause, which section 19 forbids on a pattern
whose lesson is that object's case. *Look after* is one of the pattern's own authored glosses, is
idiomatic, and keeps the object.

### `P7-NR-033` — widzieć — enhanced scrutiny (§7)

**MUST CHANGE / MEDIUM / REPLACE with `Czy widzisz tę górę?`** The shared concern is upheld. C1B's
HIGH is not.

Investigating the sense boundary rather than deferring to the convergence: in Polish the excluded
encounter sense is normally carried by **`widzieć się z kimś`** — reflexive `się` plus `z` +
Instrumental — so the bare Accusative frame of `Widziałam wczoraj twoją siostrę.` does lean
perceptual, and the Polish is not as compromised as a HIGH finding implies. C1's recorded
uncertainty was well placed.

What is decisive is a set of facts neither review assembled:

1. **The English gloss is the leak.** *I saw your sister yesterday* reads in English as an
   encounter. The learner-facing pair therefore does teach the excluded sense on one side, even
   though the Polish leans the other way.
2. **The source card was written to teach something else.** `a2-describing-past-005` has the
   headword `widziałem` and the hint *czas przeszły od 'widzieć'* — it exists to teach the past
   tense, not this pattern's Accusative object.
3. **The level does not fit.** The pattern is A1/A1; the sentence is a past-tense feminine form.

Case transparency is excellent in the current sentence and was never the complaint.

Between the two proposals, C1B's shortening wins on section 7's own terms. The visual reading is
made unavoidable by the **inanimate geographic object** — a mountain cannot be met, visited or
encountered — not by the location phrase. Dropping `na horyzoncie` therefore costs no sense-safety
while removing above-band vocabulary and a stem-softening Locative from an A1 example. `tę górę`
keeps the Accusative visible on both demonstrative and noun, and standard `tę` rather than
colloquial `tą` is itself a teaching point, consistent with the existing canonical
`Czy znasz tę restaurację?`.

Repository reuse re-confirmed impossible, correcting C1B on the facts: `Na wsi widzieliśmy konie.`
has a plural whose Accusative equals its Nominative; `Bardzo się cieszę, że cię widzę.` hides the
case in a pronoun; `Cześć, dawno się nie widzieliśmy!` is a negated reciprocal idiom; and
`Widzę kota` / `Widzę tych studentów` sit in drill **`full`** fields, which are outside the locked
`repositorySource` enum (card `pl`/`ex`, drill `prompt`/`answer`) — their prompts are gapped
(`Widzę ___ .`). C1B described these as "reusable drills"; they are not. No sentence
`Widzę kobietę` exists anywhere in the repository.

### `P7-NR-044` — zależeć — is a two-sentence example appropriate? (§10)

**Technically yes, editorially no.** This is the one row where **both** reviews are overruled.

- **Schema permits it.** `example.pl` is validated only as a non-empty string of at least three
  characters. There is no sentence-count constraint. C1B's schema reading is correct.
- **The corpus has no precedent.** All **23** existing canonical examples are single sentences.
- **The runtime renders it badly.** `index.html:4192` puts `example.pl` into a single `<p>`, so a
  question-and-answer pair arrives as one run-on line.
- **The first sentence teaches nothing about this pattern.** `Czy pójdziemy na spacer?` belongs to a
  different verb and injects an **Accusative** (`na spacer`) under a different preposition into an
  example whose entire subject is the Genitive after `od` — precisely what section 16 warns against.
- **`To zależy od pogody.` is a complete idiomatic utterance on its own**, so the construction is
  taught just as clearly without the set-up.

Trimming is not available as reuse: repository-reuse requires byte-exact equality with the card
field, and claiming a trimmed substring as `editorial-generated` would be a false provenance.

So the Phase 4C draft **B-20** that C1 rejected is adopted: `Nasze plany zależą od pogody.` It is a
single clause with a lexical subject that shows the full *X zależy od Y* argument structure rather
than the dummy `To`, it has one governed complement and no competing case, it duplicates no
repository content, and it carries AB's recorded Phase 4C linguistic acceptance of the text.

C1's stated reason for preferring reuse — keeping this row free of an editorial-actor dependency —
carries no weight once the queue is seen whole: **ten other rows already require that actor**, so C2
must register it regardless, and this row adds no new governance step.

---

## 8. The remaining rows

### `P7-NR-007` / `P7-NR-014` — originally low-risk (§14)

Both **KEEP CURRENT**. No edit was manufactured.

**014** is EXACT AGREEMENT and the evidence sustains it. The one repository alternative,
`a2-ecology-024.ex` *Będę używać wielorazowych opakowań.*, is a net loss: compound future,
low-frequency adjective, and a plural Genitive — exactly the plural Genitive/Accusative ambiguity
section 16 flags.

**007** is a substantive disagreement resolved for C1B, on a ground C1B did not give. C1's
`Czy potrzebuję antybiotyku?` is a real, byte-exact repository sentence and is marginally more
transparent. But **the pattern's errorNote is built on the current example's noun** —
`potrzebuję zaświadczenie` → `potrzebuję zaświadczenia` — and section 24 forbids editing errorNotes.
Replacing the example would leave an antibiotic example beside a certificate error note, decoupling
a working minimal pair for a modest register gain. C1's CEFR complaint also measures the sentence
against the A1 **recognition** band when it sits at the A2 **production** band, and the second
Genitive from `z pracy` follows the object, so attribution stays clear in reading order.

### `P7-NR-031` / `P7-NR-032` — pytać, reviewed together (§13)

Both **CREATE**, both EXACT AGREEMENT, both proposals adopted unchanged. The decision to keep
P7-NR-031 in the pilot was not reopened. The two do not collapse: **031** shows the topic-only frame
with a single Accusative (`o cenę`); **032** adds the person slot and shows that it is *also*
Accusative (`koleżankę … o nową restaurację`). The lexis is disjoint, and both differ from the
errorNote's `pytam mamie o adres` → `pytam mamę o adres`, so the learner meets the frame with three
vocabulary sets.

Noted and accepted on **031**: `Zawsze pytam o cenę.` restates the pattern's own
`learnerExplanationEn` illustration with an adverb. A different noun was considered so the example
would generalise the frame, but every natural A2 candidate was worse — `o drogę` forces the English
*ask for directions*, collapsing `pytać o` into `prosić o` (a separate pattern in the same corpus),
and `o godzinę` is an odd standalone habit. Weakening the Polish to avoid an echo would be the
artificiality section 16 warns against.

### `P7-NR-035` / `P7-NR-043` — missing examples (§12)

Both patterns are **sound and are not downgraded**; only the example was missing. Pattern validity
and example availability were kept apart throughout.

- **035 myśleć** — repository reuse re-confirmed impossible: `grammar-cases-locative-006` holds
  *Myślę o wakacjach.* in its **`full`** field with a gapped prompt and a one-word answer;
  `grammar-cases-locative-013` has an **array** answer the validator rejects as a sentence source;
  `b1-expressing-opinions-009` realises the excluded opinion sense; `podcasts-work-life-012.ex` is
  negated and subordinate. `Ciągle myślę o egzaminie.` also complements the pattern's own surfaces,
  which both use the plural `wakacjach`, so the learner meets the Locative in both numbers.
- **043 opiekować się** — reuse is not weak but **impossible**: the verb occurs nowhere in the 1,665
  indexed entities; the only `opiek-` hit is the adjective `opiekuńczy`. The shared noun with the
  explanation and errorNote is deliberate: the note is a minimal pair
  (`opiekuję się o babcię` → `opiekuję się babcią`) and an example showing `babcią` completes its
  correct half.

### `P7-NR-042` — zajmować się

**CREATE**, C1's sentence adopted, C1B's **MEDIUM** severity adopted over C1's LOW. Section 20 is
explicit that severity describes the adjudicated problem, not the ease of fixing it: C1 set LOW
because the pattern is recognition-only, but *recognition* is exactly what needs an instance here.
This meaning exists in the corpus only to be told apart from the same lemma's occupation-activity
meaning; the two have **identical government** (bare Instrumental); and the `learnerExplanationEn`
asserts the difference in one sentence without ever showing it. The subordinate clause
`Kiedy siostra jest w pracy` is doing that work and is not padding — a bare human Instrumental does
not by itself block the occupation reading (`zajmuję się dziećmi` can be an occupation). Eight words
is above the corpus norm but the pattern is recognition-only, so the learner never produces it.

### `P7-NR-036` — znaleźć (§11)

The strong presumption is met and the corpus confirms both counts: `znaleźć` is an infinitive buried
under impersonal `udało mi się` with a Dative clitic, and the source card `a2-describing-past-022`
has the headword **`udało mi się`** and the hint *konstrukcja nieosobowa + celownik* — it was
authored to teach the impersonal frame, not this verb; and `mieszkanie` is neuter, so the sentence
displays no Accusative at all. C1's **MUST CHANGE** is the correct classification against C1B's
USEFUL IMPROVEMENT. `W końcu znalazłam nową pracę.` puts the verb finite and first, shows the
Accusative on adjective and noun, and lands on the exact WSJP sense the reference verification
accepted (the recorded locator is the `pracę` sense). Accepted cost: the errorNote keeps
`mieszkanie` and section 24 forbids editing it — a net gain here, since the note covers the neuter
over-application trap while the example now covers the visible feminine Accusative.

---

## 9. Naturalness, case transparency, CEFR

Every final Polish sentence was checked independently for contemporary usage, idiomaticity, exact
sense, case and preposition government, participant structure, register, CEFR vocabulary and
standalone usefulness. Morphology was verified form by form: `siostrze` (Dat), `kolację`, `kawę`,
`gazetę`, `kondycję`, `cenę`, `koleżankę`, `nową restaurację`, `tę górę` (Acc); `egzaminie` (Loc);
`córką`, `chorą babcią` (Instr); `pogody` (Gen after `od`); `znalazłam` as the past of **perfective**
`znaleźć`, not of imperfective `znajdować`; `zależą` as the 3pl of `zależeć` agreeing with
non-masculine-personal `nasze plany`.

No final sentence relies on: neuter Accusative = Nominative; plural Genitive/Accusative ambiguity;
negation independently producing a Genitive; a pronoun obscuring the lesson; or the target verb
hidden under a stronger construction. No sentence was made artificial in order to expose
morphology — where displaying an ending would have required unnatural Polish, the natural sentence
was kept and the limitation recorded instead (007, 014).

### Residual risk — no native-speaker acceptance on seven sentences

This is the largest residual risk in the package and it is unchanged in kind from C1, though the set
has shifted. Carrying AB's recorded Phase 4C linguistic acceptance of the text: **011, 012, 042, 044**.
With **no native-speaker acceptance of any kind**: **018, 031, 032, 035, 036, 043**, plus **033**,
whose accepted Phase 4C draft was shortened here. Every final **English** string on 011, 018 and 033
is likewise new. AB's acceptance is acceptance of a text and is never authorship; no proposal is
presented as human-authored.

---

## 10. Provenance and copyright

- **No final origin is `original`.** `authorRegistry` stays empty and no human-authorship claim was
  created.
- Both repository-reuse sources were **re-resolved in this phase**, not taken on either review's
  word, and both match byte-exactly on `pl`, with the card `exEn` also matching the canonical `en`.
- All 11 editorial-generated sentences are absent from 27,498 repository strings and 2,532 canonical
  corpus strings, verbatim and as substrings.
- **CONFIRMED CLEAN on copyright.** No Mędak example sentence, definition, synonym list or
  explanation, and no WSJP PAN example sentence, collocation list, citation or definition was
  consulted, reproduced or paraphrased in this phase.

### Governance prerequisite for C2 — not an open decision

Eleven rows now require `origin.kind = "editorial-generated"`, which the validator resolves through
`generatorRef` plus `adoptedAt` against `editorialActorRegistry`, demanding `human: false` and the
`example-generation` role. The registry holds exactly one actor, `priority7-reference-analysis`,
carrying `reference-verification` **only**, and the architecture requires the reference and editorial
actors to be **distinct identities**. C2 must register a new nonhuman example-generation actor before
any of the eleven can be stored. C1C correctly registered none.

This is a defined implementation step, not an unresolved example choice. It was already required by
ten rows before this adjudication; 044 adds an eleventh at no additional governance cost.

### C2 implementation notes

- **Existing example IDs that can carry new wording**, with re-minted keys: 011, 012, 018, 033, 036.
- **Newly minted example IDs and keys required**: 031, 032, 035, 042, 043, 044.
- **Untouched**: 007 and 014 keep their existing examples, IDs, keys and origins exactly as they are.
- No pattern, meaning, CEFR value, teaching status, complement, evidence record, contentRef or
  errorNote is changed by any row.

---

## 11. Unresolved owner decisions

**None.** All 13 example choices are adjudicated; no row is `NO IMPLEMENTATION YET`.

---

## 12. Canonical boundary

| Item | Baseline | After C1C |
|---|---|---|
| `editorial/verb-pattern-candidates.json` | baseline | **byte-identical** |
| `editorial/priority-7-authoring-context.json` | baseline | **byte-identical** |
| Patterns | 45 | **45** |
| `reviewState` | 45 × `reference-verified` | **45 / 45** |
| `reference-verification` accepts | 47 | **47** |
| `editorial-review` events | 0 | **0** |
| `product-approval` events | 0 | **0** |
| Canonical examples | 23, all `repository-reuse` | **23, all `repository-reuse`** |
| `authorRegistry` | empty | **empty** |
| `editorialActorRegistry` | 1 actor, `reference-verification` only | **unchanged** |

No review event of any kind was created, no actor registered, and no shipping or runtime file
touched. The copied source review artifacts under `reports/phase-4fc1/` and `reports/phase-4fc1b/`
remain byte-identical to what was supplied, including the blind input at its recorded SHA-256.

The Phase 4F-C1.1 repair to `tests/test_priority7_phase4fb3b.py` is preserved unmodified: it still
tests the immutable `7beb50d7 → 080d92ad` transition and `B3B_FOOTPRINT` still holds exactly its 11
approved paths.

C1C added exactly three files, all non-shipping:

- `reports/priority-7-phase-4fc1c-example-adjudication-matrix.csv`
- `reports/priority-7-phase-4fc1c-summary.md`
- `tests/test_priority7_phase4fc1c.py`

---

## 13. Validation — real C1C workspace

The workspace was never committed. The three C1C artifacts and the two copied review directories
are untracked additions; `tests/test_priority7_phase4fb3b.py` carries the preserved C1.1 repair as
its only tracked modification; `editorial/` is byte-identical to baseline.

| Suite (§27) | Result |
|---|---|
| C1C (`test_priority7_phase4fc1c.py`) | **74 passed** |
| B3B, 4F-A, 4E.1, 4E, 5-A, 4C, 3D-1, 3F-A, 2A + C1C | **788 passed, 0 failed** |
| Full Python (`tests/`) | **1004 passed, 0 failed** |
| Full JXA (36 suites) | **36 suites, 0 failed** |
| `validate_content.py` | pass, forward baseline `2a71401d…1ce50` |
| `verify_audio.py` | 3377 phrases / 3377 manifest / 3377 MP3s, nothing orphaned |
| `build_pages.py --check` | committed output current, 32 sitemap URLs |
| `validate-editorial` | `Priority 7 private editorial record: valid` |
| `git diff --check` | clean |
| `git status --porcelain` | five untracked C1C/source paths + the B3B test modified |

### The suite was mutation-tested

Five mutants were built against the adjudication matrix and run; every one was caught, so none of
the guards is trivially satisfied:

| Mutant | Result |
|---|---|
| `finalOrigin` set to `original` on a generated row | **3 tests fail** |
| A reproduced `c1bSeverity` altered on P7-NR-033 | **1 test fails** |
| P7-NR-018 dispositioned `ADD` | **2 tests fail** |
| A generated final replaced with an existing repository string | **1 test fails** |
| A repository-reuse source pointed at a card it does not match | **2 tests fail** |

---

## 14. Committed-scratch rehearsal

A fresh isolated scratch was created by local clone, its remote removed, `push.default` set to
`nothing`, and the nine-file C1C candidate committed **there only**. The real C1C workspace was
never committed.

| Check (scratch, C1C as HEAD) | Result |
|---|---|
| Remotes | **zero** |
| Working tree after commit | **clean** |
| `git diff --name-only HEAD^ HEAD` | the nine C1C files, nothing else |
| `git diff --check HEAD^ HEAD` | **clean** |
| C1C suite | **74 passed** |
| B3B suite | **128 passed** |
| Full Python | **1004 passed, 0 failed** — identical to the real workspace |
| Full JXA | **36 suites, 0 failed** |
| `validate_content.py` | pass, same forward baseline |
| `verify_audio.py` | 3377 / 3377 / 3377, nothing orphaned |
| `build_pages.py --check` | committed output current, 32 sitemap URLs |
| `validate-editorial` | valid |

The committed candidate is: the three C1C artifacts, the five copied source review artifacts, and
the preserved B3B test. Nothing canonical, nothing shipping, nothing runtime.

### Baseline comparisons remain meaningful after C1C becomes HEAD

Proven directly in the scratch candidate:

| Anchor | Result with C1C as HEAD |
|---|---|
| `git status --porcelain` | *empty* — a status-only guard is now **vacuous** |
| `git diff --name-only HEAD` | *empty* — a HEAD-anchored guard is now **vacuous** |
| `git diff --name-only 080d92ad…` | **the nine C1C files** — the pinned guard still has teeth |

Every boundary guard in `tests/test_priority7_phase4fc1c.py` folds the pinned-commit diff into its
evidence and asserts the touched set is non-empty before checking it, so none of them can pass by
having nothing to look at. This is why the suite pins the SHA and never resolves `HEAD` — a phase
that changes nothing canonical would otherwise be comparing the baseline with itself.

`C1C_FOOTPRINT_PREFIXES` is deliberately a **prefix** allowlist rather than a closed set, applying
the Phase 4F-C1.1 lesson forward: C1C cannot enumerate what its own successors may add.

---

## 15. Verdict

**GO.**

All 13 example decisions are adjudicated with an exact C2 implementation plan: 2 KEEP CURRENT,
5 REPLACE, 6 CREATE, 0 ADD, 0 open. Ten changes are required for editorial acceptance and one is
optional polish. Every final example carries a truthful provenance decision — 2 re-resolved
repository-reuse, 11 editorial-generated, none `original`. Canonical state is untouched and the two
independent reviews were reconciled on the merits, without voting, on all three substantive
disagreements.

**Do not begin Phase 4F-C2 until the nonhuman example-generation actor is registered as its first
step.**
