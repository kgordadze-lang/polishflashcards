# Priority 8 Phase 4B authoring-guard hardening

## Outcome and scope

Phase 4B now has a reusable live semantic-structure guard alongside, but
separate from, its historical batch digests and moving progress test. The
implementation consists of a human-readable JSON registry and a generic test
interpreter. It changes no staging content, schema, production data, runtime
data, or historical test.

The registry is
`tests/fixtures/priority8_phase4b_authoring_rules.json`; the interpreter and
its mutation proofs are
`tests/test_priority8_phase4b_authoring_guards.py`.

## Three independent test layers

1. **Historical content locks** answer “Did approved Batch N content change?”
   The Batch 1-3 tests project their approved records and compare historical
   digests. They intentionally do not move with the live authoring boundary.
2. **The moving progress gate** answers “Is the live file at the authorized
   phase/revision/boundary, with the expected cumulative totals, future-empty
   records, and draft state?” Only
   `tests/test_priority8_phase4b_progress.py` owns those changing assertions.
3. **Live semantic authoring guards** answer “Does current staging violate a
   known structural semantic invariant?” The registry is evaluated against the
   current file in every future batch. It contains no phase step, staging
   revision, count, authored-boundary, future-empty-boundary, or digest value.

A digest can faithfully preserve a mistaken original interpretation. A live
guard can prevent a known class of structural mistake from recurring. Neither
control determines whether the source evidence was interpreted correctly in
the first place; that remains the job of independent linguistic review.

## Rule-engine behavior

The engine supports these declarative rule kinds:

- `forbid-complement-cooccurrence`: rejects any single pattern in the target
  lemma that matches every listed complement signature. Signatures are partial
  structural matches, so unrelated fields and arbitrary pattern keys cannot
  provide a bypass.
- `forbid-complement-match`: rejects any complement anywhere in the target
  lemma that matches a prohibited structural signature.
- `require-exact-pattern-shapes`: compares unordered multisets of exact
  complement objects per declared meaning. It can also require the exact
  meaning-key set. Pattern keys do not participate; complement type, case,
  preposition/clause kind, role, and requiredness do.
- `require-lexical-identity`: locates a frozen record by verification order,
  requires its exact canonical lemma identity, and verifies its declared
  lexical tokens. Verification order is only a stable locator; it does not
  replace the canonical-identity assertion.
- `require-empty-candidate-content`: targets a named metadata aspect partner
  under its full-record owner and rejects any `candidateContent` field.
- `allow-only-preposition-case-signatures`: checks every preposition-case
  complement in a lemma against an exact declarative allowlist. This is the
  safe mechanism for generalized roles when staging cannot itself represent
  “authorized realization” versus “arbitrary concretization.”
- `require-lexical-material-in-pattern`: selects patterns by meaning and a
  complement signature, then requires a whole lexical token in the configured
  pattern field. In the locked staging architecture that field is
  `learnerExplanationEn`, the first-class pattern-level prose available for a
  fixed lexical item. A synthetic test proves both pass and failure behavior;
  no unauthored Batch 4 rule is active yet.

Complement signatures contain data only. The registry permits no executable
Python expressions. Registry version, top-level shape, rule IDs, duplicate
IDs, known kinds, exact per-kind fields, nested signature shapes, scalar types,
and live targets are validated explicitly. Unknown or malformed rules fail
closed. Violations name the stable rule ID and lemma, plus meaning and pattern
when a concrete pattern is involved; a pattern key is diagnostic context, not
the basis of a structural decision.

## Current active rules

| Rule ID | Target | Invariant |
|---|---|---|
| `p8-4b-pozwalac-no-dative-infinitive` | `pozwalać` | No pattern may combine a direct Dative complement with an infinitive complement. |
| `p8-4b-unikac-no-infinitive` | `unikać` | No infinitive complement may occur anywhere in the lemma. |
| `p8-4b-wymagac-exact-alternative-shapes` | `wymagać` | The exact two meaning identities each have exactly two structural alternatives: required Genitive object + optional `od` + Genitive target, and required `żeby` content clause + optional `od` + Genitive target. No standalone `od` pattern or required `od` is possible. Pattern keys are ignored. The existing person-only versus person-or-thing semantic scope remains in `internalScope`; the current schema has no noun-class field with which to encode that distinction structurally. |
| `p8-4b-klocic-sie-lexical-identity` | `kłócić się` | The canonical identity and lexical `się` remain intact. |
| `p8-4b-pokazywac-authorized-preposition-cases` | `pokazywać` | The only authorized preposition-case signature is required `na` + Accusative with target role. This preserves exact pointing while rejecting arbitrary `w`/`na`/`do` location concretizations, including non-Locative ones. |
| `p8-4b-radzic-sobie-lexical-identity` | `radzić sobie` | The canonical identity and lexical `sobie` remain intact. The guard does not impose a new corpus-wide rule that every example repeat a canonical lexical token. |
| `p8-4b-zaczynac-metadata-only` | `zaczynać` | The private aspect-partner object under `zacząć` cannot acquire `candidateContent`. |
| `p8-4b-przeczytac-metadata-only` | `przeczytać` | The private aspect-partner object under `czytać` cannot acquire `candidateContent`. |

