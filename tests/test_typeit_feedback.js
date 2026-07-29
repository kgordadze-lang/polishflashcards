// Deterministic tests for TYPE IT FEEDBACK - the accepted-alternative line.
// Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_typeit_feedback.js
// Exit status is 0 only if every assertion passes (printed at the end).
//
// WHAT THIS FILE IS FOR
// Priority 3 Phase 2B: an aspect-pair card accepts EITHER aspect, so a learner
// who types "oddac" for the card whose `pl` is "oddawac" is told "Dobrze!" and
// then shown a canonical answer that is not what they typed. The feedback panel
// must explain that by naming the whole pair - "Aspect pair: oddawac / oddac" -
// taken from the authored `pair`, never rebuilt from `pl` + acceptedAnswers.
//
// The panel shows ONE alternative line, first match wins:
//     aspect pair      -> the authored `pair`         ("Aspect pair")
//     variants         -> synonym / gender forms      ("Also" / "Forms")
//     acceptedAnswers  -> abbreviation-style cards    ("Also accepted")
// so an aspect-pair card never shows "Aspect pair" AND "Also accepted" at once.
//
// HOW IT TESTS
// It does not re-implement the panel. It lifts the real ppVariantParts,
// ppAppendUsageTo, startTypeit, tRender, tRevealLetter, tCheckAnswer and
// tShowDone - and the Mixed Quiz's rCheckAnswer/rRecord - out of index.html and
// runs them against the REAL corpus, the REAL PP_ANSWER/PP_USAGE and a small
// DOM that actually parses the markup the code assigns. Assertions therefore
// read the rendered nodes a learner would see, not a copy of the template, and
// "the pair appears exactly once" is a claim about rendered text.
//
// SCOPE - what deliberately is NOT here
// How a verdict is DECIDED belongs to tests/test_answer_validation.js and
// tests/test_answer_collisions.js; how right/almost/missed are COUNTED belongs
// to tests/test_round_scoring.js; hint reporting belongs to
// tests/test_typeit_hints.js. This file owns the alternative line only, plus
// the guarantee that showing it changed none of the above and left the Mixed
// Quiz alone. Release identifiers - APP_VERSION, CACHE, AUDIO_CACHE - are not
// pinned here: they change on purpose at release time, and a permanent
// regression suite must not fail for that.
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

