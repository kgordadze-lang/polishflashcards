# Priority 7 — Phase 4D-A Summary

**Human example-authorship package only. Not a review, not a verification, not an approval.**

## 1. Purpose and boundary

Phase 4C established that five proposed replacement examples are linguistically acceptable to a
real native Polish reviewer (AB, `native-reviewer-001`) but cannot enter the canonical corpus,
because `origin.kind: "original"` requires a registered human author and `authorRegistry` is empty.
Native linguistic acceptance is not authorship.

Phase 4D-A builds the smallest package that lets a real human **write** final example sentences for
those five pattern targets. It collects authorship and nothing else. No canonical data was
modified, no author was added, no review event was created, no verification was performed, no
approval or freeze was taken, and no runtime was generated.

## 2. Baseline

- Branch `priority-7-phase-4da-example-authorship`
- HEAD `e0ef6df4e721ec45111597a649e2a70de6f02907`
- Tree `7fcf2985374ab3cd62bf245468823a632b146728`
- Zero remotes, `push.default=nothing`, clean tracked working tree at start

## 3. Package location and files

Created outside Git at:

`/Users/Kaj/Downloads/Priority_7_Governance_Closure/Example_Authorship`

| File | SHA-256 |
|---|---|
| `README.md` | `8d15658109b7beeacaf4e1b856f65860550c46dbe2eb47296cabc643e3683330` |
| `Priority_7_Example_Authorship.xlsx` | `a52f1dd5dd88ef287e6cf859aa112bfdd224e27cda6865bcf70b507873247218` |
| `example-authorship.csv` | `9d6ee53d2f27dc8bbbaf639aef62aba542302bd5661beba600b954ce52d80321` |
| `manifest.json` | not self-hashed; carries the three digests above |

Four files, nothing else in the directory. No private source PDF, no copied dictionary entries, no
copyrighted source examples, and no existing corpus example sentence is reproduced anywhere in the
package (asserted mechanically against all 23 corpus example strings).

The workbook has four sheets: **Read me first**, **Author sentences** (the five rows),
**Declaration** (blank identity and declaration fields), **Canonical mapping** (reference IDs only).
`example-authorship.csv` carries the same five rows as UTF-8 with BOM and CRLF, so a double-click in
Excel renders Polish diacritics correctly.

## 4. What the governance tooling actually requires

Read from `priority7_tooling.py`, `editorial/priority-7-authoring-context.json`, the Phase 1
provenance architecture (`reports/priority-7-provenance-and-review-specification.md` §3, §5, §6),
the Phase 2C / 2C.2 reports, the Phase 4B and 4C summaries, and the Phase 5-A synthetic provenance
fixtures. No field was invented.

`_validate_origin` (`priority7_tooling.py:883`) defines a **closed** origin object —
`{kind, authorRef, authoredAt, repositorySource}`. For `kind: "original"`:

- `authorRef` and `authoredAt` are required; `repositorySource` is forbidden;
- `authorRef` must be lowercase kebab-case and must resolve in the private `authorRegistry`;
- the resolved author record must carry `human: true`;
- `authoredAt` must be a real ISO date and must not be in the future at validation time.

Verified directly against the real validator on an in-memory copy of the corpus (repository never
modified):

| Attempt | Validator result |
|---|---|
| New wording, origin left as `repository-reuse` | `REPOSITORY_SOURCE_MISMATCH` |
| `origin.kind: "original"`, no author fields | `SCHEMA_REQUIRED` ×2, `KEY_INVALID`, `DATE_INVALID` |
| `origin.kind: "original"`, unregistered `authorRef` | `AUTHOR_REGISTRY_DANGLING` |
| `origin.kind: "original"`, registered author with `human: false` | `AUTHOR_NOT_HUMAN` |
| `origin.kind: "original"`, registered author `{"human": true}` | **0 issues** |
| Same, with `authoredAt` in the future | `DATE_IN_FUTURE` |

