"""Fast Stage 3 composition/light iteration on the already-built scene."""
from __future__ import print_function

import os
import traceback

import maya.cmds as cmds


OUT = "/Users/xixi/大学/未来创新设计/crystal_cavern/renders/tunnel_v10"
IMAGE = os.path.join(OUT, "stage3_natural_cluster_v22.png")
STATUS = "/tmp/ccv_stage3_v22_status.txt"


def aim_at(transform, target):
    locator = cmds.spaceLocator(name="CCV22_camera_target")[0]
    cmds.xform(locator, worldSpace=True, translation=target)
    constraint = cmds.aimConstraint(
        locator, transform, aimVector=(0, 0, -1), upVector=(0, 1, 0),
        worldUpType="vector", worldUpVector=(0, 1, 0),
    )
    cmds.delete(constraint, locator)


def soft_point(name, position, colour, intensity, radius):
    initial_shape = cmds.pointLight(name=name + "Shape")
    transform = (cmds.listRelatives(initial_shape, parent=True) or
                 [initial_shape])[0]
    transform = cmds.rename(transform, name)
    shape = (cmds.listRelatives(transform, shapes=True, type="pointLight") or
             [initial_shape])[0]
    cmds.xform(transform, worldSpace=True, translation=position)
    cmds.setAttr(shape + ".color", *colour, type="double3")
    cmds.setAttr(shape + ".intensity", intensity)
    cmds.setAttr(shape + ".decayRate", 2)
    if cmds.objExists(shape + ".aiRadius"):
        cmds.setAttr(shape + ".aiRadius", radius)
    return transform


