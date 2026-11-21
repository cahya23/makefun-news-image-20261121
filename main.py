#!/usr/bin/env python3
"""News front page for Saturday, 21 November 2026.

Draws a one-page newspaper front page with the day's world news and
writes it to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

Pure Python standard library only: the picture is painted pixel by
pixel onto a byte buffer, text is set with a small built-in 5x7
bitmap font, and the PNG file is encoded by hand with zlib and
struct. No network, no files read, no randomness: every run writes
exactly the same bytes.
"""

import math
import os
import struct
import sys
import zlib

W, H = 1024, 1024

PAPER = (247, 243, 232)   # warm newsprint
INK = (20, 20, 20)        # near-black ink
RED = (178, 39, 30)       # headline red
BLUE = (29, 78, 137)      # deep blue for the map sea
LIGHT_BLUE = (198, 220, 238)
GREY = (110, 108, 100)
GOLD = (176, 132, 40)


def _crc(data):
    return zlib.crc32(data) & 0xFFFFFFFF


def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    return out + struct.pack(">I", _crc(kind + data))


def write_png(path, pixels):
    """Encode an RGB byte buffer as a PNG file, deterministically."""
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw += pixels[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    blob = b"\x89PNG\r\n\x1a\n"
    blob += _chunk(b"IHDR", ihdr)
    blob += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    blob += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(blob)


class Page:
    """A 1024x1024 RGB canvas with rectangle, line and text drawing."""

    def __init__(self):
        self.px = bytearray(PAPER * W * H)

    def set(self, x, y, color):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(max(0, y), min(H, y + h)):
            base = (yy * W + max(0, x)) * 3
            span = min(W, x + w) - max(0, x)
            if span > 0:
                self.px[base:base + span * 3] = bytes(color) * span

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def poly(self, points, color, fill=None):
        if fill is not None:
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            for yy in range(min(ys), max(ys) + 1):
                cuts = []
                n = len(points)
                for i in range(n):
                    x0, y0 = points[i]
                    x1, y1 = points[(i + 1) % n]
                    if (y0 <= yy < y1) or (y1 <= yy < y0):
                        t = (yy - y0) / (y1 - y0)
                        cuts.append(int(x0 + t * (x1 - x0)))
                cuts.sort()
                for k in range(0, len(cuts) - 1, 2):
                    self.hline(cuts[k], yy, cuts[k + 1] - cuts[k], fill)
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            self.line(x0, y0, x1, y1, color)

    def star(self, cx, cy, r, color):
        pts = []
        for i in range(10):
            ang = -1.5708 + i * 0.6283
            rr = r if i % 2 == 0 else r * 0.45
            pts.append((int(cx + rr * math.cos(ang)),
                        int(cy + rr * math.sin(ang))))
        self.poly(pts, color, fill=color)


# A 5x7 bitmap font. Each glyph is 7 rows of 5 bits, '1' = ink.
# Lowercase letters are rendered with the matching capital glyph.
FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
}


