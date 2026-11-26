"""Bag tiers (phase 03 extension, economy rework 2026-11-26). Run build_all() inside Blender.

Rebuilt 2026-11-26 from the owner's reference sheets (Satchel / Ticket Pouch / Backpack / Tube / Sack and
the Ticket Wagon). Capacities are TEST values (pending items 13-16):
Satchel 25 (starter), Ticket Pouch 50, Backpack 100, Tube 200, Sack 400, Wagon 800.

Conventions (same as the tools):
- 1 unit = 1 stud. Blender (X, Y, Z) -> Roblox (X, Z, -Y); +Y is the wearer's facing direction.
- Origin = centre of an R6 torso's BACK face (torso: x -1..1, y 0..1, z -1..1; arms x +-1..2; legs
  z -3..-1; the right hand's bottom is at (1.5, 0.5, -1)). Bags hang toward -Y. Ground is z = -3.
- All six bags sample ONE shared 8 x 8 colour atlas (FWL_BagAtlas, 256 px), embedded in the GLB.
- The Wagon's four wheels are NOT in the GLB: in Roblox they are clones of the tools' Wheel mesh
  (r 0.45), on the axles listed in WAGON_WHEELS.
"""
import contextlib
import math
import os
import random

import bpy
from mathutils import Matrix, Vector

import build_tools as BTL
import fwl_kit as K
from fwl_kit import T, rot

ORDER = ["Satchel", "TicketPouch", "Backpack", "Tube", "Sack", "Wagon"]
CAPACITY_TEST = {"Satchel": 25, "TicketPouch": 50, "Backpack": 100, "Tube": 200, "Sack": 400, "Wagon": 800}

BAG_CELLS = [
    ("leather", "C77A3A"), ("leather_dk", "9A5A27"), ("brown", "7A4A26"), ("brown_dk", "553218"),
    ("gold", "F0C033"), ("gold_dk", "B98A16"), ("red", "DE3B33"), ("red_dk", "A82822"),
    ("cream", "F3E6C8"), ("cream_dk", "D8C7A2"), ("blue", "1F66E5"), ("blue_dk", "154CB4"),
    ("blue_lt", "4C8DF2"), ("purple", "7B33D9"), ("purple_dk", "5420A3"), ("orange", "F6A623"),
    ("orange_dk", "D2861A"), ("tan", "DCC08F"), ("tan_dk", "B99D6C"), ("cord", "D8312B"),
    ("teal", "1FC7B6"), ("teal_dk", "149587"), ("slot", "0E5A52"), ("yellow", "F7D21E"),
    ("yellow_dk", "D3AE10"), ("char", "3B4048"), ("char_dk", "2A2E34"), ("steel", "AEB5BD"),
    ("steel_dk", "858D96"), ("steel_lt", "DADFE4"), ("ink", "2B2420"), ("t_red", "E8473F"),
    ("t_orange", "F59A2B"), ("t_blue", "3E7FE8"), ("t_sky", "79BFF2"), ("t_white", "F8F5EE"),
    ("t_pink", "F08CA2"), ("t_yellow", "F7CF2E"), ("t_cyan", "3FD0D8"), ("t_cream", "F1E7CF"),
    ("t_stripe", "3A6FD8"),
]
BAG_GRID = 8
ATLAS_PATH = os.path.join(K.EXPORT_DIR, "FWL_BagAtlas.png")
MAT = None

WAGON_XC, WAGON_YC = 0.75, -2.45
WAGON_WHEEL_R = 0.45
WAGON_WHEELS = [(WAGON_XC + s * 1.08, y, -3 + WAGON_WHEEL_R) for y in (-1.55, -3.35) for s in (-1, 1)]
WAGON_GRIP = Vector((1.5, 0.45, -1.1))


def V(x, y, z):
    return Vector((x, y, z))


@contextlib.contextmanager
def bag_palette():
    saved = (K.GRID, K.NAMES, K.PALETTE)
    K.GRID, K.NAMES, K.PALETTE = BAG_GRID, [n for n, _ in BAG_CELLS], dict(BAG_CELLS)
    try:
        yield
    finally:
        K.GRID, K.NAMES, K.PALETTE = saved


