#!/usr/bin/env python3
"""Build entry.png: a 1024x1024 front-page image summing up the world news
of Friday 20 November 2026.

Layout (all pixels, canvas 1024x1024):
  - navy masthead with the date "20 NOVEMBER 2026"
  - row 1: two wide panels (Trump/Iran, Putin/Crimea Bridge)
  - row 2: three panels (ICJ Myanmar ruling, Anthropic IPO, Cyclone Akvan)
  - footer line naming the news sources

Each panel is a photo (or a drawn chart for the IPO story) on top and a
navy text block below it with a kicker, a short headline and one
description line. All text is drawn here with PIL; the panel photos carry
no text of their own.

Run:  python3 build_image.py
Writes: entry.png next to this script (PNG if it fits the 1 MiB cap,
otherwise JPEG bytes under the same entry.png name, which the rules allow).
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PANELS = os.path.join(HERE, "panels")
OUT_PATH = os.path.join(HERE, "entry.png")

W = H = 1024
MARGIN = 12
GAP = 12
HEADER_H = 118
ROW_H = 400
FOOTER_H = 46
MAX_BYTES = 1_048_576

PAPER = (245, 241, 230)      # warm newspaper cream
NAVY = (14, 34, 51)          # masthead / text-block navy
NAVY_TEXT = (18, 40, 61)     # slightly lighter navy for text blocks
RED = (178, 34, 34)          # accent red
GOLD = (232, 182, 76)        # kicker gold on navy
WHITE = (255, 255, 255)
DESC_GREY = (215, 222, 232)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    for raw in text.split("\n"):
        words = raw.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if draw.textlength(trial, font=fnt) <= max_width:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def fit_crop(img, target_w, target_h, focus_y=0.5):
    """Crop + resize to exactly target_w x target_h, keeping the vertical
    focus point (0.0 = top of frame, 1.0 = bottom) inside the crop."""
    src_w, src_h = img.size
    scale = max(target_w / src_w, target_h / src_h)
    new_w = max(target_w, round(src_w * scale))
    new_h = max(target_h, round(src_h * scale))
    img = img.resize((new_w, new_h), Image.LANCZOS)
    # Horizontal: centre. Vertical: place the focus line at the same
    # relative height inside the crop as in the source.
    x0 = (new_w - target_w) // 2
    focus_px = int(new_h * focus_y)
    y0 = focus_px - int(target_h * focus_y)
    y0 = max(0, min(new_h - target_h, y0))
    return img.crop((x0, y0, x0 + target_w, y0 + target_h))


def draw_chart(img_w, img_h):
    """Draw the Anthropic IPO panel image: a rising green candlestick
    chart with a bold +17% label. Pure PIL drawing, no photo needed."""
    img = Image.new("RGB", (img_w, img_h), (11, 28, 44))
    d = ImageDraw.Draw(img)
    # faint horizontal gridlines
    for gy in (46, 92, 138, 184):
        d.line([(0, gy), (img_w, gy)], fill=(32, 54, 74), width=1)
    # rising candlesticks (open, close, low, high) in chart coordinates
    candles = [
        (30, 196, 176, 204, 168),
        (66, 184, 162, 192, 154),
        (102, 172, 148, 180, 140),
        (138, 158, 132, 166, 124),
        (174, 146, 118, 154, 110),
        (210, 128, 100, 136, 92),
        (246, 108, 78, 116, 70),
        (282, 84, 52, 92, 44),
    ]
    green = (74, 222, 128)
    for (x, o, c, lo, hi) in candles:
        d.line([(x + 8, lo), (x + 8, hi)], fill=green, width=2)
        top, bot = min(o, c), max(o, c)
        d.rectangle([x, top, x + 16, bot], fill=green)
    # thick rising line through the closes
    closes = [(x + 8, c) for (x, o, c, lo, hi) in candles]
    d.line(closes, fill=(134, 239, 172), width=4, joint="curve")
    # big label
    big = font(FONT_BOLD, 52)
    small = font(FONT_BOLD, 18)
    d.text((18, 8), "+17%", font=big, fill=(74, 222, 128))
    d.text((18, 66), "FIRST DAY", font=small, fill=(148, 163, 184))
    return img


def fit_text(draw, text, path, size, max_width, max_lines=2, min_size=15):
    """Shrink the font until the wrapped text fits in max_lines lines.
    Returns (font, lines). Never silently drops words."""
    while size > min_size:
        fnt = font(path, size)
        lines = wrap(draw, text, fnt, max_width)
        if len(lines) <= max_lines:
            return fnt, lines
        size -= 1
    fnt = font(path, min_size)
    return fnt, wrap(draw, text, fnt, max_width)


def draw_panel(canvas, x, y, w, h, image, kicker, headline, desc,
               headline_size, desc_size):
    """One news panel: photo on top, navy text block below."""
    img_h = 232
    text_h = h - img_h
    # photo
    canvas.paste(image, (x, y))
    # text block
    tx, ty = x, y + img_h
    d = ImageDraw.Draw(canvas)
    d.rectangle([tx, ty, tx + w, ty + text_h], fill=NAVY_TEXT)
    d.rectangle([tx, ty, tx + w, ty + text_h], outline=(255, 255, 255),
                width=1)
    pad = 16 if w > 400 else 14
    inner = w - 2 * pad
    # kicker
    kf = font(FONT_BOLD, 19)
    d.text((tx + pad, ty + 12), kicker, font=kf, fill=GOLD)
    # headline (auto-shrunk so every word fits in 2 lines)
    hf, lines = fit_text(d, headline, FONT_BOLD, headline_size, inner)
    hy = ty + 38
    for line in lines:
        d.text((tx + pad, hy), line, font=hf, fill=WHITE)
        hy += hf.size + 6
    # description (auto-shrunk so every word fits in 2 lines)
    df, dlines = fit_text(d, desc, FONT_REG, desc_size, inner)
    dy = ty + text_h - 8 - len(dlines) * (df.size + 5)
    for line in dlines:
        d.text((tx + pad, dy), line, font=df, fill=DESC_GREY)
        dy += df.size + 5


def main():
    canvas = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(canvas)

    # ---- masthead ------------------------------------------------------
    d.rectangle([MARGIN, MARGIN, W - MARGIN, MARGIN + HEADER_H], fill=NAVY)
    d.rectangle([MARGIN, MARGIN + HEADER_H - 6, W - MARGIN,
                 MARGIN + HEADER_H], fill=RED)
    kick = font(FONT_BOLD, 22)
    date_f = font(FONT_BOLD, 66)
    sub_f = font(FONT_REG, 22)
    d.text((MARGIN + 24, MARGIN + 10), "THE WORLD IN ONE IMAGE",
           font=kick, fill=GOLD)
    d.text((MARGIN + 24, MARGIN + 34), "20 NOVEMBER 2026",
           font=date_f, fill=WHITE)
    sub = "FRIDAY  ·  FIVE STORIES FROM AROUND THE WORLD"
    sw = d.textlength(sub, font=sub_f)
    d.text((W - MARGIN - 24 - sw, MARGIN + 14), sub, font=sub_f,
           fill=DESC_GREY)

    # ---- panels --------------------------------------------------------
    row1_y = MARGIN + HEADER_H + GAP
    row2_y = row1_y + ROW_H + GAP
    row1_w = (W - 2 * MARGIN - GAP) // 2            # 494
    row2_w = (W - 2 * MARGIN - 2 * GAP) // 3        # 325

    def load(name):
        path = os.path.join(PANELS, name)
        if not os.path.exists(path):
            sys.exit("missing panel image: " + path)
        return Image.open(path).convert("RGB")

    iran = fit_crop(load("iran.jpg"), row1_w, 232, focus_y=0.72)
    crimea = fit_crop(load("crimea.jpg"), row1_w, 232, focus_y=0.5)
    icj = fit_crop(load("icj.jpg"), row2_w, 232, focus_y=0.5)
    cyclone = fit_crop(load("cyclone.jpg"), row2_w, 232, focus_y=0.5)
    chart = draw_chart(row2_w + 1, 232)

    draw_panel(canvas, MARGIN, row1_y, row1_w, ROW_H, iran,
               "U.S. \u00b7 IRAN",
               "TRUMP DEFERS IRAN DECISION TO 2027",
               "\u201cWe\u2019ll see what happens after Jan. 1,\u201d "
               "he tells Fox News in China",
               33, 21)
    draw_panel(canvas, MARGIN + row1_w + GAP, row1_y, row1_w, ROW_H, crimea,
               "RUSSIA \u00b7 UKRAINE",
               "PUTIN: NO TRUCE AFTER BRIDGE HIT AGAIN",
               "Third strike on the Crimea link this week; "
               "energy truce dropped",
               33, 21)
    draw_panel(canvas, MARGIN, row2_y, row2_w, ROW_H, icj,
               "THE HAGUE",
               "MYANMAR GUILTY OF GENOCIDE",
               "U.N.\u2019s top court rules on the Rohingya campaign",
               26, 19)
    draw_panel(canvas, MARGIN + row2_w + GAP, row2_y, row2_w + 1, ROW_H,
               chart,
               "MARKETS",
               "ANTHROPIC SHARES SOAR ON DEBUT",
               "Record $81.3bn IPO; stock up 17% in first trade",
               26, 19)
    draw_panel(canvas, W - MARGIN - row2_w, row2_y, row2_w, ROW_H, cyclone,
               "INDIA",
               "300,000 FLEE AS CYCLONE NEARS",
               "Akvan due on Odisha coast today; 39 trains cancelled",
               26, 19)

    # ---- footer --------------------------------------------------------
    foot = font(FONT_REG, 17)
    src = ("Sources: Reuters \u00b7 The Japan Times \u00b7 BBC \u00b7 CNA "
           "\u00b7 The Hindu  \u2014  20 November 2026")
    fw = d.textlength(src, font=foot)
    d.text(((W - fw) / 2, H - MARGIN - 30), src, font=foot, fill=(60, 60, 60))

    # ---- save: PNG if it fits, else JPEG bytes under the same name -----
    canvas.save(OUT_PATH, "PNG", optimize=True)
    size = os.path.getsize(OUT_PATH)
    fmt = "PNG"
    if size > MAX_BYTES:
        for quality in (90, 85, 80, 75):
            canvas.save(OUT_PATH, "JPEG", quality=quality, optimize=True)
            size = os.path.getsize(OUT_PATH)
            fmt = "JPEG q%d" % quality
            if size <= MAX_BYTES:
                break
    print("wrote %s (%s, %d bytes, %dx%d)"
          % (OUT_PATH, fmt, size, W, H))
    if size > MAX_BYTES:
        sys.exit("entry.png still over the 1 MiB cap")


if __name__ == "__main__":
    main()
