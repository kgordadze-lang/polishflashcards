# Priority 7 — Phase 2B Native Review Queue

**For:** a competent native Polish reviewer working on Po polsku editorial content
**Subject:** 30 lemmas, 34 meanings, 45 candidate patterns in
`editorial/verb-pattern-candidates.json`
**Everything here is a draft.** Nothing has been externally verified, natively reviewed or
approved. You do not need to read any implementation code to answer these questions.

## How to use this queue

Work top-down: Part A holds the questions where a wrong answer would change the *structure*
of a record, Part B holds Polish sentences that need your judgment as a native speaker,
Part C is the level/status pass, and Part D lists what is deliberately **not** in the corpus
so you can say whether anything important is missing.

Please do not sign off the corpus as a whole. Each question below is separable, and a
"no" on any of them is a useful outcome.

Notation used throughout: **Gen** Genitive, **Dat** Dative, **Acc** Accusative,
**Ins** Instrumental, **Loc** Locative, **Nom** Nominative.

---

## Part A — highest-risk structural questions

### NRQ-01 — `płacić`: is the Instrumental really a *method*, not an object?

The corpus gives `płacić` two patterns under one meaning:

- `płacić za` + Acc — what you pay for (`Ile płacę za wszystko?`)
- `płacić` + bare Ins — how you pay (`Płacę gotówką.`), classified internally as a
  **means/method** relation rather than ordinary government.

The classification exists so that Po polsku never tells a learner "`płacić` takes the
Instrumental" as if it were a fixed object. The proposed learner wording is:
*"To say how you pay, use the bare Instrumental: płacę kartą, płacę gotówką."*

1. Is that description accurate and natural?
2. Would a learner be misled into producing `*płacę kartą za` in contexts where a native
   would not?
3. Should the two slots ever be taught together (`płacę kartą za bilet`) at A2–B1, or does
   that overload the point?

### NRQ-02 — `czekać`: is a bare Genitive still current?

The 2011 research source lists **both** `czekać czego?` (bare Gen) and `czekać na co?`.
The contemporary reference lists only `na` + Acc for the nominal frame. Only `na` + Acc is
authored.

1. Is `czekać czegoś` still current in any register you would teach, or is it literary/dated?
2. If it survives, is it a separate *meaning* or the same meaning with an older frame?
3. Would omitting it entirely mislead a B1 learner reading contemporary texts?

### NRQ-03 — `być`: is the predicative scope drawn in the right place?

`być` has exactly **one** authored pattern: `być` + Ins for a role, profession or category
(`Jestem studentem pierwszego roku.`). The fixed `to jest` + Nom construction is
deliberately **not** modelled as a verb pattern; the record links to the Nominative grammar
topic as a contrast instead.

The contemporary reference lists three predicative frames for this sense: `być + JAKI`
(adjective), `być + CZYM` (Instrumental) and `być + z KOGO/CZEGO`.

1. Is "role, profession or category" the right boundary, or should it be narrower
   (profession/role only) or wider (including e.g. `jest problemem`)?
2. Adjectival predication (`Jestem zmęczony`) is out of the corpus because it is not a case
   complement in this model. Is that acceptable pedagogically, or does the learner need the
   Nom-adjective / Ins-noun contrast in one place?
3. Is the proposed wording *"For a role or profession after być, use the Instrumental"*
   accurate without being overbroad?

### NRQ-04 — `podobać się`: recognition-only, or productive at B1?

Modelled as a **subject–experiencer** construction: the thing liked is the grammatical
subject (Nom) and the person is Dat. It is currently **recognition-only**, i.e. the pilot
would not ask a learner to produce it.

1. Is the role description accurate — is the stimulus genuinely the subject?
2. Should this be productive at B1? It is extremely frequent, but the reversed mapping
   against English is exactly what makes learner production error-prone.
3. Proposed learner wording: *"The thing liked is the subject and the person is Dative:
   ten film podoba mi się."* Is `ten film podoba mi się` natural as a citation form, or
   should it be `podoba mi się ten film` (which is the far commoner word order)?
4. How should `podobać się` be contrasted with `lubić` for a learner without implying they
   are interchangeable?

### NRQ-05 — `zależeć komuś na czymś`: a construction with no subject

