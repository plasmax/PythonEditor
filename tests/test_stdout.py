####!/opt/foundry/nuke-10.0v4/nuke
######----- OLD# !/net/homes/mlast/bin/nuke-python-gui
from __future__ import print_function
import os
import sys
import unittest
import types
import nuke

# module we're testing
import PythonEditor

# ----------------------------    TEST FUNCTIONS    ---------------------------- #


def test_stdout_savedStream():
    """
    Cannot test for pre-import conditions inside this
    file (menu.py is loaded before script execution)
    """
    assert hasattr(sys.stdout, 'savedStream')


def test_stdout_saved_stream():
    assert hasattr(sys.stdout, 'saved_stream')


def test_panel_registered():
    assert nukescripts.panels.__panels.get('Python.Editor') is not None


def test_xml_exists():
    assert os.path.exists(PythonEditor.ui.features.autosavexml.AUTOSAVE_FILE)


"""
def test_
def test_
def test_
def test_autosave():
def test_load_tabs():
def test_readautosave():
def test_save():
def test_saveas():
"""



# ----------------------------END OF TEST FUNCTIONS ---------------------------- #


def print(*args, **kwargs):
    for arg in args:
        nuke.tprint(arg)


def run_all_tests():
    for obj in globals().values():
        if not isinstance(obj, types.FunctionType):
            continue
        name = obj.func_name
        if not name.startswith('test_'):
            continue
        print('Running %s' % name)
        try:
            obj.__call__()
            print(' -- OK')
        except AssertionError as e:
            print('# '+'-'*20)
            print('Test %s FAILED.\n%s\n' % (name, e))


if __name__ == '__main__':
    if os.getenv('PYTHONEDITOR_TEST_SUITE_VARIABLE') == 'test':
        run_all_tests()

    # terminate the app at the end of the test.
    raise SystemExit
