from __future__ import print_function
import __main__
from functools import partial

from PythonEditor.ui.Qt import QtWidgets, QtGui, QtCore
from PythonEditor.core import execute
from PythonEditor.utils.signals import connect


class ShortcutHandler(QtCore.QObject):
    """
    Shortcut Manager with custom signals.
    """
    clear_output_signal = QtCore.Signal()
    exec_text_signal = QtCore.Signal()

    def __init__(self, parent_widget, use_tabs=True):
        super(ShortcutHandler, self).__init__()
        self.setObjectName('ShortcutHandler')
        self.setParent(parent_widget)
        self.parent_widget = parent_widget

        if use_tabs:
            self.tabs = parent_widget
            # tss = self.tabs.tab_switched_signal
            # tss.connect(self.tab_switch_handler)
            self.set_editor()
        else:
            self.editor = parent_widget
            self.connect_signals()
        self.install_shortcuts()

    @QtCore.Slot(int, int, bool)
    def tab_switch_handler(self, previous, current, tabremoved):
        """
        On tab switch, disconnects previous
        tab's signals before connecting the
        new tab.
        """
        if not tabremoved:  # nothing's been deleted
                            # so we need to disconnect
                            # signals from previous editor
            self.disconnect_signals()

        self.set_editor()

    def set_editor(self):
        """
        Sets the current editor
        and connects signals.
        """
        # editor = self.tabs.currentWidget()
        editor = self.tabs.editor
        editor_changed = (True if not hasattr(self, 'editor')
                          else self.editor != editor)
        is_editor = editor.objectName() == 'Editor'
        if is_editor and editor_changed:
            self.editor = editor
            self.connect_signals()

    def connect_signals(self):
        """ Connects the current editor's signals to this class """
        editor = self.editor
        pairs = [
            (editor.tab_signal, self.tab_handler),
            (editor.return_signal, self.return_handler),
            (editor.wrap_signal, self.wrap_text),
            (editor.home_key_ctrl_alt_signal, self.move_to_top),
            (editor.end_key_ctrl_alt_signal, self.move_to_bottom),
            (editor.ctrl_x_signal, self.cut_line),
            (editor.home_key_signal, self.jump_to_start),
            (editor.wheel_signal, self.wheel_zoom),
            (editor.ctrl_enter_signal, self.exec_selected_text),
        ]
        self._connections = []
        for signal, slot in pairs:
            name, _, handle = connect(editor, signal, slot)
            self._connections.append((name, slot))

    def disconnect_signals(self):
        """ Disconnects the current editor's signals from this class """
        if not hasattr(self, 'editor'):
            return
        cx = self._connections
        for name, slot in cx:
            for x in range(self.editor.receivers(name)):
                self.editor.disconnect(name, slot)
        self._connections = []

    def install_shortcuts(self):
        """
        Maps shortcuts on the QPlainTextEdit widget
        to methods on this class.
        """
        def notimp(msg): return partial(self.notimplemented, msg)
        editor_shortcuts = {
                    'Ctrl+B': self.exec_current_line,
                    'Ctrl+Shift+Return': self.new_line_above,
                    'Ctrl+Alt+Return': self.new_line_below,
                    'Ctrl+Backspace': self.clear_output_signal.emit,
                    'Ctrl+Shift+D': self.duplicate_lines,
                    'Ctrl+H': self.print_help,
                    'Ctrl+T': self.print_type,
                    'Ctrl+Shift+F': self.search_input,
                    'Ctrl+L': self.select_lines,
                    'Ctrl+J': self.join_lines,
                    'Ctrl+/': self.comment_toggle,
                    'Ctrl+]': self.indent,
                    'Ctrl+[': self.unindent,
                    'Shift+Tab': self.unindent,
                    'Ctrl+Tab': self.next_tab,
                    'Ctrl+Shift+Tab': self.previous_tab,
                    'Ctrl+=': self.zoom_in,
                    'Ctrl++': self.zoom_in,
                    'Ctrl+-': self.zoom_out,
                    'Ctrl+Shift+K': self.delete_lines,
                    'Ctrl+D': self.select_word,
                    'Ctrl+M': self.hop_brackets,
                    'Ctrl+Shift+M': self.select_between_brackets,
                    'Ctrl+Shift+Delete': self.delete_to_end_of_line,
                    'Ctrl+Shift+Backspace': self.delete_to_start_of_line,
                    'Ctrl+Shift+Up': self.move_lines_up,
                    'Ctrl+Shift+Down': self.move_lines_down,
                    # 'Ctrl+Shift+Alt+Up': notimp('duplicate cursor up'),
                    # 'Ctrl+Shift+Alt+Down': notimp('duplicate cursor down'),
                    }

        if hasattr(self, 'tabs'):
            tab_shortcuts = {
                        'Ctrl+Shift+N': self.tabs.new_tab,
                        'Ctrl+Shift+W': self.tabs.close_current_tab,
                        # 'Ctrl+Shift+T': notimp('reopen previous tab'),
                        }
            editor_shortcuts.update(tab_shortcuts)

        def doc(f): return f.func_doc if hasattr(f, 'func_doc') else f.__doc__
        self.shortcut_dict = {key: doc(func)
                              for key, func in editor_shortcuts.items()}

        signal_dict = {
            'Tab': self.tab_handler.__doc__,
            'Return/Enter': self.return_handler.__doc__,
            r'\' " ( ) [ ] \{ \}': self.wrap_text.__doc__,
            'Ctrl+Alt+Home': self.move_to_top.__doc__,
            'Ctrl+Alt+End': self.move_to_bottom.__doc__,
            'Ctrl+X': self.cut_line.__doc__,
            'Home': self.jump_to_start.__doc__,
            'Ctrl+Mouse Wheel': self.wheel_zoom.__doc__,
            'Ctrl+Backspace': '\n'+' '*8+'Clear Output Terminal\n',
            }

        self.shortcut_dict.update(signal_dict)

        context = QtCore.Qt.WidgetShortcut
        for shortcut, func in editor_shortcuts.items():
            keySequence = QtGui.QKeySequence(shortcut)
            qshortcut = QtWidgets.QShortcut(
                                            keySequence,
                                            self.parent_widget,
                                            func,
                                            context=context)
            qshortcut.setObjectName(shortcut)

    def notimplemented(self, text):
        """ Development reminders to implement features """
        raise NotImplementedError(text)

    def get_selected_blocks(self, ignoreEmpty=True):
        """
        Utility method for getting lines in selection.
        """
        textCursor = self.editor.textCursor()
        doc = self.editor.document()
        start = textCursor.selectionStart()
        end = textCursor.selectionEnd()

        # get line numbers
        blockNumbers = set([
                doc.findBlock(b).blockNumber()
                for b in range(start, end)
                    ])

        pos = textCursor.position()
        blockNumbers |= set([doc.findBlock(pos).blockNumber()])

        def isEmpty(b): return doc.findBlockByNumber(b).text().strip() != ''
        blocks = []
        for b in blockNumbers:
            bn = doc.findBlockByNumber(b)
            if not ignoreEmpty:
                blocks.append(bn)
            elif isEmpty(b):
                blocks.append(bn)

        return blocks

    def offset_for_traceback(self, text=None):
        """
        Offset text using newlines to get proper line ref in tracebacks.
        """
        textCursor = self.editor.textCursor()

        if text is None:
            text = textCursor.selection().toPlainText()

        selection_offset = textCursor.selectionStart()
        doc = self.editor.document()
        block_num = doc.findBlock(selection_offset).blockNumber()
        text = '\n' * block_num + text
        return text

    def exec_selected_text(self):
        """
        Calls exec with either selected text
        or all the text in the edit widget.
        TODO: in some instances, this can still have the wrong
        line number in tracebacks! Frustratingly, it seems to right
        itself after a normal execution (full text) run.
        """
        textCursor = self.editor.textCursor()

        whole_text = self.editor.toPlainText().strip()

        if textCursor.hasSelection():
            text = self.offset_for_traceback()
        else:
            text = whole_text

        self.exec_text_signal.emit()
        whole_text = '\n'+whole_text
        error_line_numbers = execute.mainexec(text, whole_text)
        if error_line_numbers is None:
            return
        else:
            self.highlight_errored_lines(error_line_numbers)

    def exec_current_line(self):
        """
        Calls exec with the text of the line the cursor is on.
        Calls lstrip on current line text to allow exec of indented text.
        """
        textCursor = self.editor.textCursor()
        whole_text = self.editor.toPlainText()

        if textCursor.hasSelection():
            return self.exec_selected_text()

        textCursor.select(QtGui.QTextCursor.BlockUnderCursor)
        text = textCursor.selection().toPlainText().lstrip()
        text = self.offset_for_traceback(text=text)

        whole_text = '\n'+whole_text
        error_line_numbers = execute.mainexec(text, whole_text, verbosity=1)
        if error_line_numbers is None:
            return
        else:
            self.highlight_errored_lines(error_line_numbers)

    def highlight_errored_lines(self, error_line_numbers):
        """
        Draw a red background on any lines that caused an error.
        """
        extraSelections = []

        cursor = self.editor.textCursor()
        doc = self.editor.document()
        for lineno in error_line_numbers:


            selection = QtWidgets.QTextEdit.ExtraSelection()
            lineColor = QtGui.QColor.fromRgbF(0.8,
                                              0.1,
                                              0,
                                              0.2)

            selection.format.setBackground(lineColor)
            selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection,
                                         True)

            block = doc.findBlockByLineNumber(lineno-1)
            cursor.setPosition(block.position())
            selection.cursor = cursor
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.editor.setExtraSelections(extraSelections)

    @QtCore.Slot(QtGui.QKeyEvent)
    def return_handler(self, event):
        """
        New line with auto-indentation.
        """
        return self.indent_next_line()

    def indent_next_line(self):
        """
        Match next line indentation to current line
        If ':' is character in cursor position and
        current line contains non-whitespace
        characters, add an extra four spaces.
        """
        textCursor = self.editor.textCursor()
        line = textCursor.block().text()
        indentCount = len(str(line)) - len(str(line).lstrip(' '))

        doc = self.editor.document()
        if doc.characterAt(textCursor.position()-1) == ':':
            indentCount = indentCount + 4

        insertion = '\n'+' '*indentCount
        if len(line.strip()) == 0:
            insertion = '\n'

        if not self.editor.wait_for_autocomplete:
            textCursor.insertText(insertion)
            self.editor.setTextCursor(textCursor)

        return True

        return True

    @QtCore.Slot()
    def cut_line(self):
        """
        If no text selected, cut whole
        current line to clipboard.
        """
        textCursor = self.editor.textCursor()
        if textCursor.hasSelection():
            return

        textCursor.select(QtGui.QTextCursor.LineUnderCursor)
        text = textCursor.selectedText()
        textCursor.insertText('')

        QtGui.QClipboard().setText(text)

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
        Indents selected text. If no text
        is selected, adds four spaces.
        """
        textCursor = self.editor.textCursor()
        if textCursor.hasSelection():
            self.indent()
        else:
            self.tab_space()

    def indent(self):
        """
        Indent Selected Text
        """
        blocks = self.get_selected_blocks()
        for block in blocks:
            cursor = QtGui.QTextCursor(block)
            cursor.movePosition(QtGui.QTextCursor.StartOfLine)
            cursor.insertText('    ')

    def unindent(self):
        """
        Unindent Selected Text
        TODO: Maintain original selection
        and cursor position.
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

    def next_tab(self):
        if hasattr(self, 'tabs'):
            next_index = self.tabs.currentIndex()+1
            if self.tabs.widget(next_index).objectName() == 'Editor':
                self.tabs.setCurrentIndex(next_index)

    def previous_tab(self):
        if hasattr(self, 'tabs'):
            self.tabs.setCurrentIndex(self.tabs.currentIndex()-1)

    def jump_to_start(self):
        """
        Jump to first character in line.
        If at first character, jump to
        start of line.
        """
        textCursor = self.editor.textCursor()
        init_pos = textCursor.position()
        textCursor.select(QtGui.QTextCursor.LineUnderCursor)
        text = textCursor.selection().toPlainText()
        textCursor.movePosition(QtGui.QTextCursor.StartOfLine)
        pos = textCursor.position()
        offset = len(text)-len(text.lstrip())
        new_pos = pos+offset
        if new_pos != init_pos:
            textCursor.setPosition(new_pos, QtGui.QTextCursor.MoveAnchor)
        self.editor.setTextCursor(textCursor)

    def comment_toggle(self):
        """
        Toggles commenting out selected lines,
        or lines with cursor.
        """
        blocks = self.get_selected_blocks()

        # iterate through lines in doc commenting or uncommenting
        # based on whether everything is commented or not
        commentAllOut = any([not str(block.text()).lstrip().startswith('#')
                            for block in blocks])
        if commentAllOut:
            for block in blocks:
                cursor = QtGui.QTextCursor(block)
                cursor.select(QtGui.QTextCursor.LineUnderCursor)
                selectedText = cursor.selectedText()
                right_split = len(selectedText.lstrip())
                count = len(selectedText)
                split_index = count-right_split
                split_text = selectedText[split_index:]
                newText = ' '*split_index + '#' + split_text
                cursor.insertText(newText)
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
        elif key in ['<', '>']:
            key_in = '<'
            key_out = '>'

        textCursor = self.editor.textCursor()
        text = key_in + textCursor.selectedText() + key_out
        textCursor.insertText(text)

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

        textCursor.setPosition(new_end, QtGui.QTextCursor.KeepAnchor)
        self.editor.setTextCursor(textCursor)

    def join_lines(self):
        """
        Joins current line(s) with next by deleting the
        newline at the end of the current line(s).
        """
        textCursor = self.editor.textCursor()

        blocks = self.get_selected_blocks(ignoreEmpty=False)
        if len(blocks) > 1:
            text = textCursor.selectedText()
            text = ' '.join(ln.strip() for ln in text.splitlines())
            textCursor.insertText(text)
        else:
            block = textCursor.block()
            text = block.text()
            next_line = block.next().text().strip()
            new_text = text + ' ' + next_line

            textCursor.select(QtGui.QTextCursor.LineUnderCursor)
            textCursor.movePosition(QtGui.QTextCursor.EndOfLine)
            new_pos = textCursor.position()+1
            if new_pos >= self.editor.document().characterCount():
                return
            textCursor.setPosition(new_pos, QtGui.QTextCursor.KeepAnchor)

            textCursor.insertText('')
            textCursor.select(QtGui.QTextCursor.LineUnderCursor)
            textCursor.insertText(new_text)

            self.editor.setTextCursor(textCursor)

    def delete_lines(self):
        """
        Deletes the contents of the current line(s).
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

    def select_word(self):
        """
        Selects the word under cursor if no selection.
        If selection, selects next occurence of the same word.
        TODO: 1 )could optionally highlight all occurences of the word
        and iterate to the next selection. 2) Would be nice if extra
        selections could be made editable. 3) Wrap around.
        """
        textCursor = self.editor.textCursor()
        if not textCursor.hasSelection():
            textCursor.select(QtGui.QTextCursor.WordUnderCursor)
            return self.editor.setTextCursor(textCursor)

        text = textCursor.selection().toPlainText()
        start_pos = textCursor.selectionStart()
        end_pos = textCursor.selectionEnd()
        word_len = abs(end_pos - start_pos)

        whole_text = self.editor.toPlainText()
        second_half = whole_text[end_pos:]
        next_pos = second_half.find(text)

        if next_pos == -1:
            return

        next_start = next_pos + start_pos + word_len
        next_end = next_start + word_len

        textCursor.setPosition(next_start, QtGui.QTextCursor.MoveAnchor)
        textCursor.setPosition(next_end, QtGui.QTextCursor.KeepAnchor)
        self.editor.setTextCursor(textCursor)

        extraSelections = []

        selection = QtWidgets.QTextEdit.ExtraSelection()

        lineColor = QtGui.QColor.fromRgbF(1, 1, 1, 0.3)
        selection.format.setBackground(lineColor)
        selection.cursor = self.editor.textCursor()
        selection.cursor.setPosition(start_pos, QtGui.QTextCursor.MoveAnchor)
        selection.cursor.setPosition(end_pos, QtGui.QTextCursor.KeepAnchor)
        extraSelections.append(selection)
        self.editor.setExtraSelections(extraSelections)

    def hop_brackets(self):
        """
        Jump to closest bracket, starting
        with closing bracket.
        """
        textCursor = self.editor.textCursor()
        pos = textCursor.position()
        whole_text = self.editor.toPlainText()

        first_half = whole_text[:pos]
        second_half = whole_text[pos:]
        first_pos = first_half.rfind('(')
        second_pos = second_half.find(')')

        first_pos = first_pos + 1
        second_pos = second_pos + pos

        new_pos = first_pos if whole_text[pos] == ')' else second_pos
        textCursor.setPosition(new_pos, QtGui.QTextCursor.MoveAnchor)
        self.editor.setTextCursor(textCursor)

    def select_between_brackets(self):
        """
        Selects text between [] {} ()
        TODO: implement [] and {}
        """
        textCursor = self.editor.textCursor()
        pos = textCursor.position()
        whole_text = self.editor.toPlainText()

        first_half = whole_text[:pos]
        second_half = whole_text[pos:]
        first_pos = first_half.rfind('(')
        second_pos = second_half.find(')')

        first_pos = first_pos + 1
        second_pos = second_pos + pos

        textCursor.setPosition(first_pos, QtGui.QTextCursor.MoveAnchor)
        textCursor.setPosition(second_pos, QtGui.QTextCursor.KeepAnchor)
        self.editor.setTextCursor(textCursor)

    def search_input(self):
        """
        Very basic search dialog.
        TODO: Create a QAction/util for this
        as it is also accessed through
        the right-click menu.
        """
        getText = QtWidgets.QInputDialog.getText
        dialog = getText(self.editor, 'Search', '',)
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
            selected_text = textCursor.selectedText()
            for i in range(2):
                textCursor.insertText(selected_text)
                self.editor.setTextCursor(textCursor)
        else:
            textCursor.movePosition(QtGui.QTextCursor.EndOfLine)
            end_pos = textCursor.position()
            textCursor.movePosition(QtGui.QTextCursor.StartOfLine)
            textCursor.setPosition(end_pos, QtGui.QTextCursor.KeepAnchor)
            selected_text = textCursor.selectedText()
            textCursor.insertText(selected_text+'\n'+selected_text)

    def delete_to_end_of_line(self):
        """
        Deletes characters from cursor
        position to end of line.
        """
        textCursor = self.editor.textCursor()
        pos = textCursor.position()
        textCursor.movePosition(QtGui.QTextCursor.EndOfLine)
        textCursor.setPosition(pos, QtGui.QTextCursor.KeepAnchor)
        textCursor.insertText('')

    def delete_to_start_of_line(self):
        """
        Deletes characters from cursor
        position to start of line.
        """
        textCursor = self.editor.textCursor()
        pos = textCursor.position()
        textCursor.movePosition(QtGui.QTextCursor.StartOfLine)
        textCursor.setPosition(pos, QtGui.QTextCursor.KeepAnchor)
        textCursor.insertText('')

    def print_help(self):
        """
        Prints documentation
        for selected object
        """
        cursor = self.editor.textCursor()
        selection = cursor.selection()
        text = selection.toPlainText().strip()
        obj = __main__.__dict__.get(text)
        if obj is not None:
            print(obj.__doc__)
        else:
            exec('help('+text+')', __main__.__dict__)

    def print_type(self):
        """
        Prints type
        for selected object
        """
        cursor = self.editor.textCursor()
        selection = cursor.selection()
        text = selection.toPlainText().strip()
        obj = __main__.__dict__.get(text)
        if obj is not None:
            print(type(obj))
        else:
            exec('print(type('+text+'))', __main__.__dict__)

    def zoom_in(self):
        """
        Zooms in by changing the font size.
        """
        font = self.editor.font()
        size = font.pointSize()
        new_size = size + 1
        font.setPointSize(new_size)
        self.editor.setFont(font)

    def zoom_out(self):
        """
        Zooms out by changing the font size.
        """
        font = self.editor.font()
        size = font.pointSize()
        new_size = size - 1 if size > 1 else 1
        font.setPointSize(new_size)
        self.editor.setFont(font)

    def wheel_zoom(self, event):
        """
        Zooms by changing the font size
        according to the wheel zoom delta.
        """
        font = self.editor.font()
        size = font.pointSize()
        delta = event.delta()
        amount = int(delta/10) if delta > 1 or delta < -1 else delta
        new_size = size + amount
        new_size = new_size if new_size > 0 else 1
        font.setPointSize(new_size)
        self.editor.setFont(font)

    def move_lines_up(self):
        """
        Moves current lines upwards.
        TODO: Bug fix! Doesn't work with wrapped
        text (presumably needs correct block)
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

        start_offset = start-new_start

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
            new_pos = pos+start_offset
            textCursor.setPosition(new_pos, QtGui.QTextCursor.MoveAnchor)

        self.editor.setTextCursor(textCursor)

    def move_lines_down(self):
        """
        Moves current lines downwards.
        TODO: Bug fix! Doesn't work with wrapped
        text (presumably needs correct block)
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
            new_pos = pos-end_offset
            textCursor.setPosition(new_pos, QtGui.QTextCursor.MoveAnchor)

        self.editor.setTextCursor(textCursor)

    def move_to_top(self):
        """
        Move selection or line if no
        selection to top of document.
        """
        textCursor = self.editor.textCursor()
        if not textCursor.hasSelection():
            textCursor.select(QtGui.QTextCursor.LineUnderCursor)
        text = textCursor.selectedText()
        textCursor.insertText('')
        textCursor.setPosition(0, QtGui.QTextCursor.MoveAnchor)
        textCursor.insertText(text)
        self.editor.setTextCursor(textCursor)

    def move_to_bottom(self):
        """
        Move selection or line if no
        selection to bottom of document.
        """
        textCursor = self.editor.textCursor()
        if not textCursor.hasSelection():
            textCursor.select(QtGui.QTextCursor.LineUnderCursor)
        text = textCursor.selectedText()
        textCursor.insertText('')
        end = len(self.editor.toPlainText())
        textCursor.setPosition(end, QtGui.QTextCursor.MoveAnchor)
        textCursor.insertText(text)
        self.editor.setTextCursor(textCursor)
