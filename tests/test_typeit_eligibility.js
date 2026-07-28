// Deterministic tests for TYPE IT CARD SUITABILITY - the `practice.typeIt`
// opt-out. Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_typeit_eligibility.js
// Exit status is 0 only if every assertion passes (printed at the end).
//
// WHAT THIS FILE IS FOR
// Priority 3 Phase 2D: Type It asks the learner to recall words and short
// practical phrases. A few authored cards are much longer than that - a
// 51-character proverb, a spelled-out year - and typing one from memory stops
// measuring recall and starts measuring typing accuracy, where a single slipped
// letter reads as failure. Those cards are excluded from Type It ALONE, by an
// explicit per-card decision in the data:
//
//     practice: { typeIt: false }
//
// They keep every word of their learning content and go on teaching through
// flashcards, search, Listening and the Mixed Quiz.
//
// HOW IT TESTS
// The long-answer set is DISCOVERED from the shipping corpus on every run, never
// remembered: the suite recomputes which Type It candidates have a canonical `pl`
// of 30+ visible characters and requires the data to already carry the opt-out
// for exactly those. So a new long card added later fails this suite until
// somebody makes a deliberate decision about it. The count is REPORTED, never
// asserted - it is 11 today, and it is allowed to change.
//
// The 30-character boundary lives HERE, in review, not in the app. pp-usage.js
// never measures `pl`; it only reads the authored flag. That asymmetry is
// deliberate and is itself asserted (section E), because a runtime length rule
// would silently drop future cards with nothing to review in a diff.
//
// SCOPE - what deliberately is NOT here
// The general eligibleFor contract (registers, regions, recognition-only chips)
// belongs to tests/test_activities.js and is not restated. How a typed answer is
// JUDGED belongs to test_answer_validation.js / test_answer_collisions.js; how a
// round SCORES belongs to test_round_scoring.js; hints, feedback and prompt cues
// belong to their own three suites. This file owns the long-answer corpus
// review, the opt-out flag, its effect on the real Type It pools, and the
// guarantee that it changed nothing else - in particular that the excluded cards
// stay in the typed-answer ownership index through the Mixed Quiz.
// Release identifiers - APP_VERSION, CACHE, AUDIO_CACHE - are not pinned: they
// change on purpose at release time.
ObjC.import('Foundation');

