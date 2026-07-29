// Deterministic tests for the Type It and Mixed Quiz COMPLETION SCORES.
// Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_round_scoring.js
// Exit status is 0 only if every assertion passes (printed at the end).
//
// WHAT THIS FILE IS FOR
// Priority 3 Phase 1B: an answer classified "almost" (correct except Polish
// diacritics) must stop being counted as fully correct in the end-of-round
// score. Both activities now report three separate tiers - right / almost /
// missed - and the tiers must always sum to the number of questions asked.
//
// HOW IT TESTS
// It does not re-implement the scoring. It lifts the real tShowDone, rShowDone
// and rRecord out of index.html and executes them against a stub `$` and stub
// state, so a future edit to the shipping code is what these assertions see.
//
// SCOPE - what deliberately is NOT here
// This suite owns how a verdict is COUNTED, never how it is DECIDED. The
// comparator contract (normalize / fold / accepted / classify, the diacritic
// rules, pięć vs piec) belongs to tests/test_answer_validation.js and is
// expected to evolve there; duplicating it here would freeze it twice over.
// Release identifiers - APP_VERSION, CACHE, AUDIO_CACHE - are likewise not
// pinned here: they change on purpose at release time, and a permanent scoring
// regression suite must not fail for that. The only cross-file claim this file
// makes is that both per-question handlers still route through PP_ANSWER.
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

// ---------- lifting real functions out of index.html ----------
// Same brace-matching extractor the answer-validation suite uses.
function bodyOf(src, name) {
  var start = src.indexOf('function ' + name + '(');
  if (start === -1) throw new Error('extract: function ' + name + ' not found in index.html');
  var open = src.indexOf('{', src.indexOf(')', start)), depth = 0;
  for (var j = open; j < src.length; j++) {
    if (src[j] === '{') depth++;
    else if (src[j] === '}') { depth--; if (depth === 0) return src.slice(start, j + 1); }
  }
  throw new Error('extract: unbalanced braces for ' + name);
}
var SRC_T_DONE = bodyOf(INDEX, 'tShowDone');
var SRC_R_DONE = bodyOf(INDEX, 'rShowDone');
var SRC_R_RECORD = bodyOf(INDEX, 'rRecord');
// Phase 4F: rShowDone reports the round against the size it was ASKED at, which it
// reads through this helper rather than off the R.qs array the requeue mechanism grows.
// It is lifted with rShowDone so the shipping code runs; what it says about PROGRESS is
// owned by tests/test_mixed_round_legibility.js.
var SRC_R_TOTAL = bodyOf(INDEX, 'rOriginalTotal');

// Compile a lifted function with its free identifiers supplied as parameters.
function lift(src, name, argNames) {
  var f = Function.apply(null, argNames.concat([src + '\nreturn ' + name + ';']));
  return function (args) { return f.apply(null, argNames.map(function (k) { return args[k]; })); };
}
var liftTShowDone = lift(SRC_T_DONE, 'tShowDone', ['$', 'T', 'window']);
var liftRShowDone = lift(SRC_R_TOTAL + '\n' + SRC_R_DONE, 'rShowDone',
  ['$', 'R', 'LEVELS', 'ppProgressWritable', 'loadV2', 'saveV2', 'window']);
var liftRRecord = lift(SRC_R_RECORD, 'rRecord', ['R', 'gShuffle']);

// ---------- stub DOM: just enough for the two done screens ----------
// textContent coerces to string exactly as a real node does, so the assertions
// below compare what a learner would actually read.
// CAPABILITY ONLY, no new assertion: rShowDone now focuses the completion heading,
// so a node that cannot be focused throws before any score is written. Where focus
// actually LANDS is asserted in tests/test_mixed_accessibility.js, which models the
// real focus rules; this file still asks only about the numbers on the done screen.
function makeNode() {
  var o = { style: {}, focused: 0 }, t = '', h = '';
  Object.defineProperty(o, 'textContent', { get: function () { return t; },
                                            set: function (v) { t = String(v); } });
  Object.defineProperty(o, 'innerHTML', { get: function () { return h; },
                                          set: function (v) { h = String(v); } });
  o.focus = function () { o.focused++; };
  return o;
}
function makeDom() {
  var nodes = {};
  var get$ = function (id) { return (nodes[id] || (nodes[id] = makeNode())); };
  return { $: get$, text: function (id) { return get$(id).textContent; } };
}

