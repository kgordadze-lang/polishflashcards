# Priority 7 — Phase 4F-H2

## Authorized learner-content completion, and editorial review only

**Baseline commit:** `4141872721d097e53c40f05e83b3ea730c38eff0`
**Baseline tree:** `1e34a1b0a86aaca5d6ab3caa2e936d522756c224`
**Phase date:** 2026-08-18
**Matrix:** `reports/priority-7-phase-4fh2-content-matrix.csv`
**Tests:** `tests/test_priority7_phase4fh2.py`
**Normaliser:** `tests/priority7_phase4fh2_normalizer.py`

---

## 0. What this phase is, and what it deliberately is not

On 2026-08-18 the product owner authorized a correction plan with two locked
content decisions: every learner-facing English prose field that quotes a
Polish illustration must give that illustration's English translation, and
every one of the 45 patterns must carry exactly one example.

**Authorizing the plan is not approving its output.** The corrected wording and
the new sentences had not been seen when the plan was authorized, so this phase
stops one tier short of release. It completes the content, re-enters the
editorial chain on every row it moved, and leaves those rows at
`editorial-reviewed` for the owner to inspect. **No product-approval event was
created in this phase and the corrected content is not product-approved.**

Tier 1 was not re-opened: the corrections live entirely above the
reference-verification scope, so **no reference-verification event was created,
altered or invalidated** and the 47 existing reference acceptances stand
untouched.

---

## 1. Reconfirmed scope

Recomputed independently from the baseline corpus before any edit, not taken on
trust from the Phase 4F-H1 audit. Every figure below matched H1 exactly.

| Finding | Expected | Reconfirmed |
| --- | --- | --- |
| Patterns | 45 | 45 |
| Examples at baseline | 29 | 29 (18 repository-reuse, 11 editorial-generated) |
| `learnerExplanationEn` fields holding an illustration | 32 | 32 |
| `errorNotes[].guidanceEn` fields holding an illustration | 22 | 22 |
| Prose fields to change | 54 | 54 |
| Polish illustrations to translate | 55 | 55 |
| Translation-affected patterns | 42 | 42 |
| Patterns with no example | 16 | 16 |
| Patterns with no translation defect | 3 | 3 |
| Patterns changed by example alone | 2 | 2 |
| Patterns untouched by H2 | 1 | 1 |
| Clean repository-reuse candidates | 2 | 2 |

The three patterns with no translation defect are
`vp-p-rozmawiac-talk-with-z-instrumental-o-locative-4e586b18cf98`,
`vp-p-zalezec-matter-to-someone-dative-experiencer-na-locative-1fc4131471cc` and
`vp-p-zajmowac-sie-look-after-person-instrumental-object-6f93facbd939`. The
first two carry only formulas (`z + Instrumental`, `o + Locative`,
`na + Locative`) and gained an example; the third also already had an example
and is therefore the one pattern H2 does not touch at all.

Grammatical labels (`kogo? czego?`, `komu? czemu?`, `kim? czym?`,
`na kogo? na co?`, `czego?`) and case formulas (`za + Accusative`,
`o + Locative`, …) were treated as notation and were **not** glossed. A test
asserts that none of them acquired a parenthesis.

### Repository-reuse candidate search, re-run

The repository index was swept for every lemma behind the 16 exampleless
patterns. Exactly two clean candidates exist, and they are the two the plan
locks:

* `b1-career-006.ex` — *Będę prosić szefa o podwyżkę.* realises
  `prosić` + Accusative person + `o` + Accusative thing.
* `b1-expressing-opinions-004.ex` — *Szczerze mówiąc, nie podoba mi się ten
  film.* realises `podobać się` with a Nominative subject and a Dative
  experiencer.

Everything else is a gap-fill prompt containing a blank
(`grammar-cases-dative-003`, `grammar-cases-instrumental-005`,
`grammar-cases-locative-003`, `grammar-cases-dative-008`,
`building-sentences-so-that-007`, `politeness-formal-address-008`), a different
lemma (`zaufanie`, `spodobać się`, transitive `zajmować`), or the wrong frame.

