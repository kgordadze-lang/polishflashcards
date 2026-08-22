# Priority 8 Phase 4B3 — Batch 03 risk review

## Status

This audit reviews only the private Batch 3 staging draft produced by the
same authoring pass. Every staging record remains `draft`. This is **not**
an independent review, human staging approval, canonical governance event,
or product approval — an independent review is expected separately before
Batch 4, as it was for Batches 1 and 2.

**Correction record.** An independent review of this batch found that the
original `wymagać` authoring incorrectly modeled `od + Genitive` as a
standalone, required-sole-complement pattern in each meaning, with no
Phase 3 schema licensing `od` without its required Genitive/`żeby`
co-complement. This document has been updated to reflect the corrected
`wymagać` schema (4 patterns, not 6) described below; the row and questions
below describe the corrected state, not the original faulty one.

## Boundary audit

| Risk | Audit result | Control retained |
|---|---|---|
| `próbować` attempt vs tasting sense split | Clear | `attempt-action-result` and `taste-sample-food-drink` are separate meanings with disjoint pattern sets. The attempt Genitive and tasting Genitive share surface case only. |
| `próbować` Genitive noun vs infinitive distinction | Clear | `genitive-action-noun` is `type: case`, never `type: infinitive`. The infinitive is a separate pattern under the same meaning. |
| `pozwalać` alternative-schema structure | Clear | Six independent patterns across two meanings; none freely combines `na`, `żeby`, and infinitive into one frame. |
| Forbidden Dative + infinitive reconstruction | Clear | No `pozwalać` pattern in either meaning combines a Dative complement with an infinitive complement, verified by a dedicated test (`test_pozwalac_never_combines_dative_with_infinitive`) that scans every pattern's complement list for the forbidden co-occurrence, independent of the pattern's key — strengthened after independent review found the original version inspected only patterns literally keyed `"infinitive"`. |
| `pozwalać` human permission vs inanimate enabling | Clear | Dative exists only inside the permission meaning's `na`/`żeby` patterns; zero Dative complements exist anywhere in `inanimate-enabling`. |
| `unikać` rejected infinitive | Clear | Exactly one pattern (`genitive-object`); a dedicated test (`test_unikac_authors_no_infinitive`) confirms no `infinitive` complement type appears anywhere in the record. |
| `wymagać` two-sense participant restrictions | Clear (corrected) | Each meaning has exactly 2 patterns (`genitive-required-content`, `zeby-clause`), each carrying its required Phase 3 core complement plus an **optional** `od + Genitive` complement — matching the exact source schemas `(od KOGO) + CZEGO`/`(od KOGO) + żeby ZDANIE` (person) and `(od KOGO/CZEGO) + CZEGO`/`(od KOGO/CZEGO) + żeby ZDANIE` (situation). There is no standalone `od`-only pattern in either meaning (verified by `test_wymagac_od_genitive_is_optional_not_standalone`). `person-requires-behavior` restricts the optional `od` to a person; `situation-requires-content` allows person-or-thing; the restriction is recorded in each meaning's `internalScope` since the architecture has no formal noun-class mechanism to encode it structurally. The original authoring pass instead modeled `od + Genitive` as a third, required-sole-complement pattern per meaning with no licensing schema for `od` alone; that defect has been corrected. |
| `należeć` ownership vs organization membership | Clear | `do-genitive-owner` and `do-genitive-organization` are separate patterns under separate meanings despite identical surface form; category/relationship/obligation/`należeć się`/location/time/manner are not imported. |
| `kłócić się` lexical się | Clear | `canonicalLemma` is `kłócić się`; a dedicated test confirms `kłócić` (without się) does not appear among the 68 lemma names. |
| `kłócić się` singular/plural participant behavior | Clear | The plural-subject topic example (`Kłócimy się o drobiazgi.`) omits a separate `z`-interlocutor, matching the evidence's noted asymmetry, without inventing a new complement type to encode number. |
| `kłócić się` nominal vs clause topic alternatives | Clear | `o-accusative-topic`, `ze-content-clause`, and `czy-dependent-clause` are three independent patterns, each an alternative way to express the topic; none combines with `z-instrumental-interlocutor` in a single pattern. |
| `pokazywać` optional GDZIE left unconcretized | Clear | No pattern uses `type: preposition-case` with `case: locative`; a dedicated test (`test_pokazywac_has_no_concretized_gdzie_location_pattern`) enforces this. `internalScope` records `GDZIE` as selected semantic-role evidence only. |
| `pokazywać` exact na + Accusative kept distinct | Clear | `na-accusative-pointing` is its own pattern, structurally and semantically separate from `dative-recipient-accusative-thing`. |
| `radzić sobie` lexical sobie | Clear | `canonicalLemma` is `radzić sobie`; `sobie` also appears explicitly in the authored example text (dedicated test enforces both). |
| `radzić vs radzić sobie` identity separation | Clear | No construction or example references non-reflexive advice-sense `radzić`; both remain separate full lemmas in the frozen 68. |
| `kupować` three alternative purchase schemas | Clear | `seller-price-schema`, `dative-beneficiary-schema`, `dla-beneficiary-schema` are three independent patterns; none requires or freely combines seller, price, Dative, and `dla` together. |
| `kupić` three alternative purchase schemas | Clear | Same three-pattern shape, independently authored from `kupić`'s own Batch 4 evidence. |
| `kupować`/`kupić` independent evidence | Clear | Each record cites its own `phase3Evidence.verificationCsv` (`batch-03` for `kupować`, `batch-04` for `kupić`); example vocabulary differs throughout (bread/coat/daughter vs. vegetables/ticket/children) rather than being mirrored. |
| Human-approved retention of both purchase aspect partners | Clear | Neither lemma was removed, made metadata-only, or given `metadataAspectPartner`; a dedicated test (`test_kupowac_and_kupic_are_independently_authored_full_pattern_records`) confirms both remain independent full-pattern records. |
| No maximal purchase frame | Clear | The largest pattern (`seller-price-schema`) has three complements matching Phase 3's own schema-A grouping (`CO + (od KOGO) + (za CO)`); it never also carries the Dative or `dla` beneficiary. |
| CEFR/status decisions | Clear | 27 of 30 patterns are active-production with an independent justification per pattern-type; the three recognition-only patterns each have a documented, non-mechanical rationale (see the authoring report). |
| Provenance | Clear | 3 of 30 examples are truthfully marked `repository-reuse` and resolve byte-identically (verified independently, not only via the test file); the other 27 are `editorial-generated` and were checked for quiet collision against the repository index. |
| No production IDs | Clear | `tests/test_priority8_phase4b3_batch03.py::test_no_production_ids_or_id_fields_exist` passes; no `vp-*` string or production-ID field name appears anywhere in the batch. |
| No Batch 4 leakage | Clear | `test_exact_current_authored_and_future_empty_boundaries` in the progress test confirms all 38 remaining future lemmas (verification orders 32–70, excluding metadata-only 17/37) still have empty `candidateContent`. |

