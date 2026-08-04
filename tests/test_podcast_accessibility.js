// Deterministic Phase 2B tests for podcast cards and podcast-only Mixed Quiz paths.
// Runs shipping helpers/functions extracted from index.html against the real podcast
// corpus. Browser accessibility trees, screen readers and visual focus remain manual.
ObjC.import('Foundation');

function readFile(path) {
  var s = $.NSString.stringWithContentsOfFileEncodingError(path, $.NSUTF8StringEncoding, null);
  return ObjC.unwrap(s);
}
function resolveRoot() {
  var fm = $.NSFileManager.defaultManager, cwd = ObjC.unwrap(fm.currentDirectoryPath);
  var candidates = [cwd + '/', cwd + '/../'];
  for (var i = 0; i < candidates.length; i++)
    if (fm.fileExistsAtPath(candidates[i] + 'index.html')) return candidates[i];
  return cwd + '/';
}
var ROOT = resolveRoot(), INDEX = readFile(ROOT + 'index.html');
var PODCAST_DATA = readFile(ROOT + 'data-podcasts.js');
var PASS = 0, FAIL = 0, LOG = [];
function ok(name, cond) { if (cond) PASS++; else { FAIL++; LOG.push('FAIL: ' + name); } }
function eq(name, actual, expected) {
  var a = JSON.stringify(actual), e = JSON.stringify(expected);
  ok(name + (a === e ? '' : ' (got ' + a + ', want ' + e + ')'), a === e);
}
function extractFunction(src, name) {
  var needle = 'function ' + name + '(', start = src.indexOf(needle);
  if (start === -1 || src.indexOf(needle, start + 1) !== -1) throw new Error('extract: ' + name);
  var open = src.indexOf('{', src.indexOf(')', start)), depth = 0, mode = 'code';
  for (var i = open; i < src.length; i++) {
    var c = src[i], n = src[i + 1];
    if (mode === 'line') { if (c === '\n') mode = 'code'; continue; }
    if (mode === 'block') { if (c === '*' && n === '/') { mode = 'code'; i++; } continue; }
    if (mode === 'sq' || mode === 'dq' || mode === 'tpl') {
      if (c === '\\') { i++; continue; }
      if ((mode === 'sq' && c === "'") || (mode === 'dq' && c === '"') ||
          (mode === 'tpl' && c === '`')) mode = 'code';
      continue;
    }
    if (c === '/' && n === '/') { mode = 'line'; i++; continue; }
    if (c === '/' && n === '*') { mode = 'block'; i++; continue; }
    if (c === "'") { mode = 'sq'; continue; }
    if (c === '"') { mode = 'dq'; continue; }
    if (c === '`') { mode = 'tpl'; continue; }
    if (c === '{') depth++;
    else if (c === '}') { depth--; if (depth === 0) return src.slice(start, i + 1); }
  }
  throw new Error('unbalanced: ' + name);
}
function tagFor(id) {
  var at = INDEX.indexOf('id="' + id + '"');
  return INDEX.slice(INDEX.lastIndexOf('<', at), INDEX.indexOf('>', at) + 1);
}
function attr(tag, name) {
  var m = tag.match(new RegExp('\\s' + name + '\\s*=\\s*"([^"]*)"'));
  return m ? m[1] : null;
}

var win = { PP_LEVELS: [] };
(new Function('window', PODCAST_DATA))(win);
var level = win.PP_LEVELS[0], topics = level.topics;
ok('A1 real podcast data exposes at least one topic', topics.length > 0);
ok('A1 every discovered topic is a podcast', topics.every(function (t) { return t.kind === 'podcast'; }));

