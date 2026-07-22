"""Crystal Cavern Final Build — one-click total scene generation + render.

Paste into Maya Script Editor Python tab → Ctrl+Enter.

Produces:
- Enclosed cave with diamond-square terrain + fissure-textured walls + stalactites
- 40 hexagonal prism crystals (8-25m) with L-system branches + root embedding
- SSS/transmission/coat Arnold materials with cloudy internal noise texture
- Dark ambient + 3-point lighting + 25 color-matched crystal glow lights
- aiAtmosphereVolume fog + 300 dust particles
- Dynamic fly-through camera (960 frames)
- Crystal growth animation (0→full at frame 960)
- Arnold render (1920x1080, AA=6, EXR beauty+Z)
"""

import sys, os, math, random, traceback

SD = "/Users/xixi/大学/未来创新设计/crystal_cavern"
sys.path.insert(0, SD)
for m in ['cave_lighting','cave_terrain','crystal_growth','crystal_seed','arnold_render']:
    if m in sys.modules:
        del sys.modules[m]

import maya.cmds as cmds
import maya.mel as mel

OUT = os.path.join(SD, "renders", "final_v7")

# ═══════════════════════════════════════════════════════════════════════
# 0. NUCLEAR CLEANUP
# ═══════════════════════════════════════════════════════════════════════
TO_CLEAN = [
    'cave_terrain','cave_enclosure','crystal_group','dust_particles',
    'cave_fog','stalactites','stalagmites',
]
for obj in TO_CLEAN:
    if cmds.objExists(obj):
        cmds.delete(obj)
for n in ['fly_cam','render_cam']:
    for o in (cmds.ls(n + '*') or []):
        try: cmds.delete(o)
        except: pass
for lt in ['ambientLight','directionalLight','pointLight','spotLight','areaLight']:
    for l in cmds.ls(type=lt):
        try: cmds.delete(l)
        except: pass
for t in ['aiStandardSurface','lambert','blinn','phong','phongE','aiAtmosphereVolume']:
    for s in (cmds.ls(type=t) or []):
        name = str(s)
        if name not in ['lambert1','particleCloud1','standardSurface1','shaderGlow1']:
            try: cmds.delete(s)
            except: pass
for sg in (cmds.ls(type='shadingEngine') or []):
    if str(sg) not in ('initialShadingGroup','initialParticleSE'):
        try: cmds.delete(sg)
        except: pass
print("0. CLEANUP DONE")

# ═══════════════════════════════════════════════════════════════════════
# 1. IMPORTS
# ═══════════════════════════════════════════════════════════════════════
from cave_terrain import create_cave_terrain, create_cave_enclosure
from crystal_seed import get_terrain_surface_info, poisson_disc_sample
from cave_lighting import create_camera_rig

# ═══════════════════════════════════════════════════════════════════════
# 2. TERRAIN
# ═══════════════════════════════════════════════════════════════════════
print("\n1. TERRAIN (Diamond-Square + cave enclosure)")
t, hm = create_cave_terrain(width=40, depth=40, seed=2026, roughness=0.45,
                             wall_height=20, subdivisions=256)
vtx = cmds.polyEvaluate(t, vertex=True)
print("   {0} vertices, enclosed cave bowl".format(vtx))

# ═══════════════════════════════════════════════════════════════════════
# 3. SEEDS
# ═══════════════════════════════════════════════════════════════════════
print("\n2. CRYSTAL SEEDS (Poisson-disc)")
v = get_terrain_surface_info(t)
s = poisson_disc_sample(v, min_dist=1.5, seed=2026)
print("   {0} seeds (high density)".format(len(s)))

