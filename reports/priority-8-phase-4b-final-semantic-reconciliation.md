# Priority 8 Phase 4B — final 68-lemma semantic / editorial reconciliation

This document is a **semantic and editorial adjudication proposal**. It changes no
`candidateContent`, no staging, no guard, no test, no validator, no schema, no
canonical/runtime/audio/product artifact. It allocates no ID, renames no live key,
and freezes nothing. Its only repository effect is its own creation.

Every recommendation below is a **proposal awaiting human adjudication**.

---

## 1. Executive verdict

The mechanical audit's four BLOCKING items resolve as follows.

- **P8-FR-001 / P8-FR-002 (`zapominać`, `kłócić się` `clauseKind: czy`) — CONFIRMED
  DEFECT, CORRECTION REQUIRED.** This is not a judgment call. Three independent
  frozen artifacts settle it: the Phase 3 → Phase 4 handoff binds Phase 4B to
  exactly four clause distinctions (`że`, `żeby`, interrogative-dependent, direct
  speech — `czy` is not among them); Phase 3 order 63 records as a frozen *rejected
  hypothesis* that "Czy is not a distinct product construction apart from the
  established interrogative-dependent clause type"; and the SHA-locked Batch 7
  schema matrix states "**`czy` is a realization, not a fifth clauseKind**", names
  these two exact rows as carrying the wrong value, and explicitly defers them to
  this reconciliation. Both rows' own Phase 3 evidence reads
  `clause:interrogative-dependent`, never literal `czy`.
- **P8-FR-003 (source role) — NOT A PHASE 4B DEFECT; HUMAN / ARCHITECTURE DECISION,
  DEFER TO PHASE 4C.** Downgraded from BLOCKING on specific evidence: the candidate
  keys, `internalScope`, and `learnerExplanationEn` of all four rows already encode
  *source* explicitly. Nothing that freezes is wrong. The defect materializes only
  at runtime projection, which Phase 4B does not perform.
- **P8-FR-004 (regression architecture) — CONFIRMED, CORRECTION REQUIRED**, as the
  mechanical consequence of P8-FR-001/002.

Of the nine REVIEW items, **two close with no action** (P8-FR-007, P8-FR-013 — both
are correct as-authored for principled reasons given below) and **seven are adopted
as editorial corrections** with exact replacement text.

The semantic pass additionally found **three defects the mechanical audit could not
detect**, because they are semantics/translation mismatches rather than structural
ones. The most serious (P8-SR-001) is an English translation that directly
contradicts its own meaning definition.

**Candidate-key freeze gate: C — HUMAN ADJUDICATION REQUIRED BEFORE FREEZE.**
Exactly two candidate keys must change, and both are clear-cut. But the same two
rows also carry a genuine, never-answered product decision (their teaching status
and CEFR), and both changes land in the same digest-recomputing correction pass.
Gate B is unavailable because an unresolved policy decision does exist.

---

## 2. Starting state

Verified before any work; all checks exact.

| Check | Required | Observed |
|---|---|---|
| Working folder | `/Users/Kaj/Downloads/Repository for Codex - Priority 8 Phase 4B SAFE` | exact |
| Branch | `priority-8-phase-4b-editorial-authoring` | exact |
| HEAD | `e2dc1e2a18c822d6f315cf7dfdad98a84d2316a7` | exact |
| Subject | `Priority 8 Phase 4B final mechanical reconciliation audit` | exact |
| Worktree at start | clean | clean |
| Remotes | zero | zero |
| `push.default` | `nothing` | `nothing` |
| Pre-push hook | executable, blocking | executable; prints repository block message, exits 1 |
| `phaseStep` / `stagingRevision` | `4B7` / `8` | exact |
| Lemmas / meanings / patterns / examples | 68 / 95 / 224 / 224 | exact |
| Future-empty full-pattern records | 0 | 0 |
| Teaching status split | 220 active-production / 4 recognition-only | exact |
| Guard registry | 72 rules, `registryVersion = 2` | exact |
| Tests | 270 | 270, OK |
| Mechanical audit present | yes | `reports/priority-8-phase-4b-final-reconciliation-mechanical-audit.md`, 466 lines |
| Audit queue | 15 items — 4 BLOCKING / 9 REVIEW / 2 INFORMATIONAL | exact |
| Audit key-readiness conclusion | mechanically valid, semantic review required | exact (its §21 conclusion **C**) |

No mismatch. Proceeding was authorized.

---

## 3. Mechanical queue intake — all 15 IDs

All 15 items were extracted from §20 of the mechanical audit verbatim. No item was
merged, renamed, or dropped. Audit IDs are preserved throughout.

| ID | Lemma(s) | Category | Mechanical severity |
|---|---|---|---|
| P8-FR-001 | `zapominać` | clauseKind/source alignment; key freeze | BLOCKING |
| P8-FR-002 | `kłócić się` | clauseKind/source alignment; key freeze | BLOCKING |
| P8-FR-003 | `wracać`, `wrócić`, `wyjść`, `wyjechać` | role architecture debt | BLOCKING |
| P8-FR-004 | early-batch lock layer | regression architecture | BLOCKING |
| P8-FR-005 | 12 lemmas / 14 groups | semantic ownership (same-shape) | REVIEW |
| P8-FR-006 | `polecać` | editorial/semantic boundary (A4) | REVIEW |
| P8-FR-007 | `wiedzieć` + `z` + Genitive families | cross-batch role convention | REVIEW |
| P8-FR-008 | `musieć` | editorial wording | REVIEW |
| P8-FR-009 | `jeść` | editorial concision | REVIEW |
| P8-FR-010 | `kochać` | gloss ordering | REVIEW |
| P8-FR-011 | `uczyć` | example transparency (`o` + Locative) | REVIEW |
| P8-FR-012 | `uczyć` | example case transparency (`dzieci`) | REVIEW |
| P8-FR-013 | `pisać`, `napisać`, `pasować` | CEFR/priority outlier | REVIEW |
| P8-FR-014 | `pisać`, `napisać`, `powiedzieć` | duplicate English | INFORMATIONAL |
| P8-FR-015 | all 68 | candidate-key scoping | INFORMATIONAL |

---

## 4. Blocking-item adjudication

Each blocking item receives exactly one of the three permitted verdicts.

### P8-FR-001 — `zapominać` / `czy-dependent-clause`

**Verdict: A — CONFIRMED DEFECT, CORRECTION REQUIRED.**

Evidence chain, all frozen and repository-internal:

1. **Own Phase 3 evidence.** `reports/priority-8-phase-3-batch-03-verification.csv`,
   order 21, `supported_constructions_structured` reads
   `…;clause:że(recall sense);clause:interrogative-dependent(recall sense);…`. The
   `primary_source_evidence_summary` records the WSJP Składnia string as
   `że ZDANIE or ZDANIE PYTAJNOZALEŻNE`. There is **no** literal-`czy` source label.
2. **Corpus-level clause policy.** `reports/priority-8-phase-3b-phase4-handoff.md`
   binding constraint 9 (and Phase 3 final synthesis line 148) bind Phase 4 to
   "exact clause distinctions: `że`, `żeby`, interrogative-dependent, and direct
   speech." `czy` is not one of the four bound types.
3. **Explicit corpus-level rejection.** Phase 3 order 63 (`wiedzieć`),
   `rejected_or_unverified_hypotheses`: "Czy is not a distinct product construction
   apart from the established interrogative-dependent clause type." Its
   `remaining_uncertainty` instructs later authoring to "explain czy only as one
   interrogative-dependent clause realization."
4. **Approved Phase 4B governance.** The SHA-locked B7 schema matrix
   (`8b152b20…`) §on clause discipline: "**`czy` is a realization, not a fifth
   clauseKind.** … `Czy` is **not a fifth locked type**. The product therefore uses
   `clauseKind: interrogative`." It then names this exact row, notes its frozen
   evidence is interrogative-dependent, declares it out of Batch 7 scope, and takes
   no position — deferring it to precisely this reconciliation.
