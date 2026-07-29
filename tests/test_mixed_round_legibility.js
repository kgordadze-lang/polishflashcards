// Deterministic tests for the MIXED QUIZ's round progress, retry marker and hint report.
// Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_mixed_round_legibility.js
// Exit status is 0 only if every assertion passes (printed at the end).
//
// WHAT THIS PINS DOWN
// Priority 3 Phase 4F. A question missed on the first try is answered again at the
// end of the round, and the retry is APPENDED to R.qs. Every visible measure of "how
// far through" was drawn against that array, so the array growing was something the
// learner read:
//
//   * the counter re-based itself mid-round - one miss on question 1 turned the next
//     question from "2 / 15" into "2 / 16", so the round appeared to get longer as a
//     punishment for missing something;
//   * the progress bar was re-scaled the same way, so finishing all 15 original
//     questions drew 93.75% of a 16-question round rather than a finished one;
//   * the retry itself was invisible - it arrived as "16 / 16" with the ordinary
//     prompt, indistinguishable from a question being asked for the first time;
//   * meanwhile rShowDone went on scoring 15, so the counter and the score described
//     two different rounds.
//
// It also owns the Mixed Quiz's own hint report. "Reveal a letter" existed here with
// no counter behind it, so a typed round leaning on it reported nothing at all, while
// Type It had reported hint use beside its tiers since Phase 2.
//
// HOW IT TESTS
// It drives the SHIPPING Mixed Quiz functions - lifted out of index.html the way the
// other index.html suites lift theirs - against a fake DOM, and reads back the text a
// learner would actually see. Nothing here re-implements the progress arithmetic.
//
// WHAT IT DELIBERATELY DOES NOT DO
// It does not restate what the other Mixed Quiz suites own. Focus order and the
// announcement regions belong to tests/test_mixed_accessibility.js; the audio
// lifecycle to tests/test_mixed_audio.js; which options are built, and why identity
// rather than text decides them, to tests/test_mixed_distractors.js and
// tests/test_sense_groups.js; how a typed verdict is DECIDED to
// tests/test_answer_validation.js; how the tiers are COUNTED to
// tests/test_round_scoring.js. Scoring appears here only as "this phase did not move
// it", and the requeue mechanism only as "this phase did not touch it". Release
// identifiers, comment wording and corpus counts are not pinned: they change on
// purpose, and a permanent progress suite must not fail for that.
ObjC.import('Foundation');

function readFile(path) {
  var s = $.NSString.stringWithContentsOfFileEncodingError(path, $.NSUTF8StringEncoding, null);
  return ObjC.unwrap(s);
}
// The documented command runs from the repo root; also tolerate being run from tests/.
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

// ---------- tiny test framework (same shape as the other suites) ----------
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
      if ((mode === 'sq' && c === "'") || (mode === 'dq' && c === '"') || (mode === 'tpl' && c === '`')) mode = 'code';
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
// Comment-stripped view. Presence and ordering must be decided by CODE, never by
// prose that happens to mention a call - every comment in this area talks about
// R.qs.length in order to explain why it is no longer measured against.
function codeOnly(src) {
  var out = '', mode = 'code';
  for (var j = 0; j < src.length; j++) {
    var c = src[j], n = src[j + 1];
    if (mode === 'line') { if (c === '\n') { mode = 'code'; out += c; } continue; }
    if (mode === 'block') { if (c === '*' && n === '/') { mode = 'code'; j++; } continue; }
    if (mode === 'sq' || mode === 'dq' || mode === 'tpl') {
      out += c;
      if (c === '\\') { out += src[j + 1]; j++; continue; }
      if ((mode === 'sq' && c === "'") || (mode === 'dq' && c === '"') || (mode === 'tpl' && c === '`')) mode = 'code';
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
// Source checks run against a whitespace-free view. Re-indenting a block or breaking a
// long statement over two lines changes none of what the code DOES, so none of it may
// fail a test. What stays pinned is the tokens and their order.
function squash(s) { return s.replace(/\s+/g, ''); }
function hasCode(hay, needle) { return squash(hay).indexOf(squash(needle)) !== -1; }

// ---------- fake DOM ----------
// Modelled on the one tests/test_mixed_accessibility.js uses, minus the focus rules it
// owns: this file reads TEXT, so what matters is that textContent and innerHTML behave
// like the real properties and that writes through the two are distinguishable.
var ACTIVE = null, BODY = null, HTML_WRITES = {};
function FakeEl(tag) {
  this.tag = tag; this.className = ''; this.id = ''; this._disabled = false;
  this.hidden = false; this.value = ''; this.style = {}; this.children = [];
  this.classes = {}; this._own = ''; this._html = ''; this._attrs = {}; this._on = {};
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
  set: function (v) { this._disabled = !!v; if (this._disabled && ACTIVE === this) ACTIVE = BODY; }
});
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
    HTML_WRITES[this.id] = (HTML_WRITES[this.id] || 0) + 1;
    this._own = ''; this.children = [];
    var re = /<([a-zA-Z][\w-]*)([^>]*)>/g, m;
    while ((m = re.exec(this._html)) !== null) {
      if (m[1].toLowerCase() === 'br') continue;
      var kid = new FakeEl(m[1]);
      var cm = m[2].match(/\sclass\s*=\s*"([^"]*)"/);
      if (cm) kid.className = cm[1];
      this.children.push(kid);
    }
  }
});
Object.defineProperty(FakeEl.prototype, 'childNodes', { get: function () { return this.children; } });
FakeEl.prototype.appendChild = function (e) { this.children.push(e); return e; };
FakeEl.prototype.setAttribute = function (k, v) { this._attrs[k] = String(v); };
FakeEl.prototype.getAttribute = function (k) { return Object.prototype.hasOwnProperty.call(this._attrs, k) ? this._attrs[k] : null; };
FakeEl.prototype.addEventListener = function (t, fn) { (this._on[t] = this._on[t] || []).push(fn); };
FakeEl.prototype.click = function () { (this._on.click || []).forEach(function (fn) { fn({}); }); };
FakeEl.prototype.focus = function () { if (this._disabled || this.hidden) return; this.focusCount++; ACTIVE = this; };
FakeEl.prototype.querySelectorAll = function (sel) {
  var want = sel.replace('.', '');
  return this.children.filter(function (c) { return (' ' + c.className + ' ').indexOf(' ' + want + ' ') !== -1; });
};
FakeEl.prototype.querySelector = function (sel) { var h = this.querySelectorAll(sel); return h.length ? h[0] : null; };

var DOM = {};
function el(id) { if (!DOM[id]) { DOM[id] = new FakeEl('#' + id); DOM[id].id = id; } return DOM[id]; }
var fakeDoc = {
  createElement: function (t) { return new FakeEl(t); },
  createTextNode: function (t) { return { nodeType: 3, textContent: String(t) }; }
};

// ---------- the rest of the environment the extracted code runs in ----------
var window = {};
(0, eval)(readFile(ROOT + 'pp-usage.js'));
(0, eval)(readFile(ROOT + 'pp-answer.js'));
(0, eval)(readFile(ROOT + 'pp-distractor.js'));
var PP_ANSWER = window.PP_ANSWER;                 // the REAL comparator decides typed verdicts
var PP_DISTRACTOR = window.PP_DISTRACTOR;         // the REAL option builder, as index.html binds it
var ppMainAudioText = window.PP_USAGE.mainAudioText;
var ppHasMainAudio = window.PP_USAGE.hasMainAudio;

// Audio is a counter only. The lifecycle is owned by tests/test_mixed_audio.js; here it
// exists so that "the progress path started nothing" stays observable.
var AUDIO_MADE = [], UTTER_MADE = [], SPOKEN = [];
function Audio(src) { AUDIO_MADE.push(src); }
function SpeechSynthesisUtterance(t) { UTTER_MADE.push(t); }
function speakCardMain(card) { SPOKEN.push(card.pl); }
var audioManifestStatus = 'ready';
function syncRoundAudioReadiness() { return MIXED.syncReadiness(); }
function stopAllAudio() {}

var SCREENS = ['home', 'round', 'listen', 'study'];
function fakeShow(scr) {
  SCREENS.forEach(function (s) { el(s).classList.remove('active'); });
  el(scr).classList.add('active');
}
function identity(a) { return a.slice(); }
function fakeShuffle(a) { return identity(a); }   // deterministic: formats cycle listen/type/mc
function fakeEligible() { return true; }          // owned by tests/test_typeit_eligibility.js
function fakeAppendUsage() {}                     // owned by tests/test_activities.js
function ppVariantPartsStub() { return null; }    // owned by tests/test_typeit_feedback.js
var PROGRESS_WRITABLE = false, SAVED = [], STORE = { progress: {} };
function fakeProgressWritable() { return PROGRESS_WRITABLE; }
function fakeLoadV2() { return STORE; }
function fakeSaveV2(s) { SAVED.push(JSON.parse(JSON.stringify(s))); STORE = s; }

