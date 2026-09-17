"""Maintained current content-policy regressions extracted from Priority 5."""
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

def card(stable_id='a2-fixture-001', pl='Dzień dobry', en='Good morning', **extra):
    value = {'id': stable_id, 'pl': pl, 'en': en, 'hint': 'A useful fixture phrase.', 'ex': f'{pl}!', 'exEn': f'{en}!'}
    value.update(extra)
    return value

def vocab_source(cards=None, topic_id='a2-fixture'):
    return validator.corpus_from_levels([{'id': 'a2', 'level': 'A2', 'blurb': 'Fixture', 'topics': [{'id': topic_id, 'name': 'Fixture', 'emoji': '🧪', 'desc': 'Fixture topic', 'cards': cards if cards is not None else [card()]}]}], 'data-a2.js')

def valid_scenario(topic_id='scenarios-fixture', cefr='A2'):
    topic = {'id': topic_id, 'name': 'Fixture scenario', 'emoji': '🗣️', 'kind': 'convo', 'role': 'Learner', 'setting': 'Somewhere', 'goal': 'Finish', 'recap': 'Done', 'start': 's1', 'scenes': {'s1': {'npc': 'Dzień dobry.', 'npcEn': 'Good morning.', 'options': [{'pl': 'Dzień dobry!', 'en': 'Good morning!', 'goto': 'end'}]}, 'end': {'npc': 'Do widzenia.', 'npcEn': 'Goodbye.', 'end': True}}}
    if cefr is not None:
        topic['cefr'] = cefr
    return topic

def scenario_source(topic=None):
    return validator.corpus_from_levels([{'id': 'scenarios', 'level': 'Scenarios', 'blurb': 'Fixture', 'topics': [topic or valid_scenario()]}], 'data-scenarios.js')

def podcast_source(cards=None, topic_id='podcasts-fixture'):
    intro = {'id': f'{topic_id}-intro', 'intro': True, 'pl': 'Odcinek testowy', 'en': 'Test episode', 'hint': 'Fixture podcast introduction.', 'host': 'Jan Testowy', 'link': 'https://example.test/episode'}
    return validator.corpus_from_levels([{'id': 'podcasts', 'level': 'Podcasts', 'blurb': 'Fixture', 'topics': [{'id': topic_id, 'name': 'Fixture podcast', 'emoji': '🎙️', 'kind': 'podcast', 'desc': 'Fixture topic', 'cards': cards if cards is not None else [intro, card(f'{topic_id}-001')]}]}], 'data-podcasts.js')

def grammar_source(drills):
    return validator.corpus_from_levels([{'id': 'building-sentences', 'level': 'Grammar', 'blurb': 'Fixture', 'topics': [{'id': 'building-sentences-fixture', 'name': 'Fixture grammar', 'kind': 'grammar', 'drills': drills}]}], 'data-grammar.js')

