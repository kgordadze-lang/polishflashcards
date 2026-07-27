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
// WRONG for a learner - hyphenated answers rejected, "piec" accepted for the
// number five. They are marked KNOWN-UNDESIRABLE. They are not endorsements;
// they are the baseline a later behaviour change has to consciously break.
// If you are here to change one of those rules, expect the matching test to
// fail and update it deliberately - that failure is the point.
//
// WHAT THIS FILE DOES NOT TEST
// Nothing here touches the DOM, scoring counters, persistence, focus, audio or
// eligibility. It covers the pure comparator contract and a static check that
// both activities are wired to it. Round scoring and UI behaviour are not
// exercised and must not be inferred from a green run here.
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

// KNOWN-UNDESIRABLE, pinned deliberately: these are two different words that
// collapse to the same folded key, so each earns "almost" for the other.
verdict('T11 KNOWN-UNDESIRABLE piec for five is almost', 'piec', piec5, 'almost');
verdict('T11 KNOWN-UNDESIRABLE five for piec is almost', 'pięć', piecBake, 'almost');
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
// 14. STATIC WIRING CHECK
// Narrow on purpose: it proves both activities route through the shared
// comparator and that the old inline copies are gone. It does NOT execute the
// app, so it says nothing about scoring, focus or any UI behaviour.
var INDEX = readFile(ROOT + 'index.html');
var SW = readFile(ROOT + 'sw.js');

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

// (c) the old inline copies are gone - not merely unused
ok('T15 inline tNormAns is gone', INDEX.indexOf('function tNormAns') === -1);
ok('T15 inline tFold is gone', INDEX.indexOf('function tFold') === -1);
ok('T15 inline tAccepted is gone', INDEX.indexOf('function tAccepted') === -1);
ok('T15 no call site still references the old names',
   INDEX.indexOf('tNormAns(') === -1 && INDEX.indexOf('tFold(') === -1 &&
   INDEX.indexOf('tAccepted(') === -1);

// (d) the app shell can still be cached offline with the new file in it
ok('T16 sw.js precaches pp-answer.js', SW.indexOf('"./pp-answer.js"') !== -1);

// (e) this phase must not have touched the version or cache identifiers
ok('T17 APP_VERSION untouched', INDEX.indexOf('const APP_VERSION = "7.27"') !== -1);
ok('T17 CACHE untouched', SW.indexOf('const CACHE = "popolsku-v53"') !== -1);
ok('T17 AUDIO_CACHE untouched', SW.indexOf('const AUDIO_CACHE = "popolsku-audio"') !== -1);

// ---------- report ----------
console.log('Answer validation tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
LOG.forEach(function (l) { console.log('  ' + l); });
if (FAIL > 0) { throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed'); }
