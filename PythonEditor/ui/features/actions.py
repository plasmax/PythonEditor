"""
The actions module houses the majority of the functionality
of the PythonEditor user interface. Widgets with the Actions
class applied will have all the methods available on that
class applied to the widget as actions, using an overridable
JSON dictionary with shortcuts and menu locations to synchronize
these actions accross menus and shortcuts, which are applied
in the shortcuts, contextmenu and menubar modules.
"""
from __future__ import print_function
import os
import uuid
import __main__
import inspect
import subprocess
import json

from PythonEditor.ui.Qt import QtWidgets
from PythonEditor.ui.Qt import QtGui
from PythonEditor.ui.Qt import QtCore

from PythonEditor.utils import save
from PythonEditor.core import execute


def load_actions_from_json():
    """
    Return a dictionary from reading the
    JSON file that stores action names and
    their attributes.
    """
    folder = os.path.dirname(__file__)
    actions_path = os.path.join(
        folder,
        'action_register.json'
    )
    if not os.path.exists(actions_path):
        raise Exception(
            'Could not locate %s '
            % actions_path
            )
    with open(actions_path, 'r') as f:
        action_dict = json.load(f)

    # TODO:
    # search for user-defined PythonEditorShortcuts.json
    # (or perhaps in XML) that allow dictionary updates here.

    return action_dict