// =========================================================================
// 1. TYPE IT - three tiers, "almost" is never folded into the correct total
// =========================================================================
function typeItRound(total, right, almost) {
  var dom = makeDom();
  var T = { qs: new Array(total), right: right, almost: almost };
  liftTShowDone({ $: dom.$, T: T, window: {} })();
  return {
    correct: dom.text('tScoreN'),
    almost:  dom.text('tAlmostN'),
    missed:  dom.text('tMissN'),
    msg:     dom.text('tDoneMsg')
  };
}

// 1a. the worked example from the brief: 11 right, 3 almost, 1 wrong
var mix = typeItRound(15, 11, 3);
eq('T1 mixed round reports 11 correct', mix.correct, '11');
eq('T1 mixed round reports 3 almost', mix.almost, '3');
eq('T1 mixed round reports 1 missed', mix.missed, '1');
ok('T1 mixed round NEVER claims 14 correct', mix.correct !== '14' && mix.msg.indexOf('14') === -1);
ok('T1 message states the exact-right count', mix.msg.indexOf('11 of 15') !== -1);
ok('T1 message names the almost tier separately', mix.msg.indexOf('3 almost') !== -1);
ok('T1 message names the missed tier separately', mix.msg.indexOf('1 to revisit') !== -1);
ok('T1 almost is not described as correct',
   mix.msg.indexOf('3 correct') === -1 && mix.msg.indexOf('14 correct') === -1);

// 1b. all right - and only then may the round be called perfect
var allRight = typeItRound(15, 15, 0);
eq('T1 all-right correct tile', allRight.correct, '15');
eq('T1 all-right almost tile', allRight.almost, '0');
eq('T1 all-right missed tile', allRight.missed, '0');
ok('T1 all-right message is the perfect-round message',
   allRight.msg.indexOf('every one exactly right') !== -1);
ok('T1 all-right message mentions no other tier',
   allRight.msg.indexOf('almost') === -1 && allRight.msg.indexOf('revisit') === -1);

// 1c. all almost - the honesty case that used to read as a perfect score
var allAlmost = typeItRound(15, 0, 15);
eq('T1 all-almost scores zero correct', allAlmost.correct, '0');
eq('T1 all-almost reports 15 almost', allAlmost.almost, '15');
eq('T1 all-almost reports 0 missed', allAlmost.missed, '0');
ok('T1 all-almost is NOT the perfect-round message',
   allAlmost.msg.indexOf('every one exactly right') === -1);
ok('T1 all-almost says 0 of 15 exactly right', allAlmost.msg.indexOf('0 of 15') !== -1);
ok('T1 all-almost still says the almosts out loud', allAlmost.msg.indexOf('15 almost') !== -1);

// 1d. all wrong
var allWrong = typeItRound(15, 0, 0);
eq('T1 all-wrong correct tile', allWrong.correct, '0');
eq('T1 all-wrong almost tile', allWrong.almost, '0');
eq('T1 all-wrong missed tile', allWrong.missed, '15');
ok('T1 all-wrong mentions no almost clause', allWrong.msg.indexOf('almost') === -1);
ok('T1 all-wrong says 15 to revisit', allWrong.msg.indexOf('15 to revisit') !== -1);

// 1e. right + almost must not become the correct total, for every split
var COMBOS = [[15,11,3],[15,15,0],[15,0,15],[15,0,0],[15,7,8],[15,1,1],[15,14,1],[15,0,1],[10,5,4],[1,0,1]];
COMBOS.forEach(function (cmb) {
  var total = cmb[0], right = cmb[1], almost = cmb[2];
  var r = typeItRound(total, right, almost);
  ok('T1 (' + cmb.join('/') + ') correct tile is right-only',
     r.correct === String(right));
  ok('T1 (' + cmb.join('/') + ') correct tile is not right+almost',
     almost === 0 || r.correct !== String(right + almost));
  ok('T1 (' + cmb.join('/') + ') tiers sum to the round size',
     Number(r.correct) + Number(r.almost) + Number(r.missed) === total);
});

