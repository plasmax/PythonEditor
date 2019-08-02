# standard library imports
import sys

# module we're testing
from PythonEditor.ui.ide import IDE


def test_savedStream(qtbot):
    """ Assert that stdout and stderr are being
    captured by PythonEditor stream handlers.
    """
    ide = IDE()
    ide.show()
    qtbot.addWidget(ide)
    qtbot.waitForWindowShown(ide)

    assert hasattr(sys.stdout, 'saved_stream')
    assert hasattr(sys.stderr, 'saved_stream')

    print(sys.stdout)
    print(sys.stdout.saved_stream)

