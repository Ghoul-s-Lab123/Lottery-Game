"""The ten tools (phase 03). Run build_all() inside Blender.

Every object: origin at the main hand grip (handhelds) or ground centre (walk-behind / vehicle),
+Y = working end / forward, +Z = up. One shared palette texture (fwl_kit.PALETTE_PATH).
Moving parts (jaws, brushes, wheels, steering wheel) are separate objects with origins on their axes.
"""
import math

import bpy
from mathutils import Matrix, Vector

import fwl_kit as K
from fwl_kit import T, rot

# prism helpers: profile drawn in (Y, Z), extruded along X  /  profile in (X, Z), extruded along Y
MYZ = Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
MXZ = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))


def V(x, y, z):
    return Vector((x, y, z))


def dir_deg(pitch_deg):
    """Unit vector going back (-Y) and up, `pitch_deg` above horizontal."""
    a = math.radians(pitch_deg)
    return V(0, -math.cos(a), math.sin(a))


# ============================================================================ 1 Ticket Grabber
def ticket_grabber(col):
    hinge = V(0, 2.8, 0.62)
    b = K.Builder("TicketGrabber_Body")
    b.box((0.3, 0.36, 0.95), "char", T(0, -0.06, 0) @ rot(-14), chamfer=0.08, chamfer_mode="Z")
    b.box((0.34, 0.4, 0.1), "yellow", T(0, -0.18, -0.5) @ rot(-14), chamfer=0.03, chamfer_mode="Z")  # butt cap
    b.box((0.42, 1.15, 0.46), "teal", T(0, 0.18, 0.62), chamfer=0.07)
    b.box((0.13, 0.16, 0.4), "yellow", T(0, 0.33, 0.22) @ rot(-12), chamfer=0.03, chamfer_mode="Z")
    b.cyl((0, 0.7, 0.62), (0, 2.6, 0.62), 0.07, 6, "steel", caps=(False, False))
    b.cyl((0, 2.5, 0.62), (0, 2.86, 0.62), 0.2, 6, "teal")
    b.cyl((-0.25, 2.74, 0.62), (0.25, 2.74, 0.62), 0.1, 8, "steel_lt")
    body = b.finish(col)

    jaw = [(0.0, 0.02), (0.26, 0.34), (0.76, 0.42), (0.94, 0.28), (0.96, 0.0), (0.76, 0.0), (0.72, 0.2),
           (0.34, 0.14), (0.1, -0.08)]
    up = K.Builder("TicketGrabber_JawUpper")
    up.prism(jaw, 0.24, "yellow", MYZ)
    lo = K.Builder("TicketGrabber_JawLower")
    lo.prism([(y, -z) for y, z in jaw], 0.32, "yellow", MYZ)  # wider: no coplanar sides with the upper jaw
    j1 = up.finish(col, location=hinge)
    j2 = lo.finish(col, location=hinge)
    j1.parent = j2.parent = body
    return [body, j1, j2]


# ============================================================================ 2 Dustpan Scoop
def dustpan_scoop(col):
    b = K.Builder("DustpanScoop")
    b.prism([(-0.78, -0.75), (0.78, -0.75), (0.98, 0.75), (-0.98, 0.75)], 0.08, "teal", T(0, 0, 0.07))
    ang = math.degrees(math.atan2(0.2, 1.5))
    for s in (-1, 1):
        M = T(s * 0.88, 0, 0) @ rot(0, 0, -s * ang) @ MYZ
        b.prism([(-0.76, 0.06), (0.76, 0.06), (0.76, 0.18), (-0.76, 0.64)], 0.08, "teal", M)
    b.box((1.66, 0.08, 0.66), "teal", T(0, -0.79, 0.37))
    b.prism([(0.68, 0.0), (1.06, 0.0), (1.0, 0.06), (0.68, 0.13)], 2.02, "yellow", MYZ)  # front lip
    d = dir_deg(32)
    p0 = V(0, -0.8, 0.5)
    p1 = p0 + d * 0.6
    p2 = p1 + d * 1.0
    b.cyl(p0, p1, 0.21, 4, "teal", r2=0.14, phase=math.pi / 4)
    b.cyl(p1 - d * 0.05, p2, 0.15, 8, "char", caps=(False, True))
    b.cyl(p2, p2 + d * 0.14, 0.17, 8, "yellow")
    b.offset(p1 + d * 0.5)
    return [b.finish(col)]


