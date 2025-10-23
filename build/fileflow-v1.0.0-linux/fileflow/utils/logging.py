import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os

XDG_DATA_HOME = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share'))
LOG_DIR = XDG_DATA_HOME / 'selo-fileflow' / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / 'fileflow.log'


def get_logger(name='fileflow'):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        handler = RotatingFileHandler(LOG_FILE, maxBytes=1024*1024, backupCount=3)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
