from __future__ import print_function
import sys
import logging


logger = logging.getLogger('PythonEditor')

handlers = logger.handlers
for handler in handlers:
    logger.removeHandler(handler)

handler = logging.StreamHandler(sys.stdout)
format_string = '[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s'
format_string = '%(asctime)s, %(levelname)-8s [%(filename)s:%(module)s:%(funcName)s:%(lineno)d] %(message)s'
formatter = logging.Formatter(format_string)
handler.setFormatter(formatter)
logger.addHandler(handler)

# logging.basicConfig(format=format_string, datefmt='%Y-%m-%d:%H:%M:%S', level=logging.DEBUG)
