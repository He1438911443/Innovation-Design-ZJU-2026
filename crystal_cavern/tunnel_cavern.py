"""Crystal Cavern v10 — tunnel-first generator for Maya.

Unlike the legacy terrain-first scene, this module generates a navigable cave
from a seeded centreline.  A sequence of irregular ring sections becomes a
single inward-facing tunnel mesh; wall samples become crystal seeds; the same
centreline drives the fly-through camera.  The visible clusters are recursive
L-system expansions, not isolated spikes.
"""
from __future__ import print_function

import math
import os
import random

import maya.cmds as cmds
import maya.api.OpenMaya as om


ROOT = "crystalCavern_v10"
OUT_DIR = "/Users/xixi/大学/未来创新设计/crystal_cavern/renders/tunnel_v10"


def _v_add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def _v_sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def _v_scale(a, s): return (a[0] * s, a[1] * s, a[2] * s)
def _v_dot(a, b): return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
def _v_len(a): return math.sqrt(_v_dot(a, a))
def _v_norm(a):
    l = max(_v_len(a), 0.00001)
    return (a[0]/l, a[1]/l, a[2]/l)
def _v_cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def _set(node, attr, value, colour=False):
    try:
        if colour:
            cmds.setAttr(node + "." + attr, value[0], value[1], value[2], type="double3")
        else:
            cmds.setAttr(node + "." + attr, value)
    except (RuntimeError, ValueError):
        pass


def _shader(name, colour, transmission=0.0, roughness=.4, emission=.0):
    shader = cmds.shadingNode("aiStandardSurface", asShader=True, name=name)
    # A strong diffuse base made earlier versions read like coloured plastic.
    # Real quartz keeps a milky body but lets back-light travel through it.
    _set(shader, "base", .30 if transmission else 1.0)
    _set(shader, "baseColor", colour, True)
    _set(shader, "specular", 1.0 if transmission else .35)
    _set(shader, "specularRoughness", roughness)
    _set(shader, "specularIOR", 1.54)
    _set(shader, "transmission", transmission)
    _set(shader, "transmissionWeight", transmission)
    # Keep absorption colour pale: real quartz is largely neutral and acquires
    # colour through thickness rather than a saturated painted surface.
    volume_colour = tuple(.62 + c * .38 for c in colour)
    _set(shader, "transmissionColor", volume_colour, True)
    _set(shader, "transmissionDepth", 3.0)
    _set(shader, "subsurface", .14 if transmission else 0.0)
    _set(shader, "subsurfaceWeight", .14 if transmission else 0.0)
    _set(shader, "subsurfaceColor", colour, True)
    _set(shader, "emission", emission)
    _set(shader, "emissionColor", colour, True)
    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=name + "SG")
    cmds.connectAttr(shader + ".outColor", sg + ".surfaceShader", force=True)
    if transmission:
        # 3D mineral inclusions: subtle bump plus 0.05–0.18 roughness variation.
        try:
            noise = cmds.createNode("aiNoise", name=name + "_mineralNoise")
            for attr, value in (("octaves", 5), ("distortion", .22),
                                ("scaleX", 4.5), ("scaleY", 4.5),
                                ("scaleZ", 4.5)):
                _set(noise, attr, value)
            bump = cmds.shadingNode("bump2d", asUtility=True, name=name + "_microBump")
            # Crystal facets stay optically flat; inclusions should carry most
            # of the irregularity. A heavy bump made quartz read like ice rock.
            cmds.setAttr(bump + ".bumpDepth", .025)
            cmds.connectAttr(noise + ".outColorR", bump + ".bumpValue", force=True)
            if cmds.objExists(shader + ".normalCamera"):
                cmds.connectAttr(bump + ".outNormal", shader + ".normalCamera", force=True)
            remap = cmds.createNode("remapValue", name=name + "_roughnessVariation")
            cmds.setAttr(remap + ".outputMin", .05)
            cmds.setAttr(remap + ".outputMax", .18)
            cmds.connectAttr(noise + ".outColorR", remap + ".inputValue", force=True)
            cmds.connectAttr(remap + ".outValue", shader + ".specularRoughness", force=True)
        except (RuntimeError, ValueError):
            pass
    return shader


def _assign(node, shader):
    cmds.select(node, replace=True)
    cmds.hyperShade(assign=shader)


