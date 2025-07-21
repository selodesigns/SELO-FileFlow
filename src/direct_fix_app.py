"""
Complete fix for FileFlow icon and notification issues.
This script should be run after installation to fix any lingering issues.
"""
import os
import sys
import ctypes
import subprocess
from pathlib import Path

def fix_app_identity():
    """Apply comprehensive fixes for FileFlow icons and notifications"""
    print("Applying FileFlow identity fixes...")
    
    # Get the installation directory
    if getattr(sys, 'frozen', False):
        # Running as executable
        app_dir = Path(sys.executable).parent
    else:
        # Running as script
        app_dir = Path(__file__).parent.parent.absolute()
    
    icon_path = app_dir / "resources" / "icon.ico"
    
    if not icon_path.exists():
        print(f"ERROR: Icon file not found at {icon_path}")
        return False
    
    print(f"Found icon at: {icon_path}")
    
    # Fix 1: Windows AppUserModelID for title bar icon
    try:
        app_id = "SELOdev.FileFlow.App.1.0.0"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        print(f"Set Windows AppUserModelID to: {app_id}")
    except Exception as e:
        print(f"Failed to set AppUserModelID: {e}")
    
    # Fix 2: Fix application name in Windows registry
    try:
        import winreg
        # Main app registration
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\FileFlow") as key:
            winreg.SetValueEx(key, "AppName", 0, winreg.REG_SZ, "FileFlow")
            winreg.SetValueEx(key, "IconPath", 0, winreg.REG_SZ, str(icon_path))
            print("Updated registry application name and icon path")
    except Exception as e:
        print(f"Failed to update registry: {e}")
    
    # Fix 3: Clear notification cache
    try:
        # Windows notification cache directory
        notification_dir = Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Notifications"
        print(f"Notification directory: {notification_dir}")
        
        # Clean up notification database - requires admin rights
        command = f'TASKKILL /F /IM explorer.exe && DEL /F "{notification_dir}\\*" && START explorer.exe'
        print(f"To clear notification cache completely, run this as admin: {command}")
    except Exception as e:
        print(f"Failed to clear notification cache: {e}")
    
    # Fix 4: Create direct shortcut with explicit icon
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        desktop = shell.SpecialFolders("Desktop")
        shortcut_path = os.path.join(desktop, "FileFlow.lnk")
        
        # Target executable
        if getattr(sys, 'frozen', False):
            target = sys.executable
        else:
            target = os.path.join(app_dir, "FileFlow.exe")
            
        if os.path.exists(target) or os.path.exists(shortcut_path):
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = target
            shortcut.IconLocation = f"{icon_path},0"
            shortcut.Description = "FileFlow File Organization Tool"
            shortcut.WorkingDirectory = os.path.dirname(target)
            shortcut.save()
            print(f"Created desktop shortcut with explicit icon at: {shortcut_path}")
    except Exception as e:
        print(f"Failed to create shortcut: {e}")
    
    print("Identity fixes applied. Please restart the application and Windows Explorer.")
    return True

if __name__ == "__main__":
    fix_app_identity()
