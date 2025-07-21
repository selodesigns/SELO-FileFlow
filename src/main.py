#!/usr/bin/env python3
"""
SELO FileFlow main module.
Monitors download directory and organizes files based on their types.
"""

import sys
import time
import logging
import argparse
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from watchdog.observers import Observer

from src.modules.file_handler import FileHandler
from src.modules.config_manager import ConfigManager
from src.modules.event_handler import FileEventHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).parent.parent / 'logs' / 'fileflow.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='FileFlow - Automatically organize downloaded files')
    parser.add_argument('--config', type=str, default=str(Path(__file__).parent.parent / 'config' / 'settings.yaml'),
                      help='Path to configuration file')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--process-once', action='store_true', 
                      help='Process files once and exit (for scheduled task usage)')
    return parser.parse_args()

def main():
    """Main function to start FileFlow."""
    args = parse_arguments()
    
    try:
        # Create logs directory if it doesn't exist
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # Load configuration
        config_path = Path(args.config)
        if not config_path.exists():
            logger.error(f"Configuration file not found: {config_path}")
            sys.exit(1)
        
        config_manager = ConfigManager(config_path)
        config = config_manager.get_config()
        
        # Create file handler
        file_handler = FileHandler(config)
        
        # Get source directory
        source_dir = Path(config['source_directory']).expanduser().resolve()
        if not source_dir.exists():
            logger.error(f"Source directory does not exist: {source_dir}")
            sys.exit(1)
        
        # If process-once flag is set, just process existing files and exit
        if args.process_once:
            logger.info(f"Processing files in: {source_dir} (one-time mode)")
            processed_count = 0
            
            for file_path in source_dir.iterdir():
                if file_path.is_file():
                    if file_handler.process_file(file_path):
                        processed_count += 1
            
            logger.info(f"Processed {processed_count} files. Exiting.")
            return
        
        # Otherwise, set up continuous monitoring
        # Create event handler and observer
        event_handler = FileEventHandler(file_handler)
        observer = Observer()
        
        logger.info(f"Starting to monitor directory: {source_dir}")
        observer.schedule(event_handler, str(source_dir), recursive=False)
        observer.start()
        
        # Process existing files if configured to do so
        if config.get('organize_existing_files', True):
            logger.info("Processing existing files...")
            for file_path in source_dir.iterdir():
                if file_path.is_file():
                    file_handler.process_file(file_path)
        
        try:
            # Check if running as bundled executable (stdin might not be available)
            is_bundled = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
            
            if args.daemon or is_bundled:
                logger.info("Running in background mode. Press Ctrl+C to exit.")
                while True:
                    time.sleep(1)
            else:
                # Only use input() when running from source and stdin is available
                try:
                    input("Press Enter to exit...\n")
                except (EOFError, RuntimeError):
                    # Fallback if stdin is not available
                    while True:
                        time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping observer...")
            observer.stop()
        
        observer.join()
        logger.info("Observer stopped. Exiting...")
    
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
