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
function gitFile(revision, path) {
  var task = $.NSTask.alloc.init;
  task.launchPath = '/usr/bin/git';
  task.arguments = $(['--no-pager', '-C', ROOT, 'show', revision + ':' + path]);
  var pipe = $.NSPipe.pipe;
  task.standardOutput = pipe;
  task.standardError = pipe;
  task.launch;
  var data = pipe.fileHandleForReading.readDataToEndOfFile;
  task.waitUntilExit;
  if (task.terminationStatus !== 0)
    throw new Error('required historical object unavailable: ' + revision + ':' + path);
  return ObjC.unwrap($.NSString.alloc.initWithDataEncoding(data, $.NSUTF8StringEncoding));
}
function phase1Stats(runtime) {
  var result = { examples: [], recognitionOnly: 0 };
  runtime.lemmas.forEach(function (lemma) {
    lemma.meanings.forEach(function (meaning) {
      meaning.patterns.forEach(function (pattern) {
        (pattern.examples || []).forEach(function (example) { result.examples.push(example); });
        if (pattern.teachingStatus === 'recognition-only') result.recognitionOnly++;
      });
    });
  });
  return result;
}
function pRenderLemmaSource(index) {
  var start = index.indexOf('function pRenderLemma(entry){');
  var end = index.indexOf('\nfunction pRenderUnavailable', start);
  return start === -1 || end === -1 ? '' : index.slice(start, end);
}
function currentRenderUsesOnlyStaticAudioIcon(index) {
  var body = pRenderLemmaSource(index);
  var assignments = body.match(/\b\w+\.innerHTML\s*=\s*[^;]+;/g) || [];
  var icon = (index.match(/const G_AUDIO='([^']*)';/) || [])[1];
  return icon.indexOf('<svg') === 0 && icon.indexOf('pattern.') === -1 &&
    assignments.length === 1 && assignments[0] === 'audio.innerHTML = G_AUDIO;' &&
    body.indexOf('const pl = pEl("p", "vp-example-pl", pattern.example.pl);') !== -1 &&
    body.indexOf('audio.setAttribute("data-say", encodeURIComponent(pattern.example.pl));') !== -1;
}
function phase1ButtonUsesEmoji(index) {
  return index.indexOf('pEl("button", "mini-audio vp-example-audio", null)') !== -1 &&
    index.indexOf('audio.type = "button";') !== -1 &&
    index.indexOf('audio.textContent = "🔊";') !== -1;
}
var ROOT = rootPath();
var INDEX = readFile(ROOT + 'index.html');
var HELPER = readFile(ROOT + 'pp-verb-patterns.js');
var WORKER = readFile(ROOT + 'sw.js');
var RUNTIME = JSON.parse(readFile(ROOT + 'content/verb-patterns.json'));
var PHASE1_RELEASE = 'caf3716d503a51d90e3238f1a566de6caad6fef0';
var PHASE1_INDEX = gitFile(PHASE1_RELEASE, 'index.html');
var PHASE1_HELPER = gitFile(PHASE1_RELEASE, 'pp-verb-patterns.js');
var PHASE1_WORKER = gitFile(PHASE1_RELEASE, 'sw.js');
var PHASE1_RUNTIME = JSON.parse(gitFile(PHASE1_RELEASE, 'content/verb-patterns.json'));
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

// Current runtime acceptance remains live; exact Phase-1 counts are snapshots.
ok('A1 revision-2 runtime is accepted', PP_VERB_PATTERNS.acceptRuntimeDocument(RUNTIME));
var examples = [], activities = [];
for (var i = 0; i < PP_VERB_PATTERNS.summary().lemmas; i++) {
  var lemma = PP_VERB_PATTERNS.lemma(i);
  lemma.meanings.forEach(function (meaning) {
    meaning.patterns.forEach(function (pattern) {
      activities.push(pattern.eligibility);
    });
  });
}
var phase1 = phase1Stats(PHASE1_RUNTIME);
var phase1MissingAudio = JSON.parse(JSON.stringify(PHASE1_RUNTIME));
phase1MissingAudio.lemmas[0].meanings[0].patterns[0].examples[0].audioEligible = false;
ok('A2 historical 45 derived examples carry pronunciation permission',
   JSON.stringify([phase1.examples.length,
     phase1.examples.filter(function (e) { return e.audioEligible; }).length]) === '[45,45]' &&
   JSON.stringify([phase1Stats(phase1MissingAudio).examples.length,
     phase1Stats(phase1MissingAudio).examples.filter(function (e) { return e.audioEligible; }).length]) !== '[45,45]');
eq('A3 pronunciation does not infer an activity',
   activities.filter(function (list) { return list.length; }).length, 0);
var phase1RecognitionMutation = JSON.parse(JSON.stringify(PHASE1_RUNTIME));
phase1RecognitionMutation.lemmas.forEach(function (lemma) {
  lemma.meanings.forEach(function (meaning) {
    meaning.patterns.forEach(function (pattern) {
      if (pattern.teachingStatus === 'recognition-only') pattern.teachingStatus = 'introduced';
    });
  });
});
ok('A4 historical recognition-only count remains four',
   phase1.recognitionOnly === 4 && phase1Stats(phase1RecognitionMutation).recognitionOnly !== 4);

// Rendering uses a native button and the one shared data-say/player path.
ok('B1 control is conditional only on the projected audio flag',
   INDEX.indexOf('if(pattern.example.audioEligible){') !== -1);
ok('B2 historical native control uses the Phase-1 emoji implementation',
   phase1ButtonUsesEmoji(PHASE1_INDEX) &&
   !phase1ButtonUsesEmoji(PHASE1_INDEX.replace('audio.textContent = "🔊";',
                                                'audio.innerHTML = G_AUDIO;')));
ok('B2 current render permits only the static G_AUDIO innerHTML assignment',
   currentRenderUsesOnlyStaticAudioIcon(INDEX) &&
   !currentRenderUsesOnlyStaticAudioIcon(INDEX.replace('audio.innerHTML = G_AUDIO;',
                                                        'audio.innerHTML = pattern.example.pl;')));
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
ok('E1 historical shell and persistent audio cache markers are correct',
   JSON.stringify([(PHASE1_WORKER.match(/const CACHE = "([^"]+)"/) || [])[1],
     (PHASE1_WORKER.match(/const AUDIO_CACHE = "([^"]+)"/) || [])[1]]) ===
     '["popolsku-v67","popolsku-audio"]' &&
   PHASE1_WORKER.replace('const CACHE = "popolsku-v67";',
                         'const CACHE = "popolsku-v68";').indexOf('const CACHE = "popolsku-v67";') === -1);
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

ok('F1 historical release marker advanced with no new helper storage or analytics',
   JSON.stringify([(PHASE1_INDEX.match(/APP_VERSION\s*=\s*"([^"]+)"/) || [])[1],
     countOf(PHASE1_HELPER, 'localStorage'), countOf(PHASE1_HELPER, 'analytics')]) ===
     '["8.12",0,0]' &&
   (PHASE1_INDEX.replace('APP_VERSION = "8.12";', 'APP_VERSION = "8.13";')
     .match(/APP_VERSION\s*=\s*"([^"]+)"/) || [])[1] !== '8.12');

if (FAIL) {
  LOG.forEach(function (line) { console.log(line); });
  throw new Error(FAIL + ' failure(s), ' + PASS + ' pass(es)');
}
console.log('PASS ' + PASS + ' assertions');
