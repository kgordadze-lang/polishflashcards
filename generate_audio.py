#!/usr/bin/env python3
"""
Po polsku - pre-generate native pronunciation audio (Marek Neural) and update the manifest.

How it works:
  - Scans every data-*.js file for the strings the app actually plays: each card's `pl`
    (the word/phrase), `ex` (the example sentence), `full` (the drill feedback sentence),
    and `npc` (the conversation partner's line).
  - Normalizes each string EXACTLY like ppNormalize() in index.html (strip HTML tags,
    collapse whitespace, trim) so the app's runtime lookup matches.
  - Names each clip  audio/<first-12-hex-of-sha256(normalized)>.mp3  - the same scheme
    your existing clips use, so nothing gets duplicated.
  - Incremental: only missing clips are synthesized. Existing ones are left untouched.
  - Writes/updates audio-manifest.json (map of normalized pl -> file).
  - Optional cleanup:  python3 generate_audio.py --prune  additionally removes manifest
    entries whose phrase no longer exists in any data file, and LISTS (never deletes)
    orphaned MP3s in audio/ so you can `git rm` the ones you're sure about.

Run it from the project root (where index.html and the data-*.js files live):

    pip install edge-tts
    python3 generate_audio.py

Then re-upload the new files in  audio/  plus the updated  audio-manifest.json.
Bump CACHE in sw.js (e.g. v15 -> v16) so returning users pick everything up cleanly.
"""

import argparse
import asyncio
import datetime
import glob
import hashlib
import json
import os
import re

import edge_tts

VOICE = "pl-PL-MarekNeural"   # Marek
AUDIO_DIR = "audio"
MANIFEST = "audio-manifest.json"
DATA_GLOB = "data-*.js"

# Every pl / ex / full / npc string literal, escape-aware. These are the four
# fields the app actually speaks: pl (word/front), ex (card example),
# full (drill feedback sentence), npc (conversation partner's line).
STR_RE = re.compile(r'\b(?:pl|ex|full|npc)\s*:\s*"((?:[^"\\]|\\.)*)"')


def normalize(text: str) -> str:
    """MUST match ppNormalize() in index.html - same operations, same order."""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def phrase_hash(normalized: str) -> str:
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]


def collect_phrases() -> list:
    """Ordered, de-duplicated list of every normalized pl/ex phrase in the data files."""
    seen = {}
    for path in sorted(glob.glob(DATA_GLOB)):
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        for m in STR_RE.finditer(src):
            raw = json.loads('"' + m.group(1) + '"')   # JSON-unescape the literal
            n = normalize(raw)
            if n:
                seen.setdefault(n, True)
    return list(seen.keys())


async def synth(text: str, out_path: str):
    await edge_tts.Communicate(text, VOICE).save(out_path)


async def main(prune: bool = False):
    os.makedirs(AUDIO_DIR, exist_ok=True)

    manifest = {"voice": VOICE, "generatedAt": None, "audioDir": AUDIO_DIR, "entries": {}}
    if os.path.exists(MANIFEST):
        try:
            with open(MANIFEST, encoding="utf-8") as fh:
                manifest = json.load(fh)
        except Exception:
            pass
    entries = manifest.setdefault("entries", {})

    phrases = collect_phrases()
    made = failed = 0
    failures = []
    for n in phrases:
        h = phrase_hash(n)
        rel = f"{AUDIO_DIR}/{h}.mp3"
        # Incremental - a clip counts as existing only if it's non-empty.
        # (edge-tts can leave a zero-byte file behind on a partial failure;
        # treat those as missing and re-synthesize.)
        if os.path.exists(rel) and os.path.getsize(rel) > 0:
            entries[h] = {"pl": n, "file": rel}       # keep the manifest in sync
            continue
        try:
            await synth(n, rel)
            if not (os.path.exists(rel) and os.path.getsize(rel) > 0):
                raise RuntimeError("saved file is empty")
            entries[h] = {"pl": n, "file": rel}       # only enter the manifest once the clip verifiably exists
            made += 1
            print(f"  + {h}  {n[:52]}")
        except Exception as e:
            failed += 1
            failures.append(n)
            if os.path.exists(rel) and os.path.getsize(rel) == 0:
                os.remove(rel)                        # don't leave an empty file that would block a retry
            print(f"  ! failed: {n[:52]}  ({e})")
        await asyncio.sleep(0.15)                      # be gentle on the TTS endpoint

    if prune:
        # 1. Manifest: drop entries whose phrase no longer appears in any data file.
        live = {phrase_hash(n) for n in phrases}
        stale = [h for h in entries if h not in live]
        for h in stale:
            print(f"  - pruned manifest entry {h}  {entries[h].get('pl','')[:52]}")
            del entries[h]
        # 2. Disk: LIST orphaned MP3s (present in audio/ but not needed by any
        #    current phrase). Never auto-delete - you decide what to `git rm`.
        orphans = []
        for path in sorted(glob.glob(f"{AUDIO_DIR}/*.mp3")):
            h = os.path.splitext(os.path.basename(path))[0]
            if h not in live:
                orphans.append(path)
        if stale or orphans:
            print(f"\nPrune: removed {len(stale)} stale manifest entr"
                  f"{'y' if len(stale)==1 else 'ies'}.")
        if orphans:
            print(f"{len(orphans)} orphaned clip(s) on disk - review and delete manually:")
            for p in orphans:
                print(f"  git rm {p}")

    manifest["voice"] = VOICE
    manifest["audioDir"] = AUDIO_DIR
    manifest["generatedAt"] = (
        datetime.datetime.now(datetime.timezone.utc)
        .isoformat(timespec="microseconds")
        .replace("+00:00", "Z")
    )
    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=0)

    print(f"\nDone. {made} new clip(s), {failed} failed. "
          f"Manifest now has {len(entries)} entries.")
    if failures:
        print("\nThese phrases have NO audio yet - re-run the script to retry them:")
        for n in failures:
            print(f"  - {n}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Generate missing audio clips and update the manifest.")
    ap.add_argument("--prune", action="store_true",
                    help="also remove stale manifest entries and list orphaned MP3s")
    args = ap.parse_args()
    asyncio.run(main(prune=args.prune))