# ============================================================================ 3 Hand Rake
def hand_rake(col):
    b = K.Builder("HandRake")
    b.box((1.75, 0.36, 0.3), "teal", T(0, 0, 0), chamfer=0.06)
    tine = [(-0.12, 0.05), (0.12, 0.05), (0.15, -0.35), (0.3, -0.7), (0.22, -0.82), (0.03, -0.52), (-0.1, -0.3)]
    for x in (-0.68, -0.34, 0.0, 0.34, 0.68):
        b.prism(tine, 0.2, "yellow", T(x, 0, 0) @ MYZ)
    d = dir_deg(35)
    p0 = V(0, -0.05, 0.05)
    p1 = p0 + d * 0.62
    p2 = p1 + d * 1.05
    b.cyl(p0, p1, 0.2, 4, "teal", r2=0.13, phase=math.pi / 4)
    b.cyl(p1 - d * 0.05, p2, 0.15, 8, "char", caps=(False, True))
    b.cyl(p2, p2 + d * 0.14, 0.17, 8, "yellow")
    b.offset(p1 + d * 0.52)
    return [b.finish(col)]


# ============================================================================ 4 Push Broom
def push_broom(col):
    b = K.Builder("PushBroom")
    b.box((3.0, 0.56, 0.32), "teal", T(0, 0, 0.62), chamfer=0.06)
    gap = 0.05
    w = (2.9 - 3 * gap) / 4
    for i in range(4):
        x = -1.45 + w / 2 + i * (w + gap)
        b.prism([(-0.24, 0.49), (0.24, 0.49), (0.33, 0.0), (-0.33, 0.0)], w, "char_dk", T(x, 0, 0) @ MYZ)
    d = dir_deg(50)
    p0 = V(0, -0.04, 0.82)
    b.box((0.42, 0.46, 0.2), "yellow", T(0, -0.04, 0.84), chamfer=0.05)  # bracket
    b.cyl(p0 + d * 0.05, p0 + d * 0.42, 0.16, 6, "yellow", r2=0.11)  # socket
    p1 = p0 + d * 3.3
    p2 = p1 + d * 0.85
    b.cyl(p0 + d * 0.3, p1, 0.08, 6, "steel", caps=(False, False))
    b.cyl(p1, p2, 0.115, 8, "char", caps=(True, False))
    b.cyl(p2, p2 + d * 0.13, 0.13, 8, "yellow")
    b.offset(p1 + d * 0.42)
    return [b.finish(col)]


