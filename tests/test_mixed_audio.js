// Deterministic tests for the MIXED QUIZ's audio lifecycle in index.html.
// Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_mixed_audio.js
// Exit status is 0 only if every assertion passes (printed at the end).
//
// WHAT THIS PINS DOWN
// The Mixed Quiz has audio on every format, not just on "listen": the Play button
// belongs to a listen question, but the feedback panel that follows ANY answer
// carries example and canonical-answer buttons, and all of them go through the one
// shared slot (currentAudio / speakBtn). Neither show() nor rRender() touches audio,
// so before Phase 4C a clip started in a question played on over the next question,
// over the results screen, and over the home screen - and a new round started on top
// of it. This file drives the SHIPPING boundary helpers (rAdvance, rExit,
// startRound) and asserts both the cleanup and its ORDER: the audio is already
// released by the time the next question renders or Home appears.
//
// It also pins the READINESS half. audioMap is empty for the whole time
// audio-manifest.json is in flight, and an empty map reads exactly like "this phrase
// has no clip" - so a press during that window heard the device voice for a phrase
// that HAS a Marek recording, while the identical press a second later played the
// MP3. audioManifestStatus is what tells "not known yet" apart from "not there", and
// the Mixed Quiz Play button is held closed until it settles. Settlement OPENS the
// button and plays nothing: no queued first press, no autoplay, and no focus move -
// by the time the manifest lands, an early press is no longer inside the learner's
// gesture, and mobile browsers refuse audio started outside one.
//
// HOW IT AVOIDS A REAL NETWORK
// Nothing here goes near the network or a real <audio> element. The Audio object,
// speechSynthesis and the DOM are fakes the test drives directly, so every ordering
// is reproduced on demand rather than waited for. The fake play() returns a
// hand-rolled thenable settled BY HAND, not a real Promise: osascript has no run loop
// draining the microtask queue, so a real rejection would never be delivered inside a
// script that exits at the end of its first job. Both are modelled on the ones in
// tests/test_audio_fallback.js, which owns the shared engine itself.
//
// WHAT IT DELIBERATELY DOES NOT OWN
//   - the shared audio engine, the duplicate-fallback latch and the manifest-parsing
//     matrix: tests/test_audio_fallback.js
//   - the Listening lifecycle and Listening readiness: tests/test_audio_fallback.js
//     and tests/test_listening_accessibility.js
//   - Mixed Quiz announcements, option names and per-format focus in the SETTLED
//     case: tests/test_mixed_accessibility.js
//   - scoring, requeueing and option construction: tests/test_round_scoring.js and
//     tests/test_distractors.js
ObjC.import('Foundation');

function readFile(path) {
  var s = $.NSString.stringWithContentsOfFileEncodingError(path, $.NSUTF8StringEncoding, null);
  return ObjC.unwrap(s);
}
// Portable root resolution: the documented command runs from the repo root; also
// tolerate being run from inside tests/. No hard-coded absolute path.
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
var PASS = 0, FAIL = 0, LOG = [], INFO = [];
function ok(name, cond) { if (cond) { PASS++; } else { FAIL++; LOG.push('FAIL: ' + name); } }
function eq(name, a, b) {
  var sa = JSON.stringify(a), sb = JSON.stringify(b);
  ok(name + (sa === sb ? '' : '  (got ' + sa + ', want ' + sb + ')'), sa === sb);
}

// ---------- pull the real functions out of index.html ----------
// Brace scanner that skips comments and strings. It deliberately does NOT model
// regex literals: no function extracted below contains a regex carrying a brace,
// quote or backtick. If one ever does, extraction produces a broken snippet and the
// eval throws - a loud failure, which is the correct outcome.
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

