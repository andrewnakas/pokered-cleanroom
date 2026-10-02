"""Authoring helper for games/pokered/sprite_briefs.json (scratch, not part of the repo).
My own little figure style, drawn into the kept silhouettes, written out as stamps.
  python mk.py        -> writes the brief file and prints the similarity summary
"""
import json, os, sys
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np

ROOT = "D:/n64work/pokered-cleanroom"
sys.path.insert(0, ROOT)
from cleanroom.gb import gfx

SPEC = json.load(open(ROOT + "/games/pokered/spec/assets.json"))
FACING = ["down", "up", "side", "down", "up", "side"]
YY, XX = np.mgrid[0:16, 0:16]
CON = {3: 2, 2: 3, 1: 2}
CH = {1: ".", 2: "-", 3: "#"}


def edge(m):
    p = np.pad(m, 1)
    return m & ~(p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:])


class Cv:
    def __init__(s, m, facing, walk):
        s.m = m; s.f = np.zeros((16, 16), np.uint8); s.facing = facing; s.walk = walk
        s.e = edge(m); s.inner = m & ~s.e
        rows = np.nonzero(m.any(1))[0]
        s.top, s.bot = int(rows[0]), int(rows[-1])
        xs = np.nonzero(m[s.top + 2:s.top + 8].any(0))[0]
        s.cx = (xs[0] + xs[-1]) / 2
        s.L, s.R = int(np.floor(s.cx)), int(np.ceil(s.cx))
        s.ry = YY - s.top
        s.dx = XX - s.cx

    def put(s, cond, v):
        s.f[cond & s.m] = v

    def px(s, x, ry, v):
        y = ry + s.top
        if 0 <= x < 16 and 0 <= y < 16 and s.m[y, x]:
            s.f[y, x] = v

    def rows(s, a, b):
        return (s.ry >= a) & (s.ry <= b)

    def text(s):
        return ["".join(CH[v] if s.m[y, x] and v else " " for x, v in enumerate(s.f[y])) for y in range(16)]


