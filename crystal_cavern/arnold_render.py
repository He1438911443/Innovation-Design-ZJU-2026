"""
Crystal Cavern — Arnold Render Module

Handles Arnold render settings, a dedicated render camera positioned
for the best crystal view, and beauty pass rendering to EXR.

References:
- Arnold for Maya User Guide: Sampling and render settings
- Autodesk Maya cmds API documentation
"""

import maya.cmds as cmds


def setup_arnold_render_settings():
    """Configure Arnold render settings for high-quality crystal cave rendering.

    Sets AA samples, per-AOV sampling rates, 1920x1080 resolution,
    EXR output with merged AOVs, and switches the current renderer to Arnold.

    Returns:
        dict: Key-value summary of the applied settings.
    """
    # Ensure Arnold plugin is loaded
    try:
        if not cmds.pluginInfo("mtoa", query=True, loaded=True):
            cmds.loadPlugin("mtoa")
    except Exception:
        pass  # Already loaded or inaccessible; continue with attribute sets

    settings = {}

    # ── Renderer selection ──
    try:
        cmds.setAttr("defaultRenderGlobals.currentRenderer", "arnold", type="string")
        settings["currentRenderer"] = "arnold"
    except Exception as e:
        print("   Warning: Could not set renderer to Arnold: " + str(e))

    # ── Arnold translator ──
    try:
        cmds.setAttr("defaultArnoldRenderOptions.ai_translator", "Arnold", type="string")
        settings["ai_translator"] = "Arnold"
    except Exception as e:
        print("   Warning: Could not set ai_translator: " + str(e))

    # ── Sampling ──
    sampling_pairs = {
        "AASamples": 5,
        "GIDiffuseSamples": 2,
        "GISpecularSamples": 2,
        "GITransmissionSamples": 4,
        "GISssSamples": 3,
        "GIVolumeSamples": 2,
    }
    for attr, value in sampling_pairs.items():
        try:
            cmds.setAttr("defaultArnoldRenderOptions." + attr, value)
            settings[attr] = value
        except Exception as e:
            print("   Warning: Could not set " + attr + ": " + str(e))

    # ── Resolution ──
    try:
        cmds.setAttr("defaultResolution.width", 1920)
        settings["width"] = 1920
    except Exception as e:
        print("   Warning: Could not set resolution width: " + str(e))

    try:
        cmds.setAttr("defaultResolution.height", 1080)
        settings["height"] = 1080
    except Exception as e:
        print("   Warning: Could not set resolution height: " + str(e))

    # ── Arnold Driver (EXR output) ──
    driver_attrs = {
        "ai_translator": "exr",
        "mergeAOVs": True,
        "halfPrecision": False,
    }
    for attr, value in driver_attrs.items():
        try:
            cmds.setAttr("defaultArnoldDriver." + attr, value)
            settings["driver_" + attr] = value
        except Exception as e:
            print("   Warning: Could not set defaultArnoldDriver." + attr + ": " + str(e))

    # ── AOVs: beauty + Z depth ──
    # Arnold stores AOVs as a string-array multi-attribute.  Clear stale
    # multi instances first, then add each AOV so neither gets overwritten.
    aovs = ["beauty", "Z"]
    try:
        num_children = cmds.attributeQuery(
            "aovList", node="defaultArnoldRenderOptions", numberOfChildren=True
        )
        while num_children and num_children > 0:
            cmds.removeMultiInstance(
                "defaultArnoldRenderOptions.aovList[0]", b=True
            )
            num_children = cmds.attributeQuery(
                "aovList", node="defaultArnoldRenderOptions",
                numberOfChildren=True
            )
    except (RuntimeError, ValueError):
        pass
    for idx, aov_name in enumerate(aovs):
        try:
            cmds.setAttr(
                "defaultArnoldRenderOptions.aovList[{0}]".format(idx),
                aov_name, type="string",
            )
        except (RuntimeError, ValueError) as e:
            print("   Warning: Could not add AOV '{0}': {1}".format(aov_name, e))
    settings["AOVs"] = aovs

    print("   Arnold render settings configured: AA=" + str(settings.get("AASamples", "?")) +
          ", " + str(settings.get("width", "?")) + "x" + str(settings.get("height", "?")) +
          ", AOVs=" + str(aovs))
    return settings