class CurrentContentPolicyTests(unittest.TestCase):

    def assertCode(self, code, issues):
        self.assertIn(code, validator.issue_codes(issues), issues)

    def test_additive_id_is_valid(self):
        source = vocab_source([card(), card('a2-fixture-002', 'Dobry wieczór', 'Good evening')])
        origin = {'a2', 'a2-fixture', 'a2-fixture-001'}
        issues = validator.validate_corpus(source, origin)
        self.assertEqual([], issues)

    def test_topic_architecture_rejects_unsupported_kinds(self):
        for authored_kind in ('vocab', 'podcats', '', None):
            with self.subTest(authored_kind=authored_kind):
                topic = {'id': 'a2-fixture', 'kind': authored_kind, 'cards': []}
                self.assertCode('TOPIC_KIND_INVALID', validator.validate_topic_architecture(topic, 'fixture'))

    def test_topic_architecture_rejects_hybrid_containers(self):
        cases = ({'id': 'fixture', 'cards': [], 'drills': []}, {'id': 'fixture', 'cards': [], 'scenes': {}}, {'id': 'fixture', 'drills': [], 'scenes': {}})
        for topic in cases:
            with self.subTest(containers=sorted(set(topic) & {'cards', 'drills', 'scenes'})):
                self.assertCode('TOPIC_CONTAINER_CONFLICT', validator.validate_topic_architecture(topic, 'fixture'))

    def test_topic_architecture_rejects_kind_container_mismatches(self):
        cases = ({'id': 'fixture', 'kind': 'podcast', 'scenes': {}}, {'id': 'fixture', 'kind': 'grammar', 'cards': []}, {'id': 'fixture', 'kind': 'convo', 'cards': []}, {'id': 'fixture', 'drills': []}, {'id': 'fixture', 'kind': 'podcast'}, {'id': 'fixture', 'kind': 'grammar'}, {'id': 'fixture', 'kind': 'convo'})
        for topic in cases:
            with self.subTest(topic=topic):
                self.assertCode('TOPIC_KIND_CONTAINER_MISMATCH', validator.validate_topic_architecture(topic, 'fixture'))

    def test_each_supported_topic_architecture_passes(self):
        topics = ({'id': 'vocabulary', 'cards': []}, {'id': 'podcast', 'kind': 'podcast', 'cards': []}, {'id': 'grammar', 'kind': 'grammar', 'drills': []}, {'id': 'conversation', 'kind': 'convo', 'scenes': {}})
        for topic in topics:
            with self.subTest(topic=topic['id']):
                self.assertEqual([], validator.validate_topic_architecture(topic, 'fixture'))

    def test_explicit_vocab_kind_exposes_runtime_gate_and_is_rejected(self):
        source = vocab_source()
        level = source[0]['levels'][0]
        topic = level['topics'][0]
        topic['kind'] = 'vocab'
        counts = validator.topic_activity_counts(level, topic)
        self.assertEqual(0, counts['typeIt'])
        self.assertEqual(0, counts['listening'])
        self.assertEqual(0, counts['mixedQuiz'])
        self.assertCode('TOPIC_KIND_INVALID', validator.validate_corpus(source, validator.corpus_stable_id_set(source)))

    def test_duplicate_global_id_and_suffix(self):
        source = vocab_source([card(), card()])
        issues = validator.validate_corpus(source, {'a2', 'a2-fixture'})
        self.assertCode('ID_DUPLICATE_GLOBAL', issues)
        self.assertCode('ID_DUPLICATE_SUFFIX', issues)

    def test_incorrect_namespace_and_suffix(self):
        source = vocab_source([card('wrong-1')], topic_id='wrong-topic')
        issues = validator.validate_corpus(source, {'a2'})
        self.assertCode('ID_TOPIC_NAMESPACE', issues)
        self.assertCode('ID_CARD_NAMESPACE', issues)
        source = vocab_source([card('a2-fixture-1')])
        issues = validator.validate_corpus(source, {'a2', 'a2-fixture'})
        self.assertCode('ID_CARD_SUFFIX', issues)

    def test_new_card_suffix_rejects_alpha_zero_and_bad_padding(self):
        origin = {'a2', 'a2-fixture'}
        for stable_id in ('a2-fixture-alpha', 'a2-fixture-000', 'a2-fixture-01', 'a2-fixture-0001'):
            with self.subTest(stable_id=stable_id):
                issues = validator.validate_corpus(vocab_source([card(stable_id)]), origin)
                self.assertCode('ID_CARD_SUFFIX', issues)

    def test_new_drill_namespace_and_suffix(self):
        origin = {'building-sentences', 'building-sentences-fixture'}
        valid = {'id': 'building-sentences-fixture-001', 'type': 'choose', 'prompt': 'Wybierz.', 'options': ['tak', 'nie'], 'answer': 'tak'}
        self.assertNotIn('ID_DRILL_NAMESPACE', validator.issue_codes(validator.validate_corpus(grammar_source([valid]), origin)))
        self.assertNotIn('ID_DRILL_SUFFIX', validator.issue_codes(validator.validate_corpus(grammar_source([valid]), origin)))
        cases = (('other-topic-001', 'ID_DRILL_NAMESPACE'), ('building-sentences-fixture-alpha', 'ID_DRILL_SUFFIX'), ('building-sentences-fixture-000', 'ID_DRILL_SUFFIX'), ('building-sentences-fixture-01', 'ID_DRILL_SUFFIX'))
        for stable_id, code in cases:
            with self.subTest(stable_id=stable_id):
                drill = dict(valid, id=stable_id)
                self.assertCode(code, validator.validate_corpus(grammar_source([drill]), origin))

    def test_exact_podcast_intro_schema_and_namespace(self):
        source = podcast_source()
        origin = {'podcasts', 'podcasts-fixture'}
        self.assertEqual([], validator.validate_corpus(source, origin))
        intro = copy.deepcopy(source[0]['levels'][0]['topics'][0]['cards'][0])
        intro['id'] = 'podcasts-fixture-001'
        issues = validator.validate_corpus(podcast_source([intro]), origin)
        self.assertCode('ID_INTRO_NAMESPACE', issues)
        standard = card('podcasts-fixture-intro')
        issues = validator.validate_corpus(podcast_source([standard]), origin)
        self.assertCode('ID_CARD_SUFFIX', issues)

    def test_intro_requires_exact_true_fields_and_supported_keys(self):
        valid = podcast_source()[0]['levels'][0]['topics'][0]['cards'][0]
        self.assertEqual([], validator.validate_card(valid, 'fixture'))
        for field in ('host', 'link'):
            for malformed_value in ('', None, 1):
                with self.subTest(field=field, malformed_value=malformed_value):
                    malformed = copy.deepcopy(valid)
                    malformed[field] = malformed_value
                    self.assertCode('INTRO_REQUIRED_FIELD', validator.validate_card(malformed, 'fixture'))
        malformed = copy.deepcopy(valid)
        malformed['ex'] = 'Unsupported.'
        self.assertCode('INTRO_FIELD_UNSUPPORTED', validator.validate_card(malformed, 'fixture'))
        malformed = card('podcasts-fixture-001', intro=False)
        self.assertCode('INTRO_FLAG_INVALID', validator.validate_card(malformed, 'fixture'))

    def test_intro_is_supported_only_in_podcast_topics(self):
        intro = copy.deepcopy(podcast_source()[0]['levels'][0]['topics'][0]['cards'][0])
        intro['id'] = 'a2-fixture-intro'
        issues = validator.validate_corpus(vocab_source([intro]), {'a2', 'a2-fixture'})
        self.assertCode('INTRO_TOPIC_UNSUPPORTED', issues)

    def test_missing_standard_card_fields(self):
        broken = card()
        for key in ('pl', 'en', 'hint', 'ex', 'exEn'):
            broken[key] = ''
        issues = validator.validate_card(broken, 'fixture')
        self.assertGreaterEqual([item['code'] for item in issues].count('CARD_REQUIRED_FIELD'), 5)

    def test_invalid_usage_and_practice_values(self):
        for key, value in (('register', 'ceremonial'), ('region', 'krakow'), ('production', 'sometimes')):
            with self.subTest(key=key):
                issues = validator.validate_card(card(**{key: value}), 'fixture')
                self.assertCode('CARD_POLICY_ENUM', issues)
        self.assertCode('CARD_PRACTICE_INVALID', validator.validate_card(card(practice={'typeIt': 'false'}), 'fixture'))
        self.assertCode('CARD_PRACTICE_UNKNOWN', validator.validate_card(card(practice={'listening': False}), 'fixture'))

    def test_template_audio_and_recognition_policy(self):
        issues = validator.validate_card(card(cardType='template', pattern='Powiedz {coś}.', audioText='Powiedz...'), 'fixture')
        self.assertCode('TEMPLATE_AUDIO_INCOMPLETE', issues)
        issues = validator.validate_card(card(cardType='template', pattern='Powiedz {coś}.', production='recognition-only'), 'fixture')
        self.assertCode('TEMPLATE_RECOGNITION_ONLY', issues)

    def test_invalid_accepted_answers(self):
        fixtures = (('ACCEPTED_ANSWER_INVALID', []), ('ACCEPTED_ANSWER_INVALID', ['']), ('ACCEPTED_ANSWER_CANONICAL', ['dzień dobry!']), ('ACCEPTED_ANSWER_DUPLICATE', ['Witam', 'witam!']))
        for code, answers in fixtures:
            with self.subTest(code=code, answers=answers):
                issues = validator.validate_card(card(acceptedAnswers=answers), 'fixture')
                self.assertCode(code, issues)

    def test_new_strict_replica(self):
        source = vocab_source([card(), card('a2-fixture-002')])
        issues = validator.validate_corpus(source, {'a2', 'a2-fixture', 'a2-fixture-001'})
        self.assertCode('DUPLICATE_STRICT_REPLICA', issues)

    def test_reviewed_strict_replica_is_explicitly_allowed(self):
        source = vocab_source([card(), card('a2-fixture-002')])
        issues = validator.validate_corpus(source, {'a2', 'a2-fixture', 'a2-fixture-001'}, {'reviewedReplicas': [{'ids': ['a2-fixture-001', 'a2-fixture-002'], 'reason': 'Intentional teaching replica.', 'reviewReference': 'review/P5-123'}]})
        self.assertNotIn('DUPLICATE_STRICT_REPLICA', validator.issue_codes(issues))

    def test_bare_replica_review_list_is_rejected(self):
        source = vocab_source([card(), card('a2-fixture-002')])
        issues = validator.validate_corpus(source, {'a2', 'a2-fixture', 'a2-fixture-001'}, {'reviewedReplicas': [['a2-fixture-001', 'a2-fixture-002']]})
        self.assertCode('REVIEW_EXCEPTION_FORMAT', issues)
        self.assertCode('DUPLICATE_STRICT_REPLICA', issues)

    def test_candidate_accepted_answer_ownership_collision(self):
        source = vocab_source([card(), card('a2-fixture-002', 'Witam', 'Welcome', acceptedAnswers=['Dzień dobry'])])
        issues = validator.validate_corpus(source, {'a2', 'a2-fixture', 'a2-fixture-001'})
        self.assertCode('ANSWER_OWNERSHIP_COLLISION', issues)

    def test_origin_accepted_answer_ownership_is_grandfathered(self):
        source = vocab_source([card(), card('a2-fixture-002', 'Witam', 'Welcome', acceptedAnswers=['Dzień dobry'])])
        issues = validator.validate_corpus(source, {'a2', 'a2-fixture', 'a2-fixture-001', 'a2-fixture-002'})
        self.assertNotIn('ANSWER_OWNERSHIP_COLLISION', validator.issue_codes(issues))

    def test_structured_answer_ownership_review_is_allowed(self):
        source = vocab_source([card(), card('a2-fixture-002', 'Witam', 'Welcome', acceptedAnswers=['Dzień dobry'])])
        issues = validator.validate_corpus(source, {'a2', 'a2-fixture', 'a2-fixture-001'}, {'reviewedAnswerOwnership': [{'ids': ['a2-fixture-001', 'a2-fixture-002'], 'reason': 'Both answers are accepted in this exercise.', 'reviewReference': 'P5-456'}]})
        self.assertNotIn('ANSWER_OWNERSHIP_COLLISION', validator.issue_codes(issues))
        self.assertNotIn('REVIEW_EXCEPTION_FORMAT', validator.issue_codes(issues))

    def test_uncued_same_english_different_polish(self):
        source = vocab_source([card(), card('a2-fixture-002', 'Witam', 'Good morning')])
        issues = validator.validate_corpus(source, {'a2', 'a2-fixture', 'a2-fixture-001'})
        self.assertCode('PROMPT_CUE_REQUIRED', issues)

    def test_per_card_cefr(self):
        self.assertCode('CEFR_CARD_UNSUPPORTED', validator.validate_card(card(cefr='A2'), 'fixture'))

    def test_activity_expectation_conflict(self):
        source = vocab_source()
        issues = validator.validate_activity_expectations(source, {'a2-fixture': {'flashcards': 1, 'search': 1, 'typeIt': 0, 'listening': 1, 'mixedQuiz': 0}})
        self.assertCode('ACTIVITY_EXPECTATION_CONFLICT', issues)

    def test_recognition_only_eligibility(self):
        value = card(production='recognition-only')
        self.assertTrue(validator.eligible_for(value, 'flashcard'))
        self.assertTrue(validator.eligible_for(value, 'search'))
        self.assertTrue(validator.eligible_for(value, 'listen'))
        self.assertFalse(validator.eligible_for(value, 'typeit'))
        self.assertFalse(validator.eligible_for(value, 'mixed'))
        self.assertFalse(validator.eligible_for(value, 'unknown'))

    def test_template_intro_and_typeit_optout_eligibility(self):
        template = card(cardType='template', pattern='Powiedz {coś}.')
        intro = card(intro=True)
        opted_out = card(practice={'typeIt': False})
        for value in (template, intro):
            self.assertTrue(validator.eligible_for(value, 'flashcard'))
            self.assertTrue(validator.eligible_for(value, 'search'))
            self.assertFalse(validator.eligible_for(value, 'listen'))
            self.assertFalse(validator.eligible_for(value, 'typeit'))
            self.assertFalse(validator.eligible_for(value, 'mixed'))
        self.assertFalse(validator.eligible_for(opted_out, 'typeit'))
        self.assertTrue(validator.eligible_for(opted_out, 'mixed'))
        self.assertTrue(validator.eligible_for(opted_out, 'listen'))

    def test_topic_activity_runtime_gates(self):
        ordinary = {'id': 'b1-ordinary', 'cards': [card('b1-ordinary-001')]}
        mature = {'id': 'b1-mature', 'mature': True, 'cards': [card('b1-mature-001')]}
        level = {'id': 'b1', 'topics': [ordinary, mature]}
        self.assertEqual(1, validator.topic_activity_counts(level, ordinary)['typeIt'])
        mature_counts = validator.topic_activity_counts(level, mature)
        self.assertEqual(0, mature_counts['typeIt'])
        self.assertEqual(0, mature_counts['listening'])
        self.assertEqual(1, mature_counts['mixedQuiz'])
        podcast = {'id': 'podcasts-fixture', 'kind': 'podcast', 'cards': [card('podcasts-fixture-001')]}
        podcast_counts = validator.topic_activity_counts({'id': 'podcasts', 'topics': [podcast]}, podcast)
        self.assertEqual(1, podcast_counts['flashcards'])
        self.assertEqual(1, podcast_counts['search'])
        self.assertEqual(0, podcast_counts['typeIt'])
        self.assertEqual(0, podcast_counts['listening'])
        self.assertEqual(1, podcast_counts['mixedQuiz'])

    def test_audio_normalization_parity_failure(self):
        issues = validator.validate_audio_normalization_parity(lambda value: value)
        self.assertCode('AUDIO_NORMALIZATION_PARITY', issues)
        self.assertEqual([], validator.validate_audio_normalization_parity())

    def test_ordinary_report_cannot_write_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, 'report.json')
            issues = validator.validate_report_destination(path)
            self.assertCode('REPORT_WRITE_FORBIDDEN', issues)
            self.assertFalse(os.path.exists(path))

