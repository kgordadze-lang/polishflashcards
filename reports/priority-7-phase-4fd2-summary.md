# Priority 7 Phase 4F-D2 — blind independent final editorial verification

## Final verdict

**GO WITH FINDINGS**

The review covers all 45 final patterns independently. Forty-one patterns are
ready for editorial-review acceptance exactly as authored. Four patterns have
learner-facing canonical wording blockers that require adjudication and
correction before acceptance. No canonical content, governance event, actor,
ID, example entity, release state, or runtime surface was changed by D2.

## Baseline and boundary proof

| Item | Verified value |
|---|---|
| baseline commit | `3d613def18e9edf8bcabd331d40b5b90df30a9da` |
| baseline tree | `3d1a9600041f83a9a2374b0fef5a069bc77a4d63` |
| canonical corpus SHA-256 | `6a174face8dffdcf26f0c2e073bf183287f9d67c09ac28d661ce61c3b257c257` |
| authoring-context SHA-256 | `bee8eb95ed78775e50a7fc57da2381d67c43087b00c836e6e6cb0c81925df718` |
| `priority7_tooling.py` SHA-256 | `bbb8b31d9bd25ed601fec8c97e2313d2d808bfd68c55b48eb4b5de970fdfb7c2` |
| blind-input SHA-256 | `069ceee9e55bc3f1fffa152014dec024de826b8001caa0beabcffbdff114c916` |
| remotes | zero |
| `push.default` | `nothing` |

The D2 output footprint is limited to this summary, the D2 matrix, and the D2
test suite. The supplied D1 blind input remains an input dependency rather than
a D2 verdict artifact.

## Blindness proof

Before canonical review, the repository was searched for Phase 4F-D1 material.
Exactly one matching file existed:

- `reports/priority-7-phase-4fd1-blind-final-review-input.csv`

It contained one header plus 45 verdict-free rows. No D1 final editorial
matrix, summary, test, verdict count, finding register, or other verdict-bearing
D1 artifact was present. No sibling workspace or out-of-repository D1 material
was inspected, searched, requested, reconstructed, or accessed. The SHA-256
above is the digest of the blind input actually reviewed.

## Exact coverage

- matrix rows: **45**
- unique `reviewId` values: **45**
- unique `patternId` values: **45**
- canonical patterns: **45**
- blind-input pattern-ID set equals canonical pattern-ID set: **yes**
- D2-matrix pattern-ID set equals canonical pattern-ID set: **yes**
- duplicates: **0**
- omissions: **0**

Every row was assessed as an integrated lemma → meaning → pattern →
complements record, including aspect, lexical `się`, learner wording, error
notes, CEFR/status, activity eligibility, examples, evidence/provenance, and
sibling coherence.

## Counts

### D2 verdicts

| Verdict | Count |
|---|---:|
| ACCEPT | 41 |
| ACCEPT WITH NOTE | 0 |
| CHANGES NEEDED | 4 |
| DEFER | 0 |

### Severity

| Severity | Count |
|---|---:|
| NONE | 41 |
| LOW | 0 |
| MEDIUM | 4 |
| HIGH | 0 |

### Editorial acceptance recommendation

| Recommendation | Count |
|---|---:|
| YES | 41 |
| NO | 4 |

## Blockers

### P7-D2-001 — P7-NR-011 (`dziękować`)

- verdict / severity: **CHANGES NEEDED / MEDIUM**
- exact field: pattern
  `vp-p-dziekowac-thank-dative-recipient-za-accusative-057197dd300f`,
  `examples[0].en`
- current value: `I thank my sister for dinner.`
- why it blocks: with a third-person recipient and no habitual or narrative
  context, this is stilted standalone English. It functions as a literal
  case-teaching gloss, while the locked authoring rule requires the example
  translation itself to be natural English.
- exact correction: set `examples[0].en` to
  `I say thank you to my sister for dinner.`
- tier-1/reference scope affected: **no**
- fresh reference verification required: **no**

### P7-D2-002 — P7-NR-018 (`dbać`)

- verdict / severity: **CHANGES NEEDED / MEDIUM**
- exact field: pattern
  `vp-p-dbac-take-care-of-o-accusative-target-d3e3eb63129c`,
  `examples[0].en`
- current value: `I look after my fitness every day.`
- why it blocks: `look after my fitness` is not an idiomatic neutral-English
  collocation for maintaining one's physical condition. The Polish is natural
  and sense-correct; the English translation is not.
- exact correction: set `examples[0].en` to
  `I work on my fitness every day.`
- tier-1/reference scope affected: **no**
- fresh reference verification required: **no**

### P7-D2-003 — P7-NR-028 (`lubić`)

- verdict / severity: **CHANGES NEEDED / MEDIUM**
- exact field: pattern
  `vp-p-lubic-enjoy-thing-or-activity-infinitive-activity-be3742b7ce45`,
  `examples[0].en`, coupled to repository source `card:a1-free-time-003.ex`
