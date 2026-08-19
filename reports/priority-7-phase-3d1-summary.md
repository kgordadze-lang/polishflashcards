# Priority 7 — Phase 3D-1 Summary

**Phase:** 3D-1 — synthetic **grammar-choose mechanics prototype**.
**This is not Priority 7 exercise integration.** Nothing here is authored content, nothing here was
reviewed, nothing here is authorized to reach a learner, and no statement in it is a claim about
Polish. All 45 real patterns remain `research`, every real `activityEligibility` array remains empty,
and **Phase 3D-2 remains blocked** on the prerequisites listed in §16.

The phase answers one engineering question by building: *can the existing Grammar `choose` mechanics
carry a future verb-pattern practice item cleanly, accessibly, and without a second activity engine?*
**Answer: yes** — through a narrow adapter and three narrow extension points. §3 records the audit
that decision rests on.

**Three correction passes applied (§21).** The first candidate reused the authored Grammar
*retry-until-correct* mechanic on a miss, which is not the incorrect flow this phase requires; an
independent review then returned `NO-GO` on a completion sentence that could claim an uncleared retry
had been cleared, uniqueness checks that `__proto__` and whitespace-only strings walked past, and
language-of-parts errors in both directions; a second verification pass found two remaining issues —
recognised *optional* fields still read through the prototype chain, and a settled mixed option
flattened into one `aria-label` that discarded its language segmentation. **Everything below describes
the corrected state**, and §21 records what each pass changed. The retry mechanic, the authored markup
path and every accepted architectural property are retained unchanged.

---

## 1. Baseline

Verified before any file was opened for writing, all matching the expected values:

| Check | Expected | Verified |
|---|---|---|
| Branch | `priority-7-phase-3d1-synthetic-activity` | ✅ |
| HEAD | `e19bb3ccad8f7bac72927f345a14ca6954ac9074` | ✅ |
| Tree | `802803615f33692f6708fe832527fab0a2b7e097` | ✅ |
| Git remotes | none | ✅ zero |
| `push.default` | `nothing` | ✅ |
| Starting worktree | clean | ✅ |

Baseline test state was recorded before editing, so every later result is attributable to this phase:
**293 Python tests OK**; **33 JXA suites, 10,078 assertions, 0 failed** — identical to the totals
Phase 3C recorded.

## 2. Authoritative design read first

All five approved Phase 3A reports in full; `reports/priority-7-phase-3b-summary.md` and
`reports/priority-7-phase-3c-summary.md`; `pp-verb-patterns.js`; the Phase 3B/3C Priority 7 suites
(`tests/test_priority7_patterns_ui.js`, `tests/test_priority7_phase3b.py`,
`tests/test_priority7_phase3c.py`); the Grammar activity implementation in `index.html`
(`startGrammar`, `gStartPractice`, `gRenderDrill`, `gRenderChoose`, `gChooseFeedback`,
`gDrillAdvance`, `gShowDone` and the `G` state object); the shared accessibility and focus helpers
(`ppFocusActivityTarget`, `ppSetActivityStatus`, `ppSetActivityOptionState`, `ppScreenEntryTarget`,
`ppRouteScreenFocus`, `ppScreenReturnTargets`); `tests/test_grammar_interaction.js`,
`tests/test_phase3b_mobile_layout.js` and `tests/test_phase3_closeout.js`; and the locked Phase 1/2A
`activityEligibility` and future-exercise-ID architecture
(`priority-7-activity-eligibility-specification.md`, `priority-7-stable-id-specification.md`).
Both `editorial/*.json` files were read **read-only**.

## 3. Grammar `choose` engine audit

What `gRenderChoose` actually expects today, verified at this tree:

| Concern | Shipping behaviour before this phase |
|---|---|
| Drill shape | `{type:"choose", prompt, promptEn, options[], answer, full, fullEn, explain, _case?}` |
| Card construction | one `innerHTML` assignment interpolating `prompt`, `promptEn` and `_case` |
| Prompt blank | `c.prompt.replace("___", '<span class="blank"></span>')` |
| Options | `document.createElement("button")` + `textContent`, `data-val`, `aria-pressed`, `lang="pl"` |
| Scoring | `btn.getAttribute("data-val") === c.answer` — i.e. **the displayed string is the key** |
| Feedback | `gChooseFeedback` — one `innerHTML` assignment plus a `data-say` audio control |
| Progression | `G.queue` + `G.di`, requeue-once in `gDrillAdvance`, `gShowDone` scoring originals only |
| Focus | prompt on render, next available option after a miss, `#gDrillNext` after a hit |
| Announcements | `#gStatus` via `ppSetActivityStatus`, text nodes only |
| Persistence | **none** — no `rRecord`, no storage, no schema; `G` is in-memory session state |
| Unknown drill type | `gRenderDrill` routes anything that is not `choose` to **build** (latent, see §15) |

Four of these are incompatible with what a verb-pattern item needs, and only four:

1. **`innerHTML` over drill strings.** Authored drills are hand-written committed markup and 22 of
   them use it deliberately (`explain` carries `<b>`). Runtime text is data and must never be parsed
   as markup.
2. **Scoring on displayed text.** Two structural options may legitimately read the same — the fixture
   has exactly that case — so the words on the button cannot be the answer key.
3. **Retry-until-correct on a miss.** The authored mechanic disables only the chosen option and
   invites another attempt, keeping the answer hidden. That is right for inflected forms, where the
   remaining options each still cost a decision. It is wrong for a small set of *structures*:
   eliminating two of three hands over the answer without a second decision being made, scores
   identically either way, and delays the explanation — which is the part that teaches.
4. **A practice set with no lesson.** Back and `Review the lesson` both assume `topic.teach`.
5. **One language per string.** Every drill string is announced and rendered as a single language -
   options as `lang="pl"`, everything else as the document's English. A structural label is neither:
   `kogo? co? · Accusative` is Polish, a separator, then English, and both uniform answers are wrong
   about half of it. *(Found by the independent review; §12.)*
6. **A completion sentence that assumed the retry mechanic.** `… came back for a second pass and you
   cleared it` was always true while a drill could only advance by being answered correctly. Under
   `revealOnIncorrect` a requeued item can be missed again, and the sentence became capable of being
   false. *(Found by the independent review; §9.)*

Everything else — progression, requeue-once, option rendering, selected/correct/incorrect states, the
feedback region, Next, keyboard behaviour, focus, the status region and the completion panel — is
reusable **unchanged**.

## 4. Reuse decision

> **Reuse. One narrow adapter into the existing engine, plus three narrow, generic extension points
> in that engine. No new activity system, no second renderer, no second queue, no second screen and
> no parallel accessibility framework was created.**

Reuse was never close to impossible, so the §3 stop-and-document path was not entered. All three
extension points are **optional drill properties, read from the drill and never from the corpus** —
generic, not Priority 7 shaped. The generic answer handler contains no `priority7`, `PP_VERB_PATTERNS`,
`patternRef`, `exerciseId`, `vp-` or `p7-fixture` reference of any kind, asserted at source:

- **`c.textOnly`** — "every string in this drill is data". Its card and its feedback are built with
  `createElement` + `textContent` only. Authored drills carry no such flag and take the byte-identical
  markup path they always took.
- **`{value, label}` options** — an option may carry an explicit stable identity beside its label. A
  plain string option answers `gOptionValue` / `gOptionLabel` / `gOptionLang` exactly as before.
- **`c.revealOnIncorrect`** — "the first choice is the attempt". On a miss the drill marks what was
  chosen, identifies the correct option, closes every option, shows the feedback it would have shown
  anyway and hands over to Next, instead of inviting another guess. A drill without the property gets
  the retry mechanic, which is every drill in `data-grammar.js`.

- **Language fragments** — any drill string may be a plain string (one language, every authored
  drill) *or* an array of `{text, lang}` fragments. One function turns fragments into DOM, and the
  visible option, the prompt, the revealed answer, the feedback and the `#gStatus` announcement all
  go through it, so the same string cannot end up segmented two ways in two places.

Plus one guard, `gHasLesson()`, so a practice set with no lesson offers no control that would open an
empty one, and one derived summary, `gRetryOutcome()`, so the completion sentence describes what
actually happened to the drills that came back. Every topic in `data-grammar.js` has a lesson and
carries no fragment, so both answer exactly as they always did.

