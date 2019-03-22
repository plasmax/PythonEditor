from __future__ import print_function
import sys

from PythonEditor.core import streams
from PythonEditor.utils.constants import DEFAULT_FONT
from PythonEditor.ui.Qt import QtGui, QtWidgets, QtCore
from PythonEditor.utils.debug import debug


class Terminal(QtWidgets.QPlainTextEdit):
    """ Output text display widget """
    link_activated = QtCore.Signal(str)

    def __init__(self):
        super(Terminal, self).__init__()

        self.setObjectName('Terminal')
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint
        )
        self.setReadOnly(True)
        self.setup()
        self.destroyed.connect(self.stop)
        font = QtGui.QFont(DEFAULT_FONT)
        font.setPointSize(10)
        self.setFont(font)

    @QtCore.Slot(str)
    def receive(self, text):
        try:
            textCursor = self.textCursor()
            if bool(textCursor):
                self.moveCursor(
                    QtGui.QTextCursor.End
                )
        except Exception:
            pass
        self.insertPlainText(text)

    def stop(self):
        for stream in sys.stdout, sys.stderr:
            if hasattr(stream, 'reset'):
                stream.reset()

    def setup(self):
        """
        Checks for an existing stream wrapper
        for sys.stdout and connects to it. If
        not present, creates a new one.
        TODO:
        The FnRedirect sys.stdout is always active.
        With a singleton object on a thread,
        that reads off this stream, we can make it
        available to Python Editor even before opening
        the panel.
        """
        if hasattr(sys.stdout, '_signal'):
            self.speaker = sys.stdout._signal
        else:
            self.speaker = streams.Speaker()
            sys.stdout = streams.SESysStdOut(sys.stdout, self.speaker)
            sys.stderr = streams.SESysStdErr(sys.stderr, self.speaker)

        self.speaker.emitter.connect(self.receive)

    def mousePressEvent(self, e):
        if not hasattr(self, 'anchorAt'):
            # pyqt doesn't use anchorAt
            return super(Terminal, self).mousePressEvent(e)

        if (e.button() == QtCore.Qt.LeftButton):
            clickedAnchor = self.anchorAt(e.pos())
            if clickedAnchor:
                self.link_activated.emit(clickedAnchor)
        super(Terminal, self).mousePressEvent(e)
