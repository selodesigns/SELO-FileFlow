
; SELO FileFlow Installer Script
!include "MUI2.nsh"
!include "FileFunc.nsh"

; General
Name "FileFlow"
OutFile "FileFlow-Setup-1.0.0.exe"
InstallDir "$PROGRAMFILES\SELOdev\FileFlow"
InstallDirRegKey HKCU "Software\SELOdev\FileFlow" ""

; Request application privileges
RequestExecutionLevel admin

; Add version info to installer
VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "SELO FileFlow"
VIAddVersionKey "CompanyName" "SELOdev"
VIAddVersionKey "LegalCopyright" "© 2025 SELOdev"
VIAddVersionKey "FileDescription" "SELO FileFlow Installer"
VIAddVersionKey "FileVersion" "1.0.0"
VIAddVersionKey "ProductVersion" "1.0.0"

; Interface settings
!define MUI_ABORTWARNING
!define MUI_ICON "resources\icon.ico"
!define MUI_UNICON "resources\icon.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "resources\installer-side.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "resources\installer-side.bmp"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "resources\installer-header.bmp"
!define MUI_HEADERIMAGE_RIGHT
!define MUI_FINISHPAGE_RUN "$INSTDIR\SELO-FileFlow.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch FileFlow"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY

; Component selection page
!insertmacro MUI_PAGE_COMPONENTS


!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installation Options
Section "FileFlow (Required)" SecMain
  SectionIn RO  ; Read-only, cannot be deselected
  SetOutPath "$INSTDIR"
  
  ; Files
  File /r "dist\SELO-FileFlow\*.*"
  
  ; Create logs directory in user's AppData folder (writable by non-admin users)
  CreateDirectory "$APPDATA\SELOdev\FileFlow\logs"
  
  ; Set an environment variable for the app to use for logging
  WriteRegStr HKCU "Environment" "FILEFLOW_LOG_DIR" "$APPDATA\SELOdev\FileFlow\logs"
  
  ; Registry keys for uninstaller
  WriteRegStr HKCU "Software\SELOdev\FileFlow" "" $INSTDIR
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FileFlow" "DisplayName" "FileFlow"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FileFlow" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FileFlow" "Publisher" "SELOdev"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FileFlow" "DisplayIcon" "$INSTDIR\SELO-FileFlow.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FileFlow" "DisplayVersion" "1.0.0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FileFlow" "InstallLocation" "$INSTDIR"
  
  ; Get installation size
  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FileFlow" "EstimatedSize" $0
  
  ; Write uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

; Desktop shortcut (checked by default)
Section "Desktop Shortcut" SecDesktop
  ; First ensure the icon is properly copied to a known location
  SetOutPath "$INSTDIR"
  File /oname=app.ico "resources\icon.ico"
  CreateShortcut "$DESKTOP\FileFlow.lnk" "$INSTDIR\SELO-FileFlow.exe" "" "$INSTDIR\app.ico"
SectionEnd

; Start Menu shortcuts (checked by default)
Section "Start Menu Shortcuts" SecStartMenu
  CreateDirectory "$SMPROGRAMS\SELOdev"
  CreateShortcut "$SMPROGRAMS\SELOdev\FileFlow.lnk" "$INSTDIR\SELO-FileFlow.exe" "" "$INSTDIR\app.ico"
  CreateShortcut "$SMPROGRAMS\SELOdev\Uninstall FileFlow.lnk" "$INSTDIR\uninstall.exe"
SectionEnd

; Run at startup option
Section "Run at Startup" SecStartup
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "FileFlow" "$INSTDIR\SELO-FileFlow.exe --minimized"
SectionEnd

; Description texts for sections
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} "Core application files (required)"
  !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} "Create a shortcut on your desktop"
  !insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenu} "Create shortcuts in your Start Menu"
  !insertmacro MUI_DESCRIPTION_TEXT ${SecStartup} "Automatically start FileFlow when Windows starts"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

    