Two meanings are authored:

- `zależeć od` + Gen — "depend on" (`To zależy od pogody.`)
- `zależeć` + Dat + `na` + Loc — "it matters to someone" (`Zależy mi na tej pracy.`)

The second has a Dative experiencer but **no grammatical subject**, so it is typed as an
ordinary lexical frame with an `experiencer` role rather than as a subject–experiencer
construction. Proposed wording: *"No ordinary subject here: the person is Dative and the
thing takes na + Locative."*

1. Is the subjectless analysis right for the teaching purpose?
2. Are these genuinely two senses of one verb for a learner, or should they be presented as
   effectively two different verbs?
3. Is `na` + Loc the only frame worth teaching, or is `zależy mi, żeby …` equally core?

### NRQ-06 — `mówić`: meaning scope and an unrepresentable frame

One meaning ("say/tell") with two patterns: Dat + Acc, and Dat + `że` clause.

**`mówić po polsku` is not in the corpus at all.** `po polsku` is an adverbial, not a
preposition + inflected case, and the data model has no adverbial slot. Rather than force
it in, it was left out and the meaning scope explicitly excludes it.

1. Is one "tell content to a person" meaning correct for the two authored frames, or do the
   nominal and clause versions belong to different senses?
2. Is `mówić` + Dat + Acc genuinely productive at B1, or is `powiedzieć` so dominant in that
   frame that teaching the imperfective is misleading?
3. Is excluding the language-ability sense from a *verb-pattern* corpus acceptable, given
   that Po polsku already teaches `mówić po polsku` as a phrase elsewhere?

### NRQ-07 — `bać się`: one article, two meanings

The 2011 source treats the bare Gen frame and the `o` + Acc frame in a single article. The
contemporary reference numbers them as two senses. The corpus follows the contemporary
split: "be afraid of" (Gen, active-production) and "worry about" (`o` + Acc,
recognition-only).

1. Is the two-meaning split right for a learner, or is it one meaning with two frames?
2. Is `bać się o` frequent enough to be worth recognition at B1?
3. Does the Gen frame deserve production at B1, given that Gen plural forms
   (`pająków`, `burzy`) are the hard part?

### NRQ-08 — `tęsknić`: `za` + Ins only

The contemporary reference lists `tęsknić do KOGO/CZEGO` and `tęsknić za KIM/CZYM` as
alternants. Only `za` + Ins is authored.

1. Are they freely interchangeable, or is there a meaning, register or regional difference?
2. If `do` + Gen is common, should it be a second linked pattern or is teaching one enough?
3. Is `Tęsknię za tobą, kiedy wyjeżdżasz.` (reused from an existing B1 card) natural and
   unambiguous as the canonical example?

### NRQ-09 — `lubić` and the existing `nie lubię` card

Phase 0 flagged an inconsistency that this pilot inherits rather than fixes. The Accusative
grammar drill states "`Lubić` takes Accusative", while an existing A1 card presents
`nie lubię` with the example `Nie lubię ryb.` — a Genitive plural, because negation shifts
the direct object.

The corpus authors `lubić` + Acc and links the negation topic as a **contrast** reference,
but changes nothing in existing content.

1. Should the `lubić` pattern explanation itself mention the negation shift, or is leaving
   it to the negation lesson correct?
2. Does the existing `nie lubię` card need a note? (Recommending a change to existing
   content is in scope for your answer; making one is not in scope for this phase.)

### NRQ-10 — `szukać` / `znaleźć` are not an aspect pair

An existing card carries the free-text string `szukać (impf) / znaleźć (to find)`. **No**
aspect link was published anywhere in the corpus, and this pairing in particular was not
promoted: they are different verbs (activity vs. result), not aspect partners.

1. Confirm they must not be presented as an aspect pair.
2. `szukać` takes Gen and `znaleźć` takes Acc. Is teaching that contrast explicitly
   valuable, or does it invite over-generalisation?
3. Which true aspect partners among the pilot (`pomagać`/`pomóc`, `płacić`/`zapłacić`,
   `prosić`/`poprosić`, `pytać`/`zapytać`, `uczyć się`/`nauczyć się`,
   `dbać`/`zadbać`, `tęsknić`/`zatęsknić`) would you confirm, and does each partner share
   the same government?

