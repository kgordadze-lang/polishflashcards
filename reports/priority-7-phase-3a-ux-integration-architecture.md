# Priority 7 — Phase 3A UX and Integration Architecture

**Phase:** 3A design only. Nothing here is implemented, and nothing here is approved for release.
**Depends on:** [`priority-7-phase-3a-current-surface-audit.md`](priority-7-phase-3a-current-surface-audit.md)
(all repository evidence), the locked Phase 1 specifications, and the Phase 2A tooling contracts.

**Learner promise, restated from Phase 1:** *"For this meaning of this verb, what comes next in
Polish?"* This document decides how the app asks and answers that question.

---

## 1. The decision

> **Recommended architecture: a hybrid, with a dedicated Verb Patterns surface as the home of the
> content, reached through the existing Grammar category; case lessons and vocabulary cards act as
> doorways into it, never as second copies of it.**

Concretely, three tiers with strictly decreasing weight:

| Tier | Surface | Weight | Slice |
|---|---|---|---|
| **1 — home** | A `Verb patterns` **level in the Grammar category** whose canonical entry is the **A–Z verb index**; opening a verb shows that one lemma's complete hierarchy (`lemma → meaning → pattern`). Case is a **filter over that index**, never a second copy of it | owns the content | 3B |
| **2 — doorways** | Each case topic deep-links into the **case-filtered state of the verb index**; each pattern links back to its case lesson | one link each way | 3C |
| **3 — pointer** | Vocabulary card back gets an optional single `Pattern` row, resolved through a **narrowly eligible** reverse `contentRef` index (§8) | one line | 3C |

Activities come later, gated, and only where `activityEligibility` says so (§9).

### 1.0 Canonical ownership — the amendment that governs everything below

> **`Verb Patterns → lemma → meaning → pattern` is the one canonical ownership hierarchy.
> Every pattern is owned by exactly one lemma entry and is rendered in full in exactly one place.
> Case-based discovery is a *view* — a filter, a browse mode, or a deep-linked filtered state — and
> never an owner.**

The earlier draft of this document proposed seven case-grouped *sets* alongside an A–Z index as the
Tier 1 organization. That was self-contradictory: it identified the missing capability as a
lemma-first index and then made case-grouped sets the primary containers. Case sets as containers
also reintroduce, inside the new surface, exactly the fragmentation §2.1 rejects in the existing
Grammar lessons — `rozmawiać` would appear in an Instrumental set *and* a Locative set, `płacić` in
an Accusative set *and* an Instrumental set, `zależeć` in a Genitive set *and* two more.

The corrected model:

| Concept | Status | Consequence |
|---|---|---|
| Verb index (A–Z) | **canonical, default** | the surface opens here; every lemma appears exactly once |
| Lemma entry | **canonical owner** | the only place a pattern is rendered in full |
| Case filter | **derived view** | shows *rows that point into* lemma entries; renders a row summary, never an owning copy |
| Case deep-link | **derived view, addressable** | a case lesson opens the index pre-filtered; the learner is in the same index, not a different place |

A case filter row is a **pointer with a summary**, and it says so structurally: it shows
`lemma — meaning · chip` and navigates to the lemma entry. It never shows the explanation, the
example, or the links, because those belong to the owner.

**The one-lemma-one-entry invariant** is what makes this scale, and it is testable: for every lemma
id in the runtime document, the number of lemma entries rendered anywhere in the surface is exactly
one.

### 1.1 Why this, in one paragraph

The learner's actual problem — *"which verbs require which case"* — is a **lookup problem before it
is a practice problem**, and the thing the learner holds in their head when they hit it is **the
verb**, not the case. Po polsku already teaches all seven cases well and already names verb triggers
inside each case lesson, but it does so in prose, split across seven silos, with no lemma-first entry
point (audit §3.2, and
[`priority-7-current-verb-case-inventory.md`](priority-7-current-verb-case-inventory.md) §5–6).
The missing thing is a **verb index**, not another lesson and not an eighth through fourteenth case
container. An index needs a home of its own. The app already knows how to give a synthesized set of
content a home — that is exactly what `Type it` and `Listening` are (audit §2.1) — and a level
carrying `group:"grammar"` lands in the Grammar tab with no engine edit, which is precisely where a
learner asking a case question already goes.

### 1.2 What "dedicated surface" does *not* mean here

It does not mean a parallel mini-app. The recommended surface:

- lives inside `index.html`, in `PP_LEVELS`, behind the same `#home` tabs and the same `.topic` rows;
- uses the existing `.screen` / `.sbar` / `.drill-card` / `.chip` primitives and the existing
  `.usage-badge` chip idiom;
- routes through `show()` / `showScreen()` and the existing history and scroll contracts;
- uses `ppFocusActivityTarget`, `ppSetActivityStatus`, `ppScreenEntryTarget` unchanged;
- writes nothing, persists nothing, and adds no new storage key.

The only genuinely new things are one screen, one loader, and one chip component.

---

## 2. Alternatives considered and rejected

### 2.1 Rejected — *"Priority 7 is part of Grammar"* (patterns inside the seven case topics)

**Shape:** append pattern material to each case topic's `teach[]`, and generate pattern drills into
each case topic's `drills[]`.

**Why rejected:**

1. **Wrong primary key.** A learner asks *"what case does `szukać` take?"*, a lemma-first question.
   This shape can only answer *"which verbs take Genitive?"*, and only for a learner who already
   guessed the case. It optimizes the direction the learner does not have.
2. **Fragmentation is guaranteed for multi-case lemmas.** `rozmawiać` has three patterns across
   Instrumental and Locative; `płacić` spans Accusative (`za`) and Instrumental; `zależeć` spans
   Genitive (`od`) and Dative+Locative. Under this shape each lemma is shredded across two or three
   case topics and the learner can never see the contrast that makes it learnable. The Phase 0
   audit already recorded `rozmawiać z / o` as "correct but split across case silos"
   ([`priority-7-current-verb-case-inventory.md`](priority-7-current-verb-case-inventory.md) §6).
3. **It duplicates existing Grammar content.** The Genitive topic already says *"'Szukać' (to look
   for) always takes Genitive"* in drill `grammar-cases-genitive-014`. Adding a pattern block saying
   the same thing in the same lesson is duplication that will drift.
4. **`teach` and `drills` are `innerHTML`-rendered authored markup** (audit §3.3). Feeding generated
   JSON through `gRenderTeach()` is a categorical mismatch, not a styling problem.
5. **It would change existing topic counts and drill totals**, which the test plan lists as a stop
   condition ([`priority-7-test-plan.md`](priority-7-test-plan.md) baseline).

### 2.2 Rejected as *primary* — *"Priority 7 is part of vocabulary/verb cards"*

**Shape:** every verb card grows a pattern block; there is no separate surface.

**Why rejected as primary (but kept as tier 3):**

