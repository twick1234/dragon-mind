#!/bin/bash
# =============================================================================
# DragonMind Craft - macOS Build Script
# Builds a .app bundle and .dmg installer for macOS
# Requirements: macOS, Python 3.9+, pip
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
APP_NAME="DragonMindCraft"
VERSION="1.0.0"
BUNDLE_ID="com.dragonmind.craft"
DIST_DIR="$SCRIPT_DIR/dist"
BUILD_DIR="$SCRIPT_DIR/build_tmp"

echo "=============================================="
echo " DragonMind Craft - macOS Builder v${VERSION}"
echo "=============================================="
echo ""

# Check for macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "ERROR: This script must be run on macOS."
    echo "For Linux/Windows builds, use the platform-specific scripts."
    exit 1
fi

# Check Python
PYTHON="python3"
if ! command -v $PYTHON &>/dev/null; then
    echo "ERROR: Python 3 not found. Install from https://python.org"
    exit 1
fi
echo "Python: $($PYTHON --version)"

# Create virtual environment
echo ""
echo "Setting up Python virtual environment..."
cd "$PROJECT_DIR"
$PYTHON -m venv venv_build
source venv_build/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip -q
pip install ursina pyinstaller pillow numpy -q

# Generate textures
echo "Pre-generating block textures..."
cd "$PROJECT_DIR/src"
python texture_gen.py
cd "$PROJECT_DIR"

# Generate icon
echo "Generating app icon..."
python3 - <<'ICON_SCRIPT'
import os
from PIL import Image, ImageDraw

def make_icon(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Green background (grass block top)
    draw.rectangle([0, 0, size-1, size*0.6], fill=(85, 130, 50, 255))
    # Brown bottom (dirt)
    draw.rectangle([0, int(size*0.6), size-1, size-1], fill=(120, 80, 40, 255))
    # Letter D
    fw = size // 8
    draw.rectangle([fw, fw, fw*2, size-fw], fill=(255, 255, 255, 220))
    draw.rectangle([fw, fw, size-fw*2, fw*2], fill=(255, 255, 255, 220))
    draw.rectangle([fw, size-fw*2, size-fw*2, size-fw], fill=(255, 255, 255, 220))
    draw.rectangle([size-fw*2, fw*2, size-fw, size-fw*2], fill=(255, 255, 255, 220))
    return img

os.makedirs("build/icons.iconset", exist_ok=True)
sizes = [16, 32, 64, 128, 256, 512, 1024]
for s in sizes:
    img = make_icon(s)
    img.save(f"build/icons.iconset/icon_{s}x{s}.png")
    if s <= 512:
        img2 = make_icon(s*2)
        img2.save(f"build/icons.iconset/icon_{s}x{s}@2x.png")
print("Icon files generated")
ICON_SCRIPT

# Convert to .icns
if command -v iconutil &>/dev/null; then
    iconutil -c icns build/icons.iconset -o build/AppIcon.icns 2>/dev/null && echo "Created AppIcon.icns" || echo "iconutil failed, using PNG fallback"
fi

# PyInstaller spec
echo ""
echo "Creating PyInstaller spec..."
cat > "$BUILD_DIR/../DragonMindCraft.spec" <<SPEC
# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None
assets_path = os.path.join('..', 'assets')
src_path = os.path.join('..', 'src')

a = Analysis(
    ['../src/main.py'],
    pathex=['../src'],
    binaries=[],
    datas=[
        ('../assets/textures', 'assets/textures'),
    ],
    hiddenimports=[
        'ursina',
        'panda3d.core',
        'panda3d_simplepbr',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFilter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DragonMindCraft',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DragonMindCraft',
)

app = BUNDLE(
    coll,
    name='DragonMindCraft.app',
    icon='build/AppIcon.icns',
    bundle_identifier='com.dragonmind.craft',
    info_plist={
        'CFBundleDisplayName': 'DragonMind Craft',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'NSSupportsAutomaticGraphicsSwitching': True,
        'NSPrincipalClass': 'NSApplication',
        'LSMinimumSystemVersion': '10.14',
        'NSHumanReadableCopyright': '© 2024 DragonMind',
    },
)
SPEC

# Build with PyInstaller
echo "Building app bundle (this may take a few minutes)..."
pyinstaller DragonMindCraft.spec \
    --distpath "$DIST_DIR" \
    --workpath "$BUILD_DIR" \
    --noconfirm \
    --clean

echo ""
echo "App bundle built: $DIST_DIR/DragonMindCraft.app"

# Create DMG
echo ""
echo "Creating DMG installer..."
DMG_PATH="$DIST_DIR/${APP_NAME}-${VERSION}-macOS.dmg"
TEMP_DMG="$DIST_DIR/temp.dmg"
VOLUME_NAME="DragonMind Craft ${VERSION}"

# Check for create-dmg tool
if command -v create-dmg &>/dev/null; then
    create-dmg \
        --volname "$VOLUME_NAME" \
        --volicon "build/AppIcon.icns" \
        --window-pos 200 120 \
        --window-size 600 400 \
        --icon-size 100 \
        --icon "DragonMindCraft.app" 150 185 \
        --hide-extension "DragonMindCraft.app" \
        --app-drop-link 450 185 \
        "$DMG_PATH" \
        "$DIST_DIR/" \
    && echo "DMG created: $DMG_PATH" \
    || echo "create-dmg failed, using hdiutil fallback"
fi

# hdiutil fallback
if [[ ! -f "$DMG_PATH" ]]; then
    hdiutil create \
        -volname "$VOLUME_NAME" \
        -srcfolder "$DIST_DIR/DragonMindCraft.app" \
        -ov -format UDZO \
        "$DMG_PATH" \
    && echo "DMG created: $DMG_PATH"
fi

deactivate
echo ""
echo "=============================================="
echo " Build complete!"
echo " App:  $DIST_DIR/DragonMindCraft.app"
echo " DMG:  $DMG_PATH"
echo ""
echo " To install:"
echo " 1. Open the .dmg file"
echo " 2. Drag DragonMindCraft to Applications"
echo " 3. Right-click > Open (first time, to bypass Gatekeeper)"
echo "=============================================="