def _assign_hex_facets(node, shader):
    """Give the six principal faces stable light/dark mineral variation."""
    light_sg = shader + "_facetLightSG"
    dark_sg = shader + "_facetDarkSG"
    if not (cmds.objExists(light_sg) and cmds.objExists(dark_sg)):
        return
    for face in range(6):
        try:
            cmds.sets("{}.f[{}]".format(node, face), edit=True,
                      forceElement=light_sg if face in (0, 3) else dark_sg)
        except RuntimeError:
            pass


def _add_rock_detail(shader):
    """Large/small 3D noise layers for broken limestone cave walls."""
    try:
        noise = cmds.createNode("aiNoise", name=shader + "_rockNoise")
        for attr, value in (("octaves", 6), ("distortion", .48),
                            ("scaleX", .55), ("scaleY", .55),
                            ("scaleZ", .55)):
            _set(noise, attr, value)
        bump = cmds.shadingNode("bump2d", asUtility=True,
                                name=shader + "_rockBump")
        cmds.setAttr(bump + ".bumpDepth", .65)
        cmds.connectAttr(noise + ".outColorR", bump + ".bumpValue", force=True)
        if cmds.objExists(shader + ".normalCamera"):
            cmds.connectAttr(bump + ".outNormal", shader + ".normalCamera",
                             force=True)
    except (RuntimeError, ValueError):
        pass


def _aim_y(node, direction):
    """Rotate a primitive so its local Y axis follows direction."""
    p = cmds.xform(node, q=True, ws=True, t=True)
    target = cmds.spaceLocator(name="CCV10_tmpAim")[0]
    cmds.xform(target, ws=True, t=_v_add(p, direction))
    c = cmds.aimConstraint(target, node, aim=(0, 1, 0), u=(0, 0, 1),
                           wut="vector", wu=(0, 0, 1))
    cmds.delete(c, target)


def tunnel_graph(seed, length=84.0, sections=25):
    """Seeded main corridor with a broad chamber and an optional branch.

    The result is a centreline graph: its vertices are later reused by the
    mesh, crystal distribution, camera and presentation diagram.
    """
    rng = random.Random(seed)
    pts = []
    for i in range(sections):
        t = float(i) / (sections - 1)
        x = math.sin(t * math.pi * 2.1 + rng.uniform(-.12, .12)) * (5.0 + 2.2*t)
        y = -3.0 + math.sin(t * math.pi * 3.0) * 1.1 + rng.uniform(-.3, .3)
        z = -length/2.0 + t * length
        # The chamber swells at 55% of the route.
        radius = 7.5 + 8.0 * math.exp(-((t-.56)/.16)**2) + rng.uniform(-.55, .55)
        pts.append(((x, y, z), radius))
    branch_start = pts[int(sections*.58)][0]
    branch = []
    for i in range(8):
        t = float(i) / 7.0
        branch.append(((branch_start[0] + 12*t + 3*math.sin(t*math.pi),
                        branch_start[1] + 2*t,
                        branch_start[2] + 10*t), 5.5 - 1.5*t))
    return {"main": pts, "branch": branch}


def _create_tube(name, path, parent, rng, sides=12):
    """Create one irregular inward-facing tube mesh from centreline rings."""
    vertices, counts, connects, samples = [], [], [], []
    for i, (centre, radius) in enumerate(path):
        if i == 0: tangent = _v_norm(_v_sub(path[1][0], centre))
        elif i == len(path)-1: tangent = _v_norm(_v_sub(centre, path[i-1][0]))
        else: tangent = _v_norm(_v_sub(path[i+1][0], path[i-1][0]))
        ref = (0, 1, 0) if abs(tangent[1]) < .88 else (1, 0, 0)
        right = _v_norm(_v_cross(ref, tangent))
        up = _v_norm(_v_cross(tangent, right))
        for j in range(sides):
            a = 2*math.pi*j/sides
            jitter = 1.0 + .13*math.sin(j*3.1 + i*1.7) + rng.uniform(-.07, .07)
            radial = _v_add(_v_scale(right, math.cos(a)), _v_scale(up, math.sin(a)))
            vertices.append(om.MPoint(*_v_add(centre, _v_scale(radial, radius*jitter))))
            # Interior-facing normal, used as a crystal growth direction.
            samples.append((_v_add(centre, _v_scale(radial, radius*jitter)), _v_scale(radial, -1)))
    for i in range(len(path)-1):
        for j in range(sides):
            a, b = i*sides+j, i*sides+(j+1)%sides
            c, d = (i+1)*sides+(j+1)%sides, (i+1)*sides+j
            counts.append(4); connects.extend([a, d, c, b])
    # Explicit Maya arrays avoid Py3 overload ambiguity in Maya 2026/2027.
    point_array = om.MPointArray()
    for point in vertices:
        point_array.append(point)
    poly_counts = om.MIntArray()
    poly_connects = om.MIntArray()
    for count in counts:
        poly_counts.append(int(count))
    for index in connects:
        poly_connects.append(int(index))
    mesh_fn = om.MFnMesh()
    obj = mesh_fn.create(point_array, poly_counts, poly_connects)
    mesh = om.MFnDependencyNode(obj).name()
    transform = (cmds.listRelatives(mesh, parent=True) or [mesh])[0]
    transform = cmds.rename(transform, name)
    cmds.parent(transform, parent)
    return transform, samples


