import os
import sys
import re

import time
print 'importing', __name__, 'at', time.asctime()

try:
    import PySide
except:
    import sys
    sys.path.append('C:/Users/Max-Last/.nuke/python/external')
from PySide import QtGui, QtCore

from ..base import CodeEditor
from linenumbers import CodeEditorWithLines as CodeEditor

AUTO_COMPLETE = True

class Codepleter(QtGui.QCompleter):
    """docstring for Codepleter"""

    def __init__(self, stringlist):
        super(Codepleter, self).__init__(stringlist)

        self.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        
class CodeEditorAuto(CodeEditor):
    """docstring for CodeEditorAuto"""
    def __init__(self, file, _globals={}, _locals={}):
        super(CodeEditorAuto, self).__init__(file, _globals, _locals)
        self._globals = _globals
        self._locals = _locals

        self.loadedModules = sys.modules.keys()
        self.completer = None

    def focusInEvent(self, event):
        if self.completer == None:
            wordlist = list(set(re.findall('\w+', self.toPlainText())))
            self.completer = Codepleter(wordlist)#, parent=self)
            self.completer.setParent(self)
            self.completer.setWidget(self)
            self.completer.activated.connect(self.insertCompletion)
        super(CodeEditorAuto, self).focusInEvent(event)

    def wordUnderCursor(self):
        textCursor = self.textCursor()
        textCursor.select(QtGui.QTextCursor.WordUnderCursor)
        return textCursor.selectedText()

    def dotLastWord(self):
        self.completer.setCompletionPrefix('')
        textCursor = self.textCursor()
        textCursor.select(QtGui.QTextCursor.LineUnderCursor)#BlockUnderCursor
        selectedText = textCursor.selectedText()
        lastword = selectedText.split(' ')[-1]

        dotLastWord = '.'.join(lastword.split('.')[:-1])

        if (dotLastWord.strip() == '' 
            or dotLastWord.endswith('.')):
            return

        _objects = self._globals.copy()
        _objects.update(self._locals.copy())

        if dotLastWord not in _objects:
            return

        attrs = dir(self._locals.get(dotLastWord))

        methods = [a for a in attrs if a[0].islower()]
        therest = [a for a in attrs if not a[0].islower()]
        qslm =  QtGui.QStringListModel()
        qslm.setStringList(methods+therest)
        self.completer.setModel(qslm)

        cursorRect = self.cursorRect()
        cursorRect.setWidth(self.completer.popup().sizeHintForColumn(0)
            + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cursorRect)
        

    def insertCompletion(self, completion):
        # print 'prefix:', self.completer.completionPrefix()
        textCursor = self.textCursor()
        extra = (len(completion) -
            len(self.completer.completionPrefix()))
        textCursor.movePosition(QtGui.QTextCursor.Left)
        textCursor.movePosition(QtGui.QTextCursor.EndOfWord)
        textCursor.insertText(completion[-extra:])
        self.setTextCursor(textCursor)

    def keyPressEvent(self, event):
        cp = self.completer

        if cp and cp.popup() and cp.popup().isVisible():
            if event.key() in (
                                QtCore.Qt.Key_Enter,
                                QtCore.Qt.Key_Return,
                                QtCore.Qt.Key_Escape,
                                QtCore.Qt.Key_Tab,
                                QtCore.Qt.Key_Backtab):
                event.ignore()
                return True

        super(CodeEditorAuto, self).keyPressEvent(event)
                
        if event.key() == QtCore.Qt.Key_Period:
            if cp.popup():
                cp.popup().hide()
            self.dotLastWord()

        elif event.text().isalpha():
            currentWord = self.wordUnderCursor()

            cp.setCompletionPrefix(currentWord)
            cp.popup().setCurrentIndex(cp.completionModel().index(0,0))