function readFile(path) {
  var s = $.NSString.stringWithContentsOfFileEncodingError(path, $.NSUTF8StringEncoding, null);
  return ObjC.unwrap(s);
}
function fileExists(path) {
  return $.NSFileManager.defaultManager.fileExistsAtPath(path);
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
var USAGE_SRC = readFile(ROOT + 'pp-usage.js');

// index.html loads these in exactly this order.
var window = {};
['data-a1.js', 'data-a2.js', 'data-b1.js', 'data-grammar.js', 'data-verbs.js',
 'data-scenarios.js', 'data-podcasts.js', 'pp-usage.js', 'pp-answer.js']
  .forEach(function (f) { (0, eval)(readFile(ROOT + f)); });
var LEVELS = window.PP_LEVELS;
var U = window.PP_USAGE;
var A = window.PP_ANSWER;

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

// ---------- the review measure ----------
// "Visible characters" = the answer as the learner must type it: repeated
// whitespace collapsed, ends trimmed. Nothing else is folded away - a comma the
// learner has to type is a character they have to get right.
function norm(s) { return String(s == null ? '' : s).replace(/\s+/g, ' ').trim(); }
function vlen(s) { return norm(s).length; }
function wordCount(s) { var t = norm(s); return t ? t.split(' ').length : 0; }
var LONG_ENOUGH = 30;      // the REVIEW boundary - deliberately not in app code

// =========================================================================
// 0. THE REAL CORPUS AND THE REAL POOLS
// poolFor() in index.html is reproduced exactly, so "Type It pool" here means
// what it means in production. A "candidate" is a card that clears every OTHER
// Type It gate - it is what the pool would be if the opt-out did not exist,
// which is the only honest baseline for "how many did this remove".
// =========================================================================
var ALL = [];
LEVELS.forEach(function (lv) {
  (lv.topics || []).forEach(function (t) {
    (t.cards || []).forEach(function (c) {
      ALL.push({ c: c, level: lv.level, topic: t.name, kind: t.kind || '', mature: !!t.mature });
    });
  });
});
var byId = {}; ALL.forEach(function (x) { byId[x.c.id] = x.c; });

var VOCAB_SRC = LEVELS.filter(function (lv) {
  return lv.topics.length && lv.topics.every(function (t) { return !t.kind; });
});
// The real poolFor, for any activity and any level selection (null = all levels).
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
// Every Type It gate EXCEPT the opt-out, so the two sets differ by exactly the
// cards this phase removed.
function isCandidate(c) {
  if (!c || c.intro || !c.pl || !c.en) return false;
  if (c.cardType === 'template') return false;
  return !U.isRecognitionOnly(c);
}
var CANDIDATES = [];
VOCAB_SRC.forEach(function (lv) {
  lv.topics.forEach(function (t) {
    if (t.mature) return;
    t.cards.forEach(function (c) { if (isCandidate(c)) CANDIDATES.push({ c: c, level: lv.level, topic: t.name }); });
  });
});
var POOL = poolFor(null, 'typeit');
info('corpus cards: ' + ALL.length + '; Type It candidates: ' + CANDIDATES.length + '; Type It pool now: ' + POOL.length);

function optedOut(c) { return U.typeItOptOut(c); }

// =========================================================================
// A. DISCOVERY - the long-answer corpus review
// The affected set is recomputed here every run. Nothing below hardcodes which
// cards they are; the ids are printed for review, not asserted.
// =========================================================================
var LONG = CANDIDATES.filter(function (x) { return vlen(x.c.pl) >= LONG_ENOUGH; })
  .sort(function (a, b) { return vlen(b.c.pl) - vlen(a.c.pl); });
var SHORT = CANDIDATES.filter(function (x) { return vlen(x.c.pl) < LONG_ENOUGH; });

info('Type It candidates with canonical pl >= ' + LONG_ENOUGH + ' chars: ' + LONG.length);
LONG.forEach(function (x) {
  info('  len=' + vlen(x.c.pl) + ' words=' + wordCount(x.c.pl) + ' ' + x.c.id +
       ' [' + x.level + ' / ' + x.topic + '] pl="' + x.c.pl + '" en="' + x.c.en + '"' +
       ' accepted=' + JSON.stringify(A.accepted(x.c)));
});

// A1. Every long candidate carries the decision. This is the assertion that
// makes a NEW long card fail the suite until somebody rules on it.
var longMissing = LONG.filter(function (x) { return !optedOut(x.c); })
  .map(function (x) { return x.c.id + ' (' + vlen(x.c.pl) + ')'; });
eq('A1 every Type It candidate >= ' + LONG_ENOUGH + ' chars carries practice.typeIt:false', longMissing, []);

// A2. ...and nothing shorter does. A justified short exclusion is allowed to
// exist one day, but it must be argued for in review - so it fails here first,
// naming itself.
var shortOptOuts = SHORT.filter(function (x) { return optedOut(x.c); })
  .map(function (x) { return x.c.id + ' (' + vlen(x.c.pl) + ') "' + x.c.pl + '"'; });
eq('A2 no candidate shorter than ' + LONG_ENOUGH + ' chars is excluded from Type It', shortOptOuts, []);

// A3. The count is REPORTED, never asserted. It is 11 today, and every future
// number is legitimate - a twelfth long card authored and correctly opted out,
// or ZERO, if content editing eventually shortens or retires all of them. This
// suite must stay valid in all of those worlds, so nothing here requires the
// long set to be non-empty.
info('affected ids: ' + (LONG.length ? LONG.map(function (x) { return x.c.id; }).join(', ')
                                     : '(none - no candidate reaches the review boundary)'));

// A4. The decision is authored correctly on every long candidate: a real
// `practice` OBJECT whose `typeIt` is the exact boolean false.
//
// Deliberately NOT a whole-corpus shape rule. `practice` is the per-card ACTIVITY
// object, and a later phase may well add its own key beside this one -
// practice:{typeIt:false, someFutureActivity:false}. Demanding that every
// practice object in the corpus be exactly {typeIt:false} would make this suite
// block that work for no reason. Only `practice.typeIt` is this helper's
// business, so only `practice.typeIt` is asserted.
var badFlag = [];
LONG.forEach(function (x) {
  var p = x.c.practice;
  if (!p || typeof p !== 'object' || Array.isArray(p)) {
    badFlag.push(x.c.id + ' -> no practice object: ' + JSON.stringify(p));
    return;
  }
  if (p.typeIt !== false) {
    badFlag.push(x.c.id + ' -> practice.typeIt is ' + JSON.stringify(p.typeIt) + ', not boolean false');
  }
});
eq('A4 every long candidate carries a practice object whose typeIt is exactly false', badFlag, []);

// A4b. The reviewable register: every card the helper currently excludes from
// Type It, reported dynamically so the decision set is always visible in output
// rather than frozen in an assertion.
var OPTED = ALL.filter(function (x) { return optedOut(x.c); });
info('cards currently opted out of Type It: ' + OPTED.length);
OPTED.forEach(function (x) {
  info('  ' + x.c.id + ' [' + x.level + ' / ' + x.topic + '] len=' + vlen(x.c.pl) +
       ' practice=' + JSON.stringify(x.c.practice));
});

// A5. The excluded cards kept their learning content. `practice` is metadata: it
// must not have disturbed the answer set, so the accepted answers are still the
// canonical `pl` first plus any authored alternatives - byte for byte.
var contentDrift = [];
LONG.forEach(function (x) {
  var c = x.c;
  var expected = [c.pl].concat((c.acceptedAnswers || []).filter(function (a) { return a && a !== c.pl; }));
  if (JSON.stringify(A.accepted(c)) !== JSON.stringify(expected)) contentDrift.push(c.id);
  if (typeof c.pl !== 'string' || !norm(c.pl)) contentDrift.push(c.id + ' (empty pl)');
  if (typeof c.en !== 'string' || !norm(c.en)) contentDrift.push(c.id + ' (empty en)');
});
eq('A5 excluded cards keep pl, en and their full accepted-answer set', contentDrift, []);

// A6. A real cross-check against files this phase did not touch: the generated
// vocabulary pages were built from the pre-change wording, so finding each
// card's CURRENT pl and en verbatim in them proves the wording was not edited.
(function () {
  var fm = $.NSFileManager.defaultManager;
  function htmlUnder(dir) {
    if (!fileExists(ROOT + dir)) return [];
    var arr = fm.subpathsOfDirectoryAtPathError(ROOT + dir, $()), out = [];
    var n = arr && !arr.isNil() ? ObjC.unwrap(arr.count) : 0;
    for (var i = 0; i < n; i++) {
      var s = ObjC.unwrap(arr.objectAtIndex(i));
      if (typeof s === 'string' && /\.html$/.test(s)) out.push(dir + '/' + s);
    }
    return out;
  }
  var pages = htmlUnder('vocabulary').concat(htmlUnder('grammar')).concat(htmlUnder('guide'));
  var bodies = pages.map(function (f) { return readFile(ROOT + f); });
  // build_pages.py writes plain-text fields through Python's html.escape with
  // quote=True, so "don't" reaches the page as "don&#x27;t". The same escaping
  // is applied here rather than stripping markup out of the page.
  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#x27;');
  }
  function onAPage(b, text) { return countOf(b, text) > 0 || countOf(b, esc(text)) > 0; }
  var checked = 0, mismatched = [];
  LONG.forEach(function (x) {
    var c = x.c;
    var onPage = bodies.filter(function (b) { return onAPage(b, c.pl); });
    if (!onPage.length) return;                 // not every card has a generated page
    checked++;
    if (!onPage.some(function (b) { return onAPage(b, c.en); })) mismatched.push(c.id);
  });
  eq('A6 pl and en of every page-backed excluded card still match the generated page', mismatched, []);
  // COVERAGE IS REPORTED, NOT ASSERTED. Whether any excluded card happens to sit
  // in a topic that has a generated page is a fact about content, not a contract:
  // today 7 of 11 do, but a future long card could live entirely in a topic with
  // no page, and that must not fail a permanent suite. The assertion above is the
  // real check; this line only says how much of the corpus it reached.
  info('excluded cards cross-checked against untouched generated pages: ' + checked +
       ' of ' + LONG.length + (LONG.length && !checked ? '  (none page-backed - cross-check inactive)' : ''));
})();

