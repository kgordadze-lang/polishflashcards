// Deterministic tests for AUTHORED SENSE GROUPS - Priority 3 Phase 4E.
// Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_sense_groups.js
// Exit status is 0 only if every assertion passes (printed at the end).
//
// WHAT THIS FILE IS FOR
// Phase 4D made an option SET safe against everything a string comparison can
// see: the same card twice, the same stable id, the same gloss after
// normalisation, the same prompt after normalisation. What it cannot see is two
// DIFFERENT sentences that share one true meaning. A learner hearing one Polish
// farewell was offered "See you / Bye for now" and "See you (soon)" side by side,
// picked the wrong one of two right answers, and was marked wrong for it.
//
// No fold of those two strings makes them equal, and every heuristic that would
// catch them - splitting on slashes, substring containment, counting shared
// words - also catches "teacher (m)" beside "teacher (f)" and "married (man /
// woman)" beside "single / unmarried (man / woman)", which are exactly the
// questions worth asking. The corpus audit that preceded this phase caught 441
// candidate pairs and found 23 genuine conflicts among them; nothing computable
// from the text alone draws that line.
//
// So the line is DRAWN BY HAND. A card may declare `senseGroups: ["some-key"]`,
// meaning only: cards sharing this key must never be offered as options in one
// question. It does NOT mean the Polish is interchangeable, that Type It should
// accept either answer, that the cards are duplicates, or that the register,
// grammar or usage matches.
//
// HOW IT TESTS
// Two halves, the same split the other distractor suites use.
//   Synthetic fixtures pin the CONTRACT (A-H, L): no shipping card decides any
//   of those assertions, so the rules stay readable and stay true for metadata
//   nobody has authored yet.
//   The real corpus is then swept through the real builder (I-K). The authored
//   groups are DISCOVERED on every run, never remembered as a number, so a group
//   added later is covered the day it lands and an editor who removes one does
//   not fail a suite for improving the data.
//
// SCOPE - what deliberately is NOT here
// The three text rules (label, prompt, identity), the exhaustive search itself
// and the Listening corpus sweep belong to tests/test_distractors.js. Everything
// the Mixed Quiz does with the records - rendering, scoring, announcing,
// requeueing - belongs to tests/test_mixed_distractors.js. This file owns one
// question: does an authored sense group keep two cards out of one question,
// everywhere, without any inference being added anywhere?
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
var DISTRACTOR_SRC = readFile(ROOT + 'pp-distractor.js');
var VALIDATOR_SRC = readFile(ROOT + 'validate_content.py');

