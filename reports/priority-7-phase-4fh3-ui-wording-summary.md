# Priority 7 — Phase 4F-H3: UI wording

**Baseline commit** `fa524f68bada3f0b893c8ed94835bfaa274a9b35`
**Baseline tree** `c95e19834d863f2c7690147d856e01428e2b4190`
**Scope** two approved learner-facing wording changes, in one file.
**Not in scope** content, governance, audio, activities, release, versioning.

---

## 1. What this phase was for

Phase 4F-H2.1 closed with one item outstanding. Its own context notice says so:
"the UI wording change remains outstanding for a later phase". Its acceptance
note says the same in four words — "Audio deferred; UI wording separate." Phase
4F-H3 is that item and nothing else.

Two changes, both previously approved by the product owner:

1. **Title case for the surface name.** `Verb patterns` → `Verb Patterns`,
   wherever the name functions as a title or a label.
2. **The recognition-only learner badge.** `Understand this one` →
   `Understand for now`.

---

## 2. String inventory, as found

Taken from the live tree before any edit, not from an earlier phase's notes.

### `index.html`

| Line | Occurrence | Classification |
| --- | --- | --- |
| 1701 | `<h1 id="pTitle">Verb patterns</h1>` | **visible title** — the surface's static `<h1>` |
| 2067 | `name:"Verb patterns"` | **visible label** — the Grammar topic tile's name |
| 2086 | `LEVELS.push({ level:"Verb patterns", …` | **visible label** — the Grammar level name, rendered by `modeLabel()` |
| 3945 | `$("pTitle").textContent = "Verb patterns";` | **visible title** — reasserted on every index render |
| 4252 | `pEl("p", "vp-lead", "Verb patterns")` | **visible title** — the unavailable state's lead, standing in for the title |
| 4022 | `text:"No verb patterns with "` | **mid-sentence prose** — an empty-result sentence |
| 992, 3656, 3909 | `verb patterns` | **comment** |
| 1062, 1070, 3821 | `Verb Patterns` | **comment** (already title case before this phase) |
| 4099 | `"Understand this one"` | **visible badge** — the recognition-only learner label |

### `pp-verb-patterns.js`

| Line | Occurrence | Classification |
| --- | --- | --- |
| 148 | `CARD_INDEX_DOORWAY_LABEL = "See verb patterns"` | **phrase** — a card-back call to action |
| 599 | `label: "Verb patterns with the " + meta.en` | **phrase** — a `.vp-continue` button label |
| 600 | `srLabel: "Verb patterns with the " + …` | **accessibility label** — the same phrase, with the Polish case name |

`Understand this one` does not occur in `pp-verb-patterns.js`.

### Priority 7 tests

| File | Occurrences | Classification |
| --- | --- | --- |
| `tests/test_priority7_patterns_ui.js` | 22 × `Verb patterns`, 1 × `Understand this one` | live UI expectations and harness fixtures |
| `tests/test_priority7_choose_ui.js` | 1 × `level:"Verb patterns"` | live shell-shape expectation |
| `tests/test_priority7_phase3b.py` | 2 | live shell-shape expectation |
| `tests/test_priority7_phase3d1.py` | 1 | live shell-shape expectation |
| `tests/test_priority7_phase3c.py` | 2 | loader phrases — **not affected**, the loader did not change |
| `tests/test_priority7_phase4fh21.py` | 1 × `Understand this one` | historical claim, explicitly named "pre-H3" |

Nothing outside these files carries either string: not `sw.js`, not
`manifest.json`, not `build_pages.py`, and not one generated page under
`grammar/`, `guide/` or `vocabulary/`. **The wording is not part of generated
output, so nothing was regenerated.**

---

## 3. Title-case decisions

**Changed — five sites, all title/label.** They are the same name in the same
role: the name of the surface, shown as its heading, its tile or its level.
`H1` reported five; re-derived from this tree, it is these five and there is no
sixth. `tests/test_priority7_phase4fh3.py` pins the count over comment-stripped
source, so a sixth site cannot appear unnoticed.

**Not changed — `No verb patterns with <Case>`.** A sentence about an empty
result. It names no surface; it reports a count of zero.

**Not changed — `See verb patterns`.** One of two mutually exclusive labels on
the same card-back control. Its sibling is `See how this verb is used`. Both
are call-to-action sentences, and title casing one half of a matched pair would
break the pair without making anything clearer. The previous classification —
phrase, not title — holds against the live implementation.

**Not changed — `Verb patterns with the <Case>`.** The visible label of the
`.vp-continue` button at the end of a case lesson, plus the text half of that
button's accessible name (`srLabel`, which adds the Polish case name). The
loader's own comment on the line above states the intent: the wording promises
exactly what the destination shows, and no more. It describes a *filtered view*
rather than naming a surface, and it reads as one sentence with a case name
inside it. Title casing the first two words would turn a description into a
half-title. The previous classification holds, and `pp-verb-patterns.js` is
therefore byte-identical to the baseline.

