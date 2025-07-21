"""
Create a FileFlow installer (freeware edition).
"""
import os
import sys
import subprocess
from pathlib import Path

def create_windows_installer():
    """Create a Windows installer for FileFlow freeware."""
    # Check if the executable exists
    exe_path = Path("dist") / "SELO-FileFlow" / "SELO-FileFlow.exe"
    if not exe_path.exists():
        print(f"Error: Executable not found at {exe_path}")
        print("Please run build_app.py first to create the executable.")
        return False
        
    # Get version info
    version = "1.0.0"  # Default version
    try:
        # Try to read version from a version file if it exists
        if Path("version.txt").exists():
            with open("version.txt", "r") as f:
                version = f.read().strip()
    except Exception:
        pass
    
    print(f"Creating installer for FileFlow version {version}...")
    
    # Create NSIS script
    nsis_script = f"""
; FileFlow Installer Script (Freeware Edition)
!include "MUI2.nsh"
!include "FileFunc.nsh"

; General
Name "FileFlow"
OutFile "FileFlow-Setup-{version}.exe"
InstallDir "$PROGRAMFILES\\FileFlow"
InstallDirRegKey HKCU "Software\\FileFlow" ""

; Add version info to installer
VIProductVersion "{version}.0"
VIAddVersionKey "ProductName" "FileFlow"
VIAddVersionKey "CompanyName" "SELOdev"
VIAddVersionKey "LegalCopyright" "© 2025 SELOdev"
VIAddVersionKey "FileDescription" "FileFlow Installer"
VIAddVersionKey "FileVersion" "{version}"
VIAddVersionKey "ProductVersion" "{version}"

; Interface settings
!define MUI_ABORTWARNING
!define MUI_ICON "resources\\icon.ico"
!define MUI_UNICON "resources\\icon.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "resources\\installer-side.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "resources\\installer-side.bmp"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "resources\\installer-header.bmp"
!define MUI_HEADERIMAGE_RIGHT
!define MUI_FINISHPAGE_RUN "$INSTDIR\\FileFlow.exe"
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
  File /r "dist\\SELO-FileFlow\\*.*"
  
  ; Rename the executable
  Rename "$INSTDIR\\SELO-FileFlow.exe" "$INSTDIR\\FileFlow.exe"
  
  ; Create important directories if they don't exist
  CreateDirectory "$INSTDIR\\logs"
  
  ; Registry keys for uninstaller
  WriteRegStr HKCU "Software\\FileFlow" "" $INSTDIR
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\FileFlow" "DisplayName" "FileFlow"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\FileFlow" "UninstallString" "$\\"$INSTDIR\\uninstall.exe$\\""
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\FileFlow" "Publisher" "SELOdev"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\FileFlow" "DisplayIcon" "$INSTDIR\\FileFlow.exe"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\FileFlow" "DisplayVersion" "{version}"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\FileFlow" "InstallLocation" "$INSTDIR"
  
  ; Get installation size
  ${{GetSize}} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\FileFlow" "EstimatedSize" "$0"
  
  ; Write uninstaller
  WriteUninstaller "$INSTDIR\\uninstall.exe"
SectionEnd

; Optional Sections
Section "Desktop Shortcut" SecDesktop
  ; Create desktop shortcut with explicit icon
  File "/oname=$INSTDIR\\icon.ico" "resources\\icon.ico"
  CreateShortcut "$DESKTOP\\FileFlow.lnk" "$INSTDIR\\FileFlow.exe" "" "$INSTDIR\\icon.ico"
SectionEnd

Section "Start Menu Shortcuts" SecStartMenu
  CreateDirectory "$SMPROGRAMS\\FileFlow"
  CreateShortcut "$SMPROGRAMS\\FileFlow\\FileFlow.lnk" "$INSTDIR\\FileFlow.exe" "" "$INSTDIR\\icon.ico"
  CreateShortcut "$SMPROGRAMS\\FileFlow\\Uninstall FileFlow.lnk" "$INSTDIR\\uninstall.exe" "" "$INSTDIR\\icon.ico"
SectionEnd

Section "Run at Startup" SecStartup
  WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Run" "FileFlow" "$INSTDIR\\FileFlow.exe --minimized"
SectionEnd

; Descriptions for sections
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${{SecMain}} "Core application files (required)"
  !insertmacro MUI_DESCRIPTION_TEXT ${{SecDesktop}} "Create a shortcut on your desktop"
  !insertmacro MUI_DESCRIPTION_TEXT ${{SecStartMenu}} "Create shortcuts in your Start Menu"
  !insertmacro MUI_DESCRIPTION_TEXT ${{SecStartup}} "Automatically start FileFlow when Windows starts"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Uninstaller section
Section "Uninstall"
  ; Remove files and directories
  RMDir /r "$INSTDIR\\*.*"
  RMDir "$INSTDIR"
  
  ; Remove shortcuts
  Delete "$SMPROGRAMS\\FileFlow\\FileFlow.lnk"
  Delete "$SMPROGRAMS\\FileFlow\\Uninstall FileFlow.lnk"
  RMDir "$SMPROGRAMS\\FileFlow" 
  Delete "$DESKTOP\\FileFlow.lnk"
  
  ; Remove registry keys
  DeleteRegKey HKCU "Software\\FileFlow"
  DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\FileFlow"
  DeleteRegValue HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Run" "FileFlow"
SectionEnd
"""

    # Write NSIS script to file
    print("Creating NSIS installer script...")
    with open("installer.nsi", "w") as f:
        f.write(nsis_script)
    
    # Check if makensis is available
    try:
        # Try to find makensis in the default NSIS installation directory
        nsis_paths = [
            r"C:\Program Files\NSIS\makensis.exe",
            r"C:\Program Files (x86)\NSIS\makensis.exe"
        ]
        
        makensis_path = None
        for path in nsis_paths:
            if os.path.exists(path):
                makensis_path = path
                break
        
        if makensis_path:
            print(f"Found NSIS at: {makensis_path}")
        else:
            # Try to run makensis directly (if it's in PATH)
            subprocess.check_call(["makensis", "-VERSION"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
            makensis_path = "makensis"
    except (subprocess.SubprocessError, FileNotFoundError):
        print("NSIS not found. Please check your NSIS installation.")
        print("You can download NSIS from https://nsis.sourceforge.io/")
        return False
    
    # Run NSIS to create installer
    print("Creating Windows installer with NSIS...")
    try:
        if makensis_path == "makensis":
            subprocess.check_call(["makensis", "installer.nsi"])
        else:
            subprocess.check_call([makensis_path, "installer.nsi"])
        
        # Check if installer was created
        installer_path = f"FileFlow-Setup-{version}.exe"
        if os.path.exists(installer_path):
            print(f"Installer created successfully: {os.path.abspath(installer_path)}")
            
            # Move installer to dist directory
            dist_path = os.path.join("dist", installer_path)
            if not os.path.exists("dist"):
                os.makedirs("dist")
            
            # Move to dist folder
            os.replace(installer_path, dist_path)
            print(f"Installer moved to: {os.path.abspath(dist_path)}")
            return True
        else:
            print(f"Error: Installer not found at {installer_path}")
            return False
    except subprocess.SubprocessError as e:
        print(f"Error running NSIS: {e}")
        return False

if __name__ == "__main__":
    if create_windows_installer():
        print("Installer creation completed successfully!")
    else:
        print("Failed to create installer.")
