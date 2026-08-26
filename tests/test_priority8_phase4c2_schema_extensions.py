import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
STARTING_HEAD = "604df149045fb91bbcf35eb54499b0ef490e1e99"
sys.path.insert(0, str(ROOT))

import priority7_tooling as tooling  # noqa: E402
import priority8_phase4c1_stable_ids as phase4c1  # noqa: E402
import validate_priority8_staging as staging_validator  # noqa: E402


FROZEN_HASHES = {
    "editorial/priority-8-phase4-staging.json":
        "6ba1bcab43feeee5bfb99a5ac67eace8befa12c3df67f44bfb94191bf1a80adc",
    "editorial/priority-8-phase4-candidate-key-freeze.json":
        "b74bff54122ffb25c5ce8215e5bf28f8aa8823eabc2528cae8b1066a7eb1ab8b",
    "editorial/priority-8-phase4c-stable-id-map.json":
        "20fc8a566cb34825306f9198f4977fb0dacef3c33696cad45ff7ecbab6487a9d",
    "audio-manifest.json":
        "791dc09355b90f1457beb46f140a3997fc073ad46a85237a2aedecf6038707b2",
    "sw.js":
        "5f5e3d41762f14fca51f5d5984071c09ec6349c8ea2f87b36c16b8238a6a6b3e",
    "index.html":
        "2257d3c9916a4cbf2420ffbf63b25e51dfd01e87e0eb153cb37386b0af1f6eab",
}


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def git_bytes(relative):
    return subprocess.check_output(
        ["git", "show", f"{STARTING_HEAD}:{relative}"], cwd=ROOT)


def git_json(relative):
    return json.loads(git_bytes(relative).decode("utf-8"))


