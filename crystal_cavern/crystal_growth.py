"""
Crystal Cavern — Module 3: Crystal Growth v2

Improvements over v1:
- Faceted hexagonal crystal bodies (polyCone 6-sided) instead of cylinders
- Sharp pointed termination tips for realistic crystal look
- Crystal clusters: multiple crystals growing from each seed at varied angles
- Enhanced Arnold material: higher transmission, proper IOR, thin-film coat
- Returns light anchor positions for precise accent light placement

References:
- Prusinkiewicz, P., & Lindenmayer, A. (1990). The Algorithmic Beauty of Plants.
- Jensen, H. W. et al. (2001). A practical model for subsurface light transport.
"""

import maya.cmds as cmds
import random
import math

# ── Gem Presets ──────────────────────────────────────────────────────
# color = base crystal color, glow = subsurface/emission tint, ior = refraction index

GEM_PRESETS = [
    {"name": "amethyst",   "color": (0.45, 0.15, 0.60), "glow": (0.20, 0.10, 0.35), "ior": 1.54},
    {"name": "citrine",    "color": (0.80, 0.55, 0.15), "glow": (0.40, 0.28, 0.08), "ior": 1.54},
    {"name": "fluorite",   "color": (0.15, 0.55, 0.38), "glow": (0.08, 0.35, 0.22), "ior": 1.43},
    {"name": "aquamarine", "color": (0.12, 0.45, 0.62), "glow": (0.06, 0.30, 0.45), "ior": 1.58},
    {"name": "rose_quartz","color": (0.72, 0.42, 0.48), "glow": (0.40, 0.22, 0.25), "ior": 1.54},
    {"name": "obsidian",   "color": (0.06, 0.05, 0.08), "glow": (0.02, 0.01, 0.03), "ior": 1.49},
    {"name": "emerald",    "color": (0.08, 0.52, 0.28), "glow": (0.04, 0.35, 0.18), "ior": 1.57},
    {"name": "ruby",       "color": (0.72, 0.08, 0.12), "glow": (0.50, 0.05, 0.08), "ior": 1.77},
    {"name": "sapphire",   "color": (0.08, 0.15, 0.55), "glow": (0.04, 0.10, 0.40), "ior": 1.77},
    {"name": "topaz",      "color": (0.72, 0.50, 0.15), "glow": (0.35, 0.25, 0.06), "ior": 1.62},
]

# ── Crystal Type Definitions ─────────────────────────────────────────
# (base_height, min_side_crystals, max_side_crystals, side_scale, tip_ratio)

CRYSTAL_TYPES = {
    "spike":    {"height_m": 4,  "height_M": 14,  "sides": 1, "side_M": 3,
                  "side_scale": 0.25, "width": 0.20, "tip": 0.25},
    "tower":    {"height_m": 10, "height_M": 22,  "sides": 2, "side_M": 6,
                  "side_scale": 0.35, "width": 0.55, "tip": 0.18},
    "cluster":  {"height_m": 3,  "height_M": 10,  "sides": 3, "side_M": 10,
                  "side_scale": 0.40, "width": 0.30, "tip": 0.30},
    "prism":    {"height_m": 6,  "height_M": 16,  "sides": 1, "side_M": 4,
                  "side_scale": 0.28, "width": 0.40, "tip": 0.15},
}


# ── Material Cache ───────────────────────────────────────────────────
# Reuse materials per gem type to avoid material bloat across re-runs.

_material_cache = {}


def _get_or_create_material(preset):
    """Return existing material for this gem type, or create one if not cached."""
    gem_name = preset["name"]
    if gem_name in _material_cache:
        if cmds.objExists(_material_cache[gem_name]):
            return _material_cache[gem_name]

    shader_name = "gem_" + gem_name + "_shared"
    # Clean up old instance if it exists but wasn't in cache
    if cmds.objExists(shader_name):
        try:
            cmds.delete(shader_name)
        except Exception:
            pass

    mat = _create_material_shader(preset, shader_name)
    _material_cache[gem_name] = mat
    return mat


def _clear_material_cache():
    """Clear the material cache (call before full re-generation)."""
    _material_cache.clear()


