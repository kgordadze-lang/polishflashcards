# Priority 7 — Pattern Data Specification

**Phase:** 1 specification only  
**Status:** implementation-ready data contract; no learner-facing records are created here  
**Normative terms:** **MUST**, **MUST NOT**, **SHOULD**, and **MAY** are requirements at their usual strengths.

## 1. Locked architecture

The canonical editorial corpus is independent of existing cards and uses this hierarchy:

```text
dataset → lemma → meaning → pattern → complements[]
                                  └→ examples[]
```

Pattern-side references MAY point one way to existing cards, topics, drills, or scenarios. Existing content MUST NOT own verb-pattern facts or authored backlinks. Reverse indexes are derived by a future loader.

The hierarchy is locked as `lemma → meaning → pattern`. A lemma has one or more meanings; a meaning has one or more patterns; a pattern has one or more ordered complements. Pattern identity belongs to exactly one meaning and therefore exactly one lemma. It is never shared by two lemma entities.

The hierarchy has two representations with different security roles:

1. the **editorial canonical record** is the complete authoritative authoring/review/audit object;
2. the **deployable runtime projection** is a generated, separately validated public subset containing only fields required by learner features.

The runtime projection is not the canonical editorial source. Runtime consumers trust the approved projector result and never receive or interpret review/source/private audit data.

## 2. Entity boundaries

### 2.1 Lemma

A lemma is one learner lexical form, including `się` where present. `uczyć` and `uczyć się` are different lemma entities. Aspect partners are also different lemma entities.

Required fields:

| Field | Type / allowed values | Meaning and authorship | Learner-facing | Identity / change rule |
|---|---|---|---|---|
| `id` | stable ID matching the Priority 7 ID spec | Immutable entity identity; allocated by tooling from the initial identity seed | no | is identity; never changed or reused |
| `canonicalLemma` | non-empty NFC Polish infinitive, lowercase except lexically required case, single spaces | Normalized lexical form, including final `się`; linguistic editor authors, native reviewer confirms | yes | initial ID seed; a released spelling correction keeps the ID and uses correction workflow |
| `displayLemma` | optional non-empty string | Only when learner display must differ from `canonicalLemma`; omission means derive it | yes | wording only; no identity effect |
| `reflexive` | Boolean | Mechanically redundant readability/validation assertion that must equal whether `canonicalLemma` contains lexical final `się`; it is never an independent analysis | indirectly | correcting only the Boolean may keep ID; adding/removing lexical `się` in the canonical lemma changes lemma identity after release |
| `aspect` | `imperfective`, `perfective`, `biaspectual`, `unresolved` | Lexical aspect classification; `unresolved` is research-only | may be displayed | policy field; no ID effect |
| `meanings` | non-empty array | Owned meaning entities | through children | structural; ordering has no identity meaning |

Optional field:

| Field | Type | Rule |
|---|---|---|
| `aspectPartnerIds` | unique array of lemma IDs | Omit when no reviewed link exists. Links are reciprocal, non-self, human-confirmed, and never imply pattern inheritance. `unresolved` lemmas cannot publish partner links. |

The lemma does **not** store a CEFR floor or independent release/review status. Its floor is the minimum visible child-pattern recognition level. It is visible only when at least one child pattern is `approved` and learner-visible. This avoids duplicated state.

### 2.2 Meaning

A meaning is the smallest learner-relevant semantic distinction needed to choose or understand a Polish construction.

Create a separate meaning when at least one is true:

1. the truth conditions or participant roles materially differ;
2. the natural English gloss belongs to a different sense, not merely another translation;
3. register or CEFR makes the sense a separately gated teaching decision;
4. combining the senses would make an activity prompt or explanation ambiguous;
5. a native reviewer says the constructions represent distinct lexical senses.

Keep one meaning when several English glosses are ordinary translations of the same learner concept, or when a content realization changes without changing the sense—for example, nominal content versus a `że` clause may remain two patterns under one reviewed “tell/say content to a recipient” meaning.

