// Corpus tests for the typed-answer ownership index. Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_answer_collisions.js
// Exit status is 0 only if every assertion passes (printed at the end).
//
// WHAT THIS FILE IS FOR
// tests/test_answer_validation.js owns the comparator CONTRACT against
// synthetic cards. This suite owns the two questions that only the real data
// can answer:
//
//   1. WHICH cards belong in the index (PP_USAGE.typedPracticeCards) - a card
//      the learner is never asked to type must never be able to turn a correct
//      answer into a wrong one;
//   2. WHAT the shipped vocabulary actually collides on - it enumerates every
//      group of different exact answers that fold to one key, PRINTS them, and
//      asserts every cross-card collision in that list is kept out of the
//      "almost" tier.
//
// Section 4 is a named regression for the pięć / piec pair that motivated the
// change, but nothing here assumes that pair is the only one: section 3 is
// generated from the data, so a collision introduced by future content is
// covered the day it lands.
//
// WHAT THIS FILE DOES NOT TEST
// No DOM, no scoring, no persistence, no audio. It loads the data files and the
// two shared helpers, nothing else.
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
    if (fm.fileExistsAtPath(candidates[i] + 'pp-answer.js')) return candidates[i];
  }
  return cwd + '/';
}
var ROOT = resolveRoot();

// index.html loads these in exactly this order and nothing else is needed here.
var window = {};
['data-a1.js', 'data-a2.js', 'data-b1.js', 'data-grammar.js', 'data-verbs.js',
 'data-scenarios.js', 'data-podcasts.js', 'pp-usage.js', 'pp-answer.js']
  .forEach(function (f) { (0, eval)(readFile(ROOT + f)); });
var LEVELS = window.PP_LEVELS;
var U = window.PP_USAGE;
var A = window.PP_ANSWER;

// ---------- tiny test framework (same shape as the other suites) ----------
var PASS = 0, FAIL = 0, LOG = [];
function ok(name, cond) { if (cond) { PASS++; } else { FAIL++; LOG.push('FAIL: ' + name); } }
function eq(name, a, b) {
  var sa = JSON.stringify(a), sb = JSON.stringify(b);
  ok(name + (sa === sb ? '' : '  (got ' + sa + ', want ' + sb + ')'), sa === sb);
}

// =========================================================================
// 1. THE CARD SET - what the index is built from
// =========================================================================
var CARDS = U.typedPracticeCards(LEVELS);
var byId = {};
CARDS.forEach(function (c) { byId[c.id] = c; });

ok('T1 the data files loaded', !!LEVELS && LEVELS.length > 0);
ok('T1 the typed-practice set is non-empty', CARDS.length > 0);
ok('T1 every card in it has a stable id', CARDS.every(function (c) { return !!c.id; }));
eq('T1 no card appears twice', Object.keys(byId).length, CARDS.length);
ok('T1 every card in it is production-eligible',
   CARDS.every(function (c) { return U.eligibleFor(c, 'mixed'); }));
ok('T1 no template is in it',
   CARDS.every(function (c) { return c.cardType !== 'template'; }));
ok('T1 no recognition-only card is in it',
   CARDS.every(function (c) { return !U.isRecognitionOnly(c); }));
ok('T1 no intro card is in it', CARDS.every(function (c) { return !c.intro; }));
ok('T1 every card has both sides', CARDS.every(function (c) { return !!c.pl && !!c.en; }));

// The two typed activities reach their cards differently, so the production
// code collects them separately and unions the results. Recompute both sides
// here, independently, and state where they currently agree - so a future
// divergence shows up as a failing assertion rather than a silent gap.
function typeItSide() {
  var out = [];
  LEVELS.filter(function (lv) {
    return lv.topics.length && lv.topics.every(function (t) { return !t.kind; });
  }).forEach(function (lv) {
    lv.topics.forEach(function (t) {
      if (t.mature) return;
      (t.cards || []).forEach(function (c) { if (U.eligibleFor(c, 'typeit')) out.push(c); });
    });
  });
  return out;
}
function mixedSide() {
  var out = [];
  LEVELS.forEach(function (lv) {
    lv.topics.forEach(function (t) {
      if (t.kind) return;                      // podcast rounds never offer a typed question
      (t.cards || []).forEach(function (c) { if (U.eligibleFor(c, 'mixed')) out.push(c); });
    });
  });
  return out;
}
var T_SIDE = typeItSide(), M_SIDE = mixedSide();
var inSet = function (list) {
  var s = {}; list.forEach(function (c) { s[c.id] = true; }); return s;
};
var tIds = inSet(T_SIDE), mIds = inSet(M_SIDE), uIds = inSet(CARDS);
ok('T1 every Type It card is in the index set',
   T_SIDE.every(function (c) { return uIds[c.id]; }));