def _create_material_shader(preset, name):
    """Create a glass-like crystal material. Internal — use _get_or_create_material."""
    arnold_available = cmds.pluginInfo("mtoa", query=True, loaded=True)

    if arnold_available:
        try:
            shader = cmds.createNode("aiStandardSurface", name=name)
            cmds.setAttr(shader + ".base", 0.7)
            r, g, b = preset["color"]
            cmds.setAttr(shader + ".baseColor", r, g, b)
            cmds.setAttr(shader + ".specular", 1.0)
            cmds.setAttr(shader + ".specularRoughness", 0.08)
            cmds.setAttr(shader + ".specularIOR", preset.get("ior", 1.55))
            cmds.setAttr(shader + ".specularColor", 1.0, 0.98, 0.95)
            cmds.setAttr(shader + ".transmission", 0.55)
            cmds.setAttr(shader + ".transmissionDepth", 2.0)
            cmds.setAttr(shader + ".transmissionColor", r * 0.6, g * 0.6, b * 0.6)
            gr, gg, gb = preset["glow"]
            cmds.setAttr(shader + ".subsurface", 0.7)
            cmds.setAttr(shader + ".subsurfaceColor", gr, gg, gb)
            cmds.setAttr(shader + ".subsurfaceRadius", 0.4, 0.4, 0.4)
            cmds.setAttr(shader + ".subsurfaceScale", 2.5)
            cmds.setAttr(shader + ".coat", 0.3)
            cmds.setAttr(shader + ".coatRoughness", 0.03)
            cmds.setAttr(shader + ".coatIOR", 1.4)
            try:
                cmds.setAttr(shader + ".dispersionAbbe", 45)
            except (RuntimeError, ValueError):
                pass
            cmds.setAttr(shader + ".emission", 0.15)
            cmds.setAttr(shader + ".emissionColor", gr * 0.5, gg * 0.5, gb * 0.5)
            sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True,
                           name=name + "_SG")
            cmds.connectAttr(shader + ".outColor", sg + ".surfaceShader", force=True)
            return shader
        except (RuntimeError, ValueError):
            pass

    # Lambert fallback
    shader = cmds.shadingNode("lambert", asShader=True, name=name)
    r, g, b = preset["color"]
    cmds.setAttr(shader + ".color", r, g, b, type="double3")
    cmds.setAttr(shader + ".transparency", 0.35, 0.40, 0.45)
    gr, gg, gb = preset["glow"]
    cmds.setAttr(shader + ".ambientColor", gr * 0.5, gg * 0.5, gb * 0.5)
    return shader


# ── Crystal Geometry ─────────────────────────────────────────────────

