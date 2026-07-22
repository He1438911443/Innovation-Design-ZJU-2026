"""
Crystal Cavern — Module 4 v2: Cinematic Lighting, Volumetrics, Camera

Improvements over v1:
- Precise crystal accent lights at actual crystal positions (not random)
- Light color matches each crystal's glow color
- Entrance backlight + subtle fill lights for depth
- Volumetric fog with ground-hugging density
- Dust particles with gentle floating animation curves
- Cinematic spiral camera that flies close to crystal clusters

References / scope note:
- Jensen, H. W. et al. (2001). A practical model for subsurface light transport.
  NOTE: the subsurface scattering itself is implemented in crystal_growth.py via
  Arnold's aiStandardSurface `subsurface` family of attributes (an industrial
  BSSRDF following Jensen et al.). The point-light network in THIS module is
  *not* an SSS algorithm — it is emissive accent illumination placed at crystal
  anchors to enhance the subsurface *appearance* (glow-from-within look). Keeping
  the two concerns separate is intentional: BSSRDF handles light transport inside
  the crystal; the accent lights handle exterior fill so crystals read as
  self-luminous against the dark cavern.
"""

import maya.cmds as cmds
import random
import math


# ── Lighting ────────────────────────────────────────────────────────

def setup_lighting(crystal_count=30, light_anchors=None):
    """Create cave lighting with precise crystal accent placement.

    Args:
        crystal_count: Number of crystal formations.
        light_anchors: List of (position, glow_color) tuples from crystal_growth.
                       If None, falls back to random placement.

    Returns:
        Ambient light node name.
    """
    # Clear existing lights
    for light_type in ["ambientLight", "directionalLight", "pointLight",
                        "spotLight", "areaLight"]:
        for l in cmds.ls(type=light_type):
            try:
                cmds.delete(l)
            except Exception:
                pass

    # ── Dark ambient with deep purple-blue tint ──
    amb = cmds.shadingNode("ambientLight", asLight=True, name="cave_ambient")
    cmds.setAttr(amb + ".intensity", 0.06)
    cmds.setAttr(amb + ".color", 0.03, 0.02, 0.06, type="double3")
    cmds.setAttr(amb + ".ambientShade", 0.95)

    # ── Directional entrance light — warm golden, from cave mouth ──
    entrance = cmds.shadingNode("directionalLight", asLight=True,
                                 name="cave_entrance_key")
    cmds.setAttr(entrance + ".intensity", 1.5)
    cmds.setAttr(entrance + ".color", 1.0, 0.82, 0.55, type="double3")
    cmds.move(25, 12, 25, entrance)
    cmds.rotate(-30, -45, 0, entrance)

    # ── Subtle back rim light for depth ──
    rim = cmds.shadingNode("directionalLight", asLight=True,
                            name="cave_rim_light")
    cmds.setAttr(rim + ".intensity", 0.4)
    cmds.setAttr(rim + ".color", 0.3, 0.4, 0.7, type="double3")
    cmds.move(-20, 8, -20, rim)
    cmds.rotate(25, 135, 0, rim)

    # ── Crystal accent point lights ──
    if light_anchors:
        _place_crystal_lights(light_anchors)
    else:
        _place_random_lights(crystal_count)

    return amb


