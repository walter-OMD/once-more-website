from PIL import Image, ImageChops
import os

SRC = "/mnt/user-data/uploads/OnceMoreDigital_Logo_Final_02-02.png"
IMG = "/home/claude/site/assets/img"

im = Image.open(SRC).convert("RGB")
W, H = im.size

# drop the wordmark band at the top, keep the square emblem
band = int(0.17 * H)
box = im.crop((0, band, W, H))

# work small for speed
if box.width > 560:
    s = 560 / box.width
    box = box.resize((int(box.width * s), int(box.height * s)), Image.LANCZOS)

# knock out the black background (and the black letter counters) -> transparent
box = box.convert("RGBA")
px = box.load()
w, h = box.size
for y in range(h):
    for x in range(w):
        r, g, b, a = px[x, y]
        m = max(r, g, b)
        if m <= 40:
            px[x, y] = (r, g, b, 0)
        elif m < 78:
            px[x, y] = (r, g, b, int(255 * (m - 40) / 38))

bbox = box.getbbox()
if bbox:
    box = box.crop(bbox)

# pad to a centered square
side = max(box.size)
sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
sq.alpha_composite(box, ((side - box.width) // 2, (side - box.height) // 2))

# favicon: transparent, 256x256
sq.resize((256, 256), Image.LANCZOS).save(os.path.join(IMG, "favicon.png"))

# apple touch icon: emblem on a midnight-ash tile (iOS shows it on home screen)
tile = Image.new("RGBA", (180, 180), (34, 34, 34, 255))
pad = 26
inner = 180 - 2 * pad
em = sq.resize((inner, inner), Image.LANCZOS)
tile.alpha_composite(em, (pad, pad))
tile.convert("RGB").save(os.path.join(IMG, "apple-touch-icon.png"))

# remove the truly unused placeholder
old = os.path.join(IMG, "logo.png")
if os.path.exists(old):
    os.remove(old)
    print("removed logo.png")

print("favicon + apple-touch-icon rebuilt from new logo")
print("img dir:", sorted(f for f in os.listdir(IMG) if os.path.isfile(os.path.join(IMG, f))))
