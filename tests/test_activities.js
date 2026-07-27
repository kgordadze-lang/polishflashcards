// Deterministic tests for pp-usage.js - the Phase-5 usage labels and activity
// eligibility rules. Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_activities.js
// Exit status is 0 only if every assertion passes (printed at the end).
ObjC.import('Foundation');

function readFile(path) {
  var s = $.NSString.stringWithContentsOfFileEncodingError(path, $.NSUTF8StringEncoding, null);
  return ObjC.unwrap(s);
}
function resolveRoot() {
  var fm = $.NSFileManager.defaultManager;
  var cwd = ObjC.unwrap(fm.currentDirectoryPath);
  var candidates = [cwd + '/', cwd + '/../'];
  for (var i = 0; i < candidates.length; i++) {
    if (fm.fileExistsAtPath(candidates[i] + 'pp-usage.js')) return candidates[i];
  }
  return cwd + '/';
}
var ROOT = resolveRoot();
(0, eval)(readFile(ROOT + 'pp-usage.js'));            // defines global PP_USAGE

// ---------- tiny test framework ----------
var PASS = 0, FAIL = 0, LOG = [];
function ok(name, cond) { if (cond) { PASS++; } else { FAIL++; LOG.push('FAIL: ' + name); } }
function eq(name, a, b) {
  var sa = JSON.stringify(a), sb = JSON.stringify(b);
  ok(name + (sa === sb ? '' : '  (got ' + sa + ', want ' + sb + ')'), sa === sb);
}
function texts(card, opts) { return PP_USAGE.labels(card, opts).map(function (l) { return l.text; }); }
var FRONT = { suppressStrengthDuplicate: true };   // the only surface that shows a strength badge

// ---------- fixtures: the shapes that actually occur in the data ----------
var plain      = { id: 'x1', pl: 'kawa', en: 'coffee' };                                  // no metadata at all
var formal     = { id: 'x2', pl: 'kawaler', en: 'single', register: 'formal' };
var informal   = { id: 'x3', pl: 'masakra', en: 'brutal!', register: 'informal' };
var activeSlang= { id: 'x4', pl: 'spoko', en: 'cool', register: 'slang' };                // slang but PRODUCIBLE
var recogSlang = { id: 'x5', pl: 'ustawka', en: 'an arranged fight', register: 'slang',
                   production: 'recognition-only', warning: 'Strongly associated with a fight.' };
var recogRegion= { id: 'x6', pl: 'słoik', en: 'out-of-towner', register: 'slang',
                   region: 'warsaw', production: 'recognition-only', warning: 'Dismissive.' };
var regionOnly = { id: 'x7', pl: 'Mordor', en: 'office district', register: 'slang', region: 'warsaw' };
var vulgarMed  = { id: 'x8', pl: 'gówno', en: 'crap', register: 'vulgar', strength: 'medium' };
var vulgarStr  = { id: 'x9', pl: 'pojebany', en: 'f***ed up', register: 'vulgar', strength: 'strong' };
var vulgarDup  = { id: 'x10', pl: 'jebać', en: 'to f***', register: 'vulgar', strength: 'vulgar' };
var template   = { id: 'x11', pl: 'Gdzie jest...?', en: 'Where is...?', cardType: 'template' };
var intro      = { id: 'x12', pl: 'Stan umysłu', en: 'State of Mind', intro: true };
var noEn       = { id: 'x13', pl: 'coś' };
var regional   = { id: 'x14', pl: 'pyry', en: 'potatoes', region: 'regional' };
var neutralDef = { id: 'x15', pl: 'stół', en: 'table', register: 'neutral', region: 'general', production: 'active' };

// =========================================================================
// 1. defaults render nothing - ordinary cards must look unchanged
eq('T1 plain card has no chips', texts(plain), []);
eq('T1 explicit defaults have no chips', texts(neutralDef), []);
ok('T1 plain summary empty', PP_USAGE.summary(plain) === '');
ok('T1 plain is not recognition-only', PP_USAGE.isRecognitionOnly(plain) === false);

// 2. each register maps to its approved learner-facing label
eq('T2 formal', texts(formal), ['Formal']);
eq('T2 informal', texts(informal), ['Informal']);
eq('T2 slang', texts(activeSlang), ['Slang']);
eq('T2 vulgar', texts(vulgarMed), ['Vulgar']);

