"""Find the Winning Lottery - phase 03 asset kit (Blender 5.x, run inside Blender).

Conventions
- 1 Blender unit = 1 Roblox stud (matches how the Lobby meshes imported).
- Blender +Z is up (Roblox +Y). Blender +Y is the tool's forward / working end (Roblox -Z,
  the LookVector, after the glTF Y-up conversion).
- Every tool mesh samples ONE shared flat-colour palette atlas (PALETTE_PATH). Each face's UVs
  collapse to the centre of its colour cell, so one MeshPart + one texture gives a multi-colour,
  flat-shaded low-poly look (no Roblox material textures).
"""
import math
import os

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

ROOT = r"C:\Users\matei\Documents\GitHub\Lottery-Game\Assets"
TEX_DIR = os.path.join(ROOT, "Textures")
EXPORT_DIR = os.path.join(ROOT, "Export")
PALETTE_PATH = os.path.join(TEX_DIR, "FWL_ToolPalette_256.png")

# 4 x 4 cells of 64 px. Index counts from the BOTTOM-left cell (Blender image origin).
GRID = 4
TEX = 256
PALETTE = {
    "teal": "1BA99A",
    "teal_lt": "34C6B2",
    "teal_dk": "11786F",
    "yellow": "F7C326",
    "yellow_dk": "DE9F12",
    "char": "3A3E44",
    "char_dk": "26292D",
    "steel": "A7AFB8",
    "steel_lt": "D2D7DC",
    "steel_dk": "7E868F",
    "vent": None,  # grey plate with three dark slots: faces mapped across the whole cell
    "cream": "FFF3D6",
    "red": "E4573F",
    "ink": "1E2024",
    "white": "F5F5F2",
    "orange": "F08A24",
}
NAMES = list(PALETTE.keys())

# Smoothing (owner, 2026-11-26: "they need smoothening"): small bevels on every hard piece, more sides on
# round parts, smooth shading split at SHARP_ANGLE, and a Weighted Normal modifier so big faces stay flat-lit.
SMOOTH = True
BEVEL = 0.035
SHARP_ANGLE = 50.0
ROUND_SEGS = {6: 8, 8: 12, 10: 14, 12: 16}


def segs(n):
    return ROUND_SEGS.get(n, n) if SMOOTH else n


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def cell_index(name):
    return NAMES.index(name)


def cell_rect(name, inset=0.12):
    i = cell_index(name)
    col, row = i % GRID, i // GRID
    s = 1.0 / GRID
    return (col * s + s * inset, row * s + s * inset, (col + 1) * s - s * inset, (row + 1) * s - s * inset)


def cell_uv(name):
    u0, v0, u1, v1 = cell_rect(name, 0.0)
    return ((u0 + u1) / 2, (v0 + v1) / 2)


# ---------------------------------------------------------------------------- palette
def _mix(h, other, t):
    a, b = hex_rgb(h), hex_rgb(other)
    return "".join("%02X" % round((x + (y - x) * t) * 255) for x, y in zip(a, b))


# Per-tool colour schemes (owner, 2026-11-26: "different unique colors for each tool").
# primary replaces the teal cells, accent replaces the yellow cells; grips/steel/wheels/vents stay shared.
TOOL_SCHEMES = {
    "TicketGrabber": ("E5484D", "FFE8B0"),
    "DustpanScoop": ("F28C28", "2B3A67"),
    "HandRake": ("3FAE5A", "FFD23F"),
    "PushBroom": ("3BA4E8", "FF8C42"),
    "Shovel": ("1F3A93", "E63946"),
    "HandheldVacuum": ("F472B6", "5EEAD4"),
    "LeafBlower": ("84CC16", "7C3AED"),
    "ShopVac": ("2563EB", "FACC15"),
    "RotarySweeper": ("14B8A6", "FB7185"),
    "RideOnVacuum": ("6D28D9", "F5B700"),
}