// ---------- fixtures ----------
// Fifteen distinct glosses, so a FULL round is available and every option-bearing
// question can be filled. With an identity shuffle the formats cycle listen / type / mc
// from question 0, which puts the typed questions at indices 1, 4, 7, 10 and 13.
var C15 = [
  { id: 'm1',  pl: 'kawa',    en: 'coffee' },
  { id: 'm2',  pl: 'mąka',    en: 'flour' },      // typed, and carries the "almost" diacritic
  { id: 'm3',  pl: 'woda',    en: 'water' },
  { id: 'm4',  pl: 'sok',     en: 'juice' },
  { id: 'm5',  pl: 'mleko',   en: 'milk' },       // typed
  { id: 'm6',  pl: 'chleb',   en: 'bread' },
  { id: 'm7',  pl: 'ser',     en: 'cheese' },
  { id: 'm8',  pl: 'masło',   en: 'butter' },     // typed
  { id: 'm9',  pl: 'jajko',   en: 'egg' },
  { id: 'm10', pl: 'ryba',    en: 'fish' },
  { id: 'm11', pl: 'mięso',   en: 'meat' },       // typed
  { id: 'm12', pl: 'zupa',    en: 'soup' },
  { id: 'm13', pl: 'owoc',    en: 'fruit' },
  { id: 'm14', pl: 'ciasto',  en: 'cake' },       // typed
  { id: 'm15', pl: 'herbata', en: 'tea' }
];
// A topic bigger than the cap, so "15" can be shown to be a CAP rather than the number
// the counter is built from - and two smaller topics, which is what most real topics are.
var C17 = C15.concat([{ id: 'm16', pl: 'piwo', en: 'beer' }, { id: 'm17', pl: 'wino', en: 'wine' }]);
var C6 = C15.slice(0, 6);
var C3 = C15.slice(0, 3);
// Two cards, so the round's FINAL original question is a typed one - the format cycle is
// listen / type / mc, so a topic whose size is 2 mod 3 ends on "type". Its final card is
// the diacritic one, which is what makes "almost" reachable on a final question.
var C2 = C15.slice(0, 2);
// Fourteen cards: also ends on "type", but with a full-length round and a plain answer.
var C14 = C15.slice(0, 14);

var CARDS = C15;
var LEVELS = [{ level: 'A1', topics: [{ id: 'topic-1', name: 'Jedzenie', src: ['A1'],
                                        kind: 'mixed', cards: CARDS }] }];
// The thin-pool fallback. Always the full fifteen, so even a three-card topic can build
// four options - WHICH options is owned by tests/test_mixed_distractors.js, not here.
function fakePoolFor() { return C15.map(function (c) { return { c: c, topic: 'Jedzenie' }; }); }

// ---------- reading the wiring out of index.html ----------
// Paren-matching, because a handler body contains calls of its own.
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

// `$` is already taken here - it is JXA's ObjC bridge - so the shipping code is compiled
// into a generated scope and handed its free identifiers as PARAMETERS.
var RNAMES = ['rBuildOptions', 'startRound', 'rSetBlocks',
              'rSetStatus', 'rAnnounceWrong', 'rAnnounceCorrect', 'rFocusNextOption',
              'rOriginalTotal', 'rPct', 'rReviewPos', 'rSyncNextLabel',
              'rRender', 'rPickOption', 'rRevealLetter', 'rCheckAnswer', 'rRecord', 'rShowDone',
              'syncRoundAudioReadiness', 'rPlayCurrent', 'rAdvance', 'rExit'];
var RSRC = {};
RNAMES.forEach(function (n) { RSRC[n] = extractFunction(INDEX, n); });
var R_CONTROLS = ['rNext', 'rCheck', 'rHint', 'rPlay', 'rAgain', 'rBack', 'rBackBtn'];
var rStateMatch = INDEX.match(/const\s+R\s*=\s*(\{[^}]*\})\s*;/);
if (!rStateMatch) throw new Error('extract: Mixed Quiz state object R not found in index.html');
var R = (0, eval)('(' + rStateMatch[1] + ')');
var R_LITERAL = rStateMatch[1];

var PP_TYPED_INDEX = PP_ANSWER.buildIndex(C17);

var MIXED = (new Function('$', 'document', 'show', 'R', 'LEVELS', 'poolFor', 'gShuffle',
  'ppEligibleFor', 'ppAppendUsageTo', 'ppVariantParts', 'ppProgressWritable', 'loadV2', 'saveV2',
  'PP_ANSWER', 'PP_TYPED_INDEX', 'ppHasMainAudio', 'ppMainAudioText', 'G_AUDIO', 'PP_DISTRACTOR',
  RNAMES.map(function (n) { return RSRC[n]; }).join('\n') + '\n' +
  'return {\n' +
  '  startRound: function(a,b){ return startRound(a,b); },\n' +
  '  rRender: function(){ return rRender(); },\n' +
  '  rShowDone: function(){ return rShowDone(); },\n' +
  '  rRevealLetter: function(){ return rRevealLetter(); },\n' +
  '  rCheckAnswer: function(){ return rCheckAnswer(); },\n' +
  '  rOriginalTotal: function(){ return rOriginalTotal(); },\n' +
  '  rPct: function(a,b){ return rPct(a,b); },\n' +
  '  rReviewPos: function(){ return rReviewPos(); },\n' +
  '  syncReadiness: function(){ return syncRoundAudioReadiness(); },\n' +
  '  handlers: {\n' +
  R_CONTROLS.map(function (id) { return '    ' + id + ': (' + handlerExpr(id) + ')'; }).join(',\n') + '\n' +
  '  }\n' +
  '};'
))(el, fakeDoc, fakeShow, R, LEVELS, fakePoolFor, fakeShuffle,
   fakeEligible, fakeAppendUsage, ppVariantPartsStub, fakeProgressWritable, fakeLoadV2, fakeSaveV2,
   PP_ANSWER, PP_TYPED_INDEX, ppHasMainAudio, ppMainAudioText, '<svg data-icon="audio"></svg>', PP_DISTRACTOR);
function activate(id) { return MIXED.handlers[id](); }

// ---------- driving a round ----------
function reset(o) {
  o = o || {};
  DOM = {}; HTML_WRITES = {};
  AUDIO_MADE = []; UTTER_MADE = []; SPOKEN = [];
  SAVED = []; STORE = { progress: {} };
  PROGRESS_WRITABLE = !!o.progress;
  CARDS = o.cards || C15;
  LEVELS[0].topics[0].cards = CARDS;
  audioManifestStatus = 'ready';
  BODY = new FakeEl('body'); BODY.id = 'BODY'; DOM.BODY = BODY;
  ACTIVE = BODY;
  MIXED.startRound(0, 0);
}
function q() { return R.qs[R.i]; }
function opts() { return el('rOpts').children; }
function correctBtn() {
  var cur = q(), list = opts();
  for (var i = 0; i < cur.options.length; i++) if (cur.options[i].correct === true) return list[i];
  throw new Error('fixture: no correct option in question ' + R.i);
}
function wrongBtn() {
  var cur = q(), list = opts();
  for (var i = 0; i < cur.options.length; i++) if (cur.options[i].correct !== true) return list[i];
  throw new Error('fixture: no wrong option in question ' + R.i);
}
function press(btn) { btn.focus(); btn.click(); }
function typeAndCheck(text) { el('rInput').value = text; activate('rCheck'); }
// Answer the current question. 'right' is exact; 'miss' is a wrong option pressed
// before the right one, or a typed answer that is no card's answer; 'almost' is only
// reachable on the diacritic card.
function answer(outcome) {
  var cur = q();
  if (cur.fmt === 'type') {
    typeAndCheck(outcome === 'right' ? cur.c.pl
               : outcome === 'almost' ? PP_ANSWER.accepted(cur.c)[0].replace(/[ąęółżźćńś]/g, function (ch) {
                   return { 'ą': 'a', 'ę': 'e', 'ó': 'o', 'ł': 'l', 'ż': 'z', 'ź': 'z', 'ć': 'c', 'ń': 'n', 'ś': 's' }[ch];
                 })
               : 'qqqqzzzz');
  } else {
    if (outcome !== 'right') press(wrongBtn());
    press(correctBtn());
  }
}
function advance() { activate('rNext'); }
function counter() { return el('rCountLbl').textContent; }
function prompt_() { return el('rType').textContent; }
function nextLabel() { return el('rNextLabel').textContent; }
function barPct() { return parseFloat(el('rFill').style.width); }
// Walk a whole round. `plan` maps an ORIGINAL question index to its outcome; anything
// not named is answered right, and every review is answered right.
function runRound(plan, cards) {
  reset({ cards: cards });
  var total = R.originalTotal, seen = [];
  for (var i = 0; i < total; i++) {
    seen.push({ i: R.i, counter: counter(), bar: barPct(), prompt: prompt_(),
                next: nextLabel(), requeued: q().requeued, fmt: q().fmt });
    answer((plan && plan[i]) || 'right');
    advance();
  }
  var reviews = [];
  while (R.i < R.qs.length) {
    reviews.push({ i: R.i, counter: counter(), bar: barPct(), prompt: prompt_(),
                   next: nextLabel(), requeued: q().requeued, fmt: q().fmt });
    answer('right');
    advance();
  }
  return { originals: seen, reviews: reviews, total: total };
}