// A7. Length extremes, for the record.
var bySize = CANDIDATES.slice().sort(function (a, b) { return vlen(b.c.pl) - vlen(a.c.pl); });
if (bySize.length) {
  info('longest Type It candidate: ' + vlen(bySize[0].c.pl) + ' chars, ' + bySize[0].c.id + ' "' + bySize[0].c.pl + '"');
  var longestKept = bySize.filter(function (x) { return !optedOut(x.c); })[0];
  if (longestKept) {
    info('longest answer STILL in Type It: ' + vlen(longestKept.c.pl) + ' chars, ' + longestKept.c.id +
         ' [' + longestKept.topic + '] "' + longestKept.c.pl + '"');
    ok('A7 the longest answer still in Type It is under the review boundary',
       vlen(longestKept.c.pl) < LONG_ENOUGH);
  }
}
// An acceptedAnswers ALTERNATIVE being long is explicitly not a reason to
// exclude: the learner is prompted for, and can always type, the canonical `pl`.
var longAlts = [];
CANDIDATES.forEach(function (x) {
  (x.c.acceptedAnswers || []).forEach(function (a) {
    if (vlen(a) >= LONG_ENOUGH) longAlts.push(x.c.id + ' alt(' + vlen(a) + ')="' + a + '"');
  });
});
info('Type It candidates whose canonical pl is short but an accepted alternative is >= ' +
     LONG_ENOUGH + ': ' + longAlts.length + (longAlts.length ? ' -> ' + longAlts.join('; ') : ''));

