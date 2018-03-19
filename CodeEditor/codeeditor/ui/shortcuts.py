from Qt import QtWidgets, QtGui, QtCore
from functools import partial

def installShortcuts(widget):
    """
    Set up all shortcuts on 
    the QPlainTextEdit widget.
    """
    excCmd = QtGui.QKeySequence("Ctrl+Return")
    QtWidgets.QShortcut(excCmd, 
                        widget, 
                        partial(execSelectedText, widget),
                        context=QtCore.Qt.WidgetShortcut)

def execSelectedText(widget):
    """
    Emit a signal with either selected text
    or all the text in the edit widget.
    """
    textCursor = widget.textCursor()


    if textCursor.hasSelection():
        text = textCursor.selection().toPlainText()

        #offset by block number 
        #to get proper line ref in tracebacks
        b = textCursor.selectionStart()
        blockNo = widget.document().findBlock(b).blockNumber()
        text = '\n' * blockNo + text
        
    else:
        text = widget.toPlainText()


    widget.execTextSignal.emit(text)