def person(c, R):
    f = c.facing
    h = R.get("hair", 3); st = R.get("style", "short")
    hat = R.get("hat"); H = R.get("H", 3)
    L, Rr, I = c.L, c.R, c.inner
    head = I & (c.ry <= 8)
    con = CON[h]
    fw = R.get("fw", 3.5)
    c.put(c.m, 3)
    c.put(head, h)
    eyer = R.get("eye", 6)
    # ---------------- head
    if f == "down":
        c.put(I & c.rows(H + 1, 7) & (abs(c.dx) <= fw), 1)
        c.put(I & c.rows(8, 8) & (abs(c.dx) <= fw - 1), 1)
        if st in ("short", "spiky", "part", "bald", "bowl"):
            c.put(I & c.rows(6, 7) & (abs(c.dx) <= fw + 1), 1)          # ears
        if st == "bald":
            c.put(I & c.rows(1, H) & (abs(c.dx) <= fw), 1)
            c.px(L - 1, 1, 2); c.px(L - 2, 2, 2)
        elif st == "spiky":
            for x in range(16):
                if (x - L) % 2 == 0:
                    c.px(x, H + 1, h)
            for x in (L - 3, Rr + 1):
                c.px(x, 1, con); c.px(x + 1, 2, con)
        elif st == "part":
            c.put(I & c.rows(H + 1, H + 1) & (c.dx < 0), h)
            for k in range(3):
                c.px(Rr + k, 2 - (k > 0), con)
        elif st == "bowl":
            c.put(I & c.rows(H + 1, H + 1), h)
            c.px(L - 2, 1, con); c.px(L - 1, 1, con); c.px(Rr + 2, 2, con); c.px(Rr + 3, 3, con); c.px(L - 3, 3, con)
        else:
            c.px(L - 2, 1, con); c.px(L - 1, 1, con); c.px(L - 3, 2, con)
        if R.get("glasses"):
            for x in range(L - 3, Rr + 4):
                c.px(x, eyer, 3)
            c.px(L - 2, eyer, 1); c.px(Rr + 2, eyer, 1)
            c.px(L - 2, eyer + 1, 3); c.px(Rr + 2, eyer + 1, 3)
        elif R.get("shades"):
            for x in (L - 3, L - 2, L - 1, Rr + 1, Rr + 2, Rr + 3):
                c.px(x, eyer, 3); c.px(x, eyer + 1, 3)
            c.px(L, eyer, 3); c.px(Rr, eyer, 3)
        elif R.get("closed"):
            for x in (L - 3, L - 2, Rr + 2, Rr + 3):
                c.px(x, eyer + 1, 3)
        else:
            for x in (L - 2, Rr + 2):
                c.px(x, eyer, 3); c.px(x, eyer + 1, 3)
        if R.get("beard"):
            c.put(I & c.rows(8, 8) & (abs(c.dx) <= fw), R["beard"])
            c.px(L - 3, 7, R["beard"]); c.px(Rr + 3, 7, R["beard"])
            c.put(I & c.rows(9, 9) & (abs(c.dx) <= 1.5), R["beard"])
        if R.get("stache"):
            for x in range(L - 1, Rr + 2):
                c.px(x, 8, R["stache"])
        if R.get("brows"):
            for x in (L - 3, L - 2, Rr + 2, Rr + 3):
                c.px(x, eyer - 1, R["brows"])
        if R.get("blush"):
            c.px(L - 3, 8, 2); c.px(Rr + 3, 8, 2)
    elif f == "side":
        c.put(I & c.rows(H + 1, 7) & (c.dx >= -5) & (c.dx <= 0.5), 1)
        c.put(I & c.rows(8, 8) & (c.dx >= -4) & (c.dx <= 0.5), 1)
        if st in ("short", "spiky", "part", "bald", "bowl"):
            c.px(Rr + 1, 6, 1); c.px(Rr + 1, 7, 1)                      # ear
        if st == "bald":
            c.put(I & c.rows(1, H) & (c.dx >= -5) & (c.dx <= 2), 1)
            c.px(L - 1, 1, 2)
        elif st == "spiky":
            for x in range(16):
                if (x - L) % 2 == 0 and x <= Rr:
                    c.px(x, H + 1, h)
            for x in (L - 2, Rr + 2):
                c.px(x, 1, con); c.px(x + 1, 2, con)
            c.px(Rr + 3, 5, con); c.px(Rr + 4, 6, con)
        elif st == "part":
            for k in range(3):
                c.px(Rr + k, 2 - (k > 0), con)
            c.px(L - 3, H + 1, h); c.px(L - 2, H + 1, h)
        elif st == "bowl":
            c.put(I & c.rows(H + 1, H + 1), h)
        else:
            c.px(L, 1, con); c.px(L + 1, 1, con); c.px(L + 2, 2, con)
        ex = L - 2
        if R.get("glasses"):
            for x in range(ex - 2, ex + 2):
                c.px(x, eyer, 3)
            c.px(ex, eyer + 1, 3); c.px(ex + 2, eyer, 2); c.px(ex + 3, eyer, 2)
        elif R.get("shades"):
            for x in range(ex - 2, ex + 2):
                c.px(x, eyer, 3); c.px(x, eyer + 1, 3) if x < ex + 1 else None
            c.px(ex + 2, eyer, 3)
        elif R.get("closed"):
            c.px(ex, eyer + 1, 3); c.px(ex - 1, eyer + 1, 3)
        else:
            c.px(ex, eyer, 3); c.px(ex, eyer + 1, 3)
        if R.get("beard"):
            c.put(I & c.rows(8, 8) & (c.dx >= -5) & (c.dx <= 0.5), R["beard"])
            c.px(L, 7, R["beard"]); c.px(L - 1, 7, R["beard"])
        if R.get("stache"):
            c.px(ex - 2, 8, R["stache"]); c.px(ex - 1, 8, R["stache"]); c.px(ex, 8, R["stache"])
        if R.get("brows"):
            c.px(ex - 1, eyer - 1, R["brows"]); c.px(ex, eyer - 1, R["brows"])
    else:
        if st == "bald":
            c.put(I & c.rows(1, 4) & (abs(c.dx) <= 3.5), 1)
            c.px(Rr + 1, 1, 2)
            c.put(I & c.rows(7, 8) & (abs(c.dx) <= 3.5), 1)
        elif st == "spiky":
            for x, r in ((L - 3, 2), (Rr + 1, 2), (L - 1, 5), (Rr + 3, 5), (L - 4, 6)):
                c.px(x, r, con); c.px(x + 1, r - 1, con)
        elif st == "part":
            for r in range(1, 5):
                c.px(Rr, r, con)
        elif st == "bowl":
            c.put(I & c.rows(6, 6), con)
            c.px(L - 2, 2, con); c.px(Rr + 2, 2, con); c.px(Rr + 1, 1, con)
        elif st == "bob":
            c.put(I & c.rows(7, 7) & (abs(c.dx) <= 3), con)
            c.px(L - 2, 2, con); c.px(L - 3, 3, con); c.px(Rr + 2, 1, con)
        else:
            c.px(Rr + 1, 1, con); c.px(Rr + 2, 1, con); c.px(Rr + 3, 2, con)
        if st not in ("long", "bob"):
            c.put(I & c.rows(8, 8) & (abs(c.dx) <= 2.5), 1)
    # ---------------- hats
    if hat:
        t = hat["t"]; cr = hat.get("c", 2); b = hat.get("b", 3)
        hr = hat.get("r", H)
        crown = I & (c.ry < hr)
        brim = I & (c.ry == hr)
        if t != "band":
            c.put(crown, cr)
        if f == "side":
            c.put(brim & (c.dx <= 1.5), b)
            if t != "band":
                c.put(brim & (c.dx > 1.5), cr if t in ("cap", "peaked", "helmet") else b)
            else:
                c.put(brim, b)
        else:
            c.put(brim, b)
        if t == "cap":
            if f == "down":
                c.put(crown & (abs(c.dx) <= 1.5) & (c.ry >= 1), hat.get("p", 1))
            elif f == "side":
                c.put(crown & (c.dx <= -1.5) & (c.dx >= -4) & (c.ry >= 1), hat.get("p", 1))
            else:
                c.px(L, H - 1, hat.get("p", 1)); c.px(Rr, H - 1, hat.get("p", 1))
                c.put(brim, cr); c.put(I & (c.ry == H) & (abs(c.dx) <= 2.5), b)
        elif t == "nurse":
            if f == "down":
                for x, r in ((L, 1), (Rr, 1), (L - 1, 2), (L, 2), (Rr, 2), (Rr + 1, 2)):
                    c.px(x, r, 3)
                if L == Rr:
                    c.px(L + 1, 2, 3)
            elif f == "side":
                c.px(L - 3, 1, 3); c.px(L - 3, 2, 3); c.px(L - 4, 2, 3); c.px(L - 2, 2, 3)
        elif t == "peaked":
            c.put(I & (c.ry == H - 1), hat.get("band", 1))
            if f == "down":
                c.px(L, 1, hat.get("badge", 2)); c.px(Rr, 1, hat.get("badge", 2))
            if f == "up":
                c.put(brim, cr)
        elif t == "helmet":
            if f == "side":
                c.put(crown & (c.ry == 2), hat.get("p", 1))
            else:
                c.put(crown & (abs(c.dx) <= 0.6) & (c.ry >= 1), hat.get("p", 1))
        elif t == "sailor":
            c.px(L, 1, 2); c.px(Rr, 1, 2)
            if f != "down":
                c.put(I & (c.ry == H + 1) & (c.dx > 1.5 if f == "side" else c.m), b)
        elif t == "toque":
            for x in (L - 2, Rr + 2, L if f == "up" else -9):
                for r in range(1, H):
                    c.px(x, r, 2)
        elif t == "wide":
            c.px(L - 1, 1, hat.get("p", 1)); c.px(L, 1, hat.get("p", 1))
            c.put(I & (c.ry == H - 1), hat.get("band", cr))
        elif t == "top":
            c.put(I & (c.ry == H - 1), hat.get("band", 1))
        if hat.get("shadow") and f == "down":
            c.put(I & (c.ry == H + 1) & (abs(c.dx) <= fw), 2)
    # ---------------- body
    top = R.get("top", 2); legs = R.get("legs", 3); body = R.get("body", "plain")
    tc = CON[top] if top != 1 else 3
    tr = I & c.rows(9, 12)
    c.put(tr, top)
    low = I & (c.ry >= 13)
    c.put(low, legs)
    cols = np.nonzero(tr.any(0))[0]
    a0, a1 = (int(cols[0]), int(cols[-1])) if cols.size else (L, Rr)
    if st == "long" and f == "down":
        c.put(I & c.rows(9, 10) & (abs(c.dx) >= 3.5), h)
    if body in ("coat", "dress", "robe"):
        c.put(I & c.rows(13, 14), top)
        if body == "dress":
            c.put(I & c.rows(14, 14) & (c.ry < c.bot - c.top), tc)
    if body == "shorts":
        c.put(I & (c.ry >= 14), 1)
    if body == "bare":
        c.put(tr & (c.ry <= 11), 1)
        c.put(I & c.rows(12, 13), legs)
        c.put(I & (c.ry >= 14), 1)
    if R.get("boots"):
        c.put(I & (c.ry >= 14), R["boots"])
    if f != "side":
        if cols.size >= 7 and body not in ("cape",):
            sl = R.get("sleeve", top)
            c.put(tr & ((XX <= a0 + 1) | (XX >= a1 - 1)), sl)
            for xa in (a0 + 2, a1 - 2):
                c.put(tr & (XX == xa) & (c.ry >= 10), 3 if (top != 3 or sl != 3) and body != "bare" else 2)
            c.put(tr & ((XX <= a0 + 1) | (XX >= a1 - 1)) & (c.ry == 12), R.get("hand", 1))
        if body not in ("coat", "dress", "robe", "cape") and legs != 0:
            c.put(low & (c.ry >= 14) & (XX == Rr), 2 if legs == 3 else 3)
    if f == "down":
        if body == "coat":
            c.put(I & c.rows(9, 14) & (XX == Rr), 2)
            c.px(L - 1, 9, R.get("shirt", 2)); c.px(L, 9, R.get("shirt", 2)); c.px(Rr + 1, 9, R.get("shirt", 2))
            c.px(L, 11, 3); c.px(L, 13, 3)
        elif body == "suit":
            for x in range(L - 1, Rr + 2):
                c.px(x, 9, 1)
            c.px(L, 10, 1); c.px(Rr, 10, 1)
            for r in (9, 10, 11):
                c.px(Rr, r, R.get("tie", 2 if top == 3 else 3))
        elif body == "dress":
            if R.get("apron"):
                c.put(I & c.rows(10, 13) & (abs(c.dx) <= 2), R["apron"])
                c.px(L - 1, 9, R["apron"]); c.px(Rr + 1, 9, R["apron"])
            else:
                c.px(L, 9, tc); c.px(Rr, 10, tc)
        elif body == "stripe":
            c.put(tr & (c.ry % 2 == 0) & (XX > a0 + 2) & (XX < a1 - 2), R.get("stripe", tc))
        elif body == "emblem":
            for x, r in R.get("mark", ((0, 9), (0, 10), (1, 9), (1, 11))):
                c.px(L + x, r, R.get("markc", 1))
        elif body == "vest":
            c.put(tr & (abs(c.dx) <= 1.2), R.get("shirt", 1))
            c.px(Rr, 10, 3); c.px(Rr, 12, 3)
        elif body == "jacket":
            c.put(tr & (XX == Rr), 3 if top != 3 else 1)
            c.px(L - 1, 9, 1); c.px(Rr + 1, 9, 1)
        elif body == "cape":
            c.put(I & c.rows(9, 14) & (abs(c.dx) >= 2.5), R.get("cape", 3))
            c.px(L, 9, 1); c.px(Rr, 9, 1)
        elif body == "bare":
            c.px(L - 1, 10, 2); c.px(Rr + 1, 10, 2); c.px(Rr, 11, 2)
        elif body == "robe":
            c.put(I & c.rows(9, 14) & (abs(c.dx - (c.ry - 9) * 0.5 + 1) <= 0.6), 3)
            c.put(I & c.rows(12, 12) & (XX > a0 + 2) & (XX < a1 - 2), R.get("sash", 2))
        elif body == "bow":
            c.px(L - 1, 9, 3); c.px(Rr + 1, 9, 3); c.px(L, 10, 3) if L == Rr else None
            c.put(tr & (abs(c.dx) <= 1.2) & (c.ry >= 10), R.get("shirt", 1))
        if R.get("item"):
            for x in range(L - 1, Rr + 2):
                c.px(x, 11, 1); c.px(x, 12, 1)
            c.px(L, 11, 3); c.px(Rr, 12, 2)
    elif f == "up":
        if body == "coat":
            c.put(I & c.rows(10, 14) & (XX == L), 2)
        elif body == "cape":
            c.put(I & c.rows(9, 14), R.get("cape", 3))
            for x in (L - 2, Rr + 2):
                c.put(I & c.rows(10, 14) & (XX == x), CON[R.get("cape", 3)])
        elif body == "stripe":
            c.put(tr & (c.ry % 2 == 0) & (XX > a0 + 2) & (XX < a1 - 2), R.get("stripe", tc))
        elif body == "dress":
            c.put(I & c.rows(12, 12) & (XX > a0 + 2) & (XX < a1 - 2), tc if not R.get("apron") else R["apron"])
        elif body == "robe":
            c.put(I & c.rows(12, 12) & (XX > a0 + 2) & (XX < a1 - 2), R.get("sash", 2))
        elif body == "bare":
            c.px(L, 10, 2); c.px(L, 11, 2)
        if R.get("pack"):
            c.put(I & c.rows(9, 12) & (abs(c.dx) <= 2.5), R["pack"])
            c.put(I & c.rows(11, 11) & (abs(c.dx) <= 2.5), 3 if R["pack"] != 3 else 2)
        if st == "long":
            c.put(I & c.rows(8, 10) & (abs(c.dx) <= 3.5), h)
            for x in (L - 2, Rr + 2):
                for r in range(4, 10):
                    c.px(x, r, con)
        elif st == "pony":
            c.put(I & c.rows(8, 11) & (abs(c.dx) <= 1.2), h)
    else:
        c.put(tr & (XX == Rr + 1) & (c.ry <= 11), 3 if top != 3 else 2)
        c.put(tr & (XX >= L - 1) & (XX <= Rr) & (c.ry >= 10), R.get("sleeve", top))
        c.px(L - 1, 12, R.get("hand", 1)); c.px(L, 12, R.get("hand", 1))
        if body == "coat":
            c.put(I & c.rows(9, 14) & (XX == L - 2), 2)
        elif body == "cape":
            c.put(I & c.rows(9, 14) & (c.dx >= 0.5), R.get("cape", 3))
        elif body == "stripe":
            c.put(tr & (c.ry % 2 == 0) & (XX < L - 1), R.get("stripe", tc))
        elif body == "dress" and R.get("apron"):
            c.put(I & c.rows(10, 13) & (c.dx <= -2), R["apron"])
        elif body == "suit":
            c.px(L - 3, 9, 1); c.px(L - 2, 9, 1); c.px(L - 3, 10, R.get("tie", 2 if top == 3 else 3))
        elif body == "emblem":
            c.px(L - 3, 10, R.get("markc", 1))
        elif body == "bare":
            c.px(L - 2, 10, 2)
        elif body == "robe":
            c.put(I & c.rows(12, 12) & (XX < L - 1), R.get("sash", 2))
        if R.get("pack"):
            c.put(I & c.rows(9, 12) & (c.dx >= 2), R["pack"])
        if R.get("item"):
            c.px(L - 4, 11, 1); c.px(L - 3, 11, 1); c.px(L - 4, 12, 3); c.px(L - 3, 12, 1)
        if st == "long":
            c.put(I & c.rows(8, 10) & (c.dx >= 1.5), h)
        elif st == "pony":
            c.put(I & c.rows(8, 10) & (c.dx >= 3.5), h)
    if R.get("bike"):
        if f == "side":
            c.put(I & (c.ry >= 11), 3)
            for wx in (3.5, 11.5):
                dd = (XX - wx) ** 2 + (c.ry - 13.2) ** 2
                c.put(I & (dd <= 6.5) & (c.ry >= 11), 2)
                c.put(I & (dd <= 1.5), 1)
            c.put(I & (c.ry == 11) & (XX >= 5) & (XX <= 10), 2)
            c.px(4, 10, 3); c.px(3, 9, 3); c.px(4, 9, 1)
        else:
            c.put(I & (c.ry >= 12) & (abs(c.dx) <= 1.6), 2)
            c.put(I & (c.ry >= 12) & (abs(c.dx) <= 0.6), 3)
            c.put(I & (c.ry == 10) & (abs(c.dx) >= 2), 3)
            c.put(I & (c.ry == 10) & (abs(c.dx) >= 5), 1)
    c.put(c.e, 3)
    for fc, x, r, v in R.get("px", ()):
        if fc == f or fc == "*":
            c.px(L + x if x <= 0 else Rr + x - (1 if False else 0), r, v)
    return c


