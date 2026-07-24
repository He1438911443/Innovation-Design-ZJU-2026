"""Second non-destructive polish pass: mineral material and cinematic light.

Run with the existing ``crystal_cavern_polished_v1.ma`` open.  This preserves
all geometry and animation and writes a new v2 Maya ASCII scene.  The pass is
deliberately restrained: it replaces uniform neon emission with transmission,
controlled highlights and only four local mineral accents.
"""

from __future__ import print_function

import os

import maya.cmds as cmds


OUT_DIR = "/Users/xixi/大学/未来创新设计/crystal_cavern/renders/hanqian_v3_polished"
OUT_SCENE = os.path.join(OUT_DIR, "crystal_cavern_polished_v2_realism.ma")


# Muted, physically plausible mineral families.  They retain a small amount
# of fantasy colour for the course north-star, but read as coloured quartz
# under light rather than as painted plastic.
MINERAL_COLOURS = {
    "amethyst": (0.28, 0.13, 0.42),
    "aquamarine": (0.20, 0.48, 0.62),
    "citrine": (0.52, 0.37, 0.15),
    "emerald": (0.18, 0.40, 0.30),
    "fluorite": (0.24, 0.35, 0.34),
    "rose_quartz": (0.50, 0.34, 0.40),
    "ruby": (0.38, 0.08, 0.13),
    "sapphire": (0.10, 0.18, 0.42),
    "selenite": (0.62, 0.72, 0.80),
    "topaz": (0.56, 0.39, 0.15),
}


def _set(node, attr, value, colour=False):
    """Set an Arnold/Maya attribute when that version exposes it."""
    try:
        if colour:
            cmds.setAttr(node + "." + attr, value[0], value[1], value[2],
                         type="double3")
        else:
            cmds.setAttr(node + "." + attr, value)
    except (RuntimeError, ValueError):
        pass


def _mineral_key(shader):
    name = shader.lower().replace("ccv9_", "").replace("_gem", "")
    return name if name in MINERAL_COLOURS else None


def tune_crystal_materials():
    tuned = []
    for shader in cmds.ls(type="aiStandardSurface") or []:
        key = _mineral_key(shader)
        if not key:
            continue
        colour = MINERAL_COLOURS[key]

        # The important change: light now travels *through* a coloured volume.
        # A low base retains clean specular facets and stops solid body colour
        # from overwhelming the cave.
        _set(shader, "base", 0.28)
        _set(shader, "baseColor", colour, colour=True)
        _set(shader, "specular", 1.0)
        _set(shader, "specularRoughness", 0.105)
        _set(shader, "specularIOR", 1.54)
        _set(shader, "specularColor", (1.0, 0.98, 0.96), colour=True)
        _set(shader, "transmission", 0.82)
        _set(shader, "transmissionColor", colour, colour=True)
        _set(shader, "transmissionDepth", 7.0)
        _set(shader, "transmissionScatter", 0.06)
        _set(shader, "subsurface", 0.12)
        _set(shader, "subsurfaceColor", colour, colour=True)
        _set(shader, "subsurfaceScale", 0.7)
        _set(shader, "coat", 0.08)
        _set(shader, "coatRoughness", 0.06)

        # Emission is now a trace internal glint, not the primary light source.
        _set(shader, "emission", 0.12)
        _set(shader, "emissionColor", colour, colour=True)
        tuned.append(shader)
    return tuned


def _light_shape(name):
    found = cmds.ls(name, type=["pointLight", "directionalLight", "areaLight"]) or []
    return found[0] if found else None


def tune_lighting():
    # Twenty non-decaying coloured fills erase shadow and make the old render
    # look game-like.  Remove only that generated family; no cave geometry or
    # animation is touched.
    for shape in cmds.ls("CCV9_glow_*", type="pointLight") or []:
        parent = (cmds.listRelatives(shape, parent=True) or [shape])[0]
        try:
            cmds.delete(parent)
        except RuntimeError:
            pass

    ambient = cmds.ls("CCV9_ambient", type="ambientLight") or []
    if ambient:
        _set(ambient[0], "intensity", 0.035)
        _set(ambient[0], "color", (0.018, 0.022, 0.045), colour=True)

    entrance = _light_shape("CCV9_entrance_keyShape")
    if entrance:
        _set(entrance, "intensity", 18.0)
        _set(entrance, "color", (0.92, 0.75, 0.48), colour=True)

    rim = _light_shape("CCV9_blue_rimShape")
    if rim:
        _set(rim, "intensity", 7.0)
        _set(rim, "color", (0.25, 0.48, 0.88), colour=True)

    # Four falloff lights create isolated pools of mineral light.  Their
    # locations use the existing cave's actual crystal distribution.
    accents = [
        ("CCV11_ice_hero", (4.9, 5.0, 10.5), (0.38, 0.72, 1.0), 12000.0),
        ("CCV11_deep_violet", (-13.0, 3.5, -10.5), (0.45, 0.20, 0.82), 6500.0),
        ("CCV11_cave_depth", (0.9, 2.8, -12.0), (0.66, 0.78, 1.0), 10000.0),
        ("CCV11_warm_counter", (6.1, 2.2, 11.6), (1.0, 0.52, 0.20), 3800.0),
    ]
    for name, pos, colour, intensity in accents:
        old = cmds.ls(name + "*") or []
        if old:
            try:
                cmds.delete(old)
            except RuntimeError:
                pass
        shape = cmds.shadingNode("pointLight", asLight=True, name=name)
        transform = (cmds.listRelatives(shape, parent=True) or [shape])[0]
        cmds.xform(transform, worldSpace=True, translation=pos)
        _set(shape, "color", colour, colour=True)
        _set(shape, "intensity", intensity)
        _set(shape, "decayRate", 2)

    # An unused white area light flattens the whole cave when enabled.
    for area in cmds.ls("aiAreaLight*", type="aiAreaLight") or []:
        _set(area, "intensity", 0.0)


def apply_realism_pass():
    if not cmds.objExists("CCV9_crystals"):
        raise RuntimeError("Expected CCV9_crystals; no changes made.")
    os.makedirs(OUT_DIR, exist_ok=True)
    tuned = tune_crystal_materials()
    tune_lighting()

    # The v1 camera stays intact.  Keep a modest filmic exposure so bright
    # facet reflections survive instead of clipping into white blocks.
    for camera in cmds.ls(type="camera") or []:
        if camera.startswith("CCV10_polish_cam"):
            _set(camera, "ai_exposure", -0.35)

    cmds.file(rename=OUT_SCENE)
    cmds.file(save=True, type="mayaAscii", force=True)
    print("CCV11 realism pass saved: {}".format(OUT_SCENE))
    print("Mineral shaders tuned: {}; generated glow lights reduced to 4.".format(
        len(tuned)))
    return OUT_SCENE


if __name__ == "__main__":
    apply_realism_pass()
