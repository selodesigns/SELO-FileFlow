"""
Set Windows application ID for proper taskbar and title bar icon handling.
"""
import sys
import ctypes

def set_app_id():
    """
    Set the Windows Application User Model ID (AUMID).
    This helps Windows properly associate the application with its icon.
    """
    if sys.platform == 'win32':
        try:
            app_id = "SELOdev.FileFlow.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
            print(f"Set Windows AppUserModelID to: {app_id}")
            return True
        except Exception as e:
            print(f"Failed to set AppUserModelID: {e}")
            return False
    return False