## Corpus checks

- The 14 Batch 3 meanings are non-duplicative within their lemmas.
  `pozwalać`, `wymagać`, and `należeć` are deliberately split exactly where
  Phase 3 established a learner-relevant boundary (permission/enabling;
  person/situation; ownership/membership).
- The 30 patterns keep alternative schemas separate: no seller/price/
  beneficiary/Dative/interlocutor/topic material was reassembled into a
  maximal frame beyond what Phase 3's own schema grouping already permits.
- Every pattern has one, and only one, resolving example. All 30 Polish
  examples are unique, as are all 30 English translations.
- Pattern-key reuse across meanings of the same lemma (`pozwalać`'s
  `infinitive`; `wymagać`'s two shared keys; `kupować`/`kupić`'s three
  shared keys) is sibling-scoped, matching Batch 1/2 precedent — none
  relies on global uniqueness.
- All 68 statuses remain `draft`; 68 full-pattern records remain present;
  the two metadata-only partners and both `udział` guards are unchanged
  (verified by the unmodified corpus-wide assertions in
  `tests/test_priority8_phase4b_progress.py`).
- No production `vp-*` string, production ID field, canonical record,
  runtime record, audio artefact, activity field, or governance event was
  created.

## Residual reviewer questions

1. Confirm the recognition-only classification of the three
   abstract-subject/embedded-question patterns (`pozwalać`/`zeby-enabling`,
   `wymagać`/`zeby-clause` under situation-requires,
   `kłócić się`/`czy-dependent-clause`) matches the project's intended
   curriculum pacing.
2. Confirm the six-pattern, two-meaning `pozwalać` record and the
   corrected four-pattern, two-meaning `wymagać` record remain
   pedagogically manageable rather than overloaded.
3. Confirm the three-complement `seller-price-schema` pattern (shared by
   `kupować`/`kupić`) is an acceptable modeling choice — it is the only
   pattern in Batches 1–3 with more than two complements, chosen because
   Phase 3's own evidence groups seller and price together as one schema
   (`CO + (od KOGO) + (za CO)`), distinct from the separately-schemaed
   Dative and `dla` beneficiary alternatives.
4. As with Batch 1's `wracać`/`wrócić`, review the independently retained
   `kupować`/`kupić` pair's later opportunity-cost question only once all
   remaining candidates are independently verified; this batch neither
   collapses the pair nor invents a construction difference between them.

## Inherited-test compatibility note

`tests/test_priority8_phase4b0_staging.py`, `tests/test_priority8_phase4b1a_authoring_schema.py`,
`tests/test_priority8_phase4b1_batch01.py`, and
`tests/test_priority8_phase4b2_batch02.py` were not modified, per the
allowed-paths restriction, and all continue to pass unchanged — the first
two because they already read from the frozen B0 baseline fixture rather
than the live staging file, and the latter two because their approved-
content digest tests are independent of `phaseStep`/`stagingRevision`, per
`reports/priority-8-phase-4b-test-lifecycle.md`. Only
`tests/test_priority8_phase4b_progress.py` (the intentionally moving gate)
and the new `tests/test_priority8_phase4b3_batch03.py` were changed, exactly
as the test lifecycle architecture anticipates for a Batch 3 authoring
commit.