class CurrentMalformedShapeTests(unittest.TestCase):

    def assertCode(self, code, issues):
        self.assertIn(code, validator.issue_codes(issues), issues)

    def test_source_level_topic_card_and_drill_shapes(self):
        cases = []
        cases.append(('SOURCE_CONTAINER_INVALID', None))
        for malformed in (None, 'x', 1, []):
            cases.append(('SOURCE_RECORD_INVALID', [malformed]))
        source = vocab_source()
        source[0]['levels'] = {}
        cases.append(('SOURCE_LEVELS_INVALID', source))
        for malformed in (None, 'x', 1, []):
            source = vocab_source()
            source[0]['levels'] = [malformed]
            cases.append(('LEVEL_RECORD_INVALID', source))
        source = vocab_source()
        source[0]['levels'][0]['topics'] = {}
        cases.append(('LEVEL_TOPICS_INVALID', source))
        for malformed in (None, 'x', 1, []):
            source = vocab_source()
            source[0]['levels'][0]['topics'] = [malformed]
            cases.append(('TOPIC_RECORD_INVALID', source))
        source = vocab_source()
        source[0]['levels'][0]['topics'][0]['cards'] = {}
        cases.append(('TOPIC_CARDS_INVALID', source))
        for malformed in (None, 'x', 1, []):
            source = vocab_source([malformed])
            cases.append(('CARD_RECORD_INVALID', source))
        source = grammar_source([])
        source[0]['levels'][0]['topics'][0]['drills'] = {}
        cases.append(('TOPIC_DRILLS_INVALID', source))
        for malformed in (None, 'x', 1, []):
            source = grammar_source([malformed])
            cases.append(('DRILL_RECORD_INVALID', source))
        drill = {'id': 'building-sentences-fixture-001', 'type': 'choose', 'options': {}, 'answer': 'tak'}
        cases.append(('DRILL_FIELD_SHAPE', grammar_source([drill])))
        for code, malformed in cases:
            with self.subTest(code=code):
                self.assertCode(code, validator.validate_corpus(malformed))

    def test_scenario_nested_shapes(self):
        cases = []
        topic = valid_scenario()
        topic['scenes'] = []
        cases.append(('GRAPH_SCENES_INVALID', topic))
        for malformed in (None, 'x', 1, []):
            topic = valid_scenario()
            topic['scenes']['s1'] = malformed
            cases.append(('GRAPH_SCENE_INVALID', topic))
        topic = valid_scenario()
        topic['scenes']['s1']['options'] = {}
        cases.append(('GRAPH_OPTIONS_INVALID', topic))
        for malformed in (None, 'x', 1, []):
            topic = valid_scenario()
            topic['scenes']['s1']['options'] = [malformed]
            cases.append(('GRAPH_OPTION_INVALID', topic))
        topic = valid_scenario()
        topic['scenes'][1] = topic['scenes'].pop('s1')
        cases.append(('GRAPH_SCENE_KEY_INVALID', topic))
        topic = valid_scenario()
        topic['scenes']['end']['end'] = 'true'
        cases.append(('GRAPH_TERMINAL_INVALID', topic))
        for code, malformed in cases:
            with self.subTest(code=code):
                self.assertCode(code, validator.validate_conversation_graph(malformed, 'fixture'))

    def test_nearby_valid_card_continues_to_be_checked(self):
        incomplete = card('a2-fixture-002')
        incomplete['pl'] = ''
        source = vocab_source([None, incomplete])
        issues = validator.validate_corpus(source, {'a2', 'a2-fixture'})
        self.assertCode('CARD_RECORD_INVALID', issues)
        self.assertCode('CARD_REQUIRED_FIELD', issues)

    def test_cli_malformed_content_returns_one_without_traceback(self):
        incomplete = card('a2-fixture-002')
        incomplete['pl'] = ''
        sources = [None] + vocab_source([incomplete])
        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.object(validator, 'load_source_corpus', return_value=sources):
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                status = validator.main(['--report-json', '-'])
        self.assertEqual(1, status)
        self.assertNotIn('Traceback', stdout.getvalue() + stderr.getvalue())
        report = json.loads(stdout.getvalue())
        codes = validator.issue_codes(report['validation']['errors'])
        self.assertIn('SOURCE_RECORD_INVALID', codes)
        self.assertIn('CARD_REQUIRED_FIELD', codes)