**Proof that authored Grammar is unchanged:** `tests/test_grammar_interaction.js` — 612 assertions
over exactly this path, including its own markup-parsing fake DOM — passes with **no assertion
altered or removed**, and gained 4 additive ones pinning the opt-in boundary (616 total). The
authored choose path was additionally driven live in the browser and still shows `✕ Try again`, keeps
the other options enabled, keeps the answer hidden and keeps `G.state === "ask"` (§19).

## 5. Files changed

**Added (4)**

| File | What it is |
|---|---|
| `tests/fixtures/priority7/exercise-fixture.json` | the wrapped, explicitly non-release synthetic choose fixture — 10 items (§6) |
| `tests/test_priority7_choose_ui.js` | adapter, mechanics, retry outcomes, validation hardening, own-property contract, language of parts, settled accessible names, feedback, injection safety, layout — 327 assertions |
| `tests/test_priority7_phase3d1.py` | fixture identity, language contract, stable-ID space, harness boundary, startup, validation hardening, persistence, release boundary — 44 tests |
| `reports/priority-7-phase-3d1-summary.md` | this report |

**Modified (6)**

| File | Change |
|---|---|
| `pp-verb-patterns.js` | the pure mechanics adapter: `grammarChooseDrill`, `grammarChooseDrills`, `validChooseOption`, `usableId`, `CHOOSE_ACTIVITY`, `CHOOSE_INSTRUCTION`, `RESERVED_ID_PREFIX`, the `revealOnIncorrect` emission, four exports; plus the hardening — `isFilledString`, `emptyDict` / `seenBefore`, and the `validTextFragment` / `validTextValue` / `copyTextValue` language model |
| `index.html` | `gOptionValue` / `gOptionLabel` / `gOptionLang`; `gTextEl` / `gAppendDrillText` / `gPaintChooseText` / `gPaintChooseFeedbackText`; the `textOnly` branch in `gRenderChoose` and `gChooseFeedback`; `gAnnounceRevealed` and `gRevealChooseAnswer` with the one-line opt-in branch that calls it; the one `.opts.revealed .opt.wrong::after` CSS override; `gHasLesson` and its two call sites (`gBack`, `gShowDone`); `pStartChoosePractice`; plus the review corrections — the `gTextFragments` / `gFragmentText` / `gAppendFragment` / `gAppendTextParts` / `gChooseOptionLabel` language model, and `G.cleared` with `gRetryOutcome` / `gDoneMessage` |
| `tests/test_priority7_phase2a.py` | two deliberate amendments (§15); the enumerated-removal list grew to 30 lines in three groups |
| `tests/test_priority7_phase3b.py` | one deliberate amendment (§15) |
| `tests/test_priority7_phase3c.py` | one deliberate amendment (§15) |
| `tests/test_grammar_interaction.js` | `GNAMES` + 18 extraction names, and 4 **additive** assertions; **no assertion altered or removed** (§15) |

**Fixture:** modified once, in the independent-review pass, to carry explicit `{text, lang}` language
metadata (§15 deviation 5). Its wrapper, non-release markers, ten mechanics shapes, test-only
identifiers and answer positions are unchanged.

**CSS:** exactly one rule was added, in the first correction pass —
`.opts.revealed .opt.wrong::after{content:"✕ Incorrect"}`. It is a more specific override of an
existing rule, needed because a revealed answer makes the base rule's `✕ Try again` untrue; the two
base rules are byte-identical and every suite that pins them (`test_listening_accessibility.js`,
`test_mixed_accessibility.js`, `test_phase1a_accessibility.js`) is green. No new selector class, no
new media query, no new breakpoint.

**Not touched, verified byte-identical by `git diff --exit-code`:** `sw.js`, all seven `data-*.js`,
`validate_content.py`, `build_pages.py`, `priority7_tooling.py`, `pp-migrate.js`, `pp-usage.js`,
`pp-answer.js`, `pp-distractor.js`, `editorial/` (both files),
`tests/fixtures/priority7/runtime-fixture.json`, `audio-manifest.json`, `sitemap.xml`,
`manifest.json`, `robots.txt`, `grammar/`, `vocabulary/`, `guide/`, `audio/`, and every pre-existing
report. The data path reuses `.d-type`, `.q-prompt`, `.blank`, `.q-en`, `.opts`, `.opt`, `.fb-box`,
`.fb-good`, `.fb-explain` exactly as they already exist.

## 6. Synthetic exercise fixture design

`tests/fixtures/priority7/exercise-fixture.json`, 12 KB, one file, hand-written and wrapped:

```json
{ "artifactStatus": "priority-7-exercise-fixture-synthetic-nonrelease",
  "releaseAuthorized": false,
  "fixtureNotice": "SYNTHETIC-NONRELEASE: …",
  "syntheticExercises": { "fixtureFormat": 1, "items": [ … 10 … ] } }
```

**The record shape — the smallest that renders and scores an item, and nothing else:**

```
exerciseId           test-only identity
patternRef           the owning synthetic pattern, as an OPAQUE STRING
activityType         "grammar-choose"
order                explicit authored sequence
prompt               learner-facing, may contain "___"
promptEn?            learner-facing gloss
cue?                 optional short learner-facing cue
options[]            { value, label } — explicit identity beside the words
answerValue          the value of the one intended option
feedbackStructure    the correct structural pattern
feedbackExplanation  one short learner-facing explanation
```

No runtime pattern object is duplicated into an item: `patternRef` is a string the adapter never
resolves. No private Priority 7 evidence or review metadata is present at any depth (asserted against
`PRIVATE_RUNTIME_KEYS`). No release-authorization semantics exist in the record at all.

**Why hand-written rather than regenerated through `project-fixture`.** The Phase 3A slice sketch
assumed exercise records could be added to the synthetic editorial document and regenerated. They
cannot at this tree: `priority7_tooling.py`'s runtime projector emits no exercise entity, and
`priority7_tooling.py` is on the Phase 3A §A10 must-not-change list. Recorded as a deviation (§15).

**Coverage — the ten required shapes, in ten items:**

| # | Shape | Item |
|---|---|---|
| 1 | simple single-case choice | `…choose-01-single-case` |
| 2 | preposition + case | `…choose-02-preposition-case` |
| 3 | two options, same case, different structures | `…choose-03-same-case-two-structures` |
| 4 | multi-complement frame | `…choose-04-multi-complement` |
| 5 | infinitive vs nominal complement | `…choose-05-infinitive-vs-nominal` |
| 6 | clause vs nominal complement | `…choose-06-clause-vs-nominal` |
| 7 | lexical `się` | `…choose-07-lexical-sie` |
| 8 | recognition-only synthetic pattern | `…choose-08-recognition-shaped` |
| 9 | hostile learner-facing text | `…choose-09-hostile-text` |
| 10 | long mobile-wrapping text | `…choose-10-long-wrapping-text` |

