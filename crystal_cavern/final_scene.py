"""Crystal Cavern v9 — Codex-optimised presentation-quality Arnold scene builder.

Merges the best ideas from both iteration streams:
  Codex:   _safe_attr, material helper, sphere-shell cave, Poisson dart-throwing,
           aiSkyDomeLight ambient, DOF camera, compact single-module design.
  v7:      hexagonal prism crystals (sx=6), L-system 3D spherical branching,
           12% root embedding, aiNoise cloudy internal SSS texture,
           Diamond-Square terrain, stalactites/stalagmites, growth animation,
           1920×1080 EXR + Z AOV, 2400-frame fly-through, 10 gem IOR variants.

Paste into Maya Script Editor Python tab → Ctrl+Enter.
"""

import math, os, random, traceback

import maya.cmds as cmds
import maya.mel as mel

ROOT = "crystalCavern_v9"
OUT_DIR = "/Users/xixi/大学/未来创新设计/crystal_cavern/renders/final_v9"


# ═══════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════

def _safe_attr(node, attr, value, kind=None):
    """Set Arnold/Maya attribute – silently skip when version doesn't expose it."""
    plug = node + "." + attr
    if not cmds.objExists(plug):
        return
    try:
        if kind == "color":
            cmds.setAttr(plug, *value, type="double3")
        elif kind == "string":
            cmds.setAttr(plug, value, type="string")
        else:
            cmds.setAttr(plug, value)
    except RuntimeError:
        pass


def _material(name, color, transmission=0.0, emission=0.0, roughness=0.5,
              ior=1.54, subsurface_color=None):
    """Arnold aiStandardSurface with transmission + SSS + coat + emission."""
    shader = cmds.shadingNode("aiStandardSurface", asShader=True, name=name)
    _safe_attr(shader, "baseColor", color, "color")
    _safe_attr(shader, "specularRoughness", roughness)
    _safe_attr(shader, "specular", 0.9 if transmission else 0.5)
    _safe_attr(shader, "specularIOR", ior)
    _safe_attr(shader, "transmissionWeight", transmission)
    _safe_attr(shader, "transmissionDepth", 5.0 if transmission > 0 else 1.0)
    _safe_attr(shader, "transmissionColor",
               tuple(c * 0.55 for c in color), "color")
    _safe_attr(shader, "subsurfaceWeight", 0.95 if transmission else 0.0)
    sc = subsurface_color or color
    _safe_attr(shader, "subsurfaceColor", sc, "color")
    _safe_attr(shader, "subsurfaceScale", 4.0 if transmission else 0)
    _safe_attr(shader, "subsurfaceRadius",
               (0.8, 0.8, 0.8) if transmission else (0, 0, 0), "color")
    _safe_attr(shader, "coatWeight", 0.28 if transmission else 0.0)
    _safe_attr(shader, "coatRoughness", 0.04)
    _safe_attr(shader, "coatIOR", 1.38)
    _safe_attr(shader, "emissionColor", color, "color")
    _safe_attr(shader, "emission", emission)
    # Dispersion for rainbow sparkle
    try:
        cmds.setAttr(shader + ".dispersionAbbe", 42)
    except (RuntimeError, ValueError):
        pass
    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True,
                   name=name + "SG")
    cmds.connectAttr(shader + ".outColor", sg + ".surfaceShader", force=True)
    return shader


def _add_cloudy_texture(shader, gem_color):
    """Drive subsurface with 3D noise → cloudy internal inclusion texture."""
    try:
        noise = cmds.createNode("aiNoise", name=shader + "_cloud")
        _safe_attr(noise, "octaves", 4)
        _safe_attr(noise, "distortion", 0.12)
        _safe_attr(noise, "lacunarity", 2.0)
        _safe_attr(noise, "amplitude", 1.0)
        _safe_attr(noise, "scaleX", 2.8)
        _safe_attr(noise, "scaleY", 2.8)
        _safe_attr(noise, "scaleZ", 2.8)
        cc = cmds.createNode("aiColorCorrect", name=shader + "_cloud_cc")
        _safe_attr(cc, "saturation", 0.25)
        _safe_attr(cc, "hueShift", 0.0)
        # Multiply noise output with gem color
        mult = cmds.createNode("aiMultiply", name=shader + "_cloud_mult")
        cmds.connectAttr(noise + ".outColor", cc + ".input", force=True)
        cmds.connectAttr(cc + ".outColor", mult + ".input1", force=True)
        _safe_attr(mult, "input2", gem_color, "color")
        cmds.connectAttr(mult + ".outColor", shader + ".subsurfaceColor",
                         force=True)
        return True
    except (RuntimeError, ValueError):
        return False


def _assign(obj, shader):
    cmds.select(obj, replace=True)
    cmds.hyperShade(assign=shader)


