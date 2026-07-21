"""
Crystal Cavern — Module 1: Cave Terrain
Algorithm: Diamond-Square + procedural rock material
"""

import maya.cmds as cmds
import random
import math


def create_cave_terrain(width=50, depth=50, subdivisions=256, seed=2026,
                         wall_height=18, roughness=0.40):
    """Diamond-Square terrain deformation + rock material."""
    random.seed(seed)
    size = subdivisions + 1
    hm = [[0.0] * size for _ in range(size)]

    hm[0][0] = random.uniform(-1, 1)
    hm[0][size-1] = random.uniform(-1, 1)
    hm[size-1][0] = random.uniform(-1, 1)
    hm[size-1][size-1] = random.uniform(-1, 1)
    step = size - 1
    scale = wall_height * roughness
    while step > 1:
        half = step // 2
        for y in range(half, size, step):
            for x in range(half, size, step):
                s_val = 0.0; count = 0
                for dy in [-half, half]:
                    for dx in [-half, half]:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < size and 0 <= nx < size:
                            s_val += hm[ny][nx]; count += 1
                if count > 0:
                    hm[y][x] = s_val / count + (random.random() - 0.5) * scale
        for y in range(0, size, half):
            for x in range((y + half) % step, size, step):
                s_val = 0.0; count = 0
                for dy, dx in [(-half, 0), (half, 0), (0, -half), (0, half)]:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < size and 0 <= nx < size:
                        s_val += hm[ny][nx]; count += 1
                if count > 0:
                    hm[y][x] = s_val / count + (random.random() - 0.5) * scale
        step = half; scale *= roughness ** 1.8

    # Clean up existing terrain to avoid duplicates on re-runs
    if cmds.objExists("cave_terrain"):
        try:
            cmds.delete("cave_terrain")
        except (RuntimeError, ValueError):
            pass

    terrain = cmds.polyPlane(name="cave_terrain", width=width, height=depth,
                              subdivisionsWidth=subdivisions,
                              subdivisionsHeight=subdivisions,
                              axis=[0, 1, 0])[0]

    for i in range(size):
        for j in range(size):
            vtx = terrain + ".vtx[" + str(i * size + j) + "]"
            h = hm[i][j]
            cx = (i / subdivisions - 0.5) * width
            cz = (j / subdivisions - 0.5) * depth
            dist = math.sqrt(cx*cx + cz*cz) / (depth * 0.5)
            cave_y = h * (1.0 - dist) - wall_height * dist ** 1.5 + \
                     math.sin(cx * 0.3) * math.cos(cz * 0.3) * 2.0
            cmds.move(cx, cave_y, cz, vtx, relative=False, worldSpace=True)

    cmds.polyNormal(terrain, normalMode=2, userNormalMode=0, ch=1)
    cmds.polySoftEdge(terrain, angle=45, constructionHistory=1)

    # Rock material (reuse existing if present to avoid material bloat)
    arnold_ok = False
    try:
        arnold_ok = cmds.pluginInfo("mtoa", query=True, loaded=True)
    except (RuntimeError, ValueError):
        pass
    if arnold_ok:
        try:
            shader_name = "cave_rock_shader"
            if cmds.objExists(shader_name):
                shader = shader_name
            else:
                shader = cmds.createNode("aiStandardSurface", name=shader_name)
            cmds.setAttr(shader + ".baseColor", 0.15, 0.12, 0.10)
            cmds.setAttr(shader + ".specularRoughness", 0.75)
            cmds.setAttr(shader + ".specular", 0.1)
            cmds.setAttr(shader + ".subsurface", 0.15)
            cmds.setAttr(shader + ".subsurfaceColor", 0.08, 0.06, 0.05)
            sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="cave_rock_SG")
            cmds.connectAttr(shader + ".outColor", sg + ".surfaceShader", force=True)
            cmds.select(terrain); cmds.hyperShade(assign=shader)
        except (RuntimeError, ValueError, ImportError):
            arnold_ok = False

    if not arnold_ok:
        shader = cmds.shadingNode("lambert", asShader=True, name="cave_rock_lambert")
        cmds.setAttr(shader + ".color", 0.15, 0.12, 0.10, type="double3")
        cmds.setAttr(shader + ".ambientColor", 0.04, 0.03, 0.02, type="double3")
        cmds.select(terrain); cmds.hyperShade(assign=shader)

    print("Cave terrain generated: " + terrain)
    return terrain, hm