// =========================================================================
// B. THE ELIGIBILITY HELPER
// Strictness is the whole point: a data typo must never silently empty a pool,
// so ONLY the boolean false means anything.
// =========================================================================
function card(extra) {
  var c = { id: 'b-' + (card.n = (card.n || 0) + 1), pl: 'kawa', en: 'coffee' };
  if (extra) Object.keys(extra).forEach(function (k) { c[k] = extra[k]; });
  return c;
}
var ACTS = ['flashcard', 'search', 'listen', 'typeit', 'mixed'];
function eligibility(c) {
  return ACTS.filter(function (a) { return U.eligibleFor(c, a); });
}

// B1. The one value that means something.
var off = card({ practice: { typeIt: false } });
eq('B1 practice{typeIt:false} is excluded from Type It only', eligibility(off),
   ['flashcard', 'search', 'listen', 'mixed']);
ok('B1 typeItOptOut recognises it', U.typeItOptOut(off) === true);
ok('B1 flashcard keeps it', U.eligibleFor(off, 'flashcard') === true);
ok('B1 search keeps it', U.eligibleFor(off, 'search') === true);
ok('B1 Listening keeps it', U.eligibleFor(off, 'listen') === true);
ok('B1 Mixed Quiz keeps it', U.eligibleFor(off, 'mixed') === true);
ok('B1 Type It drops it', U.eligibleFor(off, 'typeit') === false);

// B1b. FORWARD COMPATIBILITY. `practice` is the activity object, not a
// single-purpose flag: a later phase may add its own key beside typeIt. This
// helper reads ONE key, so a companion key must change nothing either way.
var offPlus = card({ practice: { typeIt: false, futureActivity: false } });
eq('B1b {typeIt:false, futureActivity:false} still opts out of Type It only',
   eligibility(offPlus), ['flashcard', 'search', 'listen', 'mixed']);
ok('B1b typeItOptOut still true alongside another key', U.typeItOptOut(offPlus) === true);
var onPlus = card({ practice: { typeIt: true, futureActivity: false } });
eq('B1b {typeIt:true, futureActivity:false} is an ordinary card',
   eligibility(onPlus), ['flashcard', 'search', 'listen', 'typeit', 'mixed']);
ok('B1b typeItOptOut false alongside another key', U.typeItOptOut(onPlus) === false);
// An UNRELATED key on its own never excludes anything: no typeIt, no decision.
var otherOnly = card({ practice: { futureActivity: false, listen: false, mixed: false } });
eq('B1b a practice object with no typeIt key changes nothing',
   eligibility(otherOnly), ['flashcard', 'search', 'listen', 'typeit', 'mixed']);
ok('B1b typeItOptOut false when typeIt is absent', U.typeItOptOut(otherOnly) === false);