def run():
    # The hero checkpoint judges cluster structure. Peripheral wall clusters are
    # restored immediately after rendering and remain in the fly-through scene.
    hidden_for_hero = [
        "CCV10_lsystem_crystals",
        "CCV10_main_tunnel",
        "CCV10_branch_tunnel",
    ]
    old_visibilities = {}
    for node in hidden_for_hero:
        if cmds.objExists(node):
            old_visibilities[node] = cmds.getAttr(node + ".visibility")
            cmds.setAttr(node + ".visibility", 0)
    # The working file contains ungrouped legacy ``cry_body_*`` meshes. Keep
    # them recoverable, but exclude every non-v10 mesh from this clean render.
    for shape in cmds.ls(type="mesh", long=True) or []:
        if (shape.startswith("|crystalCavern_v10|") or
                "CCV22_hero_chamber" in shape):
            continue
        transform = (cmds.listRelatives(shape, parent=True, fullPath=True) or
                     [shape])[0]
        if cmds.objExists(transform + ".visibility"):
            old_visibilities[transform] = cmds.getAttr(
                transform + ".visibility"
            )
            cmds.setAttr(transform + ".visibility", 0)
    # Also isolate legacy top-level lights (pointLight1..., ambientLight1...).
    # They were previously hidden behind old meshes and massively overexpose a
    # clean chamber once those meshes are excluded.
    for shape in cmds.ls(lights=True, long=True) or []:
        transform = (cmds.listRelatives(shape, parent=True, fullPath=True) or
                     [shape])[0]
        if cmds.objExists(transform + ".visibility"):
            old_visibilities[transform] = cmds.getAttr(
                transform + ".visibility"
            )
            cmds.setAttr(transform + ".visibility", 0)
    try:
        camera_shape = (cmds.ls("CCV21_stage3_camShape*", type="camera") or [None])[0]
        if not camera_shape:
            raise RuntimeError("Stage 3 camera missing")
        camera = (cmds.listRelatives(camera_shape, parent=True) or [camera_shape])[0]

        # The hero chamber is an explicit inward-facing shell, not an inflated
        # tunnel cross-section. It prevents neighbouring tube rings from
        # occluding the chamber and becomes the fly-through destination.
        chamber = (-3.634726040103702, -3.519265956723606, 7.0)
        if cmds.objExists("CCV22_hero_chamber"):
            cmds.delete("CCV22_hero_chamber")
        chamber_shell = cmds.polySphere(
            name="CCV22_hero_chamber", radius=1.0,
            subdivisionsX=32, subdivisionsY=18,
        )[0]
        cmds.xform(chamber_shell, worldSpace=True, translation=chamber)
        cmds.scale(13.0, 9.5, 14.0, chamber_shell, relative=True)
        cmds.polyNormal(chamber_shell, normalMode=0, userNormalMode=0,
                        constructionHistory=False)
        cmds.select(chamber_shell, replace=True)
        cmds.hyperShade(assign="CCV10_cave_rock")

        target = (chamber[0] + .20, chamber[1] - 3.0, chamber[2] + 1.0)
        position = (chamber[0] + 8.2, chamber[1] + 1.0,
                    chamber[2] - 8.5)
        cmds.xform(camera, worldSpace=True, translation=position)
        cmds.setAttr(camera_shape + ".focalLength", 42)
        cmds.setAttr(camera_shape + ".horizontalFilmAperture", 1.25)
        aim_at(camera, target)

        # Maya 2027 may still show Arnold area emitters despite aiCamera=0.
        # Soft point lights have no renderable panel and remain deterministic.
        for old_light in (
            "CCV21_moon_key", "CCV21_amethyst_rim",
            "CCV21_warm_edge", "CCV23_front_fill", "aiAreaLight1",
            "CCV24_moon_key", "CCV24_amethyst_rim",
            "CCV24_warm_edge", "CCV24_front_fill",
        ):
            if cmds.objExists(old_light):
                cmds.delete(old_light)
        soft_point(
            "CCV24_moon_key",
            (chamber[0] + 5.5, chamber[1] + 6.8, chamber[2] - 4.0),
            (.64, .84, 1.0), 700, 2.8,
        )
        soft_point(
            "CCV24_amethyst_rim",
            (chamber[0] - 5.5, chamber[1] + 1.5, chamber[2] + 6.0),
            (.52, .18, .86), 350, 2.2,
        )
        soft_point(
            "CCV24_warm_edge",
            (chamber[0] + 3.0, chamber[1] - 1.5, chamber[2] - 3.0),
            (1.0, .34, .14), 15, 1.8,
        )
        soft_point(
            "CCV24_front_fill",
            (position[0] + .8, position[1] + 1.0, position[2] - .8),
            (.50, .74, 1.0), 280, 3.5,
        )

        # Pull the cave back into shadow and reserve bright values for facets.
        if cmds.objExists("CCV10_cave_rock.baseColor"):
            cmds.setAttr("CCV10_cave_rock.baseColor",
                         .052, .036, .070, type="double3")
        # Smooth crystal faces and readable shadow facets: surface variation is
        # subtle; cloudy cores provide the mineral complexity.
        for bump in cmds.ls("CCV10_*_microBump") or []:
            if cmds.objExists(bump + ".bumpDepth"):
                cmds.setAttr(bump + ".bumpDepth", .018)
        facet_colours = {
            "CCV10_ice_facetLight": (.78, .88, .94),
            "CCV10_ice_facetDark": (.42, .58, .68),
            "CCV10_amethyst_facetLight": (.56, .29, .66),
            "CCV10_amethyst_facetDark": (.31, .14, .38),
            "CCV10_selenite_facetLight": (.90, .91, .88),
            "CCV10_selenite_facetDark": (.64, .69, .71),
        }
        for shader, colour in facet_colours.items():
            if cmds.objExists(shader + ".baseColor"):
                cmds.setAttr(shader + ".baseColor", *colour, type="double3")
            if cmds.objExists(shader + ".transmission"):
                cmds.setAttr(shader + ".transmission", .55)
        if cmds.objExists("CCV10_volume_beam.intensity"):
            cmds.setAttr("CCV10_volume_beam.intensity", 50)
        if cmds.objExists("CCV10_chamber.intensity"):
            cmds.setAttr("CCV10_chamber.intensity", 12)
        if cmds.objExists("CCV10_atmosphere.density"):
            cmds.setAttr("CCV10_atmosphere.density", .0025)

        cmds.setAttr("defaultArnoldRenderOptions.AASamples", 3)
        for attr in ("GIDiffuseSamples", "GISpecularSamples",
                     "GITransmissionSamples", "GIVolumeSamples"):
            if cmds.objExists("defaultArnoldRenderOptions." + attr):
                cmds.setAttr("defaultArnoldRenderOptions." + attr, 1)
        cmds.arnoldRender(camera=camera_shape, width=800, height=450)
        cmds.renderWindowEditor("renderView", edit=True, writeImage=IMAGE)
    finally:
        for node, visibility in old_visibilities.items():
            if cmds.objExists(node):
                cmds.setAttr(node + ".visibility", visibility)

    with open(STATUS, "w") as handle:
        handle.write("OK\n{}\n".format(IMAGE))


try:
    run()
except Exception:
    with open(STATUS, "w") as handle:
        handle.write("ERROR\n" + traceback.format_exc())
    raise