# ============================================================================ 5 Shovel
def shovel(col):
    """Built upright (blade at the bottom, face toward -Y), then laid along +Y with the face up."""
    b = K.Builder("Shovel")
    blade = [(-0.62, 0.14), (-0.48, 0.0), (0.48, 0.0), (0.62, 0.14), (0.62, 1.22), (0.22, 1.42), (-0.22, 1.42),
             (-0.62, 1.22)]
    b.prism(blade, 0.08, "yellow", MXZ)
    for s in (-1, 1):  # raised side rims make it read as a scoop
        b.prism([(0.16, 0.0), (1.22, 0.0), (1.2, 0.18), (0.26, 0.2)], 0.09, "yellow_dk",
                T(s * 0.6, 0.0, 0) @ Matrix(((0, 0, 1, 0), (0, -1, 0, 0), (1, 0, 0, 0), (0, 0, 0, 1))))
    y = 0.2  # shaft line sits behind the blade; the socket bridges the gap
    b.cyl((0, y, 0.95), (0, y, 1.75), 0.17, 6, "teal", r2=0.12)
    b.cyl((0, y, 1.65), (0, y, 4.05), 0.075, 6, "steel", caps=(False, False))
    b.cyl((0, y, 3.95), (0, y, 4.3), 0.13, 6, "teal")
    for s in (-1, 1):  # D-grip sides: flare out, then rise to the bar
        b.tube([(s * 0.06, y, 4.22), (s * 0.34, y, 4.5), (s * 0.36, y, 4.84)], 0.065, 6, "yellow")
    b.cyl((-0.44, y, 4.88), (0.44, y, 4.88), 0.095, 8, "yellow")
    b.offset(V(0, y, 4.88))
    import bmesh
    # blade (-Z) -> +Y, blade face (-Y) -> +Z
    bmesh.ops.transform(b.bm, matrix=rot(0, 180, 0) @ rot(90), verts=b.bm.verts)
    return [b.finish(col)]


# ============================================================================ shared helpers (6-10)
def rrect_pts(M, w, h, k=0.3):
    """Rounded (chamfered) rectangle, half sizes w/h, in the local XZ plane, CCW; 8 points when smoothing."""
    if not K.SMOOTH:
        return [M @ V(sx * w, 0, sz * h) for sx, sz in ((1, 1), (-1, 1), (-1, -1), (1, -1))]
    c = min(w, h) * k
    loc = [(w, h - c), (w - c, h), (-w + c, h), (-w, h - c), (-w, -h + c), (-w + c, -h), (w - c, -h), (w, -h + c)]
    return [M @ V(x, 0, z) for x, z in loc]


def rect_sec(b, y, w, h, zc=0.0, x=0.0):
    """Axis-aligned (rounded) rectangle section in the XZ plane at depth y (half sizes w, h)."""
    return rrect_pts(T(x, y, zc), w, h)


def oct_sec(b, y, w, h, zc=0.0):
    return b.ring_pts(T(0, y, zc), w, h, K.segs(8))


def axis_sec(b, p, d, w, h, seg=4):
    """Section perpendicular to direction d at point p (width along world X)."""
    M = K.look_matrix(p, d) @ rot(90)
    return rrect_pts(M, w, h) if seg == 4 else b.ring_pts(M, w, h, seg)


def hollow_mouth(b, outer, inner_front, inner_back, color, inner_color="char_dk"):
    """Closed cup: outer band + front rim + inner throat + throat floor (normals recalc reliably)."""
    faces = b.loft([outer[0], outer[1], inner_front, inner_back], color, caps=(True, True))
    n = len(inner_front)
    throat = faces[2 * n:3 * n] + faces[-1:]  # third band + end cap
    b._paint(throat, inner_color)
    return faces


def torus(b, M, R, r, n, m, color):
    secs = []
    for i in range(n):
        a = 2 * math.pi * i / n
        c = Vector((math.cos(a) * R, math.sin(a) * R, 0))
        radial = Vector((math.cos(a), math.sin(a), 0))
        secs.append([M @ (c + radial * math.cos(2 * math.pi * k / m + math.pi / m) * r
                          + Vector((0, 0, 1)) * math.sin(2 * math.pi * k / m + math.pi / m) * r) for k in range(m)])
    before = set(b.bm.faces)
    rings = [[b.bm.verts.new(p) for p in s] for s in secs]
    for i in range(n):
        A, B = rings[i], rings[(i + 1) % n]
        for k in range(m):
            j = (k + 1) % m
            b.bm.faces.new((A[k], A[j], B[j], B[k]))
    new = b._new_faces(before)
    import bmesh
    bmesh.ops.recalc_face_normals(b.bm, faces=new)
    b._paint(new, color)


