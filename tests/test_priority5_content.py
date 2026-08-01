import copy
import contextlib
import hashlib
import io
import json
import os
import tempfile
import unittest
from collections import Counter
from unittest import mock

import validate_content as validator


HEALTHCARE_TOPIC_ID = "a2-healthcare-appointments"
HEALTHCARE_SCENARIO_ID = "scenarios-healthcare-appointments"
HEALTHCARE_APPROVAL_REFERENCE = (
    "P5-Phase-2A-healthcare-content-lock/"
    "8a50d3b0ae35587c61df5f035974434ff12f403a#"
    "P5-Phase-2B-activity-policy-override/"
    "Long-Type-It-opt-outs-and-removal-of-unnecessary-card-016-cue/"
    "Approved-2026-07-31")
HEALTHCARE_PHASE_2D_APPROVAL_REFERENCE = (
    "P5-Phase-2D-healthcare-audio-QA-correction/"
    "Human-listening-found-a-TTS-pronunciation-defect-in-jutrzejsza/"
    "Approved-replacement-Dzwonie-zeby-odwolac-wizyte-na-jutro/"
    "Approved-2026-07-31")
HEALTHCARE_PHASE_2E_APPROVAL_REFERENCE = (
    "P5-Phase-2E-native-Polish-review-corrections/"
    "Native-review-approved-all-Healthcare-Appointments-content-except-one-"
    "Card-04-standalone-naturalness-correction-and-optional-hint-additions-"
    "for-Cards-12-and-18/"
    "User-approved-implementation-and-disclosure-of-the-two-replacement-TTS-"
    "phrases-on-2026-08-01")
OLD_FOLLOW_UP_MAIN = "Chodzi o wizytę kontrolną."
OLD_FOLLOW_UP_EXAMPLE = "Dzwonię, bo chodzi o wizytę kontrolną."
NEW_FOLLOW_UP_MAIN = "Dzwonię w sprawie wizyty kontrolnej."
NEW_FOLLOW_UP_EXAMPLE = (
    "Dzień dobry, dzwonię w sprawie wizyty kontrolnej.")
OLD_FOLLOW_UP_MAIN_AUDIO_ID = "5950fe003f6f"
OLD_FOLLOW_UP_EXAMPLE_AUDIO_ID = "462e752e2a59"
NEW_FOLLOW_UP_MAIN_AUDIO_ID = "1fed173109e1"
NEW_FOLLOW_UP_EXAMPLE_AUDIO_ID = "e6063c6546c9"
NEW_FOLLOW_UP_MAIN_AUDIO_SHA256 = (
    "7041195ce7fe65893cc843895c88bf1e8197c7fc53c4d1cf835a2f15f0e25eb5")
NEW_FOLLOW_UP_EXAMPLE_AUDIO_SHA256 = (
    "00d420bc7d43899335db52a8c7e6075bdba101a3a20ffbd1085b574637da716a")
OLD_CANCELLATION_EXAMPLE = (
    "Dzwonię, żeby odwołać jutrzejszą wizytę.")
NEW_CANCELLATION_EXAMPLE = (
    "Dzwonię, żeby odwołać wizytę na jutro.")
OLD_CANCELLATION_AUDIO_ID = "e5209daccfc8"
NEW_CANCELLATION_AUDIO_ID = "648733664d0b"
NEW_CANCELLATION_AUDIO_SHA256 = (
    "1abb8891447d42cbcaa37dcec3f0eececb506be5b74bb40d3b89276a86156600")
HEALTHCARE_TOPIC_SHA256 = (
    "a030a35ad10650221fa557b7669274a8ec3c381f7e5c7fedeffbe2e56a073527")
HEALTHCARE_SCENARIO_SHA256 = (
    "fccf57671781dd3d04d8728d719d481d5e54d52fdeb434e9cce3a2970b0b6779")
PRIOR_FORWARD_BASELINE_SHA256 = (
    "509d6215adddce14987d8f0de304ee31b335ee770685477123c04a6b325de8e8")
PRE_CORRECTION_FORWARD_BASELINE_SHA256 = (
    "042d87cfbed351382d8686cd696a955504cc98b96e55745f4b1d27993062aab8")
HEALTHCARE_PHASE_2D_FORWARD_BASELINE_SHA256 = (
    "10b429637a92a645c9f65cc952032f59cd86e4df36fe5688a4449947eac072f6")
HEALTHCARE_FORWARD_BASELINE_SHA256 = (
    "2a71401d8966ccbda59ec696f2c41cc3b48801d5c6059a881183b44ea3a1ce50")


def card(stable_id="a2-fixture-001", pl="Dzień dobry",
         en="Good morning", **extra):
    value = {
        "id": stable_id,
        "pl": pl,
        "en": en,
        "hint": "A useful fixture phrase.",
        "ex": f"{pl}!",
        "exEn": f"{en}!",
    }
    value.update(extra)
    return value


def vocab_source(cards=None, topic_id="a2-fixture"):
    return validator.corpus_from_levels([{
        "id": "a2",
        "level": "A2",
        "blurb": "Fixture",
        "topics": [{
            "id": topic_id,
            "name": "Fixture",
            "emoji": "🧪",
            "desc": "Fixture topic",
            "cards": cards if cards is not None else [card()],
        }],
    }], "data-a2.js")


def valid_scenario(topic_id="scenarios-fixture", cefr="A2"):
    topic = {
        "id": topic_id,
        "name": "Fixture scenario",
        "emoji": "🗣️",
        "kind": "convo",
        "role": "Learner",
        "setting": "Somewhere",
        "goal": "Finish",
        "recap": "Done",
        "start": "s1",
        "scenes": {
            "s1": {
                "npc": "Dzień dobry.",
                "npcEn": "Good morning.",
                "options": [{
                    "pl": "Dzień dobry!",
                    "en": "Good morning!",
                    "goto": "end",
                }],
            },
            "end": {
                "npc": "Do widzenia.",
                "npcEn": "Goodbye.",
                "end": True,
            },
        },
    }
    if cefr is not None:
        topic["cefr"] = cefr
    return topic


def scenario_source(topic=None):
    return validator.corpus_from_levels([{
        "id": "scenarios",
        "level": "Scenarios",
        "blurb": "Fixture",
        "topics": [topic or valid_scenario()],
    }], "data-scenarios.js")


def podcast_source(cards=None, topic_id="podcasts-fixture"):
    intro = {
        "id": f"{topic_id}-intro",
        "intro": True,
        "pl": "Odcinek testowy",
        "en": "Test episode",
        "hint": "Fixture podcast introduction.",
        "host": "Jan Testowy",
        "link": "https://example.test/episode",
    }
    return validator.corpus_from_levels([{
        "id": "podcasts",
        "level": "Podcasts",
        "blurb": "Fixture",
        "topics": [{
            "id": topic_id,
            "name": "Fixture podcast",
            "emoji": "🎙️",
            "kind": "podcast",
            "desc": "Fixture topic",
            "cards": cards if cards is not None else [
                intro,
                card(f"{topic_id}-001"),
            ],
        }],
    }], "data-podcasts.js")


def grammar_source(drills):
    return validator.corpus_from_levels([{
        "id": "building-sentences",
        "level": "Grammar",
        "blurb": "Fixture",
        "topics": [{
            "id": "building-sentences-fixture",
            "name": "Fixture grammar",
            "kind": "grammar",
            "drills": drills,
        }],
    }], "data-grammar.js")


def baseline_for(sources):
    return validator.build_forward_baseline(
        sources,
        schema_version=2,
        migration_revision=2,
        legacy={"schema": 2, "topics": {}, "cards": {}, "retired": {}},
    )


