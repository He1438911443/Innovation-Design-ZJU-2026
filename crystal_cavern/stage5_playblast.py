"""Create the final camera fly-through preview from the generated v20 scene."""
from __future__ import print_function

import os
import traceback

import maya.cmds as cmds


PROJECT = "/Users/xixi/大学/未来创新设计/crystal_cavern"
OUT = os.path.join(PROJECT, "renders", "tunnel_v10")
MOVIE = os.path.join(OUT, "crystal_cavern_growth_flythrough_FINAL_v26.mov")
STATUS = "/tmp/ccv_stage5_playblast_v26_status.txt"


def status(message):
    with open(STATUS, "a") as handle:
        handle.write(message + "\n")


def run():
    with open(STATUS, "w") as handle:
        handle.write("START\n")

    camera = (cmds.ls("CCV10_tunnel_cam*", type="transform") or [None])[0]
    if not camera:
        raise RuntimeError("Generated camera missing")

    # Arnold sees these meshes through refractive outer shells. Viewport 2.0
    # does not reproduce the same transmission depth and shows them as opaque
    # rectangles, so hide only the internal-detail proxies for the playblast.
    internal_nodes = (
        (cmds.ls("CCV10_*_fracture_*", type="transform") or []) +
        (cmds.ls("CCV10_*_inclusion*", type="transform") or [])
    )
    for node in internal_nodes:
        cmds.setAttr(node + ".visibility", 0)
    status("HIDDEN_INTERNAL {}".format(len(internal_nodes)))

    panel = cmds.getPanel(withFocus=True)
    if not panel or cmds.getPanel(typeOf=panel) != "modelPanel":
        panel = (cmds.getPanel(type="modelPanel") or [None])[0]
    if not panel:
        raise RuntimeError("No model panel available")

    cmds.lookThru(panel, camera)
    cmds.modelEditor(
        panel, edit=True,
        displayAppearance="smoothShaded",
        displayTextures=True,
        displayLights="all",
        shadows=True,
        grid=False,
        hud=False,
    )
    cmds.currentUnit(time="film")
    cmds.playbackOptions(minTime=390, maxTime=525, animationStartTime=390,
                         animationEndTime=525)

    result = cmds.playblast(
        startTime=390,
        endTime=525,
        format="qt",
        filename=MOVIE,
        compression="H.264",
        quality=88,
        widthHeight=(1280, 720),
        percent=100,
        viewer=False,
        showOrnaments=False,
        offScreen=True,
        forceOverwrite=True,
    )
    status("MOVIE {}".format(result))
    status("OK")


try:
    run()
except Exception:
    status("ERROR\n" + traceback.format_exc())
    raise
