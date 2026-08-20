// Priority 8 Phase 1A pronunciation-playback regression coverage.
// Runs with: osascript -l JavaScript tests/test_priority8_phase1_playback.js

ObjC.import('Foundation');

function readFile(path) {
  return ObjC.unwrap($.NSString.stringWithContentsOfFileEncodingError(
    path, $.NSUTF8StringEncoding, null));
}
function rootPath() {
  var fm = $.NSFileManager.defaultManager;
  var cwd = ObjC.unwrap(fm.currentDirectoryPath);
  if (fm.fileExistsAtPath(cwd + '/index.html')) return cwd + '/';
  return cwd + '/../';
}
function countOf(text, token) {
  var n = 0, at = 0;
  while ((at = text.indexOf(token, at)) !== -1) { n++; at += token.length; }
  return n;
}
var ROOT = rootPath();
var INDEX = readFile(ROOT + 'index.html');
var HELPER = readFile(ROOT + 'pp-verb-patterns.js');
var WORKER = readFile(ROOT + 'sw.js');
var RUNTIME = JSON.parse(readFile(ROOT + 'content/verb-patterns.json'));
(0, eval)(HELPER);

var PASS = 0, FAIL = 0, LOG = [];
function ok(name, value) {
  if (value) PASS++;
  else { FAIL++; LOG.push('FAIL: ' + name); }
}
function eq(name, actual, expected) {
  var a = JSON.stringify(actual), e = JSON.stringify(expected);
  ok(name + (a === e ? '' : ' (got ' + a + ', want ' + e + ')'), a === e);
}

// The released view retains pronunciation permission without creating an activity.
ok('A1 revision-2 runtime is accepted', PP_VERB_PATTERNS.acceptRuntimeDocument(RUNTIME));
var examples = [], activities = [], recognitionOnly = 0;
for (var i = 0; i < PP_VERB_PATTERNS.summary().lemmas; i++) {
  var lemma = PP_VERB_PATTERNS.lemma(i);
  lemma.meanings.forEach(function (meaning) {
    meaning.patterns.forEach(function (pattern) {
      if (pattern.example) examples.push(pattern.example);
      activities.push(pattern.eligibility);
      if (pattern.recognitionOnly) recognitionOnly++;
    });
  });
}
eq('A2 all 45 derived examples carry pronunciation permission',
   [examples.length, examples.filter(function (e) { return e.audioEligible; }).length],
   [45, 45]);
eq('A3 pronunciation does not infer an activity',
   activities.filter(function (list) { return list.length; }).length, 0);
eq('A4 recognition-only remains recognition-only', recognitionOnly, 4);

// Rendering uses a native button and the one shared data-say/player path.
ok('B1 control is conditional only on the projected audio flag',
   INDEX.indexOf('if(pattern.example.audioEligible){') !== -1);
ok('B2 control is a native button with the existing shared audio class',
   INDEX.indexOf('pEl("button", "mini-audio vp-example-audio", null)') !== -1 &&
   INDEX.indexOf('audio.type = "button";') !== -1 &&
   INDEX.indexOf('audio.textContent = "🔊";') !== -1);