def fender(b, x, yc, zc, R0, R1, width, color, seg=6):
    """Arched band over a wheel (profile in Y/Z, extruded along X)."""
    outer = [(yc + math.cos(math.pi * i / seg) * R1, zc + math.sin(math.pi * i / seg) * R1) for i in range(seg + 1)]
    inner = [(yc + math.cos(math.pi * i / seg) * R0, zc + math.sin(math.pi * i / seg) * R0) for i in range(seg + 1)]
    b.prism(outer + list(reversed(inner)), width, color, T(x, 0, 0) @ MYZ)


def wheel_mesh(col, name="Wheel", r=0.75, w=0.42, seg=16):
    """Shared wheel (axle along X, origin on the axle). Instances scale it per vehicle."""
    if bpy.data.objects.get(name) and bpy.data.objects[name].users_collection[0] == col:
        return bpy.data.objects[name]
    b = K.Builder(name)
    c = 0.07
    secs = []
    for x, rr in ((-w / 2, r * 0.78), (-w / 2 + c, r), (w / 2 - c, r), (w / 2, r * 0.78)):
        M = T(x, 0, 0) @ rot(0, 90, 0)
        secs.append([M @ Vector((math.cos(math.pi / seg + 2 * math.pi * i / seg) * rr,
                                 math.sin(math.pi / seg + 2 * math.pi * i / seg) * rr, 0)) for i in range(seg)])
    b.loft(secs, "char_dk", caps=(True, True))
    b.cyl((-w / 2 - 0.035, 0, 0), (w / 2 + 0.035, 0, 0), r * 0.46, 8, "steel_lt")
    return b.finish(col)


# ============================================================================ 6 Handheld Vacuum
def handheld_vacuum(col):
    b = K.Builder("HandheldVacuum")
    b.loft([oct_sec(b, -1.0, 0.36, 0.38), oct_sec(b, -0.85, 0.5, 0.52), oct_sec(b, 0.2, 0.5, 0.52),
            oct_sec(b, 0.95, 0.4, 0.32, -0.12)], "teal", caps=(True, True))
    hollow_mouth(b, [rect_sec(b, 0.82, 0.4, 0.27, -0.13), rect_sec(b, 1.62, 0.52, 0.19, -0.22)],
                 rect_sec(b, 1.62, 0.4, 0.1, -0.22), rect_sec(b, 1.35, 0.34, 0.1, -0.19), "yellow")
    b.tube([(0, -0.66, 0.4), (0, -0.52, 0.93), (0, 0.12, 0.96), (0, 0.3, 0.42)], 0.14, 6, "char")
    b.box((0.13, 0.16, 0.08), "yellow", T(0, 0.02, 0.86), chamfer=0.03)  # thumb button under the bar
    for s in (-1, 1):
        b.box((0.05, 0.52, 0.36), "vent", T(s * 0.515, -0.38, 0.02))
    b.offset(V(0, -0.2, 0.96))
    return [b.finish(col)]


# ============================================================================ 7 Leaf Blower
def leaf_blower(col):
    b = K.Builder("LeafBlower")
    b.loft([oct_sec(b, -0.95, 0.44, 0.48), oct_sec(b, -0.78, 0.6, 0.64), oct_sec(b, 0.15, 0.6, 0.64),
            oct_sec(b, 0.48, 0.42, 0.42, -0.02)], "teal", caps=(True, True))
    b.loft([oct_sec(b, 0.36, 0.45, 0.45, -0.02), oct_sec(b, 0.66, 0.45, 0.45, -0.03)], "yellow", caps=(True, True))
    b.loft([oct_sec(b, 0.6, 0.34, 0.34, -0.03), oct_sec(b, 2.56, 0.24, 0.24, -0.2)], "teal", caps=(True, True))
    hollow_mouth(b, [rect_sec(b, 2.5, 0.3, 0.28, -0.21), rect_sec(b, 3.2, 0.4, 0.22, -0.28)],
                 rect_sec(b, 3.2, 0.3, 0.13, -0.28), rect_sec(b, 2.95, 0.26, 0.13, -0.26), "yellow")
    b.tube([(0, -0.62, 0.52), (0, -0.5, 1.17), (0, 0.06, 1.2), (0, 0.22, 0.56)], 0.15, 6, "char")
    for s in (-1, 1):
        b.box((0.05, 0.56, 0.42), "vent", T(s * 0.615, -0.32, 0.0))
    b.offset(V(0, -0.22, 1.19))
    return [b.finish(col)]