// Comment-stripped view of a snippet. Ordering assertions must be decided by code,
// not by prose that happens to mention a call.
function stripComments(src) {
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

// Paren-matching, because a Mixed Quiz handler body contains calls of its own - a
// non-greedy "up to the first );" would cut an arrow body in half. Works for any
// event, so the typed input's keydown handler is read the same way as the clicks.
function handlerExpr(id, evt) {
  evt = evt || 'click';
  var re = new RegExp('\\$\\(\\s*["\']' + id + '["\']\\s*\\)\\s*\\.addEventListener\\(\\s*["\']' + evt + '["\']\\s*,', 'g');
  var hits = [], m;
  while ((m = re.exec(INDEX)) !== null) hits.push(m.index + m[0].length);
  if (hits.length !== 1) throw new Error('wiring: expected exactly one ' + evt + ' handler for ' + id + ', found ' + hits.length);
  return sliceParens(hits[0]);
}
function sliceParens(start) {
  var depth = 1, mode = 'code';
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
  throw new Error('wiring: unbalanced handler expression');
}
// The delegated [data-say] listener, so section L drives the SHIPPING feedback-audio
// entry point rather than a description of it. index.html binds more than one
// document-level click listener, so the one that handles data-say is selected by
// what it contains.
function dataSayListener() {
  var re = /document\.addEventListener\(\s*["']click["']\s*,/g, m, hits = [];
  while ((m = re.exec(INDEX)) !== null) {
    var body = sliceParens(m.index + m[0].length);
    if (body.indexOf('data-say') !== -1) hits.push(body);
  }
  if (hits.length !== 1) throw new Error('wiring: expected exactly one [data-say] click listener, found ' + hits.length);
  return hits[0];
}

// What actually runs when a control is activated: the expression itself, or the
// single named function it delegates to. Inline body or named helper both resolve -
// the assertion is about behaviour, not about which style was chosen.
function handlerBody(id, evt) {
  var code = stripComments(handlerExpr(id, evt)).trim();
  var bare = code.match(/^([A-Za-z_$][A-Za-z0-9_$]*)$/);
  if (bare) return stripComments(extractFunction(INDEX, bare[1]));
  var delegate = code.match(/^\(\s*\)\s*=>\s*([A-Za-z_$][A-Za-z0-9_$]*)\s*\(/);
  if (delegate) return stripComments(extractFunction(INDEX, delegate[1]));
  return code;
}

// ---------- the shared audio engine, real ----------
var SRC = {};
['ppNormalize', 'clearSpeaking', 'stopAllAudio', 'speakText', 'playPreGenerated',
 'speakCardMain', 'speakFallback', 'currentRate', 'settleAudioManifest'
].forEach(function (n) { SRC[n] = extractFunction(INDEX, n); });

// The speed table ships in index.html too - read it rather than restating it, so a
// changed rate is caught here instead of silently passing.
var speedsMatch = INDEX.match(/const\s+SPEEDS\s*=\s*(\{[^}]*\})\s*;/);
if (!speedsMatch) throw new Error('extract: SPEEDS table not found in index.html');
var SPEEDS = (0, eval)('(' + speedsMatch[1] + ')');

var window = {};                                          // the shared helpers attach themselves here
(0, eval)(readFile(ROOT + 'pp-usage.js'));
(0, eval)(readFile(ROOT + 'pp-answer.js'));
var PP_ANSWER = window.PP_ANSWER;                         // the REAL comparator decides typed verdicts
var ppMainAudioText = window.PP_USAGE.mainAudioText;      // index.html binds these the same way
var ppHasMainAudio = window.PP_USAGE.hasMainAudio;

// A thenable the test settles by hand. See the header for why this is not a Promise.
function Thenable() { this.onRejected = null; this.done = false; }
Thenable.prototype.catch = function (fn) { this.onRejected = fn; return this; };
Thenable.prototype.then = function (onF, onR) { if (onR) this.onRejected = onR; return this; };
Thenable.prototype.reject = function (err) {
  if (this.done) return;                                  // a promise settles once, like the real thing
  this.done = true;
  if (this.onRejected) this.onRejected(err);
};
Thenable.prototype.resolve = function () { this.done = true; };

function FakeAudio(src) {
  this.src = src;
  this.playbackRate = 1;
  this.preservesPitch = false;
  this.onended = null;
  this.onerror = null;
  this.pauses = 0;
  this.playCount = 0;
  this.promise = null;
  FakeAudio.created.push(this);
}
FakeAudio.created = [];
FakeAudio.prototype.play = function () { this.playCount++; this.promise = new Thenable(); return this.promise; };
FakeAudio.prototype.pause = function () { this.pauses++; };
// Firing through the live handler property is deliberate: once the code under test
// detaches a handler, firing that event really is a no-op, exactly as it would be for
// a detached listener in a browser.
FakeAudio.prototype.fireError = function () { if (this.onerror) this.onerror({ type: 'error' }); };
FakeAudio.prototype.fireEnded = function () { if (this.onended) this.onended({ type: 'ended' }); };
FakeAudio.prototype.rejectPlay = function (name) { this.promise.reject({ name: name || 'NotSupportedError' }); };

function FakeSynth() { this.spoken = []; this.cancels = 0; }
FakeSynth.prototype.speak = function (u) { this.spoken.push(u); };
FakeSynth.prototype.cancel = function () { this.cancels++; };
FakeSynth.prototype.getVoices = function () { return []; };
function FakeUtterance(text) {
  this.text = text; this.lang = ''; this.rate = 1; this.voice = null;
  this.onend = null; this.onerror = null;
}
var synth = new FakeSynth();
window.speechSynthesis = synth;
var speechSynthesis = synth;
var SpeechSynthesisUtterance = FakeUtterance;
var Audio = FakeAudio;
function voiceHint() {}                                   // real one touches localStorage + DOM

// module-level state the extracted functions read and write
var audioMap = {};
var audioManifestStatus = 'loading';
var currentAudio = null;
var speakBtn = null;
var plVoice = null;
var currentSpeed = 'normal';
// settleAudioManifest refreshes BOTH activities' Play buttons. Listening's is owned
// by tests/test_audio_fallback.js; here it is a counter, so "settlement still calls
// it" stays observable without pulling the Listening screen into this file. The
// Mixed Quiz one is the real helper, compiled into the scope below (it needs $ and R,
// which are handed in as parameters there), reached through this one-line delegate.
var syncListeningCalls = 0;
function syncListeningAudioReadiness() { syncListeningCalls++; }
function syncRoundAudioReadiness() { return MIXED.syncReadiness(); }

Object.keys(SRC).forEach(function (n) { (0, eval)(SRC[n]); });

// ---------- a fake DOM: just enough for the real Mixed Quiz screen code ----------
var ACTIVE = null, BODY = null, HTML_WRITES = {};
function FakeEl(tag) {
  this.tag = tag || 'div';
  this._own = '';
  this.className = '';
  this.value = '';
  this.hidden = false;
  this.style = {};
  this.children = [];
  this.classes = {};
  this._html = '';
  this._attrs = {};
  this._on = {};
  this._disabled = false;
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
    if (this._disabled && ACTIVE === this) ACTIVE = BODY;   // the browser rule the loading gate trips over
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
// innerHTML parses just far enough for the feedback and verdict panels to be
// inspectable: one flat child per tag, carrying that tag's class and data-say.
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
      var dm = m[2].match(/\sdata-say\s*=\s*"([^"]*)"/);
      if (dm) kid.setAttribute('data-say', dm[1]);
      var am = m[2].match(/\saria-label\s*=\s*"([^"]*)"/);
      if (am) kid.setAttribute('aria-label', am[1]);
      this.children.push(kid);
    }
  }
});
Object.defineProperty(FakeEl.prototype, 'childNodes', { get: function () { return this.children; } });
// same accessor the boundary assertions use on rPlay, so any button reads alike
Object.defineProperty(FakeEl.prototype, 'speaking', { get: function () { return this.classes.speaking === true; } });
FakeEl.prototype.appendChild = function (el) { this.children.push(el); return el; };
FakeEl.prototype.setAttribute = function (k, v) { this._attrs[k] = String(v); };
FakeEl.prototype.getAttribute = function (k) { return Object.prototype.hasOwnProperty.call(this._attrs, k) ? this._attrs[k] : null; };
FakeEl.prototype.addEventListener = function (t, fn) { (this._on[t] = this._on[t] || []).push(fn); };
FakeEl.prototype.click = function () { (this._on.click || []).forEach(function (fn) { fn({}); }); };
FakeEl.prototype.focus = function () {
  if (this._disabled) return;                                // a disabled control cannot take focus
  if (this.hidden) return;                                   // nor can one that is not rendered
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
// outright, otherwise the button's own text.
FakeEl.prototype.accName = function () {
  var l = this.getAttribute('aria-label');
  return l === null ? this.textContent : l;
};

var DOM = {};
function el(id) {                                            // index.html's $()
  if (!DOM[id]) { DOM[id] = new FakeEl('#' + id); DOM[id].id = id; }
  return DOM[id];
}
var fakeDoc = {
  createElement: function (t) { return new FakeEl(t); },
  createTextNode: function (t) { return { nodeType: 3, textContent: String(t) }; }
};

// show() is stubbed, and records the audio state AT THE MOMENT IT IS CALLED - that
// is how "Home is shown only after cleanup" becomes an assertion rather than an
// assumption. It also moves the `active` class the way index.html's showScreen does,
// because the readiness helper and the playback guard both read it.
var shown = [];
function pauseTotal() { return FakeAudio.created.reduce(function (n, a) { return n + a.pauses; }, 0); }
var SCREENS = ['home', 'round', 'listen', 'study'];
function fakeShow(scr) {
  shown.push({ scr: scr, audio: currentAudio, pauses: pauseTotal(), btn: speakBtn,
               cancels: synth.cancels, speaking: el('rPlay').speaking });
  SCREENS.forEach(function (s) { el(s).classList.remove('active'); });
  el(scr).classList.add('active');
}

// gShuffle is deterministic: identity, so rBuildOptions leaves the correct gloss
// last and the format cycle runs listen / type / mc from question 0.
function identity(a) { return a.slice(); }
function fakeShuffle(a) { return identity(a); }
function fakeEligible() { return true; }                     // owned by tests/test_typeit_eligibility.js
function fakeAppendUsage() {}                                // owned by tests/test_activities.js
function ppVariantPartsStub() { return null; }               // owned by tests/test_typeit_feedback.js
function fakeProgressWritable() { return false; }            // owned by tests/test_round_scoring.js
var STORE = { progress: {} };
function fakeLoadV2() { return STORE; }
function fakeSaveV2(s) { STORE = s; }

// A six-card topic. Distinct glosses, so rBuildOptions returns four options every
// time; the first card carries an example so the feedback panel really builds a
// mini-audio button, and the round is fully deterministic. With an identity shuffle
// the formats cycle listen / type / mc from question 0, so questions 0 and 3 are
// listen questions and question 5 (the last) is a multiple-choice one.
var CARDS = [
  { id: 'm1', pl: 'kawa',  en: 'coffee', ex: 'Poproszę kawę.', exEn: 'A coffee, please.' },
  { id: 'm2', pl: 'mąka',  en: 'flour' },
  { id: 'm3', pl: 'woda',  en: 'water' },
  { id: 'm4', pl: 'sok',   en: 'juice' },
  { id: 'm5', pl: 'mleko', en: 'milk' },
  { id: 'm6', pl: 'chleb', en: 'bread' }
];
var LEVELS = [{ level: 'A1', topics: [{ id: 'topic-1', name: 'W kawiarni', src: ['A1'],
                                        kind: 'mixed', cards: CARDS }] }];
function fakePoolFor() { return CARDS.map(function (c) { return { c: c, topic: 'W kawiarni' }; }); }
var PP_TYPED_INDEX = PP_ANSWER.buildIndex(CARDS);

// ---------- the Mixed Quiz scope ----------
// The Mixed Quiz functions need $, document, show and the app helpers. `$` is already
// taken here - it is JXA's ObjC bridge - so they are handed in as PARAMETERS of a
// generated scope rather than planted as globals. Everything they share with the
// audio engine above (stopAllAudio, speakText, speakCardMain, currentAudio,
// speakBtn, audioManifestStatus) still resolves to the same globals the engine was
// eval'd into, so the two halves test one system, not two.
//
// The controls are compiled into that scope from their handler expressions as
// index.html writes them, so activate() below runs what the app actually binds - not
// a copy of it. (They cannot be eval'd on demand instead: under osascript a direct
// eval inside a nested function resolves globally, so it would not see this scope.)
var RNAMES = ['rBuildOptions', 'startRound', 'rSetBlocks',
              'rSetStatus', 'rAnnounceWrong', 'rAnnounceCorrect', 'rFocusNextOption',
              'rRender', 'syncRoundAudioReadiness', 'rPlayCurrent',
              'rPickOption', 'rRevealLetter', 'rCheckAnswer', 'rRecord', 'rShowDone',
              'rAdvance', 'rExit'];
var RSRC = {};
RNAMES.forEach(function (n) { RSRC[n] = extractFunction(INDEX, n); });
var R_CONTROLS = ['rNext', 'rCheck', 'rHint', 'rPlay', 'rAgain', 'rBack', 'rBackBtn'];
var rStateMatch = INDEX.match(/const\s+R\s*=\s*(\{[^}]*\})\s*;/);
if (!rStateMatch) throw new Error('extract: Mixed Quiz state object R not found in index.html');
var R = (0, eval)('(' + rStateMatch[1] + ')');