### NRQ-11 — `prosić` and `pytać`: the Accusative person

Both verbs have a two-complement pattern with an **Accusative** person plus `o` +
Accusative topic (`proszę mamę o pomoc`, `pytam kolegę o adres`). Both are currently
active-production with a B1 production floor.

1. Confirm the person is Accusative in both (a Dative is the predicted learner error).
2. Is `prosić kogoś o coś` genuinely more useful to teach than the very frequent
   `poproszę o …` service formula the app already teaches?
3. For `pytać`, is `pytam o cenę` (topic only) natural without a named addressee?

### NRQ-12 — Are the two-meaning splits the right granularity?

Two lemmas carry two meanings with the **same** case, split on sense rather than form:

| Lemma | Meaning 1 | Meaning 2 | Case in both |
|---|---|---|---|
| `słuchać` | listen to (music) | obey (a person) | Gen |
| `zajmować się` | do as an activity/job | look after a person | Ins |

1. Is a two-meaning split useful to a learner here, or does one meaning with a usage note
   serve better? (The split costs nothing structurally but doubles what the learner sees.)
2. If you would merge either pair, say so explicitly — the same merge was applied to
   `wierzyć` in the correction pass and is described in NRQ-18.

### NRQ-13 — Reflexive identity

Six lemmas contain lexical `się`: `uczyć się`, `interesować się`, `bać się`,
`podobać się`, `zajmować się`, `opiekować się`. In this model `się` is part of the lemma's
identity, so `uczyć` and `uczyć się` are different entries with different meanings.

1. Confirm that for each of the six, `się` is lexically obligatory in the authored meaning.
2. `uczyć się` carries a distractor warning that dropping `się` changes the verb to
   "teach someone". Is that the most useful warning for that verb?
3. `zajmować się` and `opiekować się` both take a bare Instrumental for a cared-for person.
   How would you tell a learner when to use which?

### NRQ-14 — `czekać, aż …` is missing and cannot currently be encoded

The contemporary reference lists `czekać + aż ZDANIE` as a core frame. The data model's
clause types are limited to `że`, `czy`, `żeby` and interrogative; `aż` is not available,
and encoding it as `żeby` would be false. Nothing was authored.

1. How important is `Czekam, aż …` for an A2–B1 learner?
2. If it matters, this is a specification change request, not a content fix — please say so
   explicitly so it can be raised as one.

### NRQ-15 — All 24 error notes are *predicted*, not documented

Every error note in the corpus is typed `predicted-distractor`: a plausible wrong form
authored to be pedagogically useful. **None** is claimed to be a documented common error,
because no learner-error dataset was available.

Please mark each as: *realistic and worth preventing* / *unrealistic* / *realistic but the
guidance is wrong*. Examples of what is proposed:

| Verb | Predicted wrong form | Proposed guidance |
|---|---|---|
| `szukać` | `szukam kawiarnię` | Genitive, not Accusative: `szukam kawiarni` |
| `pomagać` | `pomagam mamę` | Dative: `pomagam mamie` |
| `czekać` | `czekam autobus` | Needs `na` + Accusative |
| `płacić` | `płacę z kartą` | No preposition: bare Instrumental `płacę kartą` |
| `interesować się` | `interesuję się o sport` | No preposition: `interesuję się sportem` |
| `tęsknić` | `tęsknię ciebie` | `za` + Instrumental: `tęsknię za tobą` |
| `być` | `jestem student` | Instrumental: `jestem studentem` |
| `ufać` | `ufam mojego brata` | Dative: `ufam mojemu bratu` |
| `podobać się` | `podobam ten film` | Thing liked is subject, person is Dative |
| `opiekować się` | `opiekuję się o babcię` | Bare Instrumental: `opiekuję się babcią` |
| `uczyć się` | `uczę polskiego` | Keep `się`; `uczyć` means teach someone else |
| `znaleźć` | `znaleźć mieszkania` | Accusative; only `szukać` uses Genitive |
| `prosić` | `proszę mamie o pomoc` | Person asked is Accusative |
| `pytać` | `pytam mamie o adres` | Person asked is Accusative |
| `rozmawiać` | `rozmawiam z pracy` | `z` + Ins is the person, `o` + Loc is the topic |
| `myśleć` | `myślę o wakacje` | Locative after `o` in this meaning |
| `wierzyć` | `nie wierzę go` | Dative: `nie wierzę mu` |
| `zajmować się` | `zajmuję się o marketing` | Bare Instrumental |
| `dziękować` | `dziękuję mamę za pomoc` | Dative recipient |
| `używać` | `używam tę aplikację` | Genitive |
| `potrzebować` | `potrzebuję zaświadczenie` | Genitive |
| `słuchać` | `słucham muzykę` | Genitive |
| `bać się` | `boję się pająki` | Genitive |