# ---------------------------------------------------------------------------- shared pieces
def hsec(z, w, d, yc=0.0, k=0.35, seg=None, xc=0.0, radii=None):
    """Horizontal rounded rectangle (half sizes w, d) at height z, centred (xc, yc). CCW from above.
    seg -> ellipse; radii (list of seg scale factors) -> wavy ellipse."""
    if seg:
        return [V(xc + math.cos(2 * math.pi * i / seg) * w * (radii[i] if radii else 1),
                  yc + math.sin(2 * math.pi * i / seg) * d * (radii[i] if radii else 1), z) for i in range(seg)]
    c = min(w, d) * k
    pts = [(w, -d + c), (w, d - c), (w - c, d), (-w + c, d), (-w, d - c), (-w, -d + c), (-w + c, -d), (w - c, -d)]
    return [V(xc + x, yc + y, z) for x, y in pts]


def _frame(p, d):
    """Strap frame at p heading d: n points away from the torso, w across the strap."""
    q = V(max(-0.7, min(0.7, p.x)), max(0.3, min(0.7, p.y)), max(-0.8, min(0.8, p.z)))
    o = p - q
    if o.length < 1e-4:
        o = V(0, -1, 0)
    n = o - d * o.dot(d)
    if n.length < 1e-4:
        n = V(0, -1, 0)
    n.normalize()
    return d.cross(n).normalized(), n


def frame_matrix(p, d):
    d = Vector(d).normalized()
    wv, n = _frame(Vector(p), d)
    M = Matrix((wv, n, d)).transposed().to_4x4()
    M.translation = Vector(p)
    return M


def _tangent(pts, k):
    if k == 0:
        return (pts[1] - pts[0]).normalized()
    if k == len(pts) - 1:
        return (pts[-1] - pts[-2]).normalized()
    return ((pts[k + 1] - pts[k]).normalized() + (pts[k] - pts[k - 1]).normalized()).normalized()


def strap(b, pts, colour, w=0.2, t=0.06):
    """Flat strap along a polyline (rectangular section, thickness pointing away from the torso)."""
    pts = [Vector(p) for p in pts]
    secs = []
    for k, p in enumerate(pts):
        d = _tangent(pts, k)
        wv, n = _frame(p, d)
        secs.append([p + wv * w / 2 + n * t / 2, p - wv * w / 2 + n * t / 2, p - wv * w / 2 - n * t / 2,
                     p + wv * w / 2 - n * t / 2])
    b.loft(secs, colour)
    return pts


def on_strap(pts, seg, f):
    """(point, direction) a fraction f along segment seg of a strap polyline."""
    a, c = Vector(pts[seg]), Vector(pts[seg + 1])
    return a.lerp(c, f), (c - a).normalized()


def buckle(b, pts, seg, f, colour="gold", w=0.2, t=0.06, pad=None):
    p, d = on_strap(pts, seg, f)
    M = frame_matrix(p, d)
    if pad:  # coloured keeper pad under the buckle
        b.box((w * 0.82, t + 0.05, 0.26), pad, M @ T(0, 0, -0.2))
    b.box((w + 0.1, t + 0.07, 0.13), colour, M)


def shoulder_path(x, start, chest_end=0.15):
    """Back -> over the shoulder -> down the chest."""
    return [Vector(start), V(x, -0.07, 0.88), V(x, 0.15, 1.07), V(x, 0.85, 1.07), V(x, 1.07, 0.86),
            V(x, 1.07, chest_end)]


def ticket_pts(w, h):
    n = w * 0.17
    return [(-w / 2, -h / 2), (-n, -h / 2), (0, -h / 2 + n * 1.3), (n, -h / 2), (w / 2, -h / 2), (w / 2, h / 2),
            (n, h / 2), (0, h / 2 - n * 1.3), (-n, h / 2), (-w / 2, h / 2)]


def ticket(b, p, colour, yaw=0.0, tilt=0.0, roll=0.0, size=(0.32, 0.66), stripe=None, flat=False):
    """A ticket stub with V notches at both short ends. Standing: faces +-Y. Flat: faces +-Z."""
    w, h = size
    R = T(*p) @ rot(tilt, roll, yaw)
    if flat:
        b.prism(ticket_pts(w, h), 0.04, colour, R)
        if stripe:
            b.box((w * 0.2, h * 0.46, 0.03), stripe, R @ T(0, 0, 0.026))
    else:
        b.prism(ticket_pts(w, h), 0.04, colour, R @ rot(90))
        if stripe:
            b.box((w * 0.2, 0.03, h * 0.46), stripe, R @ T(0, -0.026, -h * 0.04))