// 3. region wording - "Warsaw-associated", never "Warsaw only"
eq('T3 warsaw label', texts(regionOnly), ['Slang', 'Warsaw-associated']);
eq('T3 regional label', texts(regional), ['Regional']);
ok('T3 no "Warsaw only" anywhere', JSON.stringify(PP_USAGE.REGION_LABEL).indexOf('only') === -1);
ok('T3 no "Warsaw-specific" anywhere', JSON.stringify(PP_USAGE.REGION_LABEL).indexOf('specific') === -1);

// 4. recognition-only adds its own chip, on top of register/region
eq('T4 ustawka chips', texts(recogSlang), ['Slang', 'Recognition only']);
eq('T4 słoik chips', texts(recogRegion), ['Slang', 'Warsaw-associated', 'Recognition only']);

// 5. strength/register de-duplication is SURFACE-SPECIFIC.
//    Default = the complete set, because most surfaces show no strength badge.
//    Only the flashcard front, which does show one, opts into suppression.
eq('T5 default is the complete set (jebać)', texts(vulgarDup), ['Vulgar']);
eq('T5 front suppresses the duplicate (jebać)', texts(vulgarDup, FRONT), []);
eq('T5 back / panels keep it (jebać)', texts(vulgarDup), ['Vulgar']);
// different words must both survive, even on the front
eq('T5 strength:medium + Vulgar kept on front', texts(vulgarMed, FRONT), ['Vulgar']);
eq('T5 strength:strong + Vulgar kept on front (pojebany)', texts(vulgarStr, FRONT), ['Vulgar']);
eq('T5 strength:strong + Vulgar kept by default (pojebany)', texts(vulgarStr), ['Vulgar']);
// suppression must not touch anything but an exact word match
eq('T5 informal + strength:mild unaffected on front',
   texts({ pl: 'a', en: 'b', register: 'informal', strength: 'mild' }, FRONT), ['Informal']);
eq('T5 suppression never eats region or recognition-only',
   texts({ pl: 'a', en: 'b', register: 'vulgar', strength: 'vulgar', region: 'warsaw',
           production: 'recognition-only' }, FRONT), ['Warsaw-associated', 'Recognition only']);
ok('T5 underlying metadata untouched', vulgarDup.register === 'vulgar' && vulgarDup.strength === 'vulgar');
ok('T5 no strength field means nothing is ever suppressed',
   texts({ pl: 'a', en: 'b', register: 'vulgar' }, FRONT).join() === 'Vulgar');

// 6. accessible summary sentence - and it must MIRROR the chips on that surface
ok('T6 combined summary', PP_USAGE.summary(recogRegion) === 'Usage: Slang. Warsaw-associated. Recognition only.');
ok('T6 single-label summary', PP_USAGE.summary(formal) === 'Usage: Formal.');
ok('T6 summary follows the same option (front, suppressed)', PP_USAGE.summary(vulgarDup, FRONT) === '');
ok('T6 summary follows the same option (default, complete)', PP_USAGE.summary(vulgarDup) === 'Usage: Vulgar.');
ok('T6 spoken text matches rendered chips on the front',
   PP_USAGE.summary(vulgarStr, FRONT) === 'Usage: ' + texts(vulgarStr, FRONT).join('. ') + '.');
ok('T6 spoken text matches rendered chips by default',
   PP_USAGE.summary(recogRegion) === 'Usage: ' + texts(recogRegion).join('. ') + '.');

// =========================================================================
// 7. recognition-only: kept in flashcards + Listening, dropped from production
ok('T7 recognition-only in flashcards', PP_USAGE.eligibleFor(recogSlang, 'flashcard') === true);
ok('T7 recognition-only in Listening', PP_USAGE.eligibleFor(recogSlang, 'listen') === true);
ok('T7 recognition-only NOT in Type It', PP_USAGE.eligibleFor(recogSlang, 'typeit') === false);
ok('T7 recognition-only NOT in mixed', PP_USAGE.eligibleFor(recogSlang, 'mixed') === false);
ok('T7 słoik same treatment', PP_USAGE.eligibleFor(recogRegion, 'listen') === true &&
                              PP_USAGE.eligibleFor(recogRegion, 'typeit') === false);

// 8. slang/vulgar/formal alone must NOT restrict anything
ok('T8 active slang stays in Type It', PP_USAGE.eligibleFor(activeSlang, 'typeit') === true);
ok('T8 active slang stays in mixed', PP_USAGE.eligibleFor(activeSlang, 'mixed') === true);
ok('T8 vulgar card is not auto-restricted', PP_USAGE.eligibleFor(vulgarMed, 'typeit') === true);
ok('T8 formal card is not auto-restricted', PP_USAGE.eligibleFor(formal, 'typeit') === true);
ok('T8 Warsaw card is not auto-restricted', PP_USAGE.eligibleFor(regionOnly, 'typeit') === true);

