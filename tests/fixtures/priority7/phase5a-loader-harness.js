// Priority 7 Phase 5-A cross-language loader harness (test-only, not shipped).
//
// Reads one synthetic public-runtime document produced by the Python
// release-authoritative path and drives the SHIPPING consumer in
// pp-verb-patterns.js over it, through the same dormant transport the
// application would use. It performs no network I/O, writes nothing, and makes
// no linguistic, review or release-authority claim.
//
// Usage:
//   osascript -l JavaScript tests/fixtures/priority7/phase5a-loader-harness.js \
//       <repository-root> <runtime-json-path> [mutation]
//
// It prints one JSON object on stdout describing what the shipping loader did.
// `mutation` is optional and lets a caller ask the harness to damage the parsed
// document before the loader sees it, so negative cases exercise the real
// consumer rather than a restatement of it.

ObjC.import('Foundation');

function readFile(path) {
  var value = $.NSString.stringWithContentsOfFileEncodingError(
    path, $.NSUTF8StringEncoding, null);
  return ObjC.unwrap(value);
}

function firstPattern(document) {
  return document.lemmas[0].meanings[0].patterns[0];
}

// The projection sorts patterns by ID, so the frame that carries examples is
// not necessarily the first one. Negative cases that need an example must ask
// for the pattern that has them rather than assume a position.
function patternWithExamples(document) {
  var found = null;
  document.lemmas.forEach(function (lemma) {
    lemma.meanings.forEach(function (meaning) {
      meaning.patterns.forEach(function (pattern) {
        if (!found && pattern.examples && pattern.examples.length) {
          found = pattern;
        }
      });
    });
  });
  if (!found) throw new Error('fixture has no pattern carrying examples');
  return found;
}

// Each mutation models one way a document could stop being the public contract.
var MUTATIONS = {
  none: function (document) { return document; },
  // §20 / §23-I: a private editorial field smuggled into public runtime.
  'private-review-state': function (document) {
    firstPattern(document).reviewState = 'approved';
    return document;
  },
  'private-evidence': function (document) {
    firstPattern(document).evidence = [{ sourceId: 'test-source-reference-001' }];
    return document;
  },
  'private-origin-deep': function (document) {
    patternWithExamples(document).examples[0].origin = {
      kind: 'original', authorRef: 'test-author-original-001' };
    return document;
  },
  'private-key-field': function (document) {
    document.lemmas[0].meanings[0].key = 'test-object';
    return document;
  },
  // §20 / §23-I: an envelope that is no longer closed.
  'extra-envelope-key': function (document) {
    document.releaseAuthorized = true;
    return document;
  },
  'nonrelease-wrapper': function (document) {
    return {
      artifactStatus: 'priority-7-runtime-projection-nonrelease-fixture',
      releaseAuthorized: false,
      runtimeProjection: document
    };
  },
  // §20: malformed nested structure.
  'malformed-complement': function (document) {
    firstPattern(document).complements = [{ type: 'case', case: 'not-a-case',
      required: true, role: 'object' }];
    return document;
  },
  'malformed-nested-null': function (document) {
    document.lemmas[0].meanings[0].patterns = null;
    return document;
  },
  'malformed-example': function (document) {
    patternWithExamples(document).examples[0].pl = 42;
    return document;
  },
  // §23-J: revision is part of the accepted public contract.
  'revision-zero': function (document) {
    document.patternDataRevision = 0;
    return document;
  },
  'revision-not-integer': function (document) {
    document.patternDataRevision = 1.5;
    return document;
  },
  'format-version-drift': function (document) {
    document.formatVersion = 2;
    return document;
  },
  'empty-lemmas': function (document) {
    document.lemmas = [];
    return document;
  }
};

// JavaScriptCore's osascript host does not drain native Promise jobs. This is
// the same deterministic stand-in tests/test_priority7_release_loader.js
// already uses; it models only the assimilation the shipping primitive relies
// on. The native-Promise proof stays owned by the real-browser check.
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

function run(argv) {
  var root = argv[0];
  var runtimePath = argv[1];
  var mutation = argv.length > 2 ? argv[2] : 'none';

  (0, eval)(readFile(root + '/pp-verb-patterns.js'));
  Promise = Immediate;

  var parsed = JSON.parse(readFile(runtimePath));
  if (!Object.prototype.hasOwnProperty.call(MUTATIONS, mutation)) {
    return JSON.stringify({ error: 'unknown mutation: ' + mutation });
  }
  var document = MUTATIONS[mutation](parsed);

  // Drive the dormant shipping transport exactly as the application would: one
  // injected fetch-like call resolving to a synthetic ok response.  No network.
  var settled = null;
  var response = {
    ok: true,
    json: function () { return Immediate.resolve(document); }
  };
  var requestCalls = [];
  function request(url, options) {
    requestCalls.push({ url: url, options: options });
    return Immediate.resolve(response);
  }

  PP_VERB_PATTERNS.reset();
  var availableBeforeLoad = PP_VERB_PATTERNS.available;

  PP_VERB_PATTERNS.loadRuntimeDocument(request, 'test-only://phase5a/runtime.json')
    .then(function (value) { settled = value; },
          function () { settled = 'rejected'; });

  var summary = PP_VERB_PATTERNS.summary();
  var result = {
    mutation: mutation,
    settled: settled,
    availableBeforeLoad: availableBeforeLoad,
    available: PP_VERB_PATTERNS.available,
    requestCount: requestCalls.length,
    requestUrl: requestCalls.length ? requestCalls[0].url : null,
    requestCache: requestCalls.length && requestCalls[0].options
      ? requestCalls[0].options.cache : null,
    summary: summary,
    countLabel: PP_VERB_PATTERNS.countLabel(),
    holdsPrivateKey: PP_VERB_PATTERNS.__holdsPrivateKeyForTest(document),
    formatVersion: PP_VERB_PATTERNS.FORMAT_VERSION,
    envelopeKeys: PP_VERB_PATTERNS.ENVELOPE_KEYS,
    caseOrder: PP_VERB_PATTERNS.CASE_ORDER
  };

  // The derived index/summary views, so the caller can prove the accepted
  // document is usable and not merely parseable.
  if (PP_VERB_PATTERNS.available) {
    var index = PP_VERB_PATTERNS.index();
    result.hasIndex = PP_VERB_PATTERNS.hasIndex();
    result.indexLemmas = index.map(function (row) { return row.lemma; });
    result.indexKeys = index.map(function (row) { return row.key; });
    result.indexPatternCounts = index.map(function (row) { return row.patternCount; });
    result.indexGlosses = index.map(function (row) { return row.glosses; });
    result.filterIds = PP_VERB_PATTERNS.filters().map(function (item) {
      return item.id;
    });
    result.allRowCount = PP_VERB_PATTERNS.rows("all").length;
    result.searchText = PP_VERB_PATTERNS.searchText();
    // The card-back cross-link direction, driven by the projected contentRefs.
    result.cardSupport = PP_VERB_PATTERNS.cardSupport(
      "p7-phase5a-synthetic-card-001");
    result.unknownCardSupport = PP_VERB_PATTERNS.cardSupport("no-such-card-id");
  }
  return JSON.stringify(result);
}
