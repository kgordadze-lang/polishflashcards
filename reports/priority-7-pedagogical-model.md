# Priority 7 — Pedagogical Model

**Phase:** 0 recommendation only. This document specifies teaching principles, not final UI.

## Learner promise

Priority 7 should answer one practical question:

> For this meaning of this verb, what comes next in Polish?

The internal model may use precise linguistic terminology. Learner-facing copy should prefer:

- “This verb takes…”
- “Ask `kogo? czego?`”
- “Use `na` + accusative”
- “This meaning uses a different pattern”
- “Who receives it?” / “What are you talking about?” where a role makes the rule clearer

Do not require learners to understand “valency,” “syntactic government,” “actant,” “accommodation,” or “connotation.”

## 1. Two navigation directions

### Verb first — primary Priority 7 path

A learner looks up `szukać`, `pomagać` or `rozmawiać` and sees:

1. the intended meaning;
2. a compact “what comes next” pattern;
3. the Polish diagnostic question(s);
4. preposition, if any;
5. full case name;
6. one independently authored natural example;
7. optional contrast or common error;
8. practice only when the record is approved and deterministic.

### Case first — retain the current foundation

Existing case topics should remain the place to learn forms and broad functions. A future case view may list selected approved trigger verbs, but it should link to the meaning-specific pattern rather than assert that a lemma always takes one case.

The two paths should share one canonical pattern entity; they should not duplicate explanations.

## 2. Progressive disclosure

| Layer | Learner sees | Purpose |
|---|---|---|
| 1. Recognition | lemma, meaning, compact pattern | answer “what follows?” quickly |
| 2. Explanation | question, role, ending/form reminder, one example | connect the verb to known case knowledge |
| 3. Contrast | another meaning/pattern or nearby verb | prevent translation-driven errors |
| 4. Practice | controlled choose/build/listen/type task | retrieve the pattern in context |
| 5. Reference detail | register, optional complements, aspect note, source/review status internally | support advanced use without overwhelming A1/A2 |

Do not show every linguistic possibility to every learner. Teach one high-value meaning/frame at its CEFR gate; add secondary frames only when they solve a common practical problem.

## 3. Meaning before case

A pattern belongs to a meaning, not blindly to a spelling. Examples:

- `rozmawiać z kimś` identifies an interlocutor; `rozmawiać o czymś` identifies a topic.
- `pytać kogoś` and `pytać o coś` attach different roles; `prosić o coś` is not interchangeable with generic English “ask.”
- `lubić coś` and `coś podoba się komuś` express related English meanings with different Polish roles.
- a concern frame for `bać się o…` must not be merged with the feared-stimulus frame solely because the lemma matches.

When a second frame changes meaning, label the meaning first. When two complements coexist, show each role/question separately.

### Relationship-aware wording

Use “this verb takes…” only when that wording accurately describes the relationship. Learners still need plain guidance, not an internal taxonomy. Depending on the reviewed analysis, suitable wording may instead be:

- “Use Instrumental for the payment method” for `płacić`;
- “After `być`, use Instrumental for a role or profession”;
- “The `to jest` construction uses Nominative”;
- “With `podobać się`, the liked thing is the subject and the person is Dative.”

Phase 1 must decide the smallest internal distinction needed among lexical, preposition-governed, predicative/constructional, means/method or adjunct-like, and subject/experiencer relationships. Those labels need not be exposed to learners.

## 4. Recognition before production

Recommended progression:

1. notice the pattern in a natural sentence;
2. choose the correct question/case/preposition for a supplied meaning;
3. choose the correct noun/pronoun form;
4. build a complete sentence from controlled tokens;
5. produce a form in a contextual cloze;
6. only then consider freer Type It.

Reference contrasts such as `mieć/lubić/znać` can enter production earlier. Multi-pattern verbs such as `mówić`, `wierzyć`, `podobać się` and `zależeć` should begin recognition-first.

## 5. Activity model

### Choose

Best first practice for:

- correct case/preposition after an explicit meaning;
- question-to-role mapping;
- contrasting `z` versus `o`, or direct case versus prepositional frame;
- selecting between closely related verbs when context is complete.