// =========================================================================
// A SMALL REAL DOM
// The production code assigns a template to innerHTML and then fills the
// spans through textContent, so a stub that only records strings could not
// tell "shown once" from "shown twice", nor textContent from interpolation.
// This parses what is assigned, so both questions have real answers.
// =========================================================================
function mkText(s) { return { nodeType: 3, text: String(s) }; }
function textOf(node) {
  if (node.nodeType === 3) return node.text;
  return node.children.map(textOf).join('');
}
function classesOf(el) {
  return ((el.attrs['class'] || '') + ' ' + (el.className || '')).split(/\s+/)
    .filter(function (s) { return s; });
}
function walk(el, out) {
  el.children.forEach(function (ch) {
    if (ch.nodeType !== 1) return;
    out.push(ch); walk(ch, out);
  });
  return out;
}
function matches(el, sel) {
  if (sel.charAt(0) === '.') return classesOf(el).indexOf(sel.slice(1)) !== -1;
  return el.tag === sel;
}
function El(tag) {
  var self = { tag: tag, attrs: {}, children: [], nodeType: 1,
               className: '', style: {}, value: '', disabled: false,
               hidden: false, focused: 0 };
  self.setAttribute = function (k, v) { self.attrs[k] = String(v); };
  self.getAttribute = function (k) {
    return Object.prototype.hasOwnProperty.call(self.attrs, k) ? self.attrs[k] : null;
  };
  self.appendChild = function (ch) { self.children.push(ch); return ch; };
  self.focus = function () { self.focused++; };
  Object.defineProperty(self, 'textContent', {
    get: function () { return textOf(self); },
    set: function (v) { self.children = [mkText(v)]; }
  });
  Object.defineProperty(self, 'innerHTML', {
    get: function () { return serialize(self); },
    set: function (v) { self.children = parseHTML(String(v)); }
  });
  self.querySelector = function (sel) {
    var r = walk(self, []).filter(function (e) { return matches(e, sel); });
    return r.length ? r[0] : null;
  };
  self.querySelectorAll = function (sel) {
    return walk(self, []).filter(function (e) { return matches(e, sel); });
  };
  return self;
}
function decodeEntities(s) {
  return s.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"')
          .replace(/&#39;/g, "'").replace(/&amp;/g, '&');
}
// The markup this code assigns is small and fully under its own control:
// divs, spans, one button and the inline audio svg. Self-closing tags are
// honoured; anything unbalanced would surface as a failing structural check.
var TAG_RE = new RegExp(
  '<!--[\\s\\S]*?-->' +                                  // comment
  '|</([a-zA-Z][\\w-]*)\\s*>' +                          // close
  '|<([a-zA-Z][\\w-]*)((?:\\s+[\\w:.-]+(?:\\s*=\\s*(?:"[^"]*"|\'[^\']*\'|[^\\s"\'>]+))?)*)\\s*(/?)>' +
  '|([^<]+)', 'g');
var ATTR_RE = /([\w:.-]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'>]+)))?/g;
function parseHTML(html) {
  var root = { children: [] }, stack = [root], m;
  TAG_RE.lastIndex = 0;
  while ((m = TAG_RE.exec(html)) !== null) {
    var top = stack[stack.length - 1];
    if (m[5] !== undefined) {                            // text
      if (m[5]) top.children.push(mkText(decodeEntities(m[5])));
    } else if (m[1] !== undefined) {                     // close tag
      if (stack.length > 1) stack.pop();
    } else if (m[2] !== undefined) {                     // open tag
      var el = El(m[2]), am;
      ATTR_RE.lastIndex = 0;
      while ((am = ATTR_RE.exec(m[3] || '')) !== null) {
        var val = am[2] !== undefined ? am[2] : am[3] !== undefined ? am[3]
                : am[4] !== undefined ? am[4] : '';
        el.attrs[am[1]] = decodeEntities(val);
      }
      top.children.push(el);
      if (!m[4]) stack.push(el);
    }
  }
  return root.children;
}
function serialize(el) {
  return el.children.map(function (ch) {
    if (ch.nodeType === 3) return ch.text;
    var a = Object.keys(ch.attrs).map(function (k) { return ' ' + k + '="' + ch.attrs[k] + '"'; }).join('');
    if (ch.className) a += ' class="' + ch.className + '"';
    return '<' + ch.tag + a + '>' + serialize(ch) + '</' + ch.tag + '>';
  }).join('');
}
var DOCUMENT = { createElement: function (t) { return El(t); } };

function makeDom() {
  var nodes = {};
  return { $: function (id) { return (nodes[id] || (nodes[id] = El('div'))); } };
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
// Section F asks source-level questions ("does this function read c.pair?").
// Those must be questions about CODE: prose in a comment is documentation, and
// rewording documentation must never fail a functional suite. This strips
// comments - quote-aware, since the markup templates contain "/" - so the F1
// checks below see statements only.
function codeOnly(src) {
  var out = '', i = 0, q = null;
  while (i < src.length) {
    var ch = src[i], nx = src[i + 1];
    if (q) {
      if (ch === '\\') { out += src.substr(i, 2); i += 2; continue; }
      if (ch === q) q = null;
      out += ch; i++; continue;
    }
    if (ch === '"' || ch === "'") { q = ch; out += ch; i++; continue; }
    if (ch === '/' && nx === '*') { var e = src.indexOf('*/', i + 2); i = e === -1 ? src.length : e + 2; out += ' '; continue; }
    if (ch === '/' && nx === '/') { var n = src.indexOf('\n', i); i = n === -1 ? src.length : n; out += ' '; continue; }
    out += ch; i++;
  }
  return out;
}
var SRC_VARIANT = bodyOf(INDEX, 'ppVariantParts');
var SRC_USAGE   = bodyOf(INDEX, 'ppAppendUsageTo');
var SRC_START   = bodyOf(INDEX, 'startTypeit');
var SRC_RENDER  = bodyOf(INDEX, 'tRender');
var SRC_REVEAL  = bodyOf(INDEX, 'tRevealLetter');
var SRC_TCHECK  = bodyOf(INDEX, 'tCheckAnswer');
var SRC_DONE    = bodyOf(INDEX, 'tShowDone');
var SRC_RCHECK  = bodyOf(INDEX, 'rCheckAnswer');
var SRC_RRECORD = bodyOf(INDEX, 'rRecord');
// Phase 4F: rCheckAnswer re-asks the Next-button wording after rRecord, because a miss
// on the final original question appends the first retry under a label already on screen.
// It is lifted so the shipping code RUNS; the wording itself is owned by
// tests/test_mixed_round_legibility.js and nothing here asserts about it.
var SRC_RSYNC   = bodyOf(INDEX, 'rSyncNextLabel');

// The functions call each other, so they are compiled into ONE scope with
// their free identifiers supplied as parameters.
var FREE = ['$', 'T', 'R', 'LEVELS', 'poolFor', 'gShuffle', 'show', 'PP_ANSWER', 'PP_TYPED_INDEX',
            'ppHasMainAudio', 'ppMainAudioText', 'ppUsageLabels', 'ppUsageSummary',
            'document', 'G_AUDIO', 'window'];
var COMPILE = Function.apply(null, FREE.concat([
  SRC_VARIANT + '\n' + SRC_USAGE + '\n' + SRC_START + '\n' + SRC_RENDER + '\n' + SRC_REVEAL + '\n' +
  SRC_TCHECK + '\n' + SRC_DONE + '\n' + SRC_RSYNC + '\n' + SRC_RCHECK + '\n' + SRC_RRECORD + '\n' +
  'return { startTypeit:startTypeit, tRender:tRender, tRevealLetter:tRevealLetter,' +
  '         tCheckAnswer:tCheckAnswer, tShowDone:tShowDone, rCheckAnswer:rCheckAnswer,' +
  '         ppVariantParts:ppVariantParts };'
]));

// The real ownership index, built from the real corpus - the same one both
// typed activities are handed in production.
var PP_TYPED_INDEX = A.buildIndex(U.typedPracticeCards(LEVELS));
var G_AUDIO_STUB = '<svg viewBox="0 0 24 24"><path d="M11 5 6 9H2v6h4l5 4V5z"/></svg>';

// ---------- one drivable Type It round ----------
function newRound(cards) {
  var dom = makeDom();
  var T = { topicRef: null, li: 0, ti: 0, qs: [], i: 0, right: 0, almost: 0, hinted: 0,
            revealed: 0, state: 'ask' };
  var R = { qs: [], i: 0, state: 'ask', revealed: 0 };
  var api = COMPILE(
    dom.$, T, R,
    [{ topics: [{ id: 'topic-1', name: 'Topic', src: 'topic-1' }] }],                  /* LEVELS */
    function () { return cards.map(function (c) { return { c: c, topic: 'Topic' }; }); }, /* poolFor */
    function (a) { return a; },                                                        /* gShuffle */
    function () {},                                                                    /* show */
    A, PP_TYPED_INDEX,
    U.hasMainAudio, U.mainAudioText, U.labels, U.summary,   /* the real usage helpers */
    DOCUMENT, G_AUDIO_STUB, {}
  );
  var r = {
    T: T, R: R, dom: dom, api: api,
    card:   function () { return T.qs[T.i].c; },
    type:   function (t) { dom.$('tInput').value = t; return r; },
    check:  function () { api.tCheckAnswer(); return r; },
    reveal: function (n) { for (var i = 0; i < (n || 1); i++) api.tRevealLetter(); return r; },
    next:   function () { T.i++; api.tRender(); return r; },
    answer: function (t) { return r.type(t).check(); },
    verdictNode: function () { return dom.$('tVerdict'); },
    done:   function () {
      return { correct: dom.$('tScoreN').textContent, almost: dom.$('tAlmostN').textContent,
               missed: dom.$('tMissN').textContent, msg: dom.$('tDoneMsg').textContent };
    }
  };
  api.startTypeit(0, 0);
  return r;
}
// Everything a test wants to know about ONE rendered feedback panel.
function feedbackFor(card, answer) {
  var r = newRound([card]);
  r.answer(answer);
  var v = r.verdictNode();
  var altk = v.querySelector('.v-altk'), altv = v.querySelector('.v-altv');
  var pl = v.querySelector('.v-pl'), ex = v.querySelector('.v-ex'), exen = v.querySelector('.v-exen');
  var audio = v.querySelectorAll('.mini-audio');
  return {
    round: r,
    verdictClass: v.className,
    verdict: v.className.indexOf('v-right') !== -1 ? 'right'
           : v.className.indexOf('v-almost') !== -1 ? 'almost' : 'wrong',
    head: (v.querySelector('.v-head') || { textContent: null }).textContent,
    main: pl ? pl.textContent : null,
    mainLang: pl ? pl.getAttribute('lang') : null,
    altCount: v.querySelectorAll('.v-alt').length,
    label: altk ? altk.textContent : null,
    value: altv ? altv.textContent : null,
    valueLang: altv ? altv.getAttribute('lang') : null,
    valueChildElements: altv ? altv.children.filter(function (n) { return n.nodeType === 1; }).length : 0,
    text: textOf(v),
    ex: ex ? ex.textContent : null,
    exEn: exen ? exen.textContent : null,
    audioCount: audio.length,
    audioSay: audio.length ? decodeURIComponent(audio[0].getAttribute('data-say')) : null,
    usageRows: v.querySelectorAll('.usage-row').length,
    warnBoxes: v.querySelectorAll('.warn-box').length
  };
}

// =========================================================================
// 0. FIXTURES - the real cards these tests speak about
// =========================================================================
var ALL = [];
LEVELS.forEach(function (lv) {
  (lv.topics || []).forEach(function (t) {
    (t.cards || []).forEach(function (c) { ALL.push({ c: c, level: lv.level, topic: t.name, kind: t.kind || '', mature: !!t.mature }); });
  });
});
// Recomputed the way poolFor does it, so "Type It-eligible" here means what it
// means in production rather than what this file wishes it meant.
var VOCAB_SRC = LEVELS.filter(function (lv) {
  return lv.topics.length && lv.topics.every(function (t) { return !t.kind; });
});
var TYPEIT_POOL = [];
VOCAB_SRC.forEach(function (lv) {
  lv.topics.forEach(function (t) {
    if (t.mature) return;
    t.cards.forEach(function (c) { if (U.eligibleFor(c, 'typeit')) TYPEIT_POOL.push(c); });
  });
});
function usablePair(c) { return typeof c.pair === 'string' && c.pair.trim() ? c.pair : null; }
function isAspect(c) { return c.relationType === 'aspect-pair'; }
var ASPECT_ALL  = ALL.filter(function (x) { return isAspect(x.c); });
var ASPECT_POOL = TYPEIT_POOL.filter(isAspect);
var byId = {}; ALL.forEach(function (x) { byId[x.c.id] = x.c; });

info('cards in the corpus: ' + ALL.length + '; Type It pool: ' + TYPEIT_POOL.length);
info('aspect-pair cards (whole corpus): ' + ASPECT_ALL.length +
     '; Type It-eligible: ' + ASPECT_POOL.length);
// Reported, never asserted as a magic number: content grows on purpose, and a
// permanent suite must not fail the day a 20th aspect pair is authored.
info('aspect-pair ids: ' + ASPECT_POOL.map(function (c) { return c.id; }).join(', '));
// Aspect-pair metadata is not owned by Type It. It may legitimately appear on
// grammar, conversation, podcast, mature or otherwise recognition-only content
// that this activity never asks the learner to type, and on cards belonging to
// some future activity. Those are REPORTED and then left alone: everything
// below runs against ASPECT_POOL, the eligible subset, so content added
// outside Type It can never fail this suite.
var IN_POOL = {}; ASPECT_POOL.forEach(function (c) { IN_POOL[c.id] = true; });
var ASPECT_OUT = ASPECT_ALL.filter(function (x) { return !IN_POOL[x.c.id]; });
info('aspect-pair cards NOT eligible for Type It: ' + ASPECT_OUT.length +
     (ASPECT_OUT.length ? ' -> ' + ASPECT_OUT.map(function (x) {
        return x.c.id + ' (level=' + x.level + ', topic=' + x.topic +
               (x.kind ? ', kind=' + x.kind : '') + (x.mature ? ', mature' : '') +
               (U.isRecognitionOnly(x.c) ? ', recognition-only' : '') + ')';
      }).join('; ') : ''));
// The data carries `pair` on many more cards than carry the relationType tag.
// Those are NOT touched by this phase - the tag is what gates the new line -
// and section D proves they still show nothing.
var PAIR_UNTAGGED = ALL.filter(function (x) { return x.c.pair && !isAspect(x.c); }).map(function (x) { return x.c; });
info('cards carrying `pair` WITHOUT relationType "aspect-pair": ' + PAIR_UNTAGGED.length +
     ' (untouched by this phase)');

// One diacritic slipped out of the canonical answer: the deterministic "almost".
var FOLD = { '\u0105': 'a', '\u0119': 'e', '\u00f3': 'o', '\u0142': 'l',
             '\u017c': 'z', '\u017a': 'z', '\u0107': 'c', '\u015b': 's', '\u0144': 'n' };
function slipOne(s) {
  return s.replace(/[\u0105\u0119\u00f3\u0142\u017c\u017a\u0107\u015b\u0144]/,
                   function (ch) { return FOLD[ch]; });
}
function wrongFor(c) { return 'zzzq' + (c.id || 'x'); }

// =========================================================================
// A. CORPUS INTEGRITY - the data the new line reads from
// =========================================================================
ok('A1 the data files loaded', !!LEVELS && LEVELS.length > 0);
ok('A1 there is at least one Type It-eligible aspect-pair card', ASPECT_POOL.length > 0);
// NOT asserted: that every aspect-pair card is Type It-eligible. That is an
// observation about today's corpus, not an invariant of this activity - see
// the ASPECT_OUT reporting above.

ASPECT_POOL.forEach(function (c) {
  var tag = 'A2 ' + (c.id || '(no id)');
  ok(tag + ' has a stable id', !!c.id && typeof c.id === 'string');
  ok(tag + ' has a non-empty string pair',
     typeof c.pair === 'string' && c.pair.trim().length > 0);
  ok(tag + ' has at least one acceptedAnswers entry',
     Array.isArray(c.acceptedAnswers) && c.acceptedAnswers.length > 0);
  ok(tag + ' has both sides', !!c.pl && !!c.en);
  eq(tag + ' canonical pl classifies right', A.classify(c.pl, c, PP_TYPED_INDEX), 'right');
  (c.acceptedAnswers || []).forEach(function (a) {
    eq(tag + ' accepted partner "' + a + '" classifies right',
       A.classify(a, c, PP_TYPED_INDEX), 'right');
  });
  // The authored pair is the display order. It is NOT required to be
  // `pl + " / " + partner`: a2-ecology-020 authors "brac / wziac prysznic",
  // sharing the object noun, and rebuilding it would read wrongly.
  ok(tag + ' the pair mentions the canonical answer or its first word',
     c.pair.indexOf(c.pl) !== -1 || c.pair.indexOf(c.pl.split(' ')[0]) !== -1);
});
// stated out loud, because it is the reason the pair may not be rebuilt
ASPECT_POOL.filter(function (c) { return c.pair.indexOf(c.pl) !== 0; }).forEach(function (c) {
  info('authored pair is not "pl + partner": ' + c.id + ' pl="' + c.pl + '" pair="' + c.pair + '"');
});

// =========================================================================
// B. CANONICAL AND PARTNER ANSWERS - both are right, both explain themselves
// =========================================================================
var REP = byId['a2-ecology-001'];
ok('B0 the representative card a2-ecology-001 is in the corpus', !!REP);
if (REP) {
  eq('B0 it is the aspect pair this phase was written for', REP.pl, 'oddawa\u0107');
  eq('B0 its authored pair', REP.pair, 'oddawa\u0107 / odda\u0107');
  eq('B0 its accepted partner', REP.acceptedAnswers, ['odda\u0107']);

  var canon = feedbackFor(REP, REP.pl);
  var partner = feedbackFor(REP, REP.acceptedAnswers[0]);

  eq('B1 typing the canonical form is right', canon.verdict, 'right');
  eq('B1 typing the accepted partner is right', partner.verdict, 'right');
  eq('B1 the canonical answer keeps the "Dobrze!" head', canon.head, 'Dobrze!');
  eq('B1 the partner keeps the "Dobrze!" head', partner.head, 'Dobrze!');

  eq('B2 the canonical answer is labelled "Aspect pair"', canon.label, 'Aspect pair');
  eq('B2 the partner is labelled "Aspect pair"', partner.label, 'Aspect pair');
  eq('B2 the canonical answer shows the whole authored pair', canon.value, REP.pair);
  eq('B2 the partner shows the whole authored pair', partner.value, REP.pair);
  eq('B2 both answers render the SAME pair', canon.value, partner.value);

  eq('B3 the pair value carries lang="pl"', canon.valueLang, 'pl');
  eq('B3 exactly one alternative line is rendered', canon.altCount, 1);
  eq('B3 the pair value appears exactly once in the panel',
     countOf(canon.text, REP.pair), 1);
  eq('B3 the label appears exactly once in the panel',
     countOf(canon.text, 'Aspect pair'), 1);
  eq('B3 the partner panel shows the pair exactly once',
     countOf(partner.text, REP.pair), 1);

  eq('B4 the main answer is still the canonical pl', canon.main, REP.pl);
  eq('B4 the main answer is still the canonical pl after the partner answer',
     partner.main, REP.pl);
  eq('B4 the main answer keeps lang="pl"', canon.mainLang, 'pl');
  ok('B4 "Also accepted" is never shown for an aspect-pair card',
     canon.text.indexOf('Also accepted') === -1 && partner.text.indexOf('Also accepted') === -1);
  ok('B4 the bare partner is not offered as a second alternative line',
     canon.altCount === 1 && canon.value.indexOf(' / ') !== -1);

  eq('B5 the example sentence still renders', canon.ex, REP.ex);
  eq('B5 the example translation still renders', canon.exEn, REP.exEn);
  eq('B5 the audio button still renders once', canon.audioCount, 1);
  eq('B5 the audio button still speaks the card', canon.audioSay, U.mainAudioText(REP));
}

// every real aspect pair, every accepted answer - not just the representative
ASPECT_POOL.forEach(function (c) {
  var answers = [c.pl].concat(c.acceptedAnswers || []);
  answers.forEach(function (a) {
    var f = feedbackFor(c, a);
    var tag = 'B6 ' + c.id + ' typed "' + a + '"';
    eq(tag + ' is right', f.verdict, 'right');
    eq(tag + ' is labelled "Aspect pair"', f.label, 'Aspect pair');
    eq(tag + ' shows the authored pair', f.value, c.pair);
    eq(tag + ' shows exactly one alternative line', f.altCount, 1);
    eq(tag + ' shows the pair exactly once', countOf(f.text, c.pair), 1);
    eq(tag + ' still shows the canonical answer', f.main, c.pl);
    ok(tag + ' never says "Also accepted"', f.text.indexOf('Also accepted') === -1);
    eq(tag + ' keeps its example', f.ex, c.ex || null);
    eq(tag + ' keeps its audio button', f.audioCount, U.hasMainAudio(c) ? 1 : 0);
  });
});

// =========================================================================
// C. THE OTHER VERDICTS - the pair explains a miss too, and changes no total
// =========================================================================
ASPECT_POOL.forEach(function (c) {
  var slip = slipOne(c.pl);
  var tag = 'C1 ' + c.id;
  // fixture sanity first: if the data ever stops producing an "almost" here,
  // this fails loudly instead of the feature test passing for the wrong reason
  ok(tag + ' the diacritic slip "' + slip + '" is a real almost',
     slip !== c.pl && A.classify(slip, c, PP_TYPED_INDEX) === 'almost');
  var f = feedbackFor(c, slip);
  eq(tag + ' an almost answer still reports almost', f.verdict, 'almost');
  eq(tag + ' an almost answer still shows the pair', f.value, c.pair);
  eq(tag + ' an almost answer is labelled "Aspect pair"', f.label, 'Aspect pair');
  eq(tag + ' an almost answer shows the pair exactly once', countOf(f.text, c.pair), 1);
  ok(tag + ' an almost answer keeps its own head', f.head.indexOf('Almost') === 0);

  var w = feedbackFor(c, wrongFor(c));
  eq(tag + ' a wrong answer still reports wrong', w.verdict, 'wrong');
  eq(tag + ' a wrong answer still shows the pair', w.value, c.pair);
  eq(tag + ' a wrong answer is labelled "Aspect pair"', w.label, 'Aspect pair');
  eq(tag + ' a wrong answer shows the pair exactly once', countOf(w.text, c.pair), 1);
  eq(tag + ' a wrong answer keeps its own head', w.head, 'Not this time');
});

// A whole round of aspect-pair cards: the three tiles must equal what
// PP_ANSWER says about the same answers, so the new line moved no total.
(function () {
  var cards = ASPECT_POOL.slice(0, 5);
  ok('C2 there are enough aspect pairs for a round', cards.length === 5);
  var r = newRound(cards);
  var plan = [], expect = { right: 0, almost: 0, wrong: 0 };
  for (var i = 0; i < cards.length; i++) {
    var c = r.card();
    var a = i === 0 ? c.pl
          : i === 1 ? (c.acceptedAnswers || [c.pl])[0]
          : i === 2 ? slipOne(c.pl)
          : wrongFor(c);
    plan.push(a);
    expect[A.classify(a, c, PP_TYPED_INDEX)]++;
    r.answer(a).next();
  }
  var d = r.done();
  eq('C2 the right tile matches PP_ANSWER', d.correct, String(expect.right));
  eq('C2 the almost tile matches PP_ANSWER', d.almost, String(expect.almost));
  eq('C2 the missed tile matches PP_ANSWER', d.missed, String(expect.wrong));
  eq('C2 the three tiles still sum to the round length',
     Number(d.correct) + Number(d.almost) + Number(d.missed), cards.length);
  eq('C2 no hint was used, so none is reported', r.T.hinted, 0);
  ok('C2 the summary sentence is unchanged in shape',
     d.msg.indexOf('You typed ' + expect.right + ' of ' + cards.length + ' exactly right.') === 0);
})();

// hint reporting is untouched by the new line
(function () {
  var c = ASPECT_POOL[0];
  var r = newRound([c]);
  r.reveal(2).answer(c.pl);
  var v = r.verdictNode();
  eq('C3 a hinted aspect-pair answer is still right', r.T.right, 1);
  eq('C3 a hinted aspect-pair answer still counts one hinted question', r.T.hinted, 1);
  eq('C3 a hinted aspect-pair answer still shows the pair',
     (v.querySelector('.v-altv') || { textContent: null }).textContent, c.pair);
})();

// =========================================================================
// D. THE OTHER FEEDBACK TYPES - none of them moved
// =========================================================================
(function () {
  var gv = byId['a1-about-me-017'];
  ok('D1 the gender-variant fixture exists', !!gv);
  if (!gv) return;
  eq('D1 it is a gender-variant card', gv.relationType, 'gender-variant');
  var f = feedbackFor(gv, gv.pl);
  eq('D1 a gender-variant card keeps the "Forms" label', f.label, 'Forms');
  eq('D1 a gender-variant card keeps its variant value', f.value, 'm: m\u00f3j \u00b7 f: moja');
  ok('D1 a gender-variant card is never labelled "Aspect pair"',
     f.text.indexOf('Aspect pair') === -1);
  eq('D1 it still shows exactly one alternative line', f.altCount, 1);
  // typing the other gender is still right, and still explained the same way
  var alt = feedbackFor(gv, gv.acceptedAnswers[0]);
  eq('D1 typing the feminine form is still right', alt.verdict, 'right');
  eq('D1 typing the feminine form still shows "Forms"', alt.label, 'Forms');
})();

(function () {
  var ab = byId['a2-quantities-money-003'];
  ok('D2 the abbreviation fixture exists', !!ab);
  if (!ab) return;
  ok('D2 it has acceptedAnswers and no variants and no pair',
     Array.isArray(ab.acceptedAnswers) && ab.acceptedAnswers.length &&
     !(ab.variants && ab.variants.length) && !ab.pair);
  var f = feedbackFor(ab, ab.pl);
  eq('D2 an ordinary acceptedAnswers card keeps "Also accepted"', f.label, 'Also accepted');
  eq('D2 it keeps its joined value', f.value, ab.acceptedAnswers.join(' \u00b7 '));
  ok('D2 it is never labelled "Aspect pair"', f.text.indexOf('Aspect pair') === -1);
  eq('D2 it shows exactly one alternative line', f.altCount, 1);
})();

(function () {
  var plain = TYPEIT_POOL.filter(function (c) {
    return !(c.acceptedAnswers && c.acceptedAnswers.length) &&
           !(c.variants && c.variants.length) && !c.pair;
  })[0];
  ok('D3 a card with no alternatives exists', !!plain);
  if (!plain) return;
  var f = feedbackFor(plain, plain.pl);
  eq('D3 a card with no alternatives renders no alternative line', f.altCount, 0);
  eq('D3 it has no label', f.label, null);
  ok('D3 it says neither "Aspect pair" nor "Also accepted"',
     f.text.indexOf('Aspect pair') === -1 && f.text.indexOf('Also accepted') === -1);
  eq('D3 it still shows the canonical answer', f.main, plain.pl);
})();

// the sweep: across the WHOLE Type It pool the label is "Aspect pair" exactly
// when the card is tagged aspect-pair and carries a usable pair - so no
// ordinary card, and none of the many `pair`-carrying untagged cards, is
// relabelled by this change
(function () {
  var mislabelled = [], missing = [], gained = [];
  TYPEIT_POOL.forEach(function (c) {
    var f = feedbackFor(c, c.pl);
    var want = isAspect(c) && usablePair(c);
    if (want && f.label !== 'Aspect pair') missing.push(c.id);
    if (!want && f.label === 'Aspect pair') mislabelled.push(c.id);
    if (!want && f.text.indexOf('Aspect pair') !== -1) gained.push(c.id);
  });
  eq('D4 every aspect-pair card in the pool gets the label', missing, []);
  eq('D4 no other card in the pool gets the label', mislabelled, []);
  eq('D4 no other card mentions "Aspect pair" anywhere in its panel', gained, []);
})();

// the untagged `pair` carriers specifically: still exactly what they were
(function () {
  var changed = [];
  PAIR_UNTAGGED.filter(function (c) { return U.eligibleFor(c, 'typeit'); }).forEach(function (c) {
    var f = feedbackFor(c, c.pl);
    var wantAlt = (c.variants && c.variants.length) ||
                  (Array.isArray(c.acceptedAnswers) && c.acceptedAnswers.length);
    if (!wantAlt && f.altCount !== 0) changed.push(c.id + ' gained a line');
    if (f.label === 'Aspect pair') changed.push(c.id + ' was relabelled');
  });
  eq('D5 cards carrying `pair` without the relationType tag are untouched', changed, []);
})();

// =========================================================================
// E. SAFETY - malformed metadata must not crash or print rubbish
// =========================================================================
var MALFORMED = [
  { name: 'pair missing',        card: { id: 'x1', pl: 'robic', en: 'to do', relationType: 'aspect-pair' } },
  { name: 'pair empty string',   card: { id: 'x2', pl: 'robic', en: 'to do', relationType: 'aspect-pair', pair: '' } },
  { name: 'pair all whitespace', card: { id: 'x3', pl: 'robic', en: 'to do', relationType: 'aspect-pair', pair: '   ' } },
  { name: 'pair null',           card: { id: 'x4', pl: 'robic', en: 'to do', relationType: 'aspect-pair', pair: null } },
  { name: 'pair undefined',      card: { id: 'x5', pl: 'robic', en: 'to do', relationType: 'aspect-pair', pair: undefined } },
  { name: 'pair a number',       card: { id: 'x6', pl: 'robic', en: 'to do', relationType: 'aspect-pair', pair: 42 } },
  { name: 'pair an array',       card: { id: 'x7', pl: 'robic', en: 'to do', relationType: 'aspect-pair', pair: ['a', 'b'] } },
  { name: 'pair an object',      card: { id: 'x8', pl: 'robic', en: 'to do', relationType: 'aspect-pair', pair: {} } },
  { name: 'pair a boolean',      card: { id: 'x9', pl: 'robic', en: 'to do', relationType: 'aspect-pair', pair: true } }
];
MALFORMED.forEach(function (m) {
  var f = null, threw = null;
  try { f = feedbackFor(m.card, m.card.pl); } catch (e) { threw = String(e); }
  ok('E1 ' + m.name + ': does not throw', threw === null);
  if (!f) return;
  eq('E1 ' + m.name + ': renders no alternative line', f.altCount, 0);
  ok('E1 ' + m.name + ': prints no "undefined"', f.text.indexOf('undefined') === -1);
  ok('E1 ' + m.name + ': prints no "null"', f.text.indexOf('null') === -1);
  ok('E1 ' + m.name + ': prints no bare "Aspect pair" label',
     f.text.indexOf('Aspect pair') === -1);
  eq('E1 ' + m.name + ': still shows the canonical answer', f.main, m.card.pl);
  eq('E1 ' + m.name + ': the verdict is still decided normally', f.verdict, 'right');
});

// a malformed aspect-pair card that DOES carry variants falls through to the
// behaviour it had before this line existed
(function () {
  var c = { id: 'x10', pl: 'bylem', en: 'I was', relationType: 'aspect-pair',
            variants: [{ form: 'bylem', label: 'm' }, { form: 'bylam', label: 'f' }] };
  var f = feedbackFor(c, c.pl);
  eq('E2 a pairless aspect-pair card with variants still shows "Forms"', f.label, 'Forms');
  eq('E2 ... with its variant value', f.value, 'm: bylem \u00b7 f: bylam');
})();
// ... and one that carries acceptedAnswers still shows nothing, exactly as before
(function () {
  var c = { id: 'x11', pl: 'robic', en: 'to do', relationType: 'aspect-pair',
            acceptedAnswers: ['zrobic'] };
  var f = feedbackFor(c, c.pl);
  eq('E3 a pairless aspect-pair card with acceptedAnswers still shows no line', f.altCount, 0);
  ok('E3 ... and is not labelled "Also accepted"', f.text.indexOf('Also accepted') === -1);
})();

// the pair reaches the page through textContent, so markup in the data is text
(function () {
  var c = { id: 'x12', pl: 'robic', en: 'to do', relationType: 'aspect-pair',
            pair: 'robic / <b>zrobic</b><img src=x onerror=y>' };
  var f = feedbackFor(c, c.pl);
  eq('E4 markup in `pair` is rendered as text, not parsed', f.value, c.pair);
  eq('E4 the value span has no child elements', f.valueChildElements, 0);
  eq('E4 the panel contains no injected element', f.round.verdictNode().querySelectorAll('b').length, 0);
  eq('E4 ... and no injected image', f.round.verdictNode().querySelectorAll('img').length, 0);
})();

// usage chips and warnings still land on the panel, aspect pair or not
(function () {
  var c = { id: 'x13', pl: 'robic', en: 'to do', relationType: 'aspect-pair',
            pair: 'robic / zrobic', register: 'slang', warning: 'Rude in most company.' };
  var f = feedbackFor(c, c.pl);
  eq('E5 an aspect-pair card still shows its usage row', f.usageRows, U.labels(c).length ? 1 : 0);
  eq('E5 an aspect-pair card still shows its usage warning', f.warnBoxes, 1);
  ok('E5 the warning text is still readable', f.text.indexOf('Rude in most company.') !== -1);
  eq('E5 and it still shows the pair', f.value, c.pair);
})();

// =========================================================================
// F. SCOPE - the Mixed Quiz, and everything else, stayed where it was
// =========================================================================
// (1) source-level: the STATEMENTS of rCheckAnswer, comments stripped, so this
// section answers "what does the Mixed Quiz do?" and never "how is it worded?".
// Deliberately NOT asserted anywhere here: the text of any comment.
var RCHECK_CODE = codeOnly(SRC_RCHECK);
var TCHECK_CODE = codeOnly(SRC_TCHECK);
ok('F1 rCheckAnswer still holds the pre-change variants branch',
   RCHECK_CODE.indexOf('if(vp) alt={ label:vp.k, value:vp.v };') !== -1);
ok('F1 rCheckAnswer still holds the pre-change acceptedAnswers branch',
   RCHECK_CODE.indexOf('else if(c.relationType!=="aspect-pair" && Array.isArray(c.acceptedAnswers) && c.acceptedAnswers.length)') !== -1);
ok('F1 rCheckAnswer never builds the new label',
   RCHECK_CODE.indexOf('label:"Aspect pair"') === -1);
ok('F1 rCheckAnswer never mentions the new binding', RCHECK_CODE.indexOf('apPair') === -1);
ok('F1 rCheckAnswer does not read card.pair at all', RCHECK_CODE.indexOf('c.pair') === -1);
// The stripper itself must work, or every F1 check above passes vacuously.
// It is exercised on ITS OWN fixture, never on the wording of real source:
// pinning a real comment here would reintroduce exactly the brittleness this
// section exists to avoid.
var STRIP_FIXTURE =
  'var a=1; /* prose: c.pair apPair label:"Aspect pair" */ var b="keep /* this */ me";\n' +
  'var d=2; // prose: c.pair apPair label:"Aspect pair"\n' +
  'var e="http://x // y"; var f=\'a /* b */ c\';';
var STRIPPED = codeOnly(STRIP_FIXTURE);
ok('F1 the stripper removes block-comment prose', STRIPPED.indexOf('prose:') === -1);
ok('F1 the stripper removes both comment styles entirely',
   STRIPPED.indexOf('c.pair') === -1 && STRIPPED.indexOf('apPair') === -1 &&
   STRIPPED.indexOf('label:"Aspect pair"') === -1);
ok('F1 the stripper keeps the statements around them',
   STRIPPED.indexOf('var a=1;') !== -1 && STRIPPED.indexOf('var d=2;') !== -1);
ok('F1 the stripper keeps string literals that merely LOOK like comments',
   STRIPPED.indexOf('"keep /* this */ me"') !== -1 &&
   STRIPPED.indexOf('"http://x // y"') !== -1 &&
   STRIPPED.indexOf("'a /* b */ c'") !== -1);
// and it left the real function's statements standing
ok('F1 rCheckAnswer\'s statements survive stripping',
   RCHECK_CODE.indexOf('const verdict=PP_ANSWER.classify(val, c, PP_TYPED_INDEX);') !== -1 &&
   RCHECK_CODE.indexOf('<div class="v-alt">') !== -1);
// and the Type It side really did change, so F1 is not passing vacuously
ok('F2 tCheckAnswer does carry the new label', TCHECK_CODE.indexOf('label:"Aspect pair"') !== -1);
ok('F2 tCheckAnswer does read card.pair', TCHECK_CODE.indexOf('c.pair') !== -1);
ok('F2 tCheckAnswer keeps the variants branch', TCHECK_CODE.indexOf('alt={ label:vp.k, value:vp.v }') !== -1);
ok('F2 tCheckAnswer keeps the acceptedAnswers branch',
   TCHECK_CODE.indexOf('alt={ label:"Also accepted"') !== -1);
ok('F2 the two functions are no longer identical in this region',
   TCHECK_CODE.indexOf('label:"Aspect pair"') !== -1 &&
   RCHECK_CODE.indexOf('label:"Aspect pair"') === -1);

// (2) behavioural: drive the real rCheckAnswer over the real aspect pairs
(function () {
  var changed = [];
  ASPECT_POOL.forEach(function (c) {
    var dom = makeDom();
    var T = { qs: [], i: 0, right: 0, almost: 0, hinted: 0, revealed: 0, state: 'ask' };
    var R = { qs: [{ c: c, fmt: 'typed', options: [], requeued: false, result: null }],
              i: 0, state: 'ask', revealed: 0, right: 0 };
    var api = COMPILE(dom.$, T, R, [], function () { return []; }, function (a) { return a; },
                      function () {}, A, PP_TYPED_INDEX, U.hasMainAudio, U.mainAudioText,
                      U.labels, U.summary, DOCUMENT, G_AUDIO_STUB, {});
    dom.$('rInput').value = c.pl;
    api.rCheckAnswer();
    var v = dom.$('rVerdict');
    if (v.querySelectorAll('.v-alt').length !== 0) changed.push(c.id + ' gained an alt line');
    if (textOf(v).indexOf('Aspect pair') !== -1) changed.push(c.id + ' gained the label');
    if (v.className.indexOf('v-right') === -1) changed.push(c.id + ' changed verdict');
    if (v.querySelector('.v-pl').textContent !== c.pl) changed.push(c.id + ' changed main answer');
  });
  eq('F3 the Mixed Quiz shows no aspect-pair line and no new label', changed, []);
})();
(function () {
  // the Mixed Quiz's other feedback types are also exactly where they were
  var gv = byId['a1-about-me-017'], ab = byId['a2-quantities-money-003'];
  [[gv, 'Forms'], [ab, 'Also accepted']].forEach(function (pair) {
    var c = pair[0];
    if (!c) return;
    var dom = makeDom();
    var T = { qs: [], i: 0, right: 0, almost: 0, hinted: 0, revealed: 0, state: 'ask' };
    var R = { qs: [{ c: c, fmt: 'typed', options: [], requeued: false, result: null }],
              i: 0, state: 'ask', revealed: 0 };
    var api = COMPILE(dom.$, T, R, [], function () { return []; }, function (a) { return a; },
                      function () {}, A, PP_TYPED_INDEX, U.hasMainAudio, U.mainAudioText,
                      U.labels, U.summary, DOCUMENT, G_AUDIO_STUB, {});
    dom.$('rInput').value = c.pl;
    api.rCheckAnswer();
    eq('F4 the Mixed Quiz still labels ' + c.id + ' "' + pair[1] + '"',
       (dom.$('rVerdict').querySelector('.v-altk') || { textContent: null }).textContent, pair[1]);
  });
})();

// (3) the shared comparator was not touched: the verdicts this suite relies on
// are the ones the comparator suites already pin
ok('F5 PP_ANSWER still exposes its documented surface',
   typeof A.normalize === 'function' && typeof A.fold === 'function' &&
   typeof A.accepted === 'function' && typeof A.nearMatch === 'function' &&
   typeof A.classify === 'function' && typeof A.buildIndex === 'function');
ok('F5 accepted() is still pl plus acceptedAnswers, with no "/" splitting',
   REP ? JSON.stringify(A.accepted(REP)) === JSON.stringify([REP.pl].concat(REP.acceptedAnswers))
       : false);
ok('F5 the new line never reaches the comparator: accepted() ignores `pair`',
   REP ? A.accepted(REP).indexOf(REP.pair) === -1 : false);
eq('F5 typing the whole pair string is still not a right answer',
   REP ? A.classify(REP.pair, REP, PP_TYPED_INDEX) : null, 'wrong');

// (4) index.html gained no new runtime file and no new CSS rule for this line
ok('F6 the existing .v-alt styling is still what the line uses',
   INDEX.indexOf('.verdict .v-alt{') !== -1 && INDEX.indexOf('.verdict .v-alt .v-altk{') !== -1);
ok('F6 no new alternative-line class was introduced',
   INDEX.indexOf('v-aspect') === -1 && INDEX.indexOf('.v-pair') === -1);
eq('F6 the alternative-line template is still shared by both activities',
   countOf(INDEX, '<div class="v-alt"><span class="v-altk"></span>: <span class="v-altv" lang="pl"></span></div>'), 2);

// ---------- report ----------
INFO.forEach(function (l) { console.log(l); });
console.log('Type It feedback tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
LOG.forEach(function (l) { console.log('  ' + l); });
if (FAIL > 0) { throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed'); }
