from __future__ import print_function
import sys

from PythonEditor.utils.constants import DEFAULT_FONT
from PythonEditor.ui.Qt import QtGui, QtWidgets, QtCore

WRITE_TO_SCRIPT_EDITOR = False

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


class PySingleton(object):
    """
    Return a single instance of a class
    or create a new instance if none exists.
    """
    def __new__(cls, *args, **kwargs):
        if '_the_instance' not in cls.__dict__:
            cls._the_instance = object.__new__(cls)
        return cls._the_instance


class Speaker(QtCore.QObject):
    """
    Used to relay sys stdout, stderr, stdin
    """
    emitter = QtCore.Signal(str)


class SERedirector(object):
    """
    For encapsulating and replacing a stream object.
    """
    def __init__(self, stream, _signal=None):
        fileMethods = ('fileno',
                       'flush',
                       'isatty',
                       'read',
                       'readline',
                       'readlines',
                       'seek',
                       'tell',
                       'write',
                       'writelines',
                       'xreadlines',
                       '__iter__',
                       'name')

        for i in fileMethods:
            if not hasattr(self, i) and hasattr(stream, i):
                setattr(self, i, getattr(stream, i))

        self.saved_stream = stream
        self._signal = _signal

    def close(self):
        self.flush()

    def stream(self):
        return self.saved_stream

    def __del__(self):
        self.reset()


class SESysStdOut(SERedirector, PySingleton):
    def reset(self):
        sys.stdout = self.saved_stream
        print('reset stream out')

    def write(self, text):
        if self._signal is not None:
            self._signal.emitter.emit(text)
        sys.outputRedirector(text)
        sys.__stdout__.write(text)


class SESysStdErr(SERedirector, PySingleton):
    def reset(self):
        sys.stderr = self.saved_stream
        print('reset stream err')

    def write(self, text):
        if self._signal is not None:
            self._signal.emitter.emit(text)
        sys.stderrRedirector(text)
        sys.__stderr__.write(text)


# TODO: This UI could be separate from the above
# stream wrappers, which could be placed in 'core'
class Terminal(QtWidgets.QPlainTextEdit):
    """ Output text display widget """
    link_activated = QtCore.Signal(str)

    def __init__(self):
        super(Terminal, self).__init__()
        # self.setStyleSheet('background:rgb(45,42,46);')

        self.setObjectName('Terminal')
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setReadOnly(True)
        self.setup()
        self.destroyed.connect(self.stop)
        font = QtGui.QFont(DEFAULT_FONT)
        font.setPointSize(10)
        self.setFont(font)
        
    @QtCore.Slot(str)
    def receive(self, text):
        try:
            textCursor = self.textCursor()
            if bool(textCursor):
                self.moveCursor(QtGui.QTextCursor.End)
                # pos = textCursor.position()
                # self.moveCursor(pos-1)
        except Exception:
            pass
        self.insertPlainText(text)
        # self.appendHtml(text)

    def stop(self):
        sys.stdout.reset()
        sys.stderr.reset()

    def setup(self):
        """
        Checks for an existing stream wrapper
        for sys.stdout and connects to it. If
        not present, creates a new one.
        TODO:
        The FnRedirect sys.stdout is always active.
        With a singleton object on a thread,
        that reads off this stream, we can make it
        available to Python Editor even before opening
        the panel.
        """
        if hasattr(sys.stdout, '_signal'):
            speaker = sys.stdout._signal
        else:
            speaker = Speaker()
            sys.stdout = SESysStdOut(sys.stdout, speaker)
            sys.stderr = SESysStdErr(sys.stderr, speaker)

        speaker.emitter.connect(self.receive)

    def mousePressEvent(self, e):
        if not hasattr(self, 'anchorAt'):
            #pyqt doesn't use anchorAt
            return super(Terminal, self).mousePressEvent(e)

        if (e.button() == QtCore.Qt.LeftButton):
            clickedAnchor = self.anchorAt(e.pos())
            if clickedAnchor:
                self.link_activated.emit(clickedAnchor)
        super(Terminal, self).mousePressEvent(e)


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
