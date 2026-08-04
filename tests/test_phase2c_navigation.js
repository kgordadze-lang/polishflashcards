// Deterministic tests for Phase 2C responsive navigation and information architecture.
// Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_phase2c_navigation.js
//
// The suite executes the shipping drawer and install-state functions against a
// realistic fake DOM. Browser top-layer rendering, real key synthesis, accessibility
// trees, screen readers, and Android hardware Back remain human checks.

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
var MARKUP = INDEX.slice(0, INDEX.indexOf('<script src="data-a1.js">'));
var GUIDE = readFile(ROOT + 'guide/index.html');
var LISTENING = readFile(ROOT + 'guide/listening/index.html');
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
function squash(s) { return String(s).replace(/\s+/g, ''); }
function visibleText(s) {
  return String(s).replace(/<[^>]+>/g, ' ')
    .replace(/&middot;/g, '·').replace(/&amp;/g, '&').replace(/&rsquo;/g, '’')
    .replace(/&#x27;/g, "'").replace(/\s+/g, ' ').trim();
}
function elementTexts(src, tag, className) {
  var out = [], re = new RegExp('<' + tag + '(?: class="' + className + '")?>([\\s\\S]*?)<\\/' + tag + '>', 'g'), m;
  while ((m = re.exec(src))) out.push(visibleText(m[1]));
  return out;
}
function hasCode(hay, needle) { return squash(hay).indexOf(squash(needle)) !== -1; }
function extractFunction(src, name) {
  var needle = 'function ' + name + '(';
  var start = src.indexOf(needle);
  if (start === -1) throw new Error('extract: function ' + name + ' not found');
  if (src.indexOf(needle, start + 1) !== -1) throw new Error('extract: duplicate ' + name);
  var open = src.indexOf('{', src.indexOf(')', start));
  var depth = 0, mode = 'code';
  for (var j = open; j < src.length; j++) {
    var c = src[j], n = src[j + 1];
    if (mode === 'line') { if (c === '\n') mode = 'code'; continue; }
    if (mode === 'block') { if (c === '*' && n === '/') { mode = 'code'; j++; } continue; }
    if (mode === 'sq' || mode === 'dq' || mode === 'tpl') {
      if (c === '\\') { j++; continue; }
      if (mode === 'sq' && c === "'") mode = 'code';
      else if (mode === 'dq' && c === '"') mode = 'code';
      else if (mode === 'tpl' && c === '`') mode = 'code';
      continue;
    }
    if (c === '/' && n === '/') { mode = 'line'; j++; continue; }
    if (c === '/' && n === '*') { mode = 'block'; j++; continue; }
    if (c === "'") { mode = 'sq'; continue; }
    if (c === '"') { mode = 'dq'; continue; }
    if (c === '`') { mode = 'tpl'; continue; }
    if (c === '{') depth++;
    else if (c === '}') { depth--; if (depth === 0) return src.slice(start, j + 1); }
  }
  throw new Error('extract: unbalanced ' + name);
}
function attr(tag, name) {
  var m = tag && tag.match(new RegExp('\\s' + name + '="([^"]*)"'));
  if (m) return m[1];
  return tag && new RegExp('\\s' + name + '(?:\\s|>|/)').test(tag) ? '' : null;
}
function tagFor(src, id) {
  var re = new RegExp('<[^>]+\\sid="' + id + '"[^>]*>');
  var m = src.match(re);
  return m ? m[0] : '';
}
function section(id) {
  var start = INDEX.indexOf('<section class="screen" id="' + id + '">');
  if (id === 'home') start = INDEX.indexOf('<section class="screen active" id="home">');
  var end = INDEX.indexOf('</section>', start);
  return start === -1 || end === -1 ? '' : INDEX.slice(start, end + 10);
}

// -------------------------------------------------------------------------
// A. Shipping menu structure, semantics, destinations, and primary controls.
// -------------------------------------------------------------------------
var MENU_BUTTON = tagFor(INDEX, 'siteMenuButton');
var DRAWER_START = INDEX.indexOf('<dialog class="site-drawer" id="siteDrawer"');
var DRAWER_END = INDEX.indexOf('</dialog>', DRAWER_START);
var DRAWER = INDEX.slice(DRAWER_START, DRAWER_END + 9);
var NAV_START = DRAWER.indexOf('<nav aria-label="Site menu">');
var NAV_END = DRAWER.indexOf('</nav>', NAV_START);
var NAV = DRAWER.slice(NAV_START, NAV_END + 6);
ok('A1 Menu is a native button', /^<button\b/.test(MENU_BUTTON));
eq('A1 Menu has the exact accessible name', attr(MENU_BUTTON, 'aria-label'), 'Menu');
eq('A1 Menu is collapsed initially', attr(MENU_BUTTON, 'aria-expanded'), 'false');
eq('A1 Menu controls the drawer', attr(MENU_BUTTON, 'aria-controls'), 'siteDrawer');
eq('A1 Menu remains in the normal tab order', attr(MENU_BUTTON, 'tabindex'), null);
ok('A1 the hamburger is a visible three-line icon hidden from AT',
   /<svg[\s\S]*aria-hidden="true"[\s\S]*M4 7h16M4 12h16M4 17h16/.test(section('home')));
ok('A2 Menu has a practical 44 by 44 CSS target',
   /\.site-menu-button\s*\{[^}]*width:44px[^}]*height:44px/.test(INDEX));
ok('A2 Menu retains visible focus styling', /\.site-menu-button:focus-visible\s*\{[^}]*outline:/.test(INDEX));
eq('A2 the old top-right Add app chip is gone', countOf(INDEX, 'id="ppChip"'), 0);
eq('A2 the old visible Add app label is gone', countOf(INDEX, '>\n        Add app\n'), 0);
ok('A3 the drawer is a native dialog without an initial open attribute',
   /^<dialog\b/.test(tagFor(INDEX, 'siteDrawer')) && attr(tagFor(INDEX, 'siteDrawer'), 'open') === null);
