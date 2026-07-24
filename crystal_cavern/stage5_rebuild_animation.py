"""Rebuild the collision-safe v21 animation scene without an Arnold render."""
from __future__ import print_function

import importlib
import os
import sys
import time
import traceback

import maya.cmds as cmds


PROJECT = "/Users/xixi/大学/未来创新设计/crystal_cavern"
OUT = os.path.join(PROJECT, "renders", "tunnel_v10")
SCENE = os.path.join(OUT, "crystal_cavern_final_v26_animation.ma")
STATUS = "/tmp/ccv_stage5_rebuild_v26_status.txt"


def status(message):
    with open(STATUS, "a") as handle:
        handle.write(message + "\n")


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
    cmds.file(rename=SCENE)
    cmds.file(save=True, type="mayaAscii", force=True)
    status("SCENE {}".format(SCENE))
    status("OK")


try:
    run()
except Exception:
    status("ERROR\n" + traceback.format_exc())
    raise
