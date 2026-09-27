"""Turn the photos in /images into fast, responsive WebP files in site/assets/img.

For every image key in content.IMG it writes:
  {stem}-480/-720/-960.webp          responsive sizes (srcset)
  {stem}-sq.webp                      320px square thumbnail cropped on the focal point
  {stem}-blur.webp                    small pre-blurred copy for hero backgrounds (no CSS filter cost)
  {stem}-og.jpg                       1200px JPEG for social sharing

Returns a manifest: {key: {"w":..., "h":..., "sizes": [...]}} used by build.py for width/height.
Requires Pillow (pip install pillow).
"""
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps


def _focal(pos):
    x, y = (float(v.strip("%")) / 100 for v in pos.split())
    return x, y


def _square(im, size, pos):
    fx, fy = _focal(pos)
    w, h = im.size
    s = min(w, h)
    left = min(max(int(fx * w - s / 2), 0), w - s)
    top = min(max(int(fy * h - s / 2), 0), h - s)
    return im.crop((left, top, left + s, top + s)).resize((size, size), Image.LANCZOS)


def optimise(img_map, src_dir: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for key, (fname, _alt, pos) in img_map.items():
        src = src_dir / fname
        stem = Path(fname).stem
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        w, h = im.size
        sizes = []
        for target in (480, 720, 960):
            if target > w and sizes:
                continue
            tw = min(target, w)
            th = round(h * tw / w)
            dst = out_dir / f"{stem}-{target}.webp"
            if not dst.exists():
                im.resize((tw, th), Image.LANCZOS).save(dst, "WEBP", quality=66 if target > 480 else 70, method=6)
            sizes.append((target, tw, th))
        sq = out_dir / f"{stem}-sq.webp"
        if not sq.exists():
            _square(im, 320, pos).save(sq, "WEBP", quality=72, method=6)
        blur = out_dir / f"{stem}-blur.webp"
        if not blur.exists():
            bw = 960
            small = im.resize((bw, round(h * bw / w)), Image.LANCZOS).filter(ImageFilter.GaussianBlur(2.5))
            small.save(blur, "WEBP", quality=58, method=6)
        og = out_dir / f"{stem}-og.jpg"
        if not og.exists():
            o = im.copy()
            o.thumbnail((1200, 1200), Image.LANCZOS)
            o.save(og, "JPEG", quality=74, optimize=True, progressive=True)
        manifest[key] = {"stem": stem, "w": w, "h": h, "sizes": sizes}
    return manifest