def create_crystal(position, normal, crystal_type, variance, preset_index,
                   parent="crystal_group"):
    """Create a faceted crystal formation at the given position.

    Builds hexagonal crystal body + pointed tip using polyCone.
    Adds side crystals growing at varied angles for cluster look.
    Returns (group_name, light_anchor_position).
    """
    preset = GEM_PRESETS[preset_index % len(GEM_PRESETS)]
    type_def = CRYSTAL_TYPES.get(crystal_type, CRYSTAL_TYPES["prism"])

    # Normalize direction vector
    nl = math.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2)
    nx, ny, nz = normal[0] / nl, normal[1] / nl, normal[2] / nl

    # Calculate crystal parameters with variance
    h_min, h_max = type_def["height_m"], type_def["height_M"]
    height = h_min + (h_max - h_min) * variance
    width = type_def["width"] * variance
    side_count = random.randint(type_def["sides"], type_def["side_M"])
    tip_ratio = type_def["tip"]

    # Unique IDs
    uid = random.randint(10000, 99999)
    grp_name = "crystal_" + crystal_type + "_" + str(uid)
    grp = cmds.group(empty=True, name=grp_name)
    if cmds.objExists(parent):
        cmds.parent(grp, parent)

    # Shared material for this formation (reuses per gem type)
    mat = _get_or_create_material(preset)

    # Light anchor: slightly above the crystal midpoint
    light_anchor = None

    # ── Main crystal body ──
    body_height = height * (1.0 - tip_ratio)
    # Use polyCone with 6 sides for hexagonal prism shape
    body_result = cmds.polyCone(
        name="cry_body_" + str(uid),
        radius=width,
        height=body_height,
        subdivisionsAxis=6,    # hexagonal
        subdivisionsHeight=1,
        roundCap=False,
    )
    body = body_result[0]

    # Position body so its base embeds into the terrain for a natural
    # "grown from rock" look. Without embed, the flat bottom face sits
    # exactly on the terrain vertex and appears to float because the
    # surrounding terrain dips below.
    body_half = body_height / 2.0
    body_embed = body_height * 0.12  # embed 12% into terrain
    body_center_dist = body_half - body_embed
    bx = position[0] + nx * body_center_dist
    by = position[1] + ny * body_center_dist
    bz = position[2] + nz * body_center_dist

    cmds.xform(body, translation=(bx, by, bz), worldSpace=True)

    # Widen the base vertices before rotation for a natural
    # "grown from rock" root
    _widen_crystal_root(body, factor=1.3)

    # Rotate to align with surface normal
    _align_to_normal(body, nx, ny, nz)

    cmds.parent(body, grp)
    cmds.select(body)
    try:
        cmds.hyperShade(assign=mat)
    except (RuntimeError, ValueError):
        pass

    # ── Pointed tip ──
    tip_height = height * tip_ratio
    tip_result = cmds.polyCone(
        name="cry_tip_" + str(uid),
        radius=width * 0.9,    # slightly smaller to create a shoulder
        height=tip_height,
        subdivisionsAxis=6,
        subdivisionsHeight=2,
        roundCap=False,
    )
    tip = tip_result[0]

    # Tip sits on top of the body. The body top face is at
    # (body_height - body_embed) above the seed vertex along the normal,
    # since the body was embedded into the terrain. The tip's center is
    # offset by half its own height above that.
    tip_center_dist = body_height - body_embed + tip_height / 2.0
    tx = position[0] + nx * tip_center_dist
    ty = position[1] + ny * tip_center_dist
    tz = position[2] + nz * tip_center_dist

    cmds.xform(tip, translation=(tx, ty, tz), worldSpace=True)
    _align_to_normal(tip, nx, ny, nz)
    cmds.parent(tip, grp)
    cmds.select(tip)
    try:
        cmds.hyperShade(assign=mat)
    except (RuntimeError, ValueError):
        pass

    # Light anchor: at 60% height of the crystal (good illumination point)
    light_anchor = (
        position[0] + nx * height * 0.6,
        position[1] + ny * height * 0.6,
        position[2] + nz * height * 0.6,
    )

    # ── Side crystals ──
    for s in range(side_count):
        try:
            _create_side_crystal(position, normal, height, width, variance,
                                 preset, mat, uid, s, grp)
        except (RuntimeError, ValueError):
            pass

    # Store light anchor as an attribute on the group for lighting module
    cmds.addAttr(grp, longName="lightAnchorX", attributeType="double",
                 defaultValue=light_anchor[0], keyable=False)
    cmds.addAttr(grp, longName="lightAnchorY", attributeType="double",
                 defaultValue=light_anchor[1], keyable=False)
    cmds.addAttr(grp, longName="lightAnchorZ", attributeType="double",
                 defaultValue=light_anchor[2], keyable=False)
    cmds.addAttr(grp, longName="glowR", attributeType="double",
                 defaultValue=preset["glow"][0], keyable=False)
    cmds.addAttr(grp, longName="glowG", attributeType="double",
                 defaultValue=preset["glow"][1], keyable=False)
    cmds.addAttr(grp, longName="glowB", attributeType="double",
                 defaultValue=preset["glow"][2], keyable=False)
    cmds.addAttr(grp, longName="crystalHeight", attributeType="double",
                 defaultValue=height, keyable=False)

    return grp, light_anchor


