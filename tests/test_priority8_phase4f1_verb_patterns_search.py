"""Focused lifecycle coverage for Priority 8 Phase 4F1 global search."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
START = "61108de211934d50d44f89d3fc1876c5752f0f06"
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
RUNTIME = json.loads((ROOT / "content/verb-patterns.json").read_text(encoding="utf-8"))
SIX = ("brać", "gotować", "dojechać", "odpowiadać", "uczyć się", "radzić sobie")


def extract_function(source: str, name: str) -> str:
    match = re.search(rf"function {re.escape(name)}\([^)]*\)\{{", source)
    if not match:
        raise AssertionError(f"missing function {name}")
    depth = 0
    for offset in range(match.end() - 1, len(source)):
        if source[offset] == "{":
            depth += 1
        elif source[offset] == "}":
            depth -= 1
            if depth == 0:
                return source[match.start():offset + 1]
    raise AssertionError(f"unterminated function {name}")


def git_bytes(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{START}:{path}"], cwd=ROOT)


def run_lifecycle_probe() -> dict:
    cache_declarations = re.search(
        r"const HAY = new WeakMap\(\);[^\n]*\nconst HAY_SKIP = new Set\([^\n]+\);",
        INDEX,
    )
    if not cache_declarations:
        raise AssertionError("missing production topic-search cache declarations")
    production = "\n".join((
        extract_function(INDEX, "patternIndexTopics"),
        cache_declarations.group(0),
        extract_function(INDEX, "topicHaystack"),
        extract_function(INDEX, "getVisibleTopics"),
        extract_function(INDEX, "pRefreshTopicSearch"),
        extract_function(INDEX, "pSettleRuntime"),
    ))
    probe = r'''
ObjC.import('Foundation');
function readFile(path) {
  var value = $.NSString.stringWithContentsOfFileEncodingError(
    path, $.NSUTF8StringEncoding, null);
  return ObjC.unwrap(value);
}
(function () {
  (0, eval)(readFile(__LOADER__));
  var document = JSON.parse(readFile(__RUNTIME__));
  __PRODUCTION__
  var LEVELS = [], S = { levelIdx:0, query:"" }, P = { view:"index" };
  var renderCalls = 0, lastRendered = [], homeActive = true, patternsActive = false;
  function $(id) {
    return { classList:{ contains:function (name) {
      return name === "active" && ((id === "home" && homeActive) ||
        (id === "patterns" && patternsActive));
    } } };
  }
  function renderTopics() { renderCalls += 1; lastRendered = getVisibleTopics(); }
  function pRenderIndex() {}
  function installTopic() {
    var topic = patternIndexTopics()[0];
    LEVELS = [{ level:"Verb Patterns", topics:[topic] }];
    S.levelIdx = 0;
    return topic;
  }
  function names(rows) { return rows.map(function (row) { return row.t.name; }); }
  function countVerbPatterns() {
    return getVisibleTopics().filter(function (row) {
      return row.t.name === "Verb Patterns";
    }).length;
  }

  PP_VERB_PATTERNS.reset();
  var topic = installTopic();
  S.query = "odpowiadać";
  var preLoadText = topic.searchText;
  var preLoadMatches = countVerbPatterns(); // freezes the empty haystack in HAY
  var failureSafe = true;
  try { pSettleRuntime(false); } catch (error) { failureSafe = false; }
  var failureMatches = countVerbPatterns();
  var failureRenderCalls = renderCalls;

  var accepted = PP_VERB_PATTERNS.__acceptForTest(document);
  pSettleRuntime(accepted);
  var duringLoadQueryMatches = countVerbPatterns();
  var duringLoadRenderedMatches = lastRendered.filter(function (row) {
    return row.t.name === "Verb Patterns";
  }).length;
  var postLoadText = topic.searchText;

  var lemmaMatches = {};
  document.lemmas.forEach(function (lemma) {
    var display = lemma.displayLemma || lemma.canonicalLemma;
    S.query = display;
    lemmaMatches[display] = countVerbPatterns();
  });
  var sixMatches = {};
  __SIX__.forEach(function (query) { S.query = query; sixMatches[query] = countVerbPatterns(); });
  var lexicalMatches = {};
  ["uczyć się", "radzić sobie", "spotykać się"].forEach(function (query) {
    S.query = query; lexicalMatches[query] = countVerbPatterns();
  });

  S.query = "";
  var clearNames = names(getVisibleTopics());
  S.query = "brać"; // equivalent search after entering the surface and navigating back
  var afterNavigationMatches = countVerbPatterns();

  var vpTopic = topic;
  var travel = { name:"Travel basics", desc:"train shared" };
  var food = { name:"Food basics", desc:"kitchen shared" };
  LEVELS = [{ level:"Verb Patterns", topics:[vpTopic] },
            { level:"Existing", topics:[travel, food] }];
  S.query = "train";
  var unrelatedNames = names(getVisibleTopics());
  S.query = "shared";
  var unrelatedOrder = names(getVisibleTopics());
  S.query = "brać";
  pSettleRuntime(true);
  var repeatSettleMatches = countVerbPatterns();

  PP_VERB_PATTERNS.reset();
  topic = installTopic();
  S.query = "odpowiadać";
  var reloadPreMatches = countVerbPatterns();
  var reloadAccepted = PP_VERB_PATTERNS.__acceptForTest(document);
  pSettleRuntime(reloadAccepted);
  var reloadPostMatches = countVerbPatterns();

  return JSON.stringify({
    preLoadText:preLoadText, preLoadMatches:preLoadMatches,
    failureSafe:failureSafe, failureMatches:failureMatches,
    failureRenderCalls:failureRenderCalls, accepted:accepted,
    duringLoadQueryMatches:duringLoadQueryMatches,
    duringLoadRenderedMatches:duringLoadRenderedMatches,
    postLoadText:postLoadText, renderCalls:renderCalls,
    lemmaMatches:lemmaMatches, sixMatches:sixMatches,
    lexicalMatches:lexicalMatches, clearNames:clearNames,
    afterNavigationMatches:afterNavigationMatches,
    unrelatedNames:unrelatedNames, unrelatedOrder:unrelatedOrder,
    repeatSettleMatches:repeatSettleMatches, reloadPreMatches:reloadPreMatches,
    reloadAccepted:reloadAccepted, reloadPostMatches:reloadPostMatches
  });
})()
'''
    with tempfile.TemporaryDirectory(prefix="p8-4f1-") as directory:
        script_path = Path(directory) / "probe.js"
        script_path.write_text(
            probe.replace("__LOADER__", json.dumps(str(ROOT / "pp-verb-patterns.js")))
            .replace("__RUNTIME__", json.dumps(str(ROOT / "content/verb-patterns.json")))
            .replace("__PRODUCTION__", production)
            .replace("__SIX__", json.dumps(SIX, ensure_ascii=False)),
            encoding="utf-8",
        )
        run = subprocess.run(
            ["osascript", "-l", "JavaScript", str(script_path)], cwd=ROOT,
            text=True, capture_output=True,
        )
    if run.returncode:
        raise AssertionError(run.stderr or run.stdout)
    return json.loads(run.stdout.strip().splitlines()[-1])


class Priority8Phase4F1VerbPatternsSearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.probe = run_lifecycle_probe()

    def test_01_preload_snapshot_is_empty_but_not_permanent(self):
        self.assertEqual("", self.probe["preLoadText"])
        self.assertEqual(0, self.probe["preLoadMatches"])
        self.assertTrue(self.probe["accepted"])
        self.assertTrue(self.probe["postLoadText"])

    def test_02_existing_query_refreshes_when_runtime_settles(self):
        self.assertEqual(1, self.probe["duringLoadQueryMatches"])
        self.assertEqual(1, self.probe["duringLoadRenderedMatches"])
        self.assertGreaterEqual(self.probe["renderCalls"], 1)

    def test_03_all_released_lemmas_use_the_runtime_search_corpus(self):
        expected = [lemma.get("displayLemma", lemma["canonicalLemma"])
                    for lemma in RUNTIME["lemmas"]]
        self.assertEqual(98, len(expected))
        self.assertEqual(set(expected), set(self.probe["lemmaMatches"]))
        self.assertEqual({1}, {self.probe["lemmaMatches"][lemma] for lemma in expected})

    def test_04_six_acceptance_queries_each_discover_one_topic(self):
        self.assertEqual({query: 1 for query in SIX}, self.probe["sixMatches"])

    def test_05_lexical_sie_and_sobie_forms_remain_searchable(self):
        self.assertEqual(
            {"uczyć się": 1, "radzić sobie": 1, "spotykać się": 1},
            self.probe["lexicalMatches"],
        )

    def test_06_loader_failure_is_nonblocking_and_does_not_fabricate_search(self):
        self.assertTrue(self.probe["failureSafe"])
        self.assertEqual(0, self.probe["failureMatches"])
        self.assertEqual(0, self.probe["failureRenderCalls"])

    def test_07_clear_navigation_repeat_settlement_and_reload_are_stable(self):
        self.assertEqual(["Verb Patterns"], self.probe["clearNames"])
        self.assertEqual(1, self.probe["afterNavigationMatches"])
        self.assertEqual(1, self.probe["repeatSettleMatches"])
        self.assertEqual(0, self.probe["reloadPreMatches"])
        self.assertTrue(self.probe["reloadAccepted"])
        self.assertEqual(1, self.probe["reloadPostMatches"])

    def test_08_unrelated_search_results_and_order_are_unchanged(self):
        self.assertEqual(["Travel basics"], self.probe["unrelatedNames"])
        self.assertEqual(["Travel basics", "Food basics"], self.probe["unrelatedOrder"])

    def test_09_refresh_is_wired_to_authoritative_runtime_without_query_literals(self):
        refresh = extract_function(INDEX, "pRefreshTopicSearch")
        settle = extract_function(INDEX, "pSettleRuntime")
        self.assertIn("PP_VERB_PATTERNS.searchText()", refresh)
        self.assertIn("HAY.delete(topic)", refresh)
        self.assertLess(settle.index("pRefreshTopicSearch()"), settle.index("renderTopics()"))
        self.assertIn(").then(pSettleRuntime, ()=>{});", INDEX)
        self.assertFalse(any(query in refresh for query in SIX))
        self.assertNotIn("setTimeout", refresh + settle)

    def test_10_production_counts_and_content_sha_are_frozen(self):
        patterns = sum(len(meaning["patterns"]) for lemma in RUNTIME["lemmas"]
                       for meaning in lemma["meanings"])
        self.assertEqual((98, 269), (len(RUNTIME["lemmas"]), patterns))
        self.assertEqual(
            "66a02804b8ea1bb2b8a4ec7260855018db0e32f7a0623b78dc8b62fd58801ff1",
            hashlib.sha256((ROOT / "content/verb-patterns.json").read_bytes()).hexdigest(),
        )

    def test_11_audio_human_qa_migration_and_activity_are_unchanged(self):
        manifest = json.loads((ROOT / "audio-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(3621, len(manifest["entries"]))
        self.assertEqual(3621, len(list((ROOT / "audio").glob("*.mp3"))))
        for path in ("audio-manifest.json", "editorial/priority-8-phase4e1-audio-qa.csv",
                     "pp-migrate.js"):
            self.assertEqual(git_bytes(path), (ROOT / path).read_bytes(), path)
        baseline_index = git_bytes("index.html").decode("utf-8")
        self.assertEqual(extract_function(baseline_index, "poolFor"),
                         extract_function(INDEX, "poolFor"))
        self.assertIn("const ppEligibleFor     = PP_USAGE.eligibleFor;", INDEX)

    def test_12_release_markers_and_change_scope_are_frozen(self):
        worker = (ROOT / "sw.js").read_text(encoding="utf-8")
        self.assertIn('const APP_VERSION = "8.13";', INDEX)
        self.assertIn('const CACHE = "popolsku-v68";', worker)
        self.assertIn('const AUDIO_CACHE = "popolsku-audio";', worker)
        changed = set(subprocess.check_output(
            ["git", "diff", "--name-only", START], cwd=ROOT, text=True).splitlines())
        self.assertLessEqual(changed, {
            "index.html", "tests/test_priority8_phase4f1_verb_patterns_search.py",
            "reports/priority-8-phase-4f1-verb-patterns-search.md",
        })


if __name__ == "__main__":
    unittest.main()
