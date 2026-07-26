#!/usr/bin/env python3
"""Procedural animated GIF banner for the MT5 trading guide repo.
Theme: dark hood background, teal/gold candlesticks rising, an EA "bot" node,
and a notification ping. Crisp text drawn in code (never in AI prompt)."""
import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 720, 360
FPS = 20
FRAMES = 60  # 3s loop
random.seed(7)

BG0 = (18, 22, 28)
BG1 = (28, 34, 42)
TEAL = (38, 208, 206)
GOLD = (240, 190, 70)
MUTED = (120, 140, 150)
WHITE = (235, 240, 245)

def lerp(a, b, t): return a + (b - a) * t

def bg():
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        t = y / H
        r = int(lerp(BG0[0], BG1[0], t))
        g = int(lerp(BG0[1], BG1[1], t))
        b = int(lerp(BG0[2], BG1[2], t))
        for x in range(W):
            px[x, y] = (r, g, b)
    return img

def glow_text(d, xy, text, font, fill, glow, alpha=255):
    x, y = xy
    for dx, dy in [(-2,-2),(2,-2),(-2,2),(2,2),(0,-3),(0,3),(-3,0),(3,0)]:
        d.text((x+dx, y+dy), text, font=font, fill=glow + (alpha,))
    d.text((x, y), text, font=font, fill=fill + (alpha,))

def font(sz, bold=True):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            pass
    return ImageFont.load_default()

# candlestick data (precomputed random walk)
prices = [H*0.62]
for _ in range(28):
    prices.append(max(60, min(H*0.85, prices[-1] + random.uniform(-26, 30))))

frames = []
for f in range(FRAMES):
    phase = f / FRAMES
    img = bg()
    d = ImageDraw.Draw(img, "RGBA")

    # --- moving grid lines (subtle) ---
    off = int(phase * 40) % 40
    for gx in range(-off, W, 40):
        d.line([(gx, 0), (gx, H)], fill=(255,255,255,8))
    for gy in range(0, H, 40):
        d.line([(0, gy), (W, gy)], fill=(255,255,255,8))

    # --- candlesticks rising across, scrolling ---
    n = len(prices)
    cw = 18
    gap = 6
    start = -(phase * (cw+gap) * 3) % ((cw+gap)*n)
    base_x = 40 + start
    for i in range(n):
        x = base_x + i*(cw+gap)
        if x < 20 or x > W-20:
            continue
        p = prices[i]
        up = (i % 3 != 0)
        col = GOLD if up else TEAL
        body_top = int(p - 10 - 6*math.sin(i))
        body_bot = int(p + 10)
        # wick
        d.line([(x+cw//2, body_top-14), (x+cw//2, body_bot+14)], fill=col+(200,), width=2)
        # body glow
        for e in range(6,0,-2):
            d.rectangle([x-e, body_top-e, x+cw+e, body_bot+e], fill=col+(12,))
        d.rectangle([x, body_top, x+cw, body_bot], fill=col+(230,))

    # --- EA bot node (top-right) orbiting dot ---
    cx, cy = W-110, 90
    ang = phase * 2*math.pi
    bx = int(cx + 34*math.cos(ang))
    by = int(cy + 22*math.sin(ang))
    for e in range(10,0,-2):
        d.ellipse([cx-e-14, cy-e-14, cx+e+14, cy+e+14], fill=TEAL+(10,))
    d.ellipse([cx-14, cy-14, cx+14, cy+14], fill=TEAL+(220,))
    # bot "eyes"
    d.ellipse([cx-7, cy-4, cx-2, cy+1], fill=(10,14,18,255))
    d.ellipse([cx+2, cy-4, cx+7, cy+1], fill=(10,14,18,255))
    # orbiting ping
    for e in range(8,0,-2):
        d.ellipse([bx-e, by-e, bx+e, by+e], fill=GOLD+(18,))
    d.ellipse([bx-3, by-3, bx+3, by+3], fill=GOLD+(240,))

    # connection line bot -> chart (dashed)
    dash = (int(phase*20)) % 10
    y0 = cy+10
    for yy in range(y0, H-40, 14):
        if ((yy - dash) // 14) % 2 == 0:
            d.line([(cx, yy), (cx, yy+7)], fill=TEAL+(70,))

    # --- title + tagline (crisp code text) ---
    glow_text(d,(40,24),"MT5 Trading Bot", font(34), WHITE, TEAL)
    glow_text(d,(42,70),"Headless Linux · Wine · Expert Advisors", font(16), MUTED, (0,0,0))

    # --- live "ping" indicator bottom-left pulsing ---
    pr = 6 + 4*math.sin(phase*2*math.pi)
    d.ellipse([44-pr, H-40-pr, 44+pr, H-40+pr], fill=GOLD+(120,))
    d.ellipse([40, H-44, 48, H-36], fill=GOLD+(240,))
    glow_text(d,(60, H-50),"Trade alert → notification", font(14), MUTED, (0,0,0))

    img = img.filter(ImageFilter.GaussianBlur(0.4))
    frames.append(img)

out = "/tmp/mt5-guide/mt5-banner.gif"
small = [fr.resize((600, 300)) for fr in frames[::3]]
small[0].save(out, save_all=True, append_images=small[1:],
              duration=int(1000/FPS*2), loop=0, optimize=True, disposal=2)
print("saved", out)
import os
print("size KB", round(os.path.getsize(out)/1024,1))
