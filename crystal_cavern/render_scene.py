"""Paste into Maya Script Editor (Python tab) -> Ctrl+Enter to render."""
import maya.cmds as cmds, maya.mel as mel, os

out = "/Users/xixi/大学/未来创新设计/crystal_cavern/renders/final_v4"
os.makedirs(out, exist_ok=True)
out_path = out + "/arnold_render"

# Find render camera
cam = None
for p in ['render_cam', 'fly_cam', 'persp']:
    for o in (cmds.ls(p + '*') or []):
        try:
            if cmds.nodeType(o) == 'transform':
                if cmds.listRelatives(o, shapes=True, type='camera'):
                    cam = o; break
        except:
            continue
    if cam: break

# Enable renderable
for c in cmds.ls(type='camera'):
    try: cmds.setAttr(c + '.renderable', True)
    except: pass

# Remove aim constraints (interfere with batch render)
for ac in (cmds.ls(type='aimConstraint') or []):
    try: cmds.delete(ac)
    except: pass

# Set output
cmds.setAttr('defaultRenderGlobals.imageFilePrefix', out_path, type='string')
cmds.setAttr('defaultRenderGlobals.outFormatControl', 0)
cmds.setAttr('defaultRenderGlobals.animation', 0)
cmds.setAttr('defaultRenderGlobals.putFrameBeforeExt', 0)

print("Rendering with camera: " + cam)
print("Output: " + out_path)
print("This will take 3-8 minutes for 1920x1080 Arnold render...")

mel.eval('arnoldRender -batch -camera ' + cam)

print("DONE! Check: " + out)
print("File: " + out_path + ".exr")
