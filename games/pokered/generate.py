"""CLEAN ROOM: write every picture of the game from games/pokered/spec + our own
drawing code into a tree that holds no retail picture.

    python -m games.pokered.generate <clean tree>

Drawers are looked up by path (first match in DRAWERS), then by kind.
"""
import fnmatch
import json
import os
import sys

import numpy as np

from cleanroom.gb import gfx
from games.pokered import drawn

HERE = os.path.dirname(os.path.abspath(__file__))
from games.pokered.art import DRAWERS


def draw_pic(rel, a):
    inside = gfx.unpack_mask(a["sil"], a["h"], a["w"])
    return drawn.autoshade(inside, a["grid"])


def draw_sprite(rel, a):
    h, w = a["h"], a["w"]
    inside = gfx.unpack_mask(a["sil"], h, w)
    out = np.zeros((h, w), np.uint8)
    for n, y in enumerate(range(0, h, 16)):
        m = inside[y:y + 16]
        f = drawn.autoshade(m, a["grid"][n], bias=0.3, bevel=0.0)
        f[m & (f == 0)] = 1                      # shade 0 is transparent on sprites
        out[y:y + 16] = f
    return out


def draw_sheet(rel, a):
    """Fallback for sheets nobody drew yet: the coarse grid, hatched."""
    h, w = a["h"], a["w"]
    t = drawn.grid_field(a["grid"], h, w)
    yy, xx = np.mgrid[0:h, 0:w]
    out = np.clip(np.round(t + ((xx + yy) % 4 == 0) * 0.8), 0, 3).astype(np.uint8)
    return out


def constrain(rel, a, idx):
    """Layout facts the build depends on: blank tiles stay blank, drawn tiles stay
    drawn, and de-duplicated pictures keep their tile equalities."""
    h, w = a["h"], a["w"]
    t = gfx.tiles(idx).copy()
    if "blank" in a:
        blank = set(a["blank"])
        for i in range(len(t)):
            if i in blank:
                t[i] = 0
            elif not t[i].any():
                t[i][7, 7] = 1 if a["depth"] == 2 else 3
    if "classes" in a:
        first, seen = {}, {}
        for i, c in enumerate(a["classes"]):
            if c in first:
                t[i] = t[first[c]]
            else:
                first[c] = i
                k = 0
                while t[i].tobytes() in seen:    # must differ from every other class
                    t[i][7 - k // 8, 7 - k % 8] ^= 1
                    k += 1
                seen[t[i].tobytes()] = c
    return gfx.untile(t, w)[:h]


def render(rel, a):
    for pat, fn in DRAWERS:
        if fnmatch.fnmatch(rel, pat):
            idx = fn(rel, a)
            if idx is not None:
                return idx, fn.__name__
    fn = {"pic": draw_pic, "sprite": draw_sprite, "sheet": draw_sheet}[a["kind"]]
    return fn(rel, a), fn.__name__


def load_drawers():
    for mod in ("font", "tilesets", "sprites", "misc", "pics"):
        if os.path.exists(os.path.join(HERE, "art", mod + ".py")):
            __import__(f"games.pokered.art.{mod}")


def main(tree, only=None):
    spec = json.load(open(os.path.join(HERE, "spec", "assets.json")))
    load_drawers()
    by = {}
    for rel, a in spec.items():
        if only and not fnmatch.fnmatch(rel, only):
            continue
        idx, who = render(rel, a)
        assert idx.shape == (a["h"], a["w"]), (rel, idx.shape)
        idx = constrain(rel, a, np.asarray(idx, np.uint8))
        p = os.path.join(tree, "gfx", rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        gfx.write_png(p, idx, a["depth"])
        by[who] = by.get(who, 0) + 1
    print(f"generated {sum(by.values())} pictures: " + ", ".join(f"{k} {v}" for k, v in sorted(by.items())))


if __name__ == "__main__":
    main(*sys.argv[1:])