class Actions(QtCore.QObject):
    """
    Collection of QActions that are
    accessible for menu and shortcut registry.
    """
    # clear_output_signal = QtCore.Signal()
    exec_text_signal = QtCore.Signal()

    actions = {}
    def __init__(
            self,
            pythoneditor=None,
            editor=None,
            tabeditor=None,
            terminal=None,
        ):
        """
        :param pythoneditor:
        :param editor:
        :param tabeditor:
        :param terminal:
        """
        super(Actions, self).__init__()
        self.setObjectName('Actions')

        if editor is None:
            raise Exception(
            'A text editor is necessary for this class.'
            )
        self.editor = editor

        if tabeditor is not None:
            self.tabeditor = tabeditor
            self.tabs = tabeditor.tabs
            parent_widget = tabeditor
        else:
            parent_widget = editor

        if terminal is not None:
            self.terminal = terminal

        if pythoneditor is not None:
            self.pythoneditor = pythoneditor

        self.setParent(parent_widget)
        self.create_actions()

    def create_actions(self):
        """
        Find methods on this class that have the
        same names as those registered in the
        json file(s) where actions are stored.
        """
        action_dict = load_actions_from_json()
        for widget_name, widget_actions in action_dict.items():
            if not hasattr(self, widget_name):
                continue
            widget = getattr(self, widget_name)
            if widget is None:
                continue
            for action_name, attributes in widget_actions.items():
                method_name = attributes['Method']
                if not hasattr(self, method_name):
                    print('could not find method %s: %s' % (action_name, method_name))
                    continue
                func = getattr(self, method_name)
                action = make_action(
                    action_name,
                    widget,
                    func
                )

    # -------------------------------------- #
    # ---------------         -------------- #
    # ---------------         -------------- #
    #                execution               #
    # ---------------         -------------- #
    # ---------------         -------------- #
    # -------------------------------------- #
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
        symbol_pos = text_before.rfind('\n#&&')+1 #TODO: is the +1 really necessary?
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

    # -------------------------------------- #
    # ---------------         -------------- #
    # ---------------         -------------- #
    #                text edit               #
    # ---------------         -------------- #
    # ---------------         -------------- #
    # -------------------------------------- #
    def return_handler(self):
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
            self.editor.cut()
            return

        textCursor.select(
            QtGui.QTextCursor.LineUnderCursor
        )
        text = textCursor.selectedText()
        textCursor.insertText('')

        QtGui.QClipboard().setText(text)

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

    def tab_space(self):
        """ Insert spaces instead of tabs """
        self.editor.insertPlainText('    ')

    def toggle_backslashes(self):
        toggle_backslashes(self.editor)

    def duplicate_lines(self):
        """
        Duplicates the current line or
        selected text downwards.
        """
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            if start > end:
                new_end = start
                start = end
                end = new_end
            length = end-start

            cursor.setPosition(
                end,
                QtGui.QTextCursor.MoveAnchor
            )
            cursor.insertText(selected_text)
            cursor.setPosition(
                end,
                QtGui.QTextCursor.MoveAnchor
            )
            cursor.setPosition(
                end+length,
                QtGui.QTextCursor.KeepAnchor
            )
            self.editor.setTextCursor(cursor)
        else:
            cursor.movePosition(
                QtGui.QTextCursor.EndOfLine
            )
            end_pos = cursor.position()
            cursor.movePosition(
                QtGui.QTextCursor.StartOfLine
            )
            cursor.setPosition(
                end_pos,
                QtGui.QTextCursor.KeepAnchor
            )
            selected_text = cursor.selectedText()
            cursor.insertText(
                selected_text+'\n'+selected_text
            )

    def new_line_above(self):
        """
        Inserts new line above current.
        """
        textCursor = self.editor.textCursor()
        line = textCursor.block().text()
        indentCount = len(line)-len(line.lstrip(' '))
        indent = ' '*indentCount
        textCursor.movePosition(
            textCursor.StartOfLine
        )
        self.editor.setTextCursor(textCursor)
        textCursor.insertText(indent+'\n')
        self.editor.moveCursor(textCursor.Left)

    def new_line_below(self):
        """
        Inserts new line below current.
        """
        textCursor = self.editor.textCursor()
        line = textCursor.block().text()
        indentCount = len(line)-len(line.lstrip(' '))
        indent = ' '*indentCount
        textCursor.movePosition(
            textCursor.EndOfLine
        )
        self.editor.setTextCursor(textCursor)
        textCursor.insertText('\n'+indent)

    def delete_to_end_of_line(self):
        """
        Deletes characters from cursor
        position to end of line.
        """
        textCursor = self.editor.textCursor()
        pos = textCursor.position()
        textCursor.movePosition(
            QtGui.QTextCursor.EndOfLine
        )
        textCursor.setPosition(
            pos,
            QtGui.QTextCursor.KeepAnchor
        )
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
            return

        block = textCursor.block()
        text = block.text()
        next_line = block.next().text().strip()
        new_text = text + next_line

        pos = textCursor.position()
        textCursor.select(
            QtGui.QTextCursor.LineUnderCursor
        )
        textCursor.movePosition(
            QtGui.QTextCursor.EndOfLine
        )
        new_pos = textCursor.position()+1
        if new_pos >= self.editor.document().characterCount():
            return
        textCursor.setPosition(
            new_pos,
            QtGui.QTextCursor.KeepAnchor
        )

        textCursor.insertText('')
        textCursor.select(
            QtGui.QTextCursor.LineUnderCursor
        )
        textCursor.insertText(new_text)
        textCursor.setPosition(
            pos,
            QtGui.QTextCursor.MoveAnchor
        )

        self.editor.setTextCursor(textCursor)

    def delete_lines(self):
        """
        Deletes the contents of the current line(s).
        """
        textCursor = self.editor.textCursor()
        start = textCursor.selectionStart()
        end = textCursor.selectionEnd()

        textCursor.setPosition(
            start,
            QtGui.QTextCursor.MoveAnchor
        )
        textCursor.movePosition(
            QtGui.QTextCursor.StartOfLine
        )
        new_start = textCursor.position()

        textCursor.setPosition(
            end,
            QtGui.QTextCursor.MoveAnchor
        )
        textCursor.movePosition(
            QtGui.QTextCursor.EndOfLine
        )

        new_end = textCursor.position()

        textCursor.setPosition(
            new_start,
            QtGui.QTextCursor.KeepAnchor
        )

        if not textCursor.hasSelection():
            textCursor.setPosition(
                start,
                QtGui.QTextCursor.MoveAnchor
            )
            next_line = new_end+1
            doc = self.editor.document()
            num_chars = doc.characterCount()
            if 0 < next_line >= num_chars:
                next_line = next_line-2
                if next_line == -1:
                    return
            textCursor.setPosition(
                next_line,
                QtGui.QTextCursor.KeepAnchor
            )

        textCursor.insertText('')

    def toggle_comment(self):
        """
        Toggles commenting out selected lines,
        or lines with cursor.
        """
        blocks = self.get_selected_blocks()

        # iterate through lines in doc commenting or uncommenting
        # based on whether everything is commented or not
        comment_all_out = any([
            not str(block.text()).lstrip().startswith('#')
            for block in blocks
        ])
        if comment_all_out:
            for block in blocks:
                cursor = QtGui.QTextCursor(block)
                cursor.select(
                    QtGui.QTextCursor.LineUnderCursor
                )
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
                cursor.select(
                    QtGui.QTextCursor.LineUnderCursor
                )
                selectedText = cursor.selectedText()
                newText = str(selectedText).replace('#', '', 1)
                cursor.insertText(newText)

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
        textCursor.setPosition(
            start,
            QtGui.QTextCursor.MoveAnchor
        )
        textCursor.movePosition(QtGui.QTextCursor.StartOfBlock)
        new_start = textCursor.position()

        textCursor.setPosition(
            end,
            QtGui.QTextCursor.MoveAnchor
        )
        textCursor.movePosition(QtGui.QTextCursor.EndOfBlock)

        start_offset = start-new_start

        if new_start == 0:
            return

        textCursor.setPosition(
            new_start,
            QtGui.QTextCursor.KeepAnchor
        )
        selectedText = textCursor.selectedText()

        textCursor.insertText('')
        textCursor.deletePreviousChar()
        textCursor.movePosition(QtGui.QTextCursor.StartOfBlock)
        pos = textCursor.position()
        textCursor.insertText(selectedText+'\n')
        textCursor.setPosition(pos, QtGui.QTextCursor.MoveAnchor)

        if restoreSelection:
            moved_start = textCursor.position()+start_offset
            textCursor.setPosition(
                moved_start,
                QtGui.QTextCursor.MoveAnchor
            )
            moved_end = textCursor.position()+selection_length
            textCursor.setPosition(
                moved_end,
                QtGui.QTextCursor.KeepAnchor
            )
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

    def wrap_text(self):
        """
        Wrap selected text in brackets
        or quotes of type "key".
        """
        key = unicode(self.editor.last_key_pressed)
        key_in, key_out = None, None
        if key in [u'\'', u'"']:
            key_in = key
            key_out = key
        elif key in [u'[', u']']:
            key_in = u'['
            key_out = u']'
        elif key in [u'(', u')']:
            key_in = u'('
            key_out = u')'
        elif key in [u'{', u'}']:
            key_in = u'{'
            key_out = u'}'

        if key_in is None or key_out is None:
            return

        textCursor = self.editor.textCursor()
        if not textCursor.hasSelection():
            textCursor.insertText(key)
            return

        text = key_in + textCursor.selectedText() + key_out
        textCursor.insertText(text)

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

    # -------------------------------------- #
    # ---------------         -------------- #
    # ---------------         -------------- #
    #                selection               #
    # ---------------         -------------- #
    # ---------------         -------------- #
    # -------------------------------------- #
    def duplicate_cursor_down(self):
        """
        Placeholder.
        Duplicate text cursor down.
        """
        pass

    def duplicate_cursor_up(self):
        """
        Placeholder.
        Duplicate text cursor up.
        """
        pass

    def select_lines(self):
        """
        Sets current lines selected
        and moves cursor to beginning
        of next line.
        """
        textCursor = self.editor.textCursor()

        start = textCursor.selectionStart()
        end = textCursor.selectionEnd()

        textCursor.setPosition(
            end,
            QtGui.QTextCursor.MoveAnchor
        )
        textCursor.movePosition(QtGui.QTextCursor.EndOfLine)
        new_end = textCursor.position()+1
        if new_end >= self.editor.document().characterCount():
            new_end = new_end-1

        textCursor.setPosition(
            start,
            QtGui.QTextCursor.MoveAnchor
        )
        textCursor.movePosition(
            QtGui.QTextCursor.StartOfLine
        )

        textCursor.setPosition(
            new_end,
            QtGui.QTextCursor.KeepAnchor
        )
        self.editor.setTextCursor(textCursor)

    def select_word(self):
        """
        Selects the word under cursor if no selection.
        If selection, selects next occurence of the same word.
        TODO: 1) could optionally highlight all occurences of the word
        and iterate to the next selection. 2) Would be nice if extra
        selections could be made editable.
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

        if next_pos != -1:
            next_start = next_pos + start_pos + word_len
        else:
            first_half = whole_text[:start_pos]
            next_start = first_half.find(text)
            if next_start == -1:
                return
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

    def hop_between_brackets(self):
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

        first_pos = first_pos+1
        second_pos = second_pos+pos

        textCursor.setPosition(
            first_pos,
            QtGui.QTextCursor.MoveAnchor
        )
        textCursor.setPosition(
            second_pos,
            QtGui.QTextCursor.KeepAnchor
        )
        self.editor.setTextCursor(textCursor)

    # -------------------------------------- #
    # ---------------         -------------- #
    # ---------------         -------------- #
    #                 utility                #
    # ---------------         -------------- #
    # ---------------         -------------- #
    # -------------------------------------- #

    def copy_block_or_selection(self):
        """
        If there's no text selected,
        copy the current block.
        """
        textCursor = self.editor.textCursor()

        if textCursor.hasSelection():
            self.editor.copy()
            return

        selection = textCursor.selection()
        text = selection.toPlainText()
        if not text:
            textCursor.select(
                QtGui.QTextCursor.BlockUnderCursor
            )
            selection = textCursor.selection()
            text = selection.toPlainText().lstrip()

        QtGui.QClipboard().setText(text)

    def goto_line(self):
        """
        Placeholder.
        Show small lineedit widget allowing
        user to type line to go to. Store current
        line in case user cancels.
        """
        self.goto_palette = GotoPalette(self.editor)
        self.goto_palette.show()

    def command_palette(self):
        """
        Placeholder.
        Show QLineEdit Command Palette allowing
        user to type commands instead of using shortcuts.
        """
        pass

    def show_about(self):
        """
        Placeholder.
        Show splash screen with about window and version
        info for pythoneditor.
        """
        pass

    def open_module_file(self):
        textCursor = self.editor.textCursor()
        text = textCursor.selection().toPlainText()
        if not text.strip():
            return

        obj = get_subobject(text)
        open_module_file(obj)

    def open_module_directory(self):
        textCursor = self.editor.textCursor()
        text = textCursor.selection().toPlainText()
        if not text.strip():
            return

        obj = get_subobject(text)
        open_module_directory(obj)

    def search(self):
        """
        Very basic search dialog.
        """
        textCursor = self.editor.textCursor()
        input_text = ''
        if textCursor.hasSelection():
            input_text = textCursor.selectedText()

        text, ok = QtWidgets.QInputDialog.getText(
            self.editor,
            'Search',
            '',
            QtWidgets.QLineEdit.Normal,
            input_text,
        )
        if not ok:
            return

        def lookup(text, textCursor):
            document = self.editor.document()
            cursor = document.find(text, textCursor)
            pos = cursor.position()
            if pos != -1:
                self.editor.setTextCursor(cursor)
                return True

        # start the search from the current position
        if lookup(text, textCursor):
            return
        # search from the beginning of the document
        textCursor.setPosition(
            0,
            QtGui.QTextCursor.MoveAnchor
        )
        lookup(text, textCursor)

    def reload_package(self):
        widget = self.tabeditor
        while not hasattr(widget, 'reload_package'):
            parent = widget.parent()
            if parent is None:
                return
            widget = parent
        widget.reload_package()

    def print_help(self):
        """
        Prints documentation for selected text if
        it currently represents a python object.
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

    # -------------------------------------- #
    # ---------------         -------------- #
    # ---------------         -------------- #
    #                   tabs                 #
    # ---------------         -------------- #
    # ---------------         -------------- #
    # -------------------------------------- #
    def new_tab(self):
        self.tabs.new_tab()

    def remove_current_tab(self):
        self.tabs.remove_current_tab()

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
            self.tabs.setCurrentIndex(
                self.tabs.currentIndex()-1
            )

    def save(self):
        save_action(self.tabs, self.editor)

    def save_as(self):
        save_as_action(self.tabs, self.editor)

    def open(self):
        open_action(self.tabs, self.editor)

    def clear_output(self):
        if hasattr(self, 'terminal'):
            self.terminal.clear()

    # TODO: move utility methods to functions
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
        blockNumbers |= set([
            doc.findBlock(
            pos).blockNumber()
        ])

        def isEmpty(b):
            return doc.findBlockByNumber(
                b).text().strip() != ''

        blocks = []
        for b in blockNumbers:
            bn = doc.findBlockByNumber(b)
            if not ignoreEmpty:
                blocks.append(bn)
            elif isEmpty(b):
                blocks.append(bn)

        return blocks

    def jump_to_start(self):
        """
        Jump to first character in line.
        If at first character, jump to
        start of line.
        """
        textCursor = self.editor.textCursor()
        init_pos = textCursor.position()
        textCursor.select(
            QtGui.QTextCursor.LineUnderCursor
        )
        text = textCursor.selection().toPlainText()
        textCursor.movePosition(
            QtGui.QTextCursor.StartOfLine
        )
        pos = textCursor.position()
        offset = len(text)-len(text.lstrip())
        new_pos = pos+offset
        if new_pos != init_pos:
            textCursor.setPosition(
                new_pos,
                QtGui.QTextCursor.MoveAnchor
            )
        self.editor.setTextCursor(textCursor)

    def wheel_zoom(self, event):
        """
        Zooms by changing the font size
        according to the wheel zoom delta.
        """
        font = self.editor.font()
        size = font.pointSize()
        d = event.delta()
        amount = int(d/10) if d > 1 or d < -1 else d
        new_size = size + amount
        new_size = new_size if new_size > 0 else 1
        font.setPointSize(new_size)
        self.editor.setFont(font)

    def save_selected_text(self):
        save.save_selected_text(
            self.editor
        )

    def export_selected_to_external_editor(self):
        save.export_selected_to_external_editor(
            self.editor
        )

    def export_current_tab_to_external_editor(self):
        save.export_current_tab_to_external_editor(
            self.tabs,
            self.editor
        )

    def export_all_tabs_to_external_editor(self):
        save.export_all_tabs_to_external_editor(self.tabs)

    def show_shortcuts(self):
        """
        Generates a popup dialog listing available shortcuts.
        """
        self.pythoneditor.shortcuteditor.show()

    def show_preferences(self):
        """
        Generates a popup dialog listing available preferences.
        """
        self.pythoneditor.preferenceseditor.show()

    def show_about_dialog(self):
        """
        Shows an about dialog with version information.
        TODO: Make it a borderless splash screen, centred, nice text,
        major and minor version numbers set in one place in the
        project.
        """
        msg = 'Python Editor version {0} by Max Last'.format(__version__)
        self.about_dialog = QtWidgets.QLabel(msg)
        self.about_dialog.show()