// 9. a normal card is eligible everywhere
['flashcard', 'listen', 'typeit', 'mixed'].forEach(function (a) {
  ok('T9 plain card eligible for ' + a, PP_USAGE.eligibleFor(plain, a) === true);
});

// 10. templates and podcast intros stay excluded from practice, kept as flashcards
ok('T10 template is a flashcard', PP_USAGE.eligibleFor(template, 'flashcard') === true);
['listen', 'typeit', 'mixed'].forEach(function (a) {
  ok('T10 template excluded from ' + a, PP_USAGE.eligibleFor(template, a) === false);
});
ok('T11 intro is a flashcard', PP_USAGE.eligibleFor(intro, 'flashcard') === true);
['listen', 'typeit', 'mixed'].forEach(function (a) {
  ok('T11 intro excluded from ' + a, PP_USAGE.eligibleFor(intro, a) === false);
});

// 12. defensive: missing fields and junk input
ok('T12 card without en excluded from practice', PP_USAGE.eligibleFor(noEn, 'typeit') === false);
ok('T12 null card never eligible', PP_USAGE.eligibleFor(null, 'flashcard') === false);
eq('T12 null card has no chips', PP_USAGE.labels(null), []);
ok('T12 unknown register renders nothing', texts({ pl: 'a', en: 'b', register: 'posh' }).length === 0);
ok('T12 unknown region renders nothing', texts({ pl: 'a', en: 'b', region: 'krakow' }).length === 0);
/* Unknown activity now FAILS CLOSED for every card, not just recognition-only
   ones - a typo yields an empty pool, which is visible, instead of silently
   applying the production rule. */
ok('T12 unknown activity is false for a recognition-only card',
   PP_USAGE.eligibleFor(recogSlang, 'something-new') === false);
ok('T12 unknown activity is false for an ORDINARY card too (fail closed)',
   PP_USAGE.eligibleFor(plain, 'something-new') === false);
ok('T12 empty / missing activity also fails closed',
   PP_USAGE.eligibleFor(plain, '') === false && PP_USAGE.eligibleFor(plain, undefined) === false);
ok('T12 near-miss activity names fail closed',
   PP_USAGE.eligibleFor(plain, 'Listen') === false &&
   PP_USAGE.eligibleFor(plain, 'type-it') === false &&
   PP_USAGE.eligibleFor(plain, 'flashcards') === false);

// 12b. SEARCH keeps everything. The search screen indexes whole topics and
//      returns topics, so no card is ever filtered out of it - the helper must
//      say so rather than falling through to the production rule.
ok('T12b recognition-only is searchable (ustawka)', PP_USAGE.eligibleFor(recogSlang, 'search') === true);
ok('T12b recognition-only is searchable (słoik)', PP_USAGE.eligibleFor(recogRegion, 'search') === true);
ok('T12b template is searchable', PP_USAGE.eligibleFor(template, 'search') === true);
ok('T12b podcast intro is searchable', PP_USAGE.eligibleFor(intro, 'search') === true);
ok('T12b ordinary card is searchable', PP_USAGE.eligibleFor(plain, 'search') === true);
ok('T12b vulgar card is searchable', PP_USAGE.eligibleFor(vulgarDup, 'search') === true);
ok('T12b a card missing `en` is still searchable (search shows topics, not answers)',
   PP_USAGE.eligibleFor(noEn, 'search') === true);
// search must not have loosened anything else
ok('T12b recognition-only STILL out of Type It', PP_USAGE.eligibleFor(recogSlang, 'typeit') === false);
ok('T12b recognition-only STILL out of mixed', PP_USAGE.eligibleFor(recogSlang, 'mixed') === false);
ok('T12b recognition-only STILL in Listening', PP_USAGE.eligibleFor(recogSlang, 'listen') === true);
ok('T12b template STILL out of practice',
   PP_USAGE.eligibleFor(template, 'listen') === false &&
   PP_USAGE.eligibleFor(template, 'typeit') === false &&
   PP_USAGE.eligibleFor(template, 'mixed') === false);
ok('T12b intro STILL out of practice',
   PP_USAGE.eligibleFor(intro, 'listen') === false &&
   PP_USAGE.eligibleFor(intro, 'typeit') === false &&
   PP_USAGE.eligibleFor(intro, 'mixed') === false);
