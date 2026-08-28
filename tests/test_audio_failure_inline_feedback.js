// Deterministic regression tests for the post-release inline audio-failure fix.
//
//   osascript -l JavaScript tests/test_audio_failure_inline_feedback.js
//
// The shipping functions are extracted from index.html and executed against a
// small fake DOM and hand-controlled Audio objects. No network or browser timing
// participates in the failure, retry, navigation, or stale-callback assertions.
ObjC.import('Foundation');

function readFile(path) {
  var s = $.NSString.stringWithContentsOfFileEncodingError(path, $.NSUTF8StringEncoding, null);
  return ObjC.unwrap(s);
}
function rootDir() {
  var fm = $.NSFileManager.defaultManager, cwd = ObjC.unwrap(fm.currentDirectoryPath);
  return fm.fileExistsAtPath(cwd + '/index.html') ? cwd + '/' : cwd + '/../';
}
var ROOT = rootDir();
var INDEX = readFile(ROOT + 'index.html');
var PASS = 0, FAIL = 0, LOG = [];
function ok(name, condition) { if (condition) PASS++; else { FAIL++; LOG.push('FAIL: ' + name); } }
function eq(name, actual, expected) {
  var a = JSON.stringify(actual), e = JSON.stringify(expected);
  ok(name + (a === e ? '' : ' (got ' + a + ', want ' + e + ')'), a === e);
}
function countOf(source, needle) {
  var count = 0, at = source.indexOf(needle);
  while (at !== -1) { count++; at = source.indexOf(needle, at + needle.length); }
  return count;
}
function extractFunction(src, name) {
  var needle = 'function ' + name + '(', start = src.indexOf(needle);
  if (start === -1) throw new Error('function not found: ' + name);
  if (src.indexOf(needle, start + 1) !== -1) throw new Error('duplicate function: ' + name);
  var open = src.indexOf('{', src.indexOf(')', start)), depth = 0, mode = 'code';
  for (var i = open; i < src.length; i++) {
    var c = src[i], n = src[i + 1];
    if (mode === 'line') { if (c === '\n') mode = 'code'; continue; }
    if (mode === 'block') { if (c === '*' && n === '/') { mode = 'code'; i++; } continue; }
    if (mode === 'sq' || mode === 'dq' || mode === 'tpl') {
      if (c === '\\') { i++; continue; }
      if ((mode === 'sq' && c === "'") || (mode === 'dq' && c === '"') ||
          (mode === 'tpl' && c === '`')) mode = 'code';
      continue;
    }
    if (c === '/' && n === '/') { mode = 'line'; i++; continue; }
    if (c === '/' && n === '*') { mode = 'block'; i++; continue; }
    if (c === "'") { mode = 'sq'; continue; }
    if (c === '"') { mode = 'dq'; continue; }
    if (c === '`') { mode = 'tpl'; continue; }
    if (c === '{') depth++;
    else if (c === '}') { depth--; if (depth === 0) return src.slice(start, i + 1); }
  }
  throw new Error('unbalanced function: ' + name);
}
function constString(name) {
  var m = INDEX.match(new RegExp('const\\s+' + name + '\\s*=\\s*"([^"]*)"\\s*;'));
  if (!m) throw new Error('constant not found: ' + name);
  return m[1];
}