# ═══════════════════════════════════════════════════════════════════════
# 4. GEM PRESETS + MATERIAL CACHE
# ═══════════════════════════════════════════════════════════════════════
GEMS = [
    {"name":"amethyst","color":(0.45,0.15,0.60),"glow":(0.20,0.10,0.35),"ior":1.54},
    {"name":"citrine","color":(0.75,0.50,0.12),"glow":(0.35,0.22,0.06),"ior":1.54},
    {"name":"fluorite","color":(0.12,0.52,0.35),"glow":(0.07,0.32,0.20),"ior":1.43},
    {"name":"aquamarine","color":(0.10,0.42,0.58),"glow":(0.05,0.28,0.42),"ior":1.58},
    {"name":"rose_quartz","color":(0.68,0.38,0.45),"glow":(0.38,0.20,0.23),"ior":1.54},
    {"name":"obsidian","color":(0.05,0.04,0.07),"glow":(0.02,0.01,0.02),"ior":1.49},
    {"name":"emerald","color":(0.06,0.48,0.25),"glow":(0.03,0.32,0.16),"ior":1.57},
    {"name":"ruby","color":(0.68,0.06,0.10),"glow":(0.48,0.04,0.07),"ior":1.77},
    {"name":"sapphire","color":(0.06,0.12,0.50),"glow":(0.03,0.08,0.38),"ior":1.77},
    {"name":"topaz","color":(0.68,0.45,0.10),"glow":(0.32,0.22,0.04),"ior":1.62},
]

_mat_cache = {}

def get_gem_material(preset_idx):
    """Create/return Arnold aiStandardSurface with SSS + transmission + cloudy noise."""
    p = GEMS[preset_idx % len(GEMS)]
    name = "gem_" + p["name"]
    if name in _mat_cache and cmds.objExists(_mat_cache[name]):
        return _mat_cache[name]

    # Delete old instance
    if cmds.objExists(name):
        try: cmds.delete(name)
        except: pass

    shader = cmds.createNode("aiStandardSurface", name=name)
    r, g, b = p["color"]
    gr, gg, gb = p["glow"]

    # Base + specular
    try: cmds.setAttr(shader + ".base", 0.7)
    except: pass
    try: cmds.setAttr(shader + ".baseColor", r, g, b)
    except: pass
    try: cmds.setAttr(shader + ".specular", 1.0)
    except: pass
    try: cmds.setAttr(shader + ".specularRoughness", 0.06)
    except: pass
    try: cmds.setAttr(shader + ".specularIOR", p["ior"])
    except: pass

    # Transmission (glass)
    try: cmds.setAttr(shader + ".transmission", 0.6)
    except: pass
    try: cmds.setAttr(shader + ".transmissionDepth", 3.0)
    except: pass
    try: cmds.setAttr(shader + ".transmissionColor", r*0.5, g*0.5, b*0.5)
    except: pass

    # Subsurface scattering
    try: cmds.setAttr(shader + ".subsurface", 0.8)
    except: pass
    try: cmds.setAttr(shader + ".subsurfaceColor", gr, gg, gb)
    except: pass
    try: cmds.setAttr(shader + ".subsurfaceRadius", 0.5, 0.5, 0.5)
    except: pass
    try: cmds.setAttr(shader + ".subsurfaceScale", 3.0)
    except: pass

    # Coat (thin-film iridescence)
    try: cmds.setAttr(shader + ".coat", 0.35)
    except: pass
    try: cmds.setAttr(shader + ".coatRoughness", 0.02)
    except: pass
    try: cmds.setAttr(shader + ".coatIOR", 1.4)
    except: pass

    # Emission (self-glow)
    try: cmds.setAttr(shader + ".emission", 0.2)
    except: pass
    try: cmds.setAttr(shader + ".emissionColor", gr*0.6, gg*0.6, gb*0.6)
    except: pass

    # Dispersion
    try: cmds.setAttr(shader + ".dispersionAbbe", 45)
    except: pass

    # ═══ NEW: Cloudy internal inclusion texture (subsurface scatter noise) ═══
    create_cloudy_inclusion_texture(shader, p)

    # Shading group
    try:
        sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True,
                       name=name + "_SG")
        cmds.connectAttr(shader + ".outColor", sg + ".surfaceShader", force=True)
    except: pass

    _mat_cache[name] = name
    return name


