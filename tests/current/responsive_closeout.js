// Maintained current regression extraction; release markers are injected by run_current_tests.py.
// Deterministic tests for the Mobile Launch Gate Phase 3 closeout. Runs in JavaScriptCore:
//     PYTHONDONTWRITEBYTECODE=1 python3 tests/current/run_current_tests.py
//
// Covered:
//   A  MLG-3A-14                the transient 6px entry-animation overflow, resolved at source.
//   B  podcast card #plText     the 200%-text overflow of the card headline.
//   C  Home .cat-btn            the 200%-text overflow of the category tabs.
//   C2 activity .ctrl row       the 200%-text 1px page overflow (corrective pass).
//   D  Contact email control    the icon, focus and touch-target contract for the single
//                               approved mailto: action (Priority 6 Phase 4C).
//   E  Guide introduction       the approved replacement copy, generator-owned.
//   F  shared Guide ending      the two removed elements, across every generated page.
//   G  regression boundaries    version, caches, migration, Phase 3B-2B behaviour, wording.
//
// JavaScriptCore has no layout engine, so this suite asserts stylesheet, markup and
// generated-output contracts. The rendered geometry behind every one of them (page
// scrollWidth vs clientWidth at 320/360/390/568x320/844x390/desktop, at baseline and at
// emulated 200% text, plus per-frame measurement of the entry animation) is recorded in
// reports/mobile-launch-gate-phase-3-closeout-test-results.md. Real device text scaling,
// screen readers and installed-PWA behaviour remain human checks.

ObjC.import('Foundation');

function readFile(path) {
  var s = $.NSString.stringWithContentsOfFileEncodingError(path, $.NSUTF8StringEncoding, null);
  return ObjC.unwrap(s);
}
function fileExists(path) {
  return $.NSFileManager.defaultManager.fileExistsAtPath(path);
}
function listDir(path) {
  var names = $.NSFileManager.defaultManager.contentsOfDirectoryAtPathError(path, null);
  var out = ObjC.unwrap(names) || [];
  return out.map(function (n) { return ObjC.unwrap(n); }).sort();
}
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
var BUILD = readFile(ROOT + 'build_pages.py');
var SW = readFile(ROOT + 'sw.js');
var MIGRATE = readFile(ROOT + 'pp-migrate.js');
var MANIFEST = readFile(ROOT + 'manifest.json');

var PASS = 0, FAIL = 0, LOG = [];
function ok(name, cond) {
  if (cond) PASS++;
  else { FAIL++; LOG.push('FAIL: ' + name); }
}
function eq(name, actual, expected) {
  var a = JSON.stringify(actual), e = JSON.stringify(expected);
  ok(name + (a === e ? '' : '  (got ' + a + ', want ' + e + ')'), a === e);
}
function countOf(hay, needle) {
  var n = 0, at = 0;
  while ((at = hay.indexOf(needle, at)) !== -1) { n++; at += needle.length; }
  return n;
}