**Behavioural check on the rename.** Nothing keys off the display name.
Routing matches `kind === "patterns" && surface === "verb-index"`; the Grammar
category derives from `group === "grammar"`; the only string equality on a
level name in the shell is `lv.level === "Grammar Cases"`, which is a different
level. The one place a level name reaches a derived key is Listening's
in-memory recency scope (`lScopeKey`), which a `kind:"patterns"` topic can
never enter, and which is not persisted. Search is case-folded on both sides,
so the tile remains findable by either casing.

---

## 4. The recognition-only badge

**True source.** `index.html:4099`, in `pRecognitionChip()` — the single
producer of the badge, and the only occurrence of the literal anywhere in the
repository's shipping files.

**Changed.**

```
pEl("span", "usage-badge u-recognition vp-recognition", "Understand for now")
```

**Not changed.**

* `teachingStatus = "recognition-only"` — the editorial term, and the
  governance/runtime schema around it.
* `PP_VERB_PATTERNS.isRecognitionOnly()`, which derives `recognitionOnly` from
  it. `pp-verb-patterns.js` is byte-identical to the baseline.
* The two call sites' guards: `if(row.recognitionOnly)` in `pBuildRow` and
  `if(pattern.recognitionOnly)` in `pRenderLemma`. Neither has an `else`, and
  neither gained one.
* Eligibility. `activityEligibility` is still empty on all 45 patterns.
* Style and colour. `.usage-badge.u-recognition` and `.vp-recognition` are
  untouched; the whole `<style>` block is byte-identical. The new label is two
  characters shorter than the old one, so nothing needed to change to fit.
* Accessibility. The chip is still a plain `<span>` with visible text — no
  `aria-label`, no `aria-hidden`, no `role`. It reads as part of the row
  button's accessible name in the index, and as ordinary text inside a pattern
  block in the lemma view, exactly as before.

**Who gets one, unchanged.** The canonical A-Z index badges nobody: its rows
are lemmas, `rows("all")` sets `isSummary = false` and never sets
`recognitionOnly`, and `pBuildRow` only reaches the badge inside its
`isSummary` branch. A filtered row is badged only where that pattern is
recognition-only. A lemma entry badges only its recognition-only patterns. All
three are now asserted against the rendered DOM in
`tests/test_priority7_patterns_ui.js` (section I15), which previously checked
only the source literal.

**A different, untouched label.** `pp-usage.js` owns the vocabulary card's
`Recognition only` chip. That is a separate string on a separate surface, and
it was explicitly out of scope. `pp-usage.js` is byte-identical to the
baseline.

---

## 5. File footprint

| Path | Change |
| --- | --- |
| `index.html` | 6 lines — 5 title/label sites, 1 badge |
| `tests/priority7_phase4fh3_normalizer.py` | new — the phase-owned normaliser |
| `tests/test_priority7_phase4fh3.py` | new — the phase suite |
| `tests/test_priority7_patterns_ui.js` | wording expectations + section I15 |
| `tests/test_priority7_choose_ui.js` | one wording expectation |
| `tests/test_priority7_phase3b.py`, `…phase3d1.py` | one wording expectation each |
| `tests/test_priority7_phase4f{a,b3b,c1c,c2,d31,f2,g1,h2,h21}.py`, `…phase5a.py` | phase-aware repair |
| `tests/test_priority7_phase4fc2d.py` | one entry in `REPAIRED_SUITE_DEPENDENCIES` |
| `reports/priority-7-phase-4fh3-ui-wording-summary.md` | new — this report |

No other file moved. No file was created outside `tests/` and `reports/`.

---

## 6. Content and governance

Both private editorial files are byte-identical to the baseline:

* `editorial/verb-pattern-candidates.json` —
  `sha256:3613a841a992d5848b4c422b247075c15a75efcf69b85070c6fb4168a011ee3f`
* `editorial/priority-7-authoring-context.json` —
  `sha256:4ab2bb4b1ae0fa522ec68822731a547cc04a51858beab6e2cd6ff9ae69c79a1c`

Governance stands where Phase 4F-H2.1 left it: 30 lemmas, 34 meanings, **45
patterns, 45 examples, 45 approved**. Review events are unchanged at 47
reference-verification, 133 editorial-review, 42 correction and 89
product-approval; `reopen` is still 0. No correction, reopen,
reference-verification, editorial-review or product-approval event was created.
The teaching-status split is unchanged at 41 active-production and 4
recognition-only — the badge's population is a content fact, and no content
moved.

---

## 7. Audio and release

* `activityEligibility` is empty on all 45 patterns; no example is
  `audioEligible`.
* `pp_audio_rule.py`, `pp-usage.js` and `audio-manifest.json` are
  byte-identical; no file under `audio/` moved. No audio button exists on the
  surface.
* `content/verb-patterns.json` does not exist, and neither does `content/`.
* The loader was not activated: the shell names no runtime path, still has
  exactly two `fetch(` calls, and `sw.js` names no runtime path.
* `APP_VERSION` stays `8.10`, `CACHE` stays `popolsku-v65`, `AUDIO_CACHE` stays
  `popolsku-audio`, `CONTENT_MIGRATION_REVISION` stays `2`, `schemaVersion` is
  untouched and `sw.js` did not move.
