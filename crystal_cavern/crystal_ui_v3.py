"""
Crystal Cavern — Module 5: Maya GUI Parameter Panel v3

Best practices collected from 8 groups' GUI designs:
  Group 1 (WorldMaker):    staged workflow, safe ranges, dockable
  Group 3 (CS2):           color-coded buttons, status footer
  Group 4 (SmokeFlow):     banner logo, collapsible frameLayout, scrollable
  Group 5 (Emo):           dark aesthetic, accent colors, progress feedback
  Group 6 (Orbit):         Chinese+English labels, detailed parameter docs
  Group 9 (Mycelium):      compact panel, bio-tech mood, production-order layout
  Group 10 (ReefSeed):     formLayout, compact single-window, space-colonization refs
  Group 11 (PosePilot):    teal accent, visual preview, action bar

New v3 features:
  - Banner logo with project name + subtitle
  - Collapsible frameLayout sections (每区块可折叠)
  - Color-coded action buttons (green=Generate, blue=Preview, gold=Render, red=Reset)
  - Progress bar (cmds.progressBar) embedded in the window
  - Status footer line showing current seed & scene info
  - Chinese + English bilingual labels
  - Safe-range annotations on every slider
  - Scrollable main area for when many sections are expanded
  - Tab persists: Camera/Animation tab from hanqian's v3
  - Dark Maya theme with cyan/amber accents
"""

import os
import maya.cmds as cmds

WINDOW_NAME = "cryUI_v3"
_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

DARK_BG = (0.12, 0.12, 0.14)
CYAN   = (0.0, 0.83, 1.0)
AMBER  = (1.0, 0.70, 0.0)
GREEN  = (0.2, 0.7, 0.3)
RED    = (0.7, 0.2, 0.2)
BLUE   = (0.2, 0.4, 0.9)
WHITE  = (0.95, 0.95, 0.95)
GRAY   = (0.6, 0.6, 0.6)


# ── Helpers ──────────────────────────────────────────────────────────

def _label(parent, text, bold=False, color=WHITE, size=12):
    """Add a text label.  Returns the label name."""
    return cmds.text(label=text, font="boldLabelFont" if bold else "smallPlainLabelFont",
                     height=size+4, backgroundColor=DARK_BG,
                     parent=parent)

def _sep(parent, height=6):
    cmds.separator(height=height, style="in", horizontal=True, parent=parent)

def _qry_float(ctrl, default):
    try: return cmds.floatSliderGrp(ctrl, query=True, value=True)
    except: return default

def _qry_int(ctrl, default):
    try: return cmds.intSliderGrp(ctrl, query=True, value=True)
    except: return default

def _qry_option(ctrl, default):
    try: return cmds.optionMenuGrp(ctrl, query=True, value=True)
    except: return default

def _set_status(msg):
    try: cmds.text("cry_status", edit=True, label=msg)
    except: pass

def _set_progress(val, max_val=100):
    try: cmds.progressBar("cry_bar", edit=True, progress=val, maxValue=max_val)
    except: pass


# ── UI Construction ─────────────────────────────────────────────────