function El(tag) {
  this.tagName = String(tag || 'div').toUpperCase();
  this.id = ''; this.className = ''; this.type = ''; this.textContent = '';
  this.hidden = false; this.disabled = false; this.tabIndex = 0;
  this.attrs = {}; this.children = []; this.parentNode = null; this.listeners = {};
  this.focusCount = 0; this.classes = [];
  var self = this;
  this.classList = {
    add: function (c) { if (self.classes.indexOf(c) === -1) self.classes.push(c); },
    remove: function (c) { self.classes = self.classes.filter(function (x) { return x !== c; }); },
    contains: function (c) { return self.classes.indexOf(c) !== -1; }
  };
}
El.prototype.setAttribute = function (k, v) { this.attrs[k] = String(v); if (k === 'id') this.id = String(v); };
El.prototype.getAttribute = function (k) { return this.attrs[k] === undefined ? null : this.attrs[k]; };
El.prototype.removeAttribute = function (k) { delete this.attrs[k]; };
El.prototype.appendChild = function (child) {
  if (child.parentNode) child.parentNode.removeChild(child);
  child.parentNode = this; this.children.push(child); return child;
};
El.prototype.removeChild = function (child) {
  this.children = this.children.filter(function (x) { return x !== child; });
  child.parentNode = null; return child;
};
El.prototype.insertAdjacentElement = function (position, el) {
  if (position !== 'afterend' || !this.parentNode) throw new Error('unsupported insertion');
  if (el.parentNode) el.parentNode.removeChild(el);
  var at = this.parentNode.children.indexOf(this);
  this.parentNode.children.splice(at + 1, 0, el); el.parentNode = this.parentNode; return el;
};
El.prototype.matches = function (selector) {
  if (selector[0] === '#') return this.id === selector.slice(1);
  if (selector[0] === '.') return (' ' + this.className + ' ').indexOf(' ' + selector.slice(1) + ' ') !== -1;
  return false;
};
El.prototype.closest = function (selector) {
  var node = this;
  while (node) { if (node.matches && node.matches(selector)) return node; node = node.parentNode; }
  return null;
};
El.prototype.addEventListener = function (type, fn) { (this.listeners[type] = this.listeners[type] || []).push(fn); };
El.prototype.focus = function () { this.focusCount++; if (this.ownerDoc) this.ownerDoc.activeElement = this; };
El.prototype.click = function () {
  var self = this;
  if (this.hidden || this.disabled) return;
  (this.listeners.click || []).forEach(function (fn) {
    fn({ target: self, stopPropagation: function () {}, preventDefault: function () {} });
  });
};
function makeDocument() {
  var body = new El('body');
  var doc = {
    body: body, activeElement: null, created: [],
    createElement: function (tag) { var el = new El(tag); el.ownerDoc = doc; doc.created.push(el); return el; }
  };
  body.ownerDoc = doc; return doc;
}
function el(doc, tag, id, cls, parent) {
  var node = doc.createElement(tag);
  if (id) { node.id = id; node.attrs.id = id; }
  if (cls) node.className = cls;
  if (parent) parent.appendChild(node);
  return node;
}

function Thenable() { this.rejected = null; }
Thenable.prototype['catch'] = function (fn) { this.rejected = fn; return this; };
Thenable.prototype.reject = function () { if (this.rejected) this.rejected({ name: 'NotSupportedError' }); };
function FakeAudio(src) {
  this.src = src; this.onended = null; this.onerror = null; this.pauses = 0;
  this.playCount = 0; this.promise = null; FakeAudio.created.push(this);
}
FakeAudio.created = [];
FakeAudio.prototype.play = function () { this.playCount++; this.promise = new Thenable(); return this.promise; };
FakeAudio.prototype.pause = function () { this.pauses++; };
FakeAudio.prototype.fireError = function () { if (this.onerror) this.onerror({ type: 'error' }); };
FakeAudio.prototype.fireEnded = function () { if (this.onended) this.onended({ type: 'ended' }); };
FakeAudio.prototype.rejectPlay = function () { if (this.promise) this.promise.reject(); };
function FakeSynth() { this.cancels = 0; }
FakeSynth.prototype.cancel = function () { this.cancels++; };

var AUDIO_FALLBACK_MSG = constString('AUDIO_FALLBACK_MSG');
var AUDIO_FAILED_MSG = constString('AUDIO_FAILED_MSG');
var AUDIO_RETRY_MSG = constString('AUDIO_RETRY_MSG');
var SPEEDS = { normal: 1, slow: 0.7 }, currentSpeed = 'normal';
var document, window, speechSynthesis, SpeechSynthesisUtterance, Audio = FakeAudio;
var currentAudio, currentUtterance, speakBtn, audioRetryRequest;
var audioStatusEl, audioStatusMsgEl, audioRetryEl, audioStatusOwner;
var audioMap, plVoice = null, showDoneCalls = 0, S = { pos: 0, queue: [] };
function currentRate() { return SPEEDS[currentSpeed]; }
function voiceHint() {}
function showDone() { showDoneCalls++; }

['ppNormalize', 'clearSpeaking', 'ppAudioStatusHost', 'showAudioStatus', 'clearAudioStatus',
 'retryAudio', 'stopAllAudio', 'speakText', 'playPreGenerated', 'speakFallback', 'render']
  .forEach(function (name) { (0, eval)(extractFunction(INDEX, name)); });

