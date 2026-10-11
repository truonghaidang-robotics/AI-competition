"""Generate AI/robot vector assets for EchoCommerce Studio (Taobao-orange palette).

Outputs (into ./assets):
  hero_ai_robot.png  - main hero illustration (transparent bg, dark-theme friendly)
  robot_avatar.png   - round robot avatar
  motif_waves.png    - subtle background wave/dot motif

Run:  python tools/make_assets.py
"""

import math
import os

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
os.makedirs(ASSETS, exist_ok=True)

SS = 4  # supersample factor

# ------------------------------------------------------------------ palette
ORANGE_HI = (255, 176, 58)
ORANGE = (255, 138, 31)
ORANGE_DP = (255, 80, 0)
ORANGE_DEEP = (214, 58, 0)
ORANGE_DARK = (150, 38, 0)
CREAM = (255, 232, 194)
WHITE = (255, 255, 255)
SHELL_HI = (255, 253, 249)
SHELL = (250, 238, 226)   # robot shell (kept light for contrast on dark bg)
SHELL_SIDE = (233, 208, 186)
SHELL_EDGE = (243, 214, 186)
PLAT_TOP = (255, 250, 242)
PLAT_LEFT = (240, 218, 196)
PLAT_RIGHT = (219, 192, 168)
VISOR = (32, 21, 15)
VISOR_2 = (19, 12, 9)
CARD_HI = (255, 250, 244)
CARD_LO = (245, 225, 205)
CARD_EDGE = (238, 208, 180)
DARK_RIM = (150, 92, 54)   # dark rim so light vector faces read on a dark page


def L(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(round(c1[i] + (c2[i] - c1[i]) * t)) for i in range(3))


def A(c, a):
    return (c[0], c[1], c[2], int(a))


def _bbox(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def poly(dr, pts, fill):
    dr.polygon([(float(x), float(y)) for x, y in pts], fill=fill)


def grad_poly(base, pts, c1, c2, axis="x"):
    x0, y0, x1, y1 = _bbox(pts)
    x0, y0, x1, y1 = int(x0), int(y0), int(math.ceil(x1)), int(math.ceil(y1))
    w, h = max(1, x1 - x0 + 1), max(1, y1 - y0 + 1)
    grad = Image.new("RGB", (w, h))
    gd = ImageDraw.Draw(grad)
    if axis == "x":
        for i in range(w):
            gd.line([(i, 0), (i, h)], fill=L(c1, c2, i / max(1, w - 1)))
    elif axis == "y":
        for j in range(h):
            gd.line([(0, j), (w, j)], fill=L(c1, c2, j / max(1, h - 1)))
    else:
        px = grad.load()
        for j in range(h):
            for i in range(w):
                px[i, j] = L(c1, c2, (i / max(1, w - 1) + j / max(1, h - 1)) / 2)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).polygon([(x - x0, y - y0) for x, y in pts], fill=255)
    base.paste(grad, (x0, y0), mask)


def grad_round_rect(base, box, radius, c1, c2, axis="y"):
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    radius = int(round(radius))
    w, h = max(1, x1 - x0 + 1), max(1, y1 - y0 + 1)
    grad = Image.new("RGB", (w, h))
    gd = ImageDraw.Draw(grad)
    if axis == "x":
        for i in range(w):
            gd.line([(i, 0), (i, h)], fill=L(c1, c2, i / max(1, w - 1)))
    elif axis == "y":
        for j in range(h):
            gd.line([(0, j), (w, j)], fill=L(c1, c2, j / max(1, h - 1)))
    else:
        px = grad.load()
        for j in range(h):
            for i in range(w):
                px[i, j] = L(c1, c2, (i / max(1, w - 1) + j / max(1, h - 1)) / 2)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=255)
    base.paste(grad, (x0, y0), mask)


def soft_ellipse(base, box, color, alpha, blur):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse(box, fill=A(color, alpha))
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


def glow(base, center, radius, color=ORANGE, alpha=90, rings=40, power=1.6):
    d = int(radius * 2)
    layer = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    dr = ImageDraw.Draw(layer)
    for i in range(rings, 0, -1):
        r = radius * i / rings
        a = int(alpha * (1 - i / rings) ** power)
        if a <= 0:
            continue
        dr.ellipse([radius - r, radius - r, radius + r, radius + r], fill=A(color, a))
    base.alpha_composite(
        layer.filter(ImageFilter.GaussianBlur(radius * 0.05)),
        (int(center[0] - radius), int(center[1] - radius)),
    )