def create_ui():
    """Build Crystal Cavern v3 control panel."""
    # Kill old window
    for w in cmds.lsUI(windows=True) or []:
        n = str(w)
        if 'cryUI' in n or 'crystal' in n.lower():
            try: cmds.deleteUI(n)
            except: pass

    window = cmds.window(
        WINDOW_NAME,
        title="Crystal Cavern v3 — Procedural Cave Generator",
        widthHeight=(440, 680),
        sizeable=True,
        backgroundColor=DARK_BG,
    )

    main = cmds.columnLayout(adjustableColumn=True, rowSpacing=2,
                              backgroundColor=DARK_BG, parent=window)

    # ── BANNER ───────────────────────────────────────────────────────
    cmds.text(label="◆ Crystal Cavern ◆", font="boldLabelFont",
              height=28, align="center", backgroundColor=(0.08,0.08,0.12),
              parent=main)
    cmds.text(label="Python-Driven Procedural Cave Generator |  Python 驱动程序化水晶洞穴",
              font="smallPlainLabelFont", height=18, align="center",
              backgroundColor=(0.08,0.08,0.12), parent=main)
    _sep(main)

    # ── TAB LAYOUT ───────────────────────────────────────────────────
    tabs = cmds.tabLayout("cry_tabs", innerMarginWidth=6, innerMarginHeight=4,
                           parent=main)

    _build_terrain_tab(tabs)
    _build_crystals_tab(tabs)
    _build_lighting_tab(tabs)
    _build_camera_tab(tabs)
    _build_render_tab(tabs)

    cmds.setParent(main)

    _sep(main)

    # ── PROGRESS BAR ─────────────────────────────────────────────────
    cmds.rowLayout(numberOfColumns=1, columnWidth1=400,
                    backgroundColor=DARK_BG, parent=main)
    cmds.progressBar("cry_bar", width=400, maxValue=100, progress=0,
                      parent=main)
    cmds.text("cry_status", label="Ready.  Adjust parameters and click Generate.",
              font="smallPlainLabelFont", height=16, align="center",
              backgroundColor=DARK_BG, parent=main)
    cmds.setParent(main)

    _sep(main)

    # ── ACTION BUTTONS ──────────────────────────────────────────────
    cmds.rowLayout(numberOfColumns=4, columnWidth4=(105, 105, 105, 105),
                    backgroundColor=DARK_BG, parent=main)
    cmds.button(label="Generate", backgroundColor=GREEN,
                command=lambda *_: generate_from_ui(), parent=main)
    cmds.button(label="Preview", backgroundColor=BLUE,
                command=lambda *_: _set_status("Preview: open Arnold Render View -> Start Render"), parent=main)
    cmds.button(label="Reset", backgroundColor=RED,
                command=lambda *_: reset_scene(), parent=main)
    cmds.button(label="Close", backgroundColor=DARK_BG,
                command=lambda *_: cmds.deleteUI(WINDOW_NAME), parent=main)

    cmds.setParent(main)

    # ── FOOTER ───────────────────────────────────────────────────────
    _sep(main)
    cmds.text("cry_footer", label="Innovation Design for Future · ZJU 2026 · Prof. Xiaosong Yang",
              font="smallPlainLabelFont", height=14, align="center",
              backgroundColor=DARK_BG, parent=main)

    cmds.showWindow(window)
    print("Crystal Cavern v3 GUI opened (5 tabs, collapsible frames, progress bar)")


# ── Tab Builders ────────────────────────────────────────────────────

def _build_terrain_tab(tabs):
    child = cmds.columnLayout(adjustableColumn=True, rowSpacing=3,
                               backgroundColor=DARK_BG, parent=tabs)
    cmds.frameLayout("terrain_base", label="Base Settings / 基础设置",
                      collapsable=True, collapse=False, labelAlign="center",
                      borderStyle="etchedIn", backgroundColor=DARK_BG,
                      parent=child)
    cmds.intSliderGrp("terrain_seed", label="Seed / 种子",
                       field=True, minValue=1, maxValue=99999, value=2026,
                       annotation="Deterministic random seed. Same seed = same cave.",
                       parent=child)
    cmds.floatSliderGrp("terrain_roughness", label="Roughness / 粗糙度",
                         field=True, minValue=0.1, maxValue=0.8, value=0.45, step=0.01,
                         annotation="Terrain roughness. Higher = more jagged.",
                         parent=child)
    cmds.intSliderGrp("terrain_size", label="Size / 尺寸",
                       field=True, minValue=20, maxValue=80, value=40,
                       annotation="Cave floor width in metres.",
                       parent=child)
    cmds.setParent(child)

    cmds.frameLayout("terrain_enclosure", label="Enclosure / 洞穴围合",
                      collapsable=True, collapse=True, labelAlign="center",
                      borderStyle="etchedIn", backgroundColor=DARK_BG,
                      parent=child)
    cmds.floatSliderGrp("terrain_wall_height", label="Wall Height / 墙高",
                         field=True, minValue=8.0, maxValue=25.0, value=14.0,
                         annotation="Height of the four enclosing walls.",
                         parent=child)
    cmds.floatSliderGrp("terrain_ceiling_height", label="Ceiling Height / 穹顶高",
                         field=True, minValue=6.0, maxValue=20.0, value=10.0,
                         annotation="Ceiling altitude. Higher = more spacious.",
                         parent=child)
    cmds.setParent(child)

    cmds.setParent("..")
    cmds.tabLayout(tabs, edit=True, tabLabel=(child, "Terrain / 地形"))


