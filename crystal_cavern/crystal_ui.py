"""
Crystal Cavern — Procedural Crystal Cave Generator
Module 5: Maya GUI Parameter Panel (v2)

Provides a tabbed user interface for controlling all crystal generation,
lighting, and rendering parameters.
"""

import maya.cmds as cmds

WINDOW_NAME = "crystalCavernUI_v2"
TAB_LAYOUT = "cc_tabs"


# ---------------------------------------------------------------------------
#  UI construction
# ---------------------------------------------------------------------------

def create_ui():
    """Build the Crystal Cavern v2 parameter control panel."""
    if cmds.window(WINDOW_NAME, exists=True):
        cmds.deleteUI(WINDOW_NAME)

    window = cmds.window(
        WINDOW_NAME,
        title="Crystal Cavern v2",
        widthHeight=(380, 560),
        sizeable=True,
    )

    # Keep every control inside a single root layout.  A tabLayout cannot
    # accept arbitrary siblings directly, so the bottom action row must be
    # parented to this column rather than to the window after the tabs.
    root = cmds.columnLayout(adjustableColumn=True)

    # ── Logo / Branding ────────────────────────────────────────────────
    cmds.text(label="◆ Crystal Cavern v10 ◆", font="boldLabelFont",
              height=24, align="center")
    cmds.text(label="Python-Driven Procedural Cave Generator",
              font="smallPlainLabelFont", height=16, align="center")
    cmds.separator(height=8, style="in")

    # ── Tab layout ──────────────────────────────────────────────────────
    tabs = cmds.tabLayout(TAB_LAYOUT, innerMarginWidth=6, innerMarginHeight=6)

    # ── Tab 1: Terrain ──────────────────────────────────────────────────
    _build_terrain_tab(tabs)

    # ── Tab 2: Crystals ─────────────────────────────────────────────────
    _build_crystals_tab(tabs)

    # ── Tab 3: Lighting ─────────────────────────────────────────────────
    _build_lighting_tab(tabs)

    # ── Tab 4: Render ───────────────────────────────────────────────────
    _build_render_tab(tabs)

    cmds.setParent(root)

    # ── Separator ───────────────────────────────────────────────────────
    cmds.separator(height=10, style="in")

    # ── Bottom buttons ──────────────────────────────────────────────────
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(124, 124, 124))
    cmds.button(
        label="Generate",
        backgroundColor=(0.3, 0.5, 0.3),
        command=lambda *_: generate_from_ui(),
    )
    cmds.button(
        label="Reset Scene",
        backgroundColor=(0.5, 0.3, 0.3),
        command=lambda *_: reset_scene(),
    )
    cmds.button(
        label="Close",
        command=lambda *_: cmds.deleteUI(WINDOW_NAME),
    )
    cmds.setParent(root)

    cmds.showWindow(window)


def _build_terrain_tab(tabs):
    """Populate the Terrain tab."""
    child = cmds.columnLayout(adjustableColumn=True, rowSpacing=4)
    cmds.intSliderGrp(
        "terrain_seed",
        label="Seed",
        field=True, minValue=1, maxValue=99999, value=2026,
    )
    cmds.floatSliderGrp(
        "terrain_roughness",
        label="Roughness",
        field=True, minValue=0.1, maxValue=0.8, value=0.45, step=0.01,
    )
    cmds.intSliderGrp(
        "terrain_size",
        label="Size",
        field=True, minValue=20, maxValue=80, value=40,
    )
    cmds.floatSliderGrp(
        "terrain_wall_height",
        label="Wall Height",
        field=True, minValue=5.0, maxValue=20.0, value=10.0,
    )
    cmds.floatSliderGrp(
        "terrain_ceiling_height",
        label="Ceiling Height",
        field=True, minValue=4.0, maxValue=15.0, value=8.0,
    )
    cmds.setParent("..")
    cmds.tabLayout(tabs, edit=True, tabLabel=(child, "Terrain"))


