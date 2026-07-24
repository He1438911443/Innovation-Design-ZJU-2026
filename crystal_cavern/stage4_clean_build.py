"""Clean-scene product validation for the integrated v10 generator."""
from __future__ import print_function

import importlib
import os
import sys
import time
import traceback

import maya.cmds as cmds


PROJECT = "/Users/xixi/大学/未来创新设计/crystal_cavern"
OUT = os.path.join(PROJECT, "renders", "tunnel_v10")
CHECKPOINT = os.path.join(OUT, "crystal_cavern_stage3_checkpoint_v22.ma")
CLEAN_SCENE = os.path.join(OUT, "crystal_cavern_clean_generator_v18.ma")
IMAGE = os.path.join(OUT, "stage4_portal_frame390_v4.png")
STATUS = "/tmp/ccv_stage4_clean_status.txt"


def run():
    os.makedirs(OUT, exist_ok=True)
    # Preserve the approved live lookdev state before switching to a clean file.
    if not os.path.exists(CHECKPOINT):
        cmds.file(rename=CHECKPOINT)
        cmds.file(save=True, type="mayaAscii", force=True)
    cmds.file(new=True, force=True)

    if PROJECT not in sys.path:
        sys.path.insert(0, PROJECT)
    import tunnel_cavern
    importlib.reload(tunnel_cavern)

    start = time.time()
    tunnel_cavern.build(seed=20260723, density=32, fog_density=.0025)
    build_seconds = time.time() - start

    cmds.currentTime(390)
    camera_shape = (
        cmds.ls("CCV10_tunnel_camShape*", type="camera") or [None]
    )[0]
    if not camera_shape:
        raise RuntimeError("Generated fly-through camera is missing")
    for shape in cmds.ls(type="camera") or []:
        cmds.setAttr(shape + ".renderable", int(shape == camera_shape))

    if not cmds.objExists("defaultArnoldRenderOptions"):
        import mtoa.core
        mtoa.core.createOptions()
    cmds.setAttr("defaultArnoldRenderOptions.AASamples", 2)
    for attr in ("GIDiffuseSamples", "GISpecularSamples",
                 "GITransmissionSamples", "GIVolumeSamples"):
        if cmds.objExists("defaultArnoldRenderOptions." + attr):
            cmds.setAttr("defaultArnoldRenderOptions." + attr, 1)
    cmds.setAttr("defaultArnoldDriver.aiTranslator", "png", type="string")
    cmds.arnoldRender(camera=camera_shape, width=640, height=360)
    cmds.renderWindowEditor("renderView", edit=True, writeImage=IMAGE)

    cmds.file(rename=CLEAN_SCENE)
    cmds.file(save=True, type="mayaAscii", force=True)
    with open(STATUS, "w") as handle:
        handle.write(
            "OK\nbuild_seconds={:.3f}\n{}\n{}\n{}\n".format(
                build_seconds, IMAGE, CLEAN_SCENE, CHECKPOINT
            )
        )


try:
    run()
except Exception:
    with open(STATUS, "w") as handle:
        handle.write("ERROR\n" + traceback.format_exc())
    raise
