# Priority 7 Phase 4F-C2C — Provenance Collision Repair

**Verdict: GO**

Phase 4F-C2B returned NO-GO for one contained reason: two editorial-generated
example sentences were found to collide exactly with pre-existing
language-learning material.  This phase replaces those two sentences, locks
the project's provenance interpretation so that `editorial-generated` is read
as a claim about process rather than an impossible claim about global
uniqueness, and changes nothing else.  Canonical grammar, architecture, IDs,
governance currency, the C2B technical hardening and the other nine generated
examples are untouched.

Nothing here integrates the candidate, creates a review event, approves,
freezes or projects runtime.

---

## 1. Scope of the change

Exactly four canonical string values moved, on two example objects:

| JSON path | Field |
|---|---|
| `vp-p-widziec-perceive-visually-accusative-object-80b697e51432` → `examples[0]` | `.pl`, `.en` |
| `vp-p-opiekowac-sie-care-for-instrumental-object-8aa6f0a91e5b` → `examples[0]` | `.pl`, `.en` |

A structural diff of the corpus against the arriving C2 candidate returns those
four paths and no others.  The check is mechanical: re-applying the two prior
sentence pairs to the delivered corpus reproduces the arriving C2 file at
SHA-256 `cec93c71f772bef7a6f458400e70e225ba873238e9f313ffce7eb35c3e606701`
byte for byte.

`editorial/priority-7-authoring-context.json` is unchanged from the C2
candidate: no actor was added, altered or removed, and `$.contextNotice` still
states exactly what C2B reviewed and accepted.

---

## 2. The locked provenance interpretation

For this project `editorial-generated` describes **process and provenance**.

It means the example was created through this editorial workflow rather than
sourced from, or reused from, an external work.  It does **not** assert that
the same short sentence has never appeared anywhere else in the world.  Global
uniqueness cannot reasonably be proved for elementary learner sentences, and a
provenance model that implied it would be making a claim no reviewer could
confirm.

Collision screening is therefore **best-effort**, over:

- repository content;
- the known research and reference material available to the project;
- targeted exact-phrase checks where those are available.

A later-discovered external coincidence does not by itself prove copying.
Nothing in this section weakens the standing rule: actually copying, or lightly
paraphrasing, a research or source example remains prohibited, and
`origin.kind = repository-reuse` with a resolving `repositorySource` remains the
only way a reused sentence may enter the corpus.

The operative release rule is narrower than the provenance claim.  If, before
release, an exact collision with pedagogical material is discovered —
especially material teaching the same construction — the sentence is replaced
when a clean alternative is readily available.  That is what this phase did,
twice.

This is an assurance decision taken after discovery.  It is not a finding that
any previous model or reviewer copied anything, and no such finding is made or
implied.

---

## 3. The two collisions and the two replacements

The full adjudication is
[`reports/priority-7-phase-4fc2c-provenance-adjudication.csv`](priority-7-phase-4fc2c-provenance-adjudication.csv),
which carries exactly two rows.

### P7-NR-033 — widzieć, Accusative object

| | |
|---|---|
| Prior (C1C/C2) | `Czy widzisz tę górę?` — Do you see that mountain? |
| Collision class | Exact sentence collision with language-teaching material |
| Source | Pre-existing published A1/A2 course material using the identical Polish sentence as a `widzieć` example, identified by C2B section 6 |
| Final | `Czy widzisz tę czerwoną torbę?` — Do you see that red bag? |
| Origin | `editorial-generated`, unchanged |

The replacement changes the lexical object and nothing that the row teaches.
`widzieć` still governs a plain Accusative; `tę` is the standard written
feminine Accusative demonstrative, itself a teaching point; and `czerwoną
torbę` carries the overt Accusative on both adjective and noun, so case
transparency is at least as good as `tę górę`.  The object is still inanimate,
so the separately numbered encounter sense the meaning scope excludes stays
structurally unavailable and the figurative understand sense is not in play.
`czerwony` and `torba` are A1 lexis, matching the pattern's A1/A1 bands, and
the sentence is still one clause with one terminator.

### P7-NR-043 — opiekować się, Instrumental object

| | |
|---|---|
| Prior (C1C/C2) | `Opiekuję się chorą babcią.` — I look after my sick grandmother. |
| Collision class | Exact sentence collision with **same-construction** teaching material |
| Source | *Gramatyka dla praktyka — składnia*, where the identical Polish sentence is a worked A2 example for the same `opiekować się` + Instrumental construction, identified by C2B section 6 |
| Final | `Dziś opiekuję się młodszą siostrą.` — Today I'm looking after my younger sister. |
| Origin | `editorial-generated`, unchanged |