class CommandPalette(QtWidgets.QLineEdit):
    def __init__(self, editor):
        super(CommandPalette, self).__init__()
        self.editor = editor
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.FramelessWindowHint
        )
        self.editingFinished.connect(self.hide)

    def keyPressEvent(self, event):
        esc = QtCore.Qt.Key.Key_Escape
        if event.key() == esc:
            self.hide()
        super(
            CommandPalette, self
            ).keyPressEvent(event)

    def showEvent(self, event):
        self.editor.installEventFilter(self)
        self.setFocus(QtCore.Qt.MouseFocusReason)
        super(CommandPalette, self).showEvent(event)
        self.match_editor_size()

    def hideEvent(self, event):
        self.editor.removeEventFilter(self)
        super(CommandPalette, self).hideEvent(event)

    def match_editor_size(self):
        geo = self.editor.geometry()
        centre = geo.center()
        x = centre.x()-(self.width()/2)
        y = geo.top()-12
        pos = QtCore.QPoint(x, y)
        pos = self.editor.mapToGlobal(pos)
        self.move(pos)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Move:
            self.match_editor_size()
        elif event.type() == QtCore.QEvent.Resize:
            self.match_editor_size()
        elif event.type() == QtCore.QEvent.Hide:
            self.hide()
        return False