def ticket_bunch(b, base, specs, spread, seed, size=(0.32, 0.66)):
    """specs: [(colour, stripe or None)]. Stubs rise from `base`, fanned across X."""
    rnd = random.Random(seed)
    n = len(specs)
    for i, (c, s) in enumerate(specs):
        t = (i + 0.5) / n - 0.5
        ticket(b, (base.x + t * spread * 2, base.y + rnd.uniform(-0.04, 0.04), base.z + rnd.uniform(-0.06, 0.06)), c,
               yaw=rnd.uniform(-14, 14), tilt=rnd.uniform(-10, 10), roll=t * 32 + rnd.uniform(-6, 6), size=size,
               stripe=s)


# ---------------------------------------------------------------------------- 1 Satchel (25)
def satchel(col):
    b = K.Builder("Bag_Satchel")
    xc, yc, zc = -0.25, -0.27, -0.5
    top = zc + 0.36
    secs = [hsec(zc - 0.44, 0.44, 0.19, yc, k=0.35, xc=xc), hsec(zc - 0.38, 0.52, 0.25, yc, k=0.3, xc=xc),
            hsec(top, 0.52, 0.25, yc, k=0.3, xc=xc)]
    b.loft(secs, "leather", cap_colors=("leather_dk", "leather_dk"))
    # flap over the outer half of the top and down the outer face, gold clasp at its edge
    b.box((1.1, 0.36, 0.08), "brown", T(xc, yc - 0.1, top + 0.045))
    b.box((1.1, 0.08, 0.52), "brown", T(xc, yc - 0.3, top - 0.2))
    b.box((0.24, 0.06, 0.22), "gold", T(xc, yc - 0.355, top - 0.42))
    b.box((0.12, 0.05, 0.1), "gold_dk", T(xc, yc - 0.39, top - 0.42))
    ticket_bunch(b, V(xc, yc + 0.12, top + 0.2), [("t_red", "t_white"), ("t_orange", None), ("t_blue", None)], 0.24,
                 seed=1, size=(0.3, 0.6))
    # one long strap: bag right -> up the back -> right shoulder -> across the chest -> left hip -> bag left
    pts = strap(b, [V(xc + 0.55, yc + 0.02, top - 0.06), V(0.62, -0.07, 0.86), V(0.62, 0.15, 1.07),
                    V(0.62, 0.85, 1.07), V(0.5, 1.07, 0.85), V(-0.7, 1.07, -0.62), V(-1.03, 0.5, -0.72),
                    V(-1.0, -0.08, -0.5), V(xc - 0.55, yc + 0.02, top - 0.06)], "brown_dk", w=0.19)
    buckle(b, pts, 0, 0.18, w=0.19)
    buckle(b, pts, 0, 0.75, w=0.19)
    buckle(b, pts, 7, 0.7, w=0.19)
    return [b.finish(col, material=MAT)]


# ---------------------------------------------------------------------------- 2 Ticket Pouch (50)
def ticket_pouch(col):
    b = K.Builder("Bag_TicketPouch")
    yc, zc = -0.42, -0.35
    bot, top = zc - 0.5, zc + 0.48
    secs = [hsec(bot, 0.42, 0.26, yc, k=0.25), hsec(bot + 0.06, 0.48, 0.31, yc, k=0.25),
            hsec(top, 0.62, 0.38, yc, k=0.2)]
    b.loft(secs, "red", cap_colors=("red_dk", "ink"))
    # cream rim around the open top
    for s in (-1, 1):
        b.box((1.36, 0.13, 0.15), "cream", T(0, yc + s * 0.385, top + 0.05))
        b.box((0.13, 0.9, 0.15), "cream", T(s * 0.625, yc, top + 0.05))
    # cream handle plate on the outer face
    hy, hz = yc - 0.37, zc - 0.12
    for s in (-1, 1):
        b.box((0.56, 0.08, 0.075), "cream", T(0, hy, hz + s * 0.11))
        b.box((0.075, 0.08, 0.3), "cream", T(s * 0.25, hy, hz))
    ticket_bunch(b, V(0.0, yc + 0.05, top + 0.18),
                 [("t_orange", None), ("t_white", "t_stripe"), ("t_pink", None), ("t_red", None)], 0.36, seed=2)
    for x in (-0.45, 0.45):
        pts = strap(b, shoulder_path(x, V(x, yc + 0.3, top - 0.05)), "cream", w=0.2)
        buckle(b, pts, 1, 0.55, colour="cream_dk", pad="red")
        buckle(b, pts, 4, 0.5, colour="cream_dk", pad="red")
    return [b.finish(col, material=MAT)]


