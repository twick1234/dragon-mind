# DragonMind Craft - iPad / iOS Build

## Overview

For iPad, DragonMind Craft uses **Godot Engine 4** which provides:
- Native iPad/iPhone app export
- Metal rendering for best iOS performance
- Touch controls optimized for iPad
- Full App Store distribution support

## Requirements

- macOS (required for iOS builds)
- Xcode 15+
- Godot Engine 4.2+ (download from https://godotengine.org)
- Apple Developer account (for device/App Store)
- iOS/iPadOS 16+

## Option A: Quick Start with Godot (Recommended)

1. **Download Godot 4**: https://godotengine.org/download
2. **Open the project**: File > Open > `ios/godot_project/`
3. **Export to iOS**: Project > Export > iOS
4. **Open Xcode**: Click "Export Project" button
5. **Run on iPad**: Connect iPad, select it in Xcode, click Run

## Option B: Use Unity

See `ios/unity_setup.md` for Unity-based iPad build instructions.

## Touch Controls (iPad)

| Action | Gesture |
|--------|---------|
| Look around | Right side: drag |
| Move | Left side joystick |
| Jump | Double tap left side |
| Break block | Tap (left side) |
| Place block | Long press |
| Inventory | Swipe up from bottom |
| Pause | Tap pause button (top right) |

## File Structure

```
ios/
├── godot_project/      ← Godot 4 project (open in Godot)
│   ├── project.godot
│   ├── scenes/
│   ├── scripts/
│   └── export_presets.cfg
├── xcode_wrapper/      ← Optional Xcode wrapper
└── README_iOS.md       ← This file
```