The two marginal `wierzyć` candidates H1 flagged are
`b1-exclamations-014.ex` (*Serio? Nie wierzę własnym uszom.* — a negated fixed
idiom, two sentences, exclamatory register) and `b1-everyday-slang-013.ex`
(*Nie wierz w to, to jedna wielka ściema.* — negated imperative, slang
register). The independent re-assessment agrees they are unsuitable, and per
the locked plan both `wierzyć` patterns received purpose-built
editorial-generated sentences instead.

---

## 2. Translation work — 55 glosses, 54 fields, 42 patterns

Each Polish illustration now carries a concise natural English gloss placed
immediately after it, in the locked style:

> What you are afraid of goes in the Genitive: boję się burzy (I'm afraid of
> the storm).

> To say who you worry about, use o + Accusative: boję się o dzieci (I'm
> worried about the children).

Thirteen fields carry two illustrations and therefore two glosses
(`płacę kartą (I'm paying by card), płacę gotówką (I'm paying in cash)` is the
only field with two in a single clause; the remainder are one illustration per
field). The complete before/after text of every field, with each illustration
and its gloss on its own row, is in the content matrix.

**No explanation was rewritten for style.** The suite proves this mechanically:
deleting exactly the 55 inserted `(gloss)` spans from the live prose reproduces
the baseline text byte for byte, on all 54 fields. Every other learner-facing
prose field in the corpus is baseline-identical.

---

## 3. Example work — 16 added, 45/45 coverage

| | Baseline | H2 added | Final |
| --- | --- | --- | --- |
| Patterns | 45 | — | 45 |
| Examples | 29 | +16 | **45** |
| repository-reuse | 18 | +2 | **20** |
| editorial-generated | 11 | +14 | **25** |
| original / human-authored | 0 | 0 | **0** |

Exactly one example per pattern. All 45 Polish sentences and all 45 English
translations are distinct. `authorRegistry` remains empty and
`origin.kind = original` remains unused.

### The two repository-reuse rows

| Pattern | Repository source | Polish (byte-identical) | English |
| --- | --- | --- | --- |
| `vp-p-prosic-request-accusative-person-o-accusative-thing-b7a8d9ce1a99` | `card:b1-career-006.ex` | Będę prosić szefa o podwyżkę. | I will ask my boss for a raise. |
| `vp-p-podobac-sie-appeal-to-nominative-stimulus-dative-experiencer-ef199e675ee9` | `card:b1-expressing-opinions-004.ex` | Szczerze mówiąc, nie podoba mi się ten film. | To be honest, I don't like this movie. |

Both resolve through `repository_index_from_root`, both are byte-identical to
the cited field, and both reuse the repository's own `exEn`, verified to
correspond to the exact reused Polish.

### The 14 editorial-generated rows

`origin.kind = editorial-generated`, `generatorRef = priority7-example-generation`,
`adoptedAt = 2026-08-18`, IDs allocated through `allocate_example_id(...)`.

| Pattern (lemma · construction) | Polish | English |
| --- | --- | --- |
| pomagać · Dative | Często pomagam sąsiadce. | I often help my neighbour. |
| pomagać · Dative + w + Locative | Pomagam bratu w matematyce. | I help my brother with maths. |
| słuchać · obey + Genitive | Ten pies słucha swojego pana. | This dog obeys its owner. |
| rozmawiać · z + Instrumental | Codziennie rozmawiam z mamą. | I talk to my mum every day. |
| rozmawiać · o + Locative | Zawsze rozmawiamy o muzyce. | We always talk about music. |
| rozmawiać · z + Instr. + o + Loc. | Rozmawiam z lekarzem o wynikach badań. | I'm talking to the doctor about the test results. |
| bać się · o + Accusative | Boimy się o dziadka, bo mieszka sam. | We're worried about our grandad because he lives alone. |
| mówić · Dative + Accusative | Zawsze mówię rodzicom prawdę. | I always tell my parents the truth. |
| mówić · Dative + że-clause | Mówię ci, że to dobry pomysł. | I'm telling you that it's a good idea. |
| ufać · Dative | Ufam swojej nauczycielce. | I trust my teacher. |
| wierzyć · Dative | Wierzę koleżance, bo nigdy nie kłamie. | I believe my friend because she never lies. |
| wierzyć · w + Accusative | Trener wierzy w tę drużynę. | The coach believes in this team. |
| zajmować się · Instrumental | Mój tata zajmuje się naprawą komputerów. | My dad works in computer repair. |
| zależeć · Dative + na + Locative | Bardzo mi zależy na tej pracy. | This job really matters to me. |

