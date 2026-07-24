"""
CRYSTAL CAVERN — One-click Pipeline (Maya Script Editor version)
Paste into Maya Script Editor Python tab → Ctrl+Enter to run
"""
import sys; sys.path.insert(0, "/Users/xixi/大学/未来创新设计/crystal_cavern")
from cave_terrain import create_cave_terrain
from crystal_seed import get_terrain_surface_info, poisson_disc_sample
from crystal_growth import grow_all_crystals
from cave_lighting import setup_cave_lighting, create_camera_rig

print("[1/5] Terrain...")
terrain, hm = create_cave_terrain()
print("[2/5] Seeds...")
v = get_terrain_surface_info(terrain)
seeds = poisson_disc_sample(v, min_dist=2.0, seed=2026)
print("[3/5] Crystals...")
count = grow_all_crystals(seeds, parent_group="crystal_group")
print("[4/5] Lighting...")
setup_cave_lighting(crystal_count=count)
print("[5/5] Camera...")
cam = create_camera_rig(terrain_name=terrain, crystal_group="crystal_group")
print("\nDONE! Check Outliner for: cave_terrain, crystal_group, fly_cam")