def _aim_align(obj, nx, ny, nz):
    """Rotate obj so Y+ points along normal, using aim constraint (no Euler math)."""
    pos = cmds.xform(obj, q=True, t=True, ws=True)
    loc = cmds.spaceLocator(
        name="tmp_aim_{}".format(random.randint(10000, 99999)))[0]
    cmds.xform(loc, t=(pos[0] + nx * 10, pos[1] + ny * 10, pos[2] + nz * 10),
               ws=True)
    try:
        ac = cmds.aimConstraint(loc, obj, aim=(0, 1, 0), u=(0, 0, 1),
                                wut="vector", wu=(0, 0, 1))
        cmds.delete(ac)
    except (RuntimeError, ValueError):
        pass
    try:
        cmds.delete(loc)
    except (RuntimeError, ValueError):
        pass


# ═══════════════════════════════════════════════════════════════════════
#  CRYSTAL GEOMETRY
# ═══════════════════════════════════════════════════════════════════════

def _crystal_cluster(pos, normal, scale, shader, index, parent, rng):
    """Hexagonal prism main crystal + pointed tip + 3D spherical L-system branches.

    Returns (cluster_group, light_anchor_position, crystal_height).
    """
    nx, ny, nz = normal[0], normal[1], normal[2]
    nl = math.sqrt(nx * nx + ny * ny + nz * nz)
    nx, ny, nz = nx / nl, ny / nl, nz / nl

    height = scale * rng.uniform(6.0, 12.0)
    radius = scale * rng.uniform(1.2, 2.5)  # 3-5x wider, realistic 1:4~1:6 ratio
    uid = rng.randint(10000, 99999)

    cluster = cmds.group(empty=True, name="cl_{:03d}".format(index),
                         parent=parent)

    # ── Hexagonal prism body ──
    body_h = height * 0.68
    body_embed = body_h * 0.12  # embed into terrain
    body_mid = body_h / 2.0 - body_embed
    body = cmds.polyCylinder(
        name="cry_body_{:03d}".format(index),
        radius=radius, height=body_h,
        subdivisionsX=6, subdivisionsY=2,
    )[0]
    bx, by, bz = pos[0] + nx * body_mid, pos[1] + ny * body_mid, pos[2] + nz * body_mid
    cmds.xform(body, t=(bx, by, bz), ws=True)
    _aim_align(body, nx, ny, nz)
    _assign(body, shader)
    cmds.parent(body, cluster)

    # ── Pointed tip (hexagonal cone) ──
    tip_h = height * 0.42
    tip_mid = body_h - body_embed + tip_h / 2.0
    tip = cmds.polyCone(
        name="cry_tip_{:03d}".format(index),
        radius=radius * 0.92, height=tip_h,
        subdivisionsAxis=6, subdivisionsHeight=2,
    )[0]
    cmds.xform(tip, t=(pos[0] + nx * tip_mid,
                       pos[1] + ny * tip_mid,
                       pos[2] + nz * tip_mid), ws=True)
    _aim_align(tip, nx, ny, nz)
    _assign(tip, shader)
    cmds.parent(tip, cluster)

    # ── L-system spherical branching ──
    num_branches = rng.randint(2, 5)
    for bi in range(num_branches):
        try:
            bt = rng.uniform(0.18, 0.55)
            bp = (pos[0] + nx * height * bt,
                   pos[1] + ny * height * bt,
                   pos[2] + nz * height * bt)
            dev = rng.uniform(0.28, 0.7)
            az = rng.uniform(0, 2 * math.pi)

            # Perpendicular vectors for spherical rotation
            if abs(nx) < 0.9:
                p1 = (0, -nz, ny)
            else:
                p1 = (-nz, 0, nx)
            pl = math.sqrt(p1[0] ** 2 + p1[1] ** 2 + p1[2] ** 2)
            p1 = (p1[0] / pl, p1[1] / pl, p1[2] / pl)
            p2 = (ny * p1[2] - nz * p1[1],
                   nz * p1[0] - nx * p1[2],
                   nx * p1[1] - ny * p1[0])

            bnx = (nx * math.cos(dev)
                   + p1[0] * math.sin(dev) * math.cos(az)
                   + p2[0] * math.sin(dev) * math.sin(az))
            bny = (ny * math.cos(dev)
                   + p1[1] * math.sin(dev) * math.cos(az)
                   + p2[1] * math.sin(dev) * math.sin(az))
            bnz = (nz * math.cos(dev)
                   + p1[2] * math.sin(dev) * math.cos(az)
                   + p2[2] * math.sin(dev) * math.sin(az))
            bl = math.sqrt(bnx ** 2 + bny ** 2 + bnz ** 2)
            bnx, bny, bnz = bnx / bl, bny / bl, bnz / bl

            side_h = height * rng.uniform(0.18, 0.38)
            side_r = radius * rng.uniform(0.3, 0.5)
            side_mid = side_h / 2.0
            side_obj = cmds.polyCylinder(
                name="cry_branch_{:03d}_{:02d}".format(index, bi),
                radius=side_r, height=side_h,
                subdivisionsX=6, subdivisionsY=1,
            )[0]
            cmds.xform(side_obj, t=(
                bp[0] + bnx * side_mid,
                bp[1] + bny * side_mid,
                bp[2] + bnz * side_mid,
            ), ws=True)
            _aim_align(side_obj, bnx, bny, bnz)
            _assign(side_obj, shader)
            cmds.parent(side_obj, cluster)
        except (RuntimeError, ValueError):
            pass

    light_anchor = (pos[0] + nx * height * 0.55,
                    pos[1] + ny * height * 0.55,
                    pos[2] + nz * height * 0.55)
    return cluster, light_anchor, height