None of the pre-existing 29 examples was altered; the suite asserts each is
byte-identical to its baseline object.

---

## 4. Authoring pass and final editorial pass

Two separate passes, recorded separately because they are different work.

**AUTHORING PASS.** Drafted all 55 glosses and all 16 examples against the
locked style rules: exact semantic correspondence, correct person and
tense/aspect, no narrowing or broadening, no translating a grammar label as if
it were a sentence, and for examples a visible realisation of the governed
complement, contemporary neutral Polish, no competing construction, no proper
names or niche cultural references.

**FINAL EDITORIAL PASS.** A separate second-pass audit over the proposed
material, before any acceptance event was written, checking translation
accuracy, Polish grammaticality, pattern fit, meaning fit, CEFR
appropriateness, duplicate and near-duplicate example problems, register
mismatch, construction ambiguity and English naturalness.

Findings recorded by the final pass:

1. **Corrected before acceptance.** The gloss for `dziecko słucha mamy` was
   drafted as *(the child obeys its mother)*. `mama` is informal and `its` for
   a person is unnatural in current English; the gloss was changed to
   *(the child obeys their mum)*. This is the only change the second pass made
   to the authored material.
2. **Noted and accepted — overlapping vocabulary.** The new example for
   `mówić` + Dative + Accusative (*Zawsze mówię rodzicom prawdę.*) reuses
   *prawdę* from that pattern's own explanation gloss. `mówić` takes very few
   natural Accusative content nouns, and the example adds the Dative the
   explanation omits, which is exactly the contrast the pattern teaches. Kept.
3. **Noted and accepted — CEFR stretch.** The reused
   `b1-expressing-opinions-004` sentence sits on an A2/A2 `podobać się` row.
   Its Polish is byte-locked by the correction plan; the construction itself is
   A2 and the added `Szczerze mówiąc` filler is a fixed phrase that does not
   obscure it. Kept, and flagged here for the owner.
4. **Noted and accepted — spelling register.** The same row's English is the
   repository's own `exEn`, which says *movie* where the rest of the corpus
   uses British forms (*café*, *flat*, *maths*, *mum*). The plan requires the
   repository's existing translation where it corresponds, and it does. Kept,
   and flagged here for the owner.
5. **Checked, no defect found.** All 45 Polish sentences and all 45 English
   translations are distinct; no new example introduces a competing governed
   construction; no new example is negated where negation would confuse a case
   rule; every gloss translates its illustration rather than describing the
   grammar.

Neither pass is human review. Both were performed by the project's own
editorial workflow, and the governance record says exactly that:
`editorial-reviewed` means two independent nonhuman editorial passes agreed on
the learner-facing treatment against the current tier-2 scope. It is **not
human review**, not professional linguistic review and not native-speaker
review.

---

## 5. Governance

### Correction events — 42, exactly where authorized

`kind = correction`, `decision = accept`, `reviewerRef = product-owner-001`,
`reviewedAt = 2026-08-18`, recorded under the owner's existing product
authority. No new correction, reopen or external-verification role was
registered.

> Owner-authorized correction, 2026-08-18: add English glosses to the Polish
> illustrations in the learner-facing English prose and, where applicable,
> complete the example treatment. The corrected wording itself is not
> product-approved.

