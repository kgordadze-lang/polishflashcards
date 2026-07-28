// Deterministic tests for the offline audio fallback path in index.html.
// Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_audio_fallback.js
// Exit status is 0 only if every assertion passes (printed at the end).
//
// WHAT THIS PINS DOWN
// A pre-generated clip that cannot be fetched signals its failure through TWO
// channels for ONE playback attempt: the element fires `error` AND the promise
// returned by play() rejects. speechSynthesis.speak() QUEUES rather than
// replaces, so a fallback fired from each channel spoke the phrase twice - the
// duplicate offline playback this file exists to prevent. One attempt must
// produce exactly one fallback, whichever channels fire and in whichever order.
//
// HOW IT AVOIDS A REAL NETWORK
// Nothing here goes near the network or a real <audio> element. The Audio
// object, speechSynthesis and the buttons are fakes the test drives directly,
// so every ordering is reproduced on demand rather than waited for.
//
// The fake play() returns a hand-rolled thenable that is settled SYNCHRONOUSLY
// by the test, not a real Promise: osascript has no run loop draining the
// microtask queue, so a real Promise rejection would never be delivered inside
// a script that exits at the end of its first job. The thenable also lets the
// test choose the exact interleaving of the two channels, which is the whole
// point. The code under test only ever calls .catch() on the result, and its
// latch is a plain closure variable, so sync vs async delivery is immaterial to
// what is being verified.
//
// The functions under test are read OUT OF index.html rather than copied here,
// so the audio path the app ships is literally the audio path under test.
//
// SECTIONS 10-18: THE LISTENING AUDIO LIFECYCLE
// A Listening clip is routinely still running when the learner moves on - they
// answer as soon as they recognise the word, well before the clip ends. Neither
// show() nor lRender() touches audio, so every way OUT of a question has to
// silence it: Next, Back, Home, and starting another round. Those sections drive
// the real Listening screen code (also read out of index.html) against a fake
// DOM, and assert both the cleanup and its ORDER - the audio is already released
// by the time the next question renders or Home appears. They also re-check that
// Priority 0's settle() latch still makes the abandoned clip's late error /
// rejection / ended a no-op, which is what keeps the boundary calls from needing
// any new stale-callback machinery of their own.
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

// ---------- pull the real functions out of index.html ----------
// Brace scanner that skips comments and strings. It deliberately does NOT model
// regex literals: no function extracted below contains a regex carrying a brace,
// quote or backtick. If one ever does, extraction produces a broken snippet and
// the eval throws - a loud failure, which is the correct outcome.
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

var SRC = {};
['ppNormalize', 'clearSpeaking', 'stopAllAudio', 'speakText',
 'playPreGenerated', 'speakCardMain', 'speakFallback', 'currentRate'
].forEach(function (n) { SRC[n] = extractFunction(INDEX, n); });

// The speed table ships in index.html too - read it rather than restating it,
// so a changed rate is caught here instead of silently passing.
var speedsMatch = INDEX.match(/const\s+SPEEDS\s*=\s*(\{[^}]*\})\s*;/);
if (!speedsMatch) throw new Error('extract: SPEEDS table not found in index.html');
var SPEEDS = (0, eval)('(' + speedsMatch[1] + ')');

// ---------- environment the extracted code runs in ----------
var window = {};                                     // pp-usage.js attaches itself here
(0, eval)(readFile(ROOT + 'pp-usage.js'));
var PP_USAGE = window.PP_USAGE;
var ppMainAudioText = PP_USAGE.mainAudioText;        // index.html binds these the same way
var ppHasMainAudio = PP_USAGE.hasMainAudio;