# ---------------------------------------------------------------------------- 3 Backpack (100)
def backpack(col):
    b = K.Builder("Bag_Backpack")
    yc = -0.42
    secs = [hsec(-1.02, 0.66, 0.3, yc, k=0.5), hsec(-0.92, 0.78, 0.4, yc, k=0.45), hsec(0.55, 0.8, 0.42, yc, k=0.45),
            hsec(0.82, 0.7, 0.36, yc, k=0.5), hsec(0.95, 0.5, 0.26, yc, k=0.55)]
    b.loft(secs, "blue", cap_colors=("blue_dk", "ink"))
    # big front pocket with a yellow zip and pull
    py = yc - 0.4
    psecs = [hsec(z, w, 0.16, py - 0.04, k=0.45) for z, w in ((-0.94, 0.56), (-0.86, 0.64), (-0.12, 0.64), (-0.04, 0.56))]
    b.loft(psecs, "blue_lt", cap_colors=("blue_dk", "blue_dk"))
    b.box((1.04, 0.06, 0.07), "yellow", T(0, py - 0.21, -0.24))
    b.box((0.08, 0.05, 0.28), "yellow", T(0.4, py - 0.23, -0.4))
    # side pocket (right)
    b.box((0.18, 0.5, 0.6), "blue_dk", T(0.86, yc - 0.02, -0.6))
    ticket_bunch(b, V(-0.08, yc, 1.02), [("t_sky", None), ("t_red", "t_white"), ("t_yellow", None)], 0.24, seed=4,
                 size=(0.34, 0.72))
    for x in (-0.5, 0.5):
        pts = strap(b, shoulder_path(x, V(x, -0.06, 0.6), chest_end=-0.2), "blue", w=0.24, t=0.08)
        buckle(b, pts, 4, 0.6, colour="yellow", w=0.24, t=0.08)
    return [b.finish(col, material=MAT)]


# ---------------------------------------------------------------------------- 4 Tube (200)
def tube(col):
    b = K.Builder("Bag_Tube")
    yc, zc, r, half = -0.53, -0.3, 0.48, 1.18
    seg = 16

    def ring(x, rr):
        return [V(x, yc + math.cos(2 * math.pi * i / seg) * rr, zc + math.sin(2 * math.pi * i / seg) * rr)
                for i in range(seg)]

    b.loft([ring(-half, r), ring(half, r)], "purple", caps=(False, False))
    for s in (-1, 1):  # rounded orange end caps
        prof = [(half - 0.02, r + 0.02), (half + 0.08, r + 0.03), (half + 0.16, r - 0.02), (half + 0.2, r - 0.14)]
        secs = [ring(s * x, rr) for x, rr in prof]
        b.loft(secs, "orange", caps=(True, True), cap_colors=("orange_dk", "orange"))
        b.cyl(V(s * (half - 0.26), yc, zc), V(s * (half - 0.1), yc, zc), r + 0.025, 16, "purple_dk")
    # slot on top, tickets out of it
    b.box((0.9, 0.22, 0.06), "ink", T(0, yc, zc + r - 0.005))
    ticket_bunch(b, V(0, yc, zc + r + 0.22), [("t_yellow", "t_white"), ("t_red", "t_white"), ("t_orange", None)], 0.26,
                 seed=5, size=(0.32, 0.66))
    for x in (-0.45, 0.45):
        pts = strap(b, shoulder_path(x, V(x, yc + 0.32, zc + 0.3)), "brown", w=0.2)
        buckle(b, pts, 0, 0.45)
    return [b.finish(col, material=MAT)]


