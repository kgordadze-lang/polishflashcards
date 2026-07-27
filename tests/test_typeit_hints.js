// Deterministic tests for TYPE IT HINT REPORTING.
// Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_typeit_hints.js
// Exit status is 0 only if every assertion passes (printed at the end).
//
// WHAT THIS FILE IS FOR
// Priority 3 Phase 2A: the end-of-round summary must say out loud how many
// QUESTIONS leaned on "Reveal a letter". The unit is the question, not the
// click - five reveals on one word is one hinted question - and a hint is
// reported whether the answer ended up right, almost or wrong. The three score
// tiles keep their exact meaning: nothing is deducted for asking for help.
//
// HOW IT TESTS
// It does not re-implement the round. It lifts the real startTypeit, tRender,
// tRevealLetter, tCheckAnswer and tShowDone - plus the real Enter handler - out
// of index.html and drives them against a stub DOM and the real PP_ANSWER, so a
// future edit to the shipping code is what these assertions see. Clicks go
// through a stub that honours `disabled` exactly as a browser does, and the
// same submissions are also fired raw, so the once-per-question guarantee is
// shown to rest on the `T.state` guard rather than on a disabled attribute.
//
// SCOPE - what deliberately is NOT here
// How a verdict is DECIDED belongs to tests/test_answer_validation.js and
// tests/test_answer_collisions.js; how right/almost/missed are COUNTED belongs
// to tests/test_round_scoring.js. This file owns only the hint count and the
// sentence it produces, plus the guarantee that it changed neither of those.
// Release identifiers - APP_VERSION, CACHE, AUDIO_CACHE - are not pinned here:
// they change on purpose at release time, and a permanent regression suite must
// not fail for that.
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
(0, eval)(readFile(ROOT + 'pp-answer.js'));   /* the real comparator, not a copy of its rules */

// ---------- tiny test framework (same shape as the other suites) ----------
var PASS = 0, FAIL = 0, LOG = [];
function ok(name, cond) { if (cond) { PASS++; } else { FAIL++; LOG.push('FAIL: ' + name); } }
function eq(name, a, b) {
  var sa = JSON.stringify(a), sb = JSON.stringify(b);
  ok(name + (sa === sb ? '' : '  (got ' + sa + ', want ' + sb + ')'), sa === sb);
}

// ---------- lifting real code out of index.html ----------
// Same brace-matching extractor the other suites use.
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
// The keyboard path is an inline arrow, so it is lifted by its opening text and
// re-wrapped as a named function - the body executed is still the shipping one.
function arrowBodyAfter(src, marker) {
  var at = src.indexOf(marker);
  if (at === -1) throw new Error('extract: marker not found in index.html: ' + marker);
  var open = at + marker.length - 1, depth = 0;
  for (var j = open; j < src.length; j++) {
    if (src[j] === '{') depth++;
    else if (src[j] === '}') { depth--; if (depth === 0) return src.slice(open + 1, j); }
  }
  throw new Error('extract: unbalanced braces after ' + marker);
}
var SRC_START  = bodyOf(INDEX, 'startTypeit');
var SRC_RENDER = bodyOf(INDEX, 'tRender');
var SRC_REVEAL = bodyOf(INDEX, 'tRevealLetter');
var SRC_CHECK  = bodyOf(INDEX, 'tCheckAnswer');
var SRC_DONE   = bodyOf(INDEX, 'tShowDone');
var SRC_KEY    = arrowBodyAfter(INDEX, '$("tInput").addEventListener("keydown", e=>{');

// The five functions call each other, so they are compiled into ONE scope with
// their free identifiers supplied as parameters.
var FREE = ['$', 'T', 'LEVELS', 'poolFor', 'gShuffle', 'show', 'PP_ANSWER', 'PP_TYPED_INDEX',
            'ppHasMainAudio', 'ppMainAudioText', 'ppVariantParts', 'ppAppendUsageTo',
            'G_AUDIO', 'window'];
