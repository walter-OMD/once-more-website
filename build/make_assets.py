"""Generate placeholder brand assets matching the OnceMore Digital design system.
Replace these with real artwork later. Image *paths* match the existing setup."""
from PIL import Image, ImageDraw, ImageFont
import os

DARK = (10, 10, 10)
BLUE = (77, 101, 175)
BLUE_LIGHT = (122, 144, 199)
OFF_WHITE = (244, 244, 242)

SITE = "/home/claude/site"
IMG = os.path.join(SITE, "assets", "img")
os.makedirs(IMG, exist_ok=True)


def font(size):
    for p in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def monogram(size, bg=DARK, ring=True, transparent=False):
    """Square 'OM' monogram inside a ring."""
    scale = 4
    s = size * scale
    mode = "RGBA" if transparent else "RGB"
    base = (0, 0, 0, 0) if transparent else bg
    im = Image.new(mode, (s, s), base)
    d = ImageDraw.Draw(im)
    cx = cy = s / 2
    if ring:
        r = s * 0.40
        w = max(2, int(s * 0.045))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=BLUE, width=w)
    f = font(int(s * 0.34))
    txt = "OM"
    bbox = d.textbbox((0, 0), txt, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text((cx - tw / 2 - bbox[0], cy - th / 2 - bbox[1]), txt, font=f, fill=OFF_WHITE)
    return im.resize((size, size), Image.LANCZOS)


# Header logo: 512 transparent square monogram
monogram(512, transparent=True, ring=True).save(os.path.join(IMG, "logo.png"))

# Favicon 32 and apple-touch-icon 180 (solid dark bg)
monogram(32, bg=DARK, ring=False).save(os.path.join(IMG, "favicon.png"))
monogram(180, bg=DARK, ring=True).save(os.path.join(IMG, "apple-touch-icon.png"))

# Open Graph banner 1200x630 referenced by existing path at site root
og = Image.new("RGB", (1200, 630), DARK)
d = ImageDraw.Draw(og)
# subtle accent bar
d.rectangle([0, 0, 1200, 8], fill=BLUE)
mark = monogram(180, transparent=True, ring=True)
og.paste(mark, (110, 225), mark)
f1 = font(64)
f2 = font(30)
d.text((330, 250), "OnceMore Digital", font=f1, fill=OFF_WHITE)
d.text((332, 330), "SEO  .  GEO  .  AI Optimisation  .  Content",
       font=f2, fill=BLUE_LIGHT)
# keep the exact filename/destination from the existing markup
og.save(os.path.join(SITE, "oncemoredigial-seo-marketing-logo.png"))

print("assets written to", IMG)
print(os.listdir(IMG))
print("og:", os.path.exists(os.path.join(SITE, "oncemoredigial-seo-marketing-logo.png")))
