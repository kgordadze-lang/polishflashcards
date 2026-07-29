// Deterministic tests for pp-distractor.js - the shared multiple-choice option
// builder. Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_distractors.js
// Exit status is 0 only if every assertion passes (printed at the end).
//
// WHAT THIS FILE IS FOR
// Priority 3 Phase 3A. A Listening question plays one Polish clip and offers
// four English meanings, exactly one of which is meant to be right. The corpus
// teaches the same Polish word in more than one topic, each time with its own
// gloss - `burza` is "storm" in Podroze i wakacje and "(thunder)storm" in
// Pogoda i klimat - and the old "any card whose English differs" rule let both
// into one question. The learner heard `burza`, both answers were true, and
// whichever they picked had a 50% chance of being marked wrong.
//
// HOW IT TESTS
// Two halves, deliberately.
//   Synthetic fixtures pin the CONTRACT: no Polish word and no card id from the
//   shipping data decides anything here, so the rules stay readable and stay
//   true for cards nobody has written yet.
//   The real corpus is then swept through the same builder. The collision set
//   is DISCOVERED on every run - never remembered as a number - so a new
//   duplicate-audio pair added later is covered the day it lands. Counts are
//   REPORTED and never asserted, because the corpus is allowed to grow. Today
//   the sweep finds 25 duplicate-audio groups reachable in All Levels, 11 of
//   them live inside a single level. Read on the authored text alone the first
//   figure is 28: three further groups - `blisko`, `obok`, `szczery` - carry
//   glosses that differ only by a comma or a slash, so they stop counting as
//   two different answers once punctuation is folded. They are excluded from
//   each other's questions all the same, by the heard-prompt rule.
//
// SCOPE - what deliberately is NOT here
// Which cards may be asked at all belongs to tests/test_activities.js and
// tests/test_typeit_eligibility.js. How a typed answer is judged belongs to
// test_answer_validation.js, how a round scores to test_round_scoring.js. This
// file owns the option SET: who may share a question, and that the right answer
// survives as identity rather than as a string. The Mixed Quiz adopted the same
// builder in Phase 4D; section H asserts only that the adoption is real, and
// everything the Mixed Quiz does with the records afterwards - the two prompt
// identities, the fallback join, the retry and the corpus sweep - is owned by
// tests/test_mixed_distractors.js.
// Release identifiers - APP_VERSION, CACHE, AUDIO_CACHE - are not pinned: they
// change on purpose at release time.
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
var SW = readFile(ROOT + 'sw.js');
var DISTRACTOR_SRC = readFile(ROOT + 'pp-distractor.js');

// index.html loads these in this order; pp-distractor.js sits with the other
// shared helpers and may read PP_USAGE, so PP_USAGE is evaluated first.
var window = {};
['data-a1.js', 'data-a2.js', 'data-b1.js', 'data-grammar.js', 'data-verbs.js',
 'data-scenarios.js', 'data-podcasts.js', 'pp-usage.js', 'pp-answer.js', 'pp-distractor.js']
  .forEach(function (f) { (0, eval)(readFile(ROOT + f)); });
var LEVELS = window.PP_LEVELS;
var U = window.PP_USAGE;
var D = window.PP_DISTRACTOR;

