"""Rebuild with big crystals, deep terrain, close camera. Run in Maya Script Editor."""
import sys, os
SD = "/Users/xixi/大学/未来创新设计/crystal_cavern"
sys.path.insert(0, SD)
for m in ['cave_lighting','cave_terrain','crystal_growth','crystal_seed','arnold_render']:
    if m in sys.modules: del sys.modules[m]

import maya.cmds as cmds

# Nuclear cleanup
for obj in ['cave_terrain','cave_enclosure','crystal_group','dust_particles','cave_fog','stalactites','stalagmites']:
    if cmds.objExists(obj): cmds.delete(obj)
for n in ['fly_cam','render_cam']:
    for o in (cmds.ls(n+'*') or []):
        try: cmds.delete(o)
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
print("CLEANUP DONE")

from cave_terrain import create_cave_terrain, create_cave_enclosure
from crystal_seed import get_terrain_surface_info, poisson_disc_sample
from crystal_growth import grow_all_crystals
from cave_lighting import setup_cave_lighting, create_camera_rig
from arnold_render import setup_arnold_render_settings, create_render_camera

print("Building terrain with deep bowl...")
t,hm = create_cave_terrain(width=40,depth=40,seed=2026,roughness=0.45,wall_height=18)
print("  Terrain: %d verts" % cmds.polyEvaluate(t, vertex=True))

print("Distributing seeds...")
v = get_terrain_surface_info(t)
s = poisson_disc_sample(v,min_dist=2.5,seed=2026)
print("  Seeds: %d" % len(s))

print("Growing BIG crystals...")
c,anchors = grow_all_crystals(s,type_mix="Mixed",color_seed=2026)
# Show sizes
biggest = []
for ch in (cmds.listRelatives('crystal_group',children=True,type='transform') or [])[:5]:
    try:
        h = cmds.getAttr(ch+'.crystalHeight')
        print("  %s: %.1f units tall" % (str(ch), h))
        biggest.append(h)
    except: pass
print("  Crystals: %d, tallest: %.1f" % (c, max(biggest) if biggest else 0))

print("Setting up lights + fog...")
setup_cave_lighting(crystal_count=c,light_anchors=anchors,fog_density=0.04,dust_count=300,crystal_lights=20)
print("Building enclosure + stalactites...")
create_cave_enclosure(terrain_name=t,width=40,depth=40,wall_height=14,ceiling_height=12)
print("Creating dynamic camera...")
create_camera_rig(terrain_name=t)
print("Configuring Arnold...")
setup_arnold_render_settings()
print("Creating render camera (wide, close)...")
render_cam = create_render_camera()

# Enable all cameras
for cam in cmds.ls(type='camera'):
    try: cmds.setAttr(cam+'.renderable',True)
    except: pass

# Save
out_dir = os.path.join(SD, "renders", "final_v4")
os.makedirs(out_dir,exist_ok=True)
sp = os.path.join(out_dir, "crystal_cavern.ma")
cmds.file(rename=sp)
cmds.file(save=True,type="mayaAscii")

# Take viewport screenshots
for panel in cmds.getPanel(type='modelPanel') or []:
    try:
        # render_cam view
        for o in (cmds.ls('render_cam*') or []):
            if cmds.nodeType(o)=='transform' and cmds.listRelatives(o,shapes=True,type='camera'):
                cmds.modelPanel(panel,edit=True,camera=o)
                break
    except: pass
cmds.viewFit(o,fitFactor=0.9)
cmds.playblast(frame=1,format='image',filename=out_dir+"/render_view",widthHeight=(1920,1080),viewer=False,showOrnaments=False,clearCache=True,percent=100,compression='png',quality=100)

# fly_cam at frame 360
for o in (cmds.ls('fly_cam*') or []):
    if cmds.nodeType(o)=='transform' and cmds.listRelatives(o,shapes=True,type='camera'):
        for panel in cmds.getPanel(type='modelPanel') or []:
            try: cmds.modelPanel(panel,edit=True,camera=o)
            except: pass
        cmds.currentTime(360)
        cmds.playblast(frame=360,format='image',filename=out_dir+"/fly_360",widthHeight=(1920,1080),viewer=False,showOrnaments=False,clearCache=True,percent=100,compression='png',quality=100)
        cmds.currentTime(720)
        cmds.playblast(frame=720,format='image',filename=out_dir+"/fly_720",widthHeight=(1920,1080),viewer=False,showOrnaments=False,clearCache=True,percent=100,compression='png',quality=100)
        break

print("\n===== BUILD COMPLETE =====")
print("Scene: %s" % sp)
print("Transforms: %d" % len(cmds.ls(type='transform')))
print("Lights: %d" % len(cmds.ls(type=['ambientLight','directionalLight','pointLight','spotLight','areaLight'])))
print("Screenshots: %s" % out_dir)
print(" TO RENDER: Arnold > Open Render View > set Camera to render_cam > Start Render")
print("==========================")
