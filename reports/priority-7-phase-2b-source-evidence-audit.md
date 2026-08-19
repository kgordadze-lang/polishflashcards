# Priority 7 — Phase 2B Source and Evidence Audit

**Phase:** 2B private editorial candidate authoring
**Artifact audited:** `editorial/verb-pattern-candidates.json` (private, nonproduction, unapproved)
**Status of every claim below:** research evidence only. Nothing in this report constitutes external verification, native linguistic review, or product approval.

## 1. Source policy actually applied

Four source identities exist in the private authoring context
(`editorial/priority-7-authoring-context.json`). They are deliberately separated so that
headword-list presence can never be mistaken for syntactic evidence.

| `sourceId` | `sourceKind` | `detailedEntryReviewed` | What it may support |
|---|---|---|---|
| `repository` | `repository` | n/a | What Po polsku currently teaches; never what contemporary Polish requires |
| `medak-2011-headword-index` | `medak-research` | `false` | `factType: lemma` **only** — inventory presence |
| `medak-2011-detailed-entry` | `medak-research` | `true` | `complement-frame` for the three lemmas whose detailed entry was actually read |
| `wsjp-pan` | `contemporary-reference` | n/a | Contemporary sense boundaries and `Składnia` frame classes |

The Phase 2A validator enforces this split mechanically. `MEDAK_DETAIL_NOT_ESTABLISHED`
rejects any non-`lemma` fact attributed to a Mędak registry entry that does not record a
reviewed detailed entry. The split is therefore not a convention but a checked invariant.

### Mędak use boundary

The demo PDF remains untracked in `_research/` and was neither modified nor copied.
Priority 7 stores only a source identifier, an entry-number locator, a fact type, a date,
and a short internal note. **No** headword list, definition, synonym set, entry prose or
example sentence from the book appears anywhere in Priority 7 data or reports. No
endorsement by the author or publisher is implied or asserted.

Headword-inventory presence for the 30 pilot lemmas was taken from the Phase 0 rights-safe
audit artifacts, which recorded the page-by-page inspection of the demo. The detailed
sample entries 1–50 were located and read in Phase 2B for exactly three pilot lemmas.

### WSJP use boundary

Each WSJP evidence record stores the entry/sense URL path **plus the exact section
consulted** — `Składnia` in 45 records, `Połączenia` in one. Priority 7 records only the
*class* of syntactic schema observed (for example "a bare `KOGO/CZEGO` frame"). A note
attached to a `Składnia` locator may never credit that section with a fact that came from
elsewhere on the page; §2 reports where that distinction bites. No WSJP definition,
collocation list, citation or example sentence is reproduced, and no WSJP sentence was
translated, adapted or reconstructed into a Po polsku example.

## 2. Per-lemma evidence summary

