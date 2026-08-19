# Priority 7 — Phase 4F-C1B Blind Independent Example Review

## Verdict

**CHANGES REQUIRED before editorial acceptance.** Seven current example slots are release-blocking: six are empty and one can teach the explicitly excluded sense of *widzieć*. Four further current examples are acceptable but have useful improvements. Two should remain unchanged.

This is an independent editorial review artifact only. It does not modify canonical examples, create review events or actors, approve content, or begin Phase C2.

## Blindness record

- Reviewed input: `reports/priority-7-phase-4fc1-blind-example-review-input.csv`
- SHA-256: `0af6c076be5c569074ed861e2c8e65fdd0bd048c3fa538f01ebbec60fac45771`
- Primary C1 matrix unavailable: confirmed absent before substantive review.
- Primary C1 summary unavailable: confirmed absent before substantive review.
- Primary C1 test unavailable: confirmed absent before substantive review.
- Only the blind example input supplied substantive Phase 4F-C1 proposal material.
- The sibling Claude C1 workspace was not inspected, searched, requested, or opened.
- No attempt was made to infer primary C1 counts or finding IDs.

## Exact queue and counts

The blind file maps exactly once to each of the 13 requested review IDs and to 13 unique canonical pattern IDs. There are no omissions or duplicates.

### Current classification

| Classification | Count |
| --- | ---: |
| MUST CHANGE | 7 |
| USEFUL IMPROVEMENT | 4 |
| NO CHANGE | 2 |
| **Total** | **13** |

### Severity

| Severity | Count |
| --- | ---: |
| NONE | 2 |
| LOW | 4 |
| MEDIUM | 6 |
| HIGH | 1 |
| **Total** | **13** |

### Proposal decisions

| Decision | Count |
| --- | ---: |
| ACCEPT PROPOSAL | 8 |
| ACCEPT AS ADDITION | 0 |
| REVISE PROPOSAL | 3 |
| REJECT PROPOSAL | 1 |
| NEW DRAFT NEEDED | 0 |
| NOT APPLICABLE | 1 |
| **Total** | **13** |

## MUST CHANGE rows

- **P7-NR-031 / P7-C1B-004 — pytać, o + Accusative:** current example missing. Accept `Zawsze pytam o cenę.`
- **P7-NR-032 / P7-C1B-005 — pytać, person + topic:** current example missing. Accept `Pytam koleżankę o nową restaurację.`
- **P7-NR-033 / P7-C1B-006 — widzieć, visual perception:** current `Widziałam wczoraj twoją siostrę.` is compatible with the separately excluded encounter/meet reading. This is the sole HIGH finding. Replace it with the revised, A1-controlled `Czy widzisz tę górę?`
- **P7-NR-035 / P7-C1B-007 — myśleć o:** current example missing. Accept `Ciągle myślę o egzaminie.`
- **P7-NR-042 / P7-C1B-009 — zajmować się, person-care:** current example missing. Accept `Kiedy siostra jest w pracy, zajmuję się jej córką.` The context distinguishes care from occupation/activity.
- **P7-NR-043 / P7-C1B-010 — opiekować się:** current example missing. Accept `Opiekuję się chorą babcią.`
- **P7-NR-044 / P7-C1B-011 — zależeć od:** current example missing. Accept the exact repository reuse `Czy pójdziemy na spacer? To zależy od pogody.` The two-sentence string is supported and pedagogically coherent.

## Rejected and revised proposals

