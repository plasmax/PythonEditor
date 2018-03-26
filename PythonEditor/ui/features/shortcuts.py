from functools import partial
from PythonEditor.ui.Qt import QtWidgets, QtGui, QtCore
from PythonEditor.core import execute

class ShortcutHandler(QtCore.QObject):
    """
    Shortcut Manager with custom signals.
    """
    clear_output_signal = QtCore.Signal()
    exec_text_signal = QtCore.Signal()

    def __init__(self, editor):
        super(ShortcutHandler, self).__init__()
        self.setObjectName('ShortcutHandler')
        self.setParent(editor)
        self.editor = editor
        self.installShortcuts()
        self.connectSignals()

    def connectSignals(self):
        """
        For shortcuts that cannot be 
        handled directly by QShortcut.
        """
        self.editor.tab_signal.connect(self.tab_handler)
        self.editor.return_signal.connect(self.return_handler)
        self.editor.wrap_signal.connect(self.wrap_text)

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
                    'Ctrl+D': notimp('select word or next word'),
                    'Ctrl+Shift+D': notimp('duplicate lines'),
                    'Ctrl+W': notimp('close tab'),
                    'Ctrl+H': notimp('print selection help'),
                    'Ctrl+T': notimp('print selection type'),
                    'Ctrl+F': notimp('search function'),
                    'Ctrl+L': self.select_lines,
                    'Ctrl+J': notimp('join lines'),
                    'Ctrl+M': notimp('jump to nearest bracket'),
                    'Ctrl+Shift+M': notimp('select between brackets'),
                    'Ctrl+/': self.comment_toggle,
                    'Ctrl+]': self.indent,
                    'Ctrl+[': self.unindent,
                    'Shift+Tab' : self.unindent,
                    'Ctrl+=': notimp('zoom in'),
                    'Ctrl++': notimp('zoom in'),
                    'Ctrl+-': notimp('zoom out'),
                    'Ctrl+Shift+K': notimp('delete lines'),
                    'Ctrl+Shift+Down': notimp('move lines down'),
                    'Ctrl+Shift+Up': notimp('move lines up'),
                    'Ctrl+Alt+Up': notimp('duplicate cursor up'),
                    'Ctrl+Alt+Down': notimp('duplicate cursor down'),
                  }

        context = QtCore.Qt.WidgetShortcut
        for shortcut, func in mapping.iteritems():
            keySequence = QtGui.QKeySequence(shortcut)
            qshortcut = QtWidgets.QShortcut(
                                            keySequence, 
                                            self.editor, 
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

        blocks = []
        for b in blockNumbers:
            bn = doc.findBlockByNumber(b)
            if not ignoreEmpty:
                blocks.append(bn)
            elif doc.findBlockByNumber(b).text().strip() != '':
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
        """ Indent Selected Text """
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
