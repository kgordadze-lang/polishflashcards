# Priority 8 Phase 4B5 — Batch 05 risk review

This review audits the Batch 5 implementation against the frozen
`reports/priority-8-phase-4b5-schema-matrix.md`. It does not reopen any
linguistic decision the matrix already settled or re-litigate the two
`umówić się` policy adjudications; it checks that authoring faithfully
implements them.

## 1. `oglądać` presentation-context `w + Locative`

The single pattern carries required Accusative object plus optional
`w + Locative`, in one row, never split. The example — "Oglądam ją w nowym
serialu." (I'm watching her in a new series) — deliberately realizes the
optional position with a *presentation context* reading (the series she
appears in), not a viewing-location/medium reading (a TV, a screen, a
building). The `internalScope` and `learnerExplanationEn` both state the
distinction explicitly ("not the TV or place you're watching from"). Risk:
none identified.

## 2. Aspect independence: `oglądać` / `obejrzeć`

`obejrzeć`'s single pattern is bare Accusative only; no `w + Locative` was
imported. `p8-4b-obejrzec-exact-pattern-shapes` structurally pins this
(mutation C confirms an injected `w + Locative` on `obejrzeć` is caught).
The two lemmas' examples use different objects ("w nowym serialu" vs. "ten
film") so no wording is shared either.

## 3. `skończyć`: completion vs. cessation

