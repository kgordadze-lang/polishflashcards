// Characterization tests for pp-answer.js - the shared typed-answer comparator
// used by Type It and by the Mixed Quiz's typed questions. Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_answer_validation.js
// Exit status is 0 only if every assertion passes (printed at the end).
//
// WHAT THIS FILE IS FOR
// pp-answer.js was extracted verbatim from three inline functions in index.html
// (tNormAns / tFold / tAccepted). This suite PINS THE BEHAVIOUR THAT EXISTED
// BEFORE the extraction, so the move can be shown to have changed nothing.
//
// Several assertions below deliberately lock in behaviour that is arguably
// WRONG for a learner - hyphenated answers rejected, for instance. They are
// marked KNOWN-UNDESIRABLE. They are not endorsements; they are the baseline a
// later behaviour change has to consciously break. If you are here to change
// one of those rules, expect the matching test to fail and update it
// deliberately - that failure is the point.
//
// TWO MODES, BOTH REAL
// classify() takes an OPTIONAL answer index. Called without one it is the
// isolated comparator and behaves exactly as it always has, including calling
// two words that fold together an "almost" for each other. Called WITH one -
// which is what the app does - text that is exactly another typeable card's
// answer is "wrong" instead. Every assertion below says which mode it is in.
//
// WHAT THIS FILE DOES NOT TEST
// Nothing here touches the DOM, scoring counters, persistence, focus or audio.
// It covers the pure comparator contract - including index construction against
// SYNTHETIC cards - and a static check that both activities are wired to it.
// Which REAL cards belong in the index, and what the shipped vocabulary
// actually collides on, are tests/test_answer_collisions.js's job. Round
// scoring and UI behaviour are not exercised here and must not be inferred
// from a green run.
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

var window = {};
(0, eval)(readFile(ROOT + 'pp-answer.js'));
var A = window.PP_ANSWER;

// ---------- tiny test framework (same shape as the other suites) ----------
var PASS = 0, FAIL = 0, LOG = [];
function ok(name, cond) { if (cond) { PASS++; } else { FAIL++; LOG.push('FAIL: ' + name); } }
function eq(name, a, b) {
  var sa = JSON.stringify(a), sb = JSON.stringify(b);
  ok(name + (sa === sb ? '' : '  (got ' + sa + ', want ' + sb + ')'), sa === sb);
}
function verdict(name, input, card, want) { eq(name, A.classify(input, card), want); }

// ---------- fixtures ----------
var kawa      = { id: 'f1', pl: 'kawa', en: 'coffee' };
var dzienDobry= { id: 'f2', pl: 'Dzień dobry', en: 'Good morning' };
var lodka     = { id: 'f3', pl: 'łódka', en: 'a small boat' };
var piec5     = { id: 'f4', pl: 'pięć', en: 'five' };
var piecBake  = { id: 'f5', pl: 'piec', en: 'to bake' };
var email     = { id: 'f6', pl: 'adres e-mail', en: 'email address' };
var slashPl   = { id: 'f7', pl: 'a / b', en: 'a or b' };
var parenPl   = { id: 'f8', pl: 'kilogram (kilo)', en: 'kilogram' };
var karta     = { id: 'f9', pl: 'karta', en: 'menu', acceptedAnswers: ['menu'] };
var moj       = { id: 'f10', pl: 'mój', en: 'my (m / f)', acceptedAnswers: ['moja'] };
var ellipsis  = { id: 'f11', pl: 'Gdzie jest...?', en: 'Where is...?' };

// =========================================================================
// 1. THE EXACT TIER -> "right"
verdict('T1 exact answer', 'kawa', kawa, 'right');
verdict('T1 different capitalization', 'KAWA', kawa, 'right');
verdict('T1 mixed capitalization', 'KaWa', kawa, 'right');
verdict('T1 leading and trailing whitespace', '   kawa   ', kawa, 'right');
verdict('T1 tab and newline around the answer', '\tkawa\n', kawa, 'right');
verdict('T1 repeated internal whitespace', 'dzień     dobry', dzienDobry, 'right');
verdict('T1 capitalization + spacing together', '  DZIEŃ   DOBRY  ', dzienDobry, 'right');

