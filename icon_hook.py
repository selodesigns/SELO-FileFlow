"""
PyInstaller runtime hook to force icon loading at application startup
"""
import os
import sys

# This will be executed when the application starts from the PyInstaller bundle
def apply_icon_fix():
    # Only needed on Windows
    if sys.platform != 'win32':
        return
        
    # Check if we're running in a PyInstaller bundle
    if not (getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')):
        return
        
    try:
        # Windows-specific modules
        import ctypes
        
        # Set explicit app ID for Windows
        app_id = 'SELOdev.FileFlow.App.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        
        # Debug info - will appear in console if run with console=True
        print(f"Icon hook: Applied Windows app ID: {app_id}")
        
        # Force icon cache refresh
        try:
            ctypes.windll.user32.SendMessageW(0xFFFF, 0x001C, 0, 0)
        except Exception as e:
            print(f"Icon hook: Error refreshing icon cache: {e}")
    except Exception as e:
        print(f"Icon hook: Failed to apply icon fix: {e}")

# Apply the fix immediately when this module is imported
apply_icon_fix()
