from __future__ import print_function
import __main__
import sys
import re
import keyword
import inspect
import os
import json

from PythonEditor.ui.Qt import QtGui
from PythonEditor.ui.Qt import QtCore
from PythonEditor.ui.Qt import QtWidgets
from PythonEditor.utils.debug import debug
from PythonEditor.utils.constants import NUKE_DIR


KEYWORDS = [
    'True',
    'False',
    'execfile'
]
KEYWORDS.extend(dir(__builtins__))

class_snippet = """class <!cursor>():
    def __init__(self):
        super(, self).__init__()
""".strip()

context_manager_snippet = (
"""class <!cursor>():
    def __init__(self):
        super(, self).__init__()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, """
+ """exception_value, traceback):"""
).strip()

super_snippet = """
super(<!class>, self).<!method>(<!args>)
""".strip()

function_snippet = 'def <!cursor>():'

method_snippet = 'def <!cursor>(self):'
name_main_snippet = "if __name__ == '__main__':"
pprint_snippet = 'from pprint import pprint'
node_selected = 'node = nuke.selectedNode()'
nodes_selected = 'nodes = nuke.selectedNodes()'
node_loop_snippet = (
    'for node in nuke.selectedNodes():\n    '
)
node_all_snippet = (
    'for node in nuke.allNodes():\n    '
)

node_deselect_snippet = (
    'n.setSelected(False) for n in '
    +'nuke.allNodes(recurseGroups=True)]'
)

custom_widget_snippet = """
class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super(MyWidget, self).__init__()
    def makeUI(self):
        return self
    def valueChanged(self, value):
        pass
""".strip()
qt_import_snippet = (
    'from Qt import '
    +'QtWidgets, QtGui, QtCore'
)

SNIPPETS = {
    'class [snippet]':
        class_snippet,
    'contextmanager [snippet]':
        context_manager_snippet,
    'super [snippet]':
        super_snippet,
    'def [snippet] [func]':
        function_snippet,
    'def [snippet] [method]':
        method_snippet,
    'for node selected [snippet]':
        node_loop_snippet,
    'for node all [snippet]':
        node_all_snippet,
    'n.setSelected(False) [snippet]':
        node_deselect_snippet,
    'node [snippet]':
        node_selected,
    'nodes [snippet]':
        nodes_selected,
    'custom widget [snippet]':
        custom_widget_snippet,
    'Qt [snippet]':
        qt_import_snippet,
    'if [snippet]':
		name_main_snippet,
    'pprint [snippet]' :
		pprint_snippet,
}


def locate_snippet_file():
    """
    Look for a file called PythonEditor_snippets.json
    in the local user .nuke directory. If found and
    its contents read, add them to the global SNIPPETS
    dictionary.
    """
    global SNIPPETS
    try:
        snippet_path = os.path.join(
            NUKE_DIR,
            'PythonEditor_snippets.json'
        )
        if os.path.isfile(snippet_path):
            with open(snippet_path, 'r') as f:
                data = f.read()
            user_snippets = json.loads(data)
            SNIPPETS.update(**user_snippets)
    except Exception as e:
        debug(e)


class Completer(QtWidgets.QCompleter):
    def __init__(self, stringlist):
        super(Completer, self).__init__(stringlist)

        self.setCompletionMode(
            QtWidgets.QCompleter.PopupCompletion
        )
        self.setCaseSensitivity(
            QtCore.Qt.CaseSensitive
        )