class CurrentConversationTests(unittest.TestCase):

    def assertCode(self, code, issues):
        self.assertIn(code, validator.issue_codes(issues), issues)

    def test_legacy_scenario_without_cefr(self):
        source = scenario_source(valid_scenario(cefr=None))
        issues = validator.validate_corpus(source, {'scenarios', 'scenarios-fixture'})
        self.assertEqual([], issues)

    def test_new_a2_scenario_with_cefr(self):
        source = scenario_source()
        issues = validator.validate_corpus(source, {'scenarios'})
        self.assertEqual([], issues)

    def test_invalid_or_missing_new_scenario_cefr(self):
        for cefr, code in (('C2', 'CEFR_SCENARIO_INVALID'), (None, 'CEFR_SCENARIO_REQUIRED')):
            with self.subTest(cefr=cefr):
                issues = validator.validate_corpus(scenario_source(valid_scenario(cefr=cefr)), {'scenarios'})
                self.assertCode(code, issues)

    def test_missing_and_unknown_start(self):
        topic = valid_scenario()
        del topic['start']
        self.assertCode('GRAPH_START_MISSING', validator.validate_conversation_graph(topic, 'fixture'))
        topic = valid_scenario()
        topic['start'] = 'missing'
        self.assertCode('GRAPH_START_UNKNOWN', validator.validate_conversation_graph(topic, 'fixture'))

    def test_unknown_goto(self):
        topic = valid_scenario()
        topic['scenes']['s1']['options'][0]['goto'] = 'missing'
        self.assertCode('GRAPH_GOTO_UNKNOWN', validator.validate_conversation_graph(topic, 'fixture'))

    def test_unreachable_scene(self):
        topic = valid_scenario()
        topic['scenes']['unused'] = {'npc': 'Nie używaj.', 'npcEn': 'Do not use.', 'end': True}
        self.assertCode('GRAPH_UNREACHABLE', validator.validate_conversation_graph(topic, 'fixture'))

    def test_duplicate_scene_key_sequence(self):
        self.assertCode('GRAPH_SCENE_KEY_DUPLICATE', validator.validate_unique_scene_keys(['start', 'end', 'start'], 'fixture'))

    def test_non_terminating_reachable_cycle(self):
        topic = valid_scenario()
        topic['scenes'] = {'a': {'npc': 'A', 'npcEn': 'A', 'options': [{'pl': 'B', 'en': 'B', 'goto': 'b'}]}, 'b': {'npc': 'B', 'npcEn': 'B', 'options': [{'pl': 'A', 'en': 'A', 'goto': 'a'}]}}
        topic['start'] = 'a'
        issues = validator.validate_conversation_graph(topic, 'fixture')
        self.assertCode('GRAPH_NO_TERMINAL', issues)
        self.assertCode('GRAPH_NON_TERMINATING', issues)

    def test_missing_option_language(self):
        topic = valid_scenario()
        del topic['scenes']['s1']['options'][0]['en']
        self.assertCode('GRAPH_OPTION_LANGUAGE', validator.validate_conversation_graph(topic, 'fixture'))

    def test_valid_terminating_graph(self):
        self.assertEqual([], validator.validate_conversation_graph(valid_scenario(), 'fixture'))

if __name__ == "__main__":
    unittest.main()
