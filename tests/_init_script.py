"""
Executed on nuke startup to load PythonEditor
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

if ('nuke' in globals() and nuke.GUI):
    import PythonEditor
    from PythonEditor.ui.nukefeatures import nukeinit
    nukeinit.setup()
