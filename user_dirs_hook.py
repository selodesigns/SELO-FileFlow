"""
PyInstaller hook for SELO FileFlow.
This runtime hook ensures proper handling of user directories when running as a packaged application.
"""
import os
import sys
from pathlib import Path

# This will run before the application starts
def setup_user_directories():
    """Set up user-specific directories for the packaged application."""
    try:
        # Check if running as a packaged application
        is_frozen = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
        
        if is_frozen:
            # Determine base user directory for data
            if sys.platform == 'win32':
                # Windows: Use AppData
                base_user_dir = Path(os.environ.get('APPDATA', '')) / "SELOdev" / "FileFlow"
            else:
                # Unix/Linux/Mac: Use ~/.fileflow
                base_user_dir = Path(os.path.expanduser("~")) / ".fileflow"
            
            # Create user directories if they don't exist
            for dir_name in ['config', 'logs', 'data', 'cache']:
                dir_path = base_user_dir / dir_name
                dir_path.mkdir(parents=True, exist_ok=True)
                
            # Copy default config if it doesn't exist in user directory
            user_config = base_user_dir / "config" / "settings.yaml"
            if not user_config.exists():
                # Try to copy from packaged resources
                default_config_paths = [
                    Path(sys._MEIPASS) / "config" / "settings.yaml",
                    Path(sys._MEIPASS) / "settings.yaml"
                ]
                
                for default_config in default_config_paths:
                    if default_config.exists():
                        try:
                            # Create parent directory if needed
                            user_config.parent.mkdir(parents=True, exist_ok=True)
                            
                            # Copy the default config
                            with open(default_config, 'r') as src, open(user_config, 'w') as dst:
                                dst.write(src.read())
                            break
                        except Exception:
                            # Continue to next path if copy fails
                            pass
    except Exception:
        # Don't let errors in this hook prevent the application from starting
        pass

# Run the setup
setup_user_directories()
