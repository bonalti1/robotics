"""Spotlight pictures of the real Flop (VEX's render, supplied by Rolando) for the edit — never fed to a generator.

python3 source/real_flop.py  ->  refs/real/spot_<part>.png (1920x1080): the real robot, everything but one part dimmed,
a yellow ring around the part, a "THE REAL FLOP" tag and an image credit. Part positions are in the source image's pixels.
"""
import math
from PIL import Image, ImageDraw, ImageFont

SRC = "refs/real/flop_vex_render.png"
W, H = 1920, 1080
CREAM, NAVY, YEL = (255, 248, 236), (28, 35, 64), (245, 196, 0)
FONT = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FONT_SMALL = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
TOP, HEIGHT = 255, 805  # keep the top band free for the big captions

# (cx, cy, rx, ry, angle_deg) ellipses in source pixels
PARTS = {
    "wheels": [(118, 425, 82, 78, 0), (455, 675, 70, 90, 0), (527, 180, 68, 68, 0)],
    "intake": [(1035, 585, 175, 215, 0)],
    "arm": [(560, 220, 400, 95, 19)],
    "camera": [(838, 775, 92, 118, 0)],
}


def place():
    im = Image.open(SRC).convert("RGBA")
    s = HEIGHT / im.height
    im = im.resize((round(im.width * s), HEIGHT), Image.LANCZOS)
    x0 = (W - im.width) // 2
    return im, s, x0


def ellipse_mask(size, shapes, s, x0, grow=0):
    m = Image.new("L", size, 0)
    for cx, cy, rx, ry, ang in shapes:
        rx, ry = rx * s + grow, ry * s + grow
        e = Image.new("L", (round(2 * rx) + 4, round(2 * ry) + 4), 0)
        ImageDraw.Draw(e).ellipse([2, 2, 2 * rx + 2, 2 * ry + 2], fill=255)
        e = e.rotate(-ang, expand=True, resample=Image.BICUBIC)
        X, Y = x0 + cx * s, TOP + cy * s
        m.paste(255, (round(X - e.width / 2), round(Y - e.height / 2)), e)
    return m


def render(part, out):
    im, s, x0 = place()
    base = Image.new("RGBA", (W, H), CREAM + (255,))
    base.alpha_composite(im, (x0, TOP))
    if part != "full":
        shapes = PARTS[part]
        inner = ellipse_mask((W, H), shapes, s, x0)
        ring = ellipse_mask((W, H), shapes, s, x0, grow=12)
        dim = Image.new("RGBA", (W, H), CREAM + (175,))
        dim.putalpha(Image.eval(inner, lambda v: 0 if v > 128 else 175))
        base.alpha_composite(dim)
        outline = Image.new("RGBA", (W, H), NAVY + (255,))
        outline.putalpha(ellipse_mask((W, H), shapes, s, x0, grow=16))
        yellow = Image.new("RGBA", (W, H), YEL + (255,))
        yellow.putalpha(ring)
        hole = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        lay.alpha_composite(outline); lay.alpha_composite(yellow)
        # cut the inside back out so only the ring remains
        a = lay.getchannel("A")
        a = Image.composite(Image.new("L", (W, H), 0), a, ellipse_mask((W, H), shapes, s, x0, grow=2))
        lay.putalpha(a)
        base.alpha_composite(lay)
        del hole
    d = ImageDraw.Draw(base)
    f = ImageFont.truetype(FONT, 50)
    t = "THE REAL FLOP"
    tw = d.textlength(t, font=f)
    d.rounded_rectangle([48, H - 128, 48 + tw + 70, H - 40], radius=44, fill=YEL + (255,), outline=NAVY + (255,), width=6)
    d.text((48 + 35 + tw / 2, H - 84), t, font=f, fill=NAVY, anchor="mm")
    d.text((W - 24, H - 12), "Image: VEX Robotics", font=ImageFont.truetype(FONT_SMALL, 24), fill=(28, 35, 64, 150), anchor="rs")
    base.convert("RGB").save(out)


def center(part):
    """Where to zoom: the middle of the part's highlight, in 1920x1080 pixels."""
    im, s, x0 = place()
    xs = [x0 + p[0] * s for p in PARTS[part]]
    ys = [TOP + p[1] * s for p in PARTS[part]]
    return round(sum(xs) / len(xs)), round(sum(ys) / len(ys))


if __name__ == "__main__":
    for p in ["full"] + list(PARTS):
        render(p, f"refs/real/spot_{p}.png")
        if p != "full":
            print(p, "zoom center", center(p))
    print("wrote refs/real/spot_*.png")
