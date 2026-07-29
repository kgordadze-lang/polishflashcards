// Deterministic tests for the MIXED QUIZ's non-visual feedback and focus handling.
// Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_mixed_accessibility.js
// Exit status is 0 only if every assertion passes (printed at the end).
//
// WHAT THIS PINS DOWN
// Priority 3 Phase 3D gave Listening a spoken result and a sane focus order.
// The Mixed Quiz was left where Listening had been: a multiple-choice answer was
// told to the learner in colour and in nothing else, and the only polite region
// near the options, #rFb, holds OPTIONAL material (an example, a usage chip, a
// warning) - so an ordinary card announced silence for a correct answer, and a
// rich card announced example prose that never said "correct". A wrong answer
// announced nothing at all.
//
// Focus was worse than silent. A wrong option is disabled while it still holds
// focus; the correct answer disables every option, including the focused one; and
// rRender disables Next while IT still holds focus. A browser answers all three by
// dropping focus on <body>, so a keyboard learner was thrown back to the top of the
// document twice per question, and the completion screen was reached with focus
// nowhere at all.
//
// This file drives the SHIPPING Mixed Quiz functions - read out of index.html the
// same way the other index.html suites read theirs - against a fake DOM that models
// the three things that matter here and are usually faked away:
//   * focus() on a disabled element does nothing,
//   * focus() on a hidden element does nothing, and
//   * disabling the focused element moves focus to <body>.
// Without those, "focus went somewhere sensible" is unfalsifiable. With them, a
// missing focus call reads as focus landing on <body>, which is what the learner
// actually experiences.
//
// WHAT IT DELIBERATELY DOES NOT DO
// It does not restate what the other Mixed Quiz suites own. How a typed verdict is
// DECIDED belongs to tests/test_answer_validation.js; how the tiers are COUNTED
// belongs to tests/test_round_scoring.js; which options are built belongs to
// tests/test_distractors.js; the audio lifecycle belongs to
// tests/test_audio_fallback.js. Scoring appears here only as "this phase did not
// move it", and audio only as a counter, so "the render path started nothing" is
// observable. Release identifiers, comment wording and corpus counts are not
// pinned: they change on purpose, and a permanent accessibility suite must not
// fail for that.
ObjC.import('Foundation');

function readFile(path) {
  var s = $.NSString.stringWithContentsOfFileEncodingError(path, $.NSUTF8StringEncoding, null);
  return ObjC.unwrap(s);
}
// Portable root resolution: the documented command runs from the repo root; also tolerate
// being run from inside tests/. No hard-coded absolute path.
function resolveRoot() {
  var fm = $.NSFileManager.defaultManager;
  var cwd = ObjC.unwrap(fm.currentDirectoryPath);
  var candidates = [cwd + '/', cwd + '/../'];
  for (var i = 0; i < candidates.length; i++) {
    if (fm.fileExistsAtPath(candidates[i] + 'index.html')) return candidates[i];
  }
  return cwd + '/';
}
var ROOT = resolveRoot();
var INDEX = readFile(ROOT + 'index.html');

// ---------- tiny test framework ----------
var PASS = 0, FAIL = 0, LOG = [];
function ok(name, cond) { if (cond) { PASS++; } else { FAIL++; LOG.push('FAIL: ' + name); } }
function eq(name, a, b) {
  var sa = JSON.stringify(a), sb = JSON.stringify(b);
  ok(name + (sa === sb ? '' : '  (got ' + sa + ', want ' + sb + ')'), sa === sb);
}
function info(msg) { console.log('  [info] ' + msg); }

// ---------- pull the real functions out of index.html ----------
// Same brace scanner the other index.html suites use: skips comments and strings,
// deliberately does not model regex literals. A broken extraction throws, which is
// the correct outcome.
function extractFunction(src, name) {
  var needle = 'function ' + name + '(';
  var start = src.indexOf(needle);
  if (start === -1) throw new Error('extract: function ' + name + ' not found in index.html');
  if (src.indexOf(needle, start + 1) !== -1) throw new Error('extract: function ' + name + ' declared more than once');
  var open = src.indexOf('{', src.indexOf(')', start));
  if (open === -1) throw new Error('extract: no body for ' + name);
  var depth = 0, mode = 'code';
  for (var j = open; j < src.length; j++) {
    var c = src[j], n = src[j + 1];
    if (mode === 'line') { if (c === '\n') mode = 'code'; continue; }
    if (mode === 'block') { if (c === '*' && n === '/') { mode = 'code'; j++; } continue; }
    if (mode === 'sq' || mode === 'dq' || mode === 'tpl') {
      if (c === '\\') { j++; continue; }
      if (mode === 'sq' && c === "'") mode = 'code';
      else if (mode === 'dq' && c === '"') mode = 'code';
      else if (mode === 'tpl' && c === '`') mode = 'code';
      continue;
    }
    if (c === '/' && n === '/') { mode = 'line'; j++; continue; }
    if (c === '/' && n === '*') { mode = 'block'; j++; continue; }
    if (c === "'") { mode = 'sq'; continue; }
    if (c === '"') { mode = 'dq'; continue; }
    if (c === '`') { mode = 'tpl'; continue; }
    if (c === '{') depth++;
    else if (c === '}') { depth--; if (depth === 0) return src.slice(start, j + 1); }
  }
  throw new Error('extract: unbalanced braces for ' + name);
}

// Comment-stripped view. Ordering and presence must be decided by code, never by
// prose that happens to mention a call.
function codeOnly(src) {
  var out = '', mode = 'code';
  for (var j = 0; j < src.length; j++) {
    var c = src[j], n = src[j + 1];
    if (mode === 'line') { if (c === '\n') { mode = 'code'; out += c; } continue; }
    if (mode === 'block') { if (c === '*' && n === '/') { mode = 'code'; j++; } continue; }
    if (mode === 'sq' || mode === 'dq' || mode === 'tpl') {
      out += c;
      if (c === '\\') { out += src[j + 1]; j++; continue; }
      if (mode === 'sq' && c === "'") mode = 'code';
      else if (mode === 'dq' && c === '"') mode = 'code';
      else if (mode === 'tpl' && c === '`') mode = 'code';
      continue;
    }
    if (c === '/' && n === '/') { mode = 'line'; j++; continue; }
    if (c === '/' && n === '*') { mode = 'block'; j++; continue; }
    if (c === "'" || c === '"' || c === '`') { mode = (c === "'" ? 'sq' : c === '"' ? 'dq' : 'tpl'); out += c; continue; }
    out += c;
  }
  return out;
}
function countOf(hay, needle) {
  var n = 0, at = 0;
  while ((at = hay.indexOf(needle, at)) !== -1) { n++; at += needle.length; }
  return n;
}
// Source checks run against a whitespace-free view of the code. Re-indenting a
// block, breaking a long statement over two lines or putting spaces around an `=`
// changes none of what the code DOES, so none of it may fail a test. What is still
// pinned is the tokens and their order - which is the claim being made - never the
// formatting they happen to be typed in.
function squash(s) { return s.replace(/\s+/g, ''); }
function hasCode(hay, needle) { return squash(hay).indexOf(squash(needle)) !== -1; }

// =========================================================================
// A. MARKUP SEMANTICS - the screen declares what it promises
// =========================================================================
// The opening tag carrying a given id, and its attributes. Attribute order is not
// asserted anywhere below; only presence and value are.
function tagFor(id) {
  var at = INDEX.indexOf('id="' + id + '"');
  if (at === -1) throw new Error('markup: no element with id ' + id);
  var open = INDEX.lastIndexOf('<', at), close = INDEX.indexOf('>', at);
  if (open === -1 || close === -1) throw new Error('markup: unterminated tag for ' + id);
  return INDEX.slice(open, close + 1);
}
function attr(tag, name) {
  var m = tag.match(new RegExp('\\s' + name + '\\s*=\\s*"([^"]*)"'));
  return m ? m[1] : null;
}
// The Mixed Quiz <section> alone, so the other activities' regions are never counted.
var ROUND_SCREEN = (function () {
  var s = INDEX.indexOf('<section class="screen" id="round"');
  if (s === -1) throw new Error('markup: the Mixed Quiz screen was not found');
  var e = INDEX.indexOf('<section', s + 10);
  return INDEX.slice(s, e === -1 ? INDEX.length : e);
})();

