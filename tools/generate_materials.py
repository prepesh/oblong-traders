"""Generate the placeholder material studies used across the site.

These are procedural, photographic-feeling material renders (leather, brushed
steel, a watch dial, ceramic glaze, felt, gold, hammered copper, kraft board).
They stand in until real product photography is supplied — drop real photos
into assets/img/ with the same filenames to replace them.

Usage: python3 tools/generate_materials.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parent.parent / "assets" / "img"
OUT.mkdir(parents=True, exist_ok=True)
W, H = 1600, 1200
rng = np.random.default_rng(7)


def noise(w, h, scale, seed=None):
    """Smooth value noise in [0, 1] using bicubic upsampling."""
    r = np.random.default_rng(seed) if seed is not None else rng
    gw, gh = max(2, int(w / scale)), max(2, int(h / scale))
    small = Image.fromarray((r.random((gh, gw)) * 255).astype(np.uint8))
    return np.asarray(small.resize((w, h), Image.BICUBIC), dtype=np.float32) / 255.0


def fbm(w, h, base, octaves=5, gain=0.5):
    out = np.zeros((h, w), np.float32)
    amp, total, s = 1.0, 0.0, base
    for _ in range(octaves):
        out += amp * noise(w, h, s)
        total += amp
        amp *= gain
        s = max(2, s / 2)
    return out / total


def shade(height, strength=4.0, light=(-0.6, -0.7, 0.9)):
    """Lambert shading of a height map — gives the tactile relief."""
    gy, gx = np.gradient(height * strength)
    n = np.dstack([-gx, -gy, np.ones_like(height)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    l = np.array(light, np.float32)
    l /= np.linalg.norm(l)
    return np.clip((n * l).sum(axis=2), 0, 1)


def colorize(t, stops):
    """Map t in [0,1] through color stops [(pos, (r,g,b)), ...]."""
    t = np.clip(t, 0, 1)
    out = np.zeros(t.shape + (3,), np.float32)
    for i in range(3):
        out[..., i] = np.interp(t, [p for p, _ in stops], [c[i] for _, c in stops])
    return out


def vignette(img, amount=0.35):
    h, w = img.shape[:2]
    y, x = np.ogrid[-1:1:h * 1j, -1:1:w * 1j]
    v = 1 - amount * np.clip((x ** 2 + y ** 2) / 1.6, 0, 1)
    return img * v[..., None]


def light_falloff(h, w, cx=0.3, cy=0.25, power=0.45):
    y, x = np.mgrid[0:h, 0:w]
    d = np.sqrt(((x / w) - cx) ** 2 + ((y / h) - cy) ** 2)
    return 1 - power * np.clip(d, 0, 1)


def save(arr, name, grain=0.025):
    arr = arr + rng.normal(0, grain * 255, arr.shape[:2])[..., None]
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    img.save(OUT / name, quality=80, optimize=True, progressive=True)
    print("wrote", name)


def leather():
    base = fbm(W, H, 260, 4)
    # pebble grain: thresholded high-frequency noise, blurred into soft cells
    cells = noise(W, H, 7) * 0.6 + noise(W, H, 3.5) * 0.4
    cells = np.asarray(Image.fromarray((cells * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255
    height = cells * 0.8 + base * 0.6
    lit = shade(height, 9)
    tone = colorize(base * 0.7 + lit * 0.5, [(0.0, (52, 24, 12)), (0.45, (122, 62, 30)), (0.8, (176, 98, 52)), (1.0, (214, 148, 98))])
    img = tone * (0.55 + 0.6 * lit[..., None]) * light_falloff(H, W)[..., None]
    # stitched seam
    im = Image.fromarray(np.clip(vignette(img), 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    y0 = int(H * 0.72)
    d.line([(0, y0 - 26), (W, y0 - 70)], fill=(40, 18, 8), width=5)
    for x in range(-20, W, 34):
        yy = y0 + 4 - (x / W) * 44
        d.line([(x, yy), (x + 20, yy - 1)], fill=(232, 214, 186), width=5)
    save(np.asarray(im, np.float32), "leather.jpg")


def brushed(name, stops, angle_rows=True):
    n = rng.random((H, W)).astype(np.float32)
    im = Image.fromarray((n * 255).astype(np.uint8)).resize((W // 2, H), Image.BILINEAR).resize((W, H))
    streak = np.asarray(im.filter(ImageFilter.BoxBlur(0)), np.float32)
    streak = np.asarray(Image.fromarray(streak.astype(np.uint8)).resize((40, H), Image.BOX).resize((W, H), Image.BILINEAR), np.float32) / 255
    y, x = np.mgrid[0:H, 0:W]
    band = np.exp(-(((y - x * 0.35 - H * 0.15) / (H * 0.22)) ** 2))
    t = 0.35 + 0.25 * streak + 0.35 * band
    return colorize(t, stops), band


def steel():
    tone, band = brushed("steel", [(0, (38, 39, 41)), (0.5, (120, 122, 124)), (0.8, (196, 198, 200)), (1, (236, 236, 236))])
    save(vignette(tone, 0.25), "steel.jpg", 0.02)


def watch_dial():
    S = 1600
    y, x = np.mgrid[0:S, 0:S].astype(np.float32)
    cx = cy = S / 2
    ang = np.arctan2(y - cy, x - cx)
    r = np.hypot(x - cx, y - cy)
    # sunburst brushing: noise indexed by angle only
    a_idx = ((ang + np.pi) / (2 * np.pi) * 4000).astype(int) % 4000
    ray = rng.random(4000).astype(np.float32)
    ray = np.convolve(ray, np.ones(3) / 3, mode="same")
    burst = ray[a_idx]
    sheen = 0.5 + 0.5 * np.cos(2 * (ang + 0.8))
    t = 0.18 + 0.12 * burst + 0.35 * sheen * np.clip(r / (S * 0.42), 0, 1)
    tone = colorize(t, [(0, (16, 16, 17)), (0.4, (44, 45, 47)), (0.7, (98, 99, 101)), (1, (170, 170, 170))])
    img = Image.fromarray(np.clip(tone, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    R = S * 0.40
    # case ring
    d.ellipse([cx - R - 60, cy - R - 60, cx + R + 60, cy + R + 60], outline=(150, 150, 150), width=34)
    d.ellipse([cx - R - 26, cy - R - 26, cx + R + 26, cy + R + 26], outline=(26, 26, 26), width=10)
    for i in range(60):
        a = i / 60 * 2 * np.pi
        major = i % 5 == 0
        r1, r2 = R - (70 if major else 26), R - 6
        col = (245, 130, 32) if i == 0 else (228, 228, 224)
        d.line([(cx + r1 * np.sin(a), cy - r1 * np.cos(a)), (cx + r2 * np.sin(a), cy - r2 * np.cos(a))], fill=col, width=14 if major else 4)

    def hand(a, length, width, col):
        a = np.deg2rad(a)
        tip = (cx + length * np.sin(a), cy - length * np.cos(a))
        tail = (cx - 60 * np.sin(a), cy + 60 * np.cos(a))
        d.line([tail, tip], fill=col, width=width)

    hand(305, R * 0.55, 26, (232, 232, 228))
    hand(60, R * 0.82, 16, (232, 232, 228))
    hand(160, R * 0.9, 5, (245, 130, 32))
    d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(245, 130, 32))
    arr = np.asarray(img.filter(ImageFilter.GaussianBlur(0.8)), np.float32)
    out = np.zeros((H, W, 3), np.float32) + 22
    crop = arr[(S - H) // 2:(S + H) // 2, :]
    out[:] = crop[:, :W]
    save(vignette(out, 0.45), "watch.jpg", 0.018)


def ceramic():
    base = fbm(W, H, 500, 4)
    drip = noise(W, 1, 220)[0] * 0.7 + noise(W, 1, 90)[0] * 0.3
    y = np.linspace(0, 1, H)[:, None]
    glaze_line = 0.42 + 0.16 * (drip[None, :] - 0.5) * 2
    upper = y < glaze_line
    glaze = colorize(base, [(0, (196, 204, 194)), (0.6, (226, 230, 220)), (1, (246, 246, 240))])
    clay = colorize(base, [(0, (150, 108, 82)), (0.5, (184, 140, 108)), (1, (206, 170, 138))])
    img = np.where(upper[..., None], glaze, clay)
    edge = np.exp(-((y - glaze_line) / 0.012) ** 2)
    img = img * (1 - 0.35 * edge[..., None])
    speck = rng.random((H, W)) > 0.9975
    img[speck] *= 0.45
    yy, xx = np.mgrid[0:H, 0:W]
    gloss = np.exp(-(((xx - W * 0.7) / (W * 0.08)) ** 2)) * upper * 0.18
    img = img + gloss[..., None] * 255
    lit = light_falloff(H, W, 0.75, 0.2, 0.35)
    save(vignette(img * lit[..., None], 0.3), "ceramic.jpg", 0.015)


def felt():
    fib = np.zeros((H, W), np.float32)
    for s in (2.5, 4, 7):
        n = noise(W, H, s)
        fib += np.asarray(Image.fromarray((n * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7)), np.float32) / 255
    fib /= 3
    base = fbm(W, H, 400, 3)
    lit = shade(fib + base * 0.3, 3)
    tone = colorize(base * 0.5 + fib * 0.5, [(0, (78, 76, 72)), (0.5, (128, 124, 116)), (1, (170, 164, 152))])
    img = tone * (0.7 + 0.4 * lit[..., None])
    save(vignette(img, 0.3), "felt.jpg", 0.03)


def gold():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    img = np.zeros((H, W, 3), np.float32) + np.array([20, 18, 16], np.float32)
    bok = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(bok)
    for _ in range(46):
        cx, cy, r = rng.random() * W, rng.random() * H, 30 + rng.random() * 140
        k = 0.12 + rng.random() * 0.3
        c = (int(230 * k), int(170 * k), int(90 * k))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    bok = np.asarray(bok.filter(ImageFilter.GaussianBlur(18)), np.float32)
    # a polished chain-like ring arc
    ring = np.exp(-((np.hypot(x - W * 0.58, y - H * 0.62) - H * 0.36) / 26) ** 2)
    hi = 0.5 + 0.5 * np.cos((np.arctan2(y - H * 0.62, x - W * 0.58)) * 3)
    gold_col = colorize(hi, [(0, (120, 78, 24)), (0.6, (214, 168, 84)), (1, (255, 236, 180))])
    img = img + bok + ring[..., None] * gold_col
    save(vignette(img, 0.35), "jewelry.jpg", 0.02)


def hammered():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    height = np.zeros((H, W), np.float32)
    for _ in range(420):
        cx, cy, r = rng.random() * W, rng.random() * H, 50 + rng.random() * 60
        x0, x1, y0, y1 = int(max(cx - r, 0)), int(min(cx + r, W)), int(max(cy - r, 0)), int(min(cy + r, H))
        sub = (x[y0:y1, x0:x1] - cx) ** 2 + (y[y0:y1, x0:x1] - cy) ** 2
        height[y0:y1, x0:x1] = np.minimum(height[y0:y1, x0:x1], -np.clip(1 - sub / r ** 2, 0, 1))
    lit = shade(height, 40, (-0.5, -0.6, 0.6))
    tone = colorize(lit, [(0, (60, 26, 14)), (0.45, (150, 72, 40)), (0.8, (214, 130, 84)), (1, (255, 214, 176))])
    save(vignette(tone * light_falloff(H, W, 0.4, 0.3, 0.3)[..., None], 0.35), "metalwork.jpg", 0.02)


def kraft():
    fib = fbm(W, H, 40, 4)
    base = fbm(W, H, 600, 3)
    tone = colorize(base * 0.6 + fib * 0.4, [(0, (150, 112, 74)), (0.5, (182, 142, 100)), (1, (208, 172, 130))])
    img = Image.fromarray(np.clip(tone, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    # die-cut box net: crease lines + an embossed panel
    for xx in (W * 0.28, W * 0.72):
        d.line([(xx, 0), (xx, H)], fill=(120, 88, 56), width=3)
    d.line([(0, H * 0.32), (W, H * 0.32)], fill=(120, 88, 56), width=3)
    d.rectangle([W * 0.36, H * 0.46, W * 0.64, H * 0.74], outline=(232, 204, 166), width=3)
    d.rectangle([W * 0.362, H * 0.462, W * 0.642, H * 0.742], outline=(110, 80, 50), width=2)
    arr = np.asarray(img.filter(ImageFilter.GaussianBlur(0.6)), np.float32)
    save(vignette(arr * light_falloff(H, W, 0.65, 0.2, 0.35)[..., None], 0.3), "packaging.jpg", 0.03)


def linen():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    weave = 0.5 + 0.25 * np.sin(x * 0.9 + noise(W, H, 30) * 6) * np.sin(y * 0.9 + noise(W, H, 30) * 6)
    slub = noise(W, H, 6)
    t = weave * 0.6 + slub * 0.3 + fbm(W, H, 500, 2) * 0.3
    tone = colorize(t, [(0, (150, 146, 136)), (0.5, (204, 200, 190)), (1, (238, 236, 228))])
    save(vignette(tone, 0.25), "linen.jpg", 0.02)


if __name__ == "__main__":
    for fn in (leather, steel, watch_dial, ceramic, felt, gold, hammered, kraft, linen):
        fn()
