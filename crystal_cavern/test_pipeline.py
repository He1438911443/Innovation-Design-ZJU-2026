"""Crystal Cavern v2 — Pipeline test script for Maya commandPort execution."""
import sys, json, traceback
sys.path.insert(0, "/Users/xixi/大学/未来创新设计/crystal_cavern")

for mod_name in ['cave_lighting', 'cave_terrain', 'crystal_growth', 'crystal_seed']:
    if mod_name in sys.modules:
        del sys.modules[mod_name]

import maya.cmds as cmds
results = {"success": True, "stages": {}}

# --- Cleanup ---
for obj in ['cave_terrain', 'cave_enclosure', 'crystal_group',
            'dust_particles', 'cave_fog']:
    if cmds.objExists(obj):
        cmds.delete(obj)
for obj in cmds.ls('fly_cam*') or []:
    try:
        cmds.delete(obj)
    except Exception:
        pass
for lt_type in ['ambientLight', 'directionalLight', 'pointLight',
                'spotLight', 'areaLight']:
    for l in cmds.ls(type=lt_type):
        try:
            cmds.delete(l)
        except Exception:
            pass

from cave_terrain import create_cave_terrain, create_cave_enclosure
from crystal_seed import get_terrain_surface_info, poisson_disc_sample
from crystal_growth import grow_all_crystals
from cave_lighting import setup_cave_lighting, create_camera_rig

# Stage 1: Terrain
t, hm = create_cave_terrain(width=40, depth=40, seed=2026, roughness=0.45)
results['stages']['terrain'] = t
results['stages']['terrain_vtx'] = cmds.polyEvaluate(t, vertex=True)

# Stage 2: Seeds
v = get_terrain_surface_info(t)
s = poisson_disc_sample(v, min_dist=2.0, seed=2026)
results['stages']['seeds'] = len(s)

# Stage 3: Faceted crystals (v2 — returns light_anchors)
c, anchors = grow_all_crystals(s, parent_group="crystal_group")
results['stages']['crystals'] = c
results['stages']['light_anchors'] = len(anchors) if anchors else 0

# Stage 4: Lighting with precise crystal-position lights
amb, fog, dust = setup_cave_lighting(crystal_count=c, light_anchors=anchors)
results['stages']['lighting'] = 'ok'
results['stages']['fog_exists'] = cmds.objExists('cave_fog')
results['stages']['fog_type'] = cmds.nodeType('cave_fog') if cmds.objExists('cave_fog') else None
results['stages']['dust_exists'] = cmds.objExists('dust_particles')

# Stage 5: Cave enclosure
enclosure = create_cave_enclosure(terrain_name=t, width=40, depth=40)
results['stages']['enclosure'] = enclosure
results['stages']['walls_exist'] = all(cmds.objExists(w) for w in
    ['cave_wall_N', 'cave_wall_S', 'cave_wall_E', 'cave_wall_W', 'cave_ceiling'])

# Stage 6: Camera
cam = create_camera_rig(terrain_name=t, crystal_group="crystal_group")
results['stages']['camera'] = cam
results['stages']['camera_exists'] = cmds.objExists(cam)

# Stats
results['total_transforms'] = len(cmds.ls(type='transform'))
results['total_lights'] = len(cmds.ls(type=['ambientLight', 'directionalLight',
                                             'pointLight', 'spotLight', 'areaLight']))

with open('/tmp/maya_pipeline_v5.json', 'w') as f:
    json.dump(results, f, default=str)
print('PIPELINE_V2_COMPLETE')
