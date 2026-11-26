"""Pit gems (phase 03 extension, economy rework 2026-11-26). Run build() inside Blender.

One low-poly brilliant-cut mesh (58 tris), table up, origin at the bounding-box centre.
Every facet plane has its own cell in an 8 x 8 grid (256 px, 32 px cells), so one texture per tier
paints each facet its own flat colour: shaded facets for the five solid tiers, a hue sweep for Rainbow.
In Roblox only TextureID changes between tiers (the same MeshId everywhere).

Gem facets are kept FLAT on purpose: crisp facets are what makes it read as a cut gem. Only the girdle
band is smooth-shaded.
"""
import colorsys
import math
import os

import bmesh
import bpy
import numpy as np
from mathutils import Vector

import fwl_kit as K

N = 10  # sides
R = 0.65  # girdle radius (studs): 1.3 across
TABLE_R = 0.39
GIRDLE_H = 0.035  # half height of the girdle band
CROWN_TOP = 0.29
CULET = -0.56
GRID = 8
TEX = 256

# tier -> (dark, base, light) sRGB hex. Values/rates are TEST (OWNER_DECISIONS_PENDING items 13-16).
TIERS = {
    "Emerald": ("0B6B3C", "1FB86A", "8CF2BC"),
    "Sapphire": ("143B8F", "2F6FE8", "9CC2FF"),
    "Amethyst": ("4E1C85", "9B4DE0", "D9B0FF"),
    "Ruby": ("7A0A1C", "E0263F", "FF9AA8"),
    "Diamond": ("8DB7D0", "D3EEFC", "FFFFFF"),
    "Rainbow": None,
}
TIER_ORDER = list(TIERS)
LIGHT = Vector((-0.35, -0.55, 0.76)).normalized()  # baked key light: front-left, high


def cell_uv(i):
    col, row = i % GRID, i // GRID
    return ((col + 0.5) / GRID, (row + 0.5) / GRID)


def gem_mesh(name="Gem"):
    """Returns (mesh, facets) where facets = [(role, normal, angle)] indexed by cell."""
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    step = 2 * math.pi / N
    zc = (CROWN_TOP + CULET) / 2  # recentre on the bounding box
    table = [bm.verts.new((math.cos((i + 0.5) * step) * TABLE_R, math.sin((i + 0.5) * step) * TABLE_R,
                           CROWN_TOP - zc)) for i in range(N)]
    gtop = [bm.verts.new((math.cos(i * step) * R, math.sin(i * step) * R, GIRDLE_H - zc)) for i in range(N)]
    gbot = [bm.verts.new((math.cos(i * step) * R, math.sin(i * step) * R, -GIRDLE_H - zc)) for i in range(N)]
    culet = bm.verts.new((0, 0, CULET - zc))

    facets = []

    def face(verts, role, ang, smooth=False):
        f = bm.faces.new(verts)
        f.smooth = smooth
        f.normal_update()
        idx = len(facets)
        facets.append((role, f.normal.copy(), ang))
        for l in f.loops:
            l[uv].uv = cell_uv(idx)
        return f

    face(table, "table", 0.0)
    for i in range(N):
        j = (i + 1) % N
        face((gtop[i], gtop[j], table[i]), "crown_bezel", (i + 0.5) * step)  # points up to the table
        face((table[i - 1], gtop[i], table[i]), "crown_star", i * step)  # points down to the girdle
    for i in range(N):
        j = (i + 1) % N
        face((gbot[i], gbot[j], gtop[j], gtop[i]), "girdle", (i + 0.5) * step, smooth=True)
    for i in range(N):
        j = (i + 1) % N
        face((gbot[j], gbot[i], culet), "pavilion", (i + 0.5) * step)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # recompute stored normals after the recalc (winding may have flipped)
    bm.faces.ensure_lookup_table()
    facets = [(r, bm.faces[k].normal.copy(), a) for k, (r, _, a) in enumerate(facets)]
    bmesh.ops.triangulate(bm, faces=[bm.faces[0]], quad_method="BEAUTY", ngon_method="BEAUTY")
    me = bpy.data.meshes.get(name) or bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    # sharp everywhere except between girdle quads
    for e in me.edges:
        e.use_edge_sharp = True
    me.materials.clear()
    return me, facets


def _lerp(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def facet_colour(tier, role, n, ang, idx):
    lam = max(0.0, n.dot(LIGHT))
    if tier == "Rainbow":
        hue = (ang / (2 * math.pi)) % 1.0
        if role == "table":
            return (0.97, 0.95, 1.0)
        if role == "girdle":
            return colorsys.hsv_to_rgb(hue, 0.55, 0.85)
        if role == "pavilion":
            return colorsys.hsv_to_rgb((hue + 0.5) % 1.0, 0.8, 0.55 + 0.35 * lam)
        sat = 0.55 if role == "crown_bezel" else 0.75
        v = 0.78 + 0.22 * lam
        if role == "crown_star" and idx in (2, 12):
            return (1.0, 1.0, 1.0)  # glints
        return colorsys.hsv_to_rgb(hue, sat, v)
    dark, base, light = (K.hex_rgb(h) for h in TIERS[tier])
    white = (1.0, 1.0, 1.0)
    if role == "table":
        return _lerp(base, light, 0.65)
    if role == "girdle":
        return _lerp(dark, base, 0.55)
    if role == "pavilion":
        return _lerp(dark, base, 0.25 + 0.6 * lam)
    if role == "crown_star" and idx in (2, 12):
        return _lerp(light, white, 0.75)  # two glint facets
    t = 0.35 + 0.65 * lam
    if role == "crown_bezel":
        t = min(1.0, t + 0.15)
    return _lerp(base, light, t) if t > 0.5 else _lerp(dark, base, t * 2)


def gem_texture(tier, facets):
    arr = np.zeros((TEX, TEX, 4), dtype=np.float32)
    c = TEX // GRID
    fill = K.hex_rgb(TIERS[tier][1]) if TIERS[tier] else (0.9, 0.9, 0.95)
    arr[:, :] = (*fill, 1.0)
    for idx, (role, n, ang) in enumerate(facets):
        col_, row = idx % GRID, idx // GRID
        arr[row * c:(row + 1) * c, col_ * c:(col_ + 1) * c] = (*facet_colour(tier, role, n, ang, idx), 1.0)
    name = "FWL_Gem_" + tier
    img = bpy.data.images.get(name) or bpy.data.images.new(name, TEX, TEX, alpha=True)
    img.colorspace_settings.name = "sRGB"
    img.pixels.foreach_set(arr.ravel())
    path = os.path.join(K.EXPORT_DIR, name + ".png")
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    img.reload()
    return img


def build(main_scene="Phase03"):
    main = bpy.data.scenes[main_scene]
    root = K.collection("Gems", main.collection)
    K.clear_collection(root)
    prev = K.collection("Gems_Preview6", main.collection)
    K.clear_collection(prev)
    me, facets = gem_mesh()
    mats = {}
    for tier in TIER_ORDER:
        mat = K.textured_material("FWL_Gem_" + tier, gem_texture(tier, facets), roughness=0.3)
        mats[tier] = mat
    me.materials.append(mats["Emerald"])
    ob = bpy.data.objects.new("Gem", me)
    root.objects.link(ob)
    ob.location = (0, -12, 0)
    for i, tier in enumerate(TIER_ORDER):
        p = bpy.data.objects.new("Gem_" + tier, me)
        prev.objects.link(p)
        p.material_slots[0].link = "OBJECT"
        p.material_slots[0].material = mats[tier]
        p.location = (3 + i * 1.8, -12, 0)
    return ob, facets
