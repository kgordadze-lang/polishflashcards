// Priority 7 Phase 3F-A release-path rehearsal.
//
// This suite executes the dormant shipping transport and public-shape consumer
// against an obviously synthetic, bare public-runtime fixture. It performs no
// network I/O and makes no linguistic, review or release-authority claim.
// Runs in JavaScriptCore:
//   osascript -l JavaScript tests/test_priority7_release_loader.js

ObjC.import('Foundation');

function readFile(path) {
  var value = $.NSString.stringWithContentsOfFileEncodingError(
    path, $.NSUTF8StringEncoding, null);
  return ObjC.unwrap(value);
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
var SW = readFile(ROOT + 'sw.js');
var LOADER_SOURCE = readFile(ROOT + 'pp-verb-patterns.js');
(0, eval)(LOADER_SOURCE);
var FIXTURE_PATH = 'tests/fixtures/priority7/release-runtime-fixture.json';
var FIXTURE = JSON.parse(readFile(ROOT + FIXTURE_PATH));

var PASS = 0, FAIL = 0, LOG = [];
function ok(name, condition) {
  if (condition) PASS++;
  else { FAIL++; LOG.push('FAIL: ' + name); }
}
function eq(name, actual, expected) {
  var a = JSON.stringify(actual), e = JSON.stringify(expected);
  ok(name + (a === e ? '' : '  (got ' + a + ', want ' + e + ')'), a === e);
}
function clone(value) { return JSON.parse(JSON.stringify(value)); }
function countOf(haystack, needle) {
  var count = 0, at = 0;
  while ((at = haystack.indexOf(needle, at)) !== -1) { count++; at += needle.length; }
  return count;
}

// JavaScriptCore's osascript host does not drain native Promise jobs. This
// deterministic Promise stand-in models only the assimilation the shipping
// primitive uses; a separate real-browser check owns the native Promise proof.
function Immediate(state, value) { this.state = state; this.value = value; }
Immediate.resolve = function (value) {
  return value instanceof Immediate ? value : new Immediate('fulfilled', value);
};
Immediate.reject = function (value) { return new Immediate('rejected', value); };
Immediate.prototype.then = function (onFulfilled, onRejected) {
  var callback = this.state === 'fulfilled' ? onFulfilled : onRejected;
  if (typeof callback !== 'function') return this;
  try {
    var next = callback(this.value);
    return next instanceof Immediate ? next : Immediate.resolve(next);
  } catch (error) {
    return Immediate.reject(error);
  }
};
Promise = Immediate;
function resultOf(value) {
  if (!(value instanceof Immediate)) return value;
  if (value.state === 'rejected') throw value.value;
  return value.value;
}

function makeResponse(options) {
  options = options || {};
  if (options.responseGetterThrows) {
    var hostile = {};
    Object.defineProperty(hostile, 'ok', { get: function () {
      throw new Error('synthetic response getter throw');
    }});
    return hostile;
  }
  return {
    ok: options.ok === undefined ? true : options.ok,
    status: options.status === undefined ? 200 : options.status,
    json: options.noJson ? undefined : function () {
      if (options.jsonThrows) throw new Error('synthetic parse throw');
      if (options.jsonRejects) return Immediate.reject(new Error('synthetic invalid JSON'));
      if (options.plainBody) return clone(options.document);
      if (options.rawBody) return Immediate.resolve(options.document);
      return Immediate.resolve(clone(options.document));
    }
  };
}
function loadAttempt(options) {
  options = options || {};
  var calls = [];
  function request(url, requestOptions) {
    calls.push({ url: url, options: requestOptions });
    if (options.requestThrows) throw new Error('synthetic request throw');
    if (options.networkRejects) return Immediate.reject(new Error('synthetic network rejection'));
    if (options.nonThenableResponse) return makeResponse(options);
    return Immediate.resolve(makeResponse(options));
  }
  var returned = PP_VERB_PATTERNS.loadRuntimeDocument(
    request, options.url || 'synthetic-test-only://priority7-runtime');
  return {
    result: resultOf(returned), calls: calls,
    thenable: !!returned && typeof returned.then === 'function'
  };
}
function snapshot() {
  return JSON.stringify({
    available: PP_VERB_PATTERNS.available,
    summary: PP_VERB_PATTERNS.summary(),
    index: PP_VERB_PATTERNS.index(),
    filters: PP_VERB_PATTERNS.filters(),
    first: PP_VERB_PATTERNS.lemma(0),
    second: PP_VERB_PATTERNS.lemma(1)
  });
}
function freshFailure(options) {
  PP_VERB_PATTERNS.reset();
  var attempt = loadAttempt(options);
  return [attempt.result, attempt.calls.length, PP_VERB_PATTERNS.available,
          PP_VERB_PATTERNS.summary(), PP_VERB_PATTERNS.index().length];
}

// A. Dormancy at module scope, and the ONE production activation.
//
// UPDATED by Priority 7 Phase 4F-I1, the atomic release that activates this
// path. The helper itself is unchanged and still starts dormant, owns no URL
// and never reaches for a global fetch. What moved is the shell: it now makes
// exactly one call, at one call site, to one URL. Every count below is an
// exact pin, so a second activation, a different or additional runtime URL, a
// preview/fixture URL or an extra transport still fails here.
eq('A1 module evaluation starts unavailable and performs no request',
   [PP_VERB_PATTERNS.available, PP_VERB_PATTERNS.summary()],
   [false, { lemmas: 0, patterns: 0 }]);
eq('A1 ordinary startup invokes the primitive exactly once, at one URL',
   [countOf(INDEX, 'loadRuntimeDocument'), countOf(INDEX, 'content/verb-patterns.json'),
    countOf(INDEX, 'fetch(')], [1, 1, 3]);
eq('A1 the activation is the shipping consumer, called with the official URL',
   [countOf(INDEX, 'const PRIORITY7_RUNTIME_URL = "./content/verb-patterns.json";'),
    countOf(INDEX, 'PP_VERB_PATTERNS.loadRuntimeDocument('),
    countOf(INDEX, 'PRIORITY7_RUNTIME_URL')], [1, 1, 2]);
eq('A1 no preview, fixture, editorial or query-switch alternative exists',
   ['verb-patterns.preview', 'runtime-fixture', 'editorial/', 'tests/fixtures',
    '__acceptForTest', 'URLSearchParams', 'searchParams', '?fixture',
    'localStorage.getItem("priority7', 'verb-patterns.json?']
     .filter(function (token) { return INDEX.indexOf(token) !== -1; }), []);
eq('A1 the helper owns no runtime URL and never reaches for global fetch',
   [countOf(LOADER_SOURCE, 'content/verb-patterns.json'), countOf(LOADER_SOURCE, 'fetch('),
    countOf(LOADER_SOURCE, 'request(url, { cache: "no-store" })')], [0, 0, 1]);
eq('A1 no query, storage or developer switch can activate the transport',
   ['URLSearchParams', 'location.search', 'localStorage', 'sessionStorage', 'indexedDB',
    '?fixture', 'setInterval', 'setTimeout'].filter(function (token) {
      return LOADER_SOURCE.indexOf(token) !== -1 ||
             (token !== 'setTimeout' && INDEX.indexOf(token + 'priority7') !== -1);
   }), []);
eq('A2 neither service worker nor shell knows the fixture path',
   [countOf(SW, FIXTURE_PATH), countOf(INDEX, FIXTURE_PATH)], [0, 0]);
// UPDATED by Priority 7 Phase 4F-I1: the worker now carries the runtime as a
// REQUIRED precache entry beside its helper, and classifies it network-first
// rather than sweeping it into the cache-first static inventory.
eq('A2 production caching carries the runtime and the helper, network-first',
   [countOf(SW, '"./content/verb-patterns.json"'),
    countOf(SW, '"./pp-verb-patterns.js"'),
    countOf(SW, 'const PATTERN_RUNTIME_PATH = SCOPE_PATH + "content/verb-patterns.json";'),
    countOf(SW, 'if (category === "pattern-runtime") { networkFirst(e, key, false); return; }'),
    countOf(SW, 'path !== PATTERN_RUNTIME_PATH')], [1, 1, 1, 1, 1]);

// B. Synthetic bare-public fixture contract.
eq('B1 fixture has exactly the closed public envelope',
   Object.keys(FIXTURE).sort(), ['formatVersion', 'lemmas', 'patternDataRevision']);
eq('B1 fixture uses the explicit test-only revision and two non-Polish lemmas',
   [FIXTURE.patternDataRevision, FIXTURE.lemmas.map(function (lemma) {
     return lemma.canonicalLemma;
   })], [424242, ['quuxify', 'zorbulate']]);
eq('B1 fixture has no wrapper or authority marker',
   ['artifactStatus', 'releaseAuthorized', 'runtimeProjection'].filter(function (key) {
     return Object.prototype.hasOwnProperty.call(FIXTURE, key);
   }), []);
ok('B1 fixture visibly marks every learner-facing phrase as test-only',
   JSON.stringify(FIXTURE).indexOf('TEST-ONLY') !== -1);

// C. Successful HTTP-like load and derived in-memory views.
PP_VERB_PATTERNS.reset();
var successCandidate = clone(FIXTURE);
var success = loadAttempt({ document: successCandidate, rawBody: true });
eq('C1 an explicitly successful response parses and is accepted', success.result, true);
eq('C1 the successful branch returns Promise-like Boolean settlement',
   [success.thenable, typeof success.result], [true, 'boolean']);
eq('C1 exactly one request is made with no-store and no retry', success.calls,
   [{ url: 'synthetic-test-only://priority7-runtime', options: { cache: 'no-store' } }]);
eq('C1 availability switches only after the whole candidate is accepted',
   [PP_VERB_PATTERNS.available, PP_VERB_PATTERNS.hasIndex(),
    PP_VERB_PATTERNS.summary(), PP_VERB_PATTERNS.countLabel()],
   [true, true, { lemmas: 2, patterns: 2 }, '2 verbs · 2 patterns']);
eq('C1 index and filters derive from the accepted synthetic runtime',
   [PP_VERB_PATTERNS.index().length,
    PP_VERB_PATTERNS.filters().map(function (item) { return item.id; }),
    PP_VERB_PATTERNS.rows('accusative').length,
    PP_VERB_PATTERNS.rows('dative').length],
   [2, ['all', 'accusative', 'no-case'], 1, 0]);
ok('C1 hostile strings remain unparsed data in the returned view',
   PP_VERB_PATTERNS.index()[0].lemma.indexOf('<img') !== -1 &&
   JSON.stringify(PP_VERB_PATTERNS.lemma(0)).indexOf('<script>') !== -1);
var detachedSnapshot = snapshot();
successCandidate.lemmas[0].displayLemma = 'MUTATED AFTER ACCEPTANCE';
successCandidate.lemmas[0].meanings[0].patterns[0].learnerExplanationEn =
  'MUTATED AFTER ACCEPTANCE';
eq('C1 accepted state is detached from later caller mutation', snapshot(), detachedSnapshot);
eq('C1 the primitive and consumer expose no persistence API',
   ['localStorage', 'sessionStorage', 'indexedDB', 'document.cookie'].filter(function (token) {
     return LOADER_SOURCE.indexOf(token) !== -1;
   }), []);

// D. Transport / response / parsing failure matrix, each from no prior state.
eq('D1 synchronous request rejection fails closed', freshFailure({ requestThrows: true }),
   [false, 1, false, { lemmas: 0, patterns: 0 }, 0]);
eq('D1 asynchronous network rejection fails closed', freshFailure({ networkRejects: true }),
   [false, 1, false, { lemmas: 0, patterns: 0 }, 0]);
eq('D2 HTTP 404 fails closed', freshFailure({ ok: false, status: 404, document: FIXTURE }),
   [false, 1, false, { lemmas: 0, patterns: 0 }, 0]);
eq('D2 HTTP 500 fails closed', freshFailure({ ok: false, status: 500, document: FIXTURE }),
   [false, 1, false, { lemmas: 0, patterns: 0 }, 0]);
eq('D2 a truthy non-Boolean success marker is not accepted',
   freshFailure({ ok: 1, status: 200, document: FIXTURE }),
   [false, 1, false, { lemmas: 0, patterns: 0 }, 0]);
eq('D3 rejected JSON parsing fails closed', freshFailure({ jsonRejects: true }),
   [false, 1, false, { lemmas: 0, patterns: 0 }, 0]);
eq('D3 thrown JSON parsing fails closed', freshFailure({ jsonThrows: true }),
   [false, 1, false, { lemmas: 0, patterns: 0 }, 0]);
eq('D3 a response without json() fails closed', freshFailure({ noJson: true }),
   [false, 1, false, { lemmas: 0, patterns: 0 }, 0]);
eq('D3 a non-Promise body fails closed rather than creating a test-only path',
   freshFailure({ plainBody: true, document: FIXTURE }),
   [false, 1, false, { lemmas: 0, patterns: 0 }, 0]);
eq('D3 a non-Promise response fails closed',
   freshFailure({ nonThenableResponse: true, document: FIXTURE }),
   [false, 1, false, { lemmas: 0, patterns: 0 }, 0]);
eq('D3 a throwing response member is contained and resolves false',
   freshFailure({ responseGetterThrows: true }),
   [false, 1, false, { lemmas: 0, patterns: 0 }, 0]);
PP_VERB_PATTERNS.reset();
var missingRequest = PP_VERB_PATTERNS.loadRuntimeDocument(null, 'x');
var missingUrl = PP_VERB_PATTERNS.loadRuntimeDocument(
  function () { throw new Error('must not run'); }, '');
eq('D4 missing request dependency or URL resolves false without a call',
   [resultOf(missingRequest), resultOf(missingUrl), PP_VERB_PATTERNS.available],
   [false, false, false]);
eq('D4 both guard branches return Promise-like values',
   [typeof missingRequest.then, typeof missingUrl.then], ['function', 'function']);
eq('D5 success, throws, rejection, malformed response and parse failure are all thenable',
   [
     loadAttempt({ document: FIXTURE }).thenable,
     loadAttempt({ requestThrows: true }).thenable,
     loadAttempt({ networkRejects: true }).thenable,
     loadAttempt({ ok: false, status: 500, document: FIXTURE }).thenable,
     loadAttempt({ noJson: true }).thenable,
     loadAttempt({ responseGetterThrows: true }).thenable,
     loadAttempt({ jsonRejects: true }).thenable,
     loadAttempt({ nonThenableResponse: true, document: FIXTURE }).thenable,
     loadAttempt({ plainBody: true, document: FIXTURE }).thenable
   ], [true, true, true, true, true, true, true, true, true]);

// E. Closed-envelope and nested public validation failures.
function invalidDocument(mutate) {
  var document = clone(FIXTURE);
  mutate(document);
  return freshFailure({ document: document });
}
eq('E1 wrong top-level type fails closed', freshFailure({ document: [] }),
   [false, 1, false, { lemmas: 0, patterns: 0 }, 0]);
eq('E1 every missing required envelope key fails closed',
   ['formatVersion', 'patternDataRevision', 'lemmas'].map(function (key) {
     return invalidDocument(function (document) { delete document[key]; })[0];
   }), [false, false, false]);
eq('E1 an additional unknown top-level key fails closed',
   invalidDocument(function (document) { document.unexpected = true; }),
   [false, 1, false, { lemmas: 0, patterns: 0 }, 0]);
eq('E1 an empty runtime is invalid under the locked non-empty contract',
   invalidDocument(function (document) { document.lemmas = []; }),
   [false, 1, false, { lemmas: 0, patterns: 0 }, 0]);
eq('E2 invalid nested lemma structure fails the whole candidate',
   invalidDocument(function (document) { document.lemmas[0].canonicalLemma = ''; }),
   [false, 1, false, { lemmas: 0, patterns: 0 }, 0]);
eq('E2 invalid nested meaning structure fails the whole candidate',
   invalidDocument(function (document) { document.lemmas[0].meanings[0].patterns = {}; }),
   [false, 1, false, { lemmas: 0, patterns: 0 }, 0]);
eq('E2 invalid nested pattern structure fails the whole candidate',
   invalidDocument(function (document) {
     document.lemmas[0].meanings[0].patterns[0].relationType = 'test-mystery';
   }), [false, 1, false, { lemmas: 0, patterns: 0 }, 0]);
eq('E2 an unknown nested pattern key fails the whole candidate',
   invalidDocument(function (document) {
     document.lemmas[0].meanings[0].patterns[0].surprise = 'no';
   }), [false, 1, false, { lemmas: 0, patterns: 0 }, 0]);

// F. One private/editorial key anywhere rejects the entire candidate.
var privateBlock = LOADER_SOURCE.slice(LOADER_SOURCE.indexOf('var PRIVATE_KEYS = ['));
privateBlock = privateBlock.slice(privateBlock.indexOf('[') + 1, privateBlock.indexOf(']'));
var PRIVATE_KEYS = JSON.parse('[' + privateBlock.replace(/\s+/g, ' ') + ']');
eq('F1 loader retains the one shared 26-key private rejection contract', PRIVATE_KEYS.length, 26);
var directPrivateMisses = PRIVATE_KEYS.filter(function (key) {
  var nested = { publicLookingContainer: [{ deeper: {} }] };
  nested.publicLookingContainer[0].deeper[key] = 'TEST-ONLY private marker';
  return !PP_VERB_PATTERNS.__holdsPrivateKeyForTest(nested);
});
eq('F1 the defence-in-depth sweep directly recognizes all 26 keys when nested',
   directPrivateMisses, []);
eq('F1 the direct sweep does not confuse an unknown public-looking key with a private key',
   PP_VERB_PATTERNS.__holdsPrivateKeyForTest(
     { publicLookingContainer: [{ deeper: { surprise: 'TEST-ONLY' } }] }), false);
var privateAccepted = PRIVATE_KEYS.filter(function (key) {
  var document = clone(FIXTURE);
  document.lemmas[0].meanings[0].patterns[0][key] = 'TEST-ONLY private leak';
  PP_VERB_PATTERNS.reset();
  return loadAttempt({ document: document }).result;
});
eq('F1 every private/editorial field is rejected at nested depth', privateAccepted, []);
eq('F1 explicit root editorial and review envelopes are rejected',
   ['artifactStatus', 'evidence', 'reviewState', 'reviewerRef', 'authorRef',
    'sourceRegistry', 'editorialNotes'].map(function (key) {
      var document = clone(FIXTURE); document[key] = 'TEST-ONLY';
      PP_VERB_PATTERNS.reset(); return loadAttempt({ document: document }).result;
   }), [false, false, false, false, false, false, false]);

// G. Atomic replacement and revision semantics.
PP_VERB_PATTERNS.reset();
eq('G1 precondition accepts the full candidate', loadAttempt({ document: FIXTURE }).result, true);
var FULL_SNAPSHOT = snapshot();
var laterBad = clone(FIXTURE);
laterBad.lemmas[0].meanings[0].patterns[0].complements[0].case = 'partitive';
eq('G1 a later malformed candidate is rejected', loadAttempt({ document: laterBad }).result, false);
eq('G1 malformed rejection preserves the exact last valid in-memory views',
   snapshot(), FULL_SNAPSHOT);
eq('G1 a later network failure is contained',
   loadAttempt({ networkRejects: true }).result, false);
eq('G1 network rejection also preserves the exact accepted state', snapshot(), FULL_SNAPSHOT);

var replacement = clone(FIXTURE);
replacement.lemmas = [replacement.lemmas[1]];
eq('G2 a complete later valid candidate replaces state atomically',
   loadAttempt({ document: replacement }).result, true);
eq('G2 replacement contains only the new complete view, never a union',
   [PP_VERB_PATTERNS.summary(), PP_VERB_PATTERNS.index().map(function (row) { return row.lemma; })],
   [{ lemmas: 1, patterns: 1 }, ['zorbulate']]);

var lowerRevision = clone(FIXTURE);
lowerRevision.patternDataRevision = 1;
eq('G3 browser validation checks positive-integer type but compares no revision history',
   loadAttempt({ document: lowerRevision }).result, true);
eq('G3 no revision or monotonicity API is exposed in browser state',
   Object.keys(PP_VERB_PATTERNS).filter(function (key) {
     return /revision|monotonic|rollback/i.test(key);
   }), []);

// H. Failure UX/persistence constraints and final dormant state.
eq('H1 transport has no retry, polling, logging, DOM or storage machinery',
   ['setInterval', 'setTimeout', 'console.', 'document.get', 'document.create',
    'window.', 'localStorage', 'sessionStorage', 'indexedDB'].filter(function (token) {
      return LOADER_SOURCE.indexOf(token) !== -1;
   }), []);
eq('H1 transport function is exported once and the shell calls it exactly once',
   [countOf(LOADER_SOURCE, 'loadRuntimeDocument: loadRuntimeDocument'),
    countOf(INDEX, 'loadRuntimeDocument')], [1, 1]);
PP_VERB_PATTERNS.reset();
eq('H2 reset restores the ordinary learner startup contract',
   [PP_VERB_PATTERNS.available, PP_VERB_PATTERNS.index().length,
    PP_VERB_PATTERNS.filters().length], [false, 0, 0]);

console.log('Priority 7 Phase 3F-A release-loader tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
console.log('  [info] synthetic/test-only HTTP-like responses; no network, approval or release');
console.log('  [info] the dormant shipping transport and consumer execute exactly as shipped');
LOG.forEach(function (line) { console.log('  ' + line); });
if (FAIL > 0) throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed');
