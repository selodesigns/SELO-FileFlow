import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .config import load_config
from .organizer import organize_path
from .utils.logging import get_logger

logger = get_logger()

class FileFlowEventHandler(FileSystemEventHandler):
    def _handle_file(self, path: str):
        file_path = Path(path)
        if not file_path.is_file():
            return
        try:
            result = organize_path(file_path)
            dest = result.get('destination') if isinstance(result, dict) else None
            if dest:
                logger.info(f"Organized {file_path} -> {dest}")
        except FileNotFoundError:
            logger.debug(f"Watcher skipped missing file: {file_path}")
        except Exception as exc:
            logger.error(f"Watcher failed to organize {file_path}: {exc}")

    def on_created(self, event):
        if not event.is_directory:
            logger.info(f"Detected new file: {event.src_path}")
            self._handle_file(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            logger.info(f"Detected moved file: {event.dest_path}")
            self._handle_file(event.dest_path)

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
