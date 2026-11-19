"""THE WORLD — front page for Thursday, 19 November 2026.

Draws a 1024x1024 newspaper front page with a hand-authored 5x7 bitmap
font (font5x7.py) and writes it as a PNG with a small encoder built on
the standard library alone (struct + zlib). No third-party code, no
network, no timestamps: every run writes byte-identical output.
"""

import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from font5x7 import draw_text, text_width, wrap_text

W = 1024
H = 1024
MARGIN = 36

PAPER = (255, 255, 255)
INK = (17, 17, 17)
RED = (155, 27, 27)
SKY = (201, 220, 234)
SUN = (232, 134, 46)
WATER = (46, 110, 158)
WATER_DARK = (36, 90, 128)
NAVY = (34, 48, 74)
WINDOW = (255, 215, 106)
PALM = (30, 91, 46)
TRUNK = (107, 74, 43)
CLOUD = (255, 255, 255)


class Canvas:
    """A plain RGB pixel buffer with a few drawing helpers."""

    def __init__(self, width, height, background):
        self.w = width
        self.h = height
        self.px = bytearray(bytes(background) * (width * height))

    def set_px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            off = (y * self.w + x) * 3
            self.px[off] = color[0]
            self.px[off + 1] = color[1]
            self.px[off + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            off = (yy * self.w + x0) * 3
            self.px[off:off + len(row)] = row

    def hline(self, x1, x2, y, color, thickness=1):
        self.fill_rect(x1, y, x2 - x1, thickness, color)

    def vline(self, x, y1, y2, color, thickness=1):
        self.fill_rect(x, y1, thickness, y2 - y1, color)

    def rect_outline(self, x, y, w, h, color, thickness=1):
        self.hline(x, x + w, y, color, thickness)
        self.hline(x, x + w, y + h - thickness, color, thickness)
        self.vline(x, y, y + h, color, thickness)
        self.vline(x + w - thickness, y, y + h, color, thickness)

    def line(self, x1, y1, x2, y2, color, thickness=1):
        """Bresenham line, square brush of the given thickness."""
        dx = abs(x2 - x1)
        dy = -abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx + dy
        half = thickness // 2
        while True:
            self.fill_rect(x1 - half, y1 - half, thickness, thickness, color)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x1 += sx
            if e2 <= dx:
                err += dx
                y1 += sy

    def disc(self, cx, cy, r, color):
        """Filled circle."""
        for yy in range(cy - r, cy + r + 1):
            half = int((r * r - (yy - cy) * (yy - cy)) ** 0.5)
            self.hline(cx - half, cx + half + 1, yy, color)


def write_png(path, canvas):
    """Encode the canvas as a deterministic PNG (no time chunks)."""

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.px[y * stride:(y + 1) * stride]
    header = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    data = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )
    with open(path, "wb") as handle:
        handle.write(data)


def centred(canvas, y, text, scale, color):
    """Draw one line centred on the page; return its x start."""
    x = (W - text_width(text, scale)) // 2
    draw_text(canvas, x, y, text, scale, color)
    return x


def paragraph(canvas, x, y, width, text, scale, color, leading):
    """Draw wrapped body text; return the y just below the last line."""
    for i, line in enumerate(wrap_text(text, width, scale)):
        draw_text(canvas, x, y + i * leading, line, scale, color)
    return y + len(wrap_text(text, width, scale)) * leading