def circle(base, center, radius, c1, c2=None, outline=None, width=0, axis="y"):
    box = (center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius)
    if c2 is None:
        ImageDraw.Draw(base).ellipse(box, fill=c1)
    else:
        grad_round_rect(base, box, int(radius), c1, c2, axis)
    if outline is not None:
        ImageDraw.Draw(base).ellipse(box, outline=outline, width=max(1, int(width)))


def iso_cube(base, cx, cy, s, top, left, right, h=None):
    h = s * 0.86 if h is None else h
    dr = ImageDraw.Draw(base)
    poly(dr, [(cx - s, cy), (cx, cy + s * 0.86), (cx, cy + s * 0.86 + h), (cx - s, cy + h)], left)
    poly(dr, [(cx + s, cy), (cx, cy + s * 0.86), (cx, cy + s * 0.86 + h), (cx + s, cy + h)], right)
    grad_poly(base, [(cx, cy - s * 0.86), (cx + s, cy), (cx, cy + s * 0.86), (cx - s, cy)], top[0], top[1], "y")


def iso_cube_outline(base, cx, cy, s, h, color, width):
    """Dark rim around an isometric cube so light faces read on a dark page."""
    dr = ImageDraw.Draw(base)
    hh = s * 0.86
    dr.line(
        [
            (cx, cy - hh),
            (cx + s, cy),
            (cx + s, cy + h),
            (cx, cy + hh + h),
            (cx - s, cy + h),
            (cx - s, cy),
            (cx, cy - hh),
        ],
        fill=color,
        width=width,
        joint="curve",
    )
    dr.line([(cx, cy + hh), (cx - s, cy + h)], fill=color, width=width)
    dr.line([(cx, cy + hh), (cx + s, cy + h)], fill=color, width=width)
    dr.line([(cx, cy + hh), (cx, cy + hh + h)], fill=color, width=width)


def rounded_diamond(dr, cx, cy, w, hh, outline, width):
    pts = [
        (cx, cy - hh),
        (cx + w, cy),
        (cx, cy + hh),
        (cx - w, cy),
    ]
    dr.line(pts + [pts[0]], fill=outline, width=width, joint="curve")
    r = width / 2
    for p in pts:
        dr.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=outline)