This was the more serious of the two, because the external source teaches the
very construction this row teaches.  The replacement keeps the exact sense the
meaning scope leads with — attentive care for a person, with the lexical `się`
present — and keeps the bare Instrumental with no preposition, which is the
pattern's teaching point and the correct half of the `errorNote` minimal pair.
`młodszą siostrą` shows the Instrumental `-ą` on adjective and noun and
contrasts with the Accusative `-ę` the note corrects, exactly as `chorą babcią`
did.  The fronted adverb `Dziś` is natural contemporary Polish, keeps the
sentence to one clause, and moves it further from the textbook wording than a
bare complement swap would.

Two consequences are recorded rather than hidden:

- the example no longer shares its noun with `learnerExplanationEn` and the
  `errorNote`, which C1C valued as reinforcement.  That is a deliberate trade
  of reinforcement for source distance; the learner still meets *babcia* in
  both of those fields, which C2C did not touch;
- the complement stays distinct from P7-NR-042 (`zajmować się … jej córką`), so
  the closed `zajmować się` / `opiekować się` teaching-status question is not
  reopened.

---

## 4. Identity

Both rows keep the C2 example identity.

| Row | Durable key | ID | Recomputes from `(patternId, key)` |
|---|---|---|---|
| P7-NR-033 | `saw-your-sister` | `vp-e-widziec-perceive-visually-accusative-object-saw-your-sister-ec51af47f224` | yes |
| P7-NR-043 | `caring-for-a-sick-grandmother` | `vp-e-opiekowac-sie-care-for-instrumental-object-caring-for-a-sick-grandmother-5d1ea100cdfa` | yes |

P7-NR-033 is still the same durable replacement-example entity, with wording
changed before integration.  P7-NR-043's C2-created durable entity is likewise
the same entity: C2 has never been integrated, and under the Phase 1 stable-ID
specification wording is not the durable identity key — re-minting the key
would re-mint the deterministic ID for a change that specification calls
identity-preserving.

Both keys are now opaque identifiers that no longer describe their sentences.
That is not new: C1C already replaced the sentence `saw-your-sister` was minted
from, and C2B reviewed and accepted exactly that condition.

Deterministic ID/allocation validation re-run over the delivered corpus:

- 29 examples;
- every ID recomputes from its owning pattern and durable key;
- no duplicate ID, no duplicate sibling key;
- no new key created merely because wording changed;
- no tombstone and no tombstone reuse.

Origin split is unchanged at 18 `repository-reuse` and 11
`editorial-generated`, with 0 `original`.  The example-generation actor is
still `priority7-example-generation`; no actor was added and no actor gained a
role.

---

## 5. Best-effort collision screen on the two new strings

What was checked, and what it can and cannot support:

| Screen | `Czy widzisz tę czerwoną torbę?` | `Dziś opiekuję się młodszą siostrą.` |
|---|---|---|
| Exact string across the whole Po polsku repository (`*.js`, `*.json`, `*.html`, `*.py`, `*.md`, `*.csv`) | no hit | no hit |
| Repository entity index used by the tooling (1,665 indexed entities, all string fields) | no hit | no hit |
| Pinned-baseline canonical corpus | no hit | no hit |
| Priority 7 research/reference material carried in `reports/` and `editorial/` | no hit | no hit |
| Targeted exact-phrase web checks, including construction-specific queries | no verbatim hit | no verbatim hit for the sentence |

Two observations are recorded honestly:

1. The component lexemes exist in the repository — `torba`, `siostra`,
   `młodszy` all appear in shipped cards and drills — which is what makes the
   sentences level-appropriate.  No shipped sentence matches either new string.
2. The four-word span `opiekuję się młodszą siostrą` occurs inside a
   *different* sentence on a Polish punctuation page, where it illustrates the
   comma before `a także`.  That is a different sentence teaching a different
   point, not the Instrumental construction, and the span is close to the
   minimal realisation of this verb with this complement.  It is recorded as
   **non-blocking** under section 2, not concealed.

**Limitation.**  This screen is best-effort and cannot establish global
uniqueness.  It establishes that the two sentences were written through this
editorial workflow, that they do not reuse repository content, and that no
verbatim pedagogical collision was found by the checks named above.  A later
coincidence would not, by itself, be evidence of copying.

---

## 6. What C2C did not reopen

- The other nine editorial-generated examples are byte-identical to the C2
  candidate, including their IDs, keys, audio flags and origin objects.  No
  new editorial rewrite was launched.
- The two `repository-reuse` KEEP rows are byte-identical to the pinned
  baseline and their sources still resolve exactly.
