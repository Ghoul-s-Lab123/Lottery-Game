"""Tickets: regular (36 tris) + golden (60 tris) meshes sharing one 512 x 512 ticket atlas.

Atlas rows (v from the bottom, 128 px each): 0 gold back, 1 gold front, 2 regular back, 3 regular front.
Regular rows leave the border band, the notch rim and the perforation gaps TRANSPARENT, so in Roblox
MeshPart.Color shows through: one mesh + one texture gives any number of colour variants.
"""
import math
import os

import bmesh
import bpy
from mathutils import Vector

import fwl_kit as K

L, W, TH = 2.4, 1.0, 0.05  # studs: length (X), width (Y), paper thickness (Z)
TEX_PATH = os.path.join(K.TEX_DIR, "FWL_TicketAtlas_512.png")
ROW_INSET = 0.006  # keeps mip-bleed between rows off the visible faces

REGULAR_OUTLINE = [(-1.2, -0.5), (1.2, -0.5), (1.2, -0.13), (1.04, 0.0), (1.2, 0.13), (1.2, 0.5),
                   (-1.2, 0.5), (-1.2, 0.13), (-1.04, 0.0), (-1.2, -0.13)]
def _gold_outline(r=0.12):
    """Rounded corners (3 points each) + rounded notches: 20 points -> 76 tris (budget 80)."""
    def arc(cx, cy, a0):
        return [(cx + math.cos(math.radians(a0 + k * 45)) * r, cy + math.sin(math.radians(a0 + k * 45)) * r)
                for k in range(3)]
    pts = arc(-1.2 + r, -0.5 + r, 180) + arc(1.2 - r, -0.5 + r, 270)
    pts += [(1.2, -0.15), (1.08, -0.07), (1.08, 0.07), (1.2, 0.15)]
    pts += arc(1.2 - r, 0.5 - r, 0) + arc(-1.2 + r, 0.5 - r, 90)
    pts += [(-1.2, 0.15), (-1.08, 0.07), (-1.08, -0.07), (-1.2, -0.15)]
    # arcs end exactly on the straight edges, so drop points duplicated at the corner joins
    out = []
    for p in pts:
        if not out or (abs(out[-1][0] - p[0]) > 1e-6 or abs(out[-1][1] - p[1]) > 1e-6):
            out.append(p)
    return out


GOLD_OUTLINE = _gold_outline()

TINTS = {  # 20 regular variants: MeshPart.Color values (sRGB hex)
    "Teal": "1BC0C9", "Coral": "FF6F61", "Purple": "A66BE0", "Blue": "3D8BF2", "Orange": "FF9A2E",
    "Green": "4CCB7A", "Pink": "FF7EB6", "Red": "E94B4B", "Lime": "A8D93B", "Sky": "4FC3F7",
    "Indigo": "5C6BC0", "Magenta": "D35BD6", "Mint": "3FD6B5", "Amber": "FFB300", "Rose": "F06292",
    "Cobalt": "2F6FDE", "Leaf": "66BB6A", "Tangerine": "FF7A3D", "Violet": "8E5CE6", "Aqua": "26C6DA",
}


def row_uv(row, x, y, mirror=False):
    u = (x + L / 2) / L
    if mirror:
        u = 1 - u
    v0 = row / 4 + ROW_INSET
    v1 = (row + 1) / 4 - ROW_INSET
    return (u, v0 + (y + W / 2) / W * (v1 - v0))


def ticket_mesh(name, outline, front_row, back_row, edge_uv):
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    bot = [bm.verts.new((x, y, -TH / 2)) for x, y in outline]
    top = [bm.verts.new((x, y, TH / 2)) for x, y in outline]
    n = len(outline)
    for i in range(n):
        j = (i + 1) % n
        f = bm.faces.new((bot[i], bot[j], top[j], top[i]))
        for l in f.loops:
            l[uv].uv = edge_uv
    ft = bm.faces.new(top)
    fb = bm.faces.new(list(reversed(bot)))
    for l in ft.loops:
        l[uv].uv = row_uv(front_row, l.vert.co.x, l.vert.co.y)
    for l in fb.loops:  # seen from below: mirror X so the print reads correctly when flipped over Y
        l[uv].uv = row_uv(back_row, l.vert.co.x, l.vert.co.y, mirror=True)
    # triangulate caps now (concave notches) so the count is exact and identical after export
    bmesh.ops.triangulate(bm, faces=[ft, fb], quad_method="BEAUTY", ngon_method="BEAUTY")
    me = bpy.data.meshes.get(name) or bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.clear()
    for p in me.polygons:
        p.use_smooth = False
    return me


# ---------------------------------------------------------------------------- texture authoring
def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def col(h):
    r, g, b = K.hex_rgb(h)
    return (srgb_to_lin(r), srgb_to_lin(g), srgb_to_lin(b), 1.0)