5. **Live approved precedent.** `wiedzieć/interrogative-queried-content` is live,
   guarded, and digest-locked with `clauseKind: interrogative` and a **`czy`
   example sentence** (`Nie wiem, czy zdążymy na pociąg.`). The corpus therefore
   already teaches an embedded `czy` clause under `interrogative`.
6. **The authoring slip is visible.** The B2 authoring report describes the row as
   the fifth "directly verified construction … (`czy`-clause)", transcribing
   `ZDANIE PYTAJNOZALEŻNE` as `czy`. The B2 risk review then filed the classification
   as an **unanswered residual reviewer question**, not an approved decision.

The current state is a Batch 2 implementation mistake, exactly the case §4 of the
task authorizes correcting against frozen evidence. It is not shielded by the fact
that a historical digest pins it.

### P8-FR-002 — `kłócić się` / `czy-dependent-clause`

**Verdict: A — CONFIRMED DEFECT, CORRECTION REQUIRED.**

The same chain applies, with this row's own evidence:
`reports/priority-8-phase-3-batch-03-verification.csv` order 27 reads
`…;clause:interrogative-dependent;clause:że`, and its
`primary_source_evidence_summary` records "parallel interrogative-dependent and
ŻE clause variants." No literal `czy` source exists. The B3 risk review likewise
filed the recognition-only classification as an unanswered residual question.

One helpful asymmetry: this record's `internalScope` **already** uses the correct
wording — "że and the interrogative clause are alternatives to the nominal
o + Accusative topic". Only the machine field, the key, and the learner explanation
are wrong. That is independent internal corroboration that `interrogative` was the
intended reading and `czy` was a slip at the field/key layer.

### P8-FR-003 — source-like `z` + Genitive rows encoded `role: target`

**Verdict: B — NOT A DEFECT; CURRENT STATE SHOULD REMAIN in Phase 4B.**
Classified **PHASE 4C ARCHITECTURE DEBT + HUMAN / ARCHITECTURE DECISION**.

Downgraded from BLOCKING on this specific evidence:

- The locked role enum is `subject, object, recipient, experiencer, predicate,
  content, topic, interlocutor, means, target`. There is no `source`, and Phase 4B
  is forbidden from inventing one. Of the ten available values, `target` is the only
  spatial/directional role; every alternative (`object`, `topic`, `means`) would be
  strictly worse.
- **Nothing that freezes is wrong.** All four rows carry the source semantics in
  every durable field: keys `z-genitive-return-source` (×2) and `z-genitive-source`
  (×2); `internalScope` ("z+Genitive realizes a selected source role");
  `learnerExplanationEn` ("the place you return from", "where you're leaving from").
- The misrepresentation is confined to **runtime projection**, which Phase 4B does
  not perform. `pp-verb-patterns.js` maps `target` to the learner phrase
  "what it is aimed at" — semantically backwards for `Wracam z kina`. That is a real
  and material problem, but it is a Phase 4C projection problem, not a candidate
  content problem.

Because the keys already say `source`, a future `source` role makes them *more*
correct, and its absence leaves them still accurate. **The keys are durable either
way**, which is why this item does not block freeze.

The human decision required is narrow and is recorded as **HD-2** in §18.

### P8-FR-004 — regression architecture cannot detect the mismatch

**Verdict: A — CONFIRMED, CORRECTION REQUIRED** (as the consequence of 001/002).

Confirmed independently: no guard rule targets `zapominać` at all, and the only
`kłócić się` rule is `p8-4b-klocic-sie-lexical-identity` (particle identity). B1/B2
predate the declarative guard layer. Consequently the two wrong values pass the
validator and all 270 tests, and are held in place only by the B2 and B3 SHA-256
content digests — which pin the defect rather than protect against it.

Both digests project the full `candidateContent`, so any correction necessarily
recomputes `BATCH_2_APPROVED_DIGEST` and `BATCH_3_APPROVED_DIGEST`. Correcting them
without adding positive guards would restore exactly today's blind spot, so the
correction pass must also add shape guards for both lemmas.

---

## 5. ClauseKind reconciliation

### 5.1 The two adjudicated rows

Correct Phase 4B representation for both rows is **`clauseKind: interrogative`**.

Complete correction surface, field by field. Fields deliberately **not** changed are
listed too, because the task asks for exactly what genuinely requires correction.

**`zapominać`** (order 21, Batch 2, meaning `recall-failure`):

| Field | Current | Correction | Required? |
|---|---|---|---|
| complement `clauseKind` | `czy` | `interrogative` | **yes** |
| `candidatePatternKey` | `czy-dependent-clause` | `interrogative-forgotten-content` | **yes** |
| example `patternKeyRef` | `czy-dependent-clause` | `interrogative-forgotten-content` | **yes** (referential integrity) |
| `learnerExplanationEn` | "Use czy to introduce a forgotten yes/no question…" | see below | **yes** |
| `internalScope` | "…że and czy content clauses realize forgotten propositional/question content." | see below | **yes** |
| example `pl` / `en` | `Zapominam, czy zamknąłem drzwi.` / "I forget whether I locked the door." | **unchanged** | no |
| `candidateExampleKey` | `primary` | **unchanged** | no |
| `relationType`, `role`, `required` | `lexical-frame`, `content`, `true` | **unchanged** | no |
| `cefr` / `teachingStatus` / `usage` | `B1/—`, recognition-only, common | see §11 | **HD-1** |

**`kłócić się`** (order 27, Batch 3, meaning `interpersonal-quarrelling`):

| Field | Current | Correction | Required? |
|---|---|---|---|
| complement `clauseKind` | `czy` | `interrogative` | **yes** |
| `candidatePatternKey` | `czy-dependent-clause` | `interrogative-disputed-content` | **yes** |
| example `patternKeyRef` | `czy-dependent-clause` | `interrogative-disputed-content` | **yes** |
| `learnerExplanationEn` | "Use czy to introduce an undecided yes/no topic…" | see below | **yes** |
| `internalScope` | already says "że and the interrogative clause are alternatives" | **unchanged — already correct** | no |
| example `pl` / `en` | `Kłócimy się, czy powinniśmy wyjechać.` / "We're arguing about whether we should leave." | **unchanged** | no |
| `cefr` / `teachingStatus` / `usage` | `B1/—`, recognition-only, common | see §11 | **HD-1** |

**Keeping both Polish examples is deliberate and evidence-backed.** A `czy` sentence
is a legitimate realization of the interrogative-dependent clause; the live,
approved `wiedzieć` row does exactly this. Keeping them also avoids a new-example
provenance rerun for these two rows.

Exact proposed replacement text, modelled on the approved `wiedzieć` explanation so
that all 16 interrogative rows teach the type the same way:

- `zapominać`: *"Use a dependent question clause for a forgotten question. For a
  yes/no question that word is czy: zapominam, czy zamknąłem drzwi (I forget whether
  I locked the door); question words such as gdzie or kiedy work the same way."*
