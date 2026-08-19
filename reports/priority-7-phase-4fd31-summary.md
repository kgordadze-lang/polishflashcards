# Priority 7 Phase 4F-D3.1 — Targeted Final Editorial Repair

Baseline `3d613def18e9edf8bcabd331d40b5b90df30a9da`
(tree `3d1a9600041f83a9a2374b0fef5a069bc77a4d63`).

D1 and blind D2 were adjudicated externally; the D3 decisions arrived locked.
This phase implemented them and nothing else. No new 45-pattern editorial
review was performed, no editorial-review event was created, nothing was
product-approved, and no runtime or project state was frozen.

## The locked D3 decision, as implemented

| Review | D1 | D2 | D3 | Canonical change |
|---|---|---|---|---|
| `P7-NR-011` | ACCEPT WITH NOTE | CHANGES NEEDED | blocker **OVERTURNED** | none — row is byte-identical |
| `P7-NR-018` | ACCEPT WITH NOTE | CHANGES NEEDED | blocker **UPHELD** | one English example string |
| `P7-NR-028` | ACCEPT WITH NOTE | CHANGES NEEDED | blocker **UPHELD**, shipping-card edit **rejected** | one English example string |
| `P7-NR-037` | ACCEPT WITH NOTE | CHANGES NEEDED | blocker **UPHELD** | one Polish model, in two learner-facing fields |

The complete canonical delta is four lines in one file:

| Row | Field | From | To |
|---|---|---|---|
| `P7-NR-018` | `examples[0].en` | `I look after my fitness every day.` | `I work on my fitness every day.` |
| `P7-NR-028` | `examples[0].en` | `I like reading before sleep.` | `I like reading before bed.` |
| `P7-NR-037` | `learnerExplanationEn` | `… ten film podoba mi się.` | `… ten film mi się podoba.` |
| `P7-NR-037` | `errorNotes[0].guidanceEn` | `… ten film podoba mi się.` | `… ten film mi się podoba.` |

`P7-NR-018` keeps its Polish `Codziennie dbam o kondycję.`, its
`editorial-generated` origin, its `care-every-day` key and its ID.
`P7-NR-028` keeps its Polish `Lubię czytać przed snem.`, its
`repository-reuse` origin and `repositorySource`, its key and its ID.
`P7-NR-037` changes only the positive-model substring: substituting the old
model back into either field reproduces the baseline string byte-for-byte, and
`meaning`, `complements`, `relationType`, CEFR, `teachingStatus`, IDs,
`activityEligibility`, reference evidence and review events are untouched.

### P7-NR-028 was verified independently

The example declares its source as card `a1-free-time-003`, field `ex`. That
card, at [data-a1.js:403](../data-a1.js), already carries:

```
ex:"Lubię czytać przed snem."   exEn:"I like reading before bed."
```

So the canonical English had drifted from the source it claims to reuse. D1's
record was confirmed directly against the repository rather than taken on
trust. The correction moves the canonical copy back onto its source; the card
itself is **not** modified, and is byte-identical to the baseline. D2's
proposal to edit the card instead was rejected by D3 and was not implemented.

## Scope-tier impact

Editorial-tier corrections do not touch anything a reference verification
covers, so the tier-1 projection is unchanged everywhere.

| Scope tier | Rows whose digest changed |
|---|---|
| tier-1 — `external-verification` / `reference-verification` | **0 of 45** |
| tier-2 — `native-linguistic` / `editorial-review` | **exactly 3** |
| tier-3 — `product-approval` | exactly the same 3 |

Stated unambiguously: **tier-1 changed on 0 of 45; tier-1 is unchanged on all
45 patterns.**

Changed tier-2 row set — exactly as expected:

| Row | Pattern | tier-2 digest before → after |
|---|---|---|
| `P7-NR-018` | `vp-p-dbac-take-care-of-o-accusative-target-d3e3eb63129c` | `sha256:e262cbc8…03ffb76` → `sha256:0a73a863…f65038` |
| `P7-NR-028` | `vp-p-lubic-enjoy-thing-or-activity-infinitive-activity-be3742b7ce45` | `sha256:801e79f0…dc04ea10` → `sha256:c3048bd0…348e72ca` |
| `P7-NR-037` | `vp-p-podobac-sie-appeal-to-nominative-stimulus-dative-experiencer-ef199e675ee9` | `sha256:71c7cdd4…2b8f9b84` → `sha256:1e9bc973…64e9e06e` |

Full values:

