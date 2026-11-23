#!/usr/bin/env python3
"""World news of Sunday, 22 November 2026, summed up in one image.

A self-contained renderer: standard library only, no network, no
third-party packages.  Running it draws a single 1024x1024 PNG
infographic covering the day's six major stories and writes it to
/output/entry.png (falling back to ./entry.png when /output cannot be
written).  The output is deterministic: repeated runs produce
byte-identical files.

    python3 main.py
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

# ---------------------------------------------------------------------------
# 5x7 bitmap font.  Each glyph is seven rows of five pixels, '#' = on.
# Only the characters used by the texts below are defined; anything
# else renders as a blank.
# ---------------------------------------------------------------------------

FONT = {
    "A": ".###./#...#/#...#/#####/#...#/#...#/#...#",
    "B": "####./#...#/#...#/####./#...#/#...#/####.",
    "C": ".####/#..../#..../#..../#..../#..../.####",
    "D": "####./#...#/#...#/#...#/#...#/#...#/####.",
    "E": "#####/#..../#..../####./#..../#..../#####",
    "F": "#####/#..../#..../####./#..../#..../#....",
    "G": ".####/#..../#..../#.###/#...#/#...#/.###.",
    "H": "#...#/#...#/#...#/#####/#...#/#...#/#...#",
    "I": "#####/..#../..#../..#../..#../..#../#####",
    "J": "..###/...#./...#./...#./...#./#..#./.##..",
    "K": "#...#/#..#./#.#../##.../#.#../#..#./#...#",
    "L": "#..../#..../#..../#..../#..../#..../#####",
    "M": "#...#/##.##/#.#.#/#.#.#/#...#/#...#/#...#",
    "N": "#...#/##..#/##..#/#.#.#/#..##/#..##/#...#",
    "O": ".###./#...#/#...#/#...#/#...#/#...#/.###.",
    "P": "####./#...#/#...#/####./#..../#..../#....",
    "Q": ".###./#...#/#...#/#...#/#.#.#/#..#./.##.#",
    "R": "####./#...#/#...#/####./#.#../#..#./#...#",
    "S": ".####/#..../#..../.###./....#/....#/####.",
    "T": "#####/..#../..#../..#../..#../..#../..#..",
    "U": "#...#/#...#/#...#/#...#/#...#/#...#/.###.",
    "V": "#...#/#...#/#...#/#...#/#...#/.#.#./..#..",
    "W": "#...#/#...#/#...#/#.#.#/#.#.#/##.##/#...#",
    "X": "#...#/.#.#./..#../..#../.#.#./#...#/#...#",
    "Y": "#...#/#...#/.#.#./..#../..#../..#../..#..",
    "Z": "#####/....#/...#./..#../.#.../#..../#####",
}

FONT.update({
    "0": ".###./#...#/#..##/#.#.#/##..#/#...#/.###.",
    "1": "..#../.##../..#../..#../..#../..#../#####",
    "2": ".###./#...#/....#/...#./..#../.#.../#####",
    "3": "####./....#/....#/.###./....#/....#/####.",
    "4": "...#./..##./.#.#./#..#./#####/...#./...#.",
    "5": "#####/#..../####./....#/....#/#...#/.###.",
    "6": ".###./#..../#..../####./#...#/#...#/.###.",
    "7": "#####/....#/...#./..#../.#.../.#.../.#...",
    "8": ".###./#...#/#...#/.###./#...#/#...#/.###.",
    "9": ".###./#...#/#...#/.####/....#/....#/.###.",
    " ": "...../...../...../...../...../...../.....",
    ".": "...../...../...../...../...../.##../.##..",
    ",": "...../...../...../...../...../.##../.#...",
    "'": "..#../..#../.#.../...../...../...../.....",
    "-": "...../...../...../#####/...../...../.....",
    ":": "...../.##../.##../...../.##../.##../.....",
    "/": "....#/....#/..#../..#../.#.../#..../#....",
    "(": "...##/..#../.#.../.#.../.#.../..#../...##",
    ")": "##.../..#../...#/..#../...#/..#../##...",
    "!": "..#../..#../..#../..#../..#../...../..#..",
    "?": ".###./#...#/....#/..#../..#../...../..#..",
    "&": ".##../#..#./#.#../.#.../#.#.#/#..#./.##.#",
    "+": "...../..#../..#../#####/..#../..#../.....",
})


def glyph_rows(ch):
    """Return the seven bitmap rows for one character."""
    return FONT.get(ch.upper(), FONT[" "]).split("/")


# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------

BG = (10, 15, 28)
PANEL = (22, 31, 52)
PANEL_EDGE = (52, 68, 100)
WHITE = (238, 242, 248)
BODY = (196, 206, 222)
MUTED = (140, 154, 178)
ACCENT = (226, 54, 64)
SILVER = (178, 190, 208)


# ---------------------------------------------------------------------------
# Canvas: an RGB framebuffer plus small drawing primitives.
# ---------------------------------------------------------------------------

class Canvas:
    def __init__(self, width, height, colour):
        self.w = width
        self.h = height
        self.buf = bytearray(bytes(colour) * (width * height))

    def px(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(colour)

    def rect(self, x, y, w, h, colour):
        for yy in range(y, y + h):
            if 0 <= yy < self.h:
                start = max(0, x)
                end = min(self.w, x + w)
                if start < end:
                    i = (yy * self.w + start) * 3
                    self.buf[i:i + (end - start) * 3] = \
                        bytes(colour) * (end - start)

    def rect_outline(self, x, y, w, h, colour, width=1):
        self.rect(x, y, w, width, colour)
        self.rect(x, y + h - width, w, width, colour)
        self.rect(x, y, width, h, colour)
        self.rect(x + w - width, y, width, h, colour)

    def disc(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.px(xx, yy, colour)

    def line(self, x0, y0, x1, y1, colour, width=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        brush = max(0, width // 2)
        while True:
            if brush:
                self.disc(x0, y0, brush, colour)
            else:
                self.px(x0, y0, colour)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def dashed_line(self, x0, y0, x1, y1, colour, width=1, dash=8, gap=6):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            if (i % (dash + gap)) < dash:
                x = x0 + (x1 - x0) * i // steps
                y = y0 + (y1 - y0) * i // steps
                if width > 1:
                    self.disc(x, y, width // 2, colour)
                else:
                    self.px(x, y, colour)

    def circle(self, cx, cy, r, colour, width=1):
        # Midpoint circle; width stamps a small disc at each point.
        x, y, err = r, 0, 0
        while x >= y:
            for px_, py_ in ((cx + x, cy + y), (cx + y, cy + x),
                             (cx - y, cy + x), (cx - x, cy + y),
                             (cx - x, cy - y), (cx - y, cy - x),
                             (cx + y, cy - x), (cx + x, cy - y)):
                if width > 1:
                    self.disc(px_, py_, width // 2, colour)
                else:
                    self.px(px_, py_, colour)
            y += 1
            err += 1 + 2 * y
            if 2 * (err - x) + 1 > 0:
                x -= 1
                err += 1 - 2 * x

    def ellipse(self, cx, cy, rx, ry, colour, width=1):
        # Parametric outline; dense enough for the small motifs here.
        steps = max(rx, ry) * 8
        import math
        for i in range(steps + 1):
            t = 2.0 * math.pi * i / steps
            x = int(round(cx + rx * math.cos(t)))
            y = int(round(cy + ry * math.sin(t)))
            if width > 1:
                self.disc(x, y, width // 2, colour)
            else:
                self.px(x, y, colour)

    def poly(self, points, colour):
        for i in range(len(points) - 1):
            self.line(points[i][0], points[i][1],
                      points[i + 1][0], points[i + 1][1], colour, 3)

    def fill_poly(self, points, colour):
        ys = [p[1] for p in points]
        for yy in range(min(ys), max(ys) + 1):
            nodes = []
            j = len(points) - 1
            for i in range(len(points)):
                xi, yi = points[i]
                xj, yj = points[j]
                if (yi < yy and yj >= yy) or (yj < yy and yi >= yy):
                    nodes.append(int(xi + (yy - yi) * (xj - xi) /
                                     (yj - yi)))
                j = i
            nodes.sort()
            for k in range(0, len(nodes) - 1, 2):
                self.rect(nodes[k], yy, nodes[k + 1] - nodes[k] + 1,
                          1, colour)

    # -- text ------------------------------------------------------------

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale if s else 0

    def text(self, x, y, s, scale, colour):
        cx = x
        for ch in s.upper():
            rows = glyph_rows(ch)
            for ry, row in enumerate(rows):
                for rx, cell in enumerate(row):
                    if cell == "#":
                        self.rect(cx + rx * scale, y + ry * scale,
                                  scale, scale, colour)
            cx += 6 * scale
        return cx - scale

    def wrap(self, s, scale, max_width):
        words = s.split()
        lines = []
        cur = ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if self.text_width(trial, scale) <= max_width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


# ---------------------------------------------------------------------------
# Motifs: one small geometric emblem per story, drawn in a 96x96 box
# whose top-left corner is (x, y).
# ---------------------------------------------------------------------------

def motif_globe(c, x, y, colour):
    cx, cy, r = x + 48, y + 48, 38
    c.circle(cx, cy, r, colour, 3)
    c.ellipse(cx, cy, 17, r, colour, 2)
    c.ellipse(cx, cy, r, 15, colour, 2)
    crack = [(cx + 4, cy - r), (cx - 6, cy - 18), (cx + 7, cy - 2),
             (cx - 5, cy + 16), (cx + 3, cy + r)]
    c.poly(crack, ACCENT)


def motif_house_drone(c, x, y, colour):
    # A small drone hovering over a house.
    dx, dy = x + 48, y + 16
    c.rect(dx - 10, dy - 4, 20, 9, colour)
    for ox, oy in ((-24, -10), (24, -10), (-24, 10), (24, 10)):
        c.line(dx, dy, dx + ox, dy + oy, colour, 2)
        c.circle(dx + ox, dy + oy, 6, colour, 2)
    c.disc(dx, dy + 12, 3, ACCENT)
    # House outline with a roof and a door.
    hx, hy = x + 22, y + 52
    c.rect_outline(hx, hy, 52, 32, colour, 3)
    c.line(hx - 6, hy, x + 48, hy - 20, colour, 3)
    c.line(x + 48, hy - 20, hx + 58, hy, colour, 3)
    c.rect(x + 43, y + 66, 10, 18, colour)


def motif_missile(c, x, y, colour):
    # A missile crossing a dashed border line.
    c.dashed_line(x + 74, y + 4, x + 74, y + 92, ACCENT, 2)
    tip = (x + 66, y + 14)
    tail = (x + 26, y + 58)
    c.line(tail[0], tail[1], tip[0], tip[1], colour, 9)
    c.disc(tip[0], tip[1], 5, colour)
    c.line(tail[0], tail[1], tail[0] - 12, tail[1] + 2, colour, 5)
    c.line(tail[0], tail[1], tail[0] - 2, tail[1] + 12, colour, 5)
    c.line(tail[0] - 6, tail[1] + 8, tail[0] - 16, tail[1] + 18,
           ACCENT, 3)
    c.line(tail[0] - 2, tail[1] + 12, tail[0] - 10, tail[1] + 24,
           ACCENT, 3)


def motif_handcuffs(c, x, y, colour):
    c.circle(x + 32, y + 56, 17, colour, 4)
    c.circle(x + 66, y + 56, 17, colour, 4)
    c.rect(x + 44, y + 30, 10, 8, colour)
    c.line(x + 49, y + 38, x + 49, y + 44, colour, 3)
    c.disc(x + 32, y + 40, 3, colour)
    c.disc(x + 66, y + 40, 3, colour)
    # A small star badge above.
    cx, cy = x + 49, y + 14
    star = [(cx, cy - 8), (cx + 2, cy - 2), (cx + 8, cy - 2),
            (cx + 3, cy + 2), (cx + 5, cy + 8), (cx, cy + 4),
            (cx - 5, cy + 8), (cx - 3, cy + 2), (cx - 8, cy - 2),
            (cx - 2, cy - 2), (cx, cy - 8)]
    c.fill_poly(star, (240, 180, 60))


def motif_medical(c, x, y, colour):
    cx, cy = x + 48, y + 48
    c.disc(cx, cy, 38, WHITE)
    c.circle(cx, cy, 38, colour, 3)
    c.rect(cx - 7, cy - 24, 14, 48, ACCENT)
    c.rect(cx - 24, cy - 7, 48, 14, ACCENT)


def motif_ship(c, x, y, colour):
    # Hull, mast and cabin.
    hull = [(x + 8, y + 58), (x + 88, y + 58), (x + 76, y + 76),
            (x + 20, y + 76)]
    c.fill_poly(hull, colour)
    c.rect(x + 56, y + 44, 18, 14, colour)
    c.line(x + 34, y + 58, x + 34, y + 30, colour, 3)
    c.line(x + 34, y + 30, x + 52, y + 44, colour, 2)
    # A drone above the ship.
    dx, dy = x + 24, y + 14
    c.rect(dx - 7, dy - 3, 14, 6, ACCENT)
    for ox in (-15, 15):
        c.circle(dx + ox, dy - 5, 5, ACCENT, 2)
        c.line(dx, dy, dx + ox, dy - 5, ACCENT, 2)
    # Waves.
    import math
    for row, wy in enumerate((84, 92)):
        for i in range(80):
            xx = x + 8 + i
            yy = y + wy + int(2.5 * math.sin(i / 6.0 + row * 1.7))
            c.px(xx, yy, (86, 150, 210))
            c.px(xx, yy + 1, (86, 150, 210))


# ---------------------------------------------------------------------------
# The six stories of 22 November 2026 (see SOURCES.md for full citations).
# ---------------------------------------------------------------------------

STORIES = [
    {
        "tag": "CLIMATE - ANTALYA, TURKIYE",
        "colour": (45, 180, 160),
        "motif": motif_globe,
        "headline": "COP31 TALKS COLLAPSE WITHOUT A DEAL",
        "detail": "EU and others reject a final draft with no mention of "
                  "fossil fuels, after 44 hours of overtime. First COP "
                  "failure since 2009.",
        "source": "SOURCES: AL JAZEERA / REUTERS",
    },
    {
        "tag": "UKRAINE - DYMER, KYIV REGION",
        "colour": (240, 180, 60),
        "motif": motif_house_drone,
        "headline": "DRONE STRIKE ON HOMES LEAVES 14 MISSING",
        "detail": "A Russian drone hits a five-storey home on Sunday "
                  "morning. Nine people evacuated, the fire contained, "
                  "14 feared trapped.",
        "source": "SOURCE: REUTERS",
    },
    {
        "tag": "POLAND - NATO AIRSPACE",
        "colour": (226, 84, 84),
        "motif": motif_missile,
        "headline": "THREE RUSSIAN MISSILES FLEW INTO POLAND",
        "detail": "Prosecutors say all three objects were Kh-101 "
                  "missiles. NATO's council meets in Brussels on "
                  "Monday.",
        "source": "SOURCE: REUTERS",
    },
    {
        "tag": "MEXICO - GUASAVE, SINALOA",
        "colour": (240, 130, 50),
        "motif": motif_handcuffs,
        "headline": "CARTEL BOSS 'EL CHAPO ISIDRO' CAPTURED",
        "detail": "The FBI top-10 fugitive is seized and flown to "
                  "Mexico City. Eleven die in the overnight firefight.",
        "source": "SOURCES: AP / AL JAZEERA",
    },
    {
        "tag": "CONGO - ITURI PROVINCE",
        "colour": (90, 190, 90),
        "motif": motif_medical,
        "headline": "FIGHTING DISRUPTS EBOLA RESPONSE",
        "detail": "Health workers shelter over 24 hours near a "
                  "hospital. The outbreak passes 11,000 infections "
                  "and 5,500 dead.",
        "source": "SOURCE: REUTERS",
    },
    {
        "tag": "LIBYA - BENGHAZI PORT",
        "colour": (86, 150, 210),
        "motif": motif_ship,
        "headline": "DRONE ATTACK SUSPECTED ON RUSSIAN SHIP",
        "detail": "An explosion hits a Russian ship docked to refuel "
                  "at Benghazi. Injuries reported, no deaths, no "
                  "claim made.",
        "source": "SOURCE: REUTERS",
    },
]


def draw_panel(c, x, y, w, h, story):
    c.rect(x, y, w, h, PANEL)
    c.rect_outline(x, y, w, h, PANEL_EDGE, 2)
    pad = 18
    colour = story["colour"]
    # Category label with a colour bullet.
    c.rect(x + pad, y + 16, 12, 12, colour)
    c.text(x + pad + 20, y + 15, story["tag"], 2, colour)
    # Motif at the top-right.
    story["motif"](c, x + w - pad - 96, y + 40, colour)
    # Headline, kept clear of the motif box.
    hy = y + 48
    for line in c.wrap(story["headline"], 3, w - 2 * pad - 108):
        c.text(x + pad, hy, line, 3, WHITE)
        hy += 27
    # Detail text across the full panel width.
    dy = y + 148
    for line in c.wrap(story["detail"], 2, w - 2 * pad):
        c.text(x + pad, dy, line, 2, BODY)
        dy += 19
    # Source line at the bottom.
    c.text(x + pad, y + h - 36, story["source"], 2, MUTED)


def compose():
    c = Canvas(WIDTH, HEIGHT, BG)
    margin = 24
    # Header.
    c.text(margin, 30, "WORLD NEWS", 6, WHITE)
    date = "22 NOV 2026"
    c.text(WIDTH - margin - c.text_width(date, 3), 44, date, 3, ACCENT)
    sub = "SIX STORIES THAT SHAPED SUNDAY - IN ONE IMAGE"
    c.text(margin, 88, sub, 2, MUTED)
    c.rect(margin, 122, WIDTH - 2 * margin, 4, ACCENT)
    # Panels: two columns, three rows.
    top = 142
    bottom = 968
    gap_x, gap_y = 16, 14
    pw = (WIDTH - 2 * margin - gap_x) // 2
    ph = (bottom - top - 2 * gap_y) // 3
    for i, story in enumerate(STORIES):
        px = margin + (i % 2) * (pw + gap_x)
        py = top + (i // 2) * (ph + gap_y)
        draw_panel(c, px, py, pw, ph, story)
    # Footer.
    c.rect(margin, 978, WIDTH - 2 * margin, 2, PANEL_EDGE)
    foot = "SOURCES: AL JAZEERA / REUTERS / AP - 22 NOVEMBER 2026"
    c.text((WIDTH - c.text_width(foot, 2)) // 2, 990, foot, 2, MUTED)
    return c


# ---------------------------------------------------------------------------
# PNG encoding (filter 0 scanlines, zlib level 9: deterministic).
# ---------------------------------------------------------------------------

def png_bytes(canvas):
    raw = bytearray()
    stride = canvas.w * 3
    for yy in range(canvas.h):
        raw.append(0)
        raw += canvas.buf[yy * stride:(yy + 1) * stride]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    data = png_bytes(compose())
    try:
        os.makedirs("/output", exist_ok=True)
        path = "/output/entry.png"
        with open(path, "wb") as fh:
            fh.write(data)
    except OSError:
        path = "./entry.png"
        with open(path, "wb") as fh:
            fh.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
