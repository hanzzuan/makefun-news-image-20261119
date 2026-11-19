"""THE WORLD — Thursday 19 November 2026.

A newspaper front page drawn procedurally in Python stdlib only.
No network, no fonts, no image files: every pixel comes from the code
below — a 5x7 bitmap font, rectangles, lines, circles and polygons —
and the PNG bytes are encoded by hand with zlib and CRC32.

Layout (1024 x 1024): masthead and the date in red, one lead story
(Trump, Xi and Putin meet in Shenzhen — the first-ever trilateral
summit), then Iran's strike on US bases in Kuwait and the Kerch Bridge
attack, and three smaller stories — Israel's push into Gaza, the GTA VI
global rollout, and Anthropic's $81.3bn IPO.
"""

import math
import os
import struct
import zlib

from font5x7 import glyph, text_height, text_width

W, H = 1024, 1024

PAPER = (253, 253, 247)
INK = (18, 18, 18)
RED = (186, 39, 32)
BLUE = (28, 68, 110)
GOLD = (176, 112, 24)
GREY = (128, 128, 122)
LIGHT = (236, 236, 229)
SKY = (205, 222, 235)
ORANGE = (214, 96, 32)
GREEN = (34, 120, 60)
SAND = (214, 196, 150)
SEA = (64, 120, 168)


