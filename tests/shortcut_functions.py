import imp
import __main__


qt_path = 'C:/Repositories/PythonEditor/PythonEditor/ui/Qt.py'
exec_path = 'C:/Repositories/PythonEditor/PythonEditor/core/execute.py'

Qt = imp.load_source('Qt', qt_path)
execute = imp.load_source('execute', exec_path)

QtWidgets, QtGui, QtCore = Qt.QtWidgets, Qt.QtGui, Qt.QtCore


def get_selected_blocks(code_edit, ignoreEmpty=True):
    """
    Utility method for getting lines in selection.
    """
    textCursor = code_edit.textCursor()
    doc = code_edit.document()
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


def offset_for_traceback(code_edit, text=None):
    """
    Offset text using newlines to get proper line ref in tracebacks.
    """
    textCursor = code_edit.textCursor()

    if text is None:
        text = textCursor.selection().toPlainText()

    selection_offset = textCursor.selectionStart()
    doc = code_edit.document()
    block_num = doc.findBlock(selection_offset).blockNumber()
    text = '\n' * block_num + text
    return text


def exec_selected_text(code_edit):
    """
    Calls exec with either selected text
    or all the text in the edit widget.
    TODO: in some instances, this can still have the wrong
    line number in tracebacks! Frustratingly, it seems to
    disappear after a normal execution (full text) run.
    """
    textCursor = code_edit.textCursor()

    whole_text = code_edit.toPlainText()

    if textCursor.hasSelection():
        text = offset_for_traceback(code_edit)
    else:
        text = whole_text

    # exec_text_signal.emit()
    whole_text = '\n'+whole_text
    error_line_numbers = execute.mainexec(text, whole_text)
    if error_line_numbers is None:
        return
    else:
        highlight_errored_lines(code_edit, error_line_numbers)


def exec_current_line(code_edit):
    """
    Calls exec with the text of the line the cursor is on.
    Calls lstrip on current line text to allow exec of indented text.
    """
    textCursor = code_edit.textCursor()
    whole_text = code_edit.toPlainText()

    if textCursor.hasSelection():
        return exec_selected_text()

    textCursor.select(QtGui.QTextCursor.LineUnderCursor)
    text = textCursor.selection().toPlainText().lstrip()
    text = offset_for_traceback(code_edit, text=text)

    whole_text = '\n'+whole_text
    error_line_numbers = execute.mainexec(text, whole_text)
    if error_line_numbers is None:
        return
    else:
        highlight_errored_lines(code_edit, error_line_numbers)


def highlight_errored_lines(code_edit, error_line_numbers):
    """
    Draw a red background on any lines that caused an error.
    """
    extraSelections = []

    cursor = code_edit.textCursor()
    doc = code_edit.document()
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
    code_edit.setExtraSelections(extraSelections)


@QtCore.Slot(QtGui.QKeyEvent)
def return_handler(code_edit):
    """
    New line with auto-indentation.
    """
    return indent_next_line(code_edit)


def indent_next_line(code_edit):
    """
    Match next line indentation to current line
    If ':' is character in cursor position and
    current line contains non-whitespace
    characters, add an extra four spaces.
    """
    textCursor = code_edit.textCursor()
    line = textCursor.block().text()
    indentCount = len(str(line)) - len(str(line).lstrip(' '))

    doc = code_edit.document()
    if doc.characterAt(textCursor.position()-1) == ':':
        indentCount = indentCount + 4

    insertion = '\n'+' '*indentCount
    if len(line.strip()) == 0:
        insertion = '\n'

    if not getattr(code_edit, 'wait_for_autocomplete', False):
        textCursor.insertText(insertion)
        code_edit.setTextCursor(textCursor)


@QtCore.Slot()
def cut_line(code_edit):
    """
    If no text selected, cut whole
    current line to clipboard.
    """
    textCursor = code_edit.textCursor()
    if textCursor.hasSelection():
        return

    textCursor.select(QtGui.QTextCursor.LineUnderCursor)
    text = textCursor.selectedText()
    textCursor.insertText('')

    QtGui.QClipboard().setText(text)


def new_line_above(code_edit):
    """
    Inserts new line above current.
    """
    textCursor = code_edit.textCursor()
    line = textCursor.block().text()
    indentCount = len(line) - len(line.lstrip(' '))
    indent = ' '*indentCount
    textCursor.movePosition(textCursor.StartOfLine)
    code_edit.setTextCursor(textCursor)
    textCursor.insertText(indent+'\n')
    code_edit.moveCursor(textCursor.Left)


