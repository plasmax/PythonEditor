import os
import sys
import nuke

nuke.tprint('MENU.PY')

__folder__ = os.path.dirname(os.path.dirname(__file__))
sys.path.append(__folder__)

os.environ['PYTHONEDITOR_TEST_SUITE_VARIABLE'] = 'test'
os.environ['PYTHONEDITOR_CUSTOM_DIR'] = os.path.join(
    os.path.expanduser('~'),
    'Desktop',
    'TEST' # will only work if there's a folder called TEST on the Desktop.
)
import PythonEditor
PythonEditor.nuke_menu_setup()