| Lemma | Mędak headword index | Detailed entry exists in demo | Detailed entry actually read in 2B | WSJP senses cited | Repository-reuse examples | Content refs |
|---|---|---|---|---:|---:|---:|
| `szukać` | entry 684 | no | no | 1 | 1 | 3 |
| `pomagać` | entry 440 | no | no | 1 | 0 | 5 |
| `słuchać` | entry 643 | no | no | 2 | 1 | 3 |
| `czekać` | entry 46 | **yes** | **yes** | 1 | 1 | 3 |
| `potrzebować` | entry 461 | no | no | 1 | 1 | 3 |
| `uczyć się` | entry 718 | no | no | 1 | 2 | 4 |
| `dziękować` | entry 113 | no | no | 1 | 2 | 4 |
| `płacić` | entry 406 | no | no | 1 | 2 | 5 |
| `używać` | entry 767 | no | no | 1 | 1 | 2 |
| `prosić` | entry 488 | no | no | 1 | 1 | 5 |
| `interesować się` | entry 141 | no | no | 1 | 1 | 3 |
| `dbać` | entry 60 | no | no | 1 | 1 | 2 |
| `tęsknić` | entry 696 | no | no | 1 | 1 | 2 |
| `rozmawiać` | entry 603 | no | no | 1 | 0 | 6 |
| `bać się` | entry 5 | **yes** | **yes** | 2 | 1 | 3 |
| `być` | entry 25 | **yes** | **yes** | 1 | 1 | 4 |
| `znać` | entry 972 | no | no | 1 | 1 | 4 |
| `lubić` | entry 197 | no | no | 1 | 2 | 5 |
| `mówić` | entry 226 | no | no | 1 | 0 | 4 |
| `pytać` | entry 573 | no | no | 1 | 0 | 3 |
| `widzieć` | entry 778 | no | no | 1 | 1 | 3 |
| `mieć` | entry 214 | no | no | 1 | 1 | 3 |
| `myśleć` | entry 232 | no | no | 1 | **0** | 3 |
| `znaleźć` | **not listed** | no | no | 1 | 1 | 3 |
| `podobać się` | entry 425 | no | no | 1 | 0 | 4 |
| `ufać` | entry 727 | no | no | 1 | 0 | 2 |
| `wierzyć` | entry 781 | no | no | 1 | 0 | 3 |
| `zajmować się` | entry 897 | no | no | 2 | 0 | 2 |
| `opiekować się` | entry 360 | no | no | 1 | 0 | 1 |
| `zależeć` | entry 904 | no | no | 2 | 0 | 4 |

**Totals:** 122 evidence records across 45 patterns — 46 contemporary-reference (WSJP),
46 repository, 30 Mędak (26 headword-only `lemma` records, 4 detailed-entry
`complement-frame` records). The WSJP records resolve to 44 locator strings over 34 distinct
numbered senses.

### Contemporary verification coverage — stated precisely

Every one of the 45 patterns carries at least one WSJP record naming the exact numbered
sense and the exact section consulted. That is **consultation** coverage, and it is 45/45.
It is *not* a claim that WSJP's formal `Składnia` encodes each authored frame verbatim, and
it is *not* the `external-verification` review gate, which requires a named human.

How each authored frame actually relates to the cited `Składnia` list:

| Class | Meaning | Patterns |
|---|---|---:|
| **A** | The authored frame corresponds to a complete listed `Składnia` schema, or to that schema's minimal realisation where the omitted slots are parenthesised as optional in the source | **40** |
| **B** | `Składnia` establishes the authored governed slot, but every schema containing it also carries a further non-optional participant that the pilot deliberately drops for teaching reasons | **3** |
| **C** | The complete combined realisation is attested in **neither** the formal `Składnia` list nor the collocation section; the individual slots are attested separately | **1** |
| **D** | The authored frame adds a structural slot that the schema does not name; that slot is the authoring editor's analysis | **1** |

**Class B — deliberate pedagogical subframes (3):**

| Pattern | Cited schemas always pair the slot with… | Authored as |
|---|---|---|
| `pomagać` + Dat | `w CZYM`/`przy CZYM`, `CZYM`, or an infinitive | Dative alone |
| `dziękować` + `za` + Acc | `KOMU` | `za` + Accusative alone |
| `pytać` + `o` + Acc | `KOGO` | `o` + Accusative alone |

Each is a defensible everyday realisation and each has its own sibling pattern carrying the
full frame, but **no cited schema realises the slot alone**. Whether the one-slot version
stands on its own is a native-review question, not something the source settles.

**Class C — `prosić KOGO + o CO` (1):** see §4.1.

**Class D — `podobać się` (1):** the cited `Składnia` names only the `KOMU` slot. The
structured Nominative stimulus-subject complement is the authoring editor's analysis of the
construction, recorded as such in the evidence note.

The honest summary is therefore: **40 of 45 authored frames map directly onto a listed
contemporary schema; 5 carry an explicit, recorded contemporary-verification gap.** Every
record remains `research`, so reporting the gap costs nothing and hiding it would have been
the only real error.