// =========================================================================
// 2. MIXED QUIZ - score counts "right" only; progress writes are unchanged
// =========================================================================
// A round is described as a list of [cardId, firstTryResult]; requeued copies
// are appended by the real rRecord, exactly as they are in the app.
function mixedRound(spec, opts) {
  opts = opts || {};
  var dom = makeDom();
  // Phase 4F: the round now carries the size it was ASKED at, fixed before any retry
  // could exist, plus its own hint counter. `spec` IS the original phase, so its length
  // is exactly what startRound would have banked. `hinted` defaults to none, so every
  // assertion written before this phase describes an un-hinted round, unchanged.
  var R = { li: 0, ti: 0, i: 0, originalTotal: spec.length, hinted: opts.hinted || 0,
    qs: spec.map(function (s) {
      return { c: { id: s[0], en: s[0], intro: !!s[2] }, fmt: 'type', options: [], requeued: false, result: null };
    }) };
  var rRecord = liftRRecord({ R: R, gShuffle: function (a) { return a; } });

  // walk the round the way the UI does: answer each question, including any
  // requeued copy the recorder appends while we are walking.
  var second = opts.secondPass || {};
  for (var i = 0; i < R.qs.length; i++) {
    var q = R.qs[i];
    var verdict = q.requeued ? (second[q.c.id] || 'right') : spec[i][1];
    rRecord(q, verdict);
  }

  var saved = null;
  var store = { progress: {} };
  if (opts.progress) store.progress['topic-1'] = opts.progress;
  liftRShowDone({
    $: dom.$, R: R,
    LEVELS: [{ topics: [{ id: 'topic-1', name: 'Topic' }] }],
    ppProgressWritable: function () { return opts.writable === false ? false : true; },
    loadV2: function () { return store; },
    saveV2: function (s) { saved = s; },
    window: {}
  })();
  var rec = saved && saved.progress['topic-1'];
  return {
    correct: dom.text('rScoreN'),
    almost:  dom.text('rAlmostN'),
    missed:  dom.text('rMissN'),
    msg:     dom.text('rDoneMsg'),
    asked:   R.qs.length,
    counter: dom.text('rCountLbl'),
    total:   R.originalTotal,
    known:   rec ? rec.known.slice().sort() : null,
    still:   rec ? rec.still.slice().sort() : null
  };
}

// 2a. the headline rule: only exact matches count as correct
var mq = mixedRound([['c1','right'],['c2','almost'],['c3','miss'],['c4','right'],['c5','miss']]);
eq('T2 final score counts right only', mq.correct, '2');
eq('T2 almost is reported separately', mq.almost, '1');
eq('T2 miss is reported separately', mq.missed, '2');
ok('T2 score is not right+almost', mq.correct !== '3');
ok('T2 message states the right-only count', mq.msg.indexOf('2 of 5 right on the first try') !== -1);
ok('T2 message names the almost tier', mq.msg.indexOf('1 almost') !== -1);
ok('T2 message names the review tier', mq.msg.indexOf('2 to review') !== -1);
ok('T2 tiers sum to the questions asked',
   Number(mq.correct) + Number(mq.almost) + Number(mq.missed) === 5);

// 2b. requeued copies are not counted twice
eq('T2 two misses were requeued (7 slots, 5 scored)', mq.asked, 7);
ok('T2 requeued copies add nothing to any tier',
   Number(mq.correct) + Number(mq.almost) + Number(mq.missed) === 5);
var mq2 = mixedRound([['c1','miss'],['c2','miss']], { secondPass: { c1: 'right', c2: 'right' } });
eq('T2 a requeued copy answered right does not raise the score', mq2.correct, '0');
eq('T2 a requeued copy answered right stays a miss', mq2.missed, '2');
eq('T2 a requeued copy is not requeued again', mq2.asked, 4);
var mq3 = mixedRound([['c1','miss']], { secondPass: { c1: 'almost' } });
eq('T2 a requeued copy answered almost adds nothing to the almost tier', mq3.almost, '0');

// 2c. persistence: right marks known, miss marks still, almost changes nothing
eq('T2 right marks the card known', mq.known, ['c1', 'c4']);
eq('T2 miss marks the card still learning', mq.still, ['c3', 'c5']);
ok('T2 almost does NOT mark the card known', mq.known.indexOf('c2') === -1);
ok('T2 almost does NOT mark the card still learning', mq.still.indexOf('c2') === -1);

// almost must leave PRE-EXISTING progress exactly as it found it, both ways
var wasKnown = mixedRound([['c2','almost']], { progress: { still: [], known: ['c2'] } });
eq('T2 almost leaves an already-known card known', wasKnown.known, ['c2']);
eq('T2 almost does not move a known card to still', wasKnown.still, []);
var wasStill = mixedRound([['c2','almost']], { progress: { still: ['c2'], known: [] } });
eq('T2 almost leaves an already-still card still', wasStill.still, ['c2']);
eq('T2 almost does not promote a still card to known', wasStill.known, []);

