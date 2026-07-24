# Crystal Cavern — Final Presentation Script

**Target length:** approximately 6 minutes  
**Presenter:** He Xiangrong  
**Course:** Innovation Design for Future, ZJU 2026

## Slide 1

Good afternoon, Professor Yang. My project is Crystal Cavern, a Python-driven procedural generator running inside Maya. The goal is simple: a user changes a seed, presses Generate, and receives a new glowing tunnel cave with crystals, lighting, a camera path, and growth animation. This final version focuses on one question: can a procedural result feel designed rather than mechanically generated?

## Slide 2

The north-star experience is now measurable. Starting from an empty Maya scene, version twenty-six builds the full cave in 7.9 seconds, well below my 30-second target. The system contains four recursive hero clusters and outputs a 5.2-second presentation-ready growth fly-through. The important change is that this is no longer a terrain demo. Geometry, look development, animation, and rendering now support one coherent cave experience.

## Slide 3

This slide shows the gap I used to guide iteration. The real references are enclosed tunnels filled with long translucent crystals, not an open landscape with spikes. I therefore extracted three visual requirements: a readable tunnel volume, clustered crystals with thickness and internal variation, and dramatic light moving through the mineral body. On the right, the Arnold result now reproduces those qualities while remaining procedurally generated.

## Slide 4

The teacher’s first concern was how a terrain method could produce a tunnel. I replaced the terrain-first logic with a seeded spatial centreline. Twenty-five sections define a curved route. Around each section, the algorithm builds an irregular inward-facing ring, and adjacent rings form the tunnel mesh. A separate ellipsoidal chamber creates the hero room, with entry and exit portals. The same graph also drives the camera and light positions, so every seed remains internally consistent.

## Slide 5

The second concern was that the crystals looked like spikes rather than an L-system. The explicit grammar is F becomes F, plus F, minus F. At depth two, one trunk recursively creates child branches with a sixty-degree hexagonal bias. More importantly, I corrected the animation pivot: every cluster now scales from its own mineral root. In this sequence, the clusters emerge from the rock bed instead of flying in from the world origin.

## Slide 6

The complete system is a five-stage pipeline. A seed first creates the tunnel graph. The graph becomes the tube and chamber. Surface samples place wall crystals, while the hero room receives recursive clusters. Look development then adds quartz materials, internal inclusions, fractures, colored lights, and fog. Finally, the system creates camera animation, an Arnold-ready scene, still renders, and the presentation video. Each stage is deterministic, so changing the seed produces a repeatable new cave.

## Slide 7

Material realism required more than transparency. The outer shell uses an Arnold Standard Surface with quartz-like IOR and controlled transmission. Alternating face materials break the uniform plastic look. A milky inner core gives optical thickness, and two thin internal planes create fracture highlights. Subtle three-dimensional noise varies roughness without destroying the flat crystal facets. The final lighting separates a cool key, violet rim, warm internal accent, and low ambient cave fill.

## Slide 8

The implementation is still modular. The original seven course modules handle terrain, seed distribution, crystal growth, lighting, UI, Arnold rendering, and batch output. The final tunnel_cavern integration module connects them into the current product experience. The code has docstrings, citations, deterministic seeds, and a single build entry point. This separation allowed me to change the cave representation without rewriting the material, UI, or rendering layers.

## Slide 9

The Maya interface remains the user-facing control surface. The user chooses the seed, density, crystal and lighting parameters, then presses Generate. Progress feedback prevents Maya from appearing frozen. Render Still switches to the Arnold camera and output settings. The key usability result is that the final generator does not require manual modeling after generation; creative variation happens through parameters and seed selection.

## Slide 10

These are the final outputs. The left image is a 1280 by 720 Arnold render showing the hero chamber, faceted transmission, inclusions, and colored rim light. The right side plays the embedded growth fly-through. For viewport playback, I hide only the Arnold internal-detail proxy meshes because real-time Maya does not reproduce the same refraction depth. They remain enabled in the Arnold still, so the preview and final render use the same generated crystal geometry.

## Slide 11

For the required ethics investigation, I chose authorship and accountability in AI-assisted procedural design. UNESCO emphasizes transparency, traceability, human oversight, and responsibility. In this project, the ethical risk is not that AI writes code; it is that I could present unverified AI output as my own technical knowledge. My safeguards are an iteration log, explicit disclosure of AI contributions, comparison against references, code review, and validation inside Maya. I remain responsible for every visual and technical claim.

## Slide 12

To conclude, the project now answers the original question. It generates an enclosed tunnel cave rather than a height field, demonstrates a real recursive L-system rather than isolated spikes, and produces crystals with faceted transmission, inclusions, fractures, lighting, and rooted growth. The build completes in under eight seconds, while Arnold provides the final cinematic quality. The next step would be a longer fully rendered fly-through. Thank you, and I welcome your questions.

## Presentation operation cue

On Slide 10, allow the embedded growth animation to play once. If PowerPoint blocks animated playback, open the backup MP4:

`crystal_cavern/renders/tunnel_v10/crystal_cavern_growth_flythrough_FINAL_v27.mp4`

## Likely Q&A

**How is this a cave rather than terrain?**  
The current generator constructs an inward-facing tube along a seeded 3D centreline, then joins it to an explicit chamber shell with entry and exit portals.

**Where is the L-system?**  
Each hero cluster applies `F → F[+F][−F]` recursively to depth two. Branch direction uses a 60-degree hexagonal azimuth bias, and animation pivots are placed at the mineral roots.

**Why is the animation not fully Arnold rendered?**  
The final stills use Arnold for optical accuracy. The presentation animation uses Maya Viewport 2.0 for reliable real-time delivery; Arnold-only internal proxy meshes are hidden in that preview but remain enabled for final rendering.

**What did AI contribute?**  
AI assisted code generation, debugging, refactoring and presentation iteration. I defined the target, selected references, rejected failed versions, verified the code in Maya and remain responsible for the final claims.
