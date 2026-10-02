"""Ship port tileset (Vermilion Dock): quay, water, float line, gangway, crates,
a truck and the moored liner (one 16x6-tile picture seen from above, bow to the left)."""
import numpy as np

from games.pokered.art import drawer
from games.pokered.art.tilekit import C, T8, build_sheet, put, tex
from games.pokered.art.ts_overworld import PAVE, WATER, on

WALK = (0x0a, 0x1a, 0x32, 0x3b)

SHIP = [
    [None, None, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x09, None, 0x0B, None, 0x0C, 0x0D, 0x0E, 0x0F],
    [0x10, 0x11, 0x12, 0x13, 0x00, 0x15, 0x16, 0x17, 0x18, 0x19, None, None, 0x1C, 0x1D, 0x1E, 0x1F],
    [0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, None, None, 0x2C, 0x2D, 0x2E, 0x2F],
    [0x30, None, None, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, None, None, 0x3E, 0x3D, None, None],
    [0x40, 0x41, 0x42, 0x43, 0x44, 0x45, None, None, None, None, None, None, None, 0x4D, 0x4E, 0x4F],
    [None, 0x51, 0x52, 0x53, 0x55, None, None, None, None, None, None, None, None, 0x5D, 0x5A, 0x5B],
]


def ship():
    c = on(WATER, (128, 48))
    y, x = c.grid()
    hull = (c.emask(40, 24, 40, 22) & (x < 40)) | c.pmask([(40, 2), (121, 2), (126, 7), (126, 41), (121, 46), (40, 46)])
    c.fill(hull, 0, outline=3)
    inner = hull & (c.a != 3)
    deck = inner & (y < 32)
    c.a[deck & (y % 4 == 1)] = 1                           # deck planks
    c.a[inner & (y == 3)] = 1                              # rail
    side = inner & (y >= 32)
    c.a[hull & (y == 32)] = 3
    c.a[side & (y == 36)] = 1
    c.a[side & (y >= 34) & (y <= 35) & (x % 8 == 3) & (x >= 16)] = 3   # portholes
    c.a[side & (y == 40)] = 3
    c.a[side & (y >= 41) & (y <= 42)] = 2
    c.a[side & (y >= 43)] = 1
    # bow: capstan and hatch (column 3 only; columns 1-2 stay plain deck)
    c.ellipse(28, 20, 2.6, 2.6, 1, outline=3)
    c.frame(25, 25, 31, 31, 3, fill=2)
    # bridge
    c.frame(34, 9, 63, 31, 3, fill=1)
    c.frame(40, 12, 60, 28, 3, fill=0)
    c.hline(14, 42, 58, 1); c.hline(25, 42, 58, 1)
    c.rect(35, 11, 39, 29, 2)
    for yy in (12, 17, 22):
        c.rect(36, yy, 38, yy + 3, 0)
    c.ellipse(50, 20, 3.2, 3.2, 2, outline=3); c.px(49, 19, 0)
    c.rect(34, 5, 63, 9, 1); c.hline(4, 34, 63, 3); c.vline(34, 4, 9, 3); c.vline(62, 4, 9, 3)
    # two funnels and the windows under them (each 16 px unit is identical)
    for ox in (64, 80):
        c.ellipse(ox + 8, 16.5, 6.6, 6.2, 1, outline=3)
        c.ellipse(ox + 8, 15.5, 4.2, 3.4, 3)
        c.hline(21, ox + 5, ox + 11, 2)
        c.frame(ox + 1, 25, ox + 15, 31, 3, fill=2)
        c.hline(26, ox + 3, ox + 8, 0); c.vline(ox + 8, 26, 30, 3)
    # stern: lifeboat, vent, hatch
    boat = c.emask(105, 16, 7.6, 5.4)
    c.blob(boat, 1.0, 1.2)
    c.hline(16, 100, 110, 3); c.vline(105, 12, 20, 2)
    c.frame(113, 11, 119, 22, 3, fill=1); c.rect(114, 12, 118, 15, 2)
    c.frame(105, 25, 111, 31, 3, fill=2)
    c.a[deck & (x == 122)] = 1
    return c


def gangway():
    c = C(16, 8, 1)
    c.hline(3, 0, 16, 2); c.hline(7, 0, 16, 2)
    c.vline(0, 0, 8, 3); c.vline(15, 0, 8, 3); c.vline(1, 0, 8, 0); c.vline(14, 0, 8, 0)
    return c


def crate():
    c = C(16, 16)
    c.frame(0, 0, 16, 15, 3, fill=1)
    c.frame(2, 2, 14, 13, 3, fill=0)
    c.line(3, 3, 12, 11, 2); c.line(12, 3, 3, 11, 2)
    c.hline(15, 0, 16, 3); c.hline(14, 1, 15, 2)
    return c


def truck():
    c = on(PAVE, (32, 16))
    c.frame(10, 1, 31, 13, 3, fill=0)
    c.hline(4, 12, 29, 1); c.hline(7, 12, 29, 1); c.hline(10, 12, 29, 1); c.vline(20, 2, 12, 1)
    c.frame(1, 4, 11, 13, 3, fill=1)
    c.frame(3, 6, 8, 10, 3, fill=0); c.px(4, 7, 1)
    c.hline(13, 0, 32, 3)
    for cx in (6, 16, 25):
        c.ellipse(cx, 13.5, 2.6, 2.4, 3); c.px(cx - 1, 13, 1)
    return c


def dock_sign():
    c = on(PAVE, (16, 16))
    c.rect(3, 11, 5, 16, 3); c.rect(11, 11, 13, 16, 3)
    c.frame(1, 1, 15, 12, 3, fill=0)
    c.hline(4, 3, 13, 2); c.hline(6, 3, 10, 2); c.hline(8, 3, 12, 2)
    return c


def build():
    T = {}
    T[0x0A] = PAVE; T[0x14] = WATER; T[0x5C] = np.full((8, 8), 3, np.uint8)
    T[0x1A] = C(8, 8).paste(PAVE, 0, 0).ellipse(3.5, 4, 3, 2.6, 0, outline=3).a
    T[0x3A] = tex(lambda x, y: 3 if y in (0, 7) else (3 if x == (1 if y < 4 else 5) and y != 3 else (1 if y == 1 else 2)))
    c = C(8, 8).paste(WATER, 0, 0); c.ellipse(4, 4, 3.2, 3.0, 0, outline=3); c.px(3, 3, 1); c.hline(5, 3, 6, 1)
    T[0x31] = c.a
    c = C(8, 8).paste(WATER, 0, 0); c.hline(3, 1, 5, 0); c.hline(6, 4, 7, 0); T[0x2A] = c.a   # spare: foam
    put(T, gangway(), [[0x32, 0x3B]])
    put(T, crate(), [[0x56, 0x57], [0x01, 0x50]])
    put(T, dock_sign(), [[0x54, 0x3F], [0x08, 0x47]])
    put(T, truck(), [[0x48, 0x49, 0x4A, 0x4B], [0x58, 0x59, 0x3C, 0x4C]])
    put(T, ship(), SHIP)
    return T


@drawer("tilesets/ship_port.png")
def ship_port(rel, a):
    return build_sheet(build(), a, WALK, "ship_port")