Every verb is invented (the Phase 3B `fikcjonować` family), every explanation carries the
`SYNTHETIC-NONRELEASE` marker, and a mechanical anti-leak test proves no real canonical lemma, id,
learner explanation, example or gloss appears anywhere in the file. Option **labels** deliberately
quote the app's own central chip vocabulary (`kogo? czego? · Genitive`, `+ bezokolicznik ·
Infinitive`), which is committed shipping code in `pp-verb-patterns.js`, not corpus content — so no
new linguistic claim is made by reusing it beside invented verbs.

Item 8 is *recognition-shaped* only in its learner-facing cue. Recognition/production semantics are
deliberately **not** modelled: they are a property of a real approval decision, and the adapter must
not be able to infer anything from them (§10).

**Identifier convention.** The repository's existing fixture contract already uses `p7-fixture-…`
(`tests/test_priority7_phase2a.py`, `tests/test_priority7_patterns_ui.js`), so this phase extends it:
`p7-fixture-x-choose-<shape>` for exercises, `p7-fixture-pattern-<shape>` for the owning references.
These identifiers **cannot be mistaken for or reused as release identities** — asserted three ways:
every one starts with the test prefix; none matches the release shape `vp-<family>-<stem>-<12 hex>`;
and `vp-x-…` appears in no shipping file, no projection, no corpus and no registry. Nothing entered a
frozen allocation, a tombstone record or an editorial candidate.

## 7. Adapter design

`PP_VERB_PATTERNS.grammarChooseDrill(item)` and `.grammarChooseDrills(items)` — pure, no DOM, no
storage, no network, no parse.

**What it decides:** whether a record is structurally usable as a choose item, and what its mechanics
are. It maps the record onto the engine's own drill vocabulary and stops.

**What it does not decide, and cannot:** whether the owning pattern may be practised. It never reads a
pattern, an allowlist, a teaching status, a CEFR level, a content reference or the surface's
visibility — asserted at source (`STATE`, `eligibleFor`, `activityEligibility`, `teachingStatus`,
`cefr`, `contentRefs`, `api.available` all occur **zero** times in the adapter) and behaviourally (its
output is byte-identical with and without accepted pattern data, and running it moves no eligibility
answer in either direction).

**Fail-closed, per item → `null`:** not a plain object; any `PRIVATE_RUNTIME_KEYS` member at any
depth; an unknown key; `activityType !== "grammar-choose"` (including `"grammar-Choose"`,
`"grammar-build"`, `"type-it"`, absent, non-string); an identifier in the reserved `vp-` space; a
non-positive-integer `order`; a blank prompt, structure line or explanation; fewer than two options;
an option that is not a `{value,label}` pair or carries an extra field; **duplicate option
identities**; and an `answerValue` matching zero or more than one option.

**Fail-closed, per set → `null`:** an empty or non-array input, **any** invalid item, a duplicate
`exerciseId`, or a duplicate `order`. This is deliberately stricter than the reference surface's
per-entity pruning: a reference list can drop one bad record and stay honest, a **scored** round
cannot — a set that quietly ran four of five items would report a total nobody wrote.

The set is sorted by explicit `order`, so the sequence never depends on arrival order. The adapter
contains no `Math.random`, no shuffle, no `||` default and no normalisation: it never repairs, guesses
or invents an answer.

**Fail-closed means fail-closed — the two ways it did not, and now does.**

- **Uniqueness cannot be talked out of its own invariant.** The option-value, exercise-id and order
  sets were ordinary `{}` objects. `dict["__proto__"] = true` does not create an own property — it
  invokes the inherited setter — so two records that both used that exact string each reported "not
  seen yet" and the duplicate was accepted. They are now `Object.create(null)` dictionaries written
  and read through one `seenBefore()` helper, so the invariant holds for **arbitrary** strings rather
  than for a blacklist of the ones somebody remembered. No prototype pollution was ever observed; the
  defect was that uniqueness validation could be defeated.
- **Blank-looking text is malformed text.** Required fields used `isNonEmptyString`, which accepts
  `" "`. They now use `isFilledString` (non-empty **and** containing a non-space), applied to
  `exerciseId`, `patternRef`, `prompt`, `answerValue`, `feedbackStructure`, `feedbackExplanation`,
  every option `value` and `label`, and — deliberately — to `promptEn` and `cue` when those optional
  fields are *present*: a blank optional string is a malformed record, not an absent field. The record
  is **rejected**, never trimmed and accepted; nothing the adapter is handed is mutated, and the
  fragments it emits are copies.

- **A record is exactly its own properties — optional fields included.** Required fields were already
  own-checked (`closedKeys` reads through `hasOwnProperty`), but *recognised optional* fields were
  tested with `in`, which answers for the prototype chain: an inherited `promptEn`, `cue` or fragment
  `lang` counted as supplied, and reading it afterwards **executed an inherited getter** — somebody
  else's code, run during validation. Every such check now goes through one `hasOwn()` helper, so an
  inherited recognised field is ignored and its getter is never touched, not even to ask whether it is
  there. `copyTextValue` reads a fragment's language only when the fragment owns one, so what reaches
  the renderer is an ordinary object with no prototype behaviour left in it.

**The plain-object check was reviewed and deliberately left alone.** `isPlainObject` still accepts any
non-array object, and with the own-property rule above that is now the whole story: every recognised
field — required or optional — must be an **own** property, every value is separately type-checked,
and nothing in the adapter reads an inherited member, so an object carrying a prototype behaves
identically to the JSON object the harness supplies. Tests pin the reasoning rather than leaving it as
prose: an object whose keys are all *inherited* fails closed; a required field that exists only on a
prototype satisfies nothing; an inherited private key is neither read nor able to smuggle a field past
the check, while an **own** private key still refuses the record whole; and inherited optional getters
— counting ones and throwing ones — are proven never to run.

**The three drill properties it emits.** `type:"choose"` (the engine's own vocabulary),
`textOnly: true` (every string arrived as data), and `revealOnIncorrect: true` (one choice is the
attempt). The third is a *mechanics* decision the adapter is entitled to make and states plainly:
these options are structures rather than inflected forms and the set is small, so eliminating the
remainder would hand over the answer without a second decision being made and would score identically
either way. It is emitted unconditionally for every synthetic choose item, and it is the only place in
the repository that turns the property on.

**Language travels with the text, not with the consumer.** `prompt`, `feedbackStructure` and every
option `label` are validated and passed through as `{text, lang}` fragments; `promptEn`, `cue` and
`feedbackExplanation` stay plain English strings. The adapter never derives a language — no splitting
on a separator, no "a prompt is Polish" assumption — because deriving one would be the adapter
inventing a linguistic claim, which is the one thing §7 says it must never do. The record declares
its own languages because the record is where they are known.

## 8. Harness boundary

```
tests/fixtures/priority7/exercise-fixture.json      ← wrapped; unusable by the adapter
        │  read by the TEST HARNESS only
        ▼
  harness asserts: artifactStatus === "priority-7-exercise-fixture-synthetic-nonrelease"
                   releaseAuthorized === false
                   every identifier is test-scoped and outside the reserved family
        │  harness reads .syntheticExercises.items  ← explicit, deliberate, test-only
        ▼
  PP_VERB_PATTERNS.grammarChooseDrills(items)  →  the SHIPPING Grammar choose engine
```

Four properties make this safe, and each is tested:

1. **The shipping app has no path to the file.** `index.html` contains zero occurrences of `"tests/`,
   `'tests/`, `fixture`, `exercise-fixture`, `syntheticExercises`, `releaseAuthorized`,
   `artifactStatus`, `URLSearchParams`, `searchParams`, `loadFixture` or `devMenu`, and its
   `fetch(` count is still **2** (the pre-existing audio manifest and freshness HEAD).
2. **The unwrap is an assertion, not a convenience.** Five tampering cases — missing wrapper, missing
   marker, the *runtime* fixture's marker, `releaseAuthorized: true`, `releaseAuthorized: "false"` —
   each make the harness throw. Two more prove it refuses an identifier in the reserved family or one
   that is not test-scoped.
3. **The adapter refuses the wrapper whole.** `artifactStatus` is a `PRIVATE_RUNTIME_KEYS` member, so
   feeding the wrapped document, or the payload envelope, or a runtime pattern record, all return
   `null`. The refusal is load-bearing, exactly as in Phase 3B.
4. **The two paths are mechanically distinguishable.** `acceptRuntimeDocument` (shipping pattern
   data), `__acceptForTest` (test-only injection, absent from `index.html`) and `grammarChooseDrills`
   (already-unwrapped records only) are three separate, separately named entry points.

**No shipping entry point exists.** `pStartChoosePractice` is defined exactly **once** in
`index.html` and invoked **nowhere** — no tile, no pill, no level, no route branch, no lemma-entry
affordance, no query parameter, no storage flag, no developer menu. It exists so the tests drive the
shipping adapter and the shipping engine rather than a parallel copy of either.

## 9. Choice and feedback mechanics

Learner flow, exercised end to end: synthetic prompt → choose a structural option → immediate
feedback → Next → next item → completion.

- **Prompt.** `Choose the pattern` (+ optional cue) → the prompt with its `___` rendered as a real
  `.blank` element → the English gloss. Same ids, same classes, same reading order and the same
  option container as an authored drill, so `#gInstruction`, `#gQuestion`, `#gQuestionMeaning`,
  `.opts` and `#gFbBox` all mean exactly what they already meant to the focus helpers, the status
  region and the stylesheet.
- **Correct.** Option marked `correct`, accessible name `…, correct`, every option disabled, one
  option left `aria-pressed="true"`, feedback revealed, Next enabled and focused, status reads
  `Correct. The answer is … Next is ready.` Unchanged by the correction pass.