// A thenable the test settles by hand. See the header for why this is not a Promise.
function Thenable() { this.onRejected = null; this.done = false; }
Thenable.prototype.catch = function (fn) { this.onRejected = fn; return this; };
Thenable.prototype.then = function (onF, onR) { if (onR) this.onRejected = onR; return this; };
Thenable.prototype.reject = function (err) {
  if (this.done) return;                             // a promise settles once, like the real thing
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
// Firing through the live handler property is deliberate: once the code under
// test detaches a handler, firing that event really is a no-op, exactly as it
// would be for a detached listener in a browser.
FakeAudio.prototype.fireError = function () { if (this.onerror) this.onerror({ type: 'error' }); };
FakeAudio.prototype.fireEnded = function () { if (this.onended) this.onended({ type: 'ended' }); };
FakeAudio.prototype.rejectPlay = function (name) { this.promise.reject({ name: name || 'NotSupportedError' }); };
FakeAudio.prototype.resolvePlay = function () { this.promise.resolve(); };

function FakeSynth() { this.spoken = []; this.cancels = 0; }
FakeSynth.prototype.speak = function (u) { this.spoken.push(u); };
FakeSynth.prototype.cancel = function () { this.cancels++; };
FakeSynth.prototype.getVoices = function () { return []; };

function FakeUtterance(text) {
  this.text = text; this.lang = ''; this.rate = 1; this.voice = null;
  this.onend = null; this.onerror = null;
}

function FakeBtn(id) { var self = this; this.id = id; this.speaking = false;
  this.classList = {
    add: function (c) { if (c === 'speaking') self.speaking = true; },
    remove: function (c) { if (c === 'speaking') self.speaking = false; }
  };
}

var synth = new FakeSynth();
window.speechSynthesis = synth;
var speechSynthesis = synth;
var SpeechSynthesisUtterance = FakeUtterance;
var Audio = FakeAudio;
var voiceHintCalls = 0;
function voiceHint() { voiceHintCalls++; }             // real one touches localStorage + DOM

// module-level state the extracted functions read and write
var audioMap = {};
var currentAudio = null;
var speakBtn = null;
var plVoice = null;
var currentSpeed = 'normal';

Object.keys(SRC).forEach(function (n) { (0, eval)(SRC[n]); });

var CLIP = 'audio/deadbeef.mp3';
function reset() {
  FakeAudio.created = [];
  synth.spoken = []; synth.cancels = 0;
  currentAudio = null; speakBtn = null; currentSpeed = 'normal'; voiceHintCalls = 0;
  audioMap = { 'kawa': CLIP, 'Gdzie jest apteka?': 'audio/cafe1234.mp3' };
}
function lastAudio() { return FakeAudio.created[FakeAudio.created.length - 1]; }

// =========================================================================
// 0. the extracted source really is the audio path, and BOTH failure routes
//    are still wired up. A "fix" that deletes one channel would pass every
//    behavioural test below while losing a real failure mode, so state the
//    requirement directly.
ok('T0 playPreGenerated still handles the error event', /onerror\s*=/.test(SRC.playPreGenerated));
ok('T0 playPreGenerated still handles the play() rejection', /\.play\(\)\s*\.catch\(/.test(SRC.playPreGenerated));
ok('T0 playPreGenerated still handles normal completion', /onended\s*=/.test(SRC.playPreGenerated));
ok('T0 no timer is used to suppress the duplicate',
   SRC.playPreGenerated.indexOf('setTimeout') === -1 && SRC.playPreGenerated.indexOf('setInterval') === -1);
ok('T0 speed table read from index.html', SPEEDS.normal === 1.0 && SPEEDS.slow === 0.7);

// 1. onerror THEN a rejected play promise -> exactly one fallback
reset();
speakText('kawa', new FakeBtn('speak'));
var a = lastAudio();
ok('T1 the clip was attempted', FakeAudio.created.length === 1 && a.src === CLIP && a.playCount === 1);
a.fireError();
eq('T1 error event speaks once', synth.spoken.length, 1);
a.rejectPlay();
eq('T1 later play() rejection adds nothing', synth.spoken.length, 1);
eq('T1 the fallback said the original text', synth.spoken[0].text, 'kawa');
ok('T1 failed element released', currentAudio === null);
ok('T1 handlers detached after the first outcome', a.onended === null && a.onerror === null);

// 2. a rejected play promise THEN onerror -> exactly one fallback
reset();
speakText('kawa', new FakeBtn('speak'));
a = lastAudio();
a.rejectPlay();
eq('T2 play() rejection speaks once', synth.spoken.length, 1);
a.fireError();
eq('T2 later error event adds nothing', synth.spoken.length, 1);
ok('T2 failed element released', currentAudio === null);

// 3. onerror only -> exactly one fallback
reset();
speakText('kawa', new FakeBtn('speak'));
lastAudio().fireError();
eq('T3 error event alone speaks once', synth.spoken.length, 1);

// 4. a rejected play promise only -> exactly one fallback
reset();
speakText('kawa', new FakeBtn('speak'));
lastAudio().rejectPlay();
eq('T4 play() rejection alone speaks once', synth.spoken.length, 1);
// autoplay refusal is the real case where NO error event ever arrives
reset();
speakText('kawa', new FakeBtn('speak'));
lastAudio().rejectPlay('NotAllowedError');
eq('T4 autoplay refusal still speaks once', synth.spoken.length, 1);

// 5. successful native playback -> zero fallbacks, and nothing contradicts it
reset();
var okBtn = new FakeBtn('speak');
speakText('kawa', okBtn);
a = lastAudio();
ok('T5 button marked speaking during native playback', okBtn.speaking === true);
a.resolvePlay();
eq('T5 a resolved play() speaks nothing', synth.spoken.length, 0);
a.fireEnded();
eq('T5 clean end speaks nothing', synth.spoken.length, 0);
ok('T5 button cleared at the end', okBtn.speaking === false);
ok('T5 finished element released', currentAudio === null);
a.fireError();
eq('T5 a late error after a clean end speaks nothing', synth.spoken.length, 0);

// 6. two independent attempts -> one fallback each
reset();
var b1 = new FakeBtn('speak');
speakText('kawa', b1);
var first = lastAudio();
first.fireError(); first.rejectPlay();
eq('T6 first attempt speaks once', synth.spoken.length, 1);
var b2 = new FakeBtn('speak');
speakText('kawa', b2);
var second = lastAudio();
ok('T6 the second press builds a new Audio', FakeAudio.created.length === 2 && second !== first);
ok('T6 the second press cancelled the first utterance', synth.cancels >= 1);
second.rejectPlay(); second.fireError();
eq('T6 second attempt speaks once more', synth.spoken.length, 2);
ok('T6 both utterances carried the same text',
   synth.spoken[0].text === 'kawa' && synth.spoken[1].text === 'kawa');
ok('T6 the old latch cannot leak into the new attempt', (function () {
  first.fireError();                                  // dead instance, must stay dead
  return synth.spoken.length === 2;
})());

// 7. an incomplete template has NO main audio at all: no clip, no speech
var TEMPLATES = [
  { id: 't1', pl: 'Gdzie jest...?', en: 'Where is...?', cardType: 'template' },
  { id: 't2', pl: 'Mam na imię...', en: 'My name is...', cardType: 'template' },
  { id: 't3', pl: 'Poproszę...', en: 'I would like...', cardType: 'template' },
  { id: 't4', pl: 'Boli mnie...', en: 'It hurts...', cardType: 'template' }
];
TEMPLATES.forEach(function (card) {
  reset();
  speakCardMain(card, new FakeBtn('speak'));
  ok('T7 ' + card.pl + ' requests no clip', FakeAudio.created.length === 0);
  ok('T7 ' + card.pl + ' speaks nothing', synth.spoken.length === 0);
  ok('T7 ' + card.pl + ' has no main audio', ppHasMainAudio(card) === false);
});
// a blank / incomplete audioText is refused the same way
reset();
speakCardMain({ id: 't5', pl: 'Boli mnie...', en: 'It hurts...', cardType: 'template', audioText: '   ' }, new FakeBtn('b'));
speakCardMain({ id: 't6', pl: 'Mam na imię...', en: 'My name is...', cardType: 'template', audioText: 'Mam na imię {imię}.' }, new FakeBtn('b'));
ok('T7 incomplete audioText requests no clip', FakeAudio.created.length === 0);
ok('T7 incomplete audioText speaks nothing', synth.spoken.length === 0);
// podcast intro cards are silent for their own reason - unchanged
reset();
speakCardMain({ id: 't7', pl: 'Stan umysłu', en: 'State of Mind', intro: true }, new FakeBtn('b'));
ok('T7 podcast intro stays silent', FakeAudio.created.length === 0 && synth.spoken.length === 0);
// but a template's COMPLETE example sentence still plays, and still falls back once
reset();
speakText('Gdzie jest apteka?', new FakeBtn('speakEx'));
ok('T7 complete example still requests its clip', FakeAudio.created.length === 1);
lastAudio().fireError(); lastAudio().rejectPlay();
eq('T7 complete example falls back exactly once', synth.spoken.length, 1);
// and a template carrying a complete audioText speaks that, not its pattern
reset();
audioMap['Gdzie jest apteka?'] = 'audio/cafe1234.mp3';
speakCardMain({ id: 't8', pl: 'Gdzie jest...?', en: 'Where is...?', cardType: 'template',
                audioText: 'Gdzie jest apteka?' }, new FakeBtn('speak'));
ok('T7 complete audioText plays the complete utterance',
   FakeAudio.created.length === 1 && lastAudio().src === 'audio/cafe1234.mp3');

// =========================================================================
// 8. things the fix must not have disturbed
// a phrase with no clip in the manifest goes straight to speech - no clip request
reset();
speakText('nieznane słowo', new FakeBtn('speak'));
ok('T8 manifest miss requests no clip', FakeAudio.created.length === 0);
eq('T8 manifest miss speaks once', synth.spoken.length, 1);
// empty text does nothing at all
reset();
speakText('', new FakeBtn('speak'));
ok('T8 empty text is silent', FakeAudio.created.length === 0 && synth.spoken.length === 0);
// Normal and Slow rates reach both the clip and the fallback voice
reset();
speakText('kawa', new FakeBtn('speak'));
ok('T8 normal rate on the clip', lastAudio().playbackRate === SPEEDS.normal);
ok('T8 pitch preserved on the clip', lastAudio().preservesPitch === true);
lastAudio().fireError();
ok('T8 normal rate on the fallback voice', synth.spoken[0].rate === SPEEDS.normal);
reset();
currentSpeed = 'slow';
speakText('kawa', new FakeBtn('speak'));
ok('T8 slow rate on the clip', lastAudio().playbackRate === SPEEDS.slow);
lastAudio().fireError();
ok('T8 slow rate on the fallback voice', synth.spoken[0].rate === SPEEDS.slow);
ok('T8 fallback speaks Polish', synth.spoken[0].lang === 'pl-PL');
// the fallback owns the button after it takes over
reset();
var fbBtn = new FakeBtn('speak');
speakText('kawa', fbBtn);
lastAudio().rejectPlay();
ok('T8 button still marked speaking under the fallback', fbBtn.speaking === true);
synth.spoken[0].onend();
ok('T8 button cleared when the fallback voice ends', fbBtn.speaking === false);
// a button-less call (Listening auto-play with no target) must not throw
reset();
speakText('kawa', null);
lastAudio().fireError(); lastAudio().rejectPlay();
eq('T8 button-less call still speaks once', synth.spoken.length, 1);
// stopAllAudio pauses and releases whatever is playing
reset();
speakText('kawa', new FakeBtn('speak'));
var playing = lastAudio();
stopAllAudio();
ok('T8 stopAllAudio pauses the clip', playing.pauses === 1);
ok('T8 stopAllAudio releases the clip', currentAudio === null);
ok('T8 stopAllAudio cancels pending speech', synth.cancels >= 1);
// A clip that fails AFTER stopAllAudio must NOT speak. The learner deliberately
// stopped it; pause() aborts the pending play(), so this late rejection is a
// consequence of the stop, not a playback failure worth reporting.
eq('T8 a stopped clip that then errors speaks nothing', (function () {
  var before = synth.spoken.length;
  playing.fireError();
  return synth.spoken.length - before;
})(), 0);
eq('T8 a stopped clip whose play() then rejects speaks nothing', (function () {
  var before = synth.spoken.length;
  playing.rejectPlay('AbortError');
  return synth.spoken.length - before;
})(), 0);
// the same, in the other order
reset();
speakText('kawa', new FakeBtn('speak'));
var stopped = lastAudio();
stopAllAudio();
stopped.rejectPlay('AbortError');
stopped.fireError();
eq('T8 stopped clip: rejection then error speaks nothing', synth.spoken.length, 0);
ok('T8 a stopped clip leaves currentAudio released', currentAudio === null);

// =========================================================================
// 9. a SUPERSEDED attempt must stay completely out of the way.
//    A is playing, the learner presses B. stopAllAudio() pauses A, and pause()
//    aborts A's pending play(), so A is guaranteed a late rejection - and it may
//    fire `error` afterwards too. Neither may speak A's stale phrase, and neither
//    may touch the button state that now belongs to B.
function startAB() {                                   // A superseded by B, both live clips
  reset();
  var o = {};
  o.btnA = new FakeBtn('speakA');
  speakText('kawa', o.btnA);
  o.A = lastAudio();
  o.btnB = new FakeBtn('speakB');
  speakText('kawa', o.btnB);                           // supersedes A
  o.B = lastAudio();
  return o;
}

// the handover itself
var s = startAB();
ok('T9 B is a different Audio', s.B !== s.A);
ok('T9 currentAudio is B', currentAudio === s.B);
ok('T9 stopAllAudio paused A', s.A.pauses === 1);
ok('T9 A button no longer speaking', s.btnA.speaking === false);
ok('T9 B button speaking', s.btnB.speaking === true);
ok('T9 speakBtn is B', speakBtn === s.btnB);

// 9a. late REJECTION from A, then late ERROR from A -> nothing at all
s = startAB();
s.A.rejectPlay('AbortError');
eq('T9a superseded A: late rejection speaks nothing', synth.spoken.length, 0);
ok('T9a superseded A did not clear B speaking class', s.btnB.speaking === true);
ok('T9a superseded A did not steal speakBtn', speakBtn === s.btnB);
ok('T9a currentAudio is still B', currentAudio === s.B);
s.A.fireError();
eq('T9a superseded A: following error speaks nothing', synth.spoken.length, 0);
ok('T9a B still intact after A error', currentAudio === s.B && s.btnB.speaking === true && speakBtn === s.btnB);

// 9b. late ERROR from A, then late REJECTION from A -> nothing at all
s = startAB();
s.A.fireError();
eq('T9b superseded A: late error speaks nothing', synth.spoken.length, 0);
ok('T9b superseded A did not clear B speaking class', s.btnB.speaking === true);
ok('T9b superseded A did not steal speakBtn', speakBtn === s.btnB);
ok('T9b currentAudio is still B', currentAudio === s.B);
s.A.rejectPlay('AbortError');
eq('T9b superseded A: following rejection speaks nothing', synth.spoken.length, 0);
ok('T9b B still intact after A rejection', currentAudio === s.B && s.btnB.speaking === true && speakBtn === s.btnB);

// 9c. after A's late signals, B must still be able to FAIL and fall back once
s = startAB();
s.A.rejectPlay('AbortError'); s.A.fireError();
eq('T9c A contributed no fallback', synth.spoken.length, 0);
s.B.fireError(); s.B.rejectPlay();
eq('T9c B falls back exactly once', synth.spoken.length, 1);
ok('T9c the fallback belongs to B, and owns the button', s.btnB.speaking === true && speakBtn === s.btnB);
ok('T9c B released after failing', currentAudio === null);

// 9d. after A's late signals, B must still be able to SUCCEED with no fallback
s = startAB();
s.A.fireError(); s.A.rejectPlay('AbortError');
s.B.resolvePlay();
s.B.fireEnded();
eq('T9d B completes with no fallback at all', synth.spoken.length, 0);
ok('T9d B released on clean end', currentAudio === null);
ok('T9d B button cleared on clean end', s.btnB.speaking === false);
ok('T9d speakBtn cleared, not handed back to A', speakBtn === null);

// 9e. three-deep: A superseded by B superseded by C. Only C may ever speak.
reset();
var btnA3 = new FakeBtn('A'), btnB3 = new FakeBtn('B'), btnC3 = new FakeBtn('C');
speakText('kawa', btnA3); var A3 = lastAudio();
speakText('kawa', btnB3); var B3 = lastAudio();
speakText('kawa', btnC3); var C3 = lastAudio();
A3.rejectPlay('AbortError'); A3.fireError();
B3.rejectPlay('AbortError'); B3.fireError();
eq('T9e superseded A and B speak nothing', synth.spoken.length, 0);
ok('T9e C is current and owns the button', currentAudio === C3 && btnC3.speaking === true && speakBtn === btnC3);
ok('T9e A and B buttons are not speaking', btnA3.speaking === false && btnB3.speaking === false);
C3.fireError();
eq('T9e only C falls back, once', synth.spoken.length, 1);

// 9f. the guard keys off the LIVE currentAudio, not merely off "something else
//     started" - a clip stopped with nothing replacing it is equally silent
reset();
var lone = new FakeBtn('speak');
speakText('kawa', lone);
var loneAudio = lastAudio();
stopAllAudio();
loneAudio.fireError(); loneAudio.rejectPlay('AbortError');
eq('T9f stopped-with-no-successor speaks nothing', synth.spoken.length, 0);
ok('T9f button not resurrected', lone.speaking === false && speakBtn === null);

// =========================================================================
// LISTENING AUDIO LIFECYCLE (sections 10-18)
// =========================================================================
// Everything below drives the SHIPPING Listening functions - startListen,
// lRender, lPlayCurrent, lShowDone and the two boundary helpers - pulled out of
// index.html the same way the audio functions above are.

// Comment-stripped view of a snippet. Ordering assertions must be decided by
// code, not by prose that happens to mention a call. Same string/comment machine
// as extractFunction; used only on snippets already extracted from index.html.
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

// The Listening state object ships in index.html - read its shape rather than
// restating it, so a renamed or added field is caught here.
var lStateMatch = INDEX.match(/const\s+L\s*=\s*(\{[^}]*\})\s*;/);
if (!lStateMatch) throw new Error('extract: Listening state object L not found in index.html');
var L = (0, eval)('(' + lStateMatch[1] + ')');

// ---------- a fake DOM: just enough for the real Listening screen code ----------
function FakeEl(tag) {
  this.tag = tag || 'div';
  this.textContent = '';
  this.className = '';
  this.disabled = false;
  this.style = {};
  this.children = [];
  this.classes = {};
  this._html = '';
  this._attrs = {};
  this._on = {};
  var self = this;
  this.classList = {
    add: function (c) { self.classes[c] = true; },
    remove: function (c) { delete self.classes[c]; },
    contains: function (c) { return !!self.classes[c]; }
  };
}
// innerHTML replaces every child, exactly as the real property does - that is
// what lets lRender clear the option row and the feedback box between questions.
Object.defineProperty(FakeEl.prototype, 'innerHTML', {
  get: function () { return this._html; },
  set: function (v) { this._html = String(v); this.children = this._html ? [new FakeEl('parsed')] : []; }
});
Object.defineProperty(FakeEl.prototype, 'childNodes', { get: function () { return this.children; } });
// same accessor FakeBtn exposes, so either kind of button can be checked alike
Object.defineProperty(FakeEl.prototype, 'speaking', { get: function () { return this.classes.speaking === true; } });
FakeEl.prototype.appendChild = function (el) { this.children.push(el); return el; };
FakeEl.prototype.setAttribute = function (k, v) { this._attrs[k] = v; };
FakeEl.prototype.getAttribute = function (k) { return this._attrs[k]; };
FakeEl.prototype.addEventListener = function (t, fn) { (this._on[t] = this._on[t] || []).push(fn); };
FakeEl.prototype.click = function () { (this._on.click || []).forEach(function (fn) { fn({}); }); };
FakeEl.prototype.querySelectorAll = function (sel) {
  var want = sel.replace('.', '');
  return this.children.filter(function (c) { return (' ' + c.className + ' ').indexOf(' ' + want + ' ') !== -1; });
};

var DOM = {};
function el(id) { return DOM[id] || (DOM[id] = new FakeEl('#' + id)); }   // index.html's $()
var fakeDoc = { createElement: function (t) { return new FakeEl(t); } };

// show() is stubbed, and records the audio state AT THE MOMENT IT IS CALLED.
// That is how "Home is shown only after cleanup" becomes an assertion rather
// than an assumption.
var shown = [];
function pauseTotal() { return FakeAudio.created.reduce(function (n, a) { return n + a.pauses; }, 0); }
function fakeShow(scr) { shown.push({ scr: scr, audio: currentAudio, pauses: pauseTotal(), btn: speakBtn }); }

// pp-distractor.js is the real builder - index.html calls it with exactly this shape.
(0, eval)(readFile(ROOT + 'pp-distractor.js'));
var PP_DISTRACTOR = window.PP_DISTRACTOR;

// A five-card topic. Distinct glosses, distinct heard prompts, so the builder
// returns four options every time and the round is fully deterministic.
var LCARDS = [
  { id: 'l1', pl: 'kawa',    en: 'coffee', ex: 'Poproszę kawę.', exEn: 'A coffee, please.' },
  { id: 'l2', pl: 'herbata', en: 'tea' },
  { id: 'l3', pl: 'woda',    en: 'water' },
  { id: 'l4', pl: 'sok',     en: 'juice' },
  { id: 'l5', pl: 'mleko',   en: 'milk' }
];
var LEVELS = [{ level: 'A1', topics: [{ name: 'W kawiarni', src: ['A1'], kind: 'listen' }] }];
function fakePoolFor() { return LCARDS.map(function (c) { return { c: c, topic: 'W kawiarni' }; }); }
function fakeShuffle(a) { return a.slice(); }            // deterministic: identity
// pp-usage's labelling is owned by tests/test_activities.js; nothing here depends on it.
function fakeAppendUsage() {}
var G_AUDIO_STUB = '<svg data-icon="audio"></svg>';

// ---------- reading the wiring out of index.html ----------
// The click handler expression bound to a Listening control, whatever its shape.
function handlerExpr(id) {
  var re = new RegExp('\\$\\(\\s*["\']' + id + '["\']\\s*\\)\\s*\\.addEventListener\\(\\s*["\']click["\']\\s*,([\\s\\S]*?)\\)\\s*;', 'g');
  var hits = [], m;
  while ((m = re.exec(INDEX)) !== null) hits.push(m[1].trim());
  if (hits.length !== 1) throw new Error('wiring: expected exactly one click handler for ' + id + ', found ' + hits.length);
  return hits[0];
}

// The Listening functions need $, document, show and the app-level helpers. `$`
// is already taken in this file - it is JXA's ObjC bridge - so they are handed
// in as PARAMETERS of a generated scope instead of being planted as globals.
// Everything they share with the audio path above (stopAllAudio, speakText,
// speakCardMain, currentAudio, speakBtn) still resolves to the same globals the
// sections above exercise, so the two halves test one system, not two.
//
// The four boundary CONTROLS are compiled into that scope from their handler
// expressions as index.html writes them, so activate() below runs what the app
// actually binds - not a copy of it. (They cannot be eval'd on demand instead:
// under osascript a direct eval inside a nested function resolves globally, so
// it would not see this scope at all.)
var L_CONTROLS = ['lNext', 'lBack', 'lHome', 'lAgain'];
var LNAMES = ['startListen', 'lRender', 'lPlayCurrent', 'lShowDone', 'lAdvance', 'lExit'];
var LSRC = {};
LNAMES.forEach(function (n) { LSRC[n] = extractFunction(INDEX, n); });
var LISTEN = (new Function('$', 'document', 'show', 'L', 'LEVELS', 'poolFor', 'gShuffle', 'ppAppendUsageTo', 'G_AUDIO',
  LNAMES.map(function (n) { return LSRC[n]; }).join('\n') + '\n' +
  // one wrapper so a test can watch the moment the next question renders
  'var __spy = null, __realRender = lRender;\n' +
  'lRender = function(){ if(__spy) __spy(); return __realRender(); };\n' +
  'return {\n' +
  '  spyRender: function(fn){ __spy = fn; },\n' +
  '  startListen: function(a,b){ return startListen(a,b); },\n' +
  '  lRender: function(){ return lRender(); },\n' +
  '  lPlayCurrent: function(){ return lPlayCurrent(); },\n' +
  '  handlers: {\n' +
  L_CONTROLS.map(function (id) { return '    ' + id + ': (' + handlerExpr(id) + ')'; }).join(',\n') + '\n' +
  '  }\n' +
  '};'
))(el, fakeDoc, fakeShow, L, LEVELS, fakePoolFor, fakeShuffle, fakeAppendUsage, G_AUDIO_STUB);
// What actually runs when the control is activated: the expression itself, or
// the single named function it delegates to. Inline body or named helper both
// resolve - the assertion is about behaviour, not about which style was chosen.
function handlerBody(id) {
  var code = stripComments(handlerExpr(id)).trim();
  var bare = code.match(/^([A-Za-z_$][A-Za-z0-9_$]*)$/);
  if (bare) return stripComments(extractFunction(INDEX, bare[1]));
  var delegate = code.match(/^\(\s*\)\s*=>\s*([A-Za-z_$][A-Za-z0-9_$]*)\s*\(/);
  if (delegate) return stripComments(extractFunction(INDEX, delegate[1]));
  return code;
}
// Audio must be stopped BEFORE anything the learner can observe changes.
var L_EFFECTS = ['show(', 'lRender(', 'L.i', 'L.li', 'L.qs', 'L.results', 'L.attempted'];
function stopsAudioFirst(body) {
  var stop = body.indexOf('stopAllAudio');
  if (stop === -1) return false;
  for (var i = 0; i < L_EFFECTS.length; i++) {
    var e = body.indexOf(L_EFFECTS[i]);
    if (e !== -1 && e < stop) return false;
  }
  return true;
}
function activate(id) { return LISTEN.handlers[id](); }

// ---------- per-test setup ----------
var L_CLIPS = {
  'kawa': 'audio/l-kawa.mp3', 'herbata': 'audio/l-herbata.mp3', 'woda': 'audio/l-woda.mp3',
  'sok': 'audio/l-sok.mp3', 'mleko': 'audio/l-mleko.mp3', 'Poproszę kawę.': 'audio/l-ex-kawa.mp3'
};
function lReset() {
  reset();                                                 // shared audio state, as above
  Object.keys(L_CLIPS).forEach(function (k) { audioMap[k] = L_CLIPS[k]; });
  DOM = {}; shown = []; LISTEN.spyRender(null);
}
// a fresh round on question 1, nothing playing. The navigation log is cleared
// AFTER the round opens, so `shown` below holds only what the boundary did.
function lStart() { lReset(); LISTEN.startListen(0, 0); shown = []; }
function lPress() { LISTEN.lPlayCurrent(); return lastAudio(); }   // the learner presses Play
function answerCorrect() {                                  // click the option flagged `correct`
  var opts = el('lOpts').children, q = L.qs[L.i], idx = -1;
  q.options.forEach(function (o, i) { if (o.correct) idx = i; });
  if (idx < 0) throw new Error('fixture: no correct option built for question ' + L.i);
  opts[idx].click();
}

// =========================================================================
// 10. the fixture round itself is sane, and entering it is silent
lStart();
eq('T10 a round of every fixture card', L.qs.length, 5);
eq('T10 starts on question one', L.i, 0);
ok('T10 four options built', el('lOpts').children.length === 4);
eq('T10 the counter shows question one', el('lCountLbl').textContent, '1 / 5');
ok('T10 entering a round autoplays nothing', FakeAudio.created.length === 0 && synth.spoken.length === 0);
ok('T10 Play starts the current clip', (function () {
  var clip = lPress();
  return FakeAudio.created.length === 1 && clip.src === L_CLIPS['kawa'] && currentAudio === clip;
})());
ok('T10 Play marks its button speaking', el('lPlay').speaking === true && speakBtn === el('lPlay'));

// =========================================================================
// 11. A. ADVANCE while the MP3 is playing (Next)
lStart();
var lClip = lPress();
var lBtn = el('lPlay');
var atRender = [];
LISTEN.spyRender(function () {
  atRender.push({ i: L.i, audio: currentAudio, pauses: lClip.pauses, speaking: lBtn.speaking });
});
activate('lNext');
eq('T11 the clip was paused exactly once', lClip.pauses, 1);
ok('T11 currentAudio released', currentAudio === null);
ok('T11 the Play button lost its speaking class', lBtn.speaking === false && speakBtn === null);
ok('T11 speech synthesis was cancelled', synth.cancels >= 1);
ok('T11 the audio was ALREADY stopped when the next question rendered',
   atRender.length === 1 && atRender[0].audio === null && atRender[0].pauses === 1 && atRender[0].speaking === false);
eq('T11 the render that saw the cleanup is the NEXT question', atRender[0].i, 1);
eq('T11 the round advanced', L.i, 1);
eq('T11 the next question is on screen', el('lCountLbl').textContent, '2 / 5');
ok('T11 the next question has its own options', el('lOpts').children.length === 4);
ok('T11 the next question starts silent - no autoplay',
   FakeAudio.created.length === 1 && synth.spoken.length === 0);
ok('T11 the next question can still play its own clip', (function () {
  var second = lPress();
  return FakeAudio.created.length === 2 && second !== lClip && currentAudio === second && el('lPlay').speaking === true;
})());

// advancing off the LAST question lands on the results screen, just as silently
lStart();
L.i = 4; LISTEN.lRender();
var lastClip = lPress();
activate('lNext');
eq('T11 the final clip was paused', lastClip.pauses, 1);
ok('T11 results screen reached with nothing playing', currentAudio === null && speakBtn === null);
ok('T11 the results screen is showing', el('lDone').style.display === 'flex' && el('lMain').style.display === 'none');

// =========================================================================
// 12. B/C. EXIT through Back, and through Home - identical guarantees
['lBack', 'lHome'].forEach(function (id) {
  lStart();
  var clip = lPress();
  var btn = el('lPlay');
  var cancelsBefore = synth.cancels;
  activate(id);
  eq('T12 ' + id + ' paused the clip exactly once', clip.pauses, 1);
  ok('T12 ' + id + ' released currentAudio', currentAudio === null);
  ok('T12 ' + id + ' cancelled speech synthesis', synth.cancels > cancelsBefore);
  ok('T12 ' + id + ' cleared the Play button', btn.speaking === false && speakBtn === null);
  eq('T12 ' + id + ' went home', shown.length === 1 ? shown[0].scr : shown.map(function (s) { return s.scr; }), 'home');
  ok('T12 ' + id + ' showed Home only AFTER the cleanup',
     shown[0].audio === null && shown[0].pauses === 1 && shown[0].btn === null);
  ok('T12 ' + id + ' started nothing on the way out',
     FakeAudio.created.length === 1 && synth.spoken.length === 0);
});

// =========================================================================
// 13. D. START ANOTHER ROUND - "New round", and the topic tile
// the previous round's clip cannot follow the learner into the new one
lStart();
var againClip = lPress();
var againBtn = el('lPlay');
activate('lAgain');
eq('T13 New round paused the previous clip exactly once', againClip.pauses, 1);
ok('T13 New round released currentAudio', currentAudio === null);
ok('T13 New round cleared the speaking button', againBtn.speaking === false && speakBtn === null);
ok('T13 New round cancelled speech synthesis', synth.cancels >= 1);
eq('T13 the new round starts on question one', L.i, 0);
eq('T13 the new round is a full round', L.qs.length, 5);
eq('T13 the new round has a clean score', L.results.length, 0);
eq('T13 the new round is on screen', el('lCountLbl').textContent, '1 / 5');
ok('T13 the new round autoplays nothing',
   FakeAudio.created.length === 1 && synth.spoken.length === 0);

// an EXAMPLE clip - not the question clip - is stopped by the same boundary
lStart();
var exMini = new FakeBtn('mini');
speakText('Poproszę kawę.', exMini);
var exClip = lastAudio();
ok('T13 the example clip is the live one', currentAudio === exClip && exMini.speaking === true);
activate('lAgain');
eq('T13 New round paused the example clip', exClip.pauses, 1);
ok('T13 New round released the example clip', currentAudio === null && exMini.speaking === false);

// entering from the topic tile: routeTopic calls startListen directly, with
// whatever the previous screen left playing
lReset();
var homeBtn = new FakeBtn('card');
speakText('kawa', homeBtn);
var carried = lastAudio();
LISTEN.startListen(0, 0);
eq('T13 the topic tile paused the carried-over clip', carried.pauses, 1);
ok('T13 the topic tile entry is silent', currentAudio === null && homeBtn.speaking === false);
ok('T13 the topic tile round rendered', L.qs.length === 5 && L.i === 0);

// =========================================================================
// 14. E. SPEECH-SYNTHESIS playback is cancelled at the boundaries too,
//        and the score is not touched on the way through
lStart();
answerCorrect();
eq('T14 the first try scored', L.results, [true]);
delete audioMap['kawa'];                          // no clip -> the device voice takes over
var fbBtn = el('lPlay');
lPress();
eq('T14 the fallback voice is speaking', synth.spoken.length, 1);
ok('T14 the fallback owns the button', fbBtn.speaking === true && speakBtn === fbBtn);
var cancelsPre = synth.cancels;
activate('lNext');
ok('T14 advancing cancelled the utterance', synth.cancels > cancelsPre);
ok('T14 advancing cleared the button', fbBtn.speaking === false && speakBtn === null);
eq('T14 the score is unchanged by advancing', L.results, [true]);
eq('T14 the round advanced', L.i, 1);
eq('T14 advancing started no new speech', synth.spoken.length, 1);
// and on the way out
lStart();
answerCorrect();
delete audioMap['kawa'];
lPress();
var exitCancels = synth.cancels;
activate('lHome');
ok('T14 exiting cancelled the utterance', synth.cancels > exitCancels);
ok('T14 exiting cleared the button', el('lPlay').speaking === false && speakBtn === null);
eq('T14 the score is unchanged by exiting', L.results, [true]);
ok('T14 speech was cancelled before Home appeared', shown[0].btn === null && shown[0].audio === null);

// =========================================================================
// 15. F. a LATE error / rejected play() from a clip abandoned at a boundary
//        must stay stale. settle() already refuses to act for an element that
//        is no longer currentAudio, and the boundary call is what releases it.
[['lNext', 'advance'], ['lBack', 'Back'], ['lHome', 'Home']].forEach(function (pair) {
  var id = pair[0], what = pair[1];
  // rejection first, then error
  lStart();
  var clip = lPress();
  activate(id);
  clip.rejectPlay('AbortError');
  eq('T15 ' + what + ': the abandoned clip\'s rejection speaks nothing', synth.spoken.length, 0);
  clip.fireError();
  eq('T15 ' + what + ': the following error speaks nothing', synth.spoken.length, 0);
  ok('T15 ' + what + ': nothing was resurrected', currentAudio === null && speakBtn === null);
  // error first, then rejection
  lStart();
  clip = lPress();
  activate(id);
  clip.fireError();
  eq('T15 ' + what + ': the abandoned clip\'s error speaks nothing', synth.spoken.length, 0);
  clip.rejectPlay('AbortError');
  eq('T15 ' + what + ': the following rejection speaks nothing', synth.spoken.length, 0);
  ok('T15 ' + what + ': the Play button was not re-marked', el('lPlay').speaking === false);
});
// a stale signal must not spoil the NEXT question's own failure handling
lStart();
var staleClip = lPress();
activate('lNext');
staleClip.fireError(); staleClip.rejectPlay('AbortError');
var liveClip = lPress();
liveClip.fireError(); liveClip.rejectPlay();
eq('T15 the next question still falls back exactly once', synth.spoken.length, 1);
eq('T15 and it spoke the NEW question', synth.spoken[0].text, 'herbata');

// =========================================================================
// 16. G. a LATE `ended` from question one must not disturb question two
lStart();
var q1 = lPress();
activate('lNext');
var q2 = lPress();
ok('T16 question two owns the audio', currentAudio === q2 && q2 !== q1);
ok('T16 question two owns the button', el('lPlay').speaking === true && speakBtn === el('lPlay'));
q1.fireEnded();
ok('T16 question two is still current', currentAudio === q2);
ok('T16 question two keeps its speaking class', el('lPlay').speaking === true && speakBtn === el('lPlay'));
eq('T16 the round did not move', L.i, 1);
eq('T16 the score was not touched', L.results.length, 0);
eq('T16 nothing was spoken', synth.spoken.length, 0);
q2.fireEnded();
ok('T16 question two still ends cleanly on its own', currentAudio === null && el('lPlay').speaking === false);
eq('T16 a clean end speaks nothing', synth.spoken.length, 0);
// the same after an EXIT rather than an advance
lStart();
var goneClip = lPress();
activate('lBack');
goneClip.fireEnded();
ok('T16 an abandoned clip\'s ended changes nothing on the way out',
   currentAudio === null && speakBtn === null && shown.length === 1);
eq('T16 and speaks nothing', synth.spoken.length, 0);

// =========================================================================
// 17. H. the FEEDBACK EXAMPLE's mini-audio goes through the same lifecycle
lStart();
answerCorrect();
var fbHtml = el('lFbBox').innerHTML;
var sayMatch = fbHtml.match(/data-say="([^"]*)"/);
ok('T17 the correct answer offers the example clip', !!sayMatch);
var sayText = decodeURIComponent(sayMatch[1]);
eq('T17 the mini-audio plays the example sentence', sayText, 'Poproszę kawę.');
// exactly what the delegated [data-say] listener does with that button
var mini = new FakeBtn('mini-audio');
speakText(sayText, mini);
var exampleClip = lastAudio();
ok('T17 the example clip is live', currentAudio === exampleClip && mini.speaking === true);
activate('lNext');
eq('T17 advancing paused the example clip exactly once', exampleClip.pauses, 1);
ok('T17 advancing released it', currentAudio === null);
ok('T17 advancing cleared the mini-audio button', mini.speaking === false && speakBtn === null);
eq('T17 the round advanced', L.i, 1);
ok('T17 the next question starts silent', el('lPlay').speaking === false);
exampleClip.rejectPlay('AbortError'); exampleClip.fireError();
eq('T17 the abandoned example clip speaks no fallback', synth.spoken.length, 0);
// and on the way out
lStart();
answerCorrect();
var mini2 = new FakeBtn('mini-audio');
speakText(decodeURIComponent(el('lFbBox').innerHTML.match(/data-say="([^"]*)"/)[1]), mini2);
var exampleClip2 = lastAudio();
activate('lHome');
eq('T17 exiting paused the example clip', exampleClip2.pauses, 1);
ok('T17 exiting cleared the mini-audio button', mini2.speaking === false && currentAudio === null);
ok('T17 Home appeared only after the example clip was released',
   shown[0].audio === null && shown[0].btn === null && shown[0].pauses === 1);

// =========================================================================
// 18. I. WIRING - every Listening boundary in index.html is protected, and the
//        protection runs BEFORE anything the learner can observe changes.
ok('T18 Next stops audio before the question changes', stopsAudioFirst(handlerBody('lNext')));
ok('T18 Back stops audio before leaving', stopsAudioFirst(handlerBody('lBack')));
ok('T18 Home stops audio before leaving', stopsAudioFirst(handlerBody('lHome')));
ok('T18 New round stops audio before rebuilding the round', stopsAudioFirst(handlerBody('lAgain')));
ok('T18 startListen stops audio first, so every round entry is covered',
   stopsAudioFirst(stripComments(LSRC.startListen)));
ok('T18 Play is still wired to lPlayCurrent', handlerExpr('lPlay') === 'lPlayCurrent');
// routeTopic is the OTHER way into a round - the topic tile
ok('T18 the topic tile routes Listening through startListen',
   /kind\s*===\s*"listen"\s*\)\s*startListen\(/.test(stripComments(extractFunction(INDEX, 'routeTopic'))));
// the feedback example shares currentAudio ownership because it goes through speakText
ok('T18 [data-say] audio is played by speakText',
   /closest\("\[data-say\]"\)[\s\S]{0,120}speakText\(/.test(INDEX));
// the boundaries must delegate to stopAllAudio, not hand-roll their own cleanup
['lNext', 'lBack', 'lHome', 'lAgain'].forEach(function (id) {
  var body = handlerBody(id);
  ok('T18 ' + id + ' does not hand-roll pausing',
     body.indexOf('.pause(') === -1 && body.indexOf('speechSynthesis') === -1 && body.indexOf('speakBtn') === -1);
});
// Priority 0's audio functions are untouched by this phase
ok('T18 stopAllAudio still pauses, releases, cancels and clears', (function () {
  var s = stripComments(SRC.stopAllAudio);
  return /currentAudio\s*\.\s*pause\(\)|currentAudio\.pause\(\)/.test(s) && /currentAudio\s*=\s*null/.test(s) &&
         s.indexOf('speechSynthesis.cancel()') !== -1 && s.indexOf('clearSpeaking()') !== -1;
})());
ok('T18 settle() still keys off the live currentAudio',
   /currentAudio\s*!==\s*audio/.test(stripComments(SRC.playPreGenerated)));
// no autoplay was introduced: rendering a question never starts playback
ok('T18 lRender starts no audio', (function () {
  var s = stripComments(LSRC.lRender);
  return s.indexOf('speakText') === -1 && s.indexOf('speakCardMain') === -1 && s.indexOf('lPlayCurrent') === -1;
})());
ok('T18 startListen starts no audio', (function () {
  var s = stripComments(LSRC.startListen);
  return s.indexOf('speakText') === -1 && s.indexOf('speakCardMain') === -1 && s.indexOf('lPlayCurrent') === -1;
})());

// ---------- report ----------
console.log('Audio fallback tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
LOG.forEach(function (l) { console.log('  ' + l); });
if (FAIL > 0) { throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed'); }