def create_cave_enclosure(terrain_name="cave_terrain", width=50, depth=50,
                          wall_height=12, ceiling_height=8.0):
    """Build cave walls and ceiling to enclose the terrain into a cavern.

    Creates 4 wall planes and a ceiling, all with matching rock material.
    Walls extend downward slightly below the terrain edges and rise up
    to the specified height. The ceiling curves inward for a natural cave feel.

    Returns name of the enclosure parent group.
    """
    # Clean stale enclosure
    for obj_name in ["cave_enclosure", "cave_wall_N", "cave_wall_S",
                     "cave_wall_E", "cave_wall_W", "cave_ceiling"]:
        if cmds.objExists(obj_name):
            try:
                cmds.delete(obj_name)
            except Exception:
                pass

    grp = cmds.group(empty=True, name="cave_enclosure")

    half_w = width / 2.0
    half_d = depth / 2.0

    # ── Wall material (reuse existing to avoid material bloat) ──
    arnold_ok = cmds.pluginInfo("mtoa", query=True, loaded=True)
    if arnold_ok:
        try:
            wall_name = "cave_wall_shader"
            if cmds.objExists(wall_name):
                wall_shader = wall_name
            else:
                wall_shader = cmds.createNode("aiStandardSurface", name=wall_name)
            cmds.setAttr(wall_shader + ".baseColor", 0.10, 0.08, 0.06)
            cmds.setAttr(wall_shader + ".specularRoughness", 0.8)
            cmds.setAttr(wall_shader + ".specular", 0.05)
            cmds.setAttr(wall_shader + ".subsurface", 0.1)
            cmds.setAttr(wall_shader + ".subsurfaceColor", 0.05, 0.04, 0.03)
            wall_sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True,
                                name="cave_wall_SG")
            cmds.connectAttr(wall_shader + ".outColor", wall_sg + ".surfaceShader",
                             force=True)
        except (RuntimeError, ValueError):
            wall_shader = cmds.shadingNode("lambert", asShader=True,
                                           name="cave_wall_lambert")
            cmds.setAttr(wall_shader + ".color", 0.10, 0.08, 0.06, type="double3")
            cmds.setAttr(wall_shader + ".ambientColor", 0.03, 0.02, 0.01, type="double3")
    else:
        wall_shader = cmds.shadingNode("lambert", asShader=True,
                                       name="cave_wall_lambert")
        cmds.setAttr(wall_shader + ".color", 0.10, 0.08, 0.06, type="double3")
        cmds.setAttr(wall_shader + ".ambientColor", 0.03, 0.02, 0.01, type="double3")

    # ── Four walls ──
    walls = []
    # North wall (Z+)
    n_wall = cmds.polyPlane(name="cave_wall_N", width=width + 2,
                             height=wall_height,
                             subdivisionsWidth=20, subdivisionsHeight=8,
                             axis=[0, 1, 0])[0]
    cmds.move(0, wall_height / 2.0 - 1, half_d + 1, n_wall)
    cmds.rotate(0, 0, 0, n_wall)
    walls.append(n_wall)

    # South wall (Z-)
    s_wall = cmds.polyPlane(name="cave_wall_S", width=width + 2,
                             height=wall_height,
                             subdivisionsWidth=20, subdivisionsHeight=8,
                             axis=[0, 1, 0])[0]
    cmds.move(0, wall_height / 2.0 - 1, -half_d - 1, s_wall)
    cmds.rotate(0, 180, 0, s_wall)
    walls.append(s_wall)

    # East wall (X+)
    e_wall = cmds.polyPlane(name="cave_wall_E", width=depth + 2,
                             height=wall_height,
                             subdivisionsWidth=20, subdivisionsHeight=8,
                             axis=[0, 1, 0])[0]
    cmds.move(half_w + 1, wall_height / 2.0 - 1, 0, e_wall)
    cmds.rotate(0, 90, 0, e_wall)
    walls.append(e_wall)

    # West wall (X-)
    w_wall = cmds.polyPlane(name="cave_wall_W", width=depth + 2,
                             height=wall_height,
                             subdivisionsWidth=20, subdivisionsHeight=8,
                             axis=[0, 1, 0])[0]
    cmds.move(-half_w - 1, wall_height / 2.0 - 1, 0, w_wall)
    cmds.rotate(0, -90, 0, w_wall)
    walls.append(w_wall)

    # ── Ceiling ──
    ceiling = cmds.polyPlane(name="cave_ceiling", width=width + 4,
                              height=depth + 4,
                              subdivisionsWidth=30, subdivisionsHeight=30,
                              axis=[0, 1, 0])[0]
    # Rotate to face downward
    cmds.rotate(180, 0, 0, ceiling)
    cmds.move(0, ceiling_height, 0, ceiling)

    # Deform ceiling inward (dome-like) by moving vertices down at center
    ceil_vtx_count = cmds.polyEvaluate(ceiling, vertex=True)
    ceil_subdivs = int(math.sqrt(ceil_vtx_count))
    if ceil_subdivs > 0:
        for cv in range(ceil_vtx_count):
            try:
                vtx_name = ceiling + ".vtx[" + str(cv) + "]"
                pos = cmds.xform(vtx_name, query=True, translation=True,
                                 worldSpace=True)
                # Distance from center
                cdist = math.sqrt(pos[0]**2 + pos[2]**2) / (max(width, depth) * 0.6)
                # Dome deformation: center pushes down
                dome_drop = (1.0 - min(cdist, 1.0)) * 3.0
                cmds.move(0, -dome_drop, 0, vtx_name, relative=True,
                          worldSpace=True)
            except (RuntimeError, ValueError):
                pass

    # ── Parent all walls and ceiling, apply material ──
    for wall in walls + [ceiling]:
        cmds.parent(wall, grp)
        cmds.select(wall)
        try:
            cmds.hyperShade(assign=wall_shader)
        except (RuntimeError, ValueError):
            pass
        # Soft edges for organic feel
        try:
            cmds.polySoftEdge(wall, angle=60, constructionHistory=0)
        except (RuntimeError, ValueError):
            pass

    # Add subtle random vertex jitter to walls for organic cave feel
    for wall in walls:
        try:
            vtx_count = cmds.polyEvaluate(wall, vertex=True)
            for _ in range(vtx_count // 3):  # jitter ~1/3 of vertices
                vi = random.randint(0, vtx_count - 1)
                vname = wall + ".vtx[" + str(vi) + "]"
                cmds.move(random.uniform(-0.3, 0.3),
                         random.uniform(-0.2, 0.2),
                         random.uniform(-0.3, 0.3),
                         vname, relative=True, worldSpace=True)
        except (RuntimeError, ValueError):
            pass

    # Generate stalactites and stalagmites
    create_stalactites(ceiling_name="cave_ceiling", terrain_name=terrain_name,
                       parent_group=grp)

    print("Cave enclosure: 4 walls + domed ceiling")
    return grp


def create_stalactites(ceiling_name="cave_ceiling", terrain_name="cave_terrain",
                       count=30, parent_group="cave_enclosure"):
    """Generate stalactites (hanging from ceiling) and stalagmites (rising from floor).

    Stalactites are sampled from random ceiling vertices and hang downward.
    Stalagmites are sampled from low-elevation terrain vertices (y < -2) and
    rise upward. Both use hexagonal polyCone shapes with soft edges for an
    organic cave feel.

    Returns (stalactite_group, stalagmite_group).
    """
    # --- Clean existing groups ---
    for grp_name in ["stalactites", "stalagmites"]:
        if cmds.objExists(grp_name):
            try:
                cmds.delete(grp_name)
            except Exception:
                pass

    # --- Parent groups ---
    stal_group = cmds.group(empty=True, name="stalactites")
    if cmds.objExists(parent_group):
        cmds.parent(stal_group, parent_group)
    stag_group = cmds.group(empty=True, name="stalagmites")
    if cmds.objExists(parent_group):
        cmds.parent(stag_group, parent_group)

    # --- Material (reuse cave_wall_shader if it exists) ---
    if cmds.objExists("cave_wall_shader"):
        mat = "cave_wall_shader"
    elif cmds.objExists("cave_wall_lambert"):
        mat = "cave_wall_lambert"
    else:
        mat = cmds.shadingNode("lambert", asShader=True, name="cave_wall_lambert")
        cmds.setAttr(mat + ".color", 0.10, 0.08, 0.06, type="double3")

    # --- Stalactites: downward-pointing hexagonal cones from ceiling ---
    stal_count = 0
    if cmds.objExists(ceiling_name):
        try:
            ceil_vtx_count = cmds.polyEvaluate(ceiling_name, vertex=True)
            sample_n = min(count, ceil_vtx_count)
            sample_indices = random.sample(range(ceil_vtx_count), sample_n)

            for i in sample_indices:
                vtx = ceiling_name + ".vtx[%d]" % i
                pos = cmds.xform(vtx, query=True, translation=True,
                                 worldSpace=True)
                r = random.uniform(0.15, 0.5)
                h = random.uniform(0.5, 3.0)
                cone = cmds.polyCone(r=r, h=h, sx=6, sy=2, roundCap=False,
                                     axis=[0, -1, 0])[0]
                # Base at ceiling vertex, cone points downward
                cmds.move(pos[0], pos[1], pos[2], cone)
                # Subtle random tilt for organic variety
                cmds.rotate(random.uniform(-10, 10), random.uniform(0, 360),
                            random.uniform(-10, 10), cone)
                cmds.polySoftEdge(cone, angle=180, constructionHistory=0)
                cmds.parent(cone, stal_group)
                cmds.select(cone)
                try:
                    cmds.hyperShade(assign=mat)
                except Exception:
                    pass
                stal_count += 1
        except Exception as e:
            print("Stalactite generation error: " + str(e))

    # --- Stalagmites: upward-pointing hexagonal cones from low terrain ---
    stag_count = 0
    if cmds.objExists(terrain_name):
        try:
            terrain_vtx_count = cmds.polyEvaluate(terrain_name, vertex=True)
            # Sample a pool of random vertices to find low-elevation ones
            pool_size = min(500, terrain_vtx_count)
            pool_indices = random.sample(range(terrain_vtx_count), pool_size)
            low_vertices = []
            for i in pool_indices:
                vtx = terrain_name + ".vtx[%d]" % i
                pos = cmds.xform(vtx, query=True, translation=True,
                                 worldSpace=True)
                if pos[1] < -2:
                    low_vertices.append((vtx, pos))

            sample_count = count // 2
            random.shuffle(low_vertices)
            sample_vtx = low_vertices[:min(sample_count, len(low_vertices))]

            for _vtx, pos in sample_vtx:
                r = random.uniform(0.2, 0.6)
                h = random.uniform(0.5, 2.5)
                cone = cmds.polyCone(r=r, h=h, sx=6, sy=2, roundCap=False,
                                     axis=[0, 1, 0])[0]
                # Base at terrain vertex, cone points upward
                cmds.move(pos[0], pos[1], pos[2], cone)
                cmds.rotate(random.uniform(-10, 10), random.uniform(0, 360),
                            random.uniform(-10, 10), cone)
                cmds.polySoftEdge(cone, angle=180, constructionHistory=0)
                cmds.parent(cone, stag_group)
                cmds.select(cone)
                try:
                    cmds.hyperShade(assign=mat)
                except Exception:
                    pass
                stag_count += 1
        except Exception as e:
            print("Stalagmite generation error: " + str(e))

    print("Stalactites created: %d | Stalagmites created: %d" % (stal_count, stag_count))
    return stal_group, stag_group