- **Incorrect — the corrected flow.** *One choice is the attempt.* In order: the chosen option is
  marked `wrong` with the accessible name `…, incorrect` (**no** "Try again" — there is nothing left
  to try); the correct option is marked `correct` with the accessible name `…, correct answer` and
  `aria-pressed="false"`, so it is identified without being credited to the learner; the option row
  enters the `revealed` state so the chosen option's visible words read `✕ Incorrect` rather than
  `✕ Try again`; **every** option is disabled; the feedback region is revealed with the correct
  structural pattern and the explanation; Next is enabled and takes focus; and the status announces
  it all once: `… is not correct. The answer is … Explanation available below. Next is ready.`
  The learner is **not** made to click an answer they have already been shown, and **cannot**
  brute-force the remaining options — clicking every one of them afterwards changes nothing at all,
  measured both in the suite and live.
- **The item still comes back.** The miss is banked *before* the reveal runs, so `gDrillAdvance`'s
  existing requeue-once rule is untouched: a 3-item set with one miss becomes a 4-item queue whose
  fourth entry is the same `exerciseId` carrying `_requeue`, the retry presentation opens fresh with
  nothing revealed, and the retry is still excluded from the score. The correction changes what one
  *presentation* does, never what a *round* does.
- **And the completion sentence now says what became of it.** A requeued item that is missed *again*
  ends the round without a third attempt — correctly — but the old copy still read `… came back for a
  second pass and you cleared it`, which was false. `G.results` cannot tell those apart: it records
  *right first try*, which is the scoring question, and reads `false` for a retry that was eventually
  found as well as for one that never was. A second in-memory array, `G.cleared`, records the other
  question — did this presentation end on the right answer — and `gRetryOutcome()` derives the summary
  from it and from the `_requeue` entries:

  | Outcome | Copy |
  |---|---|
  | no misses | `Every answer right on the first try. This is clicking.` |
  | every retry cleared | `… 1 drill came back for a second pass and you cleared it.` |
  | no retry cleared | `… 1 drill came back for a second pass and still needs practice.` |
  | some cleared | `… 3 drills came back for a second pass and you cleared 2 of them.` |

  Scoring, the denominator, the requeue-once policy and queue semantics are untouched; only the
  sentence changed. **Every authored round reports exactly what it always reported**, because under
  the retry mechanic nothing advances a drill except answering it correctly, so every authored
  presentation is cleared and the second row is always the one that applies. An unrecorded outcome
  also still reads as cleared, so no other caller's behaviour moved.
- **Explicit identity.** An item whose two options carry **identical labels** and different values
  scores correctly in both directions; reversing the presented order does not move the answer; and
  the reveal marks the right one of the two twins — proof that the reveal resolves the answer by
  identity, not by matching text. Option order is never the scoring key.
- **Feedback.** Proves the four required states: correct, incorrect, **the correct structural
  pattern** (`metodowac + komu? czemu? · Dative + w kim? w czym? · Locative`) and one short
  learner-facing explanation. A miss and a hit now show **byte-identical feedback**, so the learner
  who missed is not told less than the one who did not. **No audio control and no `data-say`** — a
  generated item has no clip and must not offer one. No predicted-distractor pedagogy, and the real
  Priority 7 `predicted-distractor` notes are not consumed.
- **Progression.** The existing queue, the existing requeue-once, the existing `Next` /
  `See results` labelling, and the existing completion panel. Measured end to end: a 3-item set with
  one miss becomes a 4-item queue, scores **2 / 3**, and the retry is excluded from the score.
- **End state.** `Brawo!` + the score ring + `Practice again` + `Back to topics`. `Review the lesson`
  is hidden (no lesson), the pattern continuation is hidden (no case topic), the status region is
  cleared, and the completion copy contains none of *master / saved / progress / unlock / approved /
  release*.

## 10. Default-deny activity eligibility

No real pattern became eligible for anything. The adapter cannot make one eligible: it never reads
`activityEligibility` and has no writer for it (`activityEligibility.push`, `eligibility =`,
`markEligible`, `allowActivity` all absent). `eligibleFor` is unchanged and still fails closed on an
empty allowlist, an unknown activity, a non-array, and a `recognition-only` pattern requesting a
production activity. Running the adapter over the whole synthetic set leaves both a closed allowlist
(`false`) and an open one (`true`) answering exactly as they did before.

**Harness authorization is not activity eligibility, and this phase claims no eligibility for
anything.** Future real integration still requires explicit approved exercise records and allowlisting
under the locked architecture.

## 11. Persistent-progress isolation

- `popolsku-progress-v2` is **byte-identical** across a full round: 92 bytes before, 92 bytes after,
  measured live in the browser.
- The storage key set is unchanged (exactly `popolsku-progress-v2`); `sessionStorage` is empty;
  `document.cookie` is empty.
- No `rRecord`, `localStorage`, `sessionStorage`, `indexedDB`, `saveV2`, `loadV2` or `persistProgress`
  occurs in the practice entry, in the adapter, or in **any** of the 22 Grammar functions on the
  choose path — swept in both suites.
- No mastery, completion or strength concept exists: `patternMastery`, `patternProgress`,
  `completedPatterns`, `patternStrength`, `masteredPatterns` occur nowhere.
- `schemaVersion` is `2` and `CONTENT_MIGRATION_REVISION` is `2`; `pp-migrate.js` is byte-identical.
- The whole JXA round runs in an environment with **no storage object in scope at all**.
- Session-local state is `G` only — the same in-memory object every other activity uses. A refresh
  discards the round, which is the intended behaviour.

## 12. Accessibility and mobile

**Reused wholesale, never re-implemented:** `ppFocusActivityTarget` for every focus move,
`ppSetActivityStatus` for the one announcement region, `ppSetActivityOptionState` for the selected
state, `ppScreenEntryTarget` / `ppRouteScreenFocus` / `ppScreenReturnTargets` for entry and return.
No parallel accessibility framework was created.

| Check | Result |
|---|---|
| Keyboard activation of every option | native `<button>`, no key handler of its own, so Enter and Space activate |
| One clear selected state | `aria-pressed` on every option; exactly one `"true"` after an answer |
| Correct / incorrect announced | one `sr-only role="status" aria-live="polite" aria-atomic="true"` region, written as text only; the reveal is **one atomic announcement** carrying both the chosen option and the answer, never two racing ones |
| Feedback reading order | instruction → prompt → gloss → options → feedback (`.fb-good` then `.fb-explain`), asserted as the card's child order — so the structure and the explanation follow the verdict |
| Next focus | focus moves to `#gDrillNext` on a correct answer **and on a revealed miss** |
| No answer by colour alone | three independent non-visual carriers on the revealed path: the chosen option's accessible name (`…, incorrect`), the correct option's (`…, correct answer`), and the status text; the visible words `✓ CORRECT` / `✕ INCORRECT` are a fourth, and colour is never one of them |
| Settled name, mixed option | the verdict is **appended as visually hidden text inside the button**, so the name stays computed from the language-tagged children; **no `aria-label`** is set, because one would replace that computed name with a flat string and discard the segmentation |
| Settled name, string option | keeps the `aria-label` it has always had — one language, so flattening loses nothing |
| Revealed ≠ chosen | the revealed answer keeps `aria-pressed="false"` and says `correct answer`; the learner's own wrong choice keeps `aria-pressed="true"` and says `incorrect` |
| Disabled states | every option disabled once settled — after a hit **and** after a miss — each still carrying its accessible name; nothing focusable is left behind the answer |
| Touch targets | options ≥ **48px** high at 320/375/768/1280; Next **280 × 48** at 320px |
| Screen entry focus | `#gQuestion` (the prompt heading, `tabindex="-1"`), deferred via `show("grammar", true)` |
| Return focus | Back from a lesson-less round leaves for home and refocuses the invoking `.topic-main` through the existing `ppScreenReturnTargets` path |
| Language of parts | every string is marked as what it actually is — see below |
| Focus never on `<body>` | asserted through a whole item, including after a miss |

**Language of parts.** The document is English. Measured live, in the DOM:

| Element | Result |
|---|---|
| Prompt `#gQuestion` | no `lang` on the heading; the invented Polish sentence sits in `lang="pl"` spans on both sides of the blank |
| Option button | no `lang` on the button; `kogo? co?` → `lang="pl"`, ` · Accusative` → unmarked (document English) |
| English gloss `#gQuestionMeaning` | no `lang`, no marked descendant — never falsely Polish |
| Revealed correct option | identical segmentation to the un-revealed button |
| Status `#gStatus` | outer span carries **no** `lang`; both the chosen option and the answer are segmented exactly as the buttons are |
| Structural feedback `.fb-good .p` | `fikcjonowac` → `pl`, ` + ` → unmarked, `kogo? co?` → `pl`, ` · Accusative` → unmarked |
| Explanation `.fb-explain` | no `lang`, no marked descendant — English prose is never marked Polish because its *subject* contains Polish |
| Authored string option | unchanged: `lang="pl"` on the button, and one `lang="pl"` element in the announcement |