def sha256(relative):
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def patterns(document):
    for lemma in document["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                yield lemma, meaning, pattern


def inventory(document):
    counts = {"lemmas": len(document["lemmas"]), "meanings": 0,
              "patterns": 0, "examples": 0}
    identifiers = []
    for lemma in document["lemmas"]:
        identifiers.append(lemma["id"])
        counts["meanings"] += len(lemma["meanings"])
        for meaning in lemma["meanings"]:
            identifiers.append(meaning["id"])
            counts["patterns"] += len(meaning["patterns"])
            for pattern in meaning["patterns"]:
                identifiers.append(pattern["id"])
                examples = pattern.get("examples", [])
                counts["examples"] += len(examples)
                identifiers.extend(example["id"] for example in examples)
    return counts, identifiers


def first_pattern(document):
    return document["lemmas"][0]["meanings"][0]["patterns"][0]


JXA_PROBE = r'''
ObjC.import('Foundation');
function readFile(path) {
  var value = $.NSString.stringWithContentsOfFileEncodingError(
    path, $.NSUTF8StringEncoding, null);
  return ObjC.unwrap(value);
}
(function () {
  var sourcePath = __SOURCE_PATH__;
  var runtimePath = __RUNTIME_PATH__;
  (0, eval)(readFile(sourcePath));
  var document = JSON.parse(readFile(runtimePath));
  PP_VERB_PATTERNS.reset();
  var accepted = PP_VERB_PATTERNS.__acceptForTest(document);
  var result = {
    accepted: accepted,
    available: PP_VERB_PATTERNS.available,
    formatVersion: PP_VERB_PATTERNS.FORMAT_VERSION,
    roles: PP_VERB_PATTERNS.ROLES || null,
    clauseKinds: PP_VERB_PATTERNS.CLAUSE_KINDS || null,
    complementTypes: PP_VERB_PATTERNS.COMPLEMENT_TYPES || null,
    relationTypes: PP_VERB_PATTERNS.RELATION_TYPES || null
  };
  if (accepted) {
    var lemma = document.lemmas[0];
    var pattern = lemma.meanings[0].patterns[0];
    var display = lemma.displayLemma || lemma.canonicalLemma;
    result.headline = PP_VERB_PATTERNS.headlineFor(display, pattern);
    result.chips = pattern.complements.map(function (complement) {
      return PP_VERB_PATTERNS.chipFor(complement, pattern.relationType);
    });
    result.rolesForComplements = pattern.complements.map(function (complement) {
      return PP_VERB_PATTERNS.roleFor(complement, pattern.relationType);
    });
    result.questions = pattern.complements.map(function (complement) {
      return PP_VERB_PATTERNS.questionsFor(complement);
    });
    result.searchText = PP_VERB_PATTERNS.searchText();
    result.renderProjection = PP_VERB_PATTERNS.index().map(function (row) {
      return PP_VERB_PATTERNS.lemma(row.key);
    });
    result.patternCount = PP_VERB_PATTERNS.summary().patterns;
  }
  return JSON.stringify(result);
})()
'''


def js_probe(document, source_bytes=None):
    if source_bytes is None:
        source_bytes = (ROOT / "pp-verb-patterns.js").read_bytes()
    with tempfile.TemporaryDirectory(prefix="p8-4c2-") as temporary:
        temp = Path(temporary)
        source_path = temp / "loader.js"
        runtime_path = temp / "runtime.json"
        probe_path = temp / "probe.js"
        source_path.write_bytes(source_bytes)
        runtime_path.write_text(
            json.dumps(document, ensure_ascii=False), encoding="utf-8")
        probe_path.write_text(
            JXA_PROBE.replace("__SOURCE_PATH__", json.dumps(str(source_path)))
            .replace("__RUNTIME_PATH__", json.dumps(str(runtime_path))),
            encoding="utf-8")
        run = subprocess.run(
            ["osascript", "-l", "JavaScript", str(probe_path)], cwd=ROOT,
            text=True, capture_output=True)
        if run.returncode != 0:
            raise AssertionError(run.stderr or run.stdout)
        return json.loads(run.stdout)


class Priority8Phase4C2SchemaExtensionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = load("content/verb-patterns.json")
        cls.before_runtime = git_json("content/verb-patterns.json")
        cls.editorial = load("editorial/verb-pattern-candidates.json")
        cls.context = tooling._load_context(
            str(ROOT / "editorial/priority-7-authoring-context.json"), str(ROOT))

    def runtime_with_complement(self, complement, *, lemma="testować"):
        document = copy.deepcopy(self.runtime)
        record = document["lemmas"][0]
        record["canonicalLemma"] = lemma
        record.pop("displayLemma", None)
        record["reflexive"] = lemma.endswith(" się")
        pattern = first_pattern(document)
        pattern["relationType"] = "lexical-frame"
        pattern["complements"] = [complement]
        pattern.pop("requiredLexicalItems", None)
        return document

    def assert_python_runtime_invalid(self, document, code):
        self.assertIn(code, {issue.code for issue in tooling.validate_runtime(document)})

    def test_01_released_contract_moves_only_format_version(self):
        expected = copy.deepcopy(self.before_runtime)
        self.assertEqual(1, expected["formatVersion"])
        expected["formatVersion"] = 2
        self.assertEqual(expected, self.runtime)
        self.assertEqual(2, self.runtime["formatVersion"])
        self.assertEqual(2, self.runtime["patternDataRevision"])

    def test_02_released_counts_and_all_154_ids_are_unchanged(self):
        before_counts, before_ids = inventory(self.before_runtime)
        after_counts, after_ids = inventory(self.runtime)
        self.assertEqual(
            {"lemmas": 30, "meanings": 34, "patterns": 45, "examples": 45},
            after_counts)
        self.assertEqual(before_counts, after_counts)
        self.assertEqual(before_ids, after_ids)
        self.assertEqual(154, len(after_ids))
        self.assertEqual(154, len(set(after_ids)))

    def test_03_all_released_ids_reproduce_through_locked_allocator(self):
        rows = phase4c1.released_identity_rows(self.runtime)
        self.assertEqual(154, len(rows))
        self.assertEqual(154, len({row["id"] for row in rows}))

    def test_04_private_611_id_map_is_byte_and_semantically_unchanged(self):
        self.assertEqual(
            FROZEN_HASHES["editorial/priority-8-phase4c-stable-id-map.json"],
            sha256("editorial/priority-8-phase4c-stable-id-map.json"))
        persisted = load("editorial/priority-8-phase4c-stable-id-map.json")
        regenerated = phase4c1.build_map()
        self.assertEqual(regenerated, persisted)
        summary = phase4c1.validate_map(persisted)
        self.assertEqual((154, 611, 765), (
            summary["releasedTotal"], summary["newTotal"], summary["unionTotal"]))

    def test_05_no_new_map_id_is_promoted_to_released_content(self):
        _, released_ids = inventory(self.runtime)
        mapped_ids = {
            row["id"] for row in
            load("editorial/priority-8-phase4c-stable-id-map.json")["allocations"]}
        self.assertEqual(611, len(mapped_ids))
        self.assertTrue(mapped_ids.isdisjoint(released_ids))

    def test_06_staging_freeze_map_audio_shell_and_service_worker_are_unchanged(self):
        for relative, expected in FROZEN_HASHES.items():
            self.assertEqual(expected, sha256(relative), relative)

    def test_07_python_and_javascript_contract_tables_are_in_parity(self):
        probe = js_probe(self.runtime)
        self.assertTrue(probe["accepted"])
        self.assertEqual(tooling.FORMAT_VERSION, probe["formatVersion"])
        self.assertEqual(sorted(tooling.ROLES), sorted(probe["roles"]))
        self.assertEqual(sorted(tooling.CLAUSE_KINDS), sorted(probe["clauseKinds"]))
        self.assertEqual(
            sorted(tooling.COMPLEMENT_TYPES), sorted(probe["complementTypes"]))
        self.assertEqual(sorted(tooling.RELATION_TYPES), sorted(probe["relationTypes"]))
        self.assertEqual(tooling.ROLES, staging_validator.ROLES)
        self.assertEqual(tooling.CLAUSE_KINDS, staging_validator.CLAUSE_KINDS)

    def test_08_format_version_two_is_exact_and_future_versions_fail_closed(self):
        self.assertEqual([], tooling.validate_runtime(self.runtime))
        self.assertTrue(js_probe(self.runtime)["accepted"])
        for version in (1, 3):
            with self.subTest(version=version):
                changed = copy.deepcopy(self.runtime)
                changed["formatVersion"] = version
                self.assert_python_runtime_invalid(changed, "FORMAT_VERSION")
                self.assertFalse(js_probe(changed)["accepted"])

    def test_09_upgraded_editorial_projects_the_released_runtime_exactly(self):
        # Phase 4C2 owns the exact editorial population at its starting
        # checkpoint, not a permanent assertion that no later phase may approve
        # additional patterns.  Re-read that immutable local Git snapshot and
        # apply only Phase 4C2's format-envelope upgrade.
        upgraded = git_json("editorial/verb-pattern-candidates.json")
        upgraded["formatVersion"] = 2
        self.assertEqual([], tooling.validate_editorial(upgraded, self.context))
        self.assertEqual(
            self.runtime,
            tooling.project_runtime_nonrelease(upgraded, 2, self.context))

        # Historical scoping remains strict: changing the owned approved
        # population no longer reproduces the exact released runtime.
        tampered = copy.deepcopy(upgraded)
        first_pattern(tampered)["reviewState"] = "research"
        self.assertIn(
            "REVIEW_STATE_MISMATCH",
            {issue.code for issue in tooling.validate_editorial(
                tampered, self.context)})

    def test_10_all_45_released_render_and_search_projections_are_exact(self):
        before = js_probe(
            self.before_runtime, git_bytes("pp-verb-patterns.js"))
        after = js_probe(self.runtime)
        self.assertEqual(45, before["patternCount"])
        self.assertEqual(45, after["patternCount"])
        self.assertEqual(before["renderProjection"], after["renderProjection"])
        self.assertEqual(before["searchText"], after["searchText"])

    def test_11_direct_speech_validates_and_uses_generic_clause_paths(self):
        document = self.runtime_with_complement({
            "type": "clause", "clauseKind": "direct-speech",
            "required": True, "role": "content",
        }, lemma="powiedzieć")
        self.assertEqual([], tooling.validate_runtime(document))
        probe = js_probe(document)
        self.assertTrue(probe["accepted"])
        self.assertEqual(["powiedzieć", "+", "„…”"],
                         [part["text"] for part in probe["headline"]])
        self.assertEqual("+ „…” · Clause", probe["chips"][0]["text"])
        self.assertEqual("no-case", probe["chips"][0]["bucket"])
        self.assertIn("„…”", probe["searchText"])

    def test_12_all_clause_kinds_remain_structurally_distinct_and_czy_is_retained(self):
        expected = {
            "ze": "że …", "zeby": "żeby …", "czy": "czy …",
            "interrogative": "pytanie …", "direct-speech": "„…”",
        }
        rendered = {}
        for kind, token in expected.items():
            with self.subTest(kind=kind):
                document = self.runtime_with_complement({
                    "type": "clause", "clauseKind": kind,
                    "required": True, "role": "content",
                })
                self.assertEqual([], tooling.validate_runtime(document))
                probe = js_probe(document)
                self.assertTrue(probe["accepted"])
                rendered[kind] = probe["chips"][0]["question"]
                self.assertEqual(token, rendered[kind])
        self.assertEqual(5, len(set(rendered.values())))

    def test_13_source_uses_the_approved_generic_phrase_and_is_not_animate(self):
        document = self.runtime_with_complement({
            "type": "preposition-case", "preposition": "od",
            "case": "genitive", "required": True, "role": "source",
        }, lemma="kupować")
        self.assertEqual([], tooling.validate_runtime(document))
        probe = js_probe(document)
        self.assertTrue(probe["accepted"])
        self.assertEqual("where it comes from", probe["rolesForComplements"][0])
        self.assertEqual(["od kogo?", "od czego?"], probe["questions"][0])
        self.assertEqual("od czego?", probe["headline"][-1]["text"])

    def test_14_source_accepts_person_question_override_without_global_animacy(self):
        document = self.runtime_with_complement({
            "type": "preposition-case", "preposition": "od",
            "case": "genitive", "required": True, "role": "source",
            "questionOverridePl": ["kogo?"],
        }, lemma="kupić")
        probe = js_probe(document)
        self.assertTrue(probe["accepted"])
        self.assertEqual("where it comes from", probe["rolesForComplements"][0])
        self.assertEqual(["od kogo?"], probe["questions"][0])
        self.assertEqual("od kogo?", probe["headline"][-1]["text"])

    def test_15_required_lexical_items_preserve_udzial_in_both_headlines(self):
        for lemma in ("brać", "wziąć"):
            with self.subTest(lemma=lemma):
                document = self.runtime_with_complement({
                    "type": "preposition-case", "preposition": "w",
                    "case": "locative", "required": True, "role": "target",
                }, lemma=lemma)
                first_pattern(document)["requiredLexicalItems"] = ["udział"]
                self.assertEqual([], tooling.validate_runtime(document))
                probe = js_probe(document)
                self.assertTrue(probe["accepted"])
                self.assertEqual(
                    [lemma, "udział", "+", "w czym?"],
                    [part["text"] for part in probe["headline"]])

    def test_16_absent_required_lexical_items_preserve_existing_behavior(self):
        document = self.runtime_with_complement({
            "type": "preposition-case", "preposition": "w",
            "case": "locative", "required": True, "role": "target",
        }, lemma="brać")
        self.assertNotIn("requiredLexicalItems", first_pattern(document))
        probe = js_probe(document)
        self.assertEqual(
            ["brać", "w czym?"], [part["text"] for part in probe["headline"]])

    def test_17_required_lexical_items_malformed_shapes_fail_on_both_sides(self):
        malformed = (
            "udział", [], [42], [""], [" udział"], ["Udział"],
            ["udział", "udział"], [["udział"]],
            ["jeden", "dwa", "trzy", "cztery", "pięć"],
        )
        for value in malformed:
            with self.subTest(value=value):
                changed = copy.deepcopy(self.runtime)
                first_pattern(changed)["requiredLexicalItems"] = value
                self.assertTrue(tooling.validate_runtime(changed))
                self.assertFalse(js_probe(changed)["accepted"])

    def test_18_unknown_role_and_clause_kind_fail_closed_on_both_sides(self):
        cases = (
            ({"type": "case", "case": "accusative", "required": True,
              "role": "source-like"}, "SCHEMA_ENUM"),
            ({"type": "clause", "clauseKind": "quoted-speech",
              "required": True, "role": "content"}, "SCHEMA_ENUM"),
        )
        for complement, code in cases:
            with self.subTest(complement=complement):
                document = self.runtime_with_complement(complement)
                self.assert_python_runtime_invalid(document, code)
                self.assertFalse(js_probe(document)["accepted"])

    def test_19_required_lexical_items_does_not_weaken_closed_pattern_schema(self):
        changed = copy.deepcopy(self.runtime)
        pattern = first_pattern(changed)
        pattern["requiredLexicalItems"] = ["udział"]
        pattern["requiredLexicalItem"] = "udział"
        self.assert_python_runtime_invalid(changed, "SCHEMA_UNKNOWN_FIELD")
        self.assertFalse(js_probe(changed)["accepted"])

    def test_20_editorial_validation_projection_and_structure_preserve_the_field(self):
        upgraded = copy.deepcopy(self.editorial)
        upgraded["formatVersion"] = 2
        lemma, meaning, pattern = next(patterns(upgraded))
        pattern["requiredLexicalItems"] = ["udział"]
        pattern["reviewState"] = "research"
        pattern["reviewEvents"] = []
        for example in pattern.get("examples", []):
            example["audioEligible"] = False
        self.assertEqual([], tooling.validate_editorial(upgraded, self.context))
        runtime_pattern = tooling._runtime_pattern(pattern, set())
        self.assertEqual(["udział"], runtime_pattern["requiredLexicalItems"])
        entity = tooling._EntityInfo(
            "pattern", pattern["id"], meaning["id"], pattern["key"],
            "$synthetic.pattern", pattern, lemma, meaning, pattern)
        structure = tooling._structure_for_entity(entity)
        self.assertEqual(["udział"], structure["requiredLexicalItems"])
        frozen_issues = []
        self.assertTrue(tooling._validate_frozen_structure_row(
            structure, "$synthetic.structure", frozen_issues))
        self.assertEqual([], frozen_issues)
        for stage in tooling.STAGE_KINDS:
            self.assertEqual(
                ["udział"],
                tooling.review_scope(stage, lemma, meaning, pattern)["pattern"][
                    "requiredLexicalItems"])

    def test_21_absent_field_is_absent_from_projection_and_frozen_structure(self):
        upgraded = copy.deepcopy(self.editorial)
        upgraded["formatVersion"] = 2
        lemma, meaning, pattern = next(patterns(upgraded))
        self.assertNotIn("requiredLexicalItems", pattern)
        self.assertNotIn(
            "requiredLexicalItems", tooling._runtime_pattern(pattern, set()))
        entity = tooling._EntityInfo(
            "pattern", pattern["id"], meaning["id"], pattern["key"],
            "$released.pattern", pattern, lemma, meaning, pattern)
        self.assertNotIn(
            "requiredLexicalItems", tooling._structure_for_entity(entity))
        for stage in tooling.STAGE_KINDS:
            self.assertNotIn(
                "requiredLexicalItems",
                tooling.review_scope(stage, lemma, meaning, pattern)["pattern"])

    def test_22_migration_activity_and_audio_boundaries_remain_exact(self):
        migration = (ROOT / "pp-migrate.js").read_text(encoding="utf-8")
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        service_worker = (ROOT / "sw.js").read_text(encoding="utf-8")
        self.assertRegex(migration, r"SCHEMA_VERSION\s*=\s*2")
        self.assertRegex(migration, r"CONTENT_MIGRATION_REVISION\s*=\s*2")
        self.assertRegex(index, r'APP_VERSION\s*=\s*"8\.12"')
        self.assertRegex(service_worker, r'CACHE\s*=\s*"popolsku-v67"')
        released_patterns = [pattern for _, _, pattern in patterns(self.runtime)]
        self.assertTrue(all(pattern["activityEligibility"] == []
                            for pattern in released_patterns))
        examples = [example for pattern in released_patterns
                    for example in pattern.get("examples", [])]
        self.assertEqual(45, len(examples))
        self.assertTrue(all(example["audioEligible"] is True for example in examples))


if __name__ == "__main__":
    unittest.main()