// right/miss persistence is unchanged, including the promote/demote swap
var swap = mixedRound([['c1','right'],['c2','miss']], { progress: { still: ['c1'], known: ['c2'] } });
eq('T2 right promotes and clears still', swap.known, ['c1']);
eq('T2 miss demotes and clears known', swap.still, ['c2']);

// intro cards are still never tracked (unchanged guard)
var intro = mixedRound([['c1','right',true],['c2','miss',true]]);
eq('T2 intro card is not marked known', intro.known, []);
eq('T2 intro card is not marked still', intro.still, []);

// 2d. the perfect-round message is now gated on exact matches only
var perfect = mixedRound([['c1','right'],['c2','right']]);
ok('T2 all-right earns the perfect-round message',
   perfect.msg.indexOf('Every question right on the first try') !== -1);
var nearPerfect = mixedRound([['c1','right'],['c2','almost']]);
ok('T2 an almost forfeits the perfect-round message',
   nearPerfect.msg.indexOf('Every question right on the first try') === -1);
eq('T2 near-perfect round scores 1, not 2', nearPerfect.correct, '1');
var allAlmostMq = mixedRound([['c1','almost'],['c2','almost']]);
eq('T2 an all-almost round scores zero', allAlmostMq.correct, '0');
eq('T2 an all-almost round reports both as almost', allAlmostMq.almost, '2');
eq('T2 an all-almost round requeues nothing', allAlmostMq.asked, 2);
ok('T2 an all-almost round is not called perfect',
   allAlmostMq.msg.indexOf('Every question right on the first try') === -1);

// =========================================================================
// 2e. PHASE 4F - the tiers are still the ORIGINAL round, and hints stay outside
// The round now carries `originalTotal`, fixed when it started, and `hinted`, its own
// count of first-attempt questions that used "Reveal a letter". Neither may reach the
// arithmetic above. What the counter and the hint sentence SAY during a round is owned
// by tests/test_mixed_round_legibility.js; this file owns only that the numbers on the
// done screen did not move.
// =========================================================================
// the tiers are still counted over the original questions, however much R.qs grew
var f4 = mixedRound([['c1','right'],['c2','miss'],['c3','almost'],['c4','miss'],['c5','right']]);
eq('T2e the round was asked at five questions', f4.total, 5);
eq('T2e ... and grew to seven with the retries', f4.asked, 7);
eq('T2e the tiers still sum to the ORIGINAL total',
   Number(f4.correct) + Number(f4.almost) + Number(f4.missed), f4.total);
ok('T2e ... and not to the grown array',
   Number(f4.correct) + Number(f4.almost) + Number(f4.missed) !== f4.asked);
ok('T2e the message counts out of the original total', f4.msg.indexOf('2 of 5 right') !== -1);
ok('T2e ... never out of the grown array', f4.msg.indexOf(' of 7') === -1);
eq('T2e the results counter reads the original total, twice', f4.counter, '5 / 5');
ok('T2e the results counter is not the grown array', f4.counter.indexOf('7') === -1);
// retries are still excluded from every tier, exactly as before
var f4r = mixedRound([['c1','miss'],['c2','miss'],['c3','miss']], { secondPass: { c1:'right', c2:'right', c3:'right' } });
eq('T2e three retries answered right still score zero', f4r.correct, '0');
eq('T2e ... and stay three to review', f4r.missed, '3');
eq('T2e ... over an original total of three', f4r.total, 3);
eq('T2e ... in a six-slot array', f4r.asked, 6);
eq('T2e ... with the counter still reading the original round', f4r.counter, '3 / 3');

// hints change no tier - same spec, run with and without them
var HPLAN = [['c1','right'],['c2','almost'],['c3','miss'],['c4','right']];
var noHint = mixedRound(HPLAN);
var withHint = mixedRound(HPLAN, { hinted: 3 });
eq('T2e hints do not move the correct tile', withHint.correct, noHint.correct);
eq('T2e hints do not move the almost tile', withHint.almost, noHint.almost);
eq('T2e hints do not move the review tile', withHint.missed, noHint.missed);
eq('T2e hints do not move the original total', withHint.total, noHint.total);
eq('T2e hints do not move the results counter', withHint.counter, noHint.counter);
eq('T2e hints requeue nothing extra', withHint.asked, noHint.asked);
eq('T2e hints do not move progress writeback', withHint.known, noHint.known);
eq('T2e ... either way', withHint.still, noHint.still);
// the sentence is APPENDED, outside the tier clauses
eq('T2e the hinted message is the un-hinted message plus one sentence',
   withHint.msg, noHint.msg + ' You used hints on 3 questions.');
