"""Render fast fly-through checkpoints from the current clean scene."""
from __future__ import print_function

import os
import traceback

import maya.cmds as cmds


OUT = "/Users/xixi/大学/未来创新设计/crystal_cavern/renders/tunnel_v10"
STATUS = "/tmp/ccv_stage4_keyframes_status.txt"
FRAMES = (510,)


def run():
    camera_shape = (
        cmds.ls("CCV10_tunnel_camShape*", type="camera") or [None]
    )[0]
    if not camera_shape:
        raise RuntimeError("Generated camera missing")
    # Apply the v19 corrected final chamber pose to the current v18 scene so it
    # can be checked without another full rebuild.
    camera = (cmds.listRelatives(camera_shape, parent=True) or
              [camera_shape])[0]
    look = (cmds.ls("CCV10_tunnel_lookat*",
                    type="transform") or [None])[0]
    chamber = (-3.634726040103702, -3.519265956723606, 7.0)
    position = (chamber[0] + 8.0, chamber[1] - .5, chamber[2])
    target = (chamber[0] + .20, chamber[1] - 3.0, chamber[2] + 1.0)
    for attr, value in zip(("translateX", "translateY", "translateZ"),
                           position):
        cmds.setKeyframe(camera, at=attr, t=510, v=value)
    for attr, value in zip(("translateX", "translateY", "translateZ"),
                           target):
        cmds.setKeyframe(look, at=attr, t=510, v=value)
    cmds.setKeyframe(camera_shape, at="focalLength", t=510, v=34)
    cmds.setAttr("defaultArnoldRenderOptions.AASamples", 1)
    for attr in ("GIDiffuseSamples", "GISpecularSamples",
                 "GITransmissionSamples", "GIVolumeSamples"):
        if cmds.objExists("defaultArnoldRenderOptions." + attr):
            cmds.setAttr("defaultArnoldRenderOptions." + attr, 1)
    rendered = []
    for frame in FRAMES:
        cmds.currentTime(frame)
        path = os.path.join(
            OUT, "stage4_v19_flythrough_frame{:03d}.png".format(frame)
        )
        cmds.arnoldRender(camera=camera_shape, width=480, height=270)
        cmds.renderWindowEditor("renderView", edit=True, writeImage=path)
        rendered.append(path)
    with open(STATUS, "w") as handle:
        handle.write("OK\n" + "\n".join(rendered))


try:
    run()
except Exception:
    with open(STATUS, "w") as handle:
        handle.write("ERROR\n" + traceback.format_exc())
    raise