**The author record requires exactly one field: `human: true`.** This matches the Phase 5-A
synthetic fixture (`tests/fixtures/priority7/synthetic-release-editorial.json`, author record
`{"human": true}`) and `tests/test_priority7_phase3b.py:95`.

Consequently the package requires the author to be a real human and **nothing else**. It does not
require native Polish, teaching or linguistics credentials, because no such requirement exists
anywhere in the tooling and inventing one would be a fabricated gate.

`context.author_registry` is never cross-checked against `context.reviewer_registry`; the
`REVIEWER_MULTI_ROLE_NOT_AUTHORIZED` check covers only the three review stages. Author/reviewer
separation is therefore a **governance rule enforced by the package instructions, not by the
tooling**. The package states explicitly that AB must not fill it in.

## 5. Review-scope dependency findings

Derived from `review_scope` (`priority7_tooling.py:472`), confirmed against the Phase 1 spec §6.3–6.6,
and proven by recomputing real digests on in-memory mutations of the actual corpus.

The scope projection is stage-cumulative. `external-verification` covers the common ancestor
projection plus `relationType`, `complements`, `aspectEquivalentPatternIds` and `usage` — it
**excludes examples entirely**. `native-linguistic` adds `cefr`, `teachingStatus`,
`learnerExplanationEn`, `examples` *(id, key, pl, en, exact origin, audioEligible)*, `errorNotes`
and `activityEligibility`. `product-approval` adds `contentRefs`.

Measured digest sensitivity:

| Mutation | external-verification | native-linguistic | product-approval |
|---|---|---|---|
| Example wording changed (`P7-NR-011`) | UNCHANGED | **CHANGED** | **CHANGED** |
| Example added where none existed (`P7-NR-042`) | UNCHANGED | **CHANGED** | **CHANGED** |
| Origin changed only, `pl`/`en` byte-identical (`P7-NR-012`) | UNCHANGED | **CHANGED** | **CHANGED** |

Answering the three questions directly:

- **External-verification scope — cannot be invalidated.** Neither wording nor provenance is inside
  the external projection. External verification of these five patterns is independent of this
  package and may run before or after it.
- **Native-linguistic scope — is invalidated.** By wording *and* by provenance alone. Recording
  `origin.kind: "original"`, `authorRef` and `authoredAt` on an otherwise byte-identical sentence
  is by itself sufficient to break a current native acceptance.
- **Parent meaning/pattern review — the facts are not invalidated,** since lemma fields, meaning
  fields, `relationType`, `complements` and `usage` are untouched by an example edit. But the
  native-linguistic scope is a single cumulative digest over the whole pattern projection, so a
  native reviewer re-reviews the entire pattern scope, not the sentence in isolation. There is no
  narrower "just the example" acceptance object.
- **Cascade:** `product_current` requires `native_current`, which requires `external_current`
  (`priority7_tooling.py:1310–1326`). Invalidating native therefore also invalidates product.

**Ordering consequence for the later human review:** authorship must be *fully recorded* — final
sentence, `origin.kind: "original"`, `authorRef`, `authoredAt` — **before** native-linguistic
review, because the provenance itself sits inside the native scope. Sending an authored sentence
for native review and *then* stamping its authorship would silently invalidate the acceptance just
obtained.

**Current impact: zero.** The corpus holds zero review events, so nothing recorded can be
invalidated today. Separately, AB's Phase 4C acceptance was of the exact AI-drafted wording; newly
authored sentences are different wording and that acceptance does not transfer to them.

No review data was modified or read destructively; all mutations were on in-memory copies.

## 6. The five rows and their canonical mapping

Every ID below was read out of `editorial/verb-pattern-candidates.json` and cross-checked against
the Phase 4B (§6) and Phase 4C (§7) mapping tables. Nothing was guessed.