ok('T2e the tier clauses come first',
   withHint.msg.indexOf('to review.') < withHint.msg.indexOf('You used hints'));
ok('T2e an un-hinted round says nothing about hints', noHint.msg.indexOf('hint') === -1);
var h1 = mixedRound(HPLAN, { hinted: 1 });
ok('T2e one hinted question uses the singular', h1.msg.indexOf(' You used a hint on 1 question.') !== -1);
ok('T2e ... and not the plural', h1.msg.indexOf('hints on') === -1);
// a perfect round that used hints keeps the perfect wording AND reports the hints
var hPerfect = mixedRound([['c1','right'],['c2','right']], { hinted: 2 });
eq('T2e a hinted clean sweep still scores every question', hPerfect.correct, '2');
ok('T2e ... and keeps the perfect-round wording',
   hPerfect.msg.indexOf('Every question right on the first try') === 0);
ok('T2e ... while still reporting the hints',
   hPerfect.msg.indexOf('You used hints on 2 questions.') !== -1);
ok('T2e the hint sentence never frames a hinted answer as lesser',
   [h1.msg, withHint.msg, hPerfect.msg].every(function (m) {
     return m.indexOf('deduct') === -1 && m.indexOf('penal') === -1 && m.indexOf('not count') === -1;
   }));
// persistence is untouched by either new field
var hProg = mixedRound([['c1','right'],['c2','miss'],['c3','almost']], { hinted: 2 });
eq('T2e a hinted round still writes right to known', hProg.known, ['c1']);
eq('T2e ... and miss to still learning', hProg.still, ['c2']);
ok('T2e ... and almost to neither',
   hProg.known.indexOf('c3') === -1 && hProg.still.indexOf('c3') === -1);
// and neither new field is persisted
ok('T2e neither new field reaches the stored record',
   SRC_R_DONE.indexOf('hinted:') === -1 && SRC_R_DONE.indexOf('originalTotal:') === -1);
ok('T2e the stored shape is still still/known id lists',
   SRC_R_DONE.indexOf('store.progress[tRound.id] = { still:[...still], known:[...known] };') !== -1);
// the tiers are computed from `scored`, never from the hint count
ok('T2e no tier is derived from the hint count', (function () {
  var s = SRC_R_DONE.replace(/\s+/g, '');
  return s.indexOf('right-hinted') === -1 && s.indexOf('right+hinted') === -1 &&
         s.indexOf('almost-hinted') === -1 && s.indexOf('missed+hinted') === -1 &&
         s.indexOf('scored.length-hinted') === -1;
})());
// The visible denominator is the FIXED original total, not the length of the filtered
// array. The two are equal under the current requeue policy - one retry per first-try
// miss, and a retry never re-requeues - so this is an ownership claim rather than an
// arithmetic one: R.originalTotal answers "how big was this round", and a filtered
// array that happens to agree is not the same statement.
ok('T2e the completion message is built from the fixed original total',
   SRC_R_DONE.indexOf('"You got "+right+" of "+total+" right on the first try."') !== -1);
ok('T2e the perfect-round test is against the fixed original total',
   SRC_R_DONE.indexOf('right===total ?') !== -1);
ok('T2e the fixed total is read from the original-total helper',
   SRC_R_DONE.replace(/\s+/g, '').indexOf('consttotal=rOriginalTotal()') !== -1);
ok('T2e no learner-facing "of N" is taken from scored.length', (function () {
  var s = SRC_R_DONE.replace(/\s+/g, '');
  return s.indexOf('of"+scored.length') === -1 && s.indexOf('right===scored.length') === -1;
})());
// ... while `scored` keeps the arithmetic and the persistence walk
ok('T2e the tiers are still counted off the scored originals', (function () {
  var s = SRC_R_DONE.replace(/\s+/g, '');
  return s.indexOf('scored.filter(q=>q.result==="right").length') !== -1 &&
         s.indexOf('scored.filter(q=>q.result==="almost").length') !== -1 &&
         s.indexOf('scored.filter(q=>q.result==="miss").length') !== -1;
})());
ok('T2e retries are still excluded from the scored set',
   SRC_R_DONE.indexOf('R.qs.filter(q=>!q.requeued)') !== -1);
ok('T2e the persistence walk still uses the scored originals',
   SRC_R_DONE.replace(/\s+/g, '').indexOf('scored.forEach(q=>{') !== -1);