var TAG_STATUS = tagFor('rStatus');
eq('A1 exactly one rStatus element exists', countOf(INDEX, 'id="rStatus"'), 1);
eq('A1 rStatus lives on the Mixed Quiz screen', countOf(ROUND_SCREEN, 'id="rStatus"'), 1);
eq('A1 rStatus is visually hidden by class', attr(TAG_STATUS, 'class'), 'sr-only');
eq('A1 rStatus is a status region', attr(TAG_STATUS, 'role'), 'status');
eq('A1 rStatus announces politely', attr(TAG_STATUS, 'aria-live'), 'polite');
eq('A1 rStatus is read as one whole message', attr(TAG_STATUS, 'aria-atomic'), 'true');
// It must ship EMPTY: a status region with prose in it is announced on load.
ok('A1 rStatus ships empty', /id="rStatus"[^>]*>\s*<\//.test(INDEX));
// Both format blocks take turns being `hidden`, which removes them from the
// accessibility tree - so the one region that must be readable on EVERY question
// cannot live inside either of them.
ok('A1 rStatus sits outside both format blocks', (function () {
  var mcq = ROUND_SCREEN.indexOf('id="rMcq"'), typed = ROUND_SCREEN.indexOf('id="rTyped"');
  var status = ROUND_SCREEN.indexOf('id="rStatus"');
  var next = ROUND_SCREEN.indexOf('id="rNext"');
  // after the typed block has closed and before the controls row
  return mcq !== -1 && typed !== -1 && status > typed && status < next;
})());

// The class has to actually hide it, off-screen but still rendered - display:none
// or visibility:hidden would take it out of the accessibility tree entirely.
var STYLE = (function () {
  var out = '', at = 0;
  while ((at = INDEX.indexOf('<style', at)) !== -1) {
    var s = INDEX.indexOf('>', at) + 1, e = INDEX.indexOf('</style>', s);
    out += INDEX.slice(s, e); at = e;
  }
  // Comments carry no braces, so the naive rule scanner below would glue a comment
  // onto the selector that follows it. Drop them first.
  return out.replace(/\/\*[\s\S]*?\*\//g, '');
})();
function cssBlocks(selectorNeedle) {
  var hits = [], re = /([^{}]+)\{([^{}]*)\}/g, m;
  while ((m = re.exec(STYLE)) !== null) {
    if (m[1].indexOf(selectorNeedle) !== -1) hits.push({ sel: m[1].trim(), body: m[2] });
  }
  return hits;
}
var SR_ONLY = cssBlocks('.sr-only');
ok('A2 a .sr-only rule exists', SR_ONLY.length >= 1);
ok('A2 .sr-only takes it off screen rather than out of the tree', (function () {
  var body = SR_ONLY.map(function (b) { return b.body; }).join(';');
  return body.indexOf('position:absolute') !== -1 &&
         body.indexOf('clip:') !== -1 &&
         body.indexOf('display:none') === -1 &&
         body.indexOf('visibility:hidden') === -1;
})());

// The two programmatic focus targets are reachable by script and NOT inserted into
// the tab order - tabindex="-1" is exactly that pair of properties.
var TAG_PL = tagFor('rPl');
eq('A3 rPl is focusable by script only', attr(TAG_PL, 'tabindex'), '-1');
eq('A3 exactly one rPl exists', countOf(INDEX, 'id="rPl"'), 1);
ok('A3 rPl is still the Polish prompt', attr(TAG_PL, 'lang') === 'pl' &&
   (attr(TAG_PL, 'class') || '').indexOf('q-prompt') !== -1);
ok('A3 rPl is not made a tab stop', attr(TAG_PL, 'tabindex') !== '0');
var TAG_DONE_TITLE = tagFor('rDoneTitle');
eq('A3 the completion focus target is focusable by script only', attr(TAG_DONE_TITLE, 'tabindex'), '-1');
ok('A3 the completion focus target is a heading', /^<h[1-6]\b/.test(TAG_DONE_TITLE));
eq('A3 exactly one completion focus target exists', countOf(INDEX, 'id="rDoneTitle"'), 1);
ok('A3 the completion heading still reads "Brawo!"',
   /id="rDoneTitle"[^>]*>Brawo!</.test(INDEX));

// Phase 4C adds a third anchor: the question-type line, which a "listen" question
// falls back to while the manifest is still loading and Play is closed.
var TAG_TYPE = tagFor('rType');
eq('A3 the question-type line is focusable by script only', attr(TAG_TYPE, 'tabindex'), '-1');
eq('A3 exactly one question-type line exists', countOf(INDEX, 'id="rType"'), 1);
ok('A3 the question-type line is not made a tab stop', attr(TAG_TYPE, 'tabindex') !== '0');
ok('A3 the question-type line is not a control', /^<div\b/.test(TAG_TYPE));
// The focus anchors may drop their ring - they are not tab stops - but no control
// the learner can actually Tab to is allowed to lose its indicator.
ok('A3 any ring suppression names the Mixed Quiz anchors and nothing else', (function () {
  var suppress = cssBlocks(':focus').filter(function (b) {
    return /outline\s*:\s*(none|0)/.test(b.body) && /rType|rPl|rDoneTitle/.test(b.sel);
  });
  if (!suppress.length) return true;                  // leaving the default ring on is a fine choice too
  return suppress.every(function (b) {
    return b.sel.split(',').every(function (s) { return /^#(rType|rPl|rDoneTitle):focus$/.test(s.trim()); });
  });
})());
ok('A3 the real Mixed Quiz controls keep a focus indicator', (function () {
  var killed = cssBlocks(':focus').filter(function (b) { return /outline\s*:\s*(none|0)/.test(b.body); })
    .map(function (b) { return b.sel; }).join(' ');
  return killed.indexOf('.opt') === -1 && killed.indexOf('rPlay') === -1 &&
         killed.indexOf('rNext') === -1 && killed.indexOf('rInput') === -1 &&
         killed.indexOf('.ctrl') === -1 && killed.indexOf('.t-input') === -1 &&
         cssBlocks('.opt:focus-visible').length >= 1;
})());
// Phase 3D's Listening anchors are a separate rule and must stay that way - one
// activity's ring suppression must never quietly cover another's controls.
ok('A3 the Listening anchors keep their own rule', (function () {
  return cssBlocks('#lPrompt:focus').length >= 1;
})());

// One predictable immediate region for the multiple-choice result, not two
// competing polite ones.
var TAG_FB = tagFor('rFb');
eq('A4 rFb is no longer a live region', attr(TAG_FB, 'aria-live'), null);
eq('A4 rFb is not a status or alert region either', attr(TAG_FB, 'role'), null);
ok('A4 rFb is still the visible feedback panel',
   (attr(TAG_FB, 'class') || '').indexOf('fb-box') !== -1);
eq('A4 the Mixed Quiz screen has exactly one status region', countOf(ROUND_SCREEN, 'role="status"'), 1);
eq('A4 the Mixed Quiz screen has exactly one atomic region', countOf(ROUND_SCREEN, 'aria-atomic="true"'), 1);
// Three polite regions remain, and they answer three different questions: how far
// through the round, the typed verdict, and the immediate result. They cannot fire
// together - a typed submission writes one, a multiple-choice answer the other.
ok('A4 the remaining polite regions are the counter, the typed verdict and the status',
   countOf(ROUND_SCREEN, 'aria-live="polite"') === 3 &&
   ROUND_SCREEN.indexOf('id="rCountLbl" aria-live="polite"') !== -1 &&
   attr(tagFor('rVerdict'), 'aria-live') === 'polite');
ok('A4 the typed verdict region was left alone', attr(tagFor('rVerdict'), 'role') === null);

// The visible, non-colour cue. Words, driven off the classes the code already sets.
var CUE_CORRECT = cssBlocks('.opt.correct::after');
var CUE_WRONG = cssBlocks('.opt.wrong::after');
ok('A5 a visible cue is attached to the correct option', CUE_CORRECT.length >= 1);
ok('A5 a visible cue is attached to a wrong option', CUE_WRONG.length >= 1);
ok('A5 the option colour states still exist',
   cssBlocks('.opt.correct').length >= 1 && cssBlocks('.opt.wrong').length >= 1);
// What the browser actually PAINTS, not what was typed.
function renderedContent(blocks) {
  var m = blocks.map(function (b) { return b.body; }).join(' ').match(/content\s*:\s*"([^"]*)"/);
  if (!m) return null;
  return m[1].replace(/\\([0-9a-fA-F]{1,6})[ ]?/g, function (_, hex) {
    return String.fromCharCode(parseInt(hex, 16));
  });
}
// Compared character by character rather than against a pasted literal: the
// separator is a no-break space, and a suite that happened to be typed with an
// ordinary one would fail on text the browser paints correctly.
function paintedParts(blocks) {
  var s = renderedContent(blocks);
  if (s === null) return null;
  return { mark: s.charAt(0), sep: s.charCodeAt(1), word: s.slice(2) };
}
var PAINTED_OK = paintedParts(CUE_CORRECT), PAINTED_WRONG = paintedParts(CUE_WRONG);
eq('A5 the correct cue still paints a tick', PAINTED_OK.mark, '✓');
eq('A5 the correct cue still paints the word', PAINTED_OK.word, 'Correct');
eq('A5 the wrong cue still paints a cross', PAINTED_WRONG.mark, '✕');
eq('A5 the wrong cue still paints the words', PAINTED_WRONG.word, 'Try again');
eq('A5 the correct mark is separated from its word', PAINTED_OK.sep, 0x00a0);
eq('A5 the wrong mark is separated from its words', PAINTED_WRONG.sep, 0x00a0);
ok('A5 the cue takes its own line rather than sitting beside the gloss',
   CUE_CORRECT.concat(CUE_WRONG).some(function (b) { return b.body.indexOf('display:block') !== -1; }));
ok('A5 nothing in the cue forces the button wider', (function () {
  var all = CUE_CORRECT.concat(CUE_WRONG).map(function (b) { return b.body; }).join(' ');
  return all.indexOf('white-space:nowrap') === -1 && all.indexOf('position:absolute') === -1;
})());

// =========================================================================
// A FAKE DOM WITH REAL FOCUS RULES
// =========================================================================
// Three browser behaviours are modelled beyond the obvious, and they are the three
// this phase exists to survive:
//   focus() on a disabled element is a no-op,
//   focus() on a hidden element is a no-op, and
//   disabling the focused element hands focus to <body>.
var BODY = null, ACTIVE = null, HTML_WRITES = {};

function FakeEl(tag) {
  this.tag = tag || 'div';
  this.className = '';
  this._disabled = false;
  this.hidden = false;
  this.value = '';
  this.style = {};
  this.children = [];
  this.classes = {};
  this._own = '';
  this._html = '';
  this._attrs = {};
  this._on = {};
  this.focusCount = 0;
  var self = this;
  this.classList = {
    add: function (c) { self.classes[c] = true; },
    remove: function (c) { delete self.classes[c]; },
    contains: function (c) { return !!self.classes[c]; }
  };
}
Object.defineProperty(FakeEl.prototype, 'disabled', {
  get: function () { return this._disabled; },
  set: function (v) {
    this._disabled = !!v;
    if (this._disabled && ACTIVE === this) ACTIVE = BODY;      // the browser rule this phase trips over
  }
});
// textContent as the real property behaves: reading concatenates descendants,
// writing replaces every child with one run of text.
Object.defineProperty(FakeEl.prototype, 'textContent', {
  get: function () {
    if (!this.children.length) return this._own;
    return this.children.map(function (c) { return c.textContent; }).join('');
  },
  set: function (v) { this._own = String(v); this.children = []; this._html = ''; }
});
// innerHTML parses just far enough for the verdict panel to be inspectable: one
// flat child per tag, carrying that tag's class. Nothing here is used to judge
// SAFETY - the safety claim in section J is that the status region and the option
// names are never written through this property at all.
Object.defineProperty(FakeEl.prototype, 'innerHTML', {
  get: function () { return this._html; },
  set: function (v) {
    this._html = String(v);
    HTML_WRITES[this.id] = (HTML_WRITES[this.id] || 0) + 1;
    this._own = '';
    this.children = [];
    var re = /<([a-zA-Z][\w-]*)([^>]*)>/g, m;
    while ((m = re.exec(this._html)) !== null) {
      if (m[1].toLowerCase() === 'br') continue;
      var kid = new FakeEl(m[1]);
      var cm = m[2].match(/\sclass\s*=\s*"([^"]*)"/);
      if (cm) kid.className = cm[1];
      var lm = m[2].match(/\slang\s*=\s*"([^"]*)"/);
      if (lm) kid.setAttribute('lang', lm[1]);
      this.children.push(kid);
    }
  }
});
Object.defineProperty(FakeEl.prototype, 'childNodes', { get: function () { return this.children; } });
FakeEl.prototype.appendChild = function (el) { this.children.push(el); return el; };
FakeEl.prototype.setAttribute = function (k, v) { this._attrs[k] = String(v); };
FakeEl.prototype.getAttribute = function (k) { return Object.prototype.hasOwnProperty.call(this._attrs, k) ? this._attrs[k] : null; };
FakeEl.prototype.addEventListener = function (t, fn) { (this._on[t] = this._on[t] || []).push(fn); };
FakeEl.prototype.click = function () { (this._on.click || []).forEach(function (fn) { fn({}); }); };
FakeEl.prototype.focus = function () {
  if (this._disabled) return;                                   // a disabled control cannot take focus
  if (this.hidden) return;                                      // nor can one that is not rendered
  this.focusCount++;
  ACTIVE = this;
};
FakeEl.prototype.querySelectorAll = function (sel) {
  var want = sel.replace('.', '');
  return this.children.filter(function (c) { return (' ' + c.className + ' ').indexOf(' ' + want + ' ') !== -1; });
};
FakeEl.prototype.querySelector = function (sel) {
  var hits = this.querySelectorAll(sel);
  return hits.length ? hits[0] : null;
};
// The accessible name as a browser computes it for these buttons: aria-label wins
// outright, otherwise the button's own text. CSS ::after is decoration and is
// deliberately NOT part of it - that is why the label is set in script.
FakeEl.prototype.accName = function () {
  var l = this.getAttribute('aria-label');
  return l === null ? this.textContent : l;
};

var DOM = {};
function el(id) {                                               // index.html's $()
  if (!DOM[id]) { DOM[id] = new FakeEl('#' + id); DOM[id].id = id; }
  return DOM[id];
}
var fakeDoc = {
  createElement: function (t) { return new FakeEl(t); },
  createTextNode: function (t) { var n = { nodeType: 3, textContent: String(t) }; return n; }
};

// ---------- the rest of the environment the extracted code runs in ----------
var window = {};                                                // the shared helpers attach themselves here
(0, eval)(readFile(ROOT + 'pp-usage.js'));
(0, eval)(readFile(ROOT + 'pp-answer.js'));
var PP_ANSWER = window.PP_ANSWER;                               // the REAL comparator decides typed verdicts
var ppMainAudioText = window.PP_USAGE.mainAudioText;            // index.html binds them the same way
var ppHasMainAudio = window.PP_USAGE.hasMainAudio;

// Audio appears here only as a counter. What speakCardMain actually does is owned
// by tests/test_audio_fallback.js; this stand-in exists so that "the render path
// started nothing" is observable as "no clip and no utterance was ever constructed",
// rather than as "the stub we wrote was not called".
var AUDIO_MADE = [], UTTER_MADE = [], SPOKEN = [];
function Audio(src) { AUDIO_MADE.push(src); }
function SpeechSynthesisUtterance(t) { UTTER_MADE.push(t); }
var audioMap = {};
function speakCardMain(card, btn) {
  SPOKEN.push(card.pl);
  var clip = audioMap[card.pl];
  if (clip) { new Audio(clip); } else { new SpeechSynthesisUtterance(card.pl); }
}
// Phase 4C gates the Play button on the shared manifest status, so this file needs
// the real status model and the real settlement function - focus is the thing it
// owns, and "settlement steals no focus" cannot be asserted against a stub of the
// function that would do the stealing. Everything else about the manifest (parsing,
// the single fetch, the fallback latch) stays owned by tests/test_audio_fallback.js,
// and the whole Mixed Quiz audio lifecycle by tests/test_mixed_audio.js.
var audioManifestStatus = 'ready';
var syncListeningCalls = 0;
function syncListeningAudioReadiness() { syncListeningCalls++; }
function syncRoundAudioReadiness() { return MIXED.syncReadiness(); }
// The real settlement function, and the real normalizer it keys the map with.
['ppNormalize', 'settleAudioManifest'].forEach(function (n) { (0, eval)(extractFunction(INDEX, n)); });
// A manifest that covers whatever the current fixture is using.
function manifestFor(cards) {
  var e = {}, i = 0;
  cards.forEach(function (c) { e['e' + (i++)] = { pl: c.pl, file: 'audio/r-' + c.id + '.mp3' }; });
  return { entries: e };
}
// stopAllAudio is reached by Phase 4C's boundary helpers. What it does to a real
// clip is owned by tests/test_audio_fallback.js; here it only has to exist, and to
// record that the boundary ran, so the focus assertions can run past it.
var STOPS = 0;
function stopAllAudio() { STOPS++; }

var shown = [];
// The `active` class moves the way index.html's showScreen moves it. Phase 4C's
// readiness helper and playback guard both ask whether the Mixed Quiz screen is up,
// so a fake show() that only logged the name would leave the Play button closed on
// every question and every focus assertion below would be about the wrong state.
var SCREENS = ['home', 'round', 'listen', 'study'];
function fakeShow(scr) {
  shown.push(scr);
  SCREENS.forEach(function (s) { el(s).classList.remove('active'); });
  el(scr).classList.add('active');
}
// gShuffle is deterministic and swappable: identity by default, so rBuildOptions
// leaves the correct gloss LAST, and a reversing variant for the one case that
// needs it first (a wrong LAST option, which is what proves the focus wrap).
function identity(a) { return a.slice(); }
function reverse(a) { return a.slice().reverse(); }
var SHUFFLE = identity;
function fakeShuffle(a) { return SHUFFLE(a); }
function fakeEligible() { return true; }                        // owned by tests/test_typeit_eligibility.js
function fakeAppendUsage() {}                                   // owned by tests/test_activities.js
function ppVariantPartsStub() { return null; }                  // owned by tests/test_typeit_feedback.js
var PROGRESS_WRITABLE = false, SAVED = [], STORE = { progress: {} };
function fakeProgressWritable() { return PROGRESS_WRITABLE; }
function fakeLoadV2() { return STORE; }
function fakeSaveV2(s) { SAVED.push(JSON.parse(JSON.stringify(s))); STORE = s; }

// A six-card topic. Distinct glosses, so rBuildOptions returns four options every
// time; one card carries an example, one carries a diacritic so the typed "almost"
// tier is reachable, and the round is fully deterministic.
// With an identity shuffle the formats cycle listen / type / mc from question 0.
var PLAIN_CARDS = [
  { id: 'm1', pl: 'kawa',    en: 'coffee', ex: 'Poproszę kawę.', exEn: 'A coffee, please.' },
  { id: 'm2', pl: 'mąka',    en: 'flour' },
  { id: 'm3', pl: 'woda',    en: 'water' },
  { id: 'm4', pl: 'sok',     en: 'juice' },
  { id: 'm5', pl: 'mleko',   en: 'milk' },
  { id: 'm6', pl: 'chleb',   en: 'bread' }
];
// Authored content that would become markup if anything interpolated it.
var NASTY_CARDS = [
  { id: 'n1', pl: '<b>zły</b> & "gorszy"', en: 'bad & <i>worse</i>' },
  { id: 'n2', pl: 'cudzysłów "test"',      en: 'quote "mark" test' },
  { id: 'n3', pl: 'znak <mniejszy',        en: 'less < than' },
  { id: 'n4', pl: "apostrof 'jeden'",      en: "it's an apostrophe" },
  { id: 'n5', pl: 'ampersand & spójnik',   en: 'fish & chips' },
  { id: 'n6', pl: 'cudzy > wiekszy',       en: 'greater > than' }
];
var CARDS = PLAIN_CARDS;
// startRound reads the topic's own cards; poolFor is only the thin-pool fallback,
// which six distinct glosses never reach.
var LEVELS = [{ level: 'A1', topics: [{ id: 'topic-1', name: 'W kawiarni', src: ['A1'],
                                        kind: 'mixed', cards: CARDS }] }];
function fakePoolFor() { return CARDS.map(function (c) { return { c: c, topic: 'W kawiarni' }; }); }

// ---------- reading the wiring out of index.html ----------
// Paren-matching, because a Mixed Quiz handler body contains calls of its own -
// a non-greedy "up to the first );" would cut `()=>{ R.i++; rRender(` in half.
function handlerExpr(id) {
  var re = new RegExp('\\$\\(\\s*["\']' + id + '["\']\\s*\\)\\s*\\.addEventListener\\(\\s*["\']click["\']\\s*,', 'g');
  var hits = [], m;
  while ((m = re.exec(INDEX)) !== null) hits.push(m.index + m[0].length);
  if (hits.length !== 1) throw new Error('wiring: expected exactly one click handler for ' + id + ', found ' + hits.length);
  var start = hits[0], depth = 1, mode = 'code';
  for (var j = start; j < INDEX.length; j++) {
    var c = INDEX[j], n = INDEX[j + 1];
    if (mode === 'line') { if (c === '\n') mode = 'code'; continue; }
    if (mode === 'block') { if (c === '*' && n === '/') { mode = 'code'; j++; } continue; }
    if (mode === 'sq' || mode === 'dq' || mode === 'tpl') {
      if (c === '\\') { j++; continue; }
      if ((mode === 'sq' && c === "'") || (mode === 'dq' && c === '"') || (mode === 'tpl' && c === '`')) mode = 'code';
      continue;
    }
    if (c === '/' && n === '/') { mode = 'line'; j++; continue; }
    if (c === '/' && n === '*') { mode = 'block'; j++; continue; }
    if (c === "'") { mode = 'sq'; continue; }
    if (c === '"') { mode = 'dq'; continue; }
    if (c === '`') { mode = 'tpl'; continue; }
    if (c === '(') depth++;
    else if (c === ')') { depth--; if (depth === 0) return INDEX.slice(start, j).trim(); }
  }
  throw new Error('wiring: unbalanced handler for ' + id);
}

// The Mixed Quiz functions need $, document, show and the app helpers. `$` is
// already taken here - it is JXA's ObjC bridge - so they are handed in as
// PARAMETERS of a generated scope rather than planted as globals. Everything they
// share with the counters above (speakCardMain, Audio) still resolves to the same
// globals, so what runs is one system.
// The last four are Phase 4C's: the Play button's readiness state, the guarded
// playback entry point, and the two boundary helpers. rRender calls the first of
// them and the controls route through the rest, so the compiled scope needs them for
// the shipping code to run at all. What they do to AUDIO is asserted in
// tests/test_mixed_audio.js; what they do to FOCUS is asserted here.
var RNAMES = ['rBuildOptions', 'startRound', 'rSetBlocks',
              'rSetStatus', 'rAnnounceWrong', 'rAnnounceCorrect', 'rFocusNextOption',
              'rRender', 'rPickOption', 'rRevealLetter', 'rCheckAnswer', 'rRecord', 'rShowDone',
              'syncRoundAudioReadiness', 'rPlayCurrent', 'rAdvance', 'rExit'];
var RSRC = {};
RNAMES.forEach(function (n) { RSRC[n] = extractFunction(INDEX, n); });
var R_CONTROLS = ['rNext', 'rCheck', 'rHint', 'rPlay', 'rAgain', 'rBack', 'rBackBtn'];
var rStateMatch = INDEX.match(/const\s+R\s*=\s*(\{[^}]*\})\s*;/);
if (!rStateMatch) throw new Error('extract: Mixed Quiz state object R not found in index.html');
var R = (0, eval)('(' + rStateMatch[1] + ')');