def _build_crystals_tab(tabs):
    """Populate the Crystals tab."""
    child = cmds.columnLayout(adjustableColumn=True, rowSpacing=4)
    cmds.floatSliderGrp(
        "crystal_density",
        label="Density",
        field=True, minValue=0.5, maxValue=4.0, value=2.0, step=0.1,
    )
    cmds.floatSliderGrp(
        "crystal_variance",
        label="Size Variance",
        field=True, minValue=0.3, maxValue=2.0, value=1.0, step=0.1,
    )
    cmds.intSliderGrp(
        "crystal_color_seed",
        label="Color Seed",
        field=True, minValue=1, maxValue=99999, value=42,
    )
    cmds.optionMenuGrp(
        "crystal_type_mix",
        label="Type Mix",
        columnAlign=(1, "left"), columnWidth=(1, 100),
    )
    for opt in ["Mixed", "Mostly Spikes", "Mostly Clusters",
                 "Mostly Towers", "Mostly Prisms"]:
        cmds.menuItem(label=opt)
    cmds.setParent("..")
    cmds.tabLayout(tabs, edit=True, tabLabel=(child, "Crystals"))


def _build_lighting_tab(tabs):
    """Populate the Lighting tab."""
    child = cmds.columnLayout(adjustableColumn=True, rowSpacing=4)
    cmds.floatSliderGrp(
        "light_ambient",
        label="Ambient Intensity",
        field=True, minValue=0.02, maxValue=0.3, value=0.06, step=0.01,
    )
    cmds.floatSliderGrp(
        "light_fog",
        label="Fog Density",
        field=True, minValue=0.01, maxValue=0.3, value=0.06, step=0.01,
    )
    cmds.intSliderGrp(
        "light_dust",
        label="Dust Count",
        field=True, minValue=50, maxValue=500, value=250, step=10,
    )
    cmds.intSliderGrp(
        "light_crystal_lights",
        label="Crystal Lights",
        field=True, minValue=5, maxValue=30, value=20,
    )
    cmds.setParent("..")
    cmds.tabLayout(tabs, edit=True, tabLabel=(child, "Lighting"))


def _build_render_tab(tabs):
    """Populate the Render tab."""
    child = cmds.columnLayout(adjustableColumn=True, rowSpacing=4)
    cmds.intSliderGrp(
        "render_width",
        label="Resolution Width",
        field=True, minValue=640, maxValue=3840, value=1920, step=10,
    )
    cmds.intSliderGrp(
        "render_height",
        label="Resolution Height",
        field=True, minValue=360, maxValue=2160, value=1080, step=10,
    )
    cmds.intSliderGrp(
        "render_aa",
        label="AA Samples",
        field=True, minValue=1, maxValue=10, value=5,
    )
    cmds.separator(height=6, style="none")
    cmds.button(
        label="Render Still",
        command=lambda *_: _render_still(),
    )
    cmds.setParent("..")
    cmds.tabLayout(tabs, edit=True, tabLabel=(child, "Render"))


def _render_still():
    """Confirm and then kick off an Arnold render."""
    confirmed = cmds.confirmDialog(
        title="Render Still",
        message="Start Arnold beauty render with current settings?",
        button=["Render", "Cancel"],
        defaultButton="Cancel",
        cancelButton="Cancel",
        dismissString="Cancel",
    )
    if confirmed != "Render":
        return
    try:
        import arnold_render
        arnold_render.render_beauty()
    except ImportError:
        cmds.warning("Could not import arnold_render module.")
    except Exception as e:
        cmds.warning(f"Render failed: {e}")


# ---------------------------------------------------------------------------
#  Core operations
# ---------------------------------------------------------------------------