ok('T1 every Mixed Quiz typed card is in the index set',
   M_SIDE.every(function (c) { return uIds[c.id]; }));
ok('T1 the index set adds nothing neither activity can ask for',
   CARDS.every(function (c) { return tIds[c.id] || mIds[c.id]; }));
// Today the two agree on the CARD rule (both ask for production) and differ only
// on reach: the Mixed Quiz gets to the mature topic through the study screen's
// gate, Type It never draws it. Stated as a fact, not relied on.
ok('T1 Type It cards are a subset of the Mixed Quiz typed cards',
   T_SIDE.every(function (c) { return mIds[c.id]; }));
ok('T1 the extra cards are exactly the gated (mature) ones',
   M_SIDE.filter(function (c) { return !tIds[c.id]; })
     .every(function (c) { return U.eligibleFor(c, 'typeit'); }));
console.log('  [info] typed-practice cards: ' + CARDS.length +
            ' (Type It ' + T_SIDE.length + ', Mixed Quiz typed ' + M_SIDE.length + ')');

// cards the data has but no typed activity can ask for
var ALL = [];
LEVELS.forEach(function (lv) {
  lv.topics.forEach(function (t) { (t.cards || []).forEach(function (c) { ALL.push({ c: c, t: t }); }); });
});
var EXCLUDED = ALL.filter(function (x) { return !uIds[x.c.id]; });
ok('T1 the corpus really does contain cards that are excluded', EXCLUDED.length > 0);
ok('T1 every excluded card has a reason', EXCLUDED.every(function (x) {
  return !!x.t.kind || x.c.cardType === 'template' || U.isRecognitionOnly(x.c) ||
         !!x.c.intro || !x.c.pl || !x.c.en || !x.c.id;
}));
console.log('  [info] cards excluded from the typed index: ' + EXCLUDED.length + ' of ' + ALL.length);

// =========================================================================
// 2. THE INDEX
// =========================================================================
var IDX = A.buildIndex(CARDS);
var KEYS = Object.keys(IDX.owners);
ok('T2 the index has keys', KEYS.length > 0);
ok('T2 every key is its own normalized form',
   KEYS.every(function (k) { return A.normalize(k) === k; }));
ok('T2 no key is empty', KEYS.every(function (k) { return k !== ''; }));
ok('T2 every owner id is a card in the set',
   KEYS.every(function (k) { return IDX.owners[k].every(function (id) { return !!byId[id]; }); }));
ok('T2 no key lists the same owner twice', KEYS.every(function (k) {
  var seen = {};
  return IDX.owners[k].every(function (id) { if (seen[id]) return false; seen[id] = true; return true; });
}));
ok('T2 every card is reachable from the index', CARDS.every(function (c) {
  return A.accepted(c).some(function (a) {
    var k = A.normalize(a);
    return k && IDX.owners[k] && IDX.owners[k].indexOf(c.id) !== -1;
  });
}));

// =========================================================================
// 3. EVERY FOLD COLLISION IN THE SHIPPED VOCABULARY
// Generated from the data, so this section grows by itself when content does.
// =========================================================================
var byFold = {};
KEYS.forEach(function (k) { var f = A.fold(k); (byFold[f] = byFold[f] || []).push(k); });
var GROUPS = Object.keys(byFold).filter(function (f) { return byFold[f].length > 1; }).sort();

console.log('  [info] fold-collision groups in the current corpus: ' + GROUPS.length);
GROUPS.forEach(function (f) {
  console.log('  [info]   fold "' + f + '" <- ' + byFold[f].map(function (k) {
    return '"' + k + '" [' + IDX.owners[k].join(' ') + ']';
  }).join('  |  '));
});

