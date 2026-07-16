#!/usr/bin/env python3
"""
Po polsku - verify_audio.py
Checks that EVERY phrase the app can speak (pl / ex / full / npc in every
data-*.js file) has a manifest entry AND a real, non-empty MP3 on disk.

Run from the project root:   python3 verify_audio.py

Exit code 0 = fully covered. Anything missing is listed; fix by running
generate_audio.py (it now only writes manifest entries for verified clips).
"""

import glob
import hashlib
import json
import os
import re
import sys

STR_RE = re.compile(r'\b(?:pl|ex|full|npc)\s*:\s*"((?:[^"\\]|\\.)*)"')


def normalize(text):
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()


def main():
    manifest = json.load(open("audio-manifest.json", encoding="utf-8"))["entries"]
    problems = []
    total = 0
    for path in sorted(glob.glob("data-*.js")):
        phrases = set()
        src = open(path, encoding="utf-8").read()
        for m in STR_RE.finditer(src):
            n = normalize(json.loads('"' + m.group(1) + '"'))
            if n:
                phrases.add(n)
        missing_entry, missing_file = [], []
        for n in phrases:
            h = hashlib.sha256(n.encode()).hexdigest()[:12]
            e = manifest.get(h)
            if not e:
                missing_entry.append(n)
            elif not (os.path.exists(e["file"]) and os.path.getsize(e["file"]) > 0):
                missing_file.append(n)
        total += len(phrases)
        status = "OK" if not (missing_entry or missing_file) else "PROBLEMS"
        print(f"{path:22s} {len(phrases):4d} phrases  {status}")
        for n in missing_entry:
            problems.append(f"  no manifest entry: {n[:70]}   ({path})")
        for n in missing_file:
            problems.append(f"  clip missing/empty on disk: {n[:70]}   ({path})")

    print(f"\n{total} unique-per-file phrases checked against {len(manifest)} manifest entries.")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        print("\n".join(problems))
        print("\nFix: python3 generate_audio.py   (then re-run this script)")
        sys.exit(1)
    print("All phrases have verified audio. Nothing to do.")


if __name__ == "__main__":
    main()