| Review ID | Lemma | Lemma ID | Meaning ID | Pattern ID | Current example ID | Slot |
|---|---|---|---|---|---|---|
| P7-NR-011 | dziękować | `vp-l-dziekowac-8e4ca359cb86` | `vp-m-dziekowac-thank-f19a15334790` | `vp-p-dziekowac-thank-dative-recipient-za-accusative-057197dd300f` | `vp-e-dziekowac-thank-dative-recipient-za-accusative-thanks-for-cooperation-92656ebcc371` | replaces existing example |
| P7-NR-012 | płacić | `vp-l-placic-d709669437d2` | `vp-m-placic-pay-dd4705572184` | `vp-p-placic-pay-za-accusative-goods-73c6760c091d` | `vp-e-placic-pay-za-accusative-goods-how-much-for-everything-dd5e5c88cfd4` | replaces existing example |
| P7-NR-033 | widzieć | `vp-l-widziec-59dbe12f8b3d` | `vp-m-widziec-perceive-visually-65710cb07f86` | `vp-p-widziec-perceive-visually-accusative-object-80b697e51432` | `vp-e-widziec-perceive-visually-accusative-object-saw-your-sister-ec51af47f224` | replaces existing example |
| P7-NR-042 | zajmować się | `vp-l-zajmowac-sie-176f8a1300f8` | `vp-m-zajmowac-sie-look-after-person-b23fbb8fc99b` | `vp-p-zajmowac-sie-look-after-person-instrumental-object-6f93facbd939` | — none — | new example slot |
| P7-NR-044 | zależeć | `vp-l-zalezec-679daa27f9be` | `vp-m-zalezec-depend-on-d640b1729639` | `vp-p-zalezec-depend-on-od-genitive-source-1ad29f7a1318` | — none — | new example slot |

Three rows replace the single existing example on their pattern; two rows fill a pattern that has
no example at all (`examples: null`), consistent with Phase 4C §9.

Each author row carries only what is needed to write a sentence: Review ID, lemma, learner-facing
meaning, target pattern, the case/preposition relationship, a concise instruction describing what
the example must demonstrate, a blank *Final sentence by author (Polish)* field, a blank optional
English rendering, and a blank optional note. Canonical IDs live on the reference sheet and in
`manifest.json`, not in the authoring fields.

## 7. AI drafts are omitted entirely

**Decision: the previously accepted AI drafts are not shown anywhere in the package** — not in the
authoring field, and not in a separated reference section.

Rationale. Presenting an AI-written sentence beside a blank box produces a countersigned copy, not
authorship, which is precisely the distinction this phase exists to protect. The five targets are
short, ordinary sentences, and the pattern target plus case relationship plus learner explanation
are sufficient to write from unaided, so the draft carries no information the author needs — only
anchoring. A separated "reference only" section would have been honest labelling of a still-present
anchor; omission is stronger and costs nothing.

This is disclosed rather than concealed: the README tells the author plainly that AI drafts exist,
that a native speaker found them acceptable, and that they are being withheld on purpose and why.
The drafts remain on record in `reports/priority-7-phase-4b-summary.md` and
`reports/priority-7-phase-4c-summary.md` for editorial traceability — withheld from the author, not
deleted. Absence of all five draft strings from every package file is asserted mechanically.

## 8. Author declaration design

The declaration sheet carries verbatim:

> I wrote the final example sentences entered in this package. They represent my own final wording
> for the listed teaching targets.

Three explicit non-claims sit directly beneath it: that this is **not** a native-linguistic review
and signing does not make the sentences native-reviewed; that the author is **not** claiming to have
checked dictionary, corpus or other source evidence; and that the author is **not** taking a
reviewer, verifier or approval role.

Captured fields, all shipped **blank**: author name or initials; confirmation that the author is a
real person and not an AI system or automated process; date the sentences were written
(`YYYY-MM-DD`, rejected if in the future, feeding `origin.authoredAt`); declaration acceptance; and
an optional preferred author reference key. Nothing was pre-filled, assumed or fabricated. The
README also tells the author that leaving a row blank with a note is an acceptable outcome — a blank
row is honest, a row the author did not really write is not.

## 9. Package validation

Validated by reading the shipped files back off disk and checking them against the real corpus,
independently of the code that generated them. **81/81 checks passed.**