var MIXED = (new Function('$', 'document', 'show', 'R', 'LEVELS', 'poolFor', 'gShuffle',
  'ppEligibleFor', 'ppAppendUsageTo', 'ppVariantParts', 'ppProgressWritable', 'loadV2', 'saveV2',
  'PP_ANSWER', 'PP_TYPED_INDEX', 'ppHasMainAudio', 'ppMainAudioText', 'G_AUDIO',
  RNAMES.map(function (n) { return RSRC[n]; }).join('\n') + '\n' +
  // one wrapper so a test can watch the exact moment the next question renders
  'var __spy = null, __realRender = rRender;\n' +
  'rRender = function(){ if(__spy) __spy(); return __realRender(); };\n' +
  'return {\n' +
  '  spyRender: function(fn){ __spy = fn; },\n' +
  '  startRound: function(a,b){ return startRound(a,b); },\n' +
  '  rRender: function(){ return rRender(); },\n' +
  '  rShowDone: function(){ return rShowDone(); },\n' +
  '  rPlayCurrent: function(){ return rPlayCurrent(); },\n' +
  '  rAdvance: function(){ return rAdvance(); },\n' +
  '  rExit: function(){ return rExit(); },\n' +
  '  syncReadiness: function(){ return syncRoundAudioReadiness(); },\n' +
  '  keydown: (' + handlerExpr('rInput', 'keydown') + '),\n' +
  '  dataSay: (' + dataSayListener() + '),\n' +
  '  handlers: {\n' +
  R_CONTROLS.map(function (id) { return '    ' + id + ': (' + handlerExpr(id) + ')'; }).join(',\n') + '\n' +
  '  }\n' +
  '};'
))(el, fakeDoc, fakeShow, R, LEVELS, fakePoolFor, fakeShuffle,
   fakeEligible, fakeAppendUsage, ppVariantPartsStub, fakeProgressWritable, fakeLoadV2, fakeSaveV2,
   PP_ANSWER, PP_TYPED_INDEX, ppHasMainAudio, ppMainAudioText, '<svg data-icon="audio"></svg>');
function activate(id) { return MIXED.handlers[id](); }

