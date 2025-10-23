"""
Thread-safe watcher manager for controlling the FileFlow file watcher daemon
from the web API.
"""

import threading
import time
from pathlib import Path
from typing import Optional
from watchdog.observers import Observer

from ..config import load_config
from ..watcher import FileFlowEventHandler
from ..utils.logging import get_logger

logger = get_logger()


class WatcherManager:
    """
    Manages the file watcher lifecycle in a thread-safe manner.
    
    Allows the web API to start/stop the watcher without blocking.
    """
    
    def __init__(self):
        self._observer: Optional[Observer] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.Lock()
        self._start_time: Optional[float] = None
    
    def is_running(self) -> bool:
        """Check if the watcher is currently running."""
        with self._lock:
            return self._running and self._observer is not None
    
    def start(self) -> None:
        """Start the file watcher in a background thread."""
        with self._lock:
            if self._running:
                logger.warning("Watcher is already running")
                return
            
            logger.info("Starting file watcher...")
            
            config = load_config()
            src_dirs = config.get('source_directories', [])
            
            if not src_dirs:
                raise ValueError("No source directories configured")
            
            # Create observer and schedule handlers
            self._observer = Observer()
            event_handler = FileFlowEventHandler()
            
            for src_dir in src_dirs:
                src_path = Path(src_dir).expanduser()
                if src_path.exists():
                    self._observer.schedule(event_handler, str(src_path), recursive=False)
                    logger.info(f"Watching directory: {src_path}")
                else:
                    logger.warning(f"Source directory does not exist: {src_path}")
            
            # Start observer
            self._observer.start()
            self._running = True
            self._start_time = time.time()
            
            logger.info("File watcher started successfully")
    
    def stop(self) -> None:
        """Stop the file watcher."""
        with self._lock:
            if not self._running or self._observer is None:
                logger.warning("Watcher is not running")
                return
            
            logger.info("Stopping file watcher...")
            
            try:
                self._observer.stop()
                self._observer.join(timeout=5.0)
                self._running = False
                self._observer = None
                self._start_time = None
                
                logger.info("File watcher stopped successfully")
            
            except Exception as e:
                logger.error(f"Error stopping watcher: {e}")
                self._running = False
                self._observer = None
                self._start_time = None
                raise
    
    def get_uptime(self) -> Optional[float]:
        """Get watcher uptime in seconds."""
        with self._lock:
            if self._running and self._start_time is not None:
                return time.time() - self._start_time
            return None
    
    def restart(self) -> None:
        """Restart the file watcher."""
        logger.info("Restarting file watcher...")
        self.stop()
        time.sleep(1)  # Brief pause before restart
        self.start()
