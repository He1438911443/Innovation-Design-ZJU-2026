"""Finish the Stage 3 lookdev render after removing legacy scene baggage."""
from __future__ import print_function

import os
import traceback

import maya.cmds as cmds


OUT = "/Users/xixi/大学/未来创新设计/crystal_cavern/renders/tunnel_v10"
BACKUP = os.path.join(OUT, "crystal_cavern_stage3_with_legacy_backup.ma")
CLEAN_SCENE = os.path.join(OUT, "crystal_cavern_stage3_natural_v14.ma")
IMAGE = os.path.join(OUT, "stage3_natural_cluster_v5.png")
STATUS = "/tmp/ccv_stage3_v5_status.txt"


def run():
    os.makedirs(OUT, exist_ok=True)

    # Preserve the exact pre-cleanup state before removing historical content.
    if not os.path.exists(BACKUP):
        cmds.file(rename=BACKUP)
        cmds.file(save=True, type="mayaAscii", force=True)

    if cmds.objExists("crystalCavern_v9"):
        cmds.delete("crystalCavern_v9")
    # Legacy default lights were not grouped under v9 and would flatten the
    # authored three-light look if allowed into the render.
    for node in cmds.ls(type=("ambientLight", "directionalLight", "pointLight")) or []:
        parent = (cmds.listRelatives(node, parent=True) or [node])[0]
        if not parent.startswith("CCV10_"):
            try:
                cmds.delete(parent)
            except (RuntimeError, ValueError):
                pass

    camera_shape = "CCV21_stage3_camShape"
    if not cmds.objExists(camera_shape):
        matches = cmds.ls("CCV21_stage3_camShape*", type="camera") or []
        if not matches:
            raise RuntimeError("Stage 3 camera is missing")
        camera_shape = matches[0]

    cmds.setAttr("defaultArnoldRenderOptions.AASamples", 3)
    for attr, value in (
        ("GIDiffuseSamples", 2),
        ("GISpecularSamples", 2),
        ("GITransmissionSamples", 2),
        ("GIVolumeSamples", 1),
    ):
        if cmds.objExists("defaultArnoldRenderOptions." + attr):
            cmds.setAttr("defaultArnoldRenderOptions." + attr, value)
    cmds.setAttr("defaultArnoldDriver.aiTranslator", "png", type="string")
    cmds.arnoldRender(camera=camera_shape, width=800, height=450)
    cmds.renderWindowEditor("renderView", edit=True, writeImage=IMAGE)

    cmds.file(rename=CLEAN_SCENE)
    cmds.file(save=True, type="mayaAscii", force=True)
    with open(STATUS, "w") as handle:
        handle.write("OK\n{}\n{}\n{}\n".format(IMAGE, CLEAN_SCENE, BACKUP))


try:
    run()
except Exception:
    with open(STATUS, "w") as handle:
        handle.write("ERROR\n" + traceback.format_exc())
    raise