var PP_TYPED_INDEX = PP_ANSWER.buildIndex(PLAIN_CARDS.concat(NASTY_CARDS));

var MIXED = (new Function('$', 'document', 'show', 'R', 'LEVELS', 'poolFor', 'gShuffle',
  'ppEligibleFor', 'ppAppendUsageTo', 'ppVariantParts', 'ppProgressWritable', 'loadV2', 'saveV2',
  'PP_ANSWER', 'PP_TYPED_INDEX', 'ppHasMainAudio', 'ppMainAudioText', 'G_AUDIO',
  RNAMES.map(function (n) { return RSRC[n]; }).join('\n') + '\n' +
  'return {\n' +
  '  startRound: function(a,b){ return startRound(a,b); },\n' +
  '  rRender: function(){ return rRender(); },\n' +
  '  rShowDone: function(){ return rShowDone(); },\n' +
  '  syncReadiness: function(){ return syncRoundAudioReadiness(); },\n' +
  '  handlers: {\n' +
  R_CONTROLS.map(function (id) { return '    ' + id + ': (' + handlerExpr(id) + ')'; }).join(',\n') + '\n' +
  '  }\n' +
  '};'
))(el, fakeDoc, fakeShow, R, LEVELS, fakePoolFor, fakeShuffle,
   fakeEligible, fakeAppendUsage, ppVariantPartsStub, fakeProgressWritable, fakeLoadV2, fakeSaveV2,
   PP_ANSWER, PP_TYPED_INDEX, ppHasMainAudio, ppMainAudioText, '<svg data-icon="audio"></svg>');
