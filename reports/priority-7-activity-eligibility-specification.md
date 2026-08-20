# Priority 7 — Activity Eligibility Specification

**Phase:** 1 specification only  
**Rule:** eligibility is an explicit allowlist and defaults to false. This report defines permission and prerequisites; it implements no activity logic.

## 1. Global gates

Every learner-facing activity requires `reviewState: approved`, matching `activityEligibility`, CEFR visibility, and exact owner-approved wording. `active-production` is additionally required for any task that makes the learner generate a form. Pattern approval alone never enables an activity.

At pattern-record level, `recognition-only` MUST NOT include `grammar-build` or `type-it`. `grammar-choose`, `mixed-quiz`, and `case-mix` remain possible because their future item records must separately declare recognition versus production semantics. `usage.priority: limited` MUST NOT combine with `active-production` in this A1–B1 pilot.

An eligibility key means “safe to author/collect a compliant item,” not “the pattern itself is a complete exercise.” Every future activity item has an explicit immutable `activityType` and authored `itemKey`; its stable identity is `vp-x-<pattern-stem>-<activity-type>-<item-key>-<digest12>`, seeded by `v1|exercise|<pattern-id>|<activity-type>|<item-key>`. This supports multiple items of one type for one pattern without array positions. Items also own context, answer set, feedback, and frozen policy.

## 2. Eligibility matrix

| Key | Recognition-only allowed? | Active-production required? | Minimum extra metadata/evidence |
|---|---:|---:|---|
| `reference` | yes | no | approved explanation and structured display |
| `search` | yes | no | approved whitelisted fields; useful target result |
| `grammar-choose` | yes, for recognition choice | only if selecting/generated form counts as production | complete context, safe distractors, one intended answer |
| `grammar-build` | no | yes | tokens, canonical order, all accepted orders, deterministic inflection |
| `type-it` | no | yes | closed accepted set and full disambiguating context |
| `listening` | yes | no | approved complete sentence, audio eligibility, safe question/distractors |
| `mixed-quiz` | recognition or production according to item | depends on item | approved item pool, sampling/feedback policy, no card-progress write |
| `case-mix` | recognition or controlled production | depends on item | case foundation, stratified pattern pool, explicit role/case target |
| `conversation` | yes | no | natural contextual occurrence; no artificial right/wrong branch |

## 3. Type It

Type It is eligible only when all are true:

1. context fixes the intended lemma, meaning, person, number, tense, gender where relevant, polarity, aspect, complement role, and required word order flexibility;
2. every natural answer within the intended scope is enumerated as canonical or accepted;
3. synonyms, aspect alternatives, pronoun omission, and common word-order variants are either ruled out by context or accepted;
4. the prompt tests one target decision rather than open translation;
5. a native reviewer can explain why an unlisted answer is outside the prompt.

Bare English cues such as “ask,” “talk,” “like,” “believe,” “know,” “care,” “find,” or “miss” are ineligible. A Polish sentence gap or a complete pragmatic scene is preferred. If answer closure is uncertain, use choose/build or recognition.

## 4. Listening

Listening uses a complete, natural, approved Polish sentence. Valid targets include recognizing:

- the intended meaning;
- a case ending in context;
- preposition + case;
- participant role;
- contrast between reviewed patterns.

`audioEligible: true` authorizes learner-initiated pronunciation of the exact approved example through the shared player. It does not authorize Listening. Listening remains independently gated by `activityEligibility:["listening"]` and still requires a separately governed exercise item with a safe question and distractors.

Do not synthesize or play lemma labels, pattern notation, case names, case questions, provenance, or isolated feedback. Distractors must be semantically non-colliding. Exact normalized existing audio is reused where the approved sentence matches; otherwise generation belongs to a later audio phase.

## 5. Grammar choose/build

Grammar is the primary pilot surface.

Choose requires complete context, exactly one intended option after considering natural variants, authored distractors, and feedback tied to meaning/role/question/case. Do not auto-generate every other case as a distractor.

Build requires a canonical complete natural sentence, explicit tokens, every approved alternate order, deterministic morphology, and a prompt that fixes the intended meaning. A two-complement pattern must make both roles clear. Unknown activity types fail validation rather than falling through to build.

## 6. Mixed Quiz and Case Mix

Pattern entities are never inserted as vocabulary cards. Before entering mixed practice, an item must:

1. already pass its base activity gate;
2. carry meaning, relation type, CEFR, target case/preposition, and recognition/production classification;
3. use a pool stratified enough to avoid accidental overrepresentation and false “all cases covered” claims;
4. provide pattern-aware feedback;
5. remain session-only and not modify current card/topic mastery.

Case Mix may reinforce case forms, but does not prove case coverage unless its future sampler explicitly guarantees it. Existing Case Mix behavior is unchanged.

## 7. Conversations

Conversation eligibility means the pattern may be linked as contextual reinforcement. It does not authorize rewriting a conversation, adding analytics, scoring branches, or claiming that all learners encountered it. A future explicit design is required before conversation choices become assessments.

## 8. Accepted answers and feedback metadata

Every future scored item owns:

- one `activityType` from the approved activity family;
- one immutable sibling-unique `itemKey` describing the authored context;
- one canonical answer;
- an explicit set of normalized accepted alternatives;
- accepted word orders where applicable;
- target meaning/pattern ID;
- target complement index/role when the task isolates one slot;
- feedback reason category: `meaning`, `preposition`, `case`, `role`, `inflection`, `aspect`, or `word-order`;
- concise approved feedback.

Pattern metadata never causes automatic answer invention. An aspect-equivalent pattern link is not an accepted answer declaration.

## 9. Activity rejection rules

Reject eligibility if:

- review is below `approved`;
- `recognition-only` includes `grammar-build` or `type-it`, or a future item validator classifies another selected item as production;
- `usage.priority: limited` combines with `active-production`;
- `teachingStatus: deferred` requests any learner surface;
- the example is absent/unapproved where a sentence is needed;
- more than one natural answer remains unintentionally valid;
- a restricted/dated construction would be presented as neutral core use;
- the task depends on an unreviewed aspect/reflexive relation;
- any example has `audioEligible: true` while its containing pattern is not approved;
- feedback can state only the answer but not the trigger;
- the activity would write current card progress or alter current pool totals.

## 10. Decision log

| Decision | Alternatives | Why selected | Reopen trigger |
|---|---|---|---|
| Allowlist array, default false | eligibility inferred from approval/status | prevents accidental consumers | none |
| Grammar first | Type It first | controlled context and safe distractors | pilot evidence supports closed typing |
| Separate future item IDs using type + item key | pattern doubles as exercise; type-only identity | multiple items per type retain separate frozen identity without positions | only the remaining exercise object shape is deferred |
| Pronunciation is independent from activities | infer Listening from audio or require Listening for playback | one exact example may be heard without becoming an exercise item | explicit future change to the shared playback policy |
| Session-only mixed practice | reuse card mastery | avoids semantic migration and false transfer | separately approved persistence design |
| Conversation reinforcement only | score existing branches | preserves natural scenario design | explicit future conversation assessment scope |
