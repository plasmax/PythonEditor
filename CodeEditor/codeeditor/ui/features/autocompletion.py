import sys
import re
import __main__

from codeeditor.ui.Qt import QtGui, QtCore, QtWidgets

class Completer(QtWidgets.QCompleter):
    def __init__(self, stringlist):
        super(Completer, self).__init__(stringlist)

        self.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        
class AutoCompleter(QtCore.QObject):
    """
    Provides autocompletion to QPlainTextEdit.
    Requires signals to be emitted from such
    with -pre and -post keyPressEvent signals.
    """
    def __init__(self, editor):
        super(AutoCompleter, self).__init__()

        self.loadedModules = sys.modules.keys()
        self.completer = None

        self.editor = editor
        editor.focus_in_signal.connect(self._focusInEvent)
        editor.key_pressed_signal.connect(self._pre_keyPressEvent)
        editor.post_key_pressed_signal.connect(self._post_keyPressEvent)

    @QtCore.Slot(QtGui.QFocusEvent)
    def _focusInEvent(self, event):
        if self.completer == None:
            wordlist = list(set(re.findall('\w+', self.editor.toPlainText())))
            self.completer = Completer(wordlist)
            self.completer.setParent(self)
            self.completer.setWidget(self.editor)
            self.completer.activated.connect(self.insertCompletion)

    def wordUnderCursor(self):
        """
        Returns a string with the word under the cursor.
        """
        textCursor = self.editor.textCursor()
        textCursor.select(QtGui.QTextCursor.WordUnderCursor)
        return textCursor.selectedText()

    def getObjectBeforeChar(self, _char):
        """
        Return python object from string.
        """
        self.completer.setCompletionPrefix('')
        textCursor = self.editor.textCursor()

        pos = self.editor.textCursor().position()
        bn = self.editor.document().findBlock(pos).blockNumber()

        bl = self.editor.document().findBlockByNumber(bn)
        bp = bl.position()
        s = self.editor.toPlainText()[bp:pos]

        for c in s:
            if (not c.isalnum() 
                    and not c in ['.', '_']):
                s = s.replace(c, ' ')

        word_before_dot = s.split(' ')[-1]
        word_before_dot = '.'.join(word_before_dot.split('.')[:-1])

        if (word_before_dot.strip() == '' 
                or word_before_dot.endswith(_char)
                or not word_before_dot[-1].isalnum()):
            return

        _objects = __main__.__dict__.copy()

        varname_exists = (word_before_dot in _objects)

        if varname_exists:
            _obj = _objects.get(word_before_dot)
        else:
            try:
                _ = {}
                exec('_obj = '+word_before_dot, _objects, _)
                print _
                _obj = _.get('_obj')
            except NameError, e: #we want to handle this silently
                return
                
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
        qslm =  QtCore.QStringListModel()
        qslm.setStringList(stringlist)
        self.completer.setModel(qslm)

    def showPopup(self):
        cursorRect = self.editor.cursorRect()
        cursorRect.setWidth(self.completer.popup().sizeHintForColumn(0)
            + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cursorRect)

    def insertCompletion(self, completion):
        textCursor = self.editor.textCursor()
        extra = (len(completion) -
            len(self.completer.completionPrefix()))
        textCursor.movePosition(QtGui.QTextCursor.Left)
        textCursor.movePosition(QtGui.QTextCursor.EndOfWord)
        textCursor.insertText(completion[-extra:])
        self.editor.setTextCursor(textCursor)

    @QtCore.Slot(QtGui.QKeyEvent)
    def _pre_keyPressEvent(self, event):
        """
        Called before QPlainTextEdit.keyPressEvent
        """
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
            textCursor = self.editor.textCursor()
            if (not textCursor.hasSelection()
                    and not event.modifiers() == QtCore.Qt.ShiftModifier):
                textCursor.select(QtGui.QTextCursor.LineUnderCursor)
                selectedText = textCursor.selectedText()
                if selectedText.endswith('.'):
                    self.completeObject()
                    return True
                elif selectedText.endswith('('):
                    ret = {}
                    cmd = '__ret = '+ selectedText[:-1].split(' ')[-1]
                    cmd = compile(cmd, '<Python Editor Tooltip>', 'exec')
                    exec(cmd, __main__.__dict__.copy(), ret)
                    _obj = ret.get('__ret')
                    if _obj:
                        info = str('')
                        import inspect, types #move this to top
                        if (isinstance(_obj, types.BuiltinFunctionType)
                                or isinstance(_obj, types.BuiltinMethodType)):
                            info = _obj.__doc__
                        else:
                            info = str(inspect.getargspec(_obj))
                            if _obj.__doc__:
                                info += '\n' + _obj.__doc__

                        center_cursor_rect = self.editor.cursorRect().center()
                        global_rect = self.editor.mapToGlobal(center_cursor_rect)
                        QtWidgets.QToolTip.showText(global_rect, info)
                    return True

        self.editor.wait_for_autocomplete = False
        self.editor.keyPressEvent(event)

    @QtCore.Slot(QtGui.QKeyEvent)
    def _post_keyPressEvent(self, event):
        """
        Called after QPlainTextEdit.keyPressEvent
        """
        cp = self.completer

        if event.key() == QtCore.Qt.Key_Period:
            if cp.popup():
                cp.popup().hide()
            self.completeObject()
            return True

        elif (cp and cp.popup() and cp.popup().isVisible()):
            currentWord = self.wordUnderCursor()

            cp.setCompletionPrefix(currentWord)
            cp.popup().setCurrentIndex(cp.completionModel().index(0,0))

        self.editor.wait_for_autocomplete = True
        # else:
        #     self.getObjectBeforeChar(event.text())
        #     print 'word'
        #     print self.wordUnderCursor()
        #     # self.completeVariables()