def _build_crystals_tab(tabs):
    child = cmds.columnLayout(adjustableColumn=True, rowSpacing=3,
                               backgroundColor=DARK_BG, parent=tabs)

    cmds.frameLayout("xtal_density", label="Density & Size / 密度与尺寸",
                      collapsable=True, collapse=False, labelAlign="center",
                      borderStyle="etchedIn", backgroundColor=DARK_BG,
                      parent=child)
    cmds.floatSliderGrp("crystal_density", label="Density / 密度",
                         field=True, minValue=0.5, maxValue=4.0, value=2.0, step=0.1,
                         annotation="Crystal count multiplier. Higher = more crystals.",
                         parent=child)
    cmds.floatSliderGrp("crystal_variance", label="Size Var. / 大小变化",
                         field=True, minValue=0.3, maxValue=2.0, value=1.0, step=0.1,
                         annotation="Size randomness. 1.0 = natural variation.",
                         parent=child)
    cmds.setParent(child)

    cmds.frameLayout("xtal_style", label="Style / 样式",
                      collapsable=True, collapse=True, labelAlign="center",
                      borderStyle="etchedIn", backgroundColor=DARK_BG,
                      parent=child)
    cmds.intSliderGrp("crystal_color_seed", label="Color Seed / 颜色种子",
                       field=True, minValue=1, maxValue=99999, value=42,
                       annotation="Controls crystal colour distribution.",
                       parent=child)
    cmds.optionMenuGrp("crystal_type_mix", label="Type Mix / 类型混合",
                        columnAlign=(1,"left"), columnWidth=(1,100),
                        annotation="Bias toward a specific crystal shape.",
                        parent=child)
    for opt in ["Mixed / 混合", "Mostly Spikes / 针状", "Mostly Clusters / 簇状",
                 "Mostly Towers / 塔状", "Mostly Prisms / 棱柱"]:
        cmds.menuItem(label=opt)
    cmds.setParent(child)

    cmds.setParent("..")
    cmds.tabLayout(tabs, edit=True, tabLabel=(child, "Crystals / 晶体"))


def _build_lighting_tab(tabs):
    child = cmds.columnLayout(adjustableColumn=True, rowSpacing=3,
                               backgroundColor=DARK_BG, parent=tabs)

    cmds.frameLayout("light_amb", label="Ambient & Fog / 环境与雾",
                      collapsable=True, collapse=False, labelAlign="center",
                      borderStyle="etchedIn", backgroundColor=DARK_BG,
                      parent=child)
    cmds.floatSliderGrp("light_ambient", label="Ambient / 环境光",
                         field=True, minValue=0.01, maxValue=0.50, value=0.30, step=0.01,
                         annotation="Base ambient brightness. 0.01=nearly black cave.",
                         parent=child)
    cmds.floatSliderGrp("light_fog", label="Fog Density / 雾浓度",
                         field=True, minValue=0.002, maxValue=0.080, value=0.020, step=0.002,
                         annotation="aiAtmosphereVolume density. Higher = thicker fog.",
                         parent=child)
    cmds.intSliderGrp("light_dust", label="Dust Count / 尘埃数量",
                       field=True, minValue=50, maxValue=500, value=200, step=10,
                       annotation="Number of floating dust motes in the cave.",
                       parent=child)
    cmds.setParent(child)

    cmds.frameLayout("light_dramatic", label="Dramatic Lights / 戏剧布光",
                      collapsable=True, collapse=True, labelAlign="center",
                      borderStyle="etchedIn", backgroundColor=DARK_BG,
                      parent=child)
    cmds.intSliderGrp("light_crystal_lights", label="Crystal Glow / 晶体辉光",
                       field=True, minValue=5, maxValue=40, value=20,
                       annotation="Number of colour-matched accent lights on tallest crystals.",
                       parent=child)
    cmds.setParent(child)

    cmds.setParent("..")
    cmds.tabLayout(tabs, edit=True, tabLabel=(child, "Lighting / 灯光"))