- **P7-NR-007 — REJECT PROPOSAL:** `Czy potrzebuję antybiotyku?` is exact, natural, case-transparent, and byte-exact repository reuse, but it does not materially improve the current `Potrzebuję zaświadczenia z pracy.` Multiple examples are technically supported; another near-duplicate is pedagogically unnecessary.
- **P7-NR-011 — REVISE PROPOSAL:** Polish `Dziękuję siostrze za kolację.` is an everyday, transparent improvement. English `Thanks to my sister for dinner.` changes the participant relationship into a causal “thanks to” reading. Use `I'm thanking my sister for dinner.`
- **P7-NR-018 — REVISE PROPOSAL:** Polish `Codziennie dbam o kondycję.` is natural and clearer than reflexive `siebie`, but `I take care of my fitness every day.` is not fully idiomatic English. Use `I make an effort to stay fit every day.`
- **P7-NR-033 — REVISE PROPOSAL:** `Czy widzisz tę górę na horyzoncie?` fixes the exact-sense problem, but *horyzoncie* is avoidable load for an A1 pattern. Use `Czy widzisz tę górę?` / `Do you see that mountain?`

## Independently proposed alternatives

All three alternatives are `editorial-generated`; none is claimed as original or human-authored.

| Review ID | Polish | English | Origin |
| --- | --- | --- | --- |
| P7-NR-011 | `Dziękuję siostrze za kolację.` | `I'm thanking my sister for dinner.` | `editorial-generated` |
| P7-NR-018 | `Codziennie dbam o kondycję.` | `I make an effort to stay fit every day.` | `editorial-generated` |
| P7-NR-033 | `Czy widzisz tę górę?` | `Do you see that mountain?` | `editorial-generated` |

## Current examples retained with useful improvements

- **P7-NR-011:** current is correct and transparent but formal; revised proposal is more everyday.
- **P7-NR-012:** current is grammatical but `wszystko` is Accusative=Nominative and the till question is slightly artificial. Accept `Płacę za kawę i gazetę.`
- **P7-NR-018:** current is natural, but reflexive `siebie` obscures the noun-case lesson. Use the revised proposal above.
- **P7-NR-036:** current is exact and natural, but `znaleźć` is buried under `udało mi się` and `mieszkanie` is Accusative=Nominative. Accept `W końcu znalazłam nową pracę.`

## Provenance and repository verification

No proposed origin is false:

- `Czy potrzebuję antybiotyku?` resolves byte-exact to `card:a2-pharmacy-020.ex`.
- `Czy pójdziemy na spacer? To zależy od pogody.` resolves byte-exact to `card:b1-expressing-opinions-013.ex`.
- Every `editorial-generated` proposal has an empty repository source and makes no `original`, human-author, or repository-reuse claim.
- No proposal appears copied or lightly paraphrased from the cited grammar references. References were used only to confirm the authored meaning and construction.

The current authoring context has no actor with the `example-generation` role. This is not a false claim in the review matrix, which records proposed provenance categories rather than canonical origin objects, but later canonical adoption of generated material must first supply a registered nonhuman generator plus `generatorRef` and `adoptedAt`. It must never be converted to `original` provenance.

Repository search also found several related sentences, but none displaced the decisions above. In particular, `Chciałam cię o coś zapytać.` hides both noun cases; `Czym się zajmujesz?` is the wrong activity sense for P7-NR-042; and the existing *myśleć* drills are valid but not substantially stronger than the blind proposal.

## Example format

The canonical schema stores `examples` as an array, so multiple examples per pattern are supported. Each example's Polish and English are strings; no one-sentence restriction exists. The two related sentences in P7-NR-044 form one short contextual example and are not pedagogically clumsy. P7-NR-007 shows the opposite case: an additional example is technically valid but unnecessary.

## Provenance problems and unresolved questions

- Provenance problems in the proposals: **none**.
- Unresolved linguistic or editorial questions: **none**.
- Governance prerequisite for later adoption: register a truthful nonhuman example-generation actor and add complete origin metadata for any accepted generated example.

## Canonical boundary

The canonical corpus, canonical examples, authoring context, review history, actor registries, shipping files, and runtime files remain unchanged from immutable baseline `080d92ad49a514332f21ecd90b4a11de070a243f`. The corpus remains at 45 `reference-verified` patterns, 47 reference-verification acceptances, zero editorial-review events, and zero product-approval events.