# ------------------------------------------------------------------ robot
def robot(base, cx, cy, s=1.0, accent=ORANGE_DP, badge=True):
    """Friendly AI robot. (cx, cy) = centre of the HEAD; s = pixel scale (1.0 -> ~500px tall)."""

    def X(v):
        return cx + v * s

    def Y(v):
        return cy + v * s

    dr = ImageDraw.Draw(base)

    dr = ImageDraw.Draw(base)

    # ---- floating platform (dark rim keeps it readable on a dark page)
    iso_cube(
        base,
        X(0),
        Y(214),
        s * 150,
        (PLAT_TOP, (250, 228, 202)),
        PLAT_LEFT,
        PLAT_RIGHT,
        h=s * 34,
    )
    iso_cube_outline(
        base,
        X(0),
        Y(214),
        s * 150,
        h=s * 34,
        color=DARK_RIM,
        width=max(2, int(3 * s)),
    )
    dr = ImageDraw.Draw(base)

    # ---- contact shadow on the platform top face
    soft_ellipse(base, [X(-92), Y(186), X(92), Y(232)], (96, 52, 16), 120, 14 * s)
    dr = ImageDraw.Draw(base)

    # ---- legs / feet on the platform
    for side in (-1, 1):
        fx = X(side * 46)
        dr.rounded_rectangle(
            [fx - 20 * s, Y(150), fx + 20 * s, Y(214)],
            radius=12 * s,
            fill=SHELL,
            outline=SHELL_EDGE,
            width=max(2, int(3 * s)),
        )

    # ---- arms (behind body, relaxed at the sides)
    for side in (-1, 1):
        shoulder = (X(side * 68), Y(62))
        elbow = (X(side * 112), Y(122))
        hand = (X(side * 124), Y(170))
        dr.line([shoulder, elbow, hand], fill=SHELL_SIDE, width=int(26 * s), joint="curve")
    for side in (-1, 1):
        circle(base, (X(side * 124), Y(178)), 22 * s, SHELL_HI, SHELL_SIDE, SHELL_EDGE, 3 * s)
        dr = ImageDraw.Draw(base)

    # ---- body
    body = [X(-76), Y(38), X(76), Y(178)]
    grad_round_rect(base, body, 30 * s, SHELL_HI, (243, 220, 199), "y")
    dr = ImageDraw.Draw(base)
    dr.rounded_rectangle(body, radius=30 * s, outline=SHELL_EDGE, width=max(2, int(4 * s)))
    if badge:
        circle(base, (X(0), Y(106)), 30 * s, ORANGE_HI, accent, axis="xy")
        dr = ImageDraw.Draw(base)
        rounded_diamond(dr, X(0), Y(106), 15 * s, 15 * s, (255, 248, 240), max(2, int(5 * s)))
        dr = ImageDraw.Draw(base)

    # ---- neck
    dr.rounded_rectangle(
        [X(-22), Y(-58), X(22), Y(52)],
        radius=14 * s,
        fill=(240, 219, 199),
        outline=SHELL_EDGE,
        width=max(2, int(3 * s)),
    )

    # ---- antenna
    dr.line([X(0), Y(-128), X(0), Y(-186)], fill=accent, width=max(2, int(11 * s)))
    glow(base, (X(0), Y(-206)), 56 * s, ORANGE, alpha=140)
    circle(base, (X(0), Y(-206)), 24 * s, (255, 214, 150), accent)
    dr = ImageDraw.Draw(base)

    # ---- head shell
    head = [X(-104), Y(-128), X(104), Y(60)]
    soft_ellipse(base, [X(-110), Y(-110), X(110), Y(80)], (60, 26, 6), 80, 20 * s)
    dr = ImageDraw.Draw(base)
    dr.rounded_rectangle(head, radius=44 * s, fill=SHELL)
    grad_round_rect(base, head, 44 * s, SHELL_HI, (245, 226, 206), "y")
    dr = ImageDraw.Draw(base)
    dr.rounded_rectangle(head, radius=44 * s, outline=SHELL_EDGE, width=max(2, int(4 * s)))

    # ---- visor
    visor = [X(-82), Y(-100), X(82), Y(30)]
    grad_round_rect(base, visor, 32 * s, VISOR, VISOR_2, "y")
    dr = ImageDraw.Draw(base)
    # sheen on the glass
    sheen = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(sheen).polygon(
        [
            (X(-74), Y(-96)),
            (X(-16), Y(-96)),
            (X(-60), Y(22)),
            (X(-78), Y(22)),
        ],
        fill=(255, 255, 255, 24),
    )
    base.alpha_composite(sheen)
    dr = ImageDraw.Draw(base)

    # ---- eyes
    for ex in (-40, 40):
        glow(base, (X(ex), Y(-38)), 34 * s, ORANGE, alpha=170)
        circle(base, (X(ex), Y(-38)), 16 * s, (255, 216, 152), accent)
        dr = ImageDraw.Draw(base)
        dr.ellipse([X(ex) - 5 * s, Y(-44), X(ex) + 5 * s, Y(-32)], fill=(255, 252, 246))
    # ---- smile
    dr.arc(
        [X(-30), Y(-44), X(30), Y(6)],
        start=18,
        end=162,
        fill=(255, 184, 100),
        width=max(2, int(7 * s)),
    )
    # ---- ear pods
    for side in (-1, 1):
        dr.rounded_rectangle(
            [X(side * 104) - 12 * s, Y(-72), X(side * 104) + 12 * s, Y(-4)],
            radius=11 * s,
            fill=ORANGE,
            outline=(255, 205, 130),
            width=max(1, int(2.5 * s)),
        )