// For every group, every ordered pair of distinct members, and every card that
// owns one member but not the other: typing the other member must be "wrong".
// It would otherwise reach the learner as "almost" - a real word reported as a
// near-miss for a different real word.
var crossPairs = 0, notWrong = [], notAlmostWithout = [];
GROUPS.forEach(function (f) {
  var members = byFold[f];
  members.forEach(function (mine) {
    members.forEach(function (typed) {
      if (mine === typed) return;
      IDX.owners[mine].forEach(function (id) {
        if (IDX.owners[typed].indexOf(id) !== -1) return;   // this card accepts both: not a collision
        var card = byId[id];
        crossPairs++;
        if (A.classify(typed, card, IDX) !== 'wrong') notWrong.push(id + ' typed "' + typed + '"');
        if (A.classify(typed, card) !== 'almost') notAlmostWithout.push(id + ' typed "' + typed + '"');
      });
    });
  });
});
ok('T3 the corpus contains at least one cross-card fold collision', crossPairs > 0);
ok('T3 every live cross-card collision is wrong, not almost (' + crossPairs +
   ' checked, ' + notWrong.length + ' failing)', notWrong.length === 0);
ok('T3 and every one of them WOULD have been almost without the index (' +
   notAlmostWithout.length + ' unexplained)', notAlmostWithout.length === 0);
notWrong.slice(0, 10).forEach(function (s) { LOG.push('    still not wrong: ' + s); });

// =========================================================================
// 4. NAMED REGRESSION - the pair that motivated the change
// Looked up by stable id, and skipped (loudly) if the content ever drops it.
// =========================================================================
var FIVE = byId['a1-numbers-prices-005'];   // pięć
var BAKE = byId['a2-food-shopping-007'];    // piec
ok('T4 both cards of the known pair are still typeable content', !!FIVE && !!BAKE);
if (FIVE && BAKE) {
  ok('T4 they are the pair this regression is about',
     A.fold(FIVE.pl) === A.fold(BAKE.pl) && A.normalize(FIVE.pl) !== A.normalize(BAKE.pl));
  eq('T4 typing one for the other is wrong', A.classify(BAKE.pl, FIVE, IDX), 'wrong');
  eq('T4 the reverse direction is wrong too', A.classify(FIVE.pl, BAKE, IDX), 'wrong');
  eq('T4 each card still gets its own answer right', A.classify(FIVE.pl, FIVE, IDX), 'right');
  eq('T4 and so does the other', A.classify(BAKE.pl, BAKE, IDX), 'right');
  eq('T4 without the index both were only almost',
     [A.classify(BAKE.pl, FIVE), A.classify(FIVE.pl, BAKE)], ['almost', 'almost']);
  eq('T4 capitalisation and spacing do not evade the guard',
     A.classify('  ' + BAKE.pl.toUpperCase() + '  ', FIVE, IDX), 'wrong');
}

// =========================================================================
// 5. NOTHING CORRECT WAS BROKEN
// The index can only ever downgrade an "almost". Prove it over the whole
// corpus rather than over a sample.
// =========================================================================
var lostRight = [], changedAlmost = [];
CARDS.forEach(function (c) {
  A.accepted(c).forEach(function (a) {
    if (!A.normalize(a)) return;
    if (A.classify(a, c, IDX) !== 'right') lostRight.push(c.id + ' / "' + a + '"');
  });
  // the undiacriticked spelling of the canonical answer: still "almost"
  // everywhere except where it spells another card's exact answer
  var folded = A.fold(c.pl);
  if (!folded || A.normalize(c.pl) === folded) return;
  var was = A.classify(folded, c), now = A.classify(folded, c, IDX);
  if (was !== now) changedAlmost.push(c.id + ' "' + c.pl + '" typed "' + folded + '": ' + was + ' -> ' + now);
});
ok('T5 every accepted answer of every typed card is still right (' +
   lostRight.length + ' regressions)', lostRight.length === 0);
lostRight.slice(0, 10).forEach(function (s) { LOG.push('    no longer right: ' + s); });
ok('T5 every verdict the index changed went almost -> wrong',
   changedAlmost.every(function (s) { return s.indexOf('almost -> wrong') !== -1; }));
console.log('  [info] verdicts changed by the index: ' + changedAlmost.length);
changedAlmost.forEach(function (s) { console.log('  [info]   ' + s); });