def scheme_palette(tool_id):
    primary, accent = TOOL_SCHEMES[tool_id]
    p = dict(PALETTE)
    p.update(teal=primary, teal_lt=_mix(primary, "FFFFFF", 0.25), teal_dk=_mix(primary, "000000", 0.3),
             yellow=accent, yellow_dk=_mix(accent, "000000", 0.18))
    return p


def build_palette_image(palette=None, name="FWL_ToolPalette", path=None):
    palette = palette or PALETTE
    path = path or PALETTE_PATH
    arr = np.zeros((TEX, TEX, 4), dtype=np.float32)
    c = TEX // GRID
    for i, cell in enumerate(NAMES):
        col, row = i % GRID, i // GRID
        y0, x0 = row * c, col * c
        if cell == "vent":
            arr[y0:y0 + c, x0:x0 + c] = (*hex_rgb("9AA2AA"), 1)
            # three dark slots across the middle 70 % (y runs bottom -> top)
            for k in range(3):
                sy = y0 + int(c * (0.2 + k * 0.24))
                arr[sy:sy + int(c * 0.12), x0 + int(c * 0.16):x0 + int(c * 0.84)] = (*hex_rgb("2E3237"), 1)
        else:
            arr[y0:y0 + c, x0:x0 + c] = (*hex_rgb(palette[cell]), 1)
    img = bpy.data.images.get(name)
    if img is None:
        img = bpy.data.images.new(name, TEX, TEX, alpha=True)
    img.colorspace_settings.name = "sRGB"
    img.pixels.foreach_set(arr.ravel())
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    img.reload()
    return img


def textured_material(name, image, roughness=0.75):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = image
    tex.interpolation = "Closest"
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = 0.0
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    out.location = (300, 0)
    tex.location = (-400, 0)
    return mat


def tool_material(tool_id):
    """Per-tool palette (same cell layout as the shared one). PNG goes to Export/ for upload."""
    path = os.path.join(EXPORT_DIR, "FWL_Palette_%s.png" % tool_id)
    img = build_palette_image(scheme_palette(tool_id), "FWL_Palette_" + tool_id, path)
    return textured_material("FWL_Palette_" + tool_id, img)


def palette_material():
    img = bpy.data.images.get("FWL_ToolPalette")
    if img is None or not os.path.exists(PALETTE_PATH):
        img = build_palette_image()
    return textured_material("FWL_ToolPalette", img)


# ---------------------------------------------------------------------------- mesh builder
def look_matrix(origin, direction, up=Vector((0, 0, 1))):
    """Matrix whose local +Z points along `direction`, positioned at origin."""
    d = Vector(direction).normalized()
    if abs(d.dot(up)) > 0.999:
        up = Vector((0, 1, 0))
    x = up.cross(d).normalized()
    y = d.cross(x).normalized()
    m = Matrix((x, y, d)).transposed().to_4x4()
    m.translation = Vector(origin)
    return m


def rot(deg_x=0, deg_y=0, deg_z=0):
    return (Matrix.Rotation(math.radians(deg_z), 4, "Z") @ Matrix.Rotation(math.radians(deg_y), 4, "Y")
            @ Matrix.Rotation(math.radians(deg_x), 4, "X"))


def T(x=0, y=0, z=0):
    return Matrix.Translation((x, y, z))