The two example-only patterns
(`vp-p-rozmawiac-talk-with-z-instrumental-o-locative-4e586b18cf98`,
`vp-p-zalezec-matter-to-someone-dative-experiencer-na-locative-1fc4131471cc`)
carry **no** correction event: nothing they already said was corrected. The
untouched pattern carries none either.

### Editorial chain re-entry — 44 patterns

On each of the 44 changed patterns, in order:

1. `editorial-review` / `changes-requested`, `actorRef =
   priority7-editorial-review`, with a note naming the actual H2 change
   (glosses, glosses + first example, or first example only);
2. `editorial-review` / `accept`, `actorRef = priority7-editorial-review`,
   `scopeVersion = 1`, `scopeDigest` = the freshly recomputed tier-2 digest,
   `corroboratingActorRefs = ["priority7-editorial-corroboration"]`.

130 events were appended in total: 42 × 3 plus 2 × 2.

### Event ledger

| Event | Baseline | H2 added | Final |
| --- | --- | --- | --- |
| `reference-verification` / accept | 47 | **0** | 47 |
| `editorial-review` / accept | 45 | +44 | 89 |
| `editorial-review` / changes-requested | 0 | +44 | 44 |
| `correction` / accept | 0 | +42 | 42 |
| `product-approval` / accept | 45 | **0** | 45 |
| `reopen` | 0 | 0 | 0 |

The 45 historical product approvals are preserved byte for byte. On the 44
changed patterns they are now **stale**: their pinned tier-3 digest no longer
matches the row's current tier-3 scope, which is precisely why nothing derives
`approved`. That staleness is recorded, not hidden.

### Final review state

| State | Count |
| --- | --- |
| `editorial-reviewed` | **44** |
| `approved` | **1** |

In words: 44 patterns are editorial-reviewed and exactly one is approved.

The one still-approved pattern is
`vp-p-zajmowac-sie-look-after-person-instrumental-object-6f93facbd939`, whose
row object is byte-identical to baseline.

---

## 6. Digest movement

| Tier | Scope | Patterns moved |
| --- | --- | --- |
| 1 — `external-verification` | structure, complements, usage | **0 / 45** |
| 2 — `native-linguistic` | + CEFR, teaching status, explanation, examples, error notes | **44** |
| 3 — `product-approval` | + contentRefs | **44** (the same 44) |

The untouched pattern retains all three digests and its standing approval. No
changed pattern derives `approved`, and a freeze of the live corpus admits
exactly one pattern — the untouched one — so the corrected rows are
structurally unable to reach a release before the owner sees them.

---

## 7. Audio and activity invariants

* `activityEligibility` is `[]` on all 45 patterns.
* `audioEligible` is `true` on 0 of 45 examples.
* `pp_audio_rule.py`, `pp-usage.js`, `audio-manifest.json` and every file under
  `audio/` are byte-identical to baseline.
* `verify_audio.py` is at its baseline revision. No MP3 was synthesised.

No listening or audio behaviour was enabled anywhere.

---

## 8. File footprint

Changed:

* `editorial/verb-pattern-candidates.json` — the content and governance work.
* `editorial/priority-7-authoring-context.json` — one appended `contextNotice`
  paragraph. No registry gained or lost an identity.
* `reports/priority-7-phase-4fh2-content-completion-summary.md` (this file)
* `reports/priority-7-phase-4fh2-content-matrix.csv`
* `tests/test_priority7_phase4fh2.py`
* `tests/priority7_phase4fh2_normalizer.py`
* 15 historical suites, repaired to compose the H2 normaliser (§9).

Byte-identical: `index.html`, `sw.js`, `manifest.json`, `pp-verb-patterns.js`,
`pp-usage.js`, `pp-answer.js`, `pp-distractor.js`, `pp-migrate.js`,
`priority7_tooling.py`, `validate_content.py`, `build_pages.py`,
`verify_audio.py`, `pp_audio_rule.py`, `generate_audio.py`, `sitemap.xml`,
`audio-manifest.json`, `robots.txt`, `CNAME`, every `data-*.js`, every
generated page and every audio file. `APP_VERSION` stays `8.10` and the shell
cache is unchanged. `content/verb-patterns.json` does not exist. The parked G2
workspace was not used and was not recreated. UI capitalisation
("Verb patterns") is unchanged; that is H3.