var body, cardView, stage, scene, flip, face, flashBtn, controls;
var patternExample, patternRow, patternBtn, otherBtn;
function reset(options) {
  options = options || {};
  document = makeDocument(); body = document.body;
  cardView = el(document, 'div', 'cardView', '', body);
  stage = el(document, 'div', '', 'stage', cardView);
  scene = el(document, 'div', '', 'scene', stage);
  flip = el(document, 'div', 'flip', 'flip', scene);
  face = el(document, 'div', '', 'face', flip);
  flashBtn = el(document, 'button', 'speak', 'fab', face);
  controls = el(document, 'div', '', 'controls', cardView);
  patternExample = el(document, 'div', '', 'vp-example', body);
  patternRow = el(document, 'div', '', 'vp-example-pl-row', patternExample);
  patternBtn = el(document, 'button', '', 'mini-audio vp-example-audio', patternRow);
  otherBtn = el(document, 'button', '', 'mini-audio', body);
  FakeAudio.created = [];
  speechSynthesis = new FakeSynth(); window = {};
  if (!options.noSpeech) window.speechSynthesis = speechSynthesis;
  SpeechSynthesisUtterance = undefined;
  currentAudio = null; currentUtterance = null; speakBtn = null; audioRetryRequest = null;
  audioStatusEl = null; audioStatusMsgEl = null; audioRetryEl = null; audioStatusOwner = null;
  audioMap = { A: 'audio/a.mp3', B: 'audio/b.mp3' };
  showDoneCalls = 0; S = { pos: 0, queue: [] };
  ppAudioStatusHost();
}
function lastAudio() { return FakeAudio.created[FakeAudio.created.length - 1]; }
function statusCount() { return document.created.filter(function (node) { return node.id === 'ppAudioStatus'; }).length; }
function statusIndex(parent) { return parent.children.indexOf(audioStatusEl); }

// A. Flashcard placement: outside both transformed faces, in the established
// cardView column between learning content and navigation.
reset({ noSpeech: true });
var focusBefore = document.activeElement;
showAudioStatus('failed', flashBtn);
eq('A1 failure wording and Retry are present',
   [audioStatusMsgEl.textContent, audioRetryEl.textContent], [AUDIO_FAILED_MSG, 'Try again']);
eq('A2 flashcard status is a cardView child after the stage',
   [audioStatusEl.parentNode === cardView, statusIndex(cardView), cardView.children.indexOf(stage)], [true, 1, 0]);
eq('A3 flashcard status is before navigation controls', cardView.children[statusIndex(cardView) + 1] === controls, true);
eq('A4 flashcard status is outside the transformed flip and both faces',
   [audioStatusEl.closest('#flip'), audioStatusEl.closest('.face')], [null, null]);
eq('A5 failure does not steal focus', document.activeElement, focusBefore);
eq('A6 failed control is described by the status message', flashBtn.getAttribute('aria-describedby'), 'ppAudioStatusMsg');
eq('A7 live region remains polite and atomic',
   [audioStatusEl.getAttribute('role'), audioStatusEl.getAttribute('aria-live'), audioStatusEl.getAttribute('aria-atomic')],
   ['status', 'polite', 'true']);
eq('A8 Retry is a reachable native named button',
   [audioRetryEl.tagName, audioRetryEl.type, audioRetryEl.hidden, audioRetryEl.disabled, audioRetryEl.tabIndex],
   ['BUTTON', 'button', false, false, 0]);

// B. The shared non-flashcard path remains shared: Verb Patterns does not gain a
// separate status implementation or player.
clearAudioStatus();
showAudioStatus('failed', patternBtn);
eq('B1 Verb Patterns uses the same status node', statusCount(), 1);
eq('B2 Verb Patterns status remains adjacent to its pronunciation action',
   patternRow.children[patternRow.children.indexOf(patternBtn) + 1] === audioStatusEl, true);
eq('B3 ownership moves cleanly between controls',
   [flashBtn.getAttribute('aria-describedby'), patternBtn.getAttribute('aria-describedby')],
   [null, 'ppAudioStatusMsg']);
clearAudioStatus();
eq('B4 cleanup releases only the current owner and hides Retry',
   [patternBtn.getAttribute('aria-describedby'), audioStatusEl.hidden, audioRetryEl.hidden, audioRetryEl.tabIndex],
   [null, true, true, -1]);

// C. One logical failure survives repeated terminal signals/retries; recovery
// clears it, and Retry uses the exact failed phrase/control through speakText.
reset({ noSpeech: true });
speakText('A', flashBtn); lastAudio().fireError();
eq('C1 first terminal failure exposes one panel', [statusCount(), audioStatusEl.children.length], [1, 2]);
lastAudio().rejectPlay();
eq('C2 the duplicate failure channel appends no panel', [statusCount(), audioStatusEl.children.length], [1, 2]);
audioRetryEl.click();
eq('C3 Retry returns focus and starts one fresh correct clip',
   [flashBtn.focusCount, document.activeElement === flashBtn, FakeAudio.created.length, lastAudio().src],
   [1, true, 2, 'audio/a.mp3']);
