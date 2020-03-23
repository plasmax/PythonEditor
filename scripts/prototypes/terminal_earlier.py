"""
This module needs to satisfy the following requirements:

- [ ] Redirect stdout to all Python Editor Terminal QPlainTextEdits
- [ ] Preserve unread output in Queue objects, which are read when loading the Terminal(s)
- [ ] Be reloadable without losing stdout connections
      (currently doesn't pick up on queue object because stdout is wiped on reload)
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
        print(name)
        try:
            from _fnpython import stderrRedirector, outputRedirector
            sys.outputRedirector = outputRedirector
            sys.stderrRedirector = stderrRedirector
            # sys.stdout.SERedirect = outputRedirector
            # sys.stderr.SERedirect = stderrRedirector

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
    e = QtCore.Signal()
    receivers = []
    def customEvent(self, event):
        pass
        # from _fnpython import stderrRedirector, outputRedirector
        # try:
        #     outputRedirector(event.text)
        # except:
        #     pass
        for func in self.receivers:
            func(text=event.text)
        # self.e.emit()
        # self.s.emit(event.text)

class PrintEvent(QtCore.QEvent):
    def __init__(self, text):
        self.text = text
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


def post_out(text):
    app = QtWidgets.QApplication.instance()
    app.postEvent(sys.stdout.signal, PrintEvent(text))

def post_err(text):
    app = QtWidgets.QApplication.instance()
    app.postEvent(sys.stderr.signal, PrintEvent(text))


class Redirect(object):
    def __init__(self, stream, queue=Queue()):
        self.stream = stream
        self.signal = Signal()
        self.queue = queue
        self.SERedirect = lambda x: None
        # self.post_text = lambda x: None
        self.receivers = []

        for a in dir(stream):
            try:
                getattr(self, a)
            except AttributeError:
                attr = getattr(stream, a)
                setattr(self, a, attr)

    # def post_text(self, text):
    #     app = QtWidgets.QApplication.instance()
    #     app.postEvent(self.signal, PrintEvent(text))

    def write(self, text):

        app = QtWidgets.QApplication.instance()
        event = PrintEvent(text)#, self.SERedirect)
        app.postEvent(self.signal, event)

        self.stream.write(text)
        # queue = self.queue
        # queue.put(text)
        # self.post_text(text)
        # try:
        #     self.post_text(text)
        # except Exception as e:
        #     print 'this is why it did not work', e
        #     self.stream.write('this is why it did not work:\n')
        #     self.stream.write(e)
            # self.post_text = lambda x: None
        # self.signal.s.emit(text)

        # receivers = self.receivers
        # if not receivers:
        #     queue.put(text)
        # else:
        #     if queue.empty():
        #         queue = None
        #     # TODO: at this point, what if we called
        #     # a relay object that would read the
        #     # queues and emit signals to various
        #     # listeners? instead of triggering the receivers
        #     # one by one here.
        #     for func in receivers:
        #         func(text=text, queue=queue)

        # self.stream.write(text)

        # would be nice to have a way to delay this too
        # as it seems to cause a fair bit of slowdown in Nuke.
        # self.SERedirect(text)


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
        # self.get(queue=sys.stdout.queue)
        # sys.stderr.receivers.append(self.get)
        # self.get(queue=sys.stderr.queue)

    @QtCore.Slot(str)
    def get(self, text=None, queue=None):
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
        # sys.stdout.signal.s.connect(self.get)
        # sys.stderr.signal.s.connect(self.get)
    #     print 'showing'

        for stream in sys.stdout.signal, sys.stderr.signal:
            stream.receivers.append(self.get)
            self.get(queue=stream.queue)

        super(Terminal, self).showEvent(event)
        # sys.stdout.receivers.append(self.get)
        # sys.stderr.receivers.append(self.get)
    #     # self.get(queue=sys.stdout.queue)
    #     # self.get(queue=sys.stderr.queue)

    def hideEvent(self, event):
        # sys.stdout.signal.s.disconnect(self.get)
        # sys.stderr.signal.s.disconnect(self.get)
    #     print 'hiding'
        for stream in sys.stdout.signal, sys.stderr.signal:
            if self.get in stream.receivers:
                stream.receivers.remove(self.get)

        super(Terminal, self).hideEvent(event)

    def closeEvent(self, event):
        print('closing')
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

# in case we decide to reload the module, we need to
# re-add the functions to write to Nuke's Script Editor.
try:
    from _fnpython import stderrRedirector, outputRedirector
    sys.stdout.SERedirect = outputRedirector
    sys.stderr.SERedirect = stderrRedirector
except ImportError:
    pass