---

## 9. Historical test handling

Phase 4F-H2 legitimately supersedes the live approved-content state on 44 of
the 45 patterns, so the historical suites needed a phase-aware repair. That
repair is the phase-owned normaliser
`tests/priority7_phase4fh2_normalizer.py`, composed **innermost** — H2 comes
off before Phase 4F-F2's approvals, which come off before Phase 4F-E1's
editorial review:

```python
E1.without_phase_4fe1_editorial_review(
    F2.without_phase_4ff2_product_approval(
        H2.without_phase_4fh2_content_completion(live_corpus)))
```

The normaliser is closed over the exact H2 transition and **derives nothing
from the live rows**. For each of 44 allow-listed identities it pins the exact
appended event objects including their tier-2 digests, the exact before and
after text of every rewritten field, and the exact new example object. A row is
reverted only when every pinned fact still matches, so each of the following
survives normalisation and still breaks the guard it would otherwise hide
behind: an arbitrary learner-wording mutation, a wrong translation, a missing
or unexpected example, an altered existing example, wrong example provenance, a
stale or repinned tier-2 digest, a missing correction, a correction on an
unauthorized pattern, a new reference-verification event, a new product
approval, and a wrong review state. Identities outside the 44 are untouched
entirely. The normaliser imports no tooling, opens no file and runs no
subprocess, and a test asserts that.

Three historical claims were restated rather than relaxed, each because H2
performed something that had genuinely never been performed before:

* Phase 4F-A and Phase 4F-C2 swept the live corpus text for the token
  `correction`. That sweep now runs over the H2-normalised text, so a
  `correction` no authorised phase wrote still appears and still fails.
* Phase 5A asserted that no live event outside tier-3 product approval carries
  a `reviewerRef`. `correction` is the other human-borne kind by construction,
  so the sweep now names both explicitly and still refuses any event naming
  AB.
* Phase 4F-G1's footprint claim now permits exactly one exception: an
  `editorial/` file whose only difference from the G1 baseline is the pinned H2
  layer. Any other edit to those files, and any other path, still fails.

No earlier expectation was weakened, no historical digest was repinned, and no
normalised value was read from a live row.

---

## 10. Validation

| Check | Result |
| --- | --- |
| `python3 -m unittest tests.test_priority7_phase4fh2` | 92 tests, OK |
| Full Python discovery (`tests/`), working tree | 1739 tests, OK |
| Full Python discovery (`tests/`), committed scratch | 1739 tests, OK |
| JXA suites (`osascript -l JavaScript`) | 36 files, 10544 assertions, 0 failures |
| `validate-editorial` (real private context, real repository index) | valid |
| `python3 validate_content.py` | OK — 10 levels, 97 topics, 1215 cards, 353 drills |
| `python3 verify_audio.py` | OK — 3377 phrases, 3377 manifest entries, 3377 MP3s |
| `python3 build_pages.py --check` | OK — committed output current, 32 sitemap URLs |
| `git diff --check` | clean |

`validate-runtime` was not run: no official runtime file exists in this phase
and none was created in order to run it.

---

## 11. Product-owner review

The corrected corpus is ready for visual inspection. A disposable local
preview under an ignored scratch path projects only public-shaped learner
fields from the real H2 canonical content into the existing learner UI. It is
localhost-only and fail-closed, sends no editorial or governance JSON to the
browser, creates no `content/verb-patterns.json`, changes no tracked shipping
file and advances no version or cache. Start commands and the URL are in the
delivery report.

The owner is asked to confirm, among other things, that `boję się burzy` and
`boję się o dzieci` now carry English translations, that both `pomagać`
patterns now have examples, that all 45 patterns show exactly one example with
both Polish and English, and that no audio control has appeared.

Until the owner returns a decision on the corrected content, the 44 changed
patterns stay at `editorial-reviewed`.
