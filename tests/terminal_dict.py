"""
This module needs to satisfy the following requirements:

- [ ] Redirect stdout to all Python Editor Terminal QPlainTextEdits
- [ ] Preserve unread output in Queue objects, which are read when loading the Terminal(s)
- [ ] Be reloadable without losing stdout connections
      (currently doesn't pick up on queue object because stdout is wiped on reload)
- [ ] Not keep references to destroyed objects


# would sys.displayhook be useful in here? No, displayhook is for registering
objects that are also printed.

"""


import sys
import os
from Queue import Queue

from PythonEditor.ui.Qt import QtWidgets, QtCore, QtGui


# ----- override nuke FnRedirect -----
class VirtualModule(object):
    pass


class Loader(object):
    def load_module(self, name):
        try:
            from _fnpython import stderrRedirector, outputRedirector
            sys.outputRedirector = outputRedirector
            sys.stderrRedirector = stderrRedirector
        finally:
            # firmly block all imports of the module
            return VirtualModule()


class Finder(object):
    _deletable = ''

    def find_module(self, name, path=''):
        if 'FnRedirect' in name:
            return Loader()


sys.meta_path = [i for i in sys.meta_path
                 if not hasattr(i, '_deletable')]
sys.meta_path.append(Finder())
# ----- end override section -----


class Signal(QtCore.QObject):
    s = QtCore.Signal(str)
    receivers = {
                 '<stdout>': [],
                 '<stderr>': []
                 }

    def customEvent(self, event):

        for func in self.receivers[event.print_type]:
            func(text=event.text, queue=event.queue)

        if event.text is None:
            return

        if event.print_type == '<stdout>':
            sys.outputRedirector(event.text)
        elif event.print_type == '<stderr>':
            sys.stderrRedirector(event.text)


class PrintEvent(QtCore.QEvent):
    def __init__(self, text=None, queue=None):
        self.text = text
        self.queue = queue
        super(PrintEvent, self).__init__(QtCore.QEvent.User)


class PySingleton(object):
    """
    Return a single instance of a class
    or create a new instance if none exists.
    """
    def __new__(cls, *args, **kwargs):
        if '_the_instance' not in cls.__dict__:
            cls._the_instance = object.__new__(cls)
        return cls._the_instance


class Redirect(object):
    def __init__(self, stream, queue=Queue()):
        self.stream = stream
        self.signal = Signal()
        self.queue = queue

        for a in dir(stream):
            try:
                getattr(self, a)
            except AttributeError:
                attr = getattr(stream, a)
                setattr(self, a, attr)

    def write(self, text):
        self.stream.write(text)

        queue = self.queue
        r = self.signal.receivers
        receivers = r['<stdout>']+r['<stderr>']  # this is ugly
        if bool(receivers):
            queue = None
        else:
            queue.put(text)

        app = QtWidgets.QApplication.instance()
        event = PrintEvent(text=text, queue=queue)
        event.print_type = self.stream.name
        app.postEvent(self.signal, event, -2)


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

    def get(self, text=None, queue=None, name=None):
        """
        The get method allows the terminal to pick up
        on output created between the stream object
        encapsulation and the terminal creation.

        This is as opposed to connecting directly to the
        insertPlainText method, e.g.
        sys.stdout.write = self.insertPlainText

        !Warning! Don't print anything in here, it
        will cause an infinite loop.
        """

        if name is not None:
            self.receive(name)

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

        sys.stdout.signal.receivers['<stdout>'].append(self.get)
        sys.stderr.signal.receivers['<stderr>'].append(self.get)

        for stream in sys.stdout, sys.stderr:
            self.get(queue=stream.queue)

        super(Terminal, self).showEvent(event)

    def hideEvent(self, event):

        sys.stdout.signal.receivers['<stdout>'].remove(self.get)
        sys.stderr.signal.receivers['<stderr>'].remove(self.get)

        super(Terminal, self).hideEvent(event)

    def closeEvent(self, event):
        super(Terminal, self).closeEvent(event)


# before we reset stdout and err, try to recover their queues
out_queue = getattr(sys.stdout, 'queue', Queue())
err_queue = getattr(sys.stderr, 'queue', Queue())

# reset stdout, stderr, stdin:
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__
sys.stdin = sys.__stdin__

# override stdout, stderr, stdin
sys.stdout = SysOut(sys.__stdout__, queue=out_queue)
sys.stderr = SysErr(sys.__stderr__, queue=err_queue)
sys.stdin = SysIn(sys.__stdin__)

# we need these functions to be registered in the sys module
sys.outputRedirector = lambda x: None
sys.stderrRedirector = lambda x: None

# in case we decide to reload the module, we need to
# re-add the functions to write to Nuke's Script Editor.
try:
    from _fnpython import stderrRedirector, outputRedirector
    sys.outputRedirector = outputRedirector
    sys.stderrRedirector = stderrRedirector
except ImportError:
    pass


