#!/usr/bin/env python3
"""Render the 'World News - 22 November 2026' one-image summary.

Deterministic: no network access, no randomness, no timestamps.
Running this file writes entry.png to /output/entry.png, falling back
to ./output/entry.png (next to this script) when /output is not writable.
"""

import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
BOLD = str(FONT_DIR / "DejaVuSans-Bold.ttf")
REG = str(FONT_DIR / "DejaVuSans.ttf")

BG = (247, 243, 234)
INK = (26, 30, 38)
MUTED = (88, 94, 106)
CARD = (255, 255, 255)
NAVY = (20, 33, 61)
GOLD = (242, 183, 49)

STORIES = [
    (
        "CLIMATE  |  ANTALYA, TURKIYE",
        (39, 122, 72),
        "COP31 Climate Talks Collapse Without a Deal",
        "The Antalya summit ended in record overtime as the EU and about "
        "130 parties rejected a draft omitting fossil fuels - the first "
        "COP failure since Copenhagen in 2009.",
    ),
    (
        "UKRAINE  |  DYMER, KYIV REGION",
        (38, 84, 160),
        "Drone Strike on Homes Leaves 14 Missing",
        "Part of a five-storey apartment block collapsed after a Sunday "
        "drone hit; nine people were evacuated and the fire contained, "
        "President Zelenskiy said.",
    ),
    (
        "POLAND  |  NATO AIRSPACE",
        (150, 44, 60),
        "Three Russian Missiles Flew Into Poland",
        "Prosecutors said debris showed the Kh-101 missiles were made "
        "this year in Dubna, Russia. NATO's council meets Monday on "
        "the airspace violation.",
    ),
    (
        "MEXICO  |  GUASAVE, SINALOA",
        (176, 92, 36),
        "Mexico Captures Cartel Boss 'El Chapo Isidro'",
        "Fausto Isidro Meza Flores, an FBI top-10 fugitive, was seized "
        "in Guasave; seven gunmen and four soldiers died in the "
        "overnight firefight.",
    ),
    (
        "CONGO  |  ITURI PROVINCE",
        (178, 52, 52),
        "Fighting Near Ebola Outbreak Disrupts Response",
        "Clashes near a hospital forced health workers to shelter in a "
        "maternity ward for over 24 hours, WHO chief Tedros said "
        "on Sunday.",
    ),
    (
        "LIBYA  |  BENGHAZI PORT",
        (104, 66, 160),
        "Suspected Drone Attack Hits Russian Ship",
        "An explosion aboard a docked Russian vessel injured people "
        "at the Benghazi naval base; the eastern government called "
        "it a violation of sovereignty.",
    ),
]


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_width):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def render_bytes() -> bytes:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # Header
    d.rectangle([0, 0, W, 128], fill=NAVY)
    d.rectangle([0, 128, W, 134], fill=GOLD)
    d.text((48, 26), "World News \u2014 22 November 2026", font=font(BOLD, 43), fill=(255, 255, 255))
    d.text((48, 82), "SUNDAY  \u00b7  SIX STORIES FROM AROUND THE WORLD",
           font=font(BOLD, 20), fill=(198, 210, 232))

    # Story cards
    top = 154
    card_h = 132
    gap = 10
    for i, (tag, color, headline, body) in enumerate(STORIES):
        y = top + i * (card_h + gap)
        d.rounded_rectangle([36, y, W - 36, y + card_h], radius=14, fill=CARD)
        d.rounded_rectangle([36, y, 48, y + card_h], radius=6, fill=color)
        x = 68
        d.text((x, y + 12), tag, font=font(BOLD, 17), fill=color)
        d.text((x, y + 34), headline, font=font(BOLD, 27), fill=INK)
        body_lines = wrap(d, body, font(REG, 19), W - 36 - x - 22)
        by = y + 72
        for line in body_lines[:2]:
            d.text((x, by), line, font=font(REG, 19), fill=MUTED)
            by += 25

    # Footer
    fy = top + len(STORIES) * (card_h + gap) + 2
    d.text((48, fy), "Sources: Reuters \u00b7 Al Jazeera \u00b7 AP via NCPR \u2014 all dated 22 Nov 2026",
           font=font(REG, 16), fill=MUTED)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def main() -> None:
    data = render_bytes()
    target = Path("/output/entry.png")
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    except OSError:
        target = Path(__file__).resolve().parent / "output" / "entry.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    print(f"wrote {target} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