var COMPILE = Function.apply(null, FREE.concat([
  SRC_START + '\n' + SRC_RENDER + '\n' + SRC_REVEAL + '\n' + SRC_CHECK + '\n' + SRC_DONE + '\n' +
  'function tKeydown(e){' + SRC_KEY + '}\n' +
  'return { startTypeit:startTypeit, tRender:tRender, tRevealLetter:tRevealLetter,' +
  '         tCheckAnswer:tCheckAnswer, tShowDone:tShowDone, tKeydown:tKeydown };'
]));

// ---------- stub DOM: just enough for one Type It round ----------
// textContent coerces to string exactly as a real node does, so the assertions
// below compare what a learner would actually read.
function makeNode(id) {
  var o = { id: id, style: {}, value: '', disabled: false, hidden: false,
            className: '', focused: 0, _q: {} }, t = '', h = '';
  Object.defineProperty(o, 'textContent', { get: function () { return t; },
                                            set: function (v) { t = String(v); } });
  Object.defineProperty(o, 'innerHTML', { get: function () { return h; },
                                          set: function (v) { h = String(v); } });
  o.focus = function () { o.focused++; };
  o.querySelector = function (sel) { return (o._q[sel] || (o._q[sel] = makeNode(id + sel))); };
  return o;
}
function makeDom() {
  var nodes = {};
  var get$ = function (id) { return (nodes[id] || (nodes[id] = makeNode(id))); };
  return { $: get$, text: function (id) { return get$(id).textContent; } };
}

// ---------- a controlled corpus ----------
// Short, ordinary answers. The real startTypeit shuffles and then sorts by
// answer length, so the tests never assume WHICH card a question holds: they
// read the live question and build the answer they want from it.
var CARDS = [
  { id: 'q1', pl: 'kota', en: 'a cat (acc.)' },
  { id: 'q2', pl: 'psa',  en: 'a dog (acc.)' },
  { id: 'q3', pl: 'dom',  en: 'a house' },
  { id: 'q4', pl: 'noc',  en: 'a night' },
  { id: 'q5', pl: 'sok',  en: 'a juice' }
];
var INDEX_STUB = PP_ANSWER.buildIndex(CARDS);
// One answer per verdict, derived from whichever card is being asked:
// "almost" is the same word with a diacritic slipped in, "wrong" is not a word.
function answerFor(card, kind) {
  if (kind === 'right')  return card.pl;
  if (kind === 'almost') return card.pl.replace('o', 'ó').replace('a', 'ą');
  return 'zzzz' + card.id;
}

// ---------- one drivable round ----------
// Everything a test does to a round goes through the real functions: reveal is
// tRevealLetter, submit is either the real click wiring or the real Enter
// handler, advancing is the real Next wiring (T.i++ then tRender).
function newRound(size, corpus) {
  var dom = makeDom();
  var cards = (corpus || CARDS).slice(0, size || (corpus || CARDS).length);
  var T = { topicRef: null, li: 0, ti: 0, qs: [], i: 0, right: 0, almost: 0, hinted: 0,
            revealed: 0, state: 'ask' };
  var api = COMPILE(
    dom.$, T,
    [{ topics: [{ id: 'topic-1', name: 'Topic', src: 'topic-1' }] }],                 /* LEVELS */
    function () { return cards.map(function (c) { return { c: c, topic: 'Topic' }; }); }, /* poolFor */
    function (a) { return a; },                                                        /* gShuffle */
    function () {},                                                                    /* show */
    PP_ANSWER, INDEX_STUB,
    function () { return false; },      /* ppHasMainAudio  - display only */
    function () { return ''; },         /* ppMainAudioText - display only */
    function () { return null; },       /* ppVariantParts  - display only */
    function () {},                     /* ppAppendUsageTo - display only */
    '', {}                              /* G_AUDIO, window */
  );

  var r = {
    T: T, dom: dom, api: api,
    start:  function () { api.startTypeit(0, 0); return r; },
    // the card the round is asking right now, whatever the shuffle/sort chose
    card:   function () { return T.qs[T.i].c; },
    cur:    function (kind) { return answerFor(r.card(), kind || 'right'); },
    // "Reveal a letter": a real browser cannot click a disabled button.
    reveal: function (times) {
      for (var i = 0; i < (times || 1); i++) {
        if (dom.$('tHint').disabled) continue;
        api.tRevealLetter();
      }
      return r;
    },
    type:   function (text) { dom.$('tInput').value = text; return r; },
    // The Check button, wired in index.html to tCheckAnswer.
    click:  function () { if (!dom.$('tCheck').disabled) api.tCheckAnswer(); return r; },
    clickRaw: function () { api.tCheckAnswer(); return r; },     /* ignores `disabled` */
    enter:  function () { api.tKeydown({ key: 'Enter', preventDefault: function () {} }); return r; },
    next:   function () { T.i++; api.tRender(); return r; },
    // Answer the current question and move on, the way the UI does.
    answer: function (text) { return r.type(text).click().next(); },
    answerKind: function (kind) { return r.answer(r.cur(kind)); },
    done:   function () {
      return { correct: dom.text('tScoreN'), almost: dom.text('tAlmostN'),
               missed: dom.text('tMissN'), msg: dom.text('tDoneMsg'),
               hinted: T.hinted };
    }
  };
  return r.start();
}
// A whole round in one call: `plan` is one entry per question,
// {kind:"right", reveals:2}. Reaching the end renders the done screen.
function playRound(plan) {
  var r = newRound(plan.length);
  plan.forEach(function (step) {
    if (step.reveals) r.reveal(step.reveals);
    r.answerKind(step.kind);
  });
  return r;
}
function step(kind, reveals) { return { kind: kind, reveals: reveals || 0 }; }
function repeat(n, kind, reveals) {        /* n identical questions */
  var out = []; for (var i = 0; i < n; i++) out.push(step(kind, reveals)); return out;
}

