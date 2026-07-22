"""
Crystal Cavern v2 — Procedural Crystal Cave Generator
Main Entry Point

Improvements over v1:
- Faceted hexagonal crystals with pointed tips (not cylinders)
- Precise accent lighting at actual crystal positions
- Cave enclosure with walls and domed ceiling
- Enhanced glass-like materials with subsurface scattering
- Cinematic camera flying closer to crystal formations

Pipeline:
1. Diamond-Square terrain (Fournier et al., 1982)
2. Poisson-disc crystal seed distribution (Bridson, 2007)
3. Faceted crystal growth along normals (Prusinkiewicz, 1990)
4. Precise lighting + volumetric fog + dust particles
5. Cave enclosure (walls + ceiling)
6. Fly-through camera animation (960 frames)

Author: [Your Name]
Course: Innovation Design for Future, Zhejiang University, 2026
Instructor: Prof Xiaosong Yang
"""

import maya.cmds as cmds
import sys
import os

SCRIPT_DIR = "/Users/xixi/大学/未来创新设计/crystal_cavern"
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from cave_terrain import create_cave_terrain, create_cave_enclosure
from crystal_seed import get_terrain_surface_info, poisson_disc_sample
from crystal_growth import grow_all_crystals
from cave_lighting import setup_cave_lighting, create_camera_rig
from crystal_ui import create_ui


def run_pipeline(seed=2026, roughness=0.45, size=40, density=2.0, variance=1.0):
    """Execute the complete Crystal Cavern v2 generation pipeline."""
    print("=" * 60)
    print("  CRYSTAL CAVERN v2 — Procedural Crystal Cave Generator")
    print("  Maya Python Scripting for Animation")
    print("  Innovation Design for Future, ZJU 2026")
    print("=" * 60)

    # Step 1: Cave Terrain
    print("\n[1/6] Generating cave terrain (Diamond-Square)...")
    terrain, height_map = create_cave_terrain(
        width=size, depth=size, seed=seed, roughness=roughness
    )

    # Step 2: Crystal Seed Distribution
    print("\n[2/6] Distributing crystal seeds (Poisson-disc)...")
    vertices = get_terrain_surface_info(terrain)
    seeds = poisson_disc_sample(vertices, min_dist=3.0 / density, seed=seed)
    for s in seeds:
        s["variance"] *= variance

    # Step 3: Crystal Growth (faceted hexagonal bodies + pointed tips)
    print("\n[3/6] Growing faceted crystal formations...")
    crystal_count, light_anchors = grow_all_crystals(seeds, parent_group="crystal_group")

    # Step 4: Lighting + Volumetric Fog + Dust (precise crystal-position lights)
    print("\n[4/6] Setting up cave lighting, fog, and atmosphere...")
    setup_cave_lighting(crystal_count=crystal_count, light_anchors=light_anchors)

    # Step 5: Cave Enclosure (walls + domed ceiling)
    print("\n[5/6] Building cave enclosure...")
    create_cave_enclosure(terrain_name=terrain, width=size, depth=size)

    # Step 6: Camera Animation
    print("\n[6/6] Creating cinematic fly-through camera...")
    create_camera_rig(terrain_name=terrain, crystal_group="crystal_group")

    print("\n" + "=" * 60)
    print("  PIPELINE COMPLETE")
    print("  {0} crystal formations generated".format(crystal_count))
    print("  Camera animation: 960 frames (32s at 30fps)")
    print("  Hit play button to watch the fly-through")
    print("=" * 60)

    # Open GUI for further tuning
    create_ui()
    print("\nGUI panel opened — adjust parameters and click Generate to retry.")


if __name__ == "__main__":
    run_pipeline()