// and the two agree in practice, on every fixture this file drives
[f4, f4r, noHint, withHint, h1, hPerfect, hProg, mq, mq2, mq3, perfect, nearPerfect, allAlmostMq]
  .forEach(function (r, n) {
    eq('T2e fixture ' + n + ': the tiers sum to the fixed original total',
       Number(r.correct) + Number(r.almost) + Number(r.missed), r.total);
  });

// =========================================================================
// 3. MARKUP - each done screen has its own three tiles, wired to the counters
// =========================================================================
['t', 'r'].forEach(function (p) {
  ok('T3 ' + p + 'AlmostN tile exists',
     INDEX.indexOf('id="' + p + 'AlmostN"') !== -1);
  ok('T3 ' + p + 'AlmostN uses the almost colour class',
     INDEX.indexOf('<b class="almost-n" id="' + p + 'AlmostN">0</b>') !== -1);
});
ok('T3 the almost colour class is defined once', INDEX.indexOf('.stat b.almost-n{') !== -1);
ok('T3 Type It labels the three tiles distinctly',
   INDEX.indexOf('id="tScoreN">0</b><span>CORRECT<') !== -1 &&
   INDEX.indexOf('id="tAlmostN">0</b><span>ALMOST<') !== -1 &&
   INDEX.indexOf('id="tMissN">0</b><span>MISSED<') !== -1);
ok('T3 Mixed Quiz labels the three tiles distinctly',
   INDEX.indexOf('id="rScoreN">0</b><span>CORRECT<') !== -1 &&
   INDEX.indexOf('id="rAlmostN">0</b><span>ALMOST<') !== -1 &&
   INDEX.indexOf('id="rMissN">0</b><span>TO REVIEW<') !== -1);
// the old "almost counts as correct" arithmetic must be gone, not just unused
ok('T3 Type It no longer adds almost into the score', SRC_T_DONE.indexOf('T.right+T.almost') === -1);
ok('T3 Mixed Quiz no longer adds almost into the score', SRC_R_DONE.indexOf('right+almost') === -1);
ok('T3 Mixed Quiz score tile is fed the right count alone',
   SRC_R_DONE.indexOf('$("rScoreN").textContent  = right;') !== -1);

// =========================================================================
// 4. UNCHANGED - per-question feedback and requeue policy
// Phase 1B changed only the end-of-round tally, so the things a learner meets
// DURING a round must still be exactly what they were.
// =========================================================================
var SRC_T_CHECK = bodyOf(INDEX, 'tCheckAnswer');
var SRC_R_CHECK = bodyOf(INDEX, 'rCheckAnswer');
// per-question verdict wording and the three verdict classes are untouched
['tCheckAnswer', 'rCheckAnswer'].forEach(function (fn) {
  var s = fn === 'tCheckAnswer' ? SRC_T_CHECK : SRC_R_CHECK;
  ok('T4 ' + fn + ' still classifies through PP_ANSWER', s.indexOf('PP_ANSWER.classify(') !== -1);
  ok('T4 ' + fn + ' still shows the amber almost head',
     s.indexOf('verdict==="almost" ? "Almost - watch the \\u0105') !== -1);
  ok('T4 ' + fn + ' still applies the per-verdict class', s.indexOf('"verdict show v-"+verdict') !== -1);
  ok('T4 ' + fn + ' still lets the learner continue after any verdict',
     s.indexOf('disabled=false') !== -1);
});
// Phase 1B adds no requeue for "almost"
ok('T4 only a miss is requeued', SRC_R_RECORD.indexOf('if(result==="miss"){') !== -1);
ok('T4 requeued copies still never re-score', SRC_R_RECORD.indexOf('if(q.requeued) return;') !== -1);
// the progress rules themselves are the ones that were already there
ok('T4 miss still writes still-learning', SRC_R_DONE.indexOf('still.add(id); known.delete(id);') !== -1);
ok('T4 right still writes known', SRC_R_DONE.indexOf('known.add(id); still.delete(id);') !== -1);
ok('T4 almost still writes nothing', SRC_R_DONE.indexOf('"almost" leaves progress untouched') !== -1);
ok('T4 intro cards are still excluded', SRC_R_DONE.indexOf('q.c.intro') !== -1);
ok('T4 requeued copies are still excluded from scoring',
   SRC_R_DONE.indexOf('R.qs.filter(q=>!q.requeued)') !== -1);

// ---------- report ----------
console.log('Round scoring tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
LOG.forEach(function (l) { console.log('  ' + l); });
if (FAIL > 0) { throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed'); }
