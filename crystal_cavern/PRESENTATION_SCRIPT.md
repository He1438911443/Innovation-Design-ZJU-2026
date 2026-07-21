# Crystal Cavern — Pre-production Presentation Script
# 6-minute English presentation for 20 July 2026

---

## Slide 1: Title (10 seconds)

**Title**: Crystal Cavern — A Procedural Crystal Cave Generator
**Subtitle**: Maya Python Scripting for Animation
**Name**: [Your Name]
**Course**: Innovation Design for Future, ZJU, 2026

**Say**: "Good afternoon everyone. My project is Crystal Cavern — a procedural crystal cave generator built entirely in Maya Python. I work alone on this project."

---

## Slide 2: What This Project Does (30 seconds)

**Content**: Show reference images of real crystal caves (Naica Mine, Mexico) side by side with AI-generated target render.

**Say**: "The goal is simple: with one click, Maya generates an entire crystal cave — terrain, crystals, lighting, and a camera fly-through. No manual modeling. Everything is procedural. The algorithm creates a different cave every time, controlled by parameters like seed, density, and roughness."

**Why this structure wins**: 直接展示对比——真实晶洞 vs 算法生成的，老师立刻看到视觉目标。所有高分组的 PPT 都有这个"Before our project" vs "Our target"的对比页。

---

## Slide 3: Why Crystal Caves? (30 seconds)

**Say**: "I chose crystal caves for three reasons. First, no other group is doing minerals or geology — it's completely original within our cohort. Second, crystal growth follows clear mathematical rules: they grow outward along surface normals, branch at predictable angles, and form clusters. This makes them perfect for procedural generation. Third, crystals look stunning in Maya with the right lighting. Subsurface scattering and point lights make them glow from within."

---

## Slide 4: Reference Images & Visual Target (30 seconds)

**Visuals**: 
- Real crystal cave photography (Naica, Pulpi Geode)
- AI-generated concept art of the target aesthetic
- Annotated showing key visual elements we want to achieve

**Say**: "These are my reference images. On the left, the Naica crystal cave in Mexico — the crystals there are up to 12 meters long. On the right, AI-generated concept art showing the kind of atmosphere I want: dark cavern, glowing crystals in multiple colors, dramatic shadows. The key visual elements are: cluster formations, color variation, and subsurface illumination."

---

## Slide 5: Related Work & Algorithm Foundation (45 seconds)

**Show 3-4 key references with citations**:

| Algorithm | Paper | Our Use |
|-----------|-------|---------|
| Diamond-Square | Fournier, Fussell & Carpenter (1982) | Terrain generation |
| Poisson-disc sampling | Bridson (2007) | Crystal seed distribution |
| L-System branching | Prusinkiewicz & Lindenmayer (1990) | Crystal growth rules |
| Subsurface scattering | Jensen et al. (2001) | Lighting inspiration |

**Say**: "This project stands on four well-established algorithms. Diamond-Square for the cave terrain — it's the gold standard for procedural height maps. Poisson-disc sampling for distributing crystal seeds — it guarantees no two crystals are too close together, which looks much more natural than pure random. L-Systems for crystal branching — the same algorithm that generates realistic trees can generate realistic crystal clusters. And Jensen's subsurface scattering model inspired my lighting approach."

**Why this structure wins**: ReefSeed 组和 Mycelium City 组都用了这个"算法论文 → 我们的用途"的表格结构，老师当场点头。

---

## Slide 6: Algorithm Design — 5-Stage Pipeline (60 seconds)

**Show the pipeline flowchart**:

```
[Random Seed] -> [Diamond-Square Terrain] -> [Poisson-disc Seeds]
    -> [Crystal Growth along Normals] -> [Lighting & Fog] -> [Camera Fly-through]
```

**Say**: "The algorithm has five stages. Stage one — Diamond-Square generates the cave terrain from a random seed. Stage two — Poisson-disc sampling places crystal seeds on the terrain surface, avoiding clumping. Stage three — each seed grows a crystal formation outward along the surface normal, with height, width, branching, and color all controlled by parameters. Stage four — point lights in crystal colors create the subsurface scattering effect, plus volumetric fog for depth. Stage five — a camera rig animates a slow spiral fly-through."

---

## Slide 7: Code Structure (45 seconds)

**Show the modular file structure**:

```
crystal_cavern/
├── main.py              Entry point — runs the full pipeline
├── cave_terrain.py      Diamond-Square terrain (Fournier 1982)
├── crystal_seed.py      Poisson-disc distribution (Bridson 2007)
├── crystal_growth.py    Normal-extrusion + L-System branching
├── cave_lighting.py     Point lights + volumetric fog + camera
├── crystal_ui.py        Maya GUI parameter panel
└── README.md            Full documentation with AI usage log
```