Covered: exactly four files and no extras; all three manifest SHA-256 digests match the shipped
bytes; exactly 5 CSV rows and 5 workbook rows; exactly the 5 required Review IDs in order, no
duplicates, no omissions; instruction and case-relationship populated on every row; every author
sentence, English rendering and note field blank in both CSV and workbook; the entire declaration
entry column blank; the declaration text present verbatim and carrying no native-review claim; every
lemma/meaning/pattern/example ID resolving in `editorial/verb-pattern-candidates.json` with correct
ownership; all five patterns still `reviewState: research` with zero review events; workbook mapping
sheet consistent with `manifest.json`; no authored sentence or declaration value anywhere in the
manifest; all five AI drafts absent; no existing corpus example sentence reproduced.

## 10. Canonical, governance and shipping proofs

Verified after the package was written:

- `editorial/verb-pattern-candidates.json` **unchanged** —
  SHA-256 `b6fb8139ed99368a2a1527db6dd79d32f06df3e2e069cf59ae559a798176435f`
- `editorial/priority-7-authoring-context.json` **unchanged** —
  SHA-256 `754346978577bf00a981fff528d3bd1e558c861eaf273e90d62a05372d52a7ea`
- Full-corpus `validate_editorial` against the real context: **0 issues**
- 30 lemmas, 34 meanings, **45 patterns, 45 `reviewState: research`** — no other state present
- **Zero review events** across all 45 patterns
- **`authorRegistry` still `{}`**; `allocationRegistry` still `{}`
- **`activityEligibility` empty** on all 45 patterns (0 entries corpus-wide)
- AB registry unchanged: exactly one reviewer, `native-reviewer-001`, role `['native-linguistic']`
  only, `ownerAllowsMultipleRoles` still absent, attestation ledger SHA-256 untouched
- All 23 corpus examples still `origin.kind: "repository-reuse"`; **zero `original` examples**
- The five replacements remain **noncanonical** — not inserted, not scheduled, not represented as
  accepted examples
- **No external verifier** named; no external-verification event; no approval; no freeze
- **No runtime generated** — `content/verb-patterns.json` still absent; no fixture, no projection
- **No shipping change** — no application, data, audio, build, test or tooling file touched

## 11. Git state

Exactly one tracked change, this report:

```
?? reports/priority-7-phase-4da-authorship-package-summary.md
```

`git diff HEAD` is empty. Zero remotes. `push.default=nothing`. HEAD still
`e0ef6df4e721ec45111597a649e2a70de6f02907`, tree still
`7fcf2985374ab3cd62bf245468823a632b146728`. **No commit, no push, no remote added.** The package
itself lives outside Git and is not staged, tracked or ignored-into the repository.

## 12. Verdict

**GO WITH NOTE.**

The package is accurate and ready to send. The mapping is exact, every author-supplied field is
blank, no authorship is fabricated, and the authorship route it feeds is the one the real validator
actually accepts. Three nonblocking governance considerations should be preserved for the phase
that ingests the returned package:

1. **The English rendering is optional.** The example schema requires `en`, so if an author leaves
   it blank, editorial supplies the English gloss — meaning an example recorded as
   `origin.kind: "original"` by author X may contain an English rendering X did not write. The
   Polish sentence, which is the teaching artefact and the thing the declaration covers, is
   unaffected. Worth an explicit editorial decision rather than a silent default.
2. **AB's acceptance does not carry over.** The five patterns will need a fresh native-linguistic
   review of the final authored wording *after* provenance is recorded, per §5. Nothing in the
   corpus currently claims otherwise, but the Phase 4C acceptance should not be read as covering
   whatever comes back in this package.
3. **Example `key` and ID hygiene is a downstream job.** Two rows need brand-new example IDs minted;
   three rows will carry a `key` describing the sentence being replaced (for example
   `how-much-for-everything`). The validator does not check `key` against `pl` — confirmed — so a
   stale key would pass validation silently. It should be regenerated when the sentences land.

None of these blocks sending the package. All three are decisions for the ingesting phase.
