"""Rarity tickets (phase 03 extension, economy rework 2026-11-26). Run build() inside Blender.

No new mesh: every rarity ticket is the Ticket_Regular mesh (same MeshId) with its own opaque
512 x 512 print. The regular mesh samples row 3 (front) and row 2 (back), and its paper edge samples
(0.003, 0.76), which lands on the printed border. Rows 1 / 0 repeat the print so mip bleed stays in tier.

Look (owner brief): a shiny tier-coloured border, a dark rich panel instead of cream paper, a cut-gem
emblem instead of the stars, and "<TIER> TICKET" text. Clearly different from an ordinary tinted ticket
(cream paper, star emblem) and from the gold ticket (rounded gold mesh).
"""
import colorsys
import math
import os

import bpy

import build_tickets as BT
import fwl_kit as K

# tier -> (border, shine, panel, text). TEST values: tiers and cash multipliers are pending items 13-16.
TIERS = {
    "Emerald": ("1FB86A", "8CF2BC", "0A3F25", "C9FFE2"),
    "Sapphire": ("2F6FE8", "9CC2FF", "0E2557", "D6E6FF"),
    "Amethyst": ("9B4DE0", "D9B0FF", "2E1052", "F0E0FF"),
    "Ruby": ("E0263F", "FF9AA8", "4F0712", "FFE0E5"),
    "Diamond": ("BFE6FA", "FFFFFF", "1B3045", "EAF7FF"),
    "Rainbow": (None, "FFFFFF", "1C1440", "FFFFFF"),
}
TIER_ORDER = list(TIERS)


def rgb_hex(rgb):
    return "".join("%02X" % max(0, min(255, round(c * 255))) for c in rgb)


def mix(h1, h2, t):
    a, b = K.hex_rgb(h1), K.hex_rgb(h2)
    return rgb_hex([x + (y - x) * t for x, y in zip(a, b)])


def notched_panel(name, xo, yo, c, nd, colour, z, coll, off, xg=0.2, gap=0.05):
    """Panel following the V notches, split at x=xg by a dashed perforation (gaps show the border)."""
    left = [(-xo + c, -yo), (xg - gap / 2, -yo), (xg - gap / 2, yo), (-xo + c, yo), (-xo, yo - c), (-xo, 0.2),
            (-xo + nd, 0.0), (-xo, -0.2), (-xo, -yo + c)]
    right = [(xg + gap / 2, -yo), (xo - c, -yo), (xo, -yo + c), (xo, -0.2), (xo - nd, 0.0), (xo, 0.2),
             (xo, yo - c), (xo - c, yo), (xg + gap / 2, yo)]
    BT.flat_poly(name + "L", left, colour, z, coll, off)
    BT.flat_poly(name + "R", right, colour, z, coll, off)
    n = 7
    step = 2 * yo / n
    for i in range(n):
        y0 = -yo + i * step + step * 0.32
        BT.flat_poly(name + "B", BT.rect(xg - gap / 2 - 0.001, y0, xg + gap / 2 + 0.001, y0 + step * 0.36), colour,
                     z, coll, off)


def gem_emblem(cx, cy, r, tier, coll, off, z):
    """Top-down brilliant: rim, ten bezel + ten star facets, table."""
    border, shine, panel, text = TIERS[tier]
    n = 10
    step = 2 * math.pi / n
    P = [(cx + math.cos(math.pi / 2 + i * step) * r, cy + math.sin(math.pi / 2 + i * step) * r) for i in range(n)]
    Q = [(cx + math.cos(math.pi / 2 + i * step) * (r + 0.035), cy + math.sin(math.pi / 2 + i * step) * (r + 0.035))
         for i in range(n)]
    Tb = [(cx + math.cos(math.pi / 2 + (i + 0.5) * step) * r * 0.58,
           cy + math.sin(math.pi / 2 + (i + 0.5) * step) * r * 0.58) for i in range(n)]
    BT.flat_poly("gemrim", Q, shine if tier != "Diamond" else "FFFFFF", z, coll, off)
    for i in range(n):
        j = (i + 1) % n
        a_mid = math.pi / 2 + (i + 0.5) * step
        lam = 0.5 + 0.5 * math.cos(a_mid - math.radians(135))  # light from the top-left
        if tier == "Rainbow":
            hue = ((a_mid - math.pi / 2) / (2 * math.pi)) % 1.0
            bez = rgb_hex(colorsys.hsv_to_rgb(hue, 0.7, 0.75 + 0.25 * lam))
            sta = rgb_hex(colorsys.hsv_to_rgb((hue + 0.05) % 1, 0.85, 0.6 + 0.3 * lam))
        else:
            dark = mix(border, "000000", 0.45)
            bez = mix(border, shine, lam * 0.8)
            sta = mix(dark, border, 0.3 + 0.7 * lam)
        BT.flat_poly("bezel", [P[i], P[j], Tb[i]], bez, z + 0.01, coll, off)
        BT.flat_poly("starf", [Tb[i - 1], P[i], Tb[i]], sta, z + 0.01, coll, off)
    table = mix(shine, "FFFFFF", 0.5) if tier != "Rainbow" else "F7F2FF"
    BT.flat_poly("table", Tb, table, z + 0.02, coll, off)
    BT.flat_poly("glint", BT.sparkle(cx - r * 0.18, cy + r * 0.2, r * 0.3), "FFFFFF", z + 0.03, coll, off)


