#!/usr/bin/env python3
"""
Launcher script for SELO FileFlow.
This script can launch either the command-line or graphical user interface version.
"""

import sys
import os
import argparse
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Import the user_dirs module after adding project root to path
from src.modules.user_dirs import user_dirs

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='SELO FileFlow - Automatically organize downloaded files')
    # Use user_dirs to determine default config path
    default_config = str(user_dirs.get_file_path('config', 'settings.yaml'))
    parser.add_argument('--config', type=str, default=default_config,
                      help='Path to configuration file')
    parser.add_argument('--daemon', action='store_true', help='Run in daemon mode (CLI only)')
    parser.add_argument('--process-once', action='store_true', 
                      help='Process files once and exit (CLI only)')
    parser.add_argument('--ui', action='store_true', help='Launch with graphical user interface')
    parser.add_argument('--minimized', action='store_true', help='Start UI minimized to system tray')
    return parser.parse_args()

if __name__ == "__main__":
    # Get and ensure logs directory exists using user_dirs module
    logs_dir = user_dirs.get_dir('logs')
    
    # Check if running as a packaged application
    is_frozen = user_dirs.is_frozen
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Default to UI mode when running as packaged application unless explicitly set to CLI mode
    use_ui = args.ui or (is_frozen and not (args.daemon or args.process_once))
    
    if use_ui:
        # Launch the GUI version
        from src.ui_app import main as ui_main
        # Pass our args directly to the UI app
        sys.argv = [sys.argv[0]]
        if args.config:
            sys.argv.extend(['--config', args.config])
        if args.minimized:
            sys.argv.append('--minimized')
        ui_main()
    else:
        # Launch the CLI version
        from src.main import main as cli_main
        cli_main()
