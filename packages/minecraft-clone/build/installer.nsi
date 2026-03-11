; =============================================================================
; DragonMind Craft - NSIS Windows Installer Script
; Creates a professional Windows installer (.exe)
; Requirements: NSIS 3.x (https://nsis.sourceforge.io)
; =============================================================================

Unicode True

!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"

; ---- App metadata ----
!define APP_NAME        "DragonMind Craft"
!define APP_EXE         "DragonMindCraft.exe"
!define APP_VERSION     "1.0.0"
!define PUBLISHER       "DragonMind"
!define APP_URL         "https://github.com/twick1234/dragon-mind"
!define INSTALL_REG_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\DragonMindCraft"
!define DIST_DIR        "dist\DragonMindCraft"

; ---- Installer output ----
Name "${APP_NAME}"
OutFile "dist\DragonMindCraft-${APP_VERSION}-Windows-Setup.exe"
InstallDir "$PROGRAMFILES64\${APP_NAME}"
InstallDirRegKey HKLM "${INSTALL_REG_KEY}" "InstallLocation"
RequestExecutionLevel admin
SetCompressor /SOLID lzma

; ---- Modern UI Settings ----
!define MUI_ABORTWARNING
!define MUI_ICON        "..\..\assets\icon.ico"
!define MUI_UNICON      "..\..\assets\icon.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP_NOSTRETCH
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_RIGHT

!define MUI_WELCOMEPAGE_TITLE       "Welcome to ${APP_NAME} Setup"
!define MUI_WELCOMEPAGE_TEXT        "This will install ${APP_NAME} ${APP_VERSION} on your computer.$\r$\n$\r$\nA Minecraft-inspired voxel game with procedural worlds, caves, ores, and survival mechanics.$\r$\n$\r$\nClick Next to continue."
!define MUI_FINISHPAGE_RUN          "$INSTDIR\${APP_EXE}"
!define MUI_FINISHPAGE_RUN_TEXT     "Launch ${APP_NAME}"
!define MUI_FINISHPAGE_LINK         "Visit project on GitHub"
!define MUI_FINISHPAGE_LINK_LOCATION "${APP_URL}"

; ---- Pages ----
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE       "..\..\LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

; =============================================================================
; Components
; =============================================================================

Section "DragonMind Craft (required)" SecGame
    SectionIn RO
    SetOutPath "$INSTDIR"

    ; Copy all game files from PyInstaller dist output
    File /r "${DIST_DIR}\*.*"

    ; Write uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"

    ; Registry: Add/Remove Programs entry
    WriteRegStr   HKLM "${INSTALL_REG_KEY}" "DisplayName"          "${APP_NAME}"
    WriteRegStr   HKLM "${INSTALL_REG_KEY}" "DisplayVersion"       "${APP_VERSION}"
    WriteRegStr   HKLM "${INSTALL_REG_KEY}" "Publisher"            "${PUBLISHER}"
    WriteRegStr   HKLM "${INSTALL_REG_KEY}" "URLInfoAbout"         "${APP_URL}"
    WriteRegStr   HKLM "${INSTALL_REG_KEY}" "InstallLocation"      "$INSTDIR"
    WriteRegStr   HKLM "${INSTALL_REG_KEY}" "UninstallString"      "$INSTDIR\Uninstall.exe"
    WriteRegStr   HKLM "${INSTALL_REG_KEY}" "QuietUninstallString" "$INSTDIR\Uninstall.exe /S"
    WriteRegDWORD HKLM "${INSTALL_REG_KEY}" "NoModify"             1
    WriteRegDWORD HKLM "${INSTALL_REG_KEY}" "NoRepair"             1

    ; Estimate installed size
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "${INSTALL_REG_KEY}" "EstimatedSize" "$0"
SectionEnd

Section "Desktop Shortcut" SecDesktop
    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_EXE}" 0
SectionEnd

Section "Start Menu Shortcut" SecStartMenu
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortCut  "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"  "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_EXE}" 0
    CreateShortCut  "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk"    "$INSTDIR\Uninstall.exe"
SectionEnd

; ---- Component descriptions ----
LangString DESC_SecGame      ${LANG_ENGLISH} "The full DragonMind Craft game (required)."
LangString DESC_SecDesktop   ${LANG_ENGLISH} "Add a shortcut to your Desktop."
LangString DESC_SecStartMenu ${LANG_ENGLISH} "Add shortcuts to your Start Menu."

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecGame}      $(DESC_SecGame)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop}   $(DESC_SecDesktop)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenu} $(DESC_SecStartMenu)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; =============================================================================
; Uninstaller
; =============================================================================

Section "Uninstall"
    ; Remove installed files
    RMDir /r "$INSTDIR"

    ; Remove shortcuts
    Delete "$DESKTOP\${APP_NAME}.lnk"
    RMDir /r "$SMPROGRAMS\${APP_NAME}"

    ; Remove registry entry
    DeleteRegKey HKLM "${INSTALL_REG_KEY}"
SectionEnd