eq('A3 the drawer references its visible title', attr(tagFor(INDEX, 'siteDrawer'), 'aria-labelledby'), 'siteMenuTitle');
eq('A3 the drawer has one labelled navigation landmark', countOf(DRAWER, '<nav aria-label="Site menu">'), 1);
eq('A3 the drawer has one navigation list', countOf(NAV, '<ul class="site-nav-list">'), 1);
eq('A3 no application-menu role was introduced', countOf(DRAWER, 'role="menu'), 0);
ok('A3 Close is a native labelled button', /^<button\b/.test(tagFor(INDEX, 'siteMenuClose')) &&
   attr(tagFor(INDEX, 'siteMenuClose'), 'aria-label') === 'Close menu');
ok('A3 the drawer can scroll internally', /\.site-drawer-panel\s*\{[^}]*overflow-y:auto/.test(INDEX));
ok('A3 top, right, and bottom safe-area insets are present',
   /safe-area-inset-top/.test(INDEX) && /safe-area-inset-right/.test(INDEX) && /safe-area-inset-bottom/.test(INDEX));
ok('A3 drawer height follows the dynamic viewport rather than a fixed pixel height', /height:100dvh/.test(INDEX));
ok('A3 drawer width remains bounded and avoids horizontal overflow', /width:min\(88vw,370px\)/.test(INDEX));

// The approved refinement renames the Guide menu label to "Explore more Polish" and
// moves it near the bottom. The /guide/ destination, its page, and its SEO are untouched.
var DESTS = [
  ['About', '#about', 'a'],
  ['Install', null, 'button'],
  ['Privacy', '#privacy', 'a'],
  ['What else I listen to', 'guide/listening/', 'a'],
  ['Explore more Polish', 'guide/', 'a'],
  ['Contact', '#contact', 'a']
];
var positions = [];
DESTS.forEach(function (d) {
  var needle = d[0] === 'Install' ? '<span>Install</span>' : '>' + d[0] + '</a>';
  var at = NAV.indexOf(needle);
  positions.push(at);
  ok('A4 destination exists: ' + d[0], at !== -1);
  if (d[1]) ok('A4 ' + d[0] + ' keeps the exact normal-link target',
               NAV.indexOf('href="' + d[1] + '"') !== -1);
});
ok('A4 destinations are in the approved exact order', positions.every(function (at, i) {
  return at !== -1 && (i === 0 || at > positions[i - 1]);
}));
// Read the rendered list items back in document order rather than trusting substring
// positions alone, so a reordering or an extra item cannot pass unnoticed.
function menuItemLabels(nav) {
  var out = [], re = /<li\b[^>]*>([\s\S]*?)<\/li>/g, m;
  while ((m = re.exec(nav))) {
    var anchor = m[1].match(/<a\b[^>]*>([\s\S]*?)<\/a>/);
    if (anchor) { out.push(visibleText(anchor[1])); continue; }
    var span = m[1].match(/<span>([\s\S]*?)<\/span>/);
    out.push(visibleText(span ? span[1] : m[1]));
  }
  return out;
}
eq('A4 the menu renders exactly the approved final order and labels', menuItemLabels(NAV),
   ['About', 'Install', 'Privacy', 'What else I listen to', 'Explore more Polish', 'Contact']);
eq('A4 the menu has exactly six destinations', countOf(NAV, '<li'), 6);
eq('A4 one clear list is the only copy of the menu', countOf(INDEX, 'class="site-nav-list"'), 1);
ok('A4 Install is a native action button with exact accessible name',
   /^<button\b/.test(tagFor(INDEX, 'siteInstall')) && attr(tagFor(INDEX, 'siteInstall'), 'aria-label') === 'Install');
ok('A4 the Guide destination stays discoverable as an ordinary anchor in rendered HTML',
   /<a href="guide\/">Explore more Polish<\/a>/.test(NAV));
eq('A4 the approved Guide label is exact and occurs once in the menu',
   countOf(NAV, '>Explore more Polish</a>'), 1);
eq('A4 the old visible Guide menu label is absent', countOf(NAV, '>Guide<'), 0);
eq('A4 the renamed item still points at the unchanged guide/ destination',
   countOf(NAV, 'href="guide/"'), 1);
eq('A4 the refinement added no second Guide link to the app shell',
   countOf(INDEX, 'href="guide/"'), 2);
eq('A4 Explore more Polish sits near the bottom, with only Contact after it',
   (NAV.slice(NAV.indexOf('>Explore more Polish</a>')).match(/<li\b/g) || []).length, 1);
eq('A4 Privacy is the only data/privacy menu destination', countOf(NAV, '>Privacy</a>'), 1);
eq('A4 Your data stays yours is not a competing menu item', countOf(NAV, 'Your data stays yours'), 0);
['about','privacy','contact','install'].forEach(function (id) {
  ok('A5 app target #' + id + ' exists', section(id).length > 0);
  eq('A5 app target #' + id + ' has one h1', (section(id).match(/<h1\b/g) || []).length, 1);
});
var allIds = {}, duplicateIds = [];
var idRe = /\sid="([^"]+)"/g, idMatch;
while ((idMatch = idRe.exec(MARKUP))) {
  if (allIds[idMatch[1]]) duplicateIds.push(idMatch[1]);
  allIds[idMatch[1]] = true;
}
eq('A5 shipping markup contains no duplicate ids', duplicateIds, []);
['Search','Vocabulary','Grammar','More','A1','A2','B1'].forEach(function (label) {
  ok('A6 primary control remains represented: ' + label, INDEX.indexOf(label) !== -1);
  eq('A6 primary control is outside the drawer: ' + label, DRAWER.indexOf('>' + label + '<'), -1);
});
ok('A6 Search remains the labelled home search control',
   /id="search"[^>]*aria-label="Search topics across all levels"/.test(INDEX));
ok('A6 the home logo and Menu remain siblings in the same top row',
   section('home').indexOf('class="logo"') < section('home').indexOf('id="siteMenuButton"'));

