"""Rebuild the v10 cavern and render the Stage 3 natural-cluster checkpoint.

This is intentionally separate from the one-click generator: it is a compact
look-development rig for judging the generated geometry and materials.
"""
from __future__ import print_function

import importlib
import os
import re
import traceback

import maya.cmds as cmds


PROJECT = "/Users/xixi/大学/未来创新设计/crystal_cavern"
OUT = os.path.join(PROJECT, "renders", "tunnel_v10")
IMAGE = os.path.join(OUT, "stage3_natural_cluster_v4.png")
SCENE = os.path.join(OUT, "crystal_cavern_stage3_natural_v14.ma")
STATUS = "/tmp/ccv_stage3_v4_status.txt"


def set_colour(node, attr, value):
    if cmds.objExists(node + "." + attr):
        cmds.setAttr(node + "." + attr, *value, type="double3")


def aim_at(transform, target, aim=(0, 0, -1)):
    locator = cmds.spaceLocator(name=transform + "_aimTarget")[0]
    cmds.xform(locator, worldSpace=True, translation=target)
    constraint = cmds.aimConstraint(
        locator, transform, aimVector=aim, upVector=(0, 1, 0),
        worldUpType="vector", worldUpVector=(0, 1, 0),
    )
    cmds.delete(constraint, locator)


def area_light(name, position, target, colour, exposure, scale):
    shape = cmds.shadingNode("aiAreaLight", asLight=True, name=name + "Shape")
    transform = (cmds.listRelatives(shape, parent=True) or [shape])[0]
    transform = cmds.rename(transform, name)
    cmds.xform(transform, worldSpace=True, translation=position)
    cmds.scale(scale[0], scale[1], scale[2], transform, relative=True)
    set_colour(shape, "color", colour)
    cmds.setAttr(shape + ".intensity", 1.0)
    if cmds.objExists(shape + ".exposure"):
        cmds.setAttr(shape + ".exposure", exposure)
    aim_at(transform, target)
    return transform


def run():
    if PROJECT not in __import__("sys").path:
        __import__("sys").path.insert(0, PROJECT)
    import tunnel_cavern
    importlib.reload(tunnel_cavern)

    # Remove only earlier look-development helpers. The generator owns CCV10.
    for node in list(cmds.ls() or []):
        if re.match(r"^CCV(?:1[1-9]|20)_", node):
            try:
                cmds.delete(node)
            except (RuntimeError, ValueError):
                pass

    tunnel_cavern.build(seed=20260723, density=38, fog_density=.0045)
    graph = tunnel_cavern.tunnel_graph(20260723)
    chamber = graph["main"][14][0]

    # The old v9 scene remains available to the user but must never occlude v10.
    if cmds.objExists("crystalCavern_v9"):
        cmds.setAttr("crystalCavern_v9.visibility", 0)

    # Natural dark limestone: visible in the shadows, never a flat black void.
    rock = "CCV10_cave_rock"
    set_colour(rock, "baseColor", (.085, .060, .105))
    if cmds.objExists(rock + ".specularRoughness"):
        # Disconnect procedural roughness only if a stale graph drives it.
        plugs = cmds.listConnections(rock + ".specularRoughness",
                                     source=True, plugs=True) or []
        for plug in plugs:
            cmds.disconnectAttr(plug, rock + ".specularRoughness")
        cmds.setAttr(rock + ".specularRoughness", .74)

    # Cinematic chamber camera: low enough to feel inside the cave, wide enough
    # to retain wall/ceiling context around the hero cluster.
    camera, camera_shape = cmds.camera(
        name="CCV21_stage3_cam", focalLength=32,
        horizontalFilmAperture=1.45,
    )
    camera_position = (
        chamber[0] + 10.5, chamber[1] + .1, chamber[2] - 14.0
    )
    camera_target = (
        chamber[0] - .4, chamber[1] - 3.25, chamber[2] + 1.3
    )
    cmds.xform(camera, worldSpace=True, translation=camera_position)
    aim_at(camera, camera_target)
    cmds.setAttr(camera_shape + ".nearClipPlane", .08)

    # Disable other render cameras without destroying the fly-through rig.
    for shape in cmds.ls(type="camera") or []:
        cmds.setAttr(shape + ".renderable", int(shape == camera_shape))

    # Rebalance generator lights around the hero mineral shelf.
    if cmds.objExists("CCV10_chamber"):
        cmds.setAttr("CCV10_chamber.intensity", 5200)
        cmds.xform("CCV10_chamber", worldSpace=True,
                   translation=(chamber[0], chamber[1] + 3.5,
                                chamber[2] - 1.0))
    if cmds.objExists("CCV10_ambient"):
        cmds.setAttr("CCV10_ambient.intensity", .14)
    if cmds.objExists("CCV10_atmosphere.density"):
        cmds.setAttr("CCV10_atmosphere.density", .0045)

    area_light(
        "CCV21_moon_key",
        (chamber[0] + 6.5, chamber[1] + 7.5, chamber[2] - 6.0),
        camera_target, (.52, .72, 1.0), 10.0, (4.0, 4.0, 4.0),
    )
    area_light(
        "CCV21_amethyst_rim",
        (chamber[0] - 6.0, chamber[1] + 2.0, chamber[2] + 7.5),
        (chamber[0], chamber[1] - 3.0, chamber[2] + 1.0),
        (.72, .22, 1.0), 9.2, (3.0, 5.0, 3.0),
    )
    area_light(
        "CCV21_warm_edge",
        (chamber[0] + 2.0, chamber[1] - 1.0, chamber[2] - 6.0),
        (chamber[0] - 1.0, chamber[1] - 4.2, chamber[2] + .5),
        (1.0, .42, .22), 7.5, (2.0, 2.0, 2.0),
    )

    cmds.currentTime(300)
    cmds.setAttr("defaultRenderGlobals.currentRenderer", "arnold",
                 type="string")
    cmds.setAttr("defaultArnoldRenderOptions.AASamples", 4)
    for attr, value in (
        ("GIDiffuseSamples", 2),
        ("GISpecularSamples", 3),
        ("GITransmissionSamples", 3),
        ("GIVolumeSamples", 2),
    ):
        if cmds.objExists("defaultArnoldRenderOptions." + attr):
            cmds.setAttr("defaultArnoldRenderOptions." + attr, value)
    cmds.setAttr("defaultArnoldDriver.aiTranslator", "png", type="string")
    cmds.setAttr("defaultResolution.width", 960)
    cmds.setAttr("defaultResolution.height", 540)

    os.makedirs(OUT, exist_ok=True)
    cmds.arnoldRender(camera=camera_shape, width=960, height=540)
    cmds.renderWindowEditor("renderView", edit=True, writeImage=IMAGE)
    cmds.file(rename=SCENE)
    cmds.file(save=True, type="mayaAscii", force=True)
    with open(STATUS, "w") as handle:
        handle.write("OK\n{}\n{}\n".format(IMAGE, SCENE))


try:
    run()
except Exception:
    with open(STATUS, "w") as handle:
        handle.write("ERROR\n" + traceback.format_exc())
    raise
