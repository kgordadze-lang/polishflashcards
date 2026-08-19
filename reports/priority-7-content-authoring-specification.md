# Priority 7 — Content Authoring Specification

**Phase:** 1 specification only  
**Scope:** rules for a future owner-authorized Phase 2B authoring subdivision; this report does not author the 30-verb pilot.

## 1. Polish examples

Every learner-facing example is original or an explicitly approved repository reuse with verified origin. It must be:

- one complete natural sentence, normally 4–12 orthographic words at A1, 5–15 at A2, and 6–18 at B1;
- plausible in everyday life in Poland (home, work, study, services, health, travel, relationships);
- controlled to vocabulary at or below the pattern’s recognition level except unavoidable transparent names/items;
- sufficient to identify the meaning, participant roles, polarity, aspect, and intended complement;
- focused on one target pattern; a second target is allowed only when the activity explicitly teaches their interaction;
- free of avoidable ambiguity, unnatural word order, and dictionary-like wording;
- independently reviewed for morphology, agreement, punctuation, register, and pragmatics.

Pronouns are welcome when they naturally make case contrast clear, but should not hide the target ending repeatedly. Noun/adjective agreement may provide useful practice only after the target case is known and the prompt fixes gender/number. Avoid negation unless negation is the intentional target: direct-object negation can change case and would otherwise confound the lexical pattern. One exact example may support multiple patterns only when the review explicitly maps each target and each consumer keeps one clear question; do not duplicate the string under competing identities solely for convenience.

## 2. Example data shape

```json
{
  "id": "vp-e-...",
  "key": "first-context",
  "pl": "Original Polish sentence.",
  "en": "Natural English translation.",
  "origin": {
    "kind": "original",
    "authorRef": "human-author-record",
    "authoredAt": "2026-08-08"
  },
  "audioEligible": false
}
```

The example’s common fields are required. `pl`/`en` are learner-facing frozen wording but never ID seeds. `audioEligible` defaults conceptually to false but is explicit to prevent generic phrase collection. It may be true only under a containing approved pattern whose allowlist includes `listening`, followed by exact-sentence audio/native QA; `reference` alone is insufficient.

For `origin.kind: original`, `authorRef` and `authoredAt` are required and `repositorySource` is forbidden. For `origin.kind: repository-reuse`, `repositorySource` is required:

```json
{
  "kind": "repository-reuse",
  "repositorySource": {
    "kind": "card",
    "id": "a1-stable-card-id",
    "field": "ex"
  }
}
```

Allowed sources are stable `card` (`pl`/`ex`) and `drill` (`prompt`/`answer`) entities. The validator resolves the exact field and sentence. `authorRef`/`authoredAt` MUST be omitted for reuse, and pattern-level `contentRefs` are not example provenance. Phase 1 fixtures may use `specification-fixture`; editorial production candidates and runtime validation forbid it.

## 3. English glosses and translations

### Lemma/meaning glosses

- Translate meaning, not Polish syntax.
- Keep 1–3 glosses inside one `glossesEn` array only when they represent the same learner sense.
- Split polysemy when a gloss would invite a different Polish construction or participant mapping.
- Phrasal English verbs are allowed when natural (`wait for`, `look after`); do not strip the particle to mimic Polish structure.
- Reflexive Polish forms receive the natural English meaning, not a forced “oneself” translation.
- A parenthetical may disambiguate a short gloss (`know (a person/place)`) but is not a grammar explanation.
- Never imply syntactic equivalence. The gloss “help” is fine for meaning; the explanation/activity must show Polish Dative.

### Example translations

Use natural English that preserves the situation and participant roles. A literal translation may appear only as optional explanatory wording when it genuinely clarifies structure; it never replaces the natural translation. Keep names, tense, polarity, and information structure aligned enough that the learner can identify the target.

### Explanatory wording

Explanations may contrast English and Polish explicitly, but avoid claims that English “has no cases” or that one language maps mechanically onto the other. Use the relationship-aware terminology in the pedagogical specification.

## 4. Learner explanations

