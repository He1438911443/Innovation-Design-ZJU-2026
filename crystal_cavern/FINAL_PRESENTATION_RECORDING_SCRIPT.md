# Crystal Cavern — Final Recording Script (3:40–4:10)

## Recording setup

Record at 1920×1080 with Maya visible. Start with `crystal_ui_v3.create_ui()`. Keep the project folder and the Maya Script Editor hidden. Record the narration separately if possible.

## 0:00–0:25 — Problem and result

"Hello, I am He Xiangrong. Crystal Cavern is a Maya Python generator for a walkable crystal cave. One seed creates a new tunnel route, crystal ecosystem, lighting composition and fly-through animation."

Show a real reference briefly, then a rendered tunnel frame.

## 0:25–1:10 — One-click generation

"Here is the Maya interface. I change the seed, then press Generate. The system first creates a tunnel graph: a main route, a chamber, and a branch. It sweeps irregular rings along that graph to build an inward-facing cave surface."

Change **Seed** and press **Generate**. Show Outliner groups: `CCV10_tunnel_cave`, `CCV10_lsystem_crystals`, and `CCV10_tunnel_cam`.

## 1:10–2:00 — Algorithm proof: tunnel + L-system

"The same centreline is reused three times: as cave topology, as wall-seed coordinates, and as the camera route. This guarantees that the camera travels inside a real tunnel rather than orbiting an open terrain."

"For crystal growth I use the recursive rule F becomes F, plus one positive and one negative branch: F → F[+F][-F]. It expands twice. Each generated cluster contains a main hexagonal crystal, two branches, and four smaller second-order crystals."

Select one `CCV10_cluster_*` group and show `lsystemRule` / `lsystemDepth` in the Attribute Editor.

## 2:00–2:45 — Animation and visual choices

"The clusters grow sequentially at the start of the timeline. After the growth reveal, the camera follows the tunnel path through the chamber and toward the deep blue exit. Materials use transmission, specular facets and restrained emission. Sparse entrance, chamber, and depth lights preserve darkness and scale."

Press Play; scrub to the chamber and show one Arnold render.

## 2:45–3:30 — AI ethics review and disclosure

"My AI ethics topic is authorship, transparency and environmental cost in AI-assisted procedural design. AI assisted research, API patterns and debugging, but I chose the design constraints, tested every Maya iteration, and documented the use. I also use low-resolution look-dev renders before final rendering to reduce unnecessary compute. AI is an assistant, not an undisclosed author."

Show the AI-use table and ethics slide.

## 3:30–4:00 — Close

"In summary, changing one seed changes an entire navigable cave: its route, chamber, recursive crystal formations and camera animation. Thank you."

Show the final render and title card for three seconds.