// The fixture must really produce what it claims, or every assertion below is about
// the wrong round.
reset();
eq('A0 the fifteen-card topic builds a fifteen-question round', R.qs.length, 15);
eq('A0 question 0 is the listen format', R.qs[0].fmt, 'listen');
eq('A0 question 1 is the typed format', R.qs[1].fmt, 'type');
eq('A0 question 2 is the multiple-choice format', R.qs[2].fmt, 'mc');
eq('A0 the typed questions sit where the fixture says they do',
   R.qs.map(function (x, i) { return x.fmt === 'type' ? i : -1; }).filter(function (i) { return i >= 0; }),
   [1, 4, 7, 10, 13]);

// =========================================================================
// A. BASELINE COUNTER - the round is measured against the round
// =========================================================================
reset({ cards: C15 });
eq('A1 a fifteen-question round opens at 1 / 15', counter(), '1 / 15');
eq('A1 originalTotal is the initial question count', R.originalTotal, 15);
eq('A1 originalTotal matches the list it was taken from', R.originalTotal, R.qs.length);

// A smaller topic uses its REAL size - the counter is not a constant with a 15 in it.
reset({ cards: C6 });
eq('A2 a six-question round opens at 1 / 6', counter(), '1 / 6');
eq('A2 ... and banks six as its original total', R.originalTotal, 6);
reset({ cards: C3 });
eq('A2 a three-question round opens at 1 / 3', counter(), '1 / 3');
eq('A2 ... and banks three as its original total', R.originalTotal, 3);

// And a topic BIGGER than the cap proves 15 is a cap on the sample, not a literal in
// the counter: the denominator is whatever the sample turned out to be.
reset({ cards: C17 });
eq('A3 a seventeen-card topic is still capped at fifteen questions', R.qs.length, 15);
eq('A3 ... and the counter reads the capped size', counter(), '1 / 15');
eq('A3 ... which is the list length, not a constant', R.originalTotal, R.qs.length);
// three different topics, three different denominators, one code path
var DENOMS = [C3, C6, C15].map(function (c) { reset({ cards: c }); return counter(); });
eq('A3 three topic sizes produce three different denominators', DENOMS, ['1 / 3', '1 / 6', '1 / 15']);
ok('A3 the denominator is not hard-coded anywhere in rRender',
   codeOnly(RSRC.rRender).indexOf('15') === -1);
ok('A3 startRound takes the total off the built list, not off a literal',
   hasCode(codeOnly(RSRC.startRound), 'R.originalTotal = R.qs.length'));

// =========================================================================
// B. A MISS DOES NOT ENLARGE THE DENOMINATOR
// =========================================================================
reset({ cards: C15 });
eq('B1 question 1 reads 1 / 15', counter(), '1 / 15');
answer('miss');
eq('B1 the miss appended a retry', R.qs.length, 16);
eq('B1 ... which is flagged as a second pass', R.qs[R.qs.length - 1].requeued, true);
advance();
eq('B1 question 2 still reads 2 / 15, not 2 / 16', counter(), '2 / 15');
eq('B1 the original total did not move', R.originalTotal, 15);
ok('B1 the counter never says 16', counter().indexOf('16') === -1);

// several misses, and every original question keeps the same denominator
var MANY = runRound({ 0: 'miss', 1: 'miss', 3: 'miss', 6: 'miss' }, C15);
eq('B2 four misses appended four retries', MANY.reviews.length, 4);
ok('B2 every original question was measured against 15',
   MANY.originals.every(function (s) { return / \/ 15$/.test(s.counter); }));
eq('B2 the original counters run 1..15 over a fixed total',
   MANY.originals.map(function (s) { return s.counter; }),
   ['1 / 15','2 / 15','3 / 15','4 / 15','5 / 15','6 / 15','7 / 15','8 / 15',
    '9 / 15','10 / 15','11 / 15','12 / 15','13 / 15','14 / 15','15 / 15']);
ok('B2 no original counter mentions the grown array',
   MANY.originals.every(function (s) { return s.counter.indexOf('19') === -1 && s.counter.indexOf('16') === -1; }));
// the same on a small topic, where a miss is a bigger fraction of the round
var SMALL = runRound({ 0: 'miss', 1: 'miss' }, C3);
eq('B3 a three-question round with two misses keeps its denominator',
   SMALL.originals.map(function (s) { return s.counter; }), ['1 / 3', '2 / 3', '3 / 3']);
eq('B3 ... and queued two reviews', SMALL.reviews.length, 2);

// =========================================================================
// C. PROGRESS BAR - drawn against the original round, and never retreating
// =========================================================================
var BAR = runRound({ 0: 'miss', 4: 'miss', 9: 'miss' }, C15);
// the existing convention is preserved: a question counts once it has been answered,
// so question one opens the bar at 0% and question N opens it at (N-1)/total.
eq('C1 the bar opens at zero', BAR.originals[0].bar, 0);
ok('C1 every original question is drawn against the original total',
   BAR.originals.every(function (s, i) { return Math.abs(s.bar - (i / 15 * 100)) < 1e-9; }));
eq('C1 the last original question shows fourteen fifteenths', BAR.originals[14].bar, 14 / 15 * 100);
ok('C1 the bar is NOT drawn against the grown array',
   Math.abs(BAR.originals[14].bar - (14 / 18 * 100)) > 1e-9);

// monotonic across the whole round, reviews included
var WIDTHS = BAR.originals.concat(BAR.reviews).map(function (s) { return s.bar; });
ok('C2 the bar never decreases anywhere in the round',
   WIDTHS.every(function (w, i) { return i === 0 || w >= WIDTHS[i - 1]; }));
ok('C2 R.qs grew during that round', R.qs.length > BAR.total);
eq('C2 ... by exactly the number of misses', R.qs.length - BAR.total, 3);

// reviews sit past a finished round, so the bar stays full
eq('C3 the first review is drawn full', BAR.reviews[0].bar, 100);
ok('C3 every review is drawn full', BAR.reviews.every(function (s) { return s.bar === 100; }));
ok('C3 no review shrinks the bar to fit the grown array',
   BAR.reviews.every(function (s) { return s.bar !== (BAR.total / R.qs.length * 100); }));

// the clamp: a width is a style string, so a bad input must produce a number, not "NaN%"
var PCT = MIXED.rPct;
eq('C4 zero of zero is zero, not NaN', PCT(0, 0), 0);
eq('C4 something of zero is zero, not Infinity', PCT(5, 0), 0);
eq('C4 a negative total is zero', PCT(5, -3), 0);
eq('C4 a missing total is zero', PCT(5, undefined), 0);
eq('C4 a non-numeric total is zero', PCT(5, 'x'), 0);
eq('C4 a negative position clamps to zero', PCT(-4, 10), 0);
eq('C4 overrun clamps to a hundred', PCT(40, 10), 100);
eq('C4 an exact finish is a hundred', PCT(10, 10), 100);
eq('C4 an ordinary position is an ordinary percentage', PCT(3, 12), 25);
[[0,0],[5,0],[-1,4],[9,3],[1,3],[0,15]].forEach(function (pair) {
  var v = PCT(pair[0], pair[1]);
  ok('C4 rPct(' + pair.join(',') + ') is a finite number', typeof v === 'number' && isFinite(v));
  ok('C4 rPct(' + pair.join(',') + ') is inside the track', v >= 0 && v <= 100);
});
// and the total helper refuses to hand a broken number to it
var savedTotal = R.originalTotal;
R.originalTotal = 0;        eq('C5 a zero original total reads as zero', MIXED.rOriginalTotal(), 0);
R.originalTotal = undefined; eq('C5 a missing original total reads as zero', MIXED.rOriginalTotal(), 0);
R.originalTotal = -2;       eq('C5 a negative original total reads as zero', MIXED.rOriginalTotal(), 0);
R.originalTotal = '7';      eq('C5 a numeric string is coerced', MIXED.rOriginalTotal(), 7);
R.originalTotal = savedTotal;
ok('C5 a broken total still paints a finite width', isFinite(PCT(3, MIXED.rOriginalTotal())));

// =========================================================================
// D. REVIEW COUNTER - reviews have their own ordinal and their own total
// =========================================================================
var ONE = runRound({ 2: 'miss' }, C15);
eq('D1 one miss produces one review', ONE.reviews.length, 1);
eq('D1 the single review reads Review 1 / 1', ONE.reviews[0].counter, 'Review 1 / 1');