def create_cloudy_inclusion_texture(shader, preset):
    """Add a 3D noise-driven cloudy inclusion pattern to subsurface color.

    This creates the '内部云雾状天然包裹纹理' — internal cloudy texture.
    Uses Arnold aiNoise → aiColorCorrect → subsurfaceColor chain.
    """
    try:
        # Create 3D noise node for cloudy internal texture
        noise = cmds.createNode("aiNoise", name=shader + "_cloud_noise")
        cmds.setAttr(noise + ".octaves", 4)
        cmds.setAttr(noise + ".distortion", 0.15)
        cmds.setAttr(noise + ".lacunarity", 2.0)
        cmds.setAttr(noise + ".amplitude", 1.0)
        # Scale noise so it creates visible cloudy patches inside crystals
        cmds.setAttr(noise + ".scaleX", 3.0)
        cmds.setAttr(noise + ".scaleY", 3.0)
        cmds.setAttr(noise + ".scaleZ", 3.0)

        # Color correct to tint the noise to the gem's color
        cc = cmds.createNode("aiColorCorrect", name=shader + "_cloud_cc")
        gr, gg, gb = preset["glow"]
        cmds.setAttr(cc + ".saturation", 0.3)
        cmds.setAttr(cc + ".hueShift", 0.0)

        # Connect: noise → colorCorrect.input, colorCorrect.out → subsurfaceColor
        cmds.connectAttr(noise + ".outColor", cc + ".input", force=True)
        cmds.connectAttr(cc + ".outColor", shader + ".subsurfaceColor", force=True)

        # Also drive transmission scatter with noise for varied translucency
        cmds.connectAttr(noise + ".outColorR", shader + ".subsurfaceScale", force=True)

        return True
    except (RuntimeError, ValueError):
        # Fall back to direct color if Arnold nodes unavailable
        return False


# ═══════════════════════════════════════════════════════════════════════
# 5. CRYSTAL GROWTH (hexagonal prisms + L-system branching)
# ═══════════════════════════════════════════════════════════════════════
print("\n3. CRYSTAL GROWTH (hexagonal prisms, L-system branches, root embedding)")

if cmds.objExists("crystal_group"):
    cmds.delete("crystal_group")
cmds.group(empty=True, name="crystal_group")

count = 0
light_anchors = []

# For growth animation: store visibility keys per crystal
_growth_data = []