class AutoCompleter(QtCore.QObject):
    """
    Provides autocompletion to QPlainTextEdit.
    Requires signals to be emitted from such
    with -pre and -post keyPressEvent signals.
    """
    def __init__(self, editor):
        super(AutoCompleter, self).__init__()
        self.setParent(editor)
        locate_snippet_file()

        self.loadedModules = sys.modules.keys()
        self._completer = None

        self.editor = editor
        self.connect_signals()

    @property
    def completer(self):
        """
        Sets new completer if none present.
        # WARNING: Previously, this
        # didn't need to be here.
        # Something about adding
        # another connection to the
        # focus_in_signal made this
        # necessary.
        """
        if self._completer is None:
            wordlist = re.findall(
                r'\w+',
                self.editor.toPlainText()
            )
            wordlist = list(set(wordlist))
            self._completer = Completer(wordlist)
            self._completer.setParent(self)
            self._completer.setWidget(self.editor)
            self._completer.activated.connect(
                self.insert_completion
            )
        return self._completer

    @completer.setter
    def completer(self, completer):
        self._completer = completer

    def connect_signals(self):
        self.editor.focus_in_signal.connect(
            self._focusInEvent
        )
        # TODO: QtCore.Qt.DirectConnection
        self.editor.key_pressed_signal.connect(
            self._pre_keyPressEvent
        )
        self.editor.post_key_pressed_signal.connect(
            self._post_keyPressEvent
        )

    @QtCore.Slot(QtGui.QFocusEvent)
    def _focusInEvent(self, event):
        """
        Connected to editor focusInEvent via signal.
        """
        return self.completer

    def word_under_cursor(self):
        """
        Returns a string with the
        word under the cursor.
        """
        textCursor = self.editor.textCursor()
        textCursor.select(
            QtGui.QTextCursor.WordUnderCursor
        )
        word = textCursor.selection().toPlainText()
        return word

    def word_before_cursor(self, regex=r'[\w|\.]+'):
        """
        Returns a string with the last
        word of the block.
        """
        textCursor = self.editor.textCursor()
        textCursor.select(
            QtGui.QTextCursor.BlockUnderCursor
        )
        line_text = textCursor.selection(
            ).toPlainText()
        words = re.findall(regex, line_text)
        if (len(words) == 0):
            return ''
        return words.pop()

    def get_word_after_dot(self, _char):
        """
        TODO:
        This needs a total rethink.
        Was hacked together.
        """
        self.completer.setCompletionPrefix('')
        textCursor = self.editor.textCursor()
        document = self.editor.document()

        pos = textCursor.position()
        block_number = document.findBlock(
            pos).blockNumber()

        block = document.findBlockByNumber(
            block_number
        )
        block_start = block.position()
        s = self.editor.toPlainText(
            )[block_start:pos]

        for c in s:
            if (not c.isalnum()
                and c not in ['.', '_']):
                s = s.replace(c, ' ')

        word_after_dot = s.split(' ')[-1]
        word_after_dot = word_after_dot.split(
            '.')[-1]

        return word_after_dot

    def get_obj_before_char(self, _char):
        """
        Return python object from string.
        """
        self.completer.setCompletionPrefix('')
        textCursor = self.editor.textCursor()
        document = self.editor.document()

        pos = textCursor.position()
        block_number = document.findBlock(
            pos).blockNumber()

        block = document.findBlockByNumber(
            block_number
        )
        block_start = block.position()
        s = self.editor.toPlainText(
            )[block_start:pos]

        for c in s:
            if (not c.isalnum()
                and c not in ['.', '_']):
                s = s.replace(c, ' ')

        word_before_dot = s.split(' ')[-1]
        word_before_dot = '.'.join(
            word_before_dot.split('.')[:-1])

        if (word_before_dot.strip() == ''
            or word_before_dot.endswith(_char)
            or not word_before_dot[-1].isalnum()):
            return

        if word_before_dot in ['self', 'cls']:
            class_name = self.get_inherited_class()
            if class_name:
                word_before_dot = class_name

        app_namespace = __main__.__dict__.copy()
        _obj = app_namespace.get(word_before_dot)
        if _obj is None:
            try:
                _ = {}
                exec(
                    '_obj = '+word_before_dot,
                    app_namespace,
                    _
                )
                _obj = _.get('_obj')
            except (
                NameError,
                AttributeError,
                SyntaxError
                ):
                # we want to handle this
                # silently, except. TODO:
                # SyntaxError avoidance
                # is a lazy way to avoid
                # properly formatting the
                # object.
                return

        return _obj

    def complete_object(self, _obj=None):
        """
        Get list of object properties
        and methods and set them as
        the completer string list.
        """
        if _obj is None:
            _obj = self.get_obj_before_char('.')

        if _obj is None or False:
            return

        attrs = dir(_obj)

        methods = [
            a for a in attrs
            if a[0].islower()
        ]
        therest = [
            a for a in attrs
            if not a[0].islower()
        ]
        stringlist = methods+therest
        self.set_list(stringlist)
        self.show_popup()

        cp = self.completer
        current_word = self.word_under_cursor()
        all_alpha = all(
            (c.isalnum() or c in '_.')
            for c in current_word
        )
        if not all_alpha:
            current_word = self.get_word_after_dot(
                '.'
            ) # TODO: won't always be a dot!
            all_alpha = all(
                (c.isalnum() or c in '_.')
                for c in current_word
            )
            if not all_alpha:
                cp.popup().hide()
                return
        cp.setCompletionPrefix(
            current_word
        )
        cp.popup().setCurrentIndex(
            cp.completionModel().index(0, 0)
        )

    def complete_variables(self):
        """
        Complete variable names in
        global scope.
        TODO: Substring matching
        """
        cp = self.completer
        variables = __main__.__dict__.keys()

        # add words except the word under the cursor
        word = self.word_under_cursor()
        text = self.editor.toPlainText()
        words = [
            w for w in re.findall(r'\w+', text)
            if w != word
        ]

        variables = [
            variables
            + keyword.kwlist
            + list(SNIPPETS.keys())
            + dir(__builtins__)
            + KEYWORDS
            + words
        ]

        variables = sorted(
            list(
                set().union(*variables)
            )
        )
        self.set_list(variables)
        word = self.word_under_cursor()

        if re.match('[a-zA-Z0-9_]', word) is None:
            word = self.word_before_cursor(
                regex=r'\w+'
                )

        char_len = len(word)
        cp.setCompletionPrefix(word)
        popup = cp.popup()
        popup.setCurrentIndex(
            cp.completionModel().index(0, 0)
        )

        # TODO: substring matching
        """
        for var in variables:
            found = nonconsec_find(
                word,
                var,
                anchored=True
            )
            if found:
                print(word, var)
        """

        if char_len and any(
                w[:char_len] == word
                for w in variables
            ):
            self.show_popup()

    def set_list(self, stringlist):
        """
        Sets the list of completions.
        """
        qslm = QtCore.QStringListModel()
        qslm.setStringList(stringlist)
        self.completer.setModel(qslm)

    def show_popup(self):
        """
        Show the completer list.
        """
        cursorRect = self.editor.cursorRect()
        pop = self.completer.popup()
        cursorRect.setWidth(
            pop.sizeHintForColumn(0)
            + pop.verticalScrollBar(
                ).sizeHint(
                ).width()
        )
        self.completer.complete(cursorRect)

    def insert_completion(self, completion):
        """
        Inserts a completion,
        replacing current word.
        """
        if '[snippet]' in completion:
            return self.insert_snippet_completion(
                completion
                )

        textCursor = self.editor.textCursor()
        prefix = self.completer.completionPrefix()
        pos = textCursor.position()

        textCursor.setPosition(
            pos-len(prefix),
            QtGui.QTextCursor.KeepAnchor
        )

        textCursor.insertText(completion)
        self.editor.setTextCursor(textCursor)

    def get_object_body(self, _type='class'):
        """
        Utility method to get the text from
        the current cursor position upwards
        until the 'class' keyword.
        """
        textCursor = self.editor.textCursor()
        pos = textCursor.position()
        text = self.editor.toPlainText()[:pos]

        if _type not in text:
            return ''

        class_pos = text.rfind(_type)
        text = text[class_pos:]
        return text

    def get_object_text(self, pattern, _type='class'):
        """
        Get the text attribute inside a class
        block that matches the pattern given.
        """
        text = self.get_object_body(_type=_type)
        search = re.findall(pattern, text)
        if not search:
            return ''

        class_attribute = search[0]
        return class_attribute

    def get_inherited_class(self):
        """
        Return the name of the inherited class,
        e.g.: class ClassName(Inherited.Class)
        """
        return self.get_object_text(
            r'(?:\()([a-zA-Z0-9_\.]+)',
            _type='class',
        )

    def get_current_class_name(self):
        """
        Return the class name of the first class
        defined above the text cursor.
        e.g.: class ClassName()
        """
        return self.get_object_text(
            r'(?:class\s+)(\w+)(?:\()',
            _type='class',
        )

    def get_current_function_name(self):
        """
        Return the function name of the first
        function defined above the text cursor.
        e.g.: def function_name()
        """
        return self.get_object_text(
            r'(?:def\s+)([a-zA-Z0-9_]+)(?:\()',
            _type='def',
        )

    def get_current_function_args(self):
        """
        Return the function arguments, of the
        first function defined above the text
        cursor.
        e.g.:
        def function_name(
        argument, parameter='value'
        )
        """
        return self.get_object_text(
            r'(?:def\s+\w+\()(.+)(?:\)\:)',
            _type='def',
        )

    def get_current_method_args(self):
        """
        Return the function arguments, minus 'self',
        of the first method defined above the text
        cursor.
        e.g.:
        def function_name(
        self, argument, parameter='value'
        )
        """
        return self.get_object_text(
            r'(?:def\s+\w+\(\s*self,\s*)(.+)(?:\)\:)',
            _type='def',
        )

    def insert_snippet_completion(self, completion):
        """
        Fetches snippet from dictionary and
        completes with that. Sets text cursor
        position to snippet insert point.
        """
        snippet = SNIPPETS[completion]
        completion = snippet
        if '<!cursor>' in snippet:
            cursor_insert = completion.index(
                '<!cursor>'
            )
            completion = completion.replace(
                '<!cursor>',
                ''
            )

        if '<!class>' in snippet:
            completion = completion.replace(
                '<!class>',
                self.get_current_class_name()
            )

        if '<!method>' in snippet:
            completion = completion.replace(
                '<!method>',
                self.get_current_function_name()
            )

        if '<!args>' in snippet:
            completion = completion.replace(
                '<!args>',
                self.get_current_method_args()
            )

        textCursor = self.editor.textCursor()
        prefix = self.completer.completionPrefix()
        pos = textCursor.position()
        textCursor.setPosition(
            pos-len(prefix),
            QtGui.QTextCursor.KeepAnchor
        )
        textCursor.insertText(completion)

        if '<!cursor>' in snippet:
            textCursor.setPosition(
                pos+cursor_insert-len(prefix),
                QtGui.QTextCursor.MoveAnchor
            )

        self.editor.setTextCursor(textCursor)

    @QtCore.Slot(QtGui.QKeyEvent)
    def _pre_keyPressEvent(self, event):
        """
        Called before QPlainTextEdit.keyPressEvent
        TODO:
        - Complete defined names
            (parse for "name =" thing)
        - Complete class names (parse for "self.")
        - Complete snippets
        - Hide popup if no completions available
        """
        cp = self.completer
        completing = (
            cp
            and cp.popup()
            and cp.popup().isVisible()
        )

        if completing:
            if event.key() in (
                QtCore.Qt.Key_Enter,
                QtCore.Qt.Key_Return,
                QtCore.Qt.Key_Escape,
                QtCore.Qt.Key_Tab,
                QtCore.Qt.Key_Backtab
            ):
                event.ignore()
                e = self.editor
                e.wait_for_autocomplete = True
                return True

        NOMOD = QtCore.Qt.NoModifier
        not_alnum_or_mod = (
            not event.text().isalnum()
            and event.modifiers() == NOMOD
        )

        zero_completions = (cp.completionCount() == 0)
        if not_alnum_or_mod or zero_completions:
            cp.popup().hide()

        if event.key() == QtCore.Qt.Key_Tab:
            textCursor = self.editor.textCursor()
            SHIFT = QtCore.Qt.ShiftModifier
            shift_held = (event.modifiers() == SHIFT)
            if (not textCursor.hasSelection()
                and not shift_held):
                textCursor.select(
                    QtGui.QTextCursor.LineUnderCursor
                )
                text = textCursor.selectedText()
                if text.endswith('.'):
                    self.complete_object()
                    # assuming this should be
                    # here too but untested
                    e = self.editor
                    e.wait_for_autocomplete = True
                    return True

        self.editor.wait_for_autocomplete = False
        self.editor.keyPressEvent(event)

    @QtCore.Slot(QtGui.QKeyEvent)
    def _post_keyPressEvent(self, event):
        """
        Called after QPlainTextEdit.keyPressEvent
        """
        cp = self.completer

        if (event.key() == QtCore.Qt.Key_Period
            or event.text() in [':', '!']):
            # TODO: this should hide
            # on a lot more characters!
            if cp.popup():
                cp.popup().hide()
            self.complete_object()
            self.editor.wait_for_autocomplete = True
            return True

        elif (cp and cp.popup()
                  and cp.popup().isVisible()
                  and not cp.completionCount() == 0):

            current_word = self.word_under_cursor()

            word_match = re.match(
                '[a-zA-Z0-9_]',
                current_word
            )
            if word_match is None:
                text_match = re.match(
                    '[a-zA-Z0-9_]',
                    event.text()
                )
                if text_match is None:
                    cp.popup().hide()

                current_word = self.word_before_cursor(
                    regex=r'\w+'
                )

            # TODO: add a case for "self."
            # completion in here

            cp.setCompletionPrefix(current_word)
            cp.popup().setCurrentIndex(
                cp.completionModel().index(0, 0)
            )

        elif (
            event.text().isalnum()
            or event.text() in ['_']
            ):
            pos = self.editor.textCursor().position()
            document = self.editor.document()
            block_number = document.findBlock(
                pos).blockNumber()
            block = document.findBlockByNumber(
                block_number
            )
            if '.' in block.text().split(' ')[-1]:
                self.complete_object()
            else:
                self.complete_variables()

        self.editor.wait_for_autocomplete = True