def draw_skyline(canvas, box_x, box_y, box_w, box_h):
    """Vice City waterfront at dusk: sky, sun, towers, palms, water."""
    sky_bottom = box_y + 102
    canvas.fill_rect(box_x, box_y, box_w, sky_bottom - box_y, SKY)
    canvas.fill_rect(box_x, sky_bottom, box_w, box_y + box_h - sky_bottom, WATER)

    # Sun low over the bay, with its reflection streak in the water.
    sun_cx = box_x + 150
    sun_cy = box_y + 38
    canvas.disc(sun_cx, sun_cy, 22, SUN)
    canvas.fill_rect(sun_cx - 8, sky_bottom, 16, box_y + box_h - sky_bottom, SUN)

    # A few flat clouds, each a row of overlapping discs, set where no
    # tower reaches them.
    for cx, cy in ((250, 26), (420, 20), (580, 30), (900, 24)):
        for dx, dr in ((-18, 9), (0, 12), (18, 9)):
            canvas.disc(box_x + cx + dx, box_y + cy, dr, CLOUD)

    # Towers along the far shore; each rises from the waterline.
    towers = (
        (24, 66, 44), (104, 52, 40), (168, 88, 40), (266, 60, 78),
        (336, 78, 52), (424, 58, 88), (492, 92, 44), (594, 62, 72),
        (666, 84, 48), (760, 56, 84), (826, 76, 56), (912, 46, 40),
    )
    for off, tw, th in towers:
        tx = box_x + off
        top = sky_bottom - th
        canvas.fill_rect(tx, top, tw, th, NAVY)
        # Lit windows in a fixed pattern: every third cell stays dark.
        for wy in range(top + 8, sky_bottom - 8, 12):
            for wx in range(tx + 7, tx + tw - 8, 11):
                if ((wx // 11) + (wy // 12)) % 3 != 0:
                    canvas.fill_rect(wx, wy, 4, 5, WINDOW)
        # Reflection streak under the tower, broken by the water.
        canvas.fill_rect(tx + 6, sky_bottom + 4, tw - 12, 18, WATER_DARK)

    # Palm trees on the near shore, left and right.
    for base_x, lean in ((88, 14), (872, -12)):
        top_x = base_x + lean
        top_y = box_y + box_h - 78
        canvas.line(base_x, box_y + box_h, top_x, top_y, TRUNK, 4)
        for dx, dy in ((-46, -6), (-30, -22), (-8, -30), (18, -26), (40, -10)):
            canvas.line(top_x, top_y, top_x + dx, top_y + dy, PALM, 3)
        for dx, dy in ((-38, 10), (34, 8)):
            canvas.line(top_x, top_y, top_x + dx, top_y + dy, PALM, 3)

    canvas.rect_outline(box_x, box_y, box_w, box_h, INK, 2)


LEAD_BODY = (
    "Grand Theft Auto VI went on sale around the world on Thursday, sending "
    "players back to Vice City after a wait of thirteen years. Shops reported "
    "long queues and midnight openings, and the launch is expected to be one "
    "of the biggest entertainment releases ever."
)

JEFFRIES_BODY = (
    "Democrats in the House nominated Hakeem Jeffries for Speaker, putting "
    "him on course to become the first African-American to hold the post. "
    "He has led his party's caucus since 2023."
)

ANTHROPIC_BODY = (
    "Anthropic raised $81.3 billion in the largest initial public offering "
    "in history, as investors rushed for a share of the AI boom. The listing "
    "values the maker of Claude far above any previous debut."
)

VOYAGER_BODY = (
    "NASA's Voyager 1 has become the first human-made object to travel one "
    "light-day from Earth, nearly fifty years after launch. The probe, "
    "launched in 1977, still sends data home."
)

EU_BODY = (
    "The European Union proposed a 45-billion-euro loan to Ukraine, repaid "
    "from Russian assets once Moscow pays reparations. It would keep Kyiv "
    "funded while frozen funds are settled."
)

GAZA_BODY = (
    "Australia, Canada, Italy and Britain jointly called on Israel to let "
    "aid reach Gaza without restriction, saying floods have deepened the "
    "suffering. Access must be immediate, the allies said."
)


def build_page():
    """Compose the front page and return the finished canvas."""
    page = Canvas(W, H, PAPER)
    page.rect_outline(14, 14, W - 28, H - 28, INK, 2)

    # Masthead.
    draw_text(page, (W - text_width("THE WORLD", 11)) // 2, 34,
              "THE WORLD", 11, INK)
    page.hline(MARGIN, W - MARGIN, 120, INK, 4)

    # Dateline row.
    draw_text(page, MARGIN, 132, "EST. 1894", 2, INK)
    centred(page, 132, "THURSDAY, 19 NOVEMBER 2026", 2, INK)
    price = "PRICE $1.00"
    draw_text(page, W - MARGIN - text_width(price, 2), 132, price, 2, INK)
    page.hline(MARGIN, W - MARGIN, 154, INK, 1)

    # Lead story: kicker, two-line headline, deck, illustration, body.
    centred(page, 166, "CULTURE / GAMES", 2, RED)
    centred(page, 188, "GRAND THEFT AUTO VI", 5, INK)
    centred(page, 228, "ROLLS OUT WORLDWIDE", 5, INK)
    centred(page, 272, "GAMERS RETURN TO VICE CITY AFTER A THIRTEEN-YEAR WAIT",
            2, INK)
    draw_skyline(page, MARGIN, 298, W - 2 * MARGIN, 150)

    lead_lines = wrap_text(LEAD_BODY, 466, 2)
    half = (len(lead_lines) + 1) // 2
    for i, line in enumerate(lead_lines[:half]):
        draw_text(page, MARGIN, 460 + i * 18, line, 2, INK)
    for i, line in enumerate(lead_lines[half:]):
        draw_text(page, 522, 460 + i * 18, line, 2, INK)
    page.hline(MARGIN, W - MARGIN, 544, INK, 1)

    # Middle row: Washington and the markets, side by side.
    draw_text(page, MARGIN, 556, "WASHINGTON", 2, RED)
    draw_text(page, MARGIN, 578, "A FIRST FOR THE HOUSE", 3, INK)
    paragraph(page, MARGIN, 608, 466, JEFFRIES_BODY, 2, INK, 18)

    draw_text(page, 522, 556, "TECH / MARKETS", 2, RED)
    draw_text(page, 522, 578, "THE BIGGEST IPO EVER", 3, INK)
    paragraph(page, 522, 608, 466, ANTHROPIC_BODY, 2, INK, 18)
    page.hline(MARGIN, W - MARGIN, 716, INK, 1)

    # Bottom row: three stories in three columns.
    draw_text(page, MARGIN, 728, "SPACE", 2, RED)
    draw_text(page, MARGIN, 750, "ONE LIGHT-DAY", 3, INK)
    draw_text(page, MARGIN, 776, "FROM EARTH", 3, INK)
    paragraph(page, MARGIN, 806, 300, VOYAGER_BODY, 2, INK, 18)

    draw_text(page, 362, 728, "EUROPE", 2, RED)
    draw_text(page, 362, 750, "45 BILLION", 3, INK)
    draw_text(page, 362, 776, "FOR KYIV", 3, INK)
    paragraph(page, 362, 806, 300, EU_BODY, 2, INK, 18)

    draw_text(page, 688, 728, "MIDDLE EAST", 2, RED)
    draw_text(page, 688, 750, "LET THE AID IN", 3, INK)
    paragraph(page, 688, 806, 300, GAZA_BODY, 2, INK, 18)

    # Footer.
    page.hline(MARGIN, W - MARGIN, 962, INK, 1)
    centred(page, 972, "THE WORLD - THURSDAY, 19 NOVEMBER 2026", 2, INK)
    return page


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        out_dir = "/output" if os.path.isdir("/output") else "out"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    write_png(path, build_page())
    print("wrote " + path)


if __name__ == "__main__":
    main()
