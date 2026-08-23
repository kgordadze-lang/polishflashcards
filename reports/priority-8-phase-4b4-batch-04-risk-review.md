# Priority 8 Phase 4B4 — Batch 04 risk review

This review audits the Batch 4 implementation against the frozen
`reports/priority-8-phase-4b4-schema-matrix.md`. It does not reopen any
linguistic decision the matrix already settled; it checks that authoring
faithfully implements it.

**Correction addendum.** Sections 12, 13, and 14 below are marked
CORRECTED. They record the original authoring-time reasoning as originally
written, followed by the independent review's objection and the correction
actually applied (a following commit, separate from the original authoring
commit `823ee376c258bb8e4d4183c3e577d60291ab14dd`). No other section of this
review changed: the matrix conformance, structural, guard-registry, and
immutability findings below are unaffected and remain accurate.

## 1. `dawać`/`dać` aspect independence

Both lemmas carry the identical schema (`CO` + `KOMU`, both required),
independently sourced from each lemma's own WSJP sense per the matrix. No
syntax was copied between them mechanically — each pattern was authored from
its own matrix row. Risk: none identified; the identical shape is expected
and matches the matrix exactly.

## 2. `brać`/`wziąć` literal alternatives

Two alternatives per lemma, kept separate: an Accusative object with an
*optional* Instrumental means (A1), and an Accusative object with a
*required* `za` + Accusative gripped part (A2). The optional Instrumental
stays inside the A1 pattern's own complement list; it was never authored as
a second, standalone pattern. `p8-4b-brac-exact-pattern-shapes` and
`p8-4b-wziac-exact-pattern-shapes` structurally enforce this (mutation proof
B confirms a standalone-instrumental injection is caught). Risk: none
identified.

## 3. Fixed `udział`

`brać`/`wziąć` participation is authored as a single `w+locative` complement
pattern; `udział` cannot be structurally attached to a pattern in the locked
candidate schema (documented limitation, §9 of the matrix), so it is carried
through four independent, redundant channels instead:

1. lemma-level `requiredLexicalItems: ["udział"]` (already present, unchanged);
2. the meaning's `internalScope` prose;
3. the pattern's `learnerExplanationEn`, which explicitly teaches the fixed
   expression and contains the whole token `udział`;
4. the authored example, which genuinely contains `udział` in context
   (`biorę/wziąłem udział w konferencji`).

`p8-4b-brac-participation-explanation-material` and
`p8-4b-wziac-participation-explanation-material` structurally check channel
3 (mutation proof C confirms explanation-stripping is caught). Channels 1, 2,
and 4 remain guard-unchecked by design — this is the same known limitation
the matrix already flagged, not a new gap introduced here.

## 4. Current Phase 4B structural lexical-material limitation

Confirmed and not silently worked around: no new complement type or pattern
field was invented to attach `udział` structurally. The limitation is
recorded in the matrix (§9.1) and is unchanged by this authoring. A cleaner
structural representation remains an explicitly open later schema question,
as the matrix already states.

## 5. `czytać` GDZIE anti-concretization

All five matrix rows are implemented exactly; the optional generalized
`GDZIE` present in three source rows (alternatives 1, 3, 4) was **not**
authored into any pattern — no `w+Locative`, `na+Locative`, `do+Genitive`, or
other location preposition appears anywhere in `czytać`'s five patterns.
Mutation proof E confirms an injected `w+Locative` "reading location" pattern
is caught by `p8-4b-czytac-authorized-o-locative-topic-signatures`.

## 6. `czytać` required/optional `o+Locative` signatures

Both authorized signatures are genuinely present in the authored content, not
merely asserted in prose:

- `o-locative-topic` (row 2): `preposition-case:o+locative role=topic
  required=true` — the dedicated topic alternative's required core
  complement.
- `ze-content-clause` and `interrogative-content-clause` (rows 3–4):
  `preposition-case:o+locative role=topic required=false` — the optional
  topic participant on the clause alternatives.

The new allowlist guard (`p8-4b-czytac-authorized-o-locative-topic-signatures`)
lists exactly these two signatures. Mutation proofs F and G confirm both
currently pass cleanly; proof E confirms a third, unauthorized signature is
rejected.

## 7. `pisać` 12 correspondence alternatives

