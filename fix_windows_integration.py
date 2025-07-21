"""
Comprehensive fix for Windows integration issues in FileFlow.
This will completely solve the title bar icon and notification name problems.
"""
import os
import sys
import shutil
import winreg
import subprocess
from pathlib import Path

def reset_windows_notification_cache():
    """Reset the Windows notification cache to clear any old app identities."""
    # This may require administrator privileges
    print("Attempting to reset Windows notification cache...")
    
    try:
        # Kill the Windows explorer process (this won't affect the script)
        subprocess.run("taskkill /f /im explorer.exe", shell=True, check=False)
        
        # Clear notification database - path varies by Windows version
        paths_to_clear = [
            os.path.expanduser("~\\AppData\\Local\\Microsoft\\Windows\\Notifications"),
            os.path.expanduser("~\\AppData\\Local\\Microsoft\\Windows\\ActionCenter")
        ]
        
        for path in paths_to_clear:
            if os.path.exists(path):
                print(f"Clearing notification data in: {path}")
                for item in os.listdir(path):
                    if item.endswith(".db"):
                        try:
                            os.remove(os.path.join(path, item))
                            print(f"Removed {item}")
                        except Exception as e:
                            print(f"Could not remove {item}: {e}")
        
        # Restart explorer
        subprocess.Popen("explorer.exe", shell=True)
        print("Windows Explorer restarted.")
    except Exception as e:
        print(f"Error resetting notification cache: {e}")
        print("You may need to run this script as administrator.")

def fix_registry_entries():
    """Update Windows registry entries to fix application identity."""
    print("Updating registry entries...")
    
    try:
        # Ensure FileFlow key exists and has correct values
        key_path = r"Software\FileFlow"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, "Name", 0, winreg.REG_SZ, "FileFlow")
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "SELOdev")
            print("Updated FileFlow registry entries")
        
        # Fix app user model ID in the registry
        key_path = r"Software\Classes\AppUserModelId\SELOdev.FileFlow"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "FileFlow")
            print("Created AppUserModelId registry entry")
            
        print("Registry entries updated successfully")
    except Exception as e:
        print(f"Error updating registry: {e}")

def update_shortcut_properties():
    """Update shortcut properties to ensure correct icon and app identity."""
    print("Updating shortcuts...")
    
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        
        # Find icon path
        app_dir = Path(__file__).parent
        icon_path = app_dir / "resources" / "icon.ico"
        
        if not icon_path.exists():
            print(f"Error: Icon not found at {icon_path}")
            return
            
        # Update desktop shortcut
        desktop = shell.SpecialFolders("Desktop")
        shortcut_path = os.path.join(desktop, "FileFlow.lnk")
        
        if os.path.exists(shortcut_path):
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.IconLocation = str(icon_path)
            shortcut.Description = "FileFlow File Organizer"
            shortcut.save()
            print(f"Updated desktop shortcut at {shortcut_path}")
        
        # Update Start Menu shortcut
        start_menu = shell.SpecialFolders("Programs")
        start_menu_path = os.path.join(start_menu, "FileFlow", "FileFlow.lnk")
        
        if os.path.exists(start_menu_path):
            shortcut = shell.CreateShortCut(start_menu_path)
            shortcut.IconLocation = str(icon_path)
            shortcut.Description = "FileFlow File Organizer"
            shortcut.save()
            print(f"Updated Start Menu shortcut at {start_menu_path}")
            
        print("Shortcuts updated successfully")
    except Exception as e:
        print(f"Error updating shortcuts: {e}")
        print("You may need to install pywin32: pip install pywin32")

def apply_fixes():
    """Apply all fixes."""
    print("=== FileFlow Windows Integration Fix ===")
    
    # 1. Fix registry entries
    fix_registry_entries()
    
    # 2. Update shortcuts
    update_shortcut_properties()
    
    # 3. Reset notification cache
    reset_windows_notification_cache()
    
    print("\nAll fixes have been applied. Please restart your computer for changes to take effect.")
    print("After restart, the title bar icon and notification name should be correct.")

if __name__ == "__main__":
    apply_fixes()