### NRQ-16 — Register and frequency have no corpus evidence

Every pattern is marked `register: neutral`, and priority is `core` (31) or `common` (14).
No corpus study was done, so these are editorial judgments.

Please flag any pattern that is **not** register-neutral, or whose priority is overstated.
In particular: `słuchać` (obey), `bać się o`, `zajmować się` (person), `wierzyć w`,
`zależeć komuś na czymś`.

### NRQ-17 — `lubić`: is excluding the separate people sense right?

The contemporary reference numbers a people sense (`lubić kogoś`) and a thing/activity sense
separately. The pilot authors **only** the thing/activity sense, whose `Składnia` licenses
both the Accusative object and the bare infinitive, and whose collocation range covers
consumables and abstract nouns as well as activity verbs. The meaning is keyed
`enjoy-thing-or-activity` and its scope statement explicitly excludes liking people.

1. Is one thing/activity meaning covering both `lubię kawę` and `lubię czytać` the right
   learner unit?
2. Does omitting `lubić kogoś` leave a real hole at A1, given that liking people is an
   extremely common beginner function?
3. If it should be added later, is it a separate *meaning* under the same lemma (the
   contemporary reference treats it that way), and would its case ever differ?

### NRQ-18 — `wierzyć`: both frames now sit under one trust sense

The corpus previously split `wierzyć komuś` and `wierzyć w coś` into two meanings, citing two
different numbered senses. That was corrected: the contemporary trust sense
("mieć zaufanie") itself lists **both** `KOMU/CZEMU` and `w KOGO/CO`, so both patterns now
sit under a single meaning keyed `have-trust`, with distinct learner wording per pattern:

- Dative — *"To believe a person, use the Dative: wierzę ci."* (active-production, A2→B1)
- `w` + Acc — *"For confidence in a person or thing, use w + Accusative: wierzę w tego
  lekarza."* (recognition-only, B1)

The scope statement explicitly excludes the separately numbered senses for accepting a
proposition as true, confidence in people in general or in oneself, ideological conviction
and religious faith. The earlier illustrative wording `wierzę w siebie` was removed because
it belongs to one of those excluded senses.

1. Is "having trust in a person or thing" a coherent single learner meaning for both frames,
   or does a learner need them separated regardless of how the dictionary numbers them?
2. Is `wierzę w tego lekarza` natural, and is it clearly the *trust* sense rather than the
   religious or ideological one?
3. Should `w` + Acc stay recognition-only, or is it productive at B1?
4. Is there a meaning difference between `wierzę mu` and `wierzę w niego` worth teaching
   explicitly?

### NRQ-19 — `myśleć`: opinion sense excluded, and no canonical example

The authored meaning is "direct attention to a topic" (`o` + Loc) and explicitly excludes the
opinion sense (`sądzić`, `uważać`). An earlier draft reused the existing card headword
`Co o tym myślisz?`; that reuse was **withdrawn**, because although it contains `o` + Locative
it realises the excluded opinion sense. The card is now referenced with
`purpose: contrast` instead.

The obvious structural alternative, the grammar drill sentence `Myślę o wakacjach.`, cannot
be reused: it lives in the drill's `full` field, which is outside the locked
repository-reuse provenance enum, and that enum was deliberately **not** widened.

1. Is excluding the opinion sense right, or should `Co o tym myślisz?` be taught as a second
   meaning of `myśleć` in this pilot?
2. Is draft B-22 below a good canonical example for the attention sense?
3. `myśleć nad` + Ins was not authored. Is the `o` / `nad` difference worth teaching at B1?

