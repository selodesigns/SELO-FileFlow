"""
Comprehensive icon fix for FileFlow
"""
import os
import sys
import ctypes
import winreg
from pathlib import Path

def fix_application_icons():
    """Apply comprehensive fixes for FileFlow icons"""
    print("Applying FileFlow icon fixes...")
    
    # 1. Get the application directory
    app_dir = Path(__file__).parent.absolute()
    icon_path = app_dir / "resources" / "icon.ico"
    
    if not icon_path.exists():
        print(f"ERROR: Icon file not found at {icon_path}")
        return False
    
    print(f"Found icon at: {icon_path}")
    
    # 2. Register Windows AppUserModelID for proper taskbar/title bar behavior
    try:
        app_id = "SELOdev.FileFlow.Application"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        print(f"Set Windows AppUserModelID to: {app_id}")
    except Exception as e:
        print(f"Failed to set AppUserModelID: {e}")
    
    # 3. Fix Windows registry entries for the application
    try:
        # Registry entry for FileFlow
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\FileFlow") as key:
            winreg.SetValueEx(key, "IconPath", 0, winreg.REG_SZ, str(icon_path))
            print(f"Updated registry icon path: {icon_path}")
    except Exception as e:
        print(f"Failed to update registry: {e}")
    
    # 4. Create or update desktop shortcut with correct icon
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        desktop_path = shell.SpecialFolders("Desktop")
        shortcut_path = os.path.join(desktop_path, "FileFlow.lnk")
        
        if os.path.exists(shortcut_path):
            shortcut = shell.CreateShortCut(shortcut_path)
            exe_path = app_dir / "dist" / "FileFlow" / "FileFlow.exe"
            if exe_path.exists():
                shortcut.TargetPath = str(exe_path)
                shortcut.IconLocation = f"{icon_path},0"
                shortcut.save()
                print(f"Updated desktop shortcut icon at: {shortcut_path}")
    except Exception as e:
        print(f"Failed to update desktop shortcut: {e}")
        
    print("Icon fixes applied successfully!")
    return True

if __name__ == "__main__":
    fix_application_icons()