// sanity: every card in the corpus really produces all three verdicts through
// the real PP_ANSWER, so a "wrong" below is a wrong answer and not a bad fixture
CARDS.forEach(function (c) {
  eq('T0 ' + c.pl + ': the right answer classifies right',
     PP_ANSWER.classify(answerFor(c, 'right'), c, INDEX_STUB), 'right');
  eq('T0 ' + c.pl + ': the diacritic slip classifies almost',
     PP_ANSWER.classify(answerFor(c, 'almost'), c, INDEX_STUB), 'almost');
  eq('T0 ' + c.pl + ': the junk answer classifies wrong',
     PP_ANSWER.classify(answerFor(c, 'wrong'), c, INDEX_STUB), 'wrong');
});

// =========================================================================
// A. NO HINTS - the unaided round is exactly what it was
// =========================================================================
var cleanPerfect = playRound(repeat(5, 'right')).done();
eq('A1 unaided all-right counts zero hinted questions', cleanPerfect.hinted, 0);
ok('A1 unaided all-right keeps the perfect-round message',
   cleanPerfect.msg.indexOf('You typed every one exactly right.') !== -1);
ok('A1 unaided all-right adds no hint sentence',
   cleanPerfect.msg.indexOf('hint') === -1 && cleanPerfect.msg.indexOf('Hint') === -1);
eq('A1 unaided all-right correct tile', cleanPerfect.correct, '5');
eq('A1 unaided all-right almost tile', cleanPerfect.almost, '0');
eq('A1 unaided all-right missed tile', cleanPerfect.missed, '0');

var cleanMixed = playRound([step('right'), step('right'), step('right'),
                            step('almost'), step('wrong')]).done();
eq('A2 unaided mixed round scores 3 right', cleanMixed.correct, '3');
eq('A2 unaided mixed round scores 1 almost', cleanMixed.almost, '1');
eq('A2 unaided mixed round scores 1 missed', cleanMixed.missed, '1');
eq('A2 unaided mixed round counts zero hinted questions', cleanMixed.hinted, 0);
ok('A2 unaided mixed round adds no hint sentence', cleanMixed.msg.indexOf('hint') === -1);
ok('A2 unaided mixed round still names the other tiers',
   cleanMixed.msg.indexOf('3 of 5') !== -1 && cleanMixed.msg.indexOf('1 almost') !== -1 &&
   cleanMixed.msg.indexOf('1 to revisit') !== -1);