### NRQ-20 — `widzieć`: is the reused example unambiguous for visual perception?

The authored meaning is visual perception (seeing something with the eyes), sourced from the
contemporary sense whose `Składnia` gives `KOGO/CO`. The contemporary reference numbers a
**separate** encounter/meet sense, which the pilot does not author.

The reused example is `Widziałam wczoraj twoją siostrę.` (existing A2 card).

1. Read pragmatically, does that sentence report *seeing* someone or *running into / meeting*
   someone? If a native reader defaults to the encounter reading, it exemplifies the sense
   the corpus explicitly excludes.
2. Is it good enough for a research-phase record, or should it be replaced before any
   learner use?
3. If it should be replaced, what would you use instead? (No replacement was invented here:
   fabricating an original example would need an author authority that does not exist yet.)

### NRQ-21 — `prosić kogoś o coś`: the combined frame is not in the formal syntax list

This candidate is Accusative person + `o` + Accusative thing. Its provenance was rewritten to
stop overclaiming, and the corpus now records exactly this:

- the contemporary formal syntax list gives an `o CO` slot, and separately a bare `CO` object
  slot — it does **not** encode any combined `KOGO + o CO` frame;
- the collocation section attests human Accusative objects of the verb, but does **not**
  attest a personal object combined with an `o` phrase;
- the existing A2 restaurant template shows a polite request with an addressee.

So the two slots are separately attested and the combination is not. Compare `pytać`, where
`KOGO + o KOGO/CO` **is** a formally listed schema.

1. Is `proszę mamę o pomoc` fully natural and current?
2. Is the combined frame frequent enough to teach, or is the `o CO` version alone
   sufficient at A2–B1?
3. Is there any register or politeness constraint on naming the person explicitly?
4. Does the asymmetry with `pytać` reflect a real difference, or is it an artefact of how the
   dictionary happens to list the two entries?

### NRQ-22 — three one-slot patterns that no listed schema realises alone

For three patterns the contemporary syntax list always pairs the authored slot with a further
participant. The pilot teaches the slot alone anyway, because the shorter form is what a
learner meets first. Each has a sibling pattern carrying the full frame.

| Pattern | Listed schemas always add… | Authored as | Sibling with full frame |
|---|---|---|---|
| `pomagać` + Dat | `w czymś` / `przy czymś`, `czymś`, or an infinitive | `pomagam mamie` | `pomagać komuś w czymś` |
| `dziękować` + `za` + Acc | the Dative person | `dziękuję za pomoc` | `dziękować komuś za coś` |
| `pytać` + `o` + Acc | the Accusative person | `pytam o cenę` | `pytać kogoś o coś` |

For each: does the one-slot version stand on its own in natural everyday Polish, or does it
need the second participant to be idiomatic? A "no" on any row means that pattern should be
merged into its sibling rather than taught separately.

---

## Part B — draft Polish sentences awaiting a named author and your review

22 patterns currently have **no** example. Draft sentences were written for each, but they
were **not** placed in the corpus, because Phase 1 requires original examples to carry a
named human author and no such authority has been appointed for this phase.

These drafts were composed from the abstract grammatical fact only. None is copied from,
paraphrased from, or reconstructed out of any dictionary entry or example sentence.

Please judge each for naturalness, level, ambiguity and whether it isolates the target.