var FOUR = runRound({ 0: 'miss', 3: 'miss', 8: 'miss', 12: 'miss' }, C15);
eq('D2 four misses produce four reviews', FOUR.reviews.length, 4);
eq('D2 the reviews are numbered 1..4 of 4',
   FOUR.reviews.map(function (s) { return s.counter; }),
   ['Review 1 / 4', 'Review 2 / 4', 'Review 3 / 4', 'Review 4 / 4']);
ok('D2 the very first review already knows the complete total',
   FOUR.reviews[0].counter.indexOf('/ 4') !== -1);
// the ordinal and total are DERIVED, so they survive being read out of order
reset({ cards: C15 });
answer('miss'); advance();
answer('miss'); advance();
while (!q().requeued) { answer('right'); advance(); }
eq('D3 the derived position of the first review', MIXED.rReviewPos(), { at: 1, total: 2 });
R.i = R.qs.length - 1; MIXED.rRender();
eq('D3 the derived position of the last review', MIXED.rReviewPos(), { at: 2, total: 2 });
eq('D3 ... and it renders as Review 2 / 2', counter(), 'Review 2 / 2');
R.i = 0; MIXED.rRender();
eq('D3 an original question re-rendered later still reads its own progress', counter(), '1 / 15');

// an original question never says "Review"
[ONE, FOUR, MANY, SMALL, BAR].forEach(function (run, n) {
  ok('D4 run ' + n + ': no original counter contains "Review"',
     run.originals.every(function (s) { return s.counter.indexOf('Review') === -1; }));
  ok('D4 run ' + n + ': every review counter does',
     run.reviews.every(function (s) { return s.counter.indexOf('Review') === 0; }));
  ok('D4 run ' + n + ': the review total equals the number of reviews',
     run.reviews.every(function (s) { return s.counter.indexOf('/ ' + run.reviews.length) !== -1; }));
  ok('D4 run ' + n + ': the review ordinals are 1..N in order',
     run.reviews.every(function (s, i) { return s.counter.indexOf('Review ' + (i + 1) + ' ') === 0; }));
});
// a round with no misses has no review counter at all
var CLEAN = runRound({}, C15);
eq('D5 a clean round queues no reviews', CLEAN.reviews.length, 0);
ok('D5 ... and never renders the word Review',
   CLEAN.originals.every(function (s) { return s.counter.indexOf('Review') === -1 && s.prompt.indexOf('Review') === -1; }));

// =========================================================================
// E. REVIEW PROMPT - the retry says so, in the question itself
// =========================================================================
// One miss per format, so all three prompts are reached as retries.
var BYFMT = runRound({ 0: 'miss', 1: 'miss', 2: 'miss' }, C15);
eq('E1 the three misses were listen / type / mc',
   BYFMT.originals.slice(0, 3).map(function (s) { return s.fmt; }), ['listen', 'type', 'mc']);
eq('E1 their retries carry the marked prompts',
   BYFMT.reviews.map(function (s) { return s.prompt; }),
   ['Review · What did you hear?', 'Review · Type the Polish', 'Review · What does it mean?']);
eq('E2 an original listen question keeps its wording', BYFMT.originals[0].prompt, 'What did you hear?');
eq('E2 an original typed question keeps its wording', BYFMT.originals[1].prompt, 'Type the Polish');
eq('E2 an original mc question keeps its wording', BYFMT.originals[2].prompt, 'What does it mean?');
ok('E2 no original prompt is prefixed',
   BYFMT.originals.every(function (s) { return s.prompt.indexOf('Review') === -1; }));
ok('E2 every review prompt is prefixed exactly once',
   BYFMT.reviews.every(function (s) { return countOf(s.prompt, 'Review · ') === 1; }));
ok('E2 the marked prompt still ends in the ordinary question',
   BYFMT.reviews.every(function (s) {
     return ['What did you hear?', 'Type the Polish', 'What does it mean?']
       .indexOf(s.prompt.replace('Review · ', '')) !== -1;
   }));
// the marker is TEXT, and #rType is never written through innerHTML
reset({ cards: C15 });
answer('miss'); advance();
while (!q().requeued) { answer('right'); advance(); }
eq('E3 the review prompt is the marked text', prompt_(), 'Review · What did you hear?');
eq('E3 #rType was never written through innerHTML', HTML_WRITES.rType || 0, 0);
ok('E3 rRender assigns the prompt through textContent', hasCode(codeOnly(RSRC.rRender), '$("rType").textContent ='));
ok('E3 rRender never assigns #rType through innerHTML',
   codeOnly(RSRC.rRender).indexOf('$("rType").innerHTML') === -1);
ok('E3 no new innerHTML path was introduced into rRender', (function () {
  // the option loop and the two feedback panels are the pre-existing ones; the count
  // must not have grown, and none of them is the prompt or the counter.
  var code = codeOnly(RSRC.rRender);
  return code.indexOf('rCountLbl").innerHTML') === -1 &&
         code.indexOf('rFill").innerHTML') === -1 &&
         code.indexOf('rType").innerHTML') === -1;
})());
// the separator is the one already used elsewhere in the file, not a new glyph
ok('E4 the marker uses the middle dot the app already uses',
   RSRC.rRender.indexOf('Review · ') !== -1);
ok('E4 the marker is conditional on the retry flag',
   hasCode(codeOnly(RSRC.rRender), 'q.requeued ? "Review · " : ""'));

// =========================================================================
// F. LIVE REGION - the counter still announces, and it is still the only one
// =========================================================================
var ROUND_SCREEN = (function () {
  var s = INDEX.indexOf('<section class="screen" id="round"');
  if (s === -1) throw new Error('markup: the Mixed Quiz screen was not found');
  var e = INDEX.indexOf('<section', s + 10);
  return INDEX.slice(s, e === -1 ? INDEX.length : e);
})();
function tagFor(id) {
  var at = INDEX.indexOf('id="' + id + '"');
  if (at === -1) throw new Error('markup: no element with id ' + id);
  var open = INDEX.lastIndexOf('<', at), close = INDEX.indexOf('>', at);
  return INDEX.slice(open, close + 1);
}
function attr(tag, name) {
  var m = tag.match(new RegExp('\\s' + name + '\\s*=\\s*"([^"]*)"'));
  return m ? m[1] : null;
}
eq('F1 exactly one progress counter exists', countOf(INDEX, 'id="rCountLbl"'), 1);
eq('F1 it lives on the Mixed Quiz screen', countOf(ROUND_SCREEN, 'id="rCountLbl"'), 1);
eq('F1 it is still a polite live region', attr(tagFor('rCountLbl'), 'aria-live'), 'polite');
ok('F1 it was not promoted to an alert or a status region',
   attr(tagFor('rCountLbl'), 'role') === null);
ok('F1 it was not made atomic-only or assertive',
   attr(tagFor('rCountLbl'), 'aria-live') !== 'assertive');
// the phase added NO second progress region to compete with it
eq('F2 the screen still has exactly three polite regions',
   countOf(ROUND_SCREEN, 'aria-live="polite"'), 3);
eq('F2 the screen still has exactly one status region', countOf(ROUND_SCREEN, 'role="status"'), 1);
ok('F2 the three polite regions are still the counter, the typed verdict and the status',
   ROUND_SCREEN.indexOf('id="rCountLbl" aria-live="polite"') !== -1 &&
   attr(tagFor('rVerdict'), 'aria-live') === 'polite' &&
   attr(tagFor('rStatus'), 'aria-live') === 'polite');
ok('F2 no new progress node was added to the screen',
   ROUND_SCREEN.indexOf('rReviewLbl') === -1 && ROUND_SCREEN.indexOf('rPhase') === -1 &&
   ROUND_SCREEN.indexOf('rRetryBadge') === -1);
// what it announces is the WHOLE progress sentence, on both kinds of question
var ANN = runRound({ 5: 'miss' }, C15);
ok('F3 an original announcement carries the ordinal and the total',
   /^\d+ \/ 15$/.test(ANN.originals[0].counter) && /^\d+ \/ 15$/.test(ANN.originals[9].counter));
eq('F3 a review announcement names the phase, the ordinal and the total',
   ANN.reviews[0].counter, 'Review 1 / 1');
ok('F3 the announcement is written through textContent',
   hasCode(codeOnly(RSRC.rRender), '$("rCountLbl").textContent'));
eq('F3 the counter was never written through innerHTML', HTML_WRITES.rCountLbl || 0, 0);

// =========================================================================
// G. NEXT / SEE RESULTS - the last RENDERED question, not the last original
// =========================================================================
var G1 = runRound({ 2: 'miss' }, C15);
eq('G1 the last original question still offers Next while a review is waiting',
   G1.originals[14].next, 'Next');
