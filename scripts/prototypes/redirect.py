import sys
import os
from Queue import Queue

sys.dont_write_bytecode = True
TESTS_DIR = os.path.dirname(__file__)
PACKAGE_PATH = os.path.dirname(TESTS_DIR)
sys.path.append(PACKAGE_PATH)


from PythonEditor.ui.Qt import QtWidgets, QtCore, QtGui


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


class PySingleton(object):
    """
    Return a single instance of a class
    or create a new instance if none exists.
    """
    def __new__(cls, *args, **kwargs):
        if '_the_instance' not in cls.__dict__:
            cls._the_instance = object.__new__(cls)
        return cls._the_instance


def call(func, *args, **kwargs):
    func(*args, **kwargs)


class Redirect(object):
    def __init__(self, stream):
        self.stream = stream
        self.queue = Queue()

        self.func = lambda x: None
        self.SERedirect = lambda x: None

        for a in dir(stream):
            try:
                getattr(self, a)
            except AttributeError:
                attr = getattr(stream, a)
                setattr(self, a, attr)

    def write(self, text):
        self.stream.write(text)
        self.SERedirect(text)

        self.queue.put(text)
        self.func(self.queue)


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

        sys.stdout.func = self.get
        self.get(sys.stdout.queue)
        sys.stderr.func = self.get
        self.get(sys.stderr.queue)

    def get(self, queue):
        """
        The get method allows the terminal to pick up
        on output created between the stream object
        encapsulation and the terminal creation.

        This is as opposed to connecting directly to the
        insertPlainText method, e.g.
        sys.stdout.write = self.insertPlainText
        """

        while not queue.empty():
            text = queue.get()
            self.receive(text)

    def receive(self, text):
        textCursor = self.textCursor()
        self.moveCursor(QtGui.QTextCursor.End)
        self.insertPlainText(text)

    def showEvent(self, event):
        super(Terminal, self).showEvent(event)
        self.get(sys.stdout.queue)
        self.get(sys.stderr.queue)


if not hasattr(sys.stdout, 'func'):
    sys.stdout = SysOut(sys.__stdout__)
if not hasattr(sys.stderr, 'func'):
    sys.stderr = SysErr(sys.__stderr__)
if not hasattr(sys.stdin, 'func'):
    sys.stdin = SysIn(sys.__stdin__)



# if __name__ == '__main__':
#     print "this won't get printed to the terminal"

#     print "this should get printed to the terminal"

#     print sys.stdout is sys.stderr is sys.stdin
#     print 5, object, type, sys._getframe()
#     print 'bba\npp'*8

#     print 'pre-app warmup'
#     app = QtWidgets.QApplication(sys.argv)
#     t = Terminal()
#     t.show()
#     t.receive('some text')
#     print 'and let the show begin'

#     def printhi():
#         print 'anus'
#         raise StopIteration

#     timer = QtCore.QTimer()
#     timer.timeout.connect(printhi)
#     timer.setInterval(1000)
#     timer.start()
#     sys.exit(app.exec_())
