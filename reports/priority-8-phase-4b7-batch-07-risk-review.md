# Priority 8 Phase 4B7 — Batch 07 risk review

## Overall assessment

Batch 7 implements the frozen, independently reviewed Batch 7 schema matrix
exactly: 9 lemmas, 13 meanings, 23 patterns, 23 examples, 23/23 conformance on
keys, `relationType`, roles, complements and requiredness, with zero extra and
zero missing rows. No frozen row was reinterpreted and no fresh linguistic
research was performed.

The residual risks are **semantic and editorial, not structural**. Structural
guards now pin every shape, requiredness value and meaning inventory in the
batch; what they cannot pin — which semantics sits under two pairs of
structurally identical rows, and what future example wording does to two
lexical-identity boundaries — is documented here and in the authoring report
rather than overclaimed.

## Per-lemma audit

### `musieć` — realization compression

One meaning, one infinitive pattern. The frozen source's unrestricted-subject
and zero-subject schemas differ only in whether a subject is realized, and the
subject is not a complement in the locked model, so a second pattern would have
been a byte-identical duplicate misrepresenting the source as offering two
lexical alternatives. Three independent frozen statements license the
compression. **Risk: low.** The explanation mentions personal and impersonal
realization without inventing an impersonal Polish example, deliberately, since
no such example is licensed by the frozen evidence.

### `wiedzieć` — `SKĄD` and interrogative handling

Four alternatives under one meaning; all four complements required; no
cumulative row. The optional generalized `SKĄD` is recorded in `internalScope`
as **verified but unrepresented**, explicitly distinguished from rejected
evidence, and guard C's single-signature allowlist makes any `od`/`z`/`spod`
concretization impossible. The interrogative row is `clauseKind: interrogative`;
its example realizes it with `czy` and the explanation teaches `czy` as one
realization beside `gdzie`/`kiedy`. **Risk: low.** One reviewer-visible
judgement: the interrogative example is negated (`Nie wiem, czy…`) because
positive `wiedzieć, czy…` is unnatural Polish; negation does not alter a clause
complement, so nothing is obscured.

### `jeść` — all-optional row and grammar-owned negation

The single all-optional row keeps both complements `required: false`, and the
example realizes **both** (`zupę` + `łyżką`), so learners see the full frame
even though neither part is obligatory. The Instrumental takes `role: means`
per the frozen matrix, on the live `brać`/`wziąć` precedent.

The negation boundary is stated in the learner explanation in the narrow,
correct form: the Genitive after a negated verb is **the general Polish rule
for negated objects** — ordinary, correct Polish — and is simply not authored
here as a lemma-specific pattern. **Nothing in the record implies the Genitive
is ungrammatical, marginal, or absent from Polish.** Guards D and E block a
lexical Genitive row structurally. **Risk: low**, but this wording is the single
most misreadable sentence in the batch and deserves reviewer attention.

### `pić` — Genitive exclusion

One required Accusative; no Genitive, partitive, quantity, container or source
complement; guard G blocks any Genitive row. The animate-subject restriction is
in `internalScope` only, since the locked model has no selectional-restriction
field. Alcohol-use, plant-absorption, footwear and figurative senses are
excluded by scope. **Risk: low.**

### `kochać` — three-meaning semantic separation

**Highest semantic risk in the batch.** Three meanings, four patterns, with
three structurally identical Accusative rows. Guard H pins the three-key
inventory and confines the infinitive to `strong-liking`, but a swap of the
three Accusative rows between meaning keys is **structurally invisible** —
verified empirically, and expected.

Mitigation is entirely editorial and deliberately sharp: distinct
`internalScope`, distinct `glossesEn`, distinct explanations, and examples
chosen so the intended meaning is unmistakable — a person (`swoją babcię`), an
emotional bond to a place (`swoje rodzinne miasto`), and an everyday preference
(`czekoladę`). The Batch 7 historical lock asserts that the scopes, glosses and
explanations are pairwise distinct, so the semantic carriers cannot be silently
collapsed. **Reviewers must read all three examples together** and confirm none
of them could be reassigned to another meaning.

### `przepraszać` — role and requiredness asymmetry

`role: interlocutor` on the person in both rows, per the frozen matrix
(released `prosić`/`pytać` precedent for an Accusative addressee in a speech
act). The asymmetry is exact: required with `za + Accusative`, optional with the
`że` clause, normalized in neither direction, with no combined row. The `że`
example realizes the optional person so learners see the participant while the
explanation states it is optional. Both examples use finite `przeprasza` /
`przepraszam` with complements, so neither reads as the bare discourse-marker
`przepraszam`. **Risk: low.**