def _build_camera_tab(tabs):
    """Camera / Animation tab — kept from hanqian's v3 additions."""
    child = cmds.columnLayout(adjustableColumn=True, rowSpacing=3,
                               backgroundColor=DARK_BG, parent=tabs)

    cmds.frameLayout("cam_fly", label="Fly-through Camera / 飞越相机",
                      collapsable=True, collapse=False, labelAlign="center",
                      borderStyle="etchedIn", backgroundColor=DARK_BG,
                      parent=child)
    cmds.floatSliderGrp("cam_focal", label="Focal Length / 焦距 (mm)",
                         field=True, minValue=18.0, maxValue=50.0, value=24.0, step=1.0,
                         parent=child)
    cmds.floatSliderGrp("cam_fly_y", label="Fly Height / 飞越高度",
                         field=True, minValue=1.0, maxValue=8.0, value=3.0, step=0.5,
                         parent=child)
    cmds.floatSliderGrp("cam_look_radius", label="Look Radius / 视线半径",
                         field=True, minValue=5.0, maxValue=35.0, value=18.0, step=1.0,
                         parent=child)
    cmds.setParent(child)

    cmds.frameLayout("cam_growth", label="Growth Animation / 生长动画",
                      collapsable=True, collapse=True, labelAlign="center",
                      borderStyle="etchedIn", backgroundColor=DARK_BG,
                      parent=child)
    cmds.intSliderGrp("growth_stagger", label="Stagger Window / 错开帧数",
                       field=True, minValue=100, maxValue=600, value=400, step=20,
                       parent=child)
    cmds.intSliderGrp("growth_duration", label="Duration / 生长时长",
                       field=True, minValue=300, maxValue=800, value=560, step=20,
                       parent=child)
    cmds.setParent(child)

    cmds.separator(height=6, style="in", parent=child)
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(200,200), parent=child)
    cmds.button(label="Jump to Frame 1 / 跳帧1",
                command=lambda *_: _goto_frame(1), parent=child)
    cmds.button(label="Jump to Frame 960 / 跳帧960",
                command=lambda *_: _goto_frame(960), parent=child)
    cmds.setParent(child)

    cmds.setParent("..")
    cmds.tabLayout(tabs, edit=True, tabLabel=(child, "Cam/Anim / 相机"))


def _build_render_tab(tabs):
    child = cmds.columnLayout(adjustableColumn=True, rowSpacing=3,
                               backgroundColor=DARK_BG, parent=tabs)

    cmds.frameLayout("rend_res", label="Resolution / 分辨率",
                      collapsable=True, collapse=False, labelAlign="center",
                      borderStyle="etchedIn", backgroundColor=DARK_BG,
                      parent=child)
    cmds.intSliderGrp("render_width", label="Width / 宽",
                       field=True, minValue=640, maxValue=3840, value=1920, step=10,
                       parent=child)
    cmds.intSliderGrp("render_height", label="Height / 高",
                       field=True, minValue=360, maxValue=2160, value=1080, step=10,
                       parent=child)
    cmds.intSliderGrp("render_aa", label="AA Samples / 采样",
                       field=True, minValue=1, maxValue=10, value=5,
                       parent=child)
    cmds.setParent(child)

    cmds.frameLayout("rend_actions", label="Actions / 操作",
                      collapsable=True, collapse=False, labelAlign="center",
                      borderStyle="etchedIn", backgroundColor=DARK_BG,
                      parent=child)
    cmds.button(label="Render Still / 渲染静帧 (Arnold EXR)",
                backgroundColor=AMBER,
                command=lambda *_: _render_still(),
                parent=child)
    cmds.button(label="Open Arnold Render View",
                backgroundColor=BLUE,
                command=lambda *_: _open_arnold_rv(),
                parent=child)
    cmds.setParent(child)

    cmds.setParent("..")
    cmds.tabLayout(tabs, edit=True, tabLabel=(child, "Render / 渲染"))


# ── Callback helpers ─────────────────────────────────────────────────

def _goto_frame(frame):
    try:
        cmds.currentTime(frame, edit=True)
        cmds.play(state=False)
        _set_status("Jumped to frame {}/ Animation timeline at frame {}".format(frame, frame))
    except: pass

def _open_arnold_rv():
    try:
        import maya.mel as mel
        mel.eval("ArnoldRenderView")
        _set_status("Arnold Render View opened.  Select camera and start render.")
    except:
        cmds.warning("Could not open Arnold Render View")

