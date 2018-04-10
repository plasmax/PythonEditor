import sys
import __main__
from functools import partial
from PythonEditor.ui.Qt import QtWidgets, QtGui, QtCore
from PythonEditor.core import execute

class ShortcutHandler(QtCore.QObject):
    """
    Shortcut Manager with custom signals.
    """
    clear_output_signal = QtCore.Signal()
    exec_text_signal = QtCore.Signal()

    def __init__(self, editortabs):
        super(ShortcutHandler, self).__init__()
        self.setObjectName('ShortcutHandler')
        self.editortabs = editortabs
        self.setParent(editortabs)
        self.editortabs.tab_switched_signal.connect(self.tab_switch_handler)
        self.setEditor()
        self.installShortcuts()

    @QtCore.Slot(int, int, bool)
    def tab_switch_handler(self, previous, current, tabremoved):
        if not tabremoved:  #nothing's been deleted
                            #so we need to disconnect
                            #signals from previous editor
            self.disconnectSignals()

        self.setEditor()

    def setEditor(self):
        """
        Sets the current editor
        and connects signals.
        """
        editor = self.editortabs.currentWidget()
        editorChanged = True if not hasattr(self, 'editor') else self.editor != editor
        isEditor = editor.objectName() == 'Editor'
        if isEditor and editorChanged:
            self.editor = editor
            self.connectSignals()

    def connectSignals(self):
        """
        For shortcuts that cannot be 
        handled directly by QShortcut.
        """
        try:
            QtCore.Qt.UniqueConnection
        except AttributeError as e:
            print(e)
            QtCore.Qt.UniqueConnection = 128
        self.editor.tab_signal.connect(self.tab_handler, QtCore.Qt.UniqueConnection)
        self.editor.return_signal.connect(self.return_handler, QtCore.Qt.UniqueConnection)
        self.editor.wrap_signal.connect(self.wrap_text, QtCore.Qt.UniqueConnection)
        self.editor.home_key_ctrl_alt_signal.connect(self.move_to_top, QtCore.Qt.UniqueConnection)
        self.editor.end_key_ctrl_alt_signal.connect(self.move_to_bottom, QtCore.Qt.UniqueConnection)

    def disconnectSignals(self):
        """
        For shortcuts that cannot be 
        handled directly by QShortcut.
        TODO: If editor no longer exists (has been closed)
        do not try to disconnect.
        """
        if not hasattr(self, 'editor'):
            return
        editor = self.editor
        editor.tab_signal.disconnect()
        editor.return_signal.disconnect()
        editor.wrap_signal.disconnect()
        editor.home_key_ctrl_alt_signal.disconnect()
        editor.end_key_ctrl_alt_signal.disconnect()

    def installShortcuts(self):
        """
        Set up all shortcuts on 
        the QPlainTextEdit widget.
        """
        notimp = lambda msg: partial(self.notimplemented, msg)
        mapping = { 
                    'Ctrl+Return': self.exec_selected_text,
                    'Ctrl+B': self.exec_selected_text,
                    'Ctrl+Shift+Return': self.new_line_above,
                    'Ctrl+Alt+Return': self.new_line_below,
                    'Ctrl+Backspace' : self.clear_output_signal.emit,
                    'Ctrl+Shift+D': self.duplicate_lines,
                    'Ctrl+H': self.printHelp,
                    'Ctrl+T': self.printType,
                    'Ctrl+F': self.searchInput,
                    'Ctrl+L': self.select_lines,
                    'Ctrl+J': self.join_lines,
                    'Ctrl+/': self.comment_toggle,
                    'Ctrl+]': self.indent,
                    'Ctrl+[': self.unindent,
                    'Shift+Tab' : self.unindent,
                    'Ctrl+=': self.zoomIn,
                    'Ctrl++': self.zoomIn,
                    'Ctrl+-': self.zoomOut,
                    'Ctrl+Shift+K': self.delete_lines,
                    'Ctrl+D': notimp('select word or next word'),
                    'Ctrl+M': notimp('jump to nearest bracket'),
                    'Ctrl+Shift+M': notimp('select between brackets'),
                    'Ctrl+Shift+Up': self.move_lines_up,
                    'Ctrl+Shift+Down': self.move_lines_down,
                    'Ctrl+Shift+Home': notimp('move to start'),
                    'Ctrl+Shift+Alt+Up': notimp('duplicate cursor up'),
                    'Ctrl+Shift+Alt+Down': notimp('duplicate cursor down'),
                    'Ctrl+N': self.editortabs.new_tab,
                    'Ctrl+W': self.editortabs.close_current_tab,
                    'Ctrl+X': notimp('cut line'), #won't work without overriding keyEvent
                  }

        context = QtCore.Qt.WidgetShortcut
        for shortcut, func in mapping.iteritems():
            keySequence = QtGui.QKeySequence(shortcut)
            qshortcut = QtWidgets.QShortcut(
                                            keySequence, 
                                            self.editortabs, 
                                            func,
                                            context=context)
            qshortcut.setObjectName(shortcut)

    def notimplemented(self, text):
        """ Development reminders to implement features """
        raise NotImplementedError, text

    def get_selected_blocks(self, ignoreEmpty=True):
        """
        Utility method for getting lines in selection.
        """
        textCursor = self.editor.textCursor()
        doc = self.editor.document()

        #get line numbers
        blockNumbers = set([
                doc.findBlock(b).blockNumber()
                for b in range(textCursor.selectionStart(), textCursor.selectionEnd())
                    ])
        blockNumbers |= set([doc.findBlock(textCursor.position()).blockNumber()])

        isEmpty = lambda b:  doc.findBlockByNumber(b).text().strip() != ''
        blocks = []
        for b in blockNumbers:
            bn = doc.findBlockByNumber(b)
            if not ignoreEmpty:
                blocks.append(bn)
            elif isEmpty(b):
                blocks.append(bn)

        return blocks

    def exec_selected_text(self):
        """
        Calls exec with either selected text
        or all the text in the edit widget.
        """
        textCursor = self.editor.textCursor()

        whole_text = self.editor.toPlainText()

        if textCursor.hasSelection():
            text = textCursor.selection().toPlainText()

            #to get proper line ref in tracebacks
            selection_offset = textCursor.selectionStart()
            doc = self.editor.document()
            block_num = doc.findBlock(selection_offset).blockNumber()
            text = '\n' * block_num + text
            
        else:
            text = whole_text

        self.exec_text_signal.emit()
        execute.mainexec(text, whole_text)

    @QtCore.Slot()
    def return_handler(self):
        """ Handles Return Key """
        self.indent_next_line()
        
    def indent_next_line(self):
        """
        Match next line indentation to current line
        If ':' is character in cursor position,
        add an extra line.
        """
        textCursor = self.editor.textCursor()
        line = textCursor.block().text()
        indentCount = len(str(line)) - len(str(line).lstrip(' '))

        doc = self.editor.document()
        if doc.characterAt(textCursor.position()-1) == ':':
            indentCount = indentCount + 4
        textCursor.insertText('\n'+' '*indentCount)

    def new_line_above(self):
        """
        Inserts new line above current.
        """
        textCursor = self.editor.textCursor()
        line = textCursor.block().text()
        indentCount = len(line) - len(line.lstrip(' '))
        indent = ' '*indentCount
        textCursor.movePosition(textCursor.StartOfLine)
        self.editor.setTextCursor(textCursor)
        textCursor.insertText(indent+'\n')
        self.editor.moveCursor(textCursor.Left)

    def new_line_below(self):
        """
        Inserts new line below current.
        """
        textCursor = self.editor.textCursor()
        line = textCursor.block().text()
        indentCount = len(line) - len(line.lstrip(' '))
        indent = ' '*indentCount
        textCursor.movePosition(textCursor.EndOfLine)
        self.editor.setTextCursor(textCursor)
        textCursor.insertText('\n'+indent)

    @QtCore.Slot()
    def tab_handler(self):
        """
        Handles Tab Key
        TODO: check whole line selected 
        before indenting.
        """
        textCursor = self.editor.textCursor()
        if textCursor.hasSelection():
            self.indent()
        else:
            self.tab_space()

    def indent(self):
        """ Indent Selected Text """
        blocks = self.get_selected_blocks()
        for block in blocks:
            cursor = QtGui.QTextCursor(block)
            cursor.movePosition(QtGui.QTextCursor.StartOfLine)
            cursor.insertText('    ')

    def unindent(self):
        """ 
        Unindent Selected Text 
        TODO: Keep selection.
        """
        blocks = self.get_selected_blocks(ignoreEmpty=False)
        for block in blocks:
            cursor = QtGui.QTextCursor(block)
            cursor.select(QtGui.QTextCursor.LineUnderCursor)
            lineText = cursor.selectedText()
            if lineText.startswith(' '):
                newText = str(lineText[:4]).replace(' ', '') + lineText[4:]
                cursor.insertText(newText)

    def tab_space(self):
        """ Insert spaces instead of tabs """
        self.editor.insertPlainText('    ')

    def comment_toggle(self):
        """
        Toggles commenting out selected lines,
        or lines with cursor.
        """
        blocks = self.get_selected_blocks()
        
        #iterate through lines in doc commenting or uncommenting based on whether everything is commented or not
        commentAllOut = any([not str(block.text()).lstrip().startswith('#') for block in blocks])
        if commentAllOut:
            for block in blocks:
                cursor = QtGui.QTextCursor(block)
                cursor.movePosition(QtGui.QTextCursor.StartOfLine)
                cursor.insertText('#')
        else:
            for block in blocks:
                cursor = QtGui.QTextCursor(block)
                cursor.select(QtGui.QTextCursor.LineUnderCursor)
                selectedText = cursor.selectedText()
                newText = str(selectedText).replace('#', '', 1)
                cursor.insertText(newText)

    @QtCore.Slot(str)
    def wrap_text(self, key):
        """
        Wrap selected text in brackets
        or quotes of type "key".
        """
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

        textCursor = self.editor.textCursor()
        textCursor.insertText( key_in + textCursor.selectedText() + key_out )

    def select_lines(self):
        """
        Sets current lines selected
        and moves cursor to beginning
        of next line.
        """
        textCursor = self.editor.textCursor()

        start = textCursor.selectionStart()
        end = textCursor.selectionEnd()

        textCursor.setPosition(end, QtGui.QTextCursor.MoveAnchor)
        textCursor.movePosition(QtGui.QTextCursor.EndOfLine)
        new_end = textCursor.position()+1
        if new_end >= self.editor.document().characterCount():
            new_end = new_end-1
        
        textCursor.setPosition(start, QtGui.QTextCursor.MoveAnchor)
        textCursor.movePosition(QtGui.QTextCursor.StartOfLine)

        new_start = textCursor.position()
        textCursor.setPosition(new_end, QtGui.QTextCursor.KeepAnchor)
        self.editor.setTextCursor(textCursor)

    def join_lines(self):
        """
        Deletes the newline at end
        of current line(s).
        """
        textCursor = self.editor.textCursor()

        blocks = self.get_selected_blocks(ignoreEmpty=False)
        if len(blocks) > 1:
            textCursor.insertText(textCursor.selectedText().replace(u'\u2029',''))
        else:
            textCursor.movePosition(QtGui.QTextCursor.EndOfLine)
            new_pos = textCursor.position()+1
            if new_pos >= self.editor.document().characterCount():
                return
            textCursor.setPosition(new_pos, QtGui.QTextCursor.KeepAnchor)
            textCursor.insertText('')
            self.editor.setTextCursor(textCursor)

    def delete_lines(self):
        """
        Deletes the contents of the 
        current line(s).
        """
        textCursor = self.editor.textCursor()

        start = textCursor.selectionStart()
        end = textCursor.selectionEnd()
        textCursor.setPosition(start, QtGui.QTextCursor.MoveAnchor)
        textCursor.movePosition(QtGui.QTextCursor.StartOfLine)
        new_start = textCursor.position()

        textCursor.setPosition(end, QtGui.QTextCursor.MoveAnchor)
        textCursor.movePosition(QtGui.QTextCursor.EndOfLine)

        new_end = textCursor.position()

        textCursor.setPosition(new_start, QtGui.QTextCursor.KeepAnchor)

        if textCursor.selectedText() == '':
            textCursor.setPosition(start, QtGui.QTextCursor.MoveAnchor)
            next_line = new_end+1
            if 0 < next_line >= self.editor.document().characterCount():
                next_line = next_line-2
                if next_line == -1:
                    return
            textCursor.setPosition(next_line, QtGui.QTextCursor.KeepAnchor)

        textCursor.insertText('')

    def searchInput(self):
        """
        Very basic search dialog.
        TODO: Create a QAction and store
        this in utils so that it can be 
        linked to Ctrl + F as well.
        """
        dialog = QtWidgets.QInputDialog.getText(self.editor, 
                                                'Search', '',)
        text, ok = dialog
        if not ok:
            return

        textCursor = self.editor.textCursor()
        document = self.editor.document()
        cursor = document.find(text, textCursor)
        pos = cursor.position()
        self.editor.setTextCursor(cursor)

    def duplicate_lines(self):
        """
        Duplicates the current line or 
        selected text downwards.
        """
        textCursor = self.editor.textCursor()
        if textCursor.hasSelection():
            raise NotImplementedError
        else:
            textCursor.movePosition(QtGui.QTextCursor.EndOfLine)
            end_pos = textCursor.position()
            textCursor.movePosition(QtGui.QTextCursor.StartOfLine)
            textCursor.setPosition(end_pos, QtGui.QTextCursor.KeepAnchor)
            selected_text = textCursor.selectedText()
            textCursor.insertText(selected_text+'\n'+selected_text)

    def printHelp(self):
        """
        Prints documentation
        for selected object
        """
        text = self.editor.textCursor().selectedText()
        obj = __main__.__dict__.get(text)
        if obj is not None:
            print obj.__doc__
            
    def printType(self):
        """
        Prints type
        for selected object
        """
        text = self.editor.textCursor().selectedText()
        obj = __main__.__dict__.get(text)
        if obj is not None:
            print type(obj)

    def zoomIn(self):
        """
        Zooms in by changing the font size.
        """
        font = self.editor.font()
        size = font.pointSize()
        new_size = size + 1
        font.setPointSize(new_size)
        self.editor.setFont(font)

    def zoomOut(self):
        """
        Zooms out by changing the font size.
        """
        font = self.editor.font()
        size = font.pointSize()
        new_size = size - 1 if size > 1 else 1
        font.setPointSize(new_size)
        self.editor.setFont(font)

    def move_lines_up(self):
        """
        Moves current lines upwards.
        """
        restoreSelection = False
        textCursor = self.editor.textCursor()
        if textCursor.hasSelection():
            restoreSelection = True

        start = textCursor.selectionStart()
        end = textCursor.selectionEnd()
        selection_length = end-start
        textCursor.setPosition(start, QtGui.QTextCursor.MoveAnchor)
        textCursor.movePosition(QtGui.QTextCursor.StartOfLine)
        new_start = textCursor.position()

        textCursor.setPosition(end, QtGui.QTextCursor.MoveAnchor)
        textCursor.movePosition(QtGui.QTextCursor.EndOfLine)
        new_end = textCursor.position()

        start_offset = start-new_start
        end_offset = new_end-end

        if new_start == 0:
            return

        textCursor.setPosition(new_start, QtGui.QTextCursor.KeepAnchor)
        selectedText = textCursor.selectedText()

        textCursor.insertText('')
        textCursor.deletePreviousChar()
        textCursor.movePosition(QtGui.QTextCursor.StartOfLine)
        pos = textCursor.position()
        textCursor.insertText(selectedText+'\n')
        textCursor.setPosition(pos, QtGui.QTextCursor.MoveAnchor)

        if restoreSelection:
            moved_start = textCursor.position()+start_offset
            textCursor.setPosition(moved_start, QtGui.QTextCursor.MoveAnchor)
            moved_end = textCursor.position()+selection_length
            textCursor.setPosition(moved_end, QtGui.QTextCursor.KeepAnchor)
        else:
            textCursor.setPosition(pos+start_offset, QtGui.QTextCursor.MoveAnchor)

        self.editor.setTextCursor(textCursor)

    def move_lines_down(self):
        """
        Moves current lines downwards.
        """
        restoreSelection = False

        textCursor = self.editor.textCursor()
        if textCursor.hasSelection():
            restoreSelection = True

        start = textCursor.selectionStart()
        end = textCursor.selectionEnd()
        selection_length = end-start

        textCursor.setPosition(start, QtGui.QTextCursor.MoveAnchor)
        textCursor.movePosition(QtGui.QTextCursor.StartOfLine)
        new_start = textCursor.position()

        textCursor.setPosition(end, QtGui.QTextCursor.MoveAnchor)
        textCursor.movePosition(QtGui.QTextCursor.EndOfLine)
        new_end = textCursor.position()

        if new_end + 1 >= self.editor.document().characterCount():
            return

        start_offset = start-new_start
        end_offset = new_end-end

        textCursor.setPosition(new_start, QtGui.QTextCursor.KeepAnchor)
        selectedText = textCursor.selectedText()
        textCursor.insertText('')
        textCursor.deleteChar()
        textCursor.movePosition(QtGui.QTextCursor.EndOfLine)
        textCursor.insertText('\n'+selectedText)

        if restoreSelection:
            moved_end = textCursor.position()-end_offset
            textCursor.setPosition(moved_end, QtGui.QTextCursor.MoveAnchor)
            moved_start = moved_end-selection_length
            textCursor.setPosition(moved_start, QtGui.QTextCursor.KeepAnchor)
        else:
            pos = textCursor.position()
            textCursor.setPosition(pos-end_offset, QtGui.QTextCursor.MoveAnchor)

        self.editor.setTextCursor(textCursor)

    def move_to_top(self):
        raise NotImplementedError, 'add move line to top function'

    def move_to_bottom(self):
        raise NotImplementedError, 'add move line to bottom function'
