import os
import PythonEditor


def test_AUTOSAVE_FILE():
    """ The import process for PythonEditor creates and/or reads
    an autosave file, registered in the AUTOSAVE_FILE global variable.
    """
    assert os.path.exists(PythonEditor.ui.features.autosavexml.AUTOSAVE_FILE)


# def test_PYTHONEDITOR_AUTOSAVE_FILE():
# def test_autosave():
# def test_readautosave():