eq('G1 the final review offers See results', G1.reviews[0].next, 'See results');
ok('G1 no earlier question offers See results',
   G1.originals.slice(0, 14).every(function (s) { return s.next === 'Next'; }));
var G2 = runRound({ 0: 'miss', 5: 'miss', 11: 'miss' }, C15);
ok('G2 with three reviews waiting, no original question offers See results',
   G2.originals.every(function (s) { return s.next === 'Next'; }));
eq('G2 only the last review offers See results',
   G2.reviews.map(function (s) { return s.next; }), ['Next', 'Next', 'See results']);
var G3 = runRound({}, C15);
eq('G3 a clean round ends on See results at the last original question',
   G3.originals[14].next, 'See results');
ok('G3 ... and offers Next everywhere before it',
   G3.originals.slice(0, 14).every(function (s) { return s.next === 'Next'; }));
var G4 = runRound({}, C3);
eq('G4 a three-question clean round ends on See results',
   G4.originals.map(function (s) { return s.next; }), ['Next', 'Next', 'See results']);

// -------------------------------------------------------------------------
// G5-G9. THE FINAL ORIGINAL QUESTION THAT CREATES THE FIRST REVIEW
// The one case the label cannot be decided at render time. Every case above reaches
// the last original question with R.qs ALREADY grown, because something earlier was
// missed - so "Next" was correct when it was rendered. Here nothing earlier was
// missed: the last original question renders while R.qs holds originals only, so it
// is rendered as the end of the round, and then the learner misses it and rRecord
// appends the very first retry UNDER the label already on screen. Before the fix the
// enabled, focused button still promised "See results" and the click opened
// "Review 1 / 1" - it named a screen it was no longer going to reach.
// -------------------------------------------------------------------------
// G5. the final original is a multiple-choice question (15 cards ends on "mc")
reset({ cards: C15 });
for (var g5 = 0; g5 < R.originalTotal - 1; g5++) { answer('right'); advance(); }
eq('G5 the walk stopped on the final original question', R.i, R.originalTotal - 1);
eq('G5 ... which is a multiple-choice question', q().fmt, 'mc');
eq('G5 ... with no earlier miss, so R.qs is still just the originals', R.qs.length, R.originalTotal);
eq('G5 the label before answering is See results', nextLabel(), 'See results');
answer('miss');
eq('G5 the miss appended the first retry', R.qs.length, R.originalTotal + 1);
eq('G5 ... flagged as a second pass', R.qs[R.qs.length - 1].requeued, true);
eq('G5 the label was corrected to Next', nextLabel(), 'Next');
eq('G5 ... on a button that is now enabled', el('rNext').disabled, false);
ok('G5 ... and holding focus', ACTIVE === el('rNext'));
advance();
eq('G5 clicking it opened the review, not the results', counter(), 'Review 1 / 1');
eq('G5 ... with the marked prompt', prompt_(), 'Review · What does it mean?');
eq('G5 ... and the results screen is not up', el('rDone').style.display, 'none');
eq('G5 the review itself offers See results', nextLabel(), 'See results');
answer('right'); advance();
eq('G5 and that click really did reach the results', el('rDone').style.display, 'flex');

// G6. the final original is a typed question (2 cards ends on "type")
reset({ cards: C2 });
eq('G6 the two-card topic built a two-question round', R.originalTotal, 2);
answer('right'); advance();
eq('G6 the walk stopped on the final original question', R.i, 1);
eq('G6 ... which is a typed question', q().fmt, 'type');
eq('G6 ... with R.qs still just the originals', R.qs.length, 2);
eq('G6 the label before submitting is See results', nextLabel(), 'See results');
typeAndCheck('qqqqzzzz');                      // a nonblank answer that is no card's answer
eq('G6 the wrong submission was recorded as a miss', R.qs[1].result, 'miss');
eq('G6 ... and appended the first retry', R.qs.length, 3);
eq('G6 the label was corrected to Next', nextLabel(), 'Next');
eq('G6 ... before focus landed on the button', ACTIVE, el('rNext'));
eq('G6 ... which is enabled', el('rNext').disabled, false);
advance();
eq('G6 clicking it opened the typed review', counter(), 'Review 1 / 1');
eq('G6 ... with the marked typed prompt', prompt_(), 'Review · Type the Polish');
eq('G6 ... and it really is the typed format', q().fmt, 'type');
eq('G6 the review offers See results', nextLabel(), 'See results');
// the same on a full-length round whose last question is typed
reset({ cards: C14 });
for (var g6 = 0; g6 < 13; g6++) { answer('right'); advance(); }
eq('G6 the fourteen-card round ends on a typed question', q().fmt, 'type');
eq('G6 ... labelled See results before the answer', nextLabel(), 'See results');
answer('miss');
eq('G6 ... corrected to Next once the retry exists', nextLabel(), 'Next');
advance();
eq('G6 ... and the click opened Review 1 / 1', counter(), 'Review 1 / 1');

// G7. outcomes that append NOTHING must keep "See results"
reset({ cards: C15 });
for (var g7 = 0; g7 < R.originalTotal - 1; g7++) { answer('right'); advance(); }
answer('right');
eq('G7 a right answer on the final original appended nothing', R.qs.length, R.originalTotal);
eq('G7 ... so the label stays See results', nextLabel(), 'See results');
advance();
eq('G7 ... and the click really reaches the results', el('rDone').style.display, 'flex');
// an "almost" on a final typed original: no requeue, so no relabel either
reset({ cards: C2 });
answer('right'); advance();
eq('G7 the final original is the diacritic typed card', q().c.pl, 'mąka');
answer('almost');
eq('G7 an almost was recorded as almost', R.qs[1].result, 'almost');
eq('G7 ... and appended nothing', R.qs.length, 2);
eq('G7 ... so the label stays See results', nextLabel(), 'See results');
advance();
eq('G7 ... and the click reaches the results', el('rDone').style.display, 'flex');

// G8. a review never requeues, so the final review's label never moves
reset({ cards: C15 });
for (var g8 = 0; g8 < R.originalTotal; g8++) { answer(g8 === 0 ? 'miss' : 'right'); advance(); }
eq('G8 one review is waiting', R.qs.length, R.originalTotal + 1);
eq('G8 the review is the final rendered question, labelled See results', nextLabel(), 'See results');
var g8len = R.qs.length;
answer('miss');                                 // missing a REVIEW must not queue another
eq('G8 missing a review appended nothing', R.qs.length, g8len);
eq('G8 ... it banked no result either', q().result, null);
eq('G8 ... and the label is still See results', nextLabel(), 'See results');
advance();
eq('G8 ... and the click reached the results', el('rDone').style.display, 'flex');
// the same for a typed review answered wrongly
reset({ cards: C2 });
answer('right'); advance();
answer('miss'); advance();                      // the final typed original queues one review
eq('G8 the typed review is up', q().requeued, true);
eq('G8 ... labelled See results', nextLabel(), 'See results');
typeAndCheck('qqqqzzzz');
eq('G8 a wrong typed review appended nothing', R.qs.length, 3);
eq('G8 ... and kept See results', nextLabel(), 'See results');

// G9. the label is never stale in the middle of a round either
// A miss on a NON-final original leaves "Next" as "Next" - the helper is idempotent,
// so calling it unconditionally after every answer cannot corrupt an ordinary question.
reset({ cards: C15 });
eq('G9 question one is labelled Next', nextLabel(), 'Next');
answer('miss');
eq('G9 ... and is still Next after a mid-round miss', nextLabel(), 'Next');
advance();
answer('right');
eq('G9 ... and still Next after a mid-round right answer', nextLabel(), 'Next');

// =========================================================================
// H. HINT COUNTING - questions, first attempts, typed only
// =========================================================================
// Walk to a typed question without answering anything before it is needed.
function atTyped(nth) {
  reset({ cards: C15 });
  var seen = 0;
  while (true) {
    if (q().fmt === 'type') { if (seen === nth) return; seen++; }
    answer('right'); advance();
  }
}
reset({ cards: C15 });
eq('H1 a fresh round starts with no hinted questions', R.hinted, 0);
runRound({}, C15);
eq('H1 a round answered without hints counts none', R.hinted, 0);

atTyped(0);
MIXED.rRevealLetter();
eq('H2 revealing alone banks nothing yet', R.hinted, 0);
answer('right');
eq('H2 one reveal, then a submission, counts one question', R.hinted, 1);

atTyped(0);
var H3_CANON = PP_ANSWER.accepted(q().c)[0];
MIXED.rRevealLetter(); MIXED.rRevealLetter(); MIXED.rRevealLetter(); MIXED.rRevealLetter();
// The reveal depth is capped at one letter short of the whole answer - a pre-existing
// rule, unchanged by this phase. What matters here is that the DEPTH, whatever it
// reached, is still one hinted QUESTION.
eq('H3 four presses reveal as far as the existing cap allows',
   R.revealed, Math.min(4, H3_CANON.length - 1));