# ---------------------------------------------------------------------------- 5 Sack (400)
def sack(col):
    b = K.Builder("Bag_Sack")
    yc = -0.62
    seg = 14
    ruffle = [1.0 if i % 2 == 0 else 0.8 for i in range(seg)]
    prof = [(-1.45, 0.42, 0.32, None), (-1.32, 0.74, 0.54, None), (-1.0, 0.86, 0.62, None), (-0.6, 0.84, 0.6, None),
            (-0.1, 0.66, 0.48, None), (0.25, 0.32, 0.25, None), (0.38, 0.2, 0.17, None), (0.5, 0.3, 0.25, ruffle),
            (0.62, 0.42, 0.34, ruffle)]
    secs = [hsec(z, w, d, yc, seg=seg, radii=rr) for z, w, d, rr in prof]
    for f in b.loft(secs, "tan", cap_colors=("tan_dk", "ink")):
        if f.calc_center_median().z > 0.4 and abs(f.normal.z) < 0.95:
            b._paint([f], "tan_dk" if f.index % 2 else "tan")
    # red cord at the neck with a knot and two hanging tails
    BTL.torus(b, T(0, yc, 0.38) @ Matrix.Diagonal((1.0, 0.85, 1.0, 1.0)), 0.21, 0.06, 12, 6, "cord")
    b.box((0.16, 0.12, 0.14), "cord", T(0.04, yc - 0.21, 0.37))
    b.tube([V(0.02, yc - 0.24, 0.34), V(0.0, yc - 0.33, 0.12), V(-0.04, yc - 0.43, -0.12)], 0.045, 6, "cord")
    b.tube([V(0.08, yc - 0.24, 0.34), V(0.15, yc - 0.32, 0.15), V(0.2, yc - 0.4, -0.04)], 0.045, 6, "cord")
    ticket_bunch(b, V(0.0, yc, 0.86), [("t_red", "t_white"), ("t_white", "t_stripe"), ("t_red", None)], 0.18, seed=6,
                 size=(0.3, 0.62))
    # cream patch with a red bar, low on the outer face
    patch = [(-0.24, -0.11), (0.24, -0.11), (0.28, -0.07), (0.28, 0.07), (0.24, 0.11), (-0.24, 0.11), (-0.28, 0.07),
             (-0.28, -0.07)]
    b.prism(patch, 0.14, "cream", T(0, yc - 0.6, -0.95) @ rot(90))
    b.prism([(x * 0.62, y * 0.45) for x, y in patch], 0.14, "red", T(0, yc - 0.66, -0.95) @ rot(90))
    # single strap over the left shoulder
    pts = strap(b, shoulder_path(-0.55, V(-0.3, yc + 0.32, 0.1), chest_end=-0.1), "tan", w=0.22)
    buckle(b, pts, 0, 0.6)
    return [b.finish(col, material=MAT)]


