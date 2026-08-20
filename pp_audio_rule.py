#!/usr/bin/env python3
"""
Po polsku - the single source of truth for WHICH strings need pre-generated audio.

Why this module exists: the rule used to live in a regex duplicated across
generate_audio.py and verify_audio.py, and that regex treated EVERY `pl` field as
required audio. Template cards store a display pattern in `pl` ("Gdzie jest...?"),
so the generator dutifully synthesised unfinished phrases and the app dutifully
played them. Deciding the rule in one place, from the parsed card structure rather
than from text matching, is what stops the generator, the verifier and the app from
drifting apart again.

The Python rule here mirrors PP_USAGE.mainAudioText() in pp-usage.js exactly.
index.html decides what to PLAY with the JS copy; this module decides what to BUILD
and CHECK. tests/test_activities.js pins the JS side; validate_content.py pins this
side; both are checked against each other by validate_content.py's parity guard.

The audio-bearing fields, and where the rule applies:

    pl        main-card audio  -> STANDARD cards only (see main_audio_text)
    audioText main-card audio  -> TEMPLATE cards only, and only when complete
    ex        example sentence -> always required, unchanged
    full      drill feedback   -> always required, unchanged
    npc       scenario line    -> always required, unchanged
    eligible Verb Patterns example -> required from the validated public runtime

`ex` / `full` / `npc` are deliberately NOT filtered for completeness. Several of
them legitimately trail off mid-thought inside a longer context, and they were
never the bug: only the main-card speaker was teaching an unfinished phrase as if
it were the word being learned.
"""

import glob
import re
import json
from pathlib import Path

import json5

DATA_GLOB = "data-*.js"
VERB_PATTERNS_RUNTIME = "content/verb-patterns.json"

# Fields that always need audio exactly as authored, on any node that carries them.
EXTRA_AUDIO_FIELDS = ("ex", "full", "npc")

# What makes a string an unfinished pattern rather than something a person says:
# an ellipsis in either spelling, or a {placeholder} from a template's `pattern`.
# MUST match PP_USAGE.INCOMPLETE_MARK in pp-usage.js.
INCOMPLETE_MARK = re.compile(r"\.\.\.|…|[{}]")


# ---------------------------------------------------------------- parsing


def fix_surrogates(obj):
    """json5 decodes \\uD83C\\uDFC1-style escapes as lone surrogates; re-pair
    them so emoji survive utf-8 encoding."""
    if isinstance(obj, str):
        return obj.encode("utf-16", "surrogatepass").decode("utf-16")
    if isinstance(obj, list):
        return [fix_surrogates(x) for x in obj]
    if isinstance(obj, dict):
        return {k: fix_surrogates(v) for k, v in obj.items()}
    return obj


def load_levels(data_file):
    """Extract the object literals from EVERY PP_LEVELS.push(...) call and parse
    them. The file may contain several push calls, and string values could in
    principle contain ');' - so this walks characters with a string-aware
    parenthesis counter instead of trusting a regex. json5 then tolerates
    unquoted keys, trailing commas, and comments - the data files' whole
    grammar. A parse failure is a data-file bug worth surfacing loudly."""
    src = Path(data_file).read_text(encoding="utf-8")
    levels = []
    i = 0
    while True:
        j = src.find(".push(", i)
        if j == -1:
            break
        k = j + len(".push(")
        depth, in_str, escn = 1, None, False
        start = k
        while k < len(src) and depth:
            ch = src[k]
            if in_str:
                if escn:
                    escn = False
                elif ch == "\\":
                    escn = True
                elif ch == in_str:
                    in_str = None
            else:
                if ch in "\"'":
                    in_str = ch
                elif ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
            k += 1
        payload = src[start:k - 1].strip()
        parsed = json5.loads("[" + payload + "]")
        levels.extend(fix_surrogates(parsed))
        i = k
    if not levels:
        raise SystemExit(f"could not locate PP_LEVELS.push(...) in {data_file}")
    return levels


def normalize(text):
    """Same operations as ppNormalize() in index.html, in the same order."""
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()


# ---------------------------------------------------------------- the rule


