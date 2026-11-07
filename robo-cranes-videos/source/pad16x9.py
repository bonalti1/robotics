"""Widen square reference art to 16:9 by repeating the edge background columns (art itself untouched)."""
import sys
from PIL import Image
src, dst, frac = sys.argv[1], sys.argv[2], float(sys.argv[3])  # frac = share of extra width placed on the LEFT
im = Image.open(src).convert("RGB")
w, h = im.size
W = round(h * 16 / 9)
extra = W - w
left = round(extra * frac)
out = Image.new("RGB", (W, h))
lcol = im.crop((0, 0, 1, h)).resize((left, h)) if left else None
rcol = im.crop((w - 1, 0, w, h)).resize((extra - left, h))
if lcol: out.paste(lcol, (0, 0))
out.paste(im, (left, 0))
out.paste(rcol, (left + w, 0))
out = out.resize((1920, 1080), Image.LANCZOS)
out.save(dst, optimize=True)
print(dst, out.size)
