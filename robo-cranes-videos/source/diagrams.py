"""Edit-time teaching diagrams in the flat Robo Cranes style (not fed to any generator).

python3 source/diagrams.py   ->  refs/diagrams/drift_path.png, refs/diagrams/compass_heading.png
"""
import math, os
from PIL import Image, ImageDraw, ImageFont

S = 2  # draw at 2x, then downsample for smooth edges
W, H = 1920 * S, 1080 * S
NAVY, CREAM, Y, R, B, G, CY, TILE = "#1c2340", "#fff8ec", "#f5c400", "#e5484d", "#3e7bfa", "#22a06b", "#5ef0ff", "#e9ecf3"
FONT = "/usr/share/fonts/opentype/inter/Inter-Black.otf"


def flop_topdown(d, cx, cy, ang, s=1.0):
    """Top-down Flop: white body, navy outline, eye panel at the front (direction ang, degrees, screen coords)."""
    a = math.radians(ang)
    fx, fy, lx, ly = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    def pt(f, l):
        return (cx + (f * fx + l * lx) * s * S, cy + (f * fy + l * ly) * s * S)
    body = [pt(-60, -46), pt(60, -46), pt(60, 46), pt(-60, 46)]
    d.polygon(body, fill="white", outline=NAVY, width=8 * S)
    for l in (-20, 20):
        x, y = pt(38, l)
        r = 10 * s * S
        d.ellipse([x - r, y - r, x + r, y + r], fill=CY, outline=NAVY, width=3 * S)
    x, y = pt(74, 0)  # bumper
    r = 12 * s * S
    d.ellipse([x - r, y - r, x + r, y + r], fill=R, outline=NAVY, width=4 * S)


def field(d):
    d.rounded_rectangle([360 * S, 70 * S, 1560 * S, 1010 * S], radius=24 * S, fill=NAVY)
    for i in range(6):
        for j in range(5):
            x, y = (382 + i * 193.5) * S, (92 + j * 180) * S
            d.rectangle([x, y, x + 189 * S, y + 176 * S], fill=TILE)


def dashed(d, p, q, color, width, dash=28, gap=20):
    (x1, y1), (x2, y2) = p, q
    L = math.hypot(x2 - x1, y2 - y1)
    n = int(L // ((dash + gap) * S)) + 1
    for k in range(n):
        a = k * (dash + gap) * S / L
        b = min(1, a + dash * S / L)
        d.line([(x1 + (x2 - x1) * a, y1 + (y2 - y1) * a), (x1 + (x2 - x1) * b, y1 + (y2 - y1) * b)], fill=color, width=width)


def drift_path(out):
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    field(d)
    side, err = 480, 8  # each 90-degree turn is 8 degrees too far
    start = (720 * S, 800 * S)
    # the plan: a perfect square (dashed)
    sq = [start]
    for k in range(4):
        h = math.radians(-90 * k)
        x, y = sq[-1]
        sq.append((x + side * S * math.cos(h), y + side * S * math.sin(h)))
    for p, q in zip(sq, sq[1:]):
        dashed(d, p, q, "#8a93b8", 10 * S)
    # what really happens: the small errors add up (solid red)
    pts, h = [start], 0.0
    for k in range(4):
        x, y = pts[-1]
        pts.append((x + side * S * math.cos(math.radians(h)), y + side * S * math.sin(math.radians(h))))
        h -= 90 + err
    d.line(pts, fill=R, width=16 * S, joint="curve")
    r = 26 * S  # start marker
    d.ellipse([start[0] - r, start[1] - r, start[0] + r, start[1] + r], fill=G, outline=NAVY, width=6 * S)
    ex, ey = pts[-1]
    last_h = -(90 + err) * 3
    flop_topdown(d, ex, ey, last_h, 1.1)
    f = ImageFont.truetype(FONT, 120 * S)
    d.text((ex + 100 * S, ey - 60 * S), "?", font=f, fill=Y, stroke_width=10 * S, stroke_fill=NAVY)
    img.resize((1920, 1080), Image.LANCZOS).save(out)


def compass_heading(out):
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 880 * S, W, H], fill="#d9dde6")
    cx, cy, rad = 760 * S, 610 * S, 290 * S
    d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill="white", outline=NAVY, width=14 * S)
    for deg in range(0, 360, 30):  # heading: 0 = start direction (up), clockwise
        a = math.radians(deg - 90)
        r1 = rad - (60 if deg % 90 == 0 else 34) * S
        d.line([(cx + r1 * math.cos(a), cy + r1 * math.sin(a)), (cx + (rad - 10 * S) * math.cos(a), cy + (rad - 10 * S) * math.sin(a))],
               fill=NAVY, width=(12 if deg % 90 == 0 else 6) * S)
    f = ImageFont.truetype(FONT, 58 * S)
    for deg, (dx, dy) in {0: (0, -1), 90: (1, 0), 180: (0, 1), 270: (-1, 0)}.items():
        rr = rad + 70 * S
        d.text((cx + dx * rr, cy + dy * rr), f"{deg}°", font=f, fill=NAVY, anchor="mm")
    # big arrow toward 90 degrees (the window)
    d.line([(cx + 90 * S, cy), (cx + 170 * S, cy)], fill=Y, width=40 * S)
    d.polygon([(cx + 250 * S, cy), (cx + 160 * S, cy - 56 * S), (cx + 160 * S, cy + 56 * S)], fill=Y, outline=NAVY, width=6 * S)
    flop_topdown(d, cx, cy, 0, 1.3)
    # the window
    wx0, wy0, wx1, wy1 = 1320 * S, 400 * S, 1600 * S, 820 * S
    d.rounded_rectangle([wx0, wy0, wx1, wy1], radius=16 * S, fill="#cfe9ff", outline=NAVY, width=14 * S)
    d.line([((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], fill=NAVY, width=12 * S)
    d.line([(wx0, (wy0 + wy1) / 2), (wx1, (wy0 + wy1) / 2)], fill=NAVY, width=12 * S)
    img.resize((1920, 1080), Image.LANCZOS).save(out)


if __name__ == "__main__":
    os.makedirs("refs/diagrams", exist_ok=True)
    drift_path("refs/diagrams/drift_path.png")
    compass_heading("refs/diagrams/compass_heading.png")
    print("wrote refs/diagrams/drift_path.png, refs/diagrams/compass_heading.png")