The visible label and the announcement cannot drift, because both are built by the same
`gAppendTextParts` from the same fragments; there is no second formatted copy anywhere. Nothing in
the language path parses markup, and hostile text inside a `lang="pl"` fragment is still only text
(§13).

**The settled state keeps it too.** Measured live after a miss: neither the chosen option nor the
revealed answer carries an `aria-label`; both keep `kogo? …?` in `lang="pl"` and the case name
unmarked; each gains one `.sr-only` child holding the verdict, with **no** `lang` — so the verdict is
read in the document's English, not as Polish. The hidden verdict is genuinely hidden
(`position:absolute`, 1×1px) and the button's rendered width is unchanged at 433px before and after
settlement. An untouched option gains nothing.

**Stated rather than glossed over:** the JXA harness computes no browser accessibility tree. What is
asserted is the DOM contract that *produces* the accessible name — which nodes exist, which carry a
language, whether the hidden verdict is inside the control, and whether anything overrides it. Real
name resolution, real voice switching and real screen-reader output remain human checks, exactly as
this repository's other suites state.

**Mobile, measured in the browser rather than asserted:**

| Width | Result |
|---|---|
| 320 × 780, revealed miss | `scrollWidth === clientWidth === 320`; no horizontal overflow; furthest right edge 277 of 320; the three long options wrap to 191 / 191 / 211px carrying `✕ Incorrect` and `✓ Correct` on their own lines; feedback wraps to 286px; Next 280 × 48; min touch target 48px |
| 320 × 780 | `scrollWidth === clientWidth === 320`; no horizontal overflow; the ~250-character prompt wraps between tokens; the three long options wrap to 171 / 191 / 211px; feedback wraps to 286px; nothing clipped |
| 375 × 812 | no horizontal overflow; furthest right edge 332 of 375; options 131–191px; min touch target 48px |
| 768 × 1024 | no horizontal overflow; options 91–131px |
| 1280 × 800 | no horizontal overflow; the card stays in the centred 520px column (373 → 893) |

**No new arbitrary breakpoint** — `@media` widths are still exactly `[360, 400, 400]` and the total
`@media` count is still 5. **No `overflow-x: hidden|clip` anywhere.** **No `word-break` or
`overflow-wrap: anywhere`** on any selector the data path uses. The only CSS added anywhere is the
one `content:` override described in §5.

## 13. Security and injection testing

Every synthetic runtime string is data and stays data. The hostile item carries markup in the
**prompt, the cue, an option label, the structural feedback and the explanation** simultaneously.

Measured in the browser and in the suite:

- every hostile string renders **verbatim as text** — prompt, cue, option label, feedback, explanation;
- `#gDrillCard img, script, iframe, a, style, object, embed` → **0 nodes**;
- **0** attributes matching `^on…` anywhere in the card; no `href`, no `src`, no `javascript:` URL;
- `window.__p7Pwned` stayed `undefined` through the whole item, including after answering it;
- the only element the renderer added to the prompt is the `.blank` span it creates itself;
- the four data painters (`gPaintChooseText`, `gPaintChooseFeedbackText`, `gAppendDrillText`,
  `gTextEl`) contain **no** `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval(`
  or `srcdoc`, and the data branch is chosen **before** any string is placed;
- the drill card's `innerHTML` was never written at any point during a synthetic round.

## 14. Tests, validators and totals

| Suite | Result |
|---|---|
| `python3 -m unittest discover -s tests -p 'test_*.py'` | **337 tests, OK** (293 at baseline + 44 new) |
| `python3 -m unittest tests.test_priority7_phase3d1` (new) | **44 tests, OK** |
| `python3 -m unittest tests.test_priority7_phase2a` | **77 tests, OK** (two amendments, §15) |
| `python3 -m unittest tests.test_priority7_phase3b` | **19 tests, OK** (one amendment, §15) |
| `python3 -m unittest tests.test_priority7_phase3c` | **22 tests, OK** (one amendment, §15) |
| All 34 `tests/*.js` under JXA | **10,409 assertions, 0 failed** (10,078 at baseline + 327 new + 4 additive) |
| `tests/test_priority7_choose_ui.js` (new) | **327 assertions, 0 failed** |
| `tests/test_grammar_interaction.js` | **616 assertions, 0 failed** — 612 original, none altered or removed, plus 4 additive |
| `tests/test_priority7_patterns_ui.js` | 407 assertions, 0 failed (unmodified) |
| `tests/test_phase3_closeout.js` | 510 passed |
| `tests/test_phase3b_mobile_layout.js` | 169 passed |
| `tests/test_phase3b_overlays.js` | 108 passed |
| `tests/test_phase1b_keyboard_focus.js` | 214 passed |
| `tests/test_phase2a_core_activity_accessibility.js` | 127 passed |
| `tests/test_activities.js` / `test_round_scoring.js` / `test_typeit_eligibility.js` | 146 / 168 / 120 passed |
| `python3 validate_content.py` | OK — levels 10, topics 97, cards 1,215, drills 353, 1,675 ids, forward baseline sha256 `2a71401d…` unchanged |
| `python3 verify_audio.py` | OK — 3,377 phrases / 3,377 manifest entries / 3,377 MP3s, nothing orphaned |
| `python3 build_pages.py --check` | OK — no drift; 23 grammar + 6 vocabulary pages, guide hub, 32 sitemap URLs |

**No pinned total moved:** 10 levels of vocabulary content, 97 topics, 1,215 cards, 353 drills, 1,675
ids, Type It 1,089 / Listening 1,113 pools, 3,377 audio files, 32 sitemap URLs.

### What the new assertions prove

**Harness boundary.** Ordinary startup has no Priority 7 activity — 13 levels, 6 grammar levels, the
`Verb patterns` tile reads `Reference · Not ready yet`, no practice affordance in the DOM, **zero**
network requests of any kind, no fixture read. The fixture is test-only, lives only under
`tests/fixtures/priority7/`, exists nowhere else in the tree, and appears in no public surface
(`index.html`, `sw.js`, `pp-verb-patterns.js`, `sitemap.xml` and all 33 generated pages; sitemap still
exactly 32 URLs). Shipping code cannot name, fetch or unwrap it. Only the harness can inject it, and
only after asserting the wrapper.

**Adapter.** Deterministic and order-stable; identical output on repeat and under reversed input; 31
distinct fail-closed cases including unsupported activity kind, missing correct option, two correct
options, duplicate option identities, duplicate exercise ids, duplicate orders, one bad record in an
otherwise good set, the wrapped document, the payload envelope, and a runtime pattern record.

**Choice mechanics.** Correct-first; the corrected incorrect flow end to end (verdict in words, the
correct option identified by identity rather than by label, every option closed, a brute-force sweep
of all remaining options changing nothing, feedback revealed by the miss itself, Next enabled and
focused); explicit option identity under identical labels; order independence; identical feedback on
both paths; requeue-once still the existing engine rule; end-of-session score and completion state.

**Retry outcomes (M).** Correct first try; wrong then correct on the retry (still truthfully
"cleared"); **wrong then wrong** (never claims it was cleared, and the word "cleared" does not appear);
several misses with every retry cleared, with none cleared, and with some cleared; no third attempt is
ever created; the score counts originals only and the retry stays out of the denominator; an
unrecorded outcome still reads as cleared; and no mastery or persistence word entered the copy.

**Validation hardening (N).** Duplicate option value `__proto__` **in an otherwise wholly valid
record** — the collision is between two *distractors*, the answer is a distinct singly-used value, and
the record is first asserted to be invalid for exactly one reason, so the old broken implementation
could not have passed the test for a different one; the same for five other special names and two
ordinary ones; the identical record with the collision removed is accepted; duplicate exercise id
`__proto__`; duplicate order; a special name still usable as a *unique* identity;
whitespace-only values (six blank forms) rejected for each of ten required and present-optional fields,
per item **and** for the whole set; blank fragments and fragments adding up to nothing; unusual but
non-blank strings still accepted; nothing trimmed, nothing mutated, fragments emitted as copies; and
the plain-object contract proven by an all-inherited object failing closed.

