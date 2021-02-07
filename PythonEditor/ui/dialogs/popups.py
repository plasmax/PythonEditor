import re

from PythonEditor.ui.Qt import QtWidgets
from PythonEditor.ui.Qt import QtGui
from PythonEditor.ui.Qt import QtCore

from PythonEditor.utils.goto import goto_line


class CommandPalette(QtWidgets.QLineEdit):
    """
    The base class for a LineEdit widget that
    appears over a parent widget and can be
    used for entering commands, searching, etc.
    """
    location = QtCore.Qt.BottomSection
    location = QtCore.Qt.TopSection
    def __init__(self, parent=None):
        super(CommandPalette, self).__init__()
        self._parent = parent
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.FramelessWindowHint
        )
        self.editingFinished.connect(self.hide)
        font = self.font()
        font.setPointSize(12)
        font.setBold(False)
        self.setFont(font)
        self.place_over_parent()

    def parent(self):
        return self._parent

    def keyPressEvent(self, event):
        esc = QtCore.Qt.Key.Key_Escape
        if event.key() == esc:
            self.hide()
        super(
            CommandPalette, self
        ).keyPressEvent(event)

    def showEvent(self, event):
        self.parent().installEventFilter(self)
        self.setFocus(QtCore.Qt.MouseFocusReason)
        if event.type() != QtCore.QEvent.Show:
            return
        super(CommandPalette, self).showEvent(event)
        self.place_over_parent()

    def hideEvent(self, event):
        self.parent().removeEventFilter(self)
        if event.type() != QtCore.QEvent.Hide:
            return
        super(CommandPalette, self).hideEvent(event)
        self.parent().setFocus(QtCore.Qt.MouseFocusReason)

    def place_over_parent(self):
        if self.location == QtCore.Qt.TopSection:
            self.move_to_top()
        elif self.location == QtCore.Qt.BottomSection:
            self.move_to_bottom()

    def move_to_top(self):
        geo = self.parent().geometry()
        centre = geo.center()
        x = centre.x()-(self.width()/2)
        y = geo.top()-12
        pos = QtCore.QPoint(x, y)
        pos = self.parent().mapToGlobal(pos)
        self.move(pos)

    def move_to_bottom(self):
        geo = self.parent().geometry()
        centre = geo.center()
        x = centre.x()-(self.width()/2)
        y = geo.bottom()-70
        pos = QtCore.QPoint(x, y)
        pos = self.parent().mapToGlobal(pos)
        self.move(pos)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Move:
            self.place_over_parent()
        elif event.type() == QtCore.QEvent.Resize:
            self.place_over_parent()
        elif event.type() == QtCore.QEvent.Hide:
            self.hide()
        return False


class GotoPalette(CommandPalette):
    def __init__(self, editor):
        super(GotoPalette, self).__init__(editor)
        self.editor = editor
        self.setPlaceholderText('enter line number')
        self.current_line = editor.textCursor(
            ).block(
            ).blockNumber()+1
        # self.setText(str(self.current_line))

    def keyPressEvent(self, event):
        esc = QtCore.Qt.Key.Key_Escape
        if event.key() == esc:
            goto_line(self.editor, self.current_line)
            self.hide()

        if event.text().isalpha():
            return

        super(GotoPalette, self).keyPressEvent(event)
        try:
            lineno = int(self.text())
        except ValueError:
            return
        goto_line(self.editor, lineno)