| # | Pattern | Draft Polish | Draft English | Target level |
|---:|---|---|---|---|
| B-01 | `pomagać` + Dat | Codziennie pomagam sąsiadce. | I help my neighbour every day. | A1–A2 |
| B-02 | `pomagać` + Dat + `w` + Loc | Brat pomaga mi w przeprowadzce. | My brother is helping me with the move. | A2 |
| B-03 | `słuchać` + Gen (obey) | Młodszy brat zawsze słucha rodziców. | My younger brother always does as his parents say. | B1 |
| B-04 | `prosić` + Acc + `o` + Acc | Zawsze proszę koleżankę o radę. | I always ask my colleague for advice. | B1 |
| B-05 | `rozmawiać` + `z` + Ins | Wieczorem rozmawiam z siostrą przez telefon. | In the evening I talk to my sister on the phone. | A2 |
| B-06 | `rozmawiać` + `o` + Loc | Na lekcji rozmawiamy o pogodzie. | In class we talk about the weather. | A2 |
| B-07 | `rozmawiać` + `z` + Ins + `o` + Loc | Rozmawiam z szefem o nowym projekcie. | I am talking to my boss about the new project. | B1 |
| B-08 | `bać się` + `o` + Acc | Rodzice boją się o dzieci w wielkim mieście. | Parents worry about their children in a big city. | B1 |
| B-09 | `mówić` + Dat + Acc | Mówię ci prawdę. | I am telling you the truth. | A2–B1 |
| B-10 | `mówić` + Dat + `że` | Mówię mamie, że wracam późno. | I am telling my mum that I will be back late. | B1 |
| B-11 | `pytać` + `o` + Acc | Turysta pyta o drogę na dworzec. | A tourist is asking the way to the station. | A2 |
| B-12 | `pytać` + Acc + `o` + Acc | Pytam kolegę o godzinę spotkania. | I am asking my colleague what time the meeting is. | B1 |
| B-13 | `podobać się` Nom + Dat | Podoba mi się nowa fryzura Ani. | I like Ania's new haircut. | A2 |
| B-14 | `ufać` + Dat | Ufam swojemu lekarzowi. | I trust my doctor. | B1 |
| B-15 | `wierzyć` + Dat | Wierzę ci, bo znam cię od lat. | I believe you, because I have known you for years. | B1 |
| B-16 | `wierzyć` + `w` + Acc | Wierzę w twój sukces. | I believe in your success. | B1 |
| B-17 | `zajmować się` + Ins (activity) | Zajmuję się księgowością w małej firmie. | I do the accounting in a small company. | B1 |
| B-18 | `zajmować się` + Ins (person) | W weekend zajmuję się wnukami. | At the weekend I look after my grandchildren. | B1 |
| B-19 | `opiekować się` + Ins | Opiekuję się babcią po operacji. | I am looking after my grandmother after her operation. | B1 |
| B-20 | `zależeć` + `od` + Gen | Cena biletu zależy od godziny. | The ticket price depends on the time. | B1 |
| B-21 | `zależeć` + Dat + `na` + Loc | Bardzo mi zależy na tej pracy. | I really want this job. | B1 |
| B-22 | `myśleć` + `o` + Loc | Myślę o wakacjach nad morzem. | I am thinking about a holiday by the sea. | A2 |

For each, please answer: natural? correct level? does it isolate the target frame? better
alternative?

### Reused existing sentences (23) also need your judgment

The other 23 examples are exact reuses of existing Po polsku card `ex` sentences, chosen
because they already demonstrate the target frame. They are not new Polish, but please
confirm each still isolates the pattern it is attached to. The one worth a second look is:

- `widzieć` reuses `Widziałam wczoraj twoją siostrę.` — see NRQ-20, which asks whether it
  reads as perception or as an encounter.
- `dziękować` (Dat + `za` + Acc) reuses a B1 career card,
  `Dziękuję wszystkim za owocną współpracę.` — accurate, but is the vocabulary too high for
  a pattern whose recognition level is A2?

A 24th reuse was withdrawn during the correction pass: see NRQ-19.

---

## Part C — full pattern inventory for the level and status pass

Proposed CEFR (`recognition → production`) and teaching status. Please confirm or correct.
"rec only" means the pilot would never ask the learner to produce the form.