// index.html loads these in this order; pp-distractor.js may read PP_USAGE.
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
// Comments are prose; a rule must be visible in CODE, not only described.
function codeOnly(s) {
  return s.replace(/\/\*[\s\S]*?\*\//g, ' ').replace(/(^|[^:])\/\/[^\n]*/g, '$1 ');
}
function squash(s) { return s.replace(/\s+/g, ''); }
function hasCode(hay, needle) { return squash(hay).indexOf(squash(needle)) !== -1; }
// The Python equivalent of codeOnly(), for the same reason: a rule must be visible
// in CODE, not merely described. It matters in both directions here. A comment that
// NAMES a removed construct - "`set(sg)` raises TypeError on {}" - is worth keeping,
// and must not fail the test that the construct is gone; equally, writing that
// sentence must not be enough to PASS a test about what the code does.
// Quote-aware: validate_content.py is full of f-strings containing '#', and cutting
// at the first one would silently delete real code from the line.
function pyCodeOnly(src) {
  return src.split('\n').map(function (line) {
    var q = null;
    for (var i = 0; i < line.length; i++) {
      var ch = line[i];
      if (q) {
        if (ch === '\\') { i++; continue; }
        if (ch === q) q = null;
      } else if (ch === '"' || ch === "'") {
        q = ch;
      } else if (ch === '#') {
        return line.slice(0, i);
      }
    }
    return line;
  }).join('\n');
}
// Same brace-matching extractor the other index.html suites use.
function extractFunction(src, name) {
  var start = src.indexOf('function ' + name + '(');
  if (start === -1) throw new Error('extract: function ' + name + ' not found in index.html');
  var open = src.indexOf('{', src.indexOf(')', start)), depth = 0;
  for (var j = open; j < src.length; j++) {
    if (src[j] === '{') depth++;
    else if (src[j] === '}') { depth--; if (depth === 0) return src.slice(start, j + 1); }
  }
  throw new Error('extract: unbalanced braces in ' + name);
}

// ---------- injected randomness ----------
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
var SEEDS = [1, 2, 3, 7, 11];

function nk(s) { return D.normalizeKey(s); }
function heardKeyOf(card) { return nk(U.mainAudioText(card)); }
function item(card, topic) { return { c: card, topic: topic || 'T' }; }
function labelsOf(b) { return b.options.map(function (o) { return o.label; }); }
function idsOf(b) { return b.options.map(function (o) { return o.id; }); }
// Every fixture build goes through here, so "the builder never throws on
// malformed metadata" is proved by construction rather than asserted once.
var THREW = [];
function build(spec, where) {
  try {
    return D.buildOptions(spec);
  } catch (e) {
    THREW.push((where || 'unnamed') + ': ' + e);
    return { options: [], correct: null };
  }
}
// The set of sense keys an option set actually carries, normalised the way the
// builder compares them. Read off the CARDS, never off the records, because a
// record deliberately does not carry them.
function senseKeysOf(card) {
  var raw = card && card.senseGroups;
  if (!Array.isArray(raw)) return [];
  var out = [], seen = {};
  raw.forEach(function (g) {
    if (typeof g !== 'string') return;
    var k = g.trim().toLowerCase();
    if (!k || seen[k]) return;
    seen[k] = 1; out.push(k);
  });
  return out;
}
// Any key held by two different options in one set is a defect, whichever
// options they are - the correct one included.
function repeatedSenseIn(cards) {
  var seen = {}, dups = [];
  cards.forEach(function (c) {
    senseKeysOf(c).forEach(function (k) {
      if (seen[k]) dups.push(k); else seen[k] = 1;
    });
  });
  return dups;
}

// =========================================================================
// A. METADATA NORMALISATION - defensive at runtime, strict in the corpus
// =========================================================================
// The runtime never throws and never repairs. A malformed value is simply not a
// restriction, so the worst case is the question Phase 4D already shipped. The
// corpus is held to a far stricter standard by validate_content.py; section A
// checks both halves, because either one alone would be the wrong bargain.
(function () {
  // One free card per fixture family, so a build that drops everything is visible.
  function card(id, pl, en, groups) {
    var c = { id: id, pl: pl, en: en };
    if (arguments.length > 3) c.senseGroups = groups;
    return c;
  }
  function poolOf(cards) { return cards.map(function (c) { return item(c, 'T'); }); }
  function builtFrom(cards, where) {
    var pool = poolOf(cards);
    return build({ correct: pool[0], candidates: pool, count: 4, shuffle: KEEP,
                   heardOf: U.mainAudioText }, where);
  }

  // A1. absent metadata is no restriction at all.
  var a1 = builtFrom([card('sg-a-1', 'p1', 'one'), card('sg-a-2', 'p2', 'two'),
                      card('sg-a-3', 'p3', 'three'), card('sg-a-4', 'p4', 'four')], 'A1');
  eq('A1 a corpus with no sense groups still fills a question', a1.options.length, 4);

  // A2. one group, honoured.
  var a2 = builtFrom([card('sg-b-1', 'p1', 'one', ['shared']),
                      card('sg-b-2', 'p2', 'two', ['shared']),
                      card('sg-b-3', 'p3', 'three'), card('sg-b-4', 'p4', 'four')], 'A2');
  eq('A2 one declared group removes the conflicting card', idsOf(a2).indexOf('sg-b-2'), -1);
  eq('A2 the rest of the question is unaffected', a2.options.length, 3);

  // A3. several groups on one card, each independently binding.
  var a3 = builtFrom([card('sg-c-1', 'p1', 'one', ['g1', 'g2']),
                      card('sg-c-2', 'p2', 'two', ['g1']),
                      card('sg-c-3', 'p3', 'three', ['g2']),
                      card('sg-c-4', 'p4', 'four', ['g3'])], 'A3');
  eq('A3 a card in two groups conflicts with members of both',
     idsOf(a3).filter(function (i) { return i === 'sg-c-2' || i === 'sg-c-3'; }), []);
  ok('A3 an unrelated third group is untouched', idsOf(a3).indexOf('sg-c-4') !== -1);

  // A4. duplicate entries collapse; they are not two separate memberships.
  var a4 = builtFrom([card('sg-d-1', 'p1', 'one', ['dup', 'dup', 'dup']),
                      card('sg-d-2', 'p2', 'two', ['dup']),
                      card('sg-d-3', 'p3', 'three'), card('sg-d-4', 'p4', 'four')], 'A4');
  eq('A4 a repeated key behaves exactly like one key', idsOf(a4).indexOf('sg-d-2'), -1);
  eq('A4 a repeated key does not shrink the rest of the question', a4.options.length, 3);

  // A5. case and surrounding whitespace fold - MALFORMED fixtures only. Nothing
  // shaped like this may be committed; validate_content.py rejects all of it.
  [['  SHARED  ', 'shared'], ['Shared', 'sHaReD'], ['\tshared\n', 'shared']].forEach(function (pair, n) {
    var b = builtFrom([card('sg-e' + n + '-1', 'p1', 'one', [pair[0]]),
                       card('sg-e' + n + '-2', 'p2', 'two', [pair[1]]),
                       card('sg-e' + n + '-3', 'p3', 'three'),
                       card('sg-e' + n + '-4', 'p4', 'four')], 'A5#' + n);
    eq('A5 ' + JSON.stringify(pair[0]) + ' and ' + JSON.stringify(pair[1]) + ' are one group',
       idsOf(b).indexOf('sg-e' + n + '-2'), -1);
  });

  // A6. anything that is not a usable key is not a restriction.
  var JUNK = [null, undefined, 'shared', 5, {}, { 0: 'shared' }, true, [], [''], ['   '],
              [null], [5], [{}], [[]], ['ok', null, 5]];
  JUNK.forEach(function (junk, n) {
    var a = { id: 'sg-f' + n + '-1', pl: 'p1', en: 'one' };
    var b = { id: 'sg-f' + n + '-2', pl: 'p2', en: 'two' };
    a.senseGroups = junk; b.senseGroups = junk;
    var built = builtFrom([a, b, card('sg-f' + n + '-3', 'p3', 'three'),
                           card('sg-f' + n + '-4', 'p4', 'four')], 'A6#' + n);
    // ['ok', null, 5] holds one USABLE key on both cards, so it is a real group.
    var expect = (Array.isArray(junk) && junk.indexOf('ok') !== -1) ? 3 : 4;
    eq('A6 senseGroups=' + JSON.stringify(junk) + ' yields ' + expect + ' options',
       built.options.length, expect);
  });
  eq('A7 no fixture, however malformed, made the builder throw', THREW, []);

  // A8. the corpus is NOT allowed to be this sloppy. The runtime's leniency is a
  // safety net for data that escaped review, never a licence to author it.
  var V = VALIDATOR_SRC;
  ok('A8 validate_content.py rejects a non-array senseGroups',
     /senseGroups.*must be a non-empty array/.test(V) && V.indexOf('isinstance(sg, list)') !== -1);
  ok('A8 validate_content.py rejects an empty array', V.indexOf('or not sg:') !== -1);
  ok('A8 validate_content.py rejects non-string entries',
     /entries must be strings/.test(V) && V.indexOf('isinstance(g, str)') !== -1);
  ok('A8 validate_content.py rejects blank entries', /must not be blank/.test(V));
  ok('A8 validate_content.py rejects surrounding whitespace',
     /surrounding whitespace/.test(V) && V.indexOf('g != g.strip()') !== -1);
  ok('A8 validate_content.py rejects keys outside lowercase kebab-case',
     /not lowercase kebab-case/.test(V) && V.indexOf('SENSE_GROUP_RE') !== -1);
  ok('A8 validate_content.py rejects duplicate keys on one card', /duplicate keys/.test(V));
  ok('A8 validate_content.py rejects a group with fewer than two cards',
     /at least two distinct cards/.test(V));
  ok('A8 validate_content.py does not pin how many groups exist',
     !/len\(sense_groups\)\s*[=!<>]=\s*\d/.test(V));

  // A9. THE VALIDATOR MUST REPORT BAD DATA, NOT CRASH ON IT.
  // `senseGroups: [{}]` and `senseGroups: [[]]` are malformed in the ordinary way -
  // the entry is not a string - and the per-entry check already says so. But the
  // duplicate check used to hash the RAW array, and a dict or a list is unhashable,
  // so Python raised TypeError and the process died with a traceback before the
  // error it had already recorded could be printed. The author saw a crash instead
  // of the one-line reason, and a validator that crashes on invalid input is not
  // validating it.
  //
  // The fix is structural, so the assertions are structural: duplicate tracking may
  // only ever see a key that has already survived every other check. The elif chain
  // is what guarantees it - a rejected entry can never fall through to the
  // seen-set - so the chain's ORDER is the thing worth pinning.
  var VCODE = pyCodeOnly(V);
  // the per-card block, so nothing elsewhere in the file can satisfy these by accident
  var sgStart = VCODE.indexOf('sg = c.get("senseGroups")');
  var sgEnd = VCODE.indexOf('va = c.get("variants")', sgStart);
  var BLOCK = sgStart !== -1 && sgEnd !== -1 ? VCODE.slice(sgStart, sgEnd) : '';
  ok('A9 the per-card senseGroups block was located', BLOCK.length > 0);
  ok('A9 validate_content.py never calls set(sg) directly', VCODE.indexOf('set(sg)') === -1);
  ok('A9 duplicate tracking uses its own seen-key set', hasCode(BLOCK, 'seen_keys = set()'));
  // Order is the proof: every rejection precedes the first mention of the seen-set.
  var iStr   = BLOCK.indexOf('isinstance(g, str)');
  var iBlank = BLOCK.indexOf('g.strip()');
  var iKebab = BLOCK.indexOf('SENSE_GROUP_RE.match(g)');
  var iDupe  = BLOCK.indexOf('g in seen_keys');
  var iAdd   = BLOCK.indexOf('seen_keys.add(g)');
  var iMap   = BLOCK.indexOf('sense_groups.setdefault(');
  ok('A9 every guard exists in the per-card block',
     [iStr, iBlank, iKebab, iDupe, iAdd, iMap].every(function (i) { return i !== -1; }));
  ok('A9 duplicate detection runs only after the entry is known to be a string',
     iStr < iDupe);
  ok('A9 a non-string entry can never reach the duplicate seen-set',
     iStr < iDupe && iStr < iAdd);
  ok('A9 an object or array entry is rejected before any hashing happens',
     iStr < iAdd && iStr < iMap);
  ok('A9 only a fully validated key is added to the seen-set',
     iBlank < iAdd && iKebab < iAdd);
  ok('A9 only a fully validated key reaches the group membership map',
     iStr < iMap && iKebab < iMap && iDupe < iMap);
  // The chain itself: one `if`, four `elif` rejections, then the duplicate `elif`,
  // then the single `else` that accepts. Any of these becoming a separate `if`
  // would let a rejected entry fall through to the hashing that used to crash.
  ok('A9 the guards are one elif chain, so a rejected entry cannot fall through',
     hasCode(BLOCK, 'if not isinstance(g, str):') &&
     hasCode(BLOCK, 'elif not g.strip():') &&
     hasCode(BLOCK, 'elif g != g.strip():') &&
     hasCode(BLOCK, 'elif not SENSE_GROUP_RE.match(g):') &&
     hasCode(BLOCK, 'elif g in seen_keys:'));
  ok('A9 the duplicate check is inside the per-entry loop, not a second pass over the array',
     BLOCK.indexOf('for g in sg:') !== -1 && BLOCK.indexOf('for g in sg:') < iDupe);
  ok('A9 the accepting branch does both the seen-set and the membership map',
     iAdd < iMap && (iMap - iAdd) < 200);
  // the kebab shape itself, checked rather than trusted
  var SG_RE = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
  [['greeting-whats-up', true], ['a', true], ['a1-b2', true],
   ['Greeting', false], ['greeting_whats_up', false], ['-lead', false], ['trail-', false],
   ['double--hyphen', false], ['has space', false], ['', false]].forEach(function (t) {
    eq('A8 kebab rule: ' + JSON.stringify(t[0]) + ' -> ' + t[1], SG_RE.test(t[0]), t[1]);
  });
})();

// =========================================================================
// B. THE CORRECT CARD VERSUS A DISTRACTOR
// =========================================================================
// Different gloss, different Polish, different id - and still one question too
// many, because the two share a declared answer sense.
(function () {
  var RIGHT = { id: 'sg-b1', pl: 'zzz', en: 'one way of saying it', senseGroups: ['same-sense'] };
  var TWIN  = { id: 'sg-b2', pl: 'yyy', en: 'a different way of saying it', senseGroups: ['same-sense'] };
  var POOL = [item(RIGHT), item(TWIN),
              item({ id: 'sg-b3', pl: 'www', en: 'alpha' }),
              item({ id: 'sg-b4', pl: 'vvv', en: 'beta' }),
              item({ id: 'sg-b5', pl: 'uuu', en: 'gamma' })];
  ok('B1 the fixture really is three different things',
     RIGHT.en !== TWIN.en && RIGHT.pl !== TWIN.pl && RIGHT.id !== TWIN.id);
  ok('B1 and normalisation cannot fold either pair',
     nk(RIGHT.en) !== nk(TWIN.en) && nk(RIGHT.pl) !== nk(TWIN.pl));
  SEEDS.forEach(function (s) {
    var b = build({ correct: POOL[0], candidates: POOL, count: 4,
                    shuffle: seededShuffle(s), heardOf: U.mainAudioText }, 'B seed ' + s);
    eq('B2 seed ' + s + ': the grouped twin never joins the answer', idsOf(b).indexOf('sg-b2'), -1);
    eq('B2 seed ' + s + ': the question is still full', b.options.length, 4);
    eq('B2 seed ' + s + ': exactly one option is correct',
       b.options.filter(function (o) { return o.correct; }).length, 1);
  });
  // Asked from OUTSIDE the group, both members are ordinary distractors again -
  // but still only one at a time, because the group binds them to each other too.
  var sawB1 = false, sawB2 = false, together = [];
  SEEDS.concat([13, 17, 23, 29]).forEach(function (s) {
    var other = build({ correct: POOL[2], candidates: POOL, count: 4,
                        shuffle: seededShuffle(s), heardOf: U.mainAudioText }, 'B3 seed ' + s);
    var got = idsOf(other);
    if (got.indexOf('sg-b1') !== -1) sawB1 = true;
    if (got.indexOf('sg-b2') !== -1) sawB2 = true;
    if (got.indexOf('sg-b1') !== -1 && got.indexOf('sg-b2') !== -1) together.push(s);
    eq('B3 seed ' + s + ': a question outside the group is still full', other.options.length, 4);
  });
  ok('B3 the group does not make either member globally unusable', sawB1 && sawB2);
  eq('B3 but the two never appear in one question', together, []);
})();

// =========================================================================
// C. TWO DISTRACTORS - the rule is about the SET, not about the answer
// =========================================================================
(function () {
  var RIGHT = { id: 'sg-c0', pl: 'aaa', en: 'the answer' };
  var G1 = { id: 'sg-c1', pl: 'bbb', en: 'first phrasing', senseGroups: ['pair-sense'] };
  var G2 = { id: 'sg-c2', pl: 'ccc', en: 'second phrasing', senseGroups: ['pair-sense'] };
  var POOL = [item(RIGHT), item(G1), item(G2),
              item({ id: 'sg-c3', pl: 'ddd', en: 'alpha' }),
              item({ id: 'sg-c4', pl: 'eee', en: 'beta' })];
  SEEDS.forEach(function (s) {
    var b = build({ correct: POOL[0], candidates: POOL, count: 4,
                    shuffle: seededShuffle(s), heardOf: U.mainAudioText }, 'C seed ' + s);
    var got = idsOf(b);
    ok('C1 seed ' + s + ': the two grouped distractors never appear together',
       !(got.indexOf('sg-c1') !== -1 && got.indexOf('sg-c2') !== -1));
    eq('C1 seed ' + s + ': neither is the correct card, and the question is still full',
       b.options.length, 4);
    eq('C1 seed ' + s + ': no sense key is repeated in the set',
       repeatedSenseIn(b.options.map(function (o) { return o.card; })), []);
  });
})();

// =========================================================================
// D. A CARD IN MORE THAN ONE GROUP
// =========================================================================
// One gloss can overlap two different neighbours in two different ways without
// those neighbours overlapping each other, so membership is a SET and the test
// is set intersection - not equality, and not "the first key wins".
(function () {
  var AB = { id: 'sg-d0', pl: 'aaa', en: 'in two groups', senseGroups: ['group-a', 'group-b'] };
  var ONLY_A = { id: 'sg-d1', pl: 'bbb', en: 'shares a', senseGroups: ['group-a'] };
  var ONLY_B = { id: 'sg-d2', pl: 'ccc', en: 'shares b', senseGroups: ['group-b'] };
  var ONLY_C = { id: 'sg-d3', pl: 'ddd', en: 'shares c', senseGroups: ['group-c'] };
  var FREE = { id: 'sg-d4', pl: 'eee', en: 'shares nothing' };
  var POOL = [item(AB), item(ONLY_A), item(ONLY_B), item(ONLY_C), item(FREE)];
  SEEDS.forEach(function (s) {
    var b = build({ correct: POOL[0], candidates: POOL, count: 4,
                    shuffle: seededShuffle(s), heardOf: U.mainAudioText }, 'D seed ' + s);
    var got = idsOf(b);
    eq('D1 seed ' + s + ': a member of group-a is excluded', got.indexOf('sg-d1'), -1);
    eq('D1 seed ' + s + ': a member of group-b is excluded', got.indexOf('sg-d2'), -1);
    ok('D1 seed ' + s + ': the unrelated group-c card is kept', got.indexOf('sg-d3') !== -1);
    ok('D1 seed ' + s + ': the ungrouped card is kept', got.indexOf('sg-d4') !== -1);
    eq('D1 seed ' + s + ': the honest answer is three options', b.options.length, 3);
  });
  // group-c and group-a do not conflict with EACH OTHER: asked from the other side,
  // both may sit in one question.
  var b2 = build({ correct: item(FREE), candidates: POOL, count: 4, shuffle: KEEP,
                   heardOf: U.mainAudioText }, 'D2');
  var got2 = idsOf(b2);
  ok('D2 members of different groups may share a question',
     got2.indexOf('sg-d1') !== -1 && got2.indexOf('sg-d3') !== -1);
  eq('D2 but the two-group card still excludes one of them',
     got2.indexOf('sg-d0') !== -1 && got2.indexOf('sg-d2') !== -1, false);
})();

// =========================================================================
// E. NO AUTOMATIC INFERENCE - overlap in the TEXT decides nothing
// =========================================================================
// Every pair here is one a heuristic would have refused. Each is a question
// worth asking, and each must survive.
(function () {
  var CASES = [
    ['a masculine and a feminine job title', 'someworder (m)', 'someworder (f)'],
    ['an adjective and its own negation', 'markedish', 'unmarkedish / not markedish'],
    ['a singular and a plural', 'a widget', 'widgets'],
    ['an aspect pair, both spelled out', 'to widget (ongoing)', 'to widget (completed)'],
    ['two domains, both named', 'sprocket (the tool)', 'sprocket (the fish)'],
    ['a bare verb and a phrase built on it', 'to widget', 'to widget up'],
    ['a substring of the other', 'flange', 'left flange'],
    ['every word shared, order changed', 'to flange, to sprocket', 'to sprocket, to flange']
  ];
  CASES.forEach(function (c, n) {
    var A = { id: 'sg-e' + n + '-a', pl: 'p' + n + 'a', en: c[1] };
    var B = { id: 'sg-e' + n + '-b', pl: 'p' + n + 'b', en: c[2] };
    var POOL = [item(A), item(B),
                item({ id: 'sg-e' + n + '-c', pl: 'p' + n + 'c', en: 'alpha' + n }),
                item({ id: 'sg-e' + n + '-d', pl: 'p' + n + 'd', en: 'beta' + n })];
    var b = build({ correct: POOL[0], candidates: POOL, count: 4, shuffle: KEEP,
                    heardOf: U.mainAudioText }, 'E#' + n);
    ok('E1 ' + c[0] + ' still share a question', idsOf(b).indexOf('sg-e' + n + '-b') !== -1);
    eq('E1 ' + c[0] + ' fills all four options', b.options.length, 4);
  });
  // The strongest form: identical token multiset, different string, no metadata.
  var X = { id: 'sg-e-x', pl: 'px', en: 'alpha beta gamma' };
  var Y = { id: 'sg-e-y', pl: 'py', en: 'gamma beta alpha' };
  var P = [item(X), item(Y), item({ id: 'sg-e-z', pl: 'pz', en: 'delta' }),
           item({ id: 'sg-e-w', pl: 'pw', en: 'epsilon' })];
  var bx = build({ correct: P[0], candidates: P, count: 4, shuffle: KEEP,
                   heardOf: U.mainAudioText }, 'E2');
  ok('E2 two glosses made of the same words are not inferred to be one sense',
     idsOf(bx).indexOf('sg-e-y') !== -1);
  // And the same two cards DO conflict the moment a human says so.
  X.senseGroups = ['declared']; Y.senseGroups = ['declared'];
  var by = build({ correct: P[0], candidates: P, count: 4, shuffle: KEEP,
                   heardOf: U.mainAudioText }, 'E3');
  eq('E3 the very same pair conflicts once a group is DECLARED',
     idsOf(by).indexOf('sg-e-y'), -1);
  delete X.senseGroups; delete Y.senseGroups;
})();

// =========================================================================
// F. THE LARGEST SAFE SET, NOT THE FIRST ONE FOUND
// =========================================================================
// Sense groups are a rule about PAIRS, which is precisely the shape that breaks
// a greedy fill. The first candidate here is compatible with the answer and
// blocks two of the three that follow; taking it costs the learner an option.
// A post-filter bolted onto chooseBest would return three. The search must
// backtrack over it and return four.
(function () {
  var RIGHT = { id: 'sg-f0', pl: 'aaa', en: 'the answer' };
  var BLOCKER = { id: 'sg-f1', pl: 'bbb', en: 'blocks two', senseGroups: ['g1', 'g2'] };
  var A = { id: 'sg-f2', pl: 'ccc', en: 'alpha', senseGroups: ['g1'] };
  var B = { id: 'sg-f3', pl: 'ddd', en: 'beta', senseGroups: ['g2'] };
  var C = { id: 'sg-f4', pl: 'eee', en: 'gamma' };
  var POOL = [item(RIGHT), item(BLOCKER), item(A), item(B), item(C)];

  var b = build({ correct: POOL[0], candidates: POOL, count: 4, shuffle: KEEP,
                  heardOf: U.mainAudioText }, 'F1');
  eq('F1 four options are found', b.options.length, 4);
  eq('F1 the greedy first pick was abandoned', idsOf(b).indexOf('sg-f1'), -1);
  eq('F1 the combination that fits is the one returned',
     idsOf(b).slice().sort(), ['sg-f0', 'sg-f2', 'sg-f3', 'sg-f4']);
  eq('F1 no sense key is repeated',
     repeatedSenseIn(b.options.map(function (o) { return o.card; })), []);

  // Same shape, every order: the answer must not depend on where the blocker lands.
  SEEDS.forEach(function (s) {
    var r = build({ correct: POOL[0], candidates: POOL, count: 4,
                    shuffle: seededShuffle(s), heardOf: U.mainAudioText }, 'F2 seed ' + s);
    eq('F2 seed ' + s + ': still four options', r.options.length, 4);
    eq('F2 seed ' + s + ': still no repeated sense',
       repeatedSenseIn(r.options.map(function (o) { return o.card; })), []);
  });

  // An honestly short pool: every candidate shares one key, so one distractor is
  // the true maximum. SHORT must mean the pool, never the search.
  var SHORT = [item({ id: 'sg-g0', pl: 'aaa', en: 'the answer' }),
               item({ id: 'sg-g1', pl: 'bbb', en: 'one', senseGroups: ['all'] }),
               item({ id: 'sg-g2', pl: 'ccc', en: 'two', senseGroups: ['all'] }),
               item({ id: 'sg-g3', pl: 'ddd', en: 'three', senseGroups: ['all'] })];
  SEEDS.forEach(function (s) {
    var r = build({ correct: SHORT[0], candidates: SHORT, count: 4,
                    shuffle: seededShuffle(s), heardOf: U.mainAudioText }, 'F3 seed ' + s);
    eq('F3 seed ' + s + ': a genuinely short pool returns two options', r.options.length, 2);
    eq('F3 seed ' + s + ': and it is honest about which', r.options.filter(function (o) {
      return o.correct; }).length, 1);
  });
  // The answer itself in the group: every candidate is then unusable.
  var ALONE = SHORT.slice();
  ALONE[0] = item({ id: 'sg-g0', pl: 'aaa', en: 'the answer', senseGroups: ['all'] });
  var alone = build({ correct: ALONE[0], candidates: ALONE, count: 4, shuffle: KEEP,
                      heardOf: U.mainAudioText }, 'F4');
  eq('F4 when the answer shares the only group, it stands alone', alone.options.length, 1);
  ok('F4 and the question is still marked, not blanked', alone.correct && alone.correct.correct);
})();

// =========================================================================
// G. TOPIC PREFERENCE SURVIVES
// =========================================================================
// Grouping must not quietly demote same-topic distractors: the near band is
// still tried first, and only a GROUPED near card is passed over.
(function () {
  var RIGHT = { id: 'sg-h0', pl: 'aaa', en: 'the answer' };
  var POOL = [item(RIGHT, 'NEAR'),
              item({ id: 'sg-h1', pl: 'bbb', en: 'near one' }, 'NEAR'),
              item({ id: 'sg-h2', pl: 'ccc', en: 'near two' }, 'NEAR'),
              item({ id: 'sg-h3', pl: 'ddd', en: 'near three' }, 'NEAR'),
              item({ id: 'sg-h4', pl: 'eee', en: 'far one' }, 'FAR'),
              item({ id: 'sg-h5', pl: 'fff', en: 'far two' }, 'FAR')];
  SEEDS.forEach(function (s) {
    var b = build({ correct: POOL[0], candidates: POOL, count: 4,
                    shuffle: seededShuffle(s), heardOf: U.mainAudioText }, 'G1 seed ' + s);
    eq('G1 seed ' + s + ': with no groups, every distractor is same-topic',
       b.options.filter(function (o) { return o.topic === 'FAR'; }).length, 0);
  });
  // Now group one near card with the answer. The other two near cards must still
  // be preferred, and exactly one far card is pulled in to finish the question.
  RIGHT.senseGroups = ['near-conflict'];
  POOL[1].c.senseGroups = ['near-conflict'];
  SEEDS.forEach(function (s) {
    var b = build({ correct: POOL[0], candidates: POOL, count: 4,
                    shuffle: seededShuffle(s), heardOf: U.mainAudioText }, 'G2 seed ' + s);
    var got = idsOf(b);
    eq('G2 seed ' + s + ': the grouped near card is dropped', got.indexOf('sg-h1'), -1);
    ok('G2 seed ' + s + ': the two safe near cards are still preferred',
       got.indexOf('sg-h2') !== -1 && got.indexOf('sg-h3') !== -1);
    eq('G2 seed ' + s + ': exactly one far card completes the question',
       b.options.filter(function (o) { return o.topic === 'FAR'; }).length, 1);
    eq('G2 seed ' + s + ': the question is still full', b.options.length, 4);
  });
  delete RIGHT.senseGroups; delete POOL[1].c.senseGroups;
})();

// =========================================================================
// H. THE INPUT AND OUTPUT CONTRACT
// =========================================================================
(function () {
  var CARDS = [{ id: 'sg-i0', pl: 'aaa', en: 'answer', senseGroups: ['k1'] },
               { id: 'sg-i1', pl: 'bbb', en: 'one', senseGroups: ['k1', 'k2'] },
               { id: 'sg-i2', pl: 'ccc', en: 'two', senseGroups: ['k2'] },
               { id: 'sg-i3', pl: 'ddd', en: 'three' },
               { id: 'sg-i4', pl: 'eee', en: 'four' }];
  var POOL = CARDS.map(function (c) { return item(c, 'T'); });
  var cardSnap = JSON.stringify(CARDS), poolSnap = JSON.stringify(POOL);
  var order = POOL.slice();
  var arrayIdentity = CARDS.map(function (c) { return c.senseGroups; });

  SEEDS.forEach(function (s) {
    build({ correct: POOL[0], candidates: POOL, count: 4,
            shuffle: seededShuffle(s), heardOf: U.mainAudioText }, 'H seed ' + s);
  });
  eq('H1 no card was mutated', JSON.stringify(CARDS), cardSnap);
  eq('H1 no pool item was mutated', JSON.stringify(POOL), poolSnap);
  eq('H1 the candidate array kept its order',
     POOL.every(function (x, i) { return order[i] === x; }), true);
  ok('H2 every senseGroups array is the SAME object it was',
     CARDS.every(function (c, i) { return c.senseGroups === arrayIdentity[i]; }));
  ok('H2 no senseGroups array was reordered or added to',
     CARDS[1].senseGroups.length === 2 && CARDS[1].senseGroups[0] === 'k1' &&
     CARDS[1].senseGroups[1] === 'k2');
  ok('H2 no card gained a property',
     CARDS.every(function (c) {
       return Object.keys(c).every(function (k) {
         return ['id', 'pl', 'en', 'senseGroups'].indexOf(k) !== -1;
       });
     }));

  var b = build({ correct: POOL[0], candidates: POOL, count: 4, shuffle: KEEP,
                  heardOf: U.mainAudioText }, 'H3');
  eq('H3 exactly one record is correct',
     b.options.filter(function (o) { return o.correct; }).length, 1);
  ok('H3 the returned correct record is the flagged option',
     b.correct && b.correct.correct === true && b.options.indexOf(b.correct) !== -1);
  var RECORD_KEYS = ['label', 'card', 'item', 'topic', 'id', 'correct'];
  var shapeBad = b.options.filter(function (o) {
    return Object.keys(o).sort().join(',') !== RECORD_KEYS.slice().sort().join(',');
  });
  eq('H4 records keep exactly their existing shape', shapeBad.length, 0);
  eq('H4 no record carries a senseGroups property',
     b.options.filter(function (o) {
       return Object.prototype.hasOwnProperty.call(o, 'senseGroups'); }).length, 0);
  ok('H4 every record still keeps its card, item and label',
     b.options.every(function (o) { return o.card && o.item && typeof o.label === 'string'; }));
})();

// =========================================================================
// I. THE CURRENT AUTHORED METADATA - discovered, never pinned
// =========================================================================
// Every reviewed group carries its reason here. The audit that produced them
// swept every pair of cards that can share one option pool; a pair was grouped
// only when one specific English answer sense is valid for BOTH cards, so more
// than one button beside the same prompt would be defensible. Pairs that merely
// share a word, a category, a gender, a number, an aspect or a domain - with the
// labels saying so - were deliberately left alone; section L keeps a sample of
// those honest.
var REVIEWED = {
  'greeting-whats-up':        'all three glosses offer a bare "what\'s up?"; the register notes do not change which answer is true',
  'farewell-see-you':         'all four are the same parting; "see you" is bare in each, and "nara" is literally short for "na razie"',
  'response-youre-welcome':   '"you\'re welcome" is a bare listed sense of both, so either button answers a thank-you',
  'response-okay':            'both glosses list a bare "okay" as an accepted reading',
  'response-all-good':        'both glosses list a bare "all good"',
  'money-cash':               '"cash" is bare in both; one is the neutral word, one the slang for it',
  'slang-money':              'two slang words for money, both glossed with a bare "money"',
  'slang-awesome':            'two slang intensifiers, both glossed with a bare "awesome"',
  'slang-dude':               'two informal words for a man, both glossed with a bare "dude"',
  'reaction-cringe':          'both reactions are glossed with a bare "cringe"',
  'reaction-darn':            'both minced oaths are glossed with a bare "darn"',
  'verb-to-return-give-back': 'the same two English verbs in swapped order - the closest pair in the corpus',
  'verb-to-eat':              '"to eat" is bare in both; the dietary verb lists it as its first sense',
  'body-part-arm':            'both body parts are glossed with a bare, unqualified "arm"',
  'housing-rent':             'both glosses begin with a bare "rent"',
  'time-later':               '"later" is bare in both, and the two adverbs genuinely overlap',
  'time-deadline':            '"deadline" is bare in both; one is the borrowed office word for the other',
  'weather-tornado':          '"tornado" is bare in both; one is the native term, one the loanword',
  'profession-doctor':        'one gloss names the gender and the other does not, so the unmarked "doctor" is a true answer for BOTH - unlike the marked (m)/(f) pairs, which stay ungrouped',
  'swear-the-hell':           '"the hell" is bare in both',
  'swear-to-talk-rubbish':    '"to talk rubbish" is bare in both',
  'swear-to-screw-it':        '"to screw it" is bare in both',
  'swear-not-give-a-damn':    '"to not give a f***" is bare in both'
};

// ---------- the pools a card can actually appear in, as production builds them ----------
var VOCAB_SRC = LEVELS.filter(function (lv) {
  return lv.topics.length && lv.topics.every(function (t) { return !t.kind; });
});
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
var LISTEN_POOLS = VOCAB_SRC.map(function (lv) {
  return { name: 'Listening ' + lv.level, src: [lv.level], items: poolFor([lv.level], 'listen') };
});
LISTEN_POOLS.push({ name: 'Listening All levels', src: null, items: poolFor(null, 'listen') });

// Every Mixed Quiz scope: the topic list's Quiz pill and Study's "Quiz this set".
var SCOPES = [];
LEVELS.forEach(function (lv, li) {
  lv.topics.forEach(function (t, ti) {
    if (!t.cards) return;
    if (t.kind && t.kind !== 'podcast') return;
    SCOPES.push({ li: li, ti: ti, level: lv.level, name: t.name, mature: !!t.mature });
  });
});

// Discovered from the shipping data, never listed here.
var AUTHORED = {};
var GROUPED_CARDS = [];
LEVELS.forEach(function (lv) {
  lv.topics.forEach(function (t) {
    (t.cards || []).forEach(function (c) {
      var keys = senseKeysOf(c);
      if (!keys.length) return;
      GROUPED_CARDS.push({ c: c, level: lv.level, topic: t.name });
      keys.forEach(function (k) { (AUTHORED[k] = AUTHORED[k] || []).push(c); });
    });
  });
});
var GROUP_KEYS = Object.keys(AUTHORED).sort();

info('authored sense groups in the corpus: ' + GROUP_KEYS.length +
     ' over ' + GROUPED_CARDS.length + ' card(s)');
GROUP_KEYS.forEach(function (k) {
  info('  ' + k + ': ' + AUTHORED[k].map(function (c) {
    return c.id + ' "' + c.en + '"'; }).join('  |  '));
  info('      reason: ' + (REVIEWED[k] || 'NO REVIEWED REASON RECORDED'));
});

(function () {
  var tooSmall = [], dupIds = [], badKey = [], dupKeyOnCard = [], noReason = [], unreachable = [];
  var SG_RE = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

  GROUP_KEYS.forEach(function (k) {
    var members = AUTHORED[k];
    var ids = members.map(function (c) { return c.id; });
    var uniq = {}; ids.forEach(function (i) { uniq[i] = 1; });
    if (Object.keys(uniq).length < 2) tooSmall.push(k);
    if (Object.keys(uniq).length !== ids.length) dupIds.push(k);
    if (!SG_RE.test(k)) badKey.push(k);
    if (!REVIEWED[k]) noReason.push(k);

    // A group that no supported pool can ever present twice restricts nothing;
    // it is either a typo or a leftover, and either way worth saying out loud.
    var reachable = false;
    LISTEN_POOLS.forEach(function (p) {
      if (reachable) return;
      var n = 0, seen = {};
      p.items.forEach(function (it) {
        if (uniq[it.c.id] && !seen[it.c.id]) { seen[it.c.id] = 1; n++; }
      });
      if (n >= 2) reachable = true;
    });
    SCOPES.forEach(function (s) {
      if (reachable) return;
      var topic = LEVELS[s.li].topics[s.ti];
      var shown = topic.cards.filter(function (c) { return U.eligibleFor(c, 'listen'); });
      var pool = shown.slice();
      if (pool.length < 4) pool = pool.concat(poolFor([LEVELS[s.li].level], 'listen')
                                              .map(function (x) { return x.c; }));
      var n = 0, seen = {};
      pool.forEach(function (c) { if (uniq[c.id] && !seen[c.id]) { seen[c.id] = 1; n++; } });
      if (n >= 2) reachable = true;
    });
    if (!reachable) unreachable.push(k);
  });

  // Every card's own list, read straight off the shipping data.
  GROUPED_CARDS.forEach(function (g) {
    var raw = g.c.senseGroups;
    if (!Array.isArray(raw) || !raw.length) { badKey.push(g.c.id + ' (not a non-empty array)'); return; }
    var seen = {};
    raw.forEach(function (x) {
      if (typeof x !== 'string' || x !== x.trim() || !x || !SG_RE.test(x)) badKey.push(g.c.id + ' ' + JSON.stringify(x));
      var low = String(x).trim().toLowerCase();
      if (seen[low]) dupKeyOnCard.push(g.c.id + ' ' + low);
      seen[low] = 1;
    });
  });

  eq('I1 every authored group names at least two distinct cards', tooSmall, []);
  eq('I1 no group lists the same card twice', dupIds, []);
  eq('I2 every authored key is lowercase kebab-case', badKey, []);
  eq('I2 no card repeats a key', dupKeyOnCard, []);
  eq('I3 every authored group has a reviewed reason recorded', noReason, []);
  eq('I4 every authored group can actually meet in a supported option pool', unreachable, []);
  // The reasons file must not drift into a list of groups that no longer exist.
  var stale = Object.keys(REVIEWED).filter(function (k) { return GROUP_KEYS.indexOf(k) === -1; });
  eq('I5 no reviewed reason survives its group', stale, []);
  ok('I6 the corpus actually authors at least one group (else this phase shipped nothing)',
     GROUP_KEYS.length > 0);
})();

// =========================================================================
// J. THE LISTENING CORPUS SWEEP
// =========================================================================
(function () {
  var bad = { sense: [], label: [], prompt: [], source: [], id: [], correct: [] };
  var short = [], questions = 0, byCount = {};
  LISTEN_POOLS.forEach(function (p) {
    SEEDS.forEach(function (seed) {
      var shuffle = seededShuffle(seed);
      p.items.forEach(function (correct) {
        var b = build({ correct: correct, candidates: p.items, count: 4,
                        shuffle: shuffle, heardOf: U.mainAudioText }, 'J ' + p.name);
        questions++;
        byCount[b.options.length] = (byCount[b.options.length] || 0) + 1;
        var where = p.name + ' [seed ' + seed + '] ' + correct.c.id;
        if (b.options.length !== 4) short.push(where + ' -> ' + b.options.length);
        if (b.options.filter(function (o) { return o.correct; }).length !== 1) bad.correct.push(where);
        var dups = repeatedSenseIn(b.options.map(function (o) { return o.card; }));
        if (dups.length) bad.sense.push(where + ' repeats ' + dups.join(','));
        var sc = [], si = {}, sl = {}, sp = {};
        b.options.forEach(function (o) {
          if (sc.indexOf(o.card) !== -1) bad.source.push(where);
          sc.push(o.card);
          if (o.id) { if (si[o.id]) bad.id.push(where); si[o.id] = 1; }
          var lk = nk(o.label); if (sl[lk]) bad.label.push(where); sl[lk] = 1;
          var pk = heardKeyOf(o.card); if (sp[pk]) bad.prompt.push(where); sp[pk] = 1;
        });
      });
    });
  });
  info('Listening questions built across ' + LISTEN_POOLS.length + ' pools x ' +
       SEEDS.length + ' seeds: ' + questions);
  info('Listening options per question: ' + Object.keys(byCount).sort().map(function (k) {
    return k + ' -> ' + byCount[k]; }).join(', '));
  info('Listening questions returning fewer than four options: ' + short.length +
       (short.length ? '\n            ' + short.slice(0, 20).join('\n            ') : ''));
  eq('J1 no Listening option set repeats a sense group', bad.sense.slice(0, 5), []);
  eq('J2 no Listening option set repeats a normalised label', bad.label.slice(0, 5), []);
  eq('J2 no Listening option set repeats a normalised heard prompt', bad.prompt.slice(0, 5), []);
  eq('J2 no Listening option set reuses a source card', bad.source.slice(0, 5), []);
  eq('J2 no Listening option set repeats a stable id', bad.id.slice(0, 5), []);
  eq('J3 every Listening question has exactly one correct record', bad.correct.slice(0, 5), []);
  eq('J4 no current Listening question underfills', short.slice(0, 10), []);
})();

// =========================================================================
// K. THE MIXED QUIZ CORPUS SWEEP
// =========================================================================
// The SHIPPING rBuildOptions, startRound and rRecord, lifted out of index.html and
// run over every scope a learner can start a round in. Only the four functions on
// the option path are extracted; the rendering, scoring and accessibility around
// them stay owned by tests/test_mixed_distractors.js, so this needs no DOM beyond
// the two labels startRound writes.
(function () {
  var NAMES = ['rBuildOptions', 'startRound', 'rRecord'];
  var SRC = {};
  NAMES.forEach(function (n) { SRC[n] = extractFunction(INDEX, n); });
  var rStateMatch = INDEX.match(/const\s+R\s*=\s*(\{[^}]*\})\s*;/);
  if (!rStateMatch) throw new Error('extract: Mixed Quiz state object R not found in index.html');
  var R = (0, eval)('(' + rStateMatch[1] + ')');

  var DOM = {};
  function el(id) { return DOM[id] || (DOM[id] = { textContent: '' }); }
  var SHUFFLE = KEEP;
  var MIXED = (new Function('$', 'show', 'R', 'LEVELS', 'poolFor', 'gShuffle', 'ppEligibleFor',
    'ppMainAudioText', 'stopAllAudio', 'rRender', 'PP_DISTRACTOR',
    NAMES.map(function (n) { return SRC[n]; }).join('\n') + '\n' +
    'return { startRound: function(a,b){ return startRound(a,b); },\n' +
    '         rRecord: function(q,r){ return rRecord(q,r); },\n' +
    '         rBuildOptions: function(a,b,c){ return rBuildOptions(a,b,c); } };'
  ))(el, function () {}, R, LEVELS,
     function (src, act) { return poolFor(src, act); },
     function (a) { return SHUFFLE(a); },
     function (c, a) { return U.eligibleFor(c, a); },
     function (c) { return U.mainAudioText(c); },
     function () {}, function () {}, D);

  var bad = { sense: [], label: [], prompt: [], source: [], id: [], correct: [], typed: [] };
  var retry = { sense: [], count: [], typed: [] };
  var short = [], questions = 0, byCount = {}, mutated = [];
  var SNAPSHOT = {};
  LEVELS.forEach(function (lv) {
    lv.topics.forEach(function (t) {
      (t.cards || []).forEach(function (c) { if (!SNAPSHOT[c.id]) SNAPSHOT[c.id] = JSON.stringify(c); });
    });
  });

  function checkSet(q, where, sink) {
    var promptOf = q.fmt === 'listen' ? U.mainAudioText : function (card) { return card ? card.pl : ''; };
    var dups = repeatedSenseIn(q.options.map(function (o) { return o.card; }));
    if (dups.length) sink.sense.push(where + ' repeats ' + dups.join(','));
    if (sink === bad) {
      if (q.options.filter(function (o) { return o.correct; }).length !== 1) bad.correct.push(where);
      var sc = [], si = {}, sl = {}, sp = {};
      q.options.forEach(function (o) {
        if (sc.indexOf(o.card) !== -1) bad.source.push(where);
        sc.push(o.card);
        if (o.id) { if (si[o.id]) bad.id.push(where); si[o.id] = 1; }
        var lk = nk(o.label); if (sl[lk]) bad.label.push(where); sl[lk] = 1;
        var pk = nk(promptOf(o.card)); if (sp[pk]) bad.prompt.push(where); sp[pk] = 1;
      });
    }
  }

  SCOPES.forEach(function (s) {
    SEEDS.forEach(function (seed) {
      SHUFFLE = seededShuffle(seed);
      DOM = {};
      MIXED.startRound(s.li, s.ti);
      var where = s.level + ' / ' + s.name + ' [seed ' + seed + ']';
      var asked = R.qs.slice();          // the round as first built, before any requeue
      asked.forEach(function (q) {
        if (q.fmt === 'type') {
          if (q.options.length) bad.typed.push(where + ' typed question carries options');
          return;
        }
        questions++;
        byCount[q.options.length] = (byCount[q.options.length] || 0) + 1;
        if (q.options.length !== 4) short.push(where + ' ' + q.c.id + ' -> ' + q.options.length);
        checkSet(q, where + ' ' + q.c.id, bad);
      });
      // Every question missed on the first try comes back once. The retry rebuilds
      // from the retained records, so its safety is re-proved rather than assumed.
      var before = R.qs.length;
      asked.forEach(function (q) { MIXED.rRecord(q, 'miss'); });
      R.qs.slice(before).forEach(function (q) {
        if (q.fmt === 'type') {
          if (q.options.length) retry.typed.push(where + ' requeued typed question gained options');
          return;
        }
        if (q.options.length !== 4) retry.count.push(where + ' ' + q.c.id + ' -> ' + q.options.length);
        checkSet(q, where + ' ' + q.c.id + ' [retry]', retry);
      });
    });
  });
  LEVELS.forEach(function (lv) {
    lv.topics.forEach(function (t) {
      (t.cards || []).forEach(function (c) {
        if (SNAPSHOT[c.id] && SNAPSHOT[c.id] !== JSON.stringify(c)) mutated.push(c.id);
      });
    });
  });

  info('Mixed Quiz scopes swept: ' + SCOPES.length + ' x ' + SEEDS.length + ' seeds');
  info('Mixed Quiz option-bearing questions built: ' + questions);
  info('Mixed Quiz options per question: ' + Object.keys(byCount).sort().map(function (k) {
    return k + ' -> ' + byCount[k]; }).join(', '));
  info('Mixed Quiz option-bearing questions returning fewer than four options: ' + short.length +
       (short.length ? '\n            ' + short.slice(0, 20).join('\n            ') : ''));
  eq('K1 no Mixed Quiz option set repeats a sense group', bad.sense.slice(0, 5), []);
  eq('K2 no Mixed Quiz option set repeats a normalised label', bad.label.slice(0, 5), []);
  eq('K2 no Mixed Quiz option set repeats a normalised prompt', bad.prompt.slice(0, 5), []);
  eq('K2 no Mixed Quiz option set reuses a source card', bad.source.slice(0, 5), []);
  eq('K2 no Mixed Quiz option set repeats a stable id', bad.id.slice(0, 5), []);
  eq('K3 every option-bearing question has exactly one correct record', bad.correct.slice(0, 5), []);
  eq('K3 typed questions never carry options', bad.typed.slice(0, 5), []);
  eq('K4 no current option-bearing question underfills', short.slice(0, 10), []);
  eq('K5 a requeued question is still sense-safe', retry.sense.slice(0, 5), []);
  eq('K5 a requeued question keeps its four options', retry.count.slice(0, 5), []);
  eq('K5 a requeued typed question gains no options', retry.typed.slice(0, 5), []);
  eq('K6 no source card was mutated by building a round', mutated.slice(0, 5), []);
})();