# ---------------------------------------------------------------------------- 6 Ticket Wagon (800)
def wagon(col):
    b = K.Builder("Bag_Wagon")
    xc, yc = WAGON_XC, WAGON_YC
    z0, z1 = -2.25, -1.15
    secs = [hsec(z0, 0.84, 1.14, yc, k=0.12, xc=xc), hsec(z0 + 0.06, 0.88, 1.18, yc, k=0.12, xc=xc),
            hsec(z1, 0.98, 1.3, yc, k=0.1, xc=xc)]
    b.loft(secs, "teal", cap_colors=("teal_dk", "t_cream"))

    def half_w(z):
        return 0.88 + 0.10 * (z - (z0 + 0.06)) / (z1 - z0 - 0.06)

    def half_d(z):
        return 1.18 + 0.12 * (z - (z0 + 0.06)) / (z1 - z0 - 0.06)

    aw = math.degrees(math.atan2(0.10, z1 - z0 - 0.06))
    ad = math.degrees(math.atan2(0.12, z1 - z0 - 0.06))
    for z in (-1.95, -1.7, -1.45):
        for s in (-1, 1):
            b.box((0.05, 1.8, 0.13), "slot", T(xc + s * (half_w(z) + 0.004), yc, z) @ rot(0, s * aw, 0))
            b.box((1.35, 0.05, 0.13), "slot", T(xc, yc + s * (half_d(z) + 0.004), z) @ rot(-s * ad, 0, 0))
    # thick yellow rim
    for s in (-1, 1):
        b.box((0.18, 2.8, 0.2), "yellow", T(xc + s * 1.0, yc, z1 + 0.06))
        b.box((2.18, 0.18, 0.2), "yellow", T(xc, yc + s * 1.32, z1 + 0.06))
    # heap of tickets
    mound = [hsec(z1 - 0.02, 0.96, 1.28, yc, k=0.4, xc=xc), hsec(z1 + 0.1, 0.78, 1.02, yc, k=0.5, xc=xc),
             hsec(z1 + 0.17, 0.4, 0.55, yc, k=0.5, xc=xc)]
    b.loft(mound, "t_cream", caps=(False, True))
    rnd = random.Random(9)
    cols = ["t_white", "t_yellow", "t_red", "t_cyan", "t_white", "t_red", "t_yellow", "t_cyan", "t_white"]
    for i, c in enumerate(cols):
        a = 2 * math.pi * i / len(cols) + rnd.uniform(-0.25, 0.25)
        rr = 0.12 + (i % 3) * 0.3
        p = (xc + math.cos(a) * rr * 0.75, yc + math.sin(a) * rr * 1.05, z1 + 0.24 - rr * 0.13 + i * 0.012)
        ticket(b, p, c, yaw=rnd.uniform(0, 180), tilt=rnd.uniform(-5, 5), roll=rnd.uniform(-5, 5),
               size=(0.5, 1.04), flat=True)
    # grey chassis: rails, axle beams, axles
    for s in (-1, 1):
        b.box((0.12, 2.5, 0.12), "steel", T(xc + s * 0.6, yc, z0 - 0.08))
    for x, y, z in WAGON_WHEELS[::2]:
        b.box((1.5, 0.16, 0.14), "steel", T(xc, y, z0 - 0.16))
        b.cyl(V(xc - 1.0, y, z), V(xc + 1.0, y, z), 0.06, 8, "steel_dk")
        for s in (-1, 1):
            b.box((0.12, 0.14, 0.32), "steel_dk", T(xc + s * 0.82, y, (z + z0 - 0.16) / 2))
    # pull handle: hinge at the front of the chassis, bar up to a loop grip at the right hand
    hinge = V(xc, yc + 1.3 + 0.1, z0 - 0.16)
    b.box((0.32, 0.26, 0.2), "char", T(hinge.x, hinge.y - 0.08, hinge.z))
    b.cyl(hinge + V(-0.2, 0, 0), hinge + V(0.2, 0, 0), 0.08, 10, "steel_lt")
    d = (WAGON_GRIP - hinge).normalized()
    u = Vector((0, 0, 1)).cross(d).normalized()
    near = WAGON_GRIP - d * 0.3
    far = WAGON_GRIP + d * 0.12
    b.cyl(hinge, near, 0.065, 8, "char")
    for a, c in ((near - u * 0.2, near + u * 0.2), (far - u * 0.2, far + u * 0.2), (near - u * 0.2, far - u * 0.2),
                 (near + u * 0.2, far + u * 0.2)):
        b.cyl(a - (c - a).normalized() * 0.05, c + (c - a).normalized() * 0.05, 0.07, 8, "char")
    return [b.finish(col, material=MAT)]


BUILDERS = [("Satchel", satchel), ("TicketPouch", ticket_pouch), ("Backpack", backpack), ("Tube", tube),
            ("Sack", sack), ("Wagon", wagon)]


def build_all(spacing=4.5, main_scene="Phase03"):
    global MAT
    main = bpy.data.scenes[main_scene]
    root = K.collection("Bags", main.collection)
    for c in list(root.children):  # drop the previous bags
        K.clear_collection(c)
        bpy.data.collections.remove(c)
    made = {}
    with bag_palette():
        img = K.build_palette_image(dict(BAG_CELLS), "FWL_BagAtlas", ATLAS_PATH)
        MAT = K.textured_material("FWL_BagAtlas", img)
        for i, (bag_id, fn) in enumerate(BUILDERS):
            col = K.collection("Bag_%02d_%s" % (i + 1, bag_id), root)
            K.clear_collection(col)
            objs = fn(col)
            for o in objs:
                o.location = V(i * spacing, 20, 3)
            made[bag_id] = objs
    # preview-only wagon wheels (shared tools Wheel mesh, not exported)
    wheel = bpy.data.meshes.get("Wheel")
    if wheel:
        wcol = bpy.data.collections["Bag_06_Wagon"]
        base = made["Wagon"][0].location
        k = WAGON_WHEEL_R / 0.75
        for i, p in enumerate(WAGON_WHEELS):
            w = bpy.data.objects.new("Wagon_Wheel%d" % (i + 1), wheel)
            wcol.objects.link(w)
            w.scale = (k, k, k)
            w.location = base + Vector(p)
    return made


def report(made):
    out = []
    for bag_id, objs in made.items():
        n = sum(K.tris(o) for o in objs)
        lo, hi = K.world_bounds(objs)
        s = hi - lo
        out.append(f"{bag_id}: {n} tris, size {s.x:.2f} x {s.y:.2f} x {s.z:.2f}, "
                   f"z {lo.z - objs[0].location.z:.2f}..{hi.z - objs[0].location.z:.2f}")
    return "\n".join(out)