class Page:
    """An RGB pixel buffer with small drawing helpers."""

    def __init__(self, width, height, colour):
        self.w = width
        self.h = height
        self.buf = bytearray(width * height * 3)
        self.fill_rect(0, 0, width, height, colour)

    def set(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = colour

    def fill_rect(self, x, y, w, h, colour):
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + w, self.w), min(y + h, self.h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i], self.buf[i + 1], self.buf[i + 2] = colour

    def hline(self, x, y, w, colour, t=1):
        self.fill_rect(x, y, w, t, colour)

    def vline(self, x, y, h, colour, t=1):
        self.fill_rect(x, y, t, h, colour)

    def rect(self, x, y, w, h, colour, t=1):
        self.hline(x, y, w, colour, t)
        self.hline(x, y + h - t, w, colour, t)
        self.vline(x, y, h, colour, t)
        self.vline(x + w - t, y, h, colour, t)

    def line(self, x0, y0, x1, y1, colour):
        """Bresenham line between two points."""
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, colour)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def thick_line(self, x0, y0, x1, y1, colour, t=3):
        """A line drawn t pixels wide, by offsetting across its normal."""
        dx, dy = x1 - x0, y1 - y0
        length = max(1, math.hypot(dx, dy))
        nx, ny = -dy / length, dx / length
        half = t // 2
        for k in range(-half, half + 1):
            ox, oy = round(nx * k), round(ny * k)
            self.line(x0 + ox, y0 + oy, x1 + ox, y1 + oy, colour)

    def circle(self, cx, cy, r, colour, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d <= r * r:
                        self.set(xx, yy, colour)
                elif r - 1 <= math.sqrt(d) <= r:
                    self.set(xx, yy, colour)

    def fill_poly(self, points, colour):
        """Scanline fill of a polygon given as (x, y) vertices."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                for x in range(int(xs[j]), int(xs[j + 1]) + 1):
                    self.set(x, y, colour)

    def star(self, cx, cy, r, colour):
        """A filled five-pointed star."""
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            rad = r if i % 2 == 0 else r * 0.42
            pts.append((cx + round(rad * math.cos(ang)),
                        cy + round(rad * math.sin(ang))))
        self.fill_poly(pts, colour)

    def burst(self, cx, cy, r, colour):
        """A jagged explosion starburst with twelve spikes."""
        pts = []
        for i in range(24):
            ang = -math.pi / 2 + i * math.pi / 12
            rad = r if i % 2 == 0 else r * 0.45
            pts.append((cx + round(rad * math.cos(ang)),
                        cy + round(rad * math.sin(ang))))
        self.fill_poly(pts, colour)


def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def encode_png(page):
    """Encode the page as a PNG: header, one IDAT, end marker."""
    raw = bytearray()
    for y in range(page.h):
        raw.append(0)  # filter type 0: none
        raw += page.buf[y * page.w * 3:(y + 1) * page.w * 3]
    ihdr = struct.pack(">IIBBBBB", page.w, page.h, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _chunk(b"IEND", b"")
    )


# ---------------------------------------------------------------- text

def draw_text(page, x, y, text, scale, colour, gap=1):
    """Draw one line of text, left-aligned at (x, y)."""
    cx = x
    for ch in text:
        rows = glyph(ch)
        for r in range(7):
            bits = rows[r]
            for c in range(5):
                if bits & (1 << (4 - c)):
                    page.fill_rect(cx + c * scale, y + r * scale,
                                   scale, scale, colour)
        cx += 5 * scale + gap
    return cx


def draw_centred(page, x, y, w, text, scale, colour, gap=1):
    """Draw one line centred in the band [x, x + w)."""
    tw = text_width(text, scale, gap)
    draw_text(page, x + (w - tw) // 2, y, text, scale, colour, gap)


# ---------------------------------------------------------------- panels

def panel(page, x, y, w, h):
    """A story panel: thin black frame on paper, with a hairline inside."""
    page.rect(x, y, w, h, INK, 2)
    page.rect(x + 4, y + 4, w - 8, h - 8, GREY, 1)


def kicker(page, x, y, text, colour=RED):
    """Small red section label with a square bullet."""
    page.fill_rect(x, y + 2, 10, 10, colour)
    draw_text(page, x + 16, y, text, 2, colour, gap=1)


def headline(page, x, y, w, lines, scale, colour=INK, gap=1, leading=None):
    """Centred headline lines; returns the y below the last line."""
    if leading is None:
        leading = text_height(scale) + 6
    cy = y
    for line in lines:
        draw_centred(page, x, cy, w, line, scale, colour, gap)
        cy += leading
    return cy


def rule(page, x, y, w, colour=INK, t=2):
    page.hline(x, y, w, colour, t)


# ---------------------------------------------------------------- visuals

def flag_usa(page, x, y, w, h):
    """Thirteen red and white stripes, blue canton with a grid of stars."""
    stripe = h // 13
    for i in range(13):
        colour = (178, 34, 52) if i % 2 == 0 else (245, 245, 245)
        page.fill_rect(x, y + i * stripe, w, stripe, colour)
    page.fill_rect(x, y, w * 2 // 5, stripe * 7, (60, 59, 110))
    for row in range(5):
        for col in range(6):
            sx = x + 8 + col * (w * 2 // 5 - 16) // 5
            sy = y + 6 + row * (stripe * 7 - 12) // 4
            page.circle(sx, sy, 2, (245, 245, 245), fill=True)
    page.rect(x, y, w, h, INK, 1)


def flag_china(page, x, y, w, h):
    """Red field, one large yellow star and four small ones."""
    page.fill_rect(x, y, w, h, (222, 41, 16))
    page.star(x + w // 5, y + h // 3, h // 5, GOLD)
    for sx, sy in ((w * 2 // 5, h // 6), (w // 2, h // 8),
                   (w * 3 // 5, h // 5), (w * 3 // 5, h * 2 // 5)):
        page.star(x + sx, y + sy, h // 12, GOLD)
    page.rect(x, y, w, h, INK, 1)


def flag_russia(page, x, y, w, h):
    """White over blue over red horizontal tricolour."""
    third = h // 3
    page.fill_rect(x, y, w, third, (245, 245, 245))
    page.fill_rect(x, y + third, w, third, (0, 57, 166))
    page.fill_rect(x, y + 2 * third, w, h - 2 * third, (213, 0, 50))
    page.rect(x, y, w, h, INK, 1)


def missile(page, x, y, angle_deg, s, colour=INK):
    """A small missile body with fins, drawn along an angle."""
    a = math.radians(angle_deg)
    dx, dy = math.cos(a), math.sin(a)
    nx, ny = -dy, dx
    nose = (x + round(dx * 16 * s), y + round(dy * 16 * s))
    tail = (x - round(dx * 10 * s), y - round(dy * 10 * s))
    page.thick_line(tail[0], tail[1], nose[0], nose[1], colour, 4 * s)
    fin1 = (tail[0] + round(nx * 6 * s), tail[1] + round(ny * 6 * s))
    fin2 = (tail[0] - round(nx * 6 * s), tail[1] - round(ny * 6 * s))
    page.fill_poly([tail, fin1, (tail[0] + round(dx * 6 * s),
                                 tail[1] + round(dy * 6 * s))], colour)
    page.fill_poly([tail, fin2, (tail[0] + round(dx * 6 * s),
                                 tail[1] + round(dy * 6 * s))], colour)
    page.circle(nose[0], nose[1], 2 * s, RED, fill=True)


def base_buildings(page, x, y, w, h, colour=GREY):
    """Low military-base blocks with a fence line in front."""
    page.fill_rect(x, y + h - 26, w, 26, LIGHT)
    page.fill_rect(x + 10, y + h - 52, 60, 26, colour)
    page.fill_rect(x + 90, y + h - 66, 70, 40, colour)
    page.fill_rect(x + 180, y + h - 46, 55, 20, colour)
    page.fill_rect(x + 255, y + h - 60, 64, 34, colour)
    page.fill_rect(x + 340, y + h - 50, 58, 24, colour)
    for bx in range(x, x + w, 22):
        page.vline(bx, y + h - 18, 18, INK, 1)
    page.hline(x, y + h - 18, w, INK, 1)


def bridge_scene(page, x, y, w, h):
    """A road bridge over blue water, hit by an explosion mid-span."""
    page.fill_rect(x, y, w, h, SKY)
    page.fill_rect(x, y + h * 2 // 3, w, h // 3, SEA)
    for wx in range(x + 8, x + w, 46):
        page.hline(wx, y + h * 3 // 4, 26, (255, 255, 255), 2)
        page.hline(wx + 12, y + h * 7 // 8, 26, (255, 255, 255), 2)
    # Deck and arch.
    page.fill_rect(x, y + h // 2, w, 8, INK)
    for px in range(x + 20, x + w, 70):
        page.fill_rect(px, y + h // 2 + 8, 6, h // 6, INK)
    page.thick_line(x, y + h // 2, x + w // 2, y + h // 4, INK, 3)
    page.thick_line(x + w, y + h // 2, x + w // 2, y + h // 4, INK, 3)
    # Explosion on the deck, left of centre, with smoke.
    page.burst(x + w // 3, y + h // 2 - 6, 26, ORANGE)
    page.burst(x + w // 3, y + h // 2 - 6, 14, GOLD)
    page.circle(x + w // 3 - 34, y + h // 2 - 30, 10, GREY, fill=True)
    page.circle(x + w // 3 - 20, y + h // 2 - 42, 13, GREY, fill=True)
    page.circle(x + w // 3 - 6, y + h // 2 - 34, 9, GREY, fill=True)


def arrow_push(page, x, y, w, h, colour=RED):
    """A big rightward arrow crossing a dashed yellow line."""
    page.fill_rect(x, y, w, h, SAND)
    # City blocks on the left, open ground on the right.
    for bx, bh in ((8, 34), (52, 52), (104, 28)):
        page.fill_rect(x + bx, y + h - bh - 8, 34, bh, GREY)
        page.fill_rect(x + bx + 6, y + h - bh, 6, 6, GOLD)
        page.fill_rect(x + bx + 20, y + h - bh - 2, 6, 6, GOLD)
    # The Yellow Line, dashed.
    lx = x + w // 2
    for yy in range(y + 6, y + h - 6, 14):
        page.vline(lx, yy, 8, GOLD, 4)
    # Arrow pushing across it.
    ay = y + h // 2
    page.fill_rect(x + 30, ay - 9, w - 110, 18, colour)
    page.fill_poly([(x + w - 80, ay - 26), (x + w - 24, ay),
                    (x + w - 80, ay + 26)], colour)


def sunset_skyline(page, x, y, w, h):
    """Orange sunset bands, a black skyline, and a big VI in the sun."""
    bands = [(214, 96, 32), (232, 130, 60), (240, 170, 90), (250, 210, 140)]
    bh = h // len(bands)
    for i, colour in enumerate(bands):
        page.fill_rect(x, y + i * bh, w, bh, colour)
    page.circle(x + w // 2, y + h // 2 - 6, 34, (250, 240, 200), fill=True)
    tops = [0.35, 0.55, 0.25, 0.65, 0.45, 0.3, 0.5]
    bw = w // len(tops)
    for i, frac in enumerate(tops):
        th = int(h * frac)
        page.fill_rect(x + i * bw + 2, y + h - th, bw - 4, th, INK)
        page.fill_rect(x + i * bw + bw // 2 - 2, y + h - th + 6, 4, 5, GOLD)
    page.fill_rect(x, y + h - 4, w, 4, INK)
    # The big VI goes on top of the skyline so it stays readable.
    draw_centred(page, x + w // 2 - 40, y + h // 2 - 28, 80, "VI", 6, RED, gap=2)


def ipo_chart(page, x, y, w, h):
    """Ascending bars with a steep green arrow — a record IPO day."""
    page.fill_rect(x, y, w, h, LIGHT)
    page.rect(x, y, w, h, GREY, 1)
    bars = [18, 30, 26, 44, 58, 74]
    bw = w // (len(bars) + 1)
    for i, bh in enumerate(bars):
        bx = x + (i + 1) * bw - bw // 2
        page.fill_rect(bx, y + h - 8 - bh, bw - 10, bh, BLUE)
    page.thick_line(x + 8, y + h - 24, x + w // 2, y + h - 58, GREEN, 4)
    page.thick_line(x + w // 2, y + h - 58, x + w - 10, y + 12, GREEN, 4)
    page.fill_poly([(x + w - 10, y + 12), (x + w - 34, y + 10),
                    (x + w - 12, y + 34)], GREEN)
    draw_centred(page, x, y + 4, w, "$81.3BN", 2, GREEN, gap=1)


# ---------------------------------------------------------------- layout

def draw_masthead(page):
    """THE WORLD in large type, then the date in red, large and plain."""
    draw_centred(page, 0, 26, W, "THE WORLD", 8, INK, gap=2)
    rule(page, 24, 96, W - 48, INK, 3)
    rule(page, 24, 102, W - 48, RED, 2)
    draw_centred(page, 0, 112, W, "THURSDAY 19 NOVEMBER 2026", 4, RED, gap=2)


def draw_lead(page):
    """Shenzhen: Trump, Xi and Putin meet — the first-ever trilateral."""
    x, y, w, h = 24, 152, 976, 296
    panel(page, x, y, w, h)
    kicker(page, x + 18, y + 16, "SHENZHEN  •  TRILATERAL SUMMIT")
    cy = headline(page, x + 18, y + 44, w - 36,
                  ["TRUMP, XI AND PUTIN", "MEET IN CHINA"],
                  5, INK, gap=2, leading=42)
    draw_centred(page, x, cy + 6, w,
                 "FIRST-EVER THREE-WAY SUMMIT ON APEC SIDELINES",
                 3, BLUE, gap=1)
    # Visual strip: the three flags side by side, labelled below.
    vy = y + 172
    flag_usa(page, x + 40, vy, 280, 96)
    draw_centred(page, x + 40, vy + 104, 280, "USA", 2, INK, gap=1)
    flag_china(page, x + 348, vy, 280, 96)
    draw_centred(page, x + 348, vy + 104, 280, "CHINA", 2, INK, gap=1)
    flag_russia(page, x + 656, vy, 280, 96)
    draw_centred(page, x + 656, vy + 104, 280, "RUSSIA", 2, INK, gap=1)


def draw_iran(page):
    """Kuwait: Iran strikes US military bases with drones and missiles."""
    x, y, w, h = 24, 464, 476, 232
    panel(page, x, y, w, h)
    kicker(page, x + 16, y + 14, "KUWAIT  •  GULF ESCALATION")
    cy = headline(page, x + 16, y + 40, w - 32,
                  ["IRAN STRIKES U.S.", "BASES IN KUWAIT"], 4, INK, gap=1)
    draw_centred(page, x, cy + 4, w, "DRONES AND MISSILES FLY", 2, INK, gap=1)
    # Visual: missiles diving onto the base, one burst on impact.
    sy = y + 148
    page.fill_rect(x + 16, sy, w - 32, 68, SKY)
    base_buildings(page, x + 16, sy, w - 32, 68)
    page.thick_line(x + 96, sy + 4, x + 128, sy + 26, GREY, 2)
    missile(page, x + 136, sy + 30, 55, 2)
    page.thick_line(x + 280, sy + 2, x + 306, sy + 20, GREY, 2)
    missile(page, x + 314, sy + 24, 70, 2)
    page.burst(x + 380, sy + 46, 18, ORANGE)
    page.burst(x + 380, sy + 46, 9, GOLD)


def draw_kerch(page):
    """Kerch: the bridge to Crimea is attacked again."""
    x, y, w, h = 524, 464, 476, 232
    panel(page, x, y, w, h)
    kicker(page, x + 16, y + 14, "KERCH  •  CRIMEA")
    cy = headline(page, x + 16, y + 40, w - 32,
                  ["KERCH BRIDGE", "HIT AGAIN"], 4, INK, gap=1)
    draw_centred(page, x, cy + 4, w, "KEY LINK TO CRIMEA DAMAGED", 2, INK, gap=1)
    bridge_scene(page, x + 16, y + 148, w - 32, 68)


def draw_gaza(page):
    """Gaza: Israeli troops push in beyond the Yellow Line."""
    x, y, w, h = 24, 712, 309, 272
    panel(page, x, y, w, h)
    kicker(page, x + 14, y + 14, "GAZA")
    cy = headline(page, x + 14, y + 40, w - 28,
                  ["ISRAEL PUSHES", "INTO GAZA"], 3, INK, gap=1)
    draw_centred(page, x, cy + 4, w, "BEYOND THE YELLOW LINE", 2, INK, gap=1)
    arrow_push(page, x + 14, y + 148, w - 28, 108)


def draw_gta(page):
    """GTA VI begins its global rollout."""
    x, y, w, h = 357, 712, 309, 272
    panel(page, x, y, w, h)
    kicker(page, x + 14, y + 14, "GAMING")
    cy = headline(page, x + 14, y + 40, w - 28,
                  ["GTA VI ROLLS OUT", "WORLDWIDE"], 3, INK, gap=1)
    draw_centred(page, x, cy + 4, w, "GLOBAL ROLLOUT BEGINS", 2, INK, gap=1)
    sunset_skyline(page, x + 14, y + 148, w - 28, 108)


def draw_anthropic(page):
    """Anthropic raises $81.3bn in the biggest IPO of all time."""
    x, y, w, h = 690, 712, 309, 272
    panel(page, x, y, w, h)
    kicker(page, x + 14, y + 14, "TECH  •  IPO")
    cy = headline(page, x + 14, y + 40, w - 28,
                  ["ANTHROPIC'S $81BN", "IPO"], 3, INK, gap=1)
    draw_centred(page, x, cy + 4, w, "BIGGEST IPO OF ALL TIME", 2, INK, gap=1)
    ipo_chart(page, x + 14, y + 148, w - 28, 108)


def draw_footer(page):
    draw_centred(page, 0, 994, W,
                 "THE WORLD  •  SIX STORIES, ONE DAY  •  19 NOVEMBER 2026",
                 2, GREY, gap=1)


def build():
    page = Page(W, H, PAPER)
    page.rect(8, 8, W - 16, H - 16, INK, 3)
    draw_masthead(page)
    draw_lead(page)
    draw_iran(page)
    draw_kerch(page)
    draw_gaza(page)
    draw_gta(page)
    draw_anthropic(page)
    draw_footer(page)
    return page


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png(build())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