| Pattern key | Lemma / meaning | Frame | Rel | CEFR | Status | Example |
|---|---|---|---|---|---|---|
| `genitive-target` | `szukać` / seek | Gen (target) | lex | A1→A1 | active | reuse |
| `dative-recipient` | `pomagać` / assist | Dat (recipient) | lex | A1→A1 | active | **none** |
| `dative-recipient-w-locative-area` | `pomagać` / assist | Dat (recipient) + w + Loc (topic) | lex | A2→A2 | active | **none** |
| `genitive-target` | `słuchać` / listen-to | Gen (target) | lex | A1→A1 | active | reuse |
| `genitive-object` | `słuchać` / obey | Gen (object) | lex | B1 rec only | recog | **none** |
| `na-accusative-target` | `czekać` / wait-for | na + Acc (target) | lex | A1→A1 | active | reuse |
| `genitive-object` | `potrzebować` / need | Gen (object) | lex | A1→A2 | active | reuse |
| `genitive-subject-matter` | `uczyć się` / study | Gen (content) | lex | A1→A2 | active | reuse |
| `infinitive-skill` | `uczyć się` / study | infinitive (content) | lex | A2→B1 | active | reuse |
| `za-accusative-reason` | `dziękować` / thank | za + Acc (topic) | lex | A1→A1 | active | reuse |
| `dative-recipient-za-accusative` | `dziękować` / thank | Dat (recipient) + za + Acc (topic) | lex | A2→B1 | active | reuse |
| `za-accusative-goods` | `płacić` / pay | za + Acc (target) | lex | A1→A2 | active | reuse |
| `instrumental-method` | `płacić` / pay | Ins (means) | **means** | A1→A1 | active | reuse |
| `genitive-object` | `używać` / use | Gen (object) | lex | A2→A2 | active | reuse |
| `o-accusative-request` | `prosić` / request | o + Acc (target) | lex | A1→A2 | active | reuse |
| `accusative-person-o-accusative-thing` | `prosić` / request | Acc (interlocutor) + o + Acc (target) | lex | A2→B1 | active | **none** |
| `instrumental-topic` | `interesować się` / be-interested-in | Ins (topic) | lex | A2→A2 | active | reuse |
| `o-accusative-target` | `dbać` / take-care-of | o + Acc (target) | lex | B1→B1 | active | reuse |
| `za-instrumental-target` | `tęsknić` / miss | za + Ins (target) | lex | B1→B1 | active | reuse |
| `z-instrumental-interlocutor` | `rozmawiać` / talk-with | z + Ins (interlocutor) | lex | A2→A2 | active | **none** |
| `o-locative-topic` | `rozmawiać` / talk-with | o + Loc (topic) | lex | A2→A2 | active | **none** |
| `z-instrumental-o-locative` | `rozmawiać` / talk-with | z + Ins + o + Loc | lex | B1→B1 | active | **none** |
| `genitive-stimulus` | `bać się` / be-afraid-of | Gen (target) | lex | A2→B1 | active | reuse |
| `o-accusative-concern` | `bać się` / worry-about | o + Acc (topic) | lex | B1 rec only | recog | **none** |
| `instrumental-predicate` | `być` / predicate-role | Ins (predicate) | **constr** | A1→A2 | active | reuse |
| `accusative-object` | `znać` / be-acquainted-with | Acc (object) | lex | A1→A1 | active | reuse |
| `accusative-object` | `lubić` / enjoy-thing-or-activity | Acc (object) | lex | A1→A1 | active | reuse |
| `infinitive-activity` | `lubić` / enjoy-thing-or-activity | infinitive (content) | lex | A1→A1 | active | reuse |
| `dative-recipient-accusative-content` | `mówić` / tell-content | Dat + Acc (content) | lex | A2→B1 | active | **none** |
| `dative-recipient-ze-clause` | `mówić` / tell-content | Dat + clause `że` | lex | A2→B1 | active | **none** |
| `o-accusative-topic` | `pytać` / ask-for-information | o + Acc (topic) | lex | A2→A2 | active | **none** |
| `accusative-person-o-accusative-topic` | `pytać` / ask-for-information | Acc (interlocutor) + o + Acc | lex | A2→B1 | active | **none** |
| `accusative-object` | `widzieć` / perceive-visually | Acc (object) | lex | A1→A1 | active | reuse |
| `accusative-object` | `mieć` / possess | Acc (object) | lex | A1→A1 | active | reuse |
| `o-locative-topic` | `myśleć` / think-about | o + Loc (topic) | lex | A2→A2 | active | **none** |
| `accusative-object` | `znaleźć` / find | Acc (object) | lex | A2→B1 | active | reuse |
| `nominative-stimulus-dative-experiencer` | `podobać się` / appeal-to | Nom (subject) + Dat (experiencer) | **subj-exp** | A2 rec only | recog | **none** |
| `dative-object` | `ufać` / trust | Dat (object) | lex | B1→B1 | active | **none** |
| `dative-object` | `wierzyć` / have-trust | Dat (object) | lex | A2→B1 | active | **none** |
| `w-accusative-target` | `wierzyć` / have-trust | w + Acc (target) | lex | B1 rec only | recog | **none** |
| `instrumental-topic` | `zajmować się` / occupation-activity | Ins (topic) | lex | A2→B1 | active | **none** |
| `instrumental-object` | `zajmować się` / look-after-person | Ins (object) | lex | B1 rec only | recog | **none** |
| `instrumental-object` | `opiekować się` / care-for | Ins (object) | lex | B1→B1 | active | **none** |
| `od-genitive-source` | `zależeć` / depend-on | od + Gen (topic) | lex | B1→B1 | active | **none** |
| `dative-experiencer-na-locative` | `zależeć` / matter-to-someone | Dat (experiencer) + na + Loc | lex | B1 rec only | recog | **none** |