def _crystal_segment(pos, direction, length, radius, shader, name, parent):
    # Stable per-segment twist exposes different hexagonal faces to the camera.
    # Without this, every prism presents the same broad face and reads flat.
    twist = (sum(ord(ch) for ch in name) * 17) % 60
    body = cmds.polyCylinder(name=name + "_body", radius=radius, height=length*.70,
                             subdivisionsX=6, subdivisionsY=1)[0]
    mid = _v_add(pos, _v_scale(direction, length*.35))
    cmds.xform(body, ws=True, t=mid); _aim_y(body, direction)
    cmds.rotate(0, twist, 0, body, relative=True, objectSpace=True)
    _assign(body, shader)
    _assign_hex_facets(body, shader)
    try:
        # A tiny one-segment chamfer creates the thin highlight bands visible
        # on real crystal edges without rounding the hexagonal silhouette.
        cmds.polyBevel3(body, fraction=.045, segments=1,
                         offsetAsFraction=True, chamfer=True, ch=False)
        cmds.polySoftEdge(body, angle=0, ch=False)
    except (RuntimeError, ValueError):
        pass
    tip = cmds.polyCone(name=name + "_tip", radius=radius*.93, height=length*.36,
                        subdivisionsAxis=6, subdivisionsHeight=1)[0]
    cmds.xform(tip, ws=True, t=_v_add(pos, _v_scale(direction, length*.88)))
    _aim_y(tip, direction)
    cmds.rotate(0, twist, 0, tip, relative=True, objectSpace=True)
    _assign(tip, shader)
    _assign_hex_facets(tip, shader)
    try:
        cmds.polyBevel3(tip, fraction=.035, segments=1,
                         offsetAsFraction=True, chamfer=True, ch=False)
        cmds.polySoftEdge(tip, angle=0, ch=False)
    except (RuntimeError, ValueError):
        pass
    # Milky internal growth core on larger crystals.  Seen through the outer
    # transmission layer, this creates thickness and cloudy inclusions instead
    # of an empty, uniformly coloured prism.
    core_shader = shader + "_core"
    if length > 2.6 and cmds.objExists(core_shader):
        core = cmds.polyCylinder(
            name=name + "_inclusion", radius=radius * .38,
            height=length * .58, subdivisionsX=6, subdivisionsY=1,
        )[0]
        cmds.xform(core, ws=True, t=_v_add(pos, _v_scale(direction, length * .40)))
        _aim_y(core, direction)
        cmds.rotate(0, twist + 11, 0, core, relative=True, objectSpace=True)
        _assign(core, core_shader)
        cmds.parent(core, parent)
        # Two thin internal fracture planes catch grazing light and break up the
        # otherwise uniform transmission. They stay inside the prism and use a
        # milky mineral shader rather than a noisy outer surface.
        fracture_shader = shader + "_fracture"
        if ("CCV10_hero" in name and
                cmds.objExists(fracture_shader)):
            for fracture_index, along in enumerate((.30, .54)):
                fracture = cmds.polyCube(
                    name=name + "_fracture_{}".format(fracture_index),
                    width=radius * 1.18,
                    height=max(.012, length * .012),
                    depth=radius * .92,
                )[0]
                cmds.xform(
                    fracture, worldSpace=True,
                    translation=_v_add(pos, _v_scale(direction,
                                                     length * along)),
                )
                _aim_y(fracture, direction)
                cmds.rotate(
                    17 + fracture_index * 19,
                    twist + fracture_index * 23,
                    -11 + fracture_index * 16,
                    fracture, relative=True, objectSpace=True,
                )
                _assign(fracture, fracture_shader)
                cmds.parent(fracture, parent)
    cmds.parent(body, tip, parent)


