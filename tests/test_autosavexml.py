# tests autosave.

import os
import shutil
import pytest
from xml.etree import cElementTree, ElementTree

from PythonEditor.ui.features import autosavexml

@pytest.fixture
def setup_and_teardown_autosave_file():
    """If the autosave file already exists, create a temporary
    backup, then tear down by reinstating the original file."""
    autosave_exists = os.path.isfile(autosavexml.AUTOSAVE_FILE)
    if autosave_exists:
        print("File exists: %s" % autosavexml.AUTOSAVE_FILE)

        shutil.copy2(autosavexml.AUTOSAVE_FILE,
                     autosavexml.AUTOSAVE_FILE+'.bak')
        print("Backed up autosave file to: %s" % autosavexml.AUTOSAVE_FILE+'.bak')
    yield # <- where the test() is run.
    if os.path.exists(autosavexml.AUTOSAVE_FILE+'.bak'):
        if os.path.isfile(autosavexml.AUTOSAVE_FILE):
            print('Removing %s' % autosavexml.AUTOSAVE_FILE)
            os.remove(autosavexml.AUTOSAVE_FILE)
        os.rename(autosavexml.AUTOSAVE_FILE+'.bak', autosavexml.AUTOSAVE_FILE)
        print('Restored original %s' % autosavexml.AUTOSAVE_FILE)
    if (not autosave_exists) and os.path.isfile(autosavexml.AUTOSAVE_FILE):
        os.remove(autosavexml.AUTOSAVE_FILE)


# --- critical autosave functions that are the "write/out" points of the application:

def test_create_autosave_file(setup_and_teardown_autosave_file):
    """Test that the autosave file always exists after calling this function."""
    assert autosavexml.create_autosave_file()
    assert os.path.isfile(autosavexml.AUTOSAVE_FILE)
    assert os.environ["PYTHONEDITOR_AUTOSAVE_FILE"]==autosavexml.AUTOSAVE_FILE


def test_create_empty_autosave(setup_and_teardown_autosave_file):
    """Test that an empty autosave is always created with the appropriate header."""
    autosavexml.create_empty_autosave()
    assert os.path.isfile(autosavexml.AUTOSAVE_FILE)
    assert os.environ["PYTHONEDITOR_AUTOSAVE_FILE"]==autosavexml.AUTOSAVE_FILE
    with open(autosavexml.AUTOSAVE_FILE, 'r') as fd:
        contents = fd.read()
    assert contents == '<?xml version="1.0" encoding="UTF-8"?><script></script>'


def test_writexml(setup_and_teardown_autosave_file):
    """Test that the writexml function writes back sensible data."""
    # make sure we have an autosave file
    if not os.path.isfile(autosavexml.AUTOSAVE_FILE):
        autosavexml.create_autosave_file()
        
    # read the file, then write it back.
    root, elements = autosavexml.parsexml("subscript")
    autosavexml.writexml(root, path=autosavexml.AUTOSAVE_FILE)
    
    # does the file still exist?
    assert os.path.isfile(autosavexml.AUTOSAVE_FILE)
    
    # the file may have had some characters sanitized,
    # but the number of elements should be the same.
    new_root, new_elements = autosavexml.parsexml("subscript")
    assert len(new_elements) == len(elements)

    try:
        unicode
    except NameError:
        # no unicode function in python 3
        def unicode(text): return text

    from PythonEditor.ui.features.autosavexml import sanitize

    # none of the element attributes should have changed
    for old_element, new_element in zip(elements, new_elements):
        assert old_element.attrib == new_element.attrib
        old_text = unicode(old_element.text)
        new_text = unicode(new_element.text)
        assert sanitize(old_text) == sanitize(new_text)


def test_fix_broken_xml(setup_and_teardown_autosave_file):
    if not os.path.isfile(autosavexml.AUTOSAVE_FILE):
        autosavexml.create_autosave_file()
    autosavexml.fix_broken_xml(path=autosavexml.AUTOSAVE_FILE)
    # test that the file can be parsed correctly now
    root, elements = autosavexml.parsexml("subscript", path=autosavexml.AUTOSAVE_FILE)


def test_parsexml(setup_and_teardown_autosave_file):
    root, elements = autosavexml.parsexml("subscript", path=autosavexml.AUTOSAVE_FILE)
    assert isinstance(elements, list)
    assert root is not None


# ---


# --- TODO: test methods picked up by tracing autosave usage with sys.settrace
"""
"PythonEditor.ui.features.autosavexml"
    "AutoSaveManager"
        "__init__
        "setup_save_timer
        "readautosave
        "connect_signals
        "check_autosave_modified
        "remove_existing_popups
        "check_document_modified
        "save_timer
        "autosave_handler
        "autosave
        "save_by_uuid
        "sync_tab_indices
        "store_current_index
        "remove_subscript
        "update_tab_index
        "handle_document_save"
"""