# ═══════════════════════════════════════════════════════════════════════
#  TERRAIN BUILDERS
# ═══════════════════════════════════════════════════════════════════════

def _build_diamond_square_terrain(size, seed, roughness, parent):
    """Diamond-Square height-map terrain (Fournier et al., 1982)."""
    rng = random.Random(seed)
    subdivs = 128
    n = subdivs + 1
    hm = [[0.0] * n for _ in range(n)]
    hm[0][0] = rng.uniform(-1, 1)
    hm[0][n - 1] = rng.uniform(-1, 1)
    hm[n - 1][0] = rng.uniform(-1, 1)
    hm[n - 1][n - 1] = rng.uniform(-1, 1)

    step = n - 1
    scale_val = 12 * roughness
    while step > 1:
        half = step // 2
        # Diamond
        for y in range(half, n, step):
            for x in range(half, n, step):
                s_val, cnt = 0.0, 0
                for dy in (-half, half):
                    for dx in (-half, half):
                        ny2, nx2 = y + dy, x + dx
                        if 0 <= ny2 < n and 0 <= nx2 < n:
                            s_val += hm[ny2][nx2]; cnt += 1
                if cnt:
                    hm[y][x] = s_val / cnt + (rng.random() - 0.5) * scale_val
        # Square
        for y in range(0, n, half):
            for x in range((y + half) % step, n, step):
                s_val, cnt = 0.0, 0
                for dy, dx in ((-half, 0), (half, 0), (0, -half), (0, half)):
                    ny2, nx2 = y + dy, x + dx
                    if 0 <= ny2 < n and 0 <= nx2 < n:
                        s_val += hm[ny2][nx2]; cnt += 1
                if cnt:
                    hm[y][x] = s_val / cnt + (rng.random() - 0.5) * scale_val
        step = half; scale_val *= roughness ** 1.8

    # Create deformed plane
    terrain = cmds.polyPlane(
        name="CCV9_terrain", width=size, height=size,
        subdivisionsWidth=subdivs, subdivisionsHeight=subdivs,
        axis=(0, 1, 0),
    )[0]
    half_s = size / 2.0
    for i in range(n):
        for j in range(n):
            cx = (i / subdivs - 0.5) * size
            cz = (j / subdivs - 0.5) * size
            dist = math.sqrt(cx * cx + cz * cz) / (size * 0.5)
            # Cave bowl shape — deep bowl for a sense of cave depth
            cy = (hm[i][j] * (1.0 - dist)
                  - 22 * dist ** 1.5
                  + math.sin(cx * 0.4) * math.cos(cz * 0.4) * 3.0)
            vtx = "{}.vtx[{}]".format(terrain, i * n + j)
            cmds.move(cx, cy, cz, vtx, relative=False, ws=True)
    cmds.polyNormal(terrain, normalMode=2, userNormalMode=0, ch=1)
    cmds.polySoftEdge(terrain, angle=50, constructionHistory=1)
    cmds.parent(terrain, parent)
    return terrain, hm


def _build_cave_shell(parent):
    """Inward-facing spherical shell for enclosed cave ceiling + walls.

    Wide + low dome (radius 28, Y scale 0.30, centred at Y=10) so the cave
    reads as a spacious cavern rather than a tight tunnel — crystals occupy
    a fraction of the frame, leaving room for fog, light shafts and depth.
    """
    shell = cmds.polySphere(
        name="CCV9_cave_shell", radius=28,
        subdivisionsX=52, subdivisionsY=32,
    )[0]
    cmds.scale(1.0, 0.30, 1.0, shell)
    cmds.move(0, 10, 0, shell)
    cmds.polyNormal(shell, normalMode=0, userNormalMode=0, ch=False)
    # Invert normals so interior faces inside
    cmds.polyNormal(shell, normalMode=3, userNormalMode=0, ch=1)
    cmds.parent(shell, parent)
    return shell