// ---------- per-test setup ----------
var CLIPS = {};
CARDS.forEach(function (c) { CLIPS[c.pl] = 'audio/r-' + c.id + '.mp3'; });
CLIPS['Poproszę kawę.'] = 'audio/r-ex-m1.mp3';
function manifestEntries() {
  var e = {}, i = 0;
  Object.keys(CLIPS).forEach(function (pl) { e['e' + (i++)] = { pl: pl, file: CLIPS[pl] }; });
  return { entries: e };
}
// `status` is what the app holds at the moment the round opens: 'loading' means the
// manifest is still in flight, and audioMap is EMPTY then - which is literally what
// makes an ungated press pick the device voice for a phrase Marek has recorded.
function reset(o) {
  o = o || {};
  DOM = {}; shown = []; HTML_WRITES = {};
  FakeAudio.created = []; synth.spoken = []; synth.cancels = 0;
  currentAudio = null; speakBtn = null; currentSpeed = 'normal';
  syncListeningCalls = 0;
  STORE = { progress: {} };
  audioManifestStatus = o.status || 'ready';
  audioMap = {};
  if (audioManifestStatus === 'ready') Object.keys(CLIPS).forEach(function (k) { audioMap[k] = CLIPS[k]; });
  MIXED.spyRender(null);
  BODY = new FakeEl('body'); BODY.id = 'BODY'; DOM.BODY = BODY;
  ACTIVE = BODY;
  MIXED.startRound(0, 0);
  if (o.at !== undefined) { R.i = o.at; MIXED.rRender(); }
  shown = [];                                     // the round's own show() is not what a boundary did
}
function play() { return el('rPlay'); }
function lastAudio() { return FakeAudio.created[FakeAudio.created.length - 1]; }
function lastSrc() { var a = lastAudio(); return a ? a.src : '(no clip was created)'; }
// The learner really pressing Play. A browser delivers neither click nor Enter nor
// Space to a disabled control, so this refuses exactly where the browser would, and
// otherwise runs the handler index.html actually binds.
function pressPlay() { if (play().disabled) return null; activate('rPlay'); return lastAudio(); }
function opts() { return el('rOpts').children; }
function q() { return R.qs[R.i]; }
function correctBtn() {
  var cur = q(), list = opts();
  for (var i = 0; i < cur.options.length; i++) if (cur.options[i] === cur.c.en) return list[i];
  throw new Error('fixture: no correct option in question ' + R.i);
}
// Answer the current multiple-choice-style question correctly, which is what builds
// the feedback panel and its mini-audio button.
function answerRight() { correctBtn().click(); }
// The shipping delegated listener, driven with the button the feedback panel built.
function pressFeedbackAudio(btn) {
  MIXED.dataSay({ target: { closest: function (sel) { return sel === '[data-say]' ? btn : null; } },
                  stopPropagation: function () {} });
  return lastAudio();
}
function feedbackAudioBtn(host) {
  var kids = el(host).children;
  for (var i = 0; i < kids.length; i++) if (kids[i].getAttribute('data-say') !== null) return kids[i];
  return null;
}

// The fixture must really produce the formats it claims to, or every per-format
// assertion below is about the wrong question.
reset();
eq('A0 the round is the sampled 15-or-fewer questions', R.qs.length, CARDS.length);
eq('A0 question 0 is the listen format', R.qs[0].fmt, 'listen');
eq('A0 question 1 is the typed format', R.qs[1].fmt, 'type');
eq('A0 question 2 is the multiple-choice format', R.qs[2].fmt, 'mc');
eq('A0 question 3 is a second listen question', R.qs[3].fmt, 'listen');
eq('A0 the last question is not a listen question', R.qs[R.qs.length - 1].fmt, 'mc');
ok('A0 the round screen is the active one', el('round').classList.contains('active'));

// =========================================================================
// A. BASELINE GATE - nothing may play while the manifest is in flight
// =========================================================================
reset({ status: 'loading', at: 0 });
eq('A1 the manifest is still loading', audioManifestStatus, 'loading');
eq('A1 the current question is a listen question', q().fmt, 'listen');
ok('A1 Play is disabled while loading', play().disabled === true);
eq('A1 Play reports itself busy', play().getAttribute('aria-busy'), 'true');
eq('A1 the accessible name says audio is loading', play().accName(), 'Polish audio is loading');
ok('A1 Play is visible - it is the listen question\'s own control', play().hidden === false);
// activation, the way a learner reaches it
ok('A2 a click on the disabled button starts nothing', (function () {
  var before = FakeAudio.created.length;
  pressPlay();                                              // refuses, exactly as a browser does
  return FakeAudio.created.length === before && synth.spoken.length === 0;
})());
// and the same call made directly, which `disabled` cannot stop
MIXED.rPlayCurrent();
eq('A3 a direct rPlayCurrent call creates no clip while loading', FakeAudio.created.length, 0);
eq('A3 a direct rPlayCurrent call speaks nothing while loading', synth.spoken.length, 0);
ok('A3 no button was marked speaking', play().speaking === false && speakBtn === null);
ok('A3 nothing was left playing', currentAudio === null);
// the press is refused, not remembered
audioManifestStatus = 'ready';
Object.keys(CLIPS).forEach(function (k) { audioMap[k] = CLIPS[k]; });
settleAudioManifest(manifestEntries());
eq('A4 no request was queued for after settlement - no clip', FakeAudio.created.length, 0);
eq('A4 no request was queued for after settlement - no utterance', synth.spoken.length, 0);
ok('A4 nothing is playing after settlement', currentAudio === null && speakBtn === null);

// =========================================================================
// B. SUCCESSFUL SETTLEMENT - the button opens, and only the button
// =========================================================================
reset({ status: 'loading', at: 0 });
var focusedBeforeB = ACTIVE;
settleAudioManifest(manifestEntries());
eq('B1 the manifest settled ready', audioManifestStatus, 'ready');
ok('B1 Play is enabled for the current listen question', play().disabled === false);
eq('B1 Play no longer reports itself busy', play().getAttribute('aria-busy'), 'false');
eq('B1 the accessible name is back to the ordinary one', play().accName(), 'Play the Polish audio');
eq('B2 settlement created no Audio object', FakeAudio.created.length, 0);
eq('B2 settlement created no utterance', synth.spoken.length, 0);
ok('B2 settlement started nothing at all', currentAudio === null && speakBtn === null);
ok('B3 settlement moved no focus', ACTIVE === focusedBeforeB);
eq('B3 settlement still refreshes the Listening button too', syncListeningCalls, 1);
// and NOW a press plays the manifest clip
var bClip = pressPlay();
eq('B4 pressing Play afterwards uses the manifest MP3', lastSrc(), CLIPS['kawa']);
eq('B4 exactly one clip was created', FakeAudio.created.length, 1);
eq('B4 no device voice was used', synth.spoken.length, 0);
ok('B4 the pressed button is marked speaking', play().speaking === true && speakBtn === play());
ok('B4 the clip is the shared current audio', currentAudio === bClip);