# ============================================================================ 8 Shop Vac
def shop_vac(col):
    b = K.Builder("ShopVac")
    up = rot(90)  # ring_pts' XZ plane -> XY plane

    def hsec(z, r, seg=16):
        return b.ring_pts(T(0, 0, z) @ up, r, r, seg)

    b.loft([hsec(0.3, 0.86), hsec(0.42, 0.92), hsec(1.74, 1.0)], "teal", caps=(True, True))
    b.loft([hsec(1.7, 1.08), hsec(1.86, 1.08)], "steel", caps=(True, True))
    b.loft([hsec(1.84, 1.02), hsec(2.18, 0.97), hsec(2.4, 0.62)], "char", caps=(True, True))
    b.tube([(-0.44, 0, 2.28), (-0.44, 0, 2.82), (0.44, 0, 2.82), (0.44, 0, 2.28)], 0.1, 6, "yellow")
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.cyl((sx * 0.68, sy * 0.52, 0.28), (sx * 0.92, sy * 0.52, 0.28), 0.28, 8, "char_dk")
            b.cyl((sx * 0.9, sy * 0.52, 0.28), (sx * 0.95, sy * 0.52, 0.28), 0.13, 6, "steel_lt")
    b.cyl((0, 0.92, 1.25), (0, 1.3, 1.25), 0.22, 8, "steel_dk")
    # ribbed hose along a quadratic curve
    p0, p1, p2 = V(0, 1.25, 1.25), V(0, 2.45, 1.45), V(0, 2.75, 0.62)
    pts, radii = [], []
    for i in range(11):
        t = i / 10
        pts.append(p0 * (1 - t) ** 2 + p1 * 2 * t * (1 - t) + p2 * t * t)
        radii.append(0.16 if i % 2 == 0 else 0.13)
    b.tube(pts, 0.15, 8, "steel_dk", radii=radii)
    d = (V(0, 3.15, 0.12) - V(0, 2.72, 0.66)).normalized()
    a, f = V(0, 2.68, 0.7), V(0, 3.2, 0.12)
    hollow_mouth(b, [axis_sec(b, a, d, 0.2, 0.17), axis_sec(b, f, d, 0.72, 0.14)],
                 axis_sec(b, f, d, 0.62, 0.07), axis_sec(b, f - d * 0.22, d, 0.5, 0.07), "yellow")
    b.offset(V(0, 0, 2.82))
    return [b.finish(col)]