function activate(id) { return MIXED.handlers[id](); }

// ---------- per-test setup ----------
function reset(o) {
  o = o || {};
  DOM = {}; shown = []; HTML_WRITES = {};
  AUDIO_MADE = []; UTTER_MADE = []; SPOKEN = [];
  SAVED = []; STORE = { progress: {} };
  PROGRESS_WRITABLE = !!o.progress;
  CARDS = o.cards || PLAIN_CARDS;
  LEVELS[0].topics[0].cards = CARDS;
  SHUFFLE = o.shuffle || identity;
  STOPS = 0; syncListeningCalls = 0;
  // Default to a SETTLED manifest: every focus assertion written before Phase 4C
  // describes a round the learner can actually play, and that is the ordinary case.
  // `status: 'loading'` opts a test into the pre-settlement state instead, where the
  // Play button is closed - and audioMap is empty then, which is literally what the
  // app holds while the request is in flight.
  audioManifestStatus = o.status || 'ready';
  audioMap = {};
  if (audioManifestStatus === 'ready') CARDS.forEach(function (c) { audioMap[c.pl] = 'audio/r-' + c.id + '.mp3'; });
  BODY = new FakeEl('body'); BODY.id = 'BODY'; DOM.BODY = BODY;
  ACTIVE = BODY;
  MIXED.startRound(0, 0);
  if (o.at !== undefined) { R.i = o.at; MIXED.rRender(); }
}
function opts() { return el('rOpts').children; }
function status() { return el('rStatus'); }
function q() { return R.qs[R.i]; }
// The correct button for the current question, found the way the app answers -
// the option string that equals the card's own gloss.
function correctBtn() {
  var cur = q(), list = opts();
  for (var i = 0; i < cur.options.length; i++) if (cur.options[i] === cur.c.en) return list[i];
  throw new Error('fixture: no correct option in question ' + R.i);
}
function wrongBtns() {
  var cur = q(), list = opts(), out = [];
  for (var i = 0; i < cur.options.length; i++) if (cur.options[i] !== cur.c.en) out.push(list[i]);
  return out;
}
function labelOf(btn) { return q().options[opts().indexOf(btn)]; }
// What a keyboard learner does: focus the control, then activate it.
function press(btn) { btn.focus(); btn.click(); }
function typeAndCheck(text) { el('rInput').value = text; activate('rCheck'); }

// The fixture must really produce the three formats it claims to, or every
// per-format assertion below is about the wrong question.
reset();
eq('A6 the round is the sampled 15-or-fewer questions', R.qs.length, PLAIN_CARDS.length);
eq('A6 question 0 is the listen format', R.qs[0].fmt, 'listen');
eq('A6 question 1 is the typed format', R.qs[1].fmt, 'type');
eq('A6 question 2 is the multiple-choice format', R.qs[2].fmt, 'mc');
eq('A6 every question has four options', R.qs.filter(function (x) { return x.options.length === 4; }).length, R.qs.length);
eq('A6 the round opened on the Mixed Quiz screen', shown, ['round']);

// =========================================================================
// B. INITIAL QUESTION FOCUS - a new question never starts on <body>
// =========================================================================
reset();                                       // question 0: listen
ok('B1 the listen question was built', opts().length === 4);
ok('B1 focus landed on Play', ACTIVE === el('rPlay'));
ok('B1 focus did not fall back to body', ACTIVE !== BODY);
eq('B1 no clip was created', AUDIO_MADE.length, 0);
eq('B1 no fallback utterance was created', UTTER_MADE.length, 0);
eq('B1 nothing was spoken at all', SPOKEN.length, 0);
eq('B1 Next starts closed', el('rNext').disabled, true);
eq('B1 the status region starts empty', status().textContent, '');
eq('B1 the Polish answer is not shown yet', el('rReveal').textContent, '');

reset({ at: 2 });                              // question 2: mc
ok('B2 focus landed on the Polish prompt', ACTIVE === el('rPl'));
ok('B2 focus did not fall back to body', ACTIVE !== BODY);
ok('B2 focus is not on an option', opts().indexOf(ACTIVE) === -1);
eq('B2 the prompt carries the Polish being glossed', el('rPl').textContent, R.qs[2].c.pl);
eq('B2 no option is selected', opts().filter(function (b) {
  return b.disabled || b.classList.contains('correct') || b.classList.contains('wrong') ||
         b.getAttribute('aria-label') !== null;
}).length, 0);
eq('B2 nothing autoplayed', AUDIO_MADE.length + UTTER_MADE.length + SPOKEN.length, 0);
eq('B2 the status region is empty', status().textContent, '');

reset({ at: 1 });                              // question 1: type
ok('B3 focus landed on the Polish input', ACTIVE === el('rInput'));
ok('B3 focus did not fall back to body', ACTIVE !== BODY);
eq('B3 the input starts empty and open', el('rInput').value + '|' + el('rInput').disabled, '|false');
eq('B3 nothing autoplayed', AUDIO_MADE.length + UTTER_MADE.length + SPOKEN.length, 0);
eq('B3 the typed verdict starts blank', el('rVerdict').innerHTML, '');
eq('B3 the status region is empty', status().textContent, '');

// =========================================================================
// C. A WRONG MULTIPLE-CHOICE ANSWER
// =========================================================================
reset({ at: 2 });
var w1 = wrongBtns()[0], w1Label = labelOf(w1);
press(w1);
ok('C1 the chosen option is marked wrong', w1.classList.contains('wrong'));
ok('C1 the chosen option is disabled', w1.disabled === true);
eq('C1 its accessible name says it was incorrect', w1.accName(), w1Label + ', incorrect. Try again');
ok('C1 its accessible name still names the answer', w1.accName().indexOf(w1Label) === 0);
ok('C1 the visible cue is production CSS driven by the class it just gained',
   w1.classList.contains('wrong') && CUE_WRONG.length >= 1);
ok('C2 the status names the answer that was rejected', status().textContent.indexOf(w1Label) !== -1);
ok('C2 the status says it was not correct', /not correct/i.test(status().textContent));
ok('C2 the status tells the learner to try another', /try another/i.test(status().textContent));
ok('C3 focus moved off the disabled button', ACTIVE !== w1);
ok('C3 focus did not fall back to body', ACTIVE !== BODY);
ok('C3 focus is on another option', opts().indexOf(ACTIVE) !== -1);
ok('C3 the option focused is one that can still be pressed', ACTIVE.disabled === false);
ok('C4 the Polish answer reveal stays hidden', el('rReveal').textContent === '' &&
   el('rReveal').classList.contains('show') === false);
