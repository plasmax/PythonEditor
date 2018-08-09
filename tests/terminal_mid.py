# an attempt to connect via signals instead of a list of methods, 
# with the idea that signal connections might not interrupt garbage collection

"""
This module needs to satisfy the following requirements:

- [ ] Redirect stdout to all Python Editor Terminal QPlainTextEdits
- [ ] Preserve unread output in Queue objects, which are read when loading the Terminal(s)
- [ ] Be reloadable without losing stdout connections
- [ ] Not keep references to destroyed objects


# would sys.displayhook be useful in here?

"""


import sys
import os
from Queue import Queue

sys.dont_write_bytecode = True
TESTS_DIR = os.path.dirname(__file__)
PACKAGE_PATH = os.path.dirname(TESTS_DIR)
sys.path.append(PACKAGE_PATH)


from PythonEditor.ui.Qt import QtWidgets, QtCore, QtGui


# ----- override nuke FnRedirect -----
class VirtualModule(object):
    pass


class Loader(object):
    def load_module(self, name):
        print name
        from _fnpython import stderrRedirector, outputRedirector
        sys.stdout.SERedirect = outputRedirector
        sys.stderr.SERedirect = stderrRedirector
        return VirtualModule()


class Finder(object):
    def find_module(self, name, path=''):
        if 'FnRedirect' in name:
            return Loader()


# sys.meta_path = [i for i in sys.meta_path
#                  if not isinstance(i, Finder)]
# sys.meta_path.append(Finder())
sys.meta_path = [Finder()]
# ----- end override section -----


class PySingleton(object):
    """
    Return a single instance of a class
    or create a new instance if none exists.
    """
    def __new__(cls, *args, **kwargs):
        if '_the_instance' not in cls.__dict__:
            cls._the_instance = object.__new__(cls)
        return cls._the_instance


class Redirect(QtCore.QObject):
    signal = QtCore.Signal(str, object)
    def __init__(self, stream):
        super(Redirect, self).__init__()
        self.stream = stream
        self.queue = Queue(maxsize=2000)
        self.SERedirect = lambda x: None
        # self.receivers = []

        for a in dir(stream):
            try:
                getattr(self, a)
            except AttributeError:
                attr = getattr(stream, a)
                setattr(self, a, attr)

    def write(self, text):
        queue = self.queue
        receivers = self.receivers('2signal')
        if not receivers:
            queue.put(text)
        else:
            # if queue.empty():
            #     queue = None
            # for func in receivers:
                # func(text=text, queue=queue)
            self.signal.emit(text, queue)

        self.stream.write(text)
        self.SERedirect(text)


class SysOut(Redirect, PySingleton):
    pass


class SysErr(Redirect, PySingleton):
    pass


class SysIn(Redirect, PySingleton):
    pass


class Terminal(QtWidgets.QPlainTextEdit):
    def __init__(self):
        super(Terminal, self).__init__()
        self.setReadOnly(True)
        self.setObjectName('Terminal')
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        # sys.stdout.receivers.append(self.get)
        sys.stdout.signal.connect(self.get)
        self.get(queue=sys.stdout.queue)
        sys.stderr.signal.connect(self.get)
        # sys.stderr.receivers.append(self.get)
        self.get(queue=sys.stderr.queue)

    @QtCore.Slot(str, object)
    def get(self, text=None, queue=None):
        """
        The get method allows the terminal to pick up
        on output created between the stream object
        encapsulation and the terminal creation.

        This is as opposed to connecting directly to the
        insertPlainText method, e.g.
        sys.stdout.write = self.insertPlainText
        """
        if queue is not None:
            while not queue.empty():
                _text = queue.get()
                self.receive(_text)

        if text is not None:
            self.receive(text)

    def receive(self, text):
        # textCursor = self.textCursor()
        self.moveCursor(QtGui.QTextCursor.End)
        self.insertPlainText(text)

    def showEvent(self, event):
        super(Terminal, self).showEvent(event)
        self.get(queue=sys.stdout.queue)
        self.get(queue=sys.stderr.queue)



sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__
sys.stdin = sys.__stdin__

sys.stdout = SysOut(sys.__stdout__)
sys.stderr = SysErr(sys.__stderr__)
sys.stdin = SysIn(sys.__stdin__)

try:
    from _fnpython import stderrRedirector, outputRedirector
    sys.stdout.SERedirect = outputRedirector
    sys.stderr.SERedirect = stderrRedirector
except ImportError:
    pass
    