def new_line_below(code_edit):
    """
    Inserts new line below current.
    """
    textCursor = code_edit.textCursor()
    line = textCursor.block().text()
    indentCount = len(line) - len(line.lstrip(' '))
    indent = ' '*indentCount
    textCursor.movePosition(textCursor.EndOfLine)
    code_edit.setTextCursor(textCursor)
    textCursor.insertText('\n'+indent)


@QtCore.Slot()
def tab_handler(code_edit):
    """
    Indents selected text. If no text
    is selected, adds four spaces.
    """
    textCursor = code_edit.textCursor()
    if textCursor.hasSelection():
        indent()
    else:
        tab_space()


def indent(code_edit):
    """
    Indent Selected Text
    """
    blocks = get_selected_blocks(code_edit)
    for block in blocks:
        cursor = QtGui.QTextCursor(block)
        cursor.movePosition(QtGui.QTextCursor.StartOfLine)
        cursor.insertText('    ')


def unindent(code_edit):
    """
    Unindent Selected Text
    TODO: Maintain original selection
    and cursor position.
    """
    blocks = get_selected_blocks(code_edit, ignoreEmpty=False)
    for block in blocks:
        cursor = QtGui.QTextCursor(block)
        cursor.select(QtGui.QTextCursor.LineUnderCursor)
        lineText = cursor.selectedText()
        if lineText.startswith(' '):
            newText = str(lineText[:4]).replace(' ', '') + lineText[4:]
            cursor.insertText(newText)


def tab_space(code_edit):
    """ Insert spaces instead of tabs """
    code_edit.insertPlainText('    ')


def next_tab(tabs):
    next_index = tabs.currentIndex()+1
    if tabs.widget(next_index).objectName() == 'Editor':
        tabs.setCurrentIndex(next_index)


def previous_tab(tabs):
    tabs.setCurrentIndex(tabs.currentIndex()-1)


def jump_to_start(code_edit):
    """
    Jump to first character in line.
    If at first character, jump to
    start of line.
    """
    textCursor = code_edit.textCursor()
    init_pos = textCursor.position()
    textCursor.select(QtGui.QTextCursor.LineUnderCursor)
    text = textCursor.selection().toPlainText()
    textCursor.movePosition(QtGui.QTextCursor.StartOfLine)
    pos = textCursor.position()
    offset = len(text)-len(text.lstrip())
    new_pos = pos+offset
    if new_pos != init_pos:
        textCursor.setPosition(new_pos, QtGui.QTextCursor.MoveAnchor)
    code_edit.setTextCursor(textCursor)


def comment_toggle(code_edit):
    """
    Toggles commenting out selected lines,
    or lines with cursor.
    """
    blocks = get_selected_blocks(code_edit)

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


key_lookup = {
    "'": ("'", "'"),
    '"': ('"', '"'),
    '[': ('[', ']'),
    ']': ('[', ']'),
    '(': ('(', ')'),
    ')': ('(', ')'),
    '{': ('{', '}'),
    '}': ('{', '}'),
    '<': ('<', '>'),
    '>': ('<', '>'),
}


@QtCore.Slot(str)
def wrap_text(code_edit, key):
    """
    Wrap selected text in brackets
    or quotes of type "key".
    """
    try:
        key_in, key_out = key_lookup[key]
    except KeyError:
        return

    # if key in ['\'', '"']:
    #     key_in = key
    #     key_out = key
    # elif key in ['[', ']']:
    #     key_in = '['
    #     key_out = ']'
    # elif key in ['(', ')']:
    #     key_in = '('
    #     key_out = ')'
    # elif key in ['{', '}']:
    #     key_in = '{'
    #     key_out = '}'
    # elif key in ['<', '>']:
    #     key_in = '<'
    #     key_out = '>'
    # else:
    #     return

    textCursor = code_edit.textCursor()

    text = textCursor.selectedText()
    if text:
        print text
        text = key_in + text + key_out
    else:
        text = key
    textCursor.insertText(text)


def select_lines(code_edit):
    """
    Sets current lines selected
    and moves cursor to beginning
    of next line.
    """
    textCursor = code_edit.textCursor()

    start = textCursor.selectionStart()
    end = textCursor.selectionEnd()

    textCursor.setPosition(end, QtGui.QTextCursor.MoveAnchor)
    textCursor.movePosition(QtGui.QTextCursor.EndOfLine)
    new_end = textCursor.position()+1
    if new_end >= code_edit.document().characterCount():
        new_end = new_end-1

    textCursor.setPosition(start, QtGui.QTextCursor.MoveAnchor)
    textCursor.movePosition(QtGui.QTextCursor.StartOfLine)

    textCursor.setPosition(new_end, QtGui.QTextCursor.KeepAnchor)
    code_edit.setTextCursor(textCursor)