// ---------- tiny test framework (same shape as the other suites) ----------
var PASS = 0, FAIL = 0, LOG = [], INFO = [];
function ok(name, cond) { if (cond) { PASS++; } else { FAIL++; LOG.push('FAIL: ' + name); } }
function eq(name, a, b) {
  var sa = JSON.stringify(a), sb = JSON.stringify(b);
  ok(name + (sa === sb ? '' : '  (got ' + sa + ', want ' + sb + ')'), sa === sb);
}
function info(s) { INFO.push('  [info] ' + s); }
function countOf(hay, needle) {
  if (!needle) return 0;
  var n = 0, i = 0;
  while ((i = hay.indexOf(needle, i)) !== -1) { n++; i += needle.length; }
  return n;
}
// Same brace-matching extractor the other index.html suites use.
function bodyOf(src, name) {
  var start = src.indexOf('function ' + name + '(');
  if (start === -1) throw new Error('extract: function ' + name + ' not found in index.html');
  var open = src.indexOf('{', src.indexOf(')', start)), depth = 0;
  for (var j = open; j < src.length; j++) {
    if (src[j] === '{') depth++;
    else if (src[j] === '}') { depth--; if (depth === 0) return src.slice(start, j + 1); }
  }
  throw new Error('extract: unbalanced braces in ' + name);
}
// Comments are prose; a rule must be visible in CODE, not only described.
function codeOnly(s) {
  return s.replace(/\/\*[\s\S]*?\*\//g, ' ').replace(/(^|[^:])\/\/[^\n]*/g, '$1 ');
}
// Whitespace-free view, for source checks whose claim is about TOKENS and their
// order rather than about how the line happens to be typed. Re-indenting a block,
// breaking a long statement over two lines or putting spaces around an `=`
// changes nothing the code does, so none of it may fail a test.
function squash(s) { return s.replace(/\s+/g, ''); }
function hasCode(hay, needle) { return squash(hay).indexOf(squash(needle)) !== -1; }

// ---------- injected randomness ----------
// A seeded shuffle: deterministic, repeatable, and returning a NEW array so a
// mutation of the caller's input would be visible rather than hidden.
function seededShuffle(seed) {
  var state = (seed >>> 0) || 1;
  function next() {                       // mulberry32
    state = (state + 0x6D2B79F5) >>> 0;
    var t = state;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  }
  return function (a) {
    var out = a.slice();
    for (var i = out.length - 1; i > 0; i--) {
      var j = Math.floor(next() * (i + 1));
      var tmp = out[i]; out[i] = out[j]; out[j] = tmp;
    }
    return out;
  };
}
var KEEP = function (a) { return a.slice(); };     // no reordering, still a copy
var SEEDS = [1, 2, 3, 7, 11, 42, 1009];            // the deterministic sweep

function key(s) { return D.normalizeKey(s); }
function labels(built) { return built.options.map(function (o) { return o.label; }); }
function ids(built) { return built.options.map(function (o) { return o.id; }); }
function heardKeyOf(card) { return key(U.mainAudioText(card)); }

// =========================================================================
// A. CORE CONSTRUCTION
// =========================================================================
var A_CORRECT = { id: 's-a-1', pl: 'aaa', en: 'alpha' };
var A_POOL = [
  { c: A_CORRECT, topic: 'T1' },
  { c: { id: 's-a-2', pl: 'bbb', en: 'beta' }, topic: 'T1' },
  { c: { id: 's-a-3', pl: 'ccc', en: 'gamma' }, topic: 'T1' },
  { c: { id: 's-a-4', pl: 'ddd', en: 'delta' }, topic: 'T2' },
  { c: { id: 's-a-5', pl: 'eee', en: 'epsilon' }, topic: 'T2' },
  { c: { id: 's-a-6', pl: 'fff', en: 'zeta' }, topic: 'T3' }
];
function buildA(seed, count) {
  return D.buildOptions({
    correct: A_POOL[0], candidates: A_POOL, count: count || 4,
    shuffle: seed == null ? KEEP : seededShuffle(seed), heardOf: U.mainAudioText
  });
}
(function () {
  var b = buildA(1);
  eq('A1 four options are returned', b.options.length, 4);
  eq('A1 the correct option appears exactly once',
     b.options.filter(function (o) { return o.correct; }).length, 1);
  ok('A1 the returned correct record is the flagged option',
     b.correct && b.correct.correct === true && b.options.indexOf(b.correct) !== -1);
  eq('A1 the correct record carries the correct card id', b.correct.id, 's-a-1');
  eq('A1 the correct label is the correct card gloss', b.correct.label, 'alpha');

  var srcs = b.options.map(function (o) { return o.card; });
  var dupCard = srcs.some(function (c, i) { return srcs.indexOf(c) !== i; });
  ok('A2 no source card appears twice', !dupCard);
  var idList = ids(b);
  ok('A2 no stable id appears twice', idList.every(function (x, i) { return idList.indexOf(x) === i; }));
  var lk = labels(b).map(key);
  ok('A2 English labels are unique after normalisation',
     lk.every(function (x, i) { return lk.indexOf(x) === i; }));
  var hk = b.options.map(function (o) { return heardKeyOf(o.card); });
  ok('A2 heard prompts are unique after normalisation',
     hk.every(function (x, i) { return hk.indexOf(x) === i; }));
  ok('A2 every visible label is non-empty', labels(b).every(function (s) { return !!s; }));

  // Each record keeps its source, so the caller never has to match strings.
  ok('A3 every option keeps its source card',
     b.options.every(function (o) { return o.card && typeof o.card === 'object'; }));
  ok('A3 every option keeps its source pool item',
     b.options.every(function (o) { return A_POOL.indexOf(o.item) !== -1; }));
  ok('A3 exactly one option is flagged correct and it owns the correct card',
     b.options.filter(function (o) { return o.correct; })[0].card === A_CORRECT);

  eq('A4 count is honoured (3)', buildA(1, 3).options.length, 3);
  eq('A4 count is honoured (2)', buildA(1, 2).options.length, 2);
  eq('A4 count 1 returns the correct option alone', labels(buildA(1, 1)), ['alpha']);
  eq('A4 a missing count defaults to four',
     D.buildOptions({ correct: A_POOL[0], candidates: A_POOL, shuffle: KEEP }).options.length, 4);
  eq('A4 a nonsense count falls back to four',
     D.buildOptions({ correct: A_POOL[0], candidates: A_POOL, count: 'x', shuffle: KEEP }).options.length, 4);
  eq('A4 a zero count falls back to four',
     D.buildOptions({ correct: A_POOL[0], candidates: A_POOL, count: 0, shuffle: KEEP }).options.length, 4);
})();

// A5. NOTHING THE CALLER OWNS MAY BE TOUCHED.
(function () {
  var poolSnapshot = JSON.stringify(A_POOL);
  var correctSnapshot = JSON.stringify(A_CORRECT);
  var order = A_POOL.slice();
  SEEDS.forEach(function (s) { buildA(s); });
  eq('A5 the candidate array is not mutated', JSON.stringify(A_POOL), poolSnapshot);
  eq('A5 the candidate array keeps its order', A_POOL.every(function (x, i) { return order[i] === x; }), true);
  eq('A5 the correct card is not mutated', JSON.stringify(A_CORRECT), correctSnapshot);
  ok('A5 no card gained a property',
     A_POOL.every(function (it) {
       return Object.keys(it.c).every(function (k) { return ['id', 'pl', 'en'].indexOf(k) !== -1; });
     }));
  ok('A5 no pool item gained a property',
     A_POOL.every(function (it) {
       return Object.keys(it).every(function (k) { return ['c', 'topic'].indexOf(k) !== -1; });
     }));
  // The returned array is fresh, so a caller shuffling it cannot corrupt the pool.
  var b = buildA(1);
  b.options.push({ label: 'intruder' });
  eq('A5 mutating the result does not reach the pool', A_POOL.length, 6);
})();

// =========================================================================
// B. THE REAL AMBIGUITY DEFECT - one clip must have one true answer
//    Generic fixtures: the shape of the burza pair, none of its words.
// =========================================================================
var B_ONE = { id: 's-b-1', pl: 'zzz', en: 'thing' };
var B_TWIN = { id: 's-b-2', pl: 'zzz', en: '(big) thing' };        // same audio, different gloss
var B_POOL = [
  { c: B_ONE, topic: 'T1' },
  { c: B_TWIN, topic: 'T1' },
  { c: { id: 's-b-3', pl: 'qqq', en: 'other' }, topic: 'T1' },
  { c: { id: 's-b-4', pl: 'www', en: 'another' }, topic: 'T1' },
  { c: { id: 's-b-5', pl: 'rrr', en: 'yet another' }, topic: 'T2' },
  { c: { id: 's-b-6', pl: 'ttt', en: 'one more' }, topic: 'T2' }
];
(function () {
  var sawTwin = 0, sawOne = 0, short = 0;
  SEEDS.forEach(function (s) {
    var fwd = D.buildOptions({ correct: B_POOL[0], candidates: B_POOL, count: 4,
                               shuffle: seededShuffle(s), heardOf: U.mainAudioText });
    var rev = D.buildOptions({ correct: B_POOL[1], candidates: B_POOL, count: 4,
                               shuffle: seededShuffle(s), heardOf: U.mainAudioText });
    if (fwd.options.some(function (o) { return o.card === B_TWIN; })) sawTwin++;
    if (rev.options.some(function (o) { return o.card === B_ONE; })) sawOne++;
    if (fwd.options.length !== 4 || rev.options.length !== 4) short++;
  });
  eq('B1 the same-audio sibling is never offered beside the answer', sawTwin, 0);
  eq('B1 the reverse direction is protected too', sawOne, 0);
  eq('B1 four options are still produced', short, 0);

  // Case and spacing must not smuggle it back in.
  var loud = { id: 's-b-7', pl: '  ZZZ  ', en: 'shouted thing' };
  var b = D.buildOptions({ correct: B_POOL[0], candidates: B_POOL.concat([{ c: loud, topic: 'T1' }]),
                           count: 4, shuffle: KEEP, heardOf: U.mainAudioText });
  ok('B2 a differently-cased/spaced clip counts as the same audio',
     !b.options.some(function (o) { return o.card === loud; }));

  // Punctuation is not audible: "Smacznego!" and "Smacznego" are one clip.
  var bang = { id: 's-b-8', pl: 'zzz!', en: 'punctuated thing' };
  var b2 = D.buildOptions({ correct: B_POOL[0], candidates: B_POOL.concat([{ c: bang, topic: 'T1' }]),
                            count: 4, shuffle: KEEP, heardOf: U.mainAudioText });
  ok('B2 trailing punctuation does not make a new clip',
     !b2.options.some(function (o) { return o.card === bang; }));

  // ...and a genuinely different word still gets in.
  var real = { id: 's-b-9', pl: 'zzy', en: 'different word' };
  var b3 = D.buildOptions({ correct: { c: B_ONE, topic: 'T9' }, candidates: [{ c: real, topic: 'T9' }],
                            count: 2, shuffle: KEEP, heardOf: U.mainAudioText });
  ok('B3 a genuinely different clip is still eligible',
     b3.options.some(function (o) { return o.card === real; }));

  // Diacritics are NOT folded - two Polish words that differ only there are
  // different words the learner is meant to hear apart.
  ok('B3 diacritics are not folded away', key('los') !== key('łos'));
})();

// =========================================================================
// C. DUPLICATE ENGLISH LABELS - the same answer must not be printed twice
// =========================================================================
(function () {
  var CORR = { id: 's-c-1', pl: 'aa', en: 'shared meaning' };
  var TWIN = { id: 's-c-2', pl: 'bb', en: 'Shared   Meaning ' };   // different audio, same answer
  var pool = [
    { c: CORR, topic: 'T1' },
    { c: TWIN, topic: 'T1' },
    { c: { id: 's-c-3', pl: 'cc', en: 'first other' }, topic: 'T1' },
    { c: { id: 's-c-4', pl: 'dd', en: 'second other' }, topic: 'T1' },
    { c: { id: 's-c-5', pl: 'ee', en: 'third other' }, topic: 'T1' }
  ];
  var offenders = 0, missing = 0, dup = 0;
  SEEDS.forEach(function (s) {
    var b = D.buildOptions({ correct: pool[0], candidates: pool, count: 4,
                             shuffle: seededShuffle(s), heardOf: U.mainAudioText });
    if (b.options.some(function (o) { return o.card === TWIN; })) offenders++;
    if (b.options.filter(function (o) { return o.label === 'shared meaning'; }).length !== 1) missing++;
    var lk = labels(b).map(key);
    if (!lk.every(function (x, i) { return lk.indexOf(x) === i; })) dup++;
  });
  eq('C1 a label-twin of the answer is never offered', offenders, 0);
  eq('C1 the correct gloss is printed exactly once', missing, 0);
  eq('C1 no two options read the same', dup, 0);

  // Two DISTRACTORS that share a label must not both get in either.
  var d1 = { id: 's-c-6', pl: 'ff', en: 'same gloss' };
  var d2 = { id: 's-c-7', pl: 'gg', en: 'SAME GLOSS' };
  var pool2 = [{ c: CORR, topic: 'T1' }, { c: d1, topic: 'T1' }, { c: d2, topic: 'T1' }];
  var b2 = D.buildOptions({ correct: pool2[0], candidates: pool2, count: 4, shuffle: KEEP,
                            heardOf: U.mainAudioText });
  eq('C2 two distractors sharing a gloss yield only one', b2.options.length, 2);
  ok('C2 and the answer is still there', b2.options.some(function (o) { return o.correct; }));

  // Punctuation-only differences read as the same answer too ("near / close"
  // beside "near, close" is a coin toss, not a question).
  eq('C3 punctuation-only label differences normalise together',
     key('near / close'), key('near, close'));
  eq('C3 an exclamation mark does not make a new answer',
     key('Enjoy your meal!'), key('enjoy your meal'));
  ok('C3 genuinely different glosses stay different', key('storm') !== key('(thunder)storm'));
})();

// =========================================================================
// C'. AN EARLY PICK MUST NOT COST THE LEARNER AN OPTION
//     Safety is a rule about PAIRS, so filling the question one card at a time
//     and never reconsidering can strand it an option short while a perfectly
//     good combination goes unused. Four candidates, in this order:
//
//       c1  clip k1  gloss "shared"     <- the tempting first pick
//       c2  clip k1  gloss "a"          <- collides with c1 on the CLIP
//       c3  clip k2  gloss "shared"     <- collides with c1 on the GLOSS
//       c4  clip k3  gloss "b"
//
//     Take c1 and two of the remaining three are dead, leaving three buttons.
//     Leave c1 and c2 + c3 + c4 are mutually safe, giving the full four. The
//     builder must find the second answer.
// =========================================================================
(function () {
  var C0 = { id: 'c0', pl: 'k0', en: 'answer' };
  var C1 = { id: 'c1', pl: 'k1', en: 'shared' };
  var C2 = { id: 'c2', pl: 'k1', en: 'a' };
  var C3 = { id: 'c3', pl: 'k2', en: 'shared' };
  var C4 = { id: 'c4', pl: 'k3', en: 'b' };
  var pool = [{ c: C0, topic: 'T' }, { c: C1, topic: 'T' }, { c: C2, topic: 'T' },
              { c: C3, topic: 'T' }, { c: C4, topic: 'T' }];
  var snapshot = JSON.stringify(pool);

  var b = D.buildOptions({ correct: pool[0], candidates: pool, count: 4, shuffle: KEEP,
                           heardOf: U.mainAudioText });
  eq('C4 the full four options are found, not three', b.options.length, 4);
  eq('C4 the correct option appears exactly once',
     b.options.filter(function (o) { return o.correct; }).length, 1);
  ok('C4 the correct option is the correct card',
     b.options.filter(function (o) { return o.correct; })[0].card === C0);
  ok('C4 the blocking candidate is left out',
     !b.options.some(function (o) { return o.card === C1; }));
  ok('C4 the combination that actually fits is used',
     [C2, C3, C4].every(function (c) { return b.options.some(function (o) { return o.card === c; }); }));
  var hk = b.options.map(function (o) { return heardKeyOf(o.card); });
  ok('C4 heard prompts are still unique', hk.every(function (x, i) { return hk.indexOf(x) === i; }));
  var lk = b.options.map(function (o) { return key(o.label); });
  ok('C4 labels are still unique', lk.every(function (x, i) { return lk.indexOf(x) === i; }));

  eq('C4 the result is deterministic', JSON.stringify(ids(b)),
     JSON.stringify(ids(D.buildOptions({ correct: pool[0], candidates: pool, count: 4,
                                         shuffle: KEEP, heardOf: U.mainAudioText }))));
  eq('C4 the pool is not mutated', JSON.stringify(pool), snapshot);

  // The same trap under real shuffling: whichever order the seeds produce, the
  // question is always filled to four and always safe.
  var bad = 0;
  SEEDS.forEach(function (s) {
    var r = D.buildOptions({ correct: pool[0], candidates: pool, count: 4,
                             shuffle: seededShuffle(s), heardOf: U.mainAudioText });
    if (r.options.length !== 4) bad++;
    var h = r.options.map(function (o) { return heardKeyOf(o.card); });
    var l = r.options.map(function (o) { return key(o.label); });
    if (!h.every(function (x, i) { return h.indexOf(x) === i; })) bad++;
    if (!l.every(function (x, i) { return l.indexOf(x) === i; })) bad++;
    if (r.options.filter(function (o) { return o.correct; }).length !== 1) bad++;
  });
  eq('C4 every seed still fills the question safely', bad, 0);

  // Backtracking must not paper over a pool that genuinely cannot fill four:
  // remove c4 and three mutually safe distractors no longer exist.
  var thin = [{ c: C0, topic: 'T' }, { c: C1, topic: 'T' }, { c: C2, topic: 'T' }, { c: C3, topic: 'T' }];
  var b2 = D.buildOptions({ correct: thin[0], candidates: thin, count: 4, shuffle: KEEP,
                            heardOf: U.mainAudioText });
  eq('C5 an honestly short pool still returns the honest maximum', b2.options.length, 3);
  eq('C5 and it is the largest safe set that exists',
     1 + Math.min(3, mutuallySafeCapacity({ c: C0, topic: 'T' }, thin, 3)), 3);
})();

// C6. The same claim, made generally rather than on one hand-built trap.
//     Pools are generated deterministically with heavy key reuse - exactly the
//     shape that strands a one-pass picker - and the builder's option count is
//     compared against the independent capacity oracle for several requested
//     counts. Any pool where a better combination existed shows up here.
(function () {
  var CLIPS = ['h1', 'h2', 'h3', 'h4'];          // few clips, many cards -> collisions
  var GLOSS = ['g1', 'g2', 'g3', 'g4'];
  var mismatches = [], checked = 0, shapes = 0, filled = {};
  for (var seed = 1; seed <= 60; seed++) {
    var rnd = seededShuffle(seed);
    var size = 2 + (seed % 7);
    // Deterministic pseudo-assignment of clips and glosses from the seed.
    var order = rnd([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]);
    var pool = [{ c: { id: 'p-' + seed + '-0', pl: 'answer clip', en: 'answer gloss' }, topic: 'T' }];
    for (var i = 0; i < size; i++) {
      var pick = order[i % order.length];
      pool.push({ c: { id: 'p-' + seed + '-' + (i + 1),
                       pl: CLIPS[pick % CLIPS.length],
                       en: GLOSS[(pick + (i % 3)) % GLOSS.length] },
                  topic: i % 2 ? 'T' : 'OTHER' });
    }
    shapes++;
    [1, 2, 3, 4].forEach(function (count) {
      SEEDS.slice(0, 3).forEach(function (s) {
        checked++;
        var built = D.buildOptions({ correct: pool[0], candidates: pool, count: count,
                                     shuffle: seededShuffle(s), heardOf: U.mainAudioText });
        var room = mutuallySafeCapacity(pool[0], pool, count - 1);
        var want = 1 + Math.min(count - 1, room);
        filled[built.options.length] = (filled[built.options.length] || 0) + 1;
        if (built.options.length !== want) {
          mismatches.push('seed' + seed + '/count' + count + '/shuffle' + s +
                          ' got ' + built.options.length + ' want ' + want);
        }
        // ...and whatever it returned is still safe.
        var h = built.options.map(function (o) { return heardKeyOf(o.card); });
        var l = built.options.map(function (o) { return key(o.label); });
        if (!h.every(function (x, i2) { return h.indexOf(x) === i2; })) mismatches.push('dup clip seed' + seed);
        if (!l.every(function (x, i2) { return l.indexOf(x) === i2; })) mismatches.push('dup gloss seed' + seed);
        if (built.options.filter(function (o) { return o.correct; }).length !== 1) mismatches.push('answer seed' + seed);
      });
    });
  }
  info('collision-heavy synthetic pools: ' + shapes + ' shapes, ' + checked +
       ' builds, option counts seen -> ' +
       Object.keys(filled).sort().map(function (k) { return k + ':' + filled[k]; }).join(' '));
  eq('C6 the builder always returns the independently computed maximum',
     mismatches.slice(0, 5), []);
  ok('C6 the sweep really exercised short results as well as full ones',
     Object.keys(filled).length > 1);
})();

// C7. A SHORT ANSWER MUST BE THE POOL'S FAULT, NOT THE SEARCH'S
//     The search has to be exhaustive, because "three options" has to mean one
//     thing only: this pool holds no fourth safe card. A search that stops after
//     N steps and reports what it has produces the identical output for a pool
//     that was merely slow to work through, and the learner cannot tell the two
//     apart - nor can anyone reading the code.
//
//     This pool is built to look hopeless for a long time and then not be. A
//     long run of blockers all share one clip AND one gloss, so they are
//     mutually exclusive and can each pair with at most one useful card; only
//     after all of them do the three cards that actually fit together appear:
//
//       210 blockers   clip hc   gloss B      mutually exclusive; block s1 (gloss
//                                             B) and s2 (clip hc); fit only s3
//       s1             clip h1   gloss B
//       s2             clip hc   gloss C
//       s3             clip h3   gloss D
//
//     s1 + s2 + s3 are mutually safe, so the honest answer is four options. Any
//     early cutoff returns three and calls the pool short.
// =========================================================================
(function () {
  var BLOCKERS = 210;
  var C0 = { id: 'c0', pl: 'p0', en: 'answer' };
  var S1 = { id: 's1', pl: 'h1', en: 'B' };
  var S2 = { id: 's2', pl: 'hc', en: 'C' };
  var S3 = { id: 's3', pl: 'h3', en: 'D' };
  var pool = [{ c: C0, topic: 'T' }];
  for (var i = 0; i < BLOCKERS; i++) {
    pool.push({ c: { id: 'blk-' + i, pl: 'hc', en: 'B' }, topic: 'T' });
  }
  pool.push({ c: S1, topic: 'T' }, { c: S2, topic: 'T' }, { c: S3, topic: 'T' });
  var snapshot = JSON.stringify(pool);

  // The oracle agrees the pool really can fill the question.
  eq('C7 three mutually safe distractors genuinely exist',
     mutuallySafeCapacity(pool[0], pool, 3), 3);

  var threw = false, b = null;
  try {
    b = D.buildOptions({ correct: pool[0], candidates: pool, count: 4, shuffle: KEEP,
                         heardOf: U.mainAudioText });
  } catch (e) { threw = true; }
  ok('C7 the search completes rather than giving up', !threw && !!b);
  eq('C7 the full four options are returned past 210 blockers', b.options.length, 4);
  eq('C7 the correct option appears exactly once',
     b.options.filter(function (o) { return o.correct; }).length, 1);
  ok('C7 the correct option is the correct card',
     b.options.filter(function (o) { return o.correct; })[0].card === C0);
  eq('C7 the three cards that fit together are all used', ids(b).sort(),
     ['c0', 's1', 's2', 's3']);
  ok('C7 no blocking candidate is offered',
     !b.options.some(function (o) { return o.id.indexOf('blk-') === 0; }));
  var hk = b.options.map(function (o) { return heardKeyOf(o.card); });
  ok('C7 heard prompts are unique', hk.every(function (x, i2) { return hk.indexOf(x) === i2; }));
  var lk = b.options.map(function (o) { return key(o.label); });
  ok('C7 labels are unique', lk.every(function (x, i2) { return lk.indexOf(x) === i2; }));

  eq('C7 the result is deterministic', JSON.stringify(ids(b)),
     JSON.stringify(ids(D.buildOptions({ correct: pool[0], candidates: pool, count: 4,
                                         shuffle: KEEP, heardOf: U.mainAudioText }))));
  eq('C7 the pool is not mutated', JSON.stringify(pool), snapshot);
  eq('C7 the pool keeps its length', pool.length, BLOCKERS + 4);

  // Shuffling moves the useful cards anywhere in the order; the answer is the
  // same because the search is exhaustive, not order-lucky.
  var bad = 0;
  SEEDS.forEach(function (s) {
    var r = D.buildOptions({ correct: pool[0], candidates: pool, count: 4,
                             shuffle: seededShuffle(s), heardOf: U.mainAudioText });
    if (r.options.length !== 4) bad++;
    if (r.options.some(function (o) { return o.id.indexOf('blk-') === 0; })) bad++;
  });
  eq('C7 every shuffle still finds the combination', bad, 0);

  // Growing the haystack must not change the answer either.
  var bigger = [{ c: C0, topic: 'T' }];
  for (var j = 0; j < BLOCKERS * 5; j++) {
    bigger.push({ c: { id: 'big-' + j, pl: 'hc', en: 'B' }, topic: 'T' });
  }
  bigger.push({ c: S1, topic: 'T' }, { c: S2, topic: 'T' }, { c: S3, topic: 'T' });
  var b2 = D.buildOptions({ correct: bigger[0], candidates: bigger, count: 4, shuffle: KEEP,
                            heardOf: U.mainAudioText });
  eq('C7 five times the blockers changes nothing', ids(b2).sort(), ['c0', 's1', 's2', 's3']);
})();

// C8. ...and the production source must not have grown a cutoff back.
(function () {
  var SRC = DISTRACTOR_SRC, CODE = codeOnly(DISTRACTOR_SRC);
  ok('C8 SEARCH_BUDGET is gone from pp-distractor.js', SRC.indexOf('SEARCH_BUDGET') === -1);
  ok('C8 no step budget of any name survives in the code',
     CODE.toLowerCase().indexOf('budget') === -1 && CODE.toLowerCase().indexOf('maxsteps') === -1 &&
     CODE.indexOf('steps') === -1 && CODE.indexOf('cutoff') === -1);
  // ...and the documentation no longer PROMISES less than the maximum. This
  // checks the claims, not the vocabulary: saying "there is no approximation"
  // is the contract being asserted, so the word itself is not what matters.
  var LOW = SRC.toLowerCase();
  ['theoretical best', 'one short of', 'may be one short', 'best effort',
   'approximate result', 'stops after'].forEach(function (p) {
    ok('C8 the documentation no longer promises "' + p + '"', LOW.indexOf(p) === -1);
  });
  ok('C8 the documentation states the search is exact',
     LOW.indexOf('exact') !== -1 || LOW.indexOf('exhaustive') !== -1);
  ok('C8 the documentation says a short result is the pool\'s doing',
     LOW.indexOf('no larger safe set exists') !== -1 ||
     LOW.indexOf('no larger mutually safe set exists') !== -1);
})();

// =========================================================================
// D. SAME-TOPIC PRIORITY - plausible neighbours first, safety first of all
// =========================================================================
(function () {
  var CORR = { id: 's-d-1', pl: 'p1', en: 'answer' };
  var pool = [
    { c: CORR, topic: 'HOME' },
    { c: { id: 's-d-2', pl: 'p2', en: 'near one' }, topic: 'HOME' },
    { c: { id: 's-d-3', pl: 'p3', en: 'near two' }, topic: 'HOME' },
    { c: { id: 's-d-4', pl: 'p4', en: 'near three' }, topic: 'HOME' },
    { c: { id: 's-d-5', pl: 'p5', en: 'far one' }, topic: 'AWAY' },
    { c: { id: 's-d-6', pl: 'p6', en: 'far two' }, topic: 'AWAY' }
  ];
  var leaked = 0;
  SEEDS.forEach(function (s) {
    var b = D.buildOptions({ correct: pool[0], candidates: pool, count: 4,
                             shuffle: seededShuffle(s), heardOf: U.mainAudioText });
    if (b.options.some(function (o) { return o.topic === 'AWAY'; })) leaked++;
  });
  eq('D1 a topic with enough safe cards never reaches outside itself', leaked, 0);

  // Not enough safe neighbours -> the wider pool fills the remaining places.
  var thin = [
    { c: CORR, topic: 'HOME' },
    { c: { id: 's-d-7', pl: 'p7', en: 'only neighbour' }, topic: 'HOME' },
    { c: { id: 's-d-8', pl: 'p8', en: 'far A' }, topic: 'AWAY' },
    { c: { id: 's-d-9', pl: 'p9', en: 'far B' }, topic: 'AWAY' }
  ];
  var b2 = D.buildOptions({ correct: thin[0], candidates: thin, count: 4, shuffle: KEEP,
                            heardOf: U.mainAudioText });
  eq('D2 the wider pool fills the gap', b2.options.length, 4);
  ok('D2 the lone safe neighbour is included',
     b2.options.some(function (o) { return o.id === 's-d-7'; }));
  eq('D2 both outside cards were needed',
     b2.options.filter(function (o) { return o.topic === 'AWAY'; }).length, 2);

  // An UNSAFE same-topic card is skipped, not preferred: safety outranks topic.
  var trap = [
    { c: CORR, topic: 'HOME' },
    { c: { id: 's-d-10', pl: 'p1', en: 'same clip as the answer' }, topic: 'HOME' },
    { c: { id: 's-d-11', pl: 'p11', en: 'Answer' }, topic: 'HOME' },
    { c: { id: 's-d-12', pl: 'p12', en: 'far C' }, topic: 'AWAY' },
    { c: { id: 's-d-13', pl: 'p13', en: 'far D' }, topic: 'AWAY' },
    { c: { id: 's-d-14', pl: 'p14', en: 'far E' }, topic: 'AWAY' }
  ];
  var skipped = 0, sized = 0;
  SEEDS.forEach(function (s) {
    var b = D.buildOptions({ correct: trap[0], candidates: trap, count: 4,
                             shuffle: seededShuffle(s), heardOf: U.mainAudioText });
    if (b.options.some(function (o) { return o.id === 's-d-10' || o.id === 's-d-11'; })) skipped++;
    if (b.options.length !== 4) sized++;
  });
  eq('D3 an unsafe same-topic card is skipped, never preferred', skipped, 0);
  eq('D3 the round is still filled from outside the topic', sized, 0);

  // Backtracking inside the topic. HOME leads with a card that blocks two of
  // its own neighbours; there is no wider pool to fall back on, so the only way
  // to fill the question is to give that card up.
  var blocked = [
    { c: CORR, topic: 'HOME' },
    { c: { id: 's-d-20', pl: 'q1', en: 'twin gloss' }, topic: 'HOME' },   // blocks the next two
    { c: { id: 's-d-21', pl: 'q1', en: 'home a' }, topic: 'HOME' },       // same clip as s-d-20
    { c: { id: 's-d-22', pl: 'q2', en: 'twin gloss' }, topic: 'HOME' },   // same gloss as s-d-20
    { c: { id: 's-d-23', pl: 'q3', en: 'home b' }, topic: 'HOME' }
  ];
  var b3 = D.buildOptions({ correct: blocked[0], candidates: blocked, count: 4, shuffle: KEEP,
                            heardOf: U.mainAudioText });
  eq('D5 the topic still fills the question', b3.options.length, 4);
  ok('D5 it never left the topic', b3.options.every(function (o) { return o.topic === 'HOME'; }));
  ok('D5 the blocking neighbour is the one given up',
     !b3.options.some(function (o) { return o.id === 's-d-20'; }));
  eq('D5 the combination that fits is the one used', ids(b3).sort(),
     ['s-d-1', 's-d-21', 's-d-22', 's-d-23']);

  // ...and when a wider pool IS available, the documented ordering still wins:
  // the search returns the FIRST complete combination in near-then-far order.
  // Keeping the blocker here costs nothing - the question still fills to four -
  // so it is kept, and one far card comes along to complete the set. That is
  // the specified rule, not an accident: earlier candidates are preferred, and
  // a candidate is only abandoned when keeping it would cost an option.
  var withFar = blocked.concat([
    { c: { id: 's-d-24', pl: 'q4', en: 'away a' }, topic: 'AWAY' },
    { c: { id: 's-d-25', pl: 'q5', en: 'away b' }, topic: 'AWAY' }
  ]);
  var b4 = D.buildOptions({ correct: withFar[0], candidates: withFar, count: 4, shuffle: KEEP,
                            heardOf: U.mainAudioText });
  eq('D6 the question is still filled to four', b4.options.length, 4);
  eq('D6 the first complete combination in order is returned', ids(b4).sort(),
     ['s-d-1', 's-d-20', 's-d-23', 's-d-24']);
  ok('D6 same-topic candidates are still the majority',
     b4.options.filter(function (o) { return o.topic === 'HOME'; }).length === 3);
  var hk6 = b4.options.map(function (o) { return heardKeyOf(o.card); });
  var lk6 = b4.options.map(function (o) { return key(o.label); });
  ok('D6 and the result is safe',
     hk6.every(function (x, i) { return hk6.indexOf(x) === i; }) &&
     lk6.every(function (x, i) { return lk6.indexOf(x) === i; }));

  // A pool item with no topic, and a raw card with a topic field, both work.
  var raw = D.buildOptions({
    correct: { id: 's-d-15', pl: 'p15', en: 'raw answer', topic: 'HOME' },
    candidates: [{ id: 's-d-16', pl: 'p16', en: 'raw near', topic: 'HOME' },
                 { id: 's-d-17', pl: 'p17', en: 'raw far', topic: 'AWAY' }],
    count: 2, shuffle: KEEP, heardOf: U.mainAudioText
  });
  ok('D4 raw cards are accepted and their topic respected',
     raw.options.length === 2 && raw.options.some(function (o) { return o.id === 's-d-16'; }));
})();

// =========================================================================
// E. DETERMINISTIC RANDOMNESS - the module never reaches for randomness itself
// =========================================================================
(function () {
  function run(seed) { return JSON.stringify(labels(buildA(seed))); }
  eq('E1 the same seed gives the same options twice', run(42), run(42));
  eq('E1 the same seed gives the same options a third time', run(1009), run(1009));
  var distinct = {};
  SEEDS.forEach(function (s) { distinct[run(s)] = true; });
  ok('E2 different seeds can produce different safe output', Object.keys(distinct).length > 1);
  // ...but every one of them is still safe.
  var bad = 0;
  SEEDS.forEach(function (s) {
    var b = buildA(s);
    var lk = labels(b).map(key);
    if (b.options.length !== 4) bad++;
    if (b.options.filter(function (o) { return o.correct; }).length !== 1) bad++;
    if (!lk.every(function (x, i) { return lk.indexOf(x) === i; })) bad++;
  });
  eq('E2 every seed produces a safe set', bad, 0);

  // With no shuffle injected the builder must still work, deterministically.
  var plain = D.buildOptions({ correct: A_POOL[0], candidates: A_POOL, count: 4, heardOf: U.mainAudioText });
  eq('E3 no injected shuffle still returns four options', plain.options.length, 4);
  eq('E3 no injected shuffle is deterministic', JSON.stringify(labels(plain)),
     JSON.stringify(labels(D.buildOptions({ correct: A_POOL[0], candidates: A_POOL, count: 4,
                                            heardOf: U.mainAudioText }))));

  var CODE = codeOnly(DISTRACTOR_SRC);
  ok('E4 pp-distractor.js never calls Math.random', CODE.indexOf('Math.random') === -1);
  ok('E4 pp-distractor.js never reads Date.now', CODE.indexOf('Date.now') === -1);
  ok('E4 pp-distractor.js touches no DOM', CODE.indexOf('document') === -1);
  ok('E4 pp-distractor.js touches no storage', CODE.indexOf('localStorage') === -1 &&
                                               CODE.indexOf('sessionStorage') === -1);
  // It may NAME the audio rule (PP_USAGE.mainAudioText) - it must never play it.
  ok('E4 pp-distractor.js plays no audio',
     CODE.indexOf('new Audio') === -1 && CODE.indexOf('speechSynthesis') === -1 &&
     CODE.indexOf('.play(') === -1 && CODE.indexOf('speakCard') === -1);
  ok('E4 pp-distractor.js reads no app state',
     CODE.indexOf('LEVELS') === -1 && CODE.indexOf('poolFor') === -1);
  ok('E4 the shuffle is injected, not imported', DISTRACTOR_SRC.indexOf('shuffle') !== -1);
})();

// =========================================================================
// F. SMALL AND MALFORMED POOLS - degrade honestly, never throw
// =========================================================================
(function () {
  var CORR = { id: 's-f-1', pl: 'f1', en: 'answer' };
  // Fewer than three safe distractors -> a smaller, honest set.
  var tiny = [{ c: CORR, topic: 'T' }, { c: { id: 's-f-2', pl: 'f2', en: 'only' }, topic: 'T' }];
  var b = D.buildOptions({ correct: tiny[0], candidates: tiny, count: 4, shuffle: KEEP,
                           heardOf: U.mainAudioText });
  eq('F1 a thin pool returns a smaller safe set', b.options.length, 2);
  eq('F1 the answer is present exactly once',
     b.options.filter(function (o) { return o.correct; }).length, 1);

  var alone = D.buildOptions({ correct: { c: CORR, topic: 'T' }, candidates: [], count: 4,
                               shuffle: KEEP, heardOf: U.mainAudioText });
  eq('F1 an empty pool returns the answer alone', labels(alone), ['answer']);
  eq('F1 and it is flagged correct', alone.options[0].correct, true);

  // Padding with an unsafe card to reach four is exactly what must NOT happen.
  var unsafeOnly = [
    { c: CORR, topic: 'T' },
    { c: { id: 's-f-3', pl: 'f1', en: 'same clip' }, topic: 'T' },
    { c: { id: 's-f-4', pl: 'f4', en: 'ANSWER' }, topic: 'T' }
  ];
  var b2 = D.buildOptions({ correct: unsafeOnly[0], candidates: unsafeOnly, count: 4, shuffle: KEEP,
                            heardOf: U.mainAudioText });
  eq('F2 an unsafe card is never used as padding', b2.options.length, 1);
  eq('F2 the learner is left with the answer alone', labels(b2), ['answer']);

  // Malformed input must be skipped, silently and without throwing.
  var junk = [
    { c: CORR, topic: 'T' },
    null,
    undefined,
    { c: null, topic: 'T' },
    { c: { id: 's-f-5', pl: 'f5', en: '' }, topic: 'T' },            // no gloss
    { c: { id: 's-f-6', pl: 'f6', en: '   ' }, topic: 'T' },         // blank gloss
    { c: { id: 's-f-7', pl: '', en: 'no clip' }, topic: 'T' },       // nothing to hear
    { c: { id: 's-f-8', en: 'missing pl' }, topic: 'T' },
    { c: { id: 's-f-9', pl: 'f9' }, topic: 'T' },                    // missing en
    { c: { id: 's-f-10', pl: 'f10', en: 'good one' }, topic: 'T' },
    { c: { id: 's-f-11', pl: 'f11', en: 'good two' }, topic: 'T' },
    { c: { id: 's-f-12', pl: 'f12', en: 'good three' }, topic: 'T' }
  ];
  var threw = false, b3 = null;
  try {
    b3 = D.buildOptions({ correct: junk[0], candidates: junk, count: 4, shuffle: KEEP,
                          heardOf: U.mainAudioText });
  } catch (e) { threw = true; }
  ok('F3 malformed candidates do not throw', !threw);
  eq('F3 only the usable cards were taken', labels(b3).sort(),
     ['answer', 'good one', 'good three', 'good two']);

  // A malformed CORRECT item degrades to an empty, non-throwing result. There
  // is no such thing as a half-formed question: a card the learner cannot read
  // OR cannot hear is not one that can be asked, so all three requirements -
  // a card, a gloss, a heard prompt - fail the same way.
  var edge = [
    ['null correct', null, null],
    ['undefined correct', undefined, null],
    ['correct with no card', { c: null, topic: 'T' }, null],
    ['correct with no gloss', { c: { id: 's-f-30', pl: 'f30', en: '' }, topic: 'T' }, null],
    ['correct with a blank gloss', { c: { id: 's-f-31', pl: 'f31', en: '   ' }, topic: 'T' }, null],
    ['correct with an empty pl', { c: { id: 's-f-32', pl: '', en: 'unplayable' }, topic: 'T' }, null],
    ['correct with a whitespace-only pl', { c: { id: 's-f-33', pl: '   \t\n ', en: 'unplayable' }, topic: 'T' }, null],
    ['correct with a punctuation-only pl', { c: { id: 's-f-34', pl: '!!!', en: 'unplayable' }, topic: 'T' }, null],
    ['correct with no pl at all', { c: { id: 's-f-35', en: 'unplayable' }, topic: 'T' }, null],
    // The rule follows the INJECTED heard rule, not the `pl` field: a caller
    // whose heardOf returns nothing has no clip to play whatever `pl` says.
    ['correct whose injected heardOf returns empty',
     { c: { id: 's-f-36', pl: 'looks playable', en: 'silent' }, topic: 'T' },
     function () { return ''; }],
    ['correct whose injected heardOf returns whitespace',
     { c: { id: 's-f-37', pl: 'looks playable', en: 'silent' }, topic: 'T' },
     function () { return '  '; }],
    ['correct whose injected heardOf returns a non-string',
     { c: { id: 's-f-38', pl: 'looks playable', en: 'silent' }, topic: 'T' },
     function () { return null; }]
  ];
  edge.forEach(function (row) {
    var t = false, r = null;
    try {
      r = D.buildOptions({ correct: row[1], candidates: junk, count: 4, shuffle: KEEP,
                           heardOf: row[2] || U.mainAudioText });
    } catch (e) { t = true; }
    ok('F4 ' + row[0] + ' does not throw', !t);
    ok('F4 ' + row[0] + ' returns nothing to answer', r && r.options.length === 0 && r.correct === null);
  });
  // A template is the real card shape behind that guard: PP_USAGE gives it no
  // main audio, so it can never become a question even if a caller offers it.
  var template = { id: 's-f-39', pl: 'Gdzie jest...?', en: 'Where is...?', cardType: 'template' };
  eq('F4 a template has no heard prompt to answer from', U.mainAudioText(template), '');
  var tpl = D.buildOptions({ correct: { c: template, topic: 'T' }, candidates: junk, count: 4,
                             shuffle: KEEP, heardOf: U.mainAudioText });
  ok('F4 a template is never turned into a question',
     tpl.options.length === 0 && tpl.correct === null);

  // The guard is fatal to the QUESTION, never merely to one option: a valid
  // card with the same pool still builds normally.
  var stillFine = D.buildOptions({ correct: junk[0], candidates: junk, count: 4, shuffle: KEEP,
                                   heardOf: U.mainAudioText });
  eq('F4 a valid correct card is unaffected by the guard', stillFine.options.length, 4);

  var t2 = false;
  try { D.buildOptions(); D.buildOptions({}); D.buildOptions({ correct: A_POOL[0] }); } catch (e) { t2 = true; }
  ok('F4 a missing spec does not throw', !t2);

  // Cards with NO stable id are handled without creating duplicates: identity
  // then falls back to the object itself plus the two normalised keys.
  var nid1 = { pl: 'n1', en: 'no id one' };
  var nid2 = { pl: 'n2', en: 'no id two' };
  var nidPool = [
    { c: { pl: 'n0', en: 'idless answer' }, topic: 'T' },
    { c: nid1, topic: 'T' }, { c: nid1, topic: 'T' },     // literally the same card twice
    { c: nid2, topic: 'T' }
  ];
  var b4 = D.buildOptions({ correct: nidPool[0], candidates: nidPool, count: 4, shuffle: KEEP,
                            heardOf: U.mainAudioText });
  eq('F5 id-less cards still de-duplicate by object and by key', labels(b4).sort(),
     ['idless answer', 'no id one', 'no id two']);
  eq('F5 the empty id is not treated as a shared id',
     b4.options.filter(function (o) { return o.id === ''; }).length, 3);

  // A candidate that IS the answer, by object or by id, is never offered back.
  var selfPool = [
    { c: CORR, topic: 'T' },
    { c: CORR, topic: 'T' },                                       // same object
    { c: { id: 's-f-1', pl: 'other clip', en: 'other gloss' }, topic: 'T' },   // same id
    { c: { id: 's-f-20', pl: 'f20', en: 'fine' }, topic: 'T' }
  ];
  var b5 = D.buildOptions({ correct: selfPool[0], candidates: selfPool, count: 4, shuffle: KEEP,
                            heardOf: U.mainAudioText });
  eq('F6 the answer is not offered back as its own distractor', labels(b5).sort(), ['answer', 'fine']);

  // normalizeKey is total: it never throws and never returns a non-string.
  var vals = [null, undefined, 0, 1, {}, [], true, '', '   ', '!!!', 'A  B'];
  var okAll = vals.every(function (v) { return typeof D.normalizeKey(v) === 'string'; });
  ok('F7 normalizeKey always returns a string', okAll);
  eq('F7 normalizeKey collapses and trims', D.normalizeKey('  A   B  '), 'a b');
  eq('F7 normalizeKey drops punctuation-only text', D.normalizeKey('!!!'), '');
  eq('F7 normalizeKey keeps Polish letters', D.normalizeKey('Żał'), 'żał');
})();

// =========================================================================
// G. THE CURRENT CORPUS - discovered, reported, and swept
// =========================================================================
var VOCAB_SRC = LEVELS.filter(function (lv) {
  return lv.topics.length && lv.topics.every(function (t) { return !t.kind; });
});
// poolFor() from index.html, reproduced exactly, so "the Listening pool" here
// means what it means in production.
function poolFor(srcLevels, activity) {
  var out = [];
  VOCAB_SRC.filter(function (lv) { return !srcLevels || srcLevels.indexOf(lv.level) !== -1; })
    .forEach(function (lv) {
      lv.topics.forEach(function (t) {
        if (t.mature) return;
        t.cards.forEach(function (c) {
          if (U.eligibleFor(c, activity)) out.push({ c: c, topic: t.name, level: lv.level });
        });
      });
    });
  return out;
}
var ALL_POOL = poolFor(null, 'listen');
var POOLS = VOCAB_SRC.map(function (lv) { return { name: lv.level, src: [lv.level], items: poolFor([lv.level], 'listen') }; });
POOLS.push({ name: 'All levels', src: null, items: ALL_POOL });

// Group a pool by heard prompt; a GROUP is a collision only when its members
// would print more than one different answer.
function collisionGroups(items) {
  var m = Object.create(null);
  items.forEach(function (it) {
    var k = heardKeyOf(it.c);
    if (!k) return;
    (m[k] || (m[k] = [])).push(it);
  });
  return Object.keys(m).sort().filter(function (k) {
    if (m[k].length < 2) return false;
    var seen = Object.create(null), n = 0;
    m[k].forEach(function (it) { var e = key(it.c.en); if (!seen[e]) { seen[e] = 1; n++; } });
    return n > 1;
  }).map(function (k) { return { key: k, members: m[k] }; });
}

// ---------- how many distractors COULD this question honestly have? ----------
// An independent second opinion, deliberately not built on buildOptions: asking
// the thing under test how many options it should have produced would assert
// nothing at all. This applies the documented rules directly and searches with
// backtracking for the largest set of candidates that can coexist:
//
//   - a different source object from the answer, and from each other;
//   - a different stable id, where ids exist;
//   - a usable, unique normalised English label, never the answer's;
//   - a usable, unique normalised heard prompt, never the answer's.
//
// It stops as soon as `want` is reached, so the usual case costs three picks.
// The shared normalisation (normalizeKey) is the RULE, not the implementation -
// re-deriving it here would only test that two copies of a regex agree.
function mutuallySafeCapacity(correctItem, items, want) {
  var cCard = correctItem && correctItem.c;
  if (!cCard) return 0;
  var cLabel = key(cCard.en), cHeard = heardKeyOf(cCard), cId = cCard.id || '';
  if (!cLabel || !cHeard) return 0;

  var cands = [];
  items.forEach(function (it) {
    var card = it && it.c;
    if (!card || card === cCard) return;
    if (cId && card.id === cId) return;
    var l = key(card.en), h = heardKeyOf(card);
    if (!l || !h || l === cLabel || h === cHeard) return;
    cands.push({ card: card, l: l, h: h, id: card.id || '' });
  });

  var chosen = [], best = 0;
  function fits(cand) {
    for (var i = 0; i < chosen.length; i++) {
      if (chosen[i].card === cand.card) return false;
      if (chosen[i].l === cand.l) return false;
      if (chosen[i].h === cand.h) return false;
      if (cand.id && chosen[i].id === cand.id) return false;
    }
    return true;
  }
  function search(start) {
    if (chosen.length > best) best = chosen.length;
    if (best >= want) return true;                 // enough is enough
    for (var i = start; i < cands.length; i++) {
      if (!fits(cands[i])) continue;
      chosen.push(cands[i]);
      if (search(i + 1)) return true;
      chosen.pop();
    }
    return false;
  }
  search(0);
  return best;
}
// Prove the helper on fixtures whose answer is known by inspection, so a bug in
// the yardstick cannot quietly excuse a bug in the builder.
(function () {
  var C = { id: 'cap-0', pl: 'k0', en: 'answer' };
  function it(id, pl, en) { return { c: { id: id, pl: pl, en: en }, topic: 'T' }; }
  var corr = { c: C, topic: 'T' };
  eq('G-cap an empty pool has no capacity', mutuallySafeCapacity(corr, [], 3), 0);
  eq('G-cap three distinct cards give three',
     mutuallySafeCapacity(corr, [it('c1', 'k1', 'one'), it('c2', 'k2', 'two'), it('c3', 'k3', 'three')], 3), 3);
  eq('G-cap a same-audio sibling does not count',
     mutuallySafeCapacity(corr, [it('c1', 'k0', 'other name for the answer'),
                                 it('c2', 'k2', 'two'), it('c3', 'k3', 'three')], 3), 2);
  eq('G-cap a same-label card does not count',
     mutuallySafeCapacity(corr, [it('c1', 'k1', 'ANSWER'), it('c2', 'k2', 'two'), it('c3', 'k3', 'three')], 3), 2);
  eq('G-cap candidates that clash with EACH OTHER do not both count',
     mutuallySafeCapacity(corr, [it('c1', 'k1', 'dup'), it('c2', 'k2', 'DUP'),
                                 it('c3', 'k3', 'three'), it('c4', 'k4', 'four')], 3), 3);
  eq('G-cap a pool of mutual clashes collapses to one',
     mutuallySafeCapacity(corr, [it('c1', 'k1', 'same'), it('c2', 'k2', 'same'), it('c3', 'k3', 'same')], 3), 1);
  eq('G-cap backtracking finds a set a greedy first pick would miss',
     mutuallySafeCapacity(corr, [it('c1', 'k1', 'shared'), it('c2', 'k1', 'a'),
                                 it('c3', 'k2', 'shared'), it('c4', 'k3', 'b')], 3), 3);
  eq('G-cap an unusable answer has no capacity',
     mutuallySafeCapacity({ c: { id: 'x', pl: '', en: 'no clip' }, topic: 'T' }, [it('c1', 'k1', 'one')], 3), 0);
})();

var ALL_GROUPS = collisionGroups(ALL_POOL);
var SAME_LEVEL_GROUPS = [];
POOLS.filter(function (p) { return p.src; }).forEach(function (p) {
  collisionGroups(p.items).forEach(function (g) { SAME_LEVEL_GROUPS.push({ level: p.name, g: g }); });
});

info('Listening pool: All levels ' + ALL_POOL.length + ' · ' +
     POOLS.filter(function (p) { return p.src; })
          .map(function (p) { return p.name + ' ' + p.items.length; }).join(' · '));
info('duplicate-heard-prompt groups reachable in All Levels: ' + ALL_GROUPS.length);
info('groups live inside a SINGLE-level pool: ' + SAME_LEVEL_GROUPS.length +
     ' -> ' + SAME_LEVEL_GROUPS.map(function (x) { return x.level + ':' + x.g.key; }).join(', '));
ALL_GROUPS.forEach(function (g) {
  info('  group "' + g.key + '": ' + g.members.map(function (m) {
    return m.c.id + ' [' + m.level + ' / ' + m.topic + '] pl="' + m.c.pl + '" en="' + m.c.en + '"';
  }).join('  |  '));
});
// Both counts are REPORTED above and deliberately not asserted - not even as
// "greater than zero". The collisions are a property of the authored corpus,
// not of this builder: an editor who reworded the last duplicate gloss would
// have improved the data, and a suite that failed for it would be punishing the
// fix. Every sweep below is driven by the discovered set, so a corpus with no
// collisions left runs them zero times and passes, while the synthetic
// contract tests in sections A-F keep proving the rule regardless.

// Every discovered group, in every pool that can reach it, from both directions.
(function () {
  var offences = [], checked = 0;
  POOLS.forEach(function (p) {
    collisionGroups(p.items).forEach(function (g) {
      g.members.forEach(function (mine) {
        SEEDS.forEach(function (s) {
          checked++;
          var b = D.buildOptions({ correct: mine, candidates: p.items, count: 4,
                                   shuffle: seededShuffle(s), heardOf: U.mainAudioText });
          g.members.forEach(function (other) {
            if (other.c === mine.c) return;
            if (b.options.some(function (o) { return o.card === other.c; })) {
              offences.push(p.name + '/' + g.key + '/' + mine.c.id + ' offered ' + other.c.id + ' (seed ' + s + ')');
            }
          });
        });
      });
    });
  });
  info('duplicate-audio questions built and checked: ' + checked);
  eq('G1 no duplicate-audio sibling is ever offered beside its twin', offences.slice(0, 5), []);
})();

// Named regressions for the groups the audit called out - asserted ONLY for the
// ones that independently exist in the corpus inspected on this run.
(function () {
  var WATCH = ['burza', 'upał', 'skóra', 'ubranie', 'kanapa', 'awaria', 'do zobaczenia'];
  var byKey = {};
  ALL_GROUPS.forEach(function (g) { byKey[g.key] = g; });
  var found = [];
  WATCH.forEach(function (w) {
    var g = byKey[key(w)];
    if (!g) { info('watched group "' + w + '" is not in the corpus on this run - not asserted'); return; }
    found.push(w);
    var bad = 0;
    POOLS.forEach(function (p) {
      var present = g.members.filter(function (m) { return p.items.indexOf(m) !== -1; });
      if (present.length < 2) return;
      present.forEach(function (mine) {
        var room = mutuallySafeCapacity(mine, p.items, 3);
        SEEDS.forEach(function (s) {
          var b = D.buildOptions({ correct: mine, candidates: p.items, count: 4,
                                   shuffle: seededShuffle(s), heardOf: U.mainAudioText });
          present.forEach(function (other) {
            if (other.c !== mine.c && b.options.some(function (o) { return o.card === other.c; })) bad++;
          });
          /* Exactly as many options as the pool honestly holds. */
          if (b.options.length !== Math.min(4, 1 + room)) bad++;
          if (b.options.filter(function (o) { return o.correct; }).length !== 1) bad++;
        });
      });
    });
    eq('G2 "' + w + '" offers exactly one true meaning, in every pool and seed', bad, 0);
  });
  info('watched groups present in this corpus: ' + (found.join(', ') || 'none'));
})();

// The whole Listening corpus, every pool, a deterministic set of seeds.
//
// The option COUNT is judged against what the pool can honestly supply, decided
// by mutuallySafeCapacity above and never by today's pool sizes. The required
// count is EXACT:
//
//     expected = 1 + min(requested distractors, room)
//
// so room >= 3 demands four options, room 2 demands three, room 1 demands two,
// room 0 demands one. "Any smaller safe result" is deliberately not accepted:
// a short question is only ever correct when the pool truly cannot do better,
// and the whole point of the backtracking search is that a builder which
// strands an option is a defect rather than a conservative choice. Every short
// question is still reported by name, so one appearing in a future corpus is
// visible rather than silent.
(function () {
  var bad = { count: [], correct: [], heard: [], label: [], id: [], empty: [], source: [], missing: [] };
  var built = 0, short = [], roomStats = {};
  POOLS.forEach(function (p) {
    var items = p.items;
    p.items.forEach(function (mine) {
      /* Once per question, not once per seed: the pool does not change. */
      var room = mutuallySafeCapacity(mine, items, 3);
      roomStats[room] = (roomStats[room] || 0) + 1;
      var wanted = Math.min(4, 1 + room);
      SEEDS.forEach(function (s) {
        built++;
        var b = D.buildOptions({ correct: mine, candidates: items, count: 4,
                                 shuffle: seededShuffle(s), heardOf: U.mainAudioText });
        var tag = p.name + '/' + mine.c.id + '/seed' + s;
        var mineOpts = b.options.filter(function (o) { return o.correct; });
        if (mineOpts.length !== 1 || mineOpts[0].card !== mine.c) bad.correct.push(tag);
        /* A real, playable card always yields at least its own option. */
        if (b.options.length < 1) bad.missing.push(tag);
        /* ...and exactly as many as the pool honestly holds - no more, no fewer. */
        if (b.options.length !== wanted) {
          bad.count.push(tag + ' (room for ' + wanted + ', got ' + b.options.length + ')');
        }
        if (b.options.length < 4 && s === SEEDS[0]) {
          short.push(p.name + '/' + mine.c.id + ' pl="' + mine.c.pl + '" -> ' + b.options.length +
                     ' option(s), safe distractors available: ' + room);
        }
        var hk = b.options.map(function (o) { return heardKeyOf(o.card); });
        if (!hk.every(function (x, i) { return hk.indexOf(x) === i; })) bad.heard.push(tag);
        var lk = b.options.map(function (o) { return key(o.label); });
        if (!lk.every(function (x, i) { return lk.indexOf(x) === i; })) bad.label.push(tag);
        var idl = b.options.map(function (o) { return o.id; });
        if (!idl.every(function (x, i) { return idl.indexOf(x) === i; })) bad.id.push(tag);
        if (!b.options.every(function (o) { return !!key(o.label); })) bad.empty.push(tag);
        var cs = b.options.map(function (o) { return o.card; });
        if (!cs.every(function (x, i) { return cs.indexOf(x) === i; })) bad.source.push(tag);
      });
    });
  });
  info('corpus questions built across ' + POOLS.length + ' pools × ' + SEEDS.length + ' seeds: ' + built);
  info('safe distractors available per question (capped at 3): ' +
       Object.keys(roomStats).sort().map(function (k) { return k + ' -> ' + roomStats[k]; }).join(', '));
  info('real questions returning fewer than four options: ' + short.length +
       (short.length ? '\n            ' + short.slice(0, 20).join('\n            ') : ''));
  eq('G3 the correct source appears exactly once in every question', bad.correct.slice(0, 5), []);
  eq('G3 a real card always yields at least its own option', bad.missing.slice(0, 5), []);
  eq('G3 no two options share a heard prompt', bad.heard.slice(0, 5), []);
  eq('G3 no two options share an English label', bad.label.slice(0, 5), []);
  eq('G3 no two options share a stable id', bad.id.slice(0, 5), []);
  eq('G3 no source card is used twice in one question', bad.source.slice(0, 5), []);
  eq('G3 every visible option has text', bad.empty.slice(0, 5), []);
  eq('G3 the option count equals the independently computed maximum', bad.count.slice(0, 5), []);
})();

// The corpus has cards with no stable id or no gloss? Report it - the builder
// copes either way, but it is worth seeing.
(function () {
  var noId = ALL_POOL.filter(function (x) { return !x.c.id; });
  var noEn = ALL_POOL.filter(function (x) { return !key(x.c.en); });
  var noHeard = ALL_POOL.filter(function (x) { return !heardKeyOf(x.c); });
  info('Listening cards without a stable id: ' + noId.length +
       '; without a gloss: ' + noEn.length + '; without a clip: ' + noHeard.length);
  var seen = {}, dups = [];
  ALL_POOL.forEach(function (x) { if (x.c.id) { if (seen[x.c.id]) dups.push(x.c.id); seen[x.c.id] = 1; } });
  eq('G4 no stable id is shared by two Listening cards', dups, []);
})();

// pp-distractor.js must be data-driven: no Polish word, no card id.
(function () {
  var words = [];
  ALL_GROUPS.forEach(function (g) { g.members.forEach(function (m) { words.push(m.c.pl); }); });
  var uniq = {}; words.forEach(function (w) { uniq[w] = 1; });
  var leaked = Object.keys(uniq).filter(function (w) { return DISTRACTOR_SRC.indexOf(w) !== -1; });
  eq('G5 pp-distractor.js hardcodes no colliding Polish word', leaked, []);
  var idLeak = ALL_POOL.filter(function (x) { return x.c.id && DISTRACTOR_SRC.indexOf(x.c.id) !== -1; })
                       .map(function (x) { return x.c.id; });
  eq('G5 pp-distractor.js hardcodes no card id', idLeak.slice(0, 5), []);
  var glossLeak = ALL_GROUPS.reduce(function (acc, g) {
    g.members.forEach(function (m) { if (DISTRACTOR_SRC.indexOf('"' + m.c.en + '"') !== -1) acc.push(m.c.id); });
    return acc;
  }, []);
  eq('G5 pp-distractor.js hardcodes no gloss', glossLeak, []);
})();

// =========================================================================
// H. PRODUCTION WIRING - the shipping code is what all of the above describes
// =========================================================================
var SRC_START_LISTEN = bodyOf(INDEX, 'startListen');
var SRC_LRENDER = bodyOf(INDEX, 'lRender');
var SRC_RBUILD = bodyOf(INDEX, 'rBuildOptions');
var SRC_STARTROUND = bodyOf(INDEX, 'startRound');
var CODE_START_LISTEN = codeOnly(SRC_START_LISTEN);
var CODE_LRENDER = codeOnly(SRC_LRENDER);
var CODE_RRENDER = codeOnly(bodyOf(INDEX, 'rRender'));
var CODE_RPICK = codeOnly(bodyOf(INDEX, 'rPickOption'));

ok('H1 Listening builds its options through PP_DISTRACTOR',
   CODE_START_LISTEN.indexOf('PP_DISTRACTOR.buildOptions') !== -1);
// One call site inside the per-question map: the builder runs once for each
// selected question, never twice for one and never once for the whole round.
eq('H1 the builder has exactly one call site in startListen',
   countOf(CODE_START_LISTEN, 'PP_DISTRACTOR.buildOptions'), 1);
ok('H1 it asks for four options', CODE_START_LISTEN.indexOf('count:4') !== -1);
ok('H1 it injects the app shuffle', CODE_START_LISTEN.indexOf('shuffle:gShuffle') !== -1);
ok('H1 it passes the real heard-prompt rule', CODE_START_LISTEN.indexOf('heardOf:ppMainAudioText') !== -1);
ok('H1 it still draws from the Listening pool',
   CODE_START_LISTEN.indexOf('poolFor(L.topicRef.src, "listen")') !== -1);
// Phase 3E moved the `.slice(0,15)` INTO lSelectQuestions, which now owns the
// count so it can prefer prompts the previous round did not use. The claim is
// unchanged - Listening still asks for fifteen - so only the expression it is
// read from is narrowed. Variety itself is owned by tests/test_listening_variety.js.
ok('H1 the round is still 15 questions',
   /lSelectQuestions\(\s*pool\s*,[^;]*?,\s*15\s*,\s*gShuffle\s*\)/.test(CODE_START_LISTEN));

// The old inline loop is gone - not merely bypassed.
ok('H2 the inline seen-set is gone', CODE_START_LISTEN.indexOf('new Set(') === -1);
ok('H2 the inline opts array is gone', CODE_START_LISTEN.indexOf('opts.push') === -1);
ok('H2 startListen no longer filters the pool by topic itself',
   CODE_START_LISTEN.indexOf('pool.filter(') === -1);
ok('H2 startListen no longer compares glosses', CODE_START_LISTEN.indexOf('x.c.en') === -1);

// Correctness is retained identity, never a string match.
ok('H3 lRender marks the answer by the retained flag', CODE_LRENDER.indexOf('o.correct') !== -1);
ok('H3 lRender no longer decides correctness by comparing glosses',
   CODE_LRENDER.indexOf('o===q.c.en') === -1 && CODE_LRENDER.indexOf('o === q.c.en') === -1);
ok('H3 the option button still shows the English gloss', CODE_LRENDER.indexOf('b.textContent=o.label') !== -1);

// First-attempt scoring, retries, reveal, examples and usage labels are untouched.
// Read through hasCode: the claim is which tokens appear and in what order, never
// the indentation or the spacing they are typed in.
ok('H4 a first-attempt success is still the only thing scored',
   hasCode(CODE_LRENDER, 'if(!L.attempted) L.results[L.i]=true;'));
ok('H4 a wrong answer still marks the question missed',
   hasCode(CODE_LRENDER, 'L.attempted=true; L.results[L.i]=false;'));
ok('H4 a wrong answer still disables only that button',
   hasCode(CODE_LRENDER, 'b.classList.add("wrong"); b.disabled=true;'));
ok('H4 the Polish is still revealed on success', hasCode(CODE_LRENDER, 'rv.textContent=q.c.pl'));
ok('H4 the example is still shown', hasCode(CODE_LRENDER, 'q.c.ex'));
ok('H4 usage labels are still appended', hasCode(CODE_LRENDER, 'ppAppendUsageTo(fb, q.c)'));
// Autoplay is asserted on the CODE, not on a comment that says so. A comment can
// be reworded or deleted without changing a thing the learner hears, and pinning
// its wording teaches people to restore the sentence rather than read it. What
// must stay true is that rendering a question starts no sound by any route.
ok('H4 there is still no autoplay: rendering a question starts nothing',
   ['speakText', 'speakCardMain', 'lPlayCurrent', 'new Audio', 'speechSynthesis.speak']
     .every(function (entry) { return !hasCode(CODE_LRENDER, entry); }));
// What matters is that Play still routes the CURRENT question's card through
// speakCardMain and hands it the Play button - not that the function is still
// one line long. It has since grown a manifest-readiness guard (Phase 3C), whose
// own behaviour is owned by tests/test_audio_fallback.js.
ok('H4 the replay button still speaks the card', (function () {
  var body = codeOnly(bodyOf(INDEX, 'lPlayCurrent'));
  return hasCode(body, 'L.i < L.qs.length') &&
         hasCode(body, 'speakCardMain(L.qs[L.i].c, $("lPlay"))');
})());
// The completion WORDING is a string the learner reads, so it stays pinned
// exactly - its spacing is content, not formatting.
ok('H4 the completion wording is unchanged',
   INDEX.indexOf('"You recognised "+score+" of "+L.qs.length+" on the first listen."') !== -1);
ok('H4 the score is still first-attempt successes',
   hasCode(codeOnly(INDEX), 'const score=L.results.filter(Boolean).length'));

// The Mixed Quiz adopted this builder in Priority 3 Phase 4D. What is asserted
// here is only that the ADOPTION is real - that the second caller goes through
// the same door, and that it kept the source rather than flattening it back to
// strings. Everything the Mixed Quiz does with those records afterwards - the two
// prompt identities, the fallback join, the retry, the rendering and the corpus
// sweep - belongs to tests/test_mixed_distractors.js, and duplicating it here
// would mean two files to update for one change.
// Read through hasCode: the claim is which tokens appear, never how they are typed.
ok('H5 the Mixed Quiz builds its options through PP_DISTRACTOR',
   hasCode(codeOnly(SRC_RBUILD), 'PP_DISTRACTOR.buildOptions('));
ok('H5 it asks the shared builder for four options', hasCode(codeOnly(SRC_RBUILD), 'count: 4'));
ok('H5 it injects the app shuffle', hasCode(codeOnly(SRC_RBUILD), 'shuffle: gShuffle'));
ok('H5 the old exact-string filter is gone',
   codeOnly(SRC_RBUILD).indexOf('pool.filter(') === -1 &&
   codeOnly(SRC_RBUILD).indexOf('c.en !== card.en') === -1);
ok('H5 the round hands the builder pool RECORDS, not raw cards',
   hasCode(codeOnly(SRC_STARTROUND), '{ c, topic: topic.name }') &&
   codeOnly(SRC_STARTROUND).indexOf('x=>x.c') === -1);
// This suite makes NO application-wide claim about who may call into
// pp-distractor.js. Counting call sites across index.html would be a claim about
// the app's shape rather than about this file's API, and it is exactly the count
// that Phase 4D was always going to break by adopting the builder in a second
// activity. What is asserted instead is scoped to each caller in turn.
ok('H5 the Listening question key normalises through PP_DISTRACTOR',
   hasCode(codeOnly(bodyOf(INDEX, 'lQuestionKey')), 'PP_DISTRACTOR.normalizeKey('));
ok('H5 Listening still builds its options through PP_DISTRACTOR',
   hasCode(CODE_START_LISTEN, 'PP_DISTRACTOR.buildOptions('));
ok('H5 the Mixed Quiz renders the retained label', hasCode(CODE_RRENDER, 'b.textContent=o.label'));
ok('H5 the Mixed Quiz decides correctness by the retained flag',
   hasCode(CODE_RPICK, 'o.correct===true'));
ok('H5 no visible string decides a Mixed Quiz answer',
   CODE_RPICK.indexOf('o===q.c.en') === -1 && CODE_RPICK.indexOf('o === q.c.en') === -1);

// ...and the real rBuildOptions is EXECUTED, against a synthetic pool and a
// deterministic gShuffle, so the adoption is a claim about what it does rather
// than about how it is typed.
(function () {
  var rBuildOptions = new Function('gShuffle', 'PP_DISTRACTOR', 'ppMainAudioText',
    SRC_RBUILD + '\nreturn rBuildOptions;')(KEEP, D, U.mainAudioText);
  var card = { id: 'r-1', pl: 'r1', en: 'the answer' };
  var pool = [card,
              { id: 'r-2', pl: 'r2', en: 'first' },
              { id: 'r-3', pl: 'r3', en: 'second' },
              { id: 'r-4', pl: 'r4', en: 'third' },
              { id: 'r-5', pl: 'r5', en: 'fourth' }]
             .map(function (c) { return { c: c, topic: 'Fixture topic' }; });

  var out = rBuildOptions(pool[0], pool, 'mc');
  ok('H5 rBuildOptions returns retained records, not strings',
     Array.isArray(out) && out.length > 0 &&
     out.every(function (o) { return o && typeof o === 'object' && typeof o.label === 'string'; }));
  eq('H5 rBuildOptions returns four options when the pool allows', out.length, 4);
  eq('H5 every record keeps its card, its pool item and its stable id',
     out.filter(function (o) { return o.card && o.item && o.id === o.card.id; }).length, out.length);
  eq('H5 exactly one record is flagged correct',
     out.filter(function (o) { return o.correct === true; }).length, 1);
  ok('H5 the correct record is the asked card',
     out.filter(function (o) { return o.correct === true; })[0].card === card);
  eq('H5 rBuildOptions still draws its distractors from the pool',
     out.filter(function (o) { return ['first', 'second', 'third', 'fourth'].indexOf(o.label) !== -1; }).length, 3);

  // The rules the shared builder owns now hold for the Mixed Quiz too. A DIFFERENT
  // card whose gloss merely reads the same as another is dropped - the case the old
  // exact-string filter let straight through.
  var twinPool = [card,
                  { id: 'r-11', pl: 'r11', en: 'twin' },
                  { id: 'r-12', pl: 'r12', en: 'Twin!' },
                  { id: 'r-13', pl: 'r13', en: 'distinct' }]
                 .map(function (c) { return { c: c, topic: 'Fixture topic' }; });
  var twins = rBuildOptions(twinPool[0], twinPool, 'mc');
  eq('H5 two distractors that read the same no longer share a Mixed Quiz question',
     twins.filter(function (o) { return key(o.label) === key('twin'); }).length, 1);

  // A typed question never reaches the builder at all.
  eq('H5 a typed question builds no options', rBuildOptions(pool[0], pool, 'type'), []);

  info('Mixed Quiz today: duplicate distractor glosses ' +
       (twins.filter(function (o) { return key(o.label) === key('twin'); }).length > 1
          ? 'still reach' : 'no longer reach') +
       ' the learner - the option SET is now owned by tests/test_mixed_distractors.js');
})();

// Script order and offline availability.
var tagAt = INDEX.indexOf('<script src="pp-distractor.js"></script>');
ok('H6 index.html includes pp-distractor.js as a script src', tagAt !== -1);
eq('H6 exactly once', countOf(INDEX, '<script src="pp-distractor.js"></script>'), 1);
ok('H6 it loads before the first PP_DISTRACTOR use', tagAt < INDEX.indexOf('PP_DISTRACTOR.buildOptions'));
ok('H6 it loads with the other shared helpers',
   tagAt > INDEX.indexOf('<script src="pp-usage.js">') &&
   tagAt < INDEX.indexOf('<script src="pp-migrate.js">'));
eq('H7 sw.js precaches pp-distractor.js exactly once', countOf(SW, '"./pp-distractor.js"'), 1);
ok('H7 the other precached helpers are still listed',
   SW.indexOf('"./pp-usage.js"') !== -1 && SW.indexOf('"./pp-answer.js"') !== -1 &&
   SW.indexOf('"./pp-migrate.js"') !== -1);
ok('H8 PP_DISTRACTOR exposes its documented surface',
   typeof D.buildOptions === 'function' && typeof D.normalizeKey === 'function' &&
   typeof D.labelsOf === 'function');

// ---------- report ----------
INFO.forEach(function (l) { console.log(l); });
LOG.forEach(function (l) { console.log(l); });
console.log('Distractor tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
if (FAIL) { $.NSApplication; throw new Error(FAIL + ' assertion(s) failed'); }