class GotoPalette(CommandPalette):
    def __init__(self, editor):
        super(GotoPalette, self).__init__(editor)
        self.editor = editor
        self.current_line = editor.textCursor(
            ).block(
            ).blockNumber()+1
        self.match_editor_size()

    def keyPressEvent(self, event):
        esc = QtCore.Qt.Key.Key_Escape
        if event.key() == esc:
            self.goto_line(self.current_line)
            self.hide()

        if event.text().isalpha():
            return

        super(
            GotoPalette, self
            ).keyPressEvent(event)
        try:
            lineno = int(self.text())
        except ValueError:
            return
        self.goto_line(lineno)

    def goto_line(self, lineno):
        """
        Sets the text cursor of the editor
        to the given lineno.
        """
        editor = self.editor
        count = editor.blockCount()
        if lineno > count:
            lineno = count
        lineno = lineno-1
        pos = editor.document(
            ).findBlockByNumber(
            lineno).position()

        cursor = editor.textCursor()
        cursor.setPosition(pos)
        editor.setTextCursor(cursor)


def make_action(name, widget, func):
    """
    Add action to widget with
    given triggered function.

    :action: QtWidgets.QAction
    :widget: QtWidgets.QWidget
    :func: a callable that gets executed
           when triggering the action.
    """
    action = QtWidgets.QAction(widget)
    action.triggered.connect(func)
    widget.addAction(action)
    action.setText(name)
    action.setToolTip(func.__doc__)
    return action


