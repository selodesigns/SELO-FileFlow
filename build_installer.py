#!/usr/bin/env python3
"""
Build script for SELO FileFlow.
Creates a standalone executable using PyInstaller.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_executable():
    """Build the executable package for SELO FileFlow."""
    print("Building SELO FileFlow executable...")
    
    # Ensure PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Prepare build directory
    build_dir = Path("build")
    dist_dir = Path("dist")
    
    for dir_path in [build_dir, dist_dir]:
        if dir_path.exists():
            shutil.rmtree(dir_path)
        dir_path.mkdir()
    
    # Check for required files and create them if missing
    license_file = Path("LICENSE")
    if not license_file.exists():
        print("Creating default LICENSE file...")
        with open(license_file, "w") as f:
            f.write("MIT License\n\nCopyright (c) 2025 SELOdev\n\nPermission is hereby granted...")
    
    readme_file = Path("README.md")
    if not readme_file.exists():
        print("Creating default README.md file...")
        with open(readme_file, "w") as f:
            f.write("# SELO FileFlow\n\nA professional file management solution from SELOdev.")
    
    # Create a simple icon if not exists
    icon_path = Path("resources/icon.ico")
    if not icon_path.exists() or os.path.getsize(str(icon_path)) == 0:
        print("Creating placeholder icon...")
        # We'll just create an empty file as placeholder
        icon_path.parent.mkdir(exist_ok=True)
        icon_path.touch()
    
    # Convert to string with proper escaping for spec file
    icon_path_str = str(icon_path).replace('\\', '/')
    
    # Collect data files that actually exist
    data_files = []
    
    # Always include config directory
    if Path("config").exists():
        data_files.append(("config", "config"))
    
    # Add other files if they exist
    for file in ["README.md", "LICENSE"]:
        if Path(file).exists():
            data_files.append((file, "."))
            
    # Always include the icon file
    icon_file = Path("resources/icon.ico")
    if icon_file.exists():
        data_files.append((str(icon_file), "resources"))
        # Also copy it to the root for PyInstaller to find
        data_files.append((str(icon_file), "."))
    
    # Create the icon_hook.py if it doesn't exist
    icon_hook_path = Path("icon_hook.py")
    if not icon_hook_path.exists():
        with open(icon_hook_path, "w") as f:
            f.write('"""PyInstaller runtime hook for proper icon handling."""\n')
            f.write('# This file is intentionally empty as icon handling is now in ui_app.py\n')
    
    # Create the user_dirs_hook.py if it doesn't exist
    user_dirs_hook_path = Path("user_dirs_hook.py")
    if not user_dirs_hook_path.exists():
        with open(user_dirs_hook_path, "w") as f:
            f.write('"""\nPyInstaller hook for SELO FileFlow.\n')
            f.write('This runtime hook ensures proper handling of user directories when running as a packaged application.\n')
            f.write('"""\n')
            f.write('import os\n')
            f.write('import sys\n')
            f.write('from pathlib import Path\n\n')
            f.write('# This will run before the application starts\n')
            f.write('def setup_user_directories():\n')
            f.write('    """Set up user-specific directories for the packaged application."""\n')
            f.write('    try:\n')
            f.write('        # Check if running as a packaged application\n')
            f.write('        is_frozen = getattr(sys, \'frozen\', False) and hasattr(sys, \'_MEIPASS\')\n\n')
            f.write('        if is_frozen:\n')
            f.write('            # Determine base user directory for data\n')
            f.write('            if sys.platform == \'win32\':\n')
            f.write('                # Windows: Use AppData\n')
            f.write('                base_user_dir = Path(os.environ.get(\'APPDATA\', \'\')) / "SELOdev" / "FileFlow"\n')
            f.write('            else:\n')
            f.write('                # Unix/Linux/Mac: Use ~/.fileflow\n')
            f.write('                base_user_dir = Path(os.path.expanduser("~")) / ".fileflow"\n\n')
            f.write('            # Create user directories if they don\'t exist\n')
            f.write('            for dir_name in [\'config\', \'logs\', \'data\', \'cache\']:\n')
            f.write('                dir_path = base_user_dir / dir_name\n')
            f.write('                dir_path.mkdir(parents=True, exist_ok=True)\n')
            f.write('    except Exception:\n')
            f.write('        # Don\'t let errors in this hook prevent the application from starting\n')
            f.write('        pass\n\n')
            f.write('# Run the setup\n')
            f.write('setup_user_directories()\n')

    # Build spec file content with dynamic data files - simpler approach without Path dependency
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