ok('H3 ... which is more than none', R.revealed > 1);
answer('right');
eq('H3 ... and the whole question counts once', R.hinted, 1);
// a longer answer takes all four reveals and is still one question
reset({ cards: C15 });
while (!(q().fmt === 'type' && PP_ANSWER.accepted(q().c)[0].length > 5)) { answer('right'); advance(); }
MIXED.rRevealLetter(); MIXED.rRevealLetter(); MIXED.rRevealLetter(); MIXED.rRevealLetter();
eq('H3 four reveals on a longer answer really are four letters', R.revealed, 4);
answer('right');
eq('H3 ... and still count as exactly one hinted question', R.hinted, 1);

// two separate typed questions
atTyped(0);
MIXED.rRevealLetter(); answer('right'); advance();
while (q().fmt !== 'type') { answer('right'); advance(); }
MIXED.rRevealLetter(); MIXED.rRevealLetter(); answer('right');
eq('H4 hints on two typed questions count two', R.hinted, 2);
// and an un-hinted typed question in between is not counted
advance();
while (q().fmt !== 'type') { answer('right'); advance(); }
answer('right');
eq('H4 an un-hinted typed question adds nothing', R.hinted, 2);

// a blank submission is not a submission
atTyped(0);
MIXED.rRevealLetter();
typeAndCheck('');
eq('H5 a blank submission after revealing counts nothing', R.hinted, 0);
typeAndCheck('   ');
eq('H5 a whitespace-only submission counts nothing either', R.hinted, 0);
eq('H5 ... and the question is still open', R.state, 'ask');
answer('right');
eq('H5 the later real submission counts the question exactly once', R.hinted, 1);

// the state guard is authoritative: a settled question cannot be counted twice
atTyped(0);
MIXED.rRevealLetter();
answer('right');
eq('H6 the first submission counts once', R.hinted, 1);
activate('rCheck');
eq('H6 a second Check on a settled question counts nothing more', R.hinted, 1);
MIXED.rCheckAnswer();
eq('H6 a direct re-entry counts nothing more either', R.hinted, 1);
eq('H6 the question is still settled', R.state, 'done');

// listen and mc questions have no hint path at all
var HFMT = runRound({}, C15);
eq('H7 a fully answered round with no typed reveals counts nothing', R.hinted, 0);
reset({ cards: C15 });
answer('right'); advance();                       // q0 listen, answered
eq('H7 answering a listen question banks no hint', R.hinted, 0);
while (q().fmt !== 'mc') { answer('right'); advance(); }
answer('right');
eq('H7 answering an mc question banks no hint', R.hinted, 0);
eq('H7 no reveal was recorded on either', R.revealed, 0);

// a review is excluded - the report is first-try scoring, like the tiles
reset({ cards: C15 });
while (q().fmt !== 'type') { answer('right'); advance(); }
answer('miss'); advance();                        // requeue this typed question
eq('H8 the typed miss banked no hint', R.hinted, 0);
while (!q().requeued) { answer('right'); advance(); }
eq('H8 the review is the typed question again', q().fmt, 'type');
eq('H8 ... and it is flagged as a retry', q().requeued, true);
MIXED.rRevealLetter(); MIXED.rRevealLetter();
answer('right');
eq('H8 a hint used on a review is NOT counted', R.hinted, 0);
// ... while a hint on the ORIGINAL of the same card still is
reset({ cards: C15 });
while (q().fmt !== 'type') { answer('right'); advance(); }
MIXED.rRevealLetter();
answer('miss'); advance();                        // hinted AND missed on the first try
eq('H9 a hinted first attempt counts even when it is missed', R.hinted, 1);
while (!q().requeued) { answer('right'); advance(); }
MIXED.rRevealLetter();
answer('right');
eq('H9 the retry of that same card adds nothing', R.hinted, 1);
// the hint never moves the verdict
reset({ cards: C15 });
while (q().fmt !== 'type') { answer('right'); advance(); }
var hintedCard = q().c;
MIXED.rRevealLetter(); MIXED.rRevealLetter();
answer('right');
eq('H10 a hinted answer is still recorded right', q().result, 'right');
eq('H10 ... and requeued nothing', R.qs.length, R.originalTotal);
eq('H10 ... and counted as a hint', R.hinted, 1);
reset({ cards: C15 });
while (q().fmt !== 'type') { answer('right'); advance(); }
MIXED.rRevealLetter();
answer('almost');
eq('H11 a hinted almost is still an almost', q().result, 'almost');
eq('H11 ... and still requeues nothing', R.qs.length, R.originalTotal);
eq('H11 ... and is still counted as a hint', R.hinted, 1);
info('the hinted card used for the verdict checks was "' + hintedCard.pl + '"');

// =========================================================================
// I. COMPLETION - the sentence sits beside the tiles, never inside them
// =========================================================================
// Finish a round and read the done screen. `plan` and `hints` are keyed by ORIGINAL
// question index; hints only apply to typed questions.
function finish(plan, hints, cards) {
  reset({ cards: cards });
  var total = R.originalTotal;
  for (var i = 0; i < total; i++) {
    if (hints && hints[i]) for (var h = 0; h < hints[i]; h++) MIXED.rRevealLetter();
    answer((plan && plan[i]) || 'right');
    advance();
  }
  while (R.i < R.qs.length) { answer('right'); advance(); }
  return {
    correct: el('rScoreN').textContent,
    almost: el('rAlmostN').textContent,
    missed: el('rMissN').textContent,
    msg: el('rDoneMsg').textContent,
    counter: counter(),
    bar: barPct(),
    total: total,
    hinted: R.hinted
  };
}
// zero hints: the Phase 4E message, unchanged, to the character
var I0 = finish({ 0: 'miss', 1: 'almost' }, null, C15);
eq('I1 an un-hinted round reports the old message exactly',
   I0.msg, 'You got 13 of 15 right on the first try. 1 almost - the ą and ę will come. 1 to review.');
ok('I1 ... with no hint clause appended', I0.msg.indexOf('hint') === -1);
var I0p = finish({}, null, C15);
eq('I1 an un-hinted perfect round keeps the perfect wording',
   I0p.msg, 'Every question right on the first try. Świetnie!');
ok('I1 ... and says nothing about hints', I0p.msg.indexOf('hint') === -1);

// one hint: singular
var I1 = finish({}, { 1: 1 }, C15);
eq('I2 one hinted question is counted', I1.hinted, 1);
ok('I2 ... and reported in the singular', I1.msg.indexOf(' You used a hint on 1 question.') !== -1);
ok('I2 ... not in the plural', I1.msg.indexOf('hints on') === -1);
// several hints: plural
var I3 = finish({}, { 1: 1, 4: 3, 7: 1 }, C15);
eq('I3 three hinted questions are counted', I3.hinted, 3);
ok('I3 ... and reported in the plural', I3.msg.indexOf(' You used hints on 3 questions.') !== -1);
ok('I3 ... not in the singular', I3.msg.indexOf('a hint on') === -1);
var I2q = finish({}, { 1: 2, 10: 5 }, C15);
ok('I3 two hinted questions read "hints on 2 questions"',
   I2q.msg.indexOf(' You used hints on 2 questions.') !== -1);
ok('I3 the wording matches Type It\'s', (function () {
  var t = extractFunction(INDEX, 'tShowDone');
  return t.indexOf('You used a hint on 1 question.') !== -1 &&
         t.indexOf('You used hints on ') !== -1;
})());

// the sentence lives in the existing paragraph, and no fourth tile was added
ok('I4 the hint sentence is in #rDoneMsg', I1.msg.indexOf('You used a hint') !== -1);
var DONE_MARKUP = ROUND_SCREEN.slice(ROUND_SCREEN.indexOf('<div class="done" id="rDone"'));
eq('I4 the done screen still has exactly three stat tiles',
   countOf(DONE_MARKUP, '<div class="stat">'), 3);
ok('I4 the three tiles are still CORRECT / ALMOST / TO REVIEW',
   DONE_MARKUP.indexOf('id="rScoreN">0</b><span>CORRECT<') !== -1 &&
   DONE_MARKUP.indexOf('id="rAlmostN">0</b><span>ALMOST<') !== -1 &&
   DONE_MARKUP.indexOf('id="rMissN">0</b><span>TO REVIEW<') !== -1);
ok('I4 the hint sentence reuses the existing summary paragraph',
   DONE_MARKUP.indexOf('<p id="rDoneMsg"></p>') !== -1);
ok('I4 no hint tile or hint node was added',
   DONE_MARKUP.indexOf('rHintN') === -1 && DONE_MARKUP.indexOf('rHinted') === -1 &&
   DONE_MARKUP.indexOf('HINTS') === -1);

