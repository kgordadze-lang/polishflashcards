"""Maintained current regressions extracted from the Phase 4D1 UI test."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")


def extract_function(source: str, name: str) -> str:
    match = re.search(rf"function {re.escape(name)}\([^)]*\)\{{", source)
    if not match:
        raise AssertionError(f"missing function {name}")
    depth = 0
    for index in range(match.end() - 1, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[match.start():index + 1]
    raise AssertionError(f"unterminated function {name}")


class CurrentSpeakerIconUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.renderer = extract_function(INDEX, "pRenderLemma")

    def test_verb_patterns_reuses_the_shared_svg(self):
        self.assertIn(
            'const audio = pEl("button", "mini-audio vp-example-audio", null);',
            self.renderer)
        self.assertIn("audio.innerHTML = G_AUDIO;", self.renderer)
        self.assertNotIn('audio.textContent = "🔊";', self.renderer)
        self.assertIn(
            "const G_AUDIO='<svg viewBox=\"0 0 24 24\" fill=\"none\" "
            "stroke=\"currentColor\"", INDEX)
        self.assertIn("'+G_AUDIO+'</button>", INDEX)

    def test_pattern_audio_wiring_and_readiness(self):
        self.assertIn('audio.type = "button";', self.renderer)
        self.assertIn(
            'audio.setAttribute("data-say", encodeURIComponent(pattern.example.pl));',
            self.renderer)
        self.assertIn(
            'ppSetAudioControlName(audio, "Play example sentence", pattern.example.pl);',
            self.renderer)
        self.assertIn(
            'audio.disabled = audioManifestStatus === "loading";', self.renderer)
        self.assertIn('document.querySelectorAll(".vp-example-audio")', INDEX)

    def test_shared_icon_styling_and_state_colours(self):
        self.assertIn(
            ".mini-audio{flex:0 0 auto;width:36px;height:36px;border-radius:50%;"
            "border:none;background:#fff;color:var(--mint-text);", INDEX)
        self.assertIn(".mini-audio:hover{background:var(--emerald);color:#fff}", INDEX)
        self.assertIn(".mini-audio svg{width:15px;height:15px}", INDEX)
        self.assertIn(
            ".fab.speaking,.ex-audio.speaking,.mini-audio.speaking{"
            "background:var(--emerald);color:#fff;animation:speakPulse .9s ease infinite}",
            INDEX)
        vp_rule = re.search(r"\.vp-example-audio\{[^}]*\}", INDEX)
        self.assertIsNotNone(vp_rule)
        self.assertNotIn("font-size", vp_rule.group(0))

    def test_audio_player_and_fallback_paths(self):
        speak_text = extract_function(INDEX, "speakText")
        fallback = extract_function(INDEX, "speakFallback")
        pre_generated = extract_function(INDEX, "playPreGenerated")
        self.assertIn("if(file){", speak_text)
        self.assertIn("playPreGenerated(file, btn, txt);", speak_text)
        self.assertIn("speakFallback(txt, btn, false);", speak_text)
        self.assertIn("new Audio(file)", pre_generated)
        self.assertIn("speakFallback(originalText, btn, true);", pre_generated)
        self.assertIn("new SpeechSynthesisUtterance(txt)", fallback)
        self.assertIn("speechSynthesis.speak(u);", fallback)
        self.assertIn('showAudioStatus("failed", btn);', fallback)


if __name__ == "__main__":
    unittest.main()
