// Priority 7 Phase 5-A cross-language release bridge.
//
// This suite asks the PYTHON release-authoritative path for a public runtime
// document built from the synthetic Phase 5-A editorial fixture, and then feeds
// those exact bytes to the SHIPPING JavaScript consumer in pp-verb-patterns.js.
// Nothing is hand-rewritten into a loader fixture in between, so a schema drift
// between the two languages fails here rather than at a real release.
//
// It performs no network I/O, writes only into a temporary directory, and makes
// no linguistic, review or release-authority claim. Every lemma, sentence,
// reviewer and author involved is invented and marked TEST-ONLY.
// Runs in JavaScriptCore:
//   osascript -l JavaScript tests/test_priority7_phase5a_bridge.js

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
function shell(command) {
  var task = $.NSTask.alloc.init;
  task.launchPath = '/bin/sh';
  task.arguments = ['-c', command];
  var pipe = $.NSPipe.pipe;
  task.standardOutput = pipe;
  task.standardError = pipe;
  task.launch;
  var data = pipe.fileHandleForReading.readDataToEndOfFile;
  task.waitUntilExit;
  return {
    status: task.terminationStatus,
    out: ObjC.unwrap($.NSString.alloc.initWithDataEncoding(
      data, $.NSUTF8StringEncoding))
  };
}

// The released runtime is pinned by digest, so a byte of drift in the shipping
// artifact is reported here rather than being absorbed by a looser check.
function sha256OfFile(path) {
  var result = shell("/usr/bin/shasum -a 256 " + JSON.stringify(path));
  return result.status === 0 ? String(result.out).trim().split(/\s+/)[0] : null;
}
function countOf(haystack, needle) {
  var count = 0, at = 0;
  while ((at = haystack.indexOf(needle, at)) !== -1) { count++; at += needle.length; }
  return count;
}

var ROOT = resolveRoot();
var LOADER_SOURCE = readFile(ROOT + 'pp-verb-patterns.js');
(0, eval)(LOADER_SOURCE);

// JavaScriptCore's osascript host does not drain native Promise jobs; this is
// the same deterministic stand-in tests/test_priority7_release_loader.js uses.
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

// --------------------------------------------------------------------------
// A. Ask Python's release-authoritative path for the runtime bytes.
// --------------------------------------------------------------------------

// freeze_editorial -> validate_frozen_release -> verified_runtime_from_frozen.
// The standalone projector is deliberately NOT used: it is not release
// authoritative, and this suite is about the authoritative bridge.
var PRODUCER = [
  'import json, sys',
  'from datetime import date',
  'from priority7_tooling import (RepositoryIndex, ValidationContext,',
  '    freeze_editorial, validate_frozen_release, verified_runtime_from_frozen)',
  'raw = json.load(open("tests/fixtures/priority7/synthetic-release-editorial.json", encoding="utf-8"))',
  'ids = raw["syntheticIdentities"]',
  'ctx = ValidationContext(source_registry=ids["sourceRegistry"],',
  '    reviewer_registry=ids["reviewerRegistry"],',
  '    author_registry=ids["authorRegistry"],',
  '    repository_index=RepositoryIndex.from_sources(raw["syntheticRepositorySources"]),',
  '    today=date.fromisoformat(raw["reviewContextDate"]))',
  'frozen = freeze_editorial(raw["editorial"], 1, ctx)',
  'assert not validate_frozen_release(frozen)',
  'runtime = verified_runtime_from_frozen(frozen)',
  'sys.stdout.write(json.dumps(runtime, ensure_ascii=False))'
].join('\n');

