# Legacy organizer - now imports from enhanced_content_organizer for visual analysis
from pathlib import Path

from .config import load_config as _load_config
from .content_organizer import ContentOrganizer
from .enhanced_content_organizer import EnhancedContentOrganizer
from .ui.notifications import send_notification as _send_notification
from .utils.logging import get_logger

load_config = _load_config
send_notification = _send_notification

logger = get_logger()

# Re-export the main functions for backward compatibility
__all__ = ['organize_files', 'reorganize_existing_files', 'organize_path', 'get_category_for_file', 'load_config', 'send_notification']


def get_category_for_file(filename, file_types):
    ext = Path(filename).suffix.lower()
    for category, extensions in file_types.items():
        if ext in extensions:
            return category
    return 'other'


def _should_use_enhanced(config, dest_override=None):
    return bool(dest_override or config.get('dest') or config.get('user_destination'))


def _get_organizer(config, dest_override=None):
    if _should_use_enhanced(config, dest_override):
        organizer = EnhancedContentOrganizer()
    else:
        organizer = ContentOrganizer()
    organizer.config = config
    return organizer


def organize_path(path, dest=None):
    config = load_config()
    if dest is not None:
        config['dest'] = dest
    organizer = _get_organizer(config, dest)
    return organizer.organize_path(Path(path))


def organize_files(sources=None, dest=None):
    config = load_config()
    if sources is not None:
        config['source_directories'] = list(sources)
    if dest is not None:
        config['dest'] = dest
    organizer = _get_organizer(config, dest)
    organizer.organize_files()


def reorganize_existing_files(target_dirs=None, dest=None):
    config = load_config()
    if dest is not None:
        config['dest'] = dest
    organizer = _get_organizer(config, dest)
    organizer.reorganize_existing_files(target_dirs)
