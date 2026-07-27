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

// ---------- report ----------
console.log('Audio fallback tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
LOG.forEach(function (l) { console.log('  ' + l); });
if (FAIL > 0) { throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed'); }