## Mutation proof

The guard suite deep-copies live data and mutates only memory. It proves:

| Mutation | Expected control | Result |
|---|---|---|
| Add Dative + infinitive to `pozwalać` under an arbitrary key | complement co-occurrence | caught |
| Add an infinitive to `unikać` under an arbitrary key | forbidden complement match | caught |
| Add a standalone `od` + Genitive pattern to `wymagać` | exact pattern shapes | caught |
| Change a legitimate optional `wymagać` `od` complement to required | exact pattern shapes/requiredness | caught |
| Strip `się` from the `kłócić się` canonical identity | lexical identity | caught |
| Strip `sobie` from the `radzić sobie` canonical identity | lexical identity | caught |
| Add candidate content to metadata-only `zaczynać` | metadata-only content boundary | caught |
| Add candidate content to metadata-only `przeczytać` | metadata-only content boundary | caught |
| Add unauthorized `w` + Accusative to `pokazywać` | preposition-case allowlist | caught |
| Retain the live exact `na` + Accusative pointing pattern | preposition-case allowlist | passes |
| Supply an unknown kind, malformed rule, duplicate ID, or nonexistent target | registry validation | rejected clearly |
| Require synthetic pattern-level lexical `udział`, present | lexical material primitive | passes |
| Require synthetic pattern-level lexical `udział`, absent | lexical material primitive | caught |

## Future Batch 4-7 extension

Future batches normally add registry objects, not Python branches:

- `brać udział w + Locative` and `wziąć udział w + Locative` can activate one
  `require-lexical-material-in-pattern` rule per independently authored lemma.
  Each rule should select the participation meaning and structural `w` +
  Locative complement, then require whole-token `udział` in that pattern's
  learner explanation. The existing skeleton-level `requiredLexicalItems`
  remains a separate frozen-input control; the live rule protects the authored
  pattern representation.
- A meaning with evidence-bound alternatives can use
  `require-exact-pattern-shapes` to declare its complement multisets and
  requiredness without relying on candidate pattern names.
- A generalized role with only enumerated concrete realizations can use
  `allow-only-preposition-case-signatures`. This avoids guessing semantic
  “location” from prose and makes authorized preposition/case/role/requiredness
  combinations explicit.
- Simple excluded complements and prohibited combinations use the two
  structural forbid primitives.

If a genuinely new semantic invariant cannot be expressed by these primitives,
the engine and its mutation tests should be extended in the same commit as the
first declarative use. An inactive rule must not target unauthored Batch 4
content merely to advertise future intent.

## Schema-first authoring workflow

Before editing `candidateContent` in Batches 4-7, the author prepares a compact
matrix from the binding Phase 3/3B evidence and checks it before writing keys,
examples, explanations, or staging content:

| lemma | meaning | alternative/schema | required complements | optional complements | clause kind | lexical required material | generalized-role realization status | explicit exclusions |
|---|---|---|---|---|---|---|---|---|
| `wymagać` | person requires behavior | A | Genitive content | `od` + Genitive person | — | — | not applicable | no standalone `od` |
| `wymagać` | person requires behavior | B | clause content | `od` + Genitive person | `żeby` | — | not applicable | no standalone `od` |

Each row represents one source-licensed alternative, not a bag of complements
to merge. The author verifies the matrix against evidence first, maps each row
to staging only afterward, and records the matrix in the batch authoring report
or verifies it explicitly in the authoring prompt. Applicable live rules are
then added or updated declaratively and mutation-tested before the batch is
accepted. This matrix is a control-plane artifact, not a new staging field; the
locked `candidateContent` schema remains unchanged.

## Responsibility boundary with generic validation

`validate_priority8_staging.py` and
`tests/test_priority8_phase4b1a_authoring_schema.py` continue to own ordinary
shape and reference safety: allowed fields and complement enums, candidate-key
format and uniqueness, meaning/pattern/example ownership, example origin,
review/governance boundaries, and production-ID prohibition. The authoring
guard does not reimplement those checks. It assumes a structurally valid
staging object and adds only evidence-driven semantic relationships that the
ordinary validator cannot infer: forbidden co-occurrence, forbidden semantic
signature, exact alternatives and requiredness, fixed identity, metadata-only
non-transfer, and authorized realization sets.
