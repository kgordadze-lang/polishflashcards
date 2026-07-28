// Deterministic tests for Listening's non-visual feedback and focus handling.
// Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_listening_accessibility.js
// Exit status is 0 only if every assertion passes (printed at the end).
//
// WHAT THIS PINS DOWN
// Before Priority 3 Phase 3D a Listening answer was told to the learner in colour
// and in nothing else: .opt.correct and .opt.wrong differ only by background,
// border and text colour. A screen reader was handed nothing at all - the one
// polite region on the screen, #lFbBox, holds OPTIONAL material (an example, a
// usage chip, a warning), so an ordinary card announced silence for a correct
// answer, and a rich card announced example prose that never said "correct".
//
// Focus was worse than silent. A wrong option is disabled while it still holds
// focus, and Next is disabled by lRender while IT still holds focus - a browser
// answers both by dropping focus on <body>, so a keyboard learner was thrown back
// to the top of the document twice per question.
//
// This file drives the SHIPPING Listening functions - read out of index.html the
// same way the other index.html suites read theirs - against a fake DOM that
// models the two things that matter here and are usually faked away:
//   * focus() on a disabled element does nothing, and
//   * disabling the focused element moves focus to <body>.
// Without those, "focus went somewhere sensible" is unfalsifiable. With them, a
// missing focus call reads as focus landing on <body>, which is what the learner
// actually experiences.
//
// WHAT IT DELIBERATELY DOES NOT DO
// The audio lifecycle, the manifest load and the fallback de-duplication belong to
// tests/test_audio_fallback.js and are not restated here. Audio appears in this
// file only as a counter, so "the render path started nothing" is observable.
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

var TAG_STATUS = tagFor('lStatus');
eq('A1 exactly one lStatus element exists', countOf(INDEX, 'id="lStatus"'), 1);
eq('A1 lStatus is visually hidden by class', attr(TAG_STATUS, 'class'), 'sr-only');
eq('A1 lStatus is a status region', attr(TAG_STATUS, 'role'), 'status');
eq('A1 lStatus announces politely', attr(TAG_STATUS, 'aria-live'), 'polite');
eq('A1 lStatus is read as one whole message', attr(TAG_STATUS, 'aria-atomic'), 'true');
// It must ship EMPTY: a status region with prose in it is announced on load.
ok('A1 lStatus ships empty', /id="lStatus"[^>]*>\s*<\//.test(INDEX));

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
var TAG_PROMPT = tagFor('lPrompt');
eq('A3 lPrompt is focusable by script only', attr(TAG_PROMPT, 'tabindex'), '-1');
ok('A3 lPrompt is still the question wording', INDEX.indexOf('What did you hear?') !== -1);
ok('A3 lPrompt carries the question wording itself', (function () {
  var at = INDEX.indexOf(TAG_PROMPT);
  return INDEX.slice(at, at + TAG_PROMPT.length + 40).indexOf('What did you hear?') !== -1;
})());
var TAG_DONE_TITLE = tagFor('lDoneTitle');
eq('A3 the completion focus target is focusable by script only', attr(TAG_DONE_TITLE, 'tabindex'), '-1');
ok('A3 the completion focus target is a heading', /^<h[1-6]\b/.test(TAG_DONE_TITLE));
eq('A3 exactly one completion focus target exists', countOf(INDEX, 'id="lDoneTitle"'), 1);

// The focus anchors may drop their ring - they are not tab stops - but no control
// the learner can actually Tab to is allowed to lose its indicator.
ok('A3 any ring suppression names the anchors and nothing else', (function () {
  var suppress = cssBlocks(':focus').filter(function (b) {
    return /outline\s*:\s*(none|0)/.test(b.body) && /lPrompt|lDoneTitle/.test(b.sel);
  });
  if (!suppress.length) return true;                  // leaving the default ring on is a fine choice too
  return suppress.every(function (b) {
    return b.sel.split(',').every(function (s) { return /^#(lPrompt|lDoneTitle):focus$/.test(s.trim()); });
  });
})());
ok('A3 the real Listening controls keep a focus indicator', (function () {
  var killed = cssBlocks(':focus').filter(function (b) { return /outline\s*:\s*(none|0)/.test(b.body); })
    .map(function (b) { return b.sel; }).join(' ');
  return killed.indexOf('.opt') === -1 && killed.indexOf('lPlay') === -1 && killed.indexOf('lNext') === -1 &&
         cssBlocks('.opt:focus-visible').length >= 1;
})());

// One predictable immediate region, not two competing polite ones.
var TAG_FB = tagFor('lFbBox');
eq('A4 lFbBox is no longer a live region', attr(TAG_FB, 'aria-live'), null);
eq('A4 lFbBox is not a status or alert region either', attr(TAG_FB, 'role'), null);
ok('A4 the Listening screen has exactly one polite live region', (function () {
  // the Listening <section> only, so the other activities' regions are not counted
  var s = INDEX.indexOf('<section class="screen" id="listen"'), e = INDEX.indexOf('<section', s + 10);
  var screen = INDEX.slice(s, e);
  return countOf(screen, 'aria-live="polite"') === 2 &&        // the progress counter + lStatus
         screen.indexOf('id="lCountLbl" aria-live="polite"') !== -1 &&
         countOf(screen, 'role="status"') === 1;
})());

// The visible, non-colour cue. Words, driven off the classes the code already sets.
var CUE_CORRECT = cssBlocks('.opt.correct::after');
var CUE_WRONG = cssBlocks('.opt.wrong::after');
ok('A5 a visible cue is attached to the correct option', CUE_CORRECT.length >= 1);
ok('A5 a visible cue is attached to a wrong option', CUE_WRONG.length >= 1);
ok('A5 the correct cue says the word "Correct"', (function () {
  return CUE_CORRECT.some(function (b) { return /content\s*:\s*"[^"]*Correct/.test(b.body); });
})());
ok('A5 the wrong cue says the words "Try again"', (function () {
  return CUE_WRONG.some(function (b) { return /content\s*:\s*"[^"]*Try again/.test(b.body); });
})());
ok('A5 the cue is not an icon alone', (function () {
  var all = CUE_CORRECT.concat(CUE_WRONG).map(function (b) { return b.body; }).join(' ');
  return /content\s*:\s*"[^"]*[A-Za-z]{3}/.test(all);
})());
// What the browser actually PAINTS, not what was typed. A plain space straight after
// a CSS escape is swallowed as that escape's terminator, which printed "✕Try again"
// with the mark jammed against the word - visible only once rendered.
function renderedContent(blocks) {
  var m = blocks.map(function (b) { return b.body; }).join(' ').match(/content\s*:\s*"([^"]*)"/);
  if (!m) return null;
  return m[1].replace(/\\([0-9a-fA-F]{1,6})[ ]?/g, function (_, hex) {
    return String.fromCharCode(parseInt(hex, 16));
  });
}
var PAINTED_OK = renderedContent(CUE_CORRECT), PAINTED_WRONG = renderedContent(CUE_WRONG);
eq('A6 the correct cue paints a mark, a separator and the word', PAINTED_OK, '✓ Correct');
eq('A6 the wrong cue paints a mark, a separator and the words', PAINTED_WRONG, '✕ Try again');
[[PAINTED_OK, 'correct'], [PAINTED_WRONG, 'wrong']].forEach(function (p) {
  ok('A6 the ' + p[1] + ' mark is not jammed against its word', /^\S[\s ]\S/.test(p[0]));
});
// On its own line, so a long English gloss keeps wrapping and nothing is pushed
// sideways at 375px. The colour rules are still there - the cue is additional.
ok('A5 the cue takes its own line rather than sitting beside the gloss', (function () {
  return CUE_CORRECT.concat(CUE_WRONG).some(function (b) { return b.body.indexOf('display:block') !== -1; });
})());
ok('A5 nothing in the cue forces the button wider', (function () {
  var all = CUE_CORRECT.concat(CUE_WRONG).map(function (b) { return b.body; }).join(' ');
  return all.indexOf('white-space:nowrap') === -1 && all.indexOf('position:absolute') === -1;
})());
ok('A5 colour remains as an ADDITIONAL cue on both states', (function () {
  var c = cssBlocks('.opt.correct'), w = cssBlocks('.opt.wrong');
  var base = function (list, needle) {
    return list.some(function (b) { return b.sel.indexOf('::after') === -1 && b.body.indexOf(needle) !== -1; });
  };
  return base(c, 'background') && base(c, 'border-color') && base(w, 'background') && base(w, 'border-color');
})());