# ============================================================================ 9 Rotary Sweeper
def rotary_sweeper(col):
    b = K.Builder("RotarySweeper_Body")
    b.box((2.5, 2.6, 0.16), "steel_dk", T(0, -0.1, 0.46))
    b.prism([(-1.2, 0.5), (0.9, 0.5), (0.9, 0.98), (0.55, 1.45), (-1.0, 1.52), (-1.2, 1.3)], 2.6, "teal", MYZ)
    b.box((2.0, 1.25, 0.1), "teal_lt", T(0, -0.25, 1.52) @ rot(-2), chamfer=0.03)  # raised hood panel
    for s in (-1, 1):
        b.box((0.05, 1.9, 0.36), "teal_dk", T(s * 1.315, -0.15, 0.74))
        b.box((0.12, 0.5, 0.46), "teal_dk", T(s * 1.33, -0.9, 0.75))  # wheel mounts
    b.box((3.6, 0.78, 0.44), "yellow", T(0, 1.15, 0.63), chamfer=0.1)  # brush cover / bumper
    for s in (-1, 1):
        b.tube([(s * 0.95, -1.0, 1.2), (s * 0.95, -1.4, 1.8), (s * 0.95, -2.35, 3.2)], 0.085, 6, "steel")
    b.cyl((-1.12, -2.38, 3.24), (1.12, -2.38, 3.24), 0.13, 8, "char")
    body = b.finish(col)

    br = K.Builder("RotarySweeper_Brush")
    br.cyl((0, 0, 0.47 - 0.45), (0, 0, 0.3 - 0.45), 0.3, 10, "char")
    br.cyl((0, 0, 0.33 - 0.45), (0, 0, 0.02 - 0.45), 0.6, 12, "yellow", r2=0.78)
    brush_l = br.finish(col, location=(-0.85, 1.25, 0.45))
    brush_r = bpy.data.objects.new("RotarySweeper_BrushR", brush_l.data)
    col.objects.link(brush_r)
    brush_l.name = "RotarySweeper_BrushL"
    brush_r.location = (0.85, 1.25, 0.45)

    wheel = wheel_mesh(col)
    wl = bpy.data.objects.new("RotarySweeper_WheelL", wheel.data)
    wr = bpy.data.objects.new("RotarySweeper_WheelR", wheel.data)
    for o, x in ((wl, -1.62), (wr, 1.62)):
        col.objects.link(o)
        o.location = (x, -0.9, 0.75)
    parts = [brush_l, brush_r, wl, wr]
    for o in parts:
        o.parent = body
    wheel.hide_set(True)
    wheel.hide_render = True
    return [body] + parts


# ============================================================================ 10 Ride-on Ticket Vacuum
def ride_on_vacuum(col):
    b = K.Builder("RideOnVacuum_Body")
    RW, FW = (-1.75, 0.95), (1.75, 0.8)  # (y, radius) rear / front wheels
    b.box((2.8, 3.6, 0.9), "teal", T(0, -0.6, 1.35), chamfer=0.12)  # tub
    b.prism([(0.9, 0.96), (2.55, 0.96), (2.6, 1.7), (2.15, 2.4), (1.15, 2.5), (0.85, 2.3)], 2.2, "teal", MYZ)  # hood
    b.box((1.6, 1.2, 0.08), "teal_lt", T(0, 1.62, 2.46) @ rot(-6), chamfer=0.03)
    b.box((1.3, 0.05, 0.5), "vent", T(0, 2.6, 1.42) @ rot(0, 0, 0))  # front grille
    for s in (-1, 1):
        b.box((0.16, 5.8, 0.4), "steel", T(s * 1.36, -0.1, 0.78), chamfer=0.05)  # frame rails
        fender(b, s * 1.75, RW[0], 0.95, RW[1] + 0.1, RW[1] + 0.32, 0.66, "steel")
        fender(b, s * 1.75, FW[0], 0.8, FW[1] + 0.1, FW[1] + 0.3, 0.62, "steel")
        b.box((0.52, 1.3, 0.12), "steel_dk", T(s * 1.62, 0.02, 0.98))  # foot decks
    # seat
    b.box((1.1, 1.0, 0.22), "char_dk", T(0, -1.05, 1.9))
    b.box((1.55, 1.3, 0.34), "char", T(0, -1.05, 2.18), chamfer=0.1)
    b.box((1.55, 0.32, 1.25), "char", T(0, -1.78, 2.9) @ rot(-12), chamfer=0.1)
    # steering column
    col_top = V(0, 0.55, 3.25)
    b.cyl((0, 0.7, 1.75), col_top, 0.1, 6, "steel")  # base behind the hood so it never pierces it
    # hopper + lid
    b.loft([b.ring_pts(T(0, -2.62, 1.6) @ rot(90), 1.2, 0.52, 8),
            b.ring_pts(T(0, -2.62, 3.0) @ rot(90), 1.32, 0.66, 8)], "yellow", caps=(True, True))
    b.box((2.85, 1.55, 0.24), "steel", T(0, -2.62, 3.1), chamfer=0.08)
    # front suction head
    b.prism([(2.45, 0.1), (3.65, 0.1), (3.72, 0.32), (3.42, 0.78), (2.6, 0.86), (2.45, 0.7)], 4.5, "yellow", MYZ)
    b.box((4.2, 0.05, 0.16), "char_dk", T(0, 3.68, 0.22) @ rot(-20))  # intake slot
    body = b.finish(col)

    sw = K.Builder("RideOnVacuum_SteeringWheel")
    d = (col_top - V(0, 0.7, 1.75)).normalized()
    M = K.look_matrix(V(0, 0, 0), d)
    torus(sw, M, 0.52, 0.07, 16, 6, "char")
    for a in (90, 210, 330):
        r_ = math.radians(a)
        sw.cyl(M @ V(0, 0, 0), M @ V(math.cos(r_) * 0.5, math.sin(r_) * 0.5, 0), 0.04, 4, "char")
    sw.cyl(M @ V(0, 0, -0.06), M @ V(0, 0, 0.06), 0.12, 6, "steel_lt")
    steer = sw.finish(col, location=col_top)

    wheel = wheel_mesh(K.collection("Tool09_RotarySweeper", K.collection("Tools")))
    parts = [steer]
    for name, x, (y, r), wd in (("WheelRL", -1.75, RW, 0.56), ("WheelRR", 1.75, RW, 0.56),
                               ("WheelFL", -1.75, FW, 0.5), ("WheelFR", 1.75, FW, 0.5)):
        o = bpy.data.objects.new("RideOnVacuum_" + name, wheel.data)
        col.objects.link(o)
        o.location = (x, y, r)
        o.scale = (wd / 0.42, r / 0.75, r / 0.75)
        parts.append(o)
    for o in parts:
        o.parent = body
    return [body] + parts

TOOLS = [
    ("01_TicketGrabber", ticket_grabber),
    ("02_DustpanScoop", dustpan_scoop),
    ("03_HandRake", hand_rake),
    ("04_PushBroom", push_broom),
    ("05_Shovel", shovel),
    ("06_HandheldVacuum", handheld_vacuum),
    ("07_LeafBlower", leaf_blower),
    ("08_ShopVac", shop_vac),
    ("09_RotarySweeper", rotary_sweeper),
    ("10_RideOnVacuum", ride_on_vacuum),
]


def build_all(only=None, spacing=7.0):
    main = bpy.data.scenes["Phase03"]
    root = K.collection("Tools", main.collection)
    made = {}
    for i, (cname, fn) in enumerate(TOOLS):
        if only and cname not in only:
            continue
        col = K.collection("Tool" + cname, root)
        K.clear_collection(col)
        objs = fn(col)
        top = [o for o in objs if o.parent is None]
        for o in top:
            o.location = V(i * spacing, 6, 0) + o.location
        made[cname] = objs
    apply_schemes()
    return made


def apply_schemes():
    """Per-tool colours as object-level material overrides (mesh data, UVs and uploaded MeshIds unchanged)."""
    for col in bpy.data.collections["Tools"].children:
        tool_id = col.name.split("_", 1)[1]
        mat = K.tool_material(tool_id)
        for ob in col.all_objects:
            if ob.type == "MESH" and ob.name != "Wheel":
                ob.material_slots[0].link = "OBJECT"
                ob.material_slots[0].material = mat


def report(made):
    out = []
    for cname, objs in made.items():
        n = sum(K.tris(o) for o in objs)
        lo, hi = K.world_bounds(objs)
        size = hi - lo
        out.append(f"{cname}: {n} tris, {len(objs)} mesh, size {size.x:.2f} x {size.y:.2f} x {size.z:.2f}")
    return "\n".join(out)