# ----------------------------------------------------------------- things and creatures
def blob(c, body, light=None):
    c.put(c.m, 3); c.put(c.inner, body)
    return c


def t_ball(c, R):
    blob(c, 1)
    ys = np.nonzero(c.m.any(1))[0]; cy = (ys[0] + ys[-1] + 1) // 2
    c.put(c.inner & (YY < cy), 2)
    c.put(c.inner & (YY == cy), 3)
    c.put(c.inner & (YY < cy) & (XX + YY <= c.L - 3 + ys[0] + 3), 1)
    c.put(c.inner & (YY > cy + 1) & (XX - YY >= 0), 2)
    for x in (c.L, c.R):
        c.f[cy, x] = 1; c.f[cy - 1, x] = 3; c.f[cy + 1, x] = 3
    c.f[cy, c.L - 1] = 3; c.f[cy, c.R + 1] = 3
    return c


def t_boulder(c, R):
    blob(c, 2)
    c.put(c.inner & (XX + 2 * YY <= 17), 1)
    c.put(c.inner & (XX + YY >= 22), 3)
    for x, y in ((6, 6), (7, 7), (7, 8), (8, 9), (9, 9), (10, 10), (4, 9), (5, 10), (10, 4), (11, 5), (11, 6)):
        c.put((XX == x) & (YY == y), 3)
    for x, y in ((8, 8), (9, 8), (5, 11), (6, 11), (12, 6)):
        c.put((XX == x) & (YY == y), 1)
    c.put(c.e, 3)
    return c