eq('C4 Next stays closed', el('rNext').disabled, true);
eq('C4 the question is not settled', R.state, 'ask');
eq('C5 the question is now marked attempted', R.attempted, true);
eq('C5 no result is banked until the question is answered', q().result, null);
eq('C5 no other option was given an accessible name', opts().filter(function (b) {
  return b !== w1 && b.getAttribute('aria-label') !== null;
}).length, 0);
eq('C5 no other option was disabled', opts().filter(function (b) { return b.disabled; }).length, 1);
eq('C5 no requeue has been created yet', R.qs.length, PLAIN_CARDS.length);
eq('C6 a wrong answer starts no audio', AUDIO_MADE.length + UTTER_MADE.length + SPOKEN.length, 0);
// ...and finishing the question banks exactly the first-attempt miss it always did.
press(correctBtn());
eq('C7 the first-attempt result is missed, exactly as before', R.qs[2].result, 'miss');

// The wrap: the LAST option being wrong must not be a dead end. A reversing
// shuffle puts the correct gloss first, so the last option is a distractor.
reset({ at: 2, shuffle: reverse });
var lastBtn = opts()[opts().length - 1];
ok('C8 fixture guard: the last option is a distractor', labelOf(lastBtn) !== q().c.en);
press(lastBtn);
ok('C8 a wrong last option wraps focus to the top of the list', opts().indexOf(ACTIVE) < opts().length - 1);
ok('C8 ... and lands on an enabled option', ACTIVE.disabled === false);
ok('C8 ... and not on body', ACTIVE !== BODY);

// =========================================================================
// D. SEVERAL WRONG ANSWERS IN A ROW
// =========================================================================
reset({ at: 2 });
var seen = [], said = [];
wrongBtns().forEach(function (b) {
  var lbl = labelOf(b);
  press(b);
  seen.push(b);
  said.push(status().textContent);
  ok('D1 ' + lbl + ' stays disabled', b.disabled === true);
  ok('D1 ' + lbl + ' keeps its wrong marking', b.classList.contains('wrong'));
  ok('D1 ' + lbl + ' keeps its incorrect accessible name', b.accName() === lbl + ', incorrect. Try again');
  ok('D2 focus stayed among the options', opts().indexOf(ACTIVE) !== -1);
  ok('D2 focus is never left on a disabled option', ACTIVE.disabled === false);
  ok('D2 focus never fell to body', ACTIVE !== BODY);
  ok('D3 the announcement names the option just chosen', said[said.length - 1].indexOf(lbl) !== -1);
});
eq('D3 every announcement differed from the one before it',
   said.filter(function (s, i) { return i > 0 && s === said[i - 1]; }).length, 0);
eq('D3 all three announcements are distinct', said.filter(function (s, i) { return said.indexOf(s) === i; }).length, said.length);
eq('D4 every distractor was exhausted', seen.length, 3);
ok('D4 the correct answer is still reachable', correctBtn().disabled === false);
ok('D4 ... and it is where focus now sits', ACTIVE === correctBtn());
eq('D4 the reveal is still hidden and Next still closed',
   el('rReveal').textContent + '|' + el('rNext').disabled, '|true');
press(correctBtn());
eq('D5 answering correctly at last does not recover a first-attempt right', R.qs[2].result, 'miss');
eq('D5 the earlier wrong options are still marked and disabled',
   seen.filter(function (b) { return b.classList.contains('wrong') && b.disabled; }).length, 3);
eq('D5 the earlier wrong options kept their accessible names',
   seen.filter(function (b) { return /incorrect\. Try again$/.test(b.accName()); }).length, 3);
eq('D6 three wrong answers still create exactly one requeue', R.qs.length, PLAIN_CARDS.length + 1);
eq('D6 nothing was played throughout', AUDIO_MADE.length + UTTER_MADE.length + SPOKEN.length, 0);

// =========================================================================
// E. A FIRST-ATTEMPT CORRECT ANSWER
// =========================================================================
reset({ at: 2 });                              // mc: the Polish is the prompt
var cb = correctBtn(), cbLabel = labelOf(cb);
press(cb);
ok('E1 the correct option is marked correct', cb.classList.contains('correct'));
eq('E1 its accessible name says it is correct', cb.accName(), cbLabel + ', correct');
ok('E1 the visible cue is production CSS driven by the class it just gained',
   cb.classList.contains('correct') && CUE_CORRECT.length >= 1);
eq('E2 every option is now closed', opts().filter(function (b) { return b.disabled; }).length, 4);
eq('E2 the untouched options kept their original accessible names',
   opts().filter(function (b) { return b !== cb && b.getAttribute('aria-label') !== null; }).length, 0);
ok('E3 the Polish answer is on screen as the question prompt', el('rPl').textContent === R.qs[2].c.pl);
ok('E4 the status announces success', /^Correct\./.test(status().textContent));
ok('E4 the status carries the Polish answer', status().textContent.indexOf(R.qs[2].c.pl) !== -1);
ok('E4 the status says Next is ready', /Next is ready/.test(status().textContent));
ok('E4 the Polish answer travels in its own lang="pl" node', (function () {
  var pl = status().children.filter(function (n) { return n.getAttribute && n.getAttribute('lang') === 'pl'; });
  return pl.length === 1 && pl[0].textContent === R.qs[2].c.pl;
})());
ok('E4 the English around it is NOT marked Polish',
   status().children.some(function (n) { return !n.getAttribute && /Correct/.test(n.textContent); }));
eq('E5 Next is open', el('rNext').disabled, false);
ok('E5 focus moved to Next', ACTIVE === el('rNext'));
ok('E5 focus did not fall back to body', ACTIVE !== BODY);
eq('E6 the question scores as a first-attempt right', R.qs[2].result, 'right');
eq('E6 a first-attempt right creates no requeue', R.qs.length, PLAIN_CARDS.length);
eq('E6 the question is settled', R.state, 'done');
eq('E7 answering starts no audio', AUDIO_MADE.length + UTTER_MADE.length + SPOKEN.length, 0);

// The listen format reveals the Polish, which the mc format does not need to.
reset();                                       // question 0: listen, and it has an example
press(correctBtn());
eq('E8 the listen format reveals the Polish answer', el('rReveal').textContent, R.qs[0].c.pl);
ok('E8 ... and shows it', el('rReveal').classList.contains('show'));
ok('E8 the example feedback panel still fills for a card that has one',
   el('rFb').innerHTML.indexOf('Poprosz') !== -1 && el('rFb').classList.contains('show'));
ok('E8 the status still announces the result independently of that panel',
   /^Correct\./.test(status().textContent) && status().textContent.indexOf(R.qs[0].c.pl) !== -1);
ok('E8 focus still moved to Next', ACTIVE === el('rNext'));
// The point of the whole phase: an ORDINARY card, with no example and no usage
// label, still says something.
reset({ at: 2 });                              // woda: no ex, no usage, no warning
press(correctBtn());
eq('E9 an ordinary card leaves the optional feedback panel empty', el('rFb').innerHTML, '');
ok('E9 ... and the panel is not shown', el('rFb').classList.contains('show') === false);
ok('E9 ... and the result is still announced', /^Correct\./.test(status().textContent));

// =========================================================================
// F. WRONG, THEN CORRECT
// =========================================================================
reset({ at: 2 });
var fw = wrongBtns()[0], fwLabel = labelOf(fw);
press(fw);
var retryMsg = status().textContent;
press(correctBtn());
ok('F1 the earlier wrong option is still marked', fw.classList.contains('wrong'));
ok('F1 ... and still disabled', fw.disabled === true);
eq('F1 ... and still carries its incorrect name', fw.accName(), fwLabel + ', incorrect. Try again');
ok('F2 the correct option is marked correct', correctBtn().classList.contains('correct'));
eq('F2 ... with the matching accessible name', correctBtn().accName(), labelOf(correctBtn()) + ', correct');
ok('F3 the status changed from retry feedback to success', status().textContent !== retryMsg);
ok('F3 ... and no longer tells the learner to try again', /try another/i.test(status().textContent) === false);
ok('F3 ... and announces the Polish answer', status().textContent.indexOf(R.qs[2].c.pl) !== -1);
ok('F4 focus moved to Next', ACTIVE === el('rNext'));
eq('F4 Next is open', el('rNext').disabled, false);
eq('F5 the question stays scored missed', R.qs[2].result, 'miss');
eq('F6 exactly one requeue was created', R.qs.length, PLAIN_CARDS.length + 1);
eq('F6 the requeued copy is flagged as a second pass', R.qs[R.qs.length - 1].requeued, true);
eq('F6 the requeued copy is the same card', R.qs[R.qs.length - 1].c.id, R.qs[2].c.id);
// A second pass never scores or re-requeues - Phase 4B did not touch that.
R.i = R.qs.length - 1; MIXED.rRender();
press(correctBtn());
eq('F7 the second pass banks no result', R.qs[R.qs.length - 1].result, null);
eq('F7 ... and creates no further requeue', R.qs.length, PLAIN_CARDS.length + 1);

// =========================================================================
// G. THE TYPED QUESTION
// =========================================================================
// Non-empty answers: the verdict, the score and the focus move are exactly what
// they were before this phase.
reset({ at: 1 });                              // mąka
var typedCard = R.qs[1].c;
typeAndCheck(typedCard.pl);
ok('G1 an exact answer reads as right', el('rVerdict').className.indexOf('v-right') !== -1);
eq('G1 ... and scores right', R.qs[1].result, 'right');
eq('G1 ... and settles the question', R.state, 'done');
eq('G1 ... and opens Next', el('rNext').disabled, false);
ok('G1 ... and focus moves to Next', ACTIVE === el('rNext'));
eq('G1 ... and the visible verdict still shows the Polish',
   (el('rVerdict').querySelector('.v-pl') || {}).textContent, typedCard.pl);
eq('G1 ... and the status was not used to repeat the verdict', status().textContent, '');