- No meaning, complement, relation type, CEFR, teaching status, eligibility,
  evidence, review event, release mode, shipping field or runtime field moved.
- No second example exists on any pattern; every one of the 45 patterns still
  carries at most one, and the runtime still renders `examples[0]`.

---

## 7. Historical artifacts preserved

Not edited, and pinned by digest in `tests/test_priority7_phase4fc2c.py`:

| Path | SHA-256 |
|---|---|
| `reports/phase-4fc1c/adjudication-matrix.csv` | `0c5c7f83b240b2d02ed1dc3a04a5522ca9e8227a74e175cb0fc17404aab69044` |
| `reports/phase-4fc1c/summary.md` | `21fe7541a784768dbeaf45f226af27835778a6830120b36f27e3b9b097405d64` |
| `reports/phase-4fc1/summary.md` | `45ad110a3e2bcbd9c4c8f8881824b219ccbe0e0c293bcd364ee1877021599d7f` |
| `reports/phase-4fc1/example-matrix.csv` | `2422eed842c558f8cd6671123563b88b02e5464c0d06f63ed57fce817a410f4f` |
| `reports/phase-4fc1/blind-review-input.csv` | `0af6c076be5c569074ed861e2c8e65fdd0bd048c3fa538f01ebbec60fac45771` |
| `reports/phase-4fc1b/summary.md` | `645a4252eb911f802ead3f8ce3d3afe265970d7c49befbc83da6c83e659cdb9f` |
| `reports/phase-4fc1b/example-review-matrix.csv` | `0f43a13f300e94d5edb50018bcdab5de7c145a75040c8ba70b1a4064bc1ad50e` |
| `reports/priority-7-phase-4fc2-summary.md` | `e12768828935c67d138ae77717bef0e68de10fe2c02047e8bbc2e5e332ed38d9` |
| `reports/priority-7-phase-4fc2b-summary.md` | `09995264798fe6402355ee16390ace9e7e6f3808b0a980489bfd1e7b3f778329` |

C2B reviewed the pre-C2C candidate and correctly returned NO-GO.  Its report
stands as delivered, as the historical evidence that the collision was found
before release; it is not rewritten as though it had approved C2.

The C2 report likewise stands as delivered.  It records what C2 implemented and
still carries the two superseded sentences, exactly as the C1 and C1B reports
still carry proposals C1C did not adopt.  This report is the supersession
record.

### What C2C supersedes

C2C supersedes **only the wording fields** — `finalPolish` and `finalEnglish` —
of exactly two C1C adjudication rows, P7-NR-033 and P7-NR-043.

Everything else in those two C1C rows stands: disposition, pattern, meaning,
final origin, empty final repository source, and the case/sense/naturalness/
CEFR analysis, which the replacements were chosen to satisfy.  The C1C
provenance verdict on those two rows is superseded only in the narrow sense
that its repository-local screen could not see external teaching material; its
finding that neither sentence reuses repository content still holds.

The effective implementation specification is therefore:

> **C1C adjudication + the C2C two-row provenance override.**

That override is declared as a closed two-row literal in
`tests/test_priority7_phase4fc2.py`, mirrored in the six historical
normalizers, and refuses to fire unless the C1C matrix still carries the exact
prior wording it supersedes — so an edit to the historical artifact cannot be
absorbed silently.  It is deliberately *not* a generic normalization: no third
review ID can be overridden through it, and a wording mutation on any other row
must still be rejected.

---

## 8. C2B technical hardening preserved

All six historical normalizer repairs C2B made are preserved.  None was
reverted to the weaker C2 version, and the only C2C-specific adjustment is the
two-row wording override described above, applied identically in all six.

Each normalizer still recognises the complete approved example object — locked
text, locked key, recomputed ID, `audioEligible = false` and the exact
provenance object — and still removes the generation actor only when every
field and the note digest match the approved C2 record.

Representative committed mutation controls were re-run against the C2C
candidate.  Exact C2C passes; every unauthorized mutation still fails:

| Control | Result |
|---|---|
| Unauthorized example wording outside 033/043 (repository-reuse row) | survives normalization; validator returns `REPOSITORY_SOURCE_MISMATCH` |
| Unauthorized wording on a *third* generated C1C row (P7-NR-031) | survives normalization in all six modules |
| Example ID / durable key mutation | survives in all six |
| Provenance mutation (generator, adoption date, extra origin field) | survives in all six |
| Actor-role escalation to `editorial-review` | survives in all six; C2 minimal-role guard fails |
| Meaning / complement mutation | survives; validator returns `REVIEW_STATE_MISMATCH` |
| Evidence / review-event mutation | survives; validator returns `REVIEW_STATE_MISMATCH` and `REVIEW_SCOPE_FORBIDDEN` |
| Second or out-of-queue example | survives in all six |
| Extra actor | survives in all six |