def t_fossil(c, R):
    blob(c, 2)
    c.put(c.inner & (XX + YY <= 9), 1)
    # a spiral shell of our own
    for x, y in ((6, 5), (7, 5), (8, 5), (9, 6), (10, 7), (10, 8), (9, 9), (8, 10), (7, 10), (6, 9), (5, 8), (6, 7), (7, 7), (8, 8)):
        c.put((XX == x) & (YY == y), 3)
    for x, y in ((7, 6), (8, 6), (9, 7), (9, 8), (8, 9), (7, 9), (6, 8), (7, 8)):
        c.put((XX == x) & (YY == y), 1)
    c.put(c.inner & (XX + YY >= 21), 3)
    c.put(c.e, 3)
    return c


def t_amber(c, R):
    blob(c, 2)
    c.put(c.inner & (XX - YY >= 1) & (YY <= 6), 1)
    for x, y in ((7, 7), (8, 7), (7, 8), (8, 9), (6, 9), (9, 8)):
        c.put((XX == x) & (YY == y), 3)
    c.put(c.inner & (YY >= 11), 3)
    c.px(5, 5 - c.top, 1); c.px(10, 10 - c.top, 1)
    c.put(c.e, 3)
    return c


def t_paper(c, R):
    blob(c, 1)
    xs = np.nonzero(c.inner.any(0))[0]
    for y in range(3, 13, 2):
        c.put(c.inner & (YY == y) & (XX >= xs[0] + 1) & (XX <= xs[-1] - 1 - (y % 4 == 1) * 3), 2)
    c.put(c.inner & (YY >= 3) & (YY <= 6) & (XX <= xs[0] + 4), 3)
    c.put(c.inner & (YY >= 4) & (YY <= 5) & (XX >= xs[0] + 2) & (XX <= xs[0] + 3), 2)
    c.put(c.inner & (XX + YY >= 23), 2)
    c.put(c.e, 3)
    return c