// a round where the hint button was never touched must read identically to one
// where the counter did not exist at all
var noHintAllWrong = playRound(repeat(3, 'wrong')).done();
eq('A3 an unaided all-wrong round counts zero hinted questions', noHintAllWrong.hinted, 0);
ok('A3 an unaided all-wrong round adds no hint sentence', noHintAllWrong.msg.indexOf('hint') === -1);

// =========================================================================
// B. COUNTING - the unit is the question, not the click
// =========================================================================
var oneReveal = playRound([step('right', 1), step('right'), step('right')]);
eq('B1 one reveal on one question counts once', oneReveal.T.hinted, 1);
var manyReveals = playRound([step('right', 3), step('right'), step('right')]);
eq('B2 three reveals on ONE question still count once', manyReveals.T.hinted, 1);
var maxedReveals = playRound([step('right', 12), step('right')]);
eq('B2 revealing past the end of the word still counts once', maxedReveals.T.hinted, 1);

var spread = playRound([step('right', 1), step('right', 2), step('right'),
                        step('right', 1), step('right', 5)]);
eq('B3 hints on four separate questions count four', spread.T.hinted, 4);
eq('B3 the un-hinted question in that round is not counted',
   spread.T.hinted, 5 - 1);

// a hint counts under every verdict
var hintRight  = playRound([step('right',  2)]);
var hintAlmost = playRound([step('almost', 2)]);
var hintWrong  = playRound([step('wrong',  2)]);
eq('B4 a hint followed by a right answer counts',  hintRight.T.hinted, 1);
eq('B4 a hint followed by an almost answer counts', hintAlmost.T.hinted, 1);
eq('B4 a hint followed by a wrong answer counts',   hintWrong.T.hinted, 1);
eq('B4 the hinted right answer is still right', hintRight.done().correct, '1');
eq('B4 the hinted almost answer is still almost', hintAlmost.done().almost, '1');
eq('B4 the hinted wrong answer is still missed', hintWrong.done().missed, '1');
eq('B4 a hinted right answer is NOT demoted to almost', hintRight.done().almost, '0');
eq('B4 a hinted right answer is NOT demoted to missed', hintRight.done().missed, '0');

// questions answered without touching the button never count
var none = playRound([step('right'), step('almost'), step('wrong')]);
eq('B5 questions with no reveal do not count', none.T.hinted, 0);

// the counter tracks reveals, not the existence of the button: a round where
// the button was rendered on every question but pressed on one counts one
var buttonShown = playRound([step('right'), step('right', 1), step('right')]);
eq('B6 merely rendering the hint button counts nothing', buttonShown.T.hinted, 1);

// The rule is "a letter was revealed", not "the button was pressed". The reveal
// never gives away the whole answer, so pressing it on a one-letter answer
// shows nothing - and nothing shown is not help received. (No answer that short
// is expected in the shipping pool; this pins the rule, not the corpus.)
var oneLetter = newRound(1, [{ id: 'x1', pl: 'w', en: 'in' }]);
oneLetter.reveal(3);
eq('B7 a reveal that shows no letter leaves the per-question state at zero',
   oneLetter.T.revealed, 0);
oneLetter.type('w').click();
eq('B7 a reveal that shows no letter is not counted as a hint', oneLetter.T.hinted, 0);
eq('B7 that question is still scored normally', oneLetter.T.right, 1);

// =========================================================================
// C. SUBMISSION SAFETY - at most one count per answered question
// =========================================================================
// repeated Enter. The real handler submits while the question is open and
// ADVANCES once it is answered, so "Enter again" is tested both ways: through
// the handler (which advances) and straight into tCheckAnswer (which must not
// re-score even when something calls it again on a settled question).
var rEnter = newRound(3);
rEnter.reveal(2).type(rEnter.cur()).enter();
eq('C1 the first Enter banks the hint', rEnter.T.hinted, 1);
eq('C1 the first Enter scores the question', rEnter.T.right, 1);
eq('C1 the first Enter settles the question', rEnter.T.state, 'done');
rEnter.clickRaw(); rEnter.clickRaw();     /* a settled question cannot be re-submitted */
eq('C1 re-submitting a settled question does not count it twice', rEnter.T.hinted, 1);
eq('C1 re-submitting a settled question does not score it twice', rEnter.T.right, 1);
rEnter.enter();                            /* the second Enter is the "Next" press */
eq('C1 the second Enter advances instead of re-scoring', rEnter.T.i, 1);
eq('C1 repeated Enter does not count the question twice', rEnter.T.hinted, 1);
eq('C1 repeated Enter does not score the question twice', rEnter.T.right, 1);
rEnter.enter();                            /* Enter on the fresh, empty question does nothing */
eq('C1 Enter on an empty new question counts nothing', rEnter.T.hinted, 1);
eq('C1 Enter on an empty new question scores nothing', rEnter.T.right, 1);
eq('C1 Enter on an empty new question does not skip it', rEnter.T.i, 1);