### `życzyć` / `życzyć sobie` identity

Required Dative in both rows; Genitive and `żeby` are strict alternatives; no
infinitive. Neither example contains `sobie`, and the historical lock asserts
this directly. The rule-target identity check additionally prevents record 68
from being renamed to `życzyć sobie`.

**Documented limit:** no guard primitive reads example text, so a *future*
example edit could still drift the identity. `require-lexical-identity` is an
inclusion test and cannot express a prohibition, so no guard was invented to
pretend otherwise. **Risk: low now, editorial thereafter.**

### `korzystać` — same-shape semantic distinction

Two meanings over one identical `z + Genitive` shape with `role: object` on
both, per the frozen matrix; assigning different roles to force a structural
difference would have encoded a distinction the locked enum does not have and
would have contradicted the frozen evidence that the form is identical. Guard L
pins the two-key inventory; the meaning-to-key attachment is **not**
structurally enforceable, verified empirically.

Mitigation: contrasting examples that cannot be confused — public transport as
a service used, student discounts as an advantage taken. Neither example reads
as generic "use". **Reviewers must confirm the two examples stay on opposite
sides of that line.**

### `uczyć` — six schemas, identity, and `GDZIE`

Six strict alternatives; every row has exactly two complements, so no maximal
frame exists; sense-1 complements are all required and the sense-2 learner is
optional. Guard N pins all of this, and because every authorized row carries the
Accusative learner, the bare released `uczyć się` shapes (`genitive content`,
`infinitive content`) are unauthorable — verified by mutation.

Sense-2 `GDZIE` is recorded as **verified but unrepresented**; guard O allowlists
only `o + Locative`, so `w`, `na` and `u` are all blocked, and the
school-subject example deliberately contains **no place phrase at all** to avoid
even the appearance of a concretization. No example contains `się`, asserted by
the lock.

The instruction and school-subject examples were chosen to keep the two meanings
apart: `Babcia uczy wnuczkę cierpliwości` (general instruction, non-school
content) versus `Pani Nowak uczy dzieci matematyki` (school subject).
**Risk: medium-low**, concentrated in example quality rather than structure;
the six sentences warrant close manual reading.

## CEFR / teaching-status edge cases

- `wiedzieć` Accusative at **A1/A2** rather than A1/A1: recognition is trivial
  but production is genuinely constrained, since the slot is in practice
  pronominal (`to`, `wszystko`, `coś`). The explanation says so.
- `kochać` idea/place and strong-liking rows at **A2/A2 common** although
  structurally A1-simple: the difficulty is semantic, and meaning-driven CEFR is
  precedented (frozen `zapominać` Accusative at A2/A2).
- `korzystać` benefit-from at **A2/A2 common** while resource-use is
  **A2/A2 core**: identical structure, so the level is identical and only the
  usage priority differentiates frequency. No artificial CEFR gap was invented
  to make the meanings look different.
- `uczyć` `o + Locative` at **A2/A2 common**, following the corpus-wide
  `o + Locative` convention rather than being pushed to B1 for markedness;
  frequency is expressed through `priority: common`.
- **No `recognition-only` row exists in Batch 7.** This is a deliberate,
  documented decision: `recognition-only` must not be used to park an authoring
  concern, and no Batch 7 row is marginal enough to withhold production.

## Example naturalness, aspect and translations

All 23 finite verb tokens were inspected individually and all are imperfective
forms of the exact authored lemma. The Batch 6 failure mode — an example
accidentally using a perfective partner — does not recur. Two near-miss tokens
(`nauczyciela`, `Nauczycielka`) are the **nouns** "teacher" and were explicitly
distinguished from the perfective verb `nauczyć`.