def toggle_backslashes_in_string(text):
    if '\\' in text:
        text = text.replace('\\\\', '/')
        text = text.replace('\\', '/')
    elif '/' in text:
        text = text.replace('/', '\\\\')
    return text


def toggle_backslashes(editor):
    textCursor = editor.textCursor()
    if not textCursor.hasSelection():
        textCursor.select(QtGui.QTextCursor.BlockUnderCursor)

    selection = textCursor.selection()
    text = selection.toPlainText()

    if not text:
        return

    edited_text = toggle_backslashes_in_string(text)
    if edited_text == text:
        return

    textCursor.insertText(edited_text)


def save_action(tabs, editor):
    """
    """
    path = tabs.get('path')
    text = editor.toPlainText()
    path = save.save(text, path)
    if path is None:
        return
    tabs['path'] = path
    tabs['saved'] = True
    # notify the autosave to empty entry
    tabs.contents_saved_signal.emit(tabs['uuid'])


def save_as_action(tabs, editor):
    """
    """
    text = editor.toPlainText()
    path = save.save_as(text)
    if path is None:
        return
    tabs['path'] = path
    tabs['saved'] = True

    name = os.path.basename(path)
    tabs['name'] = name
    index = tabs.currentIndex()
    tabs.setTabText(index, name)

    # notify the autosave to empty entry
    tabs.contents_saved_signal.emit(tabs['uuid'])