**Language of parts (O).** Polish-only prompt marked once and only around the Polish; the prompt
element itself claiming nothing; mixed labels split into a Polish part and a document-language part;
the button claiming no language; the English gloss and the explanation never marked Polish; the status
announcement segmented identically to the buttons on both the revealed and the correct path; the
revealed answer preserving segmentation; a plain authored string still announced as one `lang="pl"`
element; no markup path anywhere in the language helpers; the helpers containing no Priority 7
reference; one DOM-building function so the copies cannot drift; and hostile text inside a language
fragment still only text.

**Own-property contract (N4).** An inherited `promptEn`/`cue` is neither consumed nor looked at, with
the getters proven untouched by a counter *and* by a throwing variant; the drill built from such a
record is byte-identical to one built from own data alone; an inherited fragment `lang` is ignored,
including an *invalid* one, which is ignored rather than made a rejection; the same fields defined as
**own** properties are still read, validated and emitted, and an invalid own value still fails the
record closed; a required field that exists only on a prototype satisfies nothing; and the probe
itself is asserted to inherit and own exactly what it claims to, so it cannot pass vacuously.

**Settled accessible names (P).** Before settlement a mixed option is already segmented and the
English case name is not inside the Polish node. After a miss, the chosen option and the revealed
answer each keep their language-tagged children, carry **no** `aria-label`, and gain exactly one
`.sr-only` verdict with no `lang`; the revealed answer stays `aria-pressed="false"` while the
learner's choice is `"true"`; an untouched option gains nothing; the status keeps the same
segmentation. The first-try-correct path preserves all of it. A plain string option still gets its
`aria-label`, `lang="pl"` and no hidden child, and the engine branches on `Array.isArray` alone with
no Priority 7 token anywhere in it.

**The extension is opt-in, and generic.** A synthetic drill that omits `revealOnIncorrect` is driven
through the same shipping engine and gets the retry mechanic verbatim — `…, incorrect. Try again`,
only the chosen option disabled, two options still live, `G.state === "ask"`, answer hidden, feedback
empty, Next disabled, focus on another option. The flag is read in exactly one place, occurs exactly
once in `index.html` and once in `pp-verb-patterns.js`, appears **zero** times in `data-grammar.js`,
and the handler that reads it contains no Priority 7 reference of any kind.

**No progress.** No `rRecord`, no storage write, no new key, no schema move, no mastery — swept across
the entry, the adapter and all 22 Grammar functions on the path.

**Accessibility / mobile / security.** As in §12 and §13.

## 15. Deviations from the approved Phase 3A touch map

Five, all recorded rather than absorbed.

1. **The synthetic exercise fixture is hand-written, not regenerated through `project-fixture`.** The
   3A slice sketch assumed `vp-x-…` item records could be added to the synthetic editorial document
   and regenerated. They cannot at this tree — the runtime projector emits no exercise entity, and
   `priority7_tooling.py` is on the 3A §A10 must-not-change list — and the brief additionally forbids
   allocating any `vp-x-…` identity. The fixture is therefore its own wrapped, explicitly non-release
   test-only file in the same approved directory (brief §21), with its own marker and its own
   test-scoped identifier namespace (§6).
2. **The entry is named `pStartChoosePractice`, not `pStartPractice`,** and it delegates to the
   existing `gStartPractice` rather than owning a queue of its own. The 3A sketch described a
   `pStartPractice()` with "its own queue"; a second queue would have been a second engine, which
   §11 of the brief and §4 above both refuse.
3. **Three narrow, generic extension points were added to the shared Grammar choose engine**
   (`textOnly`, `{value,label}` options, `revealOnIncorrect`) plus the `gHasLesson` guard. The 3A
   touch map anticipated activity work in `index.html` but did not name these. Each is required by
   the brief itself: runtime strings must not become markup, scoring must not use displayed text,
   Back must be preserved, and the required incorrect flow reveals rather than retries. All three are
   optional drill properties read from the drill, all three leave authored drills on a byte-identical
   path, and all three are covered by regression tests.
4. **Four existing test files were amended**, each narrowed, split or extended rather than deleted or
   disabled, and each reviewed line by line:
   - `tests/test_priority7_phase2a.py` — (a) `ALLOWED_FIXTURE_FILES` gains `exercise-fixture.json`
     and each fixture's own non-release markers are now asserted individually (**strengthened**);
     (b) `ALLOWED_INDEX_REMOVALS` is split into a 3B tuple and an enumerated 3D-1 tuple naming
     **exactly** the 30 lines this phase removed, in three dated groups. The list is still exact, so an unenumerated removal
     still fails. The authored `innerHTML` skeleton and the four authored retry lines are *retained*,
     one indent deeper, and their presence is separately asserted.
   - `tests/test_priority7_phase3b.py` — the fixture-directory listing becomes "exactly these two
     wrapped non-release fixtures". The runtime fixture itself is untouched, so its byte-for-byte
     regeneration test still holds it down exactly.
   - `tests/test_priority7_phase3c.py` — the marker sweep headed *"Phase 3D has not started"* is
     **split**: the permanent safety half (no scoring, progress, mastery or measurement) still applies
     to both files and gained four more markers; the phase-boundary half still applies to the passive
     reference surface, which gained none of it; and four positive assertions now pin exactly what the
     adapter is allowed to say `grammar-choose` about.
   - `tests/test_grammar_interaction.js` — `GNAMES` + 10 extraction names, required because the
     extracted `gRenderChoose` / `gChooseFeedback` / `gShowDone` now call them, plus **4 additive**
     assertions pinning that the reveal is opt-in, that an absent flag still gets the retry mechanic,
     that the settle/close/reveal live only in the opt-in helper, and that no authored drill opts in.
     **No assertion was altered or removed** and all 612 originals still pass (616 total).
   `tests/test_priority7_patterns_ui.js` needed **no** amendment: its A7 phase-boundary assertion
   (`pStartPractice` / `queue` / `score` / `rRecord` absent from the reference block) is still
   literally true, because the prototype adds no round, no scoring and no activity vocabulary to the
   passive surface.
5. **The synthetic fixture gained explicit language metadata.** `prompt`, `feedbackStructure` and
   every option `label` are now authored as `{text, lang}` fragments; `promptEn`, `cue` and
   `feedbackExplanation` stay plain English strings. The brief permits modifying the fixture only if
   language metadata genuinely belongs in the record, and it does: a consumer that derived the
   language — by splitting on a separator, or by assuming a prompt is Polish — would be inventing a
   linguistic claim. One representation, not a parallel copy, so nothing can drift. The wrapper, the
   non-release markers, the ten mechanics shapes, the test-only identifiers and the answer positions
   are unchanged, and the long option tails were rewritten from pseudo-Polish into English so their
   declared language is honest.
6. **`gRenderDrill`'s non-`choose`-routes-to-build fallthrough was left in place.** The Activity
   Eligibility Specification §5 requires unknown activity types to *fail validation rather than fall
   through to build*, and this phase implements that **in the adapter**, which is where the brief
   places it: only validated `type:"choose"` drills can enter the queue, proven by test. Hardening the
   dispatch itself is a general Grammar change this phase does not need and therefore did not make.
   **Recorded as an open item for whichever phase first introduces a second drill type.**

One further observation, changed by nothing here: option buttons carry no `type` attribute, so they
default to `submit`. This is pre-existing shipping behaviour and harmless — they sit in no form — but
it is noted so a future phase does not discover it as new.

## 16. Runtime and release boundary

The chain a real exercise must travel, documented here and **not implemented**:

```
private approved exercise authoring        (editorial workspace; never a browser resource)
   → explicit exercise approval / allowed activity   (activityEligibility, an allowlist)
   → authorized release projection          (freeze_editorial(...) only)
   → public exercise runtime                (content/…, which does not exist)
   → Grammar adapter                        (grammarChooseDrills — the only part built here)
```

Phase 3D-1 bypasses the first four **only through the test harness**, and only for records that are
obviously synthetic. It proves **none** of: linguistic correctness, activity approval, release
authorization. The three artifacts remain non-equivalent: **test fixture ≠ validated runtime shape ≠
authorized release**, and this phase touches only the first.

Three boundaries a future phase must keep distinct, and which this phase implements only the test side
of: *public pattern runtime data* (shape-validated, private-key-free, rendered by the reference
surface); *public approved exercise runtime data* (does not exist — no schema, no file, no projector
entity); *private editorial exercise authoring data* (does not exist either — the corpus contains no
exercise record and gained none here).