// -------------------------------------------------------------------------
// B. Information architecture reorganization and preserved destinations.
// -------------------------------------------------------------------------
var ABOUT = section('about'), PRIVACY = section('privacy'), CONTACT = section('contact');
var APPROVED_ABOUT = [
  'I’m a foreigner living in Poland, learning Polish while studying for a master’s degree - and trying to use the language in everyday life, not just in a textbook. Po polsku began as a simple way to remember the words and phrases I kept needing in real situations.',
  'It has grown into a practical learning app with vocabulary, grammar, listening, typing, mixed quizzes, conversations, and pronunciation audio. I review and improve the content continuously, with help from native Polish speakers around me, including my teacher.',
  'Po polsku is completely free, requires no account, and keeps your learning progress on your device. It is built for learners who want Polish they can understand, remember, and actually use.'
];
eq('B1 About contains the exact approved three paragraphs', elementTexts(ABOUT, 'p', 'about-p'), APPROVED_ABOUT);
eq('B1 About no longer contains separated subsection cards', countOf(ABOUT, 'class="about-contact"'), 0);
eq('B1 About no longer duplicates Privacy copy', countOf(ABOUT, 'Your data stays yours'), 0);
eq('B1 About no longer duplicates listening recommendations', countOf(ABOUT, 'What else I listen to'), 0);
eq('B1 About no longer duplicates Contact', countOf(ABOUT, '>Contact<'), 0);
ok('B1 About still states the project purpose and free model', ABOUT.indexOf('Po polsku began') !== -1 && ABOUT.indexOf('completely free') !== -1);
ok('B2 Privacy has the exact approved destination heading', PRIVACY.indexOf('<h1>Privacy - your data stays yours</h1>') !== -1);
eq('B2 Privacy has the exact four semantic subsection headings', elementTexts(PRIVACY, 'h2', ''),
   ['Your learning data', 'Analytics and hosting', 'Pronunciation', 'Progress and backups']);
eq('B2 Privacy has the exact approved introduction', elementTexts(PRIVACY, 'p', 'privacy-intro'), [
  'Po polsku is designed to help you learn Polish without requiring an account or building a learner profile.'
]);
var APPROVED_PRIVACY = [
  'Your progress, known words, and app settings are stored locally in your browser on this device. Po polsku does not send this learning data to an account or central database.',
  'Where supported, the app asks your browser to keep this storage persistently, but the browser decides whether to grant that request. Browser data can still be removed by you or by your browser or device, so a backup is the safest way to keep a separate copy.',
  'Po polsku does not use advertising, marketing cookies, or analytics tools.',
  'The site is delivered through GitHub Pages and Cloudflare, which may process standard technical request data needed to deliver and protect the site. Po polsku does not use this information to build learner profiles.',
  'Pronunciation normally uses pre-recorded audio provided with the app. If a clip cannot play, the app may use your browser’s built-in speech feature. That fallback is controlled by your browser or device.',
  'A backup downloads a JSON file containing your Po polsku progress and app data to a location you choose. Restoring a backup reads the file you select and applies it on this device.',
  'Installing the app can provide a more app-like and reliable experience, but it should not replace keeping a backup.'
];
eq('B2 Privacy contains the exact approved subsection copy', elementTexts(PRIVACY, 'p', 'about-p'), APPROVED_PRIVACY);
ok('B2 Privacy owns the existing backup and restore controls',
   PRIVACY.indexOf('id="dataBackup"') !== -1 && PRIVACY.indexOf('id="dataRestore"') !== -1 && PRIVACY.indexOf('id="dataFile"') !== -1);
ok('B2 the install cross-link is now a normal stable anchor',
   /id="dataInstallLink" href="#install"/.test(PRIVACY) && PRIVACY.indexOf('role="button"') === -1);
eq('B3 Contact has the exact approved lead', elementTexts(CONTACT, 'h2', 'contact-lead'),
   ['Have an idea, want to collaborate, or simply want to connect?']);
eq('B3 Contact has the exact approved supporting paragraph', elementTexts(CONTACT, 'p', 'about-p'), [
  'Po polsku is an independent and evolving project. I’m always open to thoughtful collaborations, useful resources, new ideas, and conversations about making Polish easier and more engaging to learn.'
]);
// Phase 3 closeout: the visible word "Email" became a decorative inline envelope, and the
// accessible name is now declared explicitly on the link, so only the address is visible.
// tests/test_phase3_closeout.js section D owns the icon and accessible-name contract.
ok('B3 Contact has the prominent normal mailto action with exact destination',
   CONTACT.indexOf('<a class="contact-email" href="mailto:hello@popolsku.app" ') !== -1);
ok('B3 the contact action still carries the label Email before the visible address',
   CONTACT.indexOf('aria-label="Email hello@popolsku.app"') !== -1 &&
   CONTACT.indexOf('</svg>hello@popolsku.app</a>') !== -1);
eq('B3 the contact email occurs once in the app shell', countOf(INDEX, 'mailto:hello@popolsku.app'), 1);
ok('B4 listening recommendations retain their separate generated destination',
   /<h1>What else I listen to<\/h1>/.test(LISTENING));
ok('B4 listening page has the exact approved introduction', visibleText(LISTENING).indexOf(
   'Flashcards help you learn words. Getting used to the sound of Polish takes hours of listening. These are three resources I keep coming back to because they cover different stages of the same journey: clear learner-friendly Polish, real-life listening with plenty of visual context, and natural Polish at full speed.') !== -1);
ok('B4 Real Polish wording and external-link behavior remain present',
   LISTENING.indexOf('Real Polish') !== -1 && /href="https:\/\/realpolish\.pl\/" target="_blank" rel="noopener"/.test(LISTENING));
ok('B4 Ratio viva wording and external-link behavior remain present',
   LISTENING.indexOf('Ratio viva') !== -1 && /href="https:\/\/www\.youtube\.com\/@Ratio_viva" target="_blank" rel="noopener"/.test(LISTENING));
ok('B4 listening page has the exact approved disclosure', visibleText(LISTENING).indexOf(
   'These are personal recommendations. None of the creators paid to be included here.') !== -1);
eq('B4 removed listening sentence is absent', countOf(LISTENING, 'They are just what worked.'), 0);
eq('B4 listening recommendations are not duplicated in the app About screen', countOf(ABOUT, 'Real Polish'), 0);
ok('B5 app footer derives version and runtime year without a second value',
   INDEX.indexOf('Po polsku · <span id="footVersion"></span> · <span id="footYear"></span>') !== -1 &&
   INDEX.indexOf('"v" + APP_VERSION') !== -1 && INDEX.indexOf('new Date().getFullYear()') !== -1);