// B2. Everything else leaves the card exactly as it was. `practice:null` is the
// interesting one - typeof null is "object", so a naive check would throw.
var SAME_AS_PLAIN = ['flashcard', 'search', 'listen', 'typeit', 'mixed'];
[['absent', undefined],
 ['null', null],
 ['the STRING "false"', 'false'],
 ['an array', []],
 ['an empty object', {}],
 ['{typeIt:true}', { typeIt: true }],
 ['{typeIt:0}', { typeIt: 0 }],
 ['{typeIt:"false"}', { typeIt: 'false' }],
 ['{typeIt:null}', { typeIt: null }],
 ['{typeIt:undefined}', { typeIt: undefined }],
 ['a nested object', { typeIt: { value: false } }],
 ['an unrelated key', { mixed: false }]
].forEach(function (p) {
  var c = card();
  if (p[1] !== undefined || p[0] === 'absent') { if (p[0] !== 'absent') c.practice = p[1]; }
  else c.practice = p[1];
  eq('B2 practice = ' + p[0] + ' changes nothing', eligibility(c), SAME_AS_PLAIN);
  ok('B2 typeItOptOut(' + p[0] + ') is false', U.typeItOptOut(c) === false);
});
ok('B2 typeItOptOut(null card) is false, not a throw', U.typeItOptOut(null) === false);
ok('B2 typeItOptOut(undefined card) is false', U.typeItOptOut(undefined) === false);

// B3. The pre-existing rules still decide everything they decided before, and
// the opt-out never RESCUES a card another rule already excluded.
var tpl = card({ cardType: 'template', pl: 'Gdzie jest...?', en: 'Where is...?' });
eq('B3 template unchanged', eligibility(tpl), ['flashcard', 'search']);
var tplOff = card({ cardType: 'template', pl: 'Gdzie jest...?', en: 'Where is...?', practice: { typeIt: false } });
eq('B3 template + opt-out still just flashcard/search', eligibility(tplOff), ['flashcard', 'search']);
var intro = card({ intro: true, pl: 'Stan umysłu', en: 'State of Mind' });
eq('B3 intro unchanged', eligibility(intro), ['flashcard', 'search']);
var introOff = card({ intro: true, pl: 'Stan umysłu', en: 'State of Mind', practice: { typeIt: false } });
eq('B3 intro + opt-out still just flashcard/search', eligibility(introOff), ['flashcard', 'search']);
var recog = card({ production: 'recognition-only' });
eq('B3 recognition-only unchanged', eligibility(recog), ['flashcard', 'search', 'listen']);
var recogOff = card({ production: 'recognition-only', practice: { typeIt: false } });
eq('B3 recognition-only + opt-out unchanged', eligibility(recogOff), ['flashcard', 'search', 'listen']);
var plain = card();
eq('B3 an ordinary card is eligible for everything', eligibility(plain), SAME_AS_PLAIN);
var noEn = card({ en: '' });
eq('B3 a card with no en is unchanged', eligibility(noEn), ['flashcard', 'search']);
// A card with an explicit opt-out that is TRUE is an ordinary card.
eq('B3 practice{typeIt:true} is an ordinary card', eligibility(card({ practice: { typeIt: true } })), SAME_AS_PLAIN);

// B4. Unknown activities still fail CLOSED, opt-out or not.
['', 'TYPEIT', 'typeIt', 'type-it', 'quiz', 'listening', undefined, null, 0]
  .forEach(function (a) {
    ok('B4 unknown activity ' + JSON.stringify(a) + ' is false (plain card)', U.eligibleFor(plain, a) === false);
    ok('B4 unknown activity ' + JSON.stringify(a) + ' is false (opted-out card)', U.eligibleFor(off, a) === false);
  });
ok('B4 no card at all is still false', U.eligibleFor(null, 'typeit') === false);

// =========================================================================
// C. THE REAL POOLS
// =========================================================================
// C1. Not one excluded card survives in any Type It pool the app can build.
var leakedAll = POOL.filter(function (x) { return optedOut(x.c); }).map(function (x) { return x.c.id; });
eq('C1 no opted-out card is in the "All levels" Type It pool', leakedAll, []);