// the tiles still sum to the ORIGINAL total, hinted or not
[I0, I0p, I1, I3, I2q].forEach(function (r, n) {
  eq('I5 result ' + n + ': the three tiles sum to the original total',
     Number(r.correct) + Number(r.almost) + Number(r.missed), r.total);
  eq('I5 result ' + n + ': the results counter uses the original total',
     r.counter, r.total + ' / ' + r.total);
  eq('I5 result ' + n + ': the bar is full', r.bar, 100);
});
// scoring is IDENTICAL with and without hints - same plan, hints only added
var PLAN = { 0: 'miss', 1: 'almost', 4: 'miss', 6: 'miss' };
var NOHINT = finish(PLAN, null, C15);
var WITHHINT = finish(PLAN, { 1: 2, 7: 1, 13: 4 }, C15);
eq('I6 hints do not change the correct tile', WITHHINT.correct, NOHINT.correct);
eq('I6 hints do not change the almost tile', WITHHINT.almost, NOHINT.almost);
eq('I6 hints do not change the review tile', WITHHINT.missed, NOHINT.missed);
eq('I6 the un-hinted run counted no hints', NOHINT.hinted, 0);
eq('I6 the hinted run counted three', WITHHINT.hinted, 3);
eq('I6 the hinted message is the un-hinted message plus the sentence',
   WITHHINT.msg, NOHINT.msg + ' You used hints on 3 questions.');
ok('I6 the hint sentence is appended after the tier clauses',
   WITHHINT.msg.indexOf('to review.') < WITHHINT.msg.indexOf('You used hints'));

// a perfect round that used hints is still a perfect round, and still says so
var PERF = finish({}, { 1: 1, 4: 2 }, C15);
eq('I7 a hinted clean sweep still scores every question correct', PERF.correct, '15');
eq('I7 ... with nothing almost', PERF.almost, '0');
eq('I7 ... and nothing to review', PERF.missed, '0');
ok('I7 ... and keeps the perfect-round wording',
   PERF.msg.indexOf('Every question right on the first try. Świetnie!') === 0);
ok('I7 ... while still reporting the hints',
   PERF.msg.indexOf('You used hints on 2 questions.') !== -1);
ok('I7 the hint sentence never calls a hinted answer wrong',
   PERF.msg.indexOf('wrong') === -1 && PERF.msg.indexOf('to review') === -1 &&
   PERF.msg.indexOf('almost') === -1);
ok('I7 the hint sentence never claims a deduction',
   [I1, I3, PERF, WITHHINT].every(function (r) {
     var m = r.msg;
     return m.indexOf('penal') === -1 && m.indexOf('deduct') === -1 &&
            m.indexOf("doesn't count") === -1 && m.indexOf('not count') === -1;
   }));
// and a hinted round on a small topic still adds up
var SMALLDONE = finish({ 0: 'miss' }, { 1: 1 }, C6);
eq('I8 a six-question round reports out of six', SMALLDONE.counter, '6 / 6');
eq('I8 ... with the tiles summing to six',
   Number(SMALLDONE.correct) + Number(SMALLDONE.almost) + Number(SMALLDONE.missed), 6);
ok('I8 ... and its own hint sentence', SMALLDONE.msg.indexOf('You used a hint on 1 question.') !== -1);

// =========================================================================
// J. RESET - a new round is a new round
// =========================================================================
var J = finish({ 0: 'miss', 3: 'miss' }, { 1: 2, 4: 1 }, C15);
eq('J1 the finished round counted its hints', R.hinted, 2);
eq('J1 ... and grew past its original total', R.qs.length > R.originalTotal, true);
var beforeTotal = R.originalTotal;
activate('rAgain');                                  // the shipping "Practice again" handler
eq('J1 Practice again re-entered a question', R.i, 0);
eq('J1 ... and cleared the hint counter', R.hinted, 0);
eq('J1 ... and re-fixed the original total', R.originalTotal, R.qs.length);
eq('J1 ... to the same size for the same topic', R.originalTotal, beforeTotal);
eq('J1 ... and dropped every requeued copy',
   R.qs.filter(function (x) { return x.requeued; }).length, 0);
eq('J1 ... and the counter reads the new round', counter(), '1 / 15');
eq('J1 ... with the bar back at zero', barPct(), 0);
ok('J1 ... and no review marker anywhere', prompt_().indexOf('Review') === -1);

// a smaller topic next: the new round owns its own total
LEVELS[0].topics[0].cards = C6;
activate('rAgain');
eq('J2 a smaller round banks its own original total', R.originalTotal, 6);
eq('J2 ... and reads 1 / 6', counter(), '1 / 6');
eq('J2 ... with no hints carried over', R.hinted, 0);
// and back to a larger one
LEVELS[0].topics[0].cards = C15;
activate('rAgain');
eq('J3 a larger round banks its own original total', R.originalTotal, 15);
eq('J3 ... and reads 1 / 15', counter(), '1 / 15');
eq('J3 ... still with no hints carried over', R.hinted, 0);
// nothing leaks the other way either: hints in round two are round two's alone
MIXED.rRevealLetter();                              // q0 is a listen question - no reveal path
answer('right'); advance();
MIXED.rRevealLetter(); answer('right'); advance();  // q1 typed, hinted
eq('J4 round two counted its own single hint', R.hinted, 1);
activate('rAgain');
eq('J4 round three starts clean again', R.hinted, 0);
ok('J4 ... and startRound is what clears it', hasCode(codeOnly(RSRC.startRound), 'R.hinted = 0'));

// =========================================================================
// K. WIRING - the claims above, made against the source rather than a run
// =========================================================================
var CODE_RENDER = codeOnly(RSRC.rRender);
var CODE_START = codeOnly(RSRC.startRound);
var CODE_CHECK = codeOnly(RSRC.rCheckAnswer);
var CODE_DONE = codeOnly(RSRC.rShowDone);
var CODE_RECORD = codeOnly(RSRC.rRecord);

// the total is fixed from the built list, in startRound, before anything can requeue
ok('K1 startRound fixes the original total from the question list',
   hasCode(CODE_START, 'R.originalTotal = R.qs.length'));
ok('K1 ... after the list is built', (function () {
  var build = squash(CODE_START).indexOf('R.qs=gShuffle('), fix = squash(CODE_START).indexOf('R.originalTotal=R.qs.length');
  return build !== -1 && fix !== -1 && build < fix;
})());
ok('K1 ... and startRound is the only place it is assigned',
   countOf(codeOnly(INDEX), 'R.originalTotal =') + countOf(codeOnly(INDEX), 'R.originalTotal=') === 1);
ok('K1 the state object declares both new fields',
   /originalTotal\s*:\s*0/.test(R_LITERAL) && /hinted\s*:\s*0/.test(R_LITERAL));

// rRender never measures an original question against the mutable array. R.qs.length
// still appears in it twice, and both are about the RENDERED list rather than the size
// of the round: the guard that ends the round, and the last-question test that chooses
// the Next label. Neither is a denominator, and both must stay - a round that ignored
// the grown array would never render its reviews at all.
eq('K2 rRender mentions the mutable array exactly once',
   squash(CODE_RENDER).split('R.qs.length').length - 1, 1);
ok('K2 the one use is the guard that ends the round',
   hasCode(CODE_RENDER, 'if(R.i >= R.qs.length){ rShowDone(); return; }'));
// what matters: neither of the two things the learner reads as progress touches it
ok('K2 the counter is never built from the mutable array', (function () {
  var m = squash(CODE_RENDER).match(/\$\("rCountLbl"\)\.textContent=[^;]*;/g) || [];
  return m.length >= 1 && m.every(function (s) { return s.indexOf('R.qs.length') === -1; });
})());
ok('K2 the bar is never built from the mutable array', (function () {
  var m = squash(CODE_RENDER).match(/\$\("rFill"\)\.style\.width=[^;]*;/g) || [];
  return m.length >= 1 && m.every(function (s) { return s.indexOf('R.qs.length') === -1; });
})());
ok('K2 the counter is built from the original total',
   hasCode(CODE_RENDER, '$("rCountLbl").textContent=(R.i+1)+" / "+rOriginalTotal()'));
ok('K2 the bar is built from the original total',
   hasCode(CODE_RENDER, '$("rFill").style.width=rPct(R.i, rOriginalTotal())+"%"'));
ok('K2 the original denominator helper reads R.originalTotal and nothing else',
   codeOnly(RSRC.rOriginalTotal).indexOf('R.originalTotal') !== -1 &&
   codeOnly(RSRC.rOriginalTotal).indexOf('R.qs') === -1);

// review progress derives from the retry flag
ok('K3 rRender branches on the retry flag', hasCode(CODE_RENDER, 'if(q.requeued){'));
ok('K3 the review counter is built from the derived position',
   hasCode(CODE_RENDER, '$("rCountLbl").textContent="Review "+rev.at+" / "+rev.total'));
ok('K3 the review position is derived from the retry flags in R.qs',
   codeOnly(RSRC.rReviewPos).indexOf('requeued') !== -1);