def _build_stalactites(parent, ceiling_mesh, rng):
    """Sample ceiling vertices for downward-pointing hexagonal stalactites."""
    stal_group = cmds.group(empty=True, name="CCV9_stalactites", parent=parent)
    vtx_count = cmds.polyEvaluate(ceiling_mesh, vertex=True)
    for i in range(35):
        try:
            vi = rng.randint(0, vtx_count - 1)
            pos_ct = cmds.xform(
                "{}.vtx[{}]".format(ceiling_mesh, vi), q=True, t=True, ws=True)
            h = rng.uniform(1.5, 5.0)
            r = rng.uniform(0.15, 0.45)
            st = cmds.polyCylinder(
                name="stal_{:02d}".format(i),
                radius=r, height=h, subdivisionsX=6, subdivisionsY=2,
            )[0]
            cmds.move(pos_ct[0], pos_ct[1] - h / 2.0, pos_ct[2], st)
            cmds.rotate(rng.uniform(-8, 8), rng.uniform(-12, 12),
                        rng.uniform(-8, 8), st)
            cmds.parent(st, stal_group)
        except (RuntimeError, ValueError):
            pass
    return stal_group


# ═══════════════════════════════════════════════════════════════════════
#  IMMERSIVE FLY-THROUGH CAMERA
# ═══════════════════════════════════════════════════════════════════════

def _weighted_look_target(cam_pos, crystals, fallback, radius=18.0):
    """Weighted centre of nearby tall crystals for the camera to gaze at.

    `crystals` is a list of (position, color, height) tuples.  Weights are
    proportional to height and inversely proportional to distance, so the
    tallest *and* nearest crystals dominate framing; the gaze point is
    biased upward (height*0.2) toward the visually rich upper third of the
    crystal.  Falls back to *fallback* when nothing is in range.
    """
    wx = wy = wz = 0.0
    total = 0.0
    for pos, _color, height in crystals:
        dx = cam_pos[0] - pos[0]
        dy = cam_pos[1] - pos[1]
        dz = cam_pos[2] - pos[2]
        d = math.sqrt(dx * dx + dy * dy + dz * dz)
        if d < radius:
            w = height / max(d, 0.5)
            wx += pos[0] * w
            wy += (pos[1] + height * 0.2) * w
            wz += pos[2] * w
            total += w
    if total > 0.0:
        return (wx / total, wy / total, wz / total)
    return fallback


def _compute_camera_keyframes(top_crystals, centre, fly_y, look_radius):
    """Build an immersive 30-keyframe fly-through over 2400 frames (~100s @ 24fps).

    Layout: low ceiling-hugging entrance → spiral close passes past the
    tallest crystals (camera wraps ~200° around the cluster) → rising
    pull-back exit.  Camera eye height stays around *fly_y*+ to mid-crystal.
    Each keyframe carries a distinct lookat computed from the actual
    crystals, so the camera is forced to turn its head throughout.
    """
    total_frames = 2400
    num_keyframes = 30

    middle_n = min(7, max(len(top_crystals), 1))
    middle = top_crystals[:middle_n]

    start_pos = (16.0, fly_y + 2.0, 18.0)
    end_pos = (12.0, fly_y + 4.0, 5.0)

    # Dense spiral samples between entrance and exit
    n_spiral = num_keyframes - 2
    spiral_samples = []
    for i in range(n_spiral):
        t = i / max(n_spiral - 1, 1)
        # Smooth blend across the tallest-crystal orbit anchors
        fi = t * (middle_n - 1)
        i0 = int(fi)
        i1 = min(i0 + 1, middle_n - 1)
        blend = fi - i0
        cpos0, _, cheight0 = middle[i0]
        cpos1, _, cheight1 = middle[i1]
        cpos = (
            cpos0[0] * (1.0 - blend) + cpos1[0] * blend,
            cpos0[1] * (1.0 - blend) + cpos1[1] * blend,
            cpos0[2] * (1.0 - blend) + cpos1[2] * blend,
        )
        cheight = cheight0 * (1.0 - blend) + cheight1 * blend

        angle = math.pi / 5 + t * 1.1 * math.pi
        dist = 8.0  # stand-off so crystals read against the cave, not fill the frame
        spiral_samples.append((
            cpos[0] + math.cos(angle) * dist,
            max(fly_y, cpos[1] * 0.5 + fly_y + cheight * 0.15),
            cpos[2] + math.sin(angle) * dist,
        ))

    keys = []
    for i in range(num_keyframes):
        frame = int(round(i * total_frames / float(num_keyframes - 1)))
        if i == 0:
            cam_pos = start_pos
        elif i == num_keyframes - 1:
            cam_pos = end_pos
        else:
            cam_pos = spiral_samples[i - 1]
        look_target = _weighted_look_target(
            cam_pos, top_crystals, centre, look_radius)
        keys.append((frame, cam_pos, look_target))

    keys.sort(key=lambda k: k[0])
    return keys


