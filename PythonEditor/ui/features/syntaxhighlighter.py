from PythonEditor.ui.Qt import QtGui, QtCore

themes = {
  'Monokai': {
            'keyword': ((249, 38, 114), ''),
            'args': ((249, 38, 114), ''),
            'kwargs': ((249, 38, 114), ''),
            'string': ((230, 219, 116), ''),
            'comment': ((140, 140, 140), ''),
            'numbers': ((174, 129, 255), ''),
            'inherited': ((102, 217, 239), 'italic'),
            'class_names': ((166, 226, 46), ''),
            'function_names': ((166, 226, 46), ''),
            'arguments': ((253, 151, 31), ''),
            'formatters': ((114, 209, 221), 'italic'),
            'instantiators': ((102, 217, 239), 'italic'),
            'exceptions': ((102, 217, 239), 'italic'),
            'methods': ((102, 217, 239), ''),
            },
  'Monokai Smooth': {
            'keyword': ((255, 97, 136), ''),
            'args': ((255, 97, 136), ''),
            'kwargs': ((255, 97, 136), ''),
            'string': ((255, 216, 102), ''),
            'comment': ((108, 106, 108), 'italic'),
            'numbers': ((171, 157, 242), ''),
            'inherited': ((114, 209, 221), 'italic'),
            'class_names': ((250, 250, 248), ''),
            'function_names': ((169, 220, 118), ''),
            'arguments': ((193, 192, 192), 'italic'),
            'formatters': ((114, 209, 221), 'italic'),
            'instantiators': ((114, 209, 221), 'italic'),
            'exceptions': ((114, 209, 221), 'italic'),
            'methods': ((169, 220, 101), ''),
            }
}


class Highlight(QtGui.QSyntaxHighlighter):
    """
    Modified, simplified version of some code
    that Wouter Gilsing found and modified when researching.
    wiki.python.org/moin/PyQt/Python%20syntax%20highlighting
    """

    def __init__(self, document):
        super(Highlight, self).__init__(document)

        self.setObjectName('Highlight')

        theme = themes['Monokai Smooth']
        # theme = themes['Monokai']
        self.styles = {feature: self.format(*style)
                       for feature, style in theme.items()}

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
        self.keywords.extend(dir(__builtins__))

        self.instantiators = [
            'def', 'class'
            ]

        self.exceptions = ['BaseException',
                           'SystemExit',
                           'KeyboardInterrupt',
                           'GeneratorExit',
                           'Exception',
                           'StopIteration',
                           'StandardError',
                           'BufferError',
                           'ArithmeticError',
                           'FloatingPointError',
                           'OverflowError',
                           'ZeroDivisionError',
                           'AssertionError',
                           'AttributeError',
                           'EnvironmentError',
                           'IOError',
                           'OSError',
                           'WindowsError',
                           'VMSError',
                           'EOFError',
                           'ImportError',
                           'LookupError',
                           'IndexError',
                           'KeyError',
                           'MemoryError',
                           'NameError',
                           'UnboundLocalError',
                           'ReferenceError',
                           'RuntimeError',
                           'NotImplementedError',
                           'SyntaxError',
                           'IndentationError',
                           'TabError',
                           'SystemError',
                           'TypeError',
                           'ValueError',
                           'UnicodeError',
                           'UnicodeDecodeError',
                           'UnicodeEncodeError',
                           'UnicodeTranslateError',
                           'Warning',
                           'DeprecationWarning',
                           'PendingDeprecationWarning',
                           'RuntimeWarning',
                           'SyntaxWarning',
                           'UserWarning',
                           'FutureWarning',
                           'ImportWarning',
                           'UnicodeWarning',
                           'BytesWarning']

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

        # function args/kwargs TODO: find correct regex pattern for separate
        # args and kwargs (words) between parentheses
        # rules += [('(?:def \w+\()([^)]+)', 1, self.styles['args'])]

        class_regex = '(?:class \w+\()([a-zA-Z\.]+)(?:\))'
        rules += [(class_regex, 1, self.styles['inherited'])]
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
        rules += [(r'\b%s\b' % i, 0, self.styles['exceptions'])
                  for i in self.exceptions]

        rules += [
            # function names
            ('(?:def |)(\w+)(?:\()', 1, self.styles['function_names']),
            # class names
            ('(?:class )(\w+)(?:\()', 1, self.styles['class_names']),
            # methods
            ('(?:\.)([a-zA-Z\.]+)(?:\()', 1, self.styles['methods']),
            # decorators
            ('(?:@)(\w+)', 1, self.styles['function_names']),
            # string formatters
            (r'([rfb])(?:\'|\")', 0, self.styles['formatters']),
            # integers
            (r'\b[0-9]+\b', 0, self.styles['numbers']),
            # From # until a newline or end of a double quote
            (r'#[^\n\'\"]*', 0, self.styles['comment']),
            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, self.styles['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, self.styles['string']),
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