FONT.update({
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    "3": ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ",": ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    ":": ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    ";": ["00000", "01100", "01100", "00000", "01100", "00100", "01000"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "?": ["01110", "10001", "00001", "00110", "00100", "00000", "00100"],
    "-": ["00000", "00000", "00000", "01110", "00000", "00000", "00000"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    '"': ["01010", "01010", "01010", "00000", "00000", "00000", "00000"],
    "(": ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ")": ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    "%": ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    "+": ["00000", "00100", "00100", "01110", "00100", "00100", "00000"],
    "&": ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    "=": ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
    "*": ["00000", "00100", "10101", "01110", "10101", "00100", "00000"],
    "$": ["00100", "01111", "10100", "01110", "00101", "11110", "00100"],
})


def text_width(s, scale):
    """Width in pixels of a string drawn at a scale."""
    return len(s) * 6 * scale


def draw_text(page, x, y, s, scale, color):
    """Draw a string left-aligned at (x, y); returns the width used."""
    s = s.upper()
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT["?"])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    page.rect(cx + col * scale, y + row * scale,
                              scale, scale, color)
        cx += 6 * scale
    return cx - x


def draw_centered(page, cx, y, s, scale, color):
    draw_text(page, cx - text_width(s, scale) // 2, y, s, scale, color)


def wrap(s, max_chars):
    """Word-wrap a string into lines of at most max_chars characters."""
    lines, cur = [], ""
    for word in s.upper().split(" "):
        if cur and len(cur) + 1 + len(word) > max_chars:
            lines.append(cur)
            cur = word
        else:
            cur = (cur + " " + word).strip()
    if cur:
        lines.append(cur)
    return lines


def draw_para(page, x, y, s, scale, color, max_chars, leading=None):
    """Draw a wrapped paragraph; returns the y just below the last line."""
    if leading is None:
        leading = 9 * scale
    for line in wrap(s, max_chars):
        draw_text(page, x, y, line, scale, color)
        y += leading
    return y


def kicker(page, x, y, s, color=RED, scale=2):
    draw_text(page, x, y, s, scale, color)
    return y + 9 * scale


# ---------------------------------------------------------------------------
# Layout: a newspaper front page, 1024 x 1024.
#   masthead ............ y   24 - 150
#   lead + Poland ....... y  170 - 560
#   three columns ....... y  580 - 850
#   Also Today strip .... y  870 - 970
#   footer .............. y  985 - 1010
# ---------------------------------------------------------------------------

def draw_masthead(page):
    page.rect(16, 16, W - 32, H - 32, INK)          # outer frame (1px ring)
    page.rect(20, 20, W - 40, H - 40, PAPER)
    page.hline(24, 28, W - 48, INK, 2)
    draw_centered(page, W // 2, 44, "THE WORLD TODAY", 6, INK)
    page.hline(24, 100, W - 48, INK, 3)
    draw_centered(page, W // 2, 112, "SATURDAY, 21 NOVEMBER 2026", 3, RED)
    draw_centered(page, W // 2, 138, "ONE DAY IN THE WORLD  -  SIX STORIES, ONE PAGE",
                  2, GREY)
    page.hline(24, 162, W - 48, INK, 2)


def draw_peru_map(page, x, y, w, h):
    """Simplified map of Peru with a star on Junin and a seismograph."""
    page.rect(x, y, w, h, LIGHT_BLUE)
    # Rough outline of Peru, scaled into the box.
    pts = [(x + 78, y + 8), (x + 190, y + 6), (x + 232, y + 34),
           (x + 246, y + 82), (x + 214, y + 128), (x + 176, y + 168),
           (x + 118, y + 172), (x + 66, y + 132), (x + 40, y + 78),
           (x + 46, y + 34)]
    page.poly(pts, INK, fill=(232, 214, 170))
    page.star(x + 148, y + 92, 14, RED)
    draw_text(page, x + 168, y + 84, "JUNIN", 2, RED)
    draw_text(page, x + 12, y + 10, "PERU", 2, BLUE)
    # Seismograph zigzag along the bottom of the box.
    pts = [(x + 8, y + h - 26)]
    for dx, dy in [(30, 0), (8, -14), (8, 16), (8, -20), (8, 10),
                   (8, -8), (8, 18), (8, -16), (8, 6), (30, 0)]:
        pts.append((pts[-1][0] + dx, pts[-1][1] + dy))
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        page.line(x0, y0, x1, y1, INK)


def draw_lead(page):
    x, y, w = 24, 178, 620
    y = kicker(page, x, y, "LEAD  -  SOUTH AMERICA")
    draw_text(page, x, y, "QUAKE SHAKES", 5, INK)
    y += 5 * 9 + 4
    draw_text(page, x, y, "PERU", 5, RED)
    draw_text(page, x + 5 * 6 * 5 + 24, y + 12, "6.8", 5, RED)
    y += 5 * 9 + 10
    draw_para(page, x, y,
              "A magnitude 6.8 earthquake struck the Andean region of "
              "Junin in central Peru, shaking buildings in the capital, "
              "Lima, about 320 km away.", 2, INK, 52)
    y += 3 * 18 + 8
    draw_peru_map(page, x, y, 300, 176)
    end_y = draw_para(page, x + 316, y,
                      "THE QUAKE WAS DEEP, ABOUT 129 KM DOWN, AND WAS FELT "
                      "ACROSS THE REGION. PEOPLE RAN INTO THE STREETS IN "
                      "LIMA. THERE WERE NO IMMEDIATE REPORTS OF DEATHS OR "
                      "MAJOR DAMAGE.",
                      2, INK, 25)
    draw_text(page, x + 316, end_y + 6, "MAP: JUNIN, PERU", 2, GREY)


def draw_poland(page):
    x, y, w = 668, 178, 332
    y = kicker(page, x, y, "EUROPE  -  NATO'S BORDER")
    draw_text(page, x, y, "MISSILE LANDS", 3, INK)
    y += 3 * 9 + 4
    draw_text(page, x, y, "IN POLAND", 3, INK)
    y += 3 * 9 + 8
    draw_para(page, x, y,
              "A Russian Kh-101 cruise missile came down in fields near "
              "Nowy Lipowiec in south-east Poland. A second missile and a "
              "jet-powered drone also crossed the border. No one was hurt "
              "and nothing was damaged.", 2, INK, 27)
    y += 8 * 18 + 6
    page.hline(x, y, w, GREY, 1)
    y += 10
    y = kicker(page, x, y, "WHAT WAS SAID")
    draw_para(page, x, y,
              "\"IT DOES NOT LOOK LIKE AN ACCIDENT. WE ARE DEALING WITH A "
              "DELIBERATE PROVOCATION,\" SAID PM DONALD TUSK. NATO CALLED "
              "IT A GRAVE VIOLATION OF POLISH AIRSPACE.", 2, INK, 27)


def draw_middle(page):
    y0 = 596
    page.hline(24, y0 - 14, W - 48, INK, 2)
    cols = [
        (24, "CLIMATE  -  COP31",
         "TALKS STALL IN ANTALYA",
         "Climate talks in Turkey slipped into overtime. The latest draft "
         "deal drops any mention of moving away from fossil fuels and "
         "drops a $120bn target for adaptation finance. A new draft was "
         "promised for Saturday morning."),
        (356, "UNITED STATES  -  AI",
         "TRUMP: TAX DATA CENTRES ABROAD",
         "President Trump said the US would put a \"tremendous tax\" on "
         "American firms building AI data centres abroad, saying the most "
         "advanced AI must stay in American hands. He also urged Nvidia "
         "to rehire Jensen Huang."),
        (688, "MARKETS  -  ASIA",
         "RECORD CASH FLOWS INTO INDIA",
         "Foreign investors put a net Rs 1.22 lakh crore into Indian "
         "shares between 2 and 20 November, the biggest monthly inflow "
         "on record, beating the Rs 70,896 crore high of November 2020."),
    ]
    for x, kick, head, body in cols:
        y = y0
        y = kicker(page, x, y, kick)
        y = draw_para(page, x, y, head, 3, INK, 17)
        y += 6
        draw_para(page, x, y, body, 2, INK, 26)
        if x < 688:
            page.vline(x + 308, y0, 240, GREY, 1)


def draw_also(page):
    y0 = 858
    page.hline(24, y0 - 12, W - 48, INK, 2)
    draw_text(page, 24, y0, "ALSO TODAY", 3, RED)
    items = [
        "KL RAHUL: FIRST INDIAN OPENER WITH TEST CENTURIES IN ALL SENA COUNTRIES",
        "NEPAL PM BALEN SHAH HEADS TO DELHI FOR HIS FIRST FOREIGN VISIT",
        "DENMARK EXPELS RUSSIAN DIPLOMAT OVER ALLEGED PLOT TO KILL A RAPPER",
        "GAZA: ISRAELI DRONE STRIKES KILL SEVEN IN CENTRAL GAZA",
    ]
    y = y0 + 3 * 9 + 10
    for item in items:
        draw_text(page, 40, y, "*", 2, RED)
        y = draw_para(page, 58, y, item, 2, INK, 78)
        y += 2
    page.hline(24, 978, W - 48, INK, 2)
    draw_centered(page, W // 2, 984,
                  "ALL STORIES AS REPORTED ON SATURDAY, 21 NOVEMBER 2026",
                  2, GREY)


def build():
    page = Page()
    draw_masthead(page)
    draw_lead(page)
    draw_poland(page)
    draw_middle(page)
    draw_also(page)
    return page


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    page = build()
    path = os.path.join(out_dir, "entry.png")
    write_png(path, page.px)
    print("wrote", path, os.path.getsize(path), "bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
