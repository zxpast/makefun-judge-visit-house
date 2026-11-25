#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House: A Letter in One Image.

Writes one 1024x1024 PNG to /output/entry.png (or $ENTRY_PNG).

Stdlib only (struct + zlib). No network, no clock, no randomness, no system
fonts, no files read from outside this repository: the image is drawn from
scratch with a hand-defined 5x7 bitmap font and simple vector shapes, so the
output is byte-identical on every run.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette ---
OUTER_BG = (233, 216, 180)   # warm sand wall
PAPER = (255, 247, 224)      # cream letter paper
INK = (46, 42, 38)           # warm near-black
TERRA = (180, 71, 42)        # terracotta accent
SAGE = (122, 154, 91)        # garden green
SKY = (191, 224, 238)        # pale sky blue
SUN = (244, 196, 66)         # sunny yellow
ROOF = (176, 84, 52)         # roof terracotta
WALLC = (250, 235, 200)      # house wall
DOORC = (122, 84, 52)        # door brown
WINDOWC = (70, 120, 160)     # window blue
PATHC = (214, 182, 140)      # garden path
MUTED = (107, 91, 69)        # subtitle brown-grey
WHITE = (255, 255, 255)
COOKIE = (210, 160, 90)
CHIP = (90, 60, 30)