var produced = shell(
  'cd ' + JSON.stringify(ROOT) + " && python3 -c '" +
  PRODUCER.replace(/'/g, "'\\''") + "'");

ok('A1 the Python release-authoritative path produced a runtime',
   produced.status === 0);
if (produced.status !== 0) {
  console.log('Priority 7 Phase 5-A bridge tests: 0 passed, 1 failed.');
  console.log('  producer stderr: ' + produced.out);
  throw new Error('TESTS FAILED: the Python producer did not run');
}

var RUNTIME = JSON.parse(produced.out);
eq('A2 the produced envelope is exactly the closed public contract',
   Object.keys(RUNTIME).sort(), ['formatVersion', 'lemmas', 'patternDataRevision']);
eq('A3 the first synthetic release carries revision 1',
   RUNTIME.patternDataRevision, 1);

// Write the produced bytes to a temporary file so the transport reads a real
// document from disk, exactly as a release would. Never into the repository.
var TEMPORARY = ObjC.unwrap($.NSTemporaryDirectory()) +
  'p7-phase5a-bridge-' + Date.now() + '/';
$.NSFileManager.defaultManager
  .createDirectoryAtPathWithIntermediateDirectoriesAttributesError(
    TEMPORARY, true, $(), null);
var RUNTIME_PATH = TEMPORARY + 'synthetic-runtime.json';
$(produced.out).writeToFileAtomicallyEncodingError(
  RUNTIME_PATH, true, $.NSUTF8StringEncoding, null);
ok('A4 the generated runtime lives outside the repository',
   RUNTIME_PATH.indexOf(ROOT) !== 0);

// --------------------------------------------------------------------------
// B. Drive the shipping transport and consumer over those bytes.
// --------------------------------------------------------------------------

function load(document) {
  var settled = null;
  var calls = [];
  function request(url, options) {
    calls.push({ url: url, options: options });
    return Immediate.resolve({
      ok: true,
      json: function () { return Immediate.resolve(document); }
    });
  }
  PP_VERB_PATTERNS.reset();
  PP_VERB_PATTERNS.loadRuntimeDocument(request, 'test-only://phase5a/runtime.json')
    .then(function (value) { settled = value; },
          function () { settled = 'rejected'; });
  return { settled: settled, calls: calls,
    available: PP_VERB_PATTERNS.available };
}

var fromDisk = JSON.parse(readFile(RUNTIME_PATH));
eq('B1 the bytes read back from disk are the bytes Python emitted',
   fromDisk, RUNTIME);

var accepted = load(clone(fromDisk));
eq('B2 the shipping loader accepts the release-authoritative projection',
   accepted.settled, true);
eq('B3 PP_VERB_PATTERNS.available is true after acceptance',
   PP_VERB_PATTERNS.available, true);
eq('B4 exactly one no-store transport call was made',
   [accepted.calls.length, accepted.calls[0].options.cache], [1, 'no-store']);
eq('B5 summary derives from the accepted document',
   PP_VERB_PATTERNS.summary(), { lemmas: 1, patterns: 2 });
eq('B6 the count label derives from the accepted document',
   PP_VERB_PATTERNS.countLabel(), '1 verb · 2 patterns');
eq('B7 the index derives one synthetic lemma carrying two patterns',
   PP_VERB_PATTERNS.index().map(function (row) {
     return [row.lemma, row.patternCount];
   }), [['ZORBULATE — TEST-ONLY SYNTHETIC', 2]]);
eq('B8 filters derive from the projected complements',
   PP_VERB_PATTERNS.filters().map(function (item) { return item.id; }),
   ['all', 'accusative', 'no-case']);
eq('B9 the projected contentRef resolves the card-back cross-link',
   PP_VERB_PATTERNS.cardSupport('p7-phase5a-synthetic-card-001').state,
   'doorway');
ok('B10 no private key survives anywhere in the accepted document',
   PP_VERB_PATTERNS.__holdsPrivateKeyForTest(fromDisk) === false);
eq('B11 the unreviewed synthetic lemma never reached the runtime',
   produced.out.indexOf('quuxify'), -1);

// --------------------------------------------------------------------------
// C. Cross-language contract parity (§22).
// --------------------------------------------------------------------------

var PARITY = [
  'import json',
  'from priority7_tooling import (ACTIVITY_KEYS, CASE_IDS, CEFR_LEVELS,',
  '    CLAUSE_KINDS, COMPLEMENT_TYPES, CONTENT_KINDS, CONTENT_PURPOSES,',
  '    FORMAT_VERSION, PRIVATE_RUNTIME_KEYS, REGISTERS, RELATION_TYPES,',
  '    ROLES, USAGE_PRIORITIES)',
  'print(json.dumps({',
  '    "formatVersion": FORMAT_VERSION,',
  '    "privateKeys": sorted(PRIVATE_RUNTIME_KEYS),',
  '    "caseIds": sorted(CASE_IDS),',
  '    "complementTypes": sorted(COMPLEMENT_TYPES),',
  '    "relationTypes": sorted(RELATION_TYPES),',
  '    "roles": sorted(ROLES),',
  '    "activityKeys": sorted(ACTIVITY_KEYS),',
  '    "cefrLevels": sorted(CEFR_LEVELS),',
  '    "usagePriorities": sorted(USAGE_PRIORITIES),',
  '    "registers": sorted(REGISTERS),',
  '    "clauseKinds": sorted(CLAUSE_KINDS),',
  '    "contentKinds": sorted(CONTENT_KINDS),',
  '    "contentPurposes": sorted(CONTENT_PURPOSES)}))'
].join('\n');

var parityRun = shell(
  'cd ' + JSON.stringify(ROOT) + " && python3 -c '" +
  PARITY.replace(/'/g, "'\\''") + "'");
ok('C1 the Python contract constants are readable', parityRun.status === 0);
var PY = parityRun.status === 0 ? JSON.parse(parityRun.out) : {};

// The JS side keeps these as ordered arrays inside the module closure. They are
// read back out of the source so this stays a parity check on the real values,
// not on a copy maintained here.
function jsArray(name) {
  var marker = 'var ' + name + ' = [';
  var start = LOADER_SOURCE.indexOf(marker);
  if (start === -1) return null;
  var open = LOADER_SOURCE.indexOf('[', start);
  var close = LOADER_SOURCE.indexOf('];', open);
  var body = LOADER_SOURCE.slice(open, close + 1)
    .replace(/\/\*[\s\S]*?\*\//g, '')
    .replace(/\n/g, ' ');
  return JSON.parse(body);
}

eq('C2 FORMAT_VERSION agrees across both languages',
   PP_VERB_PATTERNS.FORMAT_VERSION, PY.formatVersion);
eq('C3 the private-key rejection list is an exact mirror',
   jsArray('PRIVATE_KEYS').slice().sort(), PY.privateKeys);
eq('C4 the seven case identifiers agree',
   PP_VERB_PATTERNS.CASE_ORDER.slice().sort(), PY.caseIds);
eq('C5 complement types agree',
   jsArray('COMPLEMENT_TYPES').slice().sort(), PY.complementTypes);
eq('C6 relation types agree',
   jsArray('RELATION_TYPES').slice().sort(), PY.relationTypes);
eq('C7 roles agree', jsArray('ROLES').slice().sort(), PY.roles);
eq('C8 activity keys agree',
   jsArray('ACTIVITY_KEYS').slice().sort(), PY.activityKeys);
eq('C9 CEFR levels agree',
   jsArray('CEFR_LEVELS').slice().sort(), PY.cefrLevels);
eq('C10 usage priorities agree',
   jsArray('USAGE_PRIORITIES').slice().sort(), PY.usagePriorities);
eq('C11 registers agree', jsArray('REGISTERS').slice().sort(), PY.registers);
eq('C12 clause kinds agree',
   jsArray('CLAUSE_KINDS').slice().sort(), PY.clauseKinds);
eq('C13 content kinds agree',
   jsArray('CONTENT_KINDS').slice().sort(), PY.contentKinds);
eq('C14 content purposes agree',
   jsArray('CONTENT_PURPOSES').slice().sort(), PY.contentPurposes);
// The JS side intentionally accepts a NARROWER teaching-status set than the
// editorial enum: "deferred" is an editorial state that must never project.
eq('C15 the runtime teaching statuses are the projectable subset',
   jsArray('TEACHING_STATUSES').slice().sort(),
   ['active-production', 'recognition-only']);

// --------------------------------------------------------------------------
// D. The bridge refuses everything that is not the release-authoritative shape.
// --------------------------------------------------------------------------

function refuses(name, mutate) {
  var candidate = clone(fromDisk);
  mutate(candidate);
  var attempt = load(candidate);
  eq(name, [attempt.settled, PP_VERB_PATTERNS.available], [false, false]);
}

refuses('D1 an injected private reviewState is refused', function (value) {
  value.lemmas[0].meanings[0].patterns[0].reviewState = 'approved';
});
refuses('D2 injected private evidence is refused', function (value) {
  value.lemmas[0].meanings[0].patterns[0].evidence = [{ sourceId: 'x' }];
});
refuses('D3 a private key at depth is refused', function (value) {
  value.lemmas[0].meanings[0].key = 'test-object';
});
refuses('D4 a nonrelease wrapper is not the public shape', function (value) {
  value.artifactStatus = 'priority-7-runtime-projection-nonrelease-fixture';
  value.releaseAuthorized = false;
});
refuses('D5 an unknown envelope key is refused whole', function (value) {
  value.releaseAuthorized = true;
});
refuses('D6 a malformed nested complement is refused', function (value) {
  value.lemmas[0].meanings[0].patterns[0].complements[0].case = 'not-a-case';
});
refuses('D7 a null nested pattern array is refused', function (value) {
  value.lemmas[0].meanings[0].patterns = null;
});
refuses('D8 revision 0 is refused', function (value) {
  value.patternDataRevision = 0;
});
refuses('D9 a non-integer revision is refused', function (value) {
  value.patternDataRevision = 1.5;
});
refuses('D10 a drifted formatVersion is refused', function (value) {
  value.formatVersion = 2;
});
refuses('D11 an empty lemma array is refused', function (value) {
  value.lemmas = [];
});

// A refused candidate must not disturb an already-accepted good value.
load(clone(fromDisk));
var goodSummary = PP_VERB_PATTERNS.summary();
var hostile = clone(fromDisk);
hostile.lemmas[0].meanings[0].patterns[0].reviewState = 'approved';
var rejected = PP_VERB_PATTERNS.__acceptForTest(hostile);
eq('D12 a rejected candidate leaves the last good value intact',
   [rejected, PP_VERB_PATTERNS.available, PP_VERB_PATTERNS.summary()],
   [false, true, goodSummary]);

// --------------------------------------------------------------------------
// E. The rehearsal leaves no release artifact behind.
// --------------------------------------------------------------------------

var fm = $.NSFileManager.defaultManager;
// SUPERSEDED by Priority 7 Phase 4F-I1, which released the official runtime.
// What this rehearsal still proves is that IT left nothing behind: the only
// document at that path is the pinned I1 release artifact, byte for byte, and
// the only reference to it in the shell is the one production URL constant.
// The synthetic bridge wrote to a temporary directory and touched neither.
var I1_RUNTIME_SHA256 =
  'd7911b2a4597147f3f0336c9b0cd154d1bec390d246fc4f33620b7bcf46460ed';
ok('E1 the only content/verb-patterns.json is the pinned I1 release artifact',
   fm.fileExistsAtPath(ROOT + 'content/verb-patterns.json') &&
   sha256OfFile(ROOT + 'content/verb-patterns.json') === I1_RUNTIME_SHA256);
eq('E2 the content directory holds exactly that one released document',
   ObjC.deepUnwrap(fm.contentsOfDirectoryAtPathError(ROOT + 'content', null))
     .slice().sort(), ['verb-patterns.json']);
eq('E3 ordinary startup fetches that runtime and no other',
   [countOf(readFile(ROOT + 'index.html'), 'content/verb-patterns.json'),
    countOf(readFile(ROOT + 'index.html'), 'loadRuntimeDocument')], [1, 1]);

fm.removeItemAtPathError(TEMPORARY, null);
ok('E4 the temporary bridge directory was cleaned up',
   !fm.fileExistsAtPath(RUNTIME_PATH));

PP_VERB_PATTERNS.reset();
eq('E5 the suite ends with the ordinary dormant learner startup contract',
   [PP_VERB_PATTERNS.available, PP_VERB_PATTERNS.index().length], [false, 0]);

console.log('Priority 7 Phase 5-A bridge tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
console.log('  [info] the runtime under test is produced by the real Python');
console.log('         release-authoritative path, not hand-authored here');
console.log('  [info] synthetic/test-only data; no network, no approval, no release');
LOG.forEach(function (line) { console.log('  ' + line); });
if (FAIL > 0) throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed');
