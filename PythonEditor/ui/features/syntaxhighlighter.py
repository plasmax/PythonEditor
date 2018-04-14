from PythonEditor.ui.Qt import QtGui, QtCore

class Highlight(QtGui.QSyntaxHighlighter):
    """
    Modified, simplified version of some code found I found when researching:
    wiki.python.org/moin/PyQt/Python%20syntax%20highlighting
    They did an awesome job, so credits to them. I only needed to make some
    modifications to make it fit my needs.
    """

    def __init__(self, document):

        super(Highlight, self).__init__(document)
        self.setObjectName('Highlight')

        self.styles = {
            'keyword': self.format([249, 38, 114]),
            'string': self.format([230, 219, 116]),
            'comment': self.format([140, 140, 140]),
            'numbers': self.format([174, 129, 255]),
            'names': self.format([166, 226, 46]),
            'arguments': self.format([253, 151, 31]),
            'instantiators': self.format([102, 217, 239]),
            }

        self.arguments = [
            'self', 'cls', 'args', 'kwargs'
            ]

        self.keywords = [
            'and', 'assert', 'break', 'continue',
            'del', 'elif', 'else', 'except', 'exec', 'finally',
            'for', 'from', 'global', 'if', 'import', 'in',
            'is', 'lambda', 'not', 'or', 'pass', 'print',
            'raise', 'return', 'try', 'while', 'yield', 'with'
            ]

        self.instantiators = [
            'def', 'class'
            ]

        self.operatorKeywords = [
            '=', '==', '!=', '<', '<=', '>', '>=',
            '\+', '-', '\*', '/', '//', '\%', '\*\*',
            '\+=', '-=', '\*=', '/=', '\%=',
            '\^', '\|', '\&', '\~', '>>', '<<',
            ]

        self.numbers = ['True', 'False', 'None']

        self.tri_single = (QtCore.QRegExp("'''"), 1, self.styles['comment'])
        self.tri_double = (QtCore.QRegExp('"""'), 2, self.styles['comment'])

        # rules
        rules = []

        rules += [('(?: \()(\w+)(?:\))', 1, self.styles['names'])]
        rules += [(r'\b%s\b' % i, 0, self.styles['arguments'])
                  for i in self.arguments]
        rules += [(r'\b%s\b' % i, 0, self.styles['keyword'])
                  for i in self.keywords]
        rules += [(i, 0, self.styles['keyword'])
                  for i in self.operatorKeywords]
        rules += [(r'\b%s\b' % i, 0, self.styles['numbers'])
                  for i in self.numbers]
        rules += [(r'\b%s\b' % i, 0, self.styles['instantiators'])
                  for i in self.instantiators]

        rules += [

            # integers
            (r'\b[0-9]+\b', 0, self.styles['numbers']),
            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, self.styles['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, self.styles['string']),
            # class and function names
            ('(?:def |class )(\w+)(?:\()', 1, self.styles['names']),
            # methods
            ('(?:\.)(\w+)(?:\()', 1, self.styles['instantiators']),
            # From '#' until a newline
            (r'#[^\n]*', 0, self.styles['comment']),
            ]

        # Build a QRegExp for each pattern
        self.rules = [(QtCore.QRegExp(pat), index, fmt)
                      for (pat, index, fmt) in rules]

    def format(self, rgb, style=''):
        """
        Return a QtGui.QTextCharFormat with the given attributes.
        """

        color = QtGui.QColor(*rgb)
        textFormat = QtGui.QTextCharFormat()
        textFormat.setForeground(color)

        if 'bold' in style:
            textFormat.setFontWeight(QtGui.QFont.Bold)
        if 'italic' in style:
            textFormat.setFontItalic(True)

        return textFormat

    def highlightBlock(self, text):
        """
        Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.tri_double)

    def match_multiline(self, text, delimiter, in_state, style):
        """
        Check whether highlighting requires multiple lines.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False