// =========================================================================
// L. THE REVIEWED FALSE POSITIVES
// =========================================================================
// Pairs the audit looked at and deliberately left alone. The claim here is only
// that no metadata binds them - NOT that they must co-occur in some random
// question, which no seed can promise and which the builder never guarantees.
(function () {
  var LEFT_UNGROUPED = [
    ['a1-about-me-024', 'a1-about-me-025', 'married vs single: opposites, and the shared "(man / woman)" is a gender note'],
    ['a1-about-me-026', 'a1-about-me-029', 'teacher (m) vs teacher (f): the labels state the difference'],
    ['a1-about-me-027', 'a1-about-me-030', 'doctor (m) vs doctor (f): both marked, so both are learnable'],
    ['a1-family-people-011', 'a1-family-people-022', 'close friend (m) vs (f): marked'],
    ['a1-family-people-013', 'a1-family-people-024', 'mate/colleague (m) vs (f): marked'],
    ['a2-work-education-001', 'a2-work-education-015', 'teacher (m) vs teacher (f): marked'],
    ['b1-culture-entertainment-012', 'b1-culture-entertainment-022', 'author (m) vs author (f): marked'],
    ['b1-relationships-008', 'b1-relationships-024', 'fiance vs fiancee: marked'],
    ['a2-character-traits-025', 'a2-character-traits-026', 'patient vs impatient: grammatical opposites'],
    ['b1-media-technology-006', 'b1-media-technology-007', 'to log in vs to log out: opposites'],
    ['a2-ecology-009', 'a2-ecology-010', 'glass the material vs a drinking glass: both domains named'],
    ['a2-health-body-007', 'a2-health-body-018', 'belly vs the organ: the parenthetical names the domain'],
    ['a1-first-verbs-011', 'a1-first-verbs-012', 'to know a fact vs a person: both domains named'],
    ['a1-first-verbs-006', 'a1-first-verbs-007', 'to go on foot vs by vehicle: both named'],
    ['a1-first-verbs-002', 'a1-first-verbs-005', 'to have vs to have to: a substring, not a sense'],
    ['a2-describing-past-002', 'a2-describing-past-008', 'I had vs I had to: a substring, not a sense'],
    ['a2-holidays-traditions-003', 'a2-holidays-traditions-004', 'Christmas vs Christmas Eve: distinct days']
  ];
  var BY_ID = {};
  LEVELS.forEach(function (lv) {
    lv.topics.forEach(function (t) { (t.cards || []).forEach(function (c) { BY_ID[c.id] = c; }); });
  });
  var missing = [], grouped = [];
  LEFT_UNGROUPED.forEach(function (row) {
    var a = BY_ID[row[0]], b = BY_ID[row[1]];
    if (!a || !b) { missing.push(row[0] + ' / ' + row[1]); return; }
    var ka = senseKeysOf(a), kb = senseKeysOf(b);
    var shared = ka.filter(function (k) { return kb.indexOf(k) !== -1; });
    if (shared.length) grouped.push(row[0] + ' / ' + row[1] + ' share ' + shared.join(','));
  });
  eq('L1 every reviewed false positive still exists in the corpus', missing, []);
  eq('L1 no reviewed false positive was given a shared sense group', grouped, []);
  info('reviewed "do not group" pairs re-checked: ' + LEFT_UNGROUPED.length);

  // The synthetic mirror, so the claim survives any editorial change to the corpus.
  var A = { id: 'sg-l1', pl: 'p1', en: 'someworder (m)' };
  var B = { id: 'sg-l2', pl: 'p2', en: 'someworder (f)' };
  var P = [item(A), item(B), item({ id: 'sg-l3', pl: 'p3', en: 'alpha' }),
           item({ id: 'sg-l4', pl: 'p4', en: 'beta' })];
  var b = build({ correct: P[0], candidates: P, count: 4, shuffle: KEEP,
                  heardOf: U.mainAudioText }, 'L2');
  ok('L2 an ungrouped marked pair still shares a question', idsOf(b).indexOf('sg-l2') !== -1);
})();