---

## 9. Governance

Derived by the tooling, not asserted:

| Quantity | Value |
|---|---|
| Patterns | 45 |
| `reference-verified` | 45 |
| `research` | 0 |
| reference-verification acceptances | 47 |
| editorial-review events | 0 |
| product-approval events | 0 |
| editorial-reviewed patterns | 0 |
| approved patterns | 0 |

No review event of any kind was created, altered or invalidated.  Every
pattern still declares `solo-maintainer-reference-backed`.

Scope digests, measured against the arriving C2 candidate:

- all 45 tier-1 `reference-verification` digests **unchanged**;
- all 45 `external-verification` digests **unchanged**;
- higher-scope (`editorial-review`, `native-linguistic`, `product-approval`)
  digests changed on exactly the two C2C rows.

Measured against the pinned baseline commit
`080d92ad49a514332f21ecd90b4a11de070a243f`, the **set** of higher-scope changed
rows is still exactly the same 11 C2 implementation rows.  Only the digest
**values** for the two C2C rows differ from C2.  No editorial history exists to
be made stale, which is why moving those digests is permitted.

---

## 10. Validation

Real uncommitted C2C workspace:

| Gate | Result |
|---|---|
| C2C | 80 tests, 0 failures/errors |
| Required targeted Python (C2C, C2B, C2, C1C, B3B, 4F-A, 4E.1, 4E, 5-A, 4C, 3D-1, 3F-A, 2A) | 992 tests, 0 failures/errors |
| Full Python discovery | 1,208 tests, 0 failures/errors |
| Full JXA | 36 suites, 10,544 assertions, 0 failed |
| `validate_content.py` | pass: 10 levels, 97 topics, 1,215 cards, 353 drills, 1,675 unique IDs |
| `verify_audio.py` | pass: 3,377 required phrases, manifest entries and MP3 files; 0 missing/orphaned |
| `build_pages.py --check` | current: 23 grammar, 6 vocabulary and guide hub; 32 sitemap URLs; 380 audio-bearing strings |
| `priority7_tooling.py validate-editorial` | valid |
| `git diff --check` | pass |

The Python runs emit the pre-existing `ResourceWarning` diagnostics for
unclosed read handles that C2B also recorded.  They fail no gate and are
outside this phase's scope.

## 11. Fresh committed scratch

A fresh isolated scratch clone was created, its remote removed, and the
complete final C2C candidate — exactly 25 files — committed there only, on top
of the pinned baseline.

| Gate | Result |
|---|---|
| Clean working tree | pass |
| Zero remotes | pass |
| `HEAD^` is `080d92ad49a514332f21ecd90b4a11de070a243f` | pass |
| Committed files | 25 (C2's 20, C2B's 2, C2C's 3) |
| C2C + C2B + C2 + C1C + B3B | 404 tests, 0 failures/errors |
| Full Python discovery | 1,208 tests, 0 failures/errors |
| Full JXA | 36 suites, 10,544 assertions, 0 failed |
| content / audio / pages / editorial | all pass, same totals as the real workspace |
| `git diff --check HEAD^ HEAD` | pass |

Committed mutation controls, applied and restored in the scratch only:

| Control | Failures raised |
|---|---|
| Unauthorized wording on a third generated row (P7-NR-031) | 17 |
| Durable-key mutation on P7-NR-043 | 24 |
| Provenance mutation (`generatorRef`) on P7-NR-033 | 22 |
| Generation-actor role escalation to `editorial-review` | 17 |
| Complement mutation (widzieć Accusative → Dative) | 29 |
| Reference acceptance flipped to `reject` | 27 |
| Reverting P7-NR-043 to the collided textbook sentence | 20 |
| Second example added to P7-NR-033 | 39 |
| Shipping mutation in `priority7_tooling.py` | 5, against the 4F-A and 4F-B3B pinned guards |

After each control the scratch was restored and verified clean; the final
committed battery was re-run green.  The real C2C workspace remains
uncommitted, with zero remotes.

---

## Final verdict

**GO**

Both discovered source collisions were replaced; the provenance model is now
explicitly process-based rather than an impossible global-uniqueness claim; all
C2B hardening survives; canonical and governance boundaries remain intact; the
candidate is ready for one final independent closure review.

Do not integrate, create editorial-review events, approve, freeze or project
runtime on the strength of this report.