`learnerExplanationEn` is one short sentence, normally at most 22 words. It names the meaning/function, preposition if relevant, and full case/question without internal jargon. It must not duplicate a case lesson or state “always” unless the reviewed scope truly supports it.

## 5. Common errors and distractors

`errorNotes` is optional and must not exist merely to fill a template.

```json
{
  "kind": "documented-common-error",
  "incorrectForm": "short form only",
  "guidanceEn": "Concise positive correction.",
  "evidenceRefs": [0]
}
```

Allowed `kind` values:

- `documented-common-error`: evidence shows a recurring learner error; `evidenceRefs` is a non-empty list of indexes into pattern evidence and native review must accept the claim “common.”
- `predicted-distractor`: an authored wrong option is pedagogically plausible but is not claimed to be common; evidence refs are optional.

The numeric indexes are an editorial convenience only. After shape/range validation, native and product review scopes resolve each index to the complete evidence-record SHA-256 digest, preserving reference order. Authors may append unrelated corroboration without disturbing a reviewed claim. If evidence is inserted before a referenced record, updating the numeric index to keep the same resolved digest does not by itself require re-review. Reordering without updating the reference, or editing the referenced record, changes the resolved digest and invalidates native/product acceptance. A currently reviewed `documented-common-error` must resolve exclusively to evidence pinned by the current external acceptance.

`incorrectForm` and `guidanceEn` are required, learner-facing only when the activity calls for them, and frozen wording. Avoid long or memorable repetition of incorrect Polish. If evidence is insufficient, use `predicted-distractor` or omit the note; never label it common.

## 6. Feedback authoring

Feedback is normally at most two short sentences and about 28 English words total. It should:

1. name the meaning/construction trigger;
2. give the Polish question and/or preposition;
3. name the full case where helpful;
4. show the correct answer in context.

At A1, English explanation is preferred with Polish target cues. At A2/B1, brief Polish role wording may supplement it. Feedback for a wrong case should not introduce an unreviewed alternative construction. Meaning errors are corrected before morphology errors when both occur.

## 7. Authoring workflow

For each future pattern:

1. define the meaning boundary and internal immutable keys;
2. add repository/research evidence locators;
3. obtain contemporary external verification;
4. select relation type and structured complement roles;
5. assign CEFR, teaching status, usage, and default-false eligibility;
6. draft an original Polish example or select an exact traceable repository reuse, then author/verify its natural English translation, explanation, and only evidenced error guidance;
7. run schema/ID/referential validation;
8. obtain native linguistic review of the exact record;
9. revise and re-review until accepted;
10. obtain product approval with a matching current product-scope digest;
11. only then run the authorized frozen release transition; a future public runtime subset may come only from that transition's validated `runtimeProjection`, never from a standalone shape projector.

Phase 2B candidate authoring does not itself admit records to the deployable projection. The full `editorial/verb-pattern-candidates.json` is permitted only inside the isolated local Priority 7 workflow and MUST NOT be copied or committed into the production/public static-site repository. Directory naming is not a privacy control. If a durable private home is needed beyond this workflow, Phase 2B must approve it before real records are authored/reviewed.

No author may copy source prose or treat AI-generated consensus as a review event.

## 8. Decision log

| Decision | Alternatives | Why selected | Reopen trigger |
|---|---|---|---|
| Short complete contextual examples | fragments/labels; long rich examples | natural audio and deterministic meaning with controlled load | testing shows level-specific limits need adjustment |
| Natural English + optional literal explanation | literal-only | preserves meaning without false syntactic equivalence | none expected |
| Optional evidenced error notes | mandatory “common error” | prevents invented claims | robust learner-error dataset supports more structure |
| One target pattern by default | multi-target efficiency | feedback remains attributable | deliberate integrated practice phase |
| Explicit `audioEligible`, authorized only by approved `listening` | infer from `pl` or `reference` | controls audio growth and leaves future reference playback undesigned | explicit reference-playback design |
| Typed per-example `repositorySource` for reuse | infer source from pattern `contentRefs` | independently auditable exact sentence origin | repository adopts a stronger universal utterance identity |
