# Priority 8 Phase 4B1 — Batch 01 risk review

## Status

This audit reviews only the private Batch 1 staging draft. Every staging record remains `draft`; this is not an independent review, human staging approval, canonical governance event, or product approval.

## Boundary audit

| Risk | Audit result | Control retained |
|---|---|---|
| `pracować` workplace / `jako` leakage | Clear | Only the production/creation meaning and `nad + Instrumental` are authored. The scope excludes workplace, occupation, beneficiary, collaboration, and work-with-person readings. |
| `iść` `do` / `na` exclusivity | Clear | Both are individual patterns whose learner explanations say they are non-exclusive destination forms; the infinitive remains separate. |
| `chodzić` attendance `na` vs spatial `na` | Clear | `regular-attendance` owns activity `na + Accusative`; its scope and explanation expressly distinguish it from a merely spatial destination. |
| `jechać` selected vehicle vs manner | Flag retained | Instrumental and `na + Locative` are separate selected vehicle/equipment patterns. The record does not create a general manner frame; independent review must reconsider the source-only vehicle analysis. |
| `jeździć` selected vehicle vs frequency / manner | Flag retained | Habituality is semantic scope, not a frequency complement. Vehicle/equipment patterns are distinct and the reviewer-risk from unavailable Walenty corroboration remains. |
| `dojść` abstract vs literal contamination | Clear | One meaning and one pattern are limited to reaching a conclusion, truth, thought, or conviction. Literal movement is explicitly excluded. |
| `dojechać` vehicle and endpoint realization | Flag retained | `do` and `na` endpoints are separate non-exclusive realizations. Instrumental and `na + Locative` vehicle/equipment patterns are separate; no route or time pattern is present. The vehicle finding remains for independent review. |
| `wracać` / `wrócić` aspect inheritance | Clear | Each record preserves its own aspectual scope and frozen evidence pointer. Shared surface patterns do not claim transferred syntax. |
| `wracać` / `wrócić` exclusive `do` / `z` wording | Clear | All four explanations call the forms one realization of a return-goal or return-source position, not exclusive government. |
| `przyjść` place vs event/activity | Clear | `literal-place-arrival` and `one-off-activity-arrival` are separate meanings. The event `na` and infinitive occur only in the latter. |
| Prohibited person-target `przyjść` frame | Clear | The literal-place scope specifically excludes person-specific targets; no such pattern or example appears. |
| Example provenance | Clear | One candidate is truthful repository reuse (`card:a1-first-verbs-006.ex`) and resolves byte-identically. The other 24 are explicitly editorial-generated. |
| Accidental copying from reference examples | Clear | Examples were newly authored after local source search; no editorial-generated example exactly matches an eligible local card/drill sentence. No WSJP example sentence was copied. |
| Durable candidate keys | Clear | Meaning keys describe stable senses, pattern keys describe constructions, and every example key is the durable slot-style `primary`. No key records Batch number, verification order, or transient sentence words. |
| Future-batch contamination | Clear | Only orders 1–10 have content. Orders in Batches 2–7 have empty meanings, patterns, and examples. |

## Corpus checks

- The 12 meanings are non-duplicative within their lemmas. `chodzić` and `przyjść` are deliberately split only where the frozen evidence establishes a learner-relevant boundary.
- The 25 patterns keep alternative schemas separate: no destination, vehicle, source, or infinitive material was reassembled into a maximal frame.
- Every pattern has one, and only one, resolving example. All 25 Polish examples are unique, as are all 25 English translations.
- The only candidate pattern keys reused across lemmas are parent-scoped structural keys such as `do-genitive-destination`; none relies on global uniqueness.
- All 68 statuses remain `draft`; 68 full-pattern records remain present; the two metadata-only partners and both `udział` guards are unchanged.
- No production `vp-*` string, production ID field, canonical record, runtime record, audio artefact, activity field, or governance event was created.

## Residual reviewer questions

1. Confirm that the project’s pedagogical complement threshold accepts the source-supported selected vehicle/equipment participants for `jechać`, `jeździć`, and `dojechać`.
2. Confirm the learner wording for concrete motion realizations remains sufficiently clear that it cannot be read as exclusive `do`, `na`, or `z` government.
3. Review the independently retained `wracać` / `wrócić` pair with the already frozen, moderate separate-slot signal in view; this draft neither removes the pair nor invents a unique frame for `wrócić`.

## Regression-test fixture status

The initial Batch 1 authoring run exposed coupling in the historical B0 and B1A tests: both treated the evolving live staging JSON as their B0 fixture. That infrastructure issue was corrected before Batch 1 acceptance in predecessor commit `902a9454c0220109dc3b4203ff9c2db9ba8ec6ce` (`Fix Phase 4B regression test fixture coupling`). The B0 suite now reads a frozen B0 baseline fixture and the B1A suite builds its schema fixtures from that baseline; no validator rule or test assertion was weakened. With the current live 4B1 staging document, B0 passes 31 tests, B1A passes 65 tests, Batch 1 passes 9 tests, and the combined suite passes 105 tests.

## Locked-role representation note

The frozen linguistic evidence distinguishes the `z + Genitive` patterns of `wracać` and `wrócić` as return-source realizations. The inherited locked role enum available to Phase 4B has no `source` member, so these two complements retain the legal compatibility value `role: "target"`. Their source semantics remain explicit in the candidate pattern keys, internal scopes, and learner explanations. This is closed-model representation debt, not a reinterpretation of the Phase 3 evidence and not authorization to add a new role during Batch 1.