// terminal punctuation the comparator currently ignores: ? ! . , ; : “ ” " '
verdict('T2 trailing exclamation ignored', 'kawa!', kawa, 'right');
verdict('T2 trailing question mark ignored', 'kawa?', kawa, 'right');
verdict('T2 trailing full stop ignored', 'kawa.', kawa, 'right');
verdict('T2 comma ignored', 'kawa,', kawa, 'right');
verdict('T2 semicolon and colon ignored', 'kawa;:', kawa, 'right');
verdict('T2 straight quotes ignored', '"kawa"', kawa, 'right');
verdict('T2 curly quotes ignored', '“kawa”', kawa, 'right');
verdict('T2 trailing apostrophe ignored', "kawa'", kawa, 'right');
// Punctuation is replaced by a SPACE, not deleted - so punctuation *inside* a
// word splits it in two. Pinned as current behaviour, not endorsed.
eq('T2 punctuation collapses to a single space, not nothing',
   A.normalize('a.b'), 'a b');
eq('T2 an internal apostrophe splits the word', A.normalize("kaw'a"), 'kaw a');
verdict('T2 KNOWN-UNDESIRABLE internal apostrophe makes it wrong', "kaw'a", kawa, 'wrong');

// ellipsis: three dots and U+2026 both become a space
eq('T3 three-dot ellipsis becomes a space', A.normalize('Gdzie jest...?'), 'gdzie jest');
eq('T3 unicode ellipsis becomes a space', A.normalize('Gdzie jest…?'), 'gdzie jest');
verdict('T3 ellipsis answer matches its ellipsis-free form', 'Gdzie jest', ellipsis, 'right');
verdict('T3 unicode ellipsis input matches three-dot card', 'Gdzie jest…?', ellipsis, 'right');

// =========================================================================
// 4. THE DIACRITIC TIER -> "almost"
verdict('T4 correct diacritics are right, not almost', 'dzień dobry', dzienDobry, 'right');
verdict('T4 missing diacritics are almost', 'dzien dobry', dzienDobry, 'almost');
verdict('T4 missing ogonek is almost', 'pieć', piec5, 'almost');
verdict('T4 every Polish diacritic dropped is still almost',
        'aeoszzcn', { pl: 'ąęóśżźćń' }, 'almost');
eq('T5 fold strips ogonki and accents', A.fold('ąęóśżźćń'), 'aeoszzcn');

// stroked l has no NFD decomposition and is mapped by hand
verdict('T5 ł typed as l is almost', 'lodka', lodka, 'almost');
verdict('T5 correct ł is right', 'łódka', lodka, 'right');
verdict('T5 capital Ł lowercases before folding', 'ŁÓDKA', lodka, 'right');
eq('T5 fold maps ł to l', A.fold('łódka'), 'lodka');
eq('T5 normalize does NOT map ł to l', A.normalize('łódka'), 'łódka');

// =========================================================================
// 6. GENUINELY WRONG ANSWERS
verdict('T6 unrelated word is wrong', 'herbata', kawa, 'wrong');
verdict('T6 truncated answer is wrong (no edit distance)', 'kaw', kawa, 'wrong');
verdict('T6 one extra letter is wrong (no edit distance)', 'kawaa', kawa, 'wrong');
verdict('T6 transposed letters are wrong (no typo tolerance)', 'kwaa', kawa, 'wrong');
verdict('T6 empty string is wrong when it reaches the comparator', '', kawa, 'wrong');