reset({ at: 1 });
typeAndCheck('maka');                          // the same word without its diacritic
ok('G2 a diacritic slip reads as almost', el('rVerdict').className.indexOf('v-almost') !== -1);
eq('G2 ... and scores almost', R.qs[1].result, 'almost');
ok('G2 ... and focus moves to Next', ACTIVE === el('rNext'));
eq('G2 ... and creates no requeue', R.qs.length, PLAIN_CARDS.length);
eq('G2 ... and the status stayed out of it', status().textContent, '');

reset({ at: 1 });
typeAndCheck('herbata');                       // a different word entirely
ok('G3 a wrong answer reads as wrong', el('rVerdict').className.indexOf('v-wrong') !== -1);
eq('G3 ... and scores missed', R.qs[1].result, 'miss');
ok('G3 ... and focus moves to Next', ACTIVE === el('rNext'));
eq('G3 ... and creates exactly one requeue', R.qs.length, PLAIN_CARDS.length + 1);
eq('G3 ... and the status stayed out of it', status().textContent, '');

// Blank submission: everything about it is unchanged except that it now says why.
['', '   ', '\t \n'].forEach(function (blank) {
  reset({ at: 1 });
  var before = { state: R.state, result: R.qs[1].result, len: R.qs.length,
                 revealed: R.revealed, attempted: R.attempted };
  el('rInput').value = blank;
  el('rNext').focus();                          // park focus away from the input first
  activate('rCheck');
  eq('G4 blank ' + JSON.stringify(blank) + ' scores nothing', R.qs[1].result, before.result);
  eq('G4 blank ' + JSON.stringify(blank) + ' does not settle the question', R.state, before.state);
  eq('G4 blank ' + JSON.stringify(blank) + ' leaves Next disabled', el('rNext').disabled, true);
  eq('G4 blank ' + JSON.stringify(blank) + ' creates no requeue', R.qs.length, before.len);
  eq('G4 blank ' + JSON.stringify(blank) + ' writes no verdict', el('rVerdict').innerHTML, '');
  eq('G4 blank ' + JSON.stringify(blank) + ' leaves the input open', el('rInput').disabled, false);
  eq('G4 blank ' + JSON.stringify(blank) + ' leaves Check open', el('rCheck').disabled, false);
  ok('G5 blank ' + JSON.stringify(blank) + ' returns focus to the input', ACTIVE === el('rInput'));
  ok('G5 blank ' + JSON.stringify(blank) + ' does not leave focus on body', ACTIVE !== BODY);
  eq('G6 blank ' + JSON.stringify(blank) + ' announces the instruction',
     status().textContent, 'Type the Polish answer first.');
});
// ...and a real answer straight afterwards behaves normally, so the instruction is
// not a state the question gets stuck in.
typeAndCheck(typedCard.pl);
ok('G7 a real answer after a blank one still reads as right', el('rVerdict').className.indexOf('v-right') !== -1);
eq('G7 ... and scores right', R.qs[1].result, 'right');
ok('G7 ... and focus moves to Next', ACTIVE === el('rNext'));
// The instruction must not outlive the thing it was asking for: left standing it
// would contradict the verdict for anyone reading the page rather than listening.
eq('G7 ... and retires the blank instruction', status().textContent, '');
eq('G8 the typed path started no audio', AUDIO_MADE.length + UTTER_MADE.length + SPOKEN.length, 0);

// =========================================================================
// H. MOVING TO THE NEXT QUESTION
// =========================================================================
reset({ at: 2 });                              // mc -> the next question is a listen one
press(correctBtn());
var wasOn = ACTIVE;
activate('rNext');                             // exactly what index.html binds to the button
eq('H1 the round advanced', R.i, 3);
eq('H1 the new question is the listen format', q().fmt, 'listen');
eq('H1 the new question has its own options', opts().length, 4);
eq('H1 no option carries a stale accessible name', opts().filter(function (b) {
  return b.getAttribute('aria-label') !== null;
}).length, 0);
eq('H1 no option is marked or closed', opts().filter(function (b) {
  return b.disabled || b.classList.contains('correct') || b.classList.contains('wrong');
}).length, 0);
eq('H2 the old status was cleared', status().textContent, '');
eq('H2 the status has no leftover nodes', status().children.length, 0);
eq('H2 the reveal was cleared', el('rReveal').textContent, '');
eq('H3 Next closed again', el('rNext').disabled, true);
ok('H3 focus moved to Play for the listen format', ACTIVE === el('rPlay'));
ok('H3 focus did NOT stay on the button that was just disabled', ACTIVE !== wasOn);
ok('H3 focus did not fall back to body', ACTIVE !== BODY);
eq('H4 advancing autoplayed nothing', AUDIO_MADE.length + UTTER_MADE.length + SPOKEN.length, 0);

// Every question of a whole round, answered correctly, so "focus never reaches
// body" is a claim about the round rather than about one question.
reset();
var strays = 0, landings = {};
for (var qi = 0; qi < PLAIN_CARDS.length; qi++) {
  if (ACTIVE === BODY) strays++;
  landings[q().fmt] = (landings[q().fmt] || 0) + (ACTIVE === el(q().fmt === 'type' ? 'rInput' : q().fmt === 'listen' ? 'rPlay' : 'rPl') ? 1 : 0);
  if (q().fmt === 'type') typeAndCheck(q().c.pl); else press(correctBtn());
  if (ACTIVE === BODY) strays++;
  activate('rNext');
}
eq('H5 focus never fell to body across a whole round', strays, 0);
eq('H5 every listen question opened on Play', landings.listen, 2);
eq('H5 every typed question opened in the input', landings.type, 2);
eq('H5 every multiple-choice question opened on the Polish prompt', landings.mc, 2);
eq('H5 a fully correct round autoplayed nothing', AUDIO_MADE.length + UTTER_MADE.length + SPOKEN.length, 0);

// A listen question has TWO focus cases, because Phase 4C holds Play closed until
// audio-manifest.json settles. The settled one is asserted above; this is the other.
// Focusing a disabled button does nothing, so without an anchor the learner would be
// dropped on <body> - which is the whole reason the question-type line is focusable.
reset({ status: 'loading', at: 0 });
eq('H6 the current question is a listen question', q().fmt, 'listen');
ok('H6 Play is closed while the manifest is in flight', el('rPlay').disabled === true);
ok('H6 focus did not land on the closed Play button', ACTIVE !== el('rPlay'));
ok('H6 focus did not fall back to body', ACTIVE !== BODY);
ok('H6 focus landed on the stable question prompt', ACTIVE === el('rType'));
eq('H6 the prompt says what the question is', el('rType').textContent, 'What did you hear?');
eq('H6 a loading question autoplayed nothing', AUDIO_MADE.length + UTTER_MADE.length + SPOKEN.length, 0);
// Settlement lands whenever the network answers - long after rRender chose where to
// put focus, and by then the learner may be anywhere on the question. It may open the
// button; it may not move anybody.
var settledFrom = ACTIVE, promptFocuses = el('rType').focusCount;
settleAudioManifest(manifestFor(CARDS));
ok('H7 settlement opened Play', el('rPlay').disabled === false);
eq('H7 settlement restored the ordinary accessible name', el('rPlay').accName(), 'Play the Polish audio');
ok('H7 settlement did not move focus', ACTIVE === settledFrom && ACTIVE === el('rType'));
eq('H7 settlement did not even re-focus the anchor', el('rType').focusCount, promptFocuses);
eq('H7 settlement never focused Play', el('rPlay').focusCount, 0);
eq('H7 settlement autoplayed nothing', AUDIO_MADE.length + UTTER_MADE.length + SPOKEN.length, 0);
eq('H7 settlement still refreshes the Listening button too', syncListeningCalls, 1);
// ...and the same for every other place focus can legitimately be sitting when the
// manifest finally answers. None of these may be pulled away.
[['an option', 2, function () { opts()[0].focus(); return opts()[0]; }],
 ['the typed input', 1, function () { el('rInput').focus(); return el('rInput'); }],
 ['Next after a correct answer', 2, function () { press(correctBtn()); return el('rNext'); }],
 ['the question prompt', 2, function () { return el('rPl'); }]
].forEach(function (spot) {
  reset({ status: 'loading', at: spot[1] });
  var held = spot[2]();
  eq('H8 focus is on ' + spot[0] + ' before settlement', ACTIVE, held);
  var statusBefore = status().textContent;
  settleAudioManifest(manifestFor(CARDS));
  ok('H8 settlement leaves focus on ' + spot[0], ACTIVE === held);
  eq('H8 settlement announces nothing over ' + spot[0], status().textContent, statusBefore);
  eq('H8 settlement plays nothing while focus is on ' + spot[0],
     AUDIO_MADE.length + UTTER_MADE.length + SPOKEN.length, 0);
});
// The completion heading is the last one: a round can finish while the request is
// still in flight on a slow connection.
reset({ status: 'loading' });
R.i = R.qs.length; MIXED.rRender();
eq('H9 completion focus landed on the heading', ACTIVE, el('rDoneTitle'));
settleAudioManifest(manifestFor(CARDS));
ok('H9 settlement leaves the completion heading focused', ACTIVE === el('rDoneTitle'));
ok('H9 settlement leaves the hidden Play button closed', el('rPlay').disabled === true);
eq('H9 settlement on the results screen played nothing',
   AUDIO_MADE.length + UTTER_MADE.length + SPOKEN.length, 0);

// Section I below reads the results screen that the H5 loop left behind, and the
// loading cases above replaced it. Rebuild exactly that state - a whole round
// answered correctly on a settled manifest - so completion is asserted against what
// it was always asserted against.
reset();
for (var qj = 0; qj < PLAIN_CARDS.length; qj++) {
  if (q().fmt === 'type') typeAndCheck(q().c.pl); else press(correctBtn());
  activate('rNext');
}

// =========================================================================
// I. COMPLETION
// =========================================================================
// The loop above advanced past the final question, so the results are showing.
ok('I1 the completion view is showing',
   el('rDone').style.display === 'flex' && el('rMain').style.display === 'none');
