from __future__ import print_function
import __main__
from functools import partial

from PythonEditor.ui.Qt import QtWidgets, QtGui, QtCore
from PythonEditor.core import execute
from PythonEditor.utils.signals import connect
from PythonEditor.utils import save
from PythonEditor.ui.features import actions

# TODO: this will probably end up in a user-editable JSON file.
REGISTER = {
'editor': {
    'Ctrl+H' : 'Print Help',
    'Ctrl+E' : 'Open Module File',
    'Ctrl+F' : 'Search',
    # ''     : 'Open Module Directory',
    },
'tabs': {
    },
'terminal': {
    },
}

# TODO:
# This needs to be moved to 'actions' and replaced with
# a class that reads user-registered shortcuts and
# applies them to their respective actions through __setitem__
class ShortcutHandler(QtCore.QObject):
    """
    Shortcut Manager with custom signals.
    """
    clear_output_signal = QtCore.Signal()
    exec_text_signal = QtCore.Signal()

    def __init__(self, parent_widget, use_tabs=True):
        """
        :param use_tabs:
        If False, the parent_widget is the QPlainTextEdit (Editor)
        widget. If True, apply shortcuts to the QTabBar as well as
        the Editor.
        """
        super(ShortcutHandler, self).__init__()
        self.setObjectName('ShortcutHandler')
        self.setParent(parent_widget)
        self.parent_widget = parent_widget
        self.use_tabs = use_tabs

        if use_tabs:
            self.tabs = parent_widget.tabs
            self.editor = parent_widget.editor
        else:
            self.editor = parent_widget

        self.connect_signals()
        self.install_shortcuts()

    def connect_signals(self):
        """ Connects the current editor's signals to this class """
        editor = self.editor
        pairs = [
            (editor.tab_signal,               self.tab_handler),
            (editor.return_signal,            self.return_handler),
            (editor.wrap_signal,              self.wrap_text),
            (editor.home_key_ctrl_alt_signal, self.move_to_top),
            (editor.end_key_ctrl_alt_signal,  self.move_to_bottom),
            (editor.ctrl_x_signal,            self.cut_line),
            (editor.ctrl_c_signal,            self.copy_block_or_selection),
            (editor.ctrl_s_signal,            self.save),
            (editor.home_key_signal,          self.jump_to_start),
            (editor.wheel_signal,             self.wheel_zoom),
            (editor.ctrl_enter_signal,        self.exec_handler),
        ]
        self._connections = []
        for signal, slot in pairs:
            name, _, handle = connect(editor, signal, slot)
            self._connections.append((name, slot))

    def install_shortcuts(self):
        """
        Maps shortcuts on the QPlainTextEdit widget
        to methods on this class.
        """
        def notimp(msg): return partial(self.notimplemented, msg)
        editor_shortcuts = {
            'Ctrl+B'               : self.exec_current_line,
            'Ctrl+Shift+Return'    : self.new_line_above,
            'Ctrl+Alt+Return'      : self.new_line_below,
            'Ctrl+Shift+D'         : self.duplicate_lines,
            'Ctrl+Shift+T'         : self.print_type,
            # 'Ctrl+Shift+F'         : self.search_input,
            # 'Ctrl+H'               : self.print_help,
            'Ctrl+L'               : self.select_lines,
            'Ctrl+J'               : self.join_lines,
            'Ctrl+/'               : self.comment_toggle,
            'Ctrl+]'               : self.indent,
            'Ctrl+['               : self.unindent,
            'Shift+Tab'            : self.unindent,
            'Ctrl+='               : self.zoom_in,
            'Ctrl++'               : self.zoom_in,
            'Ctrl+-'               : self.zoom_out,
            'Ctrl+Shift+K'         : self.delete_lines,
            'Ctrl+D'               : self.select_word,
            'Ctrl+M'               : self.hop_brackets,
            'Ctrl+Shift+M'         : self.select_between_brackets,
            'Ctrl+Shift+Delete'    : self.delete_to_end_of_line,
            'Ctrl+Shift+Backspace' : self.delete_to_start_of_line,
            'Ctrl+Shift+Up'        : self.move_blocks_up,
            'Ctrl+Shift+Down'      : self.move_blocks_down,
            'Ctrl+G'               : notimp('goto'),
            'Ctrl+P'               : notimp('palette'),
            'Ctrl+C'               : self.copy_block_or_selection,
            # 'Ctrl+E'               : self.open_module_file,
            # 'Ctrl+Shift+Alt+Up': notimp('duplicate cursor up'),
            # 'Ctrl+Shift+Alt+Down': notimp('duplicate cursor down'),
        }

        if self.use_tabs:
            editor_shortcuts['Ctrl+S'] = self.save
            editor_shortcuts[QtCore.Qt.Key_F5] = self.parent_widget.parent().parent().parent().reload_package

        terminal_shortcuts = {
                    'Ctrl+Backspace': self.clear_output_signal.emit,
                    }
        editor_shortcuts.update(terminal_shortcuts)

        if self.use_tabs:
            tab_shortcuts = {
                        'Ctrl+T': self.tabs.new_tab,
                        'Ctrl+Shift+N': self.tabs.new_tab,
                        'Ctrl+Shift+W': self.tabs.remove_current_tab,
                        'Ctrl+Tab': self.next_tab,
                        'Ctrl+Shift+Tab': self.previous_tab,
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

        def add_action(action, widget, shortcut, func):
            """
            Add action to widget with a shortcut that
            triggers the given function.

            :action: QtWidgets.QAction
            :widget: QtWidgets.QWidget
            :shortcut: str (e.g. 'Ctrl+S') or Qt Key
            :func: a callable that gets executed
                   when triggering the action.
            """
            key_seq = QtGui.QKeySequence(shortcut)
            action.setShortcut(key_seq)
            action.setShortcutContext(
                QtCore.Qt.WidgetShortcut
            )
            action.triggered.connect(func)
            widget.addAction(action)

        for shortcut, func in editor_shortcuts.items():
            a = QtWidgets.QAction(self.editor)
            add_action(a, self.editor, shortcut, func)

        if self.use_tabs:
            terminal = self.parent_widget.parent().parent().terminal
            for shortcut, func in terminal_shortcuts.items():
                a = QtWidgets.QAction(terminal)
                add_action(a, terminal, shortcut, func)

            for shortcut, func in tab_shortcuts.items():
                a = QtWidgets.QAction(self.tabs)
                add_action(a, self.tabs, shortcut, func)

        self.register_shortcuts()

    def register_shortcuts(self):
        global REGISTER
        for widget_name, actions in REGISTER.items():
            if not hasattr(self, widget_name):
                continue
            widget = getattr(self, widget_name)
            for shortcut, action_description in actions.items():
                for action in widget.actions():
                    if action.text() == action_description:
                        key_seq = QtGui.QKeySequence(shortcut)
                        action.setShortcut(key_seq)
                        action.setShortcutContext(
                            QtCore.Qt.WidgetShortcut
                        )

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

    def save(self):
        actions.save_action(
            self.tabs,
            self.editor
        )

    # FIXME: Has been moved to actions.
    def open_module_file(self):
        textCursor = self.editor.textCursor()
        text = textCursor.selection().toPlainText()
        if not text.strip():
            return

        obj = actions.get_subobject(text)
        actions.open_module_file(obj)

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

    def exec_text(self, text, whole_text):
        """
        Execute whatever text is passed into this function.

        :text: the actual text to be executed
        :whole_text: the whole text for context and full traceback
        """
        self.exec_text_signal.emit()
        error_line_numbers = execute.mainexec(text, whole_text)
        if error_line_numbers is None:
            return
        else:
            self.highlight_errored_lines(error_line_numbers)

    def exec_handler(self):
        """
        If text is selected, call exec on that text.
        If no text is selected, look for cells bordered
        by the symbols #&& and execute text between those borders.
        """
        textCursor = self.editor.textCursor()
        whole_text = self.editor.toPlainText()
        if not whole_text.strip():
            return

        # check that the document doesn't just have comments.
        if self.just_comments(whole_text):
            return

        # execute only selection
        if textCursor.hasSelection():
            text = textCursor.selection().toPlainText()
            if not text.strip():
                return
            # check that the selected text doesn't just have comments.
            if self.just_comments(text):
                return
            multiline_text = ('\n' in text)
            if not multiline_text:
                whole_text = '\n'+whole_text
            text = self.offset_for_traceback()
            return self.exec_text(text, whole_text)

        # if there are cells (marked by '\n#&&')
        # execute current cell
        if '\n#&&' in whole_text:
            return self.exec_current_cell()

        # execute whole document
        text = whole_text
        whole_text = '\n'+whole_text
        return self.exec_text(text, whole_text)

    def exec_current_cell(self):
        textCursor = self.editor.textCursor()
        whole_text = self.editor.toPlainText()
        if not whole_text.strip():
            return

        # if there are cells (marked by '\n#&&')
        # execute only that cell.
        text = whole_text
        whole_text = '\n'+whole_text

        # split the text by the cursor position
        pos = textCursor.position()
        text_before = text[:pos]
        text_after = text[pos:]

        # recover text from the current cell
        symbol_pos = text_before.rfind('#&&')
        cell_top = text_before.split('\n#&&')[-1]
        cell_bottom = text_after.split('\n#&&')[0]
        cell_text = cell_top + cell_bottom
        if not cell_text.strip():
            return
        doc = self.editor.document()
        block_num = doc.findBlock(symbol_pos).blockNumber()
        cell_text = '\n' * block_num + cell_text

        # check that the cell doesn't just have comments.
        if self.just_comments(cell_text):
            return
        self.exec_text(cell_text, whole_text)

    def exec_current_line(self):
        """
        Calls exec() with the text of the line the cursor is on.
        Calls lstrip on current line text to allow exec of indented text.
        """
        textCursor = self.editor.textCursor()
        whole_text = self.editor.toPlainText()

        if textCursor.hasSelection():
            return self.exec_handler()

        textCursor.select(QtGui.QTextCursor.BlockUnderCursor)
        text = textCursor.selection().toPlainText().lstrip()
        if not text:
            return
        # check that the current line doesn't just have comments.
        if self.just_comments(text):
            return
        text = self.offset_for_traceback(text=text)

        whole_text = '\n'+whole_text
        error_line_numbers = execute.mainexec(
            text,
            whole_text,
            verbosity=1
        )
        if error_line_numbers is None:
            return

        self.highlight_errored_lines(error_line_numbers)

    def just_comments(self, text):
        """
        Check that the given text doesn't
        just contain comments.
        """
        lines = text.strip().splitlines()
        for line in lines:
            if not line.strip():
                continue
            if line.strip().startswith('#'):
                continue
            return False
        return True

    def highlight_errored_lines(self, error_line_numbers):
        """
        Draw a red background on any lines that caused an error.
        """
        extraSelections = self.editor.extraSelections()

        cursor = self.editor.textCursor()
        doc = self.editor.document()
        for lineno in error_line_numbers:
            selection = QtWidgets.QTextEdit.ExtraSelection()
            lineColor = QtGui.QColor.fromRgbF(0.8,
                                              0.1,
                                              0,
                                              0.2)

            selection.format.setBackground(lineColor)
            selection.format.setProperty(
                QtGui.QTextFormat.FullWidthSelection,
                True
            )

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
        text = textCursor.block().text()
        indentCount = len(text) - len(text.lstrip(' '))

        doc = self.editor.document()
        if doc.characterAt(textCursor.position()-1) == ':':
            indentCount = indentCount + 4

        insertion = '\n'+' '*indentCount
        if len(text.strip()) == 0:
            insertion = '\n'

        if not self.editor.wait_for_autocomplete:
            textCursor.insertText(insertion)
            self.editor.setTextCursor(textCursor)

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
        Unindent selected text.
        """
        # TODO: Maintain original selection
        # and cursor position.
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
        """
        Switch to the next tab.
        """
        if hasattr(self, 'tabs'):
            next_index = self.tabs.currentIndex()+1
            if next_index <= self.tabs.count():
                self.tabs.setCurrentIndex(next_index)

    def previous_tab(self):
        """
        Switch to the next tab.
        """
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
        # elif key in ['<', '>']:
        #     key_in = '<'
        #     key_out = '>'

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

    def copy_block_or_selection(self):
        """
        If there's no text selected,
        copy the current block.
        """
        textCursor = self.editor.textCursor()
        selection = textCursor.selection()
        text = selection.toPlainText()
        if not text:
            textCursor.select(QtGui.QTextCursor.BlockUnderCursor)
            selection = textCursor.selection()
            text = selection.toPlainText()

        QtGui.QClipboard().setText(text)

    def select_word(self):
        """
        Selects the word under cursor if no selection.
        If selection, selects next occurence of the same word.
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
        """
        # TODO: implement [] and {}
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
        """
        # TODO: Create a QAction/util for this
        # as it is also accessed through
        # the right-click menu.
        getText = QtWidgets.QInputDialog.getText
        dialog = getText(self.editor, 'Search', '',)
        text, ok = dialog
        if not ok:
            return

        textCursor = self.editor.textCursor()
        original_pos = textCursor.position()

        # start the search from the beginning of the document
        textCursor.setPosition(0, QtGui.QTextCursor.MoveAnchor)
        document = self.editor.document()
        cursor = document.find(text, textCursor)
        pos = cursor.position()
        if pos != -1:
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

    # FIXME: moved to actions. Delete once ShortcutHandler assigns shortcuts
    def print_help(self):
        """
        Prints documentation
        for selected object
        """
        cursor = self.editor.textCursor()
        selection = cursor.selection()
        text = selection.toPlainText().strip()
        if not text:
            return
        obj = __main__.__dict__.get(text)
        if obj is not None:
            print(obj.__doc__)
        elif text:
            exec('help('+text+')', __main__.__dict__)

    def print_type(self):
        """
        Prints type
        for selected object
        """
        cursor = self.editor.textCursor()
        selection = cursor.selection()
        text = selection.toPlainText().strip()
        if not text:
            return
        obj = __main__.__dict__.get(text)
        if obj is not None:
            print(type(obj))
        elif text:
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

    def move_blocks_up(self):
        """
        Moves selected blocks upwards.
        """
        restoreSelection = False
        textCursor = self.editor.textCursor()
        if textCursor.hasSelection():
            restoreSelection = True

        start = textCursor.selectionStart()
        end = textCursor.selectionEnd()
        selection_length = end-start
        textCursor.setPosition(start, QtGui.QTextCursor.MoveAnchor)
        textCursor.movePosition(QtGui.QTextCursor.StartOfBlock)
        new_start = textCursor.position()

        textCursor.setPosition(end, QtGui.QTextCursor.MoveAnchor)
        textCursor.movePosition(QtGui.QTextCursor.EndOfBlock)

        start_offset = start-new_start

        if new_start == 0:
            return

        textCursor.setPosition(new_start, QtGui.QTextCursor.KeepAnchor)
        selectedText = textCursor.selectedText()

        textCursor.insertText('')
        textCursor.deletePreviousChar()
        textCursor.movePosition(QtGui.QTextCursor.StartOfBlock)
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

    def move_blocks_down(self):
        """
        Moves selected blocks downwards.
        """
        restoreSelection = False

        textCursor = self.editor.textCursor()
        if textCursor.hasSelection():
            restoreSelection = True

        start = textCursor.selectionStart()
        end = textCursor.selectionEnd()
        selection_length = end-start

        textCursor.setPosition(start, QtGui.QTextCursor.MoveAnchor)
        textCursor.movePosition(QtGui.QTextCursor.StartOfBlock)
        new_start = textCursor.position()

        textCursor.setPosition(end, QtGui.QTextCursor.MoveAnchor)
        textCursor.movePosition(QtGui.QTextCursor.EndOfBlock)
        new_end = textCursor.position()

        if new_end + 1 >= self.editor.document().characterCount():
            return

        end_offset = new_end-end

        textCursor.setPosition(new_start, QtGui.QTextCursor.KeepAnchor)
        selectedText = textCursor.selectedText()
        textCursor.insertText('')
        textCursor.deleteChar()
        textCursor.movePosition(QtGui.QTextCursor.EndOfBlock)
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