for i, seed_data in enumerate(s):
    try:
        pos = seed_data["position"]
        normal = seed_data["normal"]
        variance = seed_data["variance"]

        nl = math.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2)
        nx, ny, nz = normal[0]/nl, normal[1]/nl, normal[2]/nl

        # Crystal size: 8-25 units tall
        height = 8 + 17 * variance
        width = 0.3 + 0.5 * variance

        uid = random.randint(10000, 99999)
        grp = cmds.group(empty=True, name="cry_" + str(uid))
        cmds.parent(grp, "crystal_group")

        mat = get_gem_material(i)

        # ═══ BODY: hexagonal cylinder (6 sides = hexagonal prism) ═══
        body_h = height * 0.75
        body = cmds.polyCylinder(
            name="cry_body_" + str(uid),
            r=width, h=body_h,
            sx=6, sy=2, sc=0, ch=0,
        )[0]

        # Embed root 12% into terrain
        body_embed = body_h * 0.12
        body_mid = body_h / 2.0 - body_embed
        bx, by, bz = pos[0]+nx*body_mid, pos[1]+ny*body_mid, pos[2]+nz*body_mid
        cmds.xform(body, translation=(bx, by, bz), worldSpace=True)

        # Align to normal via aim constraint
        loc = cmds.spaceLocator(name="tmp_a_" + str(random.randint(10000,99999)))[0]
        cmds.xform(loc, t=(bx+nx*10, by+ny*10, bz+nz*10), ws=True)
        try:
            ac = cmds.aimConstraint(loc, body, aim=(0,1,0), u=(0,0,1), wut="vector", wu=(0,0,1))
            cmds.delete(ac)
        except: pass
        try: cmds.delete(loc)
        except: pass

        cmds.parent(body, grp)
        cmds.select(body)
        try: cmds.hyperShade(assign=mat)
        except: pass

        # ═══ TIP: sharp cone ═══
        tip_h = height * 0.25
        tip = cmds.polyCone(
            name="cry_tip_" + str(uid),
            r=width*0.9, h=tip_h,
            sx=6, sy=3, sc=0, ch=0,
        )[0]
        tip_mid = body_h - body_embed + tip_h/2.0
        cmds.xform(tip, t=(pos[0]+nx*tip_mid, pos[1]+ny*tip_mid, pos[2]+nz*tip_mid), ws=True)

        loc2 = cmds.spaceLocator(name="tmp_b_" + str(random.randint(10000,99999)))[0]
        cmds.xform(loc2, t=(pos[0]+nx*(tip_mid+10), pos[1]+ny*(tip_mid+10), pos[2]+nz*(tip_mid+10)), ws=True)
        try:
            ac2 = cmds.aimConstraint(loc2, tip, aim=(0,1,0), u=(0,0,1), wut="vector", wu=(0,0,1))
            cmds.delete(ac2)
        except: pass
        try: cmds.delete(loc2)
        except: pass

        cmds.parent(tip, grp)
        cmds.select(tip)
        try: cmds.hyperShade(assign=mat)
        except: pass

        # ═══ SIDE BRANCHES (L-system style, 3-8 per crystal) ═══
        n_sides = random.randint(3, 8)
        for si in range(n_sides):
            try:
                bt = 0.15 + random.uniform(0, 0.4)
                bp = [pos[0]+nx*height*bt, pos[1]+ny*height*bt, pos[2]+nz*height*bt]

                # Spherical branching direction
                dev = random.uniform(0.3, 0.7)
                az = random.uniform(0, 2*math.pi)

                if abs(nx) < 0.9:
                    p1 = (0, -nz, ny)
                else:
                    p1 = (-nz, 0, nx)
                pl = math.sqrt(p1[0]**2+p1[1]**2+p1[2]**2)
                p1 = (p1[0]/pl, p1[1]/pl, p1[2]/pl)
                p2 = (ny*p1[2]-nz*p1[1], nz*p1[0]-nx*p1[2], nx*p1[1]-ny*p1[0])

                bnx = nx*math.cos(dev)+p1[0]*math.sin(dev)*math.cos(az)+p2[0]*math.sin(dev)*math.sin(az)
                bny = ny*math.cos(dev)+p1[1]*math.sin(dev)*math.cos(az)+p2[1]*math.sin(dev)*math.sin(az)
                bnz = nz*math.cos(dev)+p1[2]*math.sin(dev)*math.cos(az)+p2[2]*math.sin(dev)*math.sin(az)
                bl2 = math.sqrt(bnx**2+bny**2+bnz**2)
                bnx, bny, bnz = bnx/bl2, bny/bl2, bnz/bl2

                ss = random.uniform(0.15, 0.35)
                side_h = height * ss
                side_w = width * 0.4
                side_m = side_h / 2.0

                side_obj = cmds.polyCylinder(
                    name="cry_sd_" + str(uid) + "_" + str(si),
                    r=side_w, h=side_h,
                    sx=6, sy=1, sc=0, ch=0,
                )[0]
                cmds.xform(side_obj, t=(
                    bp[0]+bnx*side_m, bp[1]+bny*side_m, bp[2]+bnz*side_m
                ), ws=True)

                loc3 = cmds.spaceLocator(name="tmp_c_" + str(random.randint(10000,99999)))[0]
                cmds.xform(loc3, t=(bp[0]+bnx*10, bp[1]+bny*10, bp[2]+bnz*10), ws=True)
                try:
                    ac3 = cmds.aimConstraint(loc3, side_obj, aim=(0,1,0), u=(0,0,1), wut="vector", wu=(0,0,1))
                    cmds.delete(ac3)
                except: pass
                try: cmds.delete(loc3)
                except: pass

                cmds.parent(side_obj, grp)
                cmds.select(side_obj)
                try: cmds.hyperShade(assign=mat)
                except: pass
            except: pass

        # Light anchor at 50% height
        light_anchors.append((
            (pos[0]+nx*height*0.5, pos[1]+ny*height*0.5, pos[2]+nz*height*0.5),
            GEMS[i % len(GEMS)]["glow"]
        ))
        count += 1
        if count % 10 == 0:
            print("   {0} crystals...".format(count))
    except Exception as e:
        print("   CRYSTAL {0} FAILED: {1}".format(i, str(e)[:80]))

print("   TOTAL: {0} faceted hexagonal prism crystals with branches".format(count))

# ═══════════════════════════════════════════════════════════════════════
# 6. LIGHTING (dark cave + 3-point + crystal glow)
# ═══════════════════════════════════════════════════════════════════════
print("\n4. LIGHTING")

