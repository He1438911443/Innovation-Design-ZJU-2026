"""Build v20 from empty and output the two final still candidates."""
from __future__ import print_function

import importlib
import os
import sys
import time
import traceback

import maya.cmds as cmds


PROJECT = "/Users/xixi/大学/未来创新设计/crystal_cavern"
OUT = os.path.join(PROJECT, "renders", "tunnel_v10")
SCENE = os.path.join(OUT, "crystal_cavern_final_v20.ma")
HERO = os.path.join(OUT, "final_v20_hero_frame450_1280.png")
ORBIT = os.path.join(OUT, "final_v20_orbit_frame510_960.png")
STATUS = "/tmp/ccv_stage5_final_v20_status.txt"


def status(message):
    with open(STATUS, "a") as handle:
        handle.write(message + "\n")


def render(camera_shape, frame, width, height, aa, path):
    cmds.currentTime(frame)
    cmds.setAttr("defaultArnoldRenderOptions.AASamples", aa)
    for attr, value in (
        ("GIDiffuseSamples", 2),
        ("GISpecularSamples", 2),
        ("GITransmissionSamples", 2),
        ("GIVolumeSamples", 1),
    ):
        if cmds.objExists("defaultArnoldRenderOptions." + attr):
            cmds.setAttr("defaultArnoldRenderOptions." + attr, value)
    cmds.arnoldRender(camera=camera_shape, width=width, height=height)
    cmds.renderWindowEditor("renderView", edit=True, writeImage=path)


def run():
    with open(STATUS, "w") as handle:
        handle.write("START\n")
    cmds.file(new=True, force=True)
    if PROJECT not in sys.path:
        sys.path.insert(0, PROJECT)
    import tunnel_cavern
    importlib.reload(tunnel_cavern)

    started = time.time()
    tunnel_cavern.build(seed=20260723, density=32, fog_density=.0025)
    status("BUILT {:.3f}s".format(time.time() - started))

    camera_shape = (
        cmds.ls("CCV10_tunnel_camShape*", type="camera") or [None]
    )[0]
    if not camera_shape:
        raise RuntimeError("Generated camera missing")
    for shape in cmds.ls(type="camera") or []:
        cmds.setAttr(shape + ".renderable", int(shape == camera_shape))
    cmds.setAttr("defaultArnoldDriver.aiTranslator", "png", type="string")

    render(camera_shape, 450, 1280, 720, 3, HERO)
    status("HERO {}".format(HERO))
    render(camera_shape, 510, 960, 540, 3, ORBIT)
    status("ORBIT {}".format(ORBIT))

    cmds.file(rename=SCENE)
    cmds.file(save=True, type="mayaAscii", force=True)
    status("SCENE {}".format(SCENE))
    status("OK")


try:
    run()
except Exception:
    status("ERROR\n" + traceback.format_exc())
    raise