// =========================================================================
// 6. TWO CARDS SHARING ONE EXACT ANSWER - common, and still right
// =========================================================================
var SHARED = KEYS.filter(function (k) { return IDX.owners[k].length > 1; });
ok('T6 the corpus really does teach the same word on several cards', SHARED.length > 0);
console.log('  [info] exact answers owned by more than one card: ' + SHARED.length);
var sharedBad = [];
SHARED.forEach(function (k) {
  IDX.owners[k].forEach(function (id) {
    if (A.classify(k, byId[id], IDX) !== 'right') sharedBad.push(id + ' / "' + k + '"');
  });
});
ok('T6 a shared exact answer is right for every card that accepts it (' +
   sharedBad.length + ' failures)', sharedBad.length === 0);
sharedBad.slice(0, 10).forEach(function (s) { LOG.push('    shared answer not right: ' + s); });

// =========================================================================
// 7. ELIGIBILITY - only a typeable card may create a collision
// Synthetic levels, so each rule is isolated. All fixture words are invented.
// =========================================================================
var asked = { id: 'q1', pl: 'ćwiks', en: 'the card being answered' };
function rival(id, extra) {
  var c = { id: id, pl: 'cwiks', en: 'a rival spelling' };
  for (var k in extra) c[k] = extra[k];
  return c;
}
function levelOf(topics) { return { level: 'Fixture', topics: topics }; }
function verdictWith(levels) {
  return A.classify('cwiks', asked, A.buildIndex(U.typedPracticeCards(levels)));
}
ok('T7 the fixtures collide at all', A.fold('ćwiks') === A.fold('cwiks'));

eq('T7 with no rival card at all it is almost',
   verdictWith([levelOf([{ name: 'T', cards: [asked] }])]), 'almost');
eq('T7 an ELIGIBLE rival card makes it wrong',
   verdictWith([levelOf([{ name: 'T', cards: [asked, rival('q2')] }])]), 'wrong');
eq('T7 a template rival creates no collision',
   verdictWith([levelOf([{ name: 'T', cards: [asked, rival('q3', { cardType: 'template' })] }])]), 'almost');
eq('T7 a recognition-only rival creates no collision',
   verdictWith([levelOf([{ name: 'T', cards: [asked, rival('q4', { production: 'recognition-only' })] }])]), 'almost');
eq('T7 an intro card creates no collision',
   verdictWith([levelOf([{ name: 'T', cards: [asked, rival('q5', { intro: true })] }])]), 'almost');
eq('T7 a card missing its English side creates no collision',
   verdictWith([levelOf([{ name: 'T', cards: [asked, { id: 'q6', pl: 'cwiks' }] }])]), 'almost');
eq('T7 a rival with no stable id creates no collision',
   verdictWith([levelOf([{ name: 'T', cards: [asked, { pl: 'cwiks', en: 'no id' }] }])]), 'almost');
eq('T7 a grammar topic creates no collision',
   verdictWith([levelOf([{ name: 'T', cards: [asked] },
                         { name: 'G', kind: 'grammar', cards: [rival('q7')] }])]), 'almost');
eq('T7 a conversation topic creates no collision',
   verdictWith([levelOf([{ name: 'T', cards: [asked] },
                         { name: 'C', kind: 'convo', cards: [rival('q8')] }])]), 'almost');
eq('T7 a podcast topic creates no collision (its rounds never type)',
   verdictWith([levelOf([{ name: 'T', cards: [asked] },
                         { name: 'P', kind: 'podcast', cards: [rival('q9')] }])]), 'almost');
eq('T7 a synthetic practice shell creates no collision',
   verdictWith([levelOf([{ name: 'T', cards: [asked] },
                         { name: 'TI', kind: 'typeit', cards: [rival('q10')] }])]), 'almost');
// The mature topic is out of Type It's reach but IS reachable in the Mixed
// Quiz, behind the study screen's gate - so its cards do count as owners.
eq('T7 a gated (mature) topic still creates a collision, because the quiz reaches it',
   verdictWith([levelOf([{ name: 'T', cards: [asked] },
                         { name: 'M', mature: true, cards: [rival('q11')] }])]), 'wrong');