class Priority5BaselineTests(unittest.TestCase):
    def assertCode(self, code, issues):
        self.assertIn(code, validator.issue_codes(issues), issues)

    def test_missing_baseline(self):
        with tempfile.TemporaryDirectory() as directory:
            document, issues = validator.load_forward_baseline(
                os.path.join(directory, "missing.json"))
        self.assertIsNone(document)
        self.assertCode("BASELINE_MISSING", issues)

    def test_wrong_baseline_kind_origin_and_digest(self):
        original = baseline_for(vocab_source())
        cases = (
            ("BASELINE_KIND", "baselineKind", "historical"),
            ("BASELINE_ORIGIN", "baselineOriginCommit", "0" * 40),
        )
        for code, key, value in cases:
            with self.subTest(code=code):
                document = copy.deepcopy(original)
                document[key] = value
                document["contentSha256"] = validator.baseline_digest(document)
                self.assertCode(
                    code, validator.validate_baseline_document(document))
        document = copy.deepcopy(original)
        document["contentSha256"] = "0" * 64
        self.assertCode(
            "BASELINE_DIGEST",
            validator.validate_baseline_document(document))

    def test_wrong_baseline_format(self):
        document = baseline_for(vocab_source())
        document["stableIds"] = {}
        document["contentSha256"] = validator.baseline_digest(document)
        self.assertCode(
            "BASELINE_FORMAT",
            validator.validate_baseline_document(document))

    def test_deep_malformed_baseline_records_fail_even_with_valid_digest(self):
        original = baseline_for(vocab_source())
        mutations = (
            lambda value: value["stableIds"][0].__setitem__("id", 1),
            lambda value: value.__setitem__("wording", [1]),
            lambda value: value.__setitem__("policy", [None]),
            lambda value: next(
                row for row in value["policy"]
                if row["kind"] == "card")["register"].__setitem__(
                    "effective", []),
            lambda value: value.__setitem__("structure", ["x"]),
            lambda value: next(
                row for row in value["structure"]
                if row["kind"] == "card").__setitem__(
                    "acceptedAnswerCount", "0"),
            lambda value: value.__setitem__("approvedChanges", [1]),
            lambda value: value.__setitem__("approvedChanges", [""]),
            lambda value: value["legacy"].__setitem__("cards", {"topic": []}),
            lambda value: value["legacy"].__setitem__(
                "retired", {"topic": [None]}),
        )
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                document = copy.deepcopy(original)
                mutate(document)
                document["contentSha256"] = validator.baseline_digest(document)
                self.assertCode(
                    "BASELINE_FORMAT",
                    validator.validate_baseline_document(document))
                comparison_issues, _ = validator.compare_forward_baseline(
                    document, original)
                self.assertCode("BASELINE_FORMAT", comparison_issues)

    def test_duplicate_baseline_record_identities_are_rejected(self):
        original = baseline_for(vocab_source())
        for section in ("stableIds", "wording", "policy", "structure"):
            with self.subTest(section=section):
                document = copy.deepcopy(original)
                document[section].append(copy.deepcopy(document[section][0]))
                document["contentSha256"] = validator.baseline_digest(document)
                self.assertCode(
                    "BASELINE_FORMAT",
                    validator.validate_baseline_document(document))

    def test_duplicate_json_object_key_is_rejected_on_load(self):
        baseline = baseline_for(vocab_source())
        payload = validator.canonical_json(baseline)
        payload = payload.replace(
            '"formatVersion": 2,',
            '"formatVersion": 2,\\n  "formatVersion": 2,', 1)
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "baseline.json")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(payload)
            document, issues = validator.load_forward_baseline(path)
        self.assertIsNone(document)
        self.assertCode("BASELINE_FORMAT", issues)

    def test_wording_and_answer_variant_drift(self):
        source = vocab_source([card(
            acceptedAnswers=["Witam"],
            variants=[{"form": "Witam", "label": "alternative"}])])
        baseline = baseline_for(source)
        mutations = (
            lambda value: value[0]["levels"][0]["topics"][0]["cards"][0].__setitem__(
                "pl", "Dobry wieczór"),
            lambda value: value[0]["levels"][0]["topics"][0]["cards"][0][
                "acceptedAnswers"].__setitem__(0, "Hej"),
            lambda value: value[0]["levels"][0]["topics"][0]["cards"][0][
                "variants"][0].__setitem__("form", "Hej"),
        )
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                candidate_source = copy.deepcopy(source)
                mutate(candidate_source)
                issues, _ = validator.compare_forward_baseline(
                    baseline, baseline_for(candidate_source))
                self.assertCode("BASELINE_WORDING_DRIFT", issues)

    def test_podcast_intro_host_and_link_are_exactly_wording_frozen(self):
        source = podcast_source()
        baseline = baseline_for(source)
        unchanged_issues, _ = validator.compare_forward_baseline(
            baseline, baseline_for(copy.deepcopy(source)))
        self.assertEqual([], unchanged_issues)

        for field, value in (
                ("host", "Jan Testowy "),
                ("link", "https://example.test/episode?changed=1")):
            with self.subTest(field=field):
                candidate_source = copy.deepcopy(source)
                candidate_source[0]["levels"][0]["topics"][0]["cards"][0][
                    field] = value
                issues, _ = validator.compare_forward_baseline(
                    baseline, baseline_for(candidate_source))
                self.assertCode("BASELINE_WORDING_DRIFT", issues)

    def test_shipping_baseline_contains_all_intro_host_link_records(self):
        sources = validator.load_source_corpus()
        baseline, baseline_issues = validator.load_forward_baseline()
        self.assertEqual([], baseline_issues)
        candidate = validator.build_repo_candidate(sources)
        expected = [
            row for row in candidate["wording"]
            if row["field"] in {"host", "link"} and
            "/card:" in row["path"]
        ]
        actual = [
            row for row in baseline["wording"]
            if row["field"] in {"host", "link"} and
            "/card:" in row["path"]
        ]
        self.assertEqual(6, len(expected))
        self.assertEqual(expected, actual)
        self.assertEqual(3, len({
            row["path"].rsplit("/card:", 1)[1] for row in actual
        }))

    def test_valid_policy_and_scenario_cefr_drift(self):
        source = vocab_source()
        baseline = baseline_for(source)
        for key, value in (
                ("production", "recognition-only"),
                ("practice", {"typeIt": False})):
            candidate_source = copy.deepcopy(source)
            candidate_source[0]["levels"][0]["topics"][0]["cards"][0][key] = value
            issues, _ = validator.compare_forward_baseline(
                baseline, baseline_for(candidate_source))
            self.assertCode("BASELINE_POLICY_DRIFT", issues)

        source = scenario_source()
        baseline = baseline_for(source)
        candidate_source = copy.deepcopy(source)
        candidate_source[0]["levels"][0]["topics"][0]["cefr"] = "B1"
        issues, _ = validator.compare_forward_baseline(
            baseline, baseline_for(candidate_source))
        self.assertCode("BASELINE_POLICY_DRIFT", issues)

    def test_relationship_and_graph_routing_drift(self):
        cards = [
            card("a2-fixture-001", relatedIds=["a2-fixture-002"],
                 relationType="contrast"),
            card("a2-fixture-002", "Dobry wieczór", "Good evening",
                 relatedIds=["a2-fixture-001"], relationType="contrast"),
        ]
        source = vocab_source(cards)
        baseline = baseline_for(source)
        candidate_source = copy.deepcopy(source)
        candidate_source[0]["levels"][0]["topics"][0]["cards"][0][
            "relatedIds"] = []
        issues, _ = validator.compare_forward_baseline(
            baseline, baseline_for(candidate_source))
        self.assertCode("BASELINE_STRUCTURE_DRIFT", issues)

        source = scenario_source()
        baseline = baseline_for(source)
        candidate_source = copy.deepcopy(source)
        option = candidate_source[0]["levels"][0]["topics"][0][
            "scenes"]["s1"]["options"][0]
        option["goto"] = "s1"
        issues, _ = validator.compare_forward_baseline(
            baseline, baseline_for(candidate_source))
        self.assertCode("BASELINE_STRUCTURE_DRIFT", issues)

    def test_removed_and_repurposed_stable_id(self):
        source = vocab_source()
        baseline = baseline_for(source)
        removed = copy.deepcopy(source)
        removed[0]["levels"][0]["topics"][0]["cards"] = []
        issues, _ = validator.compare_forward_baseline(
            baseline, baseline_for(removed))
        self.assertCode("BASELINE_ID_REMOVED", issues)

        repurposed = copy.deepcopy(source)
        repurposed[0]["source"] = "data-b1.js"
        issues, _ = validator.compare_forward_baseline(
            baseline, baseline_for(repurposed))
        self.assertCode("BASELINE_ID_REPURPOSED", issues)

    def test_unchanged_origin_baseline(self):
        source = vocab_source()
        baseline = baseline_for(source)
        issues, delta = validator.compare_forward_baseline(
            baseline, baseline_for(copy.deepcopy(source)))
        self.assertEqual([], issues)
        self.assertEqual([], delta["idChanges"])

    def test_explicit_approved_addition_updates_baseline(self):
        source = vocab_source()
        baseline = baseline_for(source)
        candidate_source = copy.deepcopy(source)
        candidate_source[0]["levels"][0]["topics"][0]["cards"].append(
            card("a2-fixture-002", "Dobry wieczór", "Good evening"))
        candidate = baseline_for(candidate_source)
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "baseline.json")
            self.assertEqual(
                [], validator.write_json_atomic(path, baseline))
            issues, delta = validator.update_forward_baseline_file(
                path, baseline, candidate, "review/P5-123")
            self.assertEqual([], issues)
            self.assertEqual(
                ["a2-fixture-002"],
                [row["id"] for row in delta["additions"]["stableIds"]])
            updated, load_issues = validator.load_forward_baseline(path)
            self.assertEqual([], load_issues)
            self.assertEqual(
                ["review/P5-123"], updated["approvedChanges"])
            self.assertEqual(
                updated["contentSha256"],
                validator.baseline_digest(updated))

    def test_update_rejects_noop_and_missing_approval(self):
        baseline = baseline_for(vocab_source())
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "baseline.json")
            validator.write_json_atomic(path, baseline)
            issues, _ = validator.update_forward_baseline_file(
                path, baseline, copy.deepcopy(baseline), "")
        self.assertCode("BASELINE_APPROVAL_REQUIRED", issues)

        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "baseline.json")
            validator.write_json_atomic(path, baseline)
            issues, _ = validator.update_forward_baseline_file(
                path, baseline, copy.deepcopy(baseline), "review/P5-123")
        self.assertCode("BASELINE_UPDATE_NOOP", issues)

    def test_update_rejects_meaningless_approval_references(self):
        baseline = baseline_for(vocab_source())
        for approval in (" ", "x"):
            with self.subTest(approval=approval):
                with tempfile.TemporaryDirectory() as directory:
                    path = os.path.join(directory, "baseline.json")
                    validator.write_json_atomic(path, baseline)
                    issues, _ = validator.update_forward_baseline_file(
                        path, baseline, copy.deepcopy(baseline), approval)
                self.assertCode("BASELINE_APPROVAL_INVALID", issues)

    def test_update_rejects_failed_nonbaseline_validation(self):
        source = vocab_source()
        baseline = baseline_for(source)
        candidate_source = copy.deepcopy(source)
        candidate_source[0]["levels"][0]["topics"][0]["cards"].append(
            card("a2-fixture-002", "Dobry wieczór", "Good evening"))
        candidate = baseline_for(candidate_source)
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "baseline.json")
            validator.write_json_atomic(path, baseline)
            with open(path, encoding="utf-8") as handle:
                before = handle.read()
            issues, _ = validator.update_forward_baseline_file(
                path, baseline, candidate, "review/P5-123",
                [validator.issue(
                    "CARD_REQUIRED_FIELD", "Synthetic validation failure.")])
            with open(path, encoding="utf-8") as handle:
                after = handle.read()
        self.assertCode("CARD_REQUIRED_FIELD", issues)
        self.assertEqual(before, after)


