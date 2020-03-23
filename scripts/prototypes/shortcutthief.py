from Qt import QtWidgets, QtGui, QtCore
from PythonEditor.utils import eventfilters


def key_to_shortcut(key):
    """
    Convert the given QtCore.Qt.Key type
    to a string including currently held modifiers.
    """
    modifier_map = {
        QtCore.Qt.Key_Control: QtCore.Qt.ControlModifier,
        QtCore.Qt.Key_Shift: QtCore.Qt.ShiftModifier,
        QtCore.Qt.Key_Alt: QtCore.Qt.AltModifier,
        QtCore.Qt.Key_Meta: QtCore.Qt.MetaModifier,
    }
    held = QtWidgets.QApplication.keyboardModifiers()
    combo = 0
    for mod in modifier_map.values():
        if held & mod == mod:
            combo |= mod
    combo |= key

    #print combo
    return combo
    shortcut = QtGui.QKeySequence(combo).toString()
    try:
        shortcut = str(shortcut)
    except UnicodeEncodeError:
        shortcut = repr(shortcut)
    return shortcut



# from PythonEditor. useful!
def remove_panel(PANEL_NAME):
    for stack in QtWidgets.QApplication.instance().allWidgets():
        if not isinstance(stack, QtWidgets.QStackedWidget):
            continue
        for child in stack.children():
            if child.objectName() == PANEL_NAME:
                child.deleteLater()


class ShortcutThief(eventfilters.GenericEventFilter):
    def event_filter(self, obj, event):
        if event.type() == event.Shortcut:
            print('mine!')
            key = event.key()
            print(key)
            print(key)_to_shortcut(key)
            if obj != self.parent():
                event.ignore()
                return True
            return False
        return False


class  Edits(QtWidgets.QPlainTextEdit):
    def focusInEvent(self, event):
        self.thief = ShortcutThief()
        self.thief.setParent(self)
        print(self.thief)
        super(Edits, self).focusInEvent(event)

    def focusOutEvent(self, event):
        self.thief.quit()
        super(Edits, self).focusOutEvent(event)

    def closeEvent(self, event):
        self.thief.quit()
        super(Edits, self).closeEvent(event)




# test floating panel
e = Edits()
e.show()

def edit_func():
    print('EDITOR!')

a = QtWidgets.QAction(e)
a.triggered.connect(edit_func)
s = QtGui.QKeySequence('Ctrl+S')
a.setShortcut(s)
a.setShortcutContext(QtCore.Qt.WidgetShortcut)
e.addAction(a)

#&& # test docked panel
remove_panel('edits')
panel = nukescripts.registerWidgetAsPanel2(
    'Edits', 'edits', 'edits', create=True
)
dock = nuke.getPaneFor('Viewer.1')
panel.addToPane(dock)