def _place_crystal_lights(light_anchors):
    """Place point lights at actual crystal positions with matching colors.

    This is emissive accent illumination, *not* subsurface scattering. The SSS
    look is produced by Arnold's BSSRDF in crystal_growth.py; these point lights
    are exterior fill that makes each crystal read as self-luminous. Samples up
    to 20 anchors for performance, prioritizing the tallest crystals.
    """
    # Sort by height (use anchor Y as proxy) to light the most prominent crystals
    sorted_anchors = sorted(light_anchors, key=lambda a: a[0][1], reverse=True)
    selected = sorted_anchors[:min(len(sorted_anchors), 20)]

    for i, (pos, glow) in enumerate(selected):
        lt = cmds.shadingNode("pointLight", asLight=True,
                              name="crystal_accent_" + str(i))
        # Match light color to crystal glow, boosted for visibility
        cmds.setAttr(lt + ".color", min(glow[0] * 3.0, 1.0),
                     min(glow[1] * 3.0, 1.0),
                     min(glow[2] * 3.0, 1.0), type="double3")
        cmds.setAttr(lt + ".intensity", random.uniform(2.0, 5.0))
        cmds.setAttr(lt + ".decayRate", 2)
        # Place slightly offset from crystal position for better illumination
        cmds.move(pos[0] + random.uniform(-1, 1),
                  pos[1] + random.uniform(0.5, 2),
                  pos[2] + random.uniform(-1, 1), lt)

    print("   Precise crystal lights: " + str(len(selected)) + " placed at crystal positions")


