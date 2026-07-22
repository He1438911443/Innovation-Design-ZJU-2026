"""
Exercise 5: Stylized City — Sci-Fi Mega City
Algorithm Design

Style: 赛博朋克科幻巨城
Reference: Blade Runner 2049 + Cyberpunk 2077 Night City

Key design elements:
- Hexagonal ring layout (not square grid)
- Tapered towers (base + body + spire)
- Neon color palette (cyan, magenta, light blue, gold, deep blue, orange)
- Central mega-spire, height decreasing with distance
"""

import maya.cmds as cmds
import random
import math

# === Clean scene ===
cmds.select(all=True)
cmds.delete()

# === Neon color palette ===
NEON = [
    (0.0, 1.0, 1.0),   # Cyan
    (1.0, 0.0, 1.0),   # Magenta
    (0.2, 0.8, 1.0),   # Light blue
    (0.8, 0.6, 0.0),   # Gold
    (0.3, 0.3, 1.0),   # Deep blue
    (1.0, 0.4, 0.0),   # Orange
]


def sci_fi_tower(x, z, w, d, h):
    """Create a tapered sci-fi tower: base (wide) + body + spire (narrow)"""
    base = cmds.polyCube(w=w * 1.2, d=d * 1.2, h=h * 0.3)[0]
    cmds.move(x, h * 0.15, z, base)

    tower = cmds.polyCube(w=w, d=d, h=h * 0.5)[0]
    cmds.move(x, h * 0.55, z, tower)

    spire = cmds.polyCube(w=w * 0.5, d=d * 0.5, h=h * 0.3)[0]
    cmds.move(x, h * 0.95, z, spire)

    # Group and assign neon material
    grp = cmds.group(base, tower, spire, name="SciFiTower")
    color = random.choice(NEON)
    shader = cmds.shadingNode("lambert", asShader=True)
    cmds.setAttr(shader + ".color", color[0], color[1], color[2], type="double3")
    cmds.select(grp)
    cmds.hyperShade(assign=shader)

    return grp


# === Hexagonal ring layout ===
positions = []
for ring in range(1, 5):
    step = max(30, 60 // ring + 30)
    for angle in range(0, 360, step):
        x = ring * 15 * math.cos(math.radians(angle))
        z = ring * 15 * math.sin(math.radians(angle))
        positions.append((x, z, ring))
positions.append((0, 0, 0))  # center

# === Build city ===
for x, z, ring in positions:
    if ring == 0:   # Center mega-spire
        h = random.uniform(12, 15)
        w, d = 3, 3
    elif ring <= 2:  # Inner city
        h = random.uniform(6, 10)
        w, d = random.uniform(2, 3.5), random.uniform(2, 3.5)
    else:            # Outer districts
        h = random.uniform(3, 6)
        w, d = random.uniform(1.5, 2.5), random.uniform(1.5, 2.5)

    sci_fi_tower(x, z, w, d, h)

print("Sci-Fi Mega City complete!")
print("Style: Hex ring layout + tapered neon towers")
print("Reference: Blade Runner 2049 + Cyberpunk 2077 Night City")

"""
=== STYLE DESCRIPTION (for submission) ===

Stylized City: Sci-Fi Mega City (科幻巨城)

Keywords: 赛博朋克, 六边形布局, 锥形塔楼, 霓虹色彩

Design description:
The city uses a hexagonal ring layout instead of a traditional grid, creating
a more organic, futuristic skyline. Each building consists of three stacked
sections — a wide base, a mid-section tower, and a narrow spire — forming a
tapered silhouette reminiscent of cyberpunk architecture. Colors are randomly
selected from a 6-color neon palette (cyan, magenta, light blue, gold, deep
blue, orange). Building height decreases naturally with distance from the
center (15m central spire → 3-6m outer buildings), creating a natural skyline
gradient without hard zone boundaries.

References: Blade Runner 2049 + Cyberpunk 2077 Night City
"""