* The parked G2 activation was not recreated.
* No generated page, no `sitemap.xml` entry and no audio file changed.

---

## 8. Historical test handling

`index.html` had not moved since `f339efb`. Every Priority 7 phase from 4F-A to
4F-H2.1 was editorial or governance only, and each states against its own
pinned baseline that no shipping file moved. H3 is the first phase since
`f339efb` entitled to change one, so ten historical suites needed the
established phase-aware repair.

**Direct expectation updates** where the assertion is live UI behaviour and the
wording is only how it names the thing:

* `tests/test_priority7_patterns_ui.js` — the rendered title, the topic name,
  the level entry, the harness fixtures and the badge literal. Section I15 was
  added: the badge's rendered text, and the three surfaces that decide who
  carries one.
* `tests/test_priority7_choose_ui.js`, `tests/test_priority7_phase3b.py`,
  `tests/test_priority7_phase3d1.py` — one `level:"Verb Patterns"` expectation
  each. The claims (one level, created unconditionally, no fetch, no second
  tile) are unchanged in force.

**The closed H3 normaliser** where the suite is explicitly historical:
`tests/priority7_phase4fh3_normalizer.py`. It pins the six `(pre, post)`
strings, reports the layer as `absent` / `complete` / `partial`, refuses to
normalise a partial layer, and performs *only* those six reverse substitutions.
The historical suites then state their claim over the normalised shell:

```python
self.assertEqual(git_blob("index.html"),
                 H3.without_phase_4fh3_ui_wording(read("index.html")))
```

Because every other byte passes through untouched, the byte comparison at the
call site still exposes everything the normaliser must not hide. That is
asserted, not asserted-about: `NormaliserTests.test_it_hides_nothing_but_its_own_six_strings`
applies six forbidden mutations — a version bump, a runtime path named in the
shell, a loader activation, a widened recognition-only guard, an inverted
recognition-only guard, and an unrelated label edit — and proves each one
survives normalisation and is refused by the footprint helper. Governance and
content mutation are out of the normaliser's reach entirely: it owns exactly
one path, `index.html`.

`test_priority7_phase4fh21.py::test_the_ui_wording_is_still_the_pre_h3_wording`
was restated rather than deleted. It asserted `assertIn("Verb Patterns", index)`
against the live shell, which was already satisfied by a CSS comment before H3
and would have been satisfied by H3 itself afterwards — a claim that could not
fail. It now runs over the normalised shell and pins the pre-H3 wording at its
five sites plus the retired badge, so it means what its name says.

**One fixture dependency.** Phase 4F-C2D rebuilds a clone of the baseline and
copies a fixed set of suites into it. Those suites now import the H3
normaliser, so the file has to travel with them; it was added to that suite's
`REPAIRED_SUITE_DEPENDENCIES`, exactly as Phase 4F-E1, 4F-F2, 4F-H2 and
4F-H2.1 each added theirs. C2D's own footprint assertion still pins exactly 27
paths, unchanged. The H3 suite pins this coupling so it cannot silently rot.

No behavioural assertion was weakened, and no suite was skipped, deleted or
marked expected-failure.

---

## 9. Validation

Run at the H3 candidate, uncommitted, and again in the committed scratch.

| Check | Result |
| --- | --- |
| `python3 -m unittest tests.test_priority7_phase4fh3` | 57 tests, OK |
| Full Python discovery (`tests/`), working tree | 1902 tests, OK |
| Full Python discovery (`tests/`), committed scratch | 1902 tests, OK |
| JXA suites (`osascript -l JavaScript`) | 36 files, 10552 assertions, 0 failures |
| `tests/test_priority7_patterns_ui.js` | 446 assertions (438 + 8 new) |
| `python3 validate_content.py` | OK — 10 levels, 97 topics, 1215 cards, 353 drills |
| `python3 verify_audio.py` | OK — 3377 phrases, 3377 manifest entries, 3377 MP3s |
| `python3 build_pages.py --check` | OK — committed output current, 32 sitemap URLs |
| `validate-editorial` (real private context, real repository index) | valid |
| `git diff --check` | clean |
| remotes | none |

The committed-state column was produced in a disposable zero-remote scratch
clone whose single commit is the direct first descendant of the baseline and
whose tree reproduces byte for byte from the live workspace. That scratch was
clean, carried no remote, was never pushed, and was deleted after validation.
The real H3 workspace stays uncommitted.

`validate-runtime` was not run: no official runtime file exists in this phase
and none was created in order to run it. The known Phase 4F-C1C
standalone-import issue was left untouched.

---

## 10. What remains

* **Audio** — still deferred. No pattern example is audio-eligible.
* **Activities** — `activityEligibility` is empty on all 45.
* **Freeze / release / runtime projection** — none performed. All 45 patterns
  are approved and eligible for a freeze, but freezing, projecting
  `content/verb-patterns.json`, its service-worker entries, the `APP_VERSION`
  advance and the shell cache bump remain one atomic release bundle, and none
  of it is in this phase.