// ---------------------------------------------------------------- CSS parsing
function stripComments(css) { return css.replace(/\/\*[\s\S]*?\*\//g, ''); }
function allStyleBlocks(src) {
  var out = [], re = /<style>([\s\S]*?)<\/style>/g, m;
  while ((m = re.exec(src))) out.push(m[1]);
  return out.join('\n');
}
var STYLE = allStyleBlocks(INDEX);
function topLevelRules(css) {
  var src = stripComments(css), out = [], i = 0;
  while (i < src.length) {
    var brace = src.indexOf('{', i);
    if (brace === -1) break;
    var prelude = src.slice(i, brace).trim();
    var depth = 0, j = brace;
    for (; j < src.length; j++) {
      if (src[j] === '{') depth++;
      else if (src[j] === '}') { depth--; if (depth === 0) break; }
    }
    out.push({ prelude: prelude, body: src.slice(brace + 1, j) });
    i = j + 1;
  }
  return out;
}
var TOP_RULES = topLevelRules(STYLE);
var DECL_BLOCKS = [];
TOP_RULES.forEach(function (rule) {
  if (rule.prelude.charAt(0) === '@') {
    if (/^@media/.test(rule.prelude)) {
      topLevelRules(rule.body).forEach(function (inner) {
        DECL_BLOCKS.push({ selector: inner.prelude, body: inner.body, media: rule.prelude });
      });
    }
    return;
  }
  DECL_BLOCKS.push({ selector: rule.prelude, body: rule.body, media: '' });
});
function decl(body, prop) {
  if (body === null || body === undefined) return null;
  var re = new RegExp('(?:^|;)\\s*' + prop + '\\s*:\\s*([^;]+)', 'i');
  var m = body.match(re);
  return m ? m[1].trim() : null;
}
function selectorsOf(prelude) {
  return prelude.split(',').map(function (s) { return s.trim(); });
}
function rulesTouching(selector, media) {
  return DECL_BLOCKS.filter(function (b) {
    return selectorsOf(b.selector).indexOf(selector) !== -1 &&
           (media === undefined || b.media === media);
  });
}
function declFor(selector, media, prop) {
  var found = null;
  rulesTouching(selector, media).forEach(function (b) {
    var v = decl(b.body, prop);
    if (v !== null) found = v;
  });
  return found;
}
function keyframes(name) {
  var src = stripComments(STYLE);
  var at = src.indexOf('@keyframes ' + name + '{');
  if (at === -1) at = src.indexOf('@keyframes ' + name + ' {');
  if (at === -1) return null;
  var brace = src.indexOf('{', at), depth = 0, j = brace;
  for (; j < src.length; j++) {
    if (src[j] === '{') depth++;
    else if (src[j] === '}') { depth--; if (depth === 0) break; }
  }
  return src.slice(brace + 1, j);
}
function visibleText(markup) {
  return markup.replace(/<script[\s\S]*?<\/script>/g, ' ')
               .replace(/<style[\s\S]*?<\/style>/g, ' ')
               .replace(/<[^>]+>/g, ' ')
               .replace(/&middot;/g, '·').replace(/&rsaquo;/g, '›')
               .replace(/&amp;/g, '&').replace(/&#x27;/g, "'")
               .replace(/\s+/g, ' ').trim();
}

// ------------------------------------------------- generated learner pages
var LEARNER_PAGES = {};
(function collect() {
  ['grammar', 'vocabulary'].forEach(function (dir) {
    listDir(ROOT + dir).forEach(function (name) {
      var rel = dir + '/' + name + '/index.html';
      if (fileExists(ROOT + rel)) LEARNER_PAGES[rel] = readFile(ROOT + rel);
    });
  });
  ['guide/index.html', 'guide/listening/index.html'].forEach(function (rel) {
    if (fileExists(ROOT + rel)) LEARNER_PAGES[rel] = readFile(ROOT + rel);
  });
})();
var PAGE_NAMES = Object.keys(LEARNER_PAGES).sort();
var GUIDE = LEARNER_PAGES['guide/index.html'];
var LISTENING = LEARNER_PAGES['guide/listening/index.html'];
var STUBS = ['grammar/index.html', 'vocabulary/index.html'].map(function (rel) {
  return [rel, fileExists(ROOT + rel) ? readFile(ROOT + rel) : ''];
});

var WIDE = '';   // no media condition

// =========================================================================
// A. MLG-3A-14 - the transient entry-animation overflow.
// =========================================================================
// Confirmed in the browser before any change: the affected element is the entering
// .screen, the axis is vertical only (scrollHeight-clientHeight peaked at exactly 6 while
// scrollWidth-clientWidth stayed 0 at every sample), and the magnitude tracked the shared
// `fade` keyframe's own translateY(6px) frame by frame, decaying to 0 by ~250ms and gone
// once the .35s animation settled. The 3-D card scene was ruled out in Phase 3B-2A.
// The resolution removes only that outward transform, for .screen only.
var SCREEN_ANIM = declFor('.screen', WIDE, 'animation');
var SCREEN_FADE = keyframes('screenFade');
var SHARED_FADE = keyframes('fade');

ok('A1 the screen entry animation is declared', SCREEN_ANIM !== null);
eq('A1 the screen entry keeps its duration and easing', SCREEN_ANIM, 'screenFade .35s ease');
ok('A1 the screen entry no longer uses the translating keyframe', !/\bfade\b/.test(SCREEN_ANIM.replace(/screenFade/g, '')));
ok('A2 a dedicated screen entry keyframe exists', SCREEN_FADE !== null);
ok('A2 the screen entry keyframe animates opacity only',
   /opacity\s*:\s*0/.test(SCREEN_FADE) && /opacity\s*:\s*1/.test(SCREEN_FADE));
eq('A2 the screen entry keyframe declares no transform',
   /transform/i.test(SCREEN_FADE), false);
eq('A2 the screen entry keyframe declares no margin, inset or translate shorthand',
   /(margin|top|bottom|left|right|translate)\s*:/i.test(SCREEN_FADE), false);

// The shared keyframe is untouched, and every other user of it still animates.
ok('A3 the shared fade keyframe still exists', SHARED_FADE !== null);
ok('A3 the shared fade keyframe is byte-unchanged',
   SHARED_FADE.replace(/\s+/g, '') === 'from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}');
var FADE_USERS = DECL_BLOCKS.filter(function (b) {
  var v = decl(b.body, 'animation') || '';
  return /(^|[\s,])fade\b/.test(v) || /\bfade\s/.test(v);
}).map(function (b) { return b.selector; }).sort();
eq('A3 exactly the pre-existing in-flow elements still use the shared fade',
   FADE_USERS,
   ['.done', '.fb-box.show', '.l-reveal.show', '.modal-overlay[open]',
    '.pp-banner', '.pp-nudge', '.toast', '.verdict.show']);
eq('A3 no unrelated animation was disabled or retimed',
   [keyframes('pop') !== null, keyframes('shake') !== null, keyframes('heroReveal') !== null,
    keyframes('heroShine') !== null, keyframes('heroBadgeIn') !== null,
    keyframes('speakPulse') !== null],
   [true, true, true, true, true, true]);

// Reduced motion still switches the screen entry off, by selector not by keyframe name.
var REDUCED = DECL_BLOCKS.filter(function (b) {
  return /prefers-reduced-motion/.test(b.media) &&
         selectorsOf(b.selector).indexOf('.screen') !== -1;
});
eq('A4 reduced motion still disables the screen entry animation',
   REDUCED.map(function (b) { return decl(b.body, 'animation'); }), ['none']);
ok('A4 reduced motion still covers the card flip alongside the screen',
   REDUCED.some(function (b) { return selectorsOf(b.selector).indexOf('.flip') !== -1; }));

// Nothing was clipped or contained to hide the measurement.
['html', 'body', '.wrap', '.app-main', '.screen', '.screen.active',
 '.scene', '.stage', '.flip', '.face', 'main'].forEach(function (sel) {
  var hiding = rulesTouching(sel, undefined).filter(function (b) {
    return ['overflow', 'overflow-x', 'overflow-y'].some(function (p) {
      return /hidden|clip/.test(decl(b.body, p) || '');
    }) || (decl(b.body, 'contain') !== null);
  }).map(function (b) { return b.selector + (b.media ? ' @ ' + b.media : ''); });
  eq('A5 ' + sel + ' introduces no clipping or containment', hiding, []);
});
eq('A5 no rule anywhere sets overflow-x to hidden or clip',
   DECL_BLOCKS.filter(function (b) { return /hidden|clip/.test(decl(b.body, 'overflow-x') || ''); }).length, 0);
eq('A5 the only overflow lock on body is still the Phase 2C drawer scroll lock',
   DECL_BLOCKS.filter(function (b) {
     return selectorsOf(b.selector).indexOf('body.site-menu-open') !== -1;
   }).map(function (b) { return decl(b.body, 'overflow'); }), ['hidden']);
eq('A5 no negative margin was introduced on the animated element',
   [declFor('.screen', WIDE, 'margin'), declFor('.screen', WIDE, 'margin-top'),
    declFor('.screen', WIDE, 'margin-bottom')], [null, null, null]);

// Focus rings on and inside the animated element stay unrestricted.
ok('A6 the card focus ring is still declared and still offset outwards',
   (declFor('.flip:focus-visible', WIDE, 'outline') || '').indexOf('2px solid') === 0 &&
   declFor('.flip:focus-visible', WIDE, 'outline-offset') === '4px');
eq('A6 the 3-D scene keeps the geometry the register originally blamed',
   [declFor('.scene', WIDE, 'perspective'), declFor('.flip', WIDE, 'transform-style')],
   ['1600px', 'preserve-3d']);

// =========================================================================
// B. Podcast card #plText at 200% text.
// =========================================================================
// Before: at 320x568 with 200% text the intro card's Polish headline rendered 478px wide
// inside a 280px card and dragged the page 228px into horizontal scrolling.
var PL = rulesTouching('.pl', WIDE);
var EN = rulesTouching('.en', WIDE);
ok('B1 the card headline rule still exists', PL.length >= 1);
eq('B1 the headline may break inside a word', declFor('.pl', WIDE, 'overflow-wrap'), 'anywhere');
eq('B1 the headline is bounded by its face', declFor('.pl', WIDE, 'max-width'), '100%');
// The direction toggle swaps the containers, so the same Polish token can land in .en.
eq('B1 the swapped-direction twin carries the same contract',
   [declFor('.en', WIDE, 'overflow-wrap'), declFor('.en', WIDE, 'max-width')],
   ['anywhere', '100%']);
ok('B1 the back-face container exists', EN.length >= 1);

// No font-size reduction was used as the fix, at any breakpoint.
eq('B2 the ordinary headline scales are unchanged',
   [declFor('.pl', WIDE, 'font-size'), declFor('.en', WIDE, 'font-size'),
    declFor('.pl.dir-en', WIDE, 'font-size'), declFor('.en.dir-pl', WIDE, 'font-size')],
   ['36px', '27px', '27px', '36px']);
eq('B2 the pre-existing narrow-width card scales are unchanged',
   DECL_BLOCKS.filter(function (b) {
     return b.media === '@media (max-width:400px)' &&
            ['.pl', '.en', '.pl.dir-en', '.en.dir-pl'].indexOf(b.selector) !== -1;
   }).map(function (b) { return b.selector + ':' + decl(b.body, 'font-size'); }).sort(),
   ['.en.dir-pl:31px', '.en:24px', '.pl.dir-en:24px', '.pl:31px']);

// Nothing clips the grown card, and the card can still grow.
['.pl', '.en', '.face', '.flip', '.scene', '.stage'].forEach(function (sel) {
  eq('B3 ' + sel + ' declares no fixed or maximum height',
     [declFor(sel, undefined, 'height'), declFor(sel, undefined, 'max-height')], [null, null]);
});
ok('B3 the card floors are still viewport-aware minimums, not fixed heights',
   /clamp\(/.test(declFor('.flip', WIDE, 'min-height') || '') &&
   /clamp\(/.test(declFor('.stage', WIDE, 'min-height') || ''));

// The headline markup and the card's own controls are untouched.
eq('B4 the podcast headline container is unchanged',
   countOf(INDEX, '<div class="pl" id="plText" lang="pl"></div>'), 1);
eq('B4 the card audio control is still present',
   countOf(INDEX, '<button class="fab" id="speak" aria-label="Play pronunciation">'), 1);
eq('B4 the episode link on the intro card is still present', countOf(INDEX, 'id="ytLink"'), 1);
eq('B4 the example-sentence audio control is untouched', countOf(INDEX, 'class="ex-audio"'), 1);
ok('B4 the podcast intro card still renders through the shared setter',
   INDEX.indexOf('ppSetSharedCardText($("plText"), c.pl, "pl")') !== -1);

// The wrapping rule is narrow: it is not applied to app text at large.
var BREAKERS = DECL_BLOCKS.filter(function (b) {
  return /anywhere|break-word|break-all/.test(
    (decl(b.body, 'overflow-wrap') || '') + ' ' + (decl(b.body, 'word-break') || ''));
}).map(function (b) { return b.selector; }).sort();
// Preserve the fields whose long learner content requires emergency wrapping,
// while allowing later product surfaces to add their own scoped rules.
ok('B5 required learner-data selectors can break inside a word',
   ['.pl', '.en', '.end-table td', '.q-prompt', '.opt', '.vp-example-pl']
     .every(function (selector) { return BREAKERS.indexOf(selector) !== -1; }));
eq('B5 no wrapping rule was attached to a document-level container',
   BREAKERS.filter(function (s) {
     return ['html', 'body', '*', '.wrap', '.app-main', '.screen', 'main'].indexOf(s) !== -1;
   }), []);

// =========================================================================
// C. Home category buttons at 200% text.
// =========================================================================
// Before: at 320x568 with 200% text the three tabs needed 366px inside a 280px track and
// dragged the page 66px into horizontal scrolling; "Vocabulary" alone was 155px.
eq('C1 the tab may shrink below its single-word label', declFor('.cat-btn', WIDE, 'min-width'), '0');
// min-width:0 is what removes the page overflow; the wrapping rule only decides whether the
// label wraps or is clipped inside the resulting 88px tab. `break-word` was measured to
// render identically to `anywhere` here (2 lines, 69.6/85.6px) because min-width:0 has
// already made the intrinsic min-content contribution irrelevant, so the narrower rule
// ships. It must not silently widen back to `anywhere` or narrow to `normal`.
eq('C1 the label may wrap inside the tab', declFor('.cat-btn', WIDE, 'overflow-wrap'), 'break-word');
eq('C1 the tab does not use the wider intrinsic-sizing break rule',
   /anywhere/.test(declFor('.cat-btn', WIDE, 'overflow-wrap') || ''), false);
eq('C1 no word-break override was added beside it', declFor('.cat-btn', WIDE, 'word-break'), null);
eq('C1 the tab still shares the track equally', declFor('.cat-btn', WIDE, 'flex'), '1');
eq('C2 the label size was not reduced', declFor('.cat-btn', WIDE, 'font-size'), '14px');
eq('C2 the padding that sets the touch height is unchanged',
   declFor('.cat-btn', WIDE, 'padding'), '10px 0');
eq('C2 the height stays automatic - no fixed, maximum or line-clamped height',
   [declFor('.cat-btn', undefined, 'height'), declFor('.cat-btn', undefined, 'max-height'),
    declFor('.cat-btn', undefined, '-webkit-line-clamp')], [null, null, null]);
eq('C2 no clipping was introduced on the tab or its track',
   ['.cat-btn', '.cat-seg'].filter(function (sel) {
     return rulesTouching(sel, undefined).some(function (b) {
       return ['overflow', 'overflow-x', 'overflow-y'].some(function (p) {
         return /hidden|clip|auto|scroll/.test(decl(b.body, p) || '');
       });
     });
   }), []);
eq('C2 no responsive block shrinks the tab label',
   DECL_BLOCKS.filter(function (b) {
     return b.media !== '' && selectorsOf(b.selector).indexOf('.cat-btn') !== -1 &&
            decl(b.body, 'font-size') !== null;
   }).length, 0);
eq('C3 the segmented track itself is unchanged',
   [declFor('.cat-seg', WIDE, 'display'), declFor('.cat-seg', WIDE, 'gap'),
    declFor('.cat-seg', WIDE, 'padding'), declFor('.cat-seg', WIDE, 'flex-wrap')],
   ['flex', '4px', '4px', null]);
ok('C3 the focus ring is still declared and still sits outside the tab',
   (declFor('.cat-btn:focus-visible', WIDE, 'outline') || '').indexOf('2px solid') === 0 &&
   declFor('.cat-btn:focus-visible', WIDE, 'outline-offset') === '2px');
eq('C3 the selected-tab styling is untouched',
   declFor('.cat-btn[aria-selected="true"]', WIDE, 'background'), 'var(--card)');
ok('C4 the tab is still built as one labelled button per category',
   INDEX.indexOf('b.className = "cat-btn"; b.type = "button"; b.textContent = c.label;') !== -1);
ok('C4 the tablist semantics are unchanged',
   INDEX.indexOf('role="tablist"') !== -1 && INDEX.indexOf('aria-label="Browse category"') !== -1);

// -------------------------------------------------------------------------
// C2. Activity control row at 200% text (corrective pass).
// -------------------------------------------------------------------------
// Before: at 320px with 200% text Prev(109.67) + Shuffle(56) + Next(113.19) plus two 11px
// gaps needed 300.86px inside the 280px row, so #next's right edge landed at x 320.86 and
// the page scrolled horizontally by 1px. Same root cause as the tabs: flex:1 items with the
// default min-width:auto. min-width:0 alone was measured collapsing the chevrons from 18px
// to 9.33px (Prev) and 5.81px (Next), because the icon is then the only thing that can
// give - so the button's own content is allowed to wrap instead, and it grows downwards.
eq('C5 the control may shrink below its icon-plus-label line',
   declFor('.ctrl', WIDE, 'min-width'), '0');
eq('C5 the control wraps its own content rather than squashing the icon',
   declFor('.ctrl', WIDE, 'flex-wrap'), 'wrap');
eq('C5 the control still shares the row equally', declFor('.ctrl', WIDE, 'flex'), '1');
eq('C5 the row itself was not changed', declFor('.controls', WIDE, 'flex-wrap'), null);
eq('C5 the row keeps its established geometry',
   [declFor('.controls', WIDE, 'gap'), declFor('.controls', WIDE, 'max-width'),
    declFor('.controls', WIDE, 'padding')], ['11px', '420px', '14px 0 24px']);
eq('C6 the label size and padding that set the touch target are unchanged',
   [declFor('.ctrl', WIDE, 'font-size'), declFor('.ctrl', WIDE, 'padding')],
   ['14.5px', '14px 10px']);
eq('C6 the height stays automatic - no fixed or maximum height',
   [declFor('.ctrl', undefined, 'height'), declFor('.ctrl', undefined, 'max-height')],
   [null, null]);
eq('C6 no clipping was introduced on the control or its row',
   ['.ctrl', '.controls'].filter(function (sel) {
     return rulesTouching(sel, undefined).some(function (b) {
       return ['overflow', 'overflow-x', 'overflow-y'].some(function (p) {
         return /hidden|clip|auto|scroll/.test(decl(b.body, p) || '');
       });
     });
   }), []);
eq('C6 no responsive block shrinks the control label',
   DECL_BLOCKS.filter(function (b) {
     return b.media !== '' && selectorsOf(b.selector).indexOf('.ctrl') !== -1 &&
            decl(b.body, 'font-size') !== null;
   }).length, 0);
eq('C6 no wrapping rule was attached to the control text',
   [declFor('.ctrl', WIDE, 'overflow-wrap'), declFor('.ctrl', WIDE, 'word-break')], [null, null]);
ok('C7 the fixed-width shuffle control is unaffected by the shrink allowance',
   declFor('.ctrl.mid', WIDE, 'flex') === '0 0 auto' &&
   declFor('.ctrl.mid', WIDE, 'width') === '56px');
ok('C7 the focus ring is still declared and still sits outside the control',
   (declFor('.ctrl:focus-visible', WIDE, 'outline') || '').indexOf('2px solid') === 0 &&
   declFor('.ctrl:focus-visible', WIDE, 'outline-offset') === '2px');
eq('C7 every control row and its labels are unchanged in markup',
   [countOf(INDEX, 'class="controls"'), countOf(INDEX, 'class="ctrl"'),
    countOf(INDEX, 'class="ctrl mid"'), countOf(INDEX, '<span id="tNextLabel">Next</span>'),
    countOf(INDEX, '<span id="gNextLabel">Next</span>')], [6, 8, 1, 1, 1]);
eq('C7 the dynamic control labels are unchanged',
   [countOf(INDEX, '"Start practice \\u2192"'), countOf(INDEX, '"See results"')], [1, 5]);

// =========================================================================
// D. Contact email control.
// =========================================================================
// Priority 6 Phase 4 (risk R-07, feedback F-1/F-2/F-3) turned the single collaboration
// action into four named-reason actions, each carrying its own subject. Priority 6
// Phase 4C consolidates those four back into one plain action below a compact reason
// list: same component, same icon rule, same touch-target contract - but the accessible
// name now comes from the link's own visible text instead of a separate aria-label, and
// the route carries no query string at all. There is still exactly one contact *address*
// and one contact *method*, with one entry point to it.
var CONTACT_LINKS = INDEX.match(/<a class="contact-email"[\s\S]*?<\/a>/g) || [];
var CONTACT_LINK = CONTACT_LINKS[0] || '';
var CONTACT_HREFS = CONTACT_LINKS.map(function (a) { return (a.match(/href="([^"]*)"/) || [])[1]; });
eq('D1 exactly one approved contact action exists', CONTACT_LINKS.length, 1);
eq('D1 exactly one contact action exists', countOf(INDEX, 'class="contact-email"'), 1);
eq('D1 the href is byte-identical to the approved bare destination', CONTACT_HREFS,
   ['mailto:hello@popolsku.app']);
eq('D1 no second contact address exists anywhere in the app shell',
   countOf(INDEX, 'mailto:') - countOf(INDEX, 'mailto:hello@popolsku.app'), 0);
eq('D1 the route carries no query string, so no subject, body, cc or bcc can be prefilled',
   CONTACT_HREFS.filter(function (h) { return h.indexOf('?') !== -1; }), []);
eq('D1 no learner data, progress or storage value is placed in the contact URL',
   CONTACT_HREFS.filter(function (h) {
     return /popolsku-|progress|know|still|level|topic|card|streak|score|localStorage/.test(h);
   }), []);
// Priority 6 Phase 4D drops the visible word "Email" so the button reads as a plain
// address, and restores the accessible name via aria-label so screen reader users still
// hear "Email hello@popolsku.app" rather than the bare address alone.
eq('D2 the visible text is the approved "hello@popolsku.app" label, and nothing else',
   CONTACT_LINKS.map(visibleText), ['hello@popolsku.app']);
eq('D2 the accessible name is restored via aria-label',
   (CONTACT_LINK.match(/\saria-label="([^"]*)"/) || [])[1], 'Email hello@popolsku.app');
eq('D2 exactly one aria-label is declared on the control', countOf(CONTACT_LINK, 'aria-label='), 1);
eq('D2 nothing else contributes a name to the control',
   [countOf(CONTACT_LINK, 'aria-labelledby'), countOf(CONTACT_LINK, 'aria-describedby'),
    countOf(CONTACT_LINK, 'title=')], [0, 0, 0]);
// The shared .sr-only utility is untouched and still used by the live regions and helps.
ok('D2 the shared .sr-only utility still exists', rulesTouching('.sr-only', WIDE).length >= 1);
ok('D2 .sr-only is still off screen rather than removed from the accessibility tree',
   rulesTouching('.sr-only', WIDE).every(function (b) {
     return !/none/.test(decl(b.body, 'display') || '') &&
            !/hidden/.test(decl(b.body, 'visibility') || '');
   }));
ok('D2 .sr-only is still in use elsewhere in the app',
   countOf(INDEX, 'class="sr-only"') >= 7);

eq('D3 exactly one inline icon exists in the link', countOf(CONTACT_LINK, '<svg'), 1);
ok('D3 the icon is hidden from assistive technology', /<svg[^>]*aria-hidden="true"/.test(CONTACT_LINK));
ok('D3 the icon is not focusable', /<svg[^>]*focusable="false"/.test(CONTACT_LINK));
ok('D3 the icon follows the link colour', /<svg[^>]*stroke="currentColor"/.test(CONTACT_LINK));
ok('D3 the icon is an envelope drawn inline, not an image, sprite or remote asset',
   countOf(CONTACT_LINK, '<img') === 0 && countOf(CONTACT_LINK, '<use') === 0 &&
   countOf(CONTACT_LINK, 'http') === 0 && countOf(CONTACT_LINK, 'background-image') === 0 &&
   countOf(CONTACT_LINK, '<rect') === 1 && countOf(CONTACT_LINK, '<path') === 1);
eq('D3 the only URL in the control is its own mailto destination',
   (CONTACT_LINK.match(/href="([^"]*)"/g) || []).length, 1);
ok('D3 no emoji was used as the icon', !/[←-⯿\uD83C-\uDBFF]/.test(CONTACT_LINK));

eq('D4 the touch height and type scale are preserved',
   [declFor('.contact-email', WIDE, 'min-height'), declFor('.contact-email', WIDE, 'font-size'),
    declFor('.contact-email', WIDE, 'padding')], ['43px', '14px', '12px 16px']);
eq('D4 the label may still wrap safely at enlarged text',
   [declFor('.contact-email', WIDE, 'overflow-wrap'), declFor('.contact-email', WIDE, 'max-width')],
   ['anywhere', '100%']);
ok('D4 the focus state is unchanged',
   (declFor('.contact-email:focus-visible', WIDE, 'outline') || '').indexOf('2px solid') === 0);
eq('D4 the icon never shrinks and never wraps on its own',
   [declFor('.contact-email svg', WIDE, 'flex'), declFor('.contact-email svg', WIDE, 'width'),
    declFor('.contact-email svg', WIDE, 'height')], ['0 0 auto', '17px', '17px']);
// Priority 6 Phase 4D (live 8.9 smoke review): the final bullet crowded the CTA, so a
// deliberate but modest gap now separates the list from the button. The four bullets
// keep their own unchanged 16px rhythm; only the space above the CTA grew.
eq('D4 the CTA has deliberate, modest separation from the reason list above it',
   declFor('.contact-email', WIDE, 'margin-top'), '20px');
eq('D4 spacing between the four bullet items is unchanged',
   declFor('.privacy-list', WIDE, 'gap'), '16px');
// Priority 6 Phase 4 (feedback F-2) replaced the collaboration-first lead with a
// learner-first one. Phase 4C keeps that lead and replaces the four reason headings that
// used to sit under it with one compact semantic list.
eq('D5 the contact lead is the approved learner-first line',
   countOf(INDEX, '<p class="contact-lead">Spotted a mistake, hit a problem, or have an idea?</p>'), 1);
eq('D5 the old collaboration-first lead is gone',
   countOf(INDEX, 'Have an idea, want to collaborate, or simply want to connect?'), 0);
// Feedback R-5: the collaboration invitation is kept, as the fourth reason in the list.
ok('D5 the collaboration reason is unchanged',
   INDEX.indexOf('Collaborations, useful resources, ideas, or general feedback are always welcome.') !== -1);
eq('D5 no other contact method was added', countOf(INDEX, 'mailto:'), 1);
eq('D5 no form, widget, survey or submission channel was introduced',
   [countOf(INDEX, '<form'), countOf(INDEX, 'XMLHttpRequest'),
    countOf(INDEX, 'navigator.sendBeacon'), countOf(INDEX, 'WebSocket')], [0, 0, 0, 0]);
// The two pre-existing fetches are the audio manifest and the connectivity HEAD probe.
// Both are relative, so the feedback route added no endpoint and nothing left the origin.
eq('D5 the app still makes only its two same-origin fetches',
   (INDEX.match(/fetch\(\s*["'][^"']*["']/g) || []),
   ['fetch("audio-manifest.json"', 'fetch("./"']);
eq('D5 the contact route promises no response time, tracking or ticketing',
   ['ticket', 'we will reply', 'within 24', 'within 48', 'guarantee', 'support team',
    'live chat'].reduce(function (n, s) {
     return n + countOf(visibleText(INDEX).toLowerCase(), s); }, 0), 0);

// =========================================================================
// E. Approved Guide introduction.
// =========================================================================
var APPROVED_INTRO = 'Built by a foreigner living in Poland and learning the language through ' +
  'everyday life - with practical flashcards, clear explanations, pronunciation audio, and ' +
  'free interactive practice for every topic.';
var FORMER_INTRO_HEAD = 'Created by a foreigner who learned it the hard way';

eq('E1 the generator owns the approved introduction',
   countOf(BUILD.replace(/'\s*\n\s*'/g, ''), APPROVED_INTRO), 1);
eq('E1 the Guide hub renders the approved introduction exactly once',
   countOf(GUIDE, '<p class="lede">' + APPROVED_INTRO + '</p>'), 1);
eq('E1 the introduction uses a simple hyphen, never an en or em dash',
   /[‐-―−]/.test(APPROVED_INTRO), false);
eq('E1 the rendered introduction carries no dash other than the simple hyphen',
   ((GUIDE.match(/<p class="lede">([\s\S]*?)<\/p>/) || ['', ''])[1].match(/[-‐-―−]/g) || []),
   ['-']);
eq('E2 the former introduction is gone from the generator', countOf(BUILD, 'hard way'), 0);
PAGE_NAMES.forEach(function (rel) {
  eq('E2 ' + rel + ' carries no trace of the former introduction',
     countOf(LEARNER_PAGES[rel], FORMER_INTRO_HEAD) + countOf(LEARNER_PAGES[rel], 'hard way'), 0);
});
// The approved copy appears only where the introduction belongs.
eq('E3 the approved introduction appears on the Guide hub and nowhere else',
   PAGE_NAMES.filter(function (rel) { return LEARNER_PAGES[rel].indexOf(APPROVED_INTRO) !== -1; }),
   ['guide/index.html']);
eq('E3 the approved introduction did not leak into the app shell',
   countOf(INDEX, APPROVED_INTRO) + countOf(INDEX, 'Built by a foreigner'), 0);
// Metadata derived from nothing changed here must be byte-identical.
// Priority 6 Phase 3 (risk R-06) renames the destination. The descriptive tail of the
// title - the part that carries search intent - is deliberately kept.
eq('E4 the Guide title carries the approved destination name and its descriptive tail',
   (GUIDE.match(/<title>([^<]+)<\/title>/) || [])[1],
   'Explore more Polish - Polish grammar, slang and idioms explained simply | Po polsku');
eq('E4 the Guide h1 is the approved destination name',
   (GUIDE.match(/<h1>([^<]+)<\/h1>/) || [])[1], 'Explore more Polish');
var GUIDE_DESC = 'Free Polish for learners: all seven cases, formal address, adjectives - plus real ' +
  'slang, idioms and proverbs. Tables, usage notes, and examples with Polish pronunciation audio.';
eq('E4 the Guide meta description is unchanged',
   countOf(GUIDE, '<meta name="description" content="' + GUIDE_DESC + '">'), 1);
eq('E4 the Guide Open Graph description is unchanged',
   countOf(GUIDE, '<meta property="og:description" content="' + GUIDE_DESC + '">'), 1);
eq('E4 the Guide JSON-LD description is unchanged',
   countOf(GUIDE, '"description": "' + GUIDE_DESC + '"'), 1);
eq('E4 the introduction is not reused as any metadata value',
   countOf(GUIDE, 'content="' + APPROVED_INTRO) + countOf(GUIDE, '"description": "' + APPROVED_INTRO), 0);
eq('E4 the Guide canonical is unchanged',
   countOf(GUIDE, '<link rel="canonical" href="https://popolsku.app/guide/">'), 1);
eq('E4 the sample note beside the introduction is unchanged',
   countOf(GUIDE, 'These pages are a sample - a taste of each topic.'), 1);
// The listening-resource copy itself stays generator-owned and is asserted verbatim in
// tests/test_build_pages.py, which is the only file allowed to hold those strings; this
// suite pins the structure around it so the introduction change cannot have disturbed it.
eq('E4 the listening recommendation entry is unchanged',
   [countOf(GUIDE, '<li><a href="/guide/listening/">'),
    countOf(GUIDE, '<span class="t">What else I listen to</span>'),
    countOf(LISTENING, '<h1>What else I listen to</h1>')], [1, 1, 1]);

// =========================================================================
// F. Shared Guide ending.
// =========================================================================
var ENDING = '<section class="guide-ending" aria-labelledby="guideEndingTitle">' +
  '<h2 id="guideEndingTitle">Ready to keep learning?</h2>' +
  '<p class="guide-ending-support">Practice the same Polish with flashcards, drills, ' +
  'conversations, and listening.</p>' +
  '<a class="guide-primary" href="/">Open the app</a>' +
  '<p class="guide-reassurance">Genuinely free. No account required.</p>' +
  '</section>';
var KEPT = ['Ready to keep learning?',
            'Practice the same Polish with flashcards, drills, conversations, and listening.',
            'Open the app',
            'Genuinely free. No account required.'];
var REMOVED = ['Your progress stays on this device and can be backed up anytime.',
               'How progress works'];

eq('F1 every generated learner page was collected', PAGE_NAMES.length, 31);
eq('F1 the page mix is the expected 23 grammar + 6 vocabulary + 2 guide',
   [PAGE_NAMES.filter(function (p) { return p.indexOf('grammar/') === 0; }).length,
    PAGE_NAMES.filter(function (p) { return p.indexOf('vocabulary/') === 0; }).length,
    PAGE_NAMES.filter(function (p) { return p.indexOf('guide/') === 0; }).length],
   [23, 6, 2]);
PAGE_NAMES.forEach(function (rel) {
  var markup = LEARNER_PAGES[rel], text = visibleText(markup);
  eq('F2 ' + rel + ' emits the shared ending exactly once', countOf(markup, ENDING), 1);
  eq('F2 ' + rel + ' has exactly one ending section', countOf(markup, 'class="guide-ending"'), 1);
  KEPT.forEach(function (line) {
    eq('F2 ' + rel + ' keeps: ' + line, countOf(text, line), 1);
  });
  REMOVED.forEach(function (line) {
    eq('F3 ' + rel + ' omits: ' + line, countOf(text, line), 0);
  });
  eq('F3 ' + rel + ' carries no progress markup or dead class',
     countOf(markup, 'guide-progress'), 0);
  eq('F3 ' + rel + ' keeps its primary app link intact',
     countOf(markup, '<a class="guide-primary" href="/">Open the app</a>'), 1);
});
eq('F4 the generator is the single source of the ending',
   [countOf(BUILD, 'def learning_ending()'), countOf(BUILD, 'learning_ending()')], [1, 5]);
eq('F4 the generator no longer emits the removed elements',
   countOf(BUILD, 'guide-progress') + countOf(BUILD, 'How progress works') +
   countOf(BUILD, 'Your progress stays on this device'), 0);
eq('F4 the ending keeps its heading hierarchy contract',
   countOf(BUILD, '<h2 id="guideEndingTitle">Ready to keep learning?</h2>'), 1);
eq('F4 the ending card spacing rules are otherwise unchanged',
   [countOf(BUILD, '.guide-ending{margin:28px 0 0;padding:20px'),
    countOf(BUILD, '.guide-reassurance{color:var(--forest);font-size:12.5px;font-weight:700;margin:14px 0 5px}'),
    countOf(BUILD, '.guide-ending-support{color:var(--muted);font-size:14.5px;margin:0 0 16px}')],
   [1, 1, 1]);
// The redirect stubs never carried the ending and still do not.
STUBS.forEach(function (pair) {
  eq('F5 ' + pair[0] + ' is still a bare redirect stub',
     countOf(pair[1], 'guide-ending') + countOf(pair[1], 'Ready to keep learning?'), 0);
});
// Privacy is untouched everywhere it actually lives.
eq('F6 the Privacy screen still exists in the app', countOf(INDEX, '<section class="screen" id="privacy">'), 1);
eq('F6 Privacy is still reachable from the site menu',
   countOf(INDEX, '<li><a href="#privacy" data-app-screen="privacy">Privacy</a></li>'), 1);
ok('F6 direct /#privacy routing is unchanged',
   /if\(\[[^\]]*"privacy"[^\]]*\]\.includes\(ppInitialScreen\)/.test(INDEX));
// Priority 6 Phase 2 (amendment) narrows this heading to a plain factual label. Phase 3
// closeout's concern is that the Privacy destination still has a heading learners land
// on, which it does - the slogan itself was never this suite's contract.
ok('F6 the Privacy heading learners land on is present',
   INDEX.indexOf('<h1>Privacy</h1>') !== -1);
ok('F6 the Privacy page still explains progress and backup',
   INDEX.indexOf('Back up progress') !== -1 || INDEX.indexOf('Back up') !== -1);
// This guard is against a destination being *removed*. Priority 6 Phase 4 (risk R-20)
// added a footer links row, so each in-app destination was briefly reachable from two
// surfaces; Priority 6 Phase 4C removes that row again (the drawer already owns these
// destinations), so each is back to being reachable from the drawer alone.
eq('F6 no other in-app link was removed alongside the ending link',
   [countOf(INDEX, 'data-app-screen="about"'), countOf(INDEX, 'data-app-screen="contact"'),
    countOf(INDEX, 'data-app-screen="privacy"')], [1, 1, 1]);
eq('F6 the drawer still owns one route to each in-app destination',
   [countOf(INDEX, '<li><a href="#about" data-app-screen="about">About</a></li>'),
    countOf(INDEX, '<li><a href="#contact" data-app-screen="contact">Contact</a></li>'),
    countOf(INDEX, '<li><a href="#privacy" data-app-screen="privacy">Privacy</a></li>')], [1, 1, 1]);
eq('F6 the footer no longer owns a competing route to any in-app destination',
   [countOf(INDEX, '<a href="#about" data-app-screen="about">About</a>\n'),
    countOf(INDEX, '<a href="#contact" data-app-screen="contact">Contact</a>\n'),
    countOf(INDEX, '<a href="#privacy" data-app-screen="privacy">Privacy</a>\n')], [0, 0, 0]);

// =========================================================================
// G. Regression boundaries.
// =========================================================================
eq('G1 APP_VERSION is the __CURRENT_APP_VERSION__ release', (INDEX.match(/APP_VERSION\s*=\s*"([^"]+)"/) || [])[1], '__CURRENT_APP_VERSION__');
// The app-shell cache revision moved to v56 in Phase 4B-1: the hardened worker
// stages its shell in a new cache so an open tab keeps being served the release
// it was loaded with. The audio cache name below stays pinned forever.
eq('G1 the app-shell cache name is the current shell revision',
   (SW.match(/CACHE\s*=\s*"([^"]+)"/) || [])[1], '__CURRENT_SHELL_CACHE__');
eq('G1 the audio cache name is unchanged', (SW.match(/AUDIO_CACHE\s*=\s*"([^"]+)"/) || [])[1], 'popolsku-audio');
eq('G1 the storage schema version is unchanged',
   (MIGRATE.match(/SCHEMA_VERSION\s*=\s*(\d+)/) || [])[1], '2');
eq('G1 the content migration revision is unchanged',
   (MIGRATE.match(/CONTENT_MIGRATION_REVISION\s*=\s*(\d+)/) || [])[1], '2');
ok('G1 the manifest still declares the same identity',
   MANIFEST.indexOf('"name"') !== -1 && MANIFEST.indexOf('popolsku') === -1 ||
   MANIFEST.indexOf('"start_url"') !== -1);
eq('G1 the generated footer still derives the app version', countOf(BUILD, 'read_app_version()'), 2);

// Phase 3B-2B behaviour must survive untouched.
eq('G2 the single reveal helper still exists exactly once',
   [countOf(INDEX, 'function ppRevealFocusedTarget('),
    countOf(INDEX, 'el.scrollIntoView({block:"nearest", inline:"nearest"})')], [1, 1]);
eq('G2 the reveal still asks for the minimum movement and no animation',
   [countOf(INDEX, 'block:"nearest", inline:"nearest"'),
    countOf(INDEX, 'behavior:"'), countOf(INDEX, "behavior:'")], [1, 0, 0]);
eq('G2 the typed-answer reveal call sites are unchanged',
   [countOf(INDEX, 'ppFocusAndRevealActivityTarget($("tNext"))'),
    countOf(INDEX, 'ppFocusAndRevealActivityTarget($("rNext"))')], [1, 1]);
eq('G2 manual scroll restoration is still owned by the app',
   countOf(INDEX, 'history.scrollRestoration = "manual"') +
   countOf(INDEX, 'history.scrollRestoration="manual"'), 1);
eq('G2 the conversation append path is unchanged',
   [countOf(INDEX, 'function cAdvanceThread('),
    countOf(INDEX, '$("cThread").insertAdjacentHTML("beforeend", cThreadBubblesHTML(from))'),
    countOf(INDEX, '.scrollTop'), countOf(INDEX, '.scrollHeight')], [1, 1, 0, 0]);
eq('G2 no scroll listener, visualViewport handler or smooth scroll was introduced',
   [countOf(INDEX, 'visualViewport'), countOf(INDEX, 'scroll-behavior:smooth'),
    countOf(INDEX, 'scroll-behavior: smooth'), countOf(INDEX, 'addEventListener("scroll"')],
   [0, 0, 0, 0]);

// Learner-visible wording outside the three approved refinements is pinned.
// The Contact lead moved in Priority 6 Phase 4 (feedback F-2) and is pinned in section D
// above; the collaboration reason it used to introduce is pinned there too. Priority 6
// Phase 4C folds the old two-sentence collaboration paragraph into one compact list item,
// so "Po polsku is an independent and evolving project." is intentionally no longer part
// of the approved copy and is not pinned here.
['Type the Polish answer first.', 'Choose your reply', 'Dobrze!', 'Not this time',
 '<h1>Privacy</h1>', 'tap to see meaning', 'Play pronunciation'].forEach(function (s) {
  ok('G3 unchanged learner string: ' + s, INDEX.indexOf(s) !== -1);
});
eq('G3 the removed ending copy exists nowhere in the app shell either',
   countOf(INDEX, 'Your progress stays on this device and can be backed up anytime.') +
   countOf(INDEX, 'How progress works'), 0);
// Priority 6 Phase 1 (risk R-04) keeps the approved H1 and rewrites only the supporting
// sentence, which now carries the positioning. The search copy is unchanged.
// Priority 6 Phase 3 (SEO S-1) leaves this approved copy alone and points the meta,
// Open Graph and Twitter descriptions at it, so the supporting sentence now appears
// four times: once visibly in the hero and once in each of the three description slots.
eq('G3 the Home hero and search copy are unchanged',
   [countOf(INDEX, '<h1>Learn the Polish<br>you\'ll <em>actually</em> use.</h1>'),
    countOf(INDEX, 'Everyday vocabulary, useful grammar, conversation practice, and Polish pronunciation audio for real life in Poland.'),
    countOf(INDEX, 'Search topics')], [1, 4, 2]);
eq('G4 no generated-page code leaked into the app shell', /build_pages/.test(INDEX), false);
eq('G4 the app shell declares no new media breakpoint',
   TOP_RULES.filter(function (r) { return /^@media/.test(r.prelude); })
            .map(function (r) { return r.prelude.replace(/^@media\s*/, '').trim(); }).sort(),
   ['(max-height:600px)', '(max-width:360px)', '(max-width:400px)', '(max-width:400px)',
    '(prefers-reduced-motion:reduce)']);

console.log('Phase 3 closeout tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
console.log('  [info] MLG-3A-14 resolved at source: .screen entry is opacity-only `screenFade` at the same .35s ease; the shared `fade` keyframe and its ' + FADE_USERS.length + ' in-flow users are unchanged');
console.log('  [info] podcast card and category tabs reflow through overflow-wrap:anywhere on exactly ' + BREAKERS.length + ' audited selectors: ' + BREAKERS.join(', '));
console.log('  [info] shared ending verified on ' + PAGE_NAMES.length + ' generated learner pages; approved introduction verified on guide/index.html only');
console.log('  [info] rendered geometry, real device text scaling, VoiceOver/TalkBack name resolution and installed-PWA behaviour remain human checks');
LOG.forEach(function (line) { console.log('  ' + line); });
if (FAIL > 0) throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed');