def t_clipboard(c, R):
    blob(c, 2)
    xs = np.nonzero(c.inner.any(0))[0]
    c.put(c.inner & (YY >= 4) & (XX >= xs[0] + 2) & (XX <= xs[-1] - 2) & (YY <= 11), 1)
    c.put(c.inner & (YY <= 2) & (abs(XX - (xs[0] + xs[-1]) / 2) <= 2), 3)
    for y in (5, 7, 9, 11):
        c.put(c.inner & (YY == y) & (XX >= xs[0] + 3) & (XX <= xs[-1] - 3 - (y == 11) * 3), 3 if y == 5 else 2)
        c.put(c.inner & (YY == y) & (XX == xs[0] + 3), 3)
    c.put(c.e, 3)
    return c


def t_pokedex(c, R):
    blob(c, 2)
    c.put(c.inner & (XX == 8), 3)                                  # spine of the open book
    c.put(c.inner & (XX >= 3) & (XX <= 6) & (YY >= 6) & (YY <= 9), 1)        # screen page
    c.put(c.inner & (XX == 4) & (YY == 7), 3)
    c.put(c.inner & (XX >= 10) & (XX <= 13) & (YY % 2 == 0) & (YY >= 6) & (YY <= 11), 1)   # text page
    c.put(c.inner & (XX >= 3) & (XX <= 5) & (YY == 11), 3)
    c.put(c.inner & (YY == 12), 3)
    c.put(c.inner & (YY <= 4), 2)
    c.put(c.e, 3)
    return c


def t_snorlax(c, R):
    blob(c, 2)
    c.put(c.inner & (((XX - 7.5) / 5.2) ** 2 + ((YY - 10) / 3.6) ** 2 <= 1), 1)     # belly
    c.put(c.inner & (YY >= 2) & (YY <= 5) & (abs(XX - 7.5) <= 3.6), 1)            # face
    for x in (4, 5, 6, 9, 10, 11):
        c.put((XX == x) & (YY == 3), 3)                                           # shut eyes
    c.put((YY == 5) & (abs(XX - 7.5) <= 1.6), 3)                                  # mouth
    c.put((YY == 4) & ((XX == 6) | (XX == 9)), 1)
    c.put(c.inner & (YY == 10) & (abs(XX - 7.5) <= 0.6), 2)
    c.put(c.inner & (YY >= 12) & (abs(XX - 7.5) >= 4.5), 1)                       # feet
    c.put(c.inner & (YY == 13) & (abs(XX - 7.5) >= 5.5), 3)
    c.put(c.e, 3)
    return c


def t_sleeper(c, R):
    """A man asleep on his side, head to the left."""
    blob(c, 2)
    c.put(c.inner & (XX <= 3), 3)                       # hair
    c.put(c.inner & (XX >= 3) & (XX <= 7) & (YY >= 3) & (YY <= 12), 1)   # face
    c.put(c.inner & (XX <= 4) & (YY <= 4), 3); c.put(c.inner & (XX <= 4) & (YY >= 11), 3)
    for y in (5, 6, 9, 10):
        c.put((XX == 5) & (YY == y), 3)                 # shut eyes (turned)
    c.put((XX == 7) & (YY >= 7) & (YY <= 8), 2)         # mouth
    c.put(c.inner & (XX == 8), 3)                       # collar
    c.put(c.inner & (XX >= 9) & (XX <= 12), 2)
    c.put(c.inner & (XX >= 9) & (XX <= 12) & (YY >= 7) & (YY <= 8), 1)   # shirt front
    c.put((XX == 10) & (YY >= 7) & (YY <= 8), 3)
    c.put(c.inner & (XX >= 13), 3)
    c.put(c.inner & (XX >= 14) & ((YY <= 4) | (YY >= 11)), 1)
    c.put(c.e, 3)
    return c


