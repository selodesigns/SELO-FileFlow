"""
Cross-platform fixes for FileFlow application UI issues.
This module handles application icon and notification text problems across different operating systems.
"""
import os
import sys
import subprocess
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CrossPlatformAppFixes:
    """Cross-platform fixes for application UI issues."""
    
    @staticmethod
    def apply_app_icon_fix():
        """Apply platform-specific icon fixes."""
        if sys.platform == 'win32':
            return CrossPlatformAppFixes._apply_windows_icon_fix()
        elif sys.platform.startswith('linux'):
            return CrossPlatformAppFixes._apply_linux_icon_fix()
        elif sys.platform == 'darwin':
            return CrossPlatformAppFixes._apply_macos_icon_fix()
        else:
            logger.info(f"No specific icon fixes needed for platform: {sys.platform}")
            return True
    
    @staticmethod
    def _apply_windows_icon_fix():
        """Apply Windows-specific icon fixes."""
        try:
            # Try to import Windows-specific modules
            import win32api
            import win32con
            import win32gui
            import ctypes
            
            # Set the process AppUserModelID
            app_id = 'SELOdev.FileFlow.Application.1'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
            logger.info(f"Set Windows application ID: {app_id}")
            
            # Get the icon path
            icon_path = os.path.abspath(os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'resources', 'icon.ico'
            ))
            
            if not os.path.exists(icon_path):
                logger.error(f"Icon not found at: {icon_path}")
                return False
                
            logger.info(f"Using Windows icon: {icon_path}")
            
            # Register a window class with our icon explicitly
            wc = win32gui.WNDCLASS()
            wc.hIcon = win32gui.LoadImage(
                0, icon_path, win32con.IMAGE_ICON,
                0, 0, win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            )
            wc.lpszClassName = "FileFlowWindowClass"
            win32gui.RegisterClass(wc)
            logger.info("Registered custom Windows window class with icon")
            
            return "FileFlowWindowClass"
            
        except ImportError:
            logger.warning("Windows-specific modules not available. Skipping Windows icon fixes.")
            return True
        except Exception as e:
            logger.error(f"Failed to apply Windows icon fix: {e}")
            return False
    
    @staticmethod
    def _apply_linux_icon_fix():
        """Apply Linux-specific icon fixes."""
        try:
            # On Linux, we primarily rely on PyQt5's icon handling
            # and desktop file integration
            
            # Get the icon path (prefer PNG for Linux)
            icon_paths = [
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources', 'icon.png'),
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources', 'icon.ico'),
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources', 'icon.svg')
            ]
            
            icon_path = None
            for path in icon_paths:
                if os.path.exists(path):
                    icon_path = path
                    break
            
            if icon_path:
                logger.info(f"Using Linux icon: {icon_path}")
                
                # Set environment variables that help with icon display
                os.environ['QT_QPA_PLATFORMTHEME'] = 'gtk3'
                
                return icon_path
            else:
                logger.warning("No suitable icon found for Linux")
                return True
                
        except Exception as e:
            logger.error(f"Failed to apply Linux icon fix: {e}")
            return False
    
    @staticmethod
    def _apply_macos_icon_fix():
        """Apply macOS-specific icon fixes."""
        try:
            # On macOS, icon handling is typically done through the app bundle
            logger.info("macOS icon handling relies on app bundle configuration")
            return True
        except Exception as e:
            logger.error(f"Failed to apply macOS icon fix: {e}")
            return False
    
    @staticmethod
    def fix_notification_text(notification_text):
        """Ensure no traces of 'Download Organizer' appear in notifications."""
        if not notification_text:
            return "FileFlow"
            
        # Replace any Download Organizer text with FileFlow
        cleaned_text = notification_text.replace("Download Organizer", "FileFlow")
        cleaned_text = cleaned_text.replace("download organizer", "FileFlow")
        cleaned_text = cleaned_text.replace("DownloadOrganizer", "FileFlow")
        
        return cleaned_text
    
    @staticmethod
    def setup_autostart(enable=True):
        """Set up application autostart across platforms."""
        if sys.platform == 'win32':
            return CrossPlatformAppFixes._setup_windows_autostart(enable)
        elif sys.platform.startswith('linux'):
            return CrossPlatformAppFixes._setup_linux_autostart(enable)
        elif sys.platform == 'darwin':
            return CrossPlatformAppFixes._setup_macos_autostart(enable)
        else:
            logger.warning(f"Autostart not supported on platform: {sys.platform}")
            return False
    
    @staticmethod
    def _setup_windows_autostart(enable):
        """Set up Windows autostart via registry."""
        try:
            import winreg
            
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            app_name = "FileFlow"
            
            if enable:
                # Get the executable path
                if getattr(sys, 'frozen', False):
                    exe_path = sys.executable
                else:
                    # For development, use python script
                    script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src', 'ui_app.py')
                    exe_path = f'python "{script_path}" --minimized'
                
                # Add to registry
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
                
                logger.info(f"Added Windows autostart entry: {exe_path}")
            else:
                # Remove from registry
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                        winreg.DeleteValue(key, app_name)
                    logger.info("Removed Windows autostart entry")
                except FileNotFoundError:
                    logger.info("Windows autostart entry was not present")
            
            return True
            
        except ImportError:
            logger.warning("Windows registry module not available")
            return False
        except Exception as e:
            logger.error(f"Failed to set Windows autostart: {e}")
            return False
    
    @staticmethod
    def _setup_linux_autostart(enable):
        """Set up Linux autostart via .desktop file."""
        try:
            autostart_dir = Path.home() / '.config' / 'autostart'
            desktop_file = autostart_dir / 'fileflow.desktop'
            
            if enable:
                # Create autostart directory if it doesn't exist
                autostart_dir.mkdir(parents=True, exist_ok=True)
                
                # Get the executable path
                if getattr(sys, 'frozen', False):
                    exe_path = sys.executable
                else:
                    # For development, use python script
                    script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src', 'ui_app.py')
                    exe_path = f'python3 "{script_path}" --minimized'
                
                # Get icon path
                icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources', 'icon.png')
                if not os.path.exists(icon_path):
                    icon_path = 'fileflow'  # Fallback to system icon name
                
                # Create .desktop file content
                desktop_content = f"""[Desktop Entry]
Type=Application
Name=FileFlow
Comment=Automatic file organization tool
Exec={exe_path}
Icon={icon_path}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
StartupNotify=false
Terminal=false
Categories=Utility;
"""
                
                # Write the desktop file
                with open(desktop_file, 'w') as f:
                    f.write(desktop_content)
                
                # Make it executable
                os.chmod(desktop_file, 0o755)
                
                logger.info(f"Created Linux autostart file: {desktop_file}")
            else:
                # Remove the desktop file
                if desktop_file.exists():
                    desktop_file.unlink()
                    logger.info(f"Removed Linux autostart file: {desktop_file}")
                else:
                    logger.info("Linux autostart file was not present")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set Linux autostart: {e}")
            return False
    
    @staticmethod
    def _setup_macos_autostart(enable):
        """Set up macOS autostart via launchd."""
        try:
            # macOS autostart implementation would go here
            # For now, just log that it's not implemented
            logger.warning("macOS autostart not yet implemented")
            return False
        except Exception as e:
            logger.error(f"Failed to set macOS autostart: {e}")
            return False

def apply_all_fixes():
    """Apply all fixes and return any needed variables."""
    logger.info("Applying FileFlow cross-platform fixes")
    
    # Apply platform-specific icon fixes
    icon_result = CrossPlatformAppFixes.apply_app_icon_fix()
    
    # Return any values needed by the main application
    return {
        "icon_result": icon_result,
        "platform": sys.platform
    }

# Maintain backward compatibility
WindowsAppFixes = CrossPlatformAppFixes

# Can be run directly for testing
if __name__ == "__main__":
    results = apply_all_fixes()
    print(f"Fixes applied with results: {results}")