// A vocabulary topic sitting in a level that also holds kinded topics is still
// quizzable one topic at a time, so it counts too.
eq('T7 a vocabulary topic in a mixed-kind level still counts',
   verdictWith([levelOf([{ name: 'T', cards: [asked] }]),
                levelOf([{ name: 'V', cards: [rival('q12')] },
                         { name: 'G', kind: 'grammar', cards: [] }])]), 'wrong');
// and the collision may come from an acceptedAnswers entry
eq('T7 a rival that owns the word only through acceptedAnswers still collides',
   verdictWith([levelOf([{ name: 'T', cards: [asked,
     { id: 'q13', pl: 'zzz other', en: 'x', acceptedAnswers: ['cwiks'] }] }])]), 'wrong');

// selection purity
ok('T7 typedPracticeCards does not mutate the levels it reads', (function () {
  var lv = [levelOf([{ name: 'T', cards: [asked, rival('q14')] }])];
  var before = JSON.stringify(lv);
  U.typedPracticeCards(lv); U.typedPracticeCards(lv);
  return JSON.stringify(lv) === before;
})());
eq('T7 typedPracticeCards tolerates no argument', U.typedPracticeCards().length, 0);
eq('T7 typedPracticeCards tolerates an empty level list', U.typedPracticeCards([]).length, 0);
eq('T7 typedPracticeCards tolerates a topic with no cards',
   U.typedPracticeCards([levelOf([{ name: 'T' }])]).length, 0);
ok('T7 typedPracticeCards is deterministic',
   JSON.stringify(U.typedPracticeCards(LEVELS).map(function (c) { return c.id; })) ===
   JSON.stringify(U.typedPracticeCards(LEVELS).map(function (c) { return c.id; })));

// =========================================================================
// 8. THE HYPHEN NEAR MISS OVER THE SHIPPED VOCABULARY
// Section 3 does this for the diacritic near miss; this is the same question
// for the hyphen one, and it is generated from the data for the same reason:
// a hyphenated answer added by future content is covered the day it lands.
//
// For every typed-practice answer carrying a word-forming hyphen, every
// spelling the comparator will accept as a near miss is enumerated, PRINTED,
// and checked against three rules:
//   - the authored spelling stays "right";
//   - a generated spelling is "right" ONLY if the card already accepts it;
//   - every other generated spelling is "almost", or a "wrong" the ownership
//     index can account for - never an unexplained "wrong".
// The pięć / piec regression in section 4 above is unaffected by any of this
// and still runs: neither word carries a hyphen.
// =========================================================================
var HYPHEN_ROWS = [];
CARDS.forEach(function (c) {
  A.accepted(c).forEach(function (a, i) {
    if (typeof a !== 'string' || !A.hyphenVariants(a).length) return;
    HYPHEN_ROWS.push({ card: c, answer: a, canonical: i === 0 });
  });
});
var HYPHEN_CARDS = {};
HYPHEN_ROWS.forEach(function (r) { HYPHEN_CARDS[r.card.id] = true; });

ok('T8 the corpus contains at least one hyphenated typed-practice answer', HYPHEN_ROWS.length > 0);
console.log('  [info] typed-practice answers with a word-forming hyphen: ' + HYPHEN_ROWS.length +
            ' on ' + Object.keys(HYPHEN_CARDS).length + ' of ' + CARDS.length + ' cards');

var notRight = [], badVariant = [], unexplainedWrong = [], newlyRight = [];
HYPHEN_ROWS.forEach(function (r) {
  var c = r.card;
  var acceptedKeys = {};
  A.accepted(c).forEach(function (a) { if (typeof a === 'string') acceptedKeys[A.normalize(a)] = true; });

  if (A.classify(r.answer, c, IDX) !== 'right') notRight.push(c.id + ' / "' + r.answer + '"');

  var vs = A.hyphenVariants(r.answer);
  console.log('  [info]   ' + c.id + (r.canonical ? ' pl ' : ' acceptedAnswers ') +
              JSON.stringify(r.answer) + ' -> ' + vs.map(function (v) {
    return JSON.stringify(v) + ' ' + A.classify(v, c, IDX);
  }).join(', '));

  vs.forEach(function (v) {
    var got = A.classify(v, c, IDX);
    var alreadyAccepted = !!acceptedKeys[A.normalize(v)];
    if (got === 'right' && !alreadyAccepted) newlyRight.push(c.id + ' typed "' + v + '"');
    if (got !== 'almost' && got !== 'wrong' && !alreadyAccepted)
      badVariant.push(c.id + ' typed "' + v + '" -> ' + got);
    // a "wrong" here is only legitimate when the ownership index explains it:
    // the learner spelled some OTHER typeable card's answer exactly
    if (got === 'wrong' && !A.ownedByOther(IDX, v, c))
      unexplainedWrong.push(c.id + ' typed "' + v + '"');
  });
});
ok('T8 every hyphenated answer is still right as authored (' + notRight.length + ' regressions)',
   notRight.length === 0);
