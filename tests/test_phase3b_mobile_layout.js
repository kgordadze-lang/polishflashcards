// Deterministic tests for Phase 3B-1A / 3B-2A narrow-screen layout, viewport fit and
// safe areas. Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_phase3b_mobile_layout.js
//
// Issues covered:
//   MLG-3A-01  home topic cards collapsed their text column to ~70px at 320px.  (3B-1A)
//   MLG-3A-11  the fixed toast had no safe-area inset.                          (3B-1A)
//   MLG-3A-04  activity header title truncated to 75px (35px at 200% text).     (3B-2A)
//   MLG-3A-05  in-app ending tables silently clipped cell text.                 (3B-2A)
//   MLG-3A-06  fixed card height floors pushed the control row below the fold.  (3B-2A)
//   MLG-3A-08  the Contact email action forced page-level horizontal overflow.  (3B-2A)
//   MLG-3A-12  three audited touch targets (.pp-x, .mini-audio, .build-pool).   (3B-2A)
//   MLG-3A-14  the reported "constant 6px" activity-page overflow.              (3B-2A)
//
// JavaScriptCore has no layout engine, so this suite asserts the stylesheet's layout
// contract rather than measured geometry. Real rendered widths, real safe-area insets
// and real device text scaling remain human checks; the Phase 3B-1A and 3B-2A evidence
// reports record the browser measurements taken alongside these assertions.
//
// Phase 3B-2B covers the remaining scroll-continuity issues (MLG-3A-09, 10, 13).

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
    if (fm.fileExistsAtPath(candidates[i] + 'index.html')) return candidates[i];
  }
  return cwd + '/';
}
var ROOT = resolveRoot();
var INDEX = readFile(ROOT + 'index.html');
function allStyleBlocks(src) {
  var out = [], re = /<style>([\s\S]*?)<\/style>/g, m;
  while ((m = re.exec(src))) out.push(m[1]);
  return out.join('\n');
}
var STYLE = allStyleBlocks(INDEX);
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
function stripComments(css) { return css.replace(/\/\*[\s\S]*?\*\//g, ''); }
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
// Every declaration block in the sheet, flattened, keeping its media condition.
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
function blocksFor(selector, media) {
  return DECL_BLOCKS.filter(function (b) {
    return b.selector === selector && (media === undefined || b.media === media);
  });
}
function mediaConditions() {
  return TOP_RULES.filter(function (r) { return /^@media/.test(r.prelude); })
                  .map(function (r) { return r.prelude.replace(/^@media\s*/, '').trim(); });
}
function maxWidthOf(condition) {
  var m = condition.match(/max-width\s*:\s*(\d+(?:\.\d+)?)px/);
  return m ? parseFloat(m[1]) : null;
}
function maxHeightOf(condition) {
  var m = condition.match(/max-height\s*:\s*(\d+(?:\.\d+)?)px/);
  return m ? parseFloat(m[1]) : null;
}
// A rule's prelude may list several selectors ('.stage,.flip'). Match any of them, so a
// grouped rule counts the same as a standalone one.
function selectorsOf(prelude) {
  return prelude.split(',').map(function (s) { return s.trim(); });
}
function rulesTouching(selector, media) {
  return DECL_BLOCKS.filter(function (b) {
    return selectorsOf(b.selector).indexOf(selector) !== -1 &&
           (media === undefined || b.media === media);
  });
}
// Last declaration wins within a media context, mirroring the cascade for equal specificity.
function declFor(selector, media, prop) {
  var found = null;
  rulesTouching(selector, media).forEach(function (b) {
    var v = decl(b.body, prop);
    if (v !== null) found = v;
  });
  return found;
}
function anyDeclares(selector, media, prop) {
  return rulesTouching(selector, media).some(function (b) { return decl(b.body, prop) !== null; });
}
function px(value) {
  if (value === null || value === undefined) return null;
  var m = String(value).match(/(-?\d+(?:\.\d+)?)px/);
  return m ? parseFloat(m[1]) : null;
}
var WIDE = '';                                   // no media condition = every width
var W400 = '@media (max-width:400px)';
function keyframes(name) {
  var rule = TOP_RULES.filter(function (r) {
    return new RegExp('^@(?:-webkit-)?keyframes\\s+' + name + '\\s*$').test(r.prelude);
  })[0];
  return rule ? rule.body : null;
}

// -------------------------------------------------------------------------
// A. One narrow-width breakpoint exists and is scoped (MLG-3A-01).
// -------------------------------------------------------------------------
var CONDITIONS = mediaConditions();
var NARROW = CONDITIONS.filter(function (c) {
  var w = maxWidthOf(c);
  return w !== null && w <= 360;
});
eq('A1 exactly one narrow breakpoint at or below 360px exists', NARROW.length, 1);
// Everything below depends on that breakpoint. Report a missing one as failed assertions
// rather than crashing the run, so the output still names what is wrong.
var NARROW_CONDITION = NARROW.length === 1 ? '@media ' + NARROW[0] : '@media (absent)';
function narrowBlock(selector) {
  return blocksFor(selector, NARROW_CONDITION)[0] || { selector: selector, body: null, media: NARROW_CONDITION };
}
eq('A1 the narrow breakpoint is the recommended 360px', NARROW.length === 1 ? maxWidthOf(NARROW[0]) : null, 360);
eq('A1 no extra widths were scattered across the sheet',
   CONDITIONS.filter(function (c) { return maxWidthOf(c) !== null; })
             .map(maxWidthOf).sort(function (a, b) { return a - b; }), [360, 400, 400]);
eq('A1 the two pre-existing 400px blocks are untouched in count',
   CONDITIONS.filter(function (c) { return maxWidthOf(c) === 400; }).length, 2);

var NARROW_BLOCKS = DECL_BLOCKS.filter(function (b) { return b.media === NARROW_CONDITION; });
var NARROW_SELECTORS = NARROW_BLOCKS.map(function (b) { return b.selector; });
ok('A2 the narrow breakpoint styles the topic row', NARROW_SELECTORS.indexOf('.topic') !== -1);
var NARROW_TOPIC = narrowBlock('.topic');
eq('A2 the topic row wraps at narrow widths', decl(NARROW_TOPIC.body, 'flex-wrap'), 'wrap');
ok('A2 the wrapped rows keep a deliberate vertical gap', decl(NARROW_TOPIC.body, 'row-gap') !== null);
var NARROW_MAIN = narrowBlock('.topic-main');
ok('A3 the text column takes a full row of its own', /100%/.test(decl(NARROW_MAIN.body, 'flex') || ''));
var NARROW_PILL = narrowBlock('.pill-practice');
ok('A3 the practice pill is restyled in the narrow breakpoint', NARROW_PILL.body !== null);
ok('A3 the practice pill no longer holds its intrinsic width against the text column',
   NARROW_PILL.body !== null && (decl(NARROW_PILL.body, 'flex') || '').replace(/\s+/g, ' ').indexOf('0 0 auto') === -1);
ok('A3 the practice pill grows into the row it now owns',
   /^1\s+1\s/.test((decl(NARROW_PILL.body, 'flex') || '').replace(/\s+/g, ' ')));
eq('A3 the decorative chevron is dropped rather than pushed onto its own row',
   decl(narrowBlock('.t-arrow').body, 'display'), 'none');
eq('A4 the emoji tile keeps its 46px touch target at every width',
   [blocksFor('.t-emoji', NARROW_CONDITION).length, decl(blocksFor('.t-emoji', '')[0].body, 'width')], [0, '46px']);
eq('A4 the narrow breakpoint changes nothing outside the topic row',
   NARROW_SELECTORS.sort(), ['.pill-practice', '.t-arrow', '.topic', '.topic-main']);

// The base rules the breakpoint overrides must still be the ones the audit measured.
var BASE_TOPIC = blocksFor('.topic', '')[0];
var BASE_MAIN = blocksFor('.topic-main', '')[0];
var BASE_PILL = blocksFor('.pill-practice', '')[0];
eq('A5 the wide-width topic row is unchanged', decl(BASE_TOPIC.body, 'display'), 'flex');
eq('A5 the wide-width topic row still has no wrapping', decl(BASE_TOPIC.body, 'flex-wrap'), null);
eq('A5 the wide-width text column still flexes and can shrink', decl(BASE_MAIN.body, 'min-width'), '0');
eq('A5 the wide-width practice pill is still intrinsically sized', decl(BASE_PILL.body, 'flex'), '0 0 auto');
eq('A6 topic markup and rendering are untouched by the layout fix',
   [countOf(INDEX, '<button class="topic-main">'), countOf(INDEX, '<div class="t-arrow">'),
    countOf(INDEX, 'class="pill-practice"'), countOf(INDEX, 'b.className = "topic"')], [1, 1, 1, 1]);
eq('A6 the line clamp that keeps descriptions to two lines is unchanged',
   decl(blocksFor('.t-desc', '')[0].body, '-webkit-line-clamp'), '2');

// -------------------------------------------------------------------------
// B. Safe areas for viewport-pinned elements (MLG-3A-11).
// -------------------------------------------------------------------------
var FIXED = DECL_BLOCKS.filter(function (b) { return (decl(b.body, 'position') || '') === 'fixed'; });
ok('B1 the sheet still has a small, reviewable set of fixed elements',
   FIXED.length > 0 && FIXED.length <= 6);
eq('B1 the fixed elements are the two modal overlays and the toast',
   FIXED.map(function (b) { return b.selector; }).sort(), ['.modal-overlay', '.site-drawer', '.toast']);

// Every fixed element is classified per edge, and no edge may simply omit the safe area:
//   auto / absent  -> that edge is not pinned; nothing to clear.
//   0              -> flush to the edge; the inset belongs in the element's own padding.
//   50% + translate-> centred, not pinned; horizontal insets belong in the width bound.
//   any real gap   -> the inset must be added to the offset itself, or system UI overlaps.
var SIDES = ['top', 'right', 'bottom', 'left'];
function insetShorthandSides(body) {
  var inset = decl(body, 'inset');
  if (inset === null) return {};
  var parts = inset.split(/\s+/);
  var t = parts[0], r = parts.length > 1 ? parts[1] : t,
      b = parts.length > 2 ? parts[2] : t, l = parts.length > 3 ? parts[3] : r;
  return { top: t, right: r, bottom: b, left: l };
}
FIXED.forEach(function (block) {
  var shorthand = insetShorthandSides(block.body);
  var centred = /translate/i.test(decl(block.body, 'transform') || '');
  var openBlock = blocksFor(block.selector + '[open]', block.media)[0];
  var panelSelector = block.selector === '.site-drawer' ? '.site-drawer-panel' : null;
  var allPadding = [decl(block.body, 'padding'),
                    openBlock ? decl(openBlock.body, 'padding') : null,
                    panelSelector ? decl(blocksFor(panelSelector, '')[0].body, 'padding') : null]
                   .filter(function (p) { return p; }).join(' ');
  var widthBound = (decl(block.body, 'max-width') || '') + ' ' + (decl(block.body, 'width') || '');
  SIDES.forEach(function (side) {
    var offset = decl(block.body, side) || shorthand[side] || null;
    var term = 'env(safe-area-inset-' + side + ')';
    if (offset === null || offset === 'auto') return;              // edge is not pinned
    if (offset === '0' || offset === '0px') {
      ok('B2 ' + block.selector + ' sits flush to the ' + side + ' edge and pads that safe area',
         allPadding.indexOf(term) !== -1);
    } else if (centred && /%$/.test(offset)) {
      ok('B2 ' + block.selector + ' is centred, so the ' + side + ' inset is taken out of its width',
         widthBound.indexOf('env(safe-area-inset-left)') !== -1 &&
         widthBound.indexOf('env(safe-area-inset-right)') !== -1);
    } else {
      ok('B2 ' + block.selector + ' pins ' + side + ' at a gap and adds the matching safe-area inset',
         offset.indexOf(term) !== -1);
    }
  });
});

var TOAST = blocksFor('.toast', '')[0];
ok('B3 the toast is still pinned to the bottom centre',
   decl(TOAST.body, 'bottom') !== null && decl(TOAST.body, 'left') === '50%');
ok('B3 the toast bottom offset clears the home indicator and the gesture bar',
   (decl(TOAST.body, 'bottom') || '').indexOf('env(safe-area-inset-bottom)') !== -1);
ok('B3 the toast keeps its original 18px visual offset above that inset',
   /calc\(\s*18px\s*\+/.test(decl(TOAST.body, 'bottom') || ''));
ok('B3 the toast width also accounts for the horizontal insets',
   (decl(TOAST.body, 'max-width') || '').indexOf('env(safe-area-inset-left)') !== -1 &&
   (decl(TOAST.body, 'max-width') || '').indexOf('env(safe-area-inset-right)') !== -1);
ok('B3 the toast keeps its original width ceiling', /min\(92vw,\s*420px\)/.test(decl(TOAST.body, 'max-width') || ''));
eq('B3 the toast is still created by the two existing owners, unchanged',
   [countOf(INDEX, 'className = "toast"') + countOf(INDEX, 'className="toast"'),
    countOf(INDEX, 'function voiceHint(')], [2, 1]);
ok('B4 the body still carries the document-level safe-area padding it always had',
   (decl(blocksFor('body', '')[0].body, 'padding') || '').indexOf('env(safe-area-inset-top)') !== -1);

// -------------------------------------------------------------------------
// C. Breakpoint inventory after Phase 3B-2A.
// -------------------------------------------------------------------------
// Phase 3B-2A adds exactly one height query and reuses the two existing width
// breakpoints. A new width breakpoint, or a second height breakpoint, is a deliberate
// architecture change and must update this list rather than slip in unnoticed.
var HEIGHT_CONDITIONS = CONDITIONS.filter(function (c) { return maxHeightOf(c) !== null; });
eq('C1 exactly one height breakpoint exists', HEIGHT_CONDITIONS.length, 1);
eq('C1 the height breakpoint is the documented 600px',
   HEIGHT_CONDITIONS.length === 1 ? maxHeightOf(HEIGHT_CONDITIONS[0]) : null, 600);
eq('C1 the height breakpoint is height-only, not a combined query',
   HEIGHT_CONDITIONS.length === 1 ? maxWidthOf(HEIGHT_CONDITIONS[0]) : 'n/a', null);
var SHORT = HEIGHT_CONDITIONS.length === 1 ? '@media ' + HEIGHT_CONDITIONS[0] : '@media (absent)';
eq('C1 the width breakpoints are unchanged from Phase 3B-1A',
   CONDITIONS.filter(function (c) { return maxWidthOf(c) !== null; })
             .map(maxWidthOf).sort(function (a, b) { return a - b; }), [360, 400, 400]);
eq('C2 the media-query set is exactly the documented set',
   CONDITIONS.slice().sort(),
   ['(max-height:600px)', '(max-width:360px)', '(max-width:400px)', '(max-width:400px)',
    '(prefers-reduced-motion:reduce)'].sort());

// -------------------------------------------------------------------------
// D. Activity header reflow (MLG-3A-04).
// -------------------------------------------------------------------------
var SBAR_NARROW = rulesTouching('.sbar', W400);
ok('D1 a narrow-width layout contract exists for .sbar', SBAR_NARROW.length > 0);
eq('D1 the narrow header is an explicit two-row grid', declFor('.sbar', W400, 'display'), 'grid');
ok('D1 the two rows are named, not implicit',
   /sbar-back[\s\S]*sbar-title[\s\S]*sbar-home[\s\S]*sbar-speed/
     .test((declFor('.sbar', W400, 'grid-template-areas') || '').replace(/"/g, '')));
ok('D1 the title column can shrink below its content width',
   /minmax\(\s*0\s*,\s*1fr\s*\)/.test(declFor('.sbar', W400, 'grid-template-columns') || ''));
ok('D1 Back keeps row one', (declFor('.sbar > .back', W400, 'grid-area') || '').indexOf('sbar-back') === 0);
ok('D1 Home keeps row one', (declFor('.sbar > .back.home-btn', W400, 'grid-area') || '').indexOf('sbar-home') === 0);
ok('D1 the title keeps row one', (declFor('.sbar > .sbar-title', W400, 'grid-area') || '').indexOf('sbar-title') === 0);
ok('D1 the speed control takes the second row',
   (declFor('.sbar > .speed-toggle', W400, 'grid-area') || '').indexOf('sbar-speed') === 0);
ok('D1 the speed control is right-aligned on its own row, like .dir-row',
   declFor('.sbar > .speed-toggle', W400, 'justify-self') === 'end');
// The wide layout is untouched: still one flex row.
eq('D2 the wide-width header is still a single flex row', declFor('.sbar', WIDE, 'display'), 'flex');
eq('D2 the wide-width header declares no grid areas', declFor('.sbar', WIDE, 'grid-template-areas'), null);

var H1 = blocksFor('.sbar-title h1', '')[0];
ok('D3 the shared activity title rule still exists', H1 !== undefined);
eq('D3 the title no longer depends on single-line white-space:nowrap',
   H1 ? decl(H1.body, 'white-space') : 'missing', null);
eq('D3 the title is allowed no more than two lines', H1 ? decl(H1.body, '-webkit-line-clamp') : null, '2');
ok('D3 the two-line clamp has the box display it needs',
   H1 !== undefined && /-webkit-box/.test(decl(H1.body, 'display') || '') &&
   decl(H1.body, '-webkit-box-orient') === 'vertical');
ok('D3 overflow past two lines is still ellipsised, not silently cut',
   H1 !== undefined && decl(H1.body, 'overflow') === 'hidden' && decl(H1.body, 'text-overflow') === 'ellipsis');
ok('D3 a long unbroken title token can wrap rather than overflow',
   H1 !== undefined && /anywhere|break-word/.test(decl(H1.body, 'overflow-wrap') || ''));
ok('D3 the title keeps its size - the fix is reflow, not smaller text',
   H1 !== undefined && decl(H1.body, 'font-size') === '15.5px');
// Exactly one speed control per activity header, still labelled, never duplicated.
eq('D4 the six activity headers each hold exactly one speed control',
   countOf(INDEX, '<button class="speed-toggle" data-role="speed-toggle" aria-label="Toggle audio speed" title="Toggle audio speed">'), 6);
eq('D4 no additional speed-toggle markup was introduced',
   countOf(INDEX, 'class="speed-toggle"') + countOf(INDEX, 'class="speed-toggle dir-toggle"'), 7);
eq('D4 the speed control keeps its visible text label, not an icon-only fallback',
   countOf(INDEX, '<span class="speed-label">Normal</span>'), 6);
eq('D4 the speed label keeps its fixed width so the chip does not jump',
   decl(blocksFor('.speed-label', '')[0].body, 'min-width'), '44px');
eq('D4 the direction toggle is still the only other member of the speed-toggle family',
   countOf(INDEX, 'class="speed-toggle dir-toggle"'), 1);
eq('D5 every header still has its Back control and its Home control',
   [countOf(INDEX, '<div class="sbar">'),
    countOf(INDEX, '<button class="back home-btn" aria-label="Home page">')], [10, 10]);
ok('D5 no header control is hidden at narrow widths',
   !rulesTouching('.sbar', W400).concat(
      rulesTouching('.sbar > .speed-toggle', W400),
      rulesTouching('.sbar > .back', W400),
      rulesTouching('.sbar > .back.home-btn', W400),
      rulesTouching('.sbar > .sbar-title', W400))
     .some(function (b) { return (decl(b.body, 'display') || '') === 'none'; }));
// The titles themselves are content and must not have been reworded or shortened.
[['<h1 id="tTitle">Type it</h1>', 'Type it'],
 ['<h1 id="lTitle">Listening</h1>', 'Listening'],
 ['<h1 id="rTitle">Practice</h1>', 'Practice'],
 ['<h1>Privacy</h1>', 'Privacy'],
 ['<h1>About</h1>', 'About'], ['<h1>Contact</h1>', 'Contact'],
 ['<h1>Install</h1>', 'Install']].forEach(function (pair) {
  eq('D6 the ' + pair[1] + ' header title is unchanged', countOf(INDEX, pair[0]), 1);
});
eq('D6 the three script-filled activity titles are still script-filled',
   [countOf(INDEX, '<h1 id="studyTitle"></h1>'), countOf(INDEX, '<h1 id="gTitle"></h1>'),
    countOf(INDEX, '<h1 id="cTitle" lang="pl"></h1>')], [1, 1, 1]);

// -------------------------------------------------------------------------
// E. In-app ending tables (MLG-3A-05).
// -------------------------------------------------------------------------
var END_TABLE = blocksFor('.end-table', '')[0];
var END_TD = blocksFor('.end-table td', '')[0];
ok('E1 the ending-table rule still exists', END_TABLE !== undefined && END_TD !== undefined);
eq('E1 the table no longer clips its own cell text', END_TABLE ? decl(END_TABLE.body, 'overflow') : 'missing', null);
ok('E1 no narrow-width rule reintroduces clipping on the table',
   !rulesTouching('.end-table', W400).some(function (b) {
     return /hidden|clip/.test(decl(b.body, 'overflow') || ''); }));
ok('E2 cells declare a deliberate wrap contract',
   END_TD !== undefined && /anywhere|break-word/.test(decl(END_TD.body, 'overflow-wrap') || ''));
eq('E2 the wrap contract is the one that also bounds min-content width',
   END_TD ? decl(END_TD.body, 'overflow-wrap') : null, 'anywhere');
eq('E2 narrow cells give the text back the room the gutters were taking',
   declFor('.end-table td', W400, 'padding'), '9px 7px');
ok('E2 the narrow cell padding is smaller than the wide one',
   px(declFor('.end-table td', W400, 'padding')) < px(decl(END_TD.body, 'padding')));
eq('E3 the rounded corner styling is kept', END_TABLE ? decl(END_TABLE.body, 'border-radius') : null, '14px');
eq('E3 the table is still a real table with predictable columns',
   END_TABLE ? decl(END_TABLE.body, 'table-layout') : null, 'fixed');
eq('E3 the column ratios are unchanged',
   [decl(blocksFor('.end-table .g', '')[0].body, 'width'),
    decl(blocksFor('.end-table .e', '')[0].body, 'width'),
    decl(blocksFor('.end-table .ex', '')[0].body, 'width')], ['30%', '34%', '36%']);
eq('E3 no font-size reduction was used to make the tables fit',
   [END_TABLE ? decl(END_TABLE.body, 'font-size') : null,
    decl(blocksFor('.end-table .e', '')[0].body, 'font-size')], ['12.5px', '14px']);
// One render path, still emitting a plain semantic table - no wrapper, nothing hidden.
eq('E4 ending tables are still emitted by exactly one render path',
   countOf(INDEX, '<table class="end-table"><tbody>'), 1);
eq('E4 the emitted markup is still a bare semantic table with no visual wrapper',
   countOf(INDEX, "if(t.table)    b+='<table class=\"end-table\"><tbody>'+t.table.map(r=>'<tr><td class=\"g\">'+r.g+'</td><td class=\"e\">'+r.e+'</td><td class=\"ex\">'+r.ex+'</td></tr>').join('')+'</tbody></table>';"), 1);
ok('E4 no ending-table cell is display:none at any width',
   !DECL_BLOCKS.filter(function (b) { return /\.end-table/.test(b.selector); })
               .some(function (b) { return (decl(b.body, 'display') || '') === 'none'; }));

// -------------------------------------------------------------------------
// F. Viewport-aware card and control fit (MLG-3A-06).
// -------------------------------------------------------------------------
['.stage', '.flip'].forEach(function (sel) {
  var base = declFor(sel, WIDE, 'min-height');
  ok('F1 ' + sel + ' declares a viewport-aware height', base !== null && /clamp\(/.test(base) && /dvh/.test(base));
  ok('F1 ' + sel + ' keeps the original 452px as its ceiling, not its floor', /452px\s*\)/.test(base || ''));
});
// No block anywhere may reintroduce a static floor above ~430px.
var STATIC_FLOORS = DECL_BLOCKS.filter(function (b) {
  return selectorsOf(b.selector).some(function (s) { return s === '.stage' || s === '.flip'; });
}).map(function (b) { return { media: b.media, value: decl(b.body, 'min-height') }; })
  .filter(function (r) { return r.value !== null; });
ok('F2 every card height declaration is a clamp, never a bare pixel floor',
   STATIC_FLOORS.length > 0 && STATIC_FLOORS.every(function (r) { return /clamp\(/.test(r.value); }));
ok('F2 no second fixed floor above ~430px survives',
   !STATIC_FLOORS.some(function (r) { return /^\s*\d+(\.\d+)?px\s*$/.test(r.value) && px(r.value) > 430; }));
eq('F2 the old 400px-wide 430px floor is gone', declFor('.flip', W400, 'min-height'), 'clamp(272px,52dvh,452px)');
ok('F2 the narrow-width floor is not larger than the wide one at the same viewport',
   px(declFor('.flip', W400, 'min-height')) <= px(declFor('.flip', WIDE, 'min-height')));
// A short-viewport rule exists and trims vertical cost rather than hiding anything.
ok('F3 the short-viewport rule sizes the card against the viewport',
   /clamp\(/.test(declFor('.stage', SHORT, 'min-height') || '') &&
   /dvh/.test(declFor('.stage', SHORT, 'min-height') || ''));
['.sbar', '.progress', '.stage', '.controls', '.done'].forEach(function (sel) {
  ok('F3 the short-viewport rule trims ' + sel + ' padding', declFor(sel, SHORT, 'padding') !== null);
});
ok('F3 the short-viewport rule hides nothing',
   !DECL_BLOCKS.filter(function (b) { return b.media === SHORT; })
               .some(function (b) { return (decl(b.body, 'display') || '') === 'none'; }));
ok('F3 the short-viewport rule resizes no text',
   !DECL_BLOCKS.filter(function (b) { return b.media === SHORT; })
               .some(function (b) { return decl(b.body, 'font-size') !== null; }));
// The two faces still share one grid cell; the flip geometry is untouched.
eq('F4 the card is still a grid so both faces share one cell', declFor('.flip', WIDE, 'display'), 'grid');
eq('F4 both faces still occupy that single cell', decl(blocksFor('.face', '')[0].body, 'grid-area'), '1/1');
eq('F4 the 3-D flip contract is unchanged',
   [declFor('.flip', WIDE, 'transform-style'),
    decl(blocksFor('.flip.flipped', '')[0].body, 'transform'),
    decl(blocksFor('.face', '')[0].body, 'backface-visibility'),
    decl(blocksFor('.back-face', '')[0].body, 'transform')],
   ['preserve-3d', 'rotateY(180deg)', 'hidden', 'rotateY(180deg)']);
ok('F4 the card is not turned into an internal scroll region',
   !['.stage', '.flip', '.face', '.scene'].some(function (sel) {
     return rulesTouching(sel, undefined).some(function (b) {
       return /auto|scroll/.test(decl(b.body, 'overflow') || decl(b.body, 'overflow-y') || ''); }); }));
// Completion actions survive, in order, on all five completion screens.
eq('F5 all five completion action groups are still present', countOf(INDEX, 'class="done-actions"'), 5);
eq('F5 the Study completion actions are unchanged in wording and order',
   (INDEX.match(/<div class="done-actions">([\s\S]*?)<\/div>/) || ['', ''])[1]
     .split('\n').map(function (l) { return (l.match(/>([^<]+)<\/button>/) || [])[1]; })
     .filter(function (t) { return t; }),
   ['Quiz this set', 'Practice still learning', 'Restart this set', 'Back to topics']);
ok('F5 the completion screens declare no height floor of their own',
   declFor('.done', WIDE, 'min-height') === null && declFor('.done-actions', WIDE, 'min-height') === null);

// -------------------------------------------------------------------------
// G. Contact email reflow (MLG-3A-08).
// -------------------------------------------------------------------------
var CE = blocksFor('.contact-email', '')[0];
ok('G1 the contact email rule still exists', CE !== undefined);
eq('G1 the action is bounded by its card', CE ? decl(CE.body, 'max-width') : null, '100%');
ok('G1 the address may break rather than overflow',
   CE !== undefined && /anywhere|break-word/.test(decl(CE.body, 'overflow-wrap') || ''));
eq('G1 the touch height is preserved, not reduced', CE ? decl(CE.body, 'min-height') : null, '43px');
eq('G1 the text is not shrunk to force one line', CE ? decl(CE.body, 'font-size') : null, '14px');
ok('G1 focus styling is still declared', blocksFor('.contact-email:focus-visible', '')[0] !== undefined);
// Phase 3 closeout replaced the visible word "Email" with a decorative inline envelope and
// an explicit aria-label. The mailto target, the reflow contract above and the 43px touch
// height are unchanged; tests/test_phase3_closeout.js section D owns the icon and name
// contract.
eq('G2 the mailto target is byte-identical',
   countOf(INDEX, '<a class="contact-email" href="mailto:hello@popolsku.app" '), 1);
eq('G2 the visible address is unchanged', countOf(INDEX, '</svg>hello@popolsku.app</a>'), 1);
eq('G2 no second contact action was introduced', countOf(INDEX, 'class="contact-email"'), 1);

// -------------------------------------------------------------------------
// H. Targeted touch targets (MLG-3A-12) - exactly three controls change.
// -------------------------------------------------------------------------
var PPX = blocksFor('.pp-x', '')[0];
eq('H1 .pp-x is exactly 40x40',
   [decl(PPX.body, 'width'), decl(PPX.body, 'height')], ['40px', '40px']);
ok('H1 .pp-x gained clear space from the adjacent Add action',
   px(decl(PPX.body, 'margin-left')) > 0);
eq('H1 .pp-x keeps its glyph and its accessible name',
   [countOf(INDEX, '<button class="pp-x" data-a2hs-dismiss aria-label="Not now">'),
    decl(blocksFor('.pp-x svg', '')[0].body, 'width')], [1, '16px']);
eq('H1 the banner row still lets the text column absorb the change',
   decl(blocksFor('.pp-tx', '')[0].body, 'min-width'), '0');
eq('H2 .mini-audio is exactly 36x36',
   [decl(blocksFor('.mini-audio', '')[0].body, 'width'),
    decl(blocksFor('.mini-audio', '')[0].body, 'height')], ['36px', '36px']);
eq('H2 .mini-audio now matches the established .ex-audio target',
   [decl(blocksFor('.mini-audio', '')[0].body, 'width'),
    decl(blocksFor('.ex-audio', '')[0].body, 'width')], ['36px', '36px']);
eq('H2 the mini-audio icon is unchanged', decl(blocksFor('.mini-audio svg', '')[0].body, 'width'), '15px');
var POOL_GAP = px(decl(blocksFor('.build-pool', '')[0].body, 'gap'));
ok('H3 .build-pool uses an approved 10-12px gap  (got ' + POOL_GAP + ')',
   POOL_GAP >= 10 && POOL_GAP <= 12);
eq('H3 the chips themselves are unchanged',
   [decl(blocksFor('.wchip', '')[0].body, 'padding'), decl(blocksFor('.wchip', '')[0].body, 'font-size')],
   ['9px 14px', '15px']);
eq('H3 the pool still wraps rather than scrolling',
   decl(blocksFor('.build-pool', '')[0].body, 'flex-wrap'), 'wrap');
// Everything the audit listed but did NOT approve must keep its exact dimensions.
[['.back', 'width', '40px'], ['.back', 'height', '40px'],
 ['.speed-toggle', 'height', '34px'], ['.chal-toggle', 'height', '30px'],
 ['.dir-toggle', 'height', '32px'],
 ['.flip-control', 'width', '40px'], ['.flip-control', 'height', '40px'],
 ['.ex-audio', 'width', '36px'], ['.ex-audio', 'height', '36px'],
 ['.pill-practice', 'padding', '7px 13px'], ['.cat-btn', 'padding', '10px 0'],
 ['.site-menu-button', 'width', '44px'], ['.site-drawer-close', 'width', '44px'],
 ['.fab', 'width', '46px'], ['.ctrl', 'padding', '14px 10px']].forEach(function (t) {
  eq('H4 ' + t[0] + ' ' + t[1] + ' was not enlarged', decl(blocksFor(t[0], '')[0].body, t[1]), t[2]);
});

// -------------------------------------------------------------------------
// I. The reported constant 6px activity overflow (MLG-3A-14).
// -------------------------------------------------------------------------
// Root cause confirmed in the browser: it is NOT the 3-D card scene. Neutralising
// perspective, transform-style and the rotated back face leaves the overflow unchanged at
// 0, while applying the .screen entry animation's own start keyframe reproduces it exactly
// (translateY(6px) -> 6px, translateY(20px) -> 20px). The overflow is transient - it lasts
// the 0.35s entry transition and is gone once the animation finishes. No containment was
// committed here: every candidate clips at the same 6px magnitude as the .flip focus ring,
// which the phase requires to stay unclipped.
//
// Phase 3 closeout resolved it at the source instead: .screen now runs an opacity-only
// `screenFade` at the same .35s ease, so no transform crosses the viewport edge and no
// clipping was needed. The shared `fade` keyframe is unchanged for the in-flow elements that
// still use it. tests/test_phase3_closeout.js section A owns that contract; the assertions
// below keep pinning the 3-D scene's innocence and the absence of global overflow hiding.
var FADE = keyframes('fade');
ok('I1 the shared fade keyframe still exists for its in-flow users', FADE !== null);
ok('I1 the shared fade keyframe is unchanged', /translateY\(6px\)/.test(FADE || ''));
ok('I1 the screen entry no longer uses the translating keyframe',
   !/\bfade\b/.test(declFor('.screen', WIDE, 'animation') || '') &&
   /\bscreenFade\b/.test(declFor('.screen', WIDE, 'animation') || ''));
ok('I2 no containment was bolted onto the 3-D scene',
   declFor('.scene', WIDE, 'overflow') === null && declFor('.scene', WIDE, 'contain') === null);
eq('I2 the scene keeps the perspective the register blamed', declFor('.scene', WIDE, 'perspective'), '1600px');
// The hard guarantee: nothing anywhere in the sheet hides overflow at document level.
['html', 'body', '.wrap', '.app-main', '.screen', '.screen.active', '.scene', '.stage'].forEach(function (sel) {
  var hiding = rulesTouching(sel, undefined).filter(function (b) {
    return ['overflow', 'overflow-x', 'overflow-y'].some(function (prop) {
      return /hidden|clip/.test(decl(b.body, prop) || ''); });
  }).map(function (b) { return b.selector + (b.media ? ' @ ' + b.media : ''); });
  eq('I3 ' + sel + ' never hides overflow at document level', hiding, []);
});
ok('I3 no rule anywhere introduces overflow-x:hidden',
   !DECL_BLOCKS.some(function (b) { return /hidden|clip/.test(decl(b.body, 'overflow-x') || ''); }));
eq('I3 the only overflow lock on body is still the Phase 2C drawer scroll lock',
   DECL_BLOCKS.filter(function (b) {
     return selectorsOf(b.selector).indexOf('body.site-menu-open') !== -1; })
     .map(function (b) { return decl(b.body, 'overflow'); }), ['hidden']);
ok('I4 the reduced-motion rule still disables the flip and screen animations',
   CONDITIONS.indexOf('(prefers-reduced-motion:reduce)') !== -1 &&
   DECL_BLOCKS.some(function (b) {
     return b.media === '@media (prefers-reduced-motion:reduce)' &&
            selectorsOf(b.selector).indexOf('.flip') !== -1 &&
            selectorsOf(b.selector).indexOf('.screen') !== -1 &&
            decl(b.body, 'animation') === 'none'; }));
eq('I4 the flip markup is unchanged',
   [countOf(INDEX, 'class="flip" id="flip"'), countOf(INDEX, 'class="flip" id="gFlip"'),
    countOf(INDEX, 'class="face back-face"'), countOf(INDEX, 'class="face back-face g-back"'),
    countOf(INDEX, 'class="scene"')], [1, 1, 1, 1, 2]);

// -------------------------------------------------------------------------
// J. Cross-cutting rejections the phase must keep honouring.
// -------------------------------------------------------------------------
// Nothing was solved by hiding a control.
var NEW_MEDIA = [W400, SHORT, NARROW_CONDITION];
ok('J1 no control is hidden inside any responsive block',
   !DECL_BLOCKS.filter(function (b) { return NEW_MEDIA.indexOf(b.media) !== -1; })
     .some(function (b) {
       return (decl(b.body, 'display') || '') === 'none' &&
              !/^\.t-arrow$/.test(b.selector);          // decorative chevron, Phase 3B-1A
     }));
ok('J1 no responsive block reduces a font size to force a layout',
   !DECL_BLOCKS.filter(function (b) { return b.media === W400 || b.media === SHORT || b.media === NARROW_CONDITION; })
     .some(function (b) {
       return decl(b.body, 'font-size') !== null &&
              ['.pl', '.en', '.pl.dir-en', '.en.dir-pl', '.hero h1'].indexOf(b.selector) === -1;
     }));                                               // the four card scales are pre-existing
eq('J2 no visibility:hidden was introduced anywhere in the sheet',
   DECL_BLOCKS.filter(function (b) { return (decl(b.body, 'visibility') || '') === 'hidden'; }).length, 0);
eq('J3 no generated-page code was pulled into the app shell', /build_pages/.test(INDEX), false);
eq('J3 the app version this phase must not touch is intact',
   (INDEX.match(/APP_VERSION\s*=\s*"([^"]+)"/) || [])[1], '8.6');
// The three approved touch-target changes are the only dimension changes in the diff: no
// other control gained width/height/padding under the new responsive blocks.
eq('J4 no control was resized inside the new responsive blocks',
   DECL_BLOCKS.filter(function (b) { return b.media === W400 || b.media === SHORT; })
     .filter(function (b) {
       return ['width', 'height'].some(function (p) { return decl(b.body, p) !== null; });
     }).map(function (b) { return b.selector; }).sort(),
   ['.done-badge', '.site-drawer']);            // completion badge trim + Phase 3B-1A drawer

console.log('Phase 3B-1A/3B-2A mobile layout tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
console.log('  [info] MLG-3A-01, 04, 05, 06, 08, 11, 12: stylesheet, markup and breakpoint contracts asserted from the shipping <style> and <body> blocks');
console.log('  [info] MLG-3A-14: root cause confirmed in the browser as the .screen entry keyframe, not the 3-D scene; no containment committed - the assertions pin the cause and the absence of global overflow hiding');
console.log('  [info] rendered widths, real safe-area insets and device text scaling remain manual; browser measurements are in the Phase 3B-1A and 3B-2A evidence reports');
LOG.forEach(function (line) { console.log('  ' + line); });
if (FAIL > 0) throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed');
