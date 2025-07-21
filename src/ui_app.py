#!/usr/bin/env python3
"""
UI Application entry point for SELO FileFlow.
Launches the PyQt5-based graphical user interface.
"""

import sys
import os
import logging
import argparse
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.modules.ui_manager import run_ui
from src.set_app_id import set_app_id
from src.modules.user_dirs import user_dirs

# Get logs directory using user_dirs module
logs_dir = user_dirs.get_dir('logs')
log_file = logs_dir / 'fileflow.log'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file, mode='a')
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='SELO FileFlow UI - Graphical interface for file organization')
    # Use user_dirs to get the appropriate config path
    default_config = str(user_dirs.get_file_path('config', 'settings.yaml'))
    parser.add_argument('--config', type=str, default=default_config,
                      help='Path to configuration file')
    parser.add_argument('--minimized', action='store_true', help='Start minimized to system tray')
    return parser.parse_args()

def main():
    """Main function to start the UI application."""
    try:
        # Logs directory is already set up in the logging configuration above
        
        # CROSS-PLATFORM FIX: Apply platform-specific application setup
        try:
            from PyQt5.QtWidgets import QApplication
            from PyQt5.QtGui import QIcon
            from src.modules.direct_fixes import CrossPlatformAppFixes
            
            # Apply cross-platform fixes
            fixes_result = CrossPlatformAppFixes.apply_app_icon_fix()
            logger.info(f"Applied cross-platform fixes: {fixes_result}")
            
            # Determine icon path - important to find it in various environments
            icon_extensions = ['.png', '.ico', '.svg'] if sys.platform.startswith('linux') else ['.ico', '.png', '.svg']
            icon_paths = []
            
            for ext in icon_extensions:
                icon_paths.extend([
                    # Development path
                    str(Path(__file__).parent.parent / 'resources' / f'icon{ext}'),
                    # PyInstaller bundled paths
                    f'icon{ext}',
                    f'resources/icon{ext}',
                    str(Path('resources') / f'icon{ext}')
                ])
            
            # Check for PyInstaller bundle
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                # Add PyInstaller-specific paths
                for ext in icon_extensions:
                    icon_paths.extend([
                        str(Path(sys._MEIPASS) / f'icon{ext}'),
                        str(Path(sys._MEIPASS) / 'resources' / f'icon{ext}')
                    ])
            
            # Find first valid icon path
            icon_path = None
            for path in icon_paths:
                if os.path.exists(path):
                    icon_path = path
                    logger.info(f"Found icon at: {icon_path}")
                    break
            
            if icon_path:
                # Initialize QApplication early to set the icon
                if QApplication.instance() is None:
                    app = QApplication(sys.argv)
                else:
                    app = QApplication.instance()
                
                # Set application icon
                app_icon = QIcon(icon_path)
                app.setWindowIcon(app_icon)
                
                logger.info(f"Set application icon: {icon_path}")
            else:
                logger.warning("Could not find application icon!")
                
        except Exception as e:
            logger.error(f"Application setup error: {e}")
        
        # Parse arguments
        args = parse_arguments()
        
        # Launch UI
        logger.info("Starting FileFlow UI")
        run_ui(config_path=args.config)
        
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
