"""Headless runner for the phase 03 extension (gems, rarity tickets, bags).

blender -b Assets/Blender/FWL_Phase03_TicketsAndTools.blend --python Assets/Blender/scripts/run_extension.py -- \
    [--export] [--save] [--preview DIR]
"""
import importlib
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import fwl_kit as K  # noqa: E402
import build_tickets  # noqa: E402,F401
import build_tools  # noqa: E402,F401
import build_gems as G  # noqa: E402
import build_rarity as RT  # noqa: E402
import build_bags as BG  # noqa: E402

for m in (K, G, RT, BG):
    importlib.reload(m)

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
PREVIEW = argv[argv.index("--preview") + 1] if "--preview" in argv else None


# ---------------------------------------------------------------------------- preview renders
def preview_scene():
    sc = bpy.data.scenes.get("ExtPreview") or bpy.data.scenes.new("ExtPreview")
    for c in list(sc.collection.children):
        sc.collection.children.unlink(c)
    for ob in list(sc.collection.objects):
        sc.collection.objects.unlink(ob)
    r = sc.render
    r.engine = "BLENDER_WORKBENCH"
    r.resolution_x, r.resolution_y, r.resolution_percentage = 1200, 700, 100
    r.film_transparent = False
    sc.display.shading.light = "STUDIO"
    sc.display.shading.color_type = "TEXTURE"
    sc.display.shading.show_cavity = False
    sc.display.shading.show_specular_highlight = False
    sc.display.shading.show_shadows = True
    sc.display.shading.background_type = "VIEWPORT"
    sc.display.shading.background_color = (0.16, 0.17, 0.2)
    sc.display.render_aa = "16"
    sc.view_settings.view_transform = "Standard"
    if sc.world is None:
        sc.world = bpy.data.worlds.new("ExtPreviewWorld")
    sc.world.color = (0.16, 0.17, 0.2)
    return sc


def render(objs, path, view=(1.0, -1.3, 0.75), ortho=None, res=(1200, 700), extra=()):
    sc = preview_scene()
    sc.render.resolution_x, sc.render.resolution_y = res
    for ob in list(objs) + list(extra):
        if ob.name not in sc.collection.objects:
            sc.collection.objects.link(ob)
    lo, hi = K.world_bounds([o for o in list(objs) + list(extra) if o.type == "MESH"])
    c = (lo + hi) / 2
    size = (hi - lo).length
    cam_data = bpy.data.cameras.get("ExtPreviewCam") or bpy.data.cameras.new("ExtPreviewCam")
    cam = bpy.data.objects.get("ExtPreviewCam") or bpy.data.objects.new("ExtPreviewCam", cam_data)
    if cam.name not in sc.collection.objects:
        sc.collection.objects.link(cam)
    d = Vector(view).normalized()
    if ortho:
        cam_data.type = "ORTHO"
        cam_data.ortho_scale = ortho
        cam.location = c + d * (size * 2)
    else:
        cam_data.type = "PERSP"
        cam_data.lens = 50
        cam.location = c + d * (size * 1.25)
    cam_data.clip_end = 500
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True, scene=sc.name)
    for ob in list(sc.collection.objects):
        sc.collection.objects.unlink(ob)
    print("rendered", path)


def r6_dummy(at):
    """Simple R6 stand-in in the bag frame (torso back centre at `at`)."""
    col = K.collection("R6Dummy", bpy.data.scenes["Phase03"].collection)
    K.clear_collection(col)
    mat = bpy.data.materials.get("DummyGrey") or bpy.data.materials.new("DummyGrey")
    mat.diffuse_color = (0.55, 0.57, 0.6, 1)
    parts = []
    for name, size, pos in (("Torso", (2, 1, 2), (0, 0.5, 0)), ("Head", (1.2, 1.2, 1.0), (0, 0.5, 1.5)),
                            ("LArm", (1, 1, 2), (-1.5, 0.5, 0)), ("RArm", (1, 1, 2), (1.5, 0.5, 0)),
                            ("LLeg", (1, 1, 2), (-0.5, 0.5, -2)), ("RLeg", (1, 1, 2), (0.5, 0.5, -2))):
        me = bpy.data.meshes.new("Dummy" + name)
        import bmesh
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
        bm.to_mesh(me)
        bm.free()
        me.materials.append(mat)
        ob = bpy.data.objects.new("Dummy" + name, me)
        col.objects.link(ob)
        ob.location = Vector(at) + Vector(pos)
        ob.matrix_world = Matrix.Translation(ob.location)
        parts.append(ob)
    return parts


def main():
    main_scene = bpy.data.scenes["Phase03"]
    gem, facets = G.build()
    print("GEM tris", K.tris(gem), "facets", len(facets), "size", tuple(round(x, 3) for x in gem.dimensions))
    if "--no-rarity" not in argv:
        RT.build()
        print("RARITY textures done")
    made = BG.build_all()
    print(BG.report(made))

    if PREVIEW:
        os.makedirs(PREVIEW, exist_ok=True)
        gems = [bpy.data.objects["Gem_" + t] for t in G.TIER_ORDER]
        render(gems, os.path.join(PREVIEW, "gems.png"), view=(0.0, -1.0, 0.55), ortho=11.5, res=(1400, 400))
        render(gems, os.path.join(PREVIEW, "gems_top.png"), view=(0.05, -0.3, 1.0), ortho=11.5, res=(1400, 400))
        if "Tickets_Rarity6" in bpy.data.collections:
            tix = list(bpy.data.collections["Tickets_Rarity6"].objects)
            render(tix, os.path.join(PREVIEW, "rarity.png"), view=(0.0, -0.05, 1.0), ortho=9.0)
        reg = [bpy.data.objects[n] for n in ("Ticket_Red", "Ticket_Golden") if n in bpy.data.objects]
        for bag_id, objs in made.items():
            col = bpy.data.collections[[c.name for c in bpy.data.collections["Bags"].children if c.name.endswith(bag_id)][0]]
            allobjs = list(col.objects)
            render(allobjs, os.path.join(PREVIEW, "solo_%s.png" % bag_id), view=(0.75, -1.3, 0.7), res=(600, 600))
            dummy = r6_dummy(objs[0].location)
            render(allobjs, os.path.join(PREVIEW, "bag_%s_back.png" % bag_id), view=(0.9, -1.4, 0.55), extra=dummy,
                   res=(800, 800))
            render(allobjs, os.path.join(PREVIEW, "bag_%s_side.png" % bag_id), view=(1.0, 0.15, 0.2), extra=dummy,
                   res=(800, 800))
            render(allobjs, os.path.join(PREVIEW, "bag_%s_front.png" % bag_id), view=(-0.5, 1.3, 0.35), extra=dummy,
                   res=(800, 800))
        K.clear_collection(bpy.data.collections["R6Dummy"])

    if "--export" in argv:
        K.export_glb([gem], "FWL_Gems.glb")
        bags = [made[b][0] for b in BG.ORDER]
        saved = [o.location.copy() for o in bags]
        for i, o in enumerate(bags):
            o.location = (i * 4.2, 0, 0)
        K.export_glb(bags, "FWL_Bags.glb")
        for o, loc in zip(bags, saved):
            o.location = loc
        print("EXPORTED")

    if "--save" in argv:
        bpy.ops.wm.save_mainfile()
        print("SAVED", bpy.data.filepath)


main()