def _branch_direction(axis, rng, angle):
    ref = (0, 1, 0) if abs(axis[1]) < .9 else (1, 0, 0)
    p = _v_norm(_v_cross(axis, ref)); q = _v_cross(p, axis)
    az = rng.uniform(0, math.pi*2)
    return _v_norm(_v_add(_v_scale(axis, math.cos(angle)),
                           _v_scale(_v_add(_v_scale(p, math.cos(az)), _v_scale(q, math.sin(az))), math.sin(angle))))


def _grow_lsystem(pos, direction, length, radius, shader, depth, rng, parent, label):
    """Mineral interpretation of ``F -> F[+F][-F]``.

    Unlike a botanical turtle, child crystals do not continue from the end of
    the parent like tree limbs.  Each recursive successor receives a slightly
    offset root beside its parent and grows in a near-parallel direction.  The
    grammar therefore remains explicit while the silhouette reads as a quartz
    cluster with visible gaps between individual prisms.
    """
    _crystal_segment(pos, direction, length, radius, shader, label, parent)
    if depth <= 0:
        return 1
    count = 1
    # Two successors match the literal [+F][-F] rule.  Mineral crystals do not
    # sprout from the middle of a trunk: both successors begin close to the
    # shared root and diverge through neighbouring cracks.  This keeps the
    # grammar explicit while producing a natural quartz-cluster silhouette.
    for k, sign in enumerate((-1, 1)):
        d = _branch_direction(direction, rng, sign * rng.uniform(.28, .48))
        lateral = _v_sub(d, _v_scale(direction, _v_dot(d, direction)))
        lateral = _v_norm(lateral)
        branch_at = _v_add(
            _v_add(pos, _v_scale(direction, length * (.035 + .055 * k))),
            _v_scale(lateral, radius * (1.05 + .35 * k)),
        )
        count += _grow_lsystem(branch_at, d, length*rng.uniform(.48, .68),
                               radius*rng.uniform(.52, .68), shader,
                               depth-1, rng, parent, label + "_{}".format(k))
    return count


def _rock_bed(chamber, rock, hero, rng):
    """Build a broken mineral shelf instead of a smooth product-display dome."""
    bed_group = cmds.group(empty=True, name="CCV10_crystal_bed", parent=hero)
    # Overlapping, rotated low-resolution stones erase the circular silhouette.
    stones = [
        (0.0, 0.0, 5.2, 3.8, 1.05),
        (-3.6, 1.1, 3.2, 2.6, .78),
        (3.4, .7, 3.5, 2.4, .72),
        (-1.0, 3.7, 3.8, 2.5, .82),
        (2.0, -3.2, 3.4, 2.8, .68),
        (-3.2, -2.8, 2.8, 2.2, .62),
    ]
    top_y = chamber[1] - 5.55
    for i, (dx, dz, sx, sz, sy) in enumerate(stones):
        stone = cmds.polySphere(
            name="CCV10_bed_rock_{:02d}".format(i), radius=1.0,
            subdivisionsX=10, subdivisionsY=6,
        )[0]
        cmds.xform(
            stone, worldSpace=True,
            translation=(chamber[0] + dx + rng.uniform(-.25, .25),
                         top_y - sy * .82 + rng.uniform(-.12, .08),
                         chamber[2] + dz + rng.uniform(-.25, .25)),
            rotation=(rng.uniform(-12, 12), rng.uniform(0, 55),
                      rng.uniform(-10, 10)),
        )
        cmds.scale(sx, sy, sz, stone, relative=True)
        _assign(stone, rock)
        cmds.parent(stone, bed_group)
    # Small angular rubble hides intersections and gives the eye a scale cue.
    for i in range(18):
        angle = rng.uniform(0, math.pi * 2)
        distance = rng.uniform(2.2, 6.0)
        rubble = cmds.polyPlatonicSolid(
            name="CCV10_rubble_{:02d}".format(i), solidType=2,
        )[0]
        size = rng.uniform(.18, .58)
        cmds.xform(
            rubble, worldSpace=True,
            translation=(chamber[0] + math.cos(angle) * distance,
                         top_y + rng.uniform(-.18, .04),
                         chamber[2] + math.sin(angle) * distance),
            rotation=(rng.uniform(0, 180), rng.uniform(0, 180),
                      rng.uniform(0, 180)),
        )
        cmds.scale(size * rng.uniform(.7, 1.5), size,
                   size * rng.uniform(.7, 1.5), rubble, relative=True)
        _assign(rubble, rock)
        cmds.parent(rubble, bed_group)
    return bed_group