function Classes() { this.names = {}; }
Classes.prototype.contains = function (n) { return !!this.names[n]; };
Classes.prototype.add = function (n) { this.names[n] = true; };
Classes.prototype.remove = function (n) { delete this.names[n]; };
Classes.prototype.toggle = function (n, force) { if (force) this.add(n); else this.remove(n); };
function El(id) {
  this.id = id || ''; this.attrs = {}; this.hidden = false; this.href = '';
  this.disabled = false; this.classList = new Classes(); this.faces = [];
}
El.prototype.setAttribute = function (n, v) { this.attrs[n] = String(v); };
El.prototype.getAttribute = function (n) {
  return Object.prototype.hasOwnProperty.call(this.attrs, n) ? this.attrs[n] : null;
};
El.prototype.removeAttribute = function (n) { delete this.attrs[n]; };
El.prototype.querySelectorAll = function (s) { return s === '.face' ? this.faces : []; };

var configure = (new Function(extractFunction(INDEX, 'ppConfigurePodcastIntroLink') +
  '\nreturn ppConfigurePodcastIntroLink;'))();
var audioName = (new Function(extractFunction(INDEX, 'ppAudioControlName') +
  '\nreturn ppAudioControlName;'))();

topics.forEach(function (topic) {
  var intros = topic.cards.filter(function (c) { return c.intro; });
  eq('A2 ' + topic.id + ' has one introduction', intros.length, 1);
  var intro = intros[0], before = JSON.stringify(intro);
  ok('A2 ' + topic.id + ' retains host/source wording', !!intro.host && !!intro.hint);
  ok('A2 ' + topic.id + ' retains an ordinary HTTPS destination', /^https:\/\//.test(intro.link));
  var link = new El('ytLink'), details = new El('backHint');
  ok('A3 ' + topic.id + ' configures its shipping anchor', configure(link, intro, details));
  eq('A3 ' + topic.id + ' preserves the exact destination', link.href, intro.link);
  eq('A3 ' + topic.id + ' associates host and description', link.getAttribute('aria-describedby'), 'backHint');
  ok('A3 ' + topic.id + ' names the episode and new-tab purpose',
     link.getAttribute('aria-label').indexOf(intro.en) !== -1 &&
     /opens in a new tab/.test(link.getAttribute('aria-label')));
  eq('A3 ' + topic.id + ' helper does not mutate frozen content', JSON.stringify(intro), before);
  topic.cards.filter(function (c) { return !c.intro; }).forEach(function (card) {
    eq('A4 ' + card.id + ' has a phrase-specific audio name',
       audioName('Play Polish pronunciation', card.pl), 'Play Polish pronunciation: ' + card.pl);
  });
});

var linkTag = tagFor('ytLink');
ok('A5 podcast destination remains a normal anchor', /^<a\b/.test(linkTag));
eq('A5 external target is unchanged', attr(linkTag, 'target'), '_blank');
eq('A5 external rel is unchanged', attr(linkTag, 'rel'), 'noopener noreferrer');
eq('A5 anchor has no script navigation', attr(linkTag, 'onclick'), null);

// Execute the shipping inactive-face helper with a podcast-shaped card.
var syncFaces = (new Function(extractFunction(INDEX, 'ppSyncFlipFaces') + '\nreturn ppSyncFlipFaces;'))();
var flip = new El('flip'), front = new El('front'), back = new El('back');
front.inert = false; back.inert = false; flip.faces = [front, back];
syncFaces(flip);
eq('B1 only the front podcast face is exposed initially',
   [front.getAttribute('aria-hidden'), front.inert, back.getAttribute('aria-hidden'), back.inert],
   [null, false, 'true', true]);
flip.classList.add('flipped'); syncFaces(flip);
eq('B1 only the back podcast face is exposed after flip',
   [front.getAttribute('aria-hidden'), front.inert, back.getAttribute('aria-hidden'), back.inert],
   ['true', true, null, false]);

// Execute the shipping startRound branch over every real episode. Stubs own only
// unrelated distractor/scoring behavior; this proves podcast eligibility and the
// listen/multiple-choice format boundary without reimplementing startRound.
var startRoundSource = extractFunction(INDEX, 'startRound');
topics.forEach(function (topic) {
  var R = {}, dom = { rTitle: new El('rTitle'), rSub: new El('rSub') }, renders = 0, shown = [];
  dom.rTitle.textContent = ''; dom.rSub.textContent = '';
  function byId(id) { return dom[id] || (dom[id] = new El(id)); }
  var run = (new Function('$', 'R', 'LEVELS', 'stopAllAudio', 'ppEligibleFor', 'poolFor',
    'gShuffle', 'rBuildOptions', 'show', 'rRender', startRoundSource + '\nreturn startRound;'))(
      byId, R, [{ level: 'Podcasts', topics: [topic] }], function () {},
      function (card, activity) { return !card.intro && (activity === 'listen' || activity === 'mixed'); },
      function () { return []; }, function (items) { return items.slice(); },
      function () { return []; }, function (screen) { shown.push(screen); }, function () { renders++; }
    );
  run(0, 0);
  eq('C1 ' + topic.id + ' excludes its intro from questions', R.originalTotal,
     Math.min(15, topic.cards.length - 1));
  ok('C1 ' + topic.id + ' uses recognition formats only',
     R.qs.length > 0 && R.qs.every(function (q) { return q.fmt === 'listen' || q.fmt === 'mc'; }));
  ok('C1 ' + topic.id + ' never introduces typing',
     R.qs.every(function (q) { return q.fmt !== 'type'; }));
  eq('C2 ' + topic.id + ' exposes podcast prompt context', dom.rSub.textContent, 'Podcast · Mixed quiz');
  eq('C2 ' + topic.id + ' preserves the episode title', dom.rTitle.textContent, topic.name);
  eq('C2 ' + topic.id + ' enters and renders once', [shown, renders], [['round'], 1]);
});

// Execute the shipping readiness and replay functions to prove episode-specific
// names without revealing the answer in a listening prompt.
var sampleTopic = topics[0], sampleIntro = sampleTopic.cards.filter(function (c) { return c.intro; })[0];
var sampleCard = sampleTopic.cards.filter(function (c) { return !c.intro; })[0];
var R = { li: 0, ti: 0, i: 0, originalTotal: 1,
          qs: [{ c: sampleCard, fmt: 'listen', requeued: false }] };
var round = new El('round'); round.classList.add('active');
var play = new El('rPlay'), dom = { round: round, rPlay: play };
function byId(id) { return dom[id]; }
var readiness = (new Function('$', 'R', 'LEVELS', 'audioManifestStatus',
  extractFunction(INDEX, 'syncRoundAudioReadiness') + '\nreturn syncRoundAudioReadiness;'))(
    byId, R, [{ topics: [sampleTopic] }], 'ready');
readiness();
ok('D1 ready podcast audio is enabled', play.disabled === false);
ok('D1 initial name identifies the episode without the hidden answer',
   play.getAttribute('aria-label').indexOf(sampleIntro.en) !== -1 &&
   play.getAttribute('aria-label').indexOf(sampleCard.pl) === -1);
var spoken = [];
var replay = (new Function('$', 'R', 'LEVELS', 'audioManifestStatus', 'speakCardMain', 'rReviewPos', 'rOriginalTotal',
  extractFunction(INDEX, 'rPlayCurrent') + '\nreturn rPlayCurrent;'))(
    byId, R, [{ topics: [sampleTopic] }], 'ready', function (card) { spoken.push(card.id); },
    function () { return { at: 1, total: 1 }; }, function () { return 1; });
replay();
eq('D2 one activation starts one podcast clip', spoken, [sampleCard.id]);
ok('D2 replay name identifies episode and position',
   play.getAttribute('aria-label').indexOf(sampleIntro.en) !== -1 &&
   /question 1 of 1/.test(play.getAttribute('aria-label')));

console.log('Podcast accessibility tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
LOG.forEach(function (line) { console.log(line); });
if (FAIL) throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed');