Two meanings, three patterns: `accusative-task` and `infinitive` under
`activity-completion`; `z-instrumental-ceased-activity` under
`definitive-cessation`. The completion patterns carry no `preposition-case`
complement at all (checked structurally in the historical lock); `z +
Instrumental` appears only in the cessation pattern. The cessation example
("Skończyłem z paleniem." — I'm done with smoking) and its explanation
explicitly flag it as a separate colloquial sense, not a completion variant.
Nothing was inherited from `kończyć` (order 19): `skończyć`'s completion
shape happens to match `kończyć`'s already-approved shape because both are
independently sourced from the identical WSJP `CO`/`BEZOKOLICZNIK`
notation, and `skończyć` additionally carries the cessation meaning
`kończyć` does not.

## 4. `chcieć`: two meanings and the first-person restriction

Desire (Genitive object, optional `od`/`dla`, infinitive, `żeby`) and
polite-request/intention (Accusative object, infinitive, `żeby`) are kept
as fully separate meanings with a structurally load-bearing case contrast
(Genitive vs. Accusative), verified directly in the historical lock. The
first-person past/conditional restriction on the polite-request sense is
not structurally enforceable (no field exists for it), so it is carried
three ways: in `internalScope`'s explicit restriction sentence, in each of
the three patterns' `learnerExplanationEn` ("Use the first-person
conditional chciałbym/chciałabym… not ordinary present-tense chcę"), and in
the examples themselves — all three polite-request examples begin with
`Chciałbym`, verified structurally
(`test_chciec_polite_request_examples_use_first_person_restriction`). The
restriction is a control-plane fact, not a guard-enforceable one; this
limitation is stated honestly in the matrix (§12, limitation 2) and
inherited here without being papered over.

## 5. `robić`: structurally-identical semantic split

`entity-creation` and `activity-performance` share the exact complement
shape (`case:accusative role=object required`) — confirmed identical in the
historical lock. This is not a defect: the matrix already documents that no
guard can distinguish them structurally, and the split is carried entirely
by `candidateMeaningKey`, distinct `internalScope` text (verified non-
identical between the two meanings), distinct `glossesEn`, and maximally
distinct examples: "Robię ciasto." (making/creating a cake) vs. "Robię
pranie." (performing the named activity of laundry) — the second example
deliberately mirrors WSJP's own "pranie" illustration so the performance
sense reads unambiguously as "doing the laundry," not "creating laundry."

## 6. `rozumieć`: person/content split

Content comprehension (Accusative, `że`, interrogative-dependent) and
empathic person understanding (Accusative) are separate meanings; no clause
was attached to the person meaning (verified structurally — the person
pattern's complement set contains no `clause` type). The person-
understanding example — "Rozumiem cię jak nikt inny." (I understand you
like no one else) — was deliberately extended beyond a bare "Rozumiem cię"
to make the empathic reading unambiguous rather than reading as literal
comprehension of spoken words.

## 7. `mieszkać`: residence realization / co-resident distinction

One pattern, required `w + Locative` plus optional `z + Instrumental`, in
one row. The example — "Mieszkam w Warszawie z bratem." (I live in Warsaw
with my brother) — realizes both, so the selected co-resident role is
pedagogically visible rather than merely asserted in prose. The explanation
states `w + Locative` is "a documented residence-place realization, not the
only possible form" and that `z + Instrumental` names "a co-resident you
live with," matching the matrix's binding constraint exactly. No `na`/`u`
alternative was authored.

## 8. `umówić się` all-optional appointment (A1)

`z-instrumental-partner-na-accusative-event` carries exactly two
complements, both `required: false`, confirmed structurally in the
historical lock. Per this task's instruction, the primary example realizes
**both** optional complements — "Umówiłem się z kolegą na kawę." (I arranged
to meet my friend for coffee) — so a complementless-reading risk never
arises: the sentence is fully natural and legible even though neither
participant is structurally required. This remains the sole all-optional
pattern in the entire Batch 1–5 corpus, exactly as the matrix states.

## 9. `umówić się` lossy A2 projection

`do-genitive-appointment-venue` carries required `do + Genitive` (target)
and optional `z + Instrumental` (interlocutor). The `learnerExplanationEn`
states the realization boundary in practical terms ("a documented
realization, not the only possible location form"), while the more
technical framing ("required in THIS product row… not exclusive
government… not epistemically identical to the source `GDZIE` slot") is
correctly kept out of learner-facing text and lives only in `internalScope`
and this matrix, per the brief's instruction not to turn learner copy into
an architecture document. The example — "Umówiłem się z żoną do lekarza."
(I made an appointment with my wife at the doctor's) — realizes the
optional `z` participant too, as instructed.

## 10. `KIEDY` omission boundary

No complement, field, or new type represents `KIEDY` anywhere in the
authored content — verified structurally (`umówić się` has exactly 7
patterns, none carrying any adverbial/time-typed complement, since no such
type exists in the locked schema to misuse). The `internalScope` for
`meeting-arrangement` states the fact explicitly: "A further source-
selected time position (KIEDY) has no documented concrete realization and
is intentionally not represented as any complement." This mirrors the
`czytać` `GDZIE`-as-role-evidence-only precedent from Phase 4B4-A. The fact
is preserved in documentation (this review, the matrix, `internalScope`)
exactly because it *cannot* be preserved structurally — no guard can assert
that a required source position exists and was deliberately left
unauthored.

## 11. `co do + Genitive` architecture deferral

Confirmed independently: `validate_priority8_staging.PREPOSITION_RE =
^[a-ząćęłńóśźż]+$` accepts only a single lowercase Polish word; `co do` is a
two-word compound and fails this pattern. No product row was authored for
it; it is not encoded as `co` or `do` alone (verified — no `umówić się`
complement anywhere has preposition `"co"`); it is not called rejected or
unsupported anywhere in the authored content or this review. It remains
classified **VERIFIED — ARCHITECTURE-DEFERRED FROM PHASE 4B** exactly as the
frozen matrix states, and is carried in the matrix's own Phase 4C backlog
(§19) rather than duplicated here as a second backlog. Neither
`PREPOSITION_RE` nor any schema/validator file was touched by this task.

## 12. `umówić się` reciprocal behavior

Both meanings' `internalScope` state the reciprocal-plural-subject fact
("A reciprocal plural personal subject… may occur without a separate
partner phrase; this is a usage fact, not a second complementless
pattern"). No second, complementless pattern was authored for either
meaning — confirmed structurally (exactly 2 appointment + 5 agreement
patterns, no more).

## 13. `dzwonić` target realizations

`do-genitive-call-target` and `na-accusative-call-target` are each required
in their own row, never combined into one pattern (confirmed: each of the
four `dzwonić` patterns has exactly one complement). Both are labelled
narrowed realizations of generalized `DOKĄD` in `internalScope`, never
exclusive government.

## 14. Rejection of governed `w sprawie`

No `dzwonić` pattern authors `w sprawie + Genitive` — confirmed
structurally (no pattern has preposition `w` at all, and no complement uses
case `"sprawie"`, which is not even a valid case value). This matches the
Phase 3 finding that `w sprawie` appears only in `Połączenia`, never in
`Składnia`, and is therefore collocational rather than governed.

## 15. `powiedzieć` 7→11 normalization

Reproduced independently: the Batch 06 narrative states the primary source
"lists seven separate schemas," and only the decomposition **2 addressee
modes (Dative, `do`+Genitive) × 3 content families (Accusative, `o`+
Locative, grouped clause) + 1 recipientless direct speech** reaches exactly
seven — confirmed by testing that an either/or-addressee reading gives six
and a per-mode clause split gives thirteen, neither of which matches the
source-stated count. The grouped clause-family rows (2 of the 7) expand
1→3 each under the existing clause-kind-per-alternative convention
(identical to the `pisać`/`napisać` precedent), yielding 7 → 11 exactly,
which is what was authored: 5 patterns per recipient mode × 2 modes + 1
direct speech = 11 (verified by direct count of the authored patterns).

## 16. `powiedzieć` direct speech recipientless

`direct-speech-content` carries exactly one complement
(`clause:direct-speech role=content required`) and no recipient of any
kind — verified structurally
(`test_powiedziec_direct_speech_is_recipientless`). No recipient was added
merely because direct speech is naturally addressed to someone in ordinary
conversation; the frozen matrix explicitly excludes this.

## 17. CEFR / status edge cases

All 40 patterns are `active-production`; 0 `recognition-only`. This is not
an artificial "everything is core" quota — each pattern was individually
assessed by construction complexity and learner value (see the authoring
report's CEFR section for the full rationale), and every clause-based
alternative across `chcieć`, `rozumieć`, `umówić się`, `dzwonić`, and
`powiedzieć` received the same A2/B1-or-A2/A2 treatment already established
across Batches 1–4 for `że`/`żeby`/interrogative clauses, not a bespoke
judgment invented for this batch. `powiedzieć`'s two recipient modes carry
identical `cefr`/`teachingStatus` per content family, mirrored exactly —
the Phase 4B4 correction's explicit lesson (classify by content-family
complexity, never by recipient mode) was applied from the start here rather
than corrected after the fact.

## 18. Example naturalness

All 40 examples are short, natural, contemporary declarative sentences.
Every required complement is realized in its example (verified
structurally against the matrix-derived expectation, 40/40). Every
high-priority optional-complement realization instruction from the
authoring brief was honoured: `oglądać`'s `w`, `mieszkać`'s `z`, `umówić
się` A1's both complements, A2's `z`, and all five agreement rows' `z`, and
all ten `powiedzieć` recipient-mode rows' recipients. `chcieć`'s
Genitive-object example realizes one optional participant (`od + Genitive`,
"Chcę pomocy od brata") rather than a forced maximal sentence combining
both `od` and `dla`, per the explicit instruction not to force unnatural
maximal sentences.

## 19. Provenance

0 repository-reuse, 40 editorial-generated. Both quiet-reuse layers were run
for every example. The supplemental raw-text scan caught two genuine
collisions on the first authoring pass — "Chcę odpocząć." and "Chciałbym
kawę." — both verbatim inside grammar-deck `teach[].examples[]`/`table[]`
arrays with no `card`/`drill` id available for a valid `repository-reuse`
citation. Both were rewritten ("Chcę zwiedzić Kraków."; "Chciałbym
herbatę.") rather than misclassified, and the replacements were re-scanned
through both layers with zero further collisions. This is exactly the
"generated text collides verbatim → reclassify or rewrite" discipline the
Phase 4B4 correction established, applied proactively here rather than
caught on review.

## 20. Live-guard scope

Fourteen new rules, all built from the two existing primitives
(`require-exact-pattern-shapes`, `allow-only-preposition-case-signatures`)
plus `require-lexical-identity` for `umówić się`'s `się`. **Explicit
guard-scoping statement, as required:** the `umówić się`
`allow-only-preposition-case-signatures` rule
(`p8-4b-umowic-sie-authorized-preposition-cases`) is **lemma-wide** — it
allowlists the five legitimate `preposition-case` signatures used across
*both* `umówić się` meanings and blocks any signature outside that set, but
it has no meaning-level awareness. An in-memory mutation moved the
appointment-only `do + Genitive` signature into the agreement meaning; the
full registry caught it via `p8-4b-umowic-sie-exact-pattern-shapes`
(`exactMeaningSet`-scoped, per-meaning), and the *same* mutation, checked
against the allowlist rule in isolation, produced **zero issues** —
empirically confirming the allowlist alone provides no meaning/row scoping.
The two rules are therefore complementary and both necessary, exactly as
the independent matrix review required stating. Twenty-three total
mutation proofs were run (A–W plus the isolated-allowlist demonstration);
all structural mutations were caught by their intended rule. Honestly
flagged as non-structural, per the matrix: `KIEDY`'s source-presence,
`co do`'s architecture-deferral rationale, the realization-vs-government
semantic claim, and `umówić się`/`mieszkać`'s participant-restriction facts
— none of these can be or are claimed to be guard-enforced.

## 21. Historical-lock future safety

`tests/test_priority8_phase4b5_batch05.py` follows the Batch 1–4
architecture exactly: it asserts neither `phaseStep`, `stagingRevision`, nor
corpus-wide draft/future-empty boundaries (those live only in
`test_priority8_phase4b_progress.py`), so Batch 6–7 authoring cannot
invalidate it. It pins the Batch 5 content digest, the frozen matrix
SHA-256, exact candidate keys, provenance counts, and the presence of all
14 new live guard rules, plus targeted structural invariants for every
high-risk lemma (§§1–16 above).

## Concerns and open items

- **`robić`'s sense split and `chcieć`'s first-person restriction remain
  non-structural**, exactly as the matrix already documents — not new gaps,
  not worked around by inventing fields.
- **Two architecture backlog items** (`co do + Genitive`, `KIEDY`) were
  faithfully implemented as deferrals, not resolved — resolution is a
  separately-governed Phase 4C decision, correctly out of scope here.
- **No contradiction with the frozen matrix was discovered during
  implementation.** Every one of the 40 rows was directly implementable in
  the locked candidate schema without exception, so no STOP condition was
  triggered.
