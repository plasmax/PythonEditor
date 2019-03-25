from Qt import QtWidgets, QtGui, QtCore


class Editor(QtWidgets.QPlainTextEdit):
    text_entered_signal = QtCore.Signal(object)
    def __init__(self):
        super(Editor, self).__init__()
        self.autocomplete = AutoCompleter(self)

    def keyPressEvent(self, event):
        self.enter_text = True
        self.text_entered_signal.emit(event)
        if not self.enter_text:
            return
        #super(Editor, self).keyPressEvent(event)
        

class AutoCompleter(QtWidgets.QListView):
    def __init__(self, editor):
        super(AutoCompleter, self).__init__()
        
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.FramelessWindowHint
        )
        self.editor = editor
        editor.setFocus(QtCore.Qt.MouseFocusReason)
        editor.text_entered_signal.connect(
            self.block,
            QtCore.Qt.DirectConnection
        )

    @QtCore.Slot(object)
    def block(self, event):
        editor = self.editor
        super(editor.__class__, editor).keyPressEvent(event)
        return
        
        if event.key() == QtCore.Qt.Key_Tab:
            event.accept()
            editor.enter_text = False
            
            rect = editor.cursorRect()
            pos = rect.bottomRight()            
            pos = editor.mapToGlobal(pos)
            self.move(pos)
            self.show()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.hide()
        super(AutoCompleter, self).keyPressEvent(event)


e = Editor()
e.show()


