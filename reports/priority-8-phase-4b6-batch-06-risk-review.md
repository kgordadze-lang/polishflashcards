# Priority 8 Phase 4B6 — Batch 06 risk review

## 1. Scope

This reviews the actual authored content in
`editorial/priority-8-phase4-staging.json` (Batch 6, orders 52-61) and the 21
new rules in `tests/fixtures/priority8_phase4b_authoring_rules.json` against
the frozen, independently-reviewed `reports/priority-8-phase-4b6-schema-matrix.md`
(SHA-256 `72ab74094d67e4a6c944eaa5b421c2a8b7509ae4bd3b59e102a448fee364fe8c`,
unchanged). Every claim below was independently re-verified against the live
files, not merely against the authoring report.

## 2. `gotować` all-optional pattern

Single pattern, one meaning, both complements `required: false`
(`case:accusative role=object required=false`,
`case:dative role=recipient required=false`), zero required complements —
exactly the frozen §8 shape. Example "Gotuję obiad mojej mamie." realizes
**both** optional complements per §6/§16/§19 of the authoring brief. No
`dla + Genitive` present anywhere. Guard A
(`p8-4b-gotowac-exact-pattern-shapes`) pins this exact shape; mutation-tested
(promotion to required, `dla` addition) — both caught.

## 3. `rezerwować` beneficiary alternatives

Two patterns, one meaning. `A` (`accusative-item-dative-beneficiary`):
required Accusative + optional Dative. `B`
(`accusative-item-dla-genitive-beneficiary`): required Accusative + optional
`dla+Genitive`. Both examples realize the optional beneficiary
("Rezerwuję stolik znajomym.", "Rezerwuję pokój dla rodziców.") per the
brief's preference. No pattern combines both beneficiary forms (verified: no
pattern has more than 2 complements). Sense 2 (`na+Accusative`,
resource/time allocation) is not present anywhere on this lemma. Guards B
(exact shapes) and C (allowlist restricted to `dla+genitive required=false`)
both hold; mutation-tested (maximal Dative+`dla` row, sense-2 `na+Accusative`
import) — both caught, the second by both guards independently.

## 4. `cieszyć się` lexical identity and four cause types

`canonicalLemma` remains `cieszyć się`; no bare `cieszyć` identity exists
anywhere in the 68-record corpus. Four single-complement patterns, one
meaning: `z+Genitive` (`role=topic`, exactly the frozen role — the
independent reviewer's note that the role enum lacks a dedicated
source/stimulus value was respected verbatim, not "improved"),
`na+Accusative` (`role=target`), Instrumental (`role=object`), `że`-clause
(`role=content`). Each example (realized cause / anticipated occasion /
nominal cause / propositional cause) is lexically and semantically distinct,
satisfying the frozen requirement that the four alternatives never read as
interchangeable. No construction transferred from non-reflexive `cieszyć`.
Guards D (lexical identity), E (exact shapes), F (allowlist:
`z+genitive role=topic required=true`, `na+accusative role=target
required=true`) all hold; mutation-tested (merger into one row, `z+Genitive`
role altered to `target`, `się` stripped) — all three caught, the role
alteration caught by both E and F simultaneously (role is part of signature
identity for both primitives).

## 5. `martwić się` overlap vs `bać się`

`canonicalLemma` remains `martwić się`; no bare `martwić` identity exists.
Four single-complement patterns: Instrumental, `o+Accusative`
(`role=topic`), `że`-clause, `interrogative`-clause. The accepted `o+Accusative`
overlap with released `bać się` is preserved as accepted product overlap —
this row is **not** reduced, hidden, or demoted because of it, matching the
human freeze's explicit retention rationale ("distinct worry semantics and
independently verified Instrumental/clause coverage"). No `z+Genitive` (the
`cieszyć się` signature) appears anywhere on this lemma; no construction
transferred from non-reflexive `martwić`. Guards G/H/I hold; mutation-tested
(import of `cieszyć się`'s `z+Genitive`, `się` stripped) — both caught.

## 6. `zgadzać się` two meanings and direct-speech partner boundary

Two meanings (`consent`, 4 patterns; `opinion-agreement`, 3 patterns), lexical
`się` preserved (no bare `zgadzać` identity exists). Consent: `na+Accusative`,
`żeby`-clause, infinitive, direct speech — none carries a `z+Instrumental`
partner (mechanically verified: zero `z`+instrumental complements anywhere
under `consent`). Agreement: `z+Instrumental` (required, standalone),
`że`-clause with optional `z+Instrumental` partner, direct speech with **no**
partner — following the frozen matrix's explicit reading of the source
enumeration ("gives z KIM/CZYM, optional z KIM/CZYM with a że clause, and
direct speech" — the optionality marker attaches to the `że` row only).
Examples for both direct-speech rows use disambiguating surrounding context
(a proposed-action exchange for consent; an opinion-exchange for agreement)
so the semantic split is legible even though the bare complement shape is
identical — this is exactly the non-structural control (§14.2 items 3 and 5
of the frozen matrix) the brief requires. No `na`, infinitive, or `żeby`
appears under `opinion-agreement` (mechanically verified). Guards J/K/L hold;
mutation-tested (consent `na` moved into agreement, partner added to
agreement direct-speech, meanings merged, `się` stripped) — all four caught,
each independently by the exact-shapes guard K, with the lexical/allowlist
guards adding independent confirmation on the last mutation.

## 7. `zapraszać` GDZIE non-concretization

Two patterns, one meaning: `accusative-invitee-na-accusative-event`
(both required), `accusative-invitee-do-genitive-destination` (both
required). The complete preposition set on this lemma is exactly `{na, do}` —
mechanically verified, no `w`, `u`, or `na+Locative` form present. The
separate `KOGO + GDZIE` schema receives no product row, exactly per the
frozen instruction. Guards M (exact shapes) and N (allowlist restricted to
these two exact signatures) both hold; mutation-tested (arbitrary `w+Locative`
row, `na`+`do` merged into one cumulative row) — both caught, the first by
both guards simultaneously.

## 8. `polecać` instruction vs recommendation

Two meanings (`directive-instruction`, 4 patterns, each with optional
Dative; `recommendation`, 1 pattern). No infinitive or clause complement type
appears anywhere under `recommendation` (mechanically verified). The A4
Accusative ("Trener polecił zawodnikom rozgrzewkę.") is glossed and explained
as an action-noun/gerund instruction, never as an ordinary recommendation;
the B1 Accusative ("Polecam ci tę restaurację.") is glossed as a recommended
item. The two meanings' `internalScope` text is distinct (mechanically
verified: `meanings["directive-instruction"]["internalScope"] !=
meanings["recommendation"]["internalScope"]`). Guard O (exact shapes,
`exactMeaningSet: true`) holds; mutation-tested (infinitive imported into
recommendation, instruction alternatives merged, recommendation meaning
removed entirely) — all three caught.

## 9. `polecać` identical A4/B1 structural limitation

A4 (`dative-accusative-action-noun`) and B1
(`dative-accusative-recommended-item`) have the byte-identical complement
multiset `{case:accusative role=object required=true, case:dative
role=recipient required=false}` — mechanically confirmed
(`test_polecac_instruction_and_recommendation_meaning_split` asserts equal
canonical shapes and distinct meaning ownership). Swapping their
`meaningKeyRef` values in an in-memory mutation produces **zero** guard
issues from the full 57-rule registry. This is reported as an **EXPECTED
NON-ENFORCEABLE SEMANTIC LIMITATION**, exactly as documented in the frozen
matrix's §14.2 item 5 (added during the independent-review correction pass,
subject "Clarify Priority 8 Phase 4B6 guard limitations"), not a guard
defect. The semantic split survives only through `internalScope`,
`glossesEn`, `learnerExplanationEn`, the two maximally distinct examples, and
independent review — all four are present and distinct in the authored
content.

## 10. `radzić` Dative asymmetry and independence from `radzić sobie`

Five patterns, one meaning. Dative `required: true` in A1
(`dative-accusative-advice-item`), A2 (`dative-zeby-advice`), A3
(`dative-interrogative-advice`), A4 (`dative-direct-speech-advice`); Dative
`required: false` in A5 (`dative-infinitive-advice`) alone — mechanically
verified pattern-by-pattern
(`test_radzic_dative_requiredness_asymmetry_and_no_sobie_or_z_instrumental`).
No `z+Instrumental` complement appears anywhere on this lemma. No
`requiredLexicalItems` field is present (and the validator independently
forecloses attaching `sobie` to any lemma other than `brać`/`wziąć` — see
§17). `canonicalLemma` remains `radzić`, distinct from the separately
authored `radzić sobie` (order 29). Guards P (exact shapes, pinning the
asymmetry structurally) and Q (`forbid-complement-match` on
`z+instrumental`) hold; mutation-tested (infinitive-row Dative promoted to
required, A1's required Dative demoted to optional, `z+Instrumental` coping
injected, `requiredLexicalItems: ["sobie"]` injected) — the first three
caught by guard P (and the third additionally by Q); the fourth is rejected
by the **validator**, not a guard, confirming a second independent control
layer.

## 11. `pasować` four meanings

Four meanings, five patterns, exactly as frozen: `appearance-harmony` (1,
required `do+Genitive`), `physical-fit` (2, both all-optional:
`do+Genitive` and `na+Accusative`), `typical-appropriateness` (1, required
`do+Genitive` + optional Dative `experiencer`), `expectation-suitability` (1,
optional Dative `experiencer` alone). No generic "fit" meaning was created;
the four `internalScope` texts each name a distinct relation
(harmony/match, physical fit, typicality/reference, expectation/suitability)
and the four meaning keys are semantic, not numbered (`fit-1`/`fit-2` never
appear). Mutation-tested (physical-fit's two rows promoted to required,
sense-5 Dative promoted to required) — both caught by guard R.

## 12. `pasować` repeated `do+Genitive` signatures

`do+Genitive` appears in three of the four meanings with three different
requiredness/role combinations
(`appearance-harmony`: required, no companion; `physical-fit`: optional, no
companion; `typical-appropriateness`: required, with optional Dative
companion). An in-memory mutation moved `physical-fit`'s optional
`do+Genitive` shape into `appearance-harmony`:

- **Lemma-wide allowlist alone** (guard S in isolation) produced **0**
  issues — it cannot place a signature in the correct meaning, exactly as
  the frozen matrix's §14.1 M/N lesson predicts.
- **Meaning-scoped exact-pattern-shapes** (guard R) caught it immediately.

This confirms the matrix's own claim about the two primitives' complementary
roles (meaning ownership vs. signature exclusion) rather than merely
asserting it.

## 13. `pasować` sense-5 `lexical-frame` fallback

`dative-expectation-holder` is authored exactly as frozen:
`relationType: lexical-frame`, single complement
`{type: case, case: dative, required: false, role: experiencer}` — mechanically
confirmed. An in-memory mutation forcing `relationType: subject-experiencer`
on this pattern (with no Nominative subject added) was submitted to the
**live validator**: result, **1 issue** —
`complements: subject-experiencer requires subject and experiencer roles`.
This independently reproduces the frozen §5.9/§18.1 finding that the
architecture genuinely cannot accept `subject-experiencer` here without
inventing a subject complement the exact source does not list. The `Dative`
role remains `experiencer` (not silently downgraded to a generic role),
preserving the structural half of the frozen fact; the richer characterization
is carried in `internalScope` exactly as frozen. No reopening of this
architecture decision occurred.

## 14. `móc` two meanings and question packaging

Two meanings (`ability-possibility`, `permission`), each with exactly one
pattern, each `{type: infinitive, required: true, role: content}` — no other
complement, no `clauseKind` field anywhere on this lemma (mechanically
verified: `clause_kinds == set()`). "Czy mogę otworzyć okno?" is authored
under `permission` using the identical infinitive-only shape; no `czy`
clause, no interrogative clause, no third meaning, no new architecture type
was created. Guards T (exact shapes, `exactMeaningSet: true`) and U
(`forbid-complement-match` on `{type: clause, clauseKind: czy}`) hold;
mutation-tested (`czy` complement added, a third question-pattern added, the
ability meaning+row removed entirely) — all three caught, the first by both
guards simultaneously.

## 15. CEFR / status edge cases

See the authoring report's "CEFR / teaching-status decisions" section for
the full per-row rationale. No pattern was forced to `recognition-only` to
hide a schema concern, and no pattern was defaulted to `active-production`
without independent consideration; every high-attention row named in the
brief (§17 of the authoring task) was individually weighed against register
and frequency, and each was retained `active-production` with an explicit,
documented reason rather than a mechanical default. `36` active-production,
`0` recognition-only is therefore a genuine, examined conclusion, not an
unconsidered uniform choice.

## 16. Example naturalness, translation duplication, provenance

All 37 Polish sentences are pairwise unique (mechanically verified). English
translations are not required to be globally unique and none collide in a
way that would obscure a structural distinction; each translation was chosen
for naturalness first. All 37 examples are `editorial-generated`; both quiet-
reuse layers (1665-entity indexed product corpus + 190-file raw-text sweep
across `data-*.js`, `pp-*.js`, top-level `*.json`, `editorial/*.json`, and
`reports/*.md`) returned zero collisions — reported as complete for the
scope actually scanned, not overstated.

## 17. Guard limitations

Per the frozen matrix's §14.2 (as corrected), structural guards cannot
enforce:

- **`móc`'s ability/permission split** — identical infinitive shape under
  both meanings; `exactMeaningSet: true` pins the meaning-key inventory and
  cardinality but not which semantics sits under which key.
- **`zgadzać się`'s two direct-speech rows** — identical single-complement
  shape under `consent` and `opinion-agreement`.
- **`polecać`'s A4/B1 rows** (§9 above) — identical two-complement shape
  under `directive-instruction` and `recommendation`.
- **`pasować`'s repeated `do+Genitive` signatures** (§12 above) — resolved
  structurally by meaning-scoped exact shapes (guard R), not by the
  lemma-wide allowlist (guard S) alone; the allowlist supplies signature
  exclusion only.

None of these is a guard defect; each is a genuine limit of complement-shape
comparison, and each is independently reproduced above through direct
mutation testing rather than asserted from the matrix text alone. Every case
is compensated by `internalScope`, `glossesEn`, `learnerExplanationEn`, a
maximally distinguishing example, and independent review — all present and
verified in the authored content.

## 18. Historical-lock future safety

`tests/test_priority8_phase4b6_batch06.py` follows the Batch 1-5 future-safe
architecture exactly: it pins the Batch 6 content digest and the Batch 6
guard-ID set, and does **not** assert `phaseStep`, `stagingRevision`, or any
corpus-wide future-empty/draft boundary — those remain the exclusive
responsibility of `tests/test_priority8_phase4b_progress.py`. Later Batch 7
authoring can freely advance `phaseStep`/`stagingRevision`/future-empty
counts without invalidating this test.

## 19. Test results

`python3 validate_priority8_staging.py`:
`PASS: Priority 8 4B6 staging revision 7 is read-only valid (68 lemmas, 21
constrained records, 12 global constraints).`

| Suite | Tests | Result |
|---|---:|---|
| `test_priority8_phase4b0_staging.py` | 31 | OK |
| `test_priority8_phase4b1a_authoring_schema.py` | 65 | OK |
| `test_priority8_phase4b1_batch01.py` | 9 | OK |
| `test_priority8_phase4b2_batch02.py` | 11 | OK |
| `test_priority8_phase4b3_batch03.py` | 17 | OK |
| `test_priority8_phase4b4_batch04.py` | 23 | OK |
| `test_priority8_phase4b5_batch05.py` | 29 | OK |
| `test_priority8_phase4b6_batch06.py` | 24 | OK |
| `test_priority8_phase4b_progress.py` | 8 | OK |
| `test_priority8_phase4b_authoring_guards.py` | 26 | OK |
| **All ten together** | **243** | **OK** |

`git diff --check` clean; `git diff --name-status` shows exactly the six
expected paths (see completion report).

## 20. Overall verdict

No deviation from the frozen matrix was required or made. All 37 rows, all
21 guards, and all structural invariants were implemented and independently
re-verified by direct mutation testing rather than assumed from the report
text. The one non-enforceable semantic limitation (`polecać` A4/B1) is
exactly the one already disclosed and adjudicated in the frozen matrix, and
is compensated through the required non-structural editorial controls. Batch
6 authoring is complete and internally consistent; recommend proceeding to
independent review before Batch 7.