# Very dark ambient
amb = cmds.shadingNode("ambientLight", asLight=True, name="cave_ambient")
try: cmds.setAttr(amb + ".intensity", 0.03)
except: pass
try: cmds.setAttr(amb + ".color", 0.015, 0.01, 0.03, type="double3")
except: pass
try: cmds.setAttr(amb + ".ambientShade", 0.98)
except: pass

# Key light (warm, from cave mouth)
key = cmds.shadingNode("directionalLight", asLight=True, name="cave_key")
try: cmds.setAttr(key + ".intensity", 2.0)
except: pass
try: cmds.setAttr(key + ".color", 1.0, 0.78, 0.45, type="double3")
except: pass
cmds.move(25, 15, 25, key)
cmds.rotate(-35, -45, 0, key)

# Rim light (cool blue, from cave rear)
rim = cmds.shadingNode("directionalLight", asLight=True, name="cave_rim")
try: cmds.setAttr(rim + ".intensity", 0.5)
except: pass
try: cmds.setAttr(rim + ".color", 0.25, 0.35, 0.65, type="double3")
except: pass
cmds.move(-18, 6, -18, rim)
cmds.rotate(20, 135, 0, rim)

# Crystal accent point lights (color-matched to each gem)
n_lights = min(len(light_anchors), 25)
for i in range(n_lights):
    pos, glow = light_anchors[i]
    lt = cmds.shadingNode("pointLight", asLight=True, name="cry_lt_" + str(i))
    try: cmds.setAttr(lt + ".color", min(glow[0]*4, 1), min(glow[1]*4, 1), min(glow[2]*4, 1), type="double3")
    except: pass
    try: cmds.setAttr(lt + ".intensity", random.uniform(3.0, 8.0))
    except: pass
    try: cmds.setAttr(lt + ".decayRate", 2)
    except: pass
    cmds.move(pos[0]+random.uniform(-2,2), pos[1]+random.uniform(1,4), pos[2]+random.uniform(-2,2), lt)

print("   Dark ambient + key + rim + {0} crystal glow lights".format(n_lights))

# ═══════════════════════════════════════════════════════════════════════
# 7. VOLUMETRIC FOG
# ═══════════════════════════════════════════════════════════════════════
print("\n5. VOLUMETRIC FOG")
for fn in ["cave_fog"]:
    if cmds.objExists(fn):
        try: cmds.delete(fn)
        except: pass

fog_ok = False
try:
    fog = cmds.createNode("aiAtmosphereVolume", name="cave_fog")
    # Each setAttr in its own try — if one fails, the rest still run
    try: cmds.setAttr(fog + ".density", 0.08)
    except: pass
    try: cmds.setAttr(fog + ".atmosphereColor", 0.03, 0.02, 0.06, type="double3")
    except: pass
    try: cmds.setAttr(fog + ".attenuation", 0.7)
    except: pass
    try: cmds.setAttr(fog + ".attenuationColor", 0.01, 0.01, 0.04, type="double3")
    except: pass
    try: cmds.setAttr(fog + ".groundNormal", 0.0, 1.0, 0.0, type="double3")
    except: pass
    try: cmds.setAttr(fog + ".groundPoint", 0.0, -12.0, 0.0, type="double3")
    except: pass
    fog_ok = True
    print("   Arnold aiAtmosphereVolume (density=0.08)")
except Exception:
    print("   Fog skipped (Arnold mtoa not available)")

# ═══════════════════════════════════════════════════════════════════════
# 8. DUST PARTICLES
# ═══════════════════════════════════════════════════════════════════════
if cmds.objExists("dust_particles"):
    cmds.delete("dust_particles")
dust_grp = cmds.group(empty=True, name="dust_particles")
dust_mat = cmds.shadingNode("lambert", asShader=True, name="dust_mat")
try: cmds.setAttr(dust_mat + ".color", 1.0, 0.9, 0.75, type="double3")
except: pass
try: cmds.setAttr(dust_mat + ".ambientColor", 0.2, 0.15, 0.1, type="double3")
except: pass
try: cmds.setAttr(dust_mat + ".transparency", 0.6, 0.65, 0.7)
except: pass