- current value: `I like reading before sleep.`
- why it blocks: `before sleep` is not idiomatic everyday neutral English;
  `before bed` or `before going to sleep` is natural. Because this example is
  declared as repository reuse, changing only the editorial copy would make
  the provenance resolver false.
- exact correction: change both `card:a1-free-time-003.ex` and the canonical
  example English to `I like reading before bed.`, preserving exact reuse.
  Alternatively, a different correction must truthfully reclassify provenance.
- tier-1/reference scope affected: **no**
- fresh reference verification required: **no**

### P7-D2-004 — P7-NR-037 (`podobać się`)

- verdict / severity: **CHANGES NEEDED / MEDIUM**
- exact fields: pattern
  `vp-p-podobac-sie-appeal-to-nominative-stimulus-dative-experiencer-ef199e675ee9`,
  `learnerExplanationEn` and `errorNotes[0].guidanceEn`
- current positive model in both fields: `ten film podoba mi się`
- why it blocks: that order is possible under contextual focus, but it is a
  marked standalone model. Neutral order is `ten film mi się podoba`. This is
  an A2 active-production pattern with no canonical example, so the two marked
  strings are its only positive Polish production model.
- exact correction: in both fields replace `ten film podoba mi się` with
  `ten film mi się podoba`; change no meaning, role, complement, relation type,
  CEFR, teaching status, ID, or provenance.
- tier-1/reference scope affected: **no**
- fresh reference verification required: **no**

## Nonblocking notes

None. D2 did not use `ACCEPT WITH NOTE`; low-priority preferences were not
promoted into findings, and no blocker was hidden as optional polish.

## Audit results

### Linguistic and semantic audit

All 45 lemma identities, aspect values, lexical-`się` decisions, meaning
boundaries, relation categories, complement roles, governed cases/prepositions,
and required/optional choices are sound under the locked selective-pattern
architecture. Aspect partners remain separate, and no row was penalized merely
because another valid Polish construction exists. The only Polish-language
blocker is the neutral word-order model on P7-NR-037; its underlying syntax and
participant mapping are correct.

The historically sensitive final states P7-NR-005, 013, 029, 030, 031, 037,
039, 040, 042, and 043 were reviewed against canonical history without relying
on any D1 verdict. Their prior structural/status issues are resolved in the
final corpus. P7-NR-037 nevertheless retains the independent learner-word-order
blocker described above.

### Learner-explanation audit

Forty-four explanations accurately name their construction, state participants
truthfully, match the intended meaning, and avoid exhaustive-valency claims.
P7-NR-037's role statement is correct but its positive Polish illustration uses
marked clitic order and must be normalized before editorial acceptance.

### Error-note audit

All present error notes are grammatically relevant to their final patterns and
none is stale merely because its noun differs from an example. P7-NR-037's
distractor is useful, but its correction repeats the same marked positive word
order and is included in P7-D2-004. Empty error-note arrays are legitimate and
do not create hidden teaching gaps.

### Example audit

All 29 Polish examples are natural, sense-correct, standalone, and suitable for
their curricular use. Twenty-six English examples are natural and semantically
equivalent. P7-NR-011, P7-NR-018, and P7-NR-028 fail the locked natural-English
translation requirement and are blockers. No example was rejected merely
because an alternative sentence could also work.

### CEFR, teaching-status, and activity audit

All 45 recognition levels, production levels/omissions, teaching statuses, and
default-false activity allowlists are internally consistent with the locked
curriculum. The intentional recognition/production asymmetries on secondary
polysemous patterns remain defensible; D2 does not invent a new curriculum
philosophy.

### Sibling-pattern audit

Multi-pattern lemmas were reviewed together. The final distinctions for
`pomagać`, `słuchać`, `uczyć się`, `dziękować`, `płacić`, `prosić`,
`rozmawiać`, `bać się`, `lubić`, `mówić`, `pytać`, `wierzyć`, `zajmować się`,
and `zależeć` remain coherent. The broader `lubić`/`podobać się` contrast also
preserves the intended subject/experiencer reversal once P7-D2-004's neutral
word order is supplied.

### Provenance audit

All repository-reuse examples currently resolve exactly to repository content.
All editorial-generated examples truthfully describe process and claim neither
human authorship nor intentional repository reuse. No internet-wide uniqueness
test was performed. P7-D2-003 requires a synchronized source/editorial wording
change (or truthful origin reclassification) so provenance remains valid after
the correction.

## Governance and unresolved questions

The canonical governance state remains:

- 45 `reference-verified` patterns
- 47 accepted `reference-verification` events
- 29 canonical examples
- 0 `editorial-review` events
- 0 `editorial-reviewed` patterns
- 0 `product-approval` events
- 0 approved patterns

There is no unresolved reference, meaning, case, aspect, lexical-`się`, CEFR,
status, sibling, or provenance question. Cross-review adjudication must decide
and apply the four exact learner-facing corrections before those rows receive
editorial acceptance. D2 creates no governance event and makes no product
decision.