ok('I1 focus moved to the completion heading', ACTIVE === el('rDoneTitle'));
ok('I1 focus did not fall back to body', ACTIVE !== BODY);
ok('I1 focus was NOT taken by Practice again', ACTIVE !== el('rAgain') && ACTIVE !== el('rBackBtn'));
eq('I2 the status was cleared', status().textContent, '');
eq('I3 the score is the first-attempt rights', el('rScoreN').textContent, String(PLAIN_CARDS.length));
eq('I3 nothing was almost', el('rAlmostN').textContent, '0');
eq('I3 nothing is to review', el('rMissN').textContent, '0');
eq('I3 the completion wording is unchanged',
   el('rDoneMsg').textContent, 'Every question right on the first try. Świetnie!');
eq('I4 Practice again is an ordinary enabled button', el('rAgain').disabled, false);
eq('I4 Back to topics is an ordinary enabled button', el('rBackBtn').disabled, false);
ok('I4 neither completion button was given a tabindex override',
   attr(tagFor('rAgain'), 'tabindex') === null && attr(tagFor('rBackBtn'), 'tabindex') === null);
ok('I4 the heading comes before the buttons in the tab order',
   INDEX.indexOf('id="rDoneTitle"') < INDEX.indexOf('id="rAgain"'));
eq('I5 completion started no audio', AUDIO_MADE.length + UTTER_MADE.length + SPOKEN.length, 0);

// A mixed round reads the same way, and the three tiers are still the Phase 1B ones.
reset({ progress: true });
for (var qj = 0; qj < PLAIN_CARDS.length; qj++) {
  if (q().fmt === 'type') { typeAndCheck(qj === 1 ? 'maka' : q().c.pl); }
  else if (qj === 2) { press(wrongBtns()[0]); press(correctBtn()); }
  else press(correctBtn());
  activate('rNext');
}
while (R.i < R.qs.length) {                     // work through the one requeued copy
  if (q().fmt === 'type') typeAndCheck(q().c.pl); else press(correctBtn());
  activate('rNext');
}
ok('I6 a mixed round still lands on the heading', ACTIVE === el('rDoneTitle'));
eq('I6 ... with the almost counted separately', el('rAlmostN').textContent, '1');
eq('I6 ... and the retried question counted', el('rMissN').textContent, '1');
eq('I6 ... and the exact answers counted', el('rScoreN').textContent, String(PLAIN_CARDS.length - 2));
eq('I6 ... and a cleared status', status().textContent, '');
ok('I7 progress was still written back to the topic', SAVED.length === 1 &&
   SAVED[0].progress['topic-1'] !== undefined);
ok('I7 ... with the missed card still learning and the right ones known',
   SAVED[0].progress['topic-1'].still.length === 1 &&
   SAVED[0].progress['topic-1'].known.length === PLAIN_CARDS.length - 2);
// "New round" through the shipping handler re-enters a question, not the results.
activate('rAgain');
eq('I8 a new round starts at question one', R.i, 0);
eq('I8 ... with an empty status', status().textContent, '');
ok('I8 ... and focus on the new question', ACTIVE === el('rPlay') && ACTIVE !== BODY);
eq('I8 ... and nothing playing', AUDIO_MADE.length + UTTER_MADE.length + SPOKEN.length, 0);