# ------------------------------------------------------------------ hero
def make_hero():
    W, H = 1600, 900
    img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))

    def P(x, y):
        return (x * SS, y * SS)

    dr = ImageDraw.Draw(img)

    # ---- subtle warm glow pockets (kept dim so they read on a dark page)
    glow(img, P(320, 400), 300 * SS, (255, 120, 30), alpha=34)
    glow(img, P(1290, 400), 300 * SS, (255, 150, 50), alpha=30)
    glow(img, P(800, 640), 330 * SS, ORANGE, alpha=26)
    dr = ImageDraw.Draw(img)

    # ---- orbit rings
    for rx, ry, wdt, al in [(330, 168, 3, 34), (408, 208, 2, 22)]:
        dr.ellipse(
            [P(800 - rx, 520 - ry)[0], P(800 - rx, 520 - ry)[1],
             P(800 + rx, 520 + ry)[0], P(800 + rx, 520 + ry)[1]],
            outline=A((255, 150, 70), al),
            width=int(wdt * SS),
        )

    # ---- dot grid confined to the centre
    for gy in range(320, 740, 26):
        for gx in range(430, 1180, 26):
            if ((gx - 800) / 420) ** 2 + ((gy - 530) / 250) ** 2 > 1:
                continue
            r = int(1.5 * SS)
            dr.ellipse([gx * SS - r, gy * SS - r, gx * SS + r, gy * SS + r], fill=A((255, 170, 90), 40))

    # ---- circuit traces
    traces = [
        [(238, 470), (392, 470), (452, 410), (560, 410)],
        [(1362, 452), (1226, 452), (1160, 512), (1058, 512)],
        [(268, 268), (420, 268), (470, 322), (596, 322)],
        [(1332, 250), (1214, 250), (1156, 306), (1052, 306)],
        [(300, 706), (430, 706), (486, 654), (612, 654)],
        [(1330, 690), (1168, 690), (1108, 650), (1010, 650)],
    ]
    for tr in traces:
        pts = [P(x, y) for x, y in tr]
        dr.line(pts, fill=A((255, 132, 46), 100), width=int(3.2 * SS), joint="curve")
        for p in (pts[0], pts[-1]):
            r = int(7 * SS)
            dr.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=A((255, 176, 84), 160))

    # ---- left: chip / data cube
    iso_cube(
        img, *P(252, 412), s=74 * SS,
        top=((255, 198, 116), ORANGE), left=(255, 118, 24), right=(198, 62, 6), h=70 * SS,
    )
    dr = ImageDraw.Draw(img)
    for dx, dy, col in [(-28, -16, (255, 238, 208)), (8, -28, (255, 208, 154)), (30, -4, (255, 182, 112))]:
        r = int(13 * SS)
        x, y = P(252 + dx, 384 + dy)
        dr.ellipse([x - r, y - r, x + r, y + r], fill=col)
    # pins
    for dx in (-40, -14, 14, 40):
        x, y = P(252 + dx, 470)
        dr.rounded_rectangle(
            [x - 5 * SS, y, x + 5 * SS, y + 26 * SS], radius=int(4 * SS), fill=(255, 172, 84)
        )

    # ---- helper robot (left) + support platform
    robot(img, 292 * SS, 556 * SS, s=0.32 * SS, accent=(255, 118, 20))

    # ---- left bottom: database cylinder (2 discs, tucked under the helper)
    for i in (2, 1):
        cx, cy = P(330, 712 + i * 26)
        rx, ry = int(78 * SS), int(39 * SS)
        dr.ellipse([cx - rx, cy - ry + 30 * SS, cx + rx, cy + ry + 30 * SS], fill=(188, 68, 6))
        dr.ellipse(
            [cx - rx, cy - ry, cx + rx, cy + ry],
            fill=L(ORANGE_DP, (150, 40, 2), (2 - i)),
        )
        dr.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=A(CREAM, 210), width=int(3 * SS))

    # ---- left: neural network
    nodes = [(470, 566), (534, 620), (486, 676), (572, 700), (614, 626)]
    edges = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (1, 4), (4, 3), (2, 4)]
    for a, b in edges:
        dr.line([P(*nodes[a]), P(*nodes[b])], fill=A((255, 150, 70), 105), width=int(2.7 * SS))
    for x, y in nodes:
        cxp, cyp = P(x, y)
        glow(img, (cxp, cyp), 40 * SS, ORANGE, alpha=80)
        dr = ImageDraw.Draw(img)
        r = int(16 * SS)
        dr.ellipse([cxp - r, cyp - r, cxp + r, cyp + r], fill=(255, 246, 234))
        dr.ellipse([cxp - r, cyp - r, cxp + r, cyp + r], outline=ORANGE, width=int(4 * SS))
        r2 = int(7 * SS)
        dr.ellipse([cxp - r2, cyp - r2, cxp + r2, cyp + r2], fill=ORANGE_DP)

    # ---- right top: paper plane
    px, py = P(1332, 292)
    plane = [
        (px - 96 * SS, py + 28 * SS),
        (px + 100 * SS, py - 36 * SS),
        (px + 6 * SS, py + 12 * SS),
        (px + 22 * SS, py + 78 * SS),
        (px - 10 * SS, py + 36 * SS),
    ]
    grad_poly(img, plane, (255, 216, 154), (255, 122, 24), "x")
    dr = ImageDraw.Draw(img)
    dr.polygon(
        [(px + 6 * SS, py + 12 * SS), (px + 100 * SS, py - 36 * SS), (px + 22 * SS, py + 78 * SS)],
        fill=(255, 158, 58),
    )
    dr.line(
        [(px - 96 * SS, py + 28 * SS), (px + 6 * SS, py + 12 * SS), (px - 10 * SS, py + 36 * SS)],
        fill=(255, 234, 204), width=int(3 * SS), joint="curve",
    )

    # ---- right: analytics card
    x0, y0 = P(1196, 452)
    x1, y1 = P(1484, 636)
    soft_ellipse(img, [x0, y0 + 12 * SS, x1, y1 + 22 * SS], (30, 12, 2), 150, 18 * SS)
    grad_round_rect(img, (x0, y0, x1, y1), 24 * SS, CARD_HI, CARD_LO, "y")
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle((x0, y0, x1, y1), radius=24 * SS, outline=CARD_EDGE, width=int(3 * SS))
    for bx, bh, col in [(1236, 92, (255, 206, 138)), (1298, 134, (255, 166, 72)), (1360, 112, ORANGE)]:
        bx0, by0 = P(bx, 592 - bh)
        bx1, by1 = P(bx + 42, 592)
        grad_round_rect(img, (bx0, by0, bx1, by1), 10 * SS, L(col, WHITE, 0.3), col, "y")
    dr = ImageDraw.Draw(img)
    trend = [P(1224, 566), P(1282, 534), P(1330, 552), P(1392, 496), P(1450, 472)]
    dr.line(trend, fill=A(ORANGE_DEEP, 200), width=int(4 * SS), joint="curve")
    for p in trend:
        r = int(6 * SS)
        dr.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=(255, 246, 232))

    # ---- right bottom: helper robot head badge
    hx, hy = P(1300, 742)
    glow(img, (hx, hy), 120 * SS, ORANGE, alpha=80)
    circle(img, (hx, hy), 76 * SS, SHELL_HI, SHELL_SIDE, A(ORANGE, 220), 4 * SS)
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle(
        [hx - 44 * SS, hy - 38 * SS, hx + 44 * SS, hy + 30 * SS],
        radius=18 * SS, fill=VISOR,
    )
    for ex in (-18, 18):
        r = int(9 * SS)
        dr.ellipse([hx + ex * SS - r, hy - 8 * SS - r, hx + ex * SS + r, hy - 8 * SS + r], fill=ORANGE_HI)
    dr.line([hx, hy - 38 * SS, hx, hy - 58 * SS], fill=ORANGE_DP, width=int(5 * SS))
    r = int(9 * SS)
    dr.ellipse([hx - r, hy - 58 * SS - r, hx + r, hy - 58 * SS + r], fill=(255, 200, 110))

    # ---- floating panels
    for x, y, w, hh, kind in [(556, 236, 246, 128, "code"), (900, 592, 236, 118, "media")]:
        px0, py0 = P(x, y)
        px1, py1 = P(x + w, y + hh)
        soft_ellipse(img, [px0, py0 + 12 * SS, px1, py1 + 20 * SS], (30, 12, 2), 140, 16 * SS)
        grad_round_rect(img, (px0, py0, px1, py1), 20 * SS, CARD_HI, CARD_LO, "y")
        dr = ImageDraw.Draw(img)
        dr.rounded_rectangle((px0, py0, px1, py1), radius=20 * SS, outline=CARD_EDGE, width=int(3 * SS))
        for i, col in enumerate([ORANGE, (255, 178, 74), (255, 214, 150)]):
            r = int(7 * SS)
            cxp, cyp = px0 + int((22 + i * 20) * SS), py0 + int(20 * SS)
            dr.ellipse([cxp - r, cyp - r, cxp + r, cyp + r], fill=col)
        if kind == "code":
            for i, fw in enumerate([0.72, 0.5, 0.62, 0.42]):
                lx0 = px0 + int(20 * SS)
                ly = py0 + int((50 + i * 19) * SS)
                lx1 = lx0 + int((w - 40) * fw * SS)
                dr.rounded_rectangle(
                    [lx0, ly, lx1, ly + int(9 * SS)],
                    radius=int(5 * SS),
                    fill=L((255, 196, 120), (255, 110, 20), i / 3),
                )
        else:
            pbx, pby = px0 + int(w * 0.28 * SS), py0 + int(hh * 0.6 * SS)
            circle(img, (pbx, pby), 30 * SS, ORANGE_HI, ORANGE_DP, axis="xy")
            dr = ImageDraw.Draw(img)
            dr.polygon(
                [(pbx - 8 * SS, pby - 14 * SS), (pbx - 8 * SS, pby + 14 * SS), (pbx + 15 * SS, pby)],
                fill=(255, 250, 244),
            )
            for i, bh in enumerate([14, 30, 22, 38, 18, 28]):
                bx = px0 + int((w * 0.5 + i * 16) * SS)
                by = py0 + int(hh * 0.6 * SS)
                dr.rounded_rectangle(
                    [bx, by - int(bh / 2 * SS), bx + int(7 * SS), by + int(bh / 2 * SS)],
                    radius=int(3.5 * SS),
                    fill=L((255, 202, 134), (255, 110, 20), i / 5),
                )

    # ---- sparkles
    dr = ImageDraw.Draw(img)
    for x, y, sz in [(700, 196, 16), (960, 168, 12), (1120, 620, 13), (330, 208, 11), (1470, 630, 12), (766, 760, 13)]:
        cxp, cyp = P(x, y)
        wdt = int(3.4 * SS)
        dr.line([cxp - sz * SS, cyp, cxp + sz * SS, cyp], fill=A((255, 190, 104), 215), width=wdt)
        dr.line([cxp, cyp - sz * SS, cxp, cyp + sz * SS], fill=A((255, 190, 104), 215), width=wdt)

    # ---- hero robot (centre)
    robot(img, 800 * SS, 380 * SS, s=1.0 * SS)

    out = img.resize((W, H), Image.LANCZOS)
    out.save(os.path.join(ASSETS, "hero_ai_robot.png"))
    return out.size