def open_action(tabs, editor, path=''):
    """
    Simple open file.
    :tabs: TabBar
    :editor: Editor
    :path: optional path to file.
    """
    if not path:
        o = QtWidgets.QFileDialog.getOpenFileName
        path, _ = o(tabs, "Open File")
        if not path:
            return
    elif not os.path.isfile(path):
        return

    with open(path, 'rt') as f:
        text = f.read()

    for index in range(tabs.count()):
        data = tabs.tabData(index)
        if data is None:
            continue

        if data.get('path') != path:
            continue

        # try to avoid more costly 2nd comparison
        if data.get('text') == text:
            tabs.setCurrentIndex(index)
            return

    tab_name = os.path.basename(path)

    # Because the document will be open in read-only mode, the
    # autosave should not save the editor's contents until the
    # contents have been modified.
    uid = str(uuid.uuid4())
    data = {
        'uuid'  : uid,
        'name'  : tab_name,
        'text'  : '',
        'path'  : path,
        'date'  : '', # need the file's date
        'saved' : True, # read-only
    }

    tabs.new_tab(tab_name=tab_name, tab_data=data)
    editor.setPlainText(text)

    # emit a signal to trigger autosave.
    # we want the file's contents to be loaded
    # into the autosave in case the file is moved.
    tabs.contents_saved_signal.emit(uid)