// =========================================================================
// C. FAILED AND MALFORMED SETTLEMENT - unavailable is a SETTLED answer
//    (the full parsing matrix is owned by tests/test_audio_fallback.js)
// =========================================================================
[['null manifest', null],
 ['a manifest with no entries', {}],
 ['an array where a dictionary belongs', { entries: [] }]
].forEach(function (pair) {
  reset({ status: 'loading', at: 0 });
  settleAudioManifest(pair[1]);
  ok('C1 ' + pair[0] + ' settles to a settled state', audioManifestStatus !== 'loading');
  ok('C1 ' + pair[0] + ' opens Play for the current listen question', play().disabled === false);
  eq('C1 ' + pair[0] + ' leaves aria-busy false', play().getAttribute('aria-busy'), 'false');
  eq('C1 ' + pair[0] + ' creates no audio at settlement', FakeAudio.created.length, 0);
  eq('C1 ' + pair[0] + ' creates no utterance at settlement', synth.spoken.length, 0);
});
reset({ status: 'loading', at: 0 });
settleAudioManifest(null);
eq('C2 a failed manifest settles unavailable', audioManifestStatus, 'unavailable');
var cFocus = ACTIVE;
pressPlay();
eq('C2 pressing Play then uses speech synthesis', synth.spoken.length, 1);
eq('C2 the fallback said the card\'s own Polish', synth.spoken[0].text, 'kawa');
eq('C2 no MP3 was requested', FakeAudio.created.length, 0);
ok('C2 the press did not move focus off Play', ACTIVE === cFocus);
pressPlay();
eq('C3 a second press is a second single utterance', synth.spoken.length, 2);
eq('C3 the second press cancelled the first', synth.cancels >= 1, true);

// =========================================================================
// D. MISSING CURRENT PHRASE - a ready manifest with no entry for this card
// =========================================================================
reset({ status: 'loading', at: 0 });
settleAudioManifest({ entries: { e0: { pl: 'herbata', file: 'audio/other.mp3' } } });
eq('D1 the manifest settled ready', audioManifestStatus, 'ready');
ok('D1 Play is enabled even though this card has no entry', play().disabled === false);
eq('D1 settlement itself played nothing', FakeAudio.created.length + synth.spoken.length, 0);
pressPlay();
eq('D2 one press produces exactly one fallback', synth.spoken.length, 1);
eq('D2 the fallback said the current card', synth.spoken[0].text, 'kawa');
eq('D2 no MP3 was created', FakeAudio.created.length, 0);
ok('D2 nothing was duplicated', synth.spoken.length === 1 && currentAudio === null);

// =========================================================================
// E. NON-LISTEN FORMATS - a hidden Play is never an actionable one
// =========================================================================
[['type', 1], ['mc', 2]].forEach(function (pair) {
  reset({ at: pair[1] });
  eq('E1 question ' + pair[1] + ' is the ' + pair[0] + ' format', q().fmt, pair[0]);
  ok('E1 ' + pair[0] + ': Play is hidden', play().hidden === true);
  ok('E1 ' + pair[0] + ': Play is disabled', play().disabled === true);
  eq('E1 ' + pair[0] + ': aria-busy is false, not a false loading claim', play().getAttribute('aria-busy'), 'false');
  MIXED.rPlayCurrent();
  eq('E2 ' + pair[0] + ': a direct call creates no clip', FakeAudio.created.length, 0);
  eq('E2 ' + pair[0] + ': a direct call speaks nothing', synth.spoken.length, 0);
  ok('E2 ' + pair[0] + ': nothing is playing', currentAudio === null && speakBtn === null);
});
// the same while the manifest is still loading: still hidden, still disabled, and
// still not claiming to be loading anything
reset({ status: 'loading', at: 2 });
ok('E3 a loading mc question keeps Play hidden and disabled', play().hidden === true && play().disabled === true);
eq('E3 a hidden button does not claim to be loading', play().getAttribute('aria-busy'), 'false');

// =========================================================================
// F. RESULTS SCREEN - no question, no playable button
// =========================================================================
reset();
R.i = R.qs.length; MIXED.rRender();
ok('F1 the results screen is showing', el('rDone').style.display === 'flex' && el('rMain').style.display === 'none');
ok('F1 Play is disabled on the results screen', play().disabled === true);
eq('F1 Play does not claim to be loading', play().getAttribute('aria-busy'), 'false');
MIXED.rPlayCurrent();
eq('F2 a direct call on the results screen creates no clip', FakeAudio.created.length, 0);
eq('F2 a direct call on the results screen speaks nothing', synth.spoken.length, 0);
ok('F2 nothing autoplayed on completion', currentAudio === null && speakBtn === null);
// and settlement arriving while the results are up opens nothing
settleAudioManifest(manifestEntries());
ok('F3 settlement on the results screen leaves Play disabled', play().disabled === true);
eq('F3 settlement on the results screen played nothing', FakeAudio.created.length + synth.spoken.length, 0);

// =========================================================================
// G. NEXT BOUNDARY - the clip is released before the next question renders
// =========================================================================
reset({ at: 0 });
var gClip = pressPlay();
ok('G1 a clip really is playing', gClip && gClip.playCount === 1 && currentAudio === gClip);
ok('G1 the Play button is marked speaking', play().speaking === true && speakBtn === play());
var atRender = null;
MIXED.spyRender(function () {
  atRender = { audio: currentAudio, pauses: gClip.pauses, btn: speakBtn, speaking: play().speaking, i: R.i };
});
activate('rNext');
eq('G2 the clip was paused exactly once', gClip.pauses, 1);
ok('G2 currentAudio was cleared', currentAudio === null);
ok('G2 speakBtn was cleared', speakBtn === null);
ok('G2 the speaking class was removed', play().speaking === false);
ok('G3 cleanup happened BEFORE the next question rendered', atRender !== null && atRender.audio === null && atRender.pauses === 1 && atRender.btn === null);
eq('G3 the next question is the one that rendered', R.i, 1);
eq('G4 the next question started no audio', FakeAudio.created.length, 1);
eq('G4 the next question spoke nothing', synth.spoken.length, 0);
// the abandoned clip's late signals must all be stale no-ops
gClip.rejectPlay('AbortError');                              // pause() guarantees this one
eq('G5 a late play() rejection speaks nothing', synth.spoken.length, 0);
gClip.fireError();
eq('G5 a late error event speaks nothing', synth.spoken.length, 0);
gClip.fireEnded();
eq('G5 a late ended event speaks nothing', synth.spoken.length, 0);
eq('G5 no second Audio object was created', FakeAudio.created.length, 1);
ok('G5 the late signals restored no speaking class', play().speaking === false && speakBtn === null);
ok('G5 the late signals did not disturb the new question', R.i === 1 && currentAudio === null);
// a fallback utterance is cancelled by the same boundary
reset({ status: 'loading', at: 0 });
settleAudioManifest(null);                                   // unavailable -> device voice
pressPlay();
eq('G6 the device voice is speaking', synth.spoken.length, 1);
var cancelsBefore = synth.cancels;
activate('rNext');
ok('G6 the boundary cancelled speech synthesis', synth.cancels > cancelsBefore);
ok('G6 the speaking class was cleared', play().speaking === false && speakBtn === null);
eq('G6 nothing new was spoken', synth.spoken.length, 1);