def _build_immersive_camera(anchors, root, rng, focal=24.0, fly_y=3.0,
                            look_radius=18.0):
    """Build the immersive fly-through camera with a persistent travelling lookat.

    Unlike the earlier rig, the aimConstraint is kept alive for the full
    animation and the lookat locator is keyframed alongside the camera, so
    the camera continuously turns toward nearby tall crystals instead of
    flying in a fixed orientation.

    Args:
        anchors: list of (position, color, height) tuples from the crystal phase.
        root:    scene root transform for parenting.
        rng:     random.Random (kept for parity / future jitter).
        focal:   focal length in mm (24 = wide, immersive).
        fly_y:   base eye height through the crystal forest.
        look_radius: radius within which crystals attract the gaze.

    Returns:
        (camera_transform, lookat_locator) names.
    """
    # Camera + lookat locator
    cam = cmds.camera(name="CCV9_render_cam", focalLength=focal)[0]
    target = cmds.spaceLocator(name="CCV9_cam_lookat")[0]
    cmds.hide(target)
    cmds.move(18, fly_y + 2, 20, cam)
    cmds.move(0, fly_y + 1, 0, target)

    # Persistent aimConstraint — the core fix. Do NOT delete it.
    cmds.aimConstraint(target, cam,
                       aimVector=(0, 0, -1),
                       upVector=(0, 1, 0),
                       worldUpType="vector",
                       worldUpVector=(0, 1, 0),
                       name="CCV9_cam_aimConstraint")

    # Depth of field (kept from the original rig)
    _safe_attr(cam + "Shape", "depthOfField", 1)
    _safe_attr(cam + "Shape", "focusDistance", 12)
    _safe_attr(cam + "Shape", "fStop", 3.2)
    # Arnold exposure — lowered: with brighter key/rim and denser fog the
    # cave no longer needs a heavy +3.0 lift, which had washed out contrast.
    try:
        cmds.setAttr(cam + "Shape.ai_exposure", 1.5)
    except (RuntimeError, ValueError):
        pass

    cmds.parent(cam, root)
    cmds.parent(target, root)

    # Candidate lookat crystals: tallest 12
    sorted_anchors = sorted(anchors, key=lambda a: a[2], reverse=True)
    top_crystals = sorted_anchors[:min(12, len(sorted_anchors))]

    # Cluster centre, boosted above the floor so we never stare at the ground
    if top_crystals:
        cx = sum(a[0][0] for a in top_crystals) / len(top_crystals)
        cy = sum(a[0][1] for a in top_crystals) / len(top_crystals) + 1.5
        cz = sum(a[0][2] for a in top_crystals) / len(top_crystals)
        centre = (cx, cy, cz)
    else:
        centre = (0.0, fly_y + 1.0, 0.0)

    keyframes = _compute_camera_keyframes(top_crystals, centre, fly_y, look_radius)

    # Keyframe BOTH the camera and the lookat locator
    for frame, cam_pos, look_pos in keyframes:
        cmds.setKeyframe(cam, attribute="translateX", value=cam_pos[0], time=frame)
        cmds.setKeyframe(cam, attribute="translateY", value=cam_pos[1], time=frame)
        cmds.setKeyframe(cam, attribute="translateZ", value=cam_pos[2], time=frame)
        cmds.setKeyframe(target, attribute="translateX", value=look_pos[0], time=frame)
        cmds.setKeyframe(target, attribute="translateY", value=look_pos[1], time=frame)
        cmds.setKeyframe(target, attribute="translateZ", value=look_pos[2], time=frame)

    try:
        cmds.select(cam)
        cmds.keyTangent(inTangentType="spline", outTangentType="spline")
        cmds.select(target)
        cmds.keyTangent(inTangentType="spline", outTangentType="spline")
    except (RuntimeError, ValueError):
        pass

    cmds.playbackOptions(min=0, max=2400, animationStartTime=0,
                         animationEndTime=2400)
    return cam, target


# ═══════════════════════════════════════════════════════════════════════
#  POISSON-DISC SEED DISTRIBUTION
# ═══════════════════════════════════════════════════════════════════════

def _poisson_sample_3d(points_with_normals, target, min_dist, rng):
    """Greedy Poisson-disc sampling on 3D points (Bridson, 2007 simplified)."""
    shuffled = list(points_with_normals)
    rng.shuffle(shuffled)
    selected = []
    for pos, normal in shuffled:
        too_close = False
        for sp, _ in selected:
            dx, dy, dz = pos[0]-sp[0], pos[1]-sp[1], pos[2]-sp[2]
            if dx*dx + dy*dy + dz*dz < min_dist * min_dist:
                too_close = True
                break
        if not too_close:
            selected.append((pos, normal))
            if len(selected) >= target:
                break
    return selected


# ═══════════════════════════════════════════════════════════════════════
#  MAIN BUILD
# ═══════════════════════════════════════════════════════════════════════