Repository evidence covers **42 of 45** patterns. The three without it —
`bać się` + `o` + Acc, `wierzyć` + `w` + Acc, and `zajmować się` (look after a person) — are
recognition-only second-sense patterns for which the current app corpus contains no
supporting material at all. That absence is recorded rather than filled with a weak
reference.

## 3. What Mędak did and did not establish

- 29 of 30 pilot lemmas appear in the demo's complete numbered headword index.
- `znaleźć` has **no** direct listed form under the Phase 0 conservative matching method.
  It therefore carries no Mędak evidence at all. Its structural claim rests on WSJP plus
  repository evidence.
- Detailed entries exist in the demo only for source entries 1–50. Of the pilot, only
  `bać się` (5), `być` (25) and `czekać` (46) fall inside that range. Those three entries
  were located and read; all other Mędak records in the corpus are headword-only and are
  typed `factType: lemma`.
- No detailed entry was inferred from headword presence anywhere in the corpus.

### Older-versus-contemporary divergences found

| Lemma | 2011 detailed entry lists | Contemporary WSJP `Składnia` lists | Disposition |
|---|---|---|---|
| `czekać` | both a bare `czego?` Genitive frame and `na co?/na kogo?` | only the `na` + Accusative nominal frame (plus `aż`/`żeby` clauses) | Only `na` + Accusative authored. The Genitive frame is **not** authored and is raised as native-review question NRQ-02. |
| `bać się` | bare Genitive plus `o co?/o kogo?` in one article | two separately numbered senses, one per frame | Modelled as **two meanings**, following the contemporary sense split rather than the 2011 single-article treatment. |
| `być` | a very long frame inventory including `czym?` | three predicative frames for the role sense, including `być + CZYM` | Only the role/profession Instrumental predicate authored; the rest deliberately out of pilot scope. |

## 4. Repository evidence and reuse

Repository evidence was gathered read-only through `validate_content.load_source_corpus`
over the seven `data-*.js` files. No existing card, drill, topic, scenario or podcast line
was modified.

- 101 typed one-way `contentRefs` resolve against real stable IDs and kinds; the validator
  checks both ID and kind.
- 23 examples are `origin.kind: repository-reuse`, each pointing at an exact card `ex`
  field. The validator enforces byte-exact string equality; a deliberately mutated
  sentence was rejected with `REPOSITORY_SOURCE_MISMATCH` during the negative-control run.
- Structural resolution is necessary but not sufficient. The `myśleć` reuse
  (`Co o tym myślisz?`, card `pl`) resolved perfectly yet realised the *opinion* sense that
  the authored meaning explicitly excludes, so it was withdrawn in the correction pass. Its
  card is now referenced with `purpose: contrast` and a `factType: contrast` evidence record
  explains why. **Semantic fit is a separate check from provenance validity.**
- **`opiekować się` has zero occurrences anywhere in the current corpus** (no card, drill,
  scenario, podcast or teaching line). Priority 7 fills a real gap there rather than
  duplicating existing material.
### 4.1 `prosić KOGO + o CO` — exact provenance treatment

This pattern is retained as a `research` candidate, but its provenance was rewritten so it
claims only what each section supports. It now carries three evidence records:

| Record | Section | What it establishes |
|---|---|---|
| WSJP `…/7501/prosic/4598076` | `Składnia` | an `o CO` slot, and separately a bare `CO` object slot. The note states explicitly that `Składnia` does **NOT** encode any combined `KOGO + o CO` frame. |
| WSJP `…/7501/prosic/4598076` | `Połączenia` | human Accusative objects of this verb are attested. The note states explicitly that this section does **not** attest a personal object combined with an `o` phrase. |
| Repository `data-a2.js#a2-restaurant-012` | — | an existing polite-request template with an addressee; the note states the combined two-complement frame remains a research candidate awaiting human external and native confirmation. |

No WSJP example, citation or collocation text is copied into the corpus or into this report.
The contrast with `pytać` is instructive and is recorded for the reviewer: for `pytać`,
`KOGO + o KOGO/CO` **is** a formally listed schema, so that combined pattern is class A while
`prosić`'s is class C.