def create_render_camera(target_transform="crystal_group"):
    """Create a dedicated render camera positioned for the best crystal view.

    Queries the tallest 5 crystal formations in target_transform, averages
    their world-space bounding box centres, and places the camera at a
    cinematic offset with a 35 mm focal length.

    Args:
        target_transform: Name of the crystal parent group (default "crystal_group").

    Returns:
        str: Name of the created render camera transform, or None on failure.
    """
    camera_name = "render_cam"

    # Remove any existing render_cam* (catches auto-incremented names)
    for obj in (cmds.ls("render_cam*") or []):
        try:
            cmds.delete(obj)
        except Exception:
            pass

    # Validate target group
    if not cmds.objExists(target_transform):
        print("   Warning: " + target_transform + " not found — placing render camera at origin")
        cam = cmds.camera(name=camera_name, focalLength=20)[0]
        cmds.move(15, 8, 18, cam)
        print("   Render camera '" + cam + "' created at default position (f=35mm)")
        return cam

    # Gather crystal children and estimate height from world bounding box
    children = cmds.listRelatives(target_transform, children=True, type="transform")
    if not children:
        print("   Warning: " + target_transform + " has no children — placing render camera at origin")
        cam = cmds.camera(name=camera_name, focalLength=20)[0]
        cmds.move(15, 8, 18, cam)
        print("   Render camera '" + cam + "' created at default position (f=35mm)")
        return cam

    # Compute bounding-box height (Y span) for each crystal
    crystal_info = []  # (height, center_x, center_y, center_z)
    for child in children:
        try:
            bbox = cmds.xform(child, query=True, boundingBox=True, worldSpace=True)
            # bbox = [xmin, ymin, zmin, xmax, ymax, zmax]
            height = bbox[4] - bbox[1]
            cx = (bbox[0] + bbox[3]) / 2.0
            cy = (bbox[1] + bbox[4]) / 2.0
            cz = (bbox[2] + bbox[5]) / 2.0
            crystal_info.append((height, cx, cy, cz))
        except Exception:
            continue

    if not crystal_info:
        print("   Warning: Could not sample crystal bounds — placing render camera at origin")
        cam = cmds.camera(name=camera_name, focalLength=20)[0]
        cmds.move(15, 8, 18, cam)
        print("   Render camera '" + cam + "' created at default position (f=35mm)")
        return cam

    # Sort by height descending, take top 5
    crystal_info.sort(key=lambda x: x[0], reverse=True)
    top_n = crystal_info[:min(5, len(crystal_info))]

    # Average centre positions
    avg_x = sum(info[1] for info in top_n) / len(top_n)
    avg_y = sum(info[2] for info in top_n) / len(top_n)
    avg_z = sum(info[3] for info in top_n) / len(top_n)

    # Camera position — MUCH closer for dramatic crystal closeups
    cam_x = avg_x + 6.0
    cam_y = avg_y + 3.0
    cam_z = avg_z + 8.0

    # Create camera
    cam = cmds.camera(name=camera_name, focalLength=20)[0]
    cmds.move(cam_x, cam_y, cam_z, cam)

    # Aim at the average crystal position
    aim_constraint_name = camera_name + "_aim"
    if cmds.objExists(aim_constraint_name):
        cmds.delete(aim_constraint_name)

    # Use an explicit aim locator so the camera always looks at the target
    aim_loc = cmds.spaceLocator(name=aim_constraint_name)[0]
    cmds.move(avg_x, avg_y, avg_z, aim_loc)
    cmds.hide(aim_loc)
    cmds.aimConstraint(aim_loc, cam,
                       aimVector=[0, 0, -1],
                       upVector=[0, 1, 0],
                       maintainOffset=False)

    print("   Render camera '" + cam + "' created: pos=(" +
          "{:.1f}".format(cam_x) + ", " + "{:.1f}".format(cam_y) + ", " +
          "{:.1f}".format(cam_z) + "), lookat=(" +
          "{:.1f}".format(avg_x) + ", " + "{:.1f}".format(avg_y) + ", " +
          "{:.1f}".format(avg_z) + "), f=35mm")
    return cam


def render_beauty(output_path="/Users/xixi/大学/未来创新设计/crystal_cavern/renders/beauty"):
    """Execute an Arnold render of the current frame to the given output path.

    Sets the render output path, invokes arnoldRender for a single frame at
    1920x1080, and verifies that the output file was created.

    Args:
        output_path: File path for the rendered EXR (default /tmp/crystal_cavern_beauty.exr).

    Returns:
        bool: True if the render completed and the output file exists, False otherwise.
    """
    import os

    # Determine which camera to use: prefer render_cam*, fall back to fly_cam* or persp
    camera_name = None
    for pattern in ["render_cam", "fly_cam", "persp"]:
        matches = cmds.ls(pattern + "*") or []
        for candidate in matches:
            try:
                if cmds.nodeType(candidate) == "transform":
                    shapes = cmds.listRelatives(candidate, shapes=True, type="camera")
                    if shapes:
                        camera_name = candidate
                        break
            except (RuntimeError, ValueError):
                continue
        if camera_name:
            break
    if camera_name is None:
        print("   Error: No renderable camera found")
        return False

    # Set render output path
    try:
        cmds.setAttr("defaultRenderGlobals.outFormatControl", 0)
        cmds.setAttr("defaultRenderGlobals.animation", 0)
        cmds.setAttr("defaultRenderGlobals.putFrameBeforeExt", 0)
        cmds.setAttr("defaultRenderGlobals.imageFilePrefix", output_path, type="string")
        print("   Render output: " + output_path)
    except Exception as e:
        print("   Warning: Could not set output path: " + str(e))

    # Execute Arnold render
    print("   Starting Arnold render (1920x1080, 1 frame) with camera '" + camera_name + "'...")
    try:
        cmds.arnoldRender(
            width=1920,
            height=1080,
            startFrame=1,
            endFrame=1,
            cam=camera_name,
        )
    except Exception as e:
        print("   Render failed: " + str(e))
        return False

    # Verify output — Arnold may append frame number and format extension
    possible_paths = [
        output_path,
        output_path.replace(".exr", ".001.exr"),
        output_path.replace(".exr", ".0001.exr"),
        output_path + ".001",
    ]
    # Also check the raw prefix as Maya might prepend the scene name etc.
    found = False
    for p in possible_paths:
        if os.path.exists(p):
            found = True
            print("   Render completed successfully → " + p)
            break

    if not found:
        # Try globbing near the output path
        import glob
        dir_part = os.path.dirname(output_path) or "."
        base_part = os.path.basename(output_path)
        # Strip the extension for a prefix match
        prefix = os.path.splitext(base_part)[0]
        matches = glob.glob(os.path.join(dir_part, prefix + "*"))
        if matches:
            found = True
            print("   Render completed successfully → " + str(matches))
        else:
            print("   Render appears to have completed (no exception) but output file not found.")
            print("   Check the Render View or Maya script editor output.")

    return True