# ------------------------------------------------------------------ avatar
def make_avatar():
    S = 640
    K = 4
    img = Image.new("RGBA", (S * K, S * K), (0, 0, 0, 0))
    r = S * 0.94
    ImageDraw.Draw(img).ellipse([S - r, S - r, S + r, S + r], fill=(24, 15, 10, 255))
    glow(img, (S, S * 0.7), S * 0.95, ORANGE, alpha=110)
    robot(img, S, S * 0.46, s=0.72, accent=(255, 118, 20), badge=False)
    mask = Image.new("L", (S * K, S * K), 0)
    ImageDraw.Draw(mask).ellipse([S - r, S - r, S + r, S + r], fill=255)
    img.putalpha(Image.composite(img.getchannel("A"), Image.new("L", img.size, 0), mask))
    out = img.resize((S, S), Image.LANCZOS)
    out.save(os.path.join(ASSETS, "robot_avatar.png"))
    return out.size


# ------------------------------------------------------------------ motif
def make_motif():
    W, H = 1200, 420
    K = 2
    img = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    for i in range(9):
        t = i / 8
        base_y = (120 + 100 * t) * K
        pts = []
        for k in range(0, 161):
            x = k / 160 * W * K
            amp = 40 * (1 - abs(0.5 - k / 160) * 1.3)
            pts.append((x, base_y + amp * math.sin(k / 160 * math.pi * 3 + i * 0.5)))
        col = L((255, 150, 60), (255, 90, 10), t)
        dr.line(pts, fill=A(col, 80), width=int(2.6 * K), joint="curve")
    img = img.resize((W, H), Image.LANCZOS)
    img.save(os.path.join(ASSETS, "motif_waves.png"))
    return img.size


