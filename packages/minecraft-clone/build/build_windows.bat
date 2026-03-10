@echo off
REM =============================================================================
REM DragonMind Craft - Windows Build Script
REM Builds an .exe installer for Windows
REM Requirements: Python 3.9+, pip
REM =============================================================================

setlocal

set APP_NAME=DragonMindCraft
set VERSION=1.0.0
set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%SCRIPT_DIR%..
set DIST_DIR=%SCRIPT_DIR%dist

echo ==============================================
echo  DragonMind Craft - Windows Builder v%VERSION%
echo ==============================================
echo.

REM Check Python
where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install from https://python.org
    exit /b 1
)

REM Virtual environment
echo Setting up virtual environment...
cd /d "%PROJECT_DIR%"
python -m venv venv_build
call venv_build\Scripts\activate.bat

REM Install deps
echo Installing dependencies...
pip install --upgrade pip -q
pip install ursina pyinstaller pillow numpy -q

REM Generate textures
echo Generating textures...
cd src
python texture_gen.py
cd ..

REM Build
echo Building executable...
pyinstaller --noconfirm --clean ^
    --name DragonMindCraft ^
    --windowed ^
    --distpath "%DIST_DIR%" ^
    --add-data "assets/textures;assets/textures" ^
    --hidden-import ursina ^
    --hidden-import panda3d.core ^
    --hidden-import PIL ^
    --hidden-import PIL.Image ^
    src\main.py

echo.
echo Build complete!
echo Output: %DIST_DIR%\DragonMindCraft\DragonMindCraft.exe

REM Create NSIS installer if available
where makensis >nul 2>&1
if not errorlevel 1 (
    echo Creating installer with NSIS...
    makensis build\installer.nsi
)

call venv_build\Scripts\deactivate.bat
echo Done!
pause