// =========================================================================
// A FAKE DOM WITH REAL FOCUS RULES
// =========================================================================
// Only two browser behaviours are modelled beyond the obvious, and they are the
// two this phase exists to survive:
//   focus() on a disabled element is a no-op, and
//   disabling the focused element hands focus to <body>.
var BODY = null, ACTIVE = null, HTML_WRITES = {};

function FakeEl(tag) {
  this.tag = tag || 'div';
  this.className = '';
  this._disabled = false;
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
Object.defineProperty(FakeEl.prototype, 'innerHTML', {
  get: function () { return this._html; },
  set: function (v) {
    this._html = String(v);
    HTML_WRITES[this.id] = (HTML_WRITES[this.id] || 0) + 1;    // section I watches who is written as markup
    this._own = '';
    this.children = this._html ? [new FakeEl('parsed')] : [];
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
  this.focusCount++;
  ACTIVE = this;
};
FakeEl.prototype.querySelectorAll = function (sel) {
  var want = sel.replace('.', '');
  return this.children.filter(function (c) { return (' ' + c.className + ' ').indexOf(' ' + want + ' ') !== -1; });
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
var window = {};                                                // pp-usage.js attaches itself here
(0, eval)(readFile(ROOT + 'pp-usage.js'));
var ppMainAudioText = window.PP_USAGE.mainAudioText;            // index.html binds it the same way
(0, eval)(readFile(ROOT + 'pp-distractor.js'));
var PP_DISTRACTOR = window.PP_DISTRACTOR;                       // the REAL builder decides correctness

// Audio appears here only as a counter. What speakCardMain actually does is owned
// by tests/test_audio_fallback.js; this stand-in exists so that "the render path
// started nothing" is observable as "no clip and no utterance was ever constructed",
// rather than as "the stub we wrote was not called".
var AUDIO_MADE = [], UTTER_MADE = [], STOPS = 0;
function Audio(src) { AUDIO_MADE.push(src); }
function SpeechSynthesisUtterance(t) { UTTER_MADE.push(t); }
var audioMap = {};
var audioManifestStatus = 'ready';
function speakCardMain(card, btn) {
  var clip = audioMap[card.pl];
  if (clip) { new Audio(clip); } else { new SpeechSynthesisUtterance(card.pl); }
}
function stopAllAudio() { STOPS++; }

var shown = [];
function fakeShow(scr) { shown.push(scr); }
function fakeShuffle(a) { return a.slice(); }                   // deterministic: identity
function fakeAppendUsage() {}                                   // owned by tests/test_activities.js

// A five-card topic; distinct glosses and distinct heard prompts, so the real
// builder returns four options every time and the round is fully deterministic.
var PLAIN_CARDS = [
  { id: 'l1', pl: 'kawa',    en: 'coffee', ex: 'Poproszę kawę.', exEn: 'A coffee, please.' },
  { id: 'l2', pl: 'herbata', en: 'tea' },
  { id: 'l3', pl: 'woda',    en: 'water' },
  { id: 'l4', pl: 'sok',     en: 'juice' },
  { id: 'l5', pl: 'mleko',   en: 'milk' }
];
// Authored content that would become markup if anything interpolated it.
var NASTY_CARDS = [
  { id: 'n1', pl: '<b>zły</b> & "gorszy"', en: 'bad & <i>worse</i>' },
  { id: 'n2', pl: 'cudzysłów "test"',      en: 'quote "mark" test' },
  { id: 'n3', pl: 'znak <mniejszy',        en: 'less < than' },
  { id: 'n4', pl: "apostrof 'jeden'",      en: "it's an apostrophe" },
  { id: 'n5', pl: 'ampersand & spójnik',   en: 'fish & chips' }
];
var CARDS = PLAIN_CARDS;
var LEVELS = [{ level: 'A1', topics: [{ name: 'W kawiarni', src: ['A1'], kind: 'listen' }] }];
function fakePoolFor() { return CARDS.map(function (c) { return { c: c, topic: 'W kawiarni' }; }); }

// ---------- reading the wiring out of index.html ----------
function handlerExpr(id) {
  var re = new RegExp('\\$\\(\\s*["\']' + id + '["\']\\s*\\)\\s*\\.addEventListener\\(\\s*["\']click["\']\\s*,([\\s\\S]*?)\\)\\s*;', 'g');
  var hits = [], m;
  while ((m = re.exec(INDEX)) !== null) hits.push(m[1].trim());
  if (hits.length !== 1) throw new Error('wiring: expected exactly one click handler for ' + id + ', found ' + hits.length);
  return hits[0];
}

// The Listening functions need $, document, show and the app helpers. `$` is
// already taken here - it is JXA's ObjC bridge - so they are handed in as
// PARAMETERS of a generated scope rather than planted as globals. Everything they
// share with the counters above (stopAllAudio, speakCardMain, Audio) still
// resolves to the same globals, so what runs is one system.
var LNAMES = ['startListen', 'lRender', 'lPlayCurrent', 'lShowDone', 'lAdvance', 'lExit',
              'syncListeningAudioReadiness',
              'lSetStatus', 'lAnnounceWrong', 'lAnnounceCorrect', 'lFocusNextOption', 'lFocusQuestion'];
var LSRC = {};
LNAMES.forEach(function (n) { LSRC[n] = extractFunction(INDEX, n); });
var L_CONTROLS = ['lNext', 'lBack', 'lHome', 'lAgain', 'lPlay'];
var lStateMatch = INDEX.match(/const\s+L\s*=\s*(\{[^}]*\})\s*;/);
if (!lStateMatch) throw new Error('extract: Listening state object L not found in index.html');
var L = (0, eval)('(' + lStateMatch[1] + ')');

var LISTEN = (new Function('$', 'document', 'show', 'L', 'LEVELS', 'poolFor', 'gShuffle', 'ppAppendUsageTo', 'G_AUDIO',
  LNAMES.map(function (n) { return LSRC[n]; }).join('\n') + '\n' +
  'return {\n' +
  '  startListen: function(a,b){ return startListen(a,b); },\n' +
  '  lRender: function(){ return lRender(); },\n' +
  '  lShowDone: function(){ return lShowDone(); },\n' +
  '  syncReadiness: function(){ return syncListeningAudioReadiness(); },\n' +
  '  handlers: {\n' +
  L_CONTROLS.map(function (id) { return '    ' + id + ': (' + handlerExpr(id) + ')'; }).join(',\n') + '\n' +
  '  }\n' +
  '};'
))(el, fakeDoc, fakeShow, L, LEVELS, fakePoolFor, fakeShuffle, fakeAppendUsage, '<svg data-icon="audio"></svg>');
function activate(id) { return LISTEN.handlers[id](); }

// ---------- per-test setup ----------
function reset(opts) {
  opts = opts || {};
  DOM = {}; shown = []; HTML_WRITES = {};
  AUDIO_MADE = []; UTTER_MADE = []; STOPS = 0;
  CARDS = opts.cards || PLAIN_CARDS;
  audioMap = {};
  CARDS.forEach(function (c) { audioMap[c.pl] = 'audio/l-' + c.id + '.mp3'; });
  audioManifestStatus = opts.loading ? 'loading' : 'ready';
  if (opts.loading) audioMap = {};              // literally what the app holds mid-flight
  BODY = new FakeEl('body'); BODY.id = 'BODY'; DOM.BODY = BODY;
  ACTIVE = BODY;
  LISTEN.startListen(0, 0);
}
function opts() { return el('lOpts').children; }
function status() { return el('lStatus'); }
// The correct button for the current question, found through the BUILDER's flag -
// the same retained identity the app answers by, never a string match on the gloss.
function correctBtn() {
  var q = L.qs[L.i], list = opts();
  for (var i = 0; i < q.options.length; i++) if (q.options[i].correct) return list[i];
  throw new Error('fixture: no correct option in question ' + L.i);
}
function wrongBtns() {
  var q = L.qs[L.i], list = opts(), out = [];
  for (var i = 0; i < q.options.length; i++) if (!q.options[i].correct) out.push(list[i]);
  return out;
}
function labelOf(btn) { var i = opts().indexOf(btn); return L.qs[L.i].options[i].label; }
// What a keyboard learner does: focus the control, then activate it.
function press(btn) { btn.focus(); btn.click(); }

// =========================================================================
// B. INITIAL QUESTION FOCUS
// =========================================================================
reset();
ok('B1 the question was built', opts().length === 4 && el('lCountLbl').textContent === '1 / 15'.replace('15', String(L.qs.length)));
ok('B1 Play is pressable on a settled manifest', el('lPlay').disabled === false);
ok('B1 focus landed on Play', ACTIVE === el('lPlay'));
ok('B1 focus did not fall back to body', ACTIVE !== BODY);
eq('B1 no clip was created', AUDIO_MADE.length, 0);
eq('B1 no fallback utterance was created', UTTER_MADE.length, 0);
eq('B1 Next starts closed', el('lNext').disabled, true);
eq('B1 the status region starts empty', status().textContent, '');

// Mid-flight: Play cannot take focus, so the question prompt does.
reset({ loading: true });
ok('B2 Play stays closed while the manifest is in flight', el('lPlay').disabled === true);
ok('B2 focus landed on the question prompt', ACTIVE === el('lPrompt'));
ok('B2 focus did not fall back to body', ACTIVE !== BODY);
eq('B2 nothing autoplayed', AUDIO_MADE.length + UTTER_MADE.length, 0);
// Settlement opens the button and touches nothing else. The learner may have moved
// on by then, so it must not drag them back.
var beforeSettle = ACTIVE, promptFocuses = el('lPrompt').focusCount;
audioManifestStatus = 'ready';
audioMap = { 'kawa': 'audio/l-l1.mp3' };
LISTEN.syncReadiness();
ok('B3 settlement opened Play', el('lPlay').disabled === false);
ok('B3 settlement did not move focus', ACTIVE === beforeSettle);
eq('B3 settlement did not re-focus the prompt either', el('lPrompt').focusCount, promptFocuses);
eq('B3 settlement never took focus to Play', el('lPlay').focusCount, 0);
eq('B3 settlement played nothing', AUDIO_MADE.length + UTTER_MADE.length, 0);
// ...and the learner who HAS moved down the options is left where they are.
reset({ loading: true });
opts()[2].focus();
var parked = ACTIVE;
audioManifestStatus = 'ready';
LISTEN.syncReadiness();
ok('B4 a learner part-way down the options is not pulled back to Play', ACTIVE === parked);
ok('B4 ... and Play is pressable for when they want it', el('lPlay').disabled === false);

// =========================================================================
// C. A WRONG ANSWER
// =========================================================================
reset();
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
ok('C4 the Polish answer is still hidden', el('lReveal').textContent === '' &&
   el('lReveal').classList.contains('show') === false);
eq('C4 Next stays closed', el('lNext').disabled, true);
eq('C5 the question is now marked attempted', L.attempted, true);
eq('C5 the question is scored missed', L.results[0], false);
eq('C5 no other option was given status text', opts().filter(function (b) {
  return b !== w1 && b.getAttribute('aria-label') !== null;
}).length, 0);
eq('C5 no other option was disabled', opts().filter(function (b) { return b.disabled; }).length, 1);
eq('C6 a wrong answer starts no audio', AUDIO_MADE.length + UTTER_MADE.length, 0);

// The wrap: the LAST option being wrong must not be a dead end.
reset();
var last = opts()[opts().length - 1];
if (!last.classList.contains('correct') && L.qs[0].options[opts().length - 1].correct === false) {
  press(last);
  ok('C7 a wrong last option wraps focus to the top of the list', opts().indexOf(ACTIVE) < opts().length - 1);
  ok('C7 ... and lands on an enabled option', ACTIVE.disabled === false);
} else {
  ok('C7 fixture guard: the last option is a distractor', false);
}

// =========================================================================
// D. SEVERAL WRONG ANSWERS IN A ROW
// =========================================================================
reset();
var seen = [], said = [];
wrongBtns().forEach(function (b) {
  press(b);
  seen.push(b);
  said.push(status().textContent);
  ok('D1 ' + labelOf(b) + ' stays disabled', b.disabled === true);
  ok('D1 ' + labelOf(b) + ' keeps its wrong marking', b.classList.contains('wrong'));
  ok('D2 focus stayed among the options', opts().indexOf(ACTIVE) !== -1);
  ok('D2 focus is never left on a disabled option', ACTIVE.disabled === false);
  ok('D3 the announcement names the option just chosen', said[said.length - 1].indexOf(labelOf(b)) !== -1);
});
eq('D3 every announcement differed from the one before it',
   said.filter(function (s, i) { return i > 0 && s === said[i - 1]; }).length, 0);
eq('D3 all three announcements are distinct', said.filter(function (s, i) { return said.indexOf(s) === i; }).length, said.length);
ok('D4 every distractor was exhausted', seen.length === 3);
ok('D4 the correct answer is still reachable', correctBtn().disabled === false);
ok('D4 ... and it is where focus now sits', ACTIVE === correctBtn());
eq('D5 the question is still scored missed', L.results[0], false);
press(correctBtn());
eq('D5 answering correctly at last does not restore the first-attempt score', L.results[0], false);
ok('D5 ... though the answer is still revealed and Next opens',
   el('lReveal').textContent === L.qs[0].c.pl && el('lNext').disabled === false);
eq('D5 the earlier wrong options are still marked and disabled',
   seen.filter(function (b) { return b.classList.contains('wrong') && b.disabled; }).length, 3);

// =========================================================================
// E. A FIRST-ATTEMPT CORRECT ANSWER
// =========================================================================
reset();
var cb = correctBtn(), cbLabel = labelOf(cb);
press(cb);
ok('E1 the correct option is marked correct', cb.classList.contains('correct'));
eq('E1 its accessible name says it is correct', cb.accName(), cbLabel + ', correct');
ok('E1 the visible cue is production CSS driven by the class it just gained',
   cb.classList.contains('correct') && CUE_CORRECT.length >= 1);
eq('E2 every option is now closed', opts().filter(function (b) { return b.disabled; }).length, 4);
eq('E3 the Polish answer is revealed', el('lReveal').textContent, L.qs[0].c.pl);
ok('E3 ... and shown', el('lReveal').classList.contains('show'));
ok('E4 the status announces success', /^Correct\./.test(status().textContent));
ok('E4 the status carries the Polish answer', status().textContent.indexOf(L.qs[0].c.pl) !== -1);
ok('E4 the status says Next is ready', /Next is ready/.test(status().textContent));
ok('E4 the Polish answer travels in its own lang="pl" node', (function () {
  var pl = status().children.filter(function (n) { return n.getAttribute && n.getAttribute('lang') === 'pl'; });
  return pl.length === 1 && pl[0].textContent === L.qs[0].c.pl;
})());
ok('E4 the English around it is NOT marked Polish', (function () {
  return status().children.some(function (n) { return !n.getAttribute && /Correct/.test(n.textContent); });
})());
eq('E5 Next is open', el('lNext').disabled, false);
ok('E5 focus moved to Next', ACTIVE === el('lNext'));
ok('E5 focus did not fall back to body', ACTIVE !== BODY);
eq('E6 the question scores as a first-attempt success', L.results[0], true);
eq('E6 the round has one result so far', L.results.filter(function (r) { return r === true; }).length, 1);
eq('E7 answering starts no audio', AUDIO_MADE.length + UTTER_MADE.length, 0);
ok('E8 the example feedback panel still fills for a card that has one',
   el('lFbBox').innerHTML.indexOf('Poprosz') !== -1 && el('lFbBox').classList.contains('show'));
// The point of the whole phase: an ORDINARY card, with no example and no usage
// label, still says something.
reset();
L.i = 1; LISTEN.lRender();                    // herbata: no ex, no usage, no warning
press(correctBtn());
eq('E9 an ordinary card leaves the optional feedback panel empty', el('lFbBox').innerHTML, '');
ok('E9 ... and still announces the result', /^Correct\./.test(status().textContent));
ok('E9 ... including the Polish answer', status().textContent.indexOf('herbata') !== -1);

// =========================================================================
// F. WRONG, THEN CORRECT
// =========================================================================
reset();
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
ok('F3 ... and announces the Polish answer', status().textContent.indexOf(L.qs[0].c.pl) !== -1);
ok('F4 focus moved to Next', ACTIVE === el('lNext'));
eq('F4 Next is open', el('lNext').disabled, false);
eq('F5 the question stays scored missed', L.results[0], false);

// =========================================================================
// G. MOVING TO THE NEXT QUESTION
// =========================================================================
reset();
press(correctBtn());
var wasOn = ACTIVE;
activate('lNext');                            // exactly what index.html binds to the button
ok('G1 Phase 3B still silences the question before it changes', STOPS >= 1);
eq('G1 the round advanced', L.i, 1);
eq('G1 the new question has its own options', opts().length, 4);
eq('G1 no option carries a stale status name', opts().filter(function (b) {
  return b.getAttribute('aria-label') !== null;
}).length, 0);
eq('G1 no option is marked or closed', opts().filter(function (b) {
  return b.disabled || b.classList.contains('correct') || b.classList.contains('wrong');
}).length, 0);
eq('G2 the old status was cleared', status().textContent, '');
eq('G2 the status has no leftover nodes', status().children.length, 0);
eq('G2 the reveal was cleared', el('lReveal').textContent, '');
eq('G3 Next closed again', el('lNext').disabled, true);
ok('G3 focus moved to Play', ACTIVE === el('lPlay'));
ok('G3 focus did NOT stay on the button that was just disabled', ACTIVE !== wasOn);
ok('G3 focus did not fall back to body', ACTIVE !== BODY);
eq('G4 advancing autoplayed nothing', AUDIO_MADE.length + UTTER_MADE.length, 0);

// The same move while the manifest is still in flight.
reset({ loading: true });
press(correctBtn());
ok('G5 Next took focus even mid-flight', ACTIVE === el('lNext'));
activate('lNext');
eq('G5 the round advanced', L.i, 1);
ok('G5 Play is still closed', el('lPlay').disabled === true);
ok('G5 focus went to the question prompt instead', ACTIVE === el('lPrompt'));
ok('G5 focus did not fall back to body', ACTIVE !== BODY);
eq('G5 nothing autoplayed', AUDIO_MADE.length + UTTER_MADE.length, 0);

// Every question of a full round, so "focus never reaches body" is a claim about
// the round rather than about question one.
reset();
var strays = 0, landings = {};
for (var qi = 0; qi < L.qs.length; qi++) {
  if (ACTIVE === BODY) strays++;
  landings[ACTIVE === el('lPlay') ? 'play' : 'other'] = true;
  press(correctBtn());
  if (ACTIVE === BODY) strays++;
  activate('lNext');
}
eq('G6 focus never fell to body across a whole round', strays, 0);
ok('G6 every question put focus on Play', landings.other !== true);

// =========================================================================
// H. COMPLETION
// =========================================================================
// The loop above advanced past the final question, so the results are showing.
ok('H1 the completion view is showing',
   el('lDone').style.display === 'flex' && el('lMain').style.display === 'none');
ok('H1 focus moved to the completion heading', ACTIVE === el('lDoneTitle'));
ok('H1 focus did not fall back to body', ACTIVE !== BODY);
ok('H1 focus was NOT taken by New round', ACTIVE !== el('lAgain') && ACTIVE !== el('lHome'));
eq('H2 the status was cleared', status().textContent, '');
eq('H3 the score is the first-attempt successes', el('lScoreN').textContent, String(L.qs.length));
eq('H3 nothing was retried', el('lMissN').textContent, '0');
eq('H3 the completion wording is unchanged',
   el('lDoneMsg').textContent, 'Every one recognised on the first listen. Świetnie!');
eq('H4 New round is an ordinary enabled button', el('lAgain').disabled, false);
eq('H4 Home is an ordinary enabled button', el('lHome').disabled, false);
ok('H4 neither completion button was given a tabindex override',
   attr(tagFor('lAgain'), 'tabindex') === null && attr(tagFor('lHome'), 'tabindex') === null);
ok('H4 the heading comes before the buttons in the tab order',
   INDEX.indexOf('id="lDoneTitle"') < INDEX.indexOf('id="lAgain"'));
eq('H5 completion started no audio', AUDIO_MADE.length + UTTER_MADE.length, 0);
// A partly-missed round reads the same way.
reset();
press(wrongBtns()[0]); press(correctBtn());
for (var k = 0; k < L.qs.length; k++) { activate('lNext'); if (L.i < L.qs.length) press(correctBtn()); }
ok('H6 a partly-missed round still lands on the heading', ACTIVE === el('lDoneTitle'));
eq('H6 ... with the retried question counted', el('lMissN').textContent, '1');
eq('H6 ... and the shipped wording for a partial round',
   el('lDoneMsg').textContent, 'You recognised ' + (L.qs.length - 1) + ' of ' + L.qs.length + ' on the first listen.');
eq('H6 ... and a cleared status', status().textContent, '');

// =========================================================================
// I. ACCESSIBLE-NAME AND STATUS SAFETY
// =========================================================================
reset({ cards: NASTY_CARDS });
var nb = wrongBtns()[0], nbLabel = labelOf(nb);
ok('I1 the fixture really carries markup characters', /[<>&"']/.test(nbLabel));
press(nb);
eq('I1 the option button shows the gloss as text', nb.textContent, nbLabel);
eq('I1 the accessible name carries the raw gloss unescaped', nb.accName(), nbLabel + ', incorrect. Try again');
ok('I1 nothing turned the gloss into markup', nb.accName().indexOf('&amp;') === -1 &&
   nb.accName().indexOf('&lt;') === -1);
eq('I2 the status was never written as HTML', HTML_WRITES.lStatus, undefined);
ok('I2 the status carries the raw gloss as text', status().textContent.indexOf(nbLabel) !== -1);
ok('I2 the status is built from real nodes, not one HTML string', status().innerHTML === '');
press(correctBtn());
var nastyPl = L.qs[0].c.pl;
ok('I3 the fixture Polish really carries markup characters', /[<>&"]/.test(nastyPl));
ok('I3 the Polish answer reached the status as text', status().textContent.indexOf(nastyPl) !== -1);
ok('I3 ... inside the lang="pl" node, unescaped', (function () {
  var pl = status().children.filter(function (n) { return n.getAttribute && n.getAttribute('lang') === 'pl'; });
  return pl.length === 1 && pl[0].textContent === nastyPl && pl[0].innerHTML === '';
})());
eq('I3 the status was still never written as HTML', HTML_WRITES.lStatus, undefined);
eq('I4 the reveal carries the raw Polish as text', el('lReveal').textContent, nastyPl);
// ...and the source agrees: the status builders never touch innerHTML at all.
['lSetStatus', 'lAnnounceWrong', 'lAnnounceCorrect'].forEach(function (n) {
  ok('I5 ' + n + ' never uses innerHTML', codeOnly(LSRC[n]).indexOf('innerHTML') === -1);
});
// The announcement builders may compose the message and hand it to the writer, so
// the safe-API requirement is on the pair, not on each function in isolation.
['lSetStatus', 'lAnnounceWrong', 'lAnnounceCorrect'].forEach(function (n) {
  ok('I5 ' + n + ' reaches the region through safe DOM APIs only', (function () {
    var s = codeOnly(LSRC[n]) + (n === 'lSetStatus' ? '' : codeOnly(LSRC.lSetStatus));
    return /textContent|createTextNode|createElement|appendChild|replaceChildren/.test(s);
  })());
});
ok('I5 the announcement text is authored in the code, not read from a card field',
   codeOnly(LSRC.lAnnounceWrong).indexOf('not correct') !== -1 &&
   codeOnly(LSRC.lAnnounceCorrect).indexOf('Correct') !== -1);

// =========================================================================
// J. SOURCE WIRING - the shipping code is what all of the above describes
// =========================================================================
var SRC_LRENDER = extractFunction(INDEX, 'lRender');
var CODE_LRENDER = codeOnly(SRC_LRENDER);
var CODE_SHOWDONE = codeOnly(LSRC.lShowDone);
var CODE_SYNC = codeOnly(LSRC.syncListeningAudioReadiness);

// Every `function lXxx(` in index.html, so the ordering assertions below can be
// judged through what a call REACHES rather than by pinning one helper's name -
// splitting or renaming a helper must not fail this suite as long as the order of
// effects survives.
// Bodies are stored whitespace-free, so every position compared below lives in the
// same space and reformatting cannot reorder anything.
var L_HELPERS = (function () {
  var out = {}, re = /function\s+(l[A-Za-z0-9_$]*)\s*\(/g, m;
  while ((m = re.exec(INDEX)) !== null) out[m[1]] = squash(codeOnly(extractFunction(INDEX, m[1])));
  return out;
})();
// Does calling this helper reach `needle`, directly or through another Listening
// helper? Walks the call graph to a fixed point; the visited set makes a cycle
// terminate rather than recurse.
function helperReaches(name, needle, seen) {
  seen = seen || {};
  if (seen[name]) return false;
  seen[name] = true;
  var body = L_HELPERS[name], want = squash(needle);
  if (!body) return false;
  if (body.indexOf(want) !== -1) return true;
  return Object.keys(L_HELPERS).some(function (n) {
    return n !== name && body.indexOf(n + '(') !== -1 && helperReaches(n, needle, seen);
  });
}
// The earliest position in `snippet` at which `needle` is reached - written there
// directly, or through a Listening helper called from there. Positions are indices
// into the whitespace-free view, so they stay comparable with each other.
function reachesAt(snippet, needle) {
  var hay = squash(snippet), best = hay.indexOf(squash(needle));
  Object.keys(L_HELPERS).forEach(function (n) {
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
var ifAt = CODE_LRENDER.indexOf('if(o.correct)');
ok('J0 the answer handler still branches on the builder\'s retained flag', ifAt !== -1);
var CORRECT_ARM = blockAfter(CODE_LRENDER, ifAt);
var WRONG_ARM = blockAfter(CODE_LRENDER, CORRECT_ARM.end);
ok('J0 both arms were located',
   CORRECT_ARM.text.indexOf('correct') !== -1 && WRONG_ARM.text.indexOf('wrong') !== -1);

// Wrong answer: say it, THEN move. A reader that is moved first announces the new
// location and swallows the reason it moved.
var wStatus = reachesAt(WRONG_ARM.text, 'lStatus');
var wFocus = reachesAt(WRONG_ARM.text, '.focus(');
ok('J1 the wrong arm writes the status region', wStatus !== -1);
ok('J1 the wrong arm moves focus', wFocus !== -1);
ok('J1 it updates the status BEFORE moving focus', wStatus < wFocus);
ok('J1 it sets an accessible name on the chosen option', WRONG_ARM.text.indexOf('aria-label') !== -1);
// Marked and closed, and ONLY the one that was chosen - the giveaway for the latter
// is that this arm never sweeps the option row the way the correct arm does.
ok('J1 it still marks and disables the chosen option',
   hasCode(WRONG_ARM.text, 'b.classList.add("wrong")') && hasCode(WRONG_ARM.text, 'b.disabled=true'));
ok('J1 it still closes no other option', WRONG_ARM.text.indexOf('querySelectorAll') === -1);
ok('J1 it still marks the question missed',
   hasCode(WRONG_ARM.text, 'L.attempted=true') && hasCode(WRONG_ARM.text, 'L.results[L.i]=false'));
ok('J1 it still does not touch the reveal', /rv\s*\.\s*(textContent|classList)/.test(WRONG_ARM.text) === false);
ok('J1 it still does not open Next', hasCode(WRONG_ARM.text, 'disabled=false') === false);

// Correct answer: announce and OPEN Next before focusing it - focus cannot land on
// a control that is still disabled.
var ARM_C = squash(CORRECT_ARM.text);
var cStatus = reachesAt(CORRECT_ARM.text, 'lStatus');
var cOpen = ARM_C.indexOf(squash('$("lNext").disabled=false'));
var cFocus = ARM_C.indexOf(squash('$("lNext").focus()'));
ok('J2 the correct arm writes the status region', cStatus !== -1);
ok('J2 it opens Next', cOpen !== -1);
ok('J2 it focuses Next', cFocus !== -1);
ok('J2 it updates the status before focusing Next', cStatus < cFocus);
ok('J2 it opens Next before focusing it', cOpen < cFocus);
ok('J2 it sets an accessible name on the chosen option', CORRECT_ARM.text.indexOf('aria-label') !== -1);
ok('J2 first-attempt scoring is unchanged',
   hasCode(CORRECT_ARM.text, 'if(!L.attempted) L.results[L.i]=true'));
ok('J2 the reveal is unchanged', hasCode(CORRECT_ARM.text, 'rv.textContent=q.c.pl'));
ok('J2 usage metadata is still appended', hasCode(CORRECT_ARM.text, 'ppAppendUsageTo(fb, q.c)'));

// lRender owns the new question's focus, and clears the old status.
ok('J3 lRender assigns a focus target', reachesAt(CODE_LRENDER, '.focus(') !== -1);
ok('J3 lRender clears the status region', reachesAt(CODE_LRENDER, 'lStatus') !== -1);
ok('J3 lRender still builds the options through the retained option objects',
   hasCode(CODE_LRENDER, 'b.textContent=o.label') && hasCode(CODE_LRENDER, 'o.correct'));
ok('J4 lShowDone assigns a completion focus target', reachesAt(CODE_SHOWDONE, '.focus(') !== -1);
ok('J4 lShowDone clears the status region', reachesAt(CODE_SHOWDONE, 'lStatus') !== -1);
ok('J4 lShowDone still reports first-attempt successes',
   hasCode(CODE_SHOWDONE, 'L.results.filter(Boolean).length'));

// Readiness stays readiness.
ok('J5 syncListeningAudioReadiness never moves focus',
   CODE_SYNC.indexOf('focus') === -1 && reachesAt(CODE_SYNC, '.focus(') === -1);
ok('J5 it still owns only the button state',
   CODE_SYNC.indexOf('btn.disabled') !== -1 && CODE_SYNC.indexOf('aria-busy') !== -1);
ok('J5 settlement reaches it and nothing else new', (function () {
  var settle = codeOnly(extractFunction(INDEX, 'settleAudioManifest'));
  return settle.indexOf('syncListeningAudioReadiness()') !== -1 && settle.indexOf('focus') === -1;
})());

// No autoplay anywhere on the render, focus or status path - neither by calling a
// playback helper nor by constructing playback directly. Deliberately says nothing
// about the COMMENTS in these functions: a permanent test must not require a
// particular explanatory note, or a particular wording of one, to keep passing.
// What the learner would actually hear is proved by the counters in B, C, E, G and
// H, which assert that a whole round creates no Audio object and no utterance.
var PLAYBACK = ['speakText', 'speakCardMain', 'lPlayCurrent',
                'new Audio', 'SpeechSynthesisUtterance', 'speechSynthesis'];
['lRender', 'lShowDone', 'lFocusQuestion', 'lFocusNextOption', 'lSetStatus',
 'lAnnounceWrong', 'lAnnounceCorrect', 'syncListeningAudioReadiness'].forEach(function (n) {
  var s = codeOnly(n === 'lRender' ? SRC_LRENDER : LSRC[n]);
  // eq, not ok: a failure names the playback API that crept in.
  eq('J6 ' + n + ' reaches no playback API',
     PLAYBACK.filter(function (p) { return hasCode(s, p); }), []);
});

// Option identity is still the builder's, not a string match. Scoped to LISTENING
// on purpose: whether any other activity also adopts the shared builder is that
// activity's business, and this suite makes no claim about it either way.
ok('J7 Listening still builds its round through PP_DISTRACTOR',
   hasCode(codeOnly(extractFunction(INDEX, 'startListen')), 'PP_DISTRACTOR.buildOptions'));
ok('J7 the answer handler branches on the option record\'s own correct flag',
   hasCode(CODE_LRENDER, 'if(o.correct)'));
// The strongest available statement that correctness is not a string match: lRender
// never reads the card's English gloss at all, so it has nothing to compare against.
ok('J7 Listening never reads the card gloss when judging an answer',
   CODE_LRENDER.indexOf('q.c.en') === -1);
ok('J7 nor compares an option against it', /o(\.label)?\s*===?\s*q\.c\.en|q\.c\.en\s*===?\s*o(\.label)?/.test(CODE_LRENDER) === false);
// Executed, not merely read: two cards sharing a gloss must still resolve by identity.
(function () {
  var twin = [
    { id: 't1', pl: 'burza', en: 'storm' },
    { id: 't2', pl: 'burza', en: '(thunder)storm' },
    { id: 't3', pl: 'deszcz', en: 'rain' },
    { id: 't4', pl: 'śnieg', en: 'snow' },
    { id: 't5', pl: 'wiatr', en: 'wind' }
  ];
  reset({ cards: twin });
  var q = L.qs[0], flagged = q.options.filter(function (o) { return o.correct; });
  eq('J8 exactly one option is flagged correct', flagged.length, 1);
  ok('J8 the flagged option is the question\'s own card', flagged[0].item.c === q.c);
  press(correctBtn());
  eq('J8 pressing it scores a first-attempt success', L.results[0], true);
  ok('J8 ... and the status announces that card\'s Polish', status().textContent.indexOf(q.c.pl) !== -1);
})();

info('assertions run against the shipping Listening code in index.html');
info('fake DOM models: focus() on a disabled element is a no-op; disabling the focused element hands focus to <body>');

// ---------- report ----------
console.log('Listening accessibility tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
LOG.forEach(function (l) { console.log('  ' + l); });
if (FAIL > 0) { throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed'); }