def join_lines(code_edit):
    """
    Joins current line(s) with next by deleting the
    newline at the end of the current line(s).
    """
    textCursor = code_edit.textCursor()

    blocks = get_selected_blocks(code_edit, ignoreEmpty=False)
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
        if new_pos >= code_edit.document().characterCount():
            return
        textCursor.setPosition(new_pos, QtGui.QTextCursor.KeepAnchor)

        textCursor.insertText('')
        textCursor.select(QtGui.QTextCursor.LineUnderCursor)
        textCursor.insertText(new_text)

        code_edit.setTextCursor(textCursor)


def delete_lines(code_edit):
    """
    Deletes the contents of the current line(s).
    """
    textCursor = code_edit.textCursor()

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
        if 0 < next_line >= code_edit.document().characterCount():
            next_line = next_line-2
            if next_line == -1:
                return
        textCursor.setPosition(next_line, QtGui.QTextCursor.KeepAnchor)

    textCursor.insertText('')


def select_word(code_edit):
    """
    Selects the word under cursor if no selection.
    If selection, selects next occurence of the same word.
    TODO: 1 )could optionally highlight all occurences of the word
    and iterate to the next selection. 2) Would be nice if extra
    selections could be made editable. 3) Wrap around.
    """
    textCursor = code_edit.textCursor()
    if not textCursor.hasSelection():
        textCursor.select(QtGui.QTextCursor.WordUnderCursor)
        return code_edit.setTextCursor(textCursor)

    text = textCursor.selection().toPlainText()
    start_pos = textCursor.selectionStart()
    end_pos = textCursor.selectionEnd()
    word_len = abs(end_pos - start_pos)

    whole_text = code_edit.toPlainText()
    second_half = whole_text[end_pos:]
    next_pos = second_half.find(text)

    if next_pos == -1:
        return

    next_start = next_pos + start_pos + word_len
    next_end = next_start + word_len

    textCursor.setPosition(next_start, QtGui.QTextCursor.MoveAnchor)
    textCursor.setPosition(next_end, QtGui.QTextCursor.KeepAnchor)
    code_edit.setTextCursor(textCursor)

    extraSelections = []

    selection = QtWidgets.QTextEdit.ExtraSelection()

    lineColor = QtGui.QColor.fromRgbF(1, 1, 1, 0.3)
    selection.format.setBackground(lineColor)
    selection.cursor = code_edit.textCursor()
    selection.cursor.setPosition(start_pos, QtGui.QTextCursor.MoveAnchor)
    selection.cursor.setPosition(end_pos, QtGui.QTextCursor.KeepAnchor)
    extraSelections.append(selection)
    code_edit.setExtraSelections(extraSelections)


def hop_brackets(code_edit):
    """
    Jump to closest bracket, starting
    with closing bracket.
    """
    textCursor = code_edit.textCursor()
    pos = textCursor.position()
    whole_text = code_edit.toPlainText()

    first_half = whole_text[:pos]
    second_half = whole_text[pos:]
    first_pos = first_half.rfind('(')
    second_pos = second_half.find(')')

    first_pos = first_pos + 1
    second_pos = second_pos + pos

    new_pos = first_pos if whole_text[pos] == ')' else second_pos
    textCursor.setPosition(new_pos, QtGui.QTextCursor.MoveAnchor)
    code_edit.setTextCursor(textCursor)


def select_between_brackets(code_edit):
    """
    Selects text between [] {} ()
    TODO: implement [] and {}
    """
    textCursor = code_edit.textCursor()
    pos = textCursor.position()
    whole_text = code_edit.toPlainText()

    first_half = whole_text[:pos]
    second_half = whole_text[pos:]
    first_pos = first_half.rfind('(')
    second_pos = second_half.find(')')

    first_pos = first_pos + 1
    second_pos = second_pos + pos

    textCursor.setPosition(first_pos, QtGui.QTextCursor.MoveAnchor)
    textCursor.setPosition(second_pos, QtGui.QTextCursor.KeepAnchor)
    code_edit.setTextCursor(textCursor)


def search_input(code_edit):
    """
    Very basic search dialog.
    TODO: Create a QAction/util for this
    as it is also accessed through
    the right-click menu.
    """
    dialog = QtWidgets.QInputDialog.getText(code_edit,
                                            'Search', '',)
    text, ok = dialog
    if not ok:
        return

    textCursor = code_edit.textCursor()
    document = code_edit.document()
    cursor = document.find(text, textCursor)
    pos = cursor.position()
    code_edit.setTextCursor(cursor)