### Proposed activity use — for your opinion only, not stored as data

No activity is enabled anywhere in the corpus (all 45 allowlists are empty, which is the
only valid value before approval). If you and the product owner later approve these records,
the drafting recommendation is:

- **reference + search** for all 45;
- **grammar-choose** for the 39 active-production patterns with a complete example;
- **grammar-build** only for single-complement A1–A2 patterns with a fixed case
  (`szukać`, `pomagać` Dat, `słuchać`, `czekać`, `potrzebować`, `interesować się`,
  `znać`, `lubić` Acc, `widzieć`, `mieć`, `płacić` Ins);
- **type-it** for none of them in this pilot — no prompt yet has a demonstrably closed
  answer set;
- **listening** only after each exact sentence passes your review and separate audio QA;
- **mixed-quiz / case-mix / conversation** deferred to a separate design.

Please say whether the grammar-build shortlist is safe.

---

## Part D — what is deliberately absent

Say whether any of these omissions would harm the pilot.

| Not authored | Reason |
|---|---|
| `czekać czegoś` (bare Gen) | present in 2011 source, absent from contemporary reference — NRQ-02 |
| `czekać, aż …` | clause type not available in the model — NRQ-14 |
| `szukać kogoś/coś` (Acc), `szukać za czymś` | flagged as questionable by the contemporary reference |
| `mówić po polsku` | adverbial, not a case complement — NRQ-06 |
| `to jest` + Nom | Phase 1 boundary decision; linked as a grammar contrast instead |
| `być` + adjective, `być z kogoś/czegoś` | out of pilot scope — NRQ-03 |
| `tęsknić do` + Gen | alternant not authored — NRQ-08 |
| `myśleć nad` + Ins | deliberation-focused alternant, not authored |
| `potrzebować` + infinitive | marginal in neutral contemporary Polish |
| `uczyć się` + `o`/`u`/`od`/`do` frames | out of pilot scope |
| `pomagać` + infinitive, `pomagać komuś czymś` | out of pilot scope |
| `prosić` + `żeby` clause, direct speech, bare Gen | out of pilot scope |
| `dziękować` + `że` clause, + Ins, direct speech | out of pilot scope |
| `bać się` + infinitive / `że` clause | out of pilot scope |
| `lubić` + `jak`/`żeby` clause | out of pilot scope |
| `dbać` + `żeby` clause | out of pilot scope |
| `lubić kogoś` (the people sense) | separately numbered contemporary sense, not authored — NRQ-17 |
| `wierzyć` — the truth/existence, self-confidence, ideological and religious senses | separately numbered contemporary senses; only the trust sense is authored — NRQ-18 |
| `myśleć` opinion sense (`Co o tym myślisz?`) and `myśleć nad` + Ins | out of the authored meaning scope — NRQ-19 |
| `mieć` — 18 of 19 contemporary senses | pilot teaches possession only |
| `być` — 7 of 8 contemporary senses | pilot teaches the role predicate only |
| Every aspect partner link | requires review on both sides before it may exist — NRQ-10 |
| Any `documented-common-error` | no learner-error evidence available — NRQ-15 |
| Any audio | no example is audio-eligible before approval |

---

## What this queue is not asking for

Please do **not** approve the corpus, the CEFR scheme, or the activity plan as a block. The
questions above are separable and each has a useful "no". After your pass, the records
still need a named external verifier and a product-approval authority before anything can
reach a learner.