# from tabtabtab by Ben Dickson
def nonconsec_find(needle, haystack, anchored=False):
    """checks if each character of "needle" can be
    found in order (but not
    necessarily consecutivly) in haystack.
    For example, "mm" can be found in "matchmove",
    but not "move2d"
    "m2" can be found in "move2d", but not "matchmove"

    >>> nonconsec_find("m2", "move2d")
    True
    >>> nonconsec_find("m2", "matchmove")
    False

    Anchored ensures the first letter matches

    >>> nonconsec_find(
    "atch", "matchmove", anchored = False)
    True
    >>> nonconsec_find(
    "atch", "matchmove", anchored = True)
    False
    >>> nonconsec_find(
    "match", "matchmove", anchored = True)
    True

    If needle starts with a string,
    non-consecutive searching is disabled:

    >>> nonconsec_find(
    " mt", "matchmove", anchored = True)
    False
    >>> nonconsec_find(
    " ma", "matchmove", anchored = True)
    True
    >>> nonconsec_find(
    " oe", "matchmove", anchored = False)
    False
    >>> nonconsec_find(
    " ov", "matchmove", anchored = False)
    True
    """

    if "[" not in needle:
        haystack = haystack.rpartition(" [")[0]

    if len(haystack) == 0 and len(needle) > 0:
        # "a" is not in ""
        return False

    elif len(needle) == 0 and len(haystack) > 0:
        # "" is in "blah"
        return True

    elif len(needle) == 0 and len(haystack) == 0:
        # ..?
        return True

    # Turn haystack into list of characters
    # (as strings are immutable)
    haystack = [hay for hay in str(haystack)]

    if needle.startswith(" "):
        # "[space]abc" does consecutive
        # search for "abc" in "abcdef"
        if anchored:
            if "".join(
                haystack).startswith(
                needle.lstrip(" ")):
                return True
        else:
            if needle.lstrip(" ") in "".join(haystack):
                return True

    if anchored:
        if needle[0] != haystack[0]:
            return False
        else:
            # First letter matches, remove it
            # for further matches
            needle = needle[1:]
            del haystack[0]

    for needle_atom in needle:
        try:
            needle_pos = haystack.index(needle_atom)
        except ValueError:
            return False
        else:
            # Dont find string in same pos or
            # backwards again
            del haystack[:needle_pos + 1]
    return True