notRight.slice(0, 10).forEach(function (s) { LOG.push('    no longer right: ' + s); });
ok('T8 no generated spelling became right unless the card already accepts it (' +
   newlyRight.length + ' failures)', newlyRight.length === 0);
newlyRight.slice(0, 10).forEach(function (s) { LOG.push('    wrongly right: ' + s); });
ok('T8 every generated spelling is almost or wrong (' + badVariant.length + ' failures)',
   badVariant.length === 0);
ok('T8 and every wrong among them is one the index accounts for (' +
   unexplainedWrong.length + ' unexplained)', unexplainedWrong.length === 0);
unexplainedWrong.slice(0, 10).forEach(function (s) { LOG.push('    unexplained wrong: ' + s); });

// The blast radius: no OTHER answer in the corpus generates a spelling at all,
// so for every other card the near-miss tier is exactly the fold comparison it
// has always been.
var strays = [];
CARDS.forEach(function (c) {
  if (HYPHEN_CARDS[c.id]) return;
  A.accepted(c).forEach(function (a) {
    if (typeof a === 'string' && A.hyphenVariants(a).length) strays.push(c.id + ' / "' + a + '"');
  });
});
ok('T8 no other typed-practice answer generates a spelling (' + strays.length + ' found)',
   strays.length === 0);

// A hyphen the corpus never wrote must not become a near miss. Checked over the
// whole corpus, not a sample: one is inserted into every hyphen-free canonical
// answer and must still be wrong.
var insertedOk = 0, insertedBad = [];
CARDS.forEach(function (c) {
  if (typeof c.pl !== 'string' || A.hyphenVariants(c.pl).length) return;
  var at = -1;
  for (var i = 1; i < c.pl.length; i++) {
    if (!/\s/.test(c.pl.charAt(i - 1)) && !/\s/.test(c.pl.charAt(i))) { at = i; break; }
  }
  if (at === -1) return;
  var spliced = c.pl.slice(0, at) + '-' + c.pl.slice(at);
  if (A.accepted(c).some(function (a) {          // a card that genuinely accepts it is not a counterexample
    return typeof a === 'string' && A.normalize(a) === A.normalize(spliced);
  })) return;
  insertedOk++;
  if (A.classify(spliced, c, IDX) !== 'wrong') insertedBad.push(c.id + ' typed "' + spliced + '"');
});
ok('T8 the hyphen-insertion sweep actually covered the corpus', insertedOk > 0);
ok('T8 inserting a hyphen the card never wrote stays wrong (' + insertedOk +
   ' cards checked, ' + insertedBad.length + ' failing)', insertedBad.length === 0);
console.log('  [info] hyphen-insertion sweep: ' + insertedOk + ' cards, all still wrong');
insertedBad.slice(0, 10).forEach(function (s) { LOG.push('    hyphen insertion not wrong: ' + s); });

// The rule is generic: pp-answer.js knows about hyphen CHARACTERS and nothing
// about the answers that carry one. Derived from the data, so a "fix" that
// special-cases a shipped phrase fails here even if nobody updates this list.
var ANSWER_SRC = readFile(ROOT + 'pp-answer.js');
HYPHEN_ROWS.forEach(function (r) {
  ok('T8 pp-answer.js does not hardcode ' + JSON.stringify(r.answer),
     ANSWER_SRC.indexOf(r.answer) === -1);
  A.hyphenVariants(r.answer).forEach(function (v) {
    ok('T8 pp-answer.js does not hardcode the spelling ' + JSON.stringify(v),
       ANSWER_SRC.indexOf(v) === -1);
  });
});

// ---------- report ----------
console.log('Answer collision tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
LOG.forEach(function (l) { console.log('  ' + l); });
if (FAIL > 0) { throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed'); }