lastAudio().fireError();
eq('C4 repeated Retry failure retains one logical panel',
   [statusCount(), audioStatusEl.children.length, audioStatusMsgEl.textContent], [1, 2, AUDIO_FAILED_MSG]);
audioRetryEl.click(); lastAudio().fireEnded();
eq('C5 successful Retry leaves the UI in its normal state',
   [audioStatusEl.hidden, audioStatusMsgEl.textContent, audioRetryEl.hidden], [true, '', true]);

// D. Critical stale-navigation ordering. render() is the actual flashcard
// boundary; the completion branch keeps its dependency surface intentionally
// small while still executing the shipping cleanup call.
reset({ noSpeech: true });
speakText('A', flashBtn); var staleA = lastAudio();
render();
eq('D1 flashcard render stops A and clears its retry/status',
   [staleA.pauses, currentAudio, audioRetryRequest, audioStatusEl.hidden, showDoneCalls],
   [1, null, null, true, 1]);
speakText('B', otherBtn); var liveB = lastAudio();
staleA.fireError(); staleA.rejectPlay();
eq('D2 delayed A failure cannot announce into B',
   [currentAudio === liveB, audioStatusEl.hidden, audioStatusMsgEl.textContent], [true, true, '']);
liveB.fireError();
eq('D3 B alone may own the current failure',
   [audioStatusEl.hidden, audioStatusMsgEl.textContent, audioStatusOwner === otherBtn],
   [false, AUDIO_FAILED_MSG, true]);

// E. Static call-path and layout contracts cover every flashcard content switch
// without recreating the whole application renderer in the fake DOM.
var renderSrc = extractFunction(INDEX, 'render');
var advanceSrc = extractFunction(INDEX, 'advance');
var prevSrc = extractFunction(INDEX, 'goPrev');
var shuffleSrc = extractFunction(INDEX, 'shuffle');
var startSrc = extractFunction(INDEX, 'startTopic');
var showScreenSrc = extractFunction(INDEX, 'showScreen');
ok('E1 render cleans audio before its completion/content branch',
   renderSrc.indexOf('stopAllAudio();') !== -1 && renderSrc.indexOf('stopAllAudio();') < renderSrc.indexOf('if(S.pos >= S.queue.length)'));
ok('E2 Next and Previous both route through the cleanup render',
   advanceSrc.indexOf('render();') !== -1 && prevSrc.indexOf('render();') !== -1);
ok('E3 Shuffle and topic changes route through the cleanup render',
   shuffleSrc.indexOf('render();') !== -1 && startSrc.indexOf('render();') !== -1);
ok('E4 direction changes retain the same cleanup render call',
   INDEX.indexOf('cardDir = (cardDir === "en") ? "pl" : "en";') !== -1 &&
   INDEX.indexOf('render();                                     /* re-renders front-side up in the new direction */') !== -1);
ok('E5 screen/topic changes use the shared cleanup boundary',
   showScreenSrc.indexOf('fromScreen!==toScreen && typeof stopAllAudio==="function"') !== -1 &&
   showScreenSrc.indexOf('stopAllAudio();') !== -1);

var css = INDEX;
var statusRule = (css.match(/\.audio-status\{([^}]*)\}/) || ['', ''])[1];
ok('E6 status participates in normal flow',
   statusRule.indexOf('position:absolute') === -1 && statusRule.indexOf('position:fixed') === -1 &&
   statusRule.indexOf('display:flex') !== -1);
ok('E7 no responsive rule restores overlay positioning',
   !/@media[\s\S]*?\.audio-status\s*\{[^}]*(position\s*:\s*(absolute|fixed))/i.test(css));
eq('E8 one app-shell failure implementation remains',
   [countOf(INDEX, 'function showAudioStatus('), countOf(INDEX, 'function retryAudio('), countOf(INDEX, 'Audio couldn\'t play.')],
   [1, 1, 1]);
ok('E9 Listening still delegates to the shared card/audio path',
   extractFunction(INDEX, 'lPlayCurrent').indexOf('speakCardMain(L.qs[L.i].c, $("lPlay"))') !== -1);

LOG.forEach(function (line) { console.log(line); });
console.log(PASS + '/' + (PASS + FAIL) + ' audio failure inline-feedback tests passed');
if (FAIL) throw new Error(FAIL + ' audio failure inline-feedback test(s) failed');