// =========================================================================
// J. SAFE TEXT INSERTION - authored content is content, never markup
// =========================================================================
reset({ cards: NASTY_CARDS, at: 2 });
var nb = wrongBtns()[0], nbLabel = labelOf(nb);
ok('J1 the fixture really carries markup characters', /[<>&"']/.test(nbLabel));
press(nb);
eq('J1 the option button shows the gloss as text', nb.textContent, nbLabel);
eq('J1 the accessible name carries the raw gloss unescaped', nb.accName(), nbLabel + ', incorrect. Try again');
ok('J1 nothing turned the gloss into markup',
   nb.accName().indexOf('&amp;') === -1 && nb.accName().indexOf('&lt;') === -1);
eq('J2 the status was never written as HTML', HTML_WRITES.rStatus, undefined);
ok('J2 the status carries the raw gloss as text', status().textContent.indexOf(nbLabel) !== -1);
ok('J2 the status is built from real nodes, not one HTML string', status().innerHTML === '');
press(correctBtn());
var nastyPl = R.qs[2].c.pl;
ok('J3 the fixture Polish really carries markup characters', /[<>&"]/.test(nastyPl));
ok('J3 the Polish answer reached the status as text', status().textContent.indexOf(nastyPl) !== -1);
ok('J3 ... inside the lang="pl" node, unescaped', (function () {
  var pl = status().children.filter(function (n) { return n.getAttribute && n.getAttribute('lang') === 'pl'; });
  return pl.length === 1 && pl[0].textContent === nastyPl && pl[0].innerHTML === '';
})());
eq('J3 the status was still never written as HTML', HTML_WRITES.rStatus, undefined);
eq('J3 the correct option name carries the raw gloss unescaped',
   correctBtn().accName(), R.qs[2].c.en + ', correct');
// The prompt and the reveal carry the same authored text, also as text.
eq('J4 the Polish prompt carries the raw Polish as text', el('rPl').textContent, nastyPl);
reset({ cards: NASTY_CARDS });                  // question 0: listen, so the reveal is used
press(correctBtn());
eq('J4 the reveal carries the raw Polish as text', el('rReveal').textContent, R.qs[0].c.pl);
// The blank-answer instruction is authored English and is written as text too.
reset({ cards: NASTY_CARDS, at: 1 });
el('rInput').value = '  ';
activate('rCheck');
eq('J5 the blank instruction is plain text', status().textContent, 'Type the Polish answer first.');
eq('J5 ... and was not written as HTML', HTML_WRITES.rStatus, undefined);
// ...and the source agrees: the status builders never touch innerHTML at all.
['rSetStatus', 'rAnnounceWrong', 'rAnnounceCorrect'].forEach(function (n) {
  ok('J6 ' + n + ' never uses innerHTML', codeOnly(RSRC[n]).indexOf('innerHTML') === -1);
});
// The announcement builders may compose the message and hand it to the writer, so
// the safe-API requirement is on the pair, not on each function in isolation.
['rSetStatus', 'rAnnounceWrong', 'rAnnounceCorrect'].forEach(function (n) {
  ok('J6 ' + n + ' reaches the region through safe DOM APIs only', (function () {
    var s = codeOnly(RSRC[n]) + (n === 'rSetStatus' ? '' : codeOnly(RSRC.rSetStatus));
    return /textContent|createTextNode|createElement|appendChild|replaceChildren/.test(s);
  })());
});
ok('J6 the announcement text is authored in the code, not read from a card field',
   codeOnly(RSRC.rAnnounceWrong).indexOf('not correct') !== -1 &&
   codeOnly(RSRC.rAnnounceCorrect).indexOf('Correct') !== -1);
ok('J6 the accessible names are authored in the code too',
   codeOnly(RSRC.rPickOption).indexOf('incorrect. Try again') !== -1 &&
   codeOnly(RSRC.rPickOption).indexOf(', correct') !== -1);
// Every write to the status region in the whole file goes through a safe API.
ok('J7 no code path writes the status region as markup',
   codeOnly(INDEX).indexOf('rStatus").innerHTML') === -1 &&
   codeOnly(INDEX).indexOf("rStatus').innerHTML") === -1);

// =========================================================================
// K. SOURCE WIRING - the shipping code is what all of the above describes
// =========================================================================
var CODE_RENDER = codeOnly(RSRC.rRender);
var CODE_PICK = codeOnly(RSRC.rPickOption);
var CODE_CHECK = codeOnly(RSRC.rCheckAnswer);
var CODE_DONE = codeOnly(RSRC.rShowDone);

// Every `function rXxx(` in index.html, so the ordering assertions below can be
// judged through what a call REACHES rather than by pinning one helper's name -
// splitting or renaming a helper must not fail this suite as long as the order of
// effects survives. Bodies are stored whitespace-free, so every position compared
// below lives in the same space and reformatting cannot reorder anything.
var R_HELPERS = (function () {
  var out = {}, re = /function\s+(r[A-Za-z0-9_$]*)\s*\(/g, m;
  while ((m = re.exec(INDEX)) !== null) out[m[1]] = squash(codeOnly(extractFunction(INDEX, m[1])));
  return out;
})();
function helperReaches(name, needle, seen) {
  seen = seen || {};
  if (seen[name]) return false;
  seen[name] = true;
  var body = R_HELPERS[name], want = squash(needle);
  if (!body) return false;
  if (body.indexOf(want) !== -1) return true;
  return Object.keys(R_HELPERS).some(function (n) {
    return n !== name && body.indexOf(n + '(') !== -1 && helperReaches(n, needle, seen);
  });
}
// The earliest position in `snippet` at which `needle` is reached - written there
// directly, or through a Mixed Quiz helper called from there.
function reachesAt(snippet, needle) {
  var hay = squash(snippet), best = hay.indexOf(squash(needle));
  Object.keys(R_HELPERS).forEach(function (n) {
    if (!helperReaches(n, needle)) return;
    var at = hay.indexOf(n + '(');
    if (at !== -1 && (best === -1 || at < best)) best = at;
  });
  return best;
}
// The two arms of the answer handler, cut out by brace depth.
function blockAfter(code, from) {
  var open = code.indexOf('{', from), depth = 0;
  for (var j = open; j < code.length; j++) {
    if (code[j] === '{') depth++;
    else if (code[j] === '}') { depth--; if (depth === 0) return { text: code.slice(open, j + 1), end: j + 1 }; }
  }
  throw new Error('wiring: unbalanced answer branch');
}
var ifAt = CODE_PICK.indexOf('if(o===q.c.en)');
ok('K0 the answer handler still branches on the option matching the card gloss', ifAt !== -1);
var CORRECT_ARM = blockAfter(CODE_PICK, ifAt);
var WRONG_ARM = blockAfter(CODE_PICK, CORRECT_ARM.end);
ok('K0 both arms were located',
   CORRECT_ARM.text.indexOf('correct') !== -1 && WRONG_ARM.text.indexOf('wrong') !== -1);

// Wrong answer: say it, THEN move. A reader that is moved first announces the new
// location and swallows the reason it moved.
var wStatus = reachesAt(WRONG_ARM.text, 'rStatus');
var wFocus = reachesAt(WRONG_ARM.text, '.focus(');
ok('K1 the wrong arm writes the status region', wStatus !== -1);
ok('K1 the wrong arm moves focus', wFocus !== -1);
ok('K1 it updates the status BEFORE moving focus', wStatus < wFocus);
ok('K1 it sets an accessible name on the chosen option', WRONG_ARM.text.indexOf('aria-label') !== -1);
ok('K1 it still marks and disables the chosen option',
   hasCode(WRONG_ARM.text, 'btn.classList.add("wrong")') && hasCode(WRONG_ARM.text, 'btn.disabled=true'));
ok('K1 it still closes no other option', WRONG_ARM.text.indexOf('querySelectorAll') === -1);
ok('K1 it still marks the question attempted', hasCode(WRONG_ARM.text, 'R.attempted=true'));
ok('K1 it still banks no result', WRONG_ARM.text.indexOf('rRecord') === -1);
ok('K1 it still does not settle the question', WRONG_ARM.text.indexOf('R.state') === -1);
ok('K1 it still does not touch the reveal', WRONG_ARM.text.indexOf('rReveal') === -1);
ok('K1 it still does not open Next', hasCode(WRONG_ARM.text, 'disabled=false') === false);

// Correct answer: announce and OPEN Next before focusing it - focus cannot land on
// a control that is still disabled.
var ARM_C = squash(CORRECT_ARM.text);
var cStatus = reachesAt(CORRECT_ARM.text, 'rStatus');
var cOpen = ARM_C.indexOf(squash('$("rNext").disabled=false'));
var cFocus = ARM_C.indexOf(squash('$("rNext").focus()'));
ok('K2 the correct arm writes the status region', cStatus !== -1);
ok('K2 it opens Next', cOpen !== -1);
ok('K2 it focuses Next', cFocus !== -1);
ok('K2 it updates the status before focusing Next', cStatus < cFocus);
ok('K2 it opens Next before focusing it', cOpen < cFocus);
ok('K2 it sets an accessible name on the chosen option', CORRECT_ARM.text.indexOf('aria-label') !== -1);
ok('K2 first-attempt scoring is unchanged',
   hasCode(CORRECT_ARM.text, 'rRecord(q, R.attempted ? "miss" : "right")'));
ok('K2 it still closes every option',
   hasCode(CORRECT_ARM.text, 'box.querySelectorAll(".opt").forEach(x=>x.disabled=true)'));
ok('K2 the listen reveal is unchanged', hasCode(CORRECT_ARM.text, '$("rReveal").textContent=q.c.pl'));
ok('K2 usage metadata is still appended', hasCode(CORRECT_ARM.text, 'ppAppendUsageTo(fb, q.c)'));

// rRender owns the new question's focus, per format, and clears the old status.
ok('K3 rRender clears the status region', reachesAt(CODE_RENDER, 'rStatus') !== -1);
ok('K3 rRender assigns a focus target', reachesAt(CODE_RENDER, '.focus(') !== -1);
ok('K3 rRender assigns focus per question format', (function () {
  var tail = squash(CODE_RENDER);
  return tail.indexOf(squash('$("rInput").focus()')) !== -1 &&
         tail.indexOf(squash('$("rPlay")')) !== -1 &&
         tail.indexOf(squash('$("rPl").focus()')) !== -1;
})());
ok('K3 the focus decision reads the question format',
   /q\.fmt===?"(type|listen|mc)"/.test(squash(CODE_RENDER)));
ok('K3 focus is assigned after the options are built', (function () {
  var hay = squash(CODE_RENDER);
  return hay.lastIndexOf(squash('box.appendChild(b)')) < hay.indexOf(squash('$("rPl").focus()'));
})());
ok('K3 the Play button is never focused while it is closed',
   hasCode(CODE_RENDER, '!play.disabled'));
ok('K3 rRender still builds the options as plain strings',
   hasCode(CODE_RENDER, 'b.textContent=o') && CODE_RENDER.indexOf('.label') === -1);
ok('K4 rShowDone focuses the completion heading', hasCode(CODE_DONE, '$("rDoneTitle")') &&
   reachesAt(CODE_DONE, '.focus(') !== -1);
ok('K4 rShowDone clears the status region', reachesAt(CODE_DONE, 'rStatus') !== -1);
ok('K4 rShowDone still reports the three Phase 1B tiers',
   hasCode(CODE_DONE, '$("rScoreN").textContent  = right') &&
   hasCode(CODE_DONE, '$("rAlmostN").textContent = almost') &&
   hasCode(CODE_DONE, '$("rMissN").textContent   = missed'));
ok('K4 rShowDone still writes progress back through the same guard',
   hasCode(CODE_DONE, 'ppProgressWritable()') && hasCode(CODE_DONE, 'saveV2(store)'));

// The blank typed submission: instruction, focus, and nothing else.
var BLANK_ARM = (function () {
  var at = squash(CODE_CHECK).indexOf(squash('if(!PP_ANSWER.normalize(val))'));
  if (at === -1) throw new Error('wiring: the blank guard was not found');
  return blockAfter(squash(CODE_CHECK), at).text;
})();
ok('K5 the blank guard is still the same PP_ANSWER.normalize test',
   hasCode(CODE_CHECK, 'if(!PP_ANSWER.normalize(val))'));
ok('K5 the blank guard writes the status region', BLANK_ARM.indexOf(squash('rStatus')) !== -1);
ok('K5 ... with the authored instruction', BLANK_ARM.indexOf(squash('Type the Polish answer first.')) !== -1);
ok('K5 ... and returns focus to the input', BLANK_ARM.indexOf(squash('$("rInput").focus()')) !== -1);
ok('K5 ... and still returns before anything is scored', BLANK_ARM.indexOf('return;') !== -1);
ok('K5 ... and still scores, settles and requeues nothing',
   BLANK_ARM.indexOf('rRecord') === -1 && BLANK_ARM.indexOf('R.state') === -1 &&
   BLANK_ARM.indexOf(squash('disabled=false')) === -1);
ok('K5 the typed verdict still classifies through the shared comparator',
   hasCode(CODE_CHECK, 'PP_ANSWER.classify(val, c, PP_TYPED_INDEX)'));
ok('K5 a settled typed answer clears the instruction rather than replacing it',
   (function () {
     var hay = squash(CODE_CHECK), at = hay.indexOf(squash('PP_ANSWER.classify('));
     var tail = hay.slice(at);
     return tail.indexOf(squash('$("rStatus").textContent=""')) !== -1 &&
            tail.indexOf(squash('rAnnounce')) === -1;
   })());
ok('K5 the typed verdict still banks through rRecord',
   hasCode(CODE_CHECK, 'rRecord(q, verdict==="wrong" ? "miss" : verdict)'));
ok('K5 the typed verdict still ends on Next',
   hasCode(CODE_CHECK, '$("rNext").disabled=false; $("rNext").focus()'));

// No autoplay anywhere on the render, focus, status or completion path - neither by
// calling a playback helper nor by constructing playback directly. Deliberately
// says nothing about the COMMENTS in these functions: a permanent test must not
// require a particular explanatory note to keep passing. What the learner would
// actually hear is proved by the counters in B, C, E, H and I.
var PLAYBACK = ['speakText', 'speakCardMain', 'stopAllAudio',
                'new Audio', 'SpeechSynthesisUtterance', 'speechSynthesis'];
['rRender', 'rPickOption', 'rShowDone', 'rSetStatus', 'rAnnounceWrong', 'rAnnounceCorrect',
 'rFocusNextOption', 'rCheckAnswer'].forEach(function (n) {
  // eq, not ok: a failure names the playback API that crept in.
  eq('K6 ' + n + ' reaches no playback API',
     PLAYBACK.filter(function (p) { return hasCode(codeOnly(RSRC[n]), p); }), []);
});
// The Play button is still the only thing on a question that starts main-card audio.
// Phase 4C moved its body into a named, guarded entry point - what that guard does is
// asserted in tests/test_mixed_audio.js; all this file needs is that the button still
// leads to speakCardMain and that nothing else in the render path does.
ok('K6 the Play button is still the only playback entry point', (function () {
  var wired = codeOnly(handlerExpr('rPlay')).trim();
  var target = /^([A-Za-z_$][A-Za-z0-9_$]*)$/.test(wired) ? codeOnly(extractFunction(INDEX, wired)) : wired;
  return /speakCardMain\(/.test(target) && /R\.qs\[R\.i\]/.test(target);
})());

// Phase 4D owns the distractor builder. This phase must not have touched it.
var CODE_BUILD = codeOnly(RSRC.rBuildOptions);
ok('K7 rBuildOptions still filters the card and its own gloss out of the pool',
   hasCode(CODE_BUILD, 'pool.filter(c => c !== card && c.en !== card.en)'));
ok('K7 rBuildOptions still takes three distractors and adds the answer',
   hasCode(CODE_BUILD, '.slice(0,3).map(c=>c.en)') && hasCode(CODE_BUILD, 'wrong.concat([card.en])'));
ok('K7 rBuildOptions still shuffles both the pool and the result',
   countOf(squash(CODE_BUILD), 'gShuffle(') === 2);
ok('K7 rBuildOptions gained no accessibility concern at all',
   ['aria', 'focus', 'rStatus', 'Status', 'label'].every(function (t) { return CODE_BUILD.indexOf(t) === -1; }));
ok('K7 the round is still sampled and built the way it was',
   hasCode(codeOnly(RSRC.startRound), 'rBuildOptions(c, dPool)') &&
   hasCode(codeOnly(RSRC.startRound), 'gShuffle(asked).slice(0,15)'));
ok('K7 the requeue rule is unchanged',
   hasCode(codeOnly(RSRC.rRecord), 'if(q.requeued) return;') &&
   hasCode(codeOnly(RSRC.rRecord), 'if(result==="miss")'));

info('assertions run against the shipping Mixed Quiz code in index.html');
info('fake DOM models: focus() on a disabled or hidden element is a no-op; disabling the focused element hands focus to <body>');

// ---------- report ----------
console.log('Mixed Quiz accessibility tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
LOG.forEach(function (l) { console.log('  ' + l); });
if (FAIL > 0) { throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed'); }
