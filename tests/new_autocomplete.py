from Qt import QtCore, QtGui, QtWidgets

key_list = {}
for k in dir(QtCore.Qt):
    try:
        key_list[int(getattr(QtCore.Qt, k))] = k
    except TypeError:
        print k

class Editor(QtWidgets.QPlainTextEdit):
    block_key_press = False
    key_pressed_signal = QtCore.Signal(QtGui.QKeyEvent)
    
    def __init__(self):
        super(Editor, self).__init__()
        self._completer = Completer(self)
    
    def keyPressEvent(self, event):
        
        self.key_pressed_signal.emit(event)
        if self.block_key_press:
            return
            
        super(Editor, self).keyPressEvent(event)
        self.block_key_press = False
        


class Completer(QtWidgets.QCompleter):
    def __init__(self, editor):
        super(Completer, self).__init__([])

        self.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.setCaseSensitivity(QtCore.Qt.CaseSensitive)
        
        self.editor = editor
        self.editor.key_pressed_signal.connect(self.key_press_event)
        self.setParent(self.editor)
        self.setWidget(self.editor)
        self.activated.connect(self.insert_completion)
        print globals().keys()
        self.set_list(globals().keys())
        
        
    def set_list(self, stringlist):
        """
        Sets the list of completions.
        """
        qslm = QtCore.QStringListModel()
        qslm.setStringList(stringlist)
        self.setModel(qslm)
        
    def word_under_cursor(self):
        """
        Returns a string with the word under the cursor.
        """
        textCursor = self.editor.textCursor()
        textCursor.select(QtGui.QTextCursor.LineUnderCursor)
        #textCursor.select(QtGui.QTextCursor.WordUnderCursor)
        word = textCursor.selection().toPlainText()
        return word
        
    def insert_completion(self, text):
        print text
    
    def show_popup(self):
        """
        Show the completer list.
        """
        cursorRect = self.editor.cursorRect()
        pop = self.popup()
        cursorRect.setWidth(pop.sizeHintForColumn(0)
                            + pop.verticalScrollBar().sizeHint().width())
        self.complete(cursorRect)

    def key_press_event(self, event):
        
        print key_list[int(event.key())]
        complete_keys = [
                        QtCore.Qt.Key_Enter,
                        QtCore.Qt.Key_Return,
                        QtCore.Qt.Key_Escape,
                        QtCore.Qt.Key_Tab,
                        QtCore.Qt.Key_Backtab,
                        QtCore.Qt.Key_Meta,
                        ]
        if event.key() in (complete_keys):
            
            if self.popup() and self.popup().isVisible():
                #event.ignore() # ? necessary?
                pass
            return      
                                              
        not_alnum_or_mod = (not str(event.text()).isalnum()
                            and event.modifiers() == QtCore.Qt.NoModifier)

        zero_completions = self.completionCount() == 0
        if not_alnum_or_mod or zero_completions:
            self.popup().hide()
            return

        current_word = self.word_under_cursor()+event.text()
        print 'Current word:', current_word
        self.setCompletionPrefix(current_word)
        self.popup().setCurrentIndex(self.completionModel().index(0, 0))
        self.show_popup()
            
        #if event.text() == 'f':
            #self.editor.block_key_press = True
        
e = Editor()
e.show()
        
nukeFRenderPub.dialog.menu
