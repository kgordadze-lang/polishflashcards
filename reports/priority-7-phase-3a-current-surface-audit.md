# Priority 7 — Phase 3A Current-Surface Audit

**Phase:** 3A architecture and UX design only. No application, data, test, editorial or runtime
file was changed.
**Baseline:** branch `priority-7-phase-3a-ux-architecture`; HEAD `2b152f4d6079762f875bf1f3a2b3c2699970e4c2`;
tree `f6e9b3ae49bd7e0f35bc2ba6f7bfd092ed017fc3`; zero Git remotes; `push.default=nothing`;
clean tracked worktree at start.

This report is repository evidence. Every claim below is a direct observation of the checked-out
source at that tree, cited by file and line. It is not generic product advice, and it contains no
recommendation — recommendations live in
[`priority-7-phase-3a-ux-integration-architecture.md`](priority-7-phase-3a-ux-integration-architecture.md).

---

## 1. Application shape

Po polsku is a **single-document application**. [`index.html`](../index.html) is 5,615 lines and
holds the entire shell: two `<style>` blocks ([`index.html:65`](../index.html#L65),
[`index.html:74`](../index.html#L74)), the whole body markup, and one inline `<script>` block
([`index.html:1841`](../index.html#L1841)–[`index.html:5613`](../index.html#L5613)).

Only four helper scripts are external, and they are pure (no DOM, no app state):

| File | Owns |
|---|---|
| [`pp-usage.js`](../pp-usage.js) | usage chips + `PP_USAGE.eligibleFor` activity gate + main-audio rule |
| [`pp-answer.js`](../pp-answer.js) | typed-answer normalization, accepted set, verdict classification |
| [`pp-distractor.js`](../pp-distractor.js) | multiple-choice option construction and collision avoidance |
| [`pp-migrate.js`](../pp-migrate.js) | progress store keys, v1→v2 migration, progress counts |

Seven data files are loaded before them, in a fixed order
([`index.html:1830`](../index.html#L1830)–[`index.html:1836`](../index.html#L1836)):
`data-a1.js`, `data-a2.js`, `data-b1.js`, `data-grammar.js`, `data-verbs.js`, `data-scenarios.js`,
`data-podcasts.js`. Each pushes onto `window.PP_LEVELS`. If `PP_LEVELS` is absent the app replaces
`document.body` with a load-failure message and throws
([`index.html:1866`](../index.html#L1866)–[`index.html:1871`](../index.html#L1871)).

There is **no build step for the app itself**. [`build_pages.py`](../build_pages.py) generates the
separate static marketing/reference pages only (§10).

**Consequence for Priority 7.** There is no module system, no bundler and no component framework
to integrate with. A new consumer is either (a) a new external `pp-*.js` helper plus a call site
in the inline script, or (b) inline script only. The existing four helpers establish (a) as the
house pattern for anything that deserves its own tests.

---

## 2. Information architecture and navigation

### 2.1 Levels, categories, tabs

`LEVELS` is `window.PP_LEVELS` ([`index.html:1865`](../index.html#L1865)). At runtime it holds
**twelve** levels: ten authored in data files, plus two appended by the shell.

Authored levels: `A1`, `A2`, `B1` (vocabulary); `Grammar Cases`, `People & Numbers`, `Politeness`,
`Building Sentences` (all `group:"grammar"`, in [`data-grammar.js`](../data-grammar.js)); `Verbs`
(`group:"grammar"`, [`data-verbs.js:16`](../data-verbs.js#L16)); `Scenarios`; `Podcasts`.

Two further levels are **synthesized at runtime and pushed onto the same array**
([`index.html:1919`](../index.html#L1919)–[`index.html:1922`](../index.html#L1922)):

```js
LEVELS.push(
  { level:"Type it",   blurb:"See the meaning, type the Polish", topics: practiceTopics("typeit","⌨️") },
  { level:"Listening", blurb:"Hear the Polish, pick the meaning", topics: practiceTopics("listen","🎧") }
);
```

A third synthetic topic — the all-cases drill mix — is `unshift`ed into the existing
`Grammar Cases` level by an IIFE ([`index.html:1923`](../index.html#L1923)–[`index.html:1941`](../index.html#L1941)).

**This is the single most important architectural fact for Priority 7.** The shipping app already
synthesizes learner-facing levels and topics from data it did not author as a level, appends them
to `PP_LEVELS` after load, and lets home navigation, search and routing pick them up through the
ordinary paths. Nothing about that mechanism is a special case.

Category membership is **derived, never stored**
([`index.html:2397`](../index.html#L2397)–[`index.html:2401`](../index.html#L2401)):

```js
function categoryOf(lv){
  if(isVocabLevel(lv)) return "vocab";
  if(lv.group === "grammar") return "grammar";
  return "practice";
}
```

`isVocabLevel` is "every topic has no `kind`" ([`index.html:2389`](../index.html#L2389)).
`CATEGORIES` is a three-entry constant — Vocabulary / Grammar / More
([`index.html:2402`](../index.html#L2402)). The code comment states the extension contract
explicitly: *"Add a new grammar level (group:"grammar") and it shows up under the Grammar tab
automatically - no engine edit."*

Current category populations: vocab 3, grammar 5, practice 4.

### 2.2 Home rendering

`renderLevels()` ([`index.html:2413`](../index.html#L2413)) renders the whole home nav: the
`#catSeg` tab bar (`role="tablist"`, buttons with `role="tab"` + `aria-selected`), the `#subFilter`
level pills (`aria-pressed`), and `renderTopicsHead()`. Pill grid columns are chosen by count:
`≤3` one row, `4` a 2×2, `5+` three across ([`index.html:2444`](../index.html#L2444)). A sixth
grammar level would therefore stay on the existing `repeat(3,1fr)` layout.

`renderTopics()` ([`index.html:2605`](../index.html#L2605)) builds one `.topic` row per visible
topic: an emoji tile (`topicIcon`, [`index.html:2591`](../index.html#L2591)), title, description,
a `.chip` (`t.chip || modeLabel(lv)`), a count string from `tCount()`
([`index.html:2593`](../index.html#L2593)), an optional `.pill-practice` "Quiz" button, and a
decorative `.t-arrow` chevron.

`tCount()` is a hard-coded switch over `t.mixOf`, `t.kind==="typeit"|"listen"`, `"grammar"`,
`"convo"`, `"podcast"`, else cards. An unknown `kind` falls through to the card branch and would
read `undefined cards`.

### 2.3 Screens and routing

Nine `<section class="screen">` elements exist: `#home`, `#study`, `#grammar`, `#convo`,
`#typeit`, `#listen`, `#round`, plus `#privacy`, `#about`, `#contact`, `#install`.

`show(scr, deferFocus)` ([`index.html:2357`](../index.html#L2357)) pushes a history entry and calls
`showScreen()` ([`index.html:2342`](../index.html#L2342)), which toggles `.active`, hides the footer
off home, applies the scroll contract and routes focus. Back is `popstate` →
`showScreen(state.scr, false, true)`. Four screens are deep-linkable by hash
(`about`, `privacy`, `contact`, `install`, [`index.html:2376`](../index.html#L2376)); the activity
screens are not.

`routeTopic(li, ti, t)` ([`index.html:3389`](../index.html#L3389)) is the one dispatch point:

```js
if(t.kind === "grammar") startGrammar(li, ti);
else if(t.kind === "convo") startConvo(li, ti);
else if(t.kind === "typeit") startTypeit(li, ti);
else if(t.kind === "listen") startListen(li, ti);
else startTopic(li, ti);                              /* vocab + podcast */
```

**It has no default-deny branch.** An unrecognized `kind` silently opens the flashcard screen with
`t.cards` undefined. `openTopic()` wraps it with the mature-language gate
([`index.html:3396`](../index.html#L3396)).

Traced concretely: `startTopic(l,t)` ([`index.html:2654`](../index.html#L2654)) assigns
`S.cards = LEVELS[l].topics[t].cards` and immediately calls `S.cards.map(...)`. For a topic with an
unknown `kind` and no `cards` array this throws a `TypeError` inside the click handler **before**
`show("study")` is reached — so `S.levelIdx`/`S.topicIdx` have already been mutated to point at a
topic the flashcard screen cannot render, no navigation occurs, and the learner gets a tile that
does nothing with no message. A topic whose `cards` array merely exists but holds the wrong shape is
worse: it navigates and renders garbage. Today no such topic exists, so the defect is latent.
**Phase 3B introduces the first new `kind` since `typeit`/`listen`, which is what makes this latent
defect reachable**; the required remediation is specified in
[`priority-7-phase-3a-implementation-plan.md`](priority-7-phase-3a-implementation-plan.md) §A4a.

### 2.4 Secondary navigation

`#siteDrawer` is a native `<dialog>` opened with `showModal()` from `#siteMenuButton`
([`index.html:2307`](../index.html#L2307)). It contains six links: About, Install, Privacy,
`guide/listening/`, `guide/`, Contact. It is a **site/meta menu, not a learning menu** — no
learning surface is reachable from it. `ppActivateSiteMenuScreen()`
([`index.html:2333`](../index.html#L2333)) routes the in-app ones.

### 2.5 Search

One input, `#search`, on home only. `topicHaystack(t)` ([`index.html:2489`](../index.html#L2489))
**recursively walks every string on the topic object** and joins them lowercased, skipping only the
keys in `HAY_SKIP = {emoji, kind, start, goto, type, link}`. `getVisibleTopics()` does a single
literal `includes(q)` and **returns whole topics, never cards or patterns**
([`index.html:2501`](../index.html#L2501)). Results are cached per topic object in a `WeakMap`.

**Consequence for Priority 7.** Any string placed on a synthesized topic object is automatically
searchable, including anything that looks like an identifier. `id` is *not* in `HAY_SKIP`.

---

## 3. Grammar surface

### 3.1 Content shape

A grammar topic is `{ id, name, emoji, kind:"grammar", chip, desc, teach:[…], drills:[…] }`.

A `teach` item may carry `front`, `sub`, `answer`, `points[]`, `table[{g,e,ex}]`, `explain`,
`note`, `examples[{pl,en}]` ([`index.html:3469`](../index.html#L3469)).

A drill is `{ id, type:"choose"|"build", prompt?, promptEn, options?, answer, explain, full, fullEn }`.
`answer` is a string for `choose` and a token array for `build`
([`data-grammar.js:101`](../data-grammar.js#L101), [`data-grammar.js:110`](../data-grammar.js#L110)).

### 3.2 The seven case topics

All seven cases have a dedicated topic in the `Grammar Cases` level:

| Topic id | Name | Line | Drills |
|---|---|---:|---:|
| `grammar-cases-nominative` | Mianownik (Nominative) | [13](../data-grammar.js#L13) | 14 |
| `grammar-cases-genitive` | Dopełniacz (Genitive) | [145](../data-grammar.js#L145) | 14 |
| `grammar-cases-dative` | Celownik (Dative) | [280](../data-grammar.js#L280) | 14 |
| `grammar-cases-accusative` | Biernik (Accusative) | [418](../data-grammar.js#L418) | 15 |
| `grammar-cases-instrumental` | Narzędnik (Instrumental) | [555](../data-grammar.js#L555) | 14 |
| `grammar-cases-locative` | Miejscownik (Locative) | [688](../data-grammar.js#L688) | 14 |
| `grammar-cases-vocative` | Wołacz (Vocative) | [825](../data-grammar.js#L825) | 14 |

Each already teaches its own Polish diagnostic question in prose — the Genitive topic's first teach
card says *"It answers **kogo? czego?**"* ([`data-grammar.js:150`](../data-grammar.js#L150)) — and
each already names verbs as triggers in prose. `grammar-cases-genitive-014` is a `build` drill whose
answer is `["Szukam","mieszkania"]` with the explanation *"'Szukać' (to look for) always takes
Genitive"* ([`data-grammar.js:275`](../data-grammar.js#L275)). This drill is already referenced by
the Priority 7 `szukać` record as a `contentRef` with `purpose:"practice"`.

The Phase 0 inventory records the existing verb-trigger emphasis per case topic
([`priority-7-current-verb-case-inventory.md`](priority-7-current-verb-case-inventory.md), §5).
Verb government is therefore **already taught, but distributed across seven case silos, in prose,
with no queryable structure and no lemma-first entry point**.

### 3.3 Grammar interaction

`startGrammar()` ([`index.html:3462`](../index.html#L3462)) → `gRenderTeach()` (flip card, learn
phase) → `gStartPractice()` → `gRenderDrill()` → `gRenderChoose()` / `gRenderBuild()` → `gShowDone()`.

Critical detail: `gRenderTeach()` and `gRenderChoose()` build their DOM with **`innerHTML` over
authored strings** ([`index.html:3480`](../index.html#L3480)–[`index.html:3489`](../index.html#L3489),
[`index.html:3571`](../index.html#L3571)). This is safe today because grammar teach/drill copy is
hand-authored markup in a committed data file that deliberately contains `<b>` and `<i>`. It is
**not** a safe host for generated JSON strings.

Grammar practice is session-only: `G.results` is in-memory, misses requeue once, and nothing is
written to progress ([`index.html:3512`](../index.html#L3512)). The all-cases mix resamples 15
drills per round via `gSampleMix()` ([`index.html:3499`](../index.html#L3499)) and tags each with
`_case` so the drill card can print its origin.

`gRenderDrill()` routes `c.type==="choose"` to choose and **everything else to build**
([`index.html:3530`](../index.html#L3530)). There is no unknown-type rejection.

---

## 4. Vocabulary / card surface

### 4.1 Card schema is closed

[`validate_content.py:812`](../validate_content.py#L812) defines `CARD_FIELDS` as a closed set:

```
id, pl, en, hint, ex, exEn, pair, relationType, relatedIds, senseGroups, register,
acceptedAnswers, strength, cardType, pattern, variants, practice, typeItCue, warning,
intro, host, link, region, production, audioText
```

Unknown card keys fail validation (`CARD_FIELD_KEY_INVALID`). There is **no `lemma`, `meaningId`,
`case`, `patternRef` or provenance field**, and Phase 0 records the same
([`priority-7-current-verb-case-inventory.md`](priority-7-current-verb-case-inventory.md), §4).

Verb government currently lives in free-text `hint`. `a1-first-verbs-020` reads
`hint:"szukam, szukasz. Takes genitive: szukam pracy."`
([`data-a1.js`](../data-a1.js), `a1-first-verbs-020`); `a1-first-verbs-022` reads
`"Takes dative: pomagam mamie."`; `a1-first-verbs-021` reads `"'Czekam na...' + accusative."`
These are prose, per card, unstructured, and not consistently present.

### 4.2 Card rendering

`render()` ([`index.html:2801`](../index.html#L2801)) paints the flashcard. The **back face** is the
only place with room for additional reference material, and it is already dense:
`#backEyebrow`, `#enText`, `#usageBack`, `#backHint`, `#warnBox`, `#pairLine`, `#variantLine`,
`#ytLink`, `#exampleBox`, then the two feedback buttons
([`index.html:1176`](../index.html#L1176)–[`index.html:1206`](../index.html#L1206) in the body
markup). `.pair-line` ([`index.html:449`](../index.html#L449)) is the existing precedent for a
compact labelled reference row: an uppercase key and a Polish value, wrapping, centred.

`ppFillUsageRow()` / `ppAppendUsageTo()` ([`index.html:2675`](../index.html#L2675),
[`index.html:2698`](../index.html#L2698)) render usage chips into an `aria-hidden` wrapper with a
sibling `.sr-only` sentence, so the chips are announced once as prose rather than as a chip soup.
This is the repository's existing, tested pattern for a chip row.

### 4.3 Card ↔ pattern linkage that already exists

The Priority 7 editorial corpus already carries **101 typed `contentRefs`** across the 45 patterns.
Every pattern has at least one. All 23 examples are `repository-reuse` with an exact
`repositorySource {kind, id, field}`. The direction is **pattern → repository**, one-way; no card
authors a backlink, and none can, because `CARD_FIELDS` is closed.

The locked enums are `CONTENT_KINDS = {card, topic, drill, scenario}` and
`CONTENT_PURPOSES = {support, practice, context, contrast}`
([`priority7_tooling.py:94`](../priority7_tooling.py#L94)). The **actual** distribution in the
committed corpus is far narrower than the enum permits, and the exact cross-tabulation matters for
any card-back design:

| `kind` × `purpose` | Count |
|---|---:|
| `card` × `support` | **29** |
| `card` × `contrast` | **6** |
| `topic` × `support` | 44 |
| `topic` × `contrast` | 5 |
| `drill` × `practice` | 17 |
| `card` × `practice` | 0 |
| `card` × `context` | 0 |
| anything × `context` | **0** |
| `scenario` × anything | **0** |

Card-level facts derived from that:

- **32** distinct cards are referenced by at least one pattern; **28** are referenced with
  `purpose:"support"`; **4** are referenced **only** with `purpose:"contrast"`
  (`a1-food-basics-023`, `a2-healthcare-appointments-017`, `b1-character-emotions-003`,
  `b1-expressing-opinions-009`).
- Exactly **one** card is claimed by more than one `support` pattern: `a2-restaurant-012`, claimed
  by both `prosić` patterns of the same meaning.
- One card carries a **mixed** pair: `a1-first-verbs-018` is `support` for `lubić` and `contrast`
  for `podobać się`.
- The `bać się` card `b1-character-emotions-010` is `support` for exactly one pattern
  (`be-afraid-of` + Genitive) — while the lemma has a **second** canonical meaning
  (`worry-about`, `o` + Accusative, recognition-only) that references **no card at all**.

That last row is the important one: a naïve "exactly one claiming pattern → show its chip" rule
would print a single confident Genitive answer on a card whose lemma has two governed meanings.
Reference-count ambiguity and **meaning ambiguity are different failure modes**, and only the first
is visible in the ref counts.

Note also that `a1-food-basics-023` — the contrast-only card for `lubić` — is precisely the card
Phase 0 flagged as internally inconsistent (it labels `nie lubię` "+ accusative" while its own
example is Genitive,
[`priority-7-current-verb-case-inventory.md`](priority-7-current-verb-case-inventory.md) §8). A
design that treated `contrast` as a teaching link would attach a pattern to the one card in the
corpus most likely to contradict it.

---

## 5. Activities

| Activity | Screen | Entry | Pool | Progress writes |
|---|---|---|---|---|
| Flashcards | `#study` | `startTopic` | `topic.cards` | **yes** — `persistProgress()` |
| Grammar | `#grammar` | `startGrammar` | `topic.teach` + `topic.drills` | no |
| Conversations | `#convo` | `startConvo` | `topic.scenes` | no |
| Type It | `#typeit` | `startTypeit` | `poolFor(src,"typeit")`, 15/round | no |
| Listening | `#listen` | `startListen` | `poolFor(src,"listen")`, 15/round | no |
| Mixed Quiz | `#round` | `startRound` | one topic's cards, 15/round | **yes** — `rRecord` |

`poolFor(srcLevels, activity)` ([`index.html:1900`](../index.html#L1900)) walks `VOCAB_SRC` (plain
vocabulary levels only), drops `t.mature` topics, and filters with `PP_USAGE.eligibleFor(c, act)`.
Its `activity` argument **defaults to `"typeit"`** deliberately, "so any future caller that forgets
the argument errs towards excluding recognition-only".

`PP_USAGE.eligibleFor` ([`pp-usage.js:136`](../pp-usage.js#L136)) is the app's existing eligibility
gate and **already fails closed on an unknown activity name**:

```js
if (activity === "flashcard" || activity === "search") return true;
if (card.intro || !card.pl || !card.en) return false;
if (card.cardType === "template") return false;
if (activity === "listen") return true;
if (activity === "typeit" && PP_USAGE.typeItOptOut(card)) return false;
if (activity === "typeit" || activity === "mixed") return !PP_USAGE.isRecognitionOnly(card);
return false;                                     /* unknown activity -> false */
```

The file's own comment states the reason: *"a typo'd or new activity name fails CLOSED"*. This is
the same default-deny philosophy the locked Priority 7 `activityEligibility` allowlist encodes,
already shipping, already tested by [`tests/test_activities.js`](../tests/test_activities.js).

### 5.1 Type It

`tRender()` ([`index.html:4148`](../index.html#L4148)) shows `c.en` (optionally suffixed with
`typeItCue`), `Context: c.exEn`, and `From: topic`. `tCheckAnswer()`
([`index.html:4198`](../index.html#L4198)) delegates the verdict to
`PP_ANSWER.classify(val, c, PP_TYPED_INDEX)` — three tiers: `right`, `almost` (diacritics only),
`wrong`. `PP_TYPED_INDEX` is built once from `PP_USAGE.typedPracticeCards(LEVELS)`
([`index.html:4144`](../index.html#L4144) region, [`pp-usage.js:198`](../pp-usage.js#L198)) so a
correct-but-undiacriticked answer that spells a *different* real card's answer is scored wrong, not
"almost".

Feedback is a `.verdict` panel: head line, canonical `pl` + audio, **one** alternatives line
(`pair` → `variants` → `acceptedAnswers`, first match wins), example, usage chips. There is no slot
for a structured explanation of *why* a form is wrong beyond that.

### 5.2 Listening

`lRender()` ([`index.html:4511`](../index.html#L4511)) plays a card's Polish and asks for its
English meaning from four options built by `PP_DISTRACTOR`. It is a **meaning-recognition** activity
over whole utterances; nothing in it tests morphology or government. Recognition-only cards are
kept (`eligibleFor(…, "listen") === true`). `syncListeningAudioReadiness()`
([`index.html:4578`](../index.html#L4578)) keeps `#lPlay` disabled and `aria-busy` until
`audio-manifest.json` settles.

### 5.3 Mixed Quiz

`startRound()` ([`index.html:4706`](../index.html#L4706)) interleaves three formats — `listen`,
`type`, `mc` — over one topic, 15 questions, misses requeued once. `rRecord()`
([`index.html:5128`](../index.html#L5128)) **writes first-try right/miss into the topic's card
progress**, which is why the topic tile's "to review" count stays honest. `rBuildOptions()`
([`index.html:4696`](../index.html#L4696)) passes a per-format prompt-identity function to
`PP_DISTRACTOR` so a heard question and a printed question cannot collide.

---

## 6. Progress and state handling

Two storage keys, both owned by [`pp-migrate.js`](../pp-migrate.js): the legacy v1 text-keyed store
(read and preserved, never written by the app) and `popolsku-progress-v2`, the ID-keyed store
(`PP_MIGRATE.KEYS.v2`, [`index.html:1994`](../index.html#L1994)).

Migration runs at startup before anything reads progress
([`index.html:1998`](../index.html#L1998)–[`index.html:2007`](../index.html#L2007)). A failed or
unsafe migration sets `PP_PROGRESS_STATE = "recovery-required"`, and `ppProgressWritable()`
gates **all** writes so stored bytes are left untouched
([`index.html:1996`](../index.html#L1996), [`index.html:2010`](../index.html#L2010)).

Only two activities persist: flashcard marking (`markKnown`/`markStill` → `persistProgress`) and
the Mixed Quiz (`rRecord`). Grammar, Type It, Listening and Conversations are entirely in-memory.
Three other `localStorage` values exist outside progress: `pp-card-dir`
([`index.html:1963`](../index.html#L1963)), the speed setting, and the A2HS install-prompt state.

Backup/restore is `ppDownloadBackup()` / `ppApplyBackup()`
([`index.html:5260`](../index.html#L5260), [`index.html:5273`](../index.html#L5273)) with a
confirmation preflight showing date and counts. Progress `schemaVersion` is `2` and
`CONTENT_MIGRATION_REVISION` is `2`.

**There is no analytics, telemetry, cookie or identifier anywhere in the app.** The Privacy screen
states this as a public commitment ([`index.html:1655`](../index.html#L1655) region:
*"The app's own code does not set cookies and contains no analytics, telemetry, or tracking code"*).

---

## 7. Accessibility architecture

The app has a small, deliberate, **shared** accessibility layer, all in the inline script, all
extracted and exercised by the JXA test suites.

| Helper | Line | Contract |
|---|---|---|
| `ppIsInteractiveTarget` | [2050](../index.html#L2050) | is this a real control (via `PP_INTERACTIVE_SELECTOR`) |
| `ppIsHiddenOrInert` | [2053](../index.html#L2053) | walks ancestors for `hidden`/`inert`/`aria-hidden`/`display:none`/inactive `.screen` |
| `ppCanFocus` | [2063](../index.html#L2063) | the single focus-validity boundary |
| `ppFocusElement` | [2068](../index.html#L2068) | always `focus({preventScroll:true})` |
| `ppFocusActivityTarget` | [2078](../index.html#L2078) | activity renderers' only focus entry point |
| `ppRevealFocusedTarget` | [2091](../index.html#L2091) | `scrollIntoView({block:"nearest"})`, never animated |
| `ppFocusAndRevealActivityTarget` | [2101](../index.html#L2101) | focus first, reveal what actually took focus |
| `ppKeepActivityFocusOr` | [2109](../index.html#L2109) | keep a still-valid trigger, else fall back |
| `ppSetActivityStatus` | [2119](../index.html#L2119) | **the one safe writer** for live regions — text nodes only, never parsed HTML, no duplicate announcement |
| `ppAnnounceTypedActivityResult` | [2131](../index.html#L2131) | shared three-verdict message, answer in its own `lang="pl"` node |
| `ppSetActivityOptionState` | [2143](../index.html#L2143) | `aria-pressed` on `.opt`, keeps native `disabled` semantics |
| `ppScreenEntryTarget` | [2149](../index.html#L2149) | a screen's `h1`, given `tabindex="-1"` |
| `ppRouteScreenFocus` | [2164](../index.html#L2164) | remembered invoker → in-screen current → entry heading |
| `ppOpenSharedOverlay` / `ppCloseSharedOverlay` | [2229](../index.html#L2229) / [2253](../index.html#L2253) | the one modal contract; never stacks two layers |
| `ppIsolateSiteMenuBackground` | [2276](../index.html#L2276) | shell `inert` + `aria-hidden` + body scroll lock, every prior state restored verbatim |
| `ppSetAudioControlName` | [2763](../index.html#L2763) | accessible name for every audio button |

Live regions are `sr-only`, `role="status"`, `aria-live="polite"`, `aria-atomic="true"`, one per
activity: `#gStatus`, `#tStatus`, `#lStatus`, `#rStatus`, `#cStatus`. The markup comments record
*why* the rich visible feedback boxes (`#lFbBox`, `#rFb`) were **demoted from live regions** — they
raced the concise result announcement.

Non-colour result signalling is a stated contract: `.opt.correct::after` / `.opt.wrong::after`
print `✓ Correct` / `✕ Try again` as generated content, and the CSS comment states that screen
readers are served by `aria-label` and the status region instead
([`index.html:864`](../index.html#L864)–[`index.html:872`](../index.html#L872)).

Focus anchors that are script-focused but never tab stops (`#lPrompt`, `#tEn`, `#rType`, `#rPl`,
`#rEn`, `#gQuestion`, and the four `*DoneTitle` headings) all carry `tabindex="-1"` **and** an
explicit `:focus{outline:none}` rule, listed per activity
([`index.html:820`](../index.html#L820)–[`index.html:838`](../index.html#L838)).

Reduced motion is handled in one block ([`index.html:986`](../index.html#L986)):
`.build-row.shake`, `.flip`, `.screen`, `.done`, `.bubble`, `.hero h1`, `.hero-badge` all lose
transition and animation.

`lang="pl"` is applied per Polish string, not per container — `#plText`, `#exPl`, `.opt` buttons in
Grammar, `#tInput`, the answer nodes inside status messages.

---

## 8. Mobile / responsive architecture

`.wrap` is `max-width:560px; padding:0 20px` ([`index.html:109`](../index.html#L109)). The app is
**built phone-first and simply centres on desktop**; there is no tablet or desktop layout.

The stylesheet contains **exactly five media queries**:

| Condition | Line | Scope |
|---|---:|---|
| `(max-width:400px)` | [890](../index.html#L890) | card/hero type scale |
| `(prefers-reduced-motion:reduce)` | [986](../index.html#L986) | motion |
| `(max-width:400px)` | [991](../index.html#L991) | drawer width, `.sbar` two-row grid, ending-table padding, card floor |
| `(max-height:600px)` | [1028](../index.html#L1028) | short viewports / landscape |
| `(max-width:360px)` | [1044](../index.html#L1044) | topic row wrap only |

[`tests/test_phase3b_mobile_layout.js`](../tests/test_phase3b_mobile_layout.js) pins this exactly:

- `A1 no extra widths were scattered across the sheet` asserts the sorted max-widths are
  **exactly `[360, 400, 400]`**;
- `A1 the two pre-existing 400px blocks are untouched in count` asserts exactly two 400px blocks;
- `A4 the narrow breakpoint changes nothing outside the topic row` asserts the 360px block's
  selector list is **exactly** `['.pill-practice', '.t-arrow', '.topic', '.topic-main']`.

[`tests/test_phase3_closeout.js`](../tests/test_phase3_closeout.js) adds:

- `A5 no rule anywhere sets overflow-x to hidden or clip`;
- `B5 only the audited selectors may break inside a word` — `overflow-wrap:anywhere` is confined to
  the card headline and the ending tables ([`index.html:553`](../index.html#L553)).

Touch targets are explicit: `.site-menu-button` and `.site-drawer-close` are 44×44
([`index.html:133`](../index.html#L133)); `.t-emoji` is 46px and the mobile test asserts it is
**not** changed at the narrow breakpoint; `.site-nav-list` rows are `min-height:52px`.

Viewport is device-width at initial scale 1 and pinch zoom is never disabled — `build_pages.py`
reads the shell's viewport and **refuses to emit** a `maximum-scale`/`user-scalable` directive
([`build_pages.py:104`](../build_pages.py#L104)).

---

## 9. Offline / cache architecture

[`sw.js`](../sw.js) declares `CACHE = "popolsku-v65"` and `AUDIO_CACHE = "popolsku-audio"`
([`sw.js:26`](../sw.js#L26)). The audio cache is deliberately versionless (content-hashed filenames);
the shell cleanup matcher is `/^popolsku-v[0-9]+$/`.

`REQUIRED_ASSETS` ([`sw.js:81`](../sw.js#L81)) is 14 entries: `./`, the four `pp-*.js` helpers, the
seven `data-*.js` files, and `audio-manifest.json`. **If any one fails to store, install fails** —
the file's comment states the reason: a half-installed shell "would claim to work offline and then
not". `OPTIONAL_ASSETS` is manifest, icons and fonts.

Routing: `DATA_FILE = /\/data-[a-z0-9-]+\.js$/` and the audio manifest get their own network-first
branches; `STATIC_ASSET_PATHS` is **derived** from the precache inventory minus those
([`sw.js:168`](../sw.js#L168)) so runtime caching can never diverge from install. Generated pages
are an **exact 32-entry inventory** (`GENERATED_PAGE_ASSETS`, [`sw.js:127`](../sw.js#L127)), with a
comment requiring the Phase 4B-2 inventory test to stay green.

`mediaGroupForPath` + `mediaTypeOf` ([`sw.js:304`](../sw.js#L304), [`sw.js:315`](../sw.js#L315))
refuse to store a `200 text/html` soft-404 under a `.js` or `.json` key.

[`tests/test_phase4b1_service_worker_cache.js`](../tests/test_phase4b1_service_worker_cache.js)
pins `A1 the app-shell cache is popolsku-v65`, `A1 the audio cache is unchanged`, and that each
constant is declared exactly once.

---

## 10. Generated-page architecture

[`build_pages.py`](../build_pages.py) owns three directories end to end
(`GENERATED_DIRS = ("grammar","vocabulary","guide")`, [`build_pages.py:84`](../build_pages.py#L84)).
It reads `data-grammar.js` and `data-b1.js` only ([`build_pages.py:60`](../build_pages.py#L60)),
via the shared parser in [`pp_audio_rule.py`](../pp_audio_rule.py). It renders **teaching content,
never drills** (`topic_page` iterates `topic["teach"]` only, [`build_pages.py:838`](../build_pages.py#L838)).

Current output: 23 grammar pages, 6 vocabulary pages, the guide hub and the listening page, and a
32-URL sitemap. `build_pages.py --check` is deterministic and `drift_report()` is asserted empty by
[`tests/test_priority7_phase2a.py`](../tests/test_priority7_phase2a.py)
(`test_generator_outputs_remain_current_and_owned_directories_contain_no_fixture`).

`data-verbs.js` is **not** an input. Adding a pattern file would have zero automatic SEO effect,
exactly as
[`priority-7-existing-content-integration-map.md`](priority-7-existing-content-integration-map.md) §5
recorded.

---

## 11. Existing Priority 7 release guards in the test suite

`DeploymentIsolationTests` in [`tests/test_priority7_phase2a.py:2976`](../tests/test_priority7_phase2a.py#L2976)
is already the enforcement mechanism for the runtime boundary. It asserts:

1. `editorial/` contains **exactly** `verb-pattern-candidates.json` and
   `priority-7-authoring-context.json`, and any other file fails closed;
2. `content/verb-patterns.json` **does not exist**;
3. no marker path and no `editorial/` prefix appears in `index.html`, `sw.js`, `sitemap.xml`, or
   any generated page;
4. the `<script src="…">` list in `index.html` is **exactly** the eleven current entries, in order;
5. the `data-*.js` glob is **exactly** the seven current files;
6. the sitemap has exactly 32 URLs;
7. `git diff --exit-code f6bdc73a…` over a 30-entry protected surface list (`index.html`, `sw.js`,
   every data file, every generated directory, the audio tree, the icons) is empty.

**Consequence for Phase 3B.** Assertions 4 and 7 mean that adding `pp-verb-patterns.js` to
`index.html` will *deliberately fail* this suite. That is the guard working as designed: the test
must be amended in the same reviewed slice that adds the loader, never quietly.

---

## 12. Priority 7 corpus shape, as it exists today

Computed directly from [`editorial/verb-pattern-candidates.json`](../editorial/verb-pattern-candidates.json)
at this tree. Reported here because the UX must fit *this* data, not a hypothetical corpus.

| Dimension | Value |
|---|---|
| Envelope | `artifactStatus: priority-7-editorial-nonproduction`, `formatVersion: 1` |
| Lemmas / meanings / patterns | 30 / 34 / 45 |
| `reviewState` | **`research` × 45** |
| `reviewEvents` | **empty on all 45** |
| `activityEligibility` | **empty on all 45** |
| Examples | 23, all `origin.kind: repository-reuse`; **22 patterns have none** |
| `audioEligible: true` | 0 |
| Complements per pattern | 36 single, 9 double |
| Complement types | 31 `case`, 20 `preposition-case`, 2 `infinitive`, 1 `clause` |
| Case occurrences | accusative 19, dative 9, instrumental 9, genitive 8, locative 5, nominative 1 |
| Preposition+case combos | `o`+Acc ×6, `za`+Acc ×3, `o`+Loc ×3, `z`+Instr ×2, then `w`+Loc, `na`+Acc, `za`+Instr, `w`+Acc, `od`+Gen, `na`+Loc ×1 |
| Relation types | 42 `lexical-frame`, 1 `means-method` (`płacić`), 1 `constructional-frame` (`być`), 1 `subject-experiencer` (`podobać się`) |
| Teaching status | 39 `active-production`, 6 `recognition-only` |
| CEFR recognition | A1 16, A2 18, B1 11 |
| Recognition ≠ production | 15 patterns; 6 have no `production` at all (the recognition-only set) |
| Lemmas with >1 meaning | `słuchać`, `bać się`, `zajmować się`, `zależeć` |
| Meanings with >1 pattern | 10, up to 3 (`rozmawiać`) |
| `contentRefs` | 101 total; every pattern has ≥1 |
| `errorNotes` | 24, all `predicted-distractor` |
| `questionOverridePl` | 0 — every question is centrally derivable |

The runtime projection contract in [`priority7_tooling.py:2332`](../priority7_tooling.py#L2332)
emits per pattern: `id`, `relationType`, `complements`, `cefr`, `teachingStatus`, `usage`,
`learnerExplanationEn`, `activityEligibility`, optional `aspectEquivalentPatternIds`, `examples`
(`id`/`pl`/`en`/`audioEligible` only), `contentRefs`, `errorNotes`. Meaning level emits `id`,
`glossesEn`, `patterns`. Lemma level emits `id`, `canonicalLemma`, `reflexive`, `aspect`, optional
`displayLemma`, optional `aspectPartnerIds`.

**It emits no case name, no Polish case name and no diagnostic question.** Those are central
consumer metadata by Phase 1 design ("Questions derive for direct and prepositional complements"),
and `PRIVATE_RUNTIME_KEYS` ([`priority7_tooling.py:99`](../priority7_tooling.py#L99)) recursively
rejects `key`, `internalScope`, `evidence`, `reviewState`, `reviewEvents`, `origin`,
`repositorySource` and 20 more from any runtime document.

---

## 13. Audit conclusions

1. **The app already has the extension mechanism Priority 7 needs.** Synthesized levels
   (`LEVELS.push`) plus derived categories (`categoryOf`) plus one dispatch switch (`routeTopic`)
   is exactly how Type It and Listening were added, and a `group:"grammar"` level joins the Grammar
   tab with no engine edit.
2. **Verb government is already taught, badly located.** All seven case topics name verb triggers in
   prose; `szukać + Genitive` already has a card hint, a build drill and an explanation. What is
   missing is not content but a **lemma-first index** and a consistent visual grammar.
3. **The card schema cannot absorb pattern data.** `CARD_FIELDS` is closed, so the Priority 7
   one-way `contentRef` model is not a stylistic preference — it is the only shape the repository
   permits without a content-schema change.
4. **Default-deny already ships.** `PP_USAGE.eligibleFor` fails closed on unknown activities, and
   `poolFor` defaults to the production-safe reading. The locked `activityEligibility` allowlist
   maps onto an existing, tested idiom rather than a new concept.
5. **Three renderers are `innerHTML`-based** (`gRenderTeach`, `gRenderChoose`, `gChooseFeedback`)
   and are safe only because their inputs are hand-authored committed markup. Generated runtime
   strings must not be routed through them.
6. **The accessibility layer is shared and complete enough to reuse wholesale.** Any new surface
   that uses `ppFocusActivityTarget`, `ppSetActivityStatus` and `ppScreenEntryTarget` inherits the
   contracts the existing JXA suites already enforce.
7. **The CSS is pinned tighter than it looks.** New breakpoints are forbidden by an existing test;
   `overflow-x:hidden` is forbidden; word-breaking is confined to two audited selectors. Any
   pattern layout must be fluid at 320px inside a 560px column with no new media query width.
8. **The offline story is atomic or nothing.** A required asset that fails to store fails the whole
   install, and the runtime allowlist is derived from the precache list, so a pattern file is
   either fully wired (precache + network-first + media type + inventory test + shell bump) or
   must not exist.
9. **The Phase 2A deployment tests are the release guard and will fail loudly** when a loader is
   added. That is correct behaviour and must be treated as an approval gate, not an obstacle.
10. **No learner-facing Priority 7 content is currently possible.** All 45 patterns are `research`,
    all `activityEligibility` arrays are empty, and 22 patterns have no example. Verified at this
    tree: `validate_editorial` over the committed corpus with the committed authoring context
    returns **0 issues**, and `project_runtime_nonrelease(document, 1, context)` then raises
    `PROJECTION_EMPTY $.lemmas: No current approved active/recognition pattern can be projected.`
    The corpus is structurally sound *and* mechanically unprojectable. Phase 3B therefore cannot be
    fed by the real corpus even accidentally — the projector itself is the guard.