class Priority5ContentPolicyTests(unittest.TestCase):
    def assertCode(self, code, issues):
        self.assertIn(code, validator.issue_codes(issues), issues)

    def test_additive_id_is_valid(self):
        source = vocab_source([
            card(),
            card("a2-fixture-002", "Dobry wieczór", "Good evening"),
        ])
        origin = {"a2", "a2-fixture", "a2-fixture-001"}
        issues = validator.validate_corpus(source, origin)
        self.assertEqual([], issues)

    def test_topic_architecture_rejects_unsupported_kinds(self):
        for authored_kind in ("vocab", "podcats", "", None):
            with self.subTest(authored_kind=authored_kind):
                topic = {"id": "a2-fixture", "kind": authored_kind,
                         "cards": []}
                self.assertCode(
                    "TOPIC_KIND_INVALID",
                    validator.validate_topic_architecture(topic, "fixture"))

    def test_topic_architecture_rejects_hybrid_containers(self):
        cases = (
            {"id": "fixture", "cards": [], "drills": []},
            {"id": "fixture", "cards": [], "scenes": {}},
            {"id": "fixture", "drills": [], "scenes": {}},
        )
        for topic in cases:
            with self.subTest(containers=sorted(
                    set(topic) & {"cards", "drills", "scenes"})):
                self.assertCode(
                    "TOPIC_CONTAINER_CONFLICT",
                    validator.validate_topic_architecture(topic, "fixture"))

    def test_topic_architecture_rejects_kind_container_mismatches(self):
        cases = (
            {"id": "fixture", "kind": "podcast", "scenes": {}},
            {"id": "fixture", "kind": "grammar", "cards": []},
            {"id": "fixture", "kind": "convo", "cards": []},
            {"id": "fixture", "drills": []},
            {"id": "fixture", "kind": "podcast"},
            {"id": "fixture", "kind": "grammar"},
            {"id": "fixture", "kind": "convo"},
        )
        for topic in cases:
            with self.subTest(topic=topic):
                self.assertCode(
                    "TOPIC_KIND_CONTAINER_MISMATCH",
                    validator.validate_topic_architecture(topic, "fixture"))

    def test_each_supported_topic_architecture_passes(self):
        topics = (
            {"id": "vocabulary", "cards": []},
            {"id": "podcast", "kind": "podcast", "cards": []},
            {"id": "grammar", "kind": "grammar", "drills": []},
            {"id": "conversation", "kind": "convo", "scenes": {}},
        )
        for topic in topics:
            with self.subTest(topic=topic["id"]):
                self.assertEqual(
                    [],
                    validator.validate_topic_architecture(topic, "fixture"))

    def test_explicit_vocab_kind_exposes_runtime_gate_and_is_rejected(self):
        source = vocab_source()
        level = source[0]["levels"][0]
        topic = level["topics"][0]
        topic["kind"] = "vocab"
        counts = validator.topic_activity_counts(level, topic)
        self.assertEqual(0, counts["typeIt"])
        self.assertEqual(0, counts["listening"])
        self.assertEqual(0, counts["mixedQuiz"])
        self.assertCode(
            "TOPIC_KIND_INVALID",
            validator.validate_corpus(
                source, validator.corpus_stable_id_set(source)))

    def test_shipping_topic_architectures_and_counts(self):
        sources = validator.load_source_corpus()
        counts = Counter()
        architecture_issues = []
        for source in sources:
            for level in source["levels"]:
                for topic in level["topics"]:
                    architecture_issues.extend(
                        validator.validate_topic_architecture(
                            topic, topic["id"]))
                    if "kind" not in topic:
                        counts["vocab"] += 1
                    else:
                        counts[topic["kind"]] += 1
        self.assertEqual([], architecture_issues)
        self.assertEqual(Counter({
            "vocab": 54,
            "grammar": 32,
            "convo": 8,
            "podcast": 3,
        }), counts)

    def test_duplicate_global_id_and_suffix(self):
        source = vocab_source([card(), card()])
        issues = validator.validate_corpus(
            source, {"a2", "a2-fixture"})
        self.assertCode("ID_DUPLICATE_GLOBAL", issues)
        self.assertCode("ID_DUPLICATE_SUFFIX", issues)

    def test_incorrect_namespace_and_suffix(self):
        source = vocab_source(
            [card("wrong-1")], topic_id="wrong-topic")
        issues = validator.validate_corpus(source, {"a2"})
        self.assertCode("ID_TOPIC_NAMESPACE", issues)
        self.assertCode("ID_CARD_NAMESPACE", issues)

        source = vocab_source([card("a2-fixture-1")])
        issues = validator.validate_corpus(
            source, {"a2", "a2-fixture"})
        self.assertCode("ID_CARD_SUFFIX", issues)

    def test_new_card_suffix_rejects_alpha_zero_and_bad_padding(self):
        origin = {"a2", "a2-fixture"}
        for stable_id in (
                "a2-fixture-alpha", "a2-fixture-000",
                "a2-fixture-01", "a2-fixture-0001"):
            with self.subTest(stable_id=stable_id):
                issues = validator.validate_corpus(
                    vocab_source([card(stable_id)]), origin)
                self.assertCode("ID_CARD_SUFFIX", issues)

    def test_new_drill_namespace_and_suffix(self):
        origin = {"building-sentences", "building-sentences-fixture"}
        valid = {
            "id": "building-sentences-fixture-001",
            "type": "choose",
            "prompt": "Wybierz.",
            "options": ["tak", "nie"],
            "answer": "tak",
        }
        self.assertNotIn(
            "ID_DRILL_NAMESPACE",
            validator.issue_codes(
                validator.validate_corpus(grammar_source([valid]), origin)))
        self.assertNotIn(
            "ID_DRILL_SUFFIX",
            validator.issue_codes(
                validator.validate_corpus(grammar_source([valid]), origin)))
        cases = (
            ("other-topic-001", "ID_DRILL_NAMESPACE"),
            ("building-sentences-fixture-alpha", "ID_DRILL_SUFFIX"),
            ("building-sentences-fixture-000", "ID_DRILL_SUFFIX"),
            ("building-sentences-fixture-01", "ID_DRILL_SUFFIX"),
        )
        for stable_id, code in cases:
            with self.subTest(stable_id=stable_id):
                drill = dict(valid, id=stable_id)
                self.assertCode(
                    code,
                    validator.validate_corpus(
                        grammar_source([drill]), origin))

    def test_exact_podcast_intro_schema_and_namespace(self):
        source = podcast_source()
        origin = {"podcasts", "podcasts-fixture"}
        self.assertEqual([], validator.validate_corpus(source, origin))

        intro = copy.deepcopy(source[0]["levels"][0]["topics"][0]["cards"][0])
        intro["id"] = "podcasts-fixture-001"
        issues = validator.validate_corpus(
            podcast_source([intro]), origin)
        self.assertCode("ID_INTRO_NAMESPACE", issues)

        standard = card("podcasts-fixture-intro")
        issues = validator.validate_corpus(
            podcast_source([standard]), origin)
        self.assertCode("ID_CARD_SUFFIX", issues)

    def test_intro_requires_exact_true_fields_and_supported_keys(self):
        valid = podcast_source()[0]["levels"][0]["topics"][0]["cards"][0]
        self.assertEqual([], validator.validate_card(valid, "fixture"))

        for field in ("host", "link"):
            for malformed_value in ("", None, 1):
                with self.subTest(
                        field=field, malformed_value=malformed_value):
                    malformed = copy.deepcopy(valid)
                    malformed[field] = malformed_value
                    self.assertCode(
                        "INTRO_REQUIRED_FIELD",
                        validator.validate_card(malformed, "fixture"))

        malformed = copy.deepcopy(valid)
        malformed["ex"] = "Unsupported."
        self.assertCode(
            "INTRO_FIELD_UNSUPPORTED",
            validator.validate_card(malformed, "fixture"))

        malformed = card("podcasts-fixture-001", intro=False)
        self.assertCode(
            "INTRO_FLAG_INVALID",
            validator.validate_card(malformed, "fixture"))

    def test_intro_is_supported_only_in_podcast_topics(self):
        intro = copy.deepcopy(
            podcast_source()[0]["levels"][0]["topics"][0]["cards"][0])
        intro["id"] = "a2-fixture-intro"
        issues = validator.validate_corpus(
            vocab_source([intro]), {"a2", "a2-fixture"})
        self.assertCode("INTRO_TOPIC_UNSUPPORTED", issues)

    def test_missing_standard_card_fields(self):
        broken = card()
        for key in ("pl", "en", "hint", "ex", "exEn"):
            broken[key] = ""
        issues = validator.validate_card(broken, "fixture")
        self.assertGreaterEqual(
            [item["code"] for item in issues].count("CARD_REQUIRED_FIELD"), 5)

    def test_invalid_usage_and_practice_values(self):
        for key, value in (
                ("register", "ceremonial"),
                ("region", "krakow"),
                ("production", "sometimes")):
            with self.subTest(key=key):
                issues = validator.validate_card(
                    card(**{key: value}), "fixture")
                self.assertCode("CARD_POLICY_ENUM", issues)
        self.assertCode(
            "CARD_PRACTICE_INVALID",
            validator.validate_card(
                card(practice={"typeIt": "false"}), "fixture"))
        self.assertCode(
            "CARD_PRACTICE_UNKNOWN",
            validator.validate_card(
                card(practice={"listening": False}), "fixture"))

    def test_template_audio_and_recognition_policy(self):
        issues = validator.validate_card(card(
            cardType="template",
            pattern="Powiedz {coś}.",
            audioText="Powiedz...",
        ), "fixture")
        self.assertCode("TEMPLATE_AUDIO_INCOMPLETE", issues)
        issues = validator.validate_card(card(
            cardType="template",
            pattern="Powiedz {coś}.",
            production="recognition-only",
        ), "fixture")
        self.assertCode("TEMPLATE_RECOGNITION_ONLY", issues)

    def test_invalid_accepted_answers(self):
        fixtures = (
            ("ACCEPTED_ANSWER_INVALID", []),
            ("ACCEPTED_ANSWER_INVALID", [""]),
            ("ACCEPTED_ANSWER_CANONICAL", ["dzień dobry!"]),
            ("ACCEPTED_ANSWER_DUPLICATE", ["Witam", "witam!"]),
        )
        for code, answers in fixtures:
            with self.subTest(code=code, answers=answers):
                issues = validator.validate_card(
                    card(acceptedAnswers=answers), "fixture")
                self.assertCode(code, issues)

    def test_new_strict_replica(self):
        source = vocab_source([
            card(),
            card("a2-fixture-002"),
        ])
        issues = validator.validate_corpus(
            source, {"a2", "a2-fixture", "a2-fixture-001"})
        self.assertCode("DUPLICATE_STRICT_REPLICA", issues)

    def test_reviewed_strict_replica_is_explicitly_allowed(self):
        source = vocab_source([
            card(),
            card("a2-fixture-002"),
        ])
        issues = validator.validate_corpus(
            source, {"a2", "a2-fixture", "a2-fixture-001"},
            {"reviewedReplicas": [{
                "ids": ["a2-fixture-001", "a2-fixture-002"],
                "reason": "Intentional teaching replica.",
                "reviewReference": "review/P5-123",
            }]},
        )
        self.assertNotIn(
            "DUPLICATE_STRICT_REPLICA", validator.issue_codes(issues))

    def test_bare_replica_review_list_is_rejected(self):
        source = vocab_source([
            card(),
            card("a2-fixture-002"),
        ])
        issues = validator.validate_corpus(
            source, {"a2", "a2-fixture", "a2-fixture-001"},
            {"reviewedReplicas": [[
                "a2-fixture-001", "a2-fixture-002"]]},
        )
        self.assertCode("REVIEW_EXCEPTION_FORMAT", issues)
        self.assertCode("DUPLICATE_STRICT_REPLICA", issues)

    def test_candidate_accepted_answer_ownership_collision(self):
        source = vocab_source([
            card(),
            card(
                "a2-fixture-002", "Witam", "Welcome",
                acceptedAnswers=["Dzień dobry"]),
        ])
        issues = validator.validate_corpus(
            source, {"a2", "a2-fixture", "a2-fixture-001"})
        self.assertCode("ANSWER_OWNERSHIP_COLLISION", issues)

    def test_origin_accepted_answer_ownership_is_grandfathered(self):
        source = vocab_source([
            card(),
            card(
                "a2-fixture-002", "Witam", "Welcome",
                acceptedAnswers=["Dzień dobry"]),
        ])
        issues = validator.validate_corpus(
            source, {
                "a2", "a2-fixture", "a2-fixture-001", "a2-fixture-002"})
        self.assertNotIn(
            "ANSWER_OWNERSHIP_COLLISION",
            validator.issue_codes(issues))

    def test_structured_answer_ownership_review_is_allowed(self):
        source = vocab_source([
            card(),
            card(
                "a2-fixture-002", "Witam", "Welcome",
                acceptedAnswers=["Dzień dobry"]),
        ])
        issues = validator.validate_corpus(
            source, {"a2", "a2-fixture", "a2-fixture-001"}, {
                "reviewedAnswerOwnership": [{
                    "ids": ["a2-fixture-001", "a2-fixture-002"],
                    "reason": "Both answers are accepted in this exercise.",
                    "reviewReference": "P5-456",
                }],
            })
        self.assertNotIn(
            "ANSWER_OWNERSHIP_COLLISION",
            validator.issue_codes(issues))
        self.assertNotIn(
            "REVIEW_EXCEPTION_FORMAT", validator.issue_codes(issues))

    def test_uncued_same_english_different_polish(self):
        source = vocab_source([
            card(),
            card("a2-fixture-002", "Witam", "Good morning"),
        ])
        issues = validator.validate_corpus(
            source, {"a2", "a2-fixture", "a2-fixture-001"})
        self.assertCode("PROMPT_CUE_REQUIRED", issues)

    def test_per_card_cefr(self):
        self.assertCode(
            "CEFR_CARD_UNSUPPORTED",
            validator.validate_card(card(cefr="A2"), "fixture"))

    def test_activity_expectation_conflict(self):
        source = vocab_source()
        issues = validator.validate_activity_expectations(source, {
            "a2-fixture": {
                "flashcards": 1,
                "search": 1,
                "typeIt": 0,
                "listening": 1,
                "mixedQuiz": 0,
            }
        })
        self.assertCode("ACTIVITY_EXPECTATION_CONFLICT", issues)

    def test_recognition_only_eligibility(self):
        value = card(production="recognition-only")
        self.assertTrue(validator.eligible_for(value, "flashcard"))
        self.assertTrue(validator.eligible_for(value, "search"))
        self.assertTrue(validator.eligible_for(value, "listen"))
        self.assertFalse(validator.eligible_for(value, "typeit"))
        self.assertFalse(validator.eligible_for(value, "mixed"))
        self.assertFalse(validator.eligible_for(value, "unknown"))

    def test_template_intro_and_typeit_optout_eligibility(self):
        template = card(
            cardType="template", pattern="Powiedz {coś}.")
        intro = card(intro=True)
        opted_out = card(practice={"typeIt": False})
        for value in (template, intro):
            self.assertTrue(validator.eligible_for(value, "flashcard"))
            self.assertTrue(validator.eligible_for(value, "search"))
            self.assertFalse(validator.eligible_for(value, "listen"))
            self.assertFalse(validator.eligible_for(value, "typeit"))
            self.assertFalse(validator.eligible_for(value, "mixed"))
        self.assertFalse(validator.eligible_for(opted_out, "typeit"))
        self.assertTrue(validator.eligible_for(opted_out, "mixed"))
        self.assertTrue(validator.eligible_for(opted_out, "listen"))

    def test_topic_activity_runtime_gates(self):
        ordinary = {
            "id": "b1-ordinary",
            "cards": [card("b1-ordinary-001")],
        }
        mature = {
            "id": "b1-mature",
            "mature": True,
            "cards": [card("b1-mature-001")],
        }
        level = {"id": "b1", "topics": [ordinary, mature]}
        self.assertEqual(
            1, validator.topic_activity_counts(
                level, ordinary)["typeIt"])
        mature_counts = validator.topic_activity_counts(level, mature)
        self.assertEqual(0, mature_counts["typeIt"])
        self.assertEqual(0, mature_counts["listening"])
        self.assertEqual(1, mature_counts["mixedQuiz"])

        podcast = {
            "id": "podcasts-fixture",
            "kind": "podcast",
            "cards": [card("podcasts-fixture-001")],
        }
        podcast_counts = validator.topic_activity_counts(
            {"id": "podcasts", "topics": [podcast]}, podcast)
        self.assertEqual(1, podcast_counts["flashcards"])
        self.assertEqual(1, podcast_counts["search"])
        self.assertEqual(0, podcast_counts["typeIt"])
        self.assertEqual(0, podcast_counts["listening"])
        self.assertEqual(1, podcast_counts["mixedQuiz"])

    def test_shipping_activity_totals_match_runtime(self):
        sources = validator.load_source_corpus()
        totals = {
            key: sum(
                validator.topic_activity_counts(level, topic)[key]
                for source in sources
                for level in source["levels"]
                for topic in level.get("topics", [])
                if "cards" in topic)
            for key in (
                "flashcards", "search", "typeIt", "listening", "mixedQuiz")
        }
        self.assertEqual({
            "flashcards": 1215,
            "search": 1215,
            "typeIt": 1089,
            "listening": 1113,
            "mixedQuiz": 1183,
        }, totals)

    def test_audio_normalization_parity_failure(self):
        issues = validator.validate_audio_normalization_parity(
            lambda value: value)
        self.assertCode("AUDIO_NORMALIZATION_PARITY", issues)
        self.assertEqual(
            [], validator.validate_audio_normalization_parity())

    def test_ordinary_report_cannot_write_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "report.json")
            issues = validator.validate_report_destination(path)
            self.assertCode("REPORT_WRITE_FORBIDDEN", issues)
            self.assertFalse(os.path.exists(path))

    def test_exact_existing_audio_reuse(self):
        source = vocab_source()
        baseline = baseline_for(source)
        phrases = ["Dzień dobry", "Dzień dobry!"]
        with tempfile.TemporaryDirectory() as directory:
            manifest_path = os.path.join(directory, "manifest.json")
            entries = {}
            for phrase in phrases:
                normalized = validator.pp_audio_rule.normalize(phrase)
                digest = hashlib.sha256(
                    normalized.encode("utf-8")).hexdigest()[:12]
                entries[digest] = {
                    "pl": normalized,
                    "file": os.path.join(directory, f"{digest}.mp3"),
                }
                open(entries[digest]["file"], "wb").close()
            with open(manifest_path, "w", encoding="utf-8") as handle:
                json.dump({"entries": entries}, handle)
            report = validator.build_inventory(
                source, baseline, [], manifest_path,
                os.path.join(directory, "*.mp3"))
        self.assertEqual(2, len(report["audio"]["exactManifestReuse"]))
        self.assertEqual([], report["audio"]["requiredNewUtterances"])
        self.assertEqual(2, report["audio"]["manifestEntries"])
        self.assertEqual(2, report["audio"]["mp3Files"])


