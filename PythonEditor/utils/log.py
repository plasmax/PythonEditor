from __future__ import print_function
import os
import sys
import logging
from logging.handlers import RotatingFileHandler


logger = logging.getLogger('PythonEditor')
logger.setLevel(logging.DEBUG)
logger.propagate = False

handlers = logger.handlers
for handler in handlers:
    logger.removeHandler(handler)

handler = logging.StreamHandler(sys.stdout)
format_string = '[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s'
format_string = '%(asctime)s, %(levelname)-8s [%(filename)s:%(module)s:%(funcName)s:%(lineno)d] %(message)s'
formatter = logging.Formatter(format_string)
handler.setFormatter(formatter)
logger.addHandler(handler)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
LOG_DIR = os.getenv('PYTHONEDITOR_LOG_DIR', os.path.join(ROOT_DIR, 'logs'))
LOG_PATH = os.path.join(LOG_DIR, 'pythoneditor.log')

try:
    os.makedirs(LOG_DIR, exist_ok=True)
    file_handler = RotatingFileHandler(
        LOG_PATH,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
except Exception:
    pass


def get_log_path():
    return LOG_PATH