// -------------------------------------------------------------------------
// C. Execute the shipping drawer functions with realistic modal/focus state.
// -------------------------------------------------------------------------
function Classes() { this.names = {}; }
Classes.prototype.contains = function (name) { return !!this.names[name]; };
Classes.prototype.add = function (name) { this.names[name] = true; };
Classes.prototype.remove = function (name) { delete this.names[name]; };
function El(id, tag) {
  this.id = id || ''; this.tag = tag || 'div'; this.attrs = {}; this.classList = new Classes();
  this.hidden = false; this.inert = false; this.disabled = false; this.connected = true;
  this.parentElement = null; this.children = []; this.focusCount = 0; this.open = false;
  this.showCount = 0; this.closeCount = 0; this.heading = null;
}
El.prototype.append = function (child) { child.parentElement = this; this.children.push(child); return child; };
El.prototype.setAttribute = function (name, value) { this.attrs[name] = String(value); };
El.prototype.getAttribute = function (name) {
  return Object.prototype.hasOwnProperty.call(this.attrs, name) ? this.attrs[name] : null;
};
El.prototype.hasAttribute = function (name) { return Object.prototype.hasOwnProperty.call(this.attrs, name); };
El.prototype.removeAttribute = function (name) { delete this.attrs[name]; };
El.prototype.focus = function (options) {
  if (!this.connected || this.disabled) return;
  for (var node = this; node; node = node.parentElement) {
    if (node.hidden || node.inert || node.getAttribute('aria-hidden') === 'true') return;
  }
  this.focusCount++; this.lastFocusOptions = options || null; fakeDocument.activeElement = this;
};
El.prototype.showModal = function () { if (this.open) throw new Error('already open'); this.open = true; this.showCount++; };
El.prototype.close = function () { if (!this.open) throw new Error('not open'); this.open = false; this.closeCount++; };
function makeScreen(id) {
  var screen = new El(id, 'section');
  var heading = screen.append(new El(id + 'Heading', 'h1')); screen.heading = heading;
  return screen;
}
var fakeBody = new El('body', 'body');
var appShell = fakeBody.append(new El('appShell'));
var menuButton = appShell.append(new El('siteMenuButton', 'button')); menuButton.setAttribute('aria-expanded', 'false');
var backgroundButton = appShell.append(new El('backgroundButton', 'button'));
var drawer = fakeBody.append(new El('siteDrawer', 'dialog'));
var menuClose = drawer.append(new El('siteMenuClose', 'button'));
// Phase 3B-1A made the maturity gate a native <dialog> outside the app shell, on the
// same modal contract as the drawer, so the drawer's stacking guard reads its open state.
var mature = fakeBody.append(new El('matureGate', 'dialog'));
var screens = { about:makeScreen('about'), privacy:makeScreen('privacy'), contact:makeScreen('contact'), install:makeScreen('install') };
Object.keys(screens).forEach(function (key) { appShell.append(screens[key]); });
var byId = { appShell:appShell, siteMenuButton:menuButton, backgroundButton:backgroundButton,
             siteDrawer:drawer, siteMenuClose:menuClose, matureGate:mature,
             about:screens.about, privacy:screens.privacy, contact:screens.contact, install:screens.install };
var fakeDocument = {
  body:fakeBody,
  activeElement:fakeBody,
  contains:function (el) { return !!(el && el.connected); }
};
function lookup(id) { return byId[id] || null; }
function focusElement(el) {
  if (!el || !el.connected || el.disabled) return false;
  var before = fakeDocument.activeElement;
  el.focus({preventScroll:true});
  return fakeDocument.activeElement === el && (before === el || el.focusCount > 0);
}
var invokers = [], shown = [], fakeScrollY = 731;
function useInvoker(el) { invokers.push(el); }
function showScreenStub(id) { shown.push(id); screens[id].heading.focus({preventScroll:true}); }
var MENU_BLOCK_START = INDEX.indexOf('var ppSiteMenuBackground = null;');
var MENU_BLOCK_END = INDEX.indexOf('function showScreen(', MENU_BLOCK_START);
if (MENU_BLOCK_START === -1 || MENU_BLOCK_END === -1) throw new Error('shipping menu helper block not found');
var MENU_BLOCK = INDEX.slice(MENU_BLOCK_START, MENU_BLOCK_END);
var MENU_FACTORY = Function('document','lookup','ppFocusElement','ppUseInvokerForNextScreen','show',
  'var $=lookup;\n' + MENU_BLOCK + '\nreturn {' +
  'isOpen:ppSiteMenuIsOpen,isolate:ppIsolateSiteMenuBackground,restore:ppRestoreSiteMenuBackground,' +
  'open:ppOpenSiteMenu,close:ppCloseSiteMenu,activate:ppActivateSiteMenuScreen,' +
  'background:function(){return ppSiteMenuBackground;}};');
var MENU_API = MENU_FACTORY(fakeDocument, lookup, focusElement, useInvoker, showScreenStub);
var learningState = { card:7, activity:'mixed', score:11, scene:'confirm', level:'A2', topic:'Home', progress:'unchanged' };
var learningSnapshot = JSON.stringify(learningState);

fakeDocument.activeElement = menuButton;
ok('C1 shipping open succeeds', MENU_API.open());
ok('C1 dialog is open in the modal path', drawer.open && MENU_API.isOpen());
eq('C1 aria-expanded becomes true', menuButton.getAttribute('aria-expanded'), 'true');
ok('C1 focus moves to Close', fakeDocument.activeElement === menuClose);
eq('C1 Close receives one explicit final focus move', menuClose.focusCount, 1);
eq('C1 focus uses preventScroll', menuClose.lastFocusOptions, {preventScroll:true});
ok('C1 the app shell is inert while open', appShell.inert && appShell.hasAttribute('inert'));
eq('C1 the app shell is hidden from the accessibility tree', appShell.getAttribute('aria-hidden'), 'true');
ok('C1 body scrolling is locked by a reversible class', fakeBody.classList.contains('site-menu-open'));
backgroundButton.focus();
ok('C2 a background control cannot receive focus while open', fakeDocument.activeElement === menuClose);
menuButton.focus();
ok('C2 the inactive Menu button cannot receive focus while open', fakeDocument.activeElement === menuClose);
eq('C2 repeated open is ignored', MENU_API.open(), false);
eq('C2 repeated open does not call showModal twice', drawer.showCount, 1);
eq('C2 opening preserves scroll position', fakeScrollY, 731);
eq('C2 opening preserves all learning state', JSON.stringify(learningState), learningSnapshot);