Different syntax does not automatically force a new meaning. It always forces a new pattern when complement type, relation type, requiredness, preposition, case, or participant structure changes. Different constructions MUST NOT be collapsed merely because their English gloss is similar.

Required fields:

| Field | Type / allowed values | Meaning and authorship | Learner-facing | Identity / change rule |
|---|---|---|---|---|
| `id` | stable meaning ID | Immutable meaning identity | no | is identity |
| `key` | lowercase ASCII kebab key | Short internal sense discriminator selected once by linguistic editor, e.g. `seek` | no | part of initial ID seed; frozen after allocation |
| `glossesEn` | array of 1–3 distinct non-empty strings | Natural English glosses for one learner meaning; first is primary | yes | wording; does not change ID |
| `internalScope` | concise non-empty string | Internal inclusion/exclusion boundary, not dictionary prose | no | policy wording; no identity effect |
| `patterns` | non-empty array | Owned pattern entities | through children | structural |

CEFR is not copied onto a meaning. Its recognition floor is the minimum recognition level of its visible patterns; its production floor is the minimum production level of active-production patterns. Search may index reviewed `glossesEn` but MUST NOT index `internalScope`.

### 2.3 Pattern

A pattern is a complete, meaning-specific learner construction with one relationship classification and an ordered set of complement slots. A new pattern is required if any of these changes materially: relation type, complement count/order, complement type, case, preposition, clause kind, requiredness, or participant structure. Activity answer changes belong to their own `vp-x` item identities and do not redefine the linguistic pattern.

Required fields:

| Field | Type / allowed values | Meaning | Learner-facing | Identity / change rule |
|---|---|---|---|---|
| `id` | stable pattern ID | Immutable construction identity | no | is identity |
| `key` | lowercase ASCII kebab key | Immutable internal discriminator such as `genitive-target` | no | part of initial ID seed |
| `relationType` | closed enum in §3 | Prevents false claims about ordinary government | no; mapped to plain wording | structural identity; after release any change creates a new pattern ID and retires the old one |
| `complements` | non-empty ordered array | Machine-readable frame | rendered | structural; material change normally creates/retires a pattern |
| `cefr` | object in §8 | Earliest recognition and, when applicable, production level | may be displayed | policy; no identity effect |
| `teachingStatus` | `active-production`, `recognition-only`, `deferred` | A1–B1 teaching disposition | indirectly | policy; frozen after release |
| `usage` | object in §9 | Frequency priority and register | only non-neutral/restricted details | policy |
| `learnerExplanationEn` | non-empty plain-language string | Meaning-specific explanation that does not overclaim relation | yes | wording; no identity effect |
| `activityEligibility` | unique array of allowed activity keys; empty allowed | Permission to author/use a consumer; default false for omitted keys | no | policy |
| `evidence` | non-empty array for any candidate | Fact provenance, never copied passages | no | audit metadata; additions do not affect ID |
| `reviewState` | closed state in review specification | Current fail-closed state | no | policy |
| `reviewEvents` | array governed by review specification | Accountable human decisions with exact review-scope digests on acceptance | no | append-only audit data excluded from its own scope digest |

Optional fields:

| Field | Type | Rule |
|---|---|---|
| `aspectEquivalentPatternIds` | unique pattern-ID array | Reciprocal links only between reviewed aspect partners. Equivalence is explicit and never inherited. |
| `examples` | array of original or approved repository-reuse example objects | Required before listening or active grammar use; exact per-example origin rules are in the content-authoring specification. |
| `contentRefs` | unique typed one-way references | Existing content support only; never establishes linguistic truth by itself. |
| `errorNotes` | array of controlled error objects | Omit unless useful and evidenced; see content-authoring specification. |

No free-form pattern label is canonical. A future renderer builds the compact learner label from lemma and structured complements. `learnerExplanationEn` carries only nuance that cannot be derived safely.

## 3. Syntactic relationship model

### Decision

Use one required pattern-level `relationType` with four values:

| Value | Use | Covers required analysis |
|---|---|---|
| `lexical-frame` | The meaning lexically selects a direct-case, prepositional, infinitive, clause, or multi-complement frame | A `szukać`/`pomagać`-type direct case and a `czekać na`/`rozmawiać o`-type selected prepositional frame; their surface difference remains in complement `type` |
| `constructional-frame` | A broader grammatical construction headed by the lemma determines the case/shape rather than an ordinary object relation | Predicative `być` + Instrumental. Fixed `to jest` + Nominative is a boundary contrast, not a canonical verb-pattern record; see below. |
| `means-method` | The phrase expresses means or method and may be optional/adjunct-like | Required `płacić kartą/gotówką` fixture; it must not produce “this verb always takes Instrumental” |
| `subject-experiencer` | Learner-relevant subject/stimulus and experiencer roles differ from the English mapping | Required `podobać się` fixture |

Complement `role` makes participants explicit. Pattern families MUST be split if one record would mix relationship types. This keeps the taxonomy small while preserving accurate learner wording.

### Alternatives rejected

- **No explicit field:** rejected because complement shape alone would mislabel method, predication, and experiencer constructions.
- **Five or more academic relation types:** rejected as unnecessary for current product behavior; direct versus prepositional lexical selection is already encoded by complement type.
- **Relation only on every complement:** rejected for the pilot because it creates repetitive mixed-level analysis. Reopen only if reviewed Phase 2A/2B fixtures prove a single indivisible pattern truly mixes relation types.
- **Meaning subtype:** rejected because the same meaning can have several surface patterns while relationship classification belongs to the construction.

This decision is reversible only through a format-version change plus fixture migration if actual released records exist.

`to jest` is deliberately outside the canonical corpus. The fixed `to` construction is not representable by “lemma `być` + Nominative complement” without creating the misleading generic display `być + Nominative`. Priority 7 MAY link from a reviewed `być` pattern to a grammar topic that explains the contrast, using a typed `contentRef`. It MUST NOT encode `to jest` through `learnerExplanationEn`, `key`, or an opaque label. If product requirements later make fixed constructions canonical entities, the model must be broadened explicitly rather than gaining a one-off field. This boundary demonstrates that the verb-pattern corpus is selective, not a universal store for every case construction.

## 4. Complement model

`type` is closed to `case`, `preposition-case`, `infinitive`, and `clause`. Union types such as `case-or-clause` and `case-or-infinitive` are prohibited. Alternatives are separate patterns or separate complement objects in one pattern when they coexist.

Every complement has:

| Field | Type | Rule |
|---|---|---|
| `type` | closed enum | required |
| `required` | Boolean | required; means required for the pattern as taught, not universal grammatical obligatoriness |
| `role` | closed enum | required: `subject`, `object`, `recipient`, `experiencer`, `predicate`, `content`, `topic`, `interlocutor`, `means`, `target` |
| `questionOverridePl` | optional non-empty array | only when the centrally derived question is misleading or a reviewed role-specific subset is pedagogically better; must be native-reviewed |

Closed role values are deliberately small. Phase 2A tooling uses only these values; a later owner-approved specification revision may add a role if Phase 2B evidence requires one. Authors MUST NOT invent ad hoc role strings.

### 4.1 Direct case

Shape:

```json
{ "type": "case", "case": "dative", "required": true, "role": "recipient" }
```

`case` is required. `preposition` and `clauseKind` are forbidden. Direct `locative` is invalid because contemporary Polish Locative is prepositional. `vocative` is not a verb complement and is invalid here. `nominative` is allowed only with `constructional-frame` or `subject-experiencer` and only with role `subject` or `predicate`. This allowance does not make fixed `to jest` representable.

### 4.2 Preposition + case

Shape:

```json
{ "type": "preposition-case", "preposition": "na", "case": "accusative", "required": true, "role": "target" }
```

Both exact lowercase NFC `preposition` and `case` are required. `clauseKind` is forbidden. One complement stores one preposition. If different prepositions express different meanings or roles, use different patterns. Genuine synonymous alternatives may be separate linked patterns; an array of opaque strings is not permitted.

### 4.3 Infinitive

Shape:

```json
{ "type": "infinitive", "required": true, "role": "content" }
```

