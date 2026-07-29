// Deterministic tests for TYPE IT PROMPT DISAMBIGUATION - the `typeItCue` field.
// Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_typeit_prompts.js
// Exit status is 0 only if every assertion passes (printed at the end).
//
// WHAT THIS FILE IS FOR
// Priority 3 Phase 2C: a few English glosses are shared by two Type It cards
// that want DIFFERENT Polish answers - "expensive" is `drogo` on one card and
// `drogi` on another, "orange" is `pomaranczowy` on one and `pomarancza` on
// another. Shown alone, that prompt is unanswerable: the learner is guessing
// which card they drew, not recalling Polish.
//
// The fix is to make the QUESTION fair, not to make the answers interchangeable.
// An optional `typeItCue` names the sense being asked for, and Type It renders
//     card.en + " - " + card.typeItCue
// (with an em dash). Nothing about ANSWERING changed: PP_ANSWER is untouched, no
// acceptedAnswers entry was added, and typing the sibling card's word is still
// wrong. Section C proves exactly that, because a "clarification" that quietly
// widened the accepted set would be the easy wrong fix.
//
// HOW IT TESTS
// It does not re-implement the prompt. It lifts the REAL tRender (plus the
// startTypeit/tCheckAnswer/tShowDone it shares a scope with, and the Mixed
// Quiz's rRender) out of index.html and runs them against the REAL corpus, the
// REAL PP_ANSWER/PP_USAGE and a small DOM that actually parses assigned markup.
// So "the cue appears exactly once" and "HTML-like text is not markup" are
// claims about rendered nodes, not about a copy of the template.
//
// The ambiguous groups are DISCOVERED, never hard-coded: section A regroups the
// live Type It pool by normalized English every run. The count is REPORTED, not
// asserted - content grows on purpose, and a permanent suite must not fail the
// day a sixth pair is authored. What IS asserted is the invariant: any group
// whose cards demand different Polish must carry distinct cues.
//
// SCOPE - what deliberately is NOT here
// How a verdict is DECIDED belongs to tests/test_answer_validation.js and
// tests/test_answer_collisions.js; how right/almost/missed are COUNTED belongs
// to tests/test_round_scoring.js; hint reporting belongs to
// tests/test_typeit_hints.js; the accepted-alternative line belongs to
// tests/test_typeit_feedback.js. This file owns the PROMPT only, plus the
// guarantee that adding it left all of the above - and every other activity -
// alone. Release identifiers (APP_VERSION, CACHE, AUDIO_CACHE) are not pinned:
// they change on purpose at release time.
ObjC.import('Foundation');

function readFile(path) {
  var s = $.NSString.stringWithContentsOfFileEncodingError(path, $.NSUTF8StringEncoding, null);
  return ObjC.unwrap(s);
}
function fileExists(path) { return $.NSFileManager.defaultManager.fileExistsAtPath(path); }
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

var EMDASH = '\u2014';
var SEP = ' ' + EMDASH + ' ';

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
// The production code assigns a template to innerHTML and then fills spans
// through textContent, so a stub that only recorded strings could not tell
// "shown once" from "shown twice", nor textContent from interpolation.
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
  self.classList = {
    add: function (c) { if (classesOf(self).indexOf(c) === -1) self.className = (self.className + ' ' + c).trim(); },
    remove: function (c) {
      self.className = classesOf(self).filter(function (x) { return x !== c; }).join(' ');
      if (self.attrs['class']) self.attrs['class'] = self.attrs['class'].split(/\s+/)
        .filter(function (x) { return x && x !== c; }).join(' ');
    },
    contains: function (c) { return classesOf(self).indexOf(c) !== -1; }
  };
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
var TAG_RE = new RegExp(
  '<!--[\\s\\S]*?-->' +
  '|</([a-zA-Z][\\w-]*)\\s*>' +
  '|<([a-zA-Z][\\w-]*)((?:\\s+[\\w:.-]+(?:\\s*=\\s*(?:"[^"]*"|\'[^\']*\'|[^\\s"\'>]+))?)*)\\s*(/?)>' +
  '|([^<]+)', 'g');
