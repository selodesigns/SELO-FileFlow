#!/usr/bin/env python3
import os
import sys
import pwd
from pathlib import Path


def resolve_user_home() -> Path:
    sudo_user = os.environ.get('SUDO_USER')
    if sudo_user:
        try:
            return Path(pwd.getpwnam(sudo_user).pw_dir)
        except KeyError:
            pass
    return Path(os.environ.get('HOME', str(Path.home())))


USER_HOME = resolve_user_home()
os.environ['HOME'] = str(USER_HOME)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fileflow.config import ensure_config_dir, load_config, save_config

SERVER_ROOT = Path('/mnt/server')
SOURCE_DIR = USER_HOME / 'Downloads'
DESTINATIONS = {
    'images': SERVER_ROOT / 'Photos',
    'videos': SERVER_ROOT / 'Videos',
    'documents': SERVER_ROOT / 'Documents',
    'music': USER_HOME / 'Music',
    'archives': SERVER_ROOT / 'Installations',
    'software': SERVER_ROOT / 'Installations',
    'other': SERVER_ROOT / 'Miscellaneous',
}


def main() -> None:
    ensure_config_dir()
    config = load_config() or {}
    config['source_directories'] = [str(SOURCE_DIR)]
    config.setdefault('destination_directories', {})
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    for key, path in DESTINATIONS.items():
        path.mkdir(parents=True, exist_ok=True)
        config['destination_directories'][key] = str(path)
    save_config(config)


if __name__ == '__main__':
    main()
