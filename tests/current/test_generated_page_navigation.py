import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

import build_pages


ROOT = Path(build_pages.__file__).resolve().parent
REDIRECT_STUBS = {"grammar/index.html", "vocabulary/index.html"}


class GeneratedHeaderParser(HTMLParser):
    """Record navigation semantics instead of relying on markup substrings."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.header_links = []
        self.breadcrumbs = 0
        self.app_ctas = 0

    def _in_class(self, class_name):
        return any(class_name in frame[1] for frame in self.stack)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = set(attrs.get("class", "").split())
        in_header = self._in_class("top")
        in_page_nav = self._in_class("page-nav")
        if tag == "nav" and "crumbs" in classes:
            self.breadcrumbs += 1
        if tag == "a" and "guide-primary" in classes and attrs.get("href") == "/":
            self.app_ctas += 1
        if tag == "a" and in_header:
            self.header_links.append({
                "attrs": attrs,
                "in_page_nav": in_page_nav,
                "svgs": [],
                "paths": [],
                "polylines": [],
            })
        if tag == "svg" and self.header_links and in_header:
            self.header_links[-1]["svgs"].append(attrs)
        if tag == "path" and self.header_links and in_header:
            self.header_links[-1]["paths"].append(attrs.get("d"))
        if tag == "polyline" and self.header_links and in_header:
            self.header_links[-1]["polylines"].append(attrs.get("points"))
        if tag not in {"meta", "link", "br", "img", "hr", "path", "polyline"}:
            self.stack.append((tag, classes))

    def handle_endtag(self, tag):
        # HTMLParser reports XHTML-style <path/> as a start/end pair. Only pop
        # a matching open container so an SVG child cannot accidentally close
        # its surrounding anchor or navigation element in this audit parser.
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()


class CurrentGeneratedPageNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.documents, _slugs, _vslugs, _audio, _notes = build_pages.render_documents()
        cls.pages = {
            relative: markup
            for relative, markup in cls.documents.items()
            if relative not in REDIRECT_STUBS
        }

    @staticmethod
    def expected_back_target(relative):
        return "/" if relative == "guide/index.html" else "/guide/"

    def parse(self, markup):
        parser = GeneratedHeaderParser()
        parser.feed(markup)
        return parser

    def test_every_intended_page_has_deterministic_back_and_home_links(self):
        self.assertEqual(len(self.pages), 31)
        self.assertEqual(sum(path.startswith("grammar/") for path in self.pages), 23)
        self.assertEqual(sum(path.startswith("vocabulary/") for path in self.pages), 6)
        self.assertEqual(sum(path.startswith("guide/") for path in self.pages), 2)

        for relative, markup in self.pages.items():
            with self.subTest(page=relative):
                parser = self.parse(markup)
                controls = [link for link in parser.header_links if link["in_page_nav"]]
                self.assertEqual(len(controls), 2)
                by_name = {link["attrs"].get("aria-label"): link for link in controls}
                self.assertEqual(set(by_name), {"Back", "Home page"})
                self.assertEqual(by_name["Back"]["attrs"].get("href"),
                                 self.expected_back_target(relative))
                self.assertEqual(by_name["Home page"]["attrs"].get("href"), "/")
                for control in controls:
                    self.assertEqual(control["attrs"].get("class"), "page-nav-link")
                    self.assertNotIn("tabindex", control["attrs"])
                    self.assertFalse(any(name.startswith("on") for name in control["attrs"]))
                    self.assertFalse(control["attrs"]["href"].lower().startswith("javascript:"))

    def test_page_class_hierarchy_and_listening_page_are_explicit(self):
        expected = {
            "guide/index.html": "/",
            "guide/listening/index.html": "/guide/",
        }
        expected.update({path: "/guide/" for path in self.pages if path.startswith("grammar/")})
        expected.update({path: "/guide/" for path in self.pages if path.startswith("vocabulary/")})
        self.assertEqual(set(expected), set(self.pages))
        for relative, target in expected.items():
            with self.subTest(page=relative):
                controls = [link for link in self.parse(self.pages[relative]).header_links
                            if link["in_page_nav"]]
                back = next(link for link in controls
                            if link["attrs"].get("aria-label") == "Back")
                self.assertEqual(back["attrs"].get("href"), target)

        listening = self.pages["guide/listening/index.html"]
        self.assertIn("<h1>What else I listen to</h1>", listening)
        self.assertEqual({link["attrs"].get("aria-label") for link in
                          self.parse(listening).header_links if link["in_page_nav"]},
                         {"Back", "Home page"})

    def test_controls_use_the_canonical_hidden_icons(self):
        for relative, markup in self.pages.items():
            with self.subTest(page=relative):
                controls = {link["attrs"].get("aria-label"): link for link in
                            self.parse(markup).header_links if link["in_page_nav"]}
                back_svg = controls["Back"]["svgs"]
                home_svg = controls["Home page"]["svgs"]
                self.assertEqual(len(back_svg), 1)
                self.assertEqual(len(home_svg), 1)
                for svg in (back_svg[0], home_svg[0]):
                    self.assertEqual(svg.get("aria-hidden"), "true")
                    self.assertEqual(svg.get("viewbox"), "0 0 24 24")
                    self.assertEqual(svg.get("fill"), "none")
                    self.assertEqual(svg.get("stroke"), "currentColor")
                    self.assertEqual(svg.get("stroke-width"), "2.2")
                    self.assertNotIn("aria-label", svg)
                self.assertEqual(controls["Back"]["paths"], ["M15 18l-6-6 6-6"])
                self.assertEqual(controls["Home page"]["paths"],
                                 ["m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"])
                self.assertEqual(controls["Home page"]["polylines"],
                                 ["9 22 9 12 15 12 15 22"])

    def test_existing_navigation_branding_and_cta_remain(self):
        for relative, markup in self.pages.items():
            with self.subTest(page=relative):
                parser = self.parse(markup)
                logo = [link for link in parser.header_links
                        if link["attrs"].get("aria-label") == "Po polsku home"]
                self.assertEqual(len(logo), 1)
                self.assertEqual(logo[0]["attrs"].get("href"), "/")
                self.assertFalse(logo[0]["in_page_nav"])
                self.assertEqual(parser.breadcrumbs, 1)
                self.assertEqual(parser.app_ctas, 1)

    def test_navigation_introduces_no_history_or_referrer_state(self):
        generator = (ROOT / "build_pages.py").read_text(encoding="utf-8")
        rendered = "\n".join(self.pages.values())
        for forbidden in ("history.back", "history.go", "document.referrer", "sessionStorage"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, generator)
                self.assertNotIn(forbidden, rendered)

    def test_shared_header_css_has_mobile_reflow_touch_and_focus_contracts(self):
        def declarations(selector):
            match = re.search(r"(?:^|\n)" + re.escape(selector) + r"\{([^}]*)\}",
                              build_pages.STYLE)
            self.assertIsNotNone(match, selector)
            return {name.strip(): value.strip() for name, value in
                    (part.split(":", 1) for part in match.group(1).split(";") if ":" in part)}

        top = declarations(".top")
        nav = declarations(".page-nav")
        control = declarations(".page-nav-link")
        self.assertEqual(top.get("display"), "flex")
        self.assertEqual(top.get("flex-wrap"), "wrap")
        self.assertNotIn("width", top)
        self.assertEqual(nav.get("display"), "flex")
        self.assertEqual(nav.get("margin-left"), "auto")
        self.assertEqual(nav.get("max-width"), "100%")
        self.assertEqual(control.get("width"), "44px")
        self.assertEqual(control.get("height"), "44px")
        self.assertEqual(control.get("flex"), "0 0 auto")
        self.assertIn("a:focus-visible", build_pages.STYLE)

    def test_redirect_stubs_stay_outside_the_learner_header(self):
        for relative in REDIRECT_STUBS:
            with self.subTest(page=relative):
                markup = self.documents[relative]
                self.assertEqual(markup, build_pages.redirect_stub("/guide/"))
                self.assertNotIn("page-nav", markup)
                self.assertIn('<meta name="robots" content="noindex">', markup)

    def test_committed_generated_documents_are_current(self):
        for relative, rendered in self.documents.items():
            with self.subTest(page=relative):
                self.assertEqual((ROOT / relative).read_text(encoding="utf-8"), rendered)


if __name__ == "__main__":
    unittest.main()