1. **The card schema is closed.** `CARD_FIELDS` in
   [`validate_content.py:812`](../validate_content.py#L812) admits no `patternRef`. Making cards the
   host means changing the content schema, the validator, the frozen content baselines and the
   generated pages — for a pilot that Phase 1 explicitly designed to be *one-way and non-invasive*.
2. **Coverage is partial and asymmetric.** Only 35 `card` refs exist across 45 patterns, and the
   Phase 0 audit found `potrzebować` has no strict lemma card at all (it lives in an A2 template and
   scenarios). Card-hosted patterns would be silently absent for exactly the verbs whose government
   is hardest.
3. **Cards are not meanings.** `słuchać`, `bać się`, `zajmować się` and `zależeć` each have two
   canonical meanings with different government. One card cannot host two meanings without becoming
   a small page — at which point it *is* the dedicated surface, just in the wrong place.
4. **The card back is already full.** Eyebrow, meaning, usage chips, hint, usage note, aspect pair,
   variants, YouTube link, example, two feedback buttons (audit §4.2). A three-line pattern block is
   the item that breaks the card's vertical budget at 320px.
5. **Discovery is backwards.** A learner has to already be studying that exact card, in that exact
   topic, to meet the pattern. Nothing answers *"show me all Dative verbs"*.

### 2.3 Rejected — a standalone Verb Patterns *screen with its own top-level tab*

**Shape:** a fourth category tab beside Vocabulary / Grammar / More.

**Why rejected:** `CATEGORIES` is a three-entry constant sized for a phone
([`index.html:2402`](../index.html#L2402)); `.cat-seg` is a flex row of three at 320px and a fourth
label ("Verb patterns") would not fit without shrinking the type or wrapping the tab — and
[`tests/test_phase3_closeout.js`](../tests/test_phase3_closeout.js) already pins the tab's wrapping
and size contract (`C1 the label size was not reduced`, `C1 the tab still shares the track
equally`). A fourth tab also asserts that verb patterns are a peer of *all of grammar*, which
overstates a 30-verb pilot. The Grammar category is the correct parent.

### 2.4 Rejected — generated static pattern pages as the primary surface

**Shape:** `build_pages.py` emits `/verbs/szukac/` etc.

**Why rejected for the pilot:** `build_pages.py` reads only `data-grammar.js` and `data-b1.js`
(audit §10); the sitemap and the service-worker `GENERATED_PAGE_ASSETS` are exact inventories that
would each need to grow by ~30 entries; and
[`priority-7-existing-content-integration-map.md`](priority-7-existing-content-integration-map.md) §5
already ruled static pages "explicitly out of the pilot unless separately scoped". Publishing 30
public pages is also a *public claim* about linguistic content that is currently `research`. This
stays out until after a release gate, and then only under its own scope.

### 2.5 Rejected — reusing `#grammar`'s teach/drill machinery for the reference view

Tempting, because `gRenderTeach` already renders headline + sub + points + table + explain + note +
examples, which maps onto a pattern almost field for field. Rejected because:

- it is `innerHTML` over its inputs (audit §3.3), and runtime JSON must never be parsed as markup;
- the flip-to-reveal metaphor is wrong for a lookup — a learner scanning for "which case?" should
  not have to flip a card to find out;
- `startGrammar` assumes `topic.teach` **and** `topic.drills`, so a reference-only topic would need
  a fake empty drill set, and `gStartPractice` would then run an empty round;
- it would entangle pattern reference with Grammar's scoring and requeue state for no benefit.

A new screen that *reuses the CSS primitives and the accessibility helpers* costs less risk than
overloading a scored activity.

---

## 3. Information hierarchy

### 3.1 The canonical descent

```
Verb patterns (level, Grammar category)
└── VERB INDEX  (A–Z, the default and canonical entry; every lemma exactly once)
    └── lemma        szukać                                  (display lemma, aspect, się intact)
        └── meaning  "look for / search for"                 (glossesEn, joined)
            └── pattern   kogo? czego? · Genitive            (complements → chips)
                ├── explanation   learnerExplanationEn        (one sentence)
                ├── example       pl + en (+ audio, later)
                └── links         case lesson · supporting card
```

Three levels of ownership — **lemma → meaning → pattern** — reached from one index, with explanation
and example nested under the pattern. Nothing is more than two taps from the Grammar tab.

**The case filter is a sibling view of the index, not a level in this tree:**

```
Verb patterns
├── VERB INDEX  (A–Z)              ← canonical, default
└── filter: [All] [Gen] [Dat] [Acc] [Instr] [Loc] [Nom]
        └── the same index, showing only lemmas that have a matching pattern,
            each row summarised by the matching pattern, linking INTO the lemma entry
```

Filtering changes **which rows are listed and how they are summarised**. It never changes where a
pattern lives, and it never renders a pattern's explanation, example or links. A learner who taps a
filtered row lands on the lemma entry — the same entry they would reach from A–Z — scrolled to the
matching meaning.

### 3.1a How lemma-first handles the four hard shapes

These are the cases the case-grouped model handled badly and the lemma-first model handles by
construction.

**(a) One lemma with several cases** — the model's core win. `rozmawiać` has one meaning with three
patterns spanning Instrumental and Locative. Under lemma-first it is **one entry** showing all three
in ascending complexity, so the contrast *is* the layout. Under case grouping it was two rows in two
containers with no way to see them together. Same for `płacić` (Accusative `za` + Instrumental
method) and `zależeć` (Genitive `od` in one meaning, Dative + Locative in another).

In the case filter, such a lemma appears once **per matching pattern**, and each row states which
pattern matched:

```
 filter: Narzędnik (Instrumental)
 ─────────────────────────────────────────────────────────
  rozmawiać   talk / have a conversation
              z kim? z czym? · Instrumental              →
 ─────────────────────────────────────────────────────────
  płacić      pay — how you pay
              kim? czym? · Instrumental                  →
 ─────────────────────────────────────────────────────────
```

A repeated lemma in a filtered list is a *pointer repeated*, not content duplicated — the row is
five lines of summary and the entry is unchanged. The learner is told so implicitly by the fact that
both rows land in the same place.

**(b) Multi-complement patterns** (9 of 45). A pattern with two complements is owned by its lemma and
appears **whole**, once. In a case filter it appears under **each** case it contains — `pomagać
komuś w czymś` matches both the Dative filter and the Locative filter — and the row **highlights the
matching chip and dims neither**: both chips are shown, in order, with the matching one carrying the
filter's own emphasis. Showing only the matching chip would teach half a frame, which is the exact
failure mode a case-owned model produces.

```
 filter: Miejscownik (Locative)
  pomagać     help — and what you help with
              komu? czemu? · Dative  +  ▸w czym? · Locative◂   →
```

**(c) Infinitive complements** (2 of 45: `uczyć się` + infinitive, `lubić` + infinitive). These have
**no case at all**, and this is precisely why case cannot own the hierarchy: under case grouping
they would have no container and would silently vanish. Under lemma-first they sit in their lemma
entry as ordinary sibling patterns, and their chip carries a verb-shaped token instead of a case:

```
  lubić      like / enjoy
             ╭──────────────────────╮   ╭──────────────────────╮
             │ kogo? co? ·Accusative│   │ + verb (bezokolicznik)│
             ╰──────────────────────╯   ╰──────────────────────╯
                the thing you like          the activity you like
```

The case filter offers an explicit **`No case (verb / clause)`** option so these are discoverable
rather than merely not-excluded. That option exists *because* infinitive and clause complements
exist, and its label is the honest description of what unites them.

**(d) Clause complements** (1 of 45: `mówić komuś, że …`). Same principle: the clause token renders
as `+ że …` (or `+ czy …` / `+ żeby …` per `clauseKind`) and the pattern is a sibling of
`mówić komuś coś` inside the one `mówić` entry, so the learner sees the nominal frame and the clause
frame together:

```
  mówić      say / tell
             komu? czemu? · Dative  +  kogo? co? · Accusative
             komu? czemu? · Dative  +  + że …
```

A mixed pattern — one cased complement plus one clause — appears in the Dative filter (it has a
Dative) **and** shows its clause token in the row, so the filter never implies the clause is a case.

### 3.1b What this costs, stated honestly

Lemma-first makes *"which verbs take the Genitive?"* one interaction slower than a dedicated Genitive
container would: the learner must open the filter rather than tap a tile. That is the deliberate
trade. It buys the one-lemma-one-entry invariant, correct handling of infinitive and clause
complements, and no fragmentation of multi-case lemmas — and the filter is still reachable in one tap
from the surface and in one tap from the end of every case lesson (§7).

### 3.2 Resolution rules for every branch case

These are the design's fail-closed answers. Each is stated as a rule, then the reason.

| Situation | Learner sees | Reason |
|---|---|---|
| **One lemma, multiple meanings** (`słuchać`, `bać się`, `zajmować się`, `zależeć`) | The lemma card lists each meaning as its own labelled block, in `glossesEn` order, each with its own pattern(s). A short lead-in — *"`słuchać` has two meanings, and they behave differently."* — precedes them. | Phase 1: *"Teach meaning before case."* The learner must know which sense is at issue before a form is selectable. |
| **One meaning, multiple patterns** (10 meanings, up to 3) | Patterns are listed as sibling rows under the meaning, ordered by complement count then by CEFR recognition, so the simplest frame is first. No pattern is hidden behind a toggle. | `rozmawiać z` before `rozmawiać z … o …` mirrors how the frames are actually acquired. Hiding a sibling makes the learner think there is one answer. |
| **Two patterns, same case, different semantics** (`o` + Accusative appears in `prosić`, `pytać`, `dbać`, `bać się`) | Each pattern always carries its **meaning label above the chip**, never the chip alone. In a case-filtered row this is what separates the two `słuchać` rows and the four `o` + Accusative rows: `bać się — worry about`, not `bać się o + Accusative` alone. | The chip is not a unique key. Meaning is what distinguishes them, so meaning is never elided from a row. |
| **Multiple complements** (9 patterns) | Chips are rendered **in authored order, joined by a thin separator**, each carrying its own role label: `komu? czemu? · Dative — the person` then `w czym? · Locative — the area`. The pattern headline shows the whole frame on one line if it fits, wrapping chip-by-chip if not. | Phase 1: complement order is pedagogical, not word order. Roles come from the closed `role` enum, rendered through a fixed English role phrasebook (§5.4). |
| **Lexical `się`** (`uczyć się`, `bać się`, `interesować się`, `zajmować się`, `opiekować się`, `podobać się`) | `się` is part of the displayed lemma everywhere — headline, index, search text, any future audio or typed answer. It is never a suffix badge and never dropped in an A–Z sort key. | Phase 1: `się` is part of canonical lemma and identity. `bać się` and a hypothetical `bać` are different entities. |
| **Recognition CEFR ≠ production CEFR** (15 patterns) | Only the **recognition** level is ever shown as a level badge. A production gap is expressed as behaviour, not as a second number: the pattern simply has no production activity offered. | Two CEFR numbers on a chip is linguist-facing noise for an A1 learner. The distinction is real but belongs in eligibility, not in the badge. |
| **Recognition-only pattern** (6 patterns) | A `Understand this one` chip, using the existing `.usage-badge.u-recognition` style and the existing `"Recognition only"` label from [`pp-usage.js:45`](../pp-usage.js#L45). No practice affordance is rendered at all. | The app already has this concept and this chip for cards; reusing it means one idiom, not two. The absence of a practice button is the real signal; the chip explains it. |
| **Deferred pattern** | **Not rendered, not counted, not searchable, not linked.** It never reaches the runtime file — `project_runtime_nonrelease` admits only `active-production` and `recognition-only` ([`priority7_tooling.py:2427`](../priority7_tooling.py#L2427)). | The UI needs no deferred branch, because the projector already removed it. Designing a "deferred" state would invent a leak. |
| **No canonical example** (22 of 45 patterns today) | The pattern renders **without an example section** — no empty box, no placeholder, no generated sentence, no "example coming soon". The explanation and the chips stand alone. | An example is optional in the runtime shape (`examples` is omitted when empty). Fabricating or promising one is exactly the failure the review gates exist to prevent. |
| **Pattern not eligible for an activity** | No practice affordance for that activity is rendered. The learner sees reference content only. There is never a disabled-looking button, never a lock icon, never an upsell. | `activityEligibility` is an allowlist defaulting to false. A greyed control tells the learner something exists that they cannot have, which is both untrue and unhelpful. |
| **Runtime file missing / malformed** | The `Verb patterns` level is **not created at all**. Home shows five grammar levels, exactly as today. No error, no empty state, no broken tile. | Fail closed, and fail invisibly: this is a reference addition, not core function. §11 and the runtime contract report specify the loader behaviour. |

### 3.3 Editorial vocabulary that never reaches the learner

Forbidden in learner-facing copy, per Phase 1 §"Learner terminology and authoring": `relationType`
and all four of its values, `lexical-frame`, `constructional-frame`, `means-method`,
`subject-experiencer`, `complement`, `valency`, `government`, `accommodation`, `actant`,
`reviewState`, `research`, `approved`, `teachingStatus`, `activityEligibility`, `contentRef`,
`patternDataRevision`, and every `vp-*` identifier.

Also forbidden as a *display* string, even though it is a runtime field: `usage.priority`
(`core`/`common`/`limited`). It is an editorial teaching-priority judgement; the learner sees its
consequence (ordering) not its label.

The role enum (`subject`, `object`, `recipient`, `experiencer`, `predicate`, `content`, `topic`,
`interlocutor`, `means`, `target`) is **translated**, never printed (§5.4).

---

## 4. Pattern presentation

### 4.1 The anatomy

Every pattern renders as one block with a fixed five-part order. This order is also the
screen-reader reading order (§10.3).

```
1  HEADLINE     lemma + frame, Polish, large, lang="pl"
2  CHIP ROW     one chip per complement, in authored order
3  EXPLANATION  learnerExplanationEn — one sentence, English
4  EXAMPLE      Polish sentence + English translation      [omitted when absent]
5  LINKS        "Learn the Genitive" · "See the card"      [omitted when absent]
```

Level badge (`A1`/`A2`/`B1`) and the `Understand this one` chip, when present, sit on the headline
row, right-aligned, so they never break the chip row's rhythm.

### 4.1a Text wireframes — the three surface states

**State 1 — the verb index (default, canonical).** Opens here every time.

```
┌──────────────────────────────────────────────────────────────┐
│  ‹        Verb patterns                                🏠    │
├──────────────────────────────────────────────────────────────┤
│  Which case does this verb take?                             │
│  30 verbs · tap one to see its patterns                      │
│                                                              │
│  Case:  [ All ]  Gen  Dat  Acc  Instr  Loc  Nom  No case     │
├──────────────────────────────────────────────────────────────┤
│  B                                                           │
│    bać się        be afraid of · worry about        2 →      │
│    być            be (a role or job)                1 →      │
│  C                                                           │
│    czekać         wait for                          1 →      │
│  D                                                           │
│    dbać           take care of                      1 →      │
│    dziękować      thank                             2 →      │
│  …                                                           │
│  S                                                           │
│    słuchać        listen to · obey                  2 →      │
│    szukać         look for                          1 →      │
└──────────────────────────────────────────────────────────────┘
```

Each row: display lemma (`się` intact), meanings joined by `·`, a pattern count, one chevron. The
letter headings are the sticky grouping that keeps the list navigable as the corpus grows (§12).
**No chips in the index** — a chip here would assert one answer for a lemma that may have several.

**State 2 — a lemma entry (the canonical owner).** One entry per lemma, always.

```
┌──────────────────────────────────────────────────────────────┐
│  ‹        rozmawiać                                    🏠    │
├──────────────────────────────────────────────────────────────┤
│  rozmawiać                                     imperfective  │
│                                                              │
│  ▸ talk / have a conversation                                │
│                                                              │
│    rozmawiać  z  kim?                                  [A2]  │
│    ╭──────────────────────────────╮                          │
│    │ z kim? z czym? · Instrumental│  the person you talk to  │
│    ╰──────────────────────────────╯                          │
│    Use z + Instrumental for the person you are talking with. │
│    ── Rozmawiam z bratem.                                    │
│       I am talking with my brother.                          │
│    Learn the Instrumental →                                  │
│    ······················································    │
│    rozmawiać  o  czym?                                 [A2]  │
│    ╭──────────────────────────────╮                          │
│    │ o kim? o czym? · Locative    │  what you talk about     │
│    ╰──────────────────────────────╯                          │
│    Use o + Locative for the subject of the conversation.     │
│    Learn the Locative →                                      │
│    ······················································    │
│    rozmawiać  z  kimś  o  czymś                        [B1]  │
│    ╭────────────────────────────╮  ╭──────────────────────╮  │
│    │ z kim? z czym? ·Instrumental│+ │ o czym? · Locative  │  │
│    ╰────────────────────────────╯  ╰──────────────────────╯  │
│        the person you talk to        what you talk about     │
└──────────────────────────────────────────────────────────────┘
```

A lemma with two meanings puts each behind its own `▸` heading, in `glossesEn` order, with the
lead-in sentence from §3.2:

```
│  bać się                                       imperfective  │
│  bać się has two meanings, and they behave differently.      │
│                                                              │
│  ▸ be afraid of / fear                                       │
│    bać się  kogo? czego?                               [A2]  │
│    ╭──────────────────────────────╮                          │
│    │ kogo? czego? · Genitive      │  what you're afraid of   │
│    ╰──────────────────────────────╯                          │
│    ······················································    │
│  ▸ worry about / fear for            [Understand this one]   │
│    bać się  o  kogo?                                   [B1]  │
│    ╭──────────────────────────────╮                          │
│    │ o kogo? o co? · Accusative   │  who you worry about     │
│    ╰──────────────────────────────╯                          │
```

**State 3 — the case-filtered index (a view, reachable directly).** Same screen, same list, filtered
and row-summarised. Reached by tapping a filter chip, or deep-linked from a case lesson.

```
┌──────────────────────────────────────────────────────────────┐
│  ‹        Verb patterns · Dopełniacz (Genitive)         🏠   │
├──────────────────────────────────────────────────────────────┤
│  Case:  All  [ Gen ]  Dat  Acc  Instr  Loc  Nom  No case     │
│  7 verbs · 8 patterns take the Genitive                      │
├──────────────────────────────────────────────────────────────┤
│  bać się      be afraid of                                   │
│               kogo? czego? · Genitive                   →    │
│  ────────────────────────────────────────────────────────    │
│  potrzebować  need                                           │
│               kogo? czego? · Genitive                   →    │
│  ────────────────────────────────────────────────────────    │
│  słuchać      listen to                                      │
│               kogo? czego? · Genitive                   →    │
│  ────────────────────────────────────────────────────────    │
│  słuchać      obey            [Understand this one]          │
│               kogo? czego? · Genitive                   →    │
│  ────────────────────────────────────────────────────────    │
│  szukać       look for                                       │
│               kogo? czego? · Genitive                   →    │
│  ────────────────────────────────────────────────────────    │
│  uczyć się    learn / study                                  │
│               kogo? czego? · Genitive                   →    │
│  ────────────────────────────────────────────────────────    │
│  używać       use                                            │
│               kogo? czego? · Genitive                   →    │
│  ────────────────────────────────────────────────────────    │
│  zależeć      depend on                                      │
│               od kogo? od czego? · Genitive             →    │
└──────────────────────────────────────────────────────────────┘
```

`słuchać` appears twice because it has two Genitive patterns under two different meanings — and the
**meaning label is what distinguishes the rows**, which is the same rule §3.2 states for two patterns
sharing a case. Both arrows land on the one `słuchać` entry, at the relevant meaning. The count line
therefore reports verbs *and* patterns, because after filtering those two numbers differ and
reporting only one of them would misdescribe the list.

Note what a filtered row is **not**: no explanation, no example, no case-lesson link, no practice
affordance. Those exist once, in the lemma entry the arrow leads to.

**State 4 — loader unavailable.** The `Verb patterns` level is not created; home shows five grammar
levels exactly as today. There is no empty state to wireframe, deliberately (§3.2).

### 4.2 The eight required constructions, rendered

Copy below is **illustrative wording for the design**, not approved learner copy. Approved wording
is a review deliverable; what is locked here is the *shape*.

```
┌──────────────────────────────────────────────────────────────┐
│  szukać  +  kogo? czego?                               [A1]  │
│  ╭──────────────────────────────╮                            │
│  │ kogo? czego?  ·  Genitive    │   the thing you're after   │
│  ╰──────────────────────────────╯                            │
│  With this meaning szukać takes a Genitive object.           │
│  ── Szukam dobrej kawiarni.                                  │
│     I am looking for a good café.                            │
│  Learn the Genitive →                                        │
└──────────────────────────────────────────────────────────────┘
```

```
┌──────────────────────────────────────────────────────────────┐
│  pomagać  +  komu? czemu?                              [A1]  │
│  ╭──────────────────────────────╮                            │
│  │ komu? czemu?  ·  Dative      │   the person you help      │
│  ╰──────────────────────────────╯                            │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  pomagać  komuś  w  czymś                              [A2]  │
│  ╭─────────────────────────╮   ╭──────────────────────────╮  │
│  │ komu? czemu? · Dative   │ + │ w czym?  ·  Locative     │  │
│  ╰─────────────────────────╯   ╰──────────────────────────╯  │
│     the person you help          what you help them with     │
└──────────────────────────────────────────────────────────────┘
```

```
┌──────────────────────────────────────────────────────────────┐
│  rozmawiać  z  kim?                                    [A2]  │
│  ╭──────────────────────────────╮                            │
│  │ z kim? z czym? · Instrumental│   the person you talk to   │
│  ╰──────────────────────────────╯                            │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  rozmawiać  z  kimś  o  czymś                          [B1]  │
│  ╭────────────────────────────╮   ╭───────────────────────╮  │
│  │ z kim? z czym? ·Instrumental│ + │ o czym? · Locative   │  │
│  ╰────────────────────────────╯   ╰───────────────────────╯  │
│      the person you talk to           what you talk about    │
└──────────────────────────────────────────────────────────────┘
```

```
┌──────────────────────────────────────────────────────────────┐
│  prosić  kogoś  o  coś                                 [A2]  │
│  ╭──────────────────────────╮   ╭─────────────────────────╮  │
│  │ kogo? co? · Accusative   │ + │ o kogo? o co? ·Accusative│ │
│  ╰──────────────────────────╯   ╰─────────────────────────╯  │
│      the person you ask            what you ask for          │
│  Both slots are Accusative here — the roles are what tell    │
│  them apart.                                                 │
└──────────────────────────────────────────────────────────────┘
```

`prosić kogoś o coś` is the clearest argument for **always showing the role line**: the two chips
carry the same case name and nearly the same question, so the case alone carries no information.
The role phrases are the disambiguator.

```
┌──────────────────────────────────────────────────────────────┐
│  podobać się                        [A2]  [Understand this one]│
│  ╭─────────────────────────╮   ╭──────────────────────────╮  │
│  │ kto? co? · Nominative   │ + │ komu? czemu? · Dative    │  │
│  ╰─────────────────────────╯   ╰──────────────────────────╯  │
│      the thing that appeals        the person it appeals to  │
│  The thing you like is the subject; the person is Dative.    │
│  English puts them the other way round.                      │
└──────────────────────────────────────────────────────────────┘
```

```
┌──────────────────────────────────────────────────────────────┐
│  zależeć  komuś  na  czymś          [B1]  [Understand this one]│
│  ╭─────────────────────────╮   ╭──────────────────────────╮  │
│  │ komu? czemu? · Dative   │ + │ na czym?  ·  Locative    │  │
│  ╰─────────────────────────╯   ╰──────────────────────────╯  │
│      the person who cares          what they care about      │
└──────────────────────────────────────────────────────────────┘
```

### 4.3 Headline construction rule

The headline is generated, never authored, from `canonicalLemma` (or `displayLemma`) plus one
**placeholder token per complement**, in order:

| Complement | Headline token |
|---|---|
| direct `case` | the case's short pronoun placeholder — `kogo? czego?` (Gen), `komu? czemu?` (Dat), `kogo? co?` (Acc), `kim? czym?` (Instr), `kto? co?` (Nom) |
| `preposition-case` | the preposition, then the placeholder — `z kim?`, `o czym?`, `na co?` |
| `infinitive` | `+ bezokolicznik` rendered as `+ verb` in the English-facing headline |
| `clause` | `+ że …` / `+ czy …` / `+ żeby …` per `clauseKind` |

For two-complement patterns the headline may use the natural indefinite pronoun forms
(`pomagać komuś w czymś`) where the runtime data makes them derivable; where it does not, the
question form is used. **Nothing in the headline is authored per pattern**, so no headline can drift
from the structured data it summarizes. This is what keeps the surface honest as the corpus grows.

### 4.4 What is deliberately absent

- **No notation system.** No `V + Gen`, no `[NP-acc]`, no arrows-into-brackets, no colour-coded case
  key that must be learned before the content can be read.
- **No frequency or priority label.** `usage.priority` orders rows; it never prints.
- **No relation-type surface.** `płacić` + Instrumental reads *"To say **how** you pay, use
  Instrumental"* and never *"means-method"*; `być` + Instrumental reads *"For a role or job after
  `być`, use Instrumental"*; `podobać się` states the roles. This is the Phase 1 relationship-aware
  wording table applied as copy rules.
- **No `to jest` pattern.** Phase 1 declares fixed `to jest` + Nominative an out-of-corpus
  constructional contrast. The `być` entry may carry a link to the Nominative lesson, which already
  teaches `to jest / to są` ([`data-grammar.js:22`](../data-grammar.js#L22)). It must not render a
  generic `być + Nominative`.

---

## 5. Case UX — the core visual grammar

This is the part of the design that has to work, because it is the answer to the problem the user
originally identified.

### 5.1 The recommendation

> **One chip type, used everywhere, reading `question(s) · Full Case Name`, with the preposition
> bonded inside the chip when there is one, and a plain-English role phrase directly beneath it.**

That is the entire visual grammar. There is no second form, no abbreviation, no per-case colour.

```
   ╭───────────────────────────────╮
   │  kogo? czego?  ·  Genitive    │        ← the chip
   ╰───────────────────────────────╯
       the thing you're looking for         ← the role phrase
```

### 5.2 Why this shape

| Candidate | Verdict | Reason |
|---|---|---|
| Case label alone (`Genitive`) | **rejected as sole cue** | Requires the learner to already own the declension. Phase 1: abbreviations are never the only cue; full names alone are only half the bridge. |
| Case question chip alone (`kogo? czego?`) | **rejected as sole cue** | `kogo? czego?` (Gen) and `kogo? co?` (Acc) differ by one word. On a phone, at a glance, they are the same chip. Without the case name the learner cannot connect to the case lesson they already studied. |
| **Question + full case name in one chip** | **selected** | Each half repairs the other's failure. It is also exactly what the case topics already teach — the Genitive lesson opens with *"It answers **kogo? czego?**"* — so the chip is a callback, not a new notation. |
| Preposition + case chip | **selected, as the same chip** | Phase 1: prepositions are visually inseparable from their case. Bonding them inside one chip enforces that structurally; two adjacent chips would invite reading them as two slots. |
| Human-readable placeholders (`komuś`, `czymś`) | **selected, but in the headline only** | They read naturally in a frame (`pomagać komuś w czymś`) but are not diagnostic questions. Keeping them in the headline and the questions in the chip gives both without conflating them. |
| Short English explanation | **selected, as the role line** | The role line is the only thing that separates `prosić kogoś` from `prosić o coś`. It is required for multi-complement patterns and shown for all patterns for consistency. |
| Link to the case lesson | **selected, one per pattern, outbound** | §7. |
| Per-case colour coding | **rejected** | Seven hues is a legend the learner must memorize, fails WCAG 1.4.1 if it ever becomes the distinguishing channel, and collides with the app's existing semantic use of green/red for correct/wrong and amber for recognition-only. The design uses **one** tint (`--mint-bg` / `--mint-text`) for every case chip. |

### 5.3 The question derivation table

Derived centrally in the loader, never stored in the runtime file — matching Phase 1
(*"Questions derive for direct and prepositional complements"*) and confirmed by the corpus, which
contains **zero** `questionOverridePl` values (audit §12).

| Case id | Polish name | English name | Direct question | Prepositional form |
|---|---|---|---|---|
| `nominative` | Mianownik | Nominative | `kto? co?` | — (not a prepositional case here) |
| `genitive` | Dopełniacz | Genitive | `kogo? czego?` | `<prep> kogo? <prep> czego?` |
| `dative` | Celownik | Dative | `komu? czemu?` | `<prep> komu? <prep> czemu?` |
| `accusative` | Biernik | Accusative | `kogo? co?` | `<prep> kogo? <prep> co?` |
| `instrumental` | Narzędnik | Instrumental | `kim? czym?` | `<prep> kim? <prep> czym?` |
| `locative` | Miejscownik | Locative | — (never direct; rejected by the validator) | `<prep> kim? <prep> czym?` |
| `vocative` | Wołacz | Vocative | — | — |

Verification against the corpus: `w`+Loc → `w kim? w czym?`; `na`+Acc → `na kogo? na co?`;
`za`+Acc → `za kogo? za co?`; `o`+Acc → `o kogo? o co?`; `za`+Instr → `za kim? za czym?`;
`z`+Instr → `z kim? z czym?`; `o`+Loc → `o kim? o czym?`; `w`+Acc → `w kogo? w co?`;
`od`+Gen → `od kogo? od czego?`; `na`+Loc → `na kim? na czym?`. All ten combinations present in the
corpus derive to natural Polish.

**Vocative** carries a direct-address cue instead of a fabricated question, per Phase 1. It does not
occur in the pilot corpus, and the validator forbids it as a direct complement, so this is a
contract for future data only.

**Chip truncation rule.** When both question words do not fit, the chip drops the *second* question
word rather than the case name, and the full pair remains in the accessible name. The case name is
never truncated — it is the half that links to the lesson.

### 5.4 The role phrasebook

Ten closed roles, ten fixed English phrasings, parameterized by nothing. This is the only place a
role becomes words.

| Role | Default phrasing | Notes |
|---|---|---|
| `subject` | *the thing that does it* / *the thing that appeals* | context-sensitive only for `subject-experiencer`, where the second form is used |
| `object` | *what it applies to* | |
| `recipient` | *the person who receives it* | |
| `experiencer` | *the person it happens to* | |
| `predicate` | *the role or job* | `być` only |
| `content` | *what is learned / said / done* | |
| `topic` | *what it is about* | |
| `interlocutor` | *the person you talk to / ask* | |
| `means` | *how it is done* | `płacić` method |
| `target` | *what it is aimed at* | |

Where a phrasing would be misleading for a specific pattern, the pattern's own
`learnerExplanationEn` — which is authored, reviewed and frozen — carries the correction. The role
phrasebook is a default, never an override of reviewed copy.

### 5.5 `szukać → Genitive`, comprehensible without decoding JSON

The chain the design guarantees, from any of four entry points, with no identifiers and no schema
knowledge:

1. **Canonical:** Home → Grammar → **Verb patterns** → `szukać` in the A–Z index → the entry shows
   the chip `kogo? czego? · Genitive`.
2. **Case-first:** the same screen → tap the `Gen` filter → the `szukać` row summarises to
   `kogo? czego? · Genitive` → tap through to the same entry.
3. **Lesson-out:** Grammar Cases → Dopełniacz (Genitive) → *"Verbs that take the Genitive →"* →
   the index, deep-linked into the Genitive-filtered state → the same entry.
4. **Card-in:** Study `szukać` (`a1-first-verbs-020`) → card back shows
   `Pattern · kogo? czego? · Genitive` → the same entry.

All four converge on one place. That is the one-lemma-one-entry invariant doing its job: there is no
"the Genitive copy of `szukać`" for the four routes to disagree about.

---

## 6. Learner journeys

### J1 — "I keep getting `szukać` wrong" (lookup, A1) — **the primary journey**

Home → Grammar tab → `Verb patterns` → the index opens at A–Z → scan to `szukać` → tap → read the
chip. **Two taps to the index, one scan, one tap.** No filter needed, no case guessed, no practice,
no round, no score, no state written. This is the journey the whole architecture is optimised for,
because it is the one the learner actually arrives with.

### J2 — "Which verbs take the Dative?" (case-first, A2)

Home → Grammar → `Verb patterns` → tap the `Dat` filter chip → rows for every lemma with a Dative
complement, `pomagać` and `dziękować` first (both `core`, both A1 recognition), each summarised by
its matching pattern and each linking into its lemma entry. One extra tap versus J1, by design
(§3.1b).

### J3 — "I just learned the Genitive" (lesson-out, A1→A2)

Home → Grammar → Grammar Cases → Dopełniacz (Genitive) → finish the lesson → the completion screen
offers *"Verbs that take the Genitive →"* → the index **opens already in the Genitive-filtered
state**, with the filter chip visibly selected so the learner can see they are in a filtered view of
one list and can clear it. This is the **one** outbound link added to each case topic (§7), and it
is a deep link into a view, not a jump into a separate container.

### J4 — "What's the difference between these two `rozmawiać`s?" (contrast, B1)

Home → Grammar → `Verb patterns` → `rozmawiać` → the entry shows one meaning with **three sibling
patterns**, in ascending complexity, so the contrast is the layout itself. Under the rejected
case-grouped model this journey was impossible without visiting two containers and holding the first
in memory.

### J5 — "This card mentions a case" (card-in, any level)

Study A1 → First verbs → `szukać` → flip → the `Pattern` row on the back → tap → the lemma entry.
Returning uses the existing `ppScreenReturnTargets` invoker restoration, so focus lands back on the
row that was tapped.

### J6 — "I want to practise this" (deferred to 3D, and often refused)

From a lemma entry, a practice affordance appears **only** when that pattern's
`activityEligibility` contains an activity that is implemented. For today's corpus that is never.
The design's honest answer for the pilot is: J6 mostly does not exist, and that is correct.

---

## 7. Relationship to existing Grammar content

### 7.1 Direction of linking — the decision

> **Case lessons deep-link *out* into the case-filtered state of the verb index (one link per case
> topic). Verb patterns link *back* to case lessons (one link per pattern).
> No pattern content is copied into a case topic; no case explanation is copied into a pattern; and
> the outbound link opens a filtered *view* of the canonical index, never a case-owned container.**

Why this direction, both ways:

- **Case → patterns** is the pedagogically correct hand-off: the learner has just been taught the
  endings and the triggers, and the natural next question is *"so which verbs?"*. The link is placed
  at the **end** of the lesson, not at the start, so it never interrupts the lesson. It carries a
  case filter as *state*, which is why §3.1's rule that a filter is a view and not an owner is what
  makes this link safe: the learner arrives inside the one verb index, filtered, with the filter
  visible and clearable — not inside a Genitive-shaped duplicate of it.
- **Pattern → case** is the correct escape hatch: a learner who cannot form the Genitive is not
  helped by knowing `szukać` takes it. Every pattern therefore offers exactly one route to the case
  that would fix the actual gap.
- **One link each way** is what prevents fragmentation. Two surfaces that each hold half of the
  explanation is the failure mode; two surfaces that each hold a complete, non-overlapping thing and
  point at each other is not.

### 7.2 Duplication risk, assessed honestly

There is one genuine overlap: `grammar-cases-genitive-014` is a build drill whose explanation says
*"'Szukać' (to look for) always takes Genitive"*, and the `szukać` pattern says the same fact. This
is acceptable and should not be resolved by deleting either:

- the drill teaches it **in a Genitive lesson, as one of fourteen triggers, in passing**;
- the pattern states it **as the entry for that verb, retrievable by verb**.

The rule that keeps this from spreading: **a case topic may name a verb; it may not acquire a chip
row, a pattern list, or a generated pattern block.** The moment a case topic starts rendering
patterns, the two surfaces are duplicates and will drift.

The amended hierarchy strengthens this rule rather than restating it. Because the canonical owner is
the lemma entry and a case view is a filter over one index, **there is no artifact in the design that
a case topic could plausibly host.** A case topic cannot "contain" a pattern set, because no such
container exists anywhere — not in Grammar, and not inside Verb Patterns either. That is the
structural reason duplication cannot creep back in, and it is worth more than the prose rule.

### 7.3 Should Grammar drills eventually be generated from patterns?

**Not into the existing case topics.** Recommended instead, and only after a release gate:
a `Verb patterns` set may host its **own** choose drills, in its own set, scored session-only,
using the existing Grammar drill semantics but a separate queue.

Reasons:

1. `data-grammar.js` drills are hand-authored, frozen wording, and counted in the pinned baseline
   (353 drills). Generating drills into those topics changes a pinned total and mixes authored and
   generated content in one array with no way to tell them apart in a diff.
2. `gRenderDrill()` routes any non-`choose` type to build ([`index.html:3530`](../index.html#L3530)).
   A generated drill with an unexpected type would silently become a build drill.
   [`priority-7-existing-content-integration-map.md`](priority-7-existing-content-integration-map.md) §3
   already names this: *"Current 'anything other than choose behaves as build' is not a safe
   extension contract."*
3. `grammar-choose` requires "complete context, safe distractors, one intended answer" per the
   Activity Eligibility Specification. Auto-generating the other six cases as distractors is
   explicitly forbidden there. Distractors must be authored per item, which means drills are
   **authored content that happens to hang off a pattern**, not a projection of it.

---

## 8. Relationship to existing vocabulary cards

### 8.1 The decision

> **Yes — but as a single collapsed pointer line on the card back, resolved through a reverse index
> built from a *narrowly eligible subset* of runtime `contentRefs`, and shown as a chip only when
> both the reference and the meaning are unambiguous.**

The earlier draft said "resolved through the reverse `contentRef` index", which was too broad: it
would have treated every `contentRef` as a learner-facing teaching link. It is corrected below.

### 8.1a Which `contentRef` relation types are eligible — audit of the locked enums

No new relation type is invented. The locked model is `{kind, id, purpose}` with
`CONTENT_KINDS = {card, topic, drill, scenario}` and
`CONTENT_PURPOSES = {support, practice, context, contrast}`
([`priority7_tooling.py:94`](../priority7_tooling.py#L94),
[`priority-7-pattern-data-specification.md`](priority-7-pattern-data-specification.md) §11). Each is
assessed for one question only: *may this reference, on its own, justify printing a pattern chip on
that card as if the card instantiates the pattern?*

| `kind` | `purpose` | In corpus | Eligible for a **direct card chip**? | Why |
|---|---|---:|---|---|
| `card` | `support` | 29 | **YES — the only eligible combination** | This is the "current card" relation: the pattern names this card as the existing content that supports it. It is the only ref type that asserts the card and the pattern are about the same thing. |
| `card` | `contrast` | 6 | **NO — never** | A contrast ref means *"this card is instructive because it differs"*. Printing the pattern here would assert the opposite of what the ref says. |
| `card` | `practice` | 0 | **NO** | Not present, and semantically it would name a card used *for exercising* a pattern, not one that instantiates it. Ineligible by definition, not merely by absence. |
| `card` | `context` | 0 | **NO** | A contextual occurrence is not an instantiation claim. |
| `topic` | `support` / `contrast` | 44 / 5 | **NO** (not a card surface) | Used for the pattern → case-lesson back-link (§7), which is a different feature in a different direction. |
| `drill` | `practice` | 17 | **NO** (not a card surface) | Reserved for a future activity link; never a card-back claim. |
| `scenario` | any | 0 | **NO** | No scenario surface is in scope. |

**Eligibility rule, final: `kind === "card" && purpose === "support"`. Nothing else, in either
direction, ever produces a direct card-back pattern pointer.**

Two consequences worth stating plainly:

- `contrast` refs are **not merely deprioritised — they are invisible to this feature.** They do not
  contribute to the claim count, they cannot downgrade a chip to a doorway, and they cannot produce
  a doorway of their own. A card referenced *only* by contrast refs shows **nothing**.
- The four contrast-only cards in the corpus are therefore untouched, which includes
  `a1-food-basics-023` — the `nie lubię` card Phase 0 flagged as internally inconsistent (audit
  §4.3). The eligibility rule keeps a pattern away from the one card most likely to contradict it,
  and it does so by semantics rather than by a special case.

### 8.2 Where, and how much

On the **back face only**, immediately after `#pairLine` / `#variantLine` and before `#exampleBox`.
It reuses the `.pair-line` idiom exactly — uppercase key, value, wrapping, centred — because that is
the card's existing precedent for a compact labelled reference row.

```
   ASPECT PAIR      szukać / poszukać          ← existing #pairLine
   PATTERN          kogo? czego? · Genitive →  ← new, one line, tappable
```

One line. Never two. Never an expanded block on the card. The arrow opens the full lemma entry,
where all the space in the world is available.

**Front face: nothing.** The front is the recall surface; adding the answer's grammar to it changes
what the flashcard tests.

### 8.3 The resolution rule — two gates, three outcomes, fail-closed

Built once at startup, in memory, from the runtime document. Only refs passing §8.1a are indexed:
`ref.kind === "card" && ref.purpose === "support"` → `ref.id → pattern`.

**Gate 1 — reference ambiguity.** How many eligible patterns claim this card?

**Gate 2 — meaning ambiguity.** Even with exactly one claiming pattern, does the owning **lemma**
expose more than one meaning, or more than one pattern, in the runtime document?

| Gate 1 | Gate 2 | Card back shows |
|---|---|---|
| zero eligible refs | — | **nothing at all** |
| exactly one | lemma has 1 meaning **and** 1 pattern | **the chip**, inline, plus the link |
| exactly one | lemma has >1 meaning **or** >1 pattern | **neutral doorway** — `PATTERN  See how this verb is used →` |
| more than one | — | **neutral doorway** |

Gate 2 is the amendment's substance. Reference-count ambiguity and meaning ambiguity are **different
failure modes**, and only the first is visible in the ref counts. A chip is a claim that *this* is
how the verb works; it may only be printed when there is exactly one way the verb works in the
released corpus.

This is the direct answer to *"do not assume every verb card can safely inherit every pattern."*
A card that cannot unambiguously inherit one pattern inherits **none**; it inherits a doorway.

### 8.3a The rule modelled against the committed corpus

Applying both gates to the 45 patterns and 32 referenced cards yields, today:

| Outcome | Cards | Examples |
|---|---:|---|
| **Chip** | 15 | `a1-first-verbs-020` (`szukać`), `a1-first-verbs-021` (`czekać`), `a2-leisure-culture-002` (`interesować się`), `b1-relationships-018` (`ufać`), `a1-about-me-026` (`być`) |
| **Doorway** | 13 | `a1-first-verbs-022` (`pomagać`, 2 patterns), `a1-numbers-prices-015` (`płacić`, 2 patterns), `a2-restaurant-012` (`prosić`, claimed twice), `b1-character-emotions-010` (`bać się`, 2 meanings), `b1-expressing-opinions-013` (`zależeć`, 2 meanings) |
| **Nothing** | 4 contrast-only + every unreferenced card | `a1-food-basics-023`, `a2-healthcare-appointments-017`, `b1-character-emotions-003`, `b1-expressing-opinions-009` |

Roughly half the referenced cards get a chip and half get a doorway. That ratio is the rule being
appropriately conservative, not the rule being broken.

### 8.4 Imperfect card↔meaning mapping — the four real cases

Every one of these exists in the committed corpus. None needs a special case in the code.

1. **Clean single mapping.** `czekać na + Accusative` refs `a1-first-verbs-021` with `support`;
   `czekać` has one meaning and one pattern. Chip shows. The card's own hint already reads
   `'Czekam na...' + accusative`, so the chip agrees with the card rather than contradicting it.
2. **`bać się` — the ambiguity the amendment exists for.** `b1-character-emotions-010` is claimed by
   **exactly one** eligible pattern (`be-afraid-of` + Genitive). Gate 1 alone would print
   `kogo? czego? · Genitive` as *the* answer. But `bać się` has a second canonical meaning
   (`worry about`, `o` + Accusative, recognition-only) that references **no card at all** — so the
   card would confidently teach half the lemma, and the half it omitted would be invisible precisely
   because it has no card. **Gate 2 catches this**: the lemma has two meanings, so the card shows the
   neutral doorway and the disambiguation happens in the lemma entry where both meanings are
   rendered side by side (§4.1a, State 2). *The card never picks a meaning on the learner's behalf,
   and the absence of a second ref never gets read as the absence of a second meaning.*
   `zależeć` (`b1-expressing-opinions-013`) and `słuchać` (`a1-free-time-005`) resolve identically.
3. **Mixed support and contrast on one card.** `a1-first-verbs-018` is `support` for `lubić` and
   `contrast` for `podobać się`. The contrast ref is invisible to the feature, so Gate 1 sees one
   eligible claim — and Gate 2 then sends it to the doorway anyway, because `lubić` has two patterns
   (Accusative object and infinitive activity). The contrast ref changed nothing in either
   direction, which is exactly the required behaviour: **a contrast reference never implies the card
   teaches or instantiates the pattern, and never influences whether another pattern is shown.**
4. **Template cards and cards that do not exist.** `potrzebować` has an A2 card
   (`a2-pharmacy-002`) that qualifies for a chip; Phase 0 separately noted that much of
   `potrzebować`'s evidence lives in a template and in scenarios. Templates are read-only
   explanatory cards excluded from every practice pool ([`pp-usage.js:140`](../pp-usage.js#L140)),
   and a government note on a template back is desirable. Where a lemma has **no** card ref at all,
   the card surface simply says nothing — the lemma remains fully reachable through the verb index,
   which is why the index and not the card is the canonical home.

### 8.5 What is explicitly not done

- No card data is edited. `CARD_FIELDS` stays closed, `validate_content.py` is untouched, the
  content frozen baselines are untouched, existing card totals are untouched.
- No card authors a backlink. The index is derived at runtime from the pattern side only, which is
  the locked one-way `contentRef` model.
- Card progress is unaffected. Opening a pattern from a card writes nothing.
- Generated vocabulary pages (`/vocabulary/*`) are untouched — `build_pages.py` does not read the
  runtime file.

---

## 9. Activity strategy

**Governing rule, unchanged from Phase 1: `activityEligibility` is an allowlist and defaults to
false. A pattern never enters an activity because it exists.** Today all 45 arrays are empty, so
the honest current answer for every activity below is *none*.

The design below is what becomes *possible* after approval, in priority order.

### 9.1 Grammar — **the first and only recommended activity**

`grammar-choose` only. Recommended shape: a `Practice these verbs` set inside the Verb Patterns
level, using the existing Grammar screen's choose interaction wholesale (`gRenderChoose`,
`gChooseFeedback`, requeue-once, session-only score, `#gStatus` announcements) but drawing from
**authored pattern exercise items**, not from a projection of the pattern record.

Each item is a `vp-x-<pattern-stem>-grammar-choose-<item-key>-<digest12>` record with its own
context sentence, its own authored distractors, one intended answer, and its own frozen feedback —
exactly as the Activity Eligibility Specification §8 requires. The pattern supplies the *target* and
the *feedback vocabulary*; it does not supply the item.

`grammar-build` is **not** recommended for the pilot: it additionally requires canonical order plus
every accepted alternate order plus deterministic inflection, which is a much larger authoring
surface for a marginal gain over choose.

### 9.2 Type It — **cue: no. Feedback: yes. Correction explanation: yes.**

- **As a cue — no.** Type It draws from `poolFor(src,"typeit")` over vocabulary levels
  ([`index.html:4142`](../index.html#L4142)). Injecting a pattern hint into `#tEn` or `#tCtx` would
  change what the existing 1,089-card pool tests and would give an unearned hint on cards that never
  asked a government question. It also changes a pinned pool without a phase owning that change.
- **As feedback — yes, narrowly, and later.** When a learner types a wrong answer for a card that is
  claimed by **exactly one** pattern, the `.verdict` panel may add one line under the existing
  alternatives line, using the pattern's `errorNotes` when the typed form matches a documented
  `incorrectForm`, else the pattern chip. The corpus has 24 `predicted-distractor` notes with
  `incorrectForm` + `guidanceEn`, which is exactly this shape (`"Szukać takes the Genitive, not the
  Accusative: szukam kawiarni."`).
- **Hard constraints if this is ever built:** `PP_ANSWER.classify` is untouched — the verdict must
  not change; `acceptedAnswers` is untouched — no new answer becomes correct; `PP_TYPED_INDEX` is
  untouched; the added line is display-only and appears after the verdict is already decided.
- **Never a `type-it` eligibility for a pattern itself in the pilot.** Type It over a pattern
  requires a demonstrably closed answer set, and the Activity Eligibility Specification §3 already
  rules out bare English cues like "ask", "talk", "believe" — which is most of this corpus.

### 9.3 Mixed Quiz — **not in the pilot**

`startRound()` writes first-try results into card progress via `rRecord()`
([`index.html:5128`](../index.html#L5128)). A pattern entering that round either (a) writes pattern
performance into card mastery — forbidden by the Frozen Data and Persistence Specification §4 — or
(b) needs a parallel non-writing path through a scoring function whose entire purpose is to write.

A pattern becomes Mixed-eligible only when **all** of these hold: it already passes its base
activity gate; a session-only pattern round exists that provably does not touch
`popolsku-progress-v2`; and the pool is stratified so a round cannot accidentally become "six
Accusative questions". That is a separate design, not a pilot slice.

### 9.4 Listening — **separate, and mostly no**

Listening tests *utterance → meaning*, not morphology ([`index.html:4511`](../index.html#L4511)).
Pattern knowledge adds nothing to that question. There is a genuinely different activity — *hear a
sentence, identify the case ending or the preposition+case* — but it is a **new activity**, not an
extension of Listening, and it requires audio that does not exist: zero examples in the corpus have
`audioEligible: true`, and `audioEligible` is only valid when the containing pattern has `listening`
eligibility, which none has.

**Recommendation: keep Listening out of scope entirely for the pilot.** Reusing an approved pattern
example as a Listening item is a Phase 4-class audio decision, not a UX decision.

### 9.5 A dedicated "Build the pattern" activity — **not justified**

Assessed and declined. `grammar-build` already exists, already has token/order/inflection semantics,
already has accessible keyboard handling in `gPaintBuild()`, and already has tests. A new activity
would duplicate it in order to feel new. Per the brief's own caution: do not create one merely
because Priority 7 exists.

The only future activity that would be genuinely new — *"which case does this verb take?"* as a
lemma→case matching drill — is attractive because it directly drills the stated learner problem. It
is recorded here as a **candidate for a later phase**, explicitly out of scope for Phase 3, and
would need its own eligibility key, its own item records and its own design.

### 9.6 Conversations

Unchanged. Contextual reinforcement only, per Phase 1: a pattern may be *linked* from a scenario
note where one already fits, and no scenario branch becomes scored. Not in the pilot.

---

## 10. Accessibility

### 10.1 Reuse, not reinvention

Every helper in audit §7 is reused as-is. Specifically, the new surface **must**:

| Need | Existing helper to use |
|---|---|
| any focus move | `ppFocusActivityTarget` (never bare `.focus()`) |
| focus on a target that may be below the fold | `ppFocusAndRevealActivityTarget` |
| screen entry focus | `ppScreenEntryTarget` via `ppRouteScreenFocus` (the screen's `h1`) |
| return focus to the invoking control | the existing `ppScreenReturnTargets` path in `show()` |
| any status announcement | `ppSetActivityStatus` — **text nodes only, never `innerHTML`** |
| expand/collapse state | native `<button aria-expanded>` + `aria-controls`, matching `#siteMenuButton` |
| audio control naming (later) | `ppSetAudioControlName` |
| screen scroll on back | the existing `ppRememberScreenScroll` / `ppApplyScreenScroll` contract |

New markup must add exactly **one** `sr-only role="status" aria-live="polite" aria-atomic="true"`
region if the surface ever announces anything, and none if it does not. A purely passive reference
surface should have none — an announcement region that never announces is the failure the
`#lFbBox` / `#rFb` demotion comments in the markup already record.

### 10.2 Semantics

- One `<h1>` per screen, in `.sbar-title`, matching every other screen.
- Set → lemma → meaning is a heading hierarchy: `h1` set name, `h2` lemma, `h3` meaning. The pattern
  block is **not** a heading; it is a `<section>` labelled by its headline via `aria-labelledby`.
- The chip row is a `<ul>` of `<li>`; each chip's Polish question carries `lang="pl"` and the case
  name does not. **No chip is an interactive control** unless it is the case link, in which case it
  is a real `<a>`/`<button>`, never a styled `<div>` with a click handler.
- The role line is ordinary text inside the same `<li>`, so a screen reader reads
  *"kogo? czego?, Genitive, the thing you're looking for"* as one item.
- Expandable content (the meaning blocks on a dense lemma, if collapsing is needed at all) uses
  `<button aria-expanded>` controlling a region by id. Content that is collapsed is `hidden`, so
  `ppIsHiddenOrInert` correctly refuses to focus into it.

### 10.3 Reading order

Fixed, and identical to visual order (§4.1): headline → level badge → recognition chip → chip 1
(question, case, role) → chip 2 → explanation → example Polish → example English → links. A
two-complement pattern must never interleave its chips and roles, which is why the role line lives
*inside* the list item rather than in a parallel row.

### 10.4 Non-colour, contrast, motion, targets

- **Never colour alone.** A case chip's meaning is entirely in its text. The single accent tint is
  decoration. The recognition-only chip reuses `.usage-badge.u-recognition`, whose *text* says
  "Recognition only" today — the new label must likewise be readable with colour removed.
- **Reduced motion.** Any expand/collapse must be added to the existing
  `@media (prefers-reduced-motion:reduce)` block ([`index.html:986`](../index.html#L986)), not given
  its own block.
- **Touch targets.** Every tappable row ≥ 44px tall, matching `.site-menu-button` (44) and
  `.site-nav-list` (52). A chip that is not interactive has no minimum; a chip that *is* a link
  must meet it.
- **Zoom / text scaling.** No `maximum-scale`, no `user-scalable=no` — the shell's viewport is the
  contract and `build_pages.py` already refuses to emit a zoom-blocking directive
  ([`build_pages.py:104`](../build_pages.py#L104)). At 200% text the chip must wrap, not clip; this
  is why the chip has no fixed width.

### 10.5 Existing tests that constrain the implementation

These suites will exercise the new code the moment it exists in `index.html`, because they extract
functions from the shipping file:

`tests/test_phase1a_accessibility.js`, `tests/test_phase1b_keyboard_focus.js` (extracts `show`,
`showScreen`), `tests/test_phase2a_core_activity_accessibility.js` (extracts
`ppIsInteractiveTarget`), `tests/test_phase2c_navigation.js` (extracts `show`, `ppOpenSiteMenu`),
`tests/test_phase3b_focus_scroll.js` (extracts `show`, `showScreen`), `tests/test_phase3b_overlays.js`,
`tests/test_phase3b_mobile_layout.js`, `tests/test_phase3_closeout.js`.

`test_phase3b_focus_scroll.js` and `test_phase1b_keyboard_focus.js` in particular pin `show()` /
`showScreen()` behaviour, so **adding a tenth screen id changes code those suites already drive**.

---

## 11. Mobile and responsive behaviour

`.wrap` is `max-width:560px` with 20px padding, phone-first, centred on desktop (audit §8). The
pattern surface inherits that column and does nothing else at any width — there is **no tablet or
desktop layout**, because the app has none and inventing one for this surface alone would be the
parallel-mini-app failure.

### 11.1 The three widths

| Class | Width | Behaviour |
|---|---|---|
| **Narrow phone** | 320–360px | Chip row goes one chip per line. The `+` separator between complements becomes a leading `+` on the second chip's line. The role line sits under its own chip. Headline wraps at token boundaries. |
| **Normal phone** | 361–560px | Two single-complement chips may share a line; a two-complement pattern still stacks, because `z kim? z czym? · Instrumental` plus `o czym? · Locative` does not fit side by side at 375px. |
| **Tablet / desktop** | >560px | Identical to normal phone, centred in the 560px column. |

**The case-filter row** is eight interactive chips (`All` + seven cases + `No case`), which cannot
fit one line at any supported width. It **wraps** (`flex-wrap`), it does not scroll horizontally —
a horizontally scrolling filter strip would violate the no-`overflow-x` constraint in §11.2 and
would hide options off-screen. At 320px it occupies three wrapped lines; each chip is a real
`<button aria-pressed>` meeting the 44px touch target, matching the existing `.seg-btn` /
`.cat-btn` idiom rather than inventing a new control.

### 11.2 The hard CSS constraints

Derived from the pinned tests in audit §8, these are not preferences:

1. **No new media-query width may be added.** `test_phase3b_mobile_layout.js` asserts the sheet's
   max-widths are exactly `[360, 400, 400]`. Any pattern CSS is either width-agnostic or lives
   inside an existing 400px block.
2. **The 360px block may not gain a selector.** Its selector list is asserted to be exactly
   `['.pill-practice','.t-arrow','.topic','.topic-main']`.
3. **No `overflow-x: hidden|clip` anywhere.** `test_phase3_closeout.js` `A5`.
4. **No new `overflow-wrap:anywhere`/`word-break`.** `B5 only the audited selectors may break
   inside a word`. Long Polish strings must fit by *wrapping between tokens*, which is why the
   headline is built from separate tokens and the chip is a flex item with `flex-wrap`.

The layout that satisfies all four: chips in a `display:flex; flex-wrap:wrap` list with
`gap`, each chip `max-width:100%` and normal word wrapping inside, and the headline as inline tokens
in a normal paragraph. No horizontal scrolling can occur because nothing has an intrinsic minimum
wider than one token.

### 11.3 The longest strings, measured against the design

The worst case in the corpus is `rozmawiać z kimś o czymś` (headline) with chips
`z kim? z czym? · Instrumental` (30 chars) and `o kim? o czym? · Locative` (25 chars). At 320px the
available content width is 280px; a 30-character chip at the `.usage-badge` scale (10.5px, uppercase
tracking) does not fit and must drop to the body scale. **Recommendation: the case chip uses the
`.chip` scale (11.5px, no uppercase transform, `--mint-bg`), not `.usage-badge`**, because
uppercasing `kogo? czego?` is both ugly and wrong for Polish question words.

### 11.4 Navigation depth

Home → index → lemma is two taps, and one Back reverses each. **Applying a case filter adds no
depth** — it is a state change on the index screen, not a navigation step, so Back from a lemma
entry returns to the index *with the filter still applied*, and Back again leaves the surface. The
lemma entry is a **scroll**, not a third level — meanings and patterns are sections on one page, so
a `rozmawiać` entry is one screen the learner scrolls, not three screens they navigate.

The deep link from a case lesson (§7) enters the index *already filtered*, which means it consumes
the same single navigation step as any other entry into the surface. No route in this design is
three levels deep.

---

## 12. Scalability beyond 30 verbs

The design is chosen partly because it survives growth, and the lemma-first correction improves this
materially: **growth adds rows to one index rather than adding containers.** At 30 lemmas / 45
patterns the A–Z index is one comfortable scroll with sticky letter headings.

| Corpus size | What changes | What does not |
|---|---|---|
| 30 → ~80 lemmas | Nothing structural. The index grows; letter headings already carry it | The hierarchy, the filter, the chip, the routing |
| ~80 → ~200 | A within-index type-ahead filter beside the case chips; case-filtered views may add a CEFR sub-band using the recognition level already in the runtime data | The one-lemma-one-entry invariant |
| ~200+ | Search becomes the primary entry point rather than browsing, which requires the field-aware pattern index described in [`priority-7-existing-content-integration-map.md`](priority-7-existing-content-integration-map.md) §4 | The presentation layer |

Note what is **absent** from that table: at no size does the number of *containers* grow. Under the
rejected case-grouped model, a corpus that introduced a new preposition+case combination or a new
teaching grouping would have argued for a new set; here it produces a new filter option at most, and
usually nothing at all.

Three properties make this work, and all three are consequences of decisions above:

1. **Nothing is authored per surface.** Headlines, chips, questions and role phrases are all derived
   from structured fields, so 200 lemmas cost 200 records and zero UI strings.
2. **There is one container, and it is data-driven.** The index is computed from the runtime
   document; filters are computed from the cases actually present. A corpus that gains a case, a
   preposition or a complement type gains a filter option, not a container — the same
   derive-don't-store property that makes `categoryOf` work today.
3. **Nothing persists.** No per-pattern progress means no migration when the corpus grows, splits,
   or retires an ID. This is the single biggest scalability gift the no-persistence decision gives.

The known scaling hazard is **search**: `topicHaystack` walks every string on a topic object and
caches it. A single index topic holding 200 rendered pattern strings would make one search entry
enormous and would index anything id-shaped that leaked onto the object. §13 handles this, and the
single-container model makes it *more* acute, not less — which is why §13's rule is a hard
constraint rather than a preference.

---

## 13. Search integration

**Pilot recommendation: the Verb Patterns *index* is searchable as one topic; individual patterns
are not searchable in Phase 3.**

- The index topic carries a deliberately small, curated `name`/`desc`/`chip`, plus a **flat,
  explicitly built** `searchText` string containing display lemmas, case names (English and Polish),
  prepositions and diagnostic questions — and nothing else. Because `topicHaystack` recurses over
  everything, the runtime lemma and pattern objects **must not be hung off the topic object**; the
  topic holds an opaque surface key, and the loader resolves entities from a separate module-scoped
  map. With one container instead of eight, this is the single string that must stay disciplined.
- `HAY_SKIP` currently skips `emoji, kind, start, goto, type, link` — **not `id`**. Any new
  identifier-shaped field placed on a topic would become searchable. The design therefore places no
  `vp-*` identifier on any topic object at all, which is stronger than extending `HAY_SKIP` and
  needs no engine change.
- Per-pattern search results (returning a *pattern*, not a topic) require the field-aware index and
  a result type the search UI does not have today. That is a separate, later slice.

---

## 14. Progress, privacy and measurement

Restating the constraints this design operates under, all of them inherited and none reopened:

- **No durable pattern mastery.** No new `localStorage`/`sessionStorage`/IndexedDB key. Session state
  is ordinary in-memory JavaScript, exactly like `G`, `T`, `L`, `R`.
- **`popolsku-progress-v2` byte-for-byte unchanged** through load, browse, open, expand, collapse
  and leave. `schemaVersion` stays 2; `CONTENT_MIGRATION_REVISION` stays 2.
- **No card↔pattern mastery transfer** in either direction.
- **No analytics, no telemetry, no cookies, no identifiers.** The Privacy screen makes this a public
  commitment ([`index.html`](../index.html), Privacy section) and this design adds nothing to
  reconsider. The parked Priority 6 measurement decision is not reopened.
- The one piece of state the surface may hold is **which set was last open, in memory, for the
  session**, which is the same class of state as `S.levelIdx`.

---

## 15. Decision log

| Decision | Alternatives | Why selected | Reopen trigger |
|---|---|---|---|
| Hybrid: dedicated surface + two doorways | Grammar-only; cards-only; standalone tab; generated pages | The learner's problem is lemma-first lookup; the app already synthesizes levels; a `group:"grammar"` level needs no engine edit | Learner evidence that browsing by case is never used |
| **`lemma → meaning → pattern` is the sole canonical ownership hierarchy; A–Z index is the default entry** | seven case-grouped sets as containers (the superseded first draft); case sets alongside A–Z | The learner arrives holding the verb; case containers fragment multi-case lemmas, have no home for infinitive/clause complements, and reproduce the silo problem inside the new surface | Only a redesign that removes multi-case lemmas and non-cased complements from the corpus |
| **Case is a filter/view over the one index, addressable as deep-linked state** | case as an owner; case as a separate screen | Views cannot duplicate ownership; a case lesson can hand off without creating a second home for a pattern | A container model is separately justified |
| Filtered rows are pointer summaries, never pattern renderings | render the full pattern in the filtered list | Full rendering in a filtered view *is* duplication under another name | — |
| Multi-complement rows show all chips, emphasising the matched one | show only the matching chip | Showing one chip of a two-slot frame teaches half a frame | — |
| Explicit `No case (verb / clause)` filter option | omit; or bucket infinitive/clause under a case | Infinitive and clause complements have no case; silence would hide them | A complement type with different semantics is added |
| Verb Patterns is a level in the **Grammar** category | fourth top-level tab | `.cat-seg` is a pinned three-tab row at 320px; Grammar is where case questions already go | A category redesign for another reason |
| New `#patterns` screen, not `#grammar` reuse | reuse `gRenderTeach` | `gRenderTeach` is `innerHTML` over authored markup; flip-to-reveal is wrong for lookup; `startGrammar` needs `drills` | A safe text-node teach renderer appears for another reason |
| One chip: `question(s) · Full Case Name`, preposition bonded | case label only; question only; two chips; per-case colour | Each half repairs the other; matches what the case lessons already teach; colour-only fails 1.4.1 and collides with existing semantic colours | Learner testing shows the pair is unreadable at 320px |
| Questions derived centrally, never stored | store per complement | Phase 1 locks central derivation; corpus has zero `questionOverridePl` | A reviewed `questionOverridePl` appears |
| Role line always shown | only for multi-complement | `prosić kogoś o coś` has two chips with the same case; consistency beats conditional layout | Layout pressure at 320px proves it unaffordable |
| Recognition CEFR only in the badge | show both | two numbers is linguist-facing; production gap is expressed as absence of practice | A production-level activity ships and learners need the distinction |
| Card back: one pointer line, gated on **`kind:"card"` + `purpose:"support"` only** | treat every `contentRef` as a learner link (the superseded first draft); include `contrast`; include `drill`/`topic` refs | `contrast` asserts difference, not instantiation; `practice`/`context` are not instantiation claims; `topic`/`drill` are different features. No new relation type invented | Only a locked-enum change |
| Card chip additionally gated on **lemma-level meaning ambiguity** (Gate 2) | ref-count gate alone | `bać się` has one eligible ref and two governed meanings — a ref-count gate alone would teach half the lemma confidently | A released corpus in which every lemma has one meaning |
| Contrast refs are invisible to the card feature — they neither show nor downgrade | let contrast produce a doorway | A contrast ref must never imply the card teaches or instantiates the pattern, in either direction | — |
| Grammar-choose is the only recommended activity | build; Type It; Mixed; Listening; new activity | choose has the smallest safe authoring surface and reuses tested interaction | Native review approves a closed answer set for a specific pattern |
| Listening explicitly out of scope | reuse examples as listening items | zero `audioEligible` examples exist and none can exist without `listening` eligibility | A separate audio phase |
| No pattern in Mixed Quiz | session-only parallel path | `rRecord` exists to write card progress | An approved session-only pattern round design |
| Sets searchable, patterns not | index every pattern | `topicHaystack` recurses over everything and does not skip `id` | A field-aware pattern index is built |
| No new media-query width | a pattern breakpoint | `test_phase3b_mobile_layout.js` pins the width list exactly | That test is deliberately amended by an owning phase |
| No persistence of any kind | session or durable pattern state | locked by Phase 1; also the main scalability gift | A separately approved persistence design |