def make_ui_icons():
    """Small round-gradient UI glyphs used in headings and buttons."""
    S, K = 96, 8
    icons = {
        "ic_doc": "doc",
        "ic_titles": "titles",
        "ic_chat": "chat",
        "ic_copy": "copy",
        "ic_image": "image",
        "ic_video": "video",
        "ic_bot": "bot",
        "ic_bolt": "bolt",
    }
    sizes = {}
    for name, kind in icons.items():
        img = Image.new("RGBA", (S * K, S * K), (0, 0, 0, 0))
        # rounded gradient tile
        grad_round_rect(
            img, (0, 0, S * K - 1, S * K - 1), 26 * K, (255, 138, 31), (226, 58, 0), "xy"
        )
        dr = ImageDraw.Draw(img)
        w = int(7 * K)
        ink = (255, 248, 240)

        def rr(x0, y0, x1, y1, rad, fill=None, outline=None, width=w):
            dr.rounded_rectangle(
                [x0 * K, y0 * K, x1 * K, y1 * K],
                radius=rad * K,
                fill=fill,
                outline=outline,
                width=width,
            )

        if kind == "doc":
            rr(28, 22, 68, 74, 8, outline=ink)
            for i, yy in enumerate((38, 50, 62)):
                xe = 60 if i < 2 else 50
                dr.line([32 * K, yy * K, xe * K, yy * K], fill=ink, width=int(5 * K))
        elif kind == "titles":
            for i, yy in enumerate((28, 48, 68)):
                xe = 74 if i != 1 else 60
                rr(20, yy - 5, xe, yy + 5, 5, fill=ink)
        elif kind == "chat":
            rr(18, 22, 78, 60, 12, outline=ink)
            dr.polygon(
                [(34 * K, 60 * K), (34 * K, 78 * K), (52 * K, 60 * K)], fill=ink
            )
        elif kind == "copy":
            rr(20, 26, 60, 74, 8, outline=ink)
            rr(34, 16, 74, 62, 8, fill=(255, 138, 31), outline=ink)
        elif kind == "image":
            rr(18, 24, 78, 72, 10, outline=ink)
            dr.ellipse([30 * K, 34 * K, 44 * K, 48 * K], fill=ink)
            dr.polygon(
                [(24 * K, 66 * K), (46 * K, 46 * K), (58 * K, 60 * K), (64 * K, 54 * K), (74 * K, 66 * K)],
                fill=ink,
            )
        elif kind == "video":
            rr(16, 28, 56, 68, 9, outline=ink)
            dr.polygon(
                [(62 * K, 40 * K), (80 * K, 28 * K), (80 * K, 68 * K), (62 * K, 56 * K)],
                fill=ink,
            )
        elif kind == "bot":
            rr(24, 30, 72, 74, 14, fill=(30, 20, 14), outline=ink)
            for ex in (38, 58):
                dr.ellipse(
                    [(ex - 7) * K, 44 * K, (ex + 7) * K, 58 * K], fill=ink
                )
            dr.line([48 * K, 30 * K, 48 * K, 16 * K], fill=ink, width=int(5 * K))
            dr.ellipse([42 * K, 8 * K, 54 * K, 20 * K], fill=ink)
        elif kind == "bolt":
            dr.polygon(
                [
                    (54 * K, 12 * K),
                    (28 * K, 54 * K),
                    (45 * K, 54 * K),
                    (40 * K, 84 * K),
                    (68 * K, 42 * K),
                    (51 * K, 42 * K),
                ],
                fill=ink,
            )
        out = img.resize((S, S), Image.LANCZOS)
        out.save(os.path.join(ASSETS, f"{name}.png"))
        sizes[name] = out.size
    return sizes


if __name__ == "__main__":
    print("hero:", make_hero())
    print("avatar:", make_avatar())
    print("motif:", make_motif())
    print("ui icons:", make_ui_icons())
    for f in sorted(os.listdir(ASSETS)):
        p = os.path.join(ASSETS, f)
        if os.path.isfile(p):
            print("  ", f, os.path.getsize(p), "bytes")