def duplicate_lines(code_edit):
    """
    Duplicates the current line or
    selected text downwards.
    """
    textCursor = code_edit.textCursor()
    if textCursor.hasSelection():
        selected_text = textCursor.selectedText()
        for i in range(2):
            textCursor.insertText(selected_text)
            code_edit.setTextCursor(textCursor)
    else:
        textCursor.movePosition(QtGui.QTextCursor.EndOfLine)
        end_pos = textCursor.position()
        textCursor.movePosition(QtGui.QTextCursor.StartOfLine)
        textCursor.setPosition(end_pos, QtGui.QTextCursor.KeepAnchor)
        selected_text = textCursor.selectedText()
        textCursor.insertText(selected_text+'\n'+selected_text)


def delete_to_end_of_line(code_edit):
    """
    Deletes characters from cursor
    position to end of line.
    """
    textCursor = code_edit.textCursor()
    pos = textCursor.position()
    textCursor.movePosition(QtGui.QTextCursor.EndOfLine)
    textCursor.setPosition(pos, QtGui.QTextCursor.KeepAnchor)
    textCursor.insertText('')


def delete_to_start_of_line(code_edit):
    """
    Deletes characters from cursor
    position to start of line.
    """
    textCursor = code_edit.textCursor()
    pos = textCursor.position()
    textCursor.movePosition(QtGui.QTextCursor.StartOfLine)
    textCursor.setPosition(pos, QtGui.QTextCursor.KeepAnchor)
    textCursor.insertText('')


def print_help(code_edit):
    """
    Prints documentation
    for selected object
    """
    text = code_edit.textCursor().selectedText()
    obj = __main__.__dict__.get(text)
    if obj is not None:
        print(obj.__doc__)
    else:
        exec('help('+text+')', __main__.__dict__)


def print_type(code_edit):
    """
    Prints type
    for selected object
    """
    text = code_edit.textCursor().selectedText()
    obj = __main__.__dict__.get(text)
    if obj is not None:
        print(type(obj))
    else:
        exec('print(type('+text+'))', __main__.__dict__)


def zoom_in(code_edit):
    """
    Zooms in by changing the font size.
    """
    font = code_edit.font()
    size = font.pointSize()
    new_size = size + 1
    font.setPointSize(new_size)
    code_edit.setFont(font)


def zoom_out(code_edit):
    """
    Zooms out by changing the font size.
    """
    font = code_edit.font()
    size = font.pointSize()
    new_size = size - 1 if size > 1 else 1
    font.setPointSize(new_size)
    code_edit.setFont(font)


def wheel_zoom(code_edit, event):
    """
    Zooms by changing the font size
    according to the wheel zoom delta.
    """
    font = code_edit.font()
    size = font.pointSize()
    delta = event.delta()
    amount = int(delta/10) if delta > 1 or delta < -1 else delta
    new_size = size + amount
    new_size = new_size if new_size > 0 else 1
    font.setPointSize(new_size)
    code_edit.setFont(font)


def move_lines_up(code_edit):
    """
    Moves current lines upwards.
    TODO: Bug fix! Doesn't work with wrapped
    text (presumably needs correct block)
    """
    restoreSelection = False
    textCursor = code_edit.textCursor()
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

    code_edit.setTextCursor(textCursor)


def move_lines_down(code_edit):
    """
    Moves current lines downwards.
    TODO: Bug fix! Doesn't work with wrapped
    text (presumably needs correct block)
    """
    restoreSelection = False

    textCursor = code_edit.textCursor()
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

    if new_end + 1 >= code_edit.document().characterCount():
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

    code_edit.setTextCursor(textCursor)


def move_to_top(code_edit):
    """
    Move selection or line if no
    selection to top of document.
    """
    textCursor = code_edit.textCursor()
    if not textCursor.hasSelection():
        textCursor.select(QtGui.QTextCursor.LineUnderCursor)
    text = textCursor.selectedText()
    textCursor.insertText('')
    textCursor.setPosition(0, QtGui.QTextCursor.MoveAnchor)
    textCursor.insertText(text)
    code_edit.setTextCursor(textCursor)


def move_to_bottom(code_edit):
    """
    Move selection or line if no
    selection to bottom of document.
    """
    textCursor = code_edit.textCursor()
    if not textCursor.hasSelection():
        textCursor.select(QtGui.QTextCursor.LineUnderCursor)
    text = textCursor.selectedText()
    textCursor.insertText('')
    end = len(code_edit.toPlainText())
    textCursor.setPosition(end, QtGui.QTextCursor.MoveAnchor)
    textCursor.insertText(text)
    code_edit.setTextCursor(textCursor)