// =========================================================================
// 7. ACCEPTED ANSWERS
eq('T7 card without acceptedAnswers yields just pl', A.accepted(kawa), ['kawa']);
eq('T7 card with acceptedAnswers puts pl first', A.accepted(karta), ['karta', 'menu']);
verdict('T7 canonical pl accepted', 'karta', karta, 'right');
verdict('T7 acceptedAnswers entry accepted', 'menu', karta, 'right');
verdict('T7 acceptedAnswers match is case-insensitive too', 'MENU', karta, 'right');
verdict('T7 acceptedAnswers match tolerates spacing', '  menu  ', karta, 'right');
verdict('T7 gendered alternative accepted', 'moja', moj, 'right');
verdict('T7 acceptedAnswers folded match is almost', 'moj', moj, 'almost');
verdict('T7 something outside the accepted set is wrong', 'jadłospis', karta, 'wrong');
eq('T8 a bare string is shorthand for { pl }', A.accepted('kawa'), ['kawa']);
eq('T8 empty acceptedAnswers array is harmless',
   A.accepted({ pl: 'x', acceptedAnswers: [] }), ['x']);
eq('T8 falsy acceptedAnswers entries are skipped',
   A.accepted({ pl: 'x', acceptedAnswers: ['', null, 'y'] }), ['x', 'y']);
eq('T8 an acceptedAnswers entry equal to pl is not duplicated',
   A.accepted({ pl: 'x', acceptedAnswers: ['x', 'y'] }), ['x', 'y']);
ok('T8 pl stays at index 0 (the reveal-a-letter hint reads it)',
   A.accepted(karta)[0] === 'karta' && A.accepted(moj)[0] === 'mój');

// =========================================================================
// 9. RULES THAT DELIBERATELY DO NOT EXIST
// A slash in visible text never creates alternatives.
eq('T9 accepted() does not split on "/"', A.accepted(slashPl), ['a / b']);
verdict('T9 the whole slashed string matches', 'a / b', slashPl, 'right');
verdict('T9 the left branch alone is wrong', 'a', slashPl, 'wrong');
verdict('T9 the right branch alone is wrong', 'b', slashPl, 'wrong');
// Parenthetical text is compared literally; it is not optional.
verdict('T9 full parenthetical string matches', 'kilogram (kilo)', parenPl, 'right');
verdict('T9 dropping the parenthetical is wrong', 'kilogram', parenPl, 'wrong');
verdict('T9 the parenthetical alone is wrong', 'kilo', parenPl, 'wrong');
ok('T9 parentheses survive normalize', A.normalize('kilogram (kilo)') === 'kilogram (kilo)');

// KNOWN-UNDESIRABLE, pinned deliberately: a hyphen is not folded to a space,
// so spelling variants a learner would consider correct are still rejected.
verdict('T10 KNOWN-UNDESIRABLE hyphen vs space stays wrong', 'adres e mail', email, 'wrong');
verdict('T10 KNOWN-UNDESIRABLE hyphen removed stays wrong', 'adres email', email, 'wrong');
verdict('T10 the hyphenated form itself is right', 'adres e-mail', email, 'right');
ok('T10 normalize leaves hyphens alone', A.normalize('adres e-mail') === 'adres e-mail');
ok('T10 fold does not rescue the hyphen either',
   A.fold('adres e mail') !== A.fold('adres e-mail'));

// ISOLATED MODE (no index): two different words that collapse to the same
// folded key still earn "almost" for each other, because a comparator with no
// corpus in front of it has no way to know the typed text is a real word of its
// own. This is the contract for classify() called with two arguments, and it is
// unchanged. The app never calls it that way - see T20 for the same pair with
// an index, where both directions are "wrong".
verdict('T11 isolated mode: piec for five is almost', 'piec', piec5, 'almost');
verdict('T11 isolated mode: five for piec is almost', 'pięć', piecBake, 'almost');
ok('T11 the two really do fold together', A.fold('pięć') === A.fold('piec'));
ok('T11 but they are distinct under normalize',
   A.normalize('pięć') !== A.normalize('piec'));