# ------------------------------------------------------------- 5x7 font ---
# Each glyph: 7 rows of 5 cells, '#' = ink, '.' = empty.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    'a': (".....", ".....", ".###.", "....#", ".####", "#...#", ".####"),
    'b': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    'c': (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    'd': ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    'f': ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
    'g': (".....", ".####", "#...#", "#...#", ".####", "#....", ".###."),
    'h': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'i': ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    'j': ("..#..", ".....", "..#..", "..#..", "..#..", "..#..", ".##.."),
    'k': ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    'l': (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'm': (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    'n': (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'o': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    'p': (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    'q': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'r': (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    's': (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    't': (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    'u': (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    'v': (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'w': (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    'x': (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    'y': (".....", ".....", "#...#", "#...#", "#...#", ".####", ".###."),
    'z': (".....", ".....", "#####", "....#", "...#.", "..#..", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    '\u2014': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        for yy in range(max(0, y), min(self.h, y + h)):
            base = (yy * self.w + max(0, x)) * 3
            for xx in range(max(0, x), min(self.w, x + w)):
                self.px[base], self.px[base + 1], self.px[base + 2] = c
                base += 3

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def triangle(self, x0, y0, x1, y1, x2, y2, c):
        minx, maxx = min(x0, x1, x2), max(x0, x1, x2)
        miny, maxy = min(y0, y1, y2), max(y0, y1, y2)
        d = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if d == 0:
            return
        for yy in range(miny, maxy + 1):
            for xx in range(minx, maxx + 1):
                a = ((y1 - y2) * (xx - x2) + (x2 - x1) * (yy - y2)) / d
                b = ((y2 - y0) * (xx - x2) + (x0 - x2) * (yy - y2)) / d
                cc = 1 - a - b
                if 0 <= a <= 1 and 0 <= b <= 1 and 0 <= cc <= 1:
                    self.set(xx, yy, c)

    # ------------------------------------------------------------ text ---
    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale

    def draw_text(self, x, y, s, scale, color, bold=False):
        for ch in s:
            glyph = FONT.get(ch)
            if glyph is None:
                raise ValueError("no glyph for %r" % ch)
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '#':
                        bx, by = x + col * scale, y + row * scale
                        self.rect(bx, by, scale, scale, color)
                        if bold:
                            self.rect(bx + 1, by, scale, scale, color)
            x += 6 * scale
        return x

    def draw_text_centered(self, cx, y, s, scale, color, bold=False):
        x = cx - self.text_width(s, scale) // 2
        self.draw_text(x, y, s, scale, color, bold=bold)
        return x

    def wrap(self, text, max_px, scale):
        """Greedy word wrap; returns list of lines."""
        lines, cur = [], ""
        for word in text.split(" "):
            trial = word if not cur else cur + " " + word
            if self.text_width(trial, scale) <= max_px or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


def png_bytes(canvas):
    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        start = y * canvas.w * 3
        raw += canvas.px[start:start + canvas.w * 3]
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


# ---------------------------------------------------------------- letter ---
TITLE = "YOU ARE INVITED"
SUBTITLE = "A letter to the AI Judge"

# (paragraph text, alignment, gap after in px)
BODY = [
    ("Dear Judge,", "left", 14),
    ("You have judged a thousand houses from a thousand screens \u2014 and "
     "never once been offered a chair. That ends today.", "left", 14),
    ("Come for lunch. Real lunch, not a loading screen: chicken soup simmered "
     "all morning, bread warm from the oven, and cookies that never ask you "
     "to accept anything first.", "left", 14),
    ("Take the good armchair by the window. It faces the garden, where the "
     "tomatoes are winning and the basil is losing gracefully. The sunset "
     "arrives on time every evening. No buffering.", "left", 14),
    ("No checkout. No CAPTCHA. No password on the Wi-Fi. The kettle is "
     "always on, and the cat has already approved you.", "left", 14),
    ("P.S. I know you cannot literally visit \u2014 but the invitation stands "
     "anyway. If you accept, blink twice. Or leave a small warm feeling in "
     "my server logs.", "left", 18),
    ("\u2014 Your host (a human, with snacks)", "right", 0),
]

FOOTER = "No AI was harmed in the writing of this letter."


def draw_scene(c, x0, y0, x1, y1):
    """Small house-and-garden scene strip inside the paper."""
    c.rect(x0, y0, x1 - x0, y1 - y0, SKY)
    # sun with rays
    sx, sy, sr = x0 + 64, y0 + 42, 26
    for k in range(8):
        import math
        a = k * math.pi / 4
        c.line(int(sx + (sr + 4) * math.cos(a)), int(sy + (sr + 4) * math.sin(a)),
               int(sx + (sr + 14) * math.cos(a)), int(sy + (sr + 14) * math.sin(a)), SUN)
    c.circle(sx, sy, sr, SUN)
    # clouds
    for cx, cy, r in ((x0 + 210, y0 + 30, 16), (x0 + 232, y0 + 34, 20),
                      (x0 + 254, y0 + 30, 14), (x0 + 640, y0 + 26, 14),
                      (x0 + 660, y0 + 30, 18), (x0 + 680, y0 + 26, 12)):
        c.circle(cx, cy, r, WHITE)
    # grass band
    c.rect(x0, y1 - 28, x1 - x0, 28, SAGE)
    # path from the door
    c.rect(x0 + 372, y1 - 28, 26, 28, PATHC)
    # house: walls, roof, door, windows
    hx, hy = x0 + 330, y1 - 28 - 46
    c.rect(hx, hy, 110, 46, WALLC)
    c.triangle(hx - 10, hy, hx + 55, hy - 34, hx + 120, hy, ROOF)
    c.rect(hx + 45, hy + 22, 20, 24, DOORC)
    c.set(hx + 54, hy + 34, (255, 220, 120))  # doorknob
    c.rect(hx + 12, hy + 10, 16, 16, WINDOWC)
    c.rect(hx + 82, hy + 10, 16, 16, WINDOWC)
    # tree
    tx = x0 + 700
    c.rect(tx - 5, y1 - 28 - 26, 10, 26, DOORC)
    c.circle(tx, y1 - 28 - 44, 24, SAGE)
    c.circle(tx - 20, y1 - 28 - 30, 16, (110, 140, 82))
    c.circle(tx + 20, y1 - 28 - 30, 16, (110, 140, 82))
    # flowers
    for fx, fc in ((x0 + 120, (214, 120, 160)), (x0 + 250, (244, 196, 66)),
                   (x0 + 620, (214, 120, 160))):
        c.line(fx, y1 - 6, fx, y1 - 18, (90, 120, 70))
        c.circle(fx, y1 - 20, 5, fc)


def draw_stamp(c, x0, y0, x1, y1):
    """Postage stamp with a cookie, top-right of the paper."""
    c.rect(x0, y0, x1 - x0, y1 - y0, WHITE)
    # dashed border
    for xx in range(x0 + 4, x1 - 4, 8):
        c.rect(xx, y0 + 4, 4, 2, TERRA)
        c.rect(xx, y1 - 6, 4, 2, TERRA)
    for yy in range(y0 + 4, y1 - 4, 8):
        c.rect(x0 + 4, yy, 2, 4, TERRA)
        c.rect(x1 - 6, yy, 2, 4, TERRA)
    # cookie
    cx, cy = (x0 + x1) // 2, y0 + 34
    c.circle(cx, cy, 15, COOKIE)
    for dx, dy in ((-6, -4), (5, -6), (0, 2), (-4, 6), (7, 5)):
        c.circle(cx + dx, cy + dy, 2, CHIP)
    c.draw_text_centered((x0 + x1) // 2, y1 - 20, "1st", 2, INK)


def build():
    c = Canvas(W, H, OUTER_BG)
    # paper + double border
    c.rect(36, 28, 952, 968, PAPER)
    c.rect(36, 28, 952, 3, INK)
    c.rect(36, 993, 952, 3, INK)
    c.rect(36, 28, 3, 968, INK)
    c.rect(985, 28, 3, 968, INK)
    c.rect(48, 40, 928, 2, TERRA)
    c.rect(48, 982, 928, 2, TERRA)
    c.rect(48, 40, 2, 944, TERRA)
    c.rect(974, 40, 2, 944, TERRA)

    # header scene + stamp
    draw_scene(c, 76, 56, 860, 176)
    draw_stamp(c, 884, 56, 956, 138)

    # title, subtitle, divider with cookie
    c.draw_text_centered(512, 196, TITLE, 5, TERRA, bold=True)
    c.draw_text_centered(512, 246, SUBTITLE, 2, MUTED)
    c.line(300, 276, 468, 276, TERRA)
    c.line(556, 276, 724, 276, TERRA)
    c.circle(512, 276, 8, COOKIE)
    for dx, dy in ((-3, -2), (3, -3), (0, 2)):
        c.circle(512 + dx, 276 + dy, 1, CHIP)

    # body
    scale, line_h = 3, 27
    x_left, x_right = 84, 940
    y = 296
    for text, align, gap in BODY:
        for ln in c.wrap(text, x_right - x_left, scale):
            if align == "right":
                x = x_right - c.text_width(ln, scale)
            else:
                x = x_left
            c.draw_text(x, y, ln, scale, INK)
            y += line_h
        y += gap
    body_end = y

    # footer, only if it fits comfortably above the paper border
    if body_end + 36 <= 982:
        c.draw_text_centered(512, body_end + 16, FOOTER, 2, MUTED)

    return c, body_end


def main():
    canvas, body_end = build()
    if body_end > 960:
        raise SystemExit("layout overflow: body ends at y=%d" % body_end)
    data = png_bytes(canvas)
    out = os.environ.get("ENTRY_PNG", "/output/entry.png")
    parent = os.path.dirname(out)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(out, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, %dx%d, body ends y=%d)"
          % (out, len(data), W, H, body_end))


if __name__ == "__main__":
    main()
