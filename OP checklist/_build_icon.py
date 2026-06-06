# -*- coding: utf-8 -*-
"""
產生 OP Checklist 的 App 圖示（加到手機主畫面用）。
設計：鋼藍漸層底 + 白色麻醉面罩（teardrop 罩體 + 頂部 22mm 接頭，含通氣孔）。
用 Pillow 在 4x 超取樣畫，再 LANCZOS 縮到各尺寸，邊緣平滑。
改完重跑：  py "OP checklist/_build_icon.py"
輸出：OP checklist/icons/{icon-512,icon-192,apple-touch-icon,favicon-32}.png
"""
import os
from PIL import Image, ImageDraw

SS = 4                      # 超取樣倍率
BASE = 512                  # 設計座標基準
W = BASE * SS               # 工作畫布尺寸

TOP = (30, 58, 95)          # #1e3a5f 深鋼藍
BOTTOM = (59, 111, 160)     # #3b6fa0 鋼藍
WHITE = (255, 255, 255, 255)
INNER = (190, 214, 239, 255)  # #bcd6ef 罩內淺藍

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
os.makedirs(OUT_DIR, exist_ok=True)


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def make_gradient():
    img = Image.new("RGB", (W, W), TOP)
    d = ImageDraw.Draw(img)
    for y in range(W):
        d.line([(0, y), (W, y)], fill=lerp(TOP, BOTTOM, y / (W - 1)))
    return img


def cubic(p0, p1, p2, p3, n=48):
    pts = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        x = (mt**3)*p0[0] + 3*(mt**2)*t*p1[0] + 3*mt*(t**2)*p2[0] + (t**3)*p3[0]
        y = (mt**3)*p0[1] + 3*(mt**2)*t*p1[1] + 3*mt*(t**2)*p2[1] + (t**3)*p3[1]
        pts.append((x, y))
    return pts


# 麻醉面罩外形（寬、圓潤偏三角：上方鼻端窄、下方下巴寬），512 座標、順時針
SEGMENTS = [
    ((256, 178), (330, 182), (380, 250), (392, 330)),   # 右上（鼻端→右臉頰）
    ((392, 330), (398, 374), (352, 400), (300, 410)),   # 右下
    ((300, 410), (272, 416), (240, 416), (212, 410)),   # 底部下巴圓弧
    ((212, 410), (160, 400), (114, 374), (120, 330)),   # 左下
    ((120, 330), (132, 250), (182, 182), (256, 178)),   # 左上（左臉頰→鼻端）
]


def teardrop_points():
    pts = []
    for seg in SEGMENTS:
        pts.extend(cubic(*seg))
    return pts


def scale_pts(pts, cx, cy, k):
    return [((x - cx) * k + cx, (y - cy) * k + cy) for (x, y) in pts]


def s(v):
    """設計座標 → 工作畫布座標"""
    return v * SS


def draw_fallback():
    """沒有 source.png 時，用程式繪製一個面罩圖示當備案。"""
    base = make_gradient().convert("RGBA")
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    outer = [(s(x), s(y)) for (x, y) in teardrop_points()]
    inner = [(s(x), s(y)) for (x, y) in scale_pts(teardrop_points(), 256, 332, 0.58)]

    d.rounded_rectangle([s(220), s(120), s(292), s(196)], radius=s(16), fill=WHITE)
    d.polygon(outer, fill=WHITE)
    d.polygon(inner, fill=INNER)
    d.ellipse([s(216), s(104), s(296), s(150)], fill=WHITE)
    d.ellipse([s(234), s(115), s(278), s(141)], fill=(0, 0, 0, 0))

    return Image.alpha_composite(base, layer).convert("RGB").resize((BASE, BASE), Image.LANCZOS)


def build():
    src = os.path.join(OUT_DIR, "source.png")
    if os.path.exists(src):
        print("using master:", os.path.join("icons", "source.png"))
        img = Image.open(src).convert("RGB")
        w, h = img.size
        if w != h:  # 非正方形 → 置中裁成正方形
            m = min(w, h)
            img = img.crop(((w - m) // 2, (h - m) // 2, (w + m) // 2, (h + m) // 2))
    else:
        print("source.png 不存在，改用內建繪製")
        img = draw_fallback()

    targets = {
        "icon-512.png": 512,
        "icon-192.png": 192,
        "apple-touch-icon.png": 180,
        "favicon-32.png": 32,
    }
    for name, size in targets.items():
        out = img.resize((size, size), Image.LANCZOS)
        out.save(os.path.join(OUT_DIR, name))
        print("wrote", os.path.join("icons", name), size)


if __name__ == "__main__":
    build()
