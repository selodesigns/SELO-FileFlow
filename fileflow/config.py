import os
import yaml
from pathlib import Path

XDG_CONFIG_HOME = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))
APP_CONFIG_DIR = XDG_CONFIG_HOME / 'selo-fileflow'
CONFIG_FILE = APP_CONFIG_DIR / 'config.yaml'

DEFAULT_CONFIG = {
    'source_directories': [str(Path.home() / 'Downloads')],
    'destination_directories': {
        'images': str(Path.home() / 'Pictures'),
        'documents': str(Path.home() / 'Documents'),
        'videos': str(Path.home() / 'Videos'),
        'music': str(Path.home() / 'Music'),
        'archives': str(Path.home() / 'Downloads/Archives'),
        'software': str(Path.home() / 'Downloads/Software'),
        'other': str(Path.home() / 'Downloads/Other')
    },
    'file_types': {
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
        'documents': ['.pdf', '.docx', '.doc', '.txt', '.odt', '.xlsx', '.pptx'],
        'videos': ['.mp4', '.avi', '.mov', '.mkv', '.webm'],
        'music': ['.mp3', '.wav', '.ogg', '.flac'],
        'archives': ['.zip', '.tar', '.gz', '.rar', '.7z'],
        'software': ['.sh', '.AppImage', '.deb', '.rpm', '.bin', '.run'],
        'other': []
    },
    'notify_on_move': True,
    'autostart': True
}

def ensure_config_dir():
    APP_CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config():
    ensure_config_dir()
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return yaml.safe_load(f)
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()


def save_config(config):
    ensure_config_dir()
    with open(CONFIG_FILE, 'w') as f:
        yaml.safe_dump(config, f)