```
P7-NR-018  from sha256:e262cbc8dba8d9741ffe772a400633cf1272a27a10684005be6f875ae03ffb76
             to sha256:0a73a863157cefe410c707afa55c9249224eff5a19217788e1b4363a50f65038
P7-NR-028  from sha256:801e79f0be7c57baf8b2a5fda4256751c29692a9e8b2c57b66210b82dc04ea10
             to sha256:c3048bd0a53d6c9d079b224769f48d153b90d2f2321ddaf52cf2c4fa348e72ca
P7-NR-037  from sha256:71c7cdd4e4a31b54a822f4fe10c2d4e3948b0c86533abde3b6cbbc8f2b8f9b84
             to sha256:1e9bc9735bade2c87d6594a2f96de2d982b69dcfd6c2238697d2a18564e9e06e
```

`P7-NR-011` (`vp-p-dziekowac-thank-dative-recipient-za-accusative-057197dd300f`)
is byte-identical to the baseline at every tier.

### Pre-existing stale historical scope digests

Two `mówić` patterns —
`vp-p-mowic-tell-content-dative-recipient-accusative-content-2f2b1add1960` and
`vp-p-mowic-tell-content-dative-recipient-ze-clause-a01ddc4a4736` — carry
recorded event `scopeDigest` values that no longer recompute against their own
pattern. These predate this phase: they were left behind by Phase 4F-B3B's
tier-1 complement corrections and were deliberately not re-stamped then.

For the record:

- **D3.1 introduced no new stale historical scope digest.** The set of rows
  whose recorded digest no longer recomputes is **identical before and after
  D3.1** — the same two `mówić` rows, and only those two.
- **None of the three corrected rows is in that set.** `P7-NR-018`,
  `P7-NR-028` and `P7-NR-037` recompute exactly against their own recorded
  reference-verification digests, because tier-1 did not move on them.
- **The current qualifying reference-verification state remains valid.** All
  45 patterns are `reference-verified` on 47 acceptances, and the tooling
  derives that state from the corpus as delivered.
- **D3.1 does not repair or rewrite historical review events.** The complete
  review-event list is byte-identical to the baseline. The inherited stale
  pair is disclosed here, not normalized away, not re-stamped, and not
  otherwise touched.

This is a disclosure of inherited state, not a D3.1 finding, and it is not
repaired here — repairing it would mean rewriting historical review events,
which is out of scope for a targeted editorial repair.

## Governance

| Property | Result |
|---|---|
| Patterns | 45 |
| Examples | 29 |
| `reference-verified` | 45 |
| Reference-verification acceptances | 47 |
| Fresh reference-verification events | 0 — event list byte-identical to baseline |
| `editorial-review` events | 0 |
| Product approvals | 0 |
| `priority7_tooling.py validate-editorial` | valid |

## Artifacts

- `reports/priority-7-phase-4fd3-adjudication.csv` — four rows (011, 018, 028,
  037) with D1/D2/D3 verdicts, the canonical change, prior/final values,
  tier-1 impact and fresh-verification requirement.
- `reports/priority-7-phase-4fd31-summary.md` — this file.
- `tests/test_priority7_phase4fd31.py` — the closure suite.

D1 and D2 left no artifact inside this workspace; both reviews were produced
independently and adjudicated externally. Their verdicts are supplied from
that external record and are now carried in full on all four rows:

| Row | D1 | D2 | D3 |
|---|---|---|---|
| `P7-NR-011` | ACCEPT WITH NOTE | CHANGES NEEDED | D2 blocker **overturned** — no canonical change |
| `P7-NR-018` | ACCEPT WITH NOTE | CHANGES NEEDED | D2 blocker **upheld** |
| `P7-NR-028` | ACCEPT WITH NOTE | CHANGES NEEDED | D2 blocker **upheld**; D2's proposed shipping-card edit **rejected** |
| `P7-NR-037` | ACCEPT WITH NOTE | CHANGES NEEDED | D2 blocker **upheld** |

An earlier draft of the CSV carried a `not-recorded-in-this-workspace`
placeholder in the D1 column for the three rows whose D1 verdict the locked D3
brief did not restate. The historical verdicts have replaced it; no
placeholder remains. D1's note on `P7-NR-028` — that card `a1-free-time-003`
already carried the corrected English — is preserved in that row's rationale
and was independently re-verified here rather than taken on trust.

The CSV schema does not carry finding-ID columns, so no D1 or D2 finding ID
was added or altered. No D1 or D2 history was rewritten.

## Historical test repair

Three later-phase canonical corrections necessarily falsified historical
guards that compare live content against their own phase baselines. They were
repaired with the future-safe semantics the project already uses for Phase
4F-B3B's corrections and Phase 4F-C2/C2C's examples: a closed literal naming
exactly the approved change, and a normalizer that reverts it only when the
exact approved final string is present.

