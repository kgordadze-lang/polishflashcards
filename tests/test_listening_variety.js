// Deterministic tests for Listening round variety - Priority 3 Phase 3E.
// Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_listening_variety.js
// Exit status is 0 only if every assertion passes (printed at the end).
//
// WHAT THIS FILE IS FOR
// Every Listening round used to be an independent sample: gShuffle(pool) then
// the first fifteen. Pressing "New round" could therefore hand back a question
// the learner had answered ten seconds earlier - and in a pool of a few hundred
// cards, a couple of repeats per round is the EXPECTED outcome, not bad luck.
// Phase 3E remembers what the last round of each scope asked and pushes those
// questions to the back of the queue.
//
// It also stops one round asking the same thing twice in a different costume:
// the corpus teaches `woda` in three topics with three glosses, and to a learner
// who only hears the clip those are one question, not three.
//
// HOW IT TESTS
// Two halves, deliberately.
//   Synthetic fixtures pin the CONTRACT. No Polish word, no card id and no count
//   from the shipping corpus decides anything in sections A-H, so the rules stay
//   readable and stay true for cards nobody has written yet.
//   The real corpus is then swept through the same production helpers in section
//   I: every actual Listening scope is discovered at runtime, two consecutive
//   rounds are built, and the overlap is compared against a minimum computed
//   independently from the corpus statistics. Counts are REPORTED, never
//   asserted - the corpus is allowed to grow.
//
// SCOPE - what deliberately is NOT here
// Which cards may be asked at all belongs to tests/test_activities.js and
// tests/test_typeit_eligibility.js. Who may share one question belongs to
// tests/test_distractors.js. Audio lifecycle and readiness belong to
// tests/test_audio_fallback.js; announcements and focus to
// tests/test_listening_accessibility.js. This file owns one thing: WHICH
// questions a round asks, and what the previous round leaves behind.
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

// index.html loads these in this order.
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
// "it did not throw" is an assertion in its own right here: section A hands the
// helper arguments no caller should ever produce, and the required behaviour is a
// harmless answer rather than an exception reaching the learner's screen.
function noThrow(name, fn) {
  var threw = null, out;
  try { out = fn(); } catch (e) { threw = e; }
  ok(name + (threw ? '  (threw ' + threw + ')' : ''), threw === null);
  return out;
}
function countOf(hay, needle) {
  if (!needle) return 0;
  var n = 0, i = 0;
  while ((i = hay.indexOf(needle, i)) !== -1) { n++; i += needle.length; }
  return n;
}

// ---------- pull the real functions out of index.html ----------
// Brace scanner that skips comments and strings, as the other index.html suites
// use. A broken extraction throws, which is the correct outcome.
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
// Comment-stripped view: a rule must be visible in CODE, never only in prose.
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
function squash(s) { return s.replace(/\s+/g, ''); }
function hasCode(hay, needle) { return squash(hay).indexOf(squash(needle)) !== -1; }

var SRC = {};
['lScopeKey', 'lQuestionKey', 'lSelectQuestions', 'startListen', 'lRender',
 'poolFor', 'practiceTopics'].forEach(function (n) { SRC[n] = extractFunction(INDEX, n); });