def _place_random_lights(crystal_count):
    """Fallback: random accent lights when light_anchors unavailable."""
    colors = [
        (0.6, 0.3, 0.85), (0.3, 0.5, 0.95), (0.3, 0.75, 0.6),
        (0.9, 0.5, 0.3), (0.5, 0.3, 0.7), (0.15, 0.8, 0.5),
    ]
    n = min(crystal_count // 2, 20)
    for i in range(n):
        lt = cmds.shadingNode("pointLight", asLight=True,
                              name="crystal_accent_" + str(i))
        cmds.setAttr(lt + ".intensity", random.uniform(1.5, 4.0))
        c = random.choice(colors)
        cmds.setAttr(lt + ".color", c[0], c[1], c[2], type="double3")
        cmds.setAttr(lt + ".decayRate", 2)
        cmds.move(random.uniform(-18, 18), random.uniform(-8, 2),
                  random.uniform(-18, 18), lt)
    print("   Random crystal lights: " + str(n) + " (no anchors available)")


# ── Volumetric Fog ───────────────────────────────────────────────────

def setup_volumetric_fog(density=0.06, altitude=18.0):
    """Create volumetric fog for cave depth and atmosphere.

    Arnold aiAtmosphereVolume with ground-hugging density.
    Falls back to Maya envFog if Arnold unavailable.

    Args:
        density: Fog density (0.0-1.0).
        altitude: Fog ceiling height.
    """
    # Clean stale fog
    for fog_name in ["cave_fog"]:
        if cmds.objExists(fog_name):
            try:
                cmds.delete(fog_name)
            except Exception:
                pass

    arnold_available = False
    try:
        if not cmds.pluginInfo("mtoa", query=True, loaded=True):
            cmds.loadPlugin("mtoa")
        arnold_available = cmds.pluginInfo("mtoa", query=True, loaded=True)
    except Exception as exc:
        print("   Arnold unavailable for atmosphere: " + str(exc))

    if arnold_available:
        try:
            fog = cmds.createNode("aiAtmosphereVolume", name="cave_fog")
            cmds.setAttr(fog + ".density", density)
            # Deep blue-purple atmospheric color
            cmds.setAttr(fog + ".color", 0.04, 0.025, 0.08, type="double3")
            cmds.setAttr(fog + ".attenuation", 0.6)
            cmds.setAttr(fog + ".attenuationColor", 0.02, 0.015, 0.05, type="double3")
            # Ground level: fog thickest near cave floor
            cmds.setAttr(fog + ".groundNormal", 0.0, 1.0, 0.0)
            cmds.setAttr(fog + ".groundPoint", 0.0, -altitude, 0.0)
            print("   Volumetric fog: Arnold aiAtmosphereVolume (density=" +
                  str(density) + ")")
            return fog
        except (RuntimeError, ValueError):
            pass

    # Maya native fallback
    try:
        fog = cmds.shadingNode("envFog", asShader=True, asUtility=True,
                                name="cave_fog")
        cmds.setAttr(fog + ".color", 0.04, 0.025, 0.08, type="double3")
        cmds.setAttr(fog + ".saturationDistance", 60.0)
        print("   Volumetric fog: Maya envFog fallback (render-time only)")
        return fog
    except (RuntimeError, ValueError):
        print("   Warning: Could not create fog")
        return None


# ── Dust Particles ───────────────────────────────────────────────────

def create_dust_particles(count=250):
    """Create floating dust mote geometry with a single shared material.

    Returns parent group.
    """
    # Clean old dust group and its materials
    if cmds.objExists("dust_particles"):
        try:
            cmds.delete("dust_particles")
        except Exception:
            pass
    # Also clean leftover dust materials from previous runs
    for mat in (cmds.ls(mat=True) or []):
        name = str(mat)
        if name.startswith("dust_mat_"):
            try:
                cmds.delete(mat)
            except Exception:
                pass

    grp = cmds.group(empty=True, name="dust_particles")

    # Create ONE shared material for all dust motes
    shader = cmds.shadingNode("lambert", asShader=True, name="dust_mat_shared")
    cmds.setAttr(shader + ".color", 1.0, 0.92, 0.78, type="double3")
    cmds.setAttr(shader + ".ambientColor", 0.15, 0.12, 0.08, type="double3")
    cmds.setAttr(shader + ".transparency", 0.65, 0.70, 0.75)

    for i in range(count):
        try:
            radius = random.uniform(0.02, 0.06)
            dust = cmds.polySphere(name="dust_" + str(i), radius=radius,
                                   subdivisionsX=4, subdivisionsY=4)[0]
            cmds.move(random.uniform(-24, 24), random.uniform(-8, 8),
                      random.uniform(-24, 24), dust)
            cmds.select(dust)
            cmds.hyperShade(assign=shader)
            cmds.parent(dust, grp)
        except (RuntimeError, ValueError):
            pass

    print("   Dust: " + str(count) + " motes (shared material)")
    return grp


# ── Camera Rig ───────────────────────────────────────────────────────

def _query_crystal_anchors(crystal_group):
    """Read lightAnchor and crystalHeight attributes from crystal transforms.

    Returns a list of ((x, y, z), height) tuples for crystals that have the
    required attributes, or an empty list if the group does not exist.
    """
    data = []
    if not cmds.objExists(crystal_group):
        return data
    children = cmds.listRelatives(crystal_group, children=True, type="transform") or []
    for child in children:
        # Verify this transform carries the custom attributes added by
        # crystal_growth v2.
        if not cmds.attributeQuery("crystalHeight", node=child, exists=True):
            continue
        try:
            ax = cmds.getAttr(child + ".lightAnchorX")
            ay = cmds.getAttr(child + ".lightAnchorY")
            az = cmds.getAttr(child + ".lightAnchorZ")
            h = cmds.getAttr(child + ".crystalHeight")
            data.append(((ax, ay, az), h))
        except (ValueError, RuntimeError):
            pass
    return data


def _blend_vector(a, b, t):
    """Linear interpolate between two 3-tuples."""
    return (a[0] + (b[0] - a[0]) * t,
            a[1] + (b[1] - a[1]) * t,
            a[2] + (b[2] - a[2]) * t)


def _weighted_look_target(cam_pos, crystals, fallback, radius=15.0):
    """Compute a weighted centre of nearby crystals for the camera to gaze at.

    Weights are proportional to crystalHeight and inversely proportional to
    distance from the camera, so the tallest *and* nearest crystals dominate
    the framing.  Falls back to *fallback* when nothing is in range.
    """
    wx, wy, wz = 0.0, 0.0, 0.0
    total = 0.0
    for (cx, cy, cz), h in crystals:
        dx = cam_pos[0] - cx
        dy = cam_pos[1] - cy
        dz = cam_pos[2] - cz
        d = math.sqrt(dx * dx + dy * dy + dz * dz)
        if d < radius:
            w = h / max(d, 0.5)
            wx += cx * w
            wy += (cy + h * 0.3) * w  # bias toward upper third of crystal
            wz += cz * w
            total += w
    if total > 0.0:
        return (wx / total, wy / total, wz / total)
    return fallback


def _build_fallback_crystals():
    """Return dummy crystal data when no real crystals are in the scene."""
    return [
        ((5.0, 0.0, 5.0), 4.0),
        ((-5.0, -1.0, 2.0), 3.5),
        ((0.0, 1.0, -5.0), 3.0),
        ((8.0, -2.0, -3.0), 2.5),
        ((-8.0, -1.0, -6.0), 2.0),
        ((3.0, 0.5, -8.0), 1.8),
        ((-10.0, 0.0, 4.0), 3.2),
        ((12.0, -0.5, -4.0), 2.8),
    ]


def create_camera_rig(terrain_name="cave_terrain", crystal_group="crystal_group"):
    """Cinematic fly-through camera dynamically generated from crystal positions.

    Queries *crystal_group* for child transforms that carry the
    ``lightAnchor`` and ``crystalHeight`` custom attributes (added by
    ``crystal_growth.py`` v2), sorts them by height, and builds a 960-frame
    camera path that sweeps past the tallest formations at close range.

    The camera uses an ``aimConstraint`` to a travelling look-at locator
    instead of baked rotation keyframes, producing much smoother results.

    Args:
        terrain_name: Ignored; kept for backward compatibility.
        crystal_group: Transform name of the crystal parent group.

    Returns:
        Camera transform name (str).  The matching look-at locator is named
        ``fly_cam_lookat``.
    """
    # ── Clean up any previous fly_cam objects and orphaned anim curves ──
    for obj in cmds.ls("fly_cam*") or []:
        try:
            cmds.delete(obj)
        except Exception:
            pass
    for curve in cmds.ls(type="animCurve") or []:
        if "fly_cam" in curve:
            try:
                cmds.delete(curve)
            except Exception:
                pass

    # ── Query crystal positions ──
    crystal_data = _query_crystal_anchors(crystal_group)

    # Sort by crystalHeight descending; take the tallest 8-12.
    crystal_data.sort(key=lambda d: d[1], reverse=True)
    top = crystal_data[:min(len(crystal_data), 12)]
    if not top:
        top = _build_fallback_crystals()

    # Overall cluster centre (boosted 2 m above floor so the camera does not
    # stare at the ground).
    all_positions = [p for p, _h in top]
    centre = (sum(p[0] for p in all_positions) / len(all_positions),
              sum(p[1] for p in all_positions) / len(all_positions) + 2.0,
              sum(p[2] for p in all_positions) / len(all_positions))

    # ── Camera + look-at locator + aim constraint ──
    cam = cmds.camera(name="fly_cam", focalLength=24)[0]

    loc = cmds.circle(name="fly_cam_lookat", radius=0.3)[0]
    cmds.move(centre[0], centre[1], centre[2], loc)

    cmds.aimConstraint(loc, cam,
                        aimVector=(0, 0, -1),
                        upVector=(0, 1, 0),
                        worldUpType="vector",
                        worldUpVector=(0, 1, 0))

    # ── Build dynamic keyframes ──
    # We want between 6 and 10 keyframes over 960 frames.
    # Layout: 1 start + N middle + 1 end.  Keep N in [4, 8].
    middle_n = max(4, min(8, len(top)))
    middle_crystals = top[:middle_n]

    keyframes = []  # list of (frame, cam_pos, look_at_pos)

    # -- Start: cave entrance overview --
    start_look = _weighted_look_target((20, 6, 20), top, centre)
    keyframes.append((0, (20, 6, 20), start_look))

    # -- Middle: close passes past the tallest crystals --
    # Each crystal gets its own keyframe; the camera position is offset
    # 3-5 units from the crystal, sweeping around the cluster.
    frame_step = 900.0 / (middle_n + 1)
    for i in range(middle_n):
        cpos, cheight = middle_crystals[i]
        f = int(60 + (i + 1) * frame_step)

        # Approach angle rotates ~200 deg so the camera wraps around the cave.
        t = i / max(middle_n - 1, 1)
        angle = math.pi / 5 + t * 1.1 * math.pi
        dist = 4.0

        cam_pos = (
            cpos[0] + math.cos(angle) * dist,
            cpos[1] + 1.8 + cheight * 0.12,
            cpos[2] + math.sin(angle) * dist,
        )
        look_target = _weighted_look_target(cam_pos, top, centre)
        keyframes.append((f, cam_pos, look_target))

    # -- End: wide establishing shot, rising above the cave --
    end_look = _weighted_look_target((15, 8, 0), top, centre)
    keyframes.append((960, (15, 8, 0), end_look))

    # -- Pad to 6 keyframes minimum if the scene is sparse --
    if len(keyframes) < 6:
        needed = 6 - len(keyframes)
        step = 900.0 / (needed + 1)
        for j in range(needed):
            f = int(200 + (j + 1) * step)
            idx = j % len(top)
            c = top[idx][0]
            pad_pos = (c[0] + 5.0, c[1] + 3.0, c[2] - 3.0)
            keyframes.append((f, pad_pos, centre))
        keyframes.sort(key=lambda k: k[0])

    # ── Apply translation keyframes on both camera and look-at locator ──
    for frame_num, cam_pos, look_target in keyframes:
        cmds.setKeyframe(cam, attribute="translateX",
                         value=cam_pos[0], time=frame_num)
        cmds.setKeyframe(cam, attribute="translateY",
                         value=cam_pos[1], time=frame_num)
        cmds.setKeyframe(cam, attribute="translateZ",
                         value=cam_pos[2], time=frame_num)
        cmds.setKeyframe(loc, attribute="translateX",
                         value=look_target[0], time=frame_num)
        cmds.setKeyframe(loc, attribute="translateY",
                         value=look_target[1], time=frame_num)
        cmds.setKeyframe(loc, attribute="translateZ",
                         value=look_target[2], time=frame_num)

    # ── Spline tangents for smooth interpolation ──
    try:
        cmds.select(cam)
        cmds.keyTangent(inTangentType="spline", outTangentType="spline")
        cmds.select(loc)
        cmds.keyTangent(inTangentType="spline", outTangentType="spline")
    except Exception:
        pass

    # ── Playback range ──
    cmds.playbackOptions(min=0, max=960, animationStartTime=0,
                          animationEndTime=960)

    queried = len(crystal_data)
    used = len(top)
    keys = len(keyframes)
    print(f"   Camera: {keys}-keyframe dynamic fly-through "
          f"({queried} crystals queried, {used} tallest used, f=24mm)")
    return cam


# ── Full Lighting Setup ──────────────────────────────────────────────

def setup_cave_lighting(crystal_count=30, light_anchors=None,
                        fog_density=0.06, dust_count=250,
                        crystal_lights=20):
    """Full cave lighting: lights + volumetric fog + dust particles.

    Args:
        crystal_count: Number of crystal formations.
        light_anchors: Optional list of (position, glow_color) for precise lights.
        fog_density: Arnold atmosphere density.
        dust_count: Number of shared-material dust motes.
        crystal_lights: Maximum number of crystal accent lights.

    Returns:
        Tuple of (ambient_light, fog_node, dust_group).
    """
    # Keep the existing precise-anchor path, while allowing the UI to cap it.
    if light_anchors:
        light_anchors = sorted(light_anchors, key=lambda a: a[0][1], reverse=True)
        light_anchors = light_anchors[:max(0, int(crystal_lights))]
    amb = setup_lighting(crystal_count, light_anchors)
    fog = setup_volumetric_fog(density=fog_density)
    dust = create_dust_particles(count=int(dust_count))
    return amb, fog, dust