`PHASE_4FD31_EDITORIAL_CORRECTION` and `without_phase_4fd31_corrections()`
were added to the six historical suites (4C, 4E, 4E.1, 4F-A, 4F-B3B, 5-A) and
to 4F-C2, and folded into the front of `without_phase_4fc2_examples()` so the
existing six-normalizer contract keeps holding. 4F-C2C reconstructs its
candidate by text, so it received the text-level equivalent
`without_phase_4fd31_text()`, which declares its required match count and
raises on any other. 4F-C2D normalizes at its JSON loader.

No historical assertion was weakened, no phase's expected values were edited,
and no future filename exclusion was added. The normalization recognizes only
these three corrections: any other wording change — a fourth row, a further
edit to one of these three rows, a reverted correction, a Polish or provenance
mutation — survives normalization and still breaks the historical guard. That
is asserted directly, per module, in the new suite.

### D3.2 closure repair: immutable candidate footprint

Focused D3.2 closure found one technical defect in the first D3.1 test: its
footprint assertion compared the pinned baseline with the entire live working
tree/current `HEAD`. That made an unrelated later-phase file look like part of
D3.1. The defect was repaired before integration without touching canonical
content, provenance, governance, tooling or shipping data.

The D3.1 suite now encodes the exact 13-path phase manifest and uses two modes:
while `HEAD` is the pinned baseline it inspects the complete uncommitted
candidate; after integration it resolves the first descendant of that baseline
and inspects only the baseline-to-first-descendant transition. Equality is
exact, not a subset check. Later report and test commits therefore leave the
historical D3.1 result green, while a missing path, an extra path inside the
D3.1 commit, or replacing one expected repair path still fails. No future
filename, directory prefix or glob exception was introduced.

## Validation

### Real uncommitted D3.1 workspace

| Gate | Result |
|---|---|
| D3.1 | 49 tests, 0 failures/errors |
| Named phase battery (D3.1, C2D, C2C, C2B, C2, C1C, B3B, 4F-A, 4E.1, 4E, 5-A, 4C, 3D-1, 3F-A, 2A) | 1,067 tests, 0 failures/errors |
| Full Python discovery | 1,283 tests, 0 failures/errors |
| Full JXA | 36 suites, 10,544 assertions, 0 failed |
| `validate_content.py` | 10 levels, 97 topics, 1,215 cards, 353 drills, 1,675 unique IDs; pass |
| `verify_audio.py` | 3,377 required phrases, 3,377 manifest entries, 3,377 MP3 files, 0 missing/orphaned |
| `build_pages.py --check` | current: 23 grammar, 6 vocabulary, guide hub, 32 sitemap URLs, 380 audio-bearing strings |
| `priority7_tooling.py validate-editorial` | valid |
| `git diff --check` | pass |

Python emits the same pre-existing unclosed-read-handle `ResourceWarning`
diagnostics recorded by prior phases. They fail no gate and were not
broadened into this closure.

### Fresh committed scratch

A fresh isolated scratch repository received the complete candidate and was
committed only there. The commit spans exactly 13 paths; `HEAD^` is the
baseline `3d613def18e9edf8bcabd331d40b5b90df30a9da`; the working tree is
clean; and the scratch has zero remotes.

| Gate | Result |
|---|---|
| Named phase battery | 1,067 tests, 0 failures/errors |
| Full Python discovery | 1,283 tests, 0 failures/errors |
| Full JXA | 36 suites, 10,544 assertions, 0 failed |
| Content / audio / pages / editorial | all pass with the same totals as the real workspace |
| `git diff --check HEAD^ HEAD` | pass |

Four negative controls were applied one at a time in the committed scratch and
restored. Every one made the D3.1 suite exit nonzero, and the exact candidate
passed again after restoration with the scratch clean:

| Control | D3.1 result |
|---|---|
| A fourth canonical wording change, on the overturned `P7-NR-011` | rejected — 7 tests failed |
| A further edit to a corrected row (018's Polish) | rejected — 5 tests failed |
| Reverting an approved correction (028) | rejected — 9 tests failed |
| Tampering with an approved correction (018's new English) | rejected — 11 tests failed |

The fourth-row control was additionally run against the whole battery to prove
the normalization is narrow rather than permissive: it produced 54 failures,
and 4C, 4F-B3B, 4F-C2, 4F-C2C and 4F-C2D each rejected it individually. The
normalizers absorb the three approved corrections and nothing else.

The real D3.1 workspace remains uncommitted and has zero remotes.

## Verdict

**GO**

The three D3-approved corrections were implemented exactly, reference
verification remains intact, no unauthorized canonical change occurred, and
the candidate is ready for focused independent closure.