- Drill `answer` reuse was evaluated and rejected as a source of learner examples: scalar
  `choose` answers are single words, and `build` answers are token arrays. Neither is a
  complete sentence, so no drill-sourced example exists in the corpus.

## 5. Where authored content relies on Claude judgment alone

Claude judgment is **never** recorded as evidence. It is recorded here so a reviewer can
see exactly what is unsupported by a cited source.

Sourced by cited evidence:

- every case, preposition, clause kind and complement inventory;
- every meaning boundary (each meaning corresponds to a WSJP-numbered sense or an
  explicitly reasoned union of adjacent frames under one sense);
- lemma aspect;
- the existence and location of the referenced repository material.

Claude editorial judgment, requiring human confirmation:

1. **Pattern selection** — which of the frames listed by WSJP were authored and which were
   left out of the pilot. Every omission is listed in the native-review queue.
2. **CEFR values** — all 45 `recognition` and 39 `production` values. Repository level
   placement informed these but does not determine them.
3. **Teaching status** — the `active-production` / `recognition-only` split.
4. **Usage priority** — `core` versus `common`. No frequency corpus was consulted, so these
   are teaching-priority judgments, not frequency claims. No `limited` value was assigned,
   because no evidence of restricted, dated or regional use was gathered.
5. **All 24 `predicted-distractor` error notes.** These are authored plausible wrong forms.
   None is claimed to be a documented common error: the corpus contains **zero**
   `documented-common-error` notes, because no learner-error dataset was available and the
   evidence-reference rules would not be satisfied by a rule statement alone.
6. **All `learnerExplanationEn` wording** and the choice of which repository sentence to
   reuse for each pattern.
7. **`relationType` assignment** for the four boundary cases (`płacić`, `być`,
   `podobać się`, `zależeć`), which Phase 1 explicitly left open.

## 6. Evidence gaps carried forward

| Gap | Affected records | Why it is open |
|---|---|---|
| No contemporary corpus (`contemporary-corpus`) evidence at all | all 45 patterns | Frequency, register and competition-between-constructions claims are therefore judgment, not measurement. Phase 1 §8 requires corpus evidence where those factors affect teaching. |
| `znaleźć` has no Mędak record | 1 pattern | Not in the demo headword index under the conservative method. |
| No aspect-partner links published | all 30 lemmas | The validator requires both linked lemmas to hold a current external-or-later review; every pattern is `research`. Free-text repository `pair` strings were deliberately not promoted. |
| No `usage.priority: limited` assessment | all 45 patterns | Would require register/frequency evidence not gathered. |
| 22 patterns have no example | see coverage report | Blocked by the missing named human example author, not by missing linguistic evidence. |
| 3 patterns have no repository evidence | `bać się` + `o` + Acc, `wierzyć` + `w` + Acc, `zajmować się` (person) | The current app corpus contains nothing for these recognition-only second senses. |
| 5 patterns whose authored frame is not a verbatim `Składnia` schema | 3 class B, 1 class C, 1 class D (§2) | Recorded explicitly rather than smoothed into a 45/45 claim. |
| `chcieć` and the `nie lubię` presentation | outside/adjacent to the pilot | `chcieć` is not a pilot lemma and was not touched. The `nie lubię` question is raised as NRQ-09. |

## 7. Corrections applied after independent review

Three source-attribution defects were found by independent review and corrected. No source
policy was relaxed; in each case the attribution was tightened to a single numbered
contemporary sense that genuinely licenses every authored frame.