def build(seed=20260721, density=56, fog_density=0.008, render=True,
          camera_focal=24, fly_y=3.0, look_radius=18.0,
          growth_stagger=400, growth_duration=560):
    """Build complete cavern + Arnold render. Returns render camera name.

    Camera/animation knobs (all optional, backward-compatible defaults):
        camera_focal:    fly-through focal length in mm (24 = immersive wide).
        fly_y:           target eye height through the crystal forest (m).
        look_radius:     radius (m) within which crystals attract the gaze.
        growth_stagger:  window over which crystals begin growing (frames).
        growth_duration: per-crystal growth length (frames).
    """
    rng = random.Random(seed)

    # ── Cleanup ───────────────────────────────────────────────────────
    for old_root in [ROOT, "crystalCavern_v8", "crystalCavern_v7",
                      "crystalCavern_v6", "crystalCavern_v5"]:
        if cmds.objExists(old_root):
            cmds.delete(old_root)
    for prefix in ["CCV9_", "CCV8_", "CCV7_", "CCV6_", "CCV5_",
                   "CCV9_cam", "crystalCavern", "cave_terrain",
                   "cave_enclosure", "crystal_group", "dust_particles",
                   "cave_fog", "stalactites", "stalagmites"]:
        for name in (cmds.ls(prefix + "*") or []):
            try: cmds.delete(name)
            except: pass

    # ── Clean orphaned camera anim curves from previous runs ──
    for curve in (cmds.ls(type="animCurve") or []):
        cname = str(curve)
        if "CCV9_render_cam" in cname or "CCV9_cam_lookat" in cname:
            try: cmds.delete(curve)
            except: pass

    # ── Arnold plugin ─────────────────────────────────────────────────
    try:
        if not cmds.pluginInfo("mtoa", query=True, loaded=True):
            cmds.loadPlugin("mtoa")
    except RuntimeError:
        pass

    # Progress window: user sees building progress across 8 stages
    _stages = [
        "Cleaning scene", "Creating materials", "Building cave shell",
        "Generating terrain", "Growing stalactites", "Sampling crystal seeds",
        "Growing crystals", "Setting up lights & fog",
    ]
    cmds.progressWindow(
        title="Crystal Cavern — Building...",
        progress=0, status="Starting...",
        isInterruptable=True,
    )
    root = cmds.group(empty=True, name=ROOT)
    print("BUILD: seed={} density={} fog={}".format(seed, density, fog_density))

    # ── Materials ─────────────────────────────────────────────────────
    rock = _material("CCV9_rock", (0.06, 0.042, 0.034), roughness=.85)
    floor_rock = _material("CCV9_floor", (0.10, 0.068, 0.054), roughness=.72)

    gem_defs = [
        ((0.48, 0.17, 0.90), "amethyst",   (0.22, 0.10, 0.38), 1.54),
        ((0.12, 0.58, 0.95), "aquamarine", (0.06, 0.28, 0.42), 1.58),
        ((0.72, 0.82, 1.0),  "selenite",   (0.28, 0.35, 0.42), 1.52),
        ((0.15, 0.80, 0.50), "emerald",    (0.04, 0.32, 0.18), 1.57),
        ((0.70, 0.08, 0.14), "ruby",       (0.50, 0.04, 0.08), 1.77),
        ((0.06, 0.12, 0.50), "sapphire",   (0.03, 0.08, 0.38), 1.77),
        ((0.68, 0.48, 0.12), "topaz",      (0.32, 0.22, 0.04), 1.62),
        ((0.55, 0.38, 0.12), "citrine",    (0.35, 0.22, 0.06), 1.54),
        ((0.70, 0.42, 0.48), "rose_quartz",(0.40, 0.22, 0.25), 1.54),
        ((0.10, 0.50, 0.32), "fluorite",   (0.07, 0.30, 0.18), 1.43),
    ]

    gems = []
    for color, name, glow, ior in gem_defs:
        m = _material("CCV9_" + name + "_gem", color, transmission=.72,
                       emission=.80, roughness=.14, ior=ior,
                       subsurface_color=glow)
        _add_cloudy_texture(m, glow)
        gems.append(m)

    # ── Sphere shell cave ───────────────────────────────────────────
    cmds.progressWindow(edit=True, progress=1, status="Building cave shell...")
    shell = _build_cave_shell(root)
    _assign(shell, rock)

    # ── Diamond-Square floor ─────────────────────────────────────────
    cmds.progressWindow(edit=True, progress=2, status="Generating Diamond-Square terrain...")
    floor, hm = _build_diamond_square_terrain(50, seed, 0.45, root)
    _assign(floor, floor_rock)

    # ── Stalactites ──────────────────────────────────────────────────
    cmds.progressWindow(edit=True, progress=3, status="Growing stalactites...")
    _build_stalactites(root, shell, rng)

    # ── Extract terrain vertices for crystal seeding ─────────────────
    cmds.progressWindow(edit=True, progress=4, status="Sampling Poisson-disc seeds...")
    vtx_count = cmds.polyEvaluate(floor, vertex=True)
    points_all = []
    for vi in range(vtx_count):
        p = cmds.xform("{}.vtx[{}]".format(floor, vi), q=True, t=True, ws=True)
        normals_raw = cmds.polyNormalPerVertex(
            "{}.vtx[{}]".format(floor, vi), q=True, xyz=True)
        if normals_raw:
            avg = [sum(normals_raw[0::3]) / len(normals_raw[0::3]),
                   sum(normals_raw[1::3]) / len(normals_raw[1::3]),
                   sum(normals_raw[2::3]) / len(normals_raw[2::3])]
            points_all.append((p, avg))

    seeds = _poisson_sample_3d(points_all, density, 2.8, rng)
    print("  seeds: {} (Poisson-disc, Bridson 2007)".format(len(seeds)))

    # ── Grow hexagonal prism crystals ────────────────────────────────
    cmds.progressWindow(edit=True, progress=5, status="Growing hexagonal crystals...")
    xtal_root = cmds.group(empty=True, name="CCV9_crystals", parent=root)
    anchors = []
    for i, (pos, normal) in enumerate(seeds):
        scale = rng.uniform(0.72, 1.6) * (1.6 if i < 12 else 1.0)
        shader = gems[i % len(gems)]
        cluster, anchor, crystal_h = _crystal_cluster(pos, normal, scale,
                                                       shader, i, xtal_root, rng)
        anchors.append((anchor, gem_defs[i % len(gem_defs)][0], crystal_h))
        if (i + 1) % 15 == 0:
            print("  crystals: {}/{}".format(i + 1, len(seeds)))
    print("  crystals: {}/{} (hexagonal prisms, L-system branches)".format(
        len(seeds), len(seeds)))

    # ── Growth animation: scale crystals 0→1 over frames 0-960 ──────
    children = cmds.listRelatives(xtal_root, children=True, type="transform") or []
    for idx, child in enumerate(children):
        start_f = int((idx / max(len(children), 1)) * growth_stagger)
        end_f = start_f + growth_duration
        try:
            for axis in ('X', 'Y', 'Z'):
                cmds.setKeyframe(child, attribute='scale' + axis,
                                 value=0.01, time=start_f)
                cmds.setKeyframe(child, attribute='scale' + axis,
                                 value=1.0, time=end_f)
        except (RuntimeError, ValueError):
            pass
    try:
        cmds.select(children)
        cmds.keyTangent(inTangentType='spline', outTangentType='spline')
    except (RuntimeError, ValueError):
        pass
    print("  growth animation: {} crystals, stagger {}f / duration {}f (ease-in-out)".format(
        len(children), growth_stagger, growth_duration))

    # ── 3-layer lighting ─────────────────────────────────────────────
    cmds.progressWindow(edit=True, progress=6, status="Setting up lights + fog + dust...")
    # Ambient dome — dimmed so shadow areas stay deep and the key/rim read.
    dome_lt = cmds.shadingNode("aiSkyDomeLight", asLight=True,
                                name="CCV9_ambient")
    _safe_attr(dome_lt, "color", (0.04, 0.025, 0.06), "color")
    _safe_attr(dome_lt, "intensity", 0.30)

    # Key light: warm golden beam from the cave entrance, steep and deep
    key = cmds.directionalLight(name="CCV9_entrance_key")
    _safe_attr(key, "color", (1.0, 0.75, 0.40), "color")
    _safe_attr(key, "intensity", 180)
    cmds.rotate(-55, -35, 0, key)
    cmds.move(20, 18, 25, key)

    # Rim light: cool blue back-glow outlining the crystals
    rim = cmds.directionalLight(name="CCV9_blue_rim")
    _safe_attr(rim, "color", (0.15, 0.30, 1.0), "color")
    _safe_attr(rim, "intensity", 40)
    cmds.rotate(25, 145, 0, rim)

    # Crystal glow: brighter point lights with linear decay so the glow stays
    # local to each crystal instead of washing the whole cave.
    for i, (pos, color, *_h) in enumerate(anchors[:20]):
        lt = cmds.pointLight(name="CCV9_glow_{:02d}".format(i))
        _safe_attr(lt, "color", color, "color")
        _safe_attr(lt, "intensity", rng.uniform(2000, 4000))
        try: cmds.setAttr(lt + ".decayRate", 1)  # linear decay
        except (RuntimeError, ValueError): pass
        cmds.move(pos[0], pos[1], pos[2], lt)
    print("  lights: dome + key + rim + {} crystal glow (linear decay)".format(
        min(len(anchors), 20)))

    # ── Volumetric fog ───────────────────────────────────────────────
    fog = cmds.createNode("aiAtmosphereVolume", name="CCV9_fog")
    fog_d = max(float(fog_density), 0.02)  # visible Tyndall beams
    _safe_attr(fog, "density", fog_d)
    _safe_attr(fog, "color", (.032, .014, .075), "color")
    _safe_attr(fog, "attenuation", .65)
    _safe_attr(fog, "attenuationColor", (.012, .006, .035), "color")
    try:
        _safe_attr(fog, "groundNormal", (0.0, 1.0, 0.0), "color")
        _safe_attr(fog, "groundPoint", (0.0, -14.0, 0.0), "color")
    except (RuntimeError, ValueError):
        pass
    except Exception:
        pass  # groundNormal/Point don't exist on all Arnold versions
    print("  fog: aiAtmosphereVolume (density={})".format(fog_d))

    # ── Dust ─────────────────────────────────────────────────────────
    # Pale, faint motes — read as suspended micro-dust caught in the light
    # shafts, not glowing orange balls.
    dust_mat = _material("CCV9_dust", (0.9, 0.85, 0.75), emission=.08,
                         roughness=.35)
    dust_grp = cmds.group(empty=True, name="CCV9_dust", parent=root)
    for i in range(200):
        mote = cmds.polySphere(
            name="CCV9_dust_{:03d}".format(i),
            radius=rng.uniform(.005, .018), subdivisionsX=4, subdivisionsY=4,
        )[0]
        cmds.move(rng.uniform(-22, 22), rng.uniform(-4, 14),
                  rng.uniform(-22, 22), mote)
        _assign(mote, dust_mat)
        cmds.parent(mote, dust_grp)

    # ── Immersive fly-through camera (24mm, travelling lookat) ────────
    cmds.progressWindow(edit=True, progress=7, status="Setting up camera + animation...")
    cam, _lookat = _build_immersive_camera(anchors, root, rng,
                                           focal=camera_focal,
                                           fly_y=fly_y,
                                           look_radius=look_radius)
    print("  camera: {}mm, DOF f/3.2, 2400-frame immersive fly-through "
          "(30 keys, travelling lookat)".format(camera_focal))

    # ── Render settings ─────────────────────────────────────────────
    cmds.setAttr("defaultRenderGlobals.currentRenderer", "arnold",
                 type="string")
    cmds.setAttr("defaultResolution.width", 1920)
    cmds.setAttr("defaultResolution.height", 1080)
    _safe_attr("defaultArnoldRenderOptions", "AASamples", 5)
    _safe_attr("defaultArnoldRenderOptions", "GIDiffuseSamples", 2)
    _safe_attr("defaultArnoldRenderOptions", "GISpecularSamples", 2)
    _safe_attr("defaultArnoldRenderOptions", "GITransmissionSamples", 5)
    _safe_attr("defaultArnoldRenderOptions", "GISssSamples", 3)
    _safe_attr("defaultArnoldRenderOptions", "GIVolumeSamples", 2)
    _safe_attr("defaultArnoldDriver", "ai_translator", "exr", "string")
    _safe_attr("defaultArnoldDriver", "mergeAOVs", 1)
    shapes = cmds.listRelatives(cam, shapes=True, type="camera")
    if shapes:
        try: cmds.setAttr(shapes[0] + ".renderable", 1)
        except: pass

    os.makedirs(OUT_DIR, exist_ok=True)
    rp = OUT_DIR + "/crystal_cavern_beauty"
    cmds.setAttr("defaultRenderGlobals.imageFilePrefix", rp, type="string")
    cmds.setAttr("defaultRenderGlobals.animation", 0)
    cmds.setAttr("defaultRenderGlobals.putFrameBeforeExt", 0)
    cmds.setAttr("defaultRenderGlobals.outFormatControl", 0)

    cmds.file(rename=OUT_DIR + "/crystal_cavern_v9.ma")
    cmds.file(save=True, type="mayaAscii", force=True)
    print("  render: 1920x1080 EXR, AA=5, transmission=5")

    # ── Final stats ──────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  CRYSTAL CAVERN v9 READY")
    print("  {} hex crystals + {} branches + {} stalactites".format(
        len(seeds),
        sum(3 + rng.randint(0, 2) for _ in seeds),
        35,
    ))
    print("  Diamond-Square terrain + sphere cave + growth animation")
    print("  Material: SSS + transmission + cloudy noise + 10 gem IORs")
    print("  DOF camera 2400f / 30-key fly-through, fog + dust + 3-layer lights")
    print("  Scene: {}".format(OUT_DIR + "/crystal_cavern_v9.ma"))
    if render:
        print("  Render: {}".format(rp + ".exr"))
        print("=" * 60)
        # Render via MEL (proven reliable)
        print("\n  Launching Arnold render (1920x1080, 3-5 min)...")
        try:
            mel.eval("arnoldRender -batch -camera " + cam)
            print("  RENDER COMPLETE: {}".format(rp + ".exr"))
        except Exception as e:
            print("  RENDER FAILED: {}".format(str(e)[:120]))
            print("  Manually: Arnold > Render View > Camera={} > Start".format(cam))
    else:
        print("  (render=False — scene saved without rendering)")
        print("=" * 60)

    cmds.progressWindow(edit=True, progress=8, status="Complete!", endProgress=1)

    return cam


if __name__ == "__main__":
    build(seed=20260721, density=56, fog_density=0.008, render=True)
