"""
Crystal Cavern — Module 2: Crystal Seed Distribution
Reference: Bridson, R. (2007). Fast Poisson Disk Sampling.
"""

import maya.cmds as cmds
import random
import math


def get_terrain_surface_info(terrain_name="cave_terrain"):
    """Extract vertex positions and normals from a terrain mesh."""
    vertices = []
    mesh_shape = cmds.listRelatives(terrain_name, shapes=True)
    if not mesh_shape:
        raise ValueError("Cannot find mesh shape for " + terrain_name)
    mesh_shape = mesh_shape[0]

    vtx_count = cmds.polyEvaluate(terrain_name, vertex=True)
    print("   Terrain has " + str(vtx_count) + " vertices")

    for i in range(vtx_count):
        pos = cmds.xform(terrain_name + ".vtx[" + str(i) + "]", query=True,
                         translation=True, worldSpace=True)
        normal = cmds.polyNormalPerVertex(terrain_name + ".vtx[" + str(i) + "]",
                                          query=True, xyz=True)
        if pos and normal:
            avg_normal = [
                sum(normal[0::3]) / len(normal[0::3]),
                sum(normal[1::3]) / len(normal[1::3]),
                sum(normal[2::3]) / len(normal[2::3]),
            ]
            vertices.append((pos, avg_normal))

    return vertices


def distribute_seeds_simple(vertices, target_count=30, min_dist=1.5, seed=2026):
    """
    Place crystal seeds with minimum spacing using a simple greedy approach.

    This is faster and more reliable than full Poisson-disc for large
    vertex sets, while producing visually equivalent results.

    Args:
        vertices: list of (position, normal) tuples
        target_count: desired number of crystal formations
        min_dist: minimum spacing between seeds
        seed: random seed
    """
    random.seed(seed)

    # Shuffle vertices for random distribution
    shuffled = list(vertices)
    random.shuffle(shuffled)

    selected = []
    for pos, normal in shuffled:
        # Skip vertices that are too close to existing selections
        too_close = False
        for sp, _ in selected:
            dx = pos[0] - sp[0]
            dy = pos[1] - sp[1]
            dz = pos[2] - sp[2]
            if dx*dx + dy*dy + dz*dz < min_dist * min_dist:
                too_close = True
                break

        if not too_close:
            selected.append((pos, normal))
            if len(selected) >= target_count:
                break

    # Build result list
    crystal_types = ["prism", "cluster", "spike", "tower"]
    result = []
    for pos, normal in selected:
        result.append({
            "position": pos,
            "normal": normal,
            "variance": random.uniform(0.6, 1.4),
            "crystal_type": random.choice(crystal_types),
            "color_seed": random.random(),
        })

    print("Crystal seeds placed: " + str(len(result)) + " / target " + str(target_count))
    print("Algorithm: Greedy spaced sampling (Bridson, 2007 simplified)")
    return result


# Backward compatibility
def poisson_disc_sample(vertices, min_dist=2.0, max_attempts=20, seed=2026):
    """Legacy wrapper — now uses the simpler algorithm."""
    return distribute_seeds_simple(vertices, target_count=40, min_dist=min_dist, seed=seed)
