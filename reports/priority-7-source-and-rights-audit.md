# Priority 7 — Source and Rights Audit

**Phase:** 0, reports only  
**Research source:** Stanisław Mędak, *Praktyczny słownik łączliwości składniowej czasowników polskich*, Universitas, supplied demo PDF  
**Status:** research input only. The PDF remains untracked under `_research/`; it was not modified, copied into `reports/`, or committed.

## 1. Source inspection

The supplied file is a 77-page, unencrypted PDF (1,158,905 bytes; SHA-256 `622d445a19cde50ce6951b9419b0cc2d3565d8b9239fd3af3c5a1ec93c002593`). All 77 pages were rendered for visual inspection and text extraction was checked against the rendered index pages.

The demo contains:

- introductory methodology and terminology;
- a complete numbered alphabetical index of 1,001 verb entries;
- sample detailed entries only for source entries 1–50;
- no complete set of 1,001 detailed valency entries.

The source's introductory framing reports 994 imperfective and seven perfective headwords, with some alternative or double labels. This is a source finding, not a recommendation for modern A1–B1 teaching.

## 2. What the source can and cannot establish

| Evidence available | Permitted Phase 0 inference | Not established |
|---|---|---|
| Complete 1,001-entry index | whether an app primary lemma is a listed form | a detailed construction for every listed verb |
| Introductory methodology | useful internal concepts and research questions | learner-facing wording or product architecture |
| Detailed sample entries 1–50 | candidate facts for a small subset, still requiring review | production-ready rules or examples |
| 2011 publication / earlier introductory material | historical descriptive evidence | present-day frequency, register, priority, or active-teaching suitability |

Only three proposed pilot lemmas fall within the demo's detailed sample range: `bać się`, `być`, and `czekać`. For the remaining source-listed pilot lemmas, the demo usually establishes headword presence only. `znaleźć` has no direct listed-form match in the index under the conservative method. None of these observations constitutes linguistic approval.

## 3. Internal extraction and QA

The complete index was reconstructed only for internal comparison. The following safeguards were applied:

1. source entry numbers were required to form the exact sequence 1–1,001;
2. index page boundaries and all five explicitly printed alternative-form groups were visually checked;
3. one OCR glyph substitution was repaired after visual comparison;
4. NFC Unicode, case-folding and whitespace collapse were applied;
5. Polish diacritics were preserved;
6. `się`, aspect, and multiword forms were not collapsed;
7. the five printed alternative groups were expanded only as explicitly listed alternatives, not as fuzzy matches.

The parsed index contains 1,001 numbered entries and 1,006 unique listed forms after expanding the five printed alternatives. Sequence validation cannot prove every OCR token; the extraction remains research tooling rather than a publishable edition.

The full index, rendered pages, extracted text, and temporary JSON were not placed in `reports/`. They will be removed from the worktree before handoff. The rights-safe overlap artifact, [`priority-7-book-headword-overlap.csv`](priority-7-book-headword-overlap.csv), has one row per app lemma and includes only app text, repository IDs, audit classifications, and source entry numbers.

## 4. Conservative overlap result

The app side contains 181 distinct primary infinitive lemmas from 228 strict infinitive-headed cards, including podcasts.

| Result | Count | Interpretation |
|---|---:|---|
| Direct listed-form matches | 98 / 181 | 97 source entry-string matches plus one explicitly printed alternative |
| No direct listed-form match | 83 / 181 | not a claim of semantic absence |
| Repository-pair-linked only | 26 / 181 | unstructured `pair` text; not counted as direct and not assumed to be true aspect |
| Opposite-`się` base collisions only | 3 / 181 | nonmatches; potentially distinct meanings/entities |
| No relation detected by the mechanical method | 54 / 181 | includes unencoded relations and genuinely unlisted/app-specific forms |
| Source entries without a direct primary-lemma match | 903 / 1,001 | absent from this narrow primary inventory, not necessarily absent from all app content |

There are no fuzzy, diacritic-stripped, reflexive-collapsed, or aspect-collapsed direct matches. Repository `pair` fields reference 28 source entries; the union of direct primary matches and encoded linked forms covers 125 distinct source entries, leaving 876 unrepresented by either mechanism. This secondary figure is heuristic because `pair` is free text and incomplete.

Four clear examples demonstrate why “no relation detected” is not semantic absence: app forms corresponding to `minąć`, `uciec`, `wziąć się`, and `zabłądzić` have plausible source-listed counterparts but lack usable `pair` metadata. Conversely, `szukać / znaleźć` shows why every slash must not be treated as an aspect pair.

## 5. Copyright and use boundary

The dictionary is a research source, not a content feed. Priority 7 must not:

- reproduce the 1,001-entry list;
- copy definitions, example collections, synonym sets, or entry prose;
- reconstruct detailed entries as a dataset;
- use source examples as app copy;
- imply endorsement by the author or publisher;
- treat historical validity as modern production priority.

Permitted internal use is fact-oriented and minimal: source identifier, entry/page locator, fact type, and reviewer conclusion. App examples must be independently authored and marked as authored; source locators should support a claim without embedding protected passages.

## 6. Recommended provenance record

The smallest useful provenance layer for a future pattern is:

| Field | Purpose |
|---|---|
| `sourceId` | stable internal identifier for the reference |
| `locator` | entry/page/section number; no copied passage |
| `factType` | headword, complement frame, usage/register warning, or contrast |
| `evidenceStatus` | what has actually been checked |
| `reviewerRef` / `reviewedAt` | accountable human review trail |
| `authoredExample` | separate flag/reference for independently written app copy |

Do not store screenshots, excerpts, or source example text in production data. If a claim is disputed later, the locator supports rechecking the research source without turning the repository into a derivative copy.

## 7. Contemporary verification workflow

| State | Entry condition | Learner-facing eligibility |
|---|---|---|
| `research-candidate` | repository or source suggests the pattern | none |
| `externally-verified` | checked against a modern reputable Polish reference and, where useful, contemporary corpus evidence | none by default |
| `native-reviewed` | competent native reviewer checks meaning, case, preposition, example, register and naturalness | still requires owner approval |
| `approved` | product owner accepts scope, CEFR, wording and activity use | eligible only for explicitly approved activities |
| `recognition-only` | valid but not suitable for active A1–B1 production | recognition/reference only |
| `rejected` / `deferred` | incorrect, marginal, outdated, ambiguous, or out of scope | none |

No external web/corpus research was authorized or performed in Phase 0. Detailed pattern claims outside the three sample entries therefore remain provisional even when repository evidence is strong. A competent native reviewer and final owner approval are mandatory for every pilot record.

## 8. Separation of claims

- **Source says:** the form is indexed, and for entries 1–50 the demo may provide detailed descriptive evidence.
- **Repository teaches:** a specific free-text rule, example, drill, or scenario line exists in current content.
- **Audit recommends:** a pattern deserves pilot investigation or a particular data shape.
- **Unresolved:** contemporary frequency, register, meaning boundaries, aspect/reflexive relations, production suitability, and final English gloss.

This separation must remain visible in Phase 1 tooling and later editorial review.
