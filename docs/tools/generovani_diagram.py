#!/usr/bin/env python3
# Regenerate docs/pictures/generovani.png with English labels,
# matching the geometry and colors of the original Czech diagram.
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/google-noto-vf/NotoSans[wght].ttf"

ORIG_W, ORIG_H = 975, 361
S = 2  # supersampling
W, H = ORIG_W * S, ORIG_H * S

YELLOW_TOP = (255, 251, 204)
YELLOW_BOT = (255, 249, 174)
BLUE_TOP = (114, 159, 207)
BLUE_BOT = (173, 197, 231)
ORANGE = (255, 218, 162)
BORDER = (52, 101, 164)
BLACK = (0, 0, 0)

im = Image.new("RGB", (W, H), (255, 255, 255))
d = ImageDraw.Draw(im)

f21 = ImageFont.truetype(FONT, 21 * S)
f12 = ImageFont.truetype(FONT, 12 * S)

def box(x0, y0, x1, y1, fill, radius=0):
    x0, y0, x1, y1 = x0 * S, y0 * S, x1 * S, y1 * S
    if radius:
        d.rounded_rectangle([x0, y0, x1, y1], radius=radius * S, fill=fill, outline=BORDER, width=2)
    else:
        d.rectangle([x0, y0, x1, y1], fill=fill, outline=BORDER, width=2)

def center_text(cx, cy, text, font, fill=BLACK):
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = cx * S - tw / 2 - bbox[0]
    y = cy * S - th / 2 - bbox[1]
    d.text((x, y), text, font=font, fill=fill)

def arrow(x0, y0, x1, y1, head=12, halfw=5):
    x0, y0, x1, y1 = x0 * S, y0 * S, x1 * S, y1 * S
    head, halfw = head * S, halfw * S
    import math
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    # shaft up to the base of the head
    bx, by = x1 - ux * head, y1 - uy * head
    d.line([x0, y0, bx, by], fill=BLACK, width=2)
    # triangular head
    px, py = -uy, ux
    d.polygon([(x1, y1), (bx + px * halfw, by + py * halfw), (bx - px * halfw, by - py * halfw)], fill=BLACK)

# ---- boxes ----
box(36, 13, 276, 119, YELLOW_TOP)                    # Grammar description
box(334, 13, 651, 109, BLUE_TOP, radius=20)          # Generator ...
box(46, 234, 286, 340, YELLOW_BOT)                   # Source text
box(343, 234, 651, 340, BLUE_BOT, radius=20)         # Generated syntactic analyzer
# parallelogram (Syntactic tree)
d.polygon([(786 * S, 234 * S), (956 * S, 234 * S), (917 * S, 340 * S), (747 * S, 340 * S)],
          fill=ORANGE, outline=BORDER, width=2)

# ---- arrows ----
arrow(278, 66, 330, 66)      # grammar description -> generator
arrow(494, 111, 494, 230)    # generator -> generated analyzer (vertical)
arrow(288, 273, 339, 273)    # source text -> generated analyzer
arrow(653, 273, 766, 273)    # generated analyzer -> syntactic tree

# ---- labels ----
center_text(156, 66, "Grammar description", f21)

center_text(492, 44, "Generator", f21)
center_text(492, 76, "of syntactic analyzers", f21)

center_text(166, 262, "Source text", f21)
center_text(166, 291, "(in the language of the given grammar)", f12)

center_text(497, 259, "Generated", f21)
center_text(497, 288, "syntactic analyzer", f21)

center_text(846, 268, "Syntactic", f21)
center_text(846, 296, "tree", f21)

im = im.resize((ORIG_W, ORIG_H), Image.LANCZOS)
im.save("/abc/grm/docs/pictures/generovani_en.png")
print("saved")