def t_bird(c, R):
    f = c.facing
    blob(c, 2)
    L, Rr = c.L, c.R
    if f == "down":
        c.put(c.inner & (c.ry >= 8) & (abs(c.dx) <= 2.6), 1)            # breast
        c.put(c.inner & (c.ry >= 5) & (c.ry <= 7) & (abs(c.dx) <= 2.6), 1)   # face
        c.px(L - 1, 6, 3); c.px(Rr + 1, 6, 3)
        c.px(L, 7, 3); c.px(Rr, 7, 3); c.px(L, 8, 3); c.px(Rr, 8, 2)     # beak
        c.px(L, 3, 3); c.px(Rr, 2, 3)                                    # crest
        for r in (10, 12):
            c.px(L - 1, r, 2); c.px(Rr + 1, r, 2)
        c.put(c.inner & (abs(c.dx) >= 4.5) & (c.ry >= 4) & (c.ry <= 9) & ((XX + YY) % 2 == 0), 3)
    elif f == "up":
        for r in range(4, 13, 2):
            for k in range(-4, 5):
                c.px(L + k, r + (abs(k) % 2), 3 if abs(k) % 4 < 2 else 1)
        c.put(c.inner & (c.ry <= 3), 2)
        c.px(L, 2, 3); c.px(Rr, 3, 3)
    else:
        if c.walk:
            c.put(c.inner & (YY >= c.top + 6) & (XX >= 4) & (XX <= 9), 1)
            c.put(c.inner & (YY <= c.top + 4) & ((XX + YY) % 3 == 0), 3)
            c.px(3, 6, 3); c.px(2, 7, 1); c.px(1, 7, 1)
            c.put(c.inner & (YY <= c.top + 2) & (XX >= 8) & ((XX + YY) % 2 == 0), 1)
        else:
            c.put(c.inner & (YY >= 8) & (XX <= 6), 1)                    # breast
            c.px(4, 5, 3); c.px(4, 4, 1); c.px(5, 4, 1)                 # eye
            c.px(1, 6, 1); c.px(2, 6, 1); c.px(2, 7, 1)                 # beak
            for k in range(4):
                c.px(8 + k, 8 + (k % 2), 3); c.px(8 + k, 10 + (k % 2), 3)   # wing feathers
            c.put(c.inner & (XX >= 12) & ((XX + YY) % 2 == 0), 1)
    c.put(c.e, 3)
    return c


def t_fairy(c, R):
    f = c.facing
    blob(c, 1)
    L, Rr = c.L, c.R
    t = c.top
    if f == "down":
        c.put(c.inner & (c.ry <= 2) & (abs(c.dx) >= 3.5), 3)               # ear tips
        c.put(c.inner & (c.ry <= 1) & (abs(c.dx) <= 1.6), 2)               # curl
        c.px(L, 2, 2); c.px(Rr + 1, 2, 3)
        for x in (L - 2, Rr + 2):
            c.px(x, 4, 3); c.px(x, 5, 3)
        c.px(L - 3, 4, 3); c.px(Rr + 3, 4, 3)                              # slanted eyes
        c.px(L, 6, 3); c.px(Rr, 6, 3); c.px(L - 1, 6, 2); c.px(Rr + 1, 6, 2)   # smile
        c.put(c.inner & (c.ry >= 8) & (abs(c.dx) <= 2.6) & (c.ry <= 11), 2)   # tummy shade
        c.put(c.inner & (c.ry >= 9) & (abs(c.dx) <= 1.6) & (c.ry <= 10), 1)
        c.put(c.inner & (c.ry >= 7) & (c.ry <= 8) & (abs(c.dx) >= 5), 2)   # hands
        c.put(c.inner & (c.ry >= 12) & (abs(c.dx) >= 2.5), 2)             # feet
    elif f == "up":
        c.put(c.inner & (c.ry <= 2) & (abs(c.dx) >= 3.5), 3)
        c.put(c.inner & (c.ry >= 5) & (c.ry <= 8) & (abs(c.dx) >= 2) & (abs(c.dx) <= 4.6), 2)   # little wings
        c.put(c.inner & (c.ry >= 6) & (c.ry <= 7) & (abs(c.dx) >= 3) & (abs(c.dx) <= 4), 3)
        c.px(Rr + 1, 10, 3); c.px(Rr + 2, 10, 3); c.px(Rr + 2, 11, 3); c.px(Rr + 1, 11, 2)       # tail curl
        c.put(c.inner & (c.ry >= 12) & (abs(c.dx) >= 2.5), 2)
        c.px(L, 1, 2); c.px(Rr, 1, 2)
    else:
        c.put(c.inner & (c.ry <= 2) & (XX >= 8), 3)                       # ear
        c.px(5, 4, 3); c.px(5, 5, 3); c.px(4, 4, 3)                       # eye
        c.px(3, 7, 3); c.px(4, 7, 2)                                      # mouth
        c.px(5, 1, 2); c.px(6, 1, 2); c.px(6, 2, 2)                       # curl
        c.put(c.inner & (XX >= 11) & (c.ry >= 6) & (c.ry <= 10), 2)      # tail and wing
        c.px(12, 8, 3); c.px(13, 8, 3); c.px(12, 7, 3)
        c.put(c.inner & (c.ry >= 12) & ((XX <= 6) | (XX >= 10)), 2)      # feet
        c.px(6, 9, 2); c.px(7, 9, 2); c.px(6, 10, 3)                      # arm
    c.put(c.e, 3)
    return c