// =========================================================================
// H. ENTER-WHEN-DONE - the keyboard's Next takes the same boundary
// =========================================================================
function typedEnter() { MIXED.keydown({ key: 'Enter', preventDefault: function () {} }); }
reset({ at: 1 });                                            // question 1 is the typed format
eq('H1 the current question is the typed format', q().fmt, 'type');
el('rInput').value = 'mąka';
activate('rCheck');
eq('H1 the answer settled the question', R.state, 'done');
var hBtn = feedbackAudioBtn('rVerdict');
ok('H1 the verdict panel carries a Polish audio button', hBtn !== null);
var hClip = pressFeedbackAudio(hBtn);
ok('H2 the verdict audio is playing through the shared slot', hClip && currentAudio === hClip);
var hAtRender = null;
MIXED.spyRender(function () { hAtRender = { audio: currentAudio, pauses: hClip.pauses, btn: speakBtn }; });
var hBefore = R.i;
typedEnter();
eq('H2 Enter advanced the round', R.i, hBefore + 1);
eq('H2 the clip was paused exactly once', hClip.pauses, 1);
ok('H2 currentAudio and speakBtn were cleared', currentAudio === null && speakBtn === null);
ok('H2 cleanup happened before the next question rendered', hAtRender !== null && hAtRender.audio === null && hAtRender.pauses === 1);
ok('H2 the feedback button is no longer marked speaking', hBtn.speaking === false);
// Enter while the question is still open is the CHECK key, not the Next key
reset({ at: 1 });
var hI = R.i;
el('rInput').value = '';                                     // an empty answer must not settle anything
typedEnter();
eq('H3 Enter while asking did not advance', R.i, hI);
eq('H3 Enter while asking ran the check, not the boundary', R.state, 'ask');
eq('H3 the empty-answer instruction was announced', el('rStatus').textContent, 'Type the Polish answer first.');
el('rInput').value = 'mąka';
typedEnter();
eq('H4 Enter with a real answer checks it', R.state, 'done');
eq('H4 Enter with a real answer still did not advance', R.i, hI);
typedEnter();
eq('H4 the next Enter advances', R.i, hI + 1);

// =========================================================================
// I. BACK BOUNDARIES - Home appears only after the audio is released
// =========================================================================
['rBack', 'rBackBtn'].forEach(function (id) {
  // an MP3 in progress
  reset({ at: 0 });
  var clip = pressPlay();
  ok('I1 ' + id + ': a clip is playing', clip && currentAudio === clip);
  activate(id);
  eq('I1 ' + id + ': the clip was paused exactly once', clip.pauses, 1);
  ok('I1 ' + id + ': currentAudio was cleared', currentAudio === null);
  ok('I1 ' + id + ': speakBtn was cleared', speakBtn === null);
  ok('I1 ' + id + ': the speaking class was cleared', play().speaking === false);
  eq('I2 ' + id + ': it navigated home', shown.map(function (s) { return s.scr; }), ['home']);
  ok('I2 ' + id + ': the audio was already released when Home was shown',
     shown[0].audio === null && shown[0].pauses === 1 && shown[0].btn === null && shown[0].speaking === false);
  eq('I2 ' + id + ': no new sound started', FakeAudio.created.length, 1);
  eq('I2 ' + id + ': nothing was spoken', synth.spoken.length, 0);
  // late signals from the abandoned clip stay stale
  clip.rejectPlay('AbortError'); clip.fireError(); clip.fireEnded();
  eq('I3 ' + id + ': late signals speak nothing after leaving', synth.spoken.length, 0);
  eq('I3 ' + id + ': late signals create no clip after leaving', FakeAudio.created.length, 1);

  // a speech-synthesis fallback in progress
  reset({ status: 'loading', at: 0 });
  settleAudioManifest(null);
  pressPlay();
  eq('I4 ' + id + ': the device voice is speaking', synth.spoken.length, 1);
  var before = synth.cancels;
  activate(id);
  ok('I4 ' + id + ': speech synthesis was cancelled', synth.cancels > before);
  ok('I4 ' + id + ': the speaking class was cleared', play().speaking === false && speakBtn === null);
  ok('I5 ' + id + ': Home was shown only after the cancel',
     shown.length === 1 && shown[0].scr === 'home' && shown[0].cancels > before && shown[0].btn === null);
  eq('I5 ' + id + ': nothing new was spoken', synth.spoken.length, 1);
});

// =========================================================================
// J. NEW ROUND - startRound owns the boundary, and owns it once
// =========================================================================
reset({ at: 0 });
var jClip = pressPlay();
ok('J1 a clip is playing before the new round', jClip && currentAudio === jClip);
var jAtRender = null;
MIXED.spyRender(function () { if (jAtRender === null) jAtRender = { audio: currentAudio, pauses: jClip.pauses, btn: speakBtn, qs: R.qs }; });
var jOldQs = R.qs;
activate('rAgain');
eq('J1 the clip was paused exactly once - one boundary, not two', jClip.pauses, 1);
ok('J1 currentAudio and speakBtn were cleared', currentAudio === null && speakBtn === null);
ok('J1 the speaking class was cleared', play().speaking === false);
ok('J2 cleanup happened before the new round rendered',
   jAtRender !== null && jAtRender.audio === null && jAtRender.pauses === 1 && jAtRender.btn === null);
ok('J2 the round really was replaced', R.qs !== jOldQs);
eq('J2 the new round starts at question 0', R.i, 0);
eq('J3 the new round started silently - no clip', FakeAudio.created.length, 1);
eq('J3 the new round started silently - no utterance', synth.spoken.length, 0);
// entering a round from the topic tile takes the same boundary
reset({ at: 0 });
var jClip2 = pressPlay();
MIXED.startRound(0, 0);
eq('J4 entering a round from scratch stops what was playing', jClip2.pauses, 1);
ok('J4 nothing is playing in the fresh round', currentAudio === null && speakBtn === null);
eq('J4 the fresh round started nothing of its own', FakeAudio.created.length, 1);
// a fallback utterance is cancelled by the same boundary
reset({ status: 'loading', at: 0 });
settleAudioManifest(null);
pressPlay();
var jCancels = synth.cancels;
activate('rAgain');
ok('J5 a new round cancels a device-voice fallback', synth.cancels > jCancels);
eq('J5 the new round spoke nothing', synth.spoken.length, 1);

// =========================================================================
// K. FINAL ADVANCE - nothing survives onto the results screen
// =========================================================================
reset();
R.qs = [R.qs[0]];                                            // one listen question: Next goes to results
R.i = 0; MIXED.rRender();
var kClip = pressPlay();
ok('K1 a clip is playing on the last question', kClip && currentAudio === kClip);
activate('rNext');
ok('K1 the results screen is showing', el('rDone').style.display === 'flex');
eq('K1 the clip was paused before completion rendered', kClip.pauses, 1);
ok('K1 no audio survives on the results screen', currentAudio === null && speakBtn === null);
ok('K1 the speaking class was cleared', play().speaking === false);
eq('K2 completion focus still lands on the results heading', ACTIVE, el('rDoneTitle'));
ok('K2 the hidden Play button is disabled there', play().disabled === true);
eq('K2 the hidden Play button does not claim to be loading', play().getAttribute('aria-busy'), 'false');
eq('K3 completion started no audio of its own', FakeAudio.created.length, 1);
eq('K3 completion spoke nothing', synth.spoken.length, 0);
kClip.rejectPlay('AbortError'); kClip.fireError(); kClip.fireEnded();
eq('K3 late signals on the results screen speak nothing', synth.spoken.length, 0);
ok('K3 late signals do not steal completion focus', ACTIVE === el('rDoneTitle'));

