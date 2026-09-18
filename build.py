#!/usr/bin/env python3
"""Build EdgeTX sound theme packs (and optionally the website).

    uv run build.py                 # all themes -> out/<id>/
    uv run build.py 8bit-hero       # selected themes
    uv run build.py --site          # also site/data, site/audio, site/dl
    uv run build.py --private DIR   # overlay your own masters (DIR mirrors SOUNDS/en) -> private/
"""
import argparse
import json
import shutil
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

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
    ap.add_argument("--private", metavar="DIR")
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
    if a.private:
        src = Path(a.private)
        for tid in ids:
            dst = ROOT / "private" / tid
            shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(OUT / tid, dst)
            for f in src.rglob("*.wav"):
                target = dst / "SOUNDS" / "en" / f.relative_to(src)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, target)
            print(f"private build with your masters -> {dst}")


if __name__ == "__main__":
    main()