Distractors must be authored and semantically safe. Do not generate every “other case” as a distractor automatically.

### Build / controlled cloze

Best production bridge for:

- case endings in a full sentence;
- two-complement frames;
- word-order variants with explicit `acceptedOrders`;
- preposition+noun phrase assembly.

The prompt must supply enough context to make meaning, person, number, gender and aspect deterministic.

### Type It

Use sparingly. A closed answer set is required. Bare English cues such as “ask,” “talk,” “care,” “know,” “like,” “believe,” “find,” or “miss” are unsafe. A full context or a Polish sentence gap may make a pattern eligible; explicit accepted alternatives must cover every intentionally valid answer.

### Listening

Use approved complete natural sentences. Ask learners to recognize meaning, complement role, preposition or case ending. Do not synthesize abstract pattern labels, case questions or notation.

### Mixed Quiz / Case Mix

Future integration should sample by approved pattern family and CEFR, not insert pattern entities as vocabulary cards. Pattern performance must not write current card mastery. Case Mix can reinforce forms but does not guarantee all cases in one round.

### Conversations

Use as contextual reinforcement. Existing scenario notes/recaps can eventually link to approved patterns. Do not turn authored branches into artificial right/wrong tests and do not force a verb into a scenario where it is unnatural.

## 6. Optional block on existing cards

A selected current card could eventually display a compact pattern block, but the card should not own the data. The block should be a read-only view resolved from pattern-side `contentRefs`. This avoids changing frozen cards, prevents duplicated wording and lets one pattern appear in verb-first, case-first and contextual views.

Not every verb card needs a block. Phrase/idiom cards, mature/recognition-only content and ambiguous translations may be better linked to a reference entry without production practice.

## 7. Aspect and reflexivity

- Keep aspect partners as distinct stable lemma entities linked after review.
- Explain aspect only when it changes the practical choice; do not make learners memorize unreviewed slash pairs.
- Do not accept an aspect partner as a typed answer unless the prompt truly permits it.
- Keep reflexive and non-reflexive meanings separate, even when they share a spelling base.
- Preserve `się` in display, search identity, audio and answer expectations.

## 8. CEFR and production policy

| Status | Appropriate use |
|---|---|
| A1 recognition | common single-frame verbs and reference contrasts |
| A1 production | deterministic direct/prepositional frames with concrete contexts |
| A2 recognition | common two-frame/reflexive/experiencer constructions |
| A2 production | controlled contexts after case foundations |
| B1 recognition | polysemy, register and less transparent multiple complements |
| B1 production | only high-frequency, reviewed patterns with natural closed prompts |

CEFR belongs to a meaning/pattern, not merely the lemma. A familiar A1 lemma may have a secondary B1 construction.

## 9. Examples and errors

Examples must be independently authored, short, natural, useful in life in Poland, and contain enough context to identify the intended pattern. Store Polish and English together; do not derive one from source prose. Mark the authoring/review history separately from evidence for the linguistic fact.

Use a common-error note only when all are true:

- the error is likely and pedagogically useful;
- the correct/incorrect contrast is deterministic;
- the wording does not teach an unnatural alternative by repetition;
- a competent reviewer has approved it.

Prefer positive guidance over exhaustive error catalogues.

## 10. Editorial acceptance checklist

Before a pattern is learner-facing, confirm:

1. lemma, `się` and aspect entity are correct;
2. the meaning boundary is explicit;
3. every complement has the correct role, question, preposition and full case ID;
4. the relationship is classified precisely enough not to present a constructional or means/method use as ordinary lexical government;
5. required/optional status is justified;
6. the Polish example is independently authored and natural;
7. the English gloss does not invite unintended Polish answers;
8. CEFR and recognition/production scope are appropriate;
9. activity prompts have a closed accepted set;
10. provenance contains locators rather than copied source text;
11. modern reference, native review and product-owner approval are recorded.

## 11. Pilot success criteria

The 30-verb pilot succeeds if learners can connect familiar case knowledge to high-value verbs without needing technical terminology, and if every production task can explain why one complement was expected. It does not succeed merely by publishing a static list of verb+case pairs.
