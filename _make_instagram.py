from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import os

SRC = "/mnt/c/Users/amani_lf8ahhr/Desktop/Mynewprojects/maadhuram/WhatsApp Image 2026-04-28 at 7.33.56 AM.jpeg"
OUT_DIR = "/mnt/c/Users/amani_lf8ahhr/Desktop/Mynewprojects/maadhuram"


def enhance(img: Image.Image) -> Image.Image:
    img = ImageEnhance.Brightness(img).enhance(1.12)
    img = ImageEnhance.Contrast(img).enhance(1.18)
    img = ImageEnhance.Color(img).enhance(1.22)
    img = ImageEnhance.Sharpness(img).enhance(1.35)
    return img


def smart_crop(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    src_w, src_h = img.size
    target_ratio = target_w / target_h
    src_ratio = src_w / src_h

    if src_ratio > target_ratio:
        new_w = int(src_h * target_ratio)
        # bottle is roughly centered horizontally, but slightly left in source
        left = max(0, (src_w - new_w) // 2 - int(src_w * 0.02))
        box = (left, 0, left + new_w, src_h)
    else:
        new_h = int(src_w / target_ratio)
        # keep top of bottle (cap) visible — bias crop upward
        top = max(0, (src_h - new_h) // 3)
        box = (0, top, src_w, top + new_h)

    cropped = img.crop(box)
    return cropped.resize((target_w, target_h), Image.LANCZOS)


def add_vignette(img: Image.Image, strength: float = 0.35) -> Image.Image:
    w, h = img.size
    # radial gradient mask
    mask = Image.new("L", (w, h), 0)
    px = mask.load()
    cx, cy = w / 2, h / 2
    max_d = (cx ** 2 + cy ** 2) ** 0.5
    for y in range(h):
        for x in range(w):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            v = int(255 * (d / max_d))
            px[x, y] = v
    mask = mask.filter(ImageFilter.GaussianBlur(radius=w * 0.08))
    dark = Image.new("RGB", (w, h), (0, 0, 0))
    return Image.composite(dark, img, mask).point(
        lambda p: p
    ) if False else Image.blend(img, Image.composite(dark, img, mask), strength)


def add_vignette_fast(img: Image.Image, strength: float = 0.35) -> Image.Image:
    w, h = img.size
    # build a small radial mask then upscale (much faster than per-pixel)
    small = 256
    m = Image.new("L", (small, small), 0)
    mp = m.load()
    cx, cy = small / 2, small / 2
    max_d = (cx ** 2 + cy ** 2) ** 0.5
    for y in range(small):
        for x in range(small):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            mp[x, y] = int(255 * (d / max_d) ** 1.6)
    m = m.resize((w, h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(radius=w * 0.06))
    dark = Image.new("RGB", (w, h), (10, 8, 6))
    darkened = Image.composite(dark, img, m)
    return Image.blend(img, darkened, strength)


def main():
    src = Image.open(SRC).convert("RGB")
    src = ImageOps.exif_transpose(src)

    # --- 4:5 portrait (1080x1350) — best for IG feed product posts
    portrait = smart_crop(src, 1080, 1350)
    portrait = enhance(portrait)
    portrait = add_vignette_fast(portrait, strength=0.30)
    p_out = os.path.join(OUT_DIR, "maadhuram_shampoo_ig_4x5.jpg")
    portrait.save(p_out, "JPEG", quality=92, optimize=True, progressive=True)
    print(f"saved {p_out} ({portrait.size})")

    # --- 1:1 square (1080x1080) — fit whole bottle with branded side padding
    # first build a tight portrait of the full bottle, then pad to square
    tight = smart_crop(src, 900, 1080)  # narrow portrait keeps whole bottle
    tight = enhance(tight)
    tight = add_vignette_fast(tight, strength=0.25)
    # warm cream/beige background that complements the label
    bg = Image.new("RGB", (1080, 1080), (236, 224, 206))
    # subtle gradient: lighter top, slightly darker bottom
    grad = Image.new("L", (1, 1080))
    gp = grad.load()
    for y in range(1080):
        gp[0, y] = int(255 - (y / 1080) * 28)
    grad = grad.resize((1080, 1080))
    dark_bg = Image.new("RGB", (1080, 1080), (210, 196, 174))
    bg = Image.composite(bg, dark_bg, grad)
    # paste the tight portrait centered, scaled to fit square height
    scale = 1080 / tight.height
    new_w = int(tight.width * scale)
    tight_resized = tight.resize((new_w, 1080), Image.LANCZOS)
    bg.paste(tight_resized, ((1080 - new_w) // 2, 0))
    s_out = os.path.join(OUT_DIR, "maadhuram_shampoo_ig_1x1.jpg")
    bg.save(s_out, "JPEG", quality=92, optimize=True, progressive=True)
    print(f"saved {s_out} ({bg.size})")

    # --- 9:16 story/reels (1080x1920)
    story = smart_crop(src, 1080, 1920)
    story = enhance(story)
    story = add_vignette_fast(story, strength=0.32)
    st_out = os.path.join(OUT_DIR, "maadhuram_shampoo_ig_9x16.jpg")
    story.save(st_out, "JPEG", quality=92, optimize=True, progressive=True)
    print(f"saved {st_out} ({story.size})")


if __name__ == "__main__":
    main()
