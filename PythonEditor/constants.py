import sys
import os

if sys.platform == "linux" or sys.platform == "linux2":
    # linux
    path = '/net/homes/'
elif sys.platform == "darwin":
    # OS X
    pass
elif sys.platform == "win32":
    # Windows...
    path = 'C:/Users/'

USER = os.environ.get('USERNAME')
NUKE_DIR = os.path.join(path, USER, '.nuke')
print NUKE_DIR
