"""Structural regression for the shared Learn card's flip-control layout."""

from html.parser import HTMLParser
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")


class Node:
    def __init__(self, tag, attrs, parent):
        self.tag = tag
        self.attrs = dict(attrs)
        self.parent = parent
        self.children = []


class Tree(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self, source):
        super().__init__()
        self.root = Node("root", [], None)
        self.stack = [self.root]
        self.ids = {}
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.stack[-1])
        node.parent.children.append(node)
        if node.attrs.get("id"):
            self.ids[node.attrs["id"]] = node
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_endtag(self, tag):
        if self.stack[-1].tag == tag:
            self.stack.pop()


DOM = Tree(INDEX)
CSS = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", INDEX, re.S))


def rule(selector):
    matches = re.findall(re.escape(selector) + r"\s*\{([^{}]*)\}", CSS)
    if not matches:
        raise AssertionError(f"No CSS rule for {selector}")
    return dict((key.strip(), value.strip()) for key, value in
                re.findall(r"([\w-]+)\s*:\s*([^;]+)", matches[0]))


class FlipControlLayoutTests(unittest.TestCase):
    def test_shared_control_row_precedes_both_flip_faces(self):
        for scene_id, flip_id, control_id in (
                ("cardView", "flip", "flipControl"),
                ("gLearn", "gFlip", "gFlipControl")):
            with self.subTest(scene=scene_id):
                flip = DOM.ids[flip_id]
                scene = flip.parent
                row = DOM.ids[control_id].parent
                self.assertEqual(scene.attrs.get("class"), "scene")
                self.assertEqual(row.attrs.get("class"), "flip-control-row")
                self.assertIs(row.parent, scene)
                self.assertEqual(scene.children[:2], [row, flip])
                self.assertEqual([n.attrs.get("class") for n in flip.children],
                                 ["face", "face back-face" if flip_id == "flip"
                                  else "face back-face g-back"])
                buttons = [n for n in row.children if n.tag == "button"]
                self.assertEqual(buttons, [DOM.ids[control_id]])
                self.assertEqual(buttons[0].attrs.get("type"), "button")
                self.assertTrue(buttons[0].attrs.get("aria-label"))
                self.assertEqual(buttons[0].attrs.get("class"), "flip-control")

    def test_control_owns_normal_flow_space_at_every_width(self):
        row = rule(".flip-control-row")
        button = rule(".flip-control")
        scene = rule(".scene")
        self.assertEqual(row["height"], "55px")
        self.assertEqual(row["display"], "flex")
        self.assertEqual(button["width"], "40px")
        self.assertEqual(button["height"], "40px")
        self.assertNotIn("position", row)
        self.assertNotIn("position", button)
        self.assertNotIn("transform", button)
        self.assertNotIn("overflow", scene)
        self.assertEqual(rule(".flip")["display"], "grid")
        self.assertEqual(rule(".face")["grid-area"], "1/1")
        self.assertEqual(CSS.count(".flip-control-row{"), 1)

    def test_behavior_accessibility_content_and_release_markers_remain(self):
        for flip_id, control_id, event in (
                ("flip", "flipControl", "flip"),
                ("gFlip", "gFlipControl", "gFlipToggle")):
            with self.subTest(control=control_id):
                self.assertEqual(INDEX.count(f'id="{control_id}"'), 1)
                self.assertIn(f'$("{control_id}").addEventListener("click", {event});', INDEX)
                self.assertIn(f'$("{flip_id}").classList.toggle("flipped")', INDEX)
                self.assertIn('class="face back-face', INDEX)
        self.assertIn('$("gPrev").addEventListener("click"', INDEX)
        self.assertIn('$("gNext").addEventListener("click"', INDEX)
        self.assertIn('$("prev").addEventListener("click"', INDEX)
        self.assertIn('$("next").addEventListener("click"', INDEX)
        grammar = (ROOT / "data-grammar.js").read_text(encoding="utf-8")
        self.assertIn('It marks the subject - the person or thing <i>doing</i> the action.', grammar)
        self.assertIn('const APP_VERSION = "9.19";', INDEX)
        worker = (ROOT / "sw.js").read_text(encoding="utf-8")
        self.assertIn('const CACHE = "popolsku-v75";', worker)
        self.assertIn('const AUDIO_CACHE = "popolsku-audio";', worker)


if __name__ == "__main__":
    unittest.main()
