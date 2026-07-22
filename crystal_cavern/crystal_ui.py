"""
Crystal Cavern — Procedural Crystal Cave Generator
Module 5: Maya GUI Parameter Panel (v2)

Provides a tabbed user interface for controlling all crystal generation,
lighting, and rendering parameters.
"""

import os

import maya.cmds as cmds

WINDOW_NAME = "crystalCavernUI_v2"
TAB_LAYOUT = "cc_tabs"

# Directory of this module (used to put the project on sys.path regardless
# of which machine / checkout the panel runs from).
_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))


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
        widthHeight=(400, 600),
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

    # ── Tab 4: Camera / Animation ───────────────────────────────────────
    _build_camera_tab(tabs)

    # ── Tab 5: Render ───────────────────────────────────────────────────
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


def _build_camera_tab(tabs):
    """Populate the Camera / Animation tab.

    Exposes the fly-through and growth-animation knobs that
    ``final_scene.build()`` now accepts, so the immersive feel can be tuned
    without editing code.
    """
    child = cmds.columnLayout(adjustableColumn=True, rowSpacing=4)
    cmds.floatSliderGrp(
        "cam_focal",
        label="Focal Length (mm)",
        field=True, minValue=18.0, maxValue=50.0, value=24.0, step=1.0,
    )
    cmds.floatSliderGrp(
        "cam_fly_y",
        label="Fly Eye Height",
        field=True, minValue=1.0, maxValue=8.0, value=3.0, step=0.5,
    )
    cmds.floatSliderGrp(
        "cam_look_radius",
        label="Look Attraction Radius",
        field=True, minValue=5.0, maxValue=35.0, value=18.0, step=1.0,
    )
    cmds.separator(height=6, style="in")
    cmds.text(label="  Crystal Growth Animation", font="smallBoldLabelFont",
              height=18, align="left")
    cmds.intSliderGrp(
        "growth_stagger",
        label="Stagger Window (frames)",
        field=True, minValue=100, maxValue=600, value=400, step=20,
    )
    cmds.intSliderGrp(
        "growth_duration",
        label="Growth Duration (frames)",
        field=True, minValue=300, maxValue=800, value=560, step=20,
    )
    cmds.separator(height=6, style="in")
    cmds.button(
        label="Frame 1 (preview start)",
        command=lambda *_: _goto_frame(1),
    )
    cmds.button(
        label="Frame 960 (preview end)",
        command=lambda *_: _goto_frame(960),
    )
    cmds.setParent("..")
    cmds.tabLayout(tabs, edit=True, tabLabel=(child, "Cam/Anim"))


def _goto_frame(frame):
    """Jump the timeline to *frame* and stop playback (preview helper)."""
    try:
        cmds.currentTime(frame, edit=True)
        cmds.play(state=False)
    except (RuntimeError, ValueError):
        pass


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

    # Camera / animation sliders (guarded: tab absent on older panels)
    cam_focal = _qry_float("cam_focal", 24.0)
    cam_fly_y = _qry_float("cam_fly_y", 3.0)
    cam_look_radius = _qry_float("cam_look_radius", 18.0)
    growth_stagger = _qry_int("growth_stagger", 400)
    growth_duration = _qry_int("growth_duration", 560)

    render_width = cmds.intSliderGrp("render_width", query=True, value=True)
    render_height = cmds.intSliderGrp("render_height", query=True, value=True)
    render_aa = cmds.intSliderGrp("render_aa", query=True, value=True)

    # ── Log ───────────────────────────────────────────────────────────
    print("=" * 60)
    print("  CRYSTAL CAVERN v10 — One-Click Generation")
    print("  seed={0}  density={1}  fog={2}  roughness={3}".format(
        terrain_seed, crystal_density, fog_density, terrain_roughness))
    print("  cam: {0}mm  fly_y={1}  look_r={2}  growth {3}/{4}f".format(
        cam_focal, cam_fly_y, cam_look_radius, growth_stagger, growth_duration))
    print("=" * 60)

    # ── Ensure project is on path (machine-independent, no hardcoded dir) ──
    import sys as _s
    if _MODULE_DIR not in _s.path:
        _s.path.insert(0, _MODULE_DIR)

    try:
        # Use final_scene (v10 all-in-one build)
        if 'final_scene' in _s.modules:
            del _s.modules['final_scene']
        import final_scene

        # Clean existing scene before building (cmds already imported at module level)
        for obj in ['crystalCavern_v9','crystalCavern_v8','crystalCavern_v10',
                    'CCV9_crystals','CCV9_dust','CCV9_cave_shell','CCV9_terrain',
                    'cave_terrain','cave_enclosure','crystal_group','dust_particles',
                    'cave_fog','stalactites','stalagmites',
                    'CCV9_cam_lookat','CCV9_cam_aimConstraint']:
            if cmds.objExists(obj): cmds.delete(obj)
        for prefix in ['CCV9_','CCV8_','CCV9_cam','fly_cam','render_cam']:
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
            render=False,  # separate render button does this
            camera_focal=cam_focal,
            fly_y=cam_fly_y,
            look_radius=cam_look_radius,
            growth_stagger=growth_stagger,
            growth_duration=growth_duration,
        )

        print("\n  Scene built! Camera: {0}".format(cam))
        print("  Fly-through 1->960; click 'Render Still' or play the timeline.")

        # Jump to frame 1 and look through the new camera so the user sees
        # the start of the fly-through immediately, without a blocking dialog.
        _look_through(cam)

    except Exception as e:
        cmds.warning("Generation failed: {0}".format(e))
        import traceback
        traceback.print_exc()


def _look_through(cam):
    """Switch the active model panel to the fly camera and go to frame 1."""
    try:
        cmds.currentTime(1, edit=True)
        cmds.play(state=False)
        panel = cmds.getPanel(withFocus=True)
        if panel and cmds.getPanel(typeOf=panel) == "modelPanel":
            cmds.modelPanel(panel, edit=True, camera=cam)
    except (RuntimeError, ValueError):
        pass


def _qry_float(name, default):
    """Query a floatSliderGrp by name, returning *default* if it is absent."""
    try:
        if cmds.floatSliderGrp(name, exists=True):
            return cmds.floatSliderGrp(name, query=True, value=True)
    except (RuntimeError, ValueError):
        pass
    return float(default)


def _qry_int(name, default):
    """Query an intSliderGrp by name, returning *default* if it is absent."""
    try:
        if cmds.intSliderGrp(name, exists=True):
            return cmds.intSliderGrp(name, query=True, value=True)
    except (RuntimeError, ValueError):
        pass
    return int(default)


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
    # Drop leftover roots / lights before opening a fresh scene so the next
    # Generate does not inherit stale geometry or orphaned lights.
    for prefix in ['crystalCavern_v', 'CCV9_', 'CCV8_', 'fly_cam', 'render_cam',
                   'cave_terrain', 'cave_enclosure', 'crystal_group',
                   'dust_particles', 'cave_fog', 'stalactites', 'stalagmites']:
        for n in (cmds.ls(prefix + '*') or []):
            try:
                cmds.delete(n)
            except (RuntimeError, ValueError):
                pass
    cmds.file(new=True, force=True)


# ---------------------------------------------------------------------------
#  Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    create_ui()
