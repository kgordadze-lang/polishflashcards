import html
import unittest

import build_pages


class ExampleEmphasisTests(unittest.TestCase):
    def test_exact_bold_pair_is_restored(self):
        self.assertEqual(
            build_pages.render_example_emphasis("To są <b>Polacy</b>."),
            "To są <b>Polacy</b>.",
        )

    def test_script_stays_escaped(self):
        rendered = build_pages.render_example_emphasis("<script>alert('x')</script>")
        self.assertNotIn("<script>", rendered)
        self.assertEqual(html.unescape(rendered), "<script>alert('x')</script>")

    def test_image_with_event_handler_stays_escaped(self):
        rendered = build_pages.render_example_emphasis('<img src=x onerror="alert(1)">')
        self.assertNotIn("<img", rendered)
        self.assertEqual(html.unescape(rendered), '<img src=x onerror="alert(1)">')

    def test_bold_tag_with_attributes_stays_escaped(self):
        rendered = build_pages.render_example_emphasis('<b class="x">word</b>')
        self.assertNotIn("<b", rendered)
        self.assertEqual(html.unescape(rendered), '<b class="x">word</b>')

    def test_unmatched_and_nested_tags_stay_escaped(self):
        cases = (
            "<b>word",
            "word</b>",
            "</b><b>word</b>",
            "<b><b>word</b></b>",
            "<b/>word",
        )
        for authored in cases:
            with self.subTest(authored=authored):
                rendered = build_pages.render_example_emphasis(authored)
                self.assertNotIn("<b>", rendered)
                self.assertNotIn("</b>", rendered)
                self.assertEqual(html.unescape(rendered), authored)

    def test_plain_polish_text_is_unchanged(self):
        authored = "Zażółć gęślą jaźń — dobrze!"
        self.assertEqual(build_pages.render_example_emphasis(authored), authored)

    def test_table_renderer_uses_the_narrow_allowlist(self):
        rendered = build_pages.render_teach_card(
            {
                "front": "Examples",
                "table": [
                    {"g": "safe", "e": "word", "ex": "<b>słowo</b>"},
                    {"g": "unsafe", "e": "word", "ex": '<img onerror="alert(1)">'},
                ],
            },
            {},
        )
        self.assertIn('<td lang="pl"><b>słowo</b></td>', rendered)
        self.assertNotIn("<img", rendered)
        self.assertIn("&lt;img onerror=&quot;alert(1)&quot;&gt;", rendered)


class AspectPairTests(unittest.TestCase):
    def test_pair_note_is_rendered_exactly_once(self):
        rendered = build_pages.vocab_card(
            {"pl": "robić", "en": "to do", "pair": "robić / zrobić"},
            {},
        )
        markup = (
            '<div class="note"><b>Aspect pair:</b> '
            '<span lang="pl">robić / zrobić</span></div>'
        )
        self.assertEqual(rendered.count(markup), 1)

    def test_card_without_pair_has_no_pair_note(self):
        rendered = build_pages.vocab_card({"pl": "dom", "en": "house"}, {})
        self.assertNotIn("Aspect pair:", rendered)


if __name__ == "__main__":
    unittest.main()
