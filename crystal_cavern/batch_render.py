"""
Phase 3 — Batch: generate + render 6 gem caves sequentially via commandPort.
Each seed cleans the scene, builds a full cave, and triggers Arnold render.
"""

import sys, os, traceback, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

for m in ['cave_lighting','cave_terrain','crystal_growth','crystal_seed','arnold_render']:
    if m in sys.modules: del sys.modules[m]

import maya.cmds as cmds

from cave_terrain import create_cave_terrain, create_cave_enclosure
from crystal_seed import get_terrain_surface_info, poisson_disc_sample
from crystal_growth import grow_all_crystals
from cave_lighting import setup_cave_lighting, create_camera_rig
from arnold_render import setup_arnold_render_settings, create_render_camera

OUT = "/Users/xixi/大学/未来创新设计/crystal_cavern_renders"


def clean():
    for obj in ['cave_terrain','cave_enclosure','crystal_group','dust_particles',
                'cave_fog','stalactites','stalagmites']:
        if cmds.objExists(obj): cmds.delete(obj)
    for n in ['fly_cam','render_cam','render_cam_aim']:
        for o in (cmds.ls(n + '*') or []):
            try: cmds.delete(o)
            except: pass
    for c in cmds.ls(type='animCurve') or []:
        if 'fly_cam' in str(c) or 'render' in str(c):
            try: cmds.delete(c)
            except: pass
    for lt in ['ambientLight','directionalLight','pointLight','spotLight','areaLight']:
        for l in cmds.ls(type=lt):
            try: cmds.delete(l)
            except: pass
    for t in ['aiStandardSurface','lambert','blinn','phong','phongE','aiAtmosphereVolume']:
        for s in (cmds.ls(type=t) or []):
            if str(s) not in ['lambert1','particleCloud1','standardSurface1','shaderGlow1']:
                try: cmds.delete(s)
                except: pass
    for sg in (cmds.ls(type='shadingEngine') or []):
        if str(sg) not in ('initialShadingGroup','initialParticleSE'):
            try: cmds.delete(sg)
            except: pass


def enable_all_cameras():
    for cam in cmds.ls(type='camera'):
        try: cmds.setAttr(cam + '.renderable', True)
        except: pass


def run(theme, seed, roughness):
    t, _ = create_cave_terrain(width=40, depth=40, seed=seed, roughness=roughness)
    v = get_terrain_surface_info(t)
    s = poisson_disc_sample(v, min_dist=2.0, seed=seed)
    c, anchors = grow_all_crystals(s, type_mix="Mixed", color_seed=seed)
    setup_cave_lighting(crystal_count=c, light_anchors=anchors,
                        fog_density=0.05, dust_count=200, crystal_lights=20)
    create_cave_enclosure(terrain_name=t, width=40, depth=40,
                           wall_height=10, ceiling_height=8)
    create_camera_rig(terrain_name=t)
    setup_arnold_render_settings()
    render_cam = create_render_camera()
    enable_all_cameras()
    # Remove aimConstraints (they interfere with batch render)
    for ac in (cmds.ls(type='aimConstraint') or []):
        try: cmds.delete(ac)
        except: pass
    return c, cmds.polyEvaluate(t, vertex=True), len(cmds.ls(type='aiStandardSurface') or [])


def render_beauty(theme, cam_name):
    d = os.path.join(OUT, theme)
    os.makedirs(d, exist_ok=True)
    p = d + "/beauty"
    cmds.setAttr('defaultRenderGlobals.imageFilePrefix', p, type='string')
    cmds.setAttr('defaultRenderGlobals.outFormatControl', 0)
    cmds.setAttr('defaultRenderGlobals.animation', 0)
    cmds.setAttr('defaultRenderGlobals.putFrameBeforeExt', 0)

    import maya.mel as mel
    mel.eval('arnoldRender -batch -camera ' + cam_name)

    # Also save .ma scene
    sp = os.path.join(d, "cave.ma")
    cmds.file(rename=sp)
    cmds.file(save=True, type='mayaAscii')
    return p, sp


def find_cam():
    for p in ['render_cam', 'fly_cam']:
        for o in (cmds.ls(p + '*') or []):
            try:
                if cmds.nodeType(o) == 'transform':
                    if cmds.listRelatives(o, shapes=True, type='camera'):
                        return o
            except: continue
    return 'persp'


def all():
    themes = [
        ("amethyst_cave",   2026, 0.45, "Purple amethyst cavern"),
        ("citrine_cave",    7734, 0.50, "Golden citrine chamber"),
        ("fluorite_cave",   4242, 0.35, "Green-cyan fluorite grotto"),
        ("aquamarine_cave", 1031, 0.40, "Ice-blue aquamarine hollow"),
        ("ruby_cave",       7777, 0.55, "Deep red ruby vault"),
        ("obsidian_cave",   1313, 0.30, "Smoky black obsidian abyss"),
    ]
    total = len(themes)
    log = []

    print("=" * 60)
    print("  CRYSTAL CAVERN — Batch Render (Phase 3)")
    print("=" * 60)

    for i, (theme, seed, rough, desc) in enumerate(themes, 1):
        print("\n[{0}/{1}] {2} (seed={3})".format(i, total, desc, seed))
        clean()
        try:
            c, vtx, shd = run(theme, seed, rough)
            cam = find_cam()
            out, scene = render_beauty(theme, cam)
            log.append("{0}: OK → {1}".format(theme, out))
            print("  {0} crystals, {1}k verts, {2} shaders".format(c, vtx, shd))
            print("  Camera: {0}, output: {1}".format(cam, out))
            print("  Scene saved: {0}".format(scene))
        except Exception as e:
            log.append("{0}: FAIL ({1})".format(theme, str(e)[:120]))
            print("  ERROR: {0}".format(e))
            traceback.print_exc()

    with open(os.path.join(OUT, "batch_log.json"), 'w') as f:
        json.dump(log, f, indent=2)

    print("\n" + "=" * 60)
    print("  BATCH COMPLETE")
    for l in log: print("  " + l)
    print("  Output: " + OUT)
    print("=" * 60)


if __name__ == "__main__":
    all()
