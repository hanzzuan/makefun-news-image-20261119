"""Hand-drawn 5x7 bitmap font for THE WORLD front page, 19 November 2026.

Each glyph is seven rows of five pixels, stored as seven integers.
Bit 4 is the leftmost column, bit 0 the rightmost. A set bit is ink.
Only uppercase letters, digits and the punctuation the front page needs
are covered; anything else renders as a blank.
"""

# Letter glyphs, A through M. Each tuple is seven row masks, top to bottom.
GLYPHS = {
    "A": (14, 17, 17, 31, 17, 17, 17),
    "B": (30, 17, 17, 30, 17, 17, 30),
    "C": (14, 17, 16, 16, 16, 17, 14),
    "D": (30, 17, 17, 17, 17, 17, 30),
    "E": (31, 16, 16, 30, 16, 16, 31),
    "F": (31, 16, 16, 30, 16, 16, 16),
    "G": (14, 17, 16, 23, 17, 17, 14),
    "H": (17, 17, 17, 31, 17, 17, 17),
    "I": (31, 4, 4, 4, 4, 4, 31),
    "J": (7, 2, 2, 2, 2, 18, 12),
    "K": (17, 18, 20, 24, 20, 18, 17),
    "L": (16, 16, 16, 16, 16, 16, 31),
    "M": (17, 27, 21, 21, 17, 17, 17),
}

# Letter glyphs, N through Z.
GLYPHS.update({
    "N": (17, 25, 21, 19, 17, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14),
    "P": (30, 17, 17, 30, 16, 16, 16),
    "Q": (14, 17, 17, 17, 21, 18, 13),
    "R": (30, 17, 17, 30, 20, 18, 17),
    "S": (15, 16, 16, 14, 1, 1, 30),
    "T": (31, 4, 4, 4, 4, 4, 4),
    "U": (17, 17, 17, 17, 17, 17, 14),
    "V": (17, 17, 17, 17, 17, 10, 4),
    "W": (17, 17, 17, 21, 21, 27, 17),
    "X": (17, 17, 10, 4, 10, 17, 17),
    "Y": (17, 17, 10, 4, 4, 4, 4),
    "Z": (31, 1, 2, 4, 8, 16, 31),
})

# Digits.
GLYPHS.update({
    "0": (14, 19, 21, 25, 17, 17, 14),
    "1": (4, 12, 4, 4, 4, 4, 14),
    "2": (14, 17, 1, 2, 4, 8, 31),
    "3": (30, 1, 1, 14, 1, 1, 30),
    "4": (2, 12, 10, 18, 31, 2, 2),
    "5": (31, 16, 30, 1, 1, 17, 14),
    "6": (14, 16, 16, 30, 17, 17, 14),
    "7": (31, 1, 2, 4, 4, 4, 4),
    "8": (14, 17, 17, 14, 17, 17, 14),
    "9": (14, 17, 17, 15, 1, 1, 14),
})

# Punctuation and marks used on the page.
GLYPHS.update({
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 12, 12),
    ",": (0, 0, 0, 0, 4, 4, 8),
    ":": (0, 12, 12, 0, 12, 12, 0),
    ";": (0, 12, 12, 0, 12, 4, 8),
    "!": (4, 4, 4, 4, 4, 0, 4),
    "?": (14, 17, 1, 2, 4, 0, 4),
    "-": (0, 0, 0, 31, 0, 0, 0),
    "/": (1, 1, 2, 4, 8, 16, 16),
    "(": (7, 4, 8, 8, 8, 4, 7),
    ")": (28, 4, 2, 2, 2, 4, 28),
    "%": (25, 26, 2, 4, 8, 22, 19),
    "$": (4, 15, 18, 14, 5, 30, 4),
    "&": (14, 17, 20, 8, 21, 18, 13),
    "+": (0, 4, 4, 14, 4, 4, 0),
    "=": (0, 0, 14, 0, 14, 0, 0),
    "'": (4, 4, 0, 0, 0, 0, 0),
    '"': (10, 10, 0, 0, 0, 0, 0),
    # Bullet: a small filled square in the middle rows.
    "•": (0, 0, 0, 12, 12, 0, 0),
})

BLANK = (0, 0, 0, 0, 0, 0, 0)


def glyph(ch):
    """Row masks for one character; unknown characters are blank."""
    return GLYPHS.get(ch, BLANK)


def text_width(text, scale, gap=1):
    """Pixel width of text at a scale, counting the gap between letters."""
    if not text:
        return 0
    return len(text) * (5 * scale + gap) - gap


def text_height(scale):
    """Pixel height of one line of text at a scale."""
    return 7 * scale