def flat_poly(name, pts, colour, z, coll, offset):
    me = bpy.data.meshes.new(name)
    vs = [(x + offset[0], y + offset[1], z) for x, y in pts]
    me.from_pydata(vs, [], [list(range(len(vs)))])
    ob = bpy.data.objects.new(name, me)
    ob.color = col(colour)
    coll.objects.link(ob)
    return ob


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def chamfer_rect(x0, y0, x1, y1, c):
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c),
            (x0, y0 + c)]


def star(cx, cy, r, inner=0.45, rotdeg=90):
    pts = []
    for i in range(10):
        a = math.radians(rotdeg) + i * math.pi / 5
        rr = r if i % 2 == 0 else r * inner
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    return pts


FONT_PATH = r"C:\Windows\Fonts\seguibl.ttf"  # Segoe UI Black: only rasterised into the texture


def text(name, body, size, x, y, z, colour, coll, offset, align="CENTER", box_w=0.74):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size
    if os.path.exists(FONT_PATH):
        cu.font = bpy.data.fonts.load(FONT_PATH, check_existing=True)
    cu.align_x = align
    cu.align_y = "CENTER"
    cu.space_character = 1.0
    # fixed text box that shrinks the line to fit, so the number never overruns its panel
    cu.overflow = "SCALE"
    tb = cu.text_boxes[0]
    tb.width, tb.height = box_w, size * 1.3
    tb.x, tb.y = -box_w / 2, -size * 0.35  # Blender drops the line one size below the box top
    ob = bpy.data.objects.new(name, cu)
    ob.location = (x + offset[0], y + offset[1], z)
    ob.color = col(colour)
    coll.objects.link(ob)
    return ob


def scratch_panel(x0, y0, x1, y1, coll, off, z):
    flat_poly("panel", chamfer_rect(x0, y0, x1, y1, 0.04), "A9AFB6", z, coll, off)
    h = y1 - y0
    for k, sx in enumerate((x0 + 0.16, x0 + 0.34)):  # two light diagonal glints, kept inside the panel
        w = 0.07 if k == 0 else 0.04
        flat_poly("glint", [(sx, y0 + 0.03), (sx + w, y0 + 0.03), (sx + w + h * 0.5, y1 - 0.03),
                            (sx + h * 0.5, y1 - 0.03)], "D5D9DD", z + 0.01, coll, off)


def cream_with_perforation(coll, off, z, colour, xg=0.2, gap=0.05):
    """Inner paper following the V notches, split at x=xg by a dashed perforation (gaps transparent)."""
    xo, yo, c, nd = 1.08, 0.4, 0.07, 0.15
    left = [(-xo + c, -yo), (xg - gap / 2, -yo), (xg - gap / 2, yo), (-xo + c, yo), (-xo, yo - c), (-xo, 0.2),
            (-xo + nd, 0.0), (-xo, -0.2), (-xo, -yo + c)]
    right = [(xg + gap / 2, -yo), (xo - c, -yo), (xo, -yo + c), (xo, -0.2), (xo - nd, 0.0), (xo, 0.2),
             (xo, yo - c), (xo - c, yo), (xg + gap / 2, yo)]
    flat_poly("paperL", left, colour, z, coll, off)
    flat_poly("paperR", right, colour, z, coll, off)
    n = 7  # bridges between the dashes
    step = 2 * yo / n
    for i in range(n):
        y0 = -yo + i * step + step * 0.32
        flat_poly("bridge", rect(xg - gap / 2 - 0.001, y0, xg + gap / 2 + 0.001, y0 + step * 0.36), colour, z, coll,
                  off)