// =========================================================================
// M. PRODUCTION WIRING - the shipping code is what all of the above describes
// =========================================================================
(function () {
  var CODE = codeOnly(DISTRACTOR_SRC);
  ok('M1 the builder reads authored sense groups off the card',
     hasCode(CODE, 'card.senseGroups'));
  ok('M1 the extractor is an overridable spec slot with a default',
     hasCode(CODE, 'fn(s.senseOf, defaultSenseOf)'));
  ok('M2 membership is normalised into a set',
     CODE.indexOf('senseSetOf') !== -1 && hasCode(CODE, '.trim().toLowerCase()'));
  ok('M2 comparison is set INTERSECTION, not equality',
     CODE.indexOf('function sharesSense') !== -1 && hasCode(CODE, 'b.indexOf(a[i]) !== -1'));
  ok('M3 the answer is compared against every candidate',
     hasCode(CODE, 'sharesSense(rightSenses'));
  ok('M3 every pair of distractors is compared, inside compatible()',
     hasCode(codeOnly(DISTRACTOR_SRC.slice(DISTRACTOR_SRC.indexOf('function compatible'))),
             'sharesSense(c.s, cand.s)'));
  // chooseBest owns the decision: the rule is a pruning rule inside the search,
  // never a filter applied to a set the search already returned.
  var afterChoose = DISTRACTOR_SRC.slice(DISTRACTOR_SRC.indexOf('function chooseBest'));
  ok('M4 chooseBest does not post-filter its own result',
     codeOnly(afterChoose).indexOf('sharesSense') === -1);
  ok('M4 buildOptions returns chooseBest\'s answer unfiltered',
     hasCode(CODE, 'shuffle([right].concat(chooseBest(usable, total - 1)))'));

  // No inference of any kind was added.
  var BANNED = [
    ['slash splitting', /\.split\(\s*['"]\s*\/\s*['"]\s*\)/],
    ['parenthesis stripping', /\\\([^)]*\\\)|\/\\\([^\/]*\)\[\^\)\]/],
    ['token-overlap scoring', /\bjaccard\b|\boverlap\b|\bsimilarity\b/i],
    ['a synonym table', /\bsynonym|\bthesaurus/i]
  ];
  BANNED.forEach(function (row) {
    ok('M5 no ' + row[0] + ' heuristic was added to pp-distractor.js', !row[1].test(CODE));
  });
  ok('M5 the builder never reads a gloss to guess a sense',
     CODE.indexOf('card.en') === -1 || !/senseSetOf\([^)]*\.en/.test(CODE));
  ok('M5 sense keys are not folded by the learner-facing normaliser',
     !/senseSetOf[\s\S]{0,200}normalizeKey/.test(CODE));

  // Both call sites get the behaviour through the shared DEFAULT.
  var idxCode = codeOnly(INDEX);
  ok('M6 Listening calls the shared builder', hasCode(idxCode, 'PP_DISTRACTOR.buildOptions({'));
  ok('M6 the Mixed Quiz calls the shared builder through rBuildOptions',
     hasCode(codeOnly(extractFunction(INDEX, 'rBuildOptions')), 'PP_DISTRACTOR.buildOptions({'));
  eq('M7 index.html gained no sense-group logic of its own',
     idxCode.indexOf('senseGroups') === -1 && idxCode.indexOf('senseOf') === -1 &&
     idxCode.indexOf('sharesSense') === -1, true);
  eq('M7 neither call site overrides the sense extractor',
     /senseOf\s*:/.test(idxCode), false);
  ok('M8 sense groups are never rendered to the learner',
     INDEX.indexOf('senseGroups') === -1);
})();

// ---------- report ----------
INFO.forEach(function (l) { console.log(l); });
LOG.forEach(function (l) { console.log(l); });
console.log('Sense group tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
if (FAIL) throw new Error(FAIL + ' assertion(s) failed');
