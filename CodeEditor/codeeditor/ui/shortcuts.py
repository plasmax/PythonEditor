from Qt import QtWidgets, QtGui, QtCore
# from PySide import QtGui, QtCore, QtGui as QtWidgets

from functools import partial

class ShortcutHandler(QtCore.QObject):
    """
    Shortcut Manager with custom signals.
    """
    clearOutputSignal = QtCore.Signal()
    execTextSignal = QtCore.Signal(str, str)

    def __init__(self, widget):
        super(ShortcutHandler, self).__init__(parent=widget)
        self.setObjectName('ShortcutHandler')
        self.setParent(widget)
        self.widget = widget
        print widget
        self.installShortcuts()
            
    def installShortcuts(self):
        """
        Set up all shortcuts on 
        the QPlainTextEdit widget.
        """
        mapping = { 'Ctrl+Return': self.execSelectedText,
                    'Ctrl+Backspace' : self.clearOutputSignal.emit,
                    'Ctrl+D': partial(self.notimplemented, 'select word or next word'),
                    'Ctrl+Shift+D': partial(self.notimplemented, 'duplicate line'),
                    'Ctrl+W': partial(self.notimplemented, 'close tab'),
                    'Ctrl+F': partial(self.notimplemented, 'search function'),
                    # '.': partial(self.notimplemented, 'dotcompletion'),
                    'Tab' : partial(self.notimplemented, 'indent'),
                    QtCore.Qt.Key_Tab : partial(self.notimplemented, 'indent'),
                    'Shift+Tab' : partial(self.notimplemented, 'unindent'),
                    'Ctrl+/': partial(self.notimplemented, 'comment'),
                    'Ctrl+=': partial(self.notimplemented, 'zoom in'),
                    'Ctrl++': partial(self.notimplemented, 'zoom in'),
                    'Ctrl+-': partial(self.notimplemented, 'zoom out'),
                    'Ctrl+Shift+K': partial(self.notimplemented, 'delete line'),
                    'Ctrl+Shift+Down': partial(self.notimplemented, 'move line down'),
                    'Ctrl+Shift+Up': partial(self.notimplemented, 'move line up'),
                  }

        context = QtCore.Qt.WidgetShortcut
        for shortcut, func in mapping.iteritems():
            keySequence = QtGui.QKeySequence(shortcut)
            qshortcut = QtWidgets.QShortcut(keySequence, 
                                self.widget, 
                                func,
                                context=context)

    def execSelectedText(self):
        """
        Emit a signal with either selected text
        or all the text in the edit widget.
        """
        textCursor = self.widget.textCursor()

        wholeText = self.widget.toPlainText()

        if textCursor.hasSelection():
            text = textCursor.selection().toPlainText()

            #offset by block number 
            #to get proper line ref in tracebacks
            b = textCursor.selectionStart()
            blockNo = self.widget.document().findBlock(b).blockNumber()
            text = '\n' * blockNo + text
            
        else:
            text = wholeText 

        self.execTextSignal.emit(text, wholeText)

    def notimplemented(self, text):
        raise NotImplementedError, text