// =========================================================================
// 12. PURITY: no mutation, no shared state, repeatable
ok('T12 classify does not mutate the card', (function () {
  var card = { id: 'm1', pl: 'karta', en: 'menu', acceptedAnswers: ['menu'] };
  var before = JSON.stringify(card);
  A.classify('menu', card); A.classify('zzz', card); A.classify('KARTA', card);
  return JSON.stringify(card) === before;
})());
ok('T12 accepted does not mutate the card', (function () {
  var card = { id: 'm2', pl: 'karta', acceptedAnswers: ['menu'] };
  var before = JSON.stringify(card);
  A.accepted(card); A.accepted(card);
  return JSON.stringify(card) === before;
})());
ok('T12 accepted does not mutate the acceptedAnswers array', (function () {
  var arr = ['menu'];
  var card = { id: 'm3', pl: 'karta', acceptedAnswers: arr };
  A.accepted(card);
  return arr.length === 1 && arr[0] === 'menu';
})());
ok('T12 accepted returns a fresh array each call', (function () {
  var card = { id: 'm4', pl: 'karta', acceptedAnswers: ['menu'] };
  var a = A.accepted(card), b = A.accepted(card);
  a.push('injected');
  return a !== b && b.length === 2 && A.accepted(card).length === 2;
})());
ok('T12 normalize does not mutate its input', (function () {
  var s = '  Dzień   Dobry!  ';
  A.normalize(s); A.fold(s);
  return s === '  Dzień   Dobry!  ';
})());
ok('T13 repeated classify calls return identical results', (function () {
  var r = [];
  for (var i = 0; i < 5; i++) r.push(A.classify('dzien dobry', dzienDobry));
  return r.every(function (x) { return x === 'almost'; });
})());
ok('T13 repeated normalize calls are identical', (function () {
  var a = A.normalize('  KAWA!  '), b = A.normalize('  KAWA!  ');
  return a === b && a === 'kawa';
})());
ok('T13 normalize is idempotent', A.normalize(A.normalize('  KAWA!  ')) === A.normalize('  KAWA!  '));
ok('T13 fold is idempotent', A.fold(A.fold('łódka')) === A.fold('łódka'));
ok('T13 classify only ever returns one of three verdicts', (function () {
  var seen = {}, cards = [kawa, karta, moj, lodka, piec5, email, slashPl, parenPl];
  var inputs = ['kawa', 'menu', 'moj', 'lodka', 'piec', 'adres e mail', 'a', 'kilo', '', 'zzz'];
  cards.forEach(function (c) { inputs.forEach(function (i) { seen[A.classify(i, c)] = true; }); });
  return Object.keys(seen).every(function (k) {
    return k === 'right' || k === 'almost' || k === 'wrong';
  });
})());

// =========================================================================
// 18. THE ANSWER INDEX - which card owns an exact answer
// buildIndex() is the whole mechanism: a map from normalized exact answer to
// the stable ids of the cards that accept it. Nothing else. All fixtures here
// are INVENTED strings, so nothing in this section can accidentally pass
// because of something in the real vocabulary.
var IDX = A.buildIndex([kawa, karta, lodka, piec5, piecBake]);

eq('T18 keys are normalized exact answers, one per distinct answer',
   Object.keys(IDX.owners).sort(),
   ['karta', 'kawa', 'menu', 'piec', 'pięć', 'łódka'].sort());
eq('T18 the canonical pl is indexed', IDX.owners['kawa'], ['f1']);
eq('T18 an acceptedAnswers entry is indexed too', IDX.owners['menu'], ['f9']);
eq('T18 a card owns every answer it accepts', IDX.owners['karta'], ['f9']);
ok('T18 values are stable ids, not card objects',
   IDX.owners['kawa'].every(function (v) { return typeof v === 'string'; }));

// keys are normalize() output, so case and spacing never fork an owner
eq('T18 answers are keyed case- and space-insensitively',
   A.buildIndex([{ id: 'c1', pl: '  KaWa  ' }]).owners['kawa'], ['c1']);