**Phase 3D-2 remains blocked.** Verified mechanically at this tree: **0** patterns above `research`,
**0** review events, **0** `activityEligibility` entries, **0** `audioEligible: true` examples, an
empty reviewer registry, an empty author registry, no authored exercise record, and no
`content/verb-patterns.json`. Completing 3D-1 moves none of them, and must never be presented as
progress toward any of them. The remaining prerequisites are unchanged: linguistic review as required,
a product decision on the relevant patterns, explicit activity eligibility, real exercise authoring,
independent content review, and release authorization.

## 17. Real corpus, review and activity state

- `editorial/verb-pattern-candidates.json` byte-identical to baseline (sha256 `b6fb8139…`), as is
  `editorial/priority-7-authoring-context.json` (sha256 `d04dabf8…`). Both were read only.
- Verified mechanically: **30 lemmas, 34 meanings, 45 patterns; `reviewState` set = `{research}`;
  0 review events; 0 `activityEligibility` entries; 0 `audioEligible: true` examples; reviewer
  registry empty; author registry empty.**
- The corpus contains no `grammar-choose`, no `p7-fixture-` identifier, no exercise record, no
  allocation registry and no tombstone registry — none of which this phase created.
- **Zero review-state change, zero new review events, zero reviewer or author identities.** No
  linguistic claim is approved, native-reviewed or release-ready by this work.
- **Zero real activity integration.** No real Priority 7 exercise, no real exercise id, no real
  progress, no real runtime, no runtime fetch, no `content/` directory.
- **No analytics.** No `gtag`, no `analytics`, no `sendBeacon`, no cookie, no identifier, no
  measurement event. Priority 6 measurement remains parked and was not reopened.
- **No `grammar-build`, Type It, Listening, Mixed Quiz, "Build the pattern", audio or free typing**
  was implemented, and the fixture declares exactly one activity family.

## 18. Version and cache state

`APP_VERSION` `8.10` — unchanged. Shell cache `popolsku-v65`, audio cache `popolsku-audio`, `sw.js`
byte-identical. `schemaVersion` `2`, `CONTENT_MIGRATION_REVISION` `2`, `pp-migrate.js` byte-identical.
No `patternDataRevision` anywhere in the shipping app. No service-worker, cache or version work was
done, and none is authorized outside a release.

## 19. Manual review

Performed read-only in a browser: the page was loaded from disk and, for the populated states, the
synthetic items were unwrapped through the harness assertions in the console and handed to
`pStartChoosePractice`. **No repository file, tool or framework was added, and the working tree was
not touched by this.** Flows exercised at 320 / 375 / 768 / 1280:

- **Ordinary startup** — 6 grammar levels, `Verb patterns` sixth, tile `Reference · Not ready yet`,
  no practice affordance, **zero** network requests, no fixture read, `PP_VERB_PATTERNS.available`
  `false`.
- **Correct flow** — prompt → choice → correct feedback naming the structure and the explanation →
  Next focused. The option row never enters the revealed state.
- **Incorrect flow (corrected)** — measured on the hardest item, the two options that read the same
  case and differ only by identity: the chosen option painted `✕ Incorrect` with the accessible name
  `kogo? co? · Accusative — after o, incorrect`; the *other* twin painted `✓ Correct` with
  `kogo? co? · Accusative — bare slot, correct answer` and `aria-pressed="false"`; `.opts` carrying
  `revealed`; all three options disabled with zero left enabled; a subsequent click on every option
  changing neither the feedback nor the status; the structural pattern and the explanation on screen;
  status `… is not correct. The answer is … Explanation available below. Next is ready.`; Next
  enabled, labelled `Next` and focused; `G.results === [false]`.
- **Requeue** — the missed item returns once as `_requeue`, the retry presentation opens fresh with
  nothing revealed, and the final score is 2 / 3 with the retry excluded.
- **Retry outcome A (wrong → correct retry)** — 2 presentations, queue 2, 1 requeued, score `0 / 1`,
  copy `Nice work through the set - 1 drill came back for a second pass and you cleared it.`,
  `G.cleared === [false, true]`.
- **Retry outcome B (wrong → wrong retry)** — 2 presentations, **no third attempt**, queue 2,
  1 requeued, score `0 / 1`, copy `Nice work through the set - 1 drill came back for a second pass and
  still needs practice.`, `G.cleared === [false, false]`. The word "cleared" does not appear.
- **Language** — measured in the live DOM and reported in full in §12: Polish-only prompt marked
  `pl` around the Polish only; the mixed option split `kogo? co?` (`pl`) + ` · Accusative`
  (unmarked); the structural feedback split lemma / `+` / questions / case name; the English
  explanation and gloss unmarked; and the status announcement carrying no outer `lang` and the same
  segmentation as the buttons.
- **Settled options** — after a miss, neither the chosen option nor the revealed answer carries an
  `aria-label`; both keep their `lang="pl"` and unmarked children and gain one `.sr-only` verdict with
  no `lang`; the verdict measures `position:absolute` at 1×1px and the button's rendered width is
  unchanged at 433px; the revealed answer is `aria-pressed="false"` while the learner's choice is
  `"true"`.
- **Inherited-field safety** — a record whose prototype defines `promptEn`, `cue` and a fragment
  `lang` as getters is accepted on its own data with **0** getter reads, and emits `""` for both
  optional fields and a language-free fragment.
- **Authored Grammar retry, live** — an authored choose drill driven through `startGrammar` +
  `gStartPractice` still shows `✕ Try again`, keeps two options enabled, leaves `G.state === "ask"`,
  reveals no answer, leaves the feedback box empty, leaves Next disabled and moves focus to another
  option.
- **Keyboard** — screen entry on the prompt; tab order Back → speed toggle → Home → options; settled
  options leave the tab order and Next enters it.
- **Narrow phone** — the long-wrapping item at 320px with long option labels and a 344-character
  explanation, in the revealed state: no horizontal scroll, everything wraps, `✕ Incorrect` and
  `✓ Correct` each on their own line, 48px targets.
- **Hostile item** — every field rendered as text; 0 injected nodes; 0 handler attributes;
  `__p7Pwned` undefined.
- **End state** — `Brawo!`, 2 / 3, `Review the lesson` hidden, no continuation, no mastery language.
- **Back** — from a lesson-less round, Back leaves the activity for home and refocuses the invoking
  tile; from an authored topic, Back still returns to the lesson.
- **Authored regression, live** — an authored choose drill still reads `Choose the right form`,
  renders its blank, carries `lang="pl"` options whose `data-val` equals their text, uses the markup
  feedback path with its audio control, keeps the retry mechanic, and still shows `Review the lesson`.
- **Console** — the only errors are the pre-existing `file://` service-worker registration and
  directory-`HEAD` failures Phase 3B recorded, confirmed identical on a clean reload with no injection.

Real screen readers, real key synthesis and real device text scaling remain human checks, exactly as
the repository's own suites state.

## 20. Git

**Zero remotes. `push.default=nothing`. No commit. No push. No remote added.** HEAD is still
`e19bb3ccad8f7bac72927f345a14ca6954ac9074`.

Final `git status --short --untracked-files=all`:

```
 M index.html
 M pp-verb-patterns.js
 M tests/test_grammar_interaction.js
 M tests/test_priority7_phase2a.py
 M tests/test_priority7_phase3b.py
 M tests/test_priority7_phase3c.py
?? tests/fixtures/priority7/exercise-fixture.json
?? tests/test_priority7_choose_ui.js
?? tests/test_priority7_phase3d1.py
```

## 21. Correction record

Two passes, recorded here rather than folded silently into the sections above. Everything described
elsewhere in this report is the **post-correction** state; the "before" paragraphs below are
historical.

### 21.1 The incorrect-answer flow

The first candidate was provisionally accepted with one mechanics requirement unmet, and this is the
record of closing it.

**Before (historical, pre-correction).** A synthetic miss took the authored Grammar mechanic
unchanged: the chosen option was marked and disabled, the *other* options stayed live, the answer and
the explanation stayed hidden, Next stayed disabled, and the learner kept choosing until they found
the answer. That is correct for authored form drills and wrong here: with three structural options,
eliminating two hands over the answer without a second decision being made, scores identically either
way, and withholds the explanation — the part that actually teaches — until the guessing ends.

**After.** `wrong choice → incorrect verdict → reveal the correct structure and the explanation →
close every choice → Next`, exactly as §9 and §12 now describe.