def build_layout(coll):
    INK, STAR, CREAM = "23262B", "F7C326", "FFF4DC"
    GOLD, GOLD_LINE, GOLD_DARK, GOLD_SHINE = "F3C22F", "B07F10", "7E5A0C", "FFDD70"

    def ofs(row):
        return (L / 2, row + 0.5)

    SUN, LABEL, SOFT_INK = "FFE6A3", "8A8F97", "3C4048"
    STARS = ((-0.48, 0.05, 0.25), (-0.82, -0.05, 0.11), (-0.14, -0.05, 0.11))

    def emblem(o, burst, star_col, z=0.0):
        sunburst(-0.48, 0.05, 0.07, 0.34, 14, burst, coll, o, z + 0.01)
        for sx, sy, r in STARS:
            flat_poly("star", star(sx, sy, r), star_col, z + 0.02, coll, o)

    # row 3: regular front
    o = ofs(3)
    cream_with_perforation(coll, o, 0.0, CREAM)
    emblem(o, SUN, STAR)
    text("cap", "LUCKY TICKET", 0.1, -0.48, -0.29, 0.03, SOFT_INK, coll, o, box_w=0.78)
    text("lbl", "TICKET No.", 0.065, 0.64, 0.31, 0.03, LABEL, coll, o, box_w=0.5)
    text("num", "482719", 0.21, 0.64, 0.15, 0.03, INK, coll, o)
    scratch_panel(0.32, -0.33, 0.97, -0.04, coll, o, 0.02)
    text("scr", "SCRATCH", 0.075, 0.645, -0.185, 0.045, "868C94", coll, o, box_w=0.5)

    # row 2: regular back
    o = ofs(2)
    cream_with_perforation(coll, o, 0.0, CREAM)
    emblem(o, SUN, STAR)
    text("cap", "GOOD LUCK!", 0.1, -0.48, -0.29, 0.03, SOFT_INK, coll, o, box_w=0.78)
    text("num", "482719", 0.2, 0.64, 0.2, 0.03, INK, coll, o)
    barcode(0.34, -0.31, 0.95, -0.02, INK, coll, o, 0.03)

    # rows 1 / 0: golden front / back
    for row, front in ((1, True), (0, False)):
        o = ofs(row)
        flat_poly("gold", rect(-1.21, -0.51, 1.21, 0.51), GOLD, 0.0, coll, o)
        for sx in (-0.95, -0.35):  # soft diagonal shine bands
            flat_poly("shine", [(sx, -0.42), (sx + 0.16, -0.42), (sx + 0.42, 0.42), (sx + 0.26, 0.42)], GOLD_SHINE,
                      0.01, coll, o)
        frame_o = chamfer_rect(-1.04, -0.42, 1.04, 0.42, 0.07)
        frame_i = chamfer_rect(-1.0, -0.38, 1.0, 0.38, 0.05)
        # frame as 8 quads between the two chamfered loops
        for i in range(8):
            j = (i + 1) % 8
            flat_poly("frame", [frame_o[i], frame_o[j], frame_i[j], frame_i[i]], GOLD_LINE, 0.02, coll, o)
        for i in range(6):
            y0 = -0.36 + i * 0.125
            flat_poly("dash", rect(0.17, y0, 0.21, y0 + 0.07), GOLD_LINE, 0.02, coll, o)
        emblem(o, "FFE48A", GOLD_DARK, z=0.02)
        for sx, sy, r in ((-0.88, 0.25, 0.06), (-0.12, 0.27, 0.05), (-0.86, -0.22, 0.04), (0.92, 0.28, 0.05)):
            flat_poly("sparkle", sparkle(sx, sy, r), "FFF6D2",
                      0.05, coll, o)
        if front:
            text("cap", "GOLDEN TICKET", 0.1, -0.48, -0.27, 0.05, GOLD_DARK, coll, o, box_w=0.76)
            text("lbl", "TICKET No.", 0.065, 0.6, 0.29, 0.05, GOLD_LINE, coll, o, box_w=0.5)
            text("num", "482719", 0.21, 0.6, 0.14, 0.05, GOLD_DARK, coll, o, box_w=0.7)
            scratch_panel(0.3, -0.32, 0.9, -0.05, coll, o, 0.03)
            text("scr", "SCRATCH", 0.075, 0.6, -0.185, 0.055, "868C94", coll, o, box_w=0.5)
        else:
            text("cap", "WINNER", 0.1, -0.48, -0.27, 0.05, GOLD_DARK, coll, o, box_w=0.76)
            text("num", "482719", 0.2, 0.6, 0.18, 0.05, GOLD_DARK, coll, o, box_w=0.7)
            barcode(0.3, -0.3, 0.9, -0.04, GOLD_DARK, coll, o, 0.05)


def sparkle(cx, cy, r):
    """Four-point glint."""
    pts = []
    for i in range(8):
        a = math.pi / 2 + i * math.pi / 4
        rr = r if i % 2 == 0 else r * 0.25
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    return pts


def sunburst(cx, cy, r0, r1, n, colour, coll, off, z):
    """Alternating rays around a point (every other wedge printed)."""
    for i in range(0, 2 * n, 2):
        a0 = i * math.pi / n
        a1 = (i + 1) * math.pi / n
        flat_poly("ray", [(cx + math.cos(a0) * r0, cy + math.sin(a0) * r0),
                          (cx + math.cos(a0) * r1, cy + math.sin(a0) * r1),
                          (cx + math.cos(a1) * r1, cy + math.sin(a1) * r1),
                          (cx + math.cos(a1) * r0, cy + math.sin(a1) * r0)], colour, z, coll, off)


def barcode(x0, y0, x1, y1, colour, coll, off, z, seed=7):
    import random
    rnd = random.Random(seed)
    x = x0
    while x < x1 - 0.012:
        w = rnd.choice((0.008, 0.008, 0.014, 0.022))
        if x + w > x1:
            break
        flat_poly("bar", rect(x, y0, x + w, y1), colour, z, coll, off)
        x += w + rnd.choice((0.008, 0.012, 0.018))