ok('C3 shipping close succeeds', MENU_API.close(true));
eq('C3 aria-expanded becomes false', menuButton.getAttribute('aria-expanded'), 'false');
ok('C3 dialog is closed', !drawer.open && !MENU_API.isOpen());
ok('C3 app-shell inertness is removed', !appShell.inert && !appShell.hasAttribute('inert'));
eq('C3 app-shell aria-hidden is removed', appShell.getAttribute('aria-hidden'), null);
ok('C3 body scrolling is restored', !fakeBody.classList.contains('site-menu-open'));
ok('C3 focus returns to Menu', fakeDocument.activeElement === menuButton);
eq('C3 Menu receives one final close focus move', menuButton.focusCount, 1);
backgroundButton.focus();
ok('C3 no focus trap remains after close', fakeDocument.activeElement === backgroundButton);
eq('C3 closing preserves scroll position', fakeScrollY, 731);
eq('C3 closing preserves all learning state', JSON.stringify(learningState), learningSnapshot);
eq('C3 repeated close is ignored', MENU_API.close(true), false);

appShell.inert = true; appShell.setAttribute('inert', 'existing');
appShell.setAttribute('aria-hidden', 'false'); fakeBody.classList.add('site-menu-open');
ok('C4 direct background isolation records a pre-existing state', MENU_API.isolate());
eq('C4 isolation changes aria-hidden while active', appShell.getAttribute('aria-hidden'), 'true');
ok('C4 restoration succeeds', MENU_API.restore());
ok('C4 prior inert property is restored', appShell.inert);
eq('C4 prior inert attribute value is restored', appShell.getAttribute('inert'), 'existing');
eq('C4 prior aria-hidden value is restored', appShell.getAttribute('aria-hidden'), 'false');
ok('C4 a pre-existing body lock class is not removed', fakeBody.classList.contains('site-menu-open'));
appShell.inert = false; appShell.removeAttribute('inert'); appShell.removeAttribute('aria-hidden'); fakeBody.classList.remove('site-menu-open');

mature.open = true; fakeDocument.activeElement = menuButton;
eq('C5 opening is rejected while the maturity overlay is active', MENU_API.open(), false);
eq('C5 no second modal layer opened', drawer.open, false);
mature.open = false;
menuClose.connected = false;
eq('C5 an invalid disconnected initial focus target aborts open safely', MENU_API.open(), false);
ok('C5 failed focus leaves no open dialog or inert app', !drawer.open && !appShell.inert && !MENU_API.background());
menuClose.connected = true;

for (var cycle = 0; cycle < 3; cycle++) {
  fakeDocument.activeElement = menuButton;
  ok('C6 repeated cycle ' + (cycle + 1) + ' opens', MENU_API.open());
  ok('C6 repeated cycle ' + (cycle + 1) + ' closes', MENU_API.close(true));
}
ok('C6 repeated cycles end with the app interactive', !drawer.open && !appShell.inert && !fakeBody.classList.contains('site-menu-open'));
eq('C6 repeated cycles preserve state', JSON.stringify(learningState), learningSnapshot);

fakeDocument.activeElement = menuButton; MENU_API.open();
var menuFocusBeforeNav = menuButton.focusCount, aboutFocusBefore = screens.about.heading.focusCount;
var aboutLink = new El('aboutLink', 'a'); aboutLink.setAttribute('data-app-screen', 'about');
ok('C7 valid app navigation activates through the shipping helper', MENU_API.activate(aboutLink));
eq('C7 navigation closes the drawer', drawer.open, false);
eq('C7 navigation reuses the existing screen router', shown[shown.length - 1], 'about');
ok('C7 navigation records Menu as the existing return-focus invoker', invokers[invokers.length - 1] === menuButton);
eq('C7 navigation avoids an intermediate Menu focus move', menuButton.focusCount, menuFocusBeforeNav);
eq('C7 navigation has one final destination focus', screens.about.heading.focusCount - aboutFocusBefore, 1);
eq('C7 navigation preserves learning state', JSON.stringify(learningState), learningSnapshot);

// Native dialog cancel is the shared path for desktop Escape and Android Back.
var historyCalls = 0, cancelPrevented = 0;
fakeDocument.activeElement = menuButton; MENU_API.open();
if (MENU_API.close(true)) cancelPrevented++;
eq('C8 an open-dialog cancel is consumed once', cancelPrevented, 1);
eq('C8 cancel closes before any history navigation', historyCalls, 0);
cancelPrevented = 0;
if (MENU_API.close(true)) cancelPrevented++;
eq('C8 a closed drawer does not swallow ordinary Back', cancelPrevented, 0);
eq('C8 the drawer helper block creates no History API state',
   [countOf(MENU_BLOCK, 'history.pushState'), countOf(MENU_BLOCK, 'history.back'), countOf(MENU_BLOCK, 'popstate')], [0,0,0]);
ok('C8 shipping cancel listener prevents default only after a successful close',
   hasCode(INDEX, 'if(ppCloseSiteMenu(true)) e.preventDefault()'));
ok('C8 backdrop activation owns the same close helper',
   hasCode(INDEX, 'if(e.target===$("siteDrawer")){ ppCloseSiteMenu(true); return; }'));
ok('C8 Close owns the same close helper', INDEX.indexOf('$("siteMenuClose").addEventListener("click", ()=>ppCloseSiteMenu(true))') !== -1);
eq('C9 the native Menu has one click listener', countOf(INDEX, '$("siteMenuButton").addEventListener("click", ppOpenSiteMenu)'), 1);
ok('C9 Enter and Space cannot reach the global Study shortcut',
   hasCode(extractFunction(INDEX, 'ppGlobalShortcutBlocked'), 'ppIsInteractiveTarget(e.target)'));

// -------------------------------------------------------------------------
// D. Execute the shipping install-state architecture.
// -------------------------------------------------------------------------
var A2HS_START = INDEX.indexOf('const PP_A2HS = (function(){');
var A2HS_END = INDEX.indexOf('})();', A2HS_START);
if (A2HS_START === -1 || A2HS_END === -1) throw new Error('shipping PP_A2HS block not found');
var A2HS_SOURCE = INDEX.slice(A2HS_START, A2HS_END + 4);
var A2HS_FACTORY = Function('document','window','navigator','localStorage','matchMedia','location','URLSearchParams',
                            'show','ppUseInvokerForNextScreen','ppCloseSiteMenu','setTimeout',
  A2HS_SOURCE + '\nreturn PP_A2HS;');
