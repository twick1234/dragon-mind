# DragonMind Craft 🎮

A fully-featured Minecraft-inspired voxel game, installable on **macOS** and **iPad**.

## Features

- **Procedural world generation** — infinite terrain with biomes (plains, desert, tundra)
- **20 block types** — grass, dirt, stone, sand, water, wood, leaves, ores (coal, iron, gold, diamond), glass, planks, lava, snow, ice, cactus, bedrock
- **Caves** — underground cave systems with lava at the bottom
- **Trees** — auto-generated trees with trunks and leaf canopies
- **Ore veins** — coal, iron, gold, diamond at different depths
- **Face-culled rendering** — only visible faces are drawn
- **Player physics** — gravity, jumping, collision detection, swimming
- **Fly mode** — toggle with `F` for creative exploration
- **Block break/place** — left click to break, right click to place
- **Inventory system** — 9-slot hotbar + 27-slot main inventory
- **Procedural textures** — all textures generated at runtime (no external assets required)
- **HUD** — crosshair, hotbar, block name, coordinates, mode indicator
- **Menus** — main menu, pause menu, settings (render distance), inventory screen
- **macOS app bundle** — `.app` + `.dmg` installer via PyInstaller
- **iPad/iOS** — Godot 4 project with Metal rendering + touch controls

---

## macOS Installation

### Option A: Pre-built (if provided)
1. Open `DragonMindCraft.dmg`
2. Drag **DragonMindCraft** to `Applications`
3. Right-click > **Open** (first launch only, to bypass Gatekeeper)

### Option B: Build from source (macOS)

```bash
# 1. Install Python 3.9+ if needed
brew install python

# 2. Clone / download this repo
cd packages/minecraft-clone

# 3. Build the .app and .dmg
chmod +x build/build_macos.sh
./build/build_macos.sh
```

The script will:
- Create a virtual environment
- Install all Python dependencies
- Generate procedural textures
- Bundle with PyInstaller into `DragonMindCraft.app`
- Create a `DragonMindCraft-1.0.0-macOS.dmg` installer

### Run without building

```bash
pip3 install ursina pillow
cd src
python3 main.py
```

---

## Controls (macOS / Desktop)

| Key | Action |
|-----|--------|
| `W A S D` | Move |
| `Mouse` | Look around |
| `Space` | Jump |
| `Left Shift` | Sprint |
| `Left Click` | Break block |
| `Right Click` | Place block |
| `Scroll Wheel` | Cycle hotbar |
| `1 – 9` | Select hotbar slot |
| `F` | Toggle fly mode |
| `Tab` | Open inventory |
| `Esc` | Pause menu |

---

## iPad / iOS Installation

The iPad version uses **Godot Engine 4** for native Metal rendering and touch controls.

### Requirements
- macOS computer (required for iOS builds)
- Xcode 15+ (free from Mac App Store)
- [Godot Engine 4.2+](https://godotengine.org/download) (free)
- Apple Developer account (free for personal device, $99/yr for App Store)

### Steps

1. **Download Godot 4** from https://godotengine.org
2. **Open the project**: File → Open → select `ios/godot_project/`
3. **Configure iOS export**:
   - Project → Export → Add iOS preset
   - Fill in your Apple Team ID
4. **Connect your iPad** via USB
5. **Click "Run on Device"** in Godot
   - Or export as Xcode project → open in Xcode → click Run

### Touch Controls (iPad)

| Gesture | Action |
|---------|--------|
| Left side joystick | Move |
| Right side drag | Look around |
| `⬆` button | Jump |
| `💥` button | Break block |
| `🧱` button | Place block |
| `✈` button | Toggle fly |
| `🎒` button | Inventory |
| Hotbar row | Select block |

---

## Project Structure

```
minecraft-clone/
├── src/
│   ├── main.py           ← Entry point, game loop
│   ├── world.py          ← World generation & chunk management
│   ├── player.py         ← Player physics, inventory, raycast
│   ├── renderer.py       ← 3D rendering with Ursina/Panda3D
│   ├── ui.py             ← Menus & HUD
│   ├── texture_gen.py    ← Procedural texture generation
│   └── constants.py      ← All game constants
├── assets/
│   └── textures/         ← Auto-generated block textures (PNG)
├── build/
│   ├── build_macos.sh    ← macOS .app + .dmg builder
│   └── build_windows.bat ← Windows .exe builder
├── ios/
│   ├── godot_project/    ← Godot 4 project for iPad
│   │   ├── project.godot
│   │   ├── scripts/      ← GDScript source
│   │   └── export_presets.cfg
│   └── README_iOS.md
└── requirements.txt
```

---

## Technical Details

### Terrain Generation
- **Perlin noise** with 4 octaves for natural-looking hills
- **Biome system**: plains (grass/trees), desert (sand/cacti), tundra (snow)
- **Cave carving**: 3D noise for underground cave systems
- **Ore distribution**: depth-based probability for coal, iron, gold, diamond

### Rendering
- **Ursina Engine** (Panda3D backend) for macOS/Windows
- **Godot 4 + Metal** for iOS/iPad
- **Face culling**: only surfaces visible from outside are rendered
- **Chunk-based**: 16×64×16 blocks per chunk, loaded dynamically

### Performance
- Render distance adjustable (2–8 chunks)
- Chunks loaded/unloaded as player moves
- Procedural textures generated once at startup

---

## License

MIT License — use freely for personal and commercial projects.
