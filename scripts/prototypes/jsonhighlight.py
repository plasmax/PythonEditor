from Qt.QtGui import QSyntaxHighlighter, QColor


PURPLE = QColor.fromRgbF(0.7, 0.5, 1, 1)
BLUE = QColor.fromRgbF(0, 0.5, 1, 1)


class JSONHighlighter(QSyntaxHighlighter):
    def highlightBlock(self, s):
        if not s.strip():
            return
        i = 0
        for start, length in get_string_ranges(s):
            if i % 2:
                color = BLUE
            else:
                color = PURPLE
            i += 1
            self.setFormat(start, length, color)


def get_string_ranges(t):
    """Get the in and out points of double-quote encased strings."""

    # life's too short to parse escape characters.
    s = t.replace('\\"', '##')
    assert len(s) == len(t)

    i = 0
    prev_c = ''
    in_str = False
    length = 0
    for i in range(len(s)):
        c = s[i]

        if in_str:
            length += 1

        if c == '\"':
            if in_str:
                # we've reached the end of the string
                in_str = False
                yield i-length+1, length-1
                length = 0
            else:
                in_str = True

        prev_c = c
        i += 1