def t_monster(c, R):
    f = c.facing
    blob(c, 2)
    L, Rr = c.L, c.R
    if f == "down":
        c.put(c.inner & (c.ry >= 8) & (abs(c.dx) <= 2.6) & (c.ry <= 12), 1)      # belly plates
        for r in (9, 11):
            c.put(c.inner & (c.ry == r) & (abs(c.dx) <= 2.6), 2)
        c.px(L, 1, 1); c.px(Rr, 1, 1); c.px(L, 2, 1)                              # horn
        for s_, x in ((-1, L - 2), (1, Rr + 2)):
            c.px(x, 4, 1); c.px(x, 5, 3); c.px(x + s_, 3, 3); c.px(x, 3, 3)       # glaring eyes
        for x in range(L - 2, Rr + 3):
            c.px(x, 7, 3 if (x - L) % 2 else 1)                                  # teeth
        c.put(c.inner & (abs(c.dx) >= 4.5) & (c.ry <= 3), 3)                     # ear spikes
        c.put(c.inner & (c.ry >= 13) & (abs(c.dx) >= 2), 1)                      # claws
    elif f == "up":
        for r in range(2, 13):
            c.px(L if r % 2 else Rr, r, 3)                                       # spine ridge
            if r % 3 == 0:
                c.px(L - 3, r, 3); c.px(Rr + 3, r, 3); c.px(L - 2, r, 1); c.px(Rr + 2, r, 1)
        c.put(c.inner & (abs(c.dx) >= 4.5) & (c.ry <= 3), 3)
        c.put(c.inner & (c.ry >= 13) & (abs(c.dx) >= 2), 1)
    else:
        t = c.top
        c.px(5, 4 + c.walk, 3); c.px(5, 5 + c.walk, 3); c.px(4, 3 + c.walk, 3); c.px(6, 4 + c.walk, 1)    # eye
        for k, x in enumerate(range(1, 5)):
            c.px(x, 8, 1 if k % 2 else 3)                                        # teeth
        c.put(c.inner & (c.ry >= 9) & (c.ry <= 12) & (XX >= 5) & (XX <= 8), 1)   # belly
        for k in range(8, 15):
            c.px(k, 5 + (k - 8) + (k % 2), 3)                                    # back spikes
        c.put(c.inner & (YY >= 14) & ((XX + YY) % 3 == 0), 1)
        c.px(5, 1, 1); c.px(4, 1, 1)
    c.put(c.e, 3)
    return c


def biggest(m):
    from scipy import ndimage
    lab, n = ndimage.label(m)
    if n == 0:
        return m.copy()
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    return lab == (1 + int(np.argmax(sizes)))


def t_seel(c, R):
    f = c.facing
    p = np.pad(c.m, 1)
    nb = (p[:-2, 1:-1].astype(int) + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:])
    body = biggest(c.m)
    eb = edge(body)
    c.put(c.m, 1)
    c.put(body, 1); c.put(eb, 3)
    inb = body & ~eb
    rows = np.nonzero(inb.any(1))[0]
    if not rows.size:
        return c
    t = int(rows[0]) - c.top
    L, Rr = c.L, c.R
    if f == "down":
        c.px(L, t, 2); c.px(Rr, t, 2)                                          # horn
        c.px(L - 2, t + 2, 3); c.px(Rr + 2, t + 2, 3); c.px(L - 2, t + 3, 3); c.px(Rr + 2, t + 3, 3)
        c.px(L, t + 4, 3); c.px(Rr, t + 4, 3)                                  # nose
        c.px(L - 1, t + 5, 2); c.px(Rr + 1, t + 5, 2); c.px(L, t + 6, 2); c.px(Rr, t + 6, 2)   # smile
        c.px(L - 4, t + 4, 2); c.px(Rr + 4, t + 4, 2)                          # whisker dots
        c.put(inb & (c.ry >= t + 7) & (abs(c.dx) >= 3), 2)
    elif f == "up":
        c.put(inb & (abs(c.dx) <= 1.6) & (c.ry >= t + 2), 2)
        c.px(L, t, 2); c.px(Rr, t, 2)
        c.put(inb & (c.ry >= t + 6) & (abs(c.dx) >= 4), 2)
    else:
        cols = np.nonzero(inb.any(0))[0]
        x0 = int(cols[0])
        c.px(x0 + 3, t + 2, 3); c.px(x0 + 3, t + 3, 3)                         # eye
        c.px(x0, t + 4, 3); c.px(x0 + 1, t + 4, 3)                             # nose
        c.px(x0 + 4, t, 2); c.px(x0 + 5, t, 2)                                 # horn
        c.put(inb & (XX >= x0 + 6) & (c.ry >= t + 4), 2)                       # back shade
        c.put(inb & (XX >= x0 + 10), 2)
        c.px(x0 + 2, t + 5, 2)
    c.put(eb, 3)
    return c


def t_swimmer(c, R):
    """Head and shoulders above the water, spray around."""
    f = c.facing
    body = biggest(c.m)
    c.put(c.m, 1)
    if not body.any():
        return c
    b = Cv(body, f, c.walk)
    I, L, Rr = b.inner, b.L, b.R
    c.put(body, 3)
    c.put(I, 1)
    water = I & (b.ry >= 7)
    if f == "down":
        c.put(I & (b.ry <= 2), 1); c.put(I & (b.ry == 2), 2)                # cap and its rim
        c.px(L, b.top - c.top + 1, 2)
        r0 = b.top - c.top
        for x in range(L - 3, Rr + 4):
            c.px(x, r0 + 3, 3)                                              # goggles
        c.px(L - 2, r0 + 3, 2); c.px(Rr + 2, r0 + 3, 2)
        c.px(L, r0 + 5, 3); c.px(Rr, r0 + 5, 3)                             # mouth
        c.put(I & (b.ry == 6), 1)
    elif f == "up":
        c.put(I & (b.ry <= 3), 1); c.put(I & (b.ry == 4), 2)
        c.put(I & (b.ry <= 3) & (XX == Rr), 2)
        c.put(I & (b.ry == 6) & (abs(b.dx) <= 1), 2)
    else:
        r0 = b.top - c.top
        c.put(I & (b.ry <= 2), 1); c.put(I & (b.ry <= 4) & (b.dx >= 1), 1)
        c.put(I & (b.ry == 2) & (b.dx < 1), 2); c.put(I & (b.ry <= 4) & (XX == Rr + 1), 2)
        for x in range(L - 4, L):
            c.px(x, r0 + 3, 3)
        c.px(L - 3, r0 + 3, 2); c.px(L - 3, r0 + 5, 3)
    c.put(water, 2)
    c.put(water & ((XX + 2 * YY) % 5 <= 1), 1)
    c.put(water & (b.ry == 7) & (abs(b.dx) <= 2.5), 1)
    c.put(b.e, 3)
    c.put(b.e & (b.ry >= 8), 2)
    return c


