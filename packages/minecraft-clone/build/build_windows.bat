@echo off
REM =============================================================================
REM DragonMind Craft - Windows Build Script
REM Produces:
REM   dist\DragonMindCraft\DragonMindCraft.exe       (standalone folder)
REM   dist\DragonMindCraft-1.0.0-Windows-Setup.exe   (NSIS installer .exe)
REM Requirements: Python 3.9+  |  NSIS 3.x (https://nsis.sourceforge.io)
REM =============================================================================

setlocal enabledelayedexpansion

set APP_NAME=DragonMindCraft
set VERSION=1.0.0
set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%SCRIPT_DIR%..
set DIST_DIR=%SCRIPT_DIR%dist
set BUILD_TMP=%SCRIPT_DIR%build_tmp

echo ==============================================
echo  DragonMind Craft - Windows Builder v%VERSION%
echo ==============================================
echo.

REM ---- Check Python ----
where python >/dev/null 2>&1
if errorlevel 1 (
    echo ERROR: Python not found.
    echo Install Python 3.9+ from https://www.python.org/downloads/
    pause & exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo Python: %%v

REM ---- Virtual environment ----
echo.
echo Setting up virtual environment...
cd /d "%PROJECT_DIR%"
if not exist venv_build (
    python -m venv venv_build
    if errorlevel 1 ( echo ERROR: Failed to create venv & pause & exit /b 1 )
)
call venv_build\Scripts\activate.bat

REM ---- Dependencies ----
echo Installing dependencies...
pip install --upgrade pip -q
pip install ursina pyinstaller pillow numpy -q
if errorlevel 1 ( echo ERROR: pip install failed & pause & exit /b 1 )

REM ---- Generate textures ----
echo Generating block textures...
cd src
python texture_gen.py
if errorlevel 1 ( echo ERROR: texture generation failed & pause & exit /b 1 )
cd ..

REM ---- Generate icon ----
echo Generating app icon...
python -c "from PIL import Image, ImageDraw; import os; os.makedirs('assets', exist_ok=True); img = Image.new('RGBA', (256,256), (0,0,0,0)); d = ImageDraw.Draw(img); d.rectangle([0,0,255,153], fill=(85,130,50,255)); d.rectangle([0,154,255,255], fill=(120,80,40,255)); fw=32; d.rectangle([fw,fw,fw*2,256-fw], fill=(255,255,255,220)); d.rectangle([fw,fw,256-fw*2,fw*2], fill=(255,255,255,220)); d.rectangle([fw,256-fw*2,256-fw*2,256-fw], fill=(255,255,255,220)); d.rectangle([256-fw*2,fw*2,256-fw,256-fw*2], fill=(255,255,255,220)); img.save('assets/icon.png'); print('icon.png saved')"
python -c "from PIL import Image; img = Image.open('assets/icon.png').convert('RGBA'); img.save('assets/icon.ico', format='ICO', sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)]); print('icon.ico saved')"

REM ---- PyInstaller build ----
echo.
echo Building executable with PyInstaller...
mkdir "%DIST_DIR%" 2>/dev/null
mkdir "%BUILD_TMP%" 2>/dev/null

pyinstaller --noconfirm --clean ^
    --name DragonMindCraft ^
    --windowed ^
    --icon assets\icon.ico ^
    --distpath "%DIST_DIR%" ^
    --workpath "%BUILD_TMP%" ^
    --add-data "assets\textures;assets\textures" ^
    --hidden-import ursina ^
    --hidden-import panda3d.core ^
    --hidden-import panda3d_simplepbr ^
    --hidden-import PIL ^
    --hidden-import PIL.Image ^
    --hidden-import PIL.ImageDraw ^
    --hidden-import PIL.ImageFilter ^
    src\main.py

if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    call venv_build\Scripts\deactivate.bat
    pause & exit /b 1
)

echo.
echo Standalone build: %DIST_DIR%\DragonMindCraft\DragonMindCraft.exe

REM ---- Generate LICENSE if missing ----
if not exist "LICENSE.txt" (
    echo MIT License > LICENSE.txt
    echo. >> LICENSE.txt
    echo Copyright (c) 2024 DragonMind >> LICENSE.txt
)

REM ---- NSIS installer ----
echo.
where makensis >/dev/null 2>&1
if not errorlevel 1 (
    echo Building NSIS installer...
    makensis /V2 build\installer.nsi
    if errorlevel 1 (
        echo WARNING: NSIS build failed. Standalone .exe still available.
    ) else (
        echo Installer: %DIST_DIR%\DragonMindCraft-%VERSION%-Windows-Setup.exe
    )
) else (
    echo NOTE: NSIS not found - skipping installer.
    echo       Install NSIS from https://nsis.sourceforge.io to produce a Setup.exe
    echo       Then re-run this script.
)

call venv_build\Scripts\deactivate.bat

echo.
echo ==============================================
echo  Build complete!
echo.
echo  Standalone:  %DIST_DIR%\DragonMindCraft\DragonMindCraft.exe
if exist "%DIST_DIR%\DragonMindCraft-%VERSION%-Windows-Setup.exe" (
    echo  Installer:   %DIST_DIR%\DragonMindCraft-%VERSION%-Windows-Setup.exe
)
echo.
echo  To create a Setup.exe installer:
echo    1. Install NSIS: https://nsis.sourceforge.io/Download
echo    2. Re-run this script
echo ==============================================
pause