// C2. The pool shrank by EXACTLY the number of excluded candidates - no card was
// lost to some other accident, and none was excluded twice.
var excludedCount = CANDIDATES.filter(function (x) { return optedOut(x.c); }).length;
eq('C2 Type It pool = candidates - exclusions', POOL.length, CANDIDATES.length - excludedCount);
eq('C2 every exclusion is a long card', excludedCount, LONG.length);
info('Type It pool: ' + CANDIDATES.length + ' before -> ' + POOL.length + ' after (' + excludedCount + ' excluded)');

// C3. Per-level Type It topics: the menu builds one topic per vocabulary level
// plus "All levels". Every one is reported and must still be able to run.
var ROUND = 15;    // Type It slices 15; a shorter round is allowed, an empty one is not
var perLevel = [];
VOCAB_SRC.forEach(function (lv) {
  var before = 0, after = 0;
  lv.topics.forEach(function (t) {
    if (t.mature) return;
    t.cards.forEach(function (c) {
      if (isCandidate(c)) { before++; if (!optedOut(c)) after++; }
    });
  });
  perLevel.push({ level: lv.level, before: before, after: after });
  var realPool = poolFor([lv.level], 'typeit');
  eq('C3 ' + lv.level + ' pool matches the expected count', realPool.length, after);
  eq('C3 ' + lv.level + ' pool contains no opted-out card',
     realPool.filter(function (x) { return optedOut(x.c); }).map(function (x) { return x.c.id; }), []);
  ok('C3 ' + lv.level + ' Type It topic is not empty', realPool.length > 0);
  info('  Type It topic "' + lv.level + '": ' + before + ' -> ' + after +
       ' (-' + (before - after) + ')' + (after < ROUND ? '  *** BELOW A FULL ' + ROUND + '-CARD ROUND ***' : ''));
  if (after < ROUND) info('    note: Type It slices 15 and tolerates a shorter round; no filler is added');
});
var allTopic = poolFor(null, 'typeit');
ok('C4 the "All levels" Type It topic is not empty', allTopic.length > 0);
// NOT asserted: that every level can fill a full 15. Type It slices 15 and is
// designed to run a shorter round, so a legitimately small level is correct
// behaviour, not a regression. Falling below 15 is REPORTED above (and again
// here) for review; only an EMPTY topic is a failure.
var thin = perLevel.filter(function (p) { return p.after < ROUND; });
info('Type It topics below a full ' + ROUND + '-card round: ' + thin.length +
     (thin.length ? ' -> ' + thin.map(function (p) { return p.level + ' (' + p.after + ')'; }).join(', ')
                  : ' (none)'));

// C5. Ordinary cards are untouched - the exclusion is narrow, not a pool-wide
// change of behaviour.
var stillThere = ['a1-first-phrases-021', 'a1-cafe-016', 'a1-numbers-prices-005']
  .filter(function (id) { return byId[id]; });
stillThere.forEach(function (id) {
  ok('C5 ordinary card ' + id + ' is still in the Type It pool',
     POOL.some(function (x) { return x.c.id === id; }));
});
ok('C5 the pool is still overwhelmingly intact', POOL.length > CANDIDATES.length * 0.95);

// C6. Listening is drawn from the same levels and must NOT have shrunk.
var listenPool = poolFor(null, 'listen');
var listenLeak = LONG.filter(function (x) {
  return !listenPool.some(function (y) { return y.c.id === x.c.id; });
}).map(function (x) { return x.c.id; });
eq('C6 every excluded card is still in the Listening pool', listenLeak, []);
info('Listening pool: ' + listenPool.length + ' (unchanged by this phase)');

// C7. Flashcards and search reach every excluded card through their own topics.
var reachLeak = [];
LONG.forEach(function (x) {
  if (!U.eligibleFor(x.c, 'flashcard')) reachLeak.push(x.c.id + ' flashcard');
  if (!U.eligibleFor(x.c, 'search')) reachLeak.push(x.c.id + ' search');
  if (!U.eligibleFor(x.c, 'mixed')) reachLeak.push(x.c.id + ' mixed');
});
eq('C7 every excluded card stays in flashcards, search and Mixed Quiz', reachLeak, []);

