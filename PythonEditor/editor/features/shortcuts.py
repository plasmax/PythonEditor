
from ...qt import QtCore, QtGui

def shortcut_handler(editor, event, editorClass):
    """
    Outsourcing CodeEditor.keyPressEvent
    """

    self = editor
    CodeEditor = editorClass

    if event.key() in (QtCore.Qt.Key_Return,
                       QtCore.Qt.Key_Enter):
        if event.modifiers() == QtCore.Qt.ControlModifier:
            self.begin_exec()

        elif event.modifiers() == QtCore.Qt.ShiftModifier | QtCore.Qt.ControlModifier:
            textCursor = self.textCursor()
            line = textCursor.block().text()
            indentCount = len(line) - len(line.lstrip(' '))
            textCursor.movePosition(textCursor.StartOfLine)
            self.setTextCursor(textCursor)
            textCursor.insertText(' '*indentCount+'\n')
            self.moveCursor(textCursor.Left)
            return True
        else:
            textCursor = self.textCursor()
            line = textCursor.block().text()
            indentCount = len(str(line)) - len(str(line).lstrip(' '))
            textCursor.insertText('\n'+' '*indentCount)
            return True

    if event.key() in (QtCore.Qt.Key_Backspace,):
        if event.modifiers() == QtCore.Qt.ControlModifier:
            self.clearOutput.emit()
            return True

    if event.key() == QtCore.Qt.Key_Backtab:
        raise NotImplementedError, 'add unindent function'
        return True
        
    if event.key() == QtCore.Qt.Key_Tab:
        textCursor = self.textCursor()
        if textCursor.hasSelection():
            safe_string = textCursor.selectedText().replace(u'\u2029', '\n')
            newLines = (len(safe_string.split('\n')) > 1)
            if newLines:
                raise NotImplementedError, 'add indent multiple lines here'
                return True

    if (event.key() == QtCore.Qt.Key_Slash
            and event.modifiers() == QtCore.Qt.ControlModifier):
        comment_toggle(self, event)

        return True

    if event.key() == QtCore.Qt.Key_BracketRight:
        if event.modifiers() == QtCore.Qt.ControlModifier:
            raise NotImplementedError, 'add right indent here'
        # elif self.textCursor().hasSelection():
        #     wraptext(self, event)

    if (event.key() == QtCore.Qt.Key_BracketLeft
            and event.modifiers() == QtCore.Qt.ControlModifier):
        raise NotImplementedError, 'add left indent here'

    if (event.key() == QtCore.Qt.Key_K
            and event.modifiers() == QtCore.Qt.ShiftModifier | QtCore.Qt.ControlModifier):
        raise NotImplementedError, 'add delete line'

    if (event.key() == QtCore.Qt.Key_F
            and event.modifiers() == QtCore.Qt.ControlModifier):
        raise NotImplementedError, 'add search function'

    if (event.key() == QtCore.Qt.Key_H
            and event.modifiers() == QtCore.Qt.ControlModifier):
        textCursor = self.textCursor()
        if textCursor.hasSelection():
            text = textCursor.selection().toPlainText()
            cmd = 'help(' + text + ')'
            self.global_exec(cmd)

    if (event.key() == QtCore.Qt.Key_T
            and event.modifiers() == QtCore.Qt.ControlModifier):
        textCursor = self.textCursor()
        if textCursor.hasSelection():
            text = textCursor.selection().toPlainText()
            cmd = 'type(' + text + ')'
            self.global_exec(cmd)

    if (event.key() == QtCore.Qt.Key_X
            and event.modifiers() == QtCore.Qt.ControlModifier):
        textCursor = self.textCursor()
        if not textCursor.hasSelection():
            raise NotImplementedError, 'add cut line function'

    if (event.key() == QtCore.Qt.Key_S
            and event.modifiers() == QtCore.Qt.ControlModifier | QtCore.Qt.AltModifier):
        event.accept()
        raise NotImplementedError, 'add save function'

    if (event.key() == QtCore.Qt.Key_D
            and event.modifiers() == QtCore.Qt.ControlModifier):
        raise NotImplementedError, 'add select duplicate function'

    if (event.key() == QtCore.Qt.Key_Home
            and event.modifiers() == QtCore.Qt.ControlModifier | QtCore.Qt.AltModifier):
        raise NotImplementedError, 'add move line to top function'

    if (event.text() in ['\'', '"', '[', ']', '(', ')', '{', '}']
            and self.textCursor().hasSelection()):
        wraptext(self, event)
        return True
        # keyDict = {value:key for key, value in QtCore.Qt.__dict__.iteritems()}
        # print keyDict.get(event.key()), event.text()

    super(CodeEditor, self).keyPressEvent(event)

def wraptext(editor, event):
    self = editor

    key = event.text()

    if key in ['\'', '"']:
        key_in = key
        key_out = key
    elif key in ['[', ']']:
        key_in = '['
        key_out = ']'
    elif key in ['(', ')']:
        key_in = '('
        key_out = ')'
    elif key in ['{', '}']:
        key_in = '{'
        key_out = '}'

    textCursor = self.textCursor()
    textCursor.insertText( key_in + textCursor.selectedText() + key_out )

def comment_toggle(editor, event):
    self = editor
    
    textCursor = self.textCursor()

    #get line numbers
    blockNumbers = set([
            self.document().findBlock(b).blockNumber()
            for b in range(textCursor.selectionStart(), textCursor.selectionEnd())
                ])
    blockNumbers |= set([self.document().findBlock(textCursor.position()).blockNumber()])
    blocks = [
            self.document().findBlockByNumber(b)
            for b in blockNumbers
            if self.document().findBlockByNumber(b).text() != ''
            ]
    
    #iterate through lines in doc commenting or uncommenting based on whether everything is commented or not
    commentAllOut = any([not str(block.text()).lstrip().startswith('#') for block in blocks])
    if commentAllOut:
        for block in blocks:
            cursor = QtGui.QTextCursor(block)
            cursor.movePosition(textCursor.StartOfLine)
            cursor.insertText('#')
    else:
        for block in blocks:
            cursor = QtGui.QTextCursor(block)
            cursor.select(QtGui.QTextCursor.LineUnderCursor)
            selectedText = cursor.selectedText()
            newText = str(selectedText).replace('#', '', 1)
            cursor.insertText(newText)