// repeated click
var rClick = newRound(2);
rClick.reveal(1).type(rClick.cur()).click().click().click();
eq('C2 repeated click does not count the question twice', rClick.T.hinted, 1);
eq('C2 repeated click does not score the question twice', rClick.T.right, 1);
// and not merely because the button went disabled - the state guard alone holds
var rClickRaw = newRound(2);
rClickRaw.reveal(1).type(rClickRaw.cur()).click().clickRaw().clickRaw();
eq('C2 a click that ignores `disabled` still counts once', rClickRaw.T.hinted, 1);
eq('C2 a click that ignores `disabled` still scores once', rClickRaw.T.right, 1);

// keyboard then click, and click then keyboard
var rMix = newRound(2);
rMix.reveal(1).type(rMix.cur()).enter().clickRaw();
eq('C3 Enter then click counts the question once', rMix.T.hinted, 1);
eq('C3 Enter then click scores the question once', rMix.T.right, 1);
var rMix2 = newRound(2);
rMix2.reveal(1).type(rMix2.cur()).click().enter();
eq('C3 click then Enter counts the question once', rMix2.T.hinted, 1);
eq('C3 click then Enter scores the question once', rMix2.T.right, 1);

// a blank submission after revealing banks nothing yet
var rBlank = newRound(2);
rBlank.reveal(2).type('').click().click();
eq('C4 a blank submission after revealing counts nothing yet', rBlank.T.hinted, 0);
eq('C4 a blank submission scores nothing', rBlank.T.right, 0);
eq('C4 a blank submission leaves the question open', rBlank.T.state, 'ask');
rBlank.type('   ').enter();
eq('C4 a whitespace-only submission counts nothing yet', rBlank.T.hinted, 0);
eq('C4 a whitespace-only submission leaves the question open', rBlank.T.state, 'ask');
// ...and the later real submission counts that question exactly once
rBlank.type(rBlank.cur()).click().enter().clickRaw();
eq('C5 the later real submission counts the question exactly once', rBlank.T.hinted, 1);
eq('C5 the later real submission scores the question exactly once', rBlank.T.right, 1);

// the reveal itself never scores - only the submission does
var rRevealOnly = newRound(2);
rRevealOnly.reveal(3);
eq('C6 revealing alone banks no hinted question yet', rRevealOnly.T.hinted, 0);
eq('C6 revealing alone scores nothing', rRevealOnly.T.right, 0);
ok('C6 tRevealLetter does not touch the round counter', SRC_REVEAL.indexOf('T.hinted') === -1);
// abandoning a hinted question without answering banks nothing
var rAbandon = newRound(3);
rAbandon.reveal(2).next();
eq('C7 leaving a hinted question unanswered counts nothing', rAbandon.T.hinted, 0);

// =========================================================================
// D. LIFECYCLE - per-question state vs round state
// =========================================================================
var rLife = newRound(3);
rLife.reveal(2);
eq('D1 reveals accumulate within the question', rLife.T.revealed, 2);
rLife.type(rLife.cur()).click();
eq('D1 the hint survives to the submission', rLife.T.hinted, 1);
rLife.next();
eq('D2 tRender resets the per-question reveal state', rLife.T.revealed, 0);
eq('D2 tRender does NOT reset the round hinted count', rLife.T.hinted, 1);
eq('D2 tRender reopens the question', rLife.T.state, 'ask');
ok('D2 tRender clears the hint line for the new question', rLife.dom.$('tHintLine').hidden === true);
ok('D2 tRender re-enables the hint button for the new question',
   rLife.dom.$('tHint').disabled === false);
