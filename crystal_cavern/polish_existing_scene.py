"""First non-destructive polish pass for the existing Crystal Cavern scene.

Run inside Maya's Python Script Editor while the existing ``hanqian_v3`` scene
is open.  It does not rebuild terrain, crystals, materials, or growth keys.
Instead it adds a collision-safe hero camera, keeps the previous camera intact,
and saves the result as a new scene under ``renders/hanqian_v3_polished``.
"""

from __future__ import print_function

import math
import os

import maya.cmds as cmds


OUT_DIR = "/Users/xixi/大学/未来创新设计/crystal_cavern/renders/hanqian_v3_polished"
OUT_SCENE = os.path.join(OUT_DIR, "crystal_cavern_polished_v1.ma")


def _aim_rotation(eye, target):
    """Return Maya camera Euler rotation for a camera looking down local -Z."""
    dx, dy, dz = target[0] - eye[0], target[1] - eye[1], target[2] - eye[2]
    horizontal = max(math.sqrt(dx * dx + dz * dz), 0.0001)
    return (
        -math.degrees(math.atan2(dy, horizontal)),
        math.degrees(math.atan2(dx, dz)),
        0.0,
    )


def _crystal_centre():
    """Get a robust median centre from existing CCV9 crystal clusters."""
    root = "CCV9_crystals"
    clusters = cmds.listRelatives(root, children=True, type="transform") or []
    samples = []
    for cluster in clusters:
        try:
            box = cmds.exactWorldBoundingBox(cluster)
            samples.append(((box[0] + box[3]) * 0.5,
                            (box[1] + box[4]) * 0.5,
                            (box[2] + box[5]) * 0.5))
        except RuntimeError:
            pass
    if not samples:
        return (0.0, 0.0, 0.0), 14.0

    # Median prevents one oversized branch from pulling the camera into it.
    xs, ys, zs = (sorted(p[i] for p in samples) for i in range(3))
    middle = len(samples) // 2
    centre = (xs[middle], ys[middle], zs[middle])
    radii = [math.sqrt((p[0] - centre[0]) ** 2 + (p[2] - centre[2]) ** 2)
             for p in samples]
    radii.sort()
    # Camera stays inside the cave, but at least 7m off the crystal cluster.
    radius = max(16.0, min(22.0, radii[int(len(radii) * 0.85)] + 7.0))
    return centre, radius


def apply_polish():
    if not cmds.objExists("CCV9_crystals"):
        raise RuntimeError("Expected CCV9_crystals in the open scene; no changes made.")

    os.makedirs(OUT_DIR, exist_ok=True)
    centre, radius = _crystal_centre()

    # Preserve every existing camera.  Re-running only replaces this polish rig.
    for node in ((cmds.ls("CCV10_polish_cam*") or []) +
                 (cmds.ls("CCV10_polish_lookat*") or [])):
        try:
            cmds.delete(node)
        except RuntimeError:
            pass

    cam = cmds.camera(name="CCV10_polish_cam", focalLength=32.0)[0]
    lookat = cmds.spaceLocator(name="CCV10_polish_lookat")[0]
    cmds.hide(lookat)
    shape = cmds.listRelatives(cam, shapes=True, type="camera")[0]
    cmds.setAttr(shape + ".renderable", 1)
    cmds.setAttr(shape + ".nearClipPlane", 0.5)
    cmds.setAttr(shape + ".farClipPlane", 1000.0)
    try:
        cmds.setAttr(shape + ".depthOfField", 0)  # validate composition first
        cmds.setAttr(shape + ".ai_exposure", 0.0)
    except RuntimeError:
        pass

    # Six slow, external orbit keys: no camera position lies inside the
    # cluster's 85th-percentile radius.  The frame range deliberately begins
    # after the growth reveal so the presentation does not open on empty space.
    orbit = [
        (960,  -0.20, 0.22,  1.7),
        (1080,  0.15, 0.12,  1.2),
        (1200,  0.48, 0.04,  0.8),
        (1320,  0.78, 0.16,  0.4),
        (1440,  1.10, 0.10, -0.1),
        (1560,  1.42, 0.24, -0.6),
    ]
    for frame, angle, y_offset, target_bias in orbit:
        eye = (
            centre[0] + math.cos(angle) * radius,
            centre[1] + 3.5 + y_offset * 5.0,
            centre[2] + math.sin(angle) * radius,
        )
        look_target = (
            centre[0] + math.cos(angle + 0.9) * target_bias,
            centre[1] + 1.8,
            centre[2] + math.sin(angle + 0.9) * target_bias,
        )
        for attr, value in zip(("translateX", "translateY", "translateZ"), eye):
            cmds.setKeyframe(cam, attribute=attr, value=value, time=frame)
        for attr, value in zip(("translateX", "translateY", "translateZ"), look_target):
            cmds.setKeyframe(lookat, attribute=attr, value=value, time=frame)

    # Aim constraints are much more reliable than manually derived Euler
    # angles: Maya's local camera -Z convention is easy to invert, and the
    # resulting error was making the camera gaze at the cave ceiling.
    cmds.aimConstraint(lookat, cam, aimVector=(0, 0, -1),
                       upVector=(0, 1, 0), worldUpType="vector",
                       worldUpVector=(0, 1, 0),
                       name="CCV10_polish_aim")

    cmds.select([cam, lookat])
    cmds.keyTangent(inTangentType="spline", outTangentType="spline")

    # Keep the original long growth keys intact, but make the delivery window
    # a focused 25-second fly-through rather than an 80-second empty lead-in.
    cmds.playbackOptions(min=960, max=1560, animationStartTime=960,
                         animationEndTime=1560)
    cmds.currentTime(1320)

    cmds.file(rename=OUT_SCENE)
    cmds.file(save=True, type="mayaAscii", force=True)
    print("CCV10 polish rig saved: {}".format(OUT_SCENE))
    print("Centre: ({:.2f}, {:.2f}, {:.2f}), safe orbit radius: {:.2f}".format(
        centre[0], centre[1], centre[2], radius))
    return cam


if __name__ == "__main__":
    apply_polish()
