import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .config import load_config
from .organizer import organize_files
from .utils.logging import get_logger

logger = get_logger()

class FileFlowEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            logger.info(f"Detected new file: {event.src_path}")
            organize_files()
    def on_moved(self, event):
        if not event.is_directory:
            logger.info(f"Detected moved file: {event.dest_path}")
            organize_files()

def start_watching():
    config = load_config()
    src_dirs = config['source_directories']
    event_handler = FileFlowEventHandler()
    observer = Observer()
    for src_dir in src_dirs:
        src_path = Path(src_dir).expanduser()
        observer.schedule(event_handler, str(src_path), recursive=False)
    observer.start()
    print("FileFlow watcher started. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