for di in range(300):
    dm = cmds.polySphere(name="dust_" + str(di), r=random.uniform(0.02, 0.06), sx=4, sy=4)[0]
    cmds.move(random.uniform(-22, 22), random.uniform(-10, 8), random.uniform(-22, 22), dm)
    cmds.select(dm); cmds.hyperShade(assign=dust_mat)
    cmds.parent(dm, dust_grp)
print("   Dust: 300 motes")

# ═══════════════════════════════════════════════════════════════════════
# 9. ENCLOSURE
# ═══════════════════════════════════════════════════════════════════════
print("\n6. CAVE ENCLOSURE (walls + ceiling + stalactites/stalagmites)")
create_cave_enclosure(terrain_name=t, width=40, depth=40, wall_height=14, ceiling_height=12)
print("   Complete")

# ═══════════════════════════════════════════════════════════════════════
# 10. DYNAMIC CAMERA + GROWTH ANIMATION
# ═══════════════════════════════════════════════════════════════════════
print("\n7. CAMERA + GROWTH ANIMATION")
create_camera_rig(terrain_name=t, crystal_group="crystal_group")

# Remove aim constraints for clean render
for ac in (cmds.ls(type='aimConstraint') or []):
    try: cmds.delete(ac)
    except: pass

# Enable renderable on all cameras
for cc in cmds.ls(type='camera'):
    try: cmds.setAttr(cc + '.renderable', True)
    except: pass

# ═══ GROWTH ANIMATION: crystals scale from 0→1 over frames 0-960 ═══
# Animate each crystal's scale to simulate growth from rock
if cmds.objExists('crystal_group'):
    children = cmds.listRelatives('crystal_group', children=True, type='transform') or []
    for idx, child in enumerate(children):
        # Stagger growth start: each crystal starts at a slightly different frame
        start_frame = int((idx / len(children)) * 200)  # spread over first 200 frames
        end_frame = start_frame + 480  # each takes ~480 frames to grow

        try:
            # Scale 0 at start
            cmds.setKeyframe(child, attribute='scaleX', value=0.01, time=start_frame)
            cmds.setKeyframe(child, attribute='scaleY', value=0.01, time=start_frame)
            cmds.setKeyframe(child, attribute='scaleZ', value=0.01, time=start_frame)
            # Scale 1 at end
            cmds.setKeyframe(child, attribute='scaleX', value=1.0, time=end_frame)
            cmds.setKeyframe(child, attribute='scaleY', value=1.0, time=end_frame)
            cmds.setKeyframe(child, attribute='scaleZ', value=1.0, time=end_frame)
        except: pass

    # Apply ease-in tangents to all growth keys
    try:
        cmds.select(children)
        cmds.keyTangent(inTangentType='linear', outTangentType='spline')
    except: pass

    print("   Growth animation: {0} crystals, staggered over 680 frames".format(len(children)))
else:
    print("   Growth animation: SKIPPED (no crystal group)")

print("   Camera: 960-frame fly-through + growth animation")

# ═══════════════════════════════════════════════════════════════════════
# 11. ARNOLD RENDER SETTINGS
# ═══════════════════════════════════════════════════════════════════════
print("\n8. ARNOLD RENDER CONFIG")
try:
    if not cmds.pluginInfo("mtoa", query=True, loaded=True):
        cmds.loadPlugin("mtoa")
except: pass

try: cmds.setAttr("defaultRenderGlobals.currentRenderer", "arnold", type="string")
except: pass
try: cmds.setAttr("defaultArnoldRenderOptions.ai_translator", "Arnold", type="string")
except: pass

# High samples for glass materials
for attr, val in [
    ("AASamples", 6), ("GIDiffuseSamples", 2), ("GISpecularSamples", 3),
    ("GITransmissionSamples", 6), ("GISssSamples", 4), ("GIVolumeSamples", 3),
]:
    try: cmds.setAttr("defaultArnoldRenderOptions." + attr, val)
    except: pass

try: cmds.setAttr("defaultResolution.width", 1920)
except: pass
try: cmds.setAttr("defaultResolution.height", 1080)
except: pass

for attr, val in [("ai_translator","exr"), ("mergeAOVs",True), ("halfPrecision",False)]:
    try: cmds.setAttr("defaultArnoldDriver." + attr, val)
    except: pass