def get_subobject(text):
    """
    Walk down an object's hierarchy to retrieve
    the object at the end of the chain.
    """
    text = text.strip()
    if '.' not in text:
        return __main__.__dict__.get(text)

    name = text.split('.')[0]
    obj = __main__.__dict__.get(name)
    if obj is None:
        return

    for name in text.split('.')[1:]:
        obj = getattr(obj, name)
        if obj is None:
            return
    return obj


def open_module_file(obj):
    try:
        file = inspect.getfile(obj)
    except TypeError as e:
        if hasattr(obj, '__class__'):
            obj = obj.__class__
            file = inspect.getfile(obj)
        else:
            raise

    if file.endswith('.pyc'):
        file = file.replace('.pyc', '.py')

    try:
        lines, lineno = inspect.getsourcelines(obj)
        file = file+':'+str(lineno)
    except AttributeError, IOError:
        pass

    print(file)

    #TODO: this is a horrible hack to avoid circular imports
    from PythonEditor.ui.features.autosavexml import get_external_editor_path

    EXTERNAL_EDITOR_PATH = get_external_editor_path()
    if (EXTERNAL_EDITOR_PATH
            and os.path.isdir(os.path.dirname(EXTERNAL_EDITOR_PATH))):
        subprocess.Popen([EXTERNAL_EDITOR_PATH, file])


def open_module_directory(obj):
    file = inspect.getfile(obj).replace('.pyc', '.py')
    folder = os.path.dirname(file)
    print(folder)

    #TODO: this is a horrible hack to avoid circular imports
    from PythonEditor.ui.features.autosavexml import get_external_editor_path

    EXTERNAL_EDITOR_PATH = get_external_editor_path()
    if (EXTERNAL_EDITOR_PATH
            and os.path.isdir(os.path.dirname(EXTERNAL_EDITOR_PATH))):
        subprocess.Popen([EXTERNAL_EDITOR_PATH, folder])


def openDir(module):
    try:
        print(bytes(module.__file__))
        subprocess.Popen(['nautilus', module.__file__])
    except AttributeError:
        file = inspect.getfile(module)
        subprocess.Popen(['nautilus', file])
    print('sublime ', __file__, ':', sys._getframe().f_lineno, sep='')  # TODO: nautilus is not multiplatform!


def find_menu_item(menu, item_name=''):
    for item in menu.children():
        if hasattr(item, 'text'):
            name = item.text()
        elif hasattr(item, 'title'):
            name = item.title()
        else:
            continue
        if str(name) == str(item_name):
            return item


# tests

TEST_TEXT = """
c:\\path/to\\some\\file.jpg
"""

EXPECTED_RESULT = """
c:/path/to/some/file.jpg
"""

if __name__ == '__main__':
    assert toggle_backslashes_in_string(TEST_TEXT) == EXPECTED_RESULT

    def test_toggle_backslashes():
        editor = QtWidgets.QPlainTextEdit()
        test_toggle_backslashes.editor = editor
        editor.setPlainText(TEST_TEXT)
        editor.show()
        textCursor = editor.textCursor()
        textCursor.setPosition(0, QtGui.QTextCursor.MoveAnchor)
        editor.setTextCursor(textCursor)
        toggle_backslashes(editor)

"""
TEST_TEXT = toggle_backslashes_in_string(TEST_TEXT)
print TEST_TEXT
test_toggle_backslashes()
"""
