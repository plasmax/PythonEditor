from __future__ import print_function
import sys
import re
import __main__
import keyword
from PythonEditor.ui.Qt import QtGui, QtCore, QtWidgets

KEYWORDS = ['True',
            'False']

class_snippet = """class <!cursor>():
    def __init__(self):
        super(, self).__init__()
"""
node_loop_snippet = "for node in nuke.selectedNodes():\n    "

SNIPPETS = {
            'class [snippet]': class_snippet,
            'for node selected [snippet]': node_loop_snippet,
            }

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
        self.connect_signals()

    def connect_signals(self):
        self.editor.focus_in_signal.connect(self._focusInEvent)
        self.editor.key_pressed_signal.connect(self._pre_keyPressEvent)
        self.editor.post_key_pressed_signal.connect(self._post_keyPressEvent)

    @QtCore.Slot(QtGui.QFocusEvent)
    def _focusInEvent(self, event):
        """
        Connected to editor focusInEvent
        via signal. Sets new completer 
        if none present.
        """
        if self.completer == None:
            wordlist = list(set(re.findall('\w+', self.editor.toPlainText())))
            self.completer = Completer(wordlist)
            self.completer.setParent(self)
            self.completer.setWidget(self.editor)
            self.completer.activated.connect(self.insertCompletion)

    def word_under_cursor(self):
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
        document = self.editor.document()

        pos = textCursor.position()
        block_number = document.findBlock(pos).blockNumber()

        block = document.findBlockByNumber(block_number)
        block_start = block.position()
        s = self.editor.toPlainText()[block_start:pos]

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
        _obj = _objects.get(word_before_dot)
        if _obj is None:
            try:
                _ = {}
                exec('_obj = '+word_before_dot, _objects, _)
                print(_)
                _obj = _.get('_obj')
            except NameError as e: #we want to handle this silently
                return
                
        return _obj

    def completeObject(self, _obj=None):
        """
        Get list of object properties
        and methods and set them as 
        the completer string list.
        """
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

        cp = self.completer
        currentWord = self.word_under_cursor()
        cp.setCompletionPrefix(currentWord)
        cp.popup().setCurrentIndex(cp.completionModel().index(0,0))
        
    def completeVariables(self):
        """
        Complete variable names in 
        global scope.
        TODO: Substring matching ;)
        """
        cp = self.completer
        variables = __main__.__dict__.keys()
        variables = variables+keyword.kwlist+list(SNIPPETS.keys())+dir(__builtins__)+KEYWORDS
        self.setList(variables)
        word = self.word_under_cursor()
        char_len = len(word)
        cp.setCompletionPrefix(word)
        cp.popup().setCurrentIndex(cp.completionModel().index(0,0))

        #TODO: substring matching
        if char_len and any(w[:char_len] == word for w in variables):
            self.showPopup()

    def setList(self, stringlist):
        qslm =  QtCore.QStringListModel()
        qslm.setStringList(stringlist)
        self.completer.setModel(qslm)

    def showPopup(self):
        """
        Show the completer list.
        """
        cursorRect = self.editor.cursorRect()
        cursorRect.setWidth(self.completer.popup().sizeHintForColumn(0)
            + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cursorRect)

    def insertCompletion(self, completion):
        """
        Inserts a completion, 
        replacing current word.
        """
        if '[snippet]' in completion:
            return self.insertSnippetCompletion(completion)

        textCursor = self.editor.textCursor()
        prefix = self.completer.completionPrefix()
        pos = textCursor.position()
        textCursor.setPosition(pos-len(prefix), QtGui.QTextCursor.KeepAnchor)
        textCursor.insertText(completion)
        self.editor.setTextCursor(textCursor)

    def insertSnippetCompletion(self, completion):
        """
        Fetches snippet from dictionary and 
        completes with that. Sets text cursor position
        to snippet insert point.
        """
        snippet = SNIPPETS[completion]
        if '<!cursor>' in snippet:
            cursor_insert = snippet.index('<!cursor>')
            completion = snippet.replace('<!cursor>', '')
        else:
            completion = snippet
            
        textCursor = self.editor.textCursor()
        prefix = self.completer.completionPrefix()
        pos = textCursor.position()
        textCursor.setPosition(pos-len(prefix), QtGui.QTextCursor.KeepAnchor)
        textCursor.insertText(completion)

        if '<!cursor>' in snippet:
            textCursor.setPosition(pos+cursor_insert-len(prefix), QtGui.QTextCursor.MoveAnchor)

        self.editor.setTextCursor(textCursor)

    @QtCore.Slot(QtGui.QKeyEvent)
    def _pre_keyPressEvent(self, event):
        """
        Called before QPlainTextEdit.keyPressEvent
        TODO:
        - Complete defined names (parse for "name =" thing)
        - Complete class names (parse for "self.")
        - Complete snippets
        """
        cp = self.completer
        cpActive = cp and cp.popup() and cp.popup().isVisible()

        if cpActive: #sometimes "enter" key doesn't trigger completion
            if event.key() in (
                                QtCore.Qt.Key_Enter,
                                QtCore.Qt.Key_Return,
                                QtCore.Qt.Key_Escape,
                                QtCore.Qt.Key_Tab,
                                QtCore.Qt.Key_Backtab):
                event.ignore()
                self.editor.wait_for_autocomplete = True
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
                    self.editor.wait_for_autocomplete = True #assuming this should be here too but untested
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
                    self.editor.wait_for_autocomplete = True #assuming this should be here too but untested
                    return True

        self.editor.wait_for_autocomplete = False
        self.editor.keyPressEvent(event)

    @QtCore.Slot(QtGui.QKeyEvent)
    def _post_keyPressEvent(self, event):
        """
        Called after QPlainTextEdit.keyPressEvent
        """
        cp = self.completer
            
        if (event.key() == QtCore.Qt.Key_Period
                or event.text() in [':', '!']): # TODO: this should hide on a lot more characters!
            if cp.popup():
                cp.popup().hide()
            self.completeObject()
            self.editor.wait_for_autocomplete = True
            return True

        elif (cp and cp.popup() and cp.popup().isVisible()):
            currentWord = self.word_under_cursor()

            cp.setCompletionPrefix(currentWord)
            cp.popup().setCurrentIndex(cp.completionModel().index(0,0))

        elif event.text().isalnum() or event.text() in ['_']:
            pos = self.editor.textCursor().position()
            document = self.editor.document()
            block_number = document.findBlock(pos).blockNumber()
            block = document.findBlockByNumber(block_number)            
            if '.' in block.text().split(' ')[-1]:
                self.completeObject()
            else:
                self.completeVariables()

        self.editor.wait_for_autocomplete = True
