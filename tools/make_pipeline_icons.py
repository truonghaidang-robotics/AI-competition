#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
make_pipeline_icons.py
======================
Generate 4 flat-vector PNG icons for a Streamlit dark sidebar.

Approach
--------
Every icon is described once as vector geometry on a shared 256px design grid.
Two masks are produced from that geometry:

  * ``fmask`` - everything painted with the orange gradient
                (#FF5000 -> #FF8A1F -> #FFB03A, diagonal TL -> BR)
  * ``lmask`` - the warm light accents (#FFE8C2)

Both masks are drawn on a 1024x1024 canvas (4x supersampling), composited into
a single RGBA image, and downscaled to 256x256 with ``Image.LANCZOS`` so every
edge is smoothly anti-aliased. The background stays fully transparent and the
corners keep alpha 0.

Shared style: 60px strokes (== 15px at the 256 scale) with round caps and
round joins, one diagonal gradient direction, one visual density.

Outputs (assets/)
-----------------
icon_selection.png   Data Cleansing / Selection Agent - funnel + falling dot
icon_content.png     PR Scripting / Content Agent     - page + fold + pen
icon_compliance.png  Compliance Check / Visual Guard  - shield + check
icon_jimeng.png      AI Visual & Video / Jimeng Node  - ring + play + aperture

Run:
    python make_pipeline_icons.py
"""

import math
import os
import sys

from PIL import Image, ImageDraw

# --------------------------------------------------------------------------
# canvas / style constants
# --------------------------------------------------------------------------
FINAL = 256            # final icon edge in px
SS = 4                 # supersampling factor
WORK = FINAL * SS      # 1024px working canvas

STROKE = 50            # 12.5px at the 256 scale (clean at icon size)
HW = STROKE / 2.0      # round cap / join radius on the working canvas

GRAD_STOPS = [         # #FF5000 -> #FF8A1F -> #FFB03A
    (0.00, (0xFF, 0x50, 0x00)),
    (0.50, (0xFF, 0x8A, 0x1F)),
    (1.00, (0xFF, 0xB0, 0x3A)),
]
LIGHT = (0xFF, 0xE8, 0xC2)


def s(*vals):
    """Scale design coordinates (256 grid) up to the working canvas."""
    if len(vals) == 1 and isinstance(vals[0], (tuple, list)):
        vals = tuple(vals[0])
    return [v * SS for v in vals]


# --------------------------------------------------------------------------
# gradient paint (linear, top-left -> bottom-right)
# --------------------------------------------------------------------------
def _lerp(a, b, t):
    return a + (b - a) * t


def make_gradient(size=WORK, stops=GRAD_STOPS):
    """Diagonal 3-stop gradient as an RGB image."""
    ts = [st[0] for st in stops]
    px = []
    for y in range(size):
        row = []
        for x in range(size):
            t = (x + y) / (2.0 * (size - 1))
            t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
            if t <= ts[1]:
                span = ts[1] - ts[0]
                f = (t - ts[0]) / span if span else 0.0
                c0, c1 = stops[0][1], stops[1][1]
            else:
                span = ts[2] - ts[1]
                f = (t - ts[1]) / span if span else 0.0
                c0, c1 = stops[1][1], stops[2][1]
            row.append(tuple(int(round(_lerp(c0[i], c1[i], f))) for i in range(3)))
        px.append(row)
    img = Image.new("RGB", (size, size))
    img.putdata([c for row in px for c in row])
    return img


# --------------------------------------------------------------------------
# primitive helpers - each one paints into BOTH masks
# --------------------------------------------------------------------------
class Painter(object):
    """Draws geometry into the gradient mask; helpers named *light* also paint
    the warm light accent mask instead of the gradient."""

    def __init__(self):
        self.f = Image.new("L", (WORK, WORK), 0)
        self.l = Image.new("L", (WORK, WORK), 0)
        self.df = ImageDraw.Draw(self.f)
        self.dl = ImageDraw.Draw(self.l)

    # -- gradient geometry ------------------------------------------------
    def cap(self, d, p, r):
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=255)

    def seg(self, p0, p1, w=STROKE, light=False):
        d = self.dl if light else self.df
        r = w / 2.0
        d.line([p0, p1], fill=255, width=int(round(w)), joint="curve")
        self.cap(d, p0, r)
        self.cap(d, p1, r)

    def poly(self, points, w=STROKE, closed=False, light=False):
        d = self.dl if light else self.df
        pts = list(points)
        if len(pts) < 2:
            return
        r = w / 2.0
        for p in pts[1:-1]:
            self.cap(d, p, r)            # round joins
        if closed:
            pts = pts + [pts[0]]
        for a, b in zip(pts, pts[1:]):
            d.line([a, b], fill=255, width=int(round(w)), joint="curve")
        if not closed:
            self.cap(d, pts[0], r)
            self.cap(d, pts[-1], r)

    def dot(self, c, r, light=False):
        d = self.dl if light else self.df
        self.cap(d, c, r)

    def ring(self, c, r, w=STROKE, light=False):
        d = self.dl if light else self.df
        d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r],
                  outline=255, width=int(round(w)))

    def block(self, points, grow=HW, light=False):
        """Filled convex polygon expanded by `grow` so the *fill* ends up with
        the same visual weight as a stroked shape."""
        d = self.dl if light else self.df
        grown = self._grow(points, grow)
        d.polygon(grown, fill=255)

    @staticmethod
    def _grow(pts, grow):
        """Offset every edge of a convex polygon outwards by `grow` and take
        the intersections of neighbouring offset edges."""
        n = len(pts)
        edges = []
        for i in range(n):
            ax, ay = pts[i]
            bx, by = pts[(i + 1) % n]
            ex, ey = bx - ax, by - ay
            L = math.hypot(ex, ey) or 1.0
            edges.append(((ax, ay), (ey / L, -ex / L)))   # outward normal
        out = []
        for i in range(n):
            a, n1 = edges[(i - 1) % n]
            b, n2 = edges[i]
            d1 = (-n1[1], n1[0])
            d2 = (-n2[1], n2[0])
            den = d1[0] * d2[1] - d1[1] * d2[0]
            if abs(den) < 1e-9:
                out.append((b[0] + n2[0] * grow, b[1] + n2[1] * grow))
                continue
            wx, wy = b[0] - a[0], b[1] - a[1]
            t = (wx * d2[1] - wy * d2[0]) / den
            out.append((a[0] + d1[0] * t + n1[0] * grow,
                        a[1] + d1[1] * t + n1[1] * grow))
        return [tuple(p) for p in out]


# --------------------------------------------------------------------------
# icon 1 - Data Cleansing / Selection Agent : funnel with dots
# --------------------------------------------------------------------------
def draw_selection(p):
    # 3 dots scattered above the funnel mouth (warm light)
    for cx, cy in ((176, 62), (128, 45), (82, 62)):
        p.dot(s(cx, cy), 18 * SS, light=True)

    # funnel: wide at the top, narrow neck at the bottom
    p.poly([s(54, 95), s(202, 95), s(143, 145),
            s(143, 174), s(113, 174), s(113, 145)],
           closed=True)

    # 1 dot falling out of the funnel (gradient)
    p.dot(s(128, 208), 17 * SS)

    # 2 tiny horizontal lines under the funnel (warm light)
    p.seg(s(100, 230), s(156, 230), 11 * SS, light=True)
    p.seg(s(111, 244), s(145, 244), 11 * SS, light=True)


# --------------------------------------------------------------------------
# icon 2 - PR Scripting / Content Agent : page + folded corner + pen
# --------------------------------------------------------------------------
def draw_content(p):
    # page outline with a folded top-right corner
    p.poly([s(64, 32), s(166, 32), s(206, 70), s(206, 238), s(64, 238)],
           closed=True)
    p.poly([s(166, 32), s(206, 70), s(166, 70)], closed=True)   # folded ear

    # 3 text lines, kept clear of the page edges
    for x0, x1, y in ((90, 166, 110), (90, 166, 144), (90, 134, 178)):
        p.seg(s(x0, y), s(x1, y), 22 * SS)

    # pen / stylus resting diagonally at the page's bottom-right: a plain
    # rounded stroke reads unmistakably as a stylus against the page edge
    p.seg(s(184, 166), s(226, 220), 28 * SS)


# --------------------------------------------------------------------------
# icon 3 - Compliance Check / Visual Guard : shield + bold check
# --------------------------------------------------------------------------
def draw_compliance(p):
    # Rounded shield outline built from a smooth half-width profile so the
    # silhouette is symmetric and curves instead of faceting. Profile:
    # vertical upper sides -> shoulders -> tapered lower half -> bottom point.
    top, side_end, bottom = 42.0, 142.0, 224.0
    half_side, peak_half = 80.0, 72.0
    pts = []

    def pw(y):
        if y <= side_end:
            return half_side
        t = (y - side_end) / (bottom - side_end)
        return half_side + (0.0 - half_side) * (t ** 1.45)

    # top edge, left -> right, a shallow dome with a small centre peak
    for i in range(13):
        x = -peak_half + (peak_half * 2.0) * i / 12.0
        u = x / peak_half
        pts.append((128.0 + x, top + 2.0 * u * u))

    # right side and lower half, down to the point
    ys = [52.0, 62.0, 72.0, 84.0, 96.0, 108.0, 120.0, (side_end - 10.0),
          side_end, 150.0, 158.0, 166.0, 174.0, 182.0, 190.0, 198.0, 206.0,
          214.0, 220.0]
    for y in ys:
        w = pw(y)
        pts.append((128.0 + w, y))
    pts.append((128.0, bottom))
    # mirror the right half back up the left side
    for y in reversed(ys):
        w = pw(y)
        pts.append((128.0 - w, y))
    p.poly([(x * SS, y * SS) for (x, y) in pts[1:]], closed=True)

    # bold check mark, comfortably inside the shield
    p.poly([s(88, 122), s(116, 154), s(166, 88)], w=STROKE * 1.35)

    # warm light sparkle near the shield's top-left
    p.seg(s(52, 72), s(52, 98), 10 * SS, light=True)
    p.seg(s(39, 85), s(65, 85), 10 * SS, light=True)
    p.dot(s(68, 30), 13 * SS, light=True)


# --------------------------------------------------------------------------
# icon 4 - AI Visual & Video / Jimeng Node : ring + play + aperture
# --------------------------------------------------------------------------
def draw_jimeng(p):
    """Circular ring + one clean rounded play triangle, centred, with a real
    gap to the ring. The aperture ticks are detached dashes OUTSIDE the ring
    at 12 / 4 / 8 o'clock, and the two light dots orbit further out still.
    Every element is separated so nothing welds together."""
    cx, cy = 478.0, 520.0                  # working-canvas units
    r = 240.0
    ring_w = 40.0
    tri_w = 48.0

    # --- single circular ring, nothing overlapping its outline -------------
    p.ring((cx, cy), r, w=ring_w)

    # --- one solid play triangle, pointing right, centred: its rounded tips
    # --- and all three edges clear the ring by ~15px (256 scale) ----------
    p.block([(cx - 36.0, cy - 73.4), (cx + 113.7, cy),
             (cx - 36.0, cy + 73.4)], grow=30.0)

    # --- 3 detached rounded dashes outside the ring at 12 / 4 / 8 o'clock --
    for clock_ang in (270.0, 30.0, 150.0):
        a = math.radians(clock_ang)
        ca, sa = math.cos(a), math.sin(a)
        r1, r2 = 285.0, 330.0              # clear of the ring at 260
        p.seg((cx + ca * r1, cy + sa * r1), (cx + ca * r2, cy + sa * r2),
              22.0)

    # --- 2 warm light dots orbiting outside the ring, placed in the two
    # --- open zones between the dashes (2 o'clock and 10 o'clock) ---------
    p.dot((cx + 249.4, cy - 144.0), 30.0, light=True)     # ~2 o'clock
    p.dot((cx - 249.4, cy - 144.0), 30.0, light=True)     # ~10 o'clock


# --------------------------------------------------------------------------
# build + verify
# --------------------------------------------------------------------------
def build(draw_fn, gradient):
    p = Painter()
    draw_fn(p)

    rgba = Image.new("RGBA", (WORK, WORK), (0, 0, 0, 0))
    rgba.paste(gradient, (0, 0), p.f)                      # gradient strokes
    rgba = Image.alpha_composite(
        rgba,
        Image.composite(Image.new("RGBA", (WORK, WORK), LIGHT + (255,)),
                        Image.new("RGBA", (WORK, WORK), (0, 0, 0, 0)), p.l))
    return rgba.resize((FINAL, FINAL), Image.LANCZOS), p


def _mask_dist(mask, cx, cy, mode="far", thr=128):
    """Distance in working px from (cx, cy) to the mask's set pixels.
    mode='far'  -> the farthest set pixel  (how far the shape reaches out)
    mode='near' -> the nearest set pixel   (how close the shape comes in)
    Only the mask's bounding box is scanned, so this stays fast."""
    bb = mask.getbbox()
    if bb is None:
        return None
    px = mask.load()
    best = None
    for y in range(bb[1], bb[3]):
        dy = y + 0.5 - cy
        for x in range(bb[0], bb[2]):
            if px[x, y] > thr:
                dx = x + 0.5 - cx
                d = math.hypot(dx, dy)
                if best is None or (d > best if mode == "far" else d < best):
                    best = d
    return best


def jimeng_clearances():
    """Rebuild the Jimeng geometry in isolation and measure the real gaps at
    the 256 scale, so welded/overlapping parts are caught numerically."""
    cx, cy = 478.0, 520.0
    r, ring_w, tri_w = 240.0, 40.0, 48.0
    tri_r = tri_w / 2.0
    tri_pts = [(cx - 36.0, cy - 73.4), (cx + 113.7, cy), (cx - 36.0, cy + 73.4)]

    # triangle alone: how far its rounded outline reaches out from the centre
    tp = Painter()
    tp.block(tri_pts, grow=30.0)
    tri_outer = _mask_dist(tp.f, cx, cy, "far")

    # ring alone
    rp = Painter()
    rp.ring((cx, cy), r, w=ring_w)
    ring_inner = _mask_dist(rp.f, cx, cy, "near")
    ring_outer = _mask_dist(rp.f, cx, cy, "far")

    # dashes + dots
    dash_pts = []
    for ang in (270.0, 30.0, 150.0):
        a = math.radians(ang)
        ca, sa = math.cos(a), math.sin(a)
        r1, r2 = 285.0, 330.0
        dash_pts.append(((cx + ca * r1, cy + sa * r1),
                         (cx + ca * r2, cy + sa * r2)))
    dash_r = 11.0
    dots = [(cx + 249.4, cy - 144.0, 30.0), (cx - 249.4, cy - 144.0, 30.0)]

    def seg_seg(a, b, c, d):
        def pt_seg(p, q, s):
            vx, vy = s[0] - q[0], s[1] - q[1]
            wx, wy = p[0] - q[0], p[1] - q[1]
            L2 = vx * vx + vy * vy
            t = 0.0 if L2 == 0 else max(0.0, min(1.0, (wx * vx + wy * vy) / L2))
            return math.hypot(p[0] - (q[0] + t * vx), p[1] - (q[1] + t * vy))
        return min(pt_seg(a, c, d), pt_seg(b, c, d),
                   pt_seg(c, a, b), pt_seg(d, a, b))

    def pt_seg_dist(p, a, b):
        return seg_seg(p, p, a, b)

    dash_gaps = []
    for i in range(3):
        for j in range(i + 1, 3):
            dash_gaps.append(seg_seg(dash_pts[i][0], dash_pts[i][1],
                                     dash_pts[j][0], dash_pts[j][1]) - 2 * dash_r)

    # clearance from every separate element to every other separate element
    dot_clear = []
    for (dx, dy, dr) in dots:
        for d in dash_pts:
            dot_clear.append(pt_seg_dist((dx, dy), d[0], d[1]) - dr - dash_r)
        dot_clear.append(math.hypot(dx - cx, dy - cy) - dr - ring_outer)
    # dashes to the ring
    dash_ring = []
    for d in dash_pts:
        dash_ring.append(pt_seg_dist((cx, cy), d[0], d[1]) - dash_r - ring_outer)
    dot_dot = math.hypot(dots[0][0] - dots[1][0], dots[0][1] - dots[1][1]) \
        - dots[0][2] - dots[1][2]
    _ = tri_r

    return {
        "tri_outer_r": tri_outer,
        "ring_inner_r": ring_inner,
        "ring_outer_r": ring_outer,
        "tri_to_ring_gap": (ring_inner - tri_outer) / SS,
        "dash_to_ring_gap": min(dash_ring) / SS,
        "dash_gaps": [g / SS for g in dash_gaps],
        "dot_clearances": [c / SS for c in dot_clear],
        "dot_dot_gap": dot_dot / SS,
    }


def verify(path, img, extra=None):
    w, h = img.size
    alpha = img.getchannel("A")
    corners = [alpha.getpixel(pt) for pt in ((0, 0), (255, 0), (0, 255), (255, 255))]
    bbox = alpha.getbbox()
    hist = alpha.histogram()
    coverage = 100.0 * sum(hist[1:]) / float(w * h)

    problems = []
    if (w, h) != (FINAL, FINAL):
        problems.append("size is %dx%d, expected 256x256" % (w, h))
    if img.mode != "RGBA":
        problems.append("mode is %s, expected RGBA" % img.mode)
    if any(c != 0 for c in corners):
        problems.append("corner alpha not 0: %s" % (corners,))
    if not (8.0 <= coverage <= 60.0):
        problems.append("coverage %.2f%% outside the 8%%-60%% density window" % coverage)
    if bbox is None:
        problems.append("no non-transparent pixels")
    elif bbox[0] < 2 or bbox[1] < 2 or bbox[2] > 254 or bbox[3] > 254:
        problems.append("bbox %s touches the canvas edge" % (bbox,))
    else:
        # rough centring check: centre of mass of the bbox near canvas centre
        cxb = (bbox[0] + bbox[2]) / 2.0
        cyb = (bbox[1] + bbox[3]) / 2.0
        if abs(cxb - 128) > 24 or abs(cyb - 128) > 24:
            problems.append("bbox centre (%.0f,%.0f) is off-centre" % (cxb, cyb))

    if extra:
        if extra["tri_to_ring_gap"] < 8.0:
            problems.append("play triangle to ring gap is only %.1fpx (<8px)"
                            % extra["tri_to_ring_gap"])
        if extra["dash_to_ring_gap"] < 3.0:
            problems.append("dashes touch the ring (gap %.1fpx)"
                            % extra["dash_to_ring_gap"])
        if min(extra["dash_gaps"]) < 4.0:
            problems.append("dashes too close to each other (%.1fpx)"
                            % min(extra["dash_gaps"]))
        if min(extra["dot_clearances"]) < 3.0:
            problems.append("a light dot touches the ring or a dash (%.1fpx)"
                            % min(extra["dot_clearances"]))
        if extra["dot_dot_gap"] < 4.0:
            problems.append("the two light dots touch (%.1fpx)"
                            % extra["dot_dot_gap"])

    return {"path": path, "size": (w, h), "mode": img.mode, "corners": corners,
            "coverage": coverage, "bbox": bbox, "problems": problems,
            "extra": extra}


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    assets = os.path.join(os.path.dirname(here), "assets")
    os.makedirs(assets, exist_ok=True)

    print("working canvas %dx%d (SS=%d) -> final %dx%d" % (WORK, WORK, SS, FINAL, FINAL))
    print("output dir     %s" % assets)
    print("gradient       #FF5000 -> #FF8A1F -> #FFB03A (TL -> BR), stroke %.0fpx @4x" % STROKE)

    gradient = make_gradient(WORK)

    jobs = (("icon_selection.png", draw_selection),
            ("icon_content.png", draw_content),
            ("icon_compliance.png", draw_compliance),
            ("icon_jimeng.png", draw_jimeng))

    results = []
    for name, fn in jobs:
        img, _painter = build(fn, gradient)
        path = os.path.join(assets, name)
        img.save(path, "PNG")
        extra = jimeng_clearances() if name == "icon_jimeng.png" else None
        results.append(verify(path, img, extra))

    print("\n" + "=" * 74)
    print("VERIFICATION")
    print("=" * 74)
    ok_all = True
    for r in results:
        ok_all = ok_all and not r["problems"]
        print("\n[%s] %s" % ("PASS" if not r["problems"] else "FAIL", r["path"]))
        print("  size        : %d x %d" % r["size"])
        print("  mode        : %s" % r["mode"])
        print("  corner alpha: (0,0)=%d (255,0)=%d (0,255)=%d (255,255)=%d"
              % tuple(r["corners"]))
        print("  coverage    : %.2f%% non-transparent" % r["coverage"])
        print("  bbox        : %s" % (r["bbox"],))
        if r["extra"]:
            e = r["extra"]
            print("  geometry    : triangle->ring gap %.1fpx | dash->ring gap %.1fpx"
                  % (e["tri_to_ring_gap"], e["dash_to_ring_gap"]))
            print("                dash-dash gaps %s px | dot clearances %s px"
                  % (["%.1f" % g for g in e["dash_gaps"]],
                     ["%.1f" % c for c in e["dot_clearances"]]))
            print("                dot-dot gap %.1fpx" % e["dot_dot_gap"])
        if r["problems"]:
            print("  PROBLEMS    : %s" % "; ".join(r["problems"]))
    print("\nOVERALL: %s" % ("ALL CHECKS PASS" if ok_all else "SOME CHECKS FAILED"))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
