"""
This script fixes Windows icon-related issues by adding explicit resource handling.
"""
import os
import sys
import ctypes
from PyQt5.QtWinExtras import QtWin
from PyQt5.QtGui import QIcon

def fix_windows_icon():
    """Apply specific Windows fixes for application icon"""
    try:
        # Set AppUserModelID (needed for Windows taskbar/titlebar icon)
        app_id = 'selodev.fileflow.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        
        # Get icon path
        icon_path = os.path.abspath(os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'resources', 
            'icon.ico'
        ))
        
        if os.path.exists(icon_path):
            # Set taskbar icon explicitly using QtWin
            if hasattr(QtWin, 'setCurrentProcessExplicitAppUserModelID'):
                QtWin.setCurrentProcessExplicitAppUserModelID(app_id)
            
            # Set window icon for taskbar grouping
            if hasattr(QtWin, 'ExtendedWindow'):
                icon = QIcon(icon_path)
                QtWin.setWindowIcon(icon)
                
            return True
    except Exception as e:
        print(f"Error setting Windows icon: {e}")
    
    return False