// one card listing the same answer several ways is ONE owner, recorded once
var dupOwner = A.buildIndex([{ id: 'd1', pl: 'dupex', acceptedAnswers: ['DUPEX', '  dupex  ', 'dupex!'] }]);
eq('T18 duplicate ownership by one stable id is deduplicated',
   dupOwner.owners['dupex'], ['d1']);
eq('T18 and it produces no other keys', Object.keys(dupOwner.owners), ['dupex']);

// empty answers never become keys
var emptyish = A.buildIndex([{ id: 'e1', pl: '   ', acceptedAnswers: ['', '  ', '...', 'realx'] }]);
eq('T18 blank and punctuation-only answers are skipped',
   Object.keys(emptyish.owners), ['realx']);

// a card with no stable id cannot own anything - it could not be told apart
// from the card being answered, so it must not be able to veto an "almost"
eq('T18 a card without an id contributes nothing',
   Object.keys(A.buildIndex([{ pl: 'ćwiks', en: 'no id' }]).owners), []);
eq('T18 buildIndex tolerates no argument', Object.keys(A.buildIndex().owners), []);
eq('T18 buildIndex tolerates an empty list', Object.keys(A.buildIndex([]).owners), []);
eq('T18 buildIndex skips holes in the card list',
   Object.keys(A.buildIndex([null, undefined, kawa]).owners), ['kawa']);

// purity
ok('T18 buildIndex does not mutate the cards it reads', (function () {
  var card = { id: 'p1', pl: 'karta', acceptedAnswers: ['menu'] };
  var before = JSON.stringify(card);
  A.buildIndex([card]);
  return JSON.stringify(card) === before;
})());
ok('T18 buildIndex is deterministic', (function () {
  var cards = [kawa, karta, piec5];
  return JSON.stringify(A.buildIndex(cards)) === JSON.stringify(A.buildIndex(cards));
})());

// =========================================================================
// 19. ownedByOther() - the one question the guard asks
ok('T19 an answer belonging to a different card is owned by another',
   A.ownedByOther(IDX, 'piec', piec5) === true);
ok('T19 a card does not count as another owner of its own answer',
   A.ownedByOther(IDX, 'kawa', kawa) === false);
ok('T19 unknown text is owned by nobody', A.ownedByOther(IDX, 'zzzzz', kawa) === false);
ok('T19 with no index the question is unanswerable, so: no',
   A.ownedByOther(null, 'piec', piec5) === false);
ok('T19 an index-shaped object with no owners answers no',
   A.ownedByOther({}, 'piec', piec5) === false);
ok('T19 a card with no id can never be compared against, so: no',
   A.ownedByOther(IDX, 'piec', { pl: 'pięć' }) === false);
ok('T19 the lookup normalizes its text', A.ownedByOther(IDX, '  PIEC!  ', piec5) === true);
ok('T19 an inherited key on a hand-built index is not an owner',
   A.ownedByOther({ owners: {} }, 'constructor', kawa) === false);
ok('T19 and buildIndex never exposes one either',
   A.buildIndex([kawa]).owners['constructor'] === undefined);

// =========================================================================
// 20. INDEXED MODE - the collision-safe verdicts
// A synthetic pair of different exact answers that fold to the same key.
var synA = { id: 'y1', pl: 'ćwiks', en: 'fixture A' };
var synB = { id: 'y2', pl: 'cwiks', en: 'fixture B' };
var SYN = A.buildIndex([synA, synB]);
ok('T20 the synthetic pair really does fold together', A.fold('ćwiks') === A.fold('cwiks'));
ok('T20 and really is two different exact answers', A.normalize('ćwiks') !== A.normalize('cwiks'));
verdict('T20 isolated, one for the other is almost', 'cwiks', synA, 'almost');
eq('T20 indexed, typing B for A is wrong', A.classify('cwiks', synA, SYN), 'wrong');
eq('T20 indexed, the reverse direction is wrong too', A.classify('ćwiks', synB, SYN), 'wrong');
eq('T20 each card still gets its own answer right', A.classify('ćwiks', synA, SYN), 'right');
eq('T20 and so does the other', A.classify('cwiks', synB, SYN), 'right');

