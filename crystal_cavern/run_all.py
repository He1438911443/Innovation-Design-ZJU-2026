"""
CRYSTAL CAVERN v2 — Render-Ready Pipeline
Paste into Maya Script Editor Python tab -> Ctrl+Enter

Generates: terrain, faceted crystals, cave enclosure, lighting, fog, dust, camera.
"""
import sys
sys.path.insert(0, "/Users/xixi/大学/未来创新设计/crystal_cavern")

from cave_terrain import create_cave_terrain, create_cave_enclosure
from crystal_seed import get_terrain_surface_info, poisson_disc_sample
from crystal_growth import grow_all_crystals
from cave_lighting import setup_cave_lighting, create_camera_rig

# Stage 1: Terrain
t, hm = create_cave_terrain(width=40, depth=40)

# Stage 2: Crystal seeds
v = get_terrain_surface_info(t)
s = poisson_disc_sample(v, min_dist=2.0, seed=2026)

# Stage 3: Faceted crystal formations (v2)
c, anchors = grow_all_crystals(s, parent_group="crystal_group")

# Stage 4: Lighting + Fog + Dust (precise crystal-position lights)
setup_cave_lighting(crystal_count=c, light_anchors=anchors)

# Stage 5: Cave enclosure (walls + domed ceiling)
create_cave_enclosure(terrain_name=t, width=40, depth=40)

# Stage 6: Camera fly-through
create_camera_rig(terrain_name=t, crystal_group="crystal_group")

# Stage 7: Arnold render settings + render camera
from arnold_render import setup_arnold_render_settings, create_render_camera, render_beauty

setup_arnold_render_settings()
create_render_camera(target_transform="crystal_group")

print("DONE v2 — Render with Arnold, or hit Play for fly-through")
print("Arnold render settings configured. Run render_beauty() to render.")