ok('D2 tRender resets nothing but the per-question state',
   SRC_RENDER.indexOf('T.hinted') === -1 && SRC_RENDER.indexOf('T.revealed=0') !== -1);
rLife.type(rLife.cur()).click().next();
eq('D2 a later un-hinted question leaves the count alone', rLife.T.hinted, 1);

// "New round" routes through startTypeit, which must clear the count
var rAgain = playRound([step('right', 2), step('right', 1), step('right')]);
eq('D3 the finished round counted its hints', rAgain.T.hinted, 2);
rAgain.start();                                   /* exactly what the "New round" button does */
eq('D3 a new round starts at zero hinted questions', rAgain.T.hinted, 0);
eq('D3 a new round starts at zero right', rAgain.T.right, 0);
eq('D3 a new round starts at zero almost', rAgain.T.almost, 0);
eq('D3 a new round starts at the first question', rAgain.T.i, 0);
ok('D3 the "New round" button is wired to startTypeit',
   INDEX.indexOf('$("tAgain").addEventListener("click", ()=>startTypeit(T.li, T.ti));') !== -1);
ok('D3 startTypeit clears the hinted count', SRC_START.indexOf('T.hinted=0') !== -1);
// the fresh round's summary carries nothing over from the previous one
[0, 1, 2].forEach(function () { rAgain.answerKind('right'); });
var afterRestart = rAgain.done();
eq('D3 the fresh round reports zero hinted questions', afterRestart.hinted, 0);
ok('D3 the fresh round earns the unaided perfect-round message',
   afterRestart.msg.indexOf('You typed every one exactly right.') !== -1);

// wording: singular vs plural
var one = playRound([step('right', 1), step('right'), step('right')]).done();
ok('D4 one hinted question uses the singular sentence',
   one.msg.indexOf('You used a hint on 1 question.') !== -1);
ok('D4 the singular sentence is not pluralised',
   one.msg.indexOf('1 questions') === -1 && one.msg.indexOf('used hints') === -1);
var two = playRound([step('right', 1), step('right', 1), step('right')]).done();
ok('D4 two hinted questions use the plural sentence',
   two.msg.indexOf('You used hints on 2 questions.') !== -1);
var four = playRound([step('right', 1), step('right', 2),
                      step('right', 1), step('right', 3),
                      step('right')]).done();
ok('D4 four hinted questions read "hints on 4 questions"',
   four.msg.indexOf('You used hints on 4 questions.') !== -1);

// an all-right round that used hints must NOT borrow the unaided message
ok('D5 a hinted all-right round loses the unaided perfect-round message',
   four.msg.indexOf('every one exactly right') === -1);
ok('D5 a hinted all-right round still states the exact-right total',
   four.msg.indexOf('You typed 5 of 5 exactly right.') !== -1);
ok('D5 a hinted all-right round states the hints separately',
   four.msg.indexOf('You used hints on 4 questions.') !== -1);
eq('D5 a hinted all-right round still scores every answer correct', four.correct, '5');
eq('D5 a hinted all-right round has nothing in the almost tile', four.almost, '0');
eq('D5 a hinted all-right round has nothing in the missed tile', four.missed, '0');
ok('D5 the two all-right summaries are worded differently', four.msg !== cleanPerfect.msg);
// one hinted question is enough to forfeit the unaided line
var barelyHinted = playRound([step('right', 1), step('right'), step('right')]).done();
ok('D5 a single hint forfeits the unaided perfect-round message',
   barelyHinted.msg.indexOf('every one exactly right') === -1);
eq('D5 a single hint does not cost the correct total', barelyHinted.correct, '3');

// the count survives the transition to the completion screen
var rSurvive = playRound([step('right', 1), step('right', 1)]);
eq('D6 the hinted count survives into the done screen', rSurvive.T.hinted, 2);
ok('D6 the done screen is the one showing', rSurvive.dom.$('tDone').style.display === 'flex');
ok('D6 the done screen reports the surviving count',
   rSurvive.dom.text('tDoneMsg').indexOf('You used hints on 2 questions.') !== -1);