class Priority5HealthcareShippingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = validator.load_source_corpus()
        cls.levels = validator.corpus_levels(cls.sources)
        cls.a2 = next(level for level in cls.levels if level["id"] == "a2")
        cls.scenario_level = next(
            level for level in cls.levels if level["id"] == "scenarios")
        cls.topic = next(
            topic for topic in cls.a2["topics"]
            if topic["id"] == HEALTHCARE_TOPIC_ID)
        cls.scenario = next(
            topic for topic in cls.scenario_level["topics"]
            if topic["id"] == HEALTHCARE_SCENARIO_ID)

    @staticmethod
    def _sha256(value):
        return hashlib.sha256(
            validator.canonical_json(value).encode("utf-8")).hexdigest()

    @classmethod
    def _candidate_ids(cls):
        return {
            HEALTHCARE_TOPIC_ID,
            HEALTHCARE_SCENARIO_ID,
            *(card["id"] for card in cls.topic["cards"]),
        }

    @staticmethod
    def _is_candidate_path(path):
        return any(marker in path for marker in (
            f"/topic:{HEALTHCARE_TOPIC_ID}",
            f"/topic:{HEALTHCARE_SCENARIO_ID}",
        ))

    @classmethod
    def _reconstruct_prior_baseline(cls, updated):
        prior = copy.deepcopy(updated)
        prior["approvedChanges"] = []
        prior["stableIds"] = [
            row for row in prior["stableIds"]
            if row["id"] not in cls._candidate_ids()
        ]
        for section in ("wording", "policy", "structure"):
            prior[section] = [
                row for row in prior[section]
                if not cls._is_candidate_path(row["path"])
            ]
        expected_extensions = {
            "data-a2.js#/level:a2": HEALTHCARE_TOPIC_ID,
            "data-scenarios.js#/level:scenarios": HEALTHCARE_SCENARIO_ID,
        }
        for path, appended_id in expected_extensions.items():
            row = next(
                record for record in prior["structure"]
                if record["path"] == path)
            if not row["topicOrder"] or row["topicOrder"][-1] != appended_id:
                raise AssertionError(
                    f"{path} is not append-only for {appended_id}")
            row["topicOrder"] = row["topicOrder"][:-1]
        prior["contentSha256"] = validator.baseline_digest(prior)
        return prior

    @classmethod
    def _reconstruct_pre_correction_baseline(cls, updated):
        prior = cls._reconstruct_pre_native_review_baseline(updated)
        if prior["approvedChanges"][-1] != \
                HEALTHCARE_PHASE_2D_APPROVAL_REFERENCE:
            raise AssertionError("Phase 2D approval is not the latest record")
        prior["approvedChanges"] = prior["approvedChanges"][:-1]
        path = (
            "data-a2.js#/level:a2/topic:a2-healthcare-appointments/"
            "card:a2-healthcare-appointments-012")
        record = next(
            row for row in prior["wording"]
            if row["path"] == path and row["field"] == "ex")
        if record["value"] != NEW_CANCELLATION_EXAMPLE:
            raise AssertionError("Phase 2D example is not canonical")
        record["value"] = OLD_CANCELLATION_EXAMPLE
        prior["contentSha256"] = validator.baseline_digest(prior)
        return prior

    @classmethod
    def _reconstruct_pre_native_review_baseline(cls, updated):
        prior = copy.deepcopy(updated)
        if prior["approvedChanges"][-1] != \
                HEALTHCARE_PHASE_2E_APPROVAL_REFERENCE:
            raise AssertionError("Phase 2E approval is not the latest record")
        prior["approvedChanges"] = prior["approvedChanges"][:-1]
        base = "data-a2.js#/level:a2/topic:a2-healthcare-appointments/card:"
        old_wording = {
            (base + "a2-healthcare-appointments-004", "pl"):
                OLD_FOLLOW_UP_MAIN,
            (base + "a2-healthcare-appointments-004", "en"):
                "It's about a follow-up appointment.",
            (base + "a2-healthcare-appointments-004", "hint"):
                ("'wizyta kontrolna' is a follow-up or check-up appointment; "
                 "the phrase does not say what the clinician will decide."),
            (base + "a2-healthcare-appointments-004", "ex"):
                OLD_FOLLOW_UP_EXAMPLE,
            (base + "a2-healthcare-appointments-004", "exEn"):
                "I'm calling because it's about a follow-up appointment.",
            (base + "a2-healthcare-appointments-012", "hint"):
                ("'odwołać' cancels the appointment; 'przełożyć' "
                 "reschedules it."),
            (base + "a2-healthcare-appointments-018", "hint"):
                ("A direct, polite and gender-neutral request. 'godzinę' "
                 "identifies the detail that should be repeated."),
        }
        for record in prior["wording"]:
            key = (record["path"], record["field"])
            if key in old_wording:
                record["value"] = old_wording.pop(key)
        if old_wording:
            raise AssertionError(
                f"Phase 2E wording records missing: {sorted(old_wording)}")
        policy = next(
            row for row in prior["policy"]
            if row["path"] == base + "a2-healthcare-appointments-004")
        if policy["practice"] != {
                "present": True, "value": {"typeIt": False}}:
            raise AssertionError("Phase 2E Type It opt-out is not canonical")
        policy["practice"] = {"present": False}
        prior["contentSha256"] = validator.baseline_digest(prior)
        return prior

    def test_locked_topic_metadata_cards_and_placement(self):
        self.assertIs(self.a2["topics"][-1], self.topic)
        self.assertEqual({
            "id": HEALTHCARE_TOPIC_ID,
            "name": "Umawianie wizyty w przychodni",
            "emoji": "📅",
            "desc": (
                "Routine clinic appointments: booking, times, changes, "
                "check-in and clarification"),
        }, {key: self.topic[key] for key in ("id", "name", "emoji", "desc")})
        cards = self.topic["cards"]
        self.assertEqual(20, len(cards))
        self.assertEqual([
            f"{HEALTHCARE_TOPIC_ID}-{index:03d}"
            for index in range(1, 21)
        ], [card["id"] for card in cards])
        self.assertEqual(
            18,
            sum(card.get("production", "active") == "active"
                for card in cards))
        self.assertEqual(
            [f"{HEALTHCARE_TOPIC_ID}-014", f"{HEALTHCARE_TOPIC_ID}-015"],
            [card["id"] for card in cards
             if card.get("production") == "recognition-only"])
        self.assertFalse(any(
            card.get("cardType") == "template" for card in cards))
        self.assertFalse(any("cefr" in card for card in cards))
        self.assertEqual(HEALTHCARE_TOPIC_SHA256, self._sha256(self.topic))

    def test_native_review_card_fields_and_hint_only_alternatives(self):
        cards = {card["id"]: card for card in self.topic["cards"]}
        card_004 = cards["a2-healthcare-appointments-004"]
        self.assertEqual({
            "id": "a2-healthcare-appointments-004",
            "pl": NEW_FOLLOW_UP_MAIN,
            "en": "I'm calling about a follow-up appointment.",
            "practice": {"typeIt": False},
            "hint": (
                "Use this as a complete opening. “Chodzi o wizytę "
                "kontrolną” is natural when answering a question about the "
                "reason for the call. 'wizyta kontrolna' is a follow-up or "
                "check-up appointment; the phrase does not say what the "
                "clinician will decide."),
            "ex": NEW_FOLLOW_UP_EXAMPLE,
            "exEn": "Hello, I'm calling about a follow-up appointment.",
        }, card_004)
        self.assertIn(
            "“Chodzi o wizytę kontrolną” is natural when answering a "
            "question about the reason for the call.", card_004["hint"])

        card_012 = cards["a2-healthcare-appointments-012"]
        self.assertEqual({
            "id": "a2-healthcare-appointments-012",
            "pl": "Muszę odwołać wizytę.",
            "en": "I need to cancel the appointment.",
            "hint": (
                "'odwołać' cancels the appointment; 'przełożyć' "
                "reschedules it. A common alternative is “odwołać "
                "jutrzejszą wizytę” — “to cancel tomorrow’s appointment”."),
            "ex": NEW_CANCELLATION_EXAMPLE,
            "exEn": "I'm calling to cancel tomorrow's appointment.",
        }, card_012)
        self.assertIn("odwołać jutrzejszą wizytę", card_012["hint"])

        card_018 = cards["a2-healthcare-appointments-018"]
        self.assertEqual({
            "id": "a2-healthcare-appointments-018",
            "pl": "Proszę powtórzyć godzinę.",
            "en": "Please repeat the time.",
            "hint": (
                "A direct, polite and gender-neutral request. 'godzinę' "
                "identifies the detail that should be repeated. For a female "
                "receptionist: “Czy mogłaby Pani powtórzyć, o której jest "
                "wizyta?” For a male receptionist: “Czy mógłby Pan "
                "powtórzyć, o której jest wizyta?” These are more deferential "
                "alternatives."),
            "ex": "Proszę powtórzyć, o której jest wizyta.",
            "exEn": "Please repeat what time the appointment is.",
        }, card_018)
        self.assertNotIn("mogłaby/mógłby", card_018["hint"])
        self.assertNotIn("Pani/Pan", card_018["hint"])
        self.assertIn(
            "Czy mogłaby Pani powtórzyć, o której jest wizyta?",
            card_018["hint"])
        self.assertIn(
            "Czy mógłby Pan powtórzyć, o której jest wizyta?",
            card_018["hint"])

        learner_data = validator.canonical_json(self.sources)
        self.assertNotIn(OLD_FOLLOW_UP_EXAMPLE, learner_data)
        self.assertNotIn(OLD_CANCELLATION_EXAMPLE, learner_data)
        self.assertEqual(1, learner_data.count(NEW_CANCELLATION_EXAMPLE))

    def test_accepted_answer_ownership_and_removed_unnecessary_cue(self):
        cards = {card["id"]: card for card in self.topic["cards"]}
        accepted = {
            stable_id: value["acceptedAnswers"]
            for stable_id, value in cards.items()
            if "acceptedAnswers" in value
        }
        self.assertEqual({
            f"{HEALTHCARE_TOPIC_ID}-003": ["Czy mogę umówić wizytę?"],
            f"{HEALTHCARE_TOPIC_ID}-008": [
                "Czy są jakieś wolne terminy po południu?"],
            f"{HEALTHCARE_TOPIC_ID}-016": [
                "Czy mam przynieść skierowanie na tę wizytę?"],
        }, accepted)
        self.assertEqual({}, {
            stable_id: value["typeItCue"]
            for stable_id, value in cards.items()
            if "typeItCue" in value
        })

        card_016 = cards[f"{HEALTHCARE_TOPIC_ID}-016"]
        normalized_prompt = " ".join(card_016["en"].casefold().split())
        productive_prompt_group = [
            value for level in self.levels
            for topic in level.get("topics", [])
            for value in topic.get("cards", [])
            if validator.eligible_for(value, "mixed")
            and " ".join(value.get("en", "").casefold().split())
            == normalized_prompt
        ]
        self.assertEqual(
            [f"{HEALTHCARE_TOPIC_ID}-016"],
            [value["id"] for value in productive_prompt_group])

        owners = Counter()
        for level in self.levels:
            for topic in level.get("topics", []):
                for value in topic.get("cards", []):
                    if not validator.eligible_for(value, "typeit"):
                        continue
                    for answer in [value.get("pl"), *value.get(
                            "acceptedAnswers", [])]:
                        owners[validator.answer_normalize(answer)] += 1
        for value in cards.values():
            if not validator.eligible_for(value, "typeit"):
                continue
            for answer in [value["pl"], *value.get("acceptedAnswers", [])]:
                self.assertEqual(1, owners[validator.answer_normalize(answer)])

    def test_activity_deltas_totals_and_recognition_exclusions(self):
        self.assertEqual({
            "flashcards": 20,
            "search": 20,
            "typeIt": 9,
            "listening": 20,
            "mixedQuiz": 18,
        }, validator.topic_activity_counts(self.a2, self.topic))
        totals = {
            activity: sum(
                validator.topic_activity_counts(level, topic)[activity]
                for level in self.levels
                for topic in level.get("topics", [])
                if "cards" in topic)
            for activity in (
                "flashcards", "search", "typeIt", "listening", "mixedQuiz")
        }
        self.assertEqual({
            "flashcards": 1215,
            "search": 1215,
            "typeIt": 1089,
            "listening": 1113,
            "mixedQuiz": 1183,
        }, totals)
        recognition = [
            card for card in self.topic["cards"]
            if card.get("production") == "recognition-only"]
        for card in recognition:
            self.assertTrue(validator.eligible_for(card, "flashcard"))
            self.assertTrue(validator.eligible_for(card, "search"))
            self.assertTrue(validator.eligible_for(card, "listen"))
            self.assertFalse(validator.eligible_for(card, "typeit"))
            self.assertFalse(validator.eligible_for(card, "mixed"))
        expected_opt_outs = {
            f"{HEALTHCARE_TOPIC_ID}-001": 30,
            f"{HEALTHCARE_TOPIC_ID}-003": 30,
            f"{HEALTHCARE_TOPIC_ID}-004": 36,
            f"{HEALTHCARE_TOPIC_ID}-006": 34,
            f"{HEALTHCARE_TOPIC_ID}-007": 30,
            f"{HEALTHCARE_TOPIC_ID}-008": 40,
            f"{HEALTHCARE_TOPIC_ID}-013": 32,
            f"{HEALTHCARE_TOPIC_ID}-016": 43,
            f"{HEALTHCARE_TOPIC_ID}-017": 33,
        }
        opted_out = {
            card["id"]: len(" ".join(card["pl"].split()))
            for card in self.topic["cards"]
            if card.get("practice", {}).get("typeIt") is False
        }
        self.assertEqual(expected_opt_outs, opted_out)
        cards_by_id = {card["id"]: card for card in self.topic["cards"]}
        for stable_id in expected_opt_outs:
            card = cards_by_id[stable_id]
            self.assertEqual("active", card.get("production", "active"))
            self.assertFalse(validator.eligible_for(card, "typeit"))
            self.assertTrue(validator.eligible_for(card, "mixed"))

    def test_scenario_metadata_routing_reachability_and_termination(self):
        self.assertIs(self.scenario_level["topics"][-1], self.scenario)
        self.assertEqual("A2", self.scenario["cefr"])
        self.assertEqual("convo", self.scenario["kind"])
        self.assertEqual("contact", self.scenario["start"])
        self.assertEqual(HEALTHCARE_SCENARIO_SHA256, self._sha256(self.scenario))
        scenes = self.scenario["scenes"]
        self.assertEqual(8, len(scenes))
        self.assertEqual(8, sum("npc" in scene for scene in scenes.values()))
        self.assertEqual(
            14, sum(len(scene.get("options", [])) for scene in scenes.values()))
        self.assertEqual({
            "contact": ["appointment-type", "appointment-type"],
            "appointment-type": ["availability", "availability"],
            "availability": ["offer", "offer"],
            "offer": ["confirmation", "clarification"],
            "clarification": ["confirmation", "confirmation"],
            "confirmation": ["end", "change"],
            "change": ["end", "end"],
            "end": [],
        }, {
            key: [option["goto"] for option in scene.get("options", [])]
            for key, scene in scenes.items()
        })
        self.assertEqual(
            [], validator.validate_conversation_graph(
                self.scenario, HEALTHCARE_SCENARIO_ID))

        reachable = set()
        stack = [self.scenario["start"]]
        while stack:
            key = stack.pop()
            if key in reachable:
                continue
            reachable.add(key)
            stack.extend(
                option["goto"] for option in scenes[key].get("options", []))
        self.assertEqual(set(scenes), reachable)

        reverse = {key: set() for key in scenes}
        for key, scene in scenes.items():
            for option in scene.get("options", []):
                reverse[option["goto"]].add(key)
        can_terminate = {
            key for key, scene in scenes.items() if scene.get("end") is True}
        stack = list(can_terminate)
        while stack:
            key = stack.pop()
            for parent in reverse[key]:
                if parent not in can_terminate:
                    can_terminate.add(parent)
                    stack.append(parent)
        self.assertTrue(reachable <= can_terminate)

    def test_booking_change_and_cancel_paths_are_consistent(self):
        scenes = self.scenario["scenes"]

        def route(choice_indexes):
            key = self.scenario["start"]
            for choice_index in choice_indexes:
                key = scenes[key]["options"][choice_index]["goto"]
            return key

        self.assertEqual("end", route([0, 0, 0, 0, 0]))
        self.assertEqual("end", route([0, 0, 0, 0, 1, 0]))
        self.assertEqual("end", route([0, 0, 0, 0, 1, 1]))
        self.assertEqual("end", route([0, 0, 0, 1, 0, 0]))
        friday_rows = (
            scenes["offer"]["npc"],
            scenes["clarification"]["npc"],
            scenes["clarification"]["options"][0]["pl"],
            scenes["confirmation"]["npc"],
        )
        self.assertTrue(all("piątek" in row.casefold() for row in friday_rows))
        self.assertEqual(
            "Dobrze, gotowe. Do widzenia.", scenes["end"]["npc"])
        self.assertTrue(scenes["end"]["end"])

    def test_card_to_scenario_reuse_contract(self):
        card_audio = {}
        for value in self.topic["cards"]:
            for field in ("pl", "ex"):
                card_audio.setdefault(
                    validator.pp_audio_rule.normalize(value[field]),
                    set()).add(value["id"])
        scenario_audio = []
        validator.pp_audio_rule.walk_audio_texts(
            self.scenario, scenario_audio)
        exact_reuse = set(card_audio) & {
            validator.pp_audio_rule.normalize(value)
            for value in scenario_audio
        }
        self.assertEqual({
            "Czy mogę przełożyć wizytę?",
            "Czy są wolne terminy w piątek?",
            "Czy wizyta jest potwierdzona?",
            "Dzień dobry, dzwonię w sprawie wizyty.",
            "Jaki jest najbliższy wolny termin?",
            "Muszę odwołać wizytę.",
            "Proszę powtórzyć godzinę.",
        }, exact_reuse)
        exact_reuse_ids = {
            int(stable_id.rsplit("-", 1)[1])
            for text in exact_reuse
            for stable_id in card_audio[text]
        }
        self.assertEqual({2, 6, 7, 11, 12, 18, 20}, exact_reuse_ids)
        semantic_reuse_ids = {1, 3, 4, 5, 9, 10, 16}
        self.assertEqual(
            {1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 16, 18, 20},
            exact_reuse_ids | semantic_reuse_ids)

    def test_existing_content_is_semantically_unchanged(self):
        expected = {
            "data-a2.js": (
                HEALTHCARE_TOPIC_ID,
                "61595bcbe7f5045b9b572a4d41a5f684c3442aa36c6583130c784a338ced41e4"),
            "data-scenarios.js": (
                HEALTHCARE_SCENARIO_ID,
                "6d1b9da93f67fd8d98b81d4d284cbeef6f9b09343bd529cc1cf61a609ba6c327"),
        }
        for source_name, (new_topic_id, expected_digest) in expected.items():
            with self.subTest(source=source_name):
                source = copy.deepcopy(next(
                    value for value in self.sources
                    if value["source"] == source_name))
                source["levels"][0]["topics"] = [
                    topic for topic in source["levels"][0]["topics"]
                    if topic["id"] != new_topic_id
                ]
                self.assertEqual(expected_digest, self._sha256(source))

    def test_exact_baseline_addition_classification_and_approval(self):
        updated, load_issues = validator.load_forward_baseline()
        self.assertEqual([], load_issues)
        self.assertEqual(
            [
                HEALTHCARE_APPROVAL_REFERENCE,
                HEALTHCARE_PHASE_2D_APPROVAL_REFERENCE,
                HEALTHCARE_PHASE_2E_APPROVAL_REFERENCE,
            ], updated["approvedChanges"])
        self.assertEqual(
            "d703f4041ec67cb43a2eb85553ca077f780456a2",
            updated["baselineOriginCommit"])
        self.assertEqual("7.30", updated["baselineOriginAppVersion"])
        self.assertEqual({
            "stableIds": 1675,
            "wording": 13387,
            "policy": 1312,
            "structure": 1777,
        }, {
            section: len(updated[section])
            for section in ("stableIds", "wording", "policy", "structure")
        })
        self.assertEqual(
            updated["contentSha256"], validator.baseline_digest(updated))
        self.assertEqual(
            HEALTHCARE_FORWARD_BASELINE_SHA256,
            updated["contentSha256"])

        candidate = validator.build_repo_candidate(self.sources)
        pre_native_review = self._reconstruct_pre_native_review_baseline(
            updated)
        self.assertEqual(
            HEALTHCARE_PHASE_2D_FORWARD_BASELINE_SHA256,
            pre_native_review["contentSha256"])
        self.assertEqual({
            "stableIds": 1675,
            "wording": 13387,
            "policy": 1312,
            "structure": 1777,
        }, {
            section: len(pre_native_review[section])
            for section in ("stableIds", "wording", "policy", "structure")
        })
        native_issues, native_delta = validator.compare_forward_baseline(
            pre_native_review, candidate, allow_delta=True)
        self.assertEqual([], native_issues)
        card_path = (
            "data-a2.js#/level:a2/topic:a2-healthcare-appointments/card:")
        self.assertEqual([
            (card_path + "a2-healthcare-appointments-004", "en",
             "It's about a follow-up appointment.",
             "I'm calling about a follow-up appointment."),
            (card_path + "a2-healthcare-appointments-004", "ex",
             OLD_FOLLOW_UP_EXAMPLE, NEW_FOLLOW_UP_EXAMPLE),
            (card_path + "a2-healthcare-appointments-004", "exEn",
             "I'm calling because it's about a follow-up appointment.",
             "Hello, I'm calling about a follow-up appointment."),
            (card_path + "a2-healthcare-appointments-004", "hint",
             ("'wizyta kontrolna' is a follow-up or check-up appointment; "
              "the phrase does not say what the clinician will decide."),
             ("Use this as a complete opening. “Chodzi o wizytę kontrolną” "
              "is natural when answering a question about the reason for the "
              "call. 'wizyta kontrolna' is a follow-up or check-up "
              "appointment; the phrase does not say what the clinician will "
              "decide.")),
            (card_path + "a2-healthcare-appointments-004", "pl",
             OLD_FOLLOW_UP_MAIN, NEW_FOLLOW_UP_MAIN),
            (card_path + "a2-healthcare-appointments-012", "hint",
             ("'odwołać' cancels the appointment; 'przełożyć' "
              "reschedules it."),
             ("'odwołać' cancels the appointment; 'przełożyć' reschedules "
              "it. A common alternative is “odwołać jutrzejszą wizytę” — "
              "“to cancel tomorrow’s appointment”.")),
            (card_path + "a2-healthcare-appointments-018", "hint",
             ("A direct, polite and gender-neutral request. 'godzinę' "
              "identifies the detail that should be repeated."),
             ("A direct, polite and gender-neutral request. 'godzinę' "
              "identifies the detail that should be repeated. For a female "
              "receptionist: “Czy mogłaby Pani powtórzyć, o której jest "
              "wizyta?” For a male receptionist: “Czy mógłby Pan powtórzyć, "
              "o której jest wizyta?” These are more deferential "
              "alternatives.")),
        ], [
            (change["after"]["path"], change["after"]["field"],
             change["before"]["value"], change["after"]["value"])
            for change in native_delta["wordingChanges"]
        ])
        self.assertEqual(1, len(native_delta["policyChanges"]))
        policy_change = native_delta["policyChanges"][0]
        self.assertEqual("changed", policy_change["change"])
        self.assertEqual(
            card_path + "a2-healthcare-appointments-004",
            policy_change["after"]["path"])
        self.assertEqual(
            {"present": False}, policy_change["before"]["practice"])
        self.assertEqual(
            {"present": True, "value": {"typeIt": False}},
            policy_change["after"]["practice"])
        policy_before = copy.deepcopy(policy_change["before"])
        policy_after = copy.deepcopy(policy_change["after"])
        policy_before.pop("practice")
        policy_after.pop("practice")
        self.assertEqual(policy_before, policy_after)
        self.assertFalse(native_delta["idChanges"])
        self.assertFalse(native_delta["structuralChanges"])
        self.assertFalse(native_delta["legacyChanges"])
        self.assertTrue(all(
            not rows for section in ("additions", "removals")
            for rows in native_delta[section].values()))

        pre_correction = self._reconstruct_pre_correction_baseline(updated)
        self.assertEqual(
            PRE_CORRECTION_FORWARD_BASELINE_SHA256,
            pre_correction["contentSha256"])
        self.assertEqual({
            "stableIds": 1675,
            "wording": 13387,
            "policy": 1312,
            "structure": 1777,
        }, {
            section: len(pre_correction[section])
            for section in ("stableIds", "wording", "policy", "structure")
        })
        correction_issues, correction_delta = (
            validator.compare_forward_baseline(
                pre_correction, pre_native_review, allow_delta=True))
        self.assertEqual([], correction_issues)
        self.assertEqual([{
            "before": {
                "field": "ex",
                "path": (
                    "data-a2.js#/level:a2/"
                    "topic:a2-healthcare-appointments/"
                    "card:a2-healthcare-appointments-012"),
                "value": OLD_CANCELLATION_EXAMPLE,
            },
            "after": {
                "path": (
                    "data-a2.js#/level:a2/"
                    "topic:a2-healthcare-appointments/"
                    "card:a2-healthcare-appointments-012"),
                "field": "ex",
                "value": NEW_CANCELLATION_EXAMPLE,
            },
        }], correction_delta["wordingChanges"])
        self.assertFalse(correction_delta["idChanges"])
        self.assertFalse(correction_delta["policyChanges"])
        self.assertFalse(correction_delta["structuralChanges"])
        self.assertFalse(correction_delta["legacyChanges"])
        self.assertTrue(all(
            not rows for section in ("additions", "removals")
            for rows in correction_delta[section].values()))

        prior = self._reconstruct_prior_baseline(updated)
        self.assertEqual(PRIOR_FORWARD_BASELINE_SHA256, prior["contentSha256"])
        self.assertEqual({
            "stableIds": 1653,
            "wording": 13213,
            "policy": 1290,
            "structure": 1747,
        }, {
            section: len(prior[section])
            for section in ("stableIds", "wording", "policy", "structure")
        })
        issues, delta = validator.compare_forward_baseline(
            prior, candidate, allow_delta=True)
        self.assertEqual([], issues)
        self.assertEqual(22, len(delta["additions"]["stableIds"]))
        self.assertEqual(174, len(delta["additions"]["wording"]))
        self.assertEqual(
            22,
            sum(change["change"] == "added"
                for change in delta["policyChanges"]))
        self.assertTrue(all(
            change["change"] == "added"
            for change in delta["policyChanges"]))
        self.assertEqual(
            30,
            sum(change["change"] == "added"
                for change in delta["structuralChanges"]))
        parent_changes = [
            change for change in delta["structuralChanges"]
            if change["change"] == "changed"]
        self.assertEqual({
            "data-a2.js#/level:a2",
            "data-scenarios.js#/level:scenarios",
        }, {change["after"]["path"] for change in parent_changes})
        for change in parent_changes:
            self.assertEqual(
                change["before"]["topicOrder"],
                change["after"]["topicOrder"][:-1])
        self.assertFalse(delta["wordingChanges"])
        self.assertFalse(delta["idChanges"])
        self.assertFalse(delta["legacyChanges"])
        self.assertTrue(all(not rows for rows in delta["removals"].values()))

    def test_candidate_audio_occurrences_unique_counts_and_manifest_reuse(self):
        occurrences = []
        validator.pp_audio_rule.walk_audio_texts(self.topic, occurrences)
        validator.pp_audio_rule.walk_audio_texts(self.scenario, occurrences)
        normalized = [
            validator.pp_audio_rule.normalize(value) for value in occurrences]
        self.assertEqual(62, len(normalized))
        self.assertEqual(55, len(set(normalized)))
        expected_reuse = {
            "9afb9ed22cc0": "Chciałbym umówić się na wizytę.",
            "5c70940c3de7": "Dziękuję.",
            "bf0a6eefc0f7": "Mam skierowanie do specjalisty.",
        }
        candidate_hashes = {
            hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]: value
            for value in set(normalized)
        }
        self.assertEqual(
            expected_reuse,
            {digest: candidate_hashes[digest] for digest in expected_reuse})
        self.assertEqual(52, len(set(candidate_hashes) - set(expected_reuse)))

        with open("audio-manifest.json", encoding="utf-8") as handle:
            manifest = json.load(handle)
        self.assertEqual("pl-PL-MarekNeural", manifest["voice"])
        self.assertEqual("audio", manifest["audioDir"])
        self.assertEqual(3377, len(manifest["entries"]))
        self.assertEqual(
            3377,
            len([name for name in os.listdir("audio")
                 if name.endswith(".mp3")]))
        self.assertNotIn(OLD_FOLLOW_UP_MAIN, normalized)
        self.assertNotIn(OLD_FOLLOW_UP_EXAMPLE, normalized)
        self.assertIn(NEW_FOLLOW_UP_MAIN, normalized)
        self.assertIn(NEW_FOLLOW_UP_EXAMPLE, normalized)
        self.assertNotIn(OLD_CANCELLATION_EXAMPLE, normalized)
        self.assertIn(NEW_CANCELLATION_EXAMPLE, normalized)
        for obsolete_id in (
                OLD_FOLLOW_UP_MAIN_AUDIO_ID,
                OLD_FOLLOW_UP_EXAMPLE_AUDIO_ID):
            with self.subTest(obsolete_id=obsolete_id):
                self.assertNotIn(obsolete_id, manifest["entries"])
                self.assertFalse(os.path.exists(f"audio/{obsolete_id}.mp3"))
        replacements = {
            NEW_FOLLOW_UP_MAIN_AUDIO_ID: (
                NEW_FOLLOW_UP_MAIN, NEW_FOLLOW_UP_MAIN_AUDIO_SHA256),
            NEW_FOLLOW_UP_EXAMPLE_AUDIO_ID: (
                NEW_FOLLOW_UP_EXAMPLE, NEW_FOLLOW_UP_EXAMPLE_AUDIO_SHA256),
        }
        for replacement_id, (utterance, expected_sha256) in \
                replacements.items():
            with self.subTest(replacement_id=replacement_id):
                self.assertEqual({
                    "pl": utterance,
                    "file": f"audio/{replacement_id}.mp3",
                }, manifest["entries"].get(replacement_id))
                with open(f"audio/{replacement_id}.mp3", "rb") as handle:
                    replacement = handle.read()
                self.assertGreater(len(replacement), 0)
                self.assertEqual(b"\xff\xf3", replacement[:2])
                self.assertEqual(
                    expected_sha256, hashlib.sha256(replacement).hexdigest())
        hint_only = {
            "odwołać jutrzejszą wizytę",
            "Czy mogłaby Pani powtórzyć, o której jest wizyta?",
            "Czy mógłby Pan powtórzyć, o której jest wizyta?",
        }
        manifest_phrases = {
            entry["pl"] for entry in manifest["entries"].values()}
        self.assertTrue(hint_only.isdisjoint(normalized))
        self.assertTrue(hint_only.isdisjoint(manifest_phrases))
        self.assertNotIn(OLD_CANCELLATION_AUDIO_ID, manifest["entries"])
        self.assertFalse(os.path.exists(
            f"audio/{OLD_CANCELLATION_AUDIO_ID}.mp3"))
        self.assertEqual({
            "pl": NEW_CANCELLATION_EXAMPLE,
            "file": f"audio/{NEW_CANCELLATION_AUDIO_ID}.mp3",
        }, manifest["entries"].get(NEW_CANCELLATION_AUDIO_ID))
        replacement_path = f"audio/{NEW_CANCELLATION_AUDIO_ID}.mp3"
        with open(replacement_path, "rb") as handle:
            replacement = handle.read()
        self.assertGreater(len(replacement), 0)
        self.assertEqual(b"\xff\xf3", replacement[:2])
        self.assertEqual(
            NEW_CANCELLATION_AUDIO_SHA256,
            hashlib.sha256(replacement).hexdigest())
        for digest, utterance in candidate_hashes.items():
            with self.subTest(digest=digest):
                self.assertEqual({
                    "pl": utterance,
                    "file": f"audio/{digest}.mp3",
                }, manifest["entries"].get(digest))
                self.assertGreater(os.path.getsize(f"audio/{digest}.mp3"), 0)