// =========================================================================
// L. FEEDBACK AUDIO - the boundary is shared-audio cleanup, not rPlay cleanup
// =========================================================================
// The answer feedback panel carries its own audio, on a question whose Play button
// was never touched - so a boundary that only stopped "what rPlay started" would
// leave this running. Driven through the SHIPPING delegated [data-say] listener.
reset({ at: 0 });                                            // listen question, card carries an example
answerRight();
var lBtn = feedbackAudioBtn('rFb');
ok('L1 the feedback panel built a mini-audio button', lBtn !== null);
eq('L1 it carries the example sentence', decodeURIComponent(lBtn.getAttribute('data-say')), 'Poproszę kawę.');
var lClip = pressFeedbackAudio(lBtn);
eq('L1 the example clip is playing', lastSrc(), CLIPS['Poproszę kawę.']);
ok('L1 it occupies the shared slot', currentAudio === lClip && speakBtn === lBtn);
ok('L1 the feedback button is the one marked speaking', lBtn.speaking === true && play().speaking === false);
activate('rNext');
eq('L2 Next stopped the feedback audio', lClip.pauses, 1);
ok('L2 the shared slot was cleared', currentAudio === null && speakBtn === null);
ok('L2 the feedback button is no longer speaking', lBtn.speaking === false);
eq('L2 the next question started nothing', FakeAudio.created.length, 1);
// the same for leaving the screen entirely
reset({ at: 0 });
answerRight();
var lBtn2 = feedbackAudioBtn('rFb');
var lClip2 = pressFeedbackAudio(lBtn2);
activate('rBack');
eq('L3 Back stopped the feedback audio', lClip2.pauses, 1);
ok('L3 Home was shown only after cleanup',
   shown.length === 1 && shown[0].scr === 'home' && shown[0].audio === null && shown[0].btn === null);
// and for a typed question's canonical-answer button, which no listen question owns
reset({ at: 1 });
el('rInput').value = 'mąka';
activate('rCheck');
var lBtn3 = feedbackAudioBtn('rVerdict');
ok('L4 the typed verdict carries a Polish audio button', lBtn3 !== null);
var lClip3 = pressFeedbackAudio(lBtn3);
ok('L4 it plays through the shared slot', lClip3 && currentAudio === lClip3);
activate('rAgain');
eq('L4 a new round stops the verdict audio', lClip3.pauses, 1);
ok('L4 the shared slot was cleared', currentAudio === null && speakBtn === null);

// =========================================================================
// M. LOADING FOCUS - a new question never starts on <body>
// =========================================================================
reset({ status: 'loading', at: 0 });
ok('M1 Play is closed while loading', play().disabled === true);
ok('M1 focus did not land on the disabled Play button', ACTIVE !== play());
ok('M1 focus did not fall back to body', ACTIVE !== BODY);
eq('M1 focus landed on the stable question prompt', ACTIVE, el('rType'));
eq('M1 the prompt says what the question is', el('rType').textContent, 'What did you hear?');
// settlement must not yank focus away from wherever the learner is
var mAnchor = ACTIVE, mAnchorFocuses = el('rType').focusCount;
settleAudioManifest(manifestEntries());
ok('M2 settlement enabled Play', play().disabled === false);
ok('M2 settlement did not steal focus from the prompt', ACTIVE === mAnchor);
eq('M2 the prompt was not re-focused either', el('rType').focusCount, mAnchorFocuses);
eq('M2 Play was never focused by settlement', play().focusCount, 0);
eq('M2 settlement autoplayed nothing', FakeAudio.created.length + synth.spoken.length, 0);
// the learner moves to Play themselves and it works
play().focus();
pressPlay();
eq('M3 the learner can then play the clip', lastSrc(), CLIPS['kawa']);
// a settled listen question focuses Play directly
reset({ at: 0 });
ok('M4 a settled listen question focuses Play', ACTIVE === play());
ok('M4 Play is pressable there', play().disabled === false);
eq('M4 the prompt was not used as the anchor', el('rType').focusCount, 0);
// the other two formats are unchanged
reset({ at: 1 });
ok('M5 a typed question still focuses the input', ACTIVE === el('rInput'));
reset({ at: 2 });
ok('M5 a multiple-choice question still focuses the Polish prompt', ACTIVE === el('rPl'));
// and settlement does not steal focus from either of them, nor from an option or Next
reset({ status: 'loading', at: 1 });
var mInput = ACTIVE;
settleAudioManifest(manifestEntries());
ok('M6 settlement leaves typed focus alone', ACTIVE === mInput && ACTIVE === el('rInput'));
reset({ status: 'loading', at: 2 });
var mPl = ACTIVE;
settleAudioManifest(manifestEntries());
ok('M6 settlement leaves mc focus alone', ACTIVE === mPl && ACTIVE === el('rPl'));
reset({ status: 'loading', at: 2 });
answerRight();
var mNext = ACTIVE;
eq('M7 a correct answer focuses Next', ACTIVE, el('rNext'));
settleAudioManifest(manifestEntries());
ok('M7 settlement leaves Next focused', ACTIVE === mNext);
eq('M7 settlement announced nothing over the result', el('rStatus').textContent.indexOf('Correct.'), 0);

// =========================================================================
// N. WIRING - the boundary belongs to the helper, and to only one helper
// =========================================================================
// Audio must be stopped BEFORE anything the learner can observe changes.
var R_EFFECTS = ['show(', 'rRender(', 'R.i', 'R.li', 'R.ti', 'R.qs', 'R.state', 'R.revealed', 'R.attempted'];
function stopsAudioFirst(body) {
  var stop = body.indexOf('stopAllAudio');
  if (stop === -1) return false;
  for (var i = 0; i < R_EFFECTS.length; i++) {
    var e = body.indexOf(R_EFFECTS[i]);
    if (e !== -1 && e < stop) return false;
  }
  return true;
}
var SRC_ADVANCE = stripComments(RSRC.rAdvance);
var SRC_EXIT = stripComments(RSRC.rExit);
var SRC_START = stripComments(RSRC.startRound);
var SRC_READY = stripComments(RSRC.syncRoundAudioReadiness);
var SRC_PLAYCUR = stripComments(RSRC.rPlayCurrent);
var SRC_RENDER = stripComments(RSRC.rRender);
var SRC_SETTLE = stripComments(SRC.settleAudioManifest);

