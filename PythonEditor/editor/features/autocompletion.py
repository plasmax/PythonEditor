import os
import sys
import re

import time
print 'importing', __name__, 'at', time.asctime()

from qt import QtGui, QtCore

# from ..base import CodeEditor
import linenumbers
CodeEditor = linenumbers.CodeEditorWithLines

AUTO_COMPLETE = True

class Codepleter(QtGui.QCompleter):
    """docstring for Codepleter"""

    def __init__(self, stringlist):
        super(Codepleter, self).__init__(stringlist)

        self.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        
class CodeEditorAuto(CodeEditor):
    """docstring for CodeEditorAuto"""
    def __init__(self, file, output):
        super(CodeEditorAuto, self).__init__(file, output)

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

    def getObjectBeforeChar(self, _char):
        self.completer.setCompletionPrefix('')
        textCursor = self.textCursor()

        textCursor.select(QtGui.QTextCursor.LineUnderCursor)
        selectedText = textCursor.selectedText()

        lastword = selectedText.split(' ')[-1]
        word_before_dot = '.'.join(lastword.split('.')[:-1])

        if (word_before_dot.strip() == '' 
                or word_before_dot.endswith(_char)
                or not word_before_dot[-1].isalnum()):
            return

        _objects = self._globals.copy()
        _objects.update(self._locals.copy())

        varname_exists = (word_before_dot in _objects)

        if varname_exists:
            _obj = _objects.get(word_before_dot)
        else:
            try:
                loc = {}
                exec('_obj = '+word_before_dot, self._globals, loc)#self._locals)
                print loc
                _obj = loc.get('_obj')
            except NameError, e:
                print e
                return

        print _obj
        return _obj

    def completeObject(self, _obj=None):

        if _obj == None:
            _obj = self.getObjectBeforeChar('.')

        if _obj is None or False:
            return

        attrs = dir(_obj)

        methods = [a for a in attrs if a[0].islower()]
        therest = [a for a in attrs if not a[0].islower()]
        stringlist = methods+therest
        self.setList(stringlist)
        self.showPopup()

    def completeVariables(self):
        pass

    def setList(self, stringlist):
        qslm =  QtGui.QStringListModel()
        qslm.setStringList(stringlist)
        self.completer.setModel(qslm)

    def showPopup(self):
        cursorRect = self.cursorRect()
        cursorRect.setWidth(self.completer.popup().sizeHintForColumn(0)
            + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cursorRect)

    def insertCompletion(self, completion):
        # print 'prefix:', self.completer.completionPrefix()
        print completion
        textCursor = self.textCursor()
        extra = (len(completion) -
            len(self.completer.completionPrefix()))
        textCursor.movePosition(QtGui.QTextCursor.Left)
        textCursor.movePosition(QtGui.QTextCursor.EndOfWord)
        textCursor.insertText(completion[-extra:])
        self.setTextCursor(textCursor)

    def keyPressEvent(self, event):
        cp = self.completer
        cpActive = cp and cp.popup() and cp.popup().isVisible()

        if cpActive:
            if event.key() in (
                                QtCore.Qt.Key_Enter,
                                QtCore.Qt.Key_Return,
                                QtCore.Qt.Key_Escape,
                                QtCore.Qt.Key_Tab,
                                QtCore.Qt.Key_Backtab):
                event.ignore()
                return True
            elif (not str(event.text()).isalnum()
                    and event.modifiers() == QtCore.Qt.NoModifier):
                cp.popup().hide()

        if event.key() == QtCore.Qt.Key_Tab:
            textCursor = self.textCursor()
            if not textCursor.hasSelection():
                textCursor.select(QtGui.QTextCursor.LineUnderCursor)
                selectedText = textCursor.selectedText()
                if selectedText.endswith('.'):
                    print selectedText
                    self.completeObject()
                    return True
                elif selectedText.endswith('('):
                    # _obj = self.getObjectBeforeChar('(')
                    # print '\tOBJECT!!!!!!!!'*10, _obj
                    ret = {}
                    # cmd = 'import inspect\n'
                    # cmd += '__ret = inspect.getargspec('+ selectedText[:-1] +')'
                    cmd = '__ret = '+ selectedText[:-1].split(' ')[-1]
                    print cmd
                    cmd = compile(cmd, '<Python Editor Tooltip>', 'exec')
                    exec(cmd, self._globals, ret)
                    _obj = ret.get('__ret')
                    if _obj:
                        print 'returned object:', _obj
                        info = str('')
                        import inspect, types #move this to top
                        if (isinstance(_obj, types.BuiltinFunctionType)
                                or isinstance(_obj, types.BuiltinMethodType)):
                            info = _obj.__doc__
                        else:
                            info = str(inspect.getargspec(_obj))
                            if _obj.__doc__:
                                info += '\n' + _obj.__doc__

                        QtGui.QToolTip.showText(self.mapToGlobal(self.cursorRect().center()), info)
                    return True

        super(CodeEditorAuto, self).keyPressEvent(event)
                
        if event.key() == QtCore.Qt.Key_Period:
            if cp.popup():
                cp.popup().hide()
            self.completeObject()
            # self.getObjectBeforeChar('.')
            return True

        elif (cp and cp.popup() and cp.popup().isVisible()):
            currentWord = self.wordUnderCursor()

            cp.setCompletionPrefix(currentWord)
            cp.popup().setCurrentIndex(cp.completionModel().index(0,0))

        # else:
            # self.completeVariables()


            