def _create_side_crystal(base_pos, normal, main_height, main_width, variance,
                         preset, mat, uid, index, grp):
    """Create a smaller side crystal branching from the main stem."""
    nx = normal[0]
    ny = normal[1]
    nz = normal[2]

    # Side crystal grows from 15%-60% up the main crystal
    branch_origin_t = 0.15 + random.uniform(0, 0.45)
    # Deviate from main normal by 20-55 degrees
    deviation = random.uniform(0.35, 0.95)  # radians
    # Rotate around the normal axis for azimuthal spread
    azimuth = random.uniform(0, 2 * math.pi)

    # Calculate perpendicular vectors to the normal for rotation
    if abs(nx) < 0.9:
        perp1 = (0, -nz, ny)  # cross with (1,0,0)
    else:
        perp1 = (-nz, 0, nx)  # cross with (0,1,0)
    pl = math.sqrt(perp1[0]**2 + perp1[1]**2 + perp1[2]**2)
    perp1 = (perp1[0] / pl, perp1[1] / pl, perp1[2] / pl)

    # Second perpendicular (cross product of normal and perp1)
    perp2 = (
        ny * perp1[2] - nz * perp1[1],
        nz * perp1[0] - nx * perp1[2],
        nx * perp1[1] - ny * perp1[0],
    )

    # Branch direction: rotate normal by deviation, then around by azimuth
    bn_x = nx * math.cos(deviation) + perp1[0] * math.sin(deviation) * math.cos(azimuth) + perp2[0] * math.sin(deviation) * math.sin(azimuth)
    bn_y = ny * math.cos(deviation) + perp1[1] * math.sin(deviation) * math.cos(azimuth) + perp2[1] * math.sin(deviation) * math.sin(azimuth)
    bn_z = nz * math.cos(deviation) + perp1[2] * math.sin(deviation) * math.cos(azimuth) + perp2[2] * math.sin(deviation) * math.sin(azimuth)

    # Normalize branch direction
    bl = math.sqrt(bn_x**2 + bn_y**2 + bn_z**2)
    bn_x, bn_y, bn_z = bn_x / bl, bn_y / bl, bn_z / bl

    # Branch position on main stem
    bp_x = base_pos[0] + nx * main_height * branch_origin_t
    bp_y = base_pos[1] + ny * main_height * branch_origin_t
    bp_z = base_pos[2] + nz * main_height * branch_origin_t

    # Branch size: 25%-50% of main
    side_scale = random.uniform(0.20, 0.45)
    side_height = main_height * side_scale
    side_width = main_width * 0.5 * side_scale

    # Create side crystal as a sharp cone
    side_result = cmds.polyCone(
        name="cry_side_" + str(uid) + "_" + str(index),
        radius=side_width,
        height=side_height,
        subdivisionsAxis=6,
        subdivisionsHeight=1,
        roundCap=False,
    )
    side_obj = side_result[0]

    # Position side crystal
    side_mid = side_height / 2.0
    sx = bp_x + bn_x * side_mid
    sy = bp_y + bn_y * side_mid
    sz = bp_z + bn_z * side_mid

    cmds.xform(side_obj, translation=(sx, sy, sz), worldSpace=True)
    _align_to_normal(side_obj, bn_x, bn_y, bn_z)
    cmds.parent(side_obj, grp)
    cmds.select(side_obj)
    try:
        cmds.hyperShade(assign=mat)
    except (RuntimeError, ValueError):
        pass


def _align_to_normal(obj, nx, ny, nz):
    """Rotate obj so its local Y+ axis points along (nx, ny, nz).

    Uses a temporary aim constraint for reliable Maya rotation matrix math,
    then bakes the result and deletes the constraint. This avoids gimbal
    lock issues that plague manual Euler-angle calculations.
    """
    # Create a temporary locator at the target direction
    loc = cmds.spaceLocator(name="tmp_aim_loc_" + str(random.randint(10000, 99999)))[0]
    obj_pos = cmds.xform(obj, query=True, translation=True, worldSpace=True)
    cmds.xform(loc, translation=(
        obj_pos[0] + nx * 10,
        obj_pos[1] + ny * 10,
        obj_pos[2] + nz * 10,
    ), worldSpace=True)

    try:
        # Aim the object's Y+ at the locator
        aim = cmds.aimConstraint(
            loc, obj,
            aimVector=(0, 1, 0),      # Y+ is "up" for polyCone
            upVector=(0, 0, 1),       # Z as up reference
            worldUpType="vector",
            worldUpVector=(0, 0, 1),
        )
        # Bake rotation and remove constraint
        cmds.delete(aim)
    except (RuntimeError, ValueError):
        pass
    finally:
        try:
            cmds.delete(loc)
        except (RuntimeError, ValueError):
            pass

    # Add subtle random variation
    cmds.xform(obj, rotation=(
        random.uniform(-5, 5),
        random.uniform(-5, 5),
        random.uniform(-8, 8),
    ), relative=True)