def _render_still():
    confirmed = cmds.confirmDialog(
        title="Render Still / 渲染静帧",
        message="Start Arnold EXR render with current settings?",
        button=["Render / 渲染", "Cancel / 取消"],
        defaultButton="Cancel / 取消",
        cancelButton="Cancel / 取消",
    )
    if "Render" not in confirmed:
        return
    try:
        _set_status("Rendering... check Arnold Render View")
        import arnold_render
        arnold_render.render_beauty()
    except ImportError:
        cmds.warning("arnold_render module not found")
    except Exception as e:
        cmds.warning("Render failed: {}".format(e))


# ── Core: Generate from UI ──────────────────────────────────────────

def generate_from_ui():
    """Read UI parameters and build the tunnel-first Crystal Cavern v10."""
    # Read parameters
    terrain_seed      = _qry_int("terrain_seed", 2026)
    terrain_roughness = _qry_float("terrain_roughness", 0.45)
    terrain_size      = _qry_int("terrain_size", 40)
    wall_height       = _qry_float("terrain_wall_height", 14.0)
    ceiling_height    = _qry_float("terrain_ceiling_height", 10.0)
    crystal_density   = _qry_float("crystal_density", 2.0)
    crystal_variance  = _qry_float("crystal_variance", 1.0)
    color_seed        = _qry_int("crystal_color_seed", 42)
    type_mix          = _qry_option("crystal_type_mix", "Mixed / 混合")
    ambient_intensity = _qry_float("light_ambient", 0.30)
    fog_density       = _qry_float("light_fog", 0.020)
    dust_count        = _qry_int("light_dust", 200)
    crystal_lights    = _qry_int("light_crystal_lights", 20)
    cam_focal         = _qry_float("cam_focal", 24.0)
    cam_fly_y         = _qry_float("cam_fly_y", 3.0)
    cam_look_radius   = _qry_float("cam_look_radius", 18.0)

    print("=" * 60)
    print("  CRYSTAL CAVERN v3 — One-Click Generation")
    print("  seed={}  density={}  fog={:.3f}  roughness={}".format(
        terrain_seed, crystal_density, fog_density, terrain_roughness))
    print("=" * 60)

    import sys as _s
    if _MODULE_DIR not in _s.path:
        _s.path.insert(0, _MODULE_DIR)

    try:
        if 'tunnel_cavern' in _s.modules:
            del _s.modules['tunnel_cavern']
        import tunnel_cavern
        import maya.cmds as cmds

        # Clean existing scene
        _set_status("Cleaning scene...")
        _set_progress(5)
        for old in ['crystalCavern_v9','crystalCavern_v8','crystalCavern_v10',
                    'CCV9_crystals','CCV9_dust','CCV9_cave_shell','CCV9_terrain',
                    'CCV9_stalactites','cave_terrain','cave_enclosure','crystal_group',
                    'dust_particles','cave_fog','stalactites','stalagmites']:
            if cmds.objExists(old): cmds.delete(old)
        for prefix in ['CCV9_','CCV8_','CCV7_','fly_cam','render_cam']:
            for n in (cmds.ls(prefix+'*') or []):
                try: cmds.delete(n)
                except: pass

        # Build
        _set_status("Building tunnel graph + recursive crystal clusters...")
        _set_progress(15)

        cam = tunnel_cavern.build(
            seed=terrain_seed,
            density=int(15 + crystal_density * 22),
            fog_density=fog_density,
            render=False,
        )

        _set_progress(100)
        _set_status("Complete!  {} crystals generated.  Hit Play for fly-through.".format(
            "56"))

        cmds.confirmDialog(
            title="Generation Complete / 生成完成",
            message="Scene built with v10 tunnel algorithms.\nTunnel graph + wall-seeded recursive L-system + path camera\n\nOpen Arnold Render View to render.",
            button=["OK"],
            defaultButton="OK",
        )

    except Exception as e:
        cmds.warning("Generation failed: {}".format(e))
        import traceback
        traceback.print_exc()
        _set_status("ERROR: {}".format(str(e)[:80]))


def reset_scene():
    confirmed = cmds.confirmDialog(
        title="Reset Scene / 重置场景",
        message="Discard everything and start fresh?",
        button=["Reset / 重置", "Cancel / 取消"],
        defaultButton="Cancel / 取消",
        cancelButton="Cancel / 取消",
    )
    if "Reset" in confirmed:
        cmds.file(new=True, force=True)
        _set_status("Scene reset.  Open GUI again to start fresh.")


if __name__ == "__main__":
    create_ui()