function Store(seed) { this.data = seed || {}; }
Store.prototype.getItem = function (key) { return Object.prototype.hasOwnProperty.call(this.data, key) ? this.data[key] : null; };
Store.prototype.setItem = function (key, value) { this.data[key] = String(value); };
Store.prototype.removeItem = function (key) { delete this.data[key]; };
function makeA2HSEnv(options) {
  options = options || {};
  var ids = {
    siteInstallItem:new El('siteInstallItem'), siteInstallDetail:new El('siteInstallDetail'),
    siteInstallStatus:new El('siteInstallStatus'), siteInstall:new El('siteInstall','button'),
    siteMenuButton:new El('siteMenuButton','button'),
    ppBanner:new El('ppBanner'), ppNative:new El('ppNative')
  };
  ids.ppNative.hidden = true;
  var documentEvents = {}, windowEvents = {}, created = [];
  var doc = {
    body:{appendChild:function (el) { created.push(el); }},
    getElementById:function (id) { return ids[id] || null; },
    querySelectorAll:function () { return []; },
    addEventListener:function (type, fn) { documentEvents[type] = fn; },
    createElement:function () { return {className:'',textContent:'',remove:function(){}}; }
  };
  var nav = {
    userAgent:options.userAgent || 'Mozilla/5.0', platform:options.platform || 'MacIntel',
    maxTouchPoints:options.maxTouchPoints || 0, standalone:!!options.navigatorStandalone,
    storage:{persisted:function(){return {then:function(){return {catch:function(){}};}};},
             persist:function(){return {catch:function(){}};}}
  };
  var win = { navigator:nav, addEventListener:function (type, fn) { windowEvents[type] = fn; } };
  var storage = new Store(options.storage || {});
  var shownScreens = [], invokerCalls = [], closeCalls = [], timerCalls = 0;
  function match(query) { return {matches:!!(options.standalone && query === '(display-mode: standalone)')}; }
  function Params(search) { this.search = search || ''; }
  Params.prototype.has = function (key) { return this.search.indexOf(key + '=') !== -1; };
  function showStub(id) { shownScreens.push(id); }
  function invokerStub(el) { invokerCalls.push(el); }
  function closeStub(restore) { closeCalls.push(restore); return true; }
  function timeoutStub() { timerCalls++; }
  var api = A2HS_FACTORY(doc, win, nav, storage, match, {search:options.search || ''}, Params,
                          showStub, invokerStub, closeStub, timeoutStub);
  return {api:api,ids:ids,docEvents:documentEvents,windowEvents:windowEvents,storage:storage,
          shown:shownScreens,invokers:invokerCalls,closes:closeCalls,created:created,
          timerCount:function(){return timerCalls;}};
}
function addClickTarget(inMenu) {
  var add = { closest:function (selector) { return selector === '#siteDrawer' && inMenu ? {} : null; } };
  return { closest:function (selector) { return selector === '[data-a2hs-add]' ? add : null; } };
}
function clickEvent(target) {
  return {target:target,preventCount:0,preventDefault:function(){this.preventCount++;}};
}

var browser = makeA2HSEnv(); browser.api.init();
eq('D1 initial supported-browser fallback state is honest instructions', browser.api.installState(), 'instructions');
eq('D1 Install remains operable in the fallback state', browser.ids.siteInstallItem.hidden, false);
eq('D1 fallback visible detail says Instructions', browser.ids.siteInstallDetail.textContent, 'Instructions');
eq('D1 fallback accessible state describes supported-browser instructions',
   browser.ids.siteInstallStatus.textContent, 'Open installation instructions for supported browsers');
var promptCount = 0, promptPrevented = 0;
var promptEvent = {
  preventDefault:function(){promptPrevented++;},
  prompt:function(){promptCount++;},
  userChoice:{then:function(){ /* deliberately pending: exercises the busy guard */ }}
};
browser.windowEvents.beforeinstallprompt(promptEvent);
eq('D2 beforeinstallprompt is prevented and retained by the shipping listener', promptPrevented, 1);
eq('D2 browser prompt state becomes available', browser.api.installState(), 'prompt');
eq('D2 menu state visibly says Ready', browser.ids.siteInstallDetail.textContent, 'Ready');
eq('D2 menu state exposes browser installation availability', browser.ids.siteInstallStatus.textContent, 'Browser installation is available');
eq('D2 existing Install now shortcut becomes available', browser.ids.ppNative.hidden, false);
var browserClick = clickEvent(addClickTarget(true));
browser.docEvents.click(browserClick);
eq('D3 menu install activation prevents unrelated default navigation', browserClick.preventCount, 1);
eq('D3 browser installation prompt runs once', promptCount, 1);
eq('D3 drawer closes once before the prompt', browser.closes, [true]);
eq('D3 browser prompt path does not navigate to instructions', browser.shown, []);
browser.docEvents.click(clickEvent(addClickTarget(true)));
eq('D3 rapid repeated activation cannot run the prompt twice', promptCount, 1);
eq('D3 rapid repeated activation still does not navigate away', browser.shown, []);
ok('D3 shipping consumes deferred before reading userChoice',
   A2HS_SOURCE.indexOf('deferred=null') < A2HS_SOURCE.indexOf('promptEvent.userChoice'));
ok('D3 shipping has an explicit pending-install guard', A2HS_SOURCE.indexOf('if(installing) return "busy"') !== -1);