- `kłócić się`: *"Use a dependent question clause when the disputed point is an open
  question. For a yes/no question that word is czy: kłócimy się, czy powinniśmy
  wyjechać (we're arguing about whether we should leave); question words such as
  gdzie or kiedy work the same way."*
- `zapominać` `internalScope`, replacing the `czy` clause only: *"…o+Locative names a
  remembered topic; że clauses realize forgotten propositional content and
  interrogative-dependent clauses realize forgotten question content (a czy sentence
  is one realization of that clause type, never a separate clause kind)."*

### 5.2 Key durability under the correction — the critical freeze question

**`czy-dependent-clause` does not remain semantically durable once the structural
`clauseKind` becomes `interrogative`.** It would be the only pattern key in the
corpus naming a surface conjunction that its own structure does not encode, and it
would contradict the governance statement that `czy` is not a type. Both keys must
change; this is the last safe point to do it.

Recommended replacements, chosen against the eight existing interrogative-row key
precedents (`interrogative-dependent-clause`, `interrogative-content-clause` ×2,
`interrogative-agreement-clause`, `interrogative-worry-content`,
`interrogative-queried-content`, `dative-interrogative-advice`,
`accusative-learner-interrogative-taught-content`):

| Lemma | Current key | Recommended key | Reason |
|---|---|---|---|
| `zapominać` | `czy-dependent-clause` | `interrogative-forgotten-content` | Matches role `content` and the sibling `ze-content-clause`; parallels `wiedzieć/interrogative-queried-content` and `martwić się/interrogative-worry-content`. |
| `kłócić się` | `czy-dependent-clause` | `interrogative-disputed-content` | Matches role `content` and the sibling `ze-content-clause`; "disputed" names this lemma's semantics without repeating the neighbouring `o-accusative-topic` key. |

Both remain unique within their `(lemma, meaning)` parent scope. Affected references:
one `patternKeyRef` each (one example per pattern), and no meaning key.

### 5.3 Global clauseKind consistency — §7 of the task

Every clause complement in the corpus (65 rows across 24 lemmas) was compared
against its own frozen `supported_constructions_structured` string. Pattern keys,
`learnerExplanationEn`, and `internalScope` were separately scanned for standalone
`czy` tokens.

**Result: NONE.** No other candidate key, learner explanation, or `clauseKind`
encodes a surface conjunction where the frozen evidence licenses the broader
interrogative-dependent class.

Specifically checked and cleared:

- `ze` (19 rows) and `zeby` (19 rows) keys do encode surface conjunctions, but `że`
  and `żeby` **are** two of the four frozen bound types. Correct as authored.
- The three other standalone-`czy` mentions in staging are all correct: `wiedzieć`
  and `móc` explicitly frame `czy` as a realization / sentence-level packaging and
  never as a type, and `zgadzać się/direct-speech-consent` uses `czy` only inside a
  framing sentence of the quoted context.
- Two divergences surfaced by the sweep are pre-existing and already documented, not
  new findings: `odpowiadać/direct-speech` is authored where frozen evidence lists
  only `clause:że` (a documented private-staging policy addition, canonical support
  deferred to 4C), and `pamiętać` authors only `zeby` where evidence also supports
  `że` and `interrogative` (a documented deliberate B2 deferral to avoid
  recall/reminder conflation). Both are under-/side-representation by explicit
  policy, not surface-conjunction narrowing. No action.

---

## 6. Motion / source role adjudication

Answering the task's four framings directly:

- **A. Is `target` an intentionally governed coarse fallback already accepted by
  Phase 4B policy?** Partly. The enum is deliberately coarse and locked, and the
  binding constraints for all four lemmas require the concrete forms to be labelled
  realizations — which they are. But no committed artifact states "`target` is the
  accepted encoding for source." It is an unstated consequence, not a recorded
  policy. That gap is the reason a human decision is genuinely needed.
- **B. Does it materially misrepresent the learner-facing candidate structure?** In
  the candidate content, **no** — keys, `internalScope`, and every
  `learnerExplanationEn` say "source"/"from". At runtime projection, **yes** —
  `ROLE_PHRASES.target` renders "what it is aimed at", which inverts the direction
  for `Wracam z kina`. Phase 4B performs no projection, so this is latent.
- **C. Should it remain as Phase 4B architecture debt for Phase 4C?** **Yes.**
- **D. Does the candidate representation need correction before key freeze?** **No.**
  The keys already encode `source` and are durable under either 4C outcome.

**Classification: HUMAN / ARCHITECTURE DECISION REQUIRED (HD-2), resolved as
PHASE 4C ARCHITECTURE DEBT.** No new role is invented in Phase 4B.

**Scope refinement (new, beyond the mechanical audit — P8-SR-003).** The audit named
four `z` + Genitive motion rows. The semantic pass finds the origin-role debt is
broader: `kupować/seller-price-schema` and `kupić/seller-price-schema` encode the
seller (`od` + Genitive, "who you buy from") as `target`, and
`zamawiać/u-genitive-provider` encodes the provider (`u` + Genitive, "ordering from
a carpenter") as `target`. These are unambiguously origin participants — **seven
rows total**, not four.

Deliberately **excluded** from that count after inspection:
`wymagać/genitive-required-content` and `zeby-clause` (×2 each) and
`chcieć/genitive-desired-object` also use `od` + Genitive with `role: target`, but
"required *of* someone" / "wanted *from* someone" is defensibly directional — the
requirement is aimed at that person. `target` is acceptable there and should not
change.

**Phase 4C implications if a `source` role is added:** it is a runtime enum change
touching `pp-verb-patterns.js` (`ROLES`, `ROLE_PHRASES`, and the `ANIMATE_ROLES`
decision), `priority7_tooling.py`, `validate_priority8_staging.py`, the released
Priority 7 canonical corpus (which must be re-audited for rows that should migrate),
plus guards, digests and tests for these seven rows. If a `source` role is **not**
added, Phase 4C must instead carry a binding constraint that the runtime never
projects "what it is aimed at" onto these seven rows.

---

## 7. Generalized-role adjudication

All 18 generalized-role families in §10 of the mechanical audit were re-inspected
against their `bindingConstraints` and live wording. The audit's finding of "no
unauthorized concretization" is **confirmed semantically**, and the hedging discipline
is real rather than nominal.

| Family | Frozen boundary | Verdict |
|---|---|---|
| `iść`, `przyjść`, `przyjechać`, `wracać`, `wrócić`, `wyjść`, `wyjechać` | `DOKĄD` / `SKĄD` | **CORRECT** — every row carries an explicit non-exclusivity hedge ("one common way… not the only form", "it does not replace other destination prepositions") |
| `dzwonić` | target `DOKĄD` | **CORRECT** — "a documented target realization, not exclusive government" |
| `mieszkać` | residence `GDZIE` | **CORRECT** — "a documented residence-place realization, not the only possible form"; `na`/`u` correctly omitted |
| `zamawiać` | provider `GDZIE` | **CORRECT** — "One common way to name the provider is u + Genitive" |
| `umówić się` | appointment `GDZIE`, time boundary | **CORRECT** — venue hedged as "a documented realization"; time correctly unencoded |
| `zapraszać` | exact `KOGO + na/do`; separate `KOGO + GDZIE` | **CORRECT** — deliberately **unhedged**, because `na`/`do` are exact source constructions here, not narrowings. Hedging would be the error. |
| `pracować`, `przynosić`, `pokazywać`, `czytać`, `wiedzieć`, `uczyć` (school `GDZIE`) | generalized role verified but unrepresented | **CORRECT / ARCHITECTURE-DEFERRED** — no concrete row invented; evidence retained in `internalScope` only |
| `KTÓRĘDY` | no authored realization anywhere | **CORRECT** |

**No item in this family needs editorial clarification or structural correction.**
The differing treatments across lemmas track differing frozen handoff constraints
and were correctly not flattened.

---

## 8. Polecać A4 adjudication

Row: `polecać / directive-instruction / dative-accusative-action-noun`
(order 58, Batch 6). Current: `Trener poleca zawodnikom rozgrzewkę.` /
"The coach orders the players to warm up."

Answering the five questions:

1. **Is the Polish sufficiently directive/instructional?** **Yes.** A coach
   prescribing a warm-up to his players is an instruction, not a product
   recommendation; `polecać` sense 1 is squarely available in that frame. The
   Polish is not the problem.
2. **Is English "orders" materially stronger than the Polish?** **Yes — and this is
   demonstrable from inside the record itself.** The three sibling patterns of the
   *same meaning* all render `poleca` as "tells": "the doctor **tells** me to rest",
   "my boss **tells** me to prepare the report", "the manager **tells** me". Only A4
   escalates to "orders". Polish `polecać` corresponds to instruct/tell/direct;
   "orders" corresponds to `rozkazywać`/`nakazywać`. The overstatement is both
   lexically wrong and internally inconsistent.
3. **Would a better Polish sentence preserve the directive meaning more
   unambiguously?** **No — and changing it would cost more than it gains.**
   `rozgrzewkę` is a feminine Accusative in `-ę`, so the governed case is *visibly*
   Accusative. The `internalScope` says the position is "ordinarily a gerund/action
   noun", but every Polish `-nie`/`-cie` verbal noun is neuter and therefore
   Nominative/Accusative syncretic. Any "more gerund-like" replacement would hide
   the case — reintroducing exactly the defect flagged in P8-FR-012. The current
   choice is the better editorial compromise.
4. **Would a better English translation solve the problem without weakening the
   distinction from recommendation?** **Yes.** "Instructs" is unambiguously directive
   and cannot be read as recommending.
5. **Should A4 remain active-production?** **Yes.** A2/A2 common, unchanged. It is a
   frequent, well-evidenced construction.

**ONE recommended final pair (no alternatives left open):**

- **PL: `Trener poleca zawodnikom rozgrzewkę.` — unchanged.**
- **EN: "The coach instructs the players to warm up."**

Consequential edit in the same row, required for consistency: the
`learnerExplanationEn` repeats the gloss and must change "the coach orders the
players to warm up" → "the coach instructs the players to warm up".

Because the Polish is unchanged, **no provenance rerun is triggered** by this item.

After this correction the A4 / recommendation boundary is carried by four
independent signals — distinct meaning keys, distinct glosses, distinct
`internalScope` (which explicitly names the structural identity), and distinct
examples ("instructs the players to warm up" vs "I recommend this restaurant to
you"). That is sufficient; see §12.

---

## 9. Batch 7 editorial-item adjudication

The B7 risk report records that the independent B7 linguistic review was outstanding
at its commit boundary and no later B7 review artifact exists. All nine items were
therefore adjudicated directly against live staging plus frozen Phase 3 evidence.

A high bar was applied: an item is adopted only where it materially improves learner
clarity, semantic distinction, or reconciliation consistency.

### A. `musieć` explanation — **ADOPT EDITORIAL IMPROVEMENT**

"always" is **not** the defect: `musieć` genuinely takes only a bare infinitive, and
that is useful for a learner to hear about a modal. The defect is the second
sentence — "Polish uses this one construction whether or not the sentence names who
has to act, so impersonal sentences add nothing new to learn." This is
**meta-commentary about the curriculum**, not instruction: it introduces an
unexplained term ("impersonal sentences") solely to tell the learner there is
nothing to learn about it. No other explanation in the corpus addresses the learner
this way.

**Replacement:** *"Musieć always takes a bare infinitive: muszę iść do lekarza (I
have to go to the doctor). This is the only construction it uses."* (22 words, down
from 40.)

### B. `jeść` explanation — **ADOPT EDITORIAL IMPROVEMENT**

This one is settled by frozen evidence rather than taste. Phase 3 order 64,
`remaining_uncertainty`: "Phase 4 authoring must teach positive Accusative as the
lexical frame and **handle negation separately**." Its `research_notes` add
"Grammar-owned distinction preserved: positive lexical object = Accusative; ordinary
Genitive of negation = sentence-grammar effect." The live 64-word explanation does
the opposite — it teaches negation-Genitive *inside* the pattern's own explanation,
on an A1/A1 core row. Corroborating inconsistency: `pić` carries the identical
`no-lexical-genitive` guard and the identical concern, and says nothing about
negation at all.

**Replacement:** *"Both parts are optional: the food takes the Accusative and the
implement the Instrumental — dziecko je zupę łyżką (the child eats the soup with a
spoon) — or just je (is eating). Jeść has no Genitive object of its own."*
(40 words, down from 64.)

This retains the boundary the guard exists to protect (no lexical Genitive) while
returning negation to grammar ownership, as the frozen evidence directs.

### C. `kochać/strong-liking` gloss order — **ADOPT EDITORIAL IMPROVEMENT**

Current: `["love (doing something)", "really like"]`. Two problems, of which the
second is the more serious and was not stated in the audit:

1. Leading with "love" foregrounds the strongest English reading on the meaning whose
   entire purpose is to be *weaker* than `person-love`.
2. **"(doing something)" is factually under-inclusive.** This meaning owns two
   patterns — `accusative-strongly-liked-thing` (`kocha czekoladę`, a *thing*) and
   `infinitive-strongly-liked-activity` (an activity). The leading gloss describes
   only the second and mislabels the first.

**Replacement:** `["really like", "love (a thing or an activity)"]`.

This also strengthens P8-FR-005: the three `kochać` meanings share one identical
Accusative signature, so the glosses carry real disambiguation load.

### D. `kochać` + infinitive register — **KEEP AS IS**

Phase 3 order 66 lists `infinitive:strongly liked activity(sense3)` as verified with
no register caveat and no note of colloquiality. Marking it `informal` would make it
the only non-`neutral` row among 224 with **no frozen evidence backing**, which is
exactly the kind of intuition-filling §1 of the task forbids. No action; recorded as
a Phase 4C observation only.

### E. `przepraszać` clause English participant attachment — **ADOPT EDITORIAL IMPROVEMENT**

Current EN: "I'm sorry I didn't call you yesterday." Polish `cię` is the **Accusative
person apologised to** — a complement of `przepraszać`. The English attaches "you"
to the *embedded* clause as the person not called. The learner therefore sees a
sentence in which the row's own optional Accusative participant has silently moved
to a different predicate. On a row whose stated teaching point is "here the person is
optional", that is a material valency error, not a stylistic one.

**Replacement EN: "I apologise to you for not calling yesterday."** Polish unchanged.

This makes `cię` visibly the apology's recipient and mirrors the sibling row's
already-approved frame ("Marek apologises **to the teacher** for being late").
Acknowledged trade-off: the English becomes a gerund rather than a clause. That is
accepted because the explanation already states the clause structure twice and shows
both Polish variants inline, whereas the participant error has no other corrective.

### F. `życzyć` + żeby, English "hope" / Dative visibility — **ADOPT (explanation only)**

Real problem: the Dative `ci` is a **required** complement, and "I hope you pass this
exam" makes it invisible while also replacing the lemma's own gloss ("wish") with
"hope". But English has no natural verb taking *wish + dative recipient + that-clause*
("I wish that you pass" is archaic), and §18 ranks natural translation above global
uniqueness.

**Resolution: keep the example pair unchanged; fix the explanation** so the required
Dative is visible through a literal gloss.

**Replacement explanation:** *"To wish for something to happen, keep the Dative person
and use a żeby clause instead of the Genitive: życzę ci, żebyś zdał egzamin (literally
'I wish for you that you pass the exam'; English usually says I hope you pass). Use
one or the other, not both."*

### G. `korzystać` benefit example redundancy — **KEEP AS IS**

`Studenci … ze zniżek studenckich` does repeat the root, but "zniżki studenckie" is
the ordinary Polish collocation and the sentence is natural. Under the stated high
bar this fails: it harms neither learner clarity nor the resource-use / benefit-from
distinction, which the example draws well. Two candidate replacements were considered
and rejected — one would have inserted a `na` + Accusative nominal modifier into a
`z` + Genitive row, reproducing the exact defect flagged in item H. No action; no
provenance rerun.

### H. `uczyć` `o` + Locative example contains surface `w` + Locative — **ADOPT**

Current: `Nauczycielka uczy dzieci o zwyczajach w innych krajach.` The row teaches
governed `o` + Locative. The example places a **second, ungoverned Locative phrase**
immediately after the governed one. In a case-teaching product this genuinely
obscures which Locative the pattern is about. Compounding it, the required Accusative
person is `dzieci`, which is Nominative/Accusative syncretic, so the row's other
complement is invisible too.

**Replacement PL: `Nauczycielka uczy uczniów o polskich zwyczajach.`**
**Replacement EN: "The teacher teaches the pupils about Polish customs."**

One Locative, governed; `uczniów` is unmistakably non-Nominative (Nom. `uczniowie`),
so the Accusative complement becomes visible; and it removes one of three `dzieci`
occurrences in a single lemma.

### I. `uczyć` school-subject example uses syncretic `dzieci` — **ADOPT**

Current: `Pani Nowak uczy dzieci matematyki.` The row is Genitive subject (required)
plus Accusative learner (optional). `dzieci` is syncretic across Nominative,
Accusative **and** Genitive plural — so beside `matematyki`, a learner may reasonably
parse two Genitives and never see the optional Accusative at all.

Note that the obvious masculine-personal fix does not work here: `uczniów` is
Accusative = Genitive for masculine-personal plurals, which would preserve the
confusion precisely because this row's sibling complement *is* Genitive. A feminine
singular is the only shape that separates the two cases cleanly.

**Replacement PL: `Pani Nowak uczy moją córkę matematyki.`**
**Replacement EN: "Mrs Nowak teaches my daughter maths."**

`córkę` is unambiguously Accusative (Genitive would be `córki`), contrasting visibly
with Genitive `matematyki`. Consequential edit: the `learnerExplanationEn` inline
gloss "pani Nowak uczy dzieci matematyki" must become "pani Nowak uczy moją córkę
matematyki".

---

## 10. CEFR / priority inversion adjudication

All three mechanical inversion candidates: **KEEP.** None is a true inconsistency.

The governing observation is that CEFR and priority measure **different axes** —
CEFR is difficulty, priority is usage frequency — so they are permitted to cross.
Crucially, in each case the apparent inversion resolves into two *separately
consistent* conventions.

| Candidate | Current | Verdict | Reason |
|---|---|---|---|
| `pisać/do-genitive-accusative-content` (A1/A1 common) vs `pisać/dative-topic` (A2/A2 core) | as authored | **KEEP** | Two orthogonal conventions applied without exception across all 13 rows: CEFR tracks the *construction* (Accusative noun easier than topic PP or clause), priority tracks the *recipient form* (bare Dative = `core`, `do` + Genitive = `common`). Verified pairwise: `dative-topic` core / `do-genitive-topic` common; `dative-accusative-content` core / `do-genitive-accusative-content` common. Consistent, not inverted. |
| `napisać` (same pair) | as authored | **KEEP** | Exact mirror of `pisać`; same reasoning. |
| `pasować/na-accusative-fitted-object` (A2/A2 common) vs `pasować/dative-evaluator-do-genitive-reference` (A2/B1 core) | as authored | **KEEP** | Frequency justifies it directly: the Dative-evaluator construction (`Ten kolor mi do ciebie nie pasuje`) is everyday high-frequency Polish, while physical `na` + Accusative fit (`pasuje na mój palec`) is genuinely narrower. `pasować` carries four `core` rows and exactly one `common` — the narrowest one. |

No CEFR or priority value should change before freeze. Mechanical normalization here
would destroy real information.

---

## 11. Recognition-only audit

All four rows reviewed. Recommendation for each is exact.

| Row | Current | Recommendation |
|---|---|---|
| `pozwalać/zeby-enabling` | B1/—, recognition-only, common | **KEEP recognition-only, KEEP B1.** Its rationale is *subject animacy* — an inanimate/abstract subject licensing an event via `żeby`. That rationale is untouched by the clauseKind correction and is independently coherent. |
| `wymagać/situation-requires-content/zeby-clause` | B1/—, recognition-only, common | **KEEP recognition-only, KEEP B1.** Same abstract-situation-subject rationale, applied consistently to the sibling meaning of the same lemma. |
| `zapominać/czy-dependent-clause` → `interrogative-forgotten-content` | B1/—, recognition-only, common | **RECOMMEND CHANGE to `recognition: A2`, `production: A2`, `active-production`, priority `common`.** See reasoning below. **HD-1.** |
| `kłócić się/czy-dependent-clause` → `interrogative-disputed-content` | B1/—, recognition-only, common | **RECOMMEND CHANGE to `recognition: A2`, `production: A2`, `active-production`, priority `common`.** **HD-1.** |

Reasoning for the two changes — this is not inertia-breaking for its own sake:

1. **The recorded rationale does not survive its own premise.** Both were justified as
   "embedded yes/no question considered comprehension-first" — a rationale about
   `czy` being a distinct, harder thing. The correction establishes that it is not a
   distinct thing.
2. **The corpus already teaches this exact construction productively.** `wiedzieć`'s
   A2/A2 active-production row *is* an embedded `czy` yes/no clause
   (`Nie wiem, czy zdążymy na pociąg.`). Holding these two at B1 recognition-only
   while teaching the identical structure at A2 elsewhere is incoherent.
3. **The convention is otherwise exceptionless.** All 14 current `interrogative` rows
   are A2/A2 active-production. All 19 `ze` rows and all 11 `direct-speech` rows are
   A2/B1 active-production. Left uncorrected, these two would be the only 2 of 16
   interrogative rows deviating.
4. **Neither classification was ever approved.** The B2 risk review (residual question
   3) and B3 risk review (residual question 1) both filed these as open questions
   requiring human confirmation of "intended curriculum pacing". No answer exists in
   the repository.

This is the one place where I recommend a change but still route it to a human,
because it alters the published product surface from **220/4 to 222/2** and because a
human question on exactly this point was asked twice and never answered. My
recommendation is firm; the decision is properly theirs.

---

## 12. Same-shape semantic-group audit

All 14 same-lemma cross-meaning signature groups were reviewed against
`internalScope`, `glossesEn`, `learnerExplanationEn`, and the primary examples.

| # | Lemma | Shared shape | Classification |
|---|---|---|---|
| 1 | `próbować` | Genitive object | **SEMANTIC CONTROL SUFFICIENT** — `Próbuję szczęścia` vs `Próbuję zupy`; explicit non-merge statement in scope |
| 2 | `pozwalać` | infinitive content | **SUFFICIENT** — subject animacy is *visible* in the examples (`Pozwalam…` vs `Internet pozwala…`) |
| 3 | `wymagać` | Genitive + optional `od` | **EDITORIAL CORRECTION REQUIRED** — see P8-SR-001 below |
| 4 | `wymagać` | `żeby` + optional `od` | **SUFFICIENT** — both subjects explicit and contrasting (`Szef…` vs `Sytuacja…`) |
| 5 | `należeć` | `do` + Genitive | **SUFFICIENT** — `Ten dom należy do sąsiadki` vs `Należę do klubu sportowego` |
| 6 | `chcieć` | infinitive | **SUFFICIENT** — the conditional-form restriction is stated in scope and visible (`Chcę…` vs `Chciałbym…`) |
| 7 | `chcieć` | `żeby` | **SUFFICIENT** — same mechanism |
| 8 | `robić` | Accusative object | **SUFFICIENT** — `Robię ciasto` vs `Robię pranie` |
| 9 | `rozumieć` | Accusative object | **SUFFICIENT** — `Rozumiem żart` vs `Rozumiem cię jak nikt inny` |
| 10 | `zgadzać się` | direct-speech content | **SUFFICIENT** — notably well controlled: the quoted string is identical ("Zgadzam się") and the distinction is carried entirely by the framing sentence, which is the only place it *can* be carried |
| 11 | `polecać` | Accusative + optional Dative | **EDITORIAL CORRECTION REQUIRED** → sufficient after the §8 English fix |
| 12 | `móc` | infinitive content | **SUFFICIENT** — `Mogę podnieść tę walizkę` vs `Czy mogę otworzyć okno?` |
| 13 | `kochać` | Accusative object (×3) | **EDITORIAL CORRECTION REQUIRED** → sufficient after the §9C gloss fix; examples (person / place / thing) are already well separated |
| 14 | `korzystać` | `z` + Genitive | **SUFFICIENT** — resource vs advantage is clear, and the example pair usefully shows the `z`/`ze` alternation |

**Eleven sufficient; three require editorial correction**, all three already covered
by recommendations elsewhere except the new one below.

### P8-SR-001 — new finding: `wymagać/person-requires-behavior/genitive-required-content`

Current: `Wymaga lojalności od pracowników.` / **"It requires loyalty from employees."**

This meaning is defined in its own `internalScope` as "**A person** requiring conduct
or a trait", and the *entire* distinction from the sibling
`situation-requires-content` meaning — which shares an identical signature — is
subject type. Yet:

- the Polish subject is dropped (natural Polish, but unrecoverable in an isolated
  teaching sentence), and
- the English supplies **"It"**, which asserts an *inanimate* subject and therefore
  directly contradicts the meaning's own definition and teaches the sibling meaning.

The sibling row shows an explicit abstract subject (`Wyjście z nałogu wymaga silnej
woli`), so the pair a learner compares is [no subject] vs [abstract subject] — giving
no evidence at all for the person reading.

**Recommended PL: `Szef wymaga lojalności od pracowników.`**
**Recommended EN: "The boss requires loyalty from employees."**

`Szef` is already established for this exact meaning in the same record's sibling
`żeby` row, so this is internally consistent rather than novel. New Polish wording →
**provenance rerun required**.

This is a genuine semantics/translation defect that no structural scan could surface,
which is why it did not appear in the mechanical queue.

---

## 13. Role / relationType audit

Applying the task's stated principles — the enum is intentionally coarse, differing
semantics do not compel differing roles, identical syntax does not compel differing
roles, and no new enum value may be invented.

| Item | Assessment | Verdict |
|---|---|---|
| `wiedzieć/accusative-known-content` uses `content` while 19 other required-Accusative rows use `object` | Genuine cross-batch convention divergence — and sharper than the audit stated, since `rozumieć/accusative-content` has near-identical semantics yet uses `object`. But both learner phrases are *accurate* for their rows ("what is learned, said or done" fits knowing a fact; "what it applies to" fits understanding a joke). The B7 matrix chose `content` deliberately, and `p8-4b-wiedziec-exact-pattern-shapes` pins it. | **NOT A DEFECT — REMAIN.** Normalizing would flatten a defensible distinction and churn a guard, a digest and a test for no learner benefit. Recorded as a Phase 4C role-vocabulary review item. |
| Same `z` + Genitive form spans `target` (motion source), `topic` (`cieszyć się`), `object` (`korzystać`) | Semantically motivated and correct; a single surface form legitimately serves three roles | **NOT A DEFECT — REMAIN** (motion subset carries the §6 debt) |
| Required Instrumental: `means-method/means` (motion vehicles) vs `lexical-frame/object` (`cieszyć się`, `martwić się`) | Genuinely different relations — instrument of travel vs. governed object | **NOT A DEFECT — REMAIN** |
| Required `z` + Instrumental: `interlocutor` (meeting/agreement/quarrel) vs `topic` (coping/cessation) | Semantically motivated | **NOT A DEFECT — REMAIN** |
| Accusative + `za` + Accusative: `object,target` (taking) vs `interlocutor,topic` (apology) | Semantically motivated | **NOT A DEFECT — REMAIN** |

**No role or `relationType` value should change before freeze.** No new enum value is
proposed. The single real architectural gap is the missing `source` role (§6).

---

## 14. All-optional audit

Confirmation pass over all six all-optional patterns. For each, the source supports
optionality (parenthesised positions in the frozen Składnia), the explanation
communicates it explicitly, and the primary example realizes the optional structure.

| Pattern | Optionality stated in explanation? | Example realizes? | Verdict |
|---|---|---|---|
| `umówić się/z-instrumental-partner-na-accusative-event` | yes — "Both … are optional" | both | **OK** |
| `gotować/accusative-dish-dative-beneficiary` | yes — "Both … are optional" | both | **OK** |
| `pasować/do-genitive-fit-target` | yes — "one optional target form" | target | **OK** |
| `pasować/na-accusative-fitted-object` | yes — "the alternative optional target form" | object | **OK** |
| `pasować/dative-expectation-holder` | yes — "with an optional Dative" | experiencer | **OK** |
| `jeść/accusative-food-instrumental-implement` | yes — "Both parts are optional" | both | **OK** structurally (explanation length is P8-FR-009, unrelated to optionality) |

**No genuine issues.** No pattern should be split or anchored. The
`pasować/do-genitive-fit-target` (optional) versus
`appearance-harmony/do-genitive-harmony-target` (required) difference is
meaning-scoped, source-driven, and correctly guarded.

---

## 15. Candidate-key semantic freeze audit

All 95 meaning keys, 224 pattern keys and 224 example keys were reviewed for
**semantic durability**, not format (the mechanical audit already cleared format,
scoping and collisions).

### Keys that must change before freeze

| Lemma | Current key | Recommended key | Reason | Affected references |
|---|---|---|---|---|
| `zapominać` | `czy-dependent-clause` | `interrogative-forgotten-content` | Encodes a surface conjunction the corrected structure no longer names; contradicts frozen governance that `czy` is not a type | 1 `patternKeyRef` on its single example |
| `kłócić się` | `czy-dependent-clause` | `interrogative-disputed-content` | Same | 1 `patternKeyRef` on its single example |

**No other key change is recommended.** Categories explicitly examined and cleared:

- **Surface conjunctions.** `ze-*` (19) and `zeby-*` (19) keys name `że` and `żeby`,
  which *are* two of the four frozen bound clause types. Durable.
- **Narrowed realizations.** `do-genitive-destination`, `na-accusative-destination`,
  `w-locative-residence-optional-co-resident`, `u-genitive-provider` and similar name
  the realization, which is exactly what those rows are. A future generalized-role
  model leaves them accurate.
- **Unstable role terminology.** `z-genitive-return-source` (×2) and
  `z-genitive-source` (×2) say *source* while the machine role says `target`. This is
  the reason they are durable, not a reason to change them: if Phase 4C adds a
  `source` role the keys become more correct; if it does not, they remain accurate.
  **Renaming them to match `target` would be actively harmful** and is not proposed.
- **Example-dependent semantics.** All 224 example keys are `primary`. No key
  incorporates sentence wording. Maximally durable.
- **Temporary workarounds.** The 11 `direct-speech` pattern keys depend on a private
  staging clauseKind whose canonical status is deferred to Phase 4C. Flagged as a
  **watch item, not a change**: if 4C ever rejects the construction the rows are
  removed rather than renamed, so no key-naming decision is pending here.

### Classification

**READY AFTER SPECIFIED KEY CHANGES** — the two renames above and nothing else.

---

## 16. Architecture debt classification

| Class | Items |
|---|---|
| **PHASE 4B DEFECT** (must fix before key freeze) | P8-FR-001, P8-FR-002 (clauseKind + keys + explanations + one `internalScope`); P8-FR-004 (B2/B3 digest recompute + new positive guards) |
| **PHASE 4C ARCHITECTURE DEBT** (faithful enough to freeze) | P8-FR-003 / P8-SR-003 (missing `source` role, 7 rows); `odpowiadać/direct-speech` canonical enum support; generalized roles verified-but-unrepresented (`GDZIE`/`SKĄD`/`KTÓRĘDY`, ~8 families); P8-FR-007 role-vocabulary granularity (`content` vs `object`); item D `kochać` + infinitive register observation |
| **EDITORIAL POLISH** (optional quality; recommended) | P8-FR-006 (`polecać` A4 EN); P8-FR-008 (`musieć`); P8-FR-009 (`jeść`); P8-FR-010 (`kochać` gloss); P8-FR-011 + P8-FR-012 (`uczyć` ×2); item E (`przepraszać` EN); item F (`życzyć` explanation); P8-SR-001 (`wymagać` — strongest of these, borders on defect); P8-SR-002 (`móc` guard signature) |
| **NO ACTION** | P8-FR-013 (CEFR/priority); P8-FR-014 (duplicate English); P8-FR-015 (key scoping); item D; item G (`korzystać`); 11 of 14 same-shape groups; all 6 all-optional patterns; all 18 generalized-role families |

**P8-SR-002 (new finding).** `p8-4b-moc-no-question-clause` forbids the signature
`{type: clause, clauseKind: czy}`. The B6 matrix documents its purpose as ensuring
"the 'no question complement' rule survives even if the shape set is later
legitimately revised." Once `czy` no longer occurs anywhere in the corpus, that guard
protects against a value nobody would author, while `clauseKind: interrogative` — the
value that *would* actually be authored on `móc` — is caught only by the shape rule
the guard exists to be independent of. **Recommend changing the signature to
`{type: clause, clauseKind: interrogative}`.** The B6 historical test pins the rule
**ID**, not its configuration, so this does not break the ID assertion.

---

## 17. Final reconciliation queue after semantic review

All 15 mechanical items, with before/after status. Nothing dropped or merged.

| ID | Before | After | Disposition |
|---|---|---|---|
| P8-FR-001 | BLOCKING | **FIX BEFORE FREEZE** (+ HD-1 on status/CEFR) | Confirmed defect; clauseKind → `interrogative`, key → `interrogative-forgotten-content`, explanation + `internalScope` rewritten |
| P8-FR-002 | BLOCKING | **FIX BEFORE FREEZE** (+ HD-1) | Confirmed defect; clauseKind → `interrogative`, key → `interrogative-disputed-content`, explanation rewritten |
| P8-FR-003 | BLOCKING | **HUMAN DECISION** → **DEFER TO PHASE 4C** | Downgraded on evidence; keys already encode source; scope widened to 7 rows (P8-SR-003). HD-2 |
| P8-FR-004 | BLOCKING | **FIX BEFORE FREEZE** | B2/B3 digest recompute plus new `require-exact-pattern-shapes` guards for `zapominać` and `kłócić się` |
| P8-FR-005 | REVIEW | **11 CLOSED — NO ACTION; 3 OPTIONAL EDITORIAL** | `wymagać` (P8-SR-001), `polecać`, `kochać` gloss; all others semantically sufficient |
| P8-FR-006 | REVIEW | **OPTIONAL EDITORIAL — ADOPT** | EN "orders" → "instructs"; Polish unchanged; A4 stays active-production |
| P8-FR-007 | REVIEW | **CLOSED — NO ACTION** | Both role assignments accurate; recorded as 4C vocabulary item |
| P8-FR-008 | REVIEW | **OPTIONAL EDITORIAL — ADOPT** | Drop meta clause; 40 → 22 words |
| P8-FR-009 | REVIEW | **OPTIONAL EDITORIAL — ADOPT** | Return negation to grammar ownership per frozen instruction; 64 → 40 words |
| P8-FR-010 | REVIEW | **OPTIONAL EDITORIAL — ADOPT** | Reorder and widen gloss; fixes an under-inclusive gloss, not just ordering |
| P8-FR-011 | REVIEW | **OPTIONAL EDITORIAL — ADOPT** | New PL/EN; removes second Locative and syncretic person |
| P8-FR-012 | REVIEW | **OPTIONAL EDITORIAL — ADOPT** | New PL/EN; `córkę` separates Accusative from Genitive |
| P8-FR-013 | REVIEW | **CLOSED — NO ACTION** | Two orthogonal, internally consistent conventions; not inversions |
| P8-FR-014 | INFORMATIONAL | **CLOSED — NO ACTION** | Five duplicate English pairs produce no ambiguity; natural translation prevails |
| P8-FR-015 | INFORMATIONAL | **CLOSED — NO ACTION** | Parent-scoped composites unique; authorized by schema lock |

New semantic-pass findings, carried as distinct IDs so implementation cannot lose them:

| ID | Item | Disposition |
|---|---|---|
| P8-SR-001 | `wymagać` person-subject example/translation contradicts its own meaning definition | **OPTIONAL EDITORIAL — ADOPT** (strongest of the editorial set) |
| P8-SR-002 | `p8-4b-moc-no-question-clause` signature becomes vacuous after correction | **FIX WITH THE CORRECTION PASS** |
| P8-SR-003 | Source-role debt extends to `kupować`/`kupić` seller and `zamawiać` provider (7 rows total) | **DEFER TO PHASE 4C** (folded into HD-2) |

---

## 18. Human decision table

Only genuine policy / architecture / product tradeoffs appear here. Everything else
in this report is a direct recommendation backed by frozen evidence.

| Decision ID | Lemma(s) | Issue | Current state | Recommended decision | Alternative(s) | Impact if accepted | Impact if rejected | Key change? | Content change? | Guard/test change? | Phase 4C impact? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **HD-1** | `zapominać`, `kłócić się` | After the clauseKind correction, should these two rows keep `B1/—` recognition-only, or align to the exceptionless A2/A2 active-production interrogative convention? The recorded rationale ("embedded yes/no is comprehension-first") is the premise the correction dissolves, and `wiedzieć` already teaches an embedded `czy` clause at A2/A2 active-production. Both B2 and B3 risk reviews asked a human to confirm this pacing; neither was ever answered. | `recognition: B1`, no `production`, `recognition-only`, `common` | **Change both to `recognition: A2`, `production: A2`, `active-production`, `common`** | (a) keep `B1/—` recognition-only; (b) `A2/B1` active-production, matching the sibling `że` rows instead of the interrogative convention | Product split moves 220/4 → **222/2**; all 16 interrogative rows become uniform; two more productive patterns for learners | Two rows remain the only interrogative rows not taught productively, teaching a structure at B1 that the corpus teaches at A2 elsewhere | No (independent of the two renames) | Yes — `cefr`, `teachingStatus` on 2 patterns | Yes — B2/B3 digests, `test_priority8_phase4b_progress.py` 220/4 assertions, batch report counts | None |
| **HD-2** | `wracać`, `wrócić`, `wyjść`, `wyjechać`, `kupować`, `kupić`, `zamawiać` | The locked role enum has no `source`, so 7 origin participants are encoded `role: target`. Candidate content is faithful (keys, `internalScope` and explanations all say *source*/*from*), but the runtime maps `target` to "what it is aimed at", which inverts the direction. | 7 rows use `role: target` | **Accept `target` as a governed coarse fallback for Phase 4B; defer a `source` role to Phase 4C, and record a binding 4C constraint that these 7 rows must not receive the `target` projection phrase** | (a) add a `source` role now — **not available**, Phase 4B forbids inventing roles; (b) defer with no recorded constraint — risks silently shipping the inverted phrase in 4C | Keys freeze as-is; debt is explicit and bounded to 7 named rows; 4C gets a concrete constraint | Debt stays implicit; 4C may project a directionally wrong learner phrase onto 7 rows | No — keys already encode `source` and are durable either way | No | No | **Yes** — either a role-enum addition (runtime + tooling + validator + released Priority 7 corpus re-audit) or a projection-mapping constraint |

Deliberately **not** escalated to the human, because the evidence makes one answer
clearly superior: the two clauseKind corrections and their key renames (§5); the
`polecać` English (§8); the seven Batch 7 editorial adoptions and two keeps (§9);
the CEFR/priority keeps (§10); the role/`relationType` keeps (§13); P8-SR-001 and
P8-SR-002.

---

## 19. Recommended implementation plan

**Nothing below has been implemented.** Execute only after HD-1 and HD-2 are answered.
Two constraints apply throughout: the four SHA-locked schema matrices (B4–B7) must
**not** be edited, and historical batch reports must receive **appended, labelled
correction notes** rather than rewritten claims, following the existing "superseded
values are explicitly labelled" convention.

### Group A — candidateContent structural changes
`editorial/priority-8-phase4-staging.json`: `zapominać` `czy` → `interrogative`;
`kłócić się` `czy` → `interrogative`. If HD-1 is accepted, also `cefr` and
`teachingStatus` on the same two patterns.
→ **CODEX.** Deterministic, exactly located, linguistically frozen.

### Group B — candidate key changes
`editorial/priority-8-phase4-staging.json`: two `candidatePatternKey` values plus the
two matching `patternKeyRef` values. Must be applied as a paired rename; a validator
run must confirm zero orphans.
→ **CODEX.**

### Group C — example / translation changes
`editorial/priority-8-phase4-staging.json`:
`polecać` A4 `en`; `przepraszać/accusative-person-ze-explanation` `en`;
`wymagać/person-requires-behavior/genitive-required-content` `pl` **and** `en`;
`uczyć/accusative-person-o-locative-taught-topic` `pl` **and** `en`;
`uczyć/accusative-learner-genitive-school-subject` `pl` **and** `en`.
**Three new Polish sentences are introduced** (`wymagać`, `uczyć` ×2) — quiet-reuse
and provenance scans **must be rerun** for these three, and `candidateOrigin` must
stay `editorial-generated` unless a scan says otherwise.
→ **CLAUDE OPUS** for the provenance/quiet-reuse judgment on the three new Polish
sentences; **CODEX** for the mechanical string replacement of all nine fields.

### Group D — learnerExplanation / internalScope / gloss changes
`editorial/priority-8-phase4-staging.json`: `zapominać` explanation + `internalScope`;
`kłócić się` explanation; `musieć` explanation; `jeść` explanation; `życzyć/…-zeby-…`
explanation; `kochać/strong-liking` `glossesEn`; `polecać` A4 explanation gloss;
`uczyć/…-school-subject` explanation inline gloss.
→ **CODEX**, applying the exact strings given in §5, §8 and §9 verbatim.

### Group E — guard changes
`tests/fixtures/priority8_phase4b_authoring_rules.json`:
add `p8-4b-zapominac-exact-pattern-shapes` and `p8-4b-klocic-sie-exact-pattern-shapes`
(closing the P8-FR-004 blind spot for both lemmas, `exactMeaningSet: true`);
change `p8-4b-moc-no-question-clause` signature `czy` → `interrogative` (P8-SR-002).
Registry goes 72 → 74 rules; `registryVersion` stays 2.
→ **CODEX.**

### Group F — historical test / digest changes
`tests/test_priority8_phase4b2_batch02.py` (`BATCH_2_APPROVED_DIGEST`);
`tests/test_priority8_phase4b3_batch03.py` (`BATCH_3_APPROVED_DIGEST`);
`tests/test_priority8_phase4b6_batch06.py` (B6 digest — `polecać`);
`tests/test_priority8_phase4b7_batch07.py` (B7 digest — `musieć`, `jeść`, `kochać`,
`uczyć`, `przepraszać`, `życzyć`); plus B3's digest again for `wymagać`.
`tests/test_priority8_phase4b_progress.py` if HD-1 changes the 220/4 assertions.
Add the two new guard IDs to the guard-registry count assertions.
Expected test total rises above 270 by the number of new guard assertions added.
→ **CODEX.** Digest recomputation is exactly the deterministic rewrite CODEX is best
suited to, once the linguistic decisions are frozen.

### Group G — report changes
Appended, clearly labelled correction notes to
`reports/priority-8-phase-4b2-batch-02-authoring.md`,
`…-4b2-batch-02-risk-review.md`, `…-4b3-batch-03-authoring.md`,
`…-4b3-batch-03-risk-review.md`, `…-4b6-batch-06-authoring.md`,
`…-4b7-batch-07-authoring.md`; plus a new
`reports/priority-8-phase-4b-final-correction-implementation.md` recording what was
applied. **Do not edit the B4–B7 schema matrices** (SHA-locked).
→ **CLAUDE SONNET** — prose that must be accurate and consistent with history but
requires no new linguistic judgment.

### Group H — Phase 4C-deferred items
No repository change now. Record in the Phase 4C handoff: the `source` role decision
(7 rows, HD-2); `odpowiadać/direct-speech` canonical enum support; the
verified-but-unrepresented generalized roles; the `content`/`object` role-vocabulary
review; the `kochać` + infinitive register observation.
→ **CLAUDE OPUS** when Phase 4C handoff authoring begins.

---

## 20. Candidate-key freeze readiness

**Gate: C — HUMAN ADJUDICATION REQUIRED BEFORE FREEZE.**

The key set is one step away from freeze: exactly two renames, both clear-cut, both
specified verbatim in §5.2 and §15. But gate **B** requires that *no unresolved policy
decision* remain, and one does — **HD-1** lands on the same two rows whose keys are
being renamed. Answering HD-1 after the rename would force a second pass over the same
two batch digests and their historical locks. HD-2 must also be answered, though it
does not itself gate the keys.

**No key is frozen by this report.**

---

## 21. Phase 4C carry-forward list

1. **Source role (HD-2).** 7 rows (`wracać`, `wrócić`, `wyjść`, `wyjechać`
   `z` + Genitive; `kupować`, `kupić` seller `od` + Genitive; `zamawiać`
   `u` + Genitive). Either add a `source` role or bind the projection layer never to
   apply `target`'s "what it is aimed at" phrase to them.
2. **`direct-speech` clauseKind.** Private staging value on 11 rows; canonical/runtime
   enum support still deferred. `odpowiadać/direct-speech` additionally has no
   frozen source label and is a documented policy addition.
3. **Generalized roles verified but unrepresented.** `GDZIE` for `pracować`,
   `pokazywać`, `czytać`, `uczyć` (school sense), `zapraszać`; `SKĄD` for `wiedzieć`;
   source/goal for `przynosić`; appointment time for `umówić się`; `KTÓRĘDY`
   corpus-wide.
4. **Role vocabulary granularity.** `content` vs `object` for required Accusative
   (`wiedzieć` vs `rozumieć` and 19 peers). Not a defect; a coarse-enum artifact.
5. **`kochać` + infinitive register.** No frozen evidence supports a non-`neutral`
   register; revisit only if Phase 4C obtains register evidence.
6. **Regression coverage for B1/B2.** Even after the two new guards, Batch 1 has no
   declarative semantic guards. Phase 4C should confirm the validator/digest layer is
   sufficient there.

---

## 22. Test / safety result

| Check | Result |
|---|---|
| `python3 validate_priority8_staging.py` | **PASS** — "Priority 8 4B7 staging revision 8 is read-only valid (68 lemmas, 21 constrained records, 12 global constraints)" |
| Eleven Phase 4B suites together via `python3 -m unittest` | **270 tests, 59.685s, OK** |
| `git status --short` | single added path: `reports/priority-8-phase-4b-final-semantic-reconciliation.md` |
| `git remote -v` | zero remotes |
| `git config --get push.default` | `nothing` |
| Pre-push hook | executable, fail-closed (exit 1) |
| Files modified | **none** |
| Files added | **one** — this report |

No `candidateContent`, staging, guard, test, validator, schema, canonical, runtime,
audio, or product file was touched. No ID was allocated. No key was frozen. No push,
deploy, or integration occurred.