THINGS = {"swimmer": t_swimmer, "poke_ball": t_ball, "boulder": t_boulder, "fossil": t_fossil, "old_amber": t_amber,
          "paper": t_paper, "clipboard": t_clipboard, "pokedex": t_pokedex, "snorlax": t_snorlax,
          "gambler_asleep": t_sleeper, "bird": t_bird, "fairy": t_fairy, "monster": t_monster, "seel": t_seel}

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "recipes.py")).read())


def build():
    out = {}
    for rel in sorted(SPEC):
        if not rel.startswith("sprites/"):
            continue
        name = rel[8:-4]
        a = SPEC[rel]
        m = gfx.unpack_mask(a["sil"], a["h"], a["w"])
        b = {}
        if name in PEOPLE:
            R = PEOPLE[name]
            b["opts"] = {"hair": R.get("hair", 3), "top": R.get("top", 2), "legs": R.get("legs", 3)}
        for n in range(a["h"] // 16):
            mm = m[n * 16:n * 16 + 16]
            if not mm.any():
                continue
            c = Cv(mm, FACING[n % 6], n >= 3)
            if name in THINGS:
                THINGS[name](c, {})
            elif name in PEOPLE:
                R = dict(PEOPLE[name])
                R.update(R.get("walk" if n >= 3 else "stand", {}))
                R.update(R.get(FACING[n % 6], {}))
                person(c, R)
            else:
                continue
            b[("walk_" if n >= 3 else "") + FACING[n % 6]] = c.text()
        if len(b) > (1 if "opts" in b else 0):
            out[name] = b
    return out


def check(out):
    from games.pokered import generate
    generate.load_drawers()
    salts = generate.load_salts()
    from games.pokered.art import sprites as sp
    sp._SB = out
    res = []
    for rel in sorted(SPEC):
        if not rel.startswith("sprites/"):
            continue
        a = SPEC[rel]
        ours, _ = generate.render(rel, a)
        ours = generate.constrain(rel, a, generate.stipple(rel, a, np.asarray(ours, np.uint8), salts))
        ret = gfx.read_png("D:/n64work/pokered/dirty/gfx/" + rel)
        m = ret > 0
        eq = float((ours[m] == ret[m]).mean())
        tiles = 0
        for y in range(0, ret.shape[0], 8):
            for x in range(0, 16, 8):
                t = ret[y:y + 8, x:x + 8]
                if t.min() != t.max() and (t == ours[y:y + 8, x:x + 8]).all():
                    tiles += 1
        res.append((eq, tiles, rel[8:-4]))
    res.sort(reverse=True)
    print("briefs", len(out), " most like retail:", " ".join("%s %.0f%%" % (n, e * 100) for e, t, n in res[:8]))
    print("median %.0f%%" % (100 * np.median([e for e, _, _ in res])), " equal tiles:", [(n, t) for e, t, n in res if t])
    miss = [r[8:-4] for r in sorted(SPEC) if r.startswith("sprites/") and r[8:-4] not in out]
    print("no brief:", miss)


def sheet(out, names, path, sc=6):
    from PIL import Image
    pal = np.array([[96, 150, 96], [255, 255, 255], [170, 170, 170], [0, 0, 0]], np.uint8)
    cols = 2
    rows = (len(names) + cols - 1) // cols
    im = np.zeros((rows * 18, cols * 100, 3), np.uint8); im[:] = (96, 150, 96)
    for i, n in enumerate(names):
        b = out[n]
        for k, key in enumerate(["down", "up", "side", "walk_down", "walk_up", "walk_side"]):
            if key in b:
                a = np.array([[" .-#".index(ch) for ch in r] for r in b[key]])
                y, x = (i // cols) * 18 + 1, (i % cols) * 100 + k * 16 + 2
                im[y:y + 16, x:x + 16] = pal[a]
    Image.fromarray(im).resize((im.shape[1] * sc, im.shape[0] * sc), Image.NEAREST).save(path)
    print("sheet", path, " | ".join("%d,%d %s" % (i // cols, i % cols, n) for i, n in enumerate(names)))


if __name__ == "__main__":
    out = build()
    if len(sys.argv) > 2:
        sheet(out, sys.argv[2].split(",") if sys.argv[2] != "all" else sorted(out)[int(sys.argv[3]):int(sys.argv[4])], sys.argv[1])
    p = ROOT + "/games/pokered/sprite_briefs.json"
    txt = "{\n" + ",\n".join(
        ' "%s": {\n' % k + ",\n".join(
            '  "%s": %s' % (kk, json.dumps(vv) if kk == "opts" else "[\n   " + ",\n   ".join(json.dumps(r) for r in vv) + "]")
            for kk, vv in v.items()) + "}" for k, v in out.items()) + "\n}\n"
    json.loads(txt)
    open(p, "w", encoding="utf-8", newline="\n").write(txt)
    check(out)
