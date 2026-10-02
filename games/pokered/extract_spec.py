"""DIRTY ROOM: read the retail pictures of a built pret/pokered tree and keep
only the approved coarse facts, as games/pokered/spec/assets.json.

    python -m games.pokered.extract_spec <built dirty tree>

Kept per picture: path, size, bit depth, kind, and
  pic     one drawn subject: 4x4 grid of mean shade (inside pixels) + 1-bit silhouette
  sprite  a strip of 16x16 frames: the same two facts per frame
  sheet   a sheet of tiles/glyphs: 4x4 grid for the whole sheet + which tiles are blank
          (no silhouette: it would be a copy of the glyphs)
  + for the two pictures the build de-duplicates: which tiles are equal (layout fact,
    the tilemaps in the code index the de-duplicated tiles).
Nothing else leaves the dirty room.
"""
import glob
import json
import os
import sys

import numpy as np

from cleanroom.gb import gfx

HERE = os.path.dirname(os.path.abspath(__file__))

PIC = ("pokemon/front/", "pokemon/back/", "trainers/", "player/", "battle/oldmanb", "battle/ghost",
       "intro/", "title/player", "trade/game_boy")
DEDUPE = ("intro/gengar", "trade/game_boy")


def kind_of(rel):
    if rel.startswith("sprites/"):
        return "sprite"
    if rel.startswith(PIC):
        return "pic"
    return "sheet"


def grid4(idx, inside):
    """4x4 grid of the mean shade of the inside pixels (None where a cell is empty)."""
    h, w = idx.shape
    ys = [round(i * h / 4) for i in range(5)]
    xs = [round(i * w / 4) for i in range(5)]
    out = []
    for j in range(4):
        row = []
        for i in range(4):
            m = inside[ys[j]:ys[j + 1], xs[i]:xs[i + 1]]
            v = idx[ys[j]:ys[j + 1], xs[i]:xs[i + 1]][m]
            row.append(round(float(v.mean()), 2) if v.size else None)
        out.append(row)
    return out


def main(tree):
    assets = {}
    counts = {}
    for f in sorted(glob.glob(os.path.join(tree, "gfx", "**", "*.png"), recursive=True)):
        rel = os.path.relpath(f, os.path.join(tree, "gfx")).replace("\\", "/")
        base = f[:-4]
        built = [e for e in ("2bpp", "1bpp", "pic") if os.path.exists(base + "." + e)]
        if not built:
            continue                                    # not part of Red/Blue: not regenerated
        idx = gfx.read_png(f)
        h, w = idx.shape
        kind = kind_of(rel)
        a = {"w": w, "h": h, "depth": 1 if "1bpp" in built else 2, "kind": kind}
        if kind == "pic":
            inside = ~gfx.flood_outside(idx)
            a["grid"] = grid4(idx, inside)
            a["sil"] = gfx.pack_mask(inside)
        elif kind == "sprite":
            inside = idx != 0
            a["grid"] = [grid4(idx[y:y + 16], inside[y:y + 16]) for y in range(0, h, 16)]
            a["sil"] = gfx.pack_mask(inside)
        else:
            a["grid"] = grid4(idx, np.ones_like(idx, bool))
            a["blank"] = [int(i) for i, t in enumerate(gfx.tiles(idx)) if not t.any()]
        if rel.startswith(DEDUPE):
            seen, cls = {}, []
            for t in gfx.tiles(idx):
                cls.append(seen.setdefault(t.tobytes(), len(seen)))
            a["classes"] = cls
        assets[rel] = a
        counts[kind] = counts.get(kind, 0) + 1
    os.makedirs(os.path.join(HERE, "spec"), exist_ok=True)
    out = os.path.join(HERE, "spec", "assets.json")
    with open(out, "w") as fh:
        json.dump(assets, fh, separators=(",", ":"), sort_keys=True)
    print(f"spec: {len(assets)} pictures {counts} -> {out} ({os.path.getsize(out) // 1024} KB)")


if __name__ == "__main__":
    main(sys.argv[1])