ok('T12b null card is not searchable', PP_USAGE.eligibleFor(null, 'search') === false);
// the documented contract, stated as one table
(function () {
  var contract = {
    flashcard: { recog: true,  template: true,  intro: true,  normal: true },
    search:    { recog: true,  template: true,  intro: true,  normal: true },
    listen:    { recog: true,  template: false, intro: false, normal: true },
    typeit:    { recog: false, template: false, intro: false, normal: true },
    mixed:     { recog: false, template: false, intro: false, normal: true }
  };
  Object.keys(contract).forEach(function (a) {
    var e = contract[a];
    ok('T12c contract ' + a + '/recognition-only', PP_USAGE.eligibleFor(recogSlang, a) === e.recog);
    ok('T12c contract ' + a + '/template', PP_USAGE.eligibleFor(template, a) === e.template);
    ok('T12c contract ' + a + '/intro', PP_USAGE.eligibleFor(intro, a) === e.intro);
    ok('T12c contract ' + a + '/normal', PP_USAGE.eligibleFor(plain, a) === e.normal);
  });
})();

// 13. every label the app can render is one of the approved strings
(function () {
  var approved = ['Formal', 'Informal', 'Slang', 'Vulgar', 'Warsaw-associated', 'Regional', 'Recognition only'];
  var produced = Object.keys(PP_USAGE.REGISTER_LABEL).map(function (k) { return PP_USAGE.REGISTER_LABEL[k]; })
    .concat(Object.keys(PP_USAGE.REGION_LABEL).map(function (k) { return PP_USAGE.REGION_LABEL[k]; }))
    .concat([PP_USAGE.RECOGNITION_LABEL]);
  ok('T13 every label is approved', produced.every(function (p) { return approved.indexOf(p) >= 0; }));
  ok('T13 neutral/general/active have no label',
     !PP_USAGE.REGISTER_LABEL.neutral && !PP_USAGE.REGION_LABEL.general);
})();

// 14. the label option must not leak into eligibility
/* jebać is vulgar but NOT recognition-only, so it stays eligible everywhere -
   the label option must have no bearing on eligibility at all. */
['flashcard', 'listen', 'typeit', 'mixed'].forEach(function (a) {
  ok('T14 vulgar-but-active card eligible for ' + a, PP_USAGE.eligibleFor(vulgarDup, a) === true);
});
ok('T14 recognition-only rules still hold',
   PP_USAGE.eligibleFor(recogSlang, 'listen') === true &&
   PP_USAGE.eligibleFor(recogSlang, 'typeit') === false &&
   PP_USAGE.eligibleFor(recogSlang, 'mixed') === false);
ok('T14 template still excluded from practice',
   PP_USAGE.eligibleFor(template, 'flashcard') === true &&
   PP_USAGE.eligibleFor(template, 'listen') === false);
ok('T14 intro still excluded from practice',
   PP_USAGE.eligibleFor(intro, 'flashcard') === true &&
   PP_USAGE.eligibleFor(intro, 'typeit') === false);
ok('T14 opts object is never mutated', (function () {
  var o = { suppressStrengthDuplicate: true };
  PP_USAGE.labels(vulgarDup, o); PP_USAGE.summary(vulgarDup, o);
  return Object.keys(o).length === 1 && o.suppressStrengthDuplicate === true;
})());

// =========================================================================
// 15. MAIN-CARD AUDIO. A template's `pl` is a display pattern, not an utterance:
//     "Gdzie jest...?" is not something anyone says. It used to be synthesised and
//     played as if it were the phrase being taught. The rule below is what the app
//     plays AND what pp_audio_rule.py generates and verifies, so a clip can't exist
//     for a string the app refuses to speak, or vice versa.
var tmplWithAudio = { id: 'x16', pl: 'Gdzie jest...?', en: 'Where is...?', cardType: 'template',
                      audioText: 'Gdzie jest apteka?' };
var tmplBadAudio  = { id: 'x17', pl: 'Poproszę...', en: "I'd like...", cardType: 'template',
                      audioText: 'Poproszę...' };            // still unfinished -> refused
var tmplBraceAudio= { id: 'x18', pl: 'Mam na imię...', en: 'My name is...', cardType: 'template',
                      audioText: 'Mam na imię {imię}.' };    // a pattern, not an utterance
var tmplBlankAudio= { id: 'x19', pl: 'Jestem z...', en: "I'm from...", cardType: 'template',
                      audioText: '   ' };
var tmplEllipsis  = { id: 'x20', pl: 'Boli mnie…', en: 'It hurts...', cardType: 'template' };  // U+2026

