#!/net/homes/mlast/bin/ nuke-safe-python-tg
""" For testing independently. """
from __future__ import absolute_import
import sys
import os

sys.dont_write_bytecode = True
TESTS_DIR = os.path.dirname(__file__)
PACKAGE_PATH = os.path.dirname(TESTS_DIR)
sys.path.append(PACKAGE_PATH)

try:
    import nuke
    pyside = ('PySide' if (nuke.NUKE_VERSION_MAJOR < 11) else 'PySide2')
except ImportError:
    pyside = 'PySide'

os.environ['QT_PREFERRED_BINDING'] = pyside

from PythonEditor.ui.Qt import QtCore, QtGui, QtWidgets
import re
import __main__


# from tabtabtab by Ben Dickson
def nonconsec_find(needle, haystack, anchored=False):
    """checks if each character of "needle" can be found in order (but not
    necessarily consecutivly) in haystack.
    For example, "mm" can be found in "matchmove", but not "move2d"
    "m2" can be found in "move2d", but not "matchmove"

    >>> nonconsec_find("m2", "move2d")
    True
    >>> nonconsec_find("m2", "matchmove")
    False

    Anchored ensures the first letter matches

    >>> nonconsec_find("atch", "matchmove", anchored = False)
    True
    >>> nonconsec_find("atch", "matchmove", anchored = True)
    False
    >>> nonconsec_find("match", "matchmove", anchored = True)
    True

    If needle starts with a string, non-consecutive searching is disabled:

    >>> nonconsec_find(" mt", "matchmove", anchored = True)
    False
    >>> nonconsec_find(" ma", "matchmove", anchored = True)
    True
    >>> nonconsec_find(" oe", "matchmove", anchored = False)
    False
    >>> nonconsec_find(" ov", "matchmove", anchored = False)
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

    # Turn haystack into list of characters (as strings are immutable)
    haystack = [hay for hay in str(haystack)]

    if needle.startswith(" "):
        # "[space]abc" does consecutive search for "abc" in "abcdef"
        if anchored:
            if "".join(haystack).startswith(needle.lstrip(" ")):
                return True
        else:
            if needle.lstrip(" ") in "".join(haystack):
                return True

    if anchored:
        if needle[0] != haystack[0]:
            return False
        else:
            # First letter matches, remove it for further matches
            needle = needle[1:]
            del haystack[0]

    for needle_atom in needle:
        try:
            needle_pos = haystack.index(needle_atom)
        except ValueError:
            return False
        else:
            # Dont find string in same pos or backwards again
            del haystack[:needle_pos + 1]
    return True



class Editor(QtWidgets.QPlainTextEdit):
    block_key_press = False
    key_pressed_signal = QtCore.Signal(QtGui.QKeyEvent)

    def __init__(self):
        super(Editor, self).__init__()
        self._completer = Completer(self)

    def keyPressEvent(self, event):

        self.block_key_press = False
        self.key_pressed_signal.emit(event)
        if self.block_key_press:
            return

        super(Editor, self).keyPressEvent(event)


class Completer(QtWidgets.QCompleter):
    def __init__(self, editor):
        super(Completer, self).__init__([])

        self.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.setCaseSensitivity(QtCore.Qt.CaseSensitive)

        self.editor = editor
        self.editor.key_pressed_signal.connect(self.key_press_event)
        self.setParent(self.editor)
        self.setWidget(self.editor)
        self.activated.connect(self.insert_completion)
        self.update_completions()

    def update_completions(self):
        """
        Generic update for all completions.
        """
        completions = __main__.__dict__.keys()
        # with open(__file__, 'rt') as f:
        #     data = f.read()
        text = self.editor.toPlainText()
        completions += re.findall('[\w|\.]+', text)
        completions = list(set(completions))
        self.set_list(completions)

    def set_list(self, stringlist):
        """
        Sets the list of completions.
        """
        qslm = QtCore.QStringListModel()
        qslm.setStringList(stringlist)
        self.setModel(qslm)

    def word_under_cursor(self):
        """
        Returns a string with the word under the cursor.
        """
        textCursor = self.editor.textCursor()
        textCursor.select(QtGui.QTextCursor.WordUnderCursor)
        word = textCursor.selection().toPlainText()
        return word

    def word_before_cursor(self):
        """
        Returns a string with the word under the cursor.
        """
        textCursor = self.editor.textCursor()
        textCursor.select(QtGui.QTextCursor.BlockUnderCursor)
        line_text = textCursor.selection().toPlainText()
        words = re.findall('[\w|\.]+', line_text)
        if (len(words) == 0):
            return ''
        return words.pop()

    def insert_completion(self, completion):
        """
        Inserts a completion,
        replacing current word.
        """
        # if '[snippet]' in completion:
        #     return self.insert_snippet_completion(completion)

        textCursor = self.editor.textCursor()
        prefix = self.completionPrefix()
        pos = textCursor.position()

        textCursor.setPosition(pos-len(prefix),
                               QtGui.QTextCursor.KeepAnchor)

        textCursor.insertText(completion)
        self.editor.setTextCursor(textCursor)

    def show_popup(self):
        """
        Show the completer list.
        """
        cursorRect = self.editor.cursorRect()
        pop = self.popup()
        cursorRect.setWidth(pop.sizeHintForColumn(0)
                            + pop.verticalScrollBar().sizeHint().width())
        self.complete(cursorRect)

    def key_press_event(self, event):

        # if it's a modifier key that's not shift, hide. we don't care.
        if event.modifiers() not in [QtCore.Qt.ShiftModifier, QtCore.Qt.NoModifier]:
            if self.popup() and self.popup().isVisible():
                self.popup().hide()
            return

        # if it's one of the following, and the popup is showing, completer handles it
        complete_keys = [
                        QtCore.Qt.Key_Enter,
                        QtCore.Qt.Key_Return,
                        QtCore.Qt.Key_Escape,
                        QtCore.Qt.Key_Tab,
                        QtCore.Qt.Key_Backtab,
                        ]
        if event.key() in complete_keys:
            if self.popup() and self.popup().isVisible():
                event.ignore() # tells the event to propagate to the completer
                self.editor.block_key_press = True
                self.popup().hide()
            return

        c = str(event.text())
        if (event.modifiers() == QtCore.Qt.ShiftModifier) and not bool(c):
            return # we're not ready yet

        is_char = (re.match('[a-zA-Z0-9_]', c) is not None)
        is_border = (c in list('.\'"()[]{}<>'))
        if not (is_char or is_border):
            return # can't complete non-word characters

        # in the case of completing after a dot (attributes) or after parentheses (dict keys)
        # we'll need to set the completion list (and then reset it if it doesn't meet certain conditions)
        if is_border:
            object_to_inspect = self.word_before_cursor()
            if not bool(object_to_inspect):
                return

            if (re.match('[a-zA-Z0-9_]', object_to_inspect[0]) is None):
                return

            print('Object to inspect: %s' % object_to_inspect)
            obj = __main__.__dict__.get(object_to_inspect)
            if obj is None:
                namespace = __main__.__dict__.copy()
                try:
                    exec('__obj__ = %s' % object_to_inspect, namespace)
                    obj = namespace['__obj__']
                except Exception as e:
                    print('Cannot recover object %s' % object_to_inspect)
                    return
            print('Recovered object %s: %s' % (object_to_inspect, obj))


            if c in list('\'"'):
                if object_to_inspect == 'nuke.selectedNode':
                    try:
                        node = obj.__call__()
                    except ValueError:
                        return
                    self.set_list(node.knobs().keys())
                elif object_to_inspect == 'nuke.toNode':
                    node_names = [n.fullName() for n in nuke.allNodes(recurseGroups=True)]
                    self.set_list(nodes)
                elif hasattr(obj, 'keys'):
                    self.set_list(obj.keys())
            elif c == '.':
                self.set_list(dir(obj))
            else:
                self.update_completions()
                return

            # if object_to_inspect == 'nuke.selectedNode':
            #     if c in list('\'"'):
            #         try:
            #             node = obj.__call__()
            #         except ValueError:
            #             return
            #         self.set_list(node.knobs().keys())
            # elif object_to_inspect == 'nuke.toNode':
            #     if c in list('\'"'):
            #         node_names = [n.fullName() for n in nuke.allNodes(recurseGroups=True)]
            #         self.set_list(nodes)
            # elif c == '.':
            #     self.set_list(dir(obj))
            # else:
            #     self.update_completions()
            #     return

        # hide if there are no completions left
        if (self.completionCount() == 0):
            if self.popup() and self.popup().isVisible():
                self.popup().hide()
                return
            self.update_completions()

        # if not (c.isalnum() or c in ['_']):

        # not_alnum_or_mod = (not c.isalnum()
        #                     and event.modifiers() == QtCore.Qt.NoModifier)

        # zero_completions = self.completionCount() == 0
        # if not_alnum_or_mod or zero_completions:
        #     self.popup().hide()
        #     return

        # char = c if is_char else ''
        if is_char:
            current_word = self.word_under_cursor() + c # WARNING! we only want to add event.text() if the cursor is on the last word
        else:
            current_word = ''

        print('Current word:', current_word)
        self.setCompletionPrefix(current_word)
        self.popup().setCurrentIndex(self.completionModel().index(0, 0))
        self.show_popup()


if __name__ == '__main__':
    """
    For testing outside of nuke.
    """
    try:
        app = QtWidgets.QApplication(sys.argv)
    except RuntimeError:
        # for running inside and outside of Nuke
        app = QtWidgets.QApplication.instance()

    e = Editor()
    e.show()


    sys.exit(app.exec_())