class Priority5MalformedShapeTests(unittest.TestCase):
    def assertCode(self, code, issues):
        self.assertIn(code, validator.issue_codes(issues), issues)

    def test_source_level_topic_card_and_drill_shapes(self):
        cases = []
        cases.append(("SOURCE_CONTAINER_INVALID", None))
        for malformed in (None, "x", 1, []):
            cases.append(("SOURCE_RECORD_INVALID", [malformed]))

        source = vocab_source()
        source[0]["levels"] = {}
        cases.append(("SOURCE_LEVELS_INVALID", source))

        for malformed in (None, "x", 1, []):
            source = vocab_source()
            source[0]["levels"] = [malformed]
            cases.append(("LEVEL_RECORD_INVALID", source))

        source = vocab_source()
        source[0]["levels"][0]["topics"] = {}
        cases.append(("LEVEL_TOPICS_INVALID", source))

        for malformed in (None, "x", 1, []):
            source = vocab_source()
            source[0]["levels"][0]["topics"] = [malformed]
            cases.append(("TOPIC_RECORD_INVALID", source))

        source = vocab_source()
        source[0]["levels"][0]["topics"][0]["cards"] = {}
        cases.append(("TOPIC_CARDS_INVALID", source))

        for malformed in (None, "x", 1, []):
            source = vocab_source([malformed])
            cases.append(("CARD_RECORD_INVALID", source))

        source = grammar_source([])
        source[0]["levels"][0]["topics"][0]["drills"] = {}
        cases.append(("TOPIC_DRILLS_INVALID", source))

        for malformed in (None, "x", 1, []):
            source = grammar_source([malformed])
            cases.append(("DRILL_RECORD_INVALID", source))

        drill = {
            "id": "building-sentences-fixture-001",
            "type": "choose",
            "options": {},
            "answer": "tak",
        }
        cases.append(("DRILL_FIELD_SHAPE", grammar_source([drill])))

        for code, malformed in cases:
            with self.subTest(code=code):
                self.assertCode(code, validator.validate_corpus(malformed))

    def test_scenario_nested_shapes(self):
        cases = []
        topic = valid_scenario()
        topic["scenes"] = []
        cases.append(("GRAPH_SCENES_INVALID", topic))

        for malformed in (None, "x", 1, []):
            topic = valid_scenario()
            topic["scenes"]["s1"] = malformed
            cases.append(("GRAPH_SCENE_INVALID", topic))

        topic = valid_scenario()
        topic["scenes"]["s1"]["options"] = {}
        cases.append(("GRAPH_OPTIONS_INVALID", topic))

        for malformed in (None, "x", 1, []):
            topic = valid_scenario()
            topic["scenes"]["s1"]["options"] = [malformed]
            cases.append(("GRAPH_OPTION_INVALID", topic))

        topic = valid_scenario()
        topic["scenes"][1] = topic["scenes"].pop("s1")
        cases.append(("GRAPH_SCENE_KEY_INVALID", topic))

        topic = valid_scenario()
        topic["scenes"]["end"]["end"] = "true"
        cases.append(("GRAPH_TERMINAL_INVALID", topic))

        for code, malformed in cases:
            with self.subTest(code=code):
                self.assertCode(
                    code,
                    validator.validate_conversation_graph(
                        malformed, "fixture"))

    def test_nearby_valid_card_continues_to_be_checked(self):
        incomplete = card("a2-fixture-002")
        incomplete["pl"] = ""
        source = vocab_source([None, incomplete])
        issues = validator.validate_corpus(
            source, {"a2", "a2-fixture"})
        self.assertCode("CARD_RECORD_INVALID", issues)
        self.assertCode("CARD_REQUIRED_FIELD", issues)

    def test_cli_malformed_content_returns_one_without_traceback(self):
        incomplete = card("a2-fixture-002")
        incomplete["pl"] = ""
        sources = [None] + vocab_source([incomplete])
        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.object(
                validator, "load_source_corpus", return_value=sources):
            with contextlib.redirect_stdout(stdout), \
                    contextlib.redirect_stderr(stderr):
                status = validator.main(["--report-json", "-"])
        self.assertEqual(1, status)
        self.assertNotIn("Traceback", stdout.getvalue() + stderr.getvalue())
        report = json.loads(stdout.getvalue())
        codes = validator.issue_codes(report["validation"]["errors"])
        self.assertIn("SOURCE_RECORD_INVALID", codes)
        self.assertIn("CARD_REQUIRED_FIELD", codes)