var ios = makeA2HSEnv({userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X)'}); ios.api.init();
eq('D4 iPhone/iPad state is derived as instructions', ios.api.installState(), 'ios-instructions');
eq('D4 iOS state does not pretend one-tap install is ready', ios.ids.siteInstallDetail.textContent, 'Instructions');
eq('D4 iOS accessible state names Home Screen instructions',
   ios.ids.siteInstallStatus.textContent, 'Open iPhone or iPad Home Screen instructions');
var iosClick = clickEvent(addClickTarget(true)); ios.docEvents.click(iosClick);
eq('D4 iOS menu action routes to the existing instructions screen', ios.shown, ['install']);
ok('D4 iOS screen routing preserves Menu as the app-screen return target', ios.invokers[0] === ios.ids.siteMenuButton);
eq('D4 iOS closes without an intermediate focus restoration', ios.closes, [false]);

var unsupported = makeA2HSEnv(); unsupported.api.init();
unsupported.docEvents.click(clickEvent(addClickTarget(true)));
eq('D5 unavailable programmatic install is not a dead action', unsupported.shown, ['install']);
eq('D5 unavailable state is described as instructions rather than automatic install',
   unsupported.ids.siteInstallStatus.textContent, 'Open installation instructions for supported browsers');

var installed = makeA2HSEnv({standalone:true}); installed.api.init();
eq('D6 installed PWA state is detected', installed.api.installState(), 'installed');
eq('D6 installed PWA hides the Install item', installed.ids.siteInstallItem.hidden, true);
eq('D6 installed PWA exposes no active delegated install action', typeof installed.docEvents.click, 'undefined');
installed.api.install();
eq('D6 direct installed-state invocation does not navigate', installed.shown, []);

var installedEvent = makeA2HSEnv(); installedEvent.api.init();
installedEvent.windowEvents.appinstalled();
eq('D7 appinstalled is authoritative only for the current session', installedEvent.api.installState(), 'installed');
eq('D7 appinstalled writes no permanent installed boolean', installedEvent.storage.getItem('popolsku-a2hs'), null);
eq('D7 appinstalled hides the menu item and banner',
   [installedEvent.ids.siteInstallItem.hidden, installedEvent.ids.ppBanner.hidden], [true,true]);
eq('D7 appinstalled retains the existing completion toast', installedEvent.created.length, 1);
ok('D8 existing beforeinstallprompt and appinstalled event owners remain singular',
   countOf(INDEX, 'window.addEventListener("beforeinstallprompt"') === 1 && countOf(INDEX, 'window.addEventListener("appinstalled"') === 1);
eq('D8 installation stays on the single delegated add-action owner', countOf(INDEX, 'e.target.closest("[data-a2hs-add]")'), 1);

// -------------------------------------------------------------------------
// E. Guide SEO, generated-page boundary, and stable internal links.
// -------------------------------------------------------------------------
eq('E1 Guide document title remains exact',
   (GUIDE.match(/<title>([^<]+)<\/title>/) || [])[1],
   'Polish guide - grammar, slang and idioms explained simply | Po polsku');
eq('E1 Guide canonical remains exact', attr((GUIDE.match(/<link rel="canonical"[^>]*>/) || [''])[0], 'href'), 'https://popolsku.app/guide/');
eq('E1 Guide has one clear main heading', (GUIDE.match(/<h1\b/g) || []).length, 1);
ok('E1 Guide main heading remains meaningful', GUIDE.indexOf('<h1>Polish, explained simply</h1>') !== -1);
ok('E1 Guide learner-facing content is rendered in HTML', GUIDE.indexOf('Grammar Cases') !== -1 && GUIDE.indexOf('Slang &amp; idioms') !== -1);
eq('E1 Guide has no noindex directive', countOf(GUIDE.toLowerCase(), 'noindex'), 0);
ok('E1 Guide remains a standalone generated page', BUILD.indexOf('def guide_page(') !== -1 && BUILD.indexOf('guide/index.html') !== -1);
eq('E1 the approved menu label did not leak into the Guide pages or the generator',
   countOf(GUIDE, 'Explore more Polish') + countOf(LISTENING, 'Explore more Polish') + countOf(BUILD, 'Explore more Polish'), 0);
ok('E1 generated breadcrumbs and back-links still use the Guide page name',
   countOf(BUILD, '<a href="/guide/">Guide</a>') === 3 && LISTENING.indexOf('href="/guide/">Guide</a>') !== -1);
ok('E1 generated pages retain their independent logo-only header',
   /<header class="top"><a href="\/" aria-label="Po polsku home"/.test(GUIDE) && GUIDE.indexOf('siteDrawer') === -1);
eq('E1 generated-page source has no Add app control', countOf(BUILD, 'ppChip'), 0);
ok('E2 Guide keeps its listening recommendation link', GUIDE.indexOf('href="/guide/listening/"') !== -1);
ok('E2 listening page links back to Guide', LISTENING.indexOf('href="/guide/">Guide</a>') !== -1);
eq('E2 listening canonical remains exact',
   attr((LISTENING.match(/<link rel="canonical"[^>]*>/) || [''])[0], 'href'), 'https://popolsku.app/guide/listening/');
eq('E2 listening page title remains meaningful',
   (LISTENING.match(/<title>([^<]+)<\/title>/) || [])[1], 'Polish podcasts worth listening to | Po polsku');
eq('E2 listening page has one main heading', (LISTENING.match(/<h1\b/g) || []).length, 1);
eq('E2 listening page has no noindex directive', countOf(LISTENING.toLowerCase(), 'noindex'), 0);
var GUIDE_PAGES = [['guide/index.html', GUIDE], ['guide/listening/index.html', LISTENING]];
GUIDE_PAGES.forEach(function (page) {
  var name = page[0], markup = page[1], text = visibleText(markup);
  eq('E3 ' + name + ' has one shared compact ending', countOf(markup, 'class="guide-ending"'), 1);
  ['Ready to keep learning?',
   'Practice the same Polish with flashcards, drills, conversations, and listening.',
   'Genuinely free. No account. Works offline.'].forEach(function (line) {
    ok('E3 ' + name + ' keeps exact ending copy: ' + line, text.indexOf(line) !== -1);
  });
  ok('E3 ' + name + ' has one normal primary app link',
     countOf(markup, '<a class="guide-primary" href="/">Open the app</a>'), 1);
  // Phase 3 closeout: the progress sentence and its Privacy link left the shared ending.
  // The Privacy screen, the drawer entry and the /#privacy route are unchanged - asserted
  // immediately below and in tests/test_phase3_closeout.js section F.
  eq('E3 ' + name + ' no longer carries the progress sentence',
     countOf(text, 'Your progress stays on this device and can be backed up anytime.'), 0);
  eq('E3 ' + name + ' no longer carries the progress link',
     countOf(markup, 'guide-progress-link') + countOf(markup, 'How progress works'), 0);
  eq('E3 ' + name + ' removes the old oversized CTA copy',
     countOf(markup, 'Open the app - flashcards, drills, conversations'), 0);
  eq('E3 ' + name + ' removes the old duplicate footer marketing sentence',
     countOf(markup, 'free Polish flashcards with audio. No account, no tracking, works offline.'), 0);
  ok('E3 ' + name + ' renders the derived version and build year',
     markup.indexOf('&middot; v8.4 &middot; ' + new Date().getFullYear() + '</footer>') !== -1);
});
ok('E3 the Guide Privacy URL is recognized as a direct app-screen destination',
   INDEX.indexOf('["about","privacy","contact","install"].includes(ppInitialScreen)') !== -1 &&
   INDEX.indexOf('showScreen(ppInitialScreen)') !== -1);
ok('E3 generated footer reads APP_VERSION and derives the build year',
   BUILD.indexOf('def read_app_version()') !== -1 && BUILD.indexOf('datetime.date.today().year') !== -1);
eq('E3 generator does not duplicate the current version literal', countOf(BUILD, '8.4'), 0);
ok('E3 one generator-owned ending and footer cover Guide, grammar and vocabulary pages',
   BUILD.indexOf('LEARNING_ENDING_STYLE =') !== -1 &&
   BUILD.indexOf('def learning_ending():') !== -1 &&
   BUILD.indexOf('def learning_footer(js=""):') !== -1 &&
   countOf(BUILD, 'body.append(learning_ending())') === 4 &&
   BUILD.indexOf('Practice this in the app - free, no account') === -1 &&
   BUILD.indexOf('Learn these as flashcards in the app - free, no account') === -1);
var internalFailures = [], hrefRe = /href="(\/[^"]*)"/g, hrefMatch;
while ((hrefMatch = hrefRe.exec(GUIDE))) {
  var path = hrefMatch[1].split('#')[0].split('?')[0];
  var local = path === '/' ? ROOT + 'index.html' : ROOT + path.replace(/^\//, '') + (path.slice(-1) === '/' ? 'index.html' : '');
  if (!$.NSFileManager.defaultManager.fileExistsAtPath(local)) internalFailures.push(path);
}
eq('E4 every rendered internal Guide link resolves to a committed target', internalFailures, []);
ok('E4 app no-script Guide link remains a normal fallback anchor',
   /<noscript>[\s\S]*<a href="guide\/"/.test(INDEX));
ok('E4 Guide does not depend on drawer JavaScript for destination content',
   GUIDE.indexOf('<main>') !== -1 && GUIDE.indexOf('<script></script>') !== -1);

// -------------------------------------------------------------------------
// F. Cross-phase safeguard and regression boundaries.
// -------------------------------------------------------------------------
ok('F1 app version is the 8.4 release', /const APP_VERSION = "8\.4"/.test(INDEX));
// Phase 4B-2 moves the app-shell cache to v57 so the revised navigation contract
// is isolated from the Phase 4B-1 shell while open tabs remain on their old worker.
ok('F1 app-shell cache is the Phase 4B-3 revision', /const CACHE = "popolsku-v58"/.test(SW));
ok('F1 audio cache remains popolsku-audio', /const AUDIO_CACHE = "popolsku-audio"/.test(SW));
ok('F1 schema version remains 2', /PP_MIGRATE\.SCHEMA_VERSION = 2/.test(MIGRATE));
ok('F1 content migration revision remains 2', /PP_MIGRATE\.CONTENT_MIGRATION_REVISION = 2/.test(MIGRATE));
ok('F1 manifest start URL and display metadata remain intact',
   MANIFEST.indexOf('"start_url": "./?pwa=1"') !== -1 && MANIFEST.indexOf('"display": "standalone"') !== -1);
ok('F2 screen routing remains on the existing History API',
   INDEX.indexOf('history.pushState') !== -1 && INDEX.indexOf('history.back()') !== -1 && INDEX.indexOf('popstate') !== -1);
eq('F2 no parallel hashchange model was introduced', countOf(INDEX, 'hashchange'), 0);
ok('F2 a direct informational screen keeps a marked replaceState entry',
   INDEX.indexOf('history.replaceState({scr:ppInitialScreen,direct:true}') !== -1);
ok('F2 the in-app Back control returns direct arrivals home without swallowing browser Back',
   hasCode(extractFunction(INDEX, 'show'), 'if(history.state.direct){ history.replaceState({scr:"home"}, "", location.pathname + location.search); showScreen("home", deferFocus); }else history.back();'));
ok('F2 drawer navigation reuses show rather than mutating learning state',
   hasCode(extractFunction(INDEX, 'ppActivateSiteMenuScreen'), 'show(scr)'));
['S.','G.','C.','T.','L.','R.'].forEach(function (prefix) {
  eq('F2 drawer helper does not mutate activity namespace ' + prefix, countOf(MENU_BLOCK, prefix), 0);
});
eq('F2 drawer helper does not touch localStorage progress', countOf(MENU_BLOCK, 'localStorage'), 0);
eq('F2 drawer helper does not stop or restart audio',
   countOf(MENU_BLOCK, 'stopAllAudio') + countOf(MENU_BLOCK, 'playPreGenerated'), 0);
ok('F3 the maturity overlay keeps its existing shared focus architecture',
   INDEX.indexOf('ppOpenSharedOverlay($("matureGate"), $("matureCancel"))') !== -1 &&
   INDEX.indexOf('ppCloseSharedOverlay($("matureGate"))') !== -1);
ok('F3 the drawer explicitly refuses modal stacking',
   hasCode(extractFunction(INDEX, 'ppOpenSiteMenu'), 'if(mature && mature.open) return false'));
eq('F3 no generated template was given the app drawer', countOf(BUILD, 'siteDrawer'), 0);

console.log('Phase 2C navigation tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
console.log('  [info] shipping drawer and install-state helpers run against deterministic modal, focus, inert, history and platform state');
console.log('  [info] real dialog top-layer rendering, key synthesis, Android Back, screen readers, zoom and safe areas remain manual');
LOG.forEach(function (line) { console.log('  ' + line); });
if (FAIL > 0) throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed');