ok('K3 the review position is not a stored mutable counter',
   codeOnly(INDEX).indexOf('R.reviewTotal') === -1 && codeOnly(INDEX).indexOf('R.reviewAt') === -1);
ok('K4 the bar stays complete during review', hasCode(CODE_RENDER, '$("rFill").style.width="100%"'));

// the hint is counted once, on an original typed submission
ok('K5 rCheckAnswer counts a hinted original question',
   hasCode(CODE_CHECK, 'if(R.revealed>0 && !q.requeued) R.hinted++'));
ok('K5 ... after the state guard has closed the question', (function () {
  var s = squash(CODE_CHECK);
  return s.indexOf('R.state="done";') !== -1 && s.indexOf('R.state="done";') < s.indexOf('R.hinted++');
})());
ok('K5 ... and after the blank guard has returned', (function () {
  var s = squash(CODE_CHECK);
  return s.indexOf('if(!PP_ANSWER.normalize(val))') < s.indexOf('R.hinted++');
})());
ok('K5 the reveal handler itself banks nothing',
   codeOnly(RSRC.rRevealLetter).indexOf('hinted') === -1);
ok('K5 the option handler banks nothing either',
   codeOnly(RSRC.rPickOption).indexOf('hinted') === -1);
ok('K5 R.hinted is incremented in exactly one place',
   countOf(codeOnly(INDEX), 'R.hinted++') === 1);

// the sentence is outside the tier arithmetic
ok('K6 rShowDone still scores original questions only',
   hasCode(CODE_DONE, 'R.qs.filter(q=>!q.requeued)'));
ok('K6 the three tiles are still fed the three tiers',
   hasCode(CODE_DONE, '$("rScoreN").textContent  = right;') &&
   hasCode(CODE_DONE, '$("rAlmostN").textContent = almost;') &&
   hasCode(CODE_DONE, '$("rMissN").textContent   = missed;'));
ok('K6 no tier is computed from the hint count', (function () {
  var s = squash(CODE_DONE);
  return s.indexOf('right-hinted') === -1 && s.indexOf('right+hinted') === -1 &&
         s.indexOf('almost+hinted') === -1 && s.indexOf('missed+hinted') === -1 &&
         s.indexOf('scored.length-hinted') === -1;
})());
ok('K6 the hint sentence is appended to the message and nothing else',
   hasCode(CODE_DONE, 'hinted===1 ? " You used a hint on 1 question."'));
ok('K6 the perfect-round rule is still the right-only one',
   hasCode(CODE_DONE, 'right===total ? "Every question right on the first try'));
// the fixed original total owns every "of N" on this screen, and it comes from the
// helper rather than from the length of a filtered array
ok('K6 the completion total is read from the original-total helper',
   hasCode(CODE_DONE, 'const total = rOriginalTotal()'));
ok('K6 the results counter is built from it',
   hasCode(CODE_DONE, '$("rCountLbl").textContent=total+" / "+total'));
ok('K6 the completion message is built from it',
   hasCode(CODE_DONE, '"You got "+right+" of "+total+" right on the first try."'));
ok('K6 no learner-facing "of N" is taken from scored.length', (function () {
  var s = squash(CODE_DONE);
  return s.indexOf('of"+scored.length') === -1 && s.indexOf('right===scored.length') === -1 &&
         s.indexOf('scored.length+"/"+scored.length') === -1;
})());
ok('K6 the results counter no longer uses the grown array',
   CODE_DONE.indexOf('R.qs.length+" / "+R.qs.length') === -1);
// ... while `scored` still owns the ARITHMETIC and the persistence walk
ok('K6 the tiers are still counted off scored', (function () {
  var s = squash(CODE_DONE);
  return s.indexOf('scored.filter(q=>q.result==="right").length') !== -1 &&
         s.indexOf('scored.filter(q=>q.result==="almost").length') !== -1 &&
         s.indexOf('scored.filter(q=>q.result==="miss").length') !== -1;
})());
ok('K6 the progress writeback still walks scored', hasCode(CODE_DONE, 'scored.forEach(q=>{'));

// K6b. the Next-button wording lives in ONE helper, and every path that can change the
// rendered list re-asks it. rRecord must stay a pure state mutation - it is lifted and
// executed on bare fixtures by tests/test_round_scoring.js, which supplies no DOM at all.
var CODE_SYNC = codeOnly(RSRC.rSyncNextLabel);
var CODE_PICK = codeOnly(RSRC.rPickOption);
ok('K6b the wording rule lives in the helper',
   hasCode(CODE_SYNC, '$("rNextLabel").textContent = R.i===R.qs.length-1 ? "See results" : "Next"'));
ok('K6b the helper measures against the CURRENT rendered list',
   CODE_SYNC.indexOf('R.qs.length') !== -1 && CODE_SYNC.indexOf('rOriginalTotal') === -1);
eq('K6b the label is written in exactly one place in the whole file',
   countOf(codeOnly(INDEX), '$("rNextLabel").textContent'), 1);
ok('K6b rRender delegates to the helper rather than inlining the rule',
   hasCode(CODE_RENDER, 'rSyncNextLabel()') &&
   CODE_RENDER.indexOf('"See results"') === -1);
// both answer paths refresh it AFTER rRecord and BEFORE the button opens
[['rCheckAnswer', CODE_CHECK], ['rPickOption', CODE_PICK]].forEach(function (pair) {
  var name = pair[0], s = squash(pair[1]);
  ok('K6b ' + name + ' refreshes the label', s.indexOf('rSyncNextLabel()') !== -1);
  ok('K6b ' + name + ' refreshes it after rRecord',
     s.indexOf('rRecord(') !== -1 && s.indexOf('rRecord(') < s.indexOf('rSyncNextLabel()'));
  ok('K6b ' + name + ' refreshes it before Next is enabled',
     s.indexOf('rSyncNextLabel()') < s.indexOf('$("rNext").disabled=false'));
  ok('K6b ' + name + ' refreshes it before Next takes focus',
     s.indexOf('rSyncNextLabel()') < s.indexOf('$("rNext").focus()'));
});
ok('K6b rRecord still contains no DOM access at all', (function () {
  var s = CODE_RECORD;
  return s.indexOf('$("') === -1 && s.indexOf('document.') === -1 &&
         s.indexOf('rNextLabel') === -1 && s.indexOf('rSyncNextLabel') === -1;
})());
ok('K6b rRecord still only appends to R.qs', hasCode(CODE_RECORD, 'R.qs.push({'));

// the requeue mechanism is untouched
ok('K7 only a first-try miss is requeued', hasCode(CODE_RECORD, 'if(result==="miss"){'));
ok('K7 a requeued question never scores or re-requeues', hasCode(CODE_RECORD, 'if(q.requeued) return;'));
ok('K7 rRecord knows nothing about progress or hints',
   CODE_RECORD.indexOf('originalTotal') === -1 && CODE_RECORD.indexOf('hinted') === -1);
ok('K7 the retry still rebuilds its options from the retained records',
   hasCode(CODE_RECORD, 'rBuildOptions(right.item, q.options.map(o=>o.item), q.fmt)'));

// nothing persisted changed shape
ok('K8 progress is still written as still/known id lists',
   hasCode(CODE_DONE, 'store.progress[tRound.id] = { still:[...still], known:[...known] }'));
ok('K8 the hint count is never persisted',
   CODE_DONE.indexOf('hinted') !== -1 &&                       // it IS used in the message
   squash(CODE_DONE).indexOf('hinted:') === -1 &&              // but never written into a record
   squash(CODE_DONE).indexOf('store.hinted') === -1);
ok('K8 the original total is never persisted',
   squash(CODE_DONE).indexOf('originalTotal:') === -1);
ok('K8 the progress guards are unchanged',
   hasCode(CODE_DONE, 'if(ppProgressWritable() && tRound && tRound.id)') &&
   hasCode(CODE_DONE, 'if(!id || (q.c && q.c.intro)) return;'));

// the progress path started no audio
eq('K9 rendering progress started no clip and no utterance',
   AUDIO_MADE.length + UTTER_MADE.length, 0);

// ---------- report ----------
info('rounds driven end to end: 17-, 15-, 14-, 6-, 3- and 2-question topics, 0-4 requeued reviews');
info('the 2- and 14-card topics end on a TYPED question and the 15-card one on multiple');
info('     choice, so the final-original retry is exercised in both answer paths');
info('the counter, the bar, the prompt, the Next label and the done message are read back');
info('     from the fake DOM the shipping rRender/rShowDone actually wrote to');
info('scoring, requeue policy and option construction are asserted UNCHANGED here, and');
info('     owned by tests/test_round_scoring.js, test_mixed_distractors.js and test_sense_groups.js');
console.log('Mixed Quiz round legibility tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
LOG.forEach(function (l) { console.log('  ' + l); });
if (FAIL > 0) { throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed'); }