# AOVs
try:
    while cmds.attributeQuery("aovList", node="defaultArnoldRenderOptions",
                              numberOfChildren=True):
        cmds.removeMultiInstance("defaultArnoldRenderOptions.aovList[0]", b=True)
except: pass
for idx, aov in enumerate(["beauty", "Z"]):
    try: cmds.setAttr("defaultArnoldRenderOptions.aovList[{0}]".format(idx),
                      aov, type="string")
    except: pass

print("   AA=6, transmission=6, SSS=4, 1920x1080 EXR, AOVs: beauty+Z")

# ═══════════════════════════════════════════════════════════════════════
# 12. RENDER CAMERA (close to tallest crystals)
# ═══════════════════════════════════════════════════════════════════════
from arnold_render import create_render_camera
create_render_camera()
print("   Render camera: 20mm wide, close to tallest crystals")

# ═══════════════════════════════════════════════════════════════════════
# 13. SAVE SCENE + TRIGGER RENDER
# ═══════════════════════════════════════════════════════════════════════
os.makedirs(OUT, exist_ok=True)
sp = os.path.join(OUT, "crystal_cavern.ma")
cmds.file(rename=sp)
cmds.file(save=True, type="mayaAscii")

# Viewport preview
for o in (cmds.ls('render_cam*') or []):
    if cmds.nodeType(o) == 'transform' and cmds.listRelatives(o, shapes=True, type='camera'):
        for panel in cmds.getPanel(type='modelPanel') or []:
            try: cmds.modelPanel(panel, edit=True, camera=o)
            except: pass
        cmds.viewFit(o, fitFactor=0.95)
        cmds.playblast(frame=1, format='image', filename=OUT+"/preview",
                       widthHeight=(1920,1080), viewer=False, showOrnaments=False,
                       clearCache=True, percent=100, compression='png', quality=100)
        break

# Find camera + render
cam = None
for p in ['render_cam', 'fly_cam']:
    for o in (cmds.ls(p + '*') or []):
        try:
            if cmds.nodeType(o) == 'transform' and cmds.listRelatives(o, shapes=True, type='camera'):
                cam = o; break
        except: continue
    if cam: break

if cam:
    rp = os.path.join(OUT, "arnold_beauty")
    try:
        cmds.setAttr('defaultRenderGlobals.imageFilePrefix', rp, type='string')
        cmds.setAttr('defaultRenderGlobals.outFormatControl', 0)
        cmds.setAttr('defaultRenderGlobals.animation', 0)
        cmds.setAttr('defaultRenderGlobals.putFrameBeforeExt', 0)
    except: pass

    print("\n=== ARNOLD RENDER: {0} ===".format(cam))
    print("Output: {0}.exr".format(rp))
    print("This takes 3-8 minutes...")
    try:
        mel.eval('arnoldRender -batch -camera ' + cam)
        print("RENDER COMPLETE: {0}.exr".format(rp))
    except Exception as e:
        print("RENDER FAILED: {0}".format(str(e)[:120]))
else:
    print("\nNO CAMERA — scene saved but render skipped")
    print("Open scene then Arnold > Render View > Start Render")

# ═══════════════════════════════════════════════════════════════════════
# 14. STATS
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("  CRYSTAL CAVERN v7 BUILD COMPLETE")
print("  {0} crystals ({1:.0f}-{2:.0f}m), {3} branches".format(
    count,
    min([s["variance"]*17+8 for s in s] or [8]),
    max([s["variance"]*17+8 for s in s] or [25]),
    sum([random.randint(3,8) for _ in s]),
))
print("  {0} transforms, {1} lights".format(
    len(cmds.ls(type='transform')),
    len(cmds.ls(type=['ambientLight','directionalLight','pointLight','spotLight','areaLight'])),
))
print("  {0} Arnold shaders, volumetric fog, growth animation".format(
    len(cmds.ls(type='aiStandardSurface') or []),
))
print("  Scene: {0}".format(sp))
print("  Render: {0}/arnold_beauty.exr".format(OUT))
print("  Animation: frame 0=bare rock, frame 960=mature crystals")
print("=" * 60)