def _chamber_shell(chamber, rock, cave):
    """Create an explicit cavern room with open tunnel portals.

    Inflating neighbouring tube rings can self-intersect and occlude the
    fly-through.  The chamber is therefore its own inward-facing ellipsoid.
    Polar face bands are removed where the main route enters and exits.
    """
    shell = cmds.polySphere(
        name="CCV10_hero_chamber", radius=1.0,
        subdivisionsX=32, subdivisionsY=18,
    )[0]
    cmds.xform(shell, worldSpace=True, translation=chamber)
    cmds.scale(13.0, 9.5, 14.0, shell, relative=True)
    cmds.makeIdentity(shell, apply=True, translate=False, rotate=False,
                      scale=True, normal=False)
    face_count = cmds.polyEvaluate(shell, face=True)
    portals = []
    for face in range(face_count):
        component = "{}.f[{}]".format(shell, face)
        bounds = cmds.xform(component, query=True, worldSpace=True,
                            boundingBox=True)
        centre_z = (bounds[2] + bounds[5]) * .5
        if (centre_z < chamber[2] - 10.8 or
                centre_z > chamber[2] + 10.8):
            portals.append(component)
    if portals:
        cmds.delete(portals)
    cmds.polyNormal(shell, normalMode=0, userNormalMode=0,
                    constructionHistory=False)
    _assign(shell, rock)
    cmds.parent(shell, cave)
    return shell


def _soft_point(name, position, colour, intensity, radius, parent):
    """Arnold-friendly soft point light with a stable transform name."""
    initial_shape = cmds.pointLight(name=name + "Shape")
    transform = (cmds.listRelatives(initial_shape, parent=True) or
                 [initial_shape])[0]
    transform = cmds.rename(transform, name)
    shape = (cmds.listRelatives(transform, shapes=True, type="pointLight") or
             [initial_shape])[0]
    cmds.xform(transform, worldSpace=True, translation=position)
    _set(shape, "color", colour, True)
    _set(shape, "intensity", intensity)
    _set(shape, "decayRate", 2)
    _set(shape, "aiRadius", radius)
    cmds.parent(transform, parent)
    return transform


def _cluster(sample, scale, shader, index, parent, rng):
    pos, inward = sample
    group = cmds.group(empty=True, name="CCV10_cluster_{:03d}".format(index), parent=parent)
    # Scale animation must grow out of the mineral root, not the world origin.
    cmds.xform(group, worldSpace=True, pivots=pos)
    # Quartz-like 1:8–1:12 proportion: avoid the old broad low-poly columns.
    pieces = _grow_lsystem(pos, inward, scale, scale*.095, shader, 2, rng, group, "CCV10_xtal_{:03d}".format(index))
    cmds.addAttr(group, ln="lsystemRule", dt="string"); cmds.setAttr(group+".lsystemRule", "F -> F[+F][-F]", type="string")
    cmds.addAttr(group, ln="lsystemDepth", at="long", dv=2); cmds.setAttr(group+".lsystemDepth", 2)
    return group, _v_add(pos, _v_scale(inward, scale*.5)), pieces


