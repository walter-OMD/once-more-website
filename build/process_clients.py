from PIL import Image, ImageChops
import os

UP = "/mnt/user-data/uploads"
OUT = "/home/claude/site/assets/img/clients"
os.makedirs(OUT, exist_ok=True)

# dst name, source file, mode
JOBS = [
    ("aig.png",          "326071863_1478758332613739_6592146866949606955_n.png", "keep"),
    ("hertz.png",        "hertz.png",                       "keep"),
    ("ikea.png",         "Ikea_logo_svg.png",               "keep"),
    ("wspace.png",       "wspace.png",                      "keep"),
    ("maggi.png",        "Maggi-Logo.png",                  "blacktrans"),
    ("nestle.png",       "Nestle__svg.png",                 "blacktrans"),
    ("xcl.png",          "xcl-logo.png",                    "blacktrans"),
    ("common-ground.png","common-ground-logo.png",          "keep"),
    ("bank-negara.png",  "Logo_Bank_Negara_Malaysia.png",   "keep"),
    ("real-schools.png", "images.png",                      "keep"),
    ("nhg.png",          "NHG.webp",                         "alpha"),
]

MAXDIM = 600

def trim_uniform(im):
    """Trim border only if it's near-white or near-black; keep coloured tiles whole."""
    rgb = im.convert("RGB")
    corner = rgb.getpixel((0, 0))
    lum = sum(corner) / 3
    if lum > 235 or lum < 20:           # white-ish or black-ish border -> trim it
        bg = Image.new("RGB", rgb.size, corner)
        diff = ImageChops.difference(rgb, bg)
        bbox = diff.getbbox()
        if bbox:
            pad = 6
            l, t, r, b = bbox
            l = max(0, l - pad); t = max(0, t - pad)
            r = min(rgb.size[0], r + pad); b = min(rgb.size[1], b + pad)
            im = im.crop((l, t, r, b))
    return im

def black_to_transparent(im):
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            m = max(r, g, b)
            if m <= 38:
                px[x, y] = (r, g, b, 0)
            elif m < 70:
                px[x, y] = (r, g, b, int(255 * (m - 38) / 32))
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    return im

def downscale(im):
    w, h = im.size
    if max(w, h) > MAXDIM:
        s = MAXDIM / max(w, h)
        im = im.resize((int(w * s), int(h * s)), Image.LANCZOS)
    return im

for dst, src, mode in JOBS:
    p = os.path.join(UP, src)
    im = Image.open(p)
    if mode == "alpha":
        im = im.convert("RGBA")
        bbox = im.getbbox()
        if bbox: im = im.crop(bbox)
    elif mode == "blacktrans":
        im = black_to_transparent(im)
    else:  # keep
        im = trim_uniform(im)
    im = downscale(im)
    im.save(os.path.join(OUT, dst))
    print(f"{dst:20s} <- {src[:30]:30s} {mode:11s} {im.size}")

print("\nclient logos:", sorted(os.listdir(OUT)))