| Lemma | Defect | Correction | Re-checked source |
|---|---|---|---|
| `lubić` | The Accusative pattern cited the people sense (`4064834`) while its example and the sibling infinitive pattern belong to the thing/activity sense | Both patterns now cite the single thing/activity sense, which lists `CO` and `BEZOKOLICZNIK` together and whose collocation range covers consumables and abstract nouns as well as activity verbs | `wsjp.pl/haslo/podglad/37948/lubic/4064835` |
| `wierzyć` | The `w` + Accusative pattern cited the truth/existence sense (`667886`) while its wording invoked the self-confidence sense | Both patterns now cite the trust sense, whose `Składnia` lists **both** `KOMU/CZEMU` and `w KOGO/CO`; the illustrative wording was changed away from `wierzę w siebie` | `wsjp.pl/haslo/podglad/2098/wierzyc/667887` |
| `myśleć` | The reused sentence realised the excluded opinion sense | Example withdrawn; card re-typed as a `contrast` reference plus a `contrast` evidence record | `wsjp.pl/haslo/podglad/17097/myslec/4692666` (unchanged) |

Both WSJP senses were re-fetched during the correction pass specifically to confirm that
one numbered sense licenses all the frames now attributed to it. Neither correction invents
a broader sense: in both cases the merge is *narrower* than what was previously implied,
because it now rests on one sense instead of two.

Mędak handling is unchanged by this pass.

### Final source-precision pass

A second independent review found three wrong sense identifiers and one overclaimed section
attribution. All four were corrected, and a systematic re-audit of **all 45** WSJP records
was then run.

| Lemma | Was | Now | Why |
|---|---|---|---|
| `widzieć` | `20375/4938155` ("kolegę") | `20375/4938152` ("dziurę") | the old locator is the separately numbered encounter/meet sense; sense 1 is visual perception and its `Składnia` gives `KOGO/CO` |
| `zależeć` (depend-on) | `35063/3938839` ("ktoś od kogoś") | `35063/3938838` ("coś od czegoś") | the old locator is the personal-dependency sense; sense 1 covers a thing or circumstance conditioned by an external factor and gives `od CZEGO` |
| `interesować się` | `45141/4723956` ("sytuacją") | `45141/4723955` ("muzyką") | sense 1 is the hobbies-and-interests sense that the authored meaning describes; same bare `CZYM` frame |
| `prosić` (combined) | one record claiming `Składnia, o CO plus personal object` | two records with exact section attribution | `Składnia` does not encode `KOGO + o CO`; see §4.1 |

Each replacement sense page was fetched during this pass and its `Składnia` transcribed
before the locator was changed. The affected `internalScope` wording was narrowed to match
the newly cited sense in all three cases.

Four further evidence notes were tightened in the same pass because they credited `Składnia`
with an unattributed editorial judgment: `pomagać`, `dziękować` and `pytać` now state that no
listed schema realises the authored slot alone, `podobać się` now states that the Nominative
subject slot is the editor's analysis, and `myśleć` drops a characterisation of the `nad`
alternant that the source does not make.

**All corrections in this pass were evidence-only.** No lemma, meaning, pattern or example
identity changed: all 132 IDs were verified byte-identical before and after.

### Re-audit result — all 45 records

The audit was run mechanically over the corpus against a transcript of every `Składnia` list
actually fetched in Phase 2B. It asserts that each cited sense exists in that transcript,
that no sense is cited which was never fetched, and that no `Połączenia`-sourced fact is
attributed to `Składnia`.

- 45 patterns audited; 34 distinct numbered senses cited; **every cited sense present in the
  verified transcript**, and no fetched sense left unused.
- Section-attribution check: **pass**.
- Classification: 40 class A, 3 class B, 1 class C, 1 class D (§2).
- **No further locator/sense mismatch was found**, and no pattern required a linguistic or
  model change.

## 8. Statement of separation

- **Mędak says:** the form is indexed; and for entries 5, 25 and 46, the detailed article
  describes the frames summarised in §3.
- **WSJP says:** the contemporary entry numbers these senses and lists these `Składnia`
  schema classes.
- **The repository teaches:** these specific existing cards, drills and lessons.
- **Claude proposes:** the selection, CEFR, teaching status, priority, explanations,
  distractors and relation-type classification listed in §5.
- **Unresolved:** everything in §6, plus every question in
  [`priority-7-phase-2b-native-review-queue.md`](priority-7-phase-2b-native-review-queue.md).

No record in this phase is externally verified, natively reviewed or approved.