// standard card -> pl, exactly as before
eq('T15 standard card speaks pl', PP_USAGE.mainAudioText(plain), 'kawa');
ok('T15 standard card has main audio', PP_USAGE.hasMainAudio(plain) === true);
eq('T15 recognition-only card still speaks pl', PP_USAGE.mainAudioText(recogSlang), 'ustawka');
ok('T15 vulgar card still speaks pl', PP_USAGE.hasMainAudio(vulgarMed) === true);

// template WITHOUT a complete audioText -> nothing, and never the unfinished pl
eq('T15 template without audioText has no main audio', PP_USAGE.mainAudioText(template), '');
ok('T15 template without audioText reports no main audio', PP_USAGE.hasMainAudio(template) === false);
ok('T15 template main audio is NOT its pl', PP_USAGE.mainAudioText(template) !== template.pl);
eq('T15 unicode-ellipsis template has no main audio', PP_USAGE.mainAudioText(tmplEllipsis), '');

// template WITH a complete audioText -> that text
eq('T15 template with complete audioText speaks it',
   PP_USAGE.mainAudioText(tmplWithAudio), 'Gdzie jest apteka?');
ok('T15 template with complete audioText has main audio',
   PP_USAGE.hasMainAudio(tmplWithAudio) === true);
ok('T15 audioText does not replace the displayed pl', tmplWithAudio.pl === 'Gdzie jest...?');

// an audioText that is itself unfinished is refused - no half-measures
eq('T15 unfinished audioText refused', PP_USAGE.mainAudioText(tmplBadAudio), '');
eq('T15 {placeholder} audioText refused', PP_USAGE.mainAudioText(tmplBraceAudio), '');
eq('T15 blank audioText refused', PP_USAGE.mainAudioText(tmplBlankAudio), '');

// completeness predicate, stated directly
ok('T15 complete utterance accepted', PP_USAGE.isCompleteUtterance('Gdzie jest apteka?') === true);
ok('T15 three-dot rejected', PP_USAGE.isCompleteUtterance('Gdzie jest...?') === false);
ok('T15 unicode ellipsis rejected', PP_USAGE.isCompleteUtterance('Boli mnie…') === false);
ok('T15 brace rejected', PP_USAGE.isCompleteUtterance('Mam na imię {imię}.') === false);
ok('T15 empty rejected', PP_USAGE.isCompleteUtterance('') === false);
ok('T15 non-string rejected',
   PP_USAGE.isCompleteUtterance(undefined) === false &&
   PP_USAGE.isCompleteUtterance(null) === false &&
   PP_USAGE.isCompleteUtterance(42) === false);
eq('T15 null card has no main audio', PP_USAGE.mainAudioText(null), '');
ok('T15 card with no pl at all has no main audio', PP_USAGE.hasMainAudio({ id: 'x21' }) === false);

// the two rules are independent: silencing main audio must not change eligibility,
// and the template's own example sentence is untouched by any of this
ok('T15 audio rule does not change eligibility',
   PP_USAGE.eligibleFor(template, 'flashcard') === true &&
   PP_USAGE.eligibleFor(template, 'listen') === false &&
   PP_USAGE.eligibleFor(tmplWithAudio, 'flashcard') === true &&
   PP_USAGE.eligibleFor(tmplWithAudio, 'typeit') === false);
ok('T15 audio rule renders no chips', PP_USAGE.labels(template).length === 0 &&
   PP_USAGE.labels(tmplWithAudio).length === 0);
ok('T15 example sentence is never filtered by the main-audio rule', (function () {
  // `ex` needs a clip whatever the card type - only the MAIN speaker is governed.
  var t = { id: 'x22', pl: 'Gdzie jest...?', en: 'Where is...?', cardType: 'template',
            ex: 'Gdzie jest apteka?' };
  return PP_USAGE.mainAudioText(t) === '' && t.ex === 'Gdzie jest apteka?';
})());
ok('T15 card object is never mutated', (function () {
  var t = { id: 'x23', pl: 'Gdzie jest...?', en: 'Where is...?', cardType: 'template' };
  PP_USAGE.mainAudioText(t); PP_USAGE.hasMainAudio(t);
  return Object.keys(t).length === 4 && t.pl === 'Gdzie jest...?' && t.audioText === undefined;
})());

// ---------- report ----------
console.log('Activity tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
LOG.forEach(function (l) { console.log('  ' + l); });
if (FAIL > 0) { throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed'); }