def render_atlas():
    sc = bpy.data.scenes.get("TicketTex")
    if sc:
        for ob in list(sc.collection.all_objects):
            data = ob.data
            bpy.data.objects.remove(ob)
            if isinstance(data, bpy.types.Mesh) and data.users == 0:
                bpy.data.meshes.remove(data)
            elif isinstance(data, bpy.types.Curve) and data.users == 0:
                bpy.data.curves.remove(data)
    else:
        sc = bpy.data.scenes.new("TicketTex")
    coll = sc.collection
    build_layout(coll)
    cam_data = bpy.data.cameras.new("TicketTexCam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 4.0
    cam = bpy.data.objects.new("TicketTexCam", cam_data)
    cam.location = (L / 2, 2.0, 5.0)
    coll.objects.link(cam)
    sc.camera = cam
    r = sc.render
    try:
        r.engine = "BLENDER_WORKBENCH"
    except TypeError as e:
        print("engine", e)
    r.resolution_x, r.resolution_y, r.resolution_percentage = 614, 1024, 100
    r.film_transparent = True
    r.image_settings.file_format = "PNG"
    r.image_settings.color_mode = "RGBA"
    sc.display.shading.light = "FLAT"
    sc.display.shading.color_type = "OBJECT"
    sc.display.render_aa = "16"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    tmp = os.path.join(K.TEX_DIR, "_ticket_render_tmp.png")
    r.filepath = tmp
    win_scene = bpy.context.window.scene
    bpy.context.window.scene = sc
    bpy.ops.render.render(write_still=True, scene=sc.name)
    bpy.context.window.scene = win_scene
    img = bpy.data.images.load(tmp, check_existing=False)
    img.scale(512, 512)
    img.filepath_raw = TEX_PATH
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)
    os.remove(tmp)
    atlas = bpy.data.images.get("FWL_TicketAtlas_512.png") or bpy.data.images.load(TEX_PATH)
    atlas.reload()
    return atlas


def preview_tint_material(atlas):
    """Blender-only preview: mixes Object Color under the atlas alpha, as Roblox does with MeshPart.Color."""
    mat = bpy.data.materials.get("FWL_TicketPreviewTint") or bpy.data.materials.new("FWL_TicketPreviewTint")
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = atlas
    info = nt.nodes.new("ShaderNodeObjectInfo")
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    nt.links.new(tex.outputs["Alpha"], mix.inputs["Factor"])
    nt.links.new(info.outputs["Color"], mix.inputs[6])
    nt.links.new(tex.outputs["Color"], mix.inputs[7])
    nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.8
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    return mat


def build():
    atlas = render_atlas()
    export_mat = K.textured_material("FWL_TicketAtlas", atlas, roughness=0.8)
    next(n for n in export_mat.node_tree.nodes if n.type == "TEX_IMAGE").interpolation = "Linear"
    gold_mat = K.textured_material("FWL_TicketGold", atlas, roughness=0.35)
    next(n for n in gold_mat.node_tree.nodes if n.type == "TEX_IMAGE").interpolation = "Linear"

    main = bpy.data.scenes["Phase03"]
    root = K.collection("Tickets", main.collection)
    K.clear_collection(root)
    reg = ticket_mesh("Ticket_Regular", REGULAR_OUTLINE, 3, 2, (0.003, 0.76))  # edge -> transparent band = tint
    gold = ticket_mesh("Ticket_Golden", GOLD_OUTLINE, 1, 0, (0.003, 0.253))  # edge -> base gold
    reg.materials.append(export_mat)
    gold.materials.append(gold_mat)
    ob_r = bpy.data.objects.new("Ticket_Regular", reg)
    ob_g = bpy.data.objects.new("Ticket_Golden", gold)
    root.objects.link(ob_r)
    root.objects.link(ob_g)
    ob_r.location = (0, 0, 0)
    ob_g.location = (0, -1.6, 0)

    # preview: 20 tinted copies sharing the regular mesh (linked data, preview material on the object slot)
    prev = K.collection("Tickets_Preview20", main.collection)
    K.clear_collection(prev)
    pm = preview_tint_material(atlas)
    for i, (name, hx) in enumerate(TINTS.items()):
        ob = bpy.data.objects.new("Ticket_" + name, reg)
        ob.material_slots  # ensure slots
        prev.objects.link(ob)
        ob.material_slots[0].link = "OBJECT"
        ob.material_slots[0].material = pm
        r, g, b, _ = col(hx)
        ob.color = (r, g, b, 1)
        ob.location = (4 + (i % 5) * 2.7, -(i // 5) * 1.3, 0)
    return ob_r, ob_g