// the collision may live in an acceptedAnswers entry rather than in pl
var accA = { id: 'y3', pl: 'zzz alpha', en: 'fixture C', acceptedAnswers: ['żóks'] };
var accB = { id: 'y4', pl: 'zoks', en: 'fixture D' };
var ACC = A.buildIndex([accA, accB]);
eq('T20 an acceptedAnswers entry is indexed as an owner', ACC.owners['żóks'], ['y3']);
eq('T20 indexed, a collision reached through acceptedAnswers is wrong',
   A.classify('zoks', accA, ACC), 'wrong');
eq('T20 and the reverse, against the plain card, is wrong', A.classify('żóks', accB, ACC), 'wrong');
eq('T20 the acceptedAnswers entry itself is still right', A.classify('żóks', accA, ACC), 'right');
verdict('T20 isolated, the same acceptedAnswers collision is only almost', 'zoks', accA, 'almost');

// only the "almost" tier is guarded - the index can never demote a "right"
eq('T20 an exact answer is right even when another card owns it too',
   A.classify('kawa', kawa, A.buildIndex([kawa, { id: 'y5', pl: 'kawa', en: 'a second coffee card' }])),
   'right');
// and ordinary near-misses are untouched by the index
eq('T20 an ordinary missing diacritic is still almost', A.classify('lodka', lodka, IDX), 'almost');
eq('T20 an unrelated word is still wrong', A.classify('herbata', kawa, IDX), 'wrong');
eq('T20 a card with no id keeps the pre-index verdict', A.classify('cwiks', { pl: 'ćwiks' }, SYN), 'almost');
ok('T20 indexed classify still only ever returns the three verdicts', (function () {
  var seen = {}, cards = [kawa, karta, lodka, piec5, piecBake, synA, synB];
  var inputs = ['kawa', 'menu', 'lodka', 'piec', 'pięć', 'cwiks', 'ćwiks', '', 'zzz'];
  cards.forEach(function (c) { inputs.forEach(function (i) { seen[A.classify(i, c, SYN)] = true; }); });
  return Object.keys(seen).every(function (k) {
    return k === 'right' || k === 'almost' || k === 'wrong';
  });
})());
ok('T20 indexed classify does not mutate the card or the index', (function () {
  var card = { id: 'y6', pl: 'ćwiks', en: 'x' };
  var idx = A.buildIndex([card, synB]);
  var b1 = JSON.stringify(card), b2 = JSON.stringify(idx);
  A.classify('cwiks', card, idx); A.classify('ćwiks', card, idx); A.classify('zzz', card, idx);
  return JSON.stringify(card) === b1 && JSON.stringify(idx) === b2;
})());

// =========================================================================
// 21. TWO CARDS MAY SHARE ONE EXACT ANSWER
// Common in the real data (the same word taught in two topics). Sharing an
// exact answer must never make either card's own answer wrong.
var shrA = { id: 'z1', pl: 'wódex', en: 'fixture E' };
var shrB = { id: 'z2', pl: 'wódex', en: 'fixture F' };
var SHR = A.buildIndex([shrA, shrB]);
eq('T21 one answer, two owners', SHR.owners['wódex'], ['z1', 'z2']);
eq('T21 the shared answer is right for the first card', A.classify('wódex', shrA, SHR), 'right');
eq('T21 the shared answer is right for the second card too', A.classify('wódex', shrB, SHR), 'right');
eq('T21 shared exact wording creates no false wrong on a near-miss',
   A.classify('wodex', shrA, SHR), 'almost');
