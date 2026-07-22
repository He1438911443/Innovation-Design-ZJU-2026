# Crystal Cavern — Final Renders

Two parameter sets, each a completely different cave:

## Scene 1: Amethyst Cavern
| Parameter | Value |
|-----------|-------|
| Seed | 2026 |
| Density | 56 crystals |
| Fog | 0.008 |
| Style | Purple amethyst, medium roughness |
| Render | 1920×1080 Arnold EXR |

## Scene 2: Ruby Vault  
| Parameter | Value |
|-----------|-------|
| Seed | 7777 |
| Density | 56 crystals |
| Fog | 0.008 |
| Style | Deep red ruby, high roughness |
| Render | 1920×1080 Arnold EXR |

## Key Visual Features
- Hexagonal prism crystals (polyCylinder sx=6) with L-system spherical branching
- 10 gem types with Arnold transmission + SSS + coat + cloudy noise texture
- Diamond-Square terrain inside sphere-shell cave
- 35 stalactites, 3-layer lighting (dome + key + rim + 20 crystal glows)
- DOF camera f/3.2, 35mm, ai_exposure=3.0
- Volumetric fog (aiAtmosphereVolume)
- Growth animation (0→1 scale over 720 frames)

Generated: 2026-07-21
