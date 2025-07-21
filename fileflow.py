#!/usr/bin/env python3
"""
Simple launcher script for FileFlow.
This script can be run directly from a fresh GitHub clone.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def main():
    """Main launcher function."""
    # Check if GUI mode is requested (default) or CLI mode
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        # Remove the --cli flag and pass remaining args to main.py
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        from src.main import main as cli_main
        cli_main()
    else:
        # GUI mode (default)
        from src.ui_app import main as gui_main
        gui_main()

if __name__ == "__main__":
    main()