block_cipher = None

a = Analysis(
    ['run_fileflow.py'],
    pathex=[],
    binaries=[],
    datas={data_files},
    hiddenimports=['PyQt5.sip'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=['icon_hook.py', 'user_dirs_hook.py'],
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
    name='SELO-FileFlow',
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
    icon='{icon_path_str}' if os.path.exists('{icon_path_str}') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SELO-FileFlow',
)
    """
    
    # Create resources directory and placeholder icon
    resources_dir = Path("resources")
    if not resources_dir.exists():
        resources_dir.mkdir()
    
    # Create a spec file
    with open("SELO-FileFlow.spec", "w") as f:
        f.write(spec_content)
    
    # Run PyInstaller
    print("Running PyInstaller...")
    subprocess.check_call([
        sys.executable, 
        "-m", 
        "PyInstaller", 
        "SELO-FileFlow.spec",
        "--noconfirm"
    ])
    
    # Create installer with NSIS (if available)
    try:
        create_windows_installer()
    except Exception as e:
        print(f"Skipping Windows installer creation: {e}")
        print("You can still use the standalone executable in the dist folder.")
    
    print("\nBuild completed!")
    print(f"Executable available at: {os.path.abspath('dist/SELO-FileFlow/SELO-FileFlow.exe')}")

def create_windows_installer():
    """Create a Windows installer using NSIS."""
    # Check for makensis in common installation locations
    makensis_cmd = "makensis"
    nsis_found = False
    
    # First try with the command directly (if in PATH)
    try:
        subprocess.check_call([makensis_cmd, "-VERSION"], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
        nsis_found = True
    except (subprocess.SubprocessError, FileNotFoundError):
        # Not in PATH, try common installation locations
        common_paths = [
            "C:\\Program Files\\NSIS\\makensis.exe",
            "C:\\Program Files (x86)\\NSIS\\makensis.exe",
            os.path.expandvars("%ProgramFiles%\\NSIS\\makensis.exe"),
            os.path.expandvars("%ProgramFiles(x86)%\\NSIS\\makensis.exe")
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                makensis_cmd = path
                nsis_found = True
                print(f"NSIS found at: {path}")
                break
    
    if not nsis_found:
        print("NSIS not found. Skipping installer creation.")
        print("To create an installer, install NSIS from https://nsis.sourceforge.io/")
        return
    
    # Get version info
    version = "1.0.0"  # Default version
    try:
        # Try to read version from a version file if it exists
        if Path("version.txt").exists():
            with open("version.txt", "r") as f:
                version = f.read().strip()
    except Exception:
        pass
    
    # Let's create a complete installer.nsi file separately instead of using Python string formatting
    # Define version for the filename only
    installer_filename = f"FileFlow-Setup-{version}.exe"
    
    # NSIS script with the version manually inserted where needed
    nsis_script = f"""
; SELO FileFlow Installer Script
!include "MUI2.nsh"
!include "FileFunc.nsh"

; General
Name "FileFlow"
OutFile "{installer_filename}"
InstallDir "$PROGRAMFILES\\SELOdev\\FileFlow"
InstallDirRegKey HKCU "Software\\SELOdev\\FileFlow" ""

; Request application privileges
RequestExecutionLevel admin

; Add version info to installer
VIProductVersion "{version}.0"
VIAddVersionKey "ProductName" "SELO FileFlow"
VIAddVersionKey "CompanyName" "SELOdev"
VIAddVersionKey "LegalCopyright" "© 2025 SELOdev"
VIAddVersionKey "FileDescription" "SELO FileFlow Installer"
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
!define MUI_FINISHPAGE_RUN "$INSTDIR\\SELO-FileFlow.exe"
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
  
  ; Create logs directory in user's AppData folder (writable by non-admin users)
  CreateDirectory "$APPDATA\\SELOdev\\FileFlow\\logs"
  
  ; Set an environment variable for the app to use for logging
  WriteRegStr HKCU "Environment" "FILEFLOW_LOG_DIR" "$APPDATA\\SELOdev\\FileFlow\\logs"
  
  ; Registry keys for uninstaller
  WriteRegStr HKCU "Software\\SELOdev\\FileFlow" "" $INSTDIR
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\FileFlow" "DisplayName" "FileFlow"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\FileFlow" "UninstallString" '"$INSTDIR\\uninstall.exe"'
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\FileFlow" "Publisher" "SELOdev"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\FileFlow" "DisplayIcon" "$INSTDIR\\SELO-FileFlow.exe"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\FileFlow" "DisplayVersion" "{version}"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\FileFlow" "InstallLocation" "$INSTDIR"
  
  ; Get installation size
  ${{GetSize}} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\FileFlow" "EstimatedSize" $0
  
  ; Write uninstaller
  WriteUninstaller "$INSTDIR\\uninstall.exe"
SectionEnd

; Desktop shortcut (checked by default)
Section "Desktop Shortcut" SecDesktop
  ; First ensure the icon is properly copied to a known location
  SetOutPath "$INSTDIR"
  File /oname=app.ico "resources\\icon.ico"
  CreateShortcut "$DESKTOP\\FileFlow.lnk" "$INSTDIR\\SELO-FileFlow.exe" "" "$INSTDIR\\app.ico"
SectionEnd

; Start Menu shortcuts (checked by default)
Section "Start Menu Shortcuts" SecStartMenu
  CreateDirectory "$SMPROGRAMS\\SELOdev"
  CreateShortcut "$SMPROGRAMS\\SELOdev\\FileFlow.lnk" "$INSTDIR\\SELO-FileFlow.exe" "" "$INSTDIR\\app.ico"
  CreateShortcut "$SMPROGRAMS\\SELOdev\\Uninstall FileFlow.lnk" "$INSTDIR\\uninstall.exe"
SectionEnd

; Run at startup option
Section "Run at Startup" SecStartup
  WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Run" "FileFlow" "$INSTDIR\\SELO-FileFlow.exe --minimized"
SectionEnd

; Description texts for sections
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${{SecMain}} "Core application files (required)"
  !insertmacro MUI_DESCRIPTION_TEXT ${{SecDesktop}} "Create a shortcut on your desktop"
  !insertmacro MUI_DESCRIPTION_TEXT ${{SecStartMenu}} "Create shortcuts in your Start Menu"
  !insertmacro MUI_DESCRIPTION_TEXT ${{SecStartup}} "Automatically start FileFlow when Windows starts"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

    """
    
    # Write NSIS script to file
    with open("installer.nsi", "w") as f:
        f.write(nsis_script)
    
    # Run NSIS to create installer
    print("Creating Windows installer with NSIS...")
    subprocess.check_call([makensis_cmd, "installer.nsi"])
    
    # Check for installer with dynamic filename
    installer_file = f"FileFlow-Setup-{version}.exe"
    if os.path.exists(installer_file):
        # Create dist directory if it doesn't exist
        if not os.path.exists("dist"):
            os.makedirs("dist")
        shutil.move(installer_file, f"dist/{installer_file}")
        print(f"Installer created at: {os.path.abspath(f'dist/{installer_file}')}")
    else:
        print(f"Warning: Expected installer file {installer_file} not found after NSIS compilation.")

if __name__ == "__main__":
    build_executable()