class Builder:
    def __init__(self, name):
        self.name = name
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")

    # -- internals
    def _paint(self, faces, color):
        if color == "vent":
            return self._paint_projected(faces, color)
        uv = cell_uv(color)
        for f in faces:
            for l in f.loops:
                l[self.uv].uv = uv

    def _paint_projected(self, faces, color):
        """Map each face planar across the cell (for the vent grille)."""
        u0, v0, u1, v1 = cell_rect(color, 0.02)
        for f in faces:
            n = f.normal
            # tangent frame: 'up' is world Z projected, else Y
            up = Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((0, 1, 0))
            t = up.cross(n).normalized()
            b = n.cross(t).normalized()
            pts = [(l.vert.co.dot(t), l.vert.co.dot(b)) for l in f.loops]
            mins = (min(p[0] for p in pts), min(p[1] for p in pts))
            maxs = (max(p[0] for p in pts), max(p[1] for p in pts))
            for l, p in zip(f.loops, pts):
                a = (p[0] - mins[0]) / max(1e-6, maxs[0] - mins[0])
                c = (p[1] - mins[1]) / max(1e-6, maxs[1] - mins[1])
                l[self.uv].uv = (u0 + a * (u1 - u0), v0 + c * (v1 - v0))

    def _new_faces(self, before):
        return [f for f in self.bm.faces if f not in before]

    def _drop_faces(self, faces, normal_dirs):
        """Remove faces whose normal is within 10 deg of any dir in normal_dirs (hidden caps)."""
        kill = []
        for f in faces:
            f.normal_update()
            for d in normal_dirs:
                if f.normal.dot(Vector(d).normalized()) > 0.985:
                    kill.append(f)
                    break
        if kill:
            bmesh.ops.delete(self.bm, geom=kill, context="FACES_ONLY")
        return [f for f in faces if f.is_valid]

    # -- primitives
    def _soften(self, faces, limit):
        """One-segment bevel on every edge of a freshly built closed piece (before it is transformed)."""
        if not SMOOTH:
            return
        off = min(BEVEL, limit)
        if off < 0.004:
            return
        edges = list({e for f in faces for e in f.edges})
        verts = list({v for f in faces for v in f.verts})
        bmesh.ops.bevel(self.bm, geom=edges + verts, offset=off, segments=1, affect="EDGES", profile=0.5,
                        clamp_overlap=True)

    def box(self, size, color, M=Matrix(), chamfer=None, chamfer_mode="ALL", drop=()):
        """Box centred at local origin. chamfer_mode 'ALL' bevels every edge, 'Z' only vertical edges.
        chamfer=None uses the default smoothing bevel."""
        sx, sy, sz = size
        if chamfer is None:
            chamfer = min(BEVEL, min(size) * 0.22) if SMOOTH else 0.0
            chamfer_mode = "ALL"
        before = set(self.bm.faces)
        if chamfer > 0 and chamfer_mode == "Z":
            c = chamfer
            pts = [(-sx / 2 + c, -sy / 2), (sx / 2 - c, -sy / 2), (sx / 2, -sy / 2 + c), (sx / 2, sy / 2 - c),
                   (sx / 2 - c, sy / 2), (-sx / 2 + c, sy / 2), (-sx / 2, sy / 2 - c), (-sx / 2, -sy / 2 + c)]
            return self.prism(pts, sz, color, M, drop=drop)
        res = bmesh.ops.create_cube(self.bm, size=1.0, matrix=Matrix.Diagonal((sx, sy, sz, 1)))
        verts = res["verts"]
        if chamfer > 0:
            edges = list({e for v in verts for e in v.link_edges})
            bmesh.ops.bevel(self.bm, geom=edges + verts, offset=chamfer, segments=1, affect="EDGES",
                            profile=0.5, clamp_overlap=True)
        new = self._new_faces(before)
        nv = {v for f in new for v in f.verts}
        bmesh.ops.transform(self.bm, matrix=M, verts=list(nv))
        new = self._drop_faces(new, [M.to_3x3() @ Vector(d) for d in drop])
        self._paint(new, color)
        return new

    def prism(self, pts2d, depth, color, M=Matrix(), caps=(True, True), drop=(), side_color=None):
        """Extrude a CCW 2D polygon (local XY) along local Z, from -depth/2 to +depth/2."""
        before = set(self.bm.faces)
        area = sum(pts2d[i][0] * pts2d[(i + 1) % len(pts2d)][1] - pts2d[(i + 1) % len(pts2d)][0] * pts2d[i][1]
                   for i in range(len(pts2d)))
        if area < 0:
            pts2d = list(reversed(pts2d))
        bot = [self.bm.verts.new((x, y, -depth / 2)) for x, y in pts2d]
        top = [self.bm.verts.new((x, y, depth / 2)) for x, y in pts2d]
        n = len(pts2d)
        sides = []
        for i in range(n):
            j = (i + 1) % n
            sides.append(self.bm.faces.new((bot[i], bot[j], top[j], top[i])))
        capf = []
        if caps[0]:
            capf.append(self.bm.faces.new(list(reversed(bot))))
        if caps[1]:
            capf.append(self.bm.faces.new(top))
        if caps[0] and caps[1]:
            self._soften(self._new_faces(before), depth * 0.3)
        new = self._new_faces(before)
        bmesh.ops.transform(self.bm, matrix=M, verts=list({v for f in new for v in f.verts}))
        new = self._drop_faces(new, [M.to_3x3() @ Vector(d) for d in drop])
        if side_color:
            self._paint([f for f in sides if f.is_valid], side_color)
            self._paint([f for f in capf if f.is_valid], color)
        else:
            self._paint(new, color)
        return new

    def ring(self, center_M, radius, seg, phase=0.0, rx=None):
        rx = radius if rx is None else rx
        vs = []
        for i in range(seg):
            a = phase + 2 * math.pi * i / seg
            vs.append(self.bm.verts.new(center_M @ Vector((math.cos(a) * rx, math.sin(a) * radius, 0))))
        return vs

    def loft(self, sections, color, caps=(True, True), cap_colors=None):
        """sections: list of lists of world-space points (same count, CCW seen from the end)."""
        before = set(self.bm.faces)
        rings = [[self.bm.verts.new(Vector(p)) for p in sec] for sec in sections]
        n = len(sections[0])
        for a, b in zip(rings, rings[1:]):
            for i in range(n):
                j = (i + 1) % n
                self.bm.faces.new((a[i], a[j], b[j], b[i]))
        cf = []
        if caps[0]:
            cf.append(self.bm.faces.new(list(reversed(rings[0]))))
        if caps[1]:
            cf.append(self.bm.faces.new(rings[-1]))
        new = self._new_faces(before)
        bmesh.ops.recalc_face_normals(self.bm, faces=new)
        self._paint(new, color)
        if cap_colors:
            for f, c in zip(cf, cap_colors):
                if c:
                    self._paint([f], c)
        return new

    def cyl(self, a, b, r, seg, color, r2=None, caps=(True, True), phase=None, cap_colors=None):
        a, b = Vector(a), Vector(b)
        r2 = r if r2 is None else r2
        seg = segs(seg) if seg >= 6 else seg
        M = look_matrix(a, b - a)
        L = (b - a).length
        ph = math.pi / seg if phase is None else phase
        secs = []
        for t, rr in ((0.0, r), (1.0, r2)):
            m = M @ T(0, 0, L * t)
            secs.append([m @ Vector((math.cos(ph + 2 * math.pi * i / seg) * rr,
                                     math.sin(ph + 2 * math.pi * i / seg) * rr, 0)) for i in range(seg)])
        return self.loft(secs, color, caps, cap_colors)

    def tube(self, pts, r, seg, color, caps=(True, True), radii=None):
        """Polyline tube with rings oriented on the averaged tangent."""
        pts = [Vector(p) for p in pts]
        seg = segs(seg) if seg >= 6 else seg
        secs = []
        for k, p in enumerate(pts):
            if k == 0:
                d = pts[1] - pts[0]
            elif k == len(pts) - 1:
                d = pts[-1] - pts[-2]
            else:
                d = (pts[k + 1] - pts[k]).normalized() + (pts[k] - pts[k - 1]).normalized()
            m = look_matrix(p, d, up=Vector((0, 0, 1)) if abs(d.normalized().z) < 0.9 else Vector((0, 1, 0)))
            rr = radii[k] if radii else r
            secs.append([m @ Vector((math.cos(math.pi / seg + 2 * math.pi * i / seg) * rr,
                                     math.sin(math.pi / seg + 2 * math.pi * i / seg) * rr, 0)) for i in range(seg)])
        return self.loft(secs, color, caps)

    def offset(self, v):
        """Move all geometry so that point v becomes the object origin."""
        bmesh.ops.translate(self.bm, vec=-Vector(v), verts=self.bm.verts)

    def ring_pts(self, M, rx, rz, seg, phase=None):
        """Points of an n-gon in local XZ (flat sides on axes when phase=None), transformed by M."""
        ph = math.pi / seg if phase is None else phase
        k = 1 / math.cos(math.pi / seg) if phase is None else 1.0
        return [M @ Vector((math.cos(ph + 2 * math.pi * i / seg) * rx * k, 0,
                            math.sin(ph + 2 * math.pi * i / seg) * rz * k)) for i in range(seg)]

    # -- output
    def finish(self, collection, location=(0, 0, 0), material=None):
        bmesh.ops.remove_doubles(self.bm, verts=self.bm.verts, dist=1e-5)
        self.bm.normal_update()
        if SMOOTH:
            lim = math.radians(SHARP_ANGLE)
            for f in self.bm.faces:
                f.smooth = True
            for e in self.bm.edges:
                e.smooth = not (len(e.link_faces) == 2 and e.calc_face_angle(0.0) > lim) and len(e.link_faces) == 2
        me = bpy.data.meshes.get(self.name)
        if me is None:
            me = bpy.data.meshes.new(self.name)
        self.bm.normal_update()
        self.bm.to_mesh(me)
        self.bm.free()
        if not SMOOTH:
            for p in me.polygons:
                p.use_smooth = False
        ob = bpy.data.objects.get(self.name)
        if ob is None:
            ob = bpy.data.objects.new(self.name, me)
        else:
            ob.data = me
        if ob.name not in collection.objects:
            for c in ob.users_collection:
                c.objects.unlink(ob)
            collection.objects.link(ob)
        ob.location = location
        me.materials.clear()
        me.materials.append(material or palette_material())
        for m in list(ob.modifiers):
            ob.modifiers.remove(m)
        if SMOOTH:
            # bake weighted normals into the mesh data so linked copies (brushes, wheels) share them
            wn = ob.modifiers.new("WeightedNormal", "WEIGHTED_NORMAL")
            wn.keep_sharp = True
            wn.weight = 50
            bpy.context.view_layer.update()
            dg = bpy.context.evaluated_depsgraph_get()
            baked = bpy.data.meshes.new_from_object(ob.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
            ob.modifiers.remove(wn)
            old = ob.data
            ob.data = baked
            if old.users == 0:
                bpy.data.meshes.remove(old)
            baked.name = self.name
            if not baked.materials:
                baked.materials.append(material or palette_material())
        return ob


# ---------------------------------------------------------------------------- utilities
def tris(ob):
    me = ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
    n = sum(len(p.vertices) - 2 for p in me.polygons)
    ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
    return n


def collection(name, parent=None):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(col)
    return col


def clear_collection(col):
    for ob in list(col.objects):
        me = ob.data
        bpy.data.objects.remove(ob)
        if me and me.users == 0:
            bpy.data.meshes.remove(me)


def isolate(names=None):
    """Hide every mesh except `names` (and their children) in viewport + render. None shows all tools."""
    keep = set()
    for n in names or []:
        ob = bpy.data.objects.get(n)
        if ob:
            keep.add(ob)
            keep.update(ob.children_recursive)
    for ob in bpy.context.scene.objects:
        if ob.type == "MESH":
            hide = bool(names) and ob not in keep
            ob.hide_render = hide
            ob.hide_set(hide)


def world_bounds(objs):
    lo = Vector((1e9, 1e9, 1e9))
    hi = -lo
    for ob in objs:
        for v in ob.data.vertices:
            w = ob.matrix_world @ v.co
            lo = Vector(map(min, lo, w))
            hi = Vector(map(max, hi, w))
    return lo, hi


def export_glb(objs, filename):
    path = os.path.join(EXPORT_DIR, filename)
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objs:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_apply=True,
                              export_yup=True, export_cameras=False, export_lights=False)
    return path