def border(tier, coll, off):
    b, shine, panel, text = TIERS[tier]
    if tier == "Rainbow":
        BT.flat_poly("base", BT.rect(-1.21, -0.51, 1.21, 0.51), "FF5A5A", 0.0, coll, off)
        n = 14
        w = 2.9 / n
        for i in range(n):  # diagonal hue bands across the whole ticket
            x0 = -1.75 + i * w
            hx = rgb_hex(colorsys.hsv_to_rgb(i / n, 0.62, 1.0))
            BT.flat_poly("band", [(x0, -0.52), (x0 + w + 0.004, -0.52), (x0 + w + 0.3, 0.52), (x0 + 0.3, 0.52)], hx,
                         0.005, coll, off)
        return
    BT.flat_poly("base", BT.rect(-1.21, -0.51, 1.21, 0.51), b, 0.0, coll, off)
    for sx, w in ((-1.05, 0.16), (-0.82, 0.06), (0.45, 0.14), (0.66, 0.05)):  # shine bands
        BT.flat_poly("shine", [(sx, -0.52), (sx + w, -0.52), (sx + w + 0.32, 0.52), (sx + 0.32, 0.52)],
                     mix(b, shine, 0.55), 0.005, coll, off)


def face(tier, coll, off, front):
    b, shine, panel, text = TIERS[tier]
    rim = shine if tier != "Rainbow" else "FFFFFF"
    border(tier, coll, off)
    notched_panel("rim", 1.1, 0.43, 0.08, 0.15, rim, 0.01, coll, off)
    notched_panel("panel", 1.08, 0.405, 0.07, 0.15, panel, 0.02, coll, off)
    glow = mix(panel, b if b else "8A5CFF", 0.35)
    BT.sunburst(-0.48, 0.06, 0.06, 0.34, 14, glow, coll, off, 0.025)
    gem_emblem(-0.48, 0.06, 0.2, tier, coll, off, 0.03)
    for sx, sy, r in ((-0.86, 0.24, 0.05), (-0.14, 0.26, 0.04), (-0.84, -0.12, 0.035)):
        BT.flat_poly("sparkle", BT.sparkle(sx, sy, r), rim, 0.06, coll, off)
    dim = mix(text, panel, 0.35)
    if front:
        BT.text("cap", tier.upper() + " TICKET", 0.095, -0.48, -0.29, 0.06, text, coll, off, box_w=0.8)
        BT.text("lbl", "TICKET No.", 0.065, 0.64, 0.31, 0.06, dim, coll, off, box_w=0.5)
        BT.text("num", "482719", 0.21, 0.64, 0.15, 0.06, text, coll, off)
        BT.scratch_panel(0.32, -0.33, 0.97, -0.04, coll, off, 0.05)
        BT.text("scr", "SCRATCH", 0.075, 0.645, -0.185, 0.075, "868C94", coll, off, box_w=0.5)
    else:
        BT.text("cap", tier.upper(), 0.11, -0.48, -0.29, 0.06, text, coll, off, box_w=0.8)
        BT.text("num", "482719", 0.2, 0.64, 0.2, 0.06, text, coll, off)
        BT.barcode(0.34, -0.31, 0.95, -0.02, dim, coll, off, 0.06)


def render_tier(tier):
    name = "RarityTex"
    sc = bpy.data.scenes.get(name)
    if sc:
        for ob in list(sc.collection.all_objects):
            data = ob.data
            bpy.data.objects.remove(ob)
            if isinstance(data, bpy.types.Mesh) and data.users == 0:
                bpy.data.meshes.remove(data)
            elif isinstance(data, bpy.types.Curve) and data.users == 0:
                bpy.data.curves.remove(data)
    else:
        sc = bpy.data.scenes.new(name)
    coll = sc.collection
    for row, front in ((3, True), (2, False), (1, True), (0, False)):
        face(tier, coll, (BT.L / 2, row + 0.5), front)
    cam_data = bpy.data.cameras.get("RarityTexCam") or bpy.data.cameras.new("RarityTexCam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 4.0
    cam = bpy.data.objects.new("RarityTexCam", cam_data)
    cam.location = (BT.L / 2, 2.0, 5.0)
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
    tmp = os.path.join(K.TEX_DIR, "_rarity_render_tmp.png")
    r.filepath = tmp
    bpy.ops.render.render(write_still=True, scene=sc.name)
    img = bpy.data.images.load(tmp, check_existing=False)
    img.scale(512, 512)
    out = os.path.join(K.EXPORT_DIR, "FWL_TicketRarity_%s.png" % tier)
    img.filepath_raw = out
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)
    os.remove(tmp)
    name = "FWL_TicketRarity_%s.png" % tier
    old = bpy.data.images.get(name)
    if old:
        bpy.data.images.remove(old)
    return bpy.data.images.load(out)


def build(main_scene="Phase03"):
    main = bpy.data.scenes[main_scene]
    prev = K.collection("Tickets_Rarity6", main.collection)
    K.clear_collection(prev)
    reg = bpy.data.meshes["Ticket_Regular"]
    for i, tier in enumerate(TIER_ORDER):
        img = render_tier(tier)
        mat = K.textured_material("FWL_TicketRarity_" + tier, img, roughness=0.5)
        next(n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE").interpolation = "Linear"
        ob = bpy.data.objects.new("Ticket_" + tier, reg)
        prev.objects.link(ob)
        ob.material_slots[0].link = "OBJECT"
        ob.material_slots[0].material = mat
        ob.location = (4 + (i % 3) * 2.7, -6.5 - (i // 3) * 1.3, 0)
