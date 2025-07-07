import shutil
from pathlib import Path
from .config import load_config
from .ui.notifications import send_notification
from .utils.logging import get_logger

logger = get_logger()

def get_category_for_file(filename, file_types):
    ext = Path(filename).suffix.lower()
    for category, extensions in file_types.items():
        if ext in extensions:
            return category
    return 'other'


def organize_files():
    config = load_config()
    src_dirs = config['source_directories']
    dest_dirs = config['destination_directories']
    file_types = config['file_types']

    notify = config.get('notify_on_move', True)
    for src_dir in src_dirs:
        src_path = Path(src_dir).expanduser()
        if not src_path.exists():
            logger.error(f"Source directory does not exist: {src_path}")
            continue
        for item in src_path.iterdir():
            if item.is_file():
                category = get_category_for_file(item.name, file_types)
                dest_dir = Path(dest_dirs.get(category, dest_dirs['other'])).expanduser()
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_file = dest_dir / item.name
                try:
                    shutil.move(str(item), str(dest_file))
                    logger.info(f"Moved {item} -> {dest_file}")
                    if notify:
                        send_notification("FileFlow: File Moved", f"{item.name} → {dest_dir}")
                except Exception as e:
                    logger.error(f"Failed to move {item}: {e}")
