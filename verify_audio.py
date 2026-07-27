#!/usr/bin/env python3
"""
Po polsku - verify_audio.py
Checks that EVERY string the app can speak has a manifest entry AND a real,
non-empty MP3 on disk - and, in the other direction, that nothing in the manifest
or in audio/ is left over from a phrase that no longer needs a clip.

What counts as "needs a clip" is decided by pp_audio_rule.py, the same module
generate_audio.py builds from and the mirror of PP_USAGE.mainAudioText() in
pp-usage.js: a standard card's `pl`, a template's complete `audioText` (a template
without one has NO main-card audio), plus every `ex`, `full` and `npc`.

Run from the project root:   python3 verify_audio.py

Exit code 0 = fully covered and nothing orphaned. Missing clips are fixed by
running generate_audio.py; orphans are listed for review and never auto-deleted.
"""

import glob
import hashlib
import json
import os
import sys

from pp_audio_rule import (DATA_GLOB, load_levels, main_audio_text, normalize,
                           required_phrases, walk_audio_texts)

AUDIO_DIR = "audio"


def phrase_hash(normalized):
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]


def main():
    manifest = json.load(open("audio-manifest.json", encoding="utf-8"))["entries"]
    problems = []

    # ---- forward: every required phrase has an entry and a real file ----
    for path in sorted(glob.glob(DATA_GLOB)):
        texts = []
        walk_audio_texts(load_levels(path), texts)
        phrases = {n for n in (normalize(t) for t in texts) if n}
        missing_entry, missing_file = [], []
        for n in sorted(phrases):
            e = manifest.get(phrase_hash(n))
            if not e:
                missing_entry.append(n)
            elif not (os.path.exists(e["file"]) and os.path.getsize(e["file"]) > 0):
                missing_file.append(n)
        status = "OK" if not (missing_entry or missing_file) else "PROBLEMS"
        print(f"{path:22s} {len(phrases):4d} phrases  {status}")
        for n in missing_entry:
            problems.append(f"  no manifest entry: {n[:70]}   ({path})")
        for n in missing_file:
            problems.append(f"  clip missing/empty on disk: {n[:70]}   ({path})")

    required = required_phrases(DATA_GLOB)
    live = {phrase_hash(n) for n in required}

    # ---- reverse: nothing left over. An orphan is not cosmetic here - a clip of
    # an unfinished template phrase surviving in the manifest is exactly how the
    # app would go on playing it. ----
    stale = sorted(h for h in manifest if h not in live)
    for h in stale:
        problems.append(f"  orphaned manifest entry: {h}  {manifest[h].get('pl','')[:60]}")

    on_disk = {os.path.splitext(os.path.basename(p))[0]
               for p in glob.glob(f"{AUDIO_DIR}/*.mp3")}
    orphan_files = sorted(on_disk - live)
    for h in orphan_files:
        problems.append(f"  orphaned MP3 on disk: {AUDIO_DIR}/{h}.mp3")

    # ---- and the specific regression this rule exists to prevent ----
    tmpl_pl_played = []
    for path in sorted(glob.glob(DATA_GLOB)):

        def check(node):
            if isinstance(node, list):
                for item in node:
                    check(item)
                return
            if not isinstance(node, dict):
                return
            if node.get("cardType") == "template":
                pl = normalize(node.get("pl") or "")
                if pl and pl != normalize(main_audio_text(node) or "") \
                        and phrase_hash(pl) in manifest:
                    tmpl_pl_played.append((node.get("id", "?"), pl))
            for val in node.values():
                check(val)

        check(load_levels(path))
    for cid, pl in tmpl_pl_played:
        problems.append(f"  incomplete template pl still has a clip: {cid}  {pl[:60]}")

    print(f"\n{len(required)} required phrase(s) checked against {len(manifest)} manifest "
          f"entries and {len(on_disk)} MP3(s) on disk.")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        print("\n".join(problems))
        print("\nFix: python3 generate_audio.py   (then re-run this script)")
        print("Orphans are never deleted automatically - review them first.")
        sys.exit(1)
    print("All required phrases have verified audio, and nothing is orphaned.")


if __name__ == "__main__":
    main()
