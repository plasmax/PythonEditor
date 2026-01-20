from __future__ import print_function
import os
import re
import sys

from PythonEditor.core import streams
from PythonEditor.utils.constants import DEFAULT_FONT
from PythonEditor.ui.Qt.QtGui import (QFont,
                                      QTextCursor,
                                      QCursor,
                                      QClipboard)
from PythonEditor.ui.Qt.QtCore import (Qt,
                                       Signal,
                                       Slot,
                                       QTimer)
from PythonEditor.ui.Qt.QtWidgets import QPlainTextEdit
from PythonEditor.utils.debug import debug
from PythonEditor.ui.features.actions import get_external_editor_path
from PythonEditor.ui.features.actions import open_in_external_editor


STARTUP = 'PYTHONEDITOR_CAPTURE_STARTUP_STREAMS'

class Terminal(QPlainTextEdit):
    """ Output text display widget """

    def __init__(self):
        super(Terminal, self).__init__()

        self.setObjectName('Terminal')
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint
        )
        self.setReadOnly(True)
        self.destroyed.connect(self.stop)
        font = QFont(DEFAULT_FONT)
        font.setPointSize(10)
        self.setFont(font)

        if os.getenv(STARTUP) == '1':
            self.setup()
        else:
            QTimer.singleShot(0, self.setup)

    @Slot(str)
    def receive(self, text):
        try:
            textCursor = self.textCursor()
            if bool(textCursor):
                self.moveCursor(
                    QTextCursor.End
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

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        path_in_line = self.path_in_line(
            self.line_from_event(event)
        )
        if path_in_line:
            def _goto():
                goto(path_in_line)
            menu.addAction('Goto {0}'.format(path_in_line), _goto)
        menu.addAction('Parse Last Traceback', self.parse_last_traceback)
        menu.exec_(QCursor().pos())

    def line_from_event(self, event):
        pos = event.pos()
        cursor = self.cursorForPosition(pos)
        block_under_cursor = getattr(QTextCursor, "BlockUnderCursor", None)
        if block_under_cursor is None and hasattr(QTextCursor, "SelectionType"):
            block_under_cursor = QTextCursor.SelectionType.BlockUnderCursor
        if block_under_cursor is not None:
            cursor.select(block_under_cursor)
        selection = cursor.selection()
        text = selection.toPlainText().strip()
        return text

    def path_in_line(self, text):
        """
        Parse the line under the cursor
        to see if it contains a path to a
        file. If it does, return it.
        """
        pattern = re.compile(r'([\w\-\.\/\\]+)(", line )(\d+)')
        path = ''
        for fp, _, lineno in re.findall(pattern, text):
            return ':'.join([fp, lineno])
        return None

    def parse_last_traceback(self):
        tb = self.toPlainText().split('Traceback')[-1]
        pattern = re.compile(r'(File ")([\w\.\/]+)(", line )(\d+)')
        text = ''
        for _, fp, _, lineno in re.findall(pattern, tb):
            text += 'sublime '+':'.join([fp, lineno])
            text += '\n'

        print(text)
        QClipboard().setText(text)


def goto(path):
    eepath = get_external_editor_path()
    if eepath is not None:
        # this assumes the external
        # editor can handle paths
        # with path:lineno
        print('Going to:')
        print(path)
        open_in_external_editor(path)