All 12 alternatives (6 content families × 2 recipient modes) are authored
with the recipient optional throughout, and Dative/`do`+Genitive never
co-occur in one pattern (verified structurally — every correspondence
pattern has exactly one recipient-typed complement). Mutation proof H
confirms combining both recipient types into one pattern is caught; proof I
confirms changing an optional recipient to required is caught.

## 8. `napisać` required-Dative asymmetry

The critical asymmetry — Dative **required** on exactly A2–A4 (`że`, `żeby`,
interrogative-dependent) and **optional** on A1/A5/A6 (topic, direct speech,
Accusative content), with `do`+Genitive optional throughout — is authored
exactly as adjudicated, and is structurally distinct from `pisać`'s uniformly
optional Dative: a direct comparison of the two lemmas' correspondence
pattern complements shows a difference on exactly the three clause
alternatives, nowhere else. Mutation proofs J and K confirm both directions
of normalization (required→optional and optional→required) are caught by
`p8-4b-napisac-exact-pattern-shapes`.

## 9. Direct-speech representation

`czytać`'s alternative 5 and `pisać`/`napisać`'s A5/B5 all use the existing
private `clauseKind: "direct-speech"` representation already locked for
Phase 4B (and already used by `odpowiadać`'s pattern in Batch 2). No new
direct-speech schema type was invented. Examples follow the existing
typographic convention (`„...”` in Polish, `"..."` in English) already
established in the corpus.

## 10. Lexical `się`

`spotykać się`/`spotkać się` each author a single `z+instrumental` pattern
with no `się` complement — `się` is part of `canonicalLemma` only, per the
matrix and the existing `kłócić się`/`radzić sobie` convention. Mutation
proofs L/L2 confirm stripping `się` from `canonicalLemma` is caught by the
new `require-lexical-identity` rules.

## 11. Reciprocal meeting-participant behavior

The matrix's decision to represent the reciprocal-plural-subject behavior as
a documented `internalScope` restriction rather than a second, complementless
pattern was followed exactly — each meeting lemma has exactly one pattern.
This decision was made in the frozen matrix, not re-litigated here; this
authoring only implements it.

## 12. CEFR / status edge cases — CORRECTED

**Original decision (superseded).** The initial authoring classified all 12
`pisać`/`napisać` `do`+Genitive correspondence patterns as `recognition-only`
as a block, reasoning that `do`+Genitive addressing is uniformly more
formal/literary than the Dative default, and cited `kłócić się`'s `czy`-clause
as corpus precedent for splitting a lemma's alternatives across
`active-production`/`recognition-only`.

**Independent review rejected this**, on two grounds, both confirmed on
direct inspection:

1. **Factually contradicted by existing product content.** `data-verbs.js`
   drill `verbs-future-tense-005` (type `"build"`) requires the learner to
   *actively produce* "Napiszę do ciebie wieczorem." — a `do`+Genitive
   correspondence sentence. A construction the product already drills for
   production cannot simultaneously be `recognition-only` in the verb-pattern
   data.
2. **The cited precedent is not like-for-like.** `kłócić się`'s `czy`-clause
   is one specific, independently marked *clause type* set to
   `recognition-only` (alongside `zapominać`'s parallel `czy`-clause); it is
   not a precedent for demoting an entire *recipient mode* — six otherwise
   ordinary content families — to `recognition-only` wholesale, irrespective
   of each family's own complexity.

**Corrected rule, now applied:** `teachingStatus` and `cefr` follow
**content-family complexity**, not recipient mode. Each `do`+Genitive
pattern's `cefr` and `teachingStatus` were mirrored, mechanically, from its
exact Dative-mode sibling in the same content family (`topic` mirrors
`topic`, `że`-clause mirrors `że`-clause, and so on), independently for
`pisać` and `napisać`. Since all 12 Dative-mode siblings are
`active-production`, this yields **41 active-production / 0
recognition-only** for the whole of Batch 4 — a result derived from
inspecting the sibling records, not asserted in advance. `usage` values were
left unchanged: `priority: common`/`core` contained no textual claim of
peripherality and is fully consistent with `active-production`.

## 13. Example naturalness — CORRECTED

**Original decision (superseded).** The initial authoring deliberately
diverged the English translation of every Dative-mode pattern from its
`do`+Genitive sibling (dropping "to" in the Dative English gloss: "writing
my friend..." vs "writing to my friend...") specifically to keep all 41
English strings pairwise unique.

**Independent review rejected this** for 8 of the resulting examples plus 2
unrelated ones, on naturalness grounds: "write my friend that…" and "write
my friend: …" are marked/awkward English that this product's own corpus
never uses (`data-grammar.js`/`data-verbs.js` consistently say "write **to**
me"/"write **to** you"/"an email **to** the boss", never a bare double
object with a `że`-clause or quoted speech); four interrogative-clause
examples used "when I'm coming back", which reads as a temporal adjunct
rather than the intended embedded question; and the `brać`/`wziąć`
optional-Instrumental examples were contrived ("soup with a spoon") or
carried a slash-alternative translation ("took/grabbed"), a form with zero
precedent across the 83 Batch 1–3 examples.

**Corrected rule, now applied:** naturalness and semantic clarity outrank
English-string uniqueness. The 10 affected examples (§ authoring report
addendum) were rewritten; duplicate English between recipient-mode siblings
is now accepted where the Polish constructions genuinely share one natural
translation. All 41 Polish sentences remain pairwise unique and
pedagogically distinct. Four distinct English translations are each shared
by a sibling pair (the interrogative-clause and direct-speech alternatives,
for both `pisać` and `napisać`), so 8 of the 41 example records participate
in English duplication; this is intentional, not an oversight. `napisać`'s
A2–A4 examples still visibly realize the required Dative; every required
complement is still realized in its example.

## 14. Provenance / quiet reuse — WORDING CORRECTED

Zero repository-reuse examples; all 41 are `editorial-generated` (unchanged
by the correction). A targeted search of `editorial/verb-pattern-
candidates.json` and the `data-*.js` product corpora found no exact
schema-faithful match to reuse, so none was forced.

**Original wording (superseded):** described the quiet-reuse scan as
checking "the complete repository entity index" — this overstated coverage.

**Corrected description.** Two distinct scans were run, and neither alone is
"complete":

1. **Historical-lock / index scan** (the one `tests/test_priority8_phase4b4_
   batch04.py` actually runs on every test invocation): every generated
   Polish sentence is checked via `priority7_tooling.
   repository_index_from_root` against exactly the fields it indexes —
   `card.pl`, `card.ex`, `drill.prompt`, `drill.answer` — across 1665
   entities (1215 `card`, 353 `drill`, 89 `topic`, 8 `scenario`). This scan
   does **not** reach nested grammar-deck `examples[].pl` text (e.g. in
   `data-verbs.js`), which is outside the `card`/`drill` record shape.
2. **Supplemental raw-text scan** (broader, run once at authoring time for
   the 10 corrected sentences, not enforced by any test): a verbatim grep of
   every `.js`, `editorial/*.json`, and `reports/*` file (187 files, ~8.2 MB),
   excluding the staging file and Batch 4's own reports — this does reach the
   grammar-deck text.

Both scans found **zero verbatim collisions** for all 41 Batch 4 Polish
sentences (including the 10 corrected). All 41 Polish strings are pairwise
unique within Batch 4; English strings are not required to be, and 8 of the
41 records now participate in one of four legitimate duplicate pairs (§13).

## 15. Future-safe historical lock

`tests/test_priority8_phase4b4_batch04.py` follows the Batch 1/2/3
architecture exactly: it does not assert `phaseStep`, `stagingRevision`, or
corpus-wide draft/future-empty boundaries (those live only in
`test_priority8_phase4b_progress.py`), so Batch 5–7 authoring cannot
invalidate it. It pins the Batch 4 content digest, the frozen-matrix SHA-256,
exact candidate keys, provenance counts, and the presence of all 14 new live
guard rules.

## Concerns and open items

- **`udział` and subject-restriction enforcement remain prose-only**, exactly
  as the matrix already documents as a known, pre-existing architecture
  limitation (§9.1–9.2 of the matrix). This is not a new gap and was not
  worked around by inventing a field.
- **No contradiction with the frozen matrix was discovered during
  implementation.** Every one of the 41 rows was directly implementable in
  the locked candidate schema without exception, so no STOP condition was
  triggered.

No already-frozen linguistic schema decision was reopened here merely because
authoring turned out to be verbose (`pisać`/`napisać` correspondence alone is
24 of the 41 patterns). Every decision recorded above traces back to an
explicit matrix row, not to authoring-time judgment about the underlying
grammar.