def is_complete_utterance(text):
    """MUST match PP_USAGE.isCompleteUtterance() in pp-usage.js."""
    if not isinstance(text, str):
        return False
    t = normalize(text)
    return bool(t) and not INCOMPLETE_MARK.search(t)


def is_template(node):
    return isinstance(node, dict) and node.get("cardType") == "template"


def main_audio_text(node):
    """The string the main speaker plays for this card, or "" for no main audio.
    MUST match PP_USAGE.mainAudioText() in pp-usage.js."""
    if not isinstance(node, dict):
        return ""
    if is_template(node):
        at = node.get("audioText")
        return at if is_complete_utterance(at) else ""
    pl = node.get("pl")
    return pl if isinstance(pl, str) else ""


# ------------------------------------------------------- required audio set


def walk_audio_texts(node, out):
    """Collect every string that needs a clip, from the PARSED structure.

    Recurses into every dict and list so it finds cards, grammar teach examples,
    drill feedback and scenario lines wherever they sit, instead of assuming a
    fixed nesting depth. Each dict contributes its own main-card audio (via the
    rule) plus any ex/full/npc it carries; a template contributes no `pl`."""
    if isinstance(node, list):
        for item in node:
            walk_audio_texts(item, out)
        return
    if not isinstance(node, dict):
        return
    main = main_audio_text(node)
    if isinstance(main, str) and normalize(main):
        out.append(main)
    for field in EXTRA_AUDIO_FIELDS:
        val = node.get(field)
        if isinstance(val, str) and normalize(val):
            out.append(val)
    for val in node.values():
        walk_audio_texts(val, out)


def verb_pattern_audio_examples(runtime_path=VERB_PATTERNS_RUNTIME):
    """Return pronunciation-authorized examples from the public runtime only."""
    path = Path(runtime_path)
    if not path.is_file():
        return []
    with path.open(encoding="utf-8") as handle:
        runtime = json.load(handle)
    from priority7_tooling import validate_runtime
    issues = validate_runtime(runtime)
    if issues:
        rendered = "\n".join(str(issue) for issue in issues[:20])
        raise ValueError(
            f"Verb Patterns runtime is not valid for audio discovery:\n{rendered}")
    found = []
    for lemma in runtime["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                for example in pattern.get("examples", []):
                    if example["audioEligible"]:
                        found.append({
                            "lemmaId": lemma["id"],
                            "lemma": lemma.get("displayLemma", lemma["canonicalLemma"]),
                            "patternId": pattern["id"],
                            "exampleId": example["id"],
                            "pl": example["pl"],
                        })
    return found


def required_phrases(data_glob=DATA_GLOB,
                     runtime_path=VERB_PATTERNS_RUNTIME):
    """Ordered, de-duplicated list of every normalized phrase that must have a clip.

    This is THE required set: what generate_audio.py builds, what verify_audio.py
    checks, and the complement of what may be pruned."""
    seen = {}
    for path in sorted(glob.glob(data_glob)):
        texts = []
        walk_audio_texts(load_levels(path), texts)
        for raw in texts:
            n = normalize(raw)
            if n:
                seen.setdefault(n, True)
    for example in verb_pattern_audio_examples(runtime_path):
        n = normalize(example["pl"])
        if n:
            seen.setdefault(n, True)
    return list(seen.keys())


def template_cards(data_glob=DATA_GLOB):
    """Every cardType:"template" card, in file order. Used by the validator and by
    the audit that recalculates which clips are now obsolete."""
    found = []

    def walk(node):
        if isinstance(node, list):
            for item in node:
                walk(item)
            return
        if not isinstance(node, dict):
            return
        if is_template(node):
            found.append(node)
        for val in node.values():
            walk(val)

    for path in sorted(glob.glob(data_glob)):
        walk(load_levels(path))
    return found


if __name__ == "__main__":
    phrases = required_phrases()
    pattern_examples = verb_pattern_audio_examples()
    tmpl = template_cards()
    with_audio = [c for c in tmpl if main_audio_text(c)]
    print(f"{len(phrases)} phrases require audio")
    print(f"{len(pattern_examples)} pronunciation-eligible Verb Patterns examples")
    print(f"{len(tmpl)} template cards, {len(with_audio)} with a complete audioText, "
          f"{len(tmpl) - len(with_audio)} with no main-card audio")