// The session-only previous-round memory, and the two top-level statements that
// build the practice levels. All three are taken from index.html rather than
// re-typed here, so what runs below is the shipping code.
var L_RECENT_SRC = (INDEX.match(/const\s+L_RECENT\s*=[^;\n]*;/) || [])[0];
if (!L_RECENT_SRC) throw new Error('extract: L_RECENT not found in index.html');
var VOCAB_SRC_SRC = (INDEX.match(/const\s+VOCAB_SRC\s*=[^;]+;/) || [])[0];
if (!VOCAB_SRC_SRC) throw new Error('extract: VOCAB_SRC not found in index.html');
var PUSH_SRC = (INDEX.match(/LEVELS\.push\(\s*\{\s*level:"Type it"[\s\S]*?\n\);/) || [])[0];
if (!PUSH_SRC) throw new Error('extract: the practice-levels LEVELS.push not found in index.html');

// The app's own level list, built the app's own way: the synthetic "Listening"
// level and its topics are what the learner actually opens, so section I must
// discover its scopes rather than be told them.
var APP = (new Function('LEVELS', 'ppEligibleFor',
  VOCAB_SRC_SRC + '\n' + SRC.practiceTopics + '\n' + PUSH_SRC + '\n' + SRC.poolFor + '\n' +
  'return { VOCAB_SRC: VOCAB_SRC, poolFor: poolFor };'
))(LEVELS, U.eligibleFor);

// ---------- a compiled Listening scope ----------
// One instance is one page load: it holds its own L_RECENT, exactly as the app
// does, so a section that wants a clean memory simply asks for a new instance.
// startListen's screen work is stubbed - $, show and lRender belong to the
// accessibility and audio suites - and stopAllAudio is counted so this file can
// see that the boundary is still honoured without owning the audio rules.
function makeListenFull(levels, poolForFn) {
  var state = { stops: 0, shown: [], rendered: 0, label: '', shuffle: keepOrder };
  var L = { topicRef: null, li: 0, ti: 0, qs: [], i: 0, results: [], attempted: false };
  var api = (new Function('$', 'show', 'L', 'LEVELS', 'poolFor', 'gShuffle', 'stopAllAudio',
                          'lRender', 'ppMainAudioText', 'PP_DISTRACTOR',
    L_RECENT_SRC + '\n' +
    [SRC.lScopeKey, SRC.lQuestionKey, SRC.lSelectQuestions, SRC.startListen].join('\n') + '\n' +
    'return {\n' +
    '  startListen: function(a,b){ return startListen(a,b); },\n' +
    '  lSelectQuestions: function(a,b,c,d){ return lSelectQuestions(a,b,c,d); },\n' +
    '  lQuestionKey: function(a){ return lQuestionKey(a); },\n' +
    '  lScopeKey: function(a,b){ return lScopeKey(a,b); },\n' +
    '  recent: L_RECENT\n' +
    '};'
  ))(
    function () { return { textContent: '' }; },
    function (scr) { state.shown.push(scr); },
    L, levels, poolForFn,
    function (a) { return state.shuffle(a); },
    function () { state.stops++; },
    function () { state.rendered++; },
    U.mainAudioText, D
  );
  api.state = state; api.L = L;
  return api;
}

// ---------- injected randomness ----------
function keepOrder(a) { return a.slice(); }                 // identity, still a NEW array
function reverseOrder(a) { return a.slice().reverse(); }
// A seeded shuffle: deterministic, repeatable, and returning a NEW array so a
// mutation of the caller's input would be visible rather than hidden.
function seeded(seed) {
  return function (a) {
    var state = (seed >>> 0) || 1, out = a.slice();
    function next() {                                        // mulberry32
      state = (state + 0x6D2B79F5) >>> 0;
      var t = state;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    }
    for (var i = out.length - 1; i > 0; i--) {
      var j = Math.floor(next() * (i + 1));
      var tmp = out[i]; out[i] = out[j]; out[j] = tmp;
    }
    return out;
  };
}

// ---------- fixtures ----------
// Synthetic cards only. Nothing below reads a Polish word out of the corpus.
function card(id, pl, en) { return { id: id, pl: pl, en: en }; }
function item(c, topic) { return { c: c, topic: topic || 'T' }; }
// n cards with n distinct heard prompts and n distinct glosses.
function distinctPool(n, tag) {
  var out = [];
  for (var i = 0; i < n; i++) out.push(item(card((tag || 'p') + i, 'pl-' + (tag || 'p') + i, 'en-' + (tag || 'p') + i)));
  return out;
}
function keysOf(list, api) { return list.map(function (it) { return api.lQuestionKey(it.c); }); }
function idsOf(list) { return list.map(function (it) { return it.c.id; }); }
function uniq(a) { var s = {}, out = []; a.forEach(function (x) { if (!s[x]) { s[x] = 1; out.push(x); } }); return out; }
function overlapCount(keys, prevKeys) {
  var prev = {}; prevKeys.forEach(function (k) { prev[k] = 1; });
  return keys.filter(function (k) { return prev[k]; }).length;
}

// One shared instance for the pure-helper sections; lSelectQuestions never reads
// LEVELS or L_RECENT, so the level list handed in is irrelevant to A-G.
var PURE = makeListenFull([{ level: 'X', topics: [{ name: 'T', src: ['X'], kind: 'listen' }] }],
                          function () { return []; });
var pick = PURE.lSelectQuestions;

// =========================================================================
// A. THE PURE HELPER'S CONTRACT
// =========================================================================
(function () {
  var pool = distinctPool(30);

  var out = pick(pool, [], 15, keepOrder);
  ok('A1 the result is an array', Array.isArray(out));
  ok('A1 the result is not the pool itself', out !== pool);
  eq('A1 fifteen were asked for and fifteen came back', out.length, 15);

  // Mutating the result must not reach back into the pool.
  var before = idsOf(pool).join(',');
  out.reverse(); out.push(null); out.length = 0;
  eq('A2 the pool is untouched by anything done to the result', idsOf(pool).join(','), before);

  // Nothing handed in is modified: not the pool, not the cards, not the history.
  var poolSnapshot = JSON.stringify(pool);
  var recent = ['pl-p0', 'pl-p1', 'pl-p2'];
  var recentSnapshot = JSON.stringify(recent);
  pick(pool, recent, 15, seeded(4));
  eq('A2 the candidate pool is not mutated', JSON.stringify(pool), poolSnapshot);
  eq('A2 the previous-round history is not mutated', JSON.stringify(recent), recentSnapshot);
  var cardSnapshot = JSON.stringify(pool.map(function (i) { return i.c; }));
  pick(pool, recent, 15, seeded(9));
  eq('A2 no card is mutated', JSON.stringify(pool.map(function (i) { return i.c; })), cardSnapshot);

  // Determinism: the same pool and the same shuffle answer the same way.
  eq('A3 the same input and shuffle produce the same result',
     idsOf(pick(pool, recent, 15, seeded(11))), idsOf(pick(pool, recent, 15, seeded(11))));
  // ...and a different shuffle is free to answer differently. Both are valid.
  var s1 = idsOf(pick(pool, [], 15, seeded(2)));
  var s2 = idsOf(pick(pool, [], 15, seeded(88)));
  ok('A3 different deterministic shuffles can produce different valid results',
     s1.join(',') !== s2.join(','));
  ok('A3 both results are still full, in-pool and duplicate-free', (function () {
    var poolIds = idsOf(pool);
    return [s1, s2].every(function (r) {
      return r.length === 15 && uniq(r).length === 15 &&
             r.every(function (id) { return poolIds.indexOf(id) !== -1; });
    });
  })());

  // The requested count is respected, above and below fifteen.
  eq('A4 a request for 15 is respected', pick(pool, [], 15, seeded(3)).length, 15);
  [1, 2, 7, 14].forEach(function (n) {
    eq('A4 a request for ' + n + ' is respected', pick(pool, [], n, seeded(3)).length, n);
  });
  // A pool smaller than the request gives every distinct source card it has.
  var small = distinctPool(6, 's');
  eq('A5 a small pool returns every available distinct source card',
     idsOf(pick(small, [], 15, keepOrder)).sort().join(','), idsOf(small).sort().join(','));

  // Malformed arguments answer harmlessly instead of throwing.
  eq('A6 a missing pool returns nothing', noThrow('A6 a missing pool does not throw',
     function () { return pick(undefined, [], 15, keepOrder); }), []);
  eq('A6 a null pool returns nothing', noThrow('A6 a null pool does not throw',
     function () { return pick(null, [], 15, keepOrder); }), []);
  eq('A6 a non-array pool returns nothing', noThrow('A6 a non-array pool does not throw',
     function () { return pick('kawa', [], 15, keepOrder); }), []);
  [0, -5, NaN, undefined, null, 'x', {}].forEach(function (bad) {
    eq('A6 a count of ' + JSON.stringify(bad) + ' returns nothing',
       noThrow('A6 a count of ' + JSON.stringify(bad) + ' does not throw',
               function () { return pick(pool, [], bad, keepOrder); }), []);
  });
  ok('A6 a fractional count is floored', pick(pool, [], 3.9, keepOrder).length === 3);
  ok('A6 a missing shuffle still selects', noThrow('A6 a missing shuffle does not throw',
     function () { return pick(pool, [], 5, null); }).length === 5);
  ok('A6 a shuffle returning a non-array still selects',
     noThrow('A6 a shuffle returning a non-array does not throw',
             function () { return pick(pool, [], 5, function () { return 'nope'; }); }).length === 5);
  [null, undefined, 'kawa', 42, {}].forEach(function (bad) {
    ok('A6 a history of ' + JSON.stringify(bad) + ' is treated as empty',
       noThrow('A6 a history of ' + JSON.stringify(bad) + ' does not throw',
               function () { return pick(pool, bad, 15, keepOrder); }).length === 15);
  });
  ok('A6 a Set of previous keys is accepted like an array', (function () {
    var asSet = pick(pool, new Set(['pl-p0', 'pl-p1']), 15, keepOrder);
    var asArr = pick(pool, ['pl-p0', 'pl-p1'], 15, keepOrder);
    return idsOf(asSet).join(',') === idsOf(asArr).join(',');
  })());
  // Broken pool ENTRIES are skipped, never thrown on and never asked. An entry
  // that is not an object, or whose `c` is not a card, has no card behind it at
  // all - there is nothing to play and nothing to answer.
  var dirty = [null, undefined, 42, 'kawa', { c: null }, { c: 'kawa' }].concat(distinctPool(4, 'd'));
  var cleaned = noThrow('A6 broken pool entries do not throw',
                        function () { return pick(dirty, [], 15, keepOrder); });
  eq('A6 only the usable entries come back', idsOf(cleaned).join(','), 'd0,d1,d2,d3');
  eq('A6 a pool of nothing but broken entries returns nothing',
     noThrow('A6 an all-broken pool does not throw',
             function () { return pick(dirty.slice(0, 6), [], 15, keepOrder); }), []);
  // A bare object IS card-shaped, so it is kept rather than silently dropped -
  // and two of them are two questions, not one, because neither can borrow the
  // other's identity. Nothing in the corpus looks like this; the rule exists so
  // that a future card missing a field is degraded, never deleted.
  var bare = noThrow('A6 a card-shaped entry with no fields does not throw',
                     function () { return pick([{}, {}], [], 15, keepOrder); });
  eq('A6 card-shaped entries keep their own identities', bare.length, 2);
})();

// =========================================================================
// B. THE FIRST ROUND OF A SCOPE
// =========================================================================
(function () {
  var pool = distinctPool(30);
  // With no history at all, the round is the shuffle's first fifteen - the old
  // behaviour, preserved, because there is nothing yet to avoid.
  eq('B1 the first-ever round follows the injected shuffle exactly',
     idsOf(pick(pool, undefined, 15, seeded(5))),
     idsOf(seeded(5)(pool)).slice(0, 15));
  eq('B1 an empty history behaves the same as no history',
     idsOf(pick(pool, [], 15, seeded(5))), idsOf(pick(pool, undefined, 15, seeded(5))));

  // The one difference from a bare slice: a duplicate prompt waits its turn.
  // Two cards say "woda" and sit FIRST in the shuffle; the round must still find
  // fifteen distinct prompts rather than ask the same clip twice.
  var dupes = [item(card('wod-a', 'woda', 'water')), item(card('wod-b', 'woda', 'still water'))]
    .concat(distinctPool(20, 'q'));
  var first = pick(dupes, [], 15, keepOrder);
  eq('B2 a first round is still fifteen questions', first.length, 15);
  eq('B2 distinct heard prompts are preferred over a duplicate prompt',
     uniq(keysOf(first, PURE)).length, 15);
  eq('B2 exactly one of the two same-sounding cards is asked',
     idsOf(first).filter(function (id) { return id.indexOf('wod-') === 0; }).length, 1);
  eq('B2 the one that is asked is the shuffle\'s first', idsOf(first)[0], 'wod-a');

  // No shortening: a round is never trimmed to look tidier.
  [16, 20, 30].forEach(function (n) {
    eq('B3 a pool of ' + n + ' still fills a fifteen-question round',
       pick(distinctPool(n, 'n' + n), [], 15, seeded(n)).length, 15);
  });
})();

// =========================================================================
// C. THIRTY DISTINCT PROMPTS - a fully fresh second round
// =========================================================================
(function () {
  var pool = distinctPool(30, 'c');
  var round1 = pick(pool, [], 15, seeded(21));
  var keys1 = keysOf(round1, PURE);
  var round2 = pick(pool, keys1, 15, seeded(22));
  var keys2 = keysOf(round2, PURE);
  eq('C1 the first round is fifteen questions', round1.length, 15);
  eq('C1 the second round is still fifteen questions', round2.length, 15);
  eq('C2 the second round repeats none of the first round\'s prompts',
     overlapCount(keys2, keys1), 0);
  eq('C2 together the two rounds cover the whole pool',
     uniq(keys1.concat(keys2)).length, 30);
  eq('C3 the second round asks no card twice', uniq(idsOf(round2)).length, 15);
})();

// =========================================================================
// D. TWENTY DISTINCT PROMPTS - every fresh prompt, then the minimum reused
// =========================================================================
(function () {
  var pool = distinctPool(20, 'd');
  var round1 = pick(pool, [], 15, seeded(31));
  var keys1 = keysOf(round1, PURE);
  var round2 = pick(pool, keys1, 15, seeded(32));
  var keys2 = keysOf(round2, PURE);
  var fresh = keys2.filter(function (k) { return keys1.indexOf(k) === -1; });

  eq('D1 the round is still fifteen questions', round2.length, 15);
  eq('D2 all five unseen prompts are used', fresh.length, 5);
  eq('D2 the five are exactly the ones the first round left out',
     fresh.slice().sort().join(','),
     keysOf(pool, PURE).filter(function (k) { return keys1.indexOf(k) === -1; }).sort().join(','));
  eq('D3 exactly ten previous prompts come back', overlapCount(keys2, keys1), 10);
  eq('D4 no card is asked twice in the round', uniq(idsOf(round2)).length, 15);
  // The fresh five come FIRST in the queue - they are the priority-1 tier.
  eq('D5 the unseen prompts are taken before any reused one',
     keys2.slice(0, 5).filter(function (k) { return keys1.indexOf(k) === -1; }).length, 5);
})();

// =========================================================================
// E. A SMALL POOL - repetition is accepted, shortening is not
// =========================================================================
(function () {
  var pool = distinctPool(10, 'e');
  var round1 = pick(pool, [], 15, seeded(41));
  var keys1 = keysOf(round1, PURE);
  var round2 = pick(pool, keys1, 15, seeded(42));
  eq('E1 a ten-card topic asks ten questions', round1.length, 10);
  eq('E1 the next round asks ten questions too', round2.length, 10);
  eq('E2 the repetition is total, because it is unavoidable',
     overlapCount(keysOf(round2, PURE), keys1), 10);
  eq('E3 no card is invented', idsOf(round2).filter(function (id) {
    return idsOf(pool).indexOf(id) === -1; }).length, 0);
  eq('E3 no card is duplicated', uniq(idsOf(round2)).length, 10);
  eq('E4 a third round is still ten questions',
     pick(pool, keysOf(round2, PURE), 15, seeded(43)).length, 10);
})();

// =========================================================================
// F. DUPLICATE HEARD PROMPTS
// =========================================================================
(function () {
  // Enough distinct prompts to fill the round, plus one same-sounding pair.
  var pair = [item(card('zam-a', 'zamek', 'castle')), item(card('zam-b', 'zamek', 'zip'))];
  var pool = pair.concat(distinctPool(20, 'f'));
  var round = pick(pool, [], 15, keepOrder);
  eq('F1 only one representative of the duplicate prompt is asked',
     idsOf(round).filter(function (id) { return id.indexOf('zam-') === 0; }).length, 1);
  eq('F1 the round still holds fifteen distinct prompts',
     uniq(keysOf(round, PURE)).length, 15);

  // Grouping follows PP_DISTRACTOR's normalisation, whatever it decides - this
  // file does not re-implement it. Case, surrounding whitespace and inaudible
  // punctuation are already equivalent there, so they cannot smuggle a second
  // copy of one clip into a round.
  var sneaky = [
    item(card('hi-a', 'Dzień dobry', 'good morning')),
    item(card('hi-b', '  dzień dobry!  ', 'good day')),
    item(card('hi-c', 'DZIEŃ DOBRY.', 'hello'))
  ].concat(distinctPool(20, 'g'));
  ok('F2 the three variants normalise to one prompt', (function () {
    var k = sneaky.slice(0, 3).map(function (i) { return PURE.lQuestionKey(i.c); });
    return k[0] === k[1] && k[1] === k[2];
  })());
  eq('F2 case, padding and punctuation do not smuggle in a second copy',
     idsOf(pick(sneaky, [], 15, keepOrder))
       .filter(function (id) { return id.indexOf('hi-') === 0; }).length, 1);

  // Diacritics are meaningful: two Polish words that differ only by a stroke are
  // two words, and hearing them apart is what Listening teaches.
  var diacritic = [item(card('be-a', 'być', 'to be')), item(card('be-b', 'byc', 'a misspelling'))]
    .concat(distinctPool(20, 'h'));
  ok('F3 a diacritic still separates two prompts',
     PURE.lQuestionKey(diacritic[0].c) !== PURE.lQuestionKey(diacritic[1].c));
  eq('F3 both are therefore askable in one round',
     idsOf(pick(diacritic, [], 15, keepOrder))
       .filter(function (id) { return id.indexOf('be-') === 0; }).length, 2);

  // The second representative is used ONLY to keep the round full - never before
  // every distinct prompt in the pool has been taken.
  var tight = [item(card('sok-a', 'sok', 'juice')), item(card('sok-b', 'sok', 'a juice'))]
    .concat(distinctPool(9, 't'));
  var round2 = pick(tight, [], 15, keepOrder);
  eq('F4 a duplicate-prompt card fills the round when nothing else can',
     round2.length, 11);
  eq('F4 it is used only after every distinct prompt',
     idsOf(round2).indexOf('sok-b'), 10);
  eq('F4 every distinct prompt is used before it',
     uniq(keysOf(round2, PURE).slice(0, 10)).length, 10);
  // With room to spare, that same pair contributes only one card.
  eq('F4 with enough distinct prompts the pair contributes one card',
     idsOf(pick([item(card('sok-a', 'sok', 'juice')), item(card('sok-b', 'sok', 'a juice'))]
       .concat(distinctPool(20, 'u')), [], 15, keepOrder))
       .filter(function (id) { return id.indexOf('sok-') === 0; }).length, 1);
})();

// =========================================================================
// G. SOURCE IDENTITY - one question per card, whatever the pool contains
// =========================================================================
(function () {
  var shared = card('pies-a', 'pies', 'dog');
  // The very same object listed twice.
  var twice = [item(shared), item(shared, 'other topic')].concat(distinctPool(20, 'x'));
  var out = pick(twice, [], 15, keepOrder);
  eq('G1 a duplicated source object is never asked twice',
     out.filter(function (i) { return i.c === shared; }).length, 1);
  eq('G1 the round is still full', out.length, 15);

  // Two different objects carrying one stable id - the same card, authored twice.
  var sameId = [item(card('kot-a', 'kot', 'cat')), item(card('kot-a', 'kot', 'a cat'))]
    .concat(distinctPool(20, 'y'));
  eq('G2 a duplicated stable id is never asked twice',
     idsOf(pick(sameId, [], 15, keepOrder)).filter(function (id) { return id === 'kot-a'; }).length, 1);

  // No id at all: object identity carries the card safely.
  var noIdA = { pl: 'ryba', en: 'fish' }, noIdB = { pl: 'ryba', en: 'a fish' };
  var noId = [item(noIdA), item(noIdA), item(noIdB)].concat(distinctPool(20, 'z'));
  var outNoId = noThrow('G3 cards without ids do not throw',
                        function () { return pick(noId, [], 15, keepOrder); });
  eq('G3 the repeated object is asked once', outNoId.filter(function (i) { return i.c === noIdA; }).length, 1);
  eq('G3 the same-sounding second card is not also asked',
     outNoId.filter(function (i) { return i.c === noIdB; }).length, 0);
  eq('G3 the round is still full', outNoId.length, 15);

  // Identity is the heard prompt, NOT the gloss. Two cards that read the same in
  // English but sound different are two questions; two that sound the same but
  // read differently are one.
  var sameGloss = [item(card('car-a', 'auto', 'car')), item(card('car-b', 'samochód', 'car'))]
    .concat(distinctPool(20, 'm'));
  eq('G4 one English gloss on two clips is two questions',
     idsOf(pick(sameGloss, [], 15, keepOrder))
       .filter(function (id) { return id.indexOf('car-') === 0; }).length, 2);
  ok('G4 the gloss does not decide identity',
     PURE.lQuestionKey(sameGloss[0].c) !== PURE.lQuestionKey(sameGloss[1].c));
  ok('G4 the identity is the normalised heard prompt',
     PURE.lQuestionKey(card('k1', 'Kawa!', 'coffee')) === D.normalizeKey(U.mainAudioText(card('k1', 'Kawa!', 'coffee'))));
  // A template with no complete audioText has no heard prompt; the id fallback
  // keeps such cards apart instead of collapsing them into one bucket.
  var tplA = { id: 'tpl1', cardType: 'template', pl: 'Gdzie jest...?', en: 'where is' };
  var tplB = { id: 'tpl2', cardType: 'template', pl: 'Ile kosztuje...?', en: 'how much' };
  eq('G5 a card with no heard prompt falls back to its stable id',
     PURE.lQuestionKey(tplA) === PURE.lQuestionKey(tplB), false);
  eq('G5 both are still askable', idsOf(pick([item(tplA), item(tplB)], [], 15, keepOrder)).join(','), 'tpl1,tpl2');
  noThrow('G5 a null card has no identity and does not throw', function () { return PURE.lQuestionKey(null); });
})();

// =========================================================================
// H. PER-SCOPE HISTORY, through the shipping startListen
// =========================================================================
// A synthetic app: one ordinary level with its own topic, plus the practice
// level whose topics are the Listening scopes. Pools are per-src, so switching
// scope really does change the candidate set.
var H_POOLS = {
  'A1': distinctPool(40, 'a1'),
  'A2': distinctPool(40, 'a2'),
  '*': distinctPool(40, 'a1').concat(distinctPool(40, 'a2'))
};
var H_LEVELS = [
  { level: 'A1', topics: [{ name: 'W kawiarni', src: ['A1'], kind: 'listen' }] },
  { level: 'Listening', topics: [
    { name: 'A1', src: ['A1'], kind: 'listen' },
    { name: 'A2', src: ['A2'], kind: 'listen' },
    { name: 'All levels', src: null, kind: 'listen' }
  ] }
];
function hPoolFor(src) { return H_POOLS[src ? src.join('+') : '*'].slice(); }
(function () {
  var app = makeListenFull(H_LEVELS, hPoolFor);
  function round(li, ti, shuffleSeed) {
    app.state.shuffle = seeded(shuffleSeed);
    app.startListen(li, ti);
    return app.L.qs.map(function (q) { return q.c.id; });
  }
  // A1, twice in a row.
  var a1r1 = round(1, 0, 101);
  var a1r2 = round(1, 0, 102);
  eq('H1 an A1 round is fifteen questions', a1r1.length, 15);
  eq('H1 the next A1 round repeats nothing', a1r1.filter(function (id) { return a1r2.indexOf(id) !== -1; }).length, 0);

  // A2 begins independently - it has never been played.
  var a2r1 = round(1, 1, 103);
  eq('H2 a scope that has never been played starts from a clean history',
     a2r1.join(','), idsOf(seeded(103)(hPoolFor(['A2']))).slice(0, 15).join(','));

  // Back to A1: it compares against A1's OWN last round, not A2's.
  var a1r3 = round(1, 0, 104);
  eq('H3 returning to A1 still avoids A1\'s last round',
     a1r3.filter(function (id) { return a1r2.indexOf(id) !== -1; }).length, 0);
  ok('H3 A1\'s memory was not consumed by the A2 round',
     a1r3.filter(function (id) { return a1r1.indexOf(id) !== -1; }).length > 0);

  // A topic of the same NAME under a different level is a different slot.
  var topicKey = app.lScopeKey(0, 0);        // level "A1", topic "W kawiarni"
  var levelKey = app.lScopeKey(1, 0);        // level "Listening", topic "A1"
  var allKey   = app.lScopeKey(1, 2);        // level "Listening", topic "All levels"
  ok('H4 a topic scope is not the same slot as a full-level scope', topicKey !== levelKey);
  ok('H4 All levels has its own slot', allKey !== levelKey && allKey !== topicKey);
  ok('H4 A1 and A2 are different slots', app.lScopeKey(1, 0) !== app.lScopeKey(1, 1));
  eq('H4 the same scope always keys the same way', app.lScopeKey(1, 0), levelKey);

  // All levels: its own history, and it does not disturb A1's.
  var allr1 = round(1, 2, 105);
  var allr2 = round(1, 2, 106);
  eq('H5 All levels repeats nothing of its own last round',
     allr1.filter(function (id) { return allr2.indexOf(id) !== -1; }).length, 0);
  var a1r4 = round(1, 0, 107);
  eq('H5 and A1 still compares against A1',
     a1r4.filter(function (id) { return a1r3.indexOf(id) !== -1; }).length, 0);

  // One slot per scope that has been opened - not one per round.
  eq('H6 exactly one history slot exists per scope played', app.recent.size, 3);
  eq('H6 a slot holds only the last round\'s identities', app.recent.get(levelKey).length, 15);
  ok('H6 the identities stored are question keys, not cards',
     app.recent.get(levelKey).every(function (k) { return typeof k === 'string'; }));

  // Leaving after one question still counts as "seen" - the memory is written
  // when the round is CREATED, not when it is finished.
  var before = app.recent.get(levelKey).slice();
  app.state.shuffle = seeded(108);
  app.startListen(1, 0);
  ok('H7 the memory is written when the round is created, not when it ends',
     app.recent.get(levelKey).join(',') !== before.join(','));

  // "New round" re-enters the CURRENT scope: the handler passes L.li and L.ti.
  var againExpr = (INDEX.match(/\$\("lAgain"\)\.addEventListener\("click",([\s\S]*?)\);/) || [])[1] || '';
  ok('H8 New round restarts the scope the learner is in',
     /startListen\(\s*L\.li\s*,\s*L\.ti\s*\)/.test(againExpr));
  eq('H8 L.li and L.ti are the scope just opened', [app.L.li, app.L.ti], [1, 0]);

  // A page reload is a fresh app: a new instance starts with an empty memory.
  eq('H9 a reload forgets everything', makeListenFull(H_LEVELS, hPoolFor).recent.size, 0);
})();

// =========================================================================
// I. THE REAL CORPUS - every Listening scope the app actually offers
// =========================================================================
(function () {
  var scopes = [];
  LEVELS.forEach(function (lv, li) {
    lv.topics.forEach(function (t, ti) { if (t.kind === 'listen') scopes.push({ li: li, ti: ti, lv: lv, t: t }); });
  });
  ok('I0 the app offers at least one Listening scope', scopes.length > 0);
  info('Listening scopes discovered: ' + scopes.length + ' -> ' +
       scopes.map(function (s) { return s.t.name; }).join(', '));

  var app = makeListenFull(LEVELS, APP.poolFor);
  var REQUEST = 15;
  var thin = [], notFresh = [], fewKeys = [];

  scopes.forEach(function (s, n) {
    var label = s.t.name;
    var pool = APP.poolFor(s.t.src, 'listen');

    // ---- what the corpus says, computed here and not from the helper ----
    var sources = [], seen = new Set(), keyOfSource = [], malformed = [];
    pool.forEach(function (it) {
      var c = it.c;
      var id = (typeof c.id === 'string' && c.id) ? c.id : c;
      if (seen.has(id)) return;
      seen.add(id); sources.push(it);
      var k = D.normalizeKey(U.mainAudioText(c));
      if (!k) malformed.push(c.id || '(no id)');
      keyOfSource.push(k || ('id␟' + (c.id || '')));
    });
    eq('I1 ' + label + ': every eligible card has a heard prompt', malformed, []);
    var distinctKeys = uniq(keyOfSource);
    var expectedLen = Math.min(REQUEST, sources.length);

    // ---- two consecutive rounds, deterministically ----
    app.state.shuffle = seeded(900 + n);
    app.startListen(s.li, s.ti);
    var r1 = app.L.qs.slice();
    app.state.shuffle = seeded(950 + n);
    app.startListen(s.li, s.ti);
    var r2 = app.L.qs.slice();

    var k1 = r1.map(function (q) { return app.lQuestionKey(q.c); });
    var k2 = r2.map(function (q) { return app.lQuestionKey(q.c); });

    eq('I2 ' + label + ': the first round is the mathematically correct length', r1.length, expectedLen);
    eq('I2 ' + label + ': the second round is the mathematically correct length', r2.length, expectedLen);
    eq('I3 ' + label + ': no card is asked twice in the first round',
       uniq(r1.map(function (q) { return q.c.id; })).length, r1.length);
    eq('I3 ' + label + ': no card is asked twice in the second round',
       uniq(r2.map(function (q) { return q.c.id; })).length, r2.length);
    eq('I4 ' + label + ': the first round uses as many distinct prompts as it can',
       uniq(k1).length, Math.min(expectedLen, distinctKeys.length));
    eq('I4 ' + label + ': so does the second', uniq(k2).length, Math.min(expectedLen, distinctKeys.length));

    // ---- the minimum overlap this scope can possibly achieve ----
    // Priority order is: unheard distinct prompts, then heard distinct prompts,
    // then repeats of unheard prompts, then repeats of heard ones. Taking the
    // round from those four queues in turn is the whole calculation, and it is
    // done here from the corpus figures alone.
    var used = {}; k1.forEach(function (k) { used[k] = 1; });
    var tier = [0, 0, 0, 0], first = {};
    keyOfSource.forEach(function (k) {
      var isFirst = !first[k]; first[k] = 1;
      tier[(isFirst ? 0 : 2) + (used[k] ? 1 : 0)]++;
    });
    var left = expectedLen, expectedOverlap = 0;
    [[tier[0], 0], [tier[1], 1], [tier[2], 0], [tier[3], 1]].forEach(function (p) {
      var take = Math.min(left, p[0]); left -= take; if (p[1]) expectedOverlap += take;
    });
    eq('I5 ' + label + ': the second round reuses exactly the unavoidable minimum',
       overlapCount(k2, k1), expectedOverlap);
    // The simple closed form, for the ordinary case of a pool with room to spare.
    if (expectedLen <= distinctKeys.length) {
      eq('I5 ' + label + ': which is max(0, round - unheard prompts remaining)',
         expectedOverlap, Math.max(0, expectedLen - (distinctKeys.length - uniq(k1).length)));
    }

    if (expectedOverlap > 0) notFresh.push(label + ' (min overlap ' + expectedOverlap + ')');
    if (sources.length < REQUEST) thin.push(label + ' (' + sources.length + ' cards)');
    if (distinctKeys.length < REQUEST) fewKeys.push(label + ' (' + distinctKeys.length + ' prompts)');

    info(label + ': ' + sources.length + ' cards, ' + distinctKeys.length + ' distinct prompts, ' +
         (sources.length - distinctKeys.length) + ' same-prompt duplicates, round ' + expectedLen +
         ', minimum repeat ' + expectedOverlap);
  });

  info('scopes whose second round cannot be fully fresh: ' + (notFresh.length ? notFresh.join('; ') : 'none'));
  info('scopes with fewer than ' + REQUEST + ' cards: ' + (thin.length ? thin.join('; ') : 'none'));
  info('scopes with fewer than ' + REQUEST + ' distinct heard prompts: ' + (fewKeys.length ? fewKeys.join('; ') : 'none'));

  // Every ordinary vocabulary topic, reported as a would-be scope. None is
  // reachable as a Listening scope today; this is here so that a future phase
  // offering per-topic Listening arrives with the figures already in view.
  var tight = [];
  APP.VOCAB_SRC.forEach(function (lv) {
    lv.topics.forEach(function (t) {
      if (t.mature) return;
      var cards = t.cards.filter(function (c) { return U.eligibleFor(c, 'listen'); });
      var ks = uniq(cards.map(function (c) { return D.normalizeKey(U.mainAudioText(c)); }));
      var n = Math.min(REQUEST, cards.length);
      var minOv = Math.max(0, n - (ks.length - Math.min(n, ks.length)));
      if (minOv > 0) tight.push(lv.level + '/' + t.name + ' (' + cards.length + ' cards, min repeat ' + minOv + ')');
    });
  });
  info('vocabulary topics that could not offer a fully fresh second round if they ever became scopes: ' +
       tight.length + ' of ' + APP.VOCAB_SRC.reduce(function (a, lv) { return a + lv.topics.length; }, 0));
})();

// =========================================================================
// J. EVERYTHING ELSE ABOUT LISTENING IS UNCHANGED
// =========================================================================
(function () {
  var START = codeOnly(SRC.startListen);
  var RENDER = codeOnly(SRC.lRender);

  ok('J1 startListen still draws from the Listening pool',
     hasCode(START, 'poolFor(L.topicRef.src, "listen")'));
  ok('J1 startListen still builds its options through PP_DISTRACTOR',
     START.indexOf('PP_DISTRACTOR.buildOptions') !== -1);
  eq('J1 the builder is still called exactly once', countOf(START, 'PP_DISTRACTOR.buildOptions'), 1);
  ok('J1 it still asks for four options', hasCode(START, 'count:4'));
  ok('J1 it still injects the app shuffle into the builder', hasCode(START, 'shuffle:gShuffle'));
  ok('J1 it still passes the real heard-prompt rule', hasCode(START, 'heardOf:ppMainAudioText'));
  ok('J1 the whole pool is still offered as distractor candidates', hasCode(START, 'candidates:pool'));

  ok('J2 Listening still asks for at most fifteen questions',
     /lSelectQuestions\(\s*pool\s*,[^;]*?,\s*15\s*,\s*gShuffle\s*\)/.test(START));
  ok('J2 the selection is the scope\'s own history', hasCode(START, 'L_RECENT.get(scope)'));
  ok('J2 the round just chosen becomes what the next one avoids',
     /L_RECENT\.set\(\s*scope\s*,/.test(START));
  ok('J2 the scope key comes from the level and topic, not an index',
     hasCode(SRC.lScopeKey, 'lv.level') && hasCode(SRC.lScopeKey, 'topic.name'));

  ok('J3 every entry into a round still stops audio first', (function () {
    var stop = START.indexOf('stopAllAudio');
    if (stop === -1) return false;
    return ['show(', 'lRender(', 'L.i', 'L.li', 'L.qs', 'L.results']
      .every(function (e) { var at = START.indexOf(e); return at === -1 || at > stop; });
  })());
  ok('J3 no autoplay was introduced',
     START.indexOf('speakText') === -1 && START.indexOf('speakCardMain') === -1 &&
     START.indexOf('lPlayCurrent') === -1);

  ok('J4 first-attempt scoring is unchanged',
     hasCode(RENDER, 'if(!L.attempted) L.results[L.i]=true;'));
  ok('J4 a wrong answer still marks the question missed',
     hasCode(RENDER, 'L.attempted=true; L.results[L.i]=false;'));
  ok('J4 correctness is still the retained flag, not a string match',
     RENDER.indexOf('o.correct') !== -1);

  // No storage of any kind stands behind the previous-round memory, and no
  // migration was added for it. The whole Phase 3E surface is checked, not just
  // startListen.
  var PHASE = L_RECENT_SRC + SRC.lScopeKey + SRC.lQuestionKey + SRC.lSelectQuestions + SRC.startListen;
  ['localStorage', 'sessionStorage', 'indexedDB', 'document.cookie', 'JSON.parse', 'PP_MIGRATE']
    .forEach(function (api) {
      ok('J5 the previous-round memory does not touch ' + api, PHASE.indexOf(api) === -1);
    });
  ok('J5 it is a plain in-memory Map', /const\s+L_RECENT\s*=\s*new Map\(\)/.test(L_RECENT_SRC));
  // How MANY times index.html names L_RECENT is not asserted. A count is a fact
  // about typing, not about behaviour: refactoring the two calls into a helper,
  // or a later phase reading the memory somewhere legitimate, would fail it while
  // changing nothing a learner can observe. What the memory actually DOES -
  // per-scope isolation, one round of history, a clean slate on reload - is
  // executed through the real startListen in section H, and the two source checks
  // above pin the reads and writes that startListen must perform.
  ok('J5 the saved-progress schema version is untouched by this phase',
     PHASE.indexOf('SCHEMA_VERSION') === -1 && PHASE.indexOf('STORE_KEY') === -1);

  // The helper is pure: it reaches for no app state and no randomness of its own.
  // These are NEGATIVE checks on purpose - "this name must not appear" stays true
  // however the code is arranged, where "this expression must appear" does not.
  var SEL = codeOnly(SRC.lSelectQuestions);
  ['Math.random', 'document', 'window.', 'L.qs', 'L.i', 'L_RECENT', '$(']
    .forEach(function (bad) {
      ok('J6 lSelectQuestions does not use ' + bad, SEL.indexOf(bad) === -1);
    });
  // How the copy is made is deliberately NOT pinned. `shuffle(pool.slice())` and
  //     var copy = pool.slice(); var order = shuffle(copy);
  // are the same promise written two ways, and only the promise is permanent:
  // sections A-G already EXECUTE it - the caller's pool, its cards and the
  // history all survive untouched, the returned array is fresh, and the injected
  // shuffle alone decides the order.
})();

// ---------- report ----------
INFO.forEach(function (l) { console.log(l); });
LOG.forEach(function (l) { console.log(l); });
console.log('Listening variety tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
if (FAIL) throw new Error(FAIL + ' assertion(s) failed');