def _camera(path, parent, chamber):
    cam = cmds.camera(name="CCV10_tunnel_cam", focalLength=28)[0]
    shape = cmds.listRelatives(cam, s=True, type="camera")[0]
    look = cmds.spaceLocator(name="CCV10_tunnel_lookat")[0]; cmds.setAttr(look+".visibility", 0)
    cmds.parent(cam, look, parent)

    def key_pose(frame, pos, target, focal):
        for attr, value in zip(("translateX", "translateY", "translateZ"), pos):
            cmds.setKeyframe(cam, at=attr, t=frame, v=value)
        for attr, value in zip(("translateX", "translateY", "translateZ"),
                               target):
            cmds.setKeyframe(look, at=attr, t=frame, v=value)
        cmds.setKeyframe(shape, at="focalLength", t=frame, v=focal)

    # First act: travel the generated centreline to the chamber threshold.
    for i, (pos, radius) in enumerate(path[:13]):
        frame = i * 30
        ahead = path[min(i+2, len(path)-1)][0]
        key_pose(frame, pos, (ahead[0], ahead[1] - .8, ahead[2]),
                 27 if i < 10 else 29)

    # Second act: move laterally into the room, reveal the growing garden, and
    # orbit around it rather than flying directly through the tallest crystal.
    reveal = (chamber[0] + .20, chamber[1] - 3.0, chamber[2] + 1.0)
    key_pose(390, (chamber[0] + 8.5, chamber[1] + 1.0,
                   chamber[2] - 2.0), reveal, 36)
    key_pose(450, (chamber[0] + 9.5, chamber[1] + .5,
                   chamber[2] + 1.5), reveal, 38)
    key_pose(510, (chamber[0] + 8.0, chamber[1] - .5,
                   chamber[2] + .0), reveal, 34)

    # Third act: continue a protected hero orbit long enough for the complete
    # L-system growth reveal, then rejoin the route beyond the garden.
    key_pose(570, (chamber[0] + 6.0, chamber[1] + .2,
                   chamber[2] + 4.8), reveal, 34)
    key_pose(630, (chamber[0] + 2.0, chamber[1] + .8,
                   chamber[2] + 8.0), reveal, 32)
    key_pose(660, (chamber[0] - 1.0, chamber[1] + .5,
                   chamber[2] + 9.0), path[18][0], 30)
    # Stop two rings before the open end. At the final ring there is no valid
    # forward look vector and the camera can turn into the wall.
    for i in range(17, min(23, len(path))):
        frame = 690 + (i - 17) * 30
        pos = path[i][0]
        ahead = path[min(i+2, len(path)-1)][0]
        key_pose(frame, pos, (ahead[0], ahead[1] - .6, ahead[2]), 28)

    cmds.aimConstraint(look, cam, aimVector=(0,0,-1), upVector=(0,1,0),
                       worldUpType="vector", worldUpVector=(0,1,0), name="CCV10_tunnel_aim")
    try:
        cmds.keyTangent(cam, look, shape, inTangentType="auto",
                        outTangentType="auto")
    except RuntimeError:
        pass
    end_frame = 840
    cmds.playbackOptions(min=0, max=end_frame, animationStartTime=0,
                         animationEndTime=end_frame)
    cmds.setAttr(shape+".renderable", 1)
    return cam