No case, preposition, or target infinitive is stored: the slot accepts a contextually chosen infinitive. Its default learner cue is centrally defined as `co zrobić?`. Control/raising taxonomies and aspect constraints are out of scope; if an activity requires a specific infinitive or aspect, that belongs to the activity item, not the linguistic slot.

### 4.4 Clause

Shape:

```json
{ "type": "clause", "clauseKind": "ze", "required": true, "role": "content" }
```

`clauseKind` is required and closed to:

| Value | Learner display |
|---|---|
| `ze` | `że…` |
| `czy` | `czy…` |
| `zeby` | `żeby…` |
| `interrogative` | an interrogative clause introduced by a reviewed question word |

One clause kind per complement prevents polymorphic strings. More kinds require a specification revision, not free text.

### 4.5 Multiple complements

Complement order is neutral pedagogical presentation order, not a claim that Polish word order is fixed. `mówić komuś coś` is two direct-case complements. `mówić komuś, że…` is a Dative complement plus a `clause` complement and therefore a separate pattern. Activity items own accepted word orders and concrete forms.

## 5. Case metadata and questions

Stable internal case IDs are:

| ID | English display | Polish display | Base questions used for derivation | Standard learner display |
|---|---|---|---|---|
| `nominative` | Nominative | Mianownik | `kto?`, `co?` | `kto? co?` |
| `genitive` | Genitive | Dopełniacz | `kogo?`, `czego?` | `kogo? czego?` |
| `dative` | Dative | Celownik | `komu?`, `czemu?` | `komu? czemu?` |
| `accusative` | Accusative | Biernik | `kogo?`, `co?` | `kogo? co?` |
| `instrumental` | Instrumental | Narzędnik | `kim?`, `czym?` | `kim? czym?` |
| `locative` | Locative | Miejscownik | `kim?`, `czym?` | `o kim? o czym?` as conventional case cue |
| `vocative` | Vocative | Wołacz | none | direct-address cue; no invented question |

This metadata is central, not copied into every record. Direct-case questions derive from base questions. Prepositional questions derive by prefixing the exact preposition to each base question, e.g. `na kogo? na co?`. `questionOverridePl` is exceptional, reviewed display metadata; it never changes the case or identity.

Case abbreviations such as `G.`, `D.`, or `A.` MAY exist in internal editorial notes but MUST NOT be stored as case IDs or used as the sole learner label. Initial learner display uses the full English case name plus Polish questions; Polish case names MAY appear in expanded reference detail.

## 6. Preposition rules

The preposition is mandatory whenever complement type is `preposition-case`. The same preposition with different cases creates different pattern structures and is never inferred from spelling alone. A future activity prompt MUST bind the intended meaning before asking for the preposition or case. Rendering and search use the structured `preposition` plus `case`; an unanalyzed string such as `na + accusative` is display output only.

## 7. Aspect and reflexivity

- Each pattern belongs to one lemma only. Aspect partners duplicate a pattern only after evidence shows the same learner meaning and frame for both lemmas.
- Equivalent partner patterns are two distinct pattern records with reciprocal `aspectEquivalentPatternIds`; they may share authored evidence references but never share identity.
- Duplication is acceptable because it makes meaning, CEFR, register, examples, and eligibility explicit per lemma.
- There is no automatic aspect inheritance. Native confirmation is required before either lemma or pattern links are approved.
- An aspect partner may have a different meaning inventory, pattern inventory, CEFR production level, or example set.
- `się` is part of `canonicalLemma`, its ID seed slug, search identity, display, audio expectations, and typed answers.
- Matching uses NFC/lowercase/space normalization and may accept query-only diacritic folding; it never removes `się` or merges reflexive and non-reflexive lemmas.
- A reviewed non-reflexive/reflexive relationship MAY be represented later as a typed cross-reference, but no such field is needed for the pilot. Search may show both only as separate results.

## 8. CEFR and teaching status

Pattern CEFR shape:

```json
{ "recognition": "A2", "production": "B1" }
```