var ATTR_RE = /([\w:.-]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'>]+)))?/g;
function parseHTML(html) {
  var root = { children: [] }, stack = [root], m;
  TAG_RE.lastIndex = 0;
  while ((m = TAG_RE.exec(html)) !== null) {
    var top = stack[stack.length - 1];
    if (m[5] !== undefined) {
      if (m[5]) top.children.push(mkText(decodeEntities(m[5])));
    } else if (m[1] !== undefined) {
      if (stack.length > 1) stack.pop();
    } else if (m[2] !== undefined) {
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
// Section D asks source-level questions ("does this function read c.typeItCue?").
// Those must be questions about CODE: the explanatory comment beside the new
// line NAMES the field, and rewording documentation must never fail a
// functional suite. This strips comments - quote-aware, since the markup
// templates contain "/" - so section D sees statements only.
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

var FREE = ['$', 'T', 'LEVELS', 'poolFor', 'gShuffle', 'show', 'PP_ANSWER', 'PP_TYPED_INDEX',
            'ppHasMainAudio', 'ppMainAudioText', 'ppUsageLabels', 'ppUsageSummary',
            'document', 'G_AUDIO', 'window'];
var COMPILE = Function.apply(null, FREE.concat([
  SRC_VARIANT + '\n' + SRC_USAGE + '\n' + SRC_START + '\n' + SRC_RENDER + '\n' + SRC_REVEAL + '\n' +
  SRC_TCHECK + '\n' + SRC_DONE + '\n' +
  'return { startTypeit:startTypeit, tRender:tRender, tRevealLetter:tRevealLetter,' +
  '         tCheckAnswer:tCheckAnswer };'
]));

// The Mixed Quiz's typed question, lifted the same way, so "the cue is Type It
// only" is proved by RENDERING the other activity rather than by grepping it.
// syncRoundAudioReadiness joins the free list because rRender calls it: Phase 4C
// gives the Mixed Quiz Play button a readiness state, refreshed once per render. It
// is passed as a no-op here - this file renders the typed question to prove what the
// PROMPT says, and the button's states are owned by tests/test_mixed_audio.js.
// Phase 4F adds three progress helpers that rRender calls; they are lifted with it for
// the same reason - the shipping code has to RUN. What they say is owned by
// tests/test_mixed_round_legibility.js; nothing here asserts about them.
var COMPILE_R = Function.apply(null, ['$', 'R', 'rShowDone', 'gShuffle', 'document',
                                      'syncRoundAudioReadiness'].concat([
  bodyOf(INDEX, 'rSetBlocks') + '\n' +
  bodyOf(INDEX, 'rOriginalTotal') + '\n' + bodyOf(INDEX, 'rPct') + '\n' +
  bodyOf(INDEX, 'rReviewPos') + '\n' + bodyOf(INDEX, 'rSyncNextLabel') + '\n' +
  bodyOf(INDEX, 'rRender') + '\n' +
  'return { rRender:rRender };'
]));

var PP_TYPED_INDEX = A.buildIndex(U.typedPracticeCards(LEVELS));
var G_AUDIO_STUB = '<svg viewBox="0 0 24 24"><path d="M11 5 6 9H2v6h4l5 4V5z"/></svg>';

// ---------- one drivable Type It round ----------
function newRound(cards, topicName) {
  var dom = makeDom();
  var T = { topicRef: null, li: 0, ti: 0, qs: [], i: 0, right: 0, almost: 0, hinted: 0,
            revealed: 0, state: 'ask' };
  var name = topicName || 'Topic';
  var api = COMPILE(
    dom.$, T,
    [{ topics: [{ id: 'topic-1', name: 'Set', src: 'topic-1' }] }],                    /* LEVELS */
    function () { return cards.map(function (c) { return { c: c, topic: name }; }); }, /* poolFor */
    function (a) { return a; },                                                        /* gShuffle */
    function () {},                                                                    /* show */
    A, PP_TYPED_INDEX,
    U.hasMainAudio, U.mainAudioText, U.labels, U.summary,
    DOCUMENT, G_AUDIO_STUB, {}
  );
  var r = {
    T: T, dom: dom, api: api,
    prompt:  function () { return dom.$('tEn').textContent; },
    promptEl:function () { return dom.$('tEn'); },
    ctx:     function () { return dom.$('tCtx').textContent; },
    from:    function () { return dom.$('tFrom').textContent; },
    type:    function (t) { dom.$('tInput').value = t; return r; },
    check:   function () { api.tCheckAnswer(); return r; },
    next:    function () { T.i++; api.tRender(); return r; },
    answer:  function (t) { return r.type(t).check(); },
    verdict: function () {
      var cl = dom.$('tVerdict').className;
      return cl.indexOf('v-right') !== -1 ? 'right'
           : cl.indexOf('v-almost') !== -1 ? 'almost'
           : cl.indexOf('v-wrong') !== -1 ? 'wrong' : null;
    }
  };
  api.startTypeit(0, 0);
  return r;
}
// The prompt a learner actually sees for ONE card.
function promptFor(card, topicName) { return newRound([card], topicName).prompt(); }
// The verdict Type It actually reaches for one typed string on one card.
function verdictFor(card, typed) { return newRound([card]).answer(typed).verdict(); }

// =========================================================================
// 0. THE REAL TYPE IT POOL
// Recomputed exactly the way poolFor does it, so "Type It-eligible" here
// means what it means in production.
// =========================================================================
var ALL = [];
LEVELS.forEach(function (lv) {
  (lv.topics || []).forEach(function (t) {
    (t.cards || []).forEach(function (c) {
      ALL.push({ c: c, level: lv.level, topic: t.name, kind: t.kind || '', mature: !!t.mature });
    });
  });
});
var VOCAB_SRC = LEVELS.filter(function (lv) {
  return lv.topics.length && lv.topics.every(function (t) { return !t.kind; });
});
var POOL = [];
VOCAB_SRC.forEach(function (lv) {
  lv.topics.forEach(function (t) {
    if (t.mature) return;
    t.cards.forEach(function (c) {
      if (U.eligibleFor(c, 'typeit')) POOL.push({ c: c, level: lv.level, topic: t.name });
    });
  });
});
var byId = {}; ALL.forEach(function (x) { byId[x.c.id] = x.c; });
info('cards in the corpus: ' + ALL.length + '; Type It pool: ' + POOL.length);

// =========================================================================
// A. CORPUS DISCOVERY
// The ambiguous groups are found, not remembered.
// =========================================================================
// One consistent normalization of the English prompt: case, accents, and
// punctuation folded away, so "film / movie" and "Film/movie" are one key.
function normEn(s) {
  return String(s == null ? '' : s).toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, ' ').trim();
}
// The card's accepted answers, normalized through the REAL comparison layer,
// so "same answer" means what PP_ANSWER means by it.
function answerSet(c) {
  var seen = {}, out = [];
  A.accepted(c).forEach(function (a) {
    var n = A.normalize(a);
    if (n && !seen[n]) { seen[n] = true; out.push(n); }
  });
  return out.sort();
}
function shares(a, b) { return a.some(function (x) { return b.indexOf(x) !== -1; }); }

var groups = Object.create(null);
POOL.forEach(function (x) { (groups[normEn(x.c.en)] || (groups[normEn(x.c.en)] = [])).push(x); });
var repeated = Object.keys(groups).filter(function (k) { return groups[k].length > 1; }).sort();

// A group is genuinely AMBIGUOUS only when some pair of its cards shares no
// accepted answer at all: then one right answer is the other's wrong answer and
// the bare gloss cannot be answered. A group where every pair shares an answer
// (identical sets, or one card additionally accepting its aspect partner) is a
// harmless repeat - the same typing is right on either card - and per the phase
// brief those must NOT be given a cue.
var SAME = [], AMBIG = [];
repeated.forEach(function (k) {
  var g = groups[k], sets = g.map(function (x) { return answerSet(x.c); }), disjoint = false;
  for (var i = 0; i < sets.length; i++)
    for (var j = i + 1; j < sets.length; j++)
      if (!shares(sets[i], sets[j])) disjoint = true;
  (disjoint ? AMBIG : SAME).push({ key: k, g: g, sets: sets });
});
info('repeated normalized English prompts in the Type It pool: ' + repeated.length +
     ' (same-answer repeats: ' + SAME.length + ', genuinely ambiguous: ' + AMBIG.length + ')');
// REPORTED, never asserted as a magic number: a sixth ambiguous pair may be
// authored on purpose, and this suite must fail only if such a pair is left
// WITHOUT cues - which the invariants below check.
AMBIG.forEach(function (e) {
  info('ambiguous "' + e.g[0].c.en + '": ' + e.g.map(function (x) {
    return x.c.id + ' [' + x.level + ' / ' + x.topic + '] pl=' + x.c.pl +
           ' cue=' + JSON.stringify(x.c.typeItCue === undefined ? null : x.c.typeItCue);
  }).join('  |  '));
});
ok('A1 the pool contains at least one repeated English prompt (discovery works)', repeated.length > 0);
ok('A2 at least one genuinely ambiguous group is found', AMBIG.length > 0);

function cueOf(c) { return c.typeItCue; }
function usableCue(c) { return typeof c.typeItCue === 'string' && c.typeItCue.trim() ? c.typeItCue.trim() : null; }

AMBIG.forEach(function (e) {
  var en = e.g[0].c.en;
  // Every card in an ambiguous group must carry a usable cue: without one, that
  // card's prompt is still unanswerable.
  e.g.forEach(function (x) {
    ok('A3 ambiguous card ' + x.c.id + ' ("' + en + '") has a non-empty string typeItCue',
       typeof cueOf(x.c) === 'string' && cueOf(x.c).trim().length > 0);
  });
  // Distinct cues - two cards labelled the same way are still indistinguishable.
  var cues = e.g.map(function (x) { return usableCue(x.c); });
  var uniq = cues.filter(function (v, i) { return cues.indexOf(v) === i; });
  eq('A4 cues within the "' + en + '" group are distinct', uniq.length, cues.length);
  // The resulting prompts must actually differ on screen.
  var shown = e.g.map(function (x) { return promptFor(x.c, x.topic); });
  var us = shown.filter(function (v, i) { return shown.indexOf(v) === i; });
  eq('A5 rendered prompts in the "' + en + '" group are all different', us.length, shown.length);
  // The cue clarifies the QUESTION. It must not have been smuggled in as a
  // widened answer set: no card may accept a sibling's canonical answer.
  e.g.forEach(function (x, i) {
    e.g.forEach(function (y, j) {
      if (i === j) return;
      var mine = e.sets[i], theirs = A.normalize(y.c.pl);
      ok('A6 ' + x.c.id + ' does not accept sibling ' + y.c.id + "'s answer (" + y.c.pl + ')',
         mine.indexOf(theirs) === -1);
    });
  });
});

// The cue is metadata, not content: the gloss and the Polish it teaches are
// exactly what they were before this phase.
var CONTENT_BASELINE = {
  'a1-numbers-prices-020':   { en: 'expensive', pl: 'drogo' },
  'a2-quantities-money-005': { en: 'expensive', pl: 'drogi' },
  'a1-numbers-prices-021':   { en: 'cheap',     pl: 'tanio' },
  'a2-quantities-money-006': { en: 'cheap',     pl: 'tani' },
  'a1-cafe-014':             { en: 'table',     pl: 'stolik' },
  'a2-apartment-027':        { en: 'table',     pl: 'st\u00f3\u0142' },
  'a1-colours-clothes-011':  { en: 'orange',    pl: 'pomara\u0144czowy' },
  'a1-fruit-vegetables-008': { en: 'orange',    pl: 'pomara\u0144cza' },
  'a2-leisure-culture-014':  { en: 'to invite', pl: 'zaprosi\u0107' },
  'a2-holidays-traditions-019': { en: 'to invite', pl: 'zaprasza\u0107' }
};
Object.keys(CONTENT_BASELINE).forEach(function (id) {
  var c = byId[id], want = CONTENT_BASELINE[id];
  ok('A7 ' + id + ' still exists', !!c);
  if (!c) return;
  eq('A8 ' + id + ' keeps its original en', c.en, want.en);
  eq('A9 ' + id + ' keeps its original pl', c.pl, want.pl);
  // These cards teach one word each and had no acceptedAnswers before the cue;
  // if a future phase adds one it must be a real alternative, never a sibling.
  eq('A10 ' + id + ' accepted set is still just its own canonical pl',
     answerSet(c), [A.normalize(want.pl)]);
});

// Cards NOT in an ambiguous group must not have been given a cue: a cue on an
// unambiguous card is noise on the prompt.
var AMBIG_IDS = {};
AMBIG.forEach(function (e) { e.g.forEach(function (x) { AMBIG_IDS[x.c.id] = true; }); });
var CUED = ALL.filter(function (x) { return x.c.typeItCue !== undefined; });
info('cards carrying typeItCue: ' + CUED.length + ' -> ' +
     CUED.map(function (x) { return x.c.id; }).join(', '));
CUED.forEach(function (x) {
  ok('A11 cued card ' + x.c.id + ' is in a genuinely ambiguous Type It group', !!AMBIG_IDS[x.c.id]);
});
// Same-answer repeats stay bare - the phase brief says so explicitly.
SAME.forEach(function (e) {
  e.g.forEach(function (x) {
    ok('A12 same-answer repeat ' + x.c.id + ' ("' + x.c.en + '") was left without a cue',
       x.c.typeItCue === undefined);
  });
});

// =========================================================================
// B. RENDERING
// =========================================================================
var CUE_CARD = byId['a1-numbers-prices-020'];          /* drogo, cue "adverb: how much it costs" */
var PLAIN = POOL.filter(function (x) { return x.c.typeItCue === undefined; })[0].c;

(function () {
  var r = newRound([CUE_CARD], 'Liczby i ceny');
  eq('B1 a cued card renders en + em dash + cue',
     r.prompt(), CUE_CARD.en + SEP + CUE_CARD.typeItCue);
  eq('B2 the cue appears exactly once in the prompt',
     countOf(r.prompt(), CUE_CARD.typeItCue), 1);
  eq('B3 the gloss appears exactly once in the prompt',
     countOf(r.prompt(), CUE_CARD.en), 1);
  eq('B4 the separator is an em dash, not a hyphen', countOf(r.prompt(), EMDASH), 1);
  ok('B5 the prompt is one text node, so the cue is text and not markup',
     r.promptEl().children.length === 1 && r.promptEl().children[0].nodeType === 3);
  // The cue is part of the visible MAIN prompt; it replaces neither of the
  // supporting lines, which must read exactly as before.
  eq('B6 the example context line is unchanged', r.ctx(), 'Context: ' + CUE_CARD.exEn);
  eq('B7 the "From" topic line is unchanged', r.from(), 'From: Liczby i ceny');
  ok('B8 the cue is not echoed into the context line', r.ctx().indexOf(CUE_CARD.typeItCue) === -1);
  ok('B9 the cue is not echoed into the topic line', r.from().indexOf(CUE_CARD.typeItCue) === -1);
})();

(function () {
  var r = newRound([PLAIN], 'Zwyk\u0142y temat');
  eq('B10 a card with no cue renders card.en exactly', r.prompt(), PLAIN.en);
  eq('B11 an uncued prompt contains no em dash separator', countOf(r.prompt(), SEP), 0);
  eq('B12 an uncued card keeps its context line', r.ctx(), PLAIN.exEn ? 'Context: ' + PLAIN.exEn : '');
  eq('B13 an uncued card keeps its topic line', r.from(), 'From: Zwyk\u0142y temat');
})();

// Every Type It card renders one of exactly two shapes - never "undefined",
// never a dangling dash. This sweeps the whole live pool.
(function () {
  var bad = [];
  POOL.forEach(function (x) {
    var got = promptFor(x.c, x.topic), cue = usableCue(x.c);
    var want = cue ? x.c.en + SEP + cue : x.c.en;
    if (got !== want) bad.push(x.c.id + ': ' + JSON.stringify(got));
  });
  eq('B14 every Type It card renders en, or en + em dash + cue (' + POOL.length + ' cards)',
     bad.slice(0, 5), []);
  var junk = POOL.map(function (x) { return promptFor(x.c, x.topic); })
    .filter(function (s) {
      return /undefined|\[object |\bnull\b/.test(s) || /\u2014\s*$/.test(s) || /\u2014\s\u2014/.test(s);
    });
  eq('B15 no rendered prompt shows undefined, null, [object Object] or a dangling dash', junk.slice(0, 5), []);
})();

// Malformed cue values are ignored - the prompt falls back to the bare gloss.
(function () {
  function synth(cue, mark) {
    var c = { id: 'synthetic-' + mark, pl: 'kot', en: 'cat', ex: 'To jest kot.', exEn: 'This is a cat.' };
    if (cue !== '@absent') c.typeItCue = cue;
    return c;
  }
  var CASES = [
    ['@absent', 'absent'], [null, 'null'], [undefined, 'undefined'], ['', 'empty string'],
    ['   ', 'whitespace only'], ['\t\n ', 'tabs and newlines'], [42, 'a number'], [0, 'zero'],
    [['a'], 'an array'], [[], 'an empty array'], [{ v: 'a' }, 'an object'], [{}, 'an empty object'],
    [true, 'true'], [false, 'false'], [NaN, 'NaN']
  ];
  CASES.forEach(function (pair) {
    var card = synth(pair[0], pair[1]), got = promptFor(card);
    eq('B16 cue = ' + pair[1] + ' is ignored; the prompt is card.en alone', got, 'cat');
    ok('B17 cue = ' + pair[1] + ' prints no placeholder text',
       !/undefined|null|\[object |NaN|true|false|\u2014/.test(got));
  });
})();

// A cue is DATA. If one ever contained markup it must reach the screen as
// literal text, because the prompt is assigned through textContent.
(function () {
  var evil = '<b onclick="x()">bold</b> & <img src=x>';
  var card = { id: 'synthetic-html', pl: 'kot', en: 'cat', exEn: 'This is a cat.', typeItCue: evil };
  var r = newRound([card]);
  eq('B18 an HTML-like cue is rendered verbatim as text', r.prompt(), 'cat' + SEP + evil);
  eq('B19 an HTML-like cue creates no elements', r.promptEl().querySelectorAll('b').length, 0);
  eq('B20 an HTML-like cue creates no img element', r.promptEl().querySelectorAll('img').length, 0);
  ok('B21 the prompt node still holds a single text node',
     r.promptEl().children.length === 1 && r.promptEl().children[0].nodeType === 3);
  // A cue with padding renders without a doubled space or a trailing gap.
  var padded = { id: 'synthetic-pad', pl: 'kot', en: 'cat', typeItCue: '  the fruit  ' };
  eq('B22 a padded cue renders trimmed, with a single separator', promptFor(padded), 'cat' + SEP + 'the fruit');
})();

// =========================================================================
// C. THE FIVE GROUPS THIS PHASE WAS WRITTEN FOR
// The prompt got clearer; the ANSWER rules did not move.
// =========================================================================
var KNOWN = [
  { en: 'expensive', a: 'a1-numbers-prices-020',   b: 'a2-quantities-money-005' },
  { en: 'cheap',     a: 'a1-numbers-prices-021',   b: 'a2-quantities-money-006' },
  { en: 'table',     a: 'a1-cafe-014',             b: 'a2-apartment-027' },
  { en: 'orange',    a: 'a1-colours-clothes-011',  b: 'a1-fruit-vegetables-008' },
  { en: 'to invite', a: 'a2-leisure-culture-014',  b: 'a2-holidays-traditions-019' }
];
KNOWN.forEach(function (k) {
  var A1 = byId[k.a], B1 = byId[k.b];
  ok('C1 "' + k.en + '" pair still present in the corpus', !!A1 && !!B1);
  if (!A1 || !B1) return;
  var pa = promptFor(A1), pb = promptFor(B1);
  ok('C2 "' + k.en + '" prompts are visibly different (' + pa + '  vs  ' + pb + ')', pa !== pb);
  ok('C3 "' + k.en + '" prompt for ' + k.a + ' still starts with the original gloss',
     pa.indexOf(A1.en) === 0);
  ok('C4 "' + k.en + '" prompt for ' + k.b + ' still starts with the original gloss',
     pb.indexOf(B1.en) === 0);
  // The right answer is still right...
  eq('C5 ' + k.a + ': typing "' + A1.pl + '" is right', verdictFor(A1, A1.pl), 'right');
  eq('C6 ' + k.b + ': typing "' + B1.pl + '" is right', verdictFor(B1, B1.pl), 'right');
  // ...and the sibling's word is still WRONG. This is the whole point: the
  // prompt was clarified, the accepted set was not widened.
  eq('C7 ' + k.a + ': typing the sibling answer "' + B1.pl + '" is wrong',
     verdictFor(A1, B1.pl), 'wrong');
  eq('C8 ' + k.b + ': typing the sibling answer "' + A1.pl + '" is wrong',
     verdictFor(B1, A1.pl), 'wrong');
});
// Ordinary diacritic slips on the affected cards are still the "almost" tier -
// the cue changed the question, not the comparison.
[['a2-apartment-027', 'stol'], ['a1-colours-clothes-011', 'pomaranczowy'],
 ['a1-fruit-vegetables-008', 'pomarancza'], ['a2-leisure-culture-014', 'zaprosic'],
 ['a2-holidays-traditions-019', 'zapraszac']].forEach(function (p) {
  eq('C9 ' + p[0] + ': the diacritic-free form "' + p[1] + '" is still almost',
     verdictFor(byId[p[0]], p[1]), 'almost');
});
// Explicit acceptedAnswers across the WHOLE pool still classify as right, so
// nothing about this phase disturbed the alternatives other cards rely on.
(function () {
  var checked = 0, bad = [];
  POOL.forEach(function (x) {
    if (!Array.isArray(x.c.acceptedAnswers)) return;
    x.c.acceptedAnswers.forEach(function (alt) {
      checked++;
      if (verdictFor(x.c, alt) !== 'right') bad.push(x.c.id + ' / ' + alt);
    });
  });
  info('explicit acceptedAnswers checked end-to-end: ' + checked);
  eq('C10 every explicit acceptedAnswers entry in the pool is still right', bad.slice(0, 5), []);
})();

// =========================================================================
// D. SCOPE - Type It is the only reader
// =========================================================================
var CODE = codeOnly(INDEX);
ok('D1 tRender reads typeItCue', codeOnly(SRC_RENDER).indexOf('typeItCue') !== -1);
// Deciding a verdict must not see the field at all.
ok('D2 tCheckAnswer does not read typeItCue', codeOnly(SRC_TCHECK).indexOf('typeItCue') === -1);
ok('D3 tRevealLetter does not read typeItCue', codeOnly(SRC_REVEAL).indexOf('typeItCue') === -1);
['rRender', 'rCheckAnswer', 'rBuildOptions', 'startRound', 'lRender', 'render',
 'gRenderTeach', 'gRenderDrill', 'gRenderChoose', 'gRenderBuild',
 'cRenderThread', 'cRenderNode', 'cRenderOptions', 'speakCardMain', 'ppVariantParts'
].forEach(function (fn) {
  ok('D4 ' + fn + ' does not read typeItCue', codeOnly(bodyOf(INDEX, fn)).indexOf('typeItCue') === -1);
});
// tRender is the ONLY place in the whole app that names the field: every
// reference in index.html is accounted for by tRender's own body.
eq('D5 typeItCue is read only inside tRender',
   countOf(CODE, 'typeItCue'), countOf(codeOnly(SRC_RENDER), 'typeItCue'));
eq('D5b tRender reads the field exactly once', countOf(codeOnly(SRC_RENDER), 'typeItCue'), 1);
// The comparison layer is untouched.
['pp-answer.js', 'pp-usage.js', 'pp-migrate.js', 'sw.js'].forEach(function (f) {
  eq('D6 ' + f + ' never mentions typeItCue', countOf(readFile(ROOT + f), 'typeItCue'), 0);
});
ok('D7 PP_ANSWER still exposes its documented surface',
   ['normalize', 'fold', 'accepted', 'classify', 'buildIndex'].every(function (k) {
     return typeof A[k] === 'function';
   }));

// The Mixed Quiz's typed question is RENDERED and must show the bare gloss.
(function () {
  var dom = makeDom();
  var R = { qs: [{ c: CUE_CARD, fmt: 'type', options: [] }], i: 0, state: 'ask', revealed: 0, attempted: false };
  var api = COMPILE_R(dom.$, R, function () {}, function (a) { return a; }, DOCUMENT, function () {});
  api.rRender();
  eq('D8 Mixed Quiz shows card.en with no cue', dom.$('rEn').textContent, CUE_CARD.en);
  eq('D9 Mixed Quiz prompt contains no em dash separator', countOf(dom.$('rEn').textContent, SEP), 0);
  eq('D10 Mixed Quiz keeps its own context line', dom.$('rCtx').textContent, 'Context: ' + CUE_CARD.exEn);
})();

// Generated pages and the generator are content built from `en`; the cue is a
// runtime prompt aid and must never have leaked into them.
(function () {
  var fm = $.NSFileManager.defaultManager;
  // ObjC.unwrap on the NSArray itself yields nulls here, so each NSString is
  // unwrapped individually.
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
  var leaked = pages.filter(function (f) { return countOf(readFile(ROOT + f), 'typeItCue') > 0; });
  eq('D11 no generated page mentions typeItCue', leaked.slice(0, 5), []);
  // The cue TEXT must not appear either - a page rendering "orange - the fruit"
  // would be this phase leaking into content.
  var cueTexts = CUED.map(function (x) { return x.c.typeItCue; });
  var textLeak = [];
  pages.forEach(function (f) {
    var body = readFile(ROOT + f);
    cueTexts.forEach(function (t) { if (body.indexOf(SEP + t) !== -1) textLeak.push(f + ' / ' + t); });
  });
  eq('D12 no generated page renders a cue as content', textLeak.slice(0, 5), []);
  if (fileExists(ROOT + 'build_pages.py'))
    eq('D13 build_pages.py never reads typeItCue', countOf(readFile(ROOT + 'build_pages.py'), 'typeItCue'), 0);
})();

// The cue never reaches audio: it is a screen label, not something to speak.
(function () {
  var spoken = CUED.filter(function (x) {
    return U.hasMainAudio(x.c) && U.mainAudioText(x.c).indexOf(x.c.typeItCue) !== -1;
  });
  eq('D14 no cue leaks into the spoken main-audio text', spoken.map(function (x) { return x.c.id; }), []);
})();

// =========================================================================
// REPORT
// =========================================================================
INFO.forEach(function (s) { console.log(s); });
console.log('Type It prompt tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
LOG.forEach(function (s) { console.log('  ' + s); });
if (FAIL > 0) { throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed'); }
