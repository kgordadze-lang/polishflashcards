# Priority 8 Phase 4B2 — Batch 02 risk review

## Status

This audit reviews only the private Batch 2 staging draft produced by the
same authoring pass. Every staging record remains `draft`. This is **not**
an independent review, human staging approval, canonical governance event,
or product approval — that independent review is expected separately before
Batch 3, as it was for Batch 1.

## Boundary audit

| Risk | Audit result | Control retained |
|---|---|---|
| `przyjechać` do/na non-exclusivity | Clear | Both destination patterns' learner explanations use "one common way" / "another common way" wording; internalScope states neither is exhaustive government. No source, vehicle, route, or time pattern exists. |
| `wyjść` source/destination realization discipline | Clear | `z`, `do`, and `na` are each labelled non-exclusive realizations of `SKĄD`/`DOKĄD` in both internalScope and learner wording. |
| `wyjść` literal vs result/event sense boundary | Clear | Only `literal-exit-from-place` is authored. The separately evidenced ranking/result sense (`na CO`, "wyjść na prowadzenie") is not authored and is not blurred into the literal meaning; its omission and rationale are documented in the authoring report rather than silently absorbed. No event/activity `na` frame was invented from everyday intuition. |
| `wyjechać` source-only narrowing | Clear | Exactly one pattern (`z-genitive-source`) is authored. No destination, vehicle, route, time, or manner pattern exists, matching the exact-lemma constraint. |
| `przynosić` Dative-recipient rejection | Clear | Only `accusative-object` is authored. No Dative pattern exists anywhere in the record, and no concrete source/goal preposition was invented beyond what Phase 3 authorized. |
| `odpowiadać` Dative-person rejection | Clear | No Dative complement exists. internalScope explicitly states the person spoken to is not a schema position. |
| `odpowiadać` clause/direct-speech alternatives | Clear | `na-accusative-question`, `ze-content-clause`, and `direct-speech` are three independent patterns under one meaning, not combined into a single frame; each has its own example. Direct speech uses the established private `clauseKind: direct-speech` shape; no canonical or runtime file was touched. |
| `zamawiać` beneficiary alternatives | Clear | `dative-beneficiary` and `dla-genitive-beneficiary` are separate patterns, each independently exemplified; no example or pattern combines both beneficiary forms into one frame. |
| `zamawiać` u+Genitive realization wording | Clear | `u-genitive-provider`'s learner explanation reads "One common way to name the provider is u + Genitive," and internalScope calls it a documented realization of a selected provider/location role, not exclusive provider government. |
| `zacząć` / metadata-only `zaczynać` independence | Clear | The pre-existing `metadataAspectPartner` object on `zacząć` is byte-for-byte unchanged. `zaczynać` was not added to the 68 `canonicalLemma` names and received no `candidateContent`. internalScope states no syntax is inherited from `zaczynać`. |
| `kończyć` / `skończyć` independence | Clear | `skończyć` is not referenced anywhere in `kończyć`'s record. internalScope explicitly states this record does not pre-decide the later pair policy. |
| `pamiętać` recall vs reminder split | Clear | `recall-retain` and `obligation-reminder` are separate meanings with disjoint pattern sets; `żeby` appears only under the obligation meaning, `o + Locative`/Accusative only under recall. |
| `zapominać` recall vs failure-to-act split | Clear | `recall-failure` and `failure-to-act` are separate meanings with disjoint pattern sets; the infinitive under `failure-to-act` does not reuse any recall-sense construction. |
| `zapominać` rejected żeby absence | Clear | No `zeby` clauseKind appears anywhere in the `zapominać` record. internalScope on both meanings explicitly states the żeby schema was rejected by Phase 3 and must not be authored. |
| Generalized-role discipline | Clear | No pattern uses `DOKĄD`, `SKĄD`, `GDZIE`, or `KTÓRĘDY` as a complement type; only concrete `case`/`preposition-case`/`infinitive`/`clause` complements were authored, each labelled a realization where the underlying sense is a generalized role. |
| Maximal-frame avoidance | Clear | Every pattern has exactly one complement. No pattern in the batch combines two or more of destination/source/beneficiary/provider/clause participants into a single frame. |
| Direct-speech private/canonical boundary | Clear | `priority7_tooling.py`, canonical enum tables, runtime schema, `formatVersion`, and `patternDataRevision` are untouched (confirmed by `git diff --name-status`, which shows only the five authorized paths). |
| Candidate provenance | Clear | All 28 examples are `editorial-generated`; none is falsely marked `repository-reuse`. A repository search was performed and its near-misses rejected for documented reasons (see the authoring report's provenance section) rather than silently ignored. |
| CEFR/status decisions | Clear | 27 of 28 patterns are active-production with an independent justification; the one recognition-only pattern (`zapominać` / `czy-dependent-clause`) has a documented concrete rationale and omits the `production` CEFR field per the validator's `recognition-only` rule. |
| No production IDs | Clear | `tests/test_priority8_phase4b2_batch02.py::test_no_production_ids_or_id_fields_exist` passes; no `vp-*` string or production-ID field name appears anywhere in the batch. |
| No Batch 3 leakage | Clear | `test_exact_current_authored_and_future_empty_boundaries` in the progress test confirms all 48 remaining future lemmas (verification orders 22–70, excluding metadata-only 17/37) still have empty `candidateContent`. |

## Corpus checks

- The 12 Batch 2 meanings are non-duplicative within their lemmas.
  `wyjść`, `odpowiadać`, and `zamawiać` remain single-meaning records with
  multiple alternative patterns, matching their single-sense Phase 3
  evidence; `pamiętać` and `zapominać` are deliberately split exactly where
  Phase 3 established a learner-relevant recall/obligation or
  recall/failure-to-act boundary.
- The 28 patterns keep alternative schemas separate: no destination,
  source, beneficiary, provider, or clause material was reassembled into a
  maximal frame.
- Every pattern has one, and only one, resolving example
  (`tests/test_priority8_phase4b2_batch02.py::test_ownership_scopes_and_one_example_per_pattern`).
  All 28 Polish examples are unique, as are all 28 English translations.
- The only candidate pattern keys reused across lemmas are parent-scoped
  structural keys (`z-genitive-source`, `do-genitive-destination`,
  `infinitive`, `accusative-object`, `o-locative-topic`); none relies on
  global uniqueness, matching the Batch 1 precedent.
- All 68 statuses remain `draft`; 68 full-pattern records remain present;
  the two metadata-only partners and both `udział` guards are unchanged
  (verified by the unmodified `tests/test_priority8_phase4b_progress.py`
  assertions covering the whole corpus).
- No production `vp-*` string, production ID field, canonical record,
  runtime record, audio artefact, activity field, or governance event was
  created.

## Residual reviewer questions

1. Confirm the intentional omission of `wyjść`'s separately evidenced
   ranking/result `na CO` sense is the correct product decision for this
   stage, rather than authoring it now as a clearly separated third
   meaning.
2. Confirm the intentional omission of the recall-sense `że`-clause and
   interrogative-dependent clause for `pamiętać` (deferred to avoid
   `że`/`żeby` sibling-meaning confusion in the same authoring pass) against
   the general completeness rule.
3. Confirm the recognition-only classification and B1 CEFR placement of
   `zapominać`'s `czy-dependent-clause` matches the project's intended
   curriculum pacing for embedded yes/no questions.
4. Confirm the `zamawiać` beneficiary/provider pattern count (four patterns
   under one meaning) remains pedagogically manageable rather than
   overloaded, given three of the four are alternative realizations of two
   underlying participants (beneficiary, provider).
5. As with Batch 1's `wracać`/`wrócić`, review the independently retained
   `zacząć`/`zaczynać` (metadata-only) and `kończyć` (pending `skończyć`)
   opportunity-cost questions only after all relevant future candidates are
   independently verified; this batch neither collapses nor pre-judges
   either pair.

## Inherited-test compatibility note

`tests/test_priority8_phase4b0_staging.py` and
`tests/test_priority8_phase4b1a_authoring_schema.py` were not modified, per
the allowed-paths restriction, and both continue to pass unchanged because
they already read from the frozen B0 baseline fixture
(`tests/fixtures/priority8_phase4b0_staging_baseline.json`) rather than the
live staging file, per the fixture-coupling fix landed before this batch.
`tests/test_priority8_phase4b1_batch01.py` was not modified and continues to
pass unchanged because its approved-content digest test is independent of
`phaseStep`/`stagingRevision`, per
`reports/priority-8-phase-4b-test-lifecycle.md`. Only
`tests/test_priority8_phase4b_progress.py` (the intentionally moving gate)
and the new `tests/test_priority8_phase4b2_batch02.py` were changed, exactly
as the test lifecycle architecture anticipates for a Batch 2 authoring
commit.

## Final reconciliation correction note (2026-08-25)

The residual question recorded above for `zapominać` is resolved by human
decision HD-1. The row is now
`interrogative-forgotten-content`, uses `clauseKind: interrogative`, and is
A2/A2 active-production. Its historical `czy-dependent-clause` key and B1
recognition-only rationale are superseded. The exact-shape rule
`p8-4b-zapominac-exact-pattern-shapes` now rejects the obsolete `czy` shape
and unauthorized clause-family alternatives. The current Batch 2 digest is
`87c07469634cc039e68e2f52a5f306a05ca7753e1e4d328d58542c4b549e2f82`;
the immediately pre-reconciliation value
`dd55047bbd7db3d28224d6366015c7353479206e4ffba64cf8b6397efb8d8db8`
is retained only as superseded historical evidence.