Allowed levels are `A1`, `A2`, `B1`, and `above-b1`. `recognition` means earliest recommended introduction. Optional `production` means earliest recommended active production; omission means no active production in A1–B1. Production cannot precede recognition. `active-production` requires an A1–B1 `production` value. `recognition-only` omits it. `deferred` is hidden from normal A1–B1 learner surfaces and normally uses `above-b1` or records an editorial deferral.

Derived lemma/meaning CEFR floors are not stored. Valid but advanced dictionary constructions SHOULD be omitted from the pilot unless needed as a contrast; if retained, they are `deferred`, not activity eligible. The corpus is selective teaching content, not an exhaustive dictionary.

## 9. Usage/register

Required shape:

```json
{ "priority": "core", "register": "neutral" }
```

`priority` is `core`, `common`, or `limited`. `register` is `neutral`, `formal`, or `informal`. `limited` covers rare, regional, dated, or otherwise restricted evidence and requires a short, approved learner-facing `note`; evidence/source details remain separate. For the A1–B1 pilot, `limited` MUST NOT use `active-production`; it may be `recognition-only` or `deferred`. Any future exception requires an explicit specification reopening. The pilot does not need separate structured labels for every restriction. “Useful” is a product rationale, not a frequency label.

## 10. Activity eligibility and audio

Allowed `activityEligibility` keys are:

`reference`, `search`, `grammar-choose`, `grammar-build`, `type-it`, `listening`, `mixed-quiz`, `case-mix`, `conversation`.

The list is an allowlist, not an activity item. Missing keys are false. `approved` is required for every learner-facing key. `recognition-only` prohibits `grammar-build`, `type-it`, and any production-scored use. Exact prerequisites are normative in the activity-eligibility report.

Audio eligibility belongs to an example, not the lemma/pattern. An example MAY set `audioEligible: true` only when the containing pattern is approved, its allowlist includes `listening`, and the exact Polish sentence later passes audio/native QA. `reference` alone never authorizes audio. Labels, case names, questions, notation, and feedback are not audio eligible by default.

## 11. Examples, errors, references, and evidence

Example shape is defined in the content-authoring report and uses stable `vp-e-…` IDs. Examples are optional in research records and required for active learner use. Their Polish and English strings are wording, not identity seeds.

`contentRefs` entries use exactly:

```json
{ "kind": "card", "id": "existing-stable-id", "purpose": "support" }
```

Allowed `kind`: `card`, `topic`, `drill`, `scenario`. Allowed `purpose`: `support`, `practice`, `context`, `contrast`. Future validation resolves both ID and kind. Refs are one-way and never make a pattern approved.

Provenance, review events, and error-note shapes are defined normatively in their dedicated reports. Source passages, dictionary examples, screenshots, and copied definitions are forbidden.

An acceptance review event MUST carry `scopeVersion: 1` and a full SHA-256 `scopeDigest` over the canonical scope projection defined in the provenance/review specification. The projection includes the owning lemma and meaning, so a covered parent change invalidates every descendant pattern approval mechanically. `reviewState: approved` is valid only while current external, native, and product acceptance digests match their recomputed scopes.

## 12. Searchable semantics

A future field-aware index MAY include only approved/eligible learner data:

- `canonicalLemma` and `displayLemma`;
- `glossesEn`;
- structured case IDs plus central English/Polish display names;
- structured prepositions;
- centrally derived or overridden Polish questions;
- approved `learnerExplanationEn`;
- non-neutral approved register labels.

It MUST exclude IDs, keys, `internalScope`, evidence locators/notes, reviewer data, and source IDs. Query normalization is NFC, lowercase, whitespace collapse, and optional query-side Polish diacritic folding while preserving the indexed original. `się` and non-`się` identities remain distinct. Natural-language queries such as “which case after szukać?” require a future intent adapter; this schema supplies the fields but does not implement it.

## 13. File, privacy, projector, and loader strategy

### 13.1 Private editorial canonical record

The working Phase 2B name is `editorial/verb-pattern-candidates.json`, but directory naming is **not** a privacy boundary. The file is allowed only in the isolated/disposable and persistent local Priority 7 authoring/review workflow. It MUST NOT be transferred to the production/public site repository, Pages source, build input, deployment bundle, cache, index, or publicly retrievable asset tree. Release verification must prove it is absent from both the production transfer set and final production tree.