// =========================================================================
// D. THE TYPED-ANSWER OWNERSHIP INDEX
// The trap this phase had to avoid: PP_USAGE.typedPracticeCards is the union of
// Type It and Mixed Quiz. A card dropped from Type It alone is STILL askable in
// the Mixed Quiz, so it must stay in the union - otherwise its answer quietly
// stops being protected and an unrelated card's "almost" verdict changes.
// =========================================================================
var TPC = U.typedPracticeCards(LEVELS);
var tpcIds = {}; TPC.forEach(function (c) { tpcIds[c.id] = true; });
info('typedPracticeCards (Type It ∪ Mixed Quiz): ' + TPC.length);

// D1. Every excluded card that the Mixed Quiz can still ask is still indexed.
var droppedFromIndex = LONG.filter(function (x) {
  return U.eligibleFor(x.c, 'mixed') && !tpcIds[x.c.id];
}).map(function (x) { return x.c.id; });
eq('D1 Mixed-eligible excluded cards remain in typedPracticeCards', droppedFromIndex, []);
eq('D1 all ' + LONG.length + ' excluded cards are Mixed-eligible and indexed',
   LONG.filter(function (x) { return tpcIds[x.c.id]; }).length, LONG.length);

// D2. The index itself is still well-formed and still owns those answers.
var IDX = A.buildIndex(TPC);
ok('D2 index has owners', !!IDX && !!IDX.owners);
var unowned = LONG.filter(function (x) {
  var owners = IDX.owners[A.normalize(x.c.pl)];
  return !owners || owners.indexOf(x.c.id) === -1;
}).map(function (x) { return x.c.id; });
eq('D2 every excluded card still owns its own answer in the index', unowned, []);

// D3. The pięć/piec protection is the canary: it depends on the index, so it is
// re-checked verbatim here.
(function () {
  var five = byId['a1-numbers-prices-005'];
  if (!five) { info('a1-numbers-prices-005 not present; pięć/piec check skipped'); return; }
  eq('D3 "piec" typed for pięć is still wrong, not almost', A.classify('piec', five, IDX), 'wrong');
  eq('D3 pięć typed exactly is still right', A.classify(five.pl, five, IDX), 'right');
})();

// D4. Exact and accepted answers still classify as before, for the excluded
// cards themselves - they are still asked in the Mixed Quiz.
var misclassified = [];
LONG.forEach(function (x) {
  var c = x.c;
  A.accepted(c).forEach(function (a) {
    if (A.classify(a, c, IDX) !== 'right') misclassified.push(c.id + ' <- "' + a + '"');
  });
  if (A.classify('zupełnie inna odpowiedź', c, IDX) !== 'wrong') misclassified.push(c.id + ' accepted nonsense');
});
eq('D4 every accepted answer of an excluded card still classifies as right', misclassified, []);

// D5. A spot-check across the whole index: the union did not change size in a
// way that would mean Type It cards fell out of it. Every Type It pool card must
// still be indexed too.
var poolNotIndexed = POOL.filter(function (x) { return x.c.id && !tpcIds[x.c.id]; }).map(function (x) { return x.c.id; });
eq('D5 every card still in the Type It pool is in the typed index', poolNotIndexed, []);

// =========================================================================
// E. SCOPE - what this phase must NOT have done
// =========================================================================
// E1. NO runtime length rule. This is the load-bearing one: the 30-character
// boundary is a review tool, and pp-usage.js must decide only from the authored
// flag. If somebody later "helpfully" adds a length threshold, this fails.
(function () {
  var start = USAGE_SRC.indexOf('PP_USAGE.typeItOptOut = function');
  ok('E1 typeItOptOut exists in pp-usage.js', start !== -1);
  if (start === -1) return;
  var body = USAGE_SRC.slice(start, USAGE_SRC.indexOf('};', start));
  ok('E1 the opt-out never measures the answer', body.indexOf('.length') === -1);
  ok('E1 the opt-out never reads pl', body.indexOf('pl') === -1 || body.indexOf('card.pl') === -1);
  ok('E1 the opt-out contains no numeric threshold', !/\b\d{2,}\b/.test(body));
})();
// ...and eligibleFor does not measure anything either.
(function () {
  var start = USAGE_SRC.indexOf('PP_USAGE.eligibleFor = function');
  var body = USAGE_SRC.slice(start, USAGE_SRC.indexOf('};', start));
  ok('E1 eligibleFor never measures pl length', body.indexOf('.length') === -1);
  ok('E1 eligibleFor still gates typeit on the opt-out', body.indexOf('typeItOptOut') !== -1);
  ok('E1 eligibleFor still returns true for flashcard/search first', body.indexOf('"flashcard"') !== -1);
})();