ok('B2 runtime-derived reference text is never parsed through innerHTML',
   /function pRenderLemma\(entry\)\{[\s\S]*?audio\.innerHTML/.test(INDEX) === false);
ok('B3 exact Polish is encoded for the shared click delegate',
   INDEX.indexOf('audio.setAttribute("data-say", encodeURIComponent(pattern.example.pl));') !== -1 &&
   INDEX.indexOf('e.target.closest("[data-say]")') !== -1);
ok('B4 accessible name is contextual and reuses the shared naming helper',
   INDEX.indexOf('ppSetAudioControlName(audio, "Play example sentence", pattern.example.pl);') !== -1);
ok('B5 the visible Polish retains its language tag',
   INDEX.indexOf('pl.setAttribute("lang", "pl");') !== -1);
ok('B6 mobile/touch target is 44px and the text may shrink and wrap',
   INDEX.indexOf('.vp-example-audio{width:44px;height:44px') !== -1 &&
   INDEX.indexOf('.vp-example-pl{flex:1;min-width:0;') !== -1);

// Manifest settlement changes pressability only; unavailable still reaches fallback.
ok('C1 pattern controls are disabled only while manifest state is loading',
   INDEX.indexOf('audio.disabled = audioManifestStatus === "loading";') !== -1 &&
   INDEX.indexOf('const loading = audioManifestStatus === "loading";') !== -1);
ok('C2 every manifest outcome resynchronizes pattern controls without autoplay',
   countOf(INDEX, 'syncPatternAudioReadiness();') === 1 &&
   INDEX.indexOf('document.querySelectorAll(".vp-example-audio")') !== -1);

// Replay, many visible controls, rapid switching and stale callbacks are owned by
// the existing single player. These exact guards are also behaviorally exercised
// by test_audio_fallback.js; this suite proves Verb Patterns routes into them.
ok('D1 every request cancels the previous owner before selecting a route',
   /function speakText\(txt, btn\)\{[\s\S]*?stopAllAudio\(\);[\s\S]*?const key/.test(INDEX));
eq('D2 one shared HTML audio constructor remains',
   countOf(INDEX, 'const audio = new Audio(file);'), 1);
ok('D3 replay makes a fresh attempt and one settled latch suppresses dual failure',
   INDEX.indexOf('const audio = new Audio(file);') !== -1 &&
   INDEX.indexOf('let settled = false;') !== -1);
ok('D4 superseded callbacks cannot clear or speak over the new request',
   INDEX.indexOf('if(currentAudio !== audio) return false;') !== -1 &&
   INDEX.indexOf('if(currentUtterance !== u) return;') !== -1);
ok('D5 returning to the index or leaving the surface stops stale playback',
   /function pRenderIndex\(enterScreen\)\{[\s\S]*?stopAllAudio\(\);/.test(INDEX) &&
   INDEX.indexOf('fromScreen.id==="patterns" && fromScreen!==toScreen) stopAllAudio();') !== -1);
ok('D6 failure and retry use the existing polite atomic status route',
   INDEX.indexOf('box.setAttribute("aria-live","polite")') !== -1 &&
   INDEX.indexOf('box.setAttribute("aria-atomic","true")') !== -1 &&
   INDEX.indexOf('function retryAudio(){') !== -1);
ok('D7 reduced motion suppresses the shared speaking animation',
   INDEX.indexOf('.fab.speaking,.ex-audio.speaking,.mini-audio.speaking{animation:none}') !== -1);

// Worker behavior is inherited unchanged by each new content-hashed MP3.
eq('E1 shell and persistent audio cache markers are correct',
   [(WORKER.match(/const CACHE = "([^"]+)"/) || [])[1],
    (WORKER.match(/const AUDIO_CACHE = "([^"]+)"/) || [])[1]],
   ['popolsku-v67', 'popolsku-audio']);
ok('E2 runtime and manifest remain network-first while audio stays cache-first',
   WORKER.indexOf('if (category === "audio-manifest") { networkFirst') !== -1 &&
   WORKER.indexOf('if (category === "pattern-runtime") { networkFirst') !== -1 &&
   WORKER.indexOf('if (category === "audio") { cacheFirst(e, AUDIO_CACHE, key);') !== -1);
ok('E3 Range handling remains on the one approved hashed-MP3 route',
   WORKER.indexOf('audioRangeResponse(e, key, range)') !== -1 &&
   WORKER.indexOf('if (requestHeader(e.request, "if-range"))') !== -1);
ok('E4 no forced worker activation was introduced',
   WORKER.replace(/\/\*[\s\S]*?\*\//g, '').indexOf('skipWaiting()') === -1 &&
   WORKER.replace(/\/\*[\s\S]*?\*\//g, '').indexOf('clients.claim()') === -1);

eq('F1 release marker advanced with no new helper storage or analytics',
   [(INDEX.match(/APP_VERSION\s*=\s*"([^"]+)"/) || [])[1],
    countOf(HELPER, 'localStorage'), countOf(HELPER, 'analytics')],
   ['8.12', 0, 0]);

if (FAIL) {
  LOG.forEach(function (line) { console.log(line); });
  throw new Error(FAIL + ' failure(s), ' + PASS + ' pass(es)');
}
console.log('PASS ' + PASS + ' assertions');