All 23 Polish sentences are unique. All 23 English translations are also unique,
though that was not a constraint: naturalness outranks translation uniqueness,
and no translation was distorted to avoid a duplicate. Two translations are
idiomatic rather than literal (`Życzę ci, żebyś zdał ten egzamin` → "I hope you
pass this exam"; `korzystają ze zniżek` → "take advantage of discounts"), which
is correct for learner-facing English.

## Provenance

Two-layer scan, honestly scoped: Layer A compared all 23 sentences against 1665
indexed entities on `card.pl`, `card.ex`, `drill.prompt`, `drill.answer` with
zero matches; Layer B substring-scanned 380 repository text/data files
(17.4 MB) with zero hits. All 23 examples are therefore `editorial-generated`
and no `repository-reuse` claim is made. No sentence was rewritten to dodge a
collision, because none was found.

## Guard limitations — stated, not overclaimed

1. `kochać`'s three identical Accusative rows cannot be semantically separated
   by any structural rule.
2. `korzystać`'s two identical `z + Genitive` rows likewise.
3. No primitive inspects example text, so future `życzyć` / `uczyć` example
   edits could drift toward `życzyć sobie` / `uczyć się` without a guard firing.
4. `musieć`'s personal-versus-impersonal contrast, `pić`'s animate-subject
   restriction, `uczyć` A5's person restriction, and both verified-but-
   unrepresented generalized roles have no structural expression at all; guards
   can forbid every wrong concretization but cannot assert that a correct
   omission was deliberate.

All four are carried in `internalScope`, glosses, explanations, examples and
this review — never claimed as guard-enforced.

## Historical-lock future safety

`tests/test_priority8_phase4b7_batch07.py` follows the Batch 1–6 future-safe
architecture and pins **no** moving lifecycle state: not `phaseStep`, not
`stagingRevision`, not the future-empty count, not review status beyond the
allowed vocabulary, and not the registry total (it asserts the 15 Batch 7 rule
IDs are present plus a lower bound). Batch 7 is the final authoring batch, so
future-empty is currently zero — but the lock must survive the 68-lemma
reconciliation and any review-status progression, so it never depends on those
values.

One authorized correction was required to make this possible batch-wide:
`tests/test_priority8_phase4b6_batch06.py` pinned
`assertEqual(57, len(registry["rules"]))`, the only moving-state assertion in
Batches 1–6 and one its own docstring disclaims. It was replaced with
`assertGreaterEqual(…, 57)`; Batch 6's digest, matrix SHA-256 and all 21
guard-presence assertions are untouched and its 24 tests still pass.

## Items needing independent review

1. Confirm `musieć`'s single-pattern compression and its explanation wording.
2. Confirm `wiedzieć`'s `SKĄD` omission is recorded as verified-but-unrepresented
   and that the negated `czy` example is acceptable.
3. Confirm the `jeść` negation sentence cannot be read as calling the Genitive
   ungrammatical, and that realizing both optional complements is right.
4. Confirm `pić`'s exclusions hold.
5. **Read `kochać`'s three examples together** and confirm no reassignment
   between the three meanings is plausible.
6. Confirm `przepraszać`'s `interlocutor` role and the requiredness asymmetry.
7. Confirm no `życzyć` example drifts toward `życzyć sobie`.
8. **Read `korzystać`'s two examples together** and confirm resource-use versus
   benefit-from is unmistakable.
9. Read all six `uczyć` examples for naturalness, non-reflexive identity, and
   the instruction-versus-school-subject split.
10. Confirm the CEFR edge cases in the section above, and the zero
    `recognition-only` decision.

## Carry-forward reconciliation items — recorded, NOT adjudicated

1. **Older Batch 2/3 `clauseKind: czy`.** Live staging carries
   `clauseKind: czy` for the already-frozen records `zapominać` and
   `kłócić się`, although their frozen Phase 3 evidence is interrogative-
   dependent (`że ZDANIE | ZDANIE PYTAJNOZALEŻNE` and `ZDANIE PYTAJNOZALEŻNE` /
   `ŻE`) rather than a direct literal-`czy` source.
   **Classification: OUT OF SCOPE FOR BATCH 7 AUTHORING; FINAL 68-LEMMA
   RECONCILIATION ITEM.** Those records were not modified, not adjudicated, and
   are not cited as precedent anywhere in Batch 7.

2. **Batch 6 `polecać` A4 directive-strength translation.** The example
   `Trener poleca zawodnikom rozgrzewkę` is currently translated approximately
   as "The coach orders the players to warm up", although the Polish does not
   unambiguously encode that directive force.
   **Classification: OUT OF SCOPE FOR BATCH 7 AUTHORING; FINAL 68-LEMMA
   RECONCILIATION ITEM.** Not modified and not adjudicated here.

## Replacement implications

None. No Batch 7 lemma is reopened, no HOLD is created, no frozen matrix row is
changed, and no reserve is researched or promoted. Independent Batch 7 review
and the final 68-lemma reconciliation remain outstanding.