eq('T21 and none on the other card either', A.classify('wodex', shrB, SHR), 'almost');
// sharing plus a real collision: the collision still wins for the OTHER word
var shrC = { id: 'z3', pl: 'wodex', en: 'fixture G' };
var SHR2 = A.buildIndex([shrA, shrB, shrC]);
eq('T21 the shared answer is still right for both owners',
   [A.classify('wódex', shrA, SHR2), A.classify('wódex', shrB, SHR2)], ['right', 'right']);
eq('T21 but the now-owned fold key is wrong', A.classify('wodex', shrA, SHR2), 'wrong');
eq('T21 and its own owner still gets it right', A.classify('wodex', shrC, SHR2), 'right');

// =========================================================================
// 14. STATIC WIRING CHECK
// Narrow on purpose: it proves both activities route through the shared
// comparator and that the old inline copies are gone. It does NOT execute the
// app, so it says nothing about scoring, focus or any UI behaviour.
var INDEX = readFile(ROOT + 'index.html');
var SW = readFile(ROOT + 'sw.js');
var ANSWER_SRC = readFile(ROOT + 'pp-answer.js');
var USAGE_SRC = readFile(ROOT + 'pp-usage.js');

function occurrences(src, needle) {
  var n = 0, at = src.indexOf(needle);
  while (at !== -1) { n++; at = src.indexOf(needle, at + needle.length); }
  return n;
}

function bodyOf(src, name) {
  var start = src.indexOf('function ' + name + '(');
  if (start === -1) throw new Error('wiring: function ' + name + ' not found in index.html');
  var open = src.indexOf('{', src.indexOf(')', start)), depth = 0;
  for (var j = open; j < src.length; j++) {
    if (src[j] === '{') depth++;
    else if (src[j] === '}') { depth--; if (depth === 0) return src.slice(start, j + 1); }
  }
  throw new Error('wiring: unbalanced braces for ' + name);
}

// (a) the utility is loaded as a real script include, before anything uses it
var tagAt = INDEX.indexOf('<script src="pp-answer.js"></script>');
ok('T14 index.html includes pp-answer.js as a script src', tagAt !== -1);
ok('T14 pp-answer.js is loaded before the first PP_ANSWER use',
   tagAt !== -1 && tagAt < INDEX.indexOf('PP_ANSWER.'));
ok('T14 pp-answer.js loads alongside the other shared helpers',
   tagAt > INDEX.indexOf('<script src="pp-usage.js">') &&
   tagAt < INDEX.indexOf('<script src="pp-migrate.js">'));

// (b) both typed activities use the SAME comparator
var tCheck = bodyOf(INDEX, 'tCheckAnswer');
var rCheck = bodyOf(INDEX, 'rCheckAnswer');
ok('T14 Type It classifies through PP_ANSWER', tCheck.indexOf('PP_ANSWER.classify(') !== -1);
ok('T14 Mixed Quiz typed questions classify through PP_ANSWER',
   rCheck.indexOf('PP_ANSWER.classify(') !== -1);
ok('T14 Type It blank guard uses PP_ANSWER.normalize', tCheck.indexOf('PP_ANSWER.normalize(') !== -1);
ok('T14 Mixed Quiz blank guard uses PP_ANSWER.normalize', rCheck.indexOf('PP_ANSWER.normalize(') !== -1);
ok('T14 both reveal-a-letter hints read PP_ANSWER.accepted',
   bodyOf(INDEX, 'tRevealLetter').indexOf('PP_ANSWER.accepted(') !== -1 &&
   bodyOf(INDEX, 'rRevealLetter').indexOf('PP_ANSWER.accepted(') !== -1);

// (b2) both typed activities hand classify the SAME shared answer index, and
// that index is built ONCE at load - never inside an answer submission.
ok('T22 Type It passes the shared answer index',
   tCheck.indexOf('PP_ANSWER.classify(val, c, PP_TYPED_INDEX)') !== -1);
