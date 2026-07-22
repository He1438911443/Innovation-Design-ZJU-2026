"""
Exercise 3: Build a City (Maya Python Script)
要求: 市中心高楼 + 边缘低楼，3组建筑模型随机选取
"""

import maya.cmds as cmds
import random

# === Clean scene ===
cmds.select(all=True)
cmds.delete()

# === 3 building groups ===
GROUP_1 = {"tall": 5, "mid": 3, "low": 2, "color": (0.2, 0.4, 0.6)}    # Blue
GROUP_2 = {"tall": 6, "mid": 4, "low": 2.5, "color": (0.8, 0.6, 0.3)}  # Gold
GROUP_3 = {"tall": 4.5, "mid": 3.5, "low": 1.5, "color": (0.6, 0.2, 0.2)}  # Red

GROUPS = [GROUP_1, GROUP_2, GROUP_3]


def create_building(x, z, width, depth, height, color):
    """Create a single building with material"""
    building = cmds.polyCube(w=width, d=depth, h=height)[0]
    cmds.move(x, height / 2, z, building)

    shader = cmds.shadingNode("lambert", asShader=True)
    cmds.setAttr(shader + ".color", color[0], color[1], color[2], type="double3")
    cmds.select(building)
    cmds.hyperShade(assign=shader)
    return building


# === Grid parameters ===
GRID_SIZE = 7       # 7x7 grid
SPACING = 12        # space between buildings
CENTER = (GRID_SIZE - 1) / 2
MAX_DIST = CENTER * 2

print("Building the city...")

for row in range(GRID_SIZE):
    for col in range(GRID_SIZE):
        dist = abs(row - CENTER) + abs(col - CENTER)

        # Randomly pick a building group
        group = random.choice(GROUPS)

        # Height decreases with distance from center
        if dist <= 2:           # Downtown — tallest
            height = group["tall"] * (0.7 + random.uniform(0, 0.3))
            width, depth = random.uniform(3, 5), random.uniform(3, 5)
        elif dist <= 4:         # Midtown
            height = group["mid"] * (0.7 + random.uniform(0, 0.3))
            width, depth = random.uniform(2, 4), random.uniform(2, 4)
        else:                   # Outskirts — shortest
            height = group["low"] * (0.7 + random.uniform(0, 0.3))
            width, depth = random.uniform(2, 3), random.uniform(2, 3)

        x = col * SPACING
        z = row * SPACING
        create_building(x, z, width, depth, height, group["color"])

print(f"City built! {GRID_SIZE * GRID_SIZE} buildings created.")
print("Center: tall towers | Edge: low buildings")
print("3 building groups randomly assigned per location")