def build(seed=20260723, density=32, fog_density=.01, render=False):
    """Build and save a fully procedural tunnel scene; safe to call from UI."""
    rng = random.Random(seed)
    for node in cmds.ls("crystalCavern_v10*") or []:
        try: cmds.delete(node)
        except Exception: pass
    for node in cmds.ls("CCV10_*") or []:
        try: cmds.delete(node)
        except Exception: pass
    try:
        if not cmds.pluginInfo("mtoa", q=True, loaded=True): cmds.loadPlugin("mtoa")
    except RuntimeError: pass
    try:
        # A truly empty Maya scene may load mtoa without creating Arnold's
        # default option/driver/filter nodes. Render must work on first click.
        import mtoa.core
        mtoa.core.createOptions()
    except (ImportError, RuntimeError, AttributeError):
        pass
    root = cmds.group(empty=True, name=ROOT)
    graph = tunnel_graph(seed)
    rock = _shader("CCV10_cave_rock", (.055,.047,.08), roughness=.82)
    _add_rock_detail(rock)
    gems = [_shader("CCV10_ice", (.58,.70,.76), .62, .10, .014),
            _shader("CCV10_amethyst", (.30,.14,.36), .52, .12, .016),
            _shader("CCV10_selenite", (.74,.77,.78), .58, .08, .010)]
    _shader("CCV10_ice_facetLight", (.78,.88,.94), .55, .07, .014)
    _shader("CCV10_ice_facetDark", (.42,.58,.68), .55, .14, .010)
    _shader("CCV10_amethyst_facetLight", (.56,.29,.66), .55, .09, .014)
    _shader("CCV10_amethyst_facetDark", (.31,.14,.38), .55, .15, .010)
    _shader("CCV10_selenite_facetLight", (.90,.91,.88), .55, .06, .010)
    _shader("CCV10_selenite_facetDark", (.64,.69,.71), .55, .12, .008)
    _shader("CCV10_ice_core", (.74,.82,.85), .04, .38, .030)
    _shader("CCV10_amethyst_core", (.48,.32,.52), .03, .40, .026)
    _shader("CCV10_selenite_core", (.84,.84,.80), .03, .36, .022)
    _shader("CCV10_ice_fracture", (.84,.91,.95), .08, .10, .026)
    _shader("CCV10_amethyst_fracture", (.62,.40,.68), .06, .12, .022)
    _shader("CCV10_selenite_fracture", (.92,.92,.88), .07, .09, .020)
    cave = cmds.group(empty=True, name="CCV10_tunnel_cave", parent=root)
    main, samples = _create_tube("CCV10_main_tunnel", graph["main"], cave, rng)
    branch, branch_samples = _create_tube("CCV10_branch_tunnel", graph["branch"], cave, rng)
    _assign(main, rock); _assign(branch, rock)
    chamber = graph["main"][14][0]
    _chamber_shell(chamber, rock, cave)
    # Portal hand-off: once the camera has crossed into the explicit chamber,
    # hide the overlapping inflated tube rings; restore them before exit.
    for tunnel in (main, branch):
        for frame, visibility in ((0, 1), (360, 1), (375, 0),
                                  (525, 0), (545, 1)):
            cmds.setKeyframe(tunnel, at="visibility", t=frame,
                             v=visibility)
        try:
            cmds.keyTangent(tunnel, at="visibility",
                            inTangentType="step", outTangentType="step")
        except RuntimeError:
            pass
    # Sample only wall/ceiling surfaces; a central clear corridor remains.
    candidates = [s for i, s in enumerate(samples + branch_samples) if (i % 3) != 1]
    rng.shuffle(candidates)
    crystals = cmds.group(empty=True, name="CCV10_lsystem_crystals", parent=root)
    for frame, visibility in ((0, 1), (360, 1), (375, 0),
                              (525, 0), (545, 1)):
        cmds.setKeyframe(crystals, at="visibility", t=frame, v=visibility)
    try:
        cmds.keyTangent(crystals, at="visibility",
                        inTangentType="step", outTangentType="step")
    except RuntimeError:
        pass
    anchors, pieces = [], 0
    for i, sample in enumerate(candidates[:max(16, int(density))]):
        # First three are hero formations.  Their deliberately larger scale and
        # full 13-segment recursive structure are used by the chamber camera.
        # Keep the centreline physically clear for the fly-through. Earlier
        # 5.5–7.0 unit wall crystals could span most of a 7.5 unit tunnel.
        scale = rng.uniform(3.5, 4.8) if i < 3 else rng.uniform(2.2, 3.8)
        cluster, anchor, count = _cluster(sample, scale, gems[i % len(gems)], i, crystals, rng)
        anchors.append(anchor); pieces += count
        # Sequential growth makes the rewrite readable in the fly-through.
        start = i * 8; end = start + 42
        for axis in "XYZ":
            cmds.setKeyframe(cluster, at="scale"+axis, t=start, v=.01)
            cmds.setKeyframe(cluster, at="scale"+axis, t=end, v=1.0)

    # A chamber-centre "hero garden" guarantees that the recursive grammar is
    # legible in the final fly-through, even when wall clusters sit in shadow.
    hero = cmds.group(empty=True, name="CCV10_hero_garden", parent=root)
    _rock_bed(chamber, rock, hero, rng)
    for i, (dx, dz, scale) in enumerate(((0.0, 0.0, 4.8), (2.2, 1.4, 3.6),
                                          (-2.2, 2.0, 3.2), (.8, 3.8, 2.8))):
        hero_cluster = cmds.group(
            empty=True, name="CCV10_hero_cluster_{:02d}".format(i),
            parent=hero,
        )
        base_pos = (chamber[0] + dx, chamber[1] - 5.5, chamber[2] + dz)
        cmds.xform(hero_cluster, worldSpace=True, pivots=base_pos)
        _grow_lsystem(base_pos,
                      (0, 1, 0), scale, scale * .095, gems[i % len(gems)], 2,
                      rng, hero_cluster, "CCV10_hero_{}".format(i))
        # Grow while the camera is in the protected chamber orbit so the
        # animation demonstrates the grammar instead of finishing off-screen.
        grow_start = 390 + i * 18
        for axis in "XYZ":
            cmds.setKeyframe(hero_cluster, at="scale" + axis,
                             t=grow_start, v=.01)
            cmds.setKeyframe(hero_cluster, at="scale" + axis,
                             t=grow_start + 52, v=1.0)
    # Low surrounding shards establish scale and stop the hero crystals from
    # floating like an isolated product render.
    for i in range(9):
        angle = math.pi * 2.0 * i / 9.0 + rng.uniform(-.16, .16)
        radius = rng.uniform(3.0, 5.4)
        pos = (chamber[0] + math.cos(angle) * radius,
               chamber[1] - 5.55,
               chamber[2] + math.sin(angle) * radius)
        _grow_lsystem(pos, (0, 1, 0), rng.uniform(1.1, 2.2),
                      rng.uniform(.10, .18), gems[i % len(gems)], 1, rng,
                      hero, "CCV10_shard_{}".format(i))
    cam = _camera(graph["main"], root, chamber)
    lights = cmds.group(empty=True, name="CCV10_lights", parent=root)
    # A clean four-light chamber rig, calibrated in a scene containing only
    # generated content. Soft point lights avoid visible Arnold emitter panels.
    _soft_point(
        "CCV10_hero_key",
        (chamber[0] + 5.5, chamber[1] + 6.8, chamber[2] - 4.0),
        (.64, .84, 1.0), 1050, 2.8, lights,
    )
    _soft_point(
        "CCV10_hero_rim",
        (chamber[0] - 5.5, chamber[1] + 1.5, chamber[2] + 6.0),
        (.52, .18, .86), 520, 2.2, lights,
    )
    _soft_point(
        "CCV10_hero_warm",
        (chamber[0] + 3.0, chamber[1] - 1.5, chamber[2] - 3.0),
        (1.0, .34, .14), 45, 1.8, lights,
    )
    _soft_point(
        "CCV10_hero_fill",
        (chamber[0] + 9.0, chamber[1] + 2.0, chamber[2] - 9.3),
        (.50, .74, 1.0), 460, 3.5, lights,
    )
    # Low-energy route markers preserve tunnel depth without flooding the room.
    _soft_point("CCV10_entry", graph["main"][1][0],
                (1.0, .48, .22), 260, 2.5, lights)
    _soft_point("CCV10_depth", graph["main"][-2][0],
                (.18, .38, 1.0), 320, 2.5, lights)
    dome = cmds.shadingNode("aiSkyDomeLight", asLight=True, name="CCV10_ambient")
    _set(dome,"color",(.012,.016,.035),True); _set(dome,"intensity",.055)
    dome_parent = (cmds.listRelatives(dome, parent=True) or [dome])[0]
    try:
        cmds.parent(dome_parent, lights)
    except RuntimeError:
        pass
    beam = cmds.spotLight(name="CCV10_volume_beam")
    _set(beam, "color", (.52, .70, 1.0), True)
    _set(beam, "intensity", 80)
    _set(beam, "coneAngle", 34)
    _set(beam, "penumbraAngle", 8)
    _set(beam, "decayRate", 2)
    beam_tr = (cmds.listRelatives(beam, parent=True) or [beam])[0]
    cmds.xform(beam_tr, worldSpace=True,
               translation=(chamber[0] + 6, chamber[1] + 8,
                            chamber[2] - 9))
    beam_target = cmds.spaceLocator(name="CCV10_volume_beam_target")[0]
    cmds.xform(beam_target, worldSpace=True, translation=chamber)
    cmds.aimConstraint(beam_target, beam_tr, aimVector=(0, 0, -1),
                       upVector=(0, 1, 0), worldUpType="vector",
                       worldUpVector=(0, 1, 0))
    cmds.setAttr(beam_target + ".visibility", 0)
    try:
        cmds.parent(beam_tr, beam_target, lights)
    except RuntimeError:
        pass
    try:
        fog = cmds.createNode("aiAtmosphereVolume", name="CCV10_atmosphere")
        _set(fog, "density", max(.0015, min(float(fog_density), .006)))
        _set(fog, "color", (.18, .22, .34), True)
        cmds.connectAttr(fog + ".outColor",
                         "defaultArnoldRenderOptions.atmosphere", force=True)
    except (RuntimeError, ValueError):
        pass
    cmds.setAttr("defaultRenderGlobals.currentRenderer", "arnold", type="string")
    cmds.setAttr("defaultResolution.width", 1920); cmds.setAttr("defaultResolution.height", 1080)
    os.makedirs(OUT_DIR, exist_ok=True)
    cmds.file(rename=os.path.join(OUT_DIR, "crystal_cavern_tunnel_v10.ma")); cmds.file(save=True, type="mayaAscii", force=True)
    print("CCV10 complete: tunnel graph={} main sections + branch; {} L-system clusters / {} crystal segments".format(len(graph['main']), len(anchors), pieces))
    return cam


if __name__ == "__main__":
    build()