// =========================================================================
// E. REGRESSION PROTECTION - the tiers, and the code that owns them
// =========================================================================
// the worked example from the brief: 11 / 3 / 1 with 4 hinted questions
var worked = newRound(5);
worked.T.qs = new Array(15);                       /* a full 15-question round */
worked.T.right = 11; worked.T.almost = 3; worked.T.hinted = 4;
worked.api.tShowDone();
eq('E1 the worked example reports 11 correct', worked.dom.text('tScoreN'), '11');
eq('E1 the worked example reports 3 almost', worked.dom.text('tAlmostN'), '3');
eq('E1 the worked example reports 1 missed', worked.dom.text('tMissN'), '1');
ok('E1 the worked example states the exact-right total',
   worked.dom.text('tDoneMsg').indexOf('11 of 15') !== -1);
ok('E1 the worked example names the almost tier',
   worked.dom.text('tDoneMsg').indexOf('3 almost') !== -1);
ok('E1 the worked example names the missed tier',
   worked.dom.text('tDoneMsg').indexOf('1 to revisit') !== -1);
ok('E1 the worked example reports 4 hinted questions',
   worked.dom.text('tDoneMsg').indexOf('You used hints on 4 questions.') !== -1);
ok('E1 hinted questions are not subtracted from the correct total',
   worked.dom.text('tScoreN') === '11' && worked.dom.text('tDoneMsg').indexOf('7 of 15') === -1);

// the same split, hinted and unhinted, must differ ONLY by the added sentence
function summaryFor(total, right, almost, hinted) {
  var h = newRound(2);
  h.T.qs = new Array(total); h.T.right = right; h.T.almost = almost; h.T.hinted = hinted;
  h.api.tShowDone();
  return { correct: h.dom.text('tScoreN'), almost: h.dom.text('tAlmostN'),
           missed: h.dom.text('tMissN'), msg: h.dom.text('tDoneMsg') };
}
[[15, 11, 3], [15, 0, 15], [15, 0, 0], [15, 7, 8], [10, 5, 4], [1, 0, 1]].forEach(function (cmb) {
  var plain = summaryFor(cmb[0], cmb[1], cmb[2], 0);
  var withHints = summaryFor(cmb[0], cmb[1], cmb[2], 2);
  var label = '(' + cmb.join('/') + ')';
  eq('E2 ' + label + ' hints do not move the correct tile', withHints.correct, plain.correct);
  eq('E2 ' + label + ' hints do not move the almost tile', withHints.almost, plain.almost);
  eq('E2 ' + label + ' hints do not move the missed tile', withHints.missed, plain.missed);
  ok('E2 ' + label + ' tiers still sum to the round size',
     Number(withHints.correct) + Number(withHints.almost) + Number(withHints.missed) === cmb[0]);
  eq('E2 ' + label + ' the hint sentence is the only difference',
     withHints.msg, plain.msg + ' You used hints on 2 questions.');
});
// a round object without the field at all (an older shape) must not print a
// hint sentence or lose the perfect-round line
var legacy = newRound(2);
legacy.T.qs = new Array(15); legacy.T.right = 15; legacy.T.almost = 0;
delete legacy.T.hinted;
legacy.api.tShowDone();
ok('E3 a round with no hinted field prints no hint sentence',
   legacy.dom.text('tDoneMsg').indexOf('hint') === -1);
ok('E3 a round with no hinted field keeps the perfect-round message',
   legacy.dom.text('tDoneMsg').indexOf('You typed every one exactly right.') !== -1);

// the shipping code still routes verdicts through the shared comparator, and
// still counts the tiers the way Phase 1B left them
ok('E4 tCheckAnswer still classifies through PP_ANSWER',
   SRC_CHECK.indexOf('PP_ANSWER.classify(val, c, PP_TYPED_INDEX)') !== -1);
ok('E4 tCheckAnswer still counts right and almost unchanged',
   SRC_CHECK.indexOf('if(verdict==="right") T.right++; else if(verdict==="almost") T.almost++;') !== -1);