**How it was implemented — the smallest generic extension.** One optional drill property,
`revealOnIncorrect`, read in exactly one place inside the generic answer handler and dispatching to
one helper, `gRevealChooseAnswer`. No `priority7`, `PP_VERB_PATTERNS`, `patternRef`, `exerciseId`,
`vp-` or fixture check exists anywhere in the handler or the helper — the engine asks the drill, never
the corpus. The synthetic adapter emits the property; `data-grammar.js` does not carry it, cannot be
given it by this phase, and is byte-identical.

**What the correction did not change.** The correct-answer path; scoring by explicit option `value`;
the twin-label and order-independence guarantees; the requeue-once rule and every other round
mechanic; the feedback content; the absence of audio; the focus and status architecture; the
no-progress boundary (`popolsku-progress-v2` still byte-identical, still no new storage key, still no
`rRecord`); the fixture, which was **not modified** — the mechanism needed nothing from it; the
harness boundary; ordinary startup; and every version, cache, corpus and review-state fact in §16–§18.

**Files changed by the correction:** `index.html` (the `gAnnounceRevealed` announcer, the
`gRevealChooseAnswer` helper, the one-line opt-in branch, one CSS override), `pp-verb-patterns.js`
(the adapter emits the property), `tests/test_priority7_choose_ui.js` (the C4/C5/D2/E1/F3/H2/H3/K0
sections), `tests/test_grammar_interaction.js` (2 more extraction names, 4 additive assertions),
`tests/test_priority7_phase2a.py` (2 more enumerated removals), and this report.

### 21.2 Independent-review findings

An independent review then returned `NO-GO` on three MEDIUM findings and one LOW test-coverage
finding, while accepting the architecture: genuine reuse of the Grammar `choose` engine, no second
engine, generic opt-in properties, authored retry-until-correct retained, no Priority 7 activity in
ordinary startup, no persistence or analytics path, and an untouched real corpus. All four are fixed;
nothing accepted was disturbed.

**(1) The completion copy could claim an uncleared retry was cleared.**
*Before:* a requeued item missed a second time ended the round with `0 / 1` — correctly — but the copy
still read `1 drill came back for a second pass and you cleared it`. The sentence had been safe only
because the retry mechanic guaranteed every requeued drill was eventually answered correctly, and
`revealOnIncorrect` retired that guarantee.
*After:* `G.cleared` records whether each presentation ended on the right answer, `gRetryOutcome()`
derives the summary from it and the `_requeue` entries, and `gDoneMessage()` picks one of four
truthful sentences (§9). Scoring, denominator, requeue-once and queue semantics are untouched, and
every authored round produces the identical sentence it always did.

**(2) Uniqueness validation was prototype-sensitive.**
*Before:* the option-value, exercise-id and order sets were `{}` objects, so two values both spelled
`__proto__` were each seen as new and the duplicate was accepted. No pollution occurred; the
invariant was simply defeated.
*After:* `Object.create(null)` dictionaries behind one `seenBefore()` helper, applied consistently to
all three sets. Not a `__proto__` blacklist — the invariant holds for arbitrary strings, and a test
sweeps six special names and also proves such a name is still usable as a *unique* identity.

**(3) Whitespace-only required strings were accepted.**
*Before:* `isNonEmptyString` accepted `" "` for required learner-facing and mechanics fields.
*After:* `isFilledString` rejects them across every required field and every *present* optional one,
per item and for the whole set. Values are rejected rather than trimmed, and nothing handed to the
adapter is mutated. The plain-object question raised alongside this was reviewed and deliberately not
changed, with the reasoning pinned by two tests rather than left as prose (§7).

**(4) Language of parts was wrong in both directions.**
*Before:* the visible Polish prompt and structural feedback carried no `lang`, so an English voice
read Polish; and a mixed label like `kogo? czego? · Genitive` was announced inside one `lang="pl"`
element, so a Polish voice read the English word `Genitive`.
*After:* a drill string may be a plain string or an array of `{text, lang}` fragments. One function
turns fragments into DOM; the visible option, the prompt, the revealed answer, the feedback and the
status announcement all go through it, so a string cannot be segmented two ways in two places. The
fixture authors the languages because the record is where they are known — the engine and the adapter
derive nothing. Measured results are in §12. **String-only authored options are untouched**, and no
real Grammar content needed migration.

**(5) Test coverage.** The review noted the suite stayed green through all three defects. The
Phase 3D-1 JXA suite grew 228 → **293** assertions with three new sections (M retry outcomes,
N validation hardening, O language of parts) and the Python suite 33 → **42** tests; every earlier
Phase 3D-1 assertion was preserved and none was weakened.

**Files changed by this pass:** `index.html`, `pp-verb-patterns.js`,
`tests/fixtures/priority7/exercise-fixture.json` (explicit language metadata — §15),
`tests/test_priority7_choose_ui.js`, `tests/test_priority7_phase3d1.py`,
`tests/test_grammar_interaction.js` (7 more extraction names only), `tests/test_priority7_phase2a.py`
(10 more enumerated removals), and this report.

### 21.3 Verification findings

A second independent verification pass found two remaining MEDIUM issues and one LOW test-quality
issue, while confirming everything else. All three are fixed and nothing accepted was redesigned.

**(1) Recognised optional fields were read through the prototype chain.**
*Before:* required fields were own-checked, but `promptEn`, `cue` and a fragment's `lang` were tested
with `in`, which answers for inherited properties. An inherited value counted as supplied, and reading
it then executed an inherited getter during validation. Reproduced for all three.
*After:* one `hasOwn()` helper is used for every recognised optional presence check, and
`copyTextValue` reads a fragment's `lang` only when the fragment owns one. The whole Phase 3D-1
record/fragment parser was swept — `" in item"`, `" in fragment"`, `" in option"` and `" in value"`
now occur **zero** times in it — and the sweep is pinned by a test. Inherited recognised fields are
ignored; inherited getters are proven never to run, by a counting probe *and* by one that throws.
Required prototype-only fields are still rejected, and a record with valid own data plus unrelated
prototype properties is still accepted.

**(2) A settled mixed option was flattened into one `aria-label`.**
*Before:* on settlement the button received `aria-label="kogo? czego? · Genitive, incorrect"`. Because
`aria-label` replaces the whole computed name, the language-tagged children were discarded and
assistive technology lost the segmentation — and the button could not carry one correct `lang` either,
since its content is not one language.
*After:* `gSetOptionVerdict()` branches on the option's **shape**, never on who supplied it. A
fragment option gets its verdict appended as a `.sr-only` child, so the name is still computed from
the same language-tagged nodes with the verdict joining it in the document's English; no `aria-label`
is written. A plain string option keeps the `aria-label` it has always had, because one language
flattens without loss — which is exactly what every authored Grammar drill still gets. `aria-pressed`,
disabled state, the live announcement, the feedback and Next focus are unchanged, and the revealed
answer still reads `correct answer` at `aria-pressed="false"` so nothing suggests the learner chose it.

**(3) The `__proto__` duplicate-option test did not isolate the failure.**
*Before:* the test made both distractors **and** the answer `__proto__`, so the old broken
implementation could still have rejected the record for having two correct options — the duplicate
regression could have returned with the test green.
*After:* the answer is a distinct, valid, singly-used value and only the two *distractors* collide;
the record is separately asserted to be invalid for exactly one reason; the identical record with the
collision removed is accepted; and the same is proven for five other special names and two ordinary
ones. Verified by running the pre-fix implementation against the new test: it accepts the `__proto__`
duplicate (regression visible) while correctly rejecting an ordinary one.

**Files changed by this pass:** `pp-verb-patterns.js`, `index.html`,
`tests/test_priority7_choose_ui.js`, `tests/test_priority7_phase3d1.py`,
`tests/test_grammar_interaction.js` (one more extraction name only), and this report. The fixture was
**not** touched, and no Phase 2A/3B/3C invariant changed — `test_priority7_phase2a.py`'s enumerated
removal list still matches at 30 lines with no edit.

## 22. What this phase does not claim

Phase 3D-1 proves that the existing Grammar `choose` mechanics can carry a future verb-pattern
practice item through a narrow adapter and three optional drill properties, that a miss ends the
presentation by answering it rather than by inviting a guess, that the adapter fails closed on
everything malformed, that synthetic runtime strings cannot become markup, that the round writes
nothing, and that a learner cannot reach any of it. **It claims nothing about Polish.** No pattern became eligible for anything;
no exercise identity was allocated, frozen or persisted; no review state moved; no release exists or
is closer to existing. **Phase 3D-2 was not started and remains blocked.**