If real records need a durable private home beyond the local Priority 7 integration workflow, Phase 2B must make and approve that operational/security decision before authoring or review begins. This specification does not invent a private store inside the public static-site repository.

### 13.2 Public runtime projection

`content/verb-patterns.json` is a generated/validated **runtime projection**, not the full editorial source. It MUST NOT be named `data-*.js`: current validators/audio discovery glob that namespace and expect `PP_LEVELS.push(...)`.

The future frozen release transition must, in order:

1. validate the complete editorial record and registries;
2. recompute and prove current external/native/product acceptance digests;
3. validate prior frozen allocations, active identities, tombstones/no resurrection, replacements, and retained history when a prior release exists;
4. admit only `reviewState: approved` patterns with `active-production` or `recognition-only` teaching status;
5. project only the locked runtime fields in §14.2;
6. validate exact frozen/runtime parity and the runtime revision transition against a separate closed runtime schema;
7. only then source `content/verb-patterns.json` from the transition's `runtimeProjection` for application/deployment inputs.

A pure standalone transform may construct runtime shape for tests or as an internal step, but has no release authority. Historical allocation membership cannot prove active membership because tombstoned allocations are retained.

Runtime consumers never need reviewer/source/audit data to decide safety. A future dedicated `pp-verb-patterns.js` loader reads only the runtime projection. Service-worker integration, loader, projector/validator, runtime schema, frozen projection, and consumer adapters deploy atomically in a later authorized phase. Audio uses only projected examples with explicit `audioEligible` and `listening` eligibility.

## 14. Editorial and runtime envelopes

### 14.1 Nonproduction editorial envelope

The smallest Phase 2B full-record envelope is:

```json
{
  "artifactStatus": "priority-7-editorial-nonproduction",
  "formatVersion": 1,
  "lemmas": []
}
```

`artifactStatus` is required and exact; `formatVersion` selects the full editorial schema; `lemmas` owns complete lemma/meaning/pattern/example structures including `internalScope`, evidence, review state/events/digests, source/reviewer references, origin, and other approval/audit fields. There is no editorial work-in-progress revision counter. `patternDataRevision` is forbidden here and begins only with the first released runtime projection.

The Phase 1 fictional artifact is a third envelope—`artifactStatus: specification-example-not-production` plus `specificationNotice`, `formatVersion`, `patternDataRevision` fixture value, and fictional `lemmas`—used only to exercise this report-time precision Schema. Phase 2A must distinguish the specification-fixture schema, the full editorial schema, and the runtime schema.

### 14.2 Deployable runtime envelope and exact field set

Runtime top level contains only:

| Field | Runtime rule |
|---|---|
| `formatVersion` | integer `1` for the runtime contract |
| `patternDataRevision` | positive released runtime-corpus counter, beginning at first release |
| `lemmas` | non-empty approved projection array |

Runtime lemma contains: `id`, `canonicalLemma`, optional `displayLemma`, `reflexive`, resolved `aspect` (never `unresolved`), optional resolved `aspectPartnerIds`, and `meanings`.

Runtime meaning contains: `id`, `glossesEn`, and `patterns`. It excludes editorial `key` and `internalScope`.

Runtime pattern contains: `id`, `relationType`, `complements`, `cefr`, `teachingStatus` (`active-production` or `recognition-only` only), approved learner-facing `usage`, `learnerExplanationEn`, `activityEligibility`, optional resolved `aspectEquivalentPatternIds`, projected `examples`, runtime-needed `contentRefs`, and projected `errorNotes`.

Runtime example contains only `id`, `pl`, `en`, and `audioEligible`. Its editorial `key`, `origin`, author/source identity, and review data are excluded.

Runtime error note contains only `kind`, `incorrectForm`, and `guidanceEn`; editorial `evidenceRefs` is excluded. Runtime `usage` contains `priority`, `register`, and the approved learner-facing `note` when required. Complement and content-reference shapes remain the structured public shapes already specified.