ok('E4 tCheckAnswer still guards on the round state', SRC_CHECK.indexOf('if(T.state!=="ask") return;') !== -1);
ok('E4 tCheckAnswer still ignores blank input',
   SRC_CHECK.indexOf('if(!PP_ANSWER.normalize(val))') !== -1);
ok('E4 the hint count is banked after the state guard closes the question',
   SRC_CHECK.indexOf('T.state="done";') !== -1 &&
   SRC_CHECK.indexOf('T.state="done";') < SRC_CHECK.indexOf('T.hinted++'));
ok('E4 the hint count is banked on a revealed letter, not on a click',
   SRC_CHECK.indexOf('if(T.revealed>0) T.hinted++;') !== -1);
ok('E4 tShowDone still fills the three tiles from the three counters',
   SRC_DONE.indexOf('$("tScoreN").textContent=right; $("tAlmostN").textContent=almost; $("tMissN").textContent=miss;') !== -1);
ok('E4 tShowDone still derives missed from the round size',
   SRC_DONE.indexOf('miss=T.qs.length-right-almost') !== -1);
ok('E4 tShowDone never folds almost into the correct total', SRC_DONE.indexOf('T.right+T.almost') === -1);
ok('E4 the perfect-round line requires no hints too',
   SRC_DONE.indexOf('right===T.qs.length && hinted===0') !== -1);

// the completion markup is unchanged - three tiles, no fourth
var DONE_MARKUP = INDEX.slice(INDEX.indexOf('<div class="done" id="tDone"'),
                              INDEX.indexOf('id="tHome"'));
eq('E5 the Type It done screen still has exactly three stat tiles',
   (DONE_MARKUP.match(/<div class="stat">/g) || []).length, 3);
ok('E5 the three tiles are still CORRECT / ALMOST / MISSED',
   DONE_MARKUP.indexOf('id="tScoreN">0</b><span>CORRECT<') !== -1 &&
   DONE_MARKUP.indexOf('id="tAlmostN">0</b><span>ALMOST<') !== -1 &&
   DONE_MARKUP.indexOf('id="tMissN">0</b><span>MISSED<') !== -1);
ok('E5 the hint sentence reuses the existing summary paragraph',
   DONE_MARKUP.indexOf('<p id="tDoneMsg"></p>') !== -1);
ok('E5 no new hint node was added to the done screen',
   DONE_MARKUP.indexOf('tHintN') === -1 && DONE_MARKUP.indexOf('tHinted') === -1);

// Mixed Quiz is untouched: its own hint reveal and its own scoring
var SRC_R_REVEAL = bodyOf(INDEX, 'rRevealLetter');
var SRC_R_CHECK  = bodyOf(INDEX, 'rCheckAnswer');
var SRC_R_DONE   = bodyOf(INDEX, 'rShowDone');
ok('E6 Mixed Quiz reveal has no hint counter', SRC_R_REVEAL.indexOf('hinted') === -1);
ok('E6 Mixed Quiz check has no hint counter', SRC_R_CHECK.indexOf('hinted') === -1);
ok('E6 Mixed Quiz done screen has no hint sentence',
   SRC_R_DONE.indexOf('hinted') === -1 && SRC_R_DONE.indexOf('used a hint') === -1);
ok('E6 Mixed Quiz still resets only its own per-question reveal',
   INDEX.indexOf('R.i=0; R.state="ask"; R.revealed=0; R.attempted=false;') !== -1);
ok('E6 the hinted counter lives on the Type It state alone',
   INDEX.indexOf('R.hinted') === -1);
// only ONE activity gained the counter, and it is declared on T
ok('E6 T declares the hinted counter', INDEX.indexOf('const T = {') !== -1 &&
   INDEX.slice(INDEX.indexOf('const T = {'), INDEX.indexOf('const T = {') + 200).indexOf('hinted:0') !== -1);

// ---------- report ----------
console.log('Type It hint tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
LOG.forEach(function (l) { console.log('  ' + l); });
if (FAIL > 0) { throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed'); }