ok('T22 Mixed Quiz typed questions pass the same shared answer index',
   rCheck.indexOf('PP_ANSWER.classify(val, c, PP_TYPED_INDEX)') !== -1);
ok('T22 there are exactly two classify call sites and both are indexed',
   occurrences(INDEX, 'PP_ANSWER.classify(') === 2 &&
   occurrences(INDEX, 'PP_ANSWER.classify(val, c, PP_TYPED_INDEX)') === 2);
ok('T22 the index is built exactly once in the whole app',
   occurrences(INDEX, 'PP_ANSWER.buildIndex(') === 1);
ok('T22 the one build is a top-level const, evaluated at load',
   INDEX.indexOf('const PP_TYPED_INDEX = PP_ANSWER.buildIndex(PP_USAGE.typedPracticeCards(LEVELS));') !== -1);
ok('T22 Type It answer checking does not build an index',
   tCheck.indexOf('buildIndex') === -1);
ok('T22 Mixed Quiz answer checking does not build an index',
   rCheck.indexOf('buildIndex') === -1);
ok('T22 the index is fed the typed-practice card set, not raw LEVELS',
   INDEX.indexOf('PP_ANSWER.buildIndex(PP_USAGE.typedPracticeCards(') !== -1);
// the card selection reuses the eligibility rules that already exist
ok('T22 typedPracticeCards routes both activities through eligibleFor',
   USAGE_SRC.indexOf('PP_USAGE.eligibleFor(c, "typeit")') !== -1 &&
   USAGE_SRC.indexOf('PP_USAGE.eligibleFor(c, "mixed")') !== -1);

// (b3) the mechanism is data-driven: no Polish word is written into it. Every
// word this suite and the corpus suite collide on is checked against both
// shared helpers, so a "fix" that special-cases a word fails here.
['pięć', 'piec', 'łódka', 'ćwiks', 'cwiks', 'żóks', 'zoks', 'wódex', 'wodex', 'dupex']
  .forEach(function (w) {
    ok('T22 pp-answer.js hardcodes no answer word (' + w + ')', ANSWER_SRC.indexOf(w) === -1);
    ok('T22 pp-usage.js hardcodes no answer word (' + w + ')', USAGE_SRC.indexOf(w) === -1);
    ok('T22 index.html hardcodes no answer word (' + w + ')', INDEX.indexOf(w) === -1);
  });
// the comparator stays free of DOM, storage, audio and randomness
['document', 'window.', 'localStorage', 'sessionStorage', 'Math.random', 'Audio', 'speechSynthesis']
  .forEach(function (banned) {
    ok('T22 pp-answer.js contains no ' + banned,
       ANSWER_SRC.replace(/typeof window !== "undefined" \? window : this/, '').indexOf(banned) === -1);
  });

// (c) the old inline copies are gone - not merely unused
ok('T15 inline tNormAns is gone', INDEX.indexOf('function tNormAns') === -1);
ok('T15 inline tFold is gone', INDEX.indexOf('function tFold') === -1);
ok('T15 inline tAccepted is gone', INDEX.indexOf('function tAccepted') === -1);
ok('T15 no call site still references the old names',
   INDEX.indexOf('tNormAns(') === -1 && INDEX.indexOf('tFold(') === -1 &&
   INDEX.indexOf('tAccepted(') === -1);

// (d) the app shell can still be cached offline with the new file in it
ok('T16 sw.js precaches pp-answer.js', SW.indexOf('"./pp-answer.js"') !== -1);

// APP_VERSION, CACHE and AUDIO_CACHE are deliberately NOT pinned here. They are
// release identifiers, meant to be bumped by a deployment; asserting their exact
// values would make this suite fail on a correct release rather than on a broken
// comparator. Whether a given CHANGE was allowed to touch them is a question for
// that change's review, not a standing assertion in the answer tests.

// ---------- report ----------
console.log('Answer validation tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
LOG.forEach(function (l) { console.log('  ' + l); });
if (FAIL > 0) { throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed'); }
