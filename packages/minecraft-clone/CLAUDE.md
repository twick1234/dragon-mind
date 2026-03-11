# DragonMind Craft — CLAUDE.md
# Project memory for Claude Code sessions

## What this is

A fully-playable **Minecraft clone** called "DragonMind Craft", built in Python
(Ursina/Panda3D) for macOS/Windows, and Godot 4 for iPad/iOS.

---

## Current status: COMPLETE ✅

All core systems are built and tested. The game runs. Installers are ready to build.

---

## What has been done

### Game engine (Python / Ursina)
- `src/constants.py` — all game constants, block IDs, colors, tuning values
- `src/world.py` — Perlin noise terrain gen, biomes, caves, ores, trees, chunk system
- `src/player.py` — physics (gravity/collision/jumping/swimming), raycast, inventory
- `src/renderer.py` — face-culled chunk meshes, VoxelBlock entities, HUD, break effects
- `src/ui.py` — main menu, pause menu, inventory screen, settings screen
- `src/texture_gen.py` — procedural block textures (PIL), generated at launch
- `src/main.py` — game loop, state machine (MAIN_MENU/PLAYING/PAUSED/INVENTORY)

### Blocks (20 types)
Grass, Dirt, Stone, Sand, Water, Wood, Leaves, Cobblestone, Planks, Glass,
Bedrock, Coal Ore, Iron Ore, Gold Ore, Diamond Ore, Gravel, Snow, Ice, Cactus, Lava

### World generation features
- Perlin noise heightmap (4 octaves)
- 3 biomes: plains (grass/trees), desert (sand/cactus), tundra (snow)
- Cave systems (3D noise carving)
- Ore veins at depth (coal→iron→gold→diamond deeper)
- Auto-generated trees with trunks + leaf canopies
- Bedrock floor, lava at cave bottoms

### Player features
- WASD + mouse look, sprint (Shift), fly mode toggle (F)
- Gravity, collision AABB, jumping, swimming in water
- Raycast block break (LMB) and place (RMB) up to 5 blocks reach
- 9-slot hotbar + 27-slot inventory with drag-and-drop UI
- Number keys 1–9 and scroll wheel for hotbar

### macOS installer
- `build/build_macos.sh` — run on macOS to build `.app` + `.dmg`
- Uses PyInstaller to bundle Python + Panda3D into a standalone `.app`
- Creates DMG via `hdiutil` (or `create-dmg` if installed)
- Output: `build/dist/DragonMindCraft-1.0.0-macOS.dmg`

### Windows installer
- `build/build_windows.bat` — run on Windows to build `.exe` folder + Setup.exe
- Uses PyInstaller for the standalone build
- Uses NSIS (`installer.nsi`) for the professional Setup.exe installer
  - Welcome / License / Components / Directory / Progress / Finish pages
  - Desktop + Start Menu shortcuts
  - Add/Remove Programs registry entry + uninstaller
- Output: `build/dist/DragonMindCraft-1.0.0-Windows-Setup.exe`
- NSIS download: https://nsis.sourceforge.io/Download

### iPad / iOS (Godot 4)
- `ios/godot_project/` — open in Godot Engine 4.2+
- `scripts/world_generator.gd` — GDScript Perlin noise world gen (FastNoiseLite)
- `scripts/chunk_renderer.gd` — face-culled mesh builder using SurfaceTool
- `scripts/player_controller.gd` — movement, touch joystick, block interaction
- `scripts/game_world.gd` — chunk load/unload manager
- `scripts/touch_hud.gd` — on-screen joystick + buttons for iPad
- Export: Project → Export → iOS → connect iPad → Run (requires macOS + Xcode 15)

---

## How to run right now (no build needed)

```bash
pip3 install ursina pillow
cd packages/minecraft-clone/src
python3 main.py
```

---

## How to build installers

**macOS** (run on a Mac):
```bash
chmod +x packages/minecraft-clone/build/build_macos.sh
packages/minecraft-clone/build/build_macos.sh
```

**Windows** (run on Windows, double-click or cmd):
```
packages\minecraft-clone\build\build_windows.bat
```
Install NSIS first for the Setup.exe: https://nsis.sourceforge.io/Download

---

## Branch

All work is on: `claude/minecraft-clone-game-E5BLo`

---

## Dependencies

- Python 3.9+
- ursina >= 7.0.0 (Panda3D backend)
- Pillow >= 10.0.0 (texture generation)
- PyInstaller >= 6.0.0 (bundling)
- NSIS 3.x (Windows installer, optional)
- Godot Engine 4.2+ (iPad build)
- Xcode 15+ on macOS (iPad deploy)

---

## Known limitations / potential next steps

- Chunk rebuild on block place/break is brute-force (rebuilds 3x3 chunks) — could be optimised
- No save/load system yet
- No mob/enemy AI yet
- No crafting system yet
- Render distance >6 may be slow on older hardware
- iPad Godot project needs textures wired up (currently uses vertex colours)