def _widen_crystal_root(mesh_name, factor=1.3):
    """Widen the base ring of vertices on a polyCone mesh.

    Selects the bottom ring of vertices (lowest Y in object space)
    and scales them outward from the cone center by the given factor.
    This creates the visual impression that the crystal grew from the
    surrounding rock rather than sitting on top of it.

    Must be called BEFORE the mesh is rotated by _align_to_normal,
    while the cone's local Y axis is still aligned with world Y.

    Args:
        mesh_name: Name of the polyCone transform/mesh node.
        factor: Scale factor for the base vertices (default 1.3).
    """
    vtx_count = cmds.polyEvaluate(mesh_name, vertex=True)
    if vtx_count == 0:
        return

    # Identify the bottom ring: vertices with the lowest Y in object space.
    bottom_verts = []
    min_y = float("inf")

    for i in range(vtx_count):
        vtx = mesh_name + ".vtx[" + str(i) + "]"
        pos = cmds.xform(vtx, query=True, translation=True, objectSpace=True)
        if pos[1] < min_y - 0.0001:
            min_y = pos[1]
            bottom_verts = [vtx]
        elif abs(pos[1] - min_y) < 0.0001:
            bottom_verts.append(vtx)

    if not bottom_verts:
        return

    # Scale each bottom vertex outward from the Y axis (cone center)
    # by multiplying its X and Z coordinates in object space.
    for vtx in bottom_verts:
        pos = cmds.xform(vtx, query=True, translation=True, objectSpace=True)
        cmds.xform(
            vtx,
            translation=(pos[0] * factor, pos[1], pos[2] * factor),
            objectSpace=True,
        )


# ── Grow All ─────────────────────────────────────────────────────────

def grow_all_crystals(seeds, parent_group="crystal_group",
                      type_mix="Mixed", color_seed=None):
    """Grow all crystal formations from seed list.

    Args:
        seeds: List of seed dicts with position, normal, crystal_type, variance.
        parent_group: Name of the parent transform group.
        type_mix: Crystal type preference ("Mixed", "Mostly Spikes", etc.).
        color_seed: If set, randomises preset-to-crystal assignment.

    Returns:
        tuple: (crystal_count, light_anchors_list)
            light_anchors is list of (position, glow_color) tuples for lighting.
    """
    if cmds.objExists(parent_group):
        cmds.delete(parent_group)
    cmds.group(empty=True, name=parent_group)

    # Clear material cache so re-runs get fresh shared materials
    _clear_material_cache()

    # Clean orphaned gem shaders from previous runs (old naming scheme)
    for shader in (cmds.ls(type="aiStandardSurface") or []):
        name = str(shader)
        if name.startswith("gem_") and "shared" not in name:
            try:
                cmds.delete(shader)
            except (RuntimeError, ValueError):
                pass
    for sg in (cmds.ls(type="shadingEngine") or []):
        name = str(sg)
        if name.startswith("gem_") and "shared" not in name:
            try:
                cmds.delete(sg)
            except (RuntimeError, ValueError):
                pass

    # ── Apply type mix preference to seeds ──
    type_bias = {
        "Mostly Spikes":  ["spike", "spike", "spike", "spike", "tower", "cluster", "prism"],
        "Mostly Clusters":["cluster", "cluster", "cluster", "cluster", "spike", "tower", "prism"],
        "Mostly Towers":  ["tower", "tower", "tower", "tower", "spike", "cluster", "prism"],
        "Mostly Prisms":  ["prism", "prism", "prism", "prism", "tower", "spike", "cluster"],
    }.get(type_mix)
    if type_bias:
        for s in seeds:
            s["crystal_type"] = random.choice(type_bias)

    # ── Apply color seed to shuffle preset assignment ──
    if color_seed is not None:
        rng_state = random.getstate()
        random.seed(int(color_seed))
        preset_indices = list(range(len(seeds)))
        random.shuffle(preset_indices)
        random.setstate(rng_state)
    else:
        preset_indices = None

    count = 0
    light_anchors = []

    for i, s in enumerate(seeds):
        try:
            preset_index = preset_indices[i] if preset_indices else i
            grp, anchor = create_crystal(
                s["position"], s["normal"], s["crystal_type"],
                s["variance"], preset_index, parent=parent_group
            )
            if anchor:
                glow_r = GEM_PRESETS[preset_index % len(GEM_PRESETS)]["glow"]
                light_anchors.append((anchor, glow_r))
            count += 1
        except Exception as e:
            print("   Crystal " + str(i) + " failed: " + str(e))

    print("Crystal growth complete: " + str(count) + " formations")
    return count, light_anchors