ok('N1 rAdvance stops audio before the index moves or anything renders', stopsAudioFirst(SRC_ADVANCE));
ok('N1 rExit stops audio before Home is shown', stopsAudioFirst(SRC_EXIT));
ok('N1 startRound stops audio before the round is rebuilt or shown', stopsAudioFirst(SRC_START));
ok('N2 rNext routes through rAdvance', /^rAdvance$/.test(stripComments(handlerExpr('rNext')).trim()));
ok('N2 rBack routes through rExit', /^rExit$/.test(stripComments(handlerExpr('rBack')).trim()));
ok('N2 rBackBtn routes through rExit', /^rExit$/.test(stripComments(handlerExpr('rBackBtn')).trim()));
ok('N2 rPlay routes through rPlayCurrent', /^rPlayCurrent$/.test(stripComments(handlerExpr('rPlay')).trim()));
ok('N3 Enter-when-done routes through rAdvance', /rAdvance\s*\(\s*\)/.test(stripComments(handlerExpr('rInput', 'keydown'))));
ok('N3 Enter-when-asking still checks the answer', /rCheckAnswer\s*\(\s*\)/.test(stripComments(handlerExpr('rInput', 'keydown'))));
ok('N3 the three boundary statements are not duplicated in the keydown handler',
   stripComments(handlerExpr('rInput', 'keydown')).indexOf('stopAllAudio') === -1);
ok('N3 nor in the Next handler', stripComments(handlerExpr('rNext')).indexOf('stopAllAudio') === -1);
ok('N4 rAgain routes through startRound', /startRound\s*\(/.test(stripComments(handlerExpr('rAgain'))));
ok('N4 rAgain does not duplicate the stop startRound already owns',
   stripComments(handlerExpr('rAgain')).indexOf('stopAllAudio') === -1);
ok('N5 rRender calls the readiness helper', /syncRoundAudioReadiness\s*\(\s*\)/.test(SRC_RENDER));
ok('N5 settleAudioManifest calls the Mixed Quiz readiness helper', /syncRoundAudioReadiness\s*\(\s*\)/.test(SRC_SETTLE));
ok('N5 settleAudioManifest still calls the Listening one', /syncListeningAudioReadiness\s*\(\s*\)/.test(SRC_SETTLE));
ok('N6 rPlayCurrent guards the loading state', /audioManifestStatus\s*===\s*"loading"/.test(SRC_PLAYCUR));
ok('N6 rPlayCurrent guards the listen format', /fmt\s*!==\s*"listen"/.test(SRC_PLAYCUR));
ok('N6 rPlayCurrent guards a current question', /R\.i\s*>=\s*R\.qs\.length/.test(SRC_PLAYCUR));
ok('N6 every guard runs before any playback call', (function () {
  var play = SRC_PLAYCUR.indexOf('speakCardMain');
  return play !== -1 &&
         SRC_PLAYCUR.indexOf('audioManifestStatus') < play &&
         SRC_PLAYCUR.indexOf('fmt') < play &&
         SRC_PLAYCUR.indexOf('R.qs.length') < play;
})());
// The two state-only functions must stay state-only.
[['syncRoundAudioReadiness', SRC_READY], ['settleAudioManifest', SRC_SETTLE]].forEach(function (pair) {
  var n = pair[0], s = pair[1];
  ok('N7 ' + n + ' starts no playback', s.indexOf('speakCardMain') === -1 && s.indexOf('speakText') === -1 &&
     s.indexOf('speakFallback') === -1 && s.indexOf('new Audio') === -1);
  ok('N7 ' + n + ' uses no timer', s.indexOf('setTimeout') === -1 && s.indexOf('setInterval') === -1);
  ok('N7 ' + n + ' moves no focus', s.indexOf('.focus(') === -1);
  ok('N7 ' + n + ' queues nothing', s.indexOf('pending') === -1 && s.indexOf('queue') === -1);
  ok('N7 ' + n + ' calls no render function', s.indexOf('rRender(') === -1 && s.indexOf('lRender(') === -1 &&
     s.indexOf('rShowDone(') === -1);
  ok('N7 ' + n + ' does not retry the manifest', s.indexOf('fetch(') === -1);
});
ok('N8 the readiness helper changes no round state',
   SRC_READY.indexOf('R.i =') === -1 && SRC_READY.indexOf('R.i=') === -1 &&
   SRC_READY.indexOf('R.qs =') === -1 && SRC_READY.indexOf('R.state') === -1);
ok('N8 the readiness helper only touches the Play button\'s state',
   /btn\.disabled/.test(SRC_READY) && /aria-busy/.test(SRC_READY) && /aria-label/.test(SRC_READY));
ok('N8 settlement still changes no round state',
   SRC_SETTLE.indexOf('R.i') === -1 && SRC_SETTLE.indexOf('L.i') === -1);
// the manifest is still fetched exactly once, with no retry anywhere
var fetchCount = (INDEX.match(/fetch\(\s*"audio-manifest\.json"/g) || []).length;
eq('N9 audio-manifest.json is requested from exactly one place', fetchCount, 1);
ok('N9 the shared status model is unchanged',
   /"loading"\s*\|\s*"ready"\s*\|\s*"unavailable"/.test(INDEX));
// the markup ships closed, so nothing is pressable before the first sync
var rPlayTag = (INDEX.match(/<button[^>]*id="rPlay"[^>]*>/) || [''])[0];
ok('N10 the rPlay markup starts disabled', /\sdisabled/.test(rPlayTag));
ok('N10 the rPlay markup starts busy', /aria-busy="true"/.test(rPlayTag));
ok('N10 the rPlay markup starts with the loading name', /aria-label="Polish audio is loading"/.test(rPlayTag));
ok('N10 the loading focus anchor is script-focusable but not a tab stop',
   /<div[^>]*id="rType"[^>]*tabindex="-1"/.test(INDEX));
ok('N10 the anchor has no control-style focus ring', /#rType:focus/.test(INDEX));
ok('N10 no real Mixed Quiz control had its focus ring suppressed',
   INDEX.indexOf('#rPlay:focus{outline:none}') === -1 && INDEX.indexOf('#rNext:focus{outline:none}') === -1 &&
   INDEX.indexOf('#rInput:focus{outline:none}') === -1);

INFO.push('assertions run against the shipping Mixed Quiz code in index.html');
INFO.push('fake DOM models: focus() on a disabled or hidden element is a no-op; disabling the focused element hands focus to <body>');
INFO.push('the shared audio engine, the fallback latch and the manifest-parsing matrix stay owned by tests/test_audio_fallback.js');

// ---------- report ----------
console.log('Mixed Quiz audio tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
LOG.forEach(function (l) { console.log('  ' + l); });
INFO.forEach(function (l) { console.log('  [info] ' + l); });
if (FAIL > 0) { throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed'); }