// E2. The exclusion reaches Type It ONLY. Reading the shipping call sites: Type
// It asks poolFor(..., "typeit"), Listening asks "listen"; the Mixed Quiz never
// consults typeit at all.
ok('E2 Type It still builds its pool with the typeit activity', countOf(INDEX, 'poolFor(T.topicRef.src, "typeit")') === 1);
ok('E2 Listening still builds its pool with the listen activity', countOf(INDEX, 'poolFor(L.topicRef.src, "listen")') === 1);
// The decision lives in pp-usage.js alone. index.html must not read the field
// itself, or there would be two rules to keep in step. ("practice" as a word
// appears in the app for unrelated things - practiceTopics, practiceSet - so
// this looks for the property access, not the word.)
ok('E2 index.html never reads card.practice itself', countOf(INDEX, '.practice') === 0);
ok('E2 index.html has no opt-out logic of its own',
   countOf(INDEX, 'typeItOptOut') === 0 && countOf(INDEX, 'typeIt:') === 0);

// E3. No generated page learned about this metadata - it is a runtime activity
// decision, never content.
(function () {
  var fm = $.NSFileManager.defaultManager;
  function htmlUnder(dir) {
    if (!fileExists(ROOT + dir)) return [];
    var arr = fm.subpathsOfDirectoryAtPathError(ROOT + dir, $()), out = [];
    var n = arr && !arr.isNil() ? ObjC.unwrap(arr.count) : 0;
    for (var i = 0; i < n; i++) {
      var s = ObjC.unwrap(arr.objectAtIndex(i));
      if (typeof s === 'string' && /\.html$/.test(s)) out.push(dir + '/' + s);
    }
    return out;
  }
  var pages = htmlUnder('vocabulary').concat(htmlUnder('grammar')).concat(htmlUnder('guide'));
  info('generated pages scanned: ' + pages.length);
  var leaked = pages.filter(function (f) {
    var b = readFile(ROOT + f);
    return countOf(b, 'typeIt:false') > 0 || countOf(b, 'typeItOptOut') > 0;
  });
  eq('E3 no generated page mentions the opt-out', leaked.slice(0, 5), []);
})();

// E4. Nothing about scoring, hints, feedback or prompt cues moved. Those four
// suites own the detail; this only asserts the shipping code still has them, so
// a future edit here cannot quietly delete one.
ok('E4 the three score tiles are still counted', countOf(INDEX, 'T.right') > 0 && countOf(INDEX, 'T.almost') > 0);
ok('E4 hint reporting still exists', countOf(INDEX, 'tRevealLetter') > 0);
ok('E4 the prompt cue is still read', countOf(INDEX, 'typeItCue') > 0);
ok('E4 no card lost its typeItCue', ALL.filter(function (x) { return x.c.typeItCue; }).length > 0);
// The cued cards are short prompts and must NOT have been caught by this phase.
var cuedExcluded = ALL.filter(function (x) { return x.c.typeItCue && optedOut(x.c); })
  .map(function (x) { return x.c.id; });
eq('E4 no card carrying a Type It prompt cue was excluded', cuedExcluded, []);
// Same for aspect pairs: their feedback only fires inside Type It.
var pairExcluded = ALL.filter(function (x) { return x.c.relationType === 'aspect-pair' && optedOut(x.c); })
  .map(function (x) { return x.c.id; });
eq('E4 no aspect-pair card was excluded from Type It', pairExcluded, []);

// E5. The corpus did not change shape.
eq('E5 no card has a duplicate id', ALL.length, Object.keys(byId).length);
ok('E5 every excluded card still has a stable id', LONG.every(function (x) { return /^[a-z0-9-]+$/.test(x.c.id); }));

// =========================================================================
// REPORT
// =========================================================================
INFO.forEach(function (s) { console.log(s); });
console.log('Type It eligibility tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
LOG.forEach(function (s) { console.log('  ' + s); });
if (FAIL > 0) { throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed'); }
