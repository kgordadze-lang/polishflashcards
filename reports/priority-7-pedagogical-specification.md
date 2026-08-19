# Priority 7 — Pedagogical Specification

**Phase:** 1 specification only  
**Learner promise:** “For this meaning of this verb, what comes next in Polish?”

## 1. Teaching unit and progression

The teaching unit is a reviewed meaning-specific pattern, not a lemma-to-case slogan. Existing case topics remain the place to learn declension and general case functions. Priority 7 supplies a verb-first bridge back to them.

Default progression is:

1. recognize the meaning and compact structured pattern;
2. connect participant role to a Polish question and full case name;
3. notice the pattern in one natural sentence;
4. choose a case/preposition/form in complete context;
5. build or complete a controlled sentence;
6. use Type It only when the answer space is demonstrably closed.

One high-value meaning/frame is introduced at its CEFR gate. Secondary, advanced, restricted, or ambiguous constructions remain recognition-only or deferred.

## 2. Meaning boundaries

Teach meaning before case. The learner must know which sense and participant is at issue before being asked to select a form. Two English translations remain one learner meaning when they name the same practical concept and accept the same participant mapping. Split meanings when roles, truth conditions, register, context, or activity answers differ materially.

Different surface frames may remain patterns under one meaning when they realize the same content differently. Conversely, similar English glosses do not justify merging `lubić` and `podobać się`, reflexive and non-reflexive forms, or semantically different constructions.

## 3. Learner terminology

Preferred language:

- “For this meaning…”
- “This verb takes…” only for a reviewed `lexical-frame` where the wording is not overbroad.
- “Ask `kogo? czego?`.”
- “Use `na` + Accusative.”
- “What comes next?”
- “This meaning uses a different pattern.”
- role prompts such as “Who receives it?” or “What are you talking about?”

Avoid as required learner vocabulary: “valency,” “syntactic government,” “actant,” “accommodation,” and “connotation.” Internal `relationType` values are never displayed verbatim.

Relationship-aware templates:

| Internal relation | Learner wording principle |
|---|---|
| `lexical-frame` | “With this meaning, [verb] takes…” or “Use [preposition] + [case].” |
| `constructional-frame` | Name the lemma-headed construction: “For a role or profession after `być`, use Instrumental.” Fixed `to jest` is not rendered as a verb pattern; link to a grammar contrast instead. |
| `means-method` | Name the function: “To say how you pay, use Instrumental.” Never “`płacić` always takes Instrumental.” |
| `subject-experiencer` | State roles: “The thing liked is the subject; the person is Dative.” |

These are principles, not final UI copy.

Priority 7 does not claim to model every Polish case construction. In particular, fixed `to jest` + Nominative is a boundary/out-of-corpus constructional contrast because the current hierarchy has no structured fixed-`to` constituent. A future `być` entry may link to an approved grammar explanation, but MUST NOT display a generic `być + Nominative` pattern. If fixed constructions later become canonical product entities, they require a broader construction model and separate approval.

## 4. Case display

At first teaching, show the complete English case name and Polish diagnostic question. Polish case name may appear in expanded detail. Abbreviations are never the only cue. Case questions are generated centrally; a reviewed override narrows them only when it makes the participant clearer. Vocative receives a direct-address cue rather than a fabricated question.

Prepositions are visually inseparable from their case in pattern display. A learner should see `na` + Accusative, not an opaque memorized string, and should also see the derived question `na kogo? na co?`.

## 5. CEFR policy

`cefr.recognition` is earliest recommended introduction; `cefr.production` is earliest recommended active production. Lemma and meaning floors are derived from child patterns.

| Level | Recognition expectation | Active-production expectation |
|---|---|---|
| A1 | Common one-frame direct cases, transparent preposition+case frames, and essential reference contrasts | Concrete, frequent frames with supplied meaning and fully deterministic person/number/gender/aspect |
| A2 | Common reflexive, two-role, cross-case, and experiencer constructions | Controlled cloze/build after case foundations; meaning and role explicit |
| B1 | Polysemy, less transparent multiple complements, register contrasts, and selected clause frames | Only frequent, native-reviewed patterns with natural closed prompts and useful payoff |

A familiar A1 lemma may contain an A2/B1 pattern. Valid above-B1 patterns are not included merely for completeness; if a contrast requires retaining one, mark it `deferred` and hide it from normal A1–B1 discovery.

## 6. Production versus recognition

The three teaching statuses are:

| Status | Learner use |
|---|---|
| `active-production` | Reference and recognition plus specifically eligible controlled production; it does not automatically allow Type It |
| `recognition-only` | Reference, explanation, search, listening recognition, and non-production choice where explicitly eligible |
| `deferred` | No normal A1–B1 learner surface; retained only for editorial contrast/research |

Research/review state is independent. Only `approved` records are learner-visible. A pattern can be linguistically approved yet recognition-only because production would be too ambiguous, uncommon, or advanced.

## 7. Usage and register

Use `core`, `common`, or `limited` teaching priority and `neutral`, `formal`, or `informal` register. Do not expose editorial frequency labels as claims unless evidence supports them. Rare, dated, regional, or otherwise restricted constructions are represented as `limited` with a sourced note and MUST be `recognition-only` or `deferred`, never `active-production`, in the A1–B1 pilot. Mędak validity or repository presence alone never establishes contemporary active-teaching priority.

## 8. Progressive disclosure

| Layer | Content |
|---|---|
| Recognition | display lemma, primary meaning gloss, derived compact pattern |
| Explanation | role, question, full case name, one concise relationship-accurate explanation |
| Example | one original natural sentence and natural English translation |
| Contrast | only a high-value alternate meaning/pattern or nearby construction |
| Practice | only explicit eligible activity with deterministic context |
| Reference detail | aspect link, register note, optional complement, additional examples |

Source and reviewer metadata are internal, not part of progressive learner disclosure.

## 9. Aspect and reflexive teaching

- Present aspect only when it helps the immediate practical choice.
- Never display unreviewed slash pairs as interchangeable.
- An aspect partner is not an accepted answer unless the activity context permits it and lists it.
- Preserve `się` in lemma, prompt, audio, and answer expectations.
- Reflexive/non-reflexive forms receive separate meaning explanations when syntax or meaning differs.

## 10. Feedback principles

Feedback identifies the trigger, then the expected form. Maximum default feedback is two short sentences: one reason and one correction/next-step cue. At A1, prefer plain English plus Polish question and full English case name. At A2/B1, concise Polish role language may supplement, but never replace clarity.

Feedback order:

1. identify meaning/construction or preposition;
2. name the role/question;
3. name the full case when useful;
4. show the correct form in its sentence context.

Examples of principles, not production copy:

- lexical: “Here, `szukać` uses Genitive: `kogo? czego?`”
- prepositional: “Use `na` + Accusative for the thing you are waiting for.”
- constructional: “For a profession after `być`, use Instrumental.”
- method: “This phrase says how you pay, so it uses Instrumental.”
- meaning-dependent: “This meaning uses a different pattern.”

Do not imply that a case rule applies to every meaning. English is appropriate for the explanation at A1–A2; the target Polish form and question remain visible. Feedback is not pronunciation-audio eligible by default.

## 11. Conversations and existing content

Conversations reinforce a reviewed pattern only where it already fits a natural branch. They remain contextual, not scored government tests. Existing cards, grammar, conversations, and exercises are unchanged; any future read-only pattern block is derived from one-way pattern references.

## 12. Pedagogical acceptance gate

A learner-visible pattern must have:

1. explicit meaning scope;
2. accurate relation type and role mapping;
3. structured complement(s), case/preposition, and derivable question;
4. suitable CEFR and teaching status;
5. contemporary verification, native review, and owner approval;
6. reviewed original example or validator-resolved approved repository reuse for any practice/listening use;
7. natural English gloss that does not imply syntactic equivalence;
8. default-false activity decision;
9. relationship-aware explanation and feedback plan;
10. no unresolved register, aspect, reflexive, or common-error claim.

## 13. Decision log

| Decision | Alternative | Reason / consequence | Reopen trigger |
|---|---|---|---|
| Recognition before production | translation-first production | reduces ambiguity and false error marking | evidence shows a pattern is immediately deterministic |
| Pattern-level CEFR | lemma-only CEFR | advanced senses of basic verbs remain gated | none expected |
| Three teaching statuses | four-plus production tiers | smallest actionable set | consumers require a distinct supported-production class |
| `limited` is recognition-only/deferred in A1–B1 | owner-note exception for active production | a closed enforceable rule avoids presenting restricted constructions as productive targets | explicit specification reopening |
| Relationship-aware wording | universal “verb takes” | prevents construction/method falsehoods | taxonomy changes |
| Case questions plus full names | abbreviations or jargon | connects current case curriculum to practical use | learner testing demonstrates another convention |
