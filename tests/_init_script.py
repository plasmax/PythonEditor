"""
Can be executed on Nuke startup to load PythonEditor.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

if ('nuke' in globals() and nuke.GUI):
    import PythonEditor
    from PythonEditor.utils.constants import NUKE_DIR
    PythonEditor.nuke_menu_setup(node_menu=True, nuke_menu=True)