The runtime projection explicitly excludes `internalScope`, all editorial keys not required by consumers, `evidence`, source IDs/locators/notes, `reviewState`, `reviewEvents`, `reviewerRef`, reviewer/source registries, all scope/evidence digests, example `origin`, `authorRef`, `authoredAt`, editorial error evidence references, editorial notes, and every rejected/deferred/unapproved candidate. Unknown/private fields fail the runtime schema.

Case metadata, role labels, clause displays, and enum display names remain loader/validator contract metadata rather than duplicated runtime content.

## 15. Decision log

| Decision | Alternatives | Reason / consequence | Reopen trigger |
|---|---|---|---|
| Independent one-way corpus | extend cards; fully isolated corpus | avoids frozen-card/progress coupling while preserving deliberate links | only if integration cannot work without two-way ownership |
| `lemma → meaning → pattern` | lemma→case; card-centric | handles polysemy, multiple frames, reflexivity, aspect | evidence that meaning layer is redundant across real pilot (unlikely) |
| Four relation types on pattern | none; academic taxonomy; per-complement relation | smallest model preventing the known false claims | indivisible pattern needs mixed relations |
| `relationType` is structural identity | treat as mutable policy | released construction classification cannot be silently repurposed | only before first frozen release may a candidate be replaced in place |
| Fixed `to jest` stays out of corpus | opaque label; one-off fixed-token field | current model cannot derive the fixed construction honestly | canonical fixed constructions require a broader entity model |
| Four complement types | union/free strings | closed, machine-readable, handles all pilot fixtures | reviewed pilot needs a genuinely new structural slot |
| Central case questions | copy on every complement | removes static duplication; override preserves pedagogy | derivation repeatedly fails native review |
| Single preposition per complement | opaque/alternative strings | keeps case-aware search/activity deterministic | true synonymous alternatives cannot be represented as linked patterns |
| Explicit duplicated aspect patterns | shared/inherited pattern | no hidden semantic inheritance | robust reviewed corpus proves safe inheritance |
| CEFR stored on pattern only | duplicate lemma/meaning levels | advanced senses remain possible; parents derive floors | consumer cannot derive efficiently (prefer build index first) |
| JSON in `content/` | `data-*.js`; executable JS | avoids current globs and execution | CSP/deployment evidence makes JSON impossible |
| Private editorial canonical record plus public runtime projection | browser-load the full audit record; treat an `editorial/` directory as private | preserves complete approval/audit authority without publishing private fields; complete frozen transition is the only release boundary | only a future secure authoring service may replace the isolated private workflow |
| Editorial envelope has status, format version, and lemmas only | reuse runtime `patternDataRevision` for WIP | makes nonproduction intent explicit without inventing revision semantics | concrete private workflow requirement for more envelope metadata |
| Deployable projection is approved-only | include half-reviewed/deferred candidates | fail-closed runtime admission and one meaning for “production corpus” | only an explicitly redesigned learner-preview channel |

## 16. Required fixture coverage

The model supports the required architecture fixtures and boundary without approving any linguistic claim:

| Fixture | Architecture feature tested |
|---|---|
| `szukać`, `potrzebować` | one direct Genitive complement |
| `pomagać` | direct Dative whose English gloss hides case |
| `czekać` | fixed preposition plus Accusative |
| `interesować się` | reflexive identity plus direct Instrumental |
| `rozmawiać` | one meaning with distinct `z`/Instrumental and `o`/Locative patterns |
| `bać się` | reflexive lemma and meaning-sensitive patterns |
| `mówić` | two direct complements versus Dative + clause |
| `płacić` | separate `means-method` and lexical prepositional patterns |
| `być` | possible Instrumental `constructional-frame`; typed link to an out-of-corpus `to jest` grammar contrast proves the corpus boundary |
| `podobać się` | Nominative subject/stimulus plus Dative experiencer |
| `zależeć` | separate meanings, multi-complement construction, recognition-first gating |

Every listed linguistic analysis remains a **provisional research fixture requiring contemporary external and native review**.
