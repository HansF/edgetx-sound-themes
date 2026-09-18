#!/usr/bin/env python3
"""Build EdgeTX sound theme packs (and optionally the website).

    uv run build.py                 # all themes -> out/<id>/
    uv run build.py 8bit-hero       # selected themes
    uv run build.py --site          # also site/data, site/audio, site/dl
    uv run build.py --private       # also build private_themes/ (never published) -> private/
    uv run build.py --private --masters DIR   # ...and overlay your own WAVs (DIR mirrors SOUNDS/en)
    uv run build.py --private --site          # local site preview including private themes
"""
import argparse
import json
import os
import shutil
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

if "--private" in sys.argv:
    os.environ["STICKBEATS_PRIVATE"] = "1"   # before the registry is imported (and in workers)

from soundgen.export import build_theme
from soundgen.themes import REGISTRY

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"


def one(tid):
    t0 = time.time()
    d = OUT / tid
    shutil.rmtree(d, ignore_errors=True)
    index = build_theme(REGISTRY[tid], d)
    (d / "index.json").write_text(json.dumps(index, indent=1))
    return tid, index, time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("themes", nargs="*")
    ap.add_argument("--site", action="store_true")
    ap.add_argument("--private", action="store_true", help="include private_themes/ (local only)")
    ap.add_argument("--masters", metavar="DIR", help="overlay your own WAVs onto the private builds")
    ap.add_argument("-j", "--jobs", type=int, default=None)
    a = ap.parse_args()
    ids = a.themes or sorted(REGISTRY)
    unknown = [t for t in ids if t not in REGISTRY]
    if unknown:
        sys.exit(f"unknown theme(s): {', '.join(unknown)}; known: {', '.join(sorted(REGISTRY))}")
    results = {}
    with ProcessPoolExecutor(a.jobs) as ex:
        for tid, index, secs in ex.map(one, ids):
            results[tid] = index
            longest = max(index.values(), key=lambda v: v["dur"])
            print(f"{tid:22s} {len(index)} files  {len({v['hash'] for v in index.values()})} unique  "
                  f"longest {longest['dur']:.2f}s  {secs:.1f}s", flush=True)
    if a.site:
        from site_build import build_site
        build_site(ROOT, OUT, sorted(REGISTRY) if not a.themes else ids)
        from voices_build import build_voices
        build_voices(ROOT / "site")
        if a.private:
            print("NOTE: site/ now contains private themes. Preview locally only; CI builds the public site from git.")
    if a.private:
        for tid in ids:
            if REGISTRY[tid].category != "private":
                continue
            dst = ROOT / "private" / tid
            shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(OUT / tid, dst)
            if a.masters:
                src = Path(a.masters).expanduser()
                for f in src.rglob("*.wav"):
                    target = dst / "SOUNDS" / "en" / f.relative_to(src)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, target)
            print(f"private pack -> {dst}  (copy its SOUNDS folder to your SD card; never publish it)")

if __name__ == "__main__":
    main()