**Say**: "The code is divided into six independent modules. Each module implements one algorithm, has its own test block, and can be developed and debugged separately. Every function has docstrings. Every algorithm used is cited in the comments."

**Why this structure wins**: ReefSeed 组 PPT 里用了完全一样的文件结构图，老师当场说这是个好的 code organization。

---

## Slide 8: GUI & Parameters (30 seconds)

**Show a screenshot of the Maya GUI panel**.

**Say**: "The GUI lets you control every stage without touching the code. Terrain seed, roughness, and size. Crystal density, size variance, and color seed. Lighting intensity. One click generates the entire cave. This satisfies the GUI requirement and makes the project reproducible and tunable — any parameter change produces a completely different cave."

---

## Slide 9: Implementation Status & Timeline (30 seconds)

**Show a checklist**:

| Milestone | Status | Target Date |
|-----------|--------|-------------|
| Terrain generation | Done | Jul 19 |
| Crystal seeding | Done | Jul 20 |
| Crystal growth algorithm | In progress | Jul 22 |
| Lighting system | In progress | Jul 23 |
| Camera animation | Planned | Jul 24 |
| GUI panel | Planned | Jul 25 |
| Final report (500 words) | Planned | Jul 26 |
| Final presentation | Planned | Jul 27 |

**Say**: "Here is my timeline. Terrain and seeding are done. Crystal growth and lighting are in progress. I plan to complete all coding by July 25, leaving two days for testing, rendering, and the final report."

---

## Slide 10: AI Ethics Topic (45 seconds)

**Topic**: *"Vibe Coding and the Academic Boundary: When AI Writes Procedural Generation Code, Who Is the Programmer?"*

**Say**: "For ethics, I chose a topic directly connected to this project. I used AI to help write the crystal growth algorithm — ChatGPT suggested the Poisson-disc approach, generated the Diamond-Square implementation, and helped debug Maya API calls. The ethical question is: when AI writes most of the code, where is the boundary between AI-assisted learning and AI-replaced thinking? I will review ZJU's academic integrity policy, compare it with overseas universities' AI policies, and analyze who owns algorithm choices made by AI."

**Why this structure wins**: SmokeFlow 组在 PPT 最后一页附上了所有的 AI prompt 原文——这是我们课程的一个明确评分点（老师说了 "document the process"）。

---

## Slide 11: AI Usage Documentation (30 seconds)

**Show a table of AI prompts used**:

| Tool | Purpose | Example Prompt |
|------|---------|---------------|
| ChatGPT | Algorithm selection | "What procedural algorithms are best for generating crystal cave terrain?" |
| ChatGPT | Code generation | "Write a Python implementation of Diamond-Square for Maya..." |
| ChatGPT | Debugging | "Why is cmds.polyNormalPerVertex returning empty?" |
| Midjourney | Concept art | "dark crystal cave, amethyst clusters, volumetric lighting, photorealistic" |

**Say**: "I documented every AI interaction. The AI suggested algorithms, generated code, and helped debug — but I verified every line, made all design decisions, and ensured every function works in Maya. The AI is a tool, not the author."

---

## Slide 12: Why This Project Should Get High Marks (30 seconds)

**Say**: "To conclude: this project hits every assessment criterion. Algorithm complexity — Diamond-Square plus Poisson-disc plus L-Systems, all properly cited. Code quality — six modules, full docstrings, clean structure. GUI — full parameter control panel. Visual impact — crystal subsurface lighting with volumetric fog. Innovation — no other group is doing mineral generation. And AI ethics — directly connected to the project's development process."

"Thank you. I'm happy to take questions."

---

## AI Prompts Log (for final report — keep updating throughout the project)

### Prompt 1: Algorithm Selection
```
I'm working on a Maya Python procedural generation project. I want to generate 
a crystal cave. What algorithms would work for: (1) cave terrain, (2) crystal 
placement on surfaces, (3) crystal growth along normals? Give me paper citations.
```

### Prompt 2: Diamond-Square Implementation
```
Write a Python implementation of the Diamond-Square algorithm for procedural 
terrain. The function should take width, depth, subdivisions, and seed as 
parameters, and return a 2D height map. Use maya.cmds to create and deform 
a polyPlane based on the height values.
```

### Prompt 3: Crystal Growth Visualization
```
I need to create crystal formations in Maya using Python. Each crystal should 
grow outward along a surface normal vector, with segments that get narrower 
toward the tip, random branching, and semi-transparent colored materials. 
Show me the cmds.polyCube approach with stacked segments.
```

### Prompt 4: Maya Lighting Setup
```
How do I create dramatic cave lighting in Maya using Python cmds? I want: 
dark ambient, point lights with colored glow near crystals, volumetric fog, 
and a key light simulating light from outside the cave.
```
