"""Fixed camera rig — spiral around crystals with direct rotation keyframes.
Injected to replace cave_lighting.create_camera_rig when building scenes.
Works with ANY crystal naming scheme (CCV9_*, crystal_group, etc)."""
import maya.cmds as cmds
import math


def create_camera_rig(terrain_name="cave_terrain", crystal_group="crystal_group"):
    # Clean old camera
    for obj in (cmds.ls("fly_cam*") or []):
        try: cmds.delete(obj)
        except: pass
    for curve in (cmds.ls(type="animCurve") or []):
        n = str(curve)
        if "fly_cam" in n:
            try: cmds.delete(curve)
            except: pass

    # Query crystal positions via bounding box (universal)
    crystal_positions = []
    for grp in [crystal_group, "CCV9_crystals", "crystal_group"]:
        if cmds.objExists(grp):
            children = cmds.listRelatives(grp, children=True, type="transform") or []
            for ch in children:
                try:
                    pos = cmds.xform(ch, q=True, t=True, ws=True)
                    bb = cmds.xform(ch, q=True, bb=True, ws=True)
                    h = bb[4] - bb[1]
                    if h > 0.3:
                        crystal_positions.append((pos, h))
                except: pass
            if crystal_positions:
                break

    crystal_positions.sort(key=lambda x: x[1], reverse=True)

    if crystal_positions:
        tallest = crystal_positions[:min(len(crystal_positions), 15)]
        cx = sum(p[0][0] for p in tallest) / len(tallest)
        cy = sum(p[0][1] for p in tallest) / len(tallest)
        cz = sum(p[0][2] for p in tallest) / len(tallest)
    else:
        cx, cy, cz = 0, -3, 0

    print("   Camera fix: %d crystals, center (%.1f, %.1f, %.1f)" %
          (len(crystal_positions), cx, cy, cz))

    cam = cmds.camera(name="fly_cam", focalLength=24)[0]
    radius = 14

    for i in range(10):
        frame = i * 106
        t = frame / 960.0
        angle = t * math.pi * 2.2
        r = radius * (0.7 + 0.3 * math.sin(t * math.pi * 3))
        cam_y = cy - 2 + 1.5 * math.sin(t * math.pi * 2)
        cam_y = max(-6, min(cam_y, 4))
        cam_x = cx + r * math.cos(angle)
        cam_z = cz + r * math.sin(angle)

        cmds.setKeyframe(cam + ".translateX", value=cam_x, time=frame)
        cmds.setKeyframe(cam + ".translateY", value=cam_y, time=frame)
        cmds.setKeyframe(cam + ".translateZ", value=cam_z, time=frame)

        # Direct look-at rotation
        dx, dy, dz = cx - cam_x, cy - cam_y, cz - cam_z
        ry = math.degrees(math.atan2(dx, dz))
        horiz = math.sqrt(dx*dx + dz*dz)
        rx = -math.degrees(math.atan2(dy, horiz)) if horiz > 0.01 else 0
        cmds.setKeyframe(cam + ".rotateX", value=rx, time=frame)
        cmds.setKeyframe(cam + ".rotateY", value=ry, time=frame)
        cmds.setKeyframe(cam + ".rotateZ", value=0, time=frame)

    try:
        cmds.select(cam)
        cmds.keyTangent(inTangentType="spline", outTangentType="spline")
    except: pass

    cmds.playbackOptions(min=0, max=960, animationStartTime=0, animationEndTime=960)
    print("   Camera fix applied: spiral fly-through, 960f, f=24mm")
    return cam
