"""
Event handler for the FileFlow application.
Monitors file system events and triggers file processing.
"""

import logging
import time
from pathlib import Path
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

class FileEventHandler(FileSystemEventHandler):
    """
    Event handler for file system events.
    Processes files when they are created or modified in the monitored directory.
    """
    
    def __init__(self, file_handler):
        """
        Initialize the event handler.
        
        Args:
            file_handler (FileHandler): The file handler to use for processing files.
        """
        self.file_handler = file_handler
        # Keep track of recently processed files to avoid duplicates
        self.recently_processed = {}
        # Debounce time in seconds
        self.debounce_time = 3
    
    def on_created(self, event):
        """
        Handle file creation events.
        
        Args:
            event (FileSystemEvent): The file system event.
        """
        if event.is_directory:
            return
        
        self._process_event(event.src_path)
    
    def on_modified(self, event):
        """
        Handle file modification events.
        
        Args:
            event (FileSystemEvent): The file system event.
        """
        if event.is_directory:
            return
        
        self._process_event(event.src_path)
    
    def on_moved(self, event):
        """
        Handle file move events.
        
        Args:
            event (FileSystemEvent): The file system event.
        """
        if event.is_directory:
            return
        
        # Only process destination if it's in our monitored directory
        self._process_event(event.dest_path)
    
    def _process_event(self, file_path):
        """
        Process a file event with debouncing to avoid processing the same file multiple times.
        
        Args:
            file_path (str): Path to the file to process.
        """
        try:
            path_obj = Path(file_path)
            
            # Skip if not a file
            if not path_obj.is_file():
                return
            
            # Skip if file was recently processed
            current_time = time.time()
            if file_path in self.recently_processed:
                last_processed = self.recently_processed[file_path]
                if current_time - last_processed < self.debounce_time:
                    logger.debug(f"Skipping recently processed file: {file_path}")
                    return
            
            # Mark file as recently processed
            self.recently_processed[file_path] = current_time
            
            # Clean up old entries from recently_processed
            self._clean_processed_cache()
            
            # Process the file after a short delay to ensure it's fully written
            logger.info(f"New file detected: {path_obj.name}")
            
            # Give the file a moment to finish being written/downloaded
            time.sleep(1)
            
            # Process the file
            self.file_handler.process_file(file_path)
            
        except Exception as e:
            logger.error(f"Error processing event for file '{file_path}': {e}")
    
    def _clean_processed_cache(self):
        """Clean up old entries from the recently processed cache."""
        current_time = time.time()
        expired_paths = [
            path for path, timestamp in self.recently_processed.items()
            if current_time - timestamp > self.debounce_time * 5
        ]
        
        for path in expired_paths:
            del self.recently_processed[path]