class Priority5ConversationTests(unittest.TestCase):
    def assertCode(self, code, issues):
        self.assertIn(code, validator.issue_codes(issues), issues)

    def test_legacy_scenario_without_cefr(self):
        source = scenario_source(valid_scenario(cefr=None))
        issues = validator.validate_corpus(
            source, {"scenarios", "scenarios-fixture"})
        self.assertEqual([], issues)

    def test_new_a2_scenario_with_cefr(self):
        source = scenario_source()
        issues = validator.validate_corpus(source, {"scenarios"})
        self.assertEqual([], issues)

    def test_invalid_or_missing_new_scenario_cefr(self):
        for cefr, code in (
                ("C2", "CEFR_SCENARIO_INVALID"),
                (None, "CEFR_SCENARIO_REQUIRED")):
            with self.subTest(cefr=cefr):
                issues = validator.validate_corpus(
                    scenario_source(valid_scenario(cefr=cefr)),
                    {"scenarios"})
                self.assertCode(code, issues)

    def test_missing_and_unknown_start(self):
        topic = valid_scenario()
        del topic["start"]
        self.assertCode(
            "GRAPH_START_MISSING",
            validator.validate_conversation_graph(topic, "fixture"))
        topic = valid_scenario()
        topic["start"] = "missing"
        self.assertCode(
            "GRAPH_START_UNKNOWN",
            validator.validate_conversation_graph(topic, "fixture"))

    def test_unknown_goto(self):
        topic = valid_scenario()
        topic["scenes"]["s1"]["options"][0]["goto"] = "missing"
        self.assertCode(
            "GRAPH_GOTO_UNKNOWN",
            validator.validate_conversation_graph(topic, "fixture"))

    def test_unreachable_scene(self):
        topic = valid_scenario()
        topic["scenes"]["unused"] = {
            "npc": "Nie używaj.",
            "npcEn": "Do not use.",
            "end": True,
        }
        self.assertCode(
            "GRAPH_UNREACHABLE",
            validator.validate_conversation_graph(topic, "fixture"))

    def test_duplicate_scene_key_sequence(self):
        self.assertCode(
            "GRAPH_SCENE_KEY_DUPLICATE",
            validator.validate_unique_scene_keys(
                ["start", "end", "start"], "fixture"))

    def test_non_terminating_reachable_cycle(self):
        topic = valid_scenario()
        topic["scenes"] = {
            "a": {
                "npc": "A", "npcEn": "A",
                "options": [{"pl": "B", "en": "B", "goto": "b"}],
            },
            "b": {
                "npc": "B", "npcEn": "B",
                "options": [{"pl": "A", "en": "A", "goto": "a"}],
            },
        }
        topic["start"] = "a"
        issues = validator.validate_conversation_graph(topic, "fixture")
        self.assertCode("GRAPH_NO_TERMINAL", issues)
        self.assertCode("GRAPH_NON_TERMINATING", issues)

    def test_missing_option_language(self):
        topic = valid_scenario()
        del topic["scenes"]["s1"]["options"][0]["en"]
        self.assertCode(
            "GRAPH_OPTION_LANGUAGE",
            validator.validate_conversation_graph(topic, "fixture"))

    def test_valid_terminating_graph(self):
        self.assertEqual(
            [],
            validator.validate_conversation_graph(
                valid_scenario(), "fixture"))


if __name__ == "__main__":
    unittest.main()