def generate_from_ui():
    """Read all UI parameters and call final_scene.build() for one-click generation."""
    # ── Read all sliders ──────────────────────────────────────────────
    terrain_seed = cmds.intSliderGrp("terrain_seed", query=True, value=True)
    terrain_roughness = cmds.floatSliderGrp("terrain_roughness", query=True, value=True)
    terrain_size = cmds.intSliderGrp("terrain_size", query=True, value=True)
    wall_height = cmds.floatSliderGrp("terrain_wall_height", query=True, value=True)
    ceiling_height = cmds.floatSliderGrp("terrain_ceiling_height", query=True, value=True)

    crystal_density = cmds.floatSliderGrp("crystal_density", query=True, value=True)
    crystal_variance = cmds.floatSliderGrp("crystal_variance", query=True, value=True)
    crystal_color_seed = cmds.intSliderGrp("crystal_color_seed", query=True, value=True)
    type_mix = cmds.optionMenuGrp("crystal_type_mix", query=True, value=True)

    ambient_intensity = cmds.floatSliderGrp("light_ambient", query=True, value=True)
    fog_density = cmds.floatSliderGrp("light_fog", query=True, value=True)
    dust_count = cmds.intSliderGrp("light_dust", query=True, value=True)
    crystal_lights = cmds.intSliderGrp("light_crystal_lights", query=True, value=True)

    render_width = cmds.intSliderGrp("render_width", query=True, value=True)
    render_height = cmds.intSliderGrp("render_height", query=True, value=True)
    render_aa = cmds.intSliderGrp("render_aa", query=True, value=True)

    # ── Log ───────────────────────────────────────────────────────────
    print("=" * 55)
    print("  CRYSTAL CAVERN v10 — One-Click Generation")
    print("  seed={0}  density={1}  fog={2}  roughness={3}".format(
        terrain_seed, crystal_density, fog_density, terrain_roughness))
    print("=" * 55)

    # ── Ensure project is on path ─────────────────────────────────────
    import sys as _s, os as _o
    _dir = "/Users/xixi/大学/未来创新设计/crystal_cavern"
    if _dir not in _s.path:
        _s.path.insert(0, _dir)

    try:
        # Use final_scene (v10 all-in-one build)
        if 'final_scene' in _s.modules:
            del _s.modules['final_scene']
        import final_scene

        # Clean existing scene before building (cmds already imported at module level)
        for obj in ['crystalCavern_v9','crystalCavern_v8','crystalCavern_v10',
                    'CCV9_crystals','CCV9_dust','CCV9_cave_shell','CCV9_terrain',
                    'cave_terrain','cave_enclosure','crystal_group','dust_particles',
                    'cave_fog','stalactites','stalagmites']:
            if cmds.objExists(obj): cmds.delete(obj)
        for prefix in ['CCV9_','CCV8_','fly_cam','render_cam']:
            for n in (cmds.ls(prefix+'*') or []):
                try: cmds.delete(n)
                except: pass

        # Map density slider (0.5-4.0) → build density (20-80)
        mapped_density = int(15 + crystal_density * 18)

        # Build scene (no Arnold render — user clicks "Render Still" button instead)
        cam = final_scene.build(
            seed=terrain_seed,
            density=mapped_density,
            fog_density=fog_density,
            render=False  # separate render button does this
        )

        print("\n  Scene built! Camera: {0}".format(cam))
        print("  Click 'Render Still' to render, or")
        print("  Arnold > Open Render View > Start Render")

        cmds.confirmDialog(
            title="Generation Complete",
            message="Scene built successfully.\n{0} crystals generated.\nClick 'Render Still' to render.".format(
                mapped_density),
            button=["OK"],
            defaultButton="OK",
        )

    except Exception as e:
        cmds.warning("Generation failed: {0}".format(e))
        import traceback
        traceback.print_exc()


def reset_scene():
    """Confirm and create a fresh scene."""
    confirmed = cmds.confirmDialog(
        title="Reset Scene",
        message="Discard everything and create a new scene?",
        button=["Reset", "Cancel"],
        defaultButton="Cancel",
        cancelButton="Cancel",
        dismissString="Cancel",
    )
    if confirmed != "Reset":
        return
    cmds.file(new=True, force=True)


# ---------------------------------------------------------------------------
#  Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    create_ui()
