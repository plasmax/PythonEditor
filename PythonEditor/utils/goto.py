


def goto_position(editor, pos):
    """
    Goto position in document. 
    """
    cursor = editor.textCursor()
    editor.moveCursor(cursor.End)
    cursor.setPosition(pos)
    editor.setTextCursor(cursor)

def goto_line(editor, lineno, scroll=False):
    """
    Sets the text cursor to the
    end of the document, then to
    the given lineno.
    """
    count = editor.blockCount()
    if lineno > count:
        lineno = count
    lineno = lineno-1
    pos = editor.document(
        ).findBlockByNumber(
        lineno).position()

    goto_position(editor, pos)
    
    if scroll:
        bar = editor.verticalScrollBar()
        bar.setValue(max(0, bar.value